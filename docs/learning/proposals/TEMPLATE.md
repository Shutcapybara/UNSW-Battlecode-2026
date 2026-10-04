# P-<n> — <title>

Author lane, date and time (UTC). Number cards in order of creation; check this directory for the highest number.
One change per card. A card that skips a rung or bundles two changes is returned unread.

## 1. Claim, rung and mechanism

- Rung (R0–R8, or `outside` for a temporary hand dial under D-044).
- Parent (registry id) and the one switch.
- Mechanism: what information or action the change adds that the parent lacks.

## 2. Expected sign and size

- Primary outcome, with the expected sign and size.
- Side effects expected: economy, deaths by cause, units and length, win by behavioural class and map_era.

## 3. Falsifier and stop rule

- The result that would refute the claim.
- The stop rule, written before the run. No extension after results are seen.

## 4. Test plan

- Offline: metric, split (from `docs/learning/splits/`), population, map_era, interval convention.
- Panel: screen (seed 1, both panels), then the D-046 §4 gate if the Chair advances it. Doses if there is a dial
  (at least three, parent = dose 0). For a map-local mechanism, name the target stratum.
- Live: roster, games budget.
- Designed invalid commands, if any, declared here (D-046 §4.4).

## 5. Cost

- CPU hours on the Mac under `build/learn/HEAVY.lock`, quota for live games, export size, turn-0 CPU.

## 6. RL translation (D-044)

- Observation. Action. Value/reward. Demonstration.

## 7. Numeric prediction

- P(pass) for the frozen objective, and the expected effect.

---

## Council reviews

Links to `docs/learning/reviews/P-<n>-<lane>.md`.

## Chair decision

D-record number, owner, frozen objective, stop rule, answers to dissents.

## Result card

Appended by the owning role: outcome against the frozen objective, per panel n, W-L-D, intervals, runtime wheel and
engine hash, fingerprint, missing fixtures listed as missing.
