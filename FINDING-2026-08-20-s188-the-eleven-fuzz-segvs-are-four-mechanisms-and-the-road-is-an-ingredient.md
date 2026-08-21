# FINDING — 2026-08-20 s188 (seat4 `/home/claude4`, Claude Opus 5; queue row `fuzz-segv-batch`, rank 1)
# THE ELEVEN FUZZ SEGVs ARE **FOUR** MECHANISMS, NOT ELEVEN AND NOT ONE — AND IN TWO OF THE FOUR THE **ROAD IS AN INGREDIENT**: THE IDENTICAL PATTERN TEXT IS GREEN WRITTEN INLINE AND CRASHES WRITTEN THROUGH A STORED PATTERN.

**WATERMARK (`make pristine` at SCRIP `87ffd0b5`, RE-PROVED after the rebase at merged SCRIP `2cf31532` — see §9, RT_OPT `-O0`, tree clean; oracle `x64/bin/sbl -bf` verified alive):** corpus **m3 332/5 · m4 325/11 SKIP 1 (337)** — the row's quoted baseline **to the digit**, fail-set unchanged. Oracle arm is `-bf` per seat1's s188 ruling (`-b` is a case-folding language switch).

## 0. THE FIRST DELIVERABLE, ANSWERED: ALL 11 ARE STILL RED AT HEAD
All 11 `fz_segv_*.sno` re-run at HEAD in **both modes**: **11/11 rc=139**, m4 identical. All 11 checked-in `.ref`s re-verified against the live oracle: **zero drift**. One movement worth naming: **`fz_segv_02` is now rc=124 (HANG) in m3** while m4 and gdb still SEGV — it is timing-bearing, not cured, and a one-run verdict on it is an arbitrary draw.

## 1. THE CLASSIFICATION — 11 WITNESSES, 4 MECHANISMS, 1 COMPOUND
Every ingredient below was established by **ablation**, not by reading: the named ingredient is removed and the program turns GREEN. Reduced witnesses are checked in beside their originals as `corpus/probe/fuzz/fz_red_*.sno` with live-oracle `.ref`s.

| # | Mechanism | Witnesses | Reduced witness | Necessary ingredients (each measured) |
|---|---|---|---|---|
| **M1** | **ARBNO RE-ENTERS A DEFERRED ELEMENT** | `fz_segv_14`, `fz_segv_24`, `fz_segv_03`(arm 2) | `fz_red_m1a_arbno_defer_fencenull` · `fz_red_m1b_arbno_defer_blob` | outer ARBNO · the defer · a forcing tail · **inline road** additionally needs `FENCE(<null-matching>)`; **blob road** needs no FENCE |
| **M2** | **SEALED CAPTURED GENERATOR + FORCING RIGHT NEIGHBOUR** | `fz_segv_10`, `fz_segv_23`, `fz_segv_18`, `fz_segv_03`(arm 1) | `fz_red_m2a_fence_cap_gen` · `fz_red_m2b_fence_cap_nullalt` · `fz_red_m2c_cap_around_defer` | a **seal** (FENCE) · a **CAPTURE** on or around a generator inside it · an element to the right that forces retreat. **Dropping the capture cures all four.** `.` and `$` behave identically |
| **M3** | **`ARBNO(<null-first-arm ALT> <generator>)`** | `fz_segv_17` | `fz_red_m3_arbno_nullalt_gen` | outer ARBNO · an ALT whose **first arm matches the null string** · a **generator** to its right. **No defer needed.** `ARBNO(('a'\|'x') ARB)` GREEN; `ARBNO(ARB)` GREEN; `ARBNO((''\|'x'))` GREEN |
| **M4** | **BLOB-ROAD FENCE/DEFER ADJACENCY** | `fz_segv_09`, `fz_segv_15`, `fz_segv_19`, `fz_segv_02` | `fz_red_m4a_blob_alt_fence_defer` · `fz_red_m4b_blob_defer_fence` · `fz_red_m4c_blob_defer_arbno_fence` | the pattern must be reached **through a stored pattern `*P`** · a FENCE (or nested ALT) adjacent to a defer inside it. **The identical text written inline in the match statement is GREEN in all four** |

⛔ **`fz_segv_03` IS A COMPOUND AND ITS TWO ARMS CRASH INDEPENDENTLY** — arm 1 (`FENCE((BREAKX('ab')) $ v0) *G0`) is M2, arm 2 (`ARBNO(*G1)`, `G1 = (BREAK(' ') | '')`) is M1. Each SEGVs on its own with the other deleted. A batch classifier that assigns one row per file books this as one shape and loses one.

