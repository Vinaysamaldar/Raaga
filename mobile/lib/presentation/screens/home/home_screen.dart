import 'package:flutter/material.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../data/catalog/sample_kannada_catalog.dart';
import '../../../domain/models/song.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';
import '../../widgets/song_tile.dart';

class HomeScreen extends StatefulWidget {
  final RaagaLocalizations l10n;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const HomeScreen({
    super.key,
    required this.l10n,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  KannadaCategory? _selectedCategory;

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final visibleCatalog = widget.downloadManager.offlineModeEnabled
        ? widget.catalog
            .where((s) => widget.downloadManager.isSongDownloaded(s.id))
            .toList()
        : widget.catalog;

    final filteredSongs = _selectedCategory == null
        ? visibleCatalog
        : visibleCatalog
            .where((s) => s.category == _selectedCategory)
            .toList();

    final trendingSongs = List<Song>.from(filteredSongs)
      ..sort((a, b) => b.popularityScore.compareTo(a.popularityScore));

    final newReleases = List<Song>.from(filteredSongs)
      ..sort((a, b) => b.year.compareTo(a.year));

    return ListView(
      padding: const EdgeInsets.only(bottom: 110),
      children: [
        // Cultural Hero Banner enforcing 100% Kannada Rule
        Container(
          margin: const EdgeInsets.all(14),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: const LinearGradient(
              colors: [RaagaColors.maroonPrimary, RaagaColors.maroonDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            border: Border.all(color: RaagaColors.mysoreGold.withOpacity(0.5)),
          ),
          child: Row(
            children: [
              const Icon(Icons.music_note, color: RaagaColors.mysoreGold, size: 38),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.tr('language_rule_badge'),
                      style: const TextStyle(
                        color: RaagaColors.mysoreGold,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'ಕನ್ನಡ ಚಲನಚಿತ್ರ ಗೀತೆಗಳು • ಭಾವಗೀತೆ • ಜಾನಪದ • ದಾಸ ಸಾಹಿತ್ಯ • ವಚನ • ರಾಜ್ಯೋತ್ಸವ • ಶಾಸ್ತ್ರೀಯ',
                      style: TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // 7 Mandatory Kannada Categories Filter Bar
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          child: Text(
            l10n.tr('categories'),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
        ),
        SizedBox(
          height: 46,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: ChoiceChip(
                  label: Text(l10n.isKannada ? 'ಎಲ್ಲಾ (All)' : 'All Kannada'),
                  selected: _selectedCategory == null,
                  onSelected: (_) => setState(() => _selectedCategory = null),
                ),
              ),
              ...KannadaCategory.values.map((cat) {
                final isSelected = _selectedCategory == cat;
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: ChoiceChip(
                    label: Text(l10n.isKannada ? cat.labelKn : cat.labelEn),
                    selected: isSelected,
                    onSelected: (_) => setState(
                      () => _selectedCategory = isSelected ? null : cat,
                    ),
                  ),
                );
              }),
            ],
          ),
        ),

        const SizedBox(height: 14),

        // Day's Mood Playlists Carousel
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Text(
            l10n.tr('mood_playlists'),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 132,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 10),
            itemCount: SampleKannadaCatalog.moodPlaylists.length,
            itemBuilder: (context, idx) {
              final mood = SampleKannadaCatalog.moodPlaylists[idx];
              return Container(
                width: 225,
                margin: const EdgeInsets.symmetric(horizontal: 6),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(14),
                  gradient: LinearGradient(
                    colors: [
                      RaagaColors.maroonPrimary.withOpacity(0.9),
                      RaagaColors.darkCard,
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  border: Border.all(
                    color: RaagaColors.mysoreGold.withOpacity(0.35),
                  ),
                ),
                child: InkWell(
                  onTap: () {
                    if (filteredSongs.isNotEmpty) {
                      widget.audioController.playSong(
                        filteredSongs.first,
                        newQueue: filteredSongs,
                      );
                    }
                  },
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        mood['titleKn']!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: RaagaColors.mysoreGold,
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                      Text(
                        mood['titleEn']!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                      Text(
                        mood['subtitle']!,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),

        const SizedBox(height: 18),

        // Trending & Top 50 Kannada Section
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.tr('trending'),
                style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
              ),
              TextButton.icon(
                onPressed: () {
                  if (trendingSongs.isNotEmpty) {
                    widget.audioController.playSong(
                      trendingSongs.first,
                      newQueue: trendingSongs,
                    );
                  }
                },
                icon: const Icon(Icons.play_circle_fill, size: 18),
                label: Text(l10n.tr('top_50')),
              ),
            ],
          ),
        ),
        ...trendingSongs.map(
          (song) => SongTile(
            song: song,
            isPlaying: widget.audioController.currentSong?.id == song.id,
            isFavorite: widget.authService.isFavorite(song.id),
            downloadTask: widget.downloadManager.getTask(song.id),
            onTap: () {
              widget.audioController.playSong(song, newQueue: trendingSongs);
              widget.authService.recordListeningHistory(song);
            },
            onFavoriteToggle: () => widget.authService.toggleFavorite(song.id),
            onDownloadTap: () => widget.downloadManager.startDownload(song),
          ),
        ),

        const SizedBox(height: 16),

        // New Releases Section
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Text(
            l10n.tr('new_releases'),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
        ),
        ...newReleases.take(4).map(
              (song) => SongTile(
                song: song,
                isPlaying: widget.audioController.currentSong?.id == song.id,
                isFavorite: widget.authService.isFavorite(song.id),
                downloadTask: widget.downloadManager.getTask(song.id),
                onTap: () {
                  widget.audioController.playSong(song, newQueue: newReleases);
                  widget.authService.recordListeningHistory(song);
                },
                onFavoriteToggle: () =>
                    widget.authService.toggleFavorite(song.id),
                onDownloadTap: () => widget.downloadManager.startDownload(song),
              ),
            ),
      ],
    );
  }
}
