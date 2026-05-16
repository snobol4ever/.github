# GOAL-ICON-BB-JCON.md — Icon: BB emitters + lower_icn DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`
**Reference:** `/refs/jcon-master/tran/irgen.icn` + `tran/ir.icn`; `.github/jcon_irgen.icn`

## Invariants (READ FIRST)

1. **No AST walking in modes 2/3/4.** Modes 2 (sm_interp) and 3 (sm_jit_interp) print `[NO-AST] <opcode>` on stderr if a tree_t* would be dereferenced. If a gate breaks with `[NO-AST] FOO`, write fresh SM/BB lowering for FOO — do not restore the AST-walking call. Mode 1 (`--ir-run` AST interp) is the reference path and unchanged.
2. **Zero C Byrd-box functions.** A C BB is `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω in C. None may exist. All BBs are x86 emitted at runtime, or `IR_block_t` DCGs driven by `icn_bb_dcg`. Exceptions: `icn_lazy_box` and `icn_bb_dcg` (infrastructure shims).
3. **Cross-language: SM↔SM via hook, BB↔BB via universal four-port contract.** Within a language: SM bridge opcodes broker that language's BB-land (Icon=`SM_BB_PUMP_PROC`/`icn_bb_dcg`/`proc_table`, SNOBOL4=`SM_PAT_*`/`pat_cat`/PATND_t, Prolog=`SM_BB_ONCE_PROC`/`pl_bb_dcg`/`dcg_table`). Cross-language: SM(A)→SM(B) via `g_user_call_hook`; BB(A)→BB(B) via the universal α/β/γ/ω contract. **Forbidden:** invoking language-A's SM-bridge handler with a language-B BB object (semantics are hardcoded per language).
4. **Four ports hard-wired with direct pointers.** `IR_node_alloc` bakes the SCRIP default: `α=nd` (self-loop entry), `β=nd` (self-loop resume), `γ=NULL` (terminator = return value to driver), `ω=NULL` (terminator = return FAIL). Hard-wired direct pointers, not zero-init coincidence. Verified `927e0296`: zero call sites in src/ depend on NULL α/β as sentinel.
5. One construct per commit (or small coherent batch). No corpus source modified to work around runtime bugs.

## Session Setup

```
cd /home/claude/one4all && bash scripts/build_scrip.sh
```

Co-expressions / TT_SUSPEND / ucontext via `coro_runtime.c` are permitted for Icon completeness. What's banned: using `coro_runtime.c` to implement BBs as C coroutine four-port functions.

## Architecture

```
AST  --(lower time)-->  SM_Program   [SM_BB_XXX bridge opcodes]
                        IR_block_t * [pre-built per bridge op, lives in BB land]
