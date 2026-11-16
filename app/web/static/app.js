"use strict";
// DataSage browser app: upload, watch the run live, approve risky fixes, read the answer.

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
const SVG_OK = '<svg aria-label="Applied" role="img" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#0F766E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 10.5l3.5 3.5 7.5-8"/></svg>';
const SVG_KEPT = '<svg aria-label="Kept as a caveat" role="img" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#B45309" stroke-width="2" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><path d="M10 6.5v4M10 13.5v.01"/></svg>';
const YES = { drop_duplicates: "Remove", exclude_rows: "Drop rows", set_missing: "Blank", normalize_labels: "Merge",
  parse_dates: "Convert", fill_missing: "Fill", cast_numeric: "Convert", recompute_column: "Recompute", trim_whitespace: "Trim" };
const PHASES = ["rules", "check", "fix", "answer"];

const S = { file: null, rules: null, sample: false, runId: null, es: null, lastSeq: -1, columns: [], rowEls: new Map(),
  cellEls: new Map(), numeric: new Set(), asks: new Map(), phase: null, running: false };

// ---------- inputs ----------
function setFile(file) {
  S.file = file; S.sample = false;
  $("#fileName").textContent = file ? file.name : "Choose file";
  $("#fileChip").classList.toggle("set", !!file);
  if (file) $("#question").focus();
}
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
$("#sampleBtn").addEventListener("click", async () => {
  const s = await (await fetch("/api/sample")).json();
  S.sample = true; S.file = null;
  $("#fileName").textContent = s.input; $("#fileChip").classList.add("set");
  $("#rulesName").textContent = s.rules; $("#rulesChip").classList.add("set");
  $("#question").value = s.question;
  start();
});
$("#askForm").addEventListener("submit", (e) => { e.preventDefault(); start(); });

const toB64 = (file) => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1] || ""); r.onerror = rej; r.readAsDataURL(file); });

// ---------- run ----------
async function start() {
  const question = $("#question").value.trim();
  if (!S.sample && !S.file) { $("#fileChip").animate([{ transform: "translateX(0)" }, { transform: "translateX(-4px)" }, { transform: "translateX(4px)" }, { transform: "translateX(0)" }], { duration: 260 }); $("#fileInput").click(); return; }
  if (!question) { $("#question").focus(); return; }
  const body = S.sample ? { sample: true, question } : { question, file_name: S.file.name, file_b64: await toB64(S.file), rules_text: S.rules };
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
  S.lastSeq = -1; S.rowEls.clear(); S.cellEls.clear(); S.asks.clear(); S.phase = null;
  $("#table").textContent = ""; $("#banner").hidden = true; $("#banner").textContent = "";
  $("#answer").hidden = true; $("#waiting").hidden = false; $("#counts").textContent = ""; $("#more").hidden = true;
  document.querySelectorAll(".rail li").forEach((li) => li.classList.remove("active", "done"));
}

function setRunning(on) {
  S.running = on;
  $("#runBtn").disabled = on;
  $("#runBtn").textContent = on ? "Running" : (S.runId ? "Run again" : "Run");
  $("#spin").hidden = !on;
}
function setStatus(t) { $("#status").textContent = t; $("#status").classList.remove("error"); }
function fail(msg) { setRunning(false); setStatus(msg); $("#status").classList.add("error"); if (S.es) S.es.close(); }

// ---------- table ----------
function buildTable(ev) {
  S.columns = ev.columns;
  S.numeric = new Set(ev.columns.filter((c) => ev.rows.length && ev.rows.every((r) => r.cells[c] === "" || !isNaN(Number(r.cells[c])))));
  const table = $("#table");
  const widths = ev.columns.map((c) => {
    const longest = Math.max(...ev.rows.map((r) => String(r.cells[c]).length), 1);
    return Math.round(Math.min(280, Math.max(64, longest * 8.6 + 36, c.length * 7.4 + 36)));
  });
  table.style.setProperty("--cols", "44px " + widths.map((w) => `minmax(${w}px, 1fr)`).join(" "));
  table.style.minWidth = `${44 + widths.reduce((a, b) => a + b, 0)}px`;
  const head = el("div", "row head"); head.setAttribute("role", "row");
  head.append(el("div", "cell idx", "#"));
  ev.columns.forEach((c) => { const h = el("div", "cell" + (S.numeric.has(c) ? " num" : ""), c); h.setAttribute("role", "columnheader"); head.append(h); });
  table.append(head);
  ev.rows.forEach((r) => {
    const row = el("div", "row"); row.setAttribute("role", "row"); row.dataset.id = r.id;
    row.append(el("div", "cell idx", String(r.id)));
    ev.columns.forEach((c) => {
      const v = r.cells[c];
      const cell = el("div", "cell" + (S.numeric.has(c) ? " num" : "") + (v === "" ? " blank" : ""));
      cell.setAttribute("role", "cell");
      const span = el("span", null, v === "" ? "—" : v); cell.append(span);
      cell.dataset.text = v; cell.dataset.state = "";
      row.append(cell); S.cellEls.set(`${r.id}|${c}`, cell);
    });
    table.append(row); S.rowEls.set(r.id, row);
  });
  if (ev.total_rows > ev.rows.length) { $("#more").hidden = false; $("#more").textContent = `Showing the first ${ev.rows.length} of ${ev.total_rows} rows. The agent works on all of them.`; }
  setStatus("Reading the table");
}

