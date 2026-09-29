#!/usr/bin/env python3
"""Make a Renoir candidate directory from a parent: copy the source, edit Params constants, write CANDIDATE.toml.

    python3 tools/ra/variant.py PARENT NEW --set bed_wait=8.0 [--set x=y ...] \
        --mechanism "..." --expect "..." [--hypothesis "..."]

Only existing `static constexpr` Params are edited (a new switch is added by hand in the parent's successor);
the measured source is always the shipped source.
"""
import argparse, hashlib, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ['.gitignore', 'atlas.hpp', 'bot.toml', 'helper.hpp', 'main.cpp', 'nav.hpp', 'params.hpp', 'policy.hpp', 'world.hpp']


def fingerprint(d):
    h = hashlib.sha256()
    for p in sorted(Path(d).iterdir()):
        if p.suffix in ('.cpp', '.hpp') or p.name == 'bot.toml':
            h.update(p.name.encode() + b'\0' + p.read_bytes() + b'\0')
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('parent'); ap.add_argument('new')
    ap.add_argument('--set', action='append', default=[])
    ap.add_argument('--mechanism', required=True); ap.add_argument('--expect', required=True)
    ap.add_argument('--hypothesis', default='')
    ap.add_argument('--base', default=None, help='accepted parent for lineage_parent (default: parent)')
    a = ap.parse_args()
    src, dst = ROOT / 'bots' / a.parent, ROOT / 'bots' / a.new
    if dst.exists():
        sys.exit(f'{dst} exists')
    dst.mkdir()
    for f in SRC:
        if (src / f).exists():
            shutil.copy(src / f, dst / f)
    p = (dst / 'params.hpp').read_text()
    for kv in a.set:
        k, v = kv.split('=', 1)
        pat = re.compile(r'(static constexpr [\w:<>]+ ' + re.escape(k) + r' = )([^;]+);')
        if not pat.search(p):
            sys.exit(f'no param {k}')
        p = pat.sub(lambda m: m.group(1) + v + ';', p, count=1)
    (dst / 'params.hpp').write_text(p)
    (dst / 'CANDIDATE.toml').write_text(
        f'name = "{a.new}"\nlineage = "gustave"\nlane = "rc"\nauthor = "claude-opus-5.5/rc"\nlanguage = "c++"\n'
        f'lineage_parent = "{a.base or a.parent}"\nmechanism = "{a.mechanism}"\nexpected_change = "{a.expect}"\n'
        f'hypothesis = "{a.hypothesis}"\nparams = {a.set!r}\nstatus = "candidate (not registered)"\n'
        f'fingerprint = "{fingerprint(dst)}"\n'.replace("'", '"'))
    print(dst, fingerprint(dst))


if __name__ == '__main__':
    main()


def refingerprint(d):
    """rewrite the fingerprint line of CANDIDATE.toml after hand edits"""
    c = Path(d) / 'CANDIDATE.toml'
    t = re.sub(r'fingerprint = "[0-9a-f]*"', f'fingerprint = "{fingerprint(d)}"', c.read_text())
    c.write_text(t)
    return fingerprint(d)
