# GOAL-ICON-BB-NATIVE.md — Icon via native Byrd Boxes (not SM coroutines)

**Repo:** one4all + .github
**Sister docs:** `GOAL-ICON-BB-COMPLETE.md` (superseded), `GOAL-LANG-ICON.md`, `GOAL-CHUNKS.md`
**Carved:** 2026-05-12

---

## The insight

JCON's IR is `ir_info(start, resume, failure, success)` — **four ports on every node, always.**
Icon is one big Byrd box graph. Every construct is a box. The broker pumps it.

The previous GOAL-ICON-BB-COMPLETE approach was wrong: it tried to hand-encode the
four-port protocol as SM coroutines (SM_JUMP / SM_RESUME / SM_STORE_GLOCAL / SM_SUSPEND /
SM_RETURN). That is reinventing BB mechanics in SM bytecode, construct by construct.
It is hard to write, hard to debug, and does not compose.

The correct approach: each Icon construct is **one C function** with signature:

```c
DESCR_t icn_bb_Foo(void *zeta, int entry);   /* entry: α=0 fresh, β=1 resume */
```

- **α** (entry=0): allocate/initialize state ζ; compute first value; return it (γ) or FAILDESCR (ω).
- **β** (entry=1): advance state ζ; compute next value; return it (γ) or FAILDESCR (ω).

The broker (`bb_broker` with `BB_PUMP`) already handles the pump loop.
The compiler emits one opcode — `SM_BB_EXEC` — which pops a `bb_node_t` and calls the broker.
That is the **only** new SM opcode needed.

JCON reference: `jcon-master/tran/irgen.icn` — 43 `ir_a_*` procedures, each mapping one
AST construct to its four-port IR. Every one that uses `ir_ResumeValue` or `closure` is
a generator; every other is a succeed-or-fail box. Both are just boxes.

---

## Done when

1. Every Icon AST kind reachable from a `--ir-run` PASS program is lowered to a
   native `icn_bb_*` C box function — no `SM_BB_PUMP_AST`, no `SM_BB_PUMP_SM`,
   no SM coroutine GLOCALs for Icon constructs.
2. `SCRIP_NO_AST_WALK=1 ./scrip --sm-run` == `./scrip --ir-run` for every program
   in the `--ir-run` PASS set (the honest gate).
3. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
4. Every `icn_bb_*` box function has a `sm_codegen_x64` template (Mode 4 path).
5. `is_suspendable` / `coro_eval` not reachable from SM dispatch under
   `SCRIP_NO_AST_WALK=1`.

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --ir-emit  → ir_print_program()                              Mode 1
  --ir-run   → execute_program() → interp_eval()              Mode 2  (AST walker, oracle)
  --sm-run   → lower() → SM_Program → sm_interp_run()        Mode 3
  --jit-run  → lower() → sm_codegen_x64() → run              Mode 3.5
```

**Mode 3 Icon execution after this goal:**

```
lower_expr(TT_FOO)
  → icn_bb_foo_make(args...)   /* allocates + initializes bb_node_t */
  → sm_emit SM_PUSH_LIT_PTR <bb_node_t*>
  → sm_emit SM_BB_EXEC         /* pops bb_node_t; calls bb_broker(BB_PUMP/BB_ONCE) */
