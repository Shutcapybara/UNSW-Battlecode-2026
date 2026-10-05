#!/usr/bin/env python3
"""D-086 §D points-limit burn test (local sandbox, unswbc 1.2.3; no upload).
Copies a bot to build/asahi/burn/<bot>-b<M>/ with one inserted block at the top of the turn loop: on the queen's
(team's starting dragon, id <= 1) 10th turn, spin until the sandbox's virtual monotonic clock (denominated in CPU
points, sandbox.py clock_time_get) has advanced BURN points. Runs one seat-A game per burn level vs --opp on --map,
seed 1, sandbox=True, and records per turn: dragon, reply bytes, metered points, error. Reports:
  (1) per burn level: the burn turn's metered points, whether that dragon died / errored, game result;
  (2) on the control (burn 0): the write cost per turn = 2.5 M + 4,000 x reply bytes (sandbox.py WRITE_* constants,
      one buffered write a turn), its share of p50 / p99 / max turn points, and at the max turn.
    python tools/asahi/burn.py bokuto-18-queenfeed --burns 0,50,95,105 [--map live/default] [--opp yuna-v05-core]
Writes build/asahi/burn/<bot>.json and prints one line per level.
"""
import argparse, json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tools/cx'))
os.chdir(ROOT)

HOOK = '''
        {   // ASAHI-BURN (D-086 §D): burn on the queen's 10th turn
            static int asahi_turn = 0;
            if (++asahi_turn == 10 && ct.get_id() <= 1 && ASAHI_BURN > 0) {
                auto asahi_t0 = std::chrono::steady_clock::now();
                volatile unsigned long long asahi_x = 0;
                while (std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now() - asahi_t0).count() < (long long)ASAHI_BURN) asahi_x = asahi_x + 1;
            }
        }
'''


def make(bot, mpts):
    src = ROOT / 'bots' / bot
    dst = ROOT / 'build/asahi/burn' / f'{bot}-b{mpts}'
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.unswbc-build', '__pycache__', '.asahi-source.json'))
    m = (dst / 'main.cpp').read_text()
    loop = re.search(r'while \(unswbc::update\(ct, game\)\) \{\n', m)
    assert loop, 'turn loop not found'
    m = m[:loop.end()] + HOOK + m[loop.end():]
    m = f'#include <chrono>\n#define ASAHI_BURN {int(mpts * 1_000_000)}LL\n' + m
    (dst / 'main.cpp').write_text(m)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('bot'); ap.add_argument('--burns', default='0,50,95,105')
    ap.add_argument('--map', default='live/default'); ap.add_argument('--opp', default='yuna-v05-core')
    a = ap.parse_args()
    import unswbc.sandbox as S
    from arena import run_game
    log = []
    orig = S.SandboxBot.ask
    fresh = {}
    of = S.SandboxBot._fresh

    def _fresh(self):   # a worker restart (first turn, or a retry after an exit with no output)
        fresh[getattr(self, '_name', '?')] = fresh.get(getattr(self, '_name', '?'), 0) + 1
        return of(self)
    S.SandboxBot._fresh = _fresh

    def ask(self, block):
        out = orig(self, block)
        h = dict(l.split(' ', 1) for l in block.decode(errors='replace').splitlines()[:12] if ' ' in l)
        lv = getattr(self, 'live', None)
        log.append(dict(name=getattr(self, '_name', '?'), fresh=fresh.pop(getattr(self, '_name', '?'), 0), reply=out[:80].decode(errors='replace'), round=int(h.get('ROUND', -1)) if h.get('ROUND', '').isdigit() else -1,
                        bytes=len(out), points=(lv[0] if lv else None), error=self.error))
        return out
    S.SandboxBot.ask = ask
    res = {}
    for b in [int(x) for x in a.burns.split(',')]:
        d = make(a.bot, b)
        log.clear()
        r = run_game(f'maps/{a.map}.map', str(d), f'bots/{a.opp}', seed=1, sandbox=True, record='A')
        teamA = {str(k) for k in (r.get('transcripts') or {})}
        log[:] = [t for t in log if t['name'] in teamA]
        qid = str(min(int(k) for k in teamA))
        errs = [e for e in r.get('errors', []) if e[2] == 'A']
        deaths = [x for x in r.get('deaths', []) if x.get('team') == 'A' and str(x.get('id')) == qid]
        res[b] = dict(dir=str(d.relative_to(ROOT)), winner=r.get('winner'), reason=r.get('end_reason'), rounds=r.get('rounds'),
                      errors_A=[list(map(str, e)) for e in errs], queen_deaths=deaths, turns=list(log),
                      stats_A=r.get('stats', {}).get('A', {}).get('points'))
        q = [t for t in log if t['name'] == qid]
        burn_turn = q[9] if len(q) >= 10 else None
        print('  queen turns 8-12:', q[7:12], flush=True)
        print(f"BURN {b}M: queen turn10 {burn_turn}; queen deaths {deaths}; errors A {errs[:3]}; winner {r.get('winner')} "
              f"{r.get('end_reason')} r{r.get('rounds')}; stats A {res[b]['stats_A']}", flush=True)
    c = res.get(0)
    if c:
        rows = [t for t in c['turns'] if t['points']]
        wc = lambda t: 2_500_000 + 4_000 * t['bytes']
        pts = sorted(t['points'] for t in rows)
        q = lambda p: pts[min(len(pts) - 1, int(p * (len(pts) - 1)))]
        mx = max(rows, key=lambda t: t['points'])
        mb = sorted(t['bytes'] for t in rows)
        print(f"WRITES control: turns {len(rows)} (team A, all dragons) reply bytes p50 {mb[len(mb)//2]} max {mb[-1]}; "
              f"points p50 {q(.5)/1e6:.2f}M p99 {q(.99)/1e6:.2f}M max {mx['points']/1e6:.2f}M; write cost at p50-bytes "
              f"{(2.5e6 + 4000 * mb[len(mb)//2])/1e6:.2f}M; at the max turn {wc(mx)/1e6:.2f}M of {mx['points']/1e6:.2f}M "
              f"({wc(mx)/mx['points']*100:.0f} %)", flush=True)
    p = ROOT / 'build/asahi/burn' / f'{a.bot}.json'
    p.write_text(json.dumps(res, indent=1, default=str))
    print('wrote', p)


if __name__ == '__main__':
    main()
