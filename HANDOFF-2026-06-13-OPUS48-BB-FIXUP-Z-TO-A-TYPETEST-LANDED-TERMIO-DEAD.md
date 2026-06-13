# HANDOFF — 2026-06-13 (Opus 4.8, 9th session) — GOAL-BB-FIXUP-Z-to-A

## STATE (verified at handoff)
- **SCRIP @ `d884849`** (committed + **pushed** to origin/main; clean rebase over concurrent `2831781`). `git log origin/main --oneline -1` confirms `d884849`.
- **CURSOR: `bb_resolve.cpp`** (tracker `# CURSOR:` line — unchanged; HELD, still dirty at 25 violations).
- SCRIP source tree CLEAN and matches pushed HEAD. `.github` updated this turn (watermark + this doc).
- All landed changes behavior-neutral.
- **Pre-existing reds (NOT introduced, do not chase):** rebus `hello` ROW-DRIFT (smoke 5/6, on-hold per PLAN); `util_template_purity_audit.sh` rc=1 = single `bb_call_write_slot.cpp` fprintf.

## WHAT LANDED (SCRIP d884849, behavior-neutral)
`bb_type_test_str(IR_t*, const char*, const std::string&)` → parameterless **`std::string bb_type_test()`**, mirroring `bb_succ_plus`/`bb_retract_throw`. **audit 58 → 0 CLEAN.**
- Dropped `pBB`/`fn`/`hdr` params + the `_str` suffix (**CV9**); dropped all `ir_call_arg`/`IR_LIT` graph access (**CV10**).
- Collapsed the divergent `MEDIUM_BINARY` raw-byte arm + `MEDIUM_TEXT` arm into ONE both-medium `x86()`-driven path (RULES both-medium + no-raw-bytes absolutes).
- Reads from prep: `_.op_sval`/`_.op_sval_lbl` (fn + its strtab label), `_.op_parts_tag[0]`/`_.op_parts_ival[0]`/`_.op_parts_str[0]`/`_.op_parts_lbl[0]` (scalar arg triple), `(IR_t*)(intptr_t)_.op_parts_ival[8]` (arg node ptr for `emit_build_compound_term`).
- Touched exactly 3 files: `BB_templates/bb_type_test.cpp` (rewrite), `BB_templates/bb_common.h` (decl `std::string bb_type_test();`), `BB_templates/bb_resolve.cpp` (bdisp call site `bb_type_test()`).
- `bb_resolve.cpp` **26 → 25** (cv9 8→7). No stray `bb_type_test_str` references remain (`grep -rn` → 0).

