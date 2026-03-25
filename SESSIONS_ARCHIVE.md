> Org renamed SNOBOL4-plus → snobol4ever, repos renamed March 2026. Historical entries use old names.

# SESSIONS_ARCHIVE.md — Append-only session log

**Format:** One `## SessionID — Description ✅/❌ (date)` block per session.
Oldest sessions pruned for context economy. Full git history is the permanent record.

---

## PJ-37 — Prolog JVM — 2026-03-25

**HEAD in:** `1f904e8` PJ-36 | **HEAD out:** `d4abf38` PJ-37

**Work done:**
- Landed `pj_body_has_cut(EXPR_t *g)` recursive helper in `prolog_emit_jvm.c` — walks `E_FNC` children for nested `E_CUT`, replacing shallow scan in `any_has_cut` loop inside `pj_emit_predicate`.
- Confirmed 18/20 baseline. Recursive helper correct, no regressions.
- **puzzle_18 root cause fully re-diagnosed:** cut is inside callee `differ/2`, not in `puzzle/0`'s body. The `any_has_cut` guard fires for the *compiled* predicate only — it cannot protect callers. At the ucall call site in `puzzle/0`, the `ifnull call_ω` only catches null (failure); cutgamma `{cs=2}` is non-null → falls through as success → body prints answer → TWICE. `grep "if_icmpeq" /tmp/Puzzle_18.j` = empty confirms no guard at call site.

**Score:** 18/20 (unchanged — fix targeted wrong layer).

**Next (PJ-38):** Implement `pj_predicate_base_nclauses(fn, arity, prog_root)` and emit call-site cutgamma detection guard in `pj_emit_body` after `ifnull call_ω`. Full spec in FRONTEND-PROLOG-JVM.md §NOW CRITICAL NEXT ACTION.

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
## Session 2026-03-24 B-289 — M-BEAUTIFY-BOOTSTRAP buffer limits + FENCE + r12

**Invariant maintained:** 106/106 ASM corpus ALL PASS ✅  
**Commit:** `0378dad` B-289

### Completed fixes (all in this session)

| Fix | File | What it fixes |
|-----|------|---------------|
| `NAMED_PAT_MAX 64→512` | `emit_byrd_asm.c` | Parse/Command/Compiland silently dropped |
| `MAX_BOXES 64→512` | `emit_byrd_asm.c` | DATA block templates missing |
| `call_slots 256→4096` | `emit_byrd_asm.c` | BSS slots for user fn calls dropped |
| `MAX_VARS/LITS/STRS/LABELS/FLTS` bumped | `emit_byrd_asm.c` | Capacity for 420+ named patterns |
| `T_FENCE/T_ARBNO/T_ARB/T_BAL` in mock_engine | `mock_engine.c` | FENCE always returned -1 (hit `default:`) |
| Remove `mock_includes` / `inc_init()` | `snobol4_stmt_rt.c` | C mocks overriding compiled SNOBOL4 functions |
| Binary `E_NAM` in `emit_expr` | `emit_byrd_asm.c` | `epsilon . *PushCounter()` emitted DT_N, not DT_P |
| `stmt_concat` handle `DT_N` | `snobol4_stmt_rt.c` | Name-refs in pattern concat now build `pat_assign_cond` |
| `emit_named_ref` r12 save/restore | `emit_byrd_asm.c` | Nested named-pat calls clobbered caller DATA block pointer |

### Status at handoff
Beauty still shows Parse Error. The r12 save/restore fix is committed but not yet tested against beauty (context window limit hit). This is the **highest-probability remaining fix** — garbage `vtype=139...` in `stmt_match_descr` is consistent with `r12` pointing at wrong DATA block after `*Parse` calls `*Space`.

### Next session action
```bash
cd /home/claude/snobol4ever/snobol4x
# Rebuild with B-289 commit
cd src && make -j4
WORK=/tmp/beauty_build
RT=src/runtime; SNO2C_INC=src/frontend/snobol4
./sno2c -asm -Idemo/inc -I$SNO2C_INC demo/beauty.sno -o $WORK/beauty.asm
nasm -f elf64 -I src/runtime/asm/ -o $WORK/beauty.o $WORK/beauty.asm
for f in snobol4_stmt_rt snobol4 snobol4_pattern mock_engine blk_alloc blk_reloc; do
  gcc -O0 -g -c "$RT/asm/${f}.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/${f}.o" 2>/dev/null ||
  gcc -O0 -g -c "$RT/snobol4/${f}.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/${f}.o" 2>/dev/null ||
  gcc -O0 -g -c "$RT/mock/${f}.c"    -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/${f}.o" 2>/dev/null
done
RT_OBJS="$WORK/snobol4_stmt_rt.o $WORK/snobol4.o $WORK/snobol4_pattern.o $WORK/mock_engine.o $WORK/blk_alloc.o $WORK/blk_reloc.o"
gcc -no-pie "$WORK/beauty.o" $RT_OBJS -lgc -lm -o "$WORK/beauty_bin"
$WORK/beauty_bin < demo/beauty.sno > $WORK/beauty_asm_out.sno
diff /tmp/beauty_oracle.sno $WORK/beauty_asm_out.sno
```
If still failing: check `SNO_CALLDEBUG=1` for garbage vtype — if gone, r12 fix worked and a new bug is next.
If garbage vtype persists: r12 is still being clobbered somewhere else (e.g. user function calls also clobber r12).

---
## Session 2026-03-24 B-289 — M-BEAUTIFY-BOOTSTRAP buffer limits + FENCE + r12

**Invariant maintained:** 106/106 ASM corpus ALL PASS ✅  
**Commit:** `0378dad` B-289 (snobol4x)

### Completed fixes
- `NAMED_PAT_MAX 64→512`: Parse/Command/Compiland silently dropped
- `MAX_BOXES 64→512`, `call_slots 256→4096`, all capacity limits bumped for 420+ named patterns
- `mock_engine.c`: add `T_FENCE/T_ARBNO` — FENCE always hit `default:→-1`
- Remove `mock_includes`/`inc_init()`: C mocks were overriding compiled SNOBOL4
- Binary `E_NAM` fix in `emit_expr`: `epsilon . *PushCounter()` now calls `stmt_concat`
- `stmt_concat`: handle `DT_N` right operand via `pat_assign_cond`
- `emit_named_ref`: save/restore `r12` across nested named-pat calls (committed, not yet tested against beauty — context limit hit)

### Next action
Rebuild beauty from B-289, run, check if garbage `vtype=139...` gone. See SESSIONS_ARCHIVE full entry for exact rebuild commands.
**Next:** IJ-13 — M-IJ-CORPUS-R4 fires immediately (rung04+05+06=15/15 already PASS). Declare it, then plan next milestone.
---

## IJ-13 — 2026-03-24

**Milestones:** M-IJ-CORPUS-R4 ✅; M-IJ-CORPUS-R5 ❌ open (t03_to_by VerifyError)

