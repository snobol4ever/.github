# GOAL-NET-MONITOR-3WAY.md — snobol4dotnet 3-way Sync-Step Monitor

**Repo:** snobol4dotnet (+ one4all for harness wiring)
**Depends on:** SN-26-bridge-coverage-b closed (csn + spl bridges fire on
`.`-captures and on chokepoint assignments — already landed in csnobol4
`ad993fe` and x64 `3cd2dcc`).  Independent of GOAL-NET-BEAUTY-SELF S-2
runtime work.

**Done when:** The canonical 3-way auto harness in one4all
(`scripts/test_monitor_3way_sync_step_auto.sh`) accepts a fourth
participant `dot` (snobol4dotnet) via `PARTICIPANTS="csn spl dot"`, and
running it on `beauty.sno < /tmp/asg.sno` produces a sync-step trace
where csn/spl/dot all emit binary wire records on every catch-all event
(VALUE on assignment + `.`-capture commit, CALL on user-fn entry,
RETURN on user-fn exit, END at process exit).  Controller advances
step-by-step until first DIVERGE; the user-facing output is the
**last-agreed + first-disagreed** record pair (per RULES.md "read the
divergence point, not the trace").

This unblocks the same workflow currently used for scrip self-host
debugging (SN-26-bridge-coverage-c) but pointed at snobol4dotnet's
S-2 beauty self-host failure.  Multiple-runtime ground truth replaces
hypothesizing about pattern-engine semantics from instrumented .sno
prints.

## Why a fourth participant, not a separate harness

The wire format (`monitor_wire.h`) and controller
(`scripts/monitor/monitor_sync_bin.py`) are runtime-agnostic.  They
compare records byte-for-byte across an arbitrary set of participants
identified by a 4-part `NAME:READY:GO:NAMES` spec.  Adding `dot`
requires:

1. A C# IPC library inside snobol4dotnet that mirrors `monitor_ipc_runtime.c`
   from CSNOBOL4 / x64 — opens `MONITOR_READY_PIPE` / `MONITOR_GO_PIPE`,
   interns names to a sidecar file, emits 13-byte fixed-header records.
2. Three fire-point hooks in snobol4dotnet runtime that match the
   established CSN and SPL chokepoints:
   - **VALUE** on every variable assignment (Var.cs `AssignToVar` /
     `ConcreteVar.Assign`) and on every `.`-capture commit
     (CursorAssignmentPattern.cs commit path).
   - **CALL** on every user-defined function entry
     (`ExecuteProgramDefinedFunction` / `CallFuncBySlot` for user-defined
     entries — not built-ins).
   - **RETURN** on every user-defined function exit
     (paired with the CALL site).
3. Env-var gate at startup: `MONITOR_BIN=1` activates the bridge;
   absence of `MONITOR_READY_PIPE` is silently no-op (same discipline
   as csn/spl).
4. Harness lane in `test_monitor_3way_sync_step_auto.sh` and a fourth
   PARTICIPANTS code-path `dot`.

After this lands, the same single command drives sync-step debugging
across ALL implementations.  The 3-way name is preserved (csn/spl/scr
or csn/spl/dot or csn/spl/scr/dot — controller is N-way, harness
exposes the env knob).

## Sub-rungs (sequenced)

- [ ] **N3-1 — DotNet IPC bridge, standalone smoke**
  Implement `Snobol4.Common/Runtime/Monitor/MonitorIpc.cs` with three
  public static entry points: `EmitValue(string name, Var value)`,
  `EmitCall(string fnName)`, `EmitReturn(string fnName)`.  Initialize
  in static ctor: read `MONITOR_BIN`/`MONITOR_READY_PIPE`/
  `MONITOR_GO_PIPE`/`MONITOR_NAMES_OUT` env vars; if `READY_PIPE`
  absent, set a `bool _enabled = false` and make all entry points
  no-op.  Otherwise open the FIFOs, write the ready handshake byte,
  begin emitting records on each entry-point call.

  Wire format already specified in `monitor_wire.h` — port the
  packing logic from `csnobol4/monitor_ipc_runtime.c` lines ~150-280.
  Names interned via a `Dictionary<string,uint>` + sidecar text file
  flushed at process exit (`AppDomain.CurrentDomain.ProcessExit`).

  **Smoke gate:** new `scripts/test_smoke_dot_bridge.sh` PASS=1.
  Probe: `dotnet Snobol4.dll -bf` on `corpus/programs/snobol4/demo/dot_bridge/probe.sno`
  with the env vars set + a tiny consumer reading the wire.  Probe
  emits a single `x = 'hello'` and END; expect 2 wire records
  (VALUE + END).

- [ ] **N3-2 — Fire-point: assignment chokepoint**
  Hook `MonitorIpc.EmitValue` from snobol4dotnet's central assignment
  path.  Candidate chokepoint: `ConcreteVar.AssignFromStack` (or
  whatever method all `=` lvalue stores funnel through; needs a
  source-side audit).  Mirrors csn `ASGNVV` (line 5938 in v311.sil)
  and spl `asign:asg01` (line 17596 in sbl.min).

  Validation: a probe equivalent to csn-bridge-a's hello probe.
  `S='hello'\nEND\n` produces exactly 1 VALUE record + END.
  Sidecar names: `S`.

  Beauty 17/17 must remain green.

- [ ] **N3-3 — Fire-point: `.`-capture commit + array/table element**
  Hook the commit path of `CursorAssignmentPattern` (the runtime
  implementation of `pat . var` and `pat . *fn(args)`).  Mirrors
  csn `NMD4` and spl post-asign coverage (SN-26-bridge-coverage-a
  and -b).

  Also covers the `<lval>` sentinel discipline established for csn:
  if the captured name resolves to anonymous storage (array element
  / table slot) rather than a vrblk-with-name, validate that
  candidate name characters are printable-ASCII identifier bytes;
  on failure intern the sentinel `<lval>`.  Symmetric with
  `lvalue_name_id()` in csn's runtime.

  Validation: probe equivalent to csn-bridge-c's
  `probe_complex.sno` (5 LHS forms).  All 5 forms emit clean
  records with correct names.

- [ ] **N3-4 — Fire-point: CALL + RETURN on user-defined functions**
  Hook the entry/exit of user-defined functions only (filter out
  builtins by checking the function-table flag).  Mirrors csn
  `DEFF18`/`DEFF20` and spl `bpf09` predecessor + `retrn` body.

  Validation: probe equivalent to csn-bridge-b — DEFINE+SQR(7).
  Expect 7-record wire (VALUE-bind + CALL + VALUE-arg + ... + RETURN).

- [ ] **N3-5 — Harness lane: `dot` participant**
  Edit `scripts/test_monitor_3way_sync_step_auto.sh`:
  - Add `dot` to the recognized PARTICIPANTS set.
  - Build the dot launch command analogously to the spl/csn ones:
    `MONITOR_BIN=1 MONITOR_READY_PIPE=... MONITOR_GO_PIPE=... \
       MONITOR_NAMES_OUT=... \
       dotnet $SNO4 -bf $SNO < $STDIN_SRC`
  - Pass through the same per-participant timeout and FIFO setup.

  Validation: `PARTICIPANTS="dot" bash test_monitor_3way_sync_step_auto.sh
  /tmp/probe.sno` produces a clean trace.

- [ ] **N3-6 — End-to-end: 3-way csn/spl/dot on beauty self-host**
  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
  PARTICIPANTS="csn spl dot" \
      STDIN_SRC=$BEAUTY/beauty.sno \
      MONITOR_TIMEOUT=120 \
      bash scripts/test_monitor_3way_sync_step_auto.sh \
      $BEAUTY/beauty.sno
  ```
  Expected: controller reports a step number where `dot` first
  diverges from csn/spl agreement.  That step's last-agreed +
  first-disagreed pair is the canonical hand-off to GOAL-NET-BEAUTY-SELF
  S-2.  Past hypotheses about cursor-callback re-firing, ARBNO
  graft, ExpressionVar deferred eval all become **verifiable**:
  the wire shows exactly which VALUE record dot emits where csn/spl
  emit something different (or omits a record csn/spl both emit).

- [ ] **N3-7 — Hand off to GOAL-NET-BEAUTY-SELF S-2**
  Once the canonical divergence point is known from N3-6, the next
  GOAL-NET-BEAUTY-SELF session reads ONLY those two records (per
  RULES.md "read the divergence point, not the trace") and fixes
  the runtime gap.  This goal closes when N3-6 produces a clean
  divergence pair; the actual self-host fix continues under
  GOAL-NET-BEAUTY-SELF.

## Gates

After every sub-rung commit:
- snobol4dotnet beauty 17/17 still green
- snobol4dotnet unit tests still green (baseline 2375p/0f/2s)
- `test_smoke_dot_bridge.sh` PASS=1 (after N3-1)
- existing `test_smoke_sn26_csn_bridge_*.sh`,
  `test_smoke_sn26_spl_bridge*.sh`, `test_smoke_sn26_auto_binary.sh`
  unchanged (we don't break the existing 3-way)

## Dependencies

None gating.  Orthogonal to SN-26-bridge-coverage-c (scrip self-host)
in one4all and to S-2 runtime work in snobol4dotnet.  Closing N3-6
makes both goals' debugging easier.

## Risks

- **C# FIFO writes and AppDomain shutdown order.**  The names sidecar
  must flush before the wire FIFO closes.  If `ProcessExit` doesn't
  fire reliably (it doesn't, in some shutdown paths), names file may
  be empty and the controller won't be able to resolve `name_id`s.
  Mitigation: flush sidecar after every record emit (cheap; the file
  is tiny).
- **Performance overhead on assignment chokepoint.**  Beauty fires
  thousands of assignments per second.  Bench: ensure beauty 17/17
  doesn't regress more than a few percent in wall time when
  `MONITOR_BIN=1` is **unset** (no-op path must be a single boolean
  check).
- **Identifier name extraction at .-capture commit.**  C# closures /
  delegates may not expose the source variable name without
  reflection.  May need a small AST-side annotation pass to surface
  the lvalue name to the commit point.

## Estimated session count

3-4 sessions.  N3-1+N3-2 in one (scaffolding + first fire-point);
N3-3+N3-4 in another (remaining fire-points); N3-5+N3-6 in a third
(harness wiring + end-to-end); N3-7 hand-off is bookkeeping.
