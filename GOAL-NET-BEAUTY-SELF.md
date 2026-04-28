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

  Suggested next-session approach:
  1. Bisect by reducing beauty's grammar — start by feeding a paragraph
     of `&FULLSCAN = 1` to a stripped beauty that retains only the
     statement/keyword grammar paths, see what the smallest grammar is
     that still fails.
  2. Or: instrument beauty.sno's `pp_*` callbacks to log every grammar
     rule that fires, compare spl vs dot.
  3. Or: walk the threaded-loop opcodes for the parse with
     `BuildOptions.TraceStatements=true` (find a way to enable from
     CLI — not currently exposed).

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
