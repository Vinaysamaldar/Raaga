# Python script to update JavaScript functions in mobile/web_preview/index.html
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Add bottom50, azSortMode, recentSearches, etc. into state
if "bottom50:" not in code:
    code = code.replace(
        "top50: new Set(ALL_CORE_IDS),",
        "top50: new Set(ALL_CORE_IDS),\n      bottom50: new Set(ALL_CORE_IDS.slice(15, 30)),\n      azSortMode: 'title',\n      azSortDesc: false,\n      searchCategory: 'Songs',\n      wifiOnly: true,\n      queueDrawerOpen: false,\n      lyricsDrawerOpen: false,"
    )
    print("Added state keys.")

# Helper functions to inject
js_additions = """
    // ==================== RECENT SEARCHES & CATEGORIES ====================
    const RECENT_SEARCHES = ['Kantara', 'Sapta Sagaradaache Ello', 'Dwapara', 'Dr Rajkumar', 'Bhavageethe', 'Janapada'];
    const SEARCH_CATEGORIES = ['Songs', 'Albums', 'Artists', 'Playlists', 'Videos'];

    function onSearchFocus() {
      const container = document.getElementById('searchTypingContainer');
      if (container) {
        container.style.display = 'block';
        container.innerHTML = `
          <div style="font-size:11px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">Recent Searches</div>
          <div class="chips-scroll" style="margin-bottom:8px;">
            ${RECENT_SEARCHES.map(t => `<button class="pill-chip" onclick="applySearchTerm('${t}')">🕒 ${t}</button>`).join('')}
          </div>
          <div class="chips-scroll">
            ${SEARCH_CATEGORIES.map(c => `<button class="pill-chip ${state.searchCategory === c ? 'active-mint' : ''}" onclick="setSearchCategory('${c}')">${c}</button>`).join('')}
          </div>
        `;
      }
    }

    function applySearchTerm(term) {
      const input = document.getElementById('searchInput');
      if (input) {
        input.value = term;
        renderSearchScreen();
      }
    }

    function setSearchCategory(cat) {
      state.searchCategory = cat;
      onSearchFocus();
      renderSearchScreen();
    }

    function goBackOrHome() {
      if (state.activeTab === 'az' || state.activeTab === 'downloads' || state.activeTab === 'recognize') {
        switchNav('home');
      } else {
        switchNav('home');
      }
    }

    // ==================== SCREEN 5: A TO Z BROWSE LOGIC ====================
    function setAzScriptMode(mode) {
      state.azScript = mode;
      document.getElementById('azToggleKnBtn').classList.toggle('active', mode === 'kn');
      document.getElementById('azToggleEnBtn').classList.toggle('active', mode === 'en');
      renderAzScreen();
    }

    function cycleAzSort() {
      const modes = ['title', 'year', 'artist'];
      const next = modes[(modes.indexOf(state.azSortMode) + 1) % modes.length];
      state.azSortMode = next;
      const labels = { title: 'Sort: Title (A–Z)', year: 'Sort: Year (2026 First)', artist: 'Sort: Artist' };
      document.getElementById('azSortBtn').innerText = labels[next];
      renderAzScreen();
    }

    function selectAzTileLetter(l) {
      state.azLetter = l;
      renderAzScreen();
    }

    function renderAzScreen() {
      const letters = state.azScript === 'kn' ? KANNADA_LETTERS : ENGLISH_LETTERS;
      const gridEl = document.getElementById('azTilesGrid');
      if (gridEl) {
        gridEl.innerHTML = [
          `<div class="az-tile-56 ${state.azLetter === 'ALL' ? 'active' : ''}" onclick="selectAzTileLetter('ALL')">All</div>`,
          ...letters.map(l => `<div class="az-tile-56 ${state.azLetter === l ? 'active' : ''}" onclick="selectAzTileLetter('${l}')">${l}</div>`)
        ].join('');
      }

      document.getElementById('azActiveStickyLetter').innerText = state.azLetter === 'ALL' ? '✨ All Letters' : state.azLetter;

      let list = state.azLetter === 'ALL'
        ? [...CATALOG]
        : CATALOG.filter(s => (state.azScript === 'kn' ? s.knInit : s.enInit) === state.azLetter);

      if (state.azSortMode === 'title') {
        list.sort((a, b) => a.titleEn.localeCompare(b.titleEn));
      } else if (state.azSortMode === 'year') {
        list.sort((a, b) => b.year - a.year);
      } else if (state.azSortMode === 'artist') {
        list.sort((a, b) => a.artist.localeCompare(b.artist));
      }

      document.getElementById('azActiveLetterCount').innerText = `${list.length} songs found`;
      const rowsEl = document.getElementById('azSongRows');
      if (rowsEl) {
        rowsEl.innerHTML = list.length === 0
          ? `<div style="text-align:center;padding:36px 12px;color:var(--text-secondary);">No songs found for letter "${state.azLetter}"</div>`
          : list.slice(0, 100).map(renderSongRow).join('');
      }

      // Render right-edge quick scrubber
      const scrubberEl = document.getElementById('azLetterScrubber');
      if (scrubberEl) {
        const scrubLetters = state.azScript === 'kn' ? ['ಅ','ಇ','ಉ','ಎ','ಕ','ಚ','ತ','ನ','ಪ','ಮ','ರ','ಲ','ಸ','ಹ'] : ['A','C','E','G','I','K','M','P','R','S','T','V','Z'];
        scrubberEl.innerHTML = scrubLetters.map(ch => `
          <span style="cursor:pointer;padding:1px;${state.azLetter===ch?'color:var(--saffron);font-weight:900;':''}" onclick="selectAzTileLetter('${ch}')">${ch}</span>
        `).join('');
      }
    }

    // ==================== SCREEN 7: DOWNLOADS & OFFLINE LOGIC ====================
    function toggleWifiOnly(checked) {
      state.wifiOnly = checked;
      document.getElementById('wifiOnlyLabel').innerText = checked ? 'Enabled' : 'Disabled';
      showRaagaToast(checked ? '✓ Downloads set to Wi-Fi only' : '⚠️ Downloads enabled on cellular & Wi-Fi');
    }

    function renderDownloadsScreen() {
      const pageSwitch = document.getElementById('dlOfflinePageSwitch');
      if (pageSwitch) {
        pageSwitch.innerText = `Offline: ${state.offlineMode ? 'ON' : 'OFF'}`;
        pageSwitch.classList.toggle('active', state.offlineMode);
      }

      const dlSongs = CATALOG.filter(s => state.downloaded.has(s.id));
      const dlTitle = document.getElementById('dlSongsTitle');
      if (dlTitle) dlTitle.innerText = `Offline Tracks (${dlSongs.length})`;

      const listEl = document.getElementById('downloadsPageList');
      if (listEl) {
        if (dlSongs.length === 0) {
          listEl.innerHTML = `
            <div style="text-align:center;padding:48px 16px;color:var(--text-secondary);">
              <div style="font-size:42px;margin-bottom:10px;">📭</div>
              <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:4px;">No Offline Downloads</div>
              <div style="font-size:12px;">Tap the ⬇ download icon on any song to save for offline listening.</div>
            </div>
          `;
        } else {
          listEl.innerHTML = dlSongs.map(s => {
            const isPlayingThis = (state.currentSong.id === s.id) && state.isPlaying;
            return `
              <div class="song-row ${isPlayingThis ? 'playing' : ''}" onclick="playOrToggleSong(event, '${s.id}')">
                <div class="song-thumb" style="background:${s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient};position:relative;">
                  <svg width="56" height="56" style="position:absolute;inset:0;transform:rotate(-90deg);">
                    <circle cx="28" cy="28" r="23" fill="none" stroke="rgba(227,234,230,0.12)" stroke-width="2.5"></circle>
                    <circle cx="28" cy="28" r="23" fill="none" stroke="var(--accent-mint)" stroke-width="2.5" stroke-dasharray="144.5" stroke-dashoffset="0"></circle>
                  </svg>
                  <span style="font-size:14px;color:var(--accent-mint);font-weight:800;position:relative;z-index:2;">✓</span>
                </div>
                <div class="song-row-text">
                  <div class="song-row-kn">${s.titleKn}</div>
                  <div class="song-row-en">${s.titleEn} • <span style="color:var(--accent-mint);font-weight:700;">Downloaded</span></div>
                  <div class="song-row-meta">${s.artist} • ${s.movie}</div>
                </div>
                <div class="song-row-actions">
                  <button class="row-play-btn ${isPlayingThis ? 'playing' : ''}" onclick="playOrToggleSong(event, '${s.id}')">
                    ${isPlayingThis ? '⏸' : '▶'}
                  </button>
                  <button class="row-icon-btn done" onclick="toggleDownload(event, '${s.id}')" title="Remove download">
                    ✓
                  </button>
                  <button class="row-icon-btn" onclick="openSongCollectionModal(event, '${s.id}')" title="Actions">
                    •••
                  </button>
                </div>
              </div>
            `;
          }).join('');
        }
      }
    }

    // ==================== NOW PLAYING QUEUE & LYRICS DRAWERS ====================
    function toggleLyricsDrawer() {
      const el = document.getElementById('npLyricsDrawer');
      if (!el) return;
      state.lyricsDrawerOpen = el.style.display === 'none';
      el.style.display = state.lyricsDrawerOpen ? 'block' : 'none';
      if (state.lyricsDrawerOpen) {
        document.getElementById('npQueueDrawer').style.display = 'none';
        document.getElementById('npEqPanel').style.display = 'none';
        renderNowPlayingLyrics();
      }
    }

    function toggleQueueDrawer() {
      const el = document.getElementById('npQueueDrawer');
      if (!el) return;
      state.queueDrawerOpen = el.style.display === 'none';
      el.style.display = state.queueDrawerOpen ? 'block' : 'none';
      if (state.queueDrawerOpen) {
        document.getElementById('npLyricsDrawer').style.display = 'none';
        document.getElementById('npEqPanel').style.display = 'none';
        renderNowPlayingQueue();
      }
    }

    function renderNowPlayingLyrics() {
      const container = document.getElementById('npLyricsContent');
      if (!container) return;
      const lyrics = (state.currentSong && state.currentSong.lyrics) || [];
      if (lyrics.length === 0) {
        container.innerHTML = '<div style="color:var(--text-secondary);font-size:12px;">Instrumental / Audio playback active</div>';
        return;
      }
      const curSec = state.positionSec;
      container.innerHTML = lyrics.map((line, idx) => {
        const isCurrent = (curSec >= line.t && (idx === lyrics.length - 1 || curSec < lyrics[idx + 1].t));
        return `
          <div class="lyrics-line ${isCurrent ? 'active' : ''}">
            <div class="lyrics-kn" style="font-size:14px;line-height:1.35;">${line.kn}</div>
            <div class="lyrics-en" style="font-size:12px;color:var(--text-secondary);margin-top:2px;">${line.en}</div>
          </div>
        `;
      }).join('');
    }

    function renderNowPlayingQueue() {
      const container = document.getElementById('npQueueContent');
      if (!container) return;
      const curIdx = CATALOG.findIndex(s => s.id === state.currentSong.id);
      const queue = CATALOG.slice(curIdx + 1, curIdx + 15);
      container.innerHTML = queue.map((s, idx) => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
          <div style="min-width:0;flex:1;">
            <div style="font-size:12.5px;font-weight:700;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${idx + 1}. ${s.titleKn}</div>
            <div style="font-size:11px;color:var(--text-secondary);">${s.artist}</div>
          </div>
          <button class="pill-chip active-mint" style="padding:3px 9px;font-size:10.5px;" onclick="playOrToggleSong(event, '${s.id}')">▶ Play</button>
        </div>
      `).join('');
    }

    // ==================== TOP BAR MODAL CONTROLS ====================
    function openHistoryModal() {
      const backdrop = document.getElementById('historyModalBackdrop');
      const content = document.getElementById('historyModalContent');
      const historySongs = CATALOG.slice(0, 10);
      content.innerHTML = `
        <div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:10px;">Recently played tracks from your sessions:</div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          ${historySongs.map(s => `
            <div style="display:flex;justify-content:space-between;align-items:center;background:var(--surface);padding:8px 12px;border-radius:12px;border:1px solid var(--border);">
              <div style="min-width:0;">
                <div style="font-size:13px;font-weight:700;color:var(--text-primary);">${s.titleKn}</div>
                <div style="font-size:11px;color:var(--text-secondary);">${s.artist} • ${s.movie}</div>
              </div>
              <button class="pill-chip active-mint" style="padding:4px 9px;font-size:11px;" onclick="playOrToggleSong(event, '${s.id}');closeHistoryModal();">▶</button>
            </div>
          `).join('')}
        </div>
      `;
      backdrop.classList.add('open');
    }
    function closeHistoryModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('historyModalBackdrop').classList.remove('open');
    }

    function openListeningStatsModal() {
      const backdrop = document.getElementById('statsModalBackdrop');
      const content = document.getElementById('statsModalContent');
      content.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">
          <div style="background:var(--surface);padding:12px;border-radius:14px;border:1px solid var(--border);text-align:center;">
            <div style="font-size:24px;font-weight:800;color:var(--saffron);">48.5</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Hours Streamed</div>
          </div>
          <div style="background:var(--surface);padding:12px;border-radius:14px;border:1px solid var(--border);text-align:center;">
            <div style="font-size:24px;font-weight:800;color:var(--accent-mint);">${state.liked.size}</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Liked Songs</div>
          </div>
        </div>
        <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:6px;">Top Kannada Artists This Month:</div>
        <div style="display:flex;flex-direction:column;gap:6px;">
          <div style="display:flex;justify-content:space-between;background:var(--surface);padding:8px 12px;border-radius:10px;">
            <span>1. Dr. Rajkumar & P. B. Sreenivas</span><span style="color:var(--saffron);font-weight:700;">18 hrs</span>
          </div>
          <div style="display:flex;justify-content:space-between;background:var(--surface);padding:8px 12px;border-radius:10px;">
            <span>2. Vijay Prakash & Ajaneesh Loknath</span><span style="color:var(--accent-mint);font-weight:700;">14 hrs</span>
          </div>
          <div style="display:flex;justify-content:space-between;background:var(--surface);padding:8px 12px;border-radius:10px;">
            <span>3. C. Ashwath & Kuvempu Bhavageethe</span><span style="color:var(--saffron);font-weight:700;">9 hrs</span>
          </div>
          <div style="display:flex;justify-content:space-between;background:var(--surface);padding:8px 12px;border-radius:10px;">
            <span>4. Sanjith Hegde & Charan Raj</span><span style="color:var(--accent-mint);font-weight:700;">7.5 hrs</span>
          </div>
        </div>
      `;
      backdrop.classList.add('open');
    }
    function closeListeningStatsModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('statsModalBackdrop').classList.remove('open');
    }

    function openAccountModal() {
      const backdrop = document.getElementById('accountModalBackdrop');
      const content = document.getElementById('accountModalContent');
      content.innerHTML = `
        <div style="text-align:center;margin-bottom:14px;">
          <div style="width:64px;height:64px;border-radius:50%;background:var(--accent-mint);color:var(--accent-mint-ink);font-size:26px;font-weight:800;display:inline-flex;align-items:center;justify-content:center;margin-bottom:8px;">ಕ</div>
          <div style="font-size:16px;font-weight:800;color:var(--text-primary);">Kannada Music Aficionado</div>
          <div style="font-size:11.5px;color:var(--accent-mint);">Member since 2026 • Karnataka, India</div>
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <div style="background:var(--surface);padding:10px 14px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <span>Audio Master Streaming</span><span style="color:var(--saffron);font-weight:700;">320 kbps HD</span>
          </div>
          <div style="background:var(--surface);padding:10px 14px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <span>Bilingual Subtitles</span><span style="color:var(--accent-mint);font-weight:700;">Enabled (ಕನ್ನಡ/EN)</span>
          </div>
          <div style="background:var(--surface);padding:10px 14px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <span>Offline Encryption</span><span style="color:var(--text-secondary);font-weight:700;">AES-256</span>
          </div>
        </div>
      `;
      backdrop.classList.add('open');
    }
    function closeAccountModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('accountModalBackdrop').classList.remove('open');
    }
"""

