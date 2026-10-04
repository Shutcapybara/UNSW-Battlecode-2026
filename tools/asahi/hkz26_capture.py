#!/usr/bin/env python3
"""P-4 / H-KZ26 exposure capture (from tools/asahi/kz12_capture.py). Originally: H-KZ12 exposure capture for an Asahi panel (copied from tools/rome/capture_kz12_logs.py on r/rome, 4 Oct; Rome's
lane is the source, this copy only changes inputs/outputs and counts every dragon, not only the queen).

Replays do not store bot stdout, so each finished fixture is re-run in-process (tools/cx/arena.run_game, same seed,
same installed engine) with the arm's side recorded; the replayed winner and round count must match the panel index
(official_match) or the row is flagged. From the `LOG KZ12 r= k= veto= fallback= cap=` lines it reports, per map and
overall, for the queen (lowest-id initial dragon) and for other dragons:
  checked decisions, decisions with >= 1 vetoed direction (veto firings), firings per 1k checked decisions,
  fallback (every direction vetoed) count, games with any firing.

    python tools/asahi/kz12_capture.py BOT --panel pool [--jobs 14] [--limit N]
"""
from __future__ import annotations

import argparse, json, os, re, sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/asahi'))
os.chdir(ROOT)
import panel as P  # noqa: E402

LOG_RE = re.compile(r'LOG HKZ26 r=(-?\d+) m=(-?\d+) heads=(\d+) lmax=(\d+) legal=(\d+) veto=(\d+) sveto=(\d+) fallback=(\d+) changed=(\d+)')


def capture(row: dict, bot: str) -> dict:
    from tools.cx.arena import run_game
    side = 'A' if row['botA'] == bot else 'B'
    g = run_game(f"maps/{row['map']}.map", f"bots/{row['botA']}", f"bots/{row['botB']}", seed=int(row['seed']), record=side)
    tr = g.get('transcripts') or {}
    queen = min((int(k) for k in tr), default=None)
    # checked, fired (>=1 vetoed legal candidate), fallback, changed, vetoed candidates, sprint-vetoed, heads-visible
    agg = {'queen': [0, 0, 0, 0, 0, 0, 0], 'other': [0, 0, 0, 0, 0, 0, 0]}
    for k, t in tr.items():
        who = 'queen' if int(k) == queen else 'other'
        for turn in t['turns']:
            for m in LOG_RE.finditer(turn.get('output', '')):
                _r, _m, heads, _lmax, legal, veto, sveto, fb, ch = map(int, m.groups())
                a = agg[who]
                a[0] += 1; a[1] += veto > 0; a[2] += fb; a[3] += ch; a[4] += veto; a[5] += sveto; a[6] += heads > 0
    return dict(game=row['game'], map=row['map'], side=side, winner=g['winner'], rounds=int(g['rounds']),
                official_match=(g['winner'] == row.get('winner') and int(g['rounds']) == row.get('rounds')),
                errors=g.get('errors', []), queen_id=queen, agg=agg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--panel', default='pool')
    ap.add_argument('--jobs', type=int, default=14); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    jobs = min(a.jobs, int(os.environ.get('ASAHI_MAX_WORKERS', '14')))
    root = P.run_root(a.bot, a.panel)
    rows = [json.loads(s) for s in open(root / 'index.jsonl') if s.strip()]
    rows = [r for r in rows if r.get('rc') == 0]
    out = root / 'hkz26.jsonl'
    done = {json.loads(s)['game'] for s in open(out)} if out.exists() else set()
    todo = [r for r in rows if r['game'] not in done][: a.limit or None]
    print(f'{len(rows)} fixtures, {len(todo)} to capture', flush=True)
    with open(out, 'a') as f, ProcessPoolExecutor(jobs) as ex:
        futs = [ex.submit(capture, r, a.bot) for r in todo]
        for i, fu in enumerate(as_completed(futs), 1):
            try:
                f.write(json.dumps(fu.result()) + '\n'); f.flush()
            except Exception as e:
                print('ERR', type(e).__name__, str(e)[:200], flush=True)
            if i % 25 == 0:
                print(f'{i}/{len(todo)}', flush=True)
    res = [json.loads(s) for s in open(out)]
    by = defaultdict(lambda: {'queen': [0] * 7, 'other': [0] * 7, 'games': 0, 'games_fired': 0})
    for r in res:
        for key in (r['map'], 'ALL'):
            b = by[key]
            b['games'] += 1
            b['games_fired'] += (r['agg']['queen'][1] + r['agg']['other'][1]) > 0
            for who in ('queen', 'other'):
                b[who] = [x + y for x, y in zip(b[who], r['agg'][who])]
    summ = dict(bot=a.bot, panel=a.panel, fixtures=len(res), mismatches=sum(not r['official_match'] for r in res),
                engine_errors=sum(bool(r['errors']) for r in res),
                by_map={k: dict(v, queen_fire_per1k=1000 * v['queen'][1] / max(1, v['queen'][0]),
                                other_fire_per1k=1000 * v['other'][1] / max(1, v['other'][0])) for k, v in sorted(by.items())})
    (root / 'hkz26_summary.json').write_text(json.dumps(summ, indent=1))
    a_ = summ['by_map'].get('ALL', {})
    print(json.dumps(dict(fixtures=summ['fixtures'], mismatches=summ['mismatches'], engine_errors=summ['engine_errors'],
                          ALL=a_), indent=1))
    return 1 if summ['mismatches'] else 0


if __name__ == '__main__':
    sys.exit(main())
