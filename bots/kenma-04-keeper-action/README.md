# Kenma 04 — keeper action clone

Parent: kenma-03-pocket-queen, exact pocket behavior and one reserved slot retained. Outside sealed pockets, original queens use a seven-class action model: F/R/B/L, split two, retain two, split half. Immediately lethal single steps are masked; the parent supplies a safe free sprint when its first step agrees. Other dragons use the parent unchanged.

Training: 26,820 oracle queen turns from keeper teams 91, 213, 507, 842, 55, training split only, no map-identity inputs. The same 270 HB-1 inputs are bound in the verified parent order. A fixed 128-round, 15-leaf LightGBM model scored 81.75% action accuracy on 7,223 rows from 17 held-out development series (majority 32.71%), then refit on all 26,820 rows. This is offline imitation evidence, not play strength.

Model SHA-256: e8bb884fe8e798ddd475be7ba841e901f302bfe1e9d0fabdadd039f2da61c99d. Reproduce with tools/kenma/queen_train.py and prepare_queen.py; output main build/kenma/queen-action-v1/.

Status: unmeasured candidate; head-to-head and deployment checks required.