if "function onSearchFocus" not in code:
    code = code.replace("function switchNav(tab) {", js_additions + "\n    function switchNav(tab) {")
    print("Injected helper functions.")

# Update switchNav to handle all tabs dynamically
new_switch_nav = """    function switchNav(tab) {
      state.activeTab = tab;
      closeNowPlaying();
      document.getElementById('appViewport').classList.toggle('home-active', tab === 'home');
      ['home', 'search', 'recognize', 'library', 'more', 'az', 'downloads'].forEach(t => {
        const pane = document.getElementById(`screen-${t}`);
        if (pane) pane.classList.toggle('active', t === tab);
        const navBtn = document.getElementById(`nav-btn-${t}`);
        if (navBtn) navBtn.classList.toggle('active', t === tab);
      });
      const titles = {
        home: 'Kannada Raaga',
        search: 'Search',
        recognize: 'Recognize Music',
        library: 'Library',
        more: 'More',
        az: 'A to Z Browse',
        downloads: 'Downloads & Offline'
      };
      const titleEl = document.getElementById('topScreenTitle');
      if (titleEl) titleEl.innerText = titles[tab] || 'Kannada Raaga';

      const backBtn = document.getElementById('topBackBtn');
      if (backBtn) {
        backBtn.style.display = (tab === 'az' || tab === 'downloads' || tab === 'recognize') ? 'flex' : 'none';
      }

      const statsBtn = document.getElementById('topStatsBtn');
      const accountBtn = document.getElementById('topAccountBtn');
      const settingsBtn = document.getElementById('topSettingsBtn');
      if (statsBtn && accountBtn && settingsBtn) {
        const isMinimalTop = (tab === 'recognize' || tab === 'az' || tab === 'downloads');
        statsBtn.style.display = isMinimalTop ? 'none' : 'flex';
        accountBtn.style.display = isMinimalTop ? 'none' : 'flex';
        settingsBtn.style.display = isMinimalTop ? 'none' : 'flex';
      }

      const fab = document.getElementById('libraryFab');
      if (fab) fab.classList.toggle('show', tab === 'library');

      renderAll();
    }"""

