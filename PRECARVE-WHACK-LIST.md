# THE PRE-CARVE WHACK LIST (CEO-1940; Lon 2026-10-24 10:3x-11:0x)

Lon, verbatim: *"You, CEO, and CTO work together to get ALL BB's locals and results onto the RSP spine which are possible."* · *"The strategy to do so is to WHACK each pre-carve one at a time and see what breaks. Most will work since BB allocate their own memory."* · *"whacking the pre-alloc will SCREAM what's wrong."* · *"Take a list of those spots in the code that do a carve, and one by one mark them off by whacking it and doing a little testing."*

THE METHOD, one site per landing: whack the carve (delete it, leave its readers to scream or as named bombs), build, run the smokes of the languages the site reaches (all eight for a shared site) and the feature handful, note what screamed, cure the screamer by making the box carve its own cell, mark the row. The hook's PLACEMENT table (pre-allocs, RSP resets at β, allocs at β) is the running score; `test_gate_no_rsp_reset_at_beta.sh` blocks at 0. Measured 2026-10-24 at SCRIP e840d8e39: 107 `x86("sub", "rsp", …)` sites in `src/templates` and `src/emitter` plus 25 `x86_rsp_land` sites; 90 of them carve a constant (a box's own cell, record or argument block) and are NOT on this list; the 17 below carve a computed size at an entry and are the pre-carve candidates. A site that turns out to be a box's own carve is marked KEEP with the reason; a site whose whack screams names the screamer and its cure.

| # | site | carve | what it carves (reading before the whack) | seat | status |
|---|---|---|---|---|---|
| D0 | `src/driver/scrip.c` main prologue | `sub rsp, 65544` floored, sized from `jcon_value_region` | the root graph's keyed value region, every value box carving its own cell anyway | ceo | WHACKED SCRIP 65c05d8d0 (branch `ceo/d0-main-carve`, the cto's review before main moves): 8 smokes, 5 cores both modes, prolog+raku cores equal to origin entry for entry, asm diff one line, nothing screamed |
| 1 | `src/emitter/emit.cpp:4378` (text) + `src/templates/xa/xa_flat.cpp:156,356,530` (binary twins) | `sub rsp, frame_total` / `kt = g_emit.flat_frame_bytes` | the chain's ζ-ACTIVATION-FRAME: the layout's keyed slots for the chain's locals and value boxes (Prolog 174,250 and Icon 11,992 pre-allocs live here) | cto (D2 Icon, D3 Prolog per ARCH § 10) | TODO |
| 2 | `src/templates/xa/xa_flat.cpp:539` | `sub rsp, argkt` (`16 * nsave`) | the CLASS-C chain's saved-argument block | cto | TODO |
| 3 | `src/templates/bb/bb_match_begin.cpp:39` | `sub rsp, 24 + op_frame_extra` | the match frame's extra: cells the pattern's boxes write (`emit_match_begin_frame_extra`) | cto (D1) | TODO |
| 4 | `src/emitter/emit.cpp:4436` | `sub rsp, blob_carve_bytes() + blob_carve_pad()` | the pattern blob's frame | cto | TODO |
| 5 | `src/emitter/emit.cpp:4445` | `sub rsp, _sph` | the blob's header cell (DT_P + rdx) | cto | TODO |
| 6 | `src/templates/bb/bb_glue_framed.cpp:11` | `sub rsp, (op_fc_bytes + 15) & ~15` | frame cells glue carves for the chain's boxes (`fc_geom`, `g_zd_k`) | ceo | TODO |
| 7 | `src/templates/bb/bb_glue_flat.cpp:30` | `sub rsp, op_fc_bytes` | the same frame cells, flat glue | ceo | TODO |
| 8 | `src/templates/bb/bb_call_fn.cpp:109` | `sub rsp, CF_N() * 16` | the call's argument block the argument boxes write into | ceo | TODO |
| 9 | `src/templates/bb/bb_call_fn.cpp:320` | `sub rsp, BCFN_EVAL_REC` | the call's eval record | ceo | TODO (classify) |
| 10 | `src/templates/bb/bb_call_proc_staged.cpp:305` | `sub rsp, Kbz = 16 * op_ival + 32` | the staged call's argument block | ceo | TODO |
| 11 | `src/templates/bb/bb_call_proc_staged.cpp:478` | `sub rsp, Kb = 16 * op_ival + 32` | the staged call's argument block, second arm | ceo | TODO |
| 12 | `src/templates/bb/bb_define.cpp:383` | `sub rsp, F4 = T4 + 16*nf4 + 16*nnv4` | the DEFINE call's saved formals and locals | ceo | TODO (classify: the call's own record?) |
| 13 | `src/templates/bb/bb_define.cpp:696` | `sub rsp, T4 + 16*nf4` | the DEFINE call's argument block | ceo | TODO |
| 14 | `src/templates/bb/bb_match_fence0.cpp:23` + `bb_match_flush.cpp:88` | `sub rsp, op_fence0_floor` | FENCE's floor | ceo | TODO (classify: FENCE's own?) |
| 15 | `src/templates/x86/x86_asm.h:2507` | `sub rsp, op_zbgrow` at a DEF β | growth at β (an allocation at β, reported by the watch) | cto | TODO |
| 16 | `src/templates/bb/bb_create.cpp:27` | `edx = max(flat_carve_total, frame_region)` to the runtime | the co-expression's frame size handed to `rt` (not an emitted carve) | cto | TODO (classify) |

Marked off when its status reads WHACKED <hash> with what screamed, or KEEP <why>. The list is the ceo's; the cto reorders its own rows; every landing names its row here.
