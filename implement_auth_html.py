# -*- coding: utf-8 -*-
"""
implement_auth_html.py
Injects the HTML markup for:
1. Auth Modal (Welcome, Email with 6-digit code, Mobile with OTP, Profile Setup, Guest Mode, Account Conflict)
2. Country Picker Dropdown Sheet
3. Google System Account Chooser
4. First-Launch Consent Sheet
5. Component Gallery Sheet
6. Prototype Walkthrough Toolbar buttons
"""

import os

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

AUTH_MODALS_HTML = '''
    <!-- ==================== AUTHENTICATION & LOGIN FLOW MODAL (Phone & Tablet Split-Screen) ==================== -->
    <div class="auth-modal-backdrop" id="authModalBackdrop" onclick="handleAuthBackdropClick(event)">
      <div class="auth-container" onclick="event.stopPropagation()">
        
        <!-- TABLET & LANDSCAPE LEFT HERO PANEL (Cover-Art Collage & Brand Atmosphere) -->
        <div class="auth-hero-panel">
          <!-- Background Cover Art Collage -->
          <div class="auth-hero-bg-collage">
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400');"></div>
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=400');"></div>
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400');"></div>
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400');"></div>
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400');"></div>
            <div class="auth-hero-art-card" style="background-image:url('https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=400');"></div>
          </div>
          <div class="auth-hero-overlay"></div>

          <!-- Brand Header on Left Panel -->
          <div style="position:relative;z-index:2;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
              <div style="width:48px;height:48px;border-radius:14px;background:var(--saffron);color:#0B1110;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:900;">ಕ</div>
              <div>
                <div style="font-size:20px;font-weight:800;color:var(--text-primary);letter-spacing:0.3px;">Kannada Raaga</div>
                <div style="font-size:12px;color:var(--saffron);font-weight:700;">ಕನ್ನಡ ರಾಗ • ಸಂಗೀತದ ಸಂಭ್ರಮ</div>
              </div>
            </div>
            <div class="auth-gold-accent"></div>
            <p style="font-size:13.5px;color:var(--text-secondary);line-height:1.5;max-width:320px;">
              Explore over 90 years of Kannada musical legacy — from 1934 Sati Sulochana to 2026 chart-toppers.
            </p>
          </div>

          <!-- Hero Bottom Pill Badges -->
          <div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:10px;">
            <div style="display:flex;align-items:center;gap:10px;background:rgba(24,33,31,0.75);backdrop-filter:blur(10px);border:1px solid var(--border);border-radius:999px;padding:8px 16px;">
              <span style="font-size:16px;">🎧</span>
              <span style="font-size:12px;font-weight:600;color:var(--text-primary);">Lossless 320 kbps Studio Audio</span>
            </div>
            <div style="display:flex;align-items:center;gap:10px;background:rgba(24,33,31,0.75);backdrop-filter:blur(10px);border:1px solid var(--border);border-radius:999px;padding:8px 16px;">
              <span style="font-size:16px;">⚡</span>
              <span style="font-size:12px;font-weight:600;color:var(--text-primary);">Offline Smart Downloads & Lyrics</span>
            </div>
          </div>
        </div>

        <!-- RIGHT FORM PANEL (Phone & Tablet) -->
        <div class="auth-form-panel">
          
          <!-- Top Row: Language Toggle & Close Button -->
          <div class="auth-top-nav-row">
            <button class="auth-lang-btn" onclick="toggleAuthLanguage()" title="Switch Language">
              <span>🌐</span><span id="authLangLabel">ಕನ್ನಡ</span>
            </button>
            <button class="auth-close-btn" onclick="closeAuthModal()" title="Close">✕</button>
          </div>

          <!-- ==================== SCREEN 1: WELCOME / LOGIN ==================== -->
          <div class="auth-step-view active" id="authStepWelcome">
            <div>
              <!-- Branded header on phone -->
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="width:36px;height:36px;border-radius:10px;background:var(--saffron);color:#0B1110;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;">ಕ</div>
                <div>
                  <div style="font-size:16px;font-weight:800;color:var(--text-primary);">Kannada Raaga</div>
                  <div style="font-size:10.5px;color:var(--saffron);font-weight:600;" id="authHeaderTagline">ಕನ್ನಡ ಹಾಡುಗಳು, ಎಲ್ಲಿಯಾದರೂ • Kannada songs, anywhere</div>
                </div>
              </div>

              <div class="auth-gold-accent"></div>

              <div style="margin-top:14px;margin-bottom:20px;">
                <h2 style="font-size:24px;font-weight:800;color:var(--text-primary);line-height:1.2;" id="authWelcomeTitle">Welcome back</h2>
                <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;" id="authWelcomeSubtitle">Sign in or create your account to sync your playlists and downloads</div>
              </div>

              <!-- Stacked Action Buttons -->
              <div style="display:flex;flex-direction:column;gap:12px;">
                <!-- 1. Continue with Google -->
                <button class="auth-btn-google" onclick="startGoogleLogin()">
                  <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
                  <span id="authBtnGoogleText">Continue with Google</span>
                </button>

                <!-- 2. Continue with mobile number -->
                <button class="auth-btn-outlined" onclick="goToAuthStep('stepMobileInput')">
                  <span style="font-size:18px;">📱</span>
                  <span id="authBtnMobileText">Continue with mobile number</span>
                </button>

                <!-- 3. Continue with email -->
                <button class="auth-btn-outlined" onclick="goToAuthStep('stepEmailInput')">
                  <span style="font-size:18px;">✉️</span>
                  <span id="authBtnEmailText">Continue with email</span>
                </button>
              </div>

              <!-- Divider -->
              <div class="auth-divider"><span id="authDividerText">or</span></div>

              <!-- Guest link -->
              <div style="text-align:center;">
                <button style="background:none;border:none;color:var(--saffron);font-size:13px;font-weight:700;cursor:pointer;padding:6px 12px;border-radius:999px;" onclick="continueAsGuest()" id="authGuestBtn">
                  Continue as guest (Browse only)
                </button>
              </div>
            </div>

            <!-- Footer: New Here & Legal -->
            <div>
              <div style="text-align:center;font-size:12px;color:var(--text-secondary);margin-top:14px;">
                <span id="authNewHereText">New here?</span> 
                <a style="color:var(--accent-mint);font-weight:700;cursor:pointer;" onclick="goToAuthStep('stepEmailInput')">Create account</a>
              </div>
              <div class="auth-terms-footer">
                By continuing you agree to the <a onclick="showLegalModal('terms')">Terms of Service</a> and <a onclick="showLegalModal('privacy')">Privacy Policy</a>
              </div>
            </div>
          </div>

          <!-- ==================== SCREEN 2A: EMAIL LOGIN STEP 1 (Email Input) ==================== -->
          <div class="auth-step-view" id="authStepEmailInput">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <button class="auth-close-btn" style="width:28px;height:28px;" onclick="goToAuthStep('stepWelcome')">←</button>
                <div style="font-size:12px;font-weight:700;color:var(--saffron);">EMAIL SIGN-IN</div>
              </div>

              <h2 style="font-size:22px;font-weight:800;color:var(--text-primary);line-height:1.2;" id="authEmailTitle">Enter your email</h2>
              <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;margin-bottom:20px;" id="authEmailSubtitle">We'll send you a 6-digit verification code to sign in</div>

              <!-- Email Field -->
              <div class="auth-pill-input-group">
                <label class="auth-input-label" for="authEmailInput">EMAIL ADDRESS</label>
                <div class="auth-pill-input-box" id="authEmailBox">
                  <span style="font-size:16px;margin-right:10px;color:var(--text-secondary);">✉</span>
                  <input type="email" id="authEmailInput" class="auth-pill-input" placeholder="name@example.com" autocomplete="email" oninput="validateEmailInput()" onkeydown="handleEmailKey(event)" />
                </div>
                <div class="auth-input-error-hint" id="authEmailError">Enter a valid email address</div>
              </div>

              <!-- Quick Demo Helper Chips -->
              <div style="margin-bottom:18px;">
                <div style="font-size:11px;color:var(--text-secondary);margin-bottom:6px;">QUICK DEMO ADDRESSES:</div>
                <div style="display:flex;flex-wrap:wrap;gap:6px;">
                  <button class="pill-chip" style="font-size:11px;padding:4px 10px;" onclick="fillDemoEmail('user@kannadaraaga.com')">user@kannadaraaga.com</button>
                  <button class="pill-chip" style="font-size:11px;padding:4px 10px;" onclick="fillDemoEmail('dr.rajkumar@gmail.com')">dr.rajkumar@gmail.com</button>
                </div>
              </div>

              <!-- Send Code Button -->
              <button class="auth-btn-primary" id="btnSendEmailCode" onclick="sendEmailVerificationCode()">
                <span id="btnSendEmailCodeText">Send verification code</span>
              </button>
            </div>

            <div class="auth-terms-footer">
              A 6-digit code will be generated. The code expires in 10 minutes.
            </div>
          </div>

          <!-- ==================== SCREEN 2A: EMAIL LOGIN STEP 2 (Verify 6-Digit Code) ==================== -->
          <div class="auth-step-view" id="authStepEmailVerify">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <button class="auth-close-btn" style="width:28px;height:28px;" onclick="goToAuthStep('stepEmailInput')">←</button>
                <div style="font-size:12px;font-weight:700;color:var(--saffron);">VERIFY CODE</div>
              </div>

              <h2 style="font-size:22px;font-weight:800;color:var(--text-primary);line-height:1.2;">Verify your email</h2>
              <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;">
                We sent a 6-digit code to <b id="authEmailTargetDisplay" style="color:var(--text-primary);">name@example.com</b>
                <a style="color:var(--saffron);margin-left:6px;font-weight:700;cursor:pointer;" onclick="goToAuthStep('stepEmailInput')">Edit</a>
              </div>

              <!-- Six Separate Code Boxes with Auto-Advance & Paste -->
              <div class="auth-otp-row" id="emailOtpRow">
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp0" oninput="handleOtpInput(0, 'email')" onkeydown="handleOtpKey(0, event, 'email')" onpaste="handleOtpPaste(event, 'email')" aria-label="Digit 1 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp1" oninput="handleOtpInput(1, 'email')" onkeydown="handleOtpKey(1, event, 'email')" aria-label="Digit 2 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp2" oninput="handleOtpInput(2, 'email')" onkeydown="handleOtpKey(2, event, 'email')" aria-label="Digit 3 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp3" oninput="handleOtpInput(3, 'email')" onkeydown="handleOtpKey(3, event, 'email')" aria-label="Digit 4 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp4" oninput="handleOtpInput(4, 'email')" onkeydown="handleOtpKey(4, event, 'email')" aria-label="Digit 5 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="emailOtp5" oninput="handleOtpInput(5, 'email')" onkeydown="handleOtpKey(5, event, 'email')" aria-label="Digit 6 of 6" />
              </div>

              <!-- Code Status Message / Attempts Left -->
              <div id="emailOtpFeedback" style="font-size:11.5px;font-weight:600;min-height:18px;margin-bottom:12px;text-align:center;"></div>

              <!-- Resend Timer & Spam Hint -->
              <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:16px;">
                <span id="emailResendTimerText" style="color:var(--text-secondary);">Resend code in 00:30</span>
                <button id="btnResendEmailCode" style="display:none;background:none;border:none;color:var(--saffron);font-weight:700;cursor:pointer;" onclick="resendEmailVerificationCode()">Resend code</button>
              </div>

              <!-- Quick Autofill Button for Demo -->
              <div style="text-align:center;margin-bottom:16px;">
                <button class="pill-chip" style="font-size:11px;padding:6px 14px;background:rgba(242,169,0,0.12);border-color:var(--saffron);color:var(--saffron);" onclick="autofillDemoOtp('123456', 'email')">
                  ⚡ Auto-fill Code: 123456
                </button>
              </div>

              <!-- Verify Button -->
              <button class="auth-btn-primary" id="btnVerifyEmailCode" disabled onclick="verifyEmailOtp()">
                <span id="btnVerifyEmailCodeText">Verify</span>
              </button>
            </div>

            <!-- Spam Folder Hint -->
            <div id="emailSpamHint" style="display:none;font-size:11px;color:var(--text-secondary);text-align:center;margin-top:12px;background:var(--surface);padding:8px 12px;border-radius:12px;">
              💡 Didn't receive the email? Check your <b>Spam</b> or <b>Junk</b> folder.
            </div>
          </div>

          <!-- ==================== SCREEN 2B: MOBILE NUMBER LOGIN (Step 1: Phone Input) ==================== -->
          <div class="auth-step-view" id="authStepMobileInput">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <button class="auth-close-btn" style="width:28px;height:28px;" onclick="goToAuthStep('stepWelcome')">←</button>
                <div style="font-size:12px;font-weight:700;color:var(--saffron);">MOBILE NUMBER</div>
              </div>

              <h2 style="font-size:22px;font-weight:800;color:var(--text-primary);line-height:1.2;">Continue with mobile</h2>
              <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;margin-bottom:20px;">We'll send a 6-digit OTP to your phone number</div>

              <!-- Country Selector + Phone Field -->
              <label class="auth-input-label">PHONE NUMBER</label>
              <div style="display:flex;gap:8px;margin-bottom:14px;">
                <div class="auth-country-selector" onclick="openCountryPicker()" title="Select Country Code">
                  <span id="authSelectedFlag">🇮🇳</span>
                  <span id="authSelectedCode">+91</span>
                  <span style="font-size:10px;color:var(--text-secondary);">▼</span>
                </div>
                <div class="auth-pill-input-box" style="flex:1;" id="authPhoneBox">
                  <input type="tel" id="authPhoneInput" class="auth-pill-input" placeholder="98765 43210" maxlength="14" oninput="validatePhoneInput()" onkeydown="handlePhoneKey(event)" />
                </div>
              </div>
              <div class="auth-input-error-hint" id="authPhoneError">Enter a valid 10-digit mobile number</div>

              <!-- Quick Demo Phone -->
              <div style="margin-bottom:18px;">
                <div style="font-size:11px;color:var(--text-secondary);margin-bottom:6px;">QUICK DEMO NUMBER:</div>
                <button class="pill-chip" style="font-size:11px;padding:4px 10px;" onclick="fillDemoPhone('9876543210')">🇮🇳 98765 43210</button>
              </div>

              <!-- Send OTP Button -->
              <button class="auth-btn-primary" id="btnSendMobileOtp" onclick="sendMobileOtp()">
                <span id="btnSendMobileOtpText">Send OTP</span>
              </button>
            </div>

            <div class="auth-terms-footer">
              Standard SMS and carrier rates may apply.
            </div>
          </div>

          <!-- ==================== SCREEN 2B: MOBILE NUMBER STEP 2 (Verify OTP) ==================== -->
          <div class="auth-step-view" id="authStepMobileVerify">
            <div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <button class="auth-close-btn" style="width:28px;height:28px;" onclick="goToAuthStep('stepMobileInput')">←</button>
                <div style="font-size:12px;font-weight:700;color:var(--saffron);">VERIFY OTP</div>
              </div>

              <h2 style="font-size:22px;font-weight:800;color:var(--text-primary);line-height:1.2;">Enter OTP</h2>
              <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;">
                Sent to <b id="authMobileTargetDisplay" style="color:var(--text-primary);">+91 98XXXXXX10</b>
                <a style="color:var(--saffron);margin-left:6px;font-weight:700;cursor:pointer;" onclick="goToAuthStep('stepMobileInput')">Change</a>
              </div>

              <!-- Six Separate Code Boxes with Auto-Advance & Paste -->
              <div class="auth-otp-row" id="mobileOtpRow">
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp0" oninput="handleOtpInput(0, 'mobile')" onkeydown="handleOtpKey(0, event, 'mobile')" onpaste="handleOtpPaste(event, 'mobile')" aria-label="Digit 1 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp1" oninput="handleOtpInput(1, 'mobile')" onkeydown="handleOtpKey(1, event, 'mobile')" aria-label="Digit 2 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp2" oninput="handleOtpInput(2, 'mobile')" onkeydown="handleOtpKey(2, event, 'mobile')" aria-label="Digit 3 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp3" oninput="handleOtpInput(3, 'mobile')" onkeydown="handleOtpKey(3, event, 'mobile')" aria-label="Digit 4 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp4" oninput="handleOtpInput(4, 'mobile')" onkeydown="handleOtpKey(4, event, 'mobile')" aria-label="Digit 5 of 6" />
                <input type="text" maxlength="1" inputmode="numeric" class="auth-otp-box" id="mobileOtp5" oninput="handleOtpInput(5, 'mobile')" onkeydown="handleOtpKey(5, event, 'mobile')" aria-label="Digit 6 of 6" />
              </div>

              <!-- OTP Status Message -->
              <div id="mobileOtpFeedback" style="font-size:11.5px;font-weight:600;min-height:18px;margin-bottom:12px;text-align:center;"></div>

              <!-- Resend Timer -->
              <div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:16px;">
                <span id="mobileResendTimerText" style="color:var(--text-secondary);">Resend OTP in 00:30</span>
                <button id="btnResendMobileOtp" style="display:none;background:none;border:none;color:var(--saffron);font-weight:700;cursor:pointer;" onclick="resendMobileOtp()">Resend OTP</button>
              </div>

              <!-- Simulated Auto-Read SMS Button -->
              <div style="text-align:center;margin-bottom:16px;">
                <button class="pill-chip" style="font-size:11px;padding:6px 14px;background:rgba(221,230,225,0.1);border-color:var(--accent-mint);color:var(--accent-mint);" onclick="autofillDemoOtp('849201', 'mobile')">
                  📨 Auto-fill from SMS: 849201
                </button>
              </div>

              <!-- Verify Button -->
              <button class="auth-btn-primary" id="btnVerifyMobileOtp" disabled onclick="verifyMobileOtp()">
                <span id="btnVerifyMobileOtpText">Verify & Continue</span>
              </button>
            </div>

            <div class="auth-terms-footer">
              Code expires in 10 minutes. Lockout occurs after 5 failed attempts.
            </div>
          </div>

          <!-- ==================== STEP 3: NEW USER PROFILE SETUP ==================== -->
          <div class="auth-step-view" id="authStepProfileSetup">
            <div>
              <div style="font-size:12px;font-weight:700;color:var(--saffron);margin-bottom:8px;">ALMOST DONE!</div>
              <h2 style="font-size:22px;font-weight:800;color:var(--text-primary);line-height:1.2;">Set up your profile</h2>
              <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;margin-bottom:18px;">Customize how you appear in Kannada Raaga</div>

              <!-- Avatar Selection -->
              <div style="text-align:center;margin-bottom:18px;">
                <div id="profileAvatarPreview" style="width:72px;height:72px;border-radius:50%;background:var(--saffron);color:#0B1110;font-size:32px;font-weight:900;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,0.4);border:2px solid var(--accent-mint);">ಕ</div>
                <div style="font-size:11px;color:var(--text-secondary);margin-top:6px;">Choose avatar icon:</div>
                <div style="display:flex;justify-content:center;gap:8px;margin-top:6px;">
                  <button class="pill-chip" onclick="selectAvatar('ಕ')">ಕ</button>
                  <button class="pill-chip" onclick="selectAvatar('👑')">👑</button>
                  <button class="pill-chip" onclick="selectAvatar('🪕')">🪕</button>
                  <button class="pill-chip" onclick="selectAvatar('🎶')">🎶</button>
                  <button class="pill-chip" onclick="selectAvatar('🦁')">🦁</button>
                </div>
              </div>

              <!-- Full Name Input -->
              <div class="auth-pill-input-group">
                <label class="auth-input-label" for="profileNameInput">YOUR NAME</label>
                <div class="auth-pill-input-box">
                  <input type="text" id="profileNameInput" class="auth-pill-input" placeholder="e.g. Vinay Samaldar" />
                </div>
              </div>

              <!-- Language Preference -->
              <div style="margin-bottom:16px;">
                <label class="auth-input-label">PREFERRED APP LANGUAGE</label>
                <div style="display:flex;gap:8px;">
                  <button class="pill-chip active-mint" id="chipLangKannada" onclick="setProfileLanguage('kn')">ಕನ್ನಡ (Kannada)</button>
                  <button class="pill-chip" id="chipLangEnglish" onclick="setProfileLanguage('en')">English</button>
                  <button class="pill-chip" id="chipLangBoth" onclick="setProfileLanguage('both')">Both (ಎರಡೂ)</button>
                </div>
              </div>

              <!-- Keep Me Signed In -->
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:18px;font-size:12.5px;color:var(--text-primary);">
                <input type="checkbox" id="authKeepSignedIn" checked style="accent-color:var(--saffron);width:16px;height:16px;" />
                <label for="authKeepSignedIn" style="cursor:pointer;">Keep me signed in on this device</label>
              </div>

              <!-- Finish Button -->
              <button class="auth-btn-primary" onclick="completeProfileSetup()">
                <span>Get started →</span>
              </button>
            </div>

            <div class="auth-terms-footer">
              Welcome to the authentic home of Kannada music.
            </div>
          </div>

          <!-- ==================== ACCOUNT CONFLICT MODAL / LINKING VIEW ==================== -->
          <div class="auth-step-view" id="authStepConflict">
            <div>
              <div style="font-size:32px;margin-bottom:8px;">⚠️</div>
              <h2 style="font-size:20px;font-weight:800;color:var(--text-primary);line-height:1.2;">Account already exists</h2>
              <div style="font-size:13px;color:var(--text-secondary);margin-top:8px;line-height:1.5;">
                An account with <b id="conflictTargetDisplay" style="color:var(--text-primary);">user@example.com</b> already exists. Sign in with your original method to link them together.
              </div>

              <div style="background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:14px;margin:18px 0;">
                <div style="font-size:12px;font-weight:700;color:var(--accent-mint);">LINKED SECURITY:</div>
                <div style="font-size:11.5px;color:var(--text-secondary);margin-top:4px;">
                  Merging accounts will safely unify your liked songs, custom playlists, and downloaded offline files.
                </div>
              </div>

              <button class="auth-btn-primary" onclick="resolveAccountConflict('email')">
                <span>Sign in with Email to Link</span>
              </button>

              <button class="auth-btn-outlined" style="margin-top:10px;" onclick="goToAuthStep('stepWelcome')">
                <span>Back to Welcome</span>
              </button>
            </div>
          </div>

        </div> <!-- /auth-form-panel -->
      </div> <!-- /auth-container -->
    </div> <!-- /auth-modal-backdrop -->


    <!-- ==================== SEARCHABLE COUNTRY PICKER DROPDOWN SHEET ==================== -->
    <div class="auth-country-sheet-backdrop" id="countryPickerBackdrop" onclick="closeCountryPicker(event)">
      <div class="auth-country-sheet" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <div style="font-size:15px;font-weight:800;color:var(--accent-mint);">Select Country Code</div>
          <button class="auth-close-btn" style="width:28px;height:28px;" onclick="closeCountryPicker()">✕</button>
        </div>

        <div class="auth-pill-input-box" style="height:42px;margin-bottom:12px;">
          <span style="font-size:14px;margin-right:8px;color:var(--text-secondary);">🔍</span>
          <input type="text" id="countrySearchInput" class="auth-pill-input" placeholder="Search country or code..." oninput="filterCountryList()" />
        </div>

        <div style="flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:4px;" id="countryOptionsList">
          <!-- Populated by JavaScript -->
        </div>
      </div>
    </div>


    <!-- ==================== SYSTEM GOOGLE ACCOUNT CHOOSER SIMULATION ==================== -->
    <div class="auth-google-chooser-backdrop" id="googleChooserBackdrop" onclick="closeGoogleChooser(event)">
      <div class="auth-google-chooser-card" onclick="event.stopPropagation()">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
          <svg width="24" height="24" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
          <div>
            <div style="font-size:16px;font-weight:700;color:#1F1F1F;">Sign in with Google</div>
            <div style="font-size:12px;color:#5F6368;">Choose an account to continue to Kannada Raaga</div>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:4px;margin-bottom:16px;">
          <!-- Account Option 1 -->
          <div class="google-account-tile" onclick="selectGoogleAccount('Vinay Samaldar', 'vinay.kannada@gmail.com', 'V')">
            <div class="google-avatar-circle">V</div>
            <div style="flex:1;">
              <div style="font-weight:700;font-size:14px;color:#1F1F1F;">Vinay Samaldar</div>
              <div style="font-size:12px;color:#5F6368;">vinay.kannada@gmail.com</div>
            </div>
          </div>

          <!-- Account Option 2 -->
          <div class="google-account-tile" onclick="selectGoogleAccount('Dr. Rajkumar Fan Club', 'dr.rajkumar.fan@gmail.com', 'R')">
            <div class="google-avatar-circle" style="background:#E37400;">R</div>
            <div style="flex:1;">
              <div style="font-weight:700;font-size:14px;color:#1F1F1F;">Dr. Rajkumar Fan Club</div>
              <div style="font-size:12px;color:#5F6368;">dr.rajkumar.fan@gmail.com</div>
            </div>
          </div>

          <!-- Use Another Account -->
          <div class="google-account-tile" onclick="selectGoogleAccount('Kannada Devotee', 'kannada.music@gmail.com', 'K')">
            <div class="google-avatar-circle" style="background:#5F6368;">+</div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:13.5px;color:#1F1F1F;">Use another Google account</div>
            </div>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;padding-top:12px;border-top:1px solid #E0E0E0;">
          <button style="background:none;border:none;color:#1A73E8;font-size:12.5px;font-weight:700;cursor:pointer;" onclick="simulateGoogleAccountConflict()">
            ⚠️ Simulate Account Conflict
          </button>
          <button style="background:none;border:none;color:#5F6368;font-size:13px;font-weight:600;cursor:pointer;" onclick="closeGoogleChooser()">
            Cancel
          </button>
        </div>
      </div>
    </div>


    <!-- ==================== FIRST-LAUNCH PRIVACY, PERMISSIONS & CONSENT SHEET ==================== -->
    <div class="auth-consent-backdrop" id="authConsentBackdrop" onclick="closeAuthConsent(event)">
      <div class="auth-consent-card" onclick="event.stopPropagation()">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
          <div style="width:36px;height:36px;border-radius:10px;background:var(--saffron);color:#0B1110;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:900;">🛡️</div>
          <div>
            <div style="font-size:16px;font-weight:800;color:var(--text-primary);">Privacy & Permissions</div>
            <div style="font-size:11px;color:var(--text-secondary);">Your data rights under DPDP & GDPR</div>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:12px;margin:16px 0;">
          <div style="background:var(--surface);padding:12px 14px;border-radius:14px;border:1px solid var(--border);">
            <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:4px;">🔒 Private Code Security</div>
            <div style="font-size:11.5px;color:var(--text-secondary);line-height:1.4;">
              Verification codes and OTPs are never exposed in lock-screen notification previews to protect your account.
            </div>
          </div>

          <div style="background:var(--surface);padding:12px 14px;border-radius:14px;border:1px solid var(--border);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-size:13px;font-weight:700;color:var(--text-primary);">Under 18 Protection Mode</div>
                <div style="font-size:11.5px;color:var(--text-secondary);">Disables ad profiling automatically</div>
              </div>
              <input type="checkbox" id="consentUnder18Checkbox" onchange="handleUnder18Toggle(this.checked)" style="accent-color:var(--saffron);width:18px;height:18px;" />
            </div>
          </div>

          <div style="background:var(--surface);padding:12px 14px;border-radius:14px;border:1px solid var(--border);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-size:13px;font-weight:700;color:var(--text-primary);">Offline Smart Sync</div>
                <div style="font-size:11.5px;color:var(--text-secondary);">Saves downloaded song progress locally</div>
              </div>
              <input type="checkbox" checked style="accent-color:var(--accent-mint);width:18px;height:18px;" />
            </div>
          </div>
        </div>

        <button class="auth-btn-primary" onclick="acceptConsentAndContinue()">
          <span>I Agree & Continue</span>
        </button>
      </div>
    </div>


    <!-- ==================== COMPONENT SHEET (Pill Inputs, 6-Box Code, Country Picker, Social) ==================== -->
    <div class="auth-components-backdrop" id="authComponentsBackdrop" onclick="closeAuthComponents(event)">
      <div class="auth-components-card" onclick="event.stopPropagation()">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div>
            <div style="font-size:17px;font-weight:800;color:var(--accent-mint);">🧩 Auth Component Specification Gallery</div>
            <div style="font-size:11.5px;color:var(--text-secondary);">Touch targets 48-56px, WCAG Contrast, Fluid Scaling</div>
          </div>
          <button class="auth-close-btn" onclick="closeAuthComponents()">✕</button>
        </div>

        <div style="display:flex;flex-direction:column;gap:20px;">
          <!-- 1. Pill Inputs -->
          <div style="background:var(--surface);padding:16px;border-radius:18px;border:1px solid var(--border);">
            <div style="font-size:13px;font-weight:800;color:var(--saffron);margin-bottom:10px;">1. FULLY ROUNDED PILL INPUTS (50-52px)</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
              <div>
                <div style="font-size:11px;color:var(--text-secondary);margin-bottom:4px;">DEFAULT / EMPTY</div>
                <div class="auth-pill-input-box" style="height:46px;">
                  <input type="text" class="auth-pill-input" placeholder="name@example.com" />
                </div>
              </div>
              <div>
                <div style="font-size:11px;color:var(--saffron);margin-bottom:4px;">ACTIVE FOCUS STATE</div>
                <div class="auth-pill-input-box" style="height:46px;border-color:var(--saffron);box-shadow:0 0 0 3px rgba(242,169,0,0.25);">
                  <input type="text" class="auth-pill-input" value="active.user@kannadaraaga.com" />
                </div>
              </div>
              <div>
                <div style="font-size:11px;color:#E53935;margin-bottom:4px;">ERROR STATE</div>
                <div class="auth-pill-input-box error" style="height:46px;">
                  <input type="text" class="auth-pill-input" value="invalid-email" />
                </div>
                <div style="font-size:10.5px;color:#E53935;font-weight:600;margin-top:2px;">Enter a valid email address</div>
              </div>
              <div>
                <div style="font-size:11px;color:var(--text-secondary);margin-bottom:4px;">DISABLED STATE</div>
                <div class="auth-pill-input-box disabled" style="height:46px;">
                  <input type="text" class="auth-pill-input" value="disabled@example.com" disabled />
                </div>
              </div>
            </div>
          </div>

          <!-- 2. Six-Box Code Input -->
          <div style="background:var(--surface);padding:16px;border-radius:18px;border:1px solid var(--border);">
            <div style="font-size:13px;font-weight:800;color:var(--saffron);margin-bottom:10px;">2. SIX-BOX AUTO-ADVANCING CODE INPUT</div>
            <div style="display:flex;gap:8px;justify-content:center;">
              <input type="text" class="auth-otp-box filled" value="1" readonly />
              <input type="text" class="auth-otp-box filled" value="2" readonly />
              <input type="text" class="auth-otp-box filled" value="3" readonly />
              <input type="text" class="auth-otp-box" style="border-color:var(--saffron);box-shadow:0 0 0 3px rgba(242,169,0,0.25);" value="4" readonly />
              <input type="text" class="auth-otp-box" placeholder="•" readonly />
              <input type="text" class="auth-otp-box" placeholder="•" readonly />
            </div>
            <div style="font-size:11.5px;color:var(--text-secondary);text-align:center;margin-top:8px;">
              Supports auto-advance, backspace retreat, clipboard paste (splits 6 digits), and screen-reader ARIA labels.
            </div>
          </div>

          <!-- 3. Buttons & Social -->
          <div style="background:var(--surface);padding:16px;border-radius:18px;border:1px solid var(--border);">
            <div style="font-size:13px;font-weight:800;color:var(--saffron);margin-bottom:10px;">3. BUTTONS & SOCIAL CONTROLS</div>
            <div style="display:flex;flex-direction:column;gap:10px;">
              <button class="auth-btn-google">
                <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
                <span>Continue with Google (Google Brand Compliance)</span>
              </button>
              <button class="auth-btn-primary">
                <span>Primary Mint Button (#DDE6E1) with Dark Ink</span>
              </button>
              <button class="auth-btn-outlined">
                <span>Outlined Pill (#18211F Surface Border)</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
'''

