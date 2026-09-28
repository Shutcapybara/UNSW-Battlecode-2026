"""A3 — starting-layout assignment (handoff §3.3).

Each live game stores map_hash (the starting layout; two per map). Question: is the layout a
function of anything we control or observe — request order, seed parity, series position, side,
arm — or random? Method: per map_id contingency of layout against covariates; seed→layout
mapping check (does a repeated seed give a repeated layout?); arm-layout matching inside
screen blocks. No B-side pooling (sides stated where used).
"""
import binascii
import json
from collections import Counter, defaultdict

from live_load import STATE, load

GAMES = None  # set in main


def layout_bit(map_id, h, first_hash):
    """1 if hash equals the map's first-seen hash else 0 — arbitrary but consistent label."""
    return 1 if h == first_hash[map_id] else 0


def main():
    d = json.load(open(STATE))
    all_games = []
    for gid, g in d['results'].items():
        row = dict(g)
        row['game_id'] = int(gid)
        all_games.append(row)
    hashes = defaultdict(set)
    for g in all_games:
        if g.get('map_hash'):
            hashes[g['map_id']].add(g['map_hash'])
    print("distinct layouts per map:", {m: len(v) for m, v in sorted(hashes.items())})
    first_hash = {m: sorted(v)[0] for m, v in hashes.items()}

    # seed reuse
    seed_n = Counter(g.get('seed') for g in all_games)
    reused = [s for s, n in seed_n.items() if n > 1]
    print(f"\nseeds: {len(seed_n)} distinct over {len(all_games)} games; reused: {len(reused)}")
    agree = disagree = 0
    for s in reused:
        rows = [g for g in all_games if g['seed'] == s]
        hs = {(g['map_id'], g['map_hash']) for g in rows}
        maps_ = {m for m, _ in hs}
        per_map_ok = all(len({h for m, h in hs if m == m0}) == 1 for m0 in maps_)
        agree += per_map_ok
        disagree += not per_map_ok
    if reused:
        print(f"  repeated seeds: same map -> same layout in {agree}, different in {disagree}")

    # layout vs covariates, per map: A-side games only
    aside = [g for g in all_games if g.get('side') == 'A']
    print(f"\nA-side games: {len(aside)}; contingency of layout bit vs covariates (per covariate value: n with layout0/layout1):")
    for cov in ('side',):
        tab = defaultdict(Counter)
        for g in all_games:
            if g.get('map_hash'):
                tab[g.get(cov)][layout_bit(g['map_id'], g['map_hash'], first_hash)] += 1
        print(f"  {cov}: " + "; ".join(f"{k}={dict(v)}" for k, v in sorted(tab.items(), key=lambda kv: str(kv[0]))))
    m17 = {g.get('map_name') for g in all_games if g['map_id'] == 17}
    print("  map_id 17 name:", m17, "| hashes by requested date:")
    when = defaultdict(set)
    for g in all_games:
        if g['map_id'] == 17 and g.get('map_hash'):
            when[g.get('requested', '')[:10]].add(g['map_hash'][:8])
    for day, hs in sorted(when.items()):
        print(f"    {day}: {sorted(hs)}")

    # arm-layout matching inside blocks (which games belong to a block via requests)
    block_of = {}
    for b in d.get('blocks', []):
        for req in b.get('requests') or []:
            for gid in req if isinstance(req, list) else []:
                block_of[int(gid)] = b
    games = load(verified_only=True)
    pairs = defaultdict(lambda: defaultdict(list))  # (block, map_id) -> arm -> layout bit
    for g in games:
        b = block_of.get(g['game_id'])
        if not b or g.get('side') != 'A':
            continue
        arm = 'cand' if g['submission'] == b['candidate'] else ('ctrl' if g['submission'] == b['control'] else None)
        if arm:
            pairs[(b['id'], g['map_id'])][arm].append(layout_bit(g['map_id'], g['map_hash'], first_hash))
    matched = mismatched = half = 0
    per_block = defaultdict(Counter)
    for (bid, m), arms in pairs.items():
        if 'cand' in arms and 'ctrl' in arms and arms['cand'] and arms['ctrl']:
            # compare the FIRST requested candidate game against first control game on that map
            same = arms['cand'][0] == arms['ctrl'][0]
            per_block[bid]['match' if same else 'mismatch'] += 1
            matched += same
            mismatched += not same
    print(f"\nwithin-block same-map candidate vs control layout: matched {matched}, mismatched {mismatched}")
    for bid, c in sorted(per_block.items()):
        print(f"  block {bid[:8]}: {dict(c)}")

    # request-order / series-position / time signals on A-side games per map: layout vs game parity in its own request batch
    req_order = {}
    for rq in d.get('requests', []):
        for i, gid in enumerate(rq.get('ids') or []):
            req_order[int(gid)] = (i, rq.get('block'), rq.get('pool'), rq.get('opponent'), rq.get('submission'))
    tab = defaultdict(Counter)
    for g in aside:
        if g['game_id'] not in req_order or not g.get('map_hash'):
            continue
        i, _, _, _, _ = req_order[g['game_id']]
        tab['pos_even' if i % 2 == 0 else 'pos_odd'][layout_bit(g['map_id'], g['map_hash'], first_hash)] += 1
    for k, v in tab.items():
        print(f"  request position {k}: layout0/1 = {dict(v)}")

    # same-map back-to-back games in one batch: layout alternation?
    alt = same = n = 0
    by_batch = defaultdict(list)
    for gid, (i, b, pool, opp, sub) in req_order.items():
        g = d['results'].get(str(gid))
        if g and g.get('side') == 'A' and g.get('map_hash'):
            by_batch[(b, i // 10)].append((i, g['map_id'], layout_bit(g['map_id'], g['map_hash'], first_hash)))
    for _, rows in by_batch.items():
        rows.sort()
        for (i1, m1, l1), (i2, m2, l2) in zip(rows, rows[1:]):
            if m1 == m2:
                n += 1
                alt += (l1 != l2)
                same += (l1 == l2)
    print(f"\nadjacent same-map games in one batch: n={n}, alternating {alt}, repeating {same}")

    # seed parity / hash-of-seed vs layout (exploratory, Bonferroni-eye)
    for name, fn in (('seed_last_hex_even', lambda s: int(s[-1], 16) % 2 == 0),):
        t = Counter()
        for g in aside:
            if g.get('seed') and g.get('map_hash'):
                t[(fn(g['seed']), layout_bit(g['map_id'], g['map_hash'], first_hash))] += 1
        print(f"  {name} x layout:", dict(t))


if __name__ == '__main__':
    main()
