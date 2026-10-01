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

#include "params.hpp"
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
    static inline double lam_dir = 1.0;     // weight of log p_dir(first step); verso-03/04: 1.0
    static inline double lam_dir2 = 0.0;    // weight of a second direction head ("dir2"), e.g. an opening donor
    static inline double beta_q = 0.0;      // weight of the Q advantage q[d] - max q
    static inline double beta_s = 0.0;      // weight of the split advantage q[S] - max q[move] (4-output q head)
    static inline double eps = 0.0;         // exploration probability (data collection only)
    static inline double eps_split = 0.0;   // probability of flipping the split / no-split choice (data collection)
    static inline double logp_floor = 1e-4; // p floor inside the log
    static inline double q_clip = 8.0;      // |advantage| clip before beta
    static inline double explore_margin = 1e9;  // explore only moves within this hand-score margin of the choice
    static inline int seed = 0;             // exploration stream
    static inline int view = 0;             // 1: also dump the tier-1 view tensor (<dump>.view)
    static inline std::string policy_path, dump_path;
    static inline std::vector<std::string> unknown;

    static bool set(const std::string& k, double v) {
        struct D { const char* n; double* p; };
        const D ds[] = {{"lam_dir", &lam_dir}, {"lam_dir2", &lam_dir2}, {"beta_q", &beta_q}, {"beta_s", &beta_s}, {"eps", &eps},
                        {"eps_split", &eps_split},
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
                unknown.push_back(kv);   // phase knobs ("o.x", "p.x", "ph_*") are read by Phase after this
            i = j + 1;
        }
    }
};

// ---------------------------------------------------------------- phases
// Two parameter sets over the knobs below — the compiled (base) values and an
// opening set — blended every turn by the opening belief b in [0, 1]:
//   value = base + b * (opening - base)
//   b = sigmoid(ph_k * (ph_0 - ph_units * units / limit - ph_clock * round / 500 - ph_contact * contact))
// with contact = 1 once an enemy part has been seen. The belief is measured
// state with the clock as a soft prior; it is 0 everywhere (base behaviour)
// unless VERSO_PARAMS sets an opening value ("o.<knob>=v") — then the knob
// moves only while the belief is high. "p.<knob>=v" sets the base value.
struct Phase {
    struct KD { const char* n; double* p; double base, open; bool set; double late = 0; bool lset = false; };
    struct KI { const char* n; int* p; double base, open; bool set; double late = 0; bool lset = false; };
    static inline std::vector<KD> kd;
    static inline std::vector<KI> ki;
    static inline double lam_open = 0.0; static inline bool lam_set = false;   // opening value of Cfg::lam_dir
    static inline double beta_open = 0.0; static inline bool beta_set = false; // opening value of Cfg::beta_q
    static inline double lam2_open = 0.0; static inline bool lam2_set = false; // opening value of Cfg::lam_dir2
    static inline double lam_base = 0.0, beta_base = 0.0, lam2_base = 0.0;
    static inline double ph_k = 8.0, ph_0 = 0.6, ph_units = 1.0, ph_clock = 1.5, ph_contact = 0.0;
    static inline bool any = false;
    static inline double belief = 0.0;
    // Late phase (the conversion / crown race): a ramp on the clock, 0 before l_from, 1 after l_to.
    // value = base + b_open (opening - base) + b_late (late - base); "l.<knob>=v" sets the late value.
    static inline double l_from = 300.0, l_to = 400.0, belief_late = 0.0;
    static inline double lam_late = 0.0; static inline bool lam_lset = false;

