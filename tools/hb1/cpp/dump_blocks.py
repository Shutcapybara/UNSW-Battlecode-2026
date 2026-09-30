"""Dump the exact round blocks one side's dragons received in a replay, plus their actions, for C++ parity.

    python3 tools/hb1/cpp/dump_blocks.py REPLAY SIDE > blocks.txt

Format per actor turn:  TURN <dragon> <team> <W> <H> <unit_limit>, the block lines (roundblock.build_block with
the same proto3 rule as features_v5), END, then ACT move <rels> | ACT split <k> | ACT none.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'team_recon_claude'))
import recon, roundblock, features_view as FV


def main(path, side):
    g = recon.Game(path)
    seen, pend, out = {}, {}, sys.stdout

    def cb(kind, **k):
        if kind == 'turn':
            d = k['dragon']
            if d.team != side:
                return
            n = seen.get(d.id, 0)
            seen[d.id] = n + 1
            lines = roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None))
            out.write(f'TURN {d.id} {side} {g.board.W} {g.board.H} {g.board.unit_limit}\n')
            out.write('\n'.join(lines) + '\nEND\n')
            pend['facing'] = d.facing
            pend['open'] = True
        elif kind == 'action' and pend.get('open') and k['dragon'].team == side:
            pend['open'] = False
            a = k['action']
            if a[0] == 'move':
                rels, c = [], pend['facing']
                for s in a[1]:
                    rels.append(FV.abs_to_rel(FV.DIRS[recon.DIRS.index(c)], FV.DIRS[recon.DIRS.index(s)]))
                    c = s
                out.write('ACT move ' + ''.join(rels) + '\n')
            elif a[0] == 'split':
                out.write(f'ACT split {a[1]}\n')
            else:
                out.write('ACT none\n')
    g.run(cb)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
