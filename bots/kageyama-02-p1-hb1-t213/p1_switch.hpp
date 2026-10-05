// kageyama-01-p1-slot (D-065 §D): the ONE switch of this bot against carthage-05-free-sprint.
// 1: the first-step direction prior comes from p1_model.hpp (a tree model on encoder v1 or on HB-1's feature vector,
//    as the header's p1::INPUT says; evaluated by gbt_compact.hpp)
//    in place of HB-1's direction GBT. Slot rule D-055 §E: F/R/L renormalised; reverse keeps the parent's value (0);
//    weight lambda = Params::hb1_dir_lambda, as in the parent.
// 0: carthage-05 exactly (golden parity); needs carthage-05's hb1_compact.hpp and hb1_direction_compact.hpp copied in.
#pragma once
#ifndef KAGEYAMA_P1_SLOT
#define KAGEYAMA_P1_SLOT 1
#endif
// With the slot on: 1 = arm A8b, the mirror-averaged prediction (two model evaluations a turn); 0 = one evaluation.
#ifndef KAGEYAMA_P1_MIRROR_AVG
#define KAGEYAMA_P1_MIRROR_AVG 0
#endif
