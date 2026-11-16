"use strict";
// Evaluation dashboard: every number comes from GET /api/results (eval/results on disk).

const R = { data: null, group: "devheld" };
const KIND = { final: "final", datasage: "", baseline: "baseline", ablation: "" };
const STEP_TEXT = {
  "datasage": ["Milestone 2", "Agent with checks, fixes, approvals and a validator."],
  "datasage-fix": ["Fix 1", "The prompt says to drop rows that break a rule, not blank them."],
  "datasage-small-fix": ["Fix 2", "The same rule on the smaller, faster 30B model."],
  "datasage-m3": ["Milestone 3, final", "Checks every column the answer uses before answering, and merges spellings into the allowed labels."],
};

fetch("/api/results").then((r) => r.json()).then((d) => {
  if (d.error) throw new Error(d.error);
  R.data = d;
  render();
}).catch((err) => {
  const box = el("p", "msg", `Could not load the results: ${err.message}`);
  $("#tiles").replaceWith(box);
});

const name = (id) => R.data.systems[id]?.label || id;
const kind = (id) => KIND[R.data.systems[id]?.kind] ?? "";
const group = (id) => R.data.groups.find((g) => g.id === id);

function render() {
  const d = R.data;
  const all = group("all");
  const fin = all && all.systems[d.final];
  if (fin) {
    $("#lede").textContent = `${fin.tasks} questions on six splits of tables with planted errors, each with a known right answer. ` +
      "The final system is DataSage at Milestone 3 on the Qwen3-30B model.";
  }
  tiles(all);
  matrix();
  const groups = d.groups.filter((g) => Object.keys(g.systems).length);
  $("#groupSeg").append(seg(groups.map((g) => [g.id, `${g.label} (${g.splits.length})`]), R.group, (id) => { R.group = id; pooled(); }, "Splits to pool"));
  pooled();
  steps();
  ablation();
  failures();
}

// ---------- headline tiles ----------
function tiles(all) {
  const box = $("#tiles");
  const s = all ? all.systems : {};
  const fin = s[R.data.final];
  if (!fin) { box.replaceWith(el("p", "msg", "The final system has no results on all six splits yet.")); return; }
  const base = Object.keys(s).filter((id) => R.data.systems[id].kind === "baseline");
  const best = (key, low) => base.slice().sort((a, b) => (low ? s[a][key] - s[b][key] : s[b][key] - s[a][key]))[0];
  const worstDamage = base.slice().sort((a, b) => s[b].damaged_cells_rows - s[a].damaged_cells_rows)[0];
  const llm = base.find((id) => s[id].tokens_median > 0);
  const add = (label, value, fmt, unit, sub, good) => {
    const t = el("div", "tile");
    t.append(el("span", "t-label", label));
    const big = el("span", `t-big${good ? " good" : ""}`); const n = el("span", null, "0"); n.dataset.count = value; n.dataset.fmt = fmt;
    big.append(n); if (unit) big.append(el("small", null, unit));
    t.append(big);
    const p = el("span", "t-sub"); p.innerHTML = sub; t.append(p);
    box.append(t);
  };
  const ba = best("analysis_accuracy");
  add("Right answers", fin.analysis_accuracy, "pct", "", `Best baseline: <b>${pct(s[ba].analysis_accuracy)}</b>, ${esc(name(ba))}`, true);
  add("Median time per question", fin.latency_median_s, "s", "s", llm ? `${esc(name(llm))}: <b>${secs(s[llm].latency_median_s)}</b>` : "");
  add("Good cells damaged", fin.damaged_cells_rows, "int", "", worstDamage && s[worstDamage].damaged_cells_rows > 0 ?
    `${esc(name(worstDamage))}: <b>${num(s[worstDamage].damaged_cells_rows)}</b>` : "No system damaged cells", true);
  const bh = best("correction_accuracy");
  add("Planted errors handled", fin.correction_accuracy, "pct", "", `Best baseline: <b>${pct(s[bh].correction_accuracy)}</b>, ${esc(name(bh))}`, true);
  reveal(box);
}

