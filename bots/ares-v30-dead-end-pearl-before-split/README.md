# Ares V30 — finish constrained pearl runs before splitting

V30 branches from V29. Match 658569 showed V28 splitting a length-4 dragon one move before the known pearl at an Autarky dead end. The parent collected the pearl as length 3 and then wall-died. V29 carried forward a movement-scoring farm predicate, but its under-room test was too narrow and still allowed routine splits on constrained approaches.

V30 retains that farm guard and adds a more direct condition: while the best movement advances toward a known pearl or bed, and both the current and next positions have at most the critical five-step body-aware reach, V30 defers all split choices and takes the move. Splitting resumes when the target route or constrained enclosure ends.

Development screen: pending.
