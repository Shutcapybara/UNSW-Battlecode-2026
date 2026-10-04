"""D-052 §B rollback rule, as written: operating characteristics (simulation) and placebo looks on real data.

Rule: one look at the first series boundary at or after 40 ranked games of the promoted submission. Roll back when
mean(new residuals) - mean(replaced submission's last 120 ranked residuals, extended back to a series boundary) < -0.08
and the 95th percentile of that difference < 0; bootstrap = whole series, windows resampled independently, 1,000
replicates, seed 7 (linear interpolation). Residual = score - E with OUR rating fixed at the activation time and the
opponent's rating at game time; games before the first snapshot are excluded.

Part 1 (simulation): series of the live submission (anchor = rating at its first ranked game) are centred and drawn
i.i.d. with replacement; the reference window draws whole series until >= 120 games, the new window whole series
until >= 40 games and is shifted by delta. The rule above is applied verbatim (inner bootstrap 1,000).
Part 2 (placebo on real sequential data): at every series boundary of the live submission's ranked history, pretend a
new submission was activated there (anchor = our rating at that moment): reference = the preceding >= 120 games,
new = the following >= 40. Same submission on both sides, so every firing is a false rollback; looks overlap.
Part 3: the one real transition in the window (previous submission -> live), on the rule as written.
Run from the repo root: python3 build/daichi/tree/tools/daichi/rollback_d052.py [sims]
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_monitor as lm  # noqa: E402

THR, INNER = -0.08, 1000


def decide(new, ref, rng):
    """new/ref: lists of per-series residual lists. Returns (diff, hi95, rollback)."""
    ns, nc = np.array([sum(s) for s in new]), np.array([len(s) for s in new])
    rs, rc = np.array([sum(s) for s in ref]), np.array([len(s) for s in ref])
    diff = ns.sum() / nc.sum() - rs.sum() / rc.sum()
    i = rng.integers(0, len(new), size=(INNER, len(new)))
    j = rng.integers(0, len(ref), size=(INNER, len(ref)))
    d = ns[i].sum(1) / nc[i].sum(1) - rs[j].sum(1) / rc[j].sum(1)
    hi = float(np.percentile(d, 95))
    return diff, hi, bool(diff < THR and hi < 0)


def draw(rng, pool, n, shift):
    out, k = [], 0
    while k < n:
        s = pool[rng.integers(len(pool))]
        out.append([x + shift for x in s])
        k += len(s)
    return out


def resid(games, ladders, keys, anchor_elo):
    for g in games:
        ro = lm.rating_at(ladders, keys, g['at'], g['opp'])
        g['r'] = None if ro is None or anchor_elo is None else g['score'] - 1 / (1 + 10 ** ((ro - anchor_elo) / 400))
    return [g for g in games if g['r'] is not None]


def series_list(games):
    by, order = {}, []
    for g in games:
        if g['series'] not in by:
            order.append(g['series'])
        by.setdefault(g['series'], []).append(g['r'])
    return [by[s] for s in order]


def main():
    sims = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    repo = Path('.')
    since = datetime.now(timezone.utc) - timedelta(days=14)
    active = str(json.loads((repo / 'hub-state/status.json').read_text())['active'])
    ladders = lm.load_ladders(repo / 'public_replays/corpus/ladder', since - timedelta(hours=2))
    keys = [t for t, _ in ladders]
    allg = [g for g in lm.own_games(repo / 'public_replays/corpus/index.jsonl', since) if g['ranked']]
    live = [g for g in allg if g['bot'] == active]
    t0 = live[0]['at']
    anchor = lm.rating_at(ladders, keys, t0, lm.TEAM)
    live = resid([dict(g) for g in live], ladders, keys, anchor)
    pool = series_list(live)
    mu = sum(map(sum, pool)) / sum(map(len, pool))
    pool = [[x - mu for x in s] for s in pool]
    print(f'# D-052 §B rollback rule — operating characteristics\n')
    print(f'Source: submission {active}, ranked, {len(live)} games / {len(pool)} series with an expectation, anchor Elo {anchor} '
          f'(our rating at its first ranked game, {t0:%Y-%m-%d %H:%MZ}); mean residual {mu:+.3f}, centred to 0. '
          f'Sims per cell {sims}; inner bootstrap {INNER}; rng seed 7.\n')
    rng = np.random.default_rng(7)
    print('## 1. Simulation (i.i.d. whole series)\n')
    print('| true new − old | P(rollback) | mean games in new window | mean games in reference |')
    print('|---|---|---|---|')
    for d in (0.0, -0.05, -0.08, -0.10, -0.15, -0.20):
        hits, nn, nr = 0, 0, 0
        for _ in range(sims):
            ref, new = draw(rng, pool, 120, 0.0), draw(rng, pool, 40, d)
            hits += decide(new, ref, rng)[2]
            nn += sum(map(len, new)); nr += sum(map(len, ref))
        p = hits / sims
        se = (p * (1 - p) / sims) ** .5
        print(f'| {d:+.2f} | {p:.3f} (±{1.96 * se:.3f}) | {nn / sims:.1f} | {nr / sims:.1f} |', flush=True)
    # Part 2: placebo looks on the real sequence
    print('\n## 2. Placebo looks on real sequential data (same submission both sides)\n')
    raw = [dict(g) for g in [g for g in allg if g['bot'] == active]]
    sids = []
    for g in raw:
        if not sids or sids[-1] != g['series']:
            sids.append(g['series'])
    looks = fired = 0
    diffs = []
    for b in range(1, len(sids)):
        before = [g for g in raw if g['series'] in set(sids[:b])]
        after_s = sids[b:]
        if len(before) < 120:
            continue
        # reference: last >= 120 games extended back to a series boundary
        ref_ids, k = [], 0
        for s in reversed(sids[:b]):
            ref_ids.append(s); k += sum(1 for g in raw if g['series'] == s)
            if k >= 120:
                break
        new_ids, k = [], 0
        for s in after_s:
            new_ids.append(s); k += sum(1 for g in raw if g['series'] == s)
            if k >= 40:
                break
        if k < 40:
            break
        when = min(g['at'] for g in raw if g['series'] == after_s[0])
        a = lm.rating_at(ladders, keys, when, lm.TEAM)
        gs = resid([dict(g) for g in raw if g['series'] in set(ref_ids) | set(new_ids)], ladders, keys, a)
        ref = series_list([g for g in gs if g['series'] in set(ref_ids)])
        new = series_list([g for g in gs if g['series'] in set(new_ids)])
        diff, hi, rb = decide(new, ref, np.random.default_rng(7))
        looks += 1; fired += rb; diffs.append(diff)
    if looks:
        ds = sorted(diffs)
        print(f'Looks: {looks} (one per series boundary with >= 120 games before and >= 40 after; heavily overlapping, '
              f'so not independent). Rule fired: **{fired} / {looks} = {fired / looks:.3f}**. Difference quantiles '
              f'5/50/95 %: {ds[int(.05 * looks)]:+.3f} / {ds[looks // 2]:+.3f} / {ds[int(.95 * looks) - 1]:+.3f}.\n')
    # Part 3: real transition
    print('## 3. The real transition in the window\n')
    subs = []
    for g in allg:
        if g['bot'] and (not subs or subs[-1] != g['bot']):
            subs.append(g['bot'])
    prev = None
    for s in subs:
        if s == active:
            break
        prev = s
    prev_g = [dict(g) for g in allg if g['bot'] == prev and g['at'] < t0]
    gs_new = [dict(g) for g in allg if g['bot'] == active]
    nids, k = [], 0
    for g in gs_new:
        if not nids or nids[-1] != g['series']:
            if k >= 40:
                break
            nids.append(g['series'])
        k += 1
    pids, k = [], 0
    for g in reversed(prev_g):
        if not pids or pids[-1] != g['series']:
            if k >= 120:
                break
            pids.append(g['series'])
        k += 1
    gs = resid([g for g in prev_g if g['series'] in set(pids)] + [g for g in gs_new if g['series'] in set(nids)], ladders, keys, anchor)
    ref = series_list([g for g in gs if g['series'] in set(pids)])
    new = series_list([g for g in gs if g['series'] in set(nids)])
    if ref and new:
        diff, hi, rb = decide(new, ref, np.random.default_rng(7))
        print(f'{prev} (last {sum(map(len, ref))} ranked games / {len(ref)} series with an expectation) -> {active} '
              f'(first {sum(map(len, new))} / {len(new)}): difference {diff:+.3f}, 95th pct {hi:+.3f} -> '
              f'**{"ROLL BACK" if rb else "keep"}** (anchor {anchor}).')
    else:
        print(f'previous submission {prev}: no reference window with an expectation in the 14-day corpus.')


if __name__ == '__main__':
    main()
