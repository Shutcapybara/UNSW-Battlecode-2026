"""HB-1 Q2: Heartbreaker's validity wrapper as code (measured on 817 corpus games, q2_enumerate.py).

Commands are the classes CMDS: first relative step F/R/L, or SPLIT k (child size k, 2..8). The wrapper
takes any policy's scores over CMDS for a batch of v5 rows and returns the command it would emit:

  W0  a split needs length>=4, units<limit and child in [2, length-2]      (0 violations / 186,440 splits)
  W1  no ordinary exit, no portal, split-eligible  -> split                  (89,986 / 90,072 = 99.9 %)
  W2  no ordinary exit, no portal, not eligible     -> ally head F>R>L, else F  (deterministic in the sample)
  W3  no ordinary exit, portal, not eligible        -> a portal step          (20,387 / 20,413)
  W4  an ordinary exit exists -> never wall / own body / ally cell / enemy body;
      free, portal, enemy head (attack) and split stay open to the policy   (12 ally, 0 wall/own of 7.08 M)
Everything else (open-position split admission, direction, portal-vs-split under W3+eligible, split size)
is the policy.
"""
import numpy as np

CMDS = ['F', 'R', 'L'] + [f'S{k}' for k in range(2, 9)] + ['X']   # X: deliberate invalid command / suicide (lane tt)
MOVES = ['F', 'R', 'L']


def masks(d):
    """Boolean (n, len(CMDS)) of commands the wrapper allows, and a forced-command index (-1 = policy)."""
    n = len(d)
    ok = np.zeros((n, len(CMDS)), bool)
    blk = {r: d[f'c{r}_block'].to_numpy() for r in MOVES}
    por = {r: d[f'c{r}_portal'].to_numpy() for r in MOVES}
    L = d['length'].to_numpy()
    elig = d['split_elig'].to_numpy() == 1
    n_ord = d['n_exit_ord'].to_numpy()
    n_por = d['n_exit_portal'].to_numpy()
    for j, r in enumerate(MOVES):
        free, portal, ehead = blk[r] == 0, (blk[r] == -1) & (por[r] == 1), blk[r] == 7
        ok[:, j] = free | portal | ehead
    for k in range(2, 9):
        ok[:, CMDS.index(f'S{k}')] = elig & (k <= L - 2)
    ok[:, CMDS.index('X')] = True                            # suicide is always available: policy, not wrapper
    forced = np.full(n, -1)
    exitless = (n_ord == 0) & (n_por == 0)
    # W1: split-eligible and exit-less: only splits
    w1 = exitless & elig
    ok[w1, :3] = False
    # W2: exit-less, not eligible: deterministic fallback
    w2 = exitless & ~elig
    fb = np.zeros(n, int)                                   # F
    for j, r in reversed(list(enumerate(MOVES))):           # F wins over R wins over L
        fb = np.where(blk[r] == 5, j, fb)
    forced[w2] = fb[w2]
    # W3: portal-only, not eligible: only portal steps (already the only open moves)
    return ok, forced


def apply(d, scores):
    """scores: (n, len(CMDS)) policy scores/probabilities -> wrapped command index per row."""
    ok, forced = masks(d)
    s = np.where(ok, scores, -np.inf)
    pick = s.argmax(1)
    none_ok = ~ok.any(1)
    pick[none_ok] = 0
    return np.where(forced >= 0, forced, pick)


def label(d):
    """Observed command index (multi-step moves by first step; child sizes clipped to 8)."""
    y = d['y_first'].map({'F': 0, 'R': 1, 'L': 2}).to_numpy(copy=True)
    sp = d['y_family'].to_numpy() == 'split'
    y = np.where(sp, 3 + np.clip(d['y_child'].to_numpy(), 2, 8) - 2, y)
    other = ~sp & (d['y_family'].to_numpy() != 'move')         # suicide / other non-move actions
    y = np.where(other, CMDS.index('X'), y)
    return y.astype(int)
