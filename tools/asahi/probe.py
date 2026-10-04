#!/usr/bin/env python3
"""Deploy probe (D-046 §4 deploy limits, D-055 §A item 4): sandbox CPU points per turn including each dragon's first
(boot / turn-0) turn, on the heaviest live maps in both seats, plus the submission zip size exactly as `unswbc submit`
builds it (unswbc.submit._zip over the project's include list; symlinks are followed, so the real model header counts).

    python tools/asahi/probe.py BOT [--opp yuna-v05-core] [--maps live/schooltime,live/portals,live/australia,live/trauma]
Writes build/asahi/probes/<bot>-<fp8>.json and prints one summary line.
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tools/cx'))
os.chdir(ROOT)
from tools.analysis.features import run_panel as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--opp', default='yuna-v05-core')
    ap.add_argument('--maps', default='live/schooltime,live/portals,live/australia,live/trauma,live/unsw')
    a = ap.parse_args()
    from arena import run_game
    from unswbc.project import Project
    from unswbc.submit import _zip
    fp = R.runtime_fingerprint(ROOT / 'bots' / a.bot)
    blob = _zip(Project.from_dir(str(ROOT / 'bots' / a.bot)))
    rows = []
    for m in a.maps.split(','):
        for A, B, seat in ((a.bot, a.opp, 'A'), (a.opp, a.bot, 'B')):
            r = run_game(f'maps/{m}.map', f'bots/{A}', f'bots/{B}', seed=1, sandbox=True)
            s = r['stats'][seat]
            rows.append(dict(map=m, seat=seat, p50=s.get('points', {}).get('p50'), p99=s.get('points', {}).get('p99'),
                             max=s.get('points', {}).get('max'), boot_max=s.get('boot', {}).get('max'),
                             errors=[e for e in r.get('errors', []) if e[2] == seat]))
            print(rows[-1], flush=True)
    out = dict(bot=a.bot, fingerprint=fp, zip_bytes=len(blob), zip_mib=len(blob) / 2 ** 20,
               max_points=max(x['max'] or 0 for x in rows), max_boot=max(x['boot_max'] or 0 for x in rows),
               errors=sum(len(x['errors']) for x in rows), rows=rows)
    p = ROOT / 'build/asahi/probes' / f'{a.bot}-{fp[:8]}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1, default=str))
    ok = out['max_points'] <= 30e6 and out['max_boot'] <= 30e6 and out['zip_bytes'] <= 4 * 2 ** 20 and not out['errors']
    print(f"PROBE {a.bot} fp {fp[:8]} zip {out['zip_mib']:.2f} MiB max {out['max_points'] / 1e6:.2f}M boot {out['max_boot'] / 1e6:.2f}M "
          f"errors {out['errors']} -> {'OK' if ok else 'OVER/ERROR'}")


if __name__ == '__main__':
    main()
