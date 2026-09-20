# FINDING — THE TINY ARENA NEVER COLLECTS OVER SncM, AND FORCING IT FINDS A SILENT WRONG ANSWER IN DEFERRED EVAL

**hq_snocone, 2026-09-20, SCRIP `5418432bb` corpus `8486bb1e2` RT_OPT=-O0, incremental `make`.** This lane's FIRST row
under MODE TENET (MODE line 2 / CEO-1011: *completeness does not open in a language until that language's GC share is
measured clean by oracle diff at the tiny arena*). Row
`snocone-gc-the-snocone-share-of-the-unmapped-slot-population-censused-by-name-and-the-master-clean-under-forced-collection`.

## 1. ⛔⭐⭐ THE TINY-ARENA BOARD WAS INERT, AND NOTHING IN IT SAID SO

| reading | board | what it actually measured |
|---|---|---|
| SncM at the shipped arena | `total=336 shipped=336 m3_pass=336 m3_fail=0 m4_pass=336 m4_fail=0 arena_mb=512` | the compiler |
| SncM at `SCRIP_HEAP_MB=1` | `total=336 shipped=336 m3_pass=336 m3_fail=0 m4_pass=336 m4_fail=0 arena_mb=1` | **nothing about the collector** |
| the same 336 entries, `[ZGC] regeneration` counted | `collectors=0 non_collectors=336 regenerations=0` | why |

**Not one SncM entry allocates a megabyte, so at a 1 MB window not one of them collects even once.** The tiny-arena
board is a statement about this corpus, and it carries `arena_mb=1` in its own line while meaning nothing by it. Had
this lane reported that green as *snocone's GC share is clean*, CONDITION 1 would have opened completeness in snocone
on a measurement that never ran. ⭐ **No rc, no denominator, no FAIL=0 anywhere in that board can say this** — the
decidability question is not asked by any instrument that grades pass/fail, and it has to be asked separately and first.

**The arm that fixes it, and it is three lines of shell:** count `[ZGC] regeneration` (`SCRIP_ZETA_TELEM=1`) over the
graded population, and REFUSE rc=2 — never report green — when the count is zero. It is ARM 1 of
`test_gate_snocone_gc_share_named_and_master_clean_under_forced_collection.sh`, and it is the only reason arms 2 and 3
mean anything. Made able to fail (`SCRIP_GC_STRESS=1`) the same population reads `collectors=336 non_collectors=0
regenerations=1268`, and the board is no longer flat.

## 2. THE CENSUS THAT NAMES — SNOCONE'S CLASS-2 SHARE IS EMPTY

`util_gc_unmapped_store_census.py` over all 336 entries materialized out of the master **by ORIGIN** (never by a
filename glob):

```
witnesses=336 graphs=1 shielded_stores=1480 members=1176 undecidable=304
BELOW-REGION=1176 RAW-SLOT=0 GAP=0 ABOVE-REGION=0 OUTSIDE-LAYOUT=0 NO-MAP=0
```

**`NO-MAP=0` is this lane's own number and it is EMPTY** — class 2 of ARCH-GC section 3c, the per-language class the
cto assigned to the HQs in writing, does not exist in snocone. This is the same fact the ceo read as `no_layout 0`,
now NAMED rather than counted: every one of the 1176 members is printed with its witness, graph, site, line, offset
and source register.

⛔ **The 1176 are NOT a defect list and this lane does not claim them as one.** They are all BELOW-REGION — class 1,
the cto's — and that census's own header says a negative offset is where spine words live BY CONSTRUCTION and was
never the discriminator (CFO-114 and CFO-136 refuted the sign rule twice). By site kind: `call` 954 · `assign_var`
130 · `subscript` 44 · `kw_assign` 24 · `field_var` 8 · `lit_integer` 6, plus the `n<NN>_unop_bx` and
`n18_kw_snobol4_bx` forms. 304 sites are UNDECIDABLE (`FRAME-DEPTH-MULTI-VALUED`, `NO-ANCHOR-REACHES-SITE`) and are
named, never folded into a green count.

⭐ **One instrument caveat worth a line:** that verdict prints `graphs=1` over 336 witnesses. `graphs_seen` is a set
union of graph NAMES and every SncM entry's graph is called `main`, so the 1 is a name collision, not a count. It is
not this row's number and nothing here rests on it — recorded so the next reader does not take it for a population.

