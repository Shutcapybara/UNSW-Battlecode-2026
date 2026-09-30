"""Fair, quota-aware target selection for the automatic unranked scrim filler.

The executor owns the API mutation and the request ledger.  This module only
chooses who and which maps to challenge, so it is straightforward to test
without credentials or a live Battlecode server.
"""


def _int_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def target_pools(cfg, ladder, team_id):
    """Return ``(field_targets, dev_targets)`` in stable, fair-rotation order.

    Field targets default to the current top ``top_n`` ladder entries.  Dev
    targets combine the configured dev list with teams currently marked
    ``dev`` by the server.  Explicit lists are useful when a server's dev flag
    is delayed or when the team wants a fixed calibration panel.
    """
    settings = cfg.get('quota_filler') or {}
    team_id = _int_id(team_id)
    configured_dev = [_int_id(x) for x in (cfg.get('team', {}).get('dev_opponents') or [])]
    configured_dev = [x for x in configured_dev if x is not None and x != team_id]
    ladder_rows = []
    for row in ladder or []:
        ident = _int_id(row.get('id')) if isinstance(row, dict) else None
        if ident is None or ident == team_id:
            continue
        rank = row.get('rank') if isinstance(row, dict) else None
        try:
            rank = int(rank)
        except (TypeError, ValueError):
            rank = 10**9
        ladder_rows.append((rank, ident, bool(row.get('dev')) if isinstance(row, dict) else False))
    ladder_rows.sort(key=lambda item: (item[0], item[1]))
    ladder_dev = [ident for _, ident, is_dev in ladder_rows if is_dev and settings.get('include_ladder_devs', True)]
    dev_targets = list(dict.fromkeys(configured_dev + ladder_dev))

    explicit_field = [_int_id(x) for x in (settings.get('field_opponents') or [])]
    explicit_field = [x for x in explicit_field if x is not None and x != team_id and x not in set(dev_targets)]
    if explicit_field:
        field_targets = list(dict.fromkeys(explicit_field))
    else:
        try:
            top_n = max(0, int(settings.get('top_n', 10)))
        except (TypeError, ValueError):
            top_n = 10
        dev_set = set(dev_targets)
        # ``top_n`` means top-N opponents, so our own team does not reduce the
        # panel when it happens to sit inside the top-N ladder ranks.
        field_targets = [ident for _, ident, is_dev in ladder_rows
                         if ident not in dev_set and not is_dev][:top_n]
    return field_targets, dev_targets


def _cursor_state(state, pool, targets, maps):
    state = dict(state or {})
    target_key = f'{pool}_target'
    map_key = f'{pool}_map'
    try:
        target = int(state.get(target_key, 0))
    except (TypeError, ValueError):
        target = 0
    try:
        map_cursor = int(state.get(map_key, 0))
    except (TypeError, ValueError):
        map_cursor = 0
    state[target_key] = target % len(targets)
    state[map_key] = map_cursor % len(maps)
    return state


def plan_batches(pool, targets, map_ids, games, batch_games=10, state=None):
    """Plan at most ``games`` one-game-per-map challenge batches.

    Batches rotate opponents and maps independently.  A batch contains
    distinct map IDs only, which matches the server endpoint's semantics and
    avoids accidentally requesting fewer games than the quota calculation
    expects.  The returned state is persisted by the executor after a live
    dispatch (and also advances in shadow mode so the plan is realistic).
    """
    targets = list(dict.fromkeys(_int_id(x) for x in (targets or [])))
    targets = [x for x in targets if x is not None]
    maps = list(dict.fromkeys(_int_id(x) for x in (map_ids or [])))
    maps = [x for x in maps if x is not None]
    try:
        games = max(0, int(games))
    except (TypeError, ValueError):
        games = 0
    try:
        batch_games = max(1, int(batch_games))
    except (TypeError, ValueError):
        batch_games = 10
    if not targets or not maps or not games:
        return [], dict(state or {})
    state = _cursor_state(state, pool, targets, maps)
    target_index = state[f'{pool}_target']
    map_cursor = state[f'{pool}_map']
    batches = []
    remaining = games
    while remaining:
        take = min(batch_games, remaining, len(maps))
        selected = [maps[(map_cursor + offset) % len(maps)] for offset in range(take)]
        opponent = targets[target_index % len(targets)]
        batches.append(dict(pool=pool, opponent=opponent, map_ids=selected, games=take))
        remaining -= take
        map_cursor = (map_cursor + take) % len(maps)
        target_index = (target_index + 1) % len(targets)
    state[f'{pool}_target'] = target_index
    state[f'{pool}_map'] = map_cursor
    state['version'] = 1
    return batches, state


def hourly_remaining(cfg, quota, pool, dispatched=0, now=None):
    """Return filler games still available after the executor's current plan.

    ``quota[pool]['used']`` is the snapshot's rolling-hour count.  ``dispatched``
    accounts for requests made earlier in this same cycle, which are not in
    that snapshot yet.  The filler intentionally uses the hourly cap rather
    than the executor's smaller experiment cap.
    """
    budget = cfg.get('budget') or {}
    hourly = budget.get('hourly_games') or {}
    current = quota.get(pool) or {}
    try:
        blocked_until = float(current.get('blocked_until') or 0)
        blocked = blocked_until > 0 and (now is None or blocked_until > float(now))
    except (TypeError, ValueError):
        return 0
    if current.get('unknown') or blocked:
        return 0
    try:
        cap = max(0, int(hourly.get(pool, 0)))
        used = max(0, int(current.get('used', 0)))
        dispatched = max(0, int(dispatched))
    except (TypeError, ValueError):
        return 0
    reserve = (cfg.get('quota_filler') or {}).get('reserve_games') or {}
    try:
        reserve = max(0, int(reserve.get(pool, 0)))
    except (TypeError, ValueError):
        reserve = 0
    return max(0, cap - used - dispatched - reserve)
