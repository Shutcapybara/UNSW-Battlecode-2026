// Verso: margins of one head from the bot's own evaluator (verso.hpp), for tools/verso/export.py parity.
//   head_parity BLOB HEAD X.f32 N OUT.f64     (X: N rows of schema-ordered float32)
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "verso.hpp"

int main(int argc, char** argv) {
    if (argc < 6) return 2;
    verso::Cfg::policy_path = argv[1];
    verso::Model m;
    m.load();
    const verso::Head* h = m.find(argv[2]);
    if (!h) { std::fprintf(stderr, "no head %s\n", argv[2]); return 1; }
    const int nf = verso::Schema::get().n, n = std::atoi(argv[4]);
    std::vector<float> x(static_cast<size_t>(nf) * n);
    FILE* f = std::fopen(argv[3], "rb");
    if (!f || std::fread(x.data(), 4, x.size(), f) != x.size()) return 1;
    std::fclose(f);
    std::vector<double> out(static_cast<size_t>(h->K) * n);
    for (int i = 0; i < n; i++) h->margins(x.data() + static_cast<size_t>(i) * nf, out.data() + static_cast<size_t>(i) * h->K);
    f = std::fopen(argv[5], "wb");
    std::fwrite(out.data(), 8, out.size(), f);
    std::fclose(f);
    return 0;
}
