# Python script to add Ads Engine, Ad Preferences, Premium logic, and between-song transition prototype
import re

file_path = r"mobile/web_preview/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

ads_js_logic = """
    // ==================== BACKGROUND-ONLY NON-INTRUSIVE ADS ENGINE ====================
    const SPONSOR_ADS = [
      {
        id: 'ad_nandini',
        brand: 'Nandini GoodLife Milk',
        tagline: 'ಶುದ್ಧ ಕರ್ನಾಟಕದ ಹಾಲು • Pure Karnataka Dairy Tradition',
        logo: '🥛',
        duration: 15
      },
      {
        id: 'ad_mysore_sandal',
        brand: 'Mysore Sandal Soap',
        tagline: 'ಕರ್ನಾಟಕದ ಗಂಧದ ಸುವಾಸನೆ • Heritage of Pure Sandalwood',
        logo: '🧼',
        duration: 15
      },
      {
        id: 'ad_karnataka_tourism',
        brand: 'Karnataka Tourism',
        tagline: 'ಒಂದು ರಾಜ್ಯ, ಹಲವು ಜಗತ್ತು • One State. Many Worlds.',
        logo: '🏛️',
        duration: 15
      }
    ];

    state.isAdPlaying = false;
    state.currentAd = null;
    state.adSecondsRemaining = 15;
    state.adTotalDuration = 15;
    state.isPremium = false;
    state.adFreeUntil = 0;
    state.adTimer = null;
    state.offlineAdImpressions = [];
    state.personalizedAds = true;
    state.under18Mode = false;

    // Simulate between-song transition: Song ends -> Audio Ad plays -> Next Song resumes
    function simulateAudioAdBetweenSongs() {
      if (state.isPremium) {
        showRaagaToast('👑 Premium Active: Audio ads are automatically skipped');
        nextTrack();
        return;
      }
      if (Date.now() < state.adFreeUntil) {
        const minsLeft = Math.ceil((state.adFreeUntil - Date.now()) / 60000);
        showRaagaToast(`🎁 Ad-Free Reward Active: ${minsLeft}m remaining without ads`);
        nextTrack();
        return;
      }

      // Pick a non-repeating sponsor ad
      const pick = SPONSOR_ADS[Math.floor(Math.random() * SPONSOR_ADS.length)];
      state.currentAd = pick;
      state.isAdPlaying = true;
      state.adTotalDuration = pick.duration;
      state.adSecondsRemaining = pick.duration;
      state.isPlaying = true;

      if (state.offlineMode) {
        state.offlineAdImpressions.push({ adId: pick.id, time: new Date().toISOString() });
        const cacheStatus = document.getElementById('offlineAdCacheStatus');
        if (cacheStatus) {
          cacheStatus.innerText = `3 audio ads cached • ${state.offlineAdImpressions.length} offline impressions (will sync when online)`;
        }
      }

      updatePlayerSurfaces();
      showRaagaToast(`📻 Audio Ad Session: ${pick.brand} (15s)`);

      if (state.adTimer) clearInterval(state.adTimer);
      state.adTimer = setInterval(() => {
        if (!state.isPlaying) return; // Respect pause / phone calls
        state.adSecondsRemaining--;
        updatePlayerSurfaces();

        if (state.adSecondsRemaining <= 0) {
          clearInterval(state.adTimer);
          state.isAdPlaying = false;
          state.currentAd = null;
          showRaagaToast('✓ Audio ad ended. Next Kannada song resuming.');
          nextTrack();
        }
      }, 1000);
    }

    function simulateFailedAdSkip() {
      if (state.isAdPlaying) {
        if (state.adTimer) clearInterval(state.adTimer);
        state.isAdPlaying = false;
        state.currentAd = null;
      }
      showRaagaToast('⚠️ Ad load failed (Network timeout). Skipped silently to next song.');
      closeAdPreferencesModal();
      nextTrack();
    }

    // ==================== PREMIUM / AD-FREE MEMBERSHIP ====================
    function openPremiumModal() {
      document.getElementById('premiumModalBackdrop').classList.add('open');
    }
    function closePremiumModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('premiumModalBackdrop').classList.remove('open');
    }

    function selectPremiumTier(tier) {
      showRaagaToast(`Selected ${tier.toUpperCase()} Plan (₹${tier === 'monthly' ? '99/mo' : '799/yr'})`);
    }

    function activatePremiumMembership() {
      state.isPremium = true;
      if (state.isAdPlaying) {
        if (state.adTimer) clearInterval(state.adTimer);
        state.isAdPlaying = false;
        state.currentAd = null;
        nextTrack();
      }
      closePremiumModal();
      const banner = document.getElementById('libPremiumBanner');
      if (banner) banner.style.display = 'none';
      renderAll();
      showRaagaToast('👑 Raaga Premium Activated: Zero ads & 320 kbps HD master audio!');
    }

    function watchRewardedAdForAdFreeHour() {
      closePremiumModal();
      showRaagaToast('🎁 Playing 15s rewarded audio ad...');
      simulateAudioAdBetweenSongs();
      state.adFreeUntil = Date.now() + 3600000; // 1 hour ad-free
      setTimeout(() => {
        showRaagaToast('🎉 1 Hour Ad-Free listening unlocked!');
      }, 15500);
    }

    // ==================== AD PREFERENCES & PRIVACY ====================
    function openAdPreferencesModal() {
      document.getElementById('adPreferencesModalBackdrop').classList.add('open');
    }
    function closeAdPreferencesModal(e) {
      if (e) e.stopPropagation();
      document.getElementById('adPreferencesModalBackdrop').classList.remove('open');
    }

    function togglePersonalizedAds(checked) {
      state.personalizedAds = checked;
      showRaagaToast(checked ? '✓ Personalized audio ads enabled' : 'Personalized ads disabled (Contextual only)');
    }

    function toggleUnder18Mode(checked) {
      state.under18Mode = checked;
      const persBox = document.getElementById('prefPersonalizedAds');
      if (persBox) {
        persBox.checked = !checked;
        persBox.disabled = checked;
      }
      state.personalizedAds = !checked;
      showRaagaToast(checked ? '🔒 Child Safe Mode enabled (All tracking disabled per DPDP/GDPR)' : 'Standard mode restored');
    }

    // ==================== LOCK SCREEN & BLUETOOTH SIMULATOR ====================
    function openLockScreenSimulator() {
      const backdrop = document.getElementById('lockScreenSimBackdrop');
      const art = document.getElementById('lockSimArt');
      const badge = document.getElementById('lockSimBadge');
      const title = document.getElementById('lockSimTitle');
      const sub = document.getElementById('lockSimSubtitle');
      const bar = document.getElementById('lockSimBar');
      const elapsed = document.getElementById('lockSimElapsed');
      const total = document.getElementById('lockSimTotal');
      const playBtn = document.getElementById('lockSimPlayBtn');

      if (state.isAdPlaying && state.currentAd) {
        art.innerText = state.currentAd.logo;
        badge.innerText = 'AD • AUDIO SPONSOR';
        badge.style.color = 'var(--saffron)';
        title.innerText = state.currentAd.brand;
        sub.innerText = `Ad • ${state.adSecondsRemaining}s remaining`;
        const pct = ((state.adTotalDuration - state.adSecondsRemaining) / state.adTotalDuration) * 100;
        bar.style.width = `${pct}%`;
        elapsed.innerText = `0:${String(state.adTotalDuration - state.adSecondsRemaining).padStart(2, '0')}`;
        total.innerText = `0:${state.adTotalDuration}`;
      } else {
        const s = state.currentSong;
        art.innerText = '🎵';
        badge.innerText = 'KANNADA RAAGA';
        badge.style.color = 'var(--accent-mint)';
        title.innerText = s.titleKn;
        sub.innerText = `${s.titleEn} • ${s.artist}`;
        const pct = (state.positionSec / (s.duration || 240)) * 100;
        bar.style.width = `${pct}%`;
        elapsed.innerText = `${Math.floor(state.positionSec/60)}:${String(state.positionSec%60).padStart(2,'0')}`;
        total.innerText = `${Math.floor((s.duration||240)/60)}:${String((s.duration||240)%60).padStart(2,'0')}`;
      }
      if (playBtn) playBtn.innerText = state.isPlaying ? '⏸' : '▶';

      backdrop.classList.add('open');
    }
    function closeLockScreenSimulator(e) {
      if (e) e.stopPropagation();
      document.getElementById('lockScreenSimBackdrop').classList.remove('open');
    }

    function simulatePhoneCallInterrupt() {
      state.isPlaying = false;
      syncAudio(false);
      updatePlayerSurfaces();
      showRaagaToast('📞 Incoming Call: Audio session paused. Resumes on call end.');
      setTimeout(() => {
        state.isPlaying = true;
        syncAudio(false);
        updatePlayerSurfaces();
        showRaagaToast('✓ Call Ended: Background audio session resumed.');
      }, 3000);
    }

    function simulateDoNotDisturb() {
      showRaagaToast('🌙 Do Not Disturb Mode active: Audio session volume balanced.');
    }
"""

