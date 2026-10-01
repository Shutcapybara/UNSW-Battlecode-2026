"""Read existing post-era corpus replays; publish provisional references, never mutate S-1.

Run with the repository venv (numpy/pandas), --repo pointing to this worktree.
Raw features are F1's, outcomes come from the authoritative replay result.
Q3 counts include the checkpoint's events, matching S-1's convention.
"""
import argparse
import collections
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd

CHECKS = (25, 50, 100, 150, 250)
ERA_START = '2026-10-01T06:00:00Z'  # Antioch's observed gap; not a deployment timestamp.
REPO = None


def init(repo):
    global REPO
    REPO = Path(repo)
    sys.path.insert(0, str(REPO))


def transit_counts(g):
    """Same commanded-path portal count as S-1 extras, not realized safe transits."""
    ans = collections.Counter()
    for a in g['events']['actions']:
        r, ident, team = a['round'], a['id'], a['team']
        if a['kind'] != 'move' or not a.get('dirs') or r < 0:
            continue
        b = g['rounds'][r].get(ident)
        if b is None:
            continue
        cur = b[1][0]
        for d in a['dirs']:
            nxt = g['nbr'][cur][d] if d < 4 else None
            if nxt is None:
                break
            normal = ((cur[0] + (0, 1, 0, -1)[d]) % g['W'],
                      (cur[1] + (-1, 0, 1, 0)[d]) % g['H'])
            if nxt != normal:
                ans[team, r] += 1
            cur = nxt
    return ans


def one(task):
    meta, corpus = task
    from tools.analysis.features.frame import decode
    from tools.analysis.features.extract import extract
    from tools.antioch.era import header
    path = Path(corpus) / 'replays' / f"{meta['game_id']}.replay"
    try:
        h = header(path)
        g = decode(path)
        old_winner = g['winner']
        g['winner'] = h['res_winner']
        g['reason'] = 'elimination' if h['res_reason'] == 0 else next(
            (k for k in ('queen', 'longest', 'total') if h[k+'_a'] != h[k+'_b']), 'tie')
        ex = extract(g)
        tr = transit_counts(g)
        out = []
        for f in ex['side_rows']:
            s = f['side']; o = 'B' if s == 'A' else 'A'
            q = min(i for i, (t, b) in g['rounds'][0].items() if t == s)
            series = [x for x in ex['series'] if x['side'] == s]
            f.update(team=str(meta['team_a' if s == 'A' else 'team_b']),
                     opp=str(meta['team_b' if s == 'A' else 'team_a']),
                     started_at=meta['started_at'], series_id=meta.get('series_id'),
                     ranked=meta['ranked'], era='post', last_round=g['last_round'],
                     official_winner=h['res_winner'], old_decoder_disagrees=old_winner != h['res_winner'],
                     round_limit=h['res_reason'] == 1, queen_id=q)
            for c in CHECKS:
                cum = lambda key: sum(x.get(key, 0) for x in series if x['round'] <= c)
                f[f'bed_capture@{c}'] = cum('eats_bed')/cum('bed_spawns') if cum('bed_spawns') else None
                f[f'bed_eats@{c}'] = cum('eats_bed')
                f[f'splits@{c}'] = cum('splits')
                f[f'transits@{c}'] = sum(n for (t, r), n in tr.items() if t == s and r <= c)
                sample = max((x for x in ex['samples'] if x['side'] == s and x['round'] <= c), key=lambda x:x['round'])
                f[f'territory@{c}'] = sample['territory']
            reached = g['last_round'] >= 490
            snap = g['rounds'][490] if reached else {}
            own = {i:len(b) for i,(t,b) in snap.items() if t == s}
            f.update(reached490=reached, queen_alive490=int(q in snap) if reached else None,
                     queen_length490=own.get(q, 0) if reached else None,
                     longest490=max(own.values(), default=0) if reached else None,
                     total490=sum(own.values()) if reached else None,
                     queen_alive_end=int(q in g['rounds'][-1]),
                     queen_length_end=h['queen_'+s.lower()], total_end=h['total_'+s.lower()],
                     opp_total_end=h['total_'+o.lower()],
                     queen_field_matches=(len(g['rounds'][-1][q][1]) if q in g['rounds'][-1] else 0)==h['queen_'+s.lower()])
            qdeath = next((d for d in g['events']['deaths'] if d['id'] == q), None)
            f['queen_death_round'] = qdeath['round'] if qdeath else None
            f['queen_ally_corpse_eats300'] = sum(e['id']==q and e['round']>=300 and e['origin']=='ally_corpse' for e in g['events']['eats'])
            qa = [a for a in g['events']['actions'] if a['id']==q and a['round']>=300 and a['kind']=='move']
            f['queen_commanded_steps300'] = sum(a['steps'] for a in qa)
            moves = [a for a in g['events']['actions'] if a['team']==s and a['kind']=='move']
            sprintkeys = {(a['round'],a['id']) for a in moves if a['steps']>1}
            f['sprint_commands'] = len(sprintkeys)
            f['move_commands'] = len(moves)
            f['commanded_steps'] = sum(a['steps'] for a in moves)
            f['deaths_on_sprint_round'] = sum((d['round'],d['id']) in sprintkeys for d in g['events']['deaths'] if d['team']==s)
            # Context, not a causal classification of death by sprint cost.
            f['avoidable_deaths_per1k'] = sum(f.get(k, 0) for k in (
                'death_wall_per1k','death_self_per1k','death_ally_body_per1k','death_h2h_ally_per1k','death_invalid_per1k'))
            out.append(f)
        return out
    except Exception as e:
        return [dict(game=str(meta['game_id']), error=f'{type(e).__name__}: {e}')]


