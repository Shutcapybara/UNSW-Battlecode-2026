# Rome H-KZ12 dose 16

Parent: `carthage-05-free-sprint`. One switch, `queen_tree_veto_k = 16`: for original queen ids 0/1, reject a first
move into a known directed terrain pocket only when inclusive C(u→v) < 16 and P+u has no simple cycle of length at
least queen length + 1. Unknown or unpaired terrain disables the veto; if it removes every legal move, the parent
decision is retained. Exact turn-start body legality is outside this narrow neck-only arm. Experimental snapshot.
