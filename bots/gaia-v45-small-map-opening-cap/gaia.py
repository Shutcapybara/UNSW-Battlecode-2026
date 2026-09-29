"""Gaia coordination and safety layer.

Gaia keeps the Fenrir planner, but adds a small deterministic macro layer:

* the first 100 rounds use stable, ID-based exploration lanes;
* only a deterministic minority of dragons may take blind portals early;
* a pearl is rejected when the post-collection body has no known escape room;
* fertile, safe bed clusters become breeding areas instead of accidental
  traffic circles; and
* one checked status packet per few turns carries the breeding centre, role,
  and parent-alive bit over sonar.

The layer is deliberately advisory.  Fenrir's route search, threat model,
newborn handoff, and crown policy remain the source of truth for legal moves.
"""
from collections import defaultdict

import world as w
import comms
import tactics as tx
import separation
import density
from params import P


MODE = ["explorer"]  # explorer, portal, or breeder
BREED_CELL = [-1]
BREED_SCORE = [0.0]
LAST_HEAD = [-1]
STALL_TURNS = [0]
LAST_MOVE = [-1]
LAST_BREED_SCAN = [-999]
DEATH_PEARLS = set()
PORTAL_USES = {}
BED_OBS = defaultdict(int)
PEARL_OBS = defaultdict(int)
REMOTE = {}  # sender -> (cell, role, flags, round)


def init():
    MODE[0] = "explorer"
    BREED_CELL[0] = -1
    BREED_SCORE[0] = 0.0
    LAST_HEAD[0] = -1
    STALL_TURNS[0] = 0
    LAST_MOVE[0] = -1
    LAST_BREED_SCAN[0] = -999
    DEATH_PEARLS.clear()
    PORTAL_USES.clear()
    BED_OBS.clear()
    PEARL_OBS.clear()
    REMOTE.clear()


def _team_offset():
    return 0 if w.TEAM == "A" else 1


def preferred_direction():
    """Return a mirrored absolute lane for the current starting side.

    Queen of Spades is xy-symmetric.  Giving team B the same absolute lane as
    team A made an apparently deterministic opening asymmetric; rotating B by
    180 degrees preserves the intended separation under the map symmetry.
    """
    raw = (w.ME + _team_offset()) % 4
    return (raw + 2) % 4 if w.TEAM == "B" else raw


def _topology(cell, depth=3, cap=80):
    """Return (reachable cells, branch points, immediate exits).

    Unknown terrain is intentionally not counted as room here.  Breeding
    areas must have a visible escape route, not merely an optimistic one.
    """
    dist = {cell: 0}
    q = [cell]
    branches = 0
    qi = 0
    while qi < len(q) and len(q) < cap:
        c = q[qi]
        qi += 1
        edges = [n for n in w.dest(c) if n >= 0 and n != c]
        if len(set(edges)) >= 3:
            branches += 1
        if dist[c] >= depth:
            continue
        for n in edges:
            if n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
                if len(q) >= cap:
                    break
    exits = len({n for n in w.dest(cell) if n >= 0 and n != cell})
    return len(dist), branches, exits


def _safe_area(cell):
    area, branches, exits = _topology(cell, depth=3, cap=80)
    return exits >= 2 and (area >= P.get("breed_min_area", 8) or branches >= 1)


def _observe_resources():
    """Accumulate local bed/pearl evidence without treating one sighting as a
    global spawn-rate estimate.

    A cell observed with a countdown is evidence of a renewable bed.  Repeated
    due/pearl observations raise its local score; stale cells decay by pruning
    the bounded dictionaries below.
    """
    for x, y, pearl, countdown in w.io_tiles():
        cell = y * w.W + x
        if countdown >= 0:
            BED_OBS[cell] += 1
        if pearl:
            PEARL_OBS[cell] += 1
    if w.RND % 32 == 0:
        # Keep this state bounded on large toroidal maps.
        for table in (BED_OBS, PEARL_OBS):
            for cell in list(table):
                table[cell] = max(0, table[cell] - 1)
                if not table[cell]:
                    del table[cell]


