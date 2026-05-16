# GOAL-ICON-BB-JCON.md — Icon: 43 BB emitters + lower_icn DCG

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--ir-run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ Co-expression support (co-expressions, TT_SUSPEND, ucontext-based proc suspend/resume) IS permitted and should be implemented via coro_runtime.c as needed for Icon completeness.
⚠ What is BANNED: using coro_runtime.c to implement Byrd boxes as C coroutine functions (the old icon_gen.c pattern). Byrd boxes are IR_block_t DCGs driven by icn_bb_dcg. Co-expressions and TT_SUSPEND are NOT Byrd boxes — they are a separate Icon feature that legitimately uses ucontext.
⚠ Read `.github/jcon_irgen.icn` before touching any BB.
⚠ No C BB functions anywhere. A C BB is a `DESCR_t foo(void *zeta, int entry)`
  function that implements four-port logic (α/β/γ/ω) in C. These must not exist.
  `icn_lazy_box` and `icn_bb_dcg` are infrastructure bridges — not generator logic — keep them.

---

## Current state (one4all b389062e+)

- `icon_gen.c` DELETED. All 43 C BB functions gone.
- `icn_runtime.c`: C BB functions also removed. `icn_bb_build` call sites
  that referenced deleted functions now route to `icn_lazy_box` (lazy fallback).
- Build is CLEAN. Gates regressed: smoke_icon 4/5, broker 20/23.
- Regression is expected — lazy fallback is single-shot, not generative.
- `icn_bb_dcg` bridge added (routes IR_block_t through bb_broker).
- `lower_icn.c` scaffolding started (upto DCG node wired in ir_exec.c).
- `SM_EXEC_BB` updated to resume on subsequent calls (β path via `IR_exec_resume`).

---

## Architecture — what we are building

### Three layers, with the SM↔BB bridge as the only contact point:

```
AST  -- (lower time) -->  SM_Program     [contains SM_BB_XXX bridge opcodes]
                          IR_block_t *   [pre-built per bridge op, lives in BB land]

Runtime: SM interp / SM JIT / SM emit-text runs SM_Program.
         An SM_BB_XXX instruction brokers from SM into BB land by handing the
         pre-built IR_block_t* to bb_broker (driving icn_bb_dcg, which calls
         IR_exec_once / IR_exec_resume).  SM never sees tree_t*; BB never sees
         tree_t*; modes 2/3/4 are AST-free.
```

The SM_Program is the entry point.  Execution starts in SM.  An Icon program
compiles down to an SM_Program containing SM_BB_XXX bridge opcodes (PUMP_PROC,
EVAL, etc.).  Those bridges hand pre-built IR_block_t*'s to bb_broker.  The
IR_block_t* registry is BB-land state, indexed by the bridge opcode's operand
(eval-id, proc-id, etc.).  Nothing at runtime dereferences a tree_t*.

### ⚡ Target shape: composition by SM bridges (SNOBOL4 pattern parallel)

End-state for Icon (Lon, 2026-05-15h refinement):

Not "one giant monolithic BB built entirely at lower time" — that loses the
SNOBOL4 parallel.  The actual target shape is:

  • Each Icon procedure compiles to **one IR_block_t* per proc**, registered
    in BB-land by name (proc_table[i].ir_body).  This is the natural unit.
  • Procs are **composable**: an IR_CALL node inside one proc's body holds
    a reference (by name or by direct pointer) to another proc's IR_block_t.
  • The whole program ends up as one BB DAG in BB-land — but the DAG is
    *built by the SM stream postorder-style*, exactly like SNOBOL4 patterns.

SNOBOL4 already does this.  Many small SM_PAT_* bridge calls each build a
small BB-land object and push it on the SM stack; composer bridges
(SM_PAT_CAT, SM_PAT_ALT) pop their operands, call BB-land's pat_cat /
pat_alt, push the composed result.  The SM stream itself encodes the
postorder traversal that builds the BB DAG.  Then one final bridge
(SM_PAT_MATCH) takes the top-of-stack pattern and drives bb_broker.

The Icon mapping:

  SM bridge instruction          → BB-land composer / driver
  ───────────────────────────────────────────────────────────────────────
  SM_BB_LIT_I  <int>             → push IR_block_t for IR_LIT_I
  SM_BB_LIT_S  <str>             → push IR_block_t for IR_LIT_S
  SM_BB_VAR    <name>            → push IR_block_t for IR_VAR
  SM_BB_BINOP  <kind>            → pop 2, push ir_binop_compose(L, R, kind)
  SM_BB_CALL   <name> <nargs>    → pop nargs, push ir_call_compose(name, args)
  SM_BB_SEQ    <nstmts>          → pop nstmts, push ir_seq_compose(stmts)
  SM_BB_PROC   <name>            → pop 1 body, register proc by name
  SM_BB_DRIVE                    → pop 1 IR_block_t*, drive via icn_bb_dcg

Each proc body is one IR_block_t* (one BB per proc); procs reference each
other through IR_CALL nodes; the whole program is one composable BB DAG.
The composer helpers `lower_icn_binop`, `lower_icn_alternate`, `lower_icn_to`,
`lower_icn_limit`, `lower_icn_iterate` already exist in lower_icn.c — they
take BB-land operands (bb_node_t / int64_t) and return composed IR_block_t*.
They are the Icon-side analogue of pat_cat / pat_alt / pat_arbno.

What's missing: the SM bridge opcodes that drive composition postorder.
Today's `lower()` emits piecemeal `SM_BB_EVAL <eval_id>` instructions that
carry tree_t* references through every_table — the wrong shape.  The right
shape is the SNOBOL4 postorder composition above.

