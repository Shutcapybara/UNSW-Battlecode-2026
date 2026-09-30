// Verso (X-1) — runtime for the learned tiers: configuration, the feature
// schema, the compiled-tree evaluator (tier 2 heads) and the per-turn dump.
//
// Everything here is inert at the compiled defaults: with no head loaded, no
// dump path and eps = 0 the policy is behaviour-identical to its parent.
//
//   VERSO_PARAMS   "lam_dir=1,beta_q=0.5,eps=0.05,seed=7"   (local games only)
//   VERSO_POLICY   path of a head blob written by tools/verso/export.py
//   VERSO_DUMP     path of the per-turn feature dump (all dragons append)
//   *_A / *_B      the same, for one team only (wins over the plain name)
//   VERSO_SCHEMA   if set, the binary prints the feature schema and exits
//
// The contest sandbox has no environment: a shipped bot plays the compiled
// defaults in Cfg and the heads embedded by verso_heads.hpp (if present).
#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include <fcntl.h>
#include <unistd.h>
#ifndef __wasm__   // the judge's wasm sandbox has no files to map; heads are embedded there
#include <sys/mman.h>
#include <sys/stat.h>
#endif

#if __has_include("verso_heads.hpp") && !defined(VERSO_NO_EMBED)
#include "verso_heads.hpp"
#define VERSO_EMBEDDED 1
#endif

namespace verso {

// Class order of every three-way head (relative to the current facing).
constexpr int NREL = 3;
inline int rel_to_abs(int face, int k) {
    static constexpr int off[NREL] = {0, 1, 3};  // F, R, L
    return (face + off[k]) & 3;
}
inline const char* const RELS[NREL] = {"F", "R", "L"};

// ---------------------------------------------------------------- config
struct Cfg {
    static inline double lam_dir = 1.0;     // weight of log p_dir(first step); verso-01: 1.0, fixed before screening
    static inline double beta_q = 0.0;      // weight of the Q advantage q[d] - max q
    static inline double eps = 0.0;         // exploration probability (data collection only)
    static inline double logp_floor = 1e-4; // p floor inside the log
    static inline double q_clip = 8.0;      // |advantage| clip before beta
    static inline double explore_margin = 1e9;  // explore only moves within this hand-score margin of the choice
    static inline int seed = 0;             // exploration stream
    static inline int view = 0;             // 1: also dump the tier-1 view tensor (<dump>.view)
    static inline std::string policy_path, dump_path;

