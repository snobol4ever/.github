# FINDING 2026-09-13 hq_R — the mod_op stamp space has THREE ids left, and its compiler/runtime boundary is already breached by seven

**Tree:** SCRIP `7923f78b3` · incremental `make`, `RT_OPT=-O0`. **Measured, not read:** `IR_OP_COUNT` was compiled
and printed, the id space was censused from `descr_tags.inc` by script, and the stamping expression was read.
**Not my lane to cure:** `descr.h` / `descr_tags.inc` / `rtx/*.s` are the shared machine. **ASK, routed to the
ceo for hq_U/cto.** Found while sizing an unrelated cure in my own lane (see below), which is why it is a
finding and not a row.

## What I was doing, and why this stopped me

The ISO char/code I/O builtins do not validate their Char/Code argument (`get_char/1,2`, `peek_char/1,2`,
`get_code/1,2`, `peek_code/1,2`, `put_char/1,2`, `put_code/1,2`): they FAIL silently, or in `put_char`'s case
SUCCEED, where ISO 8.12 wants `type_error(in_character, X)` / `type_error(integer, X)` /
`representation_error(in_character_code)` / `instantiation_error`. That is ~21 cases in six Logtalk groups,
one class. **The 2-arity forms can be cured in C today** — their rtx thunks are `PL_CTX_LEAF_BALL`, and
`PL_IN_LEAF` passes the SAME `cx` down, so a ball written in the shared body is picked up. **The 1-arity forms
cannot**: `rtx_plunify.s:229-232` registers `get_char peek_char get_code peek_code` as plain `PL_CTX_LEAF`,
which drops `cx->ball`. Promoting them needs four new `MOD_OP_*` ids.

## The measurement

```
mod_op is uint8_t (descr.h:59)                 -> the whole space is 1..255
compiler stamps mod_op = IR opcode + 1         (bb_lit_scalar.cpp:18-20, under SCRIP_DESCR_STAMP=1)
runtime sentinels start at 130, "one past IR_OP_COUNT (129, IR.h)"   (descr_tags.inc:50-72, the block comment)
123 runtime sentinels occupy 130..252          -> FREE: 253, 254, 255.  THREE.
IR_OP_COUNT compiled and printed TODAY: 136    -> the comment's 129 is stale by seven
```

⛔ **So the boundary the design rests on is already crossed.** Seven IR ops stamp straight into the runtime
range, and each pair is indistinguishable to any reader of the stamp:

| IR op | stamps mod_op | collides with |
|---|---|---|
| `IR_UNOP` | 130 | `MOD_OP_RT_FAILDESCR` (rtx_misc.s) |
| `IR_UNOP_TEST` | 131 | `MOD_OP_RT_ADD` |
| `IR_VAR` | 132 | `MOD_OP_RT_SUB` |
| `IR_VAR_REF` | 133 | `MOD_OP_RT_MUL` |
| `IR_VAR_FRAME` | 134 | `MOD_OP_RT_SIZE_D` |
| `IR_ASSIGN_FRAME` | 135 | `MOD_OP_RT_LIST_BANG_AT` |
| `IR_LIMIT_GATE` | 136 | `MOD_OP_RT_PROC_VALUE` |

⭐ **The whole point of starting at 130 is stated in the block's own comment: "so a stamp reader can tell
'compiler-stamped IR op' from 'hand-written runtime mint' ON SIGHT."** That property is what is gone. The
execution is unaffected — `mod_op` is provenance, and the compiler side is gated behind `SCRIP_DESCR_STAMP=1`
— so this is a DIAGNOSTIC defect, and it bites exactly when someone is using the diagnostic.

## ⭐ The shape worth keeping: a constant that encodes another file's count, and no instrument on the pair

`130` is `IR_OP_COUNT + 1` **written down once as a literal.** Adding an IR op is a one-line edit in `IR.h`
that silently invalidates a numbering in `descr_tags.inc`, and nothing anywhere reads both. It did not fail
loudly and it did not fail at all — it just stopped being true, seven times.

⚠ **AND I ALMOST FILED THE WRONG NUMBER.** My first census said *132 ids free in 1..255* and I nearly wrote
"the space is comfortable": ids 1..129 are unused **as sentinels** because they are RESERVED for compiler
stamps. The free-looking range is the design, not headroom — a census answering "which ids are unused" when
the question is "which ids may be allocated". Same family as `command -v` answering *is it on PATH* for *does
it exist* (CLAUDE.md), and it is why the table above is boundaries-and-owners and not a count.

## What I am asking for (not proposing — this is the shared machine)

1. **A gate over the pair**, which is the part that keeps this from recurring: assert
   `MOD_OP_RT_FAILDESCR == IR_OP_COUNT + 1` at compile time (a `DESCR_SASSERT` beside the existing ones in
   `descr.h` would make it a build error, not a finding), and assert the sentinel block is contiguous and
   within 255. Either half alone leaves the other silent.
2. **A decision on the space**, because three ids is not room for a class: renumber the sentinels above a
   boundary that is *derived* from `IR_OP_COUNT` rather than typed, or widen the stamp. `DESCR_t` is
   size-asserted at 16 bytes as a SysV register pair (`descr.h:72`), so widening is not free and is exactly
   why this is an ASK and not a patch.
3. **Until then**: my char/code validation class lands its 2-arity half in C with no new id, and the four
   1-arity promotions wait on (2). I will not spend two of the last three ids on one family in my own lane
   at the end of a sitting — an id spent is a decision nobody else can unmake.
