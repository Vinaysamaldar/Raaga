# Python script to implement responsive layout for Phones & Tablets, Download Options everywhere, Download Manager, and Offline Mode
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add CSS for Preview Shell, Device Switcher, Container Queries, 3-Pane Tablet Layout, Storage Bar, and Offline States
responsive_css = """
    /* ==================== RESPONSIVE LAYOUT & DEVICE SWITCHER ==================== */
    .preview-shell {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
      min-height: 100vh;
      padding: 10px 8px;
      box-sizing: border-box;
      background: #050807;
    }

    .device-switcher-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 5px 12px;
      border-radius: 999px;
      margin-bottom: 10px;
      flex-wrap: wrap;
      justify-content: center;
      z-index: 100;
    }
    .device-btn {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-secondary);
      font-size: 11px;
      font-weight: 700;
      padding: 5px 11px;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
    }
    .device-btn:hover { color: var(--text-primary); }
    .device-btn.active {
      background: var(--accent-mint);
      color: var(--accent-mint-ink);
    }

    /* Guided Prototype Walkthrough Pill Bar */
    .prototype-guide-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(242, 169, 0, 0.12);
      border: 1px solid rgba(242, 169, 0, 0.35);
      padding: 6px 14px;
      border-radius: 999px;
      margin-bottom: 10px;
      font-size: 11.5px;
      font-weight: 600;
      color: var(--saffron);
      flex-wrap: wrap;
      justify-content: center;
      z-index: 99;
    }
    .guide-step-chip {
      background: rgba(242, 169, 0, 0.2);
      border: 1px solid rgba(242, 169, 0, 0.4);
      color: var(--saffron);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 10.5px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .guide-step-chip:hover {
      background: var(--saffron);
      color: #0B1110;
    }

    /* Android Viewport Base & Responsive Width Variants */
    .android-viewport {
      width: 100%;
      max-width: 390px;
      height: 844px;
      background: var(--bg);
      border-radius: 38px;
      border: 6px solid #1E2624;
      box-shadow: 0 28px 80px rgba(0, 0, 0, 0.85);
      display: flex;
      flex-direction: row; /* enables side rail & persistent now playing on tablet */
      position: relative;
      overflow: hidden;
      box-sizing: border-box;
      transition: max-width 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), border-radius 0.3s ease;
      container-type: inline-size;
      container-name: raagaApp;
    }

    /* Medium Variant: 600-839px (Foldable / Small Tablet) */
    .android-viewport.layout-medium {
      max-width: 720px;
      border-radius: 28px;
    }

    /* Expanded Variant: 840px+ (Large Tablet / Landscape) */
    .android-viewport.layout-expanded {
      max-width: 1140px;
      border-radius: 24px;
    }

    /* Fluid Window Variant */
    .android-viewport.layout-fluid {
      max-width: 1400px;
      height: 94vh;
      border-radius: 20px;
    }

    /* ==================== 3-PANE LAYOUT COMPONENTS ==================== */
    /* PANE 1: LEFT NAVIGATION RAIL (Tablets & Desktops) */
    .tablet-nav-rail {
      display: none;
      flex-direction: column;
      justify-content: space-between;
      width: 88px;
      background: var(--surface);
      border-right: 1px solid var(--border);
      padding: 16px 8px;
      flex-shrink: 0;
      z-index: 30;
    }
    .android-viewport.layout-expanded .tablet-nav-rail,
    .android-viewport.layout-fluid .tablet-nav-rail {
      width: 220px;
      padding: 20px 14px;
    }

    .rail-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 4px 8px 18px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 12px;
    }
    .rail-logo-glyph {
      width: 36px;
      height: 36px;
      border-radius: 12px;
      background: var(--accent-mint);
      color: var(--accent-mint-ink);
      font-size: 18px;
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .rail-logo-text {
      display: none;
      font-size: 16px;
      font-weight: 800;
      color: var(--text-primary);
      white-space: nowrap;
    }
    .android-viewport.layout-expanded .rail-logo-text,
    .android-viewport.layout-fluid .rail-logo-text {
      display: block;
    }

    .rail-menu {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
    }
    .rail-btn {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      border-radius: 999px;
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.18s ease;
      white-space: nowrap;
    }
    .rail-btn:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
    }
    .rail-btn.active {
      background: var(--active-pill);
      color: var(--accent-mint);
      border-color: rgba(221, 230, 225, 0.15);
    }
    .rail-btn-icon {
      font-size: 19px;
      width: 26px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .rail-btn-label {
      display: none;
    }
    .android-viewport.layout-expanded .rail-btn-label,
    .android-viewport.layout-fluid .rail-btn-label {
      display: inline;
    }

    /* PANE 2: MAIN FLUID CONTENT CONTAINER */
    .main-content-flow {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      padding-top: 14px;
    }

    /* PANE 3: RIGHT PERSISTENT NOW PLAYING PANEL (Expanded Layout) */
    .tablet-persistent-player {
      display: none;
      flex-direction: column;
      width: 340px;
      background: var(--surface);
      border-left: 1px solid var(--border);
      padding: 18px 16px;
      flex-shrink: 0;
      overflow-y: auto;
      z-index: 30;
      scrollbar-width: none;
    }
    .tablet-persistent-player::-webkit-scrollbar { display: none; }

    /* Media / Container triggers for Left Rail & Persistent Right Player */
    @container raagaApp (min-width: 600px) {
      .tablet-nav-rail { display: flex; }
      .floating-nav-pill { display: none !important; }
      .floating-mini-player {
        position: relative !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        height: 64px !important;
        border-radius: 0 !important;
        border-left: none !important;
        border-right: none !important;
        border-bottom: none !important;
        margin: 0 !important;
        width: 100% !important;
      }
      .screens-wrapper { padding-bottom: 80px !important; }
      .cards-carousel.tablet-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)) !important;
        overflow-x: visible !important;
      }
      .cards-carousel.tablet-grid .chart-card { width: 100% !important; }
      .cards-carousel.tablet-grid .chart-art { width: 100% !important; height: 140px !important; }
      .cards-carousel.tablet-grid .video-poster-card { width: 100% !important; height: 210px !important; }
      .lib-grid { grid-template-columns: repeat(3, 1fr) !important; }
    }

    @container raagaApp (min-width: 840px) {
      .tablet-persistent-player { display: flex; }
      .floating-mini-player { display: none !important; }
      .screens-wrapper { padding-bottom: 24px !important; }
      .cards-carousel.tablet-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)) !important;
      }
      .lib-grid { grid-template-columns: repeat(4, 1fr) !important; }
    }

    /* Multi-Select Floating Bar for A-Z Screen */
    .multi-select-bar {
      position: absolute;
      left: 14px;
      right: 14px;
      bottom: 86px;
      background: var(--surface-elevated);
      border: 1px solid var(--saffron);
      border-radius: 999px;
      padding: 8px 14px;
      display: none;
      align-items: center;
      justify-content: space-between;
      z-index: 50;
      box-shadow: 0 8px 24px rgba(0,0,0,0.6);
      animation: popUp 0.25s ease;
    }
    .multi-select-bar.show { display: flex; }
    @keyframes popUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

    /* Segmented Storage Bar for Download Manager */
    .storage-segment-bar {
      height: 12px;
      border-radius: 999px;
      background: #141C1A;
      display: flex;
      overflow: hidden;
      margin: 8px 0;
    }
    .storage-seg-app { background: var(--saffron); width: 22%; }
    .storage-seg-other { background: #3E514B; width: 44%; }
    .storage-seg-free { background: var(--accent-mint); width: 34%; }

    /* Offline Dimmed Styling & Offline Indicators */
    .song-row.offline-dimmed {
      opacity: 0.38;
      filter: grayscale(40%);
    }
    .offline-sync-badge {
      font-size: 10px;
      color: var(--saffron);
      background: rgba(242, 169, 0, 0.15);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
      display: inline-block;
    }

    /* Download Progress Circle in Song Row */
    .dl-progress-ring {
      transform: rotate(-90deg);
    }
"""

