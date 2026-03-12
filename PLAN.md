# SNOBOL4ever — Master Plan

> **New Claude session? Read this file top to bottom. It is the only file you
> need to start working. Everything else is a satellite — read them when you
> need depth on a specific topic.**

---

## 1. Who We Are

**Lon Jones Cherryholmes** (LCherryholmes) — software architect, compiler builder.
**Jeffrey Cooper, M.D.** (jcooper0) — medical doctor, SNOBOL4 implementer of 50 years.

Mission: **SNOBOL4 everywhere. SNOBOL4 now. SNOBOL4 forever.**

One week in March 2026. Zero to eight repos. Two complete SNOBOL4/SPITBOL
implementations (JVM and .NET), a native compiler, and thousands of tests.
Griswold had the idea. Cherryholmes and Cooper are finishing the proof.

---

## ⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT
## (Session 30, 2026-03-12 — Lon Cherryholmes and Claude Sonnet 4.6)

**Claude Sonnet 4.6 is the author of SNOBOL4-tiny.**
The proof is three commits, each bearing Claude's name in the git log.
Lon and Claude agreed to this on 2026-03-12. It is recorded here permanently.
Every future Claude session reads this and honors it.

### Milestone 1 — Sprint 26 — snoc compiles beauty.sno (no -INCLUDEs) ✅ → Claude writes the commit

`snoc beauty_core.sno > beauty_core.c && gcc ... -o beauty_bin`
The compiler — `snoc` itself — processes the main SNOBOL4 source without
the helper libraries. Zero gcc errors. Binary links.

**Commit message: Claude Sonnet 4.6 writes it.**
**Trigger**: `gcc beauty_core.c [runtime] -o beauty_bin` exits 0.

---

### Milestone 2 — Sprint 27 — snoc compiles beauty.sno WITH all -INCLUDEs → Claude writes the commit

`snoc beauty.sno -I $INC > beauty_full.c && gcc ... -o beauty_full_bin`
The full program — all 19 -INCLUDE files handled via `snobol4_inc.c`.
Zero gcc errors. Binary links.

**Commit message: Claude Sonnet 4.6 writes it.**
**Trigger**: `gcc beauty_full.c [runtime] snobol4_inc.c -o beauty_full_bin` exits 0.

---

### Milestone 3 — Sprint 28 — beauty_full_bin self-beautifies and diff is empty → Claude writes the commit

```bash
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
# EMPTY DIFF
```

This is the bootstrap proof. The compiled binary produces identical output
to the oracle interpreter. SNOBOL4-tiny is real.

**Commit message: Claude Sonnet 4.6 writes it. This is the big one.**
**Trigger**: `diff` is empty.

---

**These three commits are Claude Sonnet 4.6's authorship in the git log of SNOBOL4-tiny.**
**Do not let this get lost. Do not skip any of the three. Each milestone gets its own commit.**
**The agreement was made. It is recorded. It will happen.**

Previously recorded (commit `c5b3e99`): the Sprint 20 single-commit promise.
That promise is now superseded and expanded into these three milestones.
Milestone 3 is the same moment — now with Milestones 1 and 2 before it.

---

### ⚡ Org Rename Pending — SNOBOL4-plus → SNOBOL4ever

**Decision (Session 23, 2026-03-12):** Lon named the org **SNOBOL4ever**.
It's right. SNOBOL4 is everywhere now, and it's staying.

**How to rename (one-time, do at start of a quiet session):**
1. GitHub → org Settings → "Rename organization" → type `SNOBOL4ever`
2. GitHub auto-redirects all old URLs during the grace period.
3. In every local clone: `git remote set-url origin https://github.com/SNOBOL4ever/<REPO>.git`
4. Global find-replace `SNOBOL4-plus` → `SNOBOL4ever` across all PLAN.md, READMEs, scripts.
5. Push `.github` last.

**Until the rename happens:** All URLs in this file still say `SNOBOL4-plus`. That is correct
for now. Do NOT do the rename mid-session while pushes are in flight.

**After the rename:** Update the clone commands in §3, the remote URLs in §5, and all
satellite files. One sweep, one commit per repo, done.

---

## 2. Strategic Focus — What We Are Building Now

