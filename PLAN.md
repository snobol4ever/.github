# SNOBOL4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends. Self-hosting goal: sno2c compiles sno2c.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET Roslyn), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

| | |
|-|-|
| **Active repo** | SNOBOL4-tiny |
| **Sprint** | `bug7-micro` — skeleton-build PATTERN isolation → fix emit_byrd.c |
| **HEAD** | `07d4b14` EMERGENCY WIP session116 |
| **Next action** | Run skeleton ladder (skeleton→+counter→+value→full) against oracle; first divergence pins exact FENCE arm; fix emit_byrd.c; run crosscheck ladder 104→105→109→140 |
| **Invariant** | 106/106 rungs 1–11 must pass before any work |

**Read the active L2 doc: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## M-BEAUTY-CORE Sprint Plan

### What beauty.sno does (essential model)

One big PATTERN matches the entire source. Immediate assignments (`$`) orchestrate
two stacks simultaneously during the match:

**Counter stack** — tracks children per syntactic level:
```
nPush()                  push 0       entering a level (Parse, Expr3, Expr4, Expr15, Expr17, ExprList)
nInc()                   top++        one more child at this level (X3, X4, XList, Command)
Reduce(type, ntop())     read count   build tree node — fires BEFORE nPop
nPop()                   pop          exit the level — fires AFTER Reduce
```

**Value stack** — the tree nodes:
```
shift(type, val)         push one leaf    (lowercase — the primitive worker; ~ is opsyn)
reduce(type, n)          pop n leaves, push one internal node  (& is opsyn)
```

Note: uppercase `Shift`/`Reduce` are the SNOBOL4 functions from ShiftReduce.sno that
call the lowercase primitives. The compiled binary instruments the lowercase C workers
directly. Oracle tracing wraps the lowercase SNOBOL4 functions.

**Invariant:** every `nPush()` must have exactly one matching `nPop()` on EVERY
exit path — success (γ) AND failure (ω). Missing `nPop` on any FENCE backtrack
path leaves a ghost frame that displaces all subsequent `nInc` calls.

### Bug7 — Active (confirmed session120)

`Expr17` (beauty.sno line 347):
```
FENCE(
   nPush() $'(' *Expr (...) $')' nPop()   ← arm 1: nPush fires, $'(' fails → nPop SKIPPED
|  *Function ... ("'Call'" & 2)
|  *Id      ... ("'Call'" & 2)
|  *Id ~ 'Id'                             ← taken for bare identifiers
|  ...
)
```
`Expr15` (line 343) same issue:
```
FENCE(nPush() *Expr16 ("'[]'" & 'nTop() + 1') nPop() | epsilon)
         ↑ fires     ↑ fails when no '['       ↑ SKIPPED, epsilon taken
```

**Fix:** in `emit_byrd.c`, for every `FENCE(nPush() ... nPop() | ...)`:
emit `NPOP_fn()` on the backtrack/failure exit of the nPush arm, before
jumping to the next alternative or returning ω.

### Skeleton-Build Diagnostic Protocol (NEW — replaces Bomb Protocol)

Build minimal SNOBOL4 test programs, each a strict superset of the previous.
Diff each level's trace (oracle CSNOBOL4 vs compiled binary) immediately.
**First divergence at a given level pins the exact pattern node.**

**All 5 instrumented primitives** share a single `SEQ####` counter:
```
SEQ0001 NPUSH depth=N top=N
SEQ0002 NINC  depth=N top=N
SEQ0003 NPOP  depth=N top=N
SEQ0004 SHIFT type=T val='V'
SEQ0005 REDUCE type=T n=N
```
Counter is global across nPush/nInc/nPop (snobol4.c) and shift/reduce (mock_includes.c)
via `extern int _nseq`. First line of diff = exact bug location.

**Level 0 — Pure skeleton:** PATTERN structure only, all workers replaced by
tracing no-ops. Verifies pattern control flow (FENCE/ARBNO/etc.) is correct.

**Level 1 — +counter workers:** Add real nPush/nInc/nPop logic with tracing.
Counter stack depth/top printed each event. First divergence here = counter imbalance.

**Level 2 — +value workers:** Add real shift/reduce with tracing.
First divergence here = value stack mismatch.

**Level 3 — Full:** Run full beauty_full_bin on 109_multi.input.
All 5 primitives traced. 94 compiled lines vs oracle lines — first diff = bug.

**Test inputs (smallest first):**
```
N              ← bare Id, exercises Expr17 arm 4 only
N + 1          ← concat, exercises Expr4/X4 + Expr17
GT(N,3)        ← call, exercises Expr17 arm 2/3
(N + 1)        ← grouped, exercises Expr17 arm 1 (the nPush arm)
109_multi      ← full 5-line program
```

