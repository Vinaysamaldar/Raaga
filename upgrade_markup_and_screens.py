# Python script to upgrade markup and screens in mobile/web_preview/index.html
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Top Bar
old_top_bar = """    <!-- Top App Bar -->
    <div class="top-bar">
      <div class="screen-title" id="topScreenTitle">Kannada Raaga</div>
      <input type="file" id="localMp3Input" accept="audio/*" style="display:none" onchange="loadUserMp3File(event)" />
    </div>"""

new_top_bar = """    <!-- Top App Bar -->
    <div class="top-bar">
      <div style="display:flex;align-items:center;gap:8px;min-width:0;">
        <button id="topBackBtn" class="top-icon-btn" onclick="goBackOrHome()" style="display:none;width:34px;height:34px;flex-shrink:0;" title="Back">←</button>
        <div class="screen-title" id="topScreenTitle" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">Kannada Raaga</div>
      </div>
      <div class="top-bar-icons" id="topBarIcons">
        <button class="top-icon-btn" onclick="openHistoryModal()" title="History">🕒</button>
        <button class="top-icon-btn" id="topStatsBtn" onclick="openListeningStatsModal()" title="Listening stats">📊</button>
        <button class="top-icon-btn" id="topAccountBtn" onclick="openAccountModal()" title="Account">👤</button>
        <button class="top-icon-btn" id="topSettingsBtn" onclick="switchNav('more')" title="Settings">⚙️</button>
      </div>
      <input type="file" id="localMp3Input" accept="audio/*" style="display:none" onchange="loadUserMp3File(event)" />
    </div>"""

if old_top_bar in text:
    text = text.replace(old_top_bar, new_top_bar)
    print("Replaced top bar.")

