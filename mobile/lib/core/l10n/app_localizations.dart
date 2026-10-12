import 'package:flutter/material.dart';

/// Bilingual UI Dictionary for Raaga (Kannada & English), switchable at runtime.
class RaagaLocalizations {
  final Locale locale;
  RaagaLocalizations(this.locale);

  bool get isKannada => locale.languageCode == 'kn';

  static const Map<String, Map<String, String>> _strings = {
    'en': {
      'app_title': 'Raaga',
      'app_subtitle': '100% Exclusive Kannada Music',
      'nav_home': 'Home',
      'nav_browse': 'Browse (A–Z)',
      'nav_search': 'Search',
      'nav_library': 'Library',
      'nav_downloads': 'Downloads',
      'trending': 'Trending in Karnataka',
      'new_releases': 'New Releases',
      'top_50': 'Top 50 Kannada',
      'recommended': 'Recommended For You',
      'mood_playlists': 'Today\'s Mood Playlists',
      'categories': 'Kannada Categories',
      'offline_mode': 'Offline Mode',
      'offline_banner': 'Offline Mode Active • Showing encrypted local tracks',
      'wifi_only': 'Download over Wi-Fi only',
      'search_hint': 'Search in ಕನ್ನಡ, English, or transliteration...',
      'voice_search': 'Voice Search (ಕನ್ನಡ / English)',
      'sort_title': 'Title',
      'sort_year': 'Year',
      'sort_popularity': 'Popularity',
      'browse_songs': 'Songs',
      'browse_artists': 'Artists',
      'browse_movies': 'Movies',
      'browse_albums': 'Albums',
      'lyrics_title': 'Synced Lyrics (ಕನ್ನಡ + English)',
      'sleep_timer': 'Sleep Timer',
      'equalizer': 'Equalizer',
      'streaming_quality': 'Streaming Quality',
      'quality_low': 'Low (64 kbps • Data Saver)',
      'quality_med': 'Medium (128 kbps • Balanced)',
      'quality_high': 'High (320 kbps • HD Audio)',
      'favorites': 'Favorites',
      'playlists': 'Playlists',
      'history': 'Listening History',
      'settings': 'Settings & Preferences',
      'legal_licensing': 'Licensing, Terms & Copyright',
      'sign_in': 'Sign In (Phone OTP / Google)',
      'language_rule_badge': 'Verified Language: ಕನ್ನಡ (Kannada Only)',
    },
    'kn': {
      'app_title': 'ರಾಗ (Raaga)',
      'app_subtitle': 'ಅಪ್ಪಟ ಕನ್ನಡ ಸಂಗೀತ ಮಾತ್ರ',
      'nav_home': 'ಮುಖಪುಟ',
      'nav_browse': 'ಅ–ಳ ಪಟ್ಟಿ',
      'nav_search': 'ಹುಡುಕಿ',
      'nav_library': 'ಸಂಗ್ರಹ',
      'nav_downloads': 'ಡೌನ್‌ಲೋಡ್ಸ್',
      'trending': 'ಟ್ರೆಂಡಿಂಗ್ ಕನ್ನಡ ಹಾಡುಗಳು',
      'new_releases': 'ಹೊಸ ಬಿಡುಗಡೆಗಳು',
      'top_50': 'ಟಾಪ್ ೫೦ ಕನ್ನಡ',
      'recommended': 'ನಿಮಗಾಗಿ ಆಯ್ದ ಹಾಡುಗಳು',
      'mood_playlists': 'ಇಂದಿನ ಮೂಡ್ ಪ್ಲೇಲಿಸ್ಟ್‌ಗಳು',
      'categories': 'ಕನ್ನಡ ಸಂಗೀತ ಪ್ರಕಾರಗಳು',
      'offline_mode': 'ಆಫ್‌ಲೈನ್ ಮೋಡ್',
      'offline_banner': 'ಆಫ್‌ಲೈನ್ ಮೋಡ್ ಸಕ್ರಿಯವಾಗಿದೆ • ಡೌನ್‌ಲೋಡ್ ಆದ ಹಾಡುಗಳು ಮಾತ್ರ',
      'wifi_only': 'ವೈ-ಫೈ ಮೂಲಕ ಮಾತ್ರ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ',
      'search_hint': 'ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಹಾಡುಗಳನ್ನು ಹುಡುಕಿ...',
      'voice_search': 'ಧ್ವನಿ ಹುಡುಕಾಟ (ಕನ್ನಡ / English)',
      'sort_title': 'ಹೆಸರು',
      'sort_year': 'ವರ್ಷ',
      'sort_popularity': 'ಜನಪ್ರಿಯತೆ',
      'browse_songs': 'ಹಾಡುಗಳು',
      'browse_artists': 'ಕಲಾವಿದರು',
      'browse_movies': 'ಚಲನಚಿತ್ರಗಳು',
      'browse_albums': 'ಆಲ್ಬಮ್‌ಗಳು',
      'lyrics_title': 'ಸಾಹಿತ್ಯ (ಕನ್ನಡ ಮತ್ತು ಇಂಗ್ಲಿಷ್)',
      'sleep_timer': 'ಸ್ಲೀಪ್ ಟೈಮರ್',
      'equalizer': 'ಈಕ್ವಲೈಜರ್',
      'streaming_quality': 'ಸ್ಟ್ರೀಮಿಂಗ್ ಗುಣಮಟ್ಟ',
      'quality_low': 'ಕಡಿಮೆ (64 kbps • ಡೇಟಾ ಉಳಿತಾಯ)',
      'quality_med': 'ಮಧ್ಯಮ (128 kbps • ಸಮತೋಲಿತ)',
      'quality_high': 'ಉತ್ತಮ (320 kbps • HD ಆಡಿಯೋ)',
      'favorites': 'ನೆಚ್ಚಿನ ಹಾಡುಗಳು',
      'playlists': 'ಪ್ಲೇಲಿಸ್ಟ್‌ಗಳು',
      'history': 'ಕೇಳಿದ ಹಾಡುಗಳ ಇತಿಹಾಸ',
      'settings': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
      'legal_licensing': 'ಪರವಾನಗಿ ಮತ್ತು ಹಕ್ಕುಸ್ವಾಮ್ಯ ನಿಯಮಗಳು',
      'sign_in': 'ಸೈನ್ ಇನ್ (ಮೊಬೈಲ್ OTP / Google)',
      'language_rule_badge': 'ದೃಢೀಕರಿಸಿದ ಭಾಷೆ: ಕನ್ನಡ ಮಾತ್ರ',
    },
  };

  String tr(String key) {
    final langMap = _strings[locale.languageCode] ?? _strings['en']!;
    return langMap[key] ?? _strings['en']![key] ?? key;
  }
}
