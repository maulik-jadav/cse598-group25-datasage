"use strict";
// DataSage browser app: upload, watch the run live, approve risky fixes, read the answer.

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
const SVG_OK = '<svg aria-label="Applied" role="img" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#0F766E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 10.5l3.5 3.5 7.5-8"/></svg>';
const SVG_KEPT = '<svg aria-label="Kept as a caveat" role="img" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#B45309" stroke-width="2" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><path d="M10 6.5v4M10 13.5v.01"/></svg>';
const YES = { drop_duplicates: "Remove", exclude_rows: "Drop rows", exclude_where: "Drop rows", set_missing: "Blank", normalize_labels: "Merge",
  parse_dates: "Convert", fill_missing: "Fill", cast_numeric: "Convert", recompute_column: "Recompute", trim_whitespace: "Trim" };
const PHASES = ["rules", "check", "fix", "answer"];

const S = { file: null, rules: null, sample: false, runId: null, es: null, lastSeq: -1, columns: [], rowEls: new Map(),
  cellEls: new Map(), numeric: new Set(), asks: new Map(), phase: null, running: false, ids: [], total: 0, sampleSize: "small" };

// ---------- inputs ----------
const SEP_NAMES = { ";": "semicolon", "\t": "tab", "|": "pipe" };
const ENC_NAMES = { cp1252: "Windows-1252", "latin-1": "Latin-1" };
function setFile(file) {
  S.file = file; S.sample = false; S.sheet = null;
  $("#fileName").textContent = file ? file.name : "Choose file";
  $("#fileChip").classList.toggle("set", !!file);
  $("#fileChip").title = "Choose a CSV or Excel file";
  $("#sheetChip").hidden = true;
  if (file) { $("#question").focus(); inspect(file); }
}
async function inspect(file) {
  try {
    const res = await fetch("/api/inspect", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_name: file.name, file_b64: await toB64(file) }) });
    const info = await res.json();
    if (S.file !== file) return;
    if (!res.ok) { setStatus(info.error || "Could not open the file"); return; }
    if (info.kind === "excel") {
      const sel = $("#sheetSel"); sel.textContent = "";
      info.sheets.forEach((s) => { const o = el("option", null, s); o.value = s; sel.append(o); });
      S.sheet = info.sheets[0] || null;
      $("#sheetChip").hidden = info.sheets.length < 2;
    } else {
      const notes = [SEP_NAMES[info.sep] ? `${SEP_NAMES[info.sep]}-separated` : "", ENC_NAMES[info.encoding] || ""].filter(Boolean);
      if (notes.length) { $("#fileName").textContent = `${file.name} · ${notes.join(", ")}`; $("#fileChip").title = `Read as ${notes.join(", ")}`; }
    }
  } catch { /* the run itself will report a problem with the file */ }
}
$("#sheetSel").addEventListener("change", (e) => { S.sheet = e.target.value; });
$("#fileInput").addEventListener("change", (e) => setFile(e.target.files[0] || null));
$("#rulesInput").addEventListener("change", async (e) => {
  const f = e.target.files[0];
  S.rules = f ? await f.text() : null;
  $("#rulesName").textContent = f ? f.name : "+ rules";
  $("#rulesChip").classList.toggle("set", !!f);
});
const drop = $("#drop");
["dragenter", "dragover"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach((t) => drop.addEventListener(t, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", (e) => {
  for (const f of e.dataTransfer.files) {
    if (/\.json$/i.test(f.name)) { $("#rulesInput").files = e.dataTransfer.files; f.text().then((t) => { S.rules = t; $("#rulesName").textContent = f.name; $("#rulesChip").classList.add("set"); }); }
    else if (/\.(csv|xlsx)$/i.test(f.name)) setFile(f);
  }
});
document.querySelectorAll("[data-sample]").forEach((b) => b.addEventListener("click", async () => {
  const size = b.dataset.sample;
  const s = await (await fetch(`/api/sample?size=${size}`)).json();
  S.sample = size; S.file = null; $("#sheetChip").hidden = true;
  $("#fileName").textContent = s.input; $("#fileChip").classList.add("set");
  $("#rulesName").textContent = s.rules; $("#rulesChip").classList.add("set");
  $("#question").value = s.question;
  start();
}));
$("#askForm").addEventListener("submit", (e) => { e.preventDefault(); if (S.running && S.runId) stop(); else start(); });
async function stop() {
  $("#runBtn").disabled = true; setStatus("Stopping");
  try { await fetch(`/api/runs/${S.runId}/cancel`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }); } catch { /* the run ends on its own */ }
}
// One id per browser, so a new run only replaces this browser's earlier run.
const CLIENT_ID = (() => {
  try { let id = localStorage.getItem("datasage-client"); if (!id) { id = crypto.randomUUID(); localStorage.setItem("datasage-client", id); } return id; }
  catch { return (crypto.randomUUID && crypto.randomUUID()) || String(Math.random()).slice(2); }
})();

