import 'package:flutter/material.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../domain/models/song.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';
import '../../widgets/song_tile.dart';
import '../legal/legal_screen.dart';

class LibraryScreen extends StatelessWidget {
  final RaagaLocalizations l10n;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;
  final bool isDarkMode;
  final VoidCallback onToggleTheme;
  final VoidCallback onToggleLanguage;

  const LibraryScreen({
    super.key,
    required this.l10n,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
    required this.isDarkMode,
    required this.onToggleTheme,
    required this.onToggleLanguage,
  });

  @override
  Widget build(BuildContext context) {
    final user = authService.currentUser;
    final favoriteSongs = catalog
        .where((s) => authService.favoriteSongIds.contains(s.id))
        .toList();

    return ListView(
      padding: const EdgeInsets.only(bottom: 110),
      children: [
        // User Cloud Sync & Sign-In Card (Phone OTP / Google)
        Card(
          margin: const EdgeInsets.all(14),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: RaagaColors.maroonPrimary,
                      child: Icon(Icons.person, color: RaagaColors.mysoreGold),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            user?.displayName ?? 'Guest User',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          Text(
                            'Synced via ${user?.authMethod == 'google' ? 'Google Account' : 'Phone OTP'} • Favorites, Playlists & History synced across devices',
                            style: const TextStyle(fontSize: 11.5),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () =>
                          authService.signInWithPhoneOtp('+91 99001 12233', '482910'),
                      icon: const Icon(Icons.phone_android, size: 16),
                      label: const Text('Phone OTP Sign-In'),
                    ),
                    OutlinedButton.icon(
                      onPressed: authService.signInWithGoogle,
                      icon: const Icon(Icons.cloud_done_outlined, size: 16),
                      label: const Text('Google Sync'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),

        // App Preferences: Language (ಕನ್ನಡ / English), Theme (Light / Dark), Adaptive Bitrate
        Card(
          margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.translate, color: RaagaColors.mysoreGold),
                title: const Text('App Interface Language / ಭಾಷೆ'),
                subtitle: Text(
                  l10n.isKannada ? 'ಪ್ರಸ್ತುತ: ಕನ್ನಡ (Kannada)' : 'Current: English (Switch to ಕನ್ನಡ)',
                ),
                trailing: ElevatedButton(
                  onPressed: onToggleLanguage,
                  child: Text(l10n.isKannada ? 'English' : 'ಕನ್ನಡ'),
                ),
              ),
              const Divider(height: 1),
              SwitchListTile(
                secondary: const Icon(Icons.palette_outlined,
                    color: RaagaColors.mysoreGold),
                title: const Text('Dark Mode (Karnataka Maroon & Gold)'),
                subtitle: const Text('Switch between Dark OLED and Mysuru Silk Light Theme'),
                value: isDarkMode,
                onChanged: (_) => onToggleTheme(),
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.high_quality,
                    color: RaagaColors.mysoreGold),
                title: Text(l10n.tr('streaming_quality')),
                subtitle: Text(audioController.quality.label),
                trailing: DropdownButton<StreamingQuality>(
                  value: audioController.quality,
                  underline: const SizedBox.shrink(),
                  onChanged: (q) {
                    if (q != null) audioController.setStreamingQuality(q);
                  },
                  items: StreamingQuality.values
                      .map(
                        (q) => DropdownMenuItem(
                          value: q,
                          child: Text(q.name.toUpperCase()),
                        ),
                      )
                      .toList(),
                ),
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.verified_user_outlined,
                    color: RaagaColors.mysoreGold),
                title: Text(l10n.tr('legal_licensing')),
                subtitle: const Text(
                  'Anand Audio • Lahari Music • Saregama • Aditya Music • PRK • DMCA Takedown',
                  style: TextStyle(fontSize: 11.5),
                ),
                trailing: const Icon(Icons.chevron_right),
                onTap: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const LegalAndLicensingScreen()),
                  );
                },
              ),
            ],
          ),
        ),

        const SizedBox(height: 14),

        // Custom Playlists (Online + Offline)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            l10n.tr('playlists'),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
        ),
        ...authService.playlists.map(
          (pl) => Card(
            margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
            child: ListTile(
              leading: const Icon(Icons.queue_music, color: RaagaColors.mysoreGold),
              title: Text(pl.nameKn, style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('${pl.nameEn} • ${pl.songIds.length} songs'),
              trailing: IconButton(
                icon: const Icon(Icons.download_for_offline_outlined),
                tooltip: 'Download Playlist Offline',
                onPressed: () {
                  final songs = catalog
                      .where((s) => pl.songIds.contains(s.id))
                      .toList();
                  downloadManager.downloadPlaylistOrAlbum(songs);
                },
              ),
              onTap: () {
                final songs = catalog
                    .where((s) => pl.songIds.contains(s.id))
                    .toList();
                if (songs.isNotEmpty) {
                  audioController.playSong(songs.first, newQueue: songs);
                }
              },
            ),
          ),
        ),

        const SizedBox(height: 14),

        // Synced & Offline Favorites
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            '${l10n.tr('favorites')} (${favoriteSongs.length})',
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
        ),
        ...favoriteSongs.map(
          (song) => SongTile(
            song: song,
            isPlaying: audioController.currentSong?.id == song.id,
            isFavorite: true,
            downloadTask: downloadManager.getTask(song.id),
            onTap: () =>
                audioController.playSong(song, newQueue: favoriteSongs),
            onFavoriteToggle: () => authService.toggleFavorite(song.id),
            onDownloadTap: () => downloadManager.startDownload(song),
          ),
        ),
      ],
    );
  }
}
