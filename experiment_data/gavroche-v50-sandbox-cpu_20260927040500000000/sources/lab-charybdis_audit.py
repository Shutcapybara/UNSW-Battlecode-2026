"""Measure use of the new decision mechanism, not just game outcomes."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
from replay import Reader


def audit(folder):
    manifest = json.loads((folder/'manifest.json').read_text())
    rows = json.loads((folder/'results.json').read_text())
    output = []
    for row in rows:
        side = 'A' if row['team_a'] == manifest['focus'] else 'B'
        root = Reader(folder/row['replay']).object(0, 0)
        teams = {}
        for line in root.text(0).splitlines():
            words = line.split()
            if words and words[0] == 'DRAGON':
                teams[len(teams)] = 'AB'[int(words[1])]
        counts = Counter()
        for event in root.items(3):
            kind, obj = event.num(0, 'H'), event.child(0)
            ident = obj.num()
            if kind == 10:
                teams[obj.num(4)] = teams[ident]
            elif kind == 4 and teams[ident] == side:
                counts['turns'] += 1
            elif kind == 7 and teams[ident] == side:
                message = obj.text(0)
                if not message.startswith('charybdis '):
                    continue
                fields = dict(re.findall(r'(\w+)=(-?[\d.]+)', message))
                counts['logged_decisions'] += 1
                if int(fields['foe']) >= 0:
                    counts['duel_visible'] += 1
                nodes = int(fields['nodes'])
                counts['nodes_total'] += nodes
                counts['nodes_max'] = max(counts['nodes_max'], nodes)
                if nodes:
                    counts['searched_decisions'] += 1
                    if int(fields['changed']):
                        counts['changed_decisions'] += 1
                        counts['changed_to_split' if int(fields['split']) else 'changed_to_move'] += 1
        output.append(dict(map=row['map'], side=side,
                           opponent=row['team_b'] if side=='A' else row['team_a'], **counts))
    (folder/'decision-trace.json').write_text(json.dumps(output, indent=2)+'\n')
    totals = Counter()
    for row in output:
        for key,value in row.items():
            if isinstance(value, int):
                if key=='nodes_max': totals[key]=max(totals[key],value)
                else: totals[key]+=value
    print(folder.name, dict(totals))
    return totals


if __name__ == '__main__':
    for folder in sys.argv[1:]:
        audit(Path(folder))
