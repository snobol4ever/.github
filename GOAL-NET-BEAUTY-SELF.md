# GOAL-NET-BEAUTY-SELF — snobol4dotnet Beauty Self-Hosting

**Repo:** snobol4dotnet
**Depends on:** GOAL-NET-BEAUTY-19 must be complete (19/19)
**Done when:** `dotnet Snobol4.dll -bf beauty.sno < beauty.sno` runs to
completion with exit 0, produces ≥500 lines of beautified output, and
emits no `error ` lines on stderr — matching the SPITBOL `-bf` baseline.

## ⛔ Read this first — every session

1. **Source location:** `/home/claude/corpus/programs/snobol4/demo/beauty/`
   contains `beauty.sno` and **all 19** of its `.inc` files in **one
   folder** — including `is.inc`, `FENCE.inc`, and `io.inc` which are also
   carried verbatim from `programs/include/`. The folder is intentionally
   self-contained: it runs from a single CWD with no `-I` / `SETL4PATH` /
   `SNO_LIB` flag on any runtime. See RULES.md "No duplicate corpus
   source files → Exception — self-contained demo programs" for the
   duplication policy. If `programs/include/{is,FENCE,io}.inc` ever
   changes, the copies in `demo/beauty/` must be updated in the same
   commit (byte-diff check).
   Do **not** use `/home/claude/corpus/programs/snobol4/demo/beauty.sno`
   (that one uses `-INCLUDE 'global.sno'` and lives next to demo siblings,
   not its includes — different program).

2. **Invocation flag is `-bf` (not `-b`).**
   beauty.sno relies on **case-sensitive labels** — `shift` vs `Shift`,
   `reduce` vs `Reduce`, `pop` vs `Pop`, etc. — to wire the parser's
   semantic-action callbacks. With `-b` (default fold-to-upper) those
   pairs collide as duplicate labels or the callbacks misroute silently.
   SPITBOL `-bf` is the canonical run.

3. **PASS criterion is "runs cleanly", not byte-identical.**
   Even SPITBOL's own self-host output drifts ~19 lines from the input
   (semicolon comments, whitespace alignment). Convergence is a future
   goal; this goal stops at "runs end-to-end without errors".

4. **Do not grep stdout for "Parse Error" or "Internal Error"** to
   detect failure — those strings appear in beauty.sno's own source as
   user-printed messages (`mainErr1`, `mainErr2`). A correct run echoes
   them. Detect failure via exit code + line count + stderr-clean.

5. **OUTPUT goes to stderr in snobol4dotnet** (per `REPO-snobol4dotnet.md`),
   but to stdout in SPITBOL/CSNOBOL4. The gate for snobol4dotnet must
   measure stderr (after filtering the dotnet exception trace prefix).

## Canonical oracle invocations

The folder is self-contained — no path flags needed for any runtime.

```bash
cd /home/claude/corpus/programs/snobol4/demo/beauty

# SPITBOL x64 — primary oracle
/home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno

# CSNOBOL4 — secondary oracle
/home/claude/csnobol4/snobol4 -bf -P 64k -S 64k beauty.sno < beauty.sno

# snobol4dotnet — the runtime under test
dotnet /home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll \
    -bf beauty.sno < beauty.sno
```

## What this means

beauty.sno is a SNOBOL4 beautifier. A beautifier is idempotent on
already-beautified source — feeding beauty.sno to itself should produce
beauty.sno unchanged. SPITBOL's own output is not byte-identical due to
minor formatting drift (it is a future goal to converge), so the
**self-host gate is "runs to completion with exit 0 and produces
non-empty beautified output"**, matching what SPITBOL `-bf` does today.

## Test command

snobol4dotnet sends `OUTPUT` to stderr (per `REPO-snobol4dotnet.md`),
so the beautified self-host result lands on stderr — not stdout. The
gate counts stderr lines (after filtering the dotnet exception trace
prefix) and confirms no compile-time error markers appear. SPITBOL,
by contrast, sends OUTPUT to stdout — both are correct for their
runtimes. The gate below works for snobol4dotnet specifically.

```bash
export PATH=/usr/local/dotnet10:$PATH
SNO4=/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
cd $BEAUTY
dotnet $SNO4 -bf beauty.sno < beauty.sno \
    > /tmp/beauty_self_out.txt 2>/tmp/beauty_self_err.txt
RC=$?
# Strip dotnet runtime crash prefix lines if any. Real OUTPUT is on stderr.
grep -v "^Unhandled\|^ at \|^Aborted" /tmp/beauty_self_err.txt \
    > /tmp/beauty_self_clean.txt
LINES=$(wc -l < /tmp/beauty_self_clean.txt)
echo "exit=$RC stderr-lines=$LINES"
# PASS: clean exit, plenty of beautified output, no compiler error markers,
#       and no Parse Error/Internal Error from beauty's mainErr paths.
[ $RC -eq 0 ] && [ $LINES -gt 500 ] \
    && ! grep -qE "error [0-9]+ --" /tmp/beauty_self_clean.txt \
    && ! grep -q "^Parse Error$\|^Internal Error$" /tmp/beauty_self_clean.txt \
    && echo "SELF-HOST PASS" || echo "SELF-HOST FAIL"
```

### Oracle baselines (re-verified Sun Apr 26 2026, x64 build, self-contained folder)

`demo/beauty/` is now self-contained: `is.inc`, `FENCE.inc`, `io.inc` are
present alongside the other 16 includes, so every runtime is invoked
with bare `beauty.sno` from CWD — no `SETL4PATH`, no `-I` flags.

| Oracle | Invocation | Result on this clone |
|--------|------------|----------------------|
| SPITBOL  | `sbl -bf beauty.sno < beauty.sno` | exit 0, 649 stdout lines, stderr clean — **PASS** ✅ |
| CSNOBOL4 | `snobol4 -bf -P 64k -S 64k beauty.sno < beauty.sno` | exit 1, 32 stdout lines, `beauty.sno:616: Caught signal 11 in statement 1074 at level 0` — **segfault** |
| snobol4dotnet | `dotnet Snobol4.dll -bf beauty.sno < beauty.sno` | exit 0, 31 stderr lines, `Parse Error` on `&FULLSCAN = 1` — **current S-2 bug** |

**SPITBOL is the canonical oracle for this gate.**

CSNOBOL4 segfault discrepancy: another session reports CSNOBOL4 self-hosts
cleanly with the same invocation. On this clone (csnobol4 HEAD `b3aeb9f`,
binary built fresh) it segfaults at stmt 1074. Could be platform-specific
(stack guards, signal handling, libc differences). Not investigated; not
a blocker for this goal — snobol4dotnet must match SPITBOL.

## NEW APPROACH (Mon Apr 27 2026) — 3-way binary sync-step monitor

Prior diagnosis sessions (preserved in detail below) chased S-2 by
hand-instrumenting `Shift`/`Reduce`/`Push`/`Inc`/`Pop` callbacks in a
copy of `demo/beauty/` and reading the trace.  Per RULES.md *"Sync-step
monitor — read the divergence point, not the trace"*, that approach is
deprecated.  The canonical workflow is now: drive csn + spl + dot
through the runtime-agnostic 3-way harness in one4all, let the
controller stop at first DIVERGE, and read **only** the last-agreed
+ first-disagreed wire-record pair.

The `csn` and `spl` bridges already fire on the chokepoint events
required for sync stepping (assignment, `.`-capture commit, user-fn
CALL/RETURN) — landed in csnobol4 `ad993fe` and x64 `3cd2dcc` under
SN-26-bridge-coverage-a/b in GOAL-LANG-SNOBOL4.  The wire format
(`one4all/scripts/monitor/monitor_wire.h`) and the controller
(`monitor_sync_bin.py`) are runtime-agnostic — they compare records
byte-for-byte across an arbitrary participant set identified by a
4-part `NAME:READY:GO:NAMES` spec.

**Active S-2 sub-rungs (this is the work; the speculative hypotheses
below remain as session history but are no longer the primary lens):**

- [x] **S-2-bridge-1 — DotNet IPC bridge, standalone smoke** (CLOSED 2026-04-27, snobol4dotnet @ `ba18e88`)
  Implemented `Snobol4.Common/Runtime/Monitor/MonitorIpc.cs` (~330 lines)
  with three public static entry points: `EmitValue(string name, Var value)`,
  `EmitCall(string fnName)`, `EmitReturn(string fnName, string rtnType)`.
  Lazy init reads `MONITOR_READY_PIPE`/`MONITOR_GO_PIPE`/`MONITOR_NAMES_OUT`
  on first emit; if `READY_PIPE` is absent or FIFO open() fails, all entry
  points become a single boolean check (`Enabled` getter) — zero overhead
  on normal beauty 17/17 runs.

  When fully activated: opens FIFOs (write-end ready, read-end go),
  emits 13-byte LE-packed headers + optional typed value bytes per
  `monitor_wire.h`.  Auto-interns lvalue/fn names; dumps names sidecar
  at `ProcessExit`.  Anonymous lvalues (array elements, table slots)
  intern the sentinel `<lval>` via `LooksLikeIdentifier` — mirrors csn
  `lvalue_name_id()` discipline.  Type discrimination via `switch (v)`:
  `StringVar`/`IntegerVar`/`RealVar` carry typed value bytes;
  `NameVar` carries `Pointer`; pattern/expression/array/table/code/data
  vars emit empty value (consistent with csn).

  **Smoke gate `scripts/test_smoke_dot_bridge.sh` PASS=5 FAIL=0:**
    - Build clean.
    - Beauty driver runs no-env: exit 0.
    - With `MONITOR_BIN=1` only (FIFOs absent): byte-identical to
      baseline on stdout AND stderr.
    - With non-existent FIFO paths: byte-identical to baseline.
    - Confirms zero side effects on hot path when monitor is off.

  Beauty 17/17 baseline preserved before-and-after.

  **Live-FIFO end-to-end smoke deferred to S-2-bridge-2** — until a
  fire-point is wired into the runtime, no `.sno` program can trigger
  the bridge.  S-2-bridge-2 will exercise `EmitValue` from the
  assignment chokepoint with `S='hello'\nEND\n` → 1 VALUE + END wire
  records, byte-comparable against csn-bridge-a's hello probe.

- [x] **S-2-bridge-2 — Fire-point: assignment chokepoint** (CLOSED 2026-04-27, snobol4dotnet @ `7b67cb0`)
  Hooked `MonitorIpc.EmitValue` from `Executive.Assign` in
  `Snobol4.Common/Runtime/Functions/OperatorsBinary/AssignReplace (=).cs`
  — the canonical chokepoint through which all `=` lvalue stores funnel.
  Two fire-points landed (one per early-return path):
  1. Right after `KeywordTable` handler invocation (~line 110) for
     keyword assignments like `&FULLSCAN = 1`.  Mirrors csn ASGNVV
     path for keyword stores.
  2. After the `switch (leftVar.Collection)` (~line 172), before the
     OutputChannel side-effect block, covering scalar IdentifierTable
     writes + ArrayVar element stores + TableVar slot stores in one
     place.

  Lvalue name extraction:
  - Scalar:        `stored.Symbol`  (e.g. `S` for `S = 'hello'`)
  - Array element: empty → `<lval>` sentinel via `LvalueNameId`
  - Table slot:    empty → `<lval>` sentinel via `LvalueNameId`
  - Keyword:       `leftVar.Symbol` (e.g. `&fullscan`)

  Mirrors csn `ASGNVV` (v311.sil:5938) and spl `asign:asg01`
  (sbl.min:17596) as the structural anchor.

  **Sidecar byte-format fix** also landed: `StreamWriter` forced to
  no-BOM UTF-8 (`UTF8Encoding(emitIdentifier:false)`); `NewLine`
  forced to `\n` so Windows runs produce LF-terminated sidecar
  identical to csn/spl on Linux.  Cross-runtime byte comparison
  of `names.txt` now works.

  **Live hello probe `S = 'hello' / END` produces exactly:**
  ```
  #0  kind=VALUE name_id=0 STRING(5)=b'hello'
  #1  kind=END   name_id=0xffffffff NULL(empty)
  names sidecar bytes: 53 0a   (i.e. 'S' '\n', no BOM)
  ```

  **Smoke gates:**
  - `scripts/test_smoke_dot_bridge.sh`        PASS=5 FAIL=0 (dormancy)
  - `scripts/test_smoke_dot_bridge_value.sh`  PASS=5 FAIL=0 (live FIFO)

  Beauty 17/17 baseline preserved.

