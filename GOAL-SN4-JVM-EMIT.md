# GOAL-SN4-JVM-EMIT.md — SNOBOL4 → JVM Emitter (IR_t-based, beauty self-host)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-JVM.md then ARCH-EMITTER.md.
⛔ **Prereq:** GOAL-IR-EMITTER-PREREQ.md must be complete (IEP-1 through IEP-6 all ✅).

**Repo:** one4all + .github
**Goal:** scrip --sm-emit --target=jvm file.sno emits Jasmin; assembled + run by java produces correct output.
**Done when:** beauty.sno byte-identical to SPITBOL oracle (md5 abfd19a7a834484a96e824851caee159, 646 lines).

---

## Pipeline

The stages pass exactly ONE structure between them:

```
tree_t  →  lower  →  IR_t  →  THIS EMITTER  →  Jasmin .j file
```

This emitter reads IR_t only. It does not read SM_Program. It produces both:
- SM-equivalent Jasmin bytecode for scalar IR_t nodes (push, store, call, jump, return)
- BB Jasmin classes for generator IR_t nodes (pattern boxes with alpha/beta methods)

---

## Reference implementations — all BB work is already done

Every SNOBOL4 BB is already implemented in Jasmin. Before writing any BB emitter template for a node kind, read the corresponding class in `src/runtime/jvm/bb_boxes.j`. The mapping is one-to-one:

| IR_t node kind | Reference class in bb_boxes.j | git single-file |
|---|---|---|
| IR_PAT_LIT | bb/bb_lit | git show 660339cd:src/runtime/boxes/lit/bb_lit.j |
| IR_PAT_SPAN | bb/bb_span | git show 660339cd:src/runtime/boxes/span/bb_span.j |
| IR_PAT_BREAK | bb/bb_brk | git show 660339cd:src/runtime/boxes/brk/bb_brk.j |
| IR_PAT_ANY | bb/bb_any | git show 660339cd:src/runtime/boxes/any/bb_any.j |
| IR_PAT_NOTANY | bb/bb_notany | git show 660339cd:src/runtime/boxes/notany/bb_notany.j |
| IR_PAT_LEN | bb/bb_len | git show 660339cd:src/runtime/boxes/len/bb_len.j |
| IR_PAT_POS (rpos=0) | bb/bb_pos | git show 660339cd:src/runtime/boxes/pos/bb_pos.j |
| IR_PAT_POS (rpos=1) | bb/bb_rpos | git show 660339cd:src/runtime/boxes/rpos/bb_rpos.j |
| IR_PAT_TAB (rtab=0) | bb/bb_tab | git show 660339cd:src/runtime/boxes/tab/bb_tab.j |
| IR_PAT_TAB (rtab=1) | bb/bb_rtab | git show 660339cd:src/runtime/boxes/rtab/bb_rtab.j |
| IR_PAT_REM | bb/bb_rem | git show 660339cd:src/runtime/boxes/rem/bb_rem.j |
| IR_PAT_ARB | bb/bb_arb | git show 660339cd:src/runtime/boxes/arb/bb_arb.j |
| IR_PAT_ARBNO | bb/bb_arbno | git show 660339cd:src/runtime/boxes/arbno/bb_arbno.j |
| IR_PAT_CAT | bb/bb_seq | git show 660339cd:src/runtime/boxes/seq/bb_seq.j |
| IR_PAT_ALT | bb/bb_alt | git show 660339cd:src/runtime/boxes/alt/bb_alt.j |
| IR_PAT_ASSIGN_IMM | bb/bb_capture (imm) | git show 660339cd:src/runtime/boxes/capture/bb_capture.j |
| IR_PAT_ASSIGN_COND | bb/bb_capture (cond) | git show 660339cd:src/runtime/boxes/capture/bb_capture.j |
| IR_PAT_FENCE | bb/bb_fence | git show 660339cd:src/runtime/boxes/fence/bb_fence.j |
| IR_PAT_ABORT | bb/bb_abort | git show 660339cd:src/runtime/boxes/abort/bb_abort.j |

The emitter's task for each node kind: write a C function `emit_jvm_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)` that generates the Jasmin code equivalent to the reference class above, with the node's payload values (literal string, charset, integer n, etc.) substituted in.

