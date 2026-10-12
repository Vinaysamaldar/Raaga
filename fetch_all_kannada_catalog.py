import base64
import html
import json
import os
import re
import urllib.parse
import urllib.request

from fetch_full_kannada_songs import decrypt_jiosaavn_url

# Queries covering ALL eras, genres, superstars, and music directors of Kannada cinema & music (1954–2026)
KANNADA_MASSIVE_QUERIES = [
    ("latest", "Kannada Top Hits 2025 2026", "feelgood"),
    ("latest", "Kantara Kannada Songs", "devotional"),
    ("latest", "Krishnam Pranaya Sakhi Kannada", "romance"),
    ("latest", "Sapta Sagaradaache Ello Kannada", "romance"),
    ("latest", "Kaatera Kannada Songs", "folk"),
    ("latest", "Vikrant Rona Kannada", "workout"),
    ("latest", "KGF Chapter 1 2 Kannada", "workout"),
    ("latest", "Raajakumara Puneeth Rajkumar", "feelgood"),
    ("latest", "Kirik Party Kannada", "feelgood"),
    ("latest", "Sanjith Hegde Kannada Hits", "romance"),
    ("latest", "Vijay Prakash Kannada Hits", "feelgood"),
    ("latest", "Arjun Janya Kannada Hits", "workout"),
    ("latest", "Ajaneesh Loknath Kannada", "romance"),
    ("latest", "Charan Raj Kannada Songs", "romance"),
    ("latest", "Ananya Bhat Kannada Folk", "folk"),
    ("latest", "Armaan Malik Kannada Songs", "romance"),
    ("latest", "Sonu Nigam Kannada Hits", "romance"),
    ("latest", "Shreya Ghoshal Kannada Hits", "romance"),
    ("latest", "Puneeth Rajkumar Super Hits Kannada", "workout"),
    ("latest", "Darshan Thoogudeepa Kannada Hits", "workout"),
    ("latest", "Kiccha Sudeep Kannada Hits", "workout"),
    ("latest", "Yash Kannada Songs", "workout"),
    ("latest", "Ganesh Mungaru Male Galipata Kannada", "romance"),
    ("old", "Dr Rajkumar Kannada Evergreen Hits", "devotional"),
    ("old", "Vishnuvardhan Kannada Super Hits", "feelgood"),
    ("old", "Shankar Nag Kannada Hits", "feelgood"),
    ("old", "Ravichandran Premaloka Kannada Hits", "romance"),
    ("old", "Upendra Kannada Hits", "workout"),
    ("old", "Shiva Rajkumar Om Janumada Jodi Kannada", "folk"),
    ("old", "S P Balasubrahmanyam Kannada Hits", "romance"),
    ("old", "S Janaki K S Chithra Kannada Hits", "romance"),
    ("old", "Rajesh Krishnan Kannada Hits", "romance"),
    ("old", "Hamsalekha Kannada Hits", "folk"),
    ("old", "Ilaiyaraaja Kannada Hits", "romance"),
    ("old", "C Ashwath Kannada Bhavageethe", "relax"),
    ("old", "Kuvempu Bendre G S Shivarudrappa Bhavageethe", "relax"),
    ("old", "Purandaradasa Kanakadasa Dasa Sahitya Kannada", "devotional"),
    ("old", "Raghu Dixit Shishunala Sharif Kannada", "folk"),
    ("old", "Kannada Rajyotsava Songs", "rajyotsava"),
    ("old", "Kannada Janapada Geethegalu Folk", "folk"),
]

# Helper to map first English letter to a Kannada Varnamale initial
EN_TO_KN_INIT = {
    'A': 'ಅ', 'B': 'ಬ', 'C': 'ಚ', 'D': 'ದ', 'E': 'ಎ', 'F': 'ಫ',
    'G': 'ಗ', 'H': 'ಹ', 'I': 'ಇ', 'J': 'ಜ', 'K': 'ಕ', 'L': 'ಲ',
    'M': 'ಮ', 'N': 'ನ', 'O': 'ಒ', 'P': 'ಪ', 'Q': 'ಕ', 'R': 'ರ',
    'S': 'ಸ', 'T': 'ತ', 'U': 'ಉ', 'V': 'ವ', 'W': 'ವ', 'X': 'ಕ್ಷ',
    'Y': 'ಯ', 'Z': 'ಜ'
}

def clean_text(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r'\s*\(From\s+"[^"]+"\)', '', s)
    return s.strip()

def fetch_all_kannada():
    seen_urls = set()
    seen_titles = set()
    all_tracks = []

    for era_hint, query, default_mood in KANNADA_MASSIVE_QUERIES:
        url = (
            "https://www.jiosaavn.com/api.php?__call=search.getResults"
            "&_format=json&_marker=0&api_version=4&ctx=web6dot0"
            f"&n=25&p=1&q={urllib.parse.quote(query)}"
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                results = data.get("results", [])
        except Exception as e:
            print(f"Query failed {query}: {e}")
            continue

        for item in results:
            lang = str(item.get("language", "")).lower()
            if lang and lang not in ("kannada", "sanskrit"):
                continue
            more = item.get("more_info", {}) or {}
            enc = more.get("encrypted_media_url")
            if not enc:
                continue
            try:
                stream320 = decrypt_jiosaavn_url(enc)
            except Exception:
                continue
            if not stream320 or stream320 in seen_urls:
                continue

            title_en = clean_text(item.get("title", ""))
            if not title_en:
                continue
            norm_title = re.sub(r'[^a-z0-9]', '', title_en.lower())
            if norm_title in seen_titles or len(norm_title) < 3:
                continue

            dur = int(more.get("duration") or 240)
            if dur < 60:
                continue

            yr_str = str(item.get("year") or "2022")
            try:
                year = int(yr_str[:4])
            except Exception:
                year = 2022 if era_hint == "latest" else 1995

            album = clean_text(more.get("album") or item.get("subtitle") or "Kannada Album")
            artist_map = more.get("artistMap", {}) or {}
            primary_artists = artist_map.get("primary_artists", [])
            if primary_artists:
                artist = ", ".join(clean_text(a.get("name", "")) for a in primary_artists[:2] if a.get("name"))
            else:
                artist = clean_text(more.get("music") or item.get("subtitle") or "Kannada Artist")
            if not artist:
                artist = "Kannada Artist"

            art_url = str(item.get("image") or "").replace("150x150", "500x500").replace("http://", "https://")
            stream160 = stream320.replace("_320.mp4", "_160.mp4")

            en_init = title_en[0].upper() if title_en[0].isalpha() else 'K'
            kn_init = EN_TO_KN_INIT.get(en_init, 'ಕ')

            seen_urls.add(stream320)
            seen_titles.add(norm_title)

            all_tracks.append({
                "titleEn": title_en,
                "titleKn": f"{title_en} ({kn_init})",
                "artist": artist,
                "movie": album,
                "year": year,
                "mood": default_mood,
                "duration": dur,
                "enInit": en_init,
                "knInit": kn_init,
                "cdn320Url": stream320,
                "cdn160Url": stream160,
                "artworkUrl": art_url,
            })

    print(f"Total unique full-length Kannada songs fetched: {len(all_tracks)}")
    out_path = os.path.join("mobile", "web_preview", "audio", "originals", "all_kannada_songs.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_tracks, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    fetch_all_kannada()
