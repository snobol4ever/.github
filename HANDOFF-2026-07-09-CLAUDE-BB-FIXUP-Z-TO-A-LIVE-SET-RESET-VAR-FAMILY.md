# HANDOFF — BB-FIXUP Z-to-A, LAP 2 (LIVE-SET), 21st session (Claude Sonnet 5, 2026-07-09)

## Lon directives at open
1. **Cursor RESET to Z-end** — fresh lap start.
2. **THIS PASS scope = bb_*.cpp files IN THE MAKEFILE ONLY.** The Makefile carries an explicit compile list (no wildcard), so the live set is well-defined: `grep -oE 'templates/bb_[a-z0-9_]+\.cpp' Makefile` → **116 live** of 163 on disk; **47 dormant skipped** this pass.
3. Credential supplied at end of session; pushes batched (recorded deviation from law-3 push-per-file).

## Session state
- Templates now live FLAT at `src/templates/` (the goal file's `src/emitter/BB_templates/` paths are stale). Dispatch = direct `bb_emit_x86(bb_xxx())` calls in `src/emitter/emit.cpp`; `bb_prepare`/`emit_bb.c` no longer exist as such.
- Opening rank: 163 files / 106 dirty / GRAND **1070**. Dirty∩live queue = **73**, Z→A from `bb_var_ref.cpp`.
- Closing rank: 99 dirty / GRAND **1038** (−32, all seven files git-attributed, zero growth elsewhere).

## Landed (SCRIP hashes; each ONE commit, audit rc=0, battery at floors, cursor advanced in matching .github commit)
| File | Δ | Hash | Notes |
|---|---|---|---|
| bb_var_ref | 3→0 | e0cae6aa | 5 returns→2; gva/local arms merged via **lea-operand ternary** (FRQ/RDQ both `const char *`); A/B comment-only ×2 (queens gva, mu local — both LIVE) |
| bb_var_global | 1→0 | 06877c09 | full-body ternary in canonical CV8 fence; NV arm verbatim, DORMANT at HEAD |
| bb_var_frame_ref | 5→0 | 7a6e4763 | **ORPHAN** (decl in bb_templates.h, zero dispatch sites); lang_blind purge; frame_reach locals→lambda params; audit's returns counter excludes only `return`-lines carrying a lambda-intro on the SAME line — fold accordingly |
| bb_var_frame | 7→0 | 0a297ded | same; ⚠ **frame_reach now duplicated** across the two frame files — CV2-letter vs audit 2-static tolerance vs CV7 no-pseudo-op: **LON RULING WANTED** |
| bb_var | 3→0 | dde0a615 | THREE dead flag-gated arms **DELETED** (constant-false flag; arms duplicated bb_var_global, which owns globals at the IR_VAR dispatch fork emit.cpp:722-727); frame arm LIVE deal.icn ×11; A/B ZERO ×4 |
| bb_unop | 9→0 | 7cce5c33 | resolver+uop()+enum deleted; comparisons inlined verbatim ×8 sites (11 counted returns→2); CV1 `"IR_UNOP_TEST lv"`→bare `IR_NULLTEST_VAR` (its true kind); both families LIVE |
| bb_to | 4→0 | 55124d06 | ⛔ **CV7 RO-QUAD-SEAL DECOMPOSITION PRECEDENT**: `x86_ro_seal_q(n,v)` → `x86("def",L(n)) + x86(".quad",(uint64_t)v)`. Byte-identical BOTH mediums from encoder internals: `deflabel_id` = `Drec(BASE+n)` / `.Lx<uid>_<n>:` and `.quad` tag-2 = `Lrec(u64le)` / ` .quad <n>` — exactly the seal's halves, same id space `ROQ(n)` reads (hence loop label `L(10)` dodging slots 0/1). Int arm A/B ZERO ×5; real arm DORMANT at HEAD |

Artifact regens per RULES step 4 (codegen touched): SCRIP `88445f79` (feature .s), corpus `907acfa6` (bench, 16 files) + `6c77fe7d` (demo) + icon-bench script (9 updated / 3 pre-existing compile-err flagged, untouched).

## Findings (durable)
1. **`g_gvar_flat_chain` is a DEAD KNOB.** Defined `= 0` (emit.cpp:432), header-declared (emit.h:252), **no setter anywhere in src/**. Every template read is constant-false. Six live templates still reference it: bb_assign_frame_ref, bb_assign_frame, bb_keyword_icon, bb_binop_gvar_relop, bb_binop_gvar_concat, bb_call — same purge applies at their ring stops. emit.cpp:662-665 CALL_ROUTE_GVAR_USERPROC/BYNAME routes equally dead (NOT touched — outside cursor files; flag for DEAD-CODE-SWEEP / Lon).
2. **Committed corpus .s can be stale vs HEAD** — two pockets found: snobol4 demos (treebank*/claws5 FATAL at lower, GZ#5 subset "tree kind 42") and icon rung19 real-toby (compiles, but bb_to's real arm no longer fires). Probe-hunting via committed artifacts must re-verify firing at HEAD (compile fresh, grep the comment) before trusting.
3. **Probe inventory built this session** (in /home/claude/probes, disposable): queens.icn (gva ×17, unop-test), deal.icn (bb_var frame arm ×11, unop ×3), mu.pl (var_ref local ×105), pv_sno.sno / pv_icn.icn (synthetic minimal gva), pv_toreal.icn (int to-loop). SNOBOL4 synthetic syntax traps: statements need leading whitespace (col-1 = label), `END` uppercase; Icon: no `;` after `end`.
4. **Session floors certified at open on the untouched tree**: pat suite **19 PASS + 2 pre-existing zb fails** (zb_act_arbno_in_define, zb_arena_collection_grow — identical in all three modes; ZB-ACT family, inherited); vstack **1** (better than recorded 3); icon xcheck **PASS=4 FAIL=0** (better than recorded FAIL=4); bin_t 0; handencoded 0; pat_reg strict HARD-0. Enforced NO-NEW-FAILS all session; held.
5. Audit mechanics: returns counter = `return`-lines minus lines that ALSO carry `[&](...){` — fold an inner return onto its lambda-intro line to exclude both.

## NEXT (Z→A, live set)
**bb_to_by.cpp** (TOTAL=2 returns_plus, 89 lines — bb_to sibling; check for the same seal shape). Then bb_swap_var → bb_suspend → bb_succeed → bb_subscript → bb_subject → bb_section → scan family. Dirty∩live remainder = **66**. Recompute the live set each session from the Makefile.

Cursor: `# CURSOR: bb_to.cpp` (last completed; resume procedure computes next strictly-before).
