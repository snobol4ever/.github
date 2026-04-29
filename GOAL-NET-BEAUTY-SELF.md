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

- [ ] **S-2-bridge-7-fullscan** — Diagnose the `&FULLSCAN = 1` Parse
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

