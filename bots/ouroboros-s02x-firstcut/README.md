# ouroboros-s02x-firstcut (benchmark)

The first S2 cut, kept as a benchmark. It differs from `ouroboros-s02-econ` in two ways:

- A never-seen atlas bed was valued at v_bed × P(due) alone, with no floor at the host's exploration value.
- `atlas_unseen` was 0.5.

On Trophy and Queen of Spades, where most tiles are slow (1–1000) beds, exploration collapsed:

- Units r100 fell to 6 on Trophy (host: 13).
- The economy-only arm scored −0.46 on 24 pairs there (0/11, p = 0.001).

Overall result: −0.062 vs fenrir-v18 on 120 seeded fixtures (16/23). Its `ACT:bed` marker is also older and fires on
any never-seen atlas bed. The rest of the logic is identical.
