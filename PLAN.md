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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-4 every_to.icn LANDED + BB_ALT plumbing** (Sonnet 4.6, 2026-05-28, one4all `fac53504`). **Mode-3 canonical-5: 2/5 → 3/5.** `every_to.icn` (`every write(1 to 3)`) closes via the prior session's localized one-line fix in `bb_to.cpp` MEDIUM_BINARY: `bin.sites` reordered from `{fail_off+2=64, succ_off+1=84, back_off=19}` (NON-ascending) to ascending `{back_off=19, fail_off+2=64, succ_off+1=84}` with matching label/define-flag reorder. `bb_emit_asm_result`'s ascending-walk patching loop now resolves `arg_β` at the correct slab offset (19) instead of past-end (88); `bb_call` trailer's `jmp arg_β` lands on the BB_TO counter-advance code instead of itself; no more vstack underflow. Output byte-identical to mode-2. **BB_ALT plumbing landed** (clean atomic value, separate from canonical-5 fix): (a) `bb_alt.cpp` added to Makefile sources + recipe — was a source-tree file with NO build artifact; (b) `void bb_alt(BB_t*)` decl added to `bb_templates.h`; (c) `case BB_ALT:` split out of `bb_limit` fall-through in `emit_core.c:563` — was masking the gap by silently routing to `bb_limit`; (d) `bb_alt.cpp` MEDIUM_BINARY bin extended from 2-site `{1,6}` (no β-define) to 3-site `{1,5,6}` with β-define entry mirroring `bb_fail.cpp` shape; (e) `flat_drive_alt_icn` driver + `case BB_ALT:` in `walk_bb_flat`. Driver currently aborts loudly with precise next-step doc — empirically validated that single-arm yield works via chain wiring (alt.icn prints `1` then ends) but EVERY-driven re-pump can't advance arms without runtime state. **Architectural blocker for alt.icn → 4/5:** counter-state dispatch slab needed (matches `bb_exec.c:1720` which uses `bb->counter`). Two options: (A) fold into `bb_alt.cpp` (one template, split-emit pattern with arm-walk between α/dispatch/β sections); (B) new `bb_alt_dispatch.cpp` + driver mints arm labels separately. Option A recommended — ~100-150 lines of x86 bytes in template, reference patterns in `bb_to.cpp` (counter init/inc) and `bb_lit_scalar.cpp` (push convention). **Gates HOLD:** smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, smoke_snobol4 13/13, smoke_unified_broker 39/14, icon crosscheck 2/2 (was 1/3 baseline; `every_to` flipped FAIL→PASS, `if_expr --run` FAIL is pre-existing via `flat_drive_binop_tree: missing α or β child` — verified non-regression by git-stashed baseline run). FACT-RULE 0. Handoff `HANDOFF-2026-05-28-SONNET-IBB-EVERY-TO-LANDED-ALT-PLUMBING.md`. **NEXT:** (1) author counter-state dispatch slab in `bb_alt.cpp` → alt.icn 4/5; (2) BB_BINOP_GEN added to BB_CALL int_expr dispatch + new `flat_drive_binop_gen_tree` → full.icn 5/5; then flip `SCRIP_ICN_BB` default per IBB-7 watermark. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-NEXT step 1 ✅** (Opus 4.7, 2026-05-28, one4all `a21dc32b`). **Diagnostic + partial fix.** `lower_pl_goal` returned NULL for any bare `TT_VAR` because its case-match ladder ended at `if (e->t != TT_FNC || !e->v.sval) return NULL;`. This silently wiped out the body of any user predicate that meta-called one of its own arguments — `foo(G) :- catch(G, _, R)` lowered to an empty BB graph (one RETURN), masquerading as "predicate not found." Affected catch(VAR, .., ..) and findall(_, VAR, _). Fix: 23-line TT_VAR arm in `lower_pl_goal` that synthesizes a single-arg `BB_PL_CALL` with callee="call", piggy-backing on the SWI-2d intercept in `bb_exec.c BB_PL_CALL` handler. Standard Prolog semantics: `?- X.` ≡ `?- call(X).` Bisection via `/tmp/bisect*.pl`: (4) `foo(G) :- catch(G,_,R)` reproduced silent body-wipe; (5) `foo(G) :- call(G)` worked; (6) `foo(G) :- catch(call(G),_,R)` worked → localized to catch lowering / TT_VAR fall-through. SM dump of broken case showed `foo/1` body = bare RETURN. **Step 2 (next session, NOT this commit): once/1 intercept** — `bb_exec.c BB_PL_CALL` has `callee=="call"` intercept (SWI-2d) but no `once` intercept. plunit's `pj_run_tests` uses `once(pj_run_one(...))` heavily; without the once intercept, every test enters pj_run_one and never returns. **Combined step 1 + step 2 unblocks real SWI test execution.** Mechanical fix specified in handoff: change `if (carity >= 1 && callee=="call")` to `if ((carity >= 1 && callee=="call") || (carity == 1 && callee=="once"))`. **Warning to next-session:** my first attempt this session accidentally narrowed `carity >= 1` to `carity == 1`, which would have broken SWI-2d/2e call/N for N>1; reverted to keep gates stable. Correct shape preserves call/N with the OR form. **Bonus diagnostic:** stale `libscrip_rt.so` masked a `GATE-4 m4-choice` false-regression — confirmed `make libscrip_rt` is essential alongside `make scrip` before running GATE-4. Gates byte-identical to predecessor `6c3d8703`: GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 EMPTY (honest; once/1 still blocks plunit), BB-honest 128/0, FACT 0, smokes icon/raku/snobol4 all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-TT-VAR-AS-GOAL.md`. **NEXT options:** (a) **SWI-NEXT step 2** (mechanical, ~5 lines in bb_exec.c — see handoff quickstart; expected to flip ~9 SWI suites from EMPTY → real PASS/FAIL distribution and require .ref re-baseline); (b) WAM-CP-6 LCO (segfault-cluster, needs `bb_exec_once` non-recursive refactor); (c) PL-RT-ASSERTZ (dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc). [Prior: **SWI-5 ✅** (`6c3d8703`/`bafe415`) EMPTY verdict 53/57→57/57 honest baseline; **PL-RT-USER-FROM-SYNTH-2 ✅** (`61187cc7`) rung33_bridge_callN 2/5→5/5; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **ARBNO MEDIUM_BINARY child-gate fix ✅** (Opus 4.7, 2026-05-28, one4all `4471b80d`). 2-line surgical change to `bb_arbno.cpp:19` — outer no-child gate now medium-aware: `MEDIUM_BINARY ? bb_child_fn != NULL : child_lbl && child_lbl[0]`. Root cause exactly as the predecessor handoff predicted — `bb_prepare_capture_arbno` only sets `bb_child_lbl` inside its MEDIUM_TEXT branch, so the BINARY arm hit the 10-byte no-define fallback even when `bb_child_fn` was valid, leaving site=19 (`lbl_β`) unresolved at `bb_emit_end`. The full 259-byte BINARY arm now runs. `bb_capture.cpp` did NOT need the same fix (its BINARY arm already gates on `child_fn` not `child_lbl`; only the TEXT arm guards on `child_lbl`). **Native broad corpus 157→160 (+3), zero regressions.** Newly passing: `W04_arbno_basic`, `W04_arbno_backtrack`, `W04_arbno_zero` (ARBNO-only tests). 052/054 no longer abort at emit time, but now segfault at runtime inside the **POS(0) arm**, not ARBNO — a separate pre-existing bug (rung 044, plain POS+LEN with no ARBNO, also segfaults natively at HEAD). gdb shows POS arm's `0F 85 <rel32>` jne becoming `0F 32 ...` (rdmsr) — looks like a rel32 patch off-by-one writing into the opcode byte. `bb_pat_pos.cpp:17-18` declares sites `{9,15,20,21}` for POS / `{25,31,36,37}` for RPOS, which appear off-by-one from where the rel32 actually starts after `0F 85` (e.g. POS site=9 falls inside the opcode at offset 8-9; rel32 starts at 10). Gates: G1=13/13 default+native, G2=39, G4=237/280, rungs M2=19/M4=14, Prolog/Icon/Raku smokes 5/5/5, FACT=0, audit GATE OK. **NEXT:** (a) **SBL-POS-PATCH-OFFSET** — verify whether bb_pat_pos.cpp sites are correct vs how the patcher resolves them (could be a patcher convention thing, not a sites-list thing); fix opens 044 + all POS/RPOS-anchored native tests including 052/054 (ARBNO+anchors); (b) re-attempt SBL-ARBNO inside combinators (XARBN inside XCAT/XOR via `patnd_to_bb_tree`); (c) the broad-corpus FAIL list still has clusters around SPAN (~10), BREAKX (~6), FENCE (~6) — pick one. [Prior: **ARBNO tree-shape foundation 🟡** (`debb8a4e`); **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED** (Opus 4.7 prior).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **opnames cleanup + M3-RK-NOINTERP-1 deep-dive 📋** (Sonnet, 2026-05-28 follow-up-3, one4all uncommitted-edit). Tiny edit landed: `sm_prog.c:252` opnames[] slot mislabel `"SM_UNUSED_8"` → `"SM_NAMED_CALL"` (option (a) from prior handoff). M3-RK-NOINTERP-1 architectural deep-dive: did NOT land. Surfaced ABI mismatch — mode-3 native uses SM rt-vstack (rt_push_int@PLT) whereas existing BB MEDIUM_BINARY arms (bb_to_by/bb_upto/bb_suspend/bb_iterate/bb_icn_to) write yielded values to **r12 as brokered-slab vstack pointer**. XA_FLAT_PROLOGUE / bb_broker / sm_run_native none initialise r12. Splicing existing BB BINARY arms into the SM byte stream of mode-3 yields segfault-or-corruption + the observed "libscrip_rt: SM value stack underflow." Recommended path: **(a) mode-3-ABI branch in each generator BB template using `rt_push_int@PLT`** (matches existing MEDIUM_TEXT lines, e.g. bb_to_by.cpp:89-90); split as 1a (bb_to_by — closes rk_range_for / rk_for_array family), 1b (bb_iterate), 1c (bb_upto / bb_suspend / bb_seq). Each generator-template per session minimises blast radius. Mode-2 baseline re-measured this session: 23/33 HOLD. Mode-3 native re-measured: **17/33 PASS, 2/33 FAIL, 14/33 CRASH** (one delta from prior 18/33 watermark: rk_stdio39 PASS → FAIL — stderr-ordering, unrelated to Cluster 1). Smokes all HOLD (5/5 raku/prolog/icon, 13/13 snobol4). FACT-RULE grep 0. Build clean. **NEXT recommended:** M3-RK-NOINTERP-1a — bb_to_by.cpp MEDIUM_BINARY new mode-3-ABI branch emitting `mov rdi, rcx; movabs rax, &rt_push_int; call rax` instead of r12-stack writes. Closes rk_range_for first. [Prior: **M3-RK-NOINTERP-3 ✅** (one4all `c3476078`) Cluster 2 closed via SM_NAMED_CALL Pass 3 in sm_run_native.] |
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
