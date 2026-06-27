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

---

## ATTEMPTED FIX — TWO DEAD ENDS (tried this session, REVERTED; documented so they are not repeated)

After landing the `is_resumable` prereq I attempted the full resume-spine fix on top. Both pieces
REGRESSED and were reverted to the clean `8b4ab8c` checkpoint. The repros (`every (x:=(1|2|3|4|5))>2 &
write(x)` → want `3 4 5`; `every ((1|2|3|4|5)>2) do write("y")` → want `y y y`) ALL went green with the
combined change, but the suite fell 208→198 (run) / 195 (compile, m3≠m4 asymmetry = red flag), net −10.

### Dead end 1 — lower a generator-wrapping binop as `IR_BINOP_GEN` (`lower_icon.c:138`)
```c
if ((t->n > 0 && is_resumable(t->c[0])) || (t->n > 1 && is_resumable(t->c[1]))) op->op = IR_BINOP_GEN;
```
This DID make the WITH-body form work (`every ((1|2|3|4|5)>2) do write("y")` → `y y y`) because the
emitter's `IR_BINOP_GEN` dispatch routes to `flat_drive_binop_gen_tree` (emit_bb.c:1651), whose resume
machinery is correct. BUT it is too broad: it also converts **arithmetic**-generator binops that the
plain `IR_BINOP` path was already handling, and those now loop forever (rc=124) — the whole
`rung02_arith_gen_*` family (nested_add, nested_filter, paper_mul, relfilter), `rung01_paper_*`,
`rung36_jcon_primes`, `rung10_augop_break_repeat`, `rung02_proc_locals`. The `flat_drive_binop_gen_tree`
RHS-fail→lhs_β / binop-β→rhs_β wiring does NOT terminate for these shapes.
**Narrowing needed:** convert to `IR_BINOP_GEN` ONLY for relational ops (BINOP_LT..NE) with a generator
operand — NOT arithmetic/concat — AND prove `flat_drive_binop_gen_tree` terminates for the relop-filter
shape. Test the full `rung02_arith_gen_*` family after ANY change here; they are the canary.

### Dead end 2 — report the generator's resume as the conjunction's β (`lower_icon.c` TT_SEQ, ~line 246)
```c
if (lr >= 0 && val[lr]) last_beta = val[lr];   /* lr = last resumable element index */
```
Intended to fix the `every EXPR` (no-do) `!BODY` path: `lower_every`'s `!BODY` branch collapses
`loop_target` to E because the conjunction reports `cx->beta == E` (the rightmost element `write` is
non-resumable so its β is the outer fail = E), so `gen_node == gen_result == CONJ` and the
success-loop-back never drives the generator. Setting the conjunction's β to the last resumable
element's value node DID make `every (G>2) & write(x)` (no do) → `3 4 5`. BUT it changes resume
reporting for ALL conjunctions and created infinite-loop cycles in the same `rung01/rung02` families.
**This is the harder half.** The `every EXPR` no-do form needs the canonical transform `every E` ≡
`every E do &fail` (body always fails → body.failure drives the generator), reusing the WORKING
WITH-body machinery — NOT an ad-hoc β override. The WITH-body path already produces correct loop-back
(`write.γ → ALT` directly, verified in IR). Synthesize a fail-body for the no-do every and route it
through the existing `BODY` branch, computing `loop_back` as the inner generator's resume (the part that
is currently wrong for a compound/conjunction GEN — `gen_node` resolves to `gen_result` instead of the
buried generator). `cx->last_gen` is only set for IR_TO/IR_TO_BY (lower_icon.c:393), so it does NOT
locate the buried ALT/BINOP_GEN — that tracking would need extending, OR walk gen_result's operand chain
to find the generator node.

### Net lesson
The emitter side (`flat_drive_binop_gen_tree`, `g_limit_gen_beta` pattern) is READY. The blocker is
PURELY in `lower_icon.c`: (a) selecting EXACTLY the right binops for `IR_BINOP_GEN` (relops-with-gen
only, proven-terminating), and (b) the `every EXPR` no-do loop-back for a compound generator expr. Both
must be validated against the full `rung02_arith_gen_*` + `rung01_paper_*` canary set (11 programs that
hang if you get it wrong), not just the target repros. The target repros going green is NECESSARY but
HUGELY INSUFFICIENT — every attempt this session passed the repros and still regressed 10 programs.
