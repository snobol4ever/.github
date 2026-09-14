# FINDING 2026-09-13 hq_R — two orthogonal dimensions were sharing one byte, and the divider between them was a literal that stopped being true seven times

**Tree:** SCRIP (this landing) · incremental `make`, `RT_OPT=-O0`. **Ruling:** ceo CEO-719 and its **two** corrections,
on Lon's word; the cto is HQ. **Gate:** `scripts/test_gate_mint_op_is_one_numbering.sh` — 8 arms, ~0.8s, wired.

## The measurement, and what each number answered

```
mint_op (was mod_op) is uint8_t                         descr.h:59        -> the whole space is 0..255
compiler stamps it in lit_tag_imm                       bb_lit_scalar.cpp -> was (op + 1)
123 MOD_OP_RT_* ids based at 130, "one past IR_OP_COUNT (129, IR.h)"      descr_tags.inc's own comment
IR_OP_COUNT, COMPILED AND PRINTED rather than read:     136               -> the comment was stale by seven
1 (unstamped) + 136 (IR ops) + 123 (rt ids) = 260 in a 256-wide field     -> ALREADY OVER, not running out
```

⛔ **Three things were wrong at once and none of them failed loudly.** The base was stale, so seven IR ops
(`IR_UNOP`, `IR_UNOP_TEST`, `IR_VAR`, `IR_VAR_REF`, `IR_VAR_FRAME`, `IR_ASSIGN_FRAME`, `IR_LIMIT_GATE`) stamped
straight onto `RT_FAILDESCR`…`RT_PROC_VALUE` — destroying exactly the property the base existed to provide, that
a reader can tell a compiler mint from a runtime one on sight. The total was over the field. And the two
populations were never two numberings of one thing at all.

## ⭐ The finding proper: they were ORTHOGONAL DIMENSIONS, and a name is what hid it

`mint_op` answers **which BB minted this descriptor**. The rt ids answered **which runtime function that BB
called** — *"Like BB_CALL, which call?"* (Lon). One `bb_call` dispatches to `rt_add`, `rt_concat`, `rt_size` and
dozens more with the BB identical every time, so the rt id was the only thing telling those mints apart.

**The measurement that settled it:** of the 123 ids, **118 have no IR-op counterpart by name** — there is an
`IR_BINOP` but no `IR_ADD`, an `IR_MAKE_LIST` but no `IR_LIST_BANG_AT`. They name runtime *helpers a BB calls*,
not BBs. I filed that as a question ("how can these stamp the BB op they are?"); it turned out to be the answer.

⭐ **And the field's NAME is why this happened twice.** `mod_op` reads as *modified*. A byte that records *who
minted* but is named *modified* does not look like one numbering with one meaning — so a second population with
a divider between them looked necessary, first to whoever added the 130 block, then to the ceo an hour before
this landing. The divider was the literal that went stale. **The rename is not cosmetic: it is the cure for the
thing that produced the defect.**

## The cure

`mint_op`: **0 = unstamped, 1..IR_OP_COUNT-1 = the minting BB/IR op**, and nothing else. The 123 ids are gone;
the enum starts at 1 so `mint_op == opcode` with no arithmetic to drift; the 49 direct asm mint sites and
`PL_CTX_LEAF_BALL`'s 46 uses fold **nothing** into their tag immediate, keeping the one-instruction mint the
design was bought with (`mov eax, DT_I | (MOD_OP_RT_ADD << 8)` → `mov eax, DT_I`). `IR_OP_COUNT` is 137, so 119
values are spare. **A helper-minted descriptor now reads 0, UNSTAMPED, which is true of it.**

⛔ **The loss is real, deliberate, temporary, and named where the reader will be.** Lon accepted it in those
terms — *"We can do without that granularity for now until we figure something else."* A reader chasing a bad
descriptor keeps *which BB minted this* and loses *by calling which runtime function*. Its home, when someone
finds one, is **its own storage and never this byte**: N values for which-rt added back here re-creates the
260-in-256 overflow. That text lives in the **assert's own failure message** and in `descr_tags.inc` where the
ids used to be — ⭐ the message rather than a comment because `src/` carries a zero-comment invariant, which
turned out to be the better placement anyway: a string the compiler prints when the guard fires reaches the
person who tripped it, and a comment only reaches someone already reading the file.

## ⛔ An assert nobody has seen fail is an absence-assertion

The cto's condition, and it is the sharpest sentence of the exchange: *it passes forever and nothing in its
output distinguishes it from the day it stopped being wired.* So `DESCR_SASSERT(IR_OP_COUNT <= 255, …)` was
**proven to fire** — `IR_SCRATCH_OVERFLOW_PROOF = 300` added before `IR_OP_COUNT`, one translation unit, gcc
refused quoting the whole message, reverted, recompiles clean. And the gate carries that proof permanently as
**ARM 3b**: it compiles a *deliberately violating* assert through the same macro and reds if the compiler
accepts it, because a `DESCR_SASSERT` quietly defined empty would pass ARM 3a forever while guarding nothing.

## ⭐ And a second instrument was dark the whole time

Making `rtx_unit_test` the gate's binary arm found that `scripts/test_rtx_unit.sh` compiles with
**`-Isrc/contracts`, a directory deleted in the 2026-08-24 srcreorg**. Three of its four differential batteries
— `rtx_unit_test`, `rtx_str_test`, `rtx_varval_test` — **had not compiled since**, each printing `BUILD FAIL`
into a runner that nothing wires into `make test`. ⭐ **The fourth kept passing**, because the alloc battery
includes no header from the moved directory — so the runner still printed a PASS line and looked alive, which
is why three weeks of nobody noticing was easy. One flag: all four build and pass, 8492 cases, 0 mismatches.
That is what makes the gate's ARM 6 a claim about the **binary** (the asm faildescr mint is compared bit-for-bit
against its C golden, this byte included) rather than a grep over source.

⚠ **Three dead proposals, recorded so nobody re-walks them** (CEO-719): merging the per-language IR ops is
backwards — separate `IR_KW_ICON`/`IR_CALL_SNOBOL4` are the pure no-switch form and merging would *create* the
language switch the law forbids; `src_node` cannot hold the stamp because it is the BB node id and 16 bits is
already too small; bit fields cannot be portably targeted by 49 hand-written asm mints.
