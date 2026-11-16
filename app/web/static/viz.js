"use strict";
// Small helpers shared by the analysis pages: elements, number formats, and motion on reveal.

const $ = (s, root = document) => root.querySelector(s);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
const NS = "http://www.w3.org/2000/svg";
function svg(tag, attrs = {}, text) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
}
const REDUCE = matchMedia("(prefers-reduced-motion: reduce)").matches;
const pct = (x) => (x == null ? "n/a" : `${Math.round(x * 100)}%`);
const num = (x, d = 0) => (x == null ? "n/a" : Number(x).toLocaleString("en-US", { maximumFractionDigits: d, minimumFractionDigits: 0 }));
function secs(x) {
  if (x == null) return "n/a";
  if (x < 0.1) return `${x.toFixed(x < 0.01 ? 3 : 2)} s`;
  return `${x < 10 ? x.toFixed(1) : Math.round(x)} s`;
}

// A bar track whose fill grows to `share` (0..1) when its section scrolls into view.
function bar(share, cls) {
  const b = el("div", "meter"); const i = el("i", cls || "");
  i.dataset.w = String(Math.max(0, Math.min(1, share || 0)));
  b.append(i);
  return b;
}

function countUp(node, target, fmt) {
  if (REDUCE || target == null) { node.textContent = fmt(target); return; }
  let done = false;
  const t0 = performance.now();
  const tick = () => {
    if (done) return;
    const t = Math.min(1, (performance.now() - t0) / 1000);
    node.textContent = fmt(t < 1 ? target * (1 - Math.pow(1 - t, 3)) : target);
    if (t < 1) requestAnimationFrame(tick); else done = true;
  };
  requestAnimationFrame(tick);
  setTimeout(() => { done = true; node.textContent = fmt(target); }, 1200);
}

function grow(scope) {
  scope.querySelectorAll("[data-w]").forEach((i) => { i.style.width = `${Number(i.dataset.w) * 100}%`; });
  scope.querySelectorAll("[data-count]").forEach((n) => {
    if (n.dataset.counted) return;
    n.dataset.counted = "1";
    countUp(n, Number(n.dataset.count), FORMATS[n.dataset.fmt || "int"]);
  });
  scope.classList.remove("pending");
}
const FORMATS = { int: (x) => num(Math.round(x)), pct: (x) => pct(x), s: (x) => (x == null ? "n/a" : x.toFixed(1)) };

const seen = "IntersectionObserver" in window && !REDUCE ? new IntersectionObserver((entries) => {
  entries.forEach((e) => { if (e.isIntersecting) { seen.unobserve(e.target); requestAnimationFrame(() => grow(e.target)); } });
}, { threshold: 0.12 }) : null;

// Call after a block is in the page: bars grow, numbers count up, marks scale in when it is seen.
function reveal(node) {
  node.classList.add("pending");
  if (seen) seen.observe(node); else grow(node);
}

function seg(options, current, onPick, label) {
  const box = el("div", "seg"); box.setAttribute("role", "group"); box.setAttribute("aria-label", label);
  options.forEach(([id, text]) => {
    const b = el("button", null, text); b.type = "button";
    b.setAttribute("aria-pressed", String(id === current));
    b.onclick = () => { box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", "false")); b.setAttribute("aria-pressed", "true"); onPick(id); };
    box.append(b);
  });
  return box;
}
