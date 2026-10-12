import 'package:flutter/material.dart';
import '../../../core/constants/kannada_alphabet.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../domain/models/song.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';
import '../../widgets/song_tile.dart';

enum BrowseDimension { songs, artists, movies, albums }
enum SortOrder { title, year, popularity }

/// A-to-Z Browsing Screen featuring:
/// - Full Kannada Varnamale (ಅ, ಆ, ಇ, ಈ … ಳ) & English (A–Z) script toggle
/// - Browse by Songs, Artists, Movies, and Albums
/// - Sort by Title, Year, or Popularity
/// - Fast scrolling with interactive side letter-scrubber
class AzBrowseScreen extends StatefulWidget {
  final RaagaLocalizations l10n;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const AzBrowseScreen({
    super.key,
    required this.l10n,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  State<AzBrowseScreen> createState() => _AzBrowseScreenState();
}

class _AzBrowseScreenState extends State<AzBrowseScreen> {
  bool _useKannadaAlphabet = true; // true = ಅ–ಳ, false = A–Z
  String? _selectedLetter; // null = All letters
  BrowseDimension _dimension = BrowseDimension.songs;
  SortOrder _sortOrder = SortOrder.title;

  List<String> get _activeAlphabet => _useKannadaAlphabet
      ? KannadaAlphabet.varnamale
      : KannadaAlphabet.englishAlphabet;

  String _extractDimensionInitial(Song song) {
    switch (_dimension) {
      case BrowseDimension.songs:
        return _useKannadaAlphabet ? song.kannadaInitial : song.englishInitial;
      case BrowseDimension.artists:
        return KannadaAlphabet.extractEnglishInitial(song.artist);
      case BrowseDimension.movies:
      case BrowseDimension.albums:
        return KannadaAlphabet.extractEnglishInitial(song.movieOrAlbum);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final baseSongs = widget.downloadManager.offlineModeEnabled
        ? widget.catalog
            .where((s) => widget.downloadManager.isSongDownloaded(s.id))
            .toList()
        : List<Song>.from(widget.catalog);

    // Filter by selected letter
    final filtered = _selectedLetter == null
        ? baseSongs
        : baseSongs
            .where((s) => _extractDimensionInitial(s) == _selectedLetter)
            .toList();

    // Sort by Title, Year, or Popularity
    filtered.sort((a, b) {
      switch (_sortOrder) {
        case SortOrder.title:
          return _useKannadaAlphabet
              ? a.titleKn.compareTo(b.titleKn)
              : a.titleEn.compareTo(b.titleEn);
        case SortOrder.year:
          return b.year.compareTo(a.year);
        case SortOrder.popularity:
          return b.popularityScore.compareTo(a.popularityScore);
      }
    });

    return Column(
      children: [
        // Top Controls: Kannada (ಅ–ಳ) vs English (A–Z) Toggle + Sort Menu
        Padding(
          padding: const EdgeInsets.fromLTRB(14, 10, 14, 6),
          child: Row(
            children: [
              SegmentedButton<bool>(
                segments: const [
                  ButtonSegment(
                    value: true,
                    label: Text('ಕನ್ನಡ (ಅ–ಳ)'),
                  ),
                  ButtonSegment(
                    value: false,
                    label: Text('English (A–Z)'),
                  ),
                ],
                selected: {_useKannadaAlphabet},
                onSelectionChanged: (selection) {
                  setState(() {
                    _useKannadaAlphabet = selection.first;
                    _selectedLetter = null;
                  });
                },
              ),
              const Spacer(),
              DropdownButton<SortOrder>(
                value: _sortOrder,
                underline: const SizedBox.shrink(),
                icon: const Icon(Icons.sort, color: RaagaColors.mysoreGold),
                onChanged: (val) {
                  if (val != null) setState(() => _sortOrder = val);
                },
                items: [
                  DropdownMenuItem(
                    value: SortOrder.title,
                    child: Text(l10n.tr('sort_title')),
                  ),
                  DropdownMenuItem(
                    value: SortOrder.year,
                    child: Text(l10n.tr('sort_year')),
                  ),
                  DropdownMenuItem(
                    value: SortOrder.popularity,
                    child: Text(l10n.tr('sort_popularity')),
                  ),
                ],
              ),
            ],
          ),
        ),

        // Browse Dimension Tabs: Songs, Artists, Movies, Albums
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            children: [
              _dimensionChip(BrowseDimension.songs, l10n.tr('browse_songs')),
              _dimensionChip(BrowseDimension.artists, l10n.tr('browse_artists')),
              _dimensionChip(BrowseDimension.movies, l10n.tr('browse_movies')),
              _dimensionChip(BrowseDimension.albums, l10n.tr('browse_albums')),
            ],
          ),
        ),

        const SizedBox(height: 6),

        // Horizontal Varnamale / A-Z Index Bar
        SizedBox(
          height: 44,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: _activeAlphabet.length + 1,
            itemBuilder: (context, idx) {
              if (idx == 0) {
                final isAll = _selectedLetter == null;
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  child: ActionChip(
                    backgroundColor: isAll ? RaagaColors.maroonPrimary : null,
                    label: Text(
                      'All (${baseSongs.length})',
                      style: TextStyle(
                        color: isAll ? RaagaColors.mysoreGold : null,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    onPressed: () => setState(() => _selectedLetter = null),
                  ),
                );
              }
              final letter = _activeAlphabet[idx - 1];
              final isSelected = _selectedLetter == letter;
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 3),
                child: ActionChip(
                  backgroundColor: isSelected ? RaagaColors.maroonPrimary : null,
                  label: Text(
                    letter,
                    style: TextStyle(
                      color: isSelected ? RaagaColors.mysoreGold : null,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  onPressed: () => setState(
                    () => _selectedLetter = isSelected ? null : letter,
                  ),
                ),
              );
            },
          ),
        ),

        const Divider(height: 12),

        // Main Songs List + Right-Side Fast Scrubber
        Expanded(
          child: Row(
            children: [
              Expanded(
                child: filtered.isEmpty
                    ? Center(
                        child: Text(
                          'No Kannada tracks starting with "$_selectedLetter" yet.',
                          style: const TextStyle(color: Colors.white60),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.only(bottom: 100),
                        itemCount: filtered.length,
                        itemBuilder: (context, idx) {
                          final song = filtered[idx];
                          return SongTile(
                            song: song,
                            isPlaying:
                                widget.audioController.currentSong?.id == song.id,
                            isFavorite: widget.authService.isFavorite(song.id),
                            downloadTask: widget.downloadManager.getTask(song.id),
                            onTap: () {
                              widget.audioController
                                  .playSong(song, newQueue: filtered);
                              widget.authService.recordListeningHistory(song);
                            },
                            onFavoriteToggle: () =>
                                widget.authService.toggleFavorite(song.id),
                            onDownloadTap: () =>
                                widget.downloadManager.startDownload(song),
                          );
                        },
                      ),
              ),

              // Side Alphabet Fast-Scrubber
              Container(
                width: 28,
                margin: const EdgeInsets.only(right: 4, bottom: 80),
                decoration: BoxDecoration(
                  color: RaagaColors.maroonPrimary.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: ListView.builder(
                  itemCount: _activeAlphabet.length,
                  itemBuilder: (context, idx) {
                    final letter = _activeAlphabet[idx];
                    final active = _selectedLetter == letter;
                    return InkWell(
                      onTap: () => setState(() => _selectedLetter = letter),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Center(
                          child: Text(
                            letter,
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight:
                                  active ? FontWeight.bold : FontWeight.normal,
                              color: active
                                  ? RaagaColors.saffronAccent
                                  : RaagaColors.mysoreGold,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _dimensionChip(BrowseDimension dim, String label) {
    final selected = _dimension == dim;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => setState(() {
          _dimension = dim;
          if (dim != BrowseDimension.songs) {
            _useKannadaAlphabet = false;
          }
          _selectedLetter = null;
        }),
      ),
    );
  }
}