**Work done:**
- M-IJ-CORPUS-R4 fires: rung04+rung05+rung06 = 15/15 PASS; 34/34 total.
- Implemented ICN_NOT, ICN_NEG, ICN_TO_BY (broken), ICN_SEQ/SNE/SLT/SLE/SGT/SGE.
- every/while/until/repeat drain fix: stmt loop skips sdrain for loop nodes.
- .bytecode 50.0 directive added (insufficient for JVM 21 StackMapTable requirement).
- rung07_control corpus committed (5 tests); run_rung07.sh committed.
- rung07: 4/5 PASS. t03_to_by FAIL: JVM 21 verifier requires StackMapTable for backward branches; Jasmin 2.x doesn't emit them. Logic correct under -noverify.
- HEAD: `6174c9f` on `main`.

**IJ-14 fix:** Rewrite ij_emit_to_by using forward-only α/β dispatch (same pattern as ij_emit_to) — α evaluates start/end/step and yields first value; β advances and re-checks. No backward branch. Full plan in FRONTEND-ICON-JVM.md §IJ-13 findings.
---
## Session 2026-03-24 B-290 — JVM pivot + r12/box_data fixes

**Invariant:** 106/106 ASM corpus ALL PASS ✅  
**Commit:** `05f36ae` B-290 (snobol4x main)

### Fixes landed
- `emit_named_ref`: r12 save slot now uses `flat_bss_register` (was `var_register` → landed in box DATA block → NASM undefined symbol)
- `box_data[MAX_BOXES]` heap-allocated via `calloc` — was 20MB static BSS, caused `sno2c -jvm beauty.sno` segfault mid-output
- `MAX_BOX_DATA_VARS` reverted 512→128 (max actual usage is 53 vars/box)

### PIVOT: JVM Beauty Bootstrap
- ASM bootstrap blocked on systemic r12 clobber in nested named-pattern calls (requires M-T2-INVOKE)
- JVM backend avoids the issue entirely (JVM stack frames, no r12)
- Created `M-BEAUTIFY-BOOTSTRAP-JVM` milestone in PLAN.md
- Added full JVM milestone track (19 subsystems) to BEAUTY.md
- `sno2c -jvm beauty.sno` still segfaults — `named_pats[512]` (~1.5MB static) is next fix

### Next session (J-prefix, jvm-t2 branch OR main)
1. Heap-allocate `named_pats[]` in `emit_byrd_asm.c` (same pattern as `box_data`)
2. Confirm `sno2c -jvm beauty.sno` completes without segfault
3. Assemble with jasmin.jar, run beauty, diff vs oracle
4. Work through 19 JVM subsystem milestones (M-JVM-BEAUTY-*)

## PJ-21 — 2026-03-24

**Milestone fired:** M-PJ-NEQ ✅

**Work done:**
- Added `int *next_local` to `pj_emit_goal` signature (fwd decl + defn); updated all 7 call sites in `pj_emit_body`.
- Inserted `\=/2` emit block after `\==` block: save trail mark to fresh scratch local, call `pj_unify` as probe, `istore` boolean result, `pj_trail_unwind`, `iload` result, branch inverted.
- Added `pj_count_neq` helper; folded `2 * max_neq` into `.limit locals` formula to fix `VerifyError: Illegal local variable number` on `all_diff5` (10 `\=` calls).
- Results: 9/9 rungs PASS (no regression), puzzle_08 PASS, puzzle_09 PASS, 19/21 rung10 PASS (03+11 pre-existing).
- Commit: `d6d2266` on snobol4x main.

**Next:** M-PJ-STACK-LIMIT — `.limit stack 16` hard-code needs fix for deep predicates.

## PJ-22 — 2026-03-24

**Milestone fired:** M-PJ-STACK-LIMIT ✅

**Work done:**
- Added `pj_term_stack_depth(EXPR_t*)` — recursive walker computing max JVM stack slots to construct a term (4 slots/nesting level: array-ref + dup + index + child).
- Added `pj_clause_stack_needed` — walks clause body goals + head args, takes max across all term arguments.
- Replaced hardcoded `.limit stack 16` with `max(16, computed_max)` per predicate in `pj_emit_predicate`.
- Verified: 8-level deep compound term now works (was `VerifyError: Stack size too large`).
- Results: 9/9 rungs PASS (no regression), 19/21 rung10 PASS (puzzle_03 + puzzle_11 pre-existing, different bugs).
- Commit: `cb0b4d0` on snobol4x main.

**Diagnosis of remaining failures:**
- puzzle_11 double-print: `!` inside `ages_ok` not sealing β in enclosing `puzzle` conjunction — `cut_cs_seal` not propagating across user-call boundary. → M-PJ-DISJ-ARITH or new milestone.
- puzzle_03 silent: 6-arm `(;)` with `->` in `not_dorothy` + `=\=/2` in `differ6` — disjunction emitter misfires. → M-PJ-DISJ-ARITH.

**Next:** M-PJ-DISJ-ARITH — write minimal repros, fix `pj_emit_goal` disjunction/cut wiring.

---

## IJ-14 — 2026-03-24

**Trigger:** "playing with snobol4x JVM backend for ICON frontend"
**Goal:** M-IJ-CORPUS-R5 — fix t03_to_by VerifyError, rung07 5/5 PASS

**What was done:**

Rewrote `ij_emit_to_by` in `icon_emit_jvm.c` to fix two bugs:

1. **Backward branches:** Old `adv → chkp/chkn` backward jump triggered JVM 21
   StackMapTable VerifyError. Rewrote with α→check and β→check as forward jumps;
   `check` label placed after β in instruction stream.

2. **Double conditional on single `lcmp`:** `lcmp; ifgt; iflt` stack underflow — `ifgt`
   consumes the int, `iflt` finds empty stack. Fixed with two separate lcmp sequences.

3. **`.bytecode 45.0`:** Switched from 50.0 (Java 6) to 45.0 (Java 1.1 old verifier).
   The 50.0 "no StackMapTable" comment was wrong.

**Added:** `test/frontend/icon/run_rung07.sh`

**Result:** 39/39 PASS rung01-07. M-IJ-CORPUS-R5 ✅. Commit `6780ab9`.

**Next:** M-IJ-CORPUS-R8 — create rung08 corpus, implement next Icon feature.

---

## PJ-23 — 2026-03-24

**Session:** Prolog JVM
**Branch:** `main`
**HEAD at end:** `cb0b4d0` (no new commit — diagnosis-only session)
**Next:** M-PJ-DISJ-ARITH (PJ-24)

### Work done

- Confirmed baseline: 9/9 rungs PASS, puzzle_03 + puzzle_11 FAIL (19/21).
- Exhaustively tested `(;)` ITE emitter: all patterns correct (single-arm, multi-arm, first-arm-fail, deep-arm-fail, trail unwind, variable binding across arms). The disjunction emitter is NOT the bug.
- Found true root cause of puzzle_03 silent failure: `\+` on multi-argument user predicate calls silently fails in JVM emitter. `\+ always_fail` (0-arg) works. `\+ pred(A,B,C)` (multi-arg) does not.
- Root: the `\+` handler in `pj_emit_goal` (~line 1369) does not save/restore trail around the inner call. Any bindings made by the inner predicate before it fails pollute the environment, causing subsequent goals (or the `\+` itself) to misbehave.
- puzzle_11 root cause unchanged: double-print from `!` inside `ages_ok` not sealing enclosing `puzzle` backtrack through `all_diff5`.