    static void init() {
        if (!kd.empty()) return;
        kd = {{"pearl_value", &ares::Params::pearl_value, 0, 0, false}, {"memory_value", &ares::Params::memory_value, 0, 0, false}, {"bed_value", &ares::Params::bed_value, 0, 0, false}, {"unseen_value", &ares::Params::unseen_value, 0, 0, false}, {"dive_value", &ares::Params::dive_value, 0, 0, false}, {"target_gamma", &ares::Params::target_gamma, 0, 0, false}, {"own_target_discount", &ares::Params::own_target_discount, 0, 0, false}, {"enemy_target_discount", &ares::Params::enemy_target_discount, 0, 0, false}, {"target_hysteresis", &ares::Params::target_hysteresis, 0, 0, false}, {"goal_weight", &ares::Params::goal_weight, 0, 0, false}, {"crowd_weight", &ares::Params::crowd_weight, 0, 0, false}, {"visit_weight", &ares::Params::visit_weight, 0, 0, false}, {"momentum_weight", &ares::Params::momentum_weight, 0, 0, false}, {"trap_weight", &ares::Params::trap_weight, 0, 0, false}, {"trap_farm_factor", &ares::Params::trap_farm_factor, 0, 0, false}, {"split_value", &ares::Params::split_value, 0, 0, false}, {"opening_production_value", &ares::Params::opening_production_value, 0, 0, false}, {"sprint_cost", &ares::Params::sprint_cost, 0, 0, false}, {"threat_weight", &ares::Params::threat_weight, 0, 0, false}, {"density_ally_weight", &ares::Params::density_ally_weight, 0, 0, false}, {"blind_unseen", &ares::Params::blind_unseen, 0, 0, false}, {"bed_wait", &ares::Params::bed_wait, 0, 0, false}, {"feed_k", &ares::Params::feed_k, 0, 0, false}, {"lv_end", &ares::Params::lv_end, 0, 0, false}};
        ki = {{"opening_production_until", &ares::Params::opening_production_until, 0, 0, false}, {"opening_production_unit_cap", &ares::Params::opening_production_unit_cap, 0, 0, false}, {"search_cap", &ares::Params::search_cap, 0, 0, false}, {"search_cap_late", &ares::Params::search_cap_late, 0, 0, false}, {"search_cap_born", &ares::Params::search_cap_born, 0, 0, false}, {"feed_base", &ares::Params::feed_base, 0, 0, false}, {"feed_range", &ares::Params::feed_range, 0, 0, false}, {"feed_min_crown", &ares::Params::feed_min_crown, 0, 0, false}, {"crown_margin", &ares::Params::crown_margin, 0, 0, false}, {"grow_from", &ares::Params::grow_from, 0, 0, false}, {"split_until_round", &ares::Params::split_until_round, 0, 0, false}, {"crown_claim_len", &ares::Params::crown_claim_len, 0, 0, false}};
        for (auto& k : kd) k.base = k.open = *k.p;
        for (auto& k : ki) k.base = k.open = *k.p;
    }
    // "o.name" / "p.name"; returns false if the name is not a phase knob
    static bool set(const std::string& key, double v) {
        init();
        if (key.size() >= 3 && key[0] == 'l' && key[1] == '.') {
            const std::string n = key.substr(2);
            any = true;
            if (n == "lam_dir") { lam_late = v; lam_lset = true; return true; }
            for (auto& k : kd) if (n == k.n) { k.late = v; k.lset = true; return true; }
            for (auto& k : ki) if (n == k.n) { k.late = v; k.lset = true; return true; }
            return false;
        }
        if (key.size() < 3 || key[1] != '.' || (key[0] != 'o' && key[0] != 'p')) {
            struct P { const char* n; double* p; };
            const P ps[] = {{"ph_k", &ph_k}, {"ph_0", &ph_0}, {"ph_units", &ph_units}, {"ph_clock", &ph_clock},
                            {"ph_contact", &ph_contact}, {"l_from", &l_from}, {"l_to", &l_to}};
            for (auto const& q : ps) if (key == q.n) { *q.p = v; return true; }
            return false;
        }
        const bool open = key[0] == 'o';
        const std::string n = key.substr(2);
        if (n == "lam_dir") { if (open) { lam_open = v; lam_set = true; any = true; } else Cfg::lam_dir = v; return true; }
        if (n == "lam_dir2") { if (open) { lam2_open = v; lam2_set = true; any = true; } else Cfg::lam_dir2 = v; return true; }
        if (n == "beta_q") { if (open) { beta_open = v; beta_set = true; any = true; } else Cfg::beta_q = v; return true; }
        for (auto& k : kd) if (n == k.n) { if (open) { k.open = v; k.set = true; any = true; } else { k.base = v; *k.p = v; if (!k.set) k.open = v; } return true; }
        for (auto& k : ki) if (n == k.n) { if (open) { k.open = v; k.set = true; any = true; } else { k.base = v; *k.p = static_cast<int>(v); if (!k.set) k.open = v; } return true; }
        return false;
    }
    static void freeze() { lam_base = Cfg::lam_dir; beta_base = Cfg::beta_q; lam2_base = Cfg::lam_dir2; }
    // once per turn, before the policy reads any knob
    static void apply(int units, int limit, int rnd, bool contact) {
        if (!any) return;
        const double z = ph_k * (ph_0 - ph_units * units / std::max(1, limit) - ph_clock * rnd / 500.0 -
                                 ph_contact * (contact ? 1.0 : 0.0));
        belief = 1.0 / (1.0 + std::exp(-z));
        belief_late = rnd <= l_from ? 0.0 : rnd >= l_to ? 1.0 : (rnd - l_from) / std::max(1.0, l_to - l_from);
        for (auto& k : kd)
            if (k.set || k.lset)
                *k.p = k.base + (k.set ? belief * (k.open - k.base) : 0.0) + (k.lset ? belief_late * (k.late - k.base) : 0.0);
        for (auto& k : ki)
            if (k.set || k.lset)
                *k.p = static_cast<int>(std::lround(k.base + (k.set ? belief * (k.open - k.base) : 0.0) +
                                                    (k.lset ? belief_late * (k.late - k.base) : 0.0)));
        if (lam_set || lam_lset)
            Cfg::lam_dir = lam_base + (lam_set ? belief * (lam_open - lam_base) : 0.0) +
                           (lam_lset ? belief_late * (lam_late - lam_base) : 0.0);
        if (lam2_set) Cfg::lam_dir2 = lam2_base + belief * (lam2_open - lam2_base);
        if (beta_set) Cfg::beta_q = beta_base + belief * (beta_open - beta_base);
    }
};

