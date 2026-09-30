"""K-1: gather the per-game JSONs into build/sophie/agg/{deaths,sides,cells}.parquet.

sides: one row per side-game (cohort us / top10 / field / local), counters and rates.
deaths: one row per death with position and context flags.
cells: head-turn exposure per (set, map_hash, cohort, x, y) summed over games (deaths are joined later).
"""
import gzip, json, os, sys
from pathlib import Path
import pandas as pd

REPO = Path(os.environ.get('K1_REPO', Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(REPO))
from tools.analysis.features.compare import ladder_lookup  # noqa: E402

X = REPO / os.environ.get('K1_X', 'build/sophie/x')
OUT = REPO / os.environ.get('K1_AGG', 'build/sophie/agg')
CLASSES = ('wall', 'self', 'ally_body', 'h2h_ally', 'enemy_body', 'h2h_enemy', 'suicide', 'invalid')
CTX = dict(nb='newborn', tr='trapped', po='portal', tx='transit', cr='crowd23', fi='fight')
LOCAL_BOT = 'renoir-00-base'


def map_label(meta):
    m = meta.get('map') or meta.get('map_name')
    if m == 'Prisoners Dilemma' and meta.get('n_initial') == 10:
        return 'Prisoners Dilemma 10'
    return m


def _one_game(sset, o, top_ids, sides, deaths, cells):
    m = o['meta']
    mp = map_label(m)
    local = sset.startswith('local')
    for s in 'AB':
        sd = o['side'][s]
        o_s = 'B' if s == 'A' else 'A'
        if local:
            bot = m.get('bot' + s)
            if bot != LOCAL_BOT:
                continue
            team, opp, cohort = None, m.get('bot' + o_s), 'local'
            panel = m.get('panel')
        else:
            team, opp = m['team_' + s], m['team_' + o_s]
            panel = None
            if sset == 'us' and team != 7:
                continue           # opponents of team 7 are not the field reference (BENCHMARKS convention)
            cohort = 'us' if team == 7 else ('top10' if team in top_ids else 'field')
        dt = sum(map(sum, sd['dt_rb_lb']))
        won = 1.0 if m['winner'] == s else 0.5 if m['winner'] == 'draw' else 0.0
        t5, u5 = sd['total5'], o['side'][o_s]['total5']
        # first-behind: earliest sampled round from which our total stays below theirs through r100 (or the end)
        fb = None
        upto = [i for i in range(len(t5)) if i * 5 <= 100]
        for i in upto:
            if all(t5[j] < u5[j] for j in upto if j >= i):
                fb = i * 5
                break
        row = dict(set=sset, game=str(m['game']), map=mp, map_hash=m['map_hash'], side=s, team=team, opp=opp,
                   cohort=cohort, panel=panel, ranked=m.get('ranked'), sub=m.get('sub_' + s), won=won,
                   reason=m['reason'], rounds=m['last_round'] + 1, dt=dt, dt100=sd['dt100'],
                   total100=t5[20] if len(t5) > 20 else t5[-1], opp_total100=u5[20] if len(u5) > 20 else u5[-1],
                   units100=sd['units5'][20] if len(sd['units5']) > 20 else sd['units5'][-1],
                   first_behind=fb, stationary=sd['stationary'], oscillation=sd['oscillation'],
                   transits=sd['transits'], transit_deaths=sd['transit_deaths'], steps=sd['steps'],
                   moves=sd['moves'], no_action=sd['no_action'], tle=sd['tle'], sonar=sd['sonar'],
                   births=len(sd['splits']), first_split=min(sd['splits']) if sd['splits'] else None,
                   last_split=max(sd['splits']) if sd['splits'] else None,
                   corpse_ally=sd['eat_origin'].get('ally_corpse', 0), eat_bed=sd['eat_origin'].get('bed', 0))
        for c, v in sd['pearls_at'].items():
            row[f'pearls@{c}'] = v
        for c, v in sd['births_at'].items():
            row[f'births@{c}'] = v
        for i in range(4):
            for j in range(4):
                row[f'dt_rb{i}_lb{j}'] = sd['dt_rb_lb'][i][j]
        sides.append(row)
        key_c = (sset if not local else 'local', m['map_hash'], cohort)
        cc = cells.setdefault(key_c, {})
        for x, y, n in sd['head_cells']:
            cc[(x, y)] = cc.get((x, y), 0) + n
        for d in o['deaths']:
            if d['s'] != s:
                continue
            deaths.append(dict(set=sset, game=str(m['game']), map=mp, map_hash=m['map_hash'], side=s,
                               cohort=cohort, team=team, **{k: d[k] for k in ('r', 'id', 'cls', 'L', 'age', 'x', 'y',
                                                                            'reach', 'nb', 'tr', 'po', 'tx', 'cr', 'fi', 'kt')},
                               to=d.get('to'), na=d.get('na'), ns=d.get('ns')))


def do_chunk(job):
    sset, files, stem, top_ids = job
    if (OUT / 'parts' / f'{stem}.done').exists():
        return stem
    sides, deaths, cells = [], [], {}
    for fn in files:
        o = json.load(gzip.open(X / sset / fn, 'rt'))
        _one_game(sset, o, top_ids, sides, deaths, cells)
    P = OUT / 'parts'
    pd.DataFrame(sides).to_parquet(P / f'{stem}.sides.parquet')
    pd.DataFrame(deaths).to_parquet(P / f'{stem}.deaths.parquet')
    pd.DataFrame([dict(set=k[0], map_hash=k[1], cohort=k[2], x=c[0], y=c[1], expo=n)
                  for k, cc in cells.items() for c, n in cc.items()]).to_parquet(P / f'{stem}.cells.parquet')
    (P / f'{stem}.done').touch()
    return stem


def main():
    import multiprocessing as mp, time
    t0 = time.time()
    (OUT / 'parts').mkdir(parents=True, exist_ok=True)
    _, latest = ladder_lookup(str(REPO / 'public_replays/corpus/ladder'))
    top_ids = [int(t) for t, v in sorted(latest.items(), key=lambda kv: kv[1][1]) if t != 7][:10]
    json.dump(top_ids, open(OUT / 'top_ids.json', 'w'))
    jobs = []
    for sset in sorted(os.listdir(X)):
        fs = sorted(f for f in os.listdir(X / sset) if f.endswith('.json.gz'))
        for k in range(0, len(fs), 150):
            jobs.append((sset, fs[k:k + 150], f'{sset}-{k:05d}', top_ids))
    with mp.get_context('fork').Pool(4) as pool:
        for stem in pool.imap_unordered(do_chunk, jobs):
            if time.time() - t0 > float(os.environ.get('K1_BUDGET', 160)):
                pool.terminate()
                print('budget hit; rerun to continue')
                return
    P = OUT / 'parts'
    for kind in ('sides', 'deaths', 'cells'):
        df = pd.concat([pd.read_parquet(p) for p in sorted(P.glob(f'*.{kind}.parquet'))], ignore_index=True)
        if kind == 'cells':
            df = df.groupby(['set', 'map_hash', 'cohort', 'x', 'y'], as_index=False)['expo'].sum()
        for c in ('team', 'opp', 'sub', 'panel', 'kt'):
            if c in df:
                df[c] = df[c].map(lambda v: None if v is None or v != v else str(v))
        df.to_parquet(OUT / f'{kind}.parquet')
        print(kind, len(df))
    S = pd.read_parquet(OUT / 'sides.parquet')
    print(S.groupby(['set', 'cohort']).size())


if __name__ == '__main__':
    main()