const toB64 = (file) => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1] || ""); r.onerror = rej; r.readAsDataURL(file); });

// ---------- run ----------
async function start() {
  const question = $("#question").value.trim();
  if (!S.sample && !S.file) { $("#fileChip").animate([{ transform: "translateX(0)" }, { transform: "translateX(-4px)" }, { transform: "translateX(4px)" }, { transform: "translateX(0)" }], { duration: 260 }); $("#fileInput").click(); return; }
  if (!question) { $("#question").focus(); return; }
  const mode = (document.querySelector('input[name="mode"]:checked') || {}).value || "ask";
  const body = S.sample ? { sample: S.sample, question, client_id: CLIENT_ID, approve: mode } : { question, file_name: S.file.name, file_b64: await toB64(S.file), rules_text: S.rules, sheet: S.sheet, client_id: CLIENT_ID, approve: mode };
  setRunning(true); setStatus("Uploading");
  let res;
  try { res = await fetch("/api/runs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
  catch { return fail("Could not reach the DataSage server."); }
  const data = await res.json();
  if (!res.ok) return fail(data.error || "Something went wrong.");
  reset(); S.runId = data.run_id;
  $("#empty").hidden = true; $("#work").hidden = false;
  listen();
}

function listen() {
  if (S.es) S.es.close();
  const es = new EventSource(`/api/runs/${S.runId}/events`);
  S.es = es;
  es.onmessage = (m) => {
    const ev = JSON.parse(m.data);
    if (ev.seq <= S.lastSeq) return;
    S.lastSeq = ev.seq;
    handle(ev);
  };
  es.onerror = () => { if (!S.running) es.close(); };
}

function handle(ev) {
  if (ev.type === "start") buildTable(ev);
  else if (ev.type === "step") step(ev);
  else if (ev.type === "approval") showAsk(ev);
  else if (ev.type === "approval_closed") closeAsk(ev.id);
  else if (ev.type === "done") finish(ev);
  else if (ev.type === "error") fail(ev.message);
}

function reset() {
  S.lastSeq = -1; S.rowEls.clear(); S.cellEls.clear(); S.asks.clear(); S.phase = null; S.ids = []; S.total = 0;
  $("#table").textContent = ""; $("#banner").hidden = true; $("#banner").textContent = "";
  $("#health").hidden = true; $("#counts").textContent = ""; $("#more").hidden = true; $("#toasts").textContent = "";
  document.querySelectorAll(".tab").forEach((b) => { if (b.dataset.view !== "table") { b.disabled = true; b.classList.remove("ready"); } });
  showView("table");
  document.querySelectorAll(".rail li").forEach((li) => li.classList.remove("active", "done"));
}

function setRunning(on) {
  S.running = on;
  $("#runBtn").disabled = false;
  $("#runBtn").textContent = on ? "Stop" : (S.runId ? "Run again" : "Run");
  $("#runBtn").classList.toggle("stop", on);
  $("#spin").hidden = !on;
}
function setStatus(t) { $("#status").textContent = t; $("#status").classList.remove("error"); }
function fail(msg) { setRunning(false); setStatus(msg); $("#status").classList.add("error"); if (S.es) S.es.close(); }

// ---------- views ----------
const FILE_INFO = {
  "cleaned.csv": { title: "Cleaned table", text: "Your table after the fixes, ready to use in Excel or any tool. Your original file is not changed." },
  "report.md": { title: "Report", text: "A readable summary: the problems found, every change with who approved it, and the answer." },
  "replay.py": { title: "Replay script", text: "Python that repeats the same fixes on this file without the AI, so anyone can check or rerun them." },
  "trace.jsonl": { title: "Step log", text: "Every step the agent took, in order. For auditing or debugging; you rarely need it." },
};
function showView(view) {
  document.querySelectorAll(".tab").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.view === view)));
  document.querySelectorAll(".view").forEach((v) => {
    const on = v.id === `view-${view}`;
    if (on && v.hidden) { v.hidden = false; v.classList.remove("view-in"); void v.offsetWidth; v.classList.add("view-in"); }
    else if (!on) v.hidden = true;
  });
  if (view === "answer") $('.tab[data-view="answer"]').classList.remove("ready");
}
document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => showView(b.dataset.view)));

