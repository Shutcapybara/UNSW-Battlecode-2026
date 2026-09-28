# chaewon-y05-hold

Parent `chaewon-y04-probe`. The probe ray now carries a **HOLD packet** (type 7: our head cell and round). It passes
through the portal and stops at the first dragon part — when an ally sits at the far exit, the ally receives
"a dragon holds <cell>" and prices a step onto that cell as blocked (`hold_ttl` 2 rounds). This closes the
symmetric case (two dragons approaching one portal pair from both sides), which the echo alone sees one round late.
Probe fixture (Default vs sinbad-v07, seed 2): blind head-ons into an allied head 19 → 6.

Panels (same as y04): 96 fixtures −0.026 vs y04 (10/13); pooled 196 fixtures vs yuna-v05 +0.008 (32/31).
Friendly head-on deaths per game fall to 0–8 (sinbad 18 on a Trophy fixture), but win rate does not move.
CPU (sandbox vs sinbad-v07): 1.2.2 Schooltime-as-A p99 59.9M / max 73.8M (13,307 turns; first turns p50 59M, other
turns p99 34M); Portals-as-B p99 56.7M / max 68.8M; 1.0.0 Schooltime-as-A p99 54.4M / max 66.1M. 0 faults.
