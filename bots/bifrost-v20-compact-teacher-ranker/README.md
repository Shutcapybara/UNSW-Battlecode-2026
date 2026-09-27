# Bifröst v20 — compact-map teacher ranker

This candidate keeps the Bifröst v01 action policy and Loki's learned ranker,
but applies the model bonus only on maps with at most 625 cells. On the matched
48-game external screen, Loki v01 improved Devil and Prisoner's Dilemma results
while regressing on Autarky, Default, and Queen of Spades. The gate keeps the
model active for Devil, Prisoner's Dilemma, and Trophy, where results were
strongest, and leaves Bifröst's original scoring untouched on larger maps.

This is a native screen, not judge CPU validation. Results are recorded in the
[Bifröst family notes](../../docs/bifrost-family.md).
