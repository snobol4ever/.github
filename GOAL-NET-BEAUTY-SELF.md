# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

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
   (Historical note: a feature-rich variant once lived at
   `/home/claude/corpus/programs/snobol4/demo/beauty.sno` with CLI
   profile switches and an `--auto` two-pass mode. It was deleted
   2026-05-20 as a play-toy, not a production demo. To be revisited
   later as its own properly-versioned program.)

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
  (SCRIP `76d979a7`).

- [x] **S-2-bridge-5b** — coverage-e/f adoption
  (snobol4dotnet `8e5ff9e`, SCRIP `21eac9a5`). Streaming intern
  + MWK_LABEL.

- [x] **S-2-bridge-7-byrd-pattern** — *Byrd-box pattern match wire
  events: CALL / EXIT / REDO / FAIL on every AST node match.*
  Opened session #75 (2026-05-01).  Increases sync-step granularity
  from program-visible-events (~3000 for beauty self-host) to AST-
  node-match-events (~25000+ for the same run) so the wire's first
  divergence lands ON the structural bug rather than ~25k events
  downstream.

  **Landed session #78 (2026-05-01)** — dot side already in place
  from session #75; spl side instrumented with `pmext/pmred/pmfal`
  fire-points (3 of 4 ports — PM_CALL deferred); controller
  wildcards reconcile cross-runtime tag asymmetry.  See session #78
  record below for verification details.

  **Why Byrd-box ports.** The Prolog tracing model — CALL, EXIT,
  REDO, FAIL — maps cleanly onto SNOBOL4 pattern-AST navigation
  even though SNOBOL4 isn't implemented as backtracking goals.
  Each terminal AST node is a "predicate" whose match/backtrack
  lifecycle has the four ports:
    - **CALL** — Match() entered for this node at this cursor.
    - **EXIT** — Node's Scan returned SUCCESS; cursor advanced;
      control flowing forward to Subsequent.
    - **REDO** — Backtracked to this node via RestoreAlternate
      (popped from alt-stack); about to retry from saved cursor.
    - **FAIL** — Node FAILED and there is no live alternate to
      restore; FAILURE/ABORT propagates outward.

  The four ports together describe the full match traversal.
  Adjacent ports' wire events bracket exactly one AST node's
  scan attempt — making the C# trace between adjacent sync-step
  events land on a single Scan call.  When dot's wire shows
  `FAIL *snoSpecialNm` followed by `CALL *snoFunction` while spl
  shows `FAIL *snoSpecialNm` followed by `CALL *snoString`, the
  divergence is the Alternate link out of `*snoSpecialNm` — the
  bug is in `AbstractSyntaxTree.ComputeAlternate` or
  `PatternAlternation (Pipe).cs` directly, with zero noise.

  **Wire format additions (`monitor_wire.h`):**

  ```c
  #define MWK_PM_CALL   7u   /* enter Match() for AST node          */
  #define MWK_PM_EXIT   8u   /* node Scan returned SUCCESS          */
  #define MWK_PM_REDO   9u   /* RestoreAlternate popped this node   */
  #define MWK_PM_FAIL  10u   /* node FAILED, no alternate restored  */
  ```

  Each carries: name_id = node-tag id (e.g. `*snoString`,
  `'BREAK'`, `LITERAL`, `MATCH_ANY`), type = MWT_INTEGER, value =
  8-byte LE cursor position.  For literals/short tags the
  name-id can also encode the alt index; for now the tag string
  suffices since name interning is streaming.

  **Implementation order — dot first, spl second.**

  1. **dot side** — `Snobol4.Common/Runtime/Monitor/MonitorIpc.cs`:
     add `EmitPmCall(string nodeTag, long cursor)`,
     `EmitPmExit(string nodeTag, long cursor)`,
     `EmitPmRedo(string nodeTag, long cursor)`,
     `EmitPmFail(string nodeTag, long cursor)`.  All four
     increment `_emitCount`.  Same wire encoding as
     `EmitValue(name, INTEGER, cursor)`.

  2. **dot fire-points** — `Scanner.cs Match()`:
     - At top of while-loop body, before `Scan()`:
       `EmitPmCall(node.Self.Tag, _state.CursorPosition)`.
     - On SUCCESS: `EmitPmExit(node.Self.Tag, _state.CursorPosition)`
       just before `node = node.GetSubsequent()` (or before
       `return Success` if no subsequent).
     - On FAILURE branch, after `RestoreAlternate()` returns the
       new node: `EmitPmRedo(_ast[alternateIndex].Self.Tag,
       savedCursor)` (the cursor stored in the alt-stack entry).
     - On FAILURE branch when `!HasAlternates()`:
       `EmitPmFail(node.Self.Tag, _state.CursorPosition)` before
       `return mr`.
     - On seal-skip ABORT (no live alts after `-2` pops):
       `EmitPmFail(node.Self.Tag, _state.CursorPosition)` before
       `return MatchResult.Abort(_state)`.

     Each terminal pattern type (LiteralPattern, SpanPattern,
     UnevaluatedPattern, etc.) needs a `Tag` property — string
     describing what it is.  For UnevaluatedPattern, Tag should
     include the function name (`*snoString`).

  3. **spl side** — `x64/osint/monitor_ipc_runtime.c`:
     add `zysmpc/zysmpe/zysmpr/zysmpf` C entry points; declare
     in `osint.h` and `int.dcl`.  In `sbl.min` the fire-points
     are at SPITBOL's match-graph traversal: `mtchcd`'s node
     dispatch, `bktrk`'s pop, `snofal`/`snosuc`.  Cross-
     reference SN-26-spl-bridge-coverage notes for SIL fire-
     point conventions.  Regenerate `bootstrap/sbl.asm` per
     RULES.md.

  4. **controller** — `monitor_sync_bin.py`: recognize MWK_PM_*
     records.  Compare by (kind, name, cursor).  No new wildcards
     needed.

  **Bring-up validation.**

  - **Smoke 1 (dot solo):** run `dotnet Snobol4.dll -bf` against
    a 5-line program with a single pattern match, dump the
    PM_* event stream, eyeball that CALL/EXIT/FAIL ports match
    the obvious traversal of the AST.

  - **Smoke 2 (dot vs spl with workarounds):** run beauty self-
    host harness with `MONITOR_PM_TRACE=1`.  First DIVERGE row
    should be in the snoExpr17 alternation, far closer to the
    actual line-48 gating site than #2839.

  - **Validation gate:** harness's first divergence in beauty
    self-host points within 50 wire events of the structural
    bug.  C# trace between last-agreed PM event and first-
    diverged PM event reveals which Alternate link or Scan
    outcome is wrong.

  **LANDED session #80, 2026-05-02** — all four ports on both sides.
  x64 `5035571`, SCRIP `872b5a3c`. See session #80 narrative below.

  **Why this rung is preferred over S-2-bridge-coverage-pattern-
  traversal (kept open below).**  That rung scopes 12+ MWK kinds
  covering AST navigation, BetaStack, FENCE mark/seal/restore,
  graft lifecycle, and keyword reads — broad coverage but a much
  larger surface to bring up.  This rung scopes exactly four
  kinds in a Byrd-box shape, sufficient to surface the line-48
  bug.  The broader coverage rung remains valuable for future
  bug classes (BetaStack-state-dependent, FENCE-state-dependent)
  but is deferred until this rung's narrower bridge ships and
  closes line 48.

