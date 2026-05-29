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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-5 alt.icn LANDED via BB_ALT counter-state dispatch** (Opus 4.7, 2026-05-28, one4all `1a97c0a3`). **Mode-3 canonical-5: 3/5 → 4/5.** `alt.icn` (`every write(1 | 2 | 3)`) closes via authoring the counter-state dispatch slab (Option A from prior handoff) in `bb_alt.cpp` MEDIUM_BINARY + rewriting `flat_drive_alt_icn` from ABORT-stub to functional driver. Architecture: template-first-then-bodies (mirrors `flat_drive_pl_choice`). Driver walks arms via `pBB->α` ω-chain (per `lower_icn_new_Alt`: arm[0]=pBB->α, arm[i+1]=arm[i]->ω) — NOT via `bb_pat_kid` which would read `pBB->counter` as kids-state pointer and crash for Icon BB_ALT. Allocates per-arm α/β labels, queues arm-α targets via `EMIT_PAIR_JMP`, calls `EMIT_PAIR_FILL` (template emits dispatcher), then lays down arm bodies with `emit_label_define_bb(arm_α[i])` + `walk_bb_flat(arm[i], lbl_γ, lbl_ω, arm_β[i])`. Template bytes: α: `movabs rcx,&counter; mov [rcx],0; jmp short dispatch` (19 bytes); β: `movabs rcx,&counter; add [rcx],1; (fall through)` (17 bytes); dispatch: `movabs rcx,&counter; mov rcx,[rcx]` (13 bytes); per arm i: `cmp rcx,i (48 81 F9 + u32 imm32, 7 bytes)` + `je arm_α[i] (0F 84 + u32 rel32, 6 bytes)`; final `jmp lbl_ω` for exhaustion. Uses `&pBB->counter` — same int64 slot mode-2's `bb_exec.c:1720` uses for the arm index. Imm32 form chosen so n>127 works (canonical-5 has n=3 but design is general). For canonical-5 slab is 93 bytes. Edge cases verified: `write(42)` (n=1, no alt at all) and `every write(10|20|30|40|50)` (n=5) both byte-identical mode-2 vs mode-3. Mode-3 4/5 = hello ✅ + add ✅ + every_to ✅ + alt ✅ (NEW). **Gates HOLD:** smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, smoke_snobol4 13/13, smoke_unified_broker 39/14, FACT-RULE 0, icon crosscheck 2/4 (concat / if_expr --run FAILs PRE-EXISTING — verified by `git stash` baseline run on `a21dc32b`, both root-cause to `flat_drive_binop_tree: missing α or β child` unchanged from prior sessions). Files touched: `src/emitter/BB_templates/bb_alt.cpp` (+92/-44) + `src/emitter/emit_bb.c` (+56/-44). Handoff `HANDOFF-2026-05-28-OPUS-IBB-5-ALT-DISPATCH-LANDED.md`. **NEXT:** (1) `full.icn` mode-3 → 5/5: BB_BINOP_GEN dispatch in `bb_call` int_expr predicate + new `flat_drive_binop_gen_tree` driver (cross-product walk of two BB_TO operand sub-trees applying `*`/`>` via `rt_arith`); (2) after canonical-5 5/5: flip `SCRIP_ICN_BB` default per IBB-7 watermark + run full mode-3 corpus sweep. [Prior: **IBB-4 every_to.icn LANDED + BB_ALT plumbing** (Sonnet 4.6, `fac53504`) closed the architectural prerequisite — bb_alt.cpp in Makefile, header decl, emit_core.c BB_ALT split out of bb_limit fall-through, β-define entry added.] |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-NEXT step 2 ✅ + WAM-CP-6 prelude ✅** (Opus 4.7, 2026-05-28, one4all `52f80293`). Two independent surgical changes in `bb_exec.c`. **(A) once/1 intercept** (~10 lines). Extended BB_PL_CALL call/N meta-fallback from `if (carity >= 1 && callee=="call")` to `if ((carity >= 1 && callee=="call") || (carity == 1 && callee=="once"))`. `pl_call_term` commits to one solution via `pl_invoke_var_goal` (no resume), so `once(G) ≡ call(G)` under this dispatch. OR-form preserves call/N (SWI-2d/2e) per prior session's warning. **(B) bb_exec_node stack frame reduction.** Three large stack arrays moved to `GC_MALLOC` heap: `Term *acc[4096]` 32 KB findall, `Term *elems[4096]` 32 KB sort/msort, `int out_idx[4096]` 16 KB sort/msort. Net: ~80 KB removed from function's `-O0` stack frame (was 111 KB measured via gdb, now ~30 KB), ~3× `bb_exec_once` mutual-recursion depth headroom. NOT full WAM-CP-6 LCO (proper non-recursive `bb_exec_once` refactor still pending per Sonnet's analysis handoff). **3 .ref re-baselines in corpus:** test_exception/test_list/test_misc EMPTY → FAIL (honest verdicts now that test bodies execute via once → call). test_string.ref left at EMPTY — suite segfaults mid-execution on a deeper bug. **GATE-SWI: 57/57 EMPTY (dishonest) → 55/57 (96%, honest), m2 + m3 byte-identical.** All other gates byte-identical to `a21dc32b`: GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2/m3 104/107, GATE-4 4/4, BB-honest 128/0, FACT 0, smokes icon/raku/snobol4 all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-STEP2-AND-STACK-REDUX.md`. **Bug surfaced (NOT a regression — confirmed by reverting both changes at HEAD): `bb=0x3` corruption in `pl_node_to_term` during deep pj_rev/3 recursion via user-pred synth dispatch.** gdb at crash: `zc = {args@GC heap, nargs=3, callee="pj_rev", arity=3}` but `zc->args[0]=0x3, [1]=0x61` — bogus values. Theory: `calloc` at `bb_exec.c:3317` and `pl_runtime.c:955` puts callee_env outside libgc reachability; under deep recursion GC may sweep freshly-built compound terms reachable only through callee_env. **NEXT recommended:** (a) **`bb=0x3` corruption fix** — start with one-line calloc→GC_MALLOC experiment in both files; (b) WAM-CP-6 LCO proper (multi-session, bb_exec_once non-recursive); (c) WAM-CP-13 (mode-4 corpus 54/107 long-arc); (d) PL-RT-ASSERTZ. [Prior: **SWI-NEXT step 1 ✅** (`a21dc32b`) TT_VAR-as-goal in lower_pl.c; **SWI-5 ✅** (`6c3d8703`) EMPTY verdict honest baseline; **PL-RT-USER-FROM-SYNTH-2 ✅** (`61187cc7`) rung33_bridge_callN 5/5; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1; **WAM-CP-1/2/3/4/5 ✅, 9/10 partial 🟡** (`5427e12e`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-POS-PATCH-OFFSET ✅** (Opus 4.7, 2026-05-28, one4all `61ae501e`). 2-line fix to `bb_pat_pos.cpp` sites — POS `{9,15,20,21}` → `{10,15,19,20}`, RPOS `{25,31,36,37}` → `{26,31,35,36}`. Patcher convention derived from `bb_emit_asm_result` (emit_str.cpp:70-77): `bin.sites[i]` = first byte of rel32 (for patches) OR byte where label resolves (for defines). Validated against bb_pat_any.cpp's working sites `{17, 72, 86, 90, 100}`. POS prior site #1 was at offset 9 = last byte of `0F 85` opcode, not offset 10 = first byte of rel32; sites #3/#4 shifted by +1 to compensate; site #2 correct only because `E9` is single-byte. The +1 caused patcher to write u32le rel32 starting at offset 9, overwriting the `0F 85` opcode byte → corrupted to `0F 32` (rdmsr) → SIGSEGV on rung 044. Added 23-line documentation comment of byte layout in-file. **Native broad corpus 171→187 (+16), default broad corpus 237→246 (+9), zero regressions.** Native wins: 044/045 (direct), 8 FENCE tests (061/068/102/104/106/107/117/151 — FENCE uses POS for cursor anchoring), 143_pat_regex_quantified_class, 5 drivers (Qize/ShiftReduce/stack/trace/tree). Default wins: 9 drivers (Qize/ShiftReduce/assign/fence/global/match/stack/trace/tree) — confirms some default-mode patterns route through bb_build_brokered → BINARY arm under `--interp` (was silently miscompiling and crashing). Test methodology note: `test_interp_broad_corpus_and_beauty.sh` truncates FAILURES to head -40 — gives false delta signals when FAIL >40; use sed copy with head -300 and explicit INTERP path to compare failure lists. Gates: G1=13/13 default+native, G2=39, G4=246/280, native=187/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. Handoff `HANDOFF-2026-05-28-OPUS-SBL-POS-PATCH-OFFSET.md`. **NEXT:** (a) enable combinator flat-wire in mode-3 (patnd_to_bb_tree path + extend patnd_needs_xlate for combinator roots — bytes ready via SBL-EP-BINARY, label arena landed at `744ae342`); (b) extend `patnd_tree_eligible` for XARBN inside CAT (rung 052 still empty natively post-POS — segfault gone but ARBNO inside anchored concat still fails); (c) SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms using `std::deque<int>` slot pattern from bb_capture.cpp. [Prior: **ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`) 157→160 native; **ARBNO tree-shape foundation 🟡** (`debb8a4e`); **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED** (Opus 4.7 prior).] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-1a landed + SM_BB_INVOKE BINARY stub blocker surfaced 📋** (Opus 4.7, 2026-05-28 follow-up-5, one4all this commit). Restored prior Sonnet 4.6 follow-up-4 edit to `src/emitter/BB_templates/bb_to_by.cpp`: MEDIUM_BINARY yield path swapped from four `r12`-relative writes (18 bytes, requires uninitialised r12 — segv) to `mov rdi,rcx ; movabs rax,&rt_push_int ; call rax` (15 bytes), matching `bb_to.cpp` IBB-3 convention. Added `void rt_push_int(int64_t v);` forward-decl + `<stdint.h>`. Three `bin` offsets recomputed from `(int)b.size()` snapshots so patch sites track automatically. **DISCOVERED BLOCKER:** the edit is unreachable until `SM_BB_INVOKE` MEDIUM_BINARY arm (`src/emitter/SM_templates/sm_bb_switch.cpp:35-36`) is wired up — it is currently a 5-byte no-op stub `E8 00 00 00 00` (`call rel32=0`); the MEDIUM_TEXT arm at lines 38-87 properly inlines the BB graph via `walk_bb_node_str_c(gen)` + γ/ω epilogue with `rt_set_last_ok`, but BINARY does not. Therefore `sm_run_native` reaches SM_BB_INVOKE, executes the no-op `call`, then SM_JUMP_F pops empty vstack → "SM value stack underflow." **Also discovered:** `walk_bb_flat` in `emit_bb.c:981` has `case BB_TO:` but no `case BB_TO_BY:` — falls into `default:` (define β + 2× jmp ω). Both fixes compose cleanly and are needed together to close rk_range_for. **Honest mode-3 re-baseline: 18 PASS / 0 FAIL / 15 CRASH** (rk_stdio39 PASS this session; rk_junctions lex-fails so counts as CRASH-by-exit not FAIL-by-diff in my harness, watermark categorises it as FAIL by output-diff). All gates HOLD: GATE-RK 23/33, GATE-RK4 26/33, smoke raku/prolog/icon 5/5/5, snobol4 13/13, FACT=0, build clean. **NEXT:** M3-RK-NOINTERP-1b — wire SM_BB_INVOKE MEDIUM_BINARY arm (translate the MEDIUM_TEXT reference shape into raw-byte sequence) + add `case BB_TO_BY` to walk_bb_flat; verify on rk_range_for; expect 18→19 PASS. [Prior: opnames cleanup ✅ Sonnet `67a0c196`; M3-RK-NOINTERP-3 ✅ Sonnet `c3476078`.] |
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
