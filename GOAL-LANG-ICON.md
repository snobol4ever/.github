# GOAL-LANG-ICON.md — Icon Frontend Ladder

**Repo:** one4all
**Done when:** Icon standard library procedures pass under all three modes
(--ir-run, --sm-run, --jit-run). Rung ladder reaches rung-36. Icon generator
boxes (E_TO, E_EVERY, E_SUSPEND, E_BANG, E_ALT_GEN) work under SM+BB.

**Cross-pollination:** icn_runtime.c, icon_gen.c improvements benefit
Raku (which shares icn_proc_table and icn_call_proc). BB broker improvements
(bb_broker, bb_boxes.c) benefit SNOBOL4 pattern matching.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_icon.sh             # PASS=5
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=45
bash /home/claude/one4all/scripts/test_crosscheck_icon.sh        # PASS=4 (3-mode divergence check)
bash /home/claude/one4all/scripts/test_icon_ir_all_rungs.sh      # rung01-36; --rung RUNG to target one
# Per-rung gates for IC-7:
bash /home/claude/one4all/scripts/test_icon_ir_rung_30.sh        # abs/max/min/sqrt/seq
bash /home/claude/one4all/scripts/test_icon_ir_rung_31.sh        # sort/sortf
bash /home/claude/one4all/scripts/test_icon_ir_rung_32.sh        # string retval every
bash /home/claude/one4all/scripts/test_icon_ir_rung_33.sh        # case expressions
bash /home/claude/one4all/scripts/test_icon_ir_rung_34.sh        # null/nonnull test
bash /home/claude/one4all/scripts/test_icon_ir_rung_35.sh        # block bodies + table str/str
bash /home/claude/one4all/scripts/test_icon_ir_rung_36.sh        # JCON suite (xfail=23 expected)
```

---

## Architecture reminder

```
.icn → icon_parse() → Program* [LANG_ICN]   (no AST layer — FI-2 done)
    --ir-run  → execute_program() → interp_eval() with ICN_CUR frame stack
    --sm-run  → sm_lower() → SM_BB_PUMP per stmt → bb_broker(BB_PUMP)
    --jit-run → sm_lower() → SM_BB_PUMP → sm_codegen() → sm_jit_run()

Generator boxes in icon_gen.c:
    E_TO       → icn_bb_to       (lo/hi/cur)
    E_TO_BY    → icn_bb_to_by    (lo/hi/step/cur)
    E_ITERATE  → icn_bb_iterate  (str/len/pos)
    E_SUSPEND  → icn_bb_suspend  (ucontext coroutine)
    E_FNC find → icn_bb_find     (needle/haystack/pos)
```

---

## Rung ladder — all modes, x86

Current baseline: rung01–11 59/59 PASS under --ir-run (GOAL-ICN-BROKER done).
Rung 12–36 are the ladder for this goal.

### Phase 1 — IR-run rung ladder (rung 12–36)

- [x] **IC-1** — rung01–11: 59/59 PASS --ir-run. (done, GOAL-ICN-BROKER)

- [x] **IC-2b** — Complete ALL goal-directed-evaluation ops as BB boxes in `icon_gen.c`
  and wire into `icn_eval_gen()`. No rung work until every GDE op has a box.
  Raku shares `icn_eval_gen`; this unblocks both ladders.

  Missing boxes to write (all in `src/frontend/icon/icon_gen.c` + declared in `icon_gen.h`,
  registered in `icn_eval_gen()` switch in `src/runtime/interp/icn_runtime.c`):

  Note: `E_SCAN` is the **same IR node as SNOBOL4 matching** — shared implementation,
  already handled correctly by the oneshot fallback in `icn_eval_gen`. Do NOT add a scan box.

  | Op | Box to write | State struct | Notes |
  |---|---|---|---|
  | `E_LIMIT` | `icn_bb_limit` | `icn_limit_state_t: gen, max, count` | `E \ N`: drive gen, yield each value, stop after N |
  | `E_EVERY` | `icn_bb_every` | `icn_every_state_t: gen, body (EXPR_t*)` | drive gen to exhaustion, eval body per tick |
  | `E_BANG_BINARY` | `icn_bb_bang_binary` | `icn_bang_binary_state_t: proc_expr, arg_box, cur_arg` | `E1 ! E2`: call E1 with successive values from E2 |
  | `E_SEQ_EXPR` | `icn_bb_seq_expr` | `icn_seq_state_t: children[], n, last_box` | `(E1;E2;…;En)`: eval prefix, last child is the generator |

  Gate: `bash scripts/test_smoke_icon.sh` still PASS=5; all five new boxes compile clean;
  `icn_eval_gen` returns a valid box (not `icn_oneshot_box` fallthrough) for each op.
  Smoke test for each box added to `icon_gen.c` unit test block.

- [x] **IC-2** — rung12: string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`),
  `*s` (string size).
  Gate: test_icon_ir_rung_12_strrelop_size.sh PASS.

- [x] **IC-3** — rung13: tables (`table()`, key lookup, `!T` iteration).
  Gate: test_icon_ir_rung_13_tables.sh PASS=5/5. DONE 2026-04-15.
  Bugs fixed: table() union clobber (d.s=NULL after d.tbl), delete() wrong hash (h*31 vs djb2), Icon E_ASSIGN missing E_IDX branch.

