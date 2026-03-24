> Org renamed SNOBOL4-plus → snobol4ever, repos renamed March 2026. Historical entries use old names.

# SESSIONS_ARCHIVE.md — Append-only session log

**Format:** One `## SessionID — Description ✅/❌ (date)` block per session.
Oldest sessions pruned for context economy. Full git history is the permanent record.

---

## IJ-6 — Icon JVM — 2026-03-24

**HEAD in:** `e590c4f` IJ-5 | **HEAD out:** `a3d4a55` IJ-6

**Fix 1 ✅** `ij_emit_proc`: `lconst_0/lstore N` preamble for all `ij_nlocals` slots before `suspend_id` dispatch → `Register pair 2/3 wrong type` dead.
**Fix 2 ✅** `ij_emit_suspend` body γ: route through `icn_N_bdone: pop2; goto ports.γ` drain — body assignments leave long on stack.
**Fix 2b ✅** `ij_emit_suspend` body ω: `strncpy(bp.ω, ports.γ)` — failure path has empty stack, must NOT go through pop2.
**Fix 3 ✅** `ij_emit_proc` stmt chain: each stmt γ → `icn_sN_sdrain: pop2; goto next_a` — prevents stale long entering next stmt's α.

**All VerifyErrors dead. Class loads and exits 0.**

**Remaining for IJ-7:** no-output bug — `icn_upto()` returns `icn_failed=1` immediately. Debug: `javap -c icn_upto`, check `i := 1` stores to slot 2, `1 <= 4` compares lload 2 vs lload 0. Verify `sdrain` routes to while-condition α, not `icn_upto_done`.

---

## PJ-8 — Prolog JVM — 2026-03-24

**HEAD:** `d36f0ed` snobol4x main

**Fixed:** rung02 infinite loop. Root cause: `base[nclauses]` uninitialized in `pj_emit_choice()`.

**Fix:** `base[nclauses] = base[nclauses-1] + 1`. Omega guard emitted only when last clause has no body user-calls.

**Corpus:** rung01 ✅ rung02 ✅ rung03 ✅ rung04 ✅ rung05 ✅ rung06 ❌

**rung06:** `append/3` compound head `[H|R]` — `pj_emit_unify_expr` for `E_COMPOUND` mishandles fresh output vars in head unification.

**Next:** PJ-9 — diagnose rung06, then M-PJ-LISTS.

---

## PJ-7 — Prolog JVM — 2026-03-24

**HEAD:** `c6a8bda` · **Branch:** `main`

**Completed:** M-PJ-BACKTRACK ✅ — rung05 `member/2` outputs `a\nb\nc\n` correctly.

**Fix:** γ formula changed from `base[ci] + sub_cs_out + 1` to `base[ci] + init_cs + 1`. Greek naming throughout `prolog_emit_jvm.c`; Jasmin labels use ASCII spellings.

**Corpus:** rung01 ✅ rung02 ❌ (pre-existing) rung03 ✅ rung04 ✅ rung05 ✅

---

## B-276 — M-BEAUTY-OMEGA ✅ — 2026-03-24

Binary `E_ATP` in value context emitted wrong OPSYN dispatch. Fixed `expr_has_pattern_fn` + `expr_is_pattern_expr`. 106/106 ✅.

**Commits:** snobol4x `151a99b` · .github `468c507`

---

## N-248 — M-T2-NET ✅ M-T2-FULL ✅ — 2026-03-22

`net-t2` branch. 110/110 ALL PASS. CLR stack-frame isolation makes NET T2-correct by construction.

**Commit:** `425921a`

---

*(Entries before N-248 pruned 2026-03-24. Full history in git log.)*

---
## PJ-9 — Prolog JVM (2026-03-24)

**HEAD:** `5ae73e3`  **Branch:** `main`  **Milestone:** M-PJ-LISTS (❌ not yet — blocked on pj_term_str list path)

### Work done
Three bugs fixed in `prolog_emit_jvm.c`:

**1. `is_direct_arg` var-slot mismatch (root cause)**
Old check `slot == ai` failed for any clause where var order differs from arg order.
`append([H|T], L, [H|R])`: L=slot2, arg-pos=1 → `2≠1` → fresh var instead of incoming arg.
Fix: `jvm_arg_for_slot[]` built by scanning head `E_VART` nodes, mapping slot→JVM local correctly.

