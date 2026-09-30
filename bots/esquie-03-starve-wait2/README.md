# esquie-03-starve-wait2

Esquie M-1 Part 3, second form of the starve-wait gate. Parent `esquie-01-nodevil`
(same as esquie-02; the gate change is the only difference from v02).

v02 result: local gains real (Trauma r50|map 0.111->0.222, Dilemma r250|map +0.11,
win +6pp; pinwheel +0.125 win/+17 r250 transfers; Portals/Devil bit-unchanged as
designed) but REJECTED: pooled z1 -0.024 econ / -2.19pp win; Trophy econ_pct
0.594->0.470 (win 0.719->0.562), trauma_tr r250 -29, equatorial_belt -53.

Diagnosis: the starved observable ignored beds whose countdown had already passed -
a sitting pearl on a known bed was invisible to the gate, so dragons on slow-dense
maps (Trophy: 100% beds, ripe50 0.09) "starved" while food sat known elsewhere and
waited at ripening beds instead of collecting it. v03 widens food_soon to the same
bed_stale = 60 window cell_value uses for stale-ripe bed value.
