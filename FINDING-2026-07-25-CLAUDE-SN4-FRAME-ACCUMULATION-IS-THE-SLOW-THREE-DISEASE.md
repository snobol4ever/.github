# FINDING 2026-07-25 (s157) — SN4: FRAME ACCUMULATION, NOT FRAME LAYOUT, IS THE SLOW-THREE DISEASE

**Rung worked:** R1 / DB-2 α-DIET (ruled head after s156's R3 SPLICEMAP landing).
**Outcome:** R1 is real but is aimed at ~36% of a pool that a different, unruled lever takes ~91% of.
**RT_OPT=-O0 throughout. No code changed this session — measurement only. Default `.s` untouched.**

---

## 1. SAME-MOMENT BASELINE (rail, -O0, this container, all five in one window)

| demo | sbl us/iter | scrip us/iter | ratio | gain needed for 0.50 |
|------|------------:|--------------:|------:|---------------------:|
| claws5-match       |   306.4 |   209.0 | **0.68** | 1.36x |
| json-match         |  2502.0 |  2066.4 | **0.83** | 1.66x |
| treebank-match     |   758.8 |   971.7 | **1.28** | 2.56x |
| calculator-1-match | 57500.0 |109250.0 | **1.90** | 3.80x |
| calculator-2-match |   731.9 |  1711.9 | **2.34** | 4.68x |

Cross-session variance is large (RULES/s155); these five are same-moment and mutually comparable.
`identity=OK` on all five.

## 2. s156's ATTRIBUTION REPRODUCED EXACTLY

treebank, `SCRIP_SYMMAP=1`, cachegrind D1mw: PAT$2_α **48.6%** · PAT$1_α **21.9%** ·
PAT$0_α **20.4%** · PAT$3_α **0.5%** · residual `???` 0.6%. SPLICEMAP works — the α symbols
carry real `st_size` (`PAT$2_α` = 0x65b) and the blobs are nameable.

## 3. THE α FRAME-LINE CENSUS (what DB-2c was going to attack)

Static census of every `(%rsp)`/`(%rbp)` operand inside each α range, bucketed into 64B lines
(aligned-base assumption; the real base is only 16B-aligned, so add ±1 line of alignment jitter):

| blob | distinct offsets | span | distinct 64B lines | D1mw share |
|------|-----------------:|-----:|-------------------:|-----------:|
| PAT$0_α | 11 |  92B | **2** | 20.4% |
| PAT$1_α | 10 | 120B | **3** | 21.9% |
| PAT$2_α | 19 | 280B | **5** | 48.6% |
| PAT$3_α | 27 | 360B | **6** |  0.5% |

**D1mw ÷ lines is near-constant across the three hot blobs — 18.8k / 13.4k / 17.9k.**
That is the tell: **every distinct line an activation touches costs almost exactly one miss.**
These are COMPULSORY (cold) write misses, not conflict or capacity misses.

**⭐ This also explains why DB-2a (slot0 elide) capped at ~2.6% and could never have done better:**
PAT$2_α's line 0 holds offsets **8 and 16**. Slot0 elision removes the stores at 0/8, but
`xchain9_n0_α` still writes offset **16** — same line. **The elision could not remove a single
cache line from the working set**, so its ceiling was always "two stores", never "one line".
Any future rung whose headline metric is a MISS count must state which LINE it removes, not
which store.

DB-2c (cluster offsets into fewer lines) is therefore sound and quantifiable: PAT$2 5→2 lines is
−60% of its misses, PAT$1 3→2 is −33%. **Board-weighted ≈ −36% of treebank D1mw.** Real, but see §4.

## 4. ⛔ THE REDIRECT — WHY THE LINES ARE COLD AT ALL

7.4M I refs but **183,577 D1 write misses, of which 182,016 also miss LL (99.1%)**.
182,016 x 64B = **11.6MB of distinct first-written lines.** Stack memory is not supposed to
behave that way — it should oscillate in a hot window.

**Measured peak stack, plain vs `-fence` sibling (bisected by `ulimit -s`):**

| demo | ratio | plain | fence | collapse |
|------|------:|------:|------:|---------:|
| claws5-match       | 0.68 |  4096K | 4096K | **none** |
| json-match         | 0.83 |   256K |  256K | **none** |
| calculator-1-match | 1.90 | 16384K |  512K | **32x** |
| calculator-2-match | 2.34 | 16384K | 4096K | **4x**  |
| treebank-match     | 1.28 | 16384K |  256K | **64x** |

**THE CORRELATION IS EXACT: the three demos SLOWER than SPITBOL are precisely the three whose
pattern-match frames accumulate; the two already FASTER have bounded stacks.**

treebank at kt=288B and >4MB of stack = **~14k-28k nested activations that are never released
until the whole match completes.** Every one carves virgin stack, so every line it touches is a
compulsory miss. That is the whole of §3's cold-miss pool.

**Fence A/B on treebank (cachegrind, same input):**

| metric | plain | fence | delta |
|--------|------:|------:|------:|
| I refs        | 7,415,163 | 7,564,472 | **+2.0% (MORE instructions)** |
| D refs        | 3,355,838 | 3,449,376 | +2.8% |
| D1 write miss |   183,577 |    17,242 | **-90.6%** |
| LLd write miss|   182,016 |    15,933 | **-91.2%** |
| wall (5 runs, incl. startup) | 19 ms | 4 ms | **4.75x** |

**The fence variant executes MORE instructions and runs 4.75x faster.** SPITBOL on the same
program: 3 ms. This is the cleanest possible demonstration that treebank's gap is memory, and
specifically *compulsory write misses from unreleased frames* — not instruction count, not
frame layout, not the α prologue's store list.

## 5. WHAT THIS MEANS FOR THE RULED ORDER

- **R1 / DB-2c (line clustering) reaches ~36% of the cold-miss pool. Frame release reaches ~91%.**
  They attack the SAME pool, so they do not compose additively — frame release largely subsumes
  DB-2c on the slow three. **Frame release should precede R1**, and R1 then retains value mainly
  for whatever activation depth remains after release.
- **This is the missing justification for HEAT-0's RECORD-vs-WHACK classifier**, which is already
  specified in the goal file. s148 concluded "the whack is memory-not-time (A/B noise)" — but that
  measured releasing the **γ record**, not **moving rsp back**. They are different acts; this
  session measures the second one as worth ~10x the first. HEAT-0's prize is not the record
  release, it is the 91% compulsory-miss collapse.
- **The manual licenses exactly this.** SPITBOL manual p.125: FENCE "matches the null string and
  has no effect when the pattern matcher is moving left to right... however, if the pattern matcher
  is backing up to try other alternatives, and encounters FENCE, the match fails." A region that
  cannot be backtracked into holds no live retry state, so its frames are dead and releasable.
  The `-fence` siblings are the SOURCE-level version of that proof; the compiler-side version is
  HEAT-0's classifier (conservative-to-RECORD, WHACK-class = committed one-shot interiors).
- **claws5 (0.68) and json (0.83) are a DIFFERENT disease** — no stack collapse, so frame release
  buys them nothing. They remain R3/SPLICEMAP territory (s155: 97-100% of their heat is inside the
  anonymous runtime blob).

## 6. HONEST RESIDUE / WHAT I DID NOT DO

- **No fix implemented.** The classifier is a real rung with a real gate battery; it was not
  attempted this session and none of the four demos hit the 0.50 target. Board is unchanged.
- **Measurement discrepancy, unresolved, flagged rather than smoothed:** treebank's plain build
  ran to completion at the default 8192K in an early direct test but FAILED at 8192K in the §4
  sweep loop (hence 16384K there). The two runs differed in build (`SCRIP_SYMMAP=1` vs plain) and
  in shell nesting. The 4MB-vs-8MB boundary is therefore soft; the >16x collapse is not (fence
  needs 256K either way). **Re-derive the exact boundary before quoting a stack number.**
- Callgrind per-instruction attribution was ABANDONED as unreliable here: these blobs are entered
  by `jmp`, not `call`, so callgrind's `fn=` boundaries bleed and its bucketing captured only ~26%
  of program Dw. **The §3 census is static (objdump) + cachegrind per-symbol totals** — do not
  trust a callgrind function-level number on jmp-entry blobs without cross-checking it.
- The §3 line counts assume a 64B-aligned frame base. The real base is 16B-aligned, so the true
  per-activation line count is ±1. This does not affect the D1mw/lines constancy argument (which
  is measured, not derived) but it does bound how precisely DB-2c can be predicted in advance.

---

## 7. ⭐ THE CLASSIFIER SPEC, READ OFF THE `-fence` SIBLINGS (this is HEAT-0's admission test)

The `-fence` variants are not ad-hoc tuning. Every FENCE in them wraps **a deferred recursive
variable reference**, and in every case a PROGRESS-MAKING token has already been consumed before
the recursion is reached:

```
treebank:  group    = FENCE('(' word ARBNO(delim FENCE( *group | word )) ')')
           treebank = POS(0) ARBNO(FENCE(ARBNO(*group) delim)) RPOS(0)
calc-1:    A = V | I | FENCE('(' *X ')')
           F = A | FENCE('+' *F) | FENCE('-' *F)
           T = F FENCE(('*' | '/') *T | '')
           X = T FENCE(('+' | '-') *X | '')
```

Guards: `'('` · `delim` · `'+'` · `'-'` · `'*'` · `'/'`. **Zero exceptions across both programs.**

**SPITBOL manual Ch.9 p.122 states the identical condition for a DIFFERENT reason:** "The patterns
should be designed so that some progress has been made in the subject prior to encountering the
recursion. In this example, '(' and ',' in the LIST pattern serve that purpose." (p.123 then gives
the counter-case: `EXPRESSION = *EXPRESSION | ...` is a recursive plunge.)

