# Rome 04 — H-H1 queen head-piece tie

One switch on `rome-01-nodevil`: when the crown dragon splits into equal halves, pass crown status to the new head piece (change strict-majority inheritance to majority-or-tie). The base already allocates the largest legal head piece on escape splits (`length - 2`), so this isolates the remaining two-plus-two edge at length four; it leaves production split policy and all other crown allocation unchanged.

Expected signs, recorded before the run: r150 queen survival increases; opening production and r100 material are unchanged; overall win is nonnegative. Paired pool and gen fixtures, seeds 1–3, both seats. H-H1's 95% survival interval falsifier and the paired overall-win interval will be reported. Parent: `rome-01-nodevil` (not L39 arm 03).


## Post-run estimand correction

Himeji’s source audit found that crown state cannot activate before r250 and that type-7 inheritance sets crown state on a new child, while the original queen remains the parent. The r150 survival expectation above was therefore not a valid treatment endpoint. This snapshot measures late crown-to-child equal-split handoff, not additional original-queen head retention. See `docs/findings/2026-10-04-rome-H-H1-late-crown-tie.md`; actual active-crown exposure could not be recovered from the saved controller-free replay frames.
