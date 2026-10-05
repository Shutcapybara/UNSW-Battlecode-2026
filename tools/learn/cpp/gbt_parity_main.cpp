// Prediction parity of an export_gbt.py header against its source model (tools/learn/gbt_parity.py drives it).
// Build: g++ -std=c++20 -O2 -DGBT_HEADER='"<model>.hpp"' -DGBT_NS=<ns> gbt_parity_main.cpp -o gbt_parity
// argv: X.f32 (n x N_FEAT float32, row-major) OUT.f64 (n x K)
#include <cstdio>
#include <vector>
#include GBT_HEADER
#include "gbt_compact.hpp"
int main(int argc, char** argv) {
    if (argc < 3) return 2;
    FILE* f = std::fopen(argv[1], "rb");
    std::vector<float> X;
    float buf[4096]; size_t r;
    while ((r = std::fread(buf, 4, 4096, f)) > 0) X.insert(X.end(), buf, buf + r);
    std::fclose(f);
    size_t n = X.size() / GBT_NS::N_FEAT;
    FILE* o = std::fopen(argv[2], "wb");
    for (size_t i = 0; i < n; i++) { double p[GBT_NS::K]; GBT_PROBA(GBT_NS, &X[i * GBT_NS::N_FEAT], p); std::fwrite(p, 8, GBT_NS::K, o); }
    std::fclose(o);
    return 0;
}
