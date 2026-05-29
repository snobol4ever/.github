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
| **ICON-BB** | `GOAL-ICON-BB.md` | **ADD MODE-3 PASS** (Opus 4.7, 2026-05-28, one4all `e612d519`). **Mode-3 canonical-5: 1/5 → 2/5.** `add.icn` (`write(1+2)`) now prints `3` via flat-wired x86 in `bb_pool` slab. Value-passing convention chosen: **vstack via runtime helpers** (`rt_push_int` / `rt_arith` / `rt_pop_write_int_nl`) — option 2 from the predecessor handoff. Option 1 (r12 ring) rejected because `XA_FLAT_PROLOGUE` does not initialize r12 and SNOBOL4's existing r12 pushes scribble on caller-saved register territory (see `bb_to_by.cpp:87` segfault warning). Three new flat-drive pieces wired: `bb_lit_scalar` MEDIUM_BINARY BB_LIT_I arm (32 bytes: movabs rdi,ival; movabs rax,&rt_push_int; call rax; jmp γ; β: jmp ω), new template `bb_binop.cpp` (32-byte rt_arith apply for arithmetic ICN_BINOP_ADD/SUB/MUL/DIV/MOD/EXP), and `bb_call.cpp` extended with `write(int_expr)` trailer shape (22 bytes: movabs rax,&rt_pop_write_int_nl; call rax; jmp γ; β: jmp ω). Driver-level: `flat_drive_binop_tree` walks lhs (α) then rhs (β), defines mid-labels, then EMIT_PAIR_FILL drives the apply; `flat_drive_call_intexpr` walks the arg sub-graph, defines arg_done, then EMIT_PAIR_FILL drives the call trailer. `emit_core.c` peels BB_BINOP out of the BB_VAR/ASSIGN/AUGOP group and routes to `bb_binop`. `walk_bb_flat` BB_CALL arm now shape-dispatches by a0->t (BINOP/LIT_I → flat_drive_call_intexpr; LIT_S → direct FILL). Gates: mode-2 corpus PASS=200 FAIL=47 XFAIL=36 TOTAL=283 unchanged; smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5; `--dump-sm count=0` for add.icn under SCRIP_ICN_BB; FACT rule clean. **Byte-offset bug found and fixed mid-session:** first pass copied patch offsets 27/32/33 from the bb_call strlit layout (37 bytes, has extra `BE+u32le slen`); the shorter 32-byte layouts of BB_LIT_I/bb_binop need 23/27/28 and the 22-byte bb_call trailer needs 13/17/18. Caught by `Illegal instruction` on first add.icn run; corrected by careful byte-by-byte recount. **Remaining canonical-5 abort sites:** `every_to.icn`, `alt.icn`, `full.icn` → `walk_bb_flat: BB_EVERY needs flat_drive_every`. **NEXT:** `flat_drive_every` (body.γ → body.β re-pump; body.ω → outer γ) plus generator-leaf templates BB_TO and BB_ALTERNATE under the same vstack convention. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PL-RT-USER-FROM-SYNTH-2 ✅** (Opus 4.7, 2026-05-28, one4all `61187cc7`): closes the partial fix from `953f981d`. **rung33_bridge_callN: 2/5 → 5/5** (mode-2 AND mode-3 transparent). Three latent type-domain bugs in `src/runtime/interp/pl_runtime.c`, all in the synthesized-tree path used by `pl_invoke_var_goal` (BB_PL_CALL call/N meta-fallback for user predicates), all inert until output-mode vars and integer literals reached the synth path simultaneously: (1) `pl_term_to_synth_expr` L789 `case TT_VAR:` (tree_e=5) matched `t->tag == 5` = `TermTag::TERM_REF` (never seen post-deref), so caller's `TERM_VAR` (=1) fell through to default → `pl_synth_new(TT_FNC)` v.sval=NULL → downstream `pl_unified_term_from_expr` read functor "f" → body's `unify(atom_f, int_7)` failed → DT_FAIL=99. Fixed to `case TERM_VAR:`. (2) Same function L791 `pl_synth_new(TERM_VAR)` (=1) produced tree_t with `t = TT_ILIT`; fixed to `pl_synth_new(TT_VAR)`. (3) `pl_synth_free` L770 freed `e->v.sval` for every node unconditionally — with bugs (1)+(2) fixed, real TT_VAR/TT_ILIT/TT_FLIT leaves exist with union-overlapped `v.ival`/`v.dval` set, free()'d as pointers → segfault on free(0x3) for literal 3 in `add(3,4,R)`. Gated to TT_FNC/TT_QLIT only. **Why latent under partial:** all-input cases had no TERM_VAR caller terms (bug 1 no-op) and only strdup'd atom leaves (bug 3 freed valid pointers); output-var case surfaced all three at once. **Approach B not needed**: synth round-trip works fine once leaves are typed correctly. Rebased onto concurrent upstream `debb8a4e` (SBL M3-NATIVE-4 ARBNO). Gates byte-identical to `953f981d`: GATE-1 5/5, G2=132/0 (5 ORACLE_MISS), G3 mode-2 104/107, GATE-SWI=53/57 (92%), GATE-4 4/4, BB-honest=128/0, FACT=0, sibling smokes all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-PL-RT-USER-FROM-SYNTH-2.md`. **NEXT options:** (a) WAM-CP-6 LCO (segfault-cluster fix per Sonnet 4.6 analysis — needs `bb_exec_once` non-recursive refactor); (b) SWI-5 EMPTY verdict (close the 4 SWI failures); (c) PL-RT-ASSERTZ (dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc). [Prior: **PL-RT-USER-FROM-SYNTH partial 🟡** (`953f981d`) BB-graph dispatch in interp_exec_pl_builtin's user-call branch — superseded by this ✅; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **SWI-2-fold ✅** (`43933846`) 0/57 → 53/57; **SWI-1a ✅** (`86abe166`); **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-3 ✅** (Sonnet, 2026-05-28 follow-up-2, one4all `c3476078`): mode-3 native Raku 11/33 → 18/33 (+7, full Cluster 2 closed). Root: `sm_named_call.cpp:35` MEDIUM_BINARY arm emits `movabs rax, 0; call rax` with comment "patched by linker," but `sm_run_native` has no linker pass for `SM_NAMED_CALL` absolute targets (only patches `SM_JUMP*` rel32). Prior-session triage missed this because `src/lower/sm_prog.c:252` opnames table mislabels the enum slot as `"SM_UNUSED_8"` — every test that "uses UNUSED_8" actually uses NAMED_CALL. Re-counted: all 7 Cluster 2 tests use it (3-18 calls each); 0 PASSing tests use it. Fix: 35-line Pass 3 in `sm_run_native` runs between `memcpy(code, buf, buf_n)` and `seg_seal(SEG_CODE)` (SEG_CODE still RW at that point), finds matching `SM_LABEL` by name, writes `(uintptr_t)(code + instr_off[j])` into the 8-byte placeholder at instr offset +19. No template files touched, FACT-RULE intact. Newly passing: `rk_class26`, `rk_combinator`, `rk_given`, `rk_interp`, `rk_stdio39`, `rk_subs`, `rk_try_catch25`. `rk_given18` still crashes — it has both NAMED_CALL (now fixed) and BB_INVOKE (Cluster 1, still broken). **Gates HOLD:** GATE-RK 23/33, GATE-RK4 26/33, smokes 5/5 raku/prolog/icon, 13/13 snobol4, FACT-RULE grep 0. Diagnosis correction documented in `MODE3-DISPATCH-GAP.md` ADDENDUM 2. **NEXT options:** (a) rename `"SM_UNUSED_8"` → `"SM_NAMED_CALL"` in `sm_prog.c:252` (tiny, low-risk, prevents future miscount); (b) **M3-RK-NOINTERP-1** for Cluster 1 — `SM_BB_INVOKE` MEDIUM_BINARY arm is a 5-byte no-op stub at `sm_bb_switch.cpp:35-36`; needs `walk_bb_node` driven through binary sink + BB-internal label rel32 patching (1-2 sessions, 8 tests); (c) resolve Lon Q9-Q12 for RK-BB-4 junctions. [Prior: **RK-CLASS ✅** (one4all `baf73030`) rk_class26 modes 2+4 PASS; Mode-3 honest baseline established (`SCRIP_M3_NATIVE=1`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **ARBNO tree-shape foundation 🟡** (Opus 4.7, 2026-05-28, one4all `debb8a4e`). Three files, baseline-neutral: `bb_arbno_state_t` extended with layout-compat `kids/nkids` at front; `build_patnd_tree` gets `case XARBN:` building inner via tree path; `patnd_tree_eligible`/`patnd_is_combinator_root` accept XARBN. 052/054 no longer segfault under `SCRIP_M3_NATIVE=1`; now abort at `bb_emit_end: site=19 label='pat_brok_β'`. **Diagnosis complete:** nested brokered build of ARBNO node hits `bb_arbno.cpp`'s `!child_lbl` fallback (line 19) because `g_emit.bb_child_lbl` is set only in `MEDIUM_TEXT` branch of `bb_prepare_capture_arbno`. The 10-byte fallback omits β-define; prologue's β-patch goes unresolved. **Fix:** in `bb_arbno.cpp` (likely also `bb_capture.cpp`), gate on `MEDIUM_BINARY ? bb_child_fn != NULL : child_lbl && child_lbl[0]`. Gates byte-identical to prior HEAD `10f97d29`: G1=13/13 default+native, G2=38, G3=162/82 (PLAN's 175 figure is stale upstream drift), G4=237/43, native broad 157/280, rungs M2=19/M4=14. Handoff `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-ARBNO-TREE-FOUNDATION.md`. [Prior: **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED** (Opus 4.7 prior).] |
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
