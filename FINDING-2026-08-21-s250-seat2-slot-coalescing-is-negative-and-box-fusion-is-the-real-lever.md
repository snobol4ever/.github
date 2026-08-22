# FINDING s250 — SLOT COALESCING IS MEASURABLY NEGATIVE, AND BOX FUSION IS THE REAL LEVER

**Session:** s250 (seat2, `/home/claude2`, Claude Opus 5) · **Date:** 2026-08-21 · **Queue row:** `chain-slot-coalescing` (rank 0)
**Tree:** SCRIP `58fd2369`, clean · RT_OPT `-O0` · governor `performance` · perf shim `/home/claude/.tools/bin/perf`

⛔ **NOTHING LANDED. This row is BLOCKED on a design call and the ask is filed (`hq/q-chain-slot-coalescing`).**
This document exists so the four experiments below are never paid for twice.

---

## 1. THE HEADLINE — THE ROW'S NAMED MECHANISM CANNOT ACHIEVE THE ROW'S OWN TARGET

The row is `chain-slot-coalescing` and its TARGET is *"coalesce the slots along `var -> binop -> assign` so a statement's
descriptor makes ONE round trip instead of three."* **Coalescing the slots does not remove a single round trip, and measured
head-to-head it is 4.2% SLOWER than what ships today.** Sharing a cell changes the *address* of a hand-off, not the fact of it:
a store→load pair is still a store→load pair. The thing that removes round trips is **fusing the boxes** so the value stays in
a register, and that is worth **−15.7%** on this kernel from a single statement.

| arm | instr/it | cyc/it (mean) | cyc/it (min) | stores/it | vs shipped |
|---|---|---|---|---|---|
| **A** — shipped | 112.24 | 25.347 | 25.290 | 24.05 | — |
| **B** — slot-coalesced | 112.25 | **26.408** | 26.329 | 24.05 | **+4.2% (WORSE)** |
| **C** — box-fused | 93.23 | **21.362** | 21.304 | 17.05 | **−15.7%** |

**8 interleaved rounds, A/B/C back-to-back in one loop, ranges DISJOINT:** A ∈ [25.290, 25.381], B ∈ [26.329, 26.481],
C ∈ [21.304, 21.429]. B was slower than A and C faster than A in **8 of 8 rounds**. All three arms print the identical
correct answer (`50000000`).

⭐ **Why B loses.** Identical instruction count (112.25 vs 112.24) and identical store count (24.05 both) — the *only* variable
is whether the binop writes its result back into the cell the var box just wrote, or into a fresh one. Writing back into the
just-read address serialises store-to-load forwarding on one address; two distinct addresses let the out-of-order engine
overlap the two hand-offs. **The spine's apparent redundancy is buying memory-level parallelism.** This is the counterintuitive
result of the session and it kills a whole family of "share the slot" ideas, not just this one.

---

## 2. FIRST STEP — THE s249 COST MODEL REPRODUCES EXACTLY (tree has not moved)

m4 binaries, fixed 50M-iteration driver (no timed harness — the payload is the only variable), `perf stat -r 3`:

| payload | instr/it | cyc/it | stores/it | loads/it |
|---|---|---|---|---|
| 0 × `A = A + 1` | 82.21 | 18.33 | 16.05 | 23.06 |
| 1 × | 112.23 | 25.40 | 24.05 | 30.07 |
| 2 × | 142.26 | 34.47 | 32.06 | 37.08 |
| 3 × | 172.29 | 45.57 | 40.07 | 44.09 |

Marginal statement: **+30.03 instructions** (exact, three times over), **+8.00 stores** (exact), **+9.08 cycles** (mean of 3).
s249 predicted +30 and ~+9. Confirmed independently at the asm level — the fast path is exactly 30 instructions and 8 stores:
`statement_begin` 1 + `var` 6 + `lit_integer` 5 + `binop` 11 + `assign` 5 + `statement_end` 2.

---

## 3. ⛔ BOTH CASES THE BRIEF NAMED FAIL ON ARRIVAL

