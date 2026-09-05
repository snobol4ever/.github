# FINDING 2026-09-05 hq_B — `<->`'s undo was emitted but unreachable: `is_resumable()` omits `TT_REVSWAP` while `ir_is_generator_kind()` includes `IR_REV_SWAP`

**Seat:** hq_B (Icon lane) · **Tree:** SCRIP `761eb9353` + this cure · corpus `551c824f8` · RT_OPT=`-O0` · incremental `make`
· oracle `/home/resources/icon-master/bin/{icont,iconx}` v9.5.25a

**Builds on** `FINDING-2026-09-05-seat01-icon-reversible-exchange-operator-does-not-undo-on-resume.md`, which
established the symptom and the book contract (App. D p.302-303) and correctly noted that a dedicated box
already exists. This finding supplies the root cause, which is not in that box, and the cure.

## The symptom, reproduced independently

    i := 1; j := 2;
    if (i <-> j) & &fail then write("never");
    write("B ", i, " ", j);

oracle `B 1 2` (the exchange is undone on resumption) · SCRIP `B 2 1` (not undone). A plain `:=:` control in
the same program gives `2 1` on both sides, so the witness discriminates. seat01's corpus witness (entry 760,
`every (1 to 2) & (x <-> y)`) is the same defect through a different driver.

## Why the obvious suspects are all innocent

⭐ **The runtime is correct.** `rt_rev_swap_fwd` saves both operands into `save[0]/save[1]` before swapping and
`rt_rev_swap_undo` restores them and returns FAILDESCR (`src/runtime/builtins/gen_runtime.c`). Nothing to fix.

⭐ **The box is correct.** `bb_rev_swap.cpp` emits α→`rt_rev_swap_fwd`, then γ, then β→`rt_rev_swap_undo`→ω —
structurally identical to `bb_rev_assign_var.cpp`, which works.

⭐ **The lowering builds the box and marks it.** `TT_REVSWAP` builds `IR_REV_SWAP` and sets `cx->beta = nd`.

⭐ **`IR_REV_SWAP` is already in `ir_is_generator_kind()`** (`src/optimizer/ir_query.c`), so `icn_gen_wiring()`
would wire an ω into its β correctly — if anything ever asked it to.

## The actual defect: the undo is dead code

The emitted assembly names it exactly. In one program containing both operators:

    $ grep -c 'n10_rev_swap_β'   rev.s   ->  1     (its own definition; NOTHING jumps to it)
    $ grep -c 'n40_rev_assign_β' rev.s   ->  3     (defined and targeted; this is why `<-` works)

`--dump-ir` shows where the two diverge. Both programs have the identical shape — `&fail`'s ω goes to a GOTO
wiring node — but the GOTO's destination differs:

| operator | `&fail` ω → | that GOTO targets | result |
|---|---|---|---|
| `<-` (works) | `18@` | node **12**, the `REV_ASSIGN` box → its β | undo runs |
| `<->` (broken) | `21@` | node **6**, the enclosing `DISJUNCTION` | box skipped entirely |

`lower_icon.c`'s conjunction arm chooses that destination at `:700-702`:

    IR_t * tgt = ω; if (lr >= 0) tgt = (bet[lr] && bet[lr] != ω) ? bet[lr] : val[lr];
    ...
    if (is_resumable(S[i]) || icn_tree_is_cursor_mover(S[i])) { lr = i; ... }

`lr` is the index of the last operand believed resumable. If nothing sets it, `tgt` stays `ω` and the failure
path routes *past* the box. And `is_resumable()` at `:95` reads:

    case ... case TT_UNTIL: case TT_REVASSIGN: case TT_ITERATE: return 1;

**`TT_REVASSIGN` is listed. `TT_REVSWAP` is not.** Both operators are reversible-on-resumption by definition;
one was enumerated and its sibling was missed.

## The cure

Add `case TT_REVSWAP:` to `is_resumable()`. One token. `lr` is then set, `tgt` becomes the box, and because
`IR_REV_SWAP` is *already* a generator kind, `ω_to()` routes to β — the undo that was always being emitted
finally has an inbound edge.

VERIFIED both modes, byte-identical to iconx: my `& &fail` witness (`A 1 2 / B 1 2 / C 2 1 / D 5`, where C is
the `:=:` control that must stay swapped and D the `<-` arm that already worked) and seat01's corpus witness
760 (`1 2 / 2 1 / 2 1 / 1 2`, no longer byte-identical to its `:=:` control).

## ⭐ The reusable half: two tables that answer the same question and disagree

`ir_is_generator_kind()` (IR kinds) and `is_resumable()` (parse-tree kinds) both encode "can this be resumed".
`IR_REV_SWAP` was in the first; `TT_REVSWAP` was missing from the second. **Neither table can detect the other's
omission**, and the disagreement is silent in the most dangerous possible way: the box is still built, its undo
code is still emitted, the label is still defined — everything looks present in the source, in the IR dump, and
in the assembly. Only the *absence of an inbound jump* betrays it, and nothing counts inbound jumps.

This is the same family as the by-name `!` defect cured in the same sitting
(`FINDING-2026-09-05-hq_B-the-bidlen-guard...`): a correct implementation that some caller never reaches. The
cheap detector, if anyone wants a gate: for every box whose template emits a β port, assert its β label is
referenced at least once in the emitted `.s`. A defined-but-never-targeted port is dead code with a plausible
alibi, and it will always read as "implemented" to a grep.