code = re.sub(r"function switchNav\(tab\)\s*\{[^}]*titles\[tab\];[^}]*renderAll\(\);\s*\}", new_switch_nav, code, flags=re.DOTALL)

# Update renderLibraryScreen tiles to match 56px rounded tiles: Liked, Downloaded, Exported, Cached, My top 50, My bottom 50, Local
new_lib_tiles = """      const tiles = [
        { id: 'liked', icon: '♥', label: 'Liked', count: state.liked.size },
        { id: 'downloaded', icon: '✓', label: 'Downloaded', count: state.downloaded.size },
        { id: 'exported', icon: '📤', label: 'Exported', count: state.exported.size },
        { id: 'cached', icon: '⚡', label: 'Cached', count: state.cached.size },
        { id: 'top50', icon: '📈', label: 'My top 50', count: state.top50.size },
        { id: 'bottom50', icon: '📉', label: 'My bottom 50', count: state.bottom50 ? state.bottom50.size : 20 },
        { id: 'local', icon: '📂', label: 'Local', count: state.localFiles ? state.localFiles.length : 0 }
      ];

      document.getElementById('libraryTilesGrid').innerHTML = tiles.map(t => {
        const isAct = state.libTileFilter === t.id;
        const color = t.id === 'liked' ? '#ff4d6d' : (t.id === 'downloaded' ? 'var(--accent-mint)' : (t.id === 'top50' ? 'var(--saffron)' : 'var(--text-secondary)'));
        return `
          <div class="lib-tile ${isAct ? 'active' : ''}" onclick="handleLibTileTap('${t.id}')">
            <span class="lib-tile-icon" style="color:${color};font-weight:800;">${t.icon}</span>
            <span class="lib-tile-label">${t.label}</span>
            <span style="font-size:11.5px;color:var(--text-secondary);margin-left:auto;font-weight:600;">${t.count}</span>
          </div>
        `;
      }).join('');"""

