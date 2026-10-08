# Akaashi 02 — visible queen strikes

Fork of immutable `akaashi-01-queen-escape`, retaining its queen escape safety,
Bokuto 18 economy/feeding, and disabled atlas. Experimental local candidate;
Akaashi 01 submission 20222 remains the active deployment.

Before ordinary scoring and splitting, non-queens search fully observed paths
of one to three steps for a legal collision with a visible enemy queen.
Each prefix uses the existing exact body/pearl/paid-step simulation. This
allows length-two attackers to fund a sprint by eating a pearl on the way.
Shortest successful attack wins. Own queens do not take this override.
Unknown edges, unpaired portals, body collisions and unaffordable paid steps
are rejected. Enemy queen trades have priority independent of ordinary
material scoring and team-size thresholds.

The final move is validated again before bypassing the survival/harvest guard:
intermediate prefixes must be legal, the last step must hit the visible enemy
queen head, and no step may follow the collision. Ordinary moves retain the
guard. Only current local observations are used.

Trigger: Trophy match 1407768, team A, visualiser round 47 (protocol round 46).
Dragon 4 at (12,10), length two, can eat the pearl at (12,9), then sprint east
into the queen at (13,9). Parent chooses west; 02 chooses `NE`. The official
engine confirms both attacker and enemy queen die in that collision.

Tests:

```sh
python3 tests/test_akaashi_queen_strike.py
python3 tests/test_akaashi_queen_escape.py
```

Measured diagnosis, limitations and screen results: [family notes](../../docs/akaashi-family.md).