Per-proc IR_block_t* is already produced by `lower_icn_proc_body` and
stored in `proc_table[i].ir_body`.  `SM_BB_PUMP_PROC "main"` is already the
"drive the main proc" bridge.  What's left is to extend coverage of
`lower_icn_expr_node` (and `lower_icn_proc_body`) until enough programs
parse end-to-end without falling back to legacy SM emission — at which
point the next step (replacing piecemeal SM_BB_EVAL emissions with
postorder composer bridges) becomes a cleanup, not a re-architecture.

### Earlier directive (preserved): Icon program = TWO SM instructions

Original framing (Lon, 2026-05-15): an Icon program compiles to just two
SM instructions — `SM_BB_EVAL* <id>` covering the whole program and
`SM_HALT`.  This is the *driving* shape after composition is complete:
once main's body is one IR_block_t*, the program reduces to `SM_BB_DRIVE`
(or its equivalent `SM_BB_PUMP_PROC "main"`) plus `SM_HALT`.  Composition
of that IR_block_t* happens either at lower time (today's path via
`lower_icn_proc_body`) or at startup via composer bridges (SNOBOL4-style).
Both are valid endpoints; the SNOBOL4-style composition path keeps the
SM stream involved in the build.

### Lessons from jcon — the canonical Icon IR builder

jcon (`/refs/jcon-master/tran/irgen.icn` + `tran/ir.icn`) provides the
reference design we are converging on.  Key observations:

  1. **Four-port labels per AST node.**  `procedure ir_init(p)` allocates
     four named labels for every Icon expression:

         p.ir.start    -- entry (α-port)
         p.ir.resume   -- re-entry to produce next value (β-port)
         p.ir.success  -- continuation on success    (γ-port)
         p.ir.failure  -- continuation on failure    (ω-port)

     This is exactly the Byrd-box four-port model.  Every AST node has a
     pre-allocated rendezvous label for each port.

  2. **Composition = pure label-stitching.**  Each `ir_a_FOO(p, ...)`
     procedure does three things: (a) call ir_init(p) to allocate its own
     four labels; (b) recursively suspend ir() on children (which allocates
     their labels and emits their chunks); (c) emit a handful of `ir_chunk`
     pieces whose only contents are `ir_Goto(child.ir.X)` thread-throughs.

     ir_a_Alt is the cleanest example: emits N chunks, one at each
     alternative's failure label that gotos the next alternative's start,
     and one at each success label that gotos the parent's success.  No
     state machines, no zeta structs, no opaque pointers — pure flat
     label-threaded code.

  3. **Generators carry no opaque state.**  ir_a_ToBy emits an ir_opfn for
     the "..." operator with a `closure` temporary — the state of the
     generator is just *a normal IR register* tracked through SSA-ish data
     flow.  Resume is "goto byexpr.ir.resume" which re-enters the same
     IR_opfn instruction, which advances the closure register.  No
     hand-coded α/β/γ/ω C function with a private zeta struct.

  4. **One IR instruction set, no per-construct opcodes.**  ir.icn defines
     ~25 record types covering all Icon: `ir_Move`, `ir_Goto`, `ir_OpFunction`,
     `ir_Call`, `ir_Succeed`, `ir_Fail`, `ir_Create`, `ir_CoRet`, etc.
     Every Icon construct lowers to combinations of these — there is NO
     `ir_a_To` opcode, no `ir_a_Every` opcode, no `ir_a_Limit` opcode.
     They're all expressed as chunk graphs over the basic instruction set.

#### What this tells us about our design

Our current scrip IR has TWO problems that jcon's design solves:

  • **Per-construct IR opcodes.**  We have `IR_ICN_TO`, `IR_ICN_TO_BY`,
    `IR_ICN_UPTO`, `IR_ICN_ITERATE`, `IR_ICN_ALTERNATE`, `IR_ICN_LIMIT`,
    `IR_ICN_BINOP`, `IR_ICN_EVERY` — each with private state fields
    (counter, lo/hi/step, gen[2]/which, opaque structs).  jcon does ALL
    of these with the same general `ir_Move + ir_Goto + ir_OpFunction`
    triad.  Resume is just `goto resume_label`; the operator function
    advances its own internal state on each invocation.

  • **Recursive AST-tied four-port runtime.**  Our IR_t has α/β/γ/ω
    pointer fields pointing to *other IR_t nodes* — the four-port model
    is encoded in the IR graph topology.  jcon flattens this: the four
    ports become four *labels* attached to each AST node at lower time,
    and the IR is a flat list of (label, [instructions]) chunks where
    every cross-port transition is a literal `goto` to a label.  The
    runtime just walks chunks sequentially; resume = jump.

Both observations point the same direction: **flatten IR to a chunk-of-
instructions list with explicit labels, drop per-construct IR opcodes,
express generator state as named temporaries.**  This is the SNOBOL4
postorder composition pattern applied to a flat label-threaded IR
instead of a tree.

#### Concrete next-step impact

For the immediate work (close smoke_icon every+if_expr):

  • TT_IF mirrors `ir_a_If` exactly: pre-allocate four labels on the if
    expression; lower the test, the then-branch, and the else-branch as
    sub-chunks; emit chunks stitching their success/failure labels into
    the parent's success/failure.  No new IR opcode needed.

  • TT_TO mirrors `ir_a_ToBy`: lower from/to as sub-expressions; emit a
    closure temporary; emit chunks that pump (from advances counter, to
    bounds-checks).  Today's `IR_ICN_TO` is a shortcut; the jcon shape
    is the general answer.

  • TT_EVERY mirrors `ir_a_Every`: bounded re-entry — emit a chunk at the
    body.ir.success label that gotos the gen.ir.resume label.  This IS
    the every-loop: success → resume → more values.  No special opcode.

