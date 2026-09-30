// HB-1: check the C++ evaluator against XGBoost margins on build/hb1/export/<model>_check.csv.
//   g++ -O2 -std=c++20 -I bots/hb1-01-structured tools/hb1/cpp/gbt_parity.cpp -o build/hb1/gbt_parity
#include <fstream>
#include <iostream>
#include <sstream>
#include "hb1_gbt.hpp"

static int check(hb1::Model const& m, std::string const& path) {
    std::ifstream in(path);
    std::string line;
    std::getline(in, line);
    std::vector<std::string> hdr;
    { std::stringstream ss(line); for (std::string t; std::getline(ss, t, ',');) hdr.push_back(t); }
    int rows = 0, bad = 0;
    double worst = 0;
    while (std::getline(in, line)) {
        std::stringstream ss(line);
        std::vector<double> v;
        for (std::string t; std::getline(ss, t, ',');) v.push_back(t.empty() ? NAN : std::stod(t));
        std::vector<float> x(v.begin(), v.begin() + m.n_feat);
        for (int i = 0; i < m.n_feat; i++)
            if (hdr[i] != m.feats[i]) { std::cerr << "column order mismatch at " << i << "\n"; return 1; }
        auto s = hb1::margins(m, x);
        for (int k = 0; k < m.K; k++) {
            double d = std::abs(s[k] - v[m.n_feat + k]);
            worst = std::max(worst, d);
            if (d > 1e-3) { bad++; break; }
        }
        rows++;
    }
    std::cout << m.name << ": rows " << rows << " margin mismatches " << bad << " worst |diff| " << worst << "\n";
    return bad != 0;
}

int main() {
    int f = 0;
    f |= check(hb1::gate_model, "build/hb1/export/gate_check.csv");
    f |= check(hb1::alloc_model, "build/hb1/export/alloc_check.csv");
    f |= check(hb1::direction_model, "build/hb1/export/direction_check.csv");
    f |= check(hb1::sonar_model, "build/hb1/export/sonar_check.csv");
    std::cout << (f ? "MISMATCH" : "ALL MATCH") << "\n";
    return f;
}
