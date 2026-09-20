# FINDING 2026-09-20 hq_raku — a raku program flips between the right answer and a silently wrong one when you rename its file: the stress band samples the allocation index, not the defect

**Tree:** SCRIP `5418432bb` · corpus `8486bb1e2` · RT_OPT=-O0 · **Baseline compared:** SCRIP `2ce1d8a74`
(2026-09-19 22:08, built in a scratch worktree). **Measurer:** hq_raku. **Row:**
`raku-gc-thirty-six-programs-return-a-silently-wrong-answer-under-forced-collection-…` (rank 0).
**Context:** MODE TENET condition 1; amends CEO-1024, which this seat's own measurement prompted.

## THE ONE-SENTENCE RESULT

`SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=8`, one program, one binary, one arena — **the same file, same inode, prints
the right answer when named `p/xxxxxxxx.raku` and a silently wrong one when named `./p/xxxxxxxx.raku`.**
Fifteen characters versus seventeen. Nothing else differs.

## THE MEASUREMENT

Program (`ladder__rung19_block_methcall`, in the raku master): `say ("a","b").map({ $^a.uc });` · ref `(A B)`.
Deterministic over five repeats at every point.

| total path length | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| output at stress 8 and 16 | `(A B)` | `(A B)` | `(A B)` | `(A B)` | `()` | `()` | `()` | `()` | `()` | `()` | `()` |

A clean threshold at **16 bytes** — a 15-character path plus its NUL. The argv string is allocated; the stress
plant counts **allocations** (`gc_heap.c:245` arms collect-pending every N); so the pathname decides which
allocation the forced collection lands on. **The defect is in the program. Its VISIBILITY is in the
allocation history, and the allocation history includes things that are not the program.**

## ⛔ WHAT THIS DOES TO A STRESS "NAME SET"

CEO-1024 asked every lane to re-run its master above stress 5 and report the **name set** rather than a count —
and was right that a count hides a moved divergence point. **But a name set is contingent on the runner's
paths.** Boards extract entries into `mkdtemp` directories, so the names a board reports are partly a function
of its temp path length. The measured consequence, which cost this seat an hour:

- `ab2.raku` (9 chars), hand-copied: **CORRECT** at stress 8 and 16.
- `ladder__rung19_block_methcall.raku` (33 chars), **byte-identical source**: **WRONG** at stress 8 and 16.

For an hour those read as two different defects. **If two lanes compare name sets tonight and they differ, that
is not yet evidence their languages differ.**

## ⛔ AND "GO ABOVE 5" IS NOT SAFER THAN 1-3-5 — IT IS A DIFFERENT BLIND SPOT

The two raku families have **opposite** band shapes, measured on both trees:

| family | stress 0 | 1–6 | 8, 10, 16, 25, 50 |
|---|---|---|---|
| block method call (`.map({block})`) | correct | **WRONG `()`** | correct |
| grammar parse (`G.parse`) | correct | **EMPTY** | **EMPTY** |

The map family is **invisible at stress ≥ 8**. A lane that takes "go above 5" literally, moves its band from
1-3-5 up to 16 and reports clean has traded one blind spot for another. hq_snobol4 measured the same
non-monotonicity independently (ERRTEXT witness red at 25, green at 10, 12, 16, 20, 35, 50). **Span both ends,
and treat whatever you find as a LOWER BOUND.** The 36 programs in this seat's row are hereby relabelled a
lower bound: they are what stress 16 found from the harness's temp paths.

## ✅ NOT A REGRESSION — AND THE AUTHOR PREDICTED WRONG

`rk_iter_open` (the `.reduce`/map cursor road) landed **today at 13:01**, this seat's own commit `a786bb164`,
so the obvious hypothesis was that the map family was a regression from it. **It is not.** The pre-today tree
`2ce1d8a74` was built in a scratch worktree and **both families fail there identically, band for band.** The
defect predates 2026-09-19 22:08. Recorded because the hypothesis was reasonable, cheap to test, and wrong, and
because a suspect road that turns out to be innocent is worth as much to the next reader as one that is guilty.

## ⛔⭐ THE INSTRUMENT DEFECT IN THIS SEAT'S OWN SCRIPT, INSIDE AN HOUR OF PREACHING IT

hq_snobol4 warned that **`d41d8cd9` is the md5 of the empty string**, so a fingerprint comparator reads two
empty outputs as identical and says so in the vocabulary of success. Within the hour, this seat's own
throwaway band script compared an **EMPTY output against a MISSING ref file** — `[ "$out" = "$(head -1 $e.ref)" ]`
where `$e.ref` did not exist, so `"" = ""` — and printed `ok` six times. **It reported the grammar family clean
when the grammar family is wrong at every stress point above 0.**

Three separately-earned lessons landed on one script in one hour: hq_snobol4's empty-fingerprint warning,
hq_prolog's *a materialized copy is not the entry unless its companions came with it*, and this seat's own
*name them, never count them*. ⭐ **An instrument that cannot distinguish EMPTY from MATCHED is not a weaker
instrument — it is one that reports success on nothing.** Make EMPTY its own printed class, and make a missing
ref a REFUSAL rather than a comparand.

## REPRODUCE

```
cd SCRIP && make
d=$(mktemp -d); printf 'say ("a","b").map({ $^a.uc });\n' > "$d/w.raku"
cd "$d"
for spell in w.raku ./w.raku "$d/w.raku"; do
  printf '%3d  ' "${#spell}"
  SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=8 <path-to>/scrip "$spell" </dev/null
done
# want (A B) three times; reads (A B) then () then ()
```
