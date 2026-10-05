#pragma once
#include <array>
#include <cmath>
#include <stdexcept>
#include "hb1_compact.hpp"
#include "gbt_compact.hpp"
#include "kenma_teacher213_model.hpp"
namespace kenma {
inline std::array<double,3> teacher_direction(hb1::Row const& row){
 static_assert(teacher213::K==4 && teacher213::N_FEAT==270);
 static hb1::Bound const bound{hb1::dirc_bind};auto x=bound.vec(row);double p[4];
 GBT_PROBA(teacher213,x.data(),p);double z=p[0]+p[1]+p[3];
 if(!std::isfinite(z)||z<=0)throw std::runtime_error("teacher probability");
 return {p[0]/z,p[1]/z,p[3]/z};
}
}