### Crosscheck ladder (one at a time, never skip)

```
104_label   → 105_goto → 109_multi → 120_real_prog → 130_inc_file → 140_self
```
`140_self` PASS → **M-BEAUTY-CORE fires**.

### Diagnostic tools

1. **Skeleton-build trace diff** (PRIMARY — NEW): skeleton → +counter → +value → full.
   First SEQ line divergence = exact bug node in emit_byrd.c.

2. **&STLIMIT binary search** (note: `&STCOUNT` is broken in CSNOBOL4, always 0).

3. **TRACE:** `TRACE('pp','CALL')` etc. for call/return tracing.
   Gotcha: `TRACE(...,'KEYWORD')` non-functional — use `TRACE('var','VALUE')`.

4. **DUMP():** full variable dump at any point.

---

## Product Matrix (frontend × backend)

| Frontend | TINY-C | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:------:|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | — | — | — | ⏳ | ⏳ |
| Snocone | — | — | — | — | ⏳ | — |
| Rebus | ✅ | — | — | — | — | — |
| Tiny-ICON | — | — | — | — | — | — |
| Tiny-Prolog | — | — | — | — | — | — |
| C# | — | — | — | — | — | — |
| Clojure-EDN | — | — | — | — | ✅ | — |

✅ done · ⏳ active/in-progress · — planned/future

---

## Milestone Dashboard

| ID | Trigger | Repo | ✓ |
|----|---------|------|---|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | TINY | ✅ |
| M-REBUS | Rebus round-trip diff empty | TINY | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | TINY | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | TINY | ✅ `ac54bd2` |
| **M-STACK-TRACE** | oracle_stack.txt == compiled_stack.txt for all rung-12 inputs | TINY | ✅ session119 |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies (mock stubs) | TINY | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies (real -I inc/) | TINY | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC → block_fn_t | TINY | ❌ |
| M-BYRD-SPEC | Language-agnostic Byrd box spec, all backends | HQ | ❌ |
| M-SNO2C-SNO | sno2c.sno compiled by C sno2c | TINY | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | TINY | ❌ |
| M-JVM-EVAL | JVM inline EVAL! | JVM | ❌ |
| M-JVM-SNOCONE | Snocone self-test on JVM | JVM | ❌ |
| M-NET-DELEGATES | .NET Instruction[] eliminated | DOTNET | ❌ |
| M-NET-SNOCONE | Snocone self-test on .NET | DOTNET | ❌ |

---

## L3 Reference Index

| Read when you need… | File |
|--------------------|------|
| **Frontends** | |
| SNOBOL4/SPITBOL: beauty.sno two-stack engine, full PATTERN map, TDD protocol, rung 12, diagnostic tools | [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) |
| Snocone: status, corpus, sprint sequence | [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) |
| Rebus: TR 84-9 §5 rules, round-trip protocol | [FRONTEND-REBUS.md](FRONTEND-REBUS.md) |
| Tiny-ICON: Byrd box connection, JCON reference | [FRONTEND-ICON.md](FRONTEND-ICON.md) |
| Tiny-Prolog: SLD resolution / Byrd box mapping | [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) |
| C# frontend (DOTNET only) | [FRONTEND-CSHARP.md](FRONTEND-CSHARP.md) |
| Clojure-EDN frontend (JVM only) | [FRONTEND-CLOJURE.md](FRONTEND-CLOJURE.md) |
| **Backends** | |
| C native: Byrd box techniques, block functions, setjmp, arch decisions | [BACKEND-C.md](BACKEND-C.md) |
| x64 ASM: Technique 2 mmap+memcpy+relocate | [BACKEND-X64.md](BACKEND-X64.md) |
| .NET MSIL: solution layout, open issues, performance | [BACKEND-NET.md](BACKEND-NET.md) |
| JVM bytecodes: design laws, file map, open issues | [BACKEND-JVM.md](BACKEND-JVM.md) |
| **Implementation** | |
| sno2c compiler internals: lex/parse/emit, SIL naming, CNode, artifacts | [IMPL-SNO2C.md](IMPL-SNO2C.md) |
| **Shared** | |
| Byrd box concept, oracle hierarchy, corpus ladder | [ARCH.md](ARCH.md) |
| Four testing paradigms, corpus ladder protocol | [TESTING.md](TESTING.md) |
| Mandatory rules: token, identity, artifacts, hierarchy | [RULES.md](RULES.md) |
| Session history | [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) |
| Runtime patches | [PATCHES.md](PATCHES.md) |
| Background, JCON reference, keyword tables | [MISC.md](MISC.md) |

---

*PLAN.md = L1 index only. ~3KB max. Edit L2/L3 files, not this one.*
