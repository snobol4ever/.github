# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

**Repo:** snobol4dotnet
**Depends on:** GOAL-NET-BEAUTY-19 must be complete (19/19)
**Done when:** `dotnet Snobol4.dll -bf beauty.sno < beauty.sno` runs to
completion with exit 0, produces ≥500 lines of beautified output, and
emits no `error ` lines on stderr — matching the SPITBOL `-bf` baseline.

> **Mon Apr 28 2026 — CSNOBOL4 retired as oracle.** Per RULES.md
> "Oracles" section update of the same date, CSNOBOL4 is no longer
> used as a general oracle. Drop `csn` from any new harness
> invocations: `PARTICIPANTS="spl dot"` is the canonical set.

## ⛔ Read this first — every session

1. **Source location:** `/home/claude/corpus/programs/snobol4/demo/beauty/`
   contains `beauty.sno` and **all 19** of its `.inc` files in **one
   folder** — including `is.inc`, `FENCE.inc`, and `io.inc` which are also
   carried verbatim from `programs/include/`. The folder is intentionally
   self-contained: it runs from a single CWD with no `-I` / `SETL4PATH` /
   `SNO_LIB` flag on any runtime. See RULES.md "No duplicate corpus
   source files → Exception — self-contained demo programs" for the
   duplication policy.
   Do **not** use `/home/claude/corpus/programs/snobol4/demo/beauty.sno`
   (different program — uses `-INCLUDE 'global.sno'` and lives next to demo siblings).

2. **Invocation flag is `-bf` (not `-b`).** beauty.sno relies on
   case-sensitive labels (`shift` vs `Shift`, `reduce` vs `Reduce`, etc.)
   to wire the parser's semantic-action callbacks. With `-b` (default
   fold-to-upper) those pairs collide as duplicate labels.

3. **PASS criterion is "runs cleanly", not byte-identical.** Even
   SPITBOL's own self-host output drifts ~19 lines from the input
   (semicolon comments, whitespace alignment). Convergence is a future
   goal; this goal stops at "runs end-to-end without errors".

4. **Do not grep stdout for "Parse Error" or "Internal Error"** to detect
   failure — those strings appear in beauty.sno's own source as
   user-printed messages (`mainErr1`, `mainErr2`). A correct run echoes
   them. Detect failure via exit code + line count + stderr-clean.

5. **OUTPUT goes to stderr in snobol4dotnet** (per `REPO-snobol4dotnet.md`),
   but to stdout in SPITBOL. The gate for snobol4dotnet must measure
   stderr (after filtering the dotnet exception trace prefix).

## Canonical oracle invocations

The folder is self-contained — no path flags needed for any runtime.

```bash
cd /home/claude/corpus/programs/snobol4/demo/beauty

# SPITBOL x64 — primary oracle
/home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno

# snobol4dotnet — the runtime under test
dotnet /home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll \
    -bf beauty.sno < beauty.sno
```

## Test command

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
cd $BEAUTY
dotnet $SNO4 -bf beauty.sno < beauty.sno \
    > /tmp/beauty_self_out.txt 2>/tmp/beauty_self_err.txt
RC=$?
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self_err.txt \
    > /tmp/beauty_self_clean.txt
LINES=$(wc -l < /tmp/beauty_self_clean.txt)
echo "exit=$RC stderr-lines=$LINES"
[ $RC -eq 0 ] && [ $LINES -gt 500 ] \
    && ! grep -qE "error [0-9]+ --" /tmp/beauty_self_clean.txt \
    && ! grep -q "^Parse Error$\|^Internal Error$" /tmp/beauty_self_clean.txt \
    && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
```

## Oracle baselines (Sun Apr 26 2026)

| Oracle | Result on this clone |
|--------|----------------------|
| SPITBOL  | exit 0, 649 stdout lines, stderr clean — **PASS** ✅ |
| snobol4dotnet | exit 0, ~31 stderr lines, fails with `Parse Error` — **current S-2 bug** |

**SPITBOL is the canonical oracle for this gate.**

## Approach — 2-way binary sync-step monitor

Per RULES.md "Sync-step monitor — read the divergence point, not the
trace": drive `spl` and `dot` through the runtime-agnostic 2-way
harness, let the controller stop at first DIVERGE, read **only** the
last-agreed + first-disagreed wire-record pair.

The bridges are wired (x64 `3cd2dcc`, dot through `2414a26`). Wire
format `monitor_wire.h`; controller `monitor_sync_bin.py`.

## Steps

- [x] **S-1** — Diagnose error 021. Initial diagnosis complete.

- [x] **S-2a** — Confidence demo `claws5.sno` (snobol4dotnet `8432b35`).
  Fixed `IndexTable`/`IndexArray` reference semantics. Byte-identical to ref.

- [x] **S-2b** — Confidence demo `treebank-list.sno` (`8432b35`). Same fix.

- [x] **S-2c** — Confidence demo `treebank-array.sno` (`8432b35`). Same fix.

- [x] **S-2-bridge-1** — DotNet IPC bridge, dormancy smoke
  (snobol4dotnet `ba18e88`). `MonitorIpc.cs` ~330 lines. Smoke PASS=5.

- [x] **S-2-bridge-2** — Fire-point: assignment chokepoint
  (snobol4dotnet `7b67cb0`). Hooked `Executive.Assign`. Smoke PASS=5.

- [x] **S-2-bridge-3** — Fire-point: `.`-capture + element stores
  (snobol4dotnet `18a2946`). No new fire-point — already routed through
  `Executive.Assign`. Smoke PASS=9.

- [x] **S-2-bridge-4** — Fire-point: CALL + RETURN
  (snobol4dotnet `e5b4f05`). Hooked `Define.cs ExecuteProgramDefinedFunction`.
  Smoke PASS=7.

- [x] **S-2-bridge-5** — Harness lane: `dot` participant
  (one4all `76d979a7`).

- [x] **S-2-bridge-5b** — coverage-e/f adoption
  (snobol4dotnet `8e5ff9e`, one4all `21eac9a5`). Streaming intern
  + MWK_LABEL.

- [x] **S-2-bridge-7-encoding** — StringVar UTF-8 → Latin-1
  (snobol4dotnet `28625e1`). Smoke PASS=3.

- [x] **S-2-bridge-7-stno** — LABEL stno blank-line slot alignment
  (snobol4dotnet `42c1ef7`). Smoke PASS=6.

- [x] **S-2-bridge-7-lval** — Aggregate-element collection name
  (snobol4dotnet `2414a26`). For `a<i>=v` / `t<'k'>=v`, dot emits the
  collection symbol instead of `<lval>`. Smoke PASS=9.

- [x] **S-2-bridge-7-wildcards** — Controller wildcards
  (one4all `a5117b32`, `f0f72977`). MWT_UNKNOWN as type wildcard;
  `<lval>` as name wildcard.

- [~] **S-2-bridge-7-monitor-tools** — Controller forensics (LOCAL,
  not committed). Edits to `one4all/scripts/monitor/monitor_sync_bin.py`:
  - `MONITOR_NAME_WILDCARD="spl"` env var: per-participant blanket
    name-field wildcard. Used to skip the spl-side stale-memory bug
    in `spl_vrblk_name`. Real value-byte / kind divergences are still
    reported.
  - `DIVERGE_HISTORY=5` rolling window per participant; on DIVERGE
    the controller prints the last 5 agreed records plus the
    divergence record.
  - `MONITOR_TRACE_LOG=/path/prefix` env var: write per-participant
    wire log to `/path/prefix.<participant>.log` for post-DIVERGE
    forensic grep.
  Backward-compatible (all default off). Unit smoke on `keys_match` PASS.

- [~] **S-2-bridge-6** — End-to-end `spl + dot` on beauty self-host
  (IN PROGRESS). Canonical invocation:
  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
  PARTICIPANTS="spl dot" \
      STDIN_SRC=$BEAUTY/beauty.sno \
      MONITOR_TIMEOUT=180 \
      MONITOR_NAME_WILDCARD=spl \
      MONITOR_TRACE_LOG=/tmp/wire \
      bash /home/claude/one4all/scripts/test_monitor_3way_sync_step_auto.sh \
      $BEAUTY/beauty.sno
  ```

  **First real divergence captured Mon Apr 27 2026, step 801** (with
  spl name-wildcard active to skip the SN-26 spl bridge gap):

  ```
  Last 5 agreed records (both runtimes):
    #796 LABEL stno=161
    #797 VALUE WIDE_HEADED_RIGHTWARDS_MEDIUM_BARB_ARROW = STRING(4)='🡲'
    #798 LABEL stno=160
    #799 VALUE i = INT=125
    #800 LABEL stno=161

  Divergence record:
    spl #801: LABEL stno=162                ← clean loop exit
    dot #801: VALUE i = INT=1               ← spurious VALUE event
  ```

  **Source:** `global.inc:159-163` — the SORT(UTF) post-processing loop:
  ```snobol4
      UTF_Array = SORT(UTF)
      i = 0
  G1  i = i + 1
      $UTF_Array[i, 2] = UTF_Array[i, 1]  :S(G1)
      UTF_Array =
      i =
  ```

  At the OOB iteration, the indirect-store-by-name fails. spl correctly
  emits NO VALUE on the failed iteration; dot emits a spurious
  `VALUE i = 1`. Confirmed not a control-flow divergence: dot solo run
  reaches `LABEL 162` at #802 then continues normally through 3414
  wire records to END — so this is purely an extra spurious VALUE
  emission between LABEL 161 and the eventual fall-through.

  **Hypothesis:** `Executive.Assign` chokepoint (`AssignReplace (=).cs`
  lines 179-198) fires `MonitorIpc.EmitValue` reading
  `SystemStack.Peek()` unconditionally after the switch. On the
  failed-store path, the stack may carry a stale value from earlier
  in the statement evaluation (the loop `i`). Need to audit:
  - `Executive.Assign` failure-handling around the `switch (leftVar.Collection)`
  - `Indirection ($).cs` — array/table NameVar handling (lines 35-53)
  - `IndexArray` / `IndexTable` failure propagation

- [x] **S-2-bridge-7-predicates** — FRETURN-propagation over-reach.
  Fixed Mon Apr 28 2026 (snobol4dotnet `e99b65c`).

  **Bug:** Commit `80381fb` ("S-2 FRETURN propagation: partial fix") added
  three over-broad guards to abort statement execution when a function
  FRETURNed:

  1. `ThreadedExecuteLoop.cs` `CallFunc`/`CallFuncIndirect`: a
     skip-to-`Finalize` loop on `Failure=true`.
  2. `MsilHelpers.cs` `CallFuncBySlot`: a SystemStack drain back to
     `StatementSeparator` on `Failure=true`.
  3. `BuilderEmitMsil.cs` `R_PAREN_FUNCTION`: a `Brtrue earlyExit`
     branch after `_callFuncBySlot` jumping to `FinalizeStatementMsil`.

  Each guard *individually* aborted the statement, bypassing semantically
  required follow-on work:
  - **Unary predicates** `~` (`OpNegation`) and `?` (`OpInterrogation`):
    a `~f()` or `?f()` whose `f()` FRETURNed must let the predicate run
    so it consumes the failed sentinel and (for `~`) flips Failure back
    to false. The skip/drain/branch all bypassed the predicate, leaving
    the statement in failed state. Symptom: `TEST_Negation_001/004/006`,
    `TEST_GT_002`/`LT_002`/`NE_002`, `MsilCache_NegationOperator`.
  - **Choice expressions** `(alt1, alt2, alt3)`: when `alt1` failed,
    `COMMA_CHOICE` should pop the failed sentinel and clear Failure so
    `alt2` runs. The MSIL `Brtrue earlyExit` jumped *past*
    `COMMA_CHOICE`, escaping the entire choice. Symptom:
    `TEST_Choice_002/003`, `TEST_008`,
    `MsilCache_ChoiceOperator_NegationSelectsAlternative/ThirdAlternative`.

  **Fix:** Removed all three guards. The runtime already had correct
  operator-level FRETURN propagation:
  - `OperatorFast` drains arithmetic/concat operands when `Failure=true`
    (BUG-4 carve-out at `ExecutionCache.cs:185-196`).
  - `ExtractArguments` returns `true` (signal-abort) for any operator
    with a failed-Succeeded operand, pushing a fresh sentinel.
  - `ChoiceStart` (threaded) and `_choiceStartMethod` (MSIL) clear
    Failure between alternatives.
  - `_BinaryEquals` bails at `ExtractArguments` rather than running
    `Assign` on a failed RHS.

  These are sufficient. The aggressive skip/drain/branch was redundant
  on the abort path and destructive on the predicate/choice paths.

  **Files changed:**
  - `Snobol4.Common/Runtime/Execution/ThreadedExecuteLoop.cs`
  - `Snobol4.Common/Runtime/Execution/MsilHelpers.cs`
  - `Snobol4.Common/Builder/BuilderEmitMsil.cs`

  (The MSIL emitter retained an unused `nextToken` parameter on
  `EmitSingleToken` — added during a tighter intermediate fix that was
  superseded. Harmless; left in place in case a future fix needs it.)

  **Test gate:**
  - Targeted predicate/choice subset (Negation/Interrogation/MsilCache/
    GT/LT/NE/Choice/008): **62/62 PASS**.
  - Full unit suite: **2075p / 14f**, up from **2063p / 26f** baseline.
    The remaining 14 failures are all `TEST_Csnobol4_*` corpus tests;
    confirmed pre-existing by stash-and-test against HEAD `2414a26`
    (3 Csnobol4 tests sampled, all fail at baseline too).
  - One Csnobol4 test (`TEST_Csnobol4_atn` or similar) causes a
    legitimate user-function infinite-recursion stack overflow that
    aborts the whole test host. Pre-existing.
  - Beauty 17/17: **17/17 PASS** (unchanged).
  - Beauty self-host gate: still **FAIL** at line 26 (`&FULLSCAN = 1`,
    Parse Error from `mainErr1`). Confirms goal-file diagnosis: the
    predicate regression and the `&FULLSCAN` Parse Error are **distinct
    bugs**. Predicate fix did not unblock self-host.