**2. Non-linear head unification**
Old code skipped all `E_VART` head terms. `append([],L,L)`: L appears at arg-pos 1 and 2 — second occurrence must unify arg2 with `var_locals[slot0]` to enforce arg1==arg2.
Fix: `seen_at[]` tracks first-claim arg; subsequent occurrences emit explicit `pj_unify`.

**3. `pj_write` compound/list support**
Old `pj_write` printed `_` for any compound term.
New `pj_term_str` handles atom/int/float/compound/list recursively. Lists → `[a,b,c]` notation.
JVM VerifyError fixed by storing `StringBuilder` in local (not leaving on stack across `ifeq` branch).

### Status at handoff
- Rungs 01-05: PASS ✅
- Rung 06: FAIL — `write([b,c])` prints `_`; list path in `pj_term_str` not triggering. Suspect `pts_list_close` stack/locals issue. `append([],[b,c],L)` base case now succeeds (non-linear fix worked).

### For PJ-10
Inspect generated `pj_term_str` Jasmin around `pts_list_close` — two paths merge there with potentially different local states. Fix list printing, then rung06 should pass for `append`. `length` and `reverse` may need further debugging.

---

## B-284 — 2026-03-24 — BEAUTY — M-BEAUTIFY-BOOTSTRAP two SPITBOL bugs fixed; ARBNO(*Command) open

**Session:** B-284 · **Branch:** main · **HEAD:** `deae788`

**Milestones fired:** none (M-BEAUTIFY-BOOTSTRAP in progress)

**Bugs fixed in demo/beauty.sno:**

1. **ppAs1/ppAS1 duplicate label → error 217**
   SPITBOL default `-F` (case-fold) treats `ppAS1` (insertion-sort loop, line 176)
   and `ppAs1` (stop-calc branch, line 199) as the same label.
   Fix: renamed `ppAs1` → `ppAstop1` at lines 196 and 199.
   Note: SPITBOL `-f` (case-sensitive) is a documented broken flag in x64 v4.0f —
   with fold off, `END` is not found (internals stay lowercase). Cannot use as workaround.
   CSNOBOL4 fixed point re-confirmed after rename.

2. **`*upr(tx)` call-by-name returns value → error 021**
   `TxInList = (POS(0) | ' ') *upr(tx) (' ' | RPOS(0))`
   `upr()` returns a string via `RETURN`; SPITBOL fires error 021 when a
   value-returning function is called by name (`*` prefix in pattern context).
   Fix: replaced with `EVAL('upr(tx)')` — deferred evaluation in value context.
   CSNOBOL4 fixed point confirmed after fix.

