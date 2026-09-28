"""V1 probe validation: run the probe bots and check features return the values their behaviour fixes.

python -m tools.analysis.features.probe_check --unswbc PATH [--maps trophy,default] [--out build/zoo/probes]
"""
import argparse, json, subprocess
from pathlib import Path

from .frame import decode
from .extract import extract

P = Path(__file__).parent / 'probes'


def run(exe, mp, out):
    rep = Path(out) / f'probe_{mp}.replay'
    rep.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([exe, 'run', '--seed', '1', '--no-logs', '-o', str(rep), f'maps/{mp}.map',
                    str(P / 'probe-northsonar'), str(P / 'probe-silent-splitter')], check=True, capture_output=True)
    return rep


def check(rep):
    g = decode(rep)
    x = extract(g)
    a, b = x['side_rows']
    ev = g['events']
    split_rounds = sorted({s['round'] for s in ev['splits']})
    res = {
        'A rays == turns that survived the move': sum(1 for p in ev['sonar'] if p['team'] == 'A') == sum(
            1 for x in ev['actions'] if x['team'] == 'A' and (x['round'], x['id']) not in {(d['round'], d['id']) for d in ev['deaths'] if d['actor'] == d['id']}),
        'A north share of head rays == 1': a['rays_N_share'] == 1.0,
        'A some refraction (rays into own neck)': a['ray_refracted_share'] > 0,
        'A no splits': a['births'] == 0,
        'A no sprints': a['sprint_share'] == 0,
        'B no rays': b['rays_per_dt'] == 0,
        'B child length always 2': b['births'] == 0 or (b['child_len_median'] == 2 and b['child_len_le3_share'] == 1.0),
        'B splits only on one residue mod 20': len({r % 20 for r in split_rounds}) <= 1,
    }
    return dict(map=g['map'], rounds=g['last_round'] + 1, split_rounds=split_rounds[:6], split_residue=sorted({r % 20 for r in split_rounds}),
                checks=res, passed=all(res.values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--unswbc', default='unswbc')
    ap.add_argument('--maps', default='trophy,default,portals')
    ap.add_argument('--out', default='build/zoo/probes')
    a = ap.parse_args()
    rows = [check(run(a.unswbc, m, a.out)) for m in a.maps.split(',')]
    print(json.dumps(rows, indent=1))
    Path(a.out, 'probe_check.json').write_text(json.dumps(rows, indent=1))


if __name__ == '__main__':
    main()
