# SNOBOL4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET Roslyn), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repo** | SNOBOL4-corpus + SNOBOL4-tiny |
| **Sprint** | `diag1-corpus` committed → resume `bug7-micro` next |
| **HEAD TINY** | `8761bc1` session121: 5-primitive SEQ counter instrumented |
| **HEAD HARNESS** | `198249c` session121: micro0 + micro1 skeleton committed |
| **HEAD HQ** | this commit |
| **Next action** | 1. Commit diag1 suite to SNOBOL4-corpus. 2. Resume session122 bug7-micro: run micro1_concat oracle vs compiled, get diff, fix emit_byrd.c |
| **Invariant** | 106/106 rungs 1–11 must pass before any work |

**Read the active L2 doc: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## Session 122 — Exact Next Steps

```bash
# 0. Verify invariant
cd /home/claude/SNOBOL4-tiny
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106

# 1. Oracle trace — micro1_concat (input 'N + 1', triggers Bug7)
INC=/home/claude/SNOBOL4-corpus/programs/inc
snobol4 -f -I$INC \
    /home/claude/SNOBOL4-harness/skeleton/micro1_concat.sno \
    > /tmp/micro1_oracle_out.txt 2>/tmp/micro1_oracle_trace.txt
cat /tmp/micro1_oracle_trace.txt   # C-level SEQ#### lines on stderr

# 2. Compile micro1 and run
src/sno2c/sno2c -trampoline -I$INC \
    /home/claude/SNOBOL4-harness/skeleton/micro1_concat.sno > /tmp/micro1.c
RT=src/runtime
gcc -O0 -g /tmp/micro1.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o /tmp/micro1_bin
/tmp/micro1_bin > /tmp/micro1_compiled_out.txt 2>/tmp/micro1_compiled_trace.txt
cat /tmp/micro1_compiled_trace.txt

# 3. Diff — first divergence = bug location
diff /tmp/micro1_oracle_trace.txt /tmp/micro1_compiled_trace.txt

# 4. Fix emit_byrd.c at identified location, rebuild beauty_full_bin_trace
# 5. Run crosscheck ladder: 104->105->109->120->130->140
```

### What micro0 told us (session121)

- Oracle `N`: NPUSH→NINC→NPUSH→NPOP→REDUCE→NPOP, MATCH ✅
- Compiled `N` C-trace: same sequence — **Bug7 does NOT fire on bare `N`**
- SNOBOL4-level traced fns (tNPush_ etc.) NOT dispatched in compiled binary
  (pattern-context `'' . *userFn()` not yet supported in mock engine)
- **C-level NPUSH_fn/NPOP_fn instrumentation IS the ground truth for tracing**
- micro1 (`N + 1`) is the minimal input to trigger the ghost frame

---

## M-BEAUTY-CORE Sprint Plan

### What beauty.sno does (essential model)

One big PATTERN matches the entire source. Immediate assignments (`$`) orchestrate
two stacks simultaneously during the match:

**Counter stack** — tracks children per syntactic level:
```
nPush()                  push 0       entering a level
nInc()                   top++        one more child recognized
Reduce(type, ntop())     read count   build tree node — fires BEFORE nPop
nPop()                   pop          exit the level — fires AFTER Reduce
```

**Value stack:**
```
shift(p,t)   pattern constructor — builds p . thx . *Shift('t', thx)
reduce(t,n)  pattern constructor — builds '' . *Reduce(t,n)
Shift(t,v)   match-time worker — push leaf node (called via *Shift(...))
Reduce(t,n)  match-time worker — pop n nodes, push internal node
~ is opsyn for shift (set in semantic.sno)
& is opsyn for reduce (set in semantic.sno)
```

**Invariant:** every `nPush()` must have exactly one `nPop()` on EVERY exit path —
success (γ) AND failure (ω). Missing `nPop` on FENCE backtrack = ghost frame.

### Bug7 — Active

`Expr17` arm1: `FENCE(nPush() $'(' *Expr ... nPop() | *Id ~ 'Id' | ...)`
→ nPush fires, `$'('` fails, FENCE backtracks to arm2 — **nPop SKIPPED**

`Expr15`: `FENCE(nPush() *Expr16 (...) nPop() | '')`
→ same issue when no `[` follows

**Fix location:** `emit_byrd.c` — emit `NPOP_fn()` on ω path of nPush arm
before jumping to next FENCE alternative.

### Skeleton-Build Diagnostic Protocol (PRIMARY)

Build minimal SNOBOL4 test programs, each a strict superset of previous.
Diff oracle (CSNOBOL4) vs compiled (beauty_full_bin_trace) stderr traces.
**First diverging SEQ#### line = exact bug node.**