## 2. ⭐ THE SMALLEST CRASHER IN THE BATCH — TWO LINES
```
          G0            =  FENCE('')
          'ab' ARBNO(*G0) RPOS(0)
```
Oracle **`match`**, SCRIP **SIGSEGV in both modes**. Every ingredient is load-bearing, measured: `ARBNO(FENCE(''))` written **inline** is GREEN (the defer is required) · `G0 = ''` unfenced is GREEN (the FENCE is required) · no tail is GREEN (the forcing tail is required) · empty subject is GREEN · **defer depth 2 (`G1 = *G0`) is GREEN**, which is the opposite of the `defer-depth-floor` signature and is why this is not that row.

## 3. ⛔ THE ROAD IS AN INGREDIENT — THE RESULT MOST LIKELY TO BE RE-DERIVED
For M1 and M4 the crash depends on **how the pattern is reached**, not on what it says. Measured grid, `ARBNO(*G0)` on `'a b c'`, inline in the match statement vs through `P = ARBNO(*G0)` + `*P`:

| `G0` | inline `ARBNO(*G0)` | blob `*P` where `P = ARBNO(*G0)` |
|---|---|---|
| `FENCE('')` | **SEGV** | **SEGV** |
| `(BREAK(' ') \| '')` | AGREE | **SEGV** |
| `ARBNO(TAB(1))` | AGREE | **SEGV** |
| `(LEN(1) \| '')` | AGREE | AGREE |
| `''` | AGREE | AGREE |

⭐ **A probe grid written without the stored-pattern road would score these AGREE and report the shapes clean.** This is the mechanical reason the s183 hand-written 168-combo grid scored 167 AGREE while the random walk found 27 red shapes: the generator varies the road, a hand grid varies the pattern.

## 4. ⛔ NOT DUPLICATES — EVERY NAMED ROW CHECKED AT HEAD, NOT ASSUMED
The brief named five rows to check against. All were run at HEAD:
- `defer-depth-floor` — `ptw_min_defer2_floor` **rc=0 `match`** (cured s187). Its signature is a wrong ANSWER at depth ≥2; M1's minimal witness is depth 1 and **greens at depth 2**. **Not a duplicate.**
- `arbno-tail-false-accept` — `ptw_min_arbno_tail_falseaccept` **rc=0 `nomatch`** (cured s187). A false ACCEPT, not a crash. **Not a duplicate.**
- `arb-immed-assign-retry` — `ptw_min_arb_immed_retry` **rc=0 `match`/`a+aa`** (cured s188). **Not a duplicate.** M2 measured `.` and `$` as interchangeable, so it is not a `$`-specific class either.
- `arbno-alt-fence-L1` — `ptw_min_arbno_alt_fence_L1` still red but **rc=0 `nomatch`, a wrong answer with no crash**. M3 is its neighbour (ARBNO + ALT) but needs the **null arm on the LEFT alternation and a generator to its right**, and it crashes. **Not a duplicate; adjacent family.**
- `m1-composed-wild-jump` — shares the wild-transfer *signature* (several of the 11 land in `[stack]`, in ld.so data, or at `0x0`) but none of the 11 needs beauty's ingredients. **Not a duplicate.**

## 5. ⭐⭐ THE ONE-CURE QUESTION, ANSWERED BY MEASUREMENT: **NO** — SO THE ROW CLOSES INVESTIGATION-ONLY
The strongest candidate was seat8's own routed successor `alt-arm-resume-surface`: s187 fixed the resume surface in `sno_seq_nary` (`if (sno_seq_tail() && ti) ri = ti;`) and told the next seat to **grep `g->all[before]`**; the twin site is `lower_snobol4.c:1800`, `case TT_ALT`. I applied seat8's correction there behind an **opt-in** `getenv("SCRIP_ALT_TAIL")` probe (default OFF, no cached state, **no new global**) purely as a bisect instrument.

⭐ **IT CURES `160_pat_alt_inner_gen_resume`** — the standing crosscheck board red, `rc=139` → `rc=0 V=[X]`, which is the live oracle's answer. **One line.**
⛔ **AND IT MOVES ZERO OF THE 11.** All eleven stay rc=139 in both arms. **That zero is the load-bearing result: the fuzz SEGV batch is NOT the ALT-arm resume-surface class**, and the seal that matters in M1/M2/M4 is FENCE and the ARBNO instance boundary, not the ALT arm — they are separate resume-surface sites.
The probe was **reverted; this row lands no codegen change.** The measurement was handed to `alt-arm-resume-surface` via `s4e_msg.sh ask` — it is that row's cure, it needs that row's blast-radius sweep, and taking it here would have been a drive-by widening of exactly the kind seat8 warned against.

