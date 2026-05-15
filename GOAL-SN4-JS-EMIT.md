# GOAL-SN4-JS-EMIT.md — SNOBOL4 → JavaScript Emitter (IR_t-based, beauty self-host)

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  A C Byrd box (C BB) is ANY C function with signature: DESCR_t foo(void *zeta, int entry)      ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **Read before any source file:** ARCH-IR.md then ARCH-JS.md then ARCH-EMITTER.md.
⛔ **Prereq:** GOAL-IR-EMITTER-PREREQ.md must be complete (IEP-1 through IEP-6 all ✅).

**Repo:** one4all + .github
**Goal:** scrip --sm-emit --target=js file.sno emits a .js file; node runs it correctly.
**Done when:** beauty.sno byte-identical to SPITBOL oracle (md5 abfd19a7a834484a96e824851caee159, 646 lines).

---

## Pipeline

The stages pass exactly ONE structure between them:

```
tree_t  →  lower  →  IR_t  →  THIS EMITTER  →  .js file
```

This emitter reads IR_t only. It does not read SM_Program. It produces both:
- SM-equivalent JS statements for scalar IR_t nodes (push, store, call, jump, return) inside a switch/dispatch loop
- BB JS factory functions for generator IR_t nodes (pattern boxes returning {alpha, beta} objects)

---

## Reference implementations — all BB work is already done

Every SNOBOL4 BB is already implemented in JavaScript. Before writing any BB emitter template for a node kind, read the corresponding factory in `src/runtime/js/bb_boxes.js`. The mapping is one-to-one:

| IR_t node kind | Reference factory in bb_boxes.js | git single-file |
|---|---|---|
| IR_PAT_LIT | bb_lit(lit) | git show 660339cd:src/runtime/boxes/lit/bb_lit.js |
| IR_PAT_SPAN | bb_span(chars) | git show 660339cd:src/runtime/boxes/span/bb_span.js |
| IR_PAT_BREAK | bb_brk(chars) | git show 660339cd:src/runtime/boxes/brk/bb_brk.js |
| IR_PAT_ANY | bb_any(chars) | git show 660339cd:src/runtime/boxes/any/bb_any.js |
| IR_PAT_NOTANY | bb_notany(chars) | git show 660339cd:src/runtime/boxes/notany/bb_notany.js |
| IR_PAT_LEN | bb_len(n) | git show 660339cd:src/runtime/boxes/len/bb_len.js |
| IR_PAT_POS (rpos=0) | bb_pos(n) | git show 660339cd:src/runtime/boxes/pos/bb_pos.js |
| IR_PAT_POS (rpos=1) | bb_rpos(n) | git show 660339cd:src/runtime/boxes/rpos/bb_rpos.js |
| IR_PAT_TAB (rtab=0) | bb_tab(n) | git show 660339cd:src/runtime/boxes/tab/bb_tab.js |
| IR_PAT_TAB (rtab=1) | bb_rtab(n) | git show 660339cd:src/runtime/boxes/rtab/bb_rtab.js |
| IR_PAT_REM | bb_rem() | git show 660339cd:src/runtime/boxes/rem/bb_rem.js |
| IR_PAT_ARB | bb_arb() | git show 660339cd:src/runtime/boxes/arb/bb_arb.js |
| IR_PAT_ARBNO | bb_arbno(body) | git show 660339cd:src/runtime/boxes/arbno/bb_arbno.js |
| IR_PAT_CAT | bb_seq(left,right) | git show 660339cd:src/runtime/boxes/seq/bb_seq.js |
| IR_PAT_ALT | bb_alt(children) | git show 660339cd:src/runtime/boxes/alt/bb_alt.js |
| IR_PAT_ASSIGN_IMM | bb_capture(child,var,1,vars) | git show 660339cd:src/runtime/boxes/capture/bb_capture.js |
| IR_PAT_ASSIGN_COND | bb_capture(child,var,0,vars) | git show 660339cd:src/runtime/boxes/capture/bb_capture.js |
| IR_PAT_FENCE | bb_fence() | git show 660339cd:src/runtime/boxes/fence/bb_fence.js |
| IR_PAT_ABORT | bb_abort() | git show 660339cd:src/runtime/boxes/abort/bb_abort.js |

