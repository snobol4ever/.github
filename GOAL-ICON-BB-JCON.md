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
- [x] Fix `~~x` double-complement round-trip (NUL skip + int/real coercion). `ae2d16f7`
- [x] Fix `~~generator` suspension (TT_CSET_COMPL in is_suspendable + coro_bb_cset_compl). `ae2d16f7`
- [x] Fix `to by` integer truncation of string/cset bounds (preserve pure-real path). `ae2d16f7`
- [x] Fix `to by` alternation args (every toby(A|B,...) only fires once — generator not resumed). `2f54cd84`
- [x] Fix `~~(A|B|C) ? move(5)` — scan with generative subject (TT_SCAN not suspendable). `2f54cd84`
- [x] Fix `to by` pure-real truncation (remove coro_bb_to_by_real fast-path; JCON always truncates). `b50d8180`
- [x] Fix cset image (CSETVAL sentinel slen=0xFFFF…; image() emits 'chars'; int/real cset ops coerce). `b50d8180`
- [x] Fix int ^ negative-int → truncate to integer per JCON rule. `b50d8180`
- [x] rung36_jcon_coerce PASS. rung36_jcon_numeric PASS.
- [ ] Fix `?x` random char of string/cset → moved to IJ-16 (cluster R, &random seeding step).
- [x] GATE-1..4. Commit. `b50d8180`

### IJ-8 — Lexicographic string comparison edge cases (Cluster H) ✅ `340bccc3`

- [x] bb_strrel: coerce int/real to decimal image string before strcmp.
- [x] bb_strrel: return STRVAL(rs) not raw descriptor.
- [x] rung37_str_relop.icn + .expected. GATE-1..4. Commit.
- Note: rung36_jcon_lexcmp still FAIL — blocked by IJ-12 mutual conjunction (every A & B).

### IJ-9 — Scan alternation resume (Cluster K) ⏳ PARTIAL `d1044104`

**every-as-expression fix landed (d1044104):**
- Removed `TT_EVERY` from `is_suspendable` — `every` never generates values to outer callers.
- `bb_eval_value(TT_EVERY)` returns `FAILDESCR` (all three sub-cases: TT_ASSIGN, TT_SEQ, generic).
- `lower.c`: `lower_expr` wrapper tracks `g_in_value_ctx`; `lower_every` emits `SM_BB_EVAL`
  (→ `bb_eval_value`) when ctx ≥ 2 (sub-expression), `SM_BB_PUMP_EVERY` when ctx ≤ 1 (stmt).
- `image(every write(1 to 5)) | "none"` → writes 1..5, produces `"none"`. ✅

**Architecture established (one4all `5a71bf11`):**
- `is_suspendable(TT_SCAN)` now returns 1 when subject OR body is generative.
- `coro_bb_scan_gen` extended: on β, re-installs body scan context (`body_subj`/`body_pos`),
  pumps `body_gen` β before advancing to next subject. Outer context saved/restored every tick.
- `is_scan_builtin_name()` added to scan_builtins.c/h.
- `coro_bb_fnc` loops on scan-builtin failure (upto/find/tab/move/etc.) to try next arg value.

**Root cause identified (sess 2026-05-13, Claude Sonnet 4.6):**
`coro_bb_scan_gen` on external β resumes `body_gen` β — this is WRONG per JCON semantics.
Each subject should contribute exactly ONE body execution (α tick). On external β, the scan
must advance to the NEXT subject (not resume the body).

Proof from `rung36_jcon_scan.expected` vs actual:
  Expected: `1, 5, 5`  — one value per subject (badc→1, edgf→5, x→5)
  Actual:   `2, 2, 1, 1, 4, 4, ...` — many values per subject (body β pumped)

Also confirmed by JCON JVM bytecode (`icn_76_scan_bfail → icn_77_β` = advances subject on
body exhaustion) and by running `every write(image(every write(("badc"|"edgf"|"x") ? write(upto(!&lcase)))) | "none")`
which produces the above doubled values.

**The fix:** In `coro_bb_scan_gen`, on β entry (`entry != α && z->body_live`):
  - Do NOT call `z->body_gen.fn(z->body_gen.ζ, β)`
  - Instead set `z->body_live = 0` immediately and fall through to advance subject
  This makes each subject contribute exactly one body value (from α), matching JCON semantics.

CAUTION: verify the fix does not break `every write((1 to 10) ? move(1))` (currently passing).
That test has non-generative body (move), so body β → FAIL already → subject advance. The fix
is structurally equivalent for non-generative bodies. For generative bodies, it changes behaviour
from "drain body then advance subject" to "advance subject after one body value" — which is correct.

- [ ] Fix `coro_bb_scan_gen` β: set body_live=0, skip body β, fall through to subject advance.
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

  one4all: d1044104  corpus: 04f24b8
  ir-run:  PASS=198 FAIL=37 XFAIL=30
  honest:  PASS=268 FAIL=1 ABORT=0   broker: 23/49
  Step:    IJ-9 PARTIAL — root cause of scan alternation bug identified (sess 2026-05-13).
           Fix: coro_bb_scan_gen on external β must NOT resume body_gen β.
           Instead: set body_live=0, fall through to advance subject immediately.
           Each subject contributes exactly ONE body α tick (JCON semantics).
           See detailed analysis in IJ-9 step above.
           Next: implement the fix, write rung37_scan_alt.icn, run GATE-1..4.
