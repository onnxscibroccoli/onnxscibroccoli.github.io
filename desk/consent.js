(() => {
  const KEY = "newsroom-desk-consent-v1";
  const CASH = "https://cash.app/$icoss";
  const TEL = "tel:+12676672321";
  const PHONE = "(267) 667-2321";
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
  function coffee(privacy) {
    return `
      <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">Keep the desk independent</p>
      <h2 class="mt-2 font-display text-2xl font-semibold">Buy me a coffee</h2>
      <p class="mt-2 max-w-xl text-sm leading-relaxed text-muted">Ads stay off unless you turn them on. Until then this slot is a tip jar — Cash App $icoss. If you would rather see a paying ad than tip, opt in and a bar appears at the bottom of the screen.</p>
      <div class="mt-4 flex flex-wrap gap-2">
        <a href="${CASH}" class="inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">Cash App $icoss</a>
        <button type="button" data-opt-in-ads class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Show ads instead</button>
        <a href="${privacy}" class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Ads settings</a>
      </div>
    `;
  }
  function adsOnCard(privacy) {
    return `
      <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">Ads are on</p>
      <h2 class="mt-2 font-display text-2xl font-semibold">Paying ads sit at the bottom</h2>
      <p class="mt-2 max-w-xl text-sm leading-relaxed text-muted">A non-intrusive bar funds the desk. Prefer to skip ads? Tip instead — Cash App $icoss.</p>
      <div class="mt-4 flex flex-wrap gap-2">
        <a href="${CASH}" class="inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">Cash App $icoss</a>
        <a href="${privacy}" class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Ad settings</a>
      </div>
    `;
  }
  function julesRail(privacy) {
    return `<div class="ad-rail-inner">
      <div>
        <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">Advertisement · Paid · South Shore</p>
        <p class="mt-1 font-display text-lg font-semibold">Jules Gutter Cleaning</p>
        <p class="text-sm text-muted">Gutters cleared. Downspouts flowing. South Shore Massachusetts.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a href="${TEL}" rel="sponsored nofollow" class="inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">${PHONE}</a>
        <a href="${CASH}" rel="sponsored nofollow" class="inline-flex min-h-11 items-center rounded-sm border border-rule px-4 text-sm font-medium text-ink">Cash App $icoss</a>
        <a href="${privacy}" class="inline-flex min-h-11 items-center text-xs text-muted underline">Ad settings</a>
      </div>
    </div>`;
  }
  function houseRail(privacy) {
    return `<div class="ad-rail-inner">
      <div>
        <p class="font-sans text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-slate">Advertisement · Paid placement</p>
        <p class="mt-1 font-display text-lg font-semibold">Advertise on this desk</p>
        <p class="text-sm text-muted">A non-intrusive paying ad funds the next investigation. Tip if you want; this bar is the other door.</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a href="${CASH}" rel="sponsored nofollow" class="inline-flex min-h-11 items-center rounded-sm bg-ink px-4 text-sm font-medium text-paper">Buy this space $icoss</a>
        <a href="${privacy}" class="inline-flex min-h-11 items-center text-xs text-muted underline">Ad settings</a>
      </div>
    </div>`;
  }
  function renderSlots(consent, geo) {
    document.querySelectorAll("[data-support]").forEach((el) => {
      const privacy = el.getAttribute("data-privacy") || "privacy/";
      el.innerHTML = consent.ads ? adsOnCard(privacy) : coffee(privacy);
    });
    const rail = document.getElementById("ad-rail");
    if (rail) {
      const privacy = document.querySelector("[data-support]")?.getAttribute("data-privacy") || "privacy/";
      if (consent.ads) {
        rail.hidden = false;
        document.body.classList.add("has-ads");
        rail.innerHTML = geo === "south-shore" ? julesRail(privacy) : houseRail(privacy);
      } else {
        rail.hidden = true;
        document.body.classList.remove("has-ads");
        rail.innerHTML = "";
      }
    }
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
