# chaewon-y05-hold

Parent `chaewon-y04-probe`. The probe ray now carries a **HOLD packet** (type 7: our head cell and round). It passes
through the portal and stops at the first dragon part — when an ally sits at the far exit, the ally receives
"a dragon holds <cell>" and prices a step onto that cell as blocked (`hold_ttl` 2 rounds). This closes the
symmetric case (two dragons approaching one portal pair from both sides), which the echo alone sees one round late.
Probe fixture (Default vs sinbad-v07, seed 2): blind head-ons into an allied head 19 → 6.