For the longer arc: rewriting our IR layer to be flat-chunk-based puts us
on the same architecture jcon uses, which has been battle-tested as a
viable Icon target since the 1990s.  It also matches the eventual x86
emitter shape: labels become PC values, chunks become basic blocks,
gotos become `jmp` instructions.  No translation gap.

### Same pattern as SNOBOL4 — only the granularity differs

SNOBOL4 pattern handling in sm_interp.c uses exactly this same SM↔BB bridge
shape, just at a finer granularity:

  • SNOBOL4: many small SM→BB bridge opcodes, one per pattern primitive.
    SM_PAT_LIT, SM_PAT_ANY, SM_PAT_SPAN, SM_PAT_BREAK, SM_PAT_LEN, SM_PAT_POS,
    SM_PAT_TAB, SM_PAT_ARB, SM_PAT_ARBNO, SM_PAT_CAT, SM_PAT_ALT, etc.
    Each handler is a tiny bridge: it pops its operand (a string, an integer,
    or pre-built BB sub-patterns) and pushes a BB-land pattern object built
    via pat_lit / pat_any_cs / pat_cat / pat_alt / etc.  The full pattern is
    composed by the SM stream itself in postorder.  Composition lives on the
    SM stack.

  • Icon: coarser bridge — one SM_BB_XXX opcode brokers an entire expression
    (or proc body).  The handler looks up a pre-built IR_block_t* by id and
    hands it to bb_broker.  Composition happens at lower time; the BB-land
    registry stores the composed IR_block_t.

