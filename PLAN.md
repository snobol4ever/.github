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

**The two compiler/runtimes are the harness targets. Tiny is still being born.**

For the foreseeable future, harness crosscheck targets are exactly two engines:

| Priority | Repo | Status |
|----------|------|--------|
| 1 | **SNOBOL4-jvm** | Full SNOBOL4/SPITBOL → JVM bytecode. Mature. Harness target. |
| 2 | **SNOBOL4-dotnet** | Full SNOBOL4/SPITBOL → .NET/MSIL. Mature. Harness target. |
| — | **SNOBOL4-tiny** | Native → x86-64. Still being born. Not a crosscheck target yet. |

**SNOBOL4-tiny** remains active development (Sprint 20: T_CAPTURE blocker,
Beautiful.sno goal) but is excluded from harness crosscheck until it can run
non-trivial programs reliably. It joins the crosscheck target list when it passes
the systematic batch.

**SNOBOL4-harness** — crosscheck infrastructure. Oracles are CSNOBOL4 +
SPITBOL + SNOBOL5. Engines under test are JVM and dotnet. Generator feeds
both. Monitor and probe apply to both.

**SNOBOL4-corpus** — shared programs. Updated as needed.

**SNOBOL4-python, SNOBOL4-csharp, SNOBOL4-cpython** — pattern libraries.
Not a focus.

*Updated 2026-03-11: reduced crosscheck targets from three to two.
Tiny excluded until Sprint 20 T_CAPTURE blocker is resolved and
systematic batch passes.*

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

Verified against actual oracle binaries. SPITBOL-x32 not runnable in this
container (32-bit kernel execution disabled) — values inferred from source.

### Harness requirements

**Probe loop** needs: `&STLIMIT`, `&STCOUNT`/`&STNO`, `&DUMP`
**Monitor** needs: `TRACE(var,'VALUE')`, `TRACE(fn,'CALL')`, `TRACE(fn,'RETURN')`, `TRACE(label,'LABEL')`

### Probe loop — keyword support

| Keyword | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|---------|:--------:|:-----------:|:-----------:|:-------:|
| `&STLIMIT` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `&STCOUNT` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `&STNO` | ✅ | ❌ → use `&LASTNO` | ❌ | ? |
| `&LASTNO` | ❌ | ✅ | ✅ (inferred) | ? |
| `&DUMP=2` fires at `&STLIMIT` | ✅ | ✅ | ? | ✅ |

**All three runnable oracles support the probe loop.**
Use `&STCOUNT` (not `&STNO`) as the portable statement counter across all oracles.

### Monitor — TRACE type support (verified)

| TRACE type | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|-----------|:--------:|:-----------:|:-----------:|:-------:|
| `TRACE(var,'VALUE')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'CALL')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'RETURN')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(fn,'FUNCTION')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE(label,'LABEL')` | ✅ | ✅ | ✅ (inferred) | ✅ |
| `TRACE('STCOUNT','KEYWORD')` | ✅ | ✅ | ? | ✅ |
| `TRACE('STNO','KEYWORD')` | ✅ (patched) | ❌ error 198 | ❌ | ❌ silent |

**All four monitor TRACE types (VALUE/CALL/RETURN/LABEL) work on all three
runnable oracles.** STNO keyword trace is CSNOBOL4-only.

### TRACE output format (verified — matters for monitor pipe parsing)

| Oracle | Format |
|--------|--------|
| CSNOBOL4 | `file:LINE stmt N: EVENT, time = T.` |
| SPITBOL-x64 | `****N*******  event` |
| SNOBOL5 | `    STATEMENT N: EVENT,TIME = T` |

All three carry statement number and event description. Formats differ —
monitor pipe reader must normalize per oracle.

### Full feature grid

| Feature | CSNOBOL4 | SPITBOL-x64 | SPITBOL-x32 | SNOBOL5 |
|---------|:--------:|:-----------:|:-----------:|:-------:|
| `CODE(str)` | ✅ | ✅ | ? | ✅ |
| `EVAL(str)` | ✅ | ✅ | ? | ✅ |
| `LOAD(proto,lib)` | ✅ dlopen | ❌ EXTFUN=0 | ❌ EXTFUN=0 | ❌ error 23 |
| `UNLOAD(name)` | ✅ | ✅ | ? | ✅ |
| `LABELCODE(name)` | ✅ | ❌ undef | ? | ❌ undef |
| `DATA(proto)` | ✅ uppercase | ✅ lowercase | ? | ✅ |
| `ARRAY()` / `TABLE()` | ✅ | ✅ | ? | ✅ |
| `DEFINE()` / functions | ✅ | ✅ | ? | ✅ |
| Pattern matching | ✅ | ✅ | ? | ✅ |

