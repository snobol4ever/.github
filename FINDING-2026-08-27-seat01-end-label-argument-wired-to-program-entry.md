# FINDING 2026-08-27 seat01 — `END`'s optional start-label argument now honored (silent-wrong-output conformance defect cured, both media)

**Date:** 2026-08-27 · **Seat:** seat01 (FLEET-12) · **Row:** `conform-end-label-ignored` (rank 1, locked via `next`) · **Build:** `make pristine` EXIT=0 at SCRIP HEAD (post-fix) · **Gate:** `test_one_witness.sh` on `corpus/probe/conformance/n01_end_label.sno`, both m3/m4, plus full `test_corpus_snobol4.sh` regression sweep · **Oracle:** `x64/bin/sbl -bf` (per the row's own witness receipt) · **DONE-WHEN: PASS.**

## THE DEFECT

SPITBOL manual v3.7 p.179: "An optional label may follow the word END ... to denote where program execution is to begin." SCRIP parsed and tolerated `END <label>` (no error) but silently ignored the label in both m3 and m4 — execution always started at the program's first statement. Witness (checked in by seat08, 2026-08-23):
```
        OUTPUT = 'should-be-skipped-if-end-label-honored'
startpoint
        OUTPUT = 'reached-via-end-label'
END startpoint
```
Oracle prints only `reached-via-end-label`; SCRIP (both media) printed both lines.

## ROOT CAUSE — two separate drops, found by tracing the value from parse to codegen

1. **`src/driver/stmt_ast.c` (`stmt_to_ast`, `is_end` branch):** the parser (`snobol4.y:225` `sno4_stmt_commit_go`) already captures the label correctly — for a line like `END startpoint`, "END" lands in the *label* position (column 1), which is what sets `s->is_end`, and "startpoint" lands in `s->subject` exactly like any other statement's subject. But `stmt_to_ast`'s `is_end` branch only ever read `s->label` (always the literal string `"END"` — useless, since that's what triggered `is_end` in the first place) when building the `TT_END` AST node. `s->subject` — the actual target name — was never read. Confirmed via `--dump-ast`: `(STMT :lbl END :end)`, no subject captured at all.
2. **`src/lower/lower_snobol4.c` (`lower_sno_stage2`):** even had the label survived to the AST, the top-level program graph is built by `sno_build_graph(st, nst, 0, is_def, NULL)` — the `0` is a hardcoded `entry_idx` into the statement array. This is the *same* general mechanism `DEFINE('FN()LBL')` already uses for its own optional entry label (the function takes `entry_idx` as a parameter precisely for this), but the main-program call site never computed it from anything — it was always 0, i.e. "always start at the first statement," full stop.

Also note: `st[]`/`nst` at this call site are built by filtering `prog->c[i]->t == TT_STMT` only (`lower_snobol4.c:2452`) — the `TT_END` node itself is excluded from that array entirely. So the label has to be read off the *original* `prog` list (which still has the `TT_END` node) and then resolved to an index *within* the filtered `st[]` array — two different arrays, deliberately not conflated.

## THE FIX (two small, additive changes; zero behavior change when no label is given)

- `stmt_ast.c`: added a **new**, separate `:entry` attribute (leaf, the subject's `TT_VAR` name) alongside the existing `:lbl` attribute — did not touch or remove `:lbl` (still literally `"END"`, still whatever else reads it, e.g. `driver_label.c`'s label table, is unaffected).
- `lower_snobol4.c`: before building the main graph, scan the original `prog` list for the `TT_END` node's `:entry` value; if present, resolve it to an index by scanning `st[]` for the matching `:lbl`; use that (falling back to `0`, i.e. today's behavior, if the node has no label or the label can't be resolved) as `sno_build_graph`'s `entry_idx` instead of the hardcoded `0`.

Because `sno_build_graph`'s `entry_idx` mechanism already existed and is shared with `DEFINE`'s own optional-entry feature, both mode-3 and mode-4 pick it up automatically — they share one graph-building path (`m3 ≡ m4` design invariant), so no separate mode-4-only or mode-3-only wiring was needed. Statements before the target label are still fully compiled (reachable if something else jumps to them) — they're just not where execution *starts*.

## VERIFICATION

- Witness: `test_one_witness.sh corpus/probe/conformance/n01_end_label.sno` → `m3=PASS m4=PASS` (was `DIFF`/`DIFF`). Row's exact `DONE-WHEN` command passes.
- `make pristine` EXIT=0.
- **Full corpus regression, same build:** `test_corpus_snobol4.sh` → mode-3 PASS=365 FAIL=0; mode-4 PASS=365 FAIL=0 SKIP=0 (365 total). **No regressions** — the entry_idx change is a no-op for every program that doesn't use `END <label>` (the resolve loop breaks immediately when the END node carries no `:entry`).
- **Blast radius, per the row's own STEP 3 instruction** (`grep -rn '^END\s+[A-Za-z]' corpus/`): found the witness itself, three `.ref` files where the pattern matches *printed output text* coincidentally (`callgraph.ref`, two `indirect_*.ref` — not source, not affected), and **one real hit**: `corpus/programs/lon_cherryholmes/sno/debug.sno:529` — `END           debuggo`, with a genuine label `debuggo:` defined at line 65 and an in-source comment reading *"After compilation, transfer to the top of this package to initialize."* This is a real program that was silently relying on (and being denied) exactly this feature. Per today's separate Lon ruling (`ceo` message this session, `lon-programs-parser-tests-only`), `corpus/programs/` is parser-tests-only right now and not runtime-scored, so this isn't a regression risk to any existing gate — but it's confirmed, non-hypothetical evidence the defect was live, not just theoretical.

## UNRELATED ISSUE FLAGGED, NOT FIXED

The same `test_corpus_snobol4.sh` run's gate-refusal check reports `suite:crosscheck/rung10` unresolved — no file at the hardcoded path, and `find -iname rung10.sno` across the whole corpus tree returns nothing at all (not just moved). Unrelated to this row's change (touches only the SNOBOL4 frontend/lowering, nothing in corpus suite lists); the 365/365 FAIL=0 numbers above are the actual regression signal and are clean. Sent as `q-corpus-crosscheck-rung10-missing` to hq_C rather than investigated here — out of scope for this row.

## LEDGER
Zero blank lines / 200-char-margin / no-comment style matched in both edited files. No new globals. No AST walking added in modes 3/4 — the fix reads `:entry` once during lowering (already-permitted AST-adjacent driver/lower code, same layer `stmt_to_ast`/`label_table_build` already operate at), not at runtime. `.s` artifacts not regenerated — per s269 ARTIFACT POLICY they exist only beside benchmarks/demos, and this change touches neither.