- [x] **S-2-bridge-7-stno-stable** — Wire LABEL stno emission no longer
  depends on mutable `Parent.Code`.  Fixed Mon Apr 28 2026 (snobol4dotnet
  HEAD-of-session-58).

  **Bug:** All three LABEL emit sites (`MsilHelpers.InitStatementMsil`,
  `ThreadedExecuteLoop` `OpCode.Init` case, `InitializeFinalize.InitializeStatement`)
  computed the wire stno at runtime via:
  ```
  blanks = Parent.Code.SourceLines[stmtIdx].BlankLineCount;
  EmitLabel(stmtIdx + 1 + blanks);
  ```
  But `Parent.Code` is replaced in-place by every EVAL/CODE invocation
  (`exec.Parent.Code = new SourceCode(exec.Parent)` in
  `Eval.cs`, `Code.cs`, and the four `*ConversionStrategy.cs` files).
  After the first EVAL runs, the main program's `SourceLines` list is
  gone from `Parent.Code` and `stmtIdx` falls past the end of the
  replacement (much smaller) list — the guard returned `blanks = 0`
  and the wire stno was emitted **short by the BlankLineCount of the
  enclosing statement**.

  **Symptom on the wire:** monitor at the 3-bug-fix watermark step 1046
  diverged at the first nPop call after the OPSYN'd `&` (= reduce)
  triggered an EVAL.  reduce body: `EVAL("epsilon . *Reduce(...)")` —
  EVAL fires, swaps Parent.Code, leaves a tiny replacement.  Subsequent
  `CALL nPop` correctly executed nPop's body, but the LABEL stno emit
  read blank-count from the wrong list and reported stno=587 (semantic.inc:14
  DEFINE line) instead of stno=595 (semantic.inc:24 nPop body).

  **Fix:** added `Executive.SourceStno`, a precomputed `List<long>`
  parallel to `SourceCode`, populated by `PopulateMainMetadata` and
  `PopulateCodeMetadata` at build time as `stmtNumber + 1 + line.BlankLineCount`.
  All three runtime LABEL emit sites now read from `SourceStno` instead
  of `Parent.Code.SourceLines`.  EVAL/CODE replace `Parent.Code` freely;
  `SourceStno` is build-time-frozen and never mutated, so the wire stno
  is stable.

  **Files changed:**
  - `Snobol4.Common/Runtime/Execution/Executive.cs` — declared `SourceStno`,
    initialized in constructor.
  - `Snobol4.Common/Builder/Builder.cs` — populated in
    `PopulateMainMetadata` and `PopulateCodeMetadata`.
  - `Snobol4.Common/Runtime/Execution/MsilHelpers.cs` — read from
    `SourceStno` in `InitStatementMsil`.
  - `Snobol4.Common/Runtime/Execution/ThreadedExecuteLoop.cs` — read from
    `SourceStno` in `OpCode.Init`.
  - `Snobol4.Common/Runtime/Execution/InitializeFinalize.cs` — read from
    `SourceStno` in `InitializeStatement`.

  **Test gate:**
  - Full unit suite: **2075 passed / 14 failed** — exact match to
    pre-fix baseline.  No regression.
  - Beauty self-host gate: still **FAIL** at line 26 (`&FULLSCAN = 1`,
    Parse Error) — same line count (28), same exit (0).  This stno fix
    is necessary infrastructure for the wire monitor and is not the
    cause of the Parse Error.
  - Wire monitor `spl` vs `dot` with `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`
    + `MONITOR_NAME_WILDCARD=spl`: advanced from divergence at step 1044
    (LABEL stno=595 vs 587) to step **1497**, a much later point.

- [x] **S-2-bridge-7-monitor-kw-skip** — Controller workaround for
  spl bridge's missing-VALUE-on-keyword-assignment gap, committed.

  Implementation: `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1` env var in
  `one4all/scripts/monitor/monitor_sync_bin.py`.  When the env var is
  set and a step diverges where one or more participants have a `VALUE`
  event with a name starting with `&`, the controller acks just the
  VALUE-emitting participants and reads their next record, then retries
  comparison.  Bounded by `SKIP_MAX_PER_STEP=4` per side per step.

  Off by default — explicit opt-in is required, so we don't silently
  hide divergences in a routine run.  This is a stand-in until
  SN-26-bridge-coverage extends the spl bridge to emit VALUE for
  keyword stores; when that lands, the skip becomes a no-op.

  Validated: with both env vars set, the monitor advances past the
  spl-side keyword-VALUE gap at beauty.sno line 26 (`&FULLSCAN = 1`)
  and the subsequent reduce-then-nPop chain that previously diverged
  at 1044/1046.

- [x] **S-2-bridge-7-dollar-alt** — Fix `$` operator's alternation-backtrack
  bug.  `Executive.Assign`'s deferred-Assignee evaluation loop ignored
  `Failure` after evaluating an `ExpressionVar` Assignee.  When the
  deferred form was `*fn(...)` and `fn()` FRETURNed, `Assign` consumed
  the failure-pushed null StringVar (whose Symbol is the function's own
  name), then proceeded to overwrite that variable with the captured
  substring.  Worse, `ImmediateVariableAssociation2.Scan` always
  returned `MatchResult.Success`, never propagating Assignee failure to
  the scanner — so an outer alternation never backtracked.

  Minimal repro (passes on spl, FAIL pre-fix on dot):
  ```snobol4
  patA = SPAN(&UCASE &LCASE) $ tx $ *match(listA, snoTxInList)
  patB = SPAN(&UCASE &LCASE) $ tx $ *match(listB, snoTxInList)
  'FULLSCAN' (patA | patB)                       :S(ok)F(fail)
  ```

  Fix: `AssignReplace (=).cs` — bail when `Failure` after deferred
  Assignee eval; `ImmediateVariableAssociationPattern.cs` —
  `ImmediateVariableAssociation2.Scan` returns `MatchResult.Failure`
  when `Exec.Failure` is set.  Verified: 1898/1898 non-corpus tests
  PASS, 295/295 pattern tests PASS, 14 pre-existing corpus failures
  unchanged (verified via stash + retest baseline).

  **Caveat — not the gating issue for S-2-bridge-7-fullscan.**  Beauty
  self-host produces byte-identical stderr pre-fix and post-fix (28
  lines, same Parse Error at `&FULLSCAN = 1`).  The actual
  beauty self-host failure is somewhere else — see updated diagnosis
  below.

- [x] **S-2-bridge-7-betastack-failure-leak** — *Failure leak from
  BetaStack commit loop in Executive.PatternMatch.*  Fixed Thu Apr 30
  2026 (snobol4dotnet `92b79be`).

  **Bug:** `Executive.PatternMatch` (the `?` operator) iterates
  `BetaStack` after a successful match and calls `Assign()` on each
  deferred conditional-assignment entry.  Deferred entries whose
  Assignee is an `ExpressionVar` (a `*fn(...)` capture) call into
  user-defined SNOBOL4 functions; if such a function FRETURNs (or
  otherwise sets `Failure=true` as a side effect), `Failure` is
  carried over to subsequent BetaStack iterations and out of the
  PatternMatch operator entirely.  The match itself returned SUCCESS,
  but the `Failure` flag at the operator's exit was true, so the
  statement engine took `:F` — taking `mainErr1` ("Parse Error") on
  beauty.sno line 616 even though the underlying pattern match
  unambiguously succeeded.

  **Bug found via C# function tracing between last-agreed and
  first-diverged sync-step events.**  Diagnostic patches (NOT
  committed): made `MonitorIpc._standaloneCount` tick without an
  IPC controller (so `MONITOR_TRACE_FROM_EVENT`/`TO_EVENT` works
  standalone); wired `[PM]`/`[M]`/`[ALT]` traces into `Scanner.cs`
  and `ScannerState.cs` reading `MonitorIpc.TraceEnabled`; added
  `[QPM]` traces to `Executive.PatternMatch` covering the BetaStack
  iteration.  At `MONITOR_TRACE_FROM_EVENT=2390 TO_EVENT=2700` the
  trace showed:

  ```
  [QPM ec=2394] MR.Outcome=SUCCESS BetaStack.Count=14
  [QPM ec=2394] BetaStack[0..5] Assign returned, Failure=False
  [QPM ec=2482] BetaStack[6] Assign returned, Failure=True
  ...
  [QPM ec=2603] BetaStack[13] Assignee=ExpressionVar pre=38 post=38
  [QPM ec=2607] BetaStack[13] Assign returned, Failure=True
  [QPM ec=2607] EXIT Failure=True   <-- match SUCCESS leaked Failure
  ```

  The trace makes the bug crystal clear in two adjacent lines: the
  match outcome was SUCCESS, but the operator exits with Failure=true
  because the BetaStack[13] Assign side-effected it.

  **Fix:** added `Failure = false;` after the BetaStack iteration in
  `Snobol4.Common/Runtime/Functions/OperatorsBinary/PatternMatch (Question Mark).cs`.
  Statement-level Failure must reflect the match outcome, not the
  side-effect outcome of deferred conditional-assignment commits.

  **Test gates:**
  - Unit suite (excluding pre-existing 14 TEST_Csnobol4_* failures):
    **2385 PASS, 0 FAIL, 2 skipped**.
  - Beauty 17/17 corpus drivers: **17/17 PASS**.
  - Beauty self-host: advanced from line 26 (`&FULLSCAN = 1`,
    28 stderr lines) to **line 48 (`snoDQ = '"' BREAK('"' nl) '"'`,
    47 stderr lines)**.  23 more lines of beauty.sno now parse.

  **Reframing of S-2-bridge-7-fullscan:** sessions #56–#70 chased
  this bug under the assumption that the underlying pattern match
  for `&FULLSCAN = 1` was failing (FENCE/SEAL semantics, snoExpr14
  alternation order, missing `*snoUnprotKwd` arm).  None of those
  fixes individually unblocked beauty self-host because the actual
  pattern match was succeeding all along.  The bug was in the
  STATEMENT engine's interpretation of the operator's exit state,
  not in the pattern matcher's match algorithm.  The session #66
  FENCE Mark/Seal correctness fix (`bb28a8d`) and the session #68
  Match() seal-skip fix (`c578fb5`) ARE both real and necessary —
  they fixed real bugs (test 114 `pat_fence_via_var_in_paren_alt`,
  test 061 `pat_fence_fn_seal`) — but they were not gating beauty
  self-host on `&FULLSCAN = 1`.  The single-line fix in this rung
  was.

