#!/usr/bin/env python3
"""Export map-level tournament results and common-opponent correlations."""
import argparse
import csv
from datetime import datetime, timezone
import html
import io
import json
from pathlib import Path
import sqlite3
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def atomic(path, text):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(text)
    tmp.replace(path)


def table(path, header, rows):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(header)
    writer.writerows(rows)
    atomic(path, stream.getvalue())


def correlations(profiles, minimum=30):
    """Self-opponent entries are NaN: each pair uses common third parties only."""
    n = len(profiles)
    result, counts = np.full((n, n), np.nan), np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i, n):
            x, y = profiles[i].ravel(), profiles[j].ravel()
            mask = np.isfinite(x) & np.isfinite(y)
            counts[i, j] = counts[j, i] = mask.sum()
            if mask.sum() < minimum:
                continue
            x, y = x[mask], y[mask]
            x, y = x - x.mean(), y - y.mean()
            norm = np.sqrt(np.dot(x, x) * np.dot(y, y))
            if norm > 0:
                result[i, j] = result[j, i] = np.clip(np.dot(x, y) / norm, -1, 1)
    return result, counts


def cluster_order(corr):
    """Average linkage; missing correlations use distance 1 for ordering only."""
    distance = 1 - np.nan_to_num(corr, nan=0)
    clusters = [[i] for i in range(len(corr))]
    while len(clusters) > 1:
        _, a, b = min((float(distance[np.ix_(x, y)].mean()), i, j)
                      for i, x in enumerate(clusters) for j, y in enumerate(clusters) if j > i)
        x, y = clusters[a], clusters[b]
        # Orient adjacent ends for a more legible dendrogram leaf order.
        _, x, y = min((distance[u[-1], v[0]], u, v)
                      for u in (x, x[::-1]) for v in (y, y[::-1]))
        clusters[a] = x + y
        del clusters[b]
    return clusters[0]


def color(value):
    if not np.isfinite(value):
        return (219, 221, 224)
    white = np.array([248, 247, 243])
    end = np.array([28, 110, 164] if value >= 0 else [185, 58, 61])
    return tuple((white * (1 - abs(value)) + end * abs(value)).astype(int))


def heatmap(path, names, corr, order, caption):
    cell, left, top = 21, 415, 480
    size = len(names) * cell
    picture = Image.new('RGB', (left + size + 40, top + size + 90), 'white')
    draw = ImageDraw.Draw(picture)
    font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
    font = ImageFont.truetype(font_path, 15)
    title = ImageFont.truetype(font_path, 25)
    draw.text((20, 15), 'Bot performance correlation — common opponents × maps', fill='black', font=title)
    draw.text((20, 55), caption, fill='black', font=font)
    for a, i in enumerate(order):
        draw.text((left - 8, top + a * cell + 2), names[i], fill='black', font=font, anchor='ra')
        label = Image.new('RGBA', (390, 21), (255, 255, 255, 0))
        ImageDraw.Draw(label).text((0, 0), names[i], fill='black', font=font)
        label = label.rotate(90, expand=True)
        picture.paste(label, (left + a * cell, top - 398), label)
        for b, j in enumerate(order):
            draw.rectangle((left + b * cell, top + a * cell,
                            left + (b + 1) * cell - 1, top + (a + 1) * cell - 1), fill=color(corr[i, j]))
    for k in range(401):
        draw.line((left + k, top + size + 25, left + k, top + size + 43), fill=color(k / 200 - 1))
    draw.text((left, top + size + 48), '−1: opposite', fill='black', font=font)
    draw.text((left + 175, top + size + 48), '0', fill='black', font=font)
    draw.text((left + 315, top + size + 48), '+1: similar', fill='black', font=font)
    draw.text((left + 480, top + size + 30), 'Grey: undefined / insufficient shared results', fill='black', font=font)
    temp = path.with_suffix('.tmp.png')
    picture.save(temp)
    temp.replace(path)


