#!/usr/bin/env python3
"""Regenerate the gen-panel transpose twins of the four swapped ladder maps from maps/live/ (D-043 item 4).

The existing maps/var/*_tr.map files are exactly tools/ouroboros/mapgen.py's transpose (T) of the pre-swap
maps/*.map (checked semantically below: size, tiles, kelp edges, portals, dragons). Four of them (autarky, default,
dilemma, trophy) model old geometry; their sources changed on 2 Oct. This writes maps/m2tr/<map>_tr.map = T of
maps/live/<map>.map and prints the check table. maps/var is left untouched.

    python3 tools/asahi/twins.py [--check-only]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/ouroboros'))
import mapgen  # noqa: E402

SWAPPED = ['autarky', 'default', 'dilemma', 'trophy']


def sem(text):
    m = mapgen.parse(text)
    return (m['W'], m['H'], m['tiles'], set(m['kelp_h']), set(m['kelp_v']), m['portal_h'], m['portal_v'],
            sorted((d[0], tuple(map(tuple, d[1]))) for d in m['dragons']))


def main():
    ok = True
    for p in sorted((ROOT / 'maps/var').glob('*_tr.map')):
        s = p.stem[:-3]
        old, live = ROOT / f'maps/{s}.map', ROOT / f'maps/live/{s}.map'
        gen_ok = sem(mapgen.compose(old.read_text(), ('T',))) == sem(p.read_text()) if old.exists() else None
        cur = sem(mapgen.compose(live.read_text(), ('T',))) == sem(p.read_text()) if live.exists() else None
        print(f'{s:16s} T(pre-swap)==var:{gen_ok}  T(live)==var:{cur}')
        if s in SWAPPED and cur:
            print(f'  ! {s} expected stale but matches'); ok = False
        if s not in SWAPPED and cur is False:
            print(f'  ! {s} is stale but not in SWAPPED'); ok = False
    if '--check-only' in sys.argv:
        return 0 if ok else 1
    out = ROOT / 'maps/m2tr'
    out.mkdir(exist_ok=True)
    for s in SWAPPED:
        text = mapgen.compose((ROOT / f'maps/live/{s}.map').read_text(), ('T',))
        name = [l for l in (ROOT / f'maps/live/{s}.map').read_text().splitlines() if l.startswith('MAP_NAME')][0][9:]
        text = '\n'.join(f'MAP_NAME {name} tr m2' if l.startswith('MAP_NAME') else l for l in text.splitlines()) + '\n'
        (out / f'{s}_tr.map').write_text(text)
        assert sem(text) == sem(mapgen.compose((ROOT / f'maps/live/{s}.map').read_text(), ('T',)))
        print('wrote', out / f'{s}_tr.map')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
