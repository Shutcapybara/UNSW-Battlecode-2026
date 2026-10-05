# Kenma 03 — sealed-pocket queen

Parent: carthage-05-free-sprint at ea8ada4e2. Independent of Kenma 01/02.

Proves a connected component of at most eight cells from known nonportal terrain. In such a pocket, original queens (id 0/1, as in the current engine maps) split down to length two whenever possible and otherwise take a safe single step. Nonqueen dragons seeing the original queen in their sealed pocket deliberately cull using SPLIT 1, before the queen next moves. Other dragons reserve one population slot for emergency queen splits. No map identity condition.

Precedent: Rome 06 cage E1; this variant confines donor culling and queen movement to observed sealed pockets and selects the complete single-step action instead of truncating a scored sprint.

Status: unmeasured; native and sandbox checks required.