### CSNOBOL4 TRACE patch (required)

`TRACE('STNO','KEYWORD')` silently accepted but never fires without this patch.
Deletes 2 lines from each of `snobol4.c` and `isnobol4.c`:

```bash
sed -i '/if (!chk_break(0))/{N;/goto L_INIT1;/d}' \
    /home/claude/csnobol4-src/snobol4.c \
    /home/claude/csnobol4-src/isnobol4.c
```

### Harness oracle roles

| Oracle | Probe loop | Monitor | Output crosscheck |
|--------|:----------:|:-------:|:-----------------:|
| CSNOBOL4 (patched) | ✅ primary | ✅ primary | ✅ |
| SPITBOL-x64 | ✅ | ✅ | ✅ |
| SPITBOL-x32 | ✅ (when available) | ✅ (when available) | ✅ |
| SNOBOL5 | ✅ | ✅ | ✅ |
| SNOBOL4-jvm | via `run-to-step` | via `trace-register!` | ✅ |
| SNOBOL4-dotnet | TBD | TBD | ✅ |
| SNOBOL4-tiny | TBD | TBD | ✅ |

---

## 9. Harness Cornerstone Techniques

The SNOBOL4-harness is built on two fundamental testing techniques.
Every other mechanism in the harness derives from these two.

### Technique 1: Probe Testing

Probe testing reads the interpreter's execution counters at strategic points
to observe *where* execution is without altering control flow.

**Keywords used:**
- `&STNO` — current statement number (CSNOBOL4; SPITBOL equivalent is `&LASTNO`)
- `&STCOUNT` — cumulative statements executed since program start
- `&STLIMIT` — maximum statements before forced termination (used to cap runaway programs)

**Mechanism:** The harness inserts probe statements into a copy of the subject
program (or wraps it) that read `&STNO`/`&STCOUNT` at entry, exit, and branch
points. Comparing counter snapshots across oracle runs confirms that the same
execution paths are taken, regardless of implementation differences in timing or
output formatting.

**Oracle support:**

| Keyword | CSNOBOL4 | SPITBOL-x64 | SNOBOL5 |
|---------|:--------:|:-----------:|:-------:|
| `&STNO` | ✅ | ❌ (use `&LASTNO`) | ? |
| `&STCOUNT` | ✅ | ✅ | ✅ |
| `&STLIMIT` | ✅ | ✅ | ✅ |

---

### Technique 2: Monitor Testing

Monitor testing attaches `TRACE()` callbacks that fire automatically when
variables change, functions are called or return, or labeled statements are
reached. The monitor observes *what happened* during execution.

**TRACE() types used:**

| Call | Fires when |
|------|-----------|
| `TRACE('varname', 'VALUE')` | variable is assigned |
| `TRACE('fnname', 'CALL')` | function is called |
| `TRACE('fnname', 'RETURN')` | function returns |
| `TRACE('fnname', 'FUNCTION')` | function called or returns |
| `TRACE('label', 'LABEL')` | goto transfers to label |

**Control keywords:**
- `&TRACE` — countdown; each trace event decrements it; tracing stops at zero
- `&FTRACE` — function-trace countdown (SPITBOL extension)

**Oracle support for TRACE types:**

| TRACE type | CSNOBOL4 | SPITBOL-x64 | SNOBOL5 |
|-----------|:--------:|:-----------:|:-------:|
| `'VALUE'` | ✅ | ✅ | ✅ |
| `'CALL'` | ✅ | ✅ | ✅ |
| `'RETURN'` | ✅ | ✅ | ✅ |
| `'FUNCTION'` | ✅ | ✅ | ✅ |
| `'LABEL'` | ✅ | ✅ | ✅ |
| `'KEYWORD'`+`STCOUNT` | ✅ | ✅ | ✅ |
| `'KEYWORD'`+`STNO` | ✅ (patched) | ❌ error 198 | ❌ silent |

---

### Why these two techniques are the cornerstone

Probe testing gives **structural coverage**: did execution reach the right
statements in the right order?

Monitor testing gives **behavioral coverage**: did the right values flow through
variables, functions, and control labels?

Used together on the same subject program running under multiple oracles, they
produce a crosscheck that is both cheap (no external test framework needed —
pure SNOBOL4) and thorough (covers path, data, and control flow).