if ".preview-shell" not in html:
    html = html.replace("</style>", responsive_css + "\n  </style>")
    print("Added responsive layout CSS.")

# 2. Wrap body inside .preview-shell with Device Switcher Toolbar and Prototype Guide Bar
old_body_start = """<body>
  <div class="android-viewport home-active" id="appViewport">"""

new_body_start = """<body>
  <div class="preview-shell">
    <!-- Responsive Device Viewport Switcher Toolbar (Phone, Small Tablet/Foldable, Large Tablet, Fluid) -->
    <div class="device-switcher-bar">
      <span style="font-size:11px;font-weight:800;color:var(--saffron);margin-right:4px;">RESPONSIVE BREAKPOINTS:</span>
      <button class="device-btn active" id="btnDevPhone" onclick="setDeviceViewport('phone')">📱 Phone (390×844)</button>
      <button class="device-btn" id="btnDevMedium" onclick="setDeviceViewport('medium')">📱 Small Tablet / Foldable (720px)</button>
      <button class="device-btn" id="btnDevExpanded" onclick="setDeviceViewport('expanded')">💻 Large Tablet (1140px 3-Pane)</button>
      <button class="device-btn" id="btnDevFluid" onclick="setDeviceViewport('fluid')">🖥️ 100% Fluid Window</button>
    </div>

    <!-- Prototype Walkthrough Step-by-Step Flow Guide -->
    <div class="prototype-guide-bar">
      <span>🚀 QUICK PROTOTYPE FLOW:</span>
      <span class="guide-step-chip" onclick="switchNav('az')">1. Browse A-Z</span>
      <span>→</span>
      <span class="guide-step-chip" onclick="enableAzMultiSelect()">2. Select Songs</span>
      <span>→</span>
      <span class="guide-step-chip" onclick="downloadSelectedAzSongs()">3. Download</span>
      <span>→</span>
      <span class="guide-step-chip" onclick="switchNav('downloads')">4. Download Manager</span>
      <span>→</span>
      <span class="guide-step-chip" onclick="toggleOfflineMode()">5. Switch Offline</span>
      <span>→</span>
      <span class="guide-step-chip" onclick="playRandomDownloadedSong()">6. Play Offline</span>
    </div>

    <div class="android-viewport home-active" id="appViewport">
      <!-- PANE 1: TABLET LEFT NAVIGATION RAIL (600px+ Small & Large Tablets) -->
      <nav class="tablet-nav-rail">
        <div>
          <div class="rail-logo">
            <div class="rail-logo-glyph">ಕ</div>
            <div class="rail-logo-text">Kannada Raaga</div>
          </div>
          <div class="rail-menu">
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
        </div>
      </nav>

      <!-- PANE 2: MAIN FLUID CONTENT AREA (Top Bar + Scrollable Screens) -->
      <div class="main-content-flow">"""

