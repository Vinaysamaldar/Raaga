/// Complete Kannada Varnamale (ಅ to ಳ) and English A-Z constants,
/// plus script validation utilities for enforcing the Kannada-only content rule.
class KannadaAlphabet {
  /// Standard Kannada Swaragalu (Vowels), Yogavahagalu, and Vyanjanagalu (Consonants) from ಅ to ಳ.
  static const List<String> varnamale = [
    // Swaragalu (Vowels)
    'ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಅಂ', 'ಅಃ',
    // Vargiya Vyanjanagalu (Structured Consonants)
    'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ',
    'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ',
    'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ',
    'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ',
    'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ',
    // Avargiya Vyanjanagalu (Unstructured Consonants)
    'ಯ', 'ರ', 'ಲ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ',
  ];

  /// Standard English Alphabet A to Z for transliterated browsing.
  static const List<String> englishAlphabet = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  ];

  /// Unicode block for Kannada: U+0C80 to U+0CFF
  static final RegExp kannadaUnicodeRegex = RegExp(r'[\u0C80-\u0CFF]');

  /// Validates that a string contains genuine Kannada script characters.
  static bool containsKannadaScript(String input) {
    return kannadaUnicodeRegex.hasMatch(input);
  }

  /// Extracts the base Kannada akshara (consonant/vowel root) for A-to-Z indexing.
  /// E.g., "ಕಾಣದ" -> "ಕ", "ಆಕಾಶ" -> "ಆ", "ನನ್ನ" -> "ನ".
  static String extractKannadaInitial(String titleKn) {
    final trimmed = titleKn.trim();
    if (trimmed.isEmpty) return '#';

    // Check two-character yogavahagalu first ('ಅಂ', 'ಅಃ')
    if (trimmed.startsWith('ಅಂ')) return 'ಅಂ';
    if (trimmed.startsWith('ಅಃ')) return 'ಅಃ';

    final firstChar = String.fromCharCode(trimmed.runes.first);
    if (varnamale.contains(firstChar)) {
      return firstChar;
    }
    return firstChar;
  }

  /// Extracts the uppercase English initial A-Z from a transliterated title.
  static String extractEnglishInitial(String titleEn) {
    final trimmed = titleEn.trim().toUpperCase();
    if (trimmed.isEmpty) return '#';
    final first = trimmed[0];
    return englishAlphabet.contains(first) ? first : '#';
  }
}
