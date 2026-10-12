import 'package:flutter/material.dart';
import '../../core/l10n/app_localizations.dart';
import '../../core/theme/raaga_theme.dart';
import '../../domain/models/song.dart';
import '../../services/audio/raaga_audio_handler.dart';
import '../../services/auth/auth_sync_service.dart';
import '../../services/offline/encrypted_download_manager.dart';
import 'browse/az_browse_screen.dart';
import 'downloads/downloads_screen.dart';
import 'home/home_screen.dart';
import 'library/library_screen.dart';
import 'player/full_player_screen.dart';
import 'search/search_screen.dart';

class MainShellScreen extends StatefulWidget {
  final Locale locale;
  final bool isDarkMode;
  final VoidCallback onToggleLanguage;
  final VoidCallback onToggleTheme;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const MainShellScreen({
    super.key,
    required this.locale,
    required this.isDarkMode,
    required this.onToggleLanguage,
    required this.onToggleTheme,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  State<MainShellScreen> createState() => _MainShellScreenState();
}

class _MainShellScreenState extends State<MainShellScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final l10n = RaagaLocalizations(widget.locale);

    return AnimatedBuilder(
      animation: Listenable.merge([
        widget.audioController,
        widget.downloadManager,
        widget.authService,
      ]),
      builder: (context, _) {
        final screens = [
          HomeScreen(
            l10n: l10n,
            catalog: widget.catalog,
            audioController: widget.audioController,
            downloadManager: widget.downloadManager,
            authService: widget.authService,
          ),
          AzBrowseScreen(
            l10n: l10n,
            catalog: widget.catalog,
            audioController: widget.audioController,
            downloadManager: widget.downloadManager,
            authService: widget.authService,
          ),
          SearchScreen(
            l10n: l10n,
            catalog: widget.catalog,
            audioController: widget.audioController,
            downloadManager: widget.downloadManager,
            authService: widget.authService,
          ),
          LibraryScreen(
            l10n: l10n,
            catalog: widget.catalog,
            audioController: widget.audioController,
            downloadManager: widget.downloadManager,
            authService: widget.authService,
            isDarkMode: widget.isDarkMode,
            onToggleTheme: widget.onToggleTheme,
            onToggleLanguage: widget.onToggleLanguage,
          ),
          DownloadsScreen(
            l10n: l10n,
            catalog: widget.catalog,
            audioController: widget.audioController,
            downloadManager: widget.downloadManager,
            authService: widget.authService,
          ),
        ];

        final currentSong = widget.audioController.currentSong;

        return Scaffold(
          appBar: AppBar(
            title: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: RaagaColors.maroonPrimary,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: RaagaColors.mysoreGold),
                  ),
                  child: const Text(
                    'ರಾ',
                    style: TextStyle(
                      color: RaagaColors.mysoreGold,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.tr('app_title'),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                    Text(
                      l10n.tr('app_subtitle'),
                      style: const TextStyle(
                        fontSize: 11,
                        color: RaagaColors.mysoreGold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            actions: [
              // Quick Offline Mode Switch
              FilterChip(
                label: Text(
                  widget.downloadManager.offlineModeEnabled
                      ? 'Offline'
                      : 'Online',
                  style: const TextStyle(fontSize: 11.5),
                ),
                avatar: Icon(
                  widget.downloadManager.offlineModeEnabled
                      ? Icons.cloud_off
                      : Icons.wifi,
                  size: 15,
                  color: RaagaColors.mysoreGold,
                ),
                selected: widget.downloadManager.offlineModeEnabled,
                onSelected: (val) {
                  widget.downloadManager.setOfflineMode(val);
                  widget.audioController.onConnectivityChanged(!val);
                },
              ),
              const SizedBox(width: 6),
              // Quick Language Switch (ಕನ್ನಡ / EN)
              TextButton(
                onPressed: widget.onToggleLanguage,
                child: Text(
                  l10n.isKannada ? 'EN' : 'ಕನ್ನಡ',
                  style: const TextStyle(
                    color: RaagaColors.mysoreGold,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          body: Column(
            children: [
              if (widget.downloadManager.offlineModeEnabled)
                Container(
                  width: double.infinity,
                  color: RaagaColors.maroonPrimary,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  child: Row(
                    children: [
                      const Icon(Icons.offline_pin,
                          color: RaagaColors.mysoreGold, size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          l10n.tr('offline_banner'),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              Expanded(child: screens[_selectedIndex]),
            ],
          ),
          bottomSheet: currentSong == null
              ? null
              : _buildMiniPlayer(context, currentSong),
          bottomNavigationBar: BottomNavigationBar(
            currentIndex: _selectedIndex,
            onTap: (index) => setState(() => _selectedIndex = index),
            items: [
              BottomNavigationBarItem(
                icon: const Icon(Icons.home_outlined),
                activeIcon: const Icon(Icons.home),
                label: l10n.tr('nav_home'),
              ),
              BottomNavigationBarItem(
                icon: const Icon(Icons.sort_by_alpha),
                activeIcon: const Icon(Icons.sort_by_alpha),
                label: l10n.tr('nav_browse'),
              ),
              BottomNavigationBarItem(
                icon: const Icon(Icons.search),
                activeIcon: const Icon(Icons.search),
                label: l10n.tr('nav_search'),
              ),
              BottomNavigationBarItem(
                icon: const Icon(Icons.library_music_outlined),
                activeIcon: const Icon(Icons.library_music),
                label: l10n.tr('nav_library'),
              ),
              BottomNavigationBarItem(
                icon: const Icon(Icons.download_for_offline_outlined),
                activeIcon: const Icon(Icons.download_for_offline),
                label: l10n.tr('nav_downloads'),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMiniPlayer(BuildContext context, Song currentSong) {
    final progress = widget.audioController.duration.inSeconds > 0
        ? widget.audioController.position.inSeconds /
            widget.audioController.duration.inSeconds
        : 0.0;

    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => FullPlayerScreen(
              audioController: widget.audioController,
              downloadManager: widget.downloadManager,
              authService: widget.authService,
            ),
          ),
        );
      },
      child: Container(
        height: 68,
        decoration: BoxDecoration(
          color: RaagaColors.maroonDark,
          border: const Border(
            top: BorderSide(color: RaagaColors.mysoreGold, width: 1),
          ),
        ),
        child: Column(
          children: [
            LinearProgressIndicator(
              value: progress.clamp(0.0, 1.0),
              minHeight: 2.5,
              backgroundColor: Colors.white12,
              color: RaagaColors.saffronAccent,
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Row(
                  children: [
                    const Icon(Icons.music_note, color: RaagaColors.mysoreGold),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            currentSong.titleKn,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: RaagaColors.mysoreGold,
                              fontWeight: FontWeight.bold,
                              fontSize: 13.5,
                            ),
                          ),
                          Text(
                            '${currentSong.titleEn} • ${currentSong.singer}',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 11.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.skip_previous,
                          color: Colors.white),
                      onPressed: widget.audioController.skipToPrevious,
                    ),
                    IconButton(
                      icon: Icon(
                        widget.audioController.isPlaying
                            ? Icons.pause_circle_filled
                            : Icons.play_circle_fill,
                        color: RaagaColors.mysoreGold,
                        size: 32,
                      ),
                      onPressed: widget.audioController.togglePlayPause,
                    ),
                    IconButton(
                      icon: const Icon(Icons.skip_next, color: Colors.white),
                      onPressed: widget.audioController.skipToNext,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