**⭐ THE CONVERGENCE: the token that makes a recursive pattern WELL-FOUNDED is the same token that
makes its committed frame DEAD.** Progress before recursion means the recursive descent consumed
input the alternatives cannot re-derive, so retrying it differently cannot help — which is exactly
what FENCE asserts and exactly what licenses releasing the frame. The manual's termination rule and
the classifier's admission rule are one rule.

**Proposed HEAT-0 admission test (conservative-to-RECORD per the existing H0b spec):**
1. Node is `IR_MATCH_DEFER(V)` where `V` is self-referential (the s149 defer-of-VAR split already
   isolates this class; treebank `group`, calc `X`/`F`/`T` are its live instances).
2. Some element STRICTLY LEFT of it in the enclosing SEQ is a progress-making one-shot
   (LIT / ANY / SPAN / NOTANY / BREAK) that is committed at the time the recursion is entered.
3. Then the recursion's frame is releasable on the γ (success) edge.
4. Anything else -> RECORD. In particular the s142 canary class {expr_eval, 124, 143, 145}
   (retry-into-committed-`*P` load-bearing) must still fail admission — **run it FIRST**, per H0d.

This is checkable in LOWER on the IR graph with no new runtime state, and it is greppable
after the fact. It does NOT require the programmer to write FENCE — the `-fence` siblings become
the ORACLE for the transform (compile plain, expect fence-variant frame behaviour, identical output).

**Ceiling, measured not guessed:** treebank plain->fence is 4.75x wall and -90.6% D1mw. calc-1
(16384K->512K) and calc-2 (16384K->4096K) collapse too, so all three slow demos are in scope.
claws5/json are NOT (no collapse) and stay R3/SPLICEMAP.
