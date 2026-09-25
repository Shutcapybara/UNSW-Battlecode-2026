from __future__ import annotations

import gc
import sys

from src.brain.policy import Policy
from src.communications.sonar import messages
from src.state.world import World

gc.disable()


def main() -> None:
    world = World.read_initial(sys.stdin)
    if world is None:
        return
    policy = Policy()
    while world.read_turn(sys.stdin):
        decision = policy.choose(world)
        output = [decision.command]
        output.extend(f"SONAR {direction} {packet}"
                      for direction, packet in messages(world))
        output.extend(("PROTOCOL 3", "ENDTURN"))
        sys.stdout.write("\n".join(output) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
