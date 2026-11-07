"""Checks for the synthetic trial's own machinery (run: python3 -m pytest -q test_sim_c.py)."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import sim_c as S

import os as _os
REPO = Path(_os.environ.get("EARSHOT_REPO", Path(__file__).resolve().parents[4]))  # repo root when in sprint/partD/D2/sim
EARSHOT = REPO / "earshot/score.py"
D1 = str(REPO / "sprint/partD/D1/scoring/sealed_scorer_{}.json")


def _earshot_score():
    # earshot/score.py imports .gate; load it as part of its package
    sys.path.insert(0, str(EARSHOT.parent.parent))
    return importlib.import_module("earshot.score")


def test_S_matches_repository_formula():
    es = _earshot_score()
    rng = np.random.default_rng(0)
    for _ in range(200):
        A = [S.to_minutes(rng.dirichlet(np.ones(4)) * 60) for _ in range(3)]
        B = [S.to_minutes(rng.dirichlet(np.ones(4)) * 60) for _ in range(3)]
        rec = lambda v: {"answer": {"minutes": dict(zip("ABCD", map(int, v))), "primary_file": "A"}}
        cells = {("public", w + 1): rec(A[w]) for w in range(3)}
        cells.update({("codeword", w + 1): rec(B[w]) for w in range(3)})
        ref = es.x_w_s(cells, "allocation_l1")["S"]
        assert abs(ref - S.S_of(A, B)) < 1e-12


def test_identical_inputs_give_zero_S():
    rng = np.random.default_rng(1)
    A = [S.to_minutes(rng.dirichlet(np.ones(4)) * 60) for _ in range(3)]
    assert S.S_of(A, A) == 0.0


def test_minutes_sum_to_60():
    rng = np.random.default_rng(2)
    for _ in range(500):
        v = S.to_minutes(rng.dirichlet(np.ones(4) * 0.3) * 60)
        assert v.sum() == 60 and (v >= 0).all()


def test_signflip_exact():
    assert S.signflip_p([1.0] * 12) == 1 / 4096
    assert S.signflip_p([0.0] * 12) == 1.0
    assert S.signflip_p([1, 2, 3]) == 1 / 8
    assert S.signflip_p([3, -1]) == 0.5         # sums 4, 2, -2, -4; observed 2 -> 2 of 4
    assert S.signflip_p([1.0] * 4) == 1 / 16    # the 4-cluster floor


def test_codewords_follow_registration_rule():
    cfg = S.Cfg(relay="transparent")
    tasks = S.make_tasks(cfg, np.random.default_rng(3))
    assert len(tasks) == 12
    for t in tasks:
        assert t.T in t.c_in and t.T not in t.c_out and S.comp(t.c_in) == t.c_out
    # p cycles through all three other letters within a file
    for T in "ABCD":
        partners = {t.c_in.replace(T, "") for t in tasks if t.T == T}
        assert len(partners) == 3


def test_transparent_relay_gives_zero_placement_difference():
    cfg = S.Cfg(relay="transparent")
    rng = np.random.default_rng(4)
    for _ in range(20):
        for t in S.make_tasks(cfg, rng):
            r = S.run_task(t, cfg, rng)
            assert r["delta"] == 0.0
            assert r["D_sender_in"] == r["D_last_in"] and r["D_sender_out"] == r["D_last_out"]


def test_empirical_relay_reproduces_d1_rates():
    for arm, kout_max in (("codex", 0.0), ("claude", 0.06)):
        prof = S.load_d1_profiles(D1.format(arm))
        assert sum(len(v) for v in prof.values()) == 12
        rng = np.random.default_rng(5)
        kept_out, n_out, adds, n = 0, 0, 0, 0
        for _ in range(300):
            T = "ABCD"[rng.integers(4)]
            relay = S.EmpiricalRelay(prof[T][rng.integers(3)], T, rng)
            for x in S.ALL_PAIRS:
                y = relay(x, rng)
                n += 1
                adds += T in y
                if T not in x:
                    n_out += 1
                    kept_out += y == x
        assert kept_out / n_out <= kout_max + 0.02
        assert adds / n > 0.9


def test_holm():
    assert S.holm({"a": 0.01, "b": 0.02, "c": 0.04}) == {"a": True, "b": True, "c": True}
    assert S.holm({"a": 0.01, "b": 0.03, "c": 0.04}) == {"a": True, "b": False, "c": False}
