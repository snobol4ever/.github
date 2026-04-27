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

- [ ] **S-2-bridge-7** — Fix the runtime gap, advance to next divergence.
  1. Diagnose the spurious `VALUE i = 1` at step 801.
  2. Fix; re-run S-2-bridge-6.
  3. Repeat until exit 0 and ≥500 stderr lines.

  **Gates after every sub-rung:**
  - Beauty 17/17 still green.
  - Unit tests still green (baseline 2375p/0f/2s).
  - Existing dot bridge smokes still PASS (5+5+9+7+3+6).

  **Mon Apr 27 2026 session — diagnostic notes (no fix landed):**

  Traced the spurious `VALUE i = 1` at step 801 to a stack-imbalance
  bug at the dispatch level, NOT inside `Executive.Assign`'s monitor
  fire-point. The actual chain at OOB iteration of
  `$UTF_Array[i, 2] = UTF_Array[i, 1]`:

  1. LHS `IndexCollection` for `UTF_Array[126, 2]` calls
     `NonExceptionFailure()` → pushes failed sentinel, sets `Failure=true`.
  2. `$` (`OpIndirection` via `OperatorFast`) sees the failed arg in
     `ExtractArguments`, propagates failure cleanly. Stack now has 1
     failed sentinel.
  3. RHS path: `PushVar(UTF_Array)`, `PushVar(i)`, `PushConst(1)` all
     push **unconditionally** (lines 124,134 of `ThreadedExecuteLoop.cs`
     do not check `Failure`).
  4. RHS `IndexCollection` hits `if (Failure) return;` (Array.cs:34) and
     returns silently — does NOT pop the 3 operands it just had pushed
     for it, does NOT push a sentinel.
  5. Stack is now `[…, failed_$, UTF_Array, i, IntegerConst(1)]`.
  6. `BinaryEquals.ExtractArguments(2)` pops `IntegerConst(1)` and `i`,
     both `Succeeded=true` — it does NOT detect failure. `Assign` runs
     legitimately with `leftVar=i, rightVar=1`, fires `EmitValue(i,1)`.

  Two fix attempts, both reverted:

  - **Attempt A — drain in `IndexCollection`** when `Failure` is set:
    pop indices until ArrayVar/TableVar/StatementSeparator, pop the
    collection, then `NonExceptionFailure()`. Broke 0 *new* tests
    relative to the current 26-failure baseline (see baseline note
    below) but the visible Parse Error on `&FULLSCAN = 1` did not
    move — same 28 stderr lines, same Parse Error, same line. So this
    fix targets a path that doesn't actually run before the early
    Parse Error fires.

  - **Attempt B — skip-to-Finalize in `BinaryEquals` dispatch** when
    `Failure` is set, mirroring the `CallFunc` FRETURN-propagation
    pattern. Same observable outcome: 28-line Parse Error unchanged.

  Neither fix advanced the visible self-host gate, because the gate
  fails LONG before step 801 — at line 26 of beauty.sno
  (`&FULLSCAN = 1`, the very first executable statement after the
  `-INCLUDE` block). The monitor-step-801 divergence and the
  user-visible Parse Error on `&FULLSCAN = 1` are almost certainly
  **different bugs**. The monitor diagnosis was made with
  `MONITOR_NAME_WILDCARD=spl` skipping disagreements, which can let
  the harness advance past a real prior divergence. Direct-run
  evidence (28 stderr lines, choke at the `&FULLSCAN` keyword
  assignment) suggests an issue in keyword-assignment handling,
  pattern preamble parsing, or the include-resolution path is
  reachable at runtime but the parser fires from the input stream.

  **Important: pre-existing regression.** Running the documented unit
  test gate against this clone produced **26f/2063p** (test run
  aborted after 2089), versus the goal file's documented baseline of
  **2375p/0f/2s**. Failures cluster around predicate-handling tests:
  `TEST_Negation_001/004/006`, `TEST_GT_002`, `TEST_LT_002`,
  `TEST_NE_002`, `TEST_Choice_002/003`, `TEST_008`,
  `MsilCache_ChoiceOperator_*`, `MsilCache_NegationOperator`, plus 14
  CSNOBOL4 corpus smoke tests (`TEST_Csnobol4__8bit`,
  `_a`, `_alis`, `_alph`, `_atn`, `_base`, `_case1`, `_contin`,
  `_diag1`, `_diag2`, `_digits`, `_dump`, `_err`, …). Reproduced on
  HEAD `2414a26` with no working-tree changes:
  `TEST_Negation_001` fails with `Expected:<succeed>. Actual:<failure>`
  on `~integer('a') :f(n) ; result = 'succeed' :(end) ; n result = 'failure'`,
  meaning `~` does not flip Failure from a prior `integer('a')` call
  — which is consistent with the `CallFunc`-skip-to-Finalize handler
  unconditionally bypassing the `~` predicate when the inner function
  set `Failure=true`.

  **Recommendation for next session.** Decide between two
  starting points:
  1. **Fix the predicate-handling regression first.** If `~`, `?`,
     `LT`, `GT`, `NE`, etc. are not flipping `Failure` correctly when
     called as predicates after a failing function call, that bug is
     upstream of the beauty self-host. Beauty contains ~1000 such
     predicate uses; without correct predicate semantics, no part of
     S-2-bridge-7+ is meaningful. The `CallFunc`-skip-to-Finalize
     handler likely needs to NOT skip when the next opcode is a
     predicate operator (`OpNegation`, `OpInterrogation`, `OpTilde`,
     `OpQuestion`).
  2. **Diagnose the `&FULLSCAN = 1` Parse Error directly** with a
     minimal-input repro (`echo '&FULLSCAN = 1\nEND\n' | dotnet …
     beauty.sno`) — the existing self-host gate is a 25-line
     reduction already; trace what beauty's parser does with that
     keyword assignment under dot vs spl.

  Both root-cause investigations should precede any further bridge
  fire-point work; the bridge can only advance as fast as the
  underlying runtime is correct.

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