// ---------- accuracy matrix ----------
function matrix() {
  const d = R.data, box = $("#matrix");
  const rows = d.order.filter((id) => d.systems[id].kind !== "ablation");
  const head = el("div", "mx-row"); head.style.display = "contents"; head.setAttribute("role", "row");
  const corner = el("div", "mx-h", "System"); corner.setAttribute("role", "columnheader"); head.append(corner);
  d.splits.forEach((s) => {
    const h = el("div", "mx-h"); h.setAttribute("role", "columnheader");
    h.append(el("small", null, s.kind), el("span", null, s.table));
    head.append(h);
  });
  box.append(head);
  let prev = null;
  rows.forEach((id) => {
    const k = d.systems[id].kind;
    if (prev && prev !== k && (prev === "baseline" || k === "final")) box.append(el("div", "mx-break"));
    prev = k;
    const row = el("div", `mx-row ${kind(id)}`); row.style.display = "contents"; row.setAttribute("role", "row");
    const nm = el("div", `mx-name ${kind(id)}`); nm.setAttribute("role", "rowheader"); nm.title = d.systems[id].about;
    const sw = el("i", `sw ${k === "final" ? "final" : k === "baseline" ? "baseline" : "datasage"}`);
    nm.append(sw, el("span", null, name(id)));
    row.append(nm);
    d.splits.forEach((s) => {
      const m = d.per_split[s.id]?.[id];
      const c = el("div", "mx-cell"); c.setAttribute("role", "cell");
      if (!m) { c.append(el("span", "mx-none", "not run")); c.setAttribute("aria-label", `${name(id)}, ${s.label}: not run`); }
      else {
        c.append(el("span", "mx-v", pct(m.analysis_accuracy)), bar(m.analysis_accuracy, kind(id)));
        c.title = `${name(id)} · ${s.label}: ${pct(m.analysis_accuracy)} of ${m.tasks} questions`;
      }
      row.append(c);
    });
    box.append(row);
  });
  reveal(box);
}

// ---------- pooled charts ----------
function pooled() {
  const g = group(R.group);
  const ids = R.data.order.filter((id) => g.systems[id]);
  scatter(g, ids);
  const s = g.systems;
  const pr = $("#pr"); pr.textContent = "";
  ids.forEach((id) => {
    const li = el("li", kind(id));
    li.append(el("span", "nm", name(id)), el("span", "val", `${s[id].detect_precision.toFixed(2)} / ${s[id].detect_recall.toFixed(2)}`));
    const pair = el("div", "pair");
    pair.append(bar(s[id].detect_precision, kind(id) === "final" ? "final" : ""), bar(s[id].detect_recall, "light"));
    pair.setAttribute("aria-label", `precision ${s[id].detect_precision.toFixed(2)}, recall ${s[id].detect_recall.toFixed(2)}`);
    li.append(pair); pr.append(li);
  });
  const hd = $("#handled"); hd.textContent = "";
  ids.slice().sort((a, b) => s[b].correction_accuracy - s[a].correction_accuracy).forEach((id) => {
    const li = el("li", kind(id));
    li.append(el("span", "nm", name(id)), el("span", "val", pct(s[id].correction_accuracy)), bar(s[id].correction_accuracy, kind(id)));
    hd.append(li);
  });
  const dm = $("#damage"); dm.textContent = "";
  const max = Math.max(1, ...ids.map((id) => s[id].damaged_cells_rows));
  ids.slice().sort((a, b) => s[b].damaged_cells_rows - s[a].damaged_cells_rows).forEach((id) => {
    const v = s[id].damaged_cells_rows;
    const li = el("li", kind(id));
    li.append(el("span", "nm", name(id)), el("span", `val ${v ? "warn" : "zero"}`, num(v)), bar(v / max, "bad"));
    dm.append(li);
  });
  [pr, hd, dm].forEach((n) => reveal(n.parentElement));
}

