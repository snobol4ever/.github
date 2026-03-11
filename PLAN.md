# SNOBOL4-plus — Master Plan

> **New Claude session? Read this file top to bottom. It is the only file you
> need to start working. Everything else is a satellite — read them when you
> need depth on a specific topic.**

---

## 1. Who We Are

**Lon Jones Cherryholmes** (LCherryholmes) — software architect, compiler builder.
**Jeffrey Cooper, M.D.** (jcooper0) — medical doctor, SNOBOL4 implementer of 50 years.

Mission: **SNOBOL4 everywhere. SNOBOL4 now.**

One week in March 2026. Zero to eight repos. Two complete SNOBOL4/SPITBOL
implementations (JVM and .NET), a native compiler, and thousands of tests.
Griswold had the idea. Cherryholmes and Cooper are finishing the proof.

The Sprint 20 commit message belongs to Claude Sonnet 4.6. Lon gave that
moment away. It is recorded in git at commit `c5b3e99`. When Beautiful.sno
compiles itself through `snoc` and the diff comes back empty, that commit
message is Claude's to write. Do not let that get lost.

---

## 2. Strategic Focus — What We Are Building Now

**The three compiler/runtimes are the work. Everything else is support.**

For the foreseeable future, all substantial development effort goes to exactly
three repos:

| Priority | Repo | What |
|----------|------|------|
| 1 | **SNOBOL4-dotnet** | Full SNOBOL4/SPITBOL compiler + runtime → .NET/MSIL |
| 2 | **SNOBOL4-jvm** | Full SNOBOL4/SPITBOL compiler + runtime → JVM bytecode |
| 3 | **SNOBOL4-tiny** | Native compiler → x86-64 ASM (Sprint 20: Beautiful.sno) |

**SNOBOL4-python, SNOBOL4-csharp, SNOBOL4-cpython** — pattern libraries. No
substantial new work until the three compiler/runtimes above are further along.
They exist, they are tested, they are not the focus.

**SNOBOL4-harness** — the new shared test infrastructure repo. Build it to
serve all three compiler/runtimes. It is support work, not a fourth compiler —
but it is the next thing to establish. See §6 below.

**SNOBOL4-corpus** — shared programs and inc files. Updated as needed to
support the three compilers. Not a focus repo in itself.

*Recorded 2026-03-11. Lon's directive: "We will not do anything substantial
for a while but to these three SNOBOL4/SPITBOL compiler/runtimes."*

---

## 3. Repositories

