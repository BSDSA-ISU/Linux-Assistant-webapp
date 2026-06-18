const CACHE_NAME = 'hourai-chat-v1';
const ASSETS = [
  '/',
  '/static/styles.css',
  '/static/manifest.json'
];

// Cache core files on installation
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS).catch(err => console.log("Caching asset error ignored during local setup."));
    })
  );
});

// Intercept requests so it behaves like a standalone PWA
self.addEventListener('fetch', (e) => {
  // Pass through all API requests straight to backend without locking them down to stale cache
  if (e.request.url.includes('/api/')) {
    return;
  }
  
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});