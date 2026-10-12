import json

html_path = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\index.html"
manifest_path = r"C:\Users\DELL\.gemini\antigravity\scratch\raaga\mobile\web_preview\audio\originals\manifest.json"

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

manifest_js = "    const ORIGINAL_MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=2) + ";\n\n"

old_song_fn = """    function song(id, knInit, enInit, titleKn, titleEn, artist, movie, year, mood, dur, lKn, lEn) {
      return {
        id, knInit, enInit, titleKn, titleEn, artist, movie, year, mood,
        duration: dur,
        isrc: `IN-KAN-${String(year).slice(-2)}-${id}`,
        gradient: ART_GRADIENTS[parseInt(id, 10) % ART_GRADIENTS.length],
        lyrics: [
          { t: 0, kn: lKn, en: lEn },
          { t: 7, kn: `ಗಾಯಕರು: ${artist} • ಚಿತ್ರ: ${movie} (${year})`, en: `Artist: ${artist} • Movie/Album: ${movie} (${year})` },
          { t: 14, kn: 'ಕನ್ನಡ ರಾಗ • ಅಪ್ಪಟ ಕನ್ನಡ ಸಂಗೀತ ಮಾತ್ರ', en: 'Kannada Raaga • 100% Licensed Kannada Music' }
        ]
      };
    }"""

new_song_fn = manifest_js + """    function song(id, knInit, enInit, titleKn, titleEn, artist, movie, year, mood, dur, lKn, lEn) {
      const orig = ORIGINAL_MANIFEST[id] || {};
      return {
        id, knInit, enInit, titleKn, titleEn, artist, movie, year, mood,
        duration: 30,
        fullDuration: dur,
        localAudio: orig.localAudio || null,
        remoteAudio: orig.remoteAudio || null,
        artworkUrl: orig.artworkUrl || null,
        matchedTrack: orig.matchedTrack || titleEn,
        isrc: `IN-KAN-${String(year).slice(-2)}-${id}`,
        gradient: ART_GRADIENTS[parseInt(id, 10) % ART_GRADIENTS.length],
        lyrics: [
          { t: 0, kn: lKn, en: lEn },
          { t: 8, kn: `ಗಾಯಕರು: ${artist} • ಚಿತ್ರ: ${movie} (${year})`, en: `Artist: ${artist} • Movie/Album: ${movie} (${year})` },
          { t: 16, kn: `ಮೂಲ ಧ್ವನಿಮುದ್ರಣ: ${orig.matchedTrack || titleEn}`, en: `Original Studio Recording • ${orig.matchedAlbum || movie}` }
        ]
      };
    }"""

assert old_song_fn in html, "Could not find old_song_fn"
html = html.replace(old_song_fn, new_song_fn, 1)

old_audio_sync = """    function getOrBuildSongAudioUrl(s) {
      if (s.customAudioUrl) return s.customAudioUrl;
      if (songAudioCache[s.id]) return songAudioCache[s.id];"""

new_audio_sync = """    function getOrBuildSongAudioUrl(s) {
      if (s.customAudioUrl) return s.customAudioUrl;
      const isHttp = window.location.protocol.startsWith('http');
      if (isHttp && s.localAudio && !s._localFailed) return s.localAudio;
      if (s.remoteAudio && !s._remoteFailed) return s.remoteAudio;
      if (songAudioCache[s.id]) return songAudioCache[s.id];"""

assert old_audio_sync in html, "Could not find old_audio_sync"
html = html.replace(old_audio_sync, new_audio_sync, 1)

old_sync_fn = """    function syncAudio(reset = false) {
      const url = getOrBuildSongAudioUrl(state.currentSong);
      if (audioPlayer.src !== url) audioPlayer.src = url;
      if (reset) audioPlayer.currentTime = 0;
      if (state.isPlaying) {
        audioPlayer.play().catch(() => {});
      } else {
        audioPlayer.pause();
      }
    }

    setInterval(() => {
      if (state.isPlaying) {
        state.positionSec = (state.positionSec + 1) % state.currentSong.duration;
        updatePlayerSurfaces();
      }
    }, 1000);"""

