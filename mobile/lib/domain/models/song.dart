import '../../core/constants/kannada_alphabet.dart';

/// All 7 mandatory Kannada music categories defined by Raaga Content Rules.
enum KannadaCategory {
  filmSongs(
    id: 'film_songs',
    labelEn: 'Kannada Film Songs',
    labelKn: 'ಚಲನಚಿತ್ರ ಗೀತೆಗಳು',
    subtitleEn: 'Golden classics to latest Sandalwood hits',
  ),
  bhavageethe(
    id: 'bhavageethe',
    labelEn: 'Bhavageethe',
    labelKn: 'ಭಾವಗೀತೆ',
    subtitleEn: 'Poetic melodies of Kuvempu, Bendre, Adiga &KSN',
  ),
  janapadaFolk(
    id: 'janapada',
    labelEn: 'Folk (Janapada)',
    labelKn: 'ಜನಪದ ಗೀತೆಗಳು',
    subtitleEn: 'Authentic rural folk songs of Karnataka',
  ),
  devotional(
    id: 'devotional',
    labelEn: 'Devotional (Dasa Sahitya & Vachanas)',
    labelKn: 'ದಾಸ ಸಾಹಿತ್ಯ ಮತ್ತು ವಚನಗಳು',
    subtitleEn: 'Purandaradasa, Kanakadasa, Basavanna & Bhajans',
  ),
  rajyotsava(
    id: 'rajyotsava',
    labelEn: 'Rajyotsava & Patriotic',
    labelKn: 'ಕನ್ನಡ ರಾಜ್ಯೋತ್ಸವ ಗೀತೆಗಳು',
    subtitleEn: 'Anthems celebrating Naadu, Nudi & Kannada pride',
  ),
  indieAlbums(
    id: 'indie',
    labelEn: 'Kannada Indie & Albums',
    labelKn: 'ಕನ್ನಡ ಇಂಡಿ ಮತ್ತು ಆಲ್ಬಮ್ಸ್',
    subtitleEn: 'Contemporary Kannada bands, rap & independent music',
  ),
  carnaticClassical(
    id: 'carnatic',
    labelEn: 'Kannada Devotional / Classical (Carnatic)',
    labelKn: 'ಕರ್ನಾಟಕ ಶಾಸ್ತ್ರೀಯ ಸಂಗೀತ',
    subtitleEn: 'Kritis, Varnams & Classical compositions in Kannada',
  );

  final String id;
  final String labelEn;
  final String labelKn;
  final String subtitleEn;

  const KannadaCategory({
    required this.id,
    required this.labelEn,
    required this.labelKn,
    required this.subtitleEn,
  });
}

/// Time-synced lyric line supporting both Kannada script and English transliteration.
class SyncedLyricLine {
  final Duration timestamp;
  final String kannadaLine;
  final String englishTransliteration;

  const SyncedLyricLine({
    required this.timestamp,
    required this.kannadaLine,
    required this.englishTransliteration,
  });

  Map<String, dynamic> toJson() => {
        'timestampMs': timestamp.inMilliseconds,
        'kannadaLine': kannadaLine,
        'englishTransliteration': englishTransliteration,
      };

  factory SyncedLyricLine.fromJson(Map<String, dynamic> json) => SyncedLyricLine(
        timestamp: Duration(milliseconds: json['timestampMs'] as int),
        kannadaLine: json['kannadaLine'] as String,
        englishTransliteration: json['englishTransliteration'] as String,
      );
}

/// Adaptive bitrate stream URLs for Low (64k), Medium (128k), and High (320k).
class AdaptiveStreams {
  final String low64kUrl;
  final String medium128kUrl;
  final String high320kUrl;

  const AdaptiveStreams({
    required this.low64kUrl,
    required this.medium128kUrl,
    required this.high320kUrl,
  });

  Map<String, dynamic> toJson() => {
        'low64kUrl': low64kUrl,
        'medium128kUrl': medium128kUrl,
        'high320kUrl': high320kUrl,
      };

  factory AdaptiveStreams.fromJson(Map<String, dynamic> json) => AdaptiveStreams(
        low64kUrl: json['low64kUrl'] as String,
        medium128kUrl: json['medium128kUrl'] as String,
        high320kUrl: json['high320kUrl'] as String,
      );
}

