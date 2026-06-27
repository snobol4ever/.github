# HANDOFF: ICON-BB is_resumable(binop-over-generator) prerequisite + resume-spine frontier pinned

**Date:** 2026-06-27
**Model:** Claude Sonnet 4.6 (Opus-class session)
**Baseline HEAD (SCRIP):** fc64cac — m3/m4 PASS=208 FAIL=44 EXCISED=1
**This commit:** is_resumable extension only — PASS=208 FAIL=44 EXCISED=1 (ZERO regression, ZERO new pass)
**Status:** behavior-neutral PREREQUISITE landed; the resume-spine fix it unblocks is NOT done (frontier documented below).

---

## What landed (1 file, 2 lines)

`src/lower/lower_icon.c` — `is_resumable()` now recognizes two additional resumable shapes,
matching canonical `irgen.icn`:
- a binop/relop (`lc_is_binop`) is resumable iff ANY operand is resumable — canonical `ir_binary`
  re-drives `p.right.ir.resume` on operator-failure, so `(GEN) > k`, `(GEN) + k`, `(GEN) || s` etc.
  are generators.
- `x := GEN` (TT_ASSIGN of a generator) is resumable iff its RHS is.

Before: `is_resumable` returned 0 for any `TT_GT`/`TT_LT`/.../`TT_ADD`/`TT_CAT` node, so the
TT_SEQ (`&` conjunction) backtrack-chaining (`lower_icon.c:244`, the `ω_to(val[i], val[lr])` pass)
never treated a relop-over-generator as a resumable element and never wired the fail-edge back to it.

After: the backtrack ω-edge IS now wired (verified in IR dump: `write.ω → relop`, `relop.ω → ALT`).

## Why it is a PREREQUISITE and not a fix (zero new pass)

The change is necessary but not sufficient. The canonical-correct backtrack edges are now present in
the IR, but they target **fresh (α) entries**, not **resume (β) entries**, so the generator is never
re-driven. This is the SAME "binop operand resume / node identity" frontier flagged as NEXT in the
12f0656 and 61f8836 watermarks. Now pinned exactly:

### The repro (rung13_alt_alt_filter, and the whole binop-over-gen family)
```
every (x := (1|2|3|4|5)) > 2 & write(x)     # emits 3, want 3 4 5
every (1|2|3|4|5)        > 2 & write("y")    # emits y, want y y y
```
Isolation proven: `every x:=(1|2|3|4|5) do write(x)` → 1 2 3 4 5 (plain alt-in-every works);
only the **relop-over-generator** form drops every result after the first qualifying one.

### Root cause (exact, with the line)
`src/emitter/emit_bb.c:codegen_flat_chain_body`, the per-node ω-wiring loop (~line 3665):
```c
for (k...) if (nodes[k] == otgt) {
    node_ω = (i > k && ir_is_generator_kind(nodes[k]->op)) ? betas[k] : lbls[k]; ... }
```
The loop-back/backtrack edge routes to the target's **β (resume)** label ONLY when the target is an
`ir_is_generator_kind`. The relop is a plain `IR_BINOP` (NOT a generator kind — see
`ir_is_generator_kind`, emit_bb.c:2366), so `write.ω → relop` lands on the relop's **α (fresh)**
entry → relop recomputes `x > 2` with the SAME x → the ALT is never resumed for 4, 5.

For `every EXPR` (no `do` — the AST is `TT_EVERY(TT_SEQ(relop, write))`, BODY=NULL), the
`lower_every` `!BODY` branch computes `loop_target` from `gen_node`; the conjunction reports
`gen_node == gen_result == CONJ` and `cx->beta == E`, so `loop_target` collapses to E (the EVERY
exit) and there is no success-loop-back at all. (Instrumented + confirmed: `[EVERY!BODY] gen_node ==
gen_result (op=16 IR_CONJ), cx->beta == E`.)

