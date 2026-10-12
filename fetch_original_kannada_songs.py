import json
import os
import time
import urllib.parse
import urllib.request

OUT_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\audio\originals"
os.makedirs(OUT_DIR, exist_ok=True)

# Search queries mapped to our CATALOG IDs to fetch real original Kannada studio recordings
SONG_QUERIES = [
    ("2601", "Varaha Roopam Kantara Ajaneesh Loknath"),
    ("2602", "Shaakuntle Sikkalu Sanjith Hegde Charan Raj"),
    ("2603", "Ekka Raja Rani Kailash Kher Kannada"),
    ("2604", "Gatiya Ilidu Ulidavaru Kandante Vijay Prakash"),
    ("2605", "belakina kavithe charan raj"),
    ("2606", "Om Shivoham Shankar Mahadevan Kannada"),
    ("2607", "Kodagana Koli Nungitha Raghu Dixit"),
    ("2401", "Dwapara Krishnam Pranaya Sakhi Jaskaran Singh"),
    ("2402", "Max Title Track Sudeep Ajaneesh"),
    ("2301", "Sapta Sagaradaache Ello Title Track Kapil Kapilan Charan Raj"),
    ("2302", "Pasandaagavne Kaatera Mangli"),
    ("2201", "Varaha Roopam Kantara Sai Vignesh"),
    ("2202", "Singara Siriye Kantara Vijay Prakash"),
    ("2203", "Toofan KGF Chapter 2 Kannada Ravi Basrur"),
    ("2204", "Ra Ra Rakkamma Vikrant Rona Kannada"),
    ("2101", "Sojugada Sooju Mallige Ananya Bhat"),
    ("1801", "Salaam Rocky Bhai KGF Kannada"),
    ("1802", "Tagaru Banthu Tagaru Charan Raj Anthony Daasan"),
    ("1701", "Bombe Helutaite Raajakumara Vijay Prakash"),
    ("1601", "Belageddu Kirik Party Vijay Prakash"),
    ("1201", "Vachana Venkatesh Kumar Kannada"),
    ("0801", "Krishna Nee Begane Baro Bombay Jayashri"),
    ("0601", "Mungaru Maleye Sonu Nigam"),
    ("0602", "Anisuthide Sonu Nigam Mungaru Male"),
    ("0401", "Jaya Bharata Jananiya Tanujate Kannada"),
    ("0101", "Jagadoddharana Vidyabhushana"),
    ("9501", "Chellidaru Malligeya Kannada Folk"),
    ("9301", "Huttidare Kannada Nadalli Rajkumar"),
    ("8801", "Anandamaya Ee Jagahrudaya C Ashwath"),
    ("8601", "Kaanada Kadalige C Ashwath"),
    ("8101", "Jotheyali Jotheyali Geetha SPB"),
    ("7901", "Ilidu Baa Thaayi C Ashwath PB Sreenivas"),
    ("7201", "Bangarada Manushya PB Sreenivas Rajkumar"),
    ("5401", "Bedara Kannappa Rajkumar Kannada"),
]

# Fallback pool of verified superhit Kannada searches if a niche query returns empty
FALLBACK_QUERIES = [
    "Ninnindale Sonu Nigam Kannada",
    "Paravashanadenu Sonu Nigam Paramathma",
    "NeeneModalu NeeneKone Kannada",
    "Kariya I Love You Kannada",
    "Yenagaliachhuagali Mussanje Maathu Sonu Nigam",
    "Usire Usire Hebbuli Kannada",
    "Hands Up Avane Srimannarayana",
    "Garbadhi KGF Kannada",
]

manifest = {}
used_urls = set()

def search_itunes(query):
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=song&country=IN&limit=8"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("results", [])

fallback_idx = 0

for sid, q in SONG_QUERIES:
    try:
        results = search_itunes(q)
        chosen = None
        for r in results:
            purl = r.get("previewUrl")
            if purl and purl not in used_urls:
                chosen = r
                break
        if not chosen and results:
            chosen = results[0]

        if not chosen:
            # Try fallback Kannada hit
            fq = FALLBACK_QUERIES[fallback_idx % len(FALLBACK_QUERIES)]
            fallback_idx += 1
            f_results = search_itunes(fq)
            for r in f_results:
                if r.get("previewUrl") and r.get("previewUrl") not in used_urls:
                    chosen = r
                    break
            if not chosen and f_results:
                chosen = f_results[0]

        if chosen and chosen.get("previewUrl"):
            purl = chosen["previewUrl"]
            used_urls.add(purl)
            art = chosen.get("artworkUrl100", "").replace("100x100bb", "600x600bb")
            local_file = os.path.join(OUT_DIR, f"{sid}.m4a")
            req_audio = urllib.request.Request(purl, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_audio, timeout=20) as aresp:
                with open(local_file, "wb") as f:
                    f.write(aresp.read())
            manifest[sid] = {
                "localAudio": f"audio/originals/{sid}.m4a",
                "remoteAudio": purl,
                "artworkUrl": art,
                "matchedTrack": chosen.get("trackName"),
                "matchedArtist": chosen.get("artistName"),
                "matchedAlbum": chosen.get("collectionName"),
            }
            print(f"[OK] {sid}: {chosen.get('trackName')} - {chosen.get('artistName')}")
        else:
            print(f"[MISS] {sid}: {q}")
    except Exception as e:
        print(f"[ERR] {sid}: {e}")
    time.sleep(0.2)

manifest_path = os.path.join(OUT_DIR, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Saved {len(manifest)} original Kannada tracks to {manifest_path}")
