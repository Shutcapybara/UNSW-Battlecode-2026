// HB-1: accuracy of a truncated direction blob vs number of boosting rounds kept, on labelled held-out rows.
//   g++ -O2 -std=c++20 -I bots/hb1-03-direction-scaled tools/hb1/cpp/blob_curve.cpp -o build/hb1/blob_curve
//   build/hb1/blob_curve BLOB ROWS.csv   (ROWS: model feature columns then __label)
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
    std::vector<std::vector<float>> X;
    std::vector<int> y;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::vector<float> v;
        for (std::string t; std::getline(ss, t, ',');) v.push_back(t.empty() ? NAN : std::stof(t));
        y.push_back(int(v.back()));
        v.pop_back();
        X.push_back(std::move(v));
    }
    size_t n = X.size();
    std::vector<std::array<double, 3>> s(n);
    for (size_t i = 0; i < n; i++) for (int k = 0; k < 3; k++) s[i][k] = m.base[k];
    int rounds = m.n_trees / m.K;
    long nodes = 0;
    std::cout << "rounds,trees,nodes,acc\n";
    for (int t = 0; t < m.n_trees; t++) {
        hb1::Node const* nd = m.nodes + m.tree_start[t];
        int tree_nodes = (t + 1 < m.n_trees ? m.tree_start[t + 1] : m.tree_start[t] + 1) - m.tree_start[t];
        nodes += tree_nodes;
        for (size_t i = 0; i < n; i++) {
            int j = 0;
            while (nd[j].f >= 0) { float v = X[i][nd[j].f]; j = std::isnan(v) ? nd[j].miss : (v < nd[j].t ? nd[j].yes : nd[j].no); }
            s[i][t % 3] += nd[j].leaf;
        }
        int r = t / 3 + 1;
        if (t % 3 == 2 && (r % 100 == 0 || r == rounds || r == 300)) {
            size_t ok = 0;
            for (size_t i = 0; i < n; i++) {
                int a = 0;
                for (int k = 1; k < 3; k++) if (s[i][k] > s[i][a]) a = k;
                ok += m.classes[a] == y[i];
            }
            std::cout << r << "," << t + 1 << "," << nodes << "," << double(ok) / n << "\n" << std::flush;
        }
    }
}
