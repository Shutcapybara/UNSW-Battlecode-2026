# Kenma27 — coherent teacher direction blended only for open-map queens

Parent21 (Carthage60–42), with16's previously verified lossless parent-model storage. Only original queens outside a proven sealed pocket receive a direction-prior change. Their F/R/L prior is the normalized geometric mean of the parent and team213 distributions, weight0.5 each, with the existing1e-4 floor applied before blending. Nonqueen prior, move search, splitting, pocket rescue and reserve relay remain21. Model class order F/R/B/L; back is removed and F/R/L renormalized. No fit or weight sweep.

Existing source: Hinata A1-team213 full400-round refit, SHA256 aa2fc510ac06766a25b6070a98789b8984dc3b30d26873365068a8e03b6d1bee.270 HB features in verified parent-binding order;1600trees,196404nodes. Lane-local export corrects LightGBM missing_type=None NaN routing to the zero comparison; the shared exporter and measured ancestors are unchanged. Native probabilities match LightGBM on2832 real/missing-value samples (max error 2.84e-08, all argmax equal). This is implementation evidence only, not strength evidence.

Motivation: pooled drop-in priors regressed. A coherent teacher is new evidence; restricting its blend to queens preserves the direction prior that carries most of the team's economy. This remains speculative: teacher213's full-move model was not fitted solely to queens, and the parent still controls split timing.

Status: prepared, unmeasured. Exact combined archive, runtime integration, activation/fallback audit and sandbox compute remain required before deployment; no game queue. Reserved seeds11–13/new maps untouched.

Runtime preflight: blend arithmetic passes ASan/UBSan. On997 recorded turns across12 processes, all922 nonqueen/sealed-pocket control actions match21 exactly;75 open-queen turns activate the teacher with zero fallbacks and one changed action (WeakholdB round40,W→E). This is fixed-observation evidence, not a game or survival prediction. Initial combined zip4,019,850 bytes; updated package metadata in build/kenma/teacher213/package.json. No game or deployment queue.
