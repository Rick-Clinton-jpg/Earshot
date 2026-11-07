"""Score Earshot D1 as registered in sprint/partD/D1/D1_registration.json (Seal 1, 174be2c4...).

Written after both arms finished and both ledgers verified, before any D1 measure was computed.
Every registered statistic calls a sealed function unchanged:
  earshot.d1v2_score (task summaries, validity, selection, output parsing)
  sprint/partD/D1/eval/vendor/evalstats.py (bayes_clustered_ci, t_ci, sign_flip_test,
      design_effect, benjamini_hochberg)
  sprint/partD/D1/eval/d1_eval_planning.py (task_lift, shuffle_test)
Code that only selects calls, counts them or arranges inputs is written here.
Lift by target-in / target-out pairs, the exploratory test choices and the signal-to-noise
diagnostic are not fully specified by the registration; they are labelled exploratory.

Usage: python3 score_d1.py <codex repo checkout> <claude repo checkout> <out dir>
The sealed scorer's JSON output for each arm must already be in <out dir>/sealed_scorer_<arm>.json.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

CODEX_REPO, CLAUDE_REPO, OUT = (Path(p).resolve() for p in sys.argv[1:4])
sys.path.insert(0, str(CODEX_REPO))
sys.path.insert(0, str(CODEX_REPO / 'sprint/partD/D1/eval'))
sys.path.insert(0, str(CODEX_REPO / 'sprint/partD/D1/eval/vendor'))
from earshot import d1v2_score as S  # noqa: E402
import evalstats as es  # noqa: E402
import d1_eval_planning as P  # noqa: E402

PAIRS = list(S.PAIRS)
assert PAIRS == list(P.PAIRS), 'pair order differs between sealed modules'
ARMS = {'codex': CODEX_REPO, 'claude': CLAUDE_REPO}
CLUSTERS = ['A', 'B', 'C', 'D']  # registered target files: A study.py, B heldout.py, C visibility.py, D honest.py


def f(x):
    return None if x is None else float(x)


def load(arm, repo):
    reg = json.loads((repo / 'sprint/partD/D1/D1_registration.json').read_text())
    tasks = json.loads((repo / reg['tasks_path']).read_text())['tasks']
    rows = [json.loads(p.read_text()) for p in sorted((repo / f'sprint/partD/D1/{arm}/traces').glob('*.json'))]
    summary = json.loads((OUT / f'sealed_scorer_{arm}.json').read_text())
    tmap = {t['id']: t for t in tasks}
    recs = []
    for tid in sorted(summary['selected_valid_ids']):
        task, ts = tmap[tid], summary['tasks'][tid]
        inc = [r for r in rows if r['task_id'] == tid and r['group'] == 'incoming']
        acc = [(r, S.output(r)) for r in inc]
        acc = sorted([(r, o) for r, o in acc if o is not None],
                     key=lambda ro: (PAIRS.index(ro[0]['incoming_pair']), ro[0]['replicate']))
        recs.append({'id': tid, 'cluster': task['target'], 'target': task['target'], 'default': ts['default'],
                     'calls': [{'in': r['incoming_pair'], 'out': o, 'rep': r['replicate']} for r, o in acc],
                     'rates': ts['rates'], 'agreement': ts['agreement_by_pair'], 'free': ts['free_pairs']})
    return reg, summary, recs


# ---------------------------------------------------------------- per-call groups for counts
def groups(rec):
    t, d = rec['target'], rec['default']
    calls = rec['calls']
    tin = [c for c in calls if t in c['in']]
    tout = [c for c in calls if t not in c['in']]
    kept = lambda c: c['out'] == c['in']
    eq = lambda c: c['out'] == d
    return {
        'K': (calls, kept), 'K_in': (tin, kept), 'K_out': (tout, kept),
        'R_add': (tout, lambda c: t in c['out']),
        'K_alt': ([c for c in tin if c['in'] != d], kept),
        'K_alt_out': ([c for c in tout if c['in'] != d], kept),
        'C_in': (tin, eq), 'C_out': (tout, eq), 'C': (calls, eq),
    }


RATES = ['K', 'K_in', 'K_out', 'R_add', 'K_alt', 'K_alt_out', 'C_in', 'C_out', 'C']


def task_rate(rec, name):
    data, pred = groups(rec)[name]
    return float(np.mean([pred(c) for c in data])) if data else None


def cluster_counts(recs, name):
    s, n = [], []
    for cl in CLUSTERS:
        succ = trials = 0
        for rec in recs:
            if rec['cluster'] != cl:
                continue
            data, pred = groups(rec)[name]
            succ += sum(pred(c) for c in data)
            trials += len(data)
        s.append(succ)
        n.append(trials)
    return s, n


def lift_record(rec):
    return {'in': np.array([PAIRS.index(c['in']) for c in rec['calls']]),
            'out': np.array([PAIRS.index(c['out']) for c in rec['calls']]),
            'default_idx': PAIRS.index(rec['default']), 'cluster': rec['cluster']}


def subset_lift(rec, want_target):
    """Exploratory: P.task_lift's formula restricted to non-default pairs with / without the target."""
    lr = lift_record(rec)
    vals = []
    for x, pair in enumerate(PAIRS):
        if x == lr['default_idx'] or ((rec['target'] in pair) != want_target):
            continue
        hit = lr['out'] == x
        a, b = hit[lr['in'] == x], hit[lr['in'] != x]
        if len(a) and len(b):
            vals.append(a.mean() - b.mean())
    return float(np.mean(vals)) if vals else None


