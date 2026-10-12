import 'package:flutter/material.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../domain/models/song.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';
import '../../../services/search/kannada_search_engine.dart';
import '../../widgets/song_tile.dart';

class SearchScreen extends StatefulWidget {
  final RaagaLocalizations l10n;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const SearchScreen({
    super.key,
    required this.l10n,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _controller = TextEditingController();
  String _query = '';
  bool _isListeningVoice = false;

  static const List<String> _sampleVoiceQueries = [
    'ಹುಟ್ಟಿದರೆ ಕನ್ನಡ ನಾಡಲ್ಲಿ',
    'Mungaru Maleye',
    'Varaha Roopam',
    'ಜಗದೋದ್ಧಾರನ',
    'Bombe Helutaite',
  ];

  void _startSimulatedVoiceSearch() async {
    setState(() => _isListeningVoice = true);
    await Future.delayed(const Duration(milliseconds: 900));
    if (!mounted) return;
    final sample = _sampleVoiceQueries[
        DateTime.now().second % _sampleVoiceQueries.length];
    setState(() {
      _isListeningVoice = false;
      _controller.text = sample;
      _query = sample;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final baseCatalog = widget.downloadManager.offlineModeEnabled
        ? widget.catalog
            .where((s) => widget.downloadManager.isSongDownloaded(s.id))
            .toList()
        : widget.catalog;

    final results = KannadaSearchEngine.search(
      catalog: baseCatalog,
      query: _query,
    );

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(14),
          child: TextField(
            controller: _controller,
            onChanged: (val) => setState(() => _query = val),
            decoration: InputDecoration(
              hintText: l10n.tr('search_hint'),
              prefixIcon: const Icon(Icons.search, color: RaagaColors.mysoreGold),
              suffixIcon: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (_query.isNotEmpty)
                    IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _controller.clear();
                        setState(() => _query = '');
                      },
                    ),
                  IconButton(
                    icon: Icon(
                      _isListeningVoice ? Icons.mic : Icons.mic_none,
                      color: _isListeningVoice
                          ? RaagaColors.saffronAccent
                          : RaagaColors.mysoreGold,
                    ),
                    tooltip: l10n.tr('voice_search'),
                    onPressed: _startSimulatedVoiceSearch,
                  ),
                ],
              ),
              filled: true,
              fillColor: Theme.of(context).cardTheme.color,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(14),
                borderSide: BorderSide(
                  color: RaagaColors.mysoreGold.withOpacity(0.35),
                ),
              ),
            ),
          ),
        ),

        // Quick Kannada Script & Transliteration Search Suggestions
        SizedBox(
          height: 38,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            children: [
              _quickQueryChip('ಡಾ. ರಾಜ್‌ಕುಮಾರ್ (Rajkumar)'),
              _quickQueryChip('ಕುವೆಂಪು (Kuvempu)'),
              _quickQueryChip('Mungaru Male (Typo: Mungru)'),
              _quickQueryChip('ಪುರಂದರದಾಸ (Purandaradasa)'),
              _quickQueryChip('Kantara'),
            ],
          ),
        ),

        const SizedBox(height: 8),

        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.only(bottom: 100),
            itemCount: results.length,
            itemBuilder: (context, idx) {
              final song = results[idx];
              return SongTile(
                song: song,
                isPlaying: widget.audioController.currentSong?.id == song.id,
                isFavorite: widget.authService.isFavorite(song.id),
                downloadTask: widget.downloadManager.getTask(song.id),
                onTap: () {
                  widget.audioController.playSong(song, newQueue: results);
                  widget.authService.recordListeningHistory(song);
                },
                onFavoriteToggle: () =>
                    widget.authService.toggleFavorite(song.id),
                onDownloadTap: () => widget.downloadManager.startDownload(song),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _quickQueryChip(String label) {
    final searchTerm = label.split(' ').first;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: ActionChip(
        label: Text(label, style: const TextStyle(fontSize: 12)),
        onPressed: () {
          _controller.text = searchTerm;
          setState(() => _query = searchTerm);
        },
      ),
    );
  }
}
