// Combined legal observation inputs, in verified training order.
#pragma once
#include <array>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include "learn_helper.hpp"
#include "gbt_compact.hpp"
#include "kenma_stacked_model.hpp"
namespace kenma {
static_assert(learn::N_X==1193 && kenma_stacked::N_FEAT==1466 && kenma_stacked::K==4);
struct Stacked {
    learn::Encoder enc;
    std::array<float,1466> x{};
    std::array<double,4> p{};
    Stacked(unswbc::Controller const& ct,unswbc::Game const& game):enc(learn::spawn_from(ct,game)){}
    void observe(unswbc::Controller const& ct,unswbc::Game const& game,hb1::Row const* row) {
        auto const& ex=enc.observe(learn::block_from(ct,game));
        if(!row)throw std::runtime_error("missing HB row");
        static hb1::Bound const bound{hb1::dirc_bind};
        auto hx=bound.vec(*row);
        auto hp=hb1::dirc_proba(hx);
        for(int i=0;i<learn::N_X;++i)x[i]=static_cast<float>(ex[i]);
        for(int i=0;i<270;++i)x[1193+i]=hx[i];
        for(int i=0;i<3;++i) {
            char text[32];std::snprintf(text,sizeof(text),"%.6f",hp[i]);
            x[1463+i]=std::strtof(text,nullptr);
        }
        GBT_PROBA(kenma_stacked,x.data(),p.data());
    }
    void act(int kind,int first_rel,int steps,int round){enc.act(kind,first_rel,steps,round);}
};
}
