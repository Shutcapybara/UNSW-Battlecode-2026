"""Leviathan: observe -> remember -> enumerate -> evaluate -> act.

Fresh Python implementation. Kraken informed protocol/geometry and budget
choices; no imports or writes to other bot lineages. All searches are bounded.
"""
import sys
from weights import PARAMS as P

DIRS = 'NESW'


def read():
    while True:
        line = sys.stdin.readline()
        if not line:
            return []
        words = line.partition('#')[0].split()
        if words:
            return words


class Bot:
    def __init__(self, ident, team, width, height, limit):
        self.id, self.team = ident, team
        self.w, self.h, self.n, self.limit = width, height, width * height, limit
        self.edges = {}  # canonical north/west edges; '.' / 'w' / portal id
        self.portals = {}
        self.graph = {}
        self.seen, self.pearls, self.beds, self.visits = {}, {}, {}, {}
        self.reports = {}
        self.body = []  # head first; simulated after every committed action
        self.round = 0
        self.length = 3
        self.units = 1
        self.head = 0
        self.first = True

    def neighbor(self, c, d):
        x, y = c % self.w, c // self.w
        return (((y - 1) % self.h) * self.w + x,
                y * self.w + (x + 1) % self.w,
                ((y + 1) % self.h) * self.w + x,
                y * self.w + (x - 1) % self.w)[d]

    def key(self, c, d):
        if d == 0:
            return c
        if d == 2:
            return self.neighbor(c, 2)
        if d == 3:
            return self.n + c
        return self.n + self.neighbor(c, 1)

    def learn(self, key, token):
        if self.edges.get(key) == token:
            return
        self.edges[key] = token
        self.graph.clear()
        if token not in ('.', 'w'):
            ends = self.portals.setdefault(token, [])
            if key not in ends:
                ends.append(key)

    def destinations(self, c):
        cached = self.graph.get(c)
        if cached is not None:
            return cached
        out = []
        for d in range(4):
            key = self.key(c, d)
            token = self.edges.get(key)
            if token == '.':
                out.append(self.neighbor(c, d))
            elif token is None or token == 'w':
                out.append(-1)
            else:
                ends = self.portals.get(token, [])
                if len(ends) != 2:
                    out.append(-1)
                else:
                    partner = ends[0] if ends[1] == key else ends[1]
                    cell = partner % self.n
                    # Direction is preserved through a portal; endpoints have
                    # matching orientations, as required by the map format.
                    out.append(cell if d in (1, 2) else self.neighbor(cell, d))
        self.graph[c] = tuple(out)
        return self.graph[c]

    def observe(self, tiles, parts, horizontal, vertical, messages):
        self.head = int(tiles[24][1]) * self.w + int(tiles[24][0])
        hx, hy = self.head % self.w, self.head // self.w
        for r, row in enumerate(horizontal):
            for col, token in enumerate(row):
                self.learn(((hy - 3 + r) % self.h) * self.w + (hx - 3 + col) % self.w, token)
        for r, row in enumerate(vertical):
            for col, token in enumerate(row):
                self.learn(self.n + ((hy - 3 + r) % self.h) * self.w + (hx - 3 + col) % self.w, token)
        self.visible = set()
        for x, y, pearl, countdown in tiles:
            c = int(y) * self.w + int(x)
            self.visible.add(c)
            self.seen[c] = self.round
            if pearl == '1':
                self.pearls[c] = self.round
            else:
                self.pearls.pop(c, None)
            if int(countdown) >= 0:
                self.beds[c] = self.round + int(countdown)
        self.occupied, self.enemies, self.allies = {}, {}, {}
        mine = {}
        self.counts = {}
        for team, ident, x, y, direction, is_head in parts:
            ident = int(ident)
            c = int(y) * self.w + int(x)
            self.occupied[c] = ident
            self.pearls.pop(c, None)
            self.counts[ident] = self.counts.get(ident, 0) + 1
            if ident == self.id:
                mine[c] = DIRS.index(direction[0])
            elif is_head == '1':
                (self.allies if team == self.team else self.enemies)[c] = ident
        if not self.body or self.body[0] != self.head:
            self.body = [self.head]
            while len(self.body) < self.length:
                found = next((c for c, d in mine.items() if c not in self.body
                              and self.destinations(c)[d] == self.body[-1]), None)
                if found is None:
                    break
                self.body.append(found)
        self.body = self.body[:self.length]
        self.own = set(self.body) | set(mine)
        self.other = {c for c, ident in self.occupied.items() if ident != self.id}
        self.visits[self.head] = self.visits.get(self.head, 0) + 1
        # Versioned 64-bit self report: 8 magic, 9 round, 12 id, 12 cell,
        # 10 length, 1 team. Sonar is public; range and age validation only.
        for value in messages:
            if value >> 56 != 0xB7 or (value & 1) != (self.team == 'B'):
                continue
            stamp = (value >> 47) & 511
            ident = (value >> 35) & 4095
            cell = (value >> 23) & 4095
            length = (value >> 13) & 1023
            if 0 <= self.round - stamp <= 12 and cell < self.n and length >= 2:
                self.reports[ident] = (cell, length, stamp)
        if self.round % 16 == 0:
            self.pearls = {c: r for c, r in self.pearls.items() if self.round - r < 40}
            self.reports = {i: data for i, data in self.reports.items() if self.round - data[2] <= 12}

    def threats(self):
        danger = {}
        # Every visible head acts once before our next turn, regardless of ID.
        for origin, ident in self.enemies.items():
            queue = [(origin, 0)]
            visited = {origin}
            for cell, depth in queue:
                if depth >= P['threat_steps']:
                    continue
                for nxt in self.destinations(cell):
                    if nxt < 0 or nxt in visited or nxt in self.other:
                        continue
                    visited.add(nxt)
                    danger[nxt] = max(danger.get(nxt, 0), (1.0, .8, .45)[depth])
                    queue.append((nxt, depth + 1))
        return danger

    def targets(self, danger):
        # One bounded BFS gives each legal first direction an opportunity value.
        values = [-10.0] * 4
        queue = []
        visited = {self.head} | self.own | self.other
        for d, c in enumerate(self.destinations(self.head)):
            if c >= 0 and c not in visited:
                visited.add(c)
                queue.append((c, 1, d))
        for c, distance, first in queue:
            gain = 0.0
            age = self.round - self.pearls.get(c, -1000)
            if age < 40:
                gain += 1.0 / (1 + age * .05)
            countdown = self.beds.get(c, 10000) - self.round
            if 0 <= countdown <= distance + 4:
                gain += .35
            if any(n >= 0 and n not in self.seen for n in self.destinations(c)):
                gain += .12 if self.role != 'scout' else .35
            value = gain / (distance ** .65) - .12 * danger.get(c, 0)
            values[first] = max(values[first], value)
            if len(queue) >= P['search_cap']:
                continue
            for nxt in self.destinations(c):
                if nxt >= 0 and nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, distance + 1, first))
        return values

    def space(self, head, body):
        occupied = self.other | set(body[1:])
        visited = {head}
        queue = [head]
        cap = min(64, len(body) + 8)
        for c in queue:
            for nxt in self.destinations(c):
                if nxt >= 0 and nxt not in occupied and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
                    if len(queue) >= cap:
                        return len(queue)
        return len(queue)

    def evaluate(self, path, body, eaten, danger, compass):
        c = body[0]
        space = self.space(c, body)
        exits = sum(n >= 0 and n not in self.other and n not in body
                    for n in self.destinations(c))
        features = dict(pearl=len(eaten), target=compass[path[0]],
                        frontier=float(c not in self.seen),
                        visit=min(10, self.visits.get(c, 0)), danger=danger.get(c, 0),
                        mobility=min(space, 10) + exits,
                        trap=float(space < min(len(body) + 1, 15) or exits == 0),
                        sprint=len(path) - 1)
        score = sum(P[key] * value for key, value in features.items())
        return score, features

    def decide(self):
        self.role = ('gatherer' if self.length >= P['growth_length'] or self.round >= 360
                     else 'scout' if self.round < 90 and self.length <= 3 else 'hunter')
        danger = self.threats()
        compass = self.targets(danger)
        candidates = []
        queue = [((), self.body, frozenset())]
        expanded = 0
        depth_cap = 1 if self.first and self.round > 0 else P['sprint_depth']
        for path, body, eaten in queue:
            if len(path) >= depth_cap or (path and len(body) <= 2):
                continue
            for d, nxt in enumerate(self.destinations(body[0])):
                if nxt < 0 or nxt in body or (nxt in self.own and nxt not in self.body):
                    continue
                route = path + (d,)
                if nxt in self.other:
                    if nxt in self.enemies and self.units > 1:
                        target_len = self.counts[self.enemies[nxt]]
                        score = P['trade'] * (target_len - self.length + 1)
                        if self.role == 'gatherer':
                            score -= 100
                        candidates.append((score, 'MOVE', route, body, dict(trade=target_len)))
                    continue
                pearl = nxt in self.pearls and nxt not in eaten
                new_eaten = eaten | {nxt} if pearl else eaten
                new_body = [nxt] + list(body)
                if not pearl:
                    new_body.pop()
                if path:
                    new_body.pop()
                score, features = self.evaluate(route, new_body, new_eaten, danger, compass)
                candidates.append((score, 'MOVE', route, new_body, features))
                if expanded < P['candidate_cap']:
                    queue.append((route, new_body, new_eaten))
                    expanded += 1
        target_units = min(self.limit, max(4, min(P['team_target'], self.n // 24)))
        if self.length >= P['min_split'] and self.units < self.limit:
            # Split is a stationary turn: parent head risk still applies.
            urgency = max(0.0, 1 - self.units / target_units)
            score = P['split'] * urgency - 180 * danger.get(self.head, 0)
            if self.round >= P['split_until'] or self.role == 'gatherer':
                score -= 100
            candidates.append((score, 'SPLIT', 2, self.body[:-2], dict(split=urgency)))
        if not candidates:
            return 'MOVE N', 'trapped'
        score, kind, action, body, features = max(candidates, key=lambda c: c[0])
        self.body = body
        if kind == 'MOVE':
            for c in body[:len(action)]:
                self.pearls.pop(c, None)
            action = ''.join(DIRS[d] for d in action)
        detail = ','.join('%s=%.1f' % (k, v) for k, v in features.items() if v)
        return '%s %s' % (kind, action), '%s %.1f %s' % (self.role, score, detail)

    def output(self, action, indicator):
        cell = self.body[0] if self.body else self.head
        lines = [action, 'PROTOCOL 3', 'INDICATOR ' + indicator]
        # Explicit field limits: disable reports on huge maps / late IDs.
        if cell < 4096 and self.id < 4096:
            value = (0xB7 << 56) | (self.round << 47) | (self.id << 35) | (cell << 23) | (min(1023, self.length) << 13) | (self.team == 'B')
            lines.append('SONAR %s %d' % (DIRS[(self.round + self.id) % 4], value))
        lines.append('ENDTURN')
        sys.stdout.write('\n'.join(lines) + '\n')
        sys.stdout.flush()
        self.first = False


def main():
    start = read()
    if not start:
        return
    ident, team = int(start[1]), read()[1]
    dims = read()
    bot = Bot(ident, team, int(dims[1]), int(dims[2]), int(read()[1]))
    while True:
        words = read()
        if not words or words[0] == 'ENDGAME':
            return
        bot.round = int(words[1])
        read()  # facing; movement legality follows the full body instead
        bot.length, bot.units = int(read()[1]), int(read()[1])
        messages = [int(read()[0]) for _ in range(int(read()[1]))]
        first = read()
        if first[0] == 'ECHOES':
            first = read()  # counts are aggregate, not four directional ranges
        tiles = [first] + [read() for _ in range(48)]
        parts = [read() for _ in range(int(read()[1]))]
        horizontal = [read() for _ in range(8)]
        vertical = [read() for _ in range(7)]
        bot.observe(tiles, parts, horizontal, vertical, messages)
        bot.output(*bot.decide())


if __name__ == '__main__':
    main()