if "function simulateAudioAdBetweenSongs" not in code:
    code = code.replace("function renderAll() {", ads_js_logic + "\n    function renderAll() {")
    print("Injected ads JavaScript engine.")

# Enhance updatePlayerSurfaces to render Ad State across Mini-player, Now Playing, and Tablet
old_update_surfaces = """    function updatePlayerSurfaces() {
      updateTabletRightPanel();"""

new_update_surfaces = """    function updatePlayerSurfaces() {
      updateTabletRightPanel();

      if (state.isAdPlaying && state.currentAd) {
        const ad = state.currentAd;
        // Mini Player in Ad State
        const miniArt = document.getElementById('miniArtGlyph');
        const miniTitle = document.getElementById('miniTitle');
        const miniArtist = document.getElementById('miniArtist');
        const miniCircle = document.getElementById('miniProgressCircle');
        const miniPlayBtn = document.getElementById('miniPlayBtn');
        const prevBtns = document.querySelectorAll('.mini-ctrl-btn, .top-icon-btn');

        if (miniArt) miniArt.innerText = ad.logo;
        if (miniTitle) miniTitle.innerHTML = `<span class="ad-badge">Ad</span> ${ad.brand}`;
        if (miniArtist) miniArtist.innerText = `Ad • ${state.adSecondsRemaining}s remaining`;
        if (miniCircle) {
          const pct = ((state.adTotalDuration - state.adSecondsRemaining) / state.adTotalDuration);
          miniCircle.style.strokeDashoffset = 125.6 * (1 - pct);
        }
        if (miniPlayBtn) miniPlayBtn.innerText = state.isPlaying ? '⏸' : '▶';

        // Full Now Playing in Ad State
        const npArtBox = document.getElementById('npArtBox');
        const npTitleKn = document.getElementById('npTitleKn');
        const npTitleEn = document.getElementById('npTitleEn');
        const npArtistLine = document.getElementById('npArtistLine');
        const npPlayBtn = document.getElementById('npPlayBtn');
        const npSeekSlider = document.getElementById('npSeekSlider');
        const npCurTime = document.getElementById('npCurTime');
        const npDurTime = document.getElementById('npDurTime');
        const npBadgeYear = document.getElementById('npBadgeYear');

        if (npArtBox) {
          npArtBox.style.background = 'linear-gradient(135deg, #182B24, #0E1A16)';
        }
        if (npBadgeYear) npBadgeYear.innerText = 'SPONSOR AUDIO SESSION';
        if (npTitleKn) npTitleKn.innerHTML = `<span class="ad-badge">Ad</span> ${ad.brand}`;
        if (npTitleEn) npTitleEn.innerText = ad.tagline;
        if (npArtistLine) npArtistLine.innerHTML = `Ad · ${state.adSecondsRemaining}s remaining • <span class="remove-ads-link" onclick="openPremiumModal()">✨ Remove ads</span>`;
        if (npPlayBtn) npPlayBtn.innerText = state.isPlaying ? '⏸' : '▶';
        if (npSeekSlider) {
          npSeekSlider.disabled = true;
          npSeekSlider.style.opacity = '0.35';
          npSeekSlider.value = ((state.adTotalDuration - state.adSecondsRemaining) / state.adTotalDuration) * 100;
        }
        if (npCurTime) npCurTime.innerText = `0:${String(state.adTotalDuration - state.adSecondsRemaining).padStart(2, '0')}`;
        if (npDurTime) npDurTime.innerText = `0:${state.adTotalDuration}`;

        // Lock seek & prev/next transport in Now Playing during ad
        const prevNp = document.querySelector('button[onclick*="prevTrack"]');
        const nextNp = document.querySelector('button[onclick*="nextTrack"]');
        if (prevNp) prevNp.classList.add('ad-locked-ctrl');
        if (nextNp) nextNp.classList.add('ad-locked-ctrl');

        return;
      }

      // Unlock seek & transport when playing normal song
      const npSeekSlider = document.getElementById('npSeekSlider');
      if (npSeekSlider) {
        npSeekSlider.disabled = false;
        npSeekSlider.style.opacity = '1';
      }
      const prevNp = document.querySelector('button[onclick*="prevTrack"]');
      const nextNp = document.querySelector('button[onclick*="nextTrack"]');
      if (prevNp) prevNp.classList.remove('ad-locked-ctrl');
      if (nextNp) nextNp.classList.remove('ad-locked-ctrl');"""

code = code.replace(old_update_surfaces, new_update_surfaces)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Ads system JavaScript successfully implemented.")
