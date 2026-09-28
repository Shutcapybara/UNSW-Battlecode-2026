"""Transfer graft from Vibing++ analysis: trapped-split escape guard.

Wraps an unmodified host bot.  Taps stdin (the host still reads every byte) and
filters the host's reply: if the host's MOVE would take its first step into kelp
or any dragon body (certain death), no adjacent enemy head is available for a
trade, length >= 4 and the team is below the unit limit, the MOVE is replaced by
SPLIT length-2 (child takes the tail and exits backwards; Vibing++ does this on
96% of such turns).  Everything else (sonar, logs, other actions) passes through.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fv_guard as FV  # noqa: E402

DEADLY = {1, 2, 3, 4, 5, 6}
STATE = {'lines': [], 'init': {}, 'replaced': 0}
LOG = os.environ.get('TRAPSPLIT_LOG', '/tmp/trapsplit_guard.log')


class TapIn:
    def __init__(self, f):
        self.f = f

    def readline(self, *a):
        s = self.f.readline(*a)
        if s:
            t = s.rstrip('\n')
            if t.startswith('ROUND'):
                STATE['lines'] = []
            if t.strip():
                STATE['lines'].append(t)
            p = t.split()
            if p and p[0] in ('ID', 'TEAM', 'UNIT_LIMIT'):
                STATE['init'][p[0]] = p[1]
            elif p and p[0] == 'MAP':
                STATE['init']['W'], STATE['init']['H'] = int(p[1]), int(p[2])
        return s

    def __iter__(self):
        while True:
            s = self.readline()
            if not s:
                return
            yield s

    def __getattr__(self, k):
        return getattr(self.f, k)


def decide(reply_lines):
    lines = STATE['lines']
    if not lines or not lines[0].startswith('ROUND'):
        return reply_lines
    mv = [i for i, l in enumerate(reply_lines) if l.startswith('MOVE ')]
    if not mv:
        return reply_lines
    try:
        blk, _ = FV.parse_block(lines)
    except Exception:
        return reply_lines
    L, units = blk['length'], blk['units']
    lim = int(STATE['init'].get('UNIT_LIMIT', 64))
    if L < 4 or units >= lim:
        return reply_lines
    proc = FV.Proc(int(STATE['init']['ID']), STATE['init']['TEAM'], STATE['init']['W'], STATE['init']['H'], lim)
    row = proc.features(blk)
    first = reply_lines[mv[-1]].split()[1][0]
    rel = FV.abs_to_rel(blk['dir'], first)
    rels = [r for r in ('F', 'R', 'L')]
    if rel == 'B':
        code = 2
    else:
        code = row['c%s_block' % rel]
    if code not in DEADLY:
        return reply_lines
    if any(row['c%s_block' % r] in (0, -1, 7) for r in rels):
        return reply_lines  # a non-certain-death option exists: leave the host's choice alone
    reply_lines[mv[-1]] = 'SPLIT %d' % (L - 2)
    STATE['replaced'] += 1
    if LOG:
        with open(LOG, 'a') as fh:
            fh.write('%s %s %d %d\n' % (STATE['init']['TEAM'], STATE['init']['ID'], blk['round'], L))
    return reply_lines


class FilterOut:
    def __init__(self, f):
        self.f, self.buf = f, ''

    def write(self, s):
        self.buf += s
        while '\n' in self.buf:
            if 'ENDTURN' not in self.buf:
                break
            head, _, rest = self.buf.partition('ENDTURN')
            nl = rest.find('\n')
            tail = rest[:nl + 1] if nl >= 0 else rest
            self.buf = rest[nl + 1:] if nl >= 0 else ''
            body = [l for l in head.split('\n')]
            body = decide([l for l in body if l != ''] ) if True else body
            self.f.write('\n'.join(body) + '\nENDTURN' + tail)
            self.f.flush()
        return len(s)

    def flush(self):
        self.f.flush()

    def __getattr__(self, k):
        return getattr(self.f, k)