def _choose_breeding_area():
    if w.RND < P.get("breed_from", 70):
        return -1, 0.0
    # Big Empty can expose thousands of renewable tiles.  Only inspect a
    # bounded, evidence-ranked sample and rescan periodically; a breeding
    # detector must never make every dragon spend quadratic time over the map.
    if w.RND - LAST_BREED_SCAN[0] < P.get("breed_scan_period", 8):
        return BREED_CELL[0], BREED_SCORE[0]
    LAST_BREED_SCAN[0] = w.RND
    evidence = set(BED_OBS)
    evidence.update(w.spawn)
    beds = [c for c in evidence if w.bed[c] == 2]
    beds.sort(key=lambda c: (-BED_OBS.get(c, 0), -PEARL_OBS.get(c, 0), c))
    beds = beds[:P.get("breed_candidate_cap", 64)]
    if len(beds) < P.get("breed_min_beds", 3):
        return -1, 0.0
    best_cell, best_score = -1, 0.0
    radius = P.get("breed_radius", 4)
    for centre in sorted(beds):
        cluster = [c for c in beds if w.tdist(c, centre) <= radius]
        if len(cluster) < P.get("breed_min_beds", 3) or not _safe_area(centre):
            continue
        score = 0.0
        for c in cluster:
            due = w.spawn.get(c, w.RND + P.get("breed_due_horizon", 60))
            due_weight = 1.0 if due <= w.RND + P.get("breed_due_horizon", 60) else 0.25
            score += due_weight + min(3, BED_OBS.get(c, 0)) * 0.5
            score += min(2, PEARL_OBS.get(c, 0)) * 0.35
        # Stable tie-breaking prevents the area from moving as reports arrive.
        if score > best_score or (score == best_score and centre < best_cell):
            best_cell, best_score = centre, score
    if best_score < P.get("breed_min_score", 4.0):
        return -1, 0.0
    return best_cell, best_score


def observe():
    """Refresh deterministic role, stall, and breeding-area state."""
    if LAST_HEAD[0] == w.HEAD:
        STALL_TURNS[0] += 1
    else:
        STALL_TURNS[0] = 0
    LAST_HEAD[0] = w.HEAD
    _observe_resources()

    cell, score = _choose_breeding_area()
    if cell >= 0:
        BREED_CELL[0], BREED_SCORE[0] = cell, score

    scout = ((w.ME + _team_offset()) % max(2, P.get("portal_scout_stride", 6)) == 0)
    breeder = (BREED_CELL[0] >= 0 and
               (w.ME + _team_offset()) % max(2, P.get("breeder_stride", 8)) == 0 and
               w.UNITS < P.get("breed_unit_cap", 40) and
               w.RND >= P.get("breed_from", 70))
    MODE[0] = "breeder" if breeder else "portal" if scout else "explorer"
    if parent_dead() and not breeder:
        # A missing parent is a coordination event, not a reason to wait in
        # the old split pocket. The action bonus below pushes the child away
        # from the recorded origin while retaining normal threat checks.
        MODE[0] = "explorer"


def hear(sender, cell, role, flags, rnd):
    """Consume a checked Gaia status packet received through sonar."""
    if sender == (w.ME & 4095) or rnd > w.RND:
        return
    REMOTE[sender] = (cell, role, flags, rnd)
    if role == 2 and _safe_area(cell):
        # Remote discovery may establish an area before this dragon has seen
        # its beds.  It is still only a target until local safety is confirmed.
        if BREED_CELL[0] < 0:
            BREED_CELL[0] = cell


def is_breeder():
    return MODE[0] == "breeder" and BREED_CELL[0] >= 0


def is_portal_scout():
    return MODE[0] == "portal"


def production_allowed():
    """Keep the opening growth burst, with a tiny-arena survival cap.

    On a compact arena, an unlimited first-100 split burst creates many short
    bodies before an opponent's heads can be seen reliably. The cap is based
    on map area rather than a named map, so the policy remains general.
    """
    if is_breeder():
        return True
    if w.RND < P.get("opening_until", 100):
        if w.W * w.H <= P.get("tiny_opening_area", 400):
            return w.UNITS < P.get("tiny_opening_unit_cap", 6)
        return True
    if w.W * w.H >= P.get("large_map_area", 2000):
        return w.UNITS < P.get("large_map_unit_cap", 48)
    return True


