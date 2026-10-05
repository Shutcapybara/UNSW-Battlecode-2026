# Kenma18 — entropy-matched combined prior

Parent: kenma-17-stacked-direction-prior. Only changes how its four-class prediction becomes the movement search's F/R/L prior. Raise F/R/L probabilities to1.61 and renormalize, then apply the unchanged weight1.0 and1e-4 floor. Reverse stays at parent zero. Model, features, prediction argmax, search, splits, pocket rescue and reserved slot are unchanged. The parent HB fallback retains its original treatment.

Choice is from exactly aligned189,630 out-of-fold development predictions, not from a sweep over game results. Parent mean F/R/L entropy0.422933 versus A5-400 at0.562078; matching parent entropy requires exponent1.610885, rounded to1.61. Increasing the search weight alone also changes the absolute move-versus-split offset; renormalization preserves a probability prior and isolates confidence more cleanly. This is a distribution-scale hypothesis, not proof of a better game policy.

Status: full Carthage102 running after both15 probes completed cleanly. ASan/UBSan prior normalization, facing, reverse and tiny-mass tests pass. Exact-source deployment remains required. Runtime558847bab7129bc69d0caab35cd37c66c06961ed57da8b751bee4a875a04556a. Reserved seeds11–13/new maps untouched. Evidence main build/kenma/stacked-prior/prior-scale.json; generator tools/kenma/prepare_calibrated_prior.py.
