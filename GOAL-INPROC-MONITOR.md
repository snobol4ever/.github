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

## Architecture

```
Program *prog = parse(file);

SyncCtx ctx = {0};
ctx.hook = sync_compare;

// Thread 1 (or just sequential):
ir_run_with_hook(prog,  &ctx.ir_state,  ctx.hook);   // interp.c
sm_run_with_hook(prog,  &ctx.sm_state,  ctx.hook);   // sm_interp.c
jit_run_with_hook(prog, &ctx.jit_state, ctx.hook);   // sm_codegen.c

// After each statement, hook fires for that executor.
// Comparator waits until all three have fired for stmt N, then diffs.
```

Single-threaded first implementation: run all three sequentially stmt-by-stmt,
stepping each one statement at a time using a step-mode flag.

---

## Steps

### Phase 1 — Per-statement hook in IR interpreter

- [ ] **IM-1** — Add `g_sync_hook` function pointer to `interp.c`.
  ```c
  extern sync_hook_fn g_sync_hook;   /* NULL in production */
  extern void        *g_sync_arg;
  ```
  In `execute_program()` statement loop, after each stmt executes:
  ```c
  if (g_sync_hook) {
      SyncState ss = { stno, last_ok, label_idx };
      g_sync_hook(&ss, g_sync_arg);
  }
  ```
  Gate: make scrip clean; PASS=31 FAIL=0; g_sync_hook=NULL is zero-overhead.

- [ ] **IM-2** — Add `g_sync_hook` to `sm_interp_run()` in `sm_interp.c`.
  `SM_STNO` already fires per statement — attach hook there.
  Gate: make scrip clean; PASS=31 FAIL=0.

- [ ] **IM-3** — Add `g_sync_hook` to `sm_codegen.c` JIT path.
  JIT emits a call to a C hook trampoline at each statement boundary.
  Gate: make scrip clean; --jit-run hello.sno still works.

### Phase 2 — NV store snapshot

- [ ] **IM-4** — Add `nv_snapshot(NvSnapshot *out)` to NV store.
  Captures all currently bound name→DESCR_t pairs into a flat array.
  ```c
  typedef struct { const char *name; DESCR_t val; } NvPair;
  typedef struct { NvPair *pairs; int n; } NvSnapshot;
  void nv_snapshot(NvSnapshot *out);
  void nv_snapshot_free(NvSnapshot *s);
  int  nv_snapshot_diff(const NvSnapshot *a, const NvSnapshot *b,
                        char *buf, size_t bufsz);
  ```
  Gate: make scrip clean.

### Phase 3 — Sync comparator

- [ ] **IM-5** — Write `src/driver/sync_monitor.c` + `sync_monitor.h`.
  ```c
  /* Run prog through all three modes, stepping stmt-by-stmt.
   * On first divergence: print statement number, label, differing vars.
   * Returns 0 if all three agree throughout. */
  int sync_monitor_run(Program *prog, SyncMonitorOpts *opts);
  ```
  Single-threaded: IR runs to stmt N, takes snapshot. SM runs to stmt N,
  takes snapshot. JIT runs to stmt N, takes snapshot. Compare all three.
  On divergence: print report, return 1.

  Step-mode implementation: add `step_limit` to each executor so it runs
  exactly N statements then suspends (via longjmp or return).
  Gate: sync_monitor_run on a pure-SNO program that passes all three modes
  returns 0.

- [ ] **IM-6** — Wire `--monitor` flag in `scrip.c` main().
  ```
  ./scrip --monitor file.sno
  ./scrip --monitor file.pl
  ./scrip --monitor file.icn
  ```
  Calls `sync_monitor_run(prog, &opts)`.
  Opts: `--monitor-vars X,Y,Z` — only track named variables.
  Gate: `./scrip --monitor test/sno/hello.sno` exits 0 (all agree).

### Phase 4 — Divergence reporting

- [ ] **IM-7** — Rich divergence report format.
  ```
  DIVERGE at stmt 14 [label: FOO]
    IR:  X = "hello", Y = 42, last_ok = 1
    SM:  X = "hello", Y = 43, last_ok = 1   ← Y differs
    JIT: X = "hello", Y = 43, last_ok = 1
  ```
  Print all vars that differ between any two executors.
  Print the STMT_t source if available (label + line number).
  Gate: deliberately introduce a bug in sm_interp.c, run --monitor,
  verify it points to the correct statement.

- [ ] **IM-8** — Label path tracing.
  Track sequence of labels reached by each executor.
  On divergence: print label path up to that point.
  ```
  IR  path: [START] → [LOOP] → [MATCH] → [END]
  SM  path: [START] → [LOOP] → [NOMATCH] → ...   ← diverged here
  ```
  Gate: label path printed correctly for a program with multiple branches.

### Phase 5 — All-language support

- [ ] **IM-9** — Wire ICN frame state into snapshot.
  For Icon/Raku programs: include `icn_frame_stack` top-of-stack local vars
  in the NV snapshot. `ICN_CUR.env[i]` → name from `icn_proc_table`.
  Gate: `./scrip --monitor file.icn` works.

- [ ] **IM-10** — Wire Prolog trail state into snapshot.
  For Prolog programs: include bound variables from `g_pl_env` in snapshot.
  Gate: `./scrip --monitor file.pl` works.

- [ ] **IM-11** — Write `scripts/test_monitor_inproc_snobol4.sh`.
  Runs --monitor on beauty drivers and the known-failing programs.
  Gate: SNOBOL4 programs that pass all three modes exit 0.
  Gate: Programs known to diverge are caught and reported.

- [ ] **IM-12** — Write `scripts/test_monitor_inproc_all_langs.sh`.
  Runs --monitor on one program per language.
  Gate: all programs that pass all three modes exit 0.

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

## Current state (2026-04-14, one4all HEAD 11d9e9c9)

IM-1 through IM-12 all open.
Next: IM-1 — add g_sync_hook to execute_program() statement loop.
