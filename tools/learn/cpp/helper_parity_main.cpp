// One dragon process through the OFFICIAL helper: argv[1] = file with the spawn block, argv[2] = file with that
// process's blocks separated by blank lines, argv[3] = expected vectors (one "X ..." line per turn, with ACT lines).
// Checks encode(block_from(helper)) == expected. Build: g++ -std=c++20 -I<bot dir with helper.hpp> ...
#include <fstream>
#include <iostream>
#include <sstream>
#include "learn_helper.hpp"
int main(int argc, char** argv) {
    std::ifstream sp(argv[1]), bl(argv[2]), ex(argv[3]);
    std::stringstream input; input << sp.rdbuf() << bl.rdbuf() << "ENDGAME\n";
    std::cin.rdbuf(input.rdbuf());
    auto [ct, game] = unswbc::init();
    learn::Encoder enc(learn::spawn_from(ct, game));
    std::string line; long turns = 0, bad = 0;
    while (unswbc::update(ct, game)) {
        auto const& x = enc.observe(learn::block_from(ct, game));
        while (std::getline(ex, line) && line.rfind("X ", 0) != 0) {}
        std::istringstream in(line.substr(2)); long v; int k = 0, mism = 0;
        while (in >> v) { if (x[k] != v) mism++; k++; }
        turns++; if (mism) bad++;
        if (std::getline(ex, line) && line.rfind("ACT ", 0) == 0) {
            std::istringstream a(line.substr(4)); int kind, f, n, r; a >> kind >> f >> n >> r; enc.act(kind, f, n, r);
        }
    }
    std::cout << turns << " " << bad << "\n";
    return 0;
}
