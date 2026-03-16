# FRONTEND-SNOBOL4.md — SNOBOL4/SPITBOL Frontend (L3)

SNOBOL4 and SPITBOL are treated as a single frontend (SPITBOL is a SNOBOL4
superset with minor extensions). This frontend is implemented in all three repos.

*Implementation internals (sno2c) → IMPL-SNO2C.md. Testing protocol → TESTING.md.*
*Session state → TINY.md / JVM.md / DOTNET.md.*

---

## Status by Repo

| Repo | Implementation | Active sprint | Milestone |
|------|---------------|---------------|-----------||
| TINY | sno2c (C compiler) | `stack-trace` | M-STACK-TRACE |
| JVM | Clojure interpreter + JVM codegen | `jvm-inline-eval` | M-JVM-EVAL |
| DOTNET | C# interpreter + MSIL JIT | `net-delegates` | M-NET-DELEGATES |

---

## The Proof Program — beauty.sno

`beauty.sno` is the canonical correctness test for the SNOBOL4 frontend.
It is a self-contained SNOBOL4 parser and pretty-printer written in SNOBOL4.
If a backend can run `beauty.sno` self-beautification correctly, the SNOBOL4
frontend is correct on that backend.

**Self-beautification oracle test:**
```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle.sno
<backend-binary> < $BEAUTY > compiled.sno
diff oracle.sno compiled.sno   # empty = frontend correct on this backend
```

---

## How beauty.sno Works — The Two-Stack Engine

beauty.sno is a **pattern-driven tree builder**. One big PATTERN matches the
entire source. Immediate assignments (`$`) fire mid-match to maintain two stacks:

### Counter Stack — tracks children per level

```
nPush()          push 0          entering a new syntactic level
nInc()           top++           one more child recognized
Reduce(type, ntop())             build tree node with ntop() children (read before pop)
nPop()           pop             exit the level (AFTER Reduce)
```

**Discipline:** `nPush` and `nPop` must bracket every syntactic level on ALL
exit paths — both γ (success) and ω (failure). Every sub-pattern that calls
`nPush` must call `nPop` before returning on every path. A missing `nPop` on
the γ path leaves a ghost frame that displaces all subsequent `nInc` calls.

**Reduce comes before nPop.** The sequence is always:
```
... nInc() ... nInc() ... Reduce(type, ntop()) nPop()
```
`ntop()` is read inside `Reduce` to know the child count, then `nPop` discards
the frame. Never nPop before Reduce — the count is gone.

### Value Stack — the tree nodes

```
Shift(type, val)       push one leaf node
Reduce(type, n)        pop n nodes, push one internal node with n children
```

`pp(x)` and `ss(x,len)` walk the resulting tree after the full match.

### Seven Stmt Children

The `Stmt` pattern builds a node with exactly 7 children (some may be null/empty):

| Slot | Name | Content |
|------|------|---------|
| 1 | Label | label string, or empty |
| 2 | Subject | Expr14 — leftmost expression |
| 3 | Pattern | pattern expression, or empty |
| 4 | `=` indicator | literal `=`, or empty |
| 5 | Replacement | Expr — right side of `=`, or empty |
| 6 | goto1 | success goto, or empty |
| 7 | goto2 | failure goto, or empty |

`nInc()` is called once per `Command` (one statement or directive).
`nPush()`/`nPop()` bracket `Parse` and `Compiland`.

### Key Pattern Structure

```
Parse     = nPush() ARBNO(*Command) ("'Parse'" & nTop()) nPop()
Compiland = nPush() ARBNO(*Command) ("'Compiland'" & nTop()) nPop()
Command   = nInc() FENCE(*Comment | *Control | *Stmt)
Stmt      = *Label (*White *Expr14 FENCE(...) | ...) FENCE(*Goto | ...) *Gray
Label     = BREAK(' ' tab nl ';') ~ 'Label'
Expr14    = subject expression (leftmost expr in a statement)
Goto      = *Gray ':' *Gray FENCE(*Target ... | *SorF *Target ... | ...)
```

Includes 19 helper libraries via `-INCLUDE` from `SNOBOL4-corpus/programs/inc/`.

---

## Four-Paradigm TDD Protocol (TINY → M-BEAUTY-FULL)

| Sprint | Paradigm | Catches | Trigger |
|--------|----------|---------|---------||
| `stack-trace` | Dual-stack instrumentation | nPush/nPop/nInc imbalances | M-STACK-TRACE |
| `beauty-crosscheck` | Crosscheck — diff vs oracle | Wrong output | beauty/140_self → **M-BEAUTY-CORE** |
| `beauty-probe` | Probe — &STLIMIT frame-by-frame | WHERE divergence first appears | All failures diagnosed |
| `beauty-monitor` | Monitor — TRACE double-trace | Deep recursion / call-return bugs | Trace streams match |
| `beauty-triangulate` | Triangulate — cross-engine | Edge cases, oracle quirks | Empty diff → **M-BEAUTY-FULL** |

