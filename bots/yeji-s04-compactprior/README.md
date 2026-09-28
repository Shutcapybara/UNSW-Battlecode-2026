# yeji-s04-compactprior

**Lineage:** Yeji. **Parent:** `yeji-s03-compactfield`. **Status:** frozen; superseded by `yeji-s05-young` (same policy + a CPU degradation for newborns).

One change: the public-map prior (terrain, fast beds, bed field) is loaded **only on maps of at most 625 tiles** (`prior_max_cells`); `mapprior.py` carries Portals, Dilemma, Devil and Trophy only. On open maps the bot plays like `yeji-s01p-production` plus portal-exit memory and direct certificate rays.

Panel (160 paired fixtures, 1.2.2, seed 1): **0.550** — vs control v10 **+0.056 (25 better / 16 worse, p = 0.21)**; vs `yeji-s01p-production` +0.019 (21/18). Per map vs v10: devil +0.31, portals +0.25, default +0.12, schooltime +0.12, slithery +0.12, dilemma +0.06, autarky −0.06, trophy −0.06, QoS −0.12, trauma −0.19. Per opponent: yuna-v02 +0.15, gavroche-v32 +0.10, witten-x03 +0.10.

Ablation on the 96 open-map fixtures: `w_blind_occ=0, cert_direct=0` → +0.010 (10/9): portal-exit memory and direct certificate rays are outcome-neutral; kept (certificate delivery 0.37 → 0.57).

Metered (vs sinbad-v07-divecap): Schooltime as A max 52.5M, p99 39.5M (16,332 turns); Portals as B max **79.8M**, p99 57.9M (12,271 turns) — at the edge; the spikes are newborns' second turns (cache warm-up: 62 of 88 turns above 60M) → s05.

> **Out-of-sample caveat (added 29 Sep).** The map prior only fires on the ten public maps it was built from; tournament maps are out of sample, so on them this bot plays without it. The in-sample gains above are not evidence of tournament strength. Held-out evaluation: see `yeji-s06-onlinebeds`.
