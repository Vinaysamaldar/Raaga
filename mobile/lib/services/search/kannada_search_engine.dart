import 'dart:math';
import '../../domain/models/song.dart';

/// Kannada-aware Full-Text Search Engine supporting:
/// 1. Native Kannada Unicode script (e.g., "ಹುಟ್ಟಿದರೆ", "ಮುಂಗಾರು", "ವರಾಹ")
/// 2. English & Phonetic Transliteration (e.g., "huttidare", "mungaru male", "varaha")
/// 3. Typo tolerance using phonetic normalization + Levenshtein distance
class KannadaSearchEngine {
  /// Normalizes English transliterated Kannada strings to handle common spelling variations:
  /// e.g. "aa" -> "a", "ee" -> "i", "oo" -> "u", "th" -> "t", "dh" -> "d", "sh" -> "s", "bh" -> "b"
  static String normalizeTransliteration(String input) {
    var s = input.toLowerCase().trim();
    final replacements = <String, String>{
      'aa': 'a',
      'ee': 'i',
      'oo': 'u',
      'ou': 'au',
      'th': 't',
      'dh': 'd',
      'bh': 'b',
      'gh': 'g',
      'kh': 'k',
      'ch': 'c',
      'sh': 's',
      'zh': 'l',
      'v': 'w',
      'y': 'i',
    };
    replacements.forEach((pattern, replacement) {
      s = s.replaceAll(pattern, replacement);
    });
    // Collapse repeated characters (e.g. "malligeya" -> "maligeya")
    s = s.replaceAllMapped(RegExp(r'(.)\1+'), (m) => m.group(1)!);
    return s;
  }

  /// Computes Levenshtein edit distance between two strings for typo tolerance.
  static int levenshteinDistance(String s1, String s2) {
    if (s1 == s2) return 0;
    if (s1.isEmpty) return s2.length;
    if (s2.isEmpty) return s1.length;

    List<int> v0 = List<int>.generate(s2.length + 1, (i) => i);
    List<int> v1 = List<int>.filled(s2.length + 1, 0);

    for (int i = 0; i < s1.length; i++) {
      v1[0] = i + 1;
      for (int j = 0; j < s2.length; j++) {
        final cost = (s1[i] == s2[j]) ? 0 : 1;
        v1[j + 1] = min(v1[j] + 1, min(v0[j + 1] + 1, v0[j] + cost));
      }
      final temp = v0;
      v0 = v1;
      v1 = temp;
    }
    return v0[s2.length];
  }

  /// Searches the Kannada catalog across Kannada script, English transliteration,
  /// artist, singer, composer, lyricist, movie/album, and lyrics with typo tolerance.
  static List<Song> search({
    required List<Song> catalog,
    required String query,
    KannadaCategory? categoryFilter,
  }) {
    final baseList = categoryFilter == null
        ? catalog
        : catalog.where((s) => s.category == categoryFilter).toList();

    final trimmed = query.trim();
    if (trimmed.isEmpty) return baseList;

    final lowerQuery = trimmed.toLowerCase();
    final phoneticQuery = normalizeTransliteration(lowerQuery);

    final scoredResults = <({Song song, double score})>[];

    for (final song in baseList) {
      double score = 0.0;

      // 1. Direct Kannada script match
      if (song.titleKn.contains(trimmed)) {
        score += 100.0;
      }
      for (final lyric in song.syncedLyrics) {
        if (lyric.kannadaLine.contains(trimmed)) {
          score += 50.0;
        }
      }

      // 2. Direct substring match on English transliteration / metadata
      final searchableFields = [
        song.titleEn.toLowerCase(),
        song.artist.toLowerCase(),
        song.singer.toLowerCase(),
        song.composer.toLowerCase(),
        song.lyricist.toLowerCase(),
        song.movieOrAlbum.toLowerCase(),
        song.genre.toLowerCase(),
      ];

      for (final field in searchableFields) {
        if (field.contains(lowerQuery)) {
          score += 80.0;
        }
        final normField = normalizeTransliteration(field);
        if (normField.contains(phoneticQuery)) {
          score += 65.0;
        }

        // 3. Word-level typo tolerance (Levenshtein distance <= 2)
        final words = field.split(RegExp(r'\s+'));
        for (final word in words) {
          if (word.length >= 4 && lowerQuery.length >= 4) {
            final dist = levenshteinDistance(
              normalizeTransliteration(word),
              phoneticQuery,
            );
            if (dist <= 2) {
              score += (40.0 - dist * 12.0);
            }
          }
        }
      }

      if (score > 0) {
        scoredResults.add((song: song, score: score));
      }
    }

    scoredResults.sort((a, b) => b.score.compareTo(a.score));
    return scoredResults.map((e) => e.song).toList();
  }
}
