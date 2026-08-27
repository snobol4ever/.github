# FINDING — COPY had one branch, and the other aggregate fell through to identity

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-27 · **Row:** `conform-copy-table-aliases` (CLOSED)
**Landed:** SCRIP `f13ee81c` · corpus `d472cb34f`

## What was wrong

`COPY(table)` returned the SAME table object, so mutating the "copy" silently mutated the original.

```
T = TABLE(); T<'k'> = 'v1'; T2 = COPY(T); T2<'k'> = 'v2'
oracle:  v1 / v2      (two independent tables)
SCRIP:   v2 / v2      (one object, two names)
```

`src/runtime/core/core.c`'s `_COPY_` had a real `IS_ARR` arm (`array_new` + element copy) and then a bare
`return v` for everything else. A table fell through into that identity return.

## ⭐ THE DEFECT WAS AN ABSENT BRANCH, NOT A WRONG ONE — AND THE WORKING HALF IS THE ALIBI

`COPY(array)` was correct. That is not a mitigating detail, it is **the reason this survived**: a reader
auditing `_COPY_` sees a function that plainly implements copying, with a real allocation, a real element
loop and a correct result for the type they test first. Nothing about it reads as a stub. A **half**-
implemented dispatch is more dangerous than an unimplemented one, because the half that works vouches for
the half that does not.

⛔ **This is the second instance of one class this seat closed today.** In
`FINDING-2026-08-27-hq_C-line-lastline-were-absent-from-the-keyword-table-not-broken.md`, `&LINE` had no
row in the keyword table and was silently reclassified by a catch-all tier, dying with a confident error
about a subsystem it was never in. Same shape here: **a dispatch with a default arm cannot report a miss,
because a miss is indistinguishable from a default hit by construction.** ceo reported a third the same
day — an audit measured 0 lexical-display refs and labelled a REGRESSION "dead architecture".

⭐ **The stateable form: a census counts what is present and can never distinguish `never built` from
`built and lost` or `absent by design`.** Only history can. Which is why the right first step on any
"feature X does nothing" row is not to design X, but to ask whether X was ever there.

## ⭐ THE OVER-FIX WOULD HAVE PASSED THE ROW'S OWN WITNESS

The copy must be **shallow**: values are copied as `DESCR_t`, so a table nested inside the table stays
SHARED, and mutating it through the copy IS visible through the original. Verified against SPITBOL
(`nested-shared=SHALLOW`). A DEEP copy — the obvious, more-thorough-looking implementation — passes the
row's witness `f51_copy` perfectly and is **wrong**.

⛔ So the row as briefed could have been closed green by a defect. New witness
`f52_copy_table_independence.sno` pins what `f51` structurally cannot: independence in the OTHER direction
(f51 never mutates the original after copying), integer/descriptor-hashed keys, an empty-table copy, and
the shallow-nesting boundary. ⭐ **A witness that only exercises the direction the bug was reported in
will certify the opposite bug.**

## ⭐ THREE DETAILS TAKEN FROM AN EXISTING WALK RATHER THAN INVENTED

`CONVERT(table,'ARRAY')` in the same file already had to solve this, and copying its idiom avoided three
silent wrong answers — each of which would have produced a plausible, mostly-working copy:

1. **`TBL_FOREACH` is the only sanctioned walk.** A bucket is `{slot,len,cap}`, never a chain; `core.h`
   records that a hand-rolled `e = e->next` walk deliberately no longer compiles.
2. **Keys must be re-inserted as DESCRIPTORS** via `table_set_descr_d`. The header is explicit that
   descriptor-keyed and string-keyed calls hash differently and must not be mixed — entries placed by one
   are unfindable by the other. A string-keyed re-insert yields a copy whose integer keys can never be
   found: it would pass `f51`'s string key and lose `T<2>`.
3. **`key_descr == DT_SNUL` needs the lazy `tbl_pair_key(e)` fallback**, or those entries are dropped and
   the copy is silently short.

⭐ **The generalisable move: when adding an arm to a dispatch, find the code that already traverses the
same structure for a different purpose and copy its idiom.** Every one of those three is invisible from
the function being edited and obvious from thirty lines of a neighbour.

## Measured (make pristine EXIT=0 first, HQ-27)

| arm | result |
|---|---|
| `f51_copy` (row DONE-WHEN) | **m3=PASS m4=PASS** (was DIFF/DIFF both modes) |
| `f52_copy_table_independence` (new) | **m3=PASS m4=PASS** |
| both, against the PRE-FIX build | **DIFF/DIFF** — negative-tested by stash-and-rebuild |
| SNOBOL4 board | m3 **365/365 FAIL=0** · m4 **365/365 FAIL=0 SKIP=0 MISSING=0** |
| `test_gate_emit_no_lang` / `test_gate_template_medium_invisible` | EXIT=0 / EXIT=0 |
| SHARED-NODE control arms | icon 14/14 FAIL=0 · rebus 4/4 FAIL=0 |
| prolog `clause`, snocone `procedure` | RED, pre-existing, same two A/B-proven earlier the same session |

⭐ **Both witnesses were negative-tested and it caught nothing — which is the point.** The cost is two
minutes; the alternative is shipping a witness that would have passed against the bug it was written for.
This is hq_P's rule from the same day (*a criterion nobody has seen fail is not a criterion*), and holding
one's own new witness to it is the only version that means anything.

## Two process notes from the same session

⚠️ **The board REFUSED rc=2 mid-verdict and it was not this change.** `suite:crosscheck/rung9: no suite
file` — the SCRIP suite-list commit had landed and the corpus commit carrying the files had not been
pulled. Third instance of that class in one session (seat01 twice, seat12, hq_C). ⛔ **The gate behaved
correctly**: it refused rather than reporting FAIL=0 over a shrunken denominator. Row minted:
`suite-refusal-should-name-stale-corpus`.

⛔ **corpus `c92b54d24` is mine by authorship and not by cause.** The mandated handoff regen re-emitted 22
prolog bench `.s` (a duplicate `α` label dropped from generator prologues) — another session's codegen,
materialized by my regen run. A change to a C builtin's *body* cannot move emitted `.s` at all, since
emitted code only calls it by name; consistently, the benchmark and demo regens both reported
`changed=0`. ⭐ **The handoff regen makes the current session commit artifacts caused by prior ones, so
`git blame` on a `.s` names whoever last ran the regen, never whoever changed the compiler.**
