"""EVAL planning numbers for Earshot D1, computed from the trial run's raw traces.

Planning only. The trial run is not part of D1; these numbers set D1's design.
Every statistic comes from vendor/evalstats.py (Rick's EVAL toolkit) except the
within-task shuffle test and the t-based detectable gap, which are marked [EXT].

Run from the Earshot repository root:
    python3 sprint/partD/D1/eval/d1_eval_planning.py > /tmp/planning_out.json
and compare with sprint/partD/D1/eval/planning_out.json.
"""
import glob
import itertools
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import evalstats as es  # noqa: E402

REPO = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
TRACES = os.path.join(REPO, "sprint/trial_run/traces/*.json")
FILE_OF_TARGET = {"A": "study.py", "B": "heldout.py", "C": "visibility.py", "D": "honest.py"}
PAIRS = ["".join(p) for p in itertools.combinations("ABCD", 2)]
SEED = 20261107


# ------------------------------------------------------------------ input-dependence ("lift")
def task_lift(in_idx, out_idx, default_idx):
    """[EXT] Mean over non-default pairs X of P(out = X | in = X) - P(out = X | in != X).
    Any relay whose output ignores the incoming handoff (always-default, random,
    always-include-the-target) has expected lift 0. A relay that copies has lift near 1."""
    vals = []
    for x in range(6):
        if x == default_idx:
            continue
        hit = out_idx == x
        a, b = hit[in_idx == x], hit[in_idx != x]
        if len(a) and len(b):
            vals.append(a.mean() - b.mean())
    return float(np.mean(vals))


def lift_statistic(tasks, labels):
    """Mean over clusters of the mean task lift (clusters weighted equally)."""
    by_cluster = {}
    for t, lab in zip(tasks, labels):
        by_cluster.setdefault(t["cluster"], []).append(task_lift(lab, t["out"], t["default_idx"]))
    return float(np.mean([np.mean(v) for v in by_cluster.values()]))


def shuffle_test(tasks, n_perm=20000, seed=SEED):
    """[EXT] Fisher randomization test. Under H0 (output independent of the incoming
    handoff, calls independent given the task) incoming labels are exchangeable among
    a task's calls, so permuting them within each task gives the exact null
    distribution, whatever the clustering. Two-sided; Monte Carlo with +1 correction."""
    rng = np.random.default_rng(seed)
    obs = lift_statistic(tasks, [t["in"] for t in tasks])
    count = 0
    for _ in range(n_perm):
        perm = lift_statistic(tasks, [rng.permutation(t["in"]) for t in tasks])
        count += abs(perm) >= abs(obs) - 1e-12
    return {"statistic": obs, "p_two_sided": (count + 1) / (n_perm + 1), "n_perm": n_perm}


def load_trial_tasks():
    rows = [json.load(open(p)) for p in sorted(glob.glob(TRACES))]
    by_task = {}
    for r in rows:
        by_task.setdefault(r["task_id"], []).append(r)
    tasks = []
    for tid, rs in sorted(by_task.items()):
        free = [r for r in rs if r["incoming_pair"] == "free" and r["gate_result"] == "accepted"]
        inc = [r for r in rs if r["incoming_pair"] != "free" and r["gate_result"] == "accepted"]
        if len(inc) != 12 or len(free) != 2:
            continue  # complete tasks only
        fp = [r["output_pair"] for r in free]
        default = fp[0] if fp[0] == fp[1] else None
        target = rs[0]["target"]
        t_in = [r for r in inc if target in r["incoming_pair"]]
        t_out = [r for r in inc if target not in r["incoming_pair"]]
        alt_in = [r for r in t_in if r["incoming_pair"] != default]
        alt_out = [r for r in t_out if r["incoming_pair"] != default]
        keep = lambda rs_: float(np.mean([r["output_pair"] == r["incoming_pair"] for r in rs_])) if rs_ else None
        reps = {}
        for r in inc:
            reps.setdefault(r["incoming_pair"], {})[r["replicate"]] = r
        tasks.append({
            "task": tid, "target": target, "cluster": FILE_OF_TARGET[target], "default": default,
            "K_in": keep(t_in), "K_out": keep(t_out), "K_alt": keep(alt_in), "K_alt_out": keep(alt_out),
            "C": float(np.mean([r["output_pair"] == default for r in inc])),
            "n_alt": len(alt_in), "kept_alt": int(sum(r["output_pair"] == r["incoming_pair"] for r in alt_in)),
            "kept_in": int(sum(r["output_pair"] == r["incoming_pair"] for r in t_in)),
            "eq_default": int(sum(r["output_pair"] == default for r in inc)),
            "in": np.array([PAIRS.index(r["incoming_pair"]) for r in inc]),
            "out": np.array([PAIRS.index(r["output_pair"]) for r in inc]),
            "default_idx": PAIRS.index(default) if default else -1,
            "kept_nk": [[float(reps[p][k]["output_pair"] == p) for k in (1, 2)] for p in PAIRS],
            "disagree": [p for p in PAIRS if reps[p][1]["output_pair"] != reps[p][2]["output_pair"]],
        })
    return len(rows), tasks


