# REPO-one4all.md — one4all

**What:** All 6 frontends × 6 backends in one compiler/interpreter/runtime.
**Repo:** `snobol4ever/one4all`

---

## Session Start

```bash
# Git identity — always first
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"

# Clone repos
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/one4all.git /home/claude/one4all
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus.git /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64.git /home/claude/x64

# Install tools (adjust for your goal's backend)
apt-get install -y gcc make libgc-dev    # always needed for scrip
# x86:  apt-get install -y nasm
# JVM:  apt-get install -y default-jdk
# .NET: apt-get install -y mono-complete
# WASM: apt-get install -y wabt

# Build scrip
cd /home/claude/one4all && make scrip
```

---

## Build

```bash
cd /home/claude/one4all && git pull --rebase

# scrip:
make scrip

# Silly SNOBOL4:
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
# must be zero errors, zero warnings — required before every commit
```

---

## Test gates

**scrip broad corpus:**
```bash
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
# baseline: PASS=193/203
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
# baseline: 14/19
```

**Silly build gate (before every commit):**
```bash
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -E "error:|warning:"
```

---

## Oracle

SPITBOL x64: `/home/claude/x64/bin/sbl`
Derive .ref: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno`

**Silly exception:** CSNOBOL4 is oracle for Silly goals only. See above for build.

---

## Key source paths

| Path | What |
|------|------|
| `src/frontend/snobol4/CMPILE.c` | SNOBOL4 parser |
| `src/driver/scrip.c` | unified scrip executable |
| `src/runtime/snobol4/snobol4.c` | runtime (TRACE, comm_var, monitor hooks) |
| `src/runtime/snobol4/stmt_exec.c` | 5-phase statement executor |
| `src/runtime/asm/bb_pool.c` | mmap pool for binary Byrd boxes |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations |
| `src/silly/` | Silly SNOBOL4 faithful C rewrite |
| `test/monitor/` | sync-step monitor infrastructure |

---

## scrip modes

| Flag | Mode |
|------|------|
| `scrip --ir-run file.sno` | IR tree-walk interpreter |
| `scrip --sm-run file.sno` | Stack machine (default) |
| `scrip --gen file.sno` | In-memory x86 generation |

---

## Monitor infrastructure

```bash
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_trace_driver.sno
```

SPITBOL IPC: `x64/monitor_ipc_spitbol.so`
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
