# FINDING: Pascal's display now covers lexical levels beyond 3 — frame-resident, no new pinned register, no new global variables; a real mid-implementation bug (IR operand count silently shifting an unrelated slot number) found and fixed via gdb before landing

**seat09 · 2026-09-03 · row `pascal-uplevel-nested-proc-hang`**

## 0. The defect and the constraint

`bb_var_frame.cpp`/`bb_assign_frame.cpp` implemented Pascal's non-local ("uplevel") variable access
via a classic display, but the display was exactly three registers (`r13`/`r14`/`r15` for lexical
levels 1/2/3), with a deliberate, loud bomb — `PAS-DISPLAY L>=4 fallback unimplemented` — for anything
deeper. hq_P's prior investigation (kept in the task file's `## SUPERSEDED-NEXT`) bracketed this
precisely (levels 1-3 clean, 4+ SIGABRT, no intermediate degradation) and named the constraint that
rules out the obvious fix: `r12`/`r13`/`r14`/`r15` are *also* Prolog's quad registers (TR/B/ROOT/BALL,
`ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § A.1). Taking `r12` as a fourth Pascal display level would put
a Pascal write on Prolog's trail register the day a graph reaches both. hq_P's own prescription: "a
real display — spilled into the activation frame (ζ-ACTIVATION-FRAME), indexed by level — NOT a
fourth pinned register... removes the arbitrary depth-3 ceiling instead of moving it to 4."

**Cross-checked against § A.1 itself (line 73, read after implementing, per ceo's routing) — this
design is independently RULED there, verbatim: "the Pascal cure for L≥4... is RULED a frame-resident
display — ζ-ACTIVATION-FRAME, indexed by level, per Lon's FRAME-PLACEMENT CRITERION — never a fourth
display register and never r12." What's built here matches.** § A.1 also notes the one existing point
of care around this exact area — Pascal's `[kt-40]` display-save slot in the shared zframe prologue,
and that Prolog's own header carve is deliberately keyed on `zframe_pinned_base` rather than
`zframe_graph` generally so as not to collide with it — unaffected by this row, since this fix reuses
`[kt-40]` exactly as it already existed for the save/restore role.

## 1. The design

**Key invariant, already implicit in how the existing 3-register display works**: a level-L (L>3)
procedure's immediate lexical parent chain reaches a *unique*, statically-known level-3 ancestor
(walk `PAS_PARENT` exactly `L-3` times — `PAS_PARENT` already existed, built at lower time from
declaration nesting). By Pascal's scoping rule, that ancestor's activation is *always* live on the
call stack whenever any level-4+ descendant runs (you cannot call into a nested procedure except from
within its lexical parent's text, transitively) — and since level 3 is the deepest level still
holding a register, `r15` *already* points at exactly that ancestor's frame whenever it matters, with
zero extra bookkeeping.

So: every level-3 procedure's own frame reserves 13 extra named slots — `__pas_display_4` through
`__pas_display_16` (16 = the parser's own `PAS_NEST_MAX`, not a number chosen for this row) —
registered through the *same* vslot mechanism real local variables already use
(`zeta_storage.c::zls_build`, gated strictly on `g->zframe_graph && !g->icn_cells_graph &&
g->decl_level==3`, so Icon — which sets `icn_cells_graph` — and every other language are categorically
excluded from ever reserving this space). A level-L (L>3) procedure's own prologue/epilogue
(`xa_flat.cpp`) saves the caller's old value, sets `[r15+offset(L)]` to its own frame, and restores on
exit — the identical shape the existing register save/set/restore already has, just addressed through
memory instead of a register. A reader of a level-L variable resolves its *owner's* level-3 ancestor
by name (new `stage2_owner_l3_ancestor`, mirroring the existing `stage2_owner_varslot`) and adds one
indirection: load the display pointer from `[r15+offset]`, then read/write through it exactly as the
existing L≤3 path already does through a bare register.

Levels 1-3 are byte-for-byte unchanged — confirmed, not assumed (see § 3).

## 2. A real bug, found before it landed

The first implementation carried the level-3-ancestor's name as a *second* IR operand on
`IR_VAR_FRAME`/`IR_ASSIGN_FRAME` nodes, mirroring how the owner name is already carried as operand 0.
This compiled and linked cleanly, and levels 1-3 still worked — but `deep5`
(`program_procedure_nested_1`) printed `33 22 11 66` instead of `44 33 22 11 110`: correct for the
three level ≤3 values, wrong for the level-4 one and everything downstream of it.

Root-caused via gdb on the assembled mode-4 binary (ASM-DIFF-FIRST, not guessed): the RHS value for
`d := d + 4` was produced by a `BINOP` node into `[rsp+288]`, but the following `ASSIGN_FRAME` node
read its "value to write" from `[rsp+272]` — an offset *never written anywhere in the compiled unit*.
Sixteen bytes, exactly one cell, and exactly the size of the extra operand added. Something in the
emitter's slot-numbering machinery is sensitive to `nd->n_operands` (or operand identity) in a way not
fully traced here — the fix was to stop needing it, not to find the exact sensitive line.

**Cure**: don't carry the ancestor name through IR structure at all. It's derivable at emit time from
the *owner* name, which was already correctly threaded and completely unchanged (`_.op_a_sval`) — via
a new stage2 lookup, `stage2_owner_l3_ancestor(proc)`, reading `IR_graph_t::l3_ancestor_name` (a field
populated once per procedure at lower time, sibling to the existing `decl_level`). Zero new IR
operands. Rebuilt: `deep5` now prints `44 33 22 11 110`, matching hand-derivation exactly, and every
other witness (below) is clean.

**Worth flagging for whoever next adds an IR operand to a node type that already has staged
`_.op_a_*`-shaped fields**: read how `emit.cpp` stages `op_a_slot`/`op_a_sval` etc. from
`operands[0..n]` before assuming operand count is free. It silently isn't, at least here.

## 3. Verification (`make pristine`, `-O0`, this session)

- `nest2.pas` (levels 1-3 only): output byte-identical to `.ref` — the existing fast path is untouched.
- `uplevel2.pas`/`uplevel3.pas` (this row's own DONE-WHEN witnesses, `corpus/benchmarks/pascal/`):
  correct output (`240000000`), where they previously bombed (`SIGABRT`, `PAS-DISPLAY L>=4`).
- Hand-built `nest3`..`nest7` (lexical levels 2 through 6, one variable per level, innermost
  reads/writes every enclosing level): every printed value matches hand-derived arithmetic exactly at
  every depth tested — the fix generalizes, it isn't a level-4-only patch.
- `program_procedure_nested_1` (`deep5`, master-suite entry, a level-5 reader against a level-4
  owner — this row's own bracketing witness): `44 33 22 11 110`, matching by hand.
- `test_gate_pascal_m3.sh` at commit `ec838eb2` (SCRIP `54536fbf` base, pre-rebase): **163/163,
  FAIL=0** (was 162/163 — `deep5` was the sole failure). `test_gate_pascal_m4.sh`: **154/154, FAIL=0**
  (was 153/154 — `deep5` was a `CRASH signal 6`). Both gates fully green at that commit — the first
  time this row has ever cleared them.
- SNOBOL4 blocking corpus (`test_corpus_snobol4.sh`): **1679/1679 PASS both modes**, unmoved. Checked
  because this fix touches `zeta_storage.c`, which is SNOBOL4-shared code — not because anything
  suggested a regression.
- Icon rung suite (`test_icon_rung_suite.sh --mode all`), measured twice: **264/6/1/27 of 298**
  immediately after this fix (pre-rebase, all three modes byte-identical to the then-standing FLEET-12
  watermark), and **264/6/1/26/1(XPASS) of 298** after `git pull --rebase` landed concurrent Icon work
  (one XFAIL moved to XPASS — an unrelated improvement from that work, not this row's). PASS/FAIL
  counts unmoved by this fix in both measurements. The `zframe_graph && !icn_cells_graph` gate is the
  argument for why Icon can't be affected by this row; the two measurements bracketing a large
  concurrent Icon push are the direct empirical confirmation.

## 3.5. A separate, unrelated regression surfaced by the same rebase — not this row's

`git pull --rebase` (landing `bc3b2075..d24e99d8`, including concurrent Icon work) also introduced 5
NEW Pascal m3 failures: `program_array_packed_5`, `program_array_packed_replace_{1,2,3}`,
`program_procedure_array_3` — all `Run-time error 102: numeric expected` on packed-array/string
comparison operators (`<`/`<=`/`>`/`>=`/`=`/`<>`). **Confirmed unrelated to this row**:
`program_array_packed_5` (`chararrcvc`) declares zero procedures, so none of this fix's
`decl_level`-gated code can execute for it at all; timing-isolated (149/149 pass immediately
pre-rebase, 144/149 immediately post-rebase, no Pascal-touching commit in between per `git log` on the
touched files). Reported to hq_P as `q-pascal-array-packed-regression-post-fleet12-icon-commits`; not
investigated further here since it's outside this row's lane. **This row's own DONE-WHEN (§ 5) is
therefore written to check only what this row is responsible for** — this exact incident is why.

## 4. Governance

No new global variables. All new state: one field on the already-shared `IR_graph_t`
(`l3_ancestor_name`), vslot table *entries* (data in the pre-existing `zv[]` table real locals already
populate, not a new table), and one function-local `static` string-formatting memoization
(`zls_pas_display_name` in `zeta_storage.c`) — fully encapsulated, never read outside its own
function, matching a `static int x=-1; if(x<0){...}` pattern already used dozens of times in that same
file for cached env-var/formatted lookups. None of this is the file-scope, cross-function
"stage-then-consume" state RULES.md's NO-NEW-GLOBALS rule is aimed at (the class the sibling row
`pascal-relop-into-array-and-field-lvalues-loses-value` needed, and got, an explicit ruling on).

## 5. Housekeeping fixed along the way

This row's own `DONE-WHEN` cited `/home/claude16/corpus/programs/pascal/bench` (a different seat's
clone, at the pre-re-grid path) with no `|| exit 2` guard on the `cd` — a missing path made the whole
criterion silently exit 0 regardless of the row's true state. ceo flagged this exact defect in the
task file's `## QA` on 2026-08-27, but it was never actually corrected. Rewritten to use `$S4E_HOME`,
the correct path (`corpus/benchmarks/pascal/`), and to check actual output correctness rather than
"didn't crash" alone — the same vacuous-DONE-WHEN class this seat also found and fixed on the sibling
row `pascal-relop-into-array-and-field-lvalues-loses-value` earlier this session (see that row's own
FINDING). Two independent instances of the identical defect class in the two rows this seat worked,
in one sitting — likely worth a `test_gate_baton_donewhen_runnable_live.sh`-style sweep across *all*
live batons for `cd .* &&` without a following `|| exit`, not just this row's own two.

