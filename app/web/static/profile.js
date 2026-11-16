"use strict";
// Data profile for one run: the uploaded table next to cleaned.csv, column by column (GET /api/runs/<id>/profile).

const runId = new URLSearchParams(location.search).get("run") || "";
const P = { data: null, show: "changed" };

if (!runId) fail("Open this page from a finished run (the Profile link next to the output files).");
else {
  getRunFile(`/api/runs/${encodeURIComponent(runId)}/profile`).then(async (r) => {
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || `error ${r.status}`);
    P.data = d;
    render();
  }).catch((err) => fail(`Could not load this profile: ${err.message}`));
}

// The hosted app keeps a run's files in the browser (Cache API, see app.js); the local server serves them.
async function getRunFile(url) {
  try { const hit = window.caches && (await caches.match(url)); if (hit) return hit; } catch { /* fall back to the server */ }
  return fetch(url);
}

function fail(text) {
  $("#lede").textContent = text;
  $("#lede").classList.add("error");
}

const changed = (c) => c.change.cells_changed > 0 || c.change.type_changed || c.change.added || c.change.dropped;

function render() {
  const d = P.data;
  document.title = `DataSage · Profile of ${d.input}`;
  $("#title").textContent = d.input;
  $("#lede").textContent = d.question ? `Question: ${d.question}` : "";
  tiles(d);
  const n = d.columns.filter(changed).length;
  P.show = n ? "changed" : "all";
  $("#filter").append(seg([["changed", `Changed (${n})`], ["all", `All columns (${d.columns.length})`]], P.show,
    (id) => { P.show = id; columns(); }, "Columns to show"));
  $("#colSec").hidden = false;
  columns();
}

function tiles(d) {
  const box = $("#tiles");
  const add = (label, value, sub, good) => {
    const t = el("div", "tile");
    const big = el("span", `t-big${good ? " good" : ""}`, "0"); big.dataset.count = value; big.dataset.fmt = "int";
    t.append(el("span", "t-label", label), big, el("span", "t-sub", sub));
    box.append(t);
  };
  add("Rows after cleaning", d.rows_after, `from ${num(d.rows_before)}; ${num(d.rows_removed)} removed`);
  const cols = d.columns.filter((c) => c.change.cells_changed > 0).length;
  add("Cells changed", d.cells_changed, `in ${cols} column${cols === 1 ? "" : "s"}`, d.cells_changed > 0);
  add("Blank cells after", d.missing_after, `from ${num(d.missing_before)} before`);
  const typed = d.columns.filter((c) => c.change.type_changed).length;
  add("Columns", d.columns_after, typed ? `${typed} changed type` : "no column changed type");
  reveal(box);
}

function columns() {
  const box = $("#cols"); box.textContent = "";
  const list = P.data.columns.filter((c) => P.show === "all" || changed(c));
  if (!list.length) { box.append(el("p", "msg", "No column changed. Switch to All columns to see the profile.")); return; }
  list.forEach((c, i) => {
    const card = column(c); card.style.animationDelay = `${Math.min(i, 8) * 0.05}s`;
    box.append(card); reveal(card);
  });
}

const vis = (v) => v.replace(/^ +| +$/g, (m) => "␣".repeat(m.length));  // show leading and trailing spaces
const pctOf = (x) => `${(x * 100).toFixed(x > 0 && x < 0.01 ? 1 : 0)}%`;