def generate(out):
    manifest = json.loads((out / 'manifest.json').read_text())
    names, maps = manifest['bots'], manifest['maps']
    lookup, boards = {s: i for i, s in enumerate(names)}, {s: i for i, s in enumerate(maps)}
    with sqlite3.connect('file:' + str(out / 'games.sqlite3') + '?mode=ro', uri=True) as db:
        records = [json.loads(row[0]) for row in db.execute('SELECT data FROM games ORDER BY map,a,b')]
    expected = len(names) * (len(names) - 1) * len(maps)
    keys = [(r['map'], r['team_a'], r['team_b']) for r in records]
    assert len(keys) == len(set(keys)), 'Duplicate fixtures'
    assert all(m in boards and a in lookup and b in lookup and a != b for m, a, b in keys)
    valid = [r for r in records if r['outcome'] in ('A', 'B', 'draw')]
    errors = [r for r in records if r['outcome'] == 'error']
    assert len(valid) + len(errors) == len(records), 'Unknown result type'
    n, m = len(names), len(maps)
    # Counts are from each row bot's perspective: wins, draws, losses.
    wdl = np.zeros((n, n, m, 3), dtype=int)
    side = np.zeros((n, 2, 3), dtype=int)
    faults = []
    for r in valid:
        a, b, k = lookup[r['team_a']], lookup[r['team_b']], boards[r['map']]
        assert r['winner'] == (r['team_a'] if r['outcome'] == 'A' else r['team_b'] if r['outcome'] == 'B' else None)
        result = 0 if r['outcome'] == 'A' else 1 if r['outcome'] == 'draw' else 2
        wdl[a, b, k, result] += 1
        wdl[b, a, k, 2 - result] += 1
        side[a, 0, result] += 1
        side[b, 1, 2 - result] += 1
        for fault in r.get('runtime_faults', []):
            faults.append(dict(map=r['map'], team_a=r['team_a'], team_b=r['team_b'], log=r['log'], **fault))
    count = wdl.sum(axis=3)
    assert int(count.sum()) == 2 * len(valid)
    assert (count <= 2).all()
    complete = len(valid) == expected
    if complete:
        assert (count[~np.eye(n, dtype=bool)] == 2).all()
    profiles = np.full((n, n, m), np.nan)
    paired = count == 2
    profiles[paired] = (wdl[..., 0] + .5 * wdl[..., 1])[paired] / 2
    corr, shared = correlations(profiles)
    order = cluster_order(corr)
    totals = wdl.sum(axis=(1, 2))
    played = totals.sum(axis=1)
    scores = np.divide(totals[:, 0] + .5 * totals[:, 1], played, out=np.full(n, np.nan), where=played > 0)
    ranking = sorted(range(n), key=lambda i: (-float(np.nan_to_num(scores[i], nan=-1)), names[i]))
    reports = out / 'report'
    reports.mkdir(exist_ok=True)
    game_header = ['map', 'team_a', 'team_b', 'outcome', 'winner', 'rounds', 'reason', 'seconds', 'returncode', 'runtime_fault_count', 'log', 'error']
    table(reports / 'games.csv', game_header,
          [[len(r.get('runtime_faults', [])) if key == 'runtime_fault_count' else r.get(key) for key in game_header] for r in records])
    table(reports / 'pair_by_map.csv', ['bot', 'opponent', 'map', 'wins', 'draws', 'losses', 'games', 'score'],
          [[names[i], names[j], maps[k], *wdl[i, j, k], count[i, j, k],
            (wdl[i, j, k, 0] + .5 * wdl[i, j, k, 1]) / count[i, j, k] if count[i, j, k] else '']
           for i in range(n) for j in range(n) if i != j for k in range(m)])
    table(reports / 'bot_by_map.csv', ['bot', 'map', 'wins', 'draws', 'losses'],
          [[names[i], maps[k], *wdl[i, :, k].sum(axis=0)] for i in range(n) for k in range(m)])
    table(reports / 'standings.csv', ['bot', 'games', 'wins', 'draws', 'losses', 'score', 'A_wins', 'A_draws', 'A_losses', 'B_wins', 'B_draws', 'B_losses'],
          [[names[i], played[i], *totals[i], scores[i], *side[i, 0], *side[i, 1]] for i in ranking])
    for filename, matrix in [('correlation.csv', corr), ('correlation_counts.csv', shared)]:
        table(reports / filename, ['bot'] + names,
              [[names[i]] + [float(v) if np.isfinite(v) else '' for v in matrix[i]] for i in range(n)])
    atomic(reports / 'runtime_faults.json', json.dumps(faults, indent=2))
    status = json.loads((out / 'status.json').read_text())
    status.update(complete=len(valid), total=expected, finished=complete, runtime_faults=len(faults), harness_errors=len(errors),
                  report_updated=datetime.now(timezone.utc).isoformat())
    atomic(reports / 'progress.json', json.dumps(status, indent=2))
    phase = 'COMPLETE' if complete else 'IN PROGRESS — provisional, incomplete coverage'
    caption = f'{phase} · {len(valid):,} / {expected:,} games · {n} bots · {m} maps · native runtime'
    heatmap(reports / 'correlation.png', names, corr, order, caption)
    pairs = sorted([(float(corr[i, j]), int(shared[i, j]), i, j) for i in range(n) for j in range(i + 1, n)
                    if np.isfinite(corr[i, j])], reverse=True)
    methodology = (
        'Score each game as win 1, draw 0.5, loss 0. Average the two side assignments for each bot–opponent–map. '
        'For each pair of bots, calculate Pearson correlation across the common third-party opponents and maps. '
        f'Their direct encounters and self matches are excluded; a complete pair has {(n-2)*m} shared observations. '
        'A map/opponent enters only once both side assignments have completed for both bots. '
        'Provisional correlations require at least 30 shared observations. Constant profiles have undefined correlation. '
        'Grey means undefined or insufficient results. This measures similarity of outcomes, not similarity of code or proof of strategy. '
        'Ranking measures strength separately. Average-linkage ordering uses distance 1 − correlation; undefined cells use distance 1 for ordering only. '
        'Every fixture runs once. These deterministic fixtures are not independent repeated samples. Native outcomes do not establish judge timeout safety. '
        'Engine-reported bot runtime faults remain scored outcomes and are exported separately; harness failures are not scored. '
        'Early results favor fixtures that finish quickly and have incomplete opponent coverage; do not treat provisional rankings as final.'
    )
    lines = [f'# All functional bots tournament\n\n{caption}\n', methodology,
             f'\nMaps: {", ".join(maps)}.\n',
             '\nExclusions: ' + '; '.join(f'{k}: {v}' for k, v in manifest['exclusions'].items()),
             f'\nReported runtime faults: {len(faults)}. Harness errors: {len(errors)}.\n',
             '\n| Bot | Games | W–D–L | Score |\n|---|---:|---:|---:|']
    lines += [f'| {names[i]} | {played[i]} | {totals[i,0]}–{totals[i,1]}–{totals[i,2]} | {scores[i]:.1%} |' for i in ranking]
    lines += ['\nMost similar observed pairs:\n', '| Bot 1 | Bot 2 | Correlation | Shared observations |\n|---|---|---:|---:|']
    lines += [f'| {names[i]} | {names[j]} | {r:.4f} | {c} |' for r, c, i, j in pairs[:20]]
    atomic(reports / 'README.md', '\n'.join(lines) + '\n')
    payload = json.dumps(dict(names=names, order=order, matrix=[[None if not np.isfinite(v) else float(v) for v in row] for row in corr],
                              shared=shared.tolist(), scores=[None if not np.isfinite(v) else float(v) for v in scores]), separators=(',', ':')).replace('</', '<\\/')
    rows = ''.join(f'<tr><td>{html.escape(names[i])}</td><td>{played[i]}</td><td>{totals[i,0]} / {totals[i,1]} / {totals[i,2]}</td><td>{scores[i]:.1%}</td></tr>' for i in ranking)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">REFRESH
