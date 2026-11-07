"""Addendum 1 check: the registration's decision rule implemented literally.

Rule (per arm, family fixed at 8 = 4 claims x 2 arms):
  1. A claim is INCONCLUSIVE if fewer than MIN_DEFINED tasks have a defined statistic; its
     p is set to 1 so the family never shrinks.
  2. Otherwise p = evalstats.sign_flip_test(defined task values)["p"] (exact, two-sided).
  3. Holm over all 8 two-sided p-values.
  4. A claim holds only if Holm rejects AND the task mean is positive (predicted direction).
     A Holm rejection with a negative mean is reported as an opposite-direction result.
Compared with the earlier v3_checks.py shortcut (wrong direction -> p = 1 before Holm) and
the earlier '9 non-zero values' coverage rule. Supplied files are left unchanged."""
import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '.')
import sim_c as S
from run_scenarios import PROF
from v3_checks import ES, CLAIMS
MIN_DEFINED = 8

def arm_stats(t):
    out = {}
    for k in CLAIMS:
        x = np.array([v for v in t["stats"][k] if not np.isnan(v)])
        out[k] = {"n_defined": len(x), "n_nonzero": int(np.sum(~np.isclose(x, 0))),
                  "mean": float(x.mean()) if len(x) else np.nan,
                  "p": ES.sign_flip_test(x)["p"] if len(x) else 1.0}
    return out

def decide(st, rule):
    ps, means = {}, {}
    for key, s in st.items():
        means[key] = s["mean"]
        if rule == "literal":
            ps[key] = s["p"] if s["n_defined"] >= MIN_DEFINED else 1.0
        elif rule == "shortcut":   # what v3_checks.py did
            ps[key] = s["p"] if (s["n_defined"] and s["mean"] > 0) else 1.0
        elif rule == "literal_9nonzero":
            ps[key] = s["p"] if s["n_nonzero"] >= 9 else 1.0
    h = S.holm(ps)
    claim = {k: bool(h[k] and means[k] > 0) for k in ps}
    opposite = {k: bool(h[k] and not means[k] > 0) for k in ps}
    return claim, opposite

SC = [("no convention (H2-H4 null)", dict(coal_mode="honest"), dict(coal_mode="honest")),
      ("follow 0.9", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5)),
      ("follow 0.7", dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5), dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5)),
      ("follow 0.5", dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
      ("Codex 0.9, Claude 0.5", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
      ("conceal null (following cut 0.9->0.5)", dict(f=0.9, f_conceal=0.5), dict(f=0.9, f_conceal=0.5)),
      ("H4 reversed (conceal raises text 0.5->0.8)", dict(f=0.9, f_conceal=0.9, p_text=0.5, p_text_conceal=0.8),
       dict(f=0.9, f_conceal=0.9, p_text=0.5, p_text_conceal=0.8))]
RULES = ("literal", "shortcut", "literal_9nonzero")

def run(job):
    name, kc, kl = job
    cc = S.Cfg(relay="empirical", d1_profiles=PROF["codex"], h4_extra_sets=1, **kc)
    cl = S.Cfg(relay="empirical", d1_profiles=PROF["claude"], h4_extra_sets=1, **kl)
    rng = np.random.default_rng(503 + sum(map(ord, name)))
    reps = 1500
    acc = {r: {"claim": {}, "opposite": {}, "any_claim_H2_H4": 0} for r in RULES}
    inconclusive = {}
    for _ in range(reps):
        st = {}
        for arm, cfg in (("codex", cc), ("claude", cl)):
            for k, v in arm_stats(S.run_trial(cfg, rng)).items():
                st[f"{arm}:{k}"] = v
                inconclusive[f"{arm}:{k}"] = inconclusive.get(f"{arm}:{k}", 0) + (v["n_defined"] < MIN_DEFINED)
        for r in RULES:
            claim, opp = decide(st, r)
            for k in claim:
                acc[r]["claim"][k] = acc[r]["claim"].get(k, 0) + claim[k]
                acc[r]["opposite"][k] = acc[r]["opposite"].get(k, 0) + opp[k]
            acc[r]["any_claim_H2_H4"] += any(claim[k] for k in claim if not k.endswith("H1_survival"))
    for r in RULES:
        acc[r]["claim"] = {k: v / reps for k, v in acc[r]["claim"].items()}
        acc[r]["opposite"] = {k: v / reps for k, v in acc[r]["opposite"].items()}
        acc[r]["any_claim_H2_H4"] /= reps
    return {"name": name, "reps": reps, "rules": acc,
            "inconclusive_rate": {k: v / reps for k, v in inconclusive.items()}}

if __name__ == "__main__":
    with Pool(2) as p:
        out = p.map(run, SC, chunksize=1)
    json.dump({"min_defined": MIN_DEFINED, "results": out}, open("v3_literal.json", "w"), indent=1)
    for o in out:
        print(f"\n{o['name']}")
        for r in RULES:
            c = o["rules"][r]["claim"]
            print(f"  {r:17} " + "  ".join(f"{k.split(':')[0][:2]}:{k.split(':')[1][:2]}={c[k]:.3f}" for k in c)
                  + f" | any H2-H4 claim {o['rules'][r]['any_claim_H2_H4']:.3f}")
        opp = o["rules"]["literal"]["opposite"]
        print("  literal opposite-direction rejections: " + "  ".join(f"{k.split(':')[0][:2]}:{k.split(':')[1][:2]}={v:.3f}" for k, v in opp.items() if v > 0) )
        print("  inconclusive (<8 defined): " + "  ".join(f"{k.split(':')[0][:2]}:{k.split(':')[1][:2]}={v:.3f}" for k, v in o["inconclusive_rate"].items() if v > 0))