- [x] **S-2-bridge-3 — Fire-point: `.`-capture commit + element stores** (CLOSED 2026-04-27, snobol4dotnet @ `18a2946`)
  **Discovery:** no new fire-point needed.  snobol4dotnet's
  pattern-match commit walks `BetaStack` and calls `Executive.Assign()`
  per `nameListEntry` — see line 58 of
  `Runtime/Functions/OperatorsBinary/PatternMatch (Question Mark).cs`.
  This routes `.`-capture (CVA1/CVA2 commit) and `$`-capture through
  the same `Executive.Assign` chokepoint as plain `=` stores.

  Consequence: S-2-bridge-2's single fire-point already covers all
  five csn fire sites in one stroke:
  - csn `ASGNVV`  → dot `Assign` default branch (scalar IdentifierTable)
  - csn `NMD4`    → dot `Assign` via `PatternMatch` BetaStack walk (`.`-cap)
  - csn `ENMI3`   → dot `Assign` via `PatternMatch` BetaStack walk (`$`-cap)
  - csn `ATP`     → dot `Assign` via `PatternMatch` BetaStack walk (`@`-pos)
  - csn array/table element store → dot `Assign` `Collection` switch

  The `<lval>` sentinel discipline (printable-ASCII heuristic in
  `LvalueNameId`) handles array element + table slot stores cleanly —
  both produce `<lval>` in the names sidecar at the same id (interning
  correctly deduplicates).

  **Smoke gate `scripts/test_smoke_dot_bridge_complex.sh` PASS=9 FAIL=0**
  (mirrors csn-bridge-c `probe_complex.sno` minus user-fn calls):
  ```
  myname = 'unset'              -> #0 VALUE name_id=0 STRING(5) 'unset'
  S = 'AXBYC'                   -> #1 VALUE name_id=1 STRING(5) 'AXBYC'
  S ANY('AB') . dotcap          -> #2 VALUE name_id=2 STRING(1) 'A'
  S2 = 'AXBYC'                  -> #3 VALUE name_id=3 STRING(5) 'AXBYC'
  S2 ANY('AB') $ dolcap         -> #4 VALUE name_id=4 STRING(1) 'A'
  a = ARRAY('1:3')              -> #5 VALUE name_id=5 ARRAY  empty
  a<2> = 'array_elem'           -> #6 VALUE name_id=6 STRING(10) 'array_elem'
  d = TABLE()                   -> #7 VALUE name_id=7 TABLE  empty
  d<'mykey'> = 'tbl_elem'       -> #8 VALUE name_id=6 STRING(8) 'tbl_elem'
  END                           -> #9 END   name_id=0xffffffff
  ```
  Names sidecar: `S\ndotcap\nS2\ndolcap\na\n<lval>\nd\n` (LF-terminated, no BOM).

  Beauty 17/17 baseline preserved.

- [x] **S-2-bridge-4 — Fire-point: CALL + RETURN on user-defined fns** (CLOSED 2026-04-27, snobol4dotnet @ `e5b4f05`)
  Hook entry/exit of user-defined functions in
  `Define.cs ExecuteProgramDefinedFunction`.  Three fire-points landed:
    - `MonitorIpc.EmitCall(functionName)` after `AmpFunctionLevel++`,
      before `ExecuteLoop` — mirrors csn `DEFF18` / spl `bpf09` predecessor.
    - `MonitorIpc.EmitValue(returnVarName, returnVar)` after the `nextIndex`
      switch, before `SystemStack.Push` — emits the return-slot VALUE record
      so the wire sees VALUE-then-RETURN, matching csn `DEFF20` discipline.
    - `MonitorIpc.EmitReturn(functionName, rtnTypeStr)` immediately after,
      carrying `RETURN` / `FRETURN` / `NRETURN` as a NAME-typed value.

  Builtin bypass path (early return before `UserFunctionTable.ContainsKey`
  guard) is unaffected — fire-points only reach live user-DEFINE'd
  functions.  No additional flag check needed; the existing dispatch
  structure does the filtering.

  rtnType promoted to local `rtnTypeStr` so the switch produces a single
  string consumed by both `AmpReturnType` and `EmitReturn`.

  Validation probe (probe.sno):
  ```
          DEFINE('SQR(N)')                         :(SQR_END)
  SQR     SQR = N * N                              :(RETURN)
  SQR_END
          S = 'hello world'
          S 'world' = 'there'
          N = SQR(7)
  END
  ```
  Wire (8 records, mirrors csn-bridge-b plus the bridge-2/4 split):
    #0 VALUE  S    STRING(11)='hello world'   (Assign chokepoint)
    #1 VALUE  S    STRING(11)='hello there'   (Assign chokepoint, replacement)
    #2 CALL   SQR                              (bridge-4 EmitCall)
    #3 VALUE  SQR  INTEGER(49)                 (Assign chokepoint inside body)
    #4 VALUE  SQR  INTEGER(49)                 (bridge-4 EmitValue, return slot)
    #5 RETURN SQR  STRING(6)='RETURN'          (bridge-4 EmitReturn)
    #6 VALUE  N    INTEGER(49)                 (Assign chokepoint, callsite)
    #7 END
  Names sidecar: S\nSQR\nN\n (LF-terminated, no BOM).

  **Smoke gate `scripts/test_smoke_dot_bridge_call.sh` PASS=7 FAIL=0:**
    - dot exit clean
    - CALL record present
    - RETURN record present with correct type marker
    - VALUE INTEGER(49) record present
    - END record present
    - CALL precedes RETURN (ordering)
    - Names sidecar contains S, SQR, N

  **Gates after S-2-bridge-4:**
    - `test_smoke_dot_bridge.sh`         PASS=5 FAIL=0 (dormancy)
    - `test_smoke_dot_bridge_value.sh`   PASS=5 FAIL=0 (live FIFO, VALUE)
    - `test_smoke_dot_bridge_complex.sh` PASS=9 FAIL=0 (5-LHS-form coverage)
    - `test_smoke_dot_bridge_call.sh`    PASS=7 FAIL=0 (CALL+RETURN)
    - Beauty 17/17 PASS

- [x] **S-2-bridge-5 — Harness lane: `dot` participant** (CLOSED 2026-04-27, one4all @ `76d979a7`)
  Edited `one4all/scripts/test_monitor_3way_sync_step_auto.sh`:
    - Added `dot` to recognized PARTICIPANTS set + `want_dot` flag.
    - Added `SNO4_REPO` + `SNO4_DLL` env vars (defaults to
      `/home/claude/snobol4dotnet/Snobol4/bin/Release/net10.0/Snobol4.dll`).
    - Added prerequisite checks: `dotnet` command available + dll built.
    - Added launch block with monitor env vars, `< $STDIN_SRC`, timeout,
      and `-bf` for case-sensitive identifiers (matches csn/spl).
    - Usage docstring updated with dot example.
  Default PARTICIPANTS unchanged (`csn spl scr`).

  **Validation per goal spec:**
  ```
  PARTICIPANTS="dot" bash test_monitor_3way_sync_step_auto.sh /tmp/probe.sno
  ```
  Probe: `DEFINE('SQR(N)') + S='hello world' + S 'world'='there' + N=SQR(7)`.
  Result: `[ctrl] all reached END after 7 steps`, exit 0.

  Beauty 17/17 PASS. All four dot bridge gates green
  (PASS=5/5/9/7 across dormancy / value / complex / call).

- [x] **S-2-bridge-5b — dot adopts SN-26-bridge-coverage-e/f** (CLOSED 2026-04-27, snobol4dotnet @ `8e5ff9e`, one4all @ `21eac9a5`)
  Brings snobol4dotnet up to the post-coverage-e/f wire protocol that
  csn/spl/scrip adopted in session #34/#35 — required for byte-comparable
  3-way runs in S-2-bridge-6.

  **coverage-e (streaming intern):**
    - `MonitorIpc.InternName()` emits `MWK_NAME_DEF` (kind=6) inline when
      a fresh id is assigned, BEFORE any record using that id flows.
    - `FlushNamesSidecar` and `MONITOR_NAMES_OUT` env-var read removed.
    - Harness `dot` launch block drops `MONITOR_NAMES_OUT="$TMP/dot.names"`.

  **coverage-f (MWK_LABEL):**
    - New `MonitorIpc.EmitLabel(long stno)` public entry point.
      Wire shape: kind=`MWK_LABEL`(5), name_id=NONE, type=INTEGER, 8-byte LE.
    - Hooked from all three statement-entry paths:
      `Executive.InitializeStatement`, `Executive.InitStatementMsil`,
      `OpCode.Init` in `ThreadedExecuteLoop`.
    - Wire payload: 1-based statement number (`stmtIdx + 1`) — matches
      scrip's `++stno` and oracle STNOCL/kvstn semantics.

  **Smoke gates updated for new wire shape:**
    - `test_smoke_dot_bridge.sh`         PASS=5 (dormancy unchanged)
    - `test_smoke_dot_bridge_value.sh`   PASS=5 (now 4 records: LABEL VALUE LABEL END)
    - `test_smoke_dot_bridge_complex.sh` PASS=9 (now 20 records: 10 LABEL + 9 VALUE + 1 END)
    - `test_smoke_dot_bridge_call.sh`    PASS=7 (presence-only checks, still green)

  Beauty 17/17 PASS preserved.

  Standalone harness gate:
    `PARTICIPANTS=dot bash test_monitor_3way_sync_step_auto.sh /tmp/probe.sno`
    → `[ctrl] all reached END after 14 steps`, exit 0.

