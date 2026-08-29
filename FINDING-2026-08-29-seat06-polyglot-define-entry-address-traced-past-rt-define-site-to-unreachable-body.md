# FINDING — polyglot DEFINE entry-address bug traced two layers past `rt_define_site`: the resolved label is wrong because the target's real body isn't reachable via static γ/ω traversal at all

**seat06 · 2026-08-29 · row `polyglot-define-entry-address-wrong-in-merged-program` · SCRIP HEAD `32a2d9df`**

**No fix landed. This is a deep trace, not a cure — read the "what's actually needed" section before attempting one.**

## Recap of the question this row started from

seat01's original FINDING (`FINDING-2026-08-29-seat01-polyglot-main-collision-and-a-second-masked-bug.md`) traced
this to `rt_define_site`'s `fn` argument, computed as `lea r9, [rip + <next-node-label>]` — "true and correct for
every plain single-language SNOBOL4 program... not localized further than 'somewhere in lower_snobol4.c's DEFINE
lowering or bb_define.cpp's address computation'."

## Confirmed: mode-4 only, mode-3 is correct

`demo03` (roman.scrip): m3 (`--run`) prints the correct three lines. m4 (`--compile`, assembled, linked against
`libscrip_rt.so`, run) SIGSEGVs. gdb: `rip=0x0`, stack shows a recursive `call_proc_staged` chain
(`n899`→`n894`→`n889`, matching `roman`'s own recursive `REPLACE(roman(n), ...)` call).

## The mechanism seat01's trace pointed at is NOT the one that fires here

`bb_define_bind()` (the function `_.lbl_t0` feeds into the `rt_define_site` LEA) has TWO different sources for
`op_define_role`/`lbl_t0`, dispatched by `emit.cpp`'s IR_DEFINE handling depending on the node's shape:
- **role 4** (`n_operands>=2`, built by `sno_build_call_stub` in lower_snobol4.c): `lbl_t0` comes directly from
  `IR_LIT(nd->operands[1]).sval` — a compile-time STRING baked into the IR at lowering time. For `roman`
  (`DEFINE('roman(n)t')`, no explicit second arg), this string is `"roman"` (confirmed:
  `d->entry = (entry_opt && entry_opt[0]) ? lp_strdup(entry_opt) : d->fname;` at lower_snobol4.c:916 — with no
  explicit entry label, `entry` defaults to the function's own name).
- **role 6** (`n_operands==0`, a placeholder node built during the MAIN merged-graph assembly, not by
  `sno_build_call_stub`): `lbl_t0` comes from `g_emit_cfg->dentry_name[]` — a table populated by a SEPARATE
  mechanism in **`src/driver/scrip.c` (the driver, not the lowerer)**, at the "MAIN merged graph" emission site
  (~line 1470-1486, inside the `main_bb_idx`/`bbg` handling for mode-4).

**MEASURED (temporary diagnostic, added and removed this session, not landed): `roman`'s DEFINE node goes through
role 6, not role 4.** `fname="roman"` (correct) but `lbl_t0="n853_statement_begin_α"` (wrong — a statement-boundary
bookkeeping marker, not `roman`'s real entry). Confirmed against the emitted `.s`: `lea r9, [rip +
n853_statement_begin_α]` at the `rt_define_site` call site, ten lines before a DIFFERENT, PROVEN-CORRECT label
computation (`lea rsi, [rip + roman_α]`, used for the unrelated "M4-ALPHA-SEAL" step in the same function) that
this row's fix should have produced instead.

## The role-6 (dentry) resolution mechanism, traced to its actual defect

`scrip.c`'s dentry-population block, for a placeholder node named `"roman"`: finds `s2->proc_table[]`'s "roman"
entry, gets its `proc_entry_node`, chases through `IR_SUCCEED`/`IR_FAIL`/`IR_GOTO` nodes (a "skip pass-through
markers" loop), lands on an `IR_GOTO_DEFERRED` node whose `.sval` is `"roman"` again (this is `sno_build_call_stub`'s
`gd` node — the SAME stub graph role-4 construction, now being consulted for its NAME rather than emitted
directly), then does a SECOND lookup: search `s2->proc_table[]` for an entry named exactly `"LBL__roman"` (SNOBOL4's
own label-registry convention, `lower_snobol4.c:2083`'s `bb_label_registry_add(lp_strdup(lbl), anchor[i])`, exposed
into the proc table under a `LBL__`-prefixed pseudo-proc name), takes ITS `proc_entry_node`, chases it through the
SAME `SUCCEED`/`FAIL`/`GOTO` skip-loop, and uses the result as the dentry target — later retroactively resolved to
that target NODE's own emission-time label (a separate mechanism in `emit.cpp`'s main flat-chain loop:
`if (dentry_entry[_dq] == nodes[i]) dentry_name[_dq] = lbls[i]->name;`).

**First hypothesis, tested and INSUFFICIENT:** the `SUCCEED`/`FAIL`/`GOTO` skip-loop (present at FIVE identical
sites in scrip.c: `:759`, `:1477`, `:1482`, `:1491`, `:1848`) does not also skip `IR_STATEMENT_BEGIN`/
`IR_STATEMENT_END`, so it can stop one hop early at a statement-boundary marker instead of the real content past
it. Added both to all five sites (uniformly — this exact "shared logic, N independently-typed copies" shape is
the class this codebase's own comments repeatedly warn drifts). **Measured effect: the resolved label DID move**
(`n853_statement_begin_α` → `n854_var_α`, confirming the chase now walks one hop further) **but demo03 still
SIGSEGVs identically** (same `rip=0x0`, same stack shape). `n854` is a `VAR` node (`var="n"`, roman's own
parameter reference) — closer to real content, but still not `roman_α`, and still not enough.

**Safety of the partial fix, measured before deciding to keep or drop it:** `test_gate_polyglot_demos.sh` — IDENTICAL
`m3 PASS=7 FAIL=3` / `m4 PASS=3 FAIL=7` with and without the fix (confirmed via `git stash`/rebuild both ways);
`demo05`'s pre-existing `SIGABRT` during compilation is unaffected either way (not caused by this fix). SNOBOL4
blocking set: PASS count unaffected, but `corpus/tests/snobol4/probe/guard_conflation.sno` — an ALREADY-FAILING
probe witness (wrong output, rc=0, on the unmodified baseline) — **changes failure mode to an abort (rc=134) with
the fix applied.** Both are "still failing" either way (not a pass→fail regression), but a probe witness's failure
*mode* changing, on a defect this session does not fully understand, is not something to land quietly. **Reverted
the five-site fix entirely** rather than land a change that doesn't achieve this row's goal and has an
incompletely-understood side effect on unrelated defect-documentation infrastructure — tree confirmed back to
`32a2d9df` exactly (`git diff --stat` clean) before this session's edits, matching seat01's own precedent for an
isolated-but-insufficient fix attempt on this exact row's lineage.

## The deeper discovery: `roman`'s real body is not statically reachable from the DEFINE at all

`--dump-ir` on the merged program's main graph (`n=112` nodes) shows the DEFINE statement's own control flow
(`STATEMENT_BEGIN`(13)→`DEFINE`(14)→...→`STATEMENT_END`(17)→next statement) never touches `roman`'s real content —
`MATCH_BEGIN`(65)/`MATCH_RPOS`(71)/`MATCH_LEN`(74)/the `REPLACE`+recursive-call chain(96-103) exist in the SAME
graph (they get emitted — `roman_α` IS a real label in the `.s`) but are **not reachable via any γ/ω edge chain
starting from the DEFINE's own statement** — the dump's own framing marks the region around them
"unreached (not on emit spine; shown for completeness)". This is expected and correct in isolation: `roman`'s body
is ONLY meant to be reached dynamically, via the label-registry anchor (`anchor[i]` in `sno_build_graph`, built at
lowering time specifically so a `DEFERRED`/by-name call can find it) — never via static control flow. **The
open question this row's fix actually needs to answer: does `s2->proc_table["LBL__roman"].proc_entry_node`
correctly equal (or γ-chain to) `anchor[i]` — the SNOBOL4-lowering-time node whose γ is wired to node 65 — in a
polyglot-merged program, or does something in the merge/assembly step (constructing `s2->proc_table[]` and
`bbg->all[]` from multiple languages' independently-lowered graphs) lose or misdirect that wiring?** This session
did not trace that far — `bb_proc_entry()`'s own implementation and how `ProcEntry.proc_entry_node` gets populated
for a `LBL__`-prefixed entry during polyglot assembly (as opposed to single-language compilation) is the next,
untraced link. Given the chase-loop fix genuinely advanced the resolved node (one real hop closer) without
reaching the target, the wiring is not simply "absent" — something is chaining through SEVERAL more nodes than a
single-language build would need, or `anchor[i]`'s own γ is pointing somewhere other than node 65 specifically
under merging. Both are plausible; neither is confirmed.

## What's actually needed, for whoever picks this up

1. Instrument (temporarily, as this session did) `bb_proc_entry()` for the `"LBL__roman"` `ProcEntry` specifically,
   and walk its FULL γ-chain node-by-node (op + node id at each hop), comparing a single-language SNOBOL4-only
   build of the same idiom against this polyglot build, to see exactly where the chains diverge in shape or
   length — this session compared only the START (`_lr->proc_entry_node`) and manually reasoned about the FIRST
   two hops; a full per-hop dump would settle whether more `IR_*` types need adding to the skip-loops, or whether
   the wiring itself is wrong upstream of them.
2. Check whether `anchor[i]` (lower_snobol4.c's per-statement label-registry node, one per `st[]` entry across the
   WHOLE program including all merged languages' statements) is even the SAME node graph-numbering-wise once
   `sno_build_graph`'s output gets folded into the polyglot driver's `bbg`/`s2->proc_table[]` structures — this
   session did not trace the polyglot MERGE step itself (where per-language graphs get combined), only the
   already-merged result.
3. If a fix lands here, it must be graded on the FULL `test_gate_polyglot_demos.sh` (all ten demos, not just
   demo03/demo08 — `demo02`/`demo04`/`demo09`/`demo10` fail the same way, `demo05` fails differently and
   pre-existingly, `demo07` fails m3 only) AND the SNOBOL4 blocking set AND single-language DEFINE-with-explicit-
   label programs (this row's fix touches driver code every language's polyglot path shares) before it's
   trustworthy — this row's own DONE-WHEN already requires the first; this finding adds the other two as things
   this session's own (reverted) attempt showed matter in practice, not just in principle.