function applyTable(t) {
  if (!t) return;
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
        const span = el("span", "new", c.text === "" ? "—" : c.text);
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
  setStatus("Waiting for you");
  const wrap = el("div", "ask"); wrap.dataset.id = ev.id;
  const card = el("div", "ask-card"); card.setAttribute("role", "group"); card.setAttribute("aria-label", ev.title);
  const text = el("div", "ask-text");
  text.append(el("span", "ask-title", ev.title));
  text.append(el("span", "ask-sub", `${cap(ev.risk)} risk · ${ev.summary}`));
  if (ev.reason) text.append(el("span", "ask-reason", ev.reason));
  const no = el("button", "ghost", "Keep as is"); no.type = "button";
  const yes = el("button", "btn primary", YES[ev.tool] || "Apply"); yes.type = "button";
  no.onclick = () => answer(ev.id, false, wrap); yes.onclick = () => answer(ev.id, true, wrap);
  card.append(text, no, yes); wrap.append(card);
  const targets = (ev.rows || []).map((r) => S.rowEls.get(r)).filter(Boolean);
  targets.forEach((r) => r.classList.add("target"));
  wrap._targets = targets;
  const anchor = targets[targets.length - 1] || firstFlagged(ev.column);
  if (anchor) anchor.after(wrap); else { $("#banner").hidden = false; $("#banner").append(wrap); }
  S.asks.set(ev.id, wrap);
  wrap.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  yes.focus({ preventScroll: true });
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
  setStatus(ev.finished ? `Done in ${ev.seconds} s` : `Stopped: ${ev.stop_reason}`);
  $("#waiting").hidden = true;
  const box = $("#answer"); box.hidden = false;
  box.style.animation = "none"; void box.offsetWidth; box.style.animation = "";
  const a = ev.analysis;
  $("#aTitle").textContent = a ? `${cap(a.agg)} of ${a.metric}${a.group_by && a.group_by.length ? " by " + a.group_by.join(", ") : ""}` : "No answer";
  $("#aMeta").textContent = a && a.rows_used != null ? `${a.rows_used} rows used` : "";
  renderGroups(ev.answer);
  const log = $("#aLog"); log.textContent = "";
  ev.changes.forEach((c, i) => {
    const li = el("li"); li.style.animationDelay = `${0.6 + i * 0.08}s`;
    li.innerHTML = c.applied ? SVG_OK : SVG_KEPT;
    li.append(el("span", null, plain(c.text)));
    log.append(li);
  });
  if (!ev.changes.length) log.append(el("li", null, "No changes were needed."));
  $("#aSummary").textContent = ev.summary || "";
  const files = $("#aFiles"); files.textContent = "";
  ev.files.forEach((f) => { const link = el("a", "ghost", f); link.href = `/api/runs/${S.runId}/files/${f}`; link.setAttribute("download", f); files.append(link); });
  $("#aStats").textContent = `${ev.tool_calls} tool calls · ${ev.approvals} question${ev.approvals === 1 ? "" : "s"} to you · ${ev.model}`;
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
  const t0 = performance.now();
  const tick = (now) => {
    const t = Math.min(1, Math.max(0, (now - t0) / 1100));
    const k = 1 - Math.pow(1 - t, 3);
    node.textContent = fmt(t < 1 ? Math.round(target * k * 100) / 100 : target);
    if (t < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : "");
function plain(text) {
  return text.replace(/^drop_duplicates: /, "").replace(/^normalize_labels: /, "").replace(/^exclude_rows: /, "")
    .replace(/^parse_dates: /, "").replace(/^set_missing: /, "").replace(/^trim_whitespace: /, "").replace(/^cast_numeric: /, "")
    .replace(/^fill_missing: /, "").replace(/^recompute_column: /, "")
    .replace(/\b(\d+) ([\w ]*?)\(s\)/g, (_, n, w) => `${n} ${w}${n === "1" ? "" : "s"}`)
    .replace(/^./, (c) => c.toUpperCase());
}
