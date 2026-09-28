#!/usr/bin/env python3
"""Build a bot's `mapprior.py`: terrain (kelp, portals) and pearl-bed gaps of
the public maps, so a dragon that recognises its map from its first 7x7 view
knows the whole board from turn 1.  Public information (the map files the
server uses, bytes identical to maps/*.map).

    python3 tools/yeji/build_prior.py bots/yeji-s02-dev/mapprior.py [map ...]

Edge keys follow the bots' convention: north side of cell c -> c,
west side of c -> NC + c (c = y*W + x).  Edge string chars: '.' open,
'w' kelp, 'A'+pid portal.  Beds: tuple of (cell, min_gap, max_gap) for
tiles with max_gap <= BED_MAX (slower beds carry no usable signal).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE10 = ["schooltime", "portals", "slithery_fight", "queen_of_spades", "default", "trophy",
          "dilemma", "autarky", "devil", "trauma"]
BED_MAX = 300


def parse(path):
    W = H = 0
    edges = None
    beds = []
    sym = ""
    for line in Path(path).read_text().splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == "MAP":
            W, H = int(p[1]), int(p[2])
            edges = ["."] * (2 * W * H)
        elif p[0] == "SYMMETRY":
            sym = p[1] if len(p) > 1 else ""
        elif p[0] == "TILE":
            x, y, lo, hi = map(int, p[1:5])
            if hi > 0 and hi <= BED_MAX:
                beds.append((y * W + x, lo, hi))
        elif p[0] == "EDGE":
            idx, kind, pid = int(p[1]), int(p[2]), int(p[3])
            stride = W + 1
            col, row = idx % stride, idx // stride
            if row % 2 == 0:
                if col == W or row == 2 * H:
                    continue
                k = (row // 2) * W + col
            else:
                if col == W:
                    continue
                k = W * H + ((row - 1) // 2) * W + col
            if kind == 1:
                edges[k] = "w"
            elif kind == 2:
                assert pid < 26
                edges[k] = chr(65 + pid)
    return W, H, "".join(edges), tuple(sorted(beds)), sym


ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-"
LAMBDA = 6.0


def neighbours(W, H, edges):
    """cell -> list of cells reachable in one step (kelp blocks, portals teleport)."""
    NC = W * H
    pairs = {}
    for k, ch in enumerate(edges):
        if ch.isupper():
            pairs.setdefault(ch, []).append(k)
    other = {}
    for ch, ks in pairs.items():
        if len(ks) == 2:
            other[ks[0]], other[ks[1]] = ks[1], ks[0]

    def ekey(c, d):
        x, y = c % W, c // W
        if d == 0:
            return c
        if d == 2:
            return ((y + 1) % H) * W + x
        if d == 3:
            return NC + c
        return NC + y * W + (x + 1) % W

    def step(c, d):
        x, y = c % W, c // W
        return [((y - 1) % H) * W + x, y * W + (x + 1) % W, ((y + 1) % H) * W + x, y * W + (x - 1) % W][d]

    out = []
    for c in range(NC):
        ns = []
        for d in range(4):
            k = ekey(c, d)
            ch = edges[k]
            if ch == ".":
                ns.append(step(c, d))
            elif ch == "w":
                continue
            else:
                pk = other.get(k)
                if pk is None:
                    continue
                # same rule as the bots' dest_raw
                if pk >= NC:
                    pc = pk - NC
                    px, py = pc % W, pc // W
                    ns.append(pc if d == 1 else py * W + (px - 1 if px else W - 1))
                else:
                    px, py = pk % W, pk // W
                    ns.append(pk if d == 2 else (py - 1 if py else H - 1) * W + px)
        out.append(ns)
    return out


def field(W, H, edges, beds):
    """F[c] = sum over fast beds of rate * exp(-pathdist/LAMBDA), quantised 0..63 (max = 63)."""
    import math
    NC = W * H
    nb = neighbours(W, H, edges)
    F = [0.0] * NC
    for c0, lo, hi in beds:
        rate = min(1.0, 2.0 / (lo + hi)) if lo + hi else 1.0
        dist = {c0: 0}
        q = [c0]
        for c in q:
            d = dist[c]
            if d >= 4 * LAMBDA:
                continue
            for n in nb[c]:
                if n not in dist:
                    dist[n] = d + 1
                    q.append(n)
        for c, d in dist.items():
            F[c] += rate * math.exp(-d / LAMBDA)
    m = max(F) or 1.0
    return "".join(ALPHA[int(round(63 * f / m))] for f in F)


ZS = 8


def compact_entry(W, H, e, b, sym, f):
    """CPU-cheap form for the bots (s03+): everything a dragon needs is a
    constant; loading is a few C-level slice copies."""
    ekb = bytes(1 if ch == "." else 2 if ch == "w" else 3 for ch in e)
    portals = {k: ord(ch) - 65 for k, ch in enumerate(e) if ch.isupper()}
    rates = {}
    zones = {}
    ZW = (W + ZS - 1) // ZS
    for c, lo, hi in b:
        r = min(1.0, 2.0 / (lo + hi)) if lo + hi else 1.0
        rates[c] = round(r, 4)
        z = (c // W // ZS) * ZW + (c % W) // ZS
        zones[z] = round(zones.get(z, 0.0) + r, 4)
    fb = bytes(ALPHA.index(ch) for ch in f)
    return (ekb, portals, rates, zones, sym, fb)


def main():
    if sys.argv[1] == "--compact":
        out = Path(sys.argv[2])
        names = sys.argv[3:] or LIVE10
        lines = ['"""Generated by tools/yeji/build_prior.py --compact from maps/*.map (public maps). Do not edit.',
                 'MAPS[(W, H)] = [(name, edge kinds bytes (1 open, 2 kelp, 3 portal; key c north, NC+c west),',
                 '                 {edge key: portal id}, {cell: pearls/round}, {zone(8x8): pearls/round}, symmetry,',
                 '                 field bytes 0..63 (sum of rate*exp(-pathdist/6), max 63))]"""',
                 "MAPS = {}"]
        for n in names:
            W, H, e, b, sym = parse(ROOT / "maps" / (n + ".map"))
            f = field(W, H, e, b)
            ent = compact_entry(W, H, e, b, sym, f)
            lines.append("MAPS.setdefault((%d, %d), []).append((%r,) + %r)" % (W, H, n, ent))
        out.write_text("\n".join(lines) + "\n")
        print("wrote", out, out.stat().st_size, "bytes")
        return
    out = Path(sys.argv[1])
    names = sys.argv[2:] or LIVE10
    lines = ['"""Generated by tools/yeji/build_prior.py from maps/*.map (public maps). Do not edit."""',
             "MAPS = {}"]
    for n in names:
        W, H, e, b, sym = parse(ROOT / "maps" / (n + ".map"))
        f = field(W, H, e, b)
        lines.append("MAPS.setdefault((%d, %d), []).append((%r, %r, %r, %r, %r))" % (W, H, n, e, b, sym, f))
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
