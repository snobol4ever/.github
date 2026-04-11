# REPO-one4all.md — one4all

**What:** All 6 frontends × 6 backends in one compiler/interpreter/runtime.
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/one4all.git /home/claude/one4all`
**Path:** `/home/claude/one4all`

---

## Build

```bash
cd /home/claude/one4all && git pull --rebase
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"

# scrip (unified executable — default mode is --sm-run):
make scrip

# Silly SNOBOL4:
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be zero errors, zero warnings
```

---

## Test gates

**scrip broad corpus:**
```bash
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
# current baseline: PASS=193/203
```

**scrip beauty suite (19 drivers):**
```bash
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
INC=/home/claude/corpus/programs/snobol4/demo/inc
PASS=0; FAIL=0
for sno in "$BEAUTY"/beauty_*_driver.sno; do
    name=$(basename "$sno" .sno); ref="$BEAUTY/${name}.ref"
    [ ! -f "$ref" ] && continue
    got=$(SNO_LIB="$INC" timeout 10 ./scrip --ir-run "$sno" 2>/dev/null)
    [ "$got" = "$(cat $ref)" ] && { echo "PASS $name"; PASS=$((PASS+1)); } \
                               || { echo "FAIL $name"; FAIL=$((FAIL+1)); }
done; echo "--- PASS=$PASS FAIL=$FAIL"
# current baseline: 14/19
```

**Silly SNOBOL4 build gate:**
```bash
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be clean before every commit
```

---

## Tools by backend

| Backend | Tools needed |
|---------|-------------|
| x86 | `nasm`, `libgc-dev` |
| JVM | `java`, `javac`, `jasmin.jar` (bundled) |
| .NET | `mono`, `ilasm` |
| JS | node (pre-installed) |
| WASM | `wabt` (`apt-get install -y wabt`) |
| C | gcc only |

Install: `apt-get install -y <tools>`
Never install bison or flex — generated parser files are committed.

---

## Oracle

SPITBOL x64: `/home/claude/x64/bin/sbl`
Clone: `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64.git /home/claude/x64`

**Silly SNOBOL4 exception:** CSNOBOL4 is the oracle for Silly goals only.
```
/home/claude/work/snobol4-2.3.3/snobol4     # CSNOBOL4 binary
/home/claude/work/snobol4-2.3.3/v311.sil    # SIL source (12,293 lines)
/home/claude/work/snobol4-2.3.3/snobol4.c   # generated C ground truth (14,293 lines, 383 fns)
```

---

## Key source paths

| Path | What |
|------|------|
| `src/frontend/snobol4/CMPILE.c` | SNOBOL4 parser |
| `src/driver/scrip.c` | unified scrip executable |
| `src/runtime/snobol4/snobol4.c` | SNOBOL4 runtime (TRACE, comm_var, monitor hooks) |
| `src/runtime/snobol4/stmt_exec.c` | 5-phase statement executor |
| `src/runtime/asm/bb_pool.c` | mmap pool for binary Byrd boxes |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations |
| `src/silly/` | Silly SNOBOL4 faithful C rewrite |
| `test/monitor/` | sync-step monitor infrastructure |
| `test/monitor/monitor_sync.py` | 2-participant barrier controller |
| `test/monitor/inject_traces.py` | trace preamble injector |

---

## Silly SNOBOL4 specifics

**What:** Ground-up faithful C rewrite of v311.sil (CSNOBOL4 2.3.3, Phil Budne).
**Model:** 32-bit on 64-bit platform. Arena model (128MB mmap slab). No Boehm GC.
- `int_t = int32_t`, `real_t = float`
- `A2P(off)` = pointer from arena offset; `P2A(ptr)` = offset from pointer
- Zero gotos. `if`/`while`/`for`/`switch` only.
- SIL RCALL → C function call. SIL RRTURN → `return`.
- Pattern backtracking: C call stack + `setjmp`/`longjmp` in `sil_scan.c`
- BLOCKS (v311.sil lines 7038–10208): NOT IMPLEMENTED, skipped in all passes

**Three-way diff rule:** v311.sil + snobol4.c + our code, all three simultaneously.
snobol4.c is ground truth — it resolves all SIL branch ambiguity.

---

## scrip modes

| Flag | Mode |
|------|------|
| `scrip --ir-run file.sno` | IR interpreter (tree-walk, correctness reference) |
| `scrip --sm-run file.sno` | Stack machine interpreter (default) |
| `scrip --gen file.sno` | In-memory x86 code generation |

---

## Monitor infrastructure (for GOAL-SCRIP-BEAUTY)

```bash
# 2-way monitor: SPITBOL vs scrip --ir-run
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_trace_driver.sno

# Inject traces into a .sno file:
python3 test/monitor/inject_traces.py file.sno test/monitor/tracepoints.conf > instrumented.sno
```

SPITBOL IPC: `x64/monitor_ipc_spitbol.so` (LOAD() path)
scrip IPC: C-native in `snobol4.c` (`comm_var()`, `comm_stno()`, `monitor_fd`/`monitor_ack_fd`)
