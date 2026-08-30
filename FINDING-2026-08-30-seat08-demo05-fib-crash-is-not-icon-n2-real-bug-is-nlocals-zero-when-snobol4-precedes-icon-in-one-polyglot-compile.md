# FINDING: demo05/fib.scrip's crash was mischaracterized for 3 sessions as "icon-n2-generator-activation-
# frames" (now DONE and did not fix it) — the real bug is a different, previously-unidentified defect:
# Icon's `local` declarations register zero names when a SNOBOL4 section compiles first in one polyglot file

**Who/when:** seat08, 2026-08-30, `scrip-polyglot-demo-icon-semicolon-5-files` row. `icon-n2-generator-
activation-frames` (QUEUE.tsv: DONE) landed this session — genuinely fixed the class of bug it targeted (see
Part 1) — but demo05/fib.scrip still crashes identically, because that was never the actual cause.

## Part 1 — icon-n2-generator-activation-frames's own fix is REAL and verified working in isolation

Extracted `fib.scrip`'s exact Icon section (the `fibs()` generator: `local a,b; ... repeat { suspend a; a:=:b;
b+:=a; }`, driven by `every write(fibs() \ 10)`) into a standalone `.icn` file. **Runs correctly, byte-for-byte
matching the expected Fibonacci sequence.** The narrower case (`suspend` alone, no swap) also now works. The
landed fix is not the problem — every prior session's link to it was the wrong lead, not a wrong fix.

## Part 2 — the crash is real, but the "IR op=122 has no template" message is a guard-sink, not a missing op

Every session on this row (seat05, seat06, and an earlier pass by this same seat this session, per this row's
own LEDGER) cited `FATAL emit_drive: IR op=122 has no template` at face value. **The driver's own message text
explicitly warns against this**: *"this is also the guard sink inside existing cases — if op=N plainly has a
case, the BACKTRACE LINE (not this message) names the failing guard."* Nobody checked. A real gdb backtrace on
the actual file:
```
#5 drive_unowned (nd=0x489d10) at emit.cpp:1455
#6 emit_drive (nd=0x489d10, ...) at emit.cpp:1863
#7 codegen_flat_chain_body (entry=0x48a010, prefix="proc_fibs") at emit.cpp:3261
```
`emit.cpp:1858-1863`:
```cpp
case IR_SWAP: {
    IR_t * xv = ...; IR_t * yv = ...;
    int sa = xv ? bb_varslot_peek(IR_LIT(xv).sval) : -1;
    int sb = yv ? bb_varslot_peek(IR_LIT(yv).sval) : -1;
    if (sa < 0 || sb < 0) { drive_unowned(nd); break; }   // <-- the actual guard that fires
    ...
}
```
**Op 122 is `IR_SWAP` (verified by indexing the enum programmatically, not by hand-count) and it plainly has a
case.** The guard fires because `bb_varslot_peek("a")`/`("b")` — the swap operands in `a :=: b` — can't find a
slot. This is a completely different bug class than "missing template," and has nothing to do with generator
activation frames.

## Part 3 — isolated to SNOBOL4 preceding Icon in one polyglot compile, not Icon+Prolog or Icon alone

Built the same real Icon section into three different combinations, using the FILE'S OWN real section content
(not simplified rewrites, which the first attempt used and which misleadingly did NOT reproduce it):
- **real SNOBOL4 + real Icon** (no Prolog): **CRASHES**, identically.
- **real Icon + real Prolog** (no SNOBOL4): runs clean, correct Fibonacci output.
- **all three** (the actual file): crashes, as always reported.

**A trivial hand-written SNOBOL4 section (`a=0 b=1 OUTPUT=a END`, no label/loop/keyword-assign) did NOT
reproduce it** when substituted for the real one — whatever triggers this needs the real section's specific
shape (a labeled loop with `:F()`/`:( )` goto-style control flow, `&CASE`/`&TRIM` keyword assignments, or
simply being non-trivial); not narrowed further than "the real section, not any two-line stand-in."

## Part 4 — root cause pinned to the exact field, via a live (not post-mortem) breakpoint

Broke at `drive_unowned` on the SNOBOL4+Icon combination and inspected the live state:
```
g_emit_cfg->entry == entry (0x471fb0)          -- CONFIRMED the right graph (fibs' own), not a graph mix-up
g_emit_cfg: nparams=0 pnames=NULL nlocals=0 lnames=NULL vslots=NULL n_vslots=0, icn_cells_graph=1
xv: IR_VAR sval="a"     yv: IR_VAR sval="b"
```
**`fibs()`'s own `IR_graph_t` has zero registered locals/params, confirmed to be the correct graph object, even
though its source declares `local a, b;`.** This is not a lookup bug and not a wrong-graph bug — the
declaration itself was never recorded into `nlocals`/`lnames` for this graph, only when a SNOBOL4 section
compiles first in the same process. `src/lower/lower_icon.c:1271` is where `g->nparams`/`g->nlocals`/
`g->lnames` get set from an accumulator (`lnv`) built while parsing the procedure — not traced further this
pass (see NEXT ACTOR): unclear whether `lnv` itself ends up empty, or this line's branch (`pd->n > 2 &&
pd->c[2]`) is skipped entirely for this graph in this context.

## Not attempted

No fix, no source touched (`git status --short` clean across all three repos). This is a shared lowering-stage
defect (Icon local-declaration registration interacting with prior SNOBOL4 compilation in the same process) —
out of scope for a semicolon-fixing row regardless of size, matching this row's own established precedent
(seat05 minted two new Prolog rows for out-of-scope bugs found the same way, rather than fixing them here).
Minting a new row for this rather than re-using `icon-n2-generator-activation-frames` (now DONE, on a fix that
demonstrably isn't the cause) or inventing a fix here.

## Suggested next step, not decided here

1. Trace `lower_icon.c`'s handling of `fibs()`'s procedure declaration specifically in the SNOBOL4+Icon merge
   context: is `lnv` (the locals accumulator) populated correctly but never reaching line 1271's assignment
   (branch not taken), or is it reaching the assignment already empty? A breakpoint on `lower_proc_body` itself,
   comparing the SNOBOL4-present vs. SNOBOL4-absent compiles, would settle it directly.
2. Narrow which part of the real SNOBOL4 section actually matters (the label, the `:F()`/`:( )` goto syntax,
   the keyword assignments, or just "more than one statement") — not done this pass, flagged as open.
3. Once fixed, this unblocks demo05 entirely (Part 1 already confirms the Icon side is otherwise correct) —
   demo05's Prolog section (`between/3` backtrack crash) is a SEPARATE, already-tracked blocker
   (`prolog-between-generator-backtrack-crash`), independent of this one.
