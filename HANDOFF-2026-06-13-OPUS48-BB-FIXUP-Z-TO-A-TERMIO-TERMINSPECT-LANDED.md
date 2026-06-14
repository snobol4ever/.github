# HANDOFF — 2026-06-13 (Opus 4.8, 10th session) — GOAL-BB-FIXUP-Z-to-A

## STATE (verified at handoff)
- **SCRIP @ `9c524af`** (committed + **pushed** to origin/main). `git log origin/main --oneline -1` confirms `9c524af`. Two commits landed this session: `9bf7ab3` (bb_term_io) then `9c524af` (bb_term_inspect).
- **CURSOR: `bb_resolve.cpp`** (tracker `# CURSOR:` line — unchanged; HELD, still dirty at **23** violations).
- SCRIP source tree CLEAN, matches pushed HEAD. `.github` updated this turn (watermark + this doc).
- All landed changes behavior-neutral.
- **Pre-existing reds (NOT introduced, do not chase):** rebus `hello` ROW-DRIFT (smoke 5/6, on-hold per PLAN); `util_template_purity_audit.sh` rc=1 = single `bb_call_write_slot.cpp` fprintf.

## CONTEXT ON ARRIVAL — HEAD had advanced past the 9th-session handoff
The 9th session ended at `d884849`; this session opened at **`9baaf64`** (concurrent IR-NEVER-TOUCHED work landed in between). The load-bearing commits:
- **`0f6506b`** — deleted `rt_node_to_term_ptr`/`rt_is_eval`/`rt_throw` + `emit_term_from_node_bin`, and **bombed the divergent BINARY raw-byte arms in `bb_term_inspect`/`bb_term_io`/`bb_list`** (they baked an `IR_t*` for runtime deref). So both target files arrived with their BINARY arm already a single `x86_bomb` line — the conversion was **cleaner** than the 9th-session recipe assumed (no raw-byte BINARY arm left to collapse).
- **`8b9a58e`** — "Revert mode3/4 entry bombs — emission read of IR is required & allowed." The clarification that makes the both-medium conversion legal: **emit-time IR walking is BLESSED**; only RUNTIME IR deref is forbidden.

∴ routing BOTH mediums through the emit-time `emit_build_compound_term` is correct and IR-NEVER-TOUCHED-compliant. Verified from source (`emit_term_build.cpp:93`): it builds entirely from emit-time-known scalars + sealed `[rip+__]` string labels (`blbl_lea`) + `rt_compound_build_n`/`rt_node_to_term` calls. It bakes **no** `IR_t*` for runtime deref.

## WHAT LANDED

### (1) bb_term_io — audit 53 → 0 CLEAN (SCRIP `9bf7ab3`)
`bb_term_io_str(IR_t*, const char*, const std::string&)` → parameterless **`std::string bb_term_io()`**.
- Builtins: `numbervars/3`, `term_to_atom`/`term_string/2`, `format/1`, `format/2` (4 arms; guard + one ternary).
- Dropped `pBB`/`fn`/`hdr` (CV9) + all `ir_call_arg`/`IR_LIT` (CV10). Reads `_.op_sval`/`_.op_ival`/`_.op_parts_n` for dispatch, `_.op_parts_tag/ival/str/lbl[0..2]` for scalar args, `(IR_t*)(intptr_t)_.op_parts_ival[8+j]` for `emit_build_compound_term` node ptrs.
- `@PLT` string-calls → fn-ptr form `x86("call","rt_X",(uint64_t)(uintptr_t)(void*)rt_X)`. (rt_numbervars_term / rt_term_to_atom_term / rt_format_term / rt_format were already declared in bb_common.h.)
- **Iteration note:** first pass tripped `returns_plus`+`multi_x86` from a single-line 5-`x86()` tail helper. Fix = inline the tail as separate `+ x86()` lines per arm and drop the helper — exactly the `bb_type_test` shape. Audit clean after that.

### (2) bb_term_inspect — audit 94 → 0 CLEAN (SCRIP `9c524af`)
`bb_term_inspect_str(...)` → parameterless **`std::string bb_term_inspect()`**.
- Builtins: `functor/3` (functor_t/s by a0==IR_STRUCT), `arg/3` (arg_t/s by a1==IR_STRUCT), `=../2` (univ_tt/t1/1t/ss by a0/a1==IR_STRUCT combos) — **8 emit variants** collapsed into ONE return ternary (`if(!_.op_sval)` guard + ternary = 2 returns, within budget).
- Same prep mapping. Node ptrs `_.op_parts_ival[8]` (a0) / `[9]` (a1). `@PLT`→fn-ptr.
- **Added extern decls `rt_functor`/`rt_arg`/`rt_univ` to `bb_common.h`** — the 3 scalar-arm fns are defined in `src/interp/IR_interp.c:1926/1953/2013` and the symbols are already linkable (present in `scrip` + `out/libscrip_rt.so`), but lacked a decl so their address could not be taken for the fn-ptr call form (BINARY mode-3 has no PLT).
- **Clean first pass, no iteration** (the term_io tail/ternary lessons carried over).