// ---------------------------------------------------------------- schema
// One flat float vector per turn. Blocks:
//   v5     HB-1's actor-local row (hb1_features.hpp), map-identity columns left out
//   a*_    what Ares's own search computed for each first step (F, R, L) + scalars
//   t*_    tier-4 route features over the dragon's map memory, per first step
//   s_     tier-4 / phase scalars
//   h_     outputs of the heads evaluated before the others (the dir head's log p per first step)
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
inline const char* const H_OUT[] = {"h_dir_F", "h_dir_R", "h_dir_L"};
constexpr int NH_OUT = sizeof(H_OUT) / sizeof(H_OUT[0]);
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
    int n_v5 = 0, a_rel = 0, a_scalar = 0, t_rel = 0, s_scalar = 0, h_out = 0, n = 0;
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
        h_out = static_cast<int>(names.size());
        for (int i = 0; i < sch::NH_OUT; i++) names.push_back(sch::H_OUT[i]);
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
//   kind 0: softmax over F/R/L;  kind 1: regressors, Q of F/R/L and optionally of the production split (K = 3
//   or 4);  kind 2: binary logit (K = 1)
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

// Compact embedded heads (tools/verso/export.py compact): preorder streams decoded once into 8-byte nodes.
inline float half_to_float(uint16_t h) {
    const uint32_t s = (h & 0x8000u) << 16, e = (h >> 10) & 0x1Fu, m = h & 0x3FFu;
    uint32_t u;
    if (e == 0) {
        if (m == 0) u = s;
        else {   // subnormal
            int ex = -1; uint32_t mm = m;
            do { ex++; mm <<= 1; } while (!(mm & 0x400u));
            u = s | static_cast<uint32_t>(127 - 15 - ex) << 23 | (mm & 0x3FFu) << 13;
        }
    } else if (e == 31) u = s | 0x7F800000u | m << 13;
    else u = s | (e + 112) << 23 | m << 13;
    float f;
    std::memcpy(&f, &u, 4);
    return f;
}

