"""RO live trade accounting, identity-safe corpse fates and actual death lengths.
No bot experiments, cache writes, shared norms or simulator imports.
"""
import argparse,collections,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('repo','selection','out'):p.add_argument('--'+k,type=Path,required=True)
a=p.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
rows=[];trades=[]
for pair in json.loads(a.selection.read_text())['pairs']:
    for co in ('us','field'):
        m=pair[co];gid=str(m['game_id']);side=pair['side'];path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
        root=F._reader(path).object(0,0);assert root.num(0,'I')==2 and root.child(4).num(0,'B')&1
        assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash']==pair['map_hash']
        g=F.decode(path);assert g['winner'].lower()==m['winner'];R=g['last_round'];ev=g['events']
        if co=='us':assert root.text(1 if side=='A' else 2)=='14585'
        de={d['id']:d for d in ev['deaths']}
        counts=collections.Counter();mine=[d for d in ev['deaths'] if d['team']==side and d['round']>=150]
        for d in mine:
            counts['deaths']+=1
            if d['cause']=='h2h' and d['killer_team'] not in (side,None):
                counts['enemy_h2h']+=1;counts['mover' if d['id']==d['actor'] else 'partner']+=1
        acts=[x for x in ev['actions'] if x['team']==side and x['round']>=150]
        ctx=dict(pair=pair['pair'],cohort=co,game=gid,series_id=m['series_id'],map=g['map'],map_hash=m['map_hash'],map_era='post-m2',ranked=True,side=side,team=m['team_'+side.lower()],started_at=m['started_at'],replay_sha256=m['sha256'],official_winner=g['winner'],last_round=R)
        row=dict(**ctx,counts=dict(counts),dragon_turns=len(acts),end_after150=R>=150)
        rows.append(row)
        eats=collections.defaultdict(list);spawns=collections.defaultdict(list)
        for e in ev['eats']:
            if e['donor'] is not None:eats[(e['donor'],e['round']-e['age'],tuple(e['cell']))].append(e)
        for s in ev['spawns']:
            if s['donor'] is not None:spawns[s['donor']].append(s)
        for d in ev['deaths']:
            if d['cause']!='h2h' or not d.get('mutual') or d['killer_team'] in (None,d['team']):continue
            if not 150<=d['round']<=R-50:continue
            other=de[d['killer']];assert other['cause']=='h2h' and other['round']==d['round'] and other['actor']==d['id']
            assert d['id']==d['actor'] and other['killer']==d['id']
            ledger=collections.Counter();fates=[]
            for label,who in (('m',d),('p',other)):
                for s in spawns[who['id']]:
                    assert s['round']==d['round'] and s['origin']==who['team']
                    key=(who['id'],s['round'],tuple(s['cell']));es=eats[key];assert len(es)<=1
                    e=es[0] if es else None;dest='none' if e is None or e['round']>s['round']+50 else ('m' if e['team']==d['team'] else 'p')
                    ledger[label+'_born']+=1;ledger[label+'_to_'+dest]+=1
                    fates.append(dict(donor=who['id'],cell=s['cell'],birth=s['round'],eaten_round=e['round'] if e else None,eater_team=e['team'] if e else None,fate50=dest))
            mm=ledger['m_to_m']+ledger['p_to_m'];pp=ledger['m_to_p']+ledger['p_to_p']
            ml=d['length'];pl=other['length']
            trades.append(dict(**ctx,round=d['round'],mover_id=d['id'],partner_id=other['id'],mover_team=d['team'],partner_team=other['team'],focal_mover=d['team']==side,mover_length=ml,partner_length=pl,length_advantage=pl-ml,capture_advantage=mm-pp,material_advantage=(mm-ml)-(pp-pl),mover_net=mm-ml,partner_net=pp-pl,ledger=dict(ledger),fates=fates))
        print(gid,co,g['map'],dict(counts),flush=True)
a.out.mkdir(exist_ok=True,parents=True)
(a.out/'trade-sides.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
(a.out/'trade-events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in trades))
print('completed',len(rows),'games',len(trades),'fully-followed enemy trades')
