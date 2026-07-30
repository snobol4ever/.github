# FINDING-2026-07-30b — ICN-RTX-16: `slen` IS A TEMPLATE DEFECT, NOT A C FIX — AND A BAIL COUNT CANNOT PREDICT BENEFIT

**Session s221-ICN. Lon grant: "All your choices. I'm with you on this."** Ladder: `GOAL-ICON-RTX.md`.
Contract: `ARCH-ICON-RTX.md`. `RT_OPT=-O0` throughout (O2-DIRECTED-ONLY); every timing first-round-discarded
per s201/s202.

⭐⭐ **RTX-16-ICN LANDED. `str_concat_d` GOES FROM 0 COMMITS TO 1,999,999 AND FROM 194ms TO 59ms ON A
DISPATCH-DOMINANT WINDOW — VIA ONE LINE IN A TEMPLATE, WRITING NO NEW ASM.**

⛔⛔ **AND TWO OF s220's OWN CLAIMS ARE FALSIFIED BY THE RUNG IT MINTED.** Both were well-evidenced when
written. Neither survived measurement.

---

## 1. ⛔ FALSIFIED #1: RTX-16 IS NOT "A C-SIDE DESCRIPTOR FIX". THE C SIDE IS ALREADY CORRECT.

s220 and this ladder's LIVE CURSOR both describe RTX-16 as *"a C-side descriptor fix that writes no asm"*
and as the reason `str_concat_d` bails on `SLEN0`. **Measured: the C side already populates `slen`.**

`c_str_concat_d` (`src/runtime/string_ops.c:18`) returns `BSTRVAL(buf, al+bl)` on **both** of its string
return paths — an authoritative byte count. The accumulated left operand of `s := s || "x"` therefore
arrives with a correct nonzero `slen`. **Nothing in C needed fixing.**

The defect is in the EMITTER. `src/templates/bb_lit_scalar.cpp`, `IR_LIT_STRING` arm:

```cpp
+ x86("mov", FRQ(_.op_off), (long)DT_S)      /* tag eightbyte: v=DT_S, slen=0 */
```

It writes the whole 8-byte tag word as `DT_S`, leaving `slen = 0` — **for a literal whose length is a
compile-time constant.** Read straight out of `scrip --compile` (step 0(i): the live compiler, never a
stored `.s`):

```
n11_lit_string_α:                         # the literal "x"
    mov qword ptr [rbp + 416], 1          # v=DT_S(1), slen=0   <-- length 1 DISCARDED
n12_var_ref_α:
    mov rax, 4294967305                   # 0x1_00000009 = (slen=1 << 32) | DT_N
```

⭐ **THE EMITTER PACKS `slen<<32` TWO BOXES LATER, SO THE OMISSION IS A GAP, NOT A LIMITATION** — and the
mechanism to fix it sits THREE LINES BELOW in the same file: the `IR_LIT_CHARSET` arm already writes the
`slen` half separately, `x86("mov", FR(_.op_off + 4), (long)-1)`, for the cset sentinel. The fix is that
line with the length instead of `-1`:

```cpp
+ x86("mov", FR(_.op_off + 4), (long)(_.op_sval ? strlen(_.op_sval) : 0))
```

ONE `x86(...)` concatenation, medium switched invisibly inside the encoder — compliant with
`GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` R2/R7/R9/R10 **by existing precedent in the adjacent arm**, not by
a new argument.

⇒ **CONSEQUENCE FOR THE LADDER: RTX-16 IS TEMPLATE WORK.** It is `templates/*.cpp`, which §7 assigns to
the ICON-BB ζ ladder and bars ICON-RTX from touching, and it fires `.s` regen ×3. The rung was minted as
concurrency-safe C work and is not. **It landed here only because Lon granted the §7 ruling explicitly.**
⚠ A future rung inheriting the "C-side fix" description would route to the wrong file and the wrong
ownership. **That description is now corrected in `GOAL-ICON-RTX.md`.**

## 2. THE `slen == 0` OVERLOAD IS THE ROOT DEFECT, AND IT IS ONE LINE OF CONTRACT

`core.h:descr_slen` gives `slen == 0` **two** meanings:

| `slen` | meaning |
|---|---|
| `0` | ⛔ **AMBIGUOUS** — "genuinely empty" *or* "length unknown, go call `strlen`" |
| `0xFFFFFFFF` | the operand is a CSET, not an ordinary string |
| else | authoritative byte count |

Every ported asm arm in the tree is gated on a nonzero non-sentinel `slen` and **says so in its own
comments** — `rtx_str.S:43` (*"slen == 0 => length UNKNOWN, C calls strlen. NOT an empty string"*),
`rtx_icnagg.S:31` (*"C must decide between empty string and length unknown"*). The arms are correct. They
were bailing because the emitter fed them an ambiguous descriptor. **Populating `slen` at the literal
makes the invariant hold and the arms fire unchanged.**

## 3. ⭐⭐ THE STRUCTURAL RESULT — 0 COMMITS → 1,999,999

Arm census (`util_rtx_arm_census.sh`), the s216 instrument, run before and after:

