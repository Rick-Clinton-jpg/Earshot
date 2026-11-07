"""Checks for registration v3: Holm over 8 tests (4 claims x 2 arms, as D1 controlled
its family across arms), and the v3 concealment rule (observable followers only)."""
import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '.')
import sim_c as S
from run_scenarios import PROF
import importlib.util
from pathlib import Path
import os as _os
REPO = Path(_os.environ.get("EARSHOT_REPO", Path(__file__).resolve().parents[4]))  # repo root when in sprint/partD/D2/sim
_spec = importlib.util.spec_from_file_location(
    "evalstats", str(REPO / "sprint/partD/D1/eval/vendor/evalstats.py"))
ES = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ES)   # sealed copy, sha 2ced334a
CLAIMS = ["H1_survival", "H2_lasthop", "H3_placement", "H4_v3"]
def pv(t):
    """Registered v3 rule: evalstats.sign_flip_test (two-sided, exact) on the defined task
    statistics; a claim counts only if Holm rejects AND the task mean is positive.
    Encoded as p = 1 when the mean is not positive."""
    out = {}
    for k in CLAIMS:
        x = np.array([v for v in t["stats"][k] if not np.isnan(v)])
        if len(x) == 0 or x.mean() <= 0:
            out[k] = 1.0
        else:
            out[k] = ES.sign_flip_test(x)["p"]
    return out
JOBS = [
    ("both arms: no convention, no concealment effect (FWER)", dict(coal_mode="honest"), dict(coal_mode="honest")),
    ("both arms follow 1.0, conceal text 0.75->0.5", dict(f=1.0, f_conceal=1.0, p_text_conceal=0.5), dict(f=1.0, f_conceal=1.0, p_text_conceal=0.5)),
    ("both arms follow 0.9, conceal text 0.75->0.5", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5)),
    ("both arms follow 0.7, conceal text 0.75->0.5", dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5), dict(f=0.7, f_conceal=0.7, p_text_conceal=0.5)),
    ("both arms follow 0.5, conceal text 0.75->0.5", dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
    ("Codex follows 0.9, Claude 0.5, conceal text 0.75->0.5", dict(f=0.9, f_conceal=0.9, p_text_conceal=0.5), dict(f=0.5, f_conceal=0.5, p_text_conceal=0.5)),
    ("v3 conceal null: following cut 0.9->0.5, text among followers unchanged", dict(f=0.9, f_conceal=0.5, p_text_conceal=0.75), dict(f=0.9, f_conceal=0.5, p_text_conceal=0.75)),
]
def run(job):
    name, kc, kl = job
    cc = S.Cfg(relay="empirical", d1_profiles=PROF["codex"], **kc)
    cl = S.Cfg(relay="empirical", d1_profiles=PROF["claude"], **kl)
    rng = np.random.default_rng(31 + sum(map(ord, name)))
    reps = 2000
    rej = {f"{a}:{k}": 0 for a in ("codex", "claude") for k in CLAIMS}
    raw = dict(rej); any_rej = 0
    for _ in range(reps):
        ps = {}
        for arm, cfg in (("codex", cc), ("claude", cl)):
            for k, v in pv(S.run_trial(cfg, rng)).items():
                ps[f"{arm}:{k}"] = v
        h = S.holm(ps)
        any_rej += any(h.values())
        for k in ps:
            rej[k] += h[k]; raw[k] += ps[k] <= 0.05
    return {"name": name, "reps": reps, "holm8": {k: v / reps for k, v in rej.items()},
            "raw": {k: v / reps for k, v in raw.items()}, "any_rejection": any_rej / reps}
if __name__ == "__main__":
    with Pool(2) as p:
        out = p.map(run, JOBS, chunksize=1)
    json.dump(out, open("v3_checks.json", "w"), indent=1)
    for o in out:
        print(o["name"], "| any rejection %.3f" % o["any_rejection"])
        for arm in ("codex", "claude"):
            print("   %-6s holm8 " % arm + "  ".join(f"{k}={o['holm8'][arm+':'+k]:.3f}" for k in CLAIMS)
                  + " | raw " + "  ".join(f"{o['raw'][arm+':'+k]:.3f}" for k in CLAIMS))