### The fix (next session — the actual lever)
The architecturally-aligned move is to make a binop that WRAPS a generator lower/classify as
`IR_BINOP_GEN` (already a generator kind everywhere — `ir_is_generator_kind`, `binop_operand_streams`,
scrip.c:61), so the chain walker routes its loop-back to the inner generator's β. `IR_BINOP_GEN` is
currently produced by NO lowerer (grep: only referenced in classifiers), so wiring it requires:
1. LOWER (`lower_icon.c`): when an `IR_BINOP`'s operand subtree is resumable (now detectable via the
   `is_resumable` landed here), emit `IR_BINOP_GEN` (or tag the node) AND ensure the binop box's β
   re-drives the inner generator's β (the "binop operand node identity" bug: the operand node stored
   via `bb_operand_aux_set` must be the SAME instance emitted as the chain entry — see 61f8836
   handoff §NEXT; `descr_binop_set_slots` slot=-1 on the duplicate clone is the tell).
2. EMIT (`emit_bb.c`): `bb_binop` resume arm must, on β, jump to the operand-generator's β rather than
   recompute α. The `to_inner_gen_operand_k` helper (emit_bb.c:2377) is the model — it already finds a
   generator operand's chain index for IR_TO; generalize the same lookup for IR_BINOP_GEN.
3. Verify the `every EXPR` `!BODY` path: once the conjunction's `cx->beta` is a real resumable β
   (not E), `loop_target` will resolve to it and the success-loop-back appears.

Landing this closes rung13_alt_alt_filter, rung13_alt_alt_cross_arg_sideeffect, and contributes to
several rung36_jcon_* (numeric/augment use `image(GEN) | "none"` patterns).

## Current FAIL cluster map (all 44, at fc64cac — re-tallied this session)

| Count | Cluster | Tractability |
|-------|---------|--------------|
| 16 | `bb_call: unsupported call shape fn=<X>` | distinct builtins: tab(2) move(2) any match open(2) display remove o(2) p ?(2) goal — NOT one fix; several need file I/O or coexpr |
| 10 | wrong-output rc=0 | heterogeneous: some need stdin read() (meander/roman → 0 lines w/o pipe), some the binop-gen resume family above, some content drift |
|  5 | `flat_drive_rasgn: x<-v requires IR_VAR lvalue` | the lvalue is a SUBSCRIPT (`arr[r] <- 1`) — needs a REVERSIBLE subscript-assign box (save elt, store, suspend, restore-on-resume), per canonical oasgn.r GeneralAsgn; NOT a small generalization |
|  4 | segv rc=139 | rung30, jcon lexcmp/lists/mindfa — need gdb |
|  2 | `bb_assign_local: needs descr flat-chain` | jcon kwds/wordcnt |
|  1 each | `bb_section s[i+:n]/s[i-:n]`, `bb_unop LIT_F/NUL`, `bb_binop_relop shape`, `bb_var arm`, `flat_drive_swap` (keyword swap), unresolved-fwd-ref (kross, 6 refs), find-gen hang rc=124 | singletons |

**Honest headline:** there is NO single dominant tractable lever. The biggest count (16 call-shapes)
is 11 distinct builtins. The binop-gen-resume fix above is the cleanest *next* lever because it is
canonical, self-contained, and the diagnosis is now complete — but it is real lower+emit work, not a
one-liner.

## Validation done this session
- Full suite both modes: PASS=208 FAIL=44 EXCISED=1 (identical FAIL SET to baseline — `diff` empty).
- icon smoke 12/12 m3+m4 · prolog 5/5 · snobol4 7/7.
- All 4 icn discipline gates green (no-stack 0, one-reg 0, semicolon prison, local-no-nv).
- `update_icon_bench_asm.sh`: updated=0 (byte-identical); the 11 compile-errs are PRE-EXISTING
  (confirmed by stashing the change and re-running on the baseline binary — identical 11/1 result).

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
