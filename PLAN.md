# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find goal in table below.
3. Read `RULES.md` in full.
4. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
6. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
7. Open Goal file. Open that repo's REPO file.
8. Run Goal file's `## Session Setup` scripts.
9. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-4 WIP + housekeeping** (Opus 4.7, 2026-05-28, one4all `057bc824`). **Mode-3 canonical-5: 2/5 unchanged** (hello.icn ✅, add.icn ✅; every_to.icn / alt.icn / full.icn still failing but failure surfaces shifted forward — every_to now reaches the emit chain and prints `1` before underflow, alt.icn no-ops, full.icn aborts on BB_BINOP_GEN). **Housekeeping (per Lon directives):** (a) renamed `bb_icn_to.cpp` → `bb_to.cpp` plus fn/header decl + Makefile + stale comments — BB_*/SM_* opcodes and templates are language-independent; (b) deleted redundant `bb_icn_stub.cpp` (was no-op identical to `bb_stub.cpp`; one caller `emit_core.c:619` BB_SEQ_GEN now routes to `bb_stub`); (c) removed `BB_ALTERNATE` opcode — verified zero `BB_node_alloc(*, BB_ALTERNATE)` call sites, case body in `bb_exec.c:1862` was unreachable. Cleanup touches `BB.h`, `scrip_ir.c`, `bb_exec.c` (case + 2 macros + 2 predicates), `lower_icn.c` (2 predicates), `emit_core.c`, `bb_binop_gen.cpp`, `emit_per_kind_audit.c`. Enum-value shift: every BB_op_t after BB_CONJ (16) is now one lower; nothing in source compares against raw ints, only diagnostic dumps. **IBB-4 in-flight pieces (all landed in template/driver code):** `flat_drive_every` (ival=0, β=NULL case), BB_EVERY arm wired (was abort), BB_CALL arg0 shape-dispatch widened to BB_TO/BB_ALT, bb_call.cpp int_expr trailer β-stub jmps to driver-queued β-target (was hardcoded lbl_ω), `flat_drive_call_intexpr` queues `(define=lbl_β, jmp=arg_β)` so call.β chains into arg.β for re-pump cascade, `bb_every.cpp` MEDIUM_BINARY pair-driven arm (was abort), `bb_to.cpp` MEDIUM_BINARY yield rewritten from r12-push to `rt_push_int` call (r12 not init'd by XA_FLAT_PROLOGUE; matches `bb_lit_scalar` BB_LIT_I convention). **Localized one-line blocker:** `bb_to.cpp` MEDIUM_BINARY `bin.sites` is `{fail_off+2=64, succ_off+1=84, back_off=19}` — NON-ascending. `bb_emit_asm_result` patches assume ascending order; the late `back_off` DEFINE fires with `bb_emit_pos == 88` (past end of BB_TO bytes), so `arg_β` resolves to wrong slab address (= position of `arg_done` immediately after BB_TO), and the trailer's `jmp arg_β` lands on itself → second pop without intervening push → underflow. Fix: reorder bin entries to ascending site order. **Gates:** smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, smoke_snobol4 13/13, smoke_unified_broker 39/14, Icon mode-2 corpus PASS=200 FAIL=47 XFAIL=36 TOTAL=283 unchanged, FACT 0. Handoff `HANDOFF-2026-05-28-OPUS-IBB-RENAME-AND-FLAT-EVERY-WIP.md`. **NEXT:** (1) bin-reorder fix in `bb_to.cpp` → expect every_to.icn 3/5; (2) `case BB_ALT` in walk_bb_flat + real generator MEDIUM_BINARY arm in `bb_alt.cpp` → expect alt.icn 4/5; (3) BB_BINOP_GEN added to BB_CALL int_expr dispatch + new `flat_drive_binop_gen_tree` → expect full.icn 5/5; then flip `SCRIP_ICN_BB` default per IBB-7 watermark. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-5 ✅** (Opus 4.7, 2026-05-28, corpus + one4all). **GATE-SWI: 53/57 (92%) → 57/57 (100%) honest baseline.** Three-way verdict `EMPTY`/`PASS`/`FAIL` in `pj_suite_verdict/3` driven by new per-suite counter `pj_tc` (incremented from inside `pj_inc_{pass,fail,skip}`, NOT on enqueue — `pj_run_one` can silently fail when scrip's catch/once misbehaves on a malformed goal, and counting on enqueue would falsely promote zero-test suites to PASS via `TC>0,SF=0`). Pre-SWI-5 binary `(SF=:=0 -> PASS ; FAIL)` printed PASS whenever no failure was recorded, INCLUDING when zero test bodies ran — that was the entire mechanism behind the 53/57 baseline (all 9 SWI suites had `% 0 passed, 0 failed, 0 skipped` confirming nothing executed). The 4 expected-FAIL .ref entries (`float_compare`, `max_integer_size`, `catch`, `variant`) also showed PASS, registering as `MISS FAIL`. Post-SWI-5: all 9 suites correctly emit EMPTY; all 57 .ref lines rewritten from PASS/FAIL → EMPTY; honest 57/57. Verdict written as **three clauses with cuts**, not nested `( -> ; -> ; )`, because scrip mode-2 interp drops the middle branch of nested ITE chains and jumps straight to the final else (verified on `/tmp/probe_ite.pl`: with X=1,Y=0, `(X=:=0->a; Y=:=0->b; c)` printed `c` instead of `b`; plunit.pl header has flagged "No -> operator" since v3). Touched: `corpus/programs/prolog/plunit.pl` v3→v4, 9 `corpus/programs/prolog/swi_tests/test_*.ref` files, `one4all/scripts/util_swi_{match,report}.py` accept EMPTY prefix, `one4all/scripts/test_prolog_swi_suite.sh` grep widened to EMPTY. Gates byte-identical otherwise: GATE-1 5/5, GATE-2 132/0, GATE-3 m2 104/107, GATE-4 4/4, BB-honest 128/0, FACT 0, smokes icon/raku/snobol4 all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-5-EMPTY-VERDICT.md`. **Bonus diagnostic:** confirmed nested `(C1->T1;C2->T2;E)` is broken in scrip mode-2 — control jumps to final E instead of trying C2; possible WAM-CP-9 step-B (committed-ITE node) candidate. **NEXT options:** (a) **SWI-NEXT** — fix `pj_run_one` silent failure (`pj_do_succeed` clauses both fail opaquely on simple goals; trace catch/once + cut interaction in `bb_exec.c BB_CATCH`/`BB_CUT`) — this unblocks ALL real SWI test execution; (b) WAM-CP-6 LCO (segfault-cluster, needs `bb_exec_once` non-recursive refactor); (c) PL-RT-ASSERTZ (dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc). [Prior: **PL-RT-USER-FROM-SYNTH-2 ✅** (`61187cc7`) rung33_bridge_callN 2/5→5/5; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **SWI-2-fold ✅** (`43933846`) 0/57 → 53/57; **SWI-1a ✅** (`86abe166`); **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-3 ✅** (Sonnet, 2026-05-28 follow-up-2, one4all `c3476078`): mode-3 native Raku 11/33 → 18/33 (+7, full Cluster 2 closed). Root: `sm_named_call.cpp:35` MEDIUM_BINARY arm emits `movabs rax, 0; call rax` with comment "patched by linker," but `sm_run_native` has no linker pass for `SM_NAMED_CALL` absolute targets (only patches `SM_JUMP*` rel32). Prior-session triage missed this because `src/lower/sm_prog.c:252` opnames table mislabels the enum slot as `"SM_UNUSED_8"` — every test that "uses UNUSED_8" actually uses NAMED_CALL. Re-counted: all 7 Cluster 2 tests use it (3-18 calls each); 0 PASSing tests use it. Fix: 35-line Pass 3 in `sm_run_native` runs between `memcpy(code, buf, buf_n)` and `seg_seal(SEG_CODE)` (SEG_CODE still RW at that point), finds matching `SM_LABEL` by name, writes `(uintptr_t)(code + instr_off[j])` into the 8-byte placeholder at instr offset +19. No template files touched, FACT-RULE intact. Newly passing: `rk_class26`, `rk_combinator`, `rk_given`, `rk_interp`, `rk_stdio39`, `rk_subs`, `rk_try_catch25`. `rk_given18` still crashes — it has both NAMED_CALL (now fixed) and BB_INVOKE (Cluster 1, still broken). **Gates HOLD:** GATE-RK 23/33, GATE-RK4 26/33, smokes 5/5 raku/prolog/icon, 13/13 snobol4, FACT-RULE grep 0. Diagnosis correction documented in `MODE3-DISPATCH-GAP.md` ADDENDUM 2. **NEXT options:** (a) rename `"SM_UNUSED_8"` → `"SM_NAMED_CALL"` in `sm_prog.c:252` (tiny, low-risk, prevents future miscount); (b) **M3-RK-NOINTERP-1** for Cluster 1 — `SM_BB_INVOKE` MEDIUM_BINARY arm is a 5-byte no-op stub at `sm_bb_switch.cpp:35-36`; needs `walk_bb_node` driven through binary sink + BB-internal label rel32 patching (1-2 sessions, 8 tests); (c) resolve Lon Q9-Q12 for RK-BB-4 junctions. [Prior: **RK-CLASS ✅** (one4all `baf73030`) rk_class26 modes 2+4 PASS; Mode-3 honest baseline established (`SCRIP_M3_NATIVE=1`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **ARBNO MEDIUM_BINARY child-gate fix ✅** (Opus 4.7, 2026-05-28, one4all `4471b80d`). 2-line surgical change to `bb_arbno.cpp:19` — outer no-child gate now medium-aware: `MEDIUM_BINARY ? bb_child_fn != NULL : child_lbl && child_lbl[0]`. Root cause exactly as the predecessor handoff predicted — `bb_prepare_capture_arbno` only sets `bb_child_lbl` inside its MEDIUM_TEXT branch, so the BINARY arm hit the 10-byte no-define fallback even when `bb_child_fn` was valid, leaving site=19 (`lbl_β`) unresolved at `bb_emit_end`. The full 259-byte BINARY arm now runs. `bb_capture.cpp` did NOT need the same fix (its BINARY arm already gates on `child_fn` not `child_lbl`; only the TEXT arm guards on `child_lbl`). **Native broad corpus 157→160 (+3), zero regressions.** Newly passing: `W04_arbno_basic`, `W04_arbno_backtrack`, `W04_arbno_zero` (ARBNO-only tests). 052/054 no longer abort at emit time, but now segfault at runtime inside the **POS(0) arm**, not ARBNO — a separate pre-existing bug (rung 044, plain POS+LEN with no ARBNO, also segfaults natively at HEAD). gdb shows POS arm's `0F 85 <rel32>` jne becoming `0F 32 ...` (rdmsr) — looks like a rel32 patch off-by-one writing into the opcode byte. `bb_pat_pos.cpp:17-18` declares sites `{9,15,20,21}` for POS / `{25,31,36,37}` for RPOS, which appear off-by-one from where the rel32 actually starts after `0F 85` (e.g. POS site=9 falls inside the opcode at offset 8-9; rel32 starts at 10). Gates: G1=13/13 default+native, G2=39, G4=237/280, rungs M2=19/M4=14, Prolog/Icon/Raku smokes 5/5/5, FACT=0, audit GATE OK. **NEXT:** (a) **SBL-POS-PATCH-OFFSET** — verify whether bb_pat_pos.cpp sites are correct vs how the patcher resolves them (could be a patcher convention thing, not a sites-list thing); fix opens 044 + all POS/RPOS-anchored native tests including 052/054 (ARBNO+anchors); (b) re-attempt SBL-ARBNO inside combinators (XARBN inside XCAT/XOR via `patnd_to_bb_tree`); (c) the broad-corpus FAIL list still has clusters around SPAN (~10), BREAKX (~6), FENCE (~6) — pick one. [Prior: **ARBNO tree-shape foundation 🟡** (`debb8a4e`); **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED** (Opus 4.7 prior).] |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Mode-4 SN4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | M4SN-5 or M4SN-6. 250/280 ✅. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **SN4 JVM** | `GOAL-SN4-JVM-EMIT.md` | SJ4-JVM-4 done. Beauty.sno halts at Parse Error. smoke 13/13. |
| **SN4 .NET** | `GOAL-SN4-NET-EMIT.md` | SN4-NET-5d — SM_PAT_* wiring. smoke_net 9/9, broker 23/49. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
