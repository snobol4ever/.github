# GOAL-ICON-BB-JCON.md — Icon ir-run FAIL triage

**Repo:** one4all + corpus + .github
**Carved:** 2026-05-12  **Prereq:** GOAL-ICON-BB-NATIVE ✅ (one4all `7efdf09a`)

## Objective

Fix the 39 ir-run FAILs left after GOAL-ICON-BB-NATIVE. Steps ordered by risk-to-reward.

## Baseline → Current

  Baseline (7efdf09a): ir-run PASS=196 FAIL=39. honest PASS=259.
  Current  (ce8c1211): ir-run PASS=198 FAIL=37. honest PASS=268. broker 23/49.

## Remaining FAILs by cluster

| # | Cluster | Tests | Root cause |
|---|---------|-------|------------|
| G | Coerce / type conversion | rung36_jcon_coerce, rung36_jcon_numeric | `to`-loop truncation; `~~`; `?` random |
| C | Missing builtins — proc/image | rung36_jcon_args, rung36_jcon_record, rung36_jcon_lists, rung36_jcon_fncs1 | residual after IJ-3 |
| E | Missing builtins — string | rung36_jcon_endetab, rung36_jcon_prepro | `&error`/`$define` |
| H | Lex string comparison | rung36_jcon_lexcmp | edge cases |
| I | Radix literals | rung36_jcon_radix | large binary overflow |
| J | String builtins partial | rung36_jcon_string, rung36_jcon_string1 | repl/trim edge cases |
| K | Scan alternation | rung36_jcon_scan, rung36_jcon_scan1, rung36_jcon_scan2 | alternation resume |
| L | &pos / &subject negative | rung36_jcon_subjpos, rung36_jcon_substring | negative positions |
| M | Keywords table | rung36_jcon_kwds | missing &keywords entries |
| N | Level / profsum / ck | rung36_jcon_level, rung36_jcon_profsum, rung36_jcon_ck | level() + &allocated |
| O | Segfaults | rung36_jcon_htprep, rung36_jcon_meander, rung36_jcon_kross | crashes |
| P | Queens mutual conjunction | rung36_jcon_queens, rung36_jcon_genqueen | `every A & B` |
| Q | stdin programs | rung36_jcon_parse, rung36_jcon_mindfa, rung36_jcon_mffsol | stdin fixtures |
| R | Random | rung36_jcon_random | `&random` seeding |

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

**⚠️ BB RULE:** Every step touching a BB must first read `.github/jcon_irgen.icn`
(`ir_a_Call` + `ir_a_Ident`). Do not infer BB semantics from C source alone.

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS ≥ prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS ≥ 268

## Steps

### IJ-1..IJ-6 ✅ DONE

IJ-1 `c5bb0775` TT_SEQ filter conjunction. IJ-2 `8529aec9` table key injection.
IJ-3 `248379b3` proc()/image()/indirect callee. IJ-4 math/bitwise builtins.
IJ-5 `8ecc814a` detab/entab/cset canonical. IJ-6 augop (already passing).

### IJ-7 — Operator string invocation + type coercion (Cluster G) ⏳ partial `ce8c1211`

**Done:** `icn_try_call_builtin_by_name` now dispatches all unary/binary operator
symbols: `+/-/*/ !/\\/~/?` (unary), arithmetic, numeric relops, string relops,
identity, `[]`, cset `++/--/**`. rung37_coerce.icn ✅.

**Remaining in rung36_jcon_coerce:**
- `toby`: `i to j by k` with real/cset/string bounds → truncate to integer.
  `coro_bb_to_gen` uses raw reals; need integer truncation when bounds coerce to int.
- `~~x`: double cset complement should round-trip cleanly.
- `?x`: random char of string/cset (already in unary `?` handler, debug needed).
- `rung36_jcon_numeric`: cset `--` on int args; `^` with negative exponent.

- [x] Add unary/binary operator dispatch in icn_try_call_builtin_by_name.
- [x] rung37_coerce.icn + .expected.
- [ ] Fix `to` loop integer truncation of real/string/cset bounds.
- [ ] Fix `~~x` double-complement round-trip.
- [ ] GATE-1..4. Commit.

### IJ-8 — Lexicographic string comparison edge cases (Cluster H)

- [ ] Diff rung36_jcon_lexcmp expected vs actual. Fix.
- [ ] rung37_str_relop.icn. GATE-1..4. Commit.

### IJ-9 — Scan alternation resume (Cluster K)

- [ ] Fix `(A|B) ? body` — resume subject generator on body failure.
- [ ] rung37_scan_alt.icn. GATE-1..4. Commit.

### IJ-10 — &pos / &subject negative positions (Cluster L)

- [ ] Audit icn_pos_normalize. rung37_neg_pos.icn. GATE-1..4. Commit.

### IJ-11 — Missing &keywords table entries (Cluster M)

- [ ] Diff rung36_jcon_kwds. Implement missing stubs.
- [ ] rung37_keywords.icn. GATE-1..4. Commit.

### IJ-12 — Queens mutual conjunction `every A & B` (Cluster P)

- [ ] Read JCON ir_a_Mutual. Fix TT_MUTUAL cross-product.
- [ ] rung37_mutual.icn. GATE-1..4. Commit.

### IJ-13 — Segfaults: htprep / meander / kross (Cluster O)

- [ ] ASAN build. Fix crashes. GATE-1..4. Commit per fix.

### IJ-14 — stdin programs: mindfa / mffsol (Cluster Q)

- [ ] Write .stdin fixtures. GATE-1..4. Commit.

### IJ-15 — parse program (Cluster Q)

- [ ] Diff expected. Fix root cause. GATE-1..4. Commit.

### IJ-16 — &random seeding + radix literals (Clusters R, I)

- [ ] Fix &random r/w. Fix radix overflow.
- [ ] rung37_random_radix.icn. GATE-1..4. Commit.

### IJ-17 — level / profsum / ck (Cluster N)

- [ ] level() builtin. &allocated keyword. FP XFAIL if needed. GATE-1..4. Commit.

## rung37_* test sources

| File | Step | Status |
|------|------|--------|
| rung37_proc_lookup.icn | IJ-3 | ✅ |
| rung37_math_builtins.icn | IJ-4 | ✅ |
| rung37_string_format.icn | IJ-5 | ✅ |
| rung37_augops.icn | IJ-6 | ✅ |
| rung37_coerce.icn | IJ-7 | ✅ |
| rung37_str_relop.icn | IJ-8 | ⏳ |
| rung37_scan_alt.icn | IJ-9 | ⏳ |
| rung37_neg_pos.icn | IJ-10 | ⏳ |
| rung37_keywords.icn | IJ-11 | ⏳ |
| rung37_mutual.icn | IJ-12 | ⏳ |
| rung37_random_radix.icn | IJ-16 | ⏳ |

## Done when

  ir-run PASS ≥ 230. Honest PASS ≥ 268. All rung37 tests passing. GATE-1..4 green.

## Invariants

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: broker PASS=23. Never regress.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. One cluster per step, own commit.
6. New test source has matching .expected in same commit.
7. No corpus source modified to work around runtime bugs.

## Watermark

  one4all: ce8c1211  corpus: cea9548
  ir-run:  PASS=198 FAIL=37 XFAIL=30
  honest:  PASS=268 FAIL=1 ABORT=0   broker: 23/49
  Step:    IJ-7 partial — to-loop + ~~ + ? remaining.
