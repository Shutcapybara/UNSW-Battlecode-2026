// Parity harness for learn_traj.hpp: fixture on stdin from tools/learn/test_traj_parity.py.
// Per process "SPAWN" <lines> "END", then per turn "BLOCK" <lines> "END" and "T v0 .. v6".
#include <iostream>
#include <memory>
#include "learn_traj.hpp"
int main() {
    std::string line; long turns = 0, bad = 0, procs = 0;
    std::unique_ptr<learn::Traj> t; learn::Block blk;
    auto read_until_end = [&]() { std::string s, l; while (std::getline(std::cin, l) && l != "END") s += l + "\n"; return s; };
    while (std::getline(std::cin, line)) {
        if (line == "SPAWN") { t = std::make_unique<learn::Traj>(learn::parse_spawn(read_until_end())); procs++; }
        else if (line == "BLOCK") blk = learn::parse_block(read_until_end());
        else if (line.rfind("T ", 0) == 0) {
            auto const& v = t->observe(blk);
            std::istringstream in(line.substr(2)); long x; int k = 0, mism = 0;
            while (in >> x) { if (k >= learn::N_T || v[k] != x) mism++; k++; }
            if (k != learn::N_T) mism++;
            turns++;
            if (mism) { if (bad < 5) std::cerr << "turn " << turns << " mismatches " << mism << "\n"; bad++; }
        }
    }
    std::cout << "processes " << procs << " turns " << turns << " mismatched " << bad << " N_T " << learn::N_T << "\n";
    return bad ? 1 : 0;
}
