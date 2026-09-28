"""Observed paired results, coverage and replay action hashes, without model fill."""
import argparse
from collections import defaultdict
import hashlib
import gzip
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from public_replay_review import Reader


def actions(path):
    # Repeated parity/ablation reports share immutable replay bytes. Cache the
    # parsed commands by content hash, using JSON rather than executable pickle.
    path=Path(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    cache=Path('/private/tmp/vicious-actions-v1');cache.mkdir(exist_ok=True)
    cached=cache/(digest+'.json.gz')
    if cached.exists():
        with gzip.open(cached,'rt') as f:raw=json.load(f)
        return [(r,a,k,tuple(arg) if isinstance(arg,list) else arg) for r,a,k,arg in raw]
    reader=Reader(path);root=reader.object(0,0);rnd=-1;actor=-1;out=[]
    for e in root.items(3):
        kind=e.num(0,'H');o=e.child(0)
        if kind==0:rnd=o.num()
        elif kind==1:actor=o.num()
        elif kind==4 and o.has(0):
            a=o.child(0);ak=a.num(0,'H')
            if ak==0:
                s,at,word=reader.pointer(a.s,a.a+a.dw);count=word>>35
                arg=tuple(struct.unpack_from('<'+'H'*count,reader.segments[s],at*8)) if count else ()
            elif ak==1:arg=a.num(4)
            else:arg=None
            out.append((rnd,actor,ak,arg))
    with tempfile.NamedTemporaryFile(dir=cache,delete=False) as f:temp=Path(f.name)
    try:
        with gzip.open(temp,'wt') as f:json.dump(out,f,separators=(',',':'))
        os.replace(temp,cached)
    finally:temp.unlink(missing_ok=True)
    return out


def collect(paths):
    rows=[]
    for p in paths:
        for r in json.loads((p/'results.json').read_text()):
            r=dict(r,directory=str(p));rows.append(r)
    return rows


def summarize(rows, weights, control):
    good=[r for r in rows if r['outcome']!='error' and not r.get('analysis_error')]
    byarm=defaultdict(list)
    for r in good:byarm[r['arm']].append(r)
    controls={(r['opponent'],r['map'],r['side']):r for r in byarm.get(control,[])}
    result={}
    for arm,rs in byarm.items():
        cells=defaultdict(list);maps=defaultdict(list);flips=[];changed=[];stages=defaultdict(list)
        for r in rs:
            score=0.5 if r['outcome']=='draw' else float(r['outcome']==r['side'])
            r['score']=score;maps[r['map']].append(score);cells[(r['opponent'],r['map'])].append(score)
            stats=json.loads((Path(r['directory'])/'games'/r['stats']).read_text())
            for rnd in (30,80,250,400,500):
                pt=next((p for p in stats['curve'] if p['round']==min(rnd,stats['rounds'])),None)
                if pt:
                    # Terminal state carried forward; early eliminations stay included.
                    stages[rnd].append({k:pt[r['side']].get(k,0) for k in ('units','total','longest','pearls','splits')})
            key=(r['opponent'],r['map'],r['side']);base=controls.get(key)
            if base and arm!=control:
                bs=.5 if base['outcome']=='draw' else float(base['outcome']==base['side'])
                if score!=bs:flips.append(dict(opponent=key[0],map=key[1],side=key[2],delta=score-bs))
                left=actions(Path(base['directory'])/'games'/base['replay'])
                right=actions(Path(r['directory'])/'games'/r['replay'])
                first=next((i for i,(a,b) in enumerate(zip(left,right)) if a!=b),None)
                if first is not None or len(left)!=len(right):
                    idx=first if first is not None else min(len(left),len(right))
                    changed.append(dict(opponent=key[0],map=key[1],side=key[2],
                        before=left[idx] if idx<len(left) else None,after=right[idx] if idx<len(right) else None))
        coverage=sum(weights[m] for m in maps)
        def group(prefix):
            chosen=[m for m in maps if (m.startswith(('mc26_','md26_'))) == prefix]
            mass=sum(weights[m] for m in chosen)
            return sum(weights[m]*sum(maps[m])/len(maps[m]) for m in chosen)/mass if mass else None
        result[arm]=dict(games=len(rs),wins=sum(r['score']==1 for r in rs),draws=sum(r['score']==.5 for r in rs),
                        losses=sum(r['score']==0 for r in rs),map_weight_coverage=coverage,missing_map_mass=1-coverage,
                        observed_weighted=sum(weights[m]*sum(v)/len(v) for m,v in maps.items())/coverage,
                        original=group(False),synthetic=group(True),
                        maps={m:dict(wins=sum(v),games=len(v)) for m,v in maps.items()},
                        paired_flips=flips,changed_fixtures=changed,
                        stage_means={rnd:{k:sum(x[k] for x in ps)/len(ps) for k in ps[0]} for rnd,ps in stages.items()})
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('panels',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--control',default='vicious-v01-frozen');a=p.parse_args()
    camp=Path(json.loads((ROOT/'tools/vicious/current.json').read_text())['directory'])
    weights=json.loads((camp/'baseline/experiment_data__bot-ratings__latest.json').read_text())['map_weights']
    rs=summarize(collect(a.panels),weights,a.control)
    a.out.write_text(json.dumps(rs,indent=2)+'\n')
    for b,r in rs.items():print(b,r['wins'],r['draws'],r['losses'],'weighted',round(r['observed_weighted'],3),'coverage',round(r['map_weight_coverage'],3),'changed',len(r['changed_fixtures']))
