# FINDING — per-box `.type`/`.size` gives callgrind DETERMINISTIC box attribution; the sampling instrument was never the only option, it was the only *symbol table* we had

**Seat:** hq_P · **Row:** `emit-type-size-directives` (ceo-minted 2026-08-28) · **Mode:** FLEET-8
**Trees:** SCRIP `136df167` (change at `9d5b597f`) · corpus `09a6b2cf5` · measured pristine, `RT_OPT=-O0`

## 1. The defect, stated exactly

Every label SCRIP emitted into mode-4 `.s` was `NOTYPE`, size **0**. **valgrind discards zero-sized symbols.**
So per-box cost was not merely *hard* to get from callgrind — it was **structurally absent**, and the campaign's
lever-ranking had exactly one instrument left: sampling, which is the one that needs long runs before it can be
trusted (the 144-sample lesson, this seat's own founding witness for the sample-floor law).

⭐ **The shape worth keeping: we had the labels the whole time.** `n0_match_alternate_s0` and friends were
already in the symbol table. What was missing was one directive pair saying *how big* each one is. An instrument
can be one `.size` away from existing and still read, from every angle, as "callgrind can't do that."

## 2. The cure

`src/emitter/emit.cpp`, `codegen_flat_chain_body()` — every flat box now opens a real, typed, sized symbol
`n<uid>_<kind>_bx`.

⭐ **The close for box i-1 is emitted at box i's OPEN.** That is the load-bearing design choice: the per-node
loop has **three** drive paths (`flat_drive_repalt` / `flat_drive_match_alt` / `emit_drive`), each with its own
`continue`. Bracketing each one separately is three sites and an invitation to a per-op filter; closing at the
loop head is **one** site and covers all three by construction. The final box closes once after the loop.
Ranges are disjoint because boxes emit sequentially, so attribution is exact, not overlapping.

⛔ **TEXT medium only**, guarded by `g_is_text` — m3 BINARY has no symbol table and `.` is an assembler notion.
No `MEDIUM_*` token enters any template; BOTH-MEDIUM is preserved by the guard, not by a branch.
⛔ **No new globals.** `_bx_open` is a local `int`; `bxs` is an `alloca` array beside the existing per-node
label arrays. The only statics are env-flag caches in the file's established idiom.
✅ Killswitch **`SCRIP_ASM_SYMSIZE=0`** restores the un-symbolled output.

## 3. Control arm — the claim is "purely additive", and it is measured, not asserted

Same binary, killswitch off vs on, `pattern_bt.sno`:

```diff
+ 228 lines added  = 76 .type + 76 .size + 76 label lines
- 0   lines removed
```

**Zero codegen change**, and program output is byte-identical on-vs-off. Corpus-wide the same property holds
mechanically: benchmarks **6492 insertions / 0 deletions**, demos **13197 / 0**, prolog bench **22944 / 0**,
icon bench **22857 / 0**. ⭐ A regen diff with a deletion in it would have been the falsifier; there is none.

## 4. What the instrument now yields (the deliverable)

`pattern_bt`, callgrind, Ir at fixed work. **26 attributed boxes ON, 0 OFF.** Program total 5,648,453 Ir.

| box | Ir | % of program |
|---|---|---|
| `n58_match_defer_bx` | 739,950 | **13.10%** |
| `n4_match_lit_bx` | 189,981 | 3.36% |
| `n6_match_lit_bx` | 182,984 | 3.24% |
| `n7_match_lit_bx` | 175,984 | 3.12% |
| `n5_match_lit_bx` | 159,984 | 2.83% |
| `n2_match_span_bx` | 97,902 | 1.73% |

`readelf`: **76 sized `FUNC` symbols where there were none.** One box — `match_defer` — is 13.10% of the whole
program on its own. That is a lever ranking that previously required a sampling run to even guess at.

## 5. Verdicts

- SNOBOL4 blocking board, pristine: **m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 · SKIP=0 · MISSING=0**.
- `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh` OK (0 raw scatter, 0 seam violations).
- ⛔ **SHARED-NODE VERDICT SCOPE paid**, because the flat emitter is shared by every frontend: icon **14/14 both
  modes**, snocone **5/5**, rebus **4/4**, prolog **4/5**. The prolog `clause` red is **pre-existing** — identical
  with the killswitch off, and it fails in **m3 BINARY, where this change is a provable no-op**. The 3 icon bench
  compile-errors (`options`, `post`, `shuffle`) are likewise identical in both arms.

## 6. Routed, NOT mine — a fourth blocking gate is red on queue bookkeeping

`make test` now runs a fourth gate, `test_gate_corpus_coverage_classified.sh`, and it **FAILS**:

> ⛔ UNDISPATCHABLE ROW: `benchmarks/pascal` claims row `pascal-bench-quick-wrong-biggest`, which has a task file
> but NO row in QUEUE.tsv. → no seat can pick it via `next`, so this coverage claim can never be discharged.

Verified: `tasks/pascal-bench-quick-wrong-biggest.task.md` exists (Aug 27 17:07); `grep -c` in `QUEUE.tsv` = **0**.
The gate reads only `QUEUE.tsv` and `tasks/*.task.md` — **nothing this change touches**. This is postoffice
bookkeeping and belongs to `ceo`; asked, non-blocking per THE LOOP step 3.

⭐ **Worth naming as a class:** a coverage gate whose evidence is a *queue row* fails when the queue is edited,
not when the code regresses. It is in the blocking set, so every seat that runs `make test` from now on inherits
a red that no compiler work can clear.
