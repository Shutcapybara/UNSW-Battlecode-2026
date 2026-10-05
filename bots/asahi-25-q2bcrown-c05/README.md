# asahi-25-q2bcrown-c05

Sugawara's Q2b crown queen (Q-sugawara-01 §7, BOARD 05:30Z), built by Asahi 5 Oct 05:58Z.
Parent: `carthage-05-free-sprint`. policy.hpp = bokuto-04-queen's policy.hpp (free lane Bokuto, runtime ff68a709, copied, Bokuto's tree untouched) with its three bokuto-03 lines removed (the bokuto_branch.hpp include and both branch_allowed calls); every other file is carthage-05's. So the change is exactly the '// bokuto-04' hunks: is_queen + QueenParams (no queen split after r60 at both split sites, threat x3, danger 6, dive 40, no queen prey/attack), crown (queen claims at r>=250, a live queen keeps it, feeders feed a queen crown). No bokuto.hpp guard, no main.cpp hook.
