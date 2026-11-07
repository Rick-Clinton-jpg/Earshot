"""Compare two D2 scorer outputs. Exact for text, booleans, integers, decisions and exact p-values;
floats within a tight tolerance (numpy versions can differ in the last bits). Usage: compare_scores.py A.json B.json"""
import json, math, sys

REL, ABS = 1e-9, 1e-12
diffs, worst = [], [0.0, '']


def walk(a, b, path):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))
                                       and not isinstance(a, bool) and not isinstance(b, bool)):
        diffs.append((path, 'type', type(a).__name__, type(b).__name__)); return
    if isinstance(a, dict):
        if list(a) != list(b):
            diffs.append((path, 'keys', sorted(set(a) ^ set(b))[:5])); return
        for k in a: walk(a[k], b[k], path + '/' + str(k))
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append((path, 'length', len(a), len(b))); return
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, path + '[%d]' % i)
    elif isinstance(a, float) or isinstance(b, float):
        if a == b: return
        d = abs(a - b)
        if d > worst[0]: worst[0], worst[1] = d, path
        exact_field = path.rsplit('/', 1)[-1] in ('p', 'p_adjusted')
        if exact_field or not math.isclose(a, b, rel_tol=REL, abs_tol=ABS):
            diffs.append((path, 'value', a, b))
    elif a != b:
        diffs.append((path, 'value', a, b))


A, B = (json.load(open(p)) for p in sys.argv[1:3])
walk(A, B, '')
dec = lambda d: {k: (v.get('decision'), v.get('p_adjusted')) for k, v in d['confirmatory']['tests'].items()}
print('confirmatory decisions identical:', dec(A) == dec(B))
print('exploratory decisions identical:',
      {k: v['rejected'] for k, v in A['exploratory']['tests'].items()} ==
      {k: v['rejected'] for k, v in B['exploratory']['tests'].items()})
print('largest float difference: %.3g at %s' % (worst[0], worst[1] or '-'))
print('differences beyond tolerance:', len(diffs))
for d in diffs[:20]: print('  ', d)
sys.exit(1 if diffs else 0)
