import 'package:flutter/material.dart';

/// Material You Dark Green-Black Style Guide for "Kannada Raaga" (390x844 Android-first)
/// - Background: #0B1110 (Very dark green-black)
/// - Cards & Chips: #18211F (Slightly lighter charcoal)
/// - Primary Text: #E3EAE6 (Off-white)
/// - Secondary Text: #8A9490 (Muted grey)
/// - Primary Accent: #DDE6E1 (Soft pale mint-white for Play, FAB, Recognize)
/// - Highlight Accent: #F2A900 (Kannada saffron for active chips & download progress)
class RaagaColors {
  static const Color darkBackground = Color(0xFF0B1110);
  static const Color amoledBackground = Color(0xFF000000);
  static const Color darkSurface = Color(0xFF18211F);
  static const Color darkCard = Color(0xFF18211F);
  static const Color darkElevated = Color(0xFF212D2A);

  static const Color primaryText = Color(0xFFE3EAE6);
  static const Color secondaryText = Color(0xFF8A9490);

  // Soft Pale Mint-White Accent & Kannada Saffron Highlight
  static const Color mintAccent = Color(0xFFDDE6E1);
  static const Color saffronHighlight = Color(0xFFF2A900);

  // Backwards-compatible aliases used across screens
  static const Color maroonPrimary = Color(0xFF18211F);
  static const Color maroonDark = Color(0xFF0B1110);
  static const Color mysoreGold = Color(0xFFDDE6E1);
  static const Color mysoreGoldLight = Color(0xFFE3EAE6);
  static const Color saffronAccent = Color(0xFFF2A900);

  // Light Mode Tonal Palette
  static const Color lightBackground = Color(0xFFF3F7F5);
  static const Color lightSurface = Color(0xFFE3ECE8);
  static const Color lightCard = Color(0xFFFFFFFF);

  static const Color successGreen = Color(0xFF2E7D32);
  static const Color warningAmber = Color(0xFFF2A900);
  static const Color errorRed = Color(0xFFD32F2F);
}

class RaagaTheme {
  static const String englishFontFamily = 'Montserrat';

  static ThemeData get darkTheme {
    final colorScheme = const ColorScheme.dark(
      primary: RaagaColors.mintAccent,
      onPrimary: RaagaColors.darkBackground,
      primaryContainer: RaagaColors.darkSurface,
      onPrimaryContainer: RaagaColors.primaryText,
      secondary: RaagaColors.saffronHighlight,
      onSecondary: RaagaColors.darkBackground,
      surface: RaagaColors.darkSurface,
      onSurface: RaagaColors.primaryText,
      error: RaagaColors.errorRed,
    );

    return ThemeData(
      useMaterial3: true,
      fontFamily: englishFontFamily,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: RaagaColors.darkBackground,
      colorScheme: colorScheme,
      cardTheme: CardTheme(
        color: RaagaColors.darkCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: RaagaColors.darkBackground,
        foregroundColor: RaagaColors.primaryText,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontSize: 28,
          fontWeight: FontWeight.w800,
          color: RaagaColors.primaryText,
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: RaagaColors.darkSurface,
        selectedColor: RaagaColors.saffronHighlight,
        labelStyle: const TextStyle(color: RaagaColors.primaryText, fontSize: 13),
        secondaryLabelStyle: const TextStyle(
          color: RaagaColors.darkBackground,
          fontWeight: FontWeight.w700,
        ),
        shape: const StadiumBorder(),
        side: BorderSide.none,
      ),
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: RaagaColors.mintAccent,
        foregroundColor: RaagaColors.darkBackground,
        shape: CircleBorder(),
      ),
      sliderTheme: SliderThemeData(
        activeTrackColor: RaagaColors.mintAccent,
        inactiveTrackColor: RaagaColors.secondaryText.withOpacity(0.28),
        thumbColor: RaagaColors.mintAccent,
      ),
    );
  }

  static ThemeData get lightTheme {
    final colorScheme = const ColorScheme.light(
      primary: RaagaColors.darkSurface,
      onPrimary: RaagaColors.primaryText,
      primaryContainer: RaagaColors.lightSurface,
      onPrimaryContainer: RaagaColors.darkBackground,
      secondary: RaagaColors.saffronHighlight,
      onSecondary: RaagaColors.darkBackground,
      surface: RaagaColors.lightSurface,
      onSurface: RaagaColors.darkBackground,
      error: RaagaColors.errorRed,
    );

    return ThemeData(
      useMaterial3: true,
      fontFamily: englishFontFamily,
      brightness: Brightness.light,
      scaffoldBackgroundColor: RaagaColors.lightBackground,
      colorScheme: colorScheme,
      cardTheme: CardTheme(
        color: RaagaColors.lightCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: RaagaColors.lightBackground,
        foregroundColor: RaagaColors.darkBackground,
        elevation: 0,
        centerTitle: false,
      ),
      chipTheme: const ChipThemeData(
        backgroundColor: RaagaColors.lightSurface,
        selectedColor: RaagaColors.saffronHighlight,
        shape: StadiumBorder(),
        side: BorderSide.none,
      ),
    );
  }
}
