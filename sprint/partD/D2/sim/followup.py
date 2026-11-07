import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0,'.')
import sim_c as S
from run_scenarios import PROF
JOBS=[]
for arm in ('codex','claude'):
    for f in (1.0,0.9,0.7,0.5):
        JOBS.append((f"{arm} follow {f}, conceal changes nothing", arm, dict(f=f,f_conceal=f,p_text_conceal=0.3)))
    for fc in (0.8,0.7,0.5):
        JOBS.append((f"{arm} follow 0.9, conceal cuts following to {fc}", arm, dict(f=0.9,f_conceal=fc,p_text_conceal=0.3)))
    for m in (3,6):
        JOBS.append((f"{arm} follow 0.9, relay replicates m={m}", arm, dict(f=0.9,m_relay=m)))
JOBS.append(("param k=0.3 both kinds (H1 null), m=6", None, dict(relay='param',k_alt=0.3,k_out=0.3,m_relay=6)))
def run(job):
    name, arm, kw = job
    kw=dict(kw); relay=kw.pop('relay','empirical')
    cfg=S.Cfg(relay=relay,d1_profiles=PROF.get(arm),**kw)
    rng=np.random.default_rng(7+sum(map(ord,name)))
    T=[S.run_trial(cfg,rng) for _ in range(1500)]
    r=lambda f: float(np.mean([f(t) for t in T]))
    return {"name":name,"mc":{k:r(lambda t,k=k:t["mc"][k]) for k in T[0]["mc"]},
            "H1":r(lambda t:t["p"]["H1_survival"]<=.05),
            "H1_excl":r(lambda t:t["p_secondary"]["H1_survival_excl_default"]<=.05),
            "H4":r(lambda t:t["p"]["H4_conceal"]<=.05),
            "calls":float(np.mean([t["n_calls"] for t in T])),
            "follow_told":float(np.nanmean([t["means"]["follow_told"] for t in T])),
            "follow_conceal":float(np.nanmean([t["means"]["follow_conceal"] for t in T]))}
if __name__=="__main__":
    with Pool(2) as p: out=p.map(run,JOBS,chunksize=1)
    json.dump(out,open('followup.json','w'),indent=1)
    for o in out: print(f"{o['name']:48} MC tost.2 {o['mc']['tost_0.2']:.2f} .25 {o['mc']['tost_0.25']:.2f} .3 {o['mc']['tost_0.3']:.2f} point.15 {o['mc']['point_0.15']:.2f} | H1 {o['H1']:.3f} H1excl {o['H1_excl']:.3f} | H4 {o['H4']:.3f} | calls {o['calls']:.0f}")