struct Model {
    std::vector<Head> heads;
    bool tried = false;
    std::vector<std::vector<uint64_t>> own_nodes;   // decoded compact heads
    std::vector<std::vector<uint32_t>> own_starts;

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
#if defined(VERSO_EMBEDDED) && defined(VERSO_COMPACT_HEADS)
        if (verso_c::schema_hash != Schema::get().hash) {
            std::fprintf(stderr, "verso: embedded heads were exported for another feature schema; heads off\n");
            return;
        }
        own_nodes.resize(verso_c::n_heads); own_starts.resize(verso_c::n_heads);
        // One forward pass per head, no recursion: the output is in preorder, the same order as the streams, so a
        // node's position is its index; a split's right-child offset is fixed when its left subtree closes (a
        // stack of open splits). Cheap enough for the judge's first-turn budget (the boot runs inside turn 0).
        for (int hi = 0; hi < verso_c::n_heads; hi++) {
            const auto& d = verso_c::heads[hi];
            size_t n = 0;   // nodes = number of shape bits = 2 * leaves - 1 per tree
            {
                size_t leaves = 0, splits = 0, sb = 0;
                for (int t = 0; t < d.n_trees; t++) {
                    long open = 1;
                    while (open) {
                        const bool sp = (d.shape[sb >> 3] >> (sb & 7)) & 1u;
                        sb++;
                        if (sp) { splits++; open++; } else { leaves++; open--; }
                    }
                }
                n = leaves + splits;
            }
            std::vector<uint64_t>& out = own_nodes[hi];
            out.resize(n);
            own_starts[hi].resize(static_cast<size_t>(d.n_trees));
            uint64_t* o = out.data();
            std::vector<uint32_t> stack(64);
            size_t sb = 0, fi = 0, li = 0, db = 0, i = 0;
            for (int t = 0; t < d.n_trees; t++) {
                own_starts[hi][t] = static_cast<uint32_t>(i);
                size_t top = 0;   // open splits whose left subtree is being written (bit 31: in right subtree)
                for (;;) {
                    const bool sp = (d.shape[sb >> 3] >> (sb & 7)) & 1u;
                    sb++;
                    if (sp) {
                        const unsigned f = d.feat[fi], tx = d.tix[fi];
                        fi++;
                        const uint64_t dl = (d.dflt[db >> 3] >> (db & 7)) & 1u;
                        db++;
                        uint32_t u;
                        std::memcpy(&u, &d.thr[d.thr_off[f] + tx], 4);
                        o[i] = (dl << 47) | (static_cast<uint64_t>(f) << 32) | u;
                        if (top == stack.size()) stack.resize(stack.size() * 2);
                        stack[top++] = static_cast<uint32_t>(i);
                        i++;
                    } else {
                        uint32_t u;
                        const float v = half_to_float(d.leaf[li++]);
                        std::memcpy(&u, &v, 4);
                        o[i] = (static_cast<uint64_t>(0x7FFF) << 32) | u;
                        i++;
                        while (top && (stack[top - 1] & 0x80000000u)) top--;   // right subtrees now complete
                        if (!top) break;                                         // the tree is complete
                        const uint32_t p = stack[top - 1];
                        o[p] |= static_cast<uint64_t>(i - p) << 48;              // the right child starts here
                        stack[top - 1] = p | 0x80000000u;
                    }
                }
            }
            Head hd;
            std::strncpy(hd.name, d.name, 16);
            hd.kind = d.kind; hd.K = d.K; hd.n_trees = d.n_trees; hd.base = d.base;
            heads.push_back(hd);
        }
        for (int hi = 0; hi < verso_c::n_heads; hi++) {   // pointers only after every vector has its final address
            heads[hi].tree_start = own_starts[hi].data();
            heads[hi].nodes = own_nodes[hi].data();
        }
#elif defined(VERSO_EMBEDDED)
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
// learned terms changed the hand choice, bit 2 = exploratory split flip,
// bit 3 = the greedy action was a split.
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
