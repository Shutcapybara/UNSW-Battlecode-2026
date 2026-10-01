"""Freeze and audit first existing live team-7 post-rule replays; no shared writes.

python live_first.py --repo MAIN --decoder HIMEJI --out SCRATCH
Uses Himeji post_refs.one (raw extraction only, never q.connect or shared norms).
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--decoder',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(exist_ok=True,parents=True)
    source=a.out/'games.jsonl';corp=a.repo/'public_replays/corpus'
    if not source.exists():
        raw=(corp/'index.jsonl').read_bytes()
        idx={r['game_id']:r for r in map(json.loads,raw.splitlines())}
        games=sorted((r for r in idx.values() if r['started_at']>='2026-10-01T09:23' and 7 in (r['team_a'],r['team_b']) and r['status']=='completed'),key=lambda r:r['game_id'])
        source.write_text(''.join(json.dumps(r)+'\n' for r in games))
        ladder=sorted((corp/'ladder').glob('*.json'))[-1]
        ladderraw=ladder.read_bytes();(a.out/'ladder.json').write_bytes(ladderraw)
        manifest=dict(index_unique=len(idx),index_sha256=hashlib.sha256(raw).hexdigest(),
                      latest_start=max(r['started_at'] for r in idx.values()),games=len(games),
                      game_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                      ladder=ladder.name,ladder_sha256=hashlib.sha256(ladderraw).hexdigest(),
                      cohort_counts=dict(collections.Counter('ranked' if r['ranked'] else 'unranked' for r in games)),
                      post_start='2026-10-01T09:23',decoder_parent='99b9dbd11',
                      selection='All completed collected post-rule team-7 games at freeze; no sampling or exclusions')
        (a.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(manifest),flush=True)
    sys.path.insert(0,str(a.decoder))
    from tools.himeji import post_refs as P
    from tools.analysis.features import frame as F
    P.init(str(a.decoder))
    target=a.out/'sides.jsonl'
    done={str(r['game']) for r in map(json.loads,target.read_text().splitlines())} if target.exists() else set()
    for m in map(json.loads,source.read_text().splitlines()):
        if str(m['game_id']) in done:continue
        path=corp/'replays'/f"{m['game_id']}.replay"
        assert hashlib.sha256(path.read_bytes()).hexdigest()==m['sha256']
        root=F._reader(path).object(0,0)
        bot_a,bot_b=root.text(1),root.text(2)
        assert bot_a==m['bot_a'] and bot_b==m['bot_b']
        rows=P.one((m,str(corp)))
        assert len(rows)==2 and all('error' not in r for r in rows),rows
        assert all(r['queen_field_matches'] for r in rows)
        assert all(r['official_winner'].lower()==m['winner'] for r in rows)
        assert sum(r['won'] for r in rows)==1
        for r in rows:
            r['submission']=bot_a if r['side']=='A' else bot_b
            r['opponent_submission']=bot_b if r['side']=='A' else bot_a
        with target.open('a') as f:
            f.write(''.join(json.dumps(r,default=float)+'\n' for r in rows))
        done.add(str(m['game_id']))
        print('audited',m['game_id'],m['map_name'],'ranked',m['ranked'],'count',len(done),flush=True)


if __name__=='__main__':main()
