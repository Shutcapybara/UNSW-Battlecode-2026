# asahi-07-hkz26-m0 — P-4 / H-KZ26 queen reach veto, m = 0

Parent: `carthage-05-free-sprint` (REG-000, live 14585), H-KZ12 off. One switch: `Params::queen_reach_m = 0`
(-1 = off, parent behaviour). Card: `docs/learning/proposals/P-sugawara-02-hkz26-queen-reach-veto.md` (D-054 §C).

For the original queen only (`(w.me & 4095) <= 1`): every candidate whose final head cell is within an uncapped,
body-ignoring BFS of B(L^) + m of an enemy head visible at its TurnStart is removed (B(L) = ceil(L/4) + L - 2,
L^ = `enemy_length(prey)` = visible length + 2 if cut; unknown edges passable; kelp and unpaired portals not).
Moves and sprints are judged at the simulated final head; H2H at the struck head's cell; splits at the queen's
current head (a split does not move it); dives are exempt (exit cell unobservable). The parent's argmax is then
taken over the rest in the parent's order (moves, split, opening split, escape split under the -900 rule). If every
legal candidate is vetoed: largest Cb (`queen_cb`, copied unchanged from rome-15), ties by parent score; if only
vetoed splits are legal, the parent's split is kept and logged as a fallback. Deliberate feeder deaths return
before the veto (not reach-relevant). Logged per queen decision: `LOG HKZ26 r m heads lmax legal veto sveto fallback changed`.
