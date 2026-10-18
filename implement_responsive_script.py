# Python script to add responsive controller & download logic to mobile/web_preview/index.html
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Add new state variables
new_state_keys = """      deviceLayout: 'phone', // 'phone', 'medium', 'expanded', 'fluid'
      dlFilterTab: 'all', // 'all', 'songs', 'albums', 'playlists', 'inprogress', 'failed'
      dlQualityChoice: 'high',
      rememberDlQuality: true,
      smartDownloads: true,
      inProgressDownloads: new Map([
        ['2401', { progress: 68, downloadedMb: 5.1, totalMb: 7.5, paused: false }],
        ['2301', { progress: 34, downloadedMb: 2.3, totalMb: 6.8, paused: false }]
      ]),
      failedDownloads: new Map([
        ['2602', { reason: 'Network timeout (No Wi-Fi)' }]
      ]),
      azMultiSelect: false,
      azSelectedIds: new Set(),
      offlinePendingSync: new Set(),
      tabletRightTab: 'lyrics', // 'lyrics' or 'queue'
"""

if "dlFilterTab:" not in js_code:
    js_code = js_code.replace("top50: new Set(ALL_CORE_IDS),", "top50: new Set(ALL_CORE_IDS),\n" + new_state_keys)
    print("Injected state keys.")