if old_body_start in html:
    html = html.replace(old_body_start, new_body_start)
    print("Wrapped body with preview shell and left navigation rail.")

# 3. Add Right Persistent Now Playing Panel for 840px+ Expanded Layout, closing main-content-flow
persistent_player_markup = """      </div> <!-- END .main-content-flow -->

      <!-- PANE 3: RIGHT PERSISTENT NOW PLAYING PANEL (840px+ Expanded Tablet Landscape) -->
      <aside class="tablet-persistent-player" id="tabletPersistentNowPlaying">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-size:12px;font-weight:700;color:var(--saffron);letter-spacing:0.8px;">NOW PLAYING</span>
          <span style="font-size:11px;color:var(--accent-mint);background:rgba(221,230,225,0.12);padding:2px 8px;border-radius:99px;" id="tabletAudioQualityTag">320 kbps Master</span>
        </div>

        <!-- Cover Art -->
        <div id="tabletNpArtBox" style="width:100%;height:220px;border-radius:20px;background:linear-gradient(135deg, #1E3F35, #0E1D18);background-size:cover;background-position:center;position:relative;overflow:hidden;margin-bottom:14px;border:1px solid var(--border);">
          <div style="position:absolute;bottom:10px;left:10px;right:10px;background:rgba(11,17,16,0.75);backdrop-filter:blur(10px);padding:6px 10px;border-radius:12px;display:flex;justify-content:space-between;font-size:10.5px;">
            <span id="tabletNpYear">2026 • KANNADA</span>
            <span style="color:var(--saffron);font-weight:700;">✓ Offline Ready</span>
          </div>
        </div>

        <!-- Title & Artist -->
        <div style="margin-bottom:12px;">
          <div style="font-size:17px;font-weight:800;color:var(--text-primary);line-height:1.3;" id="tabletNpTitleKn"></div>
          <div style="font-size:13px;font-weight:600;color:var(--accent-mint);margin-top:2px;" id="tabletNpTitleEn"></div>
          <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;" id="tabletNpArtist"></div>
        </div>

        <!-- Seek Slider -->
        <input
          type="range"
          id="tabletNpSeekSlider"
          min="0"
          max="100"
          step="0.1"
          value="0"
          onpointerdown="state.isSeeking = true"
          oninput="previewSeekTrackPct(this.value)"
          onchange="commitSeekTrackPct(this.value)"
          style="width:100%;accent-color:var(--accent-mint);cursor:pointer;"
        />
        <div style="display:flex;justify-content:space-between;font-size:10.5px;color:var(--text-secondary);margin:4px 0 12px;">
          <span id="tabletNpCurTime">0:00</span>
          <span id="tabletNpDurTime">4:28</span>
        </div>

        <!-- Transport Buttons -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <button class="transport-mode-btn" onclick="toggleShuffle(event)" title="Shuffle">🔀</button>
          <button class="top-icon-btn" onclick="prevTrack(event)" style="font-size:18px;">⏮</button>
          <button class="np-big-play" onclick="togglePlayPause(event)" id="tabletNpPlayBtn" style="width:54px !important;height:54px !important;font-size:22px !important;">▶</button>
          <button class="top-icon-btn" onclick="nextTrack(event)" style="font-size:18px;">⏭</button>
          <button class="transport-mode-btn active" onclick="toggleRepeat(event)" title="Repeat">🔁</button>
        </div>

        <!-- Secondary Actions -->
        <div style="display:flex;justify-content:space-between;gap:4px;background:var(--surface-elevated);padding:6px;border-radius:999px;margin-bottom:14px;">
          <button class="np-sec-btn heart-pop" id="tabletSecLikeBtn" onclick="toggleCurrentLike()" title="Like">♥</button>
          <button class="np-sec-btn" onclick="toggleDownload(event, state.currentSong.id)" title="Download">⬇</button>
          <button class="np-sec-btn" onclick="setTabletRightTab('lyrics')" id="tabBtnRightLyrics" title="Lyrics" style="font-size:12px;font-weight:700;">📝 Lyrics</button>
          <button class="np-sec-btn" onclick="setTabletRightTab('queue')" id="tabBtnRightQueue" title="Queue" style="font-size:12px;font-weight:700;">☰ Queue</button>
        </div>

        <!-- Tab Content: Synced Lyrics or Queue -->
        <div id="tabletLyricsPanel" style="flex:1;background:var(--surface-elevated);border-radius:16px;padding:12px;overflow-y:auto;max-height:220px;border:1px solid var(--border);">
          <div style="font-size:11px;font-weight:700;color:var(--saffron);margin-bottom:6px;">SYNCED KANNADA LYRICS</div>
          <div id="tabletLyricsBox" style="display:flex;flex-direction:column;gap:8px;"></div>
        </div>
        <div id="tabletQueuePanel" style="display:none;flex:1;background:var(--surface-elevated);border-radius:16px;padding:12px;overflow-y:auto;max-height:220px;border:1px solid var(--border);">
          <div style="font-size:11px;font-weight:700;color:var(--accent-mint);margin-bottom:6px;">UP NEXT IN QUEUE</div>
          <div id="tabletQueueBox" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
      </aside>
    </div> <!-- END #appViewport -->
  </div> <!-- END .preview-shell -->"""

