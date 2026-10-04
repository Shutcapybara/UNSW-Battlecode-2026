"""Operating characteristics of the D-046 §8 rollback rule (absolute) vs the D-048 §8 amendment (difference).

Resamples whole ranked series of the live submission (score − Elo expectation per game, as in live_monitor.py) to
build 40-game windows: the 'old' window is the replaced submission's last 40, the 'new' window a candidate's first 40
with its true residual shifted by delta. Each simulated decision applies the rule exactly as written, including the
series-bootstrap 95th percentile (200 inner resamples). Output: P(rollback) per delta and per incumbent level.
Run from the repo root: python3 build/daichi/tree/tools/daichi/rollback_power.py
"""
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_monitor as lm  # noqa: E402

THR = -0.08


def window(rng, series, shift, n=40):
    out = []
    while True:
        s = rng.choice(series)
        out.append([x + shift for x in s])
        if sum(len(x) for x in out) >= n:
            break
    # keep series structure, truncate the last series to reach exactly 40 games
    k = sum(len(x) for x in out) - n
    if k:
        out[-1] = out[-1][:len(out[-1]) - k]
    return [x for x in out if x]


def mean(ws):
    n = sum(len(x) for x in ws)
    return sum(sum(x) for x in ws) / n


def hi95(rng, a, b=None, inner=200):
    vals = []
    for _ in range(inner):
        pa = [rng.choice(a) for _ in a]
        v = mean(pa)
        if b is not None:
            v -= mean([rng.choice(b) for _ in b])
        vals.append(v)
    vals.sort()
    return vals[int(.95 * inner) - 1]


def main():
    repo = Path('.')
    since = datetime.now(timezone.utc) - timedelta(days=14)
    status = json.loads((repo / 'hub-state/status.json').read_text())
    active = str(status['active'])
    ladders = lm.load_ladders(repo / 'public_replays/corpus/ladder', since - timedelta(hours=2))
    keys = [t for t, _ in ladders]
    games = lm.own_games(repo / 'public_replays/corpus/index.jsonl', since)
    by = {}
    for g in games:
        if not g['ranked'] or g['bot'] != active:
            continue
        ru, ro = lm.rating_at(ladders, keys, g['at'], lm.TEAM), lm.rating_at(ladders, keys, g['at'], g['opp'])
        if ru is None or ro is None:
            continue
        by.setdefault(g['series'], []).append(g['score'] - 1 / (1 + 10 ** ((ro - ru) / 400)))
    series = list(by.values())
    mu = mean(series)
    centred = [[x - mu for x in s] for s in series]       # true residual 0, real series-level dispersion
    n = sum(len(s) for s in series)
    print(f'source: submission {active}, {n} ranked games / {len(series)} series, mean {mu:+.3f}; sims per cell {SIMS}')
    rng = random.Random(7)
    print('| incumbent true level | candidate − incumbent (true) | absolute §8 | difference, ref last 40 (D-048 §8) | difference, ref last 120 |')
    print('|---|---|---|---|---|')
    for base in (0.0, mu, -0.07):
        for d in (0.0, -0.05, -0.08, -0.10, -0.15, -0.20):
            ra = rd = r3 = 0
            for _ in range(SIMS):
                old = window(rng, centred, base)
                new = window(rng, centred, base + d)
                if mean(new) < THR and hi95(rng, new) < 0:
                    ra += 1
                if mean(new) - mean(old) < THR and hi95(rng, new, old) < 0:
                    rd += 1
                old3 = window(rng, centred, base, 120)
                if mean(new) - mean(old3) < THR and hi95(rng, new, old3) < 0:
                    r3 += 1
            print(f'| {base:+.3f} | {d:+.2f} | {ra / SIMS:.2f} | {rd / SIMS:.2f} | {r3 / SIMS:.2f} |', flush=True)


SIMS = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
if __name__ == '__main__':
    main()
