"""Replay diagnostics and dependency-free SVG charts for compare_bot.py.

Reuses the repository's version-checked replay reconstruction. All quantities
are recorded events except collision attribution and the labelled control proxy.
"""
from collections import Counter, deque
from html import escape
import math

from public_replay_review import analyse as review, Reader, load_map

COUNTERS = ("enemy_kills", "killed_by_enemy", "team_kills", "self_collisions",
            "wall_deaths", "invalid_action_deaths", "unattributed_collision_deaths")
PANELS = [
    ("units", "Living dragons"), ("total", "Total length"), ("longest", "Longest dragon"),
    ("pearls", "Pearls collected · cumulative"), ("splits", "Splits · cumulative"),
    ("deaths", "Deaths · cumulative"), ("enemy_kills", "Opponent kills · attributed"),
    ("killed_by_enemy", "Deaths to opponent · attributed"), ("team_kills", "Friendly collision deaths"),
    ("self_collisions", "Self-collision deaths"), ("wall_deaths", "Wall deaths"),
    ("invalid_action_deaths", "Invalid / absent action deaths"),
    ("suicides", "Suicide / no-action events"), ("tle", "Timed-out turns"),
    ("space_share", "Space control proxy · % of map"),
]
NOTES = (
    "Curves are start-of-round snapshots plus the final state. Event counters are cumulative. "
    "Kills attribute each collision death to the other dragon's team; mutual head collisions count "
    "one death per victim, including friendly collisions. Unresolved attribution is exported separately. "
    "Self-collisions and wall deaths do not establish intent. Replay 'suicide' actions can represent "
    "an absent/invalid action, so they do not establish deliberate feeding either. "
    "Space control is the percentage of all tiles strictly closer in terrain-only movement steps to "
    "this team's nearest living head. Kelp, portals and wrapping are included; body blocking, facing, "
    "length, speed, pearl value and tactical safety are ignored. Ties and tiles unreachable by either "
    "team remain unclaimed. Control is sampled at the configured interval and at the final state."
)


def movement_graph(maptext):
    """Each node is a tile; links are one terrain-only movement step."""
    board = load_map(maptext)
    w, h = board["W"], board["H"]
    portals = {}
    for orientation, key in ((0, "portal_h"), (1, "portal_v")):
        for (x, y), ident in board[key].items():
            portals.setdefault(ident, []).append((orientation, x, y))
    if any(len(ends) != 2 for ends in portals.values()):
        raise ValueError("A portal pair is incomplete in the replay map")
    graph = [[] for _ in range(w * h)]
    for y in range(h):
        for x in range(w):
            for direction, (orientation, ex, ey) in enumerate(
                    ((0, x, y), (1, (x+1) % w, y), (0, x, (y+1) % h), (1, x, y))):
                suffix = "v" if orientation else "h"
                if (ex, ey) in board["kelp_" + suffix]:
                    continue
                ident = board["portal_" + suffix].get((ex, ey))
                if ident is None:
                    nx, ny = (x + (0, 1, 0, -1)[direction]) % w, (y + (-1, 0, 1, 0)[direction]) % h
                else:
                    ends = portals[ident]
                    _, px, py = next(e for e in ends if e != (orientation, ex, ey))
                    nx = (px - (orientation == 1 and direction == 3)) % w
                    ny = (py - (orientation == 0 and direction == 0)) % h
                graph[y*w+x].append(ny*w+nx)
    return board, graph


def distances(graph, sources):
    result = [math.inf] * len(graph)
    queue = deque(set(sources))
    for source in queue:
        result[source] = 0
    while queue:
        here = queue.popleft()
        for there in graph[here]:
            if result[there] == math.inf:
                result[there] = result[here] + 1
                queue.append(there)
    return result


def control(graph, a, b):
    da, db = distances(graph, a), distances(graph, b)
    n = len(graph)
    return {"A": 100 * sum(x < y for x, y in zip(da, db)) / n,
            "B": 100 * sum(y < x for x, y in zip(da, db)) / n,
            "tied": 100 * sum(x == y and math.isfinite(x) for x, y in zip(da, db)) / n,
            "unreachable": 100 * sum(not math.isfinite(x) and not math.isfinite(y)
                                     for x, y in zip(da, db)) / n}


def control_series(path, every):
    reader = Reader(path)
    root = reader.object(0, 0)
    board, graph = movement_graph(root.text(0))
    w = board["W"]
    teams = {i: t for i, (t, _) in enumerate(board["dragons"])}
    heads = {i: body[0][1] * w + body[0][0] for i, (_, body) in enumerate(board["dragons"])}
    result, last_round = {}, -1

    def sample(round_number):
        result[round_number] = control(graph, [c for i, c in heads.items() if teams[i] == "A"],
                                       [c for i, c in heads.items() if teams[i] == "B"])

    def cell(point):
        return point.num(4) * w + point.num()

    for event in root.items(3):
        kind, obj = event.num(0, "H"), event.child(0)
        ident = obj.num()
        if kind == 0:
            last_round = ident
            if ident % every == 0:
                sample(ident)
        elif kind == 9:
            heads[ident] = cell(obj.child(0))
        elif kind == 10:
            child = obj.num(4)
            teams[child] = teams[ident]
            heads[ident] = cell(next(obj.items(0)))
            heads[child] = cell(next(obj.items(1)))
        elif kind == 11:
            heads.pop(ident)
    sample(last_round + 1)
    return result


