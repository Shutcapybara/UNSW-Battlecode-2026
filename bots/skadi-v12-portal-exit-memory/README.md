# Skadi v12: portal exit memory

Parent: Gavroche V54 (`bots/gavroche-final`). This variant transfers Witten x01's recent-occupancy and recent-visibility memory to estimate the danger of hidden portal landings. Recent body occupancy keeps the baseline risk; a recently surveyed clear landing gets a lower risk.

## Results

- Five-map 100-game screen: 73–27 overall. On the 90 non-self fixtures, v12 scored 67–23 versus V54's 59–31; paired fixture outcomes improved 18 and worsened 10. Direct V54: 6–4. Zero runtime faults.
- Standard six-map panel: 83–37 overall. On the 108 shared non-self fixtures, v12 scored 76–32 versus V54's 69–39; paired outcomes improved 11 and worsened 4. Direct V54: 7–5. Zero faults.
- Fresh renamed-opponent holdout: 74–46 overall. On 108 shared fixtures, v12 tied V54 at 67–41; paired outcomes improved 11 and worsened 11. Direct V54: 7–5. Zero faults.
- Four judge-sandbox games on Big Empty and Trauma: p99 43.4–44.1M points, maximum 60.2M, and zero TLEs or runtime faults.

The standard panel advantage did not repeat on the fresh holdout, so v12 is not a confirmed upgrade over V54. Reports: `experiment_data/skadi-v12-portal-exit-memory_20260928025251864461`, `experiment_data/gavroche-final_20260928030120071926`, `experiment_data/skadi-v12-portal-exit-memory_20260928031751088940`, `experiment_data/gavroche-final_20260928032911316538`, `experiment_data/skadi-v12-portal-exit-memory_20260928034047435985`, `experiment_data/gavroche-final_20260928035452736665`, and `experiment_data/skadi-v12-portal-exit-memory_20260928031021779587`.