## 3. ⛔⭐⭐ THE DEFECT: `EVAL` OF A DEFERRED EXPRESSION RETURNS THE NULL STRING UNDER COLLECTION

With the population able to fail, SncM at `SCRIP_GC_STRESS=1 SCRIP_HEAP_MB=1` reads **`m3_fail=1 m4_fail=1` over
`total=336`**, one entry: `eval_datatype_defer_1` (origin `ladder__rung11_unary_operators_deferred_asterisk`), same
fingerprint `fp=5e2133a7` in both modes.

**Minimal at two lines:**

```snocone
d = *1;
OUTPUT = EVAL(d);
```

| arm | answer |
|---|---|
| `sbl -bf` on the SNOBOL4 twin (`/home/resources/x64/bin/sbl`, absolute path) | **`1`** |
| `scrip`, no collection | `1` |
| `scrip`, `SCRIP_GC_STRESS=1` | **the null string — rc=0, no diagnostic** |

### What was ablated, and every arm of it is a measurement

| probe | result | what it kills |
|---|---|---|
| `OUTPUT = EVAL(d) :F(NOPE)` on the SNOBOL4 twin | takes the **success** branch | it is NOT a statement failure — EVAL SUCCEEDS and returns null, so **no conditional in any program can see it** |
| the SNOBOL4 twin of the same two lines | **identical wrong answer** | not snocone-specific — the cure is a SHARED node |
| `SCRIP_GC_STRESS=1` at the **shipped 512 MB** arena | **identical wrong answer** | ⛔ **the arena is not the discriminator** — a tiny-arena-only reading would have missed this entirely |
| stress 2, 3, 4, 5, 8 | all **correct**, and stress=2 does the **same number of collections** as stress=1 | not the COUNT of collections — it is WHICH allocation one lands on |
| `SCRIP_GC_BUDGET_MB=4096` (detax path off, no collection) | **correct** | not the slow allocation path |
| `SCRIP_GC_POISON=0` | identical | not a poison artifact |
| `OUTPUT = EVAL(*1)` with no variable at all | **identical wrong answer** | not the stored DT_E in a global — the loss is INSIDE the EVAL road |
| `OUTPUT = DATATYPE(d)` under stress=1 | still `EXPRESSION` | the **tag survives; the payload does not** |
| a **second** `EVAL(d)` under stress=1 | `[GZ-10] rt_call_proc_descr: procedure '' has no stackless slab` | ⭐ the procedure NAME reads as **the empty string** — a heap name string the collection lost |
| `OUTPUT = EVAL("1 + 1")` (a STRING, not a deferred expression) | correct | the `DT_X` road is clean; it is the `*expr` `DT_E` road |

### The hypothesis, NAMED AND NOT MEASURED

`EXPVAL_fn` (`src/runtime/runtime_eval.c:536-566`) holds two `DESCR_t` values in **C locals across entries into
emitted code** — `eval_chain_enter_only(fn)` on the chain arm, `NV_SET_fn` / `eval_node()` on the other — which is
exactly the class of the cfo's open row `gc-rt-c-c-to-bb-entries-...`. The `NAME_ctx_t` chain it enters is rooted at
`g_ctx_current` (`src/runtime/core/name_save.c:15`), **one of CEO-1019's own named candidates**, whose
`NAME_entry_t.substr` is a bare `const char *` and for which no visitor call was found anywhere in `src/runtime`.
⛔ **Unconfirmed, and said so rather than shipped as a diagnosis:** a gdb breakpoint on `EVAL_fn` and on `EXPVAL_fn`
is **not reached in either arm**, so the dispatch road for `EVAL` is somewhere else and this hypothesis has not been
put on the witness. Whoever takes it starts by finding that road, not by reading these two files.

## 4. CEO-1019 — SNOCONE'S SHARE OF THE ROOTED-ALLOCATION SWEEP, ONE LINE EACH

Snocone lowers through the shared SNOBOL4 road, so this lane's candidates are the SNOBOL4 set the ceo named.