new_sync_fn = """    audioPlayer.onerror = () => {
      const s = state.currentSong;
      if (!s) return;
      if (!s._localFailed && s.localAudio) {
        s._localFailed = true;
        syncAudio(false);
      } else if (!s._remoteFailed && s.remoteAudio) {
        s._remoteFailed = true;
        syncAudio(false);
      }
    };

    audioPlayer.ontimeupdate = () => {
      if (state.isPlaying && !isNaN(audioPlayer.currentTime)) {
        state.positionSec = Math.floor(audioPlayer.currentTime);
        if (audioPlayer.duration && !isNaN(audioPlayer.duration)) {
          state.currentSong.duration = Math.max(1, Math.round(audioPlayer.duration));
        }
        updatePlayerSurfaces();
      }
    };

    function syncAudio(reset = false) {
      const url = getOrBuildSongAudioUrl(state.currentSong);
      if (!audioPlayer.src || !audioPlayer.src.endsWith(url)) {
        audioPlayer.src = url;
      }
      if (reset) audioPlayer.currentTime = 0;
      if (state.isPlaying) {
        audioPlayer.play().catch(() => {});
      } else {
        audioPlayer.pause();
      }
    }"""

assert old_sync_fn in html, "Could not find old_sync_fn"
html = html.replace(old_sync_fn, new_sync_fn, 1)

# Update thumbnails and cards to display real album artwork
old_thumb = """          <div class="song-thumb" style="background:${s.gradient}">
            <span class="song-thumb-kn">${s.knInit}</span>
            <span class="song-thumb-year">${s.year}</span>
          </div>"""

new_thumb = """          <div class="song-thumb" style="background:${s.artworkUrl ? `linear-gradient(180deg, rgba(11,17,16,0.25), rgba(11,17,16,0.78)), url('${s.artworkUrl}') center/cover` : s.gradient}">
            <span class="song-thumb-kn" style="text-shadow:0 2px 6px #000;">${s.knInit}</span>
            <span class="song-thumb-year" style="text-shadow:0 1px 4px #000;">${s.year}</span>
          </div>"""

assert old_thumb in html, "Could not find old_thumb"
html = html.replace(old_thumb, new_thumb, 1)

old_sq = """        <div class="square-card" onclick="playOrToggleSong(event, '${s.id}')">
          <div class="square-art" style="background:${s.gradient}">
            <span class="square-art-badge">${badgeText || s.year}</span>
            <div class="square-art-glyph">${s.knInit}</div>
          </div>"""

new_sq = """        <div class="square-card" onclick="playOrToggleSong(event, '${s.id}')">
          <div class="square-art" style="background:${s.artworkUrl ? `linear-gradient(180deg, rgba(11,17,16,0.18), rgba(11,17,16,0.82)), url('${s.artworkUrl}') center/cover` : s.gradient}">
            <span class="square-art-badge">${badgeText || s.year}</span>
            <div class="square-art-glyph" style="text-shadow:0 2px 10px rgba(0,0,0,0.85);">${s.knInit}</div>
          </div>"""

assert old_sq in html, "Could not find old_sq"
html = html.replace(old_sq, new_sq, 1)

old_vid = """      document.getElementById('trendingVideosRow').innerHTML = CATALOG.slice(0, 6).map(s => `
        <div class="video-poster-card" style="background:${s.gradient}" onclick="playOrToggleSong(event, '${s.id}')">"""

new_vid = """      document.getElementById('trendingVideosRow').innerHTML = CATALOG.slice(0, 8).map(s => `
        <div class="video-poster-card" style="background:${s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : s.gradient}" onclick="playOrToggleSong(event, '${s.id}')">"""

assert old_vid in html, "Could not find old_vid"
html = html.replace(old_vid, new_vid, 1)

# Update updatePlayerSurfaces to show artwork on mini-player and full Now Playing
old_surf = """      document.getElementById('miniProgressCircle').style.strokeDashoffset = dashOffset;
      document.getElementById('miniArtGlyph').innerText = s.knInit;"""

new_surf = """      document.getElementById('miniProgressCircle').style.strokeDashoffset = dashOffset;
      const miniArtEl = document.getElementById('miniArtGlyph');
      miniArtEl.innerText = s.artworkUrl ? '' : s.knInit;
      miniArtEl.style.background = s.artworkUrl ? `url('${s.artworkUrl}') center/cover` : 'var(--surface-elevated)';
      const npArtBox = document.getElementById('npArtBox');
      if (npArtBox) {
        npArtBox.style.background = s.artworkUrl
          ? `linear-gradient(180deg, rgba(11,17,16,0.35) 0%, rgba(11,17,16,0.85) 100%), url('${s.artworkUrl}') center/cover`
          : s.gradient;
      }"""

