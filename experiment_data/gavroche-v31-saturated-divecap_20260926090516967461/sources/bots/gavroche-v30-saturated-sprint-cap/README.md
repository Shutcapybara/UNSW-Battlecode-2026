# Gavroche v30: saturated-phase sprint cap

Parent: Gavroche v17, preserving its policy and family-tested behavior outside
the high-population phase.

V17's Big Empty replays recorded missing-action deaths during rounds 49–199
with 44–64 allied units out of 64. V29 capped long-body three-step candidates
only before round 200, but its 500-round mirror still peaked at 99.4M CPU
points, indicating late dense turns also need coverage.

V30 keeps the full v17 three-step range while population is below 70% of the
unit limit. At or above 70%, it caps three-step candidates to lengths 4–7 for
as long as the team remains saturated, independent of round and the disabled
optional information-gradient push.
