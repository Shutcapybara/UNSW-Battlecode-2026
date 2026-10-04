"""Verify and describe a frozen collection-recovery delta, not a representative live rate.
RO local replay headers; whole-series bootstrap within mode; full map hashes retained.
"""
import argparse, collections, hashlib, json, sys
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser()
for key in ('repo','rows','metadata','out'): p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args();sys.path.insert(0,str(a.repo));from tools.analysis.features import frame as F
a.out.mkdir(exist_ok=True,parents=True)
rs=[json.loads(x) for x in a.rows.read_text().splitlines()]
meta=json.loads(a.metadata.read_text());idx={str(m['game_id']):m for m in meta}
compact=[]
keys='game side team opp started_at series_id ranked last_round official_winner won reason round_limit queen_id reached490 queen_alive490 queen_length490 longest490 total490 queen_alive_end queen_length_end total_end opp_total_end queen_death_round submission replay_sha256'.split()
for gid,m in idx.items():
    path=a.repo/'public_replays/corpus/replays'/f'{gid}.replay'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
    root=F._reader(path).object(0,0);res=root.child(4)
    assert root.num(0,'I')==2 and res.num(0,'B')&1
    winner=('a','b')[res.num(6,'H')] if res.num(4,'H')==1 else 'draw'
    assert winner==m['winner']
    assert hashlib.sha256(root.text(0).encode()).hexdigest()==m['map_hash']
    game=[r for r in rs if r['game']==gid]; assert len(game)==2
    for r in game:
        assert m['map_hash'].startswith(r['map_hash']) and r['queen_field_matches']
        assert r['queen_length_end']==res.child(0 if r['side']=='A' else 1).num(12)
        assert r['official_winner'].lower()==winner
        other=next(o for o in game if o['side']!=r['side'])
        z={k:r[k] for k in keys}; z.update(map=r['map'],map_hash=m['map_hash'],map_era='post-m2',opp_submission=other['submission'],opp_total490=other['total490'],opp_queen490=other['queen_length490'],opp_queen_end=other['queen_length_end'])
        assert r['started_at']>='2026-10-02T04:31:00'
        compact.append(z)
ours=[r for r in compact if r['team']=='7']
assert len(ours)==len(idx)==79 and all(r['submission']=='14585' for r in ours)
def counts(rows):
    rl=[r for r in rows if r['round_limit']];lost=[r for r in rows if r['won']==0 and r['official_winner']!='draw']; qlost=[r for r in lost if r['reason']=='queen']
    reach=[r for r in rows if r['reached490']]
    leading490=[r for r in rl if r['total490']>r['opp_total490']]
    leadingend=[r for r in rl if r['total_end']>r['opp_total_end']]
    rllost=[r for r in lost if r['round_limit']]
    return dict(games=len(rows),series=len({r['series_id'] for r in rows}),hashes=len({r['map_hash'] for r in rows}),wins=sum(r['won'] for r in rows),losses=len(lost),queen_losses=len(qlost),reached490=len(reach),censored490=len(rows)-len(reach),queen_alive490=sum(r['queen_alive490'] for r in reach),round_limit=len(rl),queen_alive_end_rl=sum(r['queen_alive_end'] for r in rl),rl_losses=len(rllost),leading490=len(leading490),leading490_losses=sum(r in lost for r in leading490),leadingend=len(leadingend),leadingend_losses=sum(r in lost for r in leadingend))
rng=np.random.default_rng(3333)
modes=[]
for mode in (True,False):
    x=[r for r in ours if r['ranked']==mode];sids=sorted({r['series_id'] for r in x});blocks={s:[r for r in x if r['series_id']==s] for s in sids}
    ci=collections.defaultdict(list)
    for _ in range(4000):
        b=[r for s in rng.choice(sids,len(sids),replace=True) for r in blocks[s]];c=counts(b)
        for label,num,den in [('queen_loss_share_of_losses','queen_losses','losses'),('queen_loss_share_of_games','queen_losses','games')]:
            if c[den]:ci[label].append(c[num]/c[den])
    modes.append(dict(ranked=mode,**counts(x),series_boot95={k:np.quantile(v,[.025,.975]).tolist() for k,v in ci.items()},first=min(r['started_at'] for r in x),last=max(r['started_at'] for r in x)))
perhash=[]
for key in sorted({(r['ranked'],r['map'],r['map_hash']) for r in ours}):
    x=[r for r in ours if (r['ranked'],r['map'],r['map_hash'])==key]
    perhash.append(dict(ranked=key[0],map=key[1],map_hash=key[2],**counts(x)))
(a.out/'recovered-sides.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in compact))
result=dict(contract='Recovered delta only, 79 newly indexed existing games; ranked/unranked separated, fullhash rows retained, no population trend or promotion claim. 4000 series bootstrap seed3333; few series and selection bias remain. Original queen, actual490 reach; queen loss=official round-limit queen verdict loss. Lead is total length strictly greater, restricted to round-limit games.',modes=modes,per_hash=perhash,known_missing_recovered=sorted(set(idx)&{'1020397','1020398','1020399','1020400','1020401','1019954'}),official_payload_map_checks=len(idx),queen_header_checks=len(compact),known_opponent_submission_fields=sum(bool(r['opp_submission']) for r in ours))
(a.out/'recovery-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='per_hash'},indent=2))
