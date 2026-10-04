# Rome H-KZ12 dose 5

Parent: `carthage-05-free-sprint`. One switch, `queen_tree_veto_k = 5`: for original queen ids 0/1, reject a first
move into a known directed terrain pocket only when inclusive C(u→v) < 5 and P+u has no simple cycle of length at
least queen length + 1. Unknown or unpaired terrain disables the veto; if it removes every legal move, the parent
decision is retained. Exact turn-start body legality is outside this narrow neck-only arm. Experimental snapshot.
