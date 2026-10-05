#!/usr/bin/env python3
"""Deploy checks: zip size, judge-sandbox games (points per turn incl. first turns, faults).

    python3 tools/bokuto/deploycheck.py BOT [--opp OPP] [--maps schooltime,unsw,...] [--seed 1] [--root .] [--unswbc unswbc]
Runs the sandbox games one at a time (the sandbox is memory-hungry) and parses the replay for cpu points per action.
"""
import argparse, io, json, os, re, subprocess, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/analysis/features'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools/hub/vendor/ouroboros'))


def zip_size(botdir: Path) -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(botdir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.startswith('.'):
                    continue
                p = Path(root) / f
                z.write(p, p.relative_to(botdir))
    return buf.tell()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--opp', default='carthage-05-free-sprint')
    ap.add_argument('--maps', default='schooltime,unsw,slithery_fight,australia'); ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[2])); ap.add_argument('--unswbc', default='unswbc')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    root = Path(a.root); botdir = root / 'bots' / a.bot
    zs = zip_size(botdir)
    print(f'zip {zs} bytes = {zs / 1048576:.2f} MiB ({"OK" if zs <= 4 * 1048576 else "TOO BIG"})', flush=True)
    import frame
    results = []
    for m in a.maps.split(','):
        for seat in ('A', 'B'):
            bots = [a.bot, a.opp] if seat == 'A' else [a.opp, a.bot]
            rp = root / 'build' / 'deploy' / f'{a.bot}__{m}__{seat}.json'
            rp.parent.mkdir(parents=True, exist_ok=True)
            cmd = [a.unswbc, 'run', '--sandbox', '--seed', str(a.seed), '-o', str(rp), '--no-debug', str(root / 'maps/live' / f'{m}.map')] + [str(root / 'bots' / b) for b in bots]
            p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
            text = p.stdout + p.stderr
            res = re.search(r'team (A|B) wins.*|draw.*', text)
            g = frame.decode(rp)
            team = seat
            acts = [x for x in g['events']['actions'] if x['team'] == team and x['cpu'] is not None]
            first = [x for x in acts if x['round'] == 0 or True]
            cpus = sorted(x['cpu'] for x in acts)
            # first turns: a dragon's first action = first round it appears; approximate with round-0 and any action
            # whose cpu is the first recorded for that id
            seen = set(); firsts = []
            for x in g['events']['actions']:
                if x['team'] != team or x['cpu'] is None: continue
                if x['id'] not in seen: seen.add(x['id']); firsts.append(x['cpu'])
            faults = [d for d in g['events']['deaths'] if d['team'] == team and d['cause'] in ('invalid', 'other')]
            tle = sum(1 for x in acts if x.get('tle'))
            r = dict(map=m, seat=seat, result=res.group(0) if res else text[-200:], turns=len(acts),
                     max_points=cpus[-1] if cpus else None, p99=cpus[int(len(cpus) * 0.99)] if cpus else None,
                     max_first_turn=max(firsts) if firsts else None, invalid_deaths=len(faults), tle=tle)
            results.append(r)
            print(json.dumps(r), flush=True)
    summary = dict(bot=a.bot, zip_bytes=zs, games=results,
                   max_points=max((r['max_points'] or 0) for r in results), max_first_turn=max((r['max_first_turn'] or 0) for r in results),
                   invalid_deaths=sum(r['invalid_deaths'] for r in results), tle=sum(r['tle'] for r in results))
    print(json.dumps({k: v for k, v in summary.items() if k != 'games'}))
    if a.out:
        Path(a.out).write_text(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
