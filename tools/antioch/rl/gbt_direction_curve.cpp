// CPU evaluator for gbt_direction_curve.py's compact HB1 tree prefixes.
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

template <class T> std::vector<T> split(std::string const& text) {
    std::istringstream input(text);
    std::vector<T> values;
    for (std::string value; std::getline(input, value, ',');) {
        std::istringstream number(value);
        T parsed;
        if (!(number >> parsed)) throw std::runtime_error("Invalid number");
        values.push_back(parsed);
    }
    return values;
}

int main(int argc, char** argv) {
    try {
        if (argc != 8) throw std::runtime_error("Expected model directory, rows, features, K, rounds, base, classes");
        std::string dir = argv[1];
        size_t rows = std::stoull(argv[2]), features = std::stoull(argv[3]);
        int classes_count = std::stoi(argv[4]);
        auto checkpoints = split<int>(argv[5]);
        auto base = split<double>(argv[6]);
        auto classes = split<int>(argv[7]);
        auto x = read_binary<float>(dir + "/features.f32");
        auto labels = read_binary<int32_t>(dir + "/labels.i32");
        auto starts = read_binary<int32_t>(dir + "/starts.i32");
        auto nodes = read_binary<uint64_t>(dir + "/nodes.u64");
        if (x.size() != rows * features || labels.size() != rows || int(base.size()) != classes_count ||
            classes.size() != base.size()) throw std::runtime_error("Shape mismatch");
        std::vector<double> margins(rows * classes_count);
        for (size_t row = 0; row < rows; row++)
            std::copy(base.begin(), base.end(), margins.begin() + row * classes_count);
        size_t checkpoint = 0;
        for (int tree = 0; tree < checkpoints.back() * classes_count; tree++) {
            if (size_t(tree) >= starts.size()) throw std::runtime_error("Tree prefix exceeds model");
            for (size_t row = 0; row < rows; row++) {
                size_t node = starts[tree];
                for (;;) {
                    uint64_t word = nodes.at(node);
                    unsigned feature = unsigned((word >> 32) & 0x7FFF);
                    uint32_t bits = uint32_t(word);
                    float value;
                    std::memcpy(&value, &bits, sizeof(value));
                    if (feature == 0x7FFF) {
                        margins[row * classes_count + tree % classes_count] += value;
                        break;
                    }
                    if (feature >= features) throw std::runtime_error("Invalid feature index");
                    float observed = x[row * features + feature];
                    bool left = std::isnan(observed) ? ((word >> 47) & 1) : observed < value;
                    node += left ? 1 : word >> 48;
                }
            }
            int rounds = tree / classes_count + 1;
            if ((tree + 1) % classes_count == 0 && rounds == checkpoints[checkpoint]) {
                size_t correct = 0;
                for (size_t row = 0; row < rows; row++) {
                    auto begin = margins.begin() + row * classes_count;
                    int predicted = int(std::max_element(begin, begin + classes_count) - begin);
                    correct += classes[predicted] == labels[row];
                }
                std::cout << rounds << ',' << std::setprecision(12) << double(correct) / rows << '\n';
                if (++checkpoint == checkpoints.size()) break;
            }
        }
        return 0;
    } catch (std::exception const& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
