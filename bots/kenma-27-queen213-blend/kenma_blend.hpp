#pragma once
#include <array>
#include <vector>
#include <cmath>
#include <algorithm>
namespace kenma {
inline std::vector<double> blend_direction(std::vector<double> const& parent,std::array<double,3> const& teacher){
 std::vector<double> p(3);double z=0;
 for(int i=0;i<3;++i){p[i]=std::sqrt(std::max(parent[i],1e-4)*std::max(teacher[i],1e-4));z+=p[i];}
 for(auto& v:p)v/=z;return p;
}
}
