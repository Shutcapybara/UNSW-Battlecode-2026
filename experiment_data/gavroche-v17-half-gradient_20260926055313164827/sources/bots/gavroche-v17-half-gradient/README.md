# Gavroche v17: half-strength informed expansion

Parent: Gavroche v16. This keeps the Sinbad v07 dive cap (`v_dive = 3`) and
Von Neumann x06 informed expansion, but halves `info_aggro_push` from 2.0 to
1.0. All other source and parameter settings are unchanged. The test asks
whether a weaker early-saturation push preserves v15's strong matchup against
x06 tf-05 while retaining v16's gains over Gavroche v13 and the sparse grad1
rating reconstruction.

The replay set has four 11-map series with different results by opponent
(Team A: 6/11, 4/11, 7/11, 2/11). Big Empty, Prisoner's Dilemma, and Trophy
were recurring replay loss maps. On the new cross-family panel v16 split
Big Empty overall, lost both Big Empty games against Sinbad and reconstructed
grad1, swept Dilemma against every reference, and split Trophy overall. The
full 13-map, both-side comparison checks whether a single lower gradient dose
improves this tradeoff without tuning to one replay opponent.

Comparison: `gavroche-v17-comparison.toml`.
