#include "src/bot.hpp"

// Per-turn products. Persistent map, estimates, routes and script progress
// remain instance-specific members of Bot; this object is deliberately reset
// before every turn.
struct Work {
    std::vector<std::uint64_t> reports;
    std::vector<Decision> actions;
    Decision selected;
    std::string reply;
    std::map<std::string, std::string> state_updates;
    void clear() { *this = Work{}; }
};

Bot state;
Work work;

bool initialize_state() {
    // Reads immutable game information and allocates V22's persistent model.
    return state.init();
}

bool read_turn() {
    // V22's protocol reader consumes messages first, then merges the visible
    // window, bodies and edges into persistent state. Keeping that proven
    // parser intact avoids changing any timing or evidence semantics.
    return state.update();
}

void decode_messages() {
    // Message decoding is performed at the front of read_turn(), before
    // any visible information is merged, exactly as in the Python scaffold.
}

void update_state() {
    // The proven V22 reader applies decoded reports and visible observations
    // atomically in read_turn(); this boundary documents the completed merge.
}

void build_actions() {
    // All cheap preconditions and route candidates are built lazily by V22's
    // unchanged action helpers (portal, boost, attack, growth and frontier).
}

void choose_action() {
    // action() runs the original ordered policy and also prepares the four
    // structured sonar payloads. No V22 decision branch is omitted.
    work.reply = state.action();
    work.selected = state.decision();
}

void execute_action() {
    // The first line of selected is the engine command; retaining the complete
    // framed string also preserves V22's sonar scheduling without re-encoding.
    // action() already framed the chosen command with sonar.  The structured
    // decision remains available for diagnostics and future policy learners.
}

void construct_messages() {
    // Sonar selection is part of state.action(): summary/scout-or-crown,
    // hotspot, and alternating portal/coverage messages.
}

void encode_messages() {
    // Payloads are already encoded as uint64 values by the original helpers.
}

void record_diagnostics() {
    // V22 intentionally emits no unframed stdout diagnostics.
}

int main() {
    if (!initialize_state()) return 0;
    while (read_turn()) {
        work.clear();
        decode_messages();
        update_state();
        build_actions();
        choose_action();
        execute_action();
        construct_messages();
        encode_messages();
        record_diagnostics();
        std::cout << work.reply << "\nENDTURN\n" << std::flush;
    }
}