```

SM is the entry. Bridge opcodes are the only SM↔BB contact. BB-land structures are pre-built (or stack-composed) before `bb_broker` is invoked. Nothing dereferences `tree_t*` at runtime.

**Target shape per Icon program:** two SM instructions — `SM_BB_PUMP_PROC "main"` + `SM_HALT`. Main's body is one `IR_block_t*` in `proc_table[i].ir_body`. Procs reference each other via `IR_CALL` nodes; the program is a composable BB DAG.

**Composer-bridge alternative (SNOBOL4-style, future):** `SM_BB_LIT_I` / `SM_BB_VAR` / `SM_BB_BINOP` / `SM_BB_CALL` / `SM_BB_SEQ` / `SM_BB_PROC` / `SM_BB_DRIVE` — same DAG built postorder via SM stream instead of at lower time. Composer helpers (`lower_icn_binop`, `lower_icn_alternate`, `lower_icn_to`, `lower_icn_limit`, `lower_icn_iterate`) already exist with the right shape.

**Three granularities, simultaneous in a single program:**

| Granularity | SM stream | BB land |
|---|---|---|
| Composer bridges (SNOBOL4 patterns) | `SM_PAT_LIT/ANY/CAT/ALT/...` postorder | tree via `pat_cat`/`pat_alt` |
| One BB per procedure (Icon today) | `SM_BB_PUMP_PROC "main"` + `SM_HALT` | `proc_table[i].ir_body` |
| One BB per program (endpoint) | `SM_BB_EVAL* <id>` + `SM_HALT` | single IR_block_t over whole program |

## Two execution paths for Icon generators

**Path A — `--ir-run` / `--sm-run` (interpreter):** `icn_bb_build(tree_t*)` → `bb_node_t{fn, zeta, 0}` → `bb_broker` drives `fn(zeta, α/β)`. `fn` is `icn_bb_dcg` driving an `IR_block_t` DCG built at lower time.

**Path B — `--sm-native` / mode-4 (JIT emitter):** `emit_bb_icon_*(s, f, b)` emits inline x86. Zeta in `.data`, blob reads/writes fields via `[rip+offset]`. No C function called by the blob.

**The `icn_bb_dcg` bridge:**
```c
typedef struct { IR_block_t *cfg; int first; } icn_dcg_state_t;
DESCR_t icn_bb_dcg(void *zeta, int entry) {
    icn_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; }
    return z->first ? (z->first=0, IR_exec_once(z->cfg)) : IR_exec_resume(z->cfg);
}
```
`IR_exec_resume` = same as `IR_exec_once` but skips `IR_reset` — continues from current node state.

## Lessons from jcon (reference, not target)

jcon (`tran/irgen.icn` + `tran/ir.icn`) uses four named labels per AST node (`start`/`resume`/`success`/`failure`), composes by pure label-stitching `ir_Goto`, has ~20 records (no per-construct opcodes), encodes generator state as normal IR registers (closure tmps), and represents loops as pure goto edges.

Our scrip IR is structurally aligned at the proc level (one `IR_block_t*` per proc, `IR_CALL` references) but differs in two ways:
- **Per-construct IR opcodes.** We have 8 `IR_ICN_*` opcodes (TO, TO_BY, UPTO, ITERATE, ALTERNATE, LIMIT, BINOP, EVERY); jcon does these as generic chunks. **Retracted as overreach (2026-05-15 fu#3):** per-construct opcodes are correct for encoding per-language port semantics inside the universal four-port envelope. Kept.
- **Pointer-field α/β/γ/ω vs label-based.** A possible future `GOAL-LOWER-REDESIGN` arc may rewire γ/ω to point at successor nodes (label-threaded). Until then, self-loop α/β + NULL-terminator γ/ω IS the contract.

Kept as coding-style technique: **failure/success threading by label at lower time.** When writing a new lowering, think "four labels per node, emit edges connecting children's labels to mine" — clearer than "what state struct do I need?"

## How to implement each construct

1. **Read jcon's `ir_a_CONSTRUCT`** in `tran/irgen.icn` for four-port wiring.
2. **Add IR kind** to `IR_e` in `scrip_ir.h`.
3. **Add executor case** in `ir_exec.c::IR_exec_node`: use `nd->state` (0=α, 1=β), `nd->counter`, `nd->value`, `nd->sval`, `nd->ival`. Return `nd->γ` (success) or `nd->ω` (fail).
4. **Add DCG builder** in `lower_icn.c`: `lower_icn_CONSTRUCT(args...)` calls `IR_alloc`, `IR_node_alloc(IR_ICN_CONSTRUCT)`, wires fields, returns cfg.
5. **Wire into `icn_bb_build`** (`icn_runtime.c`): replace TT_CONSTRUCT lazy fallback with `icn_bb_dcg` over the new cfg.
6. **Inline x86 emitter** (`emit_bb.c`): replace `ICN_STUB` with `.data` zeta + `.text` α/β. Study `emit_bb_xbal` for result-delivery pattern.
7. GATE-1..4, commit.

State struct templates (from deleted `icon_gen.c`, recoverable via `git show HEAD~5:src/runtime/interp/icon_gen.c`):
- `icn_to_state_t = { lo, hi, cur }`
- `icn_to_by_state_t = { lo, hi, step, cur }`
- `icn_iterate_state_t = { obj, pos, len, s }`
- `icn_alternate_state_t = { left_bb, right_bb, phase }`

## Gates

```
GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=16
GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= prev
```

## Completed steps

| Step | Outcome | Commit |
|---|---|---|
| IJ-19-debug | `upto` scalar dispatch fixed; IR_ICN_UPTO uses sval2 | `a82b42c5` |
| IJ-19-to | IR_ICN_TO DCG via icn_bb_dcg | `bb48e6c3` |
| IJ-19-to-by | IR_ICN_TO_BY DCG (ival/ival2/ival3 = lo/hi/step) | `a0b0700b` |
| IJ-19-iterate | IR_ICN_ITERATE string path (list/table/Raku still lazy) | `8cf94938` |
| IJ-19-alternate | IR_ICN_ALTERNATE DCG (n-ary chain) | `51460d4f` |
| IJ-19-limit | IR_ICN_LIMIT DCG | `b7d74bf9` |
| IJ-19-binop-gen | IR_ICN_BINOP DCG + binop_map[] + TT_CAT cross-product | `f63c60f0` |
| IJ-AST-IR-BB-if-every-to | TT_IF/EVERY/TT_TO via IR_IF + IR_EVERY | `c2c20d1a` |
| IJ-AST-IR-BB-while-until-seqexpr-globals | TT_WHILE/UNTIL/SEQ_EXPR/GLOBAL/INITIAL | `b974e111` |
| IJ-19-fail | fail keyword propagation in proc bodies | `992a2a18` |
| IJ-19-tt_seq | TT_SEQ conjunction short-circuit (was sharing case with TT_SEQ_EXPR) | `cac06b4e` |
| TT_SUSPEND | user-proc generators via GeneratorState DCG (ucontext) | `00da02b6` |
| IJ-19-to-dyn | TT_TO with non-literal bounds (TT_VAR / TT_FNC etc.) — IR_ICN_TO now evaluates `c[0]`/`c[1]` on α to seed `ival`/`ival2` when present | `c4de1e69` |

## NEXT step

**More `lower_icn_expr_node` coverage** to grow ir-run + honest. In order of complexity:

1. **TT_REPEAT** — infinite-loop construct. Wraps body in IR_WHILE with always-true cond.
2. **TT_ALTERNATE** at the lowering layer — emit `IR_ICN_ALTERNATE` from `lower_icn_expr_node` so alternation in main proc body composes into the IR_block_t.
3. **TT_AUGOP** — `+:=` / `-:=` / etc. Lower as `var := var op rhs`.
4. **Nested user-proc TT_FNC** — main proc body calling another user proc. Emits `IR_CALL` referencing `proc_table[callee].ir_body`.

Each step: extend `lower_icn_expr_node` in `lower_icn.c`, add executor case to `ir_exec.c` if a new IR kind is needed, run GATE-1..4, commit.

**Remaining TT_ITERATE paths:** list (rung22), table (rung13_table_iterate). Add when reached.

## Done when

`icn_bb_build` lazy fallbacks → `icn_bb_dcg` + `IR_block_t`. `ICN_STUB` one-liners in `emit_bb.c` → real inline x86. ir-run ≥ 230. honest ≥ 268. GATE-1..4 green.

## Watermark

```
one4all: c4de1e69 (IJ-19-to-dyn landed)  corpus: 1fe096c
ir-run:  31/265    honest: 278 PASS / 0 FAIL / 0 ABORT
smoke_icon: 5/5    broker: 16/49
cross-lang smokes: snobol4 7/7, raku 5/5, snocone 5/5, rebus 4/4, prolog 0/5 (intentional — see GOAL-PROLOG-BB-JCON)
```

Verified reproducible 2026-05-15 (Opus 4.7) after `libgc-dev` install: all four gates green.

**Session 2026-05-15 (Opus 4.7):** GOAL-ICON-BB-JCON.md and GOAL-PROLOG-BB-JCON.md trimmed (1155→140 and 561→91 lines; full per-session watermark logs preserved in git, banners collapsed to a 5-item invariant list). Landed IJ-19-to-dyn: non-literal `TT_TO` bounds via recursive child-eval on α. Lowering in `lower_icn.c` now lowers `e->c[0]`/`e->c[1]` as IR children when not both TT_ILIT; executor in `ir_exec.c` evaluates those children on α to seed `ival`/`ival2`. Verified: `every write(1 to n)` with `n := 3` lowers and runs correctly in both `--ir-run` and honest `--sm-run`. All four gates unchanged. Unlocks variable/computed loop bounds — prerequisite for several upcoming `lower_icn_expr_node` extensions (TT_REPEAT, TT_AUGOP, nested TT_FNC).
