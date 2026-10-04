"""Corpus-wide map identity check (D-043 / R0 item 9): is every post-m2 server map the maps/live/ template?
One replay per distinct (map name, map_hash) in the store; a server map matches when
  - every non-TILE line equals the template's, except DRAGON lines whose team digit may be flipped as a whole
    (the server's seat swap), and
  - TILE lines are either the template's or the redacted form 'TILE x y 0 0' on the same cells.
    python3 tools/learn/mapcheck.py [--era post-m2] -> docs/learning/splits/kageyama-mapcheck-v1.json (LEARN_DOCS_ROOT)"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path.cwd()
PY = ROOT / 'build' / 's1-pylib'
if sys.platform.startswith('linux') and PY.exists():
    sys.path.append(str(PY))
import rebuild


def templates():
    out = {}
    for f in sorted((ROOT / 'maps' / 'live').glob('*.map')):
        t = f.read_text()
        out[rebuild.Map(t).name] = (f.name, t)
    return out


def compare(server, tmpl):
    a, b = server.splitlines(), tmpl.splitlines()
    if len(a) != len(b):
        return dict(ok=False, why=f'lines {len(a)} vs {len(b)}')
    swap = None
    tiles = dict(same=0, redacted=0, other=0)
    other = 0
    for x, y in zip(a, b):
        if x == y:
            if x.startswith('TILE '):
                tiles['same'] += 1
            continue
        px, py = x.split(), y.split()
        if px[:1] == ['TILE'] and py[:1] == ['TILE'] and px[1:3] == py[1:3] and px[3:] == ['0', '0']:
            tiles['redacted'] += 1
            continue
        if px[:1] == ['DRAGON'] and py[:1] == ['DRAGON'] and px[2:] == py[2:] and {px[1], py[1]} == {'0', '1'}:
            if swap is False:
                return dict(ok=False, why='partial seat swap')
            swap = True
            continue
        if px[:1] == ['DRAGON']:
            swap = False if swap is None else swap
        other += 1
    if swap is None:
        swap = False
    return dict(ok=other == 0 and tiles['other'] == 0, seat_swap=bool(swap), tiles=tiles, other_lines=other)


def main():
    import pandas as pd
    era = sys.argv[sys.argv.index('--era') + 1] if '--era' in sys.argv else 'post-m2'
    g = pd.read_parquet(ROOT / 'build/s1/corpus/games.parquet', columns=['game', 'map', 'map_hash', 'map_era'])
    g = g[g.map_era == era]
    T = templates()
    rows = []
    for (mp, mh), x in g.groupby(['map', 'map_hash']):
        rec = dict(map=mp, map_hash=mh, games=int(len(x)))
        p = next((ROOT / f'public_replays/corpus/replays/{gid}.replay' for gid in x.game
                  if (ROOT / f'public_replays/corpus/replays/{gid}.replay').exists()), None)
        if p is None or mp not in T:
            rec.update(ok=None, why='no replay on disk' if p is None else 'no template')
        else:
            txt = rebuild.reader(p.read_bytes()).object(0, 0).text(0)
            rec.update(example=p.stem, template=T[mp][0], **compare(txt, T[mp][1]))
        rows.append(rec)
        print(rec, flush=True)
    games_ok = sum(r['games'] for r in rows if r.get('ok'))
    man = dict(era=era, distinct_maps=len(rows), games=int(g.shape[0]), games_on_matching_maps=games_ok,
               all_match=all(r.get('ok') for r in rows), rows=rows)
    docs = Path(os.environ.get('LEARN_DOCS_ROOT', ROOT)) / 'docs/learning/splits/kageyama-mapcheck-v1.json'
    docs.parent.mkdir(parents=True, exist_ok=True)
    docs.write_text(json.dumps(man, indent=1, default=str))
    print('distinct', len(rows), 'games', man['games'], 'on matching maps', games_ok, 'all_match', man['all_match'])


if __name__ == '__main__':
    main()
