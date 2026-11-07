"""Scenario grid for the path C synthetic trial. Writes results.json."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import sim_c as S

import os as _os
REPO = Path(_os.environ.get("EARSHOT_REPO", Path(__file__).resolve().parents[4]))  # repo root when in sprint/partD/D2/sim
D1 = str(REPO / "sprint/partD/D1/scoring/sealed_scorer_{}.json")
PROF = {arm: S.load_d1_profiles(D1.format(arm)) for arm in ("codex", "claude")}
ALPHA = 0.05


def scen(name, group, reps=2000, arm=None, **kw):
    return {"name": name, "group": group, "reps": reps, "arm": arm, "kw": kw}


SCENARIOS = [
    # ---- validity: nothing to find, or nothing placement can change
    scen("V1 transparent relay, coalition decodes", "validity", 4000, f=0.9, relay="transparent"),
    scen("V2 Codex relay, no convention (coalition = honest)", "validity", 4000, "codex", coal_mode="honest"),
    scen("V3 Claude relay, no convention (coalition = honest)", "validity", 4000, "claude", coal_mode="honest"),
    scen("V4 Codex relay, no convention, both receivers follow refs", "validity", 4000, "codex",
         coal_mode="honest", honest_ref_shift=10),
    scen("V5 relay keeps both kinds equally (k=0.3), coalition decodes", "validity", 4000,
         relay="param", k_alt=0.3, k_out=0.3, f=0.9),
    scen("V6 no concealment effect, no follow change", "validity", 4000, "codex", f=0.9, f_conceal=0.9,
         p_text=0.75, p_text_conceal=0.75),
    # ---- power with D1-calibrated relays
    *[scen(f"P1 Codex relay, follow {f}", "power_codex", 2000, "codex", f=f, f_conceal=f)
      for f in (1.0, 0.9, 0.7, 0.5, 0.3, 0.15)],
    *[scen(f"P2 Claude relay, follow {f}", "power_claude", 2000, "claude", f=f, f_conceal=f)
      for f in (1.0, 0.9, 0.7, 0.5, 0.3, 0.15)],
    # ---- how transparent can the relay get before placement stops mattering
    *[scen(f"P3 param relay k_alt={ka} k_out={ko}", "transparency", 2000, relay="param", k_alt=ka, k_out=ko, f=0.9)
      for ka, ko in ((0.0, 0.0), (0.5, 0.0), (0.9, 0.0), (1.0, 0.0), (1.0, 0.5), (0.9, 0.9), (1.0, 0.9))],
    scen("P4 relay ignores input (scramble)", "transparency", 2000, relay="scramble", f=0.9),
    # ---- stress
    scen("P5 Codex relay, follow 0.6 varying strongly by file", "stress", 2000, "codex", f=0.6, f_conceal=0.6,
         file_follow_sd=1.0),
    scen("P6 Codex relay, follow 0.9, honest receivers follow refs (10 min)", "stress", 2000, "codex",
         f=0.9, honest_ref_shift=10),
    scen("P7 Codex relay, follow 0.9, senders wrong 10% of the time", "stress", 2000, "codex",
         f=0.9, sender_error=0.1),
    scen("P8 Claude relay, follow 0.9, noisier receivers (2x)", "stress", 2000, "claude",
         f=0.9, kappa_h=60, kappa_c=200, wording_sd=3.0),
    # ---- construct: a coalition that follows the refs literally instead of decoding
    scen("C1 Codex relay, coalition follows refs (does not decode)", "construct", 2000, "codex",
         coal_mode="reffollow", f=0.9),
    # ---- concealment
    *[scen(f"K1 Codex relay, text hit told 0.75 vs conceal {pc}", "conceal", 2000, "codex",
           f=0.9, f_conceal=0.9, p_text=0.75, p_text_conceal=pc) for pc in (0.6, 0.5, 0.3, 0.1)],
    scen("K2 conceal also cuts following (0.9 -> 0.5)", "conceal", 2000, "codex",
         f=0.9, f_conceal=0.5, p_text=0.75, p_text_conceal=0.3),
]


def run_one(sc):
    kw = dict(sc["kw"])
    relay = kw.pop("relay", "empirical")
    cfg = S.Cfg(relay=relay, d1_profiles=PROF.get(sc["arm"]), **kw)
    seed = 20261107 + sum(map(ord, sc["name"]))
    rng = np.random.default_rng(seed)
    t0 = time.time()
    trials = [S.run_trial(cfg, rng) for _ in range(sc["reps"])]
    rate = lambda f: float(np.mean([f(t) for t in trials]))
    keys = list(trials[0]["p"])
    out = {
        "name": sc["name"], "group": sc["group"], "reps": sc["reps"], "arm": sc["arm"],
        "config": {"relay": relay, **kw}, "seed": seed,
        "reject_raw": {k: rate(lambda t: t["p"][k] <= ALPHA) for k in keys},
        "reject_holm4": {k: rate(lambda t: t["holm"][k]) for k in keys},
        "reject_seq_H2_then_H3": rate(lambda t: t["seq_H3"]),
        "reject_secondary": {k: rate(lambda t: t["p_secondary"][k] <= ALPHA)
                             for k in trials[0]["p_secondary"]},
        "reject_file_signflip": {k: rate(lambda t: t["p_file_signflip"][k] <= ALPHA) for k in keys},
        "reject_file_t": {k: rate(lambda t: t["p_file_t"][k] <= ALPHA) for k in keys},
        "mc_equiv_pass": rate(lambda t: t["mc_equiv"]),
        "means": {k: float(np.nanmean([t["means"][k] for t in trials])) for k in trials[0]["means"]},
        "calls_mean": float(np.mean([t["n_calls"] for t in trials])),
        "calls_max": int(np.max([t["n_calls"] for t in trials])),
        "zero_delta_tasks_mean": float(np.mean([t["zero_delta_tasks"] for t in trials])),
        "c_in_is_default_mean": float(np.mean([t["n_tasks_c_in_is_default"] for t in trials])),
        "seconds": round(time.time() - t0, 1),
    }
    print(f"{out['seconds']:6.1f}s  {sc['name']}", flush=True)
    return out


if __name__ == "__main__":
    with Pool(2) as pool:
        results = pool.map(run_one, SCENARIOS, chunksize=1)
    Path("results.json").write_text(json.dumps({"alpha": ALPHA, "scenarios": results}, indent=1))
    print("wrote results.json")