# 2. Add Screen 5 (A to Z Browse) and Screen 7 (Downloads & Offline) panes into screens-wrapper if not present
if 'id="screen-az"' not in text:
    az_and_downloads_markup = """
      <!-- ==================== SCREEN 5: A TO Z BROWSE ==================== -->
      <div class="screen-pane" id="screen-az">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <button class="pill-chip" onclick="switchNav('home')">← Home</button>
            <span style="font-size:16px;font-weight:700;">A to Z Browse</span>
          </div>
          <div style="display:flex;gap:4px;background:var(--surface);border-radius:999px;padding:3px;border:1px solid var(--border);">
            <button class="pill-chip active" id="azToggleKnBtn" style="padding:4px 10px;font-size:11px;" onclick="setAzScriptMode('kn')">ಕನ್ನಡ ಅ–ಳ</button>
            <button class="pill-chip" id="azToggleEnBtn" style="padding:4px 10px;font-size:11px;" onclick="setAzScriptMode('en')">English A–Z</button>
          </div>
        </div>

        <!-- 56px Rounded Tiles Grid for Letters -->
        <div id="azTilesGrid" style="display:grid;grid-template-columns:repeat(5, 1fr);gap:8px;margin-bottom:14px;"></div>

        <!-- Sticky Letter Header & Sort Menu -->
        <div style="position:sticky;top:0;background:var(--bg);z-index:10;padding:8px 0;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:24px;font-weight:800;color:var(--saffron);" id="azActiveStickyLetter">ಕ</span>
            <span style="font-size:12px;color:var(--text-secondary);" id="azActiveLetterCount">0 songs</span>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="pill-chip" style="padding:5px 10px;font-size:11px;" onclick="cycleAzSort()" id="azSortBtn">Sort: Title (A–Z)</button>
          </div>
        </div>

        <!-- Filtered Songs with Right-Edge Letter Scrubber -->
        <div style="position:relative;">
          <div id="azSongRows"></div>
          <div id="azLetterScrubber" style="position:fixed;right:14px;top:200px;bottom:200px;width:18px;display:flex;flex-direction:column;justify-content:space-between;align-items:center;font-size:9px;font-weight:700;color:var(--text-secondary);z-index:15;user-select:none;"></div>
        </div>
      </div>

      <!-- ==================== SCREEN 7: DOWNLOADS AND OFFLINE ==================== -->
      <div class="screen-pane" id="screen-downloads">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <button class="pill-chip" onclick="switchNav('library')">← Library</button>
          <span style="font-size:16px;font-weight:700;color:var(--saffron);">Downloads & Offline</span>
          <button class="pill-chip active" id="dlOfflinePageSwitch" onclick="toggleOfflineMode()">Offline: OFF</button>
        </div>

        <!-- Storage Usage Bar -->
        <div style="background:var(--surface);padding:14px;border-radius:var(--card-radius);border:1px solid var(--border);margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:13px;font-weight:700;">Device Storage</span>
            <span style="font-size:12px;color:var(--accent-mint);" id="storageUsageLabel">34.2 MB / 2.0 GB used</span>
          </div>
          <div style="height:8px;background:var(--bg);border-radius:99px;overflow:hidden;margin-bottom:10px;">
            <div style="width:28%;height:100%;background:var(--saffron);border-radius:99px;" id="storageUsageBar"></div>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:12px;color:var(--text-secondary);">Wi-Fi only downloads</span>
            <label style="cursor:pointer;display:flex;align-items:center;gap:6px;">
              <input type="checkbox" id="wifiOnlyCheckbox" checked onchange="toggleWifiOnly(this.checked)" style="accent-color:var(--accent-mint);" />
              <span style="font-size:12px;font-weight:600;" id="wifiOnlyLabel">Enabled</span>
            </label>
          </div>
        </div>

        <!-- Edge State Simulation Buttons -->
        <div style="display:flex;gap:6px;overflow-x:auto;padding-bottom:8px;margin-bottom:12px;">
          <button class="pill-chip" style="font-size:11px;" onclick="simulateEdgeState('skeleton')">💀 Skeleton State</button>
          <button class="pill-chip" style="font-size:11px;" onclick="simulateEdgeState('empty')">📭 Empty State</button>
          <button class="pill-chip" style="font-size:11px;" onclick="simulateEdgeState('failed')">⚠️ Failed + Retry</button>
          <button class="pill-chip" style="font-size:11px;" onclick="simulateEdgeState('full')">🛑 Storage Full</button>
        </div>
        <div id="downloadsEdgeAlert" style="display:none;margin-bottom:12px;padding:10px 12px;border-radius:14px;font-size:12px;line-height:1.4;"></div>

        <!-- Per-Song Rows with Progress Ring, Pause/Resume & Check when done -->
        <div class="section-header">
          <div class="section-main-title" id="dlSongsTitle">Offline Tracks</div>
          <button class="pill-chip" style="font-size:11px;" onclick="downloadAllTracks()">⬇ Download All</button>
        </div>
        <div id="downloadsPageList"></div>
      </div>
"""
    text = text.replace('<!-- ==================== SCREEN 5: MORE MENU', az_and_downloads_markup + '\n      <!-- ==================== SCREEN 8: MORE MENU')
    print("Added Screen 5 (A to Z) and Screen 7 (Downloads) markup.")

# 3. Update Now Playing secondary actions with: like, download, queue, lyrics, sleep timer, equalizer
old_np_sec = """      <!-- Secondary Actions: Add to Library, Download, Equalizer, Next Up -->
      <div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:14px;">
        <button class="pill-chip" style="flex:1;text-align:center;" onclick="openSongCollectionModal(event, state.currentSong.id)">＋ Library</button>
        <button class="pill-chip" style="flex:1;text-align:center;" onclick="toggleDownload(event, state.currentSong.id)">⬇ Download</button>
        <button class="pill-chip" style="flex:1;text-align:center;" onclick="toggleEqPanel()">🎛️ EQ</button>
        <button class="pill-chip" style="flex:1;text-align:center;" onclick="nextTrack(event)">☰ Next</button>
      </div>"""