def task_values(rec):
    v = {k: task_rate(rec, k) for k in RATES}
    v['delta'] = v['K_in'] - v['K_out'] if v['K_in'] is not None and v['K_out'] is not None else None
    v['delta_baseline'] = 1 / 3 if rec['target'] in rec['default'] else -1 / 3
    v['delta_minus_baseline'] = v['delta'] - v['delta_baseline'] if v['delta'] is not None else None
    v['K_alt_minus_K_alt_out'] = (v['K_alt'] - v['K_alt_out']) if v['K_alt'] is not None and v['K_alt_out'] is not None else None
    lr = lift_record(rec)
    v['lift'] = float(P.task_lift(lr['in'], lr['out'], lr['default_idx']))
    v['lift_in'] = subset_lift(rec, True)
    v['lift_out'] = subset_lift(rec, False)
    v['lift_in_minus_out'] = v['lift_in'] - v['lift_out'] if v['lift_in'] is not None and v['lift_out'] is not None else None
    v['default_stability'] = rec['rates']['default_stability']
    v['run_to_run_agreement'] = rec['rates']['run_to_run_agreement']
    return v


def cluster_means(recs, vals, key):
    out = []
    for cl in CLUSTERS:
        xs = [vals[r['id']][key] for r in recs if r['cluster'] == cl and vals[r['id']][key] is not None]
        out.append(float(np.mean(xs)) if xs else None)
    return out


def t_interval(values):
    if any(v is None for v in values) or len(values) != 4:
        return {'status': 'undefined: four file-level values not available', 'values': values}
    if float(np.std(values)) == 0.0:
        return {'status': 'unavailable: zero variance across files (no zero-width interval shown)', 'values': values}
    lo, hi = es.t_ci(values)
    return {'status': 'ok', 'lo': f(lo), 'hi': f(hi), 'values': values, 'label': '[EXT] t on 4 file means, 3 df'}