---

## Rung 12 Test Format (TINY crosscheck)

Tests in `SNOBOL4-corpus/crosscheck/beauty/`:
- `NNN_name.input` — SNOBOL4 snippet piped into beauty_full_bin
- `NNN_name.ref` — oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN_name.input`

Runner: `SNOBOL4-tiny/test/crosscheck/run_beauty.sh` (pre-compiled binary).

Test progression (one at a time, never skip):
```
101_comment      * a comment
102_output           OUTPUT = 'hello'
103_assign           X = 'foo'
104_label        LOOP    X = X 1
105_goto             :(END)
109_multi        5-line program
120_real_prog    20-line program
130_inc_file     program using -INCLUDE
140_self         full beauty.sno → M-BEAUTY-CORE
```

Generate oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN.input > NNN.ref`

---

## Stack-Trace Diagnostic Protocol (Sprint `stack-trace`)

**Goal:** produce a dual-stack trace (counter stack + value stack) that matches
the CSNOBOL4 oracle trace for every test input. When they match, `emit_byrd.c`
is correct. Then crosscheck can begin.

### Step 1 — Instrument beauty.sno

Create `beauty_trace.sno` — beauty.sno with `nPush/nInc/nPop/Shift/Reduce`
replaced by tracing wrappers that write to `OUTPUT`:

```snobol4
* Dual-stack trace wrappers
tPush   OUTPUT = 'NPUSH idx=' nIdx
        nIdx = nIdx + 1
        ...  (real nPush logic)

tInc    OUTPUT = 'NINC  idx=' (nIdx - 1) ' count=' nTop()
        ...  (real nInc logic)

tReduce OUTPUT = 'REDUCE type=' type ' n=' n
        ...  (real Reduce logic)

tPop    OUTPUT = 'NPOP  idx=' (nIdx - 1)
        nIdx = nIdx - 1
        ...  (real nPop logic)
```

Run under CSNOBOL4 → `oracle_stack.txt`. This is ground truth.

### Step 2 — Instrument the compiled binary

In `snobol4.c` / `mock_engine.c`, add fprintf(stderr,...) to
`NPUSH_fn`, `NPOP_fn`, `NINC_fn`, `Shift_fn`, `Reduce_fn`.
Rebuild `beauty_full_bin`.

Run compiled binary → `compiled_stack.txt`.

### Step 3 — Diff and locate

```bash
diff oracle_stack.txt compiled_stack.txt
```

First divergence = exact location of imbalance. Then binary-search
`emit_byrd.c` for the missing `nPop()` on the γ path.

### Step 4 — Fix in emit_byrd.c, verify, commit

---

## Probe Script (Paradigm 2)

```bash
python3 /home/claude/SNOBOL4-harness/probe/probe.py \
    --oracle csnobol4 --max 200 failing.sno
```
Probe targets: `pp`, `Command`, `Label`, `ss`, `pp_Parse`.
TRACE gotcha: `TRACE(...,'KEYWORD')` non-functional — use `TRACE('var','VALUE')`.
`&STCOUNT` broken in CSNOBOL4 (always 0) — use `&STLIMIT` binary search.

---

## Monitor Script (Paradigm 3)

Prepend to beauty.sno:
```snobol4
        TRACE('pp','CALL')    TRACE('pp','RETURN')
        TRACE('ss','CALL')    TRACE('ss','RETURN')
        TRACE('pp_Parse','CALL')  TRACE('Command','CALL')
```
```bash
snobol4 -f -P256k -I$INC beauty_trace.sno < input.sno 2>oracle_trace.txt
./beauty_full_bin_trace < input.sno 2>compiled_trace.txt
diff oracle_trace.txt compiled_trace.txt | head -20
```

---

## Triangulate Script (Paradigm 4 — M-BEAUTY-FULL trigger)

```bash
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle_csn.txt
./beauty_full_bin < $BEAUTY > compiled_out.txt
diff oracle_csn.txt compiled_out.txt   # empty = M-BEAUTY-FULL FIRES
```
SPITBOL excluded from full beauty.sno (error 021 at END).
Two oracles agree, compiled differs → our bug. Oracles disagree → check Gimpel §7.

---

## compiler.sno (post-M-BEAUTY-FULL bootstrap path)

`compiler.sno` = `beauty.sno` + `compile(x)` replacing `pp(x)`.
Same parse tree, same grammar (`Parse`/`Compiland`/`Stmt`/`Command`). Final action emits C Byrd boxes instead of SNOBOL4.
Proof: M-BEAUTY-FULL proves tree correct; `compile()` just walks it differently.

Architecture A (future): sprinkle emit actions into pattern alternations via
`epsilon . *action(...)` — like `iniParse` in `programs/inc/ini.sno`. Post-M-BOOTSTRAP.