function toast(text) {
  const t = el("div", "toast");
  t.append(el("span", "toast-tag", "Auto-approved"), el("span", null, text));
  $("#toasts").append(t);
  setTimeout(() => { t.classList.add("leaving"); setTimeout(() => t.remove(), 400); }, 3200);
}

// ---------- table ----------
function makeRow(id, cells) {
  const row = el("div", "row"); row.setAttribute("role", "row"); row.dataset.id = id;
  row.append(el("div", "cell idx", String(id)));
  S.columns.forEach((c) => {
    const v = cells[c] && typeof cells[c] === "object" ? cells[c].text : (cells[c] ?? "");
    const cell = el("div", "cell" + (S.numeric.has(c) ? " num" : "") + (v === "" ? " blank" : ""));
    cell.setAttribute("role", "cell");
    cell.append(el("span", null, vis(v)));
    cell.dataset.text = v; cell.dataset.state = "";
    row.append(cell); S.cellEls.set(`${id}|${c}`, cell);
  });
  S.rowEls.set(id, row);
  return row;
}

function insertRow(id, cells) {
  const row = makeRow(id, cells);
  row.classList.add("arrive");
  const next = S.ids.find((x) => x > id);
  if (next !== undefined) S.rowEls.get(next).before(row); else $("#table").append(row);
  S.ids.push(id); S.ids.sort((a, b) => a - b);
}

function refreshGaps() {
  const table = $("#table");
  table.querySelectorAll(".gap").forEach((g) => g.remove());
  let prev = -1;
  for (const id of S.ids) {
    if (id - prev > 1) S.rowEls.get(id).before(gap(id - prev - 1));
    prev = id;
  }
  if (S.total - 1 > prev) table.append(gap(S.total - 1 - prev, true));
}
function gap(n, end) {
  const g = el("div", "gap", `⋯ ${n.toLocaleString("en-US")} ${end ? "more " : ""}row${n === 1 ? "" : "s"}`);
  g.setAttribute("aria-hidden", "true");
  return g;
}

