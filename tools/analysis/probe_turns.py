"""Parse a judge-sandbox probe log (`LIVE/state/runtime/<candidate>/<map>-<side>.log`, `unswbc run --sandbox` output)
into one row per dragon-turn: round, bot id, team, number of stdout lines, number of SONAR lines, bytes written,
points charged, first command, living dragons per team at that round.

    python -m tools.analysis.probe_turns LOG > turns.csv

The candidate's own turns are the rows whose `team` equals the fixture side (9-A → team A, 20-B → team B).
Used for the Q6/Q7 per-ray and per-dragon cost regressions (docs/findings/2026-09-28-analysis-claude-Q6-runtime.md).
"""
import csv
import re
import sys

HDR = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) stdout:$')
PTS = re.compile(r'^round (\d+): bot (\d+) \(team ([AB])\) points (\d+) memory (\d+)$')
DRG = re.compile(r'^running round (\d+)/500.*dragons: (\d+) vs (\d+)')


def parse(path):
    rows, dragons = [], {}
    cur, lines = None, []
    for line in open(path, errors='replace'):
        line = line.rstrip('\n')
        m = HDR.match(line)
        if m:
            cur, lines = (int(m.group(1)), int(m.group(2)), m.group(3)), []
            continue
        m = DRG.match(line)
        if m:
            dragons[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
            continue
        m = PTS.match(line)
        if m and cur:
            r, b, t = cur
            rows.append(dict(round=r, bot=b, team=t, n_lines=sum(1 for l in lines if l), n_sonar=sum(1 for l in lines if l.startswith('SONAR ')),
                             bytes=sum(len(l) + 1 for l in lines if l), points=int(m.group(4)), first=(lines[0].split()[0] if lines and lines[0] else '')))
            cur, lines = None, []
            continue
        if cur is not None:
            lines.append(line)
    for r in rows:
        d = dragons.get(r['round'] + 1) or dragons.get(r['round']) or (None, None)
        r['dragons_a'], r['dragons_b'] = d
    return rows


def main():
    rows = parse(sys.argv[1])
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)


if __name__ == '__main__':
    main()