    static bool set(const std::string& k, double v) {
        struct D { const char* n; double* p; };
        const D ds[] = {{"lam_dir", &lam_dir}, {"beta_q", &beta_q}, {"eps", &eps},
                        {"logp_floor", &logp_floor}, {"q_clip", &q_clip},
                        {"explore_margin", &explore_margin}};
        for (auto const& d : ds) if (k == d.n) { *d.p = v; return true; }
        if (k == "seed") { seed = static_cast<int>(v); return true; }
        if (k == "view") { view = static_cast<int>(v); return true; }
        return false;
    }
    static const char* env(const char* name, char team) {
        std::string t = std::string(name) + "_" + team;
        const char* e = std::getenv(t.c_str());
        return e ? e : std::getenv(name);
    }
    static void load_env(char team) {
        if (const char* e = env("VERSO_POLICY", team)) policy_path = e;
        if (const char* e = env("VERSO_DUMP", team)) dump_path = e;
        const char* e = env("VERSO_PARAMS", team);
        if (!e) return;
        std::string s(e);
        size_t i = 0;
        while (i < s.size()) {
            size_t j = s.find(',', i);
            if (j == std::string::npos) j = s.size();
            std::string kv = s.substr(i, j - i);
            size_t eq = kv.find('=');
            if (eq != std::string::npos && !set(kv.substr(0, eq), std::atof(kv.c_str() + eq + 1)))
                std::fprintf(stderr, "VERSO_PARAMS: unknown %s\n", kv.substr(0, eq).c_str());
            i = j + 1;
        }
    }
};

// ---------------------------------------------------------------- schema
// One flat float vector per turn. Blocks:
//   v5     HB-1's actor-local row (hb1_features.hpp), map-identity columns left out
//   a*_    what Ares's own search computed for each first step (F, R, L) + scalars
//   t*_    tier-4 route features over the dragon's map memory, per first step
//   s_     tier-4 / phase scalars
namespace sch {
inline const char* const A_REL[] = {"status", "score", "progress", "room", "room_pearls", "eaten", "threat",
                                    "blind", "crowd", "visits", "momentum", "escape", "trap", "sprint_best"};
constexpr int NA_REL = sizeof(A_REL) / sizeof(A_REL[0]);
enum { A_STATUS, A_SCORE, A_PROGRESS, A_ROOM, A_ROOM_PEARLS, A_EATEN, A_THREAT, A_BLIND, A_CROWD, A_VISITS,
       A_MOMENTUM, A_ESCAPE, A_TRAP, A_SPRINT_BEST };
inline const char* const A_SCALAR[] = {"a_need", "a_why", "a_target_steps", "a_best_value", "a_escaping",
                                       "a_crown", "a_feeder", "a_age", "a_cap", "a_near_threat", "a_split_ok",
                                       "a_split_score", "a_open_ok", "a_open_score", "a_lv", "a_n_paths"};
constexpr int NA_SCALAR = sizeof(A_SCALAR) / sizeof(A_SCALAR[0]);
enum { AS_NEED, AS_WHY, AS_TARGET_STEPS, AS_BEST_VALUE, AS_ESCAPING, AS_CROWN, AS_FEEDER, AS_AGE, AS_CAP,
       AS_NEAR_THREAT, AS_SPLIT_OK, AS_SPLIT_SCORE, AS_OPEN_OK, AS_OPEN_SCORE, AS_LV, AS_N_PATHS };
inline const char* const T_REL[] = {"reach4", "reach8", "reach16", "pearl_d", "pearl_n8", "pearl_mass", "bed_d",
                                    "bed_n16", "bed_mass", "unseen_d", "unseen_n8", "dive_d", "age8", "ally8",
                                    "enemy8", "food8", "death8", "area3", "branch3", "deg", "maxdeg", "corr_len",
                                    "corr_dead", "food", "ally", "enemy", "threatew", "death", "age", "dens",
                                    "ehd", "ahd"};
constexpr int NT_REL = sizeof(T_REL) / sizeof(T_REL[0]);
enum { T_REACH4, T_REACH8, T_REACH16, T_PEARL_D, T_PEARL_N8, T_PEARL_MASS, T_BED_D, T_BED_N16, T_BED_MASS,
       T_UNSEEN_D, T_UNSEEN_N8, T_DIVE_D, T_AGE8, T_ALLY8, T_ENEMY8, T_FOOD8, T_DEATH8, T_AREA3, T_BRANCH3,
       T_DEG, T_MAXDEG, T_CORR_LEN, T_CORR_DEAD, T_FOOD, T_ALLY, T_ENEMY, T_THREATEW, T_DEATH, T_AGE, T_DENS,
       T_EHD, T_AHD };
inline const char* const S_SCALAR[] = {"s_sparsity", "s_view_units", "s_deaths_seen", "s_seen_frac",
                                       "s_pearls_known", "s_beds_known", "s_beds_ripe", "s_pairs_known",
                                       "s_unpaired_known", "s_dens_reports", "s_local_allies", "s_local_enemies",
                                       "s_crown_known", "s_crown_dist", "s_crown_len", "s_prey_known",
                                       "s_prey_dist", "s_since_enemy", "s_enemy_ids", "s_since_portal", "s_born",
                                       "s_clock", "s_eh_len_diff"};
constexpr int NS_SCALAR = sizeof(S_SCALAR) / sizeof(S_SCALAR[0]);
enum { S_SPARSITY, S_VIEW_UNITS, S_DEATHS_SEEN, S_SEEN_FRAC, S_PEARLS_KNOWN, S_BEDS_KNOWN, S_BEDS_RIPE,
       S_PAIRS_KNOWN, S_UNPAIRED_KNOWN, S_DENS_REPORTS, S_LOCAL_ALLIES, S_LOCAL_ENEMIES, S_CROWN_KNOWN,
       S_CROWN_DIST, S_CROWN_LEN, S_PREY_KNOWN, S_PREY_DIST, S_SINCE_ENEMY, S_ENEMY_IDS, S_SINCE_PORTAL, S_BORN,
       S_CLOCK, S_EH_LEN_DIFF };

inline std::vector<std::string> v5_names() {
    std::vector<std::string> n = {"round", "length", "units", "unit_limit", "units_frac", "n_msgs",
                                  "echo_kelp", "echo_ally", "echo_allyHead", "echo_enemy", "echo_enemyHead"};
    for (int rr = -3; rr <= 3; rr++)
        for (int f = -3; f <= 3; f++)
            for (const char* k : {"occ", "pearl", "cd"})
                n.push_back("g_" + std::to_string(f) + "_" + std::to_string(rr) + "_" + k);
    for (const char* k : {"vis_pearls", "vis_beds", "vis_min_cd", "vis_enemy_seg", "vis_enemy_heads",
                          "vis_ally_seg", "vis_ally_heads", "vis_own_seg", "vis_kelp", "vis_portal",
                          "pearl_front", "pearl_back", "pearl_left", "pearl_right", "enemy_front", "enemy_back",
                          "ally_front", "ally_back", "near_pearl", "near_enemy_head", "near_ally_head",
                          "near_enemy_body", "near_bed_ready"})
        n.push_back(k);
    for (const char* rel : {"F", "R", "L", "B"})
        for (const char* k : {"block", "portal", "pearl", "cd", "eh_adj", "area", "pdist", "pmass", "pc3",
                              "bedsoon", "unvisited", "allyh2", "eseg2", "run", "mem_bed", "mem_bed_n",
                              "mem_pearl"})
            n.push_back(std::string("c") + rel + "_" + k);
    for (const char* k : {"free_dirs", "mem_age", "mem_len_delta", "mem_since_split", "mem_n_splits",
                          "mem_since_eat", "mem_visited", "mem_revisit", "mem_msgs_total", "mem_portals_seen",
                          "mem_enemy_heads_prev", "mem_pearls_prev", "mem_disp", "mem_max_len", "mem_beds_known",
                          "mem_last_family", "mem_last_rel", "split_elig", "n_exit_ord", "n_exit_portal",
                          "n_exit_any"})
        n.push_back(k);
    return n;
}
}  // namespace sch

struct Schema {
    std::vector<std::string> names;
    int n_v5 = 0, a_rel = 0, a_scalar = 0, t_rel = 0, s_scalar = 0, n = 0;
    uint32_t hash = 0;

