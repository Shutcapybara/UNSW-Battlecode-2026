// Small deterministic multiclass histogram GBT for the H-Q8 feature ablation.
// This is an experiment trainer, not the deployed HB1 compact evaluator.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

namespace {
constexpr int K = 3;
constexpr int MAX_BINS = 32;
constexpr int MAX_DEPTH = 3;
constexpr int NODES_PER_TREE = (1 << (MAX_DEPTH + 1)) - 1;
constexpr double LEARNING_RATE = 0.08;
constexpr double L2 = 3.0;
constexpr double MIN_GAIN = 1.0;
constexpr size_t MIN_LEAF_ROWS = 64;

struct Node {
    uint16_t feature = 0;
    uint8_t flags = 0; // bit 0: split, bit 1: missing values go left
    uint8_t reserved = 0;
    float threshold = 0;
    float value[K] = {0, 0, 0};
};
static_assert(sizeof(Node) == 20, "Node layout is part of the size-matched experiment");

template <class T>
std::vector<T> read_values(const std::string& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("Cannot open " + path);
    auto end = input.tellg();
    if (end < 0 || size_t(end) % sizeof(T)) throw std::runtime_error("Bad binary size: " + path);
    std::vector<T> values(size_t(end) / sizeof(T));
    input.seekg(0);
    input.read(reinterpret_cast<char*>(values.data()), end);
    if (!input) throw std::runtime_error("Short binary read: " + path);
    return values;
}

template <class T>
void write_values(const std::string& path, const std::vector<T>& values) {
    std::ofstream output(path, std::ios::binary);
    if (!output) throw std::runtime_error("Cannot write " + path);
    output.write(reinterpret_cast<const char*>(values.data()), values.size() * sizeof(T));
    if (!output) throw std::runtime_error("Short binary write: " + path);
}

std::vector<std::vector<float>> make_cuts(const std::vector<float>& x, size_t rows,
                                          size_t columns, size_t features) {
    std::vector<std::vector<float>> cuts(features);
    for (size_t f = 0; f < features; ++f) {
        std::vector<float> values;
        values.reserve(rows);
        for (size_t r = 0; r < rows; ++r) {
            float value = x[r * columns + f];
            if (std::isfinite(value)) values.push_back(value);
        }
        if (values.size() < 2) continue;
        std::sort(values.begin(), values.end());
        auto& thresholds = cuts[f];
        for (int q = 1; q < MAX_BINS; ++q) {
            size_t index = (values.size() * size_t(q)) / MAX_BINS;
            if (index >= values.size()) index = values.size() - 1;
            float cut = values[index];
            if (thresholds.empty() || cut > thresholds.back()) thresholds.push_back(cut);
        }
        // A threshold at the maximum creates an empty upper branch.
        while (!thresholds.empty() && thresholds.back() >= values.back()) thresholds.pop_back();
    }
    return cuts;
}

std::vector<uint8_t> make_bins(const std::vector<float>& x, size_t rows,
                               size_t columns, size_t features,
                               const std::vector<std::vector<float>>& cuts) {
    std::vector<uint8_t> bins(features * rows);
#ifdef _OPENMP
#pragma omp parallel for schedule(static) if(features >= 64)
#endif
    for (long long ff = 0; ff < static_cast<long long>(features); ++ff) {
        size_t f = size_t(ff);
            const auto& thresholds = cuts[f];
            uint8_t* out = bins.data() + f * rows;
            for (size_t r = 0; r < rows; ++r) {
            float value = x[r * columns + f];
            out[r] = std::isfinite(value)
                ? uint8_t(1 + std::lower_bound(thresholds.begin(), thresholds.end(), value) - thresholds.begin())
                : uint8_t(0);
        }
    }
    return bins;
}

struct Candidate {
    bool valid = false;
    uint16_t feature = 0;
    uint8_t cut_bin = 0;
    bool missing_left = false;
    float threshold = 0;
    double gain = -std::numeric_limits<double>::infinity();
};

double score(const std::array<double, K>& g, const std::array<double, K>& h) {
    double result = 0;
    for (int k = 0; k < K; ++k) result += g[k] * g[k] / (h[k] + L2);
    return result;
}

class Trainer {
public:
    Trainer(const std::vector<float>& train, size_t n, size_t columns, size_t f,
            const std::vector<uint8_t>& labels, const std::vector<float>& weights,
            int rounds, std::vector<float>& holdout, size_t nhold)
        : x_(train), n_(n), columns_(columns), f_(f), labels_(labels), weights_(weights),
          rounds_(rounds), holdout_(holdout), nhold_(nhold),
          cuts_(make_cuts(train, n, columns, f)), bins_(make_bins(train, n, columns, f, cuts_)),
          nodes_(size_t(rounds) * NODES_PER_TREE) {
        if (labels_.size() != n_ || weights_.size() != n_ || train.size() != n_ * columns_ ||
            holdout_.size() != nhold_ * columns_ || f_ > columns_ || f_ > 65535 || rounds_ < 1)
            throw std::runtime_error("Input matrix/label/weight dimensions mismatch");
        base_.fill(0);
        std::array<double, K> class_weight{};
        double total = 0;
        for (size_t i = 0; i < n_; ++i) {
            if (labels_[i] >= K || !std::isfinite(weights_[i]) || weights_[i] <= 0)
                throw std::runtime_error("Invalid label or sample weight");
            class_weight[labels_[i]] += weights_[i];
            total += weights_[i];
        }
        for (int k = 0; k < K; ++k) {
            if (class_weight[k] <= 0) throw std::runtime_error("Training data lacks a class");
            base_[k] = float(std::log(class_weight[k] / total));
        }
        margins_.resize(n_ * K);
        for (size_t i = 0; i < n_; ++i)
            for (int k = 0; k < K; ++k) margins_[i * K + k] = base_[k];
        grad_.resize(n_ * K);
        hess_.resize(n_ * K);
        split_uses_.assign(f_, 0);
        all_rows_.resize(n_);
        std::iota(all_rows_.begin(), all_rows_.end(), size_t(0));
    }