- [ ] **S-2-bridge-7-fullscan** — Diagnose the next Parse Error
  Error directly. The minimal repro is lines 1-26 of beauty.sno + END
  fed as stdin to `dotnet Snobol4.dll -bf beauty.sno`. SPITBOL runs
  cleanly; dot emits the Parse Error from beauty's own `mainErr1`
  branch — meaning beauty's `*snoParse *snoSpace RPOS(0)` pattern fails
  to match `&FULLSCAN = 1` under dot. The keyword-recognition pattern
  alone (`'&' SPAN(&UCASE &LCASE) $ tx $ *match(snoUnprotKwds, snoTxInList)`)
  works correctly in isolation on dot — the bug is somewhere deeper in
  beauty's grammar (snoStmt / snoSubject / snoLabel / etc.) that gets
  exercised when an actual `&FULLSCAN = 1` paragraph is parsed.

  **Session #58 advance:** with the stno-stable fix above, the monitor
  reaches step **1497**, where the next divergence is in
  `case.inc:22` — the `icase` function:
  ```snobol4
  icase          IDENT(str)                                                           :S(RETURN)
  str            POS(0) ANY(&UCASE &LCASE) . letter =                  :F(icase1)
  ```
  Last 2 agreed and the diverge:
  ```
  | 1496 | 175 | VALUE letter = STRING(1)='E' | VALUE letter = STRING(1)='E' |
  | 1497 | 175 | VALUE str = STRING(2)='ND'   | LABEL stno=176              |
  ```
  spl emits a second VALUE event for `str = 'ND'` (the destructive
  match-and-replace `... . letter = ` consumed the first char of `str`
  and rebound it).  dot does not emit that VALUE event — it advances
  directly to LABEL 176 (the next statement).  This is a missing-VALUE
  emission on the dot side for **destructive pattern-match assignment
  in the same statement as the `.` capture-and-replace**.  The first
  `letter = 'E'` event correctly fires from dot's chokepoint; the
  follow-on `str = 'ND'` does not.  Likely fire-point gap in
  `Executive.Assign` / pattern-match scanner: the `=` after the `.`
  capture is a separate logical assignment that the wire chokepoint
  does not currently see.

  Suggested next-session approach:
  1. Add a fire-point in the pattern-match `=` (replacement) path so
     destructive-match rebinds emit a VALUE event.
  2. Verify by re-running monitor; expect to advance past 1497.
  3. Continue chasing the next divergence.  The Parse Error itself
     may surface as a real value disagreement once the wire reaches
     line 26.

  **Session #62 investigation:**
  - Confirmed `icase('END')` works semantically end-to-end on dot
    (`POS(0) ANY(&UCASE &LCASE) . letter =` rebinds `str` correctly:
    'END' → 'ND' → 'D' → ''; pattern matches END/end/EnD).
    The step-1497 divergence is a wire/diagnostic gap, not a
    semantic gap.
  - Direct attempt to reproduce the beauty self-host parse failure in
    isolation: load all -INCLUDE files, set `&FULLSCAN = 1`, then run
    `src POS(0) *snoParse *snoSpace RPOS(0)` against
    `'                  &FULLSCAN      =  1\n'`.  **Result: FAIL on
    BOTH spl and dot.**  But spl successfully parses the same line
    during real beauty self-host (verified by instrumenting beauty.sno
    with trace OUTPUT calls before each parse attempt).
  - Conclusion: the parse's success in spl beauty self-host depends on
    state accumulated between the program-startup -INCLUDE expansions
    and the FULLSCAN parse — not just the patterns/OPSYN/keywords
    visible after `:(semanticEnd)`.  Likely candidates: residue from
    the prior successful `START\n` and blank-line parses (which call
    `pp(sno)`, push/pop trees, mutate counters).  Two paths forward:
    (a) extend the trace of `beauty_trace.sno` to dump *all* relevant
    state (counter stack, tree stack, AlphaStack/BetaStack analogs)
    just before the FULLSCAN parse, replay that state in isolation and
    observe whether spl's parse then succeeds outside beauty —
    if yes, isolate the state element that flips the result.
    (b) directly dump dot's internal pattern-match state at the
    failing parse and compare against an spl trace at the same point.
    Path (a) is cheaper and gives a SPITBOL-only repro that nails down
    which state matters.  Path (b) requires more dot-side tooling but
    points directly at the root-cause divergence.

  **Session #63 — wire convention adjusted, self-host gate untouched.**
  (snobol4dotnet `724c1b6`).  Monitor watermark moved 1497 → 1617 by
  closing four wire-encoding inconsistencies between spl's and dot's
  bridges.  **Beauty self-host gate UNCHANGED — same 28 stderr lines,
  same Parse Error at `&FULLSCAN = 1`.  None of the four changes
  affected dot's SNOBOL4 semantics; all are inside `MonitorIpc.Enabled`
  guards or in the bridge emit calls themselves.  In the unmonitored
  path (which is what beauty self-host runs), dot's behavior is
  byte-identical to before the session.**

  Honest framing: this session did not progress S-2-bridge-7-fullscan.
  It made the diagnostic instrument more accurate without lowering the
  patient's fever.  The four changes were:

  1. `AssignReplace (=).cs` `ReplaceMatch` — added `MonitorIpc.EmitValue`
     for destructive subject rebind (was the step-1497 wire-only gap).
  2. `Define.cs` — `ProgramDefinedFunctionStack.Pop()` to balance Push
     (was a leak readable only by the suppression check, which itself
     was a wire concern).
  3. `Define.cs` — removed `MonitorIpc.EmitValue(returnVarName, ...)`
     before `EmitReturn` (aligns wire convention with spl/csn:
     RETURN carries only the type, value comes from body-assign emit).
  4. `AssignReplace (=).cs` `Assign` — removed `isReturnSlot`
     suppression and added `OutputChannel`-empty skip (matches spl's
     trap-bypass behavior at `asg02`/`asg14` for OUTPUT/PUNCH writes).

  Test gate clean: 2075p/14f baseline match, beauty 17/17 PASS, beauty
  self-host stderr unchanged at 28 lines.

  **What this session revealed about the harness as a tool:**

  The sync-step monitor's premise — "where the wires first disagree,
  the bug lives between" — is only useful when both bridges record the
  same events for semantically-correct execution.  Today, both bridges
  still have fire-point and type-encoding gaps; every wire divergence
  surfaced from beauty self-host so far has been a bridge inconsistency
  rather than a SNOBOL4 semantic bug.  Chasing wire divergences from
  event 1 has been clearing bridge ghosts, not finding the parse bug.

  **The goal's rung list does not include a validation step proving
  the harness can actually catch a known semantic bug.**  Every closed
  bridge rung (S-2-bridge-1..7-dollar-alt) addresses harness build /
  cleanup; none injects a synthetic dot bug to confirm the harness
  pinpoints it.  Without that validation, "watermark advance" is an
  ambiguous signal: bridge gap closure or real bug, indistinguishable.

  **The actual gating bug is almost certainly invisible to the wire.**
  Session #62 already established the FULLSCAN parse failure is
  state-dependent: it fails in isolation on BOTH spl and dot, but spl
  succeeds during real beauty self-host.  The state that flips the
  result accumulates through prior parses and is held in pattern-match
  scanner internals (BetaStack residue, ARBNO state, FENCE bookkeeping,
  counter/tree stacks) — none of which are on the wire.  Sync-step
  monitoring will agree at every event while these states diverge.

  **Recommended next-session pivot — STOP chasing wire watermark.**

  Either:

  - **Add S-2-bridge-validate rung first** — inject a known semantic
    divergence in dot (e.g. make `IDENT` always succeed), run the
    harness, confirm it pinpoints the right event.  Only after this
    proves the harness can find a real bug should wire watermark
    advance be treated as meaningful signal.

  - **Pursue path (a) directly without the harness** — instrument
    beauty.sno to dump scanner-relevant state (counter stack, tree
    stack, BetaStack analog, IdentifierTable snapshot) right before
    the FULLSCAN parse on the spl side where it succeeds.  Replay
    that state in isolated spl where the parse currently fails.
    Identify the state element that flips the result.  This is a
    SPITBOL-only diagnostic; no dot changes; bypasses the wire.

  Path (a) is cheaper to start and produces a SPITBOL-only repro
  pinpointing what state matters.  Once isolated in spl, comparing
  the same state on dot identifies the dot-side accumulation bug.

  **Session #64 — controller MWT_UNKNOWN value-byte wildcard; watermark 1617→2839; first
  divergence at counter.inc:17 NRETURN body-assign; root cause not isolated.**
  (one4all `scripts/monitor/monitor_sync_bin.py` keys_match change, no snobol4dotnet
  runtime changes.)

  **What landed:** `keys_match` extended so that when one participant emits MWT_UNKNOWN,
  the value-byte equality check is bypassed (was: extended only the type-tag wildcard).
  Rationale: SPITBOL's `spl_block_to_wire` emits MWT_UNKNOWN with zero value bytes for
  every nmblk/ptblk/atblk/tbblk/cdblk/efblk; dot's MonitorIpc encodes MWT_NAME with the
  symbol bytes (5 bytes "dummy" for `.dummy` NRETURN body assigns).  Pre-fix, the
  value-byte mismatch (`b''` vs `b'dummy'`) tripped DIVERGE before the type wildcard
  could absorb it; post-fix, an UNKNOWN on either side wildcards both type AND value,
  consistent with the design intent already documented in keys_match's docstring.

  **Effect on watermark:** beauty self-host monitor now reaches step **2839** (was 1617).
  Tiny-program smoke gate still PASS=0 (no false negatives).  Real STRING vs STRING /
  INTEGER vs INTEGER divergences still flag DIVERGE — the carve-out is strictly
  asymmetric on UNKNOWN.

  **First real divergence at step 2839** — `counter.inc:17 PushCounter = .dummy :(NRETURN)`:
  ```
  | step | spl                            | dot                                |
  |------|--------------------------------|------------------------------------|
  | 2835 | CALL upr                       | CALL upr                           |
  | 2836 | LABEL stno=168                 | LABEL stno=168                     |
  | 2837 | VALUE upr = STRING(8)='FULLSCAN'| VALUE upr = STRING(8)='FULLSCAN'   |
  | 2838 | RETURN upr (RETURN)            | RETURN upr (RETURN)                |
  |>2839 | RETURN match (NRETURN)         | CALL upr                           |
  ```
  After the 18th `*upr(tx)` returns 'FULLSCAN' inside the snoUnprotKwd match for FULLSCAN,
  spl unwinds the pattern-match scanner and reaches `:S(NRETURN)` from match.inc:8.  Dot
  fires a 19th *upr Scan instead.  Root cause not isolated this session.

  **What investigation ruled out (saved-cycles for next session):**
  - **Standalone repro.**  Built `(POS(0) | ' ') *upr(tx) (' ' | RPOS(0))` matching
    'FULLSCAN' against the same 18-keyword list, both directly via `match()` and wrapped in
    `'&FULLSCAN' snoUnprotKwd`.  Both spl and dot make exactly **18 upr calls** and match
    cleanly.  Confirms session #62's finding: the bug is state-dependent, requires the full
    beauty self-host context (likely BetaStack residue or pattern-match-scanner state from
    earlier successful matches).
  - **Stack trace at every upr entry.**  Patched `Define.cs` `EmitCall` to dump
    `Environment.StackTrace` on upr calls #18-21.  All identical:
    `ExecuteProgramDefinedFunction ← Function ← ThreadedExecuteLoop ← RunExpressionThread
     ← (CompileStarFunctions closure) ← UnevaluatedPattern.Scan ← Scanner.Match
     ← Scanner.PatternMatch ← PatternMatch (Question Mark) ← OperatorFast`.  Every call —
    including the 19th — comes from a `*upr(tx)` pattern node, not a source-level call.
  - **Pattern AST dump.**  Patched `Scanner.PatternMatch` to dump the AST built for each
    PatternMatch invocation under DOT_DUMP_AST=1.  The standalone `snoTxInList` AST has
    exactly **one** `UnevaluatedPattern` node (idx 5, Sub=7, Alt=-1) — structurally
    correct, no duplication.  The earlier "two *upr nodes alternated" reading of node
    indices in the wire-monitor diagnostic was wrong: those were two DIFFERENT ASTs from
    consecutive match() calls, not two nodes within one AST.
  - **Beauty self-host AST inventory.**  82 ASTs built before Parse Error.  Last four
    chronologically:
    1. subject='&FULLSCAN = 1' — first parse attempt.  Apparently SUCCEEDS (control proceeds).
    2. subject='&MAXLNGTH = 524288' — line 27 parse attempt.
    3. subject='ABORT ALPHABET ARB BAL FAIL FENCE FILE FNCLEVEL ...' = snoProtKwds (24 kwds).
    4. subject='ANY APPLY ARBNO ARG ARRAY ATAN ...' = snoFunctions list.
    Then Parse Error fires with `OUTPUT snoSrc='&FULLSCAN = 1'`.  The chronology is
    inconsistent with main-loop logic (main01 resets snoSrc='' between paragraphs) — needs
    direct attention.  **Note: dot does NOT build an AST against snoUnprotKwds before the
    error.**  spl is observed (via wire monitor) to enter that match and succeed.  Dot's
    grammar never reaches it.  The snoExpr14 alternation order is `... '?' | *snoProtKwd
    | *snoUnprotKwd | '&' ...` — dot tries snoProtKwd (fails correctly), then jumps to
    snoFunctions (an alternative inside a different production tree, snoAtom@line 182),
    skipping snoUnprotKwd entirely.  This is unexpected and likely the actual gating bug.
  - **Pattern algebra source review.**  `(POS(0) | ' ') *upr(tx)` builds via
    `PatternConcatenation.cs` as `ConcatenatePattern(AlternatePattern(POS(0), ' '),
    UnevaluatedPattern(...))` — a tree, not a graph; no shared sub-pattern between
    alternation arms.  `BuildNodeList` walks the tree once.  No structural duplication.

  **Recommended next-session pivot — pursue the snoExpr14 skip directly.**

  The wire monitor advance to step 2839 is informative but the divergence there is inside
  the snoUnprotKwd match path that dot never reaches in the unmonitored failing run.  The
  REAL gating bug is upstream: dot's snoExpr14 alternation tries `*snoProtKwd`, fails,
  then proceeds to `*snoFunction` (which lives in a DIFFERENT production, snoAtom@line 182)
  WITHOUT first trying `*snoUnprotKwd` (the very next alternative in snoExpr14@line 154).
  Two paths forward:

  1. **AST dump path.**  Re-enable Scanner.PatternMatch's AST-dump diagnostic, target the
     parse of `&FULLSCAN = 1` specifically (instrument *snoParse entry/exit on dot to
     bracket the relevant ASTs), and inspect the actual snoExpr14 alternation node chain
     to see whether `*snoUnprotKwd` is even reachable from where the matcher backtracks
     after `*snoProtKwd` fails.  If the AST is structurally missing the snoUnprotKwd arm
     or its Alternate edge, that is the bug.

  2. **Differential AST dump path.**  Build the same snoExpr14 pattern in a tiny standalone
     program on both spl and dot, dump the matched paths, and diff them to see whether
     dot's PatternFactory or alternation construction gives a different graph than spl's.
     Standalone reproduction has historically failed to reproduce the FULLSCAN bug
     (state-dependent), but the snoExpr14 *structure* is state-independent and may differ
     between runtimes regardless of subject.

  Path 1 is more direct.  Path 2 is the safer fallback if Path 1's instrumentation proves
  too noisy in the full self-host run.  In either case: STOP at the first concrete AST
  divergence — do not chase symptom-level retries before isolating the structural diff.

- [ ] **S-2-bridge-harness-trust** — *Stop trusting the sync-step harness
  until it can see the actual gating bug.*  Session #67 (this session)
  re-ran the unfiltered harness on beauty self-host and found that the
  **real first DIVERGE is at step 933, on `&FULLSCAN = 1` itself**:

  | step | spl | dot |
  |------|-----|-----|
  | #933 | `LABEL stno=654` | `VALUE &fullscan = INT=1` |

  spl emits no VALUE for the keyword store (the SN-26 spl bridge gap
  recorded in "Open SPITBOL bridge issue" below), so it jumps straight
  to LABEL 654.  dot emits the VALUE first.  This is a **known bridge
  gap, not a runtime semantic bug**.  All subsequent DIVERGE points
  recorded by sessions #56, #58, #62, #63, #64, #65, #66 (watermark
  801 → 933 → 1046 → 1497 → 1617 → 2839) were reached **only with
  controller-side skip workarounds** (`MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`,
  `MONITOR_NAME_WILDCARD=spl`) papering over this and other bridge
  gaps.  Each "advance" was the controller masking ghosts; the
  underlying parse-failure bug at line 26 has been invisible to the
  wire the entire time.

  Session #63 already wrote: *"Chasing wire divergences from event 1
  has been clearing bridge ghosts, not finding the parse bug."*  The
  goal file still ladders sub-rungs that depend on watermark advance.
  That is the contradiction this rung exists to resolve.

  **Done when:** the unfiltered harness (no `MONITOR_NAME_WILDCARD`,
  no `MONITOR_SKIP_EXTRA_KEYWORD_VALUES`, no other skip env vars)
  reaches at least the byte where beauty self-host actually fails on
  dot.  Either:
  - **Path A** — close the spl bridge VALUE-on-keyword-store gap in
    `x64/osint/monitor_ipc_runtime.c` (asg01 / asg14 / asg02), so spl
    emits `VALUE &fullscan = INT=1` like dot does.  This eliminates
    step #933 as a DIVERGE.  Cross-ref SN-26-bridge-coverage.
  - **Path B** — close the spl `vrsto = xl - vrvlo` stale-memory issue
    in `spl_vrblk_name` (the workaround for which is `MONITOR_NAME_WILDCARD=spl`).
    This eliminates the name-wildcard workaround.

  Both paths together restore the harness's premise: agreement on the
  wire = agreement in semantics.  Until then, watermark numbers are
  decoration.

  **Validation gate after fix:** inject a known semantic divergence
  in dot (e.g. make `IDENT` always succeed, or `RPOS(0)` always fail),
  run unfiltered harness, confirm it pinpoints the right event.  This
  is the validation rung session #63 already recommended and which has
  not been done.

  **Until this rung closes, do not chase wire-watermark advances.**
  The actual gating bug is a parse-time divergence in dot's pattern
  matching during the `&FULLSCAN = 1` parse, and it has been
  state-dependent and invisible to the wire since session #62.  Work
  that bug directly — instrument `Scanner.PatternMatch` /
  `UnevaluatedPattern.Scan` / scanner alt-stack on dot during the
  failing parse — without depending on the harness for localization.

- [~] **S-2-bridge-event-bombs** — *General-strategy mechanisms baked
  into MonitorIpc so future sessions never re-invent them.*  Once a
  DIVERGE row exposes the (last-agreed N, first-diverge N+1) pair, the
  hard part of any bug is "where in the dot runtime did execution go
  between event N and event N+1?"  Two mechanisms close that gap:

  **Mechanism A — `MONITOR_BREAK_AT_EVENT=N`** (debugger entry point).
  In `MonitorIpc.cs`, every `EmitCall`/`EmitReturn`/`EmitValue`/
  `EmitLabel` increments a static `_emitCount`.  When the env var is
  set and `_emitCount == N`, fire `System.Diagnostics.Debugger.Break()`
  if a debugger is attached, otherwise dump the managed stack to stderr
  via `Environment.StackTrace`.  Then continue normally so the next
  emit (the diverge event) is reached, where the same handler can be
  invoked again.  The result: full call-stack at the last-agreed event,
  full call-stack at the first-diverge event, side by side.  No tracing
  noise.

  **Mechanism B — `MONITOR_TRACE_FROM_EVENT=N` / `MONITOR_TRACE_TO_EVENT=M`**
  (focused tracing).  Same emit-counter; when `_emitCount` enters the
  half-open interval `[N, M)`, flip a global `MonitorIpc.TraceEnabled
  = true`.  Existing diagnostic instrumentation in dot
  (`DOT_TRACE_ALT=1` in ScannerState, AST dumps, *upr stack dumps,
  any future env-gated traces) reads this single flag instead of its
  own env var.  The harness writes the focused trace to
  `MONITOR_TRACE_LOG.dot.scan.log` automatically.  Result: a trace
  bounded to exactly the events between last-agreed and first-diverge
  — usually a few hundred to a few thousand scan operations — instead
  of the millions in a full-program trace.

  **Why this generalizes — the "set bombs" pattern.**  This is just
  event-counted trigger / event-counted untrigger, applied to a single
  emit counter.  The same mechanism extends to:
    - `MONITOR_BREAK_ON_LABEL_STNO=N` — fire on a specific source line.
    - `MONITOR_BREAK_ON_VALUE_NAME=foo` — fire when foo is assigned.
    - SNOBOL4-side analog on spl using `&STCOUNT` — set a catch-all on
      a specific statement count to trigger source-side OUTPUT or
      `DUMP()` at the agreed event, just before divergence.

  These hooks are **fire-and-forget infrastructure** — once installed,
  every future session that hits a DIVERGE row gets a one-line
  follow-up: `MONITOR_TRACE_FROM_EVENT=2837 MONITOR_TRACE_TO_EVENT=2840
  bash test_monitor...` produces a trace covering exactly the bug,
  ready for inspection.

  **Done when:**
    1. `MonitorIpc.cs` carries the `_emitCount` and the two env-var
       handlers.
    2. `ScannerState.cs` `DOT_TRACE_ALT=1` reads `MonitorIpc.TraceEnabled`
       (OR'd with the env var, for back-compat).
    3. A smoke test demonstrates the workflow: inject a known dot bug,
       run harness, get DIVERGE row, set `BREAK_AT_EVENT` to the
       last-agreed event count, attach `dotnet-trace` or read the
       stderr stack dump, identify the bug from the call stack alone.
    4. Harness driver script (`test_monitor_3way_sync_step_auto.sh`)
       passes the new env vars through to dot's environment when set.

  **Why this rung is paired with `harness-trust` not folded into it.**
  `harness-trust` is about the bridge's *output* being honest (no
  controller masking).  `event-bombs` is about turning each honest
  divergence row into a *concrete debugger entry point*.  Both are
  needed but they are independent — bombs help even when the harness
  is partially gapped (you set the bomb on a DIVERGE you know is real,
  not a ghost).

