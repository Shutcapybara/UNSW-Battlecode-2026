// Parity harness: reads a fixture written by tools/learn/test_parity.py from stdin and checks the C++ encoder
// against the Python vectors.  Fixture: per process "SPAWN" <lines> "END", then per turn "BLOCK" <lines> "END",
// "X v...", "ACT kind first nsteps round"; "PROC" separates processes.
#include <iostream>
#include "learn_encode.hpp"
int main() {
    std::string line, buf; long turns = 0, bad = 0, procs = 0;
    learn::Encoder* enc = nullptr; learn::Block blk; bool have_blk = false;
    auto read_until_end = [&]() { std::string s, l; while (std::getline(std::cin, l) && l != "END") s += l + "\n"; return s; };
    while (std::getline(std::cin, line)) {
        if (line == "SPAWN") { delete enc; enc = new learn::Encoder(learn::parse_spawn(read_until_end())); procs++; }
        else if (line == "BLOCK") { blk = learn::parse_block(read_until_end()); have_blk = true; }
        else if (line.rfind("X ", 0) == 0) {
            auto const& x = enc->observe(blk);
            std::istringstream in(line.substr(2)); long v; int k = 0, mism = 0, first = -1;
            while (in >> v) { if (k >= learn::N_X || x[k] != v) { mism++; if (first < 0) first = k; } k++; }
            if (k != learn::N_X) mism++;
            turns++;
            if (mism) { if (bad < 5) std::cerr << "turn " << turns << " mismatches " << mism << " first col " << first
                                               << " cpp " << (first >= 0 && first < learn::N_X ? x[first] : -12345) << "\n"; bad++; }
        } else if (line.rfind("ACT ", 0) == 0) {
            std::istringstream in(line.substr(4)); int kind, f, n, r; in >> kind >> f >> n >> r; enc->act(kind, f, n, r);
        }
    }
    std::cout << "processes " << procs << " turns " << turns << " mismatched " << bad << " N_X " << learn::N_X << "\n";
    return bad ? 1 : 0;
}
