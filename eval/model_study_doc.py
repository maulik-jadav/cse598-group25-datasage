"""Fill docs/final/findings_models.md from eval/model_study_findings.txt and eval/results/study_models.json, so every
number in the write-up comes from the result files. Usage: python -m eval.model_study_doc (after aggregate)."""
import glob, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
os.chdir(REPO)
tmpl = open(os.path.join(REPO, "eval", "model_study_findings.txt")).read()
d = json.load(open("eval/results/study_models.json"))
probe = json.load(open("eval/results/model_probe.json"))
M, S = d["models"], d["summary"]


def A(s):
    return M[s]["agent"]["heldout_test"]


def B(s):
    return M[s]["single_call"]["heldout_test"]


def beh(s):
    return M[s]["agent"]["behaviour"]


def acc(s):
    a = A(s)
    return f"{100 * a['accuracy']:.1f}% ({a['correct']} of {a['tasks']})"


full = [s for s in M if A(s) and A(s)["tasks"] == 80 and not s.endswith("-original")]
partial = [s for s in M if A(s) and A(s)["tasks"] < 80]
tool_ok = [s for s in full if (A(s)["tool_error_rate"] or 0) < 0.05 and A(s)["completion"] >= 0.9]
outs = sorted(M[s]["agent"]["scope_split"]["needs_exclusion_outside_question"]["correct"] for s in tool_ok)
think = [("qwen3-30b", "qwen3-30b-think"), ("qwen3-235b", "qwen3-235b-think"), ("qwen3-vl-32b", "qwen3-vl-32b-think")]
think_pairs = "; ".join(f"`{M[i]['model']}` {acc(i)} against `{M[t]['model']}` {acc(t)}" for i, t in think)
think_out = ", ".join(f"{M[t]['model']} {100 * beh(t)['tasks_checking_a_column_the_question_does_not_use']:.0f}% against "
                      f"{100 * beh(i)['tasks_checking_a_column_the_question_does_not_use']:.0f}% for its instruct twin"
                      for i, t in think)
