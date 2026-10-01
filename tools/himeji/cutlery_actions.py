"""Read-only queen command/official-result audit; freeze input, checkpoint each replay.

Usage: python cutlery_actions.py --repo MAIN --decoder WT --out SCRATCH
Reads existing Nara cause rows and corpus only. No simulator, S-1 helper or caches.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import sys


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--decoder', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    source = a.out / 'source-rows.jsonl'
    if not source.exists():
        p = a.repo / 'build/nara/queen_cause.jsonl'
        raw = p.read_bytes()
        idxraw = (a.repo / 'public_replays/corpus/index.jsonl').read_bytes()
        idx = {str(r['game_id']): r for r in map(json.loads, idxraw.splitlines())}
        picked = [r for r in map(json.loads, raw.splitlines()) if r.get('team') == 306]
        assert len({r['game'] for r in picked}) == len(picked)
        for r in picked:
            m = idx[str(r['game'])]
            assert m['status'] == 'completed' and r['started'] >= '2026-10-01T09:23'
            r.update(ranked=m['ranked'], series_id=m['series_id'], replay_sha256=m['sha256'],
                     opponent=m['team_b'] if r['side'] == 'A' else m['team_a'])
        source.write_text(''.join(json.dumps(r) + '\n' for r in sorted(picked, key=lambda r:r['started'])))
        manifest = dict(peer_artifact=str(p), peer_sha256=hashlib.sha256(raw).hexdigest(),
                        peer_rows=len(raw.splitlines()), selected=len(picked),
                        corpus_index_sha256=hashlib.sha256(idxraw).hexdigest(), corpus_games=len(idx),
                        latest_start=max(r['started_at'] for r in idx.values()),
                        post_team7=sum(r['started_at'] >= '2026-10-01T09:23' and 7 in (r['team_a'],r['team_b']) for r in idx.values()),
                        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        (a.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        print(json.dumps(manifest), flush=True)
    sys.path.insert(0, str(a.decoder))
    from tools.analysis.features import frame as F
    out = a.out/'action-rows.jsonl'
    done = {r['game'] for r in rows(out)} if out.exists() else set()
    for r in rows(source):
        if r['game'] in done:
            continue
        p = a.repo/'public_replays/corpus/replays'/f"{r['game']}.replay"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == r['replay_sha256']
        root = F._reader(p).object(0,0)
        m = F.terrain(root.text(0))[0]
        q0 = min(i for i,(tm,_) in enumerate(m['dragons']) if tm == r['side'])
        res = root.child(4)
        assert res.num(0,'B') & 1
        winner = ('A','B')[res.num(6,'H')] if res.num(4,'H') == 1 else 'draw'
        qfinal = res.child(0 if r['side']=='A' else 1).num(12)
        rnd = -1
        action = None
        death = None
        for e in root.items(3):
            k = e.num(0,'H')
            if k not in (0,4,11):
                continue
            o = e.child(0)
            if k == 0:
                rnd = o.num()
            elif o.num() == q0 and k == 4:
                action = dict(round=rnd, kind=None, tle=bool(o.num(4,'B') & 1))
                if o.has(0):
                    ak = o.child(0).num(0,'H')
                    action['kind'] = ('move','split','suicide')[ak] if ak < 3 else str(ak)
            elif o.num() == q0 and k == 11:
                assert death is None
                death = dict(round=rnd, cause=F.DEATH_CAUSES[o.num(4,'H')], action=action)
        assert (death['round'] if death else None) == r['q_death_round']
        assert (death['cause'] if death else None) == r['q_death_cause']
        assert bool(qfinal) == (death is None)
        # Actual start-of-round 490 is observed only when round 490 was played.
        reached = rnd >= 490
        alive490 = reached and (death is None or death['round'] >= 490)
        record = dict(r, q0=q0, last_played_round=rnd, official_rl=res.num(2,'H')==1,
                      official_winner=winner, official_won=winner==r['side'], queen_final=qfinal,
                      reached490=reached, alive490=alive490, death_action=death['action'] if death else None)
        with out.open('a') as f:
            f.write(json.dumps(record)+'\n')
        done.add(r['game'])
        if len(done)%20==0:
            print(f'{len(done)} replays verified', flush=True)
    print(f'Complete: {len(done)} replays', flush=True)


if __name__ == '__main__':
    main()
