# Aramis x07: P1 preview-aware decision

Parent: x04 E0/F1/P0. Executor/candidate dependencies remain exact.
P1 removes immediate trade priority from ATTACK proposals that only chase; before
round 200 chase scores -20, afterward at most 0.8. All other scores unchanged.
Optional previews share the <=52 path cache. See docs/aramis.md.
