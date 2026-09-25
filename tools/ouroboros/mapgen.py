#!/usr/bin/env python3
"""Geometric variants of maps: transpose (T) and horizontal flip (FX).

The engine's randomness is a fixed seed, so a matchup on a map is one exact
game.  Variants of the same map play out differently (bots break ties by
direction, id order meets new geometry) while keeping the map's character:
three times the evaluation samples, and a check that a gain is not an
accident of one layout.

    python3 tools/ouroboros/mapgen.py            # writes tools/ouroboros/maps/*_T.map, *_FX.map
    python3 tools/ouroboros/mapgen.py --holdout  # tools/ouroboros/holdout/*_TFX.map, *_FY.map (never tune on these)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from mapview import load_map  # noqa: E402


def parse(text):
    m = load_map(text)
    sym = None
    name = None
    for line in text.splitlines():
        p = line.split()
        if p and p[0] == "SYMMETRY":
            sym = p[1]
        if p and p[0] == "MAP_NAME":
            name = " ".join(p[1:])
    m["sym"] = sym
    m["name"] = name or "map"
    return m


def transform(m, kind):
    W, H = m["W"], m["H"]
    if kind == "T":
        nW, nH = H, W

        def cell(x, y):
            return (y, x)

        # north edge of (x,y) -> west edge of (y,x) and vice versa
        def hedge(x, y):
            return ("v", y, x)

        def vedge(x, y):
            return ("h", y, x)
        sym = {"x": "y", "y": "x", "xy": "xy", None: None}[m["sym"]]
    elif kind == "FX":
        nW, nH = W, H

        def cell(x, y):
            return (W - 1 - x, y)

        def hedge(x, y):
            return ("h", W - 1 - x, y)

        def vedge(x, y):
            return ("v", (W - x) % W, y)
        sym = m["sym"]
    else:
        raise ValueError(kind)
    out = dict(W=nW, H=nH, sym=sym, name="%s %s" % (m["name"], kind))
    out["tiles"] = {cell(x, y): v for (x, y), v in m["tiles"].items()}
    edges = []
    for (x, y) in m["kelp_h"]:
        edges.append(hedge(x, y) + (1, -1))
    for (x, y) in m["kelp_v"]:
        edges.append(vedge(x, y) + (1, -1))
    for (x, y), pid in m["portal_h"].items():
        edges.append(hedge(x, y) + (2, pid))
    for (x, y), pid in m["portal_v"].items():
        edges.append(vedge(x, y) + (2, pid))
    out["edges"] = edges
    out["dragons"] = [(t, [cell(x, y) for x, y in cells]) for t, cells in m["dragons"]]
    return out


def write(m, path):
    W, H = m["W"], m["H"]
    lines = ["MAP %d %d" % (W, H)]
    if m["sym"]:
        lines.append("SYMMETRY %s" % m["sym"])
    lines.append("MAP_NAME %s" % m["name"])
    lines.append("TILE_COUNT %d" % len(m["tiles"]))
    for (x, y), (lo, hi) in sorted(m["tiles"].items(), key=lambda kv: (kv[0][1], kv[0][0])):
        lines.append("TILE %d %d %d %d" % (x, y, lo, hi))
    lines.append("EDGE_COUNT %d" % len(m["edges"]))
    for o, x, y, kind, pid in sorted(m["edges"]):
        row = 2 * y if o == "h" else 2 * y + 1
        lines.append("EDGE %d %d %d" % (row * (W + 1) + x, kind, pid))
    lines.append("DRAGON_COUNT %d" % len(m["dragons"]))
    for t, cells in m["dragons"]:
        lines.append("DRAGON %d %d %s" % ("AB".index(t), len(cells),
                                          " ".join("%d %d" % c for c in cells)))
    lines.append("END")
    Path(path).write_text("\n".join(lines) + "\n")


def compose(text, kinds):
    """Apply transforms in order (each re-parsed from text): e.g. ("T", "FX")."""
    import tempfile
    for k in kinds:
        m = parse(text)
        with tempfile.NamedTemporaryFile("w+", suffix=".map", delete=False) as fh:
            tmp = fh.name
        write(transform(m, k), tmp)
        text = Path(tmp).read_text()
    return text


def holdout():
    """Hold-out variants (never tuned on): _TFX = FX of T, _FY = T.FX.T (a y-flip)."""
    out = HERE / "holdout"
    out.mkdir(exist_ok=True)
    n = 0
    for p in sorted((ROOT / "maps").glob("*.map")):
        text = p.read_text()
        for name, kinds in (("TFX", ("T", "FX")), ("FY", ("T", "FX", "T"))):
            (out / ("%s_%s.map" % (p.stem, name))).write_text(compose(text, kinds))
            n += 1
    print("wrote %d hold-out maps to %s" % (n, out))


def main():
    if "--holdout" in sys.argv:
        return holdout()
    out = HERE / "maps"
    out.mkdir(exist_ok=True)
    srcs = {}
    for d in (ROOT / "maps", ROOT / "bots" / "maps"):
        for p in sorted(d.glob("*.map")):
            if p.stem not in srcs and p.stem not in ("Colloseum", "small"):
                srcs[p.stem] = p
    for stem, p in sorted(srcs.items()):
        m = parse(p.read_text())
        for kind in ("T", "FX"):
            write(transform(m, kind), out / ("%s_%s.map" % (stem, kind)))
    print("wrote %d maps to %s" % (2 * len(srcs), out))


if __name__ == "__main__":
    main()