<title>All functional bots — tournament</title><style>
body{font:16px system-ui,sans-serif;margin:28px;color:#20252d;background:#fafaf8}h1{font-size:27px}p{max-width:1050px;line-height:1.5}
a{color:#185780}button,select{font:inherit;padding:7px}#viewport{overflow:auto;max-height:76vh;border:1px solid #c8cdd0;background:white}canvas{display:block}
#detail{position:sticky;top:0;padding:12px;background:#e8eff4;min-height:46px;z-index:2}table{border-collapse:collapse}td,th{padding:6px 16px;text-align:left;border-bottom:1px solid #ddd}details{margin:20px 0}
</style><h1>Bot performance similarity</h1><p><b>CAPTION</b></p><p>Updated UPDATED. ETA. This page refreshes every two minutes while the tournament runs.</p>
<p><a href="games.csv">Every game</a> · <a href="pair_by_map.csv">Pair × map results</a> · <a href="bot_by_map.csv">Bot × map results</a> · <a href="correlation.csv">Correlation matrix</a> · <a href="correlation_counts.csv">Shared sample counts</a> · <a href="correlation.png">Full resolution image</a> · <a href="runtime_faults.json">Runtime faults</a> · <a href="README.md">Report</a></p>
<details><summary>How to read the matrix</summary><p>METHOD</p></details>
<p>Order: <select id="ordering"><option value="cluster">Similarity clusters</option><option value="name">Bot name</option><option value="strength">Overall score</option></select>
 Cell size: <select id="zoom"><option>12</option><option selected>20</option><option>30</option></select></p>
<div id="detail">Hover or click a cell. Blue: similar; red: opposite; grey: undefined or insufficient data.</div><div id="viewport"><canvas id="matrix"></canvas></div>
<details><summary>Standings (win / draw / loss)</summary><table><tr><th>Bot</th><th>Games</th><th>W / D / L</th><th>Score</th></tr>ROWS</table></details>
<script>const data=PAYLOAD;const canvas=document.getElementById('matrix'),ctx=canvas.getContext('2d');let order=data.order,cell=20;const left=370,top=380;
function color(v){if(v===null)return '#dbdde0';const a=[248,247,243],b=v>=0?[28,110,164]:[185,58,61];return 'rgb('+a.map((x,i)=>Math.round(x*(1-Math.abs(v))+b[i]*Math.abs(v))).join(',')+')'}
function draw(){cell=Number(document.getElementById('zoom').value);const kind=document.getElementById('ordering').value;order=kind==='cluster'?data.order.slice():data.names.map((_,i)=>i);if(kind==='strength')order.sort((a,b)=>(data.scores[b]??-1)-(data.scores[a]??-1));canvas.width=left+cell*order.length+20;canvas.height=top+cell*order.length+20;ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.font='12px system-ui';order.forEach((i,a)=>{ctx.fillStyle='#20252d';ctx.textAlign='right';ctx.fillText(data.names[i],left-8,top+a*cell+cell*.72);ctx.save();ctx.translate(left+a*cell+cell*.72,top-8);ctx.rotate(-Math.PI/2);ctx.textAlign='left';ctx.fillText(data.names[i],0,0);ctx.restore();order.forEach((j,b)=>{ctx.fillStyle=color(data.matrix[i][j]);ctx.fillRect(left+b*cell,top+a*cell,cell-1,cell-1)})})}
function inspect(e){const rect=canvas.getBoundingClientRect(),a=Math.floor((e.clientY-rect.top-top)/cell),b=Math.floor((e.clientX-rect.left-left)/cell);if(a<0||b<0||a>=order.length||b>=order.length)return;const i=order[a],j=order[b],r=data.matrix[i][j];document.getElementById('detail').textContent=data.names[i]+' ↔ '+data.names[j]+' | r = '+(r===null?'undefined':r.toFixed(4))+' | '+data.shared[i][j]+' shared opponent–map observations | scores '+[i,j].map(k=>data.scores[k]===null?'NA':(100*data.scores[k]).toFixed(1)+'%').join(' / ')}
canvas.addEventListener('mousemove',inspect);canvas.addEventListener('click',inspect);document.getElementById('ordering').onchange=draw;document.getElementById('zoom').onchange=draw;draw();</script></html>'''
    replacements = {'REFRESH': '' if complete else '<meta http-equiv="refresh" content="120">', 'CAPTION': html.escape(caption),
                    'UPDATED': html.escape(status['report_updated']), 'ETA': ('Finished' if complete else f"Runner estimate: {status.get('eta_hours')} hours remaining"),
                    'METHOD': html.escape(methodology), 'ROWS': rows, 'PAYLOAD': payload}
    for key, value in replacements.items():
        page = page.replace(key, value)
    atomic(reports / 'index.html', page)
    print(caption, flush=True)
    return complete


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--interval', type=float, default=120)
    args = parser.parse_args()
    while True:
        if generate(args.output.resolve()) or not args.watch:
            break
        time.sleep(args.interval)
