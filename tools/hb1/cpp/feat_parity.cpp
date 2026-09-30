// HB-1: run the C++ feature mirror (bots/hb1-01-structured/hb1_features.hpp) over blocks dumped by
// dump_blocks.py and print one CSV row per actor turn, for comparison with the Python v5 rows.
//   g++ -O2 -std=c++20 -I bots/hb1-01-structured tools/hb1/cpp/feat_parity.cpp -o build/hb1/feat_parity
//   build/hb1/feat_parity < blocks.txt > rows.csv
#include <iostream>
#include <sstream>
#include "hb1_features.hpp"

static std::vector<std::string> split_ws(std::string const& s) {
    std::istringstream is(s);
    std::vector<std::string> v;
    for (std::string t; is >> t;) v.push_back(t);
    return v;
}

static hb1::Block parse_block(std::vector<std::string> const& L) {
    hb1::Block b;
    size_t i = 0;
    auto kv = [&](char const* k) {
        auto p = split_ws(L[i++]);
        if (p.empty() || p[0] != k) throw std::runtime_error(std::string("expected ") + k);
        return p;
    };
    b.round = std::stoi(kv("ROUND")[1]);
    b.dir = kv("DIR")[1][0];
    b.length = std::stoi(kv("LENGTH")[1]);
    b.units = std::stoi(kv("UNIT_COUNT")[1]);
    b.n_msgs = std::stoi(kv("NUM_MSGS")[1]);
    i += b.n_msgs;
    if (L[i].rfind("ECHOES", 0) == 0) {
        auto p = split_ws(L[i++]);
        b.has_echoes = true;
        for (int k = 0; k < 5; k++) b.echoes[k] = std::stoi(p[k + 1]);
    }
    for (int k = 0; k < 49; k++) {
        auto p = split_ws(L[i++]);
        b.tiles[k] = {std::stoi(p[0]), std::stoi(p[1]), std::stoi(p[2]), std::stoi(p[3])};
    }
    int nb = std::stoi(kv("DRAGON_BODIES")[1]);
    for (int k = 0; k < nb; k++) {
        auto p = split_ws(L[i++]);
        b.bodies.push_back({p[0][0], std::stoi(p[1]), std::stoi(p[2]), std::stoi(p[3]), p[4][0], p[5] == "1"});
    }
    for (int r = 0; r < 8; r++) {
        auto p = split_ws(L[i++]);
        for (int c = 0; c < 7; c++) b.Hm[r][c] = p[c];
    }
    for (int r = 0; r < 7; r++) {
        auto p = split_ws(L[i++]);
        for (int c = 0; c < 8; c++) b.Vm[r][c] = p[c];
    }
    return b;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::map<int, hb1::Proc> procs;
    std::vector<std::string> header;
    std::string line;
    int cur = -1;
    while (std::getline(std::cin, line)) {
        auto p = split_ws(line);
        if (p.empty()) continue;
        if (p[0] == "TURN") {
            cur = std::stoi(p[1]);
            int W = std::stoi(p[3]), H = std::stoi(p[4]), ul = std::stoi(p[5]);
            if (!procs.count(cur)) procs.emplace(cur, hb1::Proc(cur, p[2][0], W, H, ul));
            std::vector<std::string> blk;
            while (std::getline(std::cin, line) && line != "END") blk.push_back(line);
            hb1::Row row = procs.at(cur).features(parse_block(blk));
            if (header.empty()) {
                header = row.names;
                std::cout << "dragon";
                for (auto const& n : header) std::cout << "," << n;
                std::cout << "\n";
            }
            std::cout << cur;
            for (auto const& n : header) std::cout << "," << row.get(n);
            std::cout << "\n";
        } else if (p[0] == "ACT" && cur >= 0) {
            if (p[1] == "move") procs.at(cur).record_move(p[2]);
            else if (p[1] == "split") procs.at(cur).record_split(std::stoi(p[2]));
        }
    }
}