function buildTable(ev) {
  S.columns = ev.columns;
  S.numeric = new Set(ev.columns.filter((c) => ev.rows.length && ev.rows.every((r) => r.cells[c] === "" || !isNaN(Number(r.cells[c])))));
  const table = $("#table");
  const widths = ev.columns.map((c) => {
    const longest = Math.max(...ev.rows.map((r) => String(r.cells[c]).length), 1);
    return Math.round(Math.min(280, Math.max(64, longest * 8.6 + 36, c.length * 7.4 + 36)));
  });
  table.style.setProperty("--cols", "64px " + widths.map((w) => `minmax(${w}px, 1fr)`).join(" "));
  table.style.minWidth = `${64 + widths.reduce((a, b) => a + b, 0)}px`;
  const head = el("div", "row head"); head.setAttribute("role", "row");
  head.append(el("div", "cell idx", "#"));
  ev.columns.forEach((c) => { const h = el("div", "cell" + (S.numeric.has(c) ? " num" : ""), c); h.setAttribute("role", "columnheader"); head.append(h); });
  table.append(head);
  ev.rows.forEach((r) => { const row = makeRow(r.id, r.cells); table.append(row); S.ids.push(r.id); });
  S.total = ev.total_rows;
  refreshGaps();
  if (ev.total_rows > ev.rows.length) { $("#more").hidden = false; $("#more").textContent = `Showing the first ${ev.rows.length} rows, plus every row with a problem as it is found. The agent works on all ${ev.total_rows.toLocaleString("en-US")}.`; }
  setStatus("Reading the table");
}

function applyTable(t) {
  if (!t) return;
  let added = false;
  for (const [id, r] of Object.entries(t.rows)) {
    if (!S.rowEls.has(Number(id))) { insertRow(Number(id), r.cells); added = true; }
  }
  if (added) refreshGaps();
  for (const [id, r] of Object.entries(t.rows)) {
    const row = S.rowEls.get(Number(id));
    if (!row) continue;
    row.classList.toggle("removed", r.state === "removed");
    row.classList.toggle("flag", r.state === "flag");
    row.classList.toggle("kept", r.state === "kept");
    for (const [col, c] of Object.entries(r.cells)) {
      const cell = S.cellEls.get(`${id}|${col}`);
      if (!cell) continue;
      if (cell.dataset.text !== c.text) {
        cell.dataset.text = c.text;
        const span = el("span", "new", vis(c.text));
        cell.replaceChildren(span);
        cell.classList.toggle("blank", c.text === "");
      }
      if (cell.dataset.state !== c.state) {
        cell.classList.remove("flag", "fixed", "kept");
        if (c.state) cell.classList.add(c.state);
        cell.dataset.state = c.state;
      }
    }
  }
}

// ---------- progress ----------
function step(ev) {
  applyTable(ev.table);
  setPhase(ev.phase);
  setStatus(ev.refused ? "Coverage check found open problems, going back to fix them" : ev.label);
  const c = ev.counts;
  $("#counts").textContent = `${c.checks} check${c.checks === 1 ? "" : "s"} · ${c.fixes} fix${c.fixes === 1 ? "" : "es"} applied`;
}
function setPhase(p) {
  const i = PHASES.indexOf(p);
  if (i < 0) return;
  const cur = Math.max(i, PHASES.indexOf(S.phase));
  S.phase = PHASES[cur];
  document.querySelectorAll(".rail li").forEach((li, k) => { li.classList.toggle("done", k < cur); li.classList.toggle("active", k === cur); });
}

