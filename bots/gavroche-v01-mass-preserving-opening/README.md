# Gavroche v01: mass-preserving opening

Parent: `monte_christo-x12-remote-density` (Monte Christo x12).

Adds an early rescue split for long, partially observed starting dragons. During
rounds 0–4, a dragon of length at least 8 can split off two tail segments even
when the normal policy cannot reconstruct the complete body. This lets the
large remaining piece escape the constrained spawn lane.

Screen results against Monte Christo x12 and Hunter v20, on Autarky and
Prisoner's Dilemma with both side assignments: **5 wins, 3 losses**, no runner
errors. It beat x12 on both Prisoner's Dilemma sides. This established the
opening fix, but its production rate remained too low against Hunter v20.