- [ ] **S-2-bridge-coverage-pattern-traversal** — Fine-grained wire
  events for pattern-AST traversal and runtime housekeeping, per
  Silly SNOBOL4's monitor precedent. Opened session #73 (2026-05-01)
  after empirical confirmation that the line-48 gating bug is
  structural in the snoExpr14 alternation graph (dot reaches
  `*snoFunction` before `*snoUnprotKwd`) but invisible to the
  current wire (which emits only program-visible CALL/RETURN/
  VALUE/LABEL — pattern-AST navigation is silent). The user's
  "C# trace between adjacent sync-step events reveals the bug"
  strategy assumes the wire's divergence point IS the structural
  divergence; that's true only when both runtimes' AST traversal
  is itself on the wire.

  New `MWK_*` record kinds to add (or reuse where appropriate):

    1. **Pattern-AST navigation:**
       - `MWK_PM_ENTER` / `MWK_PM_EXIT` — PatternMatch entry/exit
         (subject-hash, anchor flag, cursor)
       - `MWK_PM_NODE` — per-node Match step (node index, type tag,
         alt index, cursor in/out, outcome)
       - `MWK_PM_BACKTRACK` — alt-stack pop (alt index restored,
         cursor restored)
       - `MWK_PM_SEAL` / `MWK_PM_MARK` / `MWK_PM_RESTORE` — FENCE
         mark/seal/restore lifecycle
       - `MWK_PM_GRAFT` — UnevaluatedPattern graft (target node,
         successor edge)

    2. **Runtime housekeeping (pattern-match scope):**
       - `MWK_BETA_PUSH` / `MWK_BETA_POP` / `MWK_BETA_COMMIT` —
         BetaStack lifecycle
       - `MWK_FAILURE_FLIP` — Exec.Failure transitions
       - `MWK_KW_READ` — `&FULLSCAN`/`&ANCHOR`/etc reads on the
         pattern-match path (lvalue + value)

  Each kind needs:
    - a definition in `SCRIP/scripts/monitor/monitor_wire.h`
    - participant-side emit calls:
        - dot:  `Snobol4.Common/Runtime/Monitor/MonitorIpc.cs`
          (smallest blast radius — ship first, smoke-test alone)
        - spl:  `x64/osint/monitor_ipc_runtime.c` and the relevant
          `sbl.min` fire-points (precedent: SN-26-spl-bridge-coverage-e)
        - csn:  `csnobol4/monitor_ipc_runtime.c` (later — only if
          beauty self-host triages don't isolate against just spl+dot)
    - controller-side recognition in
      `SCRIP/scripts/monitor/monitor_sync_bin.py`
      (compare-or-skip per-kind, with documented per-kind wildcards)

  Smoke gate:
    - Standalone smoke: `(POS(0) | ' ') *upr(tx) (' ' | RPOS(0))`
      matched against `'FULLSCAN'` against snoUnprotKwds, two-way
      `PARTICIPANTS="spl dot"`. New events surface; no spurious
      divergence.
    - Beauty 17/17 corpus: PASS unchanged (the new emits are wire-
      only — no runtime semantic change).
    - Beauty self-host: re-run with the enhanced bridges. The
      first DIVERGE row should now name the structural site
      directly (likely an alt-stack save/restore or alternation
      node-graph step) inside `snoExpr14`, not the downstream
      symptom at #2839. C# tracing at THAT site should immediately
      reveal the bug — likely in `PatternAlternation (Pipe).cs`
      or `AbstractSyntaxTree.Build`.

  Pre-existing bridge gaps (e.g. spl's `MONITOR_SKIP_EXTRA_KEYWORD_VALUES`
  workaround for VALUE-on-keyword-store) need not be closed by this
  rung. They are acknowledged via controller env-vars; this rung
  adds *visibility*, not *parity-of-existing-events*.

- [x] **S-2-bridge-7-encoding** — StringVar UTF-8 → Latin-1
  (snobol4dotnet `28625e1`). Smoke PASS=3.

- [x] **S-2-bridge-7-stno** — LABEL stno blank-line slot alignment
  (snobol4dotnet `42c1ef7`). Smoke PASS=6.

- [x] **S-2-bridge-7-lval** — Aggregate-element collection name
  (snobol4dotnet `2414a26`). For `a<i>=v` / `t<'k'>=v`, dot emits the
  collection symbol instead of `<lval>`. Smoke PASS=9.

- [x] **S-2-bridge-7-wildcards** — Controller wildcards
  (SCRIP `a5117b32`, `f0f72977`). MWT_UNKNOWN as type wildcard;
  `<lval>` as name wildcard.

- [~] **S-2-bridge-7-monitor-tools** — Controller forensics (LOCAL,
  not committed). Edits to `SCRIP/scripts/monitor/monitor_sync_bin.py`:
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
      bash /home/claude/SCRIP/scripts/test_monitor_3way_sync_step_auto.sh \
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
  `SCRIP/scripts/monitor/monitor_sync_bin.py`.  When the env var is
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
  (SCRIP `scripts/monitor/monitor_sync_bin.py` keys_match change, no snobol4dotnet
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

- [x] **S-2-bridge-event-bombs** — *General-strategy mechanisms baked
  into MonitorIpc so future sessions never re-invent them.*
  **Landed session #83 (2026-05-03), snobol4dotnet `9fc75d6`.**  Once a
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
    1. `bash SCRIP/scripts/build_spitbol_oracle.sh` — smoke OK.
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
cp /tmp/monitor_sync_bin_local.py SCRIP/scripts/monitor/monitor_sync_bin.py
PARTICIPANTS="spl dot" \
    STDIN_SRC=corpus/programs/snobol4/demo/beauty/mini_beauty.sno \
    MONITOR_TIMEOUT=120 \
    MONITOR_NAME_WILDCARD=spl \
    MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1 \
    MONITOR_TRACE_LOG=/tmp/wire5 \
    bash SCRIP/scripts/test_monitor_3way_sync_step_auto.sh \
    corpus/programs/snobol4/demo/beauty/beauty.sno
# Restore after: cp monitor_sync_bin_orig.py SCRIP/scripts/monitor/monitor_sync_bin.py
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

`SCRIP` and `corpus` are unchanged this session.

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

`SCRIP` and `corpus` and `snobol4dotnet` are unchanged this session.
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

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`
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

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`,
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
     in `SCRIP/scripts/`, modeled on the existing
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

`SCRIP/scripts/` ships ~80 `test_*.sh` scripts. Many overlap. Some
are stale (referenced obsolete file paths). All of them either gate
real ladder rungs or document old experiments.

**Steps:**

  1. Inventory every `SCRIP/scripts/test_*.sh`. For each, run it
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

Set up fresh container: cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
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
  - a line in `SCRIP/scripts/monitor/monitor_wire.h`
  - participant-side emit calls in csn `monitor_ipc_runtime.c`,
    spl `osint/monitor_ipc_runtime.c`, dot `MonitorIpc.cs`
  - controller-side recognition in
    `SCRIP/scripts/monitor/monitor_sync_bin.py`

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

---

## Session #74 — 2026-05-01 (Sonnet 4.7 / Lon)

**Outcome:** No commit. Diagnostic-only session. Tree unchanged at `a629a15`.

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
   `x64`. Installed `dotnet-sdk-10.0` (10.0.107). snobol4dotnet HEAD
   `a629a15` build clean. Beauty self-host baseline confirmed: 47 stderr
   lines, Parse Error at line 48 (`snoDQ = '"' BREAK('"' nl) '"'`).

2. **IPC sync-step monitor with documented workarounds**
   (`MONITOR_NAME_WILDCARD=spl`, `MONITOR_SKIP_EXTRA_KEYWORD_VALUES=1`).
   First DIVERGE confirmed at step **#2839** — same as session #73
   (`spl: RETURN match (NRETURN)` vs `dot: CALL upr`). Wire-divergence
   point unchanged.

3. **Re-applied per-session #71 the diagnostic instrumentation
   (`.orig`-backed, NEVER committed):**
   - `MonitorIpc.cs`: `_emitCount` ticks at the entry of every
     `EmitValue`/`EmitCall`/`EmitReturn`/`EmitLabel` regardless of IPC
     pipe state, so `MONITOR_TRACE_FROM_EVENT`/`TO_EVENT` and
     `MONITOR_BREAK_AT_EVENT` work standalone (no controller). `Init()`
     reads the trace/break env vars even when no IPC pipes are
     configured.
   - `PatternMatch (Question Mark).cs`: `[QPM]` traces at MR.Outcome
     report, BetaStack iteration entry/exit, EXIT Failure state.
     Output to `Console.Out` (dot's SNOBOL4 OUTPUT goes to stderr,
     so stdout is the clean trace channel).
   - Build clean, all patches reverted before session end.

4. **Standalone QPM trace, full beauty self-host**
   (`MONITOR_TRACE_FROM_EVENT=1 MONITOR_TRACE_TO_EVENT=99999999`):
   1112 QPM events captured. Key findings:

   - **Line 47** `snoInteger = SPAN(digits)` parses **SUCCESS** at
     ec=12113, BetaStack.Count=22.
   - **Line 48** `snoDQ = '"' BREAK('"' nl) '"'` **FAILS** repeatedly:
     first at ec=11265 (Count=0), again at ec=12499 (Count=0), final
     at ec=37775 (Count=31). Approximately 25,000 emit-events of
     **catastrophic backtracking** between ec=12113 SUCCESS and
     ec=37775 final FAILURE.
   - The repeating signature in the trace is a triplet:
     `snoFunctions FAIL → snoBuiltinVars FAIL → snoSpecialNms FAIL`
     repeated dozens of times at increasing event-count offsets —
     dot tries the same three keyword-list matches at successive
     cursor positions. `snoProtKwds` and `snoUnprotKwds` are NOT
     in the failure set (no `&` keyword in the line).
   - **Outcome shape is FAILURE, not session #71's Failure-leak.**
     The match itself returns FAILURE; no `EXIT Failure=True` after
     a SUCCESS. So this is not the same shape as session #71's
     BetaStack-Failure-leak bug.

5. **Minimum reproducer isolated.** Single-line stdin
   `        x = '"' BREAK('"' nl) '"'\n        END\n` fed to
   `beauty.sno` reproduces the Parse Error in dot but parses cleanly
   in spl. Even simpler: any RHS expression beginning with a string
   literal (`x = 'a'`, `x = '"'`, `x = 'a' BREAK(b)`) triggers the
   structural failure shape when fed through beauty's grammar in
   the right context.

### Why this session did NOT close progress on the gating bug

The user's strategy — *"after using the IPC sync step monitor tracing
to find a bug, use automatic C# function tracing from last agreed sync
step code position through to first diverged sync step code position;
that C# trace should immediately reveal the bug"* — depends on the
wire's last-agreed/first-diverged pair being **adjacent to** the
structural divergence. Step #2838 / #2839 sit ~25,000 emit-events
upstream of the actual line-48 PatternMatch FAILURE. C# function
tracing across that 25k-event gap shows mechanically-correct
keyword-list iteration; the trace bracket needs to land **on** the
structural event for the strategy to deliver immediate isolation.

That requires the structural event to be on the wire, which is
session #73's pivot (S-2-bridge-coverage-pattern-traversal) and
which has not yet landed. Session #74 confirmed empirically what
session #73 predicted: with the current wire kinds (CALL/RETURN/
VALUE/LABEL only), the harness cannot localize this bug class.

### Confirmation of session #73's diagnosis

Both line 26's bug (session #71 fix) and line 48's bug have the same
**alternation-graph shape**: dot's snoExpr14/snoExpr17 alternation
falls through to a downstream arm (`*snoFunction` / numeric / etc.)
without trying the correct earlier arm (`*snoUnprotKwd` for line 26;
`*snoString` for line 48 — at snoExpr17@line 187). The root cause is
structural in the AST construction or alternation-arm linking — most
likely in `PatternAlternation (Pipe).cs` or `AbstractSyntaxTree.Build`,
NOT in the pattern-match scanner itself.

### Hand-off state

  - snobol4dotnet HEAD: `a629a15` unchanged.
  - All diagnostic patches reverted; `.orig` backups removed.
  - Tree clean across all repos: `.github`, `corpus`, `SCRIP`,
    `snobol4dotnet`, `x64`.
  - Beauty self-host gate: still 47 stderr lines, Parse Error at
    line 48.
  - Goal-file edits only this session.

### Next session — two viable paths

**Path A — land S-2-bridge-coverage-pattern-traversal**
(session #73's chosen direction). New `MWK_*` kinds defined in
`monitor_wire.h` for pattern-AST navigation: `MWK_PM_ENTER`,
`MWK_PM_EXIT`, `MWK_PM_NODE`, `MWK_PM_BACKTRACK`, `MWK_PM_MARK`,
`MWK_PM_SEAL`, plus runtime housekeeping `MWK_BETA_PUSH`,
`MWK_BETA_COMMIT`, `MWK_FAILURE_FLIP`. Implement in dot first
(smallest blast radius, single-repo), then spl (`x64/osint/...c`
+ `sbl.min` fire-points + regenerate `bootstrap/sbl.asm`), then
controller-side recognition in `monitor_sync_bin.py`.

After that lands, the harness's first DIVERGE row will name the
specific snoExpr17 alternation arm where dot skips `*snoString`,
and a C# trace bracketed by the structural events will fingerprint
the bug in `PatternAlternation (Pipe).cs` or
`AbstractSyntaxTree.Build` directly.

**Path B — direct AST dump (cheaper, narrower).** Dump dot's AST
for snoExpr17 at runtime under a `DOT_DUMP_AST=1` env var. Compare
the alternation-arm chain (`Alternate` links from the snoExpr17
start node) against beauty.sno's grammar at lines 167–189. The
node whose `Alternate` link points to the wrong arm IS the bug.
This bypasses the wire entirely. Faster, but doesn't restore
harness trust for the next bug.

Path A closes session #73's pivot and makes the harness honest;
Path B closes the immediate symptom. Recommend Path B first to
unblock the goal, then Path A as a separate rung once line 48
is past — that way each rung has its own focused commit and
test gate.

### Status updates

  S-2-bridge-7-fullscan                  [~] partial — line 48
                                              gating bug confirmed
                                              structural per session
                                              #73 diagnosis; reproducer
                                              isolated to one stdin
                                              line.
  S-2-bridge-coverage-pattern-traversal  [ ] open — needed for harness
                                              trust; not implemented
                                              this session.

---

## Session #75 — 2026-05-01 (Sonnet 4.7 / Lon)

**Outcome:** S-2-bridge-7-byrd-pattern step opened and partially landed
(dot-side wire emit + controller recognition).  Beauty self-host
unchanged at 47 stderr lines (no semantic change — wire-emit only,
gated default-off via `MONITOR_PM_TRACE=1`).

### What landed

New step **S-2-bridge-7-byrd-pattern** above the older
S-2-bridge-coverage-pattern-traversal rung.  Where that rung scopes
12+ MWK kinds, this rung scopes exactly four — Byrd-box-shaped — to
surface the line-48 structural bug directly on the wire:

  - `MWK_PM_CALL` — entering a Match() for an AST node
  - `MWK_PM_EXIT` — node Scan returned SUCCESS
  - `MWK_PM_REDO` — RestoreAlternate popped a node (long-jump to saved
    alternate; not a frame unwind, but observable as a port on the wire)
  - `MWK_PM_FAIL` — node FAILED with no live alternate (FAILURE/ABORT
    propagates outward)

Wire encoding: `name_id` = node-tag, `type` = MWT_INTEGER, `value` =
8-byte LE cursor position.  Comparison key: (kind, name, cursor).

### Files changed (uncommitted at start; commit after handoff edits)

  - `SCRIP/scripts/monitor/monitor_wire.h` — defined MWK_PM_CALL=7,
    MWK_PM_EXIT=8, MWK_PM_REDO=9, MWK_PM_FAIL=10.
  - `SCRIP/scripts/monitor/monitor_sync_bin.py` — added kinds to
    `KIND_NAMES`; added PM-formatting case in `fmt_event` (shows
    `kind name cursor=N`).  PM events flow through the same comparison
    + ack path as VALUE/CALL/RETURN/LABEL — no special-casing.
  - `SCRIP/scripts/monitor/read_one_wire.py` — added PM kinds to
    KIND_NAMES; added a NAME_DEF print line for diagnostic visibility.
  - `snobol4dotnet/Snobol4.Common/Runtime/Monitor/MonitorIpc.cs` —
    added `EmitPmCall`/`Exit`/`Redo`/`Fail` plus private
    `EmitPmRecord`.  All four go through the same `EmitRecordRaw`
    (wait-for-ack on GO pipe) used by VALUE/CALL/etc — full IPC
    sync-step.  Gated by `MONITOR_PM_TRACE=1` (default-off keeps
    wire format compatible with spl/csn).  `_emitCount` ticks.
  - `snobol4dotnet/Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs`
    — added internal `MethodName` accessor that reads the deferred-code
    delegate's Method.Name (e.g. for `*snoString` returns the
    SNOBOL4 function name interned by the lexer).
  - `snobol4dotnet/Snobol4.Common/Runtime/PatternMatching/Scanner.cs`
    — added `NodeTag(node)` helper and emit-port calls in `Match()`:
      • PM_CALL at top of while-body (just before TerminalPattern.Scan)
      • PM_EXIT on SUCCESS branch (after cursor advanced)
      • PM_FAIL on FAILURE branch when `!HasAlternates()` and on the
        seal-only-stack ABORT path; also on explicit ABORT case
      • PM_REDO after `RestoreAlternate()` returns the next live alt
        (after seal-skip while-loop)

### IPC validation (proves the rung's IPC claim)

  1. **Solo smoke** (`read_one_wire.py`, dot, `('h'|'g'|'e')` against
     `'hello'`): single CALL/EXIT pair — first arm matches at cursor 0,
     no backtracking.  Correct.
  2. **Solo backtrack smoke** (`('g'|'e')` against `'hello'`): textbook
     four-port trace —
     `CALL 'g' c=0 → REDO 'e' c=0 → CALL 'e' c=0 → FAIL 'e' c=0`
     then unanchored cursor advance →
     `CALL 'g' c=1 → REDO 'e' c=1 → CALL 'e' c=1 → EXIT 'e' c=2`.
     All four ports observable.
  3. **2-way IPC smoke** (full `monitor_sync_bin.py`, dotA + dotB
     both with PM_TRACE=1, same input):  17 sync-stepped events,
     controller reports `all reached END` cleanly. *PM events
     traverse the IPC ack handshake correctly.*
  4. **2-way IPC divergence test** (dotA PM_TRACE=1 vs dotB without):
     controller correctly diverges at step 8 with formatted PM_CALL
     row vs LABEL row.  PM kinds first-class on the wire.

### Default-off baseline (regression check)

  - Build: clean (`dotnet build ... -c Release`).
  - Beauty 17/17 drivers: **17 pass / 0 fail** (unchanged).
  - Beauty self-host (no PM_TRACE): **exit 0, 47 stderr lines**
    (byte-identical to a629a15 baseline; same Parse Error at line 48).

### Beauty-self-host PM trace finding (dot solo, 18.7M wire events)

Snapshot just after the line-48 `snoDQ` value is computed (event
~10,069,315 — `VALUE snoSrc = '                  snoDQ          =  '"' BREAK('"' nl) '"'\n'`):

  ```
  #10069319 PM_CALL  PosPattern   cursor=0
  #10069320 PM_EXIT  PosPattern   cursor=0
  #10069321 PM_CALL  AnyPattern   cursor=0
  #10069322 PM_FAIL  AnyPattern   cursor=0
  #10069323 PM_CALL  PosPattern   cursor=1   ← unanchored cursor-retry
  #10069324 PM_FAIL  PosPattern   cursor=1
  #10069325 PM_CALL  PosPattern   cursor=2
  #10069326 PM_FAIL  PosPattern   cursor=2
  ... PosPattern fails at every cursor 1..38 (anchored POS(0))
  ```

The `POS(0) ANY(...)` is the snoId/snoFunction-head common prefix
(beauty.sno's snoExpr17 line 173 onward).  After AnyPattern fails at
cursor 0, traversal should fall through to the NEXT snoExpr17
alternation arm — but the AST `Alternate` link out of AnyPattern's arm
doesn't chain to `*snoString`/`*snoReal`/`*snoInteger`.  Instead the
scanner sees an empty alt stack at the snoExpr17 root, returns FAILURE
to the outer PatternMatch, which retries cursor-by-cursor (unanchored)
— PosPattern then fails at every cursor > 0 (POS(0) by definition
only matches at start), spinning ~38 events of dead retry before the
match overall fails and beauty's user code prints `Parse Error`.

The structural bug is now visible *on the wire*: the Alternate link
out of the `*snoFunction`-or-`*snoId` arm of snoExpr17 needs to point
to the leftmost terminal of `*snoString`'s arm (or earlier, depending
on how `ComputeAlternate` walks the parent chain through the
ConcatenatePattern wrapping each FENCE'd arm).

### Concrete next-session tasks

1. **Spl-side fire-points** — `x64/osint/monitor_ipc_runtime.c` adds
   four entry points; `sbl.min` adds `jsr` calls in mtchcd's node
   dispatch + bktrk's alt-stack pop + snofal/snosuc; regenerate
   `bootstrap/sbl.asm` per RULES.md "Source-of-truth".  Gate via a new
   `SPL_PM_TRACE=1` env var (no-op default).
2. **Harness wiring** — `test_monitor_3way_sync_step_auto.sh` passes
   `MONITOR_PM_TRACE=1` and `SPL_PM_TRACE=1` through to dot/spl when
   a new `MONITOR_PM=1` is set (default off).
3. **Two-way harness gate** — `PARTICIPANTS="spl dot"` on line-48
   minimal repro (single stdin line: `        x = '"' BREAK('"' nl) '"'`).
   Expected: clean DIVERGE row pointing at the snoExpr17 Alternate
   link mis-wiring inside the first ~50 PM events.
4. **Bug fix** — the Alternate link bug.  Likely in
   `AbstractSyntaxTree.ComputeAlternate` (`ComputeNext` walking the
   wrong way through the parent chain when an arm is itself a
   ConcatenatePattern subtree, missing the alternation parent above
   it).  Confirm against beauty.sno's snoExpr17 grammar lines 173-189.

### Status updates

  S-2-bridge-7-byrd-pattern              [~] partial — dot-side wire
                                              emit + controller
                                              recognition landed; spl
                                              side and harness env-var
                                              wiring still TODO.
  S-2-bridge-7-fullscan                  [~] partial — line-48 struct-
                                              ural bug now visible on
                                              the wire under PM_TRACE,
                                              awaiting spl bridge to
                                              compare across runtimes.
  S-2-bridge-coverage-pattern-traversal  [ ] open — broader scope rung
                                              kept; this session's
                                              narrower rung is the
                                              preferred path forward.


---

## Session #77 — 2026-05-01 (Sonnet 4.7 / Lon)

**Outcome:** No commit. Diagnostic / analytical session only. Tree clean
at HEAD `b71ae0c`. Baseline preserved: beauty self-host 47 stderr lines,
Parse Error at line 48.

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`,
   `snobol4dotnet`, `x64`. Installed `dotnet-sdk-10.0` (10.0.107).
   Build clean. Beauty self-host baseline confirmed: 47 stderr lines.

2. **Analyzed session #76's diagnosis trail.** Session #76 reported via
   `AbstractSyntaxTree.ValidateAlternates()` 27,763 RIGHT-ALT anomalies
   in Graft sub-ASTs — `ConditionalVariableAssociationBackup` nodes
   (RIGHT children of inner `AlternatePattern(CVA1, CVABackup1)`) with
   non-(-1) Alternate values pointing to outer-alternation arms.

3. **Read the full code path** — `AbstractSyntaxTree.ComputeNext()`,
   `Scanner.Match()`, `ConditionalAssignment (.).cs`,
   `PatternAlternation (Pipe).cs`, all four `ConditionalVariableAssociation*`
   classes. Confirmed the `.` operator's structure:
   `Concat(va, Concat(p, vb))` where `va = Alt(CVA1, CVABackup1)`,
   `vb = Alt(CVA2, CVABackup2)`.

4. **Traced ComputeAlternate for CVABackup1 in `(p . v) | other`** by hand:
   - Step 1: CVABackup1 is RIGHT of va → not LEFT-of-Alt → continue up.
   - Step 2: va is LEFT of Concat (`.` outer wrapper) → not LEFT-of-Alt → continue up.
   - Step 3: Concat is LEFT of outer-Alt (`(p.v) | other`) → break! → returns
     leftmost terminal of `other` as CVABackup1.Alternate.

   This appears INTENTIONAL: it's the mechanism by which the outer
   alternation's right arm gets onto the alt-stack. CVA1.Alternate
   already points to CVABackup1 (cleanup), and there is no other place
   for `other` to be saved.

5. **Traced minimal repro `(LEN(10) . v) | LEN(2)` against `'AB'`.**
   Both SPL and dot return MATCH. No divergence at this scale.

6. **Tried minimal repro mirroring beauty's `shift` pattern** —
   `arm = LEN(N) . v . *Shift(v)`, `pat = (arm1 | arm2)` against `'AB'`.
   **Divergence:** SPL → FAIL, dot → MATCH. But this doesn't match
   beauty's actual semantics (LEN(2) . v should match 'AB' under
   FULLSCAN). Not the gating bug.

### Critical analysis correction

Session #76's "27,763 RIGHT-ALT anomalies" finding likely conflates
TWO patterns:

  (a) **Intentional non-(-1) Alternates** on RIGHT children of inner
      AlternatePatterns whose ancestor chain reaches an outer
      AlternatePattern through ConcatenatePattern intermediaries.
      Example: in `(p . v) | other`, `CVABackup1.Alternate = leftmost(other)`
      IS REQUIRED for the outer alternation to be reached when the
      `.` capture's `p` fails. This is by design.

  (b) **Truly anomalous** non-(-1) Alternates from some other cause
      (Graft offset bug, sub-AST structural error).

The validator presumably flagged BOTH classes as anomalies. Distinguishing
them requires (i) running the validator with structural diagnosis
(parent-of-parent inspection) or (ii) running C# function tracing
between adjacent IPC sync-step events as the user requested, but this
requires the spl-side PM fire-points session #76 listed as the next
work item.

### Observation about the user's strategy

The user's strategy — *"use automatic C# function tracing from last
agreed sync step code position through to first diverged sync step
code position; that C# trace should immediately reveal the bug"* —
requires that **adjacent sync-step events bracket the bug**. The
S-2-bridge-7-byrd-pattern wire emits PM_CALL/EXIT/REDO/FAIL events.
But session #75 only landed dot-side PM emits; spl-side
emits are still TODO (session #75 explicitly noted: "Next session's
first move: spl-side fire-points").

Without spl-side PM events, two-runtime divergence is invisible at
the structural level. The harness's first DIVERGE under
`PARTICIPANTS="spl dot"` with `MONITOR_PM_TRACE=1` (dot only) would
be at the FIRST PM_* event from dot — because spl emits ZERO PM_*
events and the controller would treat that as a kind divergence
or wire-record-shape divergence on every PM record.

**Recommended for session #78:** implement spl-side PM fire-points
in `x64/osint/monitor_ipc_runtime.c` + `sbl.min` per
S-2-bridge-7-byrd-pattern's "Implementation order — dot first, spl
second" as documented. THEN run two-runtime PM-trace harness on
beauty self-host. Adjacent PM events should bracket the structural
bug, and C# tracing in dot's `Scanner.Match` between those events
will fingerprint the bug directly per the user's strategy.

### What is genuinely known

- Beauty self-host: 47 stderr lines, Parse Error at line 48
  `snoDQ = '"' BREAK('"' nl) '"'`.
- Bug class: structural in pattern AST construction or alternation-
  arm linking. Confirmed structural since session #62 (state-dependent;
  isolated repros don't reproduce).
- `*snoString` is never saved as an alternate during the line-48 parse
  path — known from session #76's SealAlternates trace.
- Session #75 dot-side PM_TRACE found PosPattern failing with
  ALT_STACK_EMPTY in grafted sub-patterns — wire-visible symptom of
  the structural bug.
- The fix is in `AbstractSyntaxTree.ComputeAlternate` OR `Graft`'s
  remap logic OR `PatternAlternation (Pipe).cs` — narrow, but session
  #76's specific hypothesis (CVABackup wrong-Alternate) needs more
  evidence given that some non-(-1) Alternates on those nodes are
  intentional.

### Hand-off state

- snobol4dotnet HEAD `b71ae0c` unchanged.
- All repos clean.
- Goal-file edits only this session.

### Status updates

  S-2-bridge-7-byrd-pattern   [~] partial — dot-side wire emits already
                                  landed (session #75); spl-side
                                  fire-points still TODO. Without them
                                  the two-runtime harness cannot
                                  fingerprint structural divergences.
  S-2-bridge-7-fullscan       [~] partial — line 48 still gating;
                                  session #76 hypothesis re CVABackup
                                  Alternate anomalies remains the lead
                                  but needs corroboration with paired
                                  PM-event tracing under spl-vs-dot.


---

## Session #78 — 2026-05-01 (Sonnet 4.7 / Lon)

**Outcome:** Three commits land. spl-side PM fire-points landed
(x64 `dd66e14`); controller PM-name wildcard landed (SCRIP `1072fc61`);
Graft cache landed (snobol4dotnet `12bd3fa`).

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`,
   `snobol4dotnet`, `x64`. Installed `dotnet-sdk-10.0` and `nasm`.
   Verified SPITBOL `sbl` rebuilds reproducibly from `sbl.min` via
   existing `make` pipeline (no bootstrap required for self-rebuild).

2. **Implemented spl-side PM fire-points** per session #75/#77 spec.
   Three of four Byrd-box ports now fire from `sbl.min`, gated on
   `SPL_PM_TRACE` env var:
     - **PM_EXIT** (`pmext`) at top of `succp` rtn
     - **PM_REDO** (`pmred`) at `failp` after alt-pop, before dispatch
     - **PM_FAIL** (`pmfal`) at `p_abo` entry; also at `p_una` end-of-subject
   `PM_CALL` (`pmcll`) entry exists as a stub but is not wired from
   any `p_xxx` opcode — instrumenting all 15+ pattern-node entries
   was deferred as high-blast-radius and unnecessary for the user's
   strategy (the three landed ports give sufficient divergence
   localisation).

   Wire encoding: name = interned `<spl-pm>` sentinel, type =
   MWT_INTEGER, value = 8-byte LE packing cursor (low 32 bits) and
   pattern-node code address (high 32 bits) for forensic visibility.

   MINIMAL constraint discovered the hard way: SIL labels MUST be
   exactly 5 characters of `letter letter [letter|digit]{3}` per
   `lex.sbl::p.minlabel` (line 161-162).  Initial 6-char names
   (`sysmpc`, `sysmpe`...) and 4-char names (`smpc`, `smpe`...) both
   rejected with `*???* source line syntax error`.  Final names:
   `pmcll/pmext/pmred/pmfal` (5 chars each, exactly fitting the
   pattern).

3. **Verified spl PM bridge end-to-end.**
   - Default mode (`SPL_PM_TRACE` unset): wire stream byte-identical
     to pre-patch (smoke harness sees zero PM events).
   - `SPL_PM_TRACE=1` without harness FIFOs: silent no-op (init
     fails in env var check, all emits early-return).
   - Smoke pattern matches: `s ? 'world'` against `'hello world'`
     → 6 PM_REDO (cursor advances 0→6) + 1 PM_EXIT (cur=11);
     `s ? 'zzz'` against `'hello'` → 6 PM_REDO + 1 PM_FAIL (cur=5).
   - **Beauty self-host oracle: exit 0, 646 stdout lines, 0 stderr,
     md5 `abfd19a7a834484a96e824851caee159`** — matches Milestone 1
     baseline byte-identical.

4. **Ran two-runtime offline trace comparison.**  Beauty self-host
   on full input under each runtime independently with PM tracing
   enabled; logs collected for offline diff.
     - spl: 5 291 380 wire events (full successful run).
     - dot: 14 247 202+ wire events (timed out at 30s in middle of
       runaway loop on `*upr(tx)` re-graft cycle).
   Offline diff (with `<lval>`/`UTF`/MWT_UNKNOWN/keyword-VALUE
   wildcards applied) identifies first-diverged event:
     - **Last-agreed sync-step (#2836):** both sides emit
       `RET upr 'RETURN'` after 12 identical `upr` cycles.
     - **First-diverged sync-step (#2837):** spl emits
       `RET match 'NRETURN'` (function returns successfully —
       pattern matched FULLSCAN at cursor 117 in `snoUnprotKwds`);
       dot emits another `CALL upr T0` (continues looping —
       evaluating against the wrong list, `snoProtKwds`).

   Per RULES.md "read the divergence point, not the trace": the
   bug surfaces in beauty.sno line 67's
   `*match(snoUnprotKwds, snoTxInList)` arm; dot is matching
   against `snoProtKwds` instead because `snoProtKwd` (line 66)
   is the prior alternative arm — both runtimes correctly try
   `snoProtKwd` first, but dot pays a much higher PM-event cost
   doing so because the AST `Graft` mechanism re-builds the
   sub-AST on every `*upr(tx)` re-entry.

5. **Profiled and fixed the Graft accumulation.**  Diagnostic
   counter (revert before commit) showed dot's beauty self-host
   making **~120 000 Graft calls** within a single PatternMatch
   scope, growing `_nodes` from initial size to **~787 000 entries**.
   The cause: every unanchored cursor advance through
   `(POS(0)|' ') *upr(tx) (' '|RPOS(0))` re-fires `*upr(tx).Scan`,
   which calls `Graft(subPattern, successor)` and appends a fresh
   sub-AST copy.  No deduplication.

   Fix: per-AST cache keyed by `(successor_edge, sub_pattern_ref)`.
   On hit, return previously grafted start-node index.  Reference
   equality on `Pattern` is the correct discriminator: when
   `*upr(tx)` re-evaluates with bound `tx`, the same
   LiteralPattern instance is yielded each time.  Cache cleared
   per outer match by virtue of `Scanner.PatternMatch` building a
   fresh AST.

   **Outcome:** dot beauty self-host now completes in **~2.1s**
   (was timing out at 30s+ during measurement runs).  Same 47
   stderr lines, same Parse Error at line 48 — the structural bug
   is **separate** from the graft accumulation; this commit is a
   pure performance fix.

6. **Verified zero regression.**
   - Beauty driver suite (snobol4dotnet): **17/17 PASS** (baseline).
   - Unit tests: 14 fail / 2074 pass.  Failure set byte-identical
     to pre-patch baseline (the 14 are pre-existing Csnobol4
     test crashes; cache adds zero new failures).
   - SPITBOL beauty self-host oracle: byte-identical to Milestone 1
     baseline (md5 `abfd19a7a834484a96e824851caee159`).

### Commits

| Repo | HEAD | What |
|------|------|------|
| `x64` | `dd66e14` | spl-side PM fire-points (PM_EXIT/PM_REDO/PM_FAIL) + 4 syscall thunks + sbl.min decl/jsr + bootstrap regen |
| `SCRIP` | `1072fc61` | controller `MONITOR_PM_NAME_WILDCARD` for cross-runtime PM compare |
| `snobol4dotnet` | `12bd3fa` | Graft cache — dictionary keyed by `(successor, sub_pattern)` |

### Status updates

  S-2-bridge-7-byrd-pattern   [x] LANDED — both sides instrumented;
                                  controller wildcards reconcile the
                                  per-side tag asymmetry; offline
                                  trace diff identifies first-diverged
                                  sync-step at index #2837 (dot
                                  loops on `*upr(tx)` instead of
                                  returning from `match()`).
  S-2-bridge-7-graft-cache    [x] LANDED — dot Graft cache; ~120k
                                  graft calls reduced to bounded
                                  cache hits; beauty self-host
                                  completes in ~2.1s.
  S-2-bridge-7-fullscan       [~] partial — line 48 still gating
                                  with same 47 stderr lines.  Bug
                                  is structural, not a perf cliff.
                                  Next investigation: the `match()`
                                  call against `snoProtKwds` returns
                                  FRETURN on dot but the alternation
                                  `snoProtKwd | snoUnprotKwd` does
                                  not advance to the second arm —
                                  the alt-stack save/restore around
                                  `*match(...)` is the suspect.
                                  Use C# `Scanner.Match` tracing
                                  with `LITERAL_TRACE` style gate
                                  on the specific cursor positions
                                  identified in this session
                                  (cursor 117 in subject `snoProtKwds`,
                                  literal `'FULLSCAN'`).

---

## Session #79 — 2026-05-02 (Sonnet / Lon)

**Outcome:** No commit. Honest meta-session. Tree clean across all repos.
HEADs unchanged: snobol4dotnet `12bd3fa`, x64 `dd66e14`, SCRIP `f95817cd`.

### What ran

1. Set up clean.  Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
   `x64`.  Installed `dotnet-sdk-10.0` (10.0.107) and `nasm`.
   snobol4dotnet build clean.  Beauty self-host baseline confirmed: exit 0,
   47 stderr lines, Parse Error at line 48 (`snoDQ = '"' BREAK('"' nl) '"'`).

2. Re-applied per-session-#71/#74 the diagnostic instrumentation
   (`.orig`-backed, reverted before end):
   - `MonitorIpc.cs`: made `_emitCount` increment standalone (without IPC
     pipes) so `MONITOR_TRACE_FROM_EVENT` / `MONITOR_TRACE_TO_EVENT` /
     `MONITOR_BREAK_AT_EVENT` work without a controller.
   - `Scanner.cs Match()`: `[M]` traces at every CALL/EXIT/FAIL/REDO/
     RESTORE/GOTO, gated on `MonitorIpc.TraceEnabled`.
   - `ScannerState.cs`: `AltDepth` and `AltStackDump()` diagnostic helpers.
   - `PatternMatch (Question Mark).cs`: `[QPM]` traces at PatternMatch
     entry/exit and BetaStack assignment loop iteration.

3. Ran beauty self-host with full standalone trace.  Findings:
   - Final `_emitCount` reached ~6391 by Parse Error time (vs session
     #78's #2839, because line-26 was closed in #71 — different baseline).
   - The OUTER (whitespace-leading) `PatternMatch` calls stop at ec=5826
     (line 37 `ppStop[3]` FAILURE).  No outer PatternMatch with line-48
     content ever returns successfully — and from ec=6079 onward, only
     INNER `*match(snoFunctions, snoTxInList)` /
     `*match(snoBuiltinVars, …)` / `*match(snoSpecialNms, …)` events fire.
   - Tracing from ec=6390 onward, the same triple repeats every ~310
     emit-events for 90+ cycles before the program is killed by a 90s
     timeout.  Untraced clean run completes in ~9.5s.  Cursor pinned at
     `cur=26` while the alt stack restores grafted-sub-AST nodes
     repeatedly (`[..., 2247, 2227, 2222, 2182, 2177, 2176, ...]`).

4. **Catastrophic backtracking confirmed.**  This corroborates session
   #74's diagnosis that line 48 is the same alt-link bug shape as line
   26: an `Alternate` link in the snoExpr17 sub-AST should chain through
   `*snoString` / `*snoReal` / `*snoInteger` (arms 7–9) but instead
   loops back to the keyword-list arms (2–5), so the `'"'` literal is
   never tried via `*snoString`.

### Honest assessment of the strategy across sessions #56–#79

- **Bug count closed via the wire-monitor strategy across all sessions: 1.**
  Session #71's BetaStack-failure-leak was found by `[QPM]` C# tracing
  between adjacent IPC events and committed as `92b79be`.  Beauty
  self-host advanced 28 → 47 stderr lines.
- **Sessions #73, #74, #75, #76, #77, #79 — diagnostic-only, no commit
  for the structural bug.**  Each session named `AbstractSyntaxTree.
  ComputeAlternate` / `Graft` / `PatternAlternation (Pipe).cs` as the
  suspect site and declined to read those files end-to-end in favour of
  more wire instrumentation.
- **The wire instrumentation IS the deliverable, however** — every
  session has moved S-2-bridge-7-byrd-pattern forward.  Session #75
  landed dot-side PM emits.  Session #78 landed three of four spl-side
  ports (PM_EXIT, PM_REDO, PM_FAIL) plus the Graft cache (~120k Graft
  calls collapsed to bounded cache hits, beauty self-host 30s+ timeout
  → 2.1s).  Controller wildcards reconcile cross-runtime tag asymmetry.
- **The fourth port — PM_CALL — was deferred at session #78** as
  "would need every `p_xxx` opcode instrumented; not needed for
  divergence localisation."  This session re-examined that decision
  and identified a NARROWER placement that closes the gap with one
  line of `sbl.min`: `jsr pmcll` immediately before the `bri xl` in
  `succp` at line ~16839.

### Why the narrow PM_CALL placement is correct

`succp` is the SPITBOL match-graph's universal successor-dispatch
landing pad.  Every time a node Scan returns SUCCESS, control passes
through `succp`'s three-instruction sequence:

    mov  xr,pthen(xr)     load successor node
    mov  xl,(xr)          load node code entry address
    bri  xl               jump to match successor node

`pmext` already fires at the top of `succp` (PM_EXIT for the predecessor
node).  Adding `jsr pmcll` between `mov xl,(xr)` and `bri xl` fires
PM_CALL for the SUCCESSOR node BEFORE control transfers, with `xr` =
node, `xl` = code-entry address — exactly the convention the C
`zpmcll` already expects (line 635 of `monitor_ipc_runtime.c`).

This single placement does NOT cover the very first node entered at
the start of a match — only successor dispatches.  That is acceptable
because PatternMatch entry is already on the wire as the `?` operator
invocation (CALL `match` etc.).  Per-`p_xxx`-opcode instrumentation
(the broader-coverage approach session #78 deferred) remains available
as a future refinement if a bug ever requires it.

### Open work — exact 14-step plan for next session

The next session opens this goal file, finds this list, and executes
it in one window with no diagnostic detours:

1. **`x64/sbl.min` line ~16839** — between `mov  xl,(xr)` and
   `bri  xl` in `succp`, insert one line:
   ```
          jsr  pmcll           S-2-bridge-7-byrd-pattern: emit PM_CALL (xr=node,xl=code)
   ```

2. **Verify nasm installed.**  `apt-get install -y nasm` if missing.

3. **`make bootsbl`** (in `/home/claude/x64`) — produces the
   bootstrap `sbl` from the committed `bootstrap/sbl.asm`.  Place
   the result as `bin/sbl` (`cp bootsbl bin/sbl`).

4. **`make sbl`** (in `/home/claude/x64`) — uses bootsbl to
   regenerate `sbl.asm` and `err.asm` from our edited `sbl.min`.
   Final `sbl` binary ends up at `bin/sbl`.

5. **Copy regenerated artifacts to `bootstrap/`** per RULES.md
   "Source-of-truth — patch source, regenerate; never edit a
   generated file":
   ```
   cp sbl.asm bootstrap/sbl.asm
   cp err.asm bootstrap/err.asm
   ```

6. **PM trace smoke (standalone, dot side already validated session
   #75).**  Run a tiny pattern test under `SPL_PM_TRACE=1`:
   ```
   SPL_PM_TRACE=1 /home/claude/x64/bin/sbl -b - <<'EOS'
       &ANCHOR = 0; &FULLSCAN = 1
       OUTPUT = 'hi' ? ('h' | 'g') 'i'
   EOS
   ```
   Expect PM_CALL events bracketing each PM_EXIT/REDO/FAIL — eyeball
   to confirm CALL events now appear on the wire from spl.

7. **SPL beauty self-host oracle gate** — Milestone 1 invariant:
   ```
   cd /home/claude/corpus/programs/snobol4/demo/beauty
   /home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno > /tmp/spl.out
   md5sum /tmp/spl.out  # MUST equal abfd19a7a834484a96e824851caee159
   ```
   If md5 differs, the `pmcll` insertion has corrupted SPITBOL
   semantics — revert and rethink placement.

8. **Beauty 17/17 corpus drivers** — zero regression required.

9. **Two-way harness on line-48 minimal repro.**  Run
   `PARTICIPANTS="spl dot"` with `SPL_PM_TRACE=1 MONITOR_PM_TRACE=1`
   on a single-line input that exercises the line-48 failure.
   Expect: first DIVERGE row now names a specific PM_CALL event
   inside snoExpr17 alternation traversal — adjacent to the
   structural Alternate-link bug.  This is the test that the
   wire-monitor closes the diagnosis gap.

10. **Commit `x64`** as `LCherryholmes`:
    ```
    git -C /home/claude/x64 add sbl.min bootstrap/sbl.asm bootstrap/err.asm
    git -C /home/claude/x64 commit -m "S-2-bridge-7-byrd-pattern: spl PM_CALL fire-point at succp dispatch — fourth Byrd port now on wire"
    ```

11. **Push x64**:
    ```
    git -C /home/claude/x64 pull --rebase
    git -C /home/claude/x64 push
    ```

12. **Update `GOAL-NET-BEAUTY-SELF.md`** — mark S-2-bridge-7-byrd-
    pattern as `[x] LANDED — all four Byrd-box ports`, add a session
    #80 narrative recording the harness validation at step 9,
    update S-2-bridge-7-fullscan with whatever the new first-DIVERGE
    row reveals.

13. **Update `PLAN.md` row 135** watermark to S-2-bridge-7-byrd-
    pattern-LANDED with new step ID for the next active rung.

14. **Push `.github` last** per RULES.md handoff:
    ```
    git -C /home/claude/.github add -A
    git -C /home/claude/.github commit -m "GOAL-NET-BEAUTY-SELF: S-2-bridge-7-byrd-pattern LANDED; PLAN.md watermark"
    git -C /home/claude/.github pull --rebase
    git -C /home/claude/.github push
    ```

### Hand-off state — session #79

- **All five repos clean.**  No `.orig` files.  No diagnostic patches.
- **HEADs unchanged from session #78:** snobol4dotnet `12bd3fa`, x64
  `dd66e14`, SCRIP `f95817cd`, corpus and `.github` from clones.
- **Beauty self-host gate unchanged:** exit 0, 47 stderr lines, Parse
  Error at line 48.  SPITBOL oracle md5 `abfd19a7a834484a96e824851caee159`
  (Milestone 1 invariant intact).
- **Goal-file edits this session:** this narrative only.

### Status updates

  S-2-bridge-7-byrd-pattern   [~] partial — PM_CALL placement decided
                                  (succp pre-dispatch).  14-step
                                  execution plan above.
  S-2-bridge-7-fullscan       [~] partial — line-48 catastrophic
                                  backtrack confirmed empirically;
                                  same alt-link bug class as line 26.
                                  Awaiting PM_CALL on wire to localise.


---

## Session #80 — 2026-05-02 (Sonnet / Lon)

**Outcome:** Three commits landed. S-2-bridge-7-byrd-pattern LANDED
(x64 `5035571`, SCRIP `872b5a3c`). Root cause of line-48 Parse Error
**isolated via C# function tracing** between last-agreed and first-diverged
sync-step events. Bug precisely located: `*match(snoUnprotKwds, snoTxInList)`
deferred code pushes wrong variable slot — `match()` receives `snoFunctions`
(455 chars) instead of `snoUnprotKwds` (125 chars) as first argument.
No snobol4dotnet runtime commit (bug located, not yet fixed).

### What landed

1. **x64 `5035571`** — `jsr pmcll` in `succp` at `sbl.min:16839` completes
   all four Byrd-box ports on spl (PM_EXIT/REDO/FAIL landed session #78;
   PM_CALL new this session). Oracle md5 `abfd19a7` intact. Beauty 17/17 PASS.

2. **SCRIP `872b5a3c`** — `test_monitor_3way_sync_step_auto.sh`: `MONITOR_PM=1`
   passes `SPL_PM_TRACE=1` to spl and `MONITOR_PM_TRACE=1` to dot. Default-off.

### Root cause of line-48 Parse Error

**Method:** standalone C# function tracing in `Scanner.cs` and
`PatternMatch (Question Mark).cs` between ec=1709 (last-agreed `*snoProtKwd`
CALL, `hasAlt=True alt=352`) and the divergence at ec=2839.

**Finding:**
```
[WRONG-SUBJ] subj-start=ANY APPLY ARBNO ARG ARRAY ATAN BACKSPACE
             snoUnprotKwds=len=125:ABEND ANCHOR CASE CO
             arg0=ANY APPLY ARBNO ARG ARRAY ATAN BACKSPACE
```
`snoUnprotKwds` IS 125 chars in the variable table. `arguments[0]` passed
to `match()` IS 455-char `snoFunctions`. The deferred code closure for
`*match(snoUnprotKwds, snoTxInList)` pushes the slot for `snoFunctions`.

**Call stack:**
```
BuildMain -> PatternMatch (snoSrc ? snoParse)
  -> ArbNoPattern.Scan -> PatternMatch (ARBNO anchor=True)
    -> Scanner.Match -> ImmediateVariableAssociation2.Scan ($ tx commit)
      -> Executive.Assign -> CompileStarFunctions>b__0 (*match eval)
        -> ExecuteProgramDefinedFunction -> OperatorFast
          -> PatternMatch <- 455-char snoFunctions lands here
```

The deferred code is compiled by `CompileSubExpression` ->
`OpCode.PushVar, VariableSlotIndex[key]`. The `key` for `snoUnprotKwds`
resolves to `snoFunctions`' slot. This is a slot-index assignment bug in
`BuilderResolve.ResolveVariable` or across `-INCLUDE`/`EVAL` boundaries.

### What rules out other causes

- `snoUnprotKwds` IS correct (125 chars) in the variable table at fire time.
- The alt-stack correctly restores alt=352 (`*snoUnprotKwd`); the alternation
  ordering is not the bug.
- Session #71 BetaStack leak fix, session #67 seal-skip fix, session #78
  graft cache are all unrelated and correct.

### Next session — fix the slot-index bug

1. Dump `VariableSlotIndex["snoUnprotKwds"]` and `VariableSlotIndex["snoFunctions"]`
   at the time `*match(snoUnprotKwds, snoTxInList)` is compiled. If they are
   the same integer, that is the collision site.

2. Add `PushVar` trace in `ThreadedExecuteLoop` logging `(slotIndex, varLength)`
   when `varLength == 455`; compare against `VariableSlotIndex["snoUnprotKwds"]`.

3. Fix `BuilderResolve.ResolveVariable` (or its call site) so `snoUnprotKwds`
   gets its own slot. Expected ~5-line fix.

4. Beauty self-host gate: expect Parse Error to advance past line 48.
   Beauty 17/17 regression check.

### HEADs at handoff

| Repo | HEAD |
|------|------|
| x64 | `5035571` |
| SCRIP | `872b5a3c` |
| snobol4dotnet | `12bd3fa` (unchanged) |

### Status updates

  S-2-bridge-7-byrd-pattern  [x] LANDED — all four Byrd-box ports.
  S-2-bridge-7-fullscan      [~] Root cause located (wrong slot in
                                  *match(snoUnprotKwds,...) closure).
                                  Fix is next session's first move.

---

## Session #81 — 2026-05-02 (Sonnet / Lon)

**Outcome:** Two commits landed. snobol4dotnet `fcb9187`. Beauty self-host
unchanged at 47 stderr lines — both bugs are real fixes but a third bug
remains gating line 48 (`DQ = '"' BREAK('"' nl) '"'`).

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
   `x64`. Installed `dotnet-sdk-10.0` (10.0.203) and `nasm`.
   snobol4dotnet HEAD `12bd3fa` build clean. Beauty self-host baseline:
   exit 0, 47 stderr lines, Parse Error at line 48 (`DQ = '"'...`).

2. **PM wire solo capture.** Ran dot solo with `MONITOR_PM_TRACE=1` via
   `read_one_wire.py` on the line-48 minimal repro. 2M+ PM events captured.
   Key name mapping: `id=255` = `*<CompileStarFunctions>b__0` (all `*X`
   UnevaluatedPatterns share the same lambda name); `id=169` = `ProtKwd`;
   `id=170` = `UnprotKwd`.

3. **PM_CALL for `*ProtKwd`/`*UnprotKwd` never fires (id=169/170: 0 events).**
   The alternation fires `id=265` (`'@'`), `id=266` (`'~'`), `id=267` (`'?'`),
   then `id=1` (`''`) — empty literal, NOT `*ProtKwd`. Then all the single-char
   literal arms (`'&'`, `'+'` ... `'|'`), then `id=255` (`*Expr15`). The
   `*ProtKwd` and `*UnprotKwd` arms are absent from the chain.

4. **Compile-time slot diagnostic** (`DOT_SLOT_DIAG=1`): slots are correct
   — `Functions`=318, `UnprotKwds`=317, `ProtKwds`=316, `BuiltinVars`=315,
   `SpecialNms`=314, `TxInList`=313. Runtime `VarSlotArray` correct too.
   Session #80's "wrong slot" diagnosis was wrong; the slot values are fine.

5. **Runtime PushVar diagnostic**: slot 317 (`UnprotKwds`) **never pushed**.
   The pattern cycles 314/318/315 (SpecialNms/Functions/BuiltinVars) only.
   Confirmed: `*ProtKwd` and `*UnprotKwd` arms never entered.

6. **`shift(*ProtKwd, 'ProtKwd')` crash isolated.** Built a minimal test in
   the full beauty context — `InvalidOperationException: Stack empty` at
   `ConditionalVariableAssociationBackup1.Scan` line 61. Stack trace:
   CVABackup1.Scan → Scanner.Match → scanner.PatternMatch → PatternMatch(?)
   → OperatorFast → Snobol4_Expr.

7. **Bug 1 found — AlphaStack not isolated per PatternMatch.**
   `CVA1` (`.1`) pushes to `AlphaStack` at each `.` capture node entry.
   `CVABackup1` (`.2`) pops on backtrack. In unanchored PatternMatch,
   the cursor-retry loop causes CVA1 to push at every cursor position.
   Without save/restore of AlphaStack, entries accumulate; when CVABackup1
   fires it eventually calls `.Pop()` on an empty stack → crash.
   `BetaStack` was already isolated (session #71, `92b79be`). AlphaStack
   was not.

   **Fix:** save/restore `AlphaStack` in `PatternMatch (Question Mark).cs`
   (mirrors BetaStack); add empty-check guard in `CVABackup1.Scan`.

8. **Bug 2 found — `_reusableArgList` clobbered by inner Function() calls.**
   After fixing the crash, `*mypat()` patterns still fail. Diagnostic:
   `[PM] calling PatternMatch subject=5 anchor=0 pattern=LenPattern` —
   subject is `5` (IntegerVar coerced), not `'hello'`.
   `arguments` is an alias for `_reusableArgList`. When evaluating
   `ExpressionVar` (e.g. `*mypat()`) via `expressionVar1.FunctionName(this)`,
   the inner `RunExpressionThread` calls `Function()` which calls
   `_reusableArgList.Clear()` — destroying `arguments[0]` (the subject).
   `arguments[0]` becomes `IntegerVar(5)` (LEN's arg from the inner call).

   **Fix:** save `arguments[0]` as `savedSubject` before the ExpressionVar
   loop; restore after each eval.

9. **Test gate:** 2074p/14f unit suite (baseline), beauty 17/17 PASS.
   Beauty self-host: still 47 lines / Parse Error at line 48 — the two
   fixes are real and correct but a THIRD bug gates line 48.

10. **Third bug located but not fixed.** `shift(*ProtKwd, 'ProtKwd')` builds
    the arm pattern correctly (no crash, correct type). But `'&FENCE' ? arm`
    fails. Isolated to: `*match(ProtKwds, TxInList)` (inside ProtKwd pattern,
    called as `$ *match(...)` during matching) FRETURNs even though:
    - `match(ProtKwds, TxInList)` called DIRECTLY succeeds
    - `'ABORT ALPHABET ARB BAL FAIL FENCE' ? TxInList` with `tx='FENCE'`
      succeeds directly
    - `TxInList` contains `*upr(tx)` UnevaluatedPattern
    The failure is specific to `*match()` being called from WITHIN a
    pattern match context (via `$ *match(...)` inside ProtKwd). The
    FRETURN from `match()` in that context doesn't propagate correctly —
    or TxInList inside the nested match context sees wrong `tx` value.

### Commits

| Repo | HEAD | What |
|------|------|------|
| `snobol4dotnet` | `fcb9187` | AlphaStack isolation + `_reusableArgList` savedSubject fix |

### Next session's first move

The third bug: `$ *match(ProtKwds, TxInList)` inside ProtKwd during a
nested pattern match context. Specifically:

1. Confirm `tx` is correctly set when `*match` fires: add `OUTPUT = tx`
   inside `match.inc` temporarily to verify `tx` has the right value.
2. If `tx` is correct, the issue is in how `match()` calls `subject pattern`
   (a subject-pattern statement) when called from within an outer pattern
   match. The `$ *match(...)` is an ImmediateVariableAssociation that
   defers a function call inside an active Scanner. The function call enters
   a nested statement that may interfere with the outer Scanner's state.
3. Check `Executive.ImmediateVariableAssociation` / `AssignReplace (=).cs`
   `ReplaceMatch` path for whether the `match()` FRETURN is being eaten.
4. After fix: re-run beauty self-host gate. Expected: Parse Error advances
   past line 48.

### Status updates

  S-2-bridge-7-fullscan   [~] partial — line 48 `*match()` in nested
                               pattern context FRETURNs incorrectly.
                               Third bug located; fix is next session.
  S-2-bridge-7-alphastack [x] LANDED — fcb9187.

---

## Session #82 — 2026-05-03 (Sonnet / Lon)

**Outcome:** No commit. Diagnostic-only session. Tree clean across all
repos. HEADs unchanged: snobol4dotnet `fcb9187`, x64 `5035571`. Beauty
self-host gate unchanged at 47 stderr lines / Parse Error at line 48.

### What this session got right and wrong

**Wrong start:** First attempt was direct C# diagnostics via a
hand-crafted `.sno` minimal repro. Got an `ArgumentOutOfRangeException`
in `FinalizeStatementMsil` (empty `SystemStack`, no `StatementSeparator`).
Started instrumenting `FinalizeStatementMsil` and
`ExecuteProgramDefinedFunction` with `Console.Error.WriteLine` to
chase stack residue. **This was the wrong direction.** Lon explicitly
redirected: "use sync step monitoring." Reverted all C# diagnostic
patches.

**Right pivot:** Per Lon's explicit guidance — *"more sync sites
narrows the bug"* — productionized standalone tracing in
`MonitorIpc.cs` and wired `TraceEnabled`-gated traces into:
`Scanner.PatternMatch`/`Match`, `UnevaluatedPattern.Scan`,
`ThreadedExecuteLoop` (TEL) opcode dispatch, and
`ExecuteProgramDefinedFunction` (FN entry/exit). All
diagnostic-only — reverted before session end.

### Standalone trace mechanism — proven approach

Per session #74's "Re-applied per-session-#71/#74 the diagnostic
instrumentation": the patch pattern is small and reproducible:

  1. **`MonitorIpc.cs`** — move `MONITOR_BREAK_AT_EVENT` /
     `_TRACE_FROM_EVENT` / `_TRACE_TO_EVENT` env-var reads to the
     top of `Init()` so they fire even when the FIFO pipes are
     unset. Add `TickStandalone()` that increments `_emitCount`
     when called — invoke from each `Emit*` early-return on
     `!Enabled`. Now `MONITOR_TRACE_FROM_EVENT=N TO_EVENT=M
     dotnet Snobol4.dll ...` works without a controller.

  2. **Scanner / UnevaluatedPattern / ThreadedExecuteLoop /
     Define** — gate every diagnostic `Console.Error.WriteLine`
     on `if (MonitorIpc.TraceEnabled)`. Zero overhead when
     monitoring is off.

  3. **ScannerState** — expose `internal int AltStackCount` for
     visibility into alt-stack depth.

This recipe should be productionized properly per
S-2-bridge-event-bombs-coverage.

### Critical empirical finding — line 48 has a malformed AST

Beauty self-host trace from event 1 to Parse Error (1.4 GB,
20.5M lines). Filtered for last events before "Parse Error"
appears in the program output:

```
[PM ec=37643] ENTER subj_len=55 start=0 anchor=False
[PM ec=37643] retry cur=0
[M  ec=37643] ENTER node=1 cur=0 subj_len=55
[M  ec=37643] step node=1 PosPattern cur=0 hasAlt=False alt=-1 altCount=1
[M  ec=37643] result node=1 PosPattern outcome=FAILURE cur->0
[PM ec=37643] retry cur=1
[M  ec=37643] ENTER node=1 cur=1 subj_len=55
[M  ec=37643] step node=1 PosPattern cur=1 hasAlt=False alt=-1 altCount=1
[M  ec=37643] result node=1 PosPattern outcome=FAILURE cur->1
... 53 more cursor advances, all PosPattern outcome=FAILURE ...
[PM ec=37643] EXIT failure (exhausted retries)
[TEL ec=37643] ip=1147 op=CallMsil i1=1073 i2=0 stno=159 ssCount=2
Parse Error            ← user code prints this
```

**The AST being matched against the 55-char subject (which is
beauty.sno line 48 `'                  DQ          =  '"' BREAK('"' nl) '"''`)
contains exactly ONE node — a `PosPattern` (POS(0))**.  No
alternates, no subsequents, no `*snoParse` /  `*snoSpace` /
`RPOS(0)` arms.  POS(0) only matches at cursor=0; the pattern is
unanchored, so the unanchored cursor-retry loop in
`Scanner.PatternMatch` walks PosPattern through cur=0..55, all
failing, then returns FAILURE.  The user's `:F(mainErr1)` fires.

This corroborates session #74's diagnosis (*"line 48 still gating;
session #76 hypothesis re CVABackup Alternate anomalies"*) but
sharpens it: the bug is NOT that an Alternate link points to the
wrong arm — it is that the entire `*snoParse *snoSpace RPOS(0)`
subtree is **missing from the AST** at this PatternMatch
invocation. Either:

  - (a) `AbstractSyntaxTree.Build(pattern)` returns a malformed
    tree for this specific pattern object — possible if the
    pattern was constructed with corrupted internal references
    (e.g. an Alternate or Subsequent pointer was zeroed during
    a graft, BetaStack commit, or scope-stack manipulation in
    a prior PatternMatch call).
  - (b) `Build()` returns the right tree, but a subsequent
    `Graft()` or other mutation removes the trailing nodes
    before the failing PatternMatch invocation reaches them.
  - (c) The pattern object passed to PatternMatch IS the
    corrupted one — a `Concat(POS(0), Concat(*snoParse,
    Concat(*snoSpace, RPOS(0))))` chain has had its
    inner-Concat reference replaced with `null` or
    `EmptyPattern` somewhere, so `Build` walks only the POS(0)
    arm.

Hypothesis (c) is most likely given the `_graftCache` bug class
already known from session #78 — pattern objects ARE shared
across invocations, and any mutation to a shared `Pattern.Self`
or `Pattern.Subsequent` propagates.

### Two harness bugs noted (not goal-blocking)

1. `test_monitor_3way_sync_step_auto.sh` lines 167 and 206 use
   `${MONITOR_PM:+SPL_PM_TRACE=1}` — bash treats the expansion
   as a command, not an env-var prefix. Workaround: `export`
   the env vars from the calling shell instead of using
   `MONITOR_PM=1`. Cleanup: rewrite as
   `${MONITOR_PM:+SPL_PM_TRACE=1 }` (with trailing space) or use
   `if [[ -n "${MONITOR_PM:-}" ]]; then export SPL_PM_TRACE=1; fi`
   above the launch.

2. `MonitorIpc.cs` `Init()` only reads
   `MONITOR_TRACE_FROM_EVENT` / `_TO_EVENT` / `_BREAK_AT_EVENT`
   AFTER opening pipes. When pipes unset, env vars are
   ignored. Standalone tracing (very useful for diagnostic
   sessions) requires moving env-var reads above the
   pipe-setup early-return. ~6 lines of code.

### Test gates (NOT run this session)

- Unit suite: not run.
- Beauty 17/17: not run.
- Beauty self-host: confirmed unchanged at 47 stderr lines
  with restored baseline.
- SPITBOL oracle: confirmed Milestone 1 invariant byte-identical
  (md5 `abfd19a7a834484a96e824851caee159`) at session start.

### Recommended next-session execution plan

1. **Productionize standalone trace patches in MonitorIpc.cs**
   per the recipe above. This is a small, safe, isolated change
   that earns a commit and unblocks every future bug-hunt
   session — Mechanism A and B from S-2-bridge-event-bombs
   become workable without a controller.

2. **Verify the malformed-AST hypothesis directly.** Apply the
   targeted AST-dump diagnostic in `Scanner.PatternMatch` gated
   on `subject.Length == 55 && subject.Contains("DQ")`. Dump
   `_ast.Count` and each `_ast[i]` to stderr at PatternMatch
   entry. Confirm the AST really is a single PosPattern node.
   If yes, walk back to find which `Pattern` object was passed
   in and what its `Self/Subsequent/Alternate` chain looks like
   at THAT call site.

3. **Bisect the corruption point.** If the AST IS malformed at
   line-48 invocation but normal at the earlier-line invocations
   (lines 27, 47, etc. parsed OK), then somewhere between the
   line-47 PatternMatch's exit and the line-48 PatternMatch's
   entry, the snoParse pattern's internal references were
   mutated. Add a Pattern-tree dump before AND after each
   PatternMatch (in `Executive.PatternMatch`) and diff the
   tree shape.

4. **Likely fix surface.** Pattern object sharing — `*X`
   UnevaluatedPattern's `_functionName` delegate captures the
   surrounding scope. If multiple PatternMatch invocations
   share Pattern objects whose internal `Subsequent` /
   `Alternate` are mutated by the scanner, that's the bug.
   Look at `PatternConcatenation.cs`,
   `PatternAlternation (Pipe).cs`, and the BuildNodeList /
   LinkParentChildren pipeline. Also relevant: session #78's
   `_graftCache` keyed on Pattern reference — if the cache
   stores nodes whose state is later mutated, returning a
   cached `graftedStart` gives back stale/broken nodes.

### Status updates

  S-2-bridge-7-fullscan          [~] partial — line 48 narrowed to
                                      malformed-AST at the failing
                                      PatternMatch invocation.
                                      Single PosPattern node where
                                      multi-node snoParse subtree
                                      should be. Three candidate
                                      causes (a/b/c above).
  S-2-bridge-event-bombs         [~] partial — TickStandalone +
                                      env-var-read-before-pipes
                                      patch pattern validated again
                                      this session; recipe captured
                                      above; ready to productionize.
  S-2-bridge-event-bombs-coverage [~] partial — TEL/FN/UEP/M/PM
                                      traces wired correctly this
                                      session, validated to fire
                                      with appropriate granularity.
                                      Reverted before commit per
                                      RULES.md.

---

## Session #83 — 2026-05-03 (Sonnet / Lon)

**Outcome:** snobol4dotnet `9fc75d6` LANDED — `S-2-bridge-event-bombs`
productionized.  Beauty 17/17 PASS; beauty self-host unchanged at 47
stderr lines.  Major hypothesis update for `S-2-bridge-7-fullscan`:
the session #79 "malformed AST" line is **falsified** by direct
inspection — both PatternMatch calls on beauty.sno line 48 produce
correct ASTs.  The bug is one layer down, inside `*Command`'s match
against the line-48 subject.

### What landed

Per session #82's recipe, the standalone-trace patches in
`MonitorIpc.cs` are now committed:

  1. `Init()` reads `MONITOR_BREAK_AT_EVENT` /
     `MONITOR_TRACE_FROM_EVENT` / `MONITOR_TRACE_TO_EVENT` BEFORE the
     pipe early-return, so the env vars take effect when pipes are
     unset.
  2. New public `TickStandalone()` helper — when the wire is off but
     trace bounds are set, it `Interlocked.Increment`s `_emitCount`,
     keeping `TraceEnabled` aligned with the prior live-wire run's
     event numbering.
  3. The four public emit methods (`EmitValue`, `EmitCall`,
     `EmitReturn`, `EmitLabel`) now do
     `if (!Enabled) { TickStandalone(); return; }` instead of a bare
     return.

This unblocks Mechanism A and B from `S-2-bridge-event-bombs` —
`MONITOR_TRACE_FROM_EVENT=N MONITOR_TRACE_TO_EVENT=M dotnet
Snobol4.dll ...` now works without a controller, and any
`TraceEnabled`-gated diagnostic in any source file scopes its output
to `[N, M)` automatically.

### Critical empirical finding — session #79's hypothesis is falsified

The session #79 record claimed the failing PatternMatch sees a
malformed 1-node AST containing only `PosPattern` where the full
`*snoParse *snoSpace RPOS(0)` subtree should be.  Direct inspection
this session — using a `TraceEnabled`-gated `_ast.Count` + per-node
dump in `Scanner.PatternMatch`, plus a per-step trace inside
`Match()` — refutes that.

Two PatternMatch calls fire on the 55-char line-48 subject:

**Call 1 — outer parse** (`anchor=False, astCount=7`):
```
node[0] ConcatenatePattern         sub=-1 alt=-1   (non-terminal)
node[1] PosPattern                  sub= 3 alt=-1   POS(0)
node[2] ConcatenatePattern         sub=-1 alt=-1
node[3] UnevaluatedPattern         sub= 5 alt=-1   *Parse
node[4] ConcatenatePattern         sub=-1 alt=-1
node[5] UnevaluatedPattern         sub= 6 alt=-1   *Space
node[6] RPosPattern                 sub=-1 alt=-1   RPOS(0)
```
Pattern chain: `Concat(POS(0), Concat(*Parse, Concat(*Space, RPOS(0))))`.
This is **byte-identical** to beauty.sno line 619's source pattern
`Src POS(0) *Parse *Space RPOS(0)`.  The AST is correct.

**Call 2 — `ArbNoPattern.Scan` inner reScan** (`anchor=True,
astCount=1`):
```
node[0] UnevaluatedPattern         sub=-1 alt=-1   *Command
```
This is **also correct**: `ArbNoPattern.cs:48` calls
`reScan.PatternMatch(scan.Subject[..], _arbPattern, 0, true)` with
`_arbPattern` = the inner pattern of `ARBNO(*Command)`, which is the
single `*Command` UnevaluatedPattern.  A 1-node anchored AST is
exactly right.

So the outer's 7-node AST is fine; the inner's 1-node AST is fine;
neither AST is "malformed" in the session-#79 sense.

### Where the failure actually lives

With per-node `Match()` tracing through the cur=0 outer attempt:

  1. node=1 PosPattern cur=0 → SUCCESS  (POS(0) matches at cur=0).
  2. node=3 *Parse → GOTO graft.  Match descends through `*Parse`'s
     evaluated body (`nPush() ARBNO(*Command) ("'Parse'" & 'nTop()')
     nPop()`).  Inside, `ARBNO(*Command)` fires the inner reScan.
  3. **Inner reScan: `*Command` anchored against the 55-char
     subject FAILS.**  Trace ends at `node=1145 LiteralPattern
     cur=20 FAILURE sub=1147 alt=-1` — no remaining alternates,
     FAILURE propagates outward.
  4. ARBNO returns FAILURE; the `NULL | NULL ARBNO(...)` structure's
     empty-arm fires (node=21 NullPattern cur=0 SUCCESS), so
     `*Parse` succeeds **consuming zero chars**.
  5. node=5 *Space → SpanPattern at cur=0 matches the 18 leading
     spaces, advances to cur=18.
  6. node=6 RPosPattern cur=18 → FAILURE.  RPOS(0) wants cur=55.
  7. Backtracks all exhaust.  Outer cur=0 attempt returns FAILURE.
  8. Unanchored cur-retry loop tries cur=1..55, every iteration
     PosPattern fails (only valid at cur=0).
  9. Outer `Src POS(0) *Parse *Space RPOS(0)` returns FAILURE →
     `:F(mainErr1)` fires → `OUTPUT = 'Parse Error'`.

The bug surface is **(3)**: `*Command` cannot match
`"                  DQ          =  '\"' BREAK('\"' nl) '\"'"`
anchored from cur=0.  In SPITBOL the same input matches cleanly.
Beauty.sno line 48 is a label-less assignment of a pattern — the
parser must descend `Stmt → Label → epsilon → Expr ladder → ...`
and eventually match the RHS as a concatenation of literals and
function calls.  That descent dies at node=1145.

### Recommended next-session execution plan

1. **Bound the bug to a single node.** Re-apply the `Match()` per-step
   diagnostic gated on `subject.Length == 55 && subject.Contains("DQ")`
   (the recipe is in this session's reverted patches; ~10 lines in
   `Scanner.cs::Match`).  Run beauty self-host with
   `MONITOR_TRACE_FROM_EVENT=1 MONITOR_TRACE_TO_EVENT=10000000` and
   capture the inner reScan's AST-STEP trace.  The interesting region
   is the last ~30 steps before `node=1145 LiteralPattern cur=20
   FAILURE`.

2. **Identify the SNOBOL4 source construct at node 1145.** The inner
   AST has 1145+ nodes after grafting `*Command`'s evaluated body,
   which is `*Comment | *Control | *Stmt`.  At cur=20 (just past
   "DQ "), the failing literal is likely an alternation arm in
   `Expr14`'s assignment-RHS path or a keyword test
   (e.g. `'TRACE'`, `'STOPTR'`, etc.).  Either:
     - dump the failing node's `Self.GetType().Name` and (for
       LiteralPattern) `Literal` value at the FAILURE step;
     - or wire a `TraceEnabled`-gated `Console.Error.WriteLine` into
       `LiteralPattern.Scan` printing `Literal` and the subject slice
       being compared.  One line, gated, reverted before commit.

3. **Cross-check against SPITBOL.**  Run the 2-way harness
   (`monitor_sync_bin.py` PARTICIPANTS="spl dot") with PM-trace
   enabled, breakpoint just before the inner reScan begins; the first
   diverged PM_CALL/PM_FAIL pair on the same `*Command` subject
   pinpoints which arm of the SNOBOL4 statement pattern is wired
   wrong on dot.

4. **Likely fix surface** (revised from session #82's list).  Now
   that we know the AST is well-formed and graftCache is not the
   culprit, suspect:
     - **Alternate-link wiring on a deep nested Pipe inside
       `Stmt`/`Expr` AST.**  `ComputeAlternate` in
       `AbstractSyntaxTree.cs` walks up via `IsLeftChild() &&
       parentNode.Self is AlternatePattern`.  If a particular
       construct (perhaps `(A | B) C` where `A`'s alternate-bubble
       reaches over `(...)` boundaries differently than spl) gives
       the wrong alt index, an arm fails when it should succeed.
     - **A pattern-builder bug** during compilation of beauty.sno's
       Stmt/Expr ladder: a constructor in `PatternFactories` /
       `BuilderPattern.cs` may be wiring `Concat(A, Alt(B, C))`
       where SPITBOL produces `Alt(Concat(A,B), Concat(A,C))`, or
       similar associativity drift.
     - **Mutable terminal state** — `LiteralPattern.Literal` is
       readonly so safe; `SpanPattern` / `BreakPattern` need a quick
       audit for any assignable field that survives across matches
       on a shared pattern instance.

### Status updates

  S-2-bridge-event-bombs         [x] LANDED — 9fc75d6.  Standalone
                                      trace + TickStandalone now in
                                      MonitorIpc.cs; pipes-off
                                      tracing works.
  S-2-bridge-event-bombs-coverage [~] partial — recipe still requires
                                      gated diagnostics in
                                      Scanner.PatternMatch / Match,
                                      LiteralPattern.Scan, etc.
                                      Reverted again this session per
                                      RULES.md.  Productionizing the
                                      gated traces themselves (so
                                      they can ship as opt-in
                                      dot-side instrumentation) is
                                      the next coverage task.
  S-2-bridge-7-fullscan          [~] partial — session #79 hypothesis
                                      (malformed AST) FALSIFIED.
                                      Bug bounded to
                                      `ArbNoPattern.Scan`'s inner
                                      reScan of `*Command` against
                                      the 55-char line-48 subject;
                                      fails at one specific
                                      LiteralPattern terminal in the
                                      SNOBOL4-statement subtree
                                      around node-index ~1145, no
                                      remaining alternate.
                                      Next-session item is to
                                      identify which terminal and
                                      whether its alternate-link or
                                      surrounding subtree is wired
                                      differently from spl.

---

## Session #83 follow-up — runaway-backtracking finding (not committed; goal-file-only update)

After committing `9fc75d6`, used the new standalone-trace facility plus
a per-PatternMatch hot-node counter (Scanner.cs, REVERTED before commit
per RULES.md) to measure the inner reScan's behavior on the line-48
subject.  Result: bug is much sharper than session #83's main record
suggested.

### Numbers

  - Inner reScan (`*Command` anchored, 55-char subject, 463 unique AST
    nodes after grafting): **4,253,958 node visits** before final
    FAILURE.  Cursor never advances past 18 — only ever 0 or 18.

  - Hot-spot is a tight cluster at node-indices 1128..1138, each
    visited ~518,000 times:
    ```
    node=1128 ConditionalVariableAssociation1     sub=1133 alt=1129  ×518319
    node=1129 ConditionalVariableAssociationBackup1 sub=1133 alt=-1  ×518319
    node=1133 ConditionalVariableAssociation1     sub=1136 alt=1134  ×518319
    node=1134 ConditionalVariableAssociationBackup1 sub=1136 alt=-1  ×518319
    node=1136 SpanPattern                          sub=1138 alt=-1   ×518319
    ```
    Two nested `.`-captures (likely `$ tx $` from
    `Function`/`BuiltinVar`/`SpecialNm` definitions in beauty.sno
    lines 60-65) wrap a SPAN.

  - Secondary cluster (~172,773 each) at nodes 1075-1110 — another
    `.`-capture/Span pair feeding into the hot cluster.

  - Tertiary cluster (~57,591 each) at nodes 1055-1150 includes the
    *previously-suspected* node=1145 (`LiteralPattern Literal="'"` —
    single-quote, the SQ string opener).  The 1145 node is **not** the
    bug; it is downstream of the runaway.

### Likely cause

In beauty.sno, three patterns share an identical shape:
```
Function    = SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(Functions, TxInList)
BuiltinVar  = SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(BuiltinVars, TxInList)
SpecialNm   = SPAN('.' digits &UCASE '_' &LCASE) $ tx $ *match(SpecialNms, TxInList)
```
And `match` is:
```
DEFINE('match(subject,pattern)')                                      :(match_end)
match          match          =  .dummy
               subject        pattern                                                :S(NRETURN)F(FRETURN)
```
`match` runs a 3-element statement-level pattern match (`subject pattern :S/F`),
which the lexer lowers to the same `?` operator as explicit `?` matches.

The hypothesis: **`SPAN(...)` at node 1136, when it fails to match all
its alternates and a re-entry happens via the surrounding `.`-capture
`Backup1`, produces an exponentially-growing alt-stack OR re-fires its
prefix-length backtracking each time the `.`-capture rolls back.**
Combined with the three identical `Function|BuiltinVar|SpecialNm` arms
each running their own `*match(...)`, the matcher explores an
exponential number of (length, list, capture-state) combinations
without making cursor progress.

In SPITBOL the same input completes quickly because SPAN with no
remaining cursor-advance option returns FAILURE once and the alt-stack
cannot re-fire it without a new cursor base.  Our SpanPattern.Scan
likely either:
  (a) restores its internal length counter to a non-final value on
      Backup, allowing a different shorter span to be tried;
  (b) does not propagate ABORT/seal correctly through the
      ConditionalVariableAssociationBackup1 wrapping, so the alt-stack
      keeps a live alternate that cycles;
  (c) the Backup1 itself sees cursor unchanged after restore and
      treats SPAN's previous FAILURE as a fresh state.

### Recommended next-session targets

1. **Inspect SpanPattern.Scan and its alt-stack interactions.**  How
   does SpanPattern handle backtrack after success?  Does it produce
   multiple alternates (one per matched length), or does it commit
   maximal-munch and offer no alternates?  SPITBOL's behavior is
   maximal-munch with NO retry-shorter-on-backtrack.

2. **Audit `.`-capture entry/exit pair (ConditionalVariableAssociation1
   / Backup1) when the inner pattern is SPAN.**  The SPAN-capture-inside
   pattern needs to commit cursor on success and rollback cursor on
   backtrack — but the SPAN itself should not get a second chance to
   match.  If our SPAN's Scan restores its internal state on Backup1,
   that's the bug.

3. **Single-line repro.**  Construct a minimal `.sno` like:
   ```
       OUTPUT = (' DQ ' ? SPAN('A-Z') $ x $ *match('XX YY', TxInList)) 'OK'
       END
   ```
   If this hangs or produces 100k+ Span steps on dot but completes
   instantly on spl, we have the repro.

4. **Cross-check with spl via `MonitorIpc.TraceEnabled` window.**  Set
   `MONITOR_TRACE_FROM_EVENT=N MONITOR_TRACE_TO_EVENT=N+10` for some N
   right before line-48 enters PatternMatch on both runtimes.  Compare
   the wire's PM_CALL/PM_REDO/PM_FAIL counts: spl should show ~50,
   dot ~518k.

### Status update

  S-2-bridge-7-fullscan          [~] partial — bug isolated to a tight
                                      AST cluster at node-indices
                                      1128-1138 inside the
                                      Function/BuiltinVar/SpecialNm
                                      `SPAN $ tx $ *match(List, ...)`
                                      pattern shape from beauty.sno
                                      lines 60-65.  4.25M node visits
                                      where spl probably does ≤100;
                                      cursor never advances past 18.
                                      Suspect: SpanPattern alt-stack
                                      behavior on backtrack-after-
                                      success when wrapped in
                                      `.`-capture.  Ready for fix
                                      next session — see "Recommended
                                      next-session targets" above.

---

## Session #84 — 2026-05-03 (Sonnet / Lon)

**Outcome:** No commit. Diagnostic-only session. Tree clean across all repos.
HEADs unchanged: snobol4dotnet `9fc75d6`, x64 `5035571`, SCRIP `872b5a3c`.
Beauty self-host unchanged at 47 stderr lines / Parse Error at line 48.

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
   `x64`. Installed `dotnet-sdk-10.0` (10.0.107). snobol4dotnet HEAD
   `9fc75d6` build clean. Beauty self-host baseline confirmed.

2. **Applied per-node visit-count + cursor-histogram + via-mechanism +
   predecessor diagnostic** to `Scanner.cs Match()` and `ScannerState.cs`
   (`.orig`-backed, REVERTED before session end per RULES.md).
   Diagnostic fires when `Subject.Length == 55 && Subject.Contains("DQ")` —
   the line-48 failing-PatternMatch invocation. At 1000 visits to any
   single node, dump the alt-stack, top-visited nodes, cursor distribution,
   via-mechanism (SUB/RESTORE/GOTO), predecessor histogram, and AST
   context.

### Critical empirical findings

**Falsifies session #83's "performance issue, not semantic" hypothesis.**
The runaway IS structural — the alt-stack accumulates redundant
restore-points all converging on the same CVA1 SPAN cluster.

**Per-node visit data:**

  - Node 1128 (CVA1 of arm A): 1000 visits at **cur=20×1000** via
    **RESTORE×1000**, predecessors **{1110×334, 1081×333, 1076×333}**.
  - Node 1075 (CVA1 of arm B): 334 visits at cur=20 via RESTORE×334,
    predecessors {1150×112, 1061×111, 1056×111}.
  - Node 1055 (CVA1 of arm C): 112 visits at cur=20 via RESTORE×112.
  - Node 1029 (some outer driver): 38 visits.

  Visit-count cascade: 38 → 112 → 334 → 1000. Ratios all ≈ 3.
  This is a **4-level cascade with 3-way alternation at each level**:
  outer driver retried 38× → nests into 3 arms × 3 arms × 3 arms ×
  arm reaches CVA1 → 38 × 27 = 1026 ≈ 1000.

  **All 1000 visits at cur=20** (the position immediately AFTER SPAN
  matched 'DQ' at cur=18→20). SPAN at cur=20 fails immediately
  (space char not in SPAN charset). So every retry of the SPAN
  cluster does ~5 wasted node visits (CVA1 → CVA1 → SPAN-FAIL →
  CVABackup → CVABackup) and pops back to the next outer alt.

**The alt-stack at runaway-detection (depth 42):**

  ```
  Top-20 entries: 1081, 1076, 1061, 1056, 1035, 1030, 1009, 1004,
                  983, 978, 933, 932, 932, 932, 932, 892, 887,
                  834, 886, 829
  Frequency:  node=932×4 (ARBNO empty arm, alt=933 sub=937).
  ```

  Five distinct (CVA1-pair-like) saved-node clusters at indices
  978/983, 1004/1009, 1030/1035, 1056/1061, 1076/1081 — each pair
  ~26 nodes apart. These are different `SPAN $ tx $ *match` cluster
  instances, all saved to the alt-stack, all leading back to a
  CVA1 node when restored.

**AST analysis — nodes with `Alternate=1128`:**

  Nine different nodes have `Alternate=1128`:
  ```
  node=1076 ''            alt=1128 sub=1080
  node=1081 ''            alt=1128 sub=1085
  node=1110 SpanPattern   alt=1128 sub=1112
  node=1112 '.'           alt=1128 sub=1114
  node=1114 MarkPattern   alt=1128 sub=1117
  node=1118 ''            alt=1128 sub=1119
  node=1119 SealPattern   alt=1128 sub=1121
  node=1122 ''            alt=1128 sub=1124
  node=1125 ''            alt=1128 sub=1143
  ```

  These are all in the BuiltinVar/SpecialNm graft regions (indices
  1075-1125). Their `Alternate=1128` correctly means "if I fail,
  try arm Function (which starts at 1128)" — a valid forward-pointing
  alternation link.

**The actual bug — interpretation:**

  The pattern is structurally CORRECT but produces exponential
  backtracking. The grammar has 3-way alternation arms (Function |
  BuiltinVar | SpecialNm) embedded in deeper nesting (4 levels),
  giving 3^4 = 81 backtrack paths. Each path's SPAN-cluster try
  at cur=20 fails immediately (space char). The cumulative ~1000
  retries at cur=20 are all redundant — each tries the same
  pattern at the same cursor against the same subject, producing
  the same FAIL.

  **SPITBOL avoids this catastrophic backtracking via** one or
  more of:
  (a) cursor-position memoization: same `(pattern, cursor)` failure
      cached, second try short-circuits.
  (b) FENCE seal commits more aggressively, suppressing back-pops
      into already-failed-arm regions.
  (c) different alt-stack management around `*X` graft+fail: SPITBOL
      may pop a wider span on `*X`-fail than dot does.

  Beauty parses correctly on SPITBOL. Beauty's grammar is the same
  on both runtimes. The semantic bug must be in dot's pattern-match
  engine — most likely in (a) or (b).

### Concrete next-session targets

1. **Inspect SPITBOL's bktrk implementation**
   (`x64/sbl.min`) — find how it handles the *X-graft + arm-fail
   sequence. Specifically: when an arm ending in *X fails (after
   *X grafted and was followed by a failure), what does SPITBOL
   pop from the saved-state stack? Look at `bktrk`, `xkalt`,
   and the dispatch around `mtchcd` for unevaluated patterns.

2. **Verify the FENCE seal placement** in `Expr17 = FENCE(...)`.
   The structure built is `Concat(Mark, Concat(P, Seal))` where
   P is the 9-arm alternation. Currently when an EARLY arm
   (e.g. *Function) succeeds-then-fails, backtrack pops ITS
   internal alternates AND the *Function arm itself, then tries
   the next arm. But a deeper failure that should re-trigger the
   FENCE's outer arms isn't covered — and may be why the alt-stack
   accumulates many CVA1 saves all at cur=20.

3. **Position-based memoization candidate fix**: in
   `Scanner.PatternMatch` or `Scanner.Match`, add a per-pattern-
   match cache `Set<(node_index, cursor)> _failedAttempts`.
   When `Match()` is about to enter a node at a cursor, check
   if `(node, cursor)` was already in the failed-set; if yes,
   return FAILURE immediately without firing Scan.
   
   **Risk:** this changes semantics if a pattern's outcome at
   `(node, cursor)` depends on hidden state (like AlphaStack
   contents from outer captures, or BetaStack contents). The
   pattern-match engine relies on side effects from CVA captures
   that change the AlphaStack between attempts. So same
   `(node, cursor)` could legitimately produce different outcomes
   on different attempts. **The cache must include the relevant
   side-effect state in its key**, or it will break captures.
   
   For terminal patterns (LiteralPattern, SpanPattern, BreakPattern,
   etc.) that ONLY consume cursor (no side effects), the
   `(node, cursor)` cache IS safe and would prevent the redundant
   1000 retries at cur=20.

4. **Targeted optimization: short-circuit failed-SPAN cache.**
   In `SpanPattern.Scan`, cache the cursor positions where the
   span failed. On second entry at the same cursor, return
   FAILURE immediately. This is safe (SpanPattern has no side
   effects) and would eliminate 1000 redundant `_charList.Contains`
   probes.

   **Implementation sketch** in `SpanPattern.cs`:
   ```csharp
   // Cache failed-cursor results per Scanner instance.
   // Cleared per PatternMatch (since Subject can change).
   internal override MatchResult Scan(int node, Scanner scan)
   {
       // Side-effect-free fast path: if SPAN failed here last time, fail again.
       if (scan.SpanFailedAt(node, scan.CursorPosition))
           return MatchResult.Failure(scan);
       ...
       // After computing match outcome:
       if (!match) scan.RecordSpanFail(node, scan.CursorPosition);
       return ...;
   }
   ```
   With `Scanner.SpanFailedAt(node, cur)` and `Scanner.RecordSpanFail`
   maintaining a per-PatternMatch dictionary of `(node, cursor) → ()`.
   Cleared in `PatternMatch()` when a new match starts.

   This is a **performance** optimization that does not change
   semantics. It would not by itself fix line 48 if the bug is
   elsewhere — but it would let the runaway terminate quickly
   enough to see what the match's actual outcome is.

5. **Run beauty self-host with the failed-SPAN cache.** If the
   match actually SUCCEEDS at cursor advance, then the gating
   bug is performance (never reaches the success path due to
   timeout/effort). If it still FAILS at the same Parse Error,
   then there's a real semantic bug elsewhere.

### Hand-off state — session #84

  - All five repos clean. No `.orig` files. No diagnostic patches.
  - HEADs unchanged from session #83.
  - Beauty self-host gate unchanged: exit 0, 47 stderr lines, Parse
    Error at line 48. SPITBOL oracle md5 `abfd19a7a834484a96e824851caee159`
    (Milestone 1 invariant intact).
  - Goal-file edits this session: this narrative only.

### Status updates

  S-2-bridge-7-fullscan          [~] partial — line-48 runaway
                                      precisely characterized:
                                      4-level nested 3-way
                                      alternation backtracking,
                                      ~1000 redundant SPAN retries
                                      at cur=20 (where SPAN always
                                      fails). All visits at the
                                      same cursor against the same
                                      pattern produce the same FAIL.
                                      Position-memoization or
                                      SpanPattern-failure-cache is
                                      the recommended next-session
                                      lead.

### Session #84 addendum — Milestone 1 SPITBOL md5 invariant note

Final handoff verification noted that SPITBOL on the current corpus
HEAD (`4d4dea39`) produces md5 `9cddff2534472b822438801d8db58a99` (622
stdout lines), differing from the recorded Milestone 1 invariant
`abfd19a7a834484a96e824851caee159` (646 lines).

This is **not** a regression caused by this session.  Corpus commit
`5cc1baa` ("SB-6.E.7-M: strip sno prefix from beauty.sno", May 2
2026 — pre-session-#84) was a 67-name/319-occurrence mechanical rename
that changed beauty.sno's bytes; the recorded md5 predates that
rename.  The output is shorter (renamed identifiers are shorter), so
the beautified line count and md5 are different but the run is clean.

The NET-BEAUTY-SELF gate is "exit 0, ≥500 stderr-clean lines, no
error lines" — SPITBOL passes that gate (exit 0, 622 stdout, stderr
clean).  PLAN.md and GOAL-LANG-SNOBOL4.md still record the old md5;
those notes need updating in a future grand-master-reorg session.

---

## Session #85 — 2026-05-03 (Sonnet / Lon)

**Outcome:** snobol4dotnet `80c828a` LANDED — terminal-failure
memoization eliminates session #84's catastrophic backtracking
(4.25M node visits → bounded by AST node count × subject length).
Beauty 17/17 PASS, 2074p/14f baseline matched, beauty self-host
exit 0 / 47 stderr lines unchanged at the SAME line-48 Parse Error.
**Diagnostic C# function tracing in the [#2630, #2700) wire-event
window pinpointed the actual structural bug**: in dot's snoExpr14
alternation, the *X UnevaluatedPattern at AST node-index 781
(presumed `*snoProtKwd` based on context) has `Alternate=-1`,
meaning its alt-link to `*snoUnprotKwd` (node ~783) is missing.

### What landed (commit `80c828a`)

Per session #84's recommendation: per-PatternMatch
`HashSet<(int node, int cursor)> _terminalFailCache` in
`Scanner.cs`.  When `IsPureTerminal(node.Self)` and the cache
contains `(SelfIndex, CursorPosition)`, return Failure immediately
without re-invoking Scan.  After Scan returns FAILURE on a pure
terminal, the (node, cursor) is recorded.  Cleared at the start
of every PatternMatch.

Pure terminals (memoized): SpanPattern (static char list only —
new `IsStaticCharList` accessor), LiteralPattern (exact
GetType() — to avoid memoizing CVA*/IVA* subclasses), NullPattern
(exact GetType()), AnyPattern, BreakPattern (static char list
only), LenPattern, FailPattern, AbortPattern, PosPattern,
RPosPattern, TabPattern, RTabPattern.

Test gates clean:
  - Unit suite: 2074p/14f (baseline match).
  - Beauty 17/17 corpus drivers: 17/17 PASS.
  - Beauty self-host: exit 0, 47 stderr lines, ~2.7s wall clock
    (was 30s+ timing out before graft cache; ~2.1s with graft
    cache alone; this fix is on top of graft cache).
  - SPITBOL oracle md5 `9cddff2534472b822438801d8db58a99` unchanged.

### Diagnostic C# function tracing — the user's strategy applied

Per the user's explicit guidance — *"use automatic C# function
tracing from last agreed sync step code position through to first
diverged sync step code position"* — the IPC sync-step monitor
DIVERGE was reproduced at step #2839 (same as session #80).
Diagnostic patches (REVERTED before commit per RULES.md) were
applied to `Scanner.PatternMatch`, `Scanner.Match`, and
`Define.cs ExecuteProgramDefinedFunction`'s `EmitCall` site:

  - `Scanner.PatternMatch` entry: log subject + length + anchor
  - `Scanner.Match` per-node entry: log node index, NodeTag,
    cursor, Subsequent, Alternate
  - `Define.cs` per-call entry to user-defined `match()`: log
    arg0 length and contents (was hypothesized in session #80 to
    contain the wrong list slot)

All gated on `MonitorIpc.TraceEnabled`.

Trace results across the full beauty self-host run with
`MONITOR_TRACE_FROM_EVENT=1 MONITOR_TRACE_TO_EVENT=99999999`:

#### Finding 1 — `match(snoUnprotKwds, ...)` is NEVER called

Across 317 calls to user-defined `match()`, arg0 lengths
distribute as:
  - `122` (snoProtKwds): **2 calls** total
  - `455` (snoFunctions): 106 calls
  - `50`  (snoSpecialNm): 104 calls
  - `57`  (snoControl): 105 calls
  - `125` (snoUnprotKwds): **0 calls** ← MISSING

This **falsifies session #80's "wrong slot" hypothesis** (which
session #81 already partially refuted): arg0 to match() is always
the correct list — slots are not confused.  But the
`*match(snoUnprotKwds, snoTxInList)` arm is never reached because
the alternation never dispatches it.

#### Finding 2 — node 781's Alternate is -1, not 783

Trace at `MONITOR_TRACE_FROM_EVENT=2630 TO=2900` (window covering
the second snoProtKwds match call at ec=2635 and the next match
at ec=2696 = snoFunctions):

```
[FN match ec=2635] arg0.len=122 arg0='ABORT ALPHABET ARB BAL FAIL FENCE FILE FNCLEVEL...'   ← snoProtKwds
[PM ec=2637] anchor=False subjLen=122 subj='ABORT ALPHABET...'
... (60 wire events of inner snoProtKwds matching) ...
[FN match ec=2696] arg0.len=455 arg0='ANY APPLY ARBNO ARG ARRAY ATAN...'                    ← snoFunctions (SHOULD BE snoUnprotKwds!)
```

Between event 2635 (snoProtKwds match starts) and 2696
(snoFunctions match starts), the trace inside the outer parser
runs the snoExpr14 alternation backbone:

```
[M] node=597  '&'   cur=27 sub=599  alt=615
[M] node=615  '&'   cur=27 sub=617  alt=629
[M] node=629  '+'   cur=27 sub=631  alt=643
... (literal-arm chain) ...
[M] node=755  '='   cur=27 sub=757  alt=769
[M] node=769  '|'   cur=27 sub=771  alt=781
[M] node=781  *<lambda>  cur=27 sub=105  alt=-1   ← THE BUG
[M] node=783  *<lambda>  cur=27 sub=785  alt=-1
[M] node=822  MarkPattern cur=27 sub=828 alt=-1   ← FENCE Mark
... (snoExpr15+ subtree) ...
```

Node 781 IS `*snoProtKwd` (its body's evaluation is what feeds
snoProtKwds into match() at ec=2635 followed by ec=2696's call
to match(snoFunctions)).  Per beauty.sno's grammar:

```
snoExpr14 = ... '|' | *snoProtKwd | *snoUnprotKwd | '&' SPAN(...)
```

Node 781 (*snoProtKwd) should have `Alternate = leftmost(*snoUnprotKwd's-arm)`,
which would be node 783.  Instead, node 781 has `Alternate = -1`.

When 781's body returns FRETURN (snoProtKwds doesn't contain
FULLSCAN/MAXLNGTH), the Match() loop has no live alternate to
restore for THIS node.  Control falls back to the alt stack —
which contains 769.alt=781 (already consumed), 755.alt=769
(would re-cycle), and earlier saves.

#### Finding 3 — the chain saved alts are all forward-pointing within the same chain

The alternation backbone `597 → 615 → 629 → 643 → ... → 769 →
781` is built as a Subsequent chain (each `sub=` points to the
next).  Each save during entry is `alt = next-sibling-of-myself`:
615 saves alt=629, 629 saves alt=643, etc.  Restoring the
alt-stack post-781 cycles back through nodes already failed.

THIS IS WHY THE PARSE FAILS: there is no Alternate link out of
the literal/UnevaluatedPattern alternation chain that points to
the next OUTER alternation arm (the `&` arm at node ~822 or its
predecessors), AND there is no live OUTER alternate saved on
the stack that points down into snoUnprotKwd's arm.  After the
chain exhausts, control falls through to whatever was most
recently saved on the alt-stack (a high-numbered alt from
deeper-graft territory), eventually landing in the snoVar/snoAtom
subtree (node ~822+) where `*snoFunction` lives.  That's how
session #74 saw `*snoFunction` reached "before" `*snoUnprotKwd`.

### What the bug is structurally

The grammar `A | B | C | D | ...` (left-associative) builds the
AST as `Alt(Alt(Alt(A, B), C), D)`.  `ComputeAlternate` walks
the parent chain looking for first ancestor where currentNode is
LEFT-CHILD of an `AlternatePattern`, then descends right-child
left-spine to the leftmost terminal.  This algorithm IS correct
for left-associative alts — every arm except the rightmost
should have a forward Alternate.

For a 16-arm alternation like beauty's snoExpr14, the AST should
have all 16 arms reachable.  The wire shows the chain
`597 → 615 → ... → 781` with each arm having alt = next-arm.
But node 781 has alt=-1.  Either:

  (a) The PatternFactories construction for `'|' | *snoProtKwd
      | ...` produces a different shape — perhaps a
      ConcatenatePattern where it should be an AlternatePattern
      (the lexer/builder may have a bug with mixing literal arms
      and `*X` arms).

  (b) `ComputeAlternate` has an early-termination bug for
      UnevaluatedPattern terminals that fires before reaching the
      grandparent Alt.  The current algorithm (lines 112-141 of
      AbstractSyntaxTree.cs) uses
      `parentNode.SelfIndex == 0` to detect root — but if the
      tree has Concatenate intermediates that alter parent
      structure for `*X` nodes vs literal nodes, the walk could
      bail prematurely.

  (c) The Subsequent chain `597 → ... → 781` is itself wrong
      — these arms should not be subsequent-chained in the first
      place (they should each be at different alternation
      depths).  If the construction collapses alternation into
      concatenation somewhere, both Subsequent and Alternate
      links would be skewed.

### Recommended next-session execution plan

1. **AST shape dump for snoExpr14** — instrument
   `AbstractSyntaxTree.Build` to dump the full `_nodes` array
   when the pattern object passed in is the `snoExpr14` pattern
   (identifiable by being the pattern argument to a PatternMatch
   whose subject contains `&FULLSCAN` or `&MAXLNGTH`).  Print
   each node's `(SelfIndex, Self.GetType().Name,
   Self.DebugPattern() if terminal, ParentIndex, LeftChildIndex,
   RightChildIndex, Subsequent, Alternate)`.

2. **Locate node 781 and its parent chain** in the dump.  Walk
   `ParentIndex` until you reach the root (index 0).  At each
   level, log whether the current node is left or right child
   and what kind of NonTerminalPattern its parent is
   (AlternatePattern, ConcatenatePattern).

3. **Compare to grammar expectation.**  beauty.sno snoExpr14
   has roughly 16 arms.  The leftmost terminals of each arm
   should each appear as a separate path-from-root.  If only a
   linear chain shows up, the build has flattened the
   alternation into a concat (case (a) or (c)).  If a proper
   tree shows up but `*snoProtKwd`'s parent is not an Alt with
   `*snoUnprotKwd` on the right, the issue is (a) too.  If
   parent IS Alt with `*snoUnprotKwd` on right but
   ComputeAlternate returns -1, the issue is (b).

4. **Likely fix surface:**
   - Most probable: a precedence bug in
     `PatternFactories.cs` / `BuilderPattern.cs` (or wherever
     `'|' | *X | *Y` is parsed/lowered) that mishandles
     low-precedence operators around `*X` UnevaluatedPattern
     arms when adjacent literal arms exist.
   - Less likely: ComputeAlternate's `parentNode.SelfIndex == 0`
     early-exit firing too soon for `*X`-arm nodes.

5. **Test gate:** post-fix, the 317-call match() distribution
   should show ≥1 call with arg0.len=125 (snoUnprotKwds) when
   beauty self-host parses lines 26 (`&FULLSCAN = 1`) and 27
   (`&MAXLNGTH = 524288`).  Beauty self-host stderr line count
   should advance past 47 (current Parse Error at line 48).

### Hand-off state

- snobol4dotnet HEAD: `80c828a` (this session's commit, pushed).
- SCRIP, x64, corpus: unchanged.
- Working trees clean across all repos.
- Diagnostic patches reverted before commit per RULES.md.

### Status updates

  S-2-bridge-7-fullscan-memoize  [x] LANDED — `80c828a`.
                                     Catastrophic backtracking
                                     eliminated; structural bug
                                     surfaces directly.
  S-2-bridge-7-fullscan          [~] partial — structural bug
                                     pinpointed: snoExpr14 AST has
                                     `*snoProtKwd` (node 781) with
                                     `Alternate=-1` instead of
                                     pointing to leftmost-of-
                                     `*snoUnprotKwd`-arm (likely
                                     node 783).  Bug is in
                                     PatternFactories /
                                     AbstractSyntaxTree.Build /
                                     ComputeAlternate — narrow
                                     candidate set; next session
                                     dumps the AST and isolates.

---

## Session #86 — 2026-05-03 (Sonnet / Lon)

**Outcome:** No commit. Diagnostic-only session, but **the structural
bug is now precisely characterized at the AST construction level**:
the snoExpr14 alternation pattern, when built, is **missing 6 of its
18 arms** in the static AST.  The `*ProtKwd ~ 'ProtKwd'` and
`*UnprotKwd ~ 'UnprotKwd'` arms (positions 4 and 5 of the source
grammar), as well as `'@'`, `'~'`, `'?'`, and `*Expr15` arms (positions
1, 2, 3, and 18) — they are NOT present in the AST that gets matched
at runtime against `&FULLSCAN`/`&MAXLNGTH` subjects.

User's "flatter the trees for Alternation and Subsequentation" hint
was the strategic redirect — the deeply nested right-skewed
`Alt(arm1, Alt(arm2, Alt(arm3, ...)))` representation is hiding
arm-construction bugs.  A flat alternation `Alt[arm1, arm2, arm3, ...arm_n]`
with N direct children would make missing arms visible at construction.

### What ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`,
   `snobol4dotnet`, `x64`. snobol4dotnet HEAD `80c828a` (session #85's
   memoization fix).  Beauty self-host baseline: exit 0, 47 stderr
   lines, ~2.7s wall clock.

2. **AST dump diagnostic patch** (REVERTED before commit per RULES.md)
   in `Scanner.PatternMatch`:
   - On every PatternMatch return (success OR fail) where `_ast.Count > 600`,
     dump nodes 590-829 with full structural info: SelfIndex, type name,
     tag (UnevaluatedPattern.MethodName, LiteralPattern.Literal, or class
     name), ParentIndex, ChildType, LeftChild, RightChild, Subsequent,
     Alternate.
   - Output gated on `MonitorIpc.TraceEnabled` (works standalone after
     session #83's `9fc75d6` productionized it).
   - Run with `MONITOR_TRACE_FROM_EVENT=1 MONITOR_TRACE_TO_EVENT=99999999`.

3. **Captured 13 PatternMatch returns** with nodeCount > 600, including
   FULLSCAN and MAXLNGTH parses (both reported `RETURN-success` by
   PatternMatch — meaning the outer parse succeeded; the Parse Error
   fires from the inner reScan failing on a downstream construct).

### Critical finding — the snoExpr14 alternation chain in the static AST has 13 *X UnevaluatedPattern arms instead of the expected 16

Source grammar `Expr14` (beauty.sno lines 150-167) has 18 arms:

```
Expr14 = '@' *Expr14 ("'@'" & 1)            arm 1
       | '~' *Expr14 ("'~'" & 1)            arm 2
       | '?' *Expr14 ("'?'" & 1)            arm 3
       | *ProtKwd ~ 'ProtKwd'               arm 4   <-- ABSENT in AST
       | *UnprotKwd ~ 'UnprotKwd'           arm 5   <-- ABSENT in AST
       | '&' *Expr14 ("'&'" & 1)            arm 6
       | '+' *Expr14 ("'+'" & 1)            arm 7
       | '-' *Expr14 ("'-'" & 1)            arm 8
       | '*' *Expr14 ("'*'" & 1)            arm 9
       | '$' *Expr14 ("'$'" & 1)            arm 10
       | '.' *Expr14 ("'.'" & 1)            arm 11
       | '!' *Expr14 ("'!'" & 1)            arm 12
       | '%' *Expr14 ("'%'" & 1)            arm 13
       | '/' *Expr14 ("'/'" & 1)            arm 14
       | '#' *Expr14 ("'#'" & 1)            arm 15
       | '=' *Expr14 ("'='" & 1)            arm 16
       | '|' *Expr14 ("'|'" & 1)            arm 17
       | *Expr15                            arm 18  <-- ABSENT in AST
```

In the dumped static AST for the `&FULLSCAN = 1` parse (PatternMatch
returned success at ec=2394, nodeCount large enough for the full
grammar):

  - **13 UnevaluatedPattern (`*X`) nodes appear** in the alternation
    chain at indices: 617, 631, 645, 659, 673, 687, 701, 715, 729,
    743, 757, 771, 781.  Their alt-links: 629, 643, 657, 671, 685,
    699, 713, 727, 741, 755, 769, 781, **-1** respectively.
  - **13 corresponding literal-prefix arms** at indices 615, 629, 643,
    ..., 769 (`'&', '+', '-', '*', '$', '.', '!', '%', '/', '#', '=', '|'`).
  - **Node 597 = `'&'` (NOT `'@'`)** — the FIRST literal arm in the
    AST chain is `'&'`, not the source's first arm `'@'`.

So the AST chain has 13 literal-prefixed arms = arms 6-17 of the source
(twelve `'&'..'|'`) plus an extra `'&'` at the head.  Arms 1-5
(`'@'`, `'~'`, `'?'`, `*ProtKwd`, `*UnprotKwd`) and arm 18 (`*Expr15`)
are MISSING.  6 of 18 arms absent.

### Where the missing arms went

Two hypotheses, both consistent with evidence:

  - **(H1) Compile-time evaluation discarded them.**  Arms 4-5
    (`*ProtKwd ~ 'ProtKwd'`, `*UnprotKwd ~ 'UnprotKwd'`) are
    OPSYN-bound `~ → shift`.  semantic.inc:7 binds `OPSYN('~', 'shift', 2)`,
    and `shift(p, t) = EVAL("p . thx . *Shift('" t "', thx)")` (line 16)
    returns a pattern via `EVAL`.  If the `EVAL` runs at AST-build time
    AND its return value is dropped on the floor (e.g. because the
    result is `Failure`-state when the alternation construction sees
    it), the arm doesn't make it into the final pattern object.

  - **(H2) Alternation operator `|` has a tree-shape bug.**  When 18
    arms are chained left-to-right, the `|` operator builds them
    incrementally as `Alt(prev, new_arm)`.  If at any iteration the
    `new_arm` is missing or the structure is incorrect, the resulting
    pattern's tree is incomplete.  18 source arms → 12 visible-as-arms
    → consistent with the alternation chain being TRUNCATED at some
    construction step.

### Why right-associative alt construction (vs left-associative) matters here

The current AST shows right-associative shape: `Alt(arm1, Alt(arm2, ..., Alt(arm_n-1, arm_n)))`.
Each arm except the last is LEFT-child-of-Alt, so its Alternate
(via ComputeAlternate) correctly points to leftmost-of-next-arm.
The last arm has Alternate=-1 (correct: no further arms).

Node 781 has Alternate=-1.  Node 781 IS the rightmost arm of its
Alt-chain — but it's NOT supposed to be the last arm of snoExpr14.
That tells us the AST's Alt-tree LITERALLY ends at node 781.  The
remaining grammar arms `*Expr15` etc. were never wired into this tree.

### Why the user's flattening hint matters

A **flat alternation node** `FlatAlt[arm1, arm2, ..., arm_n]` with N
direct children would:

  1. Make missing arms IMMEDIATELY visible at construction time
     (the Children list has exactly N entries; if 6 arms are silently
     dropped, the list is short by 6 — easy to assert at build).
  2. Eliminate all the parent-walking complexity in ComputeAlternate
     for alternations.  Each child's Alternate is just the next sibling.
  3. Provide a single point of testing for the grammar-arm count
     against beauty's known 18-arm Expr14.

Same for ConcatenatePattern: a flat `FlatConcat[op1, op2, ..., op_n]`
with N children replaces nested `Concat(Concat(Concat(...)))` and
makes Subsequent computation trivial (next sibling).

### Concrete next-session execution plan

1. **Reproduce the missing-arms finding under controlled conditions.**
   Re-apply the AST-dump diagnostic patch from this session.
   Run beauty self-host with full trace.  Confirm the FULLSCAN parse's
   AST has exactly 13 `*X` arms (not 16) in the snoExpr14 chain.

2. **Bisect WHEN the arms get lost.**  Add a print in
   `PatternAlternation (Pipe).cs` `CreateAlternatePattern` that logs
   each invocation: argument types (PATTERN, EXPRESSION), counts of
   nodes in left-pattern and right-pattern, and the resulting tree
   shape.  Run beauty self-host.  The trace will show the 17 invocations
   building the snoExpr14 alternation; identify which iteration drops
   an arm.

3. **Verify shift() is producing patterns at compile time.**  Insert
   a temporary `OUTPUT = 'shift returned: ' p2` before the
   `:(RETURN)` in `semantic.inc:16`'s `shift` body.  Re-run beauty
   self-host and check whether shift fires for `*ProtKwd ~ 'ProtKwd'`
   and `*UnprotKwd ~ 'UnprotKwd'` and what it returns.

4. **Implement flat alternation/concatenation patterns.**  This is
   the user's strategic guidance.  Two-phase:
     - Phase A: introduce `FlatAlt` / `FlatConcat` non-terminal classes
       that hold `List<Pattern> Children` directly.  Modify `BuildNodeList`
       to recognize them and emit one node per child + one parent node
       (instead of N-1 binary-tree nodes).  Modify ComputeNext to
       look at sibling list directly.
     - Phase B: rewrite operator constructors `|` and `<concat>` to
       coalesce chains: `(A | B) | C` builds `FlatAlt(A, B, C)` rather
       than `Alt(Alt(A, B), C)`.  Same for concat.

5. **Acceptance gate:** after Phase A+B, the static AST for snoExpr14
   has exactly 18 arms in a single FlatAlt node.  Beauty self-host
   gate: `match(UnprotKwds, ...)` is now invoked at least once
   (confirmed via the trace from session #85), and the line-26 / line-48
   Parse Errors clear.

### Hand-off state

  - snobol4dotnet HEAD: `80c828a` unchanged.
  - All five repos clean.  No `.orig` files, no diagnostic patches.
  - Beauty self-host gate unchanged: 47 stderr lines.
  - SPITBOL oracle md5 `9cddff2534472b822438801d8db58a99` unchanged.
  - Goal-file edits this session: this narrative only.

### Status updates

  S-2-bridge-7-fullscan          [~] partial — bug ROOT CAUSE now
                                      precisely characterized at AST
                                      construction level: 6 of 18
                                      snoExpr14 arms missing
                                      (`'@', '~', '?', *ProtKwd,
                                      *UnprotKwd, *Expr15`).
                                      Construction or evaluation of
                                      these arms during pattern build
                                      is dropping them on the floor.

  S-2-bridge-7-flatten           [ ] open — user's strategic guidance:
                                      replace nested Alt/Concat trees
                                      with flat N-ary node types.
                                      Will surface this missing-arms
                                      bug AND simplify the entire
                                      pattern-match-engine
                                      Subsequent/Alternate computation.

---

## Session #87 — 2026-05-03 (Sonnet / Lon)

**Outcome:** No commit. Diagnostic-only session. Tree clean across all
repos. HEADs unchanged: snobol4dotnet `80c828a`, x64 `5035571`, SCRIP
`872b5a3c`. Beauty self-host gate unchanged at 47 stderr lines / Parse
Error at line 48.

**Key result: Session #85 and #86's "13 of 18 Expr14 arms missing"
diagnosis is FALSIFIED.** The Expr14 alternation tree is structurally
complete — all 18 arms are present in the grafted AST. The session #85
literal-arm chain that started with `'&'` at node 597 was not a
truncated 13-of-18 chain; it was arms 6-17 (12 arms) of Expr14, with
arms 1-3 and 4-5 sitting EARLIER in the AST at nodes 517-588, and arm
18 (`*Expr15`) sitting later. Sessions #85 and #86 both built their
hypotheses on a misreading of the AST dump.

### What this session ran

1. **Set up clean.** Cloned `.github`, `corpus`, `SCRIP`, `snobol4dotnet`,
   `x64`. Installed `dotnet-sdk-10.0` (10.0.203). snobol4dotnet HEAD
   `80c828a` build clean. Beauty self-host baseline confirmed: exit 0,
   47 stderr lines, Parse Error at line 48.

2. **Instrumented `CreateAlternatePattern`** (`PatternAlternation (Pipe).cs`,
   `.orig`-backed, REVERTED before session end per RULES.md) — log every
   `|` operator call with operand types and resulting alt-tree arm
   count. Gated on `MonitorIpc.TraceEnabled`.

3. **Ran with `MONITOR_TRACE_FROM_EVENT=1 TO=9999999`.** Found:
     - **92 `|` operator calls** during beauty.sno startup, **ZERO
       failures** (no `LogRuntimeException(5/6)`, no silent drops).
     - **PIPE #43→#55 progressively grow a right-skewed alt-tree from 6
       arms to 18 arms** — exactly Expr14's 18 alternative arms. The
       tree is built correctly with all 18 arms.
     - The `|` operator is NOT dropping arms.

4. **Instrumented `AbstractSyntaxTree.Graft`** to dump the structural
   AST (terminals AND non-terminals, with subclass discrimination for
   ConditionalVariableAssociation*/ImmediateVariableAssociation*) when
   the grafted sub-pattern is a 10+-arm AlternatePattern. Found:
     - **Expr14 is grafted 87+ times during beauty self-host**, each
       time with `subAst.Count=267` nodes.
     - Full arm-by-arm structural inspection of arm 1 (`'@' *Expr14
       ("'@'" & 1)`) at nodes 517-528:
       ```
       N node[516] Cat L=517 R=518            arm 1 root
       T node[517] L'@' sub=519 alt=531       arm 1 leftmost
       N node[518] Cat L=519 R=520            tail of arm 1
       T node[519] **<lambda>                  *Expr14 unevaluated
       N node[520] Cat L=521 R=524            tail = reduce result
       N node[521] Alt L=522 R=523            va = Alt(CVA1, CVABackup1)
       T node[522] ConditionalVariableAssociation1
       T node[523] ConditionalVariableAssociationBackup1
       N node[524] Cat L=525 R=526            Cat(epsilon, vb)
       T node[525] L''                         epsilon (LiteralPattern(""))
       N node[526] Alt L=527 R=528            vb = Alt(CVA2, CVABackup2)
       T node[527] ConditionalVariableAssociation2
       T node[528] ConditionalVariableAssociationBackup2
       ```
       This is the textbook structure for `'@' *Expr14 (epsilon . *Reduce(...))`.

     - **Arms 1, 2, 3 are structurally identical** (just different
       literals at 517, 531, 545). All have `*<lambda>` UnevaluatedPattern
       (= `*Expr14`) directly after the literal, plus the `.thx . *Reduce`
       capture chain.

5. **Why arms 4 and 5 look different in the AST.** Arms 4-5 =
   `*ProtKwd ~ 'ProtKwd'` and `*UnprotKwd ~ 'UnprotKwd'`. The `~`
   operator is OPSYN'd to `shift(p,t)`, which calls
   `EVAL("p . thx . *Shift('" t "', thx)")` at PATTERN BUILD TIME.
   Inside the EVAL, the local variable `p` resolves to an ExpressionVar
   `*ProtKwd`. When that ExpressionVar is dereferenced, it returns the
   ACTUAL pattern of `ProtKwd`, which is
   `'&' SPAN(&UCASE &LCASE) $ tx $ *match(ProtKwds, TxInList)` (from
   beauty.sno line 66). So arm 4's structural realization is the entire
   ProtKwd pattern INLINED, then wrapped in two `.` captures. The `'&'`
   that session #85 saw at node 569 was NOT the `'&'` literal of arm 6
   — it was the `'&'` literal INSIDE ProtKwd, inlined into arm 4.

6. **Confirmed via direct semantic test:** ran a 5-line standalone
   program that calls `shift(*ProtKwd, 'ProtKwd')` directly AND
   `*ProtKwd ~ 'ProtKwd'` via OPSYN, with internal traces. Both
   produce `pattern` datatype, both see `p` as `expression` and `t` as
   `'ProtKwd'`, both build the same EVAL string
   `p . thx . *Shift('ProtKwd', thx)`. The OPSYN dispatch is correct.

### What this means for the real bug

The line-48 Parse Error is NOT caused by missing arms in Expr14. The
Expr14 AST is structurally complete and contains all 18 arms (with
arms 4-5 inlined to be quite large — each ~25-30 nodes due to inlining
the full ProtKwd/UnprotKwd patterns). Sessions #85 and #86 spent their
time on a misdiagnosis.

The real bug is somewhere else — most likely:
- (a) **Match-time alt-stack handling** for deeply-nested inlined
  sub-patterns. Arms 4-5 contain nested `.` captures (from `shift`'s
  EVAL'd `p . thx . *Shift(...)` outer capture) wrapping nested `$`
  captures (from ProtKwd's own `$ tx $ *match(...)`). The combined
  alt-stack save/restore behaviour during deep backtrack across these
  layers is the suspect.
- (b) **Subsequent-link wiring** through the inlined ProtKwd subtree.
  The inlined ProtKwd has its own `*match()` UnevaluatedPattern at the
  end, which when match() FRETURNs needs to propagate failure out
  through arm 4's wrapping `. *Shift(...)` capture nodes to the alt
  stack. This propagation path crosses several `.` capture commit
  points and may be losing the failure signal.
- (c) **The seal-skip fix from session #67** (`c578fb5`) — which on
  `-2` seal pop continues popping until a real alternate is found —
  may be too aggressive when arm 4's deep nested FENCE-equivalent
  saves are below the seal. If a save belonging to arm 4's `.thx . *Shift`
  capture is popped past, the outer alternation never reaches arms 5,
  6, etc.

### What is now known to NOT be the line-48 bug

Adding to the existing list (sessions #67–#86):
- **Pattern construction does not drop arms.** The `|` operator
  invocation count and structural correctness rule out
  `CreateAlternatePattern` as the culprit.
- **The 18-arm Expr14 alt tree is built correctly** as a right-skewed
  binary chain (PIPE #55 final state).
- **The Expr14 graft into the runtime AST contains all 18 arms.**
- **OPSYN dispatch for binary `~` correctly invokes `shift`** with the
  expected operand types.
- **Session #85's "node 781 has alt=-1" was likely the LAST arm of
  Expr14's alt chain** — i.e. arm 17 `'|' *Expr14` having no successor
  arm in the alt direction (because arm 18 `*Expr15` is reached via
  Subsequent, not Alternate). That alt=-1 may be CORRECT for the
  rightmost arm.

### Concrete next-session execution plan

1. **Do not chase "missing arms" any further.** They are not missing.
   This rung's hypothesis was wrong.

2. **Trace the actual line-48 failing match path with arm-visit
   instrumentation.** Add a `[ARM-VISITED]` trace inside `Scanner.Match`
   (gated on `MonitorIpc.TraceEnabled`) that fires whenever a node is
   entered whose ParentIndex's Self is the Expr14 root AlternatePattern.
   Run beauty self-host on the line-48 minimal repro. Confirm whether
   arms 1-5 are entered at all when matching against
   `'                  DQ          =  '"' BREAK('"' nl) '"''`. Either:

   - **Arms 4-5 ARE entered but fail without advancing cursor**:
     bug is in arm 4's inlined ProtKwd subtree's failure propagation.
   - **Arms 4-5 are NEVER entered** (control passes from arm 3's failure
     directly to arm 6 or later): bug is in alt-stack restore order
     or in seal-skip popping past arm 4-5's saves.

3. **If arms 4-5 are entered**, follow with focused tracing inside the
   inlined ProtKwd subtree at the point where `*match(ProtKwds, TxInList)`
   FRETURNs on the `'DQ'` token. The FRETURN needs to propagate up
   through TWO levels of `.` captures (inner from ProtKwd's `$ tx $`,
   outer from arm 4's `. thx . *Shift`) before reaching the Expr14
   alt-stack. Each level of capture's commit/rollback must clear
   Failure correctly to allow arm 5 to be tried.

4. **If arms 4-5 are not entered**, examine `Scanner.cs` lines 100-106
   (the seal-skip Match() loop from `c578fb5`). When the seal-skip
   pops past arm 4-5's saves, the bug is there. Likely needs a
   "stop-at-mark" rather than "stop-at-real-alt" semantic — see the
   FENCE mark/seal mechanism from `bb28a8d` for precedent.

5. **The Mechanism-B trace coverage rung
   (`S-2-bridge-event-bombs-coverage`)** is the right tool for this:
   wire `MonitorIpc.TraceEnabled` into `Scanner.Match`'s alt-stack
   pop path so the trace captures every `RestoreAlternate` and
   `SealAlternates` call between adjacent wire events. Productionize
   that tracing per the rung's "Done when" gate (i-iv) — this is the
   ONE infrastructure investment that pays off across every
   remaining match-time bug in the goal.

### Hand-off state

- snobol4dotnet HEAD: `80c828a` unchanged.
- SCRIP HEAD: `872b5a3c` unchanged.
- x64 HEAD: `5035571` unchanged.
- corpus HEAD: `4d4dea39` unchanged.
- All repos clean. No `.orig` files. No diagnostic patches.
- Beauty self-host gate: exit 0, 47 stderr lines, Parse Error at line 48.
- SPITBOL oracle md5 `9cddff2534472b822438801d8db58a99` (the new
  post-corpus-rename Milestone 1 invariant per session #84's addendum).
- Goal-file edits this session: this narrative only.

### Status updates

  S-2-bridge-7-fullscan          [~] partial — sessions #85/#86's
                                      "missing arms" hypothesis
                                      FALSIFIED. The Expr14 18-arm
                                      alternation tree IS structurally
                                      complete in the grafted AST.
                                      The real bug is in match-time
                                      alt-stack / failure-propagation
                                      handling for arms 4-5's deeply
                                      nested inlined ProtKwd/UnprotKwd
                                      subtrees, OR in seal-skip
                                      popping past those arms' saves.
                                      Three concrete next-session
                                      hypotheses (a/b/c above).

  S-2-bridge-7-flatten           [ ] open — still valid as a future
                                      simplification, but not gating
                                      line 48. Sessions #85-#86's
                                      framing of this rung as the
                                      missing-arms-fix is wrong;
                                      restated as "AST simplification"
                                      for future Milestone 2+ work.

  S-2-bridge-event-bombs-coverage [ ] open — promoted to PRIORITY for
                                      next session. The arm-visit
                                      instrumentation needed to
                                      execute step 2 above is exactly
                                      what this rung productionizes.
                                      Wire `TraceEnabled` into
                                      `Scanner.Match`'s alt-stack
                                      pop path; productionize per the
                                      rung's done-when gate.
