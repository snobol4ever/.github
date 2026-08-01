# FINDING-2026-08-01-CLAUDE-SN4-RTX-S231-ASLR-ROOTS-M4-OSCILLATION-AND-MIN-RAIL-LANDS.md

**Session:** s231 (2026-08-01) · **Branch:** `tag-renumber-s229` · **HEAD:** SCRIP `0bc20587`

---

## 1. FIVE MORE HARDCODED OLD TAG NUMBERS (emitter descriptor mints)

The s230 cursor directed: "sweep the SMALL old tags (S=1 P=3 A=4 T=5 R=7) in emitter code using
the `[reg+0]`=tag / `[reg+4]`=slen reading rule — grep CANNOT do this one."

A two-pass sweep found 7 small-tag-shaped immediates in register destinations (46 candidate sites
pre-filtered) and 9 in memory destinations. Of these, five were genuine descriptor tag stores —
confirmed by the `[reg+0]=TAG / [reg+4]=SLEN` reading rule:

| file | site | old literal | old meaning | new layout meaning |
|---|---|---|---|---|
| `bb_call.cpp` marshal_call_arg | LIT_INTEGER arm | `(long)6` | old DT_I | 0b110 CHARS\|REAL — NOT A TAG |
| `bb_call.cpp` marshal_call_arg | LIT_REAL arm | `(long)7` | old DT_R | 0b111 — descr.h says explicitly "not a tag" |
| `bb_call.cpp` marshal_call_arg | LIT_STRING arm | `(long)1` | old DT_S | 0b001 NUMERIC — NOT A TAG |
| `bb_gather.cpp` result mint | integer result | `(long)6` | old DT_I | same |
| `bb_mapgrep.cpp` result mint | integer result | `(long)6` | old DT_I | same |

`bb_call.cpp` already used `DT_I` and `DT_FAIL` symbolically at 5 other sites in the same file —
the same already-symbolic-vs-hardcoded inconsistency that s230 found for `DT_FAIL`.

**HONESTY: CORRECT BY READING, UNGATED BY MEASUREMENT.** Probed 60 corpus programs via
`scrip --compile` + grep on the template's own "marshal argN = LIT_*" comment marker: ZERO reach
these arms. A direct `F(41)`/`F(1.5)`/`G('hello')` probe is CORRECT on the pre-fix binary. This
is the 0(f) arm class: wrong constants on a path the current corpus does not execute.

Watermark held EXACTLY. m3 fail set byte-identical pre- and post-fix (verified by md5 of FAIL(m3)
line). Committed `9dcc0851`.

**NEW RULE EARNED:** The `util_tag_layout_verify.py` gate sweeps `.S` files but not `.cpp`
templates. The memory-destination immediate sweep (`x86("mov", FRQ/FR/ZTOS/GVA..., (long)N)`)
must be added to the gate or re-run manually on every renumber. This is a third syntactic class
(after register-destination and AT&T-asm) that the existing gate is blind to.

---

## 2. THE TAG-LAYOUT QUESTION: WHY S=0x02 AND I=0x03 DO NOT COLLIDE, AND WHY I=0x01 WOULD BREAK

The session included the question: "Should not I=0x01?" — since S=0x02 and I=0x03 differ only
in bit 0, and having `I` carry the CHARS bit looks wrong.

Brute-forced over all tag pairs, all 8 combined predicates:

```
SHIPPED  (I=0x03): SNUL=0x00 S=0x02 I=0x03 R=0x05  -> ALL 8 PREDICATES HOLD
PROPOSED (I=0x01): SNUL=0x00 S=0x02 I=0x01 R=0x05  -> 2 FAILURES: BOTH_INT(I,R), BOTH_INT(R,I)
```

`BOTH INT` is `and eax,ecx ; cmp eax,DT_I`. With I=0x01 and R=0x05: `I & R = 0x01 = DT_I` — a
mixed INT/REAL pair falsely selects the integer arm. `I=0x01` makes DT_I a strict SUBSET of DT_R
(0b001 ⊂ 0b101), which is the exact move `descr.h`'s comment bans by name.

The shipped I=0x03 works because it holds bit 1 (CHARS) that R lacks, so only `I & I` yields
0x03. The name "CHARS" is misleading for an integer — it does disambiguation work, not type work.
`is_string(I)` is correct: `0x03 & DT_NOTSTR_MASK = 0x03 & 0xFFFFFFFD = 0x01 ≠ 0`, so DT_I
does not read as a string.

---

## 3. m4 OSCILLATION ROOT-CAUSED: ASLR

s230 recorded: "m4 OSCILLATES 275/41/1 (DIVERGE 2) ↔ 276/40/1 (DIVERGE 3) on
`151_pat_arbno_inline_fence_backtrack`, ONE unchanged binary. I CANNOT ATTRIBUTE IT."

**CAUSE: ASLR (address-space layout randomization).** One binary, run 12 times:
- ASLR ON: 9/12 Bus error (empty output), 3/12 correct output — two hash members
- ASLR OFF (`setarch -R`): 12/12 deterministic, all Bus error (still wrong, but stable)

The fault signal itself flips between SIGBUS and SIGSEGV depending on layout — the signature of
a wild or misaligned pointer whose consequence depends on what happens to be mapped at the
randomized address. The program has a real bug; ASLR makes it probabilistic.

