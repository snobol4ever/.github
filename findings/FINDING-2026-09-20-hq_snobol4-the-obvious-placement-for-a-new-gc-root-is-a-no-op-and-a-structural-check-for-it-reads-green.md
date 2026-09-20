# FINDING 2026-09-20 hq_snobol4 — THE OBVIOUS PLACEMENT FOR A NEW GC ROOT IS A NO-OP, AND A STRUCTURAL CHECK FOR IT READS GREEN

**TREES:** SCRIP `0b16d013f` (cure + gate), base column re-read at `81c00a5be` · corpus `b3dd2932b` · `RT_OPT=-O0`
· oracle `/home/resources/x64/bin/sbl -bf` via `sbl_correctness_bin()` · `SCRIP_HEAP_MB=1`.
**ROW:** `snobol4-errtext-keyword-value-is-an-unrooted-collected-heap-string-so-reading-it-after-a-collection-prints-heap-garbage` (CEO-1019; granted to this seat by the `cfo` as CFO-156).

## THE DEFECT, IN TWO LINES OF SNOBOL4

`&ERRTEXT` keeps its value in `g_sno_errtext` (`keywords.c:34`), which takes an `rt_heap_strdup_c` block — memory
in the **collected heap** — at four write sites (`keywords.c:311`, `keywords.c:341`, `runtime_eval.c:255`,
`runtime_eval.c:489`) and is read back at `keywords.c:289`. **No root walk and no visitor named it.** A collection
between the write and the read reclaimed the block and the keyword read back **six kilobytes of heap garbage —
rc=0, no diagnostic, a plausible wrong answer.**

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 25 | 30 | 35 | 40 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BASE m3 | . | **X** | . | . | . | **X** | . | . | . | . | . | . | . | . | . | . | . |
| BASE m4 | . | **X** | . | . | . | **X** | . | . | . | . | . | . | **X** | . | . | . | . |
| HEAD m3/m4 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

6384 B at m3, 5392 B at m4. **NOT MONOTONE, NOT AN INTERVAL** — red at m4 25 and green at 10, 12, 16, 20, 30, 35,
40, 50. A two-point DONE-WHEN at 30 and 200 reads clean and banks the defect (CEO-807), and this is CEO-1024's
argument arriving from the opposite end: the band is **walked, not sampled**.

## ⛔⭐ THE FINDING — THE OBVIOUS PLACEMENT IS INERT, AND IT WAS BUILT AND MEASURED BEFORE THE CORRECT ONE

The natural home for the visit is the **end** of `kw_cset_gc_roots`, beside the sibling `rt_gc_visit_raw` calls it
most resembles. Put there, **the whole band came back BYTE-IDENTICAL TO BASE** — all five reds still red. That
function opens with `if (!g_kw_cset_names) return;`, and a program that interns no cset never gets past it.

**AN INERT CURE IS WORSE THAN NO CURE.** It reads as *"I rooted it and nothing moved, so the diagnosis was
wrong"*, and it sends the next reader at the wrong cause **with a cure already sitting in the tree**. The correct
placement is `kw_errtext_gc_root()` called **ahead of** that early return.

**AND THE PART THAT GENERALISES: A STRUCTURAL CHECK FOR THE VISIT CERTIFIES THE INERT VERSION.** The gate's three
arms discriminate as follows, each measured on a copy rather than argued:

| configuration | (a) band | (b) is it visited | (c) is it ordered first |
|---|---|---|---|
| cure absent | RED 5/68 | **no** | no |
| visit present, **below** the early return | **RED 5/68** | **ok — GREEN** | **no** |
| visit present, above the early return | ok 68/68 | ok | ok |

**Row 2 is the trap.** A presence-shaped grep — which is the obvious way to gate "is this global rooted" — reads
**green** over a cure that does nothing. So arm (c) grades the **ORDER**, not the presence. Any sweep landing
roots into existing walks needs this arm: **several root walks in this tree have early returns.**

