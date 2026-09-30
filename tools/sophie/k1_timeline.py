"""K-1: a compact decoded read of one game from team 7's side (a text stand-in for the visualiser pass).

    python tools/sophie/k1_timeline.py <game_id> [--step 25]
"""
import collections, gzip, json, os, sys
from pathlib import Path

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools.analysis.features.frame import decode  # noqa: E402
import hazard  # noqa: E402


def main(gid, step=25):
    idx = next(json.loads(l) for l in open(REPO / 'public_replays/corpus/index.jsonl') if json.loads(l)['game_id'] == int(gid))
    us = 'A' if idx['team_a'] == 7 else 'B'
    th = 'B' if us == 'A' else 'A'
    g = decode(REPO / f'public_replays/corpus/replays/{gid}.replay')
    o = json.load(gzip.open(REPO / f'build/sophie/x2/us/{gid}.json.gz', 'rt'))
    feats = hazard.cell_features(str(REPO / f"build/sophie/maps/{o['meta']['map_hash']}.map"))['cells']
    sig = lambda c: next((k.split('_', 1)[0] for k in hazard.SIGNATURES if hazard.SIGNATURES[k][1](feats[c])), '-')
    print(f"game {gid} {g['map']} us={us} vs team {idx['team_b'] if us == 'A' else idx['team_a']} ranked={idx['ranked']} "
          f"sub={idx['bot_a'] if us == 'A' else idx['bot_b']} winner={g['winner']} ({g['reason']}) last={g['last_round']}")
    R = g['rounds']
    eats = collections.Counter((e['team'], e['round'] // step, e['origin']) for e in g['events']['eats'])
    splits = collections.Counter((s['team'], s['round'] // step) for s in g['events']['splits'])
    D = collections.defaultdict(list)
    for d in o['deaths']:
        D[(d['s'], d['r'] // step)].append(d)
    for b in range(0, (g['last_round'] // step) + 1):
        r = b * step
        snap = R[min(r, len(R) - 1)]
        st = {t: (sum(1 for i, (tt, bb) in snap.items() if tt == t), sum(len(bb) for i, (tt, bb) in snap.items() if tt == t),
                  max([len(bb) for i, (tt, bb) in snap.items() if tt == t] or [0])) for t in 'AB'}
        def dd(t):
            c = collections.Counter()
            for d in D[(t, b)]:
                tag = d['cls'][:6] + ('*' if d['tr'] else '') + ('/' + sig((d['x'], d['y'])) if sig((d['x'], d['y'])) != '-' else '')
                c[tag] += 1
            return ' '.join(f'{k}:{v}' for k, v in c.most_common(5))
        pe = lambda t: sum(v for (tt, bb, oo), v in eats.items() if tt == t and bb == b)
        bed = lambda t: eats[(t, b, 'bed')]
        print(f" r{r:3d} us u{st[us][0]:3d} L{st[us][1]:4d} top{st[us][2]:3d} | them u{st[th][0]:3d} L{st[th][1]:4d} top{st[th][2]:3d} |"
              f" eat us {pe(us):3d}(bed {bed(us):3d}) them {pe(th):3d}(bed {bed(th):3d}) | split {splits[(us, b)]:2d}/{splits[(th, b)]:2d}")
        if D[(us, b)]:
            print(f"      our deaths {len(D[(us, b)]):3d}: {dd(us)}")
        if D[(th, b)]:
            print(f"      their deaths {len(D[(th, b)]):3d}: {dd(th)}")


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 25)
