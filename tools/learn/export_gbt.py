"""Compact export of a boosted-tree classifier to a C++ header for a bot (Data lane, kageyama; D-065 §D).

Format (read by cpp/gbt_compact.hpp, one generic evaluator):
  per node, in preorder (left child = next node):  F uint16 = feature | default_left << 15  (0x7FFF = leaf)
                                                   T uint16 = threshold-table index (internal) | leaf index within tree
                                                   R uint16 = offset of the right child (internal), 0 for a leaf
  per tree: node start (uint32), leaf start (uint32); tree t adds to class t % K
  THR: the distinct thresholds (double); LEAF: leaf values (float32 or double, --leaf f32|f64); BASE: K margins
  CMP: 0 = LightGBM (x <= t goes left), 1 = XGBoost (x < t goes left); NaN takes the default side
No information is lost for LightGBM models with missing_type None or NaN (checked; Zero is refused).

    python export_gbt.py lgb MODEL.txt OUT.hpp --ns NAME [--features FEATS.txt --input enc|hb1] [--leaf f32|f64]
With --features (the model's columns in order: encoder v1 names x_*, or HB-1 names hb_f_*), the header also carries
INPUT (0 encoder v1, 1 HB-1 vector), FEAT_NAMES (HB-1 row names, prefix stripped; for INPUT 1) and the left-right
mirror tables MIRROR_SRC / MIRROR_NEG / MIRROR_CODE_* (the map of tools/hinata/r2_mirror.py, D-066 §C.4 A8b).
    python export_gbt.py hb1 bots/carthage-05-free-sprint/hb1_direction_compact.hpp OUT.hpp --ns NAME   (re-export)
Also writes OUT.hpp.json (sizes, counts, sha256 of the source model).
"""
import argparse, hashlib, json, re, struct, sys
from pathlib import Path


def from_lgb(path):
    import lightgbm as lgb
    b = lgb.Booster(model_file=path)
    d = b.dump_model()
    K = d['num_tree_per_iteration']
    trees = []
    for t in d['tree_info']:
        nodes = []

        def walk(n):
            if 'leaf_value' in n:
                nodes.append(('L', n['leaf_value']))
                return
            assert n['decision_type'] == '<=', n['decision_type']
            assert n['missing_type'] in ('None', 'NaN'), n['missing_type']
            i = len(nodes)
            nodes.append(['N', n['split_feature'], n['threshold'], bool(n['default_left']), 0])
            walk(n['left_child'])
            nodes[i][4] = len(nodes) - i
            walk(n['right_child'])
        walk(t['tree_structure'])
        trees.append(nodes)
    return dict(K=K, trees=trees, base=[0.0] * K, cmp=0, n_feat=d['max_feature_idx'] + 1, kind='lightgbm')


def from_hb1(path):
    s = Path(path).read_text()
    K = int(re.search(r'dirc_K = (\d+)', s).group(1))
    base = [float(v.rstrip('f')) for v in re.search(r'dirc_base\[\] = \{([^}]*)\}', s).group(1).split(',')]
    starts = [int(v) for v in re.search(r'dirc_tree_start\[\] = \{([^}]*)\}', s).group(1).split(',') if v.strip()]
    body = re.search(r'dirc_nodes\[\] = \{(.*?)\};', s, re.S).group(1)
    words = [int(v.strip().rstrip('ULul'), 0) for v in body.split(',') if v.strip()]
    feats = re.search(r'dirc_feats\[\] = \{([^}]*)\}', s).group(1)
    n_feat = len(re.findall(r'"[^"]*"', feats))
    trees = []
    for ti, st in enumerate(starts):
        en = starts[ti + 1] if ti + 1 < len(starts) else len(words)
        W = words[st:en]
        nodes = []

        def walk(j):                     # re-pack only the reachable nodes (the source pads every tree)
            w = W[j]
            f = (w >> 32) & 0x7FFF
            val = struct.unpack('<f', struct.pack('<I', w & 0xFFFFFFFF))[0]
            if f == 0x7FFF:
                nodes.append(('L', val))
                return
            i = len(nodes)
            nodes.append(['N', f, val, bool((w >> 47) & 1), 0])
            walk(j + 1)
            nodes[i][4] = len(nodes) - i
            walk(j + (w >> 48))
        walk(0)
        trees.append(nodes)
    return dict(K=K, trees=trees, base=base, cmp=1, n_feat=n_feat, kind='hb1-xgboost-compact')


import re as _re
_WIN = _re.compile(r'^x_f(m?\d)r(m?\d)_(.+)$'); _HBG = _re.compile(r'^hb_f_g_(-?\d+)_(-?\d+)_(.+)$')
_SWAP = {'kelp_R': 'kelp_L', 'portal_R': 'portal_L', 'head_fac_R': 'head_fac_L'}
_SWAP.update({v: k for k, v in list(_SWAP.items())})
MIRROR_NEG = ['x_ownq_r', 'x_enemyq_r', 'x_home_r', 'x_mirror_xy_r', 'x_mirror_y_r']
MIRROR_CODE = {'x_last_first_rel': {1: 3, 3: 1}, 'hb_f_mem_last_rel': {2: 3, 3: 2}}


def _negs(v):
    return v[1:] if v.startswith('m') else ('0' if v == '0' else 'm' + v)


def partner(c):
    """Same map as tools/hinata/r2_mirror.py partner() (Kageyama's 21:26Z/21:56Z mapping)."""
    m = _WIN.match(c)
    if m:
        f, r, ch = m.groups()
        return f'x_f{f}r{_negs(r)}_{_SWAP.get(ch, ch)}'
    m = _HBG.match(c)
    if m:
        f, r, ch = m.groups()
        return f'hb_f_g_{f}_{-int(r)}_{ch}'
    for a, b in (('x_exit_R', 'x_exit_L'), ('hb_f_pearl_right', 'hb_f_pearl_left')):
        if c in (a, b):
            return b if c == a else a
    if c.startswith(('hb_f_cR_', 'hb_f_cL_')):
        return ('hb_f_cL_' if c.startswith('hb_f_cR_') else 'hb_f_cR_') + c[8:]
    return c


