# INTERP-X86.md — x86 Interpreter (C)

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE

---

## What It Is

The x86 interpreter executes `SM_Program` instructions in C. It is the
primary development and testing vehicle for the SCRIP stack machine.

When the interpreter passes the full corpus, the x86 emitter can emit
the same SM_Program as native x86 code with confidence — because they
execute the same instruction stream.

**Binary name:** `scrip-interp`
**Language:** C
**Contains:** SM dispatch loop + BB-DRIVER + all 25 bb_*.c boxes

---

## Architecture

```
scrip-interp
  ├── SM dispatch loop      (src/runtime/sm/sm_interp.c)  ← TO BE WRITTEN
  ├── SM-LOWER              (src/runtime/sm/sm_lower.c)   ← TO BE WRITTEN
  ├── BB-DRIVER             (src/runtime/dyn/stmt_exec.c) ✅
  ├── 25 bb_*.c boxes       (src/runtime/boxes/*/bb_*.c)  ✅
  ├── bb_pool               (src/runtime/asm/bb_pool.c)   ✅
  ├── bb_emit               (src/runtime/asm/bb_emit.c)   ✅ (TEXT mode)
  └── NV store / runtime    (src/runtime/snobol4/)        ✅
```

---

## Current State (2026-04-04)

`scrip-interp` currently exists but tree-walks the IR (`EXPR_t`/`STMT_t`)
directly instead of executing `SM_Program` instructions. This is wrong.

What needs to change:
1. Write `SM-LOWER`: `Program*` → `SM_Program` (IR → instruction stream)
2. Write `sm_interp.c`: dispatch loop over `SM_Program`
3. `scrip-interp.c` driver calls SM-LOWER then sm_interp, not the tree-walker

The BB-DRIVER, bb_*.c boxes, and bb_pool are correct and reusable as-is.

---

## Corpus Status

With the tree-walking scrip-interp (wrong architecture, but same runtime):
- Broad corpus: **177p/1f** (DYN-81, 2026-04-04)

This number proves the BB-DRIVER and boxes are correct.
It will be the baseline for the SM_Program-based interpreter.

---

## Build

```bash
cd /home/claude/one4all
ROOT=$(pwd); RT="$ROOT/src/runtime"
gcc -O0 -g -I src -I "$RT/snobol4" -I "$RT" -I "$RT/boxes/shared" \
    src/driver/scrip-interp.c \
    src/frontend/snobol4/lex.c src/frontend/snobol4/parse.c \
    src/runtime/snobol4/snobol4.c src/runtime/snobol4/snobol4_pattern.c \
    src/runtime/dyn/stmt_exec.c src/runtime/dyn/eval_code.c \
    $(find src/runtime/boxes -name "bb_*.c") \
    -lgc -lm -o scrip-interp
```

---

## Test

```bash
INTERP=/tmp/dyn_run_s.sh
CORPUS=/home/claude/corpus
TIMEOUT=10
bash test/run_interp_broad.sh
```

---

## References

- `SCRIP-SM.md` — the instruction set this interpreter executes
- `BB-DRIVER.md` — the Phase 3 executor inside this interpreter
- `BB-GRAPH.md` — the graph structure the driver runs
- `EMITTER-X86.md` — the emitter that produces native code from same SM_Program