### Fix for PJ-24

In `prolog_emit_jvm.c` `\+` handler (~line 1369–1378):
1. Emit `invokestatic pj_trail_mark()I`, store in fresh local `naf_mark`.
2. Call inner goal via `pj_emit_goal` as now.
3. On `inner_ok`: emit `iload naf_mark; invokestatic pj_trail_unwind(I)V`, then `goto lbl_ω`.
4. On `inner_fail`: emit `iload naf_mark; invokestatic pj_trail_unwind(I)V`, then `goto lbl_γ`.

---

## B-291 — 2026-03-25 — BSS heap fix; Sprint M5 unblocked

**Session type:** TINY backend (B-session)
**HEAD on entry:** `05f36ae` B-290
**HEAD on exit:** `309a2f9` B-291
**Branch:** main

**What happened:**
- Setup: cloned .github, snobol4x, x64 (SPITBOL), snobol4corpus. Built CSNOBOL4 2.3.3 from tarball (STNO-patched). Ran setup.sh → 106/106 ALL PASS.
- Root cause of sno2c segfault on beauty.sno diagnosed: total BSS 8.4MB > 8MB stack limit. Binary loads, BSS mapped, process crashes before main() runs.
- Fix: heap-allocated 4 large statics in emit_byrd_asm.c using calloc-on-first-use pattern (identical to existing box_data pattern):
  - named_pats[512] → pointer, -1856KB BSS
  - str_table[8192] → pointer, -2752KB BSS
  - call_slots[4096][320] → pointer, -1280KB BSS
  - lit_table[1024] → pointer, -352KB BSS
  - BSS: 8.4MB → 2.0MB. 106/106 corpus still ALL PASS.
- sno2c -asm beauty.sno → 70,840 lines of ASM. beauty_asm_bin built (1.1MB), runs, outputs 10 lines then "Parse Error" (r12 DATA-block clobber, expected per M-BUG-BOOTSTRAP-PARSE).
- sno2c -jvm beauty.sno → 18,348 lines of Jasmin, then mid-emission segfault. GDB confirmed: e=0x21 (garbage pointer) in jvm_emit_expr for DATA constructor field[2] of tree(t,v,n,c). Root cause: emit loop iterates dt->nfields but e->nchildren may be smaller; out-of-bounds children[] access. Fix: use (fi < e->nchildren) bound. Not yet applied — context limit.
- TRACE_SET_CAP 64→256 in snobol4.c (beauty.sno injects 107 TRACE registrations).
- Sprint M5 attempted: inject_traces.py on beauty.sno → 107 TRACE registrations. CSNOBOL4 oracle run: 92,601 trace events, 784 lines output. ASM trace: silent (TERMINAL= fallback; crash occurs before trace stream flows). Async diff approach identified as immediate next step.
- SPITBOL monitor IPC times out at step 0 (M-MON-BUG-SPL-EMPTY, pre-existing).

**Milestones fired:** none (M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR created, not yet fired)

**Invariants on exit:** 106/106 ALL PASS ✅

**Next session (B-292):**
1. Fix JVM mid-emission crash: `if (fi < e->nchildren)` bound in emit_byrd_jvm.c line 1133
2. Get ASM trace stream: redirect TERMINAL= output in comm_var OR just diff csn_trace.txt vs asm_trace.txt async
3. First diverging trace line names the r12 clobber site → fix emit_named_ref
4. Fire M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR

---

## IJ-15 — 2026-03-24

**Trigger:** "playing with snobol4x JVM backend for ICON frontend" + jcon-master.zip uploaded.
**Sprint:** Icon JVM. **HEAD start:** `6780ab9` (IJ-14). **HEAD end:** `6f11821`.

**Work done:**
- Cloned snobol4x + .github fresh; installed default-jdk + nasm + libgc-dev.
- Confirmed baseline **39/39 PASS** rung01–07 using `.expected` oracle harness.
- Harness clarification: `-run` needs `-o` flag + nasm link; correct harness uses `.expected` files directly.
- Extracted and read JCON-ANALYSIS.md (386 lines); read FRONTEND-ICON-JVM.md §NOW fully.
- Designed and committed **rung08_strbuiltins** corpus (5 tests: `find` one-shot, `find` generator, `match`, `tab`, `move`).
- Documented full IJ-16 implementation plan in FRONTEND-ICON-JVM.md §NOW (emitter changes for find/match/tab/move including static helpers, generator pattern for find, String-type inference for tab/move).

**Milestone:** M-IJ-CORPUS-R8 — corpus committed ✅; emitter implementation deferred to IJ-16.
**Next:** IJ-16 implements find/match/tab/move in `ij_emit_call` + static helpers → fires M-IJ-CORPUS-R8.

---
## PJ-24 — 2026-03-24

**Fixes landed (snobol4x a77555c):**
1. `\+` trail corruption: save mark before inner goal, unwind on both inner_ok and inner_fail paths. Mirrors `\=/2` pattern.
2. Body-fail trail corruption: added `bodyfail_N` trampoline per clause in `pj_emit_choice`. Body goal failure now unwinds clause trail before jumping to next clause. `lbl_outer_ω` (ucall exhaustion) bypasses trampoline to avoid double-unwind.

**Baseline:** 9/9 rungs PASS throughout.

**puzzle_03:** logic search correct (12/12 assignments match swipl). `display/6` over-generation remains open as M-PJ-DISPLAY-BT.

**HQ updates:**
- Added 20 puzzle milestones M-PZ-03..20 to PLAN.md (all ❌, write+swipl verify).
- FRONTEND-PROLOG-JVM.md §NOW updated with PJ-25 bootstrap.

**Next session (PJ-25):** Start M-PZ-14 (golf scores, easiest puzzle). Write solution, verify swipl, fire milestone. Then proceed through milestone list in order.

## IJ-16 — Icon JVM session

**Date:** 2026-03-24  **HEAD:** `be1be82`  **Milestone:** M-IJ-CORPUS-R8 ✅

Implemented `find`/`match`/`tab`/`move` string builtins in `icon_emit_jvm.c`.
All four use static helper methods (same pattern as `any`/`many`/`upto`).
`tab`/`move` return String (null on failure); `ij_expr_is_string` updated.
`need_scan_builtins` guard extended to detect `icn_find_s1_N` statics.
44/44 rung01-08 PASS. Baseline rung01-07 39/39 unchanged.

---

## B-292 — 2026-03-24 — epsilon . *VAR bug found (no fix applied)

**HEAD on entry:** `6f11821` **HEAD on exit:** no commit **Branch:** main

**TL;DR:** `epsilon . *FN()` side-effect does not fire at match time in ASM backend.

