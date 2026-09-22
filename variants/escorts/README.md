# Captain with two escorts

This experimental standalone bot uses the pre-sprint pearl seeker as its captain.
The main project and previous comparison variants are unchanged.

- Every dragon, including escorts and their children, proactively births one
  two-segment child when length is at least four and the team limit allows it.
  This happens before role movement. The allowance is remembered per dragon
  and is not reset when a child dies. The team is no longer capped at three.
- After its birth, the captain prioritises safe adjacent pearls. Friendly escorts
  do not count as predicted threats, but their occupied tiles still block moves.
- Escorts patrol two or three tiles from the captain and avoid its immediate
  exits. Before their birth they favour pearls to grow; afterward they leave
  food for the captain where possible. Captain emergency splitting remains.
- Escorts deliberately attack enemy heads within three wrapped Manhattan steps
  of the captain's observed position, or an immediately reachable enemy head.
  These are sacrificial head-on trades. Friendly heads and all bodies are blocked.
- Role selection uses the lowest known friendly ID from visible segments. A
  single survivor becomes captain; when every living teammate is visible, the
  lowest ID is elected. Merely losing sight of the captain does not trigger a
  new captain. With no visible head, escorts follow its body or last observation.

Each dragon has only local vision and its own memory. There is no guaranteed
formation, perfect interception, or instant agreement after the captain dies.
The team can grow beyond two escorts as descendants reproduce, subject to
the game unit limit. Spawning still needs length and escorts can die. This is designed for the bundled maps with
one initial dragon per team, not arbitrary multiple-starting-dragon maps.

From the repository root:

```sh
unswbc run maps/arena.map variants/escorts variants/kamikaze-swarm
unswbc run maps/arena.map variants/kamikaze-swarm variants/escorts
```

Open the generated replay in VS Code to compare movement and interception.
Replace `arena.map` with `default_small.map` or `big_empty.map` to try more space.
The benchmark script accepts `--escorts`; its output is in `build/escort-benchmark/`.
Run it with the Python interpreter belonging to the installed `unswbc` tool.
