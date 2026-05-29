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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-6 full.icn LANDED — canonical-5 mode-3 5/5** (Sonnet 4.6, 2026-05-28, one4all `3aa200cd`). `BB_BINOP_GEN` flat-wired cross-product odometer in `bb_binop_gen.cpp` MEDIUM_BINARY + `flat_drive_binop_gen_tree` driver in `emit_bb.c`. Vstack-transience problem solved via per-node cache slots (`pBB->counter` = lhs cached int, `pBB->value.i` = rhs cached int) using new `rt_pop_store_i64`/`rt_push_stored_i64` helpers. Template emits store→restore→apply slab keyed off five EMIT_PAIR entries (lhs_store def, rhs_store def, outer_γ, rhs_β retry, β-define). Arithmetic ops (MUL/ADD/etc): store/restore/rt_arith/jmp-γ. Relop ops (GT/LT/etc): store/restore/rt_acomp/rt_last_ok/test/jne-γ/rt_pop_void/jmp-rhs_β. `every write((1 to 2)*(3 to 4))` = `3\n4\n6\n8\n` byte-identical m2 vs m3. `every write(5>((1 to 2)*(3 to 4)))` = `3\n4\n` byte-identical. FACT=0. Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 39/14. **NEXT:** (1) flip `SCRIP_ICN_BB` from env-gate to default per IBB-7 watermark — drop env check, make `lower_icn_bb` the unconditional Icon lower path, run full mode-3 corpus sweep; (2) IBB-23 suspend at top-level (proc-as-generator re-entry); (3) mode-4 (`--compile`) for canonical-5. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-NEXT step 1 ✅** (Opus 4.7, 2026-05-28, one4all `a21dc32b`). **Diagnostic + partial fix.** `lower_pl_goal` returned NULL for any bare `TT_VAR` because its case-match ladder ended at `if (e->t != TT_FNC || !e->v.sval) return NULL;`. This silently wiped out the body of any user predicate that meta-called one of its own arguments — `foo(G) :- catch(G, _, R)` lowered to an empty BB graph (one RETURN), masquerading as "predicate not found." Affected catch(VAR, .., ..) and findall(_, VAR, _). Fix: 23-line TT_VAR arm in `lower_pl_goal` that synthesizes a single-arg `BB_PL_CALL` with callee="call", piggy-backing on the SWI-2d intercept in `bb_exec.c BB_PL_CALL` handler. Standard Prolog semantics: `?- X.` ≡ `?- call(X).` Bisection via `/tmp/bisect*.pl`: (4) `foo(G) :- catch(G,_,R)` reproduced silent body-wipe; (5) `foo(G) :- call(G)` worked; (6) `foo(G) :- catch(call(G),_,R)` worked → localized to catch lowering / TT_VAR fall-through. SM dump of broken case showed `foo/1` body = bare RETURN. **Step 2 (next session, NOT this commit): once/1 intercept** — `bb_exec.c BB_PL_CALL` has `callee=="call"` intercept (SWI-2d) but no `once` intercept. plunit's `pj_run_tests` uses `once(pj_run_one(...))` heavily; without the once intercept, every test enters pj_run_one and never returns. **Combined step 1 + step 2 unblocks real SWI test execution.** Mechanical fix specified in handoff: change `if (carity >= 1 && callee=="call")` to `if ((carity >= 1 && callee=="call") || (carity == 1 && callee=="once"))`. **Warning to next-session:** my first attempt this session accidentally narrowed `carity >= 1` to `carity == 1`, which would have broken SWI-2d/2e call/N for N>1; reverted to keep gates stable. Correct shape preserves call/N with the OR form. **Bonus diagnostic:** stale `libscrip_rt.so` masked a `GATE-4 m4-choice` false-regression — confirmed `make libscrip_rt` is essential alongside `make scrip` before running GATE-4. Gates byte-identical to predecessor `6c3d8703`: GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 EMPTY (honest; once/1 still blocks plunit), BB-honest 128/0, FACT 0, smokes icon/raku/snobol4 all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-TT-VAR-AS-GOAL.md`. **NEXT options:** (a) **SWI-NEXT step 2** (mechanical, ~5 lines in bb_exec.c — see handoff quickstart; expected to flip ~9 SWI suites from EMPTY → real PASS/FAIL distribution and require .ref re-baseline); (b) WAM-CP-6 LCO (segfault-cluster, needs `bb_exec_once` non-recursive refactor); (c) PL-RT-ASSERTZ (dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc). [Prior: **SWI-5 ✅** (`6c3d8703`/`bafe415`) EMPTY verdict 53/57→57/57 honest baseline; **PL-RT-USER-FROM-SYNTH-2 ✅** (`61187cc7`) rung33_bridge_callN 2/5→5/5; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
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
