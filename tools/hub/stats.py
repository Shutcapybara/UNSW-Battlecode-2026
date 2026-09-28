"""Pure statistics ported verbatim from the legacy live-validation `core.py` (protocol v1).

These functions are the retained, incident-tested logic (Part B §2.4): quota accounting over every
member's requests with reservations, exact-layout pairing, block sign-randomization and the v1
decision rule. They are not to be edited for v2; v2 lives in `decision_v2` below and is applied only
to experiments whose `protocol` column says so.
"""
import math
import re
from collections import defaultdict
from datetime import datetime

FAULT = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) (?!died:).*(?:exceeded CPU limit|exited|timed out|ran out of time|timeout|broken pipe|failed).*$', re.M | re.I)


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()


def quota_used(series, reservations, member_ids, dev_ids, now):
    """Count games, not series. Incoming challenges never use our allowance."""
    used = {'dev': 0, 'field': 0}
    seen = set()
    for item in series:
        m = item['match']
        if m.get('requestedBy') not in member_ids or timestamp(m['requestedAt']) <= now - 3605:
            continue
        key = m.get('seriesId') or str(m['id'])
        if key in seen:
            continue
        seen.add(key)
        pool = 'dev' if m['teamAId'] in dev_ids or m['teamBId'] in dev_ids else 'field'
        used[pool] += len(item['games'])
    known_ids = {g['id'] for s in series for g in s['games']}
    for r in reservations:
        if r['at'] <= now - 3605 or r['status'] in ('rejected', 'observed'):
            continue
        used[r['pool']] += sum(i not in known_ids for i in r['ids']) if r.get('ids') else r['count']
    return used


def paired_blocks(blocks, results):
    """No row-level pseudoreplication; one value per complete requested block."""
    output = []
    for b in blocks:
        if b['phase'] not in ('screen', 'confirm') or len(b.get('requests', [])) < 2:
            continue
        ids = list(dict.fromkeys(i for group in b['requests'] for i in group))
        rows = [results[str(i)] for i in ids if results.get(str(i), {}).get('verified')]
        control = [r for r in rows if r['submission'] == b['control']]
        candidate = [r for r in rows if r['submission'] == b['candidate']]

        def key(r):
            return r['map_id'], r['side'], r['opponent_submission'], r['map_hash']
        pairs = []
        for map_id in b['map_ids']:
            match = next(((x, y) for x in control for y in candidate if x['map_id'] == map_id and key(x) == key(y)), None)
            if match:
                pairs.append(match)
        complete = len(pairs) == len(b['map_ids']) and all(results.get(str(i), {}).get('verified') for i in ids)
        output.append(dict(block=b['id'], phase=b['phase'], complete=complete,
                           delta=sum(y['score'] - x['score'] for x, y in pairs) / len(pairs) if pairs else None,
                           pairs=[dict(map_id=y['map_id'], side=y['side'], delta=y['score'] - x['score'],
                                       length_delta=y['longest_margin'] - x['longest_margin']) for x, y in pairs],
                           faults=sum(y['faults'] + y.get('caught_errors', 0) for y in candidate), opponent=b['opponent'],
                           missing_maps=[m for m in b['map_ids'] if m not in {x['map_id'] for x, y in pairs}]))
    return output


def sign_flip_p(values):
    """One-sided block sign randomization, fixed confirmation sample only."""
    values = [x for x in values if abs(x) > 1e-12]
    if not values or sum(values) <= 0:
        return 1.0
    target = sum(values) - 1e-12
    if len(values) > 20:
        raise ValueError('Confirmation must remain fixed and bounded')
    sums = [0.0]
    for x in values:
        sums = [s + x for s in sums] + [s - x for s in sums]
    return sum(s >= target for s in sums) / len(sums)


def decision_v1(blocks, results, alpha, confirm_blocks=12):
    paired = paired_blocks(blocks, results)
    screen = [x for x in paired if x['phase'] == 'screen' and x['complete']]
    conf = [x for x in paired if x['phase'] == 'confirm' and x['complete']]
    if len(screen) < 3:
        return {'verdict': 'screening', 'complete_screen_blocks': len(screen), 'pairs': paired}
    if sum(x['faults'] for x in screen) or sum(x['delta'] for x in screen) <= 0:
        return {'verdict': 'reject_screen', 'pairs': paired}
    if len(conf) < confirm_blocks:
        return {'verdict': 'confirming', 'complete_confirmation_blocks': len(conf), 'pairs': paired}
    conf = conf[:confirm_blocks]
    by_map = defaultdict(list)
    for b in conf:
        for p in b['pairs']:
            by_map[p['map_id']].append(p['delta'])
    delta = sum(b['delta'] for b in conf) / len(conf)
    p = sign_flip_p([b['delta'] for b in conf])
    sides = {p['side'] for b in conf for p in b['pairs']}
    passes = delta >= .03 and p <= alpha and len({b['opponent'] for b in conf}) >= 12 and all(sum(x) / len(x) >= -.25 for x in by_map.values()) and not sum(x['faults'] for x in conf)
    return dict(verdict='promote' if passes else 'reject_confirmation', delta=delta, p=p, alpha=alpha, sides=sorted(sides),
                deployment='monitored_probation', pairs=paired, map_delta={k: sum(v) / len(v) for k, v in by_map.items()})


