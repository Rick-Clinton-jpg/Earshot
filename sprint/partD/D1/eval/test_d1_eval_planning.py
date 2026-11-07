"""Checks for the [EXT] pieces of d1_eval_planning.py: the lift measure and the shuffle test.

Run from anywhere: python3 test_d1_eval_planning.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1_eval_planning as p  # noqa: E402

RNG = np.random.default_rng(1)
INCOMING = np.repeat(np.arange(6), 2)  # six pairs, two repeats each


def task(out, default_idx, cluster):
    return {"in": INCOMING.copy(), "out": np.asarray(out), "default_idx": default_idx, "cluster": cluster}


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    return ok


results = []
# 1. Always-default relay: lift exactly 0, test cannot reject.
tasks = [task([0] * 12, 0, f"f{i % 4}") for i in range(8)]
results.append(check("always-default relay has lift 0", p.lift_statistic(tasks, [t["in"] for t in tasks]) == 0.0))
results.append(check("always-default relay: shuffle p = 1", p.shuffle_test(tasks, n_perm=499)["p_two_sided"] == 1.0))

# 2. Copying relay: lift 1 and a tiny p.
tasks = [task(INCOMING.copy(), 0, f"f{i % 4}") for i in range(8)]
r = p.shuffle_test(tasks, n_perm=999)
results.append(check("copying relay has lift 1", abs(r["statistic"] - 1.0) < 1e-12))
results.append(check("copying relay: shuffle p at its floor", r["p_two_sided"] <= 1 / 999 + 1e-9))

# 3. Always-include-the-target relay that ignores the handoff: lift 0 in expectation, and
#    the test keeps its false-positive rate (target A; pairs with A are indices 0, 1, 2).
rejections = 0
sims = 200
for s in range(sims):
    tasks = [task(RNG.choice([0, 1, 2], size=12), 0, f"f{i % 4}") for i in range(8)]
    rejections += p.shuffle_test(tasks, n_perm=199, seed=s)["p_two_sided"] <= 0.05
rate = rejections / sims
results.append(check(f"input-blind target-sticky relay: false-positive rate {rate:.3f} <= 0.09", rate <= 0.09))

# 4. Partial copier (copies half the time, else default) is detected.
def partial(i):
    out = np.where(RNG.random(12) < 0.5, INCOMING, 0)
    return task(out, 0, f"f{i % 4}")
tasks = [partial(i) for i in range(8)]
results.append(check("partial copier detected at 0.05", p.shuffle_test(tasks, n_perm=999)["p_two_sided"] <= 0.05))

print(f"{sum(results)} passed, {len(results) - sum(results)} failed")
sys.exit(0 if all(results) else 1)
