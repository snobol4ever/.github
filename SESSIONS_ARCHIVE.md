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
