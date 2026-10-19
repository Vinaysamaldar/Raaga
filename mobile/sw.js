// Ragaa Music Player - PWA Service Worker for Mobile Install & Offline Audio Cache
const CACHE_NAME = 'ragaa-pwa-v2';
const AUDIO_CACHE = 'ragaa-audio-offline-v2';

const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './ragaa_logo.jpg'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(() => {});
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME && k !== AUDIO_CACHE) {
            return caches.delete(k);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Audio stream caching & offline delivery
  if (e.request.url.includes('.m4a') || e.request.url.includes('.mp3') || e.request.url.includes('.wav') || (e.request.headers.get('range') && e.request.url.includes('saavncdn'))) {
    e.respondWith(
      caches.open(AUDIO_CACHE).then((cache) => {
        return cache.match(e.request).then((cached) => {
          if (cached) return cached;
          return fetch(e.request).then((networkRes) => {
            if (networkRes && networkRes.status === 200) {
              cache.put(e.request, networkRes.clone());
            }
            return networkRes;
          }).catch(() => {
            return cached || new Response('Offline audio', { status: 503 });
          });
        });
      })
    );
    return;
  }

  // Shell & assets network-first with cache fallback
  e.respondWith(
    fetch(e.request).then((res) => {
      if (res && res.status === 200 && e.request.method === 'GET') {
        const resClone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, resClone));
      }
      return res;
    }).catch(() => {
      return caches.match(e.request).then((cached) => {
        if (cached) return cached;
        if (e.request.mode === 'navigate') {
          return caches.match('./index.html') || caches.match('./');
        }
        return new Response('Offline', { status: 503 });
      });
    })
  );
});
