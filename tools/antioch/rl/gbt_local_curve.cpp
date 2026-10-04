// Evaluate compact GBT prefixes with the deployment evaluator's double sums.
// Define GBT_HEADER_PARITY and include the original bot headers to compare
// the full-model prediction with hb1::dirc_proba on a small sample.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef GBT_HEADER_PARITY
#include "hb1_compact.hpp"
#endif

template <class T> std::vector<T> read_binary(std::string const& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) throw std::runtime_error("Cannot read " + path);
    auto bytes = input.tellg();
    if (bytes < 0 || size_t(bytes) % sizeof(T)) throw std::runtime_error("Invalid binary length");
    std::vector<T> values(size_t(bytes) / sizeof(T));
    input.seekg(0);
    input.read(reinterpret_cast<char*>(values.data()), bytes);
    if (!input) throw std::runtime_error("Incomplete binary read");
    return values;
}

std::vector<int> split(std::string const& text) {
    std::istringstream input(text);
    std::vector<int> values;
    for (std::string value; std::getline(input, value, ',');) values.push_back(std::stoi(value));
    return values;
}

int main(int argc, char** argv) {
    try {
        if (argc != 6) throw std::runtime_error("Expected directory, rows, features, classes and checkpoints");
        std::string dir = argv[1];
        size_t rows = std::stoull(argv[2]), features = std::stoull(argv[3]);
        int classes = std::stoi(argv[4]);
        auto checkpoints = split(argv[5]);
        if (classes < 2 || checkpoints.empty() || checkpoints.front() < 1 ||
            !std::is_sorted(checkpoints.begin(), checkpoints.end())) throw std::runtime_error("Invalid checkpoints");
        auto x = read_binary<float>(dir + "/features.f32");
        auto base = read_binary<float>(dir + "/base.f32");
        auto starts = read_binary<int32_t>(dir + "/starts.i32");
        auto nodes = read_binary<uint64_t>(dir + "/nodes.u64");
        if (x.size() != rows * features || int(base.size()) != classes ||
            checkpoints.back() * size_t(classes) > starts.size()) throw std::runtime_error("Shape mismatch");
        std::vector<std::ofstream> outputs(checkpoints.size());
        for (size_t point = 0; point < checkpoints.size(); point++) {
            outputs[point].open(dir + "/probabilities-" + std::to_string(checkpoints[point]) + ".f64", std::ios::binary);
            if (!outputs[point]) throw std::runtime_error("Cannot create prediction output");
        }
        double worst = 0;
        size_t argmax_diff = 0;
        for (size_t row = 0; row < rows; row++) {
            std::vector<double> margins(base.begin(), base.end()), probabilities(classes);
            size_t checkpoint = 0;
            for (int tree = 0; tree < checkpoints.back() * classes; tree++) {
                size_t node = starts[tree];
                for (;;) {
                    uint64_t word = nodes.at(node);
                    unsigned feature = unsigned((word >> 32) & 0x7FFF);
                    uint32_t bits = uint32_t(word);
                    float value;
                    std::memcpy(&value, &bits, sizeof(value));
                    if (feature == 0x7FFF) {
                        margins[tree % classes] += value;
                        break;
                    }
                    if (feature >= features) throw std::runtime_error("Invalid feature index");
                    float observed = x[row * features + feature];
                    bool left = std::isnan(observed) ? ((word >> 47) & 1) : observed < value;
                    node += left ? 1 : word >> 48;
                }
                int rounds = tree / classes + 1;
                if ((tree + 1) % classes != 0 || rounds != checkpoints[checkpoint]) continue;
                double maximum = *std::max_element(margins.begin(), margins.end()), total = 0;
                for (int k = 0; k < classes; k++) {
                    probabilities[k] = std::exp(margins[k] - maximum);
                    total += probabilities[k];
                }
                for (double& value : probabilities) value /= total;
                outputs[checkpoint].write(reinterpret_cast<char*>(probabilities.data()), classes * sizeof(double));
                if (++checkpoint == checkpoints.size()) break;
            }
#ifdef GBT_HEADER_PARITY
            if (features != hb1::dirc_n_feat || classes != hb1::dirc_K ||
                checkpoints.back() * classes != hb1::dirc_n_trees) throw std::runtime_error("Header shape differs");
            std::vector<float> sample(x.begin() + row * features, x.begin() + (row + 1) * features);
            auto actual = hb1::dirc_proba(sample);
            for (int k = 0; k < classes; k++) worst = std::max(worst, std::abs(actual[k] - probabilities[k]));
            argmax_diff += std::max_element(actual.begin(), actual.end()) - actual.begin() !=
                           std::max_element(probabilities.begin(), probabilities.end()) - probabilities.begin();
#endif
            if ((row + 1) % 10000 == 0) std::cerr << "evaluated " << row + 1 << '/' << rows << " rows\n";
        }
        for (auto& output : outputs) {
            output.close();
            if (!output) throw std::runtime_error("Incomplete prediction write");
        }
        std::cout << "{\"rows\":" << rows << ",\"header_parity\":"
#ifdef GBT_HEADER_PARITY
                  << "true"
#else
                  << "false"
#endif
                  << ",\"max_probability_difference\":" << std::setprecision(17) << worst
                  << ",\"argmax_differences\":" << argmax_diff << "}\n";
        return argmax_diff || worst > 1e-14 ? 1 : 0;
    } catch (std::exception const& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
