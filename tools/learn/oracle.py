"""Engine-replay oracle for SERVER replays: re-run the official engine on the replay's map with the server's seed,
answering every dragon turn with the action recorded in the replay, and capture the blocks the engine sends.
If the re-run reproduces the game (same event count and result), those blocks are ground truth for that server game
and test_rebuild-style parity applies to real top-team play. Run where unswbc is importable (cloud container / Mac).
    python oracle.py SEED_HEX replay [...]   or   python oracle.py --index index.jsonl replay [...]"""
import sys, json, collections, gzip, pickle
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import rebuild, block as B

OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


def scripted(data):
    acts = collections.defaultdict(list)
    meta = {}

    def em(i, sp, txt, ctx):
        acts[i].append((ctx, txt))
    m = rebuild.walk(data, em)
    return m, acts


def reply_text(ctx):
    out = []
    a = ctx['action']
    if ctx['tle'] or a is None:
        out.append('MOVE')                       # nothing valid; the engine records what it records
    elif a[0] == 'move':
        out.append('MOVE ' + a[1])
    elif a[0] == 'split':
        out.append(f'SPLIT {a[1]}')
    else:
        out.append('MOVE')
    for p in ctx['sonar']:
        d = p['dir'] if p['origin'] == ctx['head_after'] else OPP[ctx['facing_after']]
        out.append(f"SONAR {d} {p['value']}")
    out.append('PROTOCOL 3')
    out.append('ENDTURN')
    return ('\n'.join(out) + '\n').encode()


TEMPLATES = None


def templates():
    global TEMPLATES
    if TEMPLATES is None:
        import pathlib
        try:
            T = pathlib.Path(__import__('unswbc').__file__).with_name('templates') / 'maps'
        except ImportError:                      # no wheel here: the repo's copy of the 1.2.9 templates (D-043)
            T = pathlib.Path.cwd() / 'maps' / 'live'
        TEMPLATES = {rebuild.Map(f.read_text()).name: f.read_text() for f in T.glob('*.map')}
    return TEMPLATES


def true_map(server_txt):
    """Server replays redact bed timings (every TILE line '0 0', no PearlCountdown events) and may swap the teams'
    spawn seats. The engine's map = the template's TILE lines + the replay's own other lines (DRAGON seats)."""
    t = templates()[rebuild.Map(server_txt).name]
    tl = iter([l for l in t.splitlines() if l.startswith('TILE ')])
    out = [next(tl) if l.startswith('TILE ') else l for l in server_txt.splitlines()]
    return '\n'.join(out) + ('\n' if server_txt.endswith('\n') else '')


def run(data, seed, keep=False):
    m, acts = scripted(data)
    ptr = collections.Counter()
    real = collections.defaultdict(list)

    def reply(did, raw):
        real[did].append(raw)
        k = ptr[did]; ptr[did] += 1
        if k >= len(acts[did]):
            return b'MOVE\nENDTURN\n'
        return reply_text(acts[did][k][0])
    E = EngineModule()
    redacted = not any(l.startswith('TILE ') and not l.endswith(' 0 0') for l in m.text.splitlines())
    mtext = true_map(m.text) if redacted else m.text
    res = E.run(mtext.encode(), reply, debug=0, seed=seed)
    n = bad = 0
    first_bad = None
    for did, seq in acts.items():
        for k, (ctx, txt) in enumerate(seq):
            n += 1
            have = B.canon(real[did][k]) if k < len(real[did]) else ''
            want = B.canon(txt)
            if redacted:      # the rebuild cannot know countdowns: compare everything but the pearlIn field
                have, want = _nocd(have), _nocd(want)
            if have != want:
                bad += 1
                if first_bad is None:
                    w, h = B.canon(txt).splitlines(), have.splitlines()
                    first_bad = (did, k, ctx['round'], [(j, a, b) for j, (a, b) in enumerate(zip(w, h)) if a != b][:4])
    out = dict(map=m.name, redacted=redacted, turns=n, mismatched=bad, first=first_bad, rounds=res.rounds, winner=res.winner,
                extra_engine_turns=sum(len(v) for v in real.values()) - n)
    if keep:
        out['blocks'] = real
    return out


def _nocd(text):
    o = []
    for ln in text.splitlines():
        p = ln.split()
        if len(p) == 4 and p[0].lstrip('-').isdigit():
            p[3] = 'x'
        o.append(' '.join(p))
    return '\n'.join(o)


if __name__ == '__main__':
    args = sys.argv[1:]
    seeds = {}
    if args[0] == '--index':
        for l in open(args[1]):
            r = json.loads(l)
            seeds[str(r['game_id'])] = r['seed']
        args = args[2:]
    for p in args:
        sd = seeds.get(Path(p).stem)
        print(Path(p).stem, run(Path(p).read_bytes(), int(sd, 16)), flush=True)
