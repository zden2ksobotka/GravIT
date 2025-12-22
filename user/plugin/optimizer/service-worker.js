const CACHE_NAME = 'cms-n0ip-eu-cache-v1';
const urlsToCache = [
  "/user/theme/light/css/style.css",
  "/user/theme/light/css/skeleton.css",
  "/user/theme/light/css/atom-one-dark.min.css",
  "/user/theme/light/js/main.js",
  "/user/theme/light/js/highlight.min.js",
  "https://code.jquery.com/jquery-3.6.0.min.js",
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",
  "/user/plugin/alerts/css/alerts.css",
  "/user/plugin/notices/css/notices.css",
  "/user/plugin/optimizer/js/optimizer.js",
  "/user/plugin/alerts/js/alerts.js",
  "/user/plugin/notices/js/notices.js"
];

// Install event: Open cache and add all core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        // Use a more robust caching method instead of addAll to handle redirects gracefully.
        const promises = urlsToCache.map(url => {
          return fetch(url, { redirect: 'follow' }) // Explicitly follow redirects
            .then(response => {
              if (!response.ok) {
                // If we get a bad response (404, 500, etc.), fail the install.
                throw new TypeError('Bad response for ' + url);
              }
              // Put a clone of the response into the cache.
              return cache.put(url, response);
            });
        });
        return Promise.all(promises);
      })
  );
});

// Fetch event: Serve assets from cache first, fall back to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response; // Return from cache
        }
        return fetch(event.request); // Fall back to network
      })
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