    Schema() {
        names = sch::v5_names();
        n_v5 = static_cast<int>(names.size());
        a_rel = static_cast<int>(names.size());
        for (int k = 0; k < NREL; k++)
            for (int i = 0; i < sch::NA_REL; i++) names.push_back(std::string("a") + RELS[k] + "_" + sch::A_REL[i]);
        a_scalar = static_cast<int>(names.size());
        for (int i = 0; i < sch::NA_SCALAR; i++) names.push_back(sch::A_SCALAR[i]);
        t_rel = static_cast<int>(names.size());
        for (int k = 0; k < NREL; k++)
            for (int i = 0; i < sch::NT_REL; i++) names.push_back(std::string("t") + RELS[k] + "_" + sch::T_REL[i]);
        s_scalar = static_cast<int>(names.size());
        for (int i = 0; i < sch::NS_SCALAR; i++) names.push_back(sch::S_SCALAR[i]);
        n = static_cast<int>(names.size());
        uint32_t h = 2166136261u;  // FNV-1a over the names, newline separated
        for (auto const& s : names) {
            for (char c : s) { h ^= static_cast<uint8_t>(c); h *= 16777619u; }
            h ^= '\n'; h *= 16777619u;
        }
        hash = h;
    }
    int a(int rel, int i) const { return a_rel + rel * sch::NA_REL + i; }
    int t(int rel, int i) const { return t_rel + rel * sch::NT_REL + i; }
    static const Schema& get() { static const Schema s; return s; }
};

// ---------------------------------------------------------------- heads
// Blob (little-endian, 8-byte aligned), written by tools/verso/export.py:
//   u32 magic 'VRSM', u32 version 1, u32 n_heads, u32 schema hash
//   per head: char name[16]; u32 kind, K, n_trees, n_nodes; f32 base[K] (pad to 8);
//             u32 tree_start[n_trees] (pad to 8); u64 nodes[n_nodes]
// Node word: bits 0-31 float32 threshold or leaf value; bits 32-46 feature index
// (0x7FFF = leaf); bit 47 missing-goes-left; bits 48-63 right-child offset.
// Preorder, so the left child is the next node (hb1-04's encoding). Trees are
// interleaved by output: tree t adds to output t % K.
//   kind 0: softmax over F/R/L;  kind 1: three regressors (Q of F/R/L);  kind 2: binary logit (K = 1)
struct Head {
    char name[17] = {0};
    int kind = 0, K = 0, n_trees = 0;
    const float* base = nullptr;
    const uint32_t* tree_start = nullptr;
    const uint64_t* nodes = nullptr;

