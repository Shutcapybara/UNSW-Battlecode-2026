"""Read-only event-order audit of Rome03's late own-count proxy on saved Portals pairs.
No F.load (which could write caches), runner, norm builder or bot invocation.
"""
import argparse,collections,gzip,hashlib,json,pickle,sys,time
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--rome',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=int,default=300);a=ap.parse_args()
    sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
    assert F.FRAME_VERSION==7
    roots={};selection=[]
    for panel in ['z1','gen']:
        for bot,fp in [('rome-01-nodevil','28132ee5'),('rome-03-queen-state-convert','3c786776')]:
            root=a.rome/'build/zoo'/f'{panel}-{bot}-{fp}'
            rows=[json.loads(s) for s in (root/'index.jsonl').read_text().splitlines()]
            rr=[r for r in rows if r['map']==('portals' if panel=='z1' else 'var/portals_tr')]
            assert len(rr)==48
            roots[(panel,bot)]=root
            for r in rr:selection.append({'panel':panel,'bot':bot,'root':str(root),'index_sha256':hashlib.sha256((root/'index.jsonl').read_bytes()).hexdigest(),'index':r})
    a.out.mkdir(exist_ok=True)
    (a.out/'rome-selection.json').write_text(json.dumps({'rule':'Every saved Portals fixture, both panels, candidate and parent, seeds1-3/both seats; selected because published result identified largest loss. Exploratory mechanism diagnostic, not heldout test.','decoder_sha256':hashlib.sha256(Path(F.__file__).read_bytes()).hexdigest(),'fixtures':selection},indent=2)+'\n')
    p=a.out/'rome-trigger-rows.jsonl';done={(r['panel'],r['bot'],r['game']) for r in map(json.loads,p.read_text().splitlines())} if p.exists() else set();start=time.monotonic()
    for item in selection:
        ix=item['index'];bot=item['bot'];panel=item['panel'];key=(panel,bot,ix['game'])
        if key in done:continue
        if time.monotonic()-start>a.seconds:break
        root=Path(item['root']);replay=root/ix['replay'];st=replay.stat();cachekey=hashlib.sha1(f'{replay.resolve()}|{st.st_size}|{st.st_mtime_ns}|7|123'.encode()).hexdigest()[:16];cache=root/'frames'/f'{replay.stem}.{cachekey}.pkl.gz'
        assert cache.exists(), f'Missing authoritative existing cache: {cache}'
        with gzip.open(cache,'rb') as f:g=pickle.load(f)
        side='A' if Path(g['botA']).name==bot else 'B';assert Path(g['botA' if side=='A' else 'botB']).name==bot
        first=g['rounds'][0];queen=min(i for i,(s,b) in first.items() if s==side);teams={i:s for i,(s,b) in first.items()};live=set(teams);counts=collections.Counter(teams.values());trigger=None;eligible_actions=dead_actions=0;rnd=-1
        raw=F._reader(replay).object(0,0)
        for e in raw.items(3):
            k=e.num(0,'H');o=e.child(0);i=o.num()
            if k==0:rnd=i
            elif k==10:
                child=o.num(4);assert child not in live;teams[child]=teams[i];live.add(child);counts[teams[i]]+=1
            elif k==11:
                assert i in live;live.remove(i);counts[teams[i]]-=1
            elif k==1 and teams.get(i)==side and rnd>=250 and counts[side]<=5:
                eligible_actions+=1;alive=queen in live;dead_actions+=not alive
                if trigger is None:trigger={'round':rnd,'actor':i,'units':counts[side],'queen_alive':alive,'own_live_ids':sorted(j for j in live if teams[j]==side)}
        assert counts[side]==g['final'][side]['units']
        final=g['rounds'][-1];qlen=len(final[queen][1]) if queen in final else 0;assert qlen==g['final'][side]['queen']
        opponent=Path(g['botB' if side=='A' else 'botA']).name
        row={'panel':panel,'bot':bot,'game':ix['game'],'fixture':[ix['map'],ix['seed'],opponent,side],'toolkit':ix['toolkit'],'sha256':hashlib.sha256(replay.read_bytes()).hexdigest(),'cache_sha256':hashlib.sha256(cache.read_bytes()).hexdigest(),'map_hash':g['map_hash'],'queen':queen,'first_trigger':trigger,'eligible_actions':eligible_actions,'dead_queen_eligible_actions':dead_actions,'queen_death':next((d for d in g['events']['deaths'] if d['id']==queen),None),'reached490':g['last_round']>=490,'queen490':len(g['rounds'][490][queen][1]) if g['last_round']>=490 and queen in g['rounds'][490] else 0 if g['last_round']>=490 else None,'winner':g['winner'],'score':1 if g['winner']==side else .5 if g['winner'] in ['draw','tie',None] else 0,'reason':g['reason'],'index_winner':ix['winner'],'final':g['final'][side]}
        with p.open('a') as f:f.write(json.dumps(row)+'\n')
        done.add(key)
        if len(done)%16==0:print('done',len(done),'of',len(selection),'seconds',round(time.monotonic()-start),flush=True)
    print('checkpoint',len(done),'of',len(selection),flush=True)
if __name__=='__main__':main()
