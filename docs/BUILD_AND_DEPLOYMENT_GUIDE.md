# Raaga (ರಾಗ) — Build & Deployment Guide (Google Play Store & Apple App Store)

## 1. Prerequisites
- **Flutter SDK**: `>= 3.22.0` (Dart `>= 3.2.0`)
- **Android**: Android Studio, JDK 17, Android SDK 34 (Target SDK 34, Min SDK 23 for mid-range Android optimization)
- **iOS**: Xcode 15+, CocoaPods, Apple Developer Account
- **Backend**: Node.js 20 LTS, PostgreSQL 16+ with `pg_trgm`, CloudFront / Cloudflare CDN for HLS segments

---

## 2. Running Locally

### 2.1 Backend & Admin Dashboard
```bash
cd C:\Users\DELL\.gemini\antigravity\scratch\raaga\backend
npm init -y
npm install express cors
node src/server.js
```
Open `backend/admin-dashboard/index.html` in any browser to test the Admin Upload Pipeline and verify that non-Kannada tracks are automatically rejected.

### 2.2 Flutter Mobile App (Android & iOS)
```bash
cd C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile
flutter pub get
flutter run
```

---

## 3. Platform Configuration for Background Audio, Lock-Screen & Car Support

### 3.1 Android (`android/app/src/main/AndroidManifest.xml`)
Include permissions for foreground audio service, wake lock, network state, and voice search:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.WAKE_LOCK"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
```
Declare `AudioService` and `MediaButtonReceiver` inside `<application>` for lock-screen, notification, Bluetooth AVRCP, and Android Auto support.

### 3.2 iOS (`ios/Runner/Info.plist`)
Enable background audio, CarPlay, and Kannada speech recognition:
```xml
<key>UIBackgroundModes</key>
<array>
  <string>audio</string>
  <string>fetch</string>
</array>
<key>NSMicrophoneUsageDescription</key>
<string>Raaga uses the microphone for Kannada and English voice search.</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>Raaga recognizes spoken Kannada song titles and artists.</string>
```

---

## 4. Production Release Builds

### 4.1 Android App Bundle (`.aab` for Google Play Store)
1. Generate upload keystore:
   ```bash
   keytool -genkey -v -keystore raaga-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias raaga
   ```
2. Build obfuscated & split-per-ABI bundle optimized for low-bandwidth downloads and mid-range phones:
   ```bash
   flutter build appbundle --release --obfuscate --split-debug-info=build/symbols
   ```
3. Upload `build/app/outputs/bundle/release/app-release.aab` to Google Play Console -> Production track.

### 4.2 iOS Archive (`.ipa` for Apple App Store)
1. Configure signing team and Bundle ID (`in.karnataka.raaga`) in Xcode.
2. Build release IPA:
   ```bash
   flutter build ipa --release --obfuscate --split-debug-info=build/ios-symbols
   ```
3. Upload `build/ios/ipa/raaga_kannada_music.ipa` via Xcode Organizer or Transporter to App Store Connect.
