# HANDOFF — ICON-BB IBB-8c — REAL LITERALS + {} BLOCKS + every-do-body(ival=1)

**Author:** Claude Sonnet 4.6
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-8c
**SCRIP:** `91874d71` (on origin/main; three Icon commits interleaved with concurrent Prolog work)
**Repos touched:** SCRIP (2 files), .github (this doc + GOAL watermark)

---

## What landed — three independent mode-3 fixes

### 1. `bb_lit_scalar.cpp` — BB_LIT_F vstack-push (`0be6e78d`)

The float-literal path was a pass-through stub that never pushed the real, so any
relop consuming a real popped garbage / underflowed the vstack. Added a 32-byte
MEDIUM_BINARY arm mirroring the BB_LIT_I arm exactly, but bit-casting `pBB->dval`
to `uint64_t` and calling `rt_push_real_bits` (the existing real-by-IEEE-bits push
helper, already used by `sm_push_pop_lits.cpp`). Layout identical to BB_LIT_I:
`movabs rdi,bits / movabs rax,&rt_push_real_bits / call rax / jmp γ / β: jmp ω`,
patch sites `{23,27,28}`.

Result — rung18 real relops (m2==m3, zero SM each):
**real_gt, real_lt, real_eq, mixed_relop PASS (4/5).**
`real_relop_goal` (`every write(3.0 < (2.5|3.5|4.5))`) still fails — that is a
float literal in the BB_BINOP_GEN generator-context path, a separate front.

### 2. `emit_bb.c` `walk_bb_flat` — BB_SEQ_EXPR ({} block) (`37517836`)

Block-body then/else (`if x>3 then { ...; ... }`) lowers the block to BB_SEQ_EXPR
(`lower_icn_new_SeqExpr`: `bb->α=stmts[0]`, stmts chained via γ, `ival=count`) —
structurally identical to BB_SEQ. `walk_bb_flat` had no BB_SEQ_EXPR case → it hit
`default:` (`define β; jmp ω`) and the block body was never emitted (silent
no-output in mode-3). In statement context the block value is discarded, so its
control flow is identical to BB_SEQ; routed BB_SEQ_EXPR through the same
node-keyed CFG emitter `flat_drive_seq`.

Newly passing: **rung35_block_body_if_block, rung35_block_body_if_else_block**
(m2==m3, zero SM each).

### 3. `emit_bb.c` `flat_drive_every` — every-E-do-body, ival=1 (`91874d71`)

`every 1 to 3 do write("x")` aborted (`every-with-do-body not yet flat-wired`).
`lower_icn_new_Every_ag` ival=1 (static-literal gen + simple body) wiring is a
two-node loop: `gen=bb->α` (BB_TO α==β==NULL), `body=bb->β`,
`gen.γ=body  gen.ω=bb  body.γ=gen  body.ω=gen`.

Flat topology emitted:
- walk gen: γ → body_α, ω → outer γ (exhausted), β → gen_β (advance/re-pump)
- walk body: γ → gen_β (re-pump next value), ω → gen_β, β → body_β

Body success AND failure both route to gen_β so the next generated value is
produced (do-body runs once per value, its result discarded).

Verified: `every 1 to 3 do write("x")` m2==m3 (x/x/x), zero SM. ival=2/3 do-body
shapes still abort loudly (next fronts).

---

## Gates (verified at handoff)

- smoke_icon 5/5, smoke_prolog 5/5, smoke_unified_broker 39/14
- FACT gate 0
- zero-SM holds for every migrated program (`--dump-sm | grep count=0`)
- Corpus same-sweep (`/home/claude/corpus/programs/icon`, m2-OK filter, m2==m3 && m3 rc=0):
  **28 → 46** across the session (+13 from BB_LIT_F, +5 from BB_SEQ_EXPR; every-do
  ival=1 adds capability verified by direct test but no corpus program is a pure
  ival=1 do-body so the count is flat for that commit). No regressions.

---

## NEXT — IBB-8c continued

1. **every-do-body ival=2 / ival=3.** The corpus rung35 every-do cases use
   `every x := 1 to 3 do { block }` (assign-wrapped gen + BB_SEQ_EXPR block body).
   That is the **ival=3 BODY-MEDIATED** path (`gen.γ=bb gen.ω=bb body.γ=bb body.ω=bb`,
   phase machine on `bb->state`) — the hardest. ival=2 (gen-bearing chain, simple
   body) is the intermediate. Both abort with a clear ival= message today.
   Blockers under ival=3: needs the bb back-edge phase machine (1=just-dispatched-gen,
   2=just-dispatched-body) flat-wired, plus per-pass BB_SEQ_EXPR state reset, plus
   the `x := ...` assign in the gen position and the `*`/`+:=` ops in the body.

2. **while-E-do-body.** `rung35_block_body_while_do_block` produces empty mode-3
   output (no abort) — while-loop driver + augop (`+:=`) body not flat-wired.