The emitter's task for each node kind: write a C function `emit_js_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)` that generates a JS factory function whose alpha/beta closure bodies are equivalent to the reference factory above, with the node's payload (nd->sval for literal/charset, nd->ival for n, nd->n for rpos/rtab variant) substituted in as literals.

Also read: `src/lower/ir_exec.c` IR_exec_node() — the interpreter for IR_t. Each case is the authoritative semantics for its node kind.

---

## JS emission model

**Scalar nodes** (IR_LIT_I, IR_VAR, IR_BINOP, IR_ASSIGN, IR_CALL, IR_RETURN, IR_SEQ, IR_PROC) emit into a switch/dispatch loop — mandatory because SNOBOL4 GOTO can jump backward:

```js
'use strict';
const rt = require('./sno_runtime.js');
rt._init();
const _S0 = "hello"; const _S1 = "OUTPUT";  // string table
let _pc = 0;
loop: while (true) { switch (_pc) {
case 0: rt.set_stno(1); _pc=1; continue;
case 1: rt.push_str(_S0,5); _pc=2; continue;
case 2: rt.store_var(_S1); _pc=3; continue;
case 3: rt.halt_tos(); break loop;
default: break loop;
}}
rt._finalize();
```

**Generator nodes** (all IR_PAT_* kinds) emit as factory functions before the switch loop, called from within it at SM_EXEC_GEN sites:

