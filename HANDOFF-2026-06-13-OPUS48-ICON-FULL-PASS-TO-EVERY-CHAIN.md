# HANDOFF 2026-06-13 — Opus 4.8 — ICON-FULL-PASS: descending TO + EVERY-exhaustion chaining

**Goal:** GOAL-ICON-FULL-PASS (live priority under GOAL-ICON-BB).
**HEAD (SCRIP) = `fb2daea`** (on top of prior watermark `d35075a`; clean rebase).
**Gates:** m2 200/283 HARD held · m3 44→45 · m4 50→51 · prolog 5/5 HARD held · bb_one_box unchanged.

---

## What landed (two commits, SCRIP)

### `5dc543f` — `bb_to` emits descending TO loops (negative `by`)
`src/emitter/BB_templates/bb_to.cpp`. The flat-chain arm guarded on `bb_to_by() > 0`, so
`10 to 1 by -3` fell through to `x86_bomb` **at its α label** and never emitted its `def β`
port → the downstream consumer's success→resume `jmp xchainN_nK_β` became an unresolved forward
reference → `bb_emit_end: 1 unresolved forward reference(s)` → rc=134 (`rung01_paper_to_by`).

Fix (4 lines, all through the `x86()` funnel):
- guard `bb_to_by() != 0` (was `> 0`);
- loop-exit comparison picks direction by sign: `IF(by>0, x86("jg","ω")) + IF(by<0, x86("jl","ω"))`,
  matching the m2 oracle test `(by>=0 ? counter>to : counter<to)` (IR_interp.c IR_TO_BY);
- the `add rax, <by>` step already decrements for negative `by`; the `by==1` `inc` fast-path is unchanged.
Both `jg`(0x8F)/`jl`(0x8C) already have byte-verified encoders in `x86_asm.h` — no new encoder needed.

### `fb2daea` — flat-emit: bounded EVERY exhaustion → success continuation, not proc failure
`src/emitter/emit_bb.c`, `codegen_flat_chain_body` omega resolver (~line 2970).
**Symptom:** two consecutive `every` statements dropped all but the first.
`every write(1 to 2); every write(5 to 6)` emitted only `1 2`; every descending/relop TO+EVERY
rung lost its tail statements. Reproduced with all-positive steps → independent of the bb_to fix.

**Root (and why it's safe):** confirmed m2 walks the *identical* BB graph and prints all values,
so the graph topology is correct and this is purely a flat-emitter bug (cannot move the m2 HARD
gate). In the chain omega resolver, a generator (TO/etc.) whose `ω` port resolved to its own
EVERY node was routed to `lbl_ω` (= the chain's overall failure = `main_ω`). So a generator
exhausting fired `jg main_ω` and the whole proc terminated at the first loop's end. But an Icon
`every` is **bounded**: on generator exhaustion it SUCCEEDS and passes control to the next
statement (EVERY.γ); it does not fail the procedure.

**Fix:** the resolver already computes the EVERY node's own α label (`lbls[k]`) for the resolved
case, then overrode it to `&lbl_ω` for generator-kind producers. Keep the EVERY's α label
(`lbls[omega_k]`) instead, so the EVERY box runs and takes its γ — to the next statement, or to
the proc-success epilogue for a final/single `every` (EVERY.γ → IR_SUCCEED → `lbl_γ`). Correct in
both shapes. Diff is 3 lines: thread an `omega_k` index out of the resolve loop and use it.

```c
int omega_resolved = 0; int omega_k = -1;
for (int k = 0; k < n; k++) if (nodes[k] == nodes[i]->ω.node) { node_ω = lbls[k]; omega_resolved = 1; omega_k = k; break; }
if (!omega_resolved) node_ω = &lbl_ω;
if (omega_resolved && nodes[i]->ω.node && nodes[i]->ω.node->op == IR_EVERY) {
    if (ir_is_generator_kind(nodes[i]->op)) { node_ω = lbls[omega_k]; }   /* was &lbl_ω */
    else { for (int gk = 0; gk < n; gk++) if (ir_is_generator_kind(nodes[gk]->op)) { node_ω = betas[gk]; break; } }
}
```

**Verified PASS m3/m4 after fix:** `rung01_paper_to_by`, `rung01_paper_lt` (the goal file's named
TO+relop+EVERY silent-empty representative), `rung07_control_to_by`; `pospos` two-loop → `1 2 5 6`.

---

## Method notes for next session
- Canonical authority confirmed for statement sequencing: JCON `ir_a_Compound`
  (refs/jcon-master/tran/irgen.icn:1231) — non-last statements route BOTH success and failure to
  the next statement's `.start`, lowered "always bounded". `ir_a_Every` at :309, `ir_a_ToBy` at :1168.
- Asm chain labels `xchainN_nK_*` are CHAIN POSITIONS, not graph node ids; the two index spaces differ.
- Fastest triage: `./scrip --run foo.icn 2>&1` for the bomb text; `./scrip --compile --target=x86 foo.icn`
  to read the `.s` and follow the `jmp`/`jg`/`jl` targets; `--dump-bb` for graph (no `operand_aux`).
- The "graph right (m2 passes) ⇒ flat-emit bug" pattern is a SAFE class — it cannot regress the m2 200 gate.

## Next targets (GOAL-ICON-FULL-PASS m3/m4 gap)
1. **rc=139 IR_CASE** — `rung33_case_*` segfault; no native template. Build `flat_drive_case`/`bb_case`
   from `ir_a_Case` (irgen.icn:232): bounded uses a MoveLabel temp + IndirectGoto for resume.
2. **rc=124 timeout cluster (~12)** — TO/EVERY retry wiring loops in the BINARY path on some shapes.
3. **Residual rc=134 bombs (~28)** — grep `rt_bomb` per still-failing rung; likely `bb_alt`/`bb_scan_*`.
4. **FULL-18-resid** (m2, still open) — generator in user-proc call arg disappears from BB graph;
   `lower_call` sets `cx->beta=ω` for non-gen procs. lower_icon.c lower_call line 82/94.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.8
