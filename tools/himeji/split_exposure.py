"""Read-only split-relative queen exposure from a fingerprinted local panel.
Uses existing v5 frame caches only when the normal path/size/mtime/version key matches;
never writes a shared cache. Falls back to decoding. Two seats share a bootstrap block.
"""
import argparse,collections,gzip,hashlib,json,pickle,sys
from pathlib import Path

def one(arg):
    path,repo=map(Path,arg)
    sys.path.insert(0,str(repo))
    from tools.analysis.features import frame as F
    from tools.antioch.era import header
    st=path.stat(); key=hashlib.sha1(f'{path.resolve()}|{st.st_size}|{st.st_mtime_ns}|{F.FRAME_VERSION}'.encode()).hexdigest()[:16]
    cp=path.parent.parent/'frames'/f'{path.stem}.{key}.pkl.gz'
    if cp.exists():
        with gzip.open(cp,'rb') as f: g=pickle.load(f)
        assert g['frame_version']==F.FRAME_VERSION
        source='existing-cache'
    else: g=F.decode(path);source='decode'
    side='A' if g['botA'].endswith('rome-01-nodevil') else 'B'; assert g['bot'+side].endswith('rome-01-nodevil')
    q=min(i for i,(t,b) in g['rounds'][0].items() if t==side)
    splits=sorted(e['round'] for e in g['events']['splits'] if e['parent']==q)
    death=next((d for d in g['events']['deaths'] if d['id']==q),None)
    cells=collections.Counter(); death_by=collections.Counter(); risk=collections.Counter(); W,H=g['W'],g['H']
    def dist(a,b):
        dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);return max(min(dx,W-dx),min(dy,H-dy))
    for rnd,snap in enumerate(g['rounds'][:g['last_round']+1]):
        if q not in snap: continue
        b=snap[q][1];phase='0-49' if rnd<50 else '50-149' if rnd<150 else '150+'
        length='2-3' if len(b)<=3 else '4-7' if len(b)<=7 else '8+'
        prior=[s for s in splits if s<rnd]
        # Same-round splitting is a separate bin: avoid using events later in a round to define start-of-round exposure.
        band='split-round' if rnd in splits else 'after1-3' if prior and rnd-prior[-1]<=3 else 'other'
        ally=any(dist(b[0],c)<=2 for i,(t,body) in snap.items() if i!=q and t==side for c in body)
        enemy=any(dist(b[0],body[0])<=3 for i,(t,body) in snap.items() if t!=side)
        strat=(phase,length,int(ally),int(enemy),band)
        died=int(death is not None and death['round']==rnd)
        cells[strat+('risk',)]+=1;cells[strat+('deaths',)]+=died;risk[band]+=1
        if died:death_by[band]+=1
    out=[]
    for k in sorted({k[:-1] for k in cells}):out.append(dict(phase=k[0],length=k[1],ally2=k[2],enemy3=k[3],band=k[4],risk=cells[k+('risk',)],deaths=cells[k+('deaths',)]))
    official=header(path)
    return dict(game=path.stem,map=g['map'],opponent=g['botB' if side=='A' else 'botA'],side=side,source=source,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),last_round=g['last_round'],queen_splits=len(splits),queen_death=death,own_won=official['res_winner']==side,cells=out,risk=dict(risk),deaths=dict(death_by))

def main():
    from concurrent.futures import ProcessPoolExecutor
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--seed',type=int,default=1);a=ap.parse_args()
    paths=sorted((a.panel/'replays').glob(f's{a.seed}__*.replay')); assert len(paths)==160,len(paths)
    a.out.mkdir(parents=True,exist_ok=True); op=a.out/'exposure-rows.jsonl'
    done={}
    if op.exists():done={r['game']:r for r in map(json.loads,op.read_text().splitlines())}
    with op.open('a') as f, ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for i,row in enumerate(ex.map(one,[(str(p),str(a.repo)) for p in paths if p.stem not in done])):
            f.write(json.dumps(row)+'\n');f.flush(); print(f'{len(done)+i+1}/160 {row["game"]} {row["source"]}',flush=True)
    print('DONE')
if __name__=='__main__':main()