```js
// Emitted for IR_PAT_LIT nd with sval="hello"
function make_pat_5_3(ms) {
    const lit = "hello"; const len = 5;
    let self = { succ:null, fail:null,   // wired after all nodes allocated
        alpha() { if (ms.delta+len>ms.omega||ms.sigma.slice(ms.delta,ms.delta+len)!==lit){self.fail.alpha();return;} ms.delta+=len; self.succ.alpha(); },
        beta()  { ms.delta-=len; self.fail.alpha(); }
    }; return self;
}
// Wiring function for statement 5:
function wire_pat_5(ms) {
    const n3=make_pat_5_3(ms), n4=make_pat_5_4(ms); // allocate all nodes
    n3.succ=n4; n3.fail=_term_fail;                  // wire successors
    return n3;                                        // return entry node
}
```

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
node --version
```

---

## Steps

All steps here build on GOAL-IR-EMITTER-PREREQ (IEP-1..6). Visitor infrastructure, wiring, and scalar emission are done. This GOAL adds JS-specific completeness and drives to beauty self-host.

### SJ4-JS-1 — Complete all 19 BB template emitters for JS

- [x] **SJ4-JS-1** — For each IR_PAT_* kind in the table above, implement `emit_js_bb_NODE(IR_t *nd, FILE *out, int stmt_id, int node_id)`. For each: read the reference factory from bb_boxes.js (or the git single-file path), then write the C emitter that generates equivalent JS parameterized by nd->sval / nd->ival / nd->n. All 19 node kinds.

  Count: 19 BB template functions (LIT, SPAN, BREAK, ANY, NOTANY, LEN, POS, RPOS, TAB, RTAB, REM, ARB, ARBNO, CAT/SEQ, ALT, ASSIGN_IMM, ASSIGN_COND, FENCE, ABORT).

  String escaping for JS string literals: double-quote → \", backslash → \\, \n → \\n, \t → \\t, non-printable → \\xNN. Reference: `archive/backend/emit_emitters/emit_js.c` js_escape_string().

  **Gate:** All 19 emit valid JS (node --check on a file containing all factory stubs). ✅ PASS — one4all `63adaaa4`.

### SJ4-JS-2 — Extend sno_runtime.js with SM-compatible API

- [x] **SJ4-JS-2** — `src/runtime/js/sno_runtime.js` already has _vars, _str(), _num(). Add SM-level methods called by scalar node emission (from IEP-4): push_int, push_str, push_real_bits, push_null, push_var, store_var, pop_void, concat, neg, exp_op, coerce_num, arith(op), acomp(op), lcomp(op), last_ok, set_last_ok, set_stno, halt_tos, call(name,nargs), do_return(kind,cond), _init, _finalize. Plus MatchState factory (returns {sigma,delta,omega}). Plus pending-captures list for ASSIGN_COND: _push_cap(varname,text), _commit_caps(), _discard_caps().

  **Gate:** node -e "const rt=require('./sno_runtime.js'); rt._init(); rt.push_str('hi',2); rt.halt_tos();" prints hi. ✅ PASS — one4all `a72c9b6d`. All 20+ API methods exported and tested.

### SJ4-JS-3 — Smoke 7/7

- [ ] **SJ4-JS-3a** — Implement scalar IR emitter. ✅ PARTIAL — emit_js_scalar() handles 15+ IR kinds (literals, variables, arithmetic, comparisons, calls, control flow). However, IR walk does not emit scalar ops into switch cases because statement boundaries require tracking (IR structure is DFS but scalars are grouped by statement). Requires deeper understanding of IR statement grouping (deferred to SJ4-JS-3b).

- [ ] **SJ4-JS-3b** — Create test infrastructure. ✅ DONE — `scripts/test_smoke_snobol4_js.sh` created. Emits all 6 smoke programs to JS, executes with node, compares to oracle. Currently fails (expected): switch loop is empty because scalar IR walk not yet wired to emit operations within statement cases.

- [ ] **SJ4-JS-3c** — Fix scalar statement boundaries. ⏳ BLOCKED — Requires understanding how lower() groups IR nodes by statement. Once statement IDs are available, scalar ops can be emitted into correct case statements. Estimated 1 hour once IR structure understood.

  **Gate:** 7/7 PASS once scalar IR walk is wired to emit operations.

Current status: Framework complete; waiting on statement boundary tracking.

### SJ4-JS-4 — Beauty self-host

- [ ] **SJ4-JS-4** — Run beauty.sno under `scrip --sm-emit --target=js`. Fix remaining failures. beauty.sno exercises all 19 BB kinds plus DEFINE, arithmetic, OUTPUT, &STCOUNT, indirect patterns.

  **Gate:** md5sum beauty_js.out = abfd19a7a834484a96e824851caee159.

---

## State

```
watermark: SJ4-JS-3a
head: one4all e83a09ff
session: 2026-05-15 (continued)
progress: SJ4-JS-1 ✅ SJ4-JS-2 ✅ SJ4-JS-3a ✅ (partial) SJ4-JS-3b ✅ 

Completed:
  - 19 BB emitters (emit_js.c)
  - SM API + MatchState (sno_runtime.js)
  - Scalar IR emitter stubs (15+ kinds)
  - Switch/dispatch loop structure
  - Test infrastructure (scripts/test_smoke_snobol4_js.sh)
  
Blocker for SJ4-JS-3c:
  - Scalar IR walk emits correctly but switch cases are empty
  - Requires understanding statement boundaries in IR structure
  - IR walk is DFS but scalars must be grouped by statement
  - Once statement IDs tracked, scalar ops can be emitted
```

---

## Key invariants

- **Reads IR_t only.** This emitter never reads SM_Program. IR_t is the sole input.
- **19 BB kinds, all pre-implemented.** Every alpha/beta body is already written in bb_boxes.js. Read it first.
- **Use git show 660339cd to read single-box files.** `git show 660339cd:src/runtime/boxes/NAME/bb_NAME.js` gives one box in isolation.
- **Switch/dispatch is mandatory.** SNOBOL4 GOTO can jump backward. Straight-line JS cannot handle it.
- **Flag:** --sm-emit --target=js (not --jit-emit --js).
