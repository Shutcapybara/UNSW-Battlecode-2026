# Gavroche v25: earlier longest-crown handoff

Parent: Gavroche v23. The replay panels expose longest-dragon conversion as a
repeat weakness: Big Empty M274433 had 508 total team length but lost the
longest tiebreak 34–40, and Stronghold M274440 lost on a tied 45-length crown.
V23 itself went 4–8 against v17 on the six replay-sensitive maps.

V25 changes only `crown_margin` from 3 to 1. Once another living dragon is at
least one segment longer than the reported crown, it can take the crown role
and receive crown-weighted length value. All movement, production, sprint and
feeding logic stays as in v23. The focused panel tests whether faster handoff
improves the final longest unit across the previously conflicting families.
