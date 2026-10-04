"""H-Q8 v1 actor-local integer features; see hq8_schema.md for unknown semantics."""
from collections import Counter, deque

UNKNOWN = -1
NAMES = (
    'round', 'rounds_remaining', 'is_queen', 'mode', 'rl_likely', 'pocket_map',
    'own_alive', 'own_seen_age', 'own_x', 'own_y', 'own_distance',
    'enemy_alive', 'enemy_seen_age', 'enemy_x', 'enemy_y', 'enemy_distance',
    'own_length', 'enemy_length', 'length_margin', 'own_visible_length_lb',
    'enemy_visible_length_lb', 'own_visible_rank', 'own_rank_exact',
    'own_split_age', 'own_enemy_heads_3', 'own_enemy_reach_lb', 'own_reach_exact',
    'own_ally_heads_2', 'own_ally_heads_3', 'own_free_cells_5',
    'own_free_cells_censored', 'own_kelp_edges', 'own_nearest_bed',
    'own_nearest_pearl', 'own_pearl_origin_known', 'sonar_decoded',
)


class Encoder:
    def __init__(self, my_id, team, width, height, unit_limit):
        self.id, self.team = my_id, team
        self.width, self.height, self.unit_limit = width, height, unit_limit
        self.queen = 0 if team == 'A' else 1
        self.last = [None, None]
        self.split_round = None
        self.round = 0

    def distance(self, a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return min(dx, self.width - dx) + min(dy, self.height - dy)

    def record_split(self):
        if self.id == self.queen:
            self.split_round = self.round

    def features(self, block):
        self.round = rnd = block['round']
        head = tuple(block['tiles'][24][:2])
        bodies = block['bodies']
        visible = Counter(b[1] for b in bodies)
        heads = {b[1]: (b[2], b[3]) for b in bodies if b[5]}
        xy_to_rc = {tuple(t[:2]): divmod(k, 7) for k, t in enumerate(block['tiles'])}
        occupied = {tuple(b[2:4]) for b in bodies}
        row = dict.fromkeys(NAMES, UNKNOWN)
        row.update(round=rnd, rounds_remaining=max(0, 500 - rnd),
                   is_queen=int(self.id == self.queen), sonar_decoded=0,
                   own_pearl_origin_known=0, own_rank_exact=0, own_reach_exact=0)
        for side, qid in enumerate((self.queen, 1 - self.queen)):
            prefix = ('own', 'enemy')[side]
            if qid in heads:
                self.last[side] = (heads[qid], rnd)
                row[prefix + '_alive'] = 1
            if self.last[side] is not None:
                xy, seen = self.last[side]
                row.update({prefix + '_seen_age': rnd - seen,
                            prefix + '_x': xy[0], prefix + '_y': xy[1],
                            prefix + '_distance': self.distance(head, xy)})
            row[prefix + '_visible_length_lb'] = visible[qid]
            if self.id == qid:
                row[prefix + '_length'] = block['length']
        if row['own_alive'] == row['enemy_alive'] == 1:
            row['mode'] = 3  # queen-race; other latent modes need confirmed death
        if self.id == self.queen:
            row['own_split_age'] = rnd - self.split_round if self.split_round is not None else rnd
        if self.queen in heads:
            qxy = heads[self.queen]
            allies = [xy for did, xy in heads.items() if did != self.queen and did % 2 == self.queen]
            enemies = [(did, xy) for did, xy in heads.items() if did % 2 != self.queen]
            row['own_enemy_heads_3'] = sum(self.distance(qxy, xy) <= 3 for _, xy in enemies)
            row['own_enemy_reach_lb'] = sum(self.distance(qxy, xy) <= 1 + (visible[did] + 3) // 4
                                            for did, xy in enemies)
            row['own_ally_heads_2'] = sum(self.distance(qxy, xy) <= 2 for xy in allies)
            row['own_ally_heads_3'] = sum(self.distance(qxy, xy) <= 3 for xy in allies)
            if self.id == self.queen:
                row['own_visible_rank'] = 1 + sum(n > block['length'] for did, n in visible.items()
                                                  if did % 2 == self.queen and did != self.queen)
            for name, test in (('bed', lambda t: t[3] >= 0), ('pearl', lambda t: t[2] > 0)):
                distances = [self.distance(qxy, tuple(t[:2])) for t in block['tiles'] if test(t)]
                row['own_nearest_' + name] = min(distances) if distances else UNKNOWN
            start = xy_to_rc[qxy]
            def edge(rc, dr):
                r, c = rc
                return (block['H'][r][c], block['V'][r][c + 1],
                        block['H'][r + 1][c], block['V'][r][c])[dr]
            row['own_kelp_edges'] = sum(edge(start, d) == 'w' for d in range(4))
            seen = {start}
            queue = deque([(start, 0)])
            free, censored = 0, 0
            while queue:
                (r, c), depth = queue.popleft()
                if depth == 5:
                    continue
                for dr, (dy, dx) in enumerate(((-1, 0), (0, 1), (1, 0), (0, -1))):
                    e = edge((r, c), dr)
                    if e == 'w':
                        continue
                    rr, cc = r + dy, c + dx
                    if e != '.' or not (0 <= rr < 7 and 0 <= cc < 7):
                        censored = 1
                        continue
                    rc = (rr, cc)
                    if rc in seen or tuple(block['tiles'][rr * 7 + cc][:2]) in occupied:
                        continue
                    seen.add(rc)
                    free += 1
                    queue.append((rc, depth + 1))
            row['own_free_cells_5'] = free
            row['own_free_cells_censored'] = censored
        return [row[name] for name in NAMES]
