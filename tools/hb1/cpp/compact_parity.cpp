// HB-1: the compact direction model (hb1-04) must reproduce the blob (hb1-03) exactly.
//   g++ -O2 -std=c++20 -I bots/hb1-04-deployable -I tools/hb1/cpp tools/hb1/cpp/compact_parity.cpp -o build/hb1/compact_parity
#include <fstream>
#include <iostream>
#include <sstream>
#include "hb1_gbt.hpp"
#include "hb1_blob.hpp"
#include "hb1_compact.hpp"

int main(int argc, char** argv) {
    hb1::BlobModel bm(argv[1]);
    std::ifstream in(argv[2]);
    std::string line;
    std::getline(in, line);
    for (int i = 0; i < hb1::dirc_n_feat; i++)
        if (std::string(bm.model.feats[i]) != hb1::dirc_feats[i]) { std::cerr << "feature order differs at " << i << "\n"; return 1; }
    long rows = 0, arg_diff = 0, acc_ok = 0;
    double worst = 0;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::vector<float> v;
        for (std::string t; std::getline(ss, t, ',');) v.push_back(t.empty() ? NAN : std::stof(t));
        int y = int(v.back());
        v.pop_back();
        auto a = hb1::proba(bm.model, v);
        auto b = hb1::dirc_proba(v);
        int ia = 0, ib = 0;
        for (int k = 1; k < 3; k++) { if (a[k] > a[ia]) ia = k; if (b[k] > b[ib]) ib = k; worst = std::max(worst, std::abs(a[k] - b[k])); }
        worst = std::max(worst, std::abs(a[0] - b[0]));
        arg_diff += ia != ib;
        acc_ok += hb1::dirc_classes[ib] == y;
        rows++;
    }
    std::cout << "rows " << rows << " argmax differences " << arg_diff << " worst |dp| " << worst << " compact accuracy "
              << double(acc_ok) / rows << (arg_diff ? "  MISMATCH" : "  EXACT") << "\n";
    return arg_diff != 0;
}
