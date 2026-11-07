"""Re-runs two grid scenarios with the final sim_c.py and checks they match results.json exactly."""
import json, sys
sys.path.insert(0, '.')
from run_scenarios import SCENARIOS, run_one
old = {r["name"]: r for r in json.load(open("results.json"))["scenarios"]}
ok = True
for name in ("P1 Codex relay, follow 0.7", "V3 Claude relay, no convention (coalition = honest)"):
    sc = next(s for s in SCENARIOS if s["name"] == name)
    new = run_one(sc)
    for key in ("reject_raw", "reject_holm4", "reject_file_signflip", "means"):
        same = new[key] == old[name][key]
        ok &= same
        print(f"{name[:45]:45} {key:22} {'identical' if same else 'DIFFERENT'}")
print("REPRODUCED" if ok else "MISMATCH")
