# -*- coding: utf-8 -*-
"""
apply_user_customizations.py
Applies the following exact changes:
1. Remove "Kannada Musical Heritage (1934-2026)" block from Home.
2. Remove "All Songs, Latest Songs, Old Songs" era switcher bar from Home.
3. Remove "A to Z Browse" from navigation rail, search bar, and drawer.
4. Remove "Offline / Online mode" button from navigation rail and top banner.
5. Remove "Recognize" standalone button from navigation rail and bottom nav pill, and add the Recognize button right inside the Search bar.
"""

import os
import re

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. REMOVE KANNADA MUSICAL HERITAGE BLOCK
heritage_pattern = re.compile(
    r'<!-- =+ 4-PILLAR KANNADA MUSIC HERITAGE ARCHIVE.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)
if heritage_pattern.search(html):
    html = heritage_pattern.sub('', html)
    print('Removed Kannada Musical Heritage block.')
else:
    # Fallback search by kicker
    start_str = 'KANNADA MUSICAL HERITAGE (1934–2026)'
    idx = html.find(start_str)
    if idx != -1:
        # find outer container opening <div style="background:var(--surface);...
        open_div = html.rfind('<div style="background:var(--surface);', 0, idx)
        # find closing
        close_chips = html.find('id="homeSubArchiveChips"', idx)
        if close_chips != -1:
            close_div = html.find('</div>\n        </div>', close_chips)
            if close_div != -1:
                html = html[:open_div] + html[close_div + len('</div>\n        </div>'):]
                print('Removed Kannada Musical Heritage block via indices.')

# 2. REMOVE ERA SWITCHER BAR (All Songs, Latest Songs, Old Songs)
era_pattern = re.compile(
    r'<!-- Era Switcher Segmented Bar.*?<div class="era-glass-bar">.*?</div>\s*</div>',
    re.DOTALL
)
if era_pattern.search(html):
    html = era_pattern.sub('', html)
    print('Removed Era Switcher bar via pattern.')
else:
    idx_era = html.find('<div class="era-glass-bar">')
    if idx_era != -1:
        close_era = html.find('</div>', idx_era)
        # It has internal buttons, find matching closing div
        close_bar = html.find('</div>', html.find('</button>', idx_era))
        html = html[:idx_era] + html[close_bar + 6:]
        print('Removed Era Switcher bar via index.')

# 3. REMOVE OFFLINE SLIM BANNER
if '<div class="offline-slim-banner"' in html:
    idx_off = html.find('<div class="offline-slim-banner"')
    idx_off_end = html.find('</div>', idx_off)
    if idx_off != -1 and idx_off_end != -1:
        html = html[:idx_off] + html[idx_off_end + 6:]
        print('Removed top offline slim banner.')

# 4. UPDATE TABLET NAVIGATION RAIL:
# Remove Recognize button, remove A to Z Browse, remove MODE / Offline: OFF
rail_nav_old = '''          <div class="rail-menu">
            <button class="rail-btn active" id="rail-btn-home" onclick="switchNav('home')">
              <span class="rail-btn-icon">🏠</span><span class="rail-btn-label">Home</span>
            </button>
            <button class="rail-btn" id="rail-btn-search" onclick="switchNav('search')">
              <span class="rail-btn-icon">🔍</span><span class="rail-btn-label">Search</span>
            </button>
            <button class="rail-btn" id="rail-btn-recognize" onclick="switchNav('recognize')">
              <span class="rail-btn-icon">🎙️</span><span class="rail-btn-label">Recognize</span>
            </button>
            <button class="rail-btn" id="rail-btn-library" onclick="switchNav('library')">
              <span class="rail-btn-icon">📚</span><span class="rail-btn-label">Library</span>
            </button>
            <button class="rail-btn" id="rail-btn-az" onclick="switchNav('az')">
              <span class="rail-btn-icon">ಅ</span><span class="rail-btn-label">A to Z Browse</span>
            </button>
            <button class="rail-btn" id="rail-btn-downloads" onclick="switchNav('downloads')">
              <span class="rail-btn-icon">⬇</span><span class="rail-btn-label">Downloads</span>
            </button>
            <button class="rail-btn" id="rail-btn-more" onclick="switchNav('more')">
              <span class="rail-btn-icon">⚙️</span><span class="rail-btn-label">Settings</span>
            </button>
          </div>
        </div>

        <div style="padding:10px 4px;border-top:1px solid var(--border);">
          <div style="font-size:10.5px;color:var(--text-secondary);margin-bottom:6px;">MODE</div>
          <button class="pill-chip" style="width:100%;font-size:11px;padding:6px 8px;text-align:center;" onclick="toggleOfflineMode()" id="railOfflineBtn">
            ⚡ Offline: OFF
          </button>
        </div>'''

rail_nav_new = '''          <div class="rail-menu">
            <button class="rail-btn active" id="rail-btn-home" onclick="switchNav('home')">
              <span class="rail-btn-icon">🏠</span><span class="rail-btn-label">Home</span>
            </button>
            <button class="rail-btn" id="rail-btn-search" onclick="switchNav('search')">
              <span class="rail-btn-icon">🔍</span><span class="rail-btn-label">Search</span>
            </button>
            <button class="rail-btn" id="rail-btn-library" onclick="switchNav('library')">
              <span class="rail-btn-icon">📚</span><span class="rail-btn-label">Library</span>
            </button>
            <button class="rail-btn" id="rail-btn-downloads" onclick="switchNav('downloads')">
              <span class="rail-btn-icon">⬇</span><span class="rail-btn-label">Downloads</span>
            </button>
            <button class="rail-btn" id="rail-btn-more" onclick="switchNav('more')">
              <span class="rail-btn-icon">⚙️</span><span class="rail-btn-label">Settings</span>
            </button>
          </div>
        </div>'''

if rail_nav_old in html:
    html = html.replace(rail_nav_old, rail_nav_new, 1)
    print('Updated tablet-nav-rail cleanly.')
else:
    # Replace sub-parts
    html = re.sub(r'<button class="rail-btn"[^>]*id="rail-btn-recognize".*?</button>', '', html, flags=re.DOTALL)
    html = re.sub(r'<button class="rail-btn"[^>]*id="rail-btn-az".*?</button>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div style="padding:10px 4px;border-top:1px solid var\(--border\);".*?id="railOfflineBtn".*?</div>\s*</div>', '</div>', html, flags=re.DOTALL)
    print('Updated tablet-nav-rail via regex.')

# 5. UPDATE FLOATING BOTTOM NAV PILL:
# Remove Recognize button, add Downloads button
old_bottom_nav = '''      <nav class="floating-nav-pill">
        <button class="nav-pill-item active" id="nav-btn-home" onclick="switchNav('home')">
          <span class="nav-pill-icon">🏠</span>
          <span class="nav-pill-label">Home</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-search" onclick="switchNav('search')">
          <span class="nav-pill-icon">🔍</span>
          <span class="nav-pill-label">Search</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-recognize" onclick="switchNav('recognize')">
          <span class="nav-pill-icon">🎙️</span>
          <span class="nav-pill-label">Recognize</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-library" onclick="switchNav('library')">
          <span class="nav-pill-icon">📚</span>
          <span class="nav-pill-label">Library</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-more" onclick="switchNav('more')">
          <span class="nav-pill-icon">⚙️</span>
          <span class="nav-pill-label">More</span>
        </button>
      </nav>'''

new_bottom_nav = '''      <nav class="floating-nav-pill">
        <button class="nav-pill-item active" id="nav-btn-home" onclick="switchNav('home')">
          <span class="nav-pill-icon">🏠</span>
          <span class="nav-pill-label">Home</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-search" onclick="switchNav('search')">
          <span class="nav-pill-icon">🔍</span>
          <span class="nav-pill-label">Search</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-library" onclick="switchNav('library')">
          <span class="nav-pill-icon">📚</span>
          <span class="nav-pill-label">Library</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-downloads" onclick="switchNav('downloads')">
          <span class="nav-pill-icon">⬇</span>
          <span class="nav-pill-label">Downloads</span>
        </button>
        <button class="nav-pill-item" id="nav-btn-more" onclick="switchNav('more')">
          <span class="nav-pill-icon">⚙️</span>
          <span class="nav-pill-label">Settings</span>
        </button>
      </nav>'''

if old_bottom_nav in html:
    html = html.replace(old_bottom_nav, new_bottom_nav, 1)
    print('Updated floating-nav-pill cleanly.')
else:
    # Try regex on nav-btn-recognize
    html = re.sub(r'<button class="nav-pill-item"[^>]*id="nav-btn-recognize".*?</button>', '', html, flags=re.DOTALL)
    print('Removed nav-btn-recognize from bottom nav.')

# 6. UPDATE SEARCH BAR: ADD RECOGNIZE BUTTON TO SEARCH BAR & REMOVE A-Z DRAWER TOGGLE
old_search_bar = '''        <!-- Big Rounded Pill Search Bar -->
        <div style="display:flex;align-items:center;background:var(--surface);border-radius:var(--pill-radius);padding:6px 14px;border:1px solid var(--border);margin-bottom:12px;">
          <span style="font-size:15px;color:var(--text-secondary);margin-right:8px;">🔍</span>
          <input
            type="text"
            id="searchInput"
            placeholder="Search Kannada songs, ಕನ್ನಡ, artists..."
            oninput="renderSearchScreen()"
            style="flex:1;background:transparent;border:none;color:var(--text-primary);font-size:13.5px;outline:none;padding:6px 0;"
          />
          <button class="top-icon-btn" onclick="switchNav('recognize')" title="Voice / Music Search" style="width:30px;height:30px;">🎙️</button>
          <button class="top-icon-btn" onclick="toggleAzDrawer()" title="Language / A-to-Z ಅ–ಳ Options" style="width:30px;height:30px;">🌐</button>
        </div>'''

new_search_bar = '''        <!-- Big Rounded Pill Search Bar with Integrated Recognize Music Button -->
        <div style="display:flex;align-items:center;background:var(--surface);border-radius:var(--pill-radius);padding:6px 10px 6px 16px;border:1.5px solid var(--border);margin-bottom:12px;gap:8px;">
          <span style="font-size:16px;color:var(--text-secondary);">🔍</span>
          <input
            type="text"
            id="searchInput"
            placeholder="Search Kannada songs, ಕನ್ನಡ, artists, movies..."
            oninput="renderSearchScreen()"
            style="flex:1;background:transparent;border:none;color:var(--text-primary);font-size:14px;outline:none;padding:6px 0;"
          />
          <button class="pill-chip" onclick="switchNav('recognize')" title="Recognize playing music" style="padding:6px 12px;font-size:12px;font-weight:700;background:var(--accent-mint);color:var(--accent-mint-ink);border:none;display:flex;align-items:center;gap:6px;border-radius:999px;cursor:pointer;flex-shrink:0;">
            <span style="font-size:14px;">🎙️</span>
            <span>Recognize</span>
          </button>
        </div>'''

if old_search_bar in html:
    html = html.replace(old_search_bar, new_search_bar, 1)
    print('Updated search bar with integrated Recognize button.')
else:
    # Regex replacement for search bar container
    html = re.sub(
        r'<div style="display:flex;align-items:center;background:var\(--surface\);border-radius:var\(--pill-radius\);padding:6px 14px;border:1px solid var\(--border\);margin-bottom:12px;">.*?</div>\s*<!-- Search Result Filter Tabs -->',
        new_search_bar + '\n\n        <!-- Search Result Filter Tabs -->',
        html,
        flags=re.DOTALL
    )
    print('Updated search bar via regex.')

# 7. REMOVE COLLAPSIBLE A-TO-Z BOX IN SEARCH
az_box_pattern = re.compile(
    r'<!-- Collapsible A-to-Z Kannada Varnamale.*?<div id="azBrowserBox".*?</div>\s*</div>',
    re.DOTALL
)
if az_box_pattern.search(html):
    html = az_box_pattern.sub('', html)
    print('Removed collapsible A-to-Z box in search.')

# 8. UPDATE JAVASCRIPT: Ensure home panels always display naturally
home_panels_code = '''      const latestPanel = document.getElementById('homeLatestPanel');
      const oldPanel = document.getElementById('homeOldPanel');
      if (latestPanel) latestPanel.style.display = 'block';
      if (oldPanel) oldPanel.style.display = 'block';'''

old_panels_check = '''      latestPanel.style.display = (state.homeEra === 'all' || state.homeEra === 'latest') ? 'block' : 'none';
      oldPanel.style.display = (state.homeEra === 'all' || state.homeEra === 'old') ? 'block' : 'none';'''

if old_panels_check in html:
    html = html.replace(old_panels_check, home_panels_code, 1)
    print('Updated home panels display in JavaScript.')

# Also update setHomeEra to be safe without buttons
old_set_home_era = '''    function setHomeEra(era) {
      state.homeEra = era;
      document.getElementById('eraBtnAll').className = 'era-glass-btn' + (era === 'all' ? ' active' : '');
      document.getElementById('eraBtnLatest').className = 'era-glass-btn' + (era === 'latest' ? ' active' : '');
      document.getElementById('eraBtnOld').className = 'era-glass-btn' + (era === 'old' ? ' active-gold' : '');
      renderHomeScreen();
    }'''

new_set_home_era = '''    function setHomeEra(era) {
      state.homeEra = era;
      renderHomeScreen();
    }'''

if old_set_home_era in html:
    html = html.replace(old_set_home_era, new_set_home_era, 1)
    print('Updated setHomeEra function safely.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print('Saved all customizations to mobile/web_preview/index.html.')
