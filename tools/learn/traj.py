"""Team-trajectory block (D-067 §E.7; Data lane, kageyama). TRAJ_VERSION 1. A separate column group next to encoder
v1 (encode.py): encoder v2 = v1 columns + these. Legal by construction: each value is built only from this process's
own blocks, at its own turns, in order. The C++ twin is cpp/learn_traj.hpp (bit for bit; test_traj_parity.py).

Columns (int32; BIG = 999 'no history that far back', UNSEEN = -1 'never'):
  traj_units_d20 / traj_units_d100  unit count now minus the unit count at this process's latest turn at least
                                    20 / 100 rounds ago (BIG if the process has no turn that old). The level is
                                    encoder v1's x_unit_count.
  traj_len_d20                      own length now minus own length at that turn 20 rounds ago (BIG as above)
  traj_enemy_age                    rounds since this process last saw any enemy part in its window (0 = now; -1 never)
  traj_contacts20                   own turns in the last 20 rounds (r-19..r) with any enemy part in view
  traj_close20                      own turns in the last 20 rounds with an enemy head at Manhattan distance <= 2
  traj_obs20                        own turns in the last 20 rounds (the denominator of the two counts)
Usage: t = Traj(spawn); v = t.observe(block)   # block.Block, called once per own turn, before encoding the next
"""
import collections

TRAJ_VERSION = 1
BIG = 999
UNSEEN = -1
COLS = ['traj_units_d20', 'traj_units_d100', 'traj_len_d20', 'traj_enemy_age', 'traj_contacts20', 'traj_close20',
        'traj_obs20']
N_T = len(COLS)


def _tor(d, n):
    d %= n
    return d - n if d > n // 2 else d


class Traj:
    def __init__(self, spawn):
        self.id, self.team, self.W, self.H = spawn.id, spawn.team, spawn.W, spawn.H
        self.hist = collections.deque()      # (round, units, length, enemy_vis, enemy_close), last 101 rounds
        self.last_enemy = None

    def _back(self, rnd, k):
        best = None
        for h in self.hist:                  # oldest first: keep the latest turn with round <= rnd - k
            if h[0] <= rnd - k:
                best = h
            else:
                break
        return best

    def observe(self, b):
        rnd = b.round
        hx, hy = b.tiles[24][0], b.tiles[24][1]
        ev = ec = 0
        for t, i, x, y, f, h in b.parts:
            if i == self.id or t == self.team:
                continue
            ev = 1
            if h and abs(_tor(x - hx, self.W)) + abs(_tor(y - hy, self.H)) <= 2:
                ec = 1
        if ev:
            self.last_enemy = rnd
        h20, h100 = self._back(rnd, 20), self._back(rnd, 100)
        recent = [h for h in self.hist if h[0] > rnd - 20]
        out = [b.unit_count - h20[1] if h20 else BIG,
               b.unit_count - h100[1] if h100 else BIG,
               b.length - h20[2] if h20 else BIG,
               rnd - self.last_enemy if self.last_enemy is not None else UNSEEN,
               sum(h[3] for h in recent) + ev,
               sum(h[4] for h in recent) + ec,
               len(recent) + 1]
        self.hist.append((rnd, b.unit_count, b.length, ev, ec))
        while len(self.hist) > 1 and self.hist[1][0] <= rnd - 100:   # keep one turn at or before rnd-100
            self.hist.popleft()
        return out


def names():
    return ['x_' + c for c in COLS]
