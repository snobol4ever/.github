# MILESTONE-NET-SNOBOL4.md — SNOBOL4 × .NET Milestone Ladder

**Session:** D · **Repo:** snobol4dotnet · **Runtime:** Jeff Cooper's C# pipeline
**Invariant cell:** `dotnet test` 1911/1913 · **Crosscheck:** 79/80 (@N bug)

---

## Organizing principle: the 5-phase statement executor

`stmt_exec.c` defines SNOBOL4 execution as five explicit phases.
`ThreadedExecuteLoop.cs` implements the same five phases implicitly in a
single opcode dispatch loop — with no clean phase boundaries.  Bugs like the
`@N` cursor-capture overwrite are a direct consequence of Phase 3 captures
sharing state with Phase 5 cleanup.

```
Phase 1: build_subject  — resolve subject variable, set Σ/Δ/Ω for match
Phase 2: build_pattern  — AbstractSyntaxTree.Build(pattern) → node graph
Phase 3: run_match      — Scanner.Match() trampoline, collect captures
Phase 4: build_repl     — replacement already eval'd by opcode sequence
Phase 5: perform_repl   — splice into subject, flush captures, :S/:F branch
```

---

## Architecture notes (D-165 survey)

Jeff's implementation is already remarkably complete — this is a quality
audit and gap-fill, not a rewrite.

### EVAL and CODE: self-hosted, no Roslyn

`BuildEval()` / `BuildCode()` route back through the **same compiler pipeline**
that compiled the original program: `ReadCodeInString` → `Lex` → `Parse` →
`ResolveSlots` → `EmitMsilForAllStatements` → `CompileStarFunctions`.

`CODE` uses `AppendCompile` to live-patch the running `Instruction[]` thread —
the old `Halt` is replaced with a guard `Jump` and new statements are stitched
on.  This is a live-patching threaded interpreter (closer to Forth than to
anything else in the SNOBOL4 world).  No Roslyn needed — the self-hosted
pipeline is the compiler.

### Pattern engine: already a Byrd box graph

`AbstractSyntaxTreeNode` / `Scanner` / `Pattern` is already a dynamic Byrd
box graph.  Jeff didn't use that name but the mapping is exact:

| Byrd box concept | Jeff's equivalent |
|---|---|
| α port | `TerminalPattern.Scan()` — enters node, tries to match |
| β / backtrack | `_state.RestoreAlternate()` — pops saved alternate node |
| γ / success continuation | `node.GetSubsequent()` — follows `Subsequent` index |
| ω / failure continuation | `MatchResult.Failure` → alternate stack pop |
| Box graph construction | `AbstractSyntaxTree.Build(pattern)` |
| Trampoline | `Scanner.Match()` — `while(true)` with Subsequent/alternate dispatch |

`ArbNoPattern.Scan` re-enters the trampoline recursively (≡ `bb_arbno`).
`UnevaluatedPattern.Scan` evaluates its `DeferredCode` delegate — running
the pre-compiled `StarFunctionList` entry — then matches the result.  This is
`*pattern` working correctly via the existing machinery.

### ExpressionVar / DeferredCode / StarFunctionList

When the parser sees a pattern argument containing a variable or expression
(e.g. `ARBNO(*Command)`), it wraps it as an `ExpressionVar` with a
`DeferredCode` delegate pointing into `StarFunctionList`.  At match time,
`UnevaluatedPattern.Scan` calls the delegate — re-running the compiled
expression in the live `Executive` context — gets a `PatternVar`, then
recursively matches it.  Runtime pattern composition with zero external
compilation.

### @N bug anatomy (Phase 3/5 ordering)

`CursorAssignmentPattern.Scan` writes `IdentifierTable["N"] = cursor`
during Phase 3 (match) — verified correct by sentinel.  Something in
`ThreadedExecuteLoop`'s `Init` or `Finalize` opcode (or `CheckGotoFailure`)
resets match state and clobbers it.

