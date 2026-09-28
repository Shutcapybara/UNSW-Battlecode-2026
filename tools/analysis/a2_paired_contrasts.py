"""A2 — candidate-minus-control paired contrasts (handoff §3.2).

For every experiment block with exact (map_id, side, opponent submission) pairs: per-map paired
score delta and stage-profile deltas on the SAME pairs (units r100, total r250, longest r400,
longest r499, deaths/1k). Paired differences only; unpaired games (layout fills etc.) are listed,
never pooled. Unit of independence: the pair.

'What changed when the outcome changed': pairs are split by score delta != 0 (outcome flipped)
vs == 0 (outcome held) and their stage deltas compared.
"""
import statistics
from collections import defaultdict

from live_load import load, per_1k, stage

EXPERIMENTS = ('a01aee66', '8b12ae55', '02356998', '88a5b9be')


def pair_stage_delta(c, k):
    keys = (('units', 100, 'self'), ('total', 250, 'self'), ('longest', 400, 'self'), ('longest', 499, 'self'))
    out = {}
    for name, r, who in keys:
        a, b = stage(c, r, name, who), stage(k, r, name, who)
        out[f'{name}_r{r}'] = (a - b) if (a is not None and b is not None) else None
    for key in ('death_wall', 'death_h2h'):
        a, b = per_1k(c, key), per_1k(k, key)
        out[key + '_1k'] = round(a - b, 1) if (a is not None and b is not None) else None
    return out


def main():
    games = load()
    blocks = defaultdict(dict)
    for g in games:
        if g['_block']:
            blocks[g['_block']].setdefault(g['submission'], []).append(g)
    import json
    from live_load import experiments as exps
    for e in exps():
        eid = e['id']
        if not any(eid.startswith(x) for x in EXPERIMENTS):
            continue
        cand, ctrl = e['candidate'], e['control']
        print(f"\n# {eid[:8]} candidate {cand} vs control {ctrl} — {e['status']}\n")
        all_pairs = []
        for b in (e.get('decision') or {}).get('pairs', []):
            bid, opp = b['block'], b['opponent']
            cb = blocks.get(bid, {})
            cgames, kgames = cb.get(cand, []), cb.get(ctrl, [])
            kmap = {g['map_id']: g for g in kgames}
            rows = []
            for cg in cgames:
                kg = kmap.get(cg['map_id'])
                if not kg:
                    continue
                d = dict(map_id=cg['map_id'], map=cg['map_name'], score=cg['score'] - kg['score'],
                         length=(cg.get('final', {}).get('longest') or 0) - (kg.get('final', {}).get('longest') or 0))
                d.update(pair_stage_delta(cg, kg))
                rows.append(d)
            unpaired = len(cgames) - len(rows)
            print(f"## block {bid[:8]} opp {opp} — {len(rows)} exact pairs ({unpaired} candidate games unpaired, "
                  f"{len(kgames)} control games)")
            if not rows:
                continue
            def f(v, spec='+3.0f', nd=0):
                return ('%' + spec) % v if v is not None else '—'
            for d in rows:
                flipped = 'FLIP' if d['score'] != 0 else '    '
                print(f"  - {flipped} map {d['map']:<20} score {f(d['score'], '+.0f')} length {f(d['length'], '+4d')} "
                      f"u100 {f(d['units_r100'])} t250 {f(d['total_r250'], '+4.0f')} l400 {f(d['longest_r400'])} "
                      f"l499 {f(d['longest_r499'])} wall {f(d['death_wall_1k'], '+5.1f')} h2h {f(d['death_h2h_1k'], '+5.1f')}")
            med = lambda k: statistics.median([r[k] for r in rows if r[k] is not None]) if any(r[k] is not None for r in rows) else None
            better = sum(1 for r in rows if r['score'] > 0)
            worse = sum(1 for r in rows if r['score'] < 0)
            print(f"  -> block median: score {med('score'):+.0f} length {med('length'):+.0f} u100 {med('units_r100'):+.0f} "
                  f"t250 {med('total_r250'):+.0f} l400 {med('longest_r400'):+.0f} l499 {med('longest_r499'):+.0f} "
                  f"wall {med('death_wall_1k'):+.1f} h2h {med('death_h2h_1k'):+.1f} | score better/worse {better}/{worse}")
            all_pairs.extend((bid, opp, d) for d in rows)
        if all_pairs:
            rows = [d for _, _, d in all_pairs]
            fl = [d for d in rows if d['score'] != 0]
            hd = [d for d in rows if d['score'] == 0]
            print(f"\n== {eid[:8]} overall: {len(rows)} pairs; flipped {len(fl)} (cand {sum(1 for d in fl if d['score']>0)} / ctrl {sum(1 for d in fl if d['score']<0)})")
            for label, grp in (('outcome flipped', fl), ('outcome held', hd)):
                if not grp:
                    continue
                print(f"   {label} (n={len(grp)}): median length {statistics.median([d['length'] for d in grp]):+.0f} "
                      f"u100 {statistics.median([d['units_r100'] for d in grp if d['units_r100'] is not None]):+.0f} "
                      f"t250 {statistics.median([d['total_r250'] for d in grp if d['total_r250'] is not None]):+.0f} "
                      f"l400 {statistics.median([d['longest_r400'] for d in grp if d['longest_r400'] is not None]):+.0f} "
                      f"wall {statistics.median([d['death_wall_1k'] for d in grp if d['death_wall_1k'] is not None]):+.1f} "
                      f"h2h {statistics.median([d['death_h2h_1k'] for d in grp if d['death_h2h_1k'] is not None]):+.1f}")


if __name__ == '__main__':
    main()