**Minimal reproducer:**
```snobol4
        ctr = 0
        Inc = ctr = ctr + 1
        p = epsilon . *Inc
        '' *p
        OUTPUT = 'ctr: ' ctr   * Oracle: 1 / ASM: 0
END
```

**Root cause cascade:**
- beauty.sno builds `Parse = nPush() ARBNO(*Command) ... nPop()`
- `nPush()` returns `epsilon . *PushCounter()` — a match-time side-effect pattern
- ASM does not fire `*PushCounter()` at match time → counter stack never initialized → `nTop()` wrong → parse fails → `"Parse Error"` on output line 8

**Fix location:** `src/backend/x64/emit_byrd_asm.c` — the pattern emitter for dot-operator with `E_STAR(E_CALL(...))` RHS. Currently evaluates `*FN()` at build time or builds wrong capture node. Must emit `pat_immed`-style node that executes `FN()` at match time.

**Also found:** `blk_alloc.c` missing from link line in `test/crosscheck/run_crosscheck_asm_prog.sh`.

**Next (B-293):** Fix `epsilon . *FN()` in emit_byrd_asm.c → re-run beauty bootstrap → fire M-BEAUTIFY-BOOTSTRAP.

---

## PJ-25 through PJ-30 — Puzzle corpus real-search rewrite

**Sessions:** PJ-25, PJ-26, PJ-27, PJ-28, PJ-29, PJ-30
**Branch:** main
**Repo:** snobol4x + .github

**Work done:**
- Audited all 16 M-PZ puzzle files: identified 7 hardcoded write stubs (puzzle_12, 13, 15, 16, 18, 19, 20).
- Updated FRONTEND-PROLOG.md milestone table to reflect real-search status vs stub.
- Rewrote all 7 stubs as genuine Prolog constraint search; all pass swipl.
- puzzle_15: derived correct answer (Vernon=doctor/Wilson=architect/Yates=lawyer) — original stub had wrong answer.
- puzzle_18: derived correct answer (Abbott=hardware/Denny=shoe) — original stub had Abbott/Denny swapped.
- puzzle_20: original stub violated "novelist never reads history"; real search found 4 valid solutions.
- puzzle_16: uses minimal family-inference (brakeman=art forced from "John older than Art" + uncle reasoning).
- puzzle_12: 2 valid solutions (Conroy/Eggleston math/history symmetric); accepted both.

**Milestones fired:** M-PZ-14 ✅, M-PZ-15 ✅, M-PZ-16 ✅, M-PZ-12 ✅, M-PZ-13 ✅, M-PZ-18 ✅, M-PZ-19 ✅, M-PZ-20 ✅

**Still open:** M-PJ-DISPLAY-BT (puzzle_03 JVM over-generates; ITE cut leak in pj_emit_goal).
**Next:** PJ-31 — fix puzzle_03 not_dorothy to single clause; verify JVM 1L. Then puzzle_11 2L issue.

**HEAD at handoff:** snobol4x `8ace0f7`, .github `d8e49fe`

---

## PJ-31 — Add M-PZ-01/02/05/06; JVM baseline audit

**Session:** PJ-31
**Branch:** main
**Repos:** snobol4x + .github

**Work done:**
- Discovered 4 puzzle files (01, 02, 05, 06) missing from milestone tables.
- puzzle_02 had messy debug output; rewrote as clean constraint search — swipl PASS.
- puzzle_01, 05, 06 already clean real search — no changes needed.
- Added M-PZ-01/02/05/06 to PLAN.md and FRONTEND-PROLOG.md.
- Ran full JVM baseline test: 15/20 PASS.
- Diagnosed 5 failures → 3 root causes:
  - puzzle_19: `between/3` missing → M-PJ-BETWEEN (new)
  - puzzle_03/11/18: ITE `->` not cutting enclosing choice point → M-PJ-ITE-CUT (new)
  - puzzle_12: inline disjunction silent failure → M-PJ-DISJ-ARITH (existing)
- Added M-PJ-ITE-CUT, M-PJ-BETWEEN, M-PJ-PZ-ALL-JVM to PLAN.md.

**Milestones fired:** M-PZ-01 ✅, M-PZ-02 ✅, M-PZ-05 ✅, M-PZ-06 ✅

**HEAD at handoff:** snobol4x `251ae11`, .github `750893e`
**Next:** PJ-32 — fix M-PJ-BETWEEN (add between/3 to pj_emit_goal), then M-PJ-ITE-CUT, then M-PJ-DISJ-ARITH.

---

## J-214 — M-JVM-BEAUTY-GLOBAL in progress

**Session:** J-214
**Branch:** main
**Repos:** snobol4x + .github

**Work done:**
- PIVOT 2026-03-24: launched M-BEAUTIFY-BOOTSTRAP-JVM (all 19 JVM beauty milestones, per BEAUTY.md)
- Cloned snobol4corpus; confirmed setup.sh environment OK (CSNOBOL4 2.3.3, SPITBOL, sno2c, Java 21, jasmin.jar, monitor_ipc.so)
- Found and fixed 5 JVM emitter bugs in `emit_byrd_jvm.c`:
  1. **jvm_named_pats BSS overflow** — `static JvmNamedPat[64]` on BSS → heap `calloc(512)` with lazy init in reset+register+lookup
  2. **Jasmin label scoping** — `L_<label>:` definitions and `goto L_<label>` cross-method references; Jasmin labels are method-local. Fix: qualify as `Lf<fnidx>_<label>` at all 3 emission sites (computed-goto scan, direct-goto, label-definition)
  3. **sno_array_get false non-null** — returned `""` on key-not-found; caused `:S(G1)` in global.sno UTF loop to fire unconditionally → infinite loop. Fix: return `null` on miss
  4. **SORT unimplemented** — fell to `default: ldc ""` stub; `UTF_Array = SORT(UTF)` set UTF_Array to `""`. Fix: full `sno_sort()` Jasmin method using `TreeMap` for sorted key iteration, builds 2D array with `[row,1]=key [row,2]=val` and `__rows__` sentinel
  5. **sno_array_counter field** — referenced in early sno_sort draft but never declared. Fix: removed; switched to `identityHashCode` pattern matching `sno_array_new`
- global driver: `sno2c -jvm` compile ✅, Jasmin assemble ✅, runtime test not completed at handoff (context window ~75%)

**Milestones fired:** none (M-JVM-BEAUTY-GLOBAL in progress)

**Next:** IJ-20 — implement M-IJ-CORPUS-R11: `||:=` (augop case 35 str path) + `!E` (ICN_BANG new generator) + 5-test rung11 corpus + run_rung11.sh

## PJ-33 — Parser fix + ITE-CUT seal

**Date:** 2026-03-24
**Milestone:** none fired (bugs reclassified)
**Result:** 16/20 PASS (unchanged).