    void fit() {
        const auto began = std::chrono::steady_clock::now();
        for (int round = 0; round < rounds_; ++round) {
            calculate_derivatives();
            Node* tree = nodes_.data() + size_t(round) * NODES_PER_TREE;
            std::fill(tree, tree + NODES_PER_TREE, Node{});
            build_node(tree, 0, all_rows_, 0);
            apply_train_tree(tree);
            if ((round + 1) % 20 == 0 || round + 1 == rounds_)
                std::cerr << "trained round " << round + 1 << "/" << rounds_ << "\n";
        }
        const auto ended = std::chrono::steady_clock::now();
        seconds_ = std::chrono::duration<double>(ended - began).count();
    }

    void write_outputs(const std::string& prefix) {
        std::vector<float> base(base_.begin(), base_.end());
        write_values(prefix + ".base.f32", base);
        write_values(prefix + ".nodes.bin", nodes_);
        auto train_probs = predict(x_, n_);
        write_values(prefix + ".train-prob.f64", train_probs);
        auto probs = predict(holdout_, nhold_);
        write_values(prefix + ".holdout-prob.f64", probs);
        std::ostringstream json;
        json << std::setprecision(10)
             << "{\n  \"rows_train\": " << n_ << ",\n  \"rows_holdout\": " << nhold_
             << ",\n  \"features\": " << f_ << ",\n  \"rounds\": " << rounds_
             << ",\n  \"max_depth\": " << MAX_DEPTH << ",\n  \"max_bins\": " << MAX_BINS
             << ",\n  \"learning_rate\": " << LEARNING_RATE << ",\n  \"l2\": " << L2
             << ",\n  \"min_gain\": " << MIN_GAIN << ",\n  \"min_leaf_rows\": " << MIN_LEAF_ROWS
             << ",\n  \"size_bytes\": " << nodes_.size() * sizeof(Node) + base.size() * sizeof(float)
             << ",\n  \"training_seconds\": " << seconds_ << ",\n  \"split_uses_by_feature\": {";
        bool first = true;
        for (size_t f = 0; f < f_; ++f) if (split_uses_[f]) {
            if (!first) json << ",";
            first = false;
            json << "\n    \"" << f << "\": " << split_uses_[f];
        }
        if (!first) json << "\n  ";
        json << "}\n}\n";
        std::ofstream report(prefix + ".trainer.json");
        report << json.str();
        if (!report) throw std::runtime_error("Cannot write trainer report");
    }

private:
    const std::vector<float>& x_;
    size_t n_, columns_, f_;
    const std::vector<uint8_t>& labels_;
    const std::vector<float>& weights_;
    int rounds_;
    std::vector<float>& holdout_;
    size_t nhold_;
    std::vector<std::vector<float>> cuts_;
    std::vector<uint8_t> bins_;
    std::vector<Node> nodes_;
    std::array<float, K> base_{};
    std::vector<double> margins_, grad_, hess_;
    std::vector<size_t> split_uses_, all_rows_;
    double seconds_ = 0;

