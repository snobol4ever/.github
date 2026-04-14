# GOAL-INPROC-MONITOR.md — In-Process Sync Monitor

**Repo:** one4all
**Done when:** All three execution modes (--ir-run, --sm-run, --jit-run) can
be driven synchronously within a single process, comparing variable state,
label/PC, and success/fail flag after every statement. First divergence is
reported immediately with the statement number, label, and differing variables.
No files, no diffs, no child processes, no IPC. Light speed.

---

## The Problem with the Current Monitor

The existing monitor runs three separate processes, writes output to files,
and diffs them. This gives you output divergence but not:
- Which variable diverged first
- Which label path was taken
- At which exact statement the split occurred
- What the full variable state was at that moment

It is also slow (process spawn, file I/O, shell diff) and cannot introspect
into execution state — only observable output.

## The Eureka

All three executors already share the same `Program*` (same `STMT_t` list).
`SM_STNO` fires at every statement boundary in `sm_interp_run()`.
`execute_program()` already has a per-statement loop.
The NV store (name-value) is global and readable at any point.

The sync step: after each `STMT_t`, all three executors call a hook:

```c
typedef struct {
    int     stno;       /* statement number */
    int     last_ok;    /* 1=success, 0=fail */
    int     label_idx;  /* current label index or -1 */
} SyncState;

typedef void (*sync_hook_fn)(const SyncState *st, void *arg);
```

The hook snapshots NV store variables, compares the three SyncStates, and
on first divergence prints exactly what differed and exits.

In production: hook = NULL, zero overhead.
In monitor mode: hook = comparator.

---

## The Shared State Problem

Running IR → SM → JIT sequentially over the same `Program*` is not trivially
correct because all three executors share global mutable state. After IR runs
N statements, the NV store is mutated, `kw_stcount` is incremented, and the
ICN frame stack may have residue. SM starts in a corrupted world.

### What needs snapshot/restore

```
READ-ONLY after polyglot_init (safe to share, no restore needed):
  label_table        — built once, never mutated during execution
  icn_proc_table     — built once, never mutated
  g_pl_pred_table    — built once, never mutated

MUTABLE during execution (must snapshot/restore between runs):
  NV store           — NV_GET_fn/NV_SET_fn — all program variables
  kw_stcount         — statement counter
  kw_stlimit         — statement limit
  kw_anchor          — pattern anchor flag
  icn_frame_stack[]  — Icon/Raku local variable frames
  icn_frame_depth    — frame pointer
  icn_scan_subj/pos  — scan cursor state
  g_pl_trail         — Prolog trail (bindings made during execution)
  g_pl_env           — current Prolog clause environment
  g_pl_cut_flag      — Prolog cut flag
  g_pl_active        — Prolog active flag
```

### The solution: ExecSnapshot + restore between runs

```c
typedef struct {
    /* NV store snapshot — flat array of name→DESCR_t */
    NvPair  *pairs;   int npairs;
    /* Keyword state */
    int64_t  kw_stcount, kw_stlimit, kw_anchor;
    /* ICN frame stack — top frame only for step-mode */
    int      icn_frame_depth;
    /* Prolog trail mark — restore by unwinding */
    int      pl_trail_mark;
} ExecSnapshot;

void exec_snapshot_take(ExecSnapshot *s);
void exec_snapshot_restore(const ExecSnapshot *s);
```

`exec_snapshot_restore` calls `nv_reset()` then replays all pairs via
`NV_SET_fn`, resets keyword globals, unwinds ICN frame stack to depth 0,
unwinds Prolog trail to `pl_trail_mark`.

This is ~100 lines. `nv_reset()` already exists in the test stub —
add it to the production NV implementation in `snobol4.c`.

### Step-mode: one statement at a time

Run IR to stmt N (using step_limit = N). Snapshot. Restore.
Run SM to stmt N. Snapshot. Restore.
Run JIT to stmt N. Snapshot. Restore.
Compare all three snapshots.

Each executor gets a `step_limit` parameter. IR uses a counter in
`execute_program()`. SM uses `SM_STNO` count in `sm_interp_run()`.
JIT emits a check at each statement boundary in the trampoline.

### Future upgrade: Option B (shadow structs)

Long-term, wrapping all mutable globals in an `ExecState` struct and
passing `ExecState*` to each executor enables true parallel execution
on separate threads and makes the implicit shared interface explicit.
This is a significant refactor — after the monitor works with snapshot/restore.

---

## Steps

### Phase 1 — NV store reset + snapshot

- [x] **IM-1** — Add `nv_reset()` and `nv_snapshot()` / `nv_restore()` to
  the production NV store in `snobol4.c`.
  ```c
  void    nv_reset(void);                          /* clear all variables */
  int     nv_snapshot(NvPair **out);               /* returns count */
  void    nv_restore(const NvPair *pairs, int n);  /* replay via NV_SET_fn */
  ```
  Gate: make scrip clean; PASS=31 FAIL=0; nv_reset() clears all variables.

- [x] **IM-2** — Write `ExecSnapshot` struct and `exec_snapshot_take()` /
  `exec_snapshot_restore()` in `src/driver/sync_monitor.c`.
  Captures: NV pairs, kw_stcount, kw_stlimit, kw_anchor, icn_frame_depth,
  pl_trail_mark. Restore: nv_reset + replay, reset keywords, unwind frames.
  Gate: take snapshot, mutate state, restore, confirm state matches original.

### Phase 2 — Step-mode for all three executors