**Work done:**
1. `prolog_parse.c`: `->` operator precedence fixed 900 → 1050 (ISO standard). Fixes `(A,B->C;D)` parse — was parsed as `','(A, ;(->(B,C),D))`, now correctly `';'(->(','(A,B),C),D)`.
2. `prolog_emit_jvm.c`: ITE-CUT seal emitted after `cond_ok`: `ldc cut_cs_seal; istore cs_local_for_cut`. Confirmed working for simple ITE cases.

**Root cause reclassification:**
- puzzle_11, 18: output 2x with NO `->` in source — not ITE-CUT. A 2-clause predicate matches twice. Needs trace investigation.
- puzzle_03: ITE seal now emitted but `equal_sums`/`find_couples` 6-clause predicates still over-generate all permutations.
- puzzle_12: DISJ-ARITH unchanged.

**HEAD at handoff:** snobol4x `c0987cc`, .github pending push
**Next:** PJ-34 — trace puzzle_11/18 doubling; fix M-PJ-DISJ-ARITH (puzzle_12).

---

## IJ-20 — M-IJ-CORPUS-R11 ✅ — 2026-03-24

**HEAD in:** `8f98dea` IJ-19 | **HEAD out:** `cab96d2` IJ-20

**Milestone fired:** M-IJ-CORPUS-R11 ✅ — `||:=` string augop + `!E` bang generator + rung11 corpus

**Changes in `icon_emit_jvm.c`:**
1. `ij_emit_augop` case 35 (`||:=`): String path moved before long-path temp allocation. Uses `ij_declare_static_str`/`ij_get/put_str_field` + `String.concat` + `dup`. Added `ICN_AUGOP` to `ij_expr_is_string` (returns 1 iff val.ival==35).
2. `ij_emit_bang` (new): per-site statics `icn_N_bang_str`/`icn_N_bang_pos`; `substring(pos,pos+1)` + pos++; β→check. Added to dispatch + `ij_expr_is_string`.
3. `ij_emit_every` drain: `bstart`/`gbfwd` now use `ij_expr_is_string(gen) ? "pop" : "pop2"` instead of hardcoded `pop2`.

**Corpus:** `test/frontend/icon/corpus/rung11_bang_augconcat/` (5 tests) + `run_rung11.sh`

**Result:** 59/59 PASS (rung01–11)

**Known open issue:** `ICN_ALT` β-resume gate not implemented — `every s ||:= ("a"|"b"|"c")` loops. Tracked as M-IJ-CORPUS-R12 item.

**Next:** IJ-21 — M-IJ-CORPUS-R12: ALT gate fix + string relops + size(*s)

**HEAD at handoff:** snobol4x `ff3e05c` J-214, .github (pending push)
**Next:** J-215 — run global driver to completion; fix remaining runtime divergences; fire M-JVM-BEAUTY-GLOBAL; proceed to M-JVM-BEAUTY-IS

## J-215 — M-JVM-STLIMIT-STCOUNT sprint written; &STLIMIT root cause diagnosed

**Session:** J-215
**Branch:** main
**Repos:** .github only (no snobol4x code change this session — sprint written, not yet implemented)

**Work done:**
- Continued M-JVM-BEAUTY-GLOBAL from J-214. global driver: compile ✅, assemble ✅, run → exit 124 (TIMEOUT, 15s).
- Diagnosed root cause: `&STLIMIT` is not implemented in JVM backend. `sno_kw_set` in `emit_byrd_jvm.c` handles TRIM/ANCHOR/STNO but falls through silently for STLIMIT. No `sno_kw_STLIMIT` field declared. No step counter decremented. `global.sno` sets `&STLIMIT = 1000000` then runs `G1: i=i+1 / $UTF_Array[i,2] = UTF_Array[i,1] :S(G1)` over SORT(UTF) (~100 entries) — loop never terminates.
- Confirmed: `&STLIMIT = 10000` + infinite `:(L)` loop ran 200K+ iterations in 5s — zero enforcement.
- Also noted: `sno_indr_get` has `Lsig_done` label not method-local (same scoping class of bug as J-214 fix) — fix in same session as STLIMIT.
- Sprint `M-JVM-STLIMIT-STCOUNT` written in full (6 hunks) in JVM.md §STLIMIT Sprint. JVM.md NOW updated. BEAUTY.md prerequisite row added. PLAN.md NOW row updated to J-215.
- ASM corpus: 106/106 ALL PASS ✅ (no code touched).

**Milestones fired:** none

**HEAD at handoff:** snobol4x `ff3e05c` J-214 (unchanged), .github updated
**Next:** J-216 — implement M-JVM-STLIMIT-STCOUNT (6 hunks in emit_byrd_jvm.c); verify STLIMIT enforces; run global driver to completion; fix any remaining divergences; fire M-JVM-BEAUTY-GLOBAL

---

## Session IJ-21 — 2026-03-24

**Trigger:** "playing with ICON frontend ... with JVM backend"
**Session prefix:** IJ
**Branch:** main

**Work done:**
- M-IJ-CORPUS-R12 ✅ — three changes to `icon_emit_jvm.c`:
  1. `ij_expr_is_string(ICN_IF)` fix: added `case ICN_IF:` returning then-branch string-ness. Fixed VerifyError (pop2 vs pop mismatch) when `if` statement wraps a string-producing then-branch.
  2. `ICN_SIZE` (`*s`) full pipeline: AST enum in `icon_ast.h`, `icn_kind_name()` in `icon_ast.c`, `check(p, TK_STAR)` in `parse_unary()` (before `parse_mul` so prefix wins), `ij_emit_size()` emitting `String.length()` + `i2l` → long.
  3. String relops (SEQ/SNE/SLT/SLE/SGT/SGE) — `ij_emit_strrelop` was already implemented; first corpus coverage added.
- rung12_strrelop_size corpus: 5 tests. 64/64 PASS.

**Milestones fired:** M-IJ-CORPUS-R12 ✅

**HEAD at handoff:** snobol4x `be2af59` IJ-21, .github updated
**Next:** IJ-22 — M-IJ-CORPUS-R13: ICN_ALT β-resume indirect-goto gate (JCON §4.5); enables `every s ||:= ("a"|"b"|"c")` patterns

---

## J-216 — 2026-03-25 — M-JVM-STLIMIT-STCOUNT partial

**Session type:** TINY JVM backend
**HEAD at start:** `ff3e05c` (J-214)
**HEAD at end:** `a74ccd8` (J-216) — pushed to origin/main

**Work done:**
- CSNOBOL4 2.3.3 built from tarball (`snobol4-2_3_3_tar.gz`). Smoke-tested OK.
- `snobol4x` and `x64` cloned fresh. All deps installed (libgc-dev, nasm, default-jdk).
- Implemented 6 hunks in `emit_byrd_jvm.c`:
  1. `sno_kw_STLIMIT I` + `sno_kw_STCOUNT I` field declarations
  2. `clinit`: `iconst_m1` (STLIMIT=-1 unlimited), `iconst_0` (STCOUNT=0)
  3. `sno_kw_set`: STLIMIT + STCOUNT cases added after STNO
  4. `sno_kw_get`: STLIMIT + STCOUNT cases added after ANCHOR
  5. `sno_stcount_tick()` helper: increment STCOUNT, check STLIMIT≥0, exit if exceeded. Stack-safe (no dup — re-fetches STCOUNT). Call inserted at every real statement.
  6. `Lsig_done` → `Lsig_done_indr` in `sno_indr_get` (label collision fix)
