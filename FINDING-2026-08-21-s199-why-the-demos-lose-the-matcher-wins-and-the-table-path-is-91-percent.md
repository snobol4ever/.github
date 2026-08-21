# FINDING s199 — WHY THE DEMO PROGRAMS ARE NOT FASTER THAN SPITBOL: THE MATCHER WINS, THE TABLE PATH IS 91.6% OF THE TIME
**HQ (Claude Fable 5), 2026-08-21 s199, Lon-directed ("analyze the demo programs and why they are not faster than SPITBOL"). `RT_OPT=-O0`, `SCRIP_NOHUGE=1`, `SCRIP_HEAP_MB=4096` (⛔ **gc=0 — no collection inside any window, so GC is EXCLUDED as the cause, not assumed away**), oracle `sbl -bf -s16m`, same `claws5.dat` for every row, **every run's `check:` value identical across engines** (66757/66757/66757/6469) so all four points do provably the same work.**

## THE METHOD — THE CORPUS WAS ALREADY BUILT FOR THIS QUESTION
`claws5-match.sno`'s own header states the design: *"the -match sibling runs the same grammar with NO captures; the delta between them is the cost of the sprinkled loads (capture + \*function() + structure build)."* Two of the four ablation points already existed. HQ minted the two missing middles (`claws5-cap` = captures only; `claws5-call` = captures + a **no-op** `*token()`), giving a four-point ladder over ONE grammar and ONE corpus where each step adds exactly one ingredient.

## THE LADDER (throughput, and per-iteration cost in µs)
| # | variant | ingredient added | sbl/s | m3/s | **m3:sbl** | sbl µs | m3 µs |
|---|---|---|---:|---:|---:|---:|---:|
| A | `claws5-match` | pure pattern match | 8,695 | 11,717 | **1.35× FASTER** | 115.0 | 85.3 |
| B | `claws5-cap` | + 3 conditional-assignment captures | 1,834 | 1,664 | 0.91× | 545.3 | 601.0 |
| D | `claws5-call` | + `*token()` callout (NO-OP body) | 770 | 384 | 0.50× | 1,298.5 | 2,606.9 |
| C | `claws5` | + 3-level TABLE build | 187 | 32 | **0.17×** | 5,350.5 | 30,959.8 |

## ⭐⭐⭐ THE DECOMPOSITION — each ingredient's OWN cost, and its own ratio
| ingredient | SPITBOL µs | SCRIP µs | SCRIP vs SPITBOL | share of SCRIP's total | share of SPITBOL's total |
|---|---:|---:|---:|---:|---:|
| pattern match | 115.0 | **85.3** | **1.35× FASTER** | 0.3% | 2.1% |
| captures (`. var`) | 430.3 | 515.7 | 1.20× slower | 1.7% | 8.0% |
| callout (`*fn()`, empty body) | 753.2 | 2,005.9 | **2.66× slower** | 6.5% | 14.1% |
| **3-level TABLE build** | **4,052.0** | **28,352.9** | **⛔ 7.00× slower** | **91.6%** | 75.7% |

**⇒ SCRIP's pattern engine is genuinely FASTER than SPITBOL's. The demo programs lose because a real program spends almost none of its time matching:** 91.6% of claws5's SCRIP runtime is table construction, and that is where the 7× deficit lives. The matcher — the thing this campaign has spent months on — is 0.3% of the wall clock on this workload.

## THE SECOND AXIS — RECURSIVE/DEFERRED PATTERNS (treebank, and beauty)
`treebank-match` is a **pure match with no captures** and still reads **0.74–0.85×**, where `claws5-match` reads **1.35–1.65×**. The grammar names the difference: treebank is `group = '(' word ARBNO(delim (*group | word)) ')'` — a **self-recursive deferred pattern**, the `*X` road, inside nested `ARBNO`. claws5's grammar is flat character-class scanning (`SPAN`/`NOTANY`/`BREAK`/`ANY`) with one `ARBNO` and no defer. ⭐ Independently corroborated by seat4's s168 `pt-baseline`, which named ***group defer 59.4%*** and *GC 0.0% on pure matching*. **So: flat matching WINS; deferred/recursive matching LOSES ~1.3×; and the table/callout path loses 3–7×.** beauty is all three at once (recursive `*Parse`/`*Command` defers + captures + `*SH()`/`*PC()` callouts building a tree) — which is exactly why it is the worst row on the board at 71× (m3) / 10× (m4).

## ⛔ WHY 7× IS THE INTERESTING NUMBER — IT IS NOT MERELY "TABLES ARE SLOW"
The microbenchmark suite's `table_access` row reads **0.49× (-O0) / 0.56× (-O2)** — i.e. SCRIP's *plain* per-op table access is only ~2× behind. claws5's table half is **7×** behind, **3.5× worse than the per-op deficit**. What claws5 adds over flat access: **nested tables** (`mem[num][wrd][tag]`, tables whose values are tables), **chained subscripts** (each read walks three levels; the increment does it twice), and an **`IDENT()` guard per level**. So the compounding — not the base table op — is the suspect, and it is measurable per level.

## ⛔⛔ A NEW DEFECT, FOUND BY SIMPLIFYING A WORKING PROGRAM
Flattening claws5's 3-level table to **one level** (`mem[wrd] = IDENT(mem[wrd]) 0` / `mem[wrd] = mem[wrd] + 1`, everything else identical) makes **SCRIP SIGSEGV (core dumped)** while **SPITBOL runs it correctly at 154.5/s with the same `check=6469`**. A *simpler* program crashing where the harder one runs is a class signal, and it also **blocks the per-level scaling measurement** the paragraph above calls for. Row `table-flat-1level-segv` minted. ⛔ Reproduction is exact and cheap (two `sed` substitutions on `corpus/benchmarks/snobol4/demo/claws5.sno`, recipe in the row); the witness was deliberately NOT checked into the benchmark tree, because a `*.sno` dropped in `demo/` joins the scored suite by construction.

## WHERE THE WORK IS — the ranked answer to Lon's question
1. **`table-nested-subscript-cost`** (rank 1): the 7× on nested table build/read — 91.6% of a real demo's runtime, and the single biggest lever on the board.
2. **`callout-fragment-entry-cost`** (rank 1): 2.66× on an **empty** `*fn()` — pure entry/exit overhead of a match-time callout, the same fragment-thunk road the M1 hunt lived on all week.
3. **defer/recursive matching** (~1.3×, existing D-21 territory; `*group` 59.4% already named by seat4).
4. captures at 1.20× are **not** a priority — measured small, and named here so no one spends a session on them.

## INSTRUMENT NOTES
`perf` is **unusable in this container** (`WARNING: perf not found for kernel 6.17.0-1032`) — no kernel-matched build; `valgrind` is absent. Function-level attribution therefore needs SCRIP's own instruments (`ARCH-PROFILE-BOX-HISTOGRAM.md`, `SCRIP_ZETA_TELEM`) or a gdb sampler on a lengthened `ZBUD`. **The four-point ablation above needed none of them** — ingredient-at-a-time differencing over one grammar answered the question without a profiler, and its numbers are engine-comparable by construction.
