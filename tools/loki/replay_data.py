"""Extract candidate-ranking demonstrations from public Battlecode replays.

The replay is used to recover the teacher's chosen action and game timeline.
Every feature is built from the actor's current 7x7 view, own known body, and
the public unit/round counters. Other dragons, pearls, and portal exits outside
that view are hidden before features are calculated.
"""
from collections import Counter, deque
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "leviathan"))
sys.path.insert(0, str(ROOT / "tools" / "ouroboros"))
sys.path.insert(0, str(ROOT / "bots" / "loki-v01"))

from replay import Reader
from mapview import load_map
from loki_features import features

UNIT_LIMIT = 64
SPLIT_CHILD = 2
SPLIT_MIN = 4
SPLIT_STOP = 380
GROW_FROM = 380
OPENING_RESCUE_UNTIL = 1
OPENING_RESCUE_MIN = 8
OPENING_INITIAL_ID_LIMIT = 6
OPENING_PRODUCTION_START = 1
OPENING_PRODUCTION_UNTIL = 30
OPENING_PRODUCTION_UNIT_CAP = 32
SPRINT3_LIMIT = 12


def torus_distance(a, b, width, height):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return min(dx, width - dx) + min(dy, height - dy)


def torus_chebyshev(a, b, width, height):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(min(dx, width - dx), min(dy, height - dy))


def cell_id(point, width):
    return point[1] * width + point[0]


def point(obj):
    return obj.num(), obj.num(4)


def map_geometry(map_text):
    m = load_map(map_text)
    width, height = m["W"], m["H"]
    portal_edges = {}
    portal_by_id = {}
    for (x, y), pid in m["portal_h"].items():
        edge = (0, x, y)
        portal_edges[edge] = pid
        portal_by_id.setdefault(pid, []).append(edge)
    for (x, y), pid in m["portal_v"].items():
        edge = (1, x, y)
        portal_edges[edge] = pid
        portal_by_id.setdefault(pid, []).append(edge)

    def edge_at(cell, direction):
        x, y = cell % width, cell // width
        if direction == 0:
            return (0, x, y)
        if direction == 1:
            return (1, (x + 1) % width, y)
        if direction == 2:
            return (0, x, (y + 1) % height)
        return (1, x, y)

    def full_destination(cell, direction):
        x, y = cell % width, cell // width
        if direction == 0:
            neighbor = ((y - 1) % height) * width + x
        elif direction == 1:
            neighbor = y * width + (x + 1) % width
        elif direction == 2:
            neighbor = ((y + 1) % height) * width + x
        else:
            neighbor = y * width + (x - 1) % width
        edge = edge_at(cell, direction)
        orientation, ex, ey = edge
        wall_set = m["kelp_h"] if orientation == 0 else m["kelp_v"]
        if (ex, ey) in wall_set:
            return -1
        pid = portal_edges.get(edge)
        if pid is None:
            return neighbor
        ends = portal_by_id.get(pid, ())
        if len(ends) != 2:
            return -3
        other = ends[0] if ends[1] == edge else ends[1]
        other_orientation, ox, oy = other
        out_x = ox if other_orientation == 0 or direction == 1 else ox - 1
        out_y = oy if other_orientation == 1 or direction == 2 else oy - 1
        return (out_y % height) * width + (out_x % width)

    def edges_visible_from(head):
        hx, hy = head % width, head // width
        seen = set()
        # Match the eight horizontal rows and seven vertical rows Bifröst reads.
        for row in range(8):
            y = (hy - 3 + row) % height
            for col in range(7):
                seen.add((0, (hx - 3 + col) % width, y))
        for row in range(7):
            y = (hy - 3 + row) % height
            for col in range(8):
                seen.add((1, (hx - 3 + col) % width, y))
        return seen

    def destination_for_view(head, visible_edges):
        def destination(cell, direction):
            edge = edge_at(cell, direction)
            if edge not in visible_edges:
                return -2
            out = full_destination(cell, direction)
            if out < 0:
                return out
            pid = portal_edges.get(edge)
            if pid is not None:
                ends = portal_by_id.get(pid, ())
                if len(ends) != 2:
                    return -3
                other_edge = ends[0] if ends[1] == edge else ends[1]
                # A visible paired edge lets Bifröst identify a remote exit;
                # its tile contents and occupants remain hidden in state.other.
                if other_edge not in visible_edges:
                    return -3
            return out
        return destination

    return m, destination_for_view, edges_visible_from


