"use strict";
// The top of the results page: a few plain-language charts. Everything else sits under "All the numbers".
(() => {
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const pct = (x, d = 0) => `${(x * 100).toFixed(d)}%`;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function bar(value, { ci, cls = "", max = 1 } = {}) {
    const track = el("div", "g-track");
    const fill = el("div", `g-fill ${cls}`);
    track.append(fill);
    if (ci) {
      const w = el("div", "g-ci");
      w.style.left = `${(ci[0] / max) * 100}%`; w.style.width = `${((ci[1] - ci[0]) / max) * 100}%`;
      w.title = `95% range ${pct(ci[0], 1)} to ${pct(ci[1], 1)}`;
      track.append(w);
    }
    const target = `${Math.max(0.8, (value / max) * 100)}%`;
    if (reduce) fill.style.width = target; else requestAnimationFrame(() => requestAnimationFrame(() => { fill.style.width = target; }));
    return track;
  }

  function row(label, about, value, opts = {}) {
    const r = el("div", "g-row" + (opts.highlight ? " hl" : ""));
    const name = el("div", "g-name");
    name.append(el("span", "g-label", label));
    if (about) name.append(el("span", "g-about", about));
    const right = el("div", "g-value", opts.text || pct(value, value === 0 || value === 1 ? 0 : (opts.digits ?? 1)));
    r.append(name, bar(value, opts), right);
    if (opts.pill !== undefined) r.append(opts.pill ? el("span", `g-pill ${opts.pillCls || ""}`, opts.pill) : el("span"));
    return r;
  }

  function card(title, lead) {
    const c = el("section", "g-card");
    c.append(el("h2", "g-h", title));
    if (lead) c.append(el("p", "g-lead", lead));
    return c;
  }

  function render(s) {
    const box = document.getElementById("glance");
    if (!s || !s.approaches) { box.hidden = true; document.getElementById("allNumbers").open = true; return; }
    const n = s.questions || 200;

    // 1. The answer
    const ds = s.approaches.find((a) => a.id === "datasage-m3");
    const others = s.approaches.filter((a) => a.id !== "datasage-m3");
    const best = others.reduce((a, b) => (b.accuracy > a.accuracy ? b : a), others[0]);
    const c1 = card(`Right answers on ${n} questions it had never seen`,
      `DataSage answered ${pct(ds.accuracy, 1)} correctly. The best other approach, ${best.label.toLowerCase()}, managed ${pct(best.accuracy, 1)}.`);
    const list1 = el("div", "g-list");
    [...others, ds].forEach((a) => list1.append(row(a.label, a.about, a.accuracy, { ci: a.ci95, cls: a.id === "datasage-m3" ? "final" : "", highlight: a.id === "datasage-m3" })));
    c1.append(list1);
    const damaging = s.approaches.filter((a) => a.damaged > 0);
    c1.append(el("p", "g-foot", ds.damaged === 0
      ? `DataSage never changed a correct cell.${damaging.length ? ` ${damaging.map((a) => `${a.label} damaged correct data in ${pct(a.tasks_with_damage)} of questions`).join("; ")}.` : ""} The thin band on each bar is the 95% range.`
      : "The thin band on each bar is the 95% range."));
    box.append(c1);

    // 2. What makes it work
    if (s.parts && s.parts.length) {
      const c2 = card("What makes it work", "Each row turns off one part of DataSage and asks the same questions again.");
      const list2 = el("div", "g-list with-pill");
      list2.append(row("DataSage, all parts on", null, ds.accuracy, { cls: "final", highlight: true, pill: "" }));
      s.parts.forEach((p) => list2.append(row(p.label, p.about, p.accuracy, {
        pill: p.verdict, pillCls: p.verdict.startsWith("matters") ? "strong" : p.verdict.startsWith("helps") ? "mid" : "none" })));
      c2.append(list2);
      box.append(c2);
    }

    // 3. Steady + where it misses
    const pair = el("div", "g-pair");
    if (s.consistency) {
      const c = s.consistency;
      const c3 = card("Steady from run to run", `The same ${n} questions, asked ${c.runs} separate times: between ${pct(c.min, 1)} and ${pct(c.max, 1)} right each time.`);
      const dots = el("div", "g-dots");
      c.by_run.forEach((v, i) => { const d = el("div", "g-dot"); d.append(el("span", "g-dot-v", pct(v, 1)), el("span", "g-dot-l", `Run ${i + 1}`)); dots.append(d); });
      c3.append(dots);
      pair.append(c3);
    }
    if (s.misses) {
      const m = s.misses;
      const c4 = card("Where it still misses",
        "Almost every miss is a row that breaks a rule in a column the question does not use. DataSage only checks the columns the question needs, so it leaves those rows in.");
      const list4 = el("div", "g-list compact");
      list4.append(row("Questions without such rows", `${m.not_exposed.questions} questions`, m.not_exposed.accuracy, { cls: "final" }));
      list4.append(row("Questions with such rows", `${m.exposed.questions} questions`, m.exposed.accuracy, { cls: "warn" }));
      c4.append(list4);
      pair.append(c4);
    }
    if (pair.children.length) box.append(pair);

    // 4. Which model
    if (s.models && s.models.rows && s.models.rows.length) {
      const m = s.models;
      const d = m.default;
      const c6 = card(`Which model? ${m.count} models tried as DataSage's planner`,
        `${d ? `The default, Qwen3-30B, is number ${m.rank} of ${m.count} at ${pct(d.accuracy, 1)}, and among the fastest (${Math.round(d.seconds)} s per question). ` : ""}` +
        `With DataSage around it, a model answers a median ${Math.round(m.median_lift * 100)} points more questions right than the same model asked in one call.`);
      const list6 = el("div", "g-list");
      const top = m.rows.slice(0, 6);
      if (d && !top.some((r) => r.id === d.id)) top.push(d);
      top.forEach((r) => list6.append(row(r.model, `${r.seconds ? `${Math.round(r.seconds)} s per question` : ""}${r.single != null ? ` · one call: ${pct(r.single, 0)}` : ""}`,
        r.accuracy, { cls: r.id === "qwen3-30b" ? "final" : "", highlight: r.id === "qwen3-30b", ci: r.ci95 })));
      const low = m.rows.slice(-2).reverse();
      c6.append(list6);
      c6.append(el("p", "g-foot", `80 held-out and test questions per model; the thin band is the 95% range; times were measured while many runs shared the API. Lowest: ${low.map((r) => `${r.model} ${pct(r.accuracy, 1)}`).join(", ")}, mostly from malformed tool calls. No model, strong or weak, changed a correct cell as DataSage's planner.`));
      box.append(c6);
    }

    // 5. Harder tables
    if (s.hard) {
      const h = s.hard;
      const c5 = card("On bigger, messier tables", "Tables of 300 to 2,000 rows with many problems at once, including more rule-breaking rows than a check lists.");
      const list5 = el("div", "g-list");
      Object.entries(h).forEach(([id, v]) => list5.append(row(v.label, `${v.correct} of ${v.n} right`, v.accuracy, { cls: id.startsWith("datasage") ? "final" : "", highlight: id === "datasage-m3" })));
      c5.append(list5);
      box.append(c5);
    }
  }

  fetch("/api/results").then((r) => r.json()).then((d) => render(d.story)).catch(() => {
    document.getElementById("glance").hidden = true; document.getElementById("allNumbers").open = true;
  });
})();
