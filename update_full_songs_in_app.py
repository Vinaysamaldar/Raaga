import json
import os
import re
import urllib.parse
import urllib.request
from fetch_full_kannada_songs import decrypt_jiosaavn_url

OUT_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\audio\originals"
manifest_path = os.path.join(OUT_DIR, "manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Ensure 2606 also has a full-length 320kbps Kannada stream
api_url = "https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&n=5&q=Shiva+Tandava+Shankar+Mahadevan"
req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8"))
if data.get("results"):
    r = data["results"][0]
    enc = r.get("encrypted_media_url") or r.get("more_info", {}).get("encrypted_media_url")
    if enc:
        u320 = decrypt_jiosaavn_url(enc)
        manifest["2606"] = {
            "localAudio": u320,
            "remoteAudio": u320.replace("_320.mp4", "_160.mp4"),
            "fallbackLocal": "audio/originals/2606.m4a",
            "artworkUrl": (r.get("image") or "").replace("150x150", "500x500"),
            "duration": int(r.get("duration") or 270),
            "matchedTrack": r.get("song") or r.get("title") or "Shiva Tandava Stotram",
            "matchedArtist": r.get("singers") or "Shankar Mahadevan",
            "matchedAlbum": r.get("album") or "Shiva Tandava",
        }
        print(f"[FULL {manifest['2606']['duration']}s] 2606: {manifest['2606']['matchedTrack']}")

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# Now update index.html with the new full-length manifest and full duration!
html_path = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace ORIGINAL_MANIFEST object
pattern = r"const ORIGINAL_MANIFEST = \{.*?\n    \};\n"
replacement = "const ORIGINAL_MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n"
html, count = re.subn(pattern, lambda _: replacement, html, count=1, flags=re.DOTALL)
assert count == 1, "Failed to replace ORIGINAL_MANIFEST in index.html"

# Replace duration: 30 with duration: orig.duration || dur
html = html.replace("duration: 30,\n        fullDuration: dur,", "duration: orig.duration || dur,\n        fullDuration: orig.duration || dur,")

# Update getOrBuildSongAudioUrl to prioritize the full-length 320kbps stream
old_get_url = """    function getOrBuildSongAudioUrl(s) {
      if (s.customAudioUrl) return s.customAudioUrl;
      const isHttp = window.location.protocol.startsWith('http');
      if (isHttp && s.localAudio && !s._localFailed) return s.localAudio;
      if (s.remoteAudio && !s._remoteFailed) return s.remoteAudio;
      if (songAudioCache[s.id]) return songAudioCache[s.id];"""

new_get_url = """    function getOrBuildSongAudioUrl(s) {
      if (s.customAudioUrl) return s.customAudioUrl;
      if (s.localAudio && !s._localFailed) return s.localAudio;
      if (s.remoteAudio && !s._remoteFailed) return s.remoteAudio;
      if (s.fallbackLocal && !s._fallbackFailed) return s.fallbackLocal;
      if (songAudioCache[s.id]) return songAudioCache[s.id];"""

html = html.replace(old_get_url, new_get_url)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# Also update sample_kannada_catalog.dart with full-length 320kbps, 160kbps, and 96kbps URLs
dart_path = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\lib\data\catalog\sample_kannada_catalog.dart"
with open(dart_path, "r", encoding="utf-8") as f:
    dart = f.read()

map_lines = ["  static const Map<String, String> originalAudioStreams = {"]
for sid, info in manifest.items():
    map_lines.append(f"    '{sid}': '{info['localAudio']}',")
map_lines.append("  };")
new_map_str = "\n".join(map_lines)

dart = re.sub(
    r"  static const Map<String, String> originalAudioStreams = \{.*?\n  \};",
    lambda _: new_map_str,
    dart,
    count=1,
    flags=re.DOTALL,
)

dart = dart.replace(
    """      streams: AdaptiveStreams(
        low64kUrl: origStream,
        medium128kUrl: origStream,
        high320kUrl: origStream,
      ),""",
    """      streams: AdaptiveStreams(
        low64kUrl: origStream.replaceAll('_320.mp4', '_96.mp4'),
        medium128kUrl: origStream.replaceAll('_320.mp4', '_160.mp4'),
        high320kUrl: origStream,
      ),""",
)

with open(dart_path, "w", encoding="utf-8") as f:
    f.write(dart)

print("Successfully updated index.html and sample_kannada_catalog.dart with FULL-LENGTH 320kbps songs!")
