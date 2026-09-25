# Porthos x02: stable executable intentions over Monte Christo v01

Parent: `bots/monte_christo-v01-core` (via the Porthos frozen control,
`bots/porthos-x01-frozen`).  This is the next-generation execution layer:
the legacy monolithic ranker is decomposed into the six-stage contract and a
stable six-intention menu, **with zero measured behaviour divergence**.

## Verification

- **24/24 identical complete move/split/sonar streams** vs the v01 control
  (tew-v12-mid-support, hunter-v20-portal-scouts, ouroboros-v13-ladder x
  Colosseum, devil, queen_of_spades, trauma x both sides; runs
  `monte_christo-v01-core_20260925151940672650` vs
  `porthos-x02-intentions_20260925160103012473`, report
  `build/porthos/parity-porthos-x02.json`), extended to **182/182 identical
  streams** on the full 7-reference x 13-map gauntlet (runs
  `monte_christo-v01-core_20260925162941686304` vs
  `porthos-x02-intentions_20260925160727903654`, both 112–70–0; report
  `build/porthos/gauntlet-stream-equivalence.json`).
- Judge budget (sandbox.toml, hunter-v20 x arena/stronghold x both sides):
  29,200 metered turns, median 29.71M, p99 50.23M, max 72.87M points,
  max memory 22.1 MB — inside the 100M/48MB budget with 27.1M to spare.
- 15 engine-faithful scenario and contract checks:
  `tests/test_porthos_intentions.py` (wrapping, paired/unpaired portals,
  tail occupancy, sprint cost, head trades and the strike gate, split
  geometry, child search cap, explicit intentional feeding, donation
  exclusivity, preview non-commitment, no-surviving-move recording, despair
  gating of the emergency split, executor menu/interface, crown handoff,
  traces disabled, protocol untouched).

## Contract mapping (version 1)

| Stage | Module | Content |
|---|---|---|
| 1 state update | `world.py`, `radio.py`, `roles.py` | frozen, byte-identical to v01 |
| 2 candidates | `intentions.py` | cheap frozen availability probes, stable candidate records |
| 3 features | `features.py` | global features before candidates; per-candidate mechanical previews |
| 4 decision | `decision.py` | policy P0: the v01 scoring field, expression-order identical |
| 5 execution | `executors.py` | executor set E0: one executor per intention |
| 6 commit/output | `main.py` | only the selected execution's trail cells commit; messages; reply |

Intention menu (stable names): `gather`, `scout`, `attack`, `retreat`,
`feed_ally`, `reproduce` (`intentions.KINDS`).  Candidate support (target
search) lives in `targets.py`, extracted verbatim plus an inert
`MEM["kind"]` annotation recording which branch produced the target.

Version stamps: `targets.TARGETS_VERSION`, `intentions.INTENTIONS_VERSION`,
`features.FEATURES_VERSION`, `decision.POLICY_VERSION`,
`executors.EXECUTORS_VERSION`, all 1.  State/communication are the v01
files, unchanged.

## Behaviour-preserving decisions (and why they are not labels on old moves)

- Each intention owns its availability probe and its executor.  FEED_ALLY's
  donation is an explicit, exclusive, intentional sacrifice (predicted
  `dead`, trade `donation`) -- never inferred from replay suicide labels.
  ATTACK distinguishes favourable strikes from deliberate unfavourable
  trades accepted only because every alternative was worse.  RETREAT's
  emergency split is admitted by P0 only below the despair threshold
  (legacy `-900`), exactly the legacy escape-split gate.
- E0 executors validate and serialise the decision-nominated path with the
  exact simulation, re-checking hard split invariants.  They are real but
  deliberately thin: an E1 executor may self-route to the same nominated
  target with the policy frozen; the execution record (command, predicted
  outcome, status/reason, trade class, path cells, report requests,
  diagnostics) is the interface that survives that swap.
- Global features (threat map, head-near set) are built before candidate
  construction -- the contract allows this and the REPRODUCE probe's flood
  fill reads the head-near set.  Order was chosen to keep every
  `tx.flood`/`tx.sim` call sequence's observable effects identical to v01.
- P0 keeps the legacy crowding loop in decision (not folded into a feature
  sum) so floating-point association order matches v01 exactly.
- The crown handoff sonar packet is attached at commit for ANY split
  command (legacy behaviour), including a crown's emergency retreat split.

## Divergence record

None measured: the semantic menu was introduced without an intentional
behaviour change, and the stream comparisons above cover the claim.  Any
future divergence must be recorded here with its fixture and round.

## Diagnostics

`P["intent_trace"] = 1` logs `LOG MC_INTENT {...}` per turn: selected
intention, target, score, status/reason, predicted outcome, trade class.
Off by default; never enable in deployment artifacts (a contract test
asserts this).  `LOG MC_ERROR` + legal fallback move on exception, as v01.
