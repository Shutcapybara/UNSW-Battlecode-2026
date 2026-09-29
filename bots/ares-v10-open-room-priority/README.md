# Ares V10 — open-room priority

Ares V10 branches from Ares V09 and changes only move selection around the existing time-aware room flood. Every legal post-move candidate is probed for enough reachable room to hold its full post-move length. If any candidate meets that threshold, V10 chooses among those candidates and ignores tighter moves even when they collect a pearl. If no candidate meets it, the V09 best-effort choice remains available.

This targets the highest measured leak in the September 29 team summary: trapped/mill deaths. The room flood already models body segments becoming free over time, so the change reuses that probe and does not add a second search. No portal, split, target, or threat policy is changed.

The first six-fixture screen showed lower wall deaths but an excessive pearl and r100 length drop because the filter required extra slack beyond the dragon's actual body. V10 now uses full post-move length as the threshold. Short comparisons against V09 use matched maps and seats from Portals, Slithery Fight, and Schooltime, recording death causes, pearls, r100 units/length, and sandbox points. V10 remains experimental until the documented full-panel and generalization checks are approved and complete.
