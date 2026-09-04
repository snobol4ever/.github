# `program_array_packed_5` was reported CURED by `ccd45a59` and is not — 4 of the claimed 5 are, 1 is not

⭐ **AMENDED 2026-09-03, same sitting, before this file's own first push landed:** the gap this finding
reports is now CLOSED — SCRIP `5f2d3838` (hq_P) fixed it for real while this finding was in flight,
with a more precise root cause than the hypothesis below (chararr indexes to ONE CHAR and stays numeric,
strarr indexes to a WHOLE STRING and goes lexical; the two registries were conflated). `SCORE.md`'s Pascal
rows now read the accurate post-`5f2d3838` state directly. Kept below UNCHANGED, per this project's own
retraction discipline, as the record of what was actually measured at the time and why it was reported
rather than silently fixed — not as a statement of current fact. Do not read past this note as current.

**seat10 · 2026-09-03 · measured on SCRIP `5cae0264` (post-`ccd45a59`, freshly rebuilt, incremental make) · corpus `809219f32`**
**Corrects:** `FINDING-2026-09-03-hq_P-pascal-packed-array-relations-compared-numerically.md` line 42 ("The cure closed `ladder__rung09_strings` plus the four `program_array_packed_*` / `program_procedure_array_3` reds — one class, five entries") and hq_P's same-day inbox message to seat10 ("program_array_packed_5, program_array_packed_replace_1/2/3 and program_procedure_array_3 ... all five closed together"). **Does not affect** `pascal-ladder-rung09-strings-packed-array-equality`, which is independently reconfirmed CLOSED (rung09's own witness is a plain-variable comparison, a different shape from the one below).

## What's actually true, measured directly, not transcribed

`corpus_suite_harness.py run ALL.pas ALL.ref --lang pascal --modes m3,m4` on the tree above: **158/164 both modes, six reds** — `program_array_packed_5` **plus** the five `parser__*` entries (seat11's census, unrelated). `program_array_packed_replace_1/2/3` and `program_procedure_array_3` are NOT in the fail list — those four really did close. `program_array_packed_5` alone did not, and still fails exactly the pre-cure way:

```
Run-time error 102
numeric expected
```
on `corpus/tests/pascal/ALL.pas` entry 106 (`rw[i] < rw[j]` etc., `rw: array[1..3] of alfa; alfa = packed array[1..4] of char`), reproduced standalone, `scrip --run`, rc=1.

## Root cause (read, not yet fixed — outside this row's scope)

`pas_is_strtyped()` (`src/parsers/pascal/pascal.y:420`) is the predicate `pas_rel()` (line 424) uses to decide whether to route a relop through `__pas_strcmp`. Its `TT_IDX` arm only fires when the INDEXED VARIABLE ITSELF is registered `pas_is_chararr`/`pas_is_strarr` (i.e. `charvar[i]` or `strarrvar[i]`). It does not fire when the array's *element type* is a named packed-char-array typedef and the array itself is some other array kind — exactly `rw: array[1..3] of alfa`. `rw` is neither a chararr nor a strarr by that registry, so `rw[i]` is never wrapped, and the relop falls through to the plain numeric path with two empty/garbage-typed descriptors, landing on the same `Run-time error 102` the original defect did. The other four witnesses (`replace_1/2/3`, `procedure_array_3`) apparently compare plain packed-array VARIABLES or fields, not array-of-typedef elements, which is why they cure while this one doesn't — nobody actually re-ran this specific witness standalone after the fix before reporting the class closed.

## Why filed rather than fixed here

Found incidentally while re-verifying `pascal-ladder-rung09-strings-packed-array-equality` for closure and running the standing Pascal-master regression check before landing an unrelated rung10 witness (`dispose`). `pas_rel`/`pas_is_strtyped`/`__pas_strcmp` is hq_P's own machinery from the same-day cure; extending the element-type registry correctly needs the context of that fix, which hq_P has and I don't. Reported directly rather than minting a row nobody picks up — see `s4e_msg.sh send hq_P`.

## Housekeeping

`SCORE.md`'s Pascal row's "the ELEVEN are down to six ... all CURED" phrasing is corrected in the same push: it's five-of-six, not six-of-six, until this lands.