assert old_surf in html, "Could not find old_surf"
html = html.replace(old_surf, new_surf, 1)

# Also add Live Apple Music / iTunes Kannada Search when typing in Search input!
old_search_block = """      const q = (document.getElementById('searchInput').value || '').trim().toLowerCase();
      let results = [...CATALOG];
      if (state.azLetter !== 'ALL') {
        results = results.filter(s => (state.azScript === 'kn' ? s.knInit : s.enInit) === state.azLetter);
      }
      if (q) {
        results = results.filter(s =>
          `${s.titleKn} ${s.titleEn} ${s.artist} ${s.movie} ${s.year}`.toLowerCase().includes(q)
        );
      }
      document.getElementById('searchResultsTitle').innerText = `Results (${results.length})`;
      document.getElementById('searchSongRows').innerHTML = results.map(renderSongRow).join('');"""

new_search_block = """      const q = (document.getElementById('searchInput').value || '').trim().toLowerCase();
      let results = [...CATALOG];
      if (state.azLetter !== 'ALL') {
        results = results.filter(s => (state.azScript === 'kn' ? s.knInit : s.enInit) === state.azLetter);
      }
      if (q) {
        results = results.filter(s =>
          `${s.titleKn} ${s.titleEn} ${s.artist} ${s.movie} ${s.year} ${s.matchedTrack || ''}`.toLowerCase().includes(q)
        );
        triggerLiveKannadaSearch(q);
      }
      document.getElementById('searchResultsTitle').innerText = `Original Kannada Songs (${results.length})`;
      document.getElementById('searchSongRows').innerHTML = results.map(renderSongRow).join('');"""

assert old_search_block in html, "Could not find old_search_block"
html = html.replace(old_search_block, new_search_block, 1)

live_search_fn = """    let liveSearchTimer = null;
    let lastLiveQuery = '';
    function triggerLiveKannadaSearch(q) {
      if (q.length < 3 || q === lastLiveQuery) return;
      clearTimeout(liveSearchTimer);
      liveSearchTimer = setTimeout(async () => {
        lastLiveQuery = q;
        try {
          const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(q + ' Kannada')}&entity=song&country=IN&limit=8`);
          const data = await res.json();
          let added = 0;
          (data.results || []).forEach(item => {
            if (!item.previewUrl) return;
            const sid = 'LIVE-' + item.trackId;
            if (!CATALOG.some(x => x.id === sid || x.remoteAudio === item.previewUrl)) {
              const yr = item.releaseDate ? parseInt(item.releaseDate.slice(0, 4), 10) : 2025;
              const enCh = (item.trackName || 'K').trim().charAt(0).toUpperCase();
              CATALOG.push({
                id: sid,
                knInit: 'ಕ',
                enInit: enCh,
                titleKn: `${item.trackName} (ಮೂಲ ಹಾಡು)`,
                titleEn: item.trackName,
                artist: item.artistName || 'Kannada Artist',
                movie: item.collectionName || 'Kannada Original',
                year: yr,
                mood: 'feelgood',
                duration: 30,
                localAudio: null,
                remoteAudio: item.previewUrl,
                artworkUrl: (item.artworkUrl100 || '').replace('100x100bb', '600x600bb'),
                matchedTrack: item.trackName,
                isrc: `IN-KAN-LIVE-${item.trackId}`,
                gradient: ART_GRADIENTS[added % ART_GRADIENTS.length],
                lyrics: [
                  { t: 0, kn: `${item.trackName} • ಮೂಲ ಕನ್ನಡ ಗೀತೆ`, en: `${item.trackName} • Original Studio Stream` },
                  { t: 8, kn: `ಗಾಯಕರು: ${item.artistName}`, en: `Album: ${item.collectionName}` }
                ]
              });
              added++;
            }
          });
          if (added > 0 && state.activeTab === 'search') {
            renderSearchScreen();
          }
        } catch (err) {}
      }, 450);
    }

    function renderSearchScreen() {"""

html = html.replace("    function renderSearchScreen() {", live_search_fn, 1)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully injected 34 original Kannada songs + live Kannada search into index.html!")