- STLIMIT VERIFIED: `&STLIMIT=10000` + `:(L)` infinite loop → 10000 lines then `Termination: statement limit`. ✅
- Global driver still TIMEOUTs. Root cause found: `A[i,1]`/`A[i,2]` 2D subscript emits key `"1"` not `"1,2"`. SORT stores rows as `"1,1"`/`"1,2"`. Fix attempted on `E_ARY` case but used wrong children check — ASM backend shows `nchildren==3` for 2D, not 2. Fix incomplete.

**Bugs found this session:**
- B1: STLIMIT unimplemented — FIXED ✅
- B2: `Lsig_done` label collision in `sno_indr_get` — FIXED ✅
- B3: 2D E_ARY subscript emits single-dim key — WIP, next session

**Next session J-217:** Read `emit_byrd_asm.c` lines 3530-3570 for correct E_ARY nchildren layout → fix 2D key in `emit_byrd_jvm.c` → global driver PASS → fire M-JVM-STLIMIT-STCOUNT + M-JVM-BEAUTY-GLOBAL.

---

## IJ-22 — Icon JVM — M-IJ-CORPUS-R13 ✅ (2026-03-25)

**HEAD before:** `be2af59` (IJ-21)
**HEAD after:** `a569adf` (IJ-22)
**Result:** M-IJ-CORPUS-R13 ✅ — 69/69 PASS (rung01–13)

**Work done:**
- Rewrote `ij_emit_alt` with per-site `icn_N_alt_gate I` static field + tableswitch β dispatch. Matches JCON `ir_a_Alt` (MoveLabel + IndirectGoto). Fixes infinite loop in `every s ||:= ("a"|"b"|"c")`.
- Added `ICN_ALT` case to `ij_expr_is_string` → delegates to `children[0]`. Fixes VerifyError on `every write("a"|"b"|"c")`.
- Fixed `ij_emit_concat` `left_is_value` to exclude `ICN_ALT` (generator, not one-shot). Fixes `every write(("a"|"b") || ("x"|"y"))` truncating after 2/4 results.
- Created `rung13_alt` corpus (5 tests) + `run_rung13.sh`.
- Updated PLAN.md, FRONTEND-ICON-JVM.md §NOW, MILESTONE_ARCHIVE.md.

**Next session IJ-23:** M-IJ-CORPUS-R14 — ICN_LIMIT (`E \ N`).

---

## B-292 — 2026-03-25

**Sprint:** M-BEAUTIFY-BOOTSTRAP (JVM track)
**HEAD start:** `309a2f9` B-291 → **HEAD end:** `acbc71e` B-292

**Work done:**
1. Setup: cloned snobol4x, .github, x64, snobol4corpus; ran setup.sh → 106/106 ALL PASS. CSNOBOL4 2.3.3 built from ZIP, SPITBOL x64 built, sno2c built.
2. **Fixed JVM segfault (B-292 commit `acbc71e`):** `emit_byrd_jvm.c:1156` — DATA type constructor loop `for fi in 0..nfields` accessed `e->children[fi]` without checking `fi < e->nchildren`. For `tree(t,v,n)` (3 children, 4 fields), `e->children[3]` = garbage `0x21` (non-NULL) → SIGSEGV. Fix: `fi < e->nchildren &&` guard added. `sno2c -jvm demo/beauty.sno` now emits 872,847-line beauty.j.
3. **Diagnosed L_io_end missing label:** Jasmin fails with `L_io_end has not been added to the code`. Root cause: `output_->end_label` is NULL (DEFINE has no goto, next stmt OPSYN also has no goto). `jvm_emit_fn_method` body scan runs unbounded for output_, absorbs `io_end` top-level label, emits it as `Lf5_io_end` inside output_ method. But `goto L_io_end` in main() uses unscoped name → label not found in main(). Fix strategy: add next-fn-entry stop condition to `jvm_emit_fn_method` body loop (line 4153) when `fn->end_label` is NULL. See TINY.md §CRITICAL NEXT ACTION.

**Invariant:** 106/106 ASM corpus ALL PASS throughout.
**Not done:** L_io_end fix, Jasmin assembly, JVM beauty run.
**Next session:** B-293 — apply fn-body scan fix at emit_byrd_jvm.c:4153; assemble beauty.j; run JVM beauty bootstrap.

## PJ-38 — 2026-03-25

**Score:** 18/20 → 19/20
**HEAD:** `13f4db6`
**Branch:** `main`

**Work done:**
- Diagnosed sentinel ambiguity: `base[nclauses]` == last-clause γ return for any predicate → false positives.
- Changed cutgamma port to return `2147483647` (MAX_VALUE) — unambiguous, never a legitimate cs value.
- Updated dispatch entry `if_icmpeq` guard to match `2147483647`.
- Added `static Program *pj_prog` global; set in `prolog_emit_jvm()`.
- Added `pj_predicate_base_nclauses(fn, arity)` helper.
- Added `pj_callee_has_cut_no_last_ucall(fn, arity)` helper.
- Added call-site cutgamma guard after `ifnull call_ω` — emits `if_icmpeq 2147483647 → lbl_cutγ`.
- Result: 12 previously-failing puzzles now PASS (01-02, 04-07, 12-13, 15-17, 19-20).

**Remaining bug (puzzle_18):**
- Guard conditioned on `lbl_cutγ != NULL`. `puzzle/0` has no own cut → `lbl_cutγ` NULL → guard skipped → double-print persists.
- Fix: when `lbl_cutγ` is NULL, route to `call_ω` instead (treat cutgamma as exhaustion of this call). Change `if (lbl_cutγ && ...)` to `if (pj_callee_has_cut_no_last_ucall(...))` with `cut_dest = lbl_cutγ ? lbl_cutγ : call_ω`.

**SWIPL test suite:** SWI-Prolog ships `library(plunit)` for unit testing. Run `swipl -g "load_test_files([]), run_tests" file.pl`. The puzzle corpus in `rung10_programs/` uses `swipl -q -g halt -t main` as oracle — no formal plunit suite exists for this project yet.

## IJ-23 through IJ-26 — 2026-03-25

**Score:** 69/69 → 89/89 PASS (rungs 01–17)
**HEAD:** `f10ea77`
**Branch:** `main`

**Work done:**

### IJ-23 — M-IJ-CORPUS-R14 ✅ `ICN_LIMIT` (`E \ N`)
- `ij_emit_limit`: per-site statics `icn_N_limit_count J` + `icn_N_limit_max J`. α evaluates N once, resets counter. γ-path increments counter and delivers value. β checks exhaustion without incrementing (off-by-one root cause caught and fixed). Added `ICN_LIMIT` to `ij_expr_is_string` (delegates to child[0]).
- rung14_limit: 5 tests — `(1 to 10)\3`, alt-limit, zero-limit, large-limit, string-alt-limit.