The harness crosscheck pipeline is:
1. Run subject program under CSNOBOL4 with probes → capture `&STNO`/`&STCOUNT` log
2. Run subject program under CSNOBOL4 with monitors → capture TRACE log
3. Run subject program under SPITBOL-x64 with monitors → capture TRACE log
4. Diff probe logs across oracles; diff monitor logs across oracles
5. Any divergence is a compatibility gap to document or fix in SNOBOL4+

### 2026-03-11 — Session 6 (Harness Sprint H1 — Oracle Feature Grid + probe.py)

**Oracle investigation:**
- CSNOBOL4 TRACE patch confirmed working (`TRACE('STNO','KEYWORD')` fires every stmt)
- SPITBOL x64 forked to `SNOBOL4-plus/x32` with Makefile cross-build patch
- SNOBOL5 binary downloaded and tested (2024-08-29 build)
- Full four-oracle feature grid written to PLAN.md §8
- TRACE keyword variant matrix: exhaustively tested `STNO`, `&STNO`, `STCOUNT`, `&STCOUNT`
  — SPITBOL manual confirmed: only `ERRTYPE`, `FNCLEVEL`, `STCOUNT` are valid KEYWORD targets
  — SPITBOL has no `&STNO`; equivalent is `&LASTNO`

**Harness cornerstone documented (§9):**
- Probe testing: `&STNO`/`&STCOUNT` + `&STLIMIT` — structural/path coverage
- Monitor testing: `TRACE()` on variables, functions, labels — behavioral coverage
- Both techniques documented as the foundation of all harness work

**probe.py built and pushed to SNOBOL4-harness:**
- Prepends `&STLIMIT=N` + `&DUMP=2` to subject source (two lines, no file modification)
- Runs N times (stlimit=1..N), captures variable dump at each cutoff
- Prints frame-by-frame diff: NEW/CHG for every variable after every statement
- `--oracle csnobol4|spitbol|both` — both mode runs both and diffs frames
- `--var VAR ...` — filter to specific variables
- Commit: `8e10cbb`

**State at snapshot:**
- SNOBOL4-harness: `8e10cbb` — probe.py committed, smoke-tested
- SNOBOL4-plus/.github: sections 8 and 9 added, oracle grid complete
- All other repos unchanged from Session 5

---

## 10. Harness Architecture — Top-Down Model

**Decided 2026-03-11.**

### The topology

```
SNOBOL4-plus/          ← Lon works here. This is the top.
├── .github/           ← PLAN.md, this file. The control center.
├── SNOBOL4-harness/   ← Test driver. Reaches DOWN into engines.
├── SNOBOL4-corpus/    ← Programs. Shared by all.
├── SNOBOL4-jvm/       ← Engine. Knows nothing about harness.
├── SNOBOL4-dotnet/    ← Engine. Knows nothing about harness.
└── SNOBOL4-tiny/      ← Engine. Knows nothing about harness.
```

The harness is a **peer repo at the top level**, not a submodule or library
embedded inside each engine. It calls each engine as a **subprocess** —
stdin/stdout — exactly like a user would. No engine imports harness code.
No harness code lives inside any engine repo.

### The calling convention (simple, already works)

Each engine is callable today from the harness level:

```bash
# JVM
cd SNOBOL4-jvm && lein run < program.sno

# dotnet
cd SNOBOL4-dotnet && dotnet run --project Snobol4 < program.sno

# tiny
./SNOBOL4-tiny/src/runtime/snobol4/beautiful < program.sno
```

The harness wraps these calls. Engines don't change. No API needed.

### What this means for probe and monitor

**Probe loop** — the harness prepends `&STLIMIT=N` and `&DUMP=2` to any
`.sno` file and runs it through any oracle or engine binary. The engine
is a black box. One subprocess per frame.

**Monitor** — the harness launches three subprocesses connected by pipes:
1. Oracle (CSNOBOL4 or SPITBOL) with `TRACE()` injected → pipe A
2. Engine under test (jvm/dotnet/tiny) running same program → pipe B  
3. Harness diff/sync process reading pipe A and pipe B in lockstep

The engine under test does not need to implement TRACE. The oracle provides
the ground-truth event stream. The engine provides its output stream.
The harness compares them.

### What we can test from up here today

