"""Observation-safe candidate features shared by Loki training and inference.

The training extractor reconstructs the same local view from public replay
events. Inference reads Bifröst's remembered view. No full-board replay data is
passed to the model.
"""

FEATURE_NAMES = (
    "round", "length", "unit_fraction", "age", "width", "height",
    "allies_visible", "enemies_visible", "nearest_ally", "nearest_enemy",
    "pearls_visible", "nearest_pearl", "open_exits", "is_split",
    "split_size", "split_fraction", "move_steps", "relative_direction",
    "survival", "pearls_eaten", "length_change", "portal_steps",
    "end_exits", "pearl_progress", "enemy_pressure", "enemy_head_hit",
    "split_child_exits", "largest_visible_enemy",
)


def _tdist(a, b, width, height):
    dx = abs(a % width - b % width)
    dy = abs(a // width - b // width)
    dx = min(dx, width - dx)
    dy = min(dy, height - dy)
    return dx + dy


def _cheb(a, b, width, height):
    dx = abs(a % width - b % width)
    dy = abs(a // width - b // width)
    dx = min(dx, width - dx)
    dy = min(dy, height - dy)
    return max(dx, dy)


def _neighbor(state, cell, direction):
    width, height = state["width"], state["height"]
    x, y = cell % width, cell // width
    if direction == 0:
        y = (y - 1) % height
    elif direction == 1:
        x = (x + 1) % width
    elif direction == 2:
        y = (y + 1) % height
    else:
        x = (x - 1) % width
    return y * width + x


def _dest(state, cell, direction):
    cache = state.get("_loki_dest_cache")
    if cache is None:
        return state["destination"](cell, direction)
    key = (cell, direction)
    value = cache.get(key)
    if value is None:
        value = state["destination"](cell, direction)
        cache[key] = value
    return value


def _open_exits(state, head, own_cells, extra_blocked=()):
    own = own_cells if isinstance(own_cells, set) else set(own_cells)
    if isinstance(extra_blocked, (set, frozenset)):
        blocked = extra_blocked
    elif extra_blocked:
        blocked = set(extra_blocked)
    else:
        blocked = ()
    other = state["other"]
    n_ok = 0
    for direction in range(4):
        cell = _dest(state, head, direction)
        if cell == -2:
            cell = _neighbor(state, head, direction)
        if cell < 0 or cell in own or cell in blocked or cell in other:
            continue
        n_ok += 1
    return n_ok


def _nearest(cell, points, width, height, default=16):
    if not points:
        return default
    return min(_tdist(cell, p, width, height) for p in points)


def _simulate(state, path):
    body = list(state["body"])  # tail -> head, matching Bifröst world.body
    own = set(body)
    pearls = state["pearls"]
    eaten_cells = set()
    eaten = 0
    portals = 0
    head_hit = None
    for step, direction in enumerate(path):
        if step and len(body) <= 2:
            return "dead", body, eaten, portals, head_hit
        old_head = body[-1]
        cell = _dest(state, old_head, direction)
        if cell == -2:
            cell = _neighbor(state, old_head, direction)
        elif cell == -3:
            return ("dive" if step == 0 else "dead"), body, eaten, portals, head_hit
        if cell < 0 or cell in own:
            return "dead", body, eaten, portals, head_hit
        other = state["other"].get(cell)
        if other is not None:
            if other[2]:
                head_hit = other
                return "h2h", body, eaten, portals, head_hit
            return "dead", body, eaten, portals, head_hit
        if cell != _neighbor(state, old_head, direction):
            portals += 1
        body.append(cell)
        own.add(cell)
        if cell in pearls and cell not in eaten_cells:
            eaten_cells.add(cell)
            eaten += 1
        else:
            own.discard(body.pop(0))
        if step:
            own.discard(body.pop(0))
    return "ok", body, eaten, portals, head_hit


def features(state, action):
    """Return a fixed-width vector for one Bifröst candidate action."""
    width, height = state["width"], state["height"]
    round_num = state["round"]
    length = state["length"]
    units = state["units"]
    head = state["body"][-1]
    ally_cells = [p[0] for p in state["allies"]]
    enemy_cells = [p[0] for p in state["enemies"]]
    pearl_cells = list(state["pearls"])
    nearest_ally = _nearest(head, ally_cells, width, height)
    nearest_enemy = _nearest(head, enemy_cells, width, height)
    nearest_pearl = _nearest(head, pearl_cells, width, height)
    exits_now = _open_exits(state, head, state["body"])
    largest_enemy = max((p[1] for p in state["enemies"]), default=0)

    kind, arg = action
    is_split = kind == "split"
    split_size = int(arg) if is_split else 0
    split_child_exits = 0
    eaten = portals = end_exits = enemy_hit = 0
    survival = 0.0
    length_change = 0
    end_head = head
    path = [] if is_split else list(arg)

    if is_split:
        n = split_size
        body = state["body"]
        if 0 < n and length - n >= 2 and units < state["unit_limit"]:
            if n < len(body):
                child_body = list(reversed(body[:n]))  # child head -> tail
                parent_body = body[n:]
                child_head = child_body[0]
                parent_head = parent_body[-1]
                child_cells = set(child_body)
                parent_cells = set(parent_body)
                split_child_exits = _open_exits(
                    state, child_head, child_cells, parent_cells
                )
                parent_exits = _open_exits(
                    state, parent_head, parent_cells, child_cells
                )
                survival = 1.0 if split_child_exits > 0 else 0.0
                end_exits = min(4, parent_exits)
                end_head = parent_head
            else:
                # Bifröst can issue its one-shot opening rescue even when the
                # tail is outside local sensing; score that unseen child as
                # uncertain rather than consulting the replay's hidden cells.
                survival = 0.25
                end_exits = _open_exits(state, head, body)
            length_change = -n
    else:
        status, after, eaten, portals, hit = _simulate(state, path)
        if status == "ok":
            survival = 1.0
            end_head = after[-1]
            end_exits = _open_exits(state, end_head, after)
            length_change = len(after) - length
        elif status == "h2h":
            survival = 0.5
            enemy_hit = int(hit is not None and not hit[1])
            if hit is not None:
                length_change = -length
        elif status == "dive":
            survival = 0.25

    new_pearl_dist = _nearest(end_head, pearl_cells, width, height)
    if is_split:
        new_pearl_dist = nearest_pearl
    enemy_after = _nearest(end_head, enemy_cells, width, height)
    rel_dir = 0
    if path:
        rel_dir = (path[0] - state["face"]) % 4

    return [
        round_num / 500.0,
        length / 64.0,
        units / max(1, state["unit_limit"]),
        state["age"] / 500.0,
        width / 64.0,
        height / 64.0,
        min(1.0, len(state["allies"]) / 16.0),
        min(1.0, len(state["enemies"]) / 16.0),
        min(1.0, nearest_ally / 16.0),
        min(1.0, nearest_enemy / 16.0),
        min(1.0, len(pearl_cells) / 25.0),
        min(1.0, nearest_pearl / 16.0),
        exits_now / 4.0,
        float(is_split),
        split_size / 64.0,
        split_size / max(1, length),
        len(path) / 3.0,
        rel_dir / 3.0,
        survival,
        min(1.0, eaten / 3.0),
        max(-1.0, min(1.0, length_change / 16.0)),
        min(1.0, portals / 3.0),
        end_exits / 4.0,
        max(-1.0, min(1.0, (nearest_pearl - new_pearl_dist) / 16.0)),
        1.0 / (1.0 + enemy_after),
        float(enemy_hit),
        split_child_exits / 4.0,
        largest_enemy / 64.0,
    ]


def from_world(world):
    """Build features from the same local view used by replay extraction."""
    other = dict(world.occ)
    allies = [(cell, world.alen.get(ident, 1)) for cell, ident in world.ally_heads]
    enemies = [(cell, world.elen.get(ident, 1)) for cell, ident in world.enemy_heads]
    hx, hy = world.HEAD % world.W, world.HEAD // world.W
    visible_edges = set()
    for row in range(8):
        y = (hy - 3 + row) % world.H
        for col in range(7):
            x = (hx - 3 + col) % world.W
            visible_edges.add(y * world.W + x)
    for row in range(7):
        y = (hy - 3 + row) % world.H
        for col in range(8):
            x = (hx - 3 + col) % world.W
            visible_edges.add(world.NC + y * world.W + x)

    def local_destination(cell, direction):
        edge = world.ekey(cell, direction)
        if edge not in visible_edges:
            return -2
        out = world.dest(cell)[direction]
        if world.ek[edge] == 3:
            ends = world.pends.get(world.epid.get(edge), ())
            if not ends or len(ends) < 2:
                return -3
            other_edge = ends[0] if ends[1] == edge else ends[1]
            if other_edge not in visible_edges:
                return -3
        return out

    return {
        "round": world.RND,
        "width": world.W,
        "height": world.H,
        "length": world.LEN,
        "units": world.UNITS,
        "unit_limit": world.LIMIT,
        "age": max(0, world.RND - world.BORN),
        "face": world.FACE,
        "body": list(world.body),
        "allies": allies,
        "enemies": enemies,
        "pearls": {cell for cell, seen_round in world.pearls.items()
                   if seen_round == world.RND},
        "other": other,
        "destination": local_destination,
    }



# The fitted v01 forest splits only on these six columns. Keep the full
# observation-safe feature builder above for training and use this sparse path
# in the bot.
RANKING_FEATURE_INDICES = frozenset((12, 15, 16, 17, 18, 22))


def prepare_inference(state):
    """Cache turn-invariant exit and portal lookups for all candidate actions."""
    state["_loki_dest_cache"] = {}
    state["_loki_current_exits"] = _open_exits(
        state, state["body"][-1], state["body"]
    )
    return state


def _simulate_rank_action(state, path):
    """Simulate only facts consumed by the trained ranker.

    A tail offset avoids shifting a potentially long Python list with pop(0)
    on each step. The active body remains represented by the list suffix and
    the matching occupancy set.
    """
    body = list(state["body"])
    own = set(body)
    pearls = state["pearls"]
    eaten_cells = set()
    tail = 0

    for step, direction in enumerate(path):
        if step and len(body) - tail <= 2:
            return "dead", -1, None
        old_head = body[-1]
        cell = _dest(state, old_head, direction)
        if cell == -2:
            cell = _neighbor(state, old_head, direction)
        elif cell == -3:
            return ("dive" if step == 0 else "dead"), -1, None
        if cell < 0 or cell in own:
            return "dead", -1, None
        other = state["other"].get(cell)
        if other is not None:
            return ("h2h" if other[2] else "dead"), -1, None

        body.append(cell)
        own.add(cell)
        if cell in pearls and cell not in eaten_cells:
            eaten_cells.add(cell)
        else:
            own.discard(body[tail])
            tail += 1
        if step:
            own.discard(body[tail])
            tail += 1

    return "ok", body[-1], own


def rank_features(state, action):
    """Compute just the columns used by the exported model's decision trees."""
    if "_loki_current_exits" not in state:
        prepare_inference(state)

    length = state["length"]
    units = state["units"]
    head = state["body"][-1]
    kind, arg = action
    is_split = kind == "split"
    split_size = int(arg) if is_split else 0
    path = [] if is_split else list(arg)

    survival = 0.0
    end_exits = 0
    if is_split:
        n = split_size
        body = state["body"]
        if 0 < n and length - n >= 2 and units < state["unit_limit"]:
            if n < len(body):
                child_body = list(reversed(body[:n]))
                parent_body = body[n:]
                child_head = child_body[0]
                parent_head = parent_body[-1]
                child_cells = set(child_body)
                parent_cells = set(parent_body)
                child_exits = _open_exits(
                    state, child_head, child_cells, parent_cells
                )
                parent_exits = _open_exits(
                    state, parent_head, parent_cells, child_cells
                )
                survival = 1.0 if child_exits > 0 else 0.0
                end_exits = min(4, parent_exits)
            else:
                survival = 0.25
                end_exits = _open_exits(state, head, body)
    else:
        status, end_head, after_cells = _simulate_rank_action(state, path)
        if status == "ok":
            survival = 1.0
            end_exits = _open_exits(state, end_head, after_cells)
        elif status == "h2h":
            survival = 0.5
        elif status == "dive":
            survival = 0.25

    vector = [0.0] * len(FEATURE_NAMES)
    vector[12] = state["_loki_current_exits"] / 4.0
    vector[15] = split_size / max(1, length)
    vector[16] = len(path) / 3.0
    vector[17] = ((path[0] - state["face"]) % 4) / 3.0 if path else 0.0
    vector[18] = survival
    vector[22] = end_exits / 4.0
    return vector