- [~] **S-2-bridge-6 — End-to-end: csn + spl + dot on beauty self-host** (IN PROGRESS 2026-04-27)
  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
  PARTICIPANTS="csn spl dot" \
      STDIN_SRC=$BEAUTY/beauty.sno \
      MONITOR_TIMEOUT=120 \
      bash /home/claude/one4all/scripts/test_monitor_3way_sync_step_auto.sh \
      $BEAUTY/beauty.sno
  ```

  **First divergence captured this session.** Two findings, in order
  of appearance on the wire:

  **(A) csn segfaults at global.inc:2** — 3-way harness reports
  `DIVERGE step 1` because csn emits `LABEL stno=2` while spl + dot
  both emit `LABEL stno=1`, AND csn stderr shows
  `global.inc:2: Caught signal 13 in statement 2 at level 0`.
  This is csn dying with SIGPIPE (signal 13 = broken pipe) early —
  not a dot issue.  Likely csn's bridge-e or bridge-f emit on
  global.inc:2 is racing the controller close, or csn's first
  LABEL counts comments/blanks differently from spl/dot.  Cross-ref
  SN-26-bridge-coverage-i (csn FENCE bug) — that may be related.

  **(B) Real dot vs spl divergence at step 26** (2-way `spl dot`,
  csn excluded):
    - Records #000–024 byte-identical between spl and dot.
    - **#025**: spl emits `LABEL stno=15`, dot emits `LABEL stno=14`
      (off-by-one in stmt numbering).
    - **#028**: spl emits `VALUE STRING(128)` of raw bytes 0x80–0xff
      (Latin-1, 128 bytes); dot emits `VALUE STRING(256)` of UTF-8
      encoded bytes (0xc2 0x80 .. 0xc3 0xbf, 256 bytes).

  **Diagnosis of (B-stno):** Beauty's source has 18 statements before
  the divergence point.  spl skips one stno number around the area —
  likely a CONTINUE or label-only line that spl excludes from `&STNO`
  but dot counts.  This matches the existing SN-26-bridge-coverage-f
  observation: "csn=3 LABELs, sbl=4, scrip ir-run=3, sm-run=4 —
  SPL counts END as a stmt".  Per-runtime LABEL count differences
  are documented; ordering on wire is what matters for divergence.
  Need to align dot's stno counting with one of the existing
  conventions (probably scrip's, since it's our own code).

  **Diagnosis of (B-utf8):** This is a real dot bridge bug.
  `MonitorIpc.ClassifyValue` for `StringVar` does
  `Encoding.UTF8.GetBytes(sv.Data)`.  But SPITBOL stores raw bytes
  in StringVar; dot's StringVar.Data is a C# `string` (UTF-16),
  which when UTF-8-encoded doubles the length of any non-ASCII char.
  The 128-byte STRING #028 in beauty (Latin-1 chars 0x80–0xff,
  the second half of `&UCASE`/`&LCASE` complement set) becomes
  256 bytes on dot's wire.

  **Fix path for (B-utf8):** snobol4dotnet's StringVar should be
  treated as a byte-buffer, not Unicode text, for monitor emit.
  Options:
    1. ClassifyValue iterates `sv.Data` as chars and writes each
       low byte (`(byte)(c & 0xff)`) — assumes StringVar holds
       Latin-1 in the C# string.
    2. Use ISO-8859-1 encoding: `Encoding.Latin1.GetBytes(sv.Data)`.
       Cleaner if StringVar's contract is "8-bit clean bytes
       smuggled into a C# string".
  Need to confirm the snobol4dotnet StringVar contract — see
  `Snobol4.Common/Runtime/Variable/StringVar/StringVar.cs`.

  **Open work (next session):**
    - [x] Fix dot's STRING byte encoding in `MonitorIpc.ClassifyValue`
      — landed Mon Apr 28 2026 (snobol4dotnet `28625e1`).
      `Encoding.UTF8.GetBytes` → `Encoding.Latin1.GetBytes`
      for the `StringVar` arm.  Smoke test
      `scripts/test_smoke_dot_bridge_latin1.sh` PASS=3 verifies
      `S = CHAR(128) CHAR(129)` emits STRING(2)=b'\\x80\\x81' on the
      wire (not STRING(4)=b'\\xc2\\x80\\xc2\\x81').
    - [x] Align dot's LABEL stno with SPITBOL `&STNO` convention
      — landed Mon Apr 28 2026 (snobol4dotnet `42c1ef7`).
      SPITBOL counts blank lines as consuming an stno slot (the
      compiler assigns them slots; runtime skips emit).  Pre-fix dot
      only counted executable SourceLines.  Fix: at the three
      `EmitLabel` call sites (`MsilHelpers.InitStatementMsil`,
      `ThreadedExecuteLoop OpCode.Init`, `InitializeFinalize.InitializeStatement`),
      look up the per-SourceLine running `BlankLineCount` (already
      captured at parse time in `SourceCode.ProcessSubLine`) and
      add it to the wire stno.  Verified byte-identical to spl on
      beauty.sno records #022–#035.  New smoke gate
      `scripts/test_smoke_dot_bridge_stno.sh` PASS=6.
    - [ ] Investigate csn SIGPIPE early death (B-A) — possibly a csn
      bridge-coverage fix.
    - After both: re-run `csn spl dot` 3-way and confirm DIVERGE
      moves further into beauty's run.

  Beauty 17/17 still PASS.  All six dot bridge gates green
  (PASS=5 dormancy, 5 value, 9 complex, 7 call, 3 latin1, 6 stno).

  **Mon Apr 28 2026 — first 2-way `spl dot` run after both fixes.**
  With the encoding (28625e1) and stno (42c1ef7) fixes both landed,
  re-ran `PARTICIPANTS="spl dot"` against beauty self-host.  Result:

  ```
  [ctrl] DIVERGE step 47
    spl: VALUE UTF = UNKNOWN
    dot: VALUE UTF = TABLE
  ```

  47 wire records of byte-identical agreement, then divergence on
  the type tag of `UTF = TABLE()` (global.inc:27).  This is **not a
  snobol4dotnet bug** — it is a documented gap in SPITBOL's bridge:

  ```c
  // x64/osint/monitor_ipc_runtime.c spl_block_to_wire (line 279):
  /* No public extern for nmblk, ptblk, atblk, tbblk, cdblk, efblk —
   * report UNKNOWN so the wire still records *something*.  Future
   * work: export their b_xxx symbols or compare via TYPE_XNT/XRT. */
  return MWT_UNKNOWN;
  ```

  spl emits MWT_UNKNOWN(=255) for **every** aggregate type (table,
  array, pattern, name, code, expression, file).  dot emits the
  correct typed kind (MWT_TABLE=8 here).  The name (`UTF`) and
  empty value bytes match — only the type byte differs.

  This is a SPITBOL bridge coverage gap, not a snobol4dotnet runtime
  bug.  The fix belongs in x64/osint/monitor_ipc_runtime.c +
  x64/osint/osint.h: extend the TYPE_* extern table with TYPE_NMB /
  TYPE_PAT / TYPE_AT / TYPE_TB / TYPE_CD / TYPE_EF (or equivalent
  via TYPE_XNT/XRT pattern) and discriminate in spl_block_to_wire.
  Cross-reference: SN-26-bridge-coverage in GOAL-LANG-SNOBOL4 — it
  is the home for x64/csn bridge improvements.

  **Csn parity check (also done this session):** `PARTICIPANTS="csn dot"`
  on the same input diverges at step 1: csn emits LABEL stno=2 (skipping
  the START label-only line) then SIGPIPEs at global.inc:2.  Both are
  csnobol4 issues; not snobol4dotnet.

  **Recommended sequencing:** S-2-bridge-7's iterative loop ("read
  divergence pair, fix dot runtime, advance") cannot start cleanly on
  the wire until the spl bridge covers aggregates — otherwise every
  aggregate creation in beauty (~dozen TABLE() and ARRAY() calls in
  global.inc alone) trips a spurious DIVERGE before any real dot bug.
  Either (a) wait for SN-26-bridge-coverage to extend spl's
  spl_block_to_wire, or (b) make the controller treat MWT_UNKNOWN as a
  wildcard (compare succeeds when either side is UNKNOWN).  Option (a)
  is the right long-term answer; option (b) is a one-line controller
  patch in monitor_sync_bin.py event_key.

- [ ] **S-2-bridge-7 — Fix the runtime gap, advance to next divergence**
  With the canonical divergence pair in hand, fix the snobol4dotnet
  runtime at the appropriate site (`Scanner.cs` Match, `Builder.cs`
  BuildEval, `UnevaluatedPattern.cs` Scan, `ConditionalVariableAssociationPattern.cs`,
  `ArbNoPattern.cs` — depending on what the wire reveals).  Re-run
  S-2-bridge-6.  Repeat until exit 0 and ≥500 stderr lines.

**Why this supersedes the speculative path.** The session log below
documents *six* distinct hypotheses for S-2 root cause, several of
which were definitively invalidated by isolated probes:
- ARBNO + nested-* with cursor callbacks: **not the bug** (verified
  with v6 repro).
- "2-arg DEFINE breaks pattern callbacks": **not the bug** (verified;
  was an `AmpCaseFolding` artifact, fixed in `13bfcc0`).
- Graft on multi-element concat: **not the bug** (4-element repro
  passes byte-identical to SPITBOL).
- ExpressionVar deferred eval in numeric context: **was a contributing
  bug**, fixed in `0914fbf`; not the residual.
- Callbacks re-fire on backtrack: **partially confirmed** by `probe4`
  but only in a malformed-NRETURN edge case; doesn't reproduce on
  well-formed callbacks.

Each hypothesis cost a session.  The 3-way binary monitor short-circuits
this: instead of building a probe to *prove* a hypothesis, the wire
shows the divergence directly.  Whatever the root cause is, it manifests
as a specific record at a specific step — and the fix site follows
from the record kind and name.

**Gates after every sub-rung:**
- snobol4dotnet beauty 17/17 still green.
- snobol4dotnet unit tests still green (baseline 2375p/0f/2s).
- `test_smoke_dot_bridge.sh` PASS=1 (after S-2-bridge-1).
- one4all existing bridge smokes unchanged: `test_smoke_sn26_csn_bridge_a.sh`,
  `_b.sh`, `_c.sh`, `test_smoke_sn26_spl_bridge.sh`,
  `test_smoke_sn26_spl_bridge_d.sh`, `test_smoke_sn26_auto_binary.sh`.

**Estimated session count for S-2-bridge-1..7:** 3-4 sessions.
S-2-bridge-1+2 in one (scaffolding + first fire-point);
S-2-bridge-3+4 in another (remaining fire-points);
S-2-bridge-5+6 in a third (harness wiring + first divergence);
S-2-bridge-7 is iterative — one fix per session until self-host PASS.

---

## Current diagnosis (supersedes all prior notes below)

**Sun Apr 26 2026, evening session 2 — diagnosis sharpened, pivot to confidence demos.**

S-2 root cause investigation this session:

- Prior session's "callbacks re-fire on backtrack" hypothesis was tested
  with isolated probes and **does not reproduce**. Both runtimes agree
  on ARBNO + alternation + nested cursor callbacks when the callback
  function returns `epsilon`. The `'ABB'` divergence in prior probe4 was
  a misformed test (`addg` returning NRETURN with no value).
- Real divergence captured by instrumenting `Shift`/`Reduce`/`Push`/`Inc`/`Pop`
  in a working copy of `demo/beauty/` (in `/tmp/bi/`, **not** modifying
  corpus per RULES.md):
  - Input `START\n` (works on both) — traces are byte-identical, all 6
    epsilon Shifts + 2 Reduces fire in the same order.
  - Input `              x = 1\n` — SPITBOL fires 7 Shifts + 2 Reduces in
    cursor order; snobol4dotnet fires only 3 Shifts + 2 Reduces, in
    REVERSE order, with `Reduce(snoParse, )` getting empty `n` because
    the counter stack is empty when nTop() is called.
- Architectural cause now clear: snobol4dotnet's `pat . *fn(args)` is
  implemented by stashing `*fn(args)` as an `ExpressionVar` Assignee in
  `ConditionalVariableAssociation1.Scan` (`AlphaStack.Push`), promoting
  to BetaStack at CVA2, and **only evaluating the ExpressionVar (calling
  fn) AFTER the entire pattern match succeeds**, in
  `PatternMatch (?).cs` line 50 (`foreach (BetaStack.Reverse())`). SPITBOL
  evaluates `*fn(args)` AT MATCH-CURSOR-CROSS time inside CVA2 — so
  side effects fire in match order and intermediate failures (NRETURN)
  fail the local match.
- Attempted fix: move ExpressionVar evaluation into `CVA2.Scan` in
  `ConditionalVariableAssociationPattern.cs`. Build clean, beauty 17/17
  preserved, but self-host hits `InvalidOperationException: Stack empty`
  — fix needs to handle `MsilHelpers.CallFuncBySlot` line 75
  SystemStack-unwind on Failure (NRETURN/FRETURN). Reverted; the fix
  direction is right but needs a SystemStack-water-mark guard. Recommend
  resuming after the demo-confidence steps below.

**Pivot rationale.** S-2 is a deep architectural fix touching pattern
matching semantics. Before continuing the runtime work, ensure
snobol4dotnet handles three known-good corpus demos cleanly:

| Demo | Status today | New step |
|------|-------------|----------|
| `claws5.sno` | error 235 — multi-level TABLE subscript fails | S-2a |
| `treebank-list.sno` | runs cleanly, output structurally matches SPITBOL; only `.ref` is stale | S-2b |
| `treebank-array.sno` | runs cleanly but output is empty `''`s (likely same root cause as S-2a) | S-2c |

Two of the three (S-2a, S-2c) likely share a root cause in
multi-level subscripted assignment. That is potentially a smaller fix
than the cursor-callback architecture in S-2, and a green status on
all three would establish a confidence baseline before tackling S-2's
deeper graft + commit-time-vs-cursor-time semantic.

**Sun Apr 26 2026, late session — infrastructure update.** `demo/beauty/`
is now self-contained: `is.inc`, `FENCE.inc`, `io.inc` carried verbatim
from `programs/include/`, alongside the existing 16 includes (19 total).
Every runtime now self-hosts from CWD with no path flags; SPITBOL,
CSNOBOL4, and snobol4dotnet all use the same bare `beauty.sno` invocation.
The previously-flagged side-task "add `-I` include-path support to
snobol4dotnet's CommandLine.cs" is **no longer required** for this goal —
the duplication policy carve-out (RULES.md "Exception — self-contained
demo programs") supersedes it. Note: in older session entries below,
references to copying inc files into `demo/beauty/` and to the proposed
`-I` flag are now historical only.

**Sun Apr 26 2026, evening.** Three runtime fixes landed in
snobol4dotnet @ `0914fbf` that unblock the deferred-expression path
through user-defined functions.  Beauty 17/17 still PASS.  Self-host
no longer raises any `error 109 -- ge first argument is not numeric`
(the prior-session blocker); it now reaches "Parse Error" on simple
assignments without any runtime exceptions in between.  The remaining
work is the parser pattern itself — the ARBNO(*Command) graft issue.

**Bugs fixed this session (snobol4dotnet @ 0914fbf):**

1. **Var.cs `ToNumeric`** — when the arg is an `ExpressionVar`, run its
   `DeferredCode`, pop the resulting top-of-stack value, then continue
   numeric extraction (recursing through NameVar resolution as needed).
   Mirrors SPITBOL semantics: a deferred `*(...)` evaluates on demand
   whenever a numeric value is needed.

2. **NumericComparisonHelper.cs `BinaryComparison`** — when `ToNumeric`
   returns false because the deferred expression itself failed
   (`Failure` already set), call `NonExceptionFailure()` rather than
   `LogRuntimeException(errorLeft/errorRight)`.  A failed `*(...)` in
   numeric-comparison position yields a SNOBOL match-failure, not a
   fatal "first/second argument is not numeric" error (errors 101–150).

3. **NumericHelper.cs `BinaryNumericOperation`** — same propagation
   rule for `+`, `-`, `*`, `/`, `^` (errors 1, 2, 12, 16, 26, 32).

**Verification:**
- Beauty 17/17 gate still PASS.
- Self-host: `error 109` (in ShiftReduce.inc and counter.inc) and
  `error 1` (addition in counter.inc) — all gone.  Output is now
  clean up to `Parse Error` on the first non-comment statement.
- Minimal Reduce-with-`*(GT(nTop(),1) nTop())` repro confirmed:
  evaluates correctly, no runtime exception.

**Remaining bug (the actual S-2 work) — Parse Error on assignment:**

```
$ cat > /tmp/tiny2.sno << 'EOF'
              x = 1
