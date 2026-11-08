// Analytics events for the download and Workshop buttons, and the image viewer on the mod pages.
document.addEventListener("click", (e) => {
  const link = e.target.closest("[data-track]");
  if (link && typeof gtag === "function") {
    gtag("event", link.dataset.track === "download" ? "mod_download" : "steam_workshop_click", { mod: link.dataset.mod });
  }
});

// The viewer is a horizontal scroll-snap strip: swipe, trackpad and the scroll wheel move it natively,
// the buttons and the keys (arrows, Home, End, Escape) scroll it to a slide.
const box = document.querySelector("dialog.lightbox");
if (box) {
  const shots = [...document.querySelectorAll("[data-lightbox]")];
  const track = box.querySelector(".track");
  const prev = box.querySelector(".prev");
  const next = box.querySelector(".next");
  const counter = box.querySelector(".counter");

  for (const a of shots) {
    const slide = document.createElement("div");
    slide.className = "slide";
    const img = document.createElement("img");
    img.alt = a.querySelector("img").alt;
    img.dataset.src = a.href;
    slide.append(img);
    track.append(slide);
  }
  const slides = [...track.children];

  const current = () => Math.round(track.scrollLeft / track.clientWidth);
  const load = (i) => {
    // the full images are big: load the visible one and its neighbours only
    for (const j of [i - 1, i, i + 1]) {
      const img = slides[j]?.querySelector("img");
      if (img && !img.src) img.src = img.dataset.src;
    }
  };
  const update = () => {
    const i = current();
    counter.textContent = `${i + 1} / ${slides.length}`;
    prev.disabled = i === 0;
    next.disabled = i === slides.length - 1;
    load(i);
  };
  // while a smooth scroll runs, the next key press counts from where it is going, not from where it is
  let target = null, settle;
  const base = () => target ?? current();
  const go = (i, behavior = "smooth") => {
    target = Math.max(0, Math.min(slides.length - 1, i));
    track.scrollTo({ left: target * track.clientWidth, behavior });
    clearTimeout(settle);
    settle = setTimeout(() => { target = null; }, 900);
  };

  shots.forEach((a, i) => a.addEventListener("click", (e) => {
    e.preventDefault();
    load(i);
    box.showModal();
    go(i, "instant");
    update();
  }));
  track.addEventListener("scroll", update, { passive: true });
  track.addEventListener("scrollend", () => { target = null; });
  // a vertical wheel moves the strip sideways too
  track.addEventListener("wheel", (e) => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      e.preventDefault();
      if (!track.dataset.wheelLock) {
        go(base() + Math.sign(e.deltaY));
        track.dataset.wheelLock = "1";
        setTimeout(() => delete track.dataset.wheelLock, 600);
      }
    }
  }, { passive: false });
  prev.addEventListener("click", () => go(base() - 1));
  next.addEventListener("click", () => go(base() + 1));
  box.querySelector(".close").addEventListener("click", () => box.close());
  // a click on the dark area around the picture closes the viewer
  track.addEventListener("click", (e) => { if (e.target.classList.contains("slide")) box.close(); });
  window.addEventListener("resize", () => { if (box.open) go(base(), "instant"); });
  document.addEventListener("keydown", (e) => {
    if (!box.open) return;
    const keys = { ArrowRight: base() + 1, ArrowLeft: base() - 1, PageDown: base() + 1, PageUp: base() - 1,
                   Home: 0, End: slides.length - 1 };
    if (e.key in keys) {
      e.preventDefault();
      go(keys[e.key]);
    }
  });
}

// The world map on the index page: hovering (or tapping, or focusing) a lit region shows every scenario that covers it;
// a click opens the released one. On touch the first tap shows the tooltip and a second tap on the same region opens it.
const map = document.querySelector(".hexmap");
if (map) {
  const frame = map.parentElement;
  const tip = frame.querySelector(".map-tip");
  const mods = JSON.parse(document.getElementById("map-mods").textContent);
  const zones = [...map.querySelectorAll(".zone")];
  let current = null, touch = false;

  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const show = (zone, x, y) => {
    if (zone !== current) {
      hide();
      current = zone;
      const slugs = zone.dataset.mods.split(" ");
      tip.innerHTML = slugs.map((s) => {
        const m = mods[s];
        return `<p><b>${esc(m.title)}</b>` + (m.soon ? `<span class="soon-label">Coming soon</span>`
          : `<span class="period">${esc(m.period)}</span>`) + `</p>`;
      }).join("");
      const open = zone.getAttribute("href")?.split("/")[1];
      if (touch && open) tip.innerHTML += `<p class="hint">Tap again to open ${esc(mods[open].title)}</p>`;
      for (const z of zones) if (z.dataset.mods.split(" ").includes(slugs[0])) z.classList.add("hot");
      tip.hidden = false;
    }
    // above the pointer, kept inside the frame
    const box = frame.getBoundingClientRect();
    const left = Math.max(0, Math.min(x - box.left - tip.offsetWidth / 2, box.width - tip.offsetWidth));
    let top = y - box.top - tip.offsetHeight - 14;
    if (top < 0) top = y - box.top + 18;
    tip.style.left = `${left}px`;
    tip.style.top = `${top}px`;
  };
  function hide() {
    current = null;
    tip.hidden = true;
    for (const z of zones) z.classList.remove("hot");
  }
  const centre = (zone) => {
    const r = zone.getBoundingClientRect();
    return [r.left + r.width / 2, r.top + r.height / 2];
  };

  map.addEventListener("pointerdown", (e) => { touch = e.pointerType !== "mouse"; });
  map.addEventListener("pointermove", (e) => {
    if (e.pointerType !== "mouse") return;
    const zone = e.target.closest(".zone");
    if (zone) show(zone, e.clientX, e.clientY); else if (current) hide();
  });
  map.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") hide(); });
  map.addEventListener("click", (e) => {
    const zone = e.target.closest(".zone");
    if (!zone) return hide();
    if (touch && zone !== current) {
      e.preventDefault();
      show(zone, e.clientX, e.clientY);
    }
  });
  document.addEventListener("click", (e) => { if (current && !map.contains(e.target)) hide(); });
  map.addEventListener("focusin", (e) => {
    // keyboard focus only: a tap focuses the link too, and must not count as the first tap
    const zone = e.target.closest(".zone");
    if (zone && zone.matches(":focus-visible")) show(zone, ...centre(zone));
  });
  map.addEventListener("focusout", hide);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && current) hide(); });
}