| Engine | Probe loop | Monitor (output diff) | Monitor (event stream) |
|--------|:----------:|:---------------------:|:----------------------:|
| CSNOBOL4 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SPITBOL-x64 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SNOBOL5 (oracle) | ✅ | ✅ ref | ✅ TRACE native |
| SNOBOL4-jvm | ✅ via subprocess | ✅ diff vs oracle | ⚠ needs TRACE or step hook |
| SNOBOL4-dotnet | ✅ via subprocess | ✅ diff vs oracle | ⚠ needs TRACE or step hook |
| SNOBOL4-tiny | ✅ via subprocess | ✅ diff vs oracle | ⚠ SNO_MONITOR=1 exists |

For output-level crosscheck (does this engine produce the same stdout as
CSNOBOL4?), all three engines are testable from here today with no changes.

For event-level monitor (does this engine execute the same statements in
the same order?), the engine needs to emit a trace stream. SNOBOL4-tiny
already has `SNO_MONITOR=1` → stderr. JVM has `run-to-step`. Dotnet TBD.

### The open question — deferred

How each engine exposes its internal state for event-level monitoring is
an open question. It does not block output-level crosscheck, which works
today. Decide when we get there.

---

## 11. Developer Workflow — Calling the Harness from an Engine Repo

**Decided 2026-03-11.**

### The goal

Jeffrey (or any engine developer) should be able to run the full harness
test suite from inside their engine repo without leaving that directory:

```bash
cd ~/snobol4-plus/SNOBOL4-jvm
make test-harness        # or: ../SNOBOL4-harness/run.sh jvm
```

The harness lives at `../SNOBOL4-harness/` relative to any sibling repo.
The developer does not need to know the harness internals.

### The contract

Each engine repo exposes one thing to the harness: a way to run a SNOBOL4
program from stdin and return stdout. The harness calls it as a subprocess.

The harness registry (`harness.clj` `engines` map) already defines this
for every known engine:

```clojure
:jvm     {:bin "lein" :args ["run"] :type :subprocess}   ; TBD — or uberjar
:dotnet  {:bin "dotnet" :args ["run" "--project" "..."] ...}
:tiny    {:bin ".../beautiful" :args [] ...}
```

### What needs to happen (open, not blocking crosscheck)

1. **`SNOBOL4-harness/run.sh`** — thin shell entry point:
   ```bash
   #!/bin/bash
   # Usage: run.sh <engine> [program.sno]
   # Run from anywhere inside snobol4-plus/ tree
   ```

2. **Each engine repo gets a `Makefile` target** (or `justfile`):
   ```makefile
   test-harness:
       ../SNOBOL4-harness/run.sh jvm
   ```

3. **The harness locates itself** via `$HARNESS_ROOT` env or by walking up
   from `$PWD` until it finds `SNOBOL4-harness/`.

### Note on JVM specifically

`harness.clj` currently runs the JVM engine **in-process** (direct Clojure
call). Jeffrey running from `SNOBOL4-jvm/` needs it to run the local build,
not a pinned copy. Two options — decide later:
- Keep in-process but load from local classpath (lein dependency)
- Switch `:jvm` entry in registry to a subprocess (`lein run` or uberjar)

Subprocess is simpler and keeps the contract uniform. In-process is faster.

---

## 12. Test Code Generation — Three Techniques

**Recorded 2026-03-11. Prior art inventoried.**

The harness uses three distinct testing techniques, each complementary:

```
1. Probe     — step-by-step replay     (DONE: probe.py, test_helpers.clj)
2. Monitor   — live three-process pipe (DESIGNED, not yet built)
3. Generator — program synthesis       (DONE: generator.clj, Expressions.py)
```

### What we have — generator prior art

**`adapters/jvm/generator.clj`** (migrated from SNOBOL4-jvm, Sprint 14/18)

Two tiers already built:

*Tier 1 — `rand-*` (probabilistic):*
- `rand-program [n-moves]` — weighted random walk over a move table;
  typed variable pools (int/real/str/pat), safe literals, no div-by-zero,
  legible idiomatic SNOBOL4
- `rand-statement []` — one random statement, all grammatical forms
- `rand-batch [n]` — n random programs

*Tier 2 — `gen-*` (exhaustive lazy sequences):*
- `gen-assign-int/str`, `gen-arith`, `gen-concat`, `gen-cmp`, `gen-pat-match`
  — cross-products of all vars × all literals for each construct
- `gen-by-length []` — ALL constructs, sorted by source length, deduplicated;
  canonical fixture preamble prepended so every program is self-contained
- `gen-by-length-annotated []` — same, with `:band 0..5` complexity tag
- `gen-error-class-programs []` — programs designed to hit each error class

