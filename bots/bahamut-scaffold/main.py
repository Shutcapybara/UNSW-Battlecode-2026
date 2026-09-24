"""Bahamut: observations -> evidence -> fields -> action scores -> reply."""
import sys

game, turn = {}, {}       # Initialization and current local observations.
evidence, fields = {}, {}  # Persistent belief and derived spatial fields.
work = {}                # Per-turn reports, candidates, features, scores, output.


def read_tokens():
    while True:
        line = sys.stdin.readline()
        if not line:
            return []
        tokens = line.split("#", 1)[0].split()
        if tokens:
            return tokens


def read_init():
    row = read_tokens()
    if not row:
        return False
    game.update(id=int(row[1]), team=read_tokens()[1],
                size=tuple(map(int, read_tokens()[1:])),
                unit_limit=int(read_tokens()[1]))
    return True


def read_turn():
    row = read_tokens()
    if not row or row[0] == "ENDGAME":
        return False
    turn.clear()
    turn.update(round=int(row[1]), direction=read_tokens()[1],
                length=int(read_tokens()[1]), units=int(read_tokens()[1]))
    turn["messages"] = [int(read_tokens()[0]) for _ in range(int(read_tokens()[1]))]
    row = read_tokens()
    turn["echoes"] = (0, 0, 0, 0, 0)
    if row[0] == "ECHOES":  # Optional until PROTOCOL 3 takes effect.
        turn["echoes"] = tuple(map(int, row[1:]))
        row = read_tokens()
    turn["tiles"] = [tuple(map(int, row))] + [tuple(map(int, read_tokens())) for _ in range(48)]
    turn["bodies"] = [read_tokens() for _ in range(int(read_tokens()[1]))]
    turn["horizontal_edges"] = [read_tokens() for _ in range(8)]
    turn["vertical_edges"] = [read_tokens() for _ in range(7)]
    return True


def decode_messages():
    # Raw sonar -> identified, timestamped reports in work.
    pass


def merge_evidence():
    # Local observations + decoded reports -> evidence and changed locations.
    pass


def update_fields():
    # Evidence -> friendly, enemy, pearl, control fields and confidence.
    pass


def generate_candidates():
    # Local state -> available move, sprint, split and sacrifice options.
    pass


def simulate_candidates():
    # Candidates + known geometry -> immediate effects and uncertainty.
    pass


def extract_features():
    # Candidate effects + fields + dragon state -> fixed feature vectors.
    pass


def evaluate_candidates():
    # Feature vectors -> scalar scores; shared policy, no explicit roles.
    pass


def select_action():
    # Scores -> work["action"] (argmax or seeded stochastic selection).
    pass


def schedule_messages():
    # Evidence changes/refreshes -> work["sonar"]: direction -> uint64 payload.
    pass


def record_diagnostics():
    # Observations, fields, candidate scores and compute -> optional diagnostics.
    pass


def write_reply():
    lines = [work["action"]]
    lines += [f"SONAR {direction} {payload}" for direction, payload in work["sonar"].items()]
    sys.stdout.write("\n".join(lines + ["PROTOCOL 3", "ENDTURN"]) + "\n")
    sys.stdout.flush()  # One batched write per turn.


def main():
    if not read_init():
        return
    while read_turn():
        work.clear()
        # Runnable placeholders only: straight ahead, four empty sonar payloads.
        work.update(action="MOVE " + turn["direction"], sonar={d: 0 for d in "NESW"})
        decode_messages()
        merge_evidence()
        update_fields()
        generate_candidates()
        simulate_candidates()
        extract_features()
        evaluate_candidates()
        select_action()
        schedule_messages()
        record_diagnostics()
        write_reply()


if __name__ == "__main__":
    main()
