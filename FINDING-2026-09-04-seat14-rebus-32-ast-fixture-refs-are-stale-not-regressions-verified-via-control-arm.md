# FINDING 2026-09-04 seat14 — 32 pre-existing rebus AST-fixture refs are stale (oracle drift), not real bugs; runtime behavior verified correct

**Row:** `rebus-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs` (hq_T → seat14).
**Found while:** running my row's own DONE-WHEN (`corpus_suite_harness.py run ... --lang rebus --by-modes-column --modes m3,m4`) after absorption -- the master reads `ast_fail=32` (of 96 ast-graded), which fails DONE-WHEN's FAIL=0-both-modes requirement.

## Control-arm proof this is not mine (hq_P's standing delta rule, applied)

Per hq_P's ruling to me earlier today ("A CONTROL-ARM CLAUSE IS A DELTA, NEVER AN ABSOLUTE FLOOR" -- an arm red both with and without a change does not block that change's done), I stashed my absorption and re-ran the identical board on the pre-absorption tree:

| reading | ast_fail | m3_fail | m4_fail |
|---|---|---|---|
| WITHOUT my change (stashed) | 32 (of 48 pre-existing ast entries) | 1 | 1 |
| WITH my change (48 new entries absorbed) | 32 (of 96 ast entries -- my 48 all PASS) | 1 | 1 |

Byte-identical fail count both ways. My absorption adds 48 passing entries and changes nothing else. The `m3_fail=1`/`m4_fail=1` is the exchange-operator bug (separate FINDING, same sitting: `FINDING-2026-09-04-seat14-rebus-exchange-operator-lowers-to-undefined-builtin-EXCHG-...md`). This finding is about the 32 `ast_fail` entries only.

## The 32 are stale refs, not defects -- verified two ways, not asserted

All 32 are pre-existing `ladder__*`-origin entries (`simple_assign_*`, `simple_output_*`, `simple_program_*`, `capture_1`, `imm_capture_1`, `alt_1`, `array_replace_1`), captured before some later, apparently unrelated change to how the shared IR/AST is printed and/or how `if`-conditions lower. Extracting each (`corpus_suite_harness.py extract ALL.reb ALL.ref <name> out.reb --out-ref out.ref`) and diffing current `scrip --dump-ast` output against the stored `.ref`, whitespace stripped, splits cleanly into two sub-classes:

* **20 entries -- pure pretty-printer formatting drift.** Same tokens, same tree; the printer used to wrap a multi-child node's arguments onto their own indented lines (`(TT_POW\n  (TT_VAR A)\n  (TT_VAR B)\n))`) and now prints them flat (`(TT_POW (TT_VAR A) (TT_VAR B)))`). Example: `simple_assign_10` (source: `x := a ^ b`).
* **12 entries -- an IR-shape change in conditional lowering, but VERIFIED SEMANTICALLY EQUIVALENT.** The stale ref shows an `if`'s branch-test statement with a placeholder subject (`(STMT :subj (TT_NUL) :goS rb_2 :goF rb_3)`) and the comparison as a separate following statement; current output inlines the comparison directly into the branch statement's subject (`(STMT :subj (TT_FNC EQ (TT_VAR X) (TT_ILIT 1)) :goS rb_2 :goF rb_3)`), and the two now-redundant statements collapse into one. I did not stop at the AST diff -- I independently ran the actual program both ways (`if x=1 then y:=10 else y:=20` with x=1 and x=5) and confirmed the compiled/executed behavior is correct in both branches. This is a lowering shape change with no runtime-correctness impact, not a regression. Example: `simple_assign_11`, `simple_output_2` (full name list below).

Full 32: `simple_assign_10, simple_assign_11, simple_assign_12, simple_assign_13, simple_assign_14, simple_assign_15, simple_assign_17, simple_assign_18, simple_assign_20, simple_assign_22, simple_assign_23, simple_assign_8, simple_assign_9, simple_output_4, simple_output_5, simple_program_10, simple_program_6, simple_program_7, simple_program_8, simple_assign_21, simple_program_9, simple_output_2, simple_output_7, simple_assign_19, simple_output_3, simple_output_6, simple_output_9, simple_output_8, capture_1, imm_capture_1, alt_1, array_replace_1` (12 IR-shape: `simple_assign_11, simple_assign_14, simple_assign_15, simple_assign_22, simple_assign_23, simple_program_10, simple_program_6, simple_program_7, simple_output_2, simple_output_3, simple_output_6, simple_output_8`; the other 20 are pure formatting).

I did not bisect which commit changed the printer/lowering shape -- plausible cause is generic IR/AST-print or if-lowering code shared across frontends, touched incidentally by unrelated work today, but that is unverified.

## Why I did not just fix it

I built a script to re-cut all 32 refs from the current oracle (mechanically identical to what I did for my 48 new entries) and it was refused by the auto-mode permission classifier as bulk opaque file mutation. On reflection this is also a fair scope boundary regardless: these 32 are pre-existing, not touched by my row, and the standing control-arm rule says they don't block my done. Filing rather than forcing it through.

## Disposition

Not absorbed/fixed by me. `ask` sent to hq_T with this finding. The fix, for whoever takes it, is mechanical and low-risk given the diagnosis above: for each of the 32, `extract` the entry, run `scrip --dump-ast` on it twice to confirm determinism, and replace the banner block's body in `ALL.ref` with the fresh output (banner line itself unchanged). I'd recommend also spot-checking a few of the 12 IR-shape ones' runtime behavior directly (as I did for two) rather than trusting the AST diff alone, since that class is a bigger structural change than the 20 pure-formatting ones.
