# sakura-s02-arrival-econ

Host `yuna-v05-core` (with the host's own override.py: portal_mode 1, nb_mode 2,
mom_w 0.6) plus three lever groups behind `sk_*` master flags. The three ablation
arms (`../sakura-s02-arm-{econ,safety,explore}`) are this exact code plus an
override.py that turns the other two groups off; the host itself
(`bots/yuna-v05-core`, unmodified) is the control arm. No production or conversion
clock was moved; the crown/beacon layer is the host's own.

- **econ** — arrival-ready bed valuation (fenrir-v18's lever: beds spawning later
  than arrival decay over `sk_ready_slack` 4; 1.15 premium when the pearl exists by
  arrival), 2-3-step sprints onto confirmed pearls (straight + one-bend, within the
  host's sprint caps) funded +2.0 in races / +0.6 tempo, contested-pearl appetite
  (enemy discount 0.6 -> 0.85 while r < 100, units < 26). Bed *camping* was built,
  measured toxic (total r250 135 -> 52 on schooltime) and shipped off
  (`sk_camp_w = 0`).
- **portal-safety** (chaewon y04/y05, credited) — ten-public-map atlas matched on
  the first view, newborn neck-by-adjacency fix, solo probe ray through an adjacent
  portal carrying the HOLD packet, echo/HOLD-priced blind risk.
- **explore** — on maps with >= 6 known portal pairs: mid/end blind-transit risk
  0.3/0.5 -> 0.2/0.35, unpaired-portal value 3 -> 4.5, exploration chance
  0.12 -> 0.2 (mid only; the opening keeps host prices — an opening cut measured
  135 -> 42 total r250 on schooltime).

Markers (single buffered write): `ACT:atlas` (map matched), `ACT:probe` (probe ray
cast), `ACT:sprint` (funded sprint that banked a pearl), `ACT:bed` (arrival-timed
bed step), `ACT:dive` (exploration-bonus step; note the host's own portal_mode
dives also mark, so the arm's attribution is the paired panel, not the marker).

## Six-line report

- **Strategy:** host value function untouched except where listed; lambda phases,
  crown election, feeding clocks all the host's. Funnel numbers: N/A this
  generation (no dissolve/escort work, per the S2 anti-goals).
- **Execution:** options on = forage/reposition/produce/salvage/strike/retreat/
  portal_transit/hold (host) + funded pearl sprints (econ) + probe ray
  (safety). Ablation deltas: see the paired table in
  `docs/findings/2026-09-29-sakura-s02-arrival-econ.md`.
- **Implementation:** metered (four S2 fixtures, sinbad-v07 opponent, both
  toolkits): zero faults on all eight fixture-toolkit runs; 1.2.2 p99 56.8-62.3M / max ≤ 79.5M; 1.0.0 p99 57.9-63.0M / max ≤ 81.5M — **the 1.0.0 hub gate FAILS marginally** (Slithery max 81.5 vs < 80; p99 over 60 on Schooltime/Portals/Slithery by 0.4-3.0M); the host alone meters p99 46.5-50.5M, so the excess is the atlas-enabled target search. Degradation mode: every lever is a flag; the
  exception path is the host's own (one visible LOG MC_ERROR line + fallback).
- **State:** host state + atlas name, probe round/head/landing, probe results
  (landing -> fresh/clear), HOLD reports (cell -> round), camp dict (empty; lever
  off). Consumers: blind-risk pricing, probe scheduling, cell values.
- **Messaging:** host packets (crown beacon, food gossip, portal shares, prey,
  density) + the HOLD packet on the solo probe ray (type 7: head cell + round;
  consumers: any dragon pricing a blind transit onto a held cell). The probe turn
  suppresses all other rays by design (echo attribution).
- **Momentum:** host hysteresis/nb_mode 2 unchanged; no certificate work this
  generation (A2 pending; S2 says do not depend on it).

## Paired panel

Seed-1 paired panels vs the S2 six-opponent set (97-100 exact pairs per arm;
unswbc 1.2.2): base 64.0/100 — +econ 48.0 (net −15) — +portal-safety 55.0 (−9) —
+explore 65.0 (+1; +3 on Portals/Slithery/Trauma) — **all (this bot) 40.0 (net
−22)**. H-econ and H-portal-safety are falsified; H-explore meets its bar exactly.
Deaths fell (wall+self −0.5/1k) while the economy fell harder. Full tables:
`docs/findings/2026-09-29-sakura-s02-arrival-econ.md`.