def attribute_death(death):
    """Return per-team counter increments; do not infer voluntary sacrifice."""
    team, cause = death["team"], death["cause"]
    other = death.get("hit_team") if cause == "body" else (
        death.get("attacker_team") if death["id"] != death["actor"] else death.get("victim_team"))
    result = {t: Counter() for t in "AB"}
    if cause in ("wall", "self", "invalid"):
        metric = {"wall": "wall_deaths", "self": "self_collisions", "invalid": "invalid_action_deaths"}[cause]
        result[team][metric] += 1
    elif other == team:
        result[team]["team_kills"] += 1
    elif other in ("A", "B"):
        result[other]["enemy_kills"] += 1
        result[team]["killed_by_enemy"] += 1
    else:
        result[team]["unattributed_collision_deaths"] += 1
    return result


def analyse(path, control_every=10):
    data = review(path)
    controls = control_series(path, control_every)
    deaths = iter(data["deaths"])
    death = next(deaths, None)
    counters = {t: Counter() for t in "AB"}
    series = {t: [] for t in "AB"}
    for point in data["curve"]:
        rnd = point["round"]
        while death is not None and death["round"] < rnd:
            increments = attribute_death(death)
            for t in "AB":
                counters[t].update(increments[t])
            death = next(deaths, None)
        for t in "AB":
            values = {k: point[t].get(k, 0) for k, _ in PANELS if k != "space_share"}
            values.update({k: counters[t][k] for k in COUNTERS})
            series[t].append(dict(round=rnd, **values,
                                 space_share=controls.get(rnd, {}).get(t),
                                 space_tied=controls.get(rnd, {}).get("tied"),
                                 space_unreachable=controls.get(rnd, {}).get("unreachable")))
    if death is not None:
        raise ValueError("Death events extend beyond the final replay snapshot")
    for t in "AB":
        final = series[t][-1]
        accounted = sum(final[k] for k in ("team_kills", "killed_by_enemy", "self_collisions",
                        "wall_deaths", "invalid_action_deaths", "unattributed_collision_deaths"))
        if final["deaths"] != accounted:
            raise ValueError("Death attribution does not reconcile with total deaths")
    return dict(version=data["version"], map=data["map"], rounds=data["rounds"],
                winner=data["winner"], reason=data["reason"], final=data["final"],
                series=series, deaths=data["deaths"], notes=NOTES)


def chart(path, stats, candidate, opponent, side, board):
    """One labelled SVG dashboard per map/side, with both teams on every panel."""
    other = "B" if side == "A" else "A"
    width, panel_w, panel_h, header = 1230, 400, 215, 105
    height = header + math.ceil(len(PANELS) / 3) * panel_h + 38
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#fafaf8"/>',
           '<style>text{font-family:Arial,sans-serif;fill:#25313c;font-size:12px}.title{font-size:20px;font-weight:bold}.panel{font-size:14px;font-weight:bold}</style>',
           f'<text x="20" y="30" class="title">{escape(candidate)} vs {escape(opponent)}</text>',
           f'<text x="20" y="54">{escape(board)} · candidate side {side} · winner {stats["winner"]} · {stats["rounds"]} rounds · {escape(stats["reason"])}</text>',
           f'<text x="20" y="79" style="fill:#1677b8">━━ {escape(candidate)}</text>',
           f'<text x="635" y="79" style="fill:#c35c20">━━ {escape(opponent)}</text>']
    for index, (metric, title) in enumerate(PANELS):
        ox, oy = 15 + index % 3 * (panel_w + 5), header + index // 3 * panel_h
        left, top, pw, ph = ox + 45, oy + 32, panel_w - 62, panel_h - 72
        curves = [[(p["round"], p[metric]) for p in stats["series"][t] if p[metric] is not None] for t in (side, other)]
        ymax = 100 if metric == "space_share" else max(1, max((v for points in curves for _, v in points), default=1))
        xmax = max(1, stats["rounds"])
        svg.append(f'<text x="{ox+6}" y="{oy+17}" class="panel">{escape(title)}</text>')
        for fraction in (0, .5, 1):
            y = top + ph * (1 - fraction)
            svg += [f'<path d="M{left},{y}h{pw}" stroke="#dce1e5"/>',
                    f'<text x="{left-6}" y="{y+4}" text-anchor="end">{ymax*fraction:g}</text>']
            x = left + pw * fraction
            svg.append(f'<text x="{x}" y="{top+ph+18}" text-anchor="middle">{xmax*fraction:g}</text>')
        for points, color in zip(curves, ("#1677b8", "#c35c20")):
            coordinates = " ".join(f"{left+x/xmax*pw:.1f},{top+ph-y/ymax*ph:.1f}" for x, y in points)
            svg.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="1.8"/>')
        svg.append(f'<text x="{left+pw/2}" y="{top+ph+34}" text-anchor="middle">Round</text>')
    svg.append(f'<text x="20" y="{height-15}">Control is a terrain-only nearest-head proxy. Collision counts describe outcomes, not intent. See the report for definitions.</text></svg>')
    path.write_text("\n".join(svg), encoding="utf-8")