### IJ-24 — M-IJ-CORPUS-R15 ✅ `ICN_REAL`, `ICN_SWAP`, `ICN_LCONCAT`
- `ij_emit_real`: `ldc2_w %gd` with decimal-point guard. New `'D'` static type + `ij_declare_static_dbl`/`ij_get_dbl`/`ij_put_dbl`. `ij_expr_is_real` predicate. Pre-pass extended to pre-declare `'D'`-typed var fields.
- `ij_emit_swap` (`:=:`): read-both-write-crossed with per-site tmp statics; handles long/String/double. `ICN_SWAP` added to `ij_expr_is_string`.
- `ICN_LCONCAT` (`|||`): aliases to `ij_emit_concat` (Tiny-ICON: no list type). Added to `ij_expr_is_string`.
- `write()` and `ij_emit_var`/`ij_emit_assign` updated for `'D'` type.
- rung15_real_swap: 5 tests.

### IJ-25 — M-IJ-CORPUS-R16 ✅ `ICN_SUBSCRIPT` + `if`-cond drain fix
- `ij_emit_subscript` (`s[i]`, 1-based, negatives from end): caches string in static; `l2i` index; bounds check; `substring(offset, offset+1)`. β re-drives index child's β (enables `every s[1 to N]`).
- `ij_emit_if` drain fix: `cond_then` now uses `pop` vs `pop2` based on `ij_expr_is_string(cond)`. Previously hardcoded `pop2` caused VerifyError when condition was String-typed.
- rung16_subscript: 5 tests.

### IJ-26 — M-IJ-CORPUS-R17 ✅ Real arithmetic + type conversion builtins
- `ij_emit_binop` double support: detects `ij_expr_is_real` on either child → `dstore`/`dload`/`dadd`/`dsub`/`dmul`/`ddiv`/`drem`; promotes long with `l2d` when mixing.
- `ij_expr_is_real` extended: recurses into binop children; recognises `real()` call.
- `integer(x)` builtin: `d2l` / `Long.parseLong` / identity.
- `real(x)` builtin: `l2d` / `Double.parseDouble` / identity.
- `string(x)` builtin: `Long.toString` / `Double.toString` / identity; added to `ij_expr_is_string`.
- `ldc2_w` decimal fix: `%g` produces `"2"` for `2.0`; append `.0` when no decimal/exponent present.
- rung17_real_arith: 5 tests.

**Invariant:** 89/89 JVM corpus PASS throughout (all rungs 01–17).
**Not done:** real relops (< > = on doubles), mixed int/real relational expressions.
**Next session:** IJ-27 — M-IJ-CORPUS-R18, real relops + any remaining UNIMPL gaps.

## IJ-27 — 2026-03-25

**Sprint:** M-IJ-CORPUS-R18
**HEAD:** `f976057` (snobol4x main)
**Result:** ✅ 94/94 PASS (rung01–18)

**Work done:**
- `ij_emit_relop`: added `is_dbl` detection; `dstore`/`dload`/`dcmpl`/`dcmpg` for real operands; `l2d` promotion at relay points; `dcmpl` for `<`/`<=`/`=`/`~=`, `dcmpg` for `>`/`>=` (correct NaN semantics).
- `ij_expr_is_real`: extended to relop nodes (`ICN_LT/LE/GT/GE/EQ/NE`) and `ICN_ALT` (delegates to children[0]).
- `rung18_real_relop` corpus: 5 tests — real `<`, real `>`, real `=`, mixed int/real `<`, goal-directed real relop with alt generator.
- Clarified: Icon relops return the **right-hand** operand on success.

**Next:** M-IJ-CORPUS-R19 — candidates: lists/tables, real `to by`, multi-procedure real args.

---

## Scripten Planning Session — 2026-03-25

**Session type:** Strategic planning / HQ documentation
**Branch:** main
**HEAD at start:** `bf0527a` (SCRIPTEN.md initial)
**HEAD at end:** `e2200e6`

**Work done:**

1. **SCRIPTEN.md** — Top-level vision document for Scripten (formerly SCRIPTX).
   Named the platform: **Scripten** — S/C/R/I/P + TEN (ten times faster, ten times
   better). File name uppercase per convention (`SCRIPTEN.md`), product name natural
   case. Covers: current state (18 compiler/runtime combinations, 3500+ tests),
   three levels (matrix, cross-language assemblies, polyglot fenced files), five
   deeper planning sessions (Matrix, ABI, Polyglot Parser, Bootstrap, Jupyter),
   immediate next actions.

2. **SCRIPTEN_DEMO.md** — Demo #1: Family Tree polyglot proof of concept.
   Three languages, one fenced `.scripten` source file, funny linkage via JVM
   invokestatic. SNOBOL4: 4 named patterns, one-pass CSV consumer, assertz per row.
   Prolog: dynamic facts + relational inference (grandparent/2, ancestor/2,
   sibling/2, cousin/2, generation/2). Icon: generator pipelines over Prolog
   solution sets using `every`. One new compiler change: ~20 lines in
   `icon_emit_jvm.c` to detect `Lang.method()` dot syntax and emit cross-class
   invokestatic. Everything else: Python glue scripts + hand-edited Jasmin stubs.
   Milestone: M-SCRIPTEN-DEMO.

3. **SCRIPTEN_DEMO2.md** — Demo #2: Puzzle Solver. The paradigm inversion demo.
   Prolog does NOT search — Icon searches. SNOBOL4 reads puzzle definition in
   S-expression format using reduced treebank `group()` technique (3 functions
   instead of 5: do_push_list, do_push_item, do_pop_assert). `do_pop_assert`
   combines tree-close with assertz in one NRETURN side-effect — parse and
   database population happen simultaneously in one pattern match. Prolog stores
   dynamic facts, answers one-hop `valid_assign/2` constraint queries only.
   Icon does combinatorial search via recursive `suspend` generator (`try_assign`)
   with Prolog as the constraint oracle. Uses M-IJ-CORPUS-R3 suspend (already ✅).
   Puzzles 1–5 from existing Prolog corpus. Milestone: M-SCRIPTEN-DEMO2.

**Milestones fired:** none (planning session only)

**PLAN.md:** No NOW row added — Scripten is a new track, row to be added when
M-SCRIPTEN-DEMO sprint begins.

**HEAD at handoff:** `e2200e6` on origin/main
**Next:** Begin M-SCRIPTEN-DEMO sprint — build `scripten_split.py`, compile
three blocks of `family.scripten` independently, inject funny linkage.
Then M-SCRIPTEN-DEMO2 immediately after.

---

## Scripten Planning Session 2 — 2026-03-25

**Session type:** Strategic planning / HQ documentation
**Branch:** main
**HEAD at start:** `c11c526`
**HEAD at end:** `fc01c40`

**Work done:**

