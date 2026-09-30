# Ares V42 — memory and teammate dispersion

## Hypothesis

After the V41 portal-bed changes, dragons can still converge around an exit or
spend exploration turns in areas whose remembered tiles contain no pearl beds.
Removing the map-specific lane attraction and charging movement that closes on
visible allied heads should give those dragons a clearer dispersal incentive.

## Changes

- Forked V41 as `ares-v42-memory-team-dispersion`; V41 remains unchanged.
- Removed the Devil lane bonus from candidate movement scoring and its parameters.
- Reduced the value of unseen exploration cells in 8×8 sectors with at least
  eight remembered tiles and no known pearl bed. The discount scales with
  sector coverage and tops out at 65%.
- Applied the same memory-and-bed discount when selecting a fallback sector.
- Added a movement cost for moves that reduce topological distance to visible
  allied heads within six tiles. The total cost is capped at 3. Crown and feeder
  roles do not receive this cost.
- Left direct pearl/bed valuation, hunt scoring, and split evaluation inherited
  from V41.

## Evidence and status

Replay 703779 prompted review of how a dragon chooses movement near a portal
exit. Replay 700279 documented repeated returns and allied clustering around a
portal landing. V42 targets broader dispersion through exploration memory and
teammate approach scoring.

The native V42-vs-V41 screen used `unswbc 1.2.2`, the same ten maps as V41's
parent/child screen, both starting seats, and a generated seed for each game.
V42 scored **8–12**, with zero runner errors, replay-analysis errors, or
reported runtime faults. V42 swept Portals and Slithery Fight. V41 swept
Autarky, Default, Devil, and Trophy; Dilemma, Queen of Spades, Schooltime, and
Trauma split 1–1. This is one development screen, not broad promotion evidence;
V42 remains experimental and is not admitted to the all-map frontier.

The full report, seeds, logs, and replays are in the ignored
`experiment_data/ares-v42-memory-team-dispersion_20260930123201634335/`
directory.

### Regression review

Replay snapshots point to an expansion and economy gap, rather than execution
faults. On Autarky with V42 in seat B, at round 100 it had 14 dragons, 31 total
length, and 66 pearls; V41 had 22 dragons, 52 length, and 122 pearls. By round
150 V42 was down to 8 dragons and 22 length, against V41's 26 dragons and 60
length. On Devil with V42 in seat B, the round-100 counts were 7 dragons and 73
pearls for V42 versus 27 dragons and 145 pearls for V41. Devil is also the one
map where the removed lane bonus was active (`32×16` map gate).

The movement cost is a plausible contributor on the other maps: it is charged
for every candidate move that closes on a visible ally, regardless of whether
the current target is exploration, a pearl, or prey. The replay snapshots do
not expose the internal scores, so this remains a mechanism-based diagnosis,
not an isolated causal result. V42 beat V41 on Portals and Slithery Fight, which
shows the movement changes are map-dependent. An ablation would be needed to
separate the teammate cost from the bedless-sector discount.

Source: [`ares-v42-memory-team-dispersion`](../../bots/ares-v42-memory-team-dispersion/).
