"""Family-rule options for v3. Stores per-trial two-sided sealed sign-flip p-values for
both arms, then scores several pre-declarable rules on the same trials."""
import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '.')
import sim_c as S
from run_scenarios import PROF
from v3_checks import pv, CLAIMS
SC = [("no convention (H2-H4 null)", dict(coal_mode="honest"), dict(coal_mode="honest")),
      ("follow 0.9", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5)),
      ("follow 0.7", dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5), dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5)),
      ("follow 0.5", dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
      ("Codex 0.9, Claude 0.5", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
      ("conceal null (following cut 0.9->0.5)", dict(f=0.9, f_conceal=0.5), dict(f=0.9, f_conceal=0.5))]
JOBS = [(n, kc, kl, x) for x in (0, 1) for n, kc, kl in SC]
def run(job):
    name, kc, kl, extra = job
    cc = S.Cfg(relay="empirical", d1_profiles=PROF["codex"], h4_extra_sets=extra, **kc)
    cl = S.Cfg(relay="empirical", d1_profiles=PROF["claude"], h4_extra_sets=extra, **kl)
    rng = np.random.default_rng(97 + extra + sum(map(ord, name)))
    rows, calls = [], {"codex": [], "claude": []}
    for _ in range(1500):
        row = {}
        for arm, cfg in (("codex", cc), ("claude", cl)):
            t = S.run_trial(cfg, rng)
            calls[arm].append(t["n_calls"])
            for k, v in pv(t).items():
                row[f"{arm}:{k}"] = v
        rows.append(row)
    return {"name": name, "h4_extra_sets": extra, "rows": rows,
            "calls": {a: float(np.mean(v)) for a, v in calls.items()},
            "calls_max": {a: int(np.max(v)) for a, v in calls.items()}}
def rules(rows):
    keys = list(rows[0])
    out = {}
    def rate(fam_fn):
        acc = {k: 0 for k in keys}
        for r in rows:
            for k, v in fam_fn(r).items():
                acc[k] += v
        return {k: v / len(rows) for k, v in acc.items()}
    out["holm8"] = rate(lambda r: S.holm(r))
    out["holm6_H4_exploratory"] = rate(lambda r: S.holm({k: v for k, v in r.items() if "H4" not in k}))
    out["holm4_per_arm"] = rate(lambda r: {**S.holm({k: v for k, v in r.items() if k.startswith("codex")}),
                                           **S.holm({k: v for k, v in r.items() if k.startswith("claude")})})
    return out
if __name__ == "__main__":
    with Pool(2) as p:
        res = p.map(run, JOBS, chunksize=1)
    summary = []
    for r in res:
        rr = rules(r["rows"])
        summary.append({"name": r["name"], "h4_extra_sets": r["h4_extra_sets"], "calls": r["calls"],
                        "calls_max": r["calls_max"], "power": rr})
    json.dump(summary, open("v3_options.json", "w"), indent=1)
    for s in summary:
        print(f"\n{s['name']} | H4 extra sets {s['h4_extra_sets']} | calls codex {s['calls']['codex']:.0f} claude {s['calls']['claude']:.0f}")
        for rule, v in s["power"].items():
            print(f"  {rule:22} " + "  ".join(f"{key.split(':')[0][:2]}:{key.split(':')[1][:2]}={val:.3f}"
                                              for key, val in v.items()))