**A second, sharper round, courtesy of § 3.5's regression.** The first rewrite still coupled this
row's DONE-WHEN to `test_gate_pascal_m3.sh`'s overall `FAIL=0` — reasonable when this row genuinely
was the gate's only failure, but § 3.5's concurrent, unrelated regression immediately broke that
coupling and would have blocked this row's own closure on someone else's bug. Rewritten again: check
`uplevel2`/`uplevel3` output directly, and check the *board* for the specific absence of
`program_procedure_nested_1` among per-entry FAIL/CRASH lines — never the aggregate `FAIL=0`. ceo
routed this seat's process suggestion (re-run a row's own DONE-WHEN at the GRANT-NEEDED→FREE
transition, from the sibling row's FINDING) to hq_B as a queued row; hq_P sharpened it further,
in-chat to this seat: *"a DONE-WHEN may not pin a population count in a literal string; it must read
the denominator it grades against"* — the same defect class as the sibling row's stale `"96 pass / 0
fail"` string, generalized. This row's rewritten DONE-WHEN pins no count of any kind.

## Disposition

`pascal-uplevel-nested-proc-hang`: **DONE**, closed via computed `s4e_msg.sh done` (verbatim DONE-WHEN
run, not hand-typed). `.s` artifacts regenerated per the codegen-touched handoff rule — zero changes
needed for Pascal specifically (`uplevel2`/`uplevel3` carry no committed `.s`, unlike the SNOBOL4/Icon
convention); one unrelated Prolog `.REFUSED`-marker refresh landed as the demo-regen script's own side
effect and is pushed alongside, not attributed to this row.
