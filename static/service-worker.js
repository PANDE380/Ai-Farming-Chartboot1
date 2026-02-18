
fetch("/chat", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({message: "hello"})
})

const CACHE_NAME = 'ai-farm-cache-v4';
const toCache = [
  '/',
  '/static/index.html',
  '/static/manifest.json'
];

self.addEventListener('install', evt=>{
  self.skipWaiting();
  evt.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(toCache)));
});

self.addEventListener('activate', evt=>{
  evt.waitUntil(caches.keys().then(keys => Promise.all(keys.map(k => k!==CACHE_NAME && caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', evt=>{
  if(evt.request.method !== 'GET') return;
  evt.respondWith(fetch(evt.request).catch(()=>caches.match(evt.request)));
});
