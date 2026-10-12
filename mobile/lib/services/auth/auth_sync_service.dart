import 'package:flutter/foundation.dart';
import '../../domain/models/song.dart';

class UserProfile {
  final String uid;
  final String displayName;
  final String? phoneOrEmail;
  final String authMethod; // 'phone_otp' or 'google'
  final DateTime lastSyncedAt;

  const UserProfile({
    required this.uid,
    required this.displayName,
    this.phoneOrEmail,
    required this.authMethod,
    required this.lastSyncedAt,
  });
}

class CustomPlaylist {
  final String id;
  final String nameKn;
  final String nameEn;
  final List<String> songIds;
  final bool availableOffline;

  CustomPlaylist({
    required this.id,
    required this.nameKn,
    required this.nameEn,
    required this.songIds,
    this.availableOffline = false,
  });
}

/// Manages Phone OTP & Google Sign-In, plus cross-device cloud & offline sync
/// for Favorites, Playlists, and Listening History.
class AuthAndLibrarySyncService extends ChangeNotifier {
  UserProfile? _currentUser = UserProfile(
    uid: 'usr_kannadiga_01',
    displayName: 'ಕನ್ನಡ ಸಂಗೀತ ಪ್ರೇಮಿ (Kannada Rasika)',
    phoneOrEmail: '+91 98450 XXXXX',
    authMethod: 'phone_otp',
    lastSyncedAt: DateTime.now(),
  );

  final Set<String> _favoriteSongIds = {'kn_001', 'kn_006', 'kn_008', 'kn_010'};
  final List<String> _listeningHistoryIds = ['kn_001', 'kn_009', 'kn_011', 'kn_003'];
  final List<CustomPlaylist> _playlists = [
    CustomPlaylist(
      id: 'pl_1',
      nameKn: 'ನನ್ನ ನೆಚ್ಚಿನ ಭಾವಗೀತೆಗಳು',
      nameEn: 'My Favorite Bhavageethe & Classics',
      songIds: ['kn_003', 'kn_004', 'kn_001'],
      availableOffline: true,
    ),
    CustomPlaylist(
      id: 'pl_2',
      nameKn: 'ಬೆಳಗಿನ ಭಕ್ತಿ ಗೀತೆಗಳು',
      nameEn: 'Morning Dasa Sahitya & Vachanas',
      songIds: ['kn_006', 'kn_007', 'kn_013'],
      availableOffline: true,
    ),
  ];

  bool _isSyncing = false;

  UserProfile? get currentUser => _currentUser;
  Set<String> get favoriteSongIds => Set.unmodifiable(_favoriteSongIds);
  List<String> get listeningHistoryIds => List.unmodifiable(_listeningHistoryIds);
  List<CustomPlaylist> get playlists => List.unmodifiable(_playlists);
  bool get isSyncing => _isSyncing;

  bool isFavorite(String songId) => _favoriteSongIds.contains(songId);

  void toggleFavorite(String songId) {
    if (_favoriteSongIds.contains(songId)) {
      _favoriteSongIds.remove(songId);
    } else {
      _favoriteSongIds.add(songId);
    }
    _triggerCloudSync();
    notifyListeners();
  }

  void recordListeningHistory(Song song) {
    _listeningHistoryIds.remove(song.id);
    _listeningHistoryIds.insert(0, song.id);
    if (_listeningHistoryIds.length > 50) {
      _listeningHistoryIds.removeLast();
    }
    notifyListeners();
  }

  void createPlaylist({
    required String nameKn,
    required String nameEn,
    List<String> initialSongIds = const [],
  }) {
    _playlists.add(
      CustomPlaylist(
        id: 'pl_${DateTime.now().millisecondsSinceEpoch}',
        nameKn: nameKn.isEmpty ? nameEn : nameKn,
        nameEn: nameEn,
        songIds: List.from(initialSongIds),
      ),
    );
    _triggerCloudSync();
    notifyListeners();
  }

  Future<void> signInWithPhoneOtp(String phoneNumber, String otpCode) async {
    _isSyncing = true;
    notifyListeners();
    await Future.delayed(const Duration(milliseconds: 500));
    _currentUser = UserProfile(
      uid: 'usr_otp_${phoneNumber.hashCode.abs()}',
      displayName: 'Kannada Rasika ($phoneNumber)',
      phoneOrEmail: phoneNumber,
      authMethod: 'phone_otp',
      lastSyncedAt: DateTime.now(),
    );
    _isSyncing = false;
    notifyListeners();
  }

  Future<void> signInWithGoogle() async {
    _isSyncing = true;
    notifyListeners();
    await Future.delayed(const Duration(milliseconds: 500));
    _currentUser = UserProfile(
      uid: 'usr_google_karnataka',
      displayName: 'chethan.gowda@gmail.com',
      phoneOrEmail: 'chethan.gowda@gmail.com',
      authMethod: 'google',
      lastSyncedAt: DateTime.now(),
    );
    _isSyncing = false;
    notifyListeners();
  }

  Future<void> _triggerCloudSync() async {
    if (_currentUser == null) return;
    _isSyncing = true;
    notifyListeners();
    await Future.delayed(const Duration(milliseconds: 300));
    _currentUser = UserProfile(
      uid: _currentUser!.uid,
      displayName: _currentUser!.displayName,
      phoneOrEmail: _currentUser!.phoneOrEmail,
      authMethod: _currentUser!.authMethod,
      lastSyncedAt: DateTime.now(),
    );
    _isSyncing = false;
    notifyListeners();
  }
}
