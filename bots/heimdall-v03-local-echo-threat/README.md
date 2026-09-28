# Heimdall v03 — local threat from echoes

V03 is Fenrir v18 with its parameters, portal strategy, and child-site handoff
unchanged. It uses `world.echo` as a small multiplier on the existing local
head-threat score. Enemy-head echoes carry more weight than enemy-body echoes;
the multiplier is capped at 18%. All target values, movement choices outside
known threats, and sonar message scheduling remain the measured Fenrir policy.

This tests whether the aggregate echo is useful as a prior for visible combat
risk while avoiding the broad, location-free portal penalty and the radio
blackout used in earlier variants.