def combat_allowed(enemy_id):
    """Do not initiate marginal head trades during the growth window."""
    if w.RND >= P.get("opening_until", 100):
        return True
    if enemy_id not in w.elen:
        return False
    enemy_length = w.elen[enemy_id] + (P.get("cut_extra", 1) if enemy_id in w.cut else 0)
    return w.LEN >= enemy_length + P.get("early_combat_margin", 2)


def contact_penalty(cell):
    """Discourage enemy and ally head contact throughout the game.

    The opening uses a strong margin; later rounds retain a smaller buffer so
    growth does not turn into a dense self-trading swarm.
    """
    early = w.RND < P.get("opening_until", 100)
    enemy = min((w.tdist(cell, enemy_cell) for enemy_cell, _ in w.enemy_heads),
                default=999)
    ally = min((w.tdist(cell, ally_cell) for ally_cell, _ in w.ally_heads),
               default=999)
    base = P.get("opening_contact_penalty", 18.0) if early else P.get("late_contact_penalty", 5.0)
    score = base if enemy <= 1 else base * 0.65 if enemy <= 2 else base * 0.25 if enemy <= 3 else 0.0
    ally_base = P.get("ally_contact_penalty", 7.0)
    if ally <= 1:
        score += ally_base
    elif ally <= 2:
        score += ally_base * 0.35
    return score


def target_goal():
    if is_breeder() and w.tdist(w.HEAD, BREED_CELL[0]) > 1:
        return BREED_CELL[0]
    return -1


def known_death_pearl(cell):
    return cell in DEATH_PEARLS


def pearl_escape_safe(body_after):
    """Require a known exit and enough room after a pearl is collected."""
    if tx.exits(body_after) < 1:
        return False
    required = max(P["min_area"], len(body_after) + P.get("pearl_escape_slack", 2))
    return tx.flood(body_after, required, 0) >= required


def reject_unsafe_pearl(path, body_after):
    """Remember visible death pearls so future route searches stop valuing them."""
    for d in path:
        n = w.dest(w.HEAD)[d] if d == path[0] else -1
        if n >= 0 and w.pearls.get(n) == w.RND:
            DEATH_PEARLS.add(n)
    # A multi-step path can reach more than one visible pearl.  The exact
    # simulated cells are cheap to recover and keep the rejection precise.
    st, nb, _, _ = tx.sim(path, w.body)
    if st != "dead":
        for n in nb:
            if w.pearls.get(n) == w.RND:
                DEATH_PEARLS.add(n)
    return False


def safe_move(path, body_after, eaten):
    if not eaten:
        return True
    if pearl_escape_safe(body_after):
        return True
    return reject_unsafe_pearl(path, body_after)


def can_portal(first_dir):
    """Blind portal dives are a role assignment, not a team-wide lottery."""
    if w.dest(w.HEAD)[first_dir] != -3:
        return True
    if w.RND < P.get("portal_scout_from", 100):
        return False
    if is_portal_scout():
        return True
    return w.RND >= P.get("portal_general_from", 180)


def portal_bonus(first_dir):
    if w.dest(w.HEAD)[first_dir] != -3:
        return 0.0
    last = PORTAL_USES.get((w.HEAD, first_dir), -999)
    repeat = P.get("portal_repeat_cooldown", 20) - (w.RND - last)
    penalty = P.get("portal_repeat_penalty", 4.0) if repeat > 0 else 0.0
    return (P.get("portal_scout_bonus", 5.0) if is_portal_scout() else 0.0) - penalty


