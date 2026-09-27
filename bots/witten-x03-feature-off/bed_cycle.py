"""Conservative period evidence from consecutive observations of one bed."""


class BedCycles:
    def __init__(self):
        self.last = {}  # cell -> (round, countdown)
        self.gap = {}   # cell -> largest observed reset gap

    def observe(self, cell, round_num, countdown):
        previous = self.last.get(cell)
        if previous is not None and previous[0] + 1 == round_num:
            old = previous[1]
            # The engine decreases the countdown each round and resets it to
            # a sampled gap at zero. Seeing that reset confirms one full gap.
            # Gap-one beds remain at 1 on consecutive rounds.
            if countdown > old or (countdown == old == 1):
                self.gap[cell] = max(self.gap.get(cell, 0), countdown)
        self.last[cell] = (round_num, countdown)

    def fast(self, cell, threshold):
        return 0 < self.gap.get(cell, 0) <= threshold
