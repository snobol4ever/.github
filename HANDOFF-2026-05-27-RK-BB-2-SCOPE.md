# HANDOFF 2026-05-27 — RK-BB-2 scope discovery (no code changes)

**Author:** Claude (this session)
**Goal:** GOAL-RAKU-BB.md → RK-BB-2 (gather/take Seq box)
**Status:** ⛔ NOT STARTED — scope larger than goal file suggested, fresh ~80% context recommended
**Repo state:** clean. SCRIP at `158394fb`, .github unchanged, corpus unchanged.

## Baselines confirmed at session start (`158394fb`)

```
GATE-RK  mode-2:  8/30   ✅ matches watermark
GATE-RK4 mode-4:  8/30   ✅ matches watermark
Smoke:            5/0    ✅ matches watermark
```

## Demo of the current failure (mode-2 AND mode-4 both fail rk_gather)

```
$ ./scrip --interp test/raku/rk_gather.raku
sm_lower: unhandled AST kinds: TT_EVERY
done
$ bash scripts/run_raku_via_x86_backend.sh test/raku/rk_gather.raku
done
```

Expected output: `10\n20\n30\ndone`. Actual: only `done`.

## What the goal file said vs. what's actually there

GOAL-RAKU-BB.md RK-BB-2:
> KEYSTONE lazy `Seq` box. `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP.
> Retarget `lower_gather_hoist_pass` so `take` becomes γ-yield in the Seq box
> (lower-risk than full replacement). REUSE `bb_upto.cpp`.

What's actually there:

1. **`bb_upto.cpp` is NOT a generic yield/pump primitive.** It is the Icon
   `upto(cset)` position generator (string-position scan with strchr). The
   sval/ival fields carry cset/slen. Not reusable as-is for gather/take.

2. **`BB_SUSPEND` has NO x86 template.** In `emit_core.c:532` it dispatches to
   `bb_stub(nd)`. There is no `bb_suspend.cpp` in `src/emitter/BB_templates/`.

3. **`lower_every` rejects non-Icon** (lower.c:1461):
   ```c
   if (g_lang != LANG_ICN) { lower_unhandled(t); return; }
   ```
   This is why mode-2 prints "unhandled AST kinds: TT_EVERY" for the gather
   test — Raku's `for gather { ... } -> $v { body }` lowers to
   `TT_EVERY(TT_ITERATE(__gather_0()), body)` (raku.y:307) but lower_every
   bails immediately.

4. **`lower_iterate` rejects non-Icon** (lower.c:1557): same pattern.

5. **`lower_icn_proc_body` likely returns NULL for the hoisted `__gather_N`
   proc** because `lower_icn_expr_threaded_b` has no case for `TT_SUSPEND`
   (verified via `grep TT_SUSPEND src/lower/lower_icn.c` → 0 hits). When that
   happens, the proc's `bb_idx` is -1 and the runtime takes a SM-walk fallback
   that uses GeneratorState.

## What "REUSE bb_upto.cpp" plausibly means

After reading the surrounding text ("ONE four-port pull protocol",
"BB_SUSPEND+BB_EVERY PUMP"), the goal author may have meant:
- The pull *protocol* (α fresh-pull, β resume, γ yield, ω drained) is the
  same shape as `bb_upto.cpp`'s loop structure.
- We need a NEW template `bb_suspend.cpp` that implements that protocol for
  proc bodies, generalizing the loop+yield pattern from `bb_upto.cpp`.

Or possibly:
- "REUSE" was aspirational on read — the actual implementation requires a
  new template, with `bb_upto.cpp` as the structural reference.

**Recommend Lon clarify** before implementation starts.

## Concrete surface area for RK-BB-2

Minimum viable scope to make `rk_gather.raku` print `10\n20\n30\ndone`:

### A. Lowering (lower.c)
1. Extend `lower_every` to accept `LANG_RAKU` when `gen_expr` is
   `TT_ITERATE(TT_FNC(gen_name))` where `gen_name` resolves to a proc with
   `is_generator=1`.
2. Extend `lower_iterate` to accept `LANG_RAKU` analogously (or remove the
   intermediate `TT_ITERATE` for Raku at hoist time).
3. Either:
   - **Path α (lower-risk per goal file)**: keep `lower_gather_hoist_pass`,
     ensure the hoisted `__gather_N` sub is lowered as an Icon-style
     generator proc — the existing SM_CALL_FN + is_generator + GeneratorState
     machinery should then work end-to-end in mode-2. Mode-4 will need
     `SM_BB_SWITCH(SM_BBSW_RK_GEN)` over the proc's bb_idx (if non-NULL).
   - **Path β (full replacement, goal "Open question 1")**: replace the
     hoist pass with direct `BB_SUSPEND` lowering inline. Requires more
     changes but produces cleaner BB graphs.

### B. Proc-body BB graph (lower_icn.c)
4. Add a `TT_SUSPEND` case to `lower_icn_expr_threaded_b` (or its node-builder)
   that emits a `BB_SUSPEND` node with the expression as a child. Without
   this, the hoisted gather sub's `bb_idx` stays -1 and mode-4 has no graph
   to switch on.

### C. Emitter (BB_templates + emit_core.c)
5. Write `src/emitter/BB_templates/bb_suspend.cpp` with the four-port pull
   protocol:
   - α: enter fresh, evaluate expr, push to value stack, jmp γ
   - β: resume after consumer used the previous value — on a proc-body
     suspend, β means "continue after this suspend statement"; falls
     through to next-stmt α
   - γ: yield (consumer receives the value, will β us back)
   - ω: exhausted (only reached when proc body falls off end — wired by
     BB_SEQ ω-edge)
6. Rewire `emit_core.c:532` from `bb_stub` to `bb_suspend`.

### D. SM_BB_SWITCH runtime arm (sm_bb_switch.cpp / sm_interp.c)
7. Confirm `SM_BBSW_RK_GEN` arm in `sm_bb_switch.cpp` handles a BB graph
   whose entry is `BB_SEQ` (proc body), not just a leaf generator like
   `BB_TO_BY`. RK-BB-1 used a single-node `BB_TO_BY`; proc-body graphs are
   multi-node.

### E. Tests
8. `test/raku/rk_gather.raku` already exists with `.expected`. After
   implementation: GATE-RK and GATE-RK4 should each gain +1 (8/30 → 9/30).
9. The `…` operator (Raku sequence operator) shares the same machinery
   per goal file; needs its own test.

## What I did NOT do (and why)

- **Did not modify any code.** The implementation is non-trivial enough
  that a half-finished attempt would leave the tree in an unclear state.
  Goal file already warns "Fresh context required (~80%+)" for the
  analogous Icon rung; same applies here.
- **Did not commit.** Working tree is clean.
- **Did not push.** Nothing to push.

## Recommended next-session script

1. Read this HANDOFF first.
2. Get Lon's clarification on the `bb_upto.cpp` REUSE question above.
3. If Path α: start with B+A1 (smallest first move) — add TT_SUSPEND case
   to lower_icn, then enable LANG_RAKU in lower_every. Verify mode-2 turns
   green on rk_gather. THEN do C+D for mode-4.
4. If Path β: redesign `lower_gather_hoist_pass` to emit BB_SUSPEND nodes
   directly into a BB graph; skip the proc-table hoist.

## Open questions for Lon (echoed from GOAL-RAKU-BB.md)

1. `lower_gather_hoist_pass`: retarget (Path α) or replace (Path β)?
2. `bb_upto.cpp` REUSE: literal reuse, or use as structural template for
   a new `bb_suspend.cpp`?