```

Box taxonomy (from JCON `ir_a_*`):

| Kind | Box | Broker mode | Notes |
|------|-----|-------------|-------|
| Scalar (literals, var load, field get) | trivial box — α returns value, β returns ω | BB_ONCE | Already works via interp_eval; just needs wrapping |
| Succeed/fail (relops, type tests) | α evaluates, returns value or FAILDESCR | BB_ONCE | |
| Generator (to/by, !, alternate, scan) | α = first tick, β = next tick | BB_PUMP | State in ζ |
| Control (every, while, until, repeat) | composes child boxes | BB_PUMP / BB_ONCE | |
| Procedure call | existing SM_BB_PUMP_PROC / SM_BB_ONCE_PROC | — | Unchanged |

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (run before every rung, all must be green):
```bash
bash scripts/test_smoke_icon.sh                 # PASS=5  (never regress)
bash scripts/test_smoke_unified_broker.sh       # PASS=49 (never regress)
bash scripts/test_icon_ir_all_rungs.sh          # 185/48/30 byte-identical (Mode 2 oracle)
```

Honest gate (target, increases each rung):
```bash
bash scripts/test_icon_sm_no_ast_walk.sh        # PASS count rises each rung
```

---

## Box implementation home

All `icn_bb_*` box functions live in:

```
src/runtime/interp/icn_boxes.c    (new file — created at IB-1)
src/runtime/interp/icn_boxes.h    (new file — created at IB-1)
```

Existing `coro_runtime.c` contains prototype `icn_bb_assign_gen`,
`icn_bb_identical_gen` etc. — these are the right shape but wrong home.
They will be moved/superseded rung by rung. Do not touch `coro_runtime.c`
until a rung explicitly migrates a function from it.

---

## SM_BB_EXEC opcode

One new opcode added at IB-1:

```c
SM_BB_EXEC   /* pop bb_node_t* from value stack; call bb_broker(BB_PUMP, ...); push result */
SM_BB_EXEC1  /* same but BB_ONCE (scalar/relop context) */
```

`lower.c` emits these. `sm_interp.c` and `sm_codegen_x64.c` handle them.
No other new SM opcodes needed for this goal.

---

## Rungs

### IB-0 — baseline + scaffolding
- [ ] Run session setup. Confirm smoke 5/5, broker 49/49, ir-all 185/48/30.
- [ ] Record honest baseline: `SCRIP_NO_AST_WALK=1` pass count (call it N₀).
- [ ] Create `src/runtime/interp/icn_boxes.h` — empty, with include guards and `DESCR_t icn_bb_make_node(bb_box_fn fn, void *zeta)` helper.
- [ ] Create `src/runtime/interp/icn_boxes.c` — empty stub, includes icn_boxes.h.
- [ ] Wire into Makefile (add to compilation units).
- [ ] Build clean. Smokes unchanged. Commit.

### IB-1 — SM_BB_EXEC opcode
- [ ] Add `SM_BB_EXEC` and `SM_BB_EXEC1` to `sm_prog.h` enum and `sm_prog_print`.
- [ ] Handle in `sm_interp.c`: pop `bb_node_t*`, call `bb_broker(node, BB_PUMP, collect_fn, &result)`, push first result or FAILDESCR.
- [ ] Add no-op template stub in `sm_codegen_x64.c` (abort with message — filled in later).
- [ ] Build clean. Smokes unchanged. No Icon programs use SM_BB_EXEC yet. Commit.

### IB-2 — first box: integer literal (scalar, trivial)
- [ ] Implement `icn_bb_intlit` in `icn_boxes.c`: α returns DESCR_t int, β returns FAILDESCR.
- [ ] In `lower.c`: `lower_ilit` emits `SM_PUSH_LIT_PTR <icn_bb_intlit_make(v)>` + `SM_BB_EXEC1`.
- [ ] Anchor program: `rung01_intlit.icn` — `write(42)`. Gate: honest PASS, smoke unchanged.
- [ ] Confirm `--dump-sm` shows SM_BB_EXEC1, no SM_BB_PUMP_AST. Commit.

### IB-3 — string literal + var load
- [ ] `icn_bb_strlit`: α returns string DESCR_t, β → FAILDESCR.
- [ ] `icn_bb_varload`: α reads named variable from frame/NV, β → FAILDESCR.
- [ ] Wire into `lower_strlit` and `lower_var`.
- [ ] Anchor: `rung01` string write. Gate: honest PASS. Commit.

### IB-4 — relops (succeed/fail, BB_ONCE)
- [ ] `icn_bb_relop`: α evaluates both operands, applies op, returns LHS or FAILDESCR, β → FAILDESCR.
- [ ] Wire into `lower_acomp` and `lower_lcomp`.
- [ ] Anchor: `rung02` integer comparison. Gate: honest PASS. Commit.

### IB-5 — arithmetic (succeed/fail)
- [ ] `icn_bb_arith`: α computes binary arith, returns result, β → FAILDESCR.
- [ ] Wire into `lower_add/sub/mul/div/mod/pow`.
- [ ] Anchor: `rung03` arithmetic program. Gate: honest PASS. Commit.

### IB-6 — assignment (TT_ASSIGN scalar)
- [ ] `icn_bb_assign`: α evaluates RHS, assigns to LHS, returns value, β → FAILDESCR.
- [ ] Wire into `lower_assign` scalar path.
- [ ] Anchor: `rung01` assignment. Gate: honest PASS. Commit.

### IB-7 — integer range generator (TT_TO / TT_TO_BY)
- [ ] `icn_bb_range`: state ζ = {cur, hi, step}. α = init+first tick, β = next tick.
- [ ] Wire into `lower_to` and `lower_to_by`.
- [ ] Anchor: `write(1 to 3)`. Gate: honest PASS + N↑. Commit.

### IB-8 — alternate / alt (TT_ALTERNATE)
- [ ] `icn_bb_alternate`: state ζ = {left_node, right_node, phase}. α tries left, β exhausts left then right.
- [ ] Wire into `lower_alternate` (replacing current `lower_bb_pump_ast` fallthrough).
- [ ] Anchor: `rung_alt` program. Gate: honest PASS + N↑. Commit.

### IB-9 — iterate / bang (TT_ITERATE, `!E`)
- [ ] `icn_bb_iterate`: state ζ = {subject DESCR_t, index int}. α = init+first, β = next element.
- [ ] Wire into `lower_iterate` (replacing current ICN_BANG_NEXT SM coroutine).
- [ ] Anchor: `rung15_iterate_string.icn`. Gate: honest PASS + N↑. Commit.

### IB-10 — every (TT_EVERY)
- [ ] `icn_bb_every`: state ζ = {generator node, body node}. α/β pump generator, run body each tick.
- [ ] Wire into `lower_every` (replacing SM_BB_PUMP_EVERY).
- [ ] Anchor: `every write(1 to 3)`. Gate: honest PASS + N↑. Commit.

### IB-11 — limitation (TT_LIMIT, `E \ N`)
- [ ] `icn_bb_limit`: state ζ = {inner node, count, remaining}. Caps generator at N values.
- [ ] Wire into `lower_limit`.
- [ ] Anchor: `rung14` limit program. Gate: honest PASS + N↑. Commit.

### IB-12 — not (TT_NOT)
- [ ] `icn_bb_not`: α runs child once; if child γ → ω; if child ω → γ (null). β → ω.
- [ ] Wire into `lower_not`.
- [ ] Anchor: `rung_not` program. Gate: honest PASS. Commit.

### IB-13 — if/then/else (TT_IF)
- [ ] `icn_bb_if`: α evaluates condition; on γ → then branch; on ω → else branch. β resumes live branch.
- [ ] Wire into `lower_if`.
- [ ] Anchor: `rung_if` program. Gate: honest PASS. Commit.

### IB-14 — scan (TT_SCAN, `subject ? body`)
- [ ] `icn_bb_scan`: α/β per existing `lower_scan` logic but as a box. State = subject save/restore.
- [ ] Wire into `lower_scan`.
- [ ] Anchor: `rung_scan` program. Gate: honest PASS + N↑. Commit.

### IB-15 — while / until / repeat (TT_WHILE, TT_UNTIL, TT_REPEAT)
- [ ] `icn_bb_while`, `icn_bb_until`, `icn_bb_repeat`: loop control boxes.
- [ ] Wire into `lower_while`, `lower_until`, `lower_repeat`.
- [ ] Anchor: loop programs. Gate: honest PASS + N↑. Commit.

### IB-16 — conjunction / seq_expr (TT_SEQ_EXPR, generative `;`)
- [ ] `icn_bb_seq`: evaluates children left-to-right; if any child ω the whole thing ω.
- [ ] Wire into `lower_seq_expr`.
- [ ] Anchor: `rung_seq` program. Gate: honest PASS. Commit.

### IB-17 — section ops (TT_SECTION*)
- [ ] `icn_bb_section`: α calls ICN_SECTION_RANGE/PLUS/MINUS; β → FAILDESCR.
- [ ] Wire into `lower_section_3`.
- [ ] Anchor: `rung_section` program. Gate: honest PASS. Commit.

### IB-18 — bang binary (TT_BANG_BINARY)
- [ ] `icn_bb_bang_binary`: state ζ = {left, right, left_val, right_state}. Nested generator.
- [ ] Wire into `lower_bang_binary`.
- [ ] Anchor: `rung_bang_binary` program. Gate: honest PASS + N↑. Commit.

### IB-19 — list concat (TT_LCONCAT, generative `|||`)
- [ ] `icn_bb_lconcat`: generator over list concatenation result.
- [ ] Wire into `lower_lconcat`.
- [ ] Anchor: lconcat program. Gate: honest PASS + N↑. Commit.

### IB-20 — augmented ops (TT_AUGOP)
- [ ] `icn_bb_augop`: read-compute-writeback as a box.
- [ ] Wire into `lower_augop`.
- [ ] Gate: honest PASS. Commit.

### IB-21 — case (TT_CASE)
- [ ] `icn_bb_case`: α evaluates selector, dispatches to matching arm, β resumes live arm.
- [ ] Wire into `lower_case`.
- [ ] Gate: honest PASS. Commit.

### IB-22 — delete SM_BB_PUMP_AST from Icon path
- [ ] After IB-2 through IB-21: grep for `SM_BB_PUMP_AST` in Icon lowering paths.
- [ ] Every remaining call must be replaced or justified.
- [ ] Replace `lower_bb_pump_ast` call sites in Icon with `abort("BUG: Icon fell to AST pump")`.
- [ ] Gate: honest corpus sweep shows zero AST-pump fires. Commit.

### IB-23 — Mode 4 templates for all icn_bb_* boxes
- [ ] For each `icn_bb_*` function, add `sm_codegen_x64` template.
- [ ] Gate: `--jit-run` == `--sm-run` for honest-passing programs. Commit.

### IB-24 — final sweep + coro_runtime.c cleanup
- [ ] Remove Icon-specific code from `coro_runtime.c` that is now dead (old `icn_bb_assign_gen` etc.).
- [ ] `is_suspendable` returns false for all migrated kinds.
- [ ] `coro_eval` not reachable under `SCRIP_NO_AST_WALK=1` for any Icon program.
- [ ] Full corpus: honest PASS count == `--ir-run` PASS count. Commit.

---

## Invariants (never break)

1. `test_smoke_icon.sh` PASS=5 at every rung.
2. `test_smoke_unified_broker.sh` PASS=49 at every rung.
3. `--ir-emit` byte-identical to pre-goal baseline at every rung.
4. Each rung commits exactly one construct. No bundling.
5. Each rung's anchor program must flip from non-honest to honest PASS.
6. `SM_BB_PUMP_AST` count in Icon path never increases (only decreases).

---

## Watermark

```
Last session: 2026-05-12 (carved)
one4all HEAD: (set at IB-0)
Honest PASS at carve: (set at IB-0)
Current rung: IB-0
```