    void calculate_derivatives() {
        for (size_t i = 0; i < n_; ++i) {
            double maximum = std::max({margins_[i * K], margins_[i * K + 1], margins_[i * K + 2]});
            double expv[K], total = 0;
            for (int k = 0; k < K; ++k) { expv[k] = std::exp(margins_[i * K + k] - maximum); total += expv[k]; }
            for (int k = 0; k < K; ++k) {
                double p = expv[k] / total;
                grad_[i * K + k] = weights_[i] * ((labels_[i] == k ? 1.0 : 0.0) - p);
                hess_[i * K + k] = weights_[i] * p * (1 - p);
            }
        }
    }

    Candidate best_split(const std::vector<size_t>& rows) const {
        Candidate best;
        if (rows.size() < 2 * MIN_LEAF_ROWS) return best;
        std::array<double, K> parent_g{}, parent_h{};
        for (size_t row : rows) for (int k = 0; k < K; ++k) {
            parent_g[k] += grad_[row * K + k];
            parent_h[k] += hess_[row * K + k];
        }
        const double parent_score = score(parent_g, parent_h);
        std::vector<Candidate> per_feature(f_);
#ifdef _OPENMP
#pragma omp parallel for schedule(static) if(f_ >= 64)
#endif
        for (long long ff = 0; ff < static_cast<long long>(f_); ++ff) {
            size_t f = size_t(ff);
            const auto& thresholds = cuts_[f];
            if (thresholds.empty()) continue;
            std::array<size_t, MAX_BINS + 1> count{};
            std::array<std::array<double, MAX_BINS + 1>, K> hist_g{}, hist_h{};
            const uint8_t* col = bins_.data() + f * n_;
            for (size_t row : rows) {
                uint8_t b = col[row];
                ++count[b];
                for (int k = 0; k < K; ++k) {
                    hist_g[k][b] += grad_[row * K + k];
                    hist_h[k][b] += hess_[row * K + k];
                }
            }
            std::array<size_t, MAX_BINS + 1> prefix_count{};
            std::array<std::array<double, K>, MAX_BINS + 1> prefix_g{}, prefix_h{};
            for (size_t b = 1; b <= thresholds.size() + 1; ++b) {
                prefix_count[b] = prefix_count[b - 1] + count[b];
                for (int k = 0; k < K; ++k) {
                    prefix_g[b][k] = prefix_g[b - 1][k] + hist_g[k][b];
                    prefix_h[b][k] = prefix_h[b - 1][k] + hist_h[k][b];
                }
            }
            const size_t finite_count = prefix_count[thresholds.size() + 1];
            for (size_t t = 1; t <= thresholds.size(); ++t) {
                size_t below_count = prefix_count[t];
                size_t above_count = finite_count - below_count;
                for (int missing_left = 0; missing_left <= 1; ++missing_left) {
                    size_t left_count = below_count + (missing_left ? count[0] : 0);
                    size_t right_count = above_count + (missing_left ? 0 : count[0]);
                    if (left_count < MIN_LEAF_ROWS || right_count < MIN_LEAF_ROWS) continue;
                    std::array<double, K> lg{}, lh{}, rg{}, rh{};
                    for (int k = 0; k < K; ++k) {
                        lg[k] = prefix_g[t][k] + (missing_left ? hist_g[k][0] : 0);
                        lh[k] = prefix_h[t][k] + (missing_left ? hist_h[k][0] : 0);
                        rg[k] = parent_g[k] - lg[k];
                        rh[k] = parent_h[k] - lh[k];
                    }
                    double gain = score(lg, lh) + score(rg, rh) - parent_score;
                    Candidate candidate{true, uint16_t(f), uint8_t(t), bool(missing_left), thresholds[t - 1], gain};
                    Candidate& current = per_feature[f];
                    if (!current.valid || candidate.gain > current.gain + 1e-12 ||
                        (std::abs(candidate.gain - current.gain) <= 1e-12 &&
                         std::tie(candidate.threshold, candidate.missing_left) < std::tie(current.threshold, current.missing_left)))
                        current = candidate;
                }
            }
        }
        for (const Candidate& candidate : per_feature) {
            if (!candidate.valid) continue;
            if (!best.valid || candidate.gain > best.gain + 1e-12 ||
                (std::abs(candidate.gain - best.gain) <= 1e-12 &&
                 std::tie(candidate.feature, candidate.threshold, candidate.missing_left) <
                 std::tie(best.feature, best.threshold, best.missing_left))) best = candidate;
        }
        return best;
    }

