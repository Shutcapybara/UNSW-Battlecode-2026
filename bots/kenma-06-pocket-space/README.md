# Kenma 06 — pocket rescue plus queen space filter

Parent: kenma-03-pocket-queen. Copies policy.hpp and params.hpp byte-for-byte from asahi-05-kz12-k16 in the main checkout. All other runtime files are the Kenma 03 parent.

Retains the sealed-pocket rescue, donor culling and one-slot reserve. Adds Asahi's candidate-specific optimistic reachable-space check for original queens: veto a safe single step into fewer than 16 reachable cells without a sufficiently large cycle; if every step is vetoed, fall back to maximal reachable space. Unknown terrain, immediate dive/head-to-head outcomes and multi-step paths retain the parent's treatment. No map-identity inputs or new fitted parameters. The source's diagnostic fields remain present, but main.cpp does not emit Asahi's extra log line.

Motivation: Kenma 03 lost all six Weakhold games to Kageyama; Asahi's documented seed 2–3 pool improvement replicated on Weakhold. This is a composition hypothesis, not evidence that the combination improves play.

Status: prepared, unmeasured. Required next: full 102-game Carthage comparison and exact-source sandbox checks if promising. Reserved seeds 11–13 and new maps untouched.
