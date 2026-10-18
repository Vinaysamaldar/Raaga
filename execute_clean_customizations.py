# -*- coding: utf-8 -*-
"""
execute_clean_customizations.py
Applies exact string replacements using indices:
1. Removes "All Songs, Latest Songs, Old Songs" era switcher
2. Removes "Kannada Musical Heritage (1934–2026)" block
3. Removes Recognize and A-Z Browse from left rail
4. Removes Offline Mode button from left rail and removes top offline banner
5. Removes Recognize from bottom floating nav pill and adds Downloads
6. Replaces Search bar to include the Recognize button directly inside the search bar pill
7. Removes the A-Z collapsible browser box in search
"""

import os

FILE_PATH = os.path.join('mobile', 'web_preview', 'index.html')

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Top Offline Slim Banner
idx_off = text.find('<!-- Slim Offline Mode Banner -->')
if idx_off != -1:
    end_off = text.find('</div>', text.find('<div class="offline-slim-banner"', idx_off))
    if end_off != -1:
        text = text[:idx_off] + text[end_off + 6:]
        print('1. Removed top offline slim banner.')

# 2. Update Left Navigation Rail (remove Recognize, remove A to Z, remove MODE / Offline: OFF)
idx_rail_menu = text.find('<div class="rail-menu">')
if idx_rail_menu != -1:
    end_rail_nav = text.find('</nav>', idx_rail_menu)
    new_rail_content = '''<div class="rail-menu">
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
        </div>
      '''
    text = text[:idx_rail_menu] + new_rail_content + text[end_rail_nav:]
    print('2. Updated left navigation rail (removed recognize, A-Z, and offline mode).')

# 3. Remove Era Switcher Bar (All Songs, Latest Songs, Old Songs)
idx_era = text.find('<!-- Era Switcher Segmented Bar')
if idx_era != -1:
    end_era = text.find('<!-- ==================== 4-PILLAR', idx_era)
    if end_era != -1:
        text = text[:idx_era] + text[end_era:]
        print('3. Removed Era Switcher bar.')

# 4. Remove Kannada Musical Heritage Block
idx_her = text.find('<!-- ==================== 4-PILLAR KANNADA MUSIC HERITAGE')
if idx_her != -1:
    end_her = text.find('<!-- Section 1: FEATURED PLAYLISTS FOR YOU -->', idx_her)
    if end_her != -1:
        text = text[:idx_her] + text[end_her:]
        print('4. Removed Kannada Musical Heritage block.')

# 5. Update Search Bar (Add Recognize button inside search bar, remove A-Z globe button)
idx_sb = text.find('<!-- Big Rounded Pill Search Bar -->')
if idx_sb != -1:
    end_sb = text.find('<!-- Search Result Filter Tabs -->', idx_sb)
    new_sb_content = '''<!-- Big Rounded Pill Search Bar with Integrated Recognize Button -->
        <div style="display:flex;align-items:center;background:var(--surface);border-radius:var(--pill-radius);padding:6px 8px 6px 16px;border:1.5px solid var(--border);margin-bottom:12px;gap:8px;">
          <span style="font-size:16px;color:var(--text-secondary);">🔍</span>
          <input
            type="text"
            id="searchInput"
            placeholder="Search Kannada songs, ಕನ್ನಡ, artists..."
            oninput="renderSearchScreen()"
            style="flex:1;background:transparent;border:none;color:var(--text-primary);font-size:14px;outline:none;padding:6px 0;"
          />
          <button class="pill-chip" onclick="switchNav('recognize')" title="Recognize playing music" style="padding:6px 14px;font-size:12px;font-weight:700;background:var(--accent-mint);color:var(--accent-mint-ink);border:none;display:flex;align-items:center;gap:6px;border-radius:999px;cursor:pointer;flex-shrink:0;">
            <span style="font-size:14px;">🎙️</span>
            <span>Recognize</span>
          </button>
        </div>

        '''
    text = text[:idx_sb] + new_sb_content + text[end_sb:]
    print('5. Integrated Recognize button directly into search bar and removed A-Z button.')

# 6. Remove Collapsible A-to-Z Box in Search
idx_az_box = text.find('<!-- Collapsible A-to-Z Kannada Varnamale')
if idx_az_box != -1:
    end_az_box = text.find('<!-- Trending Kannada Music Videos Row -->', idx_az_box)
    if end_az_box != -1:
        text = text[:idx_az_box] + text[end_az_box:]
        print('6. Removed collapsible A-to-Z box from search.')

# 7. Update Bottom Floating Nav Pill (Remove Recognize, add Downloads)
idx_bnav = text.find('<nav class="floating-nav-pill">')
if idx_bnav != -1:
    end_bnav = text.find('</nav>', idx_bnav)
    new_bnav = '''<nav class="floating-nav-pill">
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
    text = text[:idx_bnav] + new_bnav + text[end_bnav + 6:]
    print('7. Updated floating bottom nav pill (removed recognize, added downloads).')

# 8. Update JavaScript to ensure home panels display without era buttons
old_panels_check = '''latestPanel.style.display = (state.homeEra === 'all' || state.homeEra === 'latest') ? 'block' : 'none';
      oldPanel.style.display = (state.homeEra === 'all' || state.homeEra === 'old') ? 'block' : 'none';'''

new_panels_check = '''if (latestPanel) latestPanel.style.display = 'block';
      if (oldPanel) oldPanel.style.display = 'block';'''

if old_panels_check in text:
    text = text.replace(old_panels_check, new_panels_check, 1)
    print('8. Updated JS home panels display.')

# Make setHomeEra safe without buttons
old_set_era = '''    function setHomeEra(era) {
      state.homeEra = era;
      document.getElementById('eraBtnAll').className = 'era-glass-btn' + (era === 'all' ? ' active' : '');
      document.getElementById('eraBtnLatest').className = 'era-glass-btn' + (era === 'latest' ? ' active' : '');
      document.getElementById('eraBtnOld').className = 'era-glass-btn' + (era === 'old' ? ' active-gold' : '');
      renderHomeScreen();
    }'''

new_set_era = '''    function setHomeEra(era) {
      state.homeEra = era;
      renderHomeScreen();
    }'''

if old_set_era in text:
    text = text.replace(old_set_era, new_set_era, 1)
    print('9. Updated setHomeEra safely.')

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully applied all customizations to index.html.')