### 3.1 Case (1) is not a copy as worded — and implementing it literally is a MISCOMPILE

`IR_COERCE_NUMERIC` is a **pairwise** node, not a unary one. `--dump-ir` on `LT(ZI, 5)`:

```
15     VAR             [] var="ZI"
16     LIT_INTEGER     [] 5
17     COERCE_NUMERIC  [15,16]     <- operands[0] = value coerced, operands[1] = the SIBLING
18     COERCE_NUMERIC  [16,15]
19     CMP_TEST        [17,18]
```

and `bb_coerce_numeric` branches on the **sibling's** tag (`mov eax, dword ptr [rsp+16]; cmp eax,3; jne -> rt_coerce_num2_d`).
So `COERCE_NUMERIC[LIT_INTEGER 5, VAR ZI]` with `ZI` real must **promote 5 to DT_R** — it is not a copy of the literal.

**Census, 337 programs (`corpus/benchmarks/snobol4` + `corpus/crosscheck`), 266 `COERCE_NUMERIC` nodes:**

| shape | count | verdict |
|---|---|---|
| operands[0] statically numeric — **the brief's literal condition** | 107 | unsound as a copy test |
| BOTH static AND same type — the only true copies | **50** | all `LIT_INTEGER/LIT_INTEGER` |
| BOTH static, DIFFERENT type (`LIT_REAL/LIT_INTEGER`, `LIT_INTEGER/LIT_REAL`) | **2** | ⛔ **would MISCOMPILE** |
| `LIT_INTEGER` paired with `VAR` (sibling type unknown at compile time) | 90 | not a copy |
| `VAR/VAR` | 66 | not a copy |

**On `arith_loop` itself: 6 `COERCE_NUMERIC` nodes — 4 `VAR/VAR`, 1 `CALL/VAR`, 1 `VAR/CALL`, ZERO with a static operand.**
Case (1) fires **0 times** on the DONE-WHEN benchmark, and the 50 sound sites are all constant-vs-constant compares sitting on
no hot chain — i.e. exactly the 0.02 cyc/instr off-chain class the brief's own banner forbids spending on.

### 3.2 Case (2) is not expressible through `cp_source` at all

`cp_source`'s contract is *"return the node whose slot this node merely copies"*; `cp_run` redirects the consumer's operand
edge and the copy node falls out of the reference set. **`IR_VAR` has no operands** — every one dumps as `VAR [] var="ZI"` — so
`copy_prop.c:14` (`n_operands < 1`) returns 0 for every var that will ever exist. `IR_VAR` is a **producer** (loads
`[r9+k*16]`, stores to its spine slot), not a copy of another node's slot. There is nothing for `cp_source` to return.
Deleting a var box requires teaching **consumers** to address the GVA directly — new operand-addressing machinery, not a
`cp_source` case. The half-measure (forward the read, keep the store) is FINDING s249 §7A.2, measured at ~3.4% and already dead.

⭐ **After s249 took the null-concat, NO `cp_source`-expressible shape remains on `arith_loop`'s chain.** The prescribed
mechanism cannot reach the DONE-WHEN.

---

## 4. ⭐ WHAT DOES WORK — ARM C, AND WHAT IT COSTS

Arm C replaces `var → lit_integer → binop → assign` with one box, RSP discipline untouched (`statement_end` still adds 48):

```
n25_var_α:   sub rsp, 48
             mov eax, dword ptr [r9 + 32]      # A tag guard
             cmp eax, 3;  jne .Lfuse_slow
             mov rax, qword ptr [r9 + 40]      # A value
             add rax, 1
             mov qword ptr [r9 + 40], rax      # A value
             jmp n29_statement_end_α
.Lfuse_slow: ud2                               # prototype only: A is DT_I on every iteration here
```

| | shipped | fused | Δ |
|---|---|---|---|
| instructions for the statement | 30 | **11** | −19 |
| stores for the statement | 8 | **1** | −7 |
| cycles for the statement | ~9.08 | **~5.09** | **−44%** |