function scatter(g, ids) {
  const box = $("#scatter"); box.textContent = "";
  const W = 760, H = 360, L = 52, Rm = 20, T = 14, B = 44;
  const s = g.systems;
  const xs = ids.map((id) => s[id].latency_median_s).filter((x) => x > 0);
  const lo = Math.floor(Math.log10(Math.min(...xs))), hi = Math.ceil(Math.log10(Math.max(...xs)));
  const X = (v) => L + ((Math.log10(Math.max(v, 10 ** lo)) - lo) / (hi - lo || 1)) * (W - L - Rm);
  const Y = (v) => T + (1 - v) * (H - T - B);
  const root = svg("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img",
    "aria-label": `Scatter plot of answer accuracy against median seconds per question for ${ids.length} systems, pooled over ${g.label}. The final system is at ${pct(s[R.data.final]?.analysis_accuracy)} and ${secs(s[R.data.final]?.latency_median_s)}.` });
  [0, 0.25, 0.5, 0.75, 1].forEach((v) => {
    root.append(svg("line", { x1: L, x2: W - Rm, y1: Y(v), y2: Y(v), class: v ? "grid" : "axis" }));
    root.append(svg("text", { x: L - 10, y: Y(v) + 4, "text-anchor": "end" }, pct(v)));
  });
  for (let p = lo; p <= hi; p++) {
    root.append(svg("line", { x1: X(10 ** p), x2: X(10 ** p), y1: T, y2: H - B, class: "grid" }));
    root.append(svg("text", { x: X(10 ** p), y: H - B + 20, "text-anchor": "middle" }, `${10 ** p >= 1 ? num(10 ** p) : String(10 ** p)} s`));
  }
  root.append(svg("text", { x: (L + W - Rm) / 2, y: H - 4, "text-anchor": "middle" }, "median seconds per question (log scale)"));
  // draw the final system last so it sits on top
  const order = ids.slice().sort((a, b) => (a === R.data.final) - (b === R.data.final));
  const dots = {};
  order.forEach((id, i) => {
    const k = R.data.systems[id].kind;
    const fill = k === "final" ? "#0F766E" : k === "baseline" ? "#8F8D86" : "#3F4048";
    const c = svg("circle", { cx: X(s[id].latency_median_s), cy: Y(s[id].analysis_accuracy), r: k === "final" ? 9 : 7, fill,
      stroke: "#fff", "stroke-width": 2, class: "dot", tabindex: 0, role: "img",
      "aria-label": `${name(id)}: ${pct(s[id].analysis_accuracy)} right, ${secs(s[id].latency_median_s)} per question` });
    c.style.transitionDelay = `${i * 50}ms`;
    c.append(svg("title", {}, `${name(id)}: ${pct(s[id].analysis_accuracy)} right, ${secs(s[id].latency_median_s)} per question`));
    c.addEventListener("mouseenter", () => mark(id, true)); c.addEventListener("mouseleave", () => mark(id, false));
    c.addEventListener("focus", () => mark(id, true)); c.addEventListener("blur", () => mark(id, false));
    dots[id] = c; root.append(c);
  });
  const fin = s[R.data.final];
  if (fin) {
    const x = X(fin.latency_median_s), y = Y(fin.analysis_accuracy);
    const left = x > W * 0.6;
    root.append(svg("text", { x: left ? x - 16 : x + 16, y: y + 4, "text-anchor": left ? "end" : "start", class: "lab final" }, name(R.data.final)));
  }
  const wrap = el("div", "scatter-wrap");
  const list = el("ul", "sc-list"); list.setAttribute("aria-label", "Systems in the chart");
  ids.slice().sort((a, b) => s[b].analysis_accuracy - s[a].analysis_accuracy).forEach((id) => {
    const k = R.data.systems[id].kind;
    const li = el("li", kind(id)); li.dataset.id = id; li.title = R.data.systems[id].about;
    li.append(el("i", `sw ${k === "final" ? "final" : k === "baseline" ? "baseline" : "datasage"}`), el("span", "nm", name(id)),
      el("span", "v", pct(s[id].analysis_accuracy)), el("span", "v t", secs(s[id].latency_median_s)));
    li.addEventListener("mouseenter", () => mark(id, true)); li.addEventListener("mouseleave", () => mark(id, false));
    list.append(li);
  });
  function mark(id, on) {
    list.querySelectorAll("li").forEach((li) => li.classList.toggle("hot", on && li.dataset.id === id));
    Object.entries(dots).forEach(([k, c]) => c.classList.toggle("dim", on && k !== id));
  }
  wrap.append(root, list);
  box.append(wrap);
  reveal(box);
}

// ---------- Milestone 2 to 3 ----------
function steps() {
  const d = R.data, g = group("devheld"), box = $("#steps");
  const ids = d.progression.filter((id) => g && g.systems[id]);
  if (!ids.length) { box.replaceWith(el("p", "msg", "No progression results found.")); return; }
  const n = g.systems[ids[0]].tasks;
  $("#h-steps").nextElementSibling.textContent = `Each step on the same ${n} dev and held-out questions: right answers and median seconds per question.`;
  ids.forEach((id, i) => {
    const m = g.systems[id];
    const st = el("div", `step ${id === d.final ? "final" : ""}`); st.style.animationDelay = `${i * 0.08}s`;
    const [tag, what] = STEP_TEXT[id] || ["", ""];
    st.append(el("span", "s-tag", tag), el("span", "s-name", name(id)), el("span", "s-what", what));
    const nums = el("div", "s-nums");
    const acc = el("span", "s-acc", "0"); acc.dataset.count = m.analysis_accuracy; acc.dataset.fmt = "pct";
    nums.append(acc, el("span", "s-sec", secs(m.latency_median_s)));
    st.append(nums, bar(m.analysis_accuracy, id === d.final ? "final" : ""));
    st.setAttribute("aria-label", `${tag}: ${name(id)}, ${pct(m.analysis_accuracy)} right, ${secs(m.latency_median_s)} per question`);
    box.append(st);
  });
  reveal(box);
}