function column(c) {
  const b = c.before, a = c.after, ch = c.change;
  const card = el("article", "card col"); card.setAttribute("aria-label", `Column ${c.name}`);
  const head = el("div", "col-head");
  head.append(el("span", "col-name", c.name));
  const badge = ch.added ? "Added" : ch.dropped ? "Dropped" : ch.cells_changed ? `${num(ch.cells_changed)} cell${ch.cells_changed === 1 ? "" : "s"} changed`
    : ch.type_changed ? "Type changed" : "No change";
  head.append(el("span", `badge ${badge === "No change" ? "" : "changed"}`, badge));
  card.append(head);

  const types = el("div", "types");
  const chip = (side, other) => el("span", `type ${side.type.startsWith("mostly") || (side === b && other && other.type !== side.type) ? "messy" : ""}${side === a && b && b.type !== a.type ? " clean" : ""}`, side.type);
  if (b) types.append(chip(b, a));
  if (b && a && b.type !== a.type) { types.append(el("span", "arrow", "→"), chip(a, b)); }
  if (!b && a) types.append(chip(a, null));
  card.append(types);

  card.append(stats(b, a));

  const vals = el("div", "vals");
  const maxCount = Math.max(1, ...[b, a].filter(Boolean).flatMap((s) => (s.top || []).map((t) => t[1])));
  const histMax = Math.max(1, ...[b, a].filter((s) => s && s.hist).flatMap((s) => s.hist.counts));
  const afterSet = a && a.base === "text" && !a.other ? new Set(a.top.map((t) => t[0])) : null;
  [["Before", b, afterSet], ["After", a, null]].forEach(([label, side, keep]) => {
    const col = el("div");
    col.append(el("div", "vals-t", label));
    if (!side) col.append(el("span", "mx-none", label === "Before" ? "Not in the input" : "Not in cleaned.csv"));
    else if (side.hist) col.append(histogram(side, histMax, label === "After", c.name));
    else if (side.top && side.top.length) col.append(topValues(side, maxCount, keep));
    else col.append(el("span", "mx-none", "No values"));
    vals.append(col);
  });
  card.append(vals);

  [["Not clean", b], ["Still not clean", a]].forEach(([label, side]) => {
    if (!side || !side.unclean) return;
    const u = el("div", "unclean");
    u.append(el("span", null, `${label}: ${num(side.unclean.count)} value${side.unclean.count === 1 ? "" : "s"}, e.g.`));
    side.unclean.examples.forEach(([v]) => u.append(el("code", null, vis(v))));
    card.append(u);
  });

  const what = el("p", "what");
  const parts = [];
  if (ch.edited) parts.push(`${num(ch.edited)} value${ch.edited === 1 ? "" : "s"} rewritten`);
  if (ch.filled) parts.push(`${num(ch.filled)} blank${ch.filled === 1 ? "" : "s"} filled`);
  if (ch.blanked) parts.push(`${num(ch.blanked)} unreadable value${ch.blanked === 1 ? "" : "s"} blanked`);
  if (ch.type_changed) parts.push(`type ${b.type} → ${a.type}`);
  if (ch.added) parts.push("new column in cleaned.csv");
  if (ch.dropped) parts.push("column left out of cleaned.csv");
  const lead = el("b", null, "What changed: ");
  what.append(lead, document.createTextNode(parts.length ? `${parts.join(", ")}.` :
    P.data.rows_removed ? "no cells. Counts differ only because rows were removed." : "nothing."));
  card.append(what);
  return card;
}

function stats(b, a) {
  const g = el("div", "stats"); g.setAttribute("role", "table"); g.setAttribute("aria-label", "Column statistics before and after");
  g.append(el("span", "h", ""), el("span", "h", "Before"), el("span", "h", "After"));
  const row = (k, f) => {
    const x = b ? f(b) : "—", y = a ? f(a) : "—";
    if (x == null && y == null) return;
    g.append(el("span", "k", k), el("span", "v", x ?? "—"), el("span", `v ${x !== y ? "moved" : ""}`, y ?? "—"));
  };
  row("Blank", (s) => `${num(s.missing)} (${pctOf(s.missing_pct)})`);
  row("Distinct", (s) => num(s.distinct));
  row("Range", (s) => (s.min != null ? `${fmtV(s.min, s.base)} to ${fmtV(s.max, s.base)}` : null));
  row("Mean", (s) => (s.mean != null ? num(s.mean, 2) : null));
  return g;
}

function fmtV(v, base) { return base === "date" ? String(v) : num(v, 2); }

function topValues(side, max, keep) {
  const ul = el("ul", "tv");
  side.top.forEach(([v, n]) => {
    const li = el("li", keep && !keep.has(v) ? "gone" : "");
    li.append(el("span", "nm", vis(v)), el("span", "ct", num(n)), bar(n / max));
    li.title = `${v}: ${n} row${n === 1 ? "" : "s"}${keep && !keep.has(v) ? " (gone after cleaning)" : ""}`;
    ul.append(li);
  });
  if (side.other) ul.append(el("li", "more", `${num(side.other)} more rows in ${num(side.distinct - side.top.length)} other values`));
  return ul;
}

function histogram(side, max, after, name) {
  const W = 300, H = 96, B = 18, n = side.hist.counts.length, gap = 2;
  const w = (W - gap * (n - 1)) / n;
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "hist", role: "img",
    "aria-label": `Histogram of ${name}: ${n} bins from ${fmtV(side.hist.edges[0], side.base)} to ${fmtV(side.hist.edges[n], side.base)}` });
  root.append(svg("line", { x1: 0, x2: W, y1: H - B + 0.5, y2: H - B + 0.5, stroke: "#D3D1CA" }));
  side.hist.counts.forEach((c, i) => {
    const h = c ? Math.max(2, (c / max) * (H - B - 4)) : 0;
    const r = svg("rect", { x: i * (w + gap), y: H - B - h, width: w, height: h, rx: 2, fill: after ? "#0F766E" : "#8F8D86" });
    r.style.transitionDelay = `${i * 30}ms`;
    r.append(svg("title", {}, `${fmtV(side.hist.edges[i], side.base)} to ${fmtV(side.hist.edges[i + 1], side.base)}: ${c} row${c === 1 ? "" : "s"}`));
    root.append(r);
  });
  root.append(svg("text", { x: 0, y: H - 3 }, fmtV(side.hist.edges[0], side.base)));
  root.append(svg("text", { x: W, y: H - 3, "text-anchor": "end" }, fmtV(side.hist.edges[n], side.base)));
  return root;
}
