# ouroboros-v06-lanchester (rejected experiment)

v05 plus two combat-model ideas:

- Lanchester: local head count (ally heads in view + 1 vs enemy heads) shifts
  the trade bias (`lanchester_k`) and strike margins (`lanchester_strike`).
- Incentive-aware strike chances: `p *= clamp(1 + inc_k * (our len - their
  len), inc_min, inc_max)` - size-aware hunters strike what is longer than
  them.

Screen (7 maps x 4 opponents x both sides): v05 43-13, v06 39-17,
v06 without Lanchester 42-14. Neither moved the needle; kept as a record.
