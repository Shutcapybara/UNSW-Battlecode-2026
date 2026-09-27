# Gavroche V62 tiered search guard

Parent: V60. When live units are in the 23–44 range, cap target search at 96
nodes for length-4/5 dragons and 64 nodes for length-6+ dragons. V36's dense
cap already covers 45 or more units. Keep V60's round-380 triple cutoff.

This preserves more search for medium-body dragons than V60 while continuing
to bound the long-body search on the turns that dominate the CPU profile.
