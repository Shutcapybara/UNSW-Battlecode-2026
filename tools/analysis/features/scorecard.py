"""Single-bot scorecard: panel -> features -> fixed references -> the two
BENCHMARKS tables + W-L-D + gate, in one command (R-4 Part 3).

    python -m tools.analysis.features.scorecard bots/<candidate> [--parent bots/<parent>]
        [--panel z1|gen|both] [--seed 1,2] [--jobs N] [--atlas on|off] [--sandbox] [--replay-only]

Runs (or reuses) the candidate's fixture grid from run_panel — 8 ZOO opponents
x panel maps x both seats per seed, under build/zoo/<panel>-<bot>-<fp8>/ keyed
by the runtime-source fingerprint, so a replay set is reused only while the
sources are untouched — then extracts features, scores them against the fixed
field references in docs/analysis/benchmarks/, and prints the two tables of the
Ares V06 finding (tier-1 with parent deltas, tier-2 with % change), the panel
W-L-D, the generalisation block (--panel gen|both: no field reference exists
there, so tier-1 is raw with parent deltas and the |map columns are marked
unavailable), the CPU probe block (only with --sandbox) and the gate line.

GATE applies BENCHMARKS "How to use it" step 4 literally:
  pass  economy mean +>= 0.05 of field median with dragons and length at r100
        not falling, no tier-2 rate up > 10 %, panel win rate not down;
  hold  neither: hygiene holding or up with the economy short of the bar;
  fail  economy mean down, or any tier-2 rate up > 10 %, or panel win rate down.

Writes game_stats/runs/<candidate>-<panel>-s<seed>.json and .md.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

from .benchmarks import apply_field_rel, derive
from .run_panel import GEN_MAPS, LIVE_MAPS, fixtures, runtime_fingerprint

REFDIR = pathlib.Path('docs/analysis/benchmarks')
CHECKPOINTS = ('pearls@50', 'pearls@100', 'pearls@150', 'pearls@250')
TIER1 = [('units@100|map', 'Dragons at r100, normalized'),
         ('total@100|map', 'Total length at r100, normalized'),
         ('births@100|map', 'Births by r100, normalized')]
TIER1_RAW = ([('pearls@50', 'Pearls at r50'), ('pearls@100', 'Pearls at r100'),
              ('pearls@150', 'Pearls at r150'), ('pearls@250', 'Pearls at r250')]
             + [('units@100', 'Dragons at r100'), ('total@100', 'Total length at r100'),
                ('births@100', 'Births by r100')])
TIER2 = [('death_wall_per1k', 'Wall'), ('death_self_per1k', 'Own body'),
         ('death_ally_body_per1k', 'Ally body'), ('death_h2h_ally_per1k', 'Ally head-on'),
         ('death_invalid_per1k', 'Invalid action')]


def unswbc_bin() -> str:
    guess = pathlib.Path(sys.executable).parent / 'unswbc'
    return str(guess) if guess.is_file() else 'unswbc'


def panel_root(panel: str, bot_dir: str) -> pathlib.Path:
    fp8 = runtime_fingerprint(bot_dir)[:8]
    return pathlib.Path('build/zoo') / f'{panel}-{pathlib.Path(bot_dir).name}-{fp8}'


def atlas_variant(bot_dir: str) -> str:
    """Copy the bot under build/ with ATLAS_ENABLED flipped to false. The
    measured snapshot is never edited; the variant carries its own fingerprint,
    so its panel dir is its own."""
    src = pathlib.Path(bot_dir)
    dst = pathlib.Path('build/cx/atlas-off') / src.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__'))
    hits = 0
    for p in sorted(dst.rglob('*.hpp')):
        txt = p.read_text()
        new, n = re.subn(r'ATLAS_ENABLED\s*=\s*true', 'ATLAS_ENABLED = false', txt)
        if n:
            p.write_text(new)
            hits += n
    if hits != 1:
        raise SystemExit(f'--atlas off: expected exactly one ATLAS_ENABLED = true in {src}, found {hits}')
    return str(dst)


def ensure_panel(panel: str, bot_dir: str, seeds: tuple[int, ...], jobs: int) -> pathlib.Path:
    root = panel_root(panel, bot_dir)
    fx = fixtures(panel, bot_dir, seeds)
    missing = [f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()]
    if missing:
        cmd = [sys.executable, '-m', 'tools.analysis.features.run_panel', '--panel', panel,
               '--bot', bot_dir, '--seed', ','.join(str(s) for s in seeds), '--jobs', str(jobs),
               '--unswbc', unswbc_bin(), '--no-logs', '--out', str(root)]
        print(f'running {len(missing)}/{len(fx)} {panel} fixtures for {pathlib.Path(bot_dir).name} '
              f'-> {root}', flush=True)
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            raise SystemExit(f'panel run failed (rc={rc}); see the run_panel output above')
    still = [f for f in fx if not (root / 'replays' / (f['game'] + '.replay')).exists()]
    if still:
        raise SystemExit(f'{len(still)} {panel} fixtures still missing for {bot_dir} '
                         f'(first: {still[0]["game"]}); fix the runner state before scoring')
    return root


def extract_features(root: pathlib.Path, jobs: int) -> pd.DataFrame:
    out = root / 'features'
    cmd = [sys.executable, '-m', 'tools.analysis.features', 'extract', str(root / 'replays'),
           '--index', str(root / 'index.jsonl'), '--out', str(out), '--cache', str(root / 'frames'),
           '--jobs', str(jobs)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'feature extraction failed: {r.stderr[-2000:]}')
    return pd.read_parquet(out / 'features.parquet')


def load_refs():
    med = json.load(open(REFDIR / 'map_reference_medians.json'))
    fr = json.load(open(REFDIR / 'field_references.json'))
    dist = json.load(open(REFDIR / 'field_distributions.json'))
    refs = {}
    for c, per_map in fr.items():
        refs[c] = {}
        for m, v in per_map.items():
            v = dict(v)
            s = dist.get(c, {}).get(m)
            if s is not None:
                v['sorted'] = np.asarray(s, dtype=float)
            refs[c][m] = v
    return med, refs


def score(rows: pd.DataFrame, med, refs) -> dict:
    H = apply_field_rel(derive(rows, med), refs)
    have_ref = H['map'].isin(med.get('pearls@100', {}))
    cp = {c: float(H[f'{c}|map'].median()) for c in CHECKPOINTS}
    return {
        'n': int(len(H)),
        'wld': [int((H['result'] == k).sum()) for k in ('win', 'loss', 'draw')],
        'exp_share': float(H['won'].mean()),
        'checkpoints': cp,
        'checkpoints_raw': {c: float(H[c].median()) for c in CHECKPOINTS},
        'economy_mean': float(np.mean(list(cp.values()))),
        'tier1': {k: float(H[k].median()) for k, _ in TIER1},
        'tier1_raw': {k: float(H[k].median()) for k, _ in TIER1_RAW},
        'tier2': {k: float(H[k].median()) for k, _ in TIER2},
        'unreferenced_maps': sorted(set(H.loc[~have_ref, 'map'])),
    }


def fmt(x, nd=3):
    return '—' if x is None or (isinstance(x, float) and np.isnan(x)) else f'{x:.{nd}f}'

def fmt_delta(p, c, nd=3):
    if p is None or c is None or np.isnan(p) or np.isnan(c):
        return '— (no reference)'
    return f'{c - p:+.{nd}f}'


def wld_s(s):
    w, l, d = s['wld']
    return f'{w}–{l}–{d}'


def tier1_rows(cs, ps):
    rows = []
    if ps:
        pg, cg = ps['exp_share'] * 100, cs['exp_share'] * 100
        rows.append(('Wins–losses–draws', wld_s(ps), wld_s(cs),
                     f'{cs["exp_share"] * cs["n"] - ps["exp_share"] * ps["n"]:+.1f} expected-score points'))
        rows.append(('Expected-score share', f'{pg:.2f}%', f'{cg:.2f}%', f'{cg - pg:+.2f} percentage points'))
        rows.append(('Mean of normalized pearl checkpoints', fmt(ps['economy_mean'], 4),
                     fmt(cs['economy_mean'], 4), fmt_delta(ps['economy_mean'], cs['economy_mean'], 4)))
    else:
        rows.append(('Wins–losses–draws', '—', wld_s(cs), ''))
        rows.append(('Expected-score share', '—', f'{cs["exp_share"] * 100:.2f}%', ''))
        rows.append(('Mean of normalized pearl checkpoints', '—', fmt(cs['economy_mean'], 4), ''))
    for c in CHECKPOINTS:
        r = c.split('@')[1]
        lab = f'Pearls at r{r}, normalized'
        rows.append((lab, fmt(ps['checkpoints'][c]) if ps else '—', fmt(cs['checkpoints'][c]),
                     fmt_delta(ps['checkpoints'][c], cs['checkpoints'][c]) if ps else ''))
    for k, lab in TIER1:
        rows.append((lab, fmt(ps['tier1'][k]) if ps else '—', fmt(cs['tier1'][k]),
                     fmt_delta(ps['tier1'][k], cs['tier1'][k]) if ps else ''))
    return rows


def tier2_rows(cs, ps):
    rows = []
    for k, lab in TIER2:
        c, p = cs['tier2'][k], ps['tier2'][k] if ps else None
        if p is None:
            rows.append((lab, '—', f'{c:.3f}', ''))
        elif p == 0 and c == 0:
            rows.append((lab, f'{p:.3f}', f'{c:.3f}', 'unchanged'))
        elif p == 0:
            rows.append((lab, f'{p:.3f}', f'{c:.3f}', f'+{c:.3f} from zero'))
        else:
            rows.append((lab, f'{p:.3f}', f'{c:.3f}', f'{100 * (c - p) / p:+.1f}%'))
    return rows


def raw_rows(cs, ps):
    rows = []
    for k, lab in TIER1_RAW:
        c, p = cs['tier1_raw'][k], ps['tier1_raw'][k] if ps else None
        rows.append((lab, fmt(p, 1) if ps else '—', fmt(c, 1), f'{c - p:+.1f}' if ps else ''))
    return rows


def md_table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    out += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
    return '\n'.join(out)


def gate_line(cs, ps) -> tuple[str, str]:
    if not ps:
        return 'n/a', 'no parent given: absolute numbers only (the V04-style report)'
    de = cs['economy_mean'] - ps['economy_mean']
    dd = cs['tier1']['units@100|map'] - ps['tier1']['units@100|map']
    dl = cs['tier1']['total@100|map'] - ps['tier1']['total@100|map']
    dw = cs['exp_share'] - ps['exp_share']
    rises = []
    for k, lab in TIER2:
        c, p = cs['tier2'][k], ps['tier2'][k]
        if p == 0:
            if c > 0:
                rises.append(f'{lab} 0.00->{c:.2f}/1k (from zero)')
        elif (c - p) / p > 0.10:
            rises.append(f'{lab} {p:.2f}->{c:.2f}/1k (+{100 * (c - p) / p:.0f}%)')
    why = (f'economy mean {de:+.4f}, dragons {dd:+.3f}, length {dl:+.3f}, win share {100 * dw:+.2f}pp, '
           f'tier-2: {"; ".join(rises) if rises else "none up >10%"}')
    if de < 0 or dw < 0 or rises:
        return 'fail', why
    if de >= 0.05 and dd >= 0 and dl >= 0:
        return 'pass', why
    return 'hold', why


def probe_cpu(bot_dir: str, jobs: int, opp='bots/yuna-v05-core') -> dict | None:
    outp = pathlib.Path('build/cx') / f'{pathlib.Path(bot_dir).name}-probe.jsonl'
    cmd = [sys.executable, 'tools/cx/bench.py', bot_dir, opp, '--maps', 'probe', '--seeds', '1',
           '--sandbox', '--jobs', str(min(jobs, 4)), '--out', str(outp)]
    print(f'running the 4-fixture sandbox CPU probe vs {pathlib.Path(opp).name}', flush=True)
    rc = subprocess.run(cmd).returncode
    if rc != 0:
        print(f'probe failed (rc={rc}); CPU block omitted')
        return None
    rows = [json.loads(l) for l in outp.read_text().splitlines() if l.strip()]
    pts = [r['us']['points'] for r in rows if 'points' in r['us']]
    boots = [r['us']['boot']['max'] for r in rows if 'boot' in r['us']]
    errs = sum(len(r['errors']) for r in rows)
    return {'n_games': len(rows), 'opponent': pathlib.Path(opp).name,
            'p50_max_of_games': max(p['p50'] for p in pts), 'p99_max': max(p['p99'] for p in pts),
            'max': max(p['max'] for p in pts), 'boot_max': max(boots) if boots else None,
            'bot_errors': errs}


def run_one(bot_dir: str, panel: str, seeds, jobs, med, refs) -> dict:
    root = ensure_panel(panel, bot_dir, seeds, jobs)
    F = extract_features(root, jobs)
    name = pathlib.Path(bot_dir).name
    want = tuple(f's{s}__' for s in seeds)
    rows = F[(F['bot'] == name) & F['game'].str.startswith(want)].copy()
    if not len(rows):
        raise SystemExit(f'no side-rows for bot {name} in the extracted features')
    return score(rows, med, refs)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='tools.analysis.features.scorecard')
    ap.add_argument('bot')
    ap.add_argument('--parent')
    ap.add_argument('--panel', default='z1', choices=['z1', 'gen', 'both'])
    ap.add_argument('--seed', default='1')
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument('--atlas', default='on', choices=['on', 'off'],
                    help='off: play a build/cx/atlas-off copy with ATLAS_ENABLED=false '
                         '(the measured snapshot is never edited)')
    ap.add_argument('--sandbox', action='store_true', help='also run the 4-fixture sandbox CPU probe')
    ap.add_argument('--probe-opp', default='bots/yuna-v05-core')
    ap.add_argument('--replay-only', action='store_true',
                    help='reuse existing panel replays; fail if any are missing')
    a = ap.parse_args(argv)
    seeds = tuple(int(s) for s in a.seed.split(','))

    bot = a.bot
    note = ''
    if a.atlas == 'off':
        bot = atlas_variant(bot)
        note = f' (atlas off: build-variant of {a.bot})'
    cand_name = pathlib.Path(bot).name
    parent_name = pathlib.Path(a.parent).name if a.parent else None

    med, refs = load_refs()
    panels = ['z1', 'gen'] if a.panel == 'both' else [a.panel]

    if a.replay_only:
        for p in panels:
            root = panel_root(p, bot)
            miss = [f for f in fixtures(p, bot, seeds)
                    if not (root / 'replays' / (f['game'] + '.replay')).exists()]
            if miss:
                raise SystemExit(f'--replay-only: {len(miss)} {p} fixtures missing for {bot}')

    report = {'candidate': cand_name, 'candidate_dir': bot, 'parent': parent_name,
              'note': note.strip(), 'seeds': list(seeds),
              'fingerprint': runtime_fingerprint(bot), 'panels': {}}
    md = [f'## Scorecard: {cand_name}{note}'
          + (f' (parent {parent_name})' if parent_name else '')
          + f' — {"+".join(panels)} panel, seed {"+".join(str(s) for s in seeds)}']

    for panel in panels:
        C = run_one(bot, panel, seeds, a.jobs, med, refs)
        P = run_one(a.parent, panel, seeds, a.jobs, med, refs) if a.parent else None
        v, why = gate_line(C, P)
        report['panels'][panel] = {'candidate': C, 'parent': P, 'gate': {'verdict': v, 'why': why}}
        md.append(f'\n### {panel} panel: W–L–D {wld_s(C)} over {C["n"]} side-games '
                  f'({len(LIVE_MAPS) if panel == "z1" else len(GEN_MAPS)} maps, '
                  f'expected-score share {C["exp_share"] * 100:.2f}%)\n')
        md.append(md_table(['Metric', parent_name or '—', cand_name, 'Change'], tier1_rows(C, P)))
        md.append('\nTier-2 death rates are per 1,000 dragon-turns:\n')
        md.append(md_table(['Rate', parent_name or '—', cand_name, 'Change'], tier2_rows(C, P)))
        if panel == 'gen':
            md.append('\nNo field reference exists for the gen maps, so the `|map` columns are '
                      'unavailable — tier-1 raw medians against the parent on the same maps '
                      '(BENCHMARKS §guardrails):\n')
            md.append(md_table(['Metric (raw)', parent_name or '—', cand_name, 'Change'], raw_rows(C, P)))

    deciding = 'z1' if 'z1' in panels else panels[0]
    if deciding == 'gen':
        report['panels']['gen']['gate'] = {
            'verdict': 'n/a', 'why': 'no field reference on gen maps: the gate is decided on the '
            'z1 panel; the gen block is reported beside it (raw vs parent per guardrails)'}
    report['gate'] = report['panels'][deciding]['gate']

    if a.sandbox:
        probe = probe_cpu(bot, a.jobs, a.probe_opp)
        if probe:
            report['cpu_probe'] = probe
            md.append(f'\n### CPU probe ({probe["n_games"]} sandbox fixtures, vs {probe["opponent"]}, seed 1)\n')
            md.append(md_table(['p50 max-of-games', 'p99 max', 'max', 'boot max', 'bot errors'],
                               [[f'{probe["p50_max_of_games"] / 1e6:.1f}M', f'{probe["p99_max"] / 1e6:.1f}M',
                                 f'{probe["max"] / 1e6:.1f}M',
                                 f'{probe["boot_max"] / 1e6:.1f}M' if probe['boot_max'] else '—',
                                 probe['bot_errors']]]))

    gv = report['gate']
    md.append(f'\n**GATE ({deciding} panel): {gv["verdict"]}** — {gv["why"]}')
    text = '\n'.join(md)
    print(text)

    seed_s = '-'.join(str(s) for s in seeds)
    for panel in panels:
        payload = {k: v for k, v in report.items() if k != 'panels'}
        payload['panel'] = panel
        payload['candidate_stats'] = report['panels'][panel]['candidate']
        payload['parent_stats'] = report['panels'][panel]['parent']
        pathlib.Path(f'game_stats/runs/{cand_name}-{panel}-s{seed_s}.json').write_text(
            json.dumps(payload, indent=1))
    pathlib.Path(f'game_stats/runs/{cand_name}-{"+".join(panels)}-s{seed_s}.md').write_text(text + '\n')
    print(f'\nwrote game_stats/runs/{cand_name}-<{ "+".join(panels) }>-s{seed_s}.json/.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
