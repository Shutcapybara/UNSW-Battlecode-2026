"""HB-1 direction prior (the parent carthage-05's prior) for dragon turns, through the bot's own C++ extractor:
cpp/hb1_scores.cpp. Used by dataset.py (--hb1-exe) to add hb_pF/hb_pR/hb_pL columns. Label-free in its inputs:
the process's blocks and its own past actions only (what the bot itself had)."""
import subprocess
import labels as LB

KIND = {0: 'm', 1: 's'}


def fixture(seqs):
    """seqs: list of (spawn_text, [(block_text, label_dict), ...]) -> stdin text for hb1_scores."""
    out = []
    for sp, turns in seqs:
        out += ['PROC', 'SPAWN', sp.strip(), 'END']
        for txt, y in turns:
            out += ['BLOCK', txt.strip(), 'END']
            if y['y_kind'] == 0 and y['y_seq']:
                out.append(f"ACT m {y['y_seq']}")
            elif y['y_kind'] == 1:
                out.append(f"ACT s {y['y_child']}")
            else:
                out.append('ACT n')
    return '\n'.join(out) + '\n'


def scores(exe, seqs):
    r = subprocess.run([exe], input=fixture(seqs).encode(), capture_output=True, check=True)
    return [tuple(float(v) for v in l.split()) for l in r.stdout.decode().splitlines()]


def spawn_text(sp):
    return f"ID {sp['id']}\nTEAM {sp['team']}\nMAP {sp['W']} {sp['H']}\nUNIT_LIMIT {sp['unit_limit']}\n"