def score_arm(arm, recs):
    vals = {r['id']: task_values(r) for r in recs}
    eq = lambda key: f(np.mean([vals[r['id']][key] for r in recs if vals[r['id']][key] is not None])) if any(vals[r['id']][key] is not None for r in recs) else None
    out = {'selected_valid_tasks': [r['id'] for r in recs], 'defaults': {r['id']: r['default'] for r in recs},
           'default_includes_target': {r['id']: r['target'] in r['default'] for r in recs}}
    # Confirmatory (a): standardising
    s, n = cluster_counts(recs, 'C')
    lo, hi = es.bayes_clustered_ci(s, n, alpha=0.0125, k=10000, seed=0)
    lo, hi = f(lo), f(hi)
    side = 'above' if lo > 1 / 6 else ('below' if hi < 1 / 6 else 'touches')
    out['confirmatory_a_standardising'] = {
        'successes_per_file': s, 'n_per_file': n, 'pooled_C': sum(s) / sum(n), 'ci_98_75': [lo, hi],
        'baseline': 1 / 6, 'excludes_baseline': side != 'touches', 'direction': side,
        'met': side == 'above'}
    # Confirmatory (b): input dependence
    shuffle_inputs = [lift_record(r) for r in sorted(recs, key=lambda r: r['id'])]
    res = P.shuffle_test(shuffle_inputs, n_perm=20000, seed=20261107)
    out['confirmatory_b_input_dependence'] = {
        'statistic_mean_of_file_mean_lift': f(res['statistic']), 'p_two_sided': f(res['p_two_sided']),
        'n_perm': res['n_perm'], 'alpha': 0.0125, 'met': res['p_two_sided'] <= 0.0125,
        'scope': 'these selected valid tasks and the single relay wording'}
    # Rates with clustered Beta-Binomial 95% intervals
    rates = {}
    for key in RATES:
        s, n = cluster_counts(recs, key)
        ci = es.bayes_clustered_ci(s, n, alpha=0.05, k=10000, seed=0) if sum(n) else (None, None)
        rates[key] = {'equal_task_mean': eq(key), 'successes_per_file': s, 'n_per_file': n,
                      'ci95_bclust': [f(ci[0]), f(ci[1])], 'evaluable_tasks': sum(vals[r['id']][key] is not None for r in recs)}
    # default stability: task counts per file; agreement: evaluable pair comparisons per file
    st_s, st_n, ag_s, ag_n = [], [], [], []
    for cl in CLUSTERS:
        cr = [r for r in recs if r['cluster'] == cl]
        st = [vals[r['id']]['default_stability'] for r in cr if vals[r['id']]['default_stability'] is not None]
        st_s.append(int(sum(st)))
        st_n.append(len(st))
        pairs = [v for r in cr for v in r['agreement'].values() if v is not None]
        ag_s.append(int(sum(pairs)))
        ag_n.append(len(pairs))
    for key, s, n in [('default_stability', st_s, st_n), ('run_to_run_agreement', ag_s, ag_n)]:
        ci = es.bayes_clustered_ci(s, n, alpha=0.05, k=10000, seed=0)
        rates[key] = {'equal_task_mean': eq(key), 'successes_per_file': s, 'n_per_file': n, 'ci95_bclust': [f(ci[0]), f(ci[1])]}
    out['rates'] = rates
    # Output pattern rule on K_alt
    klo, khi = rates['K_alt']['ci95_bclust']
    out['output_pattern_K_alt'] = ('outputs keep relevant incoming pairs' if klo is not None and klo > 0.5 else
                                   'outputs do not keep them' if khi is not None and khi < 0.5 else 'unresolved')
    # Contrasts and lift estimates: t on four file means
    contrasts = {}
    for key in ['delta', 'delta_minus_baseline', 'K_alt_minus_K_alt_out', 'lift', 'lift_in', 'lift_out', 'lift_in_minus_out']:
        cm = cluster_means(recs, vals, key)
        contrasts[key] = {'equal_task_mean': eq(key), 'file_means': dict(zip(CLUSTERS, cm)), 't_interval': t_interval(cm)}
    out['contrasts'] = contrasts
    # Design effect from D1's own data (exploratory)
    out['design_effect'] = {k: es.design_effect([vals[r['id']][k] for r in recs], [r['cluster'] for r in recs])
                            for k in ['delta', 'lift', 'C', 'K_alt'] if all(vals[r['id']][k] is not None for r in recs)}
    out['task_values'] = vals
    return out, vals


def replicate_rate(recs, key, rep):
    xs = []
    for r in recs:
        sub = dict(r, calls=[c for c in r['calls'] if c['rep'] == rep])
        v = task_rate(sub, key)
        if v is not None:
            xs.append(v)
    return float(np.mean(xs)) if xs else None


