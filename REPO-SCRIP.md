# REPO-SCRIP.md — SCRIP

**What:** All 6 frontends × 6 backends in one compiler/interpreter/runtime.
**Repo:** `snobol4ever/SCRIP`

---

## Session Start

```bash
# Git identity — always first
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"

# Clone repos (adjust to your goal)
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/SCRIP.git /home/claude/SCRIP
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus.git /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64.git /home/claude/x64
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4.git /home/claude/csnobol4
```

**Note on `x64`:** `snobol4ever/x64` ships with a prebuilt SPITBOL binary at `bin/sbl`. The clone above IS the install — no build step needed for routine validation. `build_spitbol_oracle.sh` (listed in every Session Setup category below) detects the prebuilt binary and SKIPs the build, so it's safe to keep in the setup pipeline; it only ever rebuilds if you've intentionally removed the binary to patch SPITBOL itself.

**Build — run exactly what your goal's `## Session Setup` section lists. No more.**

All scripts are in `/home/claude/SCRIP/scripts/`. Each is idempotent.

---

## Session Setup

Run exactly the scripts listed in the Goal file's `## Session Setup` section.
If a Goal file has no `## Session Setup` yet, use the matching category below.

### Interp / compiler goals (scrip, IR, SM, ASM backends)
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

### Interp + cross-check goals (needs both oracles)
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

### Silly / Monitor goals (CSNOBOL4 is sole oracle for Silly)
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_monitor_ipc_shared_library.sh
bash /home/claude/SCRIP/scripts/build_ss_monitor_harness.sh
```

### JVM goals
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/install_java_and_jasmin.sh
```

### Full one-shot install (not for per-goal sessions)
```bash
bash /home/claude/SCRIP/scripts/install_everything_full_stack.sh
```

### After editing .y/.l parser/lexer sources
```bash
bash /home/claude/SCRIP/scripts/regenerate_parser_and_lexer_from_sources.sh
# then rebuild:
bash /home/claude/SCRIP/scripts/build_scrip.sh
```


---

## Build

```bash
cd /home/claude/SCRIP && git pull --rebase

# scrip:
make scrip

# Silly SNOBOL4:
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be zero errors, zero warnings — required before every commit
```

---

## Test gates

**smoke (3 programs, all pass = build is sane):**
```bash
bash test/smoke.sh
```

**regression (full corpus vs .ref, interpreter mode):**
```bash
CORPUS=/home/claude/corpus bash test/regression.sh
# baseline: PASS=41/149
```

**crosscheck (all backends — x86, JVM, NET, WASM — same programs, outputs must agree):**
```bash
CORPUS=/home/claude/corpus bash test/crosscheck.sh
```

**Silly build gate (before every commit):**
```bash
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
```

---

## Oracle