- [x] **IC-4** — rung14: limit (E \ N) — corpus rung14 is limit tests, not lists.
  Gate: test_icon_ir_rung_14_limit.sh PASS=5/5. DONE 2026-04-15.

- [x] **IC-5** — rung15+: real output format, pow (always real), E_TO_BY real step, swap(), string subscript/section, list builtins, global/initial, records, str/type builtins.
  DONE 2026-04-16: rung24 records PASS=5/5, rung21/25 initial PASS=12/12.
  Fixes: polyglot_init E_RECORD registration, ICN E_FNC sc_dat_find_type lookup,
  ICN E_ASSIGN E_FIELD lvalue, icn_init_save_frame() for initial persistence.
  Remaining IC-6: rung13 alt-gen(2), rung22 put_bang(1), rung23 key(1),
  rung16 sub_every(1), rung18 relop(1), rung19 pow(1), rung28 trim_map(1), rung29 image(1).
  Gate: smoke PASS=5, broker PASS=41, rung01-11 PASS=59. HEAD 7a64e8f9.

- [x] **IC-6** — rung01–29 PASS=156/156 FAIL=0 confirmed (2026-04-16, session 14).
  Corpus recount: all 7 suspected remaining failures (rung22 put_bang, rung23 key,
  rung16 sub_every, rung18 relop, rung19 pow, rung28 trim_map, rung29 image) were
  already passing from session 13 fixes. No new work needed.
  Gates: smoke PASS=5, broker PASS=45 FAIL=0, rung01-29 PASS=156/156. HEAD 37d45f96.

- [ ] **IC-7** — rung30–35: misc builtins, sort/sortf, string retval every, case, null-test, block bodies.
  Baseline (2026-04-16): rung30 0/5, rung31 0/5, rung32 4/5, rung33 1/5, rung34 1/5, rung35 7/7.
  Gate scripts (all rewritten for --ir-run, self-contained, xfail-aware):
    `bash scripts/test_icon_ir_rung_30.sh`  — abs/max/min/sqrt/seq builtins
    `bash scripts/test_icon_ir_rung_31.sh`  — sort(L) / sortf(L,n)
    `bash scripts/test_icon_ir_rung_32.sh`  — string-return-value in every
    `bash scripts/test_icon_ir_rung_33.sh`  — case/of/default expressions
    `bash scripts/test_icon_ir_rung_34.sh`  — null test (\x, \=x)
    `bash scripts/test_icon_ir_rung_35.sh`  — block bodies + table str/str (PASS=7/7 already)
  Overall gate: `bash scripts/test_icon_ir_all_rungs.sh` — now covers rung01–36,
    xfail-aware, --rung/--scrip/--corpus switches, timeout 30s for rung36.
  Known root causes to fix:
    rung30: abs()/max()/min()/sqrt()/seq() builtins missing from Icon E_FNC dispatch
    rung31: sort()/sortf() builtins missing
    rung32 (1 fail): strret_every — proc returning string, every over call yields only first
    rung33 (4 fail): E_CASE not evaluated (case_no_default passes — parse ok, dispatch missing)
    rung34 (4 fail): \x (null test) and \=x (nonnull test) unimplemented

- [ ] **IC-8** — rung36: JCON integration suite (75 tests).
  Baseline (2026-04-16): PASS=2 FAIL=50 XFAIL=23 TOTAL=75.
  Gate: `bash scripts/test_icon_ir_rung_36.sh` — xfail=23 known-unimplemented (co-expressions,
    large integers, &error trapping, etc.). Goal: reduce FAIL toward 0; XFAIL is acceptable.
  Note: test_icon_ir_rung_36.sh rewritten for --ir-run (was JVM-era jasmin script).

### Phase 2 — Icon standard library procedures

Install the standard Icon ilib procedures as .icn files and wire them:

- [ ] **IC-12** — Install Icon ilib subset.
  Script: `scripts/install_icon_ilib.sh` — fetches icon-lang.org ilib subset
  (strings.icn, lists.icn, sets.icn, tables.icn, sort.icn) into
  `/home/claude/corpus/programs/icon/ilib/`.
  Gate: files present, scrip parses them without error.

- [ ] **IC-13** — `strings.icn`: `center/left/right`, `trim`, `map`, `repl`, `reverse`.
  Write test file `test/icon/test_strings_lib.icn`. Run under --ir-run.
  Gate: all 6 procs produce correct output vs Icon reference.

- [ ] **IC-14** — `lists.icn`: `lsort`, `lreverse`, `lmap`, `lfind`.
  Write test file `test/icon/test_lists_lib.icn`.
  Gate: PASS under --ir-run.

- [ ] **IC-15** — `tables.icn`: `keylist`, `vallist`, `tmerge`.
  Write test file `test/icon/test_tables_lib.icn`.
  Gate: PASS under --ir-run.

### Phase 3 — SM-run (BB_PUMP over generators, x86)

- [ ] **IC-16** — rung01–11 under --sm-run.
  Each stmt routes via SM_BB_PUMP → icn_eval_gen → bb_broker.
  Gate: 59/59 PASS.