def mirror_tables(cols):
    ix = {c: i for i, c in enumerate(cols)}
    src = [ix[partner(c)] for c in cols]
    neg = [ix[c] for c in MIRROR_NEG if c in ix]
    code = [(ix[c], a, b) for c, mp in MIRROR_CODE.items() if c in ix for a, b in mp.items()]
    return src, neg, code


def emit(m, out, ns, leaf='f32', feats=None, inp=None):
    thr = sorted({n[2] for t in m['trees'] for n in t if n[0] == 'N'})
    ti = {v: i for i, v in enumerate(thr)}
    F, T, R, LEAF, NS, LS = [], [], [], [], [], []
    for t in m['trees']:
        NS.append(len(F)); LS.append(len(LEAF))
        li = 0
        for n in t:
            if n[0] == 'L':
                F.append(0x7FFF); T.append(li); R.append(0); LEAF.append(n[1]); li += 1
            else:
                assert n[1] < 0x7FFF and n[4] < 65536
                F.append(n[1] | (0x8000 if n[3] else 0)); T.append(ti[n[2]]); R.append(n[4])
        assert li < 65536
    assert len(thr) < 65536

    def arr(name, typ, vals, fmt):
        lines = []
        for i in range(0, len(vals), 24):
            lines.append(','.join(fmt(v) for v in vals[i:i + 24]))
        return f'inline constexpr {typ} {name}[] = {{\n' + ',\n'.join(lines) + '};\n'
    lt = 'float' if leaf == 'f32' else 'double'
    lf = (lambda v: repr(float(struct.unpack('<f', struct.pack('<f', v))[0])) + 'f') if leaf == 'f32' else (lambda v: repr(float(v)))
    lf32 = lambda v: ('%.9g' % struct.unpack('<f', struct.pack('<f', v))[0]) + 'f'
    h = [f'// generated by tools/learn/export_gbt.py from {m["kind"]} model - do not edit.\n#pragma once\n#include <cstdint>\n'
         f'namespace {ns} {{\n',
         f'inline constexpr int K = {m["K"]};\ninline constexpr int N_TREES = {len(m["trees"])};\n'
         f'inline constexpr int N_FEAT = {m["n_feat"]};\ninline constexpr int CMP = {m["cmp"]};\n',
         arr('BASE', 'double', m['base'], repr),
         arr('TREE_NODE', 'std::uint32_t', NS, str), arr('TREE_LEAF', 'std::uint32_t', LS, str),
         arr('THR', 'double', thr, repr),
         arr('F', 'std::uint16_t', F, str), arr('T', 'std::uint16_t', T, str), arr('R', 'std::uint16_t', R, str),
         arr('LEAF', lt, LEAF, lf32 if leaf == 'f32' else lf)]
    if feats is not None:
        assert len(feats) == m['n_feat'], (len(feats), m['n_feat'])
        src, neg, code = mirror_tables(feats)
        h += [f'inline constexpr int INPUT = {1 if inp == "hb1" else 0};\n',
              'inline constexpr char const* FEAT_NAMES[] = {\n' + ',\n'.join(
                  ', '.join('"' + (c[5:] if c.startswith('hb_f_') else c) + '"' for c in feats[i:i + 8])
                  for i in range(0, len(feats), 8)) + '};\n',
              arr('MIRROR_SRC', 'std::uint16_t', src, str),
              f'inline constexpr int N_MIRROR_NEG = {len(neg)};\n',
              arr('MIRROR_NEG', 'std::uint16_t', neg or [0], str),
              f'inline constexpr int N_MIRROR_CODE = {len(code)};\n',
              arr('MIRROR_CODE_IDX', 'std::uint16_t', [c[0] for c in code] or [0], str),
              arr('MIRROR_CODE_FROM', 'int', [c[1] for c in code] or [0], str),
              arr('MIRROR_CODE_TO', 'int', [c[2] for c in code] or [0], str)]
    h.append('}\n')
    Path(out).write_text(''.join(h))
    info = dict(kind=m['kind'], K=m['K'], trees=len(m['trees']), nodes=len(F), leaves=len(LEAF), thresholds=len(thr),
                n_feat=m['n_feat'], cmp=m['cmp'], leaf=leaf, header_bytes=Path(out).stat().st_size)
    import zipfile, io
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(out, Path(out).name)
    info['header_zip_bytes'] = len(bio.getvalue())
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kind', choices=['lgb', 'hb1']); ap.add_argument('model'); ap.add_argument('out')
    ap.add_argument('--ns', required=True); ap.add_argument('--leaf', default='f32', choices=['f32', 'f64'])
    ap.add_argument('--features'); ap.add_argument('--input', choices=['enc', 'hb1'])
    a = ap.parse_args()
    m = from_lgb(a.model) if a.kind == 'lgb' else from_hb1(a.model)
    feats = [l.strip() for l in open(a.features) if l.strip()] if a.features else None
    if feats is not None and a.input is None:
        a.input = 'hb1' if feats[0].startswith('hb_f_') else 'enc'
    info = emit(m, a.out, a.ns, a.leaf, feats, a.input)
    info['input'] = a.input
    info['source'] = a.model
    info['source_sha256'] = hashlib.sha256(Path(a.model).read_bytes()).hexdigest()
    Path(a.out + '.json').write_text(json.dumps(info, indent=1))
    print(json.dumps(info))


if __name__ == '__main__':
    main()
