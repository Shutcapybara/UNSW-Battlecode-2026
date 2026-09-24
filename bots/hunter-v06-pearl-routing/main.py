"""Python Hunter: persistent observations, conservative combat and portal trips."""
from collections import deque
import sys

DIR = 'NESW'
DX = (0, 1, 0, -1)
DY = (-1, 0, 1, 0)
MOVE_ASIDE = 1146242894
TAG = 0xA7 << 56


def read(stream):
    for line in stream:
        words = line.split('#', 1)[0].split()
        if words:
            return words
    raise EOFError


class Bot:
    def __init__(self, stream):
        self.stream = stream
        self.id = int(read(stream)[1])
        self.team = read(stream)[1]
        _, w, h = read(stream)
        self.w, self.h = int(w), int(h)
        self.limit = int(read(stream)[1])
        self.n = self.w * self.h
        self.neighbors = [[self.pos(p % self.w + DX[d], p // self.w + DY[d])
                           for d in range(4)] for p in range(self.n)]
        self.edges = [['.'] * 4 for _ in range(self.n)]
        self.visits = [0] * self.n
        self.teammates = {}
        self.enemies = {}
        self.portals = {}
        self.route = ''
        self.inside = False
        self.trip_portal = None
        self.trip_entry = None
        self.expected = (-1, -1)

    def pos(self, x, y):
        return (y % self.h) * self.w + x % self.w

    def edge_at(self, p, d):
        return (self.pos(p % self.w + (d == 1), p // self.w + (d == 2)), d % 2 == 0)

    def set_edge(self, p, d, symbol):
        self.edges[p][d] = symbol

    def update(self):
        self.round = int(read(self.stream)[1])
        self.facing = DIR.index(read(self.stream)[1])
        self.length = int(read(self.stream)[1])
        self.units = int(read(self.stream)[1])
        count = int(read(self.stream)[1])
        self.asked = False
        for _ in range(count):
            message = int(read(self.stream)[0])
            self.asked |= message == MOVE_ASIDE
            if message >> 56 == 0xA7:
                ident, size = (message >> 50) & 63, (message >> 38) & 4095
                x, y = (message >> 32) & 63, (message >> 26) & 63
                age = (self.round - ((message >> 10) & 65535)) % 65536
                if ident != self.id and age <= 20 and x < self.w and y < self.h:
                    self.teammates[ident] = (size, y * self.w + x, self.round - age)
        self.visible = set()
        self.pearls = set()
        self.countdowns = {}
        self.occupied = set()
        self.own = set()
        self.friends = {}
        self.heads = {}
        self.head_facing = {}
        self.sizes = {}
        fields = read(self.stream)
        self.echoes = (0,) * 5
        if fields[0] == 'ECHOES':
            self.echoes = tuple(map(int, fields[1:]))
            fields = read(self.stream)
        window = []
        for i in range(49):
            if i:
                fields = read(self.stream)
            x, y, pearl, countdown = map(int, fields)
            p = self.pos(x, y)
            window.append(p)
            self.visible.add(p)
            if pearl:
                self.pearls.add(p)
            if countdown >= 0:
                self.countdowns[p] = countdown
        self.head = window[24]
        self.visits[self.head] += 1
        friendly_sizes = {}
        for _ in range(int(read(self.stream)[1])):
            team, ident, x, y, facing, is_head = read(self.stream)
            ident, p = int(ident), self.pos(int(x), int(y))
            self.occupied.add(p)
            self.pearls.discard(p)
            if team == self.team and ident == self.id:
                self.own.add(p)
            elif team == self.team:
                friendly_sizes[ident] = friendly_sizes.get(ident, 0) + 1
            else:
                self.sizes[ident] = self.sizes.get(ident, 0) + 1
            if int(is_head):
                (self.friends if team == self.team else self.heads)[p] = ident
                self.head_facing[p] = DIR.index(facing)
        for ident in self.enemies.keys() | self.sizes.keys():
            self.enemies[ident] = max(self.sizes.get(ident, 0), self.enemies.get(ident, 0) - 1)
        for ident, size in friendly_sizes.items():
            old = self.teammates.get(ident, (0, -1, -1))
            self.teammates[ident] = (max(size, old[0]), old[1], self.round)
        for row in range(8):
            for col, symbol in enumerate(read(self.stream)):
                if row < 7:
                    self.set_edge(window[row * 7 + col], 0, symbol)
                if row > 0:
                    self.set_edge(window[(row - 1) * 7 + col], 2, symbol)
        for row in range(7):
            for col, symbol in enumerate(read(self.stream)):
                if col < 7:
                    self.set_edge(window[row * 7 + col], 3, symbol)
                if col > 0:
                    self.set_edge(window[row * 7 + col - 1], 1, symbol)
        self.portals = {}
        for p, edges in enumerate(self.edges):
            for d, symbol in enumerate(edges):
                if symbol not in ('.', 'w'):
                    ends = self.portals.setdefault(symbol, [])
                    edge = self.edge_at(p, d)
                    if edge not in ends:
                        ends.append(edge)
        self.danger_cache = None
        self.friend_dist = {}
        self.friend_routes = None

    def destination(self, p, d, body=True, portal=False):
        symbol = self.edges[p][d]
        if symbol == 'w':
            return -1
        q = self.neighbors[p][d]
        if symbol != '.':
            if not portal:
                return -1
            ends = self.portals.get(symbol, [])
            if len(ends) != 2:
                return -2
            entry = self.edge_at(p, d)
            out = ends[1] if ends[0] == entry else ends[0]
            if entry[1] != out[1]:
                return -2
            q = self.pos(out[0] % self.w - (d == 3), out[0] // self.w - (d == 0))
        if q not in self.visible:
            return -2
        return -1 if body and q in self.occupied else q

    def active_team(self):
        return [(ident, state[0]) for ident, state in self.teammates.items()
                if self.round - state[2] <= 20]

    def growth(self):
        if any(size > self.length or (size == self.length and ident < self.id)
               for ident, size in self.active_team()):
            return False
        return self.round >= 450 or (self.round >= 400 and
            max(self.enemies.values(), default=0) + 2 >= self.length)

    def explore_portals(self):
        return self.units >= 4 and any(size > self.length for _, size in self.active_team())

    def threats(self):
        if self.danger_cache is None:
            danger = set(self.heads)
            for p in self.heads:
                for d in range(4):
                    q = self.destination(p, d, False, True)
                    if q < 0:
                        continue
                    danger.add(q)
                    for e in range(4):
                        r = self.destination(q, e, False, True)
                        if r >= 0:
                            danger.add(r)
            self.danger_cache = danger
        return self.danger_cache

    def distance(self, p, q):
        dx, dy = abs(p % self.w - q % self.w), abs(p // self.w - q // self.w)
        return min(dx, self.w - dx) + min(dy, self.h - dy)

    def nearest_friend(self, p):
        if p not in self.friend_dist:
            self.friend_dist[p] = min((self.distance(p, q) for q in self.friends
                                      if q != self.head), default=99)
        return self.friend_dist[p]

    def owns_pearl(self, p, distance):
        # Compare actual visible routes: a teammate behind kelp cannot claim a
        # pearl just because its wrapped Manhattan distance is smaller.
        if self.friend_routes is None:
            self.friend_routes = {}
            for head, ident in self.friends.items():
                if head == self.head:
                    continue
                routes, queue = {head: 0}, deque([head])
                while queue:
                    q = queue.popleft()
                    for d in range(4):
                        nxt = self.destination(q, d)
                        if nxt >= 0 and nxt not in routes:
                            routes[nxt] = routes[q] + 1
                            queue.append(nxt)
                for q, cost in routes.items():
                    self.friend_routes[q] = min(self.friend_routes.get(q, (9999, 9999)), (cost, ident))
        return self.friend_routes.get(p, (9999, 9999)) >= (distance, self.id)

    def initial_trip(self):
        return ('', self.trip_portal if self.inside else None,
                self.trip_entry if self.inside else None, (self.head,), (),
                int(self.inside), 0, 0)

    def advance(self, state, d, danger):
        moves, portal, entry, trail, collected, stage, after, reward = state
        p = trail[-1]
        q = self.destination(p, d, False, True)
        if q < 0 or q in danger:
            return None
        step = len(moves) + 1
        pearl = q not in collected and (q in self.pearls or self.countdowns.get(q, 9999) < step)
        grown = self.length + len(collected) + pearl
        if q in self.occupied and (q not in self.own or step <= grown):
            return None
        if any(v == q and step - i <= grown for i, v in enumerate(trail)):
            return None
        symbol = self.edges[p][d]
        if symbol != '.':
            if stage == 0:
                portal, entry, stage = symbol, self.edge_at(p, d), 1
            elif stage == 1 and symbol == portal and self.edge_at(p, d) != entry:
                stage = 2
            else:
                return None
        elif stage == 2:
            after += 1
        if pearl:
            collected += (q,)
            reward += stage != 0
        return (moves + DIR[d], portal, entry, trail + (q,), collected, stage, after, reward)

    def plan_trip(self, danger):
        if not any(len(ends) == 2 for ends in self.portals.values()):
            return ''
        beam, best, reward = [self.initial_trip()], '', -1
        explore = self.explore_portals()
        for _ in range(18):
            candidates = []
            for state in beam:
                for offset in range(4):
                    nxt = self.advance(state, (offset + self.id + self.round // 8) % 4, danger)
                    if nxt is None:
                        continue
                    if nxt[5] == 2 and nxt[6] >= 2:
                        if self.inside:
                            return nxt[0]
                        if (nxt[7] > 0 or explore) and nxt[7] > reward:
                            best, reward = nxt[0], nxt[7]
                    else:
                        candidates.append(nxt)
            candidates.sort(key=lambda s: -s[7])
            retained, beam = {}, []
            for nxt in candidates:
                key = (nxt[3][-1], nxt[5])
                retained[key] = retained.get(key, 0) + 1
                if retained[key] <= 4:
                    beam.append(nxt)
                    if len(beam) == 256:
                        break
            if not beam:
                break
        return best

    def unmatched(self, danger):
        paths, queue = {self.head: ''}, deque([self.head])
        while queue:
            p = queue.popleft()
            for offset in range(4):
                d = (offset + self.id + self.round // 8) % 4
                symbol = self.edges[p][d]
                if symbol not in ('.', 'w') and len(self.portals.get(symbol, [])) == 1:
                    return paths[p] + DIR[d]
                q = self.destination(p, d)
                if q >= 0 and q not in paths and q not in danger:
                    paths[q] = paths[p] + DIR[d]
                    queue.append(q)
        return ''

    def portal_action(self):
        danger = self.threats()
        if self.expected != (self.head, self.round):
            self.route = ''
        state = self.initial_trip()
        for move in self.route:
            state = self.advance(state, DIR.index(move), danger)
            if state is None:
                self.route = ''
                break
        if not self.route:
            self.route = self.plan_trip(danger)
        if not self.route and self.explore_portals():
            self.route = self.unmatched(danger)
        if not self.route:
            return None
        d = DIR.index(self.route[0])
        symbol = self.edges[self.head][d]
        if symbol != '.':
            if not self.inside:
                self.trip_portal, self.trip_entry = symbol, self.edge_at(self.head, d)
            self.inside = not self.inside
        self.expected = (self.destination(self.head, d, False, True), self.round + 1)
        self.route = self.route[1:]
        return 'MOVE ' + DIR[d]

    def attack_path(self):
        # Never use stale sizes, walk through an unsuitable head, or chase a
        # target beyond the current movement budget. Every prefix stays clear.
        paths, queue = {self.head: ''}, deque([self.head])
        while queue:
            p = queue.popleft()
            if len(paths[p]) >= self.length - 1:
                continue
            for offset in range(4):
                d = (offset + self.id + self.round) % 4
                q = self.destination(p, d, False)
                if q < 0 or q in paths:
                    continue
                path = paths[p] + DIR[d]
                if q in self.heads:
                    if self.sizes.get(self.heads[q], 0) > self.length:
                        return path
                    continue
                if q in self.occupied:
                    continue
                paths[q] = path
                queue.append(q)
        return ''

    def signal(self):
        p = self.head
        for distance in range(1, 4):
            p = self.destination(p, self.facing, False)
            if p < 0:
                return False
            if p in self.occupied:
                return (distance >= 2 and p in self.friends and
                        self.head_facing[p] == (self.facing + 2) % 4 and self.id < self.friends[p])
        return False

    def spread_move(self, urgent=False):
        best, score = -1, -10**9
        for offset in range(4):
            d = (offset + self.id + self.round // 8) % 4
            q = self.destination(self.head, d)
            if q < 0:
                continue
            exits = sum(self.destination(q, e) >= 0 for e in range(4))
            value = self.nearest_friend(q) * (1000 if urgent else 100) + exits * 8 - self.visits[q] * 3
            value -= 20 * (d == (self.facing + 2) % 4)
            if value > score:
                best, score = d, value
        return best

    def survival_move(self):
        best, score = -1, -10**9
        danger = self.threats()
        for d in range(4):
            if self.edges[self.head][d] != '.':
                continue
            state = self.advance(self.initial_trip(), d, danger)
            if state is None:
                continue
            q = state[3][-1]
            exits = sum(self.edges[q][e] == '.' and self.advance(state, e, danger) is not None
                        for e in range(4))
            value = exits * 1000 + self.nearest_friend(q) - self.visits[q]
            if value > score:
                best, score = d, value
        return best

    def escape(self):
        move = self.survival_move()
        if move < 0:
            move = self.spread_move(True)
        if move >= 0:
            return 'MOVE ' + DIR[move]
        return 'SPLIT 2' if self.length >= 4 and self.units < self.limit else 'MOVE N'

    def forage(self, growth=False):
        distance, first, queue = {self.head: 0}, {}, deque([self.head])
        pearl, explore, pearl_score, explore_score = -1, -1, -10**9, -10**9
        danger = self.threats() if growth else set()
        while queue:
            p = queue.popleft()
            if p != self.head:
                if growth:
                    score = -distance[p] * 100 + min(self.nearest_friend(p), 10) - self.visits[p] + 20
                    eligible = p in self.pearls or self.countdowns.get(p, 9999) < distance[p]
                else:
                    score = self.nearest_friend(p) * 100 - distance[p] * 8 - self.visits[p] * 3
                    eligible = p in self.pearls and self.owns_pearl(p, distance[p])
                # Reproduction depends on collecting quickly. Keep the strong
                # separation score for exploration, but price pearl travel first.
                food_score = score if growth else -distance[p] * 100 + min(self.nearest_friend(p), 10) - self.visits[p]
                if eligible and food_score > pearl_score:
                    pearl, pearl_score = p, food_score
                if score > explore_score:
                    explore, explore_score = p, score
            for offset in range(4):
                d = offset if growth else (offset + self.id + self.round // 8) % 4
                q = self.destination(p, d)
                if q < 0 or q in distance or q in danger:
                    continue
                if growth and not any((r := self.destination(q, e)) >= 0 and r != p and r not in danger
                                      for e in range(4)):
                    continue
                distance[q] = distance[p] + 1
                first[q] = d if p == self.head else first[p]
                queue.append(q)
        target = pearl if pearl >= 0 else (-1 if growth else explore)
        if target >= 0:
            return 'MOVE ' + DIR[first[target]]
        if growth:
            return self.escape()
        if self.length >= 4 and self.units < self.limit:
            return 'SPLIT ' + str(self.length - 2)
        for d in range(4):
            if self.destination(self.head, d) == -2:
                return 'MOVE ' + DIR[d]
        return 'MOVE N'

    def body(self, signal):
        portal = self.portal_action()
        if portal:
            return portal
        if self.inside:
            return self.escape()
        if self.growth():
            return self.forage(True)
        if self.units >= 3:
            attack = self.attack_path()
            if attack:
                return 'MOVE ' + attack
        if self.asked:
            move = self.spread_move(True)
            if move >= 0:
                return 'MOVE ' + DIR[move]
        if self.length >= 4 and self.units < self.limit:
            return 'SPLIT 2'
        if signal and self.destination(self.head, self.facing) >= 0:
            return 'MOVE ' + DIR[self.facing]
        return self.forage()

    def action(self):
        signal = self.signal()
        action = self.body(signal)
        status = TAG | ((self.id & 63) << 50) | ((self.length & 4095) << 38) | ((self.head % self.w) << 32) | ((self.head // self.w) << 26) | ((self.round & 65535) << 10)
        return '\n'.join([action] + [f'SONAR {DIR[d]} {MOVE_ASIDE if signal and d == self.facing else status}'
                                    for d in range(4)] + ['ENDTURN'])


def main():
    try:
        bot = Bot(sys.stdin)
        while True:
            bot.update()
            print(bot.action(), flush=True)
    except EOFError:
        pass


if __name__ == '__main__':
    main()
