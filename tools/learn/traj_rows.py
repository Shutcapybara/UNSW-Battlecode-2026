"""Trajectory columns (traj.py, TRAJ_VERSION 1) for the teachers_v1 rows (D-067 §E.7; Data lane, kageyama).
For each teachers_v1 shard (one game), re-walk the server replay (rebuild.walk gives each process's blocks in order;
the trajectory block reads no bed countdowns, so rebuilt blocks are exact for it), run traj.Traj per process over ALL
its turns (history needs every turn, sampled or not), and write the shard's keys + x_traj_* columns:
    build/learn/kageyama/traj_v1/<game>.parquet   keys: game, dragon, round, turn
Join on (game, dragon, round, turn). Resumable; per-game shards; a manifest at the end.
    python tools/learn/traj_rows.py [--src build/learn/kageyama/teachers_v1] [--out build/learn/kageyama/traj_v1]
                                    [--replays public_replays/corpus/replays] [--jobs 8] [--limit N]"""
import argparse, collections, hashlib, json, os, sys, time
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rebuild, block as B, traj as T

A = None


def one(shard):
    import pandas as pd
    g = Path(shard).stem
    out = Path(A.out) / f'{g}.parquet'
    if out.exists():
        return g, 'skip', 0
    K = pd.read_parquet(shard, columns=['game', 'dragon', 'round', 'turn'])
    if not len(K):
        return g, 'empty', 0
    want = set(K.dragon.unique().tolist())
    turns = collections.defaultdict(list)
    rebuild.walk((Path(A.replays) / f'{int(K.game.iloc[0])}.replay').read_bytes(),
                 lambda i, sp, txt, ctx: turns[i].append((sp, txt)) if i in want else None)
    vals = {}
    for did, seq in turns.items():
        sp = seq[0][0]
        t = T.Traj(B.Spawn(sp['id'], sp['team'], sp['W'], sp['H'], sp['unit_limit']))
        for k, (_, txt) in enumerate(seq):
            b = B.parse_block(txt)
            vals[(did, b.round, k)] = t.observe(b)
    rows = [vals.get((int(d), int(r), int(k))) for d, r, k in zip(K.dragon, K['round'], K.turn)]
    miss = sum(v is None for v in rows)
    if miss:
        return g, f'missing {miss}', len(K)
    D = K.copy()
    for j, c in enumerate(T.names()):
        D[c] = [v[j] for v in rows]
        D[c] = D[c].astype('int32')
    tmp = out.with_suffix('.tmp')
    D.to_parquet(tmp, index=False); os.replace(tmp, out)
    return g, 'ok', len(K)


def main():
    global A
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='build/learn/kageyama/teachers_v1'); ap.add_argument('--out', default='build/learn/kageyama/traj_v1')
    ap.add_argument('--replays', default='public_replays/corpus/replays'); ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--limit', type=int, default=0)
    A = ap.parse_args()
    Path(A.out).mkdir(parents=True, exist_ok=True)
    shards = sorted(str(p) for p in Path(A.src).glob('*.parquet'))
    if A.limit: shards = shards[:A.limit]
    t0 = time.time(); res = collections.Counter(); rows = 0; bad = []
    with Pool(A.jobs, initializer=_init, initargs=(A,), maxtasksperchild=50) as P:
        for g, st, n in P.imap_unordered(one, shards, chunksize=4):
            res[st.split()[0]] += 1; rows += n
            if st.startswith('missing'): bad.append((g, st))
    man = dict(name='kageyama-traj-v1', traj_version=T.TRAJ_VERSION, columns=T.names(), src=A.src, out=A.out,
               shards=len(shards), status=dict(res), rows_this_run=rows, missing=bad[:50], seconds=round(time.time() - t0),
               code_sha=hashlib.sha256(Path(T.__file__).read_bytes()).hexdigest())
    Path(A.out, '_manifest.json').write_text(json.dumps(man, indent=1))
    print(json.dumps({k: v for k, v in man.items() if k != 'missing'}))


def _init(a):
    global A
    A = a


if __name__ == '__main__':
    main()
