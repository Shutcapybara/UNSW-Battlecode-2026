"""ouroboros-m01-vibing-mimic: behavioural clone of public team Vibing++ (sub 8264).

Every decision is a learned imitation of Vibing++'s recorded actions, computed only
from this dragon's own round blocks and its own process memory (features_view.py,
the exact code used to build the training rows).  No sonar is sent: the target's
64-bit payload semantics are unknown, so this is the documented no-message variant.

MODE (env MIMIC_MODE or params.json):
  pure    argmax of the imitation model (only engine-invalid splits are masked)
  guarded additionally masks first steps into kelp/bodies (certain death), keeps
          enemy-head trades and unknown portal exits; all-masked -> SPLIT 1
Split size: length-2 (target's dominant allocation; child takes the tail).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import features_view as FV  # noqa: E402
from predictor import Predictor  # noqa: E402

PARAMS = {'mode': 'guarded'}
try:
    PARAMS.update(json.load(open(os.path.join(HERE, 'params.json'))))
except Exception:
    pass
MODE = os.environ.get('MIMIC_MODE', PARAMS['mode'])
MODEL = Predictor(os.path.join(HERE, 'model.json'))
READ = sys.stdin.readline
DEATH = {1, 2, 3, 4, 5, 6}


def read_block():
    lines = []

    def take(n=1):
        for _ in range(n):
            s = READ()
            while s and not s.strip():
                s = READ()  # the engine separates blocks with a blank line
            if not s:
                raise EOFError
            lines.append(s.rstrip('\n'))
    take(5)
    n = int(lines[4].split()[1])
    take(n)
    take(1)
    take(48 if not lines[-1].startswith('ECHOES') else 49)
    take(1)
    nb = int(lines[-1].split()[1])
    take(nb)
    take(15)
    return lines


def main():
    init = {}
    while 'UNIT_LIMIT' not in init:
        s = READ()
        if not s:
            return
        p = s.split()
        if not p:
            continue
        if p[0] == 'MAP':
            init['W'], init['H'] = int(p[1]), int(p[2])
        else:
            init[p[0]] = p[1]
    proc = FV.Proc(int(init['ID']), init['TEAM'], init['W'], init['H'], int(init['UNIT_LIMIT']))
    while True:
        try:
            lines = read_block()
        except EOFError:
            return
        blk, _ = FV.parse_block(lines)
        row = proc.features(blk)
        probs = MODEL.proba(row)
        L, units = blk['length'], blk['units']
        if L < 4 or units >= proc.unit_limit:
            probs['split'] = 0.0
        if MODE == 'guarded':
            for rel in ('F', 'R', 'L'):
                if row['c%s_block' % rel] in DEATH:
                    probs[rel] = 0.0
            if max(probs[r] for r in ('F', 'R', 'L')) == 0 and probs['split'] == 0:
                probs['suicide'] = 1.0
        choice = max(probs, key=probs.get)
        out = []
        if choice in ('F', 'R', 'L'):
            out.append('MOVE ' + FV.rel_to_abs(blk['dir'], choice))
            proc.record_action('move', rels=[choice])
        elif choice == 'split':
            out.append('SPLIT %d' % (L - 2))
            proc.record_action('split', split=L - 2)
        else:
            out.append('SPLIT 1')
            proc.record_action('split', split=1)
        out.append('PROTOCOL 3')
        out.append('ENDTURN')
        sys.stdout.write('\n'.join(out) + '\n')
        sys.stdout.flush()


main()