// The index page's Previews / List switch: both views are in the page, the cards show without JS; the viewer's choice is
// remembered in localStorage when the browser allows it.
const views = document.querySelector(".view-switch");
if (views) {
  const buttons = [...views.querySelectorAll("button")];
  const panes = [...document.querySelectorAll(".scenarios [data-view]:not(button)")];
  const KEY = "hexchronicles.view";
  const pick = (view, save) => {
    if (!buttons.some((b) => b.dataset.view === view)) view = "previews";
    for (const b of buttons) b.setAttribute("aria-pressed", String(b.dataset.view === view));
    for (const p of panes) p.hidden = p.dataset.view !== view;
    if (save) {
      try { localStorage.setItem(KEY, view); } catch { /* storage blocked: the choice lasts for this page only */ }
    }
  };
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch { /* storage blocked */ }
  pick(saved || "previews", false);
  views.hidden = false;
  for (const b of buttons) b.addEventListener("click", () => pick(b.dataset.view, true));
}

// Hide map / Show map above the world map; remembered in localStorage when the browser allows it.
const mapToggle = document.querySelector(".map-toggle");
const mapFrame = document.getElementById("map-frame");
if (mapToggle && mapFrame) {
  const KEY = "hexchronicles.map";
  const show = (visible, save) => {
    mapFrame.hidden = !visible;
    mapToggle.setAttribute("aria-expanded", String(visible));
    // U+23EC / U+23EB DOWN- / UP-POINTING DOUBLE TRIANGLE with U+FE0E: the text glyphs, not the emoji
    const icon = visible ? "\u23EC" : "\u23EB";
    mapToggle.innerHTML = `<span class="map-toggle-icon" aria-hidden="true">${icon}\uFE0E</span>${visible ? "Hide map" : "Show map"}`;
    if (save) {
      try { localStorage.setItem(KEY, visible ? "shown" : "hidden"); } catch { /* storage blocked: lasts for this page only */ }
    }
  };
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch { /* storage blocked */ }
  show(saved !== "hidden", false);
  mapToggle.hidden = false;
  mapToggle.addEventListener("click", () => show(mapFrame.hidden, true));
  // the masthead's Map link opens a hidden map
  const reveal = () => { if (location.hash === "#map" && mapFrame.hidden) show(true, true); };
  reveal();
  window.addEventListener("hashchange", reveal);
}

// Copy a crypto address to the clipboard; the page works without this.
for (const button of document.querySelectorAll("[data-copy]")) {
  button.hidden = false;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Select and copy";
    }
    setTimeout(() => { button.textContent = "Copy"; }, 2000);
  });
}

// Sort by update, release or historical date, or name, ascending or descending; the page comes sorted by update date,
// newest first. The choice is remembered in localStorage when the browser allows it.
const sortBy = document.getElementById("sort-by");
const sortDir = document.getElementById("sort-dir");
if (sortBy && sortDir) {
  const KEY = "hexchronicles.sort";
  const FIELDS = { updated: "updated", released: "released", year: "year", name: "name" };
  const lists = [...document.querySelectorAll(".scenarios .grid, .scenarios .mod-list")];
  const value = (el, field) => field === "year" ? Number(el.dataset.year) : (el.dataset[field] || "");
  const apply = (field, dir, save) => {
    if (!FIELDS[field]) field = "updated";
    if (dir !== "asc") dir = "desc";
    sortBy.value = field;
    sortDir.dataset.dir = dir;
    sortDir.innerHTML = dir === "asc" ? "\u2191\uFE0E Asc" : "\u2193\uFE0E Desc";
    sortDir.setAttribute("aria-label", dir === "asc" ? "Ascending, click for descending" : "Descending, click for ascending");
    const sign = dir === "asc" ? 1 : -1;
    for (const list of lists) {
      const items = [...list.children];
      items.sort((a, b) => {
        const x = value(a, field), y = value(b, field);
        const c = typeof x === "number" ? x - y : String(x).localeCompare(String(y));
        return sign * c || a.dataset.name.localeCompare(b.dataset.name);
      });
      for (const item of items) list.appendChild(item);
    }
    if (save) {
      try { localStorage.setItem(KEY, `${field}:${dir}`); } catch { /* storage blocked: lasts for this page only */ }
    }
  };
  let saved = "";
  try { saved = localStorage.getItem(KEY) || ""; } catch { /* storage blocked */ }
  const [field, dir] = saved.split(":");
  apply(field || "updated", dir || "desc", false);
  sortBy.closest(".sort-by").hidden = false;
  sortBy.addEventListener("change", () => apply(sortBy.value, sortDir.dataset.dir, true));
  sortDir.addEventListener("click", () => apply(sortBy.value, sortDir.dataset.dir === "asc" ? "desc" : "asc", true));
}