Both: `bb_common.h` decl made parameterless + `bb_resolve.cpp` bdisp call-site updated. `bb_resolve.cpp` **25 → 23** (cv9 8→6 — both `_str` refs gone). No stray `bb_term_io_str`/`bb_term_inspect_str` anywhere.

## PRIMARY FINDING — DEAD re-verified at the NEW HEAD for BOTH files
The 9th session claimed the resolver family is DEAD (arms shadowed by `IR_DET_*`). Re-verified at `9baaf64` for both files with match-condition fire-probes (reverted):
- `bb_term_io`: shadowed by `IR_DET_FORMAT`. Zero fires across `test/prolog/*.pl` + synthetic `format/1`,`format/2`,`numbervars/3`,`term_to_atom/2` × m2/m3/m4.
- `bb_term_inspect`: shadowed by `IR_DET_FUNCTOR/ARG/UNIV` (emit_core.c:531-533, built by `pl_gz_det_node` scrip.c:1297/1321/1344). Zero fires across synthetic `functor/3`,`arg/3`,`=../2` × m2/m3/m4.
- Output IDENTICAL before/after for every probe (hello / a and b / f(A,B) / f(a,b) / f/2 / x / [f,a,b]).
- ∴ behavior-neutral by the strongest "no firing corpus → C2-by-construction" standard. The 8 (functor/arg/univ) + 4 (term_io) divergences were between UNREACHABLE paths.
- NOTE: `bti_functor.pl` m3/m4 abort (rc=134/1) is a **pre-existing** GZ-admission failure (present at HEAD without my change) — NOT mine, noted-not-chased per rule 5.

## GATES (green vs baseline, both files)
audit 0 CLEAN · prolog xcheck 4/0 (3-mode agree) · icon xcheck 4/0 HARD + m4 4/4 · byte_identity 4/0 · bin_t 0 · vstack 3 (floor) · handencoded 0 · sno_pat_reg TIER1+2 HARD · pl_m34 vacuous · smoke 5/6 (rebus ROW-DRIFT pre-existing) · purity 1 (bb_call_write_slot fprintf pre-existing).

## NEXT — continue Z→A among the resolver family (all DEAD-path low-risk hygiene)
Same mechanical pattern as bb_term_io / bb_term_inspect:
1. **`bb_list` (89)** — next file. Full multi-variant conversion (~bb_term_inspect size).
2. `bb_is_cmp` (172) — biggest.
3. **`bb_findall` (16, HEAVY)** — NOT pure template hygiene. Needs new `sm_emit_t` fields + `emit_bb.c` IR_BUILTIN prep for the findall **fs-state digest** (`fs->goal_node` incl GCONJ scan, tmpl, result, fail/true flag) + both-medium unify of the `rt_findall` baked-ptr / `rt_findall_term` term-build paths. Do this one last and budget a dedicated session.

**Per-file recipe (non-findall):** parameterless `std::string bb_X()`; guard on `_.op_sval`; own `strcmp`; read `_.op_sval`/`_.op_ival`/`_.op_parts_n` + `_.op_parts_tag/ival/str/lbl[0..2]`; node ptrs for `emit_build_compound_term` from `(IR_t*)(intptr_t)_.op_parts_ival[8+j]`; convert `@PLT`→fn-ptr (**verify each scalar-arm `rt_*` is declared in `bb_common.h` — add `extern` if missing**, as done for rt_functor/arg/univ; defs are in `src/interp/IR_interp.c`); inline the 5-line tail per arm; **split every lbl-ternary across 2 physical lines** (one `x86()` per line, else `multi_x86` trips); keep returns ≤ 2 total. Then `bb_common.h` decl + `bb_resolve.cpp` bdisp call → `bb_resolve` cv9 drops.

**FINAL rung (when `bdisp` empties of all `_str` calls):** `bb_resolve()`/`bdisp` go parameterless — drop the `bdisp(IR_t*)`/`bb_resolve(IR_t*)` sigs (CV9), the `bytes("\xE9")+u32le(0)` MEDIUM_BINARY fallback (CV5/raw_bytes), and the `return r` chain → `bb_resolve.cpp` reaches rc=0 → **advance the cursor** (in the same commit) to the next dirty file strictly-before `bb_resolve` alphabetically.

## STATE NOTES
- SCRIP source tree CLEAN, matches pushed `9c524af`; binaries regenerate at session setup. ENV needs `libgc-dev` + `libgmp-dev` (both in `scripts/install_system_packages.sh` — run setup; an un-run-setup env fails at `gc/gc.h`).
- The `_` prep struct (`emit_globals.h`) arrays are all `[16]`; the IR_BUILTIN prep (`emit_bb.c:1150-1191`) populates `op_parts_tag/ival/str[0..2]`, node ptrs `op_parts_ival[8..10]`, `op_parts_lbl[0..3]`, `op_sval`/`op_sval_lbl`/`op_ival`/`op_parts_n`. This covers every scalar/atom/struct arg the non-findall resolver sub-handlers read.

## PROCESS NOTE
Context gauge remains unobservable to the agent. Stopped at ~68% (estimate) after banking 2 clean + verified + pushed conversions, rather than half-start `bb_list` (a full multi-variant conversion) at the brake. Both conversions are on origin; the next session's resume procedure re-audits and lands on `bb_list` as the next dirty sub-handler — no half-state was left.
