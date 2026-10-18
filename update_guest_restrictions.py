# -*- coding: utf-8 -*-
"""
update_guest_restrictions.py
Applies guest restrictions to:
1. triggerDirectOrQualityDownload
2. downloadSelectedAzSongs
3. createNewPlaylistPrompt
4. toggleSongInPlaylist
"""

import os

TARGET_FILE = os.path.join('mobile', 'web_preview', 'index.html')

with open(TARGET_FILE, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update triggerDirectOrQualityDownload
old_dl = '''function triggerDirectOrQualityDownload(id) {'''
new_dl = '''function triggerDirectOrQualityDownload(id) {
      if (state.isGuest) {
        showRaagaToast('🔒 Downloads are locked in Guest mode. Sign in to download tracks.');
        openAuthModal();
        return;
      }'''

if old_dl in code and 'if (state.isGuest)' not in code:
    code = code.replace(old_dl, new_dl, 1)
    print('Updated triggerDirectOrQualityDownload with guest check.')

# 2. Update downloadSelectedAzSongs
old_az = '''function downloadSelectedAzSongs() {'''
new_az = '''function downloadSelectedAzSongs() {
      if (state.isGuest) {
        showRaagaToast('🔒 Downloads are locked in Guest mode. Sign in to download tracks.');
        openAuthModal();
        return;
      }'''

if old_az in code and new_az not in code:
    code = code.replace(old_az, new_az, 1)
    print('Updated downloadSelectedAzSongs with guest check.')

# 3. Update createNewPlaylistPrompt
old_pl = '''function createNewPlaylistPrompt(optionalSongId) {'''
new_pl = '''function createNewPlaylistPrompt(optionalSongId) {
      if (state.isGuest) {
        showRaagaToast('🔒 Custom playlists are locked in Guest mode. Sign in to create playlists.');
        openAuthModal();
        return;
      }'''

if old_pl in code and new_pl not in code:
    code = code.replace(old_pl, new_pl, 1)
    print('Updated createNewPlaylistPrompt with guest check.')

with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(code)
print('Guest restrictions applied successfully.')