- [x] **IM-3** — Add `step_limit` to `execute_program()` in `interp.c`.
  When `step_limit > 0`: stop after exactly `step_limit` statements.
  Use a flag: `int g_ir_step_limit = 0; int g_ir_steps_done = 0;`
  After each stmt: if `g_ir_steps_done++ >= g_ir_step_limit` longjmp out.
  Gate: `execute_program_steps(prog, 1)` executes exactly 1 statement.

- [x] **IM-4** — Add `step_limit` to `sm_interp_run()` in `sm_interp.c`.
  `SM_STNO` already fires per statement — add step counter there.
  Gate: `sm_interp_run_steps(prog, st, 1)` executes exactly 1 statement.

- [ ] **IM-5** — Add step limit to JIT path in `sm_codegen.c`.
  JIT emits a call to a C trampoline at each `SM_STNO` boundary.
  Trampoline checks step counter and longjmps out when reached.
  Gate: `jit_run_steps(prog, 1)` executes exactly 1 statement.

### Phase 3 — Sync comparator

- [ ] **IM-6** — Write `sync_monitor_run(Program *prog, int verbose)`.
  For each statement N = 1..nstmts:
    1. `exec_snapshot_restore(&baseline)` — reset to clean state
    2. `execute_program_steps(prog, N)` → take `ir_snap`
    3. `exec_snapshot_restore(&baseline)`
    4. `sm_interp_run_steps(prog, st, N)` → take `sm_snap`
    5. `exec_snapshot_restore(&baseline)`
    6. `jit_run_steps(prog, N)` → take `jit_snap`
    7. Compare ir_snap vs sm_snap vs jit_snap via `nv_snapshot_diff()`
    8. On divergence: print report, return stmt N
  Returns 0 if all agree throughout, stmt number of first divergence otherwise.
  Gate: runs correctly on a pure-SNO program that passes all three modes.

- [ ] **IM-7** — Wire `--monitor` flag in `scrip.c` main().
  ```
  ./scrip --monitor file.sno
  ./scrip --monitor file.pl
  ./scrip --monitor file.icn
  ```
  Gate: `./scrip --monitor test/sno/hello.sno` exits 0.

### Phase 4 — Divergence reporting

- [ ] **IM-8** — Rich divergence report.
  ```
  DIVERGE at stmt 14 [label: FOO, line 42]
    IR:  X = "hello", Y = 42, last_ok = 1
    SM:  X = "hello", Y = 43, last_ok = 1   ← Y differs
    JIT: X = "hello", Y = 43, last_ok = 1
  ```
  Gate: introduce deliberate bug in sm_interp.c, --monitor finds it.

- [ ] **IM-9** — Label path tracing.
  Track sequence of labels reached by each executor in the snapshot.
  ```
  IR  path: [START] → [LOOP] → [MATCH]
  SM  path: [START] → [LOOP] → [NOMATCH]  ← diverged here
  ```
  Gate: label path printed correctly for branching programs.

### Phase 5 — All-language support

- [ ] **IM-10** — ICN frame locals in snapshot.
  For Icon/Raku: include `ICN_CUR.env[0..env_n]` in snapshot, named
  from `icn_proc_table[icn_frame_depth-1]`.
  Gate: `./scrip --monitor file.icn` shows Icon local variables.

- [ ] **IM-11** — Prolog trail state in snapshot.
  For Prolog: include bound variables from `g_pl_env` in snapshot.
  Gate: `./scrip --monitor file.pl` shows Prolog bound variables.

- [ ] **IM-12** — Write `scripts/test_monitor_inproc_all_langs.sh`.
  Runs --monitor on one program per language. Gate: all exit 0 (modes agree)
  for known-good programs; reports divergence for known-broken programs.

---

## Replaces

| Old script | Replaced by |
|-----------|-------------|
| `test_monitor_2way_spitbol_vs_ir.sh` | `--monitor` (IR vs SM vs JIT, in-process) |
| `test_monitor_3way.sh` | `--monitor` |
| `test_monitor_5way_ipc.sh` | `--monitor` |
| `test_monitor_sync_step.sh` | `--monitor` step mode |
| External diff files | NV snapshot diff in-memory |

Note: SPITBOL oracle comparison is different — that compares against an
external ground truth and is still valuable. `--monitor` compares our
three internal modes against each other.

---

## Key files

| File | Role |
|------|------|
| `src/driver/interp.c` | IR executor — add hook at stmt loop |
| `src/runtime/x86/sm_interp.c` | SM executor — hook at SM_STNO |
| `src/runtime/x86/sm_codegen.c` | JIT executor — hook trampoline |
| `src/driver/sync_monitor.c` | New: comparator + step driver |
| `src/driver/sync_monitor.h` | New: public interface |
| `src/driver/scrip.c` | Add --monitor flag dispatch |

---

## Invariants

- `g_sync_hook = NULL` in all production paths — zero overhead.
- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every step.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=31
```

---

## Current state (2026-04-14, one4all HEAD 38470db1)

IM-1 through IM-4 complete. IM-5 through IM-12 open.

Pre-existing build breakage also fixed this session:
- sm_lower.c: old EKind names renamed to current ir.h names; stale duplicate
  case blocks removed from lower_expr() switch.
- Makefile: added icn_runtime.c, pl_runtime.c, rebus frontend files;
  excluded rebus_main.c (has own main()).

Next: IM-5 — JIT step limit in sm_codegen.c (emit C trampoline call at each
SM_STNO boundary; check g_jit_step_limit; longjmp to g_jit_step_jmp when
reached). Then IM-6: sync_monitor_run() comparator loop in sync_monitor.c.
