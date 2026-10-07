# bokuto-62-escape-priority

Immutable experiment from Bokuto 18. When every scored movement path is structurally
DEAD or H2H, a worker can prefer a larger legal tail escape split before ordinary
production. Queen, crown, feeder and reserve behavior are preserved. The guard still
reviews the selected split. No promotion implied.

Reproduction: six-segment head trapped in a corridor, tail opening into a room;
18 selects SPLIT 2 while its escape proposal is SPLIT 4. Real baseline traces did
not establish harmful distinct masking; this is a bounded mechanism experiment.
See FINALS_WORKING_MEMORY.md for fixtures and results.