*Batch runners wired to harness:*
- `run-worm-batch [n source-fn]` — runs N programs through diff-run,
  saves to `golden-corpus.edn`, returns `{:records :summary :failures}`
- `run-systematic-batch []` — exhaustive gen-by-length through harness
- `emit-regression-tests [records ns]` — converts corpus records to
  pinned Clojure deftests

**`adapters/tiny/Expressions.py`** (Sprint 15, migrated from SNOBOL4-tiny)

Two independent generation architectures for arithmetic expressions:

*Tier 1 — `rand_*` (probabilistic recursive):*
- `rand_expression/term/factor/element/item` — mutually recursive random
  descent; weighted choices at each level; generates well-formed infix
  expressions like `x+3*(y-z)/2`

*Tier 2 — `gen_*` (systematic generator-based):*
- `gen_expression/term/factor/element/item` — Python generator functions
  that yield every expression in a deterministic exhaustive order;
  self-referential (`gen_term` calls `gen_term` via `next()`) —
  produces the full infinite grammar systematically

*Also in Expressions.py:*
- `parse_expression/term/factor/element/item` — generator-based
  SNOBOL4-style pattern parser in Python (PATTERN/POS/RPOS/σ/SPAN
  classes); the parse IS the test — proves the expression grammar
- `evaluate(tree)` — tree evaluator (x=10, y=20, z=30)
- `main()` — generates 100 random expressions, parses each, evaluates,
  prints result; self-checking loop

### The two generation philosophies

**Probabilistic (`rand_*`)** — random weighted walk. Fast, finds
surprising combinations, scales to any complexity. Non-reproducible
without seed. Good for fuzzing and corpus growth.

**Exhaustive (`gen_*`)** — systematic enumeration. Every combination
at every complexity level. Reproducible. Finite at each band. Good for
regression coverage and gap analysis.

Both feed the same harness pipeline:
```
generator → program source → run(oracle, src) → outcome
                           → run(engine, src) → outcome
                                              → agree? → pass/fail
```

### What is missing

- `Expressions.py` generator is standalone Python — not yet wired to
  the harness `crosscheck` pipeline
- No SNOBOL4-statement-level generator in Python (only expression level)
- `generator.clj` is JVM-only — no Python equivalent for full SNOBOL4
  programs (dotnet/tiny need this)
- No generator for patterns beyond simple primitives (ARB, ARBNO, BAL,
  recursive patterns)
- No generator for DATA/DEFINE/CODE programs (higher-order constructs)

### Next step (when we get here)

Wire `Expressions.py` gen tier into a Python `crosscheck.py` that calls
`run(oracle, src)` and `run(engine, src)` for each generated expression
program. That gives us expression-level crosscheck for dotnet and tiny
from the top level, same pattern as the JVM batch runner.

---

## 13. Corpus + Generator — Two Feeds for the Crosschecker

**Decided 2026-03-11.**

The crosschecker has two independent sources of programs to run:

```
SNOBOL4-corpus/          ← curated, permanent, version-controlled
    benchmarks/          ← performance programs
    programs/sno/        ← real-world programs (Lon's collection)
    programs/test/       ← focused feature tests
    programs/gimpel/     ← Gimpel book examples (to add)
    programs/generated/  ← pinned worm outputs (regression guards)

generators (live, on demand) ←─────────────────────────────────────
    generator.clj            ← rand-program, gen-by-length (Clojure)
    Expressions.py           ← rand_expression, gen_expression (Python)
    [future] generator.py    ← full SNOBOL4 program generator in Python
```

### The two feeds are complementary

**Corpus** — curated, stable, human-meaningful programs. Every program
has a known purpose. Failures are regressions. Ideal for CI.

**Generators** — infinite, systematic or random. Programs are
structurally valid but machine-generated. Failures are new bugs.
Ideal for fuzzing, coverage expansion, and gap-finding.

### How generators feed the crosschecker

```
rand-program()  ──→  crosscheck(src, targets=[:jvm :dotnet])
                         ├─ run(:csnobol4, src) → ground truth
                         ├─ run(:jvm, src)      → compare
                         └─ run(:dotnet, src)   → compare

gen-by-length() ──→  same pipeline, exhaustive, sorted by complexity
```

The generator output that passes crosscheck can be pinned into
`corpus/programs/generated/` as regression guards. The generator
output that fails crosscheck is a bug report.

### Pipeline (full picture)