// ---------- approvals ----------
function showAsk(ev) {
  setPhase("fix");
  if (ev.auto) { toast(ev.summary); return; }
  setStatus("Waiting for you");
  const wrap = el("div", "ask"); wrap.dataset.id = ev.id;
  const card = el("div", "ask-card"); card.setAttribute("role", "group"); card.setAttribute("aria-label", ev.title);
  const text = el("div", "ask-text");
  text.append(el("span", "ask-title", ev.title));
  text.append(el("span", "ask-sub", `${cap(ev.risk)} risk · ${ev.summary}`));
  const ex = examplesBlock(ev.examples);
  if (ev.reason || ex) {
    const more = el("div", "ask-more"); more.id = `more-${ev.id}`;
    const inner = el("div", "ask-more-inner");
    if (ev.reason) inner.append(el("span", "ask-reason", ev.reason));
    if (ex) inner.append(ex);
    more.append(inner);
    const n = ev.examples && ev.examples.rows ? ev.examples.rows.length + (ev.examples.more || 0) : 0;
    const toggle = el("button", "ask-toggle", n ? `Details · ${n} row${n === 1 ? "" : "s"}` : "Details");
    toggle.type = "button"; toggle.setAttribute("aria-expanded", "false"); toggle.setAttribute("aria-controls", more.id);
    toggle.onclick = () => {
      const open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      more.classList.toggle("open", open);
    };
    text.append(toggle, more);
  }
  const no = el("button", "ghost", "Keep as is"); no.type = "button";
  const yes = el("button", "btn primary", YES[ev.tool] || "Apply"); yes.type = "button";
  no.onclick = () => answer(ev.id, false, wrap); yes.onclick = () => answer(ev.id, true, wrap);
  card.append(text, no, yes); wrap.append(card);
  const targets = (ev.rows || []).map((r) => S.rowEls.get(r)).filter(Boolean);
  targets.forEach((r) => r.classList.add("target"));
  wrap._targets = targets;
  const anchor = targets[0] || firstFlagged(ev.column);
  if (anchor) anchor.after(wrap); else { $("#banner").hidden = false; $("#banner").append(wrap); }
  S.asks.set(ev.id, wrap);
  const go = el("button", "go-ask", "Go to question"); go.type = "button";
  go.onclick = () => { wrap.scrollIntoView({ block: "center", behavior: "smooth" }); yes.focus({ preventScroll: true }); };
  $("#status").replaceChildren(document.createTextNode("Waiting for you · "), go);
  wrap.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  yes.focus({ preventScroll: true });
}
function rowChip(id) {
  const chip = el("button", "ex-id", `#${id}`); chip.type = "button"; chip.title = "Show this row in the table";
  chip.onclick = () => jumpTo(id);
  return chip;
}
function examplesBlock(ex) {
  if (!ex || !ex.rows || !ex.rows.length) return null;
  const box = el("div", "ex");
  ex.rows.forEach((r) => {
    const line = el("div", "ex-row");
    if (ex.kind === "duplicates") {
      line.append(rowChip(r.id), el("span", "ex-note", "repeats"), r.same_as != null ? rowChip(r.same_as) : el("span", "ex-note", "an earlier row"));
      line.append(el("span", "ex-vals", ex.columns.map((c) => r.cells[c] || "—").join("  ·  ")));
    } else if (ex.kind === "remove") {
      line.append(rowChip(r.id));
      const vals = el("span", "ex-cells");
      const bad = r.problems || {};
      ex.columns.forEach((c) => {
        if (bad[c]) { const b = el("span", "ex-bad"); b.title = bad[c]; b.append(el("span", "ex-col", c), document.createTextNode(` ${r.cells[c] || "—"}`)); vals.append(b); }
      });
      vals.append(el("span", "ex-vals", ex.columns.filter((c) => !bad[c]).map((c) => r.cells[c] || "—").join("  ·  ")));
      line.append(vals);
    } else {
      line.append(rowChip(r.id));
      const parts = el("span", "ex-changes");
      r.changes.forEach((c) => {
        const item = el("span", "ex-change");
        item.append(el("span", "ex-col", c.column), el("span", "ex-before", vis(c.before)), el("span", "ex-arrow", "→"), el("span", "ex-after", vis(c.after)));
        parts.append(item);
      });
      if (r.inputs && r.inputs.length) parts.append(el("span", "ex-note", "from " + r.inputs.map((i) => `${i.column} ${i.value}`).join(", ")));
      line.append(parts);
    }
    box.append(line);
  });
  if (ex.more) box.append(el("div", "ex-more", `+ ${ex.more} more row${ex.more === 1 ? "" : "s"}`));
  return box;
}
function jumpTo(id) {
  const row = S.rowEls.get(id);
  if (!row) return;
  row.scrollIntoView({ block: "center", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  row.classList.remove("spot"); void row.offsetWidth; row.classList.add("spot");
  setTimeout(() => row.classList.remove("spot"), 1600);
}

function firstFlagged(column) {
  if (!column) return null;
  for (const [key, cell] of S.cellEls) if (key.endsWith(`|${column}`) && cell.classList.contains("flag")) return cell.parentElement;
  return null;
}
async function answer(id, value, wrap) {
  wrap.querySelectorAll("button").forEach((b) => (b.disabled = true));
  setStatus(value ? "Applying" : "Keeping it as a caveat");
  await fetch(`/api/runs/${S.runId}/approve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id, answer: value }) });
}
function closeAsk(id) {
  if (!S.asks.has(id)) return;
  const wrap = S.asks.get(id);
  if (!wrap) return;
  S.asks.delete(id);
  (wrap._targets || []).forEach((r) => r.classList.remove("target"));
  wrap.classList.add("leaving");
  setTimeout(() => { wrap.remove(); if (!$("#banner").children.length) $("#banner").hidden = true; }, 300);
}

// ---------- answer ----------
function finish(ev) {
  applyTable(ev.table);
  setRunning(false);
  if (S.es) S.es.close();
  document.querySelectorAll(".rail li").forEach((li) => { li.classList.remove("active"); li.classList.add("done"); });
  setStatus(ev.finished ? `Done in ${ev.seconds} s` : ev.stop_reason === "cancelled" ? "Stopped" : `Stopped: ${ev.stop_reason}`);
  document.querySelectorAll(".tab").forEach((b) => { b.disabled = false; });
  $('.tab[data-view="answer"]').classList.add("ready");
  const a = ev.analysis;
  $("#aTitle").textContent = a ? `${cap(a.agg)} of ${a.metric}${a.group_by && a.group_by.length ? " by " + a.group_by.join(", ") : ""}` : "No answer";
  $("#aMeta").textContent = a && a.rows_used != null ? `${Number(a.rows_used).toLocaleString("en-US")} rows used` : "";
  renderGroups(ev.answer);
  const log = $("#aLog"); log.textContent = "";
  ev.changes.forEach((c, i) => {
    const li = el("li"); li.style.animationDelay = `${0.6 + i * 0.08}s`;
    li.innerHTML = c.applied ? SVG_OK : SVG_KEPT;
    const body = el("span", "log-text"); body.append(el("span", null, plain(c.text)));
    if (c.how) body.append(el("span", "log-how", c.how));
    li.append(body);
    log.append(li);
  });
  if (!ev.changes.length) log.append(el("li", null, "No changes were needed."));
  $("#aSummary").textContent = ev.summary || "";
  const files = $("#aFiles"); files.textContent = "";
  ev.files.forEach((f) => {
    const info = FILE_INFO[f] || { title: f, text: "" };
    const li = el("li", "file");
    const text = el("div", "file-text");
    text.append(el("span", "file-title", info.title), el("span", "file-name", f), el("span", "file-desc", info.text));
    const link = el("a", "ghost small", "Download"); link.href = `/api/runs/${S.runId}/files/${f}`; link.setAttribute("download", f);
    link.setAttribute("aria-label", `Download ${f}`);
    li.append(text, link); files.append(li);
  });
  const prof = el("li", "file");
  const ptext = el("div", "file-text");
  ptext.append(el("span", "file-title", "Column profile"), el("span", "file-name", "opens a new tab"),
    el("span", "file-desc", "Each column before and after cleaning: type, blanks, top values or a histogram, and what changed."));
  const open = el("a", "ghost small", "Open"); open.href = `/profile?run=${S.runId}`; open.target = "_blank"; open.rel = "noopener";
  prof.append(ptext, open); files.append(prof);
  renderHealth(ev.health, ev.answer);
  const asked = ev.mode === "auto" ? "approved automatically" : `${ev.approvals} question${ev.approvals === 1 ? "" : "s"} to you`;
  $("#aStats").textContent = `${ev.tool_calls} tool calls · ${asked} · ${ev.model}`;
  if (ev.finished) setTimeout(() => showView("answer"), matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 700);
}

function renderHealth(h, after) {
  const box = $("#health"); box.textContent = "";
  if (!h) { box.hidden = true; return; }
  box.hidden = false;
  const grid = el("div", "h-grid");

  const rows = el("div", "h-card");
  rows.append(el("span", "h-label", "Rows"));
  const big = el("div", "h-big");
  big.append(el("span", null, h.rows_before.toLocaleString("en-US")), el("span", "h-arrow", "→"), el("span", null, h.rows_after.toLocaleString("en-US")));
  rows.append(big);
  const why = h.removed.map((r) => `${r.count} ${r.count === 1 && r.why === "duplicates" ? "duplicate" : r.why}`).join(" · ");
  rows.append(el("span", "h-sub", why ? `Removed: ${why}` : "No rows removed"));
  rows.append(el("span", "h-sub", `${h.cells_changed.toLocaleString("en-US")} cell${h.cells_changed === 1 ? "" : "s"} changed`));
  grid.append(rows);

  const tally = { fixed: 0, kept: 0, "not needed": 0 };
  h.issues.forEach((i) => { tally[i.status] = (tally[i.status] || 0) + 1; });
  const out = el("div", "h-card");
  out.append(el("span", "h-label", "Outcome"));
  const nums = el("div", "h-tally");
  [["fixed", "fixed"], ["kept", "kept as caveat"], ["not needed", "not needed"]].forEach(([k, txt]) => {
    const cell = el("div", "h-t");
    cell.append(el("span", `h-tn ${k.replace(" ", "-")}`, String(tally[k] || 0)), el("span", "h-sub", txt));
    nums.append(cell);
  });
  out.append(nums);
  out.append(el("span", "h-sub", "Problems in columns the question doesn't use are left alone."));
  grid.append(out);

  const probs = el("div", "h-card h-wide");
  probs.append(el("span", "h-label", "Problems found"));
  const list = el("ul", "h-list");
  const maxCount = Math.max(1, ...h.issues.map((i) => i.count));
  h.issues.forEach((i, k) => {
    const li = el("li", "h-item"); li.style.animationDelay = `${0.1 + k * 0.05}s`;
    li.append(el("span", `h-dot ${i.status.replace(" ", "-")}`));
    const name = el("span", "h-name");
    if (i.column === "*") name.append(el("b", null, cap(i.name)));
    else name.append(el("b", null, i.column), document.createTextNode(` ${i.name}`));
    li.append(name);
    const bar = el("span", "h-bar"); const fillEl = el("span", "h-fill"); bar.append(fillEl); li.append(bar);
    requestAnimationFrame(() => requestAnimationFrame(() => { fillEl.style.width = `${Math.max(6, Math.round((i.count / maxCount) * 100))}%`; }));
    li.append(el("span", "h-count", String(i.count)));
    li.append(el("span", `h-status ${i.status.replace(" ", "-")}`, i.status === "kept" ? "kept as caveat" : i.status));
    list.append(li);
  });
  if (!h.issues.length) list.append(el("li", "h-sub", "No problems found."));
  probs.append(list);
  grid.append(probs);

  const impact = el("div", "h-card h-wide");
  impact.append(el("span", "h-label", "Answer before and after cleaning"));
  const raw = h.raw_answer || {};
  if (raw.error) {
    impact.append(el("p", "h-note", `Before cleaning it could not be computed: ${raw.error}.`));
  }
  if (after && typeof after === "object") {
    const tbl = el("div", "h-table");
    const head = el("div", "h-tr h-th");
    ["Group", "Before", "After", "Change"].forEach((x, n) => head.append(el("span", n === 0 ? "h-group" : null, x)));
    tbl.append(head);
    const before = raw.result || {};
    const keys = [...new Set([...Object.keys(after), ...Object.keys(before)])];
    keys.slice(0, 12).forEach((k) => {
      const tr = el("div", "h-tr");
      const b = before[k], a = after[k];
      const fmt = (x) => (typeof x === "number" ? x.toLocaleString("en-US", { maximumFractionDigits: 2 }) : "—");
      let change = "—", cls = "";
      if (typeof a === "number" && typeof b === "number" && b !== 0) { const d = ((a - b) / Math.abs(b)) * 100; change = `${d > 0 ? "+" : ""}${d.toFixed(1)}%`; cls = Math.abs(d) >= 0.05 ? "moved" : ""; }
      else if (typeof a !== "number" && typeof b === "number") { change = "merged away"; cls = "moved"; }
      else if (typeof a === "number" && raw.result && typeof b !== "number") { change = "new group"; }
      tr.append(el("span", "h-group", k), el("span", null, raw.error ? "—" : fmt(b)), el("span", null, fmt(a)), el("span", `h-change ${cls}`, raw.error ? "—" : change));
      tbl.append(tr);
    });
    impact.append(tbl);
  }
  grid.append(impact);
  box.append(grid);
  box.style.animation = "none"; void box.offsetWidth; box.style.animation = "";
}

function renderGroups(result) {
  const box = $("#aGroups"); box.textContent = "";
  let entries;
  if (result && typeof result === "object") entries = Object.entries(result);
  else if (result != null) entries = [["Result", result]];
  else { box.append(el("p", "a-meta", "The agent did not produce an answer.")); return; }
  const numeric = entries.filter(([, v]) => typeof v === "number");
  const max = Math.max(1, ...numeric.map(([, v]) => Math.abs(v)));
  entries.slice(0, 12).forEach(([k, v]) => {
    const g = el("div", "g");
    const top = el("div", "g-top");
    top.append(el("span", "g-name", k));
    const val = el("span", "g-val", typeof v === "number" ? "0" : String(v));
    top.append(val); g.append(top);
    if (typeof v === "number") {
      const track = el("div", "track"); const fill = el("div", "fill"); track.append(fill); g.append(track);
      requestAnimationFrame(() => requestAnimationFrame(() => { fill.style.width = `${Math.round((Math.abs(v) / max) * 100)}%`; }));
      countUp(val, v);
    }
    box.append(g);
  });
  if (entries.length > 12) box.append(el("p", "a-meta", `and ${entries.length - 12} more groups in report.md`));
}

function countUp(node, target) {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fmt = (x) => x.toLocaleString("en-US", { maximumFractionDigits: Number.isInteger(target) ? 0 : 2 });
  if (reduce) { node.textContent = fmt(target); return; }
  let done = false;
  const t0 = performance.now();
  const tick = () => {
    if (done) return;
    const t = Math.min(1, Math.max(0, (performance.now() - t0) / 1100));
    const k = 1 - Math.pow(1 - t, 3);
    node.textContent = fmt(t < 1 ? Math.round(target * k * 100) / 100 : target);
    if (t < 1) requestAnimationFrame(tick); else done = true;
  };
  requestAnimationFrame(tick);
  setTimeout(() => { done = true; node.textContent = fmt(target); }, 1300);  // final number even if frames stall
}

const vis = (v) => (v === "" || v == null ? "—" : String(v).replace(/^ +| +$/g, (m) => "␣".repeat(m.length)));  // stray spaces made visible
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : "");
function plain(text) {
  return text.replace(/^drop_duplicates: /, "").replace(/^normalize_labels: /, "").replace(/^exclude_rows: /, "")
    .replace(/^parse_dates: /, "").replace(/^set_missing: /, "").replace(/^trim_whitespace: /, "").replace(/^cast_numeric: /, "")
    .replace(/^fill_missing: /, "").replace(/^recompute_column: /, "")
    .replace(/\b(\d+) ([\w ]*?)\(s\)/g, (_, n, w) => `${n} ${w}${n === "1" ? "" : "s"}`)
    .replace(/^./, (c) => c.toUpperCase());
}
