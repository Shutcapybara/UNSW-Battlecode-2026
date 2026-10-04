# Rome H-KZ12 body-conditioned dose 4

Parent: `carthage-05-free-sprint`. For original queen ids 0/1, consider ordinary one-step moves only. For each
engine-legal candidate, project that candidate's post-move body and growth, relax one tail consistently, then
compute inclusive reachable capacity Cb up to16, excluding the prior head. Unknown terrain/frontier is optimistic.
Retain candidates with Cb≥4 or a cycle of length≥projected queen length+1; otherwise veto and preserve parent ranking.
If all legal one-step moves are vetoed, use the legal move with highest Cb, parent ranking as tie-break. Sprint,
split, and immediate legality behavior remain separate. Experimental snapshot, not a candidate.
