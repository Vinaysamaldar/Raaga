# -*- coding: utf-8 -*-
"""
implement_auth_logic.py
Injects JavaScript logic for complete auth flow:
- State management (currentUser, isGuest, authLanguage, authAttempts)
- Multi-step flow navigation
- Bilingual localization engine (English / Kannada)
- 6-digit code auto-advance, backspace handling, paste support, timers, lockouts
- Searchable country picker
- Google sign-in simulation with conflict handling
- Profile setup & account linking
- Account modal integration (logged in vs guest)
- Guest mode restrictions with friendly sign-in prompt
- First-launch consent modal
- Light/Dark theme toggle
"""

import os

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

AUTH_JS = '''
    // ==================== AUTHENTICATION & LOGIN FLOW JAVASCRIPT ENGINE ====================
    
    // Auth State
    const authState = {
      language: 'en', // 'en' or 'kn'
      currentStep: 'stepWelcome',
      emailTarget: '',
      phoneTarget: '',
      selectedCountry: { code: '+91', flag: '🇮🇳', name: 'India' },
      emailCode: '123456',
      mobileOtp: '849201',
      emailAttempts: 3,
      mobileAttempts: 3,
      emailTimerInterval: null,
      mobileTimerInterval: null,
      selectedAvatar: 'ಕ',
      selectedProfileLang: 'kn',
      isLockedOut: false,
      lockoutEndTime: 0
    };

    // User session in main app state
    state.currentUser = null;
    state.isGuest = false;

    // Check localStorage for saved session
    try {
      const savedUser = localStorage.getItem('kannada_raaga_user');
      if (savedUser) {
        state.currentUser = JSON.parse(savedUser);
        console.log('Restored logged-in session:', state.currentUser.name);
      }
    } catch(e) {}

    // Country Data List
    const COUNTRY_LIST = [
      { code: '+91', flag: '🇮🇳', name: 'India' },
      { code: '+1', flag: '🇺🇸', name: 'United States' },
      { code: '+44', flag: '🇬🇧', name: 'United Kingdom' },
      { code: '+971', flag: '🇦🇪', name: 'United Arab Emirates' },
      { code: '+1', flag: '🇨🇦', name: 'Canada' },
      { code: '+61', flag: '🇦🇺', name: 'Australia' },
      { code: '+65', flag: '🇸🇬', name: 'Singapore' },
      { code: '+49', flag: '🇩🇪', name: 'Germany' },
      { code: '+966', flag: '🇸🇦', name: 'Saudi Arabia' },
      { code: '+974', flag: '🇶🇦', name: 'Qatar' },
      { code: '+965', flag: '🇰🇼', name: 'Kuwait' },
      { code: '+968', flag: '🇴🇲', name: 'Oman' },
      { code: '+60', flag: '🇲🇾', name: 'Malaysia' },
      { code: '+33', flag: '🇫🇷', name: 'France' },
      { code: '+81', flag: '🇯🇵', name: 'Japan' }
    ];

    // Bilingual Dictionary for Auth
    const AUTH_STRINGS = {
      en: {
        langBtn: 'ಕನ್ನಡ',
        headerTagline: 'ಕನ್ನಡ ಹಾಡುಗಳು, ಎಲ್ಲಿಯಾದರೂ • Kannada songs, anywhere',
        welcomeTitle: 'Welcome back',
        welcomeSubtitle: 'Sign in or create your account to sync your playlists and downloads',
        btnGoogle: 'Continue with Google',
        btnMobile: 'Continue with mobile number',
        btnEmail: 'Continue with email',
        orDivider: 'or',
        btnGuest: 'Continue as guest (Browse only)',
        newHere: 'New here?',
        createAccount: 'Create account',
        emailTitle: 'Enter your email',
        emailSubtitle: "We'll send you a 6-digit verification code to sign in",
        btnSendEmail: 'Send verification code'
      },
      kn: {
        langBtn: 'English',
        headerTagline: 'ಕನ್ನಡ ಹಾಡುಗಳು, ಎಲ್ಲಿಯಾದರೂ • ನಿಮ್ಮ ಮೆಚ್ಚಿನ ರಾಗಗಳು',
        welcomeTitle: 'ಮತ್ತೆ ಸುಸ್ವಾಗತ',
        welcomeSubtitle: 'ನಿಮ್ಮ ಪ್ಲೇಪಟ್ಟಿಗಳು ಮತ್ತು ಡೌನ್‌ಲೋಡ್‌ಗಳನ್ನು ಸಿಂಕ್ ಮಾಡಲು ಸೈನ್ ಇನ್ ಮಾಡಿ ಅಥವಾ ಖಾತೆ ರಚಿಸಿ',
        btnGoogle: 'ಗೂಗಲ್ ಮೂಲಕ ಮುಂದುವರಿಯಿರಿ',
        btnMobile: 'ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯೊಂದಿಗೆ ಮುಂದುವರಿಯಿರಿ',
        btnEmail: 'ಇಮೇಲ್ ಮೂಲಕ ಮುಂದುವರಿಯಿರಿ',
        orDivider: 'ಅಥವಾ',
        btnGuest: 'ಅತಿಥಿಯಾಗಿ ಮುಂದುವರಿಯಿರಿ (ಕೇವಲ ಬ್ರೌಸ್)',
        newHere: 'ಹೊಸಬರೇ?',
        createAccount: 'ಖಾತೆ ರಚಿಸಿ',
        emailTitle: 'ನಿಮ್ಮ ಇಮೇಲ್ ನಮೂದಿಸಿ',
        emailSubtitle: 'ಸೈನ್ ಇನ್ ಮಾಡಲು ನಾವು 6-ಅಂಕಿಯ ಪರಿಶೀಲನಾ ಕೋಡ್ ಕಳುಹಿಸುತ್ತೇವೆ',
        btnSendEmail: 'ಪರಿಶೀಲನಾ ಕೋಡ್ ಕಳುಹಿಸಿ'
      }
    };

    // Open & Close Auth Modal
    function openAuthModal(step) {
      if (state.isOffline) {
        showRaagaToast("⚡ You're offline. Continue as guest to play downloaded songs.");
      }
      const backdrop = document.getElementById('authModalBackdrop');
      if (backdrop) {
        backdrop.classList.add('open');
        goToAuthStep(step || 'stepWelcome');
      }
    }

    function closeAuthModal() {
      const backdrop = document.getElementById('authModalBackdrop');
      if (backdrop) backdrop.classList.remove('open');
      clearInterval(authState.emailTimerInterval);
      clearInterval(authState.mobileTimerInterval);
    }

    function handleAuthBackdropClick(e) {
      if (e.target.id === 'authModalBackdrop') {
        closeAuthModal();
      }
    }

    // Step Navigation
    function goToAuthStep(stepId) {
      authState.currentStep = stepId;
      const steps = ['authStepWelcome', 'authStepEmailInput', 'authStepEmailVerify', 'authStepMobileInput', 'authStepMobileVerify', 'authStepProfileSetup', 'authStepConflict'];
      steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
      });

      let targetEl = null;
      if (stepId === 'stepWelcome') targetEl = document.getElementById('authStepWelcome');
      else if (stepId === 'stepEmailInput') targetEl = document.getElementById('authStepEmailInput');
      else if (stepId === 'stepEmailVerify') targetEl = document.getElementById('authStepEmailVerify');
      else if (stepId === 'stepMobileInput') targetEl = document.getElementById('authStepMobileInput');
      else if (stepId === 'stepMobileVerify') targetEl = document.getElementById('authStepMobileVerify');
      else if (stepId === 'stepProfileSetup') targetEl = document.getElementById('authStepProfileSetup');
      else if (stepId === 'stepConflict') targetEl = document.getElementById('authStepConflict');

      if (targetEl) targetEl.classList.add('active');

      // Autofocus first input if relevant
      if (stepId === 'stepEmailInput') {
        setTimeout(() => { const inp = document.getElementById('authEmailInput'); if (inp) inp.focus(); }, 100);
      } else if (stepId === 'stepEmailVerify') {
        setTimeout(() => { const inp = document.getElementById('emailOtp0'); if (inp) inp.focus(); }, 100);
      } else if (stepId === 'stepMobileInput') {
        setTimeout(() => { const inp = document.getElementById('authPhoneInput'); if (inp) inp.focus(); }, 100);
      } else if (stepId === 'stepMobileVerify') {
        setTimeout(() => { const inp = document.getElementById('mobileOtp0'); if (inp) inp.focus(); }, 100);
      }
    }

    // Toggle Language
    function toggleAuthLanguage() {
      authState.language = authState.language === 'en' ? 'kn' : 'en';
      const dict = AUTH_STRINGS[authState.language];
      
      const langLabel = document.getElementById('authLangLabel');
      if (langLabel) langLabel.textContent = dict.langBtn;

      const headerTagline = document.getElementById('authHeaderTagline');
      if (headerTagline) headerTagline.textContent = dict.headerTagline;

      const welcomeTitle = document.getElementById('authWelcomeTitle');
      if (welcomeTitle) welcomeTitle.textContent = dict.welcomeTitle;

      const welcomeSubtitle = document.getElementById('authWelcomeSubtitle');
      if (welcomeSubtitle) welcomeSubtitle.textContent = dict.welcomeSubtitle;

      const btnGoogle = document.getElementById('authBtnGoogleText');
      if (btnGoogle) btnGoogle.textContent = dict.btnGoogle;

      const btnMobile = document.getElementById('authBtnMobileText');
      if (btnMobile) btnMobile.textContent = dict.btnMobile;

      const btnEmail = document.getElementById('authBtnEmailText');
      if (btnEmail) btnEmail.textContent = dict.btnEmail;

      const divider = document.getElementById('authDividerText');
      if (divider) divider.textContent = dict.orDivider;

      const guestBtn = document.getElementById('authGuestBtn');
      if (guestBtn) guestBtn.textContent = dict.btnGuest;

      const newHere = document.getElementById('authNewHereText');
      if (newHere) newHere.textContent = dict.newHere;

      const emailTitle = document.getElementById('authEmailTitle');
      if (emailTitle) emailTitle.textContent = dict.emailTitle;

      const emailSub = document.getElementById('authEmailSubtitle');
      if (emailSub) emailSub.textContent = dict.emailSubtitle;

      const btnSendEmail = document.getElementById('btnSendEmailCodeText');
      if (btnSendEmail) btnSendEmail.textContent = dict.btnSendEmail;

      showRaagaToast(authState.language === 'kn' ? 'ಭಾಷೆಯನ್ನು ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಲಾಗಿದೆ' : 'Language switched to English');
    }

    // Continue As Guest
    function continueAsGuest() {
      state.isGuest = true;
      state.currentUser = null;
      try { localStorage.removeItem('kannada_raaga_user'); } catch(e) {}
      closeAuthModal();
      showRaagaToast('✨ Browsing as Guest. Sign in anytime to unlock downloads & playlists.');
      updateAuthUIState();
    }

    // Email Step 1: Validation & Send Code
    function validateEmailInput() {
      const input = document.getElementById('authEmailInput');
      const box = document.getElementById('authEmailBox');
      const error = document.getElementById('authEmailError');
      const val = input.value.trim();
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);

      if (val.length > 0 && !isValid) {
        box.classList.add('error');
        error.classList.add('visible');
        return false;
      } else {
        box.classList.remove('error');
        error.classList.remove('visible');
        return isValid;
      }
    }

    function handleEmailKey(e) {
      if (e.key === 'Enter') sendEmailVerificationCode();
    }

    function fillDemoEmail(email) {
      const input = document.getElementById('authEmailInput');
      if (input) {
        input.value = email;
        validateEmailInput();
        input.focus();
      }
    }

    function sendEmailVerificationCode() {
      const input = document.getElementById('authEmailInput');
      const email = input.value.trim();
      if (!validateEmailInput() || !email) {
        const box = document.getElementById('authEmailBox');
        const error = document.getElementById('authEmailError');
        box.classList.add('error');
        error.classList.add('visible');
        input.focus();
        return;
      }

      authState.emailTarget = email;
      const targetDisplay = document.getElementById('authEmailTargetDisplay');
      if (targetDisplay) targetDisplay.textContent = email;

      const btn = document.getElementById('btnSendEmailCode');
      btn.disabled = true;
      btn.innerHTML = '<span>Sending code...</span>';

      setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = '<span id="btnSendEmailCodeText">Send verification code</span>';
        goToAuthStep('stepEmailVerify');
        startEmailResendCountdown();
        showRaagaToast('✉️ 6-digit verification code sent to ' + email);
      }, 700);
    }

    // 30s Resend Countdown for Email
    function startEmailResendCountdown() {
      clearInterval(authState.emailTimerInterval);
      let secondsLeft = 30;
      const timerEl = document.getElementById('emailResendTimerText');
      const resendBtn = document.getElementById('btnResendEmailCode');
      const spamHint = document.getElementById('emailSpamHint');

      resendBtn.style.display = 'none';
      spamHint.style.display = 'none';

      authState.emailTimerInterval = setInterval(() => {
        secondsLeft--;
        if (secondsLeft > 0) {
          timerEl.textContent = 'Resend code in 00:' + (secondsLeft < 10 ? '0' : '') + secondsLeft;
        } else {
          clearInterval(authState.emailTimerInterval);
          timerEl.textContent = '';
          resendBtn.style.display = 'inline-block';
          spamHint.style.display = 'block';
        }
      }, 1000);
    }

    function resendEmailVerificationCode() {
      startEmailResendCountdown();
      showRaagaToast('🔄 New verification code sent to ' + authState.emailTarget);
    }

    // 6-Digit Code Auto-Advance, Backspace & Paste
    function handleOtpInput(index, type) {
      const currentBox = document.getElementById(type + 'Otp' + index);
      const val = currentBox.value.replace(/[^0-9]/g, '');
      currentBox.value = val ? val[val.length - 1] : '';

      if (currentBox.value) {
        currentBox.classList.add('filled');
        if (index < 5) {
          const nextBox = document.getElementById(type + 'Otp' + (index + 1));
          if (nextBox) nextBox.focus();
        }
      } else {
        currentBox.classList.remove('filled');
      }

      checkOtpCompletion(type);
    }

    function handleOtpKey(index, e, type) {
      if (e.key === 'Backspace') {
        const currentBox = document.getElementById(type + 'Otp' + index);
        if (!currentBox.value && index > 0) {
          const prevBox = document.getElementById(type + 'Otp' + (index - 1));
          if (prevBox) {
            prevBox.focus();
            prevBox.value = '';
            prevBox.classList.remove('filled');
          }
        }
      } else if (e.key === 'Enter') {
        if (type === 'email') verifyEmailOtp();
        else verifyMobileOtp();
      }
    }

    function handleOtpPaste(e, type) {
      e.preventDefault();
      const pasteData = (e.clipboardData || window.clipboardData).getData('text').trim();
      const digits = pasteData.replace(/[^0-9]/g, '').slice(0, 6);
      if (!digits) return;

      for (let i = 0; i < 6; i++) {
        const box = document.getElementById(type + 'Otp' + i);
        if (box) {
          box.value = digits[i] || '';
          if (box.value) box.classList.add('filled');
          else box.classList.remove('filled');
        }
      }

      const focusIdx = Math.min(digits.length, 5);
      const focusBox = document.getElementById(type + 'Otp' + focusIdx);
      if (focusBox) focusBox.focus();

      checkOtpCompletion(type);
    }

    function checkOtpCompletion(type) {
      let fullCode = '';
      for (let i = 0; i < 6; i++) {
        const box = document.getElementById(type + 'Otp' + i);
        if (box) fullCode += box.value;
      }

      const verifyBtn = document.getElementById(type === 'email' ? 'btnVerifyEmailCode' : 'btnVerifyMobileOtp');
      if (verifyBtn) {
        verifyBtn.disabled = fullCode.length !== 6;
      }
    }

    function autofillDemoOtp(code, type) {
      for (let i = 0; i < 6; i++) {
        const box = document.getElementById(type + 'Otp' + i);
        if (box) {
          box.value = code[i] || '';
          box.classList.add('filled');
        }
      }
      checkOtpCompletion(type);
      showRaagaToast('⚡ Demo code ' + code + ' filled');
    }

    // Verify Email Code
    function verifyEmailOtp() {
      let code = '';
      for (let i = 0; i < 6; i++) {
        const box = document.getElementById('emailOtp' + i);
        if (box) code += box.value;
      }

      const row = document.getElementById('emailOtpRow');
      const feedback = document.getElementById('emailOtpFeedback');
      const verifyBtn = document.getElementById('btnVerifyEmailCode');

      verifyBtn.disabled = true;
      verifyBtn.innerHTML = '<span>Verifying...</span>';

      setTimeout(() => {
        if (code === authState.emailCode || code === '123456') {
          // Success
          feedback.style.color = '#4CAF50';
          feedback.innerHTML = '✓ Code verified successfully!';
          showRaagaToast('✓ Email verified! Setting up session...');
          
          setTimeout(() => {
            // New user goes to profile setup
            const nameInput = document.getElementById('profileNameInput');
            if (nameInput) nameInput.value = authState.emailTarget.split('@')[0];
            goToAuthStep('stepProfileSetup');
          }, 600);
        } else {
          // Failure
          authState.emailAttempts--;
          row.classList.add('error');
          setTimeout(() => row.classList.remove('error'), 450);

          if (authState.emailAttempts > 0) {
            feedback.style.color = '#E53935';
            feedback.innerHTML = 'Incorrect code, ' + authState.emailAttempts + ' attempts left';
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<span id="btnVerifyEmailCodeText">Verify</span>';
          } else {
            // Lockout 15 min
            feedback.style.color = '#E53935';
            feedback.innerHTML = '🔒 Locked for 15 minutes due to multiple failed attempts.';
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<span>Locked (15 min)</span>';
          }
        }
      }, 700);
    }

    // Mobile Phone Validation & Sending OTP
    function validatePhoneInput() {
      const input = document.getElementById('authPhoneInput');
      const error = document.getElementById('authPhoneError');
      const digits = input.value.replace(/[^0-9]/g, '');
      input.value = digits;
      const isValid = digits.length === 10;

      if (digits.length > 0 && !isValid) {
        error.classList.add('visible');
        return false;
      } else {
        error.classList.remove('visible');
        return isValid;
      }
    }

    function handlePhoneKey(e) {
      if (e.key === 'Enter') sendMobileOtp();
    }

    function fillDemoPhone(phone) {
      const input = document.getElementById('authPhoneInput');
      if (input) {
        input.value = phone;
        validatePhoneInput();
        input.focus();
      }
    }

    function sendMobileOtp() {
      const input = document.getElementById('authPhoneInput');
      const digits = input.value.replace(/[^0-9]/g, '');
      if (digits.length !== 10) {
        document.getElementById('authPhoneError').classList.add('visible');
        input.focus();
        return;
      }

      const fullNumber = authState.selectedCountry.code + ' ' + digits;
      authState.phoneTarget = fullNumber;

      const display = document.getElementById('authMobileTargetDisplay');
      if (display) display.textContent = fullNumber;

      const btn = document.getElementById('btnSendMobileOtp');
      btn.disabled = true;
      btn.innerHTML = '<span>Sending OTP...</span>';

      setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = '<span id="btnSendMobileOtpText">Send OTP</span>';
        goToAuthStep('stepMobileVerify');
        startMobileResendCountdown();
        showRaagaToast('📱 OTP sent to ' + fullNumber);
      }, 700);
    }

    function startMobileResendCountdown() {
      clearInterval(authState.mobileTimerInterval);
      let secondsLeft = 30;
      const timerEl = document.getElementById('mobileResendTimerText');
      const resendBtn = document.getElementById('btnResendMobileOtp');

      resendBtn.style.display = 'none';

      authState.mobileTimerInterval = setInterval(() => {
        secondsLeft--;
        if (secondsLeft > 0) {
          timerEl.textContent = 'Resend OTP in 00:' + (secondsLeft < 10 ? '0' : '') + secondsLeft;
        } else {
          clearInterval(authState.mobileTimerInterval);
          timerEl.textContent = '';
          resendBtn.style.display = 'inline-block';
        }
      }, 1000);
    }

    function resendMobileOtp() {
      startMobileResendCountdown();
      showRaagaToast('🔄 New OTP sent to ' + authState.phoneTarget);
    }

    function verifyMobileOtp() {
      let code = '';
      for (let i = 0; i < 6; i++) {
        const box = document.getElementById('mobileOtp' + i);
        if (box) code += box.value;
      }

      const row = document.getElementById('mobileOtpRow');
      const feedback = document.getElementById('mobileOtpFeedback');
      const verifyBtn = document.getElementById('btnVerifyMobileOtp');

      verifyBtn.disabled = true;
      verifyBtn.innerHTML = '<span>Verifying...</span>';

      setTimeout(() => {
        if (code === authState.mobileOtp || code === '849201') {
          feedback.style.color = '#4CAF50';
          feedback.innerHTML = '✓ Phone verified successfully!';
          showRaagaToast('✓ Phone verified!');

          setTimeout(() => {
            const nameInput = document.getElementById('profileNameInput');
            if (nameInput) nameInput.value = 'Raaga Listener';
            goToAuthStep('stepProfileSetup');
          }, 600);
        } else {
          authState.mobileAttempts--;
          row.classList.add('error');
          setTimeout(() => row.classList.remove('error'), 450);

          if (authState.mobileAttempts > 0) {
            feedback.style.color = '#E53935';
            feedback.innerHTML = 'Incorrect OTP, ' + authState.mobileAttempts + ' attempts left';
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<span id="btnVerifyMobileOtpText">Verify & Continue</span>';
          } else {
            feedback.style.color = '#E53935';
            feedback.innerHTML = '🔒 Locked for 15 minutes due to multiple failed attempts.';
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<span>Locked (15 min)</span>';
          }
        }
      }, 700);
    }

    // Country Picker
    function openCountryPicker() {
      const backdrop = document.getElementById('countryPickerBackdrop');
      if (backdrop) {
        populateCountryList();
        backdrop.classList.add('open');
      }
    }

    function closeCountryPicker(e) {
      if (e) e.stopPropagation();
      const backdrop = document.getElementById('countryPickerBackdrop');
      if (backdrop) backdrop.classList.remove('open');
    }

    function populateCountryList(filterText = '') {
      const container = document.getElementById('countryOptionsList');
      if (!container) return;

      const filter = filterText.toLowerCase();
      const filtered = COUNTRY_LIST.filter(c => c.name.toLowerCase().includes(filter) || c.code.includes(filter));

      container.innerHTML = filtered.map(c => `
        <div class="col-option-btn" style="cursor:pointer;padding:10px 14px;border-radius:12px;background:var(--surface);" onclick="selectCountry('${c.code}', '${c.flag}', '${c.name}')">
          <span style="font-size:20px;margin-right:10px;">${c.flag}</span>
          <span style="font-weight:700;flex:1;color:var(--text-primary);">${c.name}</span>
          <span style="font-weight:800;color:var(--saffron);">${c.code}</span>
        </div>
      `).join('');
    }

    function filterCountryList() {
      const query = document.getElementById('countrySearchInput').value;
      populateCountryList(query);
    }

    function selectCountry(code, flag, name) {
      authState.selectedCountry = { code, flag, name };
      document.getElementById('authSelectedFlag').textContent = flag;
      document.getElementById('authSelectedCode').textContent = code;
      closeCountryPicker();
    }

    // Google Sign-In Simulation
    function startGoogleLogin() {
      const chooser = document.getElementById('googleChooserBackdrop');
      if (chooser) chooser.classList.add('open');
    }

    function closeGoogleChooser(e) {
      if (e) e.stopPropagation();
      const chooser = document.getElementById('googleChooserBackdrop');
      if (chooser) chooser.classList.remove('open');
    }

    function selectGoogleAccount(name, email, avatarLetter) {
      closeGoogleChooser();
      showRaagaToast('Signing you in with Google (' + email + ')...');

      setTimeout(() => {
        state.currentUser = {
          name: name,
          email: email,
          phone: '',
          provider: 'google',
          avatar: avatarLetter,
          tier: 'Free Listener',
          joinedYear: '2026',
          linkedGoogle: true
        };
        state.isGuest = false;
        try { localStorage.setItem('kannada_raaga_user', JSON.stringify(state.currentUser)); } catch(e) {}
        closeAuthModal();
        updateAuthUIState();
        showRaagaToast('🎉 Welcome, ' + name + '! Signed in with Google.');
      }, 800);
    }

    function simulateGoogleAccountConflict() {
      closeGoogleChooser();
      const targetDisplay = document.getElementById('conflictTargetDisplay');
      if (targetDisplay) targetDisplay.textContent = 'vinay.kannada@gmail.com';
      goToAuthStep('stepConflict');
    }

    function resolveAccountConflict(method) {
      showRaagaToast('🔗 Merging and linking Google credentials...');
      goToAuthStep('stepEmailInput');
      fillDemoEmail('vinay.kannada@gmail.com');
    }

    // Profile Setup Finish
    function selectAvatar(symbol) {
      authState.selectedAvatar = symbol;
      const preview = document.getElementById('profileAvatarPreview');
      if (preview) preview.textContent = symbol;
    }

    function setProfileLanguage(lang) {
      authState.selectedProfileLang = lang;
      ['chipLangKannada', 'chipLangEnglish', 'chipLangBoth'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active-mint');
      });
      if (lang === 'kn') document.getElementById('chipLangKannada').classList.add('active-mint');
      else if (lang === 'en') document.getElementById('chipLangEnglish').classList.add('active-mint');
      else document.getElementById('chipLangBoth').classList.add('active-mint');
    }

    function completeProfileSetup() {
      const name = document.getElementById('profileNameInput').value.trim() || 'Kannada Music Lover';
      const keepSignedIn = document.getElementById('authKeepSignedIn').checked;

      state.currentUser = {
        name: name,
        email: authState.emailTarget || 'user@kannadaraaga.com',
        phone: authState.phoneTarget || '',
        provider: authState.emailTarget ? 'email' : 'phone',
        avatar: authState.selectedAvatar,
        tier: 'Free Listener',
        joinedYear: '2026',
        linkedGoogle: false
      };
      state.isGuest = false;

      if (keepSignedIn) {
        try { localStorage.setItem('kannada_raaga_user', JSON.stringify(state.currentUser)); } catch(e) {}
      }

      closeAuthModal();
      updateAuthUIState();
      showRaagaToast('🎉 Welcome to Kannada Raaga, ' + name + '!');
    }

    // Update App Top Bar Account Button & Status
    function updateAuthUIState() {
      const accountBtn = document.getElementById('topAccountBtn');
      if (accountBtn) {
        if (state.currentUser) {
          accountBtn.innerHTML = '<span style="font-size:15px;font-weight:900;color:var(--saffron);">' + state.currentUser.avatar + '</span>';
          accountBtn.title = state.currentUser.name + ' (Signed in)';
        } else if (state.isGuest) {
          accountBtn.innerHTML = '👤';
          accountBtn.title = 'Guest Listener (Tap to sign in)';
        } else {
          accountBtn.innerHTML = '👤';
          accountBtn.title = 'Account';
        }
      }
    }

    // Integrated Account Modal (Live Session Details)
    function openAccountModal() {
      const backdrop = document.getElementById('accountModalBackdrop');
      const content = document.getElementById('accountModalContent');
      if (!backdrop || !content) return;

      if (state.currentUser) {
        content.innerHTML = `
          <div style="text-align:center;margin-bottom:16px;">
            <div style="width:68px;height:68px;border-radius:50%;background:var(--saffron);color:#0B1110;font-size:30px;font-weight:900;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,0.5);border:2px solid var(--accent-mint);">${state.currentUser.avatar}</div>
            <div style="font-size:18px;font-weight:800;color:var(--text-primary);margin-top:8px;">${state.currentUser.name}</div>
            <div style="font-size:12px;color:var(--saffron);font-weight:700;">${state.currentUser.tier} • Member since ${state.currentUser.joinedYear}</div>
            <div style="font-size:11.5px;color:var(--text-secondary);margin-top:2px;">${state.currentUser.email || state.currentUser.phone}</div>
          </div>

          <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px;">
            <div style="background:var(--surface);padding:10px 14px;border-radius:14px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:13px;color:var(--text-secondary);">Auth Method</span>
              <span style="color:var(--accent-mint);font-weight:700;font-size:12.5px;">✓ ${state.currentUser.provider.toUpperCase()} (Secure)</span>
            </div>
            <div style="background:var(--surface);padding:10px 14px;border-radius:14px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:13px;color:var(--text-secondary);">Audio Quality</span>
              <span style="color:var(--saffron);font-weight:700;font-size:12.5px;">320 kbps Studio Master</span>
            </div>
            <div style="background:var(--surface);padding:10px 14px;border-radius:14px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:13px;color:var(--text-secondary);">Bilingual Subtitles</span>
              <span style="color:var(--accent-mint);font-weight:700;font-size:12.5px;">Enabled (ಕನ್ನಡ/EN)</span>
            </div>
          </div>

          <div style="display:flex;flex-direction:column;gap:8px;">
            <button class="pill-chip" style="width:100%;padding:10px;font-size:12.5px;font-weight:700;" onclick="closeAccountModal();openAuthModal('stepEmailInput');">
              ✉️ Change Email or Mobile
            </button>
            <button class="pill-chip" style="width:100%;padding:10px;font-size:12.5px;font-weight:700;color:var(--saffron);border-color:var(--saffron);" onclick="signOutAllDevices()">
              🔐 Sign Out of All Devices
            </button>
            <button class="pill-chip" style="width:100%;padding:10px;font-size:12.5px;font-weight:700;color:#E53935;border-color:#E53935;" onclick="signOutCurrentSession()">
              🚪 Sign Out
            </button>
          </div>
        `;
      } else {
        content.innerHTML = `
          <div style="text-align:center;margin-bottom:16px;">
            <div style="width:64px;height:64px;border-radius:50%;background:var(--surface);color:var(--text-secondary);font-size:28px;display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--border);">👤</div>
            <div style="font-size:17px;font-weight:800;color:var(--text-primary);margin-top:8px;">Guest Listener</div>
            <div style="font-size:12px;color:var(--saffron);margin-top:4px;">Browse Mode Active</div>
          </div>

          <div style="background:rgba(242,169,0,0.08);border:1px solid rgba(242,169,0,0.25);border-radius:16px;padding:12px 14px;margin-bottom:16px;">
            <div style="font-size:12px;font-weight:700;color:var(--saffron);">LOCKED IN GUEST MODE:</div>
            <div style="font-size:11.5px;color:var(--text-secondary);margin-top:4px;line-height:1.4;">
              Offline downloads and personalized playlists require an account to sync across devices.
            </div>
          </div>

          <button class="auth-btn-primary" onclick="closeAccountModal();openAuthModal();">
            <span>Sign In / Create Account →</span>
          </button>
        `;
      }

      backdrop.classList.add('open');
    }

    function signOutCurrentSession() {
      state.currentUser = null;
      state.isGuest = true;
      try { localStorage.removeItem('kannada_raaga_user'); } catch(e) {}
      closeAccountModal();
      updateAuthUIState();
      showRaagaToast('Signed out successfully.');
    }

    function signOutAllDevices() {
      state.currentUser = null;
      state.isGuest = false;
      try { localStorage.removeItem('kannada_raaga_user'); } catch(e) {}
      closeAccountModal();
      updateAuthUIState();
      showRaagaToast('✓ Revoked active session tokens on all devices.');
    }

    // First-Launch Consent Modal
    function openAuthConsent() {
      const backdrop = document.getElementById('authConsentBackdrop');
      if (backdrop) backdrop.classList.add('open');
    }
    function closeAuthConsent(e) {
      if (e) e.stopPropagation();
      const backdrop = document.getElementById('authConsentBackdrop');
      if (backdrop) backdrop.classList.remove('open');
    }
    function acceptConsentAndContinue() {
      closeAuthConsent();
      showRaagaToast('✓ Privacy preferences saved under DPDP/GDPR.');
    }
    function handleUnder18Toggle(isUnder18) {
      if (isUnder18) {
        state.personalizedAds = false;
        showRaagaToast('🛡️ Under 18 mode: Personalized ads strictly disabled.');
      }
    }

    // Component Sheet Modal
    function openAuthComponents() {
      const backdrop = document.getElementById('authComponentsBackdrop');
      if (backdrop) backdrop.classList.add('open');
    }
    function closeAuthComponents(e) {
      if (e) e.stopPropagation();
      const backdrop = document.getElementById('authComponentsBackdrop');
      if (backdrop) backdrop.classList.remove('open');
    }

    // Toggle Light / Dark Theme
    function toggleLightDarkTheme() {
      const isLight = document.body.classList.toggle('theme-light');
      try { localStorage.setItem('kannada_raaga_light_theme', isLight ? 'true' : 'false'); } catch(e) {}
      showRaagaToast(isLight ? '☀️ Light Theme Variant Activated' : '🌙 Dark Theme Re-activated (#0B1110)');
    }

    // Check saved theme
    try {
      if (localStorage.getItem('kannada_raaga_light_theme') === 'true') {
        document.body.classList.add('theme-light');
      }
    } catch(e) {}

    // Terms / Privacy dummy modal
    function showLegalModal(type) {
      showRaagaToast(type === 'terms' ? '📜 Kannada Raaga Terms of Service (Fair Music Streaming)' : '🛡️ Kannada Raaga Privacy Policy (DPDP & GDPR Compliant)');
    }

    // Initialize UI state on load
    updateAuthUIState();
'''

if 'AUTHENTICATION & LOGIN FLOW JAVASCRIPT ENGINE' not in html:
    script_end = html.rfind('</script>')
    if script_end != -1:
        html = html[:script_end] + '\n' + AUTH_JS + '\n' + html[script_end:]
        print('Injected Auth JavaScript Engine successfully.')
    else:
        print('Could not find </script>')
else:
    print('Auth JS already present.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved Auth JS updates to index.html.')
