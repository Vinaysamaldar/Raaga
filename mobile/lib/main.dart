import 'package:flutter/material.dart';
import 'core/theme/raaga_theme.dart';
import 'data/catalog/sample_kannada_catalog.dart';
import 'presentation/screens/main_shell.dart';
import 'services/audio/raaga_audio_handler.dart';
import 'services/auth/auth_sync_service.dart';
import 'services/offline/encrypted_download_manager.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const RaagaKannadaApp());
}

class RaagaKannadaApp extends StatefulWidget {
  const RaagaKannadaApp({super.key});

  @override
  State<RaagaKannadaApp> createState() => _RaagaKannadaAppState();
}

class _RaagaKannadaAppState extends State<RaagaKannadaApp> {
  Locale _locale = const Locale('en'); // Default to English font & UI, switchable to Kannada
  bool _isDarkMode = true;

  late final EncryptedDownloadManager _downloadManager;
  late final RaagaAudioController _audioController;
  late final AuthAndLibrarySyncService _authService;

  @override
  void initState() {
    super.initState();
    final catalog = SampleKannadaCatalog.songs;
    _downloadManager = EncryptedDownloadManager(
      preloadedOfflineSongs: catalog,
    );
    _audioController = RaagaAudioController(
      isSongDownloaded: _downloadManager.isSongDownloaded,
    );
    _authService = AuthAndLibrarySyncService();

    // Pre-load the first iconic Kannada song into the player queue
    if (catalog.isNotEmpty) {
      _audioController.playSong(catalog.first, newQueue: catalog);
      _audioController.togglePlayPause(); // Start paused until user taps play
    }
  }

  void _toggleLanguage() {
    setState(() {
      _locale = _locale.languageCode == 'kn'
          ? const Locale('en')
          : const Locale('kn');
    });
  }

  void _toggleTheme() {
    setState(() {
      _isDarkMode = !_isDarkMode;
    });
  }

  @override
  void dispose() {
    _audioController.dispose();
    _downloadManager.dispose();
    _authService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Raaga - Exclusive Kannada Music',
      debugShowCheckedModeBanner: false,
      theme: RaagaTheme.lightTheme,
      darkTheme: RaagaTheme.darkTheme,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      locale: _locale,
      home: MainShellScreen(
        locale: _locale,
        isDarkMode: _isDarkMode,
        onToggleLanguage: _toggleLanguage,
        onToggleTheme: _toggleTheme,
        catalog: SampleKannadaCatalog.songs,
        audioController: _audioController,
        downloadManager: _downloadManager,
        authService: _authService,
      ),
    );
  }
}
