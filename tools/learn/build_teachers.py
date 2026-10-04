"""Full teacher rows, native on the Mac through the learn queue (Data lane, kageyama; D-062 §C, teachers_v1).

One zstd parquet shard per game under OUT_DIR (never concatenated): meta + encoder (int16 x_*) + labels (y_*) +
value targets + blocks_src + hb_pF/hb_pR/hb_pL + hb_f_* (HB-1's 270-feature vector, float32). Resumable: a game whose
shard exists is skipped; shards are written to .tmp and renamed. Workers are recycled every --per-child games (the
wasm engine's memory grows ~3 GB over ~60 games). Stops cleanly when free disk falls under --min-free-gb.

    python tools/learn/build_teachers.py [--sides build/learn/kageyama/teachers_v1.parquet]
        [--out build/learn/kageyama/teachers_v1] [--pct 15] [--jobs $ASAHI_MAX_WORKERS] [--limit N]

Every game must be split == train in the frozen manifest v2 (asserted); held-out maps never occur in teachers_v1.
"""
import argparse, hashlib, json, multiprocessing as mp, os, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path.cwd()
G = {}


def build_exe(out_dir):
    src = ROOT / 'tools/learn/cpp/hb1_feats.cpp'
    inc = ROOT / 'bots/carthage-05-free-sprint'
    h = hashlib.sha256(src.read_bytes() + b''.join((inc / f).read_bytes() for f in
                                                   ('hb1_features.hpp', 'hb1_gbt.hpp', 'hb1_compact.hpp',
                                                    'hb1_direction_compact.hpp'))).hexdigest()[:12]
    exe = Path(out_dir) / f'_bin/hb1_feats-{h}'
    if not exe.exists():
        exe.parent.mkdir(parents=True, exist_ok=True)
        cxx = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++') or 'c++'
        subprocess.run([cxx, '-std=c++20', '-O2', f'-I{inc}', str(src), '-o', str(exe) + '.tmp'], check=True)
        os.replace(str(exe) + '.tmp', exe)
    return str(exe), h


def init(args, exe):
    import pandas as pd
    G['a'], G['exe'] = args, exe
    G['T'] = pd.read_parquet(args.sides)
    G['S'] = pd.read_parquet(args.split_file).set_index('game')
    G['seeds'] = dict(zip(*pd.read_parquet(args.games_file, columns=['game', 'seed']).astype(str).values.T))


def one(g):
    import pandas as pd
    import dataset as DS
    a, T, S = G['a'], G['T'], G['S']
    part = Path(a.out) / f'{g}.parquet'
    if part.exists():
        return dict(game=g, skipped='exists')
    t0 = time.time()
    r = S.loc[g]
    assert r.split == 'train', (g, r.split)
    TT = T[T.game.astype(str) == g]
    meta = dict(series_key=r.series_key, split=r.split, map_hash=r.map_hash, map_era=r.map_era, ranked=bool(r.ranked),
                team_a=str(r.team_a), team_b=str(r.team_b), teacher_team=','.join(sorted(TT.team.astype(str))),
                dataset_version=DS.DATASET_VERSION, enc_version=DS.E.ENC_VERSION, label_version=DS.LB.LABEL_VERSION,
                source='server')
    rows, st = DS.game_rows(g, (Path(a.replay_dir) / f'{g}.replay').read_bytes(), G['seeds'].get(g), set(TT.side),
                            a.pct, True, meta, hb1_feats=G['exe'])
    df = DS.to_frame(rows) if rows else pd.DataFrame({'game': pd.Series([], dtype=str)})
    tmp = part.with_suffix('.tmp')
    df.to_parquet(tmp, index=False, compression='zstd')
    os.replace(tmp, part)
    return dict(game=g, **st, bytes=part.stat().st_size, sec=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sides', default='build/learn/kageyama/teachers_v1.parquet')
    ap.add_argument('--out', default='build/learn/kageyama/teachers_v1')
    ap.add_argument('--replay-dir', default='public_replays/corpus/replays')
    ap.add_argument('--games-file', default='build/s1/corpus/games.parquet')
    ap.add_argument('--split-file', default='build/learn/splits/games_split_v2.parquet')
    ap.add_argument('--pct', type=int, default=15)
    ap.add_argument('--jobs', type=int, default=int(os.environ.get('ASAHI_MAX_WORKERS', '6')))
    ap.add_argument('--per-child', type=int, default=15)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--min-free-gb', type=float, default=20)
    a = ap.parse_args()
    import pandas as pd
    Path(a.out).mkdir(parents=True, exist_ok=True)
    exe, h = build_exe(a.out)
    T = pd.read_parquet(a.sides)
    games = [g for g in sorted(T.game.astype(str).unique()) if (Path(a.replay_dir) / f'{g}.replay').exists()]
    missing = T.game.astype(str).nunique() - len(games)
    todo = [g for g in games if not (Path(a.out) / f'{g}.parquet').exists()]
    if a.limit:
        todo = todo[:a.limit]
    print(f'exe {exe} games {len(games)} (missing replay {missing}) todo {len(todo)} jobs {a.jobs}', flush=True)
    log = open(Path(a.out) / '_build.log.jsonl', 'a')
    t0, n = time.time(), 0
    with mp.get_context('spawn').Pool(a.jobs, initializer=init, initargs=(a, exe), maxtasksperchild=a.per_child) as P:
        for res in P.imap_unordered(one, todo):
            n += 1
            log.write(json.dumps(res, default=str) + '\n'); log.flush()
            if n % 25 == 0 or n == len(todo):
                print(f'{n}/{len(todo)} {time.time() - t0:.0f}s', flush=True)
            if shutil.disk_usage(a.out).free < a.min_free_gb * 2 ** 30:
                print('STOP: free disk under', a.min_free_gb, 'GB', flush=True)
                P.terminate()
                break
    Path(a.out, '_build.meta.json').write_text(json.dumps(dict(sides=a.sides, pct=a.pct, exe_sha12=h, games=len(games),
                                                               missing_replay=missing, finished=time.strftime('%FT%TZ', time.gmtime())), indent=1))
    print('done', n, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