// ---------- ablations ----------
function ablation() {
  const a = R.data.ablation, box = $("#ablation");
  if (!a.splits.length) { box.append(el("p", "msg", "No ablation results found.")); return; }
  const n = a.by_split[a.splits[0]]?.datasage?.tasks;
  $("#ablNote").textContent = `The same ${n} questions of each dev table, 235B model. Bars: right answers. Grey text: planted errors handled.`;
  const label = { "datasage": "Full agent", "datasage-novalidator": "No validator", "datasage-reject": "Every risky fix rejected" };
  a.splits.forEach((split) => {
    const g = el("div", "abl-g");
    g.append(el("span", "abl-t", R.data.splits.find((s) => s.id === split)?.label || split));
    const ul = el("ul", "hb");
    Object.entries(a.by_split[split]).forEach(([id, m]) => {
      const li = el("li", id === "datasage" ? "" : "");
      const nm = el("span", "nm"); nm.append(el("span", null, label[id] || name(id)), el("span", "sub", ` · ${pct(m.correction_accuracy)} handled`));
      li.title = R.data.systems[id]?.about || "";
      li.append(nm, el("span", "val", pct(m.analysis_accuracy)), bar(m.analysis_accuracy, m.analysis_accuracy < 0.5 ? "bad" : ""));
      ul.append(li);
    });
    g.append(ul); box.append(g);
  });
  reveal(box);
}

// ---------- failures ----------
const CHECKS = { missing: "blank cells", out_of_range: "value ranges", label_variant: "labels", text_number: "numbers stored as text",
  invalid_date: "dates", duplicates: "duplicate rows", cross_column: "formula columns", negative: "negative values" };
function cause(text) {
  let m;
  if ((m = text.match(/^never ran a check for (\w+)$/))) return `Never checked ${CHECKS[m[1]] || m[1]}`;
  if ((m = text.match(/^checked (\w+) on other columns but not the one with the error$/))) return `Checked ${CHECKS[m[1]] || m[1]}, but not on the column with the error`;
  if (text === "rule-violating rows left in the table") return "Left rows that break a rule in the table";
  if (text === "rule-violating rows blanked with set_missing instead of excluded") return "Blanked rows that break a rule instead of dropping them";
  if ((m = text.match(/^stopped early: (\w+)/))) return m[1] === "tool_budget_exhausted" ? "Ran out of tool calls" : `Stopped early (${m[1]})`;
  if (text.startsWith("other")) return "Other (see the trace)";
  return text;
}

function failures() {
  const d = R.data, box = $("#failures");
  const f = d.failures[d.final];
  if (!f) { box.append(el("p", "msg", "No failure analysis for the final system.")); return; }
  const all = group("all")?.systems[d.final];
  const head = el("div", "big-n");
  head.append(el("b", null, String(f.wrong)), el("span", null, all ? `wrong answers out of ${all.tasks} questions` : "wrong answers"));
  box.append(head);
  const max = Math.max(1, ...f.counts.map((c) => c[1]));
  const ul = el("ul", "causes"); ul.setAttribute("aria-label", "Failure causes and how many wrong answers each explains");
  f.counts.forEach(([text, count]) => {
    const li = el("li"); li.append(el("span", null, cause(text)), el("span", "val", String(count)), bar(count / max));
    ul.append(li);
  });
  box.append(ul);
  const m2 = d.failures.datasage, m2g = group("devheld")?.systems.datasage;
  if (m2 && m2g && m2.wrong === m2g.wrong && m2.counts.length) {
    const [text, count] = m2.counts[0];
    box.append(el("p", "note m2", `For comparison, Milestone 2 (235B) had ${m2.wrong} wrong answers out of ${m2g.tasks}; the most common cause was "${cause(text).toLowerCase()}" (${count}).`));
  }
  const det = el("details", "fails"); det.append(el("summary", null, `Show the ${f.tasks.length} questions`));
  const list = el("ul");
  f.tasks.forEach((t) => { const li = el("li"); li.append(el("code", null, t.id), document.createTextNode(` ${t.causes.map(cause).join("; ")}`)); list.append(li); });
  det.append(list); box.append(det);
  reveal(box);
}

function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