gains = [(M[s]["agent_minus_single_call"], s) for s in full if "agent_minus_single_call" in M[s]]
pos = [g for g, _ in gains if g > 0]
gmed = sorted(g for g, _ in gains)[len(gains) // 2]
gain_sentence = (f"For the {len(gains)} fully run models with a complete single-call run, the agent is better for "
                 f"{len(pos)}, by a median of {100 * gmed:.1f} points (from {100 * min(g for g, _ in gains):+.1f} to "
                 f"{100 * max(g for g, _ in gains):+.1f}).")


def b2_damage(s):
    rows = [json.load(open(p)) for p in glob.glob(f"eval/results/b2-{s}/*-*/*.json")
            if p.split("/")[-2] in ("sales-heldout", "penguins-heldout", "sales-test", "penguins-test")]
    return sum(r["damaged_rows"] + r["damaged_cells"] for r in rows)


dmg = ", ".join(f"{b2_damage(s)} for `{M[s]['model']}`" for s in ["qwen3-30b", "qwen3-235b", "glm-5-3", "gpt-oss-120b"])
reruns = json.load(open("eval/results/model_study_reruns.json"))["removed"]
partial_note = "; ".join(f"`{M[s]['model']}` {A(s)['tasks']} of 80" for s in partial)
k = lambda s, key: beh(s)["tool_error_kinds"].get(key, 0)
INV = "invalid arguments (schema or JSON)"
vals = {
    "N_MODELS": len(M) - 1, "N_FULL": len(full), "N_NEAR_PERFECT": len(S["models_with_80_tasks_at_least_39_of_40_on_other_tasks"]),
    "N_LISTED": probe["listed_models"], "N_NOT_CHAT": len(probe["not_chat"]), "N_PROBED": len(probe["probes"]),
    "N_PASS": sum(p["real_pass"] for p in probe["probes"]),
    "PARTIAL_NOTE": partial_note or "none",
    "OUT_TOP": f"{outs[-1]}/40", "OUT_LOW": f"{outs[0]}/40",
    "N_SPEARMAN": S["spearman_accuracy_vs_checking_outside_question_columns"]["models"],
    "RHO": f"{S['spearman_accuracy_vs_checking_outside_question_columns']['rho']:.2f}",
    "THINK_PAIRS": think_pairs, "THINK_OUTSIDE": think_out,
    "MAV_NOTOOL": A("llama4-maverick")["stop_reasons"].get("no_tool_calls", 0), "MAV_NUDGES": beh("llama4-maverick")["nudges"],
    "O7_ERR": A("olmo3-7b")["tool_errors"], "O7_CALLS": A("olmo3-7b")["tool_calls"], "O7_INV": k("olmo3-7b", INV),
    "O7_LOOPS": beh("olmo3-7b")["error_loops"], "O7_BUDGET": A("olmo3-7b")["stop_reasons"].get("tool_budget_exhausted", 0),
    "O32_INV": k("olmo3-32b", INV), "O32_AWF": A("olmo3-32b")["stop_reasons"].get("answered_without_finish", 0),
    "GEM_INV": k("gemma4-31b", INV), "GPT_AWF": A("gpt-oss-120b")["stop_reasons"].get("answered_without_finish", 0),
    "GPT_INV": k("gpt-oss-120b", INV), "SCOUT_ERR": A("llama4-scout")["tool_errors"], "SCOUT_REC": A("llama4-scout")["recovered_errors"],
    "Q30_SEC": f"{A('qwen3-30b')['seconds_median']:.0f}",
    "PARETO_S": ", ".join(f"`{M[s]['model']}` ({100 * A(s)['accuracy']:.1f}%, {A(s)['seconds_median']:.0f} s)" for s in S["pareto_accuracy_vs_median_seconds"]),
    "RHO_S": f"{S['spearman_accuracy_vs_median_seconds']:.2f}",
    "PARETO_T": ", ".join(f"`{M[s]['model']}` ({100 * A(s)['accuracy']:.1f}%, {A(s)['tokens_median']:,.0f} tokens)" for s in S["pareto_accuracy_vs_median_tokens"]),
    "TURNS": "; ".join(f"`{M[s]['model']}` {A(s)['tool_calls_median']:.0f} calls in {A(s)['model_turns_median']:.0f} turns, "
                       f"{A(s)['tokens_median']:,.0f} tokens" for s in ["glm-5-3", "mimo-v2-6-pro", "qwen3-30b", "qwen3-235b"]),
    "GLM_SPEC": acc("glm-5-3-spec"), "GLM": acc("glm-5-3"),
    "GAIN_SENTENCE": gain_sentence, "B2_DAMAGE_EXAMPLES": dmg,
    "Q30_ACC": acc("qwen3-30b"), "Q30O_ACC": acc("qwen3-30b-original"), "Q30_CALLS": A("qwen3-30b")["tool_calls"],
    "INK_ACC": acc("inkling-small"),
    "Q30_B2": f"{100 * B('qwen3-30b')['accuracy']:.1f}% ({B('qwen3-30b')['correct']} of {B('qwen3-30b')['tasks']})",
    "Q30_ACC_N": f"{A('qwen3-30b')['correct']} of 80", "Q30O_ACC_N": f"{A('qwen3-30b-original')['correct']} of 80",
    "N_RERUN": sum("Connection error" in r["reason"] for r in reruns),
    "PARTIAL_LIMIT": ("Partial models: " + partial_note + ". Their accuracy is over the questions they finished, which "
                      "are not a random sample (the earlier, mostly sales, splits finished first).") if partial else
                     "Every model in the tables ran all 80 questions.",
}
out = tmpl
for key, value in vals.items():
    out = out.replace("{" + key + "}", str(value))
tables = subprocess.run([PY, "-m", "eval.model_study", "table"], capture_output=True, text=True, check=True).stdout
out = out.replace("<!-- TABLES -->", tables.strip())
left = [w for w in out.split("{")[1:] if w.split("}")[0].isupper()]
assert not left, left
open("docs/final/findings_models.md", "w").write(out)
print("written", len(out), "chars")
