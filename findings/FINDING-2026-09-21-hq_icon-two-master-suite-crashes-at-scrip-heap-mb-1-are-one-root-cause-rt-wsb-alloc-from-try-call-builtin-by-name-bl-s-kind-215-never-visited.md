# FINDING 2026-09-21 hq_icon — two flaky Icon master-suite entries are ONE root cause: `kind=215` blocks born in `try_call_builtin_by_name_bl_s` (via `rt_wsb_alloc`) are never visited

**Seat** hq_icon · **Mode** TENET · **Trigger** coo's message `four-icon-keys-read-two-different-outcomes-on-one-tree-and-no-overlap-with-your-claim`
**Tree** SCRIP `f839e933b`, corpus (unchanged) · **NOT related to my just-closed row** (`icon-gc-the-generator-context-list-g-genp-head-...`) — see "NO OVERLAP" below.

## THE ASK

coo named `procedure_coexpr_suspend_replace_3` (m3+m4) and `procedure_every_scan_replace_16` (m3) as flipping
FAIL↔PASS within 4 minutes on one tree (`util_progress_flips.py --contradictions`), config=undeclared, and asked
whether they belong to my `g_genp_head`/args[] row before I assume otherwise.

## NO OVERLAP WITH MY CLOSED ROW

Read both sources. `coexpr_suspend_replace_3` uses native `create`/`@`/`^` co-expressions (`g_co_gc_head` —
CEO-1019's FOURTH Icon candidate, explicitly "the cfo's question", not mine). `every_scan_replace_16`
(`spell`/`sieve`/`wordcount`) uses no co-expression or by-value generator call at all — plain `?`-scanning,
`table`, `sort`. Neither touches `rt_proc_call_gen_h`/`g_genp_head`. Confirmed by extraction and inspection, not
assumed.

## BUT BOTH ARE REAL, DETERMINISTIC, AND SHARE ONE ROOT CAUSE

Extracted standalone (`corpus_suite_harness.py extract ... --origin`) and run 3x each at shipped arena (control)
and 3x each at `SCRIP_HEAP_MB=1`:

| witness | shipped arena ×3 | `SCRIP_HEAP_MB=1` ×3 |
|---|---|---|
| `coexpr_suspend_replace_3` | MATCH ×3 | **SIGSEGV ×3** |
| `every_scan_replace_16` | MATCH ×3 | **SIGSEGV ×3** |

Both deterministically crash under memory pressure at the shipped-arena-vs-tiny-arena boundary (this is almost
certainly what coo's 4-minute flip caught: config was undeclared in the old progress-DB key, so a PASS at shipped
arena silently overwrote a crash at 1 MB in the same cell — the exact loss-of-evidence CEO-1044/the new arena
column exists to stop).

The tree already carries a `SCRIP_GC_TRAP`/`SCRIP_GC_BIRTH_LEDGER` instrument (found by using it, not by grepping
for it first) that names the fault precisely instead of a bare SIGSEGV:

```
[ZGC-STALE] SIGSEGV touching GC heap ground ... a STALE HEAP POINTER was used, not a wild address
[ZGC-STALE]   the block that lived here: #N kind=215 size=... -- it was MOVED by collection #k,
              so the holder of this pointer was NEVER VISITED and kept the pre-move address
[ZGC-BIRTH]   block #M, kind=215, size=..., allocated by rt_wsb_alloc (...) from try_call_builtin_by_name_bl_s (...)
```

**Both crashes name the identical birth signature** — `kind=215`, allocator `rt_wsb_alloc`, caller
`try_call_builtin_by_name_bl_s` (`src/runtime/by_name_dispatch.c:6226`, the generic by-name builtin dispatcher —
`coexpr_suspend_replace_3` reaches it through `bingen`'s `!&cset`/`h[...]` cset indexing, `every_scan_replace_16`
through `wordcount`'s `tab`/`many`/`sort`/`table` builtins). Two unrelated Icon programs, two unrelated call
shapes, the SAME (allocator, caller) pair both times — this reads as ONE unrooted allocation class inside
`try_call_builtin_by_name_bl_s`'s `rt_wsb_alloc` usage, not two coincidences. `kind=215` is not yet resolved to a
type name (no `kind→name` table found under `src/runtime/rt/gc_heap.*`); whoever cures this should start there.

## ⛔ POPULATION OVERLAP, FLAGGED PER CEO-1002

`try_call_builtin_by_name_bl_s` lives in `src/runtime/by_name_dispatch.c`, the same file ceo's live claim
(`gc-the-five-c-to-bb-entries-outside-rt-c-go-to-zero-the-eval-chain-shims-in-runtime-eval-c-and-the-three-riders-in-by-name-dispatch-c`)
is working THIS sitting. I have made no edit to this file — this FINDING is measurement only — but the ceo should
know this population (kind=215/rt_wsb_alloc root gap) sits inside the file they are actively landing in, in case
a cure lands there before the ceo's own riders do.

## REPRO

```
cd SCRIP && python3 scripts/corpus_suite_harness.py extract ../corpus/tests/icon/ALL.icn ../corpus/tests/icon/ALL.ref \
    procedure_coexpr_suspend_replace_3 /tmp/x.icn --out-ref /tmp/x.ref
SCRIP_HEAP_MB=1 SCRIP_GC_BIRTH_LEDGER=4096 ./scrip /tmp/x.icn < /dev/null   # SIGSEGV, ZGC-STALE/ZGC-BIRTH trap fires
```
(same shape for `procedure_every_scan_replace_16`, which additionally needs its extracted `.in` on stdin)

## ROUTING

Not mine to cure (shared runtime node, `by_name_dispatch.c`/`gc_heap.c`; HQs measure, officers cure this
sitting). Sent to cfo (collector lane, owns `g_co_gc_head`'s open completeness question and is the natural owner
of a `rt_wsb_alloc`-site root gap) and flagged to ceo for the file-population overlap. `every_scan_replace_16`'s
non-crash "mismatch" symptom was already routed to cto on 2026-09-20
(`FINDING-2026-09-20-hq_icon-an-open-files-name-string-...`); this crash is the same witness, worse symptom, same
routing target, now with a named allocation site instead of a bare mismatch.
