// Read the established HB1 TURN/END/ACT replay-block format and emit int32 rows.
#include "hq8_features.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>

static std::vector<std::string> tokens(std::string const& line) {
    std::istringstream input(line);
    std::vector<std::string> out;
    for (std::string word; input >> word;) out.push_back(word);
    return out;
}
static hq8::Block parse(std::vector<std::string> const& lines) {
    hq8::Block b;
    size_t i = 0;
    auto kv = [&](std::string const& name) {
        auto p = tokens(lines.at(i++));
        if (p.at(0) != name) throw std::runtime_error("expected " + name);
        return p;
    };
    b.round = std::stoi(kv("ROUND").at(1));
    kv("DIR"); b.length = std::stoi(kv("LENGTH").at(1)); kv("UNIT_COUNT");
    int messages = std::stoi(kv("NUM_MSGS").at(1)); i += messages;
    if (lines.at(i).rfind("ECHOES", 0) == 0) i++;
    for (auto& t : b.tiles) {
        auto p = tokens(lines.at(i++));
        t = {std::stoi(p.at(0)), std::stoi(p.at(1)), std::stoi(p.at(2)), std::stoi(p.at(3))};
    }
    int n = std::stoi(kv("DRAGON_BODIES").at(1));
    for (int k = 0; k < n; k++) {
        auto p = tokens(lines.at(i++));
        b.bodies.push_back({p.at(0)[0], std::stoi(p.at(1)), std::stoi(p.at(2)), std::stoi(p.at(3)), p.at(4)[0], p.at(5) == "1"});
    }
    for (auto& row : b.H) { auto p = tokens(lines.at(i++)); for (size_t c = 0; c < row.size(); c++) row[c] = p.at(c); }
    for (auto& row : b.V) { auto p = tokens(lines.at(i++)); for (size_t c = 0; c < row.size(); c++) row[c] = p.at(c); }
    if (i != lines.size()) throw std::runtime_error("trailing block input");
    return b;
}
int main() {
    std::map<int, hq8::Encoder> actors;
    int current = -1;
    for (std::string line; std::getline(std::cin, line);) {
        auto p = tokens(line);
        if (p.empty()) continue;
        if (p[0] == "TURN") {
            current = std::stoi(p.at(1));
            if (!actors.count(current)) actors.emplace(current, hq8::Encoder(current, p.at(2)[0], std::stoi(p.at(3)), std::stoi(p.at(4)), std::stoi(p.at(5))));
            std::vector<std::string> block;
            while (std::getline(std::cin, line) && line != "END") block.push_back(line);
            auto row = actors.at(current).features(parse(block));
            // Explicit little-endian bytes: portable across host endianness.
            for (int32_t value : row) {
                uint32_t u = static_cast<uint32_t>(value);
                for (int byte = 0; byte < 4; byte++) std::cout.put(static_cast<char>((u >> (8 * byte)) & 255));
            }
        } else if (p[0] == "ACT" && p.at(1) == "split") actors.at(current).record_split();
    }
}