# Functions to add
functions_to_inject = """
    // ==================== RESPONSIVE DEVICE VIEWPORT SWITCHER ====================
    function setDeviceViewport(mode) {
      state.deviceLayout = mode;
      const vp = document.getElementById('appViewport');
      vp.classList.remove('layout-medium', 'layout-expanded', 'layout-fluid');
      ['phone', 'medium', 'expanded', 'fluid'].forEach(m => {
        const btn = document.getElementById(`btnDev${m.charAt(0).toUpperCase() + m.slice(1)}`);
        if (btn) btn.classList.toggle('active', m === mode);
      });
      if (mode === 'medium') vp.classList.add('layout-medium');
      else if (mode === 'expanded') vp.classList.add('layout-expanded');
      else if (mode === 'fluid') vp.classList.add('layout-fluid');

      updatePlayerSurfaces();
      renderAll();
      showRaagaToast(`📐 Switched to ${mode.toUpperCase()} responsive view`);
    }

    function setTabletRightTab(tab) {
      state.tabletRightTab = tab;
      const btnL = document.getElementById('tabBtnRightLyrics');
      const btnQ = document.getElementById('tabBtnRightQueue');
      const panelL = document.getElementById('tabletLyricsPanel');
      const panelQ = document.getElementById('tabletQueuePanel');
      if (btnL && btnQ && panelL && panelQ) {
        btnL.classList.toggle('active', tab === 'lyrics');
        btnQ.classList.toggle('active', tab === 'queue');
        panelL.style.display = tab === 'lyrics' ? 'block' : 'none';
        panelQ.style.display = tab === 'queue' ? 'block' : 'none';
      }
      updateTabletRightPanel();
    }

    function updateTabletRightPanel() {
      const s = state.currentSong;
      if (!s) return;
      const tKn = document.getElementById('tabletNpTitleKn');
      const tEn = document.getElementById('tabletNpTitleEn');
      const tArt = document.getElementById('tabletNpArtist');
      const tBox = document.getElementById('tabletNpArtBox');
      const tPlayBtn = document.getElementById('tabletNpPlayBtn');
      const tSlider = document.getElementById('tabletNpSeekSlider');
      const tCur = document.getElementById('tabletNpCurTime');
      const tDur = document.getElementById('tabletNpDurTime');

      if (tKn) tKn.innerText = s.titleKn;
      if (tEn) tEn.innerText = s.titleEn;
      if (tArt) tArt.innerText = `${s.artist} • ${s.movie} (${s.year})`;
      if (tPlayBtn) tPlayBtn.innerText = state.isPlaying ? '⏸' : '▶';
      if (tBox) {
        tBox.style.background = s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient;
      }
      if (tSlider && !state.isSeeking) {
        const pct = (state.positionSec / (s.duration || 240)) * 100;
        tSlider.value = pct;
      }
      const fmt = sec => `${Math.floor(sec / 60)}:${String(Math.floor(sec % 60)).padStart(2, '0')}`;
      if (tCur) tCur.innerText = fmt(state.positionSec);
      if (tDur) tDur.innerText = fmt(s.duration || 240);

      // Render lyrics in tablet panel
      const lBox = document.getElementById('tabletLyricsBox');
      if (lBox) {
        const lyrics = s.lyrics || [];
        lBox.innerHTML = lyrics.map((l, i) => {
          const isAct = (state.positionSec >= l.t && (i === lyrics.length - 1 || state.positionSec < lyrics[i+1].t));
          return `
            <div class="lyrics-line ${isAct ? 'active' : ''}">
              <div class="lyrics-kn" style="font-size:13.5px;">${l.kn}</div>
              <div class="lyrics-en" style="font-size:11.5px;color:var(--text-secondary);">${l.en}</div>
            </div>
          `;
        }).join('');
      }

      // Render queue in tablet panel
      const qBox = document.getElementById('tabletQueueBox');
      if (qBox) {
        const curIdx = CATALOG.findIndex(x => x.id === s.id);
        const qList = CATALOG.slice(curIdx + 1, curIdx + 12);
        qBox.innerHTML = qList.map((q, idx) => `
          <div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="min-width:0;flex:1;">
              <div style="font-size:12px;font-weight:700;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${idx + 1}. ${q.titleKn}</div>
              <div style="font-size:10.5px;color:var(--text-secondary);">${q.artist}</div>
            </div>
            <button class="pill-chip active-mint" style="padding:2px 7px;font-size:10px;" onclick="playOrToggleSong(event, '${q.id}')">▶</button>
          </div>
        `).join('');
      }
    }

    // ==================== DOWNLOAD OPTIONS & THREE-DOT ACTIONS ====================
    let targetDownloadSongId = null;

    function openSongActionsModal(e, id) {
      if (e) e.stopPropagation();
      const s = CATALOG.find(x => x.id === id) || state.currentSong;
      const isDl = state.downloaded.has(s.id);
      const isLiked = state.liked.has(s.id);
      const backdrop = document.getElementById('songActionsModalBackdrop');
      const content = document.getElementById('songActionsModalContent');

      content.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:15px;font-weight:800;color:var(--text-primary);">${s.titleKn} • ${s.titleEn}</div>
            <div style="font-size:11.5px;color:var(--text-secondary);">${s.artist} • ${s.movie} (${s.year})</div>
          </div>
          <button class="pill-chip" onclick="closeSongActionsModal()">Done</button>
        </div>

        <div style="display:flex;flex-direction:column;gap:6px;">
          <button class="col-option-btn" onclick="triggerDirectOrQualityDownload('${s.id}');closeSongActionsModal();">
            <span>${isDl ? '🗑️ Remove Download' : '⬇ Download Song (Offline)'}</span>
            <span style="color:var(--accent-mint);font-size:11.5px;">${isDl ? 'Saved' : 'HD Master'}</span>
          </button>
          <button class="col-option-btn" onclick="toggleSongLike(event, '${s.id}');closeSongActionsModal();">
            <span>${isLiked ? '💔 Remove from Liked' : '♥ Add to Liked Songs'}</span>
          </button>
          <button class="col-option-btn" onclick="openSongCollectionModal(event, '${s.id}');closeSongActionsModal();">
            <span>＋ Add to Playlist / Collection</span>
          </button>
          <button class="col-option-btn" onclick="addToNowPlayingQueue('${s.id}');closeSongActionsModal();">
            <span>☰ Play Next in Queue</span>
          </button>
          <button class="col-option-btn" onclick="shareSongTrack('${s.id}');closeSongActionsModal();">
            <span>↗ Share Kannada Song</span>
          </button>
          <button class="col-option-btn" onclick="applySearchTerm('${s.artist}');switchNav('search');closeSongActionsModal();">
            <span>👤 Go to Artist (${s.artist.split(',')[0]})</span>
          </button>
          <button class="col-option-btn" onclick="applySearchTerm('${s.movie}');switchNav('search');closeSongActionsModal();">
            <span>💿 Go to Album (${s.movie})</span>
          </button>
        </div>
      `;
      backdrop.classList.add('open');
    }
    function closeSongActionsModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('songActionsModalBackdrop').classList.remove('open');
    }

    function addToNowPlayingQueue(id) {
      showRaagaToast('✓ Added track to Up Next queue');
      updateTabletRightPanel();
    }

    function shareSongTrack(id) {
      const s = CATALOG.find(x => x.id === id);
      if (navigator.share) {
        navigator.share({ title: s.titleKn, text: `Listen to ${s.titleEn} on Kannada Raaga`, url: window.location.href });
      } else {
        showRaagaToast(`🔗 Copied share link for "${s.titleEn}"`);
      }
    }

    function triggerDirectOrQualityDownload(id) {
      if (state.downloaded.has(id)) {
        state.downloaded.delete(id);
        showRaagaToast('Removed track from downloads');
        saveLibraryState();
        renderAll();
        return;
      }
      if (state.wifiOnly && !navigator.onLine) {
        openMobileDataModal(id);
        return;
      }
      if (state.rememberDlQuality) {
        startSongDownloadProgress(id);
      } else {
        openDlQualityModal(id);
      }
    }

    function openDlQualityModal(id) {
      targetDownloadSongId = id;
      const s = CATALOG.find(x => x.id === id) || state.currentSong;
      const label = document.getElementById('dlQualityTargetSong');
      if (label) label.innerText = `${s.titleKn} (${s.titleEn})`;
      document.getElementById('dlQualityModalBackdrop').classList.add('open');
    }
    function closeDlQualityModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('dlQualityModalBackdrop').classList.remove('open');
    }

    function selectQualityOption(q) {
      state.dlQualityChoice = q;
    }

    function confirmDownloadWithQuality() {
      state.rememberDlQuality = document.getElementById('dlRememberChoice').checked;
      closeDlQualityModal();
      if (targetDownloadSongId) {
        startSongDownloadProgress(targetDownloadSongId);
        targetDownloadSongId = null;
      }
    }

    function startSongDownloadProgress(id) {
      state.downloading.add(id);
      const s = CATALOG.find(x => x.id === id);
      const estMb = state.dlQualityChoice === 'low' ? 1.2 : (state.dlQualityChoice === 'medium' ? 2.8 : 7.5);
      state.inProgressDownloads.set(id, { progress: 15, downloadedMb: (estMb * 0.15).toFixed(1), totalMb: estMb, paused: false });
      renderAll();
      showRaagaToast(`⬇ Downloading "${s.titleEn}" (${estMb} MB)...`);

      let progress = 15;
      const timer = setInterval(() => {
        const item = state.inProgressDownloads.get(id);
        if (!item || item.paused) return;
        progress += 28;
        if (progress >= 100) {
          clearInterval(timer);
          state.downloading.delete(id);
          state.inProgressDownloads.delete(id);
          state.downloaded.add(id);
          saveLibraryState();
          showRaagaToast(`✓ Downloaded "${s.titleEn}" (Ready Offline)`);
          renderAll();
        } else {
          item.progress = progress;
          item.downloadedMb = ((progress / 100) * estMb).toFixed(1);
          renderDownloadsScreen();
        }
      }, 450);
    }

    // ==================== BULK PLAYLIST & ALBUM DOWNLOAD ====================
    let bulkDownloadQueueIds = [];

    function promptBulkDownload(type, name, songIds) {
      bulkDownloadQueueIds = songIds || ALL_CORE_IDS.slice(0, 15);
      const count = bulkDownloadQueueIds.length;
      const estMb = (count * 3.6).toFixed(1);
      const detailEl = document.getElementById('dlBulkConfirmDetails');
      if (detailEl) {
        detailEl.innerText = `Download all ${count} tracks from "${name}" (Estimated size: ${estMb} MB • High Quality).`;
      }
      document.getElementById('dlBulkConfirmModalBackdrop').classList.add('open');
    }
    function closeDlBulkConfirmModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('dlBulkConfirmModalBackdrop').classList.remove('open');
    }
    function executeBulkCollectionDownload() {
      closeDlBulkConfirmModal();
      bulkDownloadQueueIds.forEach(id => {
        state.downloaded.add(id);
      });
      saveLibraryState();
      showRaagaToast(`✓ Downloaded ${bulkDownloadQueueIds.length} tracks for offline listening`);
      renderAll();
    }

    // ==================== A-Z MULTI-SELECT DOWNLOAD ====================
    function enableAzMultiSelect() {
      state.azMultiSelect = !state.azMultiSelect;
      if (!state.azMultiSelect) state.azSelectedIds.clear();
      renderAzScreen();
      updateMultiSelectBar();
    }

    function toggleSongSelect(id) {
      if (state.azSelectedIds.has(id)) state.azSelectedIds.delete(id);
      else state.azSelectedIds.add(id);
      renderAzScreen();
      updateMultiSelectBar();
    }

    function clearAzSelection() {
      state.azMultiSelect = false;
      state.azSelectedIds.clear();
      renderAzScreen();
      updateMultiSelectBar();
    }

    function updateMultiSelectBar() {
      const bar = document.getElementById('multiSelectBar');
      if (!bar) return;
      const count = state.azSelectedIds.size;
      bar.classList.toggle('show', state.azMultiSelect && count > 0);
      if (count > 0) {
        document.getElementById('multiSelectCount').innerText = `${count} Selected`;
        document.getElementById('multiSelectSize').innerText = `~${(count * 3.2).toFixed(1)} MB`;
      }
    }

    function downloadSelectedAzSongs() {
      const count = state.azSelectedIds.size;
      state.azSelectedIds.forEach(id => state.downloaded.add(id));
      saveLibraryState();
      showRaagaToast(`⬇ Downloaded ${count} selected Kannada songs`);
      clearAzSelection();
      renderAll();
    }

    // ==================== WI-FI & STORAGE DIALOGS ====================
    function openMobileDataModal(id) {
      targetDownloadSongId = id;
      document.getElementById('dlMobileDataModalBackdrop').classList.add('open');
    }
    function closeMobileDataModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('dlMobileDataModalBackdrop').classList.remove('open');
    }
    function overrideMobileDataDownload() {
      closeMobileDataModal();
      if (targetDownloadSongId) {
        startSongDownloadProgress(targetDownloadSongId);
        targetDownloadSongId = null;
      }
    }

    function simulateInsufficientStorage() {
      document.getElementById('storageAlertModalBackdrop').classList.add('open');
    }
    function closeStorageAlertModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('storageAlertModalBackdrop').classList.remove('open');
    }

    function toggleSmartDownloads(checked) {
      state.smartDownloads = checked;
      showRaagaToast(checked ? '✓ Smart Downloads enabled (Auto-downloads liked tracks)' : 'Smart Downloads disabled');
    }

    // ==================== DOWNLOAD MANAGER SCREEN ENHANCEMENTS ====================
    function setDlFilterTab(tab) {
      state.dlFilterTab = tab;
      renderDownloadsScreen();
    }

    function pauseResumeAllDownloads() {
      let anyActive = false;
      state.inProgressDownloads.forEach(item => {
        if (!item.paused) anyActive = true;
      });
      state.inProgressDownloads.forEach(item => {
        item.paused = anyActive;
      });
      renderDownloadsScreen();
      showRaagaToast(anyActive ? '⏸ Paused all active downloads' : '▶ Resumed all downloads');
    }

    function retryFailedDownload(id) {
      state.failedDownloads.delete(id);
      startSongDownloadProgress(id);
    }

    function deleteAllDownloadsPrompt() {
      if (confirm('Are you sure you want to delete all downloaded Kannada songs from device storage?')) {
        state.downloaded.clear();
        saveLibraryState();
        showRaagaToast('🗑️ Cleared all offline downloads');
        renderAll();
      }
    }

    // Enhanced renderDownloadsScreen
    function renderDownloadsScreen() {
      const pageSwitch = document.getElementById('dlOfflinePageSwitch');
      if (pageSwitch) {
        pageSwitch.innerText = `Offline Mode: ${state.offlineMode ? 'ON' : 'OFF'}`;
        pageSwitch.classList.toggle('active', state.offlineMode);
      }

      const listEl = document.getElementById('downloadsPageList');
      if (!listEl) return;

      const inProgressCount = state.inProgressDownloads.size;
      const failedCount = state.failedDownloads.size;
      const dlSongs = CATALOG.filter(s => state.downloaded.has(s.id));

      let filterBar = `
        <div class="chips-scroll" style="margin-bottom:12px;">
          ${['all', 'songs', 'albums', 'playlists', 'inprogress', 'failed'].map(f => `
            <button class="pill-chip ${state.dlFilterTab === f ? 'active-mint' : ''}" onclick="setDlFilterTab('${f}')">
              ${f.charAt(0).toUpperCase() + f.slice(1)} ${f === 'inprogress' ? `(${inProgressCount})` : (f === 'failed' ? `(${failedCount})` : '')}
            </button>
          `).join('')}
        </div>
      `;

      let inProgressSection = '';
      if (inProgressCount > 0 && (state.dlFilterTab === 'all' || state.dlFilterTab === 'inprogress')) {
        inProgressSection = `
          <div style="background:var(--surface);padding:12px;border-radius:16px;border:1px solid var(--saffron);margin-bottom:14px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span style="font-size:12px;font-weight:700;color:var(--saffron);">IN PROGRESS (${inProgressCount})</span>
              <button class="pill-chip" style="padding:3px 9px;font-size:10.5px;" onclick="pauseResumeAllDownloads()">Pause / Resume All</button>
            </div>
            ${Array.from(state.inProgressDownloads.entries()).map(([id, info]) => {
              const s = CATALOG.find(x => x.id === id) || { titleKn: 'Kannada Song', titleEn: 'Track', artist: 'Artist' };
              return `
                <div style="margin-bottom:8px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.06);">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:12.5px;font-weight:700;">${s.titleKn} (${s.titleEn})</div>
                    <span style="font-size:11px;color:var(--saffron);">${info.downloadedMb} / ${info.totalMb} MB (${info.progress}%)</span>
                  </div>
                  <div style="height:6px;background:var(--bg);border-radius:99px;overflow:hidden;margin:6px 0;">
                    <div style="width:${info.progress}%;height:100%;background:var(--saffron);"></div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;
      }

      let failedSection = '';
      if (failedCount > 0 && (state.dlFilterTab === 'all' || state.dlFilterTab === 'failed')) {
        failedSection = `
          <div style="background:rgba(217,4,41,0.12);padding:12px;border-radius:16px;border:1px solid rgba(217,4,41,0.4);margin-bottom:14px;">
            <div style="font-size:12px;font-weight:700;color:#ff4d6d;margin-bottom:8px;">FAILED DOWNLOADS (${failedCount})</div>
            ${Array.from(state.failedDownloads.entries()).map(([id, info]) => {
              const s = CATALOG.find(x => x.id === id) || { titleKn: 'Failed Song', titleEn: 'Track' };
              return `
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <div>
                    <div style="font-size:12.5px;font-weight:700;color:var(--text-primary);">${s.titleKn}</div>
                    <div style="font-size:10.5px;color:#ffb3c1;">⚠️ ${info.reason}</div>
                  </div>
                  <button class="pill-chip active" style="padding:4px 10px;font-size:11px;" onclick="retryFailedDownload('${id}')">Retry</button>
                </div>
              `;
            }).join('')}
          </div>
        `;
      }

      let emptyState = `
        <div style="text-align:center;padding:48px 16px;color:var(--text-secondary);">
          <div style="font-size:42px;margin-bottom:10px;">📭</div>
          <div style="font-size:16px;font-weight:700;color:var(--text-primary);margin-bottom:4px;">No Downloads Yet</div>
          <div style="font-size:12px;margin-bottom:14px;">Tap the ⬇ download icon on any song or playlist to save for offline listening.</div>
          <button class="pill-chip active-mint" onclick="switchNav('home')">Browse Kannada Songs</button>
        </div>
      `;

      let songsListHtml = dlSongs.length === 0
        ? emptyState
        : dlSongs.map(s => {
          const isPlayingThis = (state.currentSong.id === s.id) && state.isPlaying;
          return `
            <div class="song-row ${isPlayingThis ? 'playing' : ''}" onclick="playOrToggleSong(event, '${s.id}')">
              <div class="song-thumb" style="background:${s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient};position:relative;">
                <span style="font-size:14px;color:var(--accent-mint);font-weight:800;">✓</span>
              </div>
              <div class="song-row-text">
                <div class="song-row-kn">${s.titleKn}</div>
                <div class="song-row-en">${s.titleEn} • <span style="color:var(--accent-mint);font-weight:700;">Downloaded</span></div>
                <div class="song-row-meta">${s.artist} • <span style="color:var(--text-secondary);font-size:10.5px;">Expires Nov 15, 2026</span></div>
              </div>
              <div class="song-row-actions">
                <button class="row-play-btn ${isPlayingThis ? 'playing' : ''}" onclick="playOrToggleSong(event, '${s.id}')">
                  ${isPlayingThis ? '⏸' : '▶'}
                </button>
                <button class="row-icon-btn done" onclick="toggleDownload(event, '${s.id}')" title="Downloaded (Tap to remove)">
                  ✓
                </button>
                <button class="row-icon-btn" onclick="openSongActionsModal(event, '${s.id}')" title="Actions">
                  •••
                </button>
              </div>
            </div>
          `;
        }).join('');

      listEl.innerHTML = filterBar + inProgressSection + failedSection + songsListHtml + `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 4px 8px;">
          <button class="pill-chip" style="font-size:11px;" onclick="promptBulkDownload('playlist', 'All Kannada Classics', ALL_CORE_IDS.slice(0, 20))">⬇ Download Top 20 Playlist</button>
          <button class="pill-chip" style="font-size:11px;color:#ff4d6d;" onclick="deleteAllDownloadsPrompt()">🗑️ Delete All</button>
        </div>
      `;
    }

    // ==================== OFFLINE MODE ADAPTATIONS ====================
    let onlineBackTimer = null;

    function toggleOfflineMode() {
      state.offlineMode = !state.offlineMode;
      const banner = document.getElementById('offlineBanner');
      const railBtn = document.getElementById('railOfflineBtn');
      const dlSwitch = document.getElementById('dlOfflineSwitch');
      const pageSwitch = document.getElementById('dlOfflinePageSwitch');

      if (railBtn) railBtn.innerText = `⚡ Offline: ${state.offlineMode ? 'ON' : 'OFF'}`;
      if (dlSwitch) dlSwitch.innerText = `Offline Mode: ${state.offlineMode ? 'ON' : 'OFF'}`;
      if (pageSwitch) pageSwitch.innerText = `Offline: ${state.offlineMode ? 'ON' : 'OFF'}`;

      if (state.offlineMode) {
        banner.style.background = 'rgba(242, 169, 0, 0.16)';
        banner.style.borderColor = 'rgba(242, 169, 0, 0.35)';
        banner.style.color = 'var(--saffron)';
        banner.innerHTML = `
          <span>⚡ You're offline, showing downloaded songs</span>
          <button onclick="toggleOfflineMode()" style="background:none;border:none;color:var(--accent-mint);font-size:11px;font-weight:700;cursor:pointer;">Go Online</button>
        `;
        banner.classList.add('show');
        showRaagaToast('⚡ Offline Mode Active: Only downloaded songs available');
      } else {
        banner.style.background = 'rgba(34, 197, 94, 0.2)';
        banner.style.borderColor = 'rgba(34, 197, 94, 0.5)';
        banner.style.color = '#86efac';
        banner.innerHTML = `<span>✓ Back online. Synced all offline changes.</span>`;
        banner.classList.add('show');
        showRaagaToast('✓ Back Online: Live streaming & cloud archive restored');
        if (onlineBackTimer) clearTimeout(onlineBackTimer);
        onlineBackTimer = setTimeout(() => {
          banner.classList.remove('show');
        }, 2200);
      }

      renderAll();
    }

    function playRandomDownloadedSong() {
      const pool = CATALOG.filter(s => state.downloaded.has(s.id));
      if (!pool.length) return;
      const pick = pool[Math.floor(Math.random() * pool.length)];
      state.currentSong = pick;
      state.positionSec = 0;
      state.isPlaying = true;
      syncAudio(true);
      renderAll();
      showRaagaToast(`▶ Playing offline: "${pick.titleKn}"`);
    }
"""