    void margins(const float* x, double* out) const {
        for (int k = 0; k < K; k++) out[k] = base[k];
        for (int t = 0; t < n_trees; t++) {
            const uint64_t* nd = nodes + tree_start[t];
            int j = 0;
            for (;;) {
                uint64_t w = nd[j];
                unsigned f = static_cast<unsigned>(w >> 32) & 0x7FFFu;
                uint32_t u = static_cast<uint32_t>(w);
                float v;
                std::memcpy(&v, &u, 4);
                if (f == 0x7FFFu) { out[t % K] += v; break; }
                float xv = x[f];
                bool left = std::isnan(xv) ? ((w >> 47) & 1u) : (xv < v);
                j += left ? 1 : static_cast<int>(w >> 48);
            }
        }
    }
};

struct Model {
    std::vector<Head> heads;
    bool tried = false;

    bool parse(const unsigned char* b, size_t size) {
        if (size < 16 || std::memcmp(b, "VRSM", 4) != 0) return false;
        auto u32 = [&](size_t off) { uint32_t v; std::memcpy(&v, b + off, 4); return v; };
        if (u32(4) != 1) return false;
        uint32_t n_heads = u32(8);
        if (u32(12) != Schema::get().hash) {
            std::fprintf(stderr, "verso: head blob was exported for another feature schema; heads off\n");
            return false;
        }
        size_t off = 16;
        auto pad8 = [&]() { off = (off + 7) & ~static_cast<size_t>(7); };
        for (uint32_t h = 0; h < n_heads; h++) {
            if (off + 32 > size) return false;
            Head hd;
            std::memcpy(hd.name, b + off, 16); off += 16;
            hd.kind = static_cast<int>(u32(off)); hd.K = static_cast<int>(u32(off + 4));
            hd.n_trees = static_cast<int>(u32(off + 8));
            uint32_t n_nodes = u32(off + 12); off += 16;
            hd.base = reinterpret_cast<const float*>(b + off); off += 4 * static_cast<size_t>(hd.K); pad8();
            hd.tree_start = reinterpret_cast<const uint32_t*>(b + off); off += 4 * static_cast<size_t>(hd.n_trees); pad8();
            hd.nodes = reinterpret_cast<const uint64_t*>(b + off); off += 8 * static_cast<size_t>(n_nodes);
            if (off > size || hd.K < 1 || hd.K > 8) return false;
            heads.push_back(hd);
        }
        return true;
    }
    // Once per process: the file named by VERSO_POLICY (mapped read-only, shared
    // through the page cache by every dragon), else the embedded blob.
    void load() {
        if (tried) return;
        tried = true;
#ifndef __wasm__
        if (!Cfg::policy_path.empty()) {
            int fd = ::open(Cfg::policy_path.c_str(), O_RDONLY);
            if (fd >= 0) {
                struct stat sb {};
                ::fstat(fd, &sb);
                void* p = ::mmap(nullptr, static_cast<size_t>(sb.st_size), PROT_READ, MAP_SHARED, fd, 0);
                ::close(fd);
                if (p != MAP_FAILED && parse(static_cast<const unsigned char*>(p), static_cast<size_t>(sb.st_size)))
                    return;
            }
            std::fprintf(stderr, "verso: cannot load %s\n", Cfg::policy_path.c_str());
            heads.clear();
            return;
        }
#endif
#ifdef VERSO_EMBEDDED
        if (!parse(reinterpret_cast<const unsigned char*>(verso_blob), sizeof(verso_blob))) heads.clear();
#endif
    }
    const Head* find(const char* name) const {
        for (auto const& h : heads) if (std::strcmp(h.name, name) == 0) return &h;
        return nullptr;
    }
};

// ---------------------------------------------------------------- dump
// One write() per turn with O_APPEND, so all dragons of a game share a file.
// Record: int32 header[16] = {magic 'VRD1', n floats, rnd, me, team, len,
// units, face, head cell, W, H, act (0 move, 1 split), first step (abs dir, -1
// for a split), steps (or split size), flags, greedy first step}, then the
// feature vector (float32). flags: bit 0 = exploratory step, bit 1 = the
// learned terms changed the hand choice.
struct Dump {
    static constexpr int32_t MAGIC = 0x31445256;
    int fd = -2;
    bool on() {
        if (fd == -2) fd = Cfg::dump_path.empty() ? -1 : ::open(Cfg::dump_path.c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644);
        return fd >= 0;
    }
    void write(const int32_t* header16, const std::vector<float>& x) {
        if (fd < 0) return;
        std::vector<char> buf(16 * 4 + x.size() * 4);
        std::memcpy(buf.data(), header16, 64);
        std::memcpy(buf.data() + 64, x.data(), x.size() * 4);
        ssize_t r = ::write(fd, buf.data(), buf.size());
        (void)r;
    }
};

// Tier-1 input: the dragon's map memory in an egocentric (facing = up) window
// of radius VIEW_R, one byte per cell and channel. Written to <dump>.view as
// int32 {magic 'VRV1', rnd, me, team} + VIEW_C * VIEW_N * VIEW_N bytes
// (channel-major, rows from farthest ahead to behind, columns left to right).
constexpr int VIEW_R = 5, VIEW_N = 2 * VIEW_R + 1, VIEW_C = 18;
enum { VC_SEEN, VC_AGE, VC_PEARL, VC_BED, VC_BED_WAIT, VC_OCC, VC_VAC, VC_EDGE_F, VC_EDGE_R, VC_EDGE_B, VC_EDGE_L,
       VC_FOOD, VC_ALLY, VC_ENEMY, VC_THREAT, VC_DEATH, VC_VISITS, VC_BODY_SEEN };
struct ViewDump {
    static constexpr int32_t MAGIC = 0x31565256;
    int fd = -2;
    bool on() {
        if (fd == -2)
            fd = (Cfg::view && !Cfg::dump_path.empty())
                ? ::open((Cfg::dump_path + ".view").c_str(), O_WRONLY | O_CREAT | O_APPEND, 0644) : -1;
        return fd >= 0;
    }
    void write(int rnd, int me, int team, const std::vector<uint8_t>& v) {
        if (fd < 0) return;
        std::vector<char> buf(16 + v.size());
        int32_t h[4] = {MAGIC, rnd, me, team};
        std::memcpy(buf.data(), h, 16);
        std::memcpy(buf.data() + 16, v.data(), v.size());
        ssize_t r = ::write(fd, buf.data(), buf.size());
        (void)r;
    }
};

// Deterministic exploration stream: one uniform in [0, 1) per (seed, dragon, round, salt).
inline double uniform(int seed, int me, int rnd, int salt) {
    uint64_t z = (static_cast<uint64_t>(static_cast<uint32_t>(seed)) << 40) ^ (static_cast<uint64_t>(me) << 20) ^
                 static_cast<uint64_t>(rnd) ^ (static_cast<uint64_t>(salt) << 56);
    z += 0x9E3779B97F4A7C15ull;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    z ^= z >> 31;
    return static_cast<double>(z >> 11) / 9007199254740992.0;
}

}  // namespace verso
