import 'package:flutter/material.dart';
import '../../../core/l10n/app_localizations.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../domain/models/song.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';
import '../../widgets/song_tile.dart';

class DownloadsScreen extends StatelessWidget {
  final RaagaLocalizations l10n;
  final List<Song> catalog;
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const DownloadsScreen({
    super.key,
    required this.l10n,
    required this.catalog,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  Widget build(BuildContext context) {
    final completed = downloadManager.completedDownloads;
    final active = downloadManager.activeDownloads;
    final storageMb = downloadManager.totalStorageUsedMb;

    return ListView(
      padding: const EdgeInsets.only(bottom: 110),
      children: [
        // Offline Mode & Wi-Fi Only Control Card
        Card(
          margin: const EdgeInsets.all(14),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    l10n.tr('offline_mode'),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: const Text(
                    'Show only AES-256 encrypted downloaded songs & auto-fallback on network drop',
                    style: TextStyle(fontSize: 12),
                  ),
                  activeColor: RaagaColors.mysoreGold,
                  value: downloadManager.offlineModeEnabled,
                  onChanged: downloadManager.setOfflineMode,
                ),
                const Divider(),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    l10n.tr('wifi_only'),
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: const Text(
                    'Pause downloads automatically on mobile data to save bandwidth',
                    style: TextStyle(fontSize: 12),
                  ),
                  activeColor: RaagaColors.mysoreGold,
                  value: downloadManager.wifiOnly,
                  onChanged: downloadManager.setWifiOnly,
                ),
                const Divider(),
                Row(
                  children: [
                    const Icon(Icons.lock_outline,
                        color: RaagaColors.mysoreGold, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Encrypted Vault Storage: ${storageMb.toStringAsFixed(1)} MB (${completed.length} tracks • AES-256-CBC App-Only Playback)',
                        style: const TextStyle(
                          fontSize: 12.5,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: () =>
                          downloadManager.downloadPlaylistOrAlbum(catalog),
                      child: const Text('Download All'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),

        // Active / Paused Downloads Queue
        if (active.isNotEmpty) ...[
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Text(
              'Active Download Queue',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          ...active.map((task) {
            final isPaused = task.status == DownloadStatus.paused;
            return Card(
              margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
              child: ListTile(
                title: Text(task.song.titleKn),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 6),
                    LinearProgressIndicator(
                      value: task.progress,
                      color: RaagaColors.saffronAccent,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${(task.progress * 100).toInt()}% • Encrypting AES-256...',
                      style: const TextStyle(fontSize: 11.5),
                    ),
                  ],
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: Icon(isPaused ? Icons.play_arrow : Icons.pause),
                      onPressed: () => isPaused
                          ? downloadManager.resumeDownload(task.song.id)
                          : downloadManager.pauseDownload(task.song.id),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: () =>
                          downloadManager.removeDownload(task.song.id),
                    ),
                  ],
                ),
              ),
            );
          }),
          const SizedBox(height: 12),
        ],

        // Completed Offline Songs
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Downloaded Kannada Songs (${completed.length})',
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (completed.isNotEmpty)
                ElevatedButton.icon(
                  onPressed: () {
                    final offlineSongs =
                        completed.map((t) => t.song).toList();
                    audioController.playSong(
                      offlineSongs.first,
                      newQueue: offlineSongs,
                    );
                  },
                  icon: const Icon(Icons.play_arrow, size: 18),
                  label: const Text('Play Offline Queue'),
                ),
            ],
          ),
        ),

        ...completed.map((task) {
          final song = task.song;
          return SongTile(
            song: song,
            isPlaying: audioController.currentSong?.id == song.id,
            isFavorite: authService.isFavorite(song.id),
            downloadTask: task,
            onTap: () {
              final offlineQueue = completed.map((e) => e.song).toList();
              audioController.playSong(song, newQueue: offlineQueue);
              authService.recordListeningHistory(song);
            },
            onFavoriteToggle: () => authService.toggleFavorite(song.id),
            onDownloadTap: () => downloadManager.removeDownload(song.id),
          );
        }),
      ],
    );
  }
}
