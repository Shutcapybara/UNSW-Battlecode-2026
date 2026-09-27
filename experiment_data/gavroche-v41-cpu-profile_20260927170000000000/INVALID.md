Discarded profiling attempt. The diagnostic code imported `sys` inside an
exception handler, which made it local to `main()` and caused bots to exit at
round 350 when the profile logger first ran. Do not use this run's CPU or result
data. The corrected run is `gavroche-v41-cpu-profile_20260927173000000000`.
