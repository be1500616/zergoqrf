// ZERGO QR Service Worker for PWA functionality
// Provides offline caching and performance optimization

const CACHE_NAME = 'zergo-qr-v1.0.0';
const STATIC_CACHE_NAME = 'zergo-qr-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'zergo-qr-dynamic-v1.0.0';

// Static assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/main.dart.js',
  '/flutter.js',
  '/manifest.json',
  '/icons/Icon-192.png',
  '/icons/Icon-512.png',
  '/favicon.png',
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\/v1\/public\/menu\//,
  /\/api\/v1\/public\/menu\/.*\/categories/,
  /\/api\/v1\/public\/menu\/.*\/featured/,
];

// Image cache patterns
const IMAGE_CACHE_PATTERNS = [
  /\.(jpg|jpeg|png|gif|webp|svg)$/i,
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Static assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Failed to cache static assets', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME &&
                cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!request.url.startsWith('http')) {
    return;
  }

  event.respondWith(handleFetch(request, url));
});

async function handleFetch(request, url) {
  try {
    // Strategy 1: Static assets - Cache First
    if (STATIC_ASSETS.some(asset => url.pathname === asset || url.pathname.endsWith(asset))) {
      return await cacheFirst(request, STATIC_CACHE_NAME);
    }

    // Strategy 2: API requests - Network First with fallback
    if (API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname))) {
      return await networkFirstWithFallback(request, DYNAMIC_CACHE_NAME);
    }

    // Strategy 3: Images - Cache First with network fallback
    if (IMAGE_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname))) {
      return await cacheFirstWithNetworkFallback(request, DYNAMIC_CACHE_NAME);
    }

    // Strategy 4: HTML pages - Network First
    if (request.headers.get('accept')?.includes('text/html')) {
      return await networkFirst(request, DYNAMIC_CACHE_NAME);
    }

    // Default: Network only
    return await fetch(request);

  } catch (error) {
    console.error('Service Worker: Fetch failed', error);
    
    // Return offline fallback for HTML requests
    if (request.headers.get('accept')?.includes('text/html')) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      return await cache.match('/') || new Response('Offline', { status: 503 });
    }
    
    throw error;
  }
}

// Cache First strategy
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  const networkResponse = await fetch(request);
  
  if (networkResponse.ok) {
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// Network First strategy
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Network First with fallback strategy for API requests
async function networkFirstWithFallback(request, cacheName) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      // Cache API responses with timestamp for TTL management
      // Clone the response to avoid "locked response body" error
      const responseToCache = networkResponse.clone();

      // Store the current timestamp in a custom cache key for TTL tracking
      const timestampKey = `${request.url}#timestamp`;
      const timestampResponse = new Response(Date.now().toString(), {
        headers: { 'Content-Type': 'text/plain' }
      });

      // Cache both the actual response and the timestamp
      await Promise.all([
        cache.put(request, responseToCache),
        cache.put(timestampKey, timestampResponse)
      ]);
    }

    return networkResponse;
  } catch (error) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      // Check if cache is still valid (30 minutes)
      const timestampKey = `${request.url}#timestamp`;
      const timestampResponse = await cache.match(timestampKey);

      if (timestampResponse) {
        const cacheTimestamp = parseInt(await timestampResponse.text());
        const cacheAge = Date.now() - cacheTimestamp;
        const maxAge = 30 * 60 * 1000; // 30 minutes

        if (cacheAge < maxAge) {
          return cachedResponse;
        }

        // Cache is expired, remove both entries
        await Promise.all([
          cache.delete(request),
          cache.delete(timestampKey)
        ]);
      } else {
        // Return cached response if no timestamp (better than nothing)
        return cachedResponse;
      }
    }

    throw error;
  }
}

// Cache First with Network Fallback strategy for images
async function cacheFirstWithNetworkFallback(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Return a placeholder image for failed image requests
    return new Response(
      '<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" fill="#f0f0f0"/><text x="100" y="100" text-anchor="middle" dy=".3em" fill="#999">Image unavailable</text></svg>',
      {
        headers: {
          'Content-Type': 'image/svg+xml',
          'Cache-Control': 'no-cache'
        }
      }
    );
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync', event.tag);
  
  if (event.tag === 'cart-sync') {
    event.waitUntil(syncCart());
  }
});

async function syncCart() {
  try {
    // Implement cart synchronization logic here
    console.log('Service Worker: Syncing cart data');
  } catch (error) {
    console.error('Service Worker: Cart sync failed', error);
  }
}

// Push notifications (for future order updates)
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icons/Icon-192.png',
    badge: '/icons/Icon-72.png',
    vibrate: [200, 100, 200],
    data: data.data,
    actions: data.actions || []
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});

// Message handling for cache management
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(clearAllCaches());
  }
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
  console.log('Service Worker: All caches cleared');
}
