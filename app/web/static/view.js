"use strict";
// View a run's four output files in the browser, each with a download button.

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
const params = new URLSearchParams(location.search);
const RUN = (params.get("run") || "").replace(/[^A-Za-z0-9]/g, "");
const INFO = {
  "cleaned.csv": { title: "Cleaned table", text: "Your table after the fixes, ready to use in Excel or any tool. Your original file is not changed." },
  "report.md": { title: "Report", text: "A readable summary: the problems found, every change with who approved it, and the answer." },
  "replay.py": { title: "Replay script", text: "Python that repeats the same fixes on this file without the AI. Run it with pandas installed to check or redo the cleaning." },
  "trace.jsonl": { title: "Step log", text: "Every step the agent took, in order: what it checked, what it found, and what it changed." },
};
const MAX_ROWS = 500;

function show(file) {
  if (!INFO[file]) file = "cleaned.csv";
  document.querySelectorAll(".tab[data-file]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.file === file)));
  $("#title").textContent = INFO[file].title;
  $("#lede").textContent = INFO[file].text;
  document.title = `DataSage · ${INFO[file].title}`;
  const url = `/api/runs/${RUN}/files/${file}`;
  $("#download").href = url; $("#download").setAttribute("download", file);
  $("#download").setAttribute("aria-label", `Download ${file}`);
  history.replaceState(null, "", `/view?run=${RUN}&file=${file}`);
  const box = $("#viewer"); box.textContent = ""; box.append(el("p", "v-note", "Loading."));
  fetch(url).then((r) => (r.ok ? r.text() : Promise.reject(new Error(r.status === 404 ? "This file is not there. The run may have been cleaned up after a day." : `HTTP ${r.status}`))))
    .then((text) => {
      box.textContent = "";
      const render = { "cleaned.csv": csv, "report.md": markdown, "replay.py": code, "trace.jsonl": trace }[file];
      box.append(render(text));
      box.classList.remove("v-in"); void box.offsetWidth; box.classList.add("v-in");
    })
    .catch((err) => { box.textContent = ""; box.append(el("p", "v-note v-error", err.message)); });
}

// ---------- cleaned.csv ----------
function parseCSV(text) {
  const rows = []; let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; } else if (ch === '"') q = false; else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(cell); cell = ""; }
    else if (ch === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else if (ch !== "\r") cell += ch;
  }
  if (cell !== "" || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
function csv(text) {
  const rows = parseCSV(text);
  const head = rows.shift() || [];
  const wrap = el("div", "v-stack");
  wrap.append(el("p", "v-note", `${rows.length.toLocaleString("en-US")} rows · ${head.length} columns` +
    (rows.length > MAX_ROWS ? ` · showing the first ${MAX_ROWS}; download for all of them` : "") +
    (head[0] === "row" ? ". The row column is the row number in your original file." : "")));
  const box = el("div", "v-table-box");
  const table = el("table", "v-table");
  const thead = el("thead"); const tr = el("tr");
  head.forEach((h) => tr.append(el("th", null, h)));
  thead.append(tr); table.append(thead);
  const tbody = el("tbody");
  rows.slice(0, MAX_ROWS).forEach((r) => {
    const t = el("tr");
    r.forEach((v) => { const td = el("td", /^-?[\d.]+$/.test(v) ? "num" : (v === "" ? "blank" : null), v === "" ? "—" : v); t.append(td); });
    tbody.append(t);
  });
  table.append(tbody); box.append(table); wrap.append(box);
  return wrap;
}

// ---------- report.md ----------
function inline(text) {
  const span = el("span");
  text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).forEach((p) => {
    if (p.startsWith("`") && p.endsWith("`") && p.length > 1) span.append(el("code", null, p.slice(1, -1)));
    else if (p.startsWith("**") && p.endsWith("**") && p.length > 3) span.append(el("strong", null, p.slice(2, -2)));
    else if (p) span.append(document.createTextNode(p));
  });
  return span;
}
function markdown(text) {
  const out = el("article", "v-md");
  const lines = text.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^```/.test(line)) {
      const buf = []; i++;
      while (i < lines.length && !/^```/.test(lines[i])) buf.push(lines[i++]);
      out.append(el("pre", "v-pre", buf.join("\n")));
    } else if (/^#{1,4} /.test(line)) {
      const level = line.match(/^#+/)[0].length;
      const h = el(`h${Math.min(level + 1, 5)}`); h.append(inline(line.replace(/^#+ /, ""))); out.append(h);
    } else if (/^\|/.test(line)) {
      const block = [];
      while (i < lines.length && /^\|/.test(lines[i])) block.push(lines[i++]);
      i--;
      const cells = (l) => l.replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const box = el("div", "v-table-box");
      const table = el("table", "v-table");
      const head = el("tr"); cells(block[0]).forEach((c) => { const th = el("th"); th.append(inline(c)); head.append(th); });
      const thead = el("thead"); thead.append(head); table.append(thead);
      const tbody = el("tbody");
      block.slice(2).forEach((l) => { const tr = el("tr"); cells(l).forEach((c) => { const td = el("td"); td.append(inline(c)); tr.append(td); }); tbody.append(tr); });
      table.append(tbody); box.append(table); out.append(box);
    } else if (/^- /.test(line)) {
      const ul = el("ul");
      while (i < lines.length && /^- /.test(lines[i])) { const li = el("li"); li.append(inline(lines[i++].slice(2))); ul.append(li); }
      i--; out.append(ul);
    } else if (line.trim()) {
      const p = el("p"); p.append(inline(line)); out.append(p);
    }
  }
  return out;
}

// ---------- replay.py ----------
function code(text) {
  const wrap = el("div", "v-stack");
  const bar = el("div", "v-bar");
  bar.append(el("p", "v-note", "Plain pandas. It reads your original file, then applies each approved fix in order."));
  const copy = el("button", "ghost small", "Copy"); copy.type = "button";
  copy.onclick = async () => { try { await navigator.clipboard.writeText(text); copy.textContent = "Copied"; } catch { copy.textContent = "Copy failed"; } setTimeout(() => (copy.textContent = "Copy"), 1500); };
  bar.append(copy); wrap.append(bar);
  const pre = el("pre", "v-code");
  text.replace(/\n$/, "").split("\n").forEach((line, n) => {
    const row = el("span", "v-line");
    row.append(el("span", "v-ln", String(n + 1)));
    const hash = line.indexOf("#");
    if (hash >= 0 && !/['"]/.test(line.slice(0, hash))) {
      row.append(document.createTextNode(line.slice(0, hash)), el("span", "v-comment", line.slice(hash)));
    } else row.append(document.createTextNode(line));
    pre.append(row);
  });
  wrap.append(pre);
  return wrap;
}

// ---------- trace.jsonl ----------
function brief(output) {
  if (!output || typeof output !== "object") return String(output ?? "");
  if (output.error) return output.error;
  if (output.analyze_refused) return `Not yet: ${output.open_findings.length} problem(s) still open, sent back to fix`;
  if (output.result && output.group_by) return "Answer: " + Object.entries(output.result).map(([k, v]) => `${k} ${v}`).join(", ");
  if (output.applied !== undefined) return `${output.applied ? "Applied" : "Not applied"}: ${output.summary || output.message || ""}`;
  if (output.message) return output.message;
  if (output.count !== undefined) return output.count ? `Found ${output.count} (rows ${(output.rows || []).join(", ")})` : "Nothing found";
  if (output.text_numbers) return ["text_numbers", "not_numbers", "negatives"].map((k) => `${k.replace("_", " ")} ${output[k].count}`).join(" · ");
  if (output.rules) return "Read the rules file";
  if (output.finished) return "Finished";
  return JSON.stringify(output).slice(0, 160);
}
function trace(text) {
  const events = text.split("\n").filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  const tools = events.filter((e) => e.event === "tool");
  const errors = tools.filter((e) => !e.ok).length;
  const wrap = el("div", "v-stack");
  wrap.append(el("p", "v-note", `${tools.length} steps · ${errors} error${errors === 1 ? "" : "s"} · ${events.length ? events[events.length - 1].t : 0} s`));
  const list = el("ol", "v-trace");
  events.forEach((e) => {
    const li = el("li", "v-step" + (e.event === "tool" && !e.ok ? " bad" : ""));
    li.append(el("span", "v-t", `${Number(e.t || 0).toFixed(1)} s`));
    const body = el("div", "v-body");
    if (e.event === "tool") {
      const head = el("div", "v-head");
      head.append(el("span", "v-tool", e.name));
      const args = Object.entries(e.args || {}).filter(([k]) => k !== "reason").map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join(", ");
      if (args) head.append(el("span", "v-args", args));
      body.append(head, el("span", "v-out", brief(e.output)));
      if (e.args && e.args.reason) body.append(el("span", "v-reason", `Why: ${e.args.reason}`));
      const more = el("details", "v-details");
      more.append(el("summary", null, "Full result"), el("pre", "v-pre", JSON.stringify(e.output, null, 2)));
      body.append(more);
    } else {
      body.append(el("span", "v-tool", e.event), el("span", "v-out", e.text || e.error || ""));
    }
    li.append(body); list.append(li);
  });
  wrap.append(list);
  return wrap;
}

if (!RUN) {
  $("#viewer").append(el("p", "v-note v-error", "Open this page from a run's Answer tab."));
} else {
  $("#profileLink").href = `/profile?run=${RUN}`;
  document.querySelectorAll(".tab[data-file]").forEach((b) => b.addEventListener("click", () => show(b.dataset.file)));
  show(params.get("file") || "cleaned.csv");
}
