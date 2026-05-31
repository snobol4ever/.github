# HANDOFF — ICON-BB IBB-9-1 — every x:=1 to N do B + JCON-grounded IBB-9 roadmap

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-9 (new)
**SCRIP:** `e8f66866` (on origin/main, rebased onto `b408b086`)
**Repos touched:** SCRIP (2 files), .github (GOAL + PLAN watermark + this doc)

---

## What landed — IBB-9-1: `every x := 1 to N do body`

`every x := 1 to 3 do write(x)` aborted in mode-3 (`flat_drive_every: do-body ival=0
not yet flat-wired`). Now mode-2==mode-3 byte-identical (`1\n2\n3`), zero SM.

### The JCON insight that shaped it

Read `jcon/tran/irgen.icn` (the uploaded JCON Icon→IR translator — SCRIP's lowering
is a direct transcription of its `ir_a_*` chunk-wiring). The key discovery:

**JCON does NOT special-case `every x := GEN do B`.** It is plain `ir_a_Every` where
`p.expr` is the assignment `x := (1 to 3)`. Because `:=` is in `ir_a_Binop`'s `funcs`
set (irgen.icn:476), `ir_binary` (irgen.icn:438-444) wires `expr.resume → right.resume`:
the assignment is **transparent to resume** — it forwards resume straight into its rhs
generator. The generator yields the next value, `right.success` re-applies the store
opfn, and re-yields. One uniform mechanism, no shape dispatch.

### SCRIP transcription (two files)

**1. `src/lower/lower_icn.c` `lower_icn_new_Every_ag`** — new branch BEFORE the generic
gen-lowering. Gate: `c[0]` is TT_ASSIGN, its rhs is a static literal TT_TO (lowers to
BB_TO with α==β==NULL), lhs is plain TT_VAR. Build an interposed BB_ASSIGN **store**
node and wire the existing ival=1 every topology:
```
gen.γ = store    store.γ = body    body.γ = gen    body.ω = gen    gen.ω = bb
bb.α = gen_chain_entry    bb.β = store    bb.ival = 1
store.α = lhs(BB_VAR)    store.β = gen    store.ival = 1
```
`store.β = gen` (non-NULL) satisfies mode-2's BB_ASSIGN null guard
(`bb_exec.c:1157 if (!bb->α || !bb->β) fail`); `store.ival=1` tells mode-2 to read the
yielded value via `ag_ring_peek(0)` (the chain walker pushes every step's value to the
ring, `bb_exec.c:4637`) instead of recursing into β.

TT_TO_BY is **excluded** — `lower_icn_new_ToBy` keeps α=lo/β=hi operand boxes for TO_BY
even with literal bounds (template uses a BB_LIT_I fast-path, not α/β scrubbing), so it
fails the α==β==NULL static-shape check and needs separate BB_TO_BY mode-3 generator
wiring (a later step).

**2. `src/emitter/emit_bb.c` `flat_drive_every`** — in the ival=1 branch, detect the
interposed store (`pBB->β->t == BB_ASSIGN && pBB->β->ival == 1 && pBB->β->γ`) and emit
three segments instead of two:
```
walk gen  → body_α (yield), lbl_γ (exhaust), gen_β (advance)
body_α: walk store → actual_body_α (γ), lbl_γ (ω), store_ω (β-DEAD-STUB)
actual_body_α: walk do-body → gen_β (γ and ω, re-pump)
```

### THE BUG (and fix) worth remembering

First attempt passed `gen_β` as the store's `lbl_β`. `flat_drive_assign` ival=1 does
`EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω)` which **defines** `gen_β` as `jmp gen_β` — an infinite
self-loop (mode-3 printed `1` then hung). Fix: give the store a dedicated dead
`store_ω` label for its β-port; the store never backtracks so the stub is never reached.
mode-3's value comes from the vstack (`rt_push_int` in gen → `rt_pop_nv_set` in store).

### Verification

