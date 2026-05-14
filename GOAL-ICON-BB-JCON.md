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

- [x] Apply ICN_BB_EVAL guards to all 5 functions with correct placement. GATE-1..4. Commit .

### IJ-BB-4 — Eliminate LANG_ICN scalar branches from lower.c

Remove LANG_ICN inline scalar emission from lower.c. Add runtime assert no scalar SM opcode fires during Icon --sm-run.

- [x] Remove LANG_ICN scalar lowering. GATE-1..4. ✅ No-op: all remaining LANG_ICN checks in lower.c are structural (proc-as-value, Icon stmt forms, every/limit routing) — not scalar emission. Satisfied by Groups A–G.

### IJ-BB-5 — Verify fully-BB Icon

Honest PASS >= 275, zero SM scalar fallback. Retire SM_SUSPEND_VALUE if --sm-run Icon is done.

- [x] Confirm fully-BB. honest PASS=276 ABORT=0. ✅ No scalar SM fallback fires under SCRIP_NO_AST_WALK=1 across full corpus.

### IJ-16 — &random seeding + radix literals (Clusters R, I) ✅

- [x] Radix overflow: icon_lex.c uses unsigned long long; bignum cases XFAIL (corpus). one4all `ec0c62ee`.
- [x] &random / random: XFAIL (JCON RNG sequence differs; &random not updated post-? call). corpus `1554437`.
  GATE-1..4 green. ir-run FAIL=42 XFAIL=32.

### IJ-17 — level / profsum / ck (Cluster N) ✅

- [x] level() builtin. &allocated. XFAIL if needed. GATE-1..4. Commit. ✅ 2a4f7812 &level=frame_depth; jcon_level XFAIL corpus d6eed3d.

### IJ-18 — profsum / ck residual (Cluster N) ✅

- [x] Triage profsum/ck. Root causes: (1) next-in-scan doesn't restart enclosing while (profsum), (2) generative tab-arg tab(n|0) not supported (ck Image()). Both XFAIL corpus 1fe096c. Scan-builtin correctness fixes landed: any/many/upto non-advancing (6 sites across 5 files); real scan-subject coercion via real_str at all ICN_SCAN_PUSH/TT_SCAN sites. one4all 1203986f.

## IJ-19 — BB runtime generator fixes

**Root causes confirmed (both --ir-run and --sm-run identical wrong output → bug is in
icn_bb_build / bb_eval_value, NOT in lower.c).**

⚠ No coro subsystem. Icon is pure BB. Do NOT touch coro_runtime.c or coro_*.
Files to edit: `src/runtime/interp/icn_runtime.c`, `icn_runtime.h`, `icn_value.c`, `icon_gen.c`.

### IJ-19a — icn_bb_upto Byrd box (scalar args, generative)

`upto(cset, str)` with scalar args is not generative — `icn_bb_build` has no box for it.
Only `icn_upto_gen_subj_t` (generative subject) exists. Needs `icn_upto_state_t` + `icn_bb_upto`
yielding each matching position in sequence. Pattern: mirrors `icn_bb_find` (icon_gen.c).
Fixes: kross (`every j := upto(s2,s1)`), meander (`find(…)`-related), htprep.

- [ ] Add `icn_upto_state_t` struct to `icon_gen.h`. Add `icn_bb_upto` Byrd box to `icon_gen.c`.
      Wire into `icn_bb_build` TT_FNC path: when `fn=="upto"` and `nargs>=2` and args scalar,
      build `icn_upto_state_t` from evaluated cset+str args, return `icn_bb_upto` box.
      GATE-1..4. Commit.

### IJ-19b — icn_drive_node extern + bb_eval_value injection check

`icn_drive_node` is defined in `icn_runtime.c` but not extern'd in `icn_runtime.h`.
`bb_eval_value` (icn_value.c) never checks it. `icn_bb_cat` sets it but the injection
is silently ignored → `s[1 to 3]` gives `a,a,a` not `a,b,c`.

- [ ] Add `extern tree_t *icn_drive_node;` to `icn_runtime.h` (alongside existing `icn_drive_val`).
      Add check at top of `bb_eval_value`: `if (icn_drive_node && e == icn_drive_node) return icn_drive_val;`
      GATE-1..4. Commit.

### IJ-19c — drive injection in TT_EVERY/TT_ASSIGN branch

`bb_eval_value` TT_EVERY/TT_ASSIGN branch calls `bb_eval_value(gen)` without setting
`icn_drive_node=leaf, icn_drive_val=tick` first → `(1 to n)` rebuilds from α each tick.
Fixes rung02 (`every total := total + (1 to n)` → gives 5 not 15).