**All 5 instrumented primitives share `int _nseq` counter:**
```
SEQ0001 NPUSH depth=N top=N    <- snobol4.c NPUSH_fn
SEQ0002 NINC  depth=N top=N    <- snobol4.c NINC_fn
SEQ0003 NPOP  depth=N top=N    <- snobol4.c NPOP_fn
SEQ0004 SHIFT type=T val='V'   <- mock_includes.c Shift()
SEQ0005 REDUCE type=T n=N      <- mock_includes.c Reduce()
```

**Skeleton ladder (harness/skeleton/):**
```
micro0_skeleton.sno   input='N'      Bug7 does NOT fire — baseline ✅
micro1_concat.sno     input='N + 1'  Bug7 FIRES here — TODO session122
micro2_call.sno       input='GT(N,3)' Expr17 arm2/3 (call form)  TODO
micro3_grouped.sno    input='(N+1)'  Expr17 arm1 full path        TODO
micro4_full.sno       109_multi.input full 5-line program          TODO
```

### In-PATTERN Bomb Technique (NEW — session121)

You can place diagnostic calls **directly inside a PATTERN** at any edge
using `'' . *fn()` immediate side-effect syntax. The function fires
**exactly when the match engine reaches that point**, including on backtrack paths.

```snobol4
* Sequence stamp at any pattern edge — no wrapper needed
        DEFINE('seq_(label)', 'seq_B')          :(seq_End)
seq_B   seqN = seqN + 1
        OUTPUT = 'SEQ' LPAD(seqN,4,'0') ' ' label
        seq_ = .dummy                           :(NRETURN)
seq_End

* Embed at FENCE edges to see exactly which path fires:
        Expr17 = FENCE(
+                   '' . *seq_('E17_arm1_enter')
+                   nPush()
+                   $'('
+                   '' . *seq_('E17_arm1_after_paren')   <- never fires if ( fails
+                   nPop()
+                |  '' . *seq_('E17_arm2_enter')         <- fires on backtrack
+                   *Id ~ 'Id'
+                )
```

**The `'' . *seq_('E17_arm1_after_paren')` line will NEVER appear in oracle
trace for input `N` — because `$'('` fails before reaching it.**
**But `'' . *seq_('E17_arm2_enter')` WILL appear — confirming the backtrack path.**

This technique gives surgical visibility into any FENCE arm transition without
modifying the pattern logic. Works in both CSNOBOL4 oracle and compiled binary.

**Bomb variant** — abort on wrong state:
```snobol4
        DEFINE('assertDepth(expected)', 'assertB') :(assertEnd)
assertB EQ(_ntop, expected)                        :S(RETURN)
        OUTPUT = '*** BOMB depth=' _ntop ' expected=' expected
        &STLIMIT = 0                               * force abort
assertEnd
```
Place `'' . *assertDepth(1)` immediately after `nPush()` in arm1 to confirm
depth is correct before `$'('` runs.

### Crosscheck ladder (one at a time, never skip)

```
104_label → 105_goto → 109_multi → 120_real_prog → 130_inc_file → 140_self
```
`140_self` PASS → **M-BEAUTY-CORE fires**.

### Other diagnostic tools

- **&STLIMIT binary search** (`&STCOUNT` broken in CSNOBOL4 — always 0)
- **TRACE:** `TRACE('var','VALUE')` works; `TRACE(...,'KEYWORD')` does NOT
- **DUMP():** full variable dump at any point

---

## Product Matrix

| Frontend | TINY-C | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:------:|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | — | — | — | ⏳ | ⏳ |
| Snocone | — | — | — | — | ⏳ | — |
| Rebus | ✅ | — | — | — | — | — |

✅ done · ⏳ active/in-progress · — planned/future

---

## Milestone Dashboard

| ID | Trigger | Repo | ✓ |
|----|---------|------|---|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | TINY | ✅ |
| M-REBUS | Rebus round-trip diff empty | TINY | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | TINY | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | TINY | ✅ `ac54bd2` |
| **M-STACK-TRACE** | oracle == compiled stack trace, rung-12 inputs | TINY | ✅ session119 |
| **M-DIAG1** | 35-test diag1 suite 35/35 PASS on all backends | CORPUS | ⏳ session122 |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies (mock stubs) | TINY | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies (real -I inc/) | TINY | ❌ |
| **M-FLAT** | flat() emitter wired; style switch bypasses pp/ss; Style B verified | TINY | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC | TINY | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | TINY | ❌ |

---

## L3 Reference Index

| Read when you need… | File |
|--------------------|------|
| SNOBOL4/SPITBOL: two-stack engine, PATTERN map, TDD, diagnostics | [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) |
| sno2c compiler internals | [IMPL-SNO2C.md](IMPL-SNO2C.md) |
| C backend: Byrd boxes, block functions | [BACKEND-C.md](BACKEND-C.md) |
| Testing paradigms, corpus ladder | [TESTING.md](TESTING.md) |
| Rules: token, identity, artifacts | [RULES.md](RULES.md) |
| Session history | [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) |

---

*PLAN.md = L1 index only. Edit L2/L3 files, not this one.*
