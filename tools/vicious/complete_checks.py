"""Read-only campaign completion checks; never launches or changes a match."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import time

from panel import hashes
from summarize import collect, summarize
from verify import cpu, parity

ROOT = Path(__file__).resolve().parents[2]
C = Path(json.loads((ROOT / 'tools/vicious/current.json').read_text())['directory'])


def save(path, data):
    (C / path).write_text(json.dumps(data, indent=2) + '\n')


def ready():
    expected = {'release/late_native_valjean': 2,
                'cycle_05/feed_sensitivity': 12,
                'cycle_05/late_specialist': 132,
                'release/late_sandbox': 2}
    return all((C / p / 'results.json').exists() and
               len(json.loads((C / p / 'results.json').read_text())) == n
               for p, n in expected.items())


def matched_summary(panels, reference, control):
    rows = collect([C / p for p in panels])
    keys = {(r['opponent'], r['map'], r['side']) for r in rows}
    controls = [r for r in collect([C / reference]) if r['arm'] == control and
                (r['opponent'], r['map'], r['side']) in keys]
    assert len(controls) == len(keys), (len(controls), len(keys))
    weights = json.loads((C / 'baseline/experiment_data__bot-ratings__latest.json').read_text())['map_weights']
    return summarize(rows + controls, weights, control)


def main():
    save('cycle_05/CARRIER_SENSITIVITY.json', matched_summary(
        ['cycle_05/orchard', 'cycle_05/open'], 'cycle_04/broad', 'vicious-x12-crown-clear'))
    save('cycle_05/FEED_SENSITIVITY.json', matched_summary(
        ['cycle_05/feed_sensitivity'], 'cycle_05/late_specialist', 'vicious-x15-late-time'))
    weights = json.loads((C / 'baseline/experiment_data__bot-ratings__latest.json').read_text())['map_weights']
    save('cycle_05/OPPONENT_HOLDOUT.json', summarize(collect([
        C / 'cycle_04/opponent_reserve', C / 'cycle_05/late_opponent_reserve']),
        weights, 'vicious-v01-frozen'))
    for native, reference, output in [
        ('release/late_native', 'cycle_05/late_specialist', 'release/LATE_NATIVE_PARITY.json'),
        ('release/late_native_valjean', 'cycle_05/late_opponent_reserve', 'release/LATE_VALJEAN_PARITY.json')]:
        refs = {tuple(r[k] for k in ('arm', 'opponent', 'map', 'side')): r
                for r in collect([C / reference])}
        checks = []
        for r in collect([C / native]):
            ref = refs[tuple(r[k] for k in ('arm', 'opponent', 'map', 'side'))]
            checks.append(parity(C / native / 'games' / r['replay'], C / reference / 'games' / ref['replay']))
        save(output, checks)
    checks = []
    for r in collect([C / 'release/late_sandbox']):
        checks.append(dict(arm=r['arm'], opponent=r['opponent'], map=r['map'], side=r['side'],
                           usage=cpu(C / 'release/late_sandbox/games' / r['replay']), faults=r['faults']))
    save('release/LATE_CPU.json', checks)


def audit():
    panels = []
    for manifest in sorted(C.rglob('manifest.json')):
        m = json.loads(manifest.read_text()); folder = manifest.parent
        if not {'arms', 'opponents', 'source_hashes', 'map_hashes'} <= m.keys():
            continue
        issues = []
        for bot, expected in m['source_hashes'].items():
            if hashes(folder / 'sources' / bot) != expected:
                issues.append('source hash mismatch: ' + bot)
        for name, expected in m['map_hashes'].items():
            if hashlib.sha256((folder / 'sources/maps' / (name + '.map')).read_bytes()).hexdigest() != expected:
                issues.append('map hash mismatch: ' + name)
        rows = json.loads((folder / 'results.json').read_text()) if (folder / 'results.json').exists() else []
        keys = [tuple(r[k] for k in ('arm', 'opponent', 'map', 'side')) for r in rows]
        if len(keys) != len(set(keys)):
            issues.append('duplicate fixtures')
        missing = set((a, o, mp, s) for a in m['arms'] for o in m['opponents']
                      for mp in m['maps'] for s in m['seats'] if a != o) - set(keys)
        errors = []
        for r in rows:
            if r['outcome'] == 'error':
                errors.append(r.get('error')); continue
            if not r.get('stats') or r.get('analysis_error'):
                issues.append('missing replay statistics: ' + r['log']); continue
            stats = json.loads((folder / 'games' / r['stats']).read_text())
            if stats['winner'] != r['outcome']:
                issues.append('winner mismatch: ' + r['log'])
            if stats['rounds'] != r['rounds']:
                issues.append('duration mismatch: ' + r['log'])
            if any(r.get('faults', {}).values()):
                issues.append('recorded runtime fault: ' + r['log'])
            # Catch opponent-specific exception markers too; the runner's
            # standard fault table primarily names the MonteCristo lineage.
            for message, count in stats.get('log_samples', {}).items():
                if re.search(r'VJ_ERROR|MC_ERROR|Traceback|ran out of time|timed out', message):
                    issues.append('replay log fault: ' + r['log'] + ':' + message[:120])
        panels.append(dict(panel=str(folder.relative_to(C)), rows=len(rows),
                           reused=sum(bool(r.get('reused_from')) for r in rows),
                           missing=[list(k) for k in sorted(missing)], launch_errors=errors,
                           issues=issues, sandbox=m['sandbox'], accelerated=m.get('fast', False)))
    save('release/INTEGRITY_AUDIT.json', {
        'panels': panels, 'row_count': sum(p['rows'] for p in panels),
        'reused_row_count': sum(p['reused'] for p in panels),
        'interpretation': 'Rows include diagnostic, native parity and judge repeats. Reused rows and repeated deterministic fixtures are not independent playing evidence.',
        'logging_limit': 'Fault checks cover emitted diagnostics and judge timeouts. The frozen Newton control can silently execute its inherited exception fallback with TRACE disabled; absence of reported faults does not prove absence of every internally caught exception.',
        'panels_with_issues': [p['panel'] for p in panels if p['issues']]})
    print('Integrity audit saved.', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--wait', action='store_true')
    ap.add_argument('--audit-only', action='store_true'); args = ap.parse_args()
    if args.wait:
        while not ready():
            time.sleep(10)
    if not ready():
        raise SystemExit('Final panels are not complete yet; use --wait to await their saved results.')
    if not args.audit_only:
        main()
    audit()