One load, one add, one store — **ONE round trip, which is precisely the row's stated TARGET.** The `ud2` is honest prototype
scaffolding: the slow arm never executes in this kernel, and a real implementation must route it to the existing three-box path.

⭐ **The template for this already exists and is DEAD CODE.** `src/templates/bb_binop_gvar_arith_slot.cpp` is declared in
`bb_templates.h:83` and defined — and **never called from anywhere**. `grep -rn 'bb_binop_gvar_arith_slot' src/` returns only
the declaration and the definition; `IR_BINOP_GVAR_ARITH` appears in no lowerer and no IR enum. Its second arm already handles
exactly `{ADD,SUB,MUL,DIV,MOD}` × `{LIT_INTEGER, VAR}` operands. **Someone built this arm and never wired it.**

### 4.1 THE SAFETY CONDITION, STATED PRECISELY (the brief demands this BEFORE any code)

Fusion of `IR_ASSIGN(V) ← IR_BINOP(op, IR_VAR(V), IR_LIT_INTEGER)` is legal iff **all** hold:

1. `op ∈ {ADD, SUB, MUL, DIV, MOD}` — the closed arith family, every member treated identically (⛔ NO PER-OP FILTER).
2. `V` is GVA-resident and the **same** name on both sides.
3. The `BINOP` is the `ASSIGN`'s sole consumer, and the `VAR` is the `BINOP`'s sole consumer.
4. **Nothing executes between the read and the write that can write `V`.** With both operands materialisable inline (a global
   and an integer literal) the interval contains *no other box*, so this holds by construction — which is exactly why this
   narrow shape is the right first rung.

⭐ **Condition 4 is why the brief's `f(x) + A` / `A + f(x)` asymmetry does not arise here and must not be approximated
elsewhere.** SNOBOL4 evaluates left to right, so a var box's spine slot is a **snapshot taken at its own α**. Any scheme that
deletes the box and re-reads the GVA at the *consumer's* α moves the read later in time; if anything in between can write `V`,
the value changes. The general predicate belongs in ONE property-named function — `ir_node_may_write_globals(nd)` — answered
uniformly for whole families (ALL `IR_CALL*` may write; ALL `IR_MATCH_*` may write, since `.`/`$` assign during matching; ALL
literals may not), never as a per-op exception list.

---

## 5. THE UPDATED PRICE LIST (extends s249 §7C.1)

| work | cyc/instr | measured by |
|---|---|---|
| taken `jmp` to the next label | ~0.00 | s249 §7A.1 |
| off-chain `mov` (the concat box) | 0.02 | s249 §3.1 |
| **slot coalescing on the chain** | **NEGATIVE (+1.06 cyc/iter, 0 instructions changed)** | **§1 above, 8/8 interleaved** |
| `sub rsp,16` spine carve | 0.17 | s249 §7C.1 |
| on-chain statement work | 0.30 | s249 §7B.2, reproduced §2 |
| **box fusion (var+lit+binop+assign → 1)** | **−19 instr, −7 stores, −3.99 cyc/iter** | **§4 above, 8/8 interleaved** |

---

## 6. WHAT I DID NOT DO, AND WHY

- **Did not land case (1) in its sound form** (both operands static, same type). It is correct and it fires 50 times, but every
  one of those sites is off-chain — the 0.02 cyc/instr class. Landing it would repeat precisely the mistake the brief's own
  ⛔⛔ banner was written to prevent, and would touch codegen for a win no instrument here can resolve.
- **Did not touch `zd_k()`/`zd_plan()`.** Banned by the brief, and §1 shows slot planning was never the lever anyway.
- **Did not build the fusion.** It needs a design call HQ owns: wiring a dead template + a new IR node is "new machinery", which
  the brief says this row does not need. Filed as `ask chain-slot-coalescing`; not freelancing past it.

**Recommended re-scope:** rename the row to **`chain-box-fusion`**, target the dead `bb_binop_gvar_arith_slot` arm, and gate it
on §4.1. The sibling rank-0 row `spine-carve-coalescing` is unblocked and independently worth ~6% (s249 §7C.2).
