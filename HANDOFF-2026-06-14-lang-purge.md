# HANDOFF 2026-06-14 — LANGUAGE-PREFIX PURGE (continuation of GOAL-RAKU-BB)

## What shipped (SCRIP `f548d70`, on origin/main; rebased onto the IR_CALL-split tip)

One consolidated, behavior-neutral commit de-language-naming post-lower symbols, plus the RK-NFA-4a smoke. All renames are pure token renames (no logic change). Green: oracle 5/5, Raku 37/37 m2 (35+2 EXCISED m3/m4), Icon 12/12/12, SNOBOL4 7/7/7 (m4 HARD).

- **RENAME-C (NFA/regex engine, runtime-invoked, incidental `src/parser/raku/` filing):**
  `Raku_match`→`Match`, `Raku_nfa`→`Nfa`, `Raku_cc`→`Cc`, `Raku_code_fn`→`Code_fn`, `raku_cc_test`→`cc_test`, `raku_nfa_*`→`nfa_*`, `raku_re*`→`re*`, `g_raku_match`→`g_match`, `g_raku_subject`→`g_subject`; guard `RAKU_RE_H`→`NFA_RE_H`; FILES `raku_re.{c,h}`→`re.{c,h}`, `raku_nfa_bb.c`→`nfa_bb.c` (git mv). Parser entry points `raku_driver`/`raku_compile` UNTOUCHED.
- **icn_ (single `s/_icn_/_/g`, collision-clean):** `rt_icn_*`→`rt_*` (`rt_substr`, `rt_scan_enter/leave`, `rt_keyword_pos/subject`), `flat_drive_alt_icn_gen`→`flat_drive_alt_gen`, `flat_drive_icn_global_assign`→`flat_drive_global_assign`. `g_icn_postfix_resume`→`g_postfix_resume` — **cross-boundary**: defined in `lower/lower_icon.c` + `lower/lower.h` (where prefixes are *allowed*) but consumed by `driver/scrip.c`; renamed at the definition too so the driver use is neutral and still links. (This is the general rule: a parser/lower symbol *consumed by the six dirs* must be neutralized at its definition.)
- **RENAME-SNO (emitted asm-label strings — file-local, never co-linked):** `sno_proc_startup`→`proc_startup`, `sno_flat`→`flat` (flat-chain prefix in both `scrip.c` and `emit_bb.c`), `.Lsno_*`→`.L*`, `sno_pidx_buf`→`pidx_buf`.
- **SNOBOL interp C-vars (`IR_interp.c`-local + cross-file):** `SnoSaveEnt`→`SaveEnt`, `SNO_SAVE_MAX`→`SAVE_MAX`, `g_sno_save`→`g_save_stack` (DISTINCT — a plain `g_save` collides with 15 preexisting), `g_sno_save_top`→`g_save_stack_top`, `g_sno_cur_func`→`g_cur_func`, `g_sno_m4_dense_nid`→`g_m4_dense_nid` (def in `emit_core.c`).
- **Shared `ProcEntry` field** `sno_entry_idx`→`proc_entry_idx` (def `contracts/stage2.h`; uses in `scrip.c`/`gen_runtime.h`/`lower_snobol4.c`/`sm_prog.c`).
- **`polyglot.c`** local `_is_raku_owned`→`_lang_owned` (the `s_lang == LANG_RAKU` dispatch enum is retained-necessary; only the var name changed).
- **RK-NFA-4a-SMOKE:** two `~~` verdict smokes in `test_smoke_raku.sh` (`'abc123' ~~ /\d+/`→match, `'abc' ~~ /^\d+$/`→nomatch). m2 PASS, m3/m4 EXCISE.

Net LI-FENCE effect: `src/emitter` + `src/runtime` are now cleared of `icn_`, `sno_`, and regex-engine tokens. **Zero new violations introduced** (verified: none of `g_save_stack`/`proc_startup`/`proc_entry_idx`/`g_m4_dense_nid`/`rt_substr`/`flat_drive_alt_gen`/`_lang_owned`/`flat` is flagged).

## What is DELIBERATELY NOT done (blocked / owner-only) — the precise audit

The enforced purge scope is `scripts/test_gate_no_lang_names.sh` (the LI-FENCE) over `src/emitter` + `src/runtime` (minus `src/runtime/core/`, the SNOBOL library = separate LI-CORE decision). It is still RED at 128 lines — **all pre-existing, none from this purge.** Do NOT blind-`sed` these; they break the build and/or step on an active session.