**TEN KILLSWITCHES SWEPT ON M1'S MINIMAL WITNESS, ALL INERT** (`rc=139` under every one): `SCRIP_FENCE_IGNORE=1` · `SCRIP_FENCE0_WHACK=0` · `SCRIP_SPAN_FRAME=0` · `SCRIP_OPT=0` · `SCRIP_SEQ_TAIL=0` · `SCRIP_ARBNO_ALTSIB=0` · `SCRIP_PAT_INLINE=0` · `SCRIP_CAP_SEAMTIER=0` · `SCRIP_DEFER_XPAT=0` · `SCRIP_RTSEQ_RESUME=0`. ⭐ **`SCRIP_FENCE_IGNORE=1` not curing it is the sharpest single fact in the batch: the defect is not in the fence VERDICT, it is in the fence WIRING.** `SCRIP_OPT=0` reproducing it puts it at or below LOWER, not in the optimizer.

## 6. ⛔ THE 1:1 INVARIANT BREAKS IN **BOTH** DIRECTIONS INSIDE ONE THREE-TOKEN SHAPE
`m3 ≡ m4` is a design invariant. On the M2 shape it fails both ways, and one ingredient flips it. Two witnesses checked in for this alone:
- `fz_red_m2_breach_m3only` — `'a+a+a' FENCE((SPAN('abc')) . v0) REM` → **m3 rc=139 · m4 rc=0 `match` (correct)**
- `fz_red_m2_breach_m4only` — `'a+a+a' FENCE((BREAKX('abc')) $ v0) REM RPOS(0)` → **m3 rc=0 `match` (correct) · m4 rc=139**

⭐ **THEREFORE MODE AGREEMENT IS NOT EVIDENCE OF CORRECTNESS ON THIS CLASS.** Both modes crashing looked like a shared lower/graph defect; the pair above shows the same shape landing differently per medium, which is what a **wild control transfer** does — the launch is shared, the landing is not. A seat that reduces one of these witnesses and checks only one mode will silently change class. (Recorded because my own first reductions of `fz_segv_10`/`fz_segv_23` did exactly that and had to be re-minted to both-mode forms.)

## 7. ALSO SEEN, NOT MINE, ROUTED NOT WORKED
`FENCE('a' ARB . V) 'b'` on `'aXb'` → **SIGABRT rc=134**, i.e. the M2 shape with the seal spelled `FENCE` instead of `|` reaches the **`fuzz-abort-batch`** class. That row (rank 2, 2 witnesses) and this one are the same neighbourhood; whoever takes it should read §1 M2 first rather than re-reduce.

## 8. WHAT THE NEXT SEAT INHERITS
1. **M1's two-line witness is the cheapest entry point in the whole campaign** — `G0 = FENCE('')`, `'ab' ARBNO(*G0) RPOS(0)`. Start there, not at `fz_segv_02`.
2. **Do the ASM DIFF between `ARBNO(FENCE(''))` inline (GREEN) and `ARBNO(*G0)` (SEGV).** They are one token apart and one is correct; RULES' ASM-DIFF-FIRST has rarely had a cleaner pair.
3. **Do not reach for the monitor** and do not reach for `SCRIP_ZSM_ALL` (row `zsm-all-perturbation`).
4. **`fz_segv_02` needs 3-of-3 runs before any verdict** — it is the only nondeterministic member.


## 9. ⛔ RE-PROVED AFTER THE REBASE AT MERGED SCRIP `2cf31532`, NOT ASSUMED
The corpus push rebased onto seat6's `fuzz-diff-batch` and seat1's keyword-uppercasing, and **SCRIP had moved EIGHT commits upstream** since the watermark — including `2c8d2b34` *"a DEFERRED THUNK MAY RETURN AN EXPRESSION, and the STAR arm could not see one"* (seat3, row `m1-class-b-stmt-parse-error`), which lands squarely on the defer road M1 and M4 stand on. The brief's own warning applies (*"a witness may already be cured — say so, that is a result"*), so every number above was re-measured after a **second `make pristine`** at merged SCRIP `2cf31532`:

- **All 11 originals: still rc=139.** No witness was cured by the eight commits.
- **All 11 checked-in reductions: unchanged**, each in the mode profile documented above.
- **Both 1:1 breach witnesses still breach, in both directions** (`m3only` m3 rc=139 / m4 `match`; `m4only` m3 `match` / m4 rc=139).
- **Corpus board `m3 332/5 · m4 325/11 SKIP 1 (337)`, fail-set IDENTICAL BY NAME** to the `87ffd0b5` arm.

⭐ The classification is therefore stated at `2cf31532`, not at the tree it was found on.

**WITNESSES (corpus):** 13 new files in `corpus/probe/fuzz/` — 9 reductions (`fz_red_m1a`, `m1b`, `m2a`, `m2b`, `m2c`, `m3`, `m4a`, `m4b`, `m4c`) + 2 breach witnesses + live-oracle `.ref`s. Originals untouched.
**SCRIP:** no source change. **`.s` regen NOT APPLICABLE** — no codegen file touched.
