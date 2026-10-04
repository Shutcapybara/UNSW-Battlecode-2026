"""HB-1 feature vectors per teacher row (Data lane, kageyama; D-057 §C arms A1/A2/A5, D-062 §C).

For each game of a side list, re-derive the same sampled teacher processes as dataset.game_rows (same keep() rule,
same sides, same turn order), take each turn's block (engine oracle when it reproduces the game, else the replay
rebuild, flagged in blocks_src exactly as dataset.py does), and run cpp/hb1_feats: carthage-05's own HB-1 extractor
and direction GBT. Output per game, one parquet:
    keys    game, side, dragon, round, turn          (the join keys of the teacher rows)
    check   blocks_src, y_kind, y_first              (to verify the join against the encoder rows)
    prior   hb_pF, hb_pR, hb_pL                      (identical to hb1_scores.cpp's output)
    vector  hb_f_<name> float32, the 270 inputs of the direction GBT in model order (NaN = absent)
No encoder pass (fast). Label-free inputs: blocks + the process's own past actions, as the bot had them.
Rebuilt (non-oracle) rows lack bed timers, so their HB-1 features differ from play: train on blocks_src == oracle.

    python hb1_export.py SIDES.parquet REPLAY_DIR GAMES.parquet OUT_DIR PCT EXE [WORKER NWORKERS]
"""
import collections, json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
import block as B, labels as LB, rebuild
import dataset as DS
import hb1prior


def game_turns(game, data, seed, sides, pct):
    turns = collections.defaultdict(list)
    m = rebuild.walk(data, lambda i, sp, txt, ctx: turns[i].append((sp, txt, ctx)))
    src, real = 'rebuild', None
    if seed:
        import oracle
        o = oracle.run(data, int(seed, 16) if isinstance(seed, str) else int(seed), keep=True)
        if o['mismatched'] == 0 and o['extra_engine_turns'] == 0:
            real, src = o['blocks'], 'oracle'
    redacted = not any(l.startswith('TILE ') and not l.endswith(' 0 0') for l in m.text.splitlines())
    if src == 'rebuild' and redacted:
        src = 'rebuild_redacted'
    keys, seqs = [], []
    for did, seq in turns.items():
        sp = seq[0][0]
        if sides is not None and sp['team'] not in sides:
            continue
        if not DS.keep(game, did, pct):
            continue
        hb = []
        for k, (sp_, txt, ctx) in enumerate(seq):
            raw = real[did][k].decode() if real is not None else txt
            y = LB.label(ctx, B.parse_block(raw), did, sp['team'])
            hb.append((raw, y))
            keys.append((str(game), sp['team'], did, ctx['round'], k, src, y['y_kind'], y['y_first']))
        seqs.append((hb1prior.spawn_text(sp), hb))
    return keys, seqs, src


def run_exe(exe, seqs):
    r = subprocess.run([exe], input=hb1prior.fixture(seqs).encode(), capture_output=True, check=True)
    lines = r.stdout.decode().splitlines()
    head = lines[0].split()
    assert head[0] == 'NAMES' and int(head[1]) == len(head) - 2
    names = head[2:]
    X = np.array([[float(v) for v in l.split()] for l in lines[1:]], dtype=np.float64).reshape(-1, 3 + len(names))
    return names, X


def main():
    sides_f, rdir, games_f, out, pct, exe = sys.argv[1:7]
    w, nw = (int(sys.argv[7]), int(sys.argv[8])) if len(sys.argv) > 8 else (0, 1)
    pct = int(pct)
    T = pd.read_parquet(sides_f)
    seeds = dict(zip(*pd.read_parquet(games_f, columns=['game', 'seed']).astype(str).values.T))
    games = [g for g in sorted(T.game.astype(str).unique()) if (Path(rdir) / f'{g}.replay').exists()][w::nw]
    Path(out).mkdir(parents=True, exist_ok=True)
    t0, log = time.time(), []
    for g in games:
        part = Path(out) / f'{g}.parquet'
        if part.exists():
            continue
        sides = set(T[T.game.astype(str) == g].side)
        keys, seqs, src = game_turns(g, (Path(rdir) / f'{g}.replay').read_bytes(), seeds.get(g), sides, pct)
        if keys:
            names, X = run_exe(exe, seqs)
            assert len(X) == len(keys), (g, len(X), len(keys))
            df = pd.DataFrame(keys, columns=['game', 'side', 'dragon', 'round', 'turn', 'blocks_src', 'y_kind', 'y_first'])
            df['hb_pF'], df['hb_pR'], df['hb_pL'] = X[:, 0], X[:, 1], X[:, 2]
            F = pd.DataFrame(X[:, 3:].astype(np.float32), columns=['hb_f_' + n for n in names])
            df = pd.concat([df, F], axis=1)
        else:
            df = pd.DataFrame({'game': pd.Series([], dtype=str)})
        tmp = part.with_suffix('.tmp')
        df.to_parquet(tmp, index=False, compression='zstd')
        tmp.rename(part)
        log.append(dict(game=g, src=src, rows=len(keys)))
        print(g, src, len(keys), f'{time.time() - t0:.0f}s', flush=True)
    Path(out, f'_w{w}.log.json').write_text(json.dumps(log, indent=1))
    print('done worker', w)


if __name__ == '__main__':
    main()
