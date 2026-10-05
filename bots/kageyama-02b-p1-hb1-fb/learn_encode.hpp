// Phase 3 observation encoder, C++ twin of tools/learn/encode.py (ENC_VERSION 1). Header-only, C++20, no deps.
// Must match the Python encoder bit for bit (tools/learn/test_parity.py + parity_main.cpp). Do not edit one side
// without the other; bump ENC_VERSION on any change.
//
//   learn::Spawn sp{id, team, W, H, unit_limit};
//   learn::Encoder enc(sp);
//   learn::Block b = learn::parse_block(text);     // or learn::block_from(ct, game) in a bot (learn_helper.hpp)
//   auto const& x = enc.observe(b);                // std::array<int32_t, learn::N_X>
//   enc.act(kind, first_rel, nsteps, round);       // the process's own action this turn
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace learn {

constexpr int ENC_VERSION = 1;
constexpr int N_CH = 23;
constexpr int N_SC = 66;
constexpr int N_X = 49 * N_CH + N_SC;
constexpr int UNSEEN = -1;
constexpr int BIG = 999;

struct Spawn { int id = 0; char team = 'A'; int W = 0, H = 0, unit_limit = 64; };
struct Tile { int x, y, pearl, pin; };
struct Part { char team; int id, x, y; char facing; int head; };
struct Block {
    int round = 0; char dir = 'N'; int length = 0, unit_count = 0;
    std::vector<uint64_t> msgs;
    bool has_echoes = false; std::array<int, 5> echoes{};
    std::array<Tile, 49> tiles{};
    std::vector<Part> parts;
    std::array<std::array<char, 7>, 8> hedge{};   // '.', 'w' or 'p' (portal)
    std::array<std::array<char, 8>, 7> vedge{};
};

inline int dir_index(char d) { return d == 'N' ? 0 : d == 'E' ? 1 : d == 'S' ? 2 : 3; }
inline constexpr int DX[4] = {0, 1, 0, -1};
inline constexpr int DY[4] = {-1, 0, 1, 0};
inline char edge_class(std::string_view tok) { return tok == "." ? '.' : tok == "w" ? 'w' : 'p'; }

inline Spawn parse_spawn(std::string const& text) {
    Spawn s; std::istringstream in(text); std::string k;
    while (in >> k) {
        if (k == "ID") in >> s.id;
        else if (k == "TEAM") in >> s.team;
        else if (k == "MAP") in >> s.W >> s.H;
        else if (k == "UNIT_LIMIT") in >> s.unit_limit;
    }
    return s;
}

inline Block parse_block(std::string const& text) {
    std::vector<std::vector<std::string>> L;
    std::istringstream in(text); std::string line;
    while (std::getline(in, line)) {
        if (auto c = line.find('#'); c != std::string::npos) line.erase(c);
        std::istringstream ls(line); std::vector<std::string> p; std::string t;
        while (ls >> t) p.push_back(t);
        if (!p.empty()) L.push_back(std::move(p));
    }
    std::size_t i = 0;
    Block b;
    b.round = std::stoi(L[i++][1]); b.dir = L[i++][1][0];
    b.length = std::stoi(L[i++][1]); b.unit_count = std::stoi(L[i++][1]);
    int k = std::stoi(L[i++][1]);
    for (int j = 0; j < k; j++) b.msgs.push_back(std::stoull(L[i++][0]));
    if (L[i][0] == "ECHOES") { b.has_echoes = true; for (int j = 0; j < 5; j++) b.echoes[j] = std::stoi(L[i][1 + j]); i++; }
    for (int j = 0; j < 49; j++, i++) b.tiles[j] = {std::stoi(L[i][0]), std::stoi(L[i][1]), std::stoi(L[i][2]), std::stoi(L[i][3])};
    int m = std::stoi(L[i++][1]);
    for (int j = 0; j < m; j++, i++)
        b.parts.push_back({L[i][0][0], std::stoi(L[i][1]), std::stoi(L[i][2]), std::stoi(L[i][3]), L[i][4][0], std::stoi(L[i][5])});
    for (int r = 0; r < 8; r++, i++) for (int c = 0; c < 7; c++) b.hedge[r][c] = edge_class(L[i][c]);
    for (int r = 0; r < 7; r++, i++) for (int c = 0; c < 8; c++) b.vedge[r][c] = edge_class(L[i][c]);
    return b;
}

class Encoder {
public:
    explicit Encoder(Spawn const& s) : id_(s.id), team_(s.team), W_(s.W), H_(s.H), limit_(s.unit_limit) {}

    // kind: 0 none, 1 move, 2 split, 3 invalid; first_rel 0..3 (F R B L) for a move
    void act(int kind, int first_rel = -1, int nsteps = 0, int round = -1) {
        last_kind_ = kind;
        last_first_ = kind == 1 ? first_rel : -1;
        last_nsteps_ = kind == 1 ? nsteps : 0;
        if (kind == 2) { last_split_round_ = round >= 0 ? round : cur_round_; has_split_ = true; }
    }

    std::array<int32_t, N_X> const& observe(Block const& b) {
        x_.fill(0);
        int const fac = dir_index(b.dir);
        cur_round_ = b.round;
        int const hx = b.tiles[24].x, hy = b.tiles[24].y;
        if (!started_) {
            started_ = true; first_round_ = b.round;
            if (b.round == 0) { has_home_ = true; home_x_ = hx; home_y_ = hy; my_queen_ = id_ % 2; }
        }
        for (auto const& p : b.parts)
            if ((p.id == 0 || p.id == 1) && !q_team_known_[p.id]) {
                q_team_known_[p.id] = true;
                if (my_queen_ < 0) my_queen_ = p.team == team_ ? p.id : 1 - p.id;
            }
        auto rot = [&](int dx, int dy, int& f, int& r) {
            int fx = DX[fac], fy = DY[fac], rx = -fy, ry = fx;
            f = dx * fx + dy * fy; r = dx * rx + dy * ry;
        };
        auto cell = [&](int dx, int dy) { int f, r; rot(dx, dy, f, r); return (3 - f) * 7 + (3 + r); };
        auto at = [&](int c, int ch) -> int32_t& { return x_[c * N_CH + ch]; };
        auto rel_dir = [&](int a) { return ((a - fac) % 4 + 4) % 4; };

        int n_pearls = 0, n_beds = 0, cd_known = 1, pearl_min = BIG;
        for (int k = 0; k < 49; k++) {
            int dx = k % 7 - 3, dy = k / 7 - 3, c = cell(dx, dy);
            auto const& t = b.tiles[k];
            if (t.pearl) { at(c, 8) = 1; n_pearls++; pearl_min = std::min(pearl_min, std::abs(dx) + std::abs(dy)); }
            if (t.pin >= 0 || t.pin == -2) {
                at(c, 9) = 1; n_beds++;
                at(c, 10) = t.pin >= 0 ? std::min(t.pin, 255) : 0;
                if (t.pin == -2) cd_known = 0;
            }
        }
        auto put_edge = [&](int c, int r, int absd, char tok) {
            if (c < 0 || c >= 7 || r < 0 || r >= 7 || tok == '.') return;
            at(cell(c - 3, r - 3), (tok == 'w' ? 0 : 4) + rel_dir(absd)) = 1;
        };
        for (int r = 0; r < 8; r++) for (int c = 0; c < 7; c++) { put_edge(c, r, 0, b.hedge[r][c]); put_edge(c, r - 1, 2, b.hedge[r][c]); }
        for (int r = 0; r < 7; r++) for (int c = 0; c < 8; c++) { put_edge(c, r, 3, b.vedge[r][c]); put_edge(c - 1, r, 1, b.vedge[r][c]); }

        auto widx = [&](int x, int y) {
            for (int k = 0; k < 49; k++) if (b.tiles[k].x == x && b.tiles[k].y == y) return k;
            return -1;
        };
        std::vector<std::pair<int, int>> order;   // (window index, part index), sorted by window index
        order.reserve(b.parts.size());
        for (int j = 0; j < (int)b.parts.size(); j++) order.push_back({widx(b.parts[j].x, b.parts[j].y), j});
        std::sort(order.begin(), order.end());
        int n_eh = 0, n_ah = 0, n_ep = 0, n_ap = 0, eh_min = BIG, ah_min = BIG, eh_d1 = 0;
        bool q_vis[2] = {false, false}; int q_parts[2] = {0, 0};
        bool q_pos_set[2] = {false, false}, q_pos_head[2] = {false, false}; int q_px[2] = {0, 0}, q_py[2] = {0, 0};
        std::vector<std::pair<int, int>> vis_len;   // (id, count) for enemy dragons
        auto wrapx = [&](int v) { return ((v % W_) + W_) % W_; };
        auto wrapy = [&](int v) { return ((v % H_) + H_) % H_; };
        auto adj_me = [&](int x, int y) {
            for (int a = 0; a < 4; a++) if (wrapx(hx + DX[a]) == x && wrapy(hy + DY[a]) == y) return true;
            return false;
        };
        for (auto const& [k, j] : order) {
            auto const& p = b.parts[j];
            int dx = k % 7 - 3, dy = k / 7 - 3, c = cell(dx, dy), d = std::abs(dx) + std::abs(dy);
            if (p.id == id_) { at(c, 11) = p.head ? 0 : 1; continue; }
            bool ally = p.team == team_;
            if (!ally) {
                auto it = std::find_if(vis_len.begin(), vis_len.end(), [&](auto const& q) { return q.first == p.id; });
                if (it == vis_len.end()) vis_len.push_back({p.id, 1}); else it->second++;
            }
            if (p.id == 0 || p.id == 1) {
                at(c, ally ? 16 : 17) = 1;
                q_parts[p.id]++;
                if (p.head) { q_pos_set[p.id] = true; q_pos_head[p.id] = true; q_px[p.id] = p.x; q_py[p.id] = p.y; }
                else if (!q_pos_set[p.id]) { q_pos_set[p.id] = true; q_px[p.id] = p.x; q_py[p.id] = p.y; }
                q_vis[p.id] = true;
            }
            if (p.head) {
                at(c, ally ? 13 : 15) = 1;
                at(c, 18 + rel_dir(dir_index(p.facing))) = 1;
                if (ally) { n_ah++; ah_min = std::min(ah_min, d); }
                else { n_eh++; eh_min = std::min(eh_min, d); if (d == 1) eh_d1++; }
            } else {
                at(c, ally ? 12 : 14) = 1;
                if (ally) n_ap++; else n_ep++;
                int a = dir_index(p.facing);
                if (adj_me(wrapx(p.x + DX[a]), wrapy(p.y + DY[a]))) at(c, 22) = 1;
            }
        }
        for (int q = 0; q < 2; q++) if (q_pos_set[q]) { q_seen_[q] = true; q_r_[q] = b.round; q_x_[q] = q_px[q]; q_y_[q] = q_py[q]; }
        if (id_ == 0 || id_ == 1) { q_seen_[id_] = true; q_r_[id_] = b.round; q_x_[id_] = hx; q_y_[id_] = hy; q_vis[id_] = true; }

        char he[4] = {b.hedge[3][3], b.vedge[3][4], b.hedge[4][3], b.vedge[3][3]};   // N E S W
        int ex_ord = 0, ex_por = 0, ex_rel[4] = {0, 0, 0, 0};
        for (int a = 0; a < 4; a++) {
            int ok = 0;
            if (he[a] == '.') {
                int nx = wrapx(hx + DX[a]), ny = wrapy(hy + DY[a]);
                bool occ = false;
                for (auto const& p : b.parts) if (p.x == nx && p.y == ny) { occ = true; break; }
                if (!occ) { ok = 1; ex_ord++; }
            } else if (he[a] != 'w') { ok = 1; ex_por++; }
            ex_rel[rel_dir(a)] = ok;
        }
        auto tor = [](int d, int n) { d = ((d % n) + n) % n; return d > n / 2 ? d - n : d; };
        int i = 49 * N_CH;
        auto push = [&](int v) { x_[i++] = v; };
        auto qfeat = [&](int q) {
            if (q < 0 || !q_seen_[q]) { push(UNSEEN); push(BIG); push(BIG); push(BIG); return; }
            int f, r; rot(tor(q_x_[q] - hx, W_), tor(q_y_[q] - hy, H_), f, r);
            push(b.round - q_r_[q]); push(f); push(r); push(std::abs(f) + std::abs(r));
        };
        auto cellf = [&](bool known, int cx, int cy) {
            if (!known) { push(BIG); push(BIG); push(BIG); return; }
            int f, r; rot(tor(cx - hx, W_), tor(cy - hy, H_), f, r);
            push(f); push(r); push(std::abs(f) + std::abs(r));
        };
        int const rnd = b.round;
        push(rnd); push(500 - rnd); push(rnd < 25 ? 0 : rnd < 100 ? 1 : rnd < 250 ? 2 : rnd < 400 ? 3 : 4);
        push(b.length); push(b.unit_count); push(limit_); push(limit_ - b.unit_count);
        push(b.length >= 4 && b.unit_count < limit_ ? 1 : 0);
        push(turn_); push(first_round_ > 0 ? 1 : 0); push(rnd - first_round_);
        push(has_split_ ? rnd - last_split_round_ : UNSEEN);
        push(last_kind_); push(last_first_); push(last_nsteps_);
        int nz = 0, n64 = 0;
        for (auto v : b.msgs) { if (v) nz++; if (v > 0xFFFFFFFFull) n64++; }
        push((int)b.msgs.size()); push(nz); push(n64);
        push(turn_ > 0 || first_round_ > 0 ? 1 : 0);
        int es = 0;
        for (int j = 0; j < 5; j++) { int v = b.has_echoes ? b.echoes[j] : 0; push(v); es += v; }
        push(es);
        push(ex_ord); push(ex_por); push(ex_rel[0]); push(ex_rel[1]); push(ex_rel[3]);
        push(n_eh); push(n_ah); push(n_ep); push(n_ap); push(n_pearls); push(n_beds);
        int vmax = 0; for (auto const& q : vis_len) vmax = std::max(vmax, q.second);
        push(eh_d1); push(eh_min); push(ah_min); push(pearl_min); push(vmax);
        int const mq = my_queen_, eq = mq >= 0 ? 1 - mq : -1;
        push(id_ == 0 || id_ == 1 ? 1 : 0); push(mq >= 0 && q_vis[mq] ? 1 : 0); qfeat(mq);
        push(eq >= 0 && q_vis[eq] ? 1 : 0); qfeat(eq); push(eq >= 0 ? q_parts[eq] : 0);
        push(has_home_ ? 1 : 0);
        cellf(has_home_, home_x_, home_y_);
        cellf(has_home_, W_ - 1 - home_x_, H_ - 1 - home_y_);
        cellf(has_home_, home_x_, H_ - 1 - home_y_);
        push(has_prev_ ? b.length - prev_len_ : 0); push(has_prev_ ? b.unit_count - prev_units_ : 0);
        push(cd_known);
        if (i != N_X) throw std::logic_error("learn::Encoder layout " + std::to_string(i - 49 * N_CH));
        has_prev_ = true; prev_len_ = b.length; prev_units_ = b.unit_count;
        turn_++;
        return x_;
    }

private:
    int id_; char team_; int W_, H_, limit_;
    std::array<int32_t, N_X> x_{};
    bool started_ = false; int first_round_ = 0, cur_round_ = 0, turn_ = 0;
    bool has_home_ = false; int home_x_ = 0, home_y_ = 0;
    int my_queen_ = -1; bool q_team_known_[2] = {false, false};
    bool q_seen_[2] = {false, false}; int q_r_[2] = {0, 0}, q_x_[2] = {0, 0}, q_y_[2] = {0, 0};
    int last_kind_ = 0, last_first_ = -1, last_nsteps_ = 0;
    bool has_split_ = false; int last_split_round_ = 0;
    bool has_prev_ = false; int prev_len_ = 0, prev_units_ = 0;
};

}  // namespace learn
