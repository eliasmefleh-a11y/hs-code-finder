#!/usr/bin/env python3
"""
Build script: regenerates pwa/index.html and pwa_flat/index.html from the
master hs_code_finder.html by inserting the PWA-only additions (manifest
links, install-prompt UI, service worker registration + self-update check).

Run this any time hs_code_finder.html changes and needs to be propagated.
    python3 build_pwa.py
"""
import re
import sys

MASTER = "hs_code_finder.html"
PWA_OUT = "pwa/index.html"
PWA_FLAT_OUT = "pwa_flat/index.html"

HEAD_OLD = '<title>HS Code Finder — كاشف رموز التعرفة الجمركية</title>\n<style>'
HEAD_NEW = '''<title>HS Code Finder — كاشف رموز التعرفة الجمركية</title>
<meta name="description" content="Bilingual (Arabic/English) HS tariff code lookup with VAT and duty rates, built from the official Lebanese customs tariff book.">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#0a0e17">
<link rel="icon" type="image/x-icon" href="favicon.ico">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="HS Code Finder">
<meta name="mobile-web-app-capable" content="yes">
<style>'''

CSS_OLD = "  .disclaimer{\n    max-width:920px;\n    margin:8px auto 0;"
CSS_NEW = '''  .install-btn{
    padding:6px 12px;
    border-radius:999px;
    background:var(--accent);
    color:var(--accent-ink);
    border:none;
    font-size:0.82rem;
    font-weight:700;
    cursor:pointer;
  }
  .install-btn:hover{ opacity:0.9; }
  .ios-install-hint{
    max-width:920px;
    margin:8px auto 0;
    padding:10px 14px;
    background:rgba(51,209,122,0.1);
    border:1px solid rgba(51,209,122,0.35);
    border-radius:var(--radius);
    font-size:0.85rem;
    color:var(--text);
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
  }
  .ios-install-hint button{
    background:none;
    border:none;
    color:var(--muted);
    cursor:pointer;
    font-size:1rem;
  }
  .update-banner{
    max-width:920px;
    margin:8px auto 0;
    padding:10px 14px;
    background:rgba(59,130,246,0.12);
    border:1px solid rgba(59,130,246,0.4);
    border-radius:var(--radius);
    font-size:0.85rem;
    color:var(--text);
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
  }
  .update-banner button{
    padding:6px 12px;
    border-radius:999px;
    background:var(--accent);
    color:var(--accent-ink);
    border:none;
    font-size:0.82rem;
    font-weight:700;
    cursor:pointer;
    white-space:nowrap;
  }
  .update-banner button:hover{ opacity:0.9; }
  .disclaimer{
    max-width:920px;
    margin:8px auto 0;'''

HEADER_OLD = '''      <button data-lang="en">EN</button>
      <button data-lang="ar">AR</button>
    </div>
  </div>
</header>'''
HEADER_NEW = '''      <button data-lang="en">EN</button>
      <button data-lang="ar">AR</button>
    </div>
    <button class="install-btn" id="installBtn" style="display:none;" type="button">⬇ Install App</button>
    <div class="ios-install-hint" id="iosInstallHint" style="display:none;">
      Install this app: tap <b>Share</b> <span aria-hidden="true">⎋</span> then <b>Add to Home Screen</b>.
      <button type="button" id="iosHintClose" aria-label="Dismiss">✕</button>
    </div>
    <div class="update-banner" id="updateBanner" style="display:none;">
      <span>🔄 A new version of the app is available.</span>
      <button type="button" id="updateBannerReload">Refresh now</button>
    </div>
  </div>
</header>'''

JS_OLD = '/* ============================= INIT ============================= */'
JS_NEW = '''/* ============================= PWA: install + offline ============================= */
let swRegistration = null;
function showUpdateBanner(){
  const b = document.getElementById("updateBanner");
  if(b) b.style.display = "flex";
}
if("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")){
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").then(reg => {
      swRegistration = reg;
      // If an update was already found/waiting before this load (e.g. a previous
      // tab installed it), surface the banner right away instead of only on the
      // next updatefound event.
      if(reg.waiting && navigator.serviceWorker.controller){
        showUpdateBanner();
      }
      reg.addEventListener("updatefound", () => {
        const newWorker = reg.installing;
        if(!newWorker) return;
        newWorker.addEventListener("statechange", () => {
          // "installed" + an existing controller means this is an UPDATE to an
          // already-running app (not the very first install) — that's the case
          // where we want to tell the user a newer version is ready.
          if(newWorker.state === "installed" && navigator.serviceWorker.controller){
            showUpdateBanner();
          }
        });
      });
    }).catch(()=>{});
  });
  // The service worker's fetch handler already fetches the latest HTML fresh on
  // every navigation (network-first), so a normal reopen/reload always gets the
  // newest version automatically. This extra layer covers the case where someone
  // leaves the app open in one tab for hours: it periodically asks the browser to
  // check for a newer service-worker/app version in the background, and — once
  // found — shows a small non-disruptive banner (rather than force-reloading and
  // wiping out whatever the person was in the middle of typing/searching).
  const checkForUpdate = () => { if(swRegistration) swRegistration.update().catch(()=>{}); };
  document.addEventListener("visibilitychange", () => {
    if(document.visibilityState === "visible") checkForUpdate();
  });
  window.addEventListener("online", checkForUpdate);
  setInterval(checkForUpdate, 60 * 60 * 1000); // hourly, while the tab stays open
}
const updateBannerReloadBtn = document.getElementById("updateBannerReload");
if(updateBannerReloadBtn){
  updateBannerReloadBtn.addEventListener("click", () => location.reload());
}
let deferredInstallPrompt = null;
const installBtn = document.getElementById("installBtn");
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredInstallPrompt = e;
  if(installBtn) installBtn.style.display = "inline-block";
});
if(installBtn){
  installBtn.addEventListener("click", async () => {
    if(!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    installBtn.style.display = "none";
  });
}
window.addEventListener("appinstalled", () => {
  if(installBtn) installBtn.style.display = "none";
  deferredInstallPrompt = null;
});
(function iosInstallHint(){
  const ua = navigator.userAgent || "";
  const isIOS = /iphone|ipad|ipod/i.test(ua);
  const isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  const dismissed = Store.get("hscf_ios_hint_dismissed", false);
  const hint = document.getElementById("iosInstallHint");
  if(isIOS && !isStandalone && !dismissed && hint){
    hint.style.display = "flex";
  }
  const closeBtn = document.getElementById("iosHintClose");
  if(closeBtn){
    closeBtn.addEventListener("click", () => {
      if(hint) hint.style.display = "none";
      Store.set("hscf_ios_hint_dismissed", true);
    });
  }
})();

/* ============================= INIT ============================= */'''


def build():
    with open(MASTER, encoding="utf-8") as f:
        content = f.read()

    for label, old, new in [
        ("head meta", HEAD_OLD, HEAD_NEW),
        ("install/update CSS", CSS_OLD, CSS_NEW),
        ("header HTML", HEADER_OLD, HEADER_NEW),
        ("PWA JS block", JS_OLD, JS_NEW),
    ]:
        count = content.count(old)
        if count != 1:
            print(f"ERROR: anchor for '{label}' found {count} times (expected 1)", file=sys.stderr)
            sys.exit(1)
        content = content.replace(old, new)

    with open(PWA_OUT, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Wrote {PWA_OUT}")

    flat = content.replace("icons/", "")
    with open(PWA_FLAT_OUT, "w", encoding="utf-8") as f:
        f.write(flat)
    print(f"Wrote {PWA_FLAT_OUT}")


if __name__ == "__main__":
    build()
