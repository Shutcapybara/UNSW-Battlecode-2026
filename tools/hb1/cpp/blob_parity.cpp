// HB-1: check the memory-mapped direction blob (hb1-03) against XGBoost margins.
//   g++ -O2 -std=c++20 -I bots/hb1-03-direction-scaled tools/hb1/cpp/blob_parity.cpp -o build/hb1/blob_parity
//   build/hb1/blob_parity build/hb1/export/direction_v03.bin build/hb1/export/direction_v03_check.csv
#include <fstream>
#include <iostream>
#include <sstream>
#include "hb1_gbt.hpp"
#include "hb1_blob.hpp"

int main(int argc, char** argv) {
    hb1::BlobModel bm(argv[1]);
    hb1::Model const& m = bm.model;
    std::ifstream in(argv[2]);
    std::string line;
    std::getline(in, line);
    std::vector<std::string> hdr;
    { std::stringstream ss(line); for (std::string t; std::getline(ss, t, ',');) hdr.push_back(t); }
    for (int i = 0; i < m.n_feat; i++)
        if (hdr[i] != m.feats[i]) { std::cerr << "column order mismatch at " << i << "\n"; return 1; }
    int rows = 0, bad = 0;
    double worst = 0;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::vector<double> v;
        for (std::string t; std::getline(ss, t, ',');) v.push_back(t.empty() ? NAN : std::stod(t));
        std::vector<float> x(v.begin(), v.begin() + m.n_feat);
        auto s = hb1::margins(m, x);
        for (int k = 0; k < m.K; k++) {
            double d = std::abs(s[k] - v[m.n_feat + k]);
            worst = std::max(worst, d);
            if (d > 1e-3) { bad++; break; }
        }
        rows++;
    }
    std::cout << "blob " << m.n_trees << " trees: rows " << rows << " margin mismatches " << bad << " worst |diff| " << worst
              << (bad ? "  MISMATCH" : "  ALL MATCH") << "\n";
    return bad != 0;
}
