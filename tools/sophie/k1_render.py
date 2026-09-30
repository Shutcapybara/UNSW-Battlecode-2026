"""K-1: render the per-map trouble-card sections (markdown) from the JSON outputs.

    python tools/sophie/k1_render.py > build/sophie/cards.md
"""
import json, os, sys
from pathlib import Path

REPO = Path(os.environ.get('K1_TREE', Path(__file__).resolve().parents[2]))
CARDS = json.load(open(REPO / 'game_stats/runs/sophie-trouble-all.json'))['cards']
RANK = json.load(open(REPO / 'game_stats/runs/sophie-trouble-ranked.json'))['cards']
RES = json.load(open(REPO / 'game_stats/runs/sophie-trouble-residual.json'))['per_map']
EXT = json.load(open(REPO / 'docs/findings/data/sophie-K1-extras.json'))['hot_cells']
CL = ['wall', 'self', 'ally_body', 'h2h_ally', 'enemy_body', 'h2h_enemy', 'invalid']
CTX = ['newborn', 'trapped', 'portal', 'transit', 'crowd23', 'fight']
f1 = lambda v: '–' if v is None else f'{v:.1f}'
f2 = lambda v: '–' if v is None else f'{v:.2f}'


def section(m, para):
    c = CARDS[m]
    L, G = c['literal'], c['general']
    rk = RES.get(m, RES.get('Prisoners Dilemma'))
    out = [f'### {m}', '']
    rn = RANK.get(m, {})
    out.append(f"n = {c['n_us']} side-games of ours (ranked {rn.get('n_us', 0)}), {c['n_field']} field ({c['n_top10']} top-10). "
               f"Win share {G['won']['us']:.2f} (ranked {((rn.get('general') or {}).get('won') or {}).get('us') or float('nan'):.2f}); "
               f"win-probability residual **{rk['residual']:+.3f} ± {rk['se']:.3f}** (actual {rk['actual']:.2f} vs {rk['expected']:.2f} "
               f"expected from ratings, n = {rk['n']}).")
    if 'seat' in c:
        s = c['seat']
        out.append(f"Seat/spawn: spawn P {f2(s['P']['us_win'])} (n {s['P']['n_us']}, field {f2(s['P']['field_win'])}), "
                   f"spawn Q {f2(s['Q']['us_win'])} (n {s['Q']['n_us']}, field {f2(s['Q']['field_win'])}).")
    out += ['', '| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |',
            '|---|---|---|---|---|']
    for k in CL + ['all']:
        n, ln = L.get(f'n_{k}_per1k'), L.get(f'len_{k}_per1k')
        if not n:
            continue
        out.append(f"| {k} | {f2(n['us'])} · {f2(n['field'])} · {f2(n['top10'])} | {n['excess_top10']:+.2f} | {f1(ln['us'])} · {f1(ln['field'])} | {f2(n['pct'])} |")
    out += ['', '| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |', '|---|---|---|---|']
    for k in CTX:
        n, ln = L[f'n_ctx_{k}_per1k'], L[f'len_ctx_{k}_per1k']
        out.append(f"| {k} | {f2(n['us'])} · {f2(n['field'])} | {f1(ln['us'])} · {f1(ln['field'])} | {f2(n['pct'])} |")
    out += ['', 'Deaths per 1k dragon-turns spent in the band (us / field):', '',
            '| band | wall | self | ally body | ally head-on | enemy head-on |', '|---|---|---|---|---|---|']
    for b in ('round', 'length'):
        for lab, v in c['bands'][b].items():
            r = v['rates']
            out.append(f"| {lab} | " + ' | '.join(f"{r[k]['us']:.1f} / {r[k]['field']:.1f}" for k in ('wall', 'self', 'ally_body', 'h2h_ally', 'h2h_enemy')) + ' |')
    out += ['', '| general (medians; us · field · top-10) | value | field pct |', '|---|---|---|']
    rows = [('pearls r50 / r100 / r250', ['pearls@50', 'pearls@100', 'pearls@250']), ('dragons r100', ['units100']), ('length r100', ['total100']),
            ('births by r100', ['births@100']), ('pearls /100 dt (r<100)', ['pearls_per100dt_r100']), ('moves per pearl', ['moves_per_pearl']),
            ('newborn deaths /100 births', ['newborn_per100births']), ('behind on length at r100 (share)', ['behind100']),
            ('idle turns /1k dt', ['stationary_per1k']), ('loop turns /1k dt (head back within 4)', ['oscillation_per1k']),
            ('portal transits per game', ['transits']), ('deaths /100 transits (≤2 rounds)', ['transit_deaths_per100']),
            ('last split round', ['last_split']), ('sonar rays per dragon-turn', ['rays_per_dt']), ('TLE turns per game (mean)', ['tle'])]
    for lab, ks in rows:
        vals = ' / '.join(f"{G[k]['us']:.2f} · {G[k]['field']:.2f} · {f2(G[k].get('top10'))}" if G[k]['us'] is not None else '–' for k in ks)
        pc = ' / '.join(f2(G[k].get('pct')) for k in ks)
        out.append(f'| {lab} | {vals} | {pc} |')
    fb = G['first_behind_round_med']
    out.append(f"| first-behind round (median, games behind at r100) | {f1(fb['us'])} · {f1(fb['field'])} | |")
    ratio = G['pearls@100'].get('ratio_field')
    out.append('')
    out.append(f"Economy: pearls at r100 = **{ratio:.2f}× the field median** (top-10 {G['pearls@100']['top10'] / G['pearls@100']['field']:.2f}×).")
    h = EXT.get(m)
    if h:
        bs = sorted(h['by_signature'].items(), key=lambda kv: -kv[1])[:3]
        out.append(f"Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to {h['total_excess_len']:.0f} "
                   f"segments over {c['n_us']} games; by signature: " + ', '.join(f'{k} {v:+.0f}' for k, v in bs) +
                   '; top cells: ' + ', '.join(f"({t['x']},{t['y']}) {t['sig']} {t['us_len_per1k']:.0f} vs {t['field_len_per1k']:.0f}" for t in h['top'][:4]) + '.')
    out += ['', f'**What goes wrong here.** {para}', '']
    return '\n'.join(out)


if __name__ == '__main__':
    paras = json.load(open(sys.argv[1]))
    for m in [k for k in CARDS if k != 'ALL']:
        print(section(m, paras.get(m, '(no paragraph)')))