if "tabletPersistentNowPlaying" not in html:
    html = html.replace("</div>\n</body>", persistent_player_markup + "\n</body>")
    print("Added persistent right Now Playing panel for tablets.")

# 4. Add Download Modals: Quality Selector, Insufficient Storage, Playlist Download Confirmation, Mobile Data Alert, Three-dot Action Sheet
download_modals_markup = """
    <!-- DOWNLOAD QUALITY PICKER BOTTOM SHEET -->
    <div class="collection-modal-backdrop" id="dlQualityModalBackdrop" onclick="closeDlQualityModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--accent-mint);">⬇ Choose Download Quality</div>
            <div style="font-size:11px;color:var(--text-secondary);" id="dlQualityTargetSong">Kannada Audio Stream</div>
          </div>
          <button class="pill-chip" onclick="closeDlQualityModal()">✕</button>
        </div>

        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px;">
          <label class="col-option-btn" style="cursor:pointer;" onclick="selectQualityOption('low')">
            <input type="radio" name="dlQualityRadio" id="radioDlLow" style="accent-color:var(--accent-mint);" />
            <div style="flex:1;margin-left:8px;">
              <div style="font-weight:700;">Low Quality (64 kbps Data Saver)</div>
              <div style="font-size:11px;color:var(--text-secondary);">~1.2 MB per song • Ideal for slow connections</div>
            </div>
          </label>
          <label class="col-option-btn" style="cursor:pointer;" onclick="selectQualityOption('medium')">
            <input type="radio" name="dlQualityRadio" id="radioDlMedium" style="accent-color:var(--accent-mint);" />
            <div style="flex:1;margin-left:8px;">
              <div style="font-weight:700;">Medium Quality (160 kbps Balanced)</div>
              <div style="font-size:11px;color:var(--text-secondary);">~2.8 MB per song • Standard listening</div>
            </div>
          </label>
          <label class="col-option-btn" style="cursor:pointer;" onclick="selectQualityOption('high')">
            <input type="radio" name="dlQualityRadio" id="radioDlHigh" checked style="accent-color:var(--accent-mint);" />
            <div style="flex:1;margin-left:8px;">
              <div style="font-weight:700;color:var(--saffron);">High Quality (320 kbps HD Master)</div>
              <div style="font-size:11px;color:var(--text-secondary);">~7.5 MB per song • Pristine studio audio</div>
            </div>
          </label>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
          <label style="cursor:pointer;display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);">
            <input type="checkbox" id="dlRememberChoice" checked style="accent-color:var(--saffron);" />
            Remember my choice for future downloads
          </label>
        </div>

        <button class="pill-chip active-mint" style="width:100%;padding:10px;font-size:13px;font-weight:800;" onclick="confirmDownloadWithQuality()">
          ⬇ Start Download Now
        </button>
      </div>
    </div>

    <!-- BULK DOWNLOAD PLAYLIST CONFIRMATION SHEET -->
    <div class="collection-modal-backdrop" id="dlBulkConfirmModalBackdrop" onclick="closeDlBulkConfirmModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="font-size:16px;font-weight:800;color:var(--saffron);margin-bottom:4px;">⬇ Download Collection</div>
        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:12px;" id="dlBulkConfirmDetails">
          Download 24 Kannada songs (Approx 86.4 MB)
        </div>
        <div style="display:flex;gap:8px;">
          <button class="pill-chip" style="flex:1;padding:10px;" onclick="closeDlBulkConfirmModal()">Cancel</button>
          <button class="pill-chip active-mint" style="flex:1;padding:10px;font-weight:800;" onclick="executeBulkCollectionDownload()">Confirm Download</button>
        </div>
      </div>
    </div>

    <!-- MOBILE DATA VS WI-FI ALERT DIALOG -->
    <div class="collection-modal-backdrop" id="dlMobileDataModalBackdrop" onclick="closeMobileDataModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="font-size:16px;font-weight:800;color:#ffb3c1;margin-bottom:4px;">📶 Cellular Data Notice</div>
        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:14px;">
          "Download over Wi-Fi only" is enabled, but your device is on mobile data. Would you like to proceed anyway or wait for Wi-Fi?
        </div>
        <div style="display:flex;gap:8px;">
          <button class="pill-chip" style="flex:1;padding:10px;" onclick="closeMobileDataModal()">Wait for Wi-Fi</button>
          <button class="pill-chip active" style="flex:1;padding:10px;font-weight:800;" onclick="overrideMobileDataDownload()">Download Anyway</button>
        </div>
      </div>
    </div>

    <!-- INSUFFICIENT STORAGE DIALOG -->
    <div class="collection-modal-backdrop" id="storageAlertModalBackdrop" onclick="closeStorageAlertModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="font-size:16px;font-weight:800;color:#ff4d6d;margin-bottom:4px;">⚠️ Insufficient Storage</div>
        <div style="font-size:12.5px;color:var(--text-primary);margin-bottom:6px;" id="storageAlertText">
          Space needed: 125 MB • Space available: 32 MB
        </div>
        <div style="font-size:11.5px;color:var(--text-secondary);margin-bottom:14px;">
          Clear existing downloaded tracks or cached songs in your Download Manager to free up device space.
        </div>
        <div style="display:flex;gap:8px;">
          <button class="pill-chip" style="flex:1;padding:10px;" onclick="closeStorageAlertModal()">Dismiss</button>
          <button class="pill-chip active-mint" style="flex:1;padding:10px;" onclick="closeStorageAlertModal();switchNav('downloads');">Manage Storage</button>
        </div>
      </div>
    </div>

    <!-- SONG ROW THREE-DOT CONTEXT ACTION SHEET -->
    <div class="collection-modal-backdrop" id="songActionsModalBackdrop" onclick="closeSongActionsModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()" id="songActionsModalContent"></div>
    </div>
"""

