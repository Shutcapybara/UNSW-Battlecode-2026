"""Summarize retained Kenma replays, including queen deaths on other dragons' turns."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT))
from queen_replay import recent_queens
from replay import analyse

def summarize(path):
    metrics=analyse(path)
    recent=recent_queens(path.read_bytes())
    queens={}
    for ident in (0,1):
        deaths=[e for e in metrics['death_events'] if e['id']==ident]
        assert len(deaths)<=1
        queens['AB'[ident]]=dict(alive=not deaths,death=deaths[0] if deaths else None,last_turns=recent[ident])
    return dict(replay=str(path),rounds=metrics['rounds'],winner=metrics['outcome'],queens=queens,teams=metrics['teams'],population=metrics['population'])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('runs',nargs='+')
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    rows=[]
    for name in args.runs:
        for p in sorted((MAIN/'build/kenma'/name).glob('*.replay')):
            result=p.with_suffix('.json')
            if result.exists():
                r=json.loads(result.read_text())
                if r['rc'] or not r['winner'] or r['faults']:
                    continue
            else:
                continue  # Never analyze an in-flight replay.
            rows.append(summarize(p))
    out=MAIN/'build/kenma'/args.output
    out.write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:
        print(Path(r['replay']).parent.name,Path(r['replay']).stem,
              {t:('alive' if q['alive'] else f"r{q['death']['round']} {q['death']['cause']} actor {q['death']['actor']}") for t,q in r['queens'].items()})
    print('saved',len(rows),'replays to',out)

if __name__=='__main__':
    main()