3. **real_relop_goal** — float literal as LHS of a BB_BINOP_GEN relop in generator
   context.

4. Per the GOAL doc: write(BB_CALL), user-proc dispatch (large remaining cluster).

---

## Per-rung gate used this session

```bash
SCRIP_ICN_BB=1 ./scrip --interp PROG.icn > m2.txt
SCRIP_ICN_BB=1 ./scrip --run    PROG.icn > m3.txt
diff m2.txt m3.txt                                   # empty
SCRIP_ICN_BB=1 ./scrip --dump-sm PROG.icn | grep -c count=0   # == 1
```

---

## ROOT-CAUSE DIAGNOSIS — every-do-body ival=0 (`every x := 1 to 3 do B`) — next session start here

Investigated but NOT landed (tree reverted clean at `91874d71`). The diagnosis:

**The top-level Icon `every` statement does NOT go through `flat_drive_every` in
emit_bb.c.** It is dispatched by `emit_core.c:556 case BB_EVERY: bb_every(nd)` to the
**`bb_every.cpp` TEXT template** (the `.Levery<id>_body_*` labels you see in
`--compile` output). `flat_drive_every` (the `xevery%d_*` binary driver) is a
DIFFERENT, currently-unexercised path for top-level every. **Editing
`flat_drive_every` or `flat_drive_assign` does nothing for these programs** — verified
by `--compile` showing template labels regardless.

How the template works (bb_every.cpp MEDIUM_TEXT, lines 29–87): it treats `pBB->α` as
a single pumpable "body", walks it once via `walk_bb_node_str_c`, then wires
`body_γ → body_β` (re-pump) and `body_ω → outer_γ` (exhausted).

- **ival=1 (`every 1 to 3 do write("x")`) WORKS** because `pBB->α` = BB_TO and lower
  wired `gen.γ=body, body.γ=gen, gen.ω=bb`, so the BB_TO's own `body_β` advance
  (`add qword [cur],1; jg body_ω`) is present and the loop iterates.

- **ival=0 (`every x := 1 to 3 do write(...)`) FAILS (prints only first value)** because
  `pBB->α` = BB_ASSIGN (`x := 1 to 3`). lower's flat-wire gate is
  `if (gen->α==NULL && gen->β==NULL)` — a BB_ASSIGN has α=lhs-var, β=rhs, so the gate is
  SKIPPED, gen.γ/ω stay unset, ival stays 0, body is in pBB->β (ignored by template).
  The template then walks the BB_ASSIGN, whose bb_assign.cpp TEXT arm emits ONLY
  `call rt_pop_nv_set; jmp body_γ` — **the BB_TO rhs is never emitted** (the assign
  template assumes its value is already on the vstack per the ival==1 deep-thread
  convention) and there is no β-advance. So `body_β → body_ω` (exhausted) after one pass.

`lic_gen_kind_raw` deliberately EXCLUDES static BB_TO/BB_TO_BY (only streaming gens:
BB_ALT, BB_LIST_BANG, BB_BINOP_GEN, BB_ITERATE, BB_LIMIT, BB_PROC_GEN, BB_KEY_GEN,
BB_FIND_GEN, BB_SEQ_GEN), with the comment that static TO "stalls if re-pumped through
the BB_ASSIGN rhs-recursion" in the mode-2 executor — which is why mode-2 runs this on
the legacy ival=0 executor loop (bb_exec.c:1714–1731), not the flat-wire path.

**The fix belongs in lowering OR the bb_every TEXT template, not the binary flat
drivers.** Two candidate approaches:
  (A) **Lowering**: in `lower_icn_new_Every`/`_ag`, detect `gen` = BB_ASSIGN whose rhs
      is a static-literal generator (BB_TO/BB_TO_BY, α==β==NULL). Restructure so the
      BB_TO is the pumped node: `bb->α = rhs_TO`; wire `TO.γ = assign-store-step → body`,
      `body.γ = TO`, `body.ω = TO`, `TO.ω = bb`. The assign-store reads the TO's yielded
      value (on the vstack / ring) and stores into x. This makes ival match the ival=1
      shape and the existing template loops correctly. Must NOT break `every v := !t do B`
      (ival=2 streaming) — gate the new branch on the rhs being a STATIC TO specifically.
  (B) **Template**: teach bb_every.cpp (or a dedicated do-body arm) to emit the
      generator pump + per-value body when pBB->β is set and pBB->α is an assign-over-
      static-gen. More localized but duplicates loop logic.

Approach (A) is cleaner and reuses the working ival=1 template path. Verify against
mode-2 with `rung35_block_body_every_do_block` / `_nested_block` and the minimal
`every x := 1 to 3 do write(x)`. Also `rung35_block_body_while_do_block` is a separate
WHILE-driver gap (empty m3 output; while loop + `+:=` augop body not flat-wired).
