"""Action/trajectory equivalence and judge CPU extraction for frozen fixtures."""
import argparse
import json
import math
import re
from pathlib import Path
from summarize import actions, collect
from public_replay_review import Reader, analyse, load_map


def parity(left, right):
    a,b=actions(left),actions(right)
    sa,sb=analyse(left),analyse(right)
    fields=('curve','final','deaths','splits','transfers','actions','stats','winner','rounds')
    return dict(left=str(left),right=str(right),actions=len(a),
                equal_actions=a==b,equal_trajectory=all(sa[k]==sb[k] for k in fields),
                differing_fields=[k for k in fields if sa[k]!=sb[k]])


def cpu(path):
    r=Reader(path);root=r.object(0,0)
    m=load_map(root.text(0));teams={i:t for i,(t,_) in enumerate(m['dragons'])}
    samples={'A':[],'B':[]};timeouts={'A':0,'B':0};turns={'A':0,'B':0};memory={'A':None,'B':None};rnd=0
    for e in root.items(3):
        kind=e.num(0,'H');o=e.child(0);did=o.num()
        if kind==0:rnd=did
        elif kind==10:teams[o.num(4)]=teams[did]
        elif kind==4:
            turns[teams[did]]+=1
            timeouts[teams[did]]+=bool(o.num(4,'B')&1)
            if o.has(1):samples[teams[did]].append((o.child(1).num(0,'Q'),rnd,did))
    source='replay usage records'
    replay_counts={t:len(v) for t,v in samples.items()}
    # Installed unswbc 1.0.0 prints exact SandboxBot.live counters but its
    # engine callback returns only command bytes: replay usage pointers stay
    # null. Read the unrounded verbose turn records, then audit completeness
    # against independently decoded replay turn counts.
    logpath=Path(path).with_suffix('.log')
    if not any(replay_counts.values()) and logpath.exists():
        source='exact CLI judge-sandbox turn records (replay usage unavailable)'
        raw=logpath.read_text(errors='replace')
        for rr,did,team,points,mem in re.findall(r'^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)$',raw,re.M):
            samples[team].append((int(points),int(rr),int(did)))
            memory[team]=max(memory[team] or 0,int(mem))
        for team in ('A','B'):
            errors=re.findall(r'round \d+: bot \d+ \(team '+team+r'\) ([^\n]+)',raw)
            timeouts[team]=max(timeouts[team],sum(bool(re.search(r'ran out of time|timed out|out of fuel|CPU limit',x,re.I)) for x in errors))
    out={}
    for team,vals in samples.items():
        vals.sort();n=len(vals)
        complete=n==turns[team]
        out[team]=dict(turns=n,replay_turns=turns[team],coverage_complete=complete,
            source=source,replay_usage_records=replay_counts[team],memory_max_bytes=memory[team],timeouts=timeouts[team],
            p99=vals[math.ceil(.99*n)-1][0] if n else None,
            maximum=vals[-1] if n else None,
            conservative_pass=bool(n and complete and vals[-1][0]<80000000 and vals[math.ceil(.99*n)-1][0]<60000000 and not timeouts[team]))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('panel',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--against',type=Path);p.add_argument('--cpu',action='store_true');a=p.parse_args()
    rows=collect([a.panel]);out=[]
    if a.cpu:
        for row in rows:
            if row['outcome']=='error':continue
            out.append(dict(arm=row['arm'],opponent=row['opponent'],map=row['map'],side=row['side'],
                            usage=cpu(a.panel/'games'/row['replay']),faults=row['faults']))
    else:
        refs=collect([a.against]);lookup={(r['arm'],r['opponent'],r['map'],r['side']):r for r in refs}
        for row in rows:
            key=tuple(row[k] for k in ('arm','opponent','map','side'))
            ref=lookup.get(key)
            if ref:out.append(parity(a.panel/'games'/row['replay'],a.against/'games'/ref['replay']))
    a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
