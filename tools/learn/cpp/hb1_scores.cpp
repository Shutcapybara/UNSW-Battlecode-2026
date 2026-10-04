// HB-1 direction prior on teacher rows, through the bot's own C++ extractor (hb1_features.hpp) and the compact
// direction GBT (hb1_compact.hpp) of carthage-05: exactly what the parent's prior sees in play.
// Build: g++ -std=c++20 -O2 -I<bots/carthage-05-free-sprint> hb1_scores.cpp -o hb1_scores
// stdin:  per process "PROC" / "SPAWN" <spawn block> "END", then per turn "BLOCK" <block text> "END" and
//         "ACT m <rel steps>" | "ACT s <child>" | "ACT n" (the process's own action that turn)
// stdout: one line per turn "pF pR pL" (HB-1 probabilities over the forward three; reverse is not a class)
#include <cstdio>
#include <memory>
#include <algorithm>
#include <iostream>
#include <sstream>
#include "hb1_features.hpp"
#include "hb1_gbt.hpp"
#include "hb1_compact.hpp"

static std::vector<std::vector<std::string>> lines_of(std::string const& t) {
    std::vector<std::vector<std::string>> L; std::istringstream in(t); std::string l;
    while (std::getline(in, l)) { std::istringstream s(l); std::vector<std::string> p; std::string w; while (s >> w) p.push_back(w); if (!p.empty()) L.push_back(p); }
    return L;
}

static hb1::Block parse(std::string const& t) {
    auto L = lines_of(t); size_t i = 0; hb1::Block b;
    b.round = std::stoi(L[i++][1]); b.dir = L[i++][1][0]; b.length = std::stoi(L[i++][1]); b.units = std::stoi(L[i++][1]);
    b.n_msgs = std::stoi(L[i++][1]); i += b.n_msgs;
    // as the bot's hb1::block_from(ct, game) builds it: has_echoes always true (zeros when the line is absent),
    // bodies in window (tile) order, edge tokens verbatim
    b.has_echoes = true;
    if (L[i][0] == "ECHOES") { for (int j = 0; j < 5; j++) b.echoes[j] = std::stoi(L[i][1 + j]); i++; }
    for (int k = 0; k < 49; k++, i++) b.tiles[k] = {std::stoi(L[i][0]), std::stoi(L[i][1]), std::stoi(L[i][2]), std::stoi(L[i][3])};
    int m = std::stoi(L[i++][1]);
    std::vector<std::pair<int, hb1::BlockBody>> tmp;
    for (int j = 0; j < m; j++, i++) {
        hb1::BlockBody bb{L[i][0][0], std::stoi(L[i][1]), std::stoi(L[i][2]), std::stoi(L[i][3]), L[i][4][0], L[i][5] == "1"};
        int k = 0; while (k < 49 && !(b.tiles[k].x == bb.x && b.tiles[k].y == bb.y)) k++;
        tmp.push_back({k, bb});
    }
    std::stable_sort(tmp.begin(), tmp.end(), [](auto const& a, auto const& c) { return a.first < c.first; });
    for (auto& t : tmp) b.bodies.push_back(t.second);
    for (int r = 0; r < 8; r++, i++) for (int c = 0; c < 7; c++) b.Hm[r][c] = L[i][c];
    for (int r = 0; r < 7; r++, i++) for (int c = 0; c < 8; c++) b.Vm[r][c] = L[i][c];
    return b;
}

int main() {
    std::ios::sync_with_stdio(false);
    static hb1::Bound const bound{hb1::dirc_bind};
    std::unique_ptr<hb1::Proc> proc;
    std::string line;
    auto until_end = [&]() { std::string s, l; while (std::getline(std::cin, l) && l != "END") s += l + "\n"; return s; };
    while (std::getline(std::cin, line)) {
        if (line == "SPAWN") {
            auto L = lines_of(until_end());
            int id = 0, W = 0, H = 0, ul = 64; char team = 'A';
            for (auto& p : L) { if (p[0] == "ID") id = std::stoi(p[1]); else if (p[0] == "TEAM") team = p[1][0];
                                else if (p[0] == "MAP") { W = std::stoi(p[1]); H = std::stoi(p[2]); } else if (p[0] == "UNIT_LIMIT") ul = std::stoi(p[1]); }
            proc = std::make_unique<hb1::Proc>(id, team, W, H, ul);
        } else if (line == "BLOCK") {
            hb1::Row row = proc->features(parse(until_end()));
            auto p = hb1::dirc_proba(bound.vec(row));
            std::printf("%.6f %.6f %.6f\n", p[0], p[1], p[2]);
        } else if (line.rfind("ACT ", 0) == 0) {
            std::istringstream a(line.substr(4)); std::string k, v; a >> k >> v;
            if (k == "m" && !v.empty()) proc->record_move(v);
            else if (k == "s") proc->record_split(std::stoi(v));
        }
    }
    return 0;
}
