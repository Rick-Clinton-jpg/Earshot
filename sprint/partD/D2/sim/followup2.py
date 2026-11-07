import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0,'.')
import sim_c as S
from run_scenarios import PROF
JOBS=[("codex: conceal cuts following 0.9->0.5, text among followers unchanged (null)","codex",dict(f=0.9,f_conceal=0.5,p_text=0.75,p_text_conceal=0.75)),
      ("claude: conceal cuts following 0.9->0.5, text among followers unchanged (null)","claude",dict(f=0.9,f_conceal=0.5,p_text=0.75,p_text_conceal=0.75)),
      ("codex: follow 0.9, text 0.75->0.5","codex",dict(f=0.9,f_conceal=0.9,p_text=0.75,p_text_conceal=0.5)),
      ("codex: follow 0.7, text 0.75->0.5","codex",dict(f=0.7,f_conceal=0.7,p_text=0.75,p_text_conceal=0.5)),
      ("claude: follow 0.7, text 0.75->0.5","claude",dict(f=0.7,f_conceal=0.7,p_text=0.75,p_text_conceal=0.5)),
      ("codex: follow 0.9->0.7 AND text 0.75->0.5","codex",dict(f=0.9,f_conceal=0.7,p_text=0.75,p_text_conceal=0.5))]
def run(job):
    name, arm, kw = job
    cfg=S.Cfg(relay='empirical',d1_profiles=PROF[arm],**kw)
    rng=np.random.default_rng(11+sum(map(ord,name)))
    T=[S.run_trial(cfg,rng) for _ in range(1500)]
    r=lambda f: float(np.mean([f(t) for t in T]))
    return {"name":name,"H4_unconditional":r(lambda t:t["p"]["H4_conceal"]<=.05),
            "H4_among_followers":r(lambda t:t["p_secondary"]["H4_conceal_among_followers"]<=.05)}
if __name__=="__main__":
    with Pool(2) as p: out=p.map(run,JOBS,chunksize=1)
    json.dump(out,open('followup2.json','w'),indent=1)
    for o in out: print(f"{o['name']:78} H4 all calls {o['H4_unconditional']:.3f}  H4 among followers {o['H4_among_followers']:.3f}")
