# REPO-one4all.md — one4all

**What:** All 6 frontends × 6 backends in one compiler/interpreter/runtime.
**Repo:** `snobol4ever/one4all`

---

## Session Start

```bash
# Git identity — always first
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"

# Clone repos (adjust to your goal)
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/one4all.git /home/claude/one4all
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus.git /home/claude/corpus
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64.git /home/claude/x64
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4.git /home/claude/csnobol4
```

**Build — run exactly what your goal's `## Session Setup` section lists. No more.**

All scripts are in `/home/claude/one4all/scripts/`. Each is idempotent.

---

## Session Setup

Run exactly the scripts listed in the Goal file's `## Session Setup` section.
If a Goal file has no `## Session Setup` yet, use the matching category below.

### Interp / compiler goals (scrip, IR, SM, ASM backends)
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

### Interp + cross-check goals (needs both oracles)
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

### Silly / Monitor goals (CSNOBOL4 is sole oracle for Silly)
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_monitor_ipc_shared_library.sh
bash /home/claude/one4all/scripts/build_ss_monitor_harness.sh
```

### JVM goals
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/install_java_and_jasmin.sh
```

### Full one-shot install (not for per-goal sessions)
```bash
bash /home/claude/one4all/scripts/install_everything_full_stack.sh
```

### After editing .y/.l parser/lexer sources
```bash
bash /home/claude/one4all/scripts/regenerate_parser_and_lexer_from_sources.sh
# then rebuild:
bash /home/claude/one4all/scripts/build_scrip.sh
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
Build: `bash /home/claude/one4all/scripts/build_spitbol_oracle.sh`
Derive .ref: `/home/claude/x64/bin/sbl -b file.sno > file.ref`
With includes: `/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno`

**Second oracle** — CSNOBOL4: `/home/claude/csnobol4/snobol4`
Build: `bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh`
Silly exception: CSNOBOL4 is sole oracle for Silly goals (SS-MONITOR, GOAL-SILLY-*).

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

## Snocone front-end

**Status (LS-6 in `GOAL-SNOCONE-LANG-SPACE.md`):** the post-LS-4
Flex+Bison front-end is the only Snocone front-end. It is byte-
equivalent to SPITBOL on the full 14-subsystem beauty suite
across all three scrip modes (`--ir-run` / `--sm-run` / `--jit-run`)
— PASS=42 FAIL=0 SKIP=3 on `test_beauty_snocone_all_modes.sh`.

**Goal:** Snocone is Andrew Koenig's `.sc` self-host operator set,
minus `&&` / `||` / `%`, plus C-style structured control flow,
plus SPITBOL space-as-concat. **A SPITBOL program that does not
itself use `&&` / `||` / `%` as binary operators, and that uses `;`
statement terminators with `name:` label syntax, runs unchanged
under Snocone.** This functional-superset guarantee is a hard
invariant. See `RULES.md` "Snocone language facts" for the binding
working rules.

| Path | What |
|------|------|
| `src/frontend/snocone/snocone.y` | Bison grammar — current name `snocone_parse.y` after LS-4.cn rename |
| `src/frontend/snocone/snocone_parse.tab.{c,h}` | Generated parser tables |
| `src/frontend/snocone/snocone_lex.c` | Threaded-code FSM lexer (LS-3.f.1 — replaced flex output after `{W}OP{W}` envelope hangs) |
| `src/frontend/snocone/snocone_lex.h` | Public FSM API |
| `src/frontend/snocone/snocone_driver.{c,h}` | scrip-side entry point — calls `snocone_parse_program()` |
| `archive/snocone_lower.{c,h}` | Legacy lowering (archived in LS-4.k) |
| `archive/snocone_control.{c,h}` | Legacy control-flow lowering (archived in LS-4.k) |

**Lexer.** Single-pass threaded-code FSM in `snocone_lex.c` — one
C function `sc_lex_next(LexCtx *ctx)` whose body is a graph of
labelled `Label: action; goto NEXT;` blocks. No `switch` / `for` /
`while` / `do-while` in the FSM body (per Lon directive — clean
emission technique mirroring `snobol4.l`'s `{W}OP{W}` envelope
pattern). The FSM maintains a previous-token state and emits a
synthetic `T_CONCAT` token when a value-yielding token is followed
by another with whitespace between — that is the space-as-concat
implementation. Comments fold into whitespace via `S_LCOMMENT` /
`S_BCOMMENT` sub-FSMs. Token names follow the `T_<arity><charname>`
scheme matching `snobol4.tab.h` — `T_2EQUAL` (`=`), `T_2DOT` (`.`),
`T_2DOLLAR` (`$`) for binary; `T_1*` for unary.

**Grammar.** Bison parser in `snocone_parse.y`, generated to
`snocone_parse.tab.{c,h}`. Bison reports 0 shift/reduce and 0
reduce/reduce conflicts at every rung. Precedence declarations
match SPITBOL Manual Ch.15 priorities 0–13. Conditions of `if`,
`while`, `do/while`, `for`-test, `case` tag are SPITBOL backtracking
expressions — success/failure of the expression drives the branch.
Public entry: `CODE_t *snocone_parse_program(const char *src,
const char *filename)`.

**Build path.** `.l` and `.y` source edits require regeneration:

```bash
bash scripts/regenerate_parser_and_lexer_from_sources.sh
```

This regenerates `snocone_parse.tab.{c,h}` (also any other front-
end's `.tab.{c,h}` and `.lex.c`). Per `RULES.md` "Editing `.y` or
`.l` files," the `.y`/`.l` source AND the updated generated files
go in the **same commit** — never edit the generated files directly
for grammar or lexer logic. Generated files are checked in so
normal builds do not require bison/flex on the build machine; flex
and bison are installed via `scripts/install_system_packages.sh`
when a regeneration is needed.

**Smoke gate** (per-session, before every commit touching Snocone):

```bash
bash scripts/test_smoke_snocone.sh                 # PASS=5 FAIL=0
bash scripts/test_beauty_snocone_all_modes.sh      # PASS=42 FAIL=0 SKIP=3
bash scripts/test_smoke_unified_broker.sh          # PASS=49 FAIL=0
```

The 3 SKIP rows in `test_beauty_snocone_all_modes.sh` are
`beauty.sc` self-host across the three modes — gated on
GOAL-SNOCONE-BEAUTY SB-6.D until that goal closes.

---

## Silly SNOBOL4 — cherry-picks from one4all

Files in `one4all/src/runtime/snobol4/` with well-tested logic to adapt.
Adapt, don't copy verbatim — one4all uses Boehm GC + 64-bit; silly uses arena + 32-bit.

| one4all file | Useful for | Adaptation needed |
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
| `scrip --ir-run file.sno` | IR tree-walk interpreter |
| `scrip --sm-run file.sno` | Stack machine (default) |
| `scrip --gen file.sno` | In-memory x86 generation |

---

## Monitor infrastructure

The sync-step monitor harnesses compare multiple runtimes event-by-event.
SPITBOL is primary oracle; CSNOBOL4 is second oracle (added as participant 5 below).

```bash
INC=/home/claude/corpus/programs/snobol4/demo/inc
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
bash test/monitor/run_monitor_2way.sh $BEAUTY/beauty_trace_driver.sno
```

### Participant table (up to 6-way)

| # | Participant | Role | Binary |
|---|-------------|------|--------|
| 1 | SPITBOL x64 | **Primary oracle** | `/home/claude/x64/bin/sbl` |
| 2 | one4all ASM | Target | `scrip --gen` |
| 3 | one4all JVM | Target | `scrip --jvm` |
| 4 | one4all NET | Target | `scrip --net` |
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