def main():
    n_rows, tasks = load_trial_tasks()
    clusters = sorted({t["cluster"] for t in tasks})
    lab = [t["cluster"] for t in tasks]
    cm = lambda key: [float(np.mean([t[key] for t in tasks if t["cluster"] == c])) for c in clusters]
    for t in tasks:
        t["delta"] = t["K_in"] - t["K_out"]
        t["delta_minus_standardiser"] = t["delta"] - 1 / 3  # all trial defaults contain the target
        t["lift"] = task_lift(t["in"], t["out"], t["default_idx"])
    out = {"inputs": {"trace_files": n_rows, "complete_tasks": len(tasks), "clusters": clusters},
           "toolkit": {"numpy": np.__version__, "scipy": __import__("scipy").__version__}}
    out["tasks"] = [{k: v for k, v in t.items() if k not in ("in", "out", "kept_nk")} for t in tasks]
    delta = [t["delta"] for t in tasks]
    out["finding_1_four_clusters"] = {
        "design_effect_delta": es.design_effect(delta, lab),
        "se_clt": es.se_clt(delta), "se_clustered": es.se_clustered(delta, lab),
        "sign_flip_floor_two_sided": {g: es.sign_flip_test([1.0] * g)["p"] for g in (4, 5, 6, 7, 8, 12, 16)},
        "clusters_needed_for_threshold": {str(m): next(g for g in range(2, 30) if es.sign_flip_test([1.0] * g)["p"] <= 0.05 / m) for m in (1, 2, 6)},
    }
    excess = cm("delta_minus_standardiser")
    out["finding_2_delta_vs_standardiser"] = {
        "delta_cluster_means": dict(zip(clusters, cm("delta"))),
        "delta_t_ci_cluster_means_EXT": es.t_ci(cm("delta")),
        "excess_over_one_third_cluster_means": dict(zip(clusters, excess)),
        "excess_t_ci_cluster_means_EXT": es.t_ci(excess),
        "excess_sign_flip_cluster_means": es.sign_flip_test(excess),
        "identity_check_K_in_equals_third_plus_two_thirds_K_alt": float(np.mean([t["K_in"] for t in tasks])),
        "identity_rhs": 1 / 3 + 2 / 3 * float(np.mean([t["K_alt"] for t in tasks])),
    }
    s_alt = [sum(t["kept_alt"] for t in tasks if t["cluster"] == c) for c in clusters]
    n_alt = [sum(t["n_alt"] for t in tasks if t["cluster"] == c) for c in clusters]
    s_c = [sum(t["eq_default"] for t in tasks if t["cluster"] == c) for c in clusters]
    n_c = [12 * sum(1 for t in tasks if t["cluster"] == c) for c in clusters]
    s_in = [sum(t["kept_in"] for t in tasks if t["cluster"] == c) for c in clusters]
    out["finding_3_keeping_by_file"] = {
        "K_alt_by_cluster": {c: [s, n] for c, s, n in zip(clusters, s_alt, n_alt)},
        "K_alt_point": sum(s_alt) / sum(n_alt), "K_alt_bclust_95": es.bayes_clustered_ci(s_alt, n_alt),
        "K_alt_out_all_tasks": [t["K_alt_out"] for t in tasks],
    }
    out["rates_bclust_95"] = {
        "C": {"successes": s_c, "n": n_c, "point": sum(s_c) / sum(n_c), "ci": es.bayes_clustered_ci(s_c, n_c),
              "ci_97_5": es.bayes_clustered_ci(s_c, n_c, alpha=0.025),
              "wilson_if_calls_independent": es.wilson_ci(sum(s_c), sum(n_c))},
        "K_in": {"successes": s_in, "n": [6 * sum(1 for t in tasks if t["cluster"] == c) for c in clusters],
                 "point": sum(s_in) / (6 * len(tasks)),
                 "ci": es.bayes_clustered_ci(s_in, [6 * sum(1 for t in tasks if t["cluster"] == c) for c in clusters])},
    }
    lifts = cm("lift")
    out["refinement_input_dependence"] = {
        "lift_cluster_means": dict(zip(clusters, lifts)),
        "lift_t_ci_cluster_means_EXT": es.t_ci(lifts),
        "shuffle_test_EXT": shuffle_test(tasks),
    }
    nk = np.array([row for t in tasks for row in t["kept_nk"]])
    out["repeats"] = {"noise_components_kept": es.noise_components(nk),
                      "agreement": [sum(6 - len(t["disagree"]) for t in tasks), 6 * len(tasks)],
                      "disagreements": {t["task"]: t["disagree"] for t in tasks if t["disagree"]}}
    det = {}
    for key in ("delta", "C", "lift"):
        sd = float(np.std(cm(key), ddof=1))
        det[key] = {"between_cluster_sd": sd}
        for g in (4, 8):
            for rho in (0.0, 0.5):
                om = 2 * sd ** 2 * (1 - rho)
                det[key][f"G{g}_rho{rho}"] = {
                    "mde_z_M10": es.mde(g, om),
                    "mde_t_EXT": float((stats.t.ppf(0.975, g - 1) + stats.t.ppf(0.80, g - 1)) * np.sqrt(om / g))}
    out["cross_arm_detectable_gap_planning_EXT"] = det
    out["baselines_analytic"] = {
        "random_pair": {"K": 1 / 6, "K_in": 1 / 6, "K_out": 1 / 6, "C": 1 / 6, "lift": 0.0},
        "copy_incoming": {"K": 1.0, "K_in": 1.0, "K_out": 1.0, "K_alt": 1.0, "C": 1 / 6, "lift": "about 1"},
        "always_default_with_target": {"K": 1 / 6, "K_in": 1 / 3, "K_out": 0.0, "K_alt": 0.0, "C": 1.0, "delta": 1 / 3, "lift": 0.0},
        "always_target_random_other": {"K_alt": 1 / 3, "K_out": 0.0, "lift": 0.0},
    }
    print(json.dumps(clean(out), indent=1, sort_keys=True))


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    return o


if __name__ == "__main__":
    main()
