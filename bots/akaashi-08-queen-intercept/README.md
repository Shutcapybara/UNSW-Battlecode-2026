# Akaashi 08 — queen escort intercept

Experimental fork of Akaashi 07. When the queen is visible, a comparable enemy head is within five toroidal steps of her, and this is the nearest visible nonqueen ally to her, movement scoring rewards safe steps toward both queen and pursuer. The normal body simulator and threat costs remain in force; this is an escort/intercept approach, not permission to collide with a body.

Trigger: Team A, Australia match1418905. Dragon21 followed a resource route west while enemy10 tracked the queen. Replay turn order shows enemy10 acts before ally21; entering enemy10's old head cell would hit its body, so no immediate equal trade exists at the described moment. The queen and enemy10 later mutually collide at round60. Goal of this candidate is to place an ally in the pursuit corridor earlier and let an equal-value escort take the later contact. No map-specific coordinates or IDs are used.

Local observation replay probe and scripted branch are required before interpreting the change as a rescue. No upload or promotion.
