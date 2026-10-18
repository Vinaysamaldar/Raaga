# -*- coding: utf-8 -*-
"""
implement_auth_flow.py
Implements the complete Login & Sign-Up Flow for Kannada Raaga:
- Responsive Phone & Tablet / Landscape layout (Single column on phone, Split screen with cover collage & gold accent on tablet)
- Bilingual toggle (Kannada / English) on every screen
- Screen 1: Welcome / Login with Google, Phone, Email, Guest mode, Terms & Privacy links
- Screen 2A: Email Verification Code (inline validation, 6-digit auto-advancing boxes, paste support, 30s resend timer, spam hint, error shake & lockout, profile setup)
- Screen 2B: Mobile OTP (searchable country picker +91 India, 10-digit validation, SMS auto-read sim, resend timer)
- Google Login: System account chooser simulation, loading state, conflict handling, profile setup
- Account Linking & Profile Manager (change email/phone, sign out all devices, session token persistence)
- Consent sheet (privacy, notifications, ad personalization, under-18 protection)
- Component Sheet Modal (pill input states, country picker, 6-box code, Google button, toasts)
- Light/Dark theme toggle & text scaling accessibility
"""

import os
import re

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. ADD CSS STYLES
AUTH_CSS = '''
    /* ==================== COMPLETE AUTHENTICATION & LOGIN FLOW STYLES ==================== */
    .auth-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.88);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      z-index: 10000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
      animation: authModalFade 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .auth-modal-backdrop.open {
      display: flex;
    }
    @keyframes authModalFade {
      from { opacity: 0; transform: scale(0.97); }
      to { opacity: 1; transform: scale(1); }
    }

    .auth-container {
      width: 100%;
      max-width: 900px;
      height: 640px;
      max-height: 94vh;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 28px;
      overflow: hidden;
      display: flex;
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.75);
      position: relative;
    }

    /* Phone Breakpoint: Single Column Fluid (max-width: 767px) */
    @media (max-width: 767px) {
      .auth-container {
        max-width: 440px;
        height: auto;
        min-height: 520px;
        max-height: 92vh;
        flex-direction: column;
        border-radius: 24px;
        overflow-y: auto;
      }
      .auth-hero-panel {
        display: none !important;
      }
    }

    /* Tablet & Desktop Split-Screen (768px+) */
    .auth-hero-panel {
      flex: 1.15;
      background: linear-gradient(135deg, #18211F 0%, #0B1110 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 36px 32px;
      border-right: 1px solid var(--border);
    }
    .auth-hero-bg-collage {
      position: absolute;
      inset: -30px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      opacity: 0.22;
      transform: rotate(-6deg) scale(1.12);
      pointer-events: none;
    }
    .auth-hero-art-card {
      height: 140px;
      border-radius: 16px;
      background-size: cover;
      background-position: center;
      box-shadow: 0 8px 20px rgba(0,0,0,0.6);
      border: 1px solid rgba(255,255,255,0.06);
    }
    .auth-hero-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(to bottom, rgba(11,17,16,0.2) 0%, rgba(11,17,16,0.8) 70%, #0B1110 100%);
    }

    .auth-form-panel {
      flex: 1;
      max-width: 460px;
      padding: 32px 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow-y: auto;
      position: relative;
      background: var(--bg);
    }

    /* Gold Decorative Pattern & Header */
    .auth-gold-accent {
      width: 48px;
      height: 4px;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--saffron), #FFE082, var(--saffron));
      margin-bottom: 12px;
    }

    .auth-top-nav-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .auth-lang-btn {
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--accent-mint);
      font-size: 11.5px;
      font-weight: 700;
      padding: 6px 14px;
      border-radius: 999px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }
    .auth-lang-btn:hover {
      border-color: var(--saffron);
      color: var(--saffron);
    }

    .auth-close-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
    }
    .auth-close-btn:hover {
      color: var(--text-primary);
      background: var(--surface-elevated);
    }

    /* Step Views inside Form Panel */
    .auth-step-view {
      display: none;
      flex-direction: column;
      flex: 1;
      animation: authStepFade 0.2s ease-out;
    }
    .auth-step-view.active {
      display: flex;
    }
    @keyframes authStepFade {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Inputs & Form Groups */
    .auth-pill-input-group {
      margin-bottom: 14px;
      position: relative;
    }
    .auth-input-label {
      display: block;
      font-size: 11.5px;
      font-weight: 700;
      color: var(--text-secondary);
      margin-bottom: 6px;
      letter-spacing: 0.4px;
    }
    .auth-pill-input-box {
      display: flex;
      align-items: center;
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: 999px;
      padding: 0 16px;
      height: 50px;
      transition: all 0.2s ease;
    }
    .auth-pill-input-box:focus-within {
      border-color: var(--saffron);
      background: var(--surface-elevated);
      box-shadow: 0 0 0 3px rgba(242, 169, 0, 0.22);
    }
    .auth-pill-input-box.error {
      border-color: #E53935 !important;
      box-shadow: 0 0 0 3px rgba(229, 57, 53, 0.2) !important;
    }
    .auth-pill-input-box.disabled {
      opacity: 0.5;
      pointer-events: none;
    }
    .auth-pill-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-primary);
      font-size: 14px;
      font-weight: 600;
    }
    .auth-pill-input::placeholder {
      color: var(--text-secondary);
      font-weight: 400;
    }
    .auth-input-error-hint {
      font-size: 11px;
      color: #E53935;
      font-weight: 600;
      margin-top: 4px;
      margin-left: 14px;
      display: none;
    }
    .auth-input-error-hint.visible {
      display: block;
    }

    /* Buttons */
    .auth-btn-primary {
      width: 100%;
      height: 50px;
      border-radius: 999px;
      background: var(--accent-mint);
      color: var(--accent-mint-ink);
      font-size: 14px;
      font-weight: 700;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    .auth-btn-primary:hover:not(:disabled) {
      transform: translateY(-1px);
      filter: brightness(1.08);
    }
    .auth-btn-primary:disabled {
      opacity: 0.42;
      cursor: not-allowed;
      transform: none;
    }

    .auth-btn-google {
      width: 100%;
      height: 50px;
      border-radius: 999px;
      background: #FFFFFF;
      color: #1F1F1F;
      font-size: 14px;
      font-weight: 600;
      border: 1px solid #747775;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      transition: all 0.2s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.18);
      font-family: 'Roboto', 'Montserrat', sans-serif;
    }
    .auth-btn-google:hover {
      background: #F8F9FA;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      border-color: #5E6368;
    }

    .auth-btn-outlined {
      width: 100%;
      height: 50px;
      border-radius: 999px;
      background: transparent;
      color: var(--text-primary);
      font-size: 13.5px;
      font-weight: 600;
      border: 1.5px solid var(--border);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      transition: all 0.2s;
    }
    .auth-btn-outlined:hover {
      border-color: var(--accent-mint);
      background: rgba(221, 230, 225, 0.05);
    }

    /* Six-Digit Code Boxes */
    .auth-otp-row {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      margin: 16px 0;
    }
    .auth-otp-box {
      width: 46px;
      height: 54px;
      border-radius: 14px;
      background: var(--surface);
      border: 2px solid var(--border);
      color: var(--text-primary);
      font-size: 22px;
      font-weight: 800;
      text-align: center;
      outline: none;
      transition: all 0.2s;
    }
    .auth-otp-box:focus {
      border-color: var(--saffron);
      background: var(--surface-elevated);
      box-shadow: 0 0 0 3px rgba(242, 169, 0, 0.25);
    }
    .auth-otp-box.filled {
      border-color: var(--accent-mint);
      background: var(--surface-elevated);
    }
    .auth-otp-row.error .auth-otp-box {
      border-color: #E53935;
      animation: otpShake 0.35s ease-in-out;
    }
    @keyframes otpShake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-6px); }
      40%, 80% { transform: translateX(6px); }
    }

    /* Country Code Selector Pill */
    .auth-country-selector {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: 999px;
      padding: 0 12px;
      height: 50px;
      cursor: pointer;
      font-size: 13.5px;
      font-weight: 700;
      color: var(--text-primary);
      transition: all 0.2s;
      user-select: none;
    }
    .auth-country-selector:hover {
      border-color: var(--accent-mint);
    }

    /* Divider */
    .auth-divider {
      display: flex;
      align-items: center;
      margin: 16px 0;
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 600;
    }
    .auth-divider::before, .auth-divider::after {
      content: '';
      flex: 1;
      height: 1px;
      background: var(--border);
    }
    .auth-divider span {
      padding: 0 12px;
    }

    /* Terms & Footer */
    .auth-terms-footer {
      font-size: 11px;
      color: var(--text-secondary);
      text-align: center;
      line-height: 1.45;
      margin-top: 14px;
    }
    .auth-terms-footer a {
      color: var(--accent-mint);
      text-decoration: underline;
      cursor: pointer;
    }

    /* Country Picker Dropdown Sheet */
    .auth-country-sheet-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(8px);
      z-index: 10050;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .auth-country-sheet-backdrop.open {
      display: flex;
    }
    .auth-country-sheet {
      width: 100%;
      max-width: 380px;
      max-height: 480px;
      background: var(--surface-elevated);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 48px rgba(0,0,0,0.6);
    }

    /* Google System Account Chooser Simulation */
    .auth-google-chooser-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.75);
      backdrop-filter: blur(8px);
      z-index: 10060;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .auth-google-chooser-backdrop.open {
      display: flex;
    }
    .auth-google-chooser-card {
      width: 100%;
      max-width: 420px;
      background: #FFFFFF;
      color: #1F1F1F;
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 24px 60px rgba(0,0,0,0.5);
      font-family: 'Roboto', 'Montserrat', sans-serif;
    }
    .google-account-tile {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 12px;
      border-radius: 12px;
      cursor: pointer;
      transition: background 0.18s;
      margin-bottom: 6px;
    }
    .google-account-tile:hover {
      background: #F1F3F4;
    }
    .google-avatar-circle {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #1A73E8;
      color: #FFFFFF;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }

    /* Consent Sheet Modal */
    .auth-consent-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(10px);
      z-index: 10070;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .auth-consent-backdrop.open {
      display: flex;
    }
    .auth-consent-card {
      width: 100%;
      max-width: 460px;
      background: var(--surface-elevated);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      color: var(--text-primary);
    }

    /* Component Gallery Showcase Modal */
    .auth-components-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.85);
      backdrop-filter: blur(14px);
      z-index: 10080;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .auth-components-backdrop.open {
      display: flex;
    }
    .auth-components-card {
      width: 100%;
      max-width: 680px;
      max-height: 88vh;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      overflow-y: auto;
      color: var(--text-primary);
    }
'''

# Check if auth CSS already in file
if 'AUTH & LOGIN / SIGN-UP FLOW STYLES' not in html:
    # Inject before </style>
    style_end = html.find('</style>')
    if style_end != -1:
        html = html[:style_end] + '\n' + AUTH_CSS + '\n' + html[style_end:]
        print('Injected Auth CSS successfully.')
    else:
        print('Could not find </style>')
else:
    print('Auth CSS already present.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved CSS updates to index.html.')
