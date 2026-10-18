#!/usr/bin/env python3
"""
Kannada Open Music Collector
============================
Builds a catalog (and optionally downloads audio) of Kannada tracks that are
openly licensed: CC0, Public Domain, CC BY and CC BY-SA by default.

Sources (all via their official public APIs, no scraping):
  - Internet Archive   (archive.org)
  - Wikimedia Commons  (commons.wikimedia.org)
  - Jamendo            (needs a free JAMENDO_CLIENT_ID environment variable)
  - Openverse          (api.openverse.org, aggregates many CC collections)

Outputs (in --out, default ./kannada_open_catalog):
  catalog.csv / catalog.json   accepted tracks, one row each, with license info
  rejected.csv                 everything filtered out and why
  az_index.json                Kannada letter (ಅ..ಹ) and English A-Z index
  ATTRIBUTION.md               credits you must show in your app
  audio/                       downloaded files (only with --download)

Nothing is downloaded unless you pass --download.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlparse

import requests

UA = "KannadaOpenCollector/1.0 (open-licensed music cataloguing)"
KN_SCRIPT = re.compile(r"[ಀ-೿]")

COMMERCIAL_OK = {"cc0", "pdm", "by", "by-sa"}

LICENSE_LABELS = {
    "cc0": "CC0 1.0 (public domain dedication)",
    "pdm": "Public Domain",
    "by": "CC BY",
    "by-sa": "CC BY-SA",
    "by-nc": "CC BY-NC",
    "by-nc-sa": "CC BY-NC-SA",
    "by-nd": "CC BY-ND",
    "by-nc-nd": "CC BY-NC-ND",
}

CSV_FIELDS = [
    "uid", "source", "source_id", "title", "title_transliterated", "creator",
    "license", "license_url", "license_raw", "kannada_signal", "language",
    "az_kannada", "az_english", "duration_sec", "file_format", "tags",
    "page_url", "audio_url", "review_note", "downloaded_path",
]


def warn(msg: str) -> None:
    print(f"[warn] {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(msg, file=sys.stderr)


# --------------------------------------------------------------------------
# License handling
# --------------------------------------------------------------------------
def normalize_license(*texts) -> str | None:
    """Return one of cc0, pdm, by, by-sa, by-nc, by-nc-sa, by-nd, by-nc-nd or None."""
    blob = " ".join(str(t) for t in texts if t).lower().strip()
    if not blob:
        return None
    if "publicdomain/zero" in blob or re.search(r"\bcc[\s-]?0\b|cc zero", blob):
        return "cc0"
    if "publicdomain/mark" in blob or re.search(
        r"public[\s-]?domain|not_in_copyright|\bpdm\b|\bpd-", blob
    ):
        return "pdm"
    m = re.search(r"creativecommons\.org/licenses/([a-z-]+)", blob)
    if m:
        code = m.group(1)
    else:
        m = re.search(r"\bcc[\s_-]?(by(?:[\s_-]?(?:nc|sa|nd))*)\b", blob)
        if not m:
            return None
        code = m.group(1)
    toks = set(re.split(r"[\s_-]+", code))
    if "by" not in toks:
        return None
    out = "by"
    for t in ("nc", "sa", "nd"):
        if t in toks:
            out += "-" + t
    return out


def allowed_set(allow_nc: bool, allow_nd: bool) -> set[str]:
    s = set(COMMERCIAL_OK)
    if allow_nc:
        s |= {"by-nc", "by-nc-sa"}
    if allow_nd:
        s.add("by-nd")
    if allow_nc and allow_nd:
        s.add("by-nc-nd")
    return s


# --------------------------------------------------------------------------
# Kannada detection
# --------------------------------------------------------------------------
def kannada_signal(r: dict, strict: bool) -> str | None:
    lang = (r.get("language") or "").lower()
    if lang in {"kn", "kan", "kannada", "kn-in"} or "kannada" in lang:
        return "language-field"
    strong = " ".join(
        [r.get("title") or "", r.get("creator") or "", " ".join(r.get("tags") or [])]
    )
    if KN_SCRIPT.search(strong):
        return "kannada-script"
    if re.search(r"kannada", strong, re.I):
        return "keyword-title-tags"
    if not strict:
        desc = r.get("description") or ""
        if KN_SCRIPT.search(desc):
            return "script-in-description"
        if re.search(r"kannada", desc, re.I):
            return "keyword-description"
    return None


def decide(r: dict, args) -> tuple[bool, str]:
    lic = r.get("license")
    if not lic:
        return False, "no recognizable open license"
    if lic not in allowed_set(args.allow_nc, args.allow_nd):
        return False, f"license '{lic}' not allowed by policy"
    if not r.get("_item_level") and not r.get("audio_url"):
        return False, "no audio url"
    sig = kannada_signal(r, args.strict)
    if not sig:
        return False, "no Kannada signal (title/tags/language/script)"
    r["kannada_signal"] = sig
    return True, ""


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
TAG_RE = re.compile(r"<[^>]+>")


def clean(s) -> str:
    if s is None:
        return ""
    if isinstance(s, (list, tuple)):
        s = "; ".join(str(x) for x in s)
    s = TAG_RE.sub(" ", str(s))
    return re.sub(r"\s+", " ", s).strip()


def as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    return [str(x) for x in v]


def make_record(source, sid, title, creator, license_raw, license_url, page_url,
                audio_url, **kw) -> dict:
    r = {
        "source": source,
        "source_id": str(sid),
        "title": clean(title),
        "creator": clean(creator),
        "license_raw": clean(license_raw),
        "license_url": license_url or "",
        "license": normalize_license(license_url, license_raw),
        "page_url": page_url or "",
        "audio_url": audio_url or "",
        "language": clean(kw.get("language")),
        "tags": [clean(t) for t in kw.get("tags", []) if t],
        "description": clean(kw.get("description"))[:2000],
        "duration_sec": kw.get("duration_sec", ""),
        "file_format": kw.get("file_format", ""),
        "review_note": kw.get("review_note", ""),
    }
    if kw.get("_item_level"):
        r["_item_level"] = True
    return r


def http_get(sess, url, params=None, retries=3, timeout=30, stream=False):
    for i in range(retries):
        try:
            resp = sess.get(url, params=params, timeout=timeout, stream=stream)
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(2 * (i + 1))
                continue
            return resp
        except requests.RequestException as e:
            warn(f"{url}: {e}")
            time.sleep(1.5 * (i + 1))
    return None


def get_json(sess, url, params=None):
    resp = http_get(sess, url, params=params)
    if resp is None:
        return None
    if resp.status_code != 200:
        warn(f"{url} returned HTTP {resp.status_code}")
        return None
    try:
        return resp.json()
    except ValueError:
        warn(f"{url} returned non-JSON")
        return None


# --------------------------------------------------------------------------
# Source: Internet Archive
# --------------------------------------------------------------------------
IA_FORMAT_RANK = ["VBR MP3", "MP3", "128Kbps MP3", "64Kbps MP3", "Ogg Vorbis",
                  "Opus", "Flac", "AAC", "M4A", "WAVE", "Apple Lossless Audio"]


def _parse_length(v):
    if not v:
        return ""
    try:
        if ":" in str(v):
            parts = [float(x) for x in str(v).split(":")]
            sec = 0.0
            for p in parts:
                sec = sec * 60 + p
            return round(sec)
        return round(float(v))
    except ValueError:
        return ""


def fetch_archive(sess, limit, delay, accept):
    q = ("mediatype:audio AND (kannada OR language:kan OR language:kn OR "
         "language:Kannada OR subject:kannada)")
    fields = ["identifier", "title", "creator", "licenseurl", "language",
              "subject", "description", "possible-copyright-status"]
    page, got = 1, 0
    while got < limit:
        data = get_json(sess, "https://archive.org/advancedsearch.php", {
            "q": q, "fl[]": fields, "rows": min(100, limit - got), "page": page,
            "output": "json", "sort[]": "downloads desc"})
        docs = ((data or {}).get("response") or {}).get("docs") or []
        if not docs:
            break
        for d in docs:
            ident = d["identifier"]
            item = make_record(
                "archive", ident, d.get("title"), d.get("creator"),
                d.get("possible-copyright-status"), d.get("licenseurl"),
                f"https://archive.org/details/{ident}", "",
                language=clean(d.get("language")), tags=as_list(d.get("subject")),
                description=d.get("description"), _item_level=True)
            if item["license"] == "pdm" and not d.get("licenseurl"):
                item["review_note"] = ("Archive.org copyright-status claim, "
                                       "verify before commercial use")
            if not accept(item):
                yield item
                continue
            meta = get_json(sess, f"https://archive.org/metadata/{ident}")
            time.sleep(delay)
            files = (meta or {}).get("files") or []
            best = {}
            for f in files:
                fmt = f.get("format")
                if fmt not in IA_FORMAT_RANK:
                    continue
                stem = os.path.splitext(f["name"])[0]
                rank = IA_FORMAT_RANK.index(fmt)
                if stem not in best or rank < best[stem][0]:
                    best[stem] = (rank, f)
            for stem, (_, f) in list(best.items())[:60]:
                rec = dict(item)
                rec.pop("_item_level", None)
                rec["source_id"] = f"{ident}/{f['name']}"
                rec["title"] = clean(f.get("title")) or item["title"]
                rec["creator"] = clean(f.get("creator")) or item["creator"]
                rec["audio_url"] = (f"https://archive.org/download/{ident}/"
                                    f"{quote(f['name'])}")
                rec["file_format"] = f.get("format", "")
                rec["duration_sec"] = _parse_length(f.get("length"))
                yield rec
        got += len(docs)
        page += 1
        time.sleep(delay)


# --------------------------------------------------------------------------
# Source: Wikimedia Commons
# --------------------------------------------------------------------------
def fetch_commons(sess, limit, delay, accept=None):
    api = "https://commons.wikimedia.org/w/api.php"
    for term in ("kannada", "ಕನ್ನಡ"):
        cont, got = {}, 0
        while got < limit:
            params = {
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": f"{term} filetype:audio", "gsrnamespace": 6,
                "gsrlimit": min(50, limit - got), "prop": "imageinfo",
                "iiprop": "url|mime|size|extmetadata",
                "iiextmetadatafilter":
                    "LicenseShortName|LicenseUrl|Artist|ImageDescription|Credit",
            }
            params.update(cont)
            data = get_json(sess, api, params)
            if not data:
                break
            pages = (data.get("query") or {}).get("pages") or {}
            for pg in pages.values():
                ii = (pg.get("imageinfo") or [{}])[0]
                mime = ii.get("mime", "")
                if not (mime.startswith("audio") or mime == "application/ogg"):
                    continue
                md = ii.get("extmetadata") or {}
                val = lambda k: (md.get(k) or {}).get("value", "")
                title = re.sub(r"^File:", "", pg.get("title", ""))
                title = os.path.splitext(title)[0].replace("_", " ")
                yield make_record(
                    "commons", pg.get("pageid"), title, val("Artist") or val("Credit"),
                    val("LicenseShortName"), val("LicenseUrl"),
                    ii.get("descriptionurl"), ii.get("url"),
                    description=val("ImageDescription"),
                    file_format=mime, tags=[term])
            got += len(pages)
            if "continue" in data and pages:
                cont = data["continue"]
                time.sleep(delay)
            else:
                break


# --------------------------------------------------------------------------
# Source: Jamendo (free client id: https://devportal.jamendo.com)
# --------------------------------------------------------------------------
def fetch_jamendo(sess, limit, delay, accept=None):
    cid = os.environ.get("JAMENDO_CLIENT_ID")
    if not cid:
        warn("JAMENDO_CLIENT_ID not set, skipping Jamendo")
        return
    for extra in ({"search": "kannada"}, {"tags": "kannada"}, {"search": "ಕನ್ನಡ"}):
        offset = 0
        while offset < limit:
            params = {"client_id": cid, "format": "json",
                      "limit": min(200, limit - offset), "offset": offset,
                      "include": "musicinfo+licenses", "audiodlformat": "mp32"}
            params.update(extra)
            data = get_json(sess, "https://api.jamendo.com/v3.0/tracks/", params)
            results = (data or {}).get("results") or []
            if not results:
                break
            for t in results:
                mi = t.get("musicinfo") or {}
                tg = mi.get("tags") or {}
                tags = as_list(tg.get("genres")) + as_list(tg.get("vartags"))
                url = t.get("audiodownload") if t.get("audiodownload_allowed") \
                    else t.get("audio")
                yield make_record(
                    "jamendo", t.get("id"), t.get("name"), t.get("artist_name"),
                    t.get("license_ccurl"), t.get("license_ccurl"),
                    t.get("shareurl"), url, language=mi.get("lang"), tags=tags,
                    duration_sec=t.get("duration", ""), file_format="mp3")
            offset += len(results)
            time.sleep(delay)


# --------------------------------------------------------------------------
# Source: Openverse
# --------------------------------------------------------------------------
OV_CC = {"by", "by-sa", "by-nc", "by-nd", "by-nc-sa", "by-nc-nd"}


def fetch_openverse(sess, limit, delay, accept=None):
    for q in ("kannada", "ಕನ್ನಡ"):
        page, got = 1, 0
        while got < limit:
            data = get_json(sess, "https://api.openverse.org/v1/audio/",
                            {"q": q, "page": page, "page_size": 20})
            results = (data or {}).get("results") or []
            if not results:
                break
            for it in results:
                lic = (it.get("license") or "").lower()
                raw = f"cc {lic}" if lic in OV_CC else lic
                tags = [t.get("name") for t in (it.get("tags") or []) if t.get("name")]
                dur = it.get("duration")
                yield make_record(
                    "openverse", it.get("id"), it.get("title"), it.get("creator"),
                    raw, it.get("license_url"), it.get("foreign_landing_url"),
                    it.get("url"), tags=tags + as_list(it.get("genres")),
                    description=f"provider: {it.get('provider', '')}",
                    duration_sec=round(dur / 1000) if isinstance(dur, (int, float)) else "",
                    file_format=it.get("filetype", ""))
            got += len(results)
            page += 1
            if page > (data or {}).get("page_count", page):
                break
            time.sleep(delay)


SOURCES = {
    "archive": fetch_archive,
    "commons": fetch_commons,
    "jamendo": fetch_jamendo,
    "openverse": fetch_openverse,
}


# --------------------------------------------------------------------------
# A-Z index
# --------------------------------------------------------------------------
KN_LETTERS = [chr(c) for c in range(0x0C85, 0x0CBA)
              if unicodedata.category(chr(c)).startswith("L")]
KN_SET = set(KN_LETTERS)


def first_kannada_letter(title: str) -> str:
    for ch in title:
        if ch.isalnum():
            return ch if ch in KN_SET else ""
    return ""


def transliterate(title: str) -> str:
    if not KN_SCRIPT.search(title):
        return ""
    try:
        from indic_transliteration import sanscript
        return sanscript.transliterate(title, sanscript.KANNADA, sanscript.ITRANS)
    except Exception:
        return ""


def english_key(title: str, translit: str) -> str:
    for text in (title, translit):
        for ch in text:
            if ch.isascii() and ch.isalpha():
                return ch.upper()
            if ch.isdigit():
                return "#"
    return ""


def build_az(records: list[dict]) -> dict:
    kn = {c: [] for c in KN_LETTERS}
    en = {chr(c): [] for c in range(65, 91)}
    en["#"] = []
    other = []
    for r in sorted(records, key=lambda x: x["title"].casefold()):
        uid = r["uid"]
        if r["az_kannada"]:
            kn[r["az_kannada"]].append(uid)
        if r["az_english"]:
            en[r["az_english"]].append(uid)
        if not r["az_kannada"] and not r["az_english"]:
            other.append(uid)
    return {
        "kannada": {k: v for k, v in kn.items() if v},
        "english": {k: v for k, v in en.items() if v},
        "other": other,
    }


# --------------------------------------------------------------------------
# Downloading
# --------------------------------------------------------------------------
def guess_ext(r: dict) -> str:
    ext = os.path.splitext(urlparse(r["audio_url"]).path)[1].lower()
    if ext in {".mp3", ".ogg", ".oga", ".opus", ".flac", ".wav", ".m4a", ".aac"}:
        return ext
    fmt = (r.get("file_format") or "").lower()
    for key, e in (("flac", ".flac"), ("ogg", ".ogg"), ("opus", ".opus"),
                   ("wav", ".wav"), ("mp3", ".mp3"), ("mpeg", ".mp3")):
        if key in fmt:
            return e
    return ".mp3"


def download(sess, r: dict, out_dir: Path, max_mb: float) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", r["title"])[:40].strip("_") or "track"
    h = hashlib.sha1(r["audio_url"].encode()).hexdigest()[:8]
    path = out_dir / f"{r['source']}_{slug}_{h}{guess_ext(r)}"
    if path.exists():
        return str(path)
    try:
        with sess.get(r["audio_url"], stream=True, timeout=60) as resp:
            if resp.status_code != 200:
                warn(f"download HTTP {resp.status_code}: {r['audio_url']}")
                return ""
            if "text/html" in resp.headers.get("content-type", ""):
                warn(f"not audio: {r['audio_url']}")
                return ""
            size = int(resp.headers.get("content-length") or 0)
            if size and size > max_mb * 1024 * 1024:
                warn(f"skipping {size/1e6:.0f} MB file: {r['title']}")
                return ""
            written = 0
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(1 << 16):
                    written += len(chunk)
                    if written > max_mb * 1024 * 1024:
                        raise RuntimeError("file exceeds size cap")
                    fh.write(chunk)
        return str(path)
    except Exception as e:  # noqa: BLE001
        warn(f"download failed for {r['title']}: {e}")
        if path.exists():
            path.unlink()
        return ""


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------
def write_outputs(out: Path, accepted: list[dict], rejected: list[dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in accepted:
        row = {k: r.get(k, "") for k in CSV_FIELDS}
        row["tags"] = "; ".join(r.get("tags", []))
        rows.append(row)
    with open(out / "catalog.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    with open(out / "catalog.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    with open(out / "rejected.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["source", "source_id", "title", "license_raw", "reason", "page_url"])
        for r in rejected:
            w.writerow([r["source"], r["source_id"], r["title"], r["license_raw"],
                        r["reason"], r["page_url"]])
    with open(out / "az_index.json", "w", encoding="utf-8") as f:
        json.dump(build_az(accepted), f, ensure_ascii=False, indent=2)
    lines = ["# Attribution\n",
             "Credits for the openly licensed tracks in this catalog. Keep these "
             "visible in your app (about screen and/or the track page).\n"]
    for r in sorted(accepted, key=lambda x: x["title"].casefold()):
        lic = LICENSE_LABELS.get(r["license"], r["license"])
        lic_txt = f"[{lic}]({r['license_url']})" if r["license_url"] else lic
        link = r["page_url"] or r["audio_url"]
        lines.append(f'- "{r["title"]}" by {r["creator"] or "Unknown"}, {lic_txt}. '
                     f"Source: {link}")
    (out / "ATTRIBUTION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Self-test (offline)
# --------------------------------------------------------------------------
def self_test() -> int:
    n = normalize_license
    assert n("https://creativecommons.org/licenses/by-sa/4.0/") == "by-sa"
    assert n("https://creativecommons.org/licenses/by-nc-nd/3.0/") == "by-nc-nd"
    assert n("http://creativecommons.org/publicdomain/zero/1.0/") == "cc0"
    assert n("https://creativecommons.org/publicdomain/mark/1.0/") == "pdm"
    assert n("CC BY-SA 4.0") == "by-sa"
    assert n("CC BY 3.0") == "by"
    assert n("CC0") == "cc0"
    assert n("Public domain") == "pdm"
    assert n("cc by-nc-sa") == "by-nc-sa"
    assert n("NOT_IN_COPYRIGHT") == "pdm"
    assert n("All rights reserved") is None
    assert n("", None) is None

    assert allowed_set(False, False) == {"cc0", "pdm", "by", "by-sa"}
    assert "by-nc" in allowed_set(True, False)
    assert "by-nd" not in allowed_set(True, False)

    assert kannada_signal({"title": "ಕನ್ನಡ ಹಾಡು"}, True) == "kannada-script"
    assert kannada_signal({"title": "Folk", "tags": ["Kannada"]}, True) == "keyword-title-tags"
    assert kannada_signal({"title": "x", "description": "a kannada song"}, True) is None
    assert kannada_signal({"title": "x", "description": "a kannada song"}, False)
    assert kannada_signal({"title": "x", "language": "kan"}, True) == "language-field"

    class A:  # fake args
        allow_nc = False
        allow_nd = False
        strict = False

    ok = make_record("t", 1, "ಅ test", "me", "CC BY 4.0", "", "", "http://x/a.mp3")
    assert decide(ok, A())[0]
    nc = make_record("t", 2, "ಅ test", "me", "CC BY-NC 4.0", "", "", "http://x/a.mp3")
    assert not decide(nc, A())[0]
    nolic = make_record("t", 3, "ಅ test", "me", "", "", "", "http://x/a.mp3")
    assert not decide(nolic, A())[0]

    assert first_kannada_letter("ಅಮ್ಮ") == "ಅ"
    assert first_kannada_letter("Amma") == ""
    assert "ಅ" in KN_LETTERS and "ಹ" in KN_LETTERS and "ಳ" in KN_LETTERS
    recs = []
    for i, t in enumerate(["ಅಮ್ಮ", "ಕನ್ನಡ", "Bhajan", "9 songs"]):
        r = make_record("t", i, t, "", "CC0", "", "", "u")
        r["uid"] = f"t:{i}"
        r["az_kannada"] = first_kannada_letter(t)
        r["az_english"] = english_key(t, "")
        recs.append(r)
    idx = build_az(recs)
    assert idx["kannada"]["ಅ"] == ["t:0"] and idx["kannada"]["ಕ"] == ["t:1"]
    assert idx["english"]["B"] == ["t:2"] and idx["english"]["#"] == ["t:3"]
    print("self-test passed")
    return 0


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="kannada_open_catalog", help="output folder")
    ap.add_argument("--sources", default="archive,commons,jamendo,openverse",
                    help="comma list from: " + ",".join(SOURCES))
    ap.add_argument("--limit", type=int, default=200,
                    help="max search hits per source query (default 200)")
    ap.add_argument("--allow-nc", action="store_true",
                    help="also keep NonCommercial licenses (NOT safe for a monetized app)")
    ap.add_argument("--allow-nd", action="store_true",
                    help="also keep NoDerivatives licenses (transcoding may count as a change)")
    ap.add_argument("--strict", action="store_true",
                    help="require the Kannada signal in title/tags/language, not description")
    ap.add_argument("--download", action="store_true", help="download accepted audio")
    ap.add_argument("--max-downloads", type=int, default=0, help="0 = no cap")
    ap.add_argument("--max-size-mb", type=float, default=60)
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between API calls")
    ap.add_argument("--self-test", action="store_true", help="run offline tests and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    names = [s.strip() for s in args.sources.split(",") if s.strip()]
    bad = [s for s in names if s not in SOURCES]
    if bad:
        ap.error(f"unknown source(s): {', '.join(bad)}")

    out = Path(args.out)
    sess = requests.Session()
    sess.headers["User-Agent"] = UA

    accepted, rejected = [], []
    seen_urls, seen_keys = set(), set()
    accept_fn = lambda r: decide(r, args)[0]  # noqa: E731

    for name in names:
        info(f"== {name}")
        before = len(accepted)
        for r in SOURCES[name](sess, args.limit, args.delay, accept_fn):
            ok, reason = decide(r, args)
            if not ok:
                r["reason"] = reason
                rejected.append(r)
                continue
            key = (re.sub(r"\W+", "", r["title"].casefold()), r["creator"].casefold())
            if r["audio_url"] in seen_urls or key in seen_keys:
                r["reason"] = "duplicate"
                rejected.append(r)
                continue
            seen_urls.add(r["audio_url"])
            seen_keys.add(key)
            r["uid"] = f"{r['source']}:{r['source_id']}"
            r["title_transliterated"] = transliterate(r["title"])
            r["az_kannada"] = first_kannada_letter(r["title"])
            r["az_english"] = english_key(r["title"], r["title_transliterated"])
            r["downloaded_path"] = ""
            accepted.append(r)
        info(f"   accepted {len(accepted) - before}")

    if args.download and accepted:
        audio_dir = out / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for r in accepted:
            if args.max_downloads and count >= args.max_downloads:
                break
            info(f"downloading: {r['title']}")
            r["downloaded_path"] = download(sess, r, audio_dir, args.max_size_mb)
            if r["downloaded_path"]:
                count += 1
            time.sleep(args.delay)
        info(f"downloaded {count} files")

    write_outputs(out, accepted, rejected)
    info(f"\nAccepted: {len(accepted)}   Rejected: {len(rejected)}   -> {out.resolve()}")
    if not accepted:
        info("Nothing matched. Try without --strict, or check rejected.csv for reasons.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
