"""Replay -> training rows (Data lane, kageyama). One row per sampled dragon-turn:
meta + encoder vector (encode.py, int16) + labels (labels.py) + value targets.

Blocks: the official engine re-run (oracle.py: the server seed + template beds reproduce server games exactly, so the
blocks carry the real bed countdowns) when unswbc is importable and the game's seed is known; otherwise the replay
rebuild (rebuild.py), whose countdowns are unknown on server replays (pearl_in = 0, cd_known = 0). Every oracle game is
also cross-checked against the rebuild (all fields but countdowns); a mismatch drops to the rebuild and is counted.

    python3 tools/learn/dataset.py OUT.parquet --games g1,g2 | --games-file list.txt  [--sides team:62 | --sides all]
           [--process-pct 100] [--split-file build/learn/splits/games_split_v2.parquet] [--allow-split train,val]

Rows on held-out maps or outside --allow-split are never written (the leakage audit re-checks every file).
"""
import argparse, collections, hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import block as B, encode as E, labels as LB, rebuild

DATASET_VERSION = 1


def keep(game, dragon, pct):
    return pct >= 100 or int(hashlib.sha1(f'{game}/{dragon}'.encode()).hexdigest()[:8], 16) % 100 < pct


def outcome(data):
    """Official engine verdict (GameResult) and final round from the replay."""
    r = rebuild.reader(data)
    root = r.object(0, 0)
    res = root.child(4)
    winner = None
    if res.num(0, 'B') & 1 and res.num(4, 'H') == 1:
        winner = 'AB'[res.num(6, 'H')]
    reason = 'elimination' if (res.num(0, 'B') & 1 and res.num(2, 'H') == 0) else 'round_limit'
    return winner, reason


def game_rows(game, data, seed=None, sides=None, pct=100, use_oracle=True, meta=None):
    meta = meta or {}
    turns = collections.defaultdict(list)
    m = rebuild.walk(data, lambda i, sp, txt, ctx: turns[i].append((sp, txt, ctx)))
    src = 'rebuild'
    real = None
    stats = dict(oracle_mismatch=0)
    if use_oracle and seed:
        try:
            import oracle
            import unswbc.engine  # noqa: F401
            o = oracle.run(data, int(seed, 16) if isinstance(seed, str) else int(seed), keep=True)
            if o['mismatched'] == 0 and o['extra_engine_turns'] == 0:
                real, src = o['blocks'], 'oracle'
            else:
                stats['oracle_mismatch'] = o['mismatched'] or 1
        except ImportError:
            pass
    redacted = not any(l.startswith('TILE ') and not l.endswith(' 0 0') for l in m.text.splitlines())
    if src == 'rebuild' and redacted:
        src = 'rebuild_redacted'
    winner, reason = outcome(data)
    last_round = max((c['round'] for v in turns.values() for _, _, c in v), default=0)
    rows = []
    for did, seq in turns.items():
        sp = seq[0][0]
        if sides is not None and sp['team'] not in sides:
            continue
        if not keep(game, did, pct):
            continue
        enc = E.Encoder(B.Spawn(sp['id'], sp['team'], sp['W'], sp['H'], sp['unit_limit']))
        for k, (sp_, txt, ctx) in enumerate(seq):
            raw = real[did][k].decode() if real is not None else txt
            b = B.parse_block(raw)
            if src == 'rebuild_redacted':
                b.tiles = [(x, y, p, -2 if (c == -1 and (x, y) in _template_beds(m)) else c) for x, y, p, c in b.tiles]
            x = enc.observe(b)
            y = LB.label(ctx, b, did, sp['team'])
            if y['y_kind'] == 0:
                enc.act('move', list(y['y_seq']))
            elif y['y_kind'] == 1:
                enc.act('split', child=y['y_child'], rnd=ctx['round'])
            elif y['y_kind'] == 2:
                enc.act('invalid')
            else:
                enc.act('none')
            res = 0.5 if winner is None else 1.0 if winner == sp['team'] else 0.0
            rows.append(dict(meta, game=str(game), map=m.name, side=sp['team'], dragon=did, round=ctx['round'],
                             turn=k, blocks_src=src, outcome=res, end_reason=reason, last_round=last_round,
                             x=x, **y))
    return rows, dict(stats, src=src, turns=sum(len(v) for v in turns.values()), rows=len(rows))


_TB = {}


def _template_beds(m):
    if m.name not in _TB:
        import oracle
        _TB[m.name] = rebuild.Map(oracle.templates()[m.name]).beds
    return _TB[m.name]


def to_frame(rows):
    import pandas as pd, numpy as np
    names = E.names()
    X = np.asarray([r.pop('x') for r in rows], dtype=np.int16)
    df = pd.DataFrame(rows)
    xf = pd.DataFrame(X, columns=names)
    return pd.concat([df.reset_index(drop=True), xf], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--games', default='')
    ap.add_argument('--games-file', default='')
    ap.add_argument('--replay-dir', default='public_replays/corpus/replays')
    ap.add_argument('--split-file', default='build/learn/splits/games_split_v2.parquet')
    ap.add_argument('--allow-split', default='train')
    ap.add_argument('--sides', default='all', help="'all' or team:<id>[,<id>] (needs the split file's team columns)")
    ap.add_argument('--process-pct', type=int, default=100)
    ap.add_argument('--no-oracle', action='store_true')
    a = ap.parse_args()
    import pandas as pd
    S = pd.read_parquet(a.split_file).set_index('game')
    seeds = {}
    try:
        G = pd.read_parquet('build/s1/corpus/games.parquet', columns=['game', 'seed'])
        seeds = dict(zip(G.game.astype(str), G.seed))
    except Exception:
        pass
    games = [g for g in a.games.split(',') if g] + ([l.strip() for l in open(a.games_file) if l.strip()] if a.games_file else [])
    allow = set(a.allow_split.split(','))
    teams = None if a.sides == 'all' else set(a.sides.split(':', 1)[1].split(','))
    frames, log = [], []
    t0 = time.time()
    for g in games:
        if g not in S.index or S.loc[g, 'split'] not in allow:
            log.append(dict(game=g, skipped=str(S.loc[g, 'split']) if g in S.index else 'unknown'))
            continue
        r = S.loc[g]
        sides = None
        if teams is not None:
            sides = {s for s, t in (('A', str(r.team_a)), ('B', str(r.team_b))) if t in teams}
            if not sides:
                continue
        data = (Path(a.replay_dir) / f'{g}.replay').read_bytes()
        meta = dict(series_key=r.series_key, split=r.split, map_hash=r.map_hash, map_era=r.map_era, ranked=bool(r.ranked),
                    team_a=str(r.team_a), team_b=str(r.team_b), dataset_version=DATASET_VERSION,
                    enc_version=E.ENC_VERSION, label_version=LB.LABEL_VERSION)
        rows, st = game_rows(g, data, seeds.get(g), sides, a.process_pct, not a.no_oracle, meta)
        log.append(dict(game=g, **st))
        if rows:
            frames.append(to_frame(rows))
        print(g, st, f'{time.time() - t0:.0f}s', flush=True)
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    df.to_parquet(a.out, index=False)
    Path(a.out + '.log.json').write_text(json.dumps(dict(args=vars(a), games=log, rows=len(df)), indent=1, default=str))
    print('rows', len(df), '->', a.out)


if __name__ == '__main__':
    main()