if "function setDeviceViewport" not in js_code:
    js_code = js_code.replace("function renderAll() {", functions_to_inject + "\n    function renderAll() {")
    print("Injected responsive controller & download logic.")

# Update updatePlayerSurfaces to also update tablet persistent player
if "updateTabletRightPanel();" not in js_code:
    js_code = js_code.replace("function updatePlayerSurfaces() {", "function updatePlayerSurfaces() {\n      updateTabletRightPanel();")
    print("Hooked updateTabletRightPanel into updatePlayerSurfaces.")

# Update renderSongRow to support 3 download states + three-dot menu + offline dimming
updated_song_row = """    function renderSongRow(s) {
      const isCurrent = state.currentSong.id === s.id;
      const isPlayingThis = isCurrent && state.isPlaying;
      const isLiked = state.liked.has(s.id);
      const isDl = state.downloaded.has(s.id);
      const isDownloading = state.downloading.has(s.id);
      const offlineDim = state.offlineMode && !isDl;
      const inProg = state.inProgressDownloads.get(s.id);
      const isSelected = state.azSelectedIds.has(s.id);

      const titlePrimary = state.langMode === 'en' ? s.titleEn : s.titleKn;
      const titleSecondary = state.langMode === 'en' ? s.titleKn : s.titleEn;
      const durMin = Math.floor(s.duration / 60);
      const durSec = String(s.duration % 60).padStart(2, '0');

      let dlIcon = '⬇';
      if (isDownloading) {
        dlIcon = `<svg width="22" height="22" class="dl-progress-ring"><circle cx="11" cy="11" r="8" fill="none" stroke="rgba(227,234,230,0.15)" stroke-width="2"/><circle cx="11" cy="11" r="8" fill="none" stroke="var(--saffron)" stroke-width="2" stroke-dasharray="50.2" stroke-dashoffset="${50.2 * (1 - (inProg ? inProg.progress / 100 : 0.45))}"/></svg>`;
      } else if (isDl) {
        dlIcon = '✓';
      } else if (offlineDim) {
        dlIcon = '☁️⃠';
      }

      return `
        <div class="song-row ${isCurrent ? 'playing' : ''} ${offlineDim ? 'offline-dimmed' : ''}" onclick="${offlineDim ? `showRaagaToast('☁️⃠ Not available offline. Switch online to stream.')` : `playOrToggleSong(event, '${s.id}')`}">
          ${state.azMultiSelect ? `
            <input type="checkbox" ${isSelected ? 'checked' : ''} onclick="event.stopPropagation();toggleSongSelect('${s.id}')" style="width:18px;height:18px;accent-color:var(--saffron);margin-right:2px;cursor:pointer;" />
          ` : ''}
          <div class="song-thumb" style="background:${s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient}">
            ${s.artworkUrl ? '' : `<span class="song-thumb-kn" style="text-shadow:0 2px 6px #000;">${s.knInit}</span>`}
            <span class="song-thumb-year" style="text-shadow:0 1px 4px #000;background:rgba(0,0,0,0.55);padding:0 4px;border-radius:4px;">${s.year}</span>
          </div>
          <div class="song-row-text">
            <div class="song-row-kn">
              ${isPlayingThis ? `<span class="eq-bars"><span class="eq-bar"></span><span class="eq-bar"></span><span class="eq-bar"></span></span> ` : ''}
              ${titlePrimary}
            </div>
            <div class="song-row-en">${titleSecondary} ${isDl ? `<span style="color:var(--accent-mint);font-size:10.5px;">• ✓ Offline</span>` : ''}</div>
            <div class="song-row-meta">${s.artist} • ${s.movie} • <span style="color:var(--accent-mint);">${durMin}:${durSec}</span></div>
          </div>
          <div class="song-row-actions">
            <button class="row-play-btn ${isPlayingThis ? 'playing' : ''}" onclick="playOrToggleSong(event, '${s.id}')" title="${isPlayingThis ? 'Pause' : 'Play'}">
              ${isPlayingThis ? '⏸' : '▶'}
            </button>
            <button class="row-icon-btn ${isDl ? 'done' : ''}" onclick="event.stopPropagation();triggerDirectOrQualityDownload('${s.id}')" title="Download state">
              ${dlIcon}
            </button>
            <button class="row-icon-btn" onclick="openSongActionsModal(event, '${s.id}')" title="Actions menu">
              •••
            </button>
          </div>
        </div>
      `;
    }"""

js_code = re.sub(r"function renderSongRow\(s\)\s*\{[^}]*return `\s*<div class=\"song-row[^;]*\};\s*\}", updated_song_row, js_code, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Added all responsive & download JavaScript functions.")
