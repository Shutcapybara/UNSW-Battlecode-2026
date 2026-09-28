"""Refresh the current frozen roster's ratings from the shared outcome ledger."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import tempfile
from threading import Event
import time
import traceback
from filelock import FileLock
from benchmark_dashboard_data import main as build_snapshot
from game_stats import ROOT, digest, publish_games


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_text(path, text):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as f:
        temporary=Path(f.name)
        f.write(text)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def inputs(root=ROOT):
    """Track new contributions, identity metadata and a switch to another roster."""
    pointer=root/'experiment_data/benchmark-current.json'
    campaign=Path(json.loads(pointer.read_text())['directory'])
    paths=[pointer, campaign/'manifest.json', campaign/'aliases.json']
    paths+=sorted((root/'game_stats/runs').glob('*.parquet'))
    paths+=sorted((root/'game_stats/sources').glob('*.json'))
    return digest([(str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths])


def summary(data):
    bots={b['id']:b for b in data['bots']}
    lines=['# Current bot estimates', '',
        f"Updated {data['at']}; ledger snapshot taken {data['data_at']}.", '',
        f"{len(bots)} frozen bot versions, {len(data['maps'])} maps, "
        f"{data['fixtures']:,} distinct fixtures from {data['matching_records']:,} matching records "
        f"in the {data['ledger_games']:,}-game shared ledger.", '',
        f"{data.get('rating_context_bots', 0)} retired/context versions also anchor the fit; "
        'they are not scheduled for new games or listed in this active table.', '',
        'Score is predicted win + half-draw rate against the same reference panel, '
        'using the frozen campaign map weights and equal starting-side weights. The model adjusts for opponent, map '
        'and side, and uses matchup interactions when held-out prediction improves. '
        'Ranges show the middle 80% of opponent-pair bootstrap estimates, expanded '
        'to include the point estimate; they are sensitivity ranges, not calibrated confidence intervals.', '',
        'Sparse means fewer than 60 fixtures, 5 opponents, 8 maps, or observations on 80% '
        'of the target map weight. Unplayed maps borrow strength from the model; their '
        'predictions are not direct evidence. Similarity means '
        'the smallest observed score difference on at least 30 shared paired opponent/map cells; '
        'it does not establish similar code or tactics. Missing games and errors are excluded.', '',
        '| Rank | Bot | Score | Range | Fixtures | Opponents | Maps | Evidence | Closest observed profile |',
        '|---:|---|---:|---|---:|---:|---:|---|---|']
    for rank,b in enumerate(sorted(bots.values(),key=lambda b:-b['score']),1):
        neighbor=b['similar'][0] if b['similar'] else None
        similar=(f"{bots[neighbor['id']]['name']} ({neighbor['difference']*100:.1f} pp gap; "
                 f"{neighbor['shared']} cells)") if neighbor else 'Insufficient overlap'
        lines.append(f"| {rank} | {b['name']} | {b['score']:.1%} | {b['low']:.1%}–{b['high']:.1%} "
            f"| {b['games']} | {b['opponents']} | {b['maps']} | "
            f"{'Established' if b['established'] else 'Sparse'} | {similar} |")
    lines+=['', 'Matching record sources: '+json.dumps(data['source_counts'],sort_keys=True)+'.', '',
        'Reference panel: '+', '.join(bots[i]['name'] for i in data['reference_ids'])+'.', '',
        'Map distribution: '+json.dumps(data.get('map_weights',{}),sort_keys=True)+'.', '',
        'Refresh health is recorded in `status.json`; `latest.json` includes map profiles, '
        'head-to-head scores and source/map fingerprints. The earlier inline chart remains a snapshot.', '']
    return '\n'.join(lines)


def refresh(out):
    # Include contribution files received through Git, even before a manual rebuild.
    # The existing writer lock protects this union against concurrent match writers.
    publish_games([])
    with tempfile.TemporaryDirectory(prefix='.rating-',dir=out) as directory:
        data=build_snapshot(Path(directory))
    report=summary(data)
    encoded=json.dumps(data,separators=(',',':'),allow_nan=False)+'\n'
    atomic_text(out/'latest.json',encoded)
    atomic_text(out/'latest.md',report)
    return data


def run(out, interval=None):
    out.mkdir(parents=True,exist_ok=True)
    stop=Event()
    for sig in (signal.SIGINT,signal.SIGTERM):
        signal.signal(sig,lambda *_:stop.set())
    with FileLock(str(out/'.watch.lock'),timeout=0):
        previous=None
        while not stop.is_set():
            start=time.monotonic()
            status=dict(pid=os.getpid(),checked_at=now(),interval_seconds=interval)
            try:
                signature=inputs()
                if signature!=previous:
                    atomic_text(out/'status.json',json.dumps(status|dict(state='updating'))+'\n')
                    data=refresh(out)
                    previous=signature
                    print(f"Published {data['fixtures']} fixtures at {data['at']}",flush=True)
                else:
                    data=json.loads((out/'latest.json').read_text())
                status.update(state='watching' if interval else 'complete',last_success=data['at'],data_at=data['data_at'])
            except Exception as error:
                traceback.print_exc()
                status.update(state='error',error=str(error))
                if not interval:
                    atomic_text(out/'status.json',json.dumps(status)+'\n')
                    raise
            atomic_text(out/'status.json',json.dumps(status)+'\n')
            if not interval:break
            stop.wait(max(1,interval-(time.monotonic()-start)))
        if stop.is_set():
            atomic_text(out/'status.json',json.dumps(status|dict(state='stopped',stopped_at=now()))+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'experiment_data/bot-ratings')
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--interval',type=int,default=300)
    args=parser.parse_args()
    if args.interval<30:parser.error('--interval must be at least 30 seconds')
    run(args.output.resolve(),args.interval if args.watch else None)