/// Strict domain model for a Kannada song.
/// Enforces `language == "Kannada"` and Kannada script validation at instantiation.
class Song {
  static const String requiredLanguageTag = 'Kannada';

  final String id;
  final String titleKn; // Kannada script title
  final String titleEn; // English transliterated title
  final String artist;
  final String singer;
  final String composer;
  final String lyricist;
  final String movieOrAlbum;
  final int year;
  final KannadaCategory category;
  final String genre;
  final int durationSeconds;
  final String coverArtUrl;
  final String language; // MUST always be "Kannada"
  final AdaptiveStreams streams;
  final List<SyncedLyricLine> syncedLyrics;
  final String labelName; // e.g., Anand Audio, Lahari Music, Saregama, PRK Audio
  final String isrcCode;
  final int popularityScore; // 1 - 100 for sorting

  Song({
    required this.id,
    required this.titleKn,
    required this.titleEn,
    required this.artist,
    required this.singer,
    required this.composer,
    required this.lyricist,
    required this.movieOrAlbum,
    required this.year,
    required this.category,
    required this.genre,
    required this.durationSeconds,
    required this.coverArtUrl,
    this.language = requiredLanguageTag,
    required this.streams,
    required this.syncedLyrics,
    required this.labelName,
    required this.isrcCode,
    this.popularityScore = 80,
  }) {
    if (language != requiredLanguageTag) {
      throw ArgumentError(
        'Raaga Content Rule Violation: Rejected track "$titleEn". '
        'Only language="Kannada" is permitted (got "$language").',
      );
    }
    if (!KannadaAlphabet.containsKannadaScript(titleKn)) {
      throw ArgumentError(
        'Raaga Content Rule Violation: Track "$titleEn" must include valid Kannada script in titleKn.',
      );
    }
  }

  /// Initial Kannada letter (ಅ–ಳ) for Varnamale browsing.
  String get kannadaInitial => KannadaAlphabet.extractKannadaInitial(titleKn);

  /// Initial English letter (A–Z) for transliterated browsing.
  String get englishInitial => KannadaAlphabet.extractEnglishInitial(titleEn);

  String get formattedDuration {
    final minutes = durationSeconds ~/ 60;
    final seconds = (durationSeconds % 60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'titleKn': titleKn,
        'titleEn': titleEn,
        'artist': artist,
        'singer': singer,
        'composer': composer,
        'lyricist': lyricist,
        'movieOrAlbum': movieOrAlbum,
        'year': year,
        'category': category.id,
        'genre': genre,
        'durationSeconds': durationSeconds,
        'coverArtUrl': coverArtUrl,
        'language': language,
        'streams': streams.toJson(),
        'syncedLyrics': syncedLyrics.map((l) => l.toJson()).toList(),
        'labelName': labelName,
        'isrcCode': isrcCode,
        'popularityScore': popularityScore,
      };

  factory Song.fromJson(Map<String, dynamic> json) {
    final categoryId = json['category'] as String;
    final category = KannadaCategory.values.firstWhere(
      (c) => c.id == categoryId,
      orElse: () => KannadaCategory.filmSongs,
    );
    return Song(
      id: json['id'] as String,
      titleKn: json['titleKn'] as String,
      titleEn: json['titleEn'] as String,
      artist: json['artist'] as String,
      singer: json['singer'] as String,
      composer: json['composer'] as String,
      lyricist: json['lyricist'] as String,
      movieOrAlbum: json['movieOrAlbum'] as String,
      year: json['year'] as int,
      category: category,
      genre: json['genre'] as String,
      durationSeconds: json['durationSeconds'] as int,
      coverArtUrl: json['coverArtUrl'] as String,
      language: json['language'] as String,
      streams: AdaptiveStreams.fromJson(json['streams'] as Map<String, dynamic>),
      syncedLyrics: (json['syncedLyrics'] as List<dynamic>)
          .map((e) => SyncedLyricLine.fromJson(e as Map<String, dynamic>))
          .toList(),
      labelName: json['labelName'] as String,
      isrcCode: json['isrcCode'] as String,
      popularityScore: json['popularityScore'] as int? ?? 80,
    );
  }
}