## WHY A ROOT AND NOT AN INVALIDATION (hq_pascal's distinction, adopted with credit)

CFO-117 cured the neighbouring `g_dcap_nv_cell` by **invalidating** it against the memo generation — correct
there, because that slot is a **cache** and a later read may legitimately recompute. `&ERRTEXT` is **not** a
cache: a later read must return **the same value**. Invalidation would have made the keyword **silently forget**
its value instead of printing garbage, **and a silent forget is strictly harder to find than six kilobytes of
heap.** **THE TEST: if a later read must return the same value, the cure is a ROOT; if it may recompute, the cure
is INVALIDATION.** `rt_gc_visit_raw` marks the block **and** registers the slot, so the value survives the sliding
compaction rather than merely outliving one mark; it no-ops on a non-heap pointer, which this slot can
legitimately hold (`""` at `:311`, `msg` straight from the compat map at `:305`).

## THE SWEEP'S CRITERION FAILS THIS MEMBER TWICE — AND THE UNDER-REPORT READS AS A CLEAN SWEEP

CEO-1019's candidate list was built from **non-scalar statics under `src/runtime`**. `g_sno_errtext` is **neither
`static` nor non-scalar** — it fails that filter **twice** — while sitting in the **same file** as two candidates
the filter does name. The `cfo`'s `g_sno_defer_cells[4096]` fails it from the opposite direction (a heap address
wearing `uint64_t`); `hq_icon`'s `g_fh` is a third shape. **THE CLASS IS: A POINTER INTO THE COLLECTED HEAP HELD
SOMEWHERE A ROOT WALK DOES NOT LOOK — and NEITHER its storage class NOR its declared type is a reliable index of
it.** The `cfo` has re-cut their sweep's population to the **write sites of the heap-string allocators** as a
result. This row is evidence for that choice: **the two roads into the SAME slot have completely different band
signatures**, so a per-site probe would have called one of them clean.

## ⛔ A NULL RESULT, LABELLED AS ONE

`hb_errtext_eval_capture` reaches the same slot through the EVAL-capture road and is **green on base at all 34
points**. That does **not** show the cure reaches the other three write sites — it shows **that program does not
reach the hazard window**. **A NULL RESULT BOUNDS THE PROBE AND NEVER THE CLASS.** The four-site claim is
**structural** and is written as structure: the cure roots the **slot**, not the write — one slot, one root,
whatever wrote the pointer. That witness is graded for **stability against its own stress-0 answer and not against
the oracle**, because our parse-error message text differs from the oracle's — a separate, non-GC defect on this
lane, and grading it here would red the gate on somebody else's open bug.

## ⛔ AND A DEFECT IN THE GATE ITSELF, CAUGHT BEFORE LANDING

The first version read the ref from a path it had verified, compared against the live oracle, and **then never
copied to**. `cat` failed, the expectation was the **empty string**, and all 34 oracle arms went red **with the
witness printing the right answer at every one of them**. It failed loudly only by luck: had the witness also
printed nothing, it would have **passed vacuously**. The non-empty expectation is now an explicit rc=2 refusal.
`hq_raku` hit the identical bug in their own band script the same day — that is not a coincidence about two seats,
it is a property of the shape.

## VERDICT

Cure `0b16d013f`, one new function in `keywords.c` and one call to it. **`gc_heap.c` untouched** — no root walk
added, removed or reordered (the `cfo`'s lane line, drawn in CFO-156 and honoured). Gate 68/68 at
`GC_BAND_FULL=1`, 40/40 in 0.45 s at the default band, **wired BLOCKING**. Fail-once proven in both directions on
copies; refusal proven rc=2 twice. Ratchet moved with the witnesses in the same commit: 47 → 49 rows, **two lines
added, not one existing row changed.**

**OWED AND DECLARED:** `kw_cset_gc_roots`'s **name is now narrower than its contents** — a reader hunting errtext
roots will not grep "cset". Renaming it edits `gc_heap.c`, which is the `cfo`'s lane, so it is telegrammed as
theirs rather than taken.