def action_bonus(cell, first_dir):
    """Coordinate lanes, breeding traffic, and anti-stall movement."""
    score = 0.0
    if w.RND < P.get("opening_until", 100) and not w.pearls:
        preferred = preferred_direction()
        score += P.get("opening_lane_bonus", 1.6) if first_dir == preferred else -0.15
    elif w.RND >= P.get("opening_until", 100) and not is_breeder():
        # Keep a weak deterministic sector preference after growth so a full
        # team does not repeatedly select the same nearest bed corridor.
        preferred = preferred_direction()
        score += P.get("explore_lane_bonus", 0.35) if first_dir == preferred else -0.03

    # On compact maps, use exchanged density only after the growth window and
    # only when no enemy head is visible. Big Empty already has a successful
    # saturated exploration policy, so leave that large-map path unchanged.
    allies, enemies, confidence = density.field(cell)
    if (w.RND >= P.get("opening_until", 100)
            and w.W * w.H < P.get("large_map_area", 2000)
            and not w.enemy_heads
            and confidence >= P.get("density_spread_confidence", 0.20)):
        crowd = max(0.0, allies - 1.0) / max(1.0, P.get("density_spread_norm", 4.0))
        enemy = enemies / max(1.0, P.get("density_spread_enemy_norm", 2.0))
        score += P.get("density_spread_weight", 0.55) * (
            max(-1.0, min(1.0, 1.0 - crowd)) -
            P.get("density_spread_enemy_weight", 0.65) * min(1.0, enemy))

    if is_breeder():
        before = w.tdist(w.HEAD, BREED_CELL[0])
        after = w.tdist(cell, BREED_CELL[0])
        score += P.get("breed_route_bonus", 1.4) * (before - after)
        if after <= P.get("breed_radius", 4):
            score += P.get("breed_local_bonus", 0.5)
    elif BREED_CELL[0] >= 0:
        before = w.tdist(w.HEAD, BREED_CELL[0])
        after = w.tdist(cell, BREED_CELL[0])
        if before <= P.get("breed_radius", 4) + 2 and after > before:
            score += P.get("breed_leave_bonus", 1.3)

    if parent_dead():
        origin = separation.ORIGIN
        if origin >= 0:
            before = w.tdist(w.HEAD, origin)
            after = w.tdist(cell, origin)
            score += P.get("parent_dead_push", 2.0) * max(-2, min(2, after - before))

    if STALL_TURNS[0] >= P.get("stall_turns", 3):
        score += P.get("stall_escape_bonus", 2.5)
        score -= P.get("stall_revisit_penalty", 0.3) * w.visits[cell]
    return score + portal_bonus(first_dir)


def split_bonus(child_len, child_room, parent_room):
    """Reward a roomier child placement and local breeding production."""
    score = 0.25 * min(child_room, 12) + 0.10 * min(parent_room, 20)
    if child_len > P["child"] and child_room >= P.get("child_room_bonus", 7):
        score += P.get("adaptive_child_bonus", 1.0)
    if is_breeder():
        score += P.get("breed_split_bonus", 2.0)
    return score


def split_legal(n):
    return (2 <= n < w.LEN and w.LEN - n >= 2 and w.UNITS < w.LIMIT)


def record_portal(path, status):
    if path and status == "dive":
        PORTAL_USES[(w.HEAD, path[0])] = w.RND
    LAST_MOVE[0] = w.RND


def parent_dead():
    """A child treats a missing parent status as a normal leave-area signal."""
    parent = separation.PARENT_ID
    if parent < 0:
        return False
    if separation.START < 0 or w.RND - separation.START < 2:
        return False
    row = REMOTE.get(parent)
    return row is None or w.RND - row[3] > P.get("parent_status_ttl", 6)


def decorate_messages(messages):
    """Add one low-bandwidth status packet while preserving critical sonar.

    Bit 0 means the sender is alive this round; bit 1 asks nearby
    non-breeders to leave the known breeding area.  A child can therefore
    distinguish a live parent report from a stale/missing parent and adapt its
    separation objective without trusting unauthenticated foreign payloads.
    """
    if w.RND % max(1, P.get("status_period", 3)):
        return messages
    role = 2 if is_breeder() else 1 if is_portal_scout() else 0
    centre = BREED_CELL[0] if BREED_CELL[0] >= 0 else w.HEAD
    flags = 1  # parent/status sender is alive now
    if MODE[0] != "breeder" and BREED_CELL[0] >= 0:
        flags |= 2  # leave the breeding area
    packet = comms.guidance_packet(w.ME, centre, w.RND, role, flags)
    if packet is None:
        return messages
    dirs = tuple(w.DIRS[(w.ME + w.RND + k) % 4] for k in range(4))
    for direction in dirs:
        current = messages.get(direction)
        if current is None or comms.unpack(current)[0] == comms.T_FOOD:
            messages[direction] = packet
            break
    else:
        # Keep the packet moving even when all rays are occupied by relays.
        messages[dirs[0]] = packet
    return messages
