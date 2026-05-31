# HANDOFF — ICON-BB IBB-9-UNOP — value-producing unary ops + `--dump-bb` fix

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-9-UNOP (landed)
**SCRIP:** `cc7995c4` (on origin/main)
**Repos touched:** SCRIP (7 files: 1 new template + Makefile + emit_core + emit_bb + bb_call + rt.c + scrip.c), .github (GOAL watermark, PLAN row, this doc)

---

## What landed

Five Icon value-producing unary operators now run in mode-3 byte-identical to mode-2, zero SM:

- `-E`  BB_NEG
- `+E`  BB_POS
- `\E`  BB_NONNULL  (succeeds with E iff E is non-null/non-fail)
- `/E`  BB_NULL_TEST (succeeds with &null iff E is &null)
- `not E` BB_NOT     (succeeds with &null iff E fails)

### Root cause

All five routed in `emit_core.c` to the `bb_cset`/`bb_stub` no-op stubs, whose
MEDIUM_BINARY arms emit ZERO bytes. In mode-3 the operator produced no code at all,
so `write(-x)` printed nothing (and worse, `bb_call` ABORTed on the unrecognised
arg0 kind) and `if \(...)`/`if /(...)`/`if not(...)` produced empty output. Mode-2
worked because `bb_exec.c` has correct executor arms for each.

### Fix — four code pieces + one driver fix

1. **`src/emitter/BB_templates/bb_unop.cpp` (NEW grouped template).** One template
   for all five kinds, discriminating on `pBB->t` to pick the runtime helper. Control
   shape is a **direct copy of the `bb_binop.cpp` relop arm**: call the `rt_unop_*`
   helper (which pops the operand, applies, sets `LAST_OK`, and pushes the result or a
   balanced FAILDESCR), then `jmp γ` **UNCONDITIONALLY**.
   - In **condition context** (cond of if/while) `lower_icn_new_If_ag` wires the cond's
     γ==ω==BB_IF, so the single `jmp γ` always lands at the BB_IF router, which reads
     `LAST_OK` to choose then/else. This is exactly how the AG-pure relop already works.
   - In **value context** (`write(\E)`, `x := \E`) the consumer takes the pushed value;
     a failed unop leaves FAILDESCR which the write/assign trailer handles like any
     failed expr. The helper's `int` return is ignored — `LAST_OK` is the channel.
   - 17 bytes BINARY: `movabs rax,&rt_unop_<op>; call rax; jmp γ; β: jmp ω`. Patch
     sites {13,21→γ}, β-def {17}, ω {18}. FACT-clean (all bytes in the template).

2. **`src/emitter/emit_bb.c` `flat_drive_unop` (NEW driver).** Mirror of
   `flat_drive_binop_tree`/`flat_drive_call_intexpr`: the operand is `pBB->α` (icn_leaf
   keeps it on the node, NOT threaded into the outer chain). Walk α first
   (success → unop apply, failure → outer ω), then `EMIT_PAIR_FILL` the unop template.
   Routed from `walk_bb_flat`'s switch (the five kinds → `flat_drive_unop`); removed them
   from the `default:` degenerate path.

3. **`src/runtime/rt/rt.c` — five `rt_unop_*` helpers.** Each is a byte-for-byte
   transcription of the matching `bb_exec.c` arm:
   - `rt_unop_neg`/`rt_unop_pos`: coerce + sign (DT_I stays int, else REALVAL via to_real);
     fail propagates fail.
   - `rt_unop_nonnull`: fail on FAIL or DT_SNUL, else push the value.
   - `rt_unop_null_test`: push &null + LAST_OK=1 iff DT_SNUL, else FAILDESCR + LAST_OK=0.
   - `rt_unop_not`: push &null + LAST_OK=1 iff the inner value is FAIL, else FAILDESCR.

4. **`src/emitter/BB_templates/bb_call.cpp`** — extended `is_write_intexpr` and
   `arg_is_any` to include the five unop kinds, and the `BB_CALL` arg dispatch in
   `walk_bb_flat` to route an unop arg0 through `flat_drive_call_intexpr`. So
   `write(-x)` etc. work (the unop pushes its value; the any-write trailer prints it by
   runtime DESCR kind).

5. **`src/emitter/emit_core.c`** — moved BB_NEG/POS/NONNULL/NULL_TEST/NOT off the
   `bb_cset`/`bb_stub` arms onto `bb_unop`.