def _face_from_body(body, width, height):
    if len(body) < 2:
        return 0
    head, behind = body[0], body[1]
    hx, hy = head
    bx, by = behind
    if (bx, (by - 1) % height) == (hx, hy):
        return 0
    if ((bx + 1) % width, by) == (hx, hy):
        return 1
    if (bx, (by + 1) % height) == (hx, hy):
        return 2
    if ((bx - 1) % width, by) == (hx, hy):
        return 3
    return 0


def _visible_cells(head, width, height):
    hx, hy = head % width, head // width
    out = set()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = (hx + dx) % width, (hy + dy) % height
            out.add(y * width + x)
    return out


def _candidate_menu(state, actor, born_round, visible_self_count):
    width, height = state["width"], state["height"]
    length, units, round_num = state["length"], state["units"], state["round"]
    head = state["body"][-1]
    paths = [("move", (direction,)) for direction in range(4)]
    near_enemy = any(
        torus_chebyshev((head % width, head // width),
                        (cell % width, cell // width), width, height) <= 4
        for cell, _enemy_len in state["enemies"]
    )
    if length >= 3 and near_enemy:
        for d1 in range(4):
            for d2 in range(4):
                if d2 == (d1 + 2) % 4:
                    continue
                paths.append(("move", (d1, d2)))
                if 4 <= length < SPRINT3_LIMIT:
                    for d3 in range(4):
                        if d3 != (d2 + 2) % 4:
                            paths.append(("move", (d1, d2, d3)))

    actions = list(paths)
    fully_known = visible_self_count >= length
    if (fully_known and length >= SPLIT_MIN and units < state["unit_limit"]
            and round_num < SPLIT_STOP and round_num < GROW_FROM):
        actions.append(("split", SPLIT_CHILD))
    if (length >= OPENING_RESCUE_MIN and round_num <= OPENING_RESCUE_UNTIL
            and born_round <= OPENING_RESCUE_UNTIL
            and ((actor & 4095) < OPENING_INITIAL_ID_LIMIT or round_num > born_round)
            and visible_self_count < length and units < state["unit_limit"]):
        actions.append(("split", length - 2))
    if (OPENING_PRODUCTION_START <= round_num <= OPENING_PRODUCTION_UNTIL
            and length >= SPLIT_MIN and units < OPENING_PRODUCTION_UNIT_CAP
            and units < state["unit_limit"]):
        actions.append(("split", SPLIT_CHILD))
    # Bifröst v01 also offers a last-resort tail rescue when every ordinary
    # single move is fatal and the full body is known.
    if fully_known and length >= 4 and units < state["unit_limit"]:
        single_features = [features(state, action) for action in paths[:4]]
        if all(row[18] == 0.0 for row in single_features):
            actions.append(("split", length - 2))
    unique = []
    seen = set()
    for action in actions:
        key = (action[0], tuple(action[1]) if action[0] == "move" else action[1])
        if key not in seen:
            seen.add(key)
            unique.append(action)
    return unique


def _read_action(reader, action_obj):
    kind = action_obj.num(0, "H")
    if kind == 0:
        segment, at, word = reader.pointer(
            action_obj.s, action_obj.a + action_obj.dw
        )
        count = word >> 35
        if count:
            directions = struct.unpack_from(
                "<" + "H" * count, reader.segments[segment], at * 8
            )
        else:
            directions = ()
        return "move", tuple(int(d) for d in directions)
    if kind == 1:
        return "split", int(action_obj.num(4))
    return "suicide", 0


def _game_series(game_id):
    if game_id.startswith("374"):
        return "ranked-vs-calc"
    if game_id.startswith("375"):
        return "ranked-vs-shink-ai-6500"
    return "other"


def extract_game(path, teacher_side="A", keep_every=5):
    """Yield sampled (game, series, state, candidates, chosen) groups."""
    path = Path(path)
    game_id = path.stem
    reader = Reader(path)
    root = reader.object(0, 0)
    if root.num(0, "I") not in (0, 1, 2):
        raise ValueError(f"Unsupported replay format in {path}")
    map_text = root.text(0)
    m, destination_for_view, edges_visible_from = map_geometry(map_text)
    width, height = m["W"], m["H"]
    teams = {i: team for i, (team, _body) in enumerate(m["dragons"])}
    bodies = {i: deque(cells) for i, (_team, cells) in enumerate(m["dragons"])}
    live = set(bodies)
    born = {i: 0 for i in live}
    first_turn = {}
    facing = {
        i: _face_from_body(list(body), width, height)
        for i, body in bodies.items()
    }
    pearls = set()
    current_round = -1
    actor = None
    stats = Counter()
    for event in root.items(3):
        event_kind = event.num(0, "H")
        obj = event.child(0)
        ident = obj.num()
        if event_kind == 0:
            current_round = ident
        elif event_kind == 1:
            actor = ident
            first_turn.setdefault(ident, current_round)
        elif event_kind == 3:
            tile = point(obj.child(0))
            cell = cell_id(tile, width)
            if obj.num(0, "B"):
                pearls.add(cell)
            else:
                pearls.discard(cell)
        elif event_kind == 4 and actor in live and actor in bodies:
            if not obj.has(0):
                continue
            action = _read_action(reader, obj.child(0))
            stats["actions_seen"] += 1
            if teams.get(actor) != teacher_side or action[0] == "suicide":
                continue
            head = bodies[actor][0]
            head_id = cell_id(head, width)
            visible = _visible_cells(head_id, width, height)
            own_head_tail = list(bodies[actor])
            visible_self_count = sum(
                cell_id(p, width) in visible for p in own_head_tail
            )
            # At a fresh decision Bifröst can reconstruct only the contiguous
            # own-body chain visible behind the head. Hidden replay tail cells
            # must not leak into candidate simulation.
            observed_chain = []
            for p in own_head_tail:
                if cell_id(p, width) not in visible:
                    break
                observed_chain.append(p)
            body_tail_head = [cell_id(p, width) for p in reversed(observed_chain)]
            allies, enemies = [], []
            other = {}
            for did in live:
                if did == actor or did not in bodies:
                    continue
                chain = list(bodies[did])
                visible_parts = [
                    (index, p) for index, p in enumerate(chain)
                    if cell_id(p, width) in visible
                ]
                # Observation body lengths are the visible segment counts,
                # not the hidden full lengths held by replay reconstruction.
                visible_len = len(visible_parts)
                ours = teams.get(did) == teacher_side
                for index, p in visible_parts:
                    cell = cell_id(p, width)
                    other[cell] = (did, ours, index == 0, visible_len)
                head_cell = cell_id(chain[0], width)
                if head_cell in visible:
                    (allies if ours else enemies).append((head_cell, visible_len))
            visible_pearls = {cell for cell in pearls if cell in visible}
            state = {
                "round": current_round,
                "width": width,
                "height": height,
                "length": len(bodies[actor]),
                "units": sum(teams.get(did) == teacher_side for did in live),
                "unit_limit": UNIT_LIMIT,
                "age": max(0, current_round - first_turn.get(actor, current_round)),
                "face": facing.get(actor, 0),
                "body": body_tail_head,
                "allies": allies,
                "enemies": enemies,
                "pearls": visible_pearls,
                "other": other,
                "destination": destination_for_view(
                    head_id, edges_visible_from(head_id)
                ),
            }
            candidates = _candidate_menu(
                state, actor, first_turn.get(actor, current_round), visible_self_count
            )
            chosen = action
            try:
                chosen_index = candidates.index(chosen)
            except ValueError:
                stats["unsupported_actions"] += 1
                continue
            stats["teacher_actions"] += 1
            stats["teacher_splits"] += action[0] == "split"
            # Keep every split demonstration and a deterministic 1-in-keep_every
            # sample of moves; this retains rare production decisions without
            # letting ordinary movement dominate the fit.
            if action[0] != "split" and (current_round + actor) % keep_every:
                continue
            rows = [features(state, candidate) for candidate in candidates]
            yield {
                "game": game_id,
                "series": _game_series(game_id),
                "round": current_round,
                "actor": actor,
                "action": chosen,
                "candidates": candidates,
                "features": rows,
                "label": chosen_index,
                "sample_weight": 1.0 if action[0] != "split" else 1.0 / keep_every,
            }
        elif event_kind == 9 and ident in bodies:
            chain = bodies[ident]
            new_head, tail = point(obj.child(0)), point(obj.child(1))
            if not chain or chain[0] != new_head:
                chain.appendleft(new_head)
            while len(chain) > 1 and chain[-1] != tail:
                chain.pop()
            facing[ident] = int(obj.num(4, "H"))
        elif event_kind == 10 and ident in bodies:
            child_id = int(obj.num(4))
            team = teams[ident]
            teams[child_id] = team
            bodies[ident] = deque(point(p) for p in obj.items(0))
            bodies[child_id] = deque(point(p) for p in obj.items(1))
            live.add(child_id)
            born[child_id] = current_round
            facing[child_id] = int(obj.num(10, "H"))
        elif event_kind == 11:
            live.discard(ident)
            bodies.pop(ident, None)
    yield {"_summary": dict(stats)}
