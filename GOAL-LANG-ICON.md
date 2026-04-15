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
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_icon.sh       # 3-mode divergence check
bash /home/claude/one4all/scripts/test_icon_ir_all_rungs.sh      # check baseline
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

- [ ] **IC-2b** — Complete ALL goal-directed-evaluation ops as BB boxes in `icon_gen.c`
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

- [ ] **IC-2** — rung12: string relational ops (`<<`, `>>`, `<=`, `>=`, `==`, `~=`),
  `*s` (string size).
  Gate: test_icon_ir_rung_12_strrelop_size.sh PASS.

- [ ] **IC-3** — rung13: tables (`table()`, key lookup, `!T` iteration).
  Gate: test_icon_ir_rung_13.sh PASS.

- [ ] **IC-4** — rung14: lists (`list(n,v)`, subscript, `push/pop/put/get`).
  Gate: test_icon_ir_rung_14.sh PASS.

- [ ] **IC-5** — rung15: sets (`set()`, `member`, `insert`, `delete`).
  Gate: test_icon_ir_rung_15.sh PASS.

- [ ] **IC-6** — rung16: `for @arr -> $x` real array iteration (E_BANG on list).
  Gate: test_icon_ir_rung_16.sh PASS.

- [ ] **IC-7** — rung17–20: real arithmetic, section `s[i:j]`, seq expressions.
  Gate: rung17–20 all PASS.

- [ ] **IC-8** — rung21: `global` declarations and `initial` blocks.
  Gate: test_icon_ir_rung_21_global_initial.sh PASS.

- [ ] **IC-9** — rung22–25: `type()`, `image()`, `copy()`, `ord()`/`char()`.
  Gate: rung22–25 all PASS.

- [ ] **IC-10** — rung26–30: `reads()`, `read()`, file I/O, `open()`/`close()`.
  Gate: rung26–30 all PASS.

- [ ] **IC-11** — rung31–36: co-expressions, `@c`, `create`, `activate`.
  Gate: rung31–36 all PASS (or SKIP with note if co-expressions are post-scope).

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

## Current state (2026-04-15 session 4, one4all HEAD 461e3935)

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
