# Ares V34 — crown dash avoidance

V34 branches from V33 after match 669722. At round 477, the 24-length crown moved from `(20,10)` to `(20,11)`, one cell from a 4-length enemy whose visible chain was clipped by the view boundary. The enemy dashed north-west, killed the crown by adjacent head contact, and also died; Ares was eliminated. V33 only priced enemy positions the head could occupy exactly, and the clipped chain limited its estimated reach.

V34 retains V33's split-time portal handoff. For crowned dragons, a clipped enemy tail implies the maximum dash reach; threat penalties also cover adjacent head-contact cells. A nearby-enemy separation term favors moves away from visible enemy heads, and crowns do not initiate head-to-head trades. Other dragons retain V33's threat scoring.

This is an experimental research snapshot. It has not been submitted or admitted to `FRONTIER.md`. See the V34 finding for replay and benchmark evidence.

## Screen result

V34 scored 7–13 against V33 across ten live maps and both seats on seed 1, with
zero runner errors. It lost both Portal, Queen of Spades, and Slithery Fight
games. The broad retreat reward and crown trade prohibition overcorrected; this
branch is rejected. The next candidate, V35, keeps only clipped-dash and
adjacent-contact threat accounting. Details are in the
[V35 finding](../../docs/findings/2026-09-30-ares-v35-crown-clipped-dash-threat.md).