- [ ] **IC-17** — rung12–20 under --sm-run.
  Fix any sm_lower.c or bb_broker gaps revealed.
  Gate: all passing rungs under --ir-run also pass under --sm-run.

- [ ] **IC-18** — E_EVERY, E_ALT_GEN, E_BANG, E_LIMIT box implementations.
  Write missing BB boxes in icon_gen.c:
    `icn_bb_every`    — drives inner generator, runs body per tick
    `icn_bb_alt_gen`  — alternation: try first gen then second
    `icn_bb_bang`     — `!list` — iterate list elements
    `icn_bb_limit`    — `gen \ n` — limit to n ticks
  Gate: every/bang/limit tests pass under --sm-run and --ir-run.

### Phase 4 — JIT-run (x86 in-memory code gen)

- [ ] **IC-19** — rung01–11 under --jit-run.
  Gate: 59/59 PASS.

- [ ] **IC-20** — rung12–20 under --jit-run.
  Gate: all diffs vs --sm-run empty.

---

## Missing BB boxes to write (IC-18 detail)

```c
/* icn_bb_every — E_EVERY: drive gen, run body per tick */
typedef struct { bb_node_t gen; EXPR_t *body; } icn_every_state_t;
DESCR_t icn_bb_every(void *zeta, int entry);

/* icn_bb_alt_gen — E_ALT_GEN: try gen[0] then gen[1] */
typedef struct { bb_node_t g[2]; int which; } icn_alt_gen_state_t;
DESCR_t icn_bb_alt_gen(void *zeta, int entry);

/* icn_bb_bang — E_BANG: !list iterator */
typedef struct { DESCR_t *elems; int n; int pos; } icn_bang_state_t;
DESCR_t icn_bb_bang(void *zeta, int entry);

/* icn_bb_limit — E_LIMIT: gen \ n */
typedef struct { bb_node_t gen; long limit; long count; } icn_limit_state_t;
DESCR_t icn_bb_limit(void *zeta, int entry);
```

