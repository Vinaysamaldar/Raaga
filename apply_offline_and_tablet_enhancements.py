# Python script to apply tablet-grid classes and dynamic offline UI adaptations
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Add tablet-grid class to cards-carousel rows
carousels = [
    'id="featuredPlaylistsRow"',
    'id="latestCarouselRow"',
    'id="oldCarouselRow"',
    'id="danceRow"',
    'id="dasaraRow"',
    'id="heritageRow"',
    'id="trendingVideosRow"'
]

for c in carousels:
    text = text.replace(f'class="cards-carousel" {c}', f'class="cards-carousel tablet-grid" {c}')

# Update IDs on Home section headers
text = text.replace(
    '<div class="section-kicker" style="color:var(--saffron);">CURATED FOR KARNATAKA</div>\n            <div class="section-main-title">FEATURED PLAYLISTS FOR YOU</div>',
    '<div class="section-kicker" id="homeSec1Kicker" style="color:var(--saffron);">CURATED FOR KARNATAKA</div>\n            <div class="section-main-title" id="homeSec1Title">FEATURED PLAYLISTS FOR YOU</div>'
)

text = text.replace(
    '<div class="section-kicker" style="color:var(--accent-mint);">🔥 ಇತ್ತೀಚಿನ ಹೊಸ ಹಾಡುಗಳು • NEW & TRENDING ERA</div>\n              <div class="section-main-title">Latest Kannada Songs (2016–2026)</div>',
    '<div class="section-kicker" id="homeSec2Kicker" style="color:var(--accent-mint);">🔥 ಇತ್ತೀಚಿನ ಹೊಸ ಹಾಡುಗಳು • NEW & TRENDING ERA</div>\n              <div class="section-main-title" id="homeSec2Title">Latest Kannada Songs (2016–2026)</div>'
)

text = text.replace(
    '<div class="section-kicker" style="color:var(--saffron);">🏛️ ಹಳೆಯ ಮಧುರ ಗೀತೆಗಳು • GOLDEN CLASSICS ERA</div>\n              <div class="section-main-title">Old Evergreen Songs (1934–2015)</div>',
    '<div class="section-kicker" id="homeSec3Kicker" style="color:var(--saffron);">🏛️ ಹಳೆಯ ಮಧುರ ಗೀತೆಗಳು • GOLDEN CLASSICS ERA</div>\n              <div class="section-main-title" id="homeSec3Title">Old Evergreen Songs (1934–2015)</div>'
)

# Update renderHomeScreen to adapt headers when offlineMode is true
old_home_render = """      // Separate Latest Songs (2016–2026) and Old Evergreen Songs (1934–2015)
      const latestList = list.filter(s => s.year >= 2016);
      const oldList = list.filter(s => s.year < 2016);"""

new_home_render = """      // Adapt section headers if in offline mode
      const sec1K = document.getElementById('homeSec1Kicker');
      const sec1T = document.getElementById('homeSec1Title');
      const sec2K = document.getElementById('homeSec2Kicker');
      const sec2T = document.getElementById('homeSec2Title');
      const sec3K = document.getElementById('homeSec3Kicker');
      const sec3T = document.getElementById('homeSec3Title');

      if (state.offlineMode) {
        if (sec1K) sec1K.innerText = 'OFFLINE MASTER ARCHIVE';
        if (sec1T) sec1T.innerText = 'Downloaded for you';
        if (sec2K) sec2K.innerText = 'DOWNLOADED PLAYLISTS';
        if (sec2T) sec2T.innerText = 'Recently played (downloaded only)';
        if (sec3K) sec3K.innerText = 'OFFLINE HERITAGE';
        if (sec3T) sec3T.innerText = 'A-Z of downloaded songs';
      } else {
        if (sec1K) sec1K.innerText = 'CURATED FOR KARNATAKA';
        if (sec1T) sec1T.innerText = 'FEATURED PLAYLISTS FOR YOU';
        if (sec2K) sec2K.innerText = '🔥 ಇತ್ತೀಚಿನ ಹೊಸ ಹಾಡುಗಳು • NEW & TRENDING ERA';
        if (sec2T) sec2T.innerText = 'Latest Kannada Songs (2016–2026)';
        if (sec3K) sec3K.innerText = '🏛️ ಹಳೆಯ ಮಧುರ ಗೀತೆಗಳು • GOLDEN CLASSICS ERA';
        if (sec3T) sec3T.innerText = 'Old Evergreen Songs (1934–2015)';
      }

      // Separate Latest Songs (2016–2026) and Old Evergreen Songs (1934–2015)
      const latestList = list.filter(s => s.year >= 2016);
      const oldList = list.filter(s => s.year < 2016);"""

text = text.replace(old_home_render, new_home_render)

# Update search input placeholder on offlineMode
text = text.replace(
    "const q = (document.getElementById('searchInput').value || '').trim().toLowerCase();",
    "const searchEl = document.getElementById('searchInput');\n      if (searchEl) searchEl.placeholder = state.offlineMode ? 'Searching your downloads...' : 'Search Kannada songs...';\n      const q = (searchEl ? searchEl.value : '').trim().toLowerCase();"
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Applied offline and tablet enhancements.")
