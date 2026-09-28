# Monte Christo v07: selected messaging experiment

**Experimental; retain v01 as the stable recommendation.**

Parent: `monte_christo-x12-remote-density`, copied byte-for-byte for reserve
evaluation. Framework: v01's Bahamut pipeline and Sinbad-derived tactical,
production, crown and feeding components. No learned model is introduced.

Counts of unique visible allied/enemy dragons and the observer's wrapped position
use a four-round EWMA. Latest reports are deduplicated by original source and
time, capped at 32 sources and aged with the same half-life, expiring at 16 rounds.
Spatial radius is seven. One density ray is reserved, idle rays are filled, and
crown/prey reports are protected. Relays preserve source/time. Forager resource
targets outside current vision are discounted by ally crowding (0.25) and enemy
count (0.40). Direct vision bypasses this discount. Packet checks reject unrelated
or malformed messages; the checksum is not adversarial authentication.

| Cohort | v07 / identical x12 | Matched v01 |
|---|---:|---:|
| Broader development: six external references, five maps | 45–15 | 45–15 |
| Untouched reserve: six references, four maps | 24–24 | 25–23 |
| Combined external, 108 fixtures | 69–39 | 70–38 |

Direct parent matches: 6–4 development, 3–5 reserve. x12 wins the saved
direct-parent tie-break over x04 before reserve testing; the reserve has five
paired gains and six losses. The density feature alone gains 12 outcomes and
loses 11 versus the otherwise identical x13 schedule. No reliable improvement
is established. There is no v07 four-map screen record.

Development regresses on Default/Stronghold and improves Trophy/Queen of Spades.
Reserve improves Autarky (4→6 wins), regresses Big Empty (9→7) and Trauma (11→10),
and ties Dilemma (1 each). On Big Empty/Tew B, extra pearl collection and total
length coexist with a worse final crown. Full counterexamples and opponent/side
breakdowns are in the messaging report (`../../docs/monte_christo-messaging.md`).

Judge: Hunter v20 on Arena, Stronghold and Big Empty, both sides, **4–2**.
76,294 metered turns; zero timeouts/caught errors. Median 38.62M, p99 71.00M,
maximum **97,444,353 CPU points**, maximum memory **22,478,848 bytes**. The worst
turn has only 2.56% CPU headroom; these fixtures do not guarantee universal safety.
Native development/reserve audits also have zero caught errors and timeouts.

Exact runs and configurations:

- `experiment_data/monte_christo-x12-remote-density_20260925143120048676`
  (`configs/monte_christo_messaging/validation.toml`).
- `experiment_data/monte_christo-v07-radio_20260925144659848351`
  (`reserve.toml` in the same config directory).
- `experiment_data/monte_christo-v07-radio_20260925145703444967`
  (`sandbox-final.toml`).

Standalone archive: `build/monte_christo/releases/monte_christo-v07-radio.zip`.
SHA256: `0a9f9a74b1a970ad2423e378e70aab112c79f447dc143ee7010dcdcf449b2451`.
Runtime sources match their frozen snapshots. `density_trace` and `training_trace`
are zero. See `tools/monte_christo/messaging/session_manifest.json` for all source
identities, settings and actual executions, and the
next-generation handoff (`../../docs/monte_christo-execution-handoff.md`) for the
planned execution-layer work. Do not mutate this measured version.