- `every x := 1 to 3 do write(x)`: m2==m3 (`1 2 3`), zero SM, byte-identical.
- Corpus same-sweep (whole tree, see methodology below): **213 → 216 PASS (+3)**,
  SEGV 0, zero regressions (no lost passes; diff'd sorted pass-lists).
  New passes: `rung37_every_do_hello`, `rung35_block_body_nested_block`, `range_to`.
- Gates: FACT 0; smoke icon/prolog 5/5; broker 42/11; prior IBB-8b/8c rungs hold
  (rung18_real_relop_real_gt, rung35_block_body_if_block, rung37_strrelop_hello,
  rung12_strrelop_size_slt, rung07_control_seq all OK).

### GATE METHODOLOGY (now pinned in the GOAL "Current state" section)

The historical "22→28"/"28→46" rows used a NARROWER corpus filter than the whole-tree
sweep. The canonical script (use it every session for apples-to-apples deltas):
for each `corpus/programs/icon/*.icn`: run `--interp` (skip if rc≠0 — the m2-OK filter),
then `--run`; PASS iff `m3 rc==0 && m2==m3`. Baseline `30e7c0a1`=213, `e8f66866`=216.

---

## IBB-9 roadmap (now the CURRENT rung, all JCON-grounded)

Each step cites the exact `ir_a_*` procedure to transcribe. The spine: the ONLY
structural difference between loop forms is where body-success/failure routes —
`expr.resume` (every) vs `expr.start` (while/until). See GOAL-ICON-BB.md rung IBB-9.

- **9-1 ✅** every x:=1 to N do B (this commit).
- **9-2** `while C do B`. FIRST diagnose the `do {block}` parser gap
  (`while C do { … }` → `parse error: expected ; (got while)` today). THEN transcribe
  `ir_a_While` (irgen.icn:1008): body.success/failure → **expr.START** (re-eval cond).
  Target `rung35_block_body_while_do_block` (empty m3). Needs augop `+:=` body
  (`ir_augmented_assignment:417`).
- **9-3** `until C do B`. `ir_a_Until` (irgen.icn:981): cond-result edges flipped
  (success→failure-exit, failure→body). Share the while driver.
- **9-4** every ival=2 (gen-bearing chain, simple body). mode-3 flat_drive_every ival=2
  emit is the gap; lower branch already exists.
- **9-5** every ival=3 (BODY-MEDIATED block body). Hardest: phase machine on bb->state,
  per-pass BB_SEQ_EXPR reset. ALSO fix the mode-2 ival=3 x-rebind bug
  (`every x:=1 to 3 do {y:=x*2;write(y)}` → m2 prints `2 2 2`, should be `2 4 6`;
  mode-3 is already correct) or the byte-identical gate can't pass.
- **9-6** user-proc dispatch. `ir_a_Call` (irgen.icn:360): arg chain
  `L=[fn]|||args`, `ir_Call(closure,fn,args,resume)`. Needs `rt_call_proc` + BB_RETURN
  flat-wire (`ir_a_Return:867`). Largest ABORT cluster.
- **9-7** write(BB_CALL) / write(proc-result). Depends on 9-6.
- **9-8 DEFERRED** unbounded/expression-context resume = computed-goto continuation
  (`ir_MoveLabel(t, arm.resume)` + `ir_IndirectGoto(t)`, `ir_a_If:596`, `ir_a_Alt:183`).
  The `bounded` flag SCRIP currently ignores. Same idea as WAM-CP. Only when a corpus
  program forces it (`x := if a then (1 to 3); every write(x)`).

---

## Per-rung gate used this session

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh
./scrip --interp PROG.icn > m2.txt
./scrip --run    PROG.icn > m3.txt
diff m2.txt m3.txt                                       # empty
./scrip --dump-sm PROG.icn | grep count                  # count=0
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l       # 0
bash scripts/test_smoke_icon.sh                           # 5/5
bash scripts/test_smoke_prolog.sh                         # 5/5
```

JCON/ICON sources extracted to `/home/claude/jcon_icon/jcon-master/tran/irgen.icn`
(and `ir.icn`) for reference — re-extract from the uploaded `jcon-master.zip` if needed.