### The 8th-session's 4 reconciliations — resolved toward canonical/both-medium
- (a) builder = `emit_build_compound_term` (NOT `emit_term_from_node_bin`).
- (b) stack = `sub rsp, 16` / `add rsp, 16`.
- (c) arg coverage = BOTH `IR_STRUCT` and `IR_ARITH` route through the term path (`1+2` is compound `+(1,2)` — the semantically correct classification; this was the binary arm's coverage).
- (d) tail = keep the `def β` (matches `bb_succ_plus`/`bb_retract_throw`).

## PRIMARY FINDING — overturns the carried-forward risk framing
The 8th-session handoff treated `bb_type_test` as a risky semantic merge ("silent mode-3/mode-4 struct-arg regression"). **It is not — the EMIT path is empirically DEAD.**
- Verified by in-guard `fprintf(stderr,"[TT-EMIT...")` instrumentation (now reverted): **zero fires** across `test/prolog/*.pl` and all GZ-declining shapes (cut / catch / `\+`) in BOTH mode 3 (`--run`) and mode 4 (`--compile`).
- Cause: `IR_DET_TYPE_TEST` → `bb_det_type_test` totally shadows it. The GZ rewrite (`src/driver/scrip.c:1624-1652`) slots EVERY arg shape (LOGICVAR direct; everything else via a synthesized `CELL_UNIFY`) into `IR_DET_TYPE_TEST`. GZ-declined clauses **abort** (rc=134) before reaching `bb_type_test`.
- ∴ the four (a)-(d) divergences are between two UNREACHABLE code paths; unification is behavior-neutral by the strongest "no firing corpus → C2-by-construction" standard.
- Proven byte-identical baseline↔mine via **git-stash A/B** on `tt_bare`/`tt_struct`/`tt_ite`/`tt_conj`. The mode-3 `foo`/`f(a)` leading-prefix DIFFER on `tt_bare`/`tt_struct` is **PRE-EXISTING** (present at HEAD with my change stashed) — unrelated to type-test, NOT mine, noted-not-chased per rule 5.

## FINDING GENERALIZES — `bb_term_io` is ALSO DEAD (next file, now de-risked)
Same one-probe method (`[TIO-FIRE]` instrumentation, now reverted):
- `format/1` AND `format/2` (incl. list & var args — probes `format("hello~n",[])`, `format("~w and ~w~n",[a,b])`, `format("val=~w~n",[X])` all give m2=m3, rc=0, **zero fires**) route through `IR_DET_FORMAT` → `bb_det_format`.
- `queens.pl` + `sentences.pl` (the ONLY corpus `format` users) abort/fail before any `bb_term_io` emit.
- `numbervars` / `term_to_atom` / `term_string` = **0 corpus usage**.
- ∴ the whole `bb_resolve` resolver family is very likely **DEAD-PATH HYGIENE**: the bdisp arms cannot be *deleted* (the fallback exists structurally — 8th-session finding stands), but they do not *fire* in practice. Converting them is low-risk both-medium hygiene, NOT the high-risk per-builtin semantic work prior handoffs feared. **Confirm each remaining family member with the same one-probe method before converting.**

## NEXT — `bb_term_io` conversion (DEAD ∴ low-risk; same mechanical pattern as bb_type_test)
File handles `numbervars/3`, `term_to_atom`/`term_string/2`, `format/1`, `format/2` (NOT `write`/`writeq` — those are `bb_det_write`/`bb_io`). Currently 62 violations, 7 statics, divergent `MEDIUM_BINARY`/`MEDIUM_TEXT` arms.
1. Write parameterless `std::string bb_term_io()`; own `strcmp` on `_.op_sval`.
2. Per builtin, collapse the two medium arms into one both-medium path:
   - term builds via `emit_build_compound_term((IR_t*)(intptr_t)_.op_parts_ival[8+j])` for arg `j` (prep delivers node ptrs at `ival[8]`/`[9]`/`[10]`; scalar triples at `tag`/`ival`/`str`/`lbl[0..3]`). **VERIFY first** that the IR_BUILTIN prep (`emit_bb.c:1135-1192`) populates `op_parts_str[]`/`op_parts_lbl[]` for the compound/atom args these builtins read (the generic arg loop covers j=0..2; the lbl loop covers j=0..3).
   - fn-ptr call form `x86("call","rt_X",(uint64_t)(uintptr_t)(void*)rt_X)` — drop every `@PLT` string.
   - tails one-`x86()`-per-line; keep `def β`.
3. Collapse the 7 `static` helpers (`btio_lbl`, `btio_bin_ports`, `btio_txt_tail`, `btio_bin_*`, `btio_txt_*`) — inline or reduce to ≤2 statics (audit `helper_count` allows 2).
4. `bb_common.h` decl `std::string bb_term_io();` + `bb_resolve.cpp` bdisp call `bb_term_io()` → `bb_resolve` cv9 7→6.
5. Build + gates. byte_identity is **vacuous** for this box (doesn't fire), so the proof is: audit rc=0 + the standard battery green + a `[TIO-FIRE]`-style re-confirmation it still doesn't fire. Then continue Z→A: `bb_term_inspect`(97) → `bb_list` → `bb_is_cmp`(110) → `bb_findall`(10, HEAVY).

When `bdisp` empties of `_str` calls, `bb_resolve` itself goes parameterless (drop `bdisp(IR_t*)`/`bb_resolve(IR_t*)` sigs + the raw-byte `bytes("\xE9")` MEDIUM_BINARY fallback + the 12-return chain) → reaches rc=0; advance cursor then.

## STATE NOTES
- The **local `scrip` binary** carries stale `bb_term_io` `[TIO-FIRE]` instrumentation (the last rebuild compiled it). `make scrip` clears it. The SOURCE tree is clean and matches pushed `d884849`; binaries regenerate at session setup anyway.
- ENV: tree needs `libgc-dev` + `libgmp-dev` (both in `scripts/install_system_packages.sh` — run setup; an un-run-setup env fails at `gc/gc.h`).

## PROCESS NOTE
Context gauge remains unobservable to the agent; stopped at ~70% (estimate) rather than half-start the multi-builtin `bb_term_io` conversion at the brake. Per the goal's repeated norm, an unverifiable half-state is worse than a clean handoff with an execute-ready recipe.
