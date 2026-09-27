# Gavroche V59 live-unit search guard

Parent: V36. Cap target search at 64 nodes only while live units are in the
23–44 range. V36's dense cap already covers 45 or more units. Keep V36's
density-dependent sprint limits until round 380, then disable three-step
candidates for all unit counts.

This follows the V41 profile: 18 of its top 20 late CPU turns had 23–43 live
units and used the full sparse target-search cap.
