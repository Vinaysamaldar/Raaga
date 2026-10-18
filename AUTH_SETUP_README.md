# Ragaa Authentication System Setup Guide

This document describes how to configure, run, and deploy the full passwordless login and sign-up system for Ragaa (Kannada-only music app).

---

## 1. Zero-Config Demo Mode (Default)
If Firebase API keys are absent, Ragaa automatically boots in **Demo Mode**:
* A visible banner indicates: *"Demo mode: any 6-digit code works (e.g. 849201)"*.
* Google Sign-In, Mobile OTP (+91 98XXXXXX10), and Email verification work instantly without live credentials.
* Sessions persist in `localStorage` across page refreshes and function 100% offline.

---

## 2. Production Firebase Setup

### A. Create Firebase Project
1. Visit the [Firebase Console](https://console.firebase.google.com/) and create a project named **Ragaa**.
2. Enable **Firestore Database** in production mode.
3. Enable **Authentication** with the following providers:
   * **Google**
   * **Phone** (ensure Invisible reCAPTCHA is enabled in your domain list)
   * **Custom Auth** (enabled automatically for Cloud Functions Custom Tokens)

### B. Deploy Cloud Functions & Security Rules
1. Install the Firebase CLI:
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase use --add <your-project-id>
   ```
2. Deploy Firestore Rules:
   ```bash
   firebase deploy --only firestore:rules
   ```
3. Deploy Cloud Functions:
   ```bash
   cd functions
   npm install
   cd ..
   firebase deploy --only functions
   ```

### C. Client Configuration
Copy `.env.example` to `.env` or populate your Vercel project environment variables:
* `FIREBASE_API_KEY`
* `FIREBASE_AUTH_DOMAIN`
* `FIREBASE_PROJECT_ID`
* `FIREBASE_STORAGE_BUCKET`
* `FIREBASE_MESSAGING_SENDER_ID`
* `FIREBASE_APP_ID`
* `RAGAA_AUTH_SECRET`

---

## 3. Security & Rate Limiting Guarantees
* **Code Hash Storage**: Email codes are hashed with SHA-256 + HMAC salt before storing in Firestore. The database never contains plaintext codes.
* **Access Rules**: Firestore security rules (`firestore.rules`) completely disallow client read/write to `ragaa_email_codes`. Only the Admin SDK in Cloud Functions has access.
* **Expiration**: Codes expire strictly after 10 minutes (600s).
* **Single-Use**: Upon successful verification, codes are permanently marked as `used`.
* **Rate Limits**:
  * 30-second cooldown between resends.
  * Maximum 5 code requests per hour per email.
  * Maximum 5 wrong attempts before a mandatory 15-minute account lock.
* **PII & Logging**: Plaintext email addresses and raw codes are never logged to Cloud Logging.
