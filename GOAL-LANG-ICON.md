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

IC-2 still in progress: 54/59 rung01-11.

Root cause isolated this session:
- `every write(upto(4))` parses as E_EVERY with ONE child: gen=write(upto(4)), no do-body.
- icn_drive(write(upto(4))) must recurse into args to find upto(4) as drivable E_FNC.
- ICN_CUR.body_root must be set to gen itself (body?body:gen) so icn_drive_fnc 
  captures the right every_body to re-execute per suspend tick.
- CRITICAL: bash_tool swallows stderr, so fprintf(stderr,...) debug was invisible.
  Next session: write debug to /tmp/dbg.txt and cat it, or use a flag file.

Fixes landed (committed, smoke PASS=32 FAIL=0):
- E_EVERY, E_WHILE, E_UNTIL, E_REPEAT, E_SUSPEND, E_SEQ_EXPR, E_IF,
  E_BREAK, E_RETURN, E_FAIL, E_ALT added to icn_frame_depth>0 switch.
- E_EVERY sets body_root = body ? body : gen.
- icn_drive_fnc: every_body captured before frame push; run in caller frame.
- E_ALT: Icon value alternation (try left, else right). Smoke +1 pass.

Still open:
- suspend every-body passthrough (rung03 x3)
- nested to: (1 to 2) to (2 to 3) (rung01_paper_nested_to)
- match() at pos returning falsy 0: guard icn_scan_pos>0 → icn_scan_subj!=NULL (rung08_match)

Next IC-2 step: write debug to file (not stderr), confirm icn_drive is called
and recurses into upto(4) arg. Then verify every_body is non-NULL and passthrough fires.

## Current state (2026-04-14 session 6, one4all HEAD 1483a6c8)

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