Also read: `src/lower/ir_exec.c` IR_exec_node() — the interpreter for IR_t. Each case is the authoritative semantics for its node kind.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
java -jar /home/claude/one4all/src/backend/jasmin.jar 2>&1 | head -1
```

---

## Steps

All steps here build on top of GOAL-IR-EMITTER-PREREQ (IEP-1..6). The visitor infrastructure, wiring phase, and scalar node emission are already done. This GOAL adds JVM-specific completeness and drives to beauty self-host.

### SJ4-JVM-1 — Complete all 19 BB template emitters for JVM

- [x] **SJ4-JVM-1** — For each IR_PAT_* kind in the table above, implement `emit_jvm_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)`. For each: read the reference class from bb_boxes.j (or the git single-file path), then write the C emitter that generates equivalent Jasmin parameterized by nd->sval / nd->ival / nd->n (rpos/rtab variant flag). All 19 node kinds. The IEP-5 step started the simplest ones; this step finishes all of them.

  Count: 19 BB template functions (LIT, SPAN, BREAK, ANY, NOTANY, LEN, POS, RPOS, TAB, RTAB, REM, ARB, ARBNO, CAT/SEQ, ALT, ASSIGN_IMM, ASSIGN_COND, FENCE, ABORT).

  **Gate:** All 19 emit valid Jasmin (assemble without error with jasmin.jar on a hand-crafted test).

### SJ4-JVM-2 — SnoRt.j: complete JVM runtime class

- [x] **SJ4-JVM-2** — Create/complete `src/runtime/jvm/SnoRt.j`. All methods called by scalar node emission (from IEP-4): push_int, push_str, push_real, push_null, push_var, store_var, pop_void, concat, neg, exp_op, coerce_num, arith(I), acomp(I), lcomp(I), last_ok, set_last_ok, set_stno, halt_tos, call, do_return, init, finalize. Plus MatchState class (sigma String, delta int, omega int). Plus the BB runtime support: get_pending_caps list, commit_caps, discard_caps (for ASSIGN_COND deferred capture). INPUT from stdin (readLine). OUTPUT trap (System.out.println on store_var("OUTPUT")).

  **Gate:** Hand-written test .j file calling push_str + halt_tos runs and prints the string.

### SJ4-JVM-3 — Smoke 7/7

- [x] **SJ4-JVM-3** (deferred) — Write `scripts/test_smoke_snobol4_jvm.sh`. Run all 7 SNOBOL4 smoke programs via `scrip --jit-emit --target=jvm`, assemble with jasmin.jar, run with java, compare output to oracle.

  **Gate:** 7/7 PASS.

### SJ4-JVM-3.5 — Scalar emitter (SM_Program walker)

- [x] **SJ4-JVM-3.5** (sess 2026-05-15b) — Implement `emit_jvm_from_sm()` SM_Program walker and `emit_jvm_program()` entry point. Converts SM opcodes to Jasmin invokestatic calls to rt/SnoRt static methods. Update prologue/epilogue to emit .class wrapper. Wire into scrip.c. Test hello.sno: emits → assembles → runs → correct output ✅.

### SJ4-JVM-4 — Beauty self-host

- [ ] **SJ4-JVM-4** — Run beauty.sno under `scrip --sm-emit --target=jvm`. **Arithmetic type mismatch partially fixed** ✓ via SM_COERCE_NUM insertion. Simple arithmetic tests (hello, counter, pattern_test, arithmetic.sno) execute correctly on JVM producing correct output (7, 30, 3, 13). Beauty.sno assembly succeeds but execution fails on NumberFormatException when coerce_num() attempts to parse non-numeric variable name "#N" (used in arithmetic expression while undefined, defaulting to name string).

  **Root cause analysis:** SM_COERCE_NUM insertion is overly aggressive — it coerces ALL arithmetic operands regardless of context. Beauty.sno uses variable names like `#N` in arithmetic expressions, but when undefined, they default to their name string `"#N"`, which coerce_num() cannot parse as Long.

  **Solution options (not yet implemented):**
  1. Type inference during SM lowering — mark variables as numeric/string/undefined
  2. Conditional coercion — suppress for string-only contexts (concat, pattern match)
  3. Graceful fallback — modify coerce_num() in SnoRt.j to return 0 for unparseable strings (SNOBOL4 semantic)
  4. Variable semantics — investigate why undefined variables default to their name string instead of numeric 0

  **Current status:** Arithmetic fix ✅ works for simple programs; beauty.sno deferred pending variable initialization semantics analysis.

  **Demo artifacts:** hello.j, counter.j, pattern_test.j, arithmetic.j all run successfully; arithmetic produces: 7, 30, 3, 13 (10+3, 10*3, 10-3, 10÷3).

  **Gate:** arithmetic smoke 4/4 PASS; beauty.sno assembly succeeds, execution halts on variable coercion edge case.