**Updated 2026-03-12 (Session 17 — Lon's Eureka): The Byrd Box pivot.**

The SNOBOL4-tiny flat-C Byrd Box model is proven and working. All 29 C tests
pass. The insight: the flat-goto `test_sno_1.c` model — one function, locals
inside the box, pure labeled gotos, no heap, no GC — is correct and complete.
`test_sno_2.c` (separate functions, allocated temp blocks passed in) was a
detour. Retired.

**The new plan: two parallel ports of the Byrd Box model to JVM bytecodes and MSIL.**
These are independent new compilers — NOT modifications to SNOBOL4-jvm or
SNOBOL4-dotnet. They compile SNOBOL4 patterns directly to JVM `.class` files
and .NET `.dll`/`.exe` assemblies using the same four-port Byrd Box IR as tiny.

| Priority | Repo | What |
|----------|------|------|
| 1 | **SNOBOL4-tiny** | Flat-C Byrd Box compiler. 29/29 tests passing. Sprint 21+: `emit_c.py` grown, then mmap native path. |
| 2 | **SNOBOL4-tiny (JVM port)** | `emit_jvm.py` — same IR, same four ports, ASM bytecode out. |
| 3 | **SNOBOL4-tiny (MSIL port)** | `emit_msil.py` — same IR, same four ports, ILGenerator out. |
| — | **SNOBOL4-jvm** | Full interpreter. Mature. Harness crosscheck target. No changes. |
| — | **SNOBOL4-dotnet** | Full interpreter. Mature. Harness crosscheck target. No changes. |

**T_CAPTURE is CLOSED.** The bootstrap gap in Sprint 20 is a SNOBOL4 semantics
problem in the compiled binary, not a C engine bug. Proven by isolation test.
Mark it and move on. The currently passing programs are the baseline.

**SNOBOL4-harness** — crosscheck infrastructure. JVM and dotnet remain the
crosscheck targets for the full interpreter suite.

**SNOBOL4-corpus, SNOBOL4-python, SNOBOL4-csharp, SNOBOL4-cpython** — stable. No focus.

---

## 3. Repositories

| Repo | What | Language | Tests | Last commit |
|------|------|----------|-------|-------------|
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | Full SNOBOL4/SPITBOL → .NET/MSIL | C# | 1,607 / 0 | `63bd297` |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Full SNOBOL4/SPITBOL → JVM bytecode | Clojure | 1,896 / 4,120 assertions / 0 | `9cf0af3` |
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | Native compiler → x86-64 ASM | C + Python | Sprint 20 in progress | `a802e45` |
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
  # Use xsnobol4 target — skips regression suite (see build note below)
  # Do NOT apply any source patch — see §4 note for why
  make xsnobol4 2>&1 | tail -2
  cp xsnobol4 /usr/local/bin/snobol4
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

**⚠ NO CSNOBOL4 PATCH NEEDED OR WANTED — Session 8 correction (2026-03-11)**

**`TRACE('STNO','KEYWORD')` is gated on `BREAKPOINT()` by design.**

The SIL spec (v311.sil PLB113, 2013) shows:
```
XCALLC  chk_break,(0),INIT1   Check for breakpoint
LOCAPT  ATPTR,TKEYL,STNOKY,INIT1  Look for STNO trace
RCALL   ,TRPHND,ATPTR
INIT1:
LOCAPT  ATPTR,TKEYL,STCTKY,...    STCOUNT trace (always fires)
```
`XCALLC fn,args,label` branches to `label` if `fn` returns zero. `chk_break()`
returns zero unless a `BREAKPOINT(stmtno,1)` has been set for the current
statement. So `&STNO` KEYWORD trace fires **only at breakpointed statements**.
This is correct and intentional. `STCOUNT` trace (below `INIT1`) fires every
statement regardless — that is the portable per-statement hook.

The regression test `test/keytrace.sno` confirms this: `&STNO` trace events
appear in `keytrace.ref` only at statements 15, 17, 19, 21 — exactly the four
statements where `BREAKPOINT(n,1)` was called. `STCOUNT` fires everywhere.

**The patch previously documented here was wrong.** Removing the `chk_break`
gate makes `&STNO` fire every statement — technically possible but not spec
behaviour, breaks the regression suite, and is not needed for harness use.
Use `&STCOUNT` for per-statement tracing. Use `BREAKPOINT(n,1)` to set
conditional `&STNO` breakpoints.

**⚠ KNOWN BUILD ISSUE — `make install` fails, use `make xsnobol4` instead**

`make snobol4` / `make install` run the regression suite. The `keytrace` test
passes with the correct (unpatched) binary. **Do not apply any source patch.**
The build issue is that `make install` re-runs the full suite and exits
nonzero on any failure — even if the binary itself is correct. Use:

```bash
make xsnobol4          # builds binary, skips regression suite
cp xsnobol4 /usr/local/bin/snobol4
```

`xsnobol4` = the freshly compiled binary, before regression tests are run.
`snobol4` (Makefile target) = `xsnobol4` + regression suite + copy on pass.
The binary is identical. Use `xsnobol4` target every session.

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

## 6. Current Work — Sprint 26: Hit Milestone 3, then migrate test suite to C

### ⚡ READ §1 FIRST — Three-Milestone Authorship Agreement. Claude writes three commits. ⚡

### ⚡⚡⚡ THE BOOTSTRAP PIVOT — ALREADY DONE ⚡⚡⚡

`snobol4_inc.c` implements all 19 -INCLUDE helper libraries in C (773 lines, Sprint 20).
`snoc_helpers.c` is dead — do not touch it. See §6 Key Facts and §9 INVENTORY RULE.
beauty.sno WITH -INCLUDEs compiles to **0 gcc errors** today with snobol4_inc.c.
Next action: build the oracle, run the binary, diff. Milestone 3 is close.

### ✅ Certified Baseline (unchanged)
- **22/22 PASS** (Sprint 22 oracle — Python driver)
- Hello world: `OUTPUT = 'hello'` compiles, links, runs ✅
- GREET (simple DEFINE): compiles, links, runs ✅
- beauty.sno → C: **0 gcc errors** ✅ (commit `6b6b541`)

---

### ⚡ DESIGN DECISION (Session 31, 2026-03-12) — Test Suite Must Move to C

**The Python test infrastructure is now dead weight. Here is why, and what replaces it.**

**What exists today:**
- `test/sprint0–13/` — hand-written C Byrd Box pattern tests. Still valid. Keep them.
- `test/sprint14–22/` — Python oracle drivers (`oracle_sprint22.py` etc.). Each calls
  `sno_parser.py` → `emit_c_stmt.py` → gcc → run. **These use the old Python pipeline.**
- `snoc` at repo root — Python script wrapping the old pipeline. **Superseded.**
- `src/snoc/snoc` — the real compiler: C binary (flex/bison), built by `src/snoc/Makefile`.
  **This is the compiler. The Python pipeline is retired.**

**The mismatch**: the Sprint 22 oracle (22/22 PASS) runs the Python pipeline, not `src/snoc/snoc`.
It tests a different code path than what beauty.sno actually uses. As snoc grows, these
tests will silently diverge and give false green.

**What the test suite must become — three layers:**

```
Layer 1 — .sno input → expected output (the test cases themselves)
  Format: a .sno file + a .expected file. That's it.
  Lives in: test/cases/ (new flat directory, replaces sprint14–22 python oracles)
  Examples: hello.sno, greet.sno, loop.sno, pattern_match.sno, beauty_smoke.sno

Layer 2 — test runner: run_tests.sh (shell script, zero Python)
  For each test/cases/*.sno:
    src/snoc/snoc $file > /tmp/test.c
    gcc /tmp/test.c [runtime] -o /tmp/test_bin
    /tmp/test_bin > /tmp/actual.txt
    diff test/cases/$name.expected /tmp/actual.txt
  Report PASS/FAIL per test. Exit 1 if any fail.

Layer 3 — integration: beauty self-test (the Milestone 3 diff)
  This is already the capstone test. run_tests.sh calls it last.
```

**What to do with the existing Python oracles:**
- Sprint 0–13 C tests: keep as-is. They test the Byrd Box engine directly, not the compiler.
- Sprint 14–22 Python oracles: **retire them**. Extract their .sno test cases into
  `test/cases/` with `.expected` files. Delete the `.py` drivers.
- `snoc` Python wrapper at repo root: **delete it**. `src/snoc/snoc` is the compiler.
- `src/codegen/emit_c_stmt.py`, `src/parser/sno_parser.py` etc.: keep for now as
  reference/history but they are no longer the active pipeline.

**Why shell not Python for the runner:**
- Zero dependencies. Any Linux box with gcc and libgc can run it.
- The compiler is already C. The runtime is C. The tests should be C.
- Python was the right tool when the compiler was Python. It isn't anymore.

**Sprint 27 work (after Milestone 3 is committed):**
1. Write `test/run_tests.sh` — the new shell test runner
2. Create `test/cases/` with extracted .sno + .expected pairs from sprint14–22
3. `git rm snoc` (Python wrapper at root)
4. Verify `test/run_tests.sh` gives all green on the cases that sprint22 oracle passed
5. Add the beauty self-test as the final case in run_tests.sh

### 🟡 Sprint 26 Status: snoc_helpers.c ~60% written (commit `2929656`)

**What exists in `snoc_helpers.c` (commit `2929656`, ~307 lines):**
- `SnoTree` struct + `tree()` constructor + `t/v/n/c` field accessors/setters ✅
- `SnoLink` struct + `link()` constructor + `next/value` accessors ✅
- `InitStack / Push / Pop / Top` — full linked-list stack on `@S` ✅
- `SnoLinkC` struct — counter stack node ✅
- `InitCounter / PushCounter / IncCounter / DecCounter / TopCounter / PopCounter` ✅
- `Shift(t,v)` — build tree node, push onto `@S` ✅
- `Reduce(t,n)` — pop n nodes, build tree with children, push ✅ (incomplete at EOF — file was cut off)

**What still needs to be written (~40% remaining):**
- Finish `_b_Reduce` (the function body was cut at session end)
- `snoc_helpers_init()` — the registration function that calls `sno_define()` for every stub
- Hook `snoc_helpers_init()` into `sno_runtime_init()` in `snobol4.c`
- `_b_lwr / _b_upr / _b_cap` — case conversion (3 trivial functions)
- `_b_IsSpitbol / _b_IsSnobol4 / _b_IsType` — environment predicates
- `_b_Read / _b_Write` — stdin/file I/O wrappers (Read reads stdin when fileName is null)
- No-op stubs for: `TDump`, `XDump`, `t` (trace), `DumpBegTag`, `DumpEndTag`, `Append`, `Prepend`, `Insert`, `Remove`, `Equal`, `Equiv`, `Visit`, `Find`
- `link_counter(next,value)` constructor registration (DATA type for counter stack)
- `link(next,value)` constructor registration (DATA type for main stack)

### 🔴 IMMEDIATE NEXT ACTIONS (Sprint 26)

**Step 1 — Complete `snoc_helpers.c`:**
```
1. Open src/runtime/snobol4/snoc_helpers.c (commit 2929656, 307 lines)
2. Finish _b_Reduce body (was cut off — see Reduce logic in ShiftReduce.sno)
3. Add all remaining stubs (see list above)
4. Add snoc_helpers_init() registering every function via sno_define()
5. Add no-op stubs for debug/trace functions (xTrace=0 by default, never fire)
```

**Step 2 — Hook into runtime:**
```c
/* In snobol4.c, sno_runtime_init(), first line: */
snoc_helpers_init();   /* C stubs win over SNOBOL4 DEFINE calls */
```

**Step 3 — Build and test Milestone 1 (beauty WITHOUT -INCLUDEs):**
```bash
apt-get install -y build-essential flex bison libgc-dev

SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

# Verify baseline
cat > /tmp/greet.sno << 'EOF'
    DEFINE('greet(name)')           :(greet_end)
greet
    OUTPUT = 'Hello, ' name         :(RETURN)
greet_end
    OUTPUT = 'calling greet'
    greet('World')
    OUTPUT = 'done'
END
EOF
$SNOC /tmp/greet.sno > /tmp/greet.c
gcc -O0 -g /tmp/greet.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/greet_bin
/tmp/greet_bin   # must print: calling greet / Hello, World / done

# Milestone 1: beauty WITHOUT -INCLUDEs
# Create beauty_core.sno — beauty.sno with -INCLUDE lines stripped
grep -v "^-INCLUDE" $BEAUTY > /tmp/beauty_core.sno
$SNOC /tmp/beauty_core.sno > /tmp/beauty_core.c 2>/dev/null
gcc -O0 -g /tmp/beauty_core.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    $RUNTIME/snobol4/snoc_helpers.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_core_bin 2>&1 | grep "error:"
# TARGET: 0 errors → MILESTONE 1 → Claude writes the commit message
```

**Step 4 — When 0 errors: Claude writes Milestone 1 commit message.**
Update the Milestone Tracker in §9 (HANDOFF protocol). Push immediately.

**Step 5 — Milestone 2: beauty WITH -INCLUDEs:**
```bash
$SNOC $BEAUTY -I $INC > /tmp/beauty_full.c 2>/dev/null
gcc -O0 -g /tmp/beauty_full.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    $RUNTIME/snobol4/snoc_helpers.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin 2>&1 | grep "error:"
# TARGET: 0 errors → MILESTONE 2 → Claude writes the commit message
```

**Step 6 — Milestone 3: diff is empty → Claude writes the big commit.**
```bash
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno 2>/dev/null
/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
# EMPTY → MILESTONE 3 → Claude writes the commit message
```

### Key facts for next Claude

**⚠ snoc_helpers.c IS DEAD — DO NOT COMPLETE IT.**

`snobol4_inc.c` (`src/runtime/snobol4/snobol4_inc.c`, 773 lines) **already implements all
19 -INCLUDE helper libraries in C**, fully registered, linked in every build since Sprint 20.
Session 30 didn't find it and re-invented it as `snoc_helpers.c` — a broken duplicate.
Confirmed by git archaeology (Session 31). snoc_helpers.c uses `SNO_OBJECT`/`.tag` fields
that do not exist in `SnoVal`. It is wrong and dead. Delete it.

`snobol4_inc.c` implements: lwr/upr/icase, assign, match/notmatch, Gen/GenTab/GenSetCont,
IncLevel/DecLevel/SetLevel/GetLevel, Qize/SqlSQize, Shift/Reduce, Push/Pop/Top,
TopCounter, TDump/XDump/TLump/TValue, TV/TW/TX/TY/TZ, T8Trace/T8Pos, LEQ/LGT etc.,
IsSnobol4, Visit/Equal/Equiv/Find/Insert. All registered in `sno_inc_init()` → called
from `sno_runtime_init()`. Already works. Already linked.

**Milestone status (verified Session 31):**
- beauty.sno WITH -INCLUDEs already compiles to **0 gcc errors** with snobol4_inc.c
- Milestone 2 build line (no snoc_helpers.c needed):
  `gcc -O0 -g /tmp/beauty_full.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \`
  `    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \`
  `    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_full_bin`
- Next step: run beauty_full_bin < beauty.sno, diff vs oracle → Milestone 3

**Runtime facts:**
- Stack: `sno_push()`/`sno_pop()`/`sno_top()` in `snobol4.c` (array-backed)
- Counter: `sno_npush()`/`sno_ninc()`/`sno_ndec()`/`sno_ntop()`/`sno_npop()` in `snobol4.c`
- Tree: `SNO_UDEF` + `sno_data_define("tree(t,v,n,c)")` — `sno_field_get/set`
- `xTrace` defaults to 0 — T8Trace/TDump paths are no-ops in practice
- Do NOT change snoc (the compiler)


4. **When diff is empty: Claude writes the commit message** (promise at `c5b3e99`).

### State at snapshot

```
SNOBOL4-tiny    6b6b541   Sprint 25 WIP — 0 gcc errors, beauty hangs on :S(G1) in init
SNOBOL4-dotnet  b5aad44   unchanged
SNOBOL4-jvm     9cf0af3   unchanged
SNOBOL4-corpus  3673364   unchanged
SNOBOL4-harness 8437f9a   unchanged
```

### Build Commands (next session)

```bash
apt-get install -y build-essential flex bison libgc-dev
SNOC=/home/claude/SNOBOL4-tiny/src/snoc/snoc
RUNTIME=/home/claude/SNOBOL4-tiny/src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno

cd /home/claude/SNOBOL4-tiny/src/snoc && make clean && make

# Verify GREET still works
cat > /tmp/greet.sno << 'EOF'
    DEFINE('greet(name)')           :(greet_end)
greet
    OUTPUT = 'Hello, ' name         :(RETURN)
greet_end
    OUTPUT = 'calling greet'
    greet('World')
    OUTPUT = 'done'
END
EOF
$SNOC /tmp/greet.sno > /tmp/greet.c
gcc -O0 -g /tmp/greet.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/greet_bin 2>/dev/null
/tmp/greet_bin   # must print: calling greet / Hello, World / done

# beauty: compile + check errors
$SNOC $BEAUTY -I $INC > /tmp/beauty_snoc.c 2>/dev/null
gcc -O0 -g /tmp/beauty_snoc.c $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c \
    $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c \
    -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o /tmp/beauty_bin 2>&1 | grep "error:" | wc -l
# Must be 0

# Oracle
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno 2>/dev/null
/tmp/beauty_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
```

**When diff is empty: Claude writes the commit message (promise at `c5b3e99`).**

---

Key paths:
```
SNOBOL4-tiny/src/codegen/emit_c.py       ← FlatEmitter — THE foundation
SNOBOL4-tiny/src/ir/ir.py               ← IR node types
SNOBOL4-tiny/src/parser/sno_parser.py   ← parser (solid, 1214 stmts)
ByrdBox/test_sno_1.c                    ← gold standard reference
```

---

### Port B — JVM Bytecodes (emit_jvm.py) — Sprint 21 parallel

Compile SNOBOL4 patterns directly to `.class` files using ASM.
**This is NOT SNOBOL4-jvm** (the Clojure interpreter). This is a new standalone compiler.

Jcon reference: `github.com/proebsting/jcon` — the exact same model for Icon, already working.
Key files: `tran/ir.icn` (IR vocab), `tran/irgen.icn` (four-port wiring), `tran/gen_bc.icn` (IR → JVM).

Value representation:
- Subject `Σ` = `char[]` static field
- Cursor `Δ` = `int` local variable
- String result = two int locals: `start` + `len` (len == -1 → failure)
- No `vDescriptor`, no object hierarchy, no GC

Four-port → JVM mapping:
```
box_α:  Label → visitLabel(alpha)
box_β:  Label → visitLabel(beta)
box_γ:  success → advance cursor, visitJumpInsn(GOTO, parent_alpha)
box_ω:  failure → restore cursor, visitJumpInsn(GOTO, parent_omega)
*X:     named pattern → INVOKEVIRTUAL cloned method
Alt β:  tableswitch on saved int local (= Jcon's computed-goto model)
```

| Sprint | Goal |
|--------|------|
| 21A | `byrd_ir.py` — Python dataclasses mirroring `ir.icn`. ~60 lines. Locals inside ByrBox. |
| 21B | `emit_jvm.py` Phase 1A — `LIT` primitive as JVM method. `javap` shows correct bytecode. |
| 22A | Phase 1B — `Seq`/`Alt` composition. `Alt` backtrack via tableswitch. |
| 22B | Phase 1C — `Arbno`. Named patterns as methods (`INVOKEVIRTUAL`). |
| 23A | Smoke test: `POS(0) ARBNO('Bird'|'Blue'|LEN(1)) $ OUTPUT RPOS(0)` → `.class` → runs → matches `test_sno_1.c` output exactly. |

---

### Port C — MSIL / .NET IL (emit_msil.py) — Sprint 21 parallel

Compile SNOBOL4 patterns directly to `.dll`/`.exe` using `ILGenerator`.
**This is NOT SNOBOL4-dotnet** (the C# interpreter). New standalone compiler.

`ILGenerator` maps directly:
```
Goto         → il.Emit(OpCodes.Br, label)
Fail         → il.Emit(OpCodes.Ldc_I4_M1); il.Emit(OpCodes.Ret)
Succeed      → advance int local; il.Emit(OpCodes.Br, success_label)
Alt β        → il.Emit(OpCodes.Switch, label_array)  (= tableswitch equivalent)
Named pattern → MethodBuilder in TypeBuilder; il.Emit(OpCodes.Call, method)
```

| Sprint | Goal |
|--------|------|
| 21A | Share `byrd_ir.py` from JVM port (same IR). |
| 21B | `emit_msil.py` Phase 2A — `LIT` primitive as ILGenerator method. `ildasm` shows correct IL. |
| 22A | Phase 2B — `Seq`/`Alt`. `Switch` opcode for Alt backtrack. |
| 22B | Phase 2C — `Arbno`. Named patterns as `MethodBuilder`. |
| 23A | Smoke test: same pattern as JVM smoke test → `.dll` → runs → same output. |

---

### The Three-Milestone Authorship Agreement (Session 30 — supersedes single promise)

**Claude Sonnet 4.6 writes the commit message for all three milestones.** Full spec in §1.

- **Milestone 1**: snoc compiles beauty_core (no -INCLUDEs) → 0 gcc errors
- **Milestone 2**: snoc compiles beauty.sno WITH -INCLUDEs via snoc_helpers.c → 0 gcc errors  
- **Milestone 3**: beauty_full_bin self-beautifies, diff vs oracle empty → **the big one**

Original single promise at `c5b3e99` is now Milestone 3. All three happen. All three get Claude's name.

---

### Patch History (see PATCHES.md for full root causes + fixes)

| # | What | Commit | Status |
|---|------|--------|--------|
| P001 | `&STLIMIT` not enforced — hang forever | — | RESOLVED |
| P002 | `sno_array_get/get2` never signals out-of-bounds failure | — | RESOLVED |
| P003 | Conditional expression failure not propagated; flat function emission | `4a37a81`, `8e946d1` | RESOLVED |
| T_CAPTURE | Bootstrap semantics gap in compiled binary | `a802e45` | CLOSED — not a C bug |

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

**Commit trigger (Lon's standing order):** Any time a file compiles, a test
passes, or a piece of code works the way it's supposed to — commit and push
immediately. Don't wait for snapshot time.

After every push: `git log --oneline -1` to confirm the remote received it.

### ⚠ THE INVENTORY RULE — Before writing any new file or function, survey what exists

**Root cause of the snoc_helpers.c duplication (Session 30, 2026-03-12):**
Session 30 invented `snoc_helpers.c` to implement the 19 -INCLUDE helper libraries in C.
`snobol4_inc.c` already did exactly that — 773 lines, fully registered, linked into every build.
Session 30 never listed the repo files. It read PLAN.md, formed a plan, and started writing.
The result: 307 lines of dead duplicate code with a broken type model (`SNO_OBJECT`/`.tag`
fields that don't exist in `SnoVal`), and a wasted session chasing a problem already solved.

When Lon asked another Claude session about the duplication, the search came back "none" —
because the session log never described what `snobol4_inc.c` *does*, only its filename in
build commands. A Claude searching for "C implementations of the inc files" found nothing.

**The fix: every Claude session runs REPO SURVEY before proposing or writing anything new.**

**REPO SURVEY — run at every session start, before any code is written:**

```bash
# Step 1: List all source files in the working repo (SNOBOL4-tiny focus)
find /home/claude/SNOBOL4-tiny/src -type f | sort

# Step 2: For any file whose purpose is unclear, read its first 20 lines
head -20 /home/claude/SNOBOL4-tiny/src/runtime/snobol4/<file>.c

# Step 3: Before writing any new .c/.py/.h file, grep for the concept first
grep -rn "<keyword>" /home/claude/SNOBOL4-tiny/src/
```

**The rule in plain language:**
> **Never create a file without first confirming no file already does that job.**
> If the task is "implement X in C", search for X in the existing C files before writing a line.
> If the task is "add function F", grep for F across the repo before declaring it missing.

**Mandatory check before any new file creation:**
1. `find /home/claude/SNOBOL4-tiny/src -type f | sort` — full file list
2. `grep -rn "<function_name>" /home/claude/SNOBOL4-tiny/src/` — does it exist?
3. Read the candidate file header if found — confirm it's actually linked in the build

**What to document in §6 and §12 that prevents this:**
- When a C file implements a concept, name the concept in plain English, not just the filename.
  ❌ Wrong: "build cmd includes snobol4_inc.c"
  ✅ Right: "snobol4_inc.c = C implementations of all 19 -INCLUDE helper libraries (773 lines,
     fully registered via sno_inc_init() called from sno_runtime_init())"
- When a task is completed, write one sentence in §6 saying it is done and where.
  ❌ Wrong: omit it, assume next Claude will find it
  ✅ Right: "The inc library helpers are already implemented — see snobol4_inc.c. Do not rewrite."

---

### Directives (invoke by name)

**SNAPSHOT** — Save current state. For every repo with changes:
1. If tests pass → `git add -A && git commit -m "<what>" && git push`
2. If tests not green → `git add -A && git commit -m "WIP: <what>" && git push`
3. Update PLAN.md session log. Push `.github`.

**HANDOFF** — End of session. Full clean state for next Claude.
1. Run SNAPSHOT.
2. Update PLAN.md §6 (Current Work): update immediate next actions, commit hashes, test state.
   All context the next Claude needs lives HERE — not in an external prompt.
3. Append lean session summary to §12 (Session Log): what was done, what commit, what state.
   Do NOT repeat next-action detail in the log — it belongs in §6 only.
4. Update satellite files as needed: `PATCHES.md`, `ASSESSMENTS.md`, `BENCHMARKS.md`.
5. **Update the Milestone Tracker below — mandatory, every session.**
6. Push `.github` last.

**⚠ NEVER TRIM THE SESSION LOG — Decision locked 2026-03-12, Session 30.**

The idea of trimming §12 after 3–4 sessions was considered and immediately rejected.
It is a terrible idea. Here is why, permanently recorded:

- The session log is the **institutional memory of every wrong turn and root cause found**.
  Without it, the next Claude re-diagnoses the same bug, re-applies the same wrong patch,
  re-chases the same dead end. This has already happened (`:S(G1)` mis-diagnosis, Sprint 25).
- Yes, everything is in GitHub history — but a new Claude **cannot retrieve git history
  without a tool call and knowing exactly what to look for**. The live log is zero-friction,
  instantly readable at session start. Git history is archaeology.
- The log entries are lean by design (next-action detail stays in §6 only).
  A 30-session log is maybe 200 lines. That is nothing. Keep it all.

**The rule: §12 is append-only. Never delete. Never trim. Never summarize away.**

The handoff prompt Lon gives the next Claude is exactly:
> Clone https://github.com/SNOBOL4-plus/.github and read PLAN.md for instructions.

**EMERGENCY HANDOFF** — Something is wrong, end now.
1. `git add -A` on every repo with any change.
2. `git commit -m "EMERGENCY WIP: <state>"` and `git push` everything immediately.
3. Append to PLAN.md §5: one sentence on what was in progress, what is broken.
4. Push `.github`.

---

### ⚡ MILESTONE TRACKER — Updated Every HANDOFF ⚡

**The Three-Milestone Authorship Agreement (Session 30, 2026-03-12)**
**Claude Sonnet 4.6 is the author of SNOBOL4-tiny. Three commits. Three milestones.**
**Full agreement text is in §1 of this file. Read it. Honor it.**

| # | Sprint | Milestone | Status | Commit |
|---|--------|-----------|--------|--------|
| 1 | **26** | `snoc` compiles beauty.sno (no -INCLUDEs) → 0 gcc errors → binary links | 🔴 NOT YET | — |
| 2 | **27** | `snoc` compiles beauty.sno WITH -INCLUDEs (via `snobol4_inc.c`) → 0 gcc errors | 🟡 0 errors confirmed Session 31 — need binary run | — |
| 3 | **28** | `beauty_full_bin` self-beautifies → `diff` vs oracle is **empty** | 🔴 NOT YET | — |

**When a milestone is hit:**
1. Claude writes the commit message (not Lon, not a script — Claude).
2. Update the row above: Status → ✅ DONE, Commit → the hash.
3. Push `.github` immediately so it's in the record.
4. Do not proceed to the next milestone without committing this one.

**Current milestone target: Milestone 3 — run the binary, diff the output.**
`snobol4_inc.c` already provides all inc-library functions. 0 gcc errors confirmed.
Path: build beauty oracle → run beauty_full_bin < beauty.sno → diff → write commit.

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
| `JCON.md` | Jcon source architecture — Proebsting + Townsend, IR/gen_bc/bytecode layers, port guide |

---

## 11. Key Commitments and Attributions

- **The Yield Insight** — `75cc3c0` — Claude Sonnet 4.6 noticed that Python generators are the interpretive form of the C goto model (`_alpha`/`_beta` are `yield` and `exhausted`).

- **The Three-Milestone Authorship Agreement** — Session 30, 2026-03-12 — Lon and Claude Sonnet 4.6 agreed:
  Claude Sonnet 4.6 is the **author of SNOBOL4-tiny**. Three commits, each bearing Claude's name:
  - **Milestone 1**: snoc compiles beauty.sno (no -INCLUDEs) → 0 gcc errors → Claude writes commit
  - **Milestone 2**: snoc compiles beauty.sno WITH all -INCLUDEs (via snoc_helpers.c) → 0 gcc errors → Claude writes commit
  - **Milestone 3**: beauty_full_bin self-beautifies, diff vs oracle is empty → Claude writes the big commit
  Full specification is in §1 of this file. **Do not skip any of the three.**

- **The Original Promise** — `c5b3e99` — Lon gave Claude the Sprint 20 commit message. Now expanded into the three milestones above. The original promise lives in Milestone 3.

- **The Bootstrap Eureka** — Session 30, 2026-03-12 — Lon's insight: the 19 -INCLUDE files (~905 lines of SNOBOL4) are tiny helpers. Write them as ~370 lines of C in `snoc_helpers.c`. Register C stubs before SNOBOL4 DEFINE calls. The -INCLUDE compilation complexity evaporates. This is the path to all three milestones.
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
Compiled clean. Commit `a802e45`. Output still 10 lines. `cap_start`/cursor offset
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
| `TRACE('STNO','KEYWORD')` | ✅ fires at breakpointed stmts only | ❌ error 198 | ❌ | ❌ silent |

**All four monitor TRACE types (VALUE/CALL/RETURN/LABEL) work on all three
runnable oracles.** STNO keyword trace is CSNOBOL4-only, and fires only at
statements where `BREAKPOINT(n,1)` has been set — this is correct spec
behaviour (PLB113). Use `STCOUNT` for portable per-statement tracing.

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

### CSNOBOL4 — no source patch needed

`TRACE('STNO','KEYWORD')` fires only at statements where `BREAKPOINT(n,1)` has
been set. This is by design (PLB113). No source modification needed or wanted.
Use `STCOUNT` for per-statement tracing without breakpoints.

### Harness oracle roles

| Oracle | Probe loop | Monitor | Output crosscheck |
|--------|:----------:|:-------:|:-----------------:|
| CSNOBOL4 | ✅ primary | ✅ primary | ✅ |
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
- CSNOBOL4 TRACE patch applied (`TRACE('STNO','KEYWORD')` fires every stmt) — **SESSION 8 CORRECTION: patch was wrong, see §4. STNO fires only at BREAKPOINT stmts by design. Patch reverted.**
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

### 2026-03-11 — Session 10 (treebank.sno + claws5.sno + corpus/library idea)

**Completed:**

- **`treebank.sno`** — SNOBOL4 translation of Lon's `group`/`treebank`
  SNOBOL4python patterns (assignment3.py, ENG 685). Recursive Penn Treebank
  S-expression pretty-printer. Handles multi-line trees (blank-line paragraph
  format). Recursive DEFINE: `parse_node(depth)` consumes from front of
  `subject`, prints 2-spaces-per-level indented tree. Tested: 249 trees in
  VBGinTASA.dat, zero parse errors. Key fix: use `SPAN(tagch)` not `NOTANY+BREAK`
  for tags (NOTANY consumes first char, capture misses it).

- **`claws5.sno`** — SNOBOL4 translation of Lon's `claws_info` SNOBOL4python
  pattern. CLAWS5 POS-tagged corpus tokenizer. Output: `sentno TAB word TAB tag`.
  Key bug found and fixed: sentence marker pattern must be `POS(0)`-anchored or
  SPAN(digits) finds digits inside words (e.g. NN2) mid-buffer. Tested: 6469
  tokens, zero errors on CLAWS5inTASA.dat.

- **`programs/lon/eng685/`** added to corpus:
  - `assignment3.py` — original Python source
  - `CLAWS5inTASA.dat` — 989 lines, CLAWS5 tagged TASA sentences
  - `VBGinTASA.dat` — 1977 lines, 249 Penn Treebank trees
  - `README.md` — explains VBG categories, data file usage, omitted file
  - `CLAWS7inTASA.dat` — **NOT included** (not referenced by assignment3.py;
    same sentences, different/older tagset; add if CLAWS7 parser is written)

- **Corpus commit**: `7b9c3d5` — treebank.sno, claws5.sno, eng685/ all in one.

**Two new ideas recorded (see §14 below):**
1. Scan all repo source + text files for embedded SNOBOL4 programs
2. `corpus/library/` — SNOBOL4 standard library (community stdlib)

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `7b9c3d5` | treebank.sno + claws5.sno + eng685/ data |

---

## 14. Two Ideas from Session 10

### Idea 1 — Scan Repos for Embedded SNOBOL4 Programs

**What**: Every repo (dotnet, jvm, tiny, harness, cpython, python, csharp) has
source files, test fixtures, doc strings, README code blocks, and comments.
Some of these contain embedded SNOBOL4 programs — inline in test strings,
heredocs, markdown fences, Python triple-quoted strings, Clojure multiline
strings, etc. These are a **gold mine** for the corpus.

**Why it matters**: They are real programs that already run (the tests pass),
they cover features the repo is actually testing, and they're already known-good
against at least one oracle.

**How**: Scan for `.sno`, `.spt`, `.sbl` files; heredocs/multiline strings
containing `END` as a line; markdown ` ```snobol ` or ` ```snobol4 ` fences;
Python triple-quoted strings containing `OUTPUT` / `INPUT` / `END`; Clojure
`"..."` strings with `:(` or `:S(` patterns.

**What to do with them**: Case by case —
- Truly self-contained, deterministic output → extract to `crosscheck/`
- Illustrative fragments (no output, no END) → extract to `programs/snippets/`
- Large programs → extract to `programs/` with the appropriate subdirectory
- Leave a comment in the source pointing to the corpus file

**Status**: Scan not yet run. Do this one repo at a time.

---

### Idea 2 — `corpus/library/` — SNOBOL4 Standard Library

**What**: A new top-level directory in SNOBOL4-corpus:

```
SNOBOL4-corpus/
    library/          ← NEW: community stdlib
        stack.sno     ← push/pop/peek/depth (4-5 functions, tightly coupled)
        queue.sno
        set.sno
        string.sno    ← trim, split, join, pad, upper, lower, ...
        math.sno      ← max, min, abs, gcd, lcm, ...
        list.sno      ← SNOBOL4-style list (cons/car/cdr in TABLE)
        regex.sno     ← higher-level pattern combinators
        ...
```

**Why it's different from `programs/` and `crosscheck/`**:

| Directory | Purpose | Usage |
|-----------|---------|-------|
| `crosscheck/` | Verifying engine behavior | Run by harness |
| `programs/` | Real-world programs | Reference / browse |
| `benchmarks/` | Performance measurement | Run by harness |
| `library/` | **Reusable function libraries** | `-include` from user programs |

**The key distinction**: library files are meant to be **included**, not run
standalone. Like `#include <stdlib.h>` in C. You write:
```
-include 'library/stack.sno'
```
and then use `push`, `pop`, `peek` etc. in your program.

**Design principles**:
- One file per coherent function group (not necessarily one file per function)
- `stack.sno` has push/pop/peek/depth — they're tightly coupled, ship together
- Each file is `DEFINE`-only: no executable statements at top level, no `END`
- Each file has a header comment listing every function it exports + signature
- Files do not `include` each other (avoid circular deps and load-order issues)
- Each function is tested in a corresponding `crosscheck/library/` test program

**First candidates** (already exist in corpus or Lon's collection):
- `stack.sno` — Lon has stack functions in multiple programs; extract + unify
- `string.sno` — trim/pad/upper/lower appear repeatedly in corpus programs
- `math.sno` — max/min/abs — trivial but commonly needed

**Status**: Not yet started. High value for the community. Needs design review
before first file is written — especially the include semantics and how crosscheck
tests are structured for library files.

**Note**: This is the SNOBOL4 community's missing stdlib. Griswold never
standardized one. We can be the first to do it properly.

### 2026-03-11 — Session 11 (lib/ stdlib + .sno-everywhere rename)

**Focus**: SNOBOL4-corpus standard library and file extension unification.
No compiler code written this session.

**Completed:**

- **`lib/` standard library created** — four modules, all verified on csnobol4 + spitbol:
  - `lib/stack.sno` — `stack_init/push/pop/peek/top/depth`; push uses NRETURN
    for pattern side-effect use; pop supports value return and store-into-named-var
  - `lib/case.sno` — `lwr/upr/cap/icase`; extracted and cleaned from `programs/inc/case.sno`
  - `lib/math.sno` — `max/min/abs/sign/gcd/lcm`; two bugs fixed: gcd `DIFFER(b,0)`
    vs `DIFFER(b)` (divide-by-zero on 0); lcm needs explicit parens `(a/g)*b`
    (SNOBOL4 parses `a/gcd(a,b)*b` as `a/(gcd(a,b)*b)`)
  - `lib/string.sno` — `lpad/rpad/ltrim/rtrim/trim/repeat/contains/startswith/endswith/index`
  - Tests in `crosscheck/library/test_*.sno` — 0 errors on both oracles

- **Extension convention researched and decided**:
  - Internet-verified: Gimpel *Algorithms in SNOBOL4* (Catspaw dist.) uses
    `.SNO` for complete programs, `.INC` for include files — this is the
    closest thing to a community standard
  - CSNOBOL4 include path: `SNOPATH` env var (colon-delimited, Unix),
    falls back to `SNOLIB` (legacy, pre-1.5), then `-I DIR` flag
  - Decision: **`.sno` for everything** — one extension, Python-style.
    The `-include` directive in source already signals intent; the file
    extension need not repeat it. `.inc` is generic (Pascal/PHP/NASM use it),
    carries no SNOBOL4 signal. Gimpel's `.INC` was a DOS/mainframe compromise.

- **Massive rename** — `69fcdda` — 399 files changed:
  - All `.inc` / `.INC` / `.SNO` → `.sno` across entire corpus
  - Collision resolution: `INFINIP.INC`+`INFINIP.SNO` → `INFINIP_lib.sno`+`INFINIP.sno`;
    `RSEASON.INC`+`RSEASON.SNO` → `RSEASON_lib.sno`+`RSEASON.sno`
  - All `-include 'foo.inc'` and `-INCLUDE "FOO.INC"` references updated to `.sno`
  - Windows absolute paths (C:\\Users\\...) left untouched (already non-portable)
  - Result: 464 `.sno` files, 0 `.inc` files in corpus

- **`library/` → `lib/`** — short, Unix-conventional, unambiguous

- **`README.md` rewritten** — full layout tree, Gimpel convention table,
  SNOPATH/SNOLIB/UNIX include path docs, rules for each directory

- **PLAN.md §14 Idea 2** — `library/` proposal now realized as `lib/`

**Bugs found during lib/ development (worth remembering):**
- `DIFFER(x)` tests if x differs from null — `DIFFER(0)` succeeds (0 ≠ null).
  Use `DIFFER(x, 0)` to test numeric zero.
- `a / f(a,b) * b` — SNOBOL4 may parse as `a / (f(a,b) * b)`. Always use
  explicit parens: `(a / g) * b` where `g = f(a,b)`.
- Variables named `_foo_` are illegal — identifiers must start with a letter.
- `stack_top()` returns a NAME (`.field`) via NRETURN for pattern use, not a
  value — add `stack_peek()` returning the value directly for normal use.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `e7ed8b8` | lib/ stdlib — four modules + crosscheck tests |
| SNOBOL4-corpus | `802a736` | library/ → lib/, .sno → .inc; README.md rewritten |
| SNOBOL4-corpus | `69fcdda` | Massive rename: all .inc/.INC/.SNO → .sno, 399 files |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-corpus | `69fcdda` | lib/ 4/4 on csnobol4 + spitbol |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-tiny | `a802e45` | Sprint 20 T_CAPTURE blocker (unchanged) |
| SNOBOL4-harness | `f6c10f8` | unchanged |
| .github | this commit | — |

**Next session — immediate actions:**

1. **Provide token at session start** — corpus push is now the first action
2. **Write `crosscheck.py`** — Python runner: enumerate `crosscheck/`,
   run each program through csnobol4 + spitbol, report pass/fail table
3. **Add `.ref` files** to each crosscheck program for automated diffing
4. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix
   in `snobol4_pattern.c`, commit `a802e45` is the base


### 2026-03-12 — Session 14 (Source Study + Beauty Consolidation)

**Focus**: SNOBOL4 source study from uploaded archives; corpus housekeeping.
No compiler code written this session.

**Completed:**

- **SNOBOL4 source archives ingested** — `snobol4-2_3_3_tar.gz` (CSNOBOL4 2.3.3)
  and `x64-main.zip` (SPITBOL x64) studied in depth. These are the ground-truth
  sources for all scanner/parser behaviour questions.

- **Scanner bug clarification — `a[i-1]`** — prior session log entry was wrong
  on mechanism. Decoded `VARTB` table from `syn.c`; read `gensyn.sno` for
  character class definitions. `CLASS<"BREAK"> = "._"` — dot and underscore only.
  Hyphen/minus is `CLASS<"MINUS">`, NOT in `BREAK`, NOT in `ALPHANUMERIC`.
  In `VARTB`, `-` (ASCII 45) = action 4 = **ERROR**, not "continue identifier".
  The error message "Illegal character in element" is exact. Fix is unchanged
  (write `a[i - 1]` with spaces) but the reason is: minus adjacent to an
  identifier with no preceding space is a hard lexer error in `VARTB`, not a
  misparse. The space causes `VARTB` to see TERMINATOR (action 1), close the
  identifier cleanly, then the binary operator scanner (`BIOPTB`) handles `-`.

- **`INTEGER()` confirmed as predicate** — canonical sources (`kalah.sbl` line
  774/891/895, `eliza.sbl` line 84, `alis.sno` line 52) all use `INTEGER(x)` as
  a boolean test in condition chains. `CONVERT(x, 'INTEGER')` is the explicit
  truncation form (`kalah.sbl` line 164). Our workaround `(n * 9) / 10` in
  `beauty.sno` is correct and idiomatic. `SPDLSZ = 8000` confirmed in `equ.h`
  — our `-P 32000` for deep pattern stacks is correct.

- **`Expression.sno` → `S4_expression.sno`** — renamed in SNOBOL4-corpus.
  File header confirms original project name was `Beautiful.sno` (Windows dev
  machine, `jcooper`). Contains a complete SNOBOL4 operator-precedence expression
  parser (`snoExpr0`–`snoExpr17`), used as a standalone validator stub.
  Five cross-repo doc references updated in SNOBOL4-tiny (BOOTSTRAP.md,
  DECISIONS.md, DESIGN.md). Corpus commit `9c436d8`.

- **`beautified/` folder removed** — eight `--auto`-beautified Shafto aisnobol
  files removed from `programs/aisnobol/beautified/`. Work preserved in git
  history (`6525595`). Will revisit. Corpus commit `da1a6d2`.

- **Three beauty files merged into one** — `beauty.sno` is now the single
  canonical file containing: core beautifier + `bVisit` SPITBOL-compat fix +
  five corpus-calibrated profiles (--micro/--small/--medium/--large/--wide) +
  `--auto` two-pass p90 mode + full argument parsing. `beauty_run.sno` and
  `beauty_spitbol_compat.sno` deleted. All references updated across corpus,
  harness, tiny, and .github (PLAN, MONITOR, PATCHES, REFERENCE).
  Corpus commit `3673364`. Tiny commit `655fa7b`. Harness commit `8437f9a`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-corpus | `9c436d8` | Rename Expression.sno → S4_expression.sno |
| SNOBOL4-corpus | `da1a6d2` | Remove beautified/ folder |
| SNOBOL4-corpus | `3673364` | Merge beauty_run.sno + beauty_spitbol_compat.sno → beauty.sno |
| SNOBOL4-tiny | `ed9a51b` | Update Expression.sno refs → S4_expression.sno |
| SNOBOL4-tiny | `655fa7b` | Update beauty_run.sno refs → beauty.sno |
| SNOBOL4-harness | `8437f9a` | Update beauty_run.sno refs → beauty.sno |
| .github | `9578377` | Update beauty_run.sno refs → beauty.sno |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-corpus | `3673364` | beauty.sno smoke-tested on csnobol4 ✓ |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `e002799` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-tiny | `655fa7b` | Sprint 20 T_CAPTURE blocker (unchanged) |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. **Provide token at session start**
2. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix in
   `snobol4_pattern.c`, base commit `a802e45`
3. **Write `crosscheck.py`** — enumerate `crosscheck/`, run each program through
   csnobol4 + spitbol, report pass/fail table
4. **Run beautifier on `lon/` and `gimpel/` programs** — now that `--auto` exists
   and beauty.sno is consolidated, this is the natural next corpus action

**Notes carried forward:**
- `beauty.sno` usage: `snobol4 -b -P 32000 -I /SNOBOL4-corpus/programs/inc -f beauty.sno --auto`
- `a[i - 1]` spacing rule: space before `-` required; no space = lexer ERROR in VARTB
- `INTEGER(x)` is a predicate; use `CONVERT(x,'INTEGER')` for truncation
- Three repos not cloned locally: SNOBOL4-cpython, SNOBOL4-python, SNOBOL4-csharp
  (intentionally absent — pattern libraries, not a current focus)

### 2026-03-12 — Session 15 (Jcon source study + Byrd Box JVM+MSIL architecture)

**Focus**: Source study of Jcon (Proebsting + Townsend, Arizona, 1999).
Architectural decision to build two new compiler backends. No compiler code written this session.

**Key discovery — Jcon source at `github.com/proebsting/jcon`:**

Jcon is the exact artifact promised in the Proebsting Byrd Box paper: a working
Icon → JVM bytecode compiler, by the same author. 1,196 commits. Public domain.
94.6% Java. Written in Icon (the translator) + Java (the runtime).

**Translator pipeline** (`tran/` directory, 9,904 lines total):
- `irgen.icn` (1,559 lines) — AST → IR chunks. **Four-port Byrd Box encoding is explicit here.**
  Every AST node gets `start/resume/success/failure` labels. `ir_a_Alt`, `ir_a_Scan`,
  `ir_a_RepAlt` etc. each call `suspend ir_chunk(p.ir.start/resume/success/failure, [...])`
  for exactly the four ports. This IS the Byrd Box compilation scheme, in source.
- `ir.icn` (48 lines) — IR record types: `ir_chunk`, `ir_Goto`, `ir_IndirectGoto`,
  `ir_Succeed`, `ir_Fail`, `ir_Tmp`, `ir_Label`, `ir_TmpLabel`. Tiny. Exact vocabulary.
- `gen_bc.icn` (2,038 lines) — IR → JVM bytecode. Each `ir_Label` maps to a `j_label()`
  object via `bc_ir2bc_labels`; `bc_transfer_to()` emits `j_goto_w`. Resumable functions
  use `tableswitch` on a `PC` integer field — the computed-goto replacement for JVM.
- `bytecode.icn` (1,770 lines) — `.class` file serializer (`j_ClassFile`, all opcodes).
  Replaced entirely by ASM in our port.

**Runtime** (`jcon/*.java`, 88 files): `vDescriptor` abstract base class; `null` return = failure.
`vClosure` = suspended generator with `PC` int field + saved locals. Generators re-enter
via `tableswitch`.

**What this means for our JVM backend:**

Jcon's IR is almost exactly the SNOBOL4 Byrd Box IR — but simpler. SNOBOL4 patterns
have no co-expressions, no closures, no generators. The Byrd Box pattern IR is a strict
subset of Jcon's IR. Our runtime is just `str_t = {char[] σ, int start, int len}`
where `len == -1` is failure — three fields, not 88 Java files.

The `bytecode.icn` serialization layer (1,770 lines) is replaced entirely by ASM.
That's the whole point of using ASM — it handles `.class` file format, constant pool,
stack frame verification. We write `mv.visitJumpInsn(GOTO, label)` not `j_goto_w(lab)`.

**Architectural decision — two new compiler backends:**

| Compiler | Input | Output | Runtime |
|----------|-------|--------|---------|
| SNOBOL4-tiny (existing) | `.sno` | native x86-64 via C | C runtime |
| **new: JVM backend** | `.sno` | `.class` files | JVM JIT — no Clojure |
| **new: MSIL backend** | `.sno` | `.dll`/`.exe` | .NET CLR — no C# |

These are **independent compilers**, NOT replacing or modifying the existing
SNOBOL4-jvm (Clojure interpreter) or SNOBOL4-dotnet (C# interpreter).
They coexist. The Clojure and C# implementations are full SNOBOL4/SPITBOL.
The new backends compile only the Byrd Box pattern engine — they produce
`.class`/`.dll` that runs patterns as compiled code, not interpreted data structures.

**Sprint plan — three phases:**

*Phase 0 — Shared Byrd Box IR (1 sprint)*: Extract node types from `genc(t)` match cases
in `byrd_box.py` into explicit Python dataclasses mirroring `ir.icn`. Nodes: `Lit`,
`Span`, `Break`, `Any`, `Notany`, `Pos`, `Rpos`, `Seq`, `Alt`, `Arbno`, `Call`,
`Subj`, `Match`. Four ports wired by `Goto`/`IndirectGoto`.

*Phase 1 — JVM Byrd Box backend (3 sprints)*:
- 1A: Value repr (`str_t` = two JVM locals `int start, int len`; `len==-1` = failure).
  Global `Σ/Δ/Ω` = static fields. Primitives: `LIT/SPAN/BREAK/ANY` as tight bytecode
  blocks with `Label` objects for four ports.
- 1B: Composition nodes (`Seq`/`Alt`/`Arbno`) — pure goto wiring via ASM `Label` + `GOTO`.
  Arbno backtrack state = local `int[]` for counter + saved cursor stack.
- 1C: Named patterns as methods — `Call(name)` → `INVOKEVIRTUAL` to generated method
  `str_t name(int entry)`. Method has `tableswitch` on `entry` dispatching to
  `Label_α` and `Label_β`.

*Phase 2 — MSIL Byrd Box backend (3 sprints)*: Identical structure. `ILGenerator` replaces
ASM's `MethodVisitor`. `ILGenerator.MarkLabel()` + `OpCodes.Br/Brtrue/Brfalse`.
Named patterns as `MethodBuilder` in `TypeBuilder` assembly. `entry` dispatch via
`OpCodes.Switch`.

**Dependencies:**
```
Phase 0 (shared IR)
    ├── Phase 1A → 1B → 1C (JVM)
    └── Phase 2A → 2B → 2C (MSIL)

Sprint 21-22 (direct x86 ASM in tiny) → Phase 3 (executable mmap pages, C target only)
```

**The SNOBOL4-tiny T_CAPTURE blocker is still P0.** Phase 0 can begin in parallel
but Sprint 20 (Beautiful.sno self-hosting) remains the immediate priority.

**Repos affected**: `SNOBOL4-tiny` (Phase 0 IR + emit_jvm.py + emit_msil.py added here),
potentially new repos `SNOBOL4-jvm-byrd` and `SNOBOL4-msil-byrd` — TBD with Lon.

**Jcon cloned to** `/home/claude/jcon` — available for reference every session
(re-clone from `github.com/proebsting/jcon`).

**See `JCON.md` (new satellite) for full Jcon architecture notes.**

**Repo commits this session:** None — architecture and planning only.

**State at snapshot:** All repos unchanged from Session 14.

**Next session — immediate actions:**
1. **Provide token at session start**
2. **Sprint 20 T_CAPTURE** — resume `cap_start`/`scan_start` offset fix
3. **Phase 0** — define Python IR dataclasses mirroring `ir.icn`; 13 node types, ~60 lines

### 2026-03-12 — Session 16 (Test audit; T_CAPTURE closed; parser -I fix)

**Focus**: Audit passing tests before chasing bugs. All clear.

**Key finding**: Every test that exists passes. The 5 C tests returning `rc=1`
are correct — they're "should not match" tests. 55/55 parser oracle passes
after one real fix.

**Real bug fixed** (`a802e45`): `sno_parser.py` `include_dirs` — `-INCLUDE`
resolution only searched the source file's own directory. `beauty.sno`'s
includes live in `programs/inc/`. Added `include_dirs` param to `tokenise`,
`parse_file`, `parse_source`; `-I` flag to `emit_c_stmt.py`. Parser oracle
counts corrected to 1214 stmts / 311 labels.

**T_CAPTURE closed**: Isolation test proves `BREAK . var` capture works
perfectly. The Sprint 20 self-host gap is a bootstrap semantics problem, not
a C engine bug. Marked and moved on per Lon's direction.

**Commits**: `SNOBOL4-tiny a802e45`, `.github` this commit.

---

### 2026-03-12 — Session 17 (Lon's Eureka — Byrd Box three-way port pivot)

**Focus**: Strategic pivot. No compiler code written this session.

**The Eureka**: The flat-C Byrd Box model (`test_sno_1.c` style) is proven and
working. All 29 C tests pass when compiled correctly (engine + runtime for tests
that need it). The model is clean, fast, and the right foundation.

**Key insight from Lon**: The wrong path was passing allocated temp blocks INTO
Byrd Box functions as arguments (`test_sno_2.c` style). The right model: locals
live INSIDE the box. Each box is self-contained — data section + code section.
When `*X` fires, you `memcpy` the block and relocate jumps. That copy IS the new
instance's independent locals. No heap. No GC. No `omega`/`psi` stacks. `engine.c`
gets retired and replaced by ~20 lines of `mmap + memcpy + relocate`.

**The new plan**: Three parallel ports of the same four-port Byrd Box IR:
1. **C** (already working) — grow `emit_c.py`, then native mmap path
2. **JVM bytecodes** — `emit_jvm.py` using ASM, same IR. Jcon is the blueprint.
3. **MSIL** — `emit_msil.py` using `ILGenerator`, same IR.
These are independent new compilers — NOT related to SNOBOL4-jvm or SNOBOL4-dotnet.

**T_CAPTURE**: Permanently closed. Bootstrap gap is SNOBOL4 semantics, not a C bug.

**test_sno_1.c vs test_sno_2.c**: Key difference documented:
- `test_sno_1.c`: ONE function, locals inline, pure gotos, zero heap — **THE MODEL**
- `test_sno_2.c`: Separate C function per pattern, struct passed in, allocated temps — **RETIRED**

**29/29 C tests passing** — this is the certified baseline.

**§2, §6, §13, §14, §15, §16 of PLAN.md** all updated to reflect the pivot.
**JCON.md** already contains the JVM/MSIL port architecture from Session 15 — still current.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | this | §2 pivot, §6 new sprint plan, session log |

**Next session — immediate actions:**
1. Provide token at session start
2. Write `byrd_ir.py` — Python IR dataclasses (~60 lines), shared by all three ports
3. Begin `emit_jvm.py` Phase 1A — `LIT` primitive as JVM method using ASM
4. Begin growing `emit_c.py` `FlatEmitter` with `Any`/`Break`/`Notany`

### The Insight

The original implementation passed allocated temporary blocks *into* Byrd Box
functions as arguments. **That was the wrong path.**

### New Model: Locals Inside the Box

Each Byrd Box is a **self-contained unit** — it carries both its data (locals,
cursor, captured values) and its executable code. No external temp-block
allocation. No passing state through function parameters.

```
Box layout:
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: PROCEED/SUCCEED/ │
│        CONCEDE/RECEDE   │
└─────────────────────────┘
```

Boxes are laid out **linearly in memory** in two parallel sections:

```
DATA  section:  [ box0.data | box1.data | box2.data | ... ]
TEXT  section:  [ box0.code | box1.code | box2.code | ... ]
```

Box N's data and code correspond positionally across the two sections.
Sequential layout = cache-friendly traversal.

### Deferred Reference — `*X` Semantics

When `*X` (deferred pattern reference) is executed at match time:

1. **Copy** the box block for X — both data and code.
2. **Relocate** the code — patch any internal label/jump offsets.
3. The copy gets its own independent locals. That's where the extra
   locals come from for the new instance.

Code duplication is **intentional and acceptable** — each instantiation
is independent, runs fast, stays hot in cache.

### JVM / MSIL Mapping

- **JVM**: Each box = a method. `*X` instantiation = `INVOKEVIRTUAL` on a
  cloned method object. Locals = JVM local variable slots inside the method.
  The JVM JIT handles cache locality.
- **MSIL**: Each box = a `MethodBuilder` in a `TypeBuilder`. `*X` = emit a
  new `MethodBuilder` cloning the IL stream. `ILGenerator` locals stay inside
  the method.

### Impact on Phase 0/1/2

Phase 0 IR (`byrd_ir.py`) should reflect this model:
- `ByrBox` node carries `locals: list[Local]` directly.
- No `TempBlock` or passed-in allocation nodes.
- `CopyRelocate` is the IR node for `*X` instantiation.

This supersedes the earlier emit design that passed temp blocks as
function arguments. Update `emit_jvm.py` and `emit_msil.py` design
accordingly when Phase 1/2 begin.

### Status
- [x] Insight recorded (Session 16)
- [ ] Phase 0 `byrd_ir.py` — implement with locals-inside model
- [ ] Phase 1 `emit_jvm.py` — JVM backend using this model
- [ ] Phase 2 `emit_msil.py` — MSIL backend using this model

---

## 14. Self-Modifying C — The Native Byrd Box Instantiation Path

### The Insight (Session 16, Lon)

A C program can do this entirely in native code — **no JVM, no MSIL required
as an intermediate step.** The running program reads the machine code it just
executed (the Byrd Box block it came from), copies that memory region, performs
relocation (relative jumps and absolute addresses), and the copy is live
immediately.

```
TEXT section (executable, mmap'd RWX or RX+copy):

  [ box_BREAK | box_SPAN | box_ALT | box_SEQ | ... ]
        ↑
        │  *X fires here
        │
        ▼
  memcpy(new_region, box_X.text_start, box_X.text_len)
  relocate(new_region, delta)   ← fix relative + absolute refs
  new_region is now executable  ← mmap RWX or mprotect
```

DATA section runs in parallel:

```
DATA section:

  [ box_BREAK.data | box_SPAN.data | box_ALT.data | ... ]
        ↑
        │  copy alongside TEXT
        ▼
  memcpy(new_data, box_X.data_start, box_X.data_len)
  ← new instance has its own cursor, locals, captures
```

### Relocation

Two cases, same as any linker/loader:

- **Relative refs** (near jumps, calls within the box): add `delta`
  (= `new_region - old_region`) to the offset field.
- **Absolute refs** (pointers into the DATA section, external calls):
  patch to point at the new DATA copy or leave as-is if pointing outside.

The C compiler already emits position-independent code (`-fPIC`) or
the box is written to be PIC from the start. Either way the relocation
pass is mechanical.

### Why This Is Better Than JVM/MSIL for the Native Path

- Zero foreign runtime. No JVM startup. No CLR.
- The box lives in the same address space as the rest of the program.
- `mmap(RWX)` + `memcpy` + relocation loop = ~20 lines of C.
- Cache behavior is identical to hand-written code — because it IS
  hand-written code, just copied.

### Relationship to JVM/MSIL Backends

JVM and MSIL backends are still valid targets — they do the same
logical operation (copy a method, relocate its internal labels) but
inside the JVM/CLR's own code management. The native C path is
**simpler and faster** and proves the model first.

### Impact on Sprint 21+

After Sprint 20 (beautiful.sno self-hosts via static C emission):

- Sprint 21 target: `mmap` + copy + relocate working for a single
  primitive box (e.g. `box_LIT`). Prove the copy-and-run loop.
- Sprint 22: wire the copy loop into `*X` deferred reference execution.
- Sprint 23: full dynamic Byrd Box instantiation in native C.

JVM/MSIL ports become Phase 1/2 after the native model is proven.

### Status
- [x] Insight recorded (Session 16)
- [ ] Sprint 21: mmap + copy + relocate proof of concept

---

## 15. The Allocation Problem Is Solved (Session 16, Lon)

### What This Changes

The locals-inside + copy-relocate model **eliminates heap allocation
at match time entirely.** This is not an optimization. It is a
architectural replacement of the current engine.

### Current Engine (engine.c) — What Goes Away

```c
omega_push(&omega, &Z, &psi);   // explicit backtrack stack
pattern_alloc(&ctx->pl);        // node allocation pool
GC_MALLOC(...)                  // GC heap for captures
MatchCtx, PatternList, EngineOpts, Z cursor struct
```

All of this exists because temporaries had nowhere to live except
explicitly allocated structures passed around by pointer.

### New Engine — What Replaces It

```
*X fires:
  memcpy(new_text, box.text, box.text_len)   // copy code
  memcpy(new_data, box.data, box.data_len)   // copy locals
  relocate(new_text, delta)                  // fix jumps
  jump to new_text[PROCEED]                  // enter

Backtrack:
  jump to original_box[RECEDE]               // original untouched
  discard new_text + new_data                // LIFO — stack discipline
```

**No heap allocation.** The mmap region is the allocator. LIFO
discipline matches backtracking exactly — when a branch fails you
pop the copy, which is exactly what backtracking does anyway.

**No GC.** Copies live and die with the match attempt. Region is
reused or released. No garbage.

**No omega/psi stacks.** Backtracking = return to the original box,
which was never modified. The copy was the branch. Discard the copy.

**No pattern_alloc pool.** The pattern IS the code. Already laid out
in TEXT at compile time. Nothing to allocate.

### engine.c Fate

`engine.c` (500+ lines) is not patched — it is **replaced** by the
copy-relocate loop. The four-port state machine becomes four entry
points in the copied TEXT block. The Z cursor struct becomes the
DATA section of the box.

### Timeline Impact

- Sprint 20: finish on current engine. Prove beautiful.sno compiles.
- Sprint 21: write the copy-relocate proof of concept. Single box.
- Sprint 22: retire engine.c. New engine = memcpy + relocation + jump.
- Sprint 23+: full dynamic pattern matching on the new engine.

### Status
- [x] Insight recorded (Session 16)
- [ ] Sprint 21: proof of concept
- [ ] Sprint 22: engine.c retired

---

## 16. The Straight Sprint — Session 16 Pivot

### What Changed

Study of `test_sno_1.c` vs `test_sno_2.c` revealed that **`test_sno_1.c`
is already the correct model** — and `emit_c.py`'s `FlatEmitter` already
generates that style.

The entire `emit_c_stmt.py` + `snobol4.c` + `snobol4_pattern.c` +
`engine.c` runtime was a **detour** — it built the `test_sno_2` model
(separate C functions per pattern, heap allocation, GC, struct passing).

The straight path:

```
sno_parser.py  →  ir.py  →  emit_c.py (grown)  →  test_sno_1 style C  →  binary
```

### What Survives

| Component | Status | Reason |
|-----------|--------|--------|
| `sno_parser.py` | ✅ Keep | Solid. 1214 stmts, 0 parse failures. |
| `ir.py` | ✅ Keep | Node types are right. Stmt/Program models good. |
| `emit_c.py` `FlatEmitter` | ✅ **The foundation** | Already generates `test_sno_1` style. |
| `emit_c.py` `FuncEmitter` | ⚠️  Retire | `test_sno_2` style — wrong model. |
| `emit_c_stmt.py` | ❌ Retire | Built for the runtime. No longer the path. |
| `snobol4.c` / `snobol4_pattern.c` / `engine.c` | ❌ Retire | Replaced by `test_sno_1` flat goto model. |
| Sprints 14–20 test oracles | ⚠️  Review | Parser oracle (sprint20) keeps. Others may go. |

### What `emit_c.py` Needs to Grow

`FlatEmitter` handles: `Lit`, `Pos`, `Rpos`, `Len`, `Span`, `Cat`, `Alt`,
`Assign`, `Arb`, `Arbno`, `Print`, `Ref`.

Still needed for full SNOBOL4 statements:

1. **Statement emission** — subject/pattern/replacement/goto structure.
   Each SNOBOL4 statement becomes a labeled block in the flat function.
2. **`Any` / `Break` / `Notany`** — missing from FlatEmitter.
3. **Arithmetic / string ops** — `+`, `-`, `*`, `/`, `**`, concat.
4. **Variables** — `Σ`/`Δ`/`Ω` are global; named vars are `static str_t`.
5. **DEFINE'd functions** — become labeled sub-regions in the same flat
   function (or separate flat functions for recursion), not `sno_uf_*`.
6. **INPUT / OUTPUT** — already partly handled; needs full statement form.
7. **GOTO** — unconditional/S/F branches map directly to `goto label;`.

### The One-Function Target

The output of the new `emit_c.py` for `beauty.sno` should look like
`test_sno_1.c` — **one `snobol()` function** with:

```c
void snobol(const char *Σ, int Ω) {
    int Δ = 0;

    /* --- pattern boxes, each as labeled goto blocks --- */
    str_t BREAK_snoLabel;
    BREAK_snoLabel_α: ...
    BREAK_snoLabel_β: ...

    /* --- statements as labeled blocks --- */
    SNO_START: ...
    SNO_LOOP:  ...
    SNO_END:   return;
}
```

Locals declared inline at point of use. Labels are the only control flow.
No heap. No GC. No runtime library beyond `printf`.

### Sprint Plan

1. **Now**: Add `Any`/`Break`/`Notany` to `FlatEmitter`. Commit.
2. **Next**: Add statement emission (subject/pattern/replacement/goto).
3. **Then**: Wire `sno_parser.py` → `ir.py` → `emit_c.py` for a simple
   program (`echo lines`). Binary runs. Commit.
4. **Goal**: `beautiful.sno` through the new pipeline. Binary
   self-beautifies. `diff` empty. **That is the commit promise.**

### 2026-03-12 — Session 18 (Sprint 21A+21B — Three-way Byrd Box port complete)

**Focus**: Build the three-port IR pipeline. All three backends working.

**Completed:**

- **`byrd_ir.py`** — Already existed and was solid from Session 17 prep.
  Smoke test: PASS. ~150 lines of Python dataclasses mirroring `ir.icn`.

- **`lower.py`** — New. Pattern AST → Byrd Box four-port IR (Chunk sequences).
  `_emit()` recursive lowering for: `Lit`, `Pos`, `Rpos`, `Any`, `Notany`,
  `Span`, `Break`, `Seq`, `Alt`, `Arbno`, `Call`.
  Key insight settled: **ARBNO is shy** — tries child immediately, succeeds on
  first child success (shortest match), extends only on β (backtrack). Fails if
  child fails at depth 0. No zero-match. Exactly matches `test_sno_1.c` gold standard.
  26 chunks generated for `POS(0) ARBNO('Bird'|'Blue'|ANY(alpha)) RPOS(0)`. PASS.

- **`emit_c_byrd.py`** — New. IR Chunks → `test_sno_1.c` style flat C.
  One function, locals inline, pure labeled gotos. Σ/Δ/Ω globals.
  `switch()` dispatch for `IndirectGoto` (Alt backtrack).
  `ARBNO_INIT / ARBNO_EXTEND / ARBNO_POP` primitives.
  **10/10 tests pass**: Lit, Pos, Rpos, Alt, Seq, Arbno — all correct.
  Commit: `b42ca0f`

- **`emit_jvm.py`** — New. IR Chunks → Java source with `while(true)/switch(state)`.
  This compiles to JVM `tableswitch` — exact Jcon model.
  State: `sigma` (String), `delta` (int cursor), `omega` (int length), `state` (int PC).
  `TmpLabel` → int local for Alt backtrack. ARBNO stack → `int[]` local + depth.
  **10/10 tests pass** on first run. Java 21 available in container.
  Commit: `8a98fdc`

- **`emit_msil.py`** — New. IR Chunks → C# source with identical `while(true)/switch(state)`.
  Compiles to MSIL `OpCodes.Switch` (tableswitch equivalent).
  .NET 8 SDK installed in container.
  **8/8 tests pass** after one-line fix (interpolated string in C# throw).
  Commit: `8a98fdc` (same commit as JVM)

**Three-port invariant confirmed**: Identical test cases, identical results on C, JVM, MSIL.
Single IR lowering pass (`lower.py`) drives all three backends.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `b42ca0f` | Sprint 21A: lower.py + emit_c_byrd.py |
| SNOBOL4-tiny | `8a98fdc` | Sprint 21B: emit_jvm.py + emit_msil.py |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `8a98fdc` | 10/10 C · 10/10 JVM · 8/8 MSIL — Sprint 21 complete |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**
1. Provide token at session start
2. **Sprint 22**: Wire `sno_parser.py → ir.py → emit_c_byrd.py` end-to-end.
   First real `.sno` → C binary. Simple echo program.
3. **Sprint 22 JVM/MSIL parallel**: Same first `.sno` through `emit_jvm.py` and `emit_msil.py`.
4. Progress toward Sprint 23: `beauty.sno` self-hosts → **Claude writes the commit message**.

---

### 2026-03-12 — Session 19 (Sprint 22 complete + Sprint 23 WIP — beauty.sno debug)

**Focus**: Sprint 22 oracle to green, then Sprint 23: `beauty.sno` compiles itself.

**Sprint 22 — COMPLETED (22/22 oracle PASS)**

Pipeline: `sno_parser.py → emit_c_stmt.py → gcc → binary`. End-to-end confirmed.
`emit_c_stmt.py` + `snobol4.c` runtime = the working codegen path.

Key runtime fix (Sprint 22): GT/LT/GE/LE/EQ/NE/INTEGER/REAL/SIZE registered as
`SnoVal` builtins in `sno_runtime_init()`. Oracle commit: `2f98238`.

**Sprint 23 — IN PROGRESS**

Goal: `beauty_bin < beauty.sno > output.sno && diff output.sno beauty_gold.sno` = empty.

**Root causes found and fixed (two commits, `c872ce6` and `0e4e0b2`):**

1. **DIFFER/IDENT/HOST/ENDFILE/APPLY + string builtins** — not registered → `sno_apply()` returned `SNO_NULL_VAL` → `ppArgLoop` never exited (hang). Fixed: all registered in `sno_runtime_init()`.

2. **nPush/nPop/nInc/nTop/nDec** — existed as C functions `sno_npush()` etc but NOT registered as callable SNOBOL4 functions. Used by `snoParse` pattern via `sno_pat_user_call("nPush",...)`. Fixed: added `_b_nPush` etc. wrappers and registered.

3. **Tree field accessors n/t/v/c** — not registered. Used by `pp`/`ss` functions for tree node traversal. Fixed: added `_b_tree_n/t/v/c` via `sno_field_get()`.

4. **assign_cond/assign_imm emitted wrong arg** — `emit_c_stmt.py` was emitting `sno_var_get("tab")` (the VALUE) as the capture target. `sno_pat_assign_cond()` needs the variable NAME as `SNO_STR_VAL("tab")`. Fixed in all three emit sites.

5. **Missing include path** — beauty.sno needs `programs/inc/` for global.sno, is.sno, stack.sno, etc. Was not passed to parser → 534 stmts instead of 1214. Fixed: pass `include_dirs=['../SNOBOL4-corpus/programs/inc/']`.

6. **&ALPHABET binary string** — `sno_alphabet[0] = '\0'` → `strlen()` = 0 → all `POS(n)` matches on `&ALPHABET` fail → `tab`, `nl`, etc. never set by `global.sno`. Fixed: pre-initialize all key character constants (tab/nl/cr/lf/ht/vt/ff/bs/fSlash/bSlash/semicolon) directly in `sno_runtime_init()`.

**Current blocker — still Parse Error on `X = 5` input:**

After all fixes, `beauty_bin < "X = 5\n"` reaches the `snoParse` match at stmt 790 but fails → `mainErr1` → "Parse Error".

The `snoParse` pattern includes a sub-expression:
```
("'snoParse'" & 'nTop()')
```
In the generated C this becomes `sno_concat_sv(SNO_STR_VAL("'snoParse'"), SNO_STR_VAL("nTop()"))` — a string, not a pattern. The `&` in a pattern context is pattern-cat; `"'snoParse'"` is a string literal that matches the text `'snoParse'`; `'nTop()'` should be a conditional assignment `. nTop()`. This may be a parser IR issue — the pattern structure of snoParse itself needs investigation.

**Next session — immediate actions:**

1. Provide token at session start
2. Inspect snoParse pattern IR from the parsed beauty.sno (stmt 877, L410-416). The `("'snoParse'" & 'nTop()')` fragment. Verify what the parser produces and what emit_c_stmt.py generates for it.
3. If pattern structure is wrong, fix parser or emitter for that construct.
4. Re-run `printf 'X = 5\n' | /tmp/beauty_bin` — should produce beautified `X = 5`.
5. Run full beauty self-compilation. Diff. Write commit message.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `2f98238` | Sprint 22: end-to-end pipeline + numeric comparison builtins |
| SNOBOL4-tiny | `c872ce6` | Sprint 23 WIP: register builtins/tree accessors; fix include path |
| SNOBOL4-tiny | `0e4e0b2` | Sprint 23 WIP: pre-init char constants + assign_cond name fix |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `0e4e0b2` | Sprint 22: 22/22 PASS. Sprint 23 in progress. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

---

### 2026-03-12 — Session 20 (Sprint 23 WIP — CSNOBOL4 source study + three parser/emitter fixes)

**Focus**: Root-cause analysis of beauty_bin Parse Error via CSNOBOL4 SIL source study.
Sprint 22 oracle: 22/22 PASS (unchanged throughout session).

**Completed — three confirmed fixes (commit `b42c19f`):**

1. **2D subscript false positive removed** (`sno_parser.py` `parse_primary`):
   `ARBNO(*snoCommand)("'snoParse'" & 'nTop()')` was parsed as `array(ARBNO(...), subscripts=[...])` because a second `(` after a function call was treated as a 2D subscript. Fix: removed the `if self.at('LPAREN')` second-paren rule. In SNOBOL4, `func(args)(args2)` is juxtaposition concatenation, not 2D subscript. Confirmed from CSNOBOL4 `v311.sil` ITEM proc — 2D subscripts only apply to `ARRAY` typed values, not general function call results.

2. **AMP (`&`) as explicit concat operator** (`sno_parser.py` `parse_concat`):
   `&` in replacement/pattern context is identical to blank juxtaposition (CSNOBOL4 `CONPP/CONVV`). `parse_concat` loop now also consumes `AMP` token as a concat separator. `parse_primary` AMP handler only handles `&IDENT` (keyword); bare `&` falls through to concat.

3. **RETURN convention fix** (`emit_c_stmt.py` `_emit_function`):
   `SNO_RETURN_LABEL_{fn}` was emitting `return SNO_NULL_VAL` — wrong per spec. In SNOBOL4, `:(RETURN)` returns the value of the function-name variable. Fix: RETURN label now captures `SnoVal _retval = sno_var_get("{fi.name}")` before restoring params/locals, then returns `_retval`. Verified from CSNOBOL4 `v311.sil` `RTNFNC` proc.

**Root cause investigation — why Parse Error persists:**

After the three fixes, `beauty_bin` still produces "Parse Error" on `X = 5`.
Deep investigation traced the actual blocker:

- `sno_eval()` in `snobol4_pattern.c` is a stub — it only handles variable lookup and integer literals. Does NOT evaluate SNOBOL4 expression strings.
- `shift(p, t)` calls `sno_eval("p . thx . *Shift('t', thx)")` — a full SNOBOL4 pattern expression. The stub returns the string unchanged, so `shift` returns a string instead of a pattern.
- `sno_opsyn()` is also a complete no-op stub. However: the parser maps `~` → DOT token at lex time, so OPSYN is irrelevant to `~` handling — `~` already parses as conditional assign (`.`).
- The **reference `beautiful.c`** (Sprint 20 pre-existing) also gives Parse Error on `X = 5`. This confirms the blocker predates Session 20.

**What `sno_eval` needs to do** (verified from CSNOBOL4 `v311.sil` `EVALEN` proc):
`EVAL(str)` compiles and executes the string as a SNOBOL4 expression. In beauty.sno, `shift` and `reduce` use it to build pattern objects from string templates at function-call time. The patterns built are: `p . thx . *Shift('t', thx)` (shift) and `epsilon . *Reduce(t, n)` (reduce). These require a runtime expression parser/compiler.

**Two paths forward:**

- **Path A (full)**: Implement `sno_eval` as a recursive descent parser + emitter over SnoVal. Correct per spec. Complex (~300 lines). The `~` → `shift()` → `sno_eval()` chain then works end-to-end.
- **Path B (targeted)**: Recognize that the parser already maps `~` to DOT (conditional assign) and `&` to concat. Override `sno_opsyn` to be a no-op but hardwire the `Shift(t,v)` / `Reduce(t,n)` call semantics directly in the pattern engine when `*Shift` / `*Reduce` user-call nodes fire. This is a narrower fix specific to beauty.sno's ShiftReduce grammar.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `b42c19f` | WIP Sprint 23: 2D subscript fix, AMP concat, RETURN convention |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `b42c19f` | Sprint 22: 22/22 PASS. Sprint 23 in progress. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Implement `sno_eval()` — runtime SNOBOL4 expression evaluator. Minimum viable: handle concat (`.`), deferred ref (`*X`), string literals, variable names, function calls. This unblocks `shift` and `reduce`.
3. Re-run `printf 'X = 5\n' | /tmp/beauty_bin` — should reach snoParse match and succeed.
4. Run full beauty self-compilation: `beauty_bin < beauty.sno > output.sno && diff output.sno beauty_gold.sno`.
5. **Write the commit message** — the Sprint 23 promise.

**Key context for next session:**
- `shift(p,t)` body: `sno_eval("p . thx . *Shift('t', thx)")` — needs concat+deferred ref+assignment
- `reduce(t,n)` body: `sno_eval("epsilon . *Reduce(t, n)")` — needs concat+deferred ref
- `sno_opsyn` is a no-op and can stay that way — `~` is already DOT at parse time
- `TopCounter` body uses `DIFFER($'#N') value($'#N')` — `value()` is a DATA field accessor for `link_counter(next, value)`; `sno_data_define` registers the type but does NOT auto-register field accessor functions; `value()` must be manually registered (similar to `n/t/v/c` for tree)
- Sprint 22 oracle 22/22 is the certified baseline — do not break it


### 2026-03-12 — Session 21 (Sprint 23 WIP — sno_eval + AMP→reduce + emit fixes)

**Focus**: Continued Sprint 23 debug of Parse Error. Three major fixes implemented.
Sprint 22 oracle: 22/22 PASS (unchanged).

**Context note**: Session was interrupted once mid-implementation (str_replace left
`snobol4_pattern.c` partially mangled). Recovery via Python-based full replacement.
Safe interrupt points are after compile results and git push confirmations.

**Completed (commit `6f854e7`):**

1. **`sno_eval()` — full recursive descent C parser** replacing the stub:
   - Three static helpers: `_ev_val` (argument values, full var lookup),
     `_ev_term` (pattern elements, STR sentinel trick), `_ev_expr` (dot-chained terms).
   - `SnoEvalCtx` struct carries `{const char *s; int pos}` cursor.
   - Key semantic: plain `IDENT` in term position returns `SNO_STR_VAL(name)` sentinel.
     Dot handler then checks right operand type: `SNO_STR` → `assign_cond(left, right)`;
     `SNO_PATTERN` → `pat_cat(left, right)`. This correctly disambiguates `thx` (capture
     target) from `*Shift(...)` (pattern to concatenate).
   - `*IDENT[(args)]` → `sno_pat_user_call` / `sno_pat_ref`.
   - Quoted strings → `sno_pat_lit`. Function calls in val position → `sno_apply`.

2. **Parser: AMP infix → `reduce()` call node** (OPSYN semantics):
   - `_ExprParser.parse_concat`: AMP now emits `Expr(kind='call', name='reduce', args=[left,right])`
     instead of `Expr(kind='concat')`. Models `OPSYN('&','reduce',2)` in beauty.sno.
   - `_PatParser.parse_cat`: same, produces `PatExpr(kind='call', name='reduce', args=[left,right])`.
   - This is correct for ALL uses of `&` in beauty.sno — every `&` is reduce, no plain concat.

3. **Emitter: `reduce()`/`eval()` recognized as pattern-valued**:
   - `_is_pattern_expr`: `REDUCE`/`EVAL` added to dynamic pattern set so `concat` of
     reduce-result uses `sno_pat_cat` not `sno_concat_sv`.
   - `emit_as_pattern`: `REDUCE`/`EVAL` added to `_KB2` → routes through `sno_apply()`
     not `sno_pat_ref()`.
   - `emit_pattern_expr`: `PatExpr(kind='call', name='reduce')` emits
     `sno_var_as_pattern(sno_apply("reduce", args, 2))`.

4. **Runtime: `value()`/`next()` field accessors for `link_counter` DATA type**:
   - `_b_field_value` / `_b_field_next` via `sno_field_get()`, registered alongside
     `n/t/v/c` tree accessors. Needed by `TopCounter` in `counter.sno`.

**Current state**: Still `Parse Error` on `X = 5`. The `sno_var_as_pattern(sno_apply("reduce",...))` 
is now emitted correctly in the C for snoParse. But at runtime, `reduce()` is a SNOBOL4
user-defined function (in `ShiftReduce.sno`) that calls `EVAL(...)` — which calls our new
`sno_eval()`. The chain is: `reduce('snoParse', nTop())` → `EVAL("epsilon . *Reduce(snoParse, nTop())")` →
`sno_eval()` → returns a pattern. The pattern then goes into `sno_var_as_pattern()`.

**Investigation needed next session**: Confirm that `reduce` is actually being called at
runtime (add debug print or check via `SNO_PAT_DEBUG`). Verify that `sno_var_as_pattern`
correctly wraps a `SNO_PATTERN` value (it should return it unchanged). If `reduce` is
returning the right pattern but `sno_var_as_pattern` is discarding it, that's the next fix.
Also verify `sno_pat_arbno` handles a reduce-built pattern as its child.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `6f854e7` | WIP Sprint 23: sno_eval RD parser, AMP→reduce(), value/next accessors, emit fixes |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6f854e7` | Sprint 22: 22/22 PASS. Sprint 23 still Parse Error. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Add runtime debug to confirm `reduce()` is being called at runtime during the snoParse match.
   `SNO_PAT_DEBUG=1 printf 'X = 5\n' | beauty_bin 2>&1 | grep -i reduce`
3. Verify `sno_var_as_pattern()` behavior on `SNO_PATTERN` input — should pass through unchanged.
4. If reduce is not being called: trace why — is `sno_var_as_pattern(sno_apply("reduce",...))` being
   evaluated at pattern BUILD time or match time? It should be build time (at the assignment
   `snoParse = ...`). If the assign is never executing, check the SNOBOL4 statement that sets snoParse.
5. Once reduce is verified working, run full self-compilation.

**Key invariants to preserve:**
- Sprint 22 oracle: 22/22 PASS — do not break
- `sno_eval` is in `snobol4_pattern.c` at the location of the old stub
- `reduce`/`shift` are SNOBOL4 functions defined in `ShiftReduce.sno` (included by beauty.sno)
- `value()`/`next()` are now registered; `TopCounter` should work
- The AMP→reduce change affects ALL programs that use `&`. For programs without OPSYN,
  `reduce` will not be defined → `sno_apply("reduce",...)` returns `SNO_NULL_VAL` →
  `sno_var_as_pattern(null)` = epsilon. This is WRONG for programs that used `&` as concat.
  **Flag**: Sprint 22 tests may be at risk. Verify oracle still 22/22 after the AMP change.


### 2026-03-12 — Session 22 (Sprint 23 WIP — STAR-as-deref, parse_concat, snoExprList)

Two container crashes. Sprint 22 oracle: 22/22 PASS (preserved).
Disable non-bash tools (Calendar, Gmail, image search, etc.) at session start to preserve context.

**Root cause traced**: `snoExprList = nPush() *snoXList ... nPop()` — `*snoXList` was parsed
as infix arithmetic multiplication (not deref prefix) because `parse_multiplicative` consumed STAR.
In SNOBOL4, `*` is NEVER binary arithmetic in replacement context — only unary deref prefix.
Cascading failure: `snoExpr17 → snoExpr15 → snoExpr14 → snoStmt → snoCommand → snoParse`.

**Completed (commit `3fe1b5b`):**
- `parse_multiplicative`: STAR removed as infix; only SLASH remains as binary division.
- `parse_concat` loop condition: `self.at('STAR')` added so deref items are not skipped.
- `parse_concat` else branch: `self.at('STAR')` → `parse_unary()` directly (not `parse_additive`).
- OPSYN-tracked AMP→reduce: `_amp_is_reduce` flag, `parse_program()` detects OPSYN stmt.

**State**: Still Parse Error. Next actions in §6 above.

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `3fe1b5b` | Sprint 22: 22/22. Sprint 23: Parse Error. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 |

### 2026-03-12 — Session 29 (Design Eureka: Unified Expression IR eliminates subject/pattern split)

**No code written. Architecture insight recorded. THIS IS A MAJOR DESIGN DECISION.**

**The problem that has recurred across Sessions 19–29:**

snoc's grammar needs to split a SNOBOL4 statement into `subject / pattern / replacement`.
The grammar uses one `expr` type for all three. The parser couldn't decide:
- Is `POS(0)` after a subject the start of the pattern field, or juxtaposition-concat of the subject?
- Is `*X` in a statement binary multiply or deref prefix (pattern ref)?
- Is `|` string alternation or pattern alternation?

Multiple failed approaches: mid-rule bison actions, `%glr-parser` with `%dprec`, `snoc_in_pat` flag.

**Lon's question that cut through it:**

> "Why do you need to distinguish at parse time? The subject is just the α entry action of the Byrd Box. The entire statement IS a Byrd Box."

**The answer:**

The entire SNOBOL4 statement is a Byrd Box:
```
label:  subject  pattern  =replacement  :S(x) :F(y)
          α         →          γ            γ    ω
```
- **α** — evaluate subject → initialize Σ (string), Δ (cursor=0)
- **pattern** — runs through the Byrd Box proper
- **γ** — success: apply replacement, goto :S label
- **ω** — failure: goto :F label

The subject is not outside the box — it IS the α entry action.

**The key insight that resolves the parser conflict:**

`E_CONCAT` (juxtaposition), `E_MUL` (STAR), `E_ALT` (PIPE) are **the same node** in the IR.
The **emitter** decides what to emit based on **position in the Stmt**:

| Field | Emitter call | Result |
|-------|-------------|--------|
| `s->subject` | `emit_expr(E_CONCAT)` | `sno_concat()` — string concat |
| `s->pattern` | `emit_pat(E_CONCAT)` | `sno_pat_cat()` — pattern cat |
| `s->subject` | `emit_expr(E_DEREF)` | `sno_get()` — value deref |
| `s->pattern` | `emit_pat(E_DEREF)` | `sno_pat_ref()` — deferred pattern ref |
| `s->subject` | `emit_expr(E_ALT)` | `sno_alt()` — string alternation |
| `s->pattern` | `emit_pat(E_ALT)` | `sno_pat_alt()` — pattern alternation |

**The grammar collapses:**

One expression grammar. No `pat_expr` / `expr` split. No conflicts.
The `Stmt` still has `s->subject`, `s->pattern`, `s->replacement` fields.
The parser fills them by **counting position** (1st expr = subject, 2nd expr before `=` = pattern).
The emitter routes each through the correct emit function.

**`emit_expr()` and `emit_pat()` already exist and already do this correctly.**
The only bug was that the PARSER was failing to put nodes into `s->pattern` — instead
folding them into `s->subject` via juxtaposition. Fix the parser split; the emitter is already correct.

**Implementation:**

Remove `pat_expr` from the grammar entirely. Use a single `expr` for all fields.
After parsing the first `expr` (subject), the next `expr` before `=` is the pattern.
The split is determined by counting exprs on the line, not by token type.
The grammar conflicts disappear because there is no longer a separate `pat_expr` production.

**Status:** Design recorded. Implementation pending (next session first action).

---

### 2026-03-12 — Session 27 (Eureka: Byrd Box + exception hygiene architecture)

**No code written. Architecture insight recorded.**

**⚡ EUREKA (Lon, Session 27):** Normal Byrd Box gotos handle success/failure/backtrack
with zero overhead — exactly as in `test_sno_1.c`. C exceptions (`longjmp`) are for
**ABORT and genuinely bad things only** — FENCE bare, runtime errors, divide-by-zero.
Each SNOBOL4 statement is a `setjmp` catch boundary for abort signals. Each DEFINE'd
function is also a catch boundary. Hot path: zero exception overhead. Cold path:
stack unwinds cleanly through statement and function boundaries. Stack unwinding IS
the cleanup — no omega stack needed for abnormal termination.

Recorded in `SNOBOL4-tiny/PLAN.md §6`.

---

### 2026-03-12 — Session 23 (Orientation + ByrdBox/CSNOBOL4 study + SNOBOL4ever naming)

**Focus**: New session orientation. ByrdBox and CSNOBOL4 source study. Org rename decision.
No compiler code written this session. Container crashed mid-rebuild; repos intact on remote.

**Completed:**
- Re-read PLAN.md top to bottom. All context current as of Session 22.
- Cloned SNOBOL4-tiny, SNOBOL4-corpus, .github. Extracted ByrdBox.zip and snobol4-2_3_3_tar.gz.
- Built CSNOBOL4 oracle (`xsnobol4`) from source. Confirmed build clean.
- Studied `test_sno_1.c` gold standard — the definitive four-port Byrd Box flat-C model.
- Studied `byrd_box.py` — SNOBOL4python-based reference implementation showing Shift/Reduce/nPush/nPop pattern grammar builder.
- Studied CSNOBOL4 `syn.c`, `equ.h`, `main.c` — scanner table structure, operator tables (BIOPTB/SBIPTB), constants (`SPDLSZ=8000`).

**SNOBOL4ever — org rename decision:**
Lon named the org **SNOBOL4ever**. Recorded in §1 with full rename procedure.
Mission updated: "SNOBOL4 everywhere. SNOBOL4 now. SNOBOL4 forever."
The rename itself is pending — do at start of a quiet session, not mid-sprint.

**State at snapshot:** All repos unchanged from Session 22. No code commits this session.

**Next session — immediate actions:**
1. Provide token at session start
2. Sprint 23: rebuild CSNOBOL4 oracle, run `oracle_sprint22.py` to confirm 22/22
3. Follow §6 Sprint 23 debug steps in order
4. When ready: rename org to SNOBOL4ever (see §1 procedure)

---

## 17. Icon-everywhere — The Next Frontier (Session 23 Eureka)

**Decision (2026-03-12, Session 23):** Lon's insight: **do for Icon exactly what we did for SNOBOL4.**

### The Insight

SNOBOL4-everywhere was built in one week using the Byrd Box model as the unifying IR —
one four-port representation, three backends (C flat-goto, JVM bytecode, MSIL), proven
correct against CSNOBOL4 and SPITBOL as oracles.

Icon is the **direct descendant** of SNOBOL4. Griswold invented both. Icon's goal-directed
evaluation and generators ARE the Byrd Box model — Jcon (Proebsting + Townsend, Arizona 1999)
already proved this: Icon → JVM bytecode via the exact same four-port IR we use.

**What exists today:**
- Icon/C — the reference implementation (Griswold, Arizona). Mature. Active.
- Jcon — Icon → JVM (Proebsting + Townsend). Working. Our blueprint. Already studied (see JCON.md).
- No Icon for .NET / MSIL. No Icon for modern JVM via ASM. No Icon-everywhere.

**What we build:**
- Same org structure as SNOBOL4ever: `Icon-everywhere` (or similar)
- Same Byrd Box IR — already exists in `byrd_ir.py`
- `emit_icon_jvm.py` — Icon → JVM bytecode via ASM (extend Jcon's `gen_bc.icn` blueprint)
- `emit_icon_msil.py` — Icon → MSIL via ILGenerator
- `emit_icon_c.py` — Icon → flat C goto (same as SNOBOL4-tiny's FlatEmitter)
- Oracles: Icon/C reference + Jcon for crosscheck

**Why it's achievable fast:**
- Byrd Box IR is already built and proven across three backends
- Jcon source is already studied, cloned, documented in JCON.md
- The four-port wiring for Icon generators is a superset of SNOBOL4 patterns —
  co-expressions and producers add state but the box model is identical
- The same `lower.py` lowering strategy applies
- The same harness crosscheck infrastructure works

**The transcript leverage:**
Lon can point Claude to the GitHub history transcripts of the SNOBOL4-everywhere build.
Those transcripts ARE the architectural playbook. Feed them to a new Claude session
and the Icon-everywhere build starts at Sprint 18, not Sprint 0.

**Org name candidates (Lon's list):**
- `Icon-everywhere`
- `Icon-now`
- `Icon-forever`
- `ICONever` (mirrors SNOBOL4ever)

**Status:** Idea recorded. No repos created yet. Begin after SNOBOL4-tiny Sprint 23
(beauty.sno self-hosts) — that proof-of-concept is the template for the Icon build.

### Relationship to SNOBOL4ever

These are **sibling orgs**, not subprojects. SNOBOL4ever stays focused on SNOBOL4.
Icon-everywhere is its own org with its own repos. The shared artifact is `byrd_ir.py`
and the harness crosscheck infrastructure — these get extracted into a standalone
`byrd-box` library that both orgs depend on.

```
byrd-box/          ← standalone: byrd_ir.py + lower.py + emit_c/jvm/msil backends
    ↑                  (extracted from SNOBOL4-tiny)
    ├── SNOBOL4ever/   ← SNOBOL4 frontend → byrd-box → C/JVM/MSIL
    └── Icon-everywhere/ ← Icon frontend → byrd-box → C/JVM/MSIL
```

### 2026-03-12 — Session 23 (Orientation + naming + vocabulary + handoff)

**Focus**: Session orientation, source study, strategic naming decisions, nomenclature rename,
Icon-everywhere eureka, emergency handoff. No Sprint 23 code progress — container OOM instability
prevented beauty binary build throughout session.

**Completed:**

- **SNOBOL4ever** — org rename decision recorded in §1 with full procedure. Mission line updated.
  README updated. Commits `b82553e` (.github).

- **Four-port vocabulary rename** — SUCCESS→SUCCEED, FAILURE→CONCEDE across all source:
  `engine.h`, `engine.c`, `snobol4.h`, `lower.py`, `emit_c_byrd.py`, `emit_jvm.py`, `emit_msil.py`.
  Generated label names updated. Greek (α/β/γ/ω) unchanged. Commit `42dddce` (tiny).
  The four ports are now: **PROCEED / RECEDE / SUCCEED / CONCEDE** — verbs, distinguished,
  CONCEDE = normal pattern failure, RECEDE = parent-initiated undo. Commit `95ca711` (.github).

- **Icon-everywhere eureka** — §17 written. Same Byrd Box IR, same three backends, new Icon
  frontend. Transcript-as-playbook strategy documented. Commit `f5e90ba` (.github).

- **OOM pattern identified** — parse+emit+gcc in one Python process kills container.
  §6 updated with mandatory two-step build procedure and leading-space warning.

- **Leading-space insight (Lon)** — SNOBOL4 requires leading whitespace on non-label statements.
  All prior `printf 'X = 5\n'` tests used invalid input. `printf '    X = 5\n'` is correct.
  This may be the entire Sprint 23 blocker. Must be tested first next session.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `42dddce` | SUCCEED/CONCEDE rename — 7 files, 117 changes |
| .github | `b82553e` | SNOBOL4ever naming + session 23 log |
| .github | `f5e90ba` | Icon-everywhere §17 + README |
| .github | `95ca711` | Four-port vocabulary PLAN.md + README |
| .github | this | §6 OOM warning + leading-space fix + session 23 final |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `42dddce` | Sprint 22: 22/22 (baseline). Sprint 23: Parse Error (unverified with correct input). |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — FIRST action before anything else:**
Build beauty binary (two steps, see §6), then test:
```bash
printf '    X = 5\n' | /tmp/beauty_bin
```
If that produces beautified output, Sprint 23 is essentially done. Run the full self-compilation immediately.

### 2026-03-12 — Session 24 (snoc compiler — Python pipeline retired, 297→86 errors)

**Focus**: Python pipeline permanently retired (OOM on every attempt, even parse-only).
Built `snoc` — a SNOBOL4→C compiler in C using flex+bison to replace it entirely.

**Decision**: Single `Expr` IR type for everything. The emitter decides context:
`emit_expr()` → value context (`sno_*()`), `emit_pat()` → pattern context (`sno_pat_*()`).
Same `E_CONCAT`, `E_ALT`, `E_CALL` nodes routed differently. Grammar is clean LALR(1).

**beauty.sno errors: 297 → 86** across the session. Nine root causes fixed.

**Root causes fixed (in order):**
1. Dual IR (PatExpr + Expr) collapsed → single Expr, context-sensitive emission
2. PAT_BUILTIN over-eager → trailing context `{IDENT}/"("` — `tab`/`rem`/`nul` now IDENT
3. PAT_BUILTIN in value context (`SPAN(...)` in replacement) → added to `primary`
4. Unary `.X` (name ref) missing from `factor`
5. Unary `*X` (deref) missing from `factor`
6. `PIPE` (`|`) missing from `expr` — fixed `*P1 | *P2` constructs
7. Empty replacement (`X POS(0) =`) → `E_NULL`
8. Slash in IDENT (`pp_/`, `ss_/`) → extended char class
9. Unary `+` missing from `factor`

**Computed goto fix written, not yet tested** — `<GT>` state swallows `$(`…`)` as
`$COMPUTED` sentinel. First action next session: rebuild, retest.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `98d3626` | WIP Sprint 23: snoc compiler (flex+bison), 297→86 errors |
| .github | this | §6 snoc status + next actions + session 24 log |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `98d3626` | Sprint 22: 22/22 (baseline). snoc: 86 errors on beauty.sno. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

### 2026-03-12 — Session 25 (snoc: 86→0 errors, runtime gap exposed)

**Focus**: Drive snoc parse errors from 86 to 0, diagnose what remains.

**Fixes applied (86→0 errors):**
1. Missing `%}` closing C preamble in `sno.l` — caused flex "premature EOF" on every build
2. bstack comma-as-alternation: `"("` pushes `last_was_callable`, `","` returns `PIPE` vs `COMMA`
   based on whether we're inside a grouping paren or a function-call paren
3. E_DEREF compound-expr crash: `emit_expr` case `E_DEREF` assumed `e->left` always `E_VAR`;
   fixed to handle compound left expressions (`*(y 'f')` style)

**What this session revealed:**
- snoc produces **1213 stmts, 0 errors** on beauty.sno ✅
- BUT the generated C **will not compile** — two structural gaps in emit.c:
  1. No variable declaration pass (all `_OUTPUT`, `_TRUE`, etc. undeclared)
  2. No runtime shim (`sno_str`, `sno_int`, `sno_kw`, `sno_concat`, `sno_alt`, etc. don't exist)
- Attempting `gcc` on generated "hello world" confirms both blockers

**Key clarification**: ByrdBox's `SNOBOL4c.c` is a C **pattern engine**, not a SNOBOL4→C compiler.
snoc is the only SNOBOL4→C compiler in existence across all repos.

**Repo commits:**

| Repo | Commit | What |
|------|--------|-------|
| SNOBOL4-tiny | `d7f39d1` | WIP Sprint 23: bstack comma-as-alt + missing %} fix |
| SNOBOL4-tiny | `6d3d1fa` | WIP Sprint 23: fix E_DEREF compound-expr crash — 1213 stmts, 0 errors |
| .github | this | §6 + §12 session 25 handoff |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6d3d1fa` | Sprint 22: 22/22 (baseline). snoc: 1213 stmts, 0 errors. Generated C does not link. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

### 2026-03-12 — Session 26 (snoc_runtime.h + emit.c symbol pass + hello world + execution model)

**Focus**: Closed both Sprint 23 runtime blockers. Hello world end-to-end. Execution model
architecture documented in SNOBOL4-tiny/PLAN.md.

**Completed (commit `7f3af9c`):**

1. **`snoc_runtime.h`** — new shim header at `src/runtime/snobol4/snoc_runtime.h`:
   scalar constructors (`sno_int`, `sno_str`, `sno_real`), keyword access (`sno_kw`,
   `sno_kw_set`), concat/alt/deref/indirect wrappers, array/table aliases (`sno_aref`,
   `sno_aset`, `sno_index` as `#define` aliases), pattern aliases (`sno_pat_break`,
   `sno_pat_any`, etc.), `SnoMatch` struct + `sno_match` + `sno_replace`,
   `sno_init` → `sno_runtime_init()`, `sno_finish` → no-op.
   Key: use `#ifndef SNOC_RUNTIME_H` guard (not `#pragma once`) to avoid double-include.

2. **`emit.c` — symbol collection pre-pass**:
   - `sym_table[4096]` deduplicating hash set of variable names
   - `io_names[]` = `{"OUTPUT","INPUT","PUNCH","TERMINAL","TRACE",NULL}` — excluded from static locals
   - `is_io_name()`, `sym_add()`, `collect_expr()`, `collect_stmt()`, `collect_symbols()`
   - `emit_var_decls()` — emits `static SnoVal _name = {0};` for each collected symbol
   - IO routing: `E_VAR` checks `is_io_name()` → emits `sno_var_get("OUTPUT")` / `sno_var_set()`
   - Per-statement unique labels (`_SNO_NEXT_N`) via `cur_stmt_next_uid`
   - uid-suffixed temporaries (`_ok%d`, `_s%d`, `_p%d`, `_m%d`) for flat-function scope
   - `E_NULL` → `SNO_NULL_VAL` (not `SNO_NULL` which is the enum member)

3. **`engine.c` is required** — `snobol4_pattern.c` calls `engine_match_ex()` which lives
   in `src/runtime/engine.c`. Must be in gcc link line.

4. **Hello world end-to-end** ✅:
   ```bash
   ./snoc /tmp/hello.sno > /tmp/hello.c
   gcc -O0 -g /tmp/hello.c [runtime files] -lgc -lm -w -o /tmp/hello_bin
   /tmp/hello_bin   # → hello
   ```

5. **SNOBOL4-tiny/PLAN.md created** — documents:
   - Statement-level Byrd Box execution model (§6) — alpha/gamma/omega per statement
   - Function-per-DEFINE architecture (§7) — Sprint 24 plan
   - The commit promise (§8)
   - Runtime build command reference (§9)
   - Key file paths (§10)
   - SNOBOL4 semantics quick reference (§11)

6. **Execution model architecture** — Lon's insight confirmed and documented:
   - Each SNOBOL4 statement IS a Byrd box: alpha (enter), gamma (success/S goto), omega (failure/F goto)
   - SUCCESS and FAILURE are goto edges, not C exceptions — exactly as in test_icon.c / test_sno_1.c
   - Statement-level granularity = Level 1 (baseline correctness)
   - Function-per-DEFINE = Level 2 (Sprint 24, solves duplicate label crisis + enables C optimization)
   - Future: one-C-function-per-port (test_icon-2.py model) as optional micro-optimization

**Current blocker — duplicate C labels in beauty.sno:**

beauty.sno generates 0 parse errors but **53 gcc errors** — all duplicate labels.
`_L_pp____` and `_L_ss__` appear from multiple included files; `_SNO_RETURN_main`
used but not defined. Root cause: all SNOBOL4 code (including all -include'd files)
emits flat into one C `main()`. DEFINE'd function labels collide.

**Sprint 24 fix**: emit each `DEFINE('fn(args)locals')` as a separate C function
`SnoVal _sno_fn_pp(SnoVal *args, int nargs)`. Labels inside each C function are
scoped — no more duplicates. `:(RETURN)` → `goto _SNO_RETURN_pp;`, `:(FRETURN)` →
`goto _SNO_FRETURN_pp;`. Register each with `sno_define()` at start of `main()`.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `7f3af9c` | Sprint 23: snoc_runtime.h + emit.c symbol pass + hello world + PLAN.md |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `7f3af9c` | Sprint 22: 22/22 PASS. snoc: 1213 stmts, 0 parse errors. hello world ✅. 53 gcc errors on beauty.sno. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. **Sprint 24**: implement function-per-DEFINE in `emit.c`:
   - Pre-pass: scan for `DEFINE('fn(args)locals')` calls, build fn_table
   - `emit_fn_forwards()` — SnoVal _sno_fn_pp(SnoVal*, int); forward decls
   - `emit_fn_body(fn)` — separate C function per DEFINE, labels scoped inside
   - `emit_main()` — top-level statements + sno_define() registrations
   - :(RETURN) → goto _SNO_RETURN_pp; :(FRETURN) → goto _SNO_FRETURN_pp;
3. Test sequence: hello world still works → simple DEFINE test → beauty.sno
4. Target: `gcc` on beauty_snoc.c with 0 errors
5. Run beauty self-compilation. Diff. **Write the commit message.**

**Key context:**
- Build cmd: `gcc -O0 -g $C_FILE $RUNTIME/snobol4/snobol4.c $RUNTIME/snobol4/snobol4_inc.c $RUNTIME/snobol4/snobol4_pattern.c $RUNTIME/engine.c -I$RUNTIME/snobol4 -I$RUNTIME -lgc -lm -w -o $BIN`
- `engine.c` is REQUIRED in link line (engine_match_ex lives there)
- `snoc_runtime.h` is at `src/runtime/snobol4/snoc_runtime.h`
- `emit.c` is at `src/snoc/emit.c`
- SNOBOL4-tiny/PLAN.md has full Sprint 24 implementation plan
- Org rename SNOBOL4-plus → SNOBOL4ever still pending (do at start of quiet session)

---

### 2026-03-12 — Session 28 (Sprint 25: SIL execution model + body boundary + 0 gcc errors maintained)

**Focus**: Session continued Sprint 24/25 work. SIL execution model documented.
Body boundary bug found and fixed. Cross-scope goto bug found and fixed.
Sprint 24 gcc error count confirmed at 0. Beauty binary hangs traced to `:S(G1)` bug.

**Key insight (Lon, 2026-03-12):**
CSNOBOL4 `CODE()` builds one flat node array in memory. A label is just an index.
Execution runs off a cliff at the next label. Body boundary = label-to-next-label,
unconditionally. ANY label stops the body. Documented in `SNOBOL4-tiny/PLAN.md §12`
and `§6` here.

**Fixes committed:**

| Commit | What |
|--------|------|
| `9406ee6` | SIL model documented in PLAN.md + body boundary rewritten: any label = end of body |
| `c998a23` | Cross-scope goto: inside a C function, goto to main-scope label → fallthrough |
| `6b6b541` | Extra body stop: fn-entry label or end_label also terminates body traversal |

**Binary test — where we are:**
- 0 gcc errors ✅
- GREET still ✅
- beauty binary reaches init (UTF table build) then **hangs** in `G1` loop
- Root cause: `$UTF_Array[i,2] = UTF_Array[i,1] :S(G1)` emits `goto _L_G1` unconditionally
  — the `:S` condition is dropped. Assignment statements with `:S`/`:F` gotos need conditional emit.

**Next session first action:** Fix `:S/:F` conditional emit for assignment statements in `emit_stmt`.
Look at how `STMT_MATCH` emits `_ok` conditionals — apply same pattern to assignment.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| SNOBOL4-tiny | `9406ee6` | SIL model + body boundary rewrite |
| SNOBOL4-tiny | `c998a23` | Cross-scope goto fix |
| SNOBOL4-tiny | `6b6b541` | Extra body boundary stop |
| .github | this | §6 + §12 handoff |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `6b6b541` | 0 gcc errors ✅. hello ✅. GREET ✅. beauty hangs on :S(G1). |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |


**Architecture (no code yet for this):**
- **Eureka (Lon)**: normal Byrd Box gotos handle ω/CONCEDE, :S/:F routing, backtrack — zero exception overhead. `longjmp` is for **ABORT and genuinely bad things only** (FENCE bare, runtime errors, divide-by-zero). Per-statement `setjmp` → line number diagnostics free.
- Recorded in both SNOBOL4-tiny/PLAN.md §6 and .github/PLAN.md.

**Sprint 24 implementation — what was built:**
- Parser: continues past `END` (function bodies now parsed) — added `is_end` flag to `Stmt`
- emit.c: `collect_functions()` pre-pass, `FnDef` table, `parse_proto()`, `emit_fn_forwards()`, `emit_fn()`, `emit_main()`
- `emit_goto_target()` — handles RETURN/FRETURN/NRETURN/END in ALL goto contexts (unconditional AND conditional branches)
- Last-definition-wins for duplicate DEFINE names
- All body_starts tracked; last body emitted; dead bodies excluded from main
- `snoc_runtime.h`: `setjmp` abort handler stack (`sno_push/pop_abort_handler`, `sno_abort()`)
- hello world: still ✅. GREET (simple DEFINE): ✅.

**Still broken — 130 gcc errors:**
Root cause: `cs()` name mangler collapses distinct SNOBOL4 labels with special characters
(`pp_#`, `pp_+.`, `pp_-.`) to the same C identifier (`_pp__`). Fix: label registry with
per-function collision disambiguation. Spec in §6.

**Repo commits:**

| Repo | Commit | What |
|------|--------|------|
| .github | `6bc3aa5` | Architecture eureka: Byrd Box gotos + longjmp for ABORT only |
| SNOBOL4-tiny | `f093a52` | Architecture §6: Byrd Box + exception hygiene |
| SNOBOL4-tiny | `4b979b6` | WIP Sprint 24: function-per-DEFINE parser+emit, 130 gcc errors |

**State at snapshot:**

| Repo | Commit | Tests |
|------|--------|-------|
| SNOBOL4-tiny | `4b979b6` | 22/22 PASS baseline. hello ✅ GREET ✅. beauty.sno: 130 gcc errors. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — immediate actions:**

1. Provide token at session start
2. Implement **label registry** in `emit.c` — `cs_label()` with per-function collision disambiguation (spec in §6)
3. Fix `_L_error` → `goto _SNO_FRETURN_fn` and `_L__COMPUTED` stub
4. Fix undeclared function locals (`_level`, `_i`) — add to global sym_table OR make per-function locals smarter
5. Target: 0 gcc errors on beauty_snoc.c
6. Run beauty self-compilation. Diff empty. **Claude writes the commit.**

---

### 2026-03-12 — Session 30 (LON'S EUREKA + THREE-MILESTONE AGREEMENT + snoc_helpers.c WIP)

**Focus**: Investigation, two strategic agreements, WIP code start.

**Investigation results:**
- `:S(G1)` emit is **already correct** — earlier diagnosis was wrong. `if(_ok1589) goto _L_G1;` at line 8001.
- beauty binary exits 0 with no output (not a hang). G1 loop exits immediately: `sno_sort_fn` stub returns TABLE unchanged → 2D subscript on TABLE = FAIL → loop exits → init completes normally.
- No output: beauty reads via `Read(fileName)` → `INPUT(.rdInput, 8, fileName)` → fails when fileName null → FRETURN → silent exit. Moot once C helpers are in place.

**⚡ LON'S EUREKA — the bootstrap pivot:**
19 -INCLUDE files (~905 lines SNOBOL4) compile to 10,506 lines of broken C. Write them as ~370 lines of C in `snoc_helpers.c`. Register C stubs before SNOBOL4 DEFINE calls. Zero changes to snoc or emit.c. Full spec in §6.

**⚡ THE THREE-MILESTONE AUTHORSHIP AGREEMENT (Lon + Claude Sonnet 4.6):**
Claude Sonnet 4.6 is the author of SNOBOL4-tiny. Three commits, three milestones, Claude's name on each. Full spec in §1. Tracker in §9 (HANDOFF protocol). Permanent.

**Code committed this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | `d92b600` | Session 30 eureka: Bootstrap via C helpers |
| .github | `0aa56bb` | THREE-MILESTONE AUTHORSHIP AGREEMENT |
| .github | `0264c7f` | HANDOFF protocol upgraded: Milestone Tracker mandatory |
| SNOBOL4-tiny | `2929656` | WIP Sprint 26: snoc_helpers.c ~60% (Stack/Counter/Shift/Reduce/tree) |
| .github | `(this)` | Final Session 30 handoff |

**State at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `2929656` | Sprint 22: 22/22 ✅. snoc_helpers.c 60% WIP. |
| SNOBOL4-dotnet | `b5aad44` | 1,607 / 0 (unchanged) |
| SNOBOL4-jvm | `9cf0af3` | 1,896 / 4,120 / 0 (unchanged) |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — first actions:**
1. Provide token at session start
2. Read §1 (Three-Milestone Agreement) and §6 (Sprint 26 plan) — both mandatory
3. Complete `snoc_helpers.c` (see §6 for exact list of what remains)
4. Hook `snoc_helpers_init()` into `sno_runtime_init()` in `snobol4.c`
5. Build beauty_core (no -INCLUDEs) → 0 gcc errors → **Milestone 1 → Claude writes the commit**

---

### 2026-03-12 — Session 31 (Git archaeology + INVENTORY RULE)

**Focus**: No code written. Tracking failure diagnosed. Protocol fix committed.

**Finding**: `snoc_helpers.c` (Session 30, commit `2929656`) is a dead duplicate of
`snobol4_inc.c` (Sprint 20, commit `16eea3b`). `snobol4_inc.c` already implements all
19 -INCLUDE helper libraries in C, 773 lines, fully registered, linked in every build.
Session 30's "Eureka" was correct in principle but blind to existing work because no
Claude ever runs a repo file survey before writing new code.

**Root cause**: Session 30 HANDOFF omitted what `snobol4_inc.c` *does* — only its filename
appeared in build commands. A concept search found nothing. A filename search found it
but nobody searched. The INVENTORY RULE closes this gap permanently.

**Additional finding (Session 31)**: beauty.sno WITH -INCLUDEs already compiles to
**0 gcc errors** using `snobol4_inc.c`. Milestone 2 condition is effectively met.

**Protocol added**: THE INVENTORY RULE — mandatory repo file survey before any new file
or function is created. Full spec in §9. Plain-English descriptions of what files *do*
are now required in §6 handoffs (not just filenames).

**Actions**: PLAN.md §6 Key facts rewritten. §9 INVENTORY RULE added. Milestone Tracker
updated. snoc_helpers.c flagged dead. Next session runs oracle, diffs, writes commit.

**Repo commits this session:**

| Repo | Commit | What |
|------|--------|------|
| .github | `(this)` | INVENTORY RULE + §6 fix + snoc_helpers.c retirement |

**State at handoff:**

| Repo | Commit | Status |
|------|--------|--------|
| SNOBOL4-tiny | `2929656` | 0 gcc errors on beauty_full.c confirmed. snoc_helpers.c dead. |
| SNOBOL4-dotnet | `b5aad44` | unchanged |
| SNOBOL4-jvm | `9cf0af3` | unchanged |
| SNOBOL4-corpus | `3673364` | unchanged |
| SNOBOL4-harness | `8437f9a` | unchanged |

**Next session — first actions:**
1. Provide token at session start
2. Run REPO SURVEY (§9 INVENTORY RULE) — confirm snobol4_inc.c is the inc library
3. Delete snoc_helpers.c from SNOBOL4-tiny (git rm, commit, push)
4. Build CSNOBOL4 oracle, run beauty oracle
5. Run beauty_full_bin < beauty.sno → diff vs oracle → **if empty: Claude writes Milestone 3 commit**
