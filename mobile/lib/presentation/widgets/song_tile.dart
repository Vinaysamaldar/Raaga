import 'package:flutter/material.dart';
import '../../core/theme/raaga_theme.dart';
import '../../domain/models/song.dart';
import '../../services/offline/encrypted_download_manager.dart';

class SongTile extends StatelessWidget {
  final Song song;
  final bool isPlaying;
  final bool isFavorite;
  final DownloadTaskItem? downloadTask;
  final VoidCallback onTap;
  final VoidCallback onFavoriteToggle;
  final VoidCallback onDownloadTap;

  const SongTile({
    super.key,
    required this.song,
    required this.isPlaying,
    required this.isFavorite,
    this.downloadTask,
    required this.onTap,
    required this.onFavoriteToggle,
    required this.onDownloadTap,
  });

  @override
  Widget build(BuildContext context) {
    final status = downloadTask?.status ?? DownloadStatus.notDownloaded;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        leading: Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(10),
            gradient: const LinearGradient(
              colors: [RaagaColors.maroonPrimary, RaagaColors.maroonDark],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            border: Border.all(
              color: isPlaying ? RaagaColors.saffronAccent : RaagaColors.mysoreGold.withOpacity(0.4),
              width: isPlaying ? 2 : 1,
            ),
          ),
          alignment: Alignment.center,
          child: isPlaying
              ? const Icon(Icons.equalizer, color: RaagaColors.saffronAccent)
              : Text(
                  song.englishInitial,
                  style: const TextStyle(
                    color: RaagaColors.mysoreGold,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
        ),
        title: Row(
          children: [
            Expanded(
              child: Text(
                '${song.titleEn} • ${song.titleKn}',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 14.5,
                  color: isPlaying ? RaagaColors.mysoreGold : null,
                ),
              ),
            ),
            if (song.year == 2026)
              Container(
                margin: const EdgeInsets.only(left: 6),
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                decoration: BoxDecoration(
                  color: RaagaColors.mysoreGold,
                  borderRadius: BorderRadius.circular(5),
                ),
                child: const Text(
                  '2026',
                  style: TextStyle(
                    color: RaagaColors.maroonDark,
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${song.singer} • ${song.movieOrAlbum} (${song.year}) • ${song.labelName}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 2),
            Text(
              song.titleKn,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11.5,
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.75),
              ),
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(
                isPlaying ? Icons.pause_circle_filled : Icons.play_circle_fill,
                color: isPlaying ? RaagaColors.saffronAccent : RaagaColors.mysoreGold,
                size: 28,
              ),
              tooltip: isPlaying ? 'Pause' : 'Play',
              onPressed: onTap,
            ),
            IconButton(
              icon: Icon(
                isFavorite ? Icons.favorite : Icons.favorite_border,
                color: isFavorite ? RaagaColors.saffronAccent : null,
                size: 20,
              ),
              tooltip: 'Favorite',
              onPressed: onFavoriteToggle,
            ),
            _buildDownloadIcon(status, downloadTask?.progress ?? 0),
          ],
        ),
      ),
    );
  }

  Widget _buildDownloadIcon(DownloadStatus status, double progress) {
    switch (status) {
      case DownloadStatus.completed:
        return IconButton(
          icon: const Icon(
            Icons.offline_pin,
            color: RaagaColors.mysoreGold,
            size: 22,
          ),
          tooltip: 'Encrypted Offline Copy Ready (AES-256)',
          onPressed: onDownloadTap,
        );
      case DownloadStatus.downloading:
        return SizedBox(
          width: 36,
          height: 36,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CircularProgressIndicator(
                value: progress,
                strokeWidth: 2.5,
                color: RaagaColors.saffronAccent,
              ),
              IconButton(
                padding: EdgeInsets.zero,
                icon: const Icon(Icons.pause, size: 15),
                onPressed: onDownloadTap,
              ),
            ],
          ),
        );
      case DownloadStatus.paused:
      case DownloadStatus.queued:
        return IconButton(
          icon: const Icon(
            Icons.PauseCircleOutline,
            color: RaagaColors.warningAmber,
            size: 22,
          ),
          tooltip: 'Paused / Waiting for Wi-Fi',
          onPressed: onDownloadTap,
        );
      case DownloadStatus.notDownloaded:
      case DownloadStatus.failed:
        return IconButton(
          icon: const Icon(Icons.download_for_offline_outlined, size: 22),
          tooltip: 'Download Encrypted Offline Copy',
          onPressed: onDownloadTap,
        );
    }
  }
}
