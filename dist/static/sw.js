const CACHE_NAME = 'groqee-pwa-v1';
const urlsToCache = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  'https://groq.com/wp-content/uploads/2024/03/PBG-mark1-color.svg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
