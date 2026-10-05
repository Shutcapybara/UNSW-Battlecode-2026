"""Synthetic check of r2_battery.py rev 6 against Tanaka 21:25Z blockers 1-4 + nonnegative probabilities. Run from a scratch dir
containing tools/hinata/{r2_battery.py,r2_bc.py}; invented data only (100 rows, 4 teams, 10 series), no real outputs read.
Expected: cases 1, 2, 2b, 3, 5, 6b REFUSED; 1b, 3b, 4, 6 goes_forward=False (inventory incomplete); 4b goes_forward=True."""
import json, sys, subprocess, shutil
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0,'tools/hinata'); import r2_bc as R, r2_battery as B
rng=np.random.default_rng(1); n=100
A0=pd.DataFrame(dict(game=np.arange(n)//10, side=0, dragon=np.arange(n)%10, round=1, turn=0, map='M', team=(np.arange(n)//25).astype(str),
   series_key=[f's{i//10}' for i in range(n)], x_is_queen=0, y_first=rng.choice([0,1,3],n)))
A0['fold']=['f%d'%((i//10)%5) for i in range(n)]
def P_of(y,acc):
    P=np.full((len(y),4),0.1); P[:,2]=0
    hit=rng.random(len(y))<acc
    for i,(yy,hh) in enumerate(zip(y,hit)): P[i,yy if hh else (1 if yy!=1 else 0)]=0.8
    return P/P.sum(1,keepdims=True)
def mk(name,rows,arms,man,mb=None):
    d=Path('runs')/name; d.mkdir(parents=True,exist_ok=True); rows.to_parquet(d/'rows.parquet'); (d/'manifest.json').write_text(json.dumps(man))
    reg=dict(arms={},info=dict(model_bytes=mb or {k:1 for k in arms}))
    y=rows.y_first.to_numpy()
    for k,P in arms.items():
        np.save(d/f'p_{k}.npy',P); f=rows.fold.to_numpy(); q=rows.x_is_queen.to_numpy()==1
        reg['arms'][k]=dict(frl_all=R.frl(y,P),frl_queen=R.frl(y,P,q),frl_nonqueen=R.frl(y,P,~q),frl_boot=R.series_boot(y,P,rows.series_key.to_numpy(),n=50),
          frl_per_fold={x:R.frl(y,P,f==x) for x in set(f)},frl_per_team={x:R.frl(y,P,(rows.team==x).to_numpy()) for x in set(rows.team)},frl_per_map={'M':R.frl(y,P)})
    (d/'registry.json').write_text(json.dumps(reg,default=str))
def a0dir():
    d=Path('a0'); d.mkdir(exist_ok=True); A0.to_parquet(d/'rows.parquet'); P=P_of(A0.y_first.to_numpy(),0.5); np.save(d/'p_A0.npy',P)
    (d/'registry.json').write_text(json.dumps(dict(info=dict(teams_by_rating=['1','2','3','0']),arms=dict(A0=dict(frl_all=R.frl(A0.y_first.to_numpy(),P))))))
a0dir()
def run(case):
    r=subprocess.run(['python3','tools/hinata/r2_battery.py','table','--runs','runs','--a0','a0','--out','o.json'],capture_output=True,text=True)
    msg=(r.stdout+r.stderr).strip().splitlines()
    tail=[l for l in msg if 'refused' in l or 'teacher-specific' in l or 'differs' in l or 'A2 rows' in l or 'rows are not' in l or 'covers' in l]
    if r.returncode: print(f'== {case}: REFUSED :: {tail[-1][:160] if tail else msg[-1][:160]}')
    else:
        t=json.load(open('o.json'))['teacher_specific']['selection']; print(f'== {case}: ok :: best {t["best"]["cand"]} goes_forward={t["goes_forward"]} ts_missing={t["ts_missing"]}')
def reset(): shutil.rmtree('runs',ignore_errors=True)
y=A0.y_first.to_numpy()
# 1: A6 with team 0 rows declaring 1,2,3
reset(); s=A0[A0.team=='0']; mk('A6',s,{'A6-400':P_of(s.y_first.to_numpy(),1)},dict(teams_top3=['1','2','3'])); run('1 A6 wrong team')
# 1b: A6 correct
reset(); s=A0[A0.team.isin(['1','2','3'])]; mk('A6',s,{'A6-400':P_of(s.y_first.to_numpy(),.9)},dict(teams_top3=['1','2','3'])); run('1b A6 exact top3 (inventory incomplete expected)')
# 2: A7fix partial 20 rows
reset(); s=A0.iloc[20:40]; mk('A7',s,{'A7fix-400':P_of(s.y_first.to_numpy(),1)},dict(teams_top3=['1','2','3'])); run('2 A7fix partial')
# 2b: altered series_key
reset(); s=A0.copy(); s['series_key']='x'; mk('A7',s,{'A7fix-400':P_of(y,1)},dict(teams_top3=['1','2','3'])); run('2b altered series_key')
# 3: A2 with 80 rows missing although all teams supported
reset(); s=A0.iloc[:20]; mk('A2',s,{'A2-400':P_of(s.y_first.to_numpy(),1)},dict(teams_top3=['1','2','3'])); run('3 A2 80 missing')
# 3b: A2 full
reset(); mk('A2',A0,{'A2-400':P_of(y,.9)},dict(teams_top3=['1','2','3'])); run('3b A2 full support (incomplete inv expected)')
# 4: full A7fix alone
reset(); mk('A7',A0,{'A7-400':P_of(y,.9),'A7fix-400':P_of(y,.95)},dict(teams_top3=['1','2','3'])); run('4 A7fix alone')
# 4b: complete inventory
reset(); s6=A0[A0.team.isin(['1','2','3'])]
mk('A2',A0,{'A2-400':P_of(y,.9),'A2-800':P_of(y,.9)},dict(teams_top3=['1','2','3']))
mk('A6',s6,{'A6-400':P_of(s6.y_first.to_numpy(),.9),'A6-800':P_of(s6.y_first.to_numpy(),.9)},dict(teams_top3=['1','2','3']))
mk('A7',A0,{'A7-400':P_of(y,.9),'A7fix-400':P_of(y,.95),'A7fix-800':P_of(y,.95)},dict(teams_top3=['1','2','3'])); run('4b complete inventory')
# 5: negative prob
reset(); P=P_of(y,.9); P[0]=[2,-1,0,0]; mk('A3',A0,{'A3-400':P},{}); run('5 negative prob')
# 6: A2 with a team present only in one fold -> exactly that cell may be missing
A0.loc[A0.team=='0','fold']='f0'; a0dir()
reset(); bad=(A0.team=='0').to_numpy(); s=A0[~bad]; mk('A2',s,{'A2-400':P_of(s.y_first.to_numpy(),.9)},{}); run('6 A2 exact unsupported cell')
reset(); s=A0[~bad].iloc[1:]; mk('A2',s,{'A2-400':P_of(s.y_first.to_numpy(),.9)},{}); run('6b A2 one extra missing')