def percentile(x, value, direction):
    if not len(x) or not math.isfinite(value): return None
    p = float(((x < value).sum() + .5*(x == value).sum())/len(x))
    return p if direction == 'up' else 1-p


def summarize(df, out):
    from tools.analysis.features.benchmarks import FIELD_REL
    metrics = dict(FIELD_REL)
    metrics.update({f'{k}@{c}':'up' for c in CHECKS for k in ('bed_eats','bed_capture','splits','transits','territory')})
    metrics.update({k:'up' for k in ('queen_alive490','queen_length490','longest490','total490')})
    refs = []
    for m, d in df.groupby('map'):
        for metric, direction in metrics.items():
            if metric not in d: continue
            x = pd.to_numeric(d[metric], errors='coerce').dropna().to_numpy(float)
            top = pd.to_numeric(d.loc[d.top10,metric],errors='coerce').dropna().to_numpy(float)
            us = pd.to_numeric(d.loc[d.team=='7',metric],errors='coerce').dropna().to_numpy(float)
            med = float(np.median(top)) if len(top) else float('nan')
            umed = float(np.median(us)) if len(us) else float('nan')
            refs.append(dict(map=m, metric=metric, direction=direction, era='post', field_sides=len(x),
                sampled_games=d.game.nunique(), top10_sides=len(top), top10_teams=d.loc[d.top10,'team'].nunique(),
                us_sides=len(us), field_median=float(np.median(x)) if len(x) else None,
                field_p10=float(np.quantile(x,.1)) if len(x) else None, field_p90=float(np.quantile(x,.9)) if len(x) else None,
                top10_median=med, top10_field_pct=percentile(x,med,direction), us_median=umed,
                us_field_pct=percentile(x,umed,direction), top10_minus_us=med-umed,
                reference_status='provisional; no gate use'))
    pd.DataFrame(refs).to_csv(out/'references.csv',index=False)
    # Publish the full empirical distributions separately; no pre-era normalizers used.
    pd.DataFrame(refs).to_json(out/'references.json',orient='records',indent=2)
    end=[]
    for m, d in [('ALL', df)]+list(df.groupby('map')):
        for label, dd in [('field',d),('top10',d[d.top10]),('us',d[d.team=='7'])]:
            rl=dd[dd.round_limit]; reach=dd[dd.reached490]
            loss=rl[rl.won==0]; lead=rl[rl.total_end>rl.opp_total_end]
            end.append(dict(map=m,cohort=label,n=len(dd),reached490=len(reach),round_limit=len(rl),
                queen_alive490=reach.queen_alive490.mean(),queen_length490_mean=reach.queen_length490.mean(),
                queen_length490_median=reach.queen_length490.median(),rl_win=rl.won.mean(),
                rl_losses=len(loss),rl_leads=len(lead),
                lead_given_rl_loss=(loss.total_end>loss.opp_total_end).mean(),
                loss_given_rl_lead=(lead.won==0).mean()))
    pd.DataFrame(end).to_csv(out/'endgame.csv',index=False)


