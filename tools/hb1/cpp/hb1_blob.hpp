// HB-1 v03: memory-map a direction model exported by tools/hb1/q4_export_direction_blob.py and expose it as an
// hb1::Model. The mapping is read-only and shared by every dragon process through the page cache. Local-only: the
// blob lives outside the bot directory (Params::hb1_dir_blob), so this build is an experiment, not a deployable bot.
#pragma once
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <string>
#include <vector>
#include "hb1_models.hpp"

namespace hb1 {

struct BlobModel {
    Model model{};
    std::vector<std::string> names;
    std::vector<char const*> name_ptrs;

    explicit BlobModel(char const* path) {
        int fd = ::open(path, O_RDONLY);
        if (fd < 0) throw std::runtime_error(std::string("hb1 blob: cannot open ") + path);
        struct stat st {};
        ::fstat(fd, &st);
        void* p = ::mmap(nullptr, size_t(st.st_size), PROT_READ, MAP_SHARED, fd, 0);
        ::close(fd);
        if (p == MAP_FAILED) throw std::runtime_error("hb1 blob: mmap failed");
        char const* b = static_cast<char const*>(p);
        if (std::memcmp(b, "HB1D", 4) != 0) throw std::runtime_error("hb1 blob: bad magic");
        size_t off = 4;
        auto i32 = [&]() { int32_t v; std::memcpy(&v, b + off, 4); off += 4; return v; };
        auto pad8 = [&]() { off = (off + 7) & ~size_t(7); };
        int K = i32(), n_feat = i32(), n_trees = i32(), n_nodes = i32(), n_classes = i32();
        (void)n_nodes;
        model.base = reinterpret_cast<float const*>(b + off); off += 4 * K;
        model.classes = reinterpret_cast<int const*>(b + off); off += 4 * n_classes;
        int len = i32();
        std::string all(b + off, size_t(len)); off += len;
        pad8();
        size_t s = 0;
        for (size_t e; (e = all.find('\n', s)) != std::string::npos; s = e + 1) names.push_back(all.substr(s, e - s));
        names.push_back(all.substr(s));
        for (auto const& n : names) name_ptrs.push_back(n.c_str());
        model.tree_start = reinterpret_cast<int const*>(b + off); off += 4 * size_t(n_trees);
        pad8();
        model.nodes = reinterpret_cast<Node const*>(b + off);
        static_assert(sizeof(Node) == 24, "Node layout must match the blob");
        model.name = "direction_v03";
        model.n_feat = n_feat;
        model.feats = name_ptrs.data();
        model.K = K;
        model.n_class = n_classes;
        model.n_trees = n_trees;
        if (int(names.size()) != n_feat) throw std::runtime_error("hb1 blob: feature count mismatch");
    }
};

}  // namespace hb1