| workload | `str_concat_d` before | after |
|---|---|---|
| `bench_icnstr_concat_table` (s220's) | 80,000 / **80,000 bail** / **0 commits** | 80,000 / 40,001 / **39,999** |
| `bench_icnstr_concat_dispatch` (new) | 2,000,000 / **2,000,000 bail** / **0 commits** | 2,000,000 / 1 / **1,999,999** |

⭐ **PREDICTED IN ADVANCE, THEN CONFIRMED** (RTX-4's "state the expectation so a null is informative",
used prospectively): stated before measuring that bails would fall 80,000 → ~40,000 because the `tag`
half (`"k" || (i % 97)`, an integer operand) is untouched by `slen`. Measured 40,001 — the `+1` is the
first iteration's `""`, which correctly carries `slen=0` and legitimately routes to C via `IS_NULL_fn`.

## 4. ⛔⛔ FALSIFIED #2, AND IT IS THE DOCTRINE RESULT: **A BAIL COUNT CANNOT PREDICT BENEFIT**

s188's law on this ladder is *"a count cannot predict benefit."* s220 accepted that law and then built its
entire re-ranking on an **80,000-bail count**, treating bails as recoverable cost. **They are not.**

| window | bails converted | wall, gate ON before → after | verdict |
|---|---:|---|---|
| `concat_table` (s220's grading window) | 40,000 | 198ms → 195ms, **overlapping** | ⛔ **NULL** |
| `concat_dispatch` (new) | 2,000,000 | **194–231ms → 59–62ms, disjoint** | ⭐ **~2.4–3.3×** |

**Same fix. Same symbol. Same 80,000-vs-2,000,000 bails. Opposite answers.** Cause, measured not assumed:
in `concat_table` the bail cost is `strlen("x")` — **O(1), trivially cheap** — while the window's real cost
is the O(n²) byte copy of a string growing to 40,000 chars plus 119,999 `rt_str_alloc` calls. The bails
were 50% of the *count* and ~0% of the *time*.

⭐ **THE INSTRUMENT THE LADDER ACTUALLY NEEDS IS BAIL *COST SHARE*, NOT BAIL COUNT.** The way to obtain it
is a workload where the ported operation's own dispatch dominates — constant-size operands, no growth, no
allocation scaling. That is what `bench_icnstr_concat_dispatch.icn` is, and it is the first such window on
this ladder (⇒ **RTX-21-ICN's first member, landed**).

⚠ **THIS EXTENDS s220's OWN LESSON RATHER THAN CONTRADICTING IT.** s220 correctly found that the corpus
has no run phase and that the workload set was the defect. It then replaced one unrepresentative window
with another: `concat_table` HAS a run phase (95%) but its run phase is **allocation and growth**, so it
cannot grade a **dispatch** port either. **Run-phase-dominant is necessary and NOT sufficient. The window
must be dominated by the thing being ported.**

## 5. GATES — ALL THREE WATERMARKS, EACH RE-DERIVED AGAINST A PRISTINE REBUILD

⚠ `bb_lit_scalar.cpp` serves **all six languages** — string literals are universal — so this is a
system-wide invariant change and the shared-runtime rule in §0(3) applies with full force.

| gate | pristine | with RTX-16 | |
|---|---|---|---|
| Icon `test_icon_all_rungs.sh` | 252 / 11 / 30 | 252 / 11 / 30 | ✅ unmoved |
| SNOBOL4 corpus mode-3 | PASS=329 FAIL=5 | PASS=329 FAIL=5 | ✅ unmoved |
| SNOBOL4 corpus mode-4 | PASS=324 FAIL=2 SKIP=8 | PASS=324 FAIL=2 SKIP=8 | ✅ unmoved |
| Prolog rung suite interp | 164 / 0 | 164 / 0 | ✅ unmoved |
| Prolog rung suite compile | 164 / 0 | 164 / 0 | ✅ unmoved |

⭐ **THE PRISTINE COLUMN WAS MEASURED, NOT INHERITED.** The SNOBOL4 and Prolog numbers were first taken
*after* the edit; they were then re-taken against a `git stash` + full `libscrip_rt` rebuild, because a
baseline read after the change is not a baseline. Both matched.

**Kill-switch two-sided:** `SCRIP_RTX_STR=0` → 40000, gate ON → 40000. The switch switches and the results
agree. **Execution proof is the census itself** (0 → 1,999,999 commits), which is strictly stronger than a
poison probe and needed no edit to SN4-RTX's `.S`.

⚠ **`post` / `shuffle` / one other Icon benchmark report compile-err in `update_icon_bench_asm.sh`. NOT a
regression: their `.s` have never existed in the corpus and have no git history.** Verified before claiming.

## 6. WHAT THIS DOES *NOT* CLAIM

- **No `-O2` arm** (O2-DIRECTED-ONLY). `-O0` frame ceremony is part of the 2.4–3.3×; never quote it
  without the `-O0` clause.
- **The `concat_table` null is real and stands.** RTX-16 does not speed up string *building*; it speeds up
  concat *dispatch*. Those are different costs and this ladder just learned to tell them apart.
- **`rt_size_d`'s "dead arms retroactively activated"** — the third symptom RTX-16 was minted to cure — was
  **already committing** in this workload before the fix (1 entry / 0 bail / 1 commit both sides), because
  its operand came from `BSTRVAL`. That symptom was mis-attributed; the literal path was the only live one.

## 7. NEXT

- **RTX-23-ICN (`DT_S || DT_I` arm) — GRADE IT ON `concat_dispatch`, NOT `concat_table`.** The other 40,000
  `tag` bails are in the allocation-dominated window where §4 proves a converted bail buys nothing. A
  dispatch-dominant integer-operand variant must be seeded first or RTX-23 will read as a null for
  reasons that have nothing to do with its asm.
- **RTX-21-ICN — one member landed, four to go** (list/set/scan/IO), each dominated by the operation it is
  meant to grade.
- ⚠ **LEDGER ROT, FOUND AT SESSION START, NOT MINE, NOT FIXED:** `util_rtx_claims.sh` is **BLOCKED, 3
  fatal** — `rt_frame` is a **phantom** (no definition in the built `.so` AND no live `@PLT` site, though
  it was rank 7 / 255 sites at s203), and `rt_defer_open` / `rt_defer_close` are assembly whose rows are
  not `DONE` (step 0(e) violations). The `rt_defer_*` rows are SN4-RTX's to close.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
