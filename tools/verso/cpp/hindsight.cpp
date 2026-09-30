// Verso tier 3 (B): hindsight search. For each logged dragon-turn, the best value of each first step F/R/L over
// the *recorded* next rounds — true terrain, every other dragon moving as it did, pearls appearing as they did —
// with only this dragon's path varied. One-step moves only (no sprint, no split).
//
//   hindsight TAPE QUERIES N OUT HORIZON GAMMA UNIT
//     TAPE     written by tools/verso/relabel.py (tape()): terrain, per-round occupancy / pearls / eaters / heads
//     QUERIES  int32 [N, 5] = round, dragon id, length, head cell, facing (0..3 = N E S W)
//     OUT      float32 [N, 9] = per first step k in F, R, L: value, alive (1 = some path survives the horizon),
//              pearls on the best path
//
// Model (dragons act in ascending id within a round; S_r = state at the first turn of round r):
//   a cell is blocked for dragon d moving in round r if another dragon that moves later holds it in S_r, or one
//   that moves earlier holds it in S_{r+1}; d's own initial body frees segment i (from the tail) at step i + 2;
//   entering a cell that a later mover's head enters this round, or that an earlier mover's head enters next
//   round, is a head-to-head: death (both die, whatever the lengths). The recorded ram on this dragon, if any,
//   still hits the same cell at the same time: standing there is death, standing elsewhere is not. A pearl is there if it is in S_r and no earlier mover ate it this round, or
//   if d itself ate it later in the record (it would still be lying there).
//   value = sum gamma^(j-1) pearl_j  -  gamma^(j-1) (length + UNIT) if the path dies at step j.
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

struct Tape {
    int W = 0, H = 0, NC = 0, NR = 0, NID = 0;
    std::vector<int32_t> dest;       // NC * 4
    std::vector<uint16_t> occ;       // NR * NC : id + 1
    std::vector<uint8_t> pearl;      // NR * NC
    std::vector<uint16_t> eater;     // NR * NC : id + 1 of the dragon that ate the pearl here in round r
    std::vector<int32_t> head;       // NR * NID : head cell or -1
    std::vector<int32_t> parent;     // NID
    std::vector<int32_t> born;       // NID
    std::vector<int32_t> team;       // NID
    std::vector<int32_t> body_off;   // NR * NID + 1
    std::vector<int32_t> body;       // head first
    std::vector<int32_t> own_eat;    // [n, 3] round, cell, id (sorted by id, round)
    std::vector<int32_t> atk;        // [n, 4] round, cell, attacker, victim: a head-to-head into the victim's head
};

template <class T> static void rd(FILE* f, std::vector<T>& v, size_t n) {
    v.resize(n);
    if (n && std::fread(v.data(), sizeof(T), n, f) != n) { std::fprintf(stderr, "tape: short read\n"); std::exit(1); }
}