    void set_leaf(Node& node, const std::vector<size_t>& rows) {
        std::array<double, K> g{}, h{};
        for (size_t row : rows) for (int k = 0; k < K; ++k) {
            g[k] += grad_[row * K + k];
            h[k] += hess_[row * K + k];
        }
        for (int k = 0; k < K; ++k) node.value[k] = float(LEARNING_RATE * g[k] / (h[k] + L2));
    }

    void build_node(Node* tree, size_t node_index, const std::vector<size_t>& rows, int depth) {
        Node& node = tree[node_index];
        if (depth >= MAX_DEPTH) { set_leaf(node, rows); return; }
        Candidate split = best_split(rows);
        if (!split.valid || split.gain < MIN_GAIN) { set_leaf(node, rows); return; }
        node.feature = split.feature;
        node.flags = uint8_t(1 | (split.missing_left ? 2 : 0));
        node.threshold = split.threshold;
        ++split_uses_[split.feature];
        const uint8_t* col = bins_.data() + size_t(split.feature) * n_;
        std::vector<size_t> left, right;
        left.reserve(rows.size() / 2);
        right.reserve(rows.size() / 2);
        for (size_t row : rows) {
            uint8_t b = col[row];
            bool goes_left = b == 0 ? split.missing_left : b <= split.cut_bin;
            (goes_left ? left : right).push_back(row);
        }
        if (left.size() < MIN_LEAF_ROWS || right.size() < MIN_LEAF_ROWS)
            throw std::runtime_error("Chosen split violates min-leaf invariant");
        build_node(tree, node_index * 2 + 1, left, depth + 1);
        build_node(tree, node_index * 2 + 2, right, depth + 1);
    }

    void apply_train_tree(const Node* tree) {
        for (size_t row = 0; row < n_; ++row) {
            size_t node_index = 0;
            while (tree[node_index].flags & 1) {
                const Node& node = tree[node_index];
                float observed = x_[row * columns_ + node.feature];
                bool left = std::isfinite(observed) ? observed <= node.threshold : bool(node.flags & 2);
                node_index = node_index * 2 + (left ? 1 : 2);
            }
            for (int k = 0; k < K; ++k) margins_[row * K + k] += tree[node_index].value[k];
        }
    }

    std::vector<double> predict(const std::vector<float>& matrix, size_t rows) const {
        std::vector<double> result(rows * K);
        for (size_t row = 0; row < rows; ++row) {
            double margins[K] = {base_[0], base_[1], base_[2]};
            for (int round = 0; round < rounds_; ++round) {
                const Node* tree = nodes_.data() + size_t(round) * NODES_PER_TREE;
                size_t node_index = 0;
                while (tree[node_index].flags & 1) {
                    const Node& node = tree[node_index];
                    float observed = matrix[row * columns_ + node.feature];
                    bool left = std::isfinite(observed) ? observed <= node.threshold : bool(node.flags & 2);
                    node_index = node_index * 2 + (left ? 1 : 2);
                }
                for (int k = 0; k < K; ++k) margins[k] += tree[node_index].value[k];
            }
            double maximum = std::max({margins[0], margins[1], margins[2]});
            double total = 0;
            for (int k = 0; k < K; ++k) { result[row * K + k] = std::exp(margins[k] - maximum); total += result[row * K + k]; }
            for (int k = 0; k < K; ++k) result[row * K + k] /= total;
        }
        return result;
    }
};
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc != 11) throw std::runtime_error("Expected train, ntrain, columns, features, labels, weights, holdout, nhold, rounds, output-prefix");
        const std::string train_path = argv[1];
        size_t ntrain = std::stoull(argv[2]), columns = std::stoull(argv[3]), features = std::stoull(argv[4]);
        const std::string labels_path = argv[5], weights_path = argv[6], holdout_path = argv[7];
        size_t nhold = std::stoull(argv[8]);
        int rounds = std::stoi(argv[9]);
        const std::string prefix = argv[10];
        auto train = read_values<float>(train_path);
        auto labels = read_values<uint8_t>(labels_path);
        auto weights = read_values<float>(weights_path);
        auto holdout = read_values<float>(holdout_path);
        if (train.size() != ntrain * columns || holdout.size() != nhold * columns || features > columns)
            throw std::runtime_error("Input dimensions do not match binary files");
        Trainer trainer(train, ntrain, columns, features, labels, weights, rounds, holdout, nhold);
        trainer.fit();
        trainer.write_outputs(prefix);
        std::cerr << "wrote " << prefix << "\n";
    } catch (const std::exception& error) {
        std::cerr << "hq8_gbt_ablation: " << error.what() << "\n";
        return 2;
    }
    return 0;
}