**Primary oracle** — SPITBOL x64: `/home/claude/x64/bin/sbl`
Build: `bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh`
Derive .ref: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno`

**Second oracle** — CSNOBOL4: `/home/claude/csnobol4/snobol4`
Build: `bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh`
Silly exception: CSNOBOL4 is sole oracle for Silly goals (SS-MONITOR, GOAL-SILLY-*).

---

## Key source paths

| Path | What |
|------|------|
| `src/frontend/snobol4/CMPILE.c` | SNOBOL4 parser |
| `src/ast/ast.h` | shared AST node type (tree_t / tree_e) |
| `src/driver/scrip.c` | unified scrip executable |
| `src/lower/lower.c` | AST → SM_Program compiler pass |
| `src/lower/sm_prog.h` | SM_Program flat instruction array |
| `src/lower/scrip_ir.h` | IR_prog_t / IR_t DCG node types |
| `src/lower/ir_exec.c` | DCG graph-walk executor |
| `src/lower/lower_pat_dcg.c` | build IR_prog_t from pattern tree_t |
| `src/processor/sm_interp.c` | mode-2 SM C dispatch loop |
| `src/processor/sm_jit_interp.c` | mode-3 JIT runner |
| `src/processor/bb_broker.c` | unified Byrd box broker |
| `src/processor/bb_pool.c` | mmap pool for binary Byrd boxes |
| `src/emitter/emit_core.c` | x86 byte/label/patch primitives |
| `src/emitter/emit_bb.c` | BB box x86 templates |
| `src/emitter/emit_sm.c` | SM opcode x86 templates |
| `src/runtime/snobol4/snobol4.c` | runtime (TRACE, comm_var, monitor hooks) |
| `src/runtime/snobol4/stmt_exec.c` | 5-phase statement executor |
| `src/runtime/snobol4/descr.h` | DESCR_t universal value type |
| `src/runtime/interp/` | Icon / Prolog / Raku interpreter runtimes |
| `src/runtime/rt/rt.c` | libscrip_rt.so (mode-4 ABI) |
| `src/silly/` | Silly SNOBOL4 faithful C rewrite |
| `test/monitor/` | sync-step monitor infrastructure |

---

## Snocone front-end

See `ARCH-SNOCONE.md` for the Snocone language spec, lexer/grammar
implementation map, and full smoke gate. Below is just the per-
session smoke gate (the minimum a Snocone session runs before
committing):

```bash
bash scripts/test_smoke_snocone.sh                 # PASS=5 FAIL=0
bash scripts/test_beauty_snocone_all_modes.sh      # PASS=42 FAIL=0 SKIP=3
bash scripts/test_smoke_unified_broker.sh          # PASS=49 FAIL=0
```

The 3 SKIP rows in `test_beauty_snocone_all_modes.sh` are
`beauty.sc` self-host across the three modes — gated on
GOAL-SNOCONE-BEAUTY SB-6 until that goal closes.

---

## Silly SNOBOL4 — cherry-picks from SCRIP

Files in `SCRIP/src/runtime/snobol4/` with well-tested logic to adapt.
Adapt, don't copy verbatim — SCRIP uses Boehm GC + 64-bit; silly uses arena + 32-bit.

| SCRIP file | Useful for | Adaptation needed |
|---|---|---|
| `argval.c` | VARVAL_fn, INTVAL_fn, PATVAL_fn logic | remove GC_strdup, use arena; int32_t not int64_t |
| `nmd.c` | NAM_save/NAM_push/NAM_commit/NAM_discard design | remove GC_MALLOC, use arena; Name_entry → `nam_entry_t` |
| `invoke.c` | INVOKE_fn / APPLY_fn dispatch pattern | adapt to fn_entry_t table with arena ptrs |
| `sil_macros.h` | MOVD, SETAC, type-test macros | verify against our DESCR_t layout |
| `snobol4.c` | arithmetic, string ops, keyword logic | heavy adaptation — different DESCR layout |

---

## scrip modes

| Flag | Mode |
|------|------|
| `scrip --interp file.sno` | IR tree-walk interpreter |
| `scrip --interp file.sno` | Stack machine (default) |
| `scrip --gen file.sno` | In-memory x86 generation |

---

## Monitor infrastructure

The sync-step monitor harnesses compare multiple runtimes event-by-event.
SPITBOL is primary oracle; CSNOBOL4 is second oracle (added as participant 5 below).

```bash
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty_suite
bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_trace_driver.sno
```

### Participant table (up to 6-way)

| # | Participant | Role | Binary |
|---|-------------|------|--------|
| 1 | SPITBOL x64 | **Primary oracle** | `/home/claude/x64/bin/sbl` |
| 2 | SCRIP ASM | Target | `scrip --gen` |
| 3 | SCRIP JVM | Target | `scrip --jvm` |
| 4 | SCRIP NET | Target | `scrip --net` |
| 5 | CSNOBOL4 2.3.3 | **Second oracle** | `/home/claude/csnobol4/snobol4` |
| 6 | Silly SNOBOL4 | Silly target | `/tmp/silly-snobol4` |

SPITBOL IPC: `x64/monitor_ipc_spitbol.so`
CSNOBOL4 IPC: `csnobol4/monitor_ipc_csnobol4.so` (same ABI as SPITBOL IPC)
scrip IPC: C-native in `snobol4.c` (`comm_var()`, `comm_stno()`, `monitor_fd`/`monitor_ack_fd`)

---

## Tools by backend

| Backend | Tools |
|---------|-------|
| x86 | `nasm`, `libgc-dev` |
| JVM | `default-jdk`, `jasmin.jar` (bundled) |
| .NET | `mono-complete` |
| WASM | `wabt` |
| C | gcc only |
| JS | node (pre-installed) |

Never install bison or flex — generated parser files are committed.

SPITBOL is the primary oracle. See `## Session Setup` above for per-goal script lists.