def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--corpus',required=True)
    p.add_argument('--out',required=True);p.add_argument('--per-map',type=int,default=40);p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--manifest',help='Reuse the exact selected game IDs and cohort snapshot from an earlier run')
    a=p.parse_args();init(a.repo);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    raw=(Path(a.corpus)/'index.jsonl').read_bytes()
    idx={g['game_id']:g for g in map(json.loads,raw.splitlines()) if g.get('started_at')}
    ladders=sorted((Path(a.corpus)/'ladder').glob('*.json'));ladder=ladders[-1]
    teams=sorted((t for t in json.loads(ladder.read_text()) if not t.get('dev')),key=lambda t:t['rank'])
    top={str(t['id']) for t in teams[:10]}
    decoy={t['id'] for t in teams if t['id'] in (91,306) or t['name']=='STAR'}
    post=[g for g in idx.values() if g['started_at']>=ERA_START]
    eligible=[g for g in post if g['ranked'] or not ({g['team_a'],g['team_b']} & decoy)]
    groups=collections.defaultdict(list)
    for g in eligible:groups[g['map_name']].append(g)
    selected=[]
    for m, rows in sorted(groups.items()):
        selected.extend(sorted(rows,key=lambda g:hashlib.sha256(f"himeji-unit1-v1:{g['game_id']}".encode()).hexdigest())[:a.per_map])
    manifest=dict(index_sha256=hashlib.sha256(raw).hexdigest(), index_unique=len(idx),post_index=len(post),
        latest_start=max(g['started_at'] for g in post),era_threshold=ERA_START,ladder=ladder.name,
        top10=[dict(id=t['id'],name=t['name']) for t in teams[:10]],excluded_unranked_decoy_ids=sorted(decoy),
        eligible_games=len(eligible), post_us_games=sum(7 in (g['team_a'],g['team_b']) for g in post),
        sample_games=len(selected),per_map=a.per_map,sample_ids=[g['game_id'] for g in selected],
        available_by_map=dict(collections.Counter(g['map_name'] for g in post)))
    if a.manifest:
        manifest=json.loads(Path(a.manifest).read_text())
        selected=[idx[i] for i in manifest['sample_ids']]
        top={str(t['id']) for t in manifest['top10']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    done={}
    if (out/'sides.jsonl').exists():
        for line in (out/'sides.jsonl').read_text().splitlines():
            r=json.loads(line)
            if 'error' not in r:done.setdefault(str(r['game']),[]).append(r)
    tasks=[(g,a.corpus) for g in selected if str(g['game_id']) not in done]
    with (out/'sides.jsonl').open('a') as f, concurrent.futures.ProcessPoolExecutor(a.jobs,initializer=init,initargs=(a.repo,)) as pool:
        for n, rows in enumerate(pool.map(one,tasks,chunksize=1),1):
            for r in rows:f.write(json.dumps(r,default=float)+'\n')
            f.flush()
            if n%20==0:print(f'decoded {n}/{len(tasks)} games',flush=True)
    rows=[json.loads(l) for l in (out/'sides.jsonl').read_text().splitlines()]
    errors=[r for r in rows if 'error' in r]
    (out/'errors.json').write_text(json.dumps(errors,indent=2))
    wanted={str(g['game_id']) for g in selected}
    df=pd.DataFrame([r for r in rows if 'error' not in r and str(r['game']) in wanted])
    df['team']=df.team.astype(str);df['top10']=df.team.isin(top)
    assert not df.duplicated(['game','side']).any()
    assert (df.groupby('game').size()==2).all()
    assert np.allclose(df.groupby('game').won.sum(),1)
    assert df.queen_field_matches.all()
    summarize(df,out)
    print(json.dumps(dict(games=df.game.nunique(),side_rows=len(df),errors=len(errors),field_win=df.won.mean(),
        old_decoder_disagreement_games=df.loc[df.old_decoder_disagrees,'game'].nunique(),
        top10_sides=int(df.top10.sum()),top10_teams=df.loc[df.top10,'team'].nunique())),flush=True)


if __name__=='__main__':main()