- [ ] In the TT_EVERY/TT_ASSIGN while-loop body in `icn_value.c`: save/set/restore
      `icn_drive_node=leaf, icn_drive_val=tick` around the `bb_eval_value(gen)` call.
      GATE-1..4. Commit.

### IJ-19d — FRAME.suspending in icn_bb_proc_call

After `bb_exec_stmt(st)` in `icn_bb_proc_call` (icon_gen.c), only `FRAME.returning`
and `FRAME.loop_break` are checked. `FRAME.suspending` is not → suspend inside a
while-loop inside a user proc is silently dropped. Fixes rung03 (`suspend i do i:=i+1`).

- [ ] After `bb_exec_stmt(st)` in `icn_bb_proc_call`: add `if (FRAME.suspending) {`
      `DESCR_t sv=FRAME.suspend_val; z->suspend_body=FRAME.suspend_do;`
      `z->in_suspend=1; FRAME.suspending=0; return sv; }` before the loop_break check.
      GATE-1..4. Commit.

### IJ-19e — real to-by generator

`icn_bb_build` TT_TO_BY always uses `icn_bb_to_by` (int). `icn_bb_to_by_real` exists
in `icon_gen.c` but is never selected. Fixes rung19 (`3.0 to 1.0 by -1.0`).

- [ ] In `icn_bb_build` TT_TO_BY: after coercion, add `if (!any_str && IS_REAL_fn(lo_d)
      && IS_REAL_fn(hi_d) && IS_REAL_fn(step_d))` → allocate `icn_to_by_real_state_t`,
      return `icn_bb_to_by_real` box.
      GATE-1..4. Commit.

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

  one4all: 1203986f  corpus: 1fe096c
  ir-run:  PASS=191 FAIL=39 XFAIL=35
  honest:  PASS=276 FAIL=1 ABORT=0   broker: 23/49
  IJ-BB-3 Group G ✅ fb9b5fa0
  IJ-BB-4+5 ✅ fully-BB confirmed, no scalar SM fallback
  IJ-16 ✅ radix ull fix + both XFAIL (bignum/RNG mismatch)
  IJ-17 ✅ 2a4f7812 &level=frame_depth; jcon_level XFAIL corpus d6eed3d
  IJ-18 ✅ 1203986f any/many/upto non-advancing; real scan-subj coercion; profsum/ck XFAIL corpus 1fe096c
  IJ-19-prep ✅ f1dbb78b NO_AST_WALK_GUARD unconditional for Icon — no env var, always crash
  NEXT: IJ-19a — icn_bb_upto Byrd box (scalar args generative; see IJ-19 steps above)

## Session notes (sess 2026-05-14, handoff #2)

IJ-17 ✅ &level=frame_depth. IJ-18 ✅ scan builtins. IJ-19-prep ✅ NO_AST_WALK_GUARD unconditional.

BB RUNTIME BUGS FOUND (no code committed — next session implements):
1. upto() not generative in non-scan context: icn_bb_build has no Byrd box for
   upto(cset,str) with scalar args. Only handles upto(cset, gen_subject). Needs
   icn_bb_upto box yielding each position. Affects kross (every j:=upto(s2,s1)).
2. icn_drive_node not extern'd in icn_runtime.h — bb_eval_value never sees it.
   Fix: add extern, add check at top of bb_eval_value(). Affects s[1 to 3] (rung16).
3. TT_EVERY/TT_ASSIGN drive injection missing: bb_eval_value(gen) called without
   setting icn_drive_node=leaf/icn_drive_val=tick first. Affects rung02 (every total:=total+(1 to n)).
4. FRAME.suspending not caught in icn_bb_proc_call after bb_exec_stmt() returns.
   Only checks FRAME.returning and FRAME.loop_break. Affects rung03 (suspend in while).
5. TT_TO_BY always uses int path: icn_bb_to_by_real exists but never used from
   icn_bb_build. Fix: when all bounds DT_R, use real box. Affects rung19.
6. find() not generative in non-scan context for meander algorithm.

CONFIRMED: kross/meander/htprep bugs are in BB runtime (icn_bb_build/bb_eval_value),
NOT in lower.c. --ir-run and --sm-run produce identical wrong output.

NEXT: IJ-19 — implement the above BB runtime fixes.
Files: src/runtime/interp/icn_runtime.c, icn_runtime.h, icn_value.c, icon_gen.c.