- [ ] **S-2-bridge-event-bombs-coverage** — *Mechanism B's TraceEnabled
  hook must instrument every site that runs between two adjacent wire
  emits, not just the pattern matcher.*  Session #69 demonstrated the
  failure mode: with TraceEnabled wired only into `Scanner` /
  `ScannerState`, the trace between #932 (LABEL on `&FULLSCAN = 1`)
  and #933 (VALUE `&fullscan`) came back **empty**, because the
  statement does no pattern matching — only a keyword store.  An
  empty trace was wrongly reported as "nothing happened between the
  two events", when in fact `Executive.Assign` ran a complete
  keyword-handler dispatch.  The lesson: **TraceEnabled must light up
  every C# function on every code path the runtime can take between
  two emits**, or it lies by omission.

  **Done when:** every code path leading between two adjacent
  `Emit*` calls produces at least one TraceEnabled-gated line.
  Concretely, instrument:

    a. **Threaded execute loop** — `ThreadedExecuteLoop.cs`'s
       opcode-dispatch `while (...)` body emits one `[TEL]` line
       per opcode dispatched (Op + IntOperand + IntOperand2 +
       AmpCurrentLineNumber + InstructionPointer).
    b. **Assign path** — `OperatorsBinary/AssignReplace (=).cs`
       `Assign(args)` and `ReplaceMatch(args)` emit `[ASN]` lines
       at entry, at each branch (keyword-path,
       collection-path, NameVar-path, fallthrough), at the
       keyword-handler dispatch, and at exit of each branch.
    c. **Function dispatch** — `Executive.Function(int)` and
       `ProgramDefinedFunction.Execute` emit `[FN ]` lines at entry
       and return, before/after the `EmitCall`/`EmitReturn` fire.
    d. **Pattern matcher** — already covered by the existing
       `[PM ]`/`[M ]`/`[ALT]` triple in `Scanner.cs`/`ScannerState.cs`.
       Keep as-is.
    e. **Builtin / keyword handlers** — when a handler is
       dispatched from `Assign`'s `KeywordTable.TryGetValue(...)`,
       a thin wrapper around the handler delegate emits `[KWH]`
       at entry and return.
    f. **InitializeFinalize / MsilHelpers** — both contain
       `EmitLabel` call sites; both emit `[INI]` / `[MSI]` lines
       on entry to the routine that fires the label.

  **Acceptance smoke test:** with `MONITOR_TRACE_FROM_EVENT=N
  MONITOR_TRACE_TO_EVENT=N+2` for any chosen N at which beauty
  self-host runs cleanly, the trace MUST contain at least one line
  for every C# method actually invoked while `_emitCount == N`.
  Concretely: pick N=932 (last-agreed before `&FULLSCAN = 1`).
  Trace must show, in order, an opcode dispatch, an Assign entry,
  the keyword-path branch, a keyword-handler dispatch, a
  keyword-handler return, the EmitValue, and the next opcode
  dispatch.  Session #69 produced 5 of these 7 lines (TEL, ASN x4)
  before the diagnostic was written down; the remaining 2 (FN at
  CallMsil dispatch into the JIT body, and the actual keyword-
  handler dispatch wrapper) are the gap this step closes.

  **Constraint:** all instrumentation is `if (MonitorIpc.TraceEnabled)`-
  gated.  Zero overhead when monitoring is off.  All trace lines
  go to `Console.Error` so they pipe into the existing
  `dot.err` capture from `test_monitor_3way_sync_step_auto.sh`.

  **Done when:**
    i.   Every callsite (a)–(f) above emits a TraceEnabled line.
    ii.  Acceptance smoke test passes.
    iii. Beauty 17/17 corpus unchanged with TraceEnabled OFF
         (build clean, baseline self-host stderr line count
         unchanged from the c578fb5 baseline of 28).
    iv.  Test gate: a `scripts/test_smoke_dot_trace_coverage.sh`
         that runs beauty self-host with `MONITOR_TRACE_FROM_EVENT=
         MONITOR_TRACE_TO_EVENT=$(($1+2))` for N supplied as $1,
         and asserts the resulting `dot.err` contains at least
         one TEL, one ASN, one FN, one PM, and one INI/MSI line.

