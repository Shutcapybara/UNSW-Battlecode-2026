#!/usr/bin/env python3
"""explain: make a traced copy of an Ouroboros bot that logs WHY it moved.

    python3 tools/ouroboros/explain.py BOT OUTDIR [--rounds 10-40] [--logdir /tmp/ouro-explain]
    unswbc run maps/arena.map OUTDIR/BOT opponent      # then read LOGDIR/log-A-<id>.log

The copy (behaviour unchanged) writes per dragon and turn:
  r<R> id.. role.. len.. head.. tgt.. top=[best candidates]
  "  cand PATH v=.. [(feature, contribution), ...]"   every scored move, split by feature
  "  pearl CELL dDIST s=SCORE"                          every pearl the target search scored
  "  target CELL s=SCORE"                               the chosen target
Works on v10 (single main.py) and v12+ (evaluate.py / targets.py).
"""
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def patch_eval(src, lo, hi):
    lines = src.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("    for path, res in cands:"))
    end = next(i for i, l in enumerate(lines) if 'scored.append((v, path, "move"))' in l)
    out = []
    for i, l in enumerate(lines):
        if start < i < end:
            m = re.match(r"^(\s*)v ([-+])= (.*)$", l.split("  #")[0])
            if m and m.group(3).count("(") == m.group(3).count(")"):
                ind, sign, expr = m.groups()
                lab = re.sub(r"[^A-Za-z_]+", "_", expr).replace("P_", "").strip("_")[:16]
                l = '%s_d = %s(%s); v += _d; _parts.append(("%s", round(_d, 2)))' % (
                    ind, "-" if sign == "-" else "", expr, lab)
            elif re.match(r"^\s*v = lvv", l):
                ind = l[: len(l) - len(l.lstrip())]
                l = l + "\n" + ind + '_parts = [("mat", round(v, 2))]'
        if i == end:
            ind = l[: len(l) - len(l.lstrip())]
            out.append(ind + 'if TRACE and %d <= RND < %d: trace("  cand %%s v=%%.2f %%s" %% '
                       '(path, v, [x for x in _parts if x[1]]))' % (lo, hi))
        out.append(l)
    return "\n".join(out)


def patch_target(src, lo, hi):
    src = src.replace("""            if s > best_s:
                best_s = s
                best = n
    # role pulls""", """            if TRACE and %d <= RND < %d and pr is not None:
                trace("  pearl %%d d%%d s=%%.2f" %% (n, dn, s))
            if s > best_s:
                best_s = s
                best = n
    # role pulls""" % (lo, hi))
    return src.replace("""    return best, far, best_s
""", """    if TRACE and %d <= RND < %d:
        trace("  target %%d s=%%.2f" %% (best, best_s))
    return best, far, best_s
""" % (lo, hi))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot")
    ap.add_argument("outdir")
    ap.add_argument("--rounds", default="0-60")
    ap.add_argument("--logdir", default="/tmp/ouro-explain")
    a = ap.parse_args()
    lo, hi = map(int, a.rounds.split("-"))
    src = Path(a.bot) if Path(a.bot).is_dir() else ROOT / "bots" / a.bot
    dst = Path(a.outdir) / src.name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".unswbc-build", "__pycache__"))
    Path(a.logdir).mkdir(parents=True, exist_ok=True)
    for f in dst.glob("*.py"):
        s = f.read_text()
        s = re.sub(r"^TRACE = .*$", "TRACE = True", s, flags=re.M)
        s = s.replace('"/tmp/ouro-trace-%s-%d.log"', '"%s/log-%%s-%%d.log"' % a.logdir)
        if "for path, res in cands:" in s:
            s = patch_eval(s, lo, hi)
        if "def choose_target" in s:
            s = patch_target(s, lo, hi)
        f.write_text(s)
        compile(s, str(f), "exec")
    print(dst)


if __name__ == "__main__":
    main()
