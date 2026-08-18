/* HS Code Finder — service worker.
   Caches the app shell on install so it opens instantly and works offline
   after the first visit. Everything the app needs (data, logic, styles) is
   inlined in index.html, so caching that one file plus the manifest/icons
   is enough for full offline use. */
const CACHE_NAME = "hscf-cache-v3";
const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-192.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png",
  "./favicon.ico"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// The app's HTML (what you see when you open it) is network-first: every time
// you open the app with internet access, it fetches the latest version so
// fixes/updates show up immediately instead of waiting on a stale cached
// copy to slowly get revalidated. If there's no connection, it falls back
// to the last cached copy so the app still opens offline.
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  const isNavigation = event.request.mode === "navigate" || event.request.destination === "document";
  if (isNavigation) {
    event.respondWith(
      fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.ok) {
          const copy = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
        }
        return networkResponse;
      }).catch(() => caches.match(event.request).then(cached => cached || caches.match("./index.html")))
    );
    return;
  }
  // Everything else (icons, manifest) stays cache-first for speed, with a
  // background refresh so it still keeps itself current over time.
  event.respondWith(
    caches.match(event.request).then(cached => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.ok) {
          const copy = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
        }
        return networkResponse;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