# 2. INJECT AUTH MODALS INTO HTML
if 'authModalBackdrop' not in html:
    insert_point = html.find('<!-- ACCOUNT MODAL -->')
    if insert_point != -1:
        html = html[:insert_point] + AUTH_MODALS_HTML + '\n\n' + html[insert_point:]
        print('Injected Auth Modals HTML successfully.')
    else:
        print('Could not find insert point for auth modals.')
else:
    print('Auth modals already present.')

# 3. ADD BUTTONS TO WALKTHROUGH TOOLBAR
TOOLBAR_ITEMS = '''
      <span class="guide-step-chip" style="background:rgba(242,169,0,0.18);color:var(--saffron);border-color:var(--saffron);" onclick="openAuthModal()">🔐 Login / Sign-Up Flow</span>
      <span class="guide-step-chip" onclick="openAuthComponents()">🧩 Component Sheet</span>
      <span class="guide-step-chip" onclick="toggleLightDarkTheme()">🌓 Toggle Light/Dark</span>
      <span class="guide-step-chip" onclick="openAuthConsent()">🛡️ Privacy Consent</span>
'''

if 'openAuthModal()' not in html:
    guide_bar_pos = html.find('<div class="prototype-guide-bar">')
    if guide_bar_pos != -1:
        close_guide = html.find('</div>', guide_bar_pos)
        if close_guide != -1:
            html = html[:close_guide] + TOOLBAR_ITEMS + '\n    ' + html[close_guide:]
            print('Added walkthrough toolbar auth triggers.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved Auth HTML updates.')
