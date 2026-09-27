# Gavroche v23: selective sprint CPU cap

Parent: Gavroche v19. V21 showed that disabling all three-step sprint options
reduced Big Empty CPU peaks to 90.7M/93.1M, but its first 46 native fixtures
lost all four completed Big Empty, Autarky and Queen of Spades games. Three-
step moves appear strategically load-bearing for early short hunters.

V23 restores three-step candidate paths for lengths 4–7 and disables them for
lengths 8–11. Single-step and two-step candidates are unchanged. This tests
whether the least-long combat dragons retain their burst movement while the
longer candidates stop multiplying per-turn evaluation cost.
