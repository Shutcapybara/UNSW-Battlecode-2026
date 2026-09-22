# Dragon hunters

An aggressive swarm variant. Every dragon repeatedly splits whenever it has
four segments and the team has capacity. Enemy heads are pursued only while at
least three friendly dragons are alive, preserving a small force that can
rebuild the swarm after losses.

Hunters prioritise, in order:

1. with at least three friendly dragons, colliding with a reachable enemy head
   (including a two-step sprint),
2. reacting to a close-range friendly face-off sonar message,
3. splitting into more hunters,
4. spreading away from visible friendly heads,
5. collecting visible pearls, then exploring.

When two aligned friendly heads face each other from two or three tiles away,
the lower-ID dragon sends sonar value `1146242894` (`DRGN`). The receiver treats
that as a request to move aside. Sonar cannot be delivered from an adjacent
face-off without first colliding, so adjacent dragons simply use the normal
friendly-repulsion movement.

Run it with:

```sh
unswbc run maps/arena.map variants/dragon-hunters variants/dragon-hunters
```
