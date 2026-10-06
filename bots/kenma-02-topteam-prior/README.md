# Kenma 02 — top-team direction prior

Parent: carthage-05-free-sprint at ea8ada4e2. Replaces only the direction prior with Hinata A1-u fold-f0, truncated to 400 boosting iterations. The top-ten pooled development model uses the same 270 HB-1 features; F/R/L are renormalised. Split, sprint, sonar and search remain the parent policy.

This is a development fold model, not a full-data fit. Model archive SHA-256: f20de44d11e5374b67a554178a0eb4aa2f3bd3257293fc0944d112872e341f0c. Recreate with tools/kenma/prepare_a1.py; lane output build/kenma/a1/provenance.json records feature ordering and exporter counts.

Status: rejected as an improvement. Native head-to-head versus Carthage 05 on 17 ranked maps, both seats, seeds 1–3: 42 wins, 60 losses, 0 runtime errors. Prediction parity passed on 20,000 rows (all argmax equal, max absolute error 4.65e-8); archive 1,142,429 bytes before README. Results: main build/kenma/k02-v-carthage-s123/score.json and build/kenma/a1/parity.json. No sandbox checks spent on this failed screen.