if "dlQualityModalBackdrop" not in html:
    html = html.replace("<!-- FLOATING TOAST PILL -->", download_modals_markup + "\n    <!-- FLOATING TOAST PILL -->")
    print("Added download options and alert modals.")

# 5. Add multi-select bar to Screen 5 (A to Z)
if "multiSelectBar" not in html:
    multi_select_markup = """
        <!-- Multi-Select Floating Bar for A-Z Screen -->
        <div class="multi-select-bar" id="multiSelectBar">
          <div>
            <span style="font-weight:800;color:var(--saffron);" id="multiSelectCount">0 Selected</span>
            <span style="font-size:11px;color:var(--text-secondary);margin-left:6px;" id="multiSelectSize">~0 MB</span>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="pill-chip active-mint" style="padding:4px 10px;font-size:11px;" onclick="downloadSelectedAzSongs()">⬇ Download</button>
            <button class="pill-chip" style="padding:4px 10px;font-size:11px;" onclick="clearAzSelection()">Cancel</button>
          </div>
        </div>
    """
    html = html.replace('<!-- Filtered Songs with Right-Edge Letter Scrubber -->', multi_select_markup + '\n        <!-- Filtered Songs with Right-Edge Letter Scrubber -->')
    print("Added multi-select floating bar to A-Z screen.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML structural updates applied.")