**Most likely cause:** `Init` snapshots pre-match variable state; `Finalize`
or `CheckGotoFailure` restores it on the failure path — and capture writes
are within that snapshot window.

In `stmt_exec.c` this is solved by an explicit pending-capture list flushed
only in Phase 5 on `:S`.  The .NET fix is analogous: identify the opcode
doing the clobber, guard it so Phase 3 capture writes survive into Phase 5.

---

## Phase A — Correctness: fix Phase 3/5 capture boundary

### M-NET-P35-FIX — @N cursor capture survives Phase 5

**Depends on:** D-164 baseline (1911/1913, 79/80 crosscheck)
**Scope:**
- Add sentinel `Console.Error.WriteLine($"N={IdentifierTable[\"N\"]}")` before
  and after `CheckGotoFailure`, `Init`, `Finalize` in `ThreadedExecuteLoop`
- Run `strings/cross` — identify which opcode writes `N=0` after
  `CursorAssignmentPattern.Scan` correctly writes cursor
- Fix: guard that opcode so Phase 3 capture writes are not clobbered
- Confirm `X ? @N ANY('B')` produces correct N

**Gate:** crosscheck 80/80 ✅ · `dotnet test` ≥1911/1913 ✅

---

### M-NET-POLISH — Cross-test clean + diagnostics + benchmark

**Depends on:** M-NET-P35-FIX
**Scope:**
- 106/106 corpus crosscheck via harness (all rungs)
- diag1 35/35 regression suite
- Benchmark grid (ARCH-testing.md)

**Gate:** 106/106 crosscheck ✅ · diag1 35/35 ✅ · benchmark published ✅

---

## Phase B — Coverage: audit Phase 2/3 pattern gaps

### M-NET-PAT-CAPTURES — Phase 3 capture completeness

**Depends on:** M-NET-POLISH
**Rationale:** After the Phase 3/5 fix, audit all three capture operators
against `stmt_exec.c`'s pending-capture-list semantics.

**Oracle:** `stmt_exec.c` capture-flush section + `CursorAssignmentPattern`,
`ConditionalVariableAssociationPattern`, `DollarSign` (immediate capture).

**Scope:**
- `@var` cursor capture — fixed by M-NET-P35-FIX, confirm clean
- `.var` conditional capture — flush only on `:S` path
- `$var` immediate capture — write on each match advance
- Run rung9 capture tests vs SPITBOL oracle

**Gate:** rung9 capture tests match SPITBOL oracle 100% ✅

---

### M-NET-PAT-PRIMITIVES — Phase 2 pattern primitive audit

**Depends on:** M-NET-PAT-CAPTURES
**Scope:**
- Run full pattern corpus (rung2–rung9) vs SPITBOL oracle
- Audit each of: LEN POS RPOS TAB RTAB REM ANY NOTANY SPAN BREAK BREAKX
  FENCE FAIL SUCCEED ABORT BAL — `TerminalPattern.Scan` vs x86 reference
- Fix each delta; add corpus tests for any gap

**Gate:** rung2–rung9 all pass vs SPITBOL oracle ✅ · `dotnet test` ≥1913/1913 ✅

---

## Phase C — Advanced: CODE/EVAL completeness + bootstrap

### M-NET-EVAL-COMPLETE — EVAL/CODE edge cases

**Depends on:** M-NET-PAT-PRIMITIVES
**Rationale:** `BuildEval` / `BuildCode` exist and work for the common case.
This milestone audits edge cases: EVAL of a pattern expression, CODE'd blocks
that use captures, EVAL inside a pattern context (e.g. `ARBNO(EVAL(expr))`).

**Oracle:** `UnevaluatedPattern.Scan` + `ExpressionVar` + `StarFunctionList`
machinery already in place.  `DeferredExpression = true` routing in
`ReadCodeInString`.

