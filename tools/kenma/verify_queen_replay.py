"""Compare the narrow reader against saved full-reconstruction evidence."""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[2];MAIN=ROOT.parent/'UNSW-Battlecode-2026';sys.path.insert(0,str(ROOT))
from queen_replay import recent_queens
from replay_diagnostics import analyse
out=MAIN/'build/kenma';expected=json.loads((out/'k21-final-diagnostics.json').read_text());start=time.monotonic();turns=0
for row in expected:
    recent=json.loads(json.dumps(recent_queens(Path(row['replay']).read_bytes())))
    metrics=analyse(Path(row['replay']));queens={}
    for i in (0,1):
        deaths=[e for e in metrics['death_events'] if e['id']==i];assert len(deaths)<=1
        queens['AB'[i]]=dict(alive=not deaths,death=deaths[0] if deaths else None,last_turns=recent[str(i)])
    result=dict(replay=row['replay'],rounds=metrics['rounds'],winner=metrics['outcome'],queens=queens,teams=metrics['teams'],population=metrics['population'])
    assert json.loads(json.dumps(result))==row,row['replay']

    for i in (0,1):
        assert recent[str(i)]==row['queens']['AB'[i]]['last_turns'],(row['replay'],i,recent[str(i)],row['queens']['AB'[i]]['last_turns'])
        turns+=len(recent[str(i)])
report=dict(replays=len(expected),queen_histories=2*len(expected),retained_turns=turns,fields=['round','head','length','units','action'],seconds=round(time.monotonic()-start,3),all_equal=True,full_summary_equal=True,reference='k21-final-diagnostics.json, original full rebuild.walk reader')
(out/'queen-reader-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