int main(int argc, char** argv) {
    if (argc < 8) return 2;
    Tape t;
    FILE* f = std::fopen(argv[1], "rb");
    if (!f) return 1;
    int32_t h[9];
    if (std::fread(h, 4, 9, f) != 9 || h[0] != 0x33544856) return 1;
    t.W = h[1]; t.H = h[2]; t.NC = h[3]; t.NR = h[4]; t.NID = h[5];
    const int n_body = h[6], n_eat = h[7], n_atk = h[8];
    rd(f, t.dest, static_cast<size_t>(t.NC) * 4);
    rd(f, t.occ, static_cast<size_t>(t.NR) * t.NC);
    rd(f, t.pearl, static_cast<size_t>(t.NR) * t.NC);
    rd(f, t.eater, static_cast<size_t>(t.NR) * t.NC);
    rd(f, t.head, static_cast<size_t>(t.NR) * t.NID);
    rd(f, t.parent, t.NID);
    rd(f, t.born, t.NID);
    rd(f, t.team, t.NID);
    rd(f, t.body_off, static_cast<size_t>(t.NR) * t.NID + 1);
    rd(f, t.body, n_body);
    rd(f, t.own_eat, static_cast<size_t>(n_eat) * 3);
    rd(f, t.atk, static_cast<size_t>(n_atk) * 4);
    std::fclose(f);

    const int N = std::atoi(argv[3]);
    const int HOR = std::atoi(argv[5]);
    const double GAMMA = std::atof(argv[6]), UNIT = std::atof(argv[7]);
    std::vector<int32_t> Q;
    f = std::fopen(argv[2], "rb");
    if (!f) return 1;
    rd(f, Q, static_cast<size_t>(N) * 5);
    std::fclose(f);
    std::vector<float> out(static_cast<size_t>(N) * 9, 0.f);

    const int NC = t.NC, NS = NC * 4;
    std::vector<double> val(NS), nval(NS);
    std::vector<float> npearl(NS), vpearl(NS);
    std::vector<int32_t> stamp(NS, -1), nstamp(NS, -1), front, nfront;
    std::vector<uint16_t> mask(NC, 0);      // own initial body: blocked for steps < mask
    std::vector<int32_t> extra(NC, -1);     // pearls d ate itself in the record: round eaten (-1 none)
    std::vector<int32_t> touched;
    static const int OFF[3] = {0, 1, 3};
    int gen = 0;

    auto rank_earlier = [&](int x, int d, int r) {   // does dragon x act before d in round r?
        int rx = (t.born[x] == r && t.parent[x] >= 0) ? t.parent[x] : x;   // a newborn exists once its parent has acted
        return rx < d;
    };

    for (int qi = 0; qi < N; qi++) {
        const int r0 = Q[qi * 5], d = Q[qi * 5 + 1], len = Q[qi * 5 + 2], h0 = Q[qi * 5 + 3], f0 = Q[qi * 5 + 4];
        float* o = out.data() + static_cast<size_t>(qi) * 9;
        if (r0 < 0 || r0 >= t.NR - 1 || d < 0 || d >= t.NID || h0 < 0 || h0 >= NC) {
            for (int k = 0; k < 9; k++) o[k] = std::nanf("");
            continue;
        }
        const double DEATH = len + UNIT;
        // own initial body mask
        for (int c : touched) { mask[c] = 0; extra[c] = -1; }
        touched.clear();
        {
            const int b0 = t.body_off[static_cast<size_t>(r0) * t.NID + d], b1 = t.body_off[static_cast<size_t>(r0) * t.NID + d + 1];
            const int L = b1 - b0;
            for (int i = 0; i < L; i++) {   // i = 0 head ... L-1 tail; segment (L-1-i) from the tail frees at step (L-1-i) + 2
                int c = t.body[b0 + i];
                mask[c] = static_cast<uint16_t>((L - 1 - i) + 2);
                touched.push_back(c);
            }
        }
        for (size_t e = 0; e < t.own_eat.size() / 3; e++)
            if (t.own_eat[e * 3 + 2] == d && t.own_eat[e * 3] >= r0) {
                int c = t.own_eat[e * 3 + 1];
                if (extra[c] < 0) { extra[c] = t.own_eat[e * 3]; touched.push_back(c); }
            }
        const int hmax = std::min(HOR, t.NR - 1 - r0);
        // Recorded head-to-heads involving this dragon (both die, whatever the lengths). As the victim: the
        // attacker still rams that cell at that time. As the attacker: the victim's head is still there.
        int hit_round = -1, hit_cell = -1, hit_by = -1, ram_round = -1, ram_cell = -1, ram_into = -1;
        for (size_t e = 0; e < t.atk.size() / 4; e++) {
            if (t.atk[e * 4] < r0) continue;
            if (t.atk[e * 4 + 3] == d && hit_round < 0) {
                hit_by = t.atk[e * 4 + 2];
                hit_round = hit_by < d ? t.atk[e * 4] - 1 : t.atk[e * 4];   // our move after which we stand there
                hit_cell = t.atk[e * 4 + 1];
            }
            if (t.atk[e * 4 + 2] == d && ram_round < 0) {
                ram_round = t.atk[e * 4]; ram_cell = t.atk[e * 4 + 1]; ram_into = t.atk[e * 4 + 3];
            }
        }
        auto len_at = [&](int x, int r) {
            return t.body_off[static_cast<size_t>(r) * t.NID + x + 1] - t.body_off[static_cast<size_t>(r) * t.NID + x];
        };
        // material swing of a head-to-head with dragon x around round r, beyond our own loss
        auto trade = [&](int x, int r) {
            int l = len_at(x, r);
            if (!l && r > 0) l = len_at(x, r - 1);
            const double v = l + UNIT;
            return t.team[x] != t.team[d] ? v : -v;
        };

        // Try to enter cell n at step j (round r = r0 + j - 1): 0 illegal (death on the spot), 1 ok, 2 ok but the
        // dragon dies after the step (head-to-head). `pearl`: a pearl is eaten; `credit`: the other side of a trade.
        auto enter = [&](int n, int j, bool& pearl, double& credit) -> int {
            const int r = r0 + j - 1;
            pearl = false; credit = 0.0;
            if (n < 0) return 0;
            if (mask[n] > j) return 0;
            if (r == ram_round && n == ram_cell) { credit = trade(ram_into, r); return 0; }
            const uint16_t x = t.occ[static_cast<size_t>(r) * NC + n];
            if (x && x - 1 != d && !rank_earlier(x - 1, d, r)) {
                if (t.head[static_cast<size_t>(r) * t.NID + (x - 1)] == n) credit = trade(x - 1, r);
                return 0;
            }
            const uint16_t y = t.occ[static_cast<size_t>(r + 1) * NC + n];
            if (y && y - 1 != d && rank_earlier(y - 1, d, r)) {
                if (t.head[static_cast<size_t>(r + 1) * t.NID + (y - 1)] == n) credit = trade(y - 1, r + 1);
                return 0;
            }
            if (t.pearl[static_cast<size_t>(r) * NC + n]) {
                const uint16_t e = t.eater[static_cast<size_t>(r) * NC + n];
                pearl = !(e && e - 1 != d && rank_earlier(e - 1, d, r));
            }
            if (!pearl && extra[n] >= 0 && extra[n] < r) pearl = true;
            if (r == hit_round && n == hit_cell) { credit = trade(hit_by, r); return 2; }
            // a later mover's head arrives here this round, or an earlier mover's next round
            if (y && y - 1 != d && t.head[static_cast<size_t>(r + 1) * t.NID + (y - 1)] == n &&
                t.head[static_cast<size_t>(r) * t.NID + (y - 1)] != n) {
                credit = trade(y - 1, r + 1);
                return 2;
            }
            if (r + 2 < t.NR) {
                const uint16_t z = t.occ[static_cast<size_t>(r + 2) * NC + n];
                if (z && z - 1 != d && z - 1 < d && t.head[static_cast<size_t>(r + 2) * t.NID + (z - 1)] == n &&
                    t.head[static_cast<size_t>(r + 1) * t.NID + (z - 1)] != n) {
                    credit = trade(z - 1, r + 2);
                    return 2;
                }
            }
            return 1;
        };

        for (int k = 0; k < 3; k++) {
            double best_alive = -1e18, best_dead = -1e18;
            float pearls_alive = 0.f, pearls_dead = 0.f;
            const int dir0 = (f0 + OFF[k]) & 3;
            bool pearl;
            double credit;
            if (hmax < 1) { o[k * 3] = 0.f; o[k * 3 + 1] = 1.f; o[k * 3 + 2] = 0.f; continue; }
            const int n0 = t.dest[h0 * 4 + dir0];
            const int e0 = enter(n0, 1, pearl, credit);
            if (e0 == 0) { o[k * 3] = static_cast<float>(credit - DEATH); o[k * 3 + 1] = 0.f; o[k * 3 + 2] = 0.f; continue; }
            if (e0 == 2) {
                o[k * 3] = static_cast<float>((pearl ? 1.0 : 0.0) + credit - DEATH); o[k * 3 + 1] = 0.f; o[k * 3 + 2] = pearl;
                continue;
            }
            gen++;
            front.clear();
            int s0 = n0 * 4 + dir0;
            val[s0] = pearl ? 1.0 : 0.0; vpearl[s0] = pearl ? 1.f : 0.f; stamp[s0] = gen;
            front.push_back(s0);
            double g = 1.0;
            for (int j = 2; j <= hmax && !front.empty(); j++) {
                g *= GAMMA;
                gen++;
                nfront.clear();
                for (int s : front) {
                    const int c = s >> 2, fc = s & 3;
                    const double v = val[s];
                    bool any = false;
                    for (int kk = 0; kk < 3; kk++) {
                        const int dd = (fc + OFF[kk]) & 3;
                        const int n = t.dest[c * 4 + dd];
                        bool p2;
                        double cr;
                        const int e = enter(n, j, p2, cr);
                        if (e == 0) {
                            // a deliberate head-to-head is a move too: both die, the trade is the value
                            if (cr != 0.0 && v + g * (cr - DEATH) > best_dead) { best_dead = v + g * (cr - DEATH); pearls_dead = vpearl[s]; }
                            continue;
                        }
                        const double nv = v + (p2 ? g : 0.0);
                        const float np = vpearl[s] + (p2 ? 1.f : 0.f);
                        if (e == 2) {   // dies after this step
                            if (nv + g * (cr - DEATH) > best_dead) { best_dead = nv + g * (cr - DEATH); pearls_dead = np; }
                            any = true;   // it was a legal move, just a fatal one
                            continue;
                        }
                        any = true;
                        const int ns = n * 4 + dd;
                        if (nstamp[ns] != gen) { nstamp[ns] = gen; nval[ns] = nv; npearl[ns] = np; nfront.push_back(ns); }
                        else if (nv > nval[ns]) { nval[ns] = nv; npearl[ns] = np; }
                    }
                    if (!any && v - g * DEATH > best_dead) { best_dead = v - g * DEATH; pearls_dead = vpearl[s]; }
                }
                front.swap(nfront);
                val.swap(nval); vpearl.swap(npearl); stamp.swap(nstamp);
            }
            for (int s : front)
                if (val[s] > best_alive) { best_alive = val[s]; pearls_alive = vpearl[s]; }
            // the value is the best of surviving and of a (favourable) trade; `alive` says a surviving path exists
            const bool alive = best_alive > -1e17;
            const bool use_dead = best_dead > best_alive;
            o[k * 3] = static_cast<float>(use_dead ? best_dead : best_alive);
            o[k * 3 + 1] = alive ? 1.f : 0.f;
            o[k * 3 + 2] = use_dead ? pearls_dead : pearls_alive;
        }
    }
    f = std::fopen(argv[4], "wb");
    std::fwrite(out.data(), 4, out.size(), f);
    std::fclose(f);
    return 0;
}