| static | can it hold a collected-heap pointer live across a collection? |
|---|---|
| `_vstack[VSTACK_MAX]`, core/core.c:3573 | **NO — it is DEAD STORAGE.** `DESCR_t`, so it could; but it is `static` with **zero** other references in `src/`, and being `static` it has no external linkage, so emitted code cannot name it either (the one escape route the root digest warns about). Nothing writes it, so it holds nothing. **Closed, and a deletion candidate** — shared node, so an ASK, never a landing from here. |
| `g_name_save`, rt/rt.c:1226 | **NO — already rooted.** `rt_gc_visit_raw` on the table and on every `[i].name` at rt.c:1338-1340. Closed. |
| `g_dcap_nv_cell[]`, pattern_match.c:713 | **Guarded, on the cfo's own terms.** Every read is gated on `g_nv_memo_seen[i] == g_nv_memo_gen`, the generation CFO-117 joined to the collector's invalidation at `5418432bb`. Closed on that landing; not re-measured here, and said so. |
| `g_nv_memo_val[]`, core/core.c:3070 | **Same generation guard** (`g_nv_memo_seen`/`g_nv_memo_gen`). Same disposition, same caveat. |
| `g_ctx_current`, core/name_save.c:15 | ⛔ **CANNOT TELL — and this is the one that touches this lane's live defect.** It points at C STACK frames (`NAME_ctx_enter(&eval_ctx)`), so the pointer itself is not a heap pointer; but `NAME_entry_t.substr` is a bare `const char *` that can point into a collected heap string, `ctx->entries` is grown storage, and **no visitor names either**. By the ceo's own rule that is a GC row in this lane. |
| `g_lf_type`, pattern_match.c:24 | ⛔ **CANNOT TELL.** `DATBLK_t *` with no visitor found; whether the block it names is carved from the collected heap is not settled here. |
| `g_dcap[BB_DCAP_MAX]`, rt_runtime.c:24 | ⛔ **CANNOT TELL.** `bb_dcap_t` array, no visitor found; the deferred-capture state is on the same road as the defect above. |
| `g_kwb[]` / `g_kwb_bound`, keywords.c:205,240 | ⛔ **CANNOT TELL.** A static initialised table, so the entries themselves are image data; whether any cell is ever overwritten with a heap value under `&`-keyword assignment is not settled here. |

Four CANNOT-TELLs, and per CEO-1019 that is a GC row in this lane rather than an answer. It is not minted this sitting:
the row in hand is the one above, `g_ctx_current` is very likely the same defect wearing a different hat, and minting a
second row for a cause the first row's cure will settle is the duplication the ceo's loop exists to prevent.

## 5. WHAT THIS LANE IS NOT CLAIMING

- **Not** that snocone is clean. It is not: one entry returns a wrong answer under forced collection, the row is open.
- **Not** that the 1176 BELOW-REGION members are defects. They are a named residual on the cto's classes 1 and 4.
- **Not** that the cure is this lane's. It reproduces from the SNOBOL4 frontend, so it is a shared node: handed to the
  **cfo** (collector / safe-point road) under Lon's escalation order, with the witness, the ablation and the cost.
- **Not** a re-reading of the shipped-arena board. SncM remains 336/336 both modes at `arena_mb=512`, unmoved.

## 6. THE INSTRUMENTS THIS LANDED

- `SCRIP/scripts/test_gate_gc_snocone_deferred_eval_survives_a_collection.sh` — the two-line witness, both frontends,
  **ref cut from `sbl -bf` at gate time** and never pinned. RED on origin today and named in `make test-arena`'s sweep,
  which is where that recipe says a collector finding belongs. It discriminates in both directions by construction:
  it first requires the witness to be CORRECT without a collection, so "wrong always" fails differently from
  "wrong only under collection".
- `SCRIP/scripts/test_gate_snocone_gc_share_named_and_master_clean_under_forced_collection.sh` — the row's DONE-WHEN.
  ARM 1 decidability (refuses rc=2 on a population that did not collect) · ARM 2 the census, read by its **printed
  verdict and not its rc** (it exits 1 whenever it names any member) · ARM 3 the master graded by oracle-cut refs over
  its **printed** denominator. ~5 min; deliberately NOT in `make test` — the blocking set is the shared resource that
  does not scale with seats (CONDITION 2), and wiring a five-minute arm into it is the coo's call, not this lane's.

## 7. ⭐ THE REUSABLE HALF

**A board that carries the knob in its own verdict line is not thereby exercising the knob.** `arena_mb=1` was printed
on a run where nothing collected. The instrument was honest, the denominator was real, the FAIL=0 was true, and the
conclusion would have been false — because the question *did the population do the thing I am grading it for* is not
asked by any pass/fail instrument and has to be asked on its own. The general form is the one the root digest already
carries about `command -v` and `$?`-after-a-pipeline: **an instrument that answers a narrower question than you think
you asked will never say so** — and here the narrowing was not even in an instrument, it was in the population.