1. **Prolog GZ type-migration tail (owner-only; densely gated).** The Prolog session already migrated the gz FUNCTIONS to neutral names (`gz_emit_cell`, `gz_callee_labels`, `gz_emit_chain`, …) but the TYPES still carry `pl_`:
   `pl_gz_call_state_t`, `pl_gz_findall_state_t`, `pl_gz_callee_t`, `pl_gz_ite_state_t`; entry fns `pl_gz_build`, `pl_gz_codegen`; catch-block tracker `pl_catch_block_index`, `g_pl_catch_nodes`, `g_pl_catch_n`, `PL_CATCH_MAX`; runtime `rt_pl_is_cell_int`/`rt_pl_is_cell_float`.
   This is IN-FLIGHT Prolog work, guarded by `test_gate_pl_gz2..7`, `test_gate_pl_coupling`, `test_gate_pl_no_new_global`, `test_gate_pl_m34_parity`. **Recommendation:** the Prolog owner finishes `pl_gz_*_t`→`gz_*_t` (+ `pl_catch_*`→`catch_*`, `g_pl_catch_*`→`g_catch_*`, `PL_CATCH_MAX`→`CATCH_MAX`, `rt_pl_is_cell_*`→`rt_is_cell_*`) as ONE commit, running the full `pl_*` gate suite. RULES.md "edit only your own boxes" applies — this is the Prolog session's box.

2. **LI-FENCE false-positives to ADD to the gate's ALLOW list** (the gate explicitly invites this):
   - `__rk_bool` — a frontend-contract dispatch string, exactly like the already-carved `__rk_jct`/`__rk_arr`; and the `CALL_ROUTE_RK_BOOL_*` enum that routes it.
   - `IR_DET_SUCC_PLUS` / `_PLUS` — benign ("PLUS" matches the `_PL` tag by accident).
   - the `_pl` union local in the float-bit-cast (`union { double d; int64_t q; } _pl;`).
   Also the LI-FENCE ALLOW list still carries now-DEAD Raku-NFA carve-outs (`Raku_nfa`, `Raku_match`, `raku_nfa_`, `raku_re`, `raku_nfa_compile`, `g_raku_match`, `g_raku_subject`) — RENAME-C removed those symbols, so the entries are harmless but stale; trim when convenient.

3. **`pas_*` (Pascal frame / static-link helpers) — owner-only; NO gate to verify.**
   `pas_base`, `pas_slot_read`, `pas_slot_write`, `pas_uplevel_find`, `pas_loc_of_name`, `pas_sl_setup`, `pas_real_str` — in `interp/IR_interp.c` (m2, `static`) **and** referenced via `runtime/by_name_dispatch.c` + `emitter/BB_templates/bb_call.cpp` (m3/m4). A naive prefix-strip collides hard (`base` appears ×153 in IR_interp.c). There is **no `test_smoke_pascal.sh`** to catch a regression. **Recommendation:** the Pascal owner renames to concept-based names (`frame_base`, `frame_slot_read`/`write`, `frame_uplevel_find`, `frame_loc_of_name`, `static_link_setup`, `real_to_str`) across all three files and lands a Pascal smoke gate alongside. (Note: the IR_interp.c copy is outside the LI-FENCE emitter+runtime scope, so it does not block the gate; the `bb_call.cpp`/`by_name_dispatch.c` references are the in-scope ones if any.)

4. **`pl_*` in `driver/`/`interp/`** (out of the LI-FENCE emitter+runtime scope) — same Prolog ownership; covered by item 1's owner pass.

## Method notes for the next session

- After ANY runtime edit, rebuild BOTH (scrip statically links the runtime; `out/libscrip_rt.so` is m4-only): `rm -f scrip && make -j4 scrip && make libscrip_rt`.
- The repo is VERY active — expect push rejections. For mechanical renames, the robust rebase is: `git fetch … main`, `git reset --hard FETCH_HEAD`, re-run the rename `sed`s via grep-driven file discovery (idempotent; also catches newly-introduced prefixed tokens), rebuild, re-gate, recommit. Used twice this session.
- Push form (token in URL — bare `origin` fails "could not read Username"): `git push https://<TOKEN>@github.com/snobol4ever/SCRIP main`. Push the code repo FIRST, `.github` LAST.
- Gate floor that must stay green every commit: `test_gate_raku_nfa_oracle.sh` 5/5, `test_smoke_raku.sh` (m2 all-PASS), `test_smoke_icon.sh` 12/12/12, `test_smoke_snobol4.sh` m4 7/7; invariants `test_gate_no_vstack.sh` (`g_vstack`=0), `test_gate_no_bb_bin_t.sh`.
