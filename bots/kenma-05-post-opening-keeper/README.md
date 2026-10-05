# Kenma 05 — post-opening keeper

Parent: kenma-04-keeper-action. One runtime change: the learned queen controller starts at round 25 instead of round 0. The pocket rescue remains active from the start; all other behavior and the model are identical.

Motivation: Kenma 04 keeps more queens but its seed-1 losses on Trophy and Tower Defense show a population deficit by rounds 50–100. This candidate preserves the parent policy through the opening before switching the queen to the keeper action model. This mechanism is a hypothesis; no score is claimed before paired games finish.

Model provenance and original export parity: main build/kenma/queen-action-v1/. Status: prepared, unmeasured.
