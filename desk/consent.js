(() => {
  const KEY = "newsroom-desk-consent-v1";
  const CASH = "https://cash.app/$icoss";
  const BOX = { minLat: 41.98, maxLat: 42.32, minLng: -71.12, maxLng: -70.64 };
  function inSouthShore(lat, lng) {
    return lat >= BOX.minLat && lat <= BOX.maxLat && lng >= BOX.minLng && lng <= BOX.maxLng;
  }
  function read() {
    try {
      const parsed = JSON.parse(localStorage.getItem(KEY) || "{}");
      return { ads: parsed.ads === true, geo: parsed.geo === true, updatedAt: parsed.updatedAt || "" };
    } catch {
      return { ads: false, geo: false, updatedAt: "" };
    }
  }
  function write(partial) {
    const next = { ...read(), ...partial, updatedAt: new Date().toISOString() };
    if (!next.ads) next.geo = false;
    localStorage.setItem(KEY, JSON.stringify(next));
    window.dispatchEvent(new CustomEvent("desk-consent"));
    return next;
  }
  function coffee(privacy, consent, geo) {
    const note = consent.ads
      ? (consent.geo
          ? (geo === "elsewhere"
              ? "House ads for Jules Gutter Cleaning are geo-fenced to the South Shore. This device is outside that fence, so you still see the tip jar."
              : "Ads are on. Local South Shore ads load only if this device is inside the fence.")
          : "Ads are on, but location is off. Local South Shore ads will not load without it.")
      : "Future ads, if you opt in, can be geo-fenced to the South Shore for Jules Gutter Cleaning. No ad network loads until you say so.";
    return `
      <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">Keep the desk independent</p>
      <h2 class="mt-2 font-display text-2xl font-semibold">Buy me a coffee</h2>
      <p class="mt-2 max-w-xl text-sm leading-relaxed text-muted">Ads stay off unless you turn them on. Until then this slot is a tip jar — Cash App $icoss.</p>
      <div class="mt-4 flex flex-wrap gap-2">
        <a href="${CASH}" class="inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">Cash App $icoss</a>
        ${consent.ads ? "" : '<button type="button" data-opt-in-ads class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Opt in to ads</button>'}
        <a href="${privacy}" class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Ads settings</a>
      </div>
      <p class="mt-3 text-xs text-muted">${note} <a href="${privacy}" class="underline">How this works</a>.</p>
    `;
  }
  function jules(privacy) {
    return `
      <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">South Shore · house ad</p>
      <h2 class="mt-2 font-display text-2xl font-semibold">Jules Gutter Cleaning</h2>
      <p class="mt-2 text-sm leading-relaxed text-muted">Gutters cleared. Downspouts flowing. South Shore Massachusetts.</p>
      <a href="${CASH}" class="mt-4 inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">Pay or tip on Cash App $icoss</a>
      <p class="mt-3 text-xs text-muted">Shown because you opted into ads and this device looks like South Shore Massachusetts. <a href="${privacy}" class="underline">Change this</a>.</p>
    `;
  }
  function renderSlots(consent, geo) {
    document.querySelectorAll("[data-support]").forEach((el) => {
      const privacy = el.getAttribute("data-privacy") || "privacy/";
      el.innerHTML = consent.ads && geo === "south-shore" ? jules(privacy) : coffee(privacy, consent, geo);
    });
  }
  function syncForm(consent) {
    const ads = document.querySelector("[data-ads-toggle]");
    const geo = document.querySelector("[data-geo-toggle]");
    if (ads) ads.checked = consent.ads;
    if (geo) {
      geo.checked = consent.geo;
      geo.disabled = !consent.ads;
    }
  }
  function locateAndPaint() {
    const consent = read();
    syncForm(consent);
    if (!consent.ads || !consent.geo || !navigator.geolocation) {
      renderSlots(consent, "unknown");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        renderSlots(consent, inSouthShore(pos.coords.latitude, pos.coords.longitude) ? "south-shore" : "elsewhere");
      },
      () => renderSlots(consent, "unknown"),
      { maximumAge: 86400000, timeout: 8000, enableHighAccuracy: false },
    );
  }
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-opt-in-ads]")) write({ ads: true });
  });
  document.addEventListener("change", (e) => {
    const t = e.target;
    if (t.matches("[data-ads-toggle]")) write({ ads: t.checked, geo: t.checked ? read().geo : false });
    if (t.matches("[data-geo-toggle]")) write({ geo: t.checked });
  });
  window.addEventListener("desk-consent", locateAndPaint);
  locateAndPaint();
})();
