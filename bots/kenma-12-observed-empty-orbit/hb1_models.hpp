// HB-1: model node/struct definitions only. The direction-prior bots use just the compact direction model
// (hb1_direction_compact.hpp); the exported gate/alloc/sonar models of hb1-01 are not needed and are left out to
// fit the 4 MiB upload zip.
#pragma once
namespace hb1 {
struct Node { short f; float t; int yes, no, miss; float leaf; };
struct Model { char const* name; int n_feat; char const* const* feats; int K; int n_class;
               int const* classes; float const* base; int n_trees; int const* tree_start; Node const* nodes; };
}  // namespace hb1