code = re.sub(r"const tiles = \[\s*\{ id: 'liked'[^;]*document\.getElementById\('libraryTilesGrid'\)\.innerHTML = tiles\.map[^;]*\}\)\.join\(''\);", new_lib_tiles, code, flags=re.DOTALL)

# Update chart card rendering for FEATURED PLAYLISTS FOR YOU
new_chart_card_render = """    function renderChartCard(s, badgeText) {
      return `
        <div class="chart-card" onclick="playOrToggleSong(event, '${s.id}')">
          <div class="chart-art" style="background:${s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient}">
            <span class="square-art-badge">${badgeText || 'CHART'}</span>
            ${s.artworkUrl ? '' : `<div class="square-art-glyph">${s.knInit}</div>`}
          </div>
          <div class="card-title">${s.titleEn}</div>
          <div class="card-sub">Chart • ${s.artist}</div>
        </div>
      `;
    }"""

if "function renderChartCard" not in code:
    code = code.replace("function renderSquareCard(s, badgeText) {", new_chart_card_render + "\n\n    function renderSquareCard(s, badgeText) {")
    print("Added renderChartCard.")

code = code.replace("renderSquareCard(CATALOG[idx], featuredBadges[i] || 'FEATURED')", "renderChartCard(CATALOG[idx], featuredBadges[i] || 'CHART')")

# Update renderAll to call renderAzScreen and renderDownloadsScreen
if "renderAzScreen();" not in code:
    code = code.replace(
        "renderLibraryScreen();\n      updatePlayerSurfaces();",
        "renderLibraryScreen();\n      renderAzScreen();\n      renderDownloadsScreen();\n      updatePlayerSurfaces();"
    )

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated JavaScript logic successfully.")
