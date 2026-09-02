self.addEventListener("install",event=>{
  self.skipWaiting();
});

self.addEventListener("activate",event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.filter(key=>key.startsWith("fabios-")).map(key=>caches.delete(key)));
    await self.clients.claim();
  })());
});

// Fabio's standalone uses network responses directly. Keeping the service worker
// cache-free prevents an iOS Home Screen app from being pinned to an old shell.
self.addEventListener("fetch",event=>{
  if(event.request.mode==="navigate"){
    event.respondWith(fetch(event.request,{cache:"no-store"}).catch(()=>fetch("/fabios-app/",{cache:"no-store"})));
  }
});