All go in `src/frontend/icon/icon_gen.c` + declared in `icon_gen.h`.
Register in `icn_eval_gen()` switch.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/icon/icon_parse.c` | Parser — builds IR directly (no AST) |
| `src/frontend/icon/icon_driver.c` | `icon_compile()` entry point |
| `src/frontend/icon/icon_gen.c` | Generator BB boxes |
| `src/frontend/icon/icon_gen.h` | Box declarations + state typedefs |
| `src/runtime/interp/icn_runtime.c` | Frame stack, proc table, icn_eval_gen |
| `src/runtime/interp/icn_runtime.h` | Public interface |
| `scripts/test_icon_ir_all_rungs.sh` | Full rung sweep |
| `scripts/test_icon_ir_rung_NN.sh` | Per-rung gates |
| `corpus/programs/icon/` | Icon corpus |

## JCON reference — goldmine for every BB box

**`corpus/programs/icon/jcon-ref/irgen.icn`** — 1,559-line Icon program from the
JCON compiler (Proebsting 1996) that generates Byrd Box four-port IR from AST nodes.
Every `ir_a_Foo` procedure is the **canonical four-port wiring** (α start / β resume /
ω fail / γ succeed) for one Icon construct. This is the ground truth for every
`icn_bb_*` box in `icon_gen.c`.

Key procedures and their construct:

| `irgen.icn` procedure | Icon construct | Our box |
|---|---|---|
| `ir_a_BinOp` | `+` `-` `*` `/` `%` relops `\|\|` | `icn_bb_binop_gen` |
| `ir_a_To` | `E1 to E2` | `icn_bb_to` |
| `ir_a_ToBy` | `E1 to E2 by E3` | `icn_bb_to_by` |
| `ir_a_Every` | `every E do body` | `icn_bb_every` |
| `ir_a_Alt` | `E1 \| E2` alternation | `icn_bb_alternate` |
| `ir_a_Limit` | `E \ N` limitation | `icn_bb_limit` |
| `ir_a_Suspend` | `suspend E do body` | `icn_bb_suspend` |
| `ir_a_While` / `ir_a_Until` / `ir_a_Repeat` | loop forms | interp.c loop handling |
| `ir_a_If` | `if E then T else F` | indirect-goto gate |
| `ir_a_Scan` | `E ? body` | shared SNOBOL4 scan (no box needed) |
| `ir_a_Not` | `not E` | oneshot fallback |
| `ir_a_Call` | procedure/function call | `icn_call_proc` |
| `ir_a_Augop` | augmented assignment `:=` `+:=` … | `icn_bb_binop_gen` augop path |

Full analysis with wiring diagrams: `.github/archive/MISC-ICON-JCON.md`.

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Never modify icn_proc_table layout — Raku shares it.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-14, one4all HEAD a22ffac2)

IC-1 done. IC-2 in progress: 54/59 rung01-11 PASS.
Relop fix done (NUMREL/STRREL return right operand — oracle confirmed).
Suspend skeleton in place (icn_drive_fnc, IcnFrame.suspending, E_WHILE breaks on suspend)
but every-body not yet receiving suspended value — rung03 still failing.
Root cause: debug icn_drive_node/val passthrough and every_body capture in icn_drive_fnc.
Next: IC-2 — fix suspend every-body passthrough, get rung03 PASS, then rung12 str relops.

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.


---

## Current state (2026-04-14 session 2, one4all HEAD 5438115c)

IC-2 in progress: PASS=44 FAIL=15 TOTAL=59.

Two root causes fixed this session:

1. icn_call_proc body loop (icn_runtime.c): was using for(i) + inner while(suspending)
   that called interp_eval(st) to re-enter loops — restarted loop from scratch and never
   ran the do-clause. Fixed: replaced with stmt-pinned while loop matching icn_drive_fnc,
   running do-clause on resume, pinning stmt index for E_WHILE/E_REPEAT/E_UNTIL.

2. E_WHILE/E_UNTIL/E_REPEAT in interp.c: neither Icon-context block checked
   ICN_CUR.suspending as an exit condition. E_WHILE kept looping internally when
   E_SUSPEND fired, never returning to icn_call_proc's suspend handler.
   Fixed: added !ICN_CUR.suspending to while conditions and post-body break in
   both copies (SNOBOL4-context and Icon-context) of all three loop kinds.

New passes: rung03_suspend_gen, rung03_suspend_gen_compose, rung03_suspend_gen_filter.
Broker PASS=31 FAIL=3 (FAIL=3 confirmed pre-existing baseline — no regressions).

Remaining 15 failures:
- rung01 x4: binop generator backtracking (3 < ((1 to 3) * (1 to 2)), nested-to, etc.)
- rung02 x5: user proc calls + nested arithmetic generators
- rung08 x1: find() generator (only first result, not all)
- rung10 x1: break in repeat with augop (gets 5, wants 15)
- rung11 x1: bang+augconcat ordering (gets y|, wants xy|)

Next IC-2 step: attack rung02_proc_* failures (fact, locals, add_proc) — user proc
call path. Then rung01 binop backtracking (icn_bb_binop_gen right-retry on relop fail).

## Current state (2026-04-15 session 8, one4all HEAD 09dbff9c)

IC-3 IN PROGRESS: table builtins written, DT_T frame slot coercion bug blocks gate.

What was done:
- interp.c: table()/insert()/delete()/member() builtins added in Icon E_FNC dispatch
- interp.c: E_SIZE handles DT_T via tbl->size; E_ITERATE oneshot handles DT_T first-value
- icon_gen.h: icn_tbl_iterate_state_t + icn_bb_tbl_iterate decl; snobol4.h included
- icon_gen.c: icn_bb_tbl_iterate box (B-5b) walks TABLE_BUCKETS, yields entry->val
- icn_runtime.c: icn_eval_gen E_ITERATE routes DT_T to icn_bb_tbl_iterate
- scripts/test_icon_ir_rung_13_tables.sh: gate script (5 tests)
- corpus: rung13_table_*.icn + .expected (5 tests, semicolons required by parser)

BLOCKER — DT_T frame slot coercion bug:
  table() returns TABLE_VAL(tbl) with .v=DT_T correctly.
  But t["x"] after t:=table() gives Error 3 (erroneous array/table reference).
  Root cause: ICN_CUR.env[slot] stores DESCR_t directly — DT_T should survive
  since it is just a struct. Suspect: E_VAR retrieval in Icon frame context, or
  subscript_get(base, idx) receiving base.v != DT_T due to silent coercion.

Debug plan for next session:
  1. In E_ASSIGN (Icon frame path, interp.c ~line 780): fprintf to /tmp/dbg.txt
     printing val.v after storing to env[slot].
  2. In E_IDX handler: fprintf base.v after interp_eval(e->children[0]).
  3. Confirm whether DT_T survives the env round-trip.
  4. If yes: problem is in subscript_get — check IS_TBL(base) branch.
  5. If no: find where coercion strips DT_T (possibly VARVAL_fn or NAME_DEREF).

Gate status: test_icon_ir_rung_13_tables.sh PASS=0 FAIL=5 (blocker above)
Smoke: test_smoke_icon.sh PASS=5 FAIL=0 (no regression)

Next: IC-3 — fix DT_T frame slot bug, get rung13 PASS=5.



IC-2b DONE. IC-2 (rung01-11) DONE: PASS=59 FAIL=0 TOTAL=59.
cross_lang broker fix DONE: PASS=37 FAIL=0 (was PASS=36 FAIL=1).

cross_lang root cause: E_CAT absent from icn_is_gen's recursive check.
every write("ICN: " || (1 to 3)) produced only ICN: 1 — oneshot fallback.
Fix: E_CAT added to icn_is_gen; icn_bb_cat_gen box pumps leaf gen,
injects via icn_drive_node, re-evaluates concat per tick.

Next: IC-2 — rung12 string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`), `*s`.


IC-2b DONE. IC-2 (rung01-11) DONE: PASS=59 FAIL=0 TOTAL=59.

Three final root causes fixed this session:

1. **rung01_paper_nested_to**: Added `icn_bb_to_nested` box (icon_gen.c/h).
   `icn_eval_gen(E_TO)` now detects generative lo/hi children via `icn_is_gen`
   and routes to cross-product box that pre-collects all lo/hi values.