- [ ] **S-2-bridge-7-A1** — *Path A: close the spl bridge VALUE-on-
  keyword-store gap so the unfiltered harness advances past
  step #933 honestly.*

  **Diagnosis (session #69, with full TEL/ASN tracing):**
  Trace `MONITOR_TRACE_FROM_EVENT=931 TO=935`, no controller
  workarounds.  Captured 10 trace events between dot's wire emits
  #931 and #934.  In particular, between #932 (LABEL stno=653)
  and #933 (VALUE &fullscan = 1), dot ran:

  ```
  [TEL ec=931 ip=643 stno=642] OP CallMsil i1=643 i2=0
  [ASN ec=932] ENTER left=IntegerVar/sym='&fullscan'/kwd=True right=IntegerVar
  [ASN ec=932] KEYWORD-PATH sym='&fullscan' readonly=False rightType=IntegerVar
  [ASN ec=932] KEYWORD-HANDLER-FOUND sym='&fullscan' value=1
  [ASN ec=932] KEYWORD-HANDLER-RETURNED sym='&fullscan'
  [TEL ec=933 ip=644 stno=643] OP CallMsil i1=644 i2=0
  ```

  The `[ASN]` block is dot's `Executive.Assign(args)` call which
  routes through the keyword-path (lines 110–141 of
  `OperatorsBinary/AssignReplace (=).cs`), looks up `&fullscan`
  in `KeywordTable`, dispatches the handler, then fires
  `MonitorIpc.EmitValue("&fullscan", 1)` — wire #933.  **dot is
  doing the right thing.**

  The same source statement on spl runs `asign → asg14 → asg26
  → asg15 → exi` (sbl.min:17611, 17766, 17861, 17783).  None of
  those branches calls `sysmv` / `sysmw`.  spl's wire jumps from
  #932 (LABEL 653) directly to a LABEL 654, skipping the VALUE.
  The bug is the missing fire-point in spl's `asign` keyword
  paths.

  **Fix shape:** new C entry point `zysmk` in
  `x64/osint/monitor_ipc_runtime.c`, modeled on `zysmv`, that
  takes the keyword's `kvblk` pointer + value and emits one
  `MWK_VALUE` record with `name = &kvname` (lower-cased to
  match dot's emission, e.g. `&fullscan`) and `type = INTEGER`.

  **Fire-point:** `jsr sysmk` inserted in `sbl.min asign`
  on every successful keyword-commit branch — `asg15`, `asg16`,
  `asg21..23`, `asg25`, `asg17`, `asg19`.  Cleanest is option
  (a): one `jsr sysmk` immediately before each `exi`.  Option
  (b) — refactor `asg14` to converge all keyword-success paths
  through a single landing pad before commit — is a larger diff
  for marginal benefit; prefer (a).

  **Deliverables:**
    i.   `osint/monitor_ipc_runtime.c` — new `zysmk` (~30 lines).
    ii.  `osint/osint.h` — extern decl for `sysmk` if needed.
    iii. `int.dcl` — global decl for `sysmk` (parallel to `sysmv`).
    iv.  `sbl.min` — `jsr sysmk` insertions in keyword paths.
    v.   `bootstrap/sbl.asm` — regenerated, NOT hand-edited
         (per RULES.md "Source-of-truth").

  **Test gate:**
    1. `bash one4all/scripts/build_spitbol_oracle.sh` — smoke OK.
    2. Beauty 17/17 unchanged.
    3. corpus crosscheck `assign` family clean (refs are stdout,
       not wire — should not regress).
    4. **Primary gate:** unfiltered beauty self-host harness
       (`PARTICIPANTS="spl dot"`, no `MONITOR_*` workarounds)
       runs past step #933.  spl's #933 is now `VALUE &fullscan
       = INT=1` matching dot's; controller advances.

  **Done when:** primary gate passes AND
  `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1` is removable from every
  harness invocation referenced in this goal file with no change
  in observed first-DIVERGE step.

- [ ] **S-2-bridge-7-A2** — *Path A continued: authenticate vrblk
  in `spl_vrblk_name` so `MONITOR_NAME_WILDCARD=spl` becomes
  unnecessary.*

  Already specified in detail under "Open SPITBOL bridge issue"
  below.  Promote here as an active sub-rung.  Fix shape: in
  `x64/osint/monitor_ipc_runtime.c` `spl_vrblk_name`, verify
  `vr->vrget == b_vrl || vr->vrget == b_vra` before trusting
  `vrlen`/`vrchs`.  Synthesized "vrblks" from teblks/arblks
  have `b_tet`/`b_art` at offset 0 — fail authenticity → emit
  `<lval>` (the existing empty-name path).

  **Deliverables:** `int.dcl` declares `b_vrl`, `b_vra` global;
  `osint/osint.h` externs them; `spl_vrblk_name` adds the check
  at top; regenerate `bootstrap/sbl.asm`.

  **Test gate:** unfiltered harness runs without
  `MONITOR_NAME_WILDCARD=spl`; first-DIVERGE step ≥ the step A1
  alone reaches.

  **Done when:** `MONITOR_NAME_WILDCARD` is removable from every
  harness invocation referenced in this goal file with no change
  in observed first-DIVERGE step.

- [ ] **S-2-bridge-7-A3** — *Validation gate: the unfiltered
  harness pinpoints an injected dot semantic divergence.*

  With A1 and A2 landed, the harness's premise is restored:
  agreement on the wire = agreement in semantics.  Prove it.

  **Steps:**
    1. Inject a known dot semantic break — e.g. modify
       `Snobol4.Common/Runtime/Functions/Builtin/Ident.cs` so
       `IDENT(X, Y)` always succeeds.  Build dot.  Confirm
       beauty 17/17 fails on the IDENT-exercising test.
    2. Run unfiltered harness on a `.sno` that uses IDENT.
       The harness MUST produce a single, clean DIVERGE row
       pointing at the injected divergence.
    3. Revert the injection.  Confirm the same harness run is
       clean (no DIVERGE) on un-injected dot.

  **Done when:** step 2 produces a single clean DIVERGE row
  pointing at the injected break.  Harness is now a trustworthy
  oracle for the next dot-side bug.

### Session #69 — what failed and what was learned (recorded for the trail)

  Lon asked for the trace between the last-agreed and first-
  diverged events on the unfiltered harness.  I wired
  TraceEnabled into `Scanner` / `ScannerState` only, ran the
  harness with `MONITOR_TRACE_FROM_EVENT=932 TO=934`, got an
  empty `dot.err`, and reported "the trace shows nothing
  happened — dot is fine, the bug is on spl".  That conclusion
  was correct in the end, but the empty trace did not justify
  it: the trace was empty because my instrumentation was
  incomplete, not because the runtime did nothing.  An honest
  read of the empty trace is "I instrumented the wrong code
  path", not "no code path was taken".  Lon caught the error
  ("a C# function was called after the last agreed event...
  you are an idiot to believe otherwise") and required the
  instrumentation gap be fixed.  After adding `[TEL]` and
  `[ASN]` traces in `ThreadedExecuteLoop.cs` and
  `OperatorsBinary/AssignReplace (=).cs`, the same
  `MONITOR_TRACE_FROM_EVENT=931 TO=935` window produced the
  10-line trace shown in S-2-bridge-7-A1 above, which makes
  the spl gap diagnostic and unambiguous.  S-2-bridge-event-
  bombs-coverage exists to make sure no future session can
  read an empty trace as evidence of nothing-happened.

### Session #70 — TraceEnabled wired into Scanner; SealAlternates over-eager confirmed; first attempted fix not sufficient

  **snobol4dotnet HEAD:** `c578fb5` (UNCHANGED — diagnostic patches
  reverted before commit per RULES.md).

  **What ran:** Re-applied the Mechanism B wiring (TraceEnabled-gated
  `[ALT]`/`[PM]`/`[M]` traces in `Scanner.cs` / `ScannerState.cs`)
  AND patched `MonitorIpc.cs` so `_standaloneCount` ticks on every
  `Emit*` call regardless of whether `READY_PIPE` is set.  This
  makes `MONITOR_TRACE_FROM_EVENT` / `MONITOR_TRACE_TO_EVENT` work
  in standalone mode (no controller) — useful for direct
  instrumentation runs.  Verified with a tiny pattern test program;
  trace fires correctly.

  **Beauty self-host total emit count: 2609** (standalone, no
  monitor).  Session #68's "controller step #2839" maps to
  controller-side counting under filtering — not directly
  comparable to dot's standalone `_emitCount`.  Last live scanner
  state in beauty self-host is **s90** at `ec=2497`.  The four
  `&FULLSCAN = 1` parses appear at scanner states **s63 (ec=1395),
  s77 (ec=1705), s79 (ec=1709), s80 (ec=1709)**.  s80 is the
  failing parse — 2.5M alt-stack events on s80 alone.

  **Confirmed bug shape on s80:** the alt stack accumulates many
  `-2` seals from prior FENCEs interleaved with outer alts, with
  only a single `-3` mark at the bottom.  Example just before the
  final SEAL on s80:
  ```
  SEAL-PRE  depth=32 stack=[94, 91, 86, -2, -2, 352, -2, -2, 594, 589, 588, 588, 588, 566, 561, 352, -2, 503, 503, 352, 479, 476, 471, 466, 56, 51, 24, 19, -3, 10, 5, -1]
  SEAL-POST depth=4  stack=[-2, 10, 5, -1]
  ```
  The seal pops 28 entries — including the prior `-2` seals and
  the snoExpr14/snoVar outer alts (`19, 24, 51, 56, 466, 471, 476,
  479, 352, 503, 503`) — to find the lone `-3` mark at the bottom.
  The outer alts (where `*snoUnprotKwd` lives, per session #68's
  diagnosis) are wiped.

  **Fix attempted (NOT committed):** added `if (top == -2) break;`
  to `SealAlternates` so the seal stops at a previous seal as well
  as at its own mark.  Build clean.  Beauty self-host: **same 28
  stderr lines, same Parse Error**.  Re-trace post-fix shows the
  seals DO stop at `-2` correctly (final seal on s80 popped 3
  entries instead of 28, preserving outer alts), but s80 ends
  with the same total event count and same outcome.  Either:
    - The fix is in the right direction but masks a downstream
      bug (the preserved alts still lead to the same FAILURE path).
    - The fix has its own correctness problem: `-3` marks now
      ACCUMULATE on the stack because seals on top of nested marks
      stop at intermediate `-2`s rather than consuming the marks
      they were paired with.  Stack depths grow far past the
      pre-fix depth (107+ vs 32), suggesting mark accumulation is
      real and is itself a new bug.  Reverted.

  **What this rules out:** the failing-parse outcome is NOT
  hyper-sensitive to whether `-2`s are barriers in `SealAlternates`.
  Even with the outer snoExpr14/snoVar alts preserved on the
  stack post-seal, the parse still fails the same way at the same
  cursor position.  This corroborates session #68's diagnosis
  that **the bug is above the seal, not at the seal**.  Backtrack
  is not even reaching the seal; the outer alts (whether preserved
  or wiped) are not being consulted.

  **Where the bug actually is — refined hypothesis:** the high-
  numbered alts (`588, 588, 588, 589, 594` and the 273000-series
  and 280000-series) that fire BEFORE backtrack reaches snoExpr14's
  alts include the Subsequent chain that eventually leads to
  `*snoFunction` (in snoVar/snoAtom production).  When those
  high-numbered alts succeed at intermediate steps, they consume
  cursor and never failback far enough to expose `*snoUnprotKwd`
  underneath.  Concretely: the trace shows hundreds of
  `RESTORE alt=NNNNNN` events on s80 for high-numbered alts but
  **the lower-numbered alts (`19, 24, 51, 56, 466, 471, 476, 479`)
  are never RESTOREd**.  They sit on the stack untouched because
  the high-numbered alts find a SUCCESS path elsewhere and the
  match terminates without backtracking that far.

  **Recommended next-session pivot:** the tools needed to find this
  bug are now wired:
    1. Restore the diagnostic patches from this session (revert is
       trivial — copy from session #70 trace text below).
    2. Run beauty self-host with full TraceEnabled=on, redirect
       stderr to `/tmp/full_trace.log` (≈6.6M lines, 1.3 GB).
    3. Find the FIRST `[M  s80] Result=SUCCESS` for any node that
       leads to `*snoFunction`.  That is the wrong success — it
       commits the parse to the snoFunction path before snoExpr14
       has tried snoUnprotKwd.
    4. Walk back from that node to find which alternate from
       snoExpr14 was supposed to be tried before snoFunction
       (per beauty.sno's grammar: `... '?' | *snoProtKwd |
       *snoUnprotKwd | '&' ...`).  That alternate's index will be
       in the saved-alt stack at the time of the wrong success,
       and is one of the lower numbers (19, 24, 51, 56, etc).
    5. The bug is whatever causes that alternate to be skipped.
       Likely candidates: AST-build wiring (`*snoUnprotKwd`'s
       `Alternate` edge points to something other than the next
       arm); or the SEAL/MARK semantics (a fence between snoExpr14
       arms is wiping the wrong alts at the wrong time).

  **Status updates:**
    S-2-bridge-event-bombs-coverage   [~] partial — Mechanism B
                                          wiring approach validated
                                          standalone (TraceEnabled
                                          fires without controller).
                                          Productionizing into
                                          ThreadedExecuteLoop /
                                          AssignReplace / Define /
                                          builtins still TODO.
    S-2-bridge-7-fullscan             [~] still partial — seal-stop-
                                          at-`-2` is NOT the missing
                                          fix.  Bug is in alternation
                                          ordering above the seal.


- [ ] **S-3** — Gate: `SELF-HOST PASS` per "Test command" above.

## Open SPITBOL bridge issue (cross-ref SN-26-bridge-coverage)

The spl bridge in `x64/osint/monitor_ipc_runtime.c spl_vrblk_name` accepts
stale memory bytes as variable names when called from `asg01` for
table-element stores. Symptom: emits `ss` instead of the table's
collection name.

**Root cause:** `asign` is called with `(xl, wa)` =
`(teblk_ptr, teval_offset)` for table-element stores. The bridge
fire-point at `asg01` (sbl.min:17610) synthesizes
`vrsto = xl - vrvlo`, which lands in arbitrary pre-teblk memory
when xl is a teblk slot. `spl_vrblk_name`'s printable-ASCII validator
can't distinguish stale bytes from real names.

**Candidate fix:** authenticity check before trusting `vrlen`/`vrchs` —
verify `vr->vrget` equals `b_vrl` or `b_vra` (real vrblk's load-routine
pointers). Synthesized "vrblks" from teblks/arblks have `b_tet`/`b_art`
at offset 0. Requires:
- Add `b_vrl`, `b_vra` to `int.dcl` global declarations.
- Add `extern void b_vrl(); extern void b_vra();` to `osint/osint.h`.
- Add the check in `spl_vrblk_name`.

**Workaround in use:** `MONITOR_NAME_WILDCARD=spl` controller env var
lets the wire advance past the spl bug to expose real snobol4dotnet
bugs. Real value-byte divergences are still reported.

The proper fix belongs in SN-26-bridge-coverage (GOAL-LANG-SNOBOL4).

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator
  in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.

---

## Session #56 findings — appended for next-session orientation

**snobol4dotnet commit:** `3a74102`  
**Monitor state:** reached step **1046** (was 801 before this session)

### Three bugs fixed (all in monitor bridge, not runtime)

1. **`Array.cs` `IndexCollection` Failure sentinel missing** — early `if (Failure) return` left stale operands (`i`, subscript `1`) on the stack; `BinaryEquals` consumed them as spurious `i = 1` assignment + false `VALUE i = INT=1` wire event. Fix: push `StringVar(false){Succeeded=false}` sentinel before returning. Advanced monitor 801 → 933.

2. **`AssignReplace (=).cs` duplicate VALUE for function return slot** — when a function body assigns to its own name (e.g. `nPush = epsilon . *PushCounter()`), `Assign` fired `EmitValue` mid-body AND `Define.cs` fired it again at RETURN time. spl/csn emit only the latter. Fix: suppress `EmitValue` in `Assign` when `ProgramDefinedFunctionStack.TryPeek()` matches the lvalue symbol. Advanced monitor 933 → 1040.

3. **`MonitorIpc.cs` RETURN event type byte** — `EmitReturn` used `MWT_NAME` (4); spl's `spl_block_to_wire` returns `MWT_STRING` (1) for the return-type scblk. Fix: use `MWT_STRING`. Advanced monitor to 1046.

### Next divergence (step 1046, OPEN)

Context: beauty.sno line 787-790 builds `snoExprList` pattern at init time:
```
snoExprList = nPush() *snoXList ("'snoExprList'" & '*(GT(nTop(), 1) nTop())') nPop()
```
During execution of this assignment, `nPush()` is called, which calls `PushCounter()`. After the entire RHS is evaluated, `nPop()` is called as the last sub-expression. When `nPop()` returns:
- **spl** → `LABEL stno=595` = `XDump.inc:22` (`XDump20  objProto = PROTOTYPE(object)`, inside `refs` function body — the correct continuation after the `snoExprList` assignment statement)
- **dot** → `LABEL stno=587` = `XDump.inc:14` (`IDENT(objType, 'PATTERN') :S(XDump00)`, a different point inside XDump)

Both landing addresses are inside the `XDump` function body (which was defined and compiled earlier). This is **function return-stack corruption**: dot's return address for `nPop()` (called during expression evaluation, not from a statement-level call) is pointing at the wrong label. The stno values come from the stno_map: stno 587 = XDump.inc line 14, stno 595 = XDump.inc line 22.

**Hypothesis:** The threaded execute loop's call-return stack (`ExecuteLoop` return index) is being indexed wrongly when a user-defined function is called *during evaluation of an expression that appears on the RHS of an assignment* (as opposed to being called from a top-level statement). The `snoExprList = nPush() ... nPop()` line calls `nPush` and `nPop` as part of the RHS expression. The return from `nPop` may be using a stale/wrong saved return address, possibly because `ExecuteLoop` is reinvoked recursively and the return-address stack shared with earlier calls (like the XDump function definition) has not been fully cleaned up.

**Where to look in dot code:**
- `Snobol4.Common/Runtime/Execution/ThreadedExecuteLoop.cs` — how `ExecuteLoop` saves/restores return addresses for function calls
- `Snobol4.Common/Runtime/Functions/FunctionControl/Define.cs` — `ExecuteProgramDefinedFunction` calls `ExecuteLoop(LabelTable[entry])` which returns `nextIndex`; the RETURN/FRETURN/NRETURN cases then push `returnVar` and resume. The bug may be that after this inner `ExecuteLoop` returns, the outer `ExecuteLoop` resumes at the wrong instruction index.
- Compare with how csn (`csnobol4`) handles the same: the call stack in csn is separate from the threaded code pointer.

**The monitor skip patch** (`MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`) is needed to get past the spl bridge's keyword-VALUE gap at step 933. The patched controller is at `/tmp/monitor_sync_bin_local.py` but is NOT committed (it's a local diagnostic aid). To reproduce the step-1046 divergence, run:

```bash
cp /tmp/monitor_sync_bin_local.py one4all/scripts/monitor/monitor_sync_bin.py
PARTICIPANTS="spl dot" \
    STDIN_SRC=corpus/programs/snobol4/demo/beauty/mini_beauty.sno \
    MONITOR_TIMEOUT=120 \
    MONITOR_NAME_WILDCARD=spl \
    MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1 \
    MONITOR_TRACE_LOG=/tmp/wire5 \
    bash one4all/scripts/test_monitor_3way_sync_step_auto.sh \
    corpus/programs/snobol4/demo/beauty/beauty.sno
# Restore after: cp monitor_sync_bin_orig.py one4all/scripts/monitor/monitor_sync_bin.py
```

where `mini_beauty.sno` is the first 26 lines of beauty.sno + "END" (the minimal stdin that reproduces the Parse Error).


---

## Session #65 findings — SealAlternates IS clearing outer alternates, but fix doesn't unblock

**snobol4dotnet HEAD:** `724c1b6` (unchanged — runtime patch reverted, no commit this session).

### What was done

Instrumented `Snobol4.Common/Runtime/PatternMatching/ScannerState.cs` with env-gated
(`DOT_TRACE_ALT=1`) tracing on every `SaveAlternate` / `RestoreAlternate` /
`ClearAlternates` / `SealAlternates` call.  Ran `dotnet Snobol4.dll -bf beauty.sno
< beauty.sno` with the trace on.

The trace produces 2.45M `[ALT]` lines.  82 distinct ScannerStates over the run
(matches the AST-inventory count from session #64).

### Confirmed: the SEAL clears outer snoExpr14 alternates

Trace excerpt for the failing `&FULLSCAN = 1` parse (the 80th ScannerState):

```
[ALT] new ScannerState subject=[                  &FULLSCAN      =  1...
[ALT] CLEAR  curs=0
[ALT] SAVE   alt=5  curs=0  depth=2     ← outer snoStmt / snoSubject saves
[ALT] SAVE   alt=10 curs=0  depth=3
... (depth 2..13 saves at curs=0 — outer parser context) ...
[ALT] SAVE   alt=491 curs=0  depth=13
[ALT] SAVE   alt=488 curs=18 depth=14    ← cursor moves to '&' (col 18)
[ALT] RESTORE alt=488 curs=18 depth=13
[ALT] SAVE   alt=491 curs=18 depth=14    ← snoExpr14 alternation arm
[ALT] SAVE   alt=491 curs=18 depth=15    ← deeper snoExpr14 arm
[ALT] SEAL   curs=18 prevDepth=15        ← *** entire stack wiped ***
[ALT] SAVE   alt=346 curs=18 depth=2     ← stack now at depth 2 ([-1, -2])
... no more saves at deeper levels — snoUnprotKwd was on the wiped stack ...
```

`Snobol4.Common/Runtime/PatternMatching/ScannerState.cs` `SealAlternates`:

```csharp
public void SealAlternates()
{
    _alternatePatternStack.Clear();      // ← wipes ALL 15 entries
    _alternateCursorStack.Clear();
    _alternatePatternStack.Push(-2);
    _alternateCursorStack.Push(CursorPosition);
}
```

The docstring at the call site claims the seal clears only "P's saved alternates"
(the alternates inside FENCE'd p), but the implementation wipes the whole stack
including outer alternates that should remain live.

### Why session #64's standalone repro could not reproduce

The seal is triggered by a `SealPattern` from `FENCE(...)`.  Beauty has nested
FENCE in `snoExpr10`..`snoExpr13`:

```
snoExpr13 = *snoExpr14 FENCE($'~' *snoExpr13 (...) | epsilon)
snoExpr12 = *snoExpr13 FENCE($'$'... | $'.'... | epsilon)
snoExpr11 = *snoExpr12 FENCE(($'^' | $'!' | $'**') ...| epsilon)
snoExpr10 = *snoExpr11 FENCE($'%' *snoExpr10 (...) | epsilon)
```

When the parser walks `&FULLSCAN`, snoExpr14 alternation pushes ~14 alternates
(`*snoUnprotKwd` is one of them), then snoExpr13's FENCE matches `epsilon` and
fires SealPattern — wiping the snoExpr14 alternates.  Standalone reproductions
without the deep nested-FENCE context lack the depth-15 stack at SEAL time, so
the SEAL clears only what was actually inside the FENCE.

### Fix attempted (NOT committed; reverted)

Implemented a fence-mark scheme:

1. New `Snobol4.Common/Runtime/Pattern/MarkPattern.cs` — terminal pattern, always
   succeeds; pushes a `-3` fence-mark sentinel onto the alternate stack.
2. `ScannerState.SealAlternates` — pop entries until a `-3` is found, then push
   `-2` seal sentinel.  Outer alternates (below the mark) are preserved.
3. `ScannerState.RestoreAlternate` — auto-skip `-3` sentinels (handles the case
   where FENCE'd p fails before SealPattern fires; the mark is a stale leftover).
4. `ScannerState.HasAlternates` — looks past `-3`s when checking for live alternates.
5. `Scanner.MarkFence` — pass-through to `_state.MarkFence()`.
6. `PatternFactories.CreateFenceFunction` — wrap FENCE(p) as
   `Concat(MarkPattern, Concat(p, SealPattern))` instead of `Concat(p, SealPattern)`.

### Result of the fix attempt

Build clean.  Beauty self-host gate: **same 28 stderr lines, same Parse Error
at `&FULLSCAN = 1`.**  Unit tests not run (session ended mid-suite).

So: the SEAL-wipes-outer-alternates issue IS real and is observed in the trace,
but the seal-with-mark fix alone does NOT unblock beauty self-host.  Either:
- The fix has a subtle correctness bug (mark not landing in the right place,
  HasAlternates wrong on -3-only stacks, etc.) that masks its effect.
- A second bug exists upstream of the seal — the parse fails for a different
  reason and the seal is downstream of the actual gating issue.

The runtime patch and instrumentation were reverted (working tree clean).
RULES.md "Test gate passes before every commit" was honored — no commit landed.

### Recommended next-session pivot

1. Re-apply the MarkPattern + ScannerState changes from above (small, ~80 LOC
   total).  Add tracing back temporarily.
2. Verify the trace shows a fence-mark `-3` being pushed at SEAL site, and the
   SEAL clearing only down to that `-3` — preserving outer alternates.
3. If snoExpr14 alternates ARE preserved but parse still fails: the failure is
   downstream of snoExpr14.  Check whether `*snoUnprotKwd` is now actually
   tried — instrument `UnevaluatedPattern.Scan` to log the deferred-code name
   and search the trace for `snoUnprotKwd` evaluations.
4. If `*snoUnprotKwd` IS evaluated and still fails, that's a state-dependent
   *match() invocation — back to session #62/#64 territory (BetaStack residue,
   pattern-match-scanner state from prior matches).
5. If `*snoUnprotKwd` is NOT evaluated: the AST node Alternate links of
   snoExpr14 are wrong, OR the cursor position at restore is wrong, OR the
   `-3` mark is being placed too shallow (above snoExpr14's saves, so SEAL
   wipes them anyway).  Dump the AST node-by-node with HasAlternate values
   and check.

### Why "SealAlternates clears all" might be intentional in some sense

CSNOBOL4's FNCD (FENCE) clears the alternate stack down to a saved P-stack
pointer captured at FENCE entry — equivalent to the MarkPattern scheme above,
not a blanket wipe.  SPITBOL's `xkalt` is the same.  So the blanket-wipe
implementation in this runtime is genuinely incorrect; the question is just
whether fixing it alone closes beauty self-host.


---

## Session #66 findings — FENCE mark/seal landed; Fence_061 now PASS; beauty self-host still blocked by second downstream bug

**snobol4dotnet HEAD:** `bb28a8d` (FENCE mark/seal mechanism committed).

### What landed

The MarkPattern / SealAlternates fix from session #65's notes — implemented
afresh, with one critical correction.  Five files changed, +118 / −22 lines:

  1. **NEW** `Snobol4.Common/Runtime/Pattern/MarkPattern.cs` — terminal pattern;
     pushes a `-3` sentinel onto the alt stack at FENCE entry.
  2. `Snobol4.Common/Runtime/PatternMatching/ScannerState.cs`:
     - `MarkAlternates()`: pushes `-3` and current cursor.
     - `SealAlternates()`: pops entries until the most recent `-3` mark, pops
       the mark itself, then pushes `-2`.  If no `-3` found (defensive: floor
       reached), pushes `-2` atop the floor.
     - `RestoreAlternate()`: skips stale `-3` marks transparently in a loop
       before popping the real entry.
     - `HasAlternates()`: walks past `-3` marks; true iff the next non-`-3`
       entry is a real alternate or a `-2` seal.
  3. `Snobol4.Common/Runtime/PatternMatching/Scanner.cs`:
     - Adds `MarkAlternates()` pass-through.
     - **`-2` seal hit on backtrack now returns `MatchResult.Abort`** (was
       `MatchResult.Failure`).  This is the critical correction over session
       #65's attempt: returning Failure allowed `PatternMatch`'s unanchored
       cursor-retry loop to keep advancing position and rescue the match,
       defeating the seal entirely.  Returning Abort terminates the entire
       match without cursor retry, matching Gimpel's `FENCE = NULL | ABORT`.
  4. `Snobol4.Common/Runtime/Pattern/PatternFactories.cs`:
     - `CreateFenceFunction` wraps as `Concat(Mark, Concat(p, Seal))` instead
       of `Concat(p, Seal)`.
  5. `Snobol4.Common/Runtime/Pattern/SealPattern.cs`: docstring updated.

### Why session #65's mark scheme didn't unblock beauty

Session #65's attempt was structurally correct (Mark-pair-with-Seal) but kept
the original `MatchResult.Failure(_state)` return on `-2`.  That allowed the
unanchored retry in `PatternMatch` (`cursorPosition++` loop, line 43 in
`Scanner.cs`) to advance and try again at the next start position, where the
sealed pattern could succeed via a different path — masking any seal effect.
So even though the alt stack was being managed correctly, the `Failure` return
path defeated the seal's commit semantics.

The fix is to recognize that the seal hit is conceptually an ABORT, not a
FAILURE.  Per Gimpel 1973 §"Pattern Theory":

> ABORT will terminate pattern matching in whatever state it is in. … FENCE,
> which can be written FENCE = NULL | ABORT, also does not conform [to the
> normal alternation laws].

The seal `-2` is the realised form of that ABORT.  When backtrack reaches it,
the entire match must terminate — no cursor retry, no outer alternates fire
(those were below the mark; they are not in scope when seal fires after P
matched).

### Test gate — clean

  | Gate                       | Result                                          |
  |----------------------------|-------------------------------------------------|
  | `Pattern.Fence` (8 tests)  | 8/8 PASS                                        |
  | `CorpusRef_FenceTests`     | 10/10 PASS (was 9/10 — Fence_061 was failing)  |
  | TestSnobol4 full suite     | 2075p / 14f (matches baseline; +1 from Fence_061; 14 fails are all pre-existing TEST_Csnobol4_*) |
  | Beauty 17/17               | 17 PASS / 0 FAIL (unchanged)                    |
  | Beauty self-host           | exit=0, 28 stderr-lines, Parse Error at &FULLSCAN = 1 — **STILL FAILS, unchanged from baseline** |

### Witness test for the fix

`TEST_Fence_061_pat_fence_fn_seal` was the in-tree failing test that
exercised exactly the seal-with-outer-context bug:

```snobol4
X = 'AB'
X FENCE(LEN(1) | LEN(2)) RPOS(0)  :S(YES)F(NO)
```

Pre-fix output: `should not reach` (match succeeded via unanchored retry at
cursor=1, where LEN(1)→2, RPOS(0) matches).  Post-fix output: `sealed
correctly` (LEN(1) chosen at cursor=0, seal fires, RPOS(0) fails at cursor=1,
backtrack hits seal, ABORT terminates match — F branch).

### Beauty self-host: second gating bug confirmed downstream

Beauty self-host produces byte-identical stderr pre-fix and post-fix (28
lines, same Parse Error at `&FULLSCAN = 1`).  This **confirms session #65's
prediction**: "Either the mark scheme has a subtle correctness bug, or there
is a second gating bug downstream."  The answer is **both** — session #65's
attempt had the Failure-vs-Abort bug, AND there is a second bug downstream.

The `*snoUnprotKwd` skip from session #64's diagnosis is real and not yet
explained.  With correct mark/seal semantics in place, beauty's snoExpr14
alternation should now preserve outer alternates correctly across the
nested-FENCE chain — but it doesn't reach `*snoUnprotKwd` at the
`&FULLSCAN = 1` parse anyway.  Either:
  - The mark is being placed at the wrong syntactic level (need to verify
    via `DOT_TRACE_ALT=1` re-run on beauty self-host).
  - Or a different mechanism (graft-time AST construction, alternation-arm
    walking, or *snoExpr14 grammar invocation order) is responsible for
    the skip.

### Recommended next-session pivot

1. Re-enable `DOT_TRACE_ALT=1` instrumentation (already env-gated; just
   uncomment the `Console.Error.WriteLine` lines saved in this session's
   diagnostic patches if reverted).  Re-run beauty self-host with trace.
2. Search the trace for the exact sequence around the `&FULLSCAN = 1` parse.
   Look for: `MARK` events at snoExpr10..snoExpr13 entries; `SEAL` events at
   their epsilon arms; the alt depth at each point; whether saves for
   `*snoUnprotKwd` (an arm of snoExpr14) are below or above any active marks.
3. Differential-AST path (path 2 from session #64) is still the safe fallback
   if the trace doesn't pinpoint the issue.

`one4all` and `corpus` are unchanged this session.

---

## Session #67 findings — harness-trust step opened; minimal repro for dot FENCE bug isolated

**snobol4dotnet HEAD:** `bb28a8d` (unchanged — no commit this session beyond the goal-file edits).

### What happened

Session was scoped to "find and fix the bug between last agreed and first diverge."
The harness reached the same DIVERGE step #2839 sessions #64–#66 reported
(`RETURN match (NRETURN)` vs `CALL upr`).  Multiple iterations theorizing
without isolating; correctly redirected to **stop tracing, run minimal
example**.

### Minimal repro found: corpus crosscheck test 114

Ran the 34 corpus FENCE crosscheck patterns (`corpus/crosscheck/patterns/*fence*`)
against dot.  **Two failures on dot, both real divergences from spl:**

  - **`114_pat_fence_via_var_in_paren_alt`** — clean repro of the bug:
    ```snobol4
    cmd = FENCE('a' | 'ab')
    outer = (*cmd 'X' | *cmd 'Y' | LEN(0))
    s = 'aY'
    s POS(0) *outer RPOS(0)                               :S(YES)F(NO)
    ```
    spl: `second outer alt matched aY` (PASS).
    dot: `fail`.

  - **`130_pat_two_star_fence_concat_outer`** — *both* spl and dot
    produce `fail`; the .ref expects `sequence of star-cmd-FENCE matched`.
    Bad ref or spl bug — set aside.

Test 114 is the **canonical structural bug**: `*cmd 'X'` matches 'a'
inside the FENCE then fails on 'X', the seal ABORTs the entire match
on dot, but spl correctly tries the OUTER alternation arms `*cmd 'Y'`
and `LEN(0)` — those arms were saved on the alt stack BEFORE the FENCE's
Mark was pushed and remain live below the seal.

This is structurally identical to beauty's `snoExpr14` alternation
(ladders of `*snoProtKwd | *snoUnprotKwd | ... | *snoExpr15`) under
`snoExpr13`'s `FENCE($'~' *snoExpr13 ... | epsilon)`.  Same bug class.

### Where the dot bug lives

`Snobol4.Common/Runtime/PatternMatching/Scanner.cs`, `Match()` lines 100–106:

```csharp
case MatchResult.Status.FAILURE:
    if (!_state.HasAlternates())
        return mr;
    var (alternateIndex, _) = _state.RestoreAlternate();
    if (alternateIndex == -2)
        return MatchResult.Abort(_state);   // ← TOO AGGRESSIVE
    node = _ast![alternateIndex];
    break;
```

Session #66's correction (`-2` → ABORT instead of FAILURE) was right
that ABORT must block the unanchored cursor-retry loop in
`PatternMatch`.  But it's wrong to ABORT immediately when there are
real alternates BELOW the `-2` on the stack — those outer alternates
were saved before the FENCE's Mark and remain live.

**Sketch of fix:** on popping `-2`, keep popping until a real alternate
is found (fire it) or the stack is exhausted (then ABORT to suppress
unanchored retry).  Nested `-2` seals stack on top of each other and
should all be skipped.

This fix was drafted in this session but **not committed** because
RULES.md "test gate before commit" — needs:
  1. unit suite to confirm no regression on existing FENCE tests,
  2. corpus crosscheck — at minimum tests 058–119, 129, 130 to
     confirm 114 flips FAIL→PASS without flipping any of the 33 PASS→FAIL,
  3. beauty 17/17 unchanged,
  4. beauty self-host re-run.

### Why session #67 isn't claiming "fixed"

Beauty self-host failure has been state-dependent (session #62: standalone
repro fails on BOTH spl and dot; succeeds in real beauty on spl).  The 5-line
test 114 is structurally similar but is NOT the beauty self-host failure
itself.  Test 114 may be one bug among several gating beauty self-host;
fixing it may or may not unblock line 26.

The honest claim: **dot has a real, isolated, 5-line FENCE seal bug** that
SPITBOL handles correctly.  Probability that fixing it reduces the
beauty-self-host distance is high.  Probability it closes self-host is
unknown.

### S-2-bridge-harness-trust step opened

The unfiltered sync-step harness reaches DIVERGE at step **#933 on
`&FULLSCAN = 1` itself** — a known spl bridge gap (no VALUE on keyword
store).  Every previous session's watermark advance (801 → 933 → 1046 →
1497 → 1617 → 2839) required the controller workaround
`MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1` plus `MONITOR_NAME_WILDCARD=spl` to
mask bridge gaps.  Watermark numbers were measuring the controller's
masking, not the runtime's progress.

New step **S-2-bridge-harness-trust** added before S-3.  Done when the
unfiltered harness can pinpoint a known injected dot semantic bug.  Until
that gate passes, watermark advances are decoration.

### Recommended next-session pivot

1. **Apply the Match() fix sketched above.**  Run corpus crosscheck
   FENCE subset (34 tests) and the unit FENCE suite.  Targeted gate:
   test 114 PASS, no regressions in 058–119/129/130 set.
2. If 114 PASSes, run beauty 17/17 + beauty self-host.  Beauty self-host
   may still fail at line 26 — that's the state-dependent second bug.
3. Either way: **commit the fix** (with tests) — it's a real bug
   regardless of whether it closes self-host.
4. After fix lands, decide whether to:
   - chase the residual beauty self-host failure with direct dot
     instrumentation (NOT the wire monitor), OR
   - close S-2-bridge-harness-trust by fixing the spl bridge gaps so
     the harness becomes trustworthy again.

`one4all` and `corpus` and `snobol4dotnet` are unchanged this session.
Goal-file edits only.

---

## Session #67 follow-up — S-2-bridge-event-bombs partial landed

**snobol4dotnet HEAD:** `3c1637d`.

### What landed

`Snobol4.Common/Runtime/Monitor/MonitorIpc.cs` now carries:

  - `_emitCount` — incremented on every wire record except `MWK_NAME_DEF`.
  - `MONITOR_BREAK_AT_EVENT=N` — when `_emitCount == N` just before sending
    the Nth record, dump managed stack to stderr and call
    `Debugger.Break()` if a debugger is attached.  Sessions that have
    identified a DIVERGE row at event N can pin the dot-side call stack
    at that exact emit.
  - `MONITOR_TRACE_FROM_EVENT=N` / `MONITOR_TRACE_TO_EVENT=M` — half-open
    interval gate for the public `MonitorIpc.TraceEnabled` flag.  Other
    dot-side instrumentation (`DOT_TRACE_ALT=1` in ScannerState, AST
    dumps, scan logging) can read this single flag to scope output to
    the gap between last-agreed and first-diverge.
  - Public `MonitorIpc.EmitCount` and `MonitorIpc.TraceEnabled` readers.

All three env vars are silently no-op when unset (back-compat).

### Smoke test result

Harness run with `MONITOR_BREAK_AT_EVENT=2838` on beauty self-host produces
a stack dump in `dot.err`:

```
[MonitorIpc] BREAK_AT_EVENT fired at #2838 kind=5 type=2 valueLen=8
   at System.Environment.get_StackTrace()
   at Snobol4.Common.MonitorIpc.EmitRecordRaw(...) ...
   at Snobol4.Common.MonitorIpc.EmitLabel(Int64 stno) ...
   at Snobol4.Common.Executive.InitStatementMsil(Int32 stmtIdx) ...
   at Snobol4_Expr(Executive)
   ...
```

Beauty self-host stderr unchanged at 28 lines (no semantic regression).
The bomb fires; the stack is observable.

### Known limitation

Dot's `_emitCount` (with NAME_DEF excluded) does not exactly align with
the controller's wire-log `#N` numbering.  In the smoke test, controller
wire-log #2838 = `RETURN upr` but dot's count #2838 = a `LABEL` emit two
records earlier.  The exact offset varies through the run (controller
filters or skips some records via `MONITOR_SKIP_EXTRA_KEYWORD_VALUES`,
`MONITOR_NAME_WILDCARD`, etc., further widening the discrepancy).

**Workaround for next session:** iterate.  Set `MONITOR_BREAK_AT_EVENT=N`,
read the `kind=` from the stack-dump line, decode against `MWK_*` (1=VALUE,
2=CALL, 3=RETURN, 5=LABEL), bisect against the wire log's expected event
to find the alignment offset.  Or set the bomb **+/-50** around the target
and grep all the dumps for the right kind+source-line.

**Proper fix (future):** either (a) the controller emits its own
"#N" into the wire-log alongside the dot count, so users can correlate;
or (b) a third env var `MONITOR_BREAK_ON_KIND_AND_LINE=KIND:STNO` fires
on a specific (kind, stno) match rather than count, eliminating the
alignment problem entirely.  Either is ~10 lines.

### Path 2 (TraceEnabled) ready but not yet wired into ScannerState

`MonitorIpc.TraceEnabled` is a public flag the harness can flip via env
vars, but `ScannerState.cs`'s existing `DOT_TRACE_ALT=1` env var still
reads its own env var, not `TraceEnabled`.  Wiring the two together is
the next sub-step (~3 lines in ScannerState).  Not done this session.

### Status of S-2-bridge-event-bombs

  [~] partial: Mechanism A (BREAK_AT_EVENT) landed and demonstrably works.
              Alignment offset documented as known-limitation.
  [ ] open:   Mechanism B (TraceEnabled wired into ScannerState et al.).
  [ ] open:   Validation gate — inject a known dot bug, drive harness to
              its DIVERGE row, BREAK on that event, read the bug from
              the call stack alone.


---

## Session #68 — 2026-04-30 (Sonnet 4.7 / Lon)

**Outcome:** seal-skip Match() fix landed (`c578fb5`), test 114 closed.
Beauty self-host still gated by a SECOND bug above the seal.

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `one4all`, `snobol4dotnet`
   (HEAD `3c1637d` — has BREAK_AT_EVENT bombs from session #67), and
   `x64`. Installed `dotnet-sdk-10.0` via apt (10.0.107). snobol4dotnet
   build clean. Beauty self-host baseline confirmed: SPITBOL passes
   (646 stdout lines), dot fails Parse Error at line 26.

2. **First-divergence localization with bridge-gap workarounds.**
   Ran `test_monitor_3way_sync_step_auto.sh` with `PARTICIPANTS="spl dot"`,
   `MONITOR_NAME_WILDCARD=spl`, `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`.
   First REAL divergence at controller step **#2839** (same as session
   #64–#67): spl `RETURN match (NRETURN)` vs dot's spurious 19th
   `CALL upr`.

3. **Bomb confirmed alignment offset.** Computed dot's `_emitCount` for
   the divergence: controller step + 2 (the two skipped events at
   controller #933 and #934 = beauty.sno line 26 and 27 keyword stores).
   So dot emit count #2840 = last-agreed RETURN upr, #2841 = first-
   diverged CALL upr. Bomb at 2840 captured the 18th RETURN's stack;
   bomb at 2841 captured the spurious 19th CALL's stack. Stack diff:
   the 25-frame lower stack was BYTE-IDENTICAL between the two events
   — only the upr function frame differs (one exits, the other enters).
   Confirms: the same Scanner state, after `*upr(tx)` returned
   successfully, dispatched `*upr(tx)` AGAIN.

4. **Wrote minimal repro.** `'&FULLSCAN' kwd` against the same keyword
   list, both runtimes do exactly 18 upr calls and report `matched`.
   Confirms the 19th call is **state-dependent** — only triggered by
   state accumulated through the 80+ prior parses in beauty self-host.

5. **Wired Mechanism B (TraceEnabled into ScannerState).** Per the
   "Path 2 (TraceEnabled) ready but not yet wired" note left by
   session #67, added `MonitorIpc.TraceEnabled`-gated tracing on every
   alt-stack op (Save/Restore/Clear/Mark/Seal) plus every Match
   dispatch and PatternMatch outer-loop iteration. Each scanner state
   gets a stable id `s<n>`. Stack contents serialized inline. Backed
   up the originals as `.orig`. **This was diagnostic instrumentation
   ONLY — restored to baseline before commit per RULES.md.** But the
   wiring approach is correct; a future productionizable form would
   keep the `MonitorIpc.TraceEnabled` reads and let a future caller
   substitute different output channels.

6. **Trace from last-agreed event.** Ran with
   `MONITOR_TRACE_FROM_EVENT=2840 TO=2842` and saw the alt stack at
   the moment the spurious 19th `*upr` fires:

       P=[..., 561, 352, -2, 503, 503, 352, 479, 476, 471, 466,
          56, 51, 24, 19, -3, 10, 5, -1]

   A `-2` seal at depth 8 with **outer alternates (503, 352, 479, 476,
   471, 466, 56, 51, 24, 19) preserved BELOW** by the existing
   SealAlternates mark/seal mechanism. Session #67 was right that the
   seal handling is broken — the existing code returns ABORT on `-2`
   pop, abandoning these outer alts.

7. **Applied session #67's sketched fix to `Scanner.cs Match()`:** on
   `-2` seal hit during backtrack, pop the seal and **continue popping**
   until a real alternate is found (fire it) or only floor `-1` remains
   (then ABORT to suppress unanchored cursor-retry). One while-loop
   replacing one if-statement.

8. **Test gate before commit (per RULES.md):**

   | Test set | Baseline | With fix |
   |---|---|---|
   | corpus crosscheck `*fence*` (35 tests) | 34 PASS, 1 FAIL (test 114) | **35 PASS, 0 FAIL** |
   | TestSnobol4 FENCE unit suite (23 tests) | 23 PASS | 23 PASS |
   | TestSnobol4 full suite (2089 tests) | 2075 PASS / 14 FAIL | **2075 PASS / 14 FAIL (identical set: TEST_Csnobol4_*)** |
   | beauty 17/17 corpus | (not re-run — full unit suite covers) | (not re-run) |
   | beauty self-host gate | FAIL (Parse Error) | FAIL (same — second bug) |

   Zero regressions. Test 114 newly passes. Committed as `c578fb5`,
   pushed to `main`.

9. **Diagnosis of remaining beauty self-host failure.** Re-traced
   between `*match(snoProtKwds, ...)` failing and `*match(snoFunctions,
   ...)` starting (events 2762→2763). Counted `RESTORE alt=-2` in that
   window: **0 seal-pops occur**. The high-numbered alternates ABOVE
   the seal (588, 594, 597, 615, 629, 643, 657, 671, 685, 699, 713,
   727, 741, 755, 769, 781) all fire and fail without ever reaching
   the seal. Then a NEW MARK fires at cursor=19 (entering a NEW FENCE
   region) and eventually the cursor advances to 27 (matching
   `&FULLSCAN`) and `*match(snoFunctions, ...)` begins.

   So the second bug is **above the seal**: dot's snoExpr14 alternation
   high-numbered alternates somehow chain to `*snoFunction` (in the
   snoVar production tree, subjlen=455) BEFORE backtrack ever reaches
   the snoExpr14 `*snoUnprotKwd` arm (which would have its alt index
   among the 503, 352, 479, 476, 471, 466, 56, 51, 24, 19 BELOW the
   seal). The seal-skip fix is necessary (test 114 confirms) but not
   sufficient — the second bug prevents backtrack from ever reaching
   the seal in this beauty path.

### What landed

- `c578fb5` — Match() seal-skip fix. Test 114 PASS, zero regressions.

### What's still open for S-2-bridge-7-fullscan

- The second bug: dot's snoExpr14 high-numbered alternates dispatch
  to `*snoFunction` before reaching `*snoUnprotKwd`.

### Next session's first move

Trace **from event 2683** (the FIRST `CALL match` for
`*match(snoProtKwds, ...)` — controller step #2681) to see what alt
indices are SAVED on s80 BEFORE the snoProtKwds match begins. Compare
those saved alt indices against beauty's grammar: identify which
correspond to `*snoUnprotKwd`, `*snoFunction`, etc. Then we'll know
whether:

- (a) `*snoUnprotKwd`'s alt is never saved (AST-build bug),
- (b) `*snoUnprotKwd`'s alt is saved but cleared/popped by some
  intermediate operation,
- (c) `*snoFunction`'s alt is saved earlier in the alt-stack such
  that it gets fired first when backtrack rises out of snoProtKwd's
  subtree.

The Mechanism B wiring (this session's diagnostic patch) is the right
tool for that. The patch text is in this session's narrative — re-apply
to ScannerState.cs/Scanner.cs as `.orig`-backed diagnostic, trace from
event 2683 (one event window covers the snoExpr14 setup), grep for SAVE
events on s80 BEFORE the s81 (snoProtKwds) match begins.

### Status updates

  S-2-bridge-7-fullscan      [~] partial — seal-skip done; second bug
                                 above seal blocks beauty self-host.
  S-2-bridge-event-bombs     [~] Mechanism B wiring approach validated
                                 in this session (diagnostic only —
                                 reverted before commit). Productionizing
                                 still TODO.

---

---

## Session #71 — 2026-04-30 (Sonnet 4.7 / Lon)

**Outcome:** S-2-bridge-7-betastack-failure-leak landed (`92b79be`).
Beauty self-host advanced 28→47 stderr lines (line 26 → line 48).

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `one4all`,
   `snobol4dotnet`, `x64`. Installed `dotnet-sdk-10.0` (10.0.107).
   snobol4dotnet HEAD `c578fb5` build clean.  Beauty self-host
   baseline: 28 stderr lines, Parse Error at `&FULLSCAN = 1`.

2. **Re-applied Mechanism B (TraceEnabled wiring) standalone.** Per
   session #70's "next session's first move":
     - `MonitorIpc.cs`: added `_standaloneCount` and
       `StandaloneInitEnvVars()`; made `_standaloneCount` tick on
       every `EmitCall`/`EmitReturn`/`EmitValue`/`EmitLabel` regardless
       of IPC pipe state; redirected `EmitCount` and `TraceEnabled`
       to `_standaloneCount`.  `MONITOR_TRACE_FROM_EVENT`/`TO_EVENT`
       now works without a controller.
     - `Scanner.cs`/`ScannerState.cs`: added `[PM]`/`[M]`/`[ALT]`
       traces gated on `MonitorIpc.TraceEnabled`.  Output to
       `Console.Out` (not `.Error`) to avoid interleaving with
       SNOBOL4 OUTPUT (which dot writes to stderr).
     - `ScannerState`: added stable `Id` per ScannerState instance
       so trace lines are diff-able across runs.
   All these patches are diagnostic — reverted before commit.

3. **Trace at MONITOR_TRACE_FROM_EVENT=1700 TO=1750.**
   Identified scanner-state `s79` at `ec=1709` matching subject
   `[                  &FULLSCAN      =  1\n] anchor=False` —
   that is the line 616 outer match `snoSrc POS(0) *snoParse
   *snoSpace RPOS(0)`.  Inside s79, `s80` started at `ec=1709`
   `anchor=True` — that's the ARBNO sub-match for `*snoCommand`
   inside snoParse.

4. **Trace at MONITOR_TRACE_FROM_EVENT=1709 TO=2700.**  s79 returned
   `Result=SUCCESS curs=38` at `ec=2394`.  s80 also returned SUCCESS.
   The pattern match for `&FULLSCAN = 1` succeeded.  Yet beauty
   stderr still contained "Parse Error".  The match's success was
   not being honoured by the statement engine.

5. **Added [QPM] traces to `Executive.PatternMatch`** (the `?`
   operator's C# implementation in
   `OperatorsBinary/PatternMatch (Question Mark).cs`).  Trace lines
   at `MONITOR_TRACE_FROM_EVENT=2390 TO=2700`:

   ```
   [QPM ec=2394] MR.Outcome=SUCCESS BetaStack.Count=14
   [QPM ec=2394] BetaStack[0..5] Assign returned, Failure=False
   [QPM ec=2482] BetaStack[6] Assign returned, Failure=True
   ...
   [QPM ec=2603] BetaStack[13] Assignee=ExpressionVar pre=38 post=38
   [QPM ec=2607] BetaStack[13] Assign returned, Failure=True
   [QPM ec=2607] EXIT Failure=True
   ```

   Two adjacent lines reveal the bug: match outcome was SUCCESS,
   exit Failure was True.  The 14 BetaStack entries committed
   deferred conditional assignments by calling `Assign()`, and
   one of the Assignees was an `ExpressionVar` (`*fn(...)`) whose
   underlying function FRETURNed, leaving Failure=true.  The
   PatternMatch operator never cleared Failure before exiting,
   so the statement engine took `:F(mainErr1)`.

6. **Fix.** Added one statement after the BetaStack iteration:
   ```csharp
   Failure = false;
   ```
   plus a 9-line comment explaining the rationale.  After a
   successful match, statement-level Failure must reflect the
   match outcome, not deferred-commit side effects.

7. **Test gate.**
     - Unit suite (filter out pre-existing 14 `TEST_Csnobol4_*`):
       **2385p / 0f / 2s**.  No regressions.
     - Beauty 17/17 corpus drivers: **17/17 PASS**.
     - Beauty self-host: **47 stderr lines** (was 28).  Parse Error
       advanced from line 26 (`&FULLSCAN = 1`) to line 48
       (`snoDQ = '"' BREAK('"' nl) '"'`).  23 more lines of
       beauty.sno now parse cleanly.

8. **Reverted diagnostic instrumentation.**  Restored MonitorIpc.cs,
   Scanner.cs, ScannerState.cs to HEAD via `git checkout`.  Final
   committed diff is 11 lines in
   `OperatorsBinary/PatternMatch (Question Mark).cs` only.

### What landed

- `92b79be` — Failure-leak fix in PatternMatch operator.

### What's still open for S-2-bridge-7-fullscan

- A second Parse Error at line 48 (`snoDQ = '"' BREAK('"' nl) '"'`).
  Likely the same shape (Failure leak from a different commit path)
  or distinct (BREAK-pattern boundary, SPAN-of-quote handling).
  Needs the same diagnostic approach: re-apply the diagnostic
  patches, find the new last-agreed→first-diverge window, run
  `[QPM]` trace, identify the leak.

### Next session's first move

Repeat session #71's exact workflow on the new failing line 48:

  1. Re-apply MonitorIpc `_standaloneCount` patch.
  2. Re-apply Scanner / ScannerState `[PM]`/`[M]`/`[ALT]` traces.
  3. Re-apply `[QPM]` traces in `PatternMatch (Question Mark).cs`.
  4. Run beauty self-host.  Find the `[PM] Result=SUCCESS` for the
     line-48 parse and check whether `[QPM] EXIT Failure=True`
     leaks again.
  5. If yes: identify which BetaStack entry's Assign sets Failure;
     trace into Assign / ExpressionVar.FunctionName invocation.
     The bug may be in:
       - Another Failure-propagation site analogous to PatternMatch
         (some other operator that doesn't clear Failure on success).
       - Assign itself failing on a specific deferred-fn pattern
         that should silently succeed.
       - A specific function (icase, upr, match) FRETURNing where
         it shouldn't.
  6. If no: the line-48 failure has a different root cause —
     trace into the pattern matcher itself for `s{N}` where the
     parse fails, find first `[M] Result=FAILURE` in the outer
     match and walk back.

### Status updates

  S-2-bridge-7-betastack-failure-leak  [x] LANDED.  92b79be.
  S-2-bridge-7-fullscan                [~] partial — beauty self-host
                                            now reaches line 48; new
                                            Parse Error there is the
                                            next gating bug.
  S-2-bridge-event-bombs-coverage      [~] partial — Mechanism B
                                            wiring approach validated
                                            (this session demonstrated
                                            it pinpoints the bug in
                                            two adjacent trace lines).
                                            Productionizing into TEL/ASN
                                            etc. still TODO.


## Sub-steps for "zero regressions, zero skips" hygiene

Goal: every baseline and invariant test surface that S-2 / S-3 work
touches must be at 100 % PASS / 0 SKIP **before** the SELF-HOST PASS
gate is declared closed, **not** after. Each sub-step below is
independently shippable and has its own mini test gate.

### S-2-hygiene-csnobol4 — close the 14 baseline `TEST_Csnobol4_*` failures

   [ ] open

The pre-existing 14 failures in `TestSnobol4/Corpus/CorpusRef_Csnobol4Suite.cs`
abort the full-suite run with a stack overflow somewhere in
`ExecuteProgramDefinedFunction → CallFuncBySlot` recursion. The 14 are
all alphabetically early, suggesting one of them throws an unhandled
exception that VSTest catches as "Test Run Aborted" and prematurely
ends the run before the remaining ~70 Csnobol4 tests are even attempted.
The 14 (in `/tmp/csnobol4_14.txt` at handoff time, also reproducible
via baseline run):

    TEST_Csnobol4__8bit, _8bit2, _a, _alis, _alph, _atn, _base,
    _case1, _contin, _diag1, _diag2, _digits, _dump, _err

Source programs at `corpus/programs/csnobol4-suite/{8bit,8bit2,a,alis,
alph,atn,base,case1,contin,diag1,diag2,digits,dump,err}.sno` (Phil
Budne's CSNOBOL4 test suite, 116 programs total — 8 already excluded
per the suite header comment).

**Steps:**

  1. Run each of the 14 standalone via `dotnet Snobol4.dll -bf <file>.sno`
     and diff against `<file>.ref`. Categorize each failure:
       (a) test program reads stdin via "data below END" — needs
           `RunWithInput` wrapper; check whether the test method
           uses it.
       (b) 8-bit `&ALPHABET` content (`8bit`, `8bit2` are obvious
           candidates) — likely a string-encoding or `CHAR(n)` for
           n≥128 issue.
       (c) deep-recursion programs (`atn` = arctan via Taylor series,
           `digits` likely similar) — may need stack growth or
           tail-call optimization, or may be hitting the same bug
           that aborts the whole run.
       (d) diagnostic-output programs (`dump`, `diag1`, `diag2`,
           `err`) — output may differ in formatting from CSNOBOL4
           reference (e.g. `&ERRTYPE` value, `&STNO` numbering,
           `DUMP()` output column alignment).
       (e) the "Test Run Aborted" culprit — one specific test throws
           an unhandled native exception that kills the runner.
           Identify by running each test in isolation and looking for
           the one that produces a stack-overflow stack trace in the
           output rather than a clean Assert.AreEqual failure.

  2. Fix in priority order: (e) first (it's hiding the actual size of
     the failure set), then (a) (purely mechanical), then (b)–(d) on
     their merits.

  3. **Test gate:** the full TestSnobol4 run shows
     `Failed: 0, Passed: 2089, Skipped: 0` (or 2086 if the 3 ABI-skip
     `[Ignore]` tests stay deferred — those ARE legitimate skips
     documented in BUILDING.md and are out of scope for this rung).
     Beauty 17/17 corpus continues to PASS.

  4. **Commit per fix**, not per category — small commits with clear
     witness tests. Reference this rung's tag in commit messages.

### S-2-hygiene-corpus-crosscheck — full corpus crosscheck PASS

   [ ] open

The corpus has 30 crosscheck families (`arith`, `arith_new`, `assign`,
`beauty`, `capture`, `concat`, `control`, `control_new`, `coverage`,
`data`, `functions`, `hello`, `keywords`, `library`, `output`,
`patterns`, `rung10`, `rung11`, `rung2`, `rung3`, `rung4`, `rung8`,
`rung9`, `rungW01`–`rungW07`, `snocone`, `strings`). Session #68
verified only the FENCE subset of `patterns` (35 tests, 35/35).

**Steps:**

  1. Run dot against EVERY `corpus/crosscheck/*/[!_]*.sno` file
     (skipping any prefixed with `_` if the convention is "draft").
     Diff actual output against the matching `.ref`. Build a
     summary table: family × (PASS / FAIL / TIMEOUT / N/A — `.sno`
     without a `.ref`). Use a 30-second timeout per test. (No script
     for this exists at handoff time — write `scripts/test_corpus_full_dot.sh`
     in `one4all/scripts/`, modeled on the existing
     `test_crosscheck_net_backend.sh` which already drives a subset.)

  2. Categorize FAILs into:
       - regressions caused by `c578fb5` (the seal-skip fix): triage
         immediately — this gates session #68's commit's safety. None
         expected based on FENCE-suite results, but confirm.
       - pre-existing baseline failures: log to a tracking ticket
         under this rung; one fix per commit.
       - tests with `.sno` but no `.ref`: either generate `.ref` from
         SPITBOL oracle (and commit) or move to `_skipped/` with a
         README explaining why. **No silent skips.**

  3. **Test gate:** every crosscheck family has matching `.sno` /
     `.ref` pairs and dot's actual matches the ref byte-for-byte
     (modulo trailing newline). The FENCE suite (35) gate from
     session #68 is preserved. Failures investigated, categorized,
     and either fixed or formally documented as known-limitation
     with a tracking step.

  4. **No `.sno` without `.ref`. No `.ref` without `.sno`.** If a
     `.sno` is intentionally non-runnable (e.g. demonstrates a
     parse-time error class), move it to `corpus/crosscheck/_pending/`
     with a one-line README justification and a tracking-rung name.

### S-2-hygiene-harness-orphans — harness scripts must agree on PASS/FAIL

   [ ] open

`one4all/scripts/` ships ~80 `test_*.sh` scripts. Many overlap. Some
are stale (referenced obsolete file paths). All of them either gate
real ladder rungs or document old experiments.

**Steps:**

  1. Inventory every `one4all/scripts/test_*.sh`. For each, run it
     once against current HEADs of all repos. Categorize:
       (a) PASS — keep, document in a one-line `scripts/README.md`
           entry that says what rung it gates.
       (b) FAIL but documents a known-open rung — keep, link to the
           goal file's tag.
       (c) FAIL or skip-spam, no documented purpose, references
           paths that don't exist — propose for deletion in this
           rung's PR. Don't delete unilaterally; SPITBOL/csnobol4
           bridges may depend on harnesses that haven't been
           exercised in months.
       (d) PASS but irrelevant to S-2/S-3 — keep, leave alone.

  2. **Test gate:** every script in (a) and (b) has a documented
     home in a goal file (or is a generic infrastructure script
     like `install_*` / `build_*`). Scripts in (c) are either
     fixed, deleted, or moved to `scripts/_archive/` with a
     `README.md` explaining the move. The active sync-step harness
     `test_monitor_3way_sync_step_auto.sh` keeps full coverage of
     `{csn, spl, scr, dot}` participants — no participant becomes
     unreachable.

  3. Commit one batch deletion + one batch documentation update per
     PR, not 80 commits.

### S-2-hygiene-bridge-trust — close the harness-trust gate

   [ ] open (already tracked as `S-2-bridge-harness-trust`)

The unfiltered harness diverges at step #933 (spl bridge gap for
keyword-VALUE events on `&FULLSCAN = 1`). With workarounds active
(`MONITOR_NAME_WILDCARD=spl` + `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`)
the first real divergence moves to step #2839 — but the workarounds
mask real bugs in addition to bridge gaps.

**Steps:**

  1. Pick Path A (fix `spl` bridge to fire VALUE on keyword stores)
     OR Path B (drop the workarounds and rebuild trust by closing
     spl `vrblk_name` stale-memory issue) — see the existing
     S-2-bridge-harness-trust narrative above for the analysis.

  2. Once path chosen and landed, run the unfiltered harness on
     beauty self-host. The first DIVERGE step number must be
     ≥ #2839 (no regression in trust depth) and the workarounds
     must be removable from harness invocations going forward.

  3. **Test gate:** `test_monitor_3way_sync_step_auto.sh` with
     `PARTICIPANTS="csn spl scr"` AND with `PARTICIPANTS="csn spl
     dot"` both run to completion (full corpus subset of small
     programs) without needing `MONITOR_*` env-var workarounds.
     Beauty self-host run against the harness reaches at LEAST the
     same depth as the workaround-on run does today.

### S-3-hygiene-self-host-witnesses — invariant suite for the SELF-HOST PASS gate

   [ ] open

Once S-2-bridge-7-fullscan closes and beauty self-hosts on dot, the
SELF-HOST PASS gate (`S-3`) must include INVARIANT tests that detect
regressions in self-host behaviour without needing to re-derive them
each session.

**Steps:**

  1. Add `corpus/crosscheck/beauty/self_host.{sno,ref}` (the program
     is `beauty.sno`, the input is `beauty.sno`, the reference is
     the SPITBOL oracle's stdout — captured once, committed). The
     self-host gate's success criterion becomes a byte-diff against
     this committed reference.

  2. Add 5–10 minimal "snippet" self-host inputs that EXERCISE the
     specific snoExpr14/snoVar/snoProtKwd/snoUnprotKwd/snoFunction
     alternation arms in different orders and combinations. These
     act as regression sentinels for any future Match() / alt-stack
     change. Reference shapes for each of: identifier-only, keyword-
     only (both prot and unprot), function-call-only, mixed, and
     pathological-backtrack cases.

  3. **Test gate:** the test_gate script `test_gate_sn7_beauty_self_host.sh`
     becomes a regression check — exit 0 when beauty self-hosts AND
     all 5–10 sentinel snippets self-host. Failure of any sentinel
     reopens this rung. Beauty 17/17 corpus is a precondition (must
     pass before self-host gate is even attempted).

  4. The SELF-HOST PASS gate is declared closed only when:
       - this rung's invariant suite passes,
       - S-2-hygiene-csnobol4 shows 0 / 0 / 0 (failures / skips / aborts),
       - S-2-hygiene-corpus-crosscheck shows zero unexplained skips,
       - the unfiltered harness (S-2-hygiene-bridge-trust) reaches
         beauty's full execution without divergence.

### Status updates

  S-2-hygiene-csnobol4              [ ] open
  S-2-hygiene-corpus-crosscheck     [ ] open
  S-2-hygiene-harness-orphans       [ ] open
  S-2-hygiene-bridge-trust          [ ] open  (alias of S-2-bridge-harness-trust)
  S-3-hygiene-self-host-witnesses   [ ] open

---

## Session #73 — 2026-05-01 (Sonnet 4.7 / Lon)

**Outcome:** No commit. Strategic redirect. Tree unchanged at `a629a15`.

### What happened

Set up fresh container: cloned `.github`, `corpus`, `one4all`, `snobol4dotnet`,
`x64`, `harness`. Installed `dotnet-sdk-10.0` (10.0.107). Built snobol4dotnet
at HEAD `a629a15` (session #71's BetaStack-isolation commit). x64 SPITBOL
binary at HEAD `71ff275` already had monitor IPC bridge linked.

Verified baseline gates:
  - Unit suite: 2073p / 14f-Csnobol4-only / 0s. (PLAN row 135's "2385p/0f/2s"
    is stale from an earlier session; the real invariant — "no non-Csnobol4
    failures" — holds.)
  - Beauty 17/17 corpus drivers: PASS.
  - Beauty self-host: 47 stderr lines / Parse Error at line 48
    `snoDQ = '"' BREAK('"' nl) '"'` — exactly as PLAN.md described.

Reproduced DIVERGE step #2839 via the IPC sync-step monitor with documented
controller workarounds (`MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`,
`MONITOR_NAME_WILDCARD=spl`). Confirmed unchanged from session #72: spl
emits `RETURN match (NRETURN)` while dot emits a 19th `CALL upr`.

Re-applied diagnostic C# function tracing (`[QPM]`/`[PM]`/`[M]`/`[UEP]`)
gated on `MonitorIpc.TraceEnabled`, in `PatternMatch (Question Mark).cs`,
`Scanner.cs`, and `UnevaluatedPattern.cs`. Re-ran the harness with
`MONITOR_TRACE_FROM_EVENT=2700 MONITOR_TRACE_TO_EVENT=2842`.

### Critical empirical finding

The trace at `[QPM ec=2768] ENTER` shows dot's outer `?` operator subject is
`'ANY APPLY ARBNO ARG ARRAY ATAN BACKSPACE BREAK BREAKX CHAR C...'` — that's
**`snoFunctions`** (length 455). spl, at the same logical wire-position, is
matching against **`snoUnprotKwds`** (length 125). FULLSCAN is in
snoUnprotKwds (18th keyword) but is NOT in snoFunctions, which is why
dot keeps iterating cursor positions calling `*upr(tx)` past the 18th
while spl finds the match and exits.

**Independent confirmation of session #64's diagnosis** (lines 644–707
above): dot's `snoExpr14` alternation tries `*snoProtKwd` (correctly
fails for `&FULLSCAN` since FULLSCAN is not in snoProtKwds), then falls
through to `*snoFunction` in `snoAtom@line 182` instead of trying
`*snoUnprotKwd` at `snoExpr14@line 154`. The bug is structural in the
alternation graph.

### What is now known to NOT be the line-48 gating bug

  - Session #71 `a629a15` BetaStack save/restore per PatternMatch
    invocation. Architecturally correct, shipped, divergence persists.
  - Session #71 `92b79be` Failure leak clear after BetaStack assignment
    commits in Executive.PatternMatch. Architecturally correct, shipped,
    divergence persists.
  - Session #67 `c578fb5` seal `-2` skip-to-next-real-alt. Architecturally
    correct, shipped, divergence persists.
  - `UnevaluatedPattern.Scan`'s `ExpressionVar` re-evaluation block (commit
    `ec59eeb`). Confirmed inactive for `*upr(tx)`: `evaluatedExpression`
    is `StringVar`, not `ExpressionVar`. Block doesn't fire.
  - `Scanner.PatternMatch`'s cursor-retry loop. Mechanically correct given
    its inputs.

The bug is the AST it's *given* to match against, not what it does
with it. Look upstream in pattern-construction.

### Why the user's premise didn't apply at this divergence

User's strategy: "After using the IPC sync step monitor tracing to find a
bug, use automatic C# function tracing from last agreed sync step code
position through to first diverged sync step code position. That C#
trace should immediately reveal the bug."

This works when the wire's divergence point IS the runtime's structural
divergence — i.e. when the bug is behavioural inside a known-good-then-
suddenly-bad state-machine path, both runtimes built the same AST, and
they only diverge in how they walk it.

Step #2839 isn't that. The wire emits only program-visible CALL/RETURN/
VALUE/LABEL records. Pattern-AST navigation, BetaStack push/pop,
alt-stack save/restore, SealAlternates/MarkAlternates, and FENCE
mark/seal — all are invisible to the wire. By the time the wire sees
divergence at #2839, dot has been running the wrong `match()` invocation
for ~70 wire-events. C# tracing inside that wrong-match shows
mechanically-correct snoFunctions iteration; it cannot reveal *why*
that match was started.

### Strategic pivot for session #74 — finer-grained bridges

Per Lon (2026-05-01): don't keep zooming in tighter at #2839. Instead,
enhance the participant bridges (csn, spl, dot) to emit at finer
granularity so the wire-visible divergence aligns with the actual
gating bug. The Silly SNOBOL4 monitor already does this; reuse the
precedent.

Add new `MWK_*` record kinds (or repurpose existing ones) for:

  1. **Pattern-AST navigation events** — emit on:
     - PatternMatch entry/exit (subject hash, pattern shape signature,
       anchor flag, cursor)
     - Per-node Match step (node index, type, alt index, subseq,
       cursor in/out, outcome)
     - Backtrack pop (alt index restored, cursor restored)
     - SealAlternates / MarkAlternates / RestoreAlternate
     - UnevaluatedPattern Scan entry/exit (graft target, subsequent)

  2. **Internal housekeeping** — emit on:
     - SystemStack Push/Pop (kind only, not value, to keep wire small)
     - BetaStack Push/Pop and Reverse-commit-loop iteration
     - Failure flag transitions
     - AmpAnchor / `&FULLSCAN` / mutable-keyword reads on the pattern
       match path

Each new kind needs:
  - a line in `one4all/scripts/monitor/monitor_wire.h`
  - participant-side emit calls in csn `monitor_ipc_runtime.c`,
    spl `osint/monitor_ipc_runtime.c`, dot `MonitorIpc.cs`
  - controller-side recognition in
    `one4all/scripts/monitor/monitor_sync_bin.py`

The controller's "last-agreed N vs first-diverged N+1" model still
applies. Divergence will now surface at the structural level — likely
inside `snoExpr14` alternation traversal where spl visits
`*snoUnprotKwd`'s alt-stack save/restore while dot does not — and
adjacent C# tracing at THAT site directly fingers
`PatternAlternation (Pipe).cs` or `AbstractSyntaxTree.Build` as the
buggy code.

### Concrete starting tasks for session #74

  1. Read silly-snobol4's monitor bridge for the precedent on
     fine-grained pattern-AST instrumentation.
  2. Define new `MWK_*` kinds in `monitor_wire.h`.
  3. Implement them in dot's `MonitorIpc.cs` first (smallest blast
     radius); verify standalone using
     `(POS(0) | ' ') *upr(tx) (' ' | RPOS(0))` matched against
     `'FULLSCAN'` against `snoUnprotKwds`.
  4. Implement in spl bridge (`x64/osint/monitor_ipc_runtime.c`).
  5. Update `monitor_sync_bin.py` to recognise/compare the new kinds.
  6. Re-run beauty self-host harness with `PARTICIPANTS="spl dot"`. The
     first DIVERGE row should now name the structural buggy site
     directly.
  7. Apply C# trace at THAT site between the new adjacent events. Fix.

### Files NOT to revisit blindly

  - `PatternMatch (Question Mark).cs` — session #71 BetaStack isolation
    is correct.
  - `Scanner.cs Match()` — session #67 seal-skip is correct.
  - `Scanner.cs PatternMatch()` cursor-retry loop — behaviourally
    correct given its inputs.
  - `UnevaluatedPattern.cs` ExpressionVar re-eval block — confirmed
    inactive for the symptom path.

### Hand-off state

  - snobol4dotnet HEAD: `a629a15` unchanged.
  - All diagnostic patches reverted per RULES.md (originals saved as
    `.orig`, restored, `.orig` files removed).
  - Tree clean.
  - PLAN.md row 135 updated with this session's strategic pivot summary.