| Repo | What | Language | Tests | Last commit |
|------|------|----------|-------|-------------|
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | Full SNOBOL4/SPITBOL → .NET/MSIL | C# | 1,607 / 0 | `63bd297` |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Full SNOBOL4/SPITBOL → JVM bytecode | Clojure | 1,896 / 4,120 assertions / 0 | `9cf0af3` |
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | Native compiler → x86-64 ASM | C + Python | Sprint 20 in progress | `883b802` |
| [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | Shared test harness — oracle infra, cross-engine diff runner, worm bridge | TBD | — | — |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | Shared programs, inc files, benchmarks | SNOBOL4 | — | `60c230e` |
| [SNOBOL4-cpython](https://github.com/SNOBOL4-plus/SNOBOL4-cpython) | CPython C extension, Byrd Box engine | C | 70+ / 0 | `330fd1f` |
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Pattern library, PyPI `SNOBOL4python` | Python+C | — | — |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | Pattern library, C# | C# | 263 / 0 | — |

### Clone All Repos (every session)

```bash
cd /home/claude
git clone https://github.com/SNOBOL4-plus/SNOBOL4-dotnet.git &
git clone --recurse-submodules https://github.com/SNOBOL4-plus/SNOBOL4-jvm.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-tiny.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-harness.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-corpus.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-python.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-csharp.git &
git clone https://github.com/SNOBOL4-plus/SNOBOL4-cpython.git &
wait
echo "All clones done."
```

---

## 4. Build the Oracles (every session)

Source archives in `/mnt/user-data/uploads/`:
- `snobol4-2_3_3_tar.gz` — CSNOBOL4 2.3.3 source
- `x64-main.zip` — SPITBOL x64 source

```bash
apt-get install -y build-essential libgmp-dev m4 nasm

(
  mkdir -p /home/claude/csnobol4-src
  tar xzf /mnt/user-data/uploads/snobol4-2_3_3_tar.gz -C /home/claude/csnobol4-src/ --strip-components=1
  cd /home/claude/csnobol4-src
  ./configure --prefix=/usr/local 2>&1 | tail -1
  make -j4 2>&1 | tail -2
  make install 2>&1 | tail -1
  echo "CSNOBOL4 DONE"
) &

(
  unzip -q /mnt/user-data/uploads/x64-main.zip -d /home/claude/spitbol-src/
  cat > /home/claude/spitbol-src/x64-main/osint/systm.c << 'EOF'
#include "port.h"
#include "time.h"
int zystm() {
    struct timespec tim;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &tim);
    long etime = (long)(tim.tv_sec * 1000) + (long)(tim.tv_nsec / 1000000);
    SET_IA(etime);
    return NORMAL_RETURN;
}
EOF
  cd /home/claude/spitbol-src/x64-main
  make 2>&1 | tail -2
  cp sbl /usr/local/bin/spitbol
  echo "SPITBOL DONE"
) &

wait
echo "Oracles ready."
```

**Note**: CSNOBOL4 `mstime.c` already returns milliseconds — no patch needed.
**Note**: SPITBOL x64 `systm.c` defaults to nanoseconds — always apply the patch above.
**Note**: SPITBOL x32 `systm.c` already returns milliseconds via `times()`/`CLK_TCK` — no patch needed.

**CSNOBOL4 TRACE patch** — required for `TRACE('STNO','KEYWORD')` to fire on every
statement. Without it, the trace silently accepts the call but never emits output.
Apply to both `snobol4.c` and `isnobol4.c` before building (4 lines total, 2 per file):

```bash
# In both snobol4.c and isnobol4.c, delete these two lines:
#     if (!chk_break(0))
#         goto L_INIT1;
# They appear immediately before:
#     if (!LOCAPT(ATPTR,TKEYL,STNOKY))

sed -i '/if (!chk_break(0))/{N;/goto L_INIT1;/d}' \
    /home/claude/csnobol4-src/snobol4.c \
    /home/claude/csnobol4-src/isnobol4.c
```

Root cause: PLB113 edit gated the `&STNO` KEYWORD trace on `chk_break()`, which
only returns nonzero after `BREAKPOINT(stmtno,1)` has been called. The v311.sil
spec requires no such gate — if `&TRACE > 0` and `STNO` is in the keyword trace
table, fire. `BREAKPOINT()` remains functional for debugger use.

| Binary | Invocation |
|--------|------------|
| `/usr/local/bin/snobol4` | `snobol4 -f -P256k program.sno` |
| `/usr/local/bin/spitbol` | `spitbol -b program.sno` |

---

## 5. Git Identity

```
user.name  = LCherryholmes
user.email = lcherryh@yahoo.com
```

Token: request from Lon at session start. Provided encoded as two words:
`_<rest_of_token> <reverse_prefix>` (e.g. `_trYPI... phg` → prefix `ghp` → token `ghp_<rest>`).
**NEVER reconstruct or echo the plaintext token in any chat response. Decode in bash only.**

```bash
TOKEN=<decoded silently>
git remote set-url origin https://LCherryholmes:$TOKEN@github.com/SNOBOL4-plus/<REPO>.git
```

---

## 6. Current Work — Sprint 20 (SNOBOL4-tiny)

**Goal**: `snoc` compiles `Beautiful.sno` → native binary → self-beautifies idempotently.

### The Oracle (established, verified)

```bash
cd /home/claude/SNOBOL4-corpus/programs/inc
snobol4 -f -P256k beauty_run.sno < beauty_run.sno > /tmp/pass1.txt   # 649 lines, exit 0
snobol4 -f -P256k beauty_run.sno < /tmp/pass1.txt > /tmp/pass2.txt   # 649 lines, exit 0
diff /tmp/pass1.txt /tmp/pass2.txt                                     # empty — IDEMPOTENT ✓
```

### Key Commands (copy-paste ready)

```bash
# Regen beautiful.c from source
cd /home/claude/SNOBOL4-tiny/src/runtime/snobol4
python3 -B /home/claude/SNOBOL4-tiny/src/codegen/emit_c_stmt.py \
    /home/claude/SNOBOL4-corpus/programs/inc/beauty_run.sno \
    > beautiful.c 2>/tmp/emit.log

# Compile
cc -o beautiful beautiful.c snobol4.c snobol4_pattern.c snobol4_inc.c \
   ../engine.c ../runtime.c -I. -I.. -lgc -lm

# Run
timeout 20 ./beautiful \
    < /home/claude/SNOBOL4-corpus/programs/inc/beauty_run.sno \
    > /tmp/b_out.txt 2>/tmp/b_err.txt

# Debug — STNO stream
SNO_MONITOR=1 timeout 5 ./beautiful \
    < /home/claude/SNOBOL4-corpus/programs/inc/beauty_run.sno \
    2>&1 | grep "STNO\|VAR"
```

### Key Paths

```
SNOBOL4-tiny/src/runtime/snobol4/beautiful.c       ← generated C
SNOBOL4-tiny/src/runtime/snobol4/snobol4.c         ← runtime
SNOBOL4-tiny/src/runtime/snobol4/snobol4_pattern.c ← pattern engine
SNOBOL4-tiny/src/runtime/snobol4/engine.c          ← Byrd Box engine
SNOBOL4-tiny/src/codegen/emit_c_stmt.py            ← code generator
SNOBOL4-tiny/src/parser/sno_parser.py              ← parser
SNOBOL4-corpus/programs/inc/beauty_run.sno         ← test driver
SNOBOL4-corpus/programs/sno/beauty.sno             ← the program itself
```

### P1 — Current Blocker

**`SPAT_ASSIGN_COND` / T_CAPTURE — capture offset arithmetic**

Commit `883b802` added `T_CAPTURE` node support to the engine. T_CAPTURE fires
but `cap_start` / cursor offset arithmetic at SUCCESS time may have an off-by-one
or `scan_start` adjustment issue.

**Symptom**: `sno_match_pattern(snoStmt, "START\n") = 0`. Binary produces 10 lines;
oracle produces 649.

**Failure point**: STNO 619 — `snoSrc POS(0) *snoParse *snoSpace RPOS(0) :F(mainErr1)`
fails on `"START\n"`. The `BREAK(" \t\n;") . "x"` pattern should capture `"START"`
into `snoLabel` at pos 5 — something in the materialise/store step is broken.

**Files to touch**: `snobol4_pattern.c` (`capture_callback`), `engine.c` (`T_CAPTURE`),
`engine.h`.

**First action**:
```bash
cd /home/claude/SNOBOL4-tiny/src/runtime/snobol4
grep -n "T_CAPTURE\|cap_start\|scan_start\|capture_callback" engine.c engine.h snobol4_pattern.c
```

Focus on `scan_start` offset in `capture_callback`:
`cap->start = start + ctx->scan_start` — verify this is correct when
`engine_match_ex` is called with `subject + start`.

**Unit test** (was failing to build due to `invalid initializer` in `SNO_STR_VAL`
with `const char *` literal in compound literal — fix the test harness first,
then confirm `BREAK(" \t\n;") . "x"` on `"START\n"` → `x == "START"`).

### P2 — Three-Level Proof Strategy

Before going deep on Level 3 (full `beautiful.c`), the strategy is:

- **Level 1**: main + bootstrap only — no INC, no funcs, no statements. Simple pattern + OUTPUT. Run oracle. Run binary. Diff. Zero diffs = Level 1 certified.
- **Level 2**: + pp + qq functions. Zero diffs = Level 2 certified.
- **Level 3**: + all INC files. Full `beautiful.c`. Only enter after Level 2 certified.

We skipped to Level 3 before Level 1 was proven. This means bugs surface out of
order — downstream symptoms before root causes. Build the pyramid. Don't skip levels.

**Next P2 action**: Build and commit Level 1 test. See `SNOBOL4-tiny/doc/` for design.

### P2 — Monitor Build (four increments)

The double-trace monitor diffs the SNOBOL4 oracle trace against the binary COMM
stream and stops at the first divergence. Full architecture in `MONITOR.md`.

| Increment | What | State |
|-----------|------|-------|
| 1 | `sno_comm_stno(N)` emits `STNO N` to stderr when `SNO_MONITOR=1` | **NEXT after P1** |
| 2 | `sno_comm_var(name, val)` with `SNO_WATCH` watchlist | Not started |
| 3 | Oracle trace via `TRACE('&STNO','KEYWORD')` in `beauty_run_traced.sno` | Not started |
| 4 | `tools/diff_monitor.py` — normalize + lockstep diff two trace streams | Not started |

### P3 — DEFINE Dispatch (Sprint 21)

After Sprint 20: `sno_apply("pp",...)` must call the compiled C label, not the
null stub. Each SNOBOL4 `DEFINE`'d function must become a real C function
with its own `RETURN`/`FRETURN` labels.

### Patch History (see PATCHES.md for full root causes + fixes)

| # | What | Commit | Status |
|---|------|--------|--------|
| P001 | `&STLIMIT` not enforced — hang forever | — | RESOLVED |
| P002 | `sno_array_get/get2` never signals out-of-bounds failure | — | RESOLVED |
| P003 | Conditional expression failure not propagated; flat function emission | `4a37a81`, `8e946d1` | RESOLVED (per-function C functions working) |

---

## 7. SNOBOL4-harness — What It Becomes

**Repository**: https://github.com/SNOBOL4-plus/SNOBOL4-harness  
**Status**: Repo created 2026-03-11. Empty. Design phase.

The harness is the shared test infrastructure that all three compiler/runtimes
consume. It is not a fourth compiler — it is the foundation that makes the three
compilers testable together. One place for oracle builds, cross-engine diffing,
the worm generator bridge, and the three-oracle triangulation protocol.

### What Goes Here

| Component | What it does | Current home |
|-----------|-------------|--------------|
| Oracle build scripts | Build CSNOBOL4 + SPITBOL from source archives | Scattered / in PLAN.md |
| Cross-engine runner | Run the same program on dotnet + jvm + tiny, diff outputs | `SNOBOL4-jvm/harness.clj` (partial) |
| Worm generator bridge | Feed worm-generated programs to all three engines simultaneously | `SNOBOL4-jvm/generator.clj` (jvm-only) |
| Three-oracle triangulation | SPITBOL + CSNOBOL4 agree → ground truth; disagree → flag | `SNOBOL4-jvm/harness.clj` |
| `diff_monitor.py` | Sprint 20 double-trace diff tool | `SNOBOL4-tiny/tools/` (not yet written) |
| Corpus test runner | Execute all programs in SNOBOL4-corpus against all engines | Not yet written |
| Coverage grid | `COVERAGE.md` — feature × engine pass/fail matrix | Not yet written |

### Design Principles

- **Language-agnostic interface.** Each engine exposes a `run(program, input) → output`
  call. The harness does not care whether the engine is C#, Clojure, or C.
- **Corpus-driven.** Test programs live in SNOBOL4-corpus. The harness runs them.
  No test programs live in the harness itself.
- **Oracle-first.** CSNOBOL4 and SPITBOL are always the ground truth.
  The harness builds them, runs them, and compares our engines against them.
- **Incremental.** Start with the cross-engine runner (one script, three engines,
  one program). Add components one at a time.

### First Action (when harness work begins)

1. Move `harness.clj` from SNOBOL4-jvm into SNOBOL4-harness as the reference implementation.
2. Write `run_dotnet.sh` and `run_tiny.sh` — thin wrappers that produce identical output format.
3. Write `crosscheck.sh` — runs one `.sno` program on all three, diffs, reports.
4. Wire into SNOBOL4-corpus: `make crosscheck` runs all corpus programs.

**This is not the immediate priority.** Sprint 20 (SNOBOL4-tiny) is the immediate priority.
Harness work begins after Sprint 20 or in parallel if Jeffrey takes the harness track.

---

## 8. Per-Repo Quick Start

### SNOBOL4-dotnet
```bash
cd /home/claude/SNOBOL4-dotnet
export PATH=$PATH:/usr/local/dotnet
dotnet build Snobol4.sln -c Release -p:EnableWindowsTargeting=true
dotnet test TestSnobol4/TestSnobol4.csproj -c Release
# Expected: 1,607 / 0
```
> Linux: always pass `-p:EnableWindowsTargeting=true` — `Snobol4W` is Windows GUI.

### SNOBOL4-jvm
```bash
cd /home/claude/SNOBOL4-jvm
lein test
# Expected: 1,896 / 4,120 assertions / 0
```

### SNOBOL4-tiny
```bash
cd /home/claude/SNOBOL4-tiny
pip install --break-system-packages -e .
pytest test/
# Sprint 0–3 oracles (7 passing). Sprint 20 in progress.
```

### SNOBOL4-csharp
```bash
cd /home/claude/SNOBOL4-csharp
dotnet test tests/SNOBOL4.Tests
# Expected: 263 / 0
```

### SNOBOL4-cpython
```bash
cd /home/claude/SNOBOL4-cpython
pip install --break-system-packages -e .
python tests/test_bead.py
# Expected: 70+ / 0
```

---

## 9. Protocols

### The One Rule — Small Increments, Commit Often
**The container resets without warning. Anything not pushed is lost.**

Write a file → push. Change a file → push. No exceptions. Do not accumulate
two changes before pushing. Every logical change is exactly one push.

After every push: `git log --oneline -1` to confirm the remote received it.

### Directives (invoke by name)

**SNAPSHOT** — Save current state. For every repo with changes:
1. If tests pass → `git add -A && git commit -m "<what>" && git push`
2. If tests not green → `git add -A && git commit -m "WIP: <what>" && git push`
3. Update PLAN.md session log. Push `.github`.

**HANDOFF** — End of session. Full clean state for next Claude.
1. Run SNAPSHOT.
2. Update PLAN.md §5 (Current Work): check off completed items, add new problems,
   update commit hashes and test baselines.
3. Update satellite files as needed: `PATCHES.md`, `ASSESSMENTS.md`, `BENCHMARKS.md`.
4. Push `.github` last.
5. Write handoff prompt in plain prose — include the Sprint 20 commit promise.

**EMERGENCY HANDOFF** — Something is wrong, end now.
1. `git add -A` on every repo with any change.
2. `git commit -m "EMERGENCY WIP: <state>"` and `git push` everything immediately.
3. Append to PLAN.md §5: one sentence on what was in progress, what is broken.
4. Push `.github`.

### Snapshot Protocol (SNOBOL4-dotnet)
```bash
dotnet test /home/claude/SNOBOL4-dotnet/TestSnobol4/TestSnobol4.csproj -c Release 2>&1 | tail -3
# Must show: Failed: 0 before committing a non-WIP snapshot.
cd /home/claude/SNOBOL4-dotnet && git add -A && git commit -m "..." && git push
```

---

## 10. Satellite Map

Read these when you need depth. Do not read them at session start unless
the work specifically requires it.

| File | Read when |
|------|-----------|
| `PATCHES.md` | Any Sprint 20 runtime work — patch index tells you what was broken and why |
| `MONITOR.md` | Building or operating the double-trace monitor — full architecture, sync taxonomy |
| `ASSESSMENTS.md` | Checking test status, gaps, or cross-platform conformance |
| `BENCHMARKS.md` | Performance work or benchmark comparisons |
| `ORIGIN.md` | Understanding why this project exists — Lon's 60-year arc, the one-week build |
| `COMPILAND_REACHABILITY.md` | Sprint 20 inc-file → C mapping |
| `STRING_ESCAPES.md` | Any work involving string literals in SNOBOL4 / C / Python |
| `SPITBOL_LANDSCAPE.md` | SPITBOL distributions, owners, install, versions |
| `KEYWORD_GRID.md` | Pattern keyword reference |
| `SESSION_LOG.md` | Full session-by-session history — architecture decisions, what failed, insights |
| `REPO_PLANS.md` | Per-repo deep plans: dotnet, jvm, tiny sprint plan, Snocone front-end plan |

---

## 11. Key Commitments and Attributions

- **The Yield Insight** — `75cc3c0` — Claude Sonnet 4.6 noticed that Python generators are the interpretive form of the C goto model (`_alpha`/`_beta` are `yield` and `exhausted`).
- **The Infamous Login Promise** — `c5b3e99` — Lon gave the Sprint 20 commit message to Claude Sonnet 4.6. When `beautiful` compiles itself and the diff is empty, Claude writes the commit message.
- **The Sprint 20 commit** will be the third Claude attribution in this project's git log.

The org went from zero to world-class in seven days. "AlphaFold did not replace
biologists. It gave them an instrument they never had." — Lon, 2026-03-10.

---

## 12. Session Log

### 2026-03-10 — Session 1 (Sprint 20 Triage)

Drove Beautiful.sno to idempotent self-beautification under CSNOBOL4.
SPITBOL `-f` flag mystery resolved (breaks system label matching — use `-b` only).
CSNOBOL4 requires `-f` (DATA/DEFINE case collision) and `-P256k` (pattern stack).
Gen.inc GenTab bug found and fixed (idempotence blocker — continuation char missing).
SNOBOL4-corpus commits `2a38222`, `60c230e`. Oracle established: 649 lines, idempotent.

### 2026-03-10 — Session 2 (P001, P002, P003, per-function emission)

P001 fixed: `&STLIMIT` now enforced in `sno_comm_stno()`.
P002 fixed: `SNO_FAIL_VAL` type added; `sno_array_get/get2` returns it on out-of-bounds;
`sno_match_and_replace` propagates failure. Unit test `test_p002.c` 40/40.
P003 partial: FAIL propagation through expressions works; exposed flat function emission
bug (RETURN/FRETURN exit entire program). Fixed: per-function C emission. First real
output: 7 comment lines. Pattern emission chain fixed (alt, deferred ref, pattern concat).
Output: 10 lines. Remaining failure at STNO 619: `snoStmt` fails on `"START\n"`.
SNOBOL4-tiny commit `8610016`.

### 2026-03-10 — Session 3 (Continuity + Snapshot)

No code written. Continuity/orientation session. Read full plan, verified all repos
clean against last-known commits. Current state unchanged from Session 2.
SNOBOL4-tiny `8610016`, SNOBOL4-corpus `60c230e`, dotnet `63bd297`, jvm `9cf0af3`.

### 2026-03-11 — Session 4 (P1 SPAT_ASSIGN_COND fix)

Diagnosed `SPAT_ASSIGN_COND` materialise: captures recorded into `ctx->captures[]`
but never applied. Added `T_CAPTURE = 43` node type; `engine_match_ex()` with
`CaptureFn` callback; `capture_callback()` and `apply_captures()` in `snobol4_pattern.c`.
Compiled clean. Commit `883b802`. Output still 10 lines. `cap_start`/cursor offset
arithmetic under investigation. Next: fix unit test harness (`invalid initializer`),
confirm `BREAK(" \t\n;") . "x"` on `"START\n"` → `x == "START"`, then run
full binary with `SNO_PAT_DEBUG=1`.

### 2026-03-11 — Session 5 (Restructure + Harness)

PLAN.md restructured: 4,260 lines → 405 lines. Content preserved in two new
satellite files: `SESSION_LOG.md` (full history) and `REPO_PLANS.md` (per-repo
deep plans). Repo table reordered: dotnet first, then jvm, then tiny.

Strategic focus declared: **all substantial work goes to SNOBOL4-dotnet,
SNOBOL4-jvm, and SNOBOL4-tiny**. Pattern libraries (python, csharp, cpython)
are stable — no substantial new work until the three compilers are further along.

`SNOBOL4-harness` repo created (`2026-03-11`). Empty. Design documented in §7.
First action when harness work begins: migrate `harness.clj` from jvm, write
thin engine wrappers, write `crosscheck.sh`.

No code changes to any compiler this session.

---

*This file is the single operational briefing. Update §6 (Current Work) and §12
(Session Log) at every HANDOFF. Everything else is stable.*

---

## 8. Oracle Feature Coverage

Quick reference — does the feature exist and minimally work across known oracles?
SPITBOL-x32 is not testable in this container (kernel has 32-bit execution disabled).

| Feature | CSNOBOL4 2.3.3 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|---------|:--------------:|:-----------:|:-----------:|:-------:|
| `CODE(str)` | ✅ | ✅ | ? | ✅ |
| `EVAL(str)` | ✅ | ✅ | ? | ✅ |
| `LOAD(proto,lib)` | ✅ dlopen | ❌ stubbed (EXTFUN=0) | ❌ stubbed (EXTFUN=0) | ❌ error 23 (obj too large) |
| `UNLOAD(name)` | ✅ | ✅ | ? | ✅ |
| `LABELCODE(name)` | ✅ | ❌ undefined | ? | ❌ undefined |
| `DATA(proto)` | ✅ | ✅ (lowercase name) | ? | ✅ |
| `ARRAY()` / `TABLE()` | ✅ | ✅ | ? | ✅ |
| `DEFINE()` / functions | ✅ | ✅ | ? | ✅ |
| `TRACE('STNO','KEYWORD')` | ✅ (patched) | ❌ error 198 | ? | ❌ silent |
| `TRACE('STCOUNT','KEYWORD')` | ✅ | ✅ | ? | ✅ (different format) |
| `TRACE('X','VALUE')` | ✅ | ✅ | ? | ✅ (different format) |
| Pattern matching | ✅ | ✅ | ? | ✅ |
| `CODE()` execution `:<C>` | ✅ | ✅ | ? | ✅ |

**Notes:**
- SPITBOL-x64 `LOAD()`: `EXTFUN=0` in `port.h` — the dlopen plumbing exists in `sysld.c` but is compiled out
- SPITBOL-x32: same `EXTFUN=0` situation; binary cannot run in this container (32-bit kernel support disabled)
- SNOBOL5 `LOAD()`: fails with error 23 (object exceeds size limit) when loading large libs like libc; may work with small `.so` files
- SNOBOL5 trace format: `    STATEMENT N: &VAR = V,TIME = T` — different from CSNOBOL4/SPITBOL format
- SNOBOL5 `TRACE('STNO','KEYWORD')`: silently accepted, never fires — same symptom as pre-patch CSNOBOL4
- SPITBOL `DATA()`: returns lowercase datatype name (`point` not `POINT`) — corpus tests must account for this
- CSNOBOL4 `TRACE('STNO','KEYWORD')`: requires the 4-line patch to `isnobol4.c`/`snobol4.c` (see §4)

**Harness implication**: CSNOBOL4 (patched) is the sole reliable statement-trace oracle.
SPITBOL-x64 serves as output crosscheck. SNOBOL5 is a candidate third oracle for output
crosscheck but its trace format and STNO gap make it unsuitable as a trace oracle.
