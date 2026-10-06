"""H-SZ45: parent flood-room estimate (LOG SZROOM rnd room len status) for our queen vs static reachable room from the
frame snapshot at the same round (all bodies block, kelp via nbr None), for sealed (self/wall) and other queen deaths."""
import sys, glob, re, collections; sys.path.insert(0, '/home/claude/fr'); import frame, replay
rows = []
for f in sorted(glob.glob(sys.argv[1])):
    raw = replay.unpack(open(f, 'rb').read()); t = raw.decode('latin1') if isinstance(raw, (bytes, bytearray)) else str(raw)
    est = {int(a): (int(b), int(c), int(d)) for a, b, c, d in re.findall(r'SZROOM (\d+) (-?\d+) (\d+) (\d+)', t)}
    g = frame.decode(f); p = f.split('/')[-1][:-7].split('_'); bots = {'A': p[2], 'B': p[3]}
    q = [i for i in (0, 1) if i in g['rounds'][0] and bots[g['rounds'][0][i][0]] == 'c05rl']
    if not q: continue
    q = q[0]; d = next((x for x in g['events']['deaths'] if x['id'] == q), None)
    if d is None: continue
    D = d['round']
    def true_room(r):
        snap = g['rounds'][r]; occ = {c for (_, b) in snap.values() for c in b}
        if q not in snap: return None
        h = snap[q][1][0]; seen = {h}; fr = [h]
        while fr and len(seen) < 400:
            nx = []
            for c in fr:
                for n in g['nbr'].get(c, ()):
                    if n is None or n in seen or n in occ: continue
                    seen.add(n); nx.append(n)
            fr = nx
        return len(seen) - 1
    for k in (1, 2, 3):
        r = D - k
        if r in est and r >= 0:
            rows.append((d['cause'], k, est[r][0], true_room(r), est[r][1]))
by = collections.defaultdict(list)
for cause, k, e, tr, L in rows: by[('sealed' if cause in ('self', 'wall') else cause, k)].append((e, tr, L))
for key in sorted(by):
    v = by[key]; n = len(v)
    print(key, 'n', n, 'est>=2L', sum(e >= 2 * L for e, tr, L in v), 'true<L', sum(tr is not None and tr < L for e, tr, L in v),
          'both', sum(e >= 2 * L and tr is not None and tr < L for e, tr, L in v), 'median est', sorted(e for e, _, _ in v)[n // 2], 'median true', sorted((tr or 0) for _, tr, _ in v)[n // 2])
