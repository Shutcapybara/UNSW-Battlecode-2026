# Gavroche V50 sparse late search

Parent: V49. After round 150, when the team has at most 20 live units, restore
the target-search cap to 64 and allow length-4/5 three-step paths. Keep V46's
32-node/24-cell budgets during denser late play.

Hypothesis: extra search matters most after attrition makes late exploration
and escape decisions more important, while avoiding the 23–43 unit interval
where V41 profiling found the highest CPU turns.