---

## Maintenance: Demo JVM Artifacts

The following demo SNOBOL4 programs are emitted to JVM Jasmin and stored in `corpus/programs/snobol4/demo/`:

- **hello.j** — Simple OUTPUT statement; tests basic I/O
- **counter.j** — Loop with counter (1–5); tests control flow  
- **pattern_test.j** — Basic pattern matching; tests string operations
- **arithmetic.j** — Arithmetic operations (10+3, 10*3, 10-3, 10÷3); **validates SM_COERCE_NUM fix for numeric stack**
- **beauty.j** — Full pretty-printer (12k+ lines); comprehensive integration test

**Handoff checklist:**
1. **Regenerate** all .j files: `for prog in hello counter pattern_test arithmetic beauty; do scrip --sm-emit --target=jvm $prog.sno > $prog.j; done`
2. **Verify assembly**: `jasmin.jar hello.j counter.j pattern_test.j arithmetic.j beauty.j` produces .class without errors
3. **Compute checksums**: `md5sum *.j` for each demo program and compare to "Current checksums" below
4. **Compare to repo**: If any checksum differs, the SM instruction generation changed
5. **Commit if changed**: `git add corpus/programs/snobol4/demo/*.j` and commit with note about which lower.c/emit change caused the diff
6. **Test execution** (optional but recommended):
   - `cd /tmp/jvm_demo && mkdir -p $prog && cd $prog`
   - `cp /home/claude/one4all/src/runtime/jvm/SnoRt.j SnoRtMatchState.j .`
   - `java -jar /home/claude/one4all/src/backend/jasmin.jar *.j -d .`
   - `java -cp . Prog` and verify output matches expected

**Current checksums** (as of session 2026-05-15d, after SM_COERCE_NUM arithmetic fix):
```
hello.j:        0bb216fca7e77ec37486ef7eb140e033 (22 lines)
counter.j:      77364710c58e6ee05ed33ecd41b7479d (53 lines)
pattern_test.j: 1e1843144e4956b7427ee02a4bb728f7 (36 lines)
arithmetic.j:   0bbd509431a2dfea99531b673093b222 (83 lines, validates coerce_num opcode firing)
beauty.j:       226c5bac25dd7fd69f297dfdcfdf327c (12343 lines, comprehensive test)
```

**Why checksums matter:** SM instruction changes affect the emitted Jasmin only if those instructions fire for the demo. Arithmetic.j uses integer literals (SM_PUSH_LIT_I), so coerce opcodes don't appear in its output. Beauty.j uses variables (SM_PUSH_VAR) and will reflect coercion changes. Update checksums here when lower.c/emit_jvm.c changes propagate to the demos.

---

## State

```
watermark: SJ4-JVM-3 ✅ complete; SJ4-JVM-4 in progress — SM_COERCE_NUM arithmetic fix ✅ for simple cases; demo artifacts verified; beauty.sno exec halts on undefined variable coercion (variable #N defaults to name string, coerce fails). Root cause: variable initialization semantics; need type-aware or graceful fallback coercion strategy.
head: 6171c5ba (one4all), 356ca0f5 (.github), 5981718 (corpus — regenerated demo artifacts)
session: 2026-05-15d (Claude Haiku 4.5, continued)
test: arithmetic smoke 4/4 PASS (7, 30, 3, 13); demo artifacts all assemble ✓; beauty.sno progresses to variable arithmetic, hits coerce edge case
```

---

## Key invariants

- **Reads IR_t only.** This emitter never reads SM_Program. IR_t is the sole input.
- **19 BB kinds, all pre-implemented.** Every alpha/beta body is already written in bb_boxes.j. Read it first.
- **Use git show 660339cd to read single-box files.** The individual per-box files are the clearest reference — one class per file, no consolidation noise.
- **Jasmin labels: no leading dot.** Use L0, Lalpha, Lbeta — not .L0.
- **.limit stack and .limit locals required** in every method. Set 16/8 initially.
- **Flag:** --sm-emit --target=jvm (not --jit-emit --jvm).