```
[generator]  →  source string
[corpus]     →  source string
                    ↓
             crosscheck(src)
                    ↓
         triangulate oracles (CSNOBOL4 + SPITBOL + SNOBOL5)
                    ↓
              ground truth
                    ↓
         run JVM    run dotnet
                    ↓
              agree? → :pass
              differ? → :fail → probe/monitor to find divergence point
```

### What this means for SNOBOL4-corpus organization

The corpus needs a `generated/` subdirectory for pinned generator
outputs. Everything else (sno/, benchmarks/, gimpel/, test/) is
hand-curated. The generator feeds the crosschecker directly — it does
not need to land in the corpus first unless we want to pin it.

### 2026-03-11 — Session 7 (Harness Sprint H1 continued — Architecture + Corpus)

**Focus**: Harness architecture, corpus reorganization, strategic planning.
No compiler code written this session.

**Completed:**

- **§8 Oracle Feature Grid** — rewritten with fully verified TRACE output
  formats for all three runnable oracles (CSNOBOL4, SPITBOL, SNOBOL5).
  Confirmed VALUE/CALL/RETURN/LABEL TRACE works on all three.

- **§10 Top-down harness model** — documented: harness is a peer repo at
  top level, engines are black boxes called as subprocesses. Output-level
  crosscheck works today with zero engine changes.

- **§11 Developer workflow** — Jeffrey can run `make test-harness` from
  inside SNOBOL4-jvm. Calling convention documented. Open question on
  in-process vs subprocess for JVM deferred.

- **§12 Test code generation** — generator.clj (rand-program, gen-by-length)
  and Expressions.py (rand_*/gen_* expression tiers) inventoried and
  documented. Both migrated into SNOBOL4-harness/adapters/.

- **§13 Corpus + generators as two feeds** — documented: corpus is curated
  permanent collection; generators are infinite live tap. Both feed
  crosscheck directly. Generator failures = bug reports. Passing generator
  outputs → pinned in corpus/generated/.

- **harness.clj refactored** — unified `run/triangulate/crosscheck` API,
  engine registry with `:role :oracle/:target`, `targets` def (JVM +
  dotnet only; tiny excluded). Commit `f6c10f8`.

- **Crosscheck targets reduced to JVM + dotnet** — tiny excluded until
  Sprint 20 T_CAPTURE blocker resolved.

- **SNOBOL4-corpus reorganized** — new structure: `crosscheck/` by feature
  (hello/arith/strings/patterns/capture/control/functions/arrays/code),
  `programs/` (beauty/lon/dotnet/icon/gimpel), `generated/` placeholder.
  Scattered .sno files from dotnet and tiny collected. Commit `8d58091`.

- **gimpel.zip + aisnobol.zip** — Lon attempted to upload; I/O error on
  uploads mount (session too long). Re-upload at start of next session.
  These go into `corpus/programs/gimpel/` and `corpus/crosscheck/`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-harness | `f6c10f8` | Unified harness API + engine registry |
| SNOBOL4-harness | `54511e8` | Expressions.py added |
| SNOBOL4-harness | `2774249` | All testing artifacts pulled in |
| SNOBOL4-corpus | `8d58091` | Full corpus reorganization |
| .github | `db71c6c` | §13 corpus+generators as two feeds |
| .github | `c93702b` | §2 reduce targets to JVM+dotnet |
| .github | `16bd73f` | §12 generator documentation |
| .github | `874d993` | §11 developer workflow |
| .github | `8ffbcfa` | §10 top-down harness model |
| .github | `a558ac8` | §8 verified oracle grid |

**Next session — immediate actions:**

1. **Re-upload gimpel.zip and aisnobol.zip** — add to corpus/programs/gimpel/
   and sort into crosscheck/ subdirs as appropriate.
2. **Smoke test dotnet engine** — verify `dotnet run` produces clean stdout
   from a simple .sno; confirm engine registry entry is correct.
3. **Write crosscheck.py** — Python crosscheck runner: enumerates
   `corpus/crosscheck/`, runs each program through oracles + JVM + dotnet,
   reports pass/fail table. This is the first end-to-end harness run.
4. **Sprint 20 T_CAPTURE** — resume when ready; blocker is
   `cap_start`/`scan_start` offset arithmetic in `snobol4_pattern.c`.

**Open questions carried forward:**
- JVM: in-process vs subprocess for harness calling convention
- gimpel/ and capture/ crosscheck subdirs still empty
- monitor.py (three-process pipe monitor) not yet built