**Scope:**
- Run `corpus/crosscheck/rung10/1016_eval.sno` vs SPITBOL oracle
- Confirm `CODE()` across statement boundaries (label resolution in
  `AppendCompile` jump patching)
- Confirm `EVAL()` inside pattern context routes through
  `UnevaluatedPattern` correctly
- Fix any gaps

**Gate:** rung10 1016_eval PASS ✅ · CODE corpus tests pass ✅

---

### M-NET-NRETURN — NRETURN lvalue-assign

**Depends on:** M-NET-EVAL-COMPLETE
**Rationale:** NRETURN lvalue-assign (`ref_a() = 26`) is the .NET equivalent
of the DYN-41/42 x86 interpreter bug.  The fix strategy from DYN-42 (Option A:
parser skip-whitespace before `(`, or Option B: interpreter write-through guard)
applies here.  Wait for DYN-42 to land; adopt the winning option.

**Oracle:** DYN-42 committed fix in `scrip-interp.c` / `parse_expr17`.

**Scope:**
- Run `corpus/crosscheck/rung10/1013_func_nreturn.sno` vs SPITBOL oracle
- Port the DYN-42 fix to C# (`Parser.cs` or `ThreadedExecuteLoop.cs`)

**Gate:** rung10 1013_func_nreturn PASS ✅

---

### M-NET-SNOCONE — Snocone self-test

**Depends on:** M-NET-NRETURN
**Gate:** Snocone self-test ✅

---

### M-NET-BOOTSTRAP — snobol4dotnet compiles itself

**Depends on:** M-NET-SNOCONE
**Gate:** Self-hosting bootstrap ✅

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| D-165 | M-NET-P35-FIX | Trace @N clobber · fix Phase 3/5 boundary |
| D-166 | M-NET-POLISH | 106/106 crosscheck · diag1 · benchmark |
| D-167 | M-NET-PAT-CAPTURES | Capture audit: @/./$  vs stmt_exec.c |
| D-168 | M-NET-PAT-PRIMITIVES | 16 primitives vs SPITBOL oracle |
| D-169 | M-NET-EVAL-COMPLETE | EVAL/CODE edge cases + rung10/1016 |
| D-170 | M-NET-NRETURN | NRETURN lvalue (follow DYN-42) |
| D-171 | M-NET-SNOCONE | Snocone self-test |
| D-172 | M-NET-BOOTSTRAP | Self-hosting bootstrap |

---

## How ThreadedExecuteLoop relates to stmt_exec.c

| Aspect | x86 (`stmt_exec.c`) | .NET (`ThreadedExecuteLoop.cs`) |
|--------|---------------------|---------------------------------|
| Phase 1 subject | `NV_GET_fn` → `spec_t` | `IdentifierTable[slot]` → string |
| Phase 2 pattern | `PATND_t*` → bb graph | `AbstractSyntaxTree.Build()` → node array |
| Phase 3 drive | C goto trampoline | `Scanner.Match()` while-loop |
| Phase 4 repl | `DESCR_t` already eval'd | opcode-evaluated stack value |
| Phase 5 splice | `memmove` + `NV_SET_fn` | subject assign + `CheckGotoFailure` |
| Captures | pending list, flush on :S | direct `IdentifierTable` write — **Phase 3/5 bug here** |
| EVAL/CODE | `eval_code.c` + re-entry | `BuildEval`/`BuildCode` self-hosted pipeline |
| *pattern | `bb_unevaluated` box | `UnevaluatedPattern.Scan` + `DeferredCode` delegate |

---

*MILESTONE-NET-SNOBOL4.md — rewritten D-165, 2026-04-02, Claude Sonnet 4.6.*
*Architecture survey complete. Pattern engine = Byrd boxes already. EVAL/CODE self-hosted.*
*@N = Phase 3/5 capture boundary bug. Milestones are audit+gap-fill, not rewrite.*
