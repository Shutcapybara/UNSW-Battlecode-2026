// Verso tier 3 (B): hindsight search. For each logged dragon-turn, the best value of each first step F/R/L over
// the *recorded* next rounds — true terrain, every other dragon moving as it did, pearls appearing as they did —
// with only this dragon's path varied. One-step moves only (no sprint, no split).
//
//   hindsight TAPE QUERIES N OUT HORIZON GAMMA UNIT [GAMMA_DEATH [P_ADJ [ESC [RHO [KAPPA]]]]]
//     TAPE     written by tools/verso/relabel.py (tape()): terrain, per-round occupancy / pearls / eaters / heads
//     QUERIES  int32 [N, 5] = round, dragon id, length, head cell, facing (0..3 = N E S W)
//     OUT      float32 [N, 9] = per first step k in F, R, L: value, alive (1 = some path survives the horizon),
//              pearls on the best path
//
// Model (dragons act in ascending id within a round; S_r = state at the first turn of round r):
//   a cell is blocked for dragon d moving in round r if another dragon that moves later holds it in S_r, or one
//   that moves earlier holds it in S_{r+1}; d's own initial body frees segment i (from the tail) at step i + 2;
//   a head-to-head kills both dragons whatever their lengths and is scored as a trade (their material for ours
//   if an enemy). The recorded ram on this dragon, if any, is reactive: it kills wherever the dragon stands within
//   the attacker's reach at that moment. An enemy head that enters a cell we would occupy is a head-to-head with
//   probability PADJ; an ally is assumed to see us and yield. A pearl is there if it is in S_r and no earlier mover ate it this round, or
//   if d itself ate it later in the record (it would still be lying there).
//   value = sum gamma^(j-1) pearl_j  -  gamma_death^(j-1) loss if the path ends at step j, where loss is the
//   dragon (length + UNIT) when it is rammed or shorter than 4, and ESC (the stub of an escape split) when a
//   dragon of length >= 4, counting what it ate on the way, merely runs out of moves.
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
    std::vector<int32_t> atk;        // [n, 5] round, cell, attacker, victim, steps: a head-to-head into the victim's head
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
    if (std::fread(h, 4, 9, f) != 9 || h[0] != 0x34544856) return 1;
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
    rd(f, t.atk, static_cast<size_t>(n_atk) * 5);
    std::fclose(f);

    const int N = std::atoi(argv[3]);
    const int HOR = std::atoi(argv[5]);
    const double GAMMA = std::atof(argv[6]), UNIT = std::atof(argv[7]);
    const double GD = argc > 8 ? std::atof(argv[8]) : GAMMA;   // discount of the death / trade term
    const double PADJ = argc > 9 ? std::atof(argv[9]) : 0.5;   // P(head-to-head) when an enemy head enters our cell
    // A dragon of length >= 4 that runs out of moves is not lost: Ares's escape split sends the rear out as a new
    // dragon and only the two-segment stub dies. ESC is that cost; < 0 disables (every dead end is a full loss).
    const double ESC = argc > 10 ? std::atof(argv[10]) : 2.0;
    // Tempo credit (S-1 T: net income = pearls eaten minus *unrecovered* loss): RHO is the share of a dead
    // dragon's length the side does not eat back, KAPPA the share of a killed enemy's length it does eat.
    // RHO = 1, KAPPA = 1 with UNIT = 3 is the plain material form.
    const double RHO = argc > 11 ? std::atof(argv[11]) : 1.0;
    const double KAPPA = argc > 12 ? std::atof(argv[12]) : 1.0;
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
    std::vector<int32_t> touched, zone;
    std::vector<uint8_t> inzone(NC, 0);
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
        const double DEATH = RHO * len + UNIT;
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
        // Recorded head-to-heads involving this dragon (both die, whatever the lengths). As the attacker: the
        // victim's head is still there. As the victim: the ram followed us, so it is not pinned on the cell we
        // took — it kills wherever we stand within the attacker's reach (the steps its ram used) at that moment.
        int hit_round = -1, hit_by = -1, ram_round = -1, ram_cell = -1, ram_into = -1;
        for (int c : zone) inzone[c] = 0;
        zone.clear();
        for (size_t e = 0; e < t.atk.size() / 5; e++) {
            if (t.atk[e * 5] < r0) continue;
            if (t.atk[e * 5 + 3] == d && hit_round < 0) {
                hit_by = t.atk[e * 5 + 2];
                const int ra = t.atk[e * 5];
                hit_round = hit_by < d ? ra - 1 : ra;   // our move after which the ram arrives
                const int src = t.head[static_cast<size_t>(ra) * t.NID + hit_by];
                if (src >= 0) {   // cells within `steps` of the attacker's head at the start of its turn
                    std::vector<int> cur{src}, nxt;
                    for (int st = 0; st < t.atk[e * 5 + 4]; st++) {
                        nxt.clear();
                        for (int c : cur)
                            for (int dd = 0; dd < 4; dd++) {
                                int n = t.dest[c * 4 + dd];
                                if (n >= 0 && !inzone[n]) { inzone[n] = 1; zone.push_back(n); nxt.push_back(n); }
                            }
                        cur.swap(nxt);
                    }
                } else {
                    int c = t.atk[e * 5 + 1];
                    inzone[c] = 1; zone.push_back(c);
                }
            }
            if (t.atk[e * 5 + 2] == d && ram_round < 0) {
                ram_round = t.atk[e * 5]; ram_cell = t.atk[e * 5 + 1]; ram_into = t.atk[e * 5 + 3];
            }
        }
        auto len_at = [&](int x, int r) {
            return t.body_off[static_cast<size_t>(r) * t.NID + x + 1] - t.body_off[static_cast<size_t>(r) * t.NID + x];
        };
        // material swing of a head-to-head with dragon x around round r, beyond our own loss
        auto trade = [&](int x, int r) {
            int l = len_at(x, r);
            if (!l && r > 0) l = len_at(x, r - 1);
            return t.team[x] != t.team[d] ? KAPPA * l + UNIT : -(RHO * l + UNIT);
        };

        // Try to enter cell n at step j (round r = r0 + j - 1): 0 illegal (death on the spot), 1 ok, 2 ok but the
        // dragon dies after the step (rammed). `pearl`: a pearl is eaten; `credit`: the other side of a trade;
        // `risk`: expected value of a possible head-to-head with an enemy head that enters this cell (<= 0 mostly).
        auto enter = [&](int n, int j, bool& pearl, double& credit, double& risk) -> int {
            const int r = r0 + j - 1;
            pearl = false; credit = 0.0; risk = 0.0;
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
            if (r == hit_round && inzone[n]) { credit = trade(hit_by, r); return 2; }
            // an enemy head that moves into this cell after us (this round, or next round before our turn)
            if (y && y - 1 != d && t.team[y - 1] != t.team[d] &&
                t.head[static_cast<size_t>(r + 1) * t.NID + (y - 1)] == n &&
                t.head[static_cast<size_t>(r) * t.NID + (y - 1)] != n)
                risk += PADJ * (trade(y - 1, r + 1) - DEATH);
            if (r + 2 < t.NR) {
                const uint16_t z = t.occ[static_cast<size_t>(r + 2) * NC + n];
                if (z && z - 1 != d && z - 1 < d && t.team[z - 1] != t.team[d] &&
                    t.head[static_cast<size_t>(r + 2) * t.NID + (z - 1)] == n &&
                    t.head[static_cast<size_t>(r + 1) * t.NID + (z - 1)] != n)
                    risk += PADJ * (trade(z - 1, r + 2) - DEATH);
            }
            return 1;
        };

        for (int k = 0; k < 3; k++) {
            double best_alive = -1e18, best_dead = -1e18;
            float pearls_alive = 0.f, pearls_dead = 0.f;
            const int dir0 = (f0 + OFF[k]) & 3;
            bool pearl;
            double credit, risk;
            if (hmax < 1) { o[k * 3] = 0.f; o[k * 3 + 1] = 1.f; o[k * 3 + 2] = 0.f; continue; }
            const int n0 = t.dest[h0 * 4 + dir0];
            const int e0 = enter(n0, 1, pearl, credit, risk);
            if (e0 == 0) { o[k * 3] = static_cast<float>(credit - DEATH); o[k * 3 + 1] = 0.f; o[k * 3 + 2] = 0.f; continue; }
            if (e0 == 2) {
                o[k * 3] = static_cast<float>((pearl ? 1.0 : 0.0) + credit - DEATH); o[k * 3 + 1] = 0.f; o[k * 3 + 2] = pearl;
                continue;
            }
            gen++;
            front.clear();
            int s0 = n0 * 4 + dir0;
            val[s0] = (pearl ? 1.0 : 0.0) + risk; vpearl[s0] = pearl ? 1.f : 0.f; stamp[s0] = gen;
            front.push_back(s0);
            double g = 1.0, gd = 1.0;
            for (int j = 2; j <= hmax && !front.empty(); j++) {
                g *= GAMMA; gd *= GD;
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
                        double cr, rk;
                        const int e = enter(n, j, p2, cr, rk);
                        if (e == 0) {
                            // a deliberate head-to-head is a move too: both die, the trade is the value
                            if (cr != 0.0 && v + gd * (cr - DEATH) > best_dead) { best_dead = v + gd * (cr - DEATH); pearls_dead = vpearl[s]; }
                            continue;
                        }
                        const double nv = v + (p2 ? g : 0.0) + gd * rk;
                        const float np = vpearl[s] + (p2 ? 1.f : 0.f);
                        if (e == 2) {   // dies after this step
                            if (nv + gd * (cr - DEATH) > best_dead) { best_dead = nv + gd * (cr - DEATH); pearls_dead = np; }
                            any = true;   // it was a legal move, just a fatal one
                            continue;
                        }
                        any = true;
                        const int ns = n * 4 + dd;
                        if (nstamp[ns] != gen) { nstamp[ns] = gen; nval[ns] = nv; npearl[ns] = np; nfront.push_back(ns); }
                        else if (nv > nval[ns]) { nval[ns] = nv; npearl[ns] = np; }
                    }
                    if (!any) {   // stuck: a full loss, or the escape split if the dragon (with what it ate) is long enough
                        const double loss = (ESC >= 0.0 && len + vpearl[s] >= 4) ? ESC : DEATH;
                        if (v - gd * loss > best_dead) { best_dead = v - gd * loss; pearls_dead = vpearl[s]; }
                    }
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
