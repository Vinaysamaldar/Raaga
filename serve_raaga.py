import html
import http.server
import json
import os
import re
import socketserver
import urllib.parse
import urllib.request

from fetch_full_kannada_songs import decrypt_jiosaavn_url

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


class RaagaRangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/kannada-search":
            self.handle_kannada_search(parsed.query)
            return

        range_header = self.headers.get("Range")
        if not range_header:
            return super().do_GET()

        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().do_GET()

        try:
            file_size = os.path.getsize(path)
            m = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if not m:
                return super().do_GET()

            start_str, end_str = m.groups()
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            if start >= file_size:
                self.send_error(416, "Requested Range Not Satisfiable")
                return
            end = min(end, file_size - 1)
            length = end - start + 1

            ctype = self.guess_type(path)
            self.send_response(206, "Partial Content")
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.end_headers()

            with open(path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            pass

    def handle_kannada_search(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        q = (params.get("q", [""])[0] or "").strip()
        if not q:
            self._send_json([])
            return

        api_url = (
            "https://www.jiosaavn.com/api.php?__call=search.getResults"
            "&_format=json&_marker=0&api_version=4&ctx=web6dot0"
            f"&n=30&p=1&q={urllib.parse.quote(q + ' Kannada')}"
        )
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        tracks = []
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for item in data.get("results", []):
                    more = item.get("more_info", {}) or {}
                    enc = more.get("encrypted_media_url")
                    if not enc:
                        continue
                    try:
                        stream320 = decrypt_jiosaavn_url(enc)
                    except Exception:
                        continue
                    title_en = clean_text(item.get("title", ""))
                    if not title_en:
                        continue
                    dur = int(more.get("duration") or 240)
                    yr_str = str(item.get("year") or "2024")
                    year = int(yr_str[:4]) if yr_str[:4].isdigit() else 2024
                    album = clean_text(more.get("album") or item.get("subtitle") or "Kannada Original")
                    artist_map = more.get("artistMap", {}) or {}
                    p_artists = artist_map.get("primary_artists", [])
                    if p_artists:
                        artist = ", ".join(clean_text(a.get("name", "")) for a in p_artists[:2] if a.get("name"))
                    else:
                        artist = clean_text(more.get("music") or "Kannada Artist")
                    art_url = str(item.get("image") or "").replace("150x150", "500x500").replace("http://", "https://")
                    en_init = title_en[0].upper() if title_en[0].isalpha() else 'K'
                    kn_init = EN_TO_KN_INIT.get(en_init, 'ಕ')
                    tracks.append({
                        "id": "SAAVN-" + str(item.get("id", "")),
                        "titleEn": title_en,
                        "titleKn": f"{title_en} ({kn_init})",
                        "artist": artist,
                        "movie": album,
                        "year": year,
                        "mood": "feelgood",
                        "duration": dur,
                        "enInit": en_init,
                        "knInit": kn_init,
                        "cdn320Url": stream320,
                        "cdn160Url": stream320.replace("_320.mp4", "_160.mp4"),
                        "artworkUrl": art_url,
                    })
        except Exception:
            pass
        self._send_json(tracks)

    def _send_json(self, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    port = 8090
    print(f"Serving Kannada Raaga with HTTP 206 Byte-Range Seeking & Live Kannada Catalog API on port {port}...")
    server = ThreadedHTTPServer(("", port), RaagaRangeHTTPRequestHandler)
    server.serve_forever()