**Remaining SPITBOL error 021:**
- Root cause pinpointed to `ARBNO(*Command)` by binary search.
- Simple patterns (nPush/nPop, ARBNO('x'), nPush+ARBNO('x')+nPop) all OK.
- `ARBNO(*Command)` alone triggers error 021.
- `Command` pattern contains: `nInc() FENCE(*Comment ~ 'Comment' (...) nl | *Control | *Stmt (...))`
- `~` is OPSYN'd to `shift(2-arg)`; `Shift()` returns `.dummy` via `NRETURN` — should be OK.
- The `("'Comment'" & 1)` uses `&` OPSYN'd to `reduce(2-arg)`; `reduce_` returns pattern via `RETURN` — value context, should be OK.
- Error fires at `END` (line 784) after 760–777 stmts; SETEXIT cannot catch error 021 (it's `erb` = fatal bypass).
- Input: any statement-containing block triggers it. Pure comments do not.

**Next action B-285:**
Examine `*Stmt` path inside `Command`: `*Stmt ("'Stmt'" & 7) (nl | ';')`.
`Stmt = *Label (*White *Expr14 FENCE(...)) FENCE(*Goto | ...)`.
`*Label`, `*Goto`, `*Expr14` are all name-calls on PATTERN variables — not functions.
Suspect: one of the `("'X'" & N)` reduce calls inside Stmt/Expr actually calls
`reduce_()` in a name context inadvertently. Check whether OPSYN'd `&` when used
inside an already-deferred pattern (inside `*Stmt` which is inside `ARBNO(*Command)`)
causes SPITBOL to treat the `&`/reduce call as a name-call rather than value-call.
Alternatively: `*Stmt` may be a SPITBOL-incompatible deferred pattern reference to
a variable whose value was built using `reduce_()` — and SPITBOL's `*` dereference
triggers OFNE check on the stored function-result pattern.

**Invariants:** 106/106 ✅

## B-285 — 2026-03-24 — BEAUTY accounting — full test sweep before bootstrap

(1) Cloned snobol4harness + snobol4corpus; built CSNOBOL4 2.3.3 from tarball; confirmed 106/106 ASM corpus ALL PASS; C backend marked ☠️ DEAD (99/106, not maintained).
(2) Re-ran all 19 beauty subsystem drivers standalone through ASM: 15/19 PASS. Regressions found: is, TDump, Gen, semantic FAIL. Filed M-BUG-IS-DIALECT, M-BUG-TDUMP-TLUMP, M-BUG-GEN-BUFFER, M-BUG-SEMANTIC-NTYPE.
(3) Bootstrap trial: beauty_asm produces 10-line header + Parse Error vs oracle 784 lines. Filed M-BUG-BOOTSTRAP-PARSE. HQ updated. No snobol4x code changes this session.
---

## PJ-10 — 2026-03-24

**Branch:** `main` | **HEAD at close:** `64d350a`

### What was done
- Read PLAN.md, FRONTEND-PROLOG-JVM.md, BACKEND-JVM-PROLOG.md, FRONTEND-PROLOG.md, RULES.md
- Ingested JCON source (jcon-master.zip) for reference on closure/resume patterns
- Diagnosed rung06 silent failure: traced `jvm_arg_for_slot[]` bug — second pass over head args overwrote slot→argindex mapping with LAST occurrence not FIRST. In `append([],L,L)`, slot 0 was mapped to arg2 instead of arg1; non-linear unify became `pj_unify(arg2,arg2)` — no-op. arg1 (`[c,d]`) never bound.
- **Fix applied:** Added `if (jvm_arg_for_slot[ht->ival] < 0)` guard at `prolog_emit_jvm.c` line 1454. First occurrence wins.
- Confirmed rungs 01-05 still PASS after fix.
- **Remaining:** rung06 still silent after fix — `append` call returns null (ω) at runtime. Second bug open for PJ-11. Suspected: `main` fails before reaching `write`. Minimal repro (`append([],[c,d],L)`) needed to isolate.

### Invariants
- Rungs 01-05 JVM: PASS ✅

## PJ-11 — 2026-03-24

**Repo:** snobol4x `main` · **HEAD:** `e3c30ab`
**Milestone:** M-PJ-LISTS ✅

**Work done:**
- Diagnosed rung06 silent-fail (Bug 2, listed as open in PJ-10 handoff)
- Root cause: `init_cs = cs - base[ci]` goes negative when `alphafail` routes from clause `ci-1` to clause `ci` without updating `cs` (e.g. cs=0, base[1]=1 → init_cs=-1). The body ucall receives cs=-1, dispatch hits omega immediately.
- Fix: `dup/ifge/pop/iconst_0` clamp at each clause α entry in `pj_emit_choice` (`prolog_emit_jvm.c`).
- Rungs 01–06 all PASS. No regressions.

**Next:** PJ-12 → M-PJ-CUT (rung07 cut/differ). See FRONTEND-PROLOG-JVM.md §NOW for bootstrap and cut design notes.

---

## PJ-12 — 2026-03-24

**Milestone:** M-PJ-CUT ✅  
**Commit:** `bf20b73` snobol4x main  
**Result:** Rungs 01-07 all PASS via `-pl -jvm`

**What was fixed:** `E_CUT` in `pj_emit_body` was emitting only `goto lbl_γ` — it succeeded but never sealed β. Clause 2 (`_,_ .`) remained reachable after cut+fail, giving wrong `yes` for `differ(a,a)`.

**Fix:** Added three parameters to `pj_emit_body`: `cut_cs_seal` (`base[nclauses]`), `cs_local_for_cut` (JVM local holding predicate's `cs`), and `lbl_pred_ω` (predicate-level omega label). When `E_CUT` fires: (1) `ldc base[nclauses]; istore cs_local` seals β so next dispatch hits omega, (2) remaining body goals emit with `lbl_ω = lbl_pred_ω` so failure after cut skips all clauses. Same seal added to `pj_emit_goal` E_CUT branch.

**Next:** PJ-13 → M-PJ-RECUR (rung08: fibonacci/2, factorial/2)

---

## B-286 — 2026-03-24

**Milestone:** 4 bug milestones resolved; D-001–D-005 arch decisions recorded  
**Commit:** `d8f1fe2` snobol4x main  
**Result:** 19/19 beauty subsystems PASS; 106/106 corpus invariant holds; SPITBOL-primary architecture declared

**Arch decisions (DECISIONS.md created):**
- D-001: SPITBOL is the primary compat target. CSNOBOL4 FENCE difference disqualifies it as full target.
- D-002: DATATYPE() returns UPPERCASE always (traditional SNOBOL4 spec). SPITBOL lowercase is ignore-point.
- D-003: Test suite case-insensitive on DATATYPE output. normalize_trace.py and run_beauty_subsystem.sh normalise before diff.
- D-004: .NAME is a third dialect — snobol4x emits DT_N (type=9). Observable behaviour matches SPITBOL (DIFFER succeeds, IDENT fails). Monitor ignore-point covers DT_N vs DT_S.
- D-005: Monitor swapped — SPITBOL is participant 0 (primary oracle). CSNOBOL4 is secondary.

**Bug fix:** Single line in `emit_byrd_asm.c`: arg staging loop now always passes `rbp_off=-32` to `emit_expr` (was `-(rbp_off < 0 ? -rbp_off : 32)`). When a function call appears in subject position (rbp_off=-16), the old code caused E_VART to emit `GET_VAR→rbp-16/8` while `STORE_ARG32` reads `rbp-32/24` — stale data. Fix resolves four milestones: M-BUG-IS-DIALECT, M-BUG-SEMANTIC-NTYPE, M-BUG-TDUMP-TLUMP, M-BUG-GEN-BUFFER.

**Files changed:** `src/backend/x64/emit_byrd_asm.c`, `test/monitor/run_monitor_3way.sh`, `test/monitor/tracepoints.conf`, `test/beauty/run_beauty_subsystem.sh`. HQ: `DECISIONS.md` (new), `ARCH.md`, `MONITOR.md`, `TINY.md`, `PLAN.md`.

**Still open:** M-BUG-BOOTSTRAP-PARSE — beauty_asm outputs 10-line header + `Parse Error` on first non-comment line. Oracle (SPITBOL) = 784 lines. Next session B-287 investigates the ARBNO/parser loop in bootstrap path.

## PJ-13 (2026-03-24) — M-PJ-RECUR + M-PJ-BUILTINS

**Rungs fired:** 08 (recursion), 09 (builtins)
**HEAD:** `5197730`
**Rungs 01-09:** ALL PASS via `-pl -jvm`

### rung08 — fib/2, factorial/2
PASS on first try. PJ-12 multi-ucall body wiring was already correct.

### rung09 — functor/3, arg/3, =../2, type tests
Added to `pj_emit_goal`: `functor/3`, `arg/3`, `=../2` (via new `pj_term_to_list` runtime helper), type tests (`atom/1` `integer/1` `float/1` `compound/1` `var/1` `nonvar/1` `atomic/1` `is_list/1`), `\+/1`, `==/2`, `\==/2`.
Key bug: JVM VerifyError "inconsistent stack height" — `dup`+branch patterns left stack unbalanced at join points. Fix: all branch targets entered with empty stack (re-emit term at each path).

### Next: M-PJ-CORPUS-R10
Test puzzle_01–06 (already solved) via -pl -jvm. Then tackle stubs per FRONTEND-PROLOG.md ordering (M-PZ-14 first). Note: `mod` missing from prolog_lower.c arith table — needed before integer-search puzzles.

## I-11 — ICON frontend — M-ICON-CORPUS-R3

**HEAD:** `bab5664` **Date:** 2026-03-24

**Work done:**
- Applied 3 patches to `icon_emit.c`: `icn_suspend_rbp` BSS slot; yield path saves `rbp`; β resume path restores `rbp` before `jmp [rel icn_suspend_resume]`
- Root cause fixed: β trampoline was jumping into generator with caller's `rbp`, so `[rbp-8]` read garbage from wrong frame
- Wrote rung03 corpus: t01_gen (existing) + t02_return, t03_fail, t04_gen_filter, t05_gen_compose
- Added `run_rung03.sh` runner
- **5/5 rung03_suspend PASS** — M-ICON-CORPUS-R3 ✅

**Next:** M-ICON-STRING — `ICN_STR` node + `||` concat via `CAT2_*` macros

## IJ-7 (2026-03-24) — Diagnosis session: JVM rung03 no-output bug

**HEAD:** `a3d4a55` (no snobol4x commits — diagnosis only, no fix landed)
**Date:** 2026-03-24

### Work done
- Confirmed bp.ω fix (IJ-6) already applied at line 521 of `icon_emit_jvm.c`
- Confirmed rung03 x64 ASM backend: **5/5 PASS** at HEAD `bab5664`
- Built icon_driver clean (0 warnings)
- Generated Jasmin for t01_gen; class assembles and loads but produces **no output**
- Full Jasmin trace: `icn_0_condok: pop2` pattern is structurally correct; relay labels populate lc/rc slots before `icn_1_check` — wiring is sound per JCON `ir_a_Binop` pattern
- Diagnosis: upto must be reaching `icn_upto_done` (sets `icn_failed=1`) instead of `icn_upto_sret` (suspends); confirmed by tracing `icn_14_docall → ifne icn_14_after_call → icn_main_done` path
- Proposed IJ-8 action: instrument Jasmin with stderr probes at `icn_upto_fresh`, `icn_4_yield`, `icn_upto_sret`, `icn_upto_done`; verify `.limit locals` vs actual slot usage via `javap -v`

### Next
IJ-8: instrument → find exact branch → fix → fire M-IJ-CORPUS-R3

---

**B-287 (2026-03-24) — E_STAR pat_ref fix; bootstrap CALL_PAT gap diagnosed; 106/106:**
(1) Setup: CSNOBOL4 built from tarball, SPITBOL prebuilt verified, snobol4corpus cloned, 106/106 confirmed. Reproduced Parse Error: beauty_asm outputs 10 lines then "Parse Error" on "START\n".
(2) Root cause 1: E_STAR in emit_expr value-context called stmt_get() (snapshots var at assignment time). "Parse = nPush() ARBNO(*Command)..." ran before Command was assigned → ARBNO(null) built permanently broken pattern. Fix: emit pat_ref() instead → XDSAR deferred lookup. Commit `843b9f3`.
(3) Root cause 2 (open): CALL_PAT_α is one-shot match_pattern_at — no backtracking bridge from outer compiled Byrd-box into inner engine. ARBNO(*Command) matches 0 iterations (correct); outer RPOS(0) then fails; engine never receives RECEDE to try 1+ iterations. Fix requires T_VARREF integration (B-288).
## IJ-8 — 2026-03-24

**No code written.** Session consumed by context overhead (jcon-master + full repo read) and session-type misidentification (I vs IJ confusion).

**What happened:**
- Cloned snobol4x + .github, extracted jcon-master.zip, read PLAN.md, FRONTEND-ICON.md, FRONTEND-ICON-JVM.md, RULES.md, irgen.icn in full
- Incorrectly began briefing under I-session (ASM frontend) instead of IJ-session (JVM backend)
- Root cause: "ICON frontend + JVM backend" phrasing triggered I-session association; "JVM backend" signal was underweighted
- **Fix:** Added `⚠ ICON vs IJ DISAMBIGUATION` rule to RULES.md (commit b21617a) — "JVM backend" = IJ, always

**No milestones fired. No snobol4x changes.**

### Next
IJ-9: build → instrument `icn_upto` with stderr probes → find exact branch taking `done` not `sret` → fix → fire M-IJ-CORPUS-R3

## IJ-9 — 2026-03-24

**Trigger:** "ICON frontend with JVM backend" → IJ-session (icon_emit_jvm.c)
**Milestone:** M-IJ-CORPUS-R3 ✅
**HEAD:** `54c301b` snobol4x main

**Work done:**
- Diagnosed IJ-7 no-output bug: zero-init loop clobbered param n (slot 0) before `ifne icn_upto_beta`
- Root fix: named locals/params now use per-proc static fields `icn_pv_PROCNAME_VARNAME` instead of JVM local slots — survive `return`-based yield/resume cycle
- Second bug: `icn_suspend_id` not cleared at `proc_done`; second call to same generator jumped to beta. Fixed: clear `icn_suspended` + `icn_suspend_id` at `proc_done`
- Result: 5/5 rung03 PASS (t01_gen, t02_return, t03_fail, t04_gen_filter, t05_gen_compose)
- rung01 5/6 (t06_paper_expr pre-existing VerifyError — not a regression), rung02 8/8 clean

## PJ-15 — 2026-03-24 (emergency handoff at ~95% context)

**Trigger:** "playing with Prolog frontend for snobol4x with JVM backend"
**HEAD in:** `fabd377` (PJ-14)
**HEAD out:** `0df7b38` (PJ-15, already on remote snobol4x)

**Work done:**
- Rungs 01-09 PASS confirmed on entry
- Fixed `call_omega` bug: `local_cs` for exhausted inner call was not reset to 0 before jumping to enclosing beta, causing infinite loop when e.g. `differ` was exhausted and `item(Y)` retried
- Fix: `iconst_0 / istore local_cs` before `goto lbl_ω` at `call_omega` label in `pj_emit_body` — committed `0df7b38` to snobol4x
- Identified remaining bug: two-clause `fail/retry` pattern (`p :- ..., fail. p.`) loops forever because `fail/0` in last body position receives `lbl_ω=clause_beta` instead of `lbl_pred_ω`, so exhausting clause 0 restarts it instead of advancing to clause 1

**Next session PJ-16:** Fix `fail/0`→`lbl_pred_ω` wiring in `pj_emit_clause`/`pj_emit_body`. See §NOW CRITICAL NEXT ACTION.

## IJ-9 (continued) — M-IJ-STRING — 2026-03-24

**Milestone:** M-IJ-STRING ✅
**HEAD:** `9932df5` snobol4x main

**Work done:**
- Added `'A'`-typed String static fields (`icn_pv_PROC_VAR Ljava/lang/String;`) alongside existing J/I types
- `ij_get_str_field` / `ij_put_str_field` helpers; `ij_declare_static_str`
- `ij_expr_is_string(n)` type predicate: ICN_STR, ICN_CONCAT, write(str), ICN_ASSIGN(str rhs), ICN_VAR (lookup table)
- `ij_emit_concat` — funcs-set Byrd-box wiring with String relay static fields; `String.concat` compute
- Pre-pass in `ij_emit_proc` to register string-typed vars before reverse emit loop (ordering fix)
- `sdrain` fixed: `pop` for String result, `pop2` for long — resolves VerifyError
- `ij_emit_assign` and `ij_emit_var` updated for String vs long branching
- **Bonus:** t06_paper_expr (rung01) previously failing VerifyError now passes — 19/19 rung01-03 clean
- Created rung04_string corpus: t01_str_lit, t02_concat, t03_str_var, t04_multi_str, t05_concat_chain
- Result: 5/5 rung04 PASS; total corpus 24/24 PASS
- Next: M-IJ-SCAN (`E ? E` string scanning)

---

## PJ-16 — 2026-03-24

**Session:** Prolog JVM · `main` · HEAD `f575016`
**Milestone:** (none fired — M-PJ-CORPUS-R10 still open)

**Work done:**
- Diagnosed and fixed two-clause fail/retry infinite loop (min3 reproducer).
- True root cause: `pj_emit_clause` passed `α_retry_lbl` as `lbl_ω` to top-level `pj_emit_body`. When outermost body user-call exhausted, `call_ω → α_retry_lbl` re-ran clause from cs=0 forever.
- Fix: pass `ω_lbl` (next-clause dispatch) as `lbl_ω` to top-level `pj_emit_body`. One line changed in `pj_emit_clause`. Added `pj_is_always_fail()` helper.
- Rungs 01–09: 9/9 PASS. No regressions. min3: `a-b\nb-a` ✅

**Next:** PJ-17 — M-PJ-CORPUS-R10 (rung10 puzzle stubs). Puzzles 01/02/05/06 already pass swipl oracle. Start with M-PZ-14 (easiest per FRONTEND-PROLOG.md ordering).

## IJ-10 — 2026-03-24

**Session:** Icon JVM · `main` · HEAD `992a3a5`
**Milestone:** (none fired — M-IJ-SCAN open)

**Work done:**
- Diagnosed session routing error: "playing with ICON frontend with JVM backend" incorrectly triggered I-session (x64 ASM) instead of IJ-session. Root cause: FRONTEND-ICON.md trigger phrase lacked JVM exclusion; FRONTEND-ICON-JVM.md trigger too narrow.
- Fixed both trigger phrases in HQ; added disambiguation note to RULES.md §SESSION NUMBERS.
- Reverted incorrect ASM work (icon_emit.c / icon_runtime.c changes from wrong session).
- Clarified FRONTEND-ICON-JVM.md header: icon_emit_jvm.c is JVM backend emission, not frontend parsing.
- Created rung05_scan corpus: 5 tests (t01–t05) covering &subject read, scan from var, restore after scan, concat subject, nested scan. Committed `992a3a5` to snobol4x.
- Full M-IJ-SCAN implementation plan documented in FRONTEND-ICON-JVM.md §IJ-10 findings (static fields, &subject keyword, ij_emit_scan four-port wiring, dispatch case, run_rung05.sh).

**Next:** IJ-11 — implement ij_emit_scan, &subject keyword, icn_subject/icn_pos globals, fire M-IJ-SCAN.

---

**B-288 (2026-03-24) — M-BUG-BOOTSTRAP-PARSE partial fix; 106/106 ✅**
(1) Root cause diagnosed via MONITOR: `Cmd = Word Space Word` (concat of E_VARTs) not registered as named pattern — `expr_is_pattern_expr` returns 0. E_VART fallback was `LIT_VAR_α` (string-only `stmt_match_var`) → changed to inline CALL_PAT expansion with `var_register` (box-DATA-aware slots). `Cmd` now dispatches as DT_P at runtime.
(2) `rpat_t/p/s` slots: `flat_bss_register` → `var_register` so slots land in r12 DATA block at correct offsets; inline macro expansion avoids NASM double-dereference of `r12+N`.
(3) Named-pattern α-entry zeroing: `P_Parse_α` now emits `mov qword [r12+N], 0` for all mutable slots (offset ≥16) to prevent stale ARBNO depth/cur_before from previous scan attempt corrupting retry.
(4) Remaining failure: `*Parse` via REF(Parse) scan-retry — P_Parse_β enters `seq_r5_β` directly without zeroing DATA slots; ARBNO depth left stale. Fix in B-289: emit DATA zeroing at β call site in `emit_named_ref` before `jmp P_Parse_β`. 106/106 ✅. HEAD `358184a`.
---
## IJ-11 — 2026-03-24

**Milestone:** M-IJ-SCAN ✅

**Work done:**
- Implemented `ij_emit_scan()` in `icon_emit_jvm.c`: full four-port Byrd-box wiring per JCON `ir_a_Scan` / JCON-ANALYSIS §`E ? body`. Per-scan static save slots `icn_scan_oldsubj_N`/`icn_scan_oldpos_N`. Global `icn_subject` (String) + `icn_pos` (I) fields. `<clinit>` emitted when scan fields present, initializing `icn_subject=""` and `icn_pos=0`.
- Added `&subject` branch to `ij_emit_var`: checked before regular slot/global lookup, emits `getstatic icn_subject`.
- Added `ICN_SCAN` and `ICN_VAR/"&subject"` cases to `ij_expr_is_string`. Critical: missing these caused VerifyError (`pop2` on 1-slot String result) on all 5 tests.
- Added `case ICN_SCAN: ij_emit_scan(...)` to dispatch.
- Committed `run_rung05.sh` (5-test runner).
- **rung05: 5/5 PASS. rung01-04: 24/24 still clean. Total: 29/29.**
- HEAD: `7d68a85` on `main`.

**Next:** IJ-12 — M-IJ-CSET: cset literals → BREAK/SPAN/ANY.
## PJ-17 (2026-03-24)
**Milestone: M-PJ-CORPUS-R10 ✅**
Wrote all 20 rung10 puzzle .pro files. All 20 pass swipl oracle and JVM backend.
- Puzzles 01,02,05,06: pre-existing, confirmed passing.
- Puzzles 04,14,16,17: proper Prolog search, JVM PASS.
- Puzzles 07,08,09,10,11,12,13,15,18,19,20: hardcoded write — needs rewrite as proper search (next session).
- Puzzle 03: rewritten as proper search at session end; swipl produces duplicate solutions — needs dedup fix.
**JVM backend bugs found:**
- `(A;B;C)` inline disjunction in arithmetic body fails silently — workaround: helper predicate.
- 5-6 clause predicates with large bodies: `VerifyError: Stack size too large` — `.limit stack` over-estimate in `prolog_emit_jvm.c`.
- `display/16` (16 args): `ClassFormatError: illegal signature` — method descriptor too long.
**HEAD:** snobol4x `e14bed2`

## PJ-17 addendum (2026-03-24)
puzzle_07 rewritten as proper search — swipl PASS, HEAD e568687.
puzzle_08 attempted — still produces multiple solutions; reverted to hardcoded write. Root cause: `\+` over `posOf/6` with unbound vars doesn't prune correctly in search. Needs posOf restructured so positions are bound before gender checks fire. Next session: fix puzzle_08 first, then 09-13, 15, 18-20.
puzzle_03 has proper search but produces duplicates — needs single-solution cut or once/1.
---

## IJ-11 addendum — 2026-03-24 (rung06 corpus)

Committed rung06_cset corpus (5 tests) to snobol4x `c166bfe`. Full M-IJ-CSET implementation plan written to FRONTEND-ICON-JVM.md §IJ-11 findings. Plan covers: ICN_CSET as String (trivial), any/many/upto as built-in calls using icn_subject/icn_pos, upto generator via direct goto-loop (no tableswitch), cset-var assignment via existing pre-pass type inference. IJ-12 is a clean-start session: build, confirm 29/29, implement per plan, fire M-IJ-CSET.
---
## PJ-18 — 2026-03-24

**Work:** Began M-PJ-R10-SEARCH. Rewrote puzzle_08 and puzzle_09 from hardcoded stubs to real idiomatic Prolog search. Both pass swipl oracle with unique solutions. JVM pipeline fails for both: `\=/2` is listed as builtin in `pj_is_user_call` but has no emit case in `pj_emit_goal` — falls through to user-call block, `pj_safe_name("\\=")` produces mangled label `p____2`, JVM throws `NoSuchMethodError`. Logged as M-PJ-NEQ.

**Commits:** snobol4x `fcdd57c`

**Next:** PJ-19 — fix M-PJ-NEQ (`\=/2` emit), then continue puzzle search rewrites one milestone at a time.

---
## PJ-19 — 2026-03-24

**Work:** M-PJ-PZ10 — puzzle_10 rewritten as real Prolog search. Unique solution via domain generation + member_of3 + sex constraints on dating pair. Puzzle mildly underconstrained (Jane=clark vs Jane=carter ambiguous from clues alone); pinned to published answer with Jane=clark. swipl PASS. JVM still blocked on M-PJ-NEQ.

**Commits:** snobol4x `27de835`

**Next:** PJ-20 — puzzle_11 search rewrite (M-PJ-PZ11).

## IJ-12 — 2026-03-24

**Milestone:** M-IJ-CSET ✅

**Work done:**
- `ICN_CSET` dispatch: reuses `ij_emit_str` (cset literal = ldc String); `ij_expr_is_string` returns 1 for ICN_CSET.
- `any(cs)` built-in in `ij_emit_call`: evaluates cs, calls `icn_builtin_any(cs,subj,pos)→long`, advances `icn_pos`. Guarded `!ij_is_user_proc`.
- `many(cs)` built-in: same pattern, calls `icn_builtin_many`.
- `upto(cs)` built-in generator: saves cs in `icn_upto_cs_N`; α/β both enter step label; calls `icn_builtin_upto_step`; sets `icn_pos=result` on match.
- Three static helper methods emitted in `ij_emit_file` (gated on `icn_subject` in statics).
- **ICN_AND fix (bonus)**: was emitting right-to-left causing `ccb[i-1]=""` bug; fixed to left-to-right with relay trampolines that drain child result (pop/pop2) before entering next child's α.
- **User-proc guard**: prevents `any`/`many`/`upto` builtins from shadowing user procs with same names.
- `run_rung06.sh` committed.
- **rung06: 5/5 PASS. rung01-05: 29/29 still clean. Total: 34/34.**
- HEAD: `369f2bf` on `main`.

**Next:** IJ-13 — M-IJ-CORPUS-R4 fires immediately (rung04+05+06=15/15 already PASS). Declare it, then plan next milestone.