# Handoff — AG-PURE Wholesale Rewrite Steps 1-7 Landed

**Date:** 2026-05-27
**Author:** Claude Opus 4.7 on direction from Lon Cherryholmes
**Branch:** `ag-pure-icn` (this branch — not yet merged to main)
**Goal:** GOAL-ICON-BB.md (wholesale lower_icn.c + bb_exec.c rewrite to four-port-only-CFG model)

## What was done

The Icon lower + executor was migrated from a hybrid tree/CFG shape (operands as pointers in α/β) to a pure four-port CFG model (α/β/γ/ω all CFG edges; operand values flow through a `cfg->ring`).

| Commit | Step | Kind |
|--------|------|------|
| `64805e16` | 1 | Ring fields in BB_graph_t (dormant) |
| `e2850a98` | 2 | Chain walker pushes to ring EVERY step (incl. FAIL) |
| `9d4d25b0` | 3 | **BB_BINOP** AG-pure |
| `245ae97e` | 4 | **BB_SEQ** AG-pure + BB_FAIL terminal + FRAME.returning walker |
| `687d6694` | 5 | **BB_IF** AG-pure |
| `76453c56` | 6 | **BB_CONJ** AG-pure |
| `e8217005` | 7 | **BB_ALT** AG-pure |

## Gate parity at every commit

```
smoke_icon       PASS=5  FAIL=0
test_smoke_unified_broker PASS=24  FAIL=26
test_icon_all_rungs PASS=198 FAIL=34 XFAIL=36 TOTAL=268
test_smoke_prolog PASS=5 FAIL=0
```

## Key invariants discovered (must hold for any further migration)

1. **Push every step.** Chain walker pushes `cur->value` to ring even when value is FAILDESCR. Routing boxes (BB_IF, BB_CONJ-fail, BB_ALT arm-fail) need to see the actual predecessor value via `ag_ring_peek(g_current_cfg, 0)`.

2. **fail_term pre-loop.** `lower_icn_proc_body` allocates the BB_FAIL terminal BEFORE the stmt-build loop and passes it as the initial `succ` argument. Composite stmts at the proc tail (BB_IF then/else branches, BB_ALT arms, etc.) inherit it as their γ_in/ω_in and end at the terminal — without this, branches exit with their own value and the SM caller pumps the cfg forever.

3. **Termination-signal kinds excluded from stmt-ω-rewrite.** BB_RETURN, BB_FAIL, BB_BREAK, BB_NEXT: their ω is a termination signal (chain walker stops, FRAME.returning carries return value), NOT a CFG edge to a next stmt. Rewriting their ω causes a recursion segfault.

4. **FRAME.returning safety net.** `bb_exec_once` and `bb_exec_resume` check FRAME.returning after each step and bail with `g_ir_return_val`. Defense in depth.

5. **AG intercepts at wrapper level.** AG-pure intercepts fire in `lower_icn_expr_threaded_b`, AFTER `lower_icn_expr_node` builds the legacy α/β-as-tree shape. The intercept scrubs α/β to NULL and lays the chain. Inner sub-expressions (e.g., the cond of an IF when itself a BINOP) retain legacy shape because `lower_icn_expr_node` recursively builds them WITHOUT going through the wrapper. Both shapes coexist: the chain walker treats each box as a single chain step producing a value via `cur->value`, regardless of internal recursion.

6. **AG-pure dispatch in executor: gate on α==NULL && β==NULL.** Apply-box cases in `bb_exec.c` check `if (!nd->α && !nd->β)` to take the peek-based AG path; legacy α/β-set path remains as fallback.

## Remaining work — Steps 8, 9, 10

### Step 8 — Generators (BB_EVERY, BB_TO, BB_TO_BY, BB_BINOP_GEN)

**Complexity:** HIGH. Generators are resumable (`β=self`). The chain walker enters at α on fresh, returns from γ with each yielded value; external code calls `bb_exec_resume` which re-enters at β to ask for next value.

- **BB_TO_BY** has two paths today:
  - Compile-time literals: `nd->α=NULL, nd->β=NULL`, bounds in `ival`/`dval`. THIS PATH IS ALREADY AG-PURE-SHAPED — the executor reads ival/dval, not nd->α/β. No lower change needed; the executor already works.
  - Dynamic operands: `nd->α=lo_box, nd->β=hi_box`. Executor reads `nd->α->value` and `nd->β->value` on state==0 (fresh) and each β-resume re-reads `nd->β->value` for `to_val`.
  - Migration: chain lo→hi→nd in lower; on fresh entry, executor reads `peek(1)=lo, peek(0)=hi`, caches BOTH (lo in counter already, hi needs a new slot — propose stashing hi in `nd->value` immediately and re-fetching from nd's own state on resume; on yield, overwrite value with the yielded count). Or add a `cached_hi` field to BB_t via a sidecar entry indexed by nd.
  - Risk: real-mode TO_BY uses dval as position, so the int-mode trick (dval=cached_hi) doesn't work uniformly.

- **BB_TO** (single-arg-style "lo to hi") — same shape as TO_BY but no step. Same caching question.

- **BB_BINOP_GEN** — generator-aware binop. Current executor (line 737+) is a stateful machine that drives left/right operand generators via `bb_exec_node` recursive calls. Migrating this is a major rework: needs the chain walker to handle a cross-product odometer. Provisional approach: keep BB_BINOP_GEN legacy for now; only single-shot BB_BINOP is AG-pure.

- **BB_EVERY** — has an internal `while` loop calling `bb_exec_node(nd->α)` and `bb_exec_node(nd->β)`. Major rework to make the chain walker drive the loop via β-resume on nd->α (the generator). The expr-side BB_EVERY (TT_EVERY case) already does some flat-wire of generator γ/ω/β edges — building on that pattern, the executor could become: on α-entry, return nd->α->α to enter the generator's chain; on each yield, the chain returns at our γ (or β-resume); we drive body via γ; loop terminates when generator's ω fires.
  - Risk: FRAME.loop_break / FRAME.loop_next / FRAME.returning interactions are subtle.

### Step 9 — N-ary applies

- **BB_CALL** currently uses the operand_aux sidecar (Family 2 from the prior PEERS-RULE work). To go AG-pure ring-peek: chain args via γ (lower already does this); apply reads `peek(N-1), peek(N-2), ..., peek(0)`.
- **BB_LCONCAT, BB_SECTION, BB_IDX, BB_IDX_SET, BB_FIELD_GET, BB_FIELD_SET, BB_SWAP** — all currently use `nd->α / nd->β` as operand pointers. Pattern same as BB_BINOP migration.

### Step 10 — Sidecar cleanup

- Delete `bb_operand_aux_set` calls from `lower_icn_expr_threaded_b` Family 1 (BB_ASSIGN) and Family 2 (BB_CALL) intercepts — once those kinds are converted to ring-peek.
- BB_ASSIGN executor currently reads from `bb_operand_aux_get(g_current_cfg, nd, &ops_n)` and falls back to `bb_exec_node(nd->β)`. AG-pure version: read `peek(0)` for rhs value (lhs is a BB_VAR by reference, not a value-producer in the chain).
- Sidecar struct + functions stay in BB.h for Prolog/SNOBOL4/other languages mid-migration.

## Architecture summary post-Step-7

```
src/include/BB.h
  BB_graph_t {
    entry, all, n, max, lang,
    operand_aux*, operand_aux_n, operand_aux_max,  // legacy, used by BB_ASSIGN+BB_CALL+other langs
    ring[16], ring_head, ring_depth                // NEW: AG-pure value flow
  }
  ag_ring_push / ag_ring_peek / ag_ring_clear      // NEW inline helpers

src/lower/lower_icn.c
  lower_icn_proc_body:
    - fail_term = BB_node_alloc(cfg, BB_FAIL) PRE-LOOP
    - back-to-front build with succ=fail_term initially
    - stmt-advance loop sets prev->ω = cur_entry, EXCLUDING
      BB_RETURN/BB_FAIL/BB_BREAK/BB_NEXT/BB_IF
    - terminal-wire pass sets last prev γ/ω to fail_term (same exclusions)

  lower_icn_expr_threaded_b:
    Pattern: lower via lower_icn_expr_node (builds legacy α/β shape),
    then intercept by e->t for the kinds that have AG-pure form.
    AG-pure intercepts implemented: TT_ADD/SUB/MUL/DIV/MOD/POW/LT/LE/GT/GE/EQ/NE/CAT (BB_BINOP),
                                    TT_IF (BB_IF), TT_SEQ (BB_CONJ), TT_ALTERNATE (BB_ALT).
    Each intercept: scrubs nd->α=nd->β=NULL, wires the chain with γ/ω,
    populates the ring path implicitly through chain order.

src/lower/bb_exec.c
  bb_exec_once / bb_exec_resume / bb_exec_pump:
    - Chain walker pushes cur->value to ring on EVERY step
    - bb_exec_once/resume honor FRAME.returning, exit with g_ir_return_val
  bb_reset: also clears ring via ag_ring_clear

  case BB_BINOP: if(!α && !β) read peek(1)/peek(0); else legacy
  case BB_IF:    if(!α && !β) read peek(0), route γ/ω; else legacy
  case BB_CONJ:  if(!α && !β) read peek(0) for value; else legacy
  case BB_ALT:   if(!α)       read peek(0) for value; else legacy
  case BB_SEQ:   passthrough: return nd->α (chain walker drives)
  case BB_FAIL:  unchanged (sets FAILDESCR, returns ω)
  case BB_RETURN: unchanged (sets FRAME.returning, returns ω)
```

## Next session quick start

```bash
git clone https://TOKEN@github.com/snobol4ever/SCRIP
cd SCRIP
git checkout ag-pure-icn
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh        # expect 5/5
bash scripts/test_icon_all_rungs.sh    # expect 198/268
```

Pick up at Step 8. Recommended first move: BB_TO_BY dynamic-operand AG-migration (smallest scope, well-bounded test space).

## ADDENDUM — Step 8 ordering insight (discovered 2026-05-27, attempted then reverted)

I attempted BB_TO_BY AG-pure migration in isolation and hit the same wall as Step 4 (BB_IF without BB_SEQ first):

**The dispatcher swallows ring visibility.** When BB_EVERY pumps its child generator, it calls `bb_exec_node(nd->α)` recursively — the same way the legacy BB_SEQ did. So when the child is BB_TO_BY with chained lo→hi→apply operand boxes, those operand boxes never push to the ring because they're walked through a recursive `bb_exec_node` call, not the outer chain walker.

**Sequencer-first ordering applies recursively.** Just as BB_SEQ had to be AG-pure before BB_IF could read peek(0), BB_EVERY (and other DISPATCHERS like BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL, BB_SCAN) must be AG-pure before generator-kinds nested under them can read peek().

**Recommended Step 8 sequence:**

- **Step 8.0:** Make `bb_exec_node` itself push the value to the ring for any cur it executes — i.e., move the ring-push from the outer chain walkers into the per-node executor entry/exit, so ANY box's execution updates the ring, whether driven by the outer walker OR a recursive bb_exec_node call.
  - Caveat: this might over-pollute the ring; need to think about whether recursive operand evals (e.g., BB_BINOP legacy reading nd->α via bb_exec_node) push transient values that confuse downstream peeks. Probably fine because the outer chain walker re-pushes the apply box's own value before advancing.
  - Alternative: have each dispatcher (BB_EVERY/BB_LIMIT/etc.) explicitly push child values to the ring before reading apply boxes downstream.

- **Step 8.1:** BB_EVERY AG-pure rework. Current internal `while` loop becomes a chain-walker-driven β-resume sequence. Heavy.

- **Step 8.2:** BB_TO_BY / BB_TO / BB_BINOP_GEN — once BB_EVERY drives them through the chain.

I lean toward Step 8.0 (push from bb_exec_node itself) as the unblocking move. It eliminates the dispatcher-swallow problem categorically.

The risk to evaluate: does pushing on EVERY bb_exec_node call (including recursive operand evals from legacy BB_BINOP etc.) misalign peek indices for AG-pure apply boxes higher in the chain? It might — because the chain walker pushes cur->value once per step, and if a step internally recurses through multiple boxes, each recursion would push too, ballooning the ring depth between the lhs/rhs of an outer binop.

Hmm — actually no. The OUTER chain walker calls bb_exec_node(cur) once per chain step. Within that call, if cur recurses (legacy BB_BINOP recurses into nd->α and nd->β to compute its operands), those recursive calls run and return — they don't push to the ring (because the push is in the outer walker, not in bb_exec_node). Then the outer walker pushes cur->value once. So the ring depth is well-behaved.

If I move the push INTO bb_exec_node, every recursive eval also pushes. That would mean for a legacy BB_BINOP with deep operand subtrees, the ring sees: lhs.value (lhs leaf), nd->α.value (BB_BINOP node), rhs.value (rhs leaf), nd->β.value (BB_BINOP node again? No, just once), the outer BB_BINOP.value. The chain walker then advances. An apply box downstream peeking expecting "the value of the box that just ran in the chain" would get the right thing (latest = outer BINOP.value), but earlier peeks might pick up intermediate operand values that aren't what the AG semantic wants.

Probably needs to be: only push from the OUTER chain walker (current design), AND make BB_EVERY/BB_LIMIT/etc. into AG-pure passthroughs like BB_SEQ. The chain walker then sees each generator-driven body iteration as a chain step.

That's where the next session should pick up.

