# HANDOFF — 2026-06-13 (Opus 4.8, 8th session) — GOAL-BB-FIXUP-Z-to-A

## STATE (verified at handoff)
- **SCRIP @ `eb29686`** (pushed to origin/main) · **.github** updated this turn (watermark + this doc)
- **CURSOR: `bb_resolve.cpp`** (tracker `# CURSOR:` line — the ONE source of truth; HELD, not advanced)
- Baseline `scrip` builds green (after the env fix below). All landed changes behavior-neutral.
- **Pre-existing reds (NOT introduced, do not chase):** rebus `hello` ROW-DRIFT (on-hold per PLAN); `util_template_purity_audit.sh` rc=1 = single `bb_call_write_slot.cpp` fprintf.

## ENV NOTE (do this at session setup)
The tree did NOT build on arrival: `fatal error: gc/gc.h: No such file or directory`. Fix:
`sudo apt-get install -y libgc-dev libgmp-dev` (both are already in `scripts/install_system_packages.sh` — this was an un-run-setup environment, not a code regression). After that `make -j4 scrip` is green.

## WHAT THIS SESSION DID (SCRIP eb29686, behavior-neutral)
1. **Unblocked the build** (env fix above).
2. **`op_sval_lbl` prep field** — added to `sm_emit_t` (`src/emitter/emit_globals.h`, after `op_sval`) and populated in the IR_BUILTIN block of `bb_prepare` (`src/emitter/emit_bb.c`, ~line 1178): `strtab_label(IR_LIT(nd).sval)` into a static buf. Dead-write (no reader yet); it is the **one** field the pending `bb_type_test` conversion needs that prep wasn't already delivering. Compile-verified.
3. **Closed the audit hole** (`scripts/audit_bb_fixup_file.sh`) — added **CV9** and **CV10** counters, folded into `total`/rc:
   - CV9: `grep -cE 'bb_[a-z0-9_]*_str\b'` (the `bb_` prefix is REQUIRED — bare `_str\b` falsely matches the `op_parts_str` field) **+** `grep -cE 'std::string[^;]*IR_t *\*'` (signature-level `IR_t*` params; does NOT match the blessed `(IR_t*)…` cast or local decls).
   - CV10: `grep -cE 'ir_call_arg\(|ir_pair_arg\(|ir_operand|IR_LIT *\('`.
   - VERIFIED: clean exemplars (succ_plus, retract_throw, var_frame, var_frame_ref, alt, atom) stay **rc=0**. `bb_resolve` now reads **26** (cv9=8, cv10=0 — its term-build was relocated out in session 7, so its only remaining sin is the parameterized dispatch); `bb_type_test` reads **69** (cv9=2, cv10=9).
   - **CAVEAT:** CV9/CV10 may re-flag OTHER files previously called "clean" that still take params / use the graph — intended (they were never conformant). **Re-run `scripts/audit_bb_fixup_rank.sh` next session for the true dirty set.**

## KEY FINDINGS (correct the carried-forward plan — do NOT re-chase the old hypothesis)
1. **The IR_DET_*-shadowed `bdisp` arms are NOT dead.** The GZ rewrite that builds `IR_DET_*` is `pl_gz_*` body-goal lowering in `src/driver/scrip.c` (IR_DET_SUCC_PLUS@1347, IR_DET_TYPE_TEST@1616). It is **opportunistic-with-fallback**: it `return 0`s on arg shapes it can't handle (e.g. `if (ax->op != IR_LIT_I) return 0;`@1339), and on decline the original `IR_BUILTIN` survives to `bb_resolve → bdisp → bb_type_test_str`/`bb_succ_plus`. So the "SHARP FIRST CHECK / delete a dead arm" quick win from prior handoffs is **dead**. An arm can be retired only after its `IR_DET_*` path is made **TOTAL** (handles every shape the arm catches) — per-builtin semantic work, Prolog-regression risk. This is why bb_resolve's 12-return chain is genuinely multi-session.
2. **`bb_type_test` is not a clean both-medium merge** like `bb_retract_throw` was — its binary/text arms diverge in four behavior-relevant ways (see NEXT).

## NEXT — the focused `bb_type_test` conversion (now mechanical except 4 choices)
Prep already delivers (for a unary type-test): `_.op_parts_tag[0]`=k0(a0->op), `_.op_parts_ival[0]`=i0, `_.op_parts_str[0]`/`_.op_parts_lbl[0]`=s0+label, `_.op_parts_ival[8]`=(intptr_t)a0 (arg node ptr), `_.op_sval`=fn, **`_.op_sval_lbl`**=fn's strtab label (NEW this session).

Write parameterless `std::string bb_type_test()` mirroring `bb_succ_plus`/`bb_retract_throw`: own `strcmp` on `_.op_sval`; fn rip-lea via `x86("lea","rdi","[rip + __]",(uint64_t)(uintptr_t)_.op_sval,_.op_sval_lbl)`; struct path via `emit_build_compound_term((IR_t*)(intptr_t)_.op_parts_ival[8])`. **PRESERVE BOTH call forms** (behavior-neutrality demands it): `rt_type_test(k0,i0,s0)` for scalar literal args, `rt_type_test_term(build(a0))` for struct args — both via the fn-ptr `x86("call",sym,fp)` form (no `@PLT` string, no hand-rolled bytes).

**Reconcile these 4 binary/text divergences (document each choice):**
- (a) builder: binary `emit_term_from_node_bin(a0)` vs text `emit_build_compound_term(a0)` — pick the canonical one (text uses `emit_build_compound_term`).
- (b) stack: binary `sub rsp,8` vs text `sub rsp,16`.
- (c) arg coverage: binary handles `IR_STRUCT||IR_ARITH`; text only `IR_STRUCT` (IR_ARITH → text scalar path).
- (d) tail: binary struct arm has NO `def β`; text HAS it.

Then `bb_common.h` decl `bb_type_test_str(IR_t*,const char*,const std::string&)` → `bb_type_test()`, and `bb_resolve.cpp` bdisp call site. **Build + FULL gates** (prolog xcheck var/atom/number/struct/arith with m2=m3=m4; icon xcheck; byte_identity; bin_t; vstack; sno_pat_reg; purity). A light smoke is INSUFFICIENT — a wrong reconciliation choice is a silent mode-3/mode-4 struct-arg regression.

**Then continue Z→A among the resolver family:** `bb_term_io`(62) → `bb_term_inspect`(97) → `bb_list` → `bb_is_cmp`(110) → `bb_findall`(10, HEAVY — both-medium unify + fs-state digest). When `bdisp` empties, `bb_resolve` dissolves to parameterless and reaches rc=0; advance cursor then.

## PROCESS NOTE
Context gauge remains unobservable to the agent; this session estimated ~70% at the brake and ~75% at handoff (guesses). Handed off at the brake rather than start the `bb_type_test` reconciliation, which is too large to finish+verify in remaining budget without risking an unverifiable half-state.
