# GOAL-ICON-BB-JCON.md — Icon ir-run FAIL triage

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Objective

Fix ir-run FAILs left after GOAL-ICON-BB-NATIVE. Steps by risk-to-reward.

## Remaining FAILs by cluster

| # | Cluster | Tests | Root cause |
|---|---------|-------|------------|
| C | Missing builtins — proc/image | rung36_jcon_args, rung36_jcon_record, rung36_jcon_lists, rung36_jcon_fncs1 | residual after IJ-3 |
| E | Missing builtins — string | rung36_jcon_endetab, rung36_jcon_prepro | `&error`/`$define` |
| H | Lex string comparison | rung36_jcon_lexcmp | upto(!cset) arg semantics |
| I | Radix literals | rung36_jcon_radix | large binary overflow |
| J | String builtins partial | rung36_jcon_string, rung36_jcon_string1 | repl/trim edge cases |
| K | Scan alternation | rung36_jcon_scan, rung36_jcon_scan1, rung36_jcon_scan2 | upto(!cset) arg semantics |
| L | &pos / &subject negative | rung36_jcon_substring | negative-index substring assignment |
| M | Keywords table | rung36_jcon_kwds | generative keywords (&features, &allocated, etc.) |
| N | Level / profsum / ck | rung36_jcon_level, rung36_jcon_profsum, rung36_jcon_ck | level() + &allocated |
| O | Output routing | rung36_jcon_htprep, rung36_jcon_meander, rung36_jcon_kross | while-loop/scan bug in in() |
| Q | stdin programs | rung36_jcon_mindfa, rung36_jcon_mffsol | algorithm logic (cset infra done) |
| R | Random | rung36_jcon_random | `&random` seeding |

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

**⚠️ BB RULE:** Every step touching a BB must first read `.github/jcon_irgen.icn`
(`ir_a_Call` + `ir_a_Ident`). Do not infer BB semantics from C source alone.

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

## Closed steps (trail)

IJ-1..6 ✅ TT_SEQ, table keys, proc/image/indirect, math/bitwise, detab/cset, augop.
IJ-7 ✅ `b50d8180` operator dispatch + coerce. Cluster G done.
IJ-8 ✅ `340bccc3` bb_strrel: coerce int/real to string before strcmp.
IJ-9 ✅ `4008701c` scan_gen: advance subject not resume body. rung37_scan_alt.
IJ-10 ✅ `259e1aec` ICN_KW_SWAP. Cluster L partial.
IJ-11 ✅ icn_kw_read(); type()/image() cset fixes. Cluster M partial.
IJ-12 ✅ `6b20b4a2` static parent-frame fallback for recursive procs. Cluster P.
IJ-13a ✅ `d2453ecc` ast_gc_clone: GC_strdup sval only for string nodes.
IJ-13b ✅ `2d5567ca` &input/&output/&errout → INTVAL(0/1/2).
IJ-13c ✅ `1e4a6d7f` DT_FH sentinel; write/read/open route via DT_FH. rung37_file_io.
IJ-14 ✅ `00cec4c3` coro_bb_iterate static-alias (GC_strdup each tick).
IJ-15 ✅ `52db8b96` cset literal/builtin/ops. rung37_cset_ops.
IJ-CORO-1..5 ✅ `dfb2497c` delete swapcontext machinery; rename coro_*→icn_*; delete SM_RESUME/SM_GEN_TICK; clean includes.
IJ-BB-1 ✅ Gap audit: 7 Icon-reachable TT_* kinds missing bb_eval_value handlers.
IJ-BB-2 ✅ `601af0e0` 7 handlers added (TT_INTERROGATE, TT_GLOBAL, TT_INDIRECT, TT_NAME, TT_RECORD, TT_VLIST, TT_OPSYN).
IJ-BB-3 Groups A–E, H ✅ ICN_BB_EVAL in lower_strlit/ilit/flit/nul/var/keyword/unary/binary/augop/sections. `767d9a2d`.

## Active steps

### IJ-BB-3 Group G — calls+records (IN PROGRESS)

Add `ICN_BB_EVAL(t)` to `lower_vlist`, `lower_opsyn`, `lower_makelist`, `lower_record`, `lower_fnc`.

**lower_fnc placement rule:** guard fires **after** the EVAL-thunk special case and **only when `t->v.sval != NULL`**. Icon-style calls (`sval==NULL`, `c[0]` is callee) must not be intercepted — `bb_eval_value` TT_FNC expects the name in `sval`. Naïve guard at top regresses rung36_jcon_nargs (args() returns wrong count).

- [ ] Apply ICN_BB_EVAL guards to all 5 functions with correct placement. GATE-1..4. Commit.

### IJ-BB-4 — Eliminate LANG_ICN scalar branches from lower.c

Remove LANG_ICN inline scalar emission from lower.c. Add runtime assert no scalar SM opcode fires during Icon --sm-run.

- [ ] Remove LANG_ICN scalar lowering. GATE-1..4. Commit.

### IJ-BB-5 — Verify fully-BB Icon

Honest PASS >= 275, zero SM scalar fallback. Retire SM_SUSPEND_VALUE if --sm-run Icon is done.

- [ ] Confirm fully-BB. GATE-1..4. Commit.

### IJ-16 — &random seeding + radix literals (Clusters R, I)

- [ ] Fix &random r/w. Fix radix overflow. rung37_random_radix.icn. GATE-1..4. Commit.

### IJ-17 — level / profsum / ck (Cluster N)

- [ ] level() builtin. &allocated. XFAIL if needed. GATE-1..4. Commit.

## Done when

  ir-run PASS >= 230. Honest PASS >= 268. All rung37 tests passing. GATE-1..4 green.

## Invariants

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: broker PASS=23. Never regress.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. One cluster per step, own commit.
6. New test source has matching .expected in same commit.
7. No corpus source modified to work around runtime bugs.
8. scrip Icon requires explicit `;` after every statement. All rung37_*.icn must use semicolons.

## Architecture note

icn_bb_* C functions = EMIT_BINARY_BROKERED box implementations (same pattern as rt_bb_arb, rt_bb_len in rt.c). emit_bb_icon_* templates emit x86: mov rdi/esi, call@PLT, test, jne/jmp. Correct BROKERED form per ARCH-x86.md.

## Watermark

  one4all: dfb2497c (session start)  corpus: 2ba5a92
  ir-run:  PASS=192 FAIL=43 XFAIL=30  (Group G partial: vlist/opsyn/makelist/record ✅; lower_fnc needs sval guard)
  honest:  PASS=273 FAIL=2 ABORT=0   broker: 23/49
  rung36_jcon_arith FAIL is pre-existing (pointer value in output).
  NEXT: IJ-BB-3 Group G — fix lower_fnc sval guard, commit all 5 functions
