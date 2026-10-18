# Python script to implement non-intrusive background-only ads, ad preferences, premium upsell, and lock-screen simulator
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add CSS for Ad States, Badges, and Lock Screen Simulator
ad_styles = """
    /* ==================== BACKGROUND-ONLY NON-INTRUSIVE ADS STYLING ==================== */
    .ad-badge {
      display: inline-flex;
      align-items: center;
      background: rgba(242, 169, 0, 0.18);
      color: var(--saffron);
      border: 1px solid rgba(242, 169, 0, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-right: 6px;
    }

    .ad-locked-ctrl {
      opacity: 0.28 !important;
      pointer-events: none !important;
      cursor: not-allowed !important;
    }

    .remove-ads-link {
      font-size: 11.5px;
      color: var(--accent-mint);
      text-decoration: underline;
      cursor: pointer;
      opacity: 0.9;
      transition: opacity 0.15s;
    }
    .remove-ads-link:hover { opacity: 1; }

    /* Lock Screen & Bluetooth Media Notification Simulator */
    .lock-screen-sim-card {
      background: rgba(18, 25, 23, 0.95);
      border: 1px solid rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(20px);
      border-radius: 20px;
      padding: 14px 16px;
      margin: 12px 0;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
    }

    /* Premium Banner Card (Inside Settings and Library only - never covering player) */
    .go-premium-card {
      background: linear-gradient(135deg, rgba(242, 169, 0, 0.14) 0%, rgba(221, 230, 225, 0.08) 100%);
      border: 1px solid rgba(242, 169, 0, 0.35);
      border-radius: 18px;
      padding: 14px;
      margin: 10px 0 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
"""

if ".ad-badge" not in code:
    code = code.replace("</style>", ad_styles + "\n  </style>")
    print("Added ads CSS styling.")

# 2. Add prototype buttons to walkthrough bar
old_guide_bar = """    <!-- Prototype Walkthrough Step-by-Step Flow Guide -->
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
    </div>"""

new_guide_bar = """    <!-- Prototype Walkthrough Step-by-Step Flow Guide -->
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
      <span>|</span>
      <span class="guide-step-chip" style="background:rgba(221,230,225,0.18);color:var(--accent-mint);border-color:var(--accent-mint);" onclick="simulateAudioAdBetweenSongs()">📻 Test Audio Ad (Between Songs)</span>
      <span class="guide-step-chip" onclick="openPremiumModal()">👑 Go Premium</span>
      <span class="guide-step-chip" onclick="openAdPreferencesModal()">⚙️ Ad Preferences</span>
      <span class="guide-step-chip" onclick="openLockScreenSimulator()">🔒 Lock Screen / Bluetooth State</span>
    </div>"""

code = code.replace(old_guide_bar, new_guide_bar)

# 3. Add Go Premium Cards inside Library and Settings (More)
premium_card_library = """
        <!-- Go Premium Banner Card (Inside Library only - never covering player) -->
        <div class="go-premium-card" id="libPremiumBanner">
          <div>
            <div style="font-size:13.5px;font-weight:800;color:var(--saffron);">👑 Go Ad-Free with Raaga Premium</div>
            <div style="font-size:11px;color:var(--text-secondary);margin-top:2px;">Zero audio ads • 320 kbps HD downloads • Unlocked archive</div>
          </div>
          <button class="pill-chip active" style="padding:6px 12px;font-size:11px;font-weight:800;" onclick="openPremiumModal()">Try Free</button>
        </div>
"""

if 'id="libPremiumBanner"' not in code:
    code = code.replace('<div class="lib-grid" id="libraryTilesGrid"></div>', '<div class="lib-grid" id="libraryTilesGrid"></div>\n' + premium_card_library)

