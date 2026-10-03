# Sparta 04 — queen reserve

Sparta 04 forks Sparta 01. It keeps Carthage 05's sprint/search base, queen
movement guard, shared enemy-queen pursuit, and unconditional non-queen queen
trades. Its one strategy change disables ordinary and opening splits for our
original queen, preserving her body length. The emergency split fallback
remains available if every movement is unsafe.

Sparta 03 recorded 156 original-queen split actions and 19 head-on queen
deaths across its 48-game screen, motivating this isolated test. Sparta 04
scored 13–11 against Sparta 01 and 7–17 against Carthage 05. The queen was
alive at round 490 in 3 of 32 games that reached it, a small directional
improvement over Sparta 03's 0 of 22. She still died in 45 of 48 games, and
Sparta 04 killed the enemy queen in 13 games, down from 28 for Sparta 03. The
production cost suggests trying a length reserve before rejecting the idea.
See the [queen-reserve finding](../../docs/findings/2026-10-02-sparta04-queen-reserve.md).
