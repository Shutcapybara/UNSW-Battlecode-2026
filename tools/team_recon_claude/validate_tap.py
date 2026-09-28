"""Compare reconstructed round blocks with the blocks a tapped bot actually read.

    python3 validate_tap.py REPLAY TAPDIR TEAM
"""
import collections, glob, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import recon, roundblock


def parse_logs(tapdir):
    """-> {dragon_id: [block_lines, ...]} (init block stripped). One file per process."""
    per = collections.defaultdict(list)
    for f in glob.glob(tapdir + '/*.log'):
        lines = [l.rstrip('\n') for l in open(f)]
        i, did = 0, None
        blocks = []
        while i < len(lines):
            if lines[i].startswith('ID '):
                did = int(lines[i].split()[1]); i += 4; continue
            if not lines[i].startswith('ROUND'):
                i += 1; continue
            j = i + 1
            while j < len(lines) and not lines[j].startswith('ROUND') and not lines[j].startswith('ID '):
                j += 1
            blk = lines[i:j]
            while blk and blk[-1] == '':
                blk.pop()
            blocks.append(blk); i = j
        per[did].append((f, blocks))
    return per


def main(replay, tapdir, team):
    logs = parse_logs(tapdir)
    g = recon.Game(replay)
    turns = collections.defaultdict(list)
    first = {}

    def cb(kind, **k):
        if kind == 'turn' and k['dragon'].team == team:
            d = k['dragon']
            n = len(turns[d.id])
            turns[d.id].append(roundblock.build_block(g, d, proto3=(n > 0 or d.parent is not None)))
    g.run(cb)
    stats = collections.Counter()
    mism = collections.Counter()
    examples = []
    for did, recs in turns.items():
        got = []
        for f, blocks in logs.get(did, []):
            got += blocks
        for i, rb in enumerate(recs):
            if i >= len(got):
                stats['missing_log'] += 1; continue
            lb = got[i]
            if lb == rb:
                stats['exact'] += 1
            else:
                stats['diff'] += 1
                for a, b in zip(lb, rb):
                    if a != b:
                        mism[a.split()[0] if a else '?'] += 1
                        if len(examples) < 8:
                            examples.append((did, i, a, b))
                        break
                if len(lb) != len(rb):
                    mism['length'] += 1
    print(json.dumps(dict(stats=stats, first_mismatch_kind=mism, checks=g.checks)), flush=True)
    for e in examples:
        print('EX', e)
    return stats


if __name__ == '__main__':
    main(*sys.argv[1:4])