# 4. Add Modals: Premium Modal, Ad Preferences Modal, Lock Screen Simulator Modal, First Launch Consent Modal
ads_modals = """
    <!-- PREMIUM / AD-FREE UPSELL BOTTOM SHEET -->
    <div class="collection-modal-backdrop" id="premiumModalBackdrop" onclick="closePremiumModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:17px;font-weight:800;color:var(--saffron);">👑 Kannada Raaga Premium</div>
            <div style="font-size:11.5px;color:var(--text-secondary);">Unlimited Kannada Heritage • 100% Ad-Free</div>
          </div>
          <button class="pill-chip" onclick="closePremiumModal()">✕</button>
        </div>

        <div style="background:var(--surface);padding:12px;border-radius:14px;border:1px solid rgba(242,169,0,0.3);margin-bottom:14px;">
          <div style="font-size:12px;font-weight:700;color:var(--accent-mint);margin-bottom:6px;">PREMIUM MEMBER PRIVILEGES:</div>
          <div style="font-size:11.5px;line-height:1.6;color:var(--text-primary);">
            ✓ <b>Zero Audio Ads</b>: Pure uninterrupted listening between songs<br>
            ✓ <b>320 kbps Studio Masters</b>: Download all Kannada tracks in lossless HD<br>
            ✓ <b>Full Offline Freedom</b>: No download expiry limits<br>
            ✓ <b>Direct Artist Support</b>: Proceeds support Kannada folk & classical preservation
          </div>
        </div>

        <div style="display:flex;gap:8px;margin-bottom:14px;">
          <div style="flex:1;background:var(--surface);padding:12px;border-radius:14px;border:1.5px solid var(--accent-mint);text-align:center;cursor:pointer;" onclick="selectPremiumTier('monthly')">
            <div style="font-size:10px;font-weight:800;color:var(--accent-mint);text-transform:uppercase;">Monthly Plan</div>
            <div style="font-size:18px;font-weight:800;color:var(--text-primary);margin:4px 0;">₹99 <small style="font-size:10px;color:var(--text-secondary);">/ mo</small></div>
            <div style="font-size:10px;color:var(--text-secondary);">7-Day Free Trial</div>
          </div>
          <div style="flex:1;background:var(--surface);padding:12px;border-radius:14px;border:1.5px solid var(--saffron);text-align:center;cursor:pointer;" onclick="selectPremiumTier('yearly')">
            <span style="font-size:9px;background:var(--saffron);color:#0B1110;padding:1px 6px;border-radius:99px;font-weight:800;">SAVE 33%</span>
            <div style="font-size:10px;font-weight:800;color:var(--saffron);text-transform:uppercase;margin-top:2px;">Yearly Plan</div>
            <div style="font-size:18px;font-weight:800;color:var(--text-primary);margin:4px 0;">₹799 <small style="font-size:10px;color:var(--text-secondary);">/ yr</small></div>
            <div style="font-size:10px;color:var(--text-secondary);">Best Value</div>
          </div>
        </div>

        <!-- Rewarded Ad Option -->
        <button class="col-option-btn" style="margin-bottom:12px;background:rgba(221,230,225,0.06);" onclick="watchRewardedAdForAdFreeHour()">
          <span>🎁 Watch one 15s audio ad → Unlock 1 hour ad-free</span>
          <span style="color:var(--accent-mint);font-size:11px;font-weight:700;">Free Reward</span>
        </button>

        <button class="pill-chip active-mint" style="width:100%;padding:12px;font-size:13px;font-weight:800;" onclick="activatePremiumMembership()">
          👑 Activate Premium Membership (₹99/mo)
        </button>
      </div>
    </div>

    <!-- AD PREFERENCES MODAL (Settings Screen) -->
    <div class="collection-modal-backdrop" id="adPreferencesModalBackdrop" onclick="closeAdPreferencesModal(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--accent-mint);">⚙️ Ad Preferences & Privacy</div>
            <div style="font-size:11px;color:var(--text-secondary);">Non-intrusive background audio ads policy</div>
          </div>
          <button class="pill-chip" onclick="closeAdPreferencesModal()">✕</button>
        </div>

        <div style="background:var(--surface);padding:12px;border-radius:14px;border:1px solid var(--border);font-size:11.5px;line-height:1.55;color:var(--text-secondary);margin-bottom:12px;">
          <b style="color:var(--text-primary);">Our Non-Intrusive Principles:</b><br>
          • <b>Audio Only</b>: Played strictly between songs (1 ad every 4–5 tracks).<br>
          • <b>Zero Interruptions</b>: Never stops a playing song in the middle.<br>
          • <b>Zero Cover Banners</b>: Never obscures your mini-player or controls.<br>
          • <b>Offline Caching</b>: Ads pre-fetch when online and report impressions when reconnected.
        </div>

        <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:14px;">
          <div style="background:var(--surface);padding:10px 14px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:13px;font-weight:700;color:var(--text-primary);">Personalized Audio Ads</div>
              <div style="font-size:11px;color:var(--text-secondary);">Tailor sponsors to your Kannada music taste</div>
            </div>
            <input type="checkbox" id="prefPersonalizedAds" checked onchange="togglePersonalizedAds(this.checked)" style="accent-color:var(--accent-mint);width:18px;height:18px;" />
          </div>

          <div style="background:var(--surface);padding:10px 14px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:13px;font-weight:700;color:var(--text-primary);">Age Under 18 / Child Safe Mode</div>
              <div style="font-size:11px;color:var(--text-secondary);">DPDP & GDPR rule: strictly disables ad tracking</div>
            </div>
            <input type="checkbox" id="prefUnder18" onchange="toggleUnder18Mode(this.checked)" style="accent-color:var(--saffron);width:18px;height:18px;" />
          </div>
        </div>

        <div style="background:var(--surface-elevated);padding:10px 12px;border-radius:12px;font-size:11px;color:var(--text-secondary);margin-bottom:12px;">
          📦 <b>Offline Ad Cache Status:</b> <span id="offlineAdCacheStatus">3 audio ads cached • 0 pending sync</span>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--accent-mint);">
          <span style="text-decoration:underline;cursor:pointer;" onclick="showRaagaToast('DPDP 2023 & GDPR Privacy Policy: Raaga complies with strict privacy rules.')">DPDP / GDPR Privacy Policy</span>
          <button class="pill-chip" onclick="simulateFailedAdSkip()">Test Ad Fail Fallback</button>
        </div>
      </div>
    </div>

    <!-- LOCK SCREEN & BLUETOOTH MEDIA METADATA SIMULATOR -->
    <div class="collection-modal-backdrop" id="lockScreenSimBackdrop" onclick="closeLockScreenSimulator(event)">
      <div class="collection-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--accent-mint);">🔒 Lock Screen & Bluetooth Car State</div>
            <div style="font-size:11px;color:var(--text-secondary);">Simulates background audio session notification card</div>
          </div>
          <button class="pill-chip" onclick="closeLockScreenSimulator()">✕</button>
        </div>

        <div class="lock-screen-sim-card">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div style="width:48px;height:48px;border-radius:12px;background:var(--surface-elevated);display:flex;align-items:center;justify-content:center;font-size:24px;" id="lockSimArt">
              🥛
            </div>
            <div style="flex:1;min-width:0;">
              <div style="font-size:10px;font-weight:800;color:var(--saffron);margin-bottom:2px;" id="lockSimBadge">AD • AUDIO SPONSOR</div>
              <div style="font-size:14px;font-weight:700;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" id="lockSimTitle">Nandini GoodLife Milk</div>
              <div style="font-size:11.5px;color:var(--text-secondary);" id="lockSimSubtitle">Ad • 12s remaining</div>
            </div>
            <button class="pill-chip active-mint" style="width:38px;height:38px;padding:0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;" onclick="togglePlayPause(event)" id="lockSimPlayBtn">
              ⏸
            </button>
          </div>
          <div style="height:4px;background:rgba(255,255,255,0.1);border-radius:99px;overflow:hidden;">
            <div style="width:58%;height:100%;background:var(--saffron);" id="lockSimBar"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--text-secondary);margin-top:4px;">
            <span id="lockSimElapsed">0:03</span>
            <span id="lockSimTotal">0:15</span>
          </div>
        </div>

        <div style="display:flex;gap:6px;">
          <button class="pill-chip" style="flex:1;font-size:11px;" onclick="simulatePhoneCallInterrupt()">📞 Simulate Phone Call (Pause)</button>
          <button class="pill-chip" style="flex:1;font-size:11px;" onclick="simulateDoNotDisturb()">🌙 Do Not Disturb</button>
        </div>
      </div>
    </div>
"""

if 'id="premiumModalBackdrop"' not in code:
    code = code.replace("<!-- FLOATING TOAST PILL -->", ads_modals + "\n    <!-- FLOATING TOAST PILL -->")
    print("Added ads modals.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("HTML with ads feature applied.")
