"""Read retained successful replays and count explicit integration markers."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT.parent/'UNSW-Battlecode-2026'
sys.path.insert(0,str(ROOT/'tools/hub/vendor/leviathan'))
from replay import unpack

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('run');ap.add_argument('--markers',nargs='+',required=True)
    ap.add_argument('--require-complete',action='store_true')
    ap.add_argument('--fail-if-present',action='store_true')
    args=ap.parse_args();out=MAIN/'build/kenma'/args.run
    manifest=json.loads((out/'manifest.json').read_text());rows=[]
    for f in sorted(out.glob('live*.json')):
        result=json.loads(f.read_text())
        if result['rc'] or result['faults'] or not result['winner']:continue
        replay=f.with_suffix('.replay')
        if not replay.exists():
            if args.require_complete:raise RuntimeError(f'Missing replay for {f.name}')
            continue
        raw=unpack(replay.read_bytes())
        rows.append({'file':replay.name,**{s:raw.count(s.encode()) for s in args.markers}})
    totals={s:sum(r[s] for r in rows) for s in args.markers}
    complete=len(rows)==len(manifest['fixtures'])
    report={'run':args.run,'replays_read':len(rows),'expected':len(manifest['fixtures']),'complete':complete,'totals':totals,'rows':rows}
    (out/'replay-log-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}),flush=True)
    if args.require_complete and not complete:raise SystemExit('Replay audit incomplete')
    if args.fail_if_present and any(totals.values()):raise SystemExit('Audited marker present')

if __name__=='__main__':main()
