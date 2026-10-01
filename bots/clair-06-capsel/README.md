# clair-06-capsel

Maelle F5 (L02 sparsity cap selector) on the prior base. SF-1 state.hpp + Tun ported verbatim onto hb1-14; capsel = 1 (lo 48, hi 384): late cap = lo + (hi-lo)*sparsity, replacing round-keyed caps for age>=2. Parent: `bots/hb1-14-prior-r540` (unchanged). H-1 Test 1. On maelle-02: loses at every setting (econ -0.02..-0.03). Zero-capsel parity vs hb1-14: 0 divergent.

Gate: D-032 via `tools/clair/lane.py score clair-06-capsel --parent hb1-14-prior-r540`.