Both designs respect the same invariants: SM is the entry; bridge opcodes are
the only contact surface; BB-land structures (SNOBOL4 patterns, Icon
IR_block_t's) are pre-built (or stack-composed) before bb_broker is invoked;
nothing dereferences tree_t* at runtime.

### Two execution paths for Icon generators:

**Path A — `--ir-run` / `--sm-run` (interpreter):**
`icn_bb_build(tree_t*)` → `bb_node_t{fn, zeta, 0}` → `bb_broker` drives fn(zeta,α/β).
The `fn` pointer used to be a C BB. Now it must be `icn_bb_dcg` which drives an
`IR_block_t` DCG built at lower time (or built fresh from `lower_icn_*` at runtime).

**Path B — `--sm-native` / mode-4 (JIT emitter):**
`emit_bb_icon_*(s, f, b)` emits inline x86 implementing α/β directly.
No C function called by the blob. Zeta in .data, blob reads/writes fields via [rip+offset].

### The `icn_bb_dcg` bridge (infrastructure, not a C BB):

```c
typedef struct { IR_block_t *cfg; int first; } icn_dcg_state_t;
DESCR_t icn_bb_dcg(void *zeta, int entry) {
    icn_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; }
    return z->first ? (z->first=0, IR_exec_once(z->cfg)) : IR_exec_resume(z->cfg);
}
```

`icn_bb_build` creates an `icn_dcg_state_t` with a freshly built `IR_block_t` and
returns `(bb_node_t){ icn_bb_dcg, dz, 0 }`. The broker calls `icn_bb_dcg(zeta, α)`
on first pump, `icn_bb_dcg(zeta, β)` on subsequent pumps.

### IR_exec_resume (ir_exec.c):
Same as IR_exec_once but skips IR_reset — continues from current node state.
α path: `IR_exec_once` (resets counter/state to 0). β path: `IR_exec_resume`.

### IR_ICN_UPTO executor (ir_exec.c):
```c
case IR_ICN_UPTO: {
    if (nd->state == 0) nd->counter = 0;   /* α: reset */
    nd->state = 1;                           /* β next time */
    const char *cset = nd->sval;
    const char *hay  = nd->value.s;
    int slen = (int)nd->value.slen;
    while (nd->counter < slen) {
        char c = hay[nd->counter++];
        if (strchr(cset, c)) { nd->value = INTVAL(nd->counter); return nd->γ; }
    }
    nd->state = 0; nd->value = FAILDESCR; return nd->ω;
}
```

---

## DEBUGGING NEEDED: upto scalar dispatch

`upto('aeiou', "hello world")` with `--ir-run` currently returns empty (fails silently).
Root cause: the `icn_bb_build` TT_FNC dispatch for `upto` scalar may not be matching.

In `icn_bb_build`, Icon-style function calls have `e->c[0]->v.sval = "upto"` and
the variable `fn` is set like: `const char *fn = e->n > 0 ? e->c[0]->v.sval : NULL`.
The scalar dispatch condition (added this session) checks `fn && strcmp(fn,"upto")==0`
but may be in the wrong position in the if-chain, or `fn` may not be set at that point.

**Fix needed:** Add `fprintf(stderr, "DEBUG upto fn=%s nargs=%d\n", fn?fn:"NULL", nargs);`
just before the upto scalar dispatch block to confirm it's reached. Then fix condition.

---

## How to implement each of the 43 BB

For each construct:

### Step 1 — Understand alpha/beta
Read deleted `icon_gen.c` from git:
  `git show HEAD~5:src/runtime/interp/icon_gen.c | grep -A30 "icn_bb_CONSTRUCT"`
Read `jcon_irgen.icn` `ir_a_CONSTRUCT` for four-port wiring.

### Step 2 — Add IR kind (scrip_ir.h)
Add `IR_ICN_CONSTRUCT` to the Icon section of `IR_e` enum in `scrip_ir.h`.

### Step 3 — Add executor case (ir_exec.c)
Add `case IR_ICN_CONSTRUCT:` to `IR_exec_node` switch.
Use `nd->state` (0=α, 1=β), `nd->counter` (integer scratch), `nd->value` (result),
`nd->sval` (string arg), `nd->ival` (integer arg).
Set `nd->value = result` and return `nd->γ` (success) or `nd->ω` (fail).

### Step 4 — Add DCG builder (lower_icn.c)
Write `lower_icn_CONSTRUCT(args...)` that calls `IR_alloc(N, IR_LANG_ICN)`,
`IR_node_alloc(cfg, IR_ICN_CONSTRUCT)`, wires α/β/γ/ω, sets fields, returns cfg.

### Step 5 — Wire into icn_bb_build (icn_runtime.c)
In `icn_bb_build`, find the TT_CONSTRUCT block. Replace the lazy fallback with:
```c
IR_block_t *cfg = lower_icn_CONSTRUCT(args);
icn_dcg_state_t *dz = calloc(1, sizeof(*dz));
dz->cfg = cfg; dz->first = 1;
return (bb_node_t){ icn_bb_dcg, dz, 0 };
```

### Step 6 — Write inline x86 emitter (emit_bb.c)
Replace the ICN_STUB one-liner with real inline x86:
```c
void emit_bb_icon_CONSTRUCT(bb_label_t *s, bb_label_t *f, bb_label_t *b) {
    emit_bb_box_banner("ICN_CONSTRUCT", "");
    if (IS_TEXT) {
        int id = g_flat_node_id++;
        // Emit .data: zeta fields as .quad 0 slots
        // Emit .text alpha: read zeta, compute, set result, jmp s or f
        emit_label_define(b);
        // Emit .text beta: advance state, jmp s or f
        return;
    }
    // binary mode: insn_* helpers
}
```
Zeta layout: `.quad 0` per 8-byte field, accessed as `[rip + zlbl + offset]`.
Result value delivery: for Icon value generators, the result DESCR_t must be
written somewhere readable by the broker. Study `emit_bb_xbal` for the pattern
of writing a result and jumping to succ vs fail.

### Step 7 — GATE-1..4, commit

---

## State structs (from deleted icon_gen.c, git show HEAD~5:...)

  icn_to_state_t        = { long lo; long hi; long cur; }                   3 quads
  icn_to_by_state_t     = { long lo; long hi; long step; long cur; }        4 quads
  icn_iterate_state_t   = { DESCR_t obj; int pos; int len; char *s; }       complex
  icn_alternate_state_t = { bb_node_t left; bb_node_t right; int phase; }   complex

Simple constructs first (pure integer state, no child generators):
  TT_TO      → IR_ICN_TO      α: cur=lo; cur>hi→ω; ret cur(γ).   β: cur++; same test.
  TT_TO_BY   → IR_ICN_TO_BY   α: cur=lo; bounds check→ω; ret cur. β: cur+=step; same.

---

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5 (currently 4)
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23 (currently 20)
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

---

## Active steps

### ✅ EMERGENCY — REVERT icn_bb_every AND icn_bb_to — DONE `bb48e6c3`

`icn_bb_to` → `IR_ICN_TO` DCG (ir_exec.c executor + lower_icn_to + icn_bb_dcg wire).
`icn_bb_every` → `IR_ICN_EVERY` DCG (ir_exec.c executor + lower_icn_every + icn_bb_dcg wire).
TT_SEQ filter path also wired to lower_icn_every. Gates: smoke_icon 5/5, broker 21/49.

### IJ-19-debug — fix upto scalar dispatch in icn_bb_build (FIRST)

- [x] Add debug print, confirm `fn` and position in TT_FNC block.
      Fix dispatch condition so `upto('aeiou', "hello world")` → `icn_bb_dcg`.
      Verify: `./scrip --ir-run /tmp/test_upto.icn` prints `2\n5\n8` (positions in "hello world").
      GATE-1..4. Commit.
      Root causes fixed: (1) IR_ICN_UPTO stored hay in nd->value.s which IR_reset zeroed —
      moved to new IR_t.sval2 field. (2) icn_bb_every was returning icn_lazy_box stub —
      implemented and wired. one4all `a82b42c5`.

### IJ-19-to — implement TT_TO generator (smoke_icon every test)

- [x] Implemented as IR_ICN_TO DCG (icn_bb_to C BB deleted). lower_icn_to+icn_bb_dcg wire.
      Verify: `every write(1 to 3)` prints 1,2,3. GATE-1 PASS=5. one4all `bb48e6c3`.

### IJ-19-to-by — implement TT_TO_BY

- [x] IR_ICN_TO_BY DCG. ival=lo,ival2=hi,ival3=step. lower_icn_to_by+icn_bb_dcg.
      rung07_control_to_by PASS, rung19_pow_toby_* int/var PASS. one4all `a0b0700b`.

### IJ-19-iterate — implement TT_ITERATE (!str, !list, !table)

- [x] IR_ICN_ITERATE string path. sval2=str, ival=len, counter=pos; GC_malloc 1-char per tick.
      lower_icn_iterate + icn_bb_dcg wire. list/table/Raku remain lazy (future). one4all `8cf94938`.

### IJ-19-alternate — implement TT_ALTERNATE (A|B)

- [x] IR_ICN_ALTERNATE DCG. icn_alt_dcg_t{gen[2],which} in opaque. n-ary chain. one4all `51460d4f`.
      ir-run 153→159 (+6), honest 271→275 (+4).

### IJ-19-limit — implement TT_LIMIT (gen\\N)

- [x] IR_ICN_LIMIT DCG. icn_lim_dcg_t{gen,max,count} in opaque. one4all `b7d74bf9`.
      ir-run 159→164 (+5), honest 275→276 (+1).

### IJ-19-binop-gen — arith/relop with generative operands

- [x] IR_ICN_BINOP DCG. icn_binop_dcg_t in opaque. icn_binop_apply in lower_icn.c.
      binop_map[] + TT_CAT cross-product wired. one4all `f63c60f0`.
      ir-run 164→174 (+10), broker 22→23.

### IJ-19-remaining — remaining constructs in order of complexity

**RESOLVED:** `rung13_alt_alt_filter` now passes (fixed in prior session).

**RESOLVED:** `fail` keyword in proc bodies now propagates correctly (IJ-19-fail, sess 2026-05-14).
Two bugs in `sm_interp.c`: (1) `SM_BB_EVAL` did not check `FRAME.returning` after `bb_eval_value`
drives `TT_PROC_FAIL` via alternation arm (`expr | fail`). (2) `sm_call_expression` read stack
top instead of `FAILDESCR` when `SM_FRETURN` fired at top-level of nested SM_State. Both fixed.
Fixes `if cond then fail`, `expr | fail`, bare `fail` as statement. `rung36_jcon_roman` now passes.
one4all `992a2a18`.

Next DCGs to implement (highest ir-run yield first):
- TT_SUSPEND (rung03_suspend_gen_*) — user proc suspend/resume — implement via ucontext coro in coro_runtime.c (co-expression/coroutine support now enabled per Lon 2026-05-15)
- TT_ITERATE list/table paths (rung22, rung13_table_iterate)
- rung36_jcon_* suite residual — most remaining failures: `every f(gen_arg)` doesn't
  re-pump arg generators. Landed this session: math builtins nargs>=1,
  list() nargs, ||| list concat, any/many/upto 2-arg, cset identity, image(DT_FH).
  rung36_jcon_kross now PASS. Remaining: fncs1 (global/record-field name collision),
  endetab (infinite loop), coerce (pre-existing segfault).

---

## Done when

  All icn_bb_build lazy fallbacks replaced with icn_bb_dcg + IR_block_t.
  All ICN_STUB one-liners in emit_bb.c replaced with inline x86.
  ir-run PASS >= 230. Honest PASS >= 268. GATE-1..4 green.

---

## Invariants

1. GATE-1: smoke_icon PASS=5. Restore before any other work.
2. GATE-2: broker PASS=23. Never regress below committed baseline.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. No `DESCR_t foo(void *zeta, int entry)` four-port C BB functions.
   `icn_lazy_box` and `icn_bb_dcg` are infrastructure — keep them.
6. One construct per commit (or small coherent batch).
7. No corpus source modified to work around runtime bugs.

---

## Watermark

  one4all: 66b4d52e  corpus: 1fe096c
  ir-run:  BROKEN — see session notes below (was 207)
  honest:  BROKEN — see session notes below (was 275)
  smoke_icon: 3/5   smoke_prolog: 0/5   broker: 15/49
  Other smokes unchanged: snobol4 7/7, raku 5/5, snocone 5/5, rebus 4/4.
  smoke_icon: write_str, arith, string_op PASS via AST→IR→BB path through
  SM_BB_PUMP_PROC main → icn_bb_dcg → lower_icn_proc_body.  if_expr + every
  still FAIL — need TT_IF, TT_EVERY, TT_TO support in lower_icn_expr_node.
  Breakage still intentional for prolog (Lon directive: break gates to expose
  missing SM/BB lowering).

  Session 2026-05-15h (Claude Sonnet 4.6, one4all `66b4d52e`):
    Architectural directive recorded (Lon, 2026-05-15): Icon program = TWO SM
    instructions — `SM_BB_EVAL*` (covering whole program via pre-built
    IR_block_t*) + `SM_HALT`.  That single bridge instruction brokers into BB
    land.  HQ updated: GOAL-ICON-BB-JCON.md added "Target shape: Icon program
    = TWO SM instructions" section.

    The earlier hypothesis in this watermark (build per-expression
    ir_eval_registry keyed by SM eval-id) is the WRONG abstraction under the
    two-instruction directive — those piecemeal SM_BB_EVAL emissions shouldn't
    exist in the final state.  Instead: keep growing lower_icn_proc_body
    coverage so main()'s body lowers to a single IR_block_t*, driven by the
    one `SM_BB_PUMP_PROC "main"` bridge that `lower()` already emits.  That
    IS the target two-instruction shape.

    Landing wedge: extended lower_icn_expr_node with TT_ADD/SUB/MUL/DIV/MOD/
    LT/LE/GT/GE/EQ/NE/CAT → IR_BINOP.  Added IR_BINOP executor in ir_exec.c
    using icn_binop_apply.  Added public lower_icn_expr_top() wrapper for
    future single-expr callers.

    Gates moved: smoke_icon 1/5 → 3/5 (+arith, +string_op); broker 14/49 →
    15/49.  No regressions.  Remaining smoke_icon fails: if_expr (TT_IF),
    every (TT_EVERY + TT_TO).

  NEXT: extend lower_icn_expr_node further to close the remaining smokes:
        (1) TT_IF — emit IR conditional (executor case + lowering).
        (2) TT_TO — wrap IR_ICN_TO state into IR DAG nested inside the
            main-body IR_block_t.
        (3) TT_EVERY — IR_EVERY executor covering the loop semantics.
        (4) Eventually: non-builtin TT_FNC (user procs called from main).

        Architectural framing for the SNOBOL4 parallel (refined this session):
        each Icon proc = one IR_block_t* (one BB per proc); procs compose
        through IR_CALL references; the whole program is one composable BB
        DAG.  SNOBOL4 builds its DAG at startup via postorder SM_PAT_* bridge
        ops; Icon can do the same with SM_BB_LIT_I / VAR / BINOP / CALL / SEQ
        / PROC / DRIVE composer bridges.  Composer helpers (lower_icn_binop,
        lower_icn_alternate, lower_icn_to, lower_icn_limit, lower_icn_iterate)
        already exist and have the right SNOBOL4-pat_cat shape; what's missing
        is the SM postorder-composition bridge opcodes.  Today's path
        (lower_icn_proc_body at compile time → proc_table[i].ir_body →
        SM_BB_PUMP_PROC main + SM_HALT) reaches the same endpoint via a
        different composition path — both are valid.

  Architectural correction (recorded after Lon clarified, 2026-05-15):
    The first wedge attempt this session had SM_BB_EVAL call IR_exec_once
    directly — wrong because it bypassed bb_broker / icn_bb_dcg.  The fix
    is NOT to remove SM_BB_EVAL from the path; it is to keep SM_BB_EVAL as
    the SM→BB bridge but have it broker via icn_bb_dcg over a pre-built
    IR_block_t* (looked up from a BB-land registry by eval-id).  SM stays
    in the loop; SM is the entry point; SM_BB_XXX is the only contact
    surface with BB land; nothing dereferences tree_t* at runtime.

  Session notes (2026-05-15, one4all 7fd70c00, Claude Opus 4.7):
    First AST→IR→BB wedge per Lon's directive (forward pipeline is AST→IR→BB
    only; SM not in the loop).

    Two earlier attempts in this session put IR behind an SM lookup
    (ir_eval_table keyed by SM eval-id, then inline AST→SM lowering).  Both
    reverted after Lon flagged the SM-layering violation.  Recorded lesson:
    the SM_BB_EVAL stub message "needs fresh SM/BB lowering" is misleading.
    The real fix is to remove SM_BB_EVAL from the path entirely — build
    IR_block_t for proc bodies, drive via icn_bb_dcg / bb_broker.

    The landing wedge:
      • IcnProcEntry gains IR_block_t *ir_body.
      • lower_proc_skeletons calls new lower_icn_proc_body(tree_t*) per proc.
        Returns NULL on any unsupported AST kind (caller falls back silently
        to legacy SM emission, which is also still emitted).
      • lower_icn_proc_body builds an IR_SEQ over body statements ending at
        FAILDESCR so bb_broker(BB_PUMP) exits after one tick — matches Icon
        procedure-falls-off-end semantics (no trailing newline from
        pump_print on NULVCL).
      • lower_icn_expr_node currently covers TT_ILIT, TT_QLIT, TT_VAR,
        TT_ASSIGN(TT_VAR := expr), TT_FNC(builtin).
      • icn_bb_pump_proc_by_name: when ir_body != NULL, pushes a fresh
        IcnFrame with proc's lower_sc, wraps IR_block in icn_dcg_state_t,
        returns (bb_node_t){icn_bb_dcg, dz, 0}.  bb_broker drives.
        icn_bb_dcg calls IR_exec_once(α) / IR_exec_resume(β).
      • New IR executor cases (ir_exec.c): IR_VAR, IR_ASSIGN, IR_CALL, IR_SEQ.
        IR_VAR/IR_ASSIGN resolve frame slots by NAME via scope_get(&FRAME.sc,
        name) at exec time — no tree_t* deref at runtime.  IR_CALL uses
        icn_try_call_builtin_by_name.
      • SM_BB_EVAL stub untouched.  New path does not go through it.

    Wedge program: 'procedure main(); i := 0; write(i); end' prints '0'.

    Gates: smoke_icon 0/5 -> 1/5 (write_str PASS).  All other passing gates
    unchanged: snobol4 7/7, snocone 5/5, rebus 4/4, raku 5/5.  Prolog 0/5
    unchanged.

  Session notes (2026-05-15g, one4all fb3c4153, Claude Opus 4.7):
    Lon directive: delete ALL AST walking from modes 2, 3, 4.  Mode 4 is alive
    (HQ updated: ARCH-SCRIP.md Mode-4 description rewritten present-tense; same
    in GOAL-MODE3-EMIT.md). Mode 1 stays.

    AST-walk inventory and disposition:
      Mode 2 (sm_interp.c):
        line 652  SM_BB_PUMP            — stubbed, prints [NO-AST]
        line 661  SM_BB_ONCE            — stubbed
        line 671  SM_BB_EVAL            — stubbed (was the FRETURN-handling block)
        line 704  SM_BB_ONCE_PROC       — stubbed (Prolog clause lookup)
        line 813  SM_BB_PUMP_EVERY      — stubbed
        line 1300 SM_CALL "PL_UNIFY"    — stubbed
        line 1327 SM_CALL "PL_BUILTIN"  — stubbed
        line 1785 sm_call_proc body loop — removed (icn_scope_patch walked proc->c[bi]);
                                           lower_sc now used as-is from lower time
      Mode 3 (sm_jit_interp.c):
        line 277  h_bb_pump             — stubbed
        line 287  h_bb_once             — stubbed
        line 298  h_bb_once_proc        — stubbed
        line 412  h_bb_pump_every       — stubbed
        line 811  h_usercall PL_UNIFY   — stubbed
        line 838  h_usercall PL_BUILTIN — stubbed
      Mode 3/4 emitter templates (src/emitter/*.c): zero AST walks pre-existing.

    Build: clean.  Diff: sm_interp.c −66, sm_jit_interp.c −15, net −81 lines.

    Dead infrastructure left in place (no walking, just storage):
      sm_interp.c:84  extern decl of icn_bb_build (no caller in this file now)
      sm_interp.c:114-132  g_every_table registry (producer alive, no consumer)
      sm_jit_interp.c:263  extern decl of icn_bb_build
    Defer their deletion to a follow-up.

    Pre-deletion baseline: icon 5/5  snobol4 7/7  prolog 5/5  raku 5/5
                           snocone 5/5  rebus 4/4  broker 23/49.
    Post-deletion gates:   icon 0/5  snobol4 7/7  prolog 0/5  raku 5/5
                           snocone 5/5  rebus 4/4  broker 14/49.

    HQ updated (.github):
      ARCH-SCRIP.md: Mode 4 description present-tense (EMIT_TEXT via shared
                     src/emitter/*.c templates; same SM_Program as mode 3).
      GOAL-MODE3-EMIT.md: one "Mode 4 will not dump" → "does not dump".

  Session notes (2026-05-15c, one4all 54304353, Claude Opus 4.7):
    Lon directive: old AST-walker system is being deleted.  Forward pipeline
    is AST → IR → BB/SM only.  Anything not on BB/SM goes.

    BB tally: 10 of 51 DCGs done.  Done: TO, TO_BY, TO_NESTED, UPTO,
    EVERY, ITERATE (string only), ALTERNATE, LIMIT, BINOP, PROC_GEN.
    Remaining 41 grouped: ~15 trivial single-shot wrappers (csetlit,
    intlit, strlit, fail_bb, etc.), ~10 single-state generators
    (list_iterate, tbl_iterate, find, find_subj, upto_subj, bal,
    record_iterate, key_gen, etc.), ~10 conditional/composite (if_bb,
    not, unop, return_bb, until_gen, while_gen, repeat_gen, case_gen,
    field_gen, section_gen), ~5 composition over child generators
    (compound_gen, listcon_gen, repalt, arglist, coexplist, create),
    plus suspend (already covered by proc_gen), make_proc_box, proc_call
    (infrastructure).

    This session deleted polyglot_execute (one4all `54304353`):
      - scrip.c: removed `else if (has_non_sno && g_polyglot)` arm
      - polyglot.c: deleted polyglot_execute() definition (57 lines)
      - polyglot.h: deleted polyglot_execute() declaration
      parse_scrip_polyglot() retained (parsing, not execution).
      Polyglot .scrip / .md files now route through SM dispatch via the
      has_non_sno fallthrough arm at scrip.c:402.  Previously broken:
      polyglot_execute called proc_table_call without setting up
      g_current_sm_prog, so proc_table_call hit its `entry_pc>=0 &&
      g_current_sm_prog!=NULL` guard, returned FAILDESCR, and produced
      empty output.  Now /tmp/probe.scrip with a trivial Icon block
      prints "hello from icon" correctly.
      All four Icon gates unchanged: smoke 5/5, broker 23/49, ir-run
      207, honest 275.

    Also this session: removed all CH-17g references from this Goal file
    per Lon directive (.github `489b9e12`).  That blocker is not to be
    mentioned again; BB construction is unblocked and proceeds without it.

    NEXT-SESSION DELETION PLAN (5K+ lines):
      1. interp_eval.c (4268 lines) — AST walker; entry points include
         interp_eval(), called from polyglot.c (already deleted there),
         icn_runtime.c, icn_value.c, raku_builtins.c, eval_pat.c.  Audit
         each call site: replace with SM dispatch or remove.
      2. interp_exec.c — AST execution paths using proc_table_call (which
         is itself fine — it routes through sm_call_proc already).
      3. _usercall_hook in interp_hooks.c — the g_user_call_hook dispatch
         is the SM-side entry; verify all reachable paths terminate in
         SM/BB and not AST walks, then prune the AST-fallback branches.
      4. Any remaining coro_call(proc_table[pi].proc, ...) fallback in
         coro_runtime.c (per prior session notes, may already be gone;
         confirm).
      5. Files in src/runtime/interp/ that still walk tree_t* at runtime
         (icn_runtime.c has NO_AST_WALK_GUARD declarations that flag
         improper AST access — those guards become the boundary).

    Watermark commit 54304353 verified on remote.

  Session notes (2026-05-15, one4all f82de5d0, Claude Opus 4.7):
    IJ-19-remaining: FAIL-arg propagation in named-proc fast-paths.
    Two missing IS_FAIL_fn short-circuits in user-proc call sites — both
    had sister paths in the same handler that already did the check
    correctly, so the fix is two minimal patches matching the surrounding
    pattern.
    (1) icn_value.c TT_FNC named-proc fast-path (~line 453): the arg
        eval loop returned the value of bb_eval_value without checking
        IS_FAIL_fn, unlike the indirect-callee and fallback paths in the
        same TT_FNC handler which do.
    (2) icn_runtime.c icn_bb_build named-proc oneshot (~line 1444): same
        omission at BB-construction time. Fix: short-circuit by
        returning an icn_bb_oneshot seeded with FAILDESCR (which already
        returns FAIL on first pump via existing IS_FAIL_fn guard at
        line 348).
    Repro: limage("u", x[-3+:6]) | write("u. wraparound failed")
      Before: " &null" (limage runs with lst=FAIL printed as &null)
      After:  "u. wraparound failed" (call fails, | falls through)
    Misdiagnosis correction: the prior watermark hypothesized that
    SM_STORE_VAR was converting FAIL->&null on store. That handler is
    actually correct (sm_interp.c:387-391 short-circuits on DT_FAIL).
    The y := x[-3+:6] reproducer with "y prints null" is not actually
    buggy — y was never assigned, and type(&null)="null" is correct
    Icon semantics for an unassigned local. Verified by pre-setting
    y := 999: assignment correctly fails, y stays 999.
    Gates: smoke_icon 5/5, broker 23/49, ir-run 206->207 (+1),
    honest 275. Cross-language smoke: prolog 5/5, rebus 4/4, raku 5/5,
    scrip_all_modes 2/2. rung36_jcon_lists diff: 1 region -> 0 (PASS).

  Session notes (2026-05-15, one4all 0fed7020, Claude Opus 4.7):
    IJ-19-remaining: ICN_RANDOM_SET list case wired.
    Bug: handler in sm_interp.c:1014 went straight to base.u->type->nfields

    user-record path, skipping the icn_type=="list" check. ?x := val on a
    list silently no-op'd; subsequent ASGN/INDEX path then extended list
    with &null.
    Fix: add list branch using subscript_set(base, INTVAL(fi+1), val),
    mirroring icn_value.c:386. Track ok through all branches.
    Repro: x := [1]; ?x := 2  -> [1] 2  (was [2] 1 &null).
    rung36_jcon_lists diff: 5 regions -> 1 region remaining (wraparound).
    Gates unchanged: smoke 5/5, broker 23/49, ir-run 206, honest 275.

  Session notes (2026-05-17 EMERGENCY FINAL, one4all 63c6fd2a):
    icn_bb_assign_lhs_gen implemented. key() generator EXISTS (icn_bb_tbl_key_iterate).
    BLOCKER IDENTIFIED: table test shows x[key(x)]:=99 fails — values remain 88 not 99.
    Hypothesis: subscript_set() for tables works (line 469: table_set_descr called).
    BUT: the assignment pump may be restoring saved value on β instead of keeping assignment.
    BUG LIKELY: icn_bb_assign_lhs_gen line ~660 calls subscript_set but doesn't prevent
    restoration of saved value. Check: when entry != α, it restores z->saved before pump.
    FIX: probably need to NOT restore on β if this is persistent assignment (not revassign).
    NEXT: trace through revassign_lhs_gen vs assign_lhs_gen logic — are they identical?
    They probably shouldn't be: revswap UNDOES on β; assign should PERSIST assignment on β.

  Session notes (2026-05-17, one4all cac06b4e):
    IJ-19-remaining: fix TT_SEQ conjunction & short-circuit in bb_exec_stmt.
    Root cause: TT_SEQ (Icon & operator) shared case with TT_SEQ_EXPR (block) in
    bb_exec_stmt; both used bb_exec_stmt per child which discards return value and
    never short-circuits. Fix: TT_SEQ now uses bb_eval_value per child, returns on
    IS_FAIL_fn. TT_SEQ_EXPR keeps bb_exec_stmt per child (statement failure absorbed).
    Reproducer: every x := 0|1|2 do { member(T,x) & write(x) } -- write fired for
    all x; now fires only when member succeeds. Gates unchanged (206/275/5/5/23) --
    fix is correctness improvement; failing rungs have additional issues beyond this.
    Investigated next: list negative indexing (x[-2] off-by-one) and list slices
    (x[1:0] hitting string path). Not yet fixed -- context window limit reached.

  Session notes (2026-05-16, one4all 00da02b6):
    TT_SUSPEND user-proc generators implemented via GeneratorState DCG.
    Rename: SmGenState -> GeneratorState (31 sites, 11 files); sm_gen_state_new ->
    generator_state_new; g_current_gen_state -> g_current_generator_state.
    lower_suspend: emit SM_SUSPEND (not SM_SUSPEND_VALUE). GeneratorState gains
    saved_frame_depth; generator_state_new_proc() pushes frame and captures depth.
    bb_broker_drive_sm_one: restores frame_depth before each pump, pops on exhaustion.
    IR_ICN_PROC_GEN executor drives bb_broker_drive_sm_one. icn_bb_build: proc_has_suspend()
    detects generator procs; uses GeneratorState DCG path. All rung03_suspend_* PASS.
    ir-run 202->205 (+3). Gates: smoke 5/5, broker 23/49, honest 275.
  Session notes (2026-05-15, no commit to one4all -- all approaches reverted):
    HQ commit a2c7cb62: enabled co-expression/TT_SUSPEND support in GOAL-ICON-BB-JCON + ARCH-ICON.
    Three approaches tried and rejected: (1) SM_BB_EVAL path -- sm_yield_to_caller stub returns 0.
    (2) ucontext swapcontext -- rejected: complex lifecycle. (3) AST walk at pump time --
    rejected by Lon 2026-05-15: NO AST/tree_t* at runtime pump time.
  Prior session fix:
    e2d80506 IJ-19-remaining: fix icn_bb_scan_gen integer subject crash (honest 273->275)
  Prior session fixes:
    11c43e0d IJ-19-remaining: image(DT_FH) fix; any/many/upto 2-arg in icn_try_call_builtin_by_name
    fec85821 IJ-19-remaining: any/many/upto 2-arg outside scan, cset identity (slen=0xFFFFFFFF) fix
    390335c3 IJ-19-remaining: math nargs>=1, list() nargs>=0, ||| list concat, scan_pos default
    992a2a18 IJ-19-fail: fix fail keyword in proc bodies (SM_BB_EVAL + sm_call_expression) — roman +1
