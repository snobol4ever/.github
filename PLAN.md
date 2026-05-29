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
| **ICON-BB** | `GOAL-ICON-BB.md` | **IBB-6 full.icn LANDED — canonical-5 mode-3 5/5** (Sonnet 4.6, 2026-05-28, one4all `3aa200cd`). `BB_BINOP_GEN` flat-wired cross-product odometer in `bb_binop_gen.cpp` MEDIUM_BINARY + `flat_drive_binop_gen_tree` driver in `emit_bb.c`. Vstack-transience problem solved via per-node cache slots (`pBB->counter` = lhs cached int, `pBB->value.i` = rhs cached int) using new `rt_pop_store_i64`/`rt_push_stored_i64` helpers. Template emits store→restore→apply slab keyed off five EMIT_PAIR entries. `every write((1 to 2)*(3 to 4))` = `3\n4\n6\n8\n` byte-identical m2 vs m3. `every write(5>((1 to 2)*(3 to 4)))` = `3\n4\n` byte-identical. FACT=0. Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 39/14. **Mode-3 corpus sweep result (249 testable programs): 20 PASS / 23 FAIL / 206 ABORT. Dominant blocker: bb_call unsupported shape (181 cases).** Handoff `HANDOFF-2026-05-28-SONNET-ICON-BB-IBB6-FULL-ICN.md`. **NEXT:** Add `rt_pop_write_any_nl` + `write(BB_VAR)` support (~30 cases): (1) `rt_pop_write_any_nl` in rt.c/rt.h; (2) add `BB_VAR` to `is_write_intexpr` in bb_call.cpp; (3) flat-wire `BB_VAR` arg0 via `rt_nv_get` call + any-write trailer; (4) case BB_VAR in walk_bb_flat. After that: relop in if-condition context (16 cases), every-with-do-body (4 cases). |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **SWI-NEXT step 1 ✅** (Opus 4.7, 2026-05-28, one4all `a21dc32b`). **Diagnostic + partial fix.** `lower_pl_goal` returned NULL for any bare `TT_VAR` because its case-match ladder ended at `if (e->t != TT_FNC || !e->v.sval) return NULL;`. This silently wiped out the body of any user predicate that meta-called one of its own arguments — `foo(G) :- catch(G, _, R)` lowered to an empty BB graph (one RETURN), masquerading as "predicate not found." Affected catch(VAR, .., ..) and findall(_, VAR, _). Fix: 23-line TT_VAR arm in `lower_pl_goal` that synthesizes a single-arg `BB_PL_CALL` with callee="call", piggy-backing on the SWI-2d intercept in `bb_exec.c BB_PL_CALL` handler. Standard Prolog semantics: `?- X.` ≡ `?- call(X).` Bisection via `/tmp/bisect*.pl`: (4) `foo(G) :- catch(G,_,R)` reproduced silent body-wipe; (5) `foo(G) :- call(G)` worked; (6) `foo(G) :- catch(call(G),_,R)` worked → localized to catch lowering / TT_VAR fall-through. SM dump of broken case showed `foo/1` body = bare RETURN. **Step 2 (next session, NOT this commit): once/1 intercept** — `bb_exec.c BB_PL_CALL` has `callee=="call"` intercept (SWI-2d) but no `once` intercept. plunit's `pj_run_tests` uses `once(pj_run_one(...))` heavily; without the once intercept, every test enters pj_run_one and never returns. **Combined step 1 + step 2 unblocks real SWI test execution.** Mechanical fix specified in handoff: change `if (carity >= 1 && callee=="call")` to `if ((carity >= 1 && callee=="call") || (carity == 1 && callee=="once"))`. **Warning to next-session:** my first attempt this session accidentally narrowed `carity >= 1` to `carity == 1`, which would have broken SWI-2d/2e call/N for N>1; reverted to keep gates stable. Correct shape preserves call/N with the OR form. **Bonus diagnostic:** stale `libscrip_rt.so` masked a `GATE-4 m4-choice` false-regression — confirmed `make libscrip_rt` is essential alongside `make scrip` before running GATE-4. Gates byte-identical to predecessor `6c3d8703`: GATE-1 5/5, GATE-2 132/0 (5 ORACLE_MISS), GATE-3 m2 104/107, GATE-4 4/4, GATE-SWI 57/57 EMPTY (honest; once/1 still blocks plunit), BB-honest 128/0, FACT 0, smokes icon/raku/snobol4 all green. Handoff `HANDOFF-2026-05-28-OPUS-PROLOG-BB-SWI-NEXT-TT-VAR-AS-GOAL.md`. **NEXT options:** (a) **SWI-NEXT step 2** (mechanical, ~5 lines in bb_exec.c — see handoff quickstart; expected to flip ~9 SWI suites from EMPTY → real PASS/FAIL distribution and require .ref re-baseline); (b) WAM-CP-6 LCO (segfault-cluster, needs `bb_exec_once` non-recursive refactor); (c) PL-RT-ASSERTZ (dynamic clause support); (d) WAM-CP-13 (full mode-4 corpus 54/107 long-arc). [Prior: **SWI-5 ✅** (`6c3d8703`/`bafe415`) EMPTY verdict 53/57→57/57 honest baseline; **PL-RT-USER-FROM-SYNTH-2 ✅** (`61187cc7`) rung33_bridge_callN 2/5→5/5; **SWI-2e ✅** (`3de01576`) call/N N>1; **SWI-2d ✅** (`d805b0fe`) call/1 fallback; **SWI-2c ✅** (`a88f1e68`) plunit fold revival; **WAM-CP-1/2/3/4/5 ✅. WAM-CP-9/10 partial 🟡** (`5427e12e`).] |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-SPAN-ARB-ESCAPE-FIX ✅** (Opus 4.7, 2026-05-28, one4all this commit). Mechanical escape-sequence fix to `bb_pat_span.cpp` and `bb_pat_arb.cpp` MEDIUM_BINARY arms — every `bytes(N, "...")` literal used double-backslash escapes (`"\\x48\\xB9"`) where working templates use single (`"\x48\xB9"`). `"\\x48\\xB9"` in C is 8 chars `\ x 4 8 \ x B 9`; `bytes(2, ...)` returned `5C 78` (literal backslash + 'x') instead of `48 B9` (movabs rcx prefix) → every SPAN slab byte-corrupt → SIGSEGV in every native SPAN run. `gdb x/40bx` showed `5C 78 90 33 DA …` where `48 B9 <z_slot ptr>` belonged. Audit's REAL classification fooled because `bin.sites.push_back` activity is substantive. bb_pat_arb has the same shape, same bug. Fix: `\\x` → `\x` in MEDIUM_BINARY lambda of both files (no site/offset changes — original sites were correct for the *intended* layout). **Native broad corpus 187→195 (+8), default broad corpus 246→250 (+4), mode-4 compile 175→178 (+3), ZERO regressions.** Newly passing native: `041_pat_span`, `W05_span` (direct), `063/064/065/066_pat_fence_fn_*` (FENCE uses SPAN internally — same multiplier effect as POS-PATCH-OFFSET's FENCE chain), `test_string`, `wordcount`. Gates: G1=13/13 default+native, G2=39, G3=178/280, G4=250/280, native=195/280, rungs M2=19/M4=15, Prolog/Raku/Icon smokes 5/5/5, FACT=0, audit GATE OK. **Sibling bug, NOT fixed:** bb_arbno.cpp:23, bb_binop_gen.cpp:120, bb_pl_alt/_call/_choice, bb_to.cpp:65 each contain 2-jmp/3-jmp placeholder patterns `bytes(1,"\\xE9")+u32le(0)+…` (BOMB-style fallthrough stubs likely never reached; no known crash, but prophylactic cleanup next session). Files: `src/emitter/BB_templates/bb_pat_span.cpp` (+45/-45 escape replacements), `src/emitter/BB_templates/bb_pat_arb.cpp` (+16/-16). Handoff `HANDOFF-2026-05-28-OPUS-SBL-SPAN-ARB-ESCAPE-FIX.md`. **NEXT:** (a) enable combinator flat-wire in mode-3 (patnd_to_bb_tree path is now live in stmt_exec.c, rungs 050/055 verified passing — broader corpus probably needs `patnd_tree_eligible` extension for nested combinators); (b) prophylactic `\\x`→`\x` cleanup in the 7 BOMB-stub sites; (c) extend `patnd_tree_eligible` for XARBN inside CAT (rung 052/054 still empty native — POS+SPAN segfaults gone, but anchored ARBNO-in-CAT still doesn't match). [Prior: **SBL-POS-PATCH-OFFSET ✅** (`61ae501e`) `bb_pat_pos.cpp` sites realigned to rel32-start convention; **ARBNO MEDIUM_BINARY child-gate fix ✅** (`4471b80d`); **M3-NATIVE-4 combinator flat-wire LANDED ✅** (`10f97d29`); **SBL-EP-BINARY ✅** (`1bc53211`); **bb_capture BINARY arm FIXED**.] |
| **Raku BB** | `GOAL-RAKU-BB.md` | **M3-RK-NOINTERP-1b LANDED ✅** (Opus 4.7, 2026-05-28, one4all `48ca4e21`). **Mode-3 native 18→19 PASS / 14→13 CRASH** (rk_range_for CRASH→PASS). SM_BB_INVOKE MEDIUM_BINARY arm wired from 5-byte no-op stub to full scratch-buffer-flush implementation: saves outer `bb_emit_buf` / `bb_emit_pos` / `bb_emit_size` / `bb_emit_overflow` / `bb_patch_count` / `bb_patch_list` / **`g_emit_sink`** state, allocates 4KB heap scratch + per-sid 1-byte malloc'd entry-flag, emits pre-amble entry-flag dispatch (`movabs rax,&flag ; cmp byte[rax],0 ; je fresh ; jmp lβ ; fresh: mov [rax],1`), calls `walk_bb_node(gen, NULL)` so the BB template (bb_to_by.cpp) emits via MEDIUM_BINARY into our scratch with γ/ω/β patches in `bb_patch_list`, emits γ post-amble (`mov edi,1 ; movabs rax,&rt_set_last_ok ; call rax ; jmp done`) which resolves γ patches in-place, emits ω post-amble with flag-reset + `rt_set_last_ok(0)`, defines done, calls `bb_emit_end()` to verify all patches resolved, restores outer state, returns the bytes as `std::string` for the SM wrapper's `emit_text_n`. **Critical sink save/restore:** `walk_bb_node` line 517 calls `emit_io_set_sink(NULL)` which zeroes `g_emit_sink` — without saving+restoring (via new `emit_io_get_sink()` accessor in `emit_io.{c,h}`), every subsequent `emit_text_n` in `sm_run_native` after the first SM_BB_INVOKE silently drops bytes; was the empty-output failure mode of the first wiring attempt. **Companion fixes:** (a) `case BB_TO_BY: FILL(...)` added to `walk_bb_flat` in `emit_bb.c` — was falling through to `default:` which emitted `define β ; jmp ω ; jmp ω`. (b) Parallel ascending-sites bug in `bb_to_by.cpp:142` — reordered `bin.sites` from non-ascending `{fail_off+2, succ_off+1, back_off}` to ascending `{back_off, fail_off+2, succ_off+1}` matching the canonical-5 fix in `bb_to.cpp` per the every_to.icn fix (bb_emit_asm_result's patch loop walks sites with strictly-advancing pos). **rk_range_for output byte-identical to .expected**. All other gates HOLD byte-for-byte: GATE-RK 23/33 mode-2, GATE-RK4 26/33 mode-4, smoke raku/prolog/icon 5/5/5, snobol4 13/13, FACT-RULE 0, build clean. Handoff `HANDOFF-2026-05-28-OPUS-RAKU-BB-M3-NOINTERP-1b-LANDED.md`. **NEXT:** **M3-RK-NOINTERP-1c (bb_iterate.cpp r12→rt_push_int)** — closes rk_for_array{,_simple,_underscore} + rk_map_grep_sort24 (4 tests, biggest impact). Same surgery as 1a (mirror bb_to.cpp / bb_to_by.cpp). Then 1d (bb_upto: rk_gather, rk_given18) and 1e (bb_suspend/bb_seq). Each is now a ~10-30 line BB-template-local fix — the architectural blocker is gone. [Prior: **M3-RK-NOINTERP-1a ✅** Sonnet 4.6 (`55d03444`) bb_to_by.cpp r12→rt_push_int landed but unreachable; **opnames cleanup ✅** Sonnet `67a0c196`; **M3-RK-NOINTERP-3 ✅** Sonnet `c3476078`.] |
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