### Bonus — `--dump-bb` no longer aborts

`--dump-bb` set `g_opt_dump_bb` but **nothing consumed it**, so the driver fell through
to the default `--run` path and the program executed (ABORTing on any not-yet-wired
shape — which is how I first hit it while dumping a `write(-x)` graph). Added a
`dump_bb` early-return in `scrip.c` mirroring `--dump-sm`: build the BB graphs via
`sm_preamble`, walk every proc's `bb_table` entry, `bb_print`, return 0 — no native
emission. `./scrip --dump-bb prog.icn` now prints the graph and exits clean.

NOTE for a future cleanup (NOT done here): `bb_op_name`'s `kind_names[]` table in
`scrip_ir.c` is stale/misaligned vs the live `BB_op_t` enum in `BB.h` (it predates
BB_REPEAT/BB_ALT/BB_SIZE/BB_CASE/… insertions), so `--dump-bb` prints WRONG op names
for high-numbered kinds (e.g. a BB_NONNULL shows as "BB_PAT_SPAN"). The node `->t` is
correct; only the printed label is wrong. Cosmetic, but worth fixing the table.

---

## Gates (verified at handoff)

- smoke_icon 5/5, smoke_prolog 5/5, smoke_unified_broker 49/11
- FACT gate 0 (`seg_byte/SL_B/sl_emit_one/emit_standard_blob/bake_blob_call` outside
  templates+emit_core == 0; `bytes/u32le/u64le` outside templates only in the helper
  defs and `bomb_bytes`).
- zero-SM holds for every migrated program (`--dump-sm | grep -c '^   [0-9]'` == 0).
- Corpus same-sweep (`/home/claude/corpus/programs/icon/*.icn`, m2-OK filter, PASS iff
  `m3 rc==0 && m2==m3`): **62 → 69 PASS (+7)**, SEGV 0.
- **Regressions == 0, verified rigorously**: built a pristine HEAD binary in a
  `git worktree`, ran the same sweep, diffed sorted pass-lists. `comm -23 base after`
  empty; `comm -13 base after` = exactly the 7 new programs:
  rung07_control_{neg,not,repeat_break}, rung34_null_test_{nonnull_fails,
  nonnull_succeeds,null_fails,null_succeeds}.

---

## NEXT

1. **Finish the unop family**: `*E` (BB_SIZE) and `?E` (BB_RANDOM) use the SAME
   `bb_unop` template slot — just add `rt_unop_size`/`rt_unop_random` helpers (SIZE
   needs the DT_DATA-list/DT_T-table/cset length handling from `bb_exec.c` BB_SIZE).
   Add the kinds to `emit_core.c`/`walk_bb_flat`/`bb_call.cpp` exactly as this rung did.
   `rung12_strrelop_size_size` and several `rung36_jcon_*` use `*s`.
2. **`nonnull_in_every`** (`every \(1|2|3)`-style): unop over a generator-bearing chain;
   belongs with IBB-9-4 (gen-bearing every body), not here.
3. **Biggest lever remains user-proc dispatch (IBB-9-6)** — ~158 of the 167 aborts are
   `bb_call: unsupported call shape`. JCON `ir_a_Call` (irgen.icn:360): arg chain
   `L=[fn]|||args`, `ir_Call(closure,fn,args,resume)`; needs `rt_call_proc` + BB_RETURN
   flat-wire (`ir_a_Return:867`). Start with a 0-arg / 1-arg user proc returning a value.
4. Smaller mode-3 gaps still open: `||` lconcat (rung13 nested), `case` (BB_CASE flat
   driver; rung33), BB_AUGOP-in-every (rung10 `sum +:= 1 to 5` → m3 prints `1`, m2 `15`),
   loop `break`/`next` mode-3.

---

## Per-rung gate used this session

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh
./scrip --interp PROG.icn > m2.txt
./scrip --run    PROG.icn > m3.txt
diff m2.txt m3.txt                                       # empty
./scrip --dump-sm PROG.icn | grep -c '^   [0-9]'         # 0
./scrip --dump-bb PROG.icn                               # prints graph, rc 0 (no abort)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l       # 0
bash scripts/test_smoke_icon.sh                           # 5/5
bash scripts/test_smoke_prolog.sh                         # 5/5
bash scripts/test_smoke_unified_broker.sh                 # 49/11
```

Regression-proof methodology (do this every session): build HEAD in a worktree,
sweep both binaries, `comm` the sorted pass-lists.