**FALSIFIED:** `-no-pie` as the cause. Tested: `-no-pie` link → 8/12 Bus error, still
nondeterministic. The REPO-SCRIP.md note about TEXTREL/PIE does not explain this program.

**`160_pat_alt_inner_gen_resume`** — same class. ASLR ON: 5/5 hash A, 5/5 hash B across 10
runs. ASLR OFF: 10/10 deterministic (one hash, wrong). Set CLOSED: `{d41d8cd9, ba109c42}`.
s217/s219/s220 each recorded different memberships because they ran N=1 against a 2-member set.

**`413_arith_mixed` and `W06_len`** — s220 quarantine does NOT reproduce at HEAD. Both 10/10
stable and correct (= ref) under ASLR ON. These were likely transient noise at s220 and are not
quarantine members at `0bc20587`.

**CONSEQUENCE:** `setarch -R` makes m4 fully gradeable. Three consecutive full-suite runs under
`setarch -R` → byte-identical: **m3 276/41/0 · m4 275/41/1 · DIVERGE=2 STABLE**. The two
DIVERGE programs under this watermark are `140_pat_eval_double_fn_trick` (m3 segfaults, m4 does
not) and `151` (m3 segfaults deterministically, m4 has the ASLR-driven crash). All 41 m3 fails
and 41 m4 fails are ARBNO/FENCE/capture — the ζ-ladder's territory.

---

## 4. MIN-OF-N BENCHMARK RAIL

`scripts/bench_min_of_n.sh` committed `0bc20587`. This instrument has blocked every speed claim
for four sessions (s220/s222/s224/s228 each deferred it).

**Why MIN, not MEDIAN:** Wall time = floor + non-negative noise. An interfering process can only
make a run SLOWER. MIN is monotone-stable — more rounds can only lower it, never flip a verdict.
s224 measured the median WORSENING with more rounds (1.071× → 1.922× on an unchanged binary),
falsifying "the window was too short" as the explanation.

**Two-sided validation (SCRIP_RTX_ARITH on/off, N=5):**

| program | A=on (ms) | B=off (ms) | B/A | note |
|---|---|---|---|---|
| arith_mixed | 532 | 2034 | **3.823×** | |
| arith_int | 1035 | 1567 | **1.514×** | |
| arith_loop | 17 | 23 | **1.353×** | |
| fibonacci | 323 | 326 | 1.009× | auto-flagged ~null(<1.10×) |

`fibonacci` is CALL-bound and never routes through ARITH — the ladder's own prediction.
Positive on positive, null on null.

**Full N=4 board (all 21 benchmarks, gates untouched):**

| program | min(ms) | spread% | note |
|---|---|---|---|
| arith_int | 1102 | 6 | |
| arith_loop | 18 | 0 | |
| arith_mixed | 555 | 2 | |
| arith_str | 378 | 7 | |
| **eval_dynamic** | **82312** | 5 | ⭐⭐ see §5 |
| eval_fixed | 191 | 8 | |
| fibonacci | 326 | 10 | |
| func_call | 1197 | 9 | |
| func_call_overhead | 1212 | 3 | |
| indirect_dispatch | 7 | 14 | |
| mixed_workload | 367 | 407 | NOISY |
| op_dispatch | 37 | 2 | |
| pattern_bt | 102 | 12 | |
| pattern_bt_deep | 1428 | 93 | NOISY |
| roman | 341 | 43 | NOISY |
| string_concat | 15 | 6 | |
| string_manip | 1118 | 97 | NOISY |
| string_pattern | 1635 | 88 | NOISY |
| table_access | 1227 | 49 | NOISY |
| table_churn | 1195 | 6 | |
| var_access | 282 | 13 | |

NOISY rows confirm the s201 hugepage bimodality is real. The minima of those rows are STABLE
(board ran to completion without refusal). All numbers are RT_OPT=-O0 per RULES.md O2-DIRECTED-ONLY.

---

## 5. BOARD HEADLINE: eval_dynamic IS THE DOMINANT LEVER

`eval_dynamic`: 82,312 ms. `eval_fixed`: 191 ms. Same 1M iterations of `EVAL()`.
Difference: `eval_dynamic` constructs a fresh string `'N + ' N` each call; `eval_fixed` evaluates
the constant `'X + 1'` each call. Ratio: **430×**. At 82 µs per call, the compile itself is
the cost — and `eval_fixed` at 191 µs / 1M = 0.19 µs per call implies a compile CACHE.

**Manual Ch.9 semantics (read this session):** EVAL-of-a-string must compile the argument as a
SPITBOL expression. There is no semantic shortcut — a fresh string MUST be compiled fresh.
The question is whether the 430× gap is (a) a real cache in `eval_fixed`'s path that
`eval_dynamic` legitimately misses, (b) a cache that should be keyed on the compiled IR not the
string, or (c) an implementation artifact (e.g. the fixed string resolves to a compile-once
CODE object on first call and subsequent calls bypass compilation).

**This outranks the `VARVAL_fn` queue by measurement.** The census ranked `VARVAL_fn` at 29M
entries across 20 programs; `eval_dynamic` costs 430× a 191ms baseline on a single program and
dominates the whole board. Root-cause first; port second.

**NOT a porting target this session.** Scoped, not started. Lon's routing.
