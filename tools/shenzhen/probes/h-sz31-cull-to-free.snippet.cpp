// SHENZHEN PROBE K (H-SZ31, "cull to free") — insert after probe D in main.cpp of the C+D patch (analysis copy only).
// At the unit cap a short non-queen (len 2) on its round slot kills itself (invalid command), leaving a corpse and a
// free slot; no production split is ever blocked.
if (ct.get_id() > 1 && w.units >= w.limit && w.len <= 2 && (ct.get_id() + w.rnd) % 6 == 0) {
    std::cout << "SPLIT 99\nLOG SZ:cap_cull\nPROTOCOL " << unswbc::Constants::PROTOCOL_MAJOR << "\n";
    pol.send_radio(ct); std::cout << "ENDTURN\n" << std::flush; continue;
}