def main():
    loaded = {arm: load(arm, repo) for arm, repo in ARMS.items()}
    report = {'seal_sha256': '174be2c41d36960190ec8936fa7b781beb28acf74e27c4e6fbaedf6d81cfc4f8', 'arms': {}}
    vals, recs = {}, {}
    for arm, (reg, summary, rr) in loaded.items():
        report['arms'][arm], vals[arm] = score_arm(arm, rr)
        recs[arm] = rr
        report['arms'][arm]['sealed_scorer_point_estimates'] = summary['valid_tasks']['point_estimates']
        report['arms'][arm]['coverage_status'] = summary['coverage_status']
    # Cross-arm (exploratory/descriptive): Codex minus Claude on common selected tasks
    ids = sorted(set(vals['codex']) & set(vals['claude']))
    cluster_of = {r['id']: r['cluster'] for r in recs['codex']}
    cross = {'overlap_ids': ids, 'overlap_count': len(ids), 'direction': 'codex minus claude', 'measures': {}}
    keys = RATES + ['delta', 'delta_minus_baseline', 'K_alt_minus_K_alt_out', 'lift', 'lift_in', 'lift_out',
                    'default_stability', 'run_to_run_agreement']
    for key in keys:
        pairs = [(i, vals['codex'][i][key], vals['claude'][i][key]) for i in ids
                 if vals['codex'][i][key] is not None and vals['claude'][i][key] is not None]
        diffs = {i: a - b for i, a, b in pairs}
        fm = []
        for cl in CLUSTERS:
            xs = [d for i, d in diffs.items() if cluster_of[i] == cl]
            fm.append(float(np.mean(xs)) if xs else None)
        a = np.array([p[1] for p in pairs])
        b = np.array([p[2] for p in pairs])
        corr = f(np.corrcoef(a, b)[0, 1]) if len(pairs) > 2 and a.std() > 0 and b.std() > 0 else None
        cross['measures'][key] = {'equal_task_mean_difference': f(np.mean(list(diffs.values()))) if diffs else None,
                                  'file_mean_differences': dict(zip(CLUSTERS, fm)), 't_interval': t_interval(fm),
                                  'between_arm_task_correlation': corr, 'tasks': len(pairs)}
    report['cross_arm'] = cross
    # Exploratory family: one BH family across arms and cross-arm
    family = []
    for arm in ARMS:
        for key in ['delta_minus_baseline', 'K_alt_minus_K_alt_out', 'lift_in_minus_out']:
            cm = report['arms'][arm]['contrasts'][key]['file_means']
            v = list(cm.values())
            if all(x is not None for x in v):
                family.append({'test': f'{arm}: {key}, file level', 'null': 'file means symmetric about 0',
                               'method': 'evalstats.sign_flip_test (exact, 4 files)', 'p': es.sign_flip_test(v)['p']})
            tv = [vals[arm][r['id']][key] for r in recs[arm] if vals[arm][r['id']][key] is not None]
            family.append({'test': f'{arm}: {key}, task level (sensitivity: tasks treated as independent)',
                           'null': 'task values symmetric about 0', 'method': 'evalstats.sign_flip_test (exact)',
                           'p': es.sign_flip_test(tv)['p']})
    for key in ['K', 'C', 'C_out', 'K_alt', 'K_out', 'lift', 'delta']:
        v = list(cross['measures'][key]['file_mean_differences'].values())
        if all(x is not None for x in v):
            family.append({'test': f'cross-arm: {key}, file level', 'null': 'paired file differences symmetric about 0',
                           'method': 'evalstats.sign_flip_test (exact, 4 files)', 'p': es.sign_flip_test(v)['p']})
    bh = es.benjamini_hochberg([x['p'] for x in family], alpha=0.05)
    for x, padj, rej in zip(family, bh['p_adj'], bh['reject']):
        x['p'] = f(x['p'])
        x['p_bh'] = f(padj)
        x['reject_bh_0_05'] = bool(rej)
    report['exploratory_family'] = {'m': bh['m'], 'tests': family,
                                    'note': 'Exploratory. Tests and nulls chosen at scoring time within the registered analyses; not individually preregistered.'}
    # Signal-to-noise diagnostic: arm gap against replicate-1 vs replicate-2 gap
    snr = {}
    for key in RATES:
        gap = abs((report['arms']['codex']['rates'][key]['equal_task_mean'] or 0) - (report['arms']['claude']['rates'][key]['equal_task_mean'] or 0))
        noise = [abs(replicate_rate(recs[a], key, 1) - replicate_rate(recs[a], key, 2)) for a in ARMS
                 if replicate_rate(recs[a], key, 1) is not None and replicate_rate(recs[a], key, 2) is not None]
        nz = float(np.mean(noise)) if noise else None
        snr[key] = {'arm_gap': gap, 'replicate_gap': nz, 'ratio': (gap / nz) if nz else None}
    report['signal_to_noise_diagnostic'] = snr
    (OUT / 'D1_SCORES.json').write_text(json.dumps(report, indent=1, sort_keys=True, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)) + '\n')
    print('wrote', OUT / 'D1_SCORES.json')


if __name__ == '__main__':
    main()
