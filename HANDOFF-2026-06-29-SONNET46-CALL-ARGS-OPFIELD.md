# HANDOFF — 2026-06-29 — Sonnet 4.6 — GZ#5 D1-CALL-ARGS + Call-kind into op field

## Session summary

Two-part rung executed and pushed to SCRIP main (`6058d6f`):

### Part 1 — IR_CALL with arguments (flat operand-tmp model, JCON bc_gen_ir_Call conversion)

Before this session `write(f(3))` printed `1` (arg not reaching param) and
`write(abs(-5))` hit `[SMX] op=200 has no native template` and segfaulted.

Root causes found and fixed:
- `emit_drive_node` IR_CALL case set `op_arg_slot_n=0` and did not own
  IR_CALL_BUILTIN (op 200) or any other call kind variants.
- `bcps_arg_slot` gated on `dval==1.0` (dead for flat calls) and fell back
  to the null subgraph branch, returning slot 0 (garbage).
- `bcps_result_slot` / `bb_call_fn` used `bb_slot_alloc16(_.node)` for the
  call result — emit-time fresh alloc — so the result slot diverged from
  `nd->tmp` which the consumer (`write`) reads via its operand's tmp.
  This was the keystone violation: producer writes to alloc'd slot X,
  consumer reads nd->tmp=Y, X≠Y → empty/wrong output.

Fixes (4 files, all src/emitter/):
- `emit_drive.c` IR_CALL: owns all six call kinds; fills
  `op_arg_slot[i] = ir_call_arg(nd,i)->tmp` for i in 0..n_operands.
- `bb_call_proc_staged.cpp`: `bcps_arg_slot` reads operand->tmp directly;
  new `bcps_result_slot()` reads nd->tmp with cursor-reserve; all 4 arms use it.
- `bb_call_fn.cpp`: `bcfn_result_slot()` reads pBB->tmp; arg-staging buffer
  via `bb_slot_claim(nargs*16)` (fresh scratch, no collision with LOWER slots).

### Part 2 — Call kind into nd->op; dval gates deleted from the flat classifier

Lon's directive: move the dval tags {1.0, 2.0} off dval into the op field.

- `resolve_call_kinds_descr` (emit_bb.c:3724): ZERO dval gates now. Flat
  IR_CALL classified directly from `rt_proc_is_registered` / `rt_builtin_is_known`
  name tables. Writes IR_CALL_PROC_STAGED / IR_PROC_GEN / IR_CALL_BUILTIN into
  `nd->op`. This is the single point that sets call kind; runs after proc
  registration, before emit.
- `bb_call_route_classify` (emit_bb.c:2750): new op-first fast path reads
  `nd->op` (the resolved IR_CALL_* member) before any dval-gated legacy
  fallback. For flat Icon calls the op-first block always fires.

## Verified

- Heartbeat green both modes (hello world, 1+2=3)
- `write(f(3))`→4, `write(abs(-5))`→5, both mode-3 and mode-4 full cycle
- 10/10 broad spread: max(3,7)=7, g(2,3)=5, f(f(1))=3, abs(-5)+1=6,
  f(3)*2=8, reverse("abc")=cba, f(y)=11, repl("ab",3)=ababab,
  integer("42")=42, two-call sequences
- Stash-and-compare confirms while/every/suspend were already EXCISED at
  pristine ec3bd5b3 — no regression.
- Gate HARD=38 (no new mutations added; all fixes are template/driver reads).

## Gate and informational counts

```
A op-writes=29   B field-writes=9   HARD TOTAL=38  (target 0)
C informational: rt_* emit-time queries in emit_bb.c = 20
```

The informational count went 18→20: the two new op-first guards in
`bb_call_route_classify` add `rt_builtin_is_generator` / `rt_builtin_is_known`
checks. These are the same name-table queries as before, relocated to the
op-first block. Full F2/B4 (move classification into LOWER so emitter does zero
rt_* queries) is a later rung.

## State of the conversion-method artifact

Written to `/home/claude/work/CONVERSION-METHOD.md` on the sandbox.
The rung ladder in that file shows this rung closed:
  ✅ IR_CALL with args — flat operand-tmp + call-kind in op field

## What's next (dependency order)

The conversion method is established and mechanical. Per CONVERSION-METHOD.md:

1. **IR_GOTO / IR_IF / IR_CONJ** — already correct via walk_bb_flat fallback;
   convert onto emit_drive_node switch (low risk, confirms JCON ir_a_If wiring).
   op=19 (IR_IF/IR_WHILE — verify exact enum) currently EXCISED by the driver.

2. **IR_TO_BY / IR_EVERY** (op=103/op=18 currently EXCISED) — generators.
   JCON reference: `ir_a_ToBy`, `ir_a_Every` in irgen.icn.
   Edge threading is the critical part (resume port = β in SCRIP).

3. **IR_SUSPEND** (op=28, D1-SUSPEND) — EXCISED. lower_icon.c:210 sets
   dval=1.0; verify emit-readership; convert to ω-wiring or subtag.

4. **D1-VAR-HOPS** — 6 `(int)dval` hop-count reads in bb_call.cpp for
   nested-scope VAR. Move hop count off dval.

5. **D2 / GEN_SCAN** — `s?expr` scan: dval=1.0 + sub-graph smuggling via
   ival → operands[]/flat edges.

6. **GVAR-arith cluster** (~11 →op swaps) → op_gvar_route field. Biggest
   gate drop.

7. **B4** — delete resolve_call_kinds_descr (emit-time rt_* retag); full
   classification into LOWER proc table.

8. **B7** — gate strict 0.

## HEAD state

- SCRIP main: `6058d6f` (pushed 2026-06-29)
- Heartbeat: green both modes
- Gate: HARD=38
- Next session: start rung IR_IF/IR_WHILE/IR_EVERY/IR_TO_BY onto emit_drive_node.
  Read irgen.icn `ir_a_If`, `ir_a_Every`, `ir_a_ToBy` for the 4-port threading.
  Read gen_bc.icn `bc_gen_ir_If`, `bc_gen_ir_Every`, `bc_gen_ir_ToBy` for templates.
  Use the CONVERSION-METHOD recipe (Lower→Driver→Template→Verify).

## PUSH STATUS: COMPLETE

SCRIP: ec3bd5b → 6058d6f pushed to origin/main ✅
.github: this handoff doc pushed to origin/main ✅
