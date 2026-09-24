# hunter-v16-boost-traps

C++ fork of Hunter V15 with cautious boost-and-trap attacks.

It first looks for a compact boost route of at most six steps that leaves the
enemy head's three adjacent sides occupied by the attacker's body, then falls
back to a shorter boost that blocks one exit and leaves the enemy at most one
known exit.
The surround route must keep all three blocking body segments after paying
the boost cost, leave the attacker at least two safe exits, and preserve a
four-segment size lead. The shorter cutoff requires a three-segment lead.

Both attacks require tracing the enemy's full body through visible tiles and
target only enemies that have not acted yet this round. The route also requires
fully visible enemy exits and the attacker's full route. Unknown enemy body or
exit information cancels the tactic.

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/arena.map bots/hunter-v16-boost-traps bots/hunter-v15-shared-territory
```
