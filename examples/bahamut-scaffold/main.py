"""EDIT THIS FILE: information -> state -> intent -> command; reports -> sonar."""
from enum import Enum, auto
import protocol as io


class Intent(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    SPLIT = auto()
    ATTACK = auto()       # Example scripted intention, not an engine command.
    FEED_ALLY = auto()    # Intentional sacrifice, distinct from ordinary movement.


state = {}  # Persistent, instance-specific memory: map, estimates, script progress.
work = {}   # Temporary reports, candidate intents and outgoing information.
# io.game and io.observation contain engine input; treat them as read-only.
# io.reply contains the engine command and encoded sonar payloads to send.


def initialize_state():
    # Set model-specific initial memory once when this dragon process starts.
    pass


def decode_messages():
    # io.observation["messages"] (uint64s) -> work["reports"] (structured data).
    pass


def update_state():
    # Visible information + decoded reports -> persistent state.
    pass


def build_actions():
    # State -> available (Intent, parameters) pairs in work["actions"].
    # Example: (Intent.FEED_ALLY, {"target_id": 17}); check cheap preconditions.
    pass


def choose_action():
    # Available intents + state -> work["selected"]; rules or a learned policy.
    pass


def execute_action():
    # Selected intent -> io.reply["command"] and io.reply["argument"].
    # Example: FEED_ALLY -> (io.Command.MOVE, "E"); ATTACK may run pathing.
    # Queue script-memory changes in work["state_updates"] for the final commit.
    pass


def construct_messages():
    # Choose information to send and ray directions -> work["messages"].
    pass


def encode_messages():
    # Structured outgoing messages -> io.reply["sonar"]: direction -> uint64.
    pass


def record_diagnostics():
    # Optional prediction/action/probability records; never print unframed stdout.
    pass


def main():
    if not io.read_init():
        return
    initialize_state()
    while io.read_turn():
        work.clear()
        work.update(reports=[], actions=[], selected=None, messages=[], state_updates={})
        # Transport-only fallback until execute_action is implemented: go straight.
        io.reply.clear()
        io.reply.update(command=io.Command.MOVE, argument=io.observation["direction"], sonar={})
        decode_messages()
        update_state()
        build_actions()
        choose_action()
        execute_action()
        construct_messages()
        encode_messages()
        record_diagnostics()
        state.update(work["state_updates"])  # Explicit selected-script memory commit.
        io.write_reply()


if __name__ == "__main__":
    main()
