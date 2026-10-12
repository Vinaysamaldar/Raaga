import 'package:flutter/material.dart';
import '../../../core/theme/raaga_theme.dart';
import '../../../services/audio/raaga_audio_handler.dart';
import '../../../services/auth/auth_sync_service.dart';
import '../../../services/offline/encrypted_download_manager.dart';

class FullPlayerScreen extends StatefulWidget {
  final RaagaAudioController audioController;
  final EncryptedDownloadManager downloadManager;
  final AuthAndLibrarySyncService authService;

  const FullPlayerScreen({
    super.key,
    required this.audioController,
    required this.downloadManager,
    required this.authService,
  });

  @override
  State<FullPlayerScreen> createState() => _FullPlayerScreenState();
}

class _FullPlayerScreenState extends State<FullPlayerScreen> {
  bool _showTransliteration = true;

  String _formatDuration(Duration d) {
    final m = d.inMinutes;
    final s = (d.inSeconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([
        widget.audioController,
        widget.downloadManager,
        widget.authService,
      ]),
      builder: (context, _) {
        final song = widget.audioController.currentSong;
        if (song == null) {
          return const Scaffold(
            body: Center(child: Text('No song selected')),
          );
        }

        final pos = widget.audioController.position;
        final dur = widget.audioController.duration;
        final activeLyricIdx = widget.audioController.activeLyricIndex;

        return Scaffold(
          appBar: AppBar(
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  song.category.labelKn,
                  style: const TextStyle(
                    fontSize: 13,
                    color: RaagaColors.mysoreGold,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${song.movieOrAlbum} (${song.year}) • ${song.labelName}',
                  style: const TextStyle(fontSize: 11.5),
                ),
              ],
            ),
            actions: [
              // Bluetooth / CarPlay / Lock-Screen Active Indicator
              IconButton(
                icon: const Icon(Icons.directions_car_filled_outlined,
                    color: RaagaColors.mysoreGold),
                tooltip: 'Android Auto / CarPlay & Bluetooth AVRCP Ready',
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'MediaSession active: Lock-screen, Notification, Bluetooth AVRCP & CarPlay/Android Auto controls enabled.',
                      ),
                    ),
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.queue_music),
                tooltip: 'Up Next Queue',
                onPressed: () => _showQueueModal(context),
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            children: [
              // Cover Art & Metadata Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(20),
                  gradient: const LinearGradient(
                    colors: [RaagaColors.maroonPrimary, RaagaColors.maroonDark],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  border: Border.all(
                    color: RaagaColors.mysoreGold.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.black38,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'Language: ${song.language} • ISRC: ${song.isrcCode}',
                            style: const TextStyle(
                              fontSize: 10.5,
                              color: RaagaColors.mysoreGold,
                            ),
                          ),
                        ),
                        if (widget.audioController.usingOfflineFallback ||
                            widget.downloadManager.isSongDownloaded(song.id))
                          const Row(
                            children: [
                              Icon(Icons.offline_pin,
                                  color: RaagaColors.mysoreGold, size: 16),
                              SizedBox(width: 4),
                              Text(
                                'AES-256 Offline Ready',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: RaagaColors.mysoreGold,
                                ),
                              ),
                            ],
                          ),
                      ],
                    ),
                    const SizedBox(height: 18),
                    Text(
                      song.titleKn,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: RaagaColors.mysoreGold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      song.titleEn,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 15,
                        color: Colors.white,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'ಹಾಡಿದವರು (Singer): ${song.singer}\nಸಂಗೀತ (Composer): ${song.composer} • ಸಾಹಿತ್ಯ (Lyricist): ${song.lyricist}',
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.white70,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Seek Bar & Time Indicators
              Slider(
                value: pos.inSeconds.toDouble().clamp(0, dur.inSeconds.toDouble()),
                max: dur.inSeconds.toDouble(),
                onChanged: (v) =>
                    widget.audioController.seekTo(Duration(seconds: v.toInt())),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(_formatDuration(pos),
                        style: const TextStyle(fontSize: 12)),
                    Text(
                      widget.audioController.quality.label,
                      style: const TextStyle(
                        fontSize: 11,
                        color: RaagaColors.mysoreGold,
                      ),
                    ),
                    Text(_formatDuration(dur),
                        style: const TextStyle(fontSize: 12)),
                  ],
                ),
              ),

              const SizedBox(height: 10),

              // Primary Transport Controls (Shuffle, Previous, Play/Pause, Next, Repeat)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.shuffle,
                      color: widget.audioController.isShuffle
                          ? RaagaColors.saffronAccent
                          : null,
                    ),
                    onPressed: widget.audioController.toggleShuffle,
                  ),
                  IconButton(
                    iconSize: 34,
                    icon: const Icon(Icons.skip_previous),
                    onPressed: widget.audioController.skipToPrevious,
                  ),
                  FloatingActionButton(
                    backgroundColor: RaagaColors.mysoreGold,
                    foregroundColor: RaagaColors.maroonDark,
                    onPressed: widget.audioController.togglePlayPause,
                    child: Icon(
                      widget.audioController.isPlaying
                          ? Icons.pause
                          : Icons.play_arrow,
                      size: 32,
                    ),
                  ),
                  IconButton(
                    iconSize: 34,
                    icon: const Icon(Icons.skip_next),
                    onPressed: widget.audioController.skipToNext,
                  ),
                  IconButton(
                    icon: Icon(
                      widget.audioController.repeatMode ==
                              RepeatModeState.repeatOne
                          ? Icons.repeat_one
                          : Icons.repeat,
                      color: widget.audioController.repeatMode !=
                              RepeatModeState.off
                          ? RaagaColors.saffronAccent
                          : null,
                    ),
                    onPressed: widget.audioController.cycleRepeatMode,
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Secondary Utility Row: Equalizer, Sleep Timer, Favorite, Download
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  TextButton.icon(
                    onPressed: () => _showEqualizerModal(context),
                    icon: const Icon(Icons.tune, size: 18),
                    label: const Text('Equalizer'),
                  ),
                  TextButton.icon(
                    onPressed: () => _showSleepTimerModal(context),
                    icon: const Icon(Icons.bedtime_outlined, size: 18),
                    label: Text(
                      widget.audioController.sleepTimerRemaining == null
                          ? 'Sleep Timer'
                          : _formatDuration(
                              widget.audioController.sleepTimerRemaining!),
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      widget.authService.isFavorite(song.id)
                          ? Icons.favorite
                          : Icons.favorite_border,
                      color: RaagaColors.saffronAccent,
                    ),
                    onPressed: () =>
                        widget.authService.toggleFavorite(song.id),
                  ),
                  IconButton(
                    icon: Icon(
                      widget.downloadManager.isSongDownloaded(song.id)
                          ? Icons.offline_pin
                          : Icons.download_for_offline_outlined,
                      color: RaagaColors.mysoreGold,
                    ),
                    onPressed: () =>
                        widget.downloadManager.startDownload(song),
                  ),
                ],
              ),

              const Divider(height: 22),

              // Time-Synced Lyrics Card (Kannada Script + English Transliteration)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'ಸಾಹಿತ್ಯ • Synced Lyrics (ಕನ್ನಡ + English)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  FilterChip(
                    label: const Text('Transliteration'),
                    selected: _showTransliteration,
                    onSelected: (v) =>
                        setState(() => _showTransliteration = v),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ...List.generate(song.syncedLyrics.length, (idx) {
                final line = song.syncedLyrics[idx];
                final isCurrent = idx == activeLyricIdx;
                return InkWell(
                  onTap: () => widget.audioController.seekTo(line.timestamp),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 250),
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isCurrent
                          ? RaagaColors.maroonPrimary.withOpacity(0.55)
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(12),
                      border: isCurrent
                          ? Border.all(color: RaagaColors.mysoreGold)
                          : null,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          line.kannadaLine,
                          style: TextStyle(
                            fontSize: isCurrent ? 16.5 : 14.5,
                            fontWeight:
                                isCurrent ? FontWeight.bold : FontWeight.w500,
                            color: isCurrent ? RaagaColors.mysoreGold : null,
                          ),
                        ),
                        if (_showTransliteration) ...[
                          const SizedBox(height: 3),
                          Text(
                            line.englishTransliteration,
                            style: TextStyle(
                              fontSize: 12.5,
                              color: isCurrent
                                  ? Colors.white
                                  : Colors.white60,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              }),
            ],
          ),
        );
      },
    );
  }

  void _showEqualizerModal(BuildContext context) {
    final bands = ['60 Hz', '230 Hz', '910 Hz', '3.6 kHz', '14 kHz'];
    showModalBottomSheet(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            return Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '5-Band Kannada Acoustic Equalizer & Presets',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 6,
                    children: EqualizerPreset.presets.map((preset) {
                      final selected =
                          widget.audioController.activePreset.id == preset.id;
                      return ChoiceChip(
                        label: Text(preset.nameEn),
                        selected: selected,
                        onSelected: (_) {
                          widget.audioController.setEqualizerPreset(preset);
                          setModalState(() {});
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 12),
                  ...List.generate(5, (i) {
                    final gain = widget.audioController.customBands[i];
                    return Row(
                      children: [
                        SizedBox(width: 58, child: Text(bands[i])),
                        Expanded(
                          child: Slider(
                            value: gain,
                            min: -10,
                            max: 10,
                            onChanged: (v) {
                              widget.audioController.updateEqualizerBand(i, v);
                              setModalState(() {});
                            },
                          ),
                        ),
                        SizedBox(
                          width: 48,
                          child: Text('${gain.toStringAsFixed(1)} dB'),
                        ),
                      ],
                    );
                  }),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _showSleepTimerModal(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'ಸ್ಲೀಪ್ ಟೈಮರ್ • Sleep Timer',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            ListTile(
              title: const Text('15 Minutes'),
              onTap: () {
                widget.audioController
                    .setSleepTimer(const Duration(minutes: 15));
                Navigator.pop(ctx);
              },
            ),
            ListTile(
              title: const Text('30 Minutes'),
              onTap: () {
                widget.audioController
                    .setSleepTimer(const Duration(minutes: 30));
                Navigator.pop(ctx);
              },
            ),
            ListTile(
              title: const Text('60 Minutes'),
              onTap: () {
                widget.audioController
                    .setSleepTimer(const Duration(minutes: 60));
                Navigator.pop(ctx);
              },
            ),
            ListTile(
              title: const Text('Turn Off Sleep Timer'),
              onTap: () {
                widget.audioController.setSleepTimer(null);
                Navigator.pop(ctx);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showQueueModal(BuildContext context) {
    final queue = widget.audioController.queue;
    showModalBottomSheet(
      context: context,
      builder: (ctx) => ListView.builder(
        padding: const EdgeInsets.all(14),
        itemCount: queue.length,
        itemBuilder: (ctx, idx) {
          final item = queue[idx];
          final active = idx == widget.audioController.currentIndex;
          return ListTile(
            leading: Icon(
              active ? Icons.play_circle_fill : Icons.music_note,
              color: active ? RaagaColors.mysoreGold : null,
            ),
            title: Text(item.titleKn),
            subtitle: Text(item.titleEn),
            onTap: () {
              widget.audioController.playSong(item, newQueue: queue);
              Navigator.pop(ctx);
            },
          );
        },
      ),
    );
  }
}