2. **rung08_strbuiltins_find_gen**: Added explicit `find()` scalar-arg detector
   in `icn_eval_gen` before generic E_FNC block — builds `icn_bb_find` box directly.

3. **rung02_proc_locals**: Added `icn_find_leaf_gen()` in interp.c.
   `E_EVERY` with `E_ASSIGN(var, compound+gen)` now drives the leaf generator
   (e.g. `E_TO`) alone, injects each tick via `icn_drive_node/icn_drive_val`,
   and re-evaluates the full assignment so frame slot reads are fresh per tick.
   Universal `icn_drive_node` interception added at top of `interp_eval`.
   `E_AUGOP` excluded from E_EVERY special-case (has its own icn_is_gen path).

Gates: test_smoke_icon PASS=5, test_icon_ir_all_rungs PASS=59 FAIL=0,
test_smoke_unified_broker PASS=36 FAIL=1 (cross_lang pre-existing).

Next: IC-2 — rung12 string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`), `*s`.


IC-2 in progress: PASS=56 FAIL=3 TOTAL=59 (+4 this session, 2026-04-15 session 4).

Three root causes fixed:

1. **icn_is_gen exported** (icn_runtime.c/h): made non-static so interp.c can use it.

2. **E_AUGOP per-tick accumulation** (interp.c): was collecting last RHS generator value;
   now re-reads LHS and applies op for each RHS tick.
   Fixed: rung10_augop_break_repeat, rung11_bang_augconcat_bang_concat.

3. **icn_lazy_box for E_VAR/literals** (icn_runtime.c): icn_eval_gen(E_VAR) now returns a
   lazy box that re-evaluates interp_eval(e) on every alpha pump instead of capturing once.
   Fixed: rung02_arith_gen_relfilter, rung02_arith_gen_nested_filter.

Broker gate: PASS=36 FAIL=1 (cross_lang pre-existing — no regression).

Remaining 3 failures for next session:
- **rung01_paper_nested_to**: `(1 to 2) to (2 to 3)` — icn_eval_gen(E_TO) evals lo/hi
  eagerly via interp_eval; need to detect icn_is_gen(child[0])||icn_is_gen(child[1])
  and build a cross-product box (iterate lo_gen x hi_gen, inner lo..hi each pair).
- **rung02_proc_locals**: `every total := total + (1 to n)` inside a proc — E_ASSIGN
  wrapping E_ADD(E_VAR(total), E_TO(1,n)); lazy box may not propagate through E_ADD
  into binop_gen left child when called from within icn_call_proc frame.
  Debug: add fprintf to /tmp/dbg.txt to trace icn_lazy_box alpha calls and left_val.
- **rung08_strbuiltins_find_gen**: `every write(find("a","banana"))` — find() builtin
  with scalar args hits oneshot fallback; needs dedicated generator path in icn_eval_gen
  (mirror the icn_drive find-generator: strstr loop, successive 1-based positions).
  Add before generic E_FNC builtin path in icn_eval_gen.

IC-2b DONE. E_SCAN_AUGOP removed (dead IR node — never emitted, never handled).
Suspend coroutine fix PARTIAL:
- icn_active_ss global + trampoline sets it + icn_call_proc swapcontexts on suspending.
- FIXED: write(gen()) with bare suspends works (10/20/30 correct).
- BROKEN: every write(upto(4)) outputs only '4' instead of '1 2 3 4'.
  Root cause: after swapcontext resumes in icn_call_proc, re-calling interp_eval(st)
  on a while-stmt restarts the loop from the top instead of resuming mid-loop.
  Fix needed: pin i on while-stmt type, do NOT re-call interp_eval — let the
  while loop's own iteration handle re-entry. Just swapcontext and continue the
  outer for-loop; the while will re-check its condition naturally on the next
  interp_eval(st) call that the for-loop issues (i does not advance).

Next IC-2 step:
1. Fix i-pinning in icn_call_proc: when ICN_CUR.suspending fires inside a
   loop stmt (E_WHILE/E_REPEAT/E_UNTIL), decrement i before continuing so
   the outer for-loop re-enters the same stmt. Remove the inner
   result=interp_eval(st) re-call entirely.
2. Verify every write(upto(4)) → 1 2 3 4.
3. Run full rung01-11 suite, target PASS=59.
4. Then rung12 str relops (IC-2 proper).

Debug note: bash_tool swallows stderr — write debug to /tmp/dbg.txt.

IC-2b DONE. All GDE ops now have BB boxes wired into icn_eval_gen:
  E_LIMIT → icn_bb_limit, E_EVERY → icn_bb_every,
  E_BANG_BINARY → icn_bb_bang_binary, E_SEQ_EXPR → icn_bb_seq_expr.
  E_SCAN: intentionally no box — same IR node as SNOBOL4 matching, oneshot fallback correct.
Build clean. Icon smoke PASS=5. Unified broker PASS=31 FAIL=2 (pre-existing).
Raku ladder unblocked (shares icn_eval_gen).

Next: IC-2 (rung03 suspend/every-body passthrough debug, then rung12 str relops).
Debug note: bash_tool swallows stderr — write debug to /tmp/dbg.txt, not fprintf(stderr,...).

IC-2a wire-up DONE. PASS=41 FAIL=18 TOTAL=59 (wiring complete; remaining failures
are pre-wiring bugs — not regressions from this session).

Completed this session:
- icn_eval_gen (icn_runtime.c): E_ALTERNATE → icn_bb_alternate wired.
- icn_eval_gen (icn_runtime.c): E_ADD/SUB/MUL/DIV/MOD/LT/LE/GT/GE/EQ/NE →
  icn_bb_binop_gen wired (fires only when ≥1 child is generator kind).
- E_AUGOP (interp.c): RHS driven through icn_eval_gen α/β pump when RHS is
  generator (fixes rung10/rung11 augop patterns in principle; still blocked by
  underlying suspend issues for rung03 cases).
- Build clean. Smoke icon PASS=5. Unified broker PASS=31 FAIL=2 (pre-existing).
- JCON studied: vClosure/Resume pattern confirmed as direct analogue of icn_bb_* boxes.
- Prolog BB box history recovered (commit 7adca486): pl_box_true/fail/builtin/cat/
  choice/cut all documented; current pl_broker.c is live unified-ABI successor.

Remaining open bugs blocking PASS=59:
- rung03 x3: suspend every-body passthrough. CRITICAL DEBUG NOTE: bash_tool swallows
  stderr — write debug to /tmp/dbg.txt and cat it, NOT fprintf(stderr,...).
  Root: icn_drive must recurse into upto(4) arg; every_body must be non-NULL and
  passthrough must fire per tick.
- rung01 x1: nested-to (1 to 2) to (2 to 3) — needs icn_bb_to_nested or special
  handling in icn_eval_gen for E_TO where lo/hi are themselves E_TO.
- rung08 x1: match() at pos returning falsy 0 — guard: icn_scan_pos>0 → icn_scan_subj!=NULL.
- rung02 x?: user proc call path investigation.
- rung11 x1: bang_augconcat_bang_concat (want: xy| got: y|) — augop/bang ordering.

Next IC-2a step: write debug to /tmp/dbg.txt, confirm icn_drive is called and
recurses into upto(4) arg; verify every_body non-NULL and passthrough fires (rung03).
4. rung03_suspend_* — verify icn_bb_suspend coroutine passthrough.
5. rung02_proc_* — user proc call path investigation.
6. After 59/59: delete icn_drive/icn_drive_fnc (IC-2c), then IC-2d rung12.

## Current state (2026-04-15 session 9, one4all HEAD 4a5f382d)

IC-3 DONE: rung13 tables PASS=5/5. Three bugs fixed this session:
1. table() DESCR_t union clobber: d.s=NULL after d.tbl=tbl overwrote pointer (same union).
2. delete() wrong hash: was h*31+c, binary uses djb2 (init=0x1505, h*33^c, &0xFF).
3. Icon E_ASSIGN missing E_IDX branch: t["p"]:=7 had no handler; added subscript_set path.

IC-4 DONE: rung14 limit PASS=5/5. Already passing via icn_bb_limit (IC-2b).
New gate script: test_icon_ir_rung_14_limit.sh.

IC-5 IN PROGRESS: real output + pow + E_TO_BY real done; remaining rung15-29 work ahead.
- icn_real_str helper: write/writes format reals with decimal point (%.15g + .0 if needed).
- E_POW: always returns DT_R now (was delegating to SNOBOL4 POWER_fn → int for int^int).
- icn_bb_to_by_real: new box for E_TO_BY with real step/bounds; icn_eval_gen routes there when any arg is DT_R.

Rung baseline rung12-29: PASS=35 FAIL=62 before this session → after: rung17/19/26 pow/real fixed.
Next: IC-5 — swap() builtin, string subscript s[i] and section s[i:j], list builtins (push/pop/put/get), initial block fix, records.

## Current state (2026-04-15 session 10, one4all HEAD 9bcbe7a8)

IC-5 IN PROGRESS: rung15 PASS=5/5. Rung16-29: PASS=53 FAIL=24 (was 31/77, +22).
Broker: PASS=38 FAIL=0. Rung01-11: 59/59.

Implemented: E_SWAP, E_LCONCAT, E_MAKELIST, E_SECTION, E_INITIAL, E_RECORD;
subscript_get/get2 DT_S; E_SIZE/E_ITERATE DT_DATA icnlist; 20+ builtins.

Next: neg subscript fix, initial persistence, !list BB box, table default, records, read().

## Current state (2026-04-15 session 11, one4all HEAD da83ab23)

IC-5 IN PROGRESS: rung01-29 PASS=137 FAIL=19 TOTAL=156. Broker PASS=39 FAIL=0.

Fixes this session:
1. E_RECORD: sc_dat_register(spec) so type enters dispatch table; once-guard ival=1.
2. E_FIELD read (case E_FIELD in interp_eval) + write (interp_eval_ref case E_FIELD).
3. E_INITIAL persistence: file-scope icn_init_tab[64] keyed on e->id; snapshot updated
   by icn_init_update_snapshot() at call_user_function exit before NV restore.
4. E_ALTERNATE n-ary: left-recursive chain of binary boxes for 3+ children.
5. !list (E_ITERATE DT_DATA icnlist): icn_bb_list_iterate + icn_list_iterate_state_t.
6. table default: TBBLK_t.dflt field; table(dflt) wires it; subscript_get miss returns dflt.
7. neg subscript off-by-one: slen+1+i+1 → slen+i+1.
8. read()/reads(): fgets/fread from stdin, fail on EOF.

Remaining 19 failures — next session priority:
  1. rung24 records (5): E_FIELD/E_RECORD landed but point(3,4) still blank — debug
     whether Icon E_FNC call routes through icn_call_proc (bypasses sc_dat_find_type).
  2. rung21/25 initial (4): icn_frame_depth=0 in NV path — snapshot restores to NV
     but Icon frame env slot not updated; check icn_call_proc vs call_user_function routing.
  3. rung13 alt filter/nested (2): alternation with generator operands.
  4. rung22 put_bang (1), rung23 key (1), rung16 sub_every (1).
  5. rung18 relop_goal (1), rung19 pow_real (1), rung28 trim_map (1), rung29 image (1).

## Current state (2026-04-15 session 12, one4all HEAD 57d51c88)

IC-6 IN PROGRESS: rung01-29 PASS=154 FAIL=2 TOTAL=156. Broker PASS=42 FAIL=0. Smoke PASS=5.

Fixes this session (rung12-29: 79→154 PASS, +75):

1. icn_real_str: shortest round-trip precision (try %.15g..%.17g, stop when strtod round-trips).
   Fixes: rung15 real_literal, rung17 string_conv, rung29 image (3.14 not 3.1400000000000001).
2. E_POW: always returns DT_R (Icon semantics). Fixes: rung19 pow_int, rung26 ×4.
3. image(): string returns value without quotes. Fixes: rung29 type_image.
4. trim(): g_lang==1 → Icon trailing-only; else Raku both-sides. Fixes: rung28, rk_str22.
5. push()/put(): read n from icn_size (not ea.v==DT_I which was always 0). Fixes: rung22 put_bang.
6. icn_bb_list_iterate: store live list_obj DESCR_t, re-read each tick. Fixes: rung22 put_bang.
7. icn_bb_tbl_key_iterate: new box; key(T) wired in icn_eval_gen. Fixes: rung23 table_key.
8. icn_is_gen: added E_IDX (gen if index child gen), E_ASSIGN (gen if RHS gen).
9. icn_eval_gen: E_IDX routes to icn_bb_cat_gen (drive leaf, re-eval subscript). Fixes: rung16 sub_every.
10. icn_eval_gen: E_LCONCAT added to binop_map for cross-product concat.
11. icn_oneshot_box: reset fired=0 on alpha so cross-product can replay scalar arms.
12. icn_binop_apply: relops return actual rv DESCR_t (not INTVAL cast). Fixes: rung18 real_relop_goal.
13. icn_binop_apply: real-aware arithmetic. Fixes: rung17 real_arith.
14. E_EVERY: E_SEQ conjunction special case added. Partial fix for rung13 filter.
15. test_icon_ir_all_rungs.sh: extended to rung01-29; added .stdin support. Fixes: rung27 ×4.

OPEN (2 failures, next session IC-6 priority):

- rung13_alt_alt_filter: every (x:=alt)>2 & write(x).
  E_SEQ special case fires icn_eval_gen(E_GT(E_ASSIGN(x,alt),2)).
  icn_bb_binop_gen pumps E_ASSIGN as left box — but E_ASSIGN side-effect
  (writing x into frame slot) is not replayed per tick; needs icn_drive_node
  injection the same way the E_ASSIGN special case in E_EVERY does it.
  Fix: in E_EVERY E_SEQ path, detect E_GT/relop with E_ASSIGN left child;
  drive the alt leaf directly via icn_drive_node, re-eval the full filter each tick.

- rung13_alt_alt_nested: every write(("a"|"b") || ("x"|"y")).
  E_LCONCAT with two E_ALTERNATE children should route to icn_bb_binop_gen
  cross-product. icn_oneshot reset fixed. Root cause: E_CAT handler in
  icn_eval_gen fires before the binop_map loop and intercepts E_LCONCAT
  (E_CAT and E_LCONCAT share the icn_is_gen case but E_CAT block only
  checks e->kind == E_CAT). Verify: add E_LCONCAT check to E_CAT block guard.
## Current state (2026-04-16 session 13, one4all HEAD 37d45f96)

IC-6 rung13 alt-gen DONE: rung01-29 PASS=156/156 FAIL=0. Broker PASS=43 FAIL=0. Smoke PASS=5.

Two root causes fixed this session:

1. **icn_bb_assign_gen** (icn_runtime.c): New box for E_ASSIGN with generative RHS.
   Pumps RHS generator on each α/β tick, writes result to target var slot (or NV),
   returns value so enclosing binop_gen can test it per tick.
   Added: icn_assign_gen_state_t typedef, icn_bb_assign_gen() static function,
   E_ASSIGN case in icn_eval_gen() before E_VAR lazy box.
   Fixes: rung13_alt_filter — every (x:=(1|2|3|4))>2 & write(x) → 3\n4.

2. **E_CAT cross-product** (icn_runtime.c): E_CAT block in icn_eval_gen now detects
   when BOTH children are generative and routes to icn_bb_binop_gen (ICN_BINOP_CONCAT)
   for full cross-product instead of one-side icn_bb_cat_gen pump.
   Fixes: rung13_alt_nested — every write(("a"|"b")||("x"|"y")) → ax\nay\nbx\nby.
   Note: "||" is E_CAT (string concat), not E_LCONCAT ("|||" list concat) — the prior
   diagnosis in session 12 had the kind name wrong but the fix is correct.

New script: scripts/test_icon_ir_rung_13_alt.sh PASS=2/2 (inline, no corpus).

Next IC-6: run corpus rung16–29 with corpus cloned to recount remaining open failures.
Without corpus the rung all-rungs script SKIPs. Remaining known open (from session 12):
rung22 put_bang(1), rung23 key(1), rung16 sub_every(1), rung18 relop(1),
rung19 pow(1), rung28 trim_map(1), rung29 image(1).

## Current state (2026-04-16 session 14, one4all HEAD 37d45f96)

IC-6 DONE: rung01-29 PASS=156/156 confirmed with corpus. Broker PASS=45 FAIL=0. Smoke PASS=5.
Crosscheck PASS=4. All suspected IC-6 failures were already fixed from session 13.

Scripts rewritten/extended this session (all in one4all/scripts/, self-contained, --ir-run):
  test_icon_ir_rung_30.sh  — abs/max/min/sqrt/seq   (was JVM/jasmin stub)
  test_icon_ir_rung_31.sh  — sort/sortf              (was JVM/jasmin stub)
  test_icon_ir_rung_32.sh  — string retval every     (was JVM/jasmin stub)
  test_icon_ir_rung_33.sh  — case expressions        (was JVM/jasmin stub)
  test_icon_ir_rung_34.sh  — null/nonnull test       (was JVM/jasmin stub)
  test_icon_ir_rung_35.sh  — block bodies + str/str  (was JVM/jasmin stub)
  test_icon_ir_rung_36.sh  — JCON suite 75 tests     (was JVM/jasmin stub)
  test_icon_ir_all_rungs.sh — extended rung01-36, xfail-aware, --rung/--scrip/--corpus switches

IC-7 baseline (rung30-35):
  rung30 0/5 — abs/max/min/sqrt/seq missing from E_FNC dispatch
  rung31 0/5 — sort()/sortf() missing
  rung32 4/5 — strret_every: every over proc yielding string returns only first value
  rung33 1/5 — E_CASE dispatch not implemented (parse ok, eval missing)
  rung34 1/5 — \x null-test and \=x nonnull-test unimplemented
  rung35 7/7 — ALREADY PASSING (no work needed)

IC-8 baseline (rung36 JCON): PASS=2 FAIL=50 XFAIL=23 TOTAL=75

Next IC-7: fix rung30 builtins first (abs/max/min/sqrt/seq in icn_runtime.c E_FNC dispatch),
then rung31 sort/sortf, then rung33 case, then rung34 null-test, then rung32 strret_every.

## Current state (2026-04-16 session 15, one4all HEAD 9eb8c669)

IC-7 IN PROGRESS. Broker PASS=49 FAIL=0. Smoke PASS=5. Rung01-29 PASS=156/156.

Fixes this session (interp.c + icn_runtime.c):
1. abs/max/min/sqrt added to Icon E_FNC dispatch.
2. seq() added as E_FNC builtin (returns first value) AND as icn_bb_to_by infinite
   generator in icn_eval_gen (every write(seq(1) \\ 3) → 1 2 3).
3. sort(L)/sortf(L,n) — insertion sort over icnlist; sortf uses DATINST_t->fields[n-1].
4. E_CASE rewritten: Icon pairs layout [val,body]...[default_body].
   Raku triples detected by (nchildren-1)%3==0 AND child[1] is E_ILIT/E_NUL.
5. E_NULL (/E) and E_NONNULL (\E) added to interp_eval.
   E_NONNULL added to icn_is_gen + icn_eval_gen pass-through via icn_bb_limit
   so every write(\(1 to 3)) → 1 2 3.
6. User-proc-with-gen-arg box wired in icn_eval_gen (before oneshot fallback):
   detects first generative arg of a user proc, builds icn_fnc_gen_state_t.

IC-7 rung30-35 results:
  rung30 5/5 DONE — abs/max/min/sqrt/seq
  rung31 5/5 DONE — sort/sortf
  rung32 4/5 OPEN — strret_every: every write(tag("a"|"b"|"c")) yields only first value
  rung33 5/5 DONE — case expressions
  rung34 5/5 DONE — null/nonnull tests
  rung35 7/7 DONE — already passing (no new work)

rung32 open root cause: icn_bb_fnc_gen calls icn_call_builtin → icn_call_proc
for user procs. icn_call_proc returns after first `return` statement — not a
coroutine. Fix: in icn_bb_fnc_gen, when call targets a user proc, build a fresh
icn_bb_suspend coroutine each tick with the substituted arg, instead of calling
icn_call_builtin.

Next IC-7: fix rung32 strret_every (1 test), then IC-8 rung36 JCON suite.