new_np_sec = """      <!-- Secondary Actions: like, download, queue, lyrics, sleep timer and equalizer -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;background:var(--surface);padding:8px 14px;border-radius:999px;border:1px solid var(--border);">
        <button class="np-sec-btn heart-pop" id="npSecLikeBtn" onclick="toggleCurrentLike()" title="Like">♥</button>
        <button class="np-sec-btn" id="npSecDlBtn" onclick="toggleDownload(event, state.currentSong.id)" title="Download">⬇</button>
        <button class="np-sec-btn" onclick="toggleQueueDrawer()" title="Queue">☰</button>
        <button class="np-sec-btn" onclick="toggleLyricsDrawer()" title="Lyrics">📝</button>
        <button class="np-sec-btn" id="npSecSleepBtn" onclick="cycleSleepTimer()" title="Sleep Timer">🌙</button>
        <button class="np-sec-btn" onclick="toggleEqPanel()" title="Equalizer">🎛️</button>
      </div>

      <!-- Synced Lyrics Drawer (Active line illuminated with transliteration) -->
      <div id="npLyricsDrawer" style="display:none;background:var(--surface);padding:14px;border-radius:var(--card-radius);margin-bottom:12px;max-height:220px;overflow-y:auto;border:1px solid var(--border);">
        <div style="font-size:12px;font-weight:700;color:var(--saffron);margin-bottom:8px;">Bilingual Synced Lyrics (ಕನ್ನಡ & English)</div>
        <div id="npLyricsContent" style="display:flex;flex-direction:column;gap:8px;"></div>
      </div>

      <!-- Up Next Queue Drawer -->
      <div id="npQueueDrawer" style="display:none;background:var(--surface);padding:14px;border-radius:var(--card-radius);margin-bottom:12px;max-height:220px;overflow-y:auto;border:1px solid var(--border);">
        <div style="font-size:12px;font-weight:700;color:var(--accent-mint);margin-bottom:8px;">Up Next in Queue</div>
        <div id="npQueueContent"></div>
      </div>"""

if old_np_sec in text:
    text = text.replace(old_np_sec, new_np_sec)
    print("Replaced Now Playing secondary row.")

# 4. Add Top-Bar Modals (History, Listening Stats, Account)
modals_markup = """
    <!-- HISTORY MODAL -->
    <div class="collection-modal-backdrop" id="historyModalBackdrop" onclick="closeHistoryModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--accent-mint);">🕒 Listening History</div>
            <div style="font-size:11px;color:var(--text-secondary);">Recently played Kannada melodies</div>
          </div>
          <button class="pill-chip" onclick="closeHistoryModal()">✕ Close</button>
        </div>
        <div id="historyModalContent"></div>
      </div>
    </div>

    <!-- LISTENING STATS MODAL -->
    <div class="collection-modal-backdrop" id="statsModalBackdrop" onclick="closeListeningStatsModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--saffron);">📊 Listening Stats</div>
            <div style="font-size:11px;color:var(--text-secondary);">Your Kannada music streaming footprint</div>
          </div>
          <button class="pill-chip" onclick="closeListeningStatsModal()">✕ Close</button>
        </div>
        <div id="statsModalContent"></div>
      </div>
    </div>

    <!-- ACCOUNT MODAL -->
    <div class="collection-modal-backdrop" id="accountModalBackdrop" onclick="closeAccountModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--accent-mint);">👤 Account & Preferences</div>
            <div style="font-size:11px;color:var(--text-secondary);">Kannada Raaga Premium Master Edition</div>
          </div>
          <button class="pill-chip" onclick="closeAccountModal()">✕ Close</button>
        </div>
        <div id="accountModalContent"></div>
      </div>
    </div>
"""

if 'id="historyModalBackdrop"' not in text:
    text = text.replace('<!-- FLOATING TOAST PILL -->', modals_markup + '\n    <!-- FLOATING TOAST PILL -->')
    print("Added top-bar modals.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated markup and screens.")