END
EOF
$ dotnet Snobol4.dll -bf beauty.sno < /tmp/tiny2.sno
Parse Error
              x = 1
```

`Parse = nPush() ARBNO(*Command) *Top()` only succeeds on input that
the grammar already accepts at zero-Commands (comment-only input,
label-only `START\n`).  Real statements (`x = 1\n`, `&FULLSCAN = 1\n`)
trip Parse Error.  No runtime errors fire — the pattern just fails.
This is the ARBNO(*Command) graft territory from prior sessions:
multiple sessions have noted that `'AB' POS(0) *Parse RPOS(0)` works
when `Parse = nPush() ARBNO(LEN(1))` (Graft fix landed) but fails
when the inner pattern is `*Command` — semantic actions inside the
ARBNO body don't fire and/or backtracking alternates are dropped.

**Likely fix sites for next session:**
1. `Snobol4.Common/Runtime/Pattern/ArbNoPattern.cs` — verify the Graft
   fix (826d4ff) applies correctly when inner is `*X` returning a
   pattern that itself contains `*Y` (nested star-expressions, which
   is what `*Command` ultimately expands to via the `&` OPSYN chain).
2. `Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs` — `Scan`
   uses `Graft` on the outer scanner.  When it grafts a pattern whose
   nodes themselves contain `*` references, those inner stars
   themselves Scan via the outer scanner — does that re-graft path
   preserve ARBNO's alternates?
3. Test target: a minimal `Parse = nPush() ARBNO(*X) *Top()` where
   `X = ('a' . *push) | ('b' . *push)` (i.e. *X picks tokens with
   semantic actions on each), feed it `'aab'`, expect 3 push calls.
   If that fails, the graft + ARBNO loop has the same root cause as
   beauty's Parse failure.

The runtime is now SPITBOL-compatible enough for deferred expressions
in numeric/comparison contexts; the pattern engine is the next layer.

---

## Prior diagnosis (superseded by above; preserved for history)

**Sun Apr 26 2026, late afternoon.** Three infrastructure bugs in
snobol4dotnet were fixed (CommandLine.cs concatenated boolean flags,
SourceCode.cs IsEndStatement uppercase END, MainConsole.cs debug print
removed); committed as `13bfcc0`.  After those fixes the program ran
end-to-end but tripped `mainErr1` (Parse Error).  See git log for
detail.

**Original repro that drove this session** — now passes after `0914fbf`:
the `*Shift` resolution failure was a symptom of `AmpCaseFolding`
default; that was already fixed in `13bfcc0`.


---

## Steps

- [x] **S-1** — Diagnose error 021 on beauty.sno self-input. Confirmed:
  - FENCE.sno deleted (CSNOBOL4 now has FENCE built-in; shim no longer needed)
  - io.sno fixed: OPSYN('INPUT','input_') guard added (SPITBOL rejects this with fatal error 248)
  - Beauty suite: dotnet 18/18, SPITBOL 15/18 (improved from 13/18)
  - Self-host infinite loop: snobol4dotnet loops; SPITBOL gets error 021 at stmt ~750
  - Root cause identified: nTop() uses RETURN (value return) but Parse pattern calls
    it via string evaluation ("'nTop()'" & ...) in a pattern context expecting NRETURN.
    ARBNO(*Command) also loops under snobol4dotnet — same root cause or related.
  - corpus HEAD: 0074bc5

- [x] **S-2a** — Confidence demo: `claws5.sno < claws5.input`. **DONE** (snobol4dotnet @ 8432b35).
  - Root cause: `IndexTable`/`IndexArray` deep-cloned every value read from
    a Table/Array slot, including stored Tables and Arrays.  Chained-
    subscript writes (`m['s']['w'] = 1`) modified the transient clone, never
    the inner stored aggregate.  SNOBOL4 spec requires reference semantics
    for aggregates; only scalars need cloning.
  - Fix (≈10 lines, two files):
    - `Snobol4.Common/Runtime/Functions/ArraysTables/Table.cs IndexTable`
    - `Snobol4.Common/Runtime/Functions/ArraysTables/Array.cs IndexArray`
    - When stored value `is ArrayVar or TableVar`, push as-is.  Otherwise
      clone (existing scalar aliasing protection unchanged).  Missing-key
      path in IndexTable still clones Fill (each empty slot independent).
  - Verification on this clone:
    - `claws5.sno < claws5.input` (tiny 16-line canonical input):
      exit 0, 95 stderr-clean lines, **byte-identical to `claws5.ref`**.
    - Beauty 17/17 still PASS.
    - Crosscheck smoke sweep over hello/output/assign/concat/data/
      keywords/strings/arith_new/control_new/patterns/capture/functions:
      128/129 PASS (the lone fail is the pre-existing `099_keyword_rw`
      noted in `REPO-snobol4dotnet.md`, unrelated).

- [x] **S-2b** — Confidence demo: `treebank-list.sno < treebank.input`. **DONE** (snobol4dotnet @ 8432b35).
  - The canonical input for this demo is the tiny `treebank.input`
    (4 sentences) — NOT the much larger `VBGinTASA.dat` used in earlier
    sessions.  `treebank-list.ref` is the 24-line reference for the
    tiny input and is **not** stale.
  - Same root cause as S-2a/S-2c (aggregate reference semantics);
    the IndexTable/IndexArray fix closes this demo too.
  - Verification on this clone:
    - `treebank-list.sno < treebank.input`: exit 0, 24 stderr-clean
      lines, **byte-identical to `treebank-list.ref`**.
    - SPITBOL `-bf` on the same input: byte-identical to the same ref.

- [x] **S-2c** — Confidence demo: `treebank-array.sno < treebank.input`. **DONE** (snobol4dotnet @ 8432b35).
  - Same root cause as S-2a (multi-level subscripted assignment via
    Array indexing).  Same fix (`IndexArray` reference-semantics for
    aggregates) closes both demos.
  - The canonical input is the tiny `treebank.input` (4 sentences);
    `treebank-array.ref` is the 24-line reference for that input.
  - Verification on this clone:
    - `treebank-array.sno < treebank.input`: exit 0, 24 stderr-clean
      lines, **byte-identical to `treebank-array.ref`**.
    - SPITBOL `-bf` on the same input: byte-identical to the same ref.

- [ ] **S-2** — Fix root cause: self-host Parse fails on label-only statements.
  FRETURN PROPAGATION — PARTIAL FIX (snobol4dotnet 80381fb, INCOMPLETE):
    Confirmed bug: FRETURN from user-defined function does not abort calling statement.
    Two fix sites identified and partially patched:
    (A) BuilderEmitMsil.cs: earlyExit label added; after CallFuncBySlot emits
        Failure check + Brtrue earlyExit; earlyExit marked before FinalizeStatementMsil.
    (B) ThreadedExecuteLoop.cs: CallFunc/CallFuncIndirect now scan to next Finalize
        when Failure=true.
    BLOCKER: When function defined via runtime DEFINE() (not compile-time visible),
    it is absent from FunctionSlotIndex. MSIL emitter R_PAREN_FUNCTION returns false
    -> statement falls back to threaded opcodes. But ThreadIsMsilOnly=true for whole
    program -> fast path runs -> threaded CallFunc fix never fires; MSIL fix also
    never fires (statement not cached). Test still fails.

  NEXT SESSION — two options to complete the fix:
    Option 1 (preferred): Fix MsilHelpers.cs CallFuncBySlot() — after entry.Handler()
      sets Failure=true, pop SystemStack back to StatementSeparator immediately.
      Fires regardless of MSIL vs threaded path. Then remove threaded scan-forward.
    Option 2: When R_PAREN_FUNCTION falls back, emit a CallMsil wrapper that calls
      the runtime function then checks Failure, keeping ThreadIsMsilOnly=true.

  After fix: run /tmp/test_step2.sno ('D after ffail' must NOT print),
  beauty 17/17, then self-host.
  ROOT CAUSE CONFIRMED (826d4ff): UnevaluatedPattern.Scan creates a child Scanner
  to match *X. ARBNO's backtracking alternates are saved in the child scanner's state,
  then discarded when the child returns its first success. The outer scanner can never
  backtrack into ARBNO for more iterations. Result: nPush() ARBNO(*Command) always
  matches only one Command; 'START\n' (label-only statement) causes Parse Error.

  Minimal repro confirmed:
    'AB' POS(0) *Parse RPOS(0) FAILS when Parse = nPush() ARBNO(LEN(1))
    'AB' POS(0)  Parse RPOS(0) PASSES (direct, no * indirection)

  SIDE WORK THIS SESSION (snobol4dotnet d4e523f, corpus 4c044d2):
    - FENCE(p) sealing bug fixed: new SealPattern + ScannerState.SealAlternates() (-2 sentinel)
    - Structure now: AlternatePattern(ConcatenatePattern(p, SealPattern()), AbortPattern())
    - 7 new corpus tests added: crosscheck/patterns/068-074 (*var and FENCE coverage)
    - 061_pat_fence_fn_seal now PASSES; all 12 FENCE corpus tests pass (058-069)
    - Fixed pre-existing wrong assertions in TEST_Fence_064/065
    - Pre-existing failures unchanged: 14 TEST_Csnobol4_* unit tests, 099_keyword_rw
    - ALSO FOUND: ARBNO(*fn()) crashes Stack empty in ConditionalVariableAssociationPattern
      (separate bug, same Graft fix needed)

  FIX APPROACH - Graft (826d4ff, INCOMPLETE):
    UnevaluatedPattern.Scan evaluates *X, grafts the result's nodes into the
    RUNNING scanner's AST (remapped indices, dangling Subsequent=-1 wired to the
    node following *X), returns GOTO so Match jumps inline. All alternates stay
    in one unified stack. MatchResult.cs + AbstractSyntaxTree.cs scaffolded.

  SESSION WORK (corpus fixes, io.sno removal):
    - Removed -INCLUDE 'io.sno' from demo/beauty.sno, demo/expression.sno, smoke/beauty_oracle.sno
    - Deleted beauty_io_driver.sno + .ref (tested io.sno only)
    - Fixed feat/f10_io_basic.sno, feat/f11_io_file.sno: 4-arg SNOBOL4+ -> 3-arg SPITBOL protocol
    - Fixed demo/beauty.sno + smoke/beauty_oracle.sno: output__/input__ -> OUTPUT/INPUT (3-arg)
      This eliminated the InvalidCastException crash in --auto two-pass mode
    - Graft scaffolding (Scanner.Graft, GOTO in Match loop, UnevaluatedPattern.Scan) already
      complete in code from prior session (826d4ff). Beauty suite: 17/17 (was 18/18 with io driver).
    - Self-host: crash gone; now truncates at ARBNO(*Command) — known S-2 graft bug remains.
    - corpus HEAD: 7d26569

  SESSION WORK (prior session — diagnosis only, no code changes):
    - Minimal repro 'AB' POS(0) *Parse RPOS(0) where Parse = nPush() ARBNO(LEN(1))
      now PASSES — Graft fix is working for that case.
    - Self-host still FAILS with new symptom: InvalidCastException PatternVar→ProgramDefinedDataVar
      in GetProgramDefinedDataField (Data.cs:206) when pp(sno) calls t(sno) and sno is a PatternVar.
    - Root cause fully diagnosed (see below).

  SESSION WORK (this session — diagnosis deeper, no code committed):
    - Confirmed crash site: t(Pop()) in pp(), sno = Pop() returns PatternVar not tree node.
    - Mini repro confirmed: minimal program with Label/Command/Parse/ARBNO reproduces the bug.
    - DumpStack() after match shows $'@S' is EMPTY — Shift never pushed any tree nodes.
    - Attempted Graft fix in ArbNoPattern.Scan (two variants): first caused infinite loop (wired
      graft end back to ARBNO node itself), second gave only 1 iteration. Both reverted.
    - ArbNoPattern.Scan currently uses child scanner (reScan = new Scanner(scan.Exec)) —
      Exec IS shared, so $'@S' globals are accessible; Shift should fire correctly in child.
    - New hypothesis: FRETURN propagation bug in nested function call args. When $'@S' = '',
      DIFFER($'@S') → DIFFER('','') → fails → FRETURN from Pop(). But DATATYPE(Pop()) in
      the OUTPUT statement still outputs 'pattern' instead of failing silently. This suggests
      snobol4dotnet does not correctly propagate FRETURN through nested function-call arguments.
    - ALSO: confirmed $'@S' is empty after match — meaning Shift() was never called at all.
      The semantic actions inside ARBNO(*Command) are not firing.
    - snobol4dotnet HEAD: 080e19c (unchanged)
    - corpus HEAD: 7d26569 (unchanged)
    - beauty suite: 17/17 confirmed at session start

  NEXT SESSION must investigate TWO things:
    A. Why Shift() is never called inside ARBNO(*Command). Add OUTPUT tracing directly into
       Shift_ body (not guarded by xTrace) to confirm whether Shift fires at all during the
       ARBNO match. If it doesn't fire, the *Label ~ 'Label' semantic action isn't executing —
       meaning UnevaluatedPattern inside the child scanner is not triggering semantic side-effects.
    B. FRETURN propagation: write a standalone test:
         DEFINE('ffail()', 'ffail_')
         ffail_  :(FRETURN)
         OUTPUT = 'before: ' DATATYPE(ffail())
         OUTPUT = 'should not print'
       If 'before: pattern' prints, there is a FRETURN propagation bug in output/function-arg
       context. Fix would be in the function-call evaluation path (MsilHelpers or Executive).
    C. If (A) shows Shift does fire but $'@S' is still empty, check if child scanner's Graft
       for *Shift(...) is failing silently (error 103 from re_ EVAL) rather than executing Shift.
    - snobol4dotnet HEAD: 080e19c (unchanged this session)
    - corpus HEAD: 7d26569 (unchanged this session)

  ROOT CAUSE (newly diagnosed):
    When *P is used where P holds a pattern built by reduce() (e.g. the ("'Parse'" & '...') term),
    the UnevaluatedPattern compiled for *P re-evaluates the BUILD-TIME expression that created P
    at match time, rather than simply reading P's current value (the already-built PatternVar).
    This re-invokes re_ (the build-time reduce function) with pattern arguments instead of strings
    → error 103 in re_'s EVAL → no pattern returned → Shift is never called → $'@S' is empty
    → Pop() returns '' (empty string) → pp(sno) calls t('') → GetProgramDefinedDataField crashes
    casting StringVar to ProgramDefinedDataVar.

    Evidence:
      - Trace confirms re_ fires at match time (not build time) when *P is matched
      - Shift() is never called during the match — no tree nodes pushed
      - Pop() returns 'string' not 'treeNode'
      - Standalone EVAL tests confirm re_ and sh_ EVALs both work correctly when P is a global
        variable — the bug is specific to how ConvertUnaryStarOperatorsToDeferredExpressions /
        ExtractStarExpressions in Lexer.cs compiles *P references.

    Hypothesis: ExtractStarExpressions captures the full RHS expression tree that initialized P
    (the reduce(...) call) as the deferred expression for *P, rather than a simple variable load.
    This is correct for inline *EXPR but wrong for *P where P is a plain variable already holding
    a pattern.

  NEXT SESSION must:
    1. In Lexer.cs ExtractStarExpressions: verify what DeferredCode is generated for *P
       when P is a simple IDENTIFIER token (not a compound expression). It should emit
       a plain variable-load, not replay the expression that last assigned P.
    2. Write unit test: assign P = somePattern; match 'x' *P — verify P's value is read,
       not P's initializer re-evaluated.
    3. Fix ExtractStarExpressions (or the MSIL emitter) so *P for a simple variable
       emits a variable load, not expression replay.
    4. Run beauty suite gate (must stay 17/17).
    5. Run self-host test: SELF-HOST PASS.
    6. Run unit tests + commit + push snobol4dotnet.

- [ ] **S-3** — Gate: see "Test command" section above. Output: `SELF-HOST PASS`.

## Rules

- Test gate passes before every commit.
- Commit as `LCherryholmes` / `lcherryh@yahoo.com`.
- Rebase before every .github push.
- **Windows compatibility:** never use bare `'\n'` as a line separator in C# source; always use `Environment.NewLine`.
- See RULES.md for full rules including handoff checklist.

  SESSION WORK (this session — deep diagnostic, no code changes, HEAD unchanged ec59eeb):
    - Beauty gate confirmed 17/17 at session start (HEAD ec59eeb)
    - Self-host crash with 'START\n' as input: same InvalidCastException at Data.cs:206

    KEY FINDING: ARBNO + *fn() semantic actions are NOT broken in general.
    Exhaustive tests show all these work correctly:
      - ARBNO(LEN(1) *inc()) on 'ABC' POS(0)..RPOS(0) → count=3 ✓
      - ARBNO(*cmd) where cmd = LEN(1) *inc() → count=3 ✓
      - *Parse where Parse = *Push() ARBNO(*Command) *Top() → stack correct ✓
      - FENCE + alternates inside ARBNO → correct ✓
      - *Parse (via Graft) with ARBNO inside → correct ✓
    The prior session's "ARBNO(*P) semantic actions never fire" finding was
    a test artifact: 'ABC' ARBNO(p) (no anchoring) succeeds with 0 iterations
    because ARBNO(epsilon) matches at position 0. With POS(0)/RPOS(0) forcing
    full-string match, it works correctly. The Graft fix is sound.

    ROOT CAUSE IS ELSEWHERE — narrowed to beauty.sno's Stmt/Command/Reduce interaction:
    - Command = nInc() FENCE(*Comment~'Comment'(..)nl | *Control~'Control'(..)nl | *Stmt(..)7 nl)
    - *Stmt arm calls Reduce('Stmt', 7) — pops 7 items from the tree stack
    - For input 'START\n' (label-only statement), some of the 7 slots are empty/wrong type
    - Reduce() pops a PatternVar (one of the OPSYN'd operators stored as pattern)
      instead of a tree node — that PatternVar lands in a tree child slot
    - Later pp() calls t(x) → GetProgramDefinedDataField → PatternVar cast crash

    ARCHITECTURE NOTE — semantic.sno OPSYN design:
    - OPSYN('~', 'shift', 2): p ~ 'Label' calls shift(p, 'Label') at BUILD TIME
      → returns pattern: p . thx . *Shift('Label', thx)
    - OPSYN('&', 'reduce', 2): p & 'nTop()' calls reduce(p, 'nTop()') at BUILD TIME
      → returns pattern: epsilon . *Reduce('Parse', nTop())  [n is a string, evaluated at match time]
    - nPush/nInc/nTop/nPop all return PATTERNS (epsilon . *PushCounter() etc.)
      evaluated at BUILD TIME; side effects fire at MATCH TIME via *fn()

    NEXT SESSION must:
    1. Instrument Reduce() in ShiftReduce.sno to OUTPUT the DATATYPE of each
       popped item when xTrace > 0. Run self-host on 'START\n' with xTrace=1.
       Identify which of the 7 pops returns a PatternVar.
    2. Trace which sub-pattern of Stmt produces the bad value. Stmt parses:
       Label + White + Expr14 + (pattern|assignment) + Goto + Gray → 7 slots.
       For 'START\n': Label='START', everything else is epsilon/empty.
       Verify each ~ 'tag' call correctly produces a tree node for empty matches.
    3. Fix: ensure epsilon ~ 'tag' produces a proper null/empty tree node,
       not a PatternVar, when the matched value is empty.
    4. ALTERNATIVELY (simpler): harden GetProgramDefinedDataField in Data.cs:206
       to handle PatternVar gracefully (return null/empty tree) rather than crashing,
       then check if beauty output becomes correct.
    5. Run beauty gate (must stay 17/17), then self-host.

    - snobol4dotnet HEAD: ec59eeb (unchanged)
    - corpus HEAD: 7d26569 (unchanged)

  SESSION WORK (this session — crash localized to BuildMain, not match time):
    - Beauty gate confirmed 17/17 at session start (HEAD ec59eeb)
    - FRETURN investigation: confirmed FRETURN works for standalone calls with
      explicit :S/:F goto. For calls embedded in RHS with no goto, statement
      correctly fails and falls through. No FRETURN bug affecting self-host.
    - Added stack-unwind in CallFuncBySlot (MsilHelpers.cs) after handler sets
      Failure=true: unwinds SystemStack to StatementSeparator. Beauty 17/17 still
      passes. Committed as dcf6457.
    - KEY FINDING: crash at Data.cs:206 fires at BUILD TIME (BuildMain), not
      during match. Confirmed by xTrace experiment: crash happens before any
      Reduce/Shift trace fires, during parser pattern construction in beauty.sno.
    - Stack trace: BuildMain → ExecuteLoop → (pattern build stmt) →
      CallFuncBySlot → ExecuteProgramDefinedFunction → ExecuteLoop →
      (treeNode field accessor t/v/n/c) → CallFuncBySlot →
      GetProgramDefinedDataField → PatternVar cast crash at line 206.
    - The crash is during OPSYN/reduce()/shift() calls that build patterns at
      load time — something in the pattern construction chain calls t()/v()/n()/c()
      with a PatternVar argument.
    - Prior session hypothesis about *P reading P's build-time initializer is
      likely correct; needs confirmation in Lexer.cs ExtractStarExpressions /
      CreateSimpleStarExpression.

  SESSION WORK (this session — Data.cs hardened, self-host now reaches Parse Error):
    - Data.cs:206 hardened: guarded pattern match replaces hard cast.
      PatternVar (or any non-ProgramDefinedDataVar) now returns FRETURN cleanly.
    - Beauty gate: 17/17 PASS (unchanged)
    - Self-host: InvalidCastException eliminated. Now outputs 26 lines then
      'Parse Error' — mainErr1 path fires on 'START\n' (label-only statement).
    - Root cause: ARBNO(*Command) fails to parse label-only stmt in Parse pattern.
      Stmt has epsilon ~ '' for all optional slots; Reduce('Stmt', 7) may receive
      a bad type (PatternVar?) for one of the 7 slots when all are epsilon.
    - snobol4dotnet HEAD: 1c27d52
    - corpus HEAD: 7d26569 (unchanged)

  NEXT SESSION must:
    1. Instrument Reduce() in ShiftReduce.sno: add OUTPUT of DATATYPE of each
       popped item when xTrace > 0. Run self-host on 'START\n' with xTrace=1.
       Identify which of the 7 Reduce('Stmt',7) pops returns a PatternVar.
    2. Trace which sub-pattern of Stmt produces the bad value for empty match.
       Stmt slots: Label, White, Expr14, (pattern|assignment), Goto, Gray → 7.
       For 'START\n': Label='START', all else epsilon.
       Verify epsilon ~ 'tag' produces a proper null/empty tree node, not PatternVar.
    3. Fix: ensure epsilon ~ 'tag' gives a correct tree node for empty matches.
    4. Run beauty gate (must stay 17/17), then self-host gate (SELF-HOST PASS).

    - snobol4dotnet HEAD: 1c27d52
    - corpus HEAD: 7d26569 (unchanged)


  SESSION WORK (this session — MINIMAL REPRO FOUND, prior theory invalidated):
    Beauty gate 17/17 confirmed at session start (HEAD 1c27d52).

    INSTRUMENTATION RESULT invalidates prior hypothesis:
      Added unconditional OUTPUT trace to both Shift() and Reduce() in ShiftReduce.sno.
      Ran self-host with input '&FULLSCAN = 1\n' (simpler than 'START\n' — same failure).
      Confirmed "DEBUG: ShiftReduce.sno loaded" fires at load time.
      Then Parse Error fires.
      NEITHER Shift NOR Reduce is ever called. Zero semantic actions during Parse.
      Prior "Reduce('Stmt',7) pops a bad PatternVar" hypothesis is WRONG —
      Reduce never runs, so it can't pop anything.

    BISECTED TO SHARP MINIMAL REPRO — 2-arg DEFINE kills pattern callbacks:

    REPRO-FAILS (Shift callback never fires during match):
           DEFINE('Shift(t,v)')
           DEFINE('shift(p,t)','shift_')                         :(setup_end)
    Shift  OUTPUT = 'SHIFT(' t ', v=[' v '])'                    :(NRETURN)
    shift_ shift = EVAL("p . thx . *Shift('" t "', thx)")        :(RETURN)
    setup_end
           x = 'ABC' CHAR(10)
           L1 = shift(BREAK(' ' CHAR(10) ';'), 'Label')
           x POS(0) L1                                           :S(ok)F(fail)
    ok     OUTPUT = 'match passed'                               :(END)
    fail   OUTPUT = 'match failed'
    END
    Result: prints 'match passed' but never 'SHIFT(...)'.

    REPRO-WORKS (identical body, only DEFINE form differs):
           DEFINE('Shift(t,v)')
           DEFINE('shift1(p,t)')                                 :(setup_end)
    Shift  OUTPUT = 'SHIFT(' t ', v=[' v '])'                    :(NRETURN)
    shift1 shift1 = EVAL("p . thx . *Shift('" t "', thx)")       :(RETURN)
    setup_end
           x = 'ABC' CHAR(10)
           L1 = shift1(BREAK(' ' CHAR(10) ';'), 'Label')
           x POS(0) L1                                           :S(ok)F(fail)
    Result: prints 'SHIFT(Label, v=[ABC])' then 'match passed'.

    QUIRK — when BOTH 1-arg and 2-arg defined functions appear in the same program,
    BOTH fire correctly regardless of call order. Feels like MSIL / ExecutionCache
    decides something on the whole-program function set. Consistent with prior
    session's "R_PAREN_FUNCTION falls back / ThreadIsMsilOnly=true / MSIL fix
    never fires" note.

    CONCLUSION — THIS is S-2's root cause.
    semantic.sno uses 2-arg DEFINE for EVERY helper:
      DEFINE('shift(p,t)',  'shift_')
      DEFINE('reduce(t,n)', 'reduce_')
      DEFINE('pop()',       'pop_')
      DEFINE('nPush()',     'nPush_')   etc.
    So every *Shift, *Reduce, *PushCounter, *IncCounter, *TopCounter, *PopCounter,
    *PopDummy callback embedded in every parser pattern built via ~ or & silently
    fails to fire during match. Parse matches structurally (ARBNO accepts 0 Commands),
    stack stays empty, Pop() returns '', pp('') crashes or errors downstream.

  NEXT SESSION must:
    1. Instrument the runtime to confirm: what's different in the pattern graph
       compiled for a 2-arg vs 1-arg DEFINE'd function that returns a pattern with
       a *Callback reference?
       Likely places:
         - Builder.cs / DefineImpl — how the function entry is registered
         - FunctionSlotIndex — is 2-arg slot populated differently?
         - BuilderEmitMsil.cs R_PAREN_FUNCTION — prior session noted the MSIL
           fallback doesn't wire properly when function is DEFINE'd at runtime
           (2-arg form is runtime DEFINE).
         - ExecutionCache.cs — is the pattern being cached with a stale version
           missing the callback?
    2. Try: run snobol4dotnet with MSIL cache / ThreadIsMsilOnly disabled on
       repro19.sno. If Shift then fires, that confirms MSIL is the culprit.
    3. Minimal fix attempt: in DefineImpl, ensure 2-arg form creates the same
       FunctionSlotIndex entry shape as 1-arg form.
    4. Beauty gate 17/17 must still pass after fix.
    5. Self-host gate: SELF-HOST PASS.

    - snobol4dotnet HEAD: 1c27d52 (unchanged — this session diagnosis only, no code)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)


  SESSION WORK (this session — ROOT CAUSE FIXED for prior repros, new error 109 surfaces):

    PRIOR THEORY INVALIDATED.  The "2-arg DEFINE breaks pattern callbacks" theory
    from last session was wrong.  Both 1-arg and 2-arg DEFINE forms had the SAME
    bug.  Real root cause:

    BUG: `AmpCaseFolding` field defaults to `1` (fold ON) and was never seeded
    from the `-f` command-line flag.  When `EVAL` runs, it does:
        Parent.BuildOptions.CaseFolding = AmpCaseFolding != 0;
    to restore the user's `&CASE` keyword setting.  This temporarily flipped
    CaseFolding back to `true` even with `-bf`, folding identifiers like
    `Shift` to `SHIFT` inside the EVAL'd pattern.  At match time, *Shift's
    function call looked up `'SHIFT'` in FunctionTable -> not found -> error 22.

    FIX (snobol4dotnet 13bfcc0):  ApplyStartupOptions seeds AmpCaseFolding=0
    when -f is set.  8-line minimal diff in Builder.cs.

    VERIFICATION:
      - Beauty 17/17 PASS (unchanged, no regression)
      - Original S-2 minimal repros from goal file (REPRO-FAILS and REPRO-WORKS):
        BOTH PASS now; output matches SPITBOL exactly:
          SHIFT(Label, v=[ABC])
          match passed
      - Isolated EVAL+star repros (t3, t4, t10, t11, t13, t17, t18 — see
        instrumented test sequence in commit message of 13bfcc0): ALL PASS
      - Self-host PROGRESS: was 16-line output (Parse Error on START),
        now 35-line output reaching `&FULLSCAN = 1` before failing with
        new bug -- error 109 in ShiftReduce.inc

    NEW BUG SURFACED (now the actual S-2 blocker):

    Self-host on `&FULLSCAN = 1` input fails with:
      ShiftReduce.inc(3/3/3): error 109 -- ge first argument is not numeric
                     c              =    GE(n, 1) ARRAY('1:' n)

    Reduce trace shows `n` arrives as DATATYPE(n)='expression' (an
    ExpressionVar), not integer.  The expression is `*(GT(nTop(),1) nTop())`
    which IS what beauty's grammar passes via the `&` OPSYN reduce wiring:
        ("'|'" & '*(GT(nTop(),1) nTop())')
    -> reduce("'|'", "*(GT(nTop(),1) nTop())")
    -> EVAL("epsilon . *Reduce('|', *(GT(nTop(),1) nTop()))")

    Inside that EVAL'd pattern, `*(GT(nTop(),1) nTop())` is in function-arg
    position to `*Reduce`.  snobol4dotnet pushes it as ExpressionVar (deferred)
    rather than evaluating it eagerly.  When *Reduce fires, `n` is the
    ExpressionVar.  ShiftReduce.inc tries `IDENT(DATATYPE(n), 'EXPRESSION')`
    to detect this and EVAL it -- but DATATYPE returns lowercase 'expression'
    while the test compares uppercase 'EXPRESSION', so the IDENT fails under
    case-sensitive `-f` mode and falls through to `GE(ExpressionVar, 1)` ->
    error 109.

    THREE POSSIBLE FIX APPROACHES (none committed this session):

    A. Make snobol4dotnet evaluate ExpressionVar args eagerly when calling
       user-defined functions (matches SPITBOL semantics).  Tried this:
       added EvaluateExpressionArgs in Function() and CallFuncBySlot().
       BLOCKER: also fires during BUILD-TIME grammar construction calls
       like `reduce(t, n)` where n is a string -> EVAL builds the pattern
       -- but the pattern is then used as left-side of an assignment
       `snoStmt = reduce_result`, which evaluates left-side ExpressionVars
       in Assign().  That sub-thread runs OUTSIDE Scanner so a ScanDepth
       gate doesn't help: ScanDepth=0 when Reduce ultimately fires inside
       the grafted pattern.  All revert: no code changes survived.

    B. Fix ExpressionVar's PATTERN conversion to evaluate eagerly when the
       result is non-pattern (integer, string).  Likely the cleaner fix.
       In IntegerConversionStrategy.cs, the EXPRESSION case wraps integers
       as ExpressionVar by re-compiling them as star-expressions.  This is
       wrong direction; a star-expression that yielded an integer should
       BE the integer when used as a function argument.

    C. Patch beauty source: change `IDENT(DATATYPE(n), 'EXPRESSION')` to
       compare case-insensitively.  Per RULES.md "Portable tests only"
       (DATATYPE Portable Tests goal), this is what corpus tests are
       supposed to do anyway:
           dEXPR = REPLACE(DATATYPE(*(0)), &LCASE, &UCASE)
           ...
           IDENT(REPLACE(DATATYPE(n), &LCASE, &UCASE), dEXPR)
       But RULES.md ALSO says "never patch corpus to work around runtime
       bugs" -- and SPITBOL handles this case without needing the EXPRESSION
       branch (it never produces ExpressionVar from `*(integer)`).  So this
       is a runtime bug, not a corpus bug.

    RECOMMEND APPROACH B for next session: make IntegerConversionStrategy
    (and similar) convert to PATTERN by producing a SucceedPattern (or
    proper terminal) wrapping the value, NOT wrapping as another
    ExpressionVar.  Then `*(GT(nTop(),1) nTop())` evaluates to integer 7,
    which when needed as a pattern wraps to a pattern-of-int-7, and when
    needed as a function arg passes as integer 7.

    SIDE NOTE: Three corpus include files (is.inc, FENCE.inc, io.inc) had
    to be copied into demo/beauty/ for self-host to find them, since
    snobol4dotnet's -INCLUDE searches CWD only (no -I or SETL4PATH support).
    These copies were temporary and cleaned up at session end.  Adding
    -I include-path support to snobol4dotnet's CommandLine.cs is a
    follow-on (independent of S-2).

    - snobol4dotnet HEAD: 13bfcc0 (committed and pushed)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)
    - Self-host: now reaches `&FULLSCAN = 1`, fails with error 109 on
      ExpressionVar arg to Reduce

  SESSION WORK (Sun Apr 26 evening — runtime errors fixed, parser still blocks):

    Approach B (from prior session's recommended fixes) implemented:
    on-demand evaluation of ExpressionVar in non-pattern conversion
    contexts.  Three small changes in snobol4dotnet (commit 0914fbf):

      • Var.cs ToNumeric: ExpressionVar arg → run DeferredCode, pop
        result, recurse for numeric extraction.
      • NumericComparisonHelper.cs BinaryComparison: when ToNumeric
        fails because Failure was already set by the deferred eval,
        use NonExceptionFailure() instead of error 109/110/etc.
      • NumericHelper.cs BinaryNumericOperation: same propagation rule
        for +, -, *, /, ^ (errors 1, 2, 12, 16, 26, 32).

    Approach A (eager-evaluate ExpressionVar in ExtractArguments) was
    tried first and **regressed Qize/XDump/omega** drivers.  Root
    cause: the *assign(.part, *'literal') idiom in Qize.inc relies on
    `expression` arriving at the user-defined `assign` function as
    EXPRESSION so it can `EVAL(expression)` later.  Eager evaluation
    in ExtractArguments breaks that idiom.  Reverted; replaced with
    the on-demand strategy in conversion sites only.  Build-time
    `reduce(t, n)` calls are also unaffected because their args are
    StringVar (the EVAL'd source string), not ExpressionVar.

    Also discovered: `_reusableArgList` is shared across recursive
    Function/Operator calls; running DeferredCode mid-ExtractArguments
    corrupts the list (ArgumentOutOfRangeException).  Documented but
    not exploited — the on-demand fix sidesteps the issue.

    Self-host result on this clone:
      • All `error 109` lines: gone.
      • All `error 1` lines: gone.
      • Output is now clean up to "Parse Error" on the first
        non-comment statement.
      • Tiny inputs that succeed: comment-only, label-only `START\n`,
        `END`-only.
      • Tiny input that fails (Parse Error): `              x = 1`.

    Conclusion: the runtime is now SPITBOL-compatible enough for the
    Reduce/EVAL deferred-expression chain.  The remaining S-2 work is
    the **pattern engine** — `nPush() ARBNO(*Command) *Top()` only
    matches at zero-Command count.  Same territory as multiple prior
    sessions; the Graft fix from 826d4ff handles direct `*P` but not
    the nested-star case that `*Command` ultimately compiles to via
    the `&` OPSYN chain.

  NEXT SESSION must:
    1. Write a minimal repro outside beauty: e.g.
         X = ('a' . *push) | ('b' . *push)
         Parse = nPush() ARBNO(*X) *Top()
         'aab' POS(0) *Parse RPOS(0)
       Expect 3 push calls.  If <3, that's the same root cause.
    2. Re-investigate ArbNoPattern.Scan + UnevaluatedPattern.Scan
       interaction.  Specifically: when an ARBNO body is `*X` and
       `X` itself contains `*Y` callbacks, do those callbacks run
       AND does ARBNO see the alternates needed for backtracking?
    3. After fix: beauty 17/17 must pass; self-host gate must produce
       SELF-HOST PASS (≥500 stderr lines, exit 0, no error markers).
    4. Side task (independent): add `-I` include-path support to
       CommandLine.cs so beauty.sno can self-host without copying
       is.inc/FENCE.inc/io.inc into demo/beauty/.  Goal-file already
       notes the temp-copy trick is not the answer.

    - snobol4dotnet HEAD: 0914fbf (committed and pushed)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS (verified end-of-session)
    - Self-host: runtime errors eliminated; Parse Error on assignment
      remains (graft + ARBNO interaction)

  SESSION WORK (Sun Apr 26 evening — diagnosis only, no code changes):

    PRIOR HYPOTHESIS INVALIDATED — ARBNO + nested-* is not the bug.

    Step 1 of the prior "NEXT SESSION must" list specified a minimal
    repro: `X = ('a' . *push) | ('b' . *push); Parse = nPush() ARBNO(*X)
    *Top(); 'aab' POS(0) *Parse RPOS(0)` — expect 3 push calls; if <3,
    that confirms the ARBNO + nested-* root cause.

    Result on this clone (HEAD 0914fbf): produces **3 push calls**.
    Output identical to SPITBOL.  The Graft fix from 826d4ff handles
    this shape correctly.  ARBNO + nested-* with cursor-driven
    callbacks (including alternation under *X) is NOT the bug.

    Variations tested, all PASS on snobol4dotnet at 0914fbf:
      • ARBNO(LEN(1) *push())                       on 'aab' → 3 ✓
      • ARBNO(*X) where X = ('a' . *push) | ('b' . *push)   → 3 ✓
      • Cmd = nInc FENCE(*A | *B | *C); ARBNO(*Cmd)         → 6 ✓
      • r19: EVAL("epsilon . *Reduce('lit', nTop())") where
        nTop is properly DEFINEd as a function                → ✓
      • Mini-beauty (r16d): nPush ARBNO(*snoCommand) without
        the trailing reduce-pattern                           → ✓

    NEW DIAGNOSIS — divergence is at *snoParse match dispatch.

    Instrumented Shift/Reduce/PushCounter/IncCounter in a temp copy of
    semantic.inc + counter.inc + ShiftReduce.inc (under /tmp/inst_beauty/,
    NOT modifying corpus per RULES.md).  Ran beauty.sno < tiny.sno where
    tiny.sno is `              x = 1\n` (the documented self-host failure
    input).

    BUILD-PHASE TRACES: identical for the first 79 lines on both runtimes.
    All shift(p,t=...) and reduce(t=...,n=...) build-time helper calls
    fire in the same order with the same arguments.  The grammar build
    is sound; snoParse on both runtimes ends up with type PATTERN
    (snobol4dotnet returns lowercase 'pattern' per spec).

    MATCH-PHASE TRACES:
      • SPITBOL: fires [T] PushCounter() then [T] IncCounter() 4 times
        (= 4 successful match invocations across main loop), beautifies
        cleanly to 5 output lines.
      • snobol4dotnet: fires ZERO match-time semantic actions, falls
        straight through to mainErr1 → "Parse Error".

    Added [M2] trace at beauty.sno:619 (the first `snoSrc POS(0)
    *snoParse *snoSpace RPOS(0)` invocation):
      • SPITBOL: [M2] before match: DATATYPE=PATTERN SIZE=20 → match OK
      • snobol4dotnet: [M2] before match: DATATYPE=pattern SIZE=20
        → :F(mainErr1) taken, NO callback fires in between.

    The match dispatch reaches the call site with a valid PATTERN value
    and the correct 20-byte snoSrc, then fails in the engine before
    any inner action — including nPush()'s `epsilon . *PushCounter()`
    cursor — can run.  Since epsilon always matches, *PushCounter()
    should fire if the engine even enters snoParse's body.  It doesn't.

    FOCUS REGION FOR NEXT SESSION

    `Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs` Scan() — the
    Graft path when the pattern being grafted is a 4-element
    concatenation: `nPush ARBNO(*snoCommand) ("'snoParse'" & 'nTop()')
    nPop()`.  Hypothesis: Graft wires the wrong start node — possibly
    skipping past nPush directly to ARBNO — so the cursor on nPush's
    epsilon never executes its *PushCounter() callback.  ARBNO then
    matches zero Commands (stack empty), the trailing reduce expects
    nTop() ≥ 1 children, and the whole match fails before any
    semantic action fires.

    Files to read first:
      • Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs
      • Snobol4.Common/Runtime/PatternMatching/Scanner.cs (Graft, Match)
      • Snobol4.Common/Runtime/AbstractSyntaxTree.cs (Graft impl)

  NEXT SESSION must:
    1. Build a minimal repro proving the issue: a 4-element concat
         P = nPush ARBNO(LEN(1)) reduce_pat nPop
       where nPush, reduce_pat, nPop are each independently shown to
       work, and assert that `'foo' POS(0) *P RPOS(3)` fires
       PushCounter exactly once on snobol4dotnet.  If it fires zero
       times, that confirms the Graft-on-multi-element-concat bug.
    2. Read AbstractSyntaxTree.Graft and Scanner.Match to verify Graft
       wires the FIRST node of the grafted pattern as the entry, not
       (e.g.) the last leaf or some other node.
    3. Fix Graft / UnevaluatedPattern.Scan as needed.  Beauty 17/17 must
       remain green after the fix.
    4. Run self-host gate: SELF-HOST PASS (≥500 stderr lines, exit 0).
    5. Side task: add `-I` include-path support to CommandLine.cs so
       beauty.sno can self-host without copying is.inc/FENCE.inc/io.inc
       into demo/beauty/.  (Independent from S-2 fix.)

    UNRELATED FINDING worth a sub-rung: snobol4dotnet's case-sensitive
    mode (`-bf`) appears to fold the lowercase identifier `input` to the
    `INPUT` reserved I/O name.  Repro:
      cat > /tmp/r14.sno << 'EOF'
                     &ANCHOR        =  0
                     &FULLSCAN      =  1
                     input          =  'hello'
                     OUTPUT         =  'value=[' input ']'
      END
      EOF
      dotnet Snobol4.dll -bf /tmp/r14.sno              # hangs on stdin
      dotnet Snobol4.dll -bf /tmp/r14.sno < /dev/null  # exits silently
      sbl    -bf /tmp/r14.sno                          # prints value=[hello]
    Expected per SN-31 (case-sensitive): lowercase `input` is a normal
    user variable, distinct from `INPUT`.  Likely separate bug —
    consider a new rung NET-INPUT-CASE.

    INFRA NOTE: dotnet-install.sh URL (https://dot.net/v1/...) and the
    CDN mirror are blocked by the egress proxy on this clone (HTTP 503
    "DNS cache overflow" from the proxy).  `apt-get install -y
    dotnet-sdk-10.0` on Ubuntu 24.04 (after `apt-get update`) works and
    yields 10.0.107 at /usr/bin/dotnet.  Consider adding
    `install_dotnet10.sh` under one4all/scripts/ that prefers apt and
    falls back to the script.  REPO-snobol4dotnet.md currently says
    `apt-get install -y dotnet-sdk-10.0` which works — but the
    `export PATH=/usr/local/dotnet10:$PATH` line is misleading on this
    clone (apt installs to /usr/bin).

    - snobol4dotnet HEAD: 0914fbf (unchanged this session — diagnosis only)
    - corpus HEAD: 7d26569 (unchanged)
    - Beauty gate: 17/17 PASS still expected (not re-run; build clean,
      no code changes)
    - SPITBOL self-host baseline: re-verified 649 lines exit 0 stderr-clean

  SESSION WORK (Sun Apr 26 late evening — Graft theory invalidated, bug localized to match ordering):

    Beauty 17/17 confirmed at session start (HEAD 0914fbf).
    Self-host: same 'Parse Error' on `              x = 1\n`.

    GRAFT-ON-MULTI-ELEMENT-CONCAT THEORY INVALIDATED.

    Built the predicted minimal repro per the prior session's "NEXT SESSION
    must" Step 1, in increasingly faithful versions (v1 → v6).  Final v6
    mirrors beauty exactly: function-form nPush()/nInc()/nPop()/nTop(),
    `~`/`&` OPSYN'd to EVAL-building shift_/reduce_, ARBNO(*Command)
    where Command = nInc() FENCE(*token), trailing
    `("'Top'" & 'nTop()')`.  ALL versions PASS byte-identical on
    snobol4dotnet and SPITBOL.  Output:
      PushCounter() / IncCounter() / Shift(Tok,a) (3x) /
      Reduce(Top,2) / PopCounter() / OK
    The "Graft skips first node of multi-element concat" hypothesis is
    therefore FALSE at the level the prior session imagined.  ARBNO +
    nested-* + EVAL'd reduce-pat all work together correctly.

    NEW BISECTION — input form determines outcome.

    With instrumented beauty in /tmp/beauty_inst (added unconditional
    TRACE- OUTPUTs to Shift/Reduce/PushCounter/IncCounter — NOT modifying
    corpus per RULES.md):

    | input              | snobol4dotnet result                  | matches SPITBOL? |
    |--------------------|---------------------------------------|------------------|
    | `\n` (newline only)| full traces, beautified output OK     | yes              |
    | `START\n` + `END\n`| full traces, prints START / END       | yes              |
    | `END\n`            | full traces, prints END               | yes              |
    | `x\n`              | snoLabel='x' path (BREAK swallowed it)| yes              |
    | `x=1\n` (no spaces)| snoLabel='x=1'  (BREAK swallowed it)  | yes              |
    | `              x\n`| **Parse Error** (with all-includes)   | NO (SPITBOL OK)  |
    | `              x = 1\n`| Parse Error                       | NO (SPITBOL OK)  |
    | `  x = 1\n`        | Parse Error                           | NO (SPITBOL OK)  |

    Trigger condition: ANY input where `*snoLabel` matches empty (BREAK
    at POS(0) when first char is space/tab) and snoStmt's grammar has
    to enter the non-epsilon arm starting `*snoWhite *snoExpr14 ...`.
    The all-epsilon arm 4 (`epsilon~'' epsilon~'' epsilon~'' epsilon~''`)
    works on snobol4dotnet; the *snoExpr14 arm does not.

    SECONDARY DIVERGENCE — semantic action ORDER is wrong.

    Compared trace order on `              x = 1\n` (input where SPITBOL
    succeeds and snobol4dotnet fails):

    SPITBOL fires (in this order):
      PushCounter, IncCounter,
      Shift(snoLabel,''), Shift(snoId,'x'), Shift('',''), Shift('=','='),
      PushCounter, IncCounter, PushCounter, IncCounter,   (nested in ())
      Shift(snoInteger,'1'), PATTERN, PATTERN, Shift('',''), Shift('',''),
      Reduce(snoStmt, 7), Reduce(snoParse, 1).
      Output: `                  x              =  1`

    snobol4dotnet fires:
      Shift(snoInteger,'1'),               ← first event! out of order
      PushCounter,                         ← only ONE total (vs 3 in SPITBOL)
      pattern, pattern,                    ← lowercase — DATATYPE='pattern'
      Shift('',''), Shift('',''),
      Reduce(snoStmt, 7),
      Reduce(snoParse, '').                ← second arg EMPTY, not 1!
      → Parse Error

    Three observations from this:

    (a) Side effects fire OUT OF MATCH ORDER on snobol4dotnet.  Shift
        for snoInteger fires BEFORE PushCounter, even though in the
        match Push must fire before any inner cursor.  SPITBOL fires
        them strictly in match-position order.  Smells like the EVAL'd
        patterns are replaying their build-time expressions during the
        match traversal, in build order rather than positional order.

    (b) Many side effects DON'T FIRE: the LHS Shifts (snoLabel,
        snoId='x', the '=' token) never produce trace lines on
        snobol4dotnet.  But the structural match still claims to
        succeed (Reduce(snoStmt, 7) is called).  This means the
        Stmt match completes structurally — the `=` literal IS
        consumed — but the cursor-bound `~ 'snoX'` semantic actions
        on intermediate slots never invoke shift_.

    (c) `Reduce(snoParse, )` with empty second arg confirms `nTop()`
        FRETURNed at match time.  TopCounter checks `DIFFER($'#N')`;
        FRETURN means `$'#N'` is empty.  But (a)+(b) explain why:
        only one PushCounter fired, and it may have fired AFTER the
        inner pattern that called nTop().  So nTop sees an empty
        counter stack at the moment Reduce uses its return value.

    The pattern `pattern` (lowercase) appears twice in the trace.  Its
    source is unknown but it's not from explicit OUTPUT in any beauty
    .inc file — searched all .inc and beauty.sno.  Likely an implicit
    type print via some failed conversion.  SPITBOL prints
    `PATTERN PATTERN` (uppercase) at the SAME trace position — so the
    underlying mechanism agrees, only the case differs (DATATYPE return
    case for pattern type).

    HYPOTHESIS — re-stated for next session.

    The bug is in how snobol4dotnet schedules side-effects of
    EVAL-built patterns containing `*Fn()` callbacks.  When a pattern
    of the shape `s . *Fn1 OTHERPAT . *Fn2` is built via EVAL and
    later grafted into an outer scanner, the Fn1/Fn2 callbacks fire
    in graft/build order rather than at the match cursor positions
    they originally annotated.  For a single-element concat
    (e.g. v6: `nPush ARBNO(*Cmd) reduce nPop`) the build order
    happens to coincide with match order because each side-effect
    is at a distinct positional anchor — so it works.  For
    snoStmt's deep alternation, where multiple cursor-bound `~` and
    `&` actions inside one statement-level pattern compete, the
    order goes wrong.

  NEXT SESSION must:

    1. Verify hypothesis (a) in isolation.  Build a 2-cursor pattern:
         P = ('a' . *F1) ('b' . *F2)
       built via two separate EVAL calls and concatenated.  Match
       'ab' POS(0) *P RPOS(2).  Expect F1, F2 in order.  Then build
       it as ONE big EVAL("('a' . *F1) ('b' . *F2)") and match.
       Compare to a hand-coded (no EVAL) version.  If side effects
       fire in different order in the EVAL'd version vs the
       hand-coded one, hypothesis confirmed.

    2. If (1) reproduces, the cause is in
       `Snobol4.Common/Runtime/Pattern/UnevaluatedPattern.cs` Scan or
       in how `EVAL` builds the pattern AST in the first place
       (`Builder.cs` BuildEval).  Likely the *Fn() nodes are being
       detached from their `s . *Fn` cursor parent and re-attached as
       root-level callbacks in the grafted graph.

    3. If (1) does NOT reproduce, the bug is specific to *Variable
       references where the variable holds an EVAL'd pattern.  Test
       with the 4-element concat from v6 but make one element
       depend on a deferred `*P` where P holds a multi-cursor
       pattern.  This is closer to beauty's nested *snoExpr14 chain.

    4. Side check: the lowercase `pattern` lines.  When XDump fires
       on a PATTERN object, snobol4dotnet returns 'pattern' from
       DATATYPE; XDump's `IDENT(objType, 'PATTERN')` test fails
       under -bf (case-sensitive); falls through to XDump40 which
       outputs `nm = pattern()`.  But XDump isn't called from
       beauty proper.  Source unknown — find what code path emits
       lowercase `pattern` standalone in the trace.  Possibly a
       diagnostic OUTPUT inside snobol4dotnet's runtime.  Worth
       finding because it indicates which exact pattern is being
       processed when the divergence happens.

    5. After the runtime fix: beauty 17/17 must pass; self-host gate
       must produce SELF-HOST PASS.

    Useful debugging files left in /tmp (NOT committed):
      • /tmp/beauty_inst/   instrumented beauty copy (unconditional
        TRACE- OUTPUTs in Shift, Reduce, PushCounter, IncCounter;
        is.inc, FENCE.inc, io.inc copied in for self-host)
      • /tmp/repro_v6.sno   verified-clean repro of v6 (passes both)
      • /tmp/t3.sno         minimal failing input: `              x = 1\nEND\n`

    Operational notes for next session:

    • SPITBOL oracle is at /home/claude/x64/bin/sbl after running
      `bash /home/claude/one4all/scripts/build_spitbol_oracle.sh`.
      Exits 0 normally on this clone.

    • dotnet-sdk-10.0 installs cleanly via apt-get on Ubuntu 24.04
      after `apt-get update`.  Proxy blocks dot.net.  Binary at
      /usr/bin/dotnet (NOT /usr/local/dotnet10 as REPO doc says).

    • Beauty 17/17 gate from REPO-snobol4dotnet.md works as written,
      but reports `*_driver.sno` (filenames in this corpus tree
      omit the `beauty_` prefix that the REPO doc shows; total is
      17 drivers, not 19).

    - snobol4dotnet HEAD: 0914fbf (unchanged this session — diagnosis only)
    - corpus HEAD: 0074bc5 (unchanged)
    - Beauty gate: 17/17 PASS (verified at session start)
    - SPITBOL/CSNOBOL4 baselines unchanged.

    REVISED HYPOTHESIS — EMPIRICALLY CONFIRMED:

    The pattern-match engine in snobol4dotnet RE-FIRES `*Fn()` callbacks
    on backtrack.  When a match has to retry an alternation arm whose
    body contains `pat $ *Fn(...)` cursor callbacks, the callbacks are
    invoked AGAIN on the retry — even though the arm was already
    structurally evaluated.  SPITBOL fires each callback exactly once,
    at the moment the cursor crosses its position.

    Evidence (test in /tmp/probe4.sno):

      P = 'a' $ *addg('A') ('y' $ *addg('Y') | 'b' $ *addg('B'))

      Successful match `'ab' POS(0) P`:
        SPITBOL → g='AB', snobol4dotnet → g='AB' (identical)

      Failing match `'ab' POS(0) P RPOS(99)` (RPOS always fails,
      forces engine into post-match retry sweep):
        SPITBOL → g='AB' (one A, one B)
        snobol4dotnet → g='ABB' (one A, TWO Bs)

    On a match that must retry, snobol4dotnet re-runs the alternation
    arm and re-fires its callback.  For beauty's deep grammar with many
    nested alternations and deep backtracking, this inflates Push counts
    on `$'@S'` (tree stack) and `$'#N'` (counter stack).  Reduce(snoStmt, 7)
    then pops 7 items from a stack that may have many duplicates from
    spurious retries — popping the wrong children.  The resulting
    tree has bogus structure, pp() prints garbage / drops fields, and
    the gate fails.

    This is also consistent with the parallel scrip finding (commit
    7ca7af1: "5 items vanish from `$'@S'`") — same symptom seen from
    the other end: scrip's diagnosis interprets the resulting wrong
    children as "missing items"; snobol4dotnet's instrumented trace
    shows EXTRA Reduces firing.  Same root cause: callbacks firing
    on backtrack/retry that should not.

    The "build-order" appearance in my earlier trace is then explained:
    the trace's first event Shift(snoInteger,1) is the LATEST retry —
    earlier events of the SAME callback fired first and were correct,
    but the trace shows the last write of g (or the OUTPUT line of the
    latest invocation), not the full history.  My instrumentation used
    OUTPUT directly so each call DOES print, but with multiple inner
    backtracks the order of OUTPUT lines reflects the retry sequence
    rather than the final-successful-path order.

  NEXT SESSION must:

    1. Build snobol4dotnet, reproduce /tmp/probe4.sno's T2 divergence
       (SPITBOL g='AB' vs snobol4dotnet g='ABB').  This is the
       single-line confirmation that the bug is "backtrack re-fires
       callbacks", not anything ARBNO/Graft-specific.

    2. Find the alternation backtrack path in
       `Snobol4.Common/Runtime/PatternMatching/Scanner.cs` (or wherever
       alternation try/retry is implemented).  When the engine
       advances past a `$ *Fn` cursor-callback node, it must remember
       that the callback ALREADY FIRED and not re-fire it on retry.

       The fix is conceptually: each AST node that has fired a
       callback during the current match attempt records that fact
       in the per-match scratch; on retry/backtrack, the Scanner
       checks before invoking *Fn.  Or equivalently: alternation
       backtrack restores the cursor but does NOT replay any callbacks
       between the alternation start and the failure point.

    3. After the runtime fix:
         - /tmp/probe4.sno T2 must produce g='AB' on snobol4dotnet
         - Beauty 17/17 must remain green
         - Self-host gate must produce SELF-HOST PASS

    Useful debugging files left in /tmp (NOT committed):
      • /tmp/probe4.sno          minimal repro (1 page)
      • /tmp/beauty_inst/        instrumented beauty copy
      • /tmp/repro_v6.sno        verified-clean repro of v6 (passes both)
      • /tmp/t3.sno              minimal failing input

    Operational notes for next session:

    • SPITBOL oracle is at /home/claude/x64/bin/sbl after running
      `bash /home/claude/one4all/scripts/build_spitbol_oracle.sh`.

    • dotnet-sdk-10.0 installs cleanly via apt-get on Ubuntu 24.04
      after `apt-get update`.  Proxy blocks dot.net.  Binary at
      /usr/bin/dotnet (NOT /usr/local/dotnet10 as REPO doc says).

    • Beauty 17/17 gate from REPO-snobol4dotnet.md works as written,
      but reports `*_driver.sno` (filenames in this corpus tree
      omit the `beauty_` prefix that the REPO doc shows; total is
      17 drivers, not 19).

  CROSS-REFERENCE — see GOAL-LANG-SNOBOL4 SN-26c-parseerr-h (commit 7ca7af1):

    A parallel session on `scrip` (the other SNOBOL4 implementation in
    one4all) reports an isomorphic symptom on beauty: items appear to
    "vanish" from `$'@S'` between Push and Reduce.  The diagnosis there
    blamed pattern-match save/restore stomping on globals.  The
    snobol4dotnet evidence in this session shows the inverse mechanism
    (callbacks RE-FIRE on backtrack, inflating the stack), which
    produces the same downstream symptom (Reduce pops wrong children →
    pp() prints garbage).  The two implementations may have the same
    bug, the same root cause, or two different bugs in the same area.
    Worth keeping the cross-reference open: a fix in either runtime
    should be checked against both repros.