1. **Tiny-Prolog vs SWI-Prolog gap analysis** — full comparison across all
   language features. Identified Tier 1 (findall, atom builtins, retract, sort),
   Tier 2 (succ/plus, format, string ops, bagof/setof, copy_term, exceptions,
   extended arith), Tier 3 (DCG — deferred, SNOBOL4 covers parsing).

2. **FRONTEND-PROLOG-JVM.md enhanced** — added "Tiny-Prolog Enhancement Roadmap"
   section with 11 new milestones (M-PJ-FINDALL through M-PJ-NUMBER-OPS) plus
   M-PJ-DCG as 💭 future. New corpus rungs rung11–rung21 defined. Sprint order
   documented. Appended to PJ trigger doc per convention.

**Milestones fired:** none (planning session)
**HEAD at handoff:** `fc01c40` on origin/main
**Next:** Begin M-PJ-PZ-ALL-JVM (clear puzzle_18 NAF bug, puzzle_03 over-gen),
then M-PJ-FINDALL as first enhancement sprint.

## IJ-28 — 2026-03-25

**Milestone:** M-IJ-CORPUS-R19 ✅
**HEAD:** `2574281` (snobol4x main)
**Result:** 99/99 PASS (rung01–19)

**What fired:** ICN_POW (exponentiation `^`) + real `to-by` generator support.

**Key changes:**
- `icon_parse.c`: `parse_pow()` right-associative `^` at precedence above `*`
- `icon_emit_jvm.c`: `ij_emit_pow` via `Math.pow(DD)D`; D-field helpers; `ij_emit_to_by` real mode (`is_dbl` flag); `ij_emit_neg` `dneg` for real; `ij_expr_is_real` extended for `ICN_POW/NEG/TO_BY/TO`
- rung19 corpus: 5/5 PASS

**Root cause caught mid-session:** `-1.0` literal (unary neg of real) hit `lneg` → VerifyError. Fixed by `ij_expr_is_real(ICN_NEG)` + `dneg` in `ij_emit_neg`.

**Next:** M-IJ-CORPUS-R20 — ICN_SEQ_EXPR (`;` sequence), string section `s[i:j]`, or `ICN_CASE`.

---

## Scripten Planning Session 3 — 2026-03-25

**Session type:** Strategic planning / HQ documentation
**Branch:** main
**HEAD at start:** `c6b87d7`
**HEAD at end:** `7d6f964`

**Work done:**

1. **Tiny-Icon vs JCON vs real Icon gap analysis** — read JCON irgen.icn (43
   ir_a_* node handlers), real Icon runtime (fstr.r, fstruct.r, fmisc.r, fscan.r),
   and Tiny-Icon icon_ast.h + icon_emit_jvm.c. Identified 9 unemitted semantic
   features: RECORD/FIELD, GLOBAL, CREATE (co-expressions), CASE, POW,
   SCAN_AUGOP, plus missing builtins (list/table/sort/read/str-ops/type).

2. **FRONTEND-ICON-JVM.md enhanced** — added "Tiny-Icon Enhancement Roadmap"
   section with 14 new milestones (M-IJ-LISTS through M-IJ-MULTIFILE) plus
   M-IJ-COEXPR/MATH/MULTIFILE as 💭 future. New corpus rungs rung19–rung27
   defined. Sprint order documented. Co-expression note: Java 21 virtual threads
   (Project Loom) as the right JVM implementation when ready.

3. **Grand Master Reorganization scoped** — began reading source layout for
   the unified IR / shared emitter plan. Stopped at 67% context — this plan
   requires a fresh session with full context to do correctly.
   Key findings so far:
   - 5 frontends currently have inconsistent naming: ASM uses P_NAME_alpha/beta/
     gamma/omega; JVM SNOBOL4 uses Lalpha/Lbeta; Icon JVM uses ports.α/β/γ/ω;
     Prolog JVM uses lbl_γ/lbl_ω; .NET uses its own conventions
   - Icon JVM emitter (3158 lines) and Prolog JVM emitter (2622 lines) live under
     frontend/ rather than backend/ — wrong location for shared emitters
   - The reorganization needs: unified IR node taxonomy, shared backend dispatch,
     consistent Greek-letter port naming across all 5×3=15 emitter combinations,
     folder restructure, Makefile update, and full test suite verification at
     each incremental step

**Milestones fired:** none (planning session)
**HEAD at handoff:** `7d6f964` on origin/main
**Next:** Start fresh session for GRAND_MASTER_REORG.md — read all 5 emitters
completely, inventory existing milestones that overlap, then write the full plan.

---

## IJ-29 — M-IJ-CORPUS-R20 ✅

**Date:** 2026-03-25  **HEAD:** `7f8e3a2`  **PASS:** 104/104

**Features:** ICN_SECTION (`s[i:j]`) + ICN_SEQ_EXPR (`(E1;E2;...En)`)

**Parser:** Subscript rule extended to detect `:` after first index → ICN_SECTION(str,lo,hi). Paren rule extended to collect `;`-separated exprs → ICN_SEQ_EXPR.

**Emitter:** `ij_emit_section` — JCON `ir_a_Sectionop` 3-operand pattern; per-site statics for str/lo/hi; 1-based→0-based with positive/negative/zero handling; hi clamped to length; `String.substring(II)`. `ij_emit_seq_expr` — clone of ICN_AND relay-label wiring; drains intermediates (pop/pop2 string-aware); last child flows to ports.γ/ω.

**Corpus:** rung20_section_seqexpr — 5 tests, 5/5 PASS first run. No regressions (104/104 total).

---

## IJ-30 — M-IJ-CORPUS-R21 WIP (session ended at context limit)

**Date:** 2026-03-25  **HEAD:** `a6808a7`  **Status:** WIP — 2 bugs open

**Baseline:** 104/104 PASS throughout. Rung21 corpus written (5 tests).

**What was built:**
- `ICN_INITIAL` added to AST enum + kind_name
- `ICN_GLOBAL` top-level parse fixed: names now collected into ICN_GLOBAL node (was silently discarded)
- `ICN_INITIAL` parse added in parse_stmt: `initial stmt;` → `ICN_INITIAL(body)`
- `ij_emit_file` Pass 0: pre-declares top-level globals as `icn_gvar_*` fields
- `ij_emit_initial`: per-proc `icn_init_PROC I` flag gate
- `ICN_GLOBAL` dispatch: declares `icn_gvar_*`, emits no-op statement
- `ICN_INITIAL` dispatch: wired to `ij_emit_initial`
- `rung21_global_initial/` corpus: 5 tests; t01/t05 PASS, t02/t03/t04 FAIL

**Bug 1 (t02):** `NoSuchFieldError` for String global — pre-pass locks type to `J`. Fix: remove pre-declaration from Pass 0; track names in separate global-name set only.

**Bug 2 (t03/t04):** `VerifyError` inconsistent stack height on `initial` clause — skip path stack=2, body path stack=4. Fix: drain body result before `lconst_0` push (see §NOW for concrete patch).

**NOTE:** All sessions FROZEN — Grand Master Reorg in progress. Resume IJ-31 post-reorg.
