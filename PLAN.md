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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **PL-RT-USER-FROM-SYNTH partial 🟡** (Opus 4.7, 2026-05-28, one4all `953f981d`): replaced the `[NO-AST] interp_eval stub` at `pl_runtime.c:931` with real BB-graph dispatch via `pl_bb_lookup` + `bb_exec_once`, mirroring BB_PL_CALL's post-intercept logic. Old stub used `pl_pred_table_lookup` to retrieve the clause AST and would have walked it directly — RULES.md forbids AST walking in modes 2/3/4. New path goes BB-table only. **Two fixes that did land:** (1) `pl_bb_lookup` key format — registration stores `e->key = "name/arity"` as the *name* field, so lookup must pass the full slash-form (`"add/3"`), not the bare name; (2) RULES compliance — zero AST walking. **Partial:** works for user predicates with all-input-mode args (verified: `greet3(A,B,C):-write(A),write(B),write(C),nl.` via `call(G,hi,ho,hum)` prints `hihohum`). FAILS for output-mode vars — even the simplest non-arithmetic case `bind3(A,B,C):-C=wow.` via `call(G,x,y,R)` returns `DT_FAIL=99` from `bb_exec_once`. The Term* round trip (caller BB_PL_VAR → `pl_node_to_term` → `tenv[slot]` → `pl_unified_term_from_expr` → `unify` with `term_new_var(ai)`) doesn't connect the body's local-var read to the caller's R cell. rung33_bridge_callN unchanged at 2/5. **NEXT recommended (Approach B):** **PL-RT-USER-FROM-SYNTH-2** — redesign `pl_call_term_n` to dispatch *directly* through `pl_bb_lookup` + `bb_exec_once` with a Term*-built callee env, bypassing `pl_term_to_synth_expr` entirely. Mirrors BB_PL_CALL exactly and avoids the synthesis-layer fidelity loss. The synthesis round-trip exists for builtin dispatch; user-pred dispatch shouldn't go through it at all. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-PL-RT-USER-FROM-SYNTH-PARTIAL.md`. Gates byte-identical: smoke 5/5, G2=132/0 (5 ORACLE_MISS), G3=104/107, GATE-SWI=53/57 (92%), BB-honest=128/0, FACT=0. **NEXT options:** (a) **PL-RT-USER-FROM-SYNTH-2** (RECOMMENDED — Approach B above, closes rung33 02/04/05); (b) SWI-5 EMPTY verdict; (c) PL-RT-ASSERTZ; (d) WAM-CP-13; (e) WAM-CP-6 LCO. [Prior: **SWI-2e ✅** (`3de01576`) call/N for N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **SWI-2-fold ✅** (`43933846`) 0/57 → 53/57; **SWI-1a ✅** (`86abe166`) directive whitelist; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-3 ✅** (Sonnet, 2026-05-28 follow-up-2, one4all `c3476078`): mode-3 native Raku 11/33 → 18/33 (+7, full Cluster 2 closed). Root: `sm_named_call.cpp:35` MEDIUM_BINARY arm emits `movabs rax, 0; call rax` with comment "patched by linker," but `sm_run_native` has no linker pass for `SM_NAMED_CALL` absolute targets (only patches `SM_JUMP*` rel32). Prior-session triage missed this because `src/lower/sm_prog.c:252` opnames table mislabels the enum slot as `"SM_UNUSED_8"` — every test that "uses UNUSED_8" actually uses NAMED_CALL. Re-counted: all 7 Cluster 2 tests use it (3-18 calls each); 0 PASSing tests use it. Fix: 35-line Pass 3 in `sm_run_native` runs between `memcpy(code, buf, buf_n)` and `seg_seal(SEG_CODE)` (SEG_CODE still RW at that point), finds matching `SM_LABEL` by name, writes `(uintptr_t)(code + instr_off[j])` into the 8-byte placeholder at instr offset +19. No template files touched, FACT-RULE intact. Newly passing: `rk_class26`, `rk_combinator`, `rk_given`, `rk_interp`, `rk_stdio39`, `rk_subs`, `rk_try_catch25`. `rk_given18` still crashes — it has both NAMED_CALL (now fixed) and BB_INVOKE (Cluster 1, still broken). **Gates HOLD:** GATE-RK 23/33, GATE-RK4 26/33, smokes 5/5 raku/prolog/icon, 13/13 snobol4, FACT-RULE grep 0. Diagnosis correction documented in `MODE3-DISPATCH-GAP.md` ADDENDUM 2. **NEXT options:** (a) rename `"SM_UNUSED_8"` → `"SM_NAMED_CALL"` in `sm_prog.c:252` (tiny, low-risk, prevents future miscount); (b) **M3-RK-NOINTERP-1** for Cluster 1 — `SM_BB_INVOKE` MEDIUM_BINARY arm is a 5-byte no-op stub at `sm_bb_switch.cpp:35-36`; needs `walk_bb_node` driven through binary sink + BB-internal label rel32 patching (1-2 sessions, 8 tests); (c) resolve Lon Q9-Q12 for RK-BB-4 junctions. [Prior: **RK-CLASS ✅** (one4all `baf73030`) rk_class26 modes 2+4 PASS; Mode-3 honest baseline established (`SCRIP_M3_NATIVE=1`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 combinator flat-wire LANDED ✅** (Opus 4.7, 2026-05-28, one4all `10f97d29`). Three commits this session: `1e9ae6c6` (bb_seq n==0 BINARY arm walks EP-pair — audit FAKE-JMP→REAL); `a4b62c1f` (combinator flat-wire — new `patnd_to_bb_tree` in lower_pat_dcg.c translates XCAT/XOR/XFNCE roots over atoms into emit_sm-shaped trees with `bb_pat_kids_state_t` kid arrays via `nd->counter`, so `flat_drive_alt/cat/fence` finds populated kids via `bb_pat_nkids/bb_pat_kid`. New `patnd_tree_eligible` + `patnd_is_combinator_root` in stmt_exec.c gate the route; LIVE-mode only, BROKERED untouched); `10f97d29` (capture-wrap extension — XNME/XFNME wrapping eligible subtrees translate to `BB_PAT_ASSIGN_COND/IMM` with inner as single kid, routes through existing `bb_build_brokered` child-build via `pre_build_children`). Root cause confirmed: PATND_t kind enum (XCAT=19) collides with BB_op_t (BB_EVERY=19) on raw cast — explains 055_pat_concat_seq's "BB_EVERY needs flat_drive_every" abort. With label arena (`744ae342`) in place, no dangling-stack-label regression from prior attempts. **Canonical wins:** `('cat'\|'dog') . V` over `'dog'` → `dog` native ✓ ; `LEN(2) . A LEN(2) . B LEN(2) . C` over `'abcdef'` → `ab cd ef` native ✓. **Gates:** G1=13/13 default+native, G2=38/53, G3=162/280, G4=237/280, **native broad 142→157/280 (+15)**, rung suite M2=19/M4=14, Prolog/Raku/Icon smokes 5/5. Audit was OK at my push time; concurrent upstream commit `6393c743` (IBB bb_call/bb_seq n>0) introduced a new FAKE-JMP in `bb_lit_scalar.cpp` — separate from this work, owned by ICON-BB. Handoff `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-COMBINATOR-FLATWIRE.md`. **NEXT:** ARBNO inside combinators (rung 052/054 still fail native — extend XARBN handling in `build_patnd_tree`, likely delegate to `build_patnd` since its inner-block shape already works); then 053_pat_alt_commit / 056_pat_star_deref / 057_pat_fail_builtin investigation; eventually flip the `SCRIP_M3_NATIVE=1` default. |
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