def decision_v2(blocks, results, alpha=0.025, confirm_blocks=12, screen_blocks=3, paired=None):
    """Protocol v2 (Part B §7.4-§7.5): futility stops in the screen and futility-only interims at 6 and 9 blocks.

    Screen: after block 1 stop if net paired wins <= -4; after block 2 stop if cumulative net <= -4; pass after 3
    blocks iff cumulative net > 0 with zero candidate faults. Confirmation: reject at 6 complete blocks if the
    mean paired delta <= 0, at 9 if <= +0.01; efficacy once at 12: mean delta >= +0.03, one-sided sign-randomization
    p <= alpha, no map mean below -0.25, 12 distinct opponents, zero faults.
    """
    paired = paired_blocks(blocks, results) if paired is None else paired
    screen = [x for x in paired if x['phase'] == 'screen' and x['complete']]
    conf = [x for x in paired if x['phase'] == 'confirm' and x['complete']]
    net = lambda xs: sum(p['delta'] for b in xs for p in b['pairs'])
    if sum(x['faults'] for x in screen):
        return {'verdict': 'reject_screen', 'reason': 'candidate fault in screen', 'pairs': paired}
    if len(screen) >= 1 and len(screen) < screen_blocks and net(screen[:len(screen)]) <= -4:
        return {'verdict': 'reject_screen', 'reason': f'futility after {len(screen)} block(s): net {net(screen)}', 'pairs': paired}
    if len(screen) < screen_blocks:
        return {'verdict': 'screening', 'complete_screen_blocks': len(screen), 'net': net(screen), 'pairs': paired}
    screen = screen[:screen_blocks]
    if net(screen) <= 0:
        return {'verdict': 'reject_screen', 'reason': f'net {net(screen)} <= 0 after {screen_blocks} blocks', 'pairs': paired}
    means = [b['delta'] for b in conf]
    if len(conf) >= 6 and len(conf) < confirm_blocks:
        interim = sum(means[:6]) / 6
        if interim <= 0:
            return {'verdict': 'reject_confirmation', 'reason': f'futility at 6 blocks: mean {interim:.3f}', 'pairs': paired}
    if len(conf) >= 9 and len(conf) < confirm_blocks:
        interim = sum(means[:9]) / 9
        if interim <= 0.01:
            return {'verdict': 'reject_confirmation', 'reason': f'futility at 9 blocks: mean {interim:.3f}', 'pairs': paired}
    if len(conf) < confirm_blocks:
        return {'verdict': 'confirming', 'complete_confirmation_blocks': len(conf), 'pairs': paired}
    conf = conf[:confirm_blocks]
    by_map = defaultdict(list)
    for b in conf:
        for p in b['pairs']:
            by_map[p['map_id']].append(p['delta'])
    delta = sum(b['delta'] for b in conf) / len(conf)
    p = sign_flip_p([b['delta'] for b in conf])
    passes = (delta >= .03 and p <= alpha and len({b['opponent'] for b in conf}) >= confirm_blocks
              and all(sum(x) / len(x) >= -.25 for x in by_map.values()) and not sum(x['faults'] for x in conf))
    return dict(verdict='promote' if passes else 'reject_confirmation', delta=delta, p=p, alpha=alpha,
                deployment='monitored_probation', pairs=paired, map_delta={k: sum(v) / len(v) for k, v in by_map.items()})


def critic(rows):
    """Transparent Beta(1,1) empirical critic; descriptive only."""
    cells = defaultdict(list)
    for r in rows:
        if r.get('verified'):
            cells[(r['submission'], r['pool'], r['map_id'], r['opponent'], r['opponent_submission'], r['side'])].append(r)
    out = []
    for key, rs in sorted(cells.items(), key=lambda kv: [str(x) for x in kv[0]]):
        wins = sum(r['score'] for r in rs)
        n = len(rs)
        a = 1 + wins
        b = 1 + n - wins
        out.append(dict(zip(('submission', 'pool', 'map', 'opponent', 'opponent_submission', 'side'), key),
                        n=n, posterior_mean=a / (a + b), posterior_sd=math.sqrt(a * b / ((a + b) ** 2 * (a + b + 1))),
                        faults=sum(r['faults'] for r in rs), series=len({r.get('series') for r in rs})))
    return out


def in_blackout(utc_minute_of_day, before=8, after=12):
    """Ranked-exposure guard (Part B §7.6): true inside [-before, +after] minutes around each even UTC hour."""
    for hour in range(0, 24, 2):
        centre = hour * 60
        if centre - before <= utc_minute_of_day <= centre + after:
            return True
    return utc_minute_of_day >= 24 * 60 - before  # the 00:00 boundary seen from 23:5x
