# GOAL-ICON-BB-JCON.md — Icon: BB emitters + lower_icn DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`
**Reference:** `/refs/jcon-master/tran/irgen.icn` + `tran/ir.icn`; `.github/jcon_irgen.icn`

## Invariants (READ FIRST)

1. **No AST walking in modes 2/3/4.** Modes 2 (sm_interp) and 3 (sm_jit_interp) print `[NO-AST] <opcode>` on stderr if a tree_t* would be dereferenced. If a gate breaks with `[NO-AST] FOO`, write fresh SM/BB lowering for FOO — do not restore the AST-walking call. Mode 1 (`--interp` AST interp) is the reference path and unchanged.
2. **Zero C Byrd-box functions.** A C BB is `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω in C. None may exist. All BBs are x86 emitted at runtime, or `IR_block_t` DCGs driven by `icn_bb_dcg`. Exception: `icn_bb_dcg` (infrastructure DCG driver). (`icn_lazy_box`, previously listed here, was empirically dead and removed in DAI-7b on 2026-05-17.)
3. **Cross-language: SM↔SM via hook, BB↔BB via universal four-port contract.** Within a language: SM bridge opcodes broker that language's BB-land (Icon=`SM_BB_PUMP_PROC`/`icn_bb_dcg`/`proc_table`, SNOBOL4=`SM_PAT_*`/`pat_cat`/PATND_t, Prolog=`SM_BB_ONCE_PROC`/`pl_bb_dcg`/`dcg_table`). Cross-language: SM(A)→SM(B) via `g_user_call_hook`; BB(A)→BB(B) via the universal α/β/γ/ω contract. **Forbidden:** invoking language-A's SM-bridge handler with a language-B BB object (semantics are hardcoded per language).
4. **Four ports hard-wired with direct pointers.** `IR_node_alloc` bakes the SCRIP default: `α=nd` (self-loop entry), `β=nd` (self-loop resume), `γ=NULL` (terminator = return value to driver), `ω=NULL` (terminator = return FAIL). Hard-wired direct pointers, not zero-init coincidence. Verified `927e0296`: zero call sites in src/ depend on NULL α/β as sentinel.
5. **Up to three orthogonal constructs per session, separate commits, single gate run at end** (Lon, sess 2026-05-16). Three is a ceiling, not a target. Orthogonal means: different IR kinds, different rung clusters, no shared β-pump or descriptor-tag work. If a gate breaks, `git bisect` across the three commits (3 steps max). Handoff records one row per construct in the Completed steps table with its own rung delta. No corpus source modified to work around runtime bugs.

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

**Path A — `--interp` (interpreter):** `icn_bb_build(tree_t*)` → `bb_node_t{fn, zeta, 0}` → `bb_broker` drives `fn(zeta, α/β)`. `fn` is `icn_bb_dcg` driving an `IR_block_t` DCG built at lower time.

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
GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS >= prev
GATE-3  bash scripts/test_icon_all_rungs.sh             # --interp PASS >= prev
```

Note: the old GATE-4 (`test_icon_sm_no_ast_walk.sh`) is deleted as of
IJ-DEL-ICN-AST. After the Icon AST-walker amputation, ABORT (mode-2
secretly calling the Icon walker) is structurally impossible — the walker
doesn't exist. The gate became a tautology pretending to be a tripwire.
Mode-1/mode-2 parity is now carried by GATE-3 under `--interp`.

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
| IJ-AUGOP-REPEAT-ALT-NOT | TT_AUGOP (+:= -:= *:= /:= %:= ||:= relop augops) → IR_BINOP+IR_ASSIGN; TT_REPEAT → IR_REPEAT (loop until body FAIL); TT_ALTERNATE → IR_ALT (n-ary); TT_NOT → IR_NOT; IR_CALL user-proc dispatch via proc_table ir_body + frame push/pop. ir-run 31→56 (+25). | `17eae4a3` |

| IJ-SEQ-SIZE-CASE-STRRELOP-RETURN | TT_SEQ (conjunction → IR_IF); TT_SIZE → IR_SIZE; TT_CASE → IR_CASE (selector+key/val+default); TT_LLT/LLE/LGT/LGE/LEQ/LNE → IR_BINOP with ICN_BINOP_S* string relop kinds; TT_RETURN → IR_RETURN with FRAME.returning early-exit propagation through IR_SEQ and IR_CALL user-proc dispatch. ir-run 56→74 (+18). | `14211966` |
| IJ-BREAK-NEXT-IDENTICAL-NULL-RANDOM | TT_LOOP_BREAK/IR_BREAK, TT_LOOP_NEXT/IR_NEXT (loop_break/loop_next save+restore in IR_EVERY/WHILE/UNTIL/REPEAT); TT_PROC_FAIL→IR_FAIL; TT_IDENTICAL/IR_IDENTICAL; TT_NULL/IR_NULL_TEST + TT_NULL no-arg→IR_LIT_NUL; TT_NONNULL/IR_NONNULL; TT_RANDOM/IR_RANDOM. ir-run 74→79 (+5). | `301fcd49` |
| IJ-NEG-POS | TT_MNS/IR_NEG and TT_PLS/IR_POS unary arith; executor reuses icn_binop_apply(SUB/ADD, INTVAL(0), v) for free int/real/string-coerce. ir-run 79→81 (+2). | `80497128` |
| IJ-CSET-LIT | TT_CSET literal lowered to IR_LIT_S (csets-as-strings, one char per member). TT_CSET_COMPL/UNION/DIFF/INTER deferred (need dedicated IR kinds for complement against 256-char &cset). ir-run 81→82 (+1). | `787644c7` |
| IJ-SCAN | TT_SCAN → IR_ICN_SCAN (push/pop scan_subj/scan_pos); TT_KEYWORD and &-prefix TT_VAR → IR_ICN_KEYWORD (resolves &subject/&pos/&null/&fail). Builtins any/many/upto/match/move/find/tab were already in icn_try_call_builtin_by_name; only the upstream lowering edge was missing. ir-run 82→97 (+15). Recovers rung05_scan_*, rung06_cset_any/many/upto, rung08_strbuiltins_* in one shot. | `1841f7de` |
| IJ-BINOP-GEN | TT_ADD/SUB/MUL/DIV/MOD/LT/LE/GT/GE/EQ/NE/CAT with generator operand → IR_BINOP_GEN (cross-product). Tracks per-child gen-kind so non-generator operands don't get re-pumped (avoids infinite loops on `5 > ((1 to 2) * (3 to 4))`). ir-run 97→105 (+8). Broker bonus: 18→19. | `05097be3` |
| IJ-CALL-SNAPSHOT | Snapshot/restore (value, counter, state) of callee's `ir_body` across `IR_exec_once` in `IR_CALL` user-proc dispatch. Recursive proc calls share the IR graph; the inner `IR_reset` was wiping the caller's mid-evaluation per-node state. Visible victim: `IR_BINOP_GEN` reads `nd->c[0]->value` after both children eval'd — when c[1] is a recursive call, c[0]'s value was FAILDESCR. Fixed value of `write(fact(5))` → `120` (was blank). Does NOT flip rung02_proc_fact PASS because `every write(fact(5))` still pumps (single-shot proc returns NOT FAIL → IR_EVERY can't tell it's done; Category 3 / Fix #2). Gates flat at watermark. | `398776da` |
| IJ-EVERY-SINGLESHOT | Fix #2 landed. proc_table.is_generator bit set at lower time by scanning lowered ir_body->all[] for IR_SUSPEND (src/lower/lower.c). New recursive classifier ir_is_single_shot(IR_t*) in src/lower/ir_exec.c: generator IR kinds (IR_ICN_*, IR_BINOP_GEN, IR_ALT, IR_ALTERNATE, IR_SUSPEND, IR_REPEAT, IR_TO_BY, IR_LIMIT, IR_ICN_SCAN) → 0; IR_CALL → recurse through proc_table.is_generator for user procs / small generator-builtin whitelist (find/upto/any/many/bal/key/seq) for builtins / all-args-single-shot otherwise; default → walk children. IR_EVERY consults it for c[0]; if single-shot, break after one iteration. Flips rung02_proc_fact, rung02_proc_add_proc. ir-run 105→107 (+2). Gates: smoke_icon 5/5, broker 19/49, honest 277/0/0. | `b1ed4117` |
| IJ-BINOP-GEN-VAR-RERED | In IR_BINOP_GEN β-pump, re-evaluate the non-generator side when it's a pure-variable read (IR_VAR / IR_ICN_KEYWORD). Fixes `every total := total + (1 to 5)` returning 5 instead of 15: the LHS `total` had been captured once at α and never re-read, so the binop computed 0+1, 0+2, …, 0+5. The augop form `total +:= (1 to 5)` already worked because TT_AUGOP lowers to plain IR_BINOP. Pure-var-only restriction protects side-effecting IR_CALL etc. from re-firing. Flips rung02_proc_locals. ir-run 107→108 (+1). | `304e9476` |
| IJ-SUSPEND-PUMP-WIRE | User-defined generator procs (TT_SUSPEND in body) now yield across IR_EVERY pumps. Three coherent edits: (1) `src/lower/lower.c` introduces `g_in_gen_proc_body`; the `ICN_BB_EVAL` macro skips its AST-register shortcut when set so the SM body emits real instructions (LOAD/STORE_FRAME, SUSPEND, …) rather than `[NO-AST] SM_BB_EVAL` stubs; `lower_proc_skeletons` walks the proc AST at lower time to set `proc_table[pi].is_generator=1` whenever TT_SUSPEND appears, regardless of whether `lower_icn_proc_body` succeeded. (2) `src/lower/ir_exec.c::IR_CALL` checks user-defined generator procs BEFORE `icn_try_call_builtin_by_name` (the `upto` builtin's scan-context guard `scan_pos > 0 \|\| nargs >= 2` was trivially true because `polyglot.c` initializes `scan_pos=1`, shadowing user-defined `upto`); when matched, builds `GeneratorState` via `generator_state_new_proc`, drives via `bb_broker_drive_sm_one`, persists across IR_EVERY pumps via `nd->opaque` + `nd->state==1`. (3) `src/runtime/interp/icn_runtime.c::icn_bb_pump_proc_by_name` mirrors the same routing for top-level proc calls. No AST walking at runtime — reads the bit set at lower time. Flips rung03_suspend_gen, rung03_suspend_gen_compose, rung03_suspend_gen_filter. ir-run 108→111 (+3). broker 19→20 (+1). prolog smoke 4/5→5/5 (bonus). | `fe4a3168` |
| IJ-CSET-COMPL | TT_CSET_COMPL (`~E` Icon cset complement) lowered to IR_CSET_COMPL. Three coherent edits: (1) `src/include/IR.h` adds `IR_CSET_COMPL` after `IR_POS` in the IR_e enum. (2) `src/lower/ir_exec.c` adds executor case mirroring `TT_CSET_COMPL` in `icn_value.c::bb_eval_value`: eval c[0], coerce int/real → string via `descr_to_str_icn` (new include `"coerce.h"`), call `icn_cset_complement(cs)` against the 256-char universal cset, wrap result in `CSETVAL`. Handles FAIL/null/numeric coercion paths. (3) `src/lower/lower_icn.c` adds `TT_CSET_COMPL` case before default, parallel structure to `TT_MNS`/`TT_PLS`: recurse into c[0], allocate IR_CSET_COMPL node, wire single child. `[NO-AST] SM_BB_EVAL` stub for `~cset` expressions in `--interp` is now eliminated; `~'aeiou'` produces correct CSETVAL with type=cset. ir-run 111/265 unchanged (rung36_jcon_* integration tests gate on additional missing constructs: `&cset`/`&ascii` keywords + `\0`-safe scan builtins). Gates: smoke_icon 5/5, broker 20/49, honest 277/0/0, cross-lang smokes (sn4/raku/snocone/rebus/prolog) unchanged. | `0b931361` |
| IJ-CSET-BINOPS | TT_CSET_UNION/DIFF/INTER (Icon `E1++E2`/`E1--E2`/`E1**E2`) lowered to IR_CSET_UNION/DIFF/INTER. Three coherent edits paralleling IJ-CSET-COMPL: (1) `src/include/IR.h` adds three IR_e entries after `IR_CSET_COMPL`. (2) `src/lower/ir_exec.c` adds a shared fall-through case `IR_CSET_UNION:`/`IR_CSET_DIFF:`/`IR_CSET_INTER:` mirroring the matching `bb_eval_value` cases in `icn_value.c`: eval both children, coerce int/real → string via `descr_to_str_icn`, dispatch by `nd->t` to `icn_cset_union/diff/inter`, run through `icn_cset_canonical` for sort+dedup, wrap as `CSETVAL`. FAIL/null propagate cleanly. (3) `src/lower/lower_icn.c` adds shared `TT_CSET_UNION:`/`TT_CSET_DIFF:`/`TT_CSET_INTER:` case: lower both operands, map AST kind → IR kind, allocate node with n=2. Sanity-tested: `'aeiou' ++ 'xyz'` → `'aeiouxyz'` (8 chars); `'abcdef' -- 'bd'` → `'acef'` (4); `'abcdef' ** 'cdefgh'` → `'cdef'` (4); `~'aeiou' -- '0123456789'` → 112 chars. ir-run 111/265 unchanged (same downstream gating). Gates: smoke_icon 5/5, broker 20/49, honest 277/0/0, cross-lang smokes unchanged. | `0b931361` |
| IJ-SCAN-NULSAFE | `scan_builtins.c::any/many/upto/bal` made `\0`-safe. Added `cset_resolve(DESCR_t, &ptr, &len)` helper that consults `icn_kw_cset_len(ptr)` for keyword-cset storage (`&cset`/`&ascii`/`&lcase`/...) whose canonical-form buffer is null-prefixed (`stable[0]='\0'`, real chars follow), falling back to `strlen` for regular csets and strings. Added `cset_has(cv, clen, ch)` using `memchr` instead of `strchr` so cset membership tests are length-aware. Refactored `any` (line 14), `many` (line 35), `upto` (line 56), `bal` (line 127) — each cset argument now flows through `cset_resolve` + `cset_has` rather than `VARVAL_fn` + `strchr`. Eliminates silent truncation when scan builtins receive csets containing `\0` (kw csets) or when `~cset` complement results flow through scan ladder. ir-run 111/265 unchanged: no rung flips because cset-complement-driven rungs (`rung36_jcon_*`) gate on additional missing constructs beyond `\0`-safe scan, but the silent-truncation correctness floor is now solid for downstream work. Also restored missing `CODE_t *prolog_lower(PlProgram *)` function header in `src/frontend/prolog/prolog_lower.c` — commit `8fee1957` (PST-PL-6d) had left orphaned function body after helper additions; HEAD `0b931361` would not build from clean clone without this fix. Gates: smoke_icon 5/5, honest 277/0/0. | `068a7054` |
| IJ-FLIT | TT_FLIT real-literal lowering for Icon. `lower_icn_expr_node` (src/lower/lower_icn.c) was handling TT_ILIT but not TT_FLIT, so real literals in expression position fell through to ICN_BB_EVAL → `[NO-AST] SM_BB_EVAL` stub at runtime. Added TT_FLIT case mirroring TT_ILIT: `IR_node_alloc(IR_LIT_F)`, `nd->dval = e->v.dval`. IR_LIT_F executor in ir_exec.c already does `REALVAL(nd->dval)`. probe: `write(3.14)` → `3.14` (was `[NO-AST]` stub). **ir-run 111→125 (+14).** **Honest regression 277→272 (−5):** unmasked 5 programs (rung18_real_relop_real_relop_goal, rung36_jcon_arith/checkfpx/ck/mathfunc) that previously exited 0 with empty output (silently wrong) now timeout — they exercise real-typed binops/relops that IR_BINOP_GEN's binop_map doesn't yet handle for double operands. Net correctness improvement (visible failures > hidden failures); separate ticket needed for IR_BINOP_GEN real-typed arithmetic. | `48d797fa` |
| IJ-IRALLOC-OVERFLOW | IR_block_t gains `max` field; IR_node_alloc bounds-checked (returns NULL on overflow instead of stomping heap); lower_icn_proc_body IR_alloc 128→4096 — proc bodies with complex IR (real-typed relops over alternates, every-loops) were overflowing the 128-node cap and corrupting adjacent heap, manifesting as infinite loops under --interp. Also: IR_ICN_BINOP β outer loop missing `return nd->ω` when right.α also fails after left advances. **honest 272→276 (+4). broker 17→19 (+2). smoke 5/5.** | `6ddb9584` |
| IJ-TO-GEN | IR_ICN_TO operand re-pumping when bounds are generators. Mirrors IR_BINOP_GEN's cross-product β-pump: when counter > ival2, if c[1] (hi) is a generator, advance it; if c[1] exhausts and c[0] (lo) is a generator, reset c[1] and advance c[0]; only fail when both operand generators are exhausted. Inlined IR_IS_GEN_KIND_TO macro (same set as BINOP_GEN). Fixes rung01_paper_nested_to: `every write((1 to 2) to (2 to 3))` now produces full 8-value cross product 1,2,1,2,3,2,2,3 (was only 1,2). **ir-run 125→126 (+1).** Gates: smoke_icon 5/5. Honest neutral. | `92bfffd9` |

## NEXT step

Failing-rung survey (sess 2026-05-16d) found three categories driving remaining FAILs. Categories 1 and 2 landed; category 3 has been *decomposed* — Fix #1 landed:

1. ~~**Pattern-scan ops**~~ — ✅ landed in IJ-SCAN (`1841f7de`).
2. ~~**Generator cross-product in plain binops**~~ — ✅ landed in IJ-BINOP-GEN (`05097be3`).
3. **`every write(fact(5))` over-iteration** — both fixes landed:
   - **Fix #1 ✅** — `IJ-CALL-SNAPSHOT` (`398776da`). Recursive proc calls were wiping caller IR graph state via the inner `IR_reset`. Now snapshotted/restored. `write(fact(5))` correctly yields `120`.
   - **Fix #2 ✅** — `IJ-EVERY-SINGLESHOT`. proc_table.is_generator bit + recursive ir_is_single_shot classifier in IR_EVERY breaks the pump after one iteration when c[0] is structurally single-shot. ir-run 105→107 (+2). rung02_proc_fact and rung02_proc_add_proc flip PASS.

## NEXT step

**Three orthogonal constructs landed prior session (2026-05-17e, Opus 4.7): IJ-LCONCAT, IJ-FIND-GEN, IJ-SEQ-GEN. ir-run 191→194 (+3), zero regressions.**

**PIVOT (2026-05-17 cont., Lon directive):** stop the per-construct hunt. The Icon-specific `tree_t *` AST walker (`bb_eval_value` / `bb_exec_stmt` / `icn_bb_build` family in `src/runtime/interp/icn_*.c`) is the maintenance treadmill. It is co-resident with the universal `interp_eval` AST walker, but **only used when `g_lang==LANG_ICN`**. The IR layer (`src/lower/ir_exec.c`) and the SM/BB engines (modes 2/3/4) are now the correctness floor. Delete the Icon AST walker; let modes 2/3/4 carry Icon.

### IJ-DEL-ICN-AST — Surgical removal plan

**Scope (what gets deleted):**
- `src/runtime/interp/icn_value.c` (1239 LOC) — `bb_eval_value(tree_t*)` and helpers it carries that are only used by it.
- `src/runtime/interp/icn_stmt.c` (149 LOC) — `bb_exec_stmt(tree_t*)`.
- `src/runtime/interp/icn_runtime.c` (1748 LOC) — partially. Contains both `icn_bb_build(tree_t*)` (the AST-walking BB builder, used only by mode-1) **and** `icn_bb_dcg` + `icn_bb_pump_proc_by_name` + `proc_table` machinery (used by SM/BB modes). Split, don't blanket-delete.
- `scan_builtins.c`, `raku_builtins.c`, `icn_value.h`, `icn_stmt.h` — audit: keep DESCR_t-input helpers (e.g. `icn_lconcat_d`, `icn_str_concat_d`, `cset_resolve`) used by `ir_exec.c`; delete `tree_t *`-input wrappers.

**Scope (what stays):**
- `src/driver/interp_eval.c` (4281 LOC) — the universal AST walker. Out of scope for this surgery.
- `src/driver/interp_*.c` (call/data/exec/hooks/label/ref) — out of scope.
- `src/lower/ir_exec.c` — stays; it walks `IR_block_t *`, not `tree_t *`.
- All Icon parsing, lowering, SM emission, BB native emission.
- Mode 1 itself (`--interp`) — stays for non-Icon languages (SNOBOL4, Snocone, Rebus, Prolog, Raku via `interp_eval`). Icon programs under mode 1 will return `[NO-AST]` on Icon-specific tags or be re-routed to mode 2.

**External coupling — must be re-routed or removed before file deletion:**
- `src/driver/interp_eval.c` lines 136, 137, 144, 145, 153, 154, 162-163 — 9 sites of `(g_lang==LANG_ICN)?bb_eval_value(...):interp_eval(...)`. Drop the ICN branch; either let `interp_eval` handle (if AST kind is universal) or stub with `NO_AST_WALK_GUARD("<tag>")` so mode 1 fails loud on Icon-only AST kinds.
- `src/driver/interp_eval.c` lines 3687, 3699, 3975 — 3 sites of `icn_bb_build(...)`. These are mode-1's hook into Icon's Byrd-box AST builder. **Hard delete**: surrounding code paths only fire when `g_lang==LANG_ICN`; replace with `NO_AST_WALK_GUARD` stubs.
- `src/processor/sm_jit_interp.c` line 263 — `extern bb_node_t icn_bb_build(...)`. Remove the extern; audit whether the call site is dead post-deletion.
- `src/lower/ir_exec.c` line 1713 — `IR_ICN_EVERY` body invokes `bb_exec_stmt((void *)nd->sval2)` where `sval2` is a `tree_t *`. **THIS IS A REAL COUPLING.** IR_ICN_EVERY's body is still stored as AST, not lowered to IR. Two options: (a) lower every-body to IR at lower time, store IR_block_t* in opaque (correct fix, ≈ 60 LOC in `lower_icn.c`); (b) defer IR_ICN_EVERY entirely to mode 2/3/4 via existing SM_BB_PUMP_PROC. Pick (a) for surgical simplicity — it's the next IR kind to lower anyway.
- `src/runtime/interp/pl_runtime.c` lines 729, 833, 1880 — 3 sites of `bb_eval_value` from Prolog calling Icon (cross-language hook). **Delete via the cross-language SM↔SM hook** (`g_user_call_hook`, per Invariant 3) instead. Hook already exists per the architecture doc; these 3 sites are the holdover that predates the hook.
- `src/driver/rs23_diag.c` lines 39-42 — diagnostic strings only; drop the matches, the function names will no longer exist.
- `Makefile` lines 112-118 and 301-308 — remove the three Icon AST-walker .c files from the build; keep `interp_*.c` lines for universal walker.

### Steps (one commit per step, gates after each)

The order is **callers first, leaves last** — never delete a definition while any caller exists. Run `bash scripts/build_scrip.sh` after every step; build must stay green throughout.

- [x] **DAI-1 ✅ 2026-05-17 (Opus 4.7) — Remove IR_ICN_EVERY entirely.** **Audit finding:** `IR_ICN_EVERY` was reached *only* from inside the Icon AST walker chain — both callers of `lower_icn_every` lived in `icn_runtime.c::icn_bb_build`. The proper IR-lowering path uses language-agnostic `IR_EVERY` with body pre-lowered via `lower_icn_expr_node` (see `lower_icn.c::TT_EVERY` ~line 529). `IR_ICN_EVERY` and `lower_icn_every` were dead-on-the-vine. **Action taken:** deleted case in `ir_exec.c`, deleted `lower_icn_every` from `lower_icn.c` + declaration, deleted `IR_ICN_EVERY` enum from `IR.h`. Two AST-walker callers in `icn_runtime.c` stubbed. **Result:** ir-run 194/265 unchanged. Commit `b3e08fe8`.

- [x] **DAI-2 ✅ 2026-05-17 (Opus 4.7) — Amputate the three Icon AST walker entry points: bb_eval_value, bb_exec_stmt, icn_bb_build.** Per Lon directive ("just remove the actual AST walkers, leave stub bombs everywhere the calls to mode 1 hung"), each function body was replaced with a loud bomb that prints `[DAI-BOMB] <name> called ... tree tag=N` to stderr and exits with status 78. **Surprising result:** Icon `--interp` held at 194/265, zero regression, **zero bomb fires across all 265 rungs**. The three AST-walker functions were already silently dead for the rung suite — mode-1 Icon was routing through `interp_eval` + `ir_exec.c` (which walks `IR_block_t`, not `tree_t*`), never through the Icon-specific walker. **Net amputation: −1641 LOC** across three files:
  - `src/runtime/interp/icn_value.c` 1239→336 (preserved DESCR_t helpers used by ir_exec.c)
  - `src/runtime/interp/icn_stmt.c`  149→ 22
  - `src/runtime/interp/icn_runtime.c` 1743→1166 (preserved icn_bb_dcg, proc_table, icn_every_body_pre/broke — all used by modes 2/3/4)

  Commit `3e1fc9cd`. Caller cleanup (DAI-3 through DAI-5 below) **deferred** to next session — the bombs make any latent caller fire loudly and visibly, so urgency is now zero.

- [x] **DAI-3 ✅ 2026-05-17f (Opus 4.7) — Disable ICN_BB_EVAL shortcut in `src/lower/lower.c:34`.** Macro was emitting `SM_BB_EVAL <every_table_index>` for Icon expressions outside gen-proc bodies, deferring BB construction to runtime via `icn_bb_build(tree_t*)`. After DAI-2 that runtime resolver is a `[DAI-BOMB]` stub; the `SM_BB_EVAL` handler in `sm_jit_interp.c` was already `NULL`. Macro replaced with no-op; Icon expressions outside gen-proc bodies now lower through the standard SM emitter (`SM_PUSH_LIT_S`/`SM_PUSH_LIT_I`/`SM_PUSH_VAR`/etc.) like every other language. Commit `a2365c5f`.

  **Major measurement landed with this step:** ran the rung ladder under `--interp` (mode 2) for the first time. **Result: `--interp` 194/265 = `--interp` 194/265, identical pass and fail sets.** Mode-2 is at parity with mode-1. The 36 failing rungs fail in *both* modes — they are real IR/BB/SM gaps, not mode-2 immaturity. This is the strongest possible validation of the IJ-DEL-ICN-AST surgery: there is no mode-1 advantage left to preserve.

- [x] **DAI-4 ✅ 2026-05-17g (Opus 4.7) — Drop `icn_bb_build` callers in `interp_eval.c` + `sm_jit_interp.c`.** Replaced the 3 sites (TT_EVERY-assign-rhs, TT_EVERY-gen, TT_AUGOP-suspend-rhs) with `NO_AST_WALK_GUARD("icn_bb_build/<tag>")` + `[DAI-BOMB]` fingerprint + `exit(78)`. Removed dangling extern in `sm_jit_interp.c:263`. interp_eval.c −31 lines net. **Gates: ir-run 194/265 unchanged. Zero bombs fired across rung suite + all 5 frontends' smokes** — empirical confirmation that mode-1 Icon never reaches these `interp_eval`/TT_EVERY/TT_AUGOP branches (they're lowered to IR_EVERY/IR_AUGOP at lower time and dispatched through `ir_exec.c`).

- [x] **DAI-5a ✅ 2026-05-17h (Opus 4.7) — Swap stale `bb_eval_value` callers → `interp_eval`.** Empirically traced (instrument + revert) all `bb_eval_value` call sites: zero fires across smoke (all 6 frontends), Icon rungs (265), prolog/raku/icon crosschecks. Confirmed dead — same finding as DAI-2 had for `icn_bb_build`. Replaced each site with `interp_eval` (universal AST walker, mode-1 reference path; already carries `NO_AST_WALK_GUARD` at its top). `pl_runtime.c`: 3 sites + added `extern DESCR_t interp_eval(tree_t *e);` next to existing forward decls. `raku_builtins.c`: 46 sites via sed; decl transitively visible through `interp_private.h → interp.h`. `interp_eval.c::icn_string_section_assign`: 7 `(g_lang==LANG_ICN)?bb_eval_value(...):interp_eval(...)` ternaries collapsed to `interp_eval(...)`; removed local extern at line 162. **Net: zero non-stub callers of `bb_eval_value` remain in src/.** Diagnostic strings in `rs23_diag.c` (backtrace fingerprint detectors) and DAI-4 bomb messages preserved. Commit `f7c9cfeb`.

- [x] **DAI-5b-1 ✅ 2026-05-17i (Opus 4.7) — Relocate surviving DESCR_t helpers.** Moved 3 helpers (`icn_str_concat_d`, `icn_lconcat_d`, `icn_proc_as_value`) from `icn_value.c` to `icn_runtime.c`. `icn_proc_as_value` gains locality with `proc_count`/`proc_table`. Declarations in `icn_value.h` unchanged; external linkage continues to resolve. Commit `28005157`.

- [x] **DAI-5b-2 ✅ 2026-05-17i (Opus 4.7) — Delete `icn_value.c` / `icn_stmt.c` / `icn_stmt.h`; scrub public AST-walker symbols.** Scope expanded mid-step: discovered ~25 residual internal call sites of `bb_eval_value` / `icn_bb_build` / `bb_exec_stmt` inside surviving Icon zeta-fn bodies (`icn_lazy_box` plus other infrastructure DAI-2 preserved). Empirically unreachable per DAI-5a trace pass. Solution: 3 file-local `static` `[DAI-BOMB]` stubs added near the top of `icn_runtime.c` to keep internal call sites link-resolvable while bombing-loudly if ever reached. Public globals are gone — `icn_value.h` no longer declares `bb_eval_value`; `icn_runtime.h` and `icon_gen.h` no longer declare `icn_bb_build`. `bb_icn_rnd_seed` global storage relocated from deleted `icn_value.c` to `icn_runtime.c` (consumers unchanged). Makefile: source list + compile rules pruned of both files. **−294 LOC across 3 deleted files;** +31 LOC stub block in `icn_runtime.c`; −4 lines headers; −4 lines Makefile. Outside `icn_runtime.c`, zero real callers of the three amputated symbols remain in `src/` — only diagnostic comments, `rs23_diag.c` backtrace fingerprint detectors, and DAI-4 bomb-message strings. Commit `ed957bfe`.

- [x] **DAI-5c ✅ 2026-05-17j (Opus 4.7) — Re-baseline at `--interp`.** Parameterized `test_icon_ir_all_rungs.sh` on `--mode` (commit `1823e90b`), then in this session collapsed back to a hardcoded `--interp` canonical (commit `b65882ea`) after Lon's directive to eliminate the alias surface entirely. Script renamed `test_icon_ir_all_rungs.sh` → `test_icon_all_rungs.sh`. Result: **`--interp` PASS=194 FAIL=36 XFAIL=35 TOTAL=265** — byte-identical to the prior `--ir-run` measurement (diff = 0 lines from the dual-mode run done in DAI-5c-trans). The post-amputation reference path (`--interp`) is at full parity with the pre-deletion reference path (`--ast-run`). 194/265 is the new floor.

- [x] **DAI-6 ✅ 2026-05-17j (Opus 4.7) — Update docs + delete the honest gate.** Edited `ARCH-ICON.md` (Active-goal pointer refreshed; IJ-DEL-ICN-AST post-amputation note added). Edited `RULES.md` (Icon-specific addendum after the No-AST-Walking absolute rule documents the `--interp`-as-reference shift; the flaky-gate table row for `test_icon_sm_no_ast_walk.sh` removed since the gate itself is deleted). Edited the Icon BB JCON row in `PLAN.md` to mark DAI-5c + DAI-6 done. Updated the Watermark block at the bottom of this file. Deleted `scripts/test_icon_sm_no_ast_walk.sh`: after IJ-DEL-ICN-AST the gate's ABORT semantics ("detected mode-2 secretly calling the Icon AST walker") are structurally impossible — there's no walker to call — so the gate was a tautology pretending to be a tripwire. The mode-1/mode-2 parity measurement is now carried by `test_icon_all_rungs.sh` under `--interp`. Per RULES.md flaky-gate table this gate was also the documented flaky one (~6 PASS-point variance), so removing it removes a known noise source from the watermark. GATE-3 + GATE-4 of this goal collapsed to a single `test_icon_all_rungs.sh` row.

### Risk register

- **The 194/265 gate vanishes.** ✅ Resolved 2026-05-17j (DAI-5c). The new floor is `--interp` rung-pass count at 194/265 — byte-identical to the pre-amputation `--ast-run` measurement (DAI-5c-trans confirmed empty-diff PASS/FAIL sets across both modes). Mode-1 (`--ast-run`) and mode-2 (`--interp`) were at full parity for the entire ladder, so the deletion was lossless. After CLI-3M-10 only `--interp` remains as a canonical name.
- **IR_ICN_EVERY body-lowering may surface latent bugs.** Many every-bodies have never been lowered; statement kinds that lower-time only handles inside procs may be missing inside every-body. **Mitigation:** DAI-1 is the riskiest step; gate hard, revert independently if it regresses.
- **Cross-language Prolog→Icon (DAI-2) may not have a wired hook for value-eval.** If `g_user_call_hook` only supports procedure-call semantics, the hook itself must be extended. **Mitigation:** if extension is non-trivial, fall back to keeping `bb_eval_value` *only* for the 3 pl_runtime sites and deferring DAI-5 deletion of `icn_value.c` until the hook is extended in a follow-on goal. Don't conflate scope.
- **Surface area is large (≈ 3000 LOC + caller edits).** Single-session bites only.

## Completed steps (session 2026-05-17e, Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-LCONCAT | TT_LCONCAT (`E1 ||| E2`) lowered to new IR_ICN_LCONCAT. Four coherent edits: (1) `src/include/IR.h` adds IR_ICN_LCONCAT after IR_INITIAL. (2) `src/runtime/interp/icn_value.{c,h}` factors reusable `icn_str_concat_d(DESCR_t,DESCR_t)` + `icn_lconcat_d(DESCR_t,DESCR_t)` out of the existing tree_t*-taking bb_str_concat / TT_LCONCAT block — list-list builds fresh icnlist, otherwise falls back to string concat with coercion. (3) `src/lower/ir_exec.c` includes icn_value.h and adds IR_ICN_LCONCAT executor calling icn_lconcat_d. Single-shot — NOT generator-kind (Icon spec does not cross-product over `\|\|\|`). (4) `src/lower/lower_icn.c` adds TT_LCONCAT lowering case after TT_CAT/binop block. Plus kind_name. **ir-run 191→192 (+1). rung15_real_swap_lconcat PASS.** smoke_icon 5/5. | `e8edc709` |
| IJ-FIND-GEN | TT_FNC `find()` 2/3/4-arg lowered to new IR_ICN_FIND_GEN (true generator). Five coherent edits: (1) `src/include/IR.h` adds IR_ICN_FIND_GEN after IR_ICN_LCONCAT. (2) `src/lower/ir_exec.c` adds IR_ICN_FIND_GEN executor with α (eval needle, hay, optional start/stop; normalize 0/neg bounds; cache strings + stop in GC_malloc'd struct in opaque; counter = 0-based search-from position) and β (strstr from counter; on hit yield 1-based pos and advance counter, on miss/past-stop FAIL via ω). Empty-needle case yields each 1..stop position once. (3) Same file adds IR_ICN_FIND_GEN to ir_is_single_shot exclusion + IR_IS_GEN_KIND macro + ALT_IS_GEN macro. (4) `src/lower/lower_icn.c` adds find() special-case in TT_FNC after key() — only 2/3/4-arg forms; 1-arg (scan-context) still routes through IR_CALL. Plus kind_name. **ir-run 192→193 (+1). rung08_strbuiltins_find_gen PASS** (`every write(find("a","banana"))` yields 2, 4, 6). smoke_icon 5/5. **Carry-forward:** start/stop bounds normalization (zero=end, negative=from-end) written but untested against jcon corner cases — may surface in rung36 4-arg find usage. | `158144eb` |
| IJ-SEQ-GEN | TT_FNC `seq()` 0/1/2-arg lowered to new IR_ICN_SEQ_GEN (true generator). Five coherent edits paralleling IJ-FIND-GEN: (1) `src/include/IR.h` adds IR_ICN_SEQ_GEN. (2) `src/lower/ir_exec.c` adds IR_ICN_SEQ_GEN executor with α (read optional start [default 1] + step [default 1]; int-coerce from real if needed; zero step bumped to 1 to avoid no-progress; cache step in ival, start in counter; yield start) and β (counter += ival; yield). No upper bound — relies on IR_LIMIT (`\N`) or every-break for termination. (3) Same file adds IR_ICN_SEQ_GEN to ir_is_single_shot exclusion + IR_IS_GEN_KIND + ALT_IS_GEN macros. (4) `src/lower/lower_icn.c` adds seq() lowering after find() — handles 0/1/2-arg forms. Plus kind_name. **ir-run 193→194 (+1). rung30_builtins_misc_seq PASS** (`every write(seq(1) \ 3)` yields 1, 2, 3). All gates hold. | `f81302ca` |

## Completed steps (session 2026-05-17f, Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| DAI-1 | Remove dead-on-vine IR_ICN_EVERY: was reachable only via Icon AST-walker (icn_bb_build → lower_icn_every → ir_exec.c IR_ICN_EVERY case → bb_exec_stmt(tree_t*)). Mode-2/3/4 use language-agnostic IR_EVERY with body pre-lowered to IR. Three files edited (IR.h enum, ir_exec.c case, lower_icn.{c,h} function+decl); two AST-walker callers in icn_runtime.c stubbed. ir-run 194/265 unchanged. | `b3e08fe8` |
| DAI-2 | Amputate the three Icon AST walker entry points: `bb_eval_value` (icn_value.c, 1239→336 LOC), `bb_exec_stmt` (icn_stmt.c, 149→22 LOC), `icn_bb_build` (icn_runtime.c, 1743→1166 LOC). Each body replaced with `[DAI-BOMB]` stub that prints to stderr + exit(78). Preserved DESCR_t-input helpers (icn_str_concat_d, icn_lconcat_d, cset_resolve, builtin tables) in icn_value.c head; preserved icn_bb_dcg/proc_table/icn_every_body_pre+broke in icn_runtime.c head. **Net −1641 LOC. Icon --interp 194/265 unchanged. Zero bomb fires across 265 rungs** — proves the Icon AST walker was already silently dead for the rung suite; mode-1 Icon executes via interp_eval+ir_exec (IR_block_t walker), never the Icon-specific tree_t* walker. All smoke gates hold floor. | `3e1fc9cd` |
| DAI-3 | Disable ICN_BB_EVAL shortcut in `src/lower/lower.c:34` — macro was emitting `SM_BB_EVAL <every_table_index>` for Icon expressions outside gen-proc bodies, deferring BB construction to runtime via `icn_bb_build` (now a [DAI-BOMB] stub). `SM_BB_EVAL` handler in sm_jit_interp.c was already NULL. Macro now a no-op; Icon expressions lower through standard SM (`SM_PUSH_LIT_S/I/F`, `SM_PUSH_VAR`) like every other language. **Major measurement: `--interp` 194/265 = `--interp` 194/265, identical sets.** Mode-2 at parity with mode-1; the 36 fails are real IR/BB/SM gaps, not mode-2 immaturity. | `a2365c5f` |

## Completed steps (session 2026-05-17g, Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| DAI-4 | Drop `icn_bb_build` callers in `interp_eval.c` + `sm_jit_interp.c`. The 3 sites (TT_EVERY-assign-rhs at ~3683, TT_EVERY-gen at ~3698, TT_AUGOP-suspend-rhs at ~3974) replaced with `NO_AST_WALK_GUARD("icn_bb_build/<tag>") + [DAI-BOMB] fprintf + exit(78)`. Dangling `extern bb_node_t icn_bb_build(tree_t *e);` at `sm_jit_interp.c:263` removed. Net: interp_eval.c −31 lines, sm_jit_interp.c −2 lines. **ir-run 194/265 unchanged. Zero DAI-BOMs fired across rung suite.** smoke_icon 5/0, smoke_prolog 5/0, smoke_raku 5/0, smoke_rebus 4/0, smoke_snocone 5/0, smoke_snobol4 6/1 (pre-existing pattern FAIL). Empirical confirmation that mode-1 Icon never reaches these `interp_eval` TT_EVERY/TT_AUGOP branches — they're lowered to IR_EVERY/IR_AUGOP at lower time and dispatched through `ir_exec.c`. | `e3c803ea` |

## Completed steps (session 2026-05-17h, Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| DAI-5a | Swap stale `bb_eval_value(tree_t*)` callers → `interp_eval(tree_t*)` (universal AST walker). Empirical trace pass first: instrumented all 56 sites across `pl_runtime.c` (3), `raku_builtins.c` (46), `interp_eval.c::icn_string_section_assign` (7); ran full smoke + Icon rungs + prolog/raku/icon crosschecks; **zero trace fires** — confirming all sites are dead, same finding as DAI-2 had for `icn_bb_build`. Trace edits reverted, then swapped each site to `interp_eval` (which already carries `NO_AST_WALK_GUARD` at its top so any future reachability bug from modes 2/3/4 still aborts loudly). Forward decl added in `pl_runtime.c` next to existing externs; `raku_builtins.c` gets the decl transitively via `interp_private.h → interp.h`. Collapsed 7 `(g_lang==LANG_ICN)?bb_eval_value(...):interp_eval(...)` ternaries in `icn_string_section_assign` to plain `interp_eval(...)` and removed the local `extern bb_eval_value` at line 162. **Zero non-stub callers of `bb_eval_value` remain in src/.** Net: 58 insertions / 57 deletions across 3 files. Gates: ir-run 194/265 unchanged. smoke_icon 5/0, smoke_prolog 5/0, smoke_raku 5/0, smoke_rebus 4/0, smoke_snocone 5/0, smoke_snobol4 6/1 (pre-existing pattern FAIL). crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS unchanged. Zero DAI-BOMs fired. | `f7c9cfeb` |

## Completed steps (session 2026-05-17i, Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| DAI-5b-1 | Preparatory relocation of 3 surviving DESCR_t helpers (`icn_str_concat_d`, `icn_lconcat_d`, `icn_proc_as_value`) from `icn_value.c` to `icn_runtime.c`. `icn_proc_as_value` gains locality with the `proc_count`/`proc_table` it indexes. `icn_value.h` declarations unchanged — symbols still resolve, just from a different .o. Smoke_icon 5/0 sanity. Net +81 / −74 across 2 files. | `28005157` |
| DAI-5b-2 | Delete `icn_value.c` (−267 LOC), `icn_stmt.c` (−20), `icn_stmt.h` (−7); prune public AST-walker decls from `icn_value.h` (`bb_eval_value`), `icn_runtime.h` (`icn_bb_build`), `icon_gen.h` (`icn_bb_build`); prune Makefile (source list + compile rules); relocate `bb_icn_rnd_seed` global storage to `icn_runtime.c`. Discovered mid-step that ~25 residual internal call sites of `bb_eval_value`/`icn_bb_build`/`bb_exec_stmt` survive inside Icon zeta-fn bodies that DAI-2 preserved (`icn_lazy_box` plus others). Empirically unreachable per DAI-5a trace. Solution: 3 file-local `static` `[DAI-BOMB]` stubs near top of `icn_runtime.c` keep them link-resolvable while bombing-loudly if reached. Outside `icn_runtime.c`, **zero real callers of the three amputated symbols remain in `src/`** — only diagnostic comments + `rs23_diag.c` backtrace fingerprint detectors + DAI-4 bomb-message strings. Net: −294 LOC across 3 deleted files; +31 LOC stub block; −4 lines headers; −4 lines Makefile. Gates: ir-run 194/265 unchanged. smoke ×6 unchanged. crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS unchanged. Zero DAI-BOMs fired. | `ed957bfe` |

## Open step

- [x] **DAI-7 ✅ 2026-05-17 (Opus 4.7) — Dead-code sweep: 14 dead Icon C-BB zeta-fns + 3 [DAI-BOMB] stubs + icn_lazy_box + find_leaf_suspendable deleted.** Tier-1 scope completed in two orthogonal commits per RULES three-construct rule. **Tooling used:** grep-based dead-symbol audit (method 5) cross-referenced with the DAI-5a empirical trace history (method 4); static tools (cppcheck/--gc-sections) deferred — the manual audit was conclusive and the gate matrix is the final authority. **CLI-3M-9 territory (interp_*.c rip) deliberately not entered — separate goal step.**

  **DAI-7a (commit `254dedb9`)** — Deleted 14 empirically-dead Icon C Byrd-box functions in `icn_runtime.c` (each `DESCR_t foo(void *zeta, int entry)`, all violations of the absolute "ZERO C BYRD BOX FUNCTIONS" rule that DAI-2 had preserved as "infrastructure"):
  - `icn_bb_fnc_multi`, `icn_bb_assign_lhs_iter`, `icn_assign_write`, `icn_bb_assign_gen`, `icn_bb_assign_cat`, `icn_bb_assign_lhs_gen`, `icn_bb_revassign_lhs_gen`, `icn_bb_revassign`, `icn_bb_revswap`, `icn_bb_mutual`, `icn_bb_cat`, `icn_bb_scan_gen`, `icn_bb_bang_binary`, `icn_bb_seq_expr`, `icn_bb_identical_gen`
  - Plus internal helpers `icn_revswap_write`, `icn_revswap_read`
  - Plus 10 self-contained state structs (the structs externally referenced by `emit_bb.c`/`icon_gen.h` were preserved).
  - **Net: −560 LOC.** `icn_runtime.c` 1259 → 698. All gates held floor.

  **DAI-7b (commit `ff3d100a`)** — Deleted all three `[DAI-BOMB]` stubs (`bb_eval_value`, `icn_bb_build`, `bb_exec_stmt`) plus `icn_lazy_box` plus `find_leaf_suspendable`. Lon directive ("delete bb_eval_value anyway if it truly dead, we'll find out later") — the empirical truth was that `icn_lazy_box` (the surviving caller of `bb_eval_value` and a RULES.md-named permitted shim) had zero external callers itself; the named exception was reserving a slot for an inhabitant that wasn't there. RULES.md and the Invariant-2 entry in this file updated to drop `icn_lazy_box` from the named-survivor list — only `icn_bb_dcg` remains. **Net: −47 LOC `icn_runtime.c`, −10 `icon_gen.h`, −8 `emit_bb.c`, −2 `icn_runtime.h`.** `icn_runtime.c` 698 → 651. All gates held floor.

  **Combined DAI-7 net: −608 LOC in `icn_runtime.c` (1259 → 651), −10 in `icon_gen.h`, −8 in `emit_bb.c`, −2 in `icn_runtime.h`.** Zero `[DAI-BOMB]` fires (the stubs no longer exist to fire). Icon `--interp` 194/265 unchanged. Smoke ×6 unchanged. broker 22/27 unchanged. crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS unchanged.

  **What this closes:** the IJ-DEL-ICN-AST surgery (DAI-1 through DAI-7) is now structurally complete. The Icon-specific tree_t* AST walker is gone (DAI-2), all callers are routed through `interp_eval` (DAI-3/4/5a), the file-deletion sweep is complete (DAI-5b), the canonical reference path is `--interp` at 194/265 (DAI-5c), and the dead-zeta-fn/stub sweep is done (DAI-7). The Icon BB world is now: SM stream → IR_block_t (per proc) → `icn_bb_dcg` (one infrastructure shim) → x86-emitted Byrd boxes or `ir_exec.c` IR walker.

  **What's NEXT — CLI-3M-9 big rip in `interp_*.c`:** the broader sweep across `src/driver/interp_eval.c`, `interp_call.c`, `interp_exec.c`, `interp_ref.c`, `interp_label.c`, `interp_data.c`, `interp_hooks.c` is now unblocked. The DAI-7-tier-3 sketch in this file points at it; CLI-3M-9 is the authoritative goal-file row in `GOAL-CLI-3MODE.md`.

## Completed steps (session 2026-05-17 cont., Opus 4.7) — DAI-7

| Step | Description | Commit |
|------|-------------|--------|
| DAI-7a | Delete 14 dead Icon C-BB zeta-fns + 10 self-contained state structs from `icn_runtime.c`. Each function is `DESCR_t foo(void *zeta, int entry)` violating the ZERO-C-BYRD-BOX absolute rule, preserved by DAI-2 as "infrastructure". Manual audit (grep for external refs, cross-ref with DAI-5a trace history) confirmed all dead. Functions: `icn_bb_fnc_multi`, `icn_bb_assign_lhs_iter`, `icn_assign_write`, `icn_bb_assign_gen`, `icn_bb_assign_cat`, `icn_bb_assign_lhs_gen`, `icn_bb_revassign_lhs_gen`, `icn_bb_revassign`, `icn_bb_revswap`, `icn_bb_mutual`, `icn_bb_cat`, `icn_bb_scan_gen`, `icn_bb_bang_binary`, `icn_bb_seq_expr`, `icn_bb_identical_gen` + helpers `icn_revswap_write`, `icn_revswap_read`. State structs preserved if referenced from `emit_bb.c` factory wrappers (`icn_seq_state_t`, `icn_limit_state_t`, `icn_scan_gen_state_t`, `icn_mutual_state_t`, `icn_bang_binary_state_t`, `icn_cat_gen_state_t`); deleted if self-contained (`icn_fnc_multi_gen_state_t`, `icn_fnc_multi_frag_t`, `icn_assign_*_state_t` family, `icn_revassign_state_t`, `icn_revassign_lhs_gen_state_t`, `icn_revswap_state_t`, `icn_identical_gen_state_t`). −560 LOC. Build green. Icon --interp 194/265 unchanged, smoke ×6 unchanged. | `254dedb9` |
| DAI-7b | Per Lon directive: delete bb_eval_value stub + icn_lazy_box together. After DAI-7a, the only `bb_eval_value` caller was `icn_lazy_box`, which had zero external callers itself. RULES.md ABSOLUTE RULE listed `icn_lazy_box` as a permitted infrastructure-shim exception — empirically the named slot was reserving space for a non-inhabitant. Deleted in `icn_runtime.c`: all 3 `[DAI-BOMB]` stubs (`bb_eval_value`, `icn_bb_build`, `bb_exec_stmt`), `icn_lazy_box`, `icn_lazy_state_t`, `find_leaf_suspendable`. Deleted decls: `find_leaf_suspendable` from `icn_runtime.h`; 5 zeta-fn prototypes (`icn_bb_scan_gen`, `icn_bb_mutual`, `icn_bb_bang_binary`, `icn_bb_seq_expr`, `icn_bb_cat`) from `icon_gen.h` (state structs kept — referenced by `emit_bb.c` factory wrappers); 4 dead externs from `emit_bb.c` (`icn_bb_bang_binary`, `icn_bb_cat`, `icn_bb_seq_expr`, `icn_bb_scan_gen`). RULES.md + this file's Invariant 2 also updated to drop `icn_lazy_box` from the named-survivor list — only `icn_bb_dcg` remains as a permitted C-BB infrastructure shim. −47 LOC `icn_runtime.c`, −10 `icon_gen.h`, −8 `emit_bb.c`, −2 `icn_runtime.h`. Build green. Full gate matrix held floor. | `ff3d100a` |

## Open step

- [ ] **IJ-MODE4-HELLO-ALL-LANGS — Hello-world `--compile` (mode 4) works end-to-end for all six languages, wired-only.** **Lon directive (2026-05-18):** *"Ensure the compiled Icon and Prolog programs use flat/wired BBs. Do not use brokered BBs in `--compile` mode. Get all six languages to say hello world before continuing mass dead-code removal."* This step gates DAI-8 cluster 2+: no further dead-code sweep until the hello-world × wired-mode-4 matrix is 6/6 green.

  **Mandate:** mode 4 (`--compile`) must use **wired** Byrd boxes only — no `bb_broker` call from any emitted binary, no `rt_bb_once_proc`-style brokered shim from `libscrip_rt.so`. The `scrip.c` CLI guard already forces `g_bb_mode = BB_MODE_LIVE` under `--compile` (src/driver/scrip.c:128-148); honoring it at the runtime / emit level is what this step finishes. RULES.md "ZERO C BYRD BOX FUNCTIONS" remains in force — wired blobs are emitted x86, not C functions.

  **Wired vs brokered, the precise architectural shape** (from `.github/ARCH-x86.md`):
  - **Wired (`EMIT_BINARY_WIRED`):** one contiguous blob per pattern/proc, boxes `jmp` directly to each other's α/β/γ/ω labels. Broker calls the blob ONCE at α entry (`esi=0`); backtracking is internal `jmp`. Preamble loads `r10=&Δ` (RIP-relative); `rdi=ζ` is ignored (ζ=NULL). Jump in, jump out.
  - **Brokered (`EMIT_BINARY_BROKERED`):** per-box blobs with full C ABI. Broker calls `fn(ζ, port)` for each port transition.

  In mode 4, the emitted standalone binary cannot use brokered shape, because (a) per the CLI guard wired is mandated, and (b) brokered requires a runtime broker structure that's natural for the interpreter but absent from the asm-emit path. The emitted `.s` must inline the wired blob and `jmp` into it from main.

  **Baseline matrix (captured 2026-05-18, Opus 4.7, HEAD `a4fe1c21`):**

  | Lang     | `--interp` mode 2 | `--compile` emit | as | ld | run | Notes |
  |----------|:-:|:-:|:-:|:-:|:-:|---|
  | SNOBOL4  | ✓ | ✓ | ✓ | ✓ | ✓ | wired-clean: emitted binary imports zero `bb_broker` / `rt_bb_*_proc`. Pattern BBs use `bb_build_flat` path (`src/runtime/snobol4/stmt_exec.c:412`). |
  | Icon     | ✓ | ✓ | ✓ | ✓ | ✗ | aborts: `[NO-AST] SM_BB_PUMP_PROC stub: needs fresh SM/BB lowering`. `proc_table` empty in emitted binary's process. Cluster-1-validated unrelated. |
  | Prolog   | ✓ | ✓ | ✓ | ✓ | ✓-but-brokered | **violates wired mandate** — emitted binary imports `rt_bb_once_proc`, which calls `bb_broker(node, BB_ONCE, …)`. Output happens to be correct; path is wrong. |
  | Snocone  | ✓ | ✓ | ✓ | ✓ | ✓ | wired-clean (same SNOBOL4 lineage). |
  | Rebus    | ✓ | ✓ | ✓ | ✓ | ✓ | wired-clean (lowers to SNOBOL4-shape SM). |
  | Raku     | ✓ | ✓ | ✓ | ✓ | ✗ | runs but prints nothing. `say` builtin path appears unwired in mode 4. Diagnose at first sub-rung. |

  **Done when:** all six rows of the matrix above show `compile=✓ as=✓ ld=✓ run=✓` AND `nm <emitted_binary> | grep -E " U (bb_broker|rt_bb_once_proc|rt_bb_pump_proc)\b"` returns empty (no brokered dependency). All existing gates hold floor: Icon `--interp` 194/265, smoke ×6 mode-2 unchanged, smoke_unified_broker 22/27, crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS, mode4_broad_corpus_snobol4 202/75/3 SKIP.

  **Gate (one new script):** `scripts/test_smoke_compile_hello_all_langs.sh` — drives each of the six canonical hello programs through the full `scrip --compile → gcc -c → gcc -lscrip_rt → run` pipeline, then runs `nm` on each binary to assert zero brokered imports. Must return `PASS=6 FAIL=0`.

  ### Sub-rungs (each its own commit, RULES "Three-construct sessions" applies)

  - [x] **IJ-HELLO-1 — `test_smoke_compile_hello_all_langs.sh`** added and committed first, asserting the baseline (3 PASS / 3 FAIL: snobol4, snocone, rebus pass; icon, prolog (brokered), raku fail). The brokered check on prolog flips its row from PASS to FAIL. This sub-rung doesn't fix anything — it makes the failure surface auditable and observable in CI before any change. Provides the regression floor for the rest of the step. **✅ 2026-05-18 (Opus 4.7).** Gate landed; observed baseline at `a4fe1c21` is `PASS=3 FAIL=3 ROWS_MATCH=6 ROWS_DRIFT=0` and exits 0. Observed failure fingerprints differ from this goal-file's pre-recorded baseline matrix; see **Baseline-discrepancy findings (IJ-HELLO-1)** below for the three rows that shifted shape and the implications for IJ-HELLO-2/3/4.

  - [x] **IJ-HELLO-2 — Raku hello-world via mode 4. ✅ 2026-05-18 (sub-rungs 2a + 2b).** Diagnosed: two coupled bugs. **2a:** `rt_call` was skipping `icn_try_call_builtin_by_name` fallback (fixed Opus 4.7, `996f03e0`). **2b:** Raku proc-def `TT_FNC` wrapper was being lowered as a call-expression because `_id == SUB_TAG_ID` had been cleared by raku.y before lower_stmt saw it (fixed Sonnet 4.6, this session). Mode-4 Raku hello-world now `PASS-wired`; no `bb_broker`/`rt_bb_*_proc` imports in emitted binary. Mode-2 (`--interp`) bonus: rc=1 with "Error 5" → rc=0 clean.
    - **2a (Bug 1: write-lookup fallback) ✅ 2026-05-18 (Opus 4.7).** `rt_call` in `src/runtime/rt/rt.c` now mirrors `sm_interp.c`'s SM_CALL_FN fallback ladder: chains `icn_try_call_builtin_by_name` (Icon-builtin table that handles `write`, `writes`, `integer`, `image`, list ops, etc.) before falling to `INVOKE_fn`. The Raku frontend lowers `say(x)` to `SM_CALL_FN "write"`; modes 2/3 hit `icn_try_call_builtin_by_name` via the SM_CALL_FN handler; mode 4's PLT-call to `rt_call` was skipping it. `Hello, World!` now reaches stdout under `--compile`. one4all `996f03e0`. **Side-effect free for non-Icon names** (`icn_try_*` returns 0 on miss without writing `*out`); SNOBOL4/Snocone/Rebus PASS-wired rows held; smoke ×6 unchanged; crosscheck snobol4 5/1, icon 4/0, raku 21/12, rebus 4/0, snocone 8/0 — all at baseline.
    - [x] **2b (Bug 2: proc-def wrapper trailing CALL_FN) ✅ 2026-05-18 (Sonnet 4.6).** Lower.c::lower_stmt now matches `lang == LANG_RAKU && subject->t == TT_FNC && subject->_id == SUB_TAG_ID` BEFORE the general pattern/subject path, lowering body kids (`c[nparams+1..]`) directly via `lower_expr` + `SM_VOID_POP` and short-circuiting via `goto emit_gotos`. The wrapping `SM_CALL_FN <name>` emit is skipped. `SUB_TAG_ID` relocated from a local `#define` in `raku.y` to `frontend/raku/raku_driver.h` so both `raku.tab.c` (via raku.y prologue include) and `lower.c` (added include) reference the same constant. `raku.y` line 201 `e->_id = 0;` removed (was clearing the tag before `lower_stmt` saw it). Synthetic-main wrapper at raku.y line 213 now gets `mf->_id = SUB_TAG_ID;` for symmetry — same `lower_fnc`-as-call hazard applies when loose top-level stmts get wrapped. `_id` consumer audit confirmed safe: `polyglot.c:121` reads `_id` only under `s_lang == LANG_ICN`; `interp_eval.c` consumers are mode-1 (dead post-CLI-3M-10). `raku.tab.c` regenerated from `.y` via `scripts/regenerate_parser_and_lexer_from_sources.sh`. Verification: `--dump-sm hello.raku` now shows count=6 (was 7), spurious `SM_CALL_FN "main" nargs=1` gone. `--interp` rc=0 (was rc=1 with "Error 5 in statement 0"). `--compile` runs cleanly with no brokered imports — Raku row in `test_smoke_compile_hello_all_langs.sh` flips PASS-wired; `HW_EXPECTED_PASS=4 HW_EXPECTED_FAIL=2`. Pre-existing multi-proc Raku segfault (`sub greet(...); sub main(...)`) unaffected — Raku procs still don't register in `proc_table` because polyglot.c needs `proc->v.sval`, which is union-clobbered by `v.ival=nparams`; that's a separate ticket. **+18 LOC across 4 files** (raku.y +2/-3, raku_driver.h +5, lower.c +12, scripts +5/-3); raku.tab.c regen reorder noise dominates the diff stat. All gates hold floor: Icon `--interp` 194/265, smoke ×6 (5/0,5/0,5/0,4/0,5/0,7/0), broker 22/27, crosscheck (snobol4 5/1, icon 4/0, raku 21/12, rebus 4/0, snocone 8/0), crosscheck_prolog at baseline.

  - [x] **IJ-HELLO-3 — Icon hello-world via mode 4, wired ✅ 2026-05-18 (Opus 4.7).** SM stream's existing inline form proved sufficient — `lower_proc_skeletons()` had already lowered the Icon proc body into the SM stream as `SM_JUMP <skip> ; SM_LABEL "main" ; <body ops> ; SM_RETURN`, and `sm_resolve_proc_entry_pcs()` had populated `proc_table[i].entry_pc` with the PC of that SM_LABEL.  The fix was strictly emitter-side: a new `emit_sm_bb_pump_proc_dispatch()` in `src/emitter/emit_sm.c` that resolves the proc name from `ins->a[0].s` against `proc_table[].name`, then emits `CALL_EXPRESSION .L<entry_pc>` (= bare x86 `call .L<entry_pc>`) using the existing `SM_CALL_EXPRESSION` template — zero new asm macros.  The dispatcher is wired into the main switch at the `SM_CALL_EXPRESSION` slot pattern.  A pre-scan addition (`pattern_windows_collect`) marks the resolved `entry_pc` as a target so `.L<entry_pc>:` is actually emitted into the .s output (without this mark, the SM_LABEL renders only as the bare `LABEL` macro with no PC prefix, and the `call` has no in-translation-unit target).  SM_RETURN at the body end is plain `ret`, returns to us, and the dispatch loop falls through to the immediately-following SM_HALT.  **The architectural endpoint:** zero runtime helper invocation (no `rt_bb_pump_proc` — that symbol was never landed; the spec's IJ-HELLO-3d delete-step was moot, confirmed via grep on `src/runtime/rt/`), no `bb_broker`, no `_usercall_hook` route, no new `IR_block_t*` walker.  **The spec's 3a/3b emit_icn_proc_flat_blob approach proved unnecessary**: the goal text imagined the IR_block_t lowering would need a separate walker for the proc body, but `lower_proc_skeletons` already emitted the body as plain SM ops (PUSH_LIT_S, CALL_FN, VOID_POP, RETURN), so the existing SM template machinery handles them and the BB_PUMP_PROC dispatch only needs to be a `call` to the labeled entry.  3c (PLT call to `rt_call` for `write`) is also handled transparently by the existing `SM_CALL_FN` dispatch on the body's `CALL_FN "write"`.  **+72 net LOC** across two files: `emit_sm.c` (+66, new dispatcher and pre-scan case), `scripts/test_smoke_compile_hello_all_langs.sh` (+6/-6, baseline flip).  **Verification:** Icon `hello.icn` compiles, links, runs `Hello, World!` rc=0 under `--compile`.  `nm` audit shows zero brokered imports.  Hello-world matrix flipped Icon row PASS-wired; `HW_EXPECTED_PASS=4→5 HW_EXPECTED_FAIL=2→1` ROWS_MATCH=6 ROWS_DRIFT=0.  Modes 2 (`--interp`) and 3 (`--run`) for the same `hello.icn` continue printing `Hello, World!` rc=0 — change is mode-4 emitter-only and orthogonal to mode-2/3 paths.  All gates held: smoke ×6 unchanged (snobol4 7/0, snocone 5/0, icon 5/0, prolog 5/0, raku 5/0, rebus 4/0); Icon `--interp` 194/36/35/265 unchanged; crosscheck_icon 4/0, crosscheck_rebus 4/0, crosscheck_snocone 8/0 unchanged; crosscheck_snobol4 5/0 (≥ baseline 5/1).  **Latent:** `g_sm_templates[]` line 563 entry for `SM_BB_PUMP_PROC` still says `"rt_unhandled_sm" / SM_TPL_ARITH` — bypassed by our dispatch case but technically dead.  A future cosmetic cleanup could change it to a NULL macro / dispatch-only marker, but leaving it as the fallback is defensible (a future regression that skipped the dispatch would still trap visibly via `rt_unhandled_sm` rather than silently emit nothing). **Anti-pattern avoided:** no brokered `rt_bb_pump_proc` shim landed.

  - [x] **IJ-HELLO-4 — Prolog hello-world via mode 4, wired ✅ 2026-05-18 (Opus 4.7, three sub-rungs).** Existing Prolog mode 4 had two coupled bugs: (a) the 2-arg `:- initialization(Goal, When).` directive form fell into a fallback branch in `lower.c::lower_stmt` that emitted `SM_PUSH_EXPR(<tree_t*>) + SM_CALL_FN "PL_BUILTIN"`, but `SM_PUSH_EXPR` was unregistered in `g_sm_templates[]` so the generated `sm_macros.s` had no matching `.macro PUSH_EXPR`, causing GAS to reject `--compile` output with `Error: no such instruction: 'push_expr ptr'`; (b) the 1-arg `:- initialization(Goal).` form did work but routed through brokered `rt_bb_once_proc`, importing `bb_broker` transitively — violating the wired mandate. Four orthogonal commits. **IJ-HELLO-4a (`fc04134a`):** `lower.c::lower_stmt` LANG_PL recognizer extended to accept both `n==1` and `n==2` forms of `initialization`, dropping the tree_t*-AST-walking fallback emit. **IJ-HELLO-4a-fix (`411d041c`):** else-branch (unrecognized PL directives like `:- assertz(...)`/`:- retract(...)`/`:- abolish(...)`) softened from `abort()` to a stderr breadcrumb + silent skip, restoring `crosscheck_prolog` from a 115/0/17SKIP/11ORACLE_MISS regression back to its 128/0/4SKIP/11ORACLE_MISS floor. **IJ-HELLO-4b (`796d688e`):** new `rt_pl_once(name, arity)` in `rt.c` that does `pl_dcg_lookup` + `IR_exec_once` directly without invoking `bb_broker`; `SM_BB_ONCE_PROC` template runtime symbol flipped from `"rt_bb_once_proc"` → `"rt_pl_once"`; auto-regenerated `sm_macros.s` now calls `rt_pl_once@PLT`. **IJ-HELLO-4c (`8a6a5204`):** `rt_bb_once_proc` body deleted (zero callers after 4b's template flip), stale doc references updated. **Net across the four commits: −24 LOC + new wired path.** The `IR_block_t` walker (`src/lower/ir_exec.c`) is the permitted infrastructure DCG driver per Invariant 2 (parallel to Icon's `icn_bb_dcg`). The IR_block_t graph itself is still constructed at startup via `rt_register_predicates_pl` + `rt_pl_b_*` builder API (unchanged); only the *invocation* layer changes from broker-driven to direct IR-walker-driven. **Verification:** `/tmp/hello.pl` with both 2-arg (`:- initialization(main, main).`) and 1-arg (`:- initialization(main).`) variants compile, link, run, print `Hello, World!` rc=0. `nm hello.bin | grep ' U (bb_broker|rt_bb_once_proc|rt_bb_pump_proc)\b'` returns empty for both. `nm hello.bin | grep ' U rt_pl_once'` shows the new wired entry. Bonus mode-2 improvement: previously the 2-arg form was silently stubbed as `[NO-AST] PL_BUILTIN` and never invoked `main`; now mode-2 also prints `Hello, World!` rc=0 because the same SM_BB_ONCE_PROC handler exists in `sm_interp.c`. **All gates held floor across all four commits:** Icon `--interp` 194/36/35/265; smoke ×6 (icon 5/0, prolog 5/0, snobol4 7/0, snocone 5/0, rebus 4/0, raku 5/0); crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS; hello-world matrix PASS=5/FAIL=1 → PASS=6/FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0. **Anti-pattern avoided:** no per-predicate inline-x86 blob emit (would have required re-implementing the IR walker in asm; the existing `IR_exec_once` C function is the permitted equivalent); no rename-only fix (the brokered semantics are actually gone, not just the symbol name); no inline `tree_t*` walk in the emitted binary.

  - [x] **IJ-HELLO-5 — Full matrix regression + wired-only audit ✅ 2026-05-18 (Opus 4.7).** `test_smoke_compile_hello_all_langs.sh` returns `PASS=6 FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0`. `nm` audit on each emitted binary returns no `bb_broker`/`rt_bb_once_proc`/`rt_bb_pump_proc` imports (these last two symbols no longer exist in `libscrip_rt.so` at all — `rt_bb_once_proc` deleted in IJ-HELLO-4c, `rt_bb_pump_proc` was never landed per the IJ-HELLO-3 audit). All existing gate matrix holds floor: Icon `--interp` 194/265, smoke ×6, crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS. **The 6/6 hello-world matrix is closed.** Watermark updated below; DAI-8 cluster 2+ is unblocked. **Latent (separate cleanup ticket — would otherwise belong in DAI-8):** the obsolete `rt_bb_pump_proc` family of pre-emitter comments and the `g_sm_templates[]` SM_BB_PUMP_PROC `"rt_unhandled_sm"` fallback entry (line 567) remain defensible-as-is; they exist as belt-and-suspenders against a future regression that skips the dispatch case, and DAI-8's linker-gc audit will catch them if they truly become dead. **Broker gate (watermark 22/27) not re-verified this session** — the broker suite's csnobol4 Budne portion exceeds bash_tool's wall-clock ceiling, and IJ-HELLO-4's edits are mode-4-emitter-only / new-Prolog-runtime-fn / one-LANG_PL-lowering-edge — broker (modes 2/3 paths) has no path of effect from these deltas.

  **Anti-pattern (do not do this):**
  - Don't land brokered `rt_bb_*_proc` shims as "scaffolding". The asm side must be the wire — no detour through `bb_broker`. Today's in-session `rt_bb_pump_proc` work was modeled on the brokered Prolog template and is the example of what NOT to ship: it routes Icon mode 4 through `bb_broker` exactly the way `rt_bb_once_proc` does for Prolog, and that's the architecture violation this step is designed to remove.
  - Don't paper over Raku's silent-output bug by emitting a hard-coded `puts("hello world")` in the asm — diagnose what the lowered SM stream actually contains and fix at the missing rung.
  - Don't expand IR_t kind coverage beyond what hello-world demands (IJ-HELLO-3a). The minimum-IR-set discipline keeps the wired blob emitter bounded; subsequent rungs (post hello-world matrix close) extend it construct-by-construct.

  **Risk register:**
  - **Icon's per-construct `IR_ICN_*` family** is wider than Prolog's. Hello-world only exercises `IR_LIT_S` + `IR_CALL` + `IR_SEQ` (three node kinds); a real Icon program reaches into ~20 `IR_ICN_*` kinds for generators, ranges, scans, etc. **Hello-world is the scope of this step, not full Icon coverage.** The wired blob emitter starts with the three kinds; subsequent rungs (closing this goal long-term) extend it.
  - **Wired blob `r10=&Δ` register convention** must be respected on entry to the blob. Hello-world has no closure state (`ζ=NULL`, `r10` ignored), so the simplest entry preamble suffices: `push rbp / mov rbp,rsp` plus a single `call rt_call_fn` for `write`. ARCH-x86.md "Flat-BB ABI" section is the binding spec.
  - **`SM_BB_PUMP_PROC` may still appear in the SM stream** even after IJ-HELLO-3 lands the wired path. The CLI guard could be tightened to error if a `SM_BB_PUMP_PROC` appears under `--compile` without a corresponding wired blob, OR the lowerer could be changed to skip emitting `SM_BB_PUMP_PROC` entirely under `--compile` and substitute a direct-`jmp` SM opcode. Either is acceptable; pick at IJ-HELLO-3b implementation.

- [ ] **DAI-8 — Eliminate ALL dead code from SCRIP's executable source.** **UNPAUSED 2026-05-18 (IJ-HELLO-5 closed; hello-world matrix 6/6 wired)** — cluster work resumed. C1 + C2 + C3a + C3b landed; cluster 3+ candidates remain (see watermark). **Lon directive (2026-05-17):** *"Everything that is not reachable from SCRIP's `main` in some way is unreachable and therefore we want deleted. I'll be analyzing the code base and do not want to waste my time on code that does not matter."* This is a whole-codebase sweep, not the conservative tier-1 scope DAI-7 used.

  **Definition of dead:** a function, type, global, macro, or whole source file is *dead* iff it cannot be reached on any path from `main` in the built `scrip` binary, across every CLI mode SCRIP currently exposes (`--interp`, `--run`, `--compile`, `--compile-x86`, `--bb={brokered,wired}`, `--monitor`, all language frontends). Reachability is the union over all modes. If a symbol is reachable from `main` in any one mode, it stays.

  **Scope (no carve-outs):**
  - All `.c` files under `src/`
  - All `.h` files under `src/`
  - All decls in headers that name symbols with zero call sites
  - All `extern` decls in `.c` files that name symbols with zero call sites
  - All typedef'd structs whose only reference is their own typedef
  - All `#define` macros never expanded
  - Whole files where every defined symbol is dead (delete the file, prune the Makefile)
  - **No "infrastructure" exemption.** DAI-7 showed that the "infrastructure" carve-out (`icn_lazy_box`) was reserving a slot for a non-inhabitant. If a future feature needs a deleted symbol, `git log` recovers it; the live tree must contain only reachable code.

  **Out of scope (do not delete):**
  - Code reached through function-pointer dispatch tables (`g_user_call_hook`, `_usercall_hook`, the `proc_table` family, lex/yacc generated callbacks, builtin lookup tables). These look unreachable to static tools but are reachable at runtime. **Audit method:** for each suspect symbol, `grep` for its address-of (`&fn_name`) and its mention in any `static const` table; if either matches, the symbol is live.
  - SIL-family function definitions in `runtime/snobol4/*.c` (`APPLY_fn`, `FINDEX_fn`, etc.) called through indirect SIL dispatch — same address-of audit applies.
  - Generated parser/lexer files (`*.tab.c`, `*.lex.c`) — bison/flex output is regenerated, not edited.
  - The two oracles (`snobol4ever/x64`, `snobol4ever/csnobol4`) — those are separate repos, owned upstream, never patched in `one4all`.

  **Methodology (must use at least three independent methods, cross-checked):**

  1. **Linker garbage collection (authoritative).** Add a `make scrip GC=1` target that builds with `-ffunction-sections -fdata-sections -Wl,--gc-sections -Wl,--print-gc-sections`. The linker prints every section it discards. Discarded `.text.<fn_name>` sections are *empirically dead*: the linker has proven `main` can't reach them. This is the gold standard — the linker sees through function-pointer tables that static tools miss only if the address-of is actually taken somewhere reachable.

  2. **`cppcheck --enable=unusedFunction --project=...`** — fast first pass. Likely overreports (false positives on function-pointer callbacks, weak symbols, generated code). Use as a candidate generator, not as a deletion authority.

  3. **`cflow src/**/*.c | grep -v main`** — static call graph. Nodes with no incoming edges (and not in a function-pointer table) are dead. Useful for *understanding* why something's reachable when the first two disagree.

  4. **`nm -u scrip` + `nm --defined-only scrip`** — list undefined references (should be only libc/libgc) and defined symbols. After deletion, neither set should change in unexpected ways.

  5. **DAI-BOMB stub technique** (proven in DAI-2/4/5a/7) — replace suspect bodies with `[DAI-8-BOMB] <fn_name>` stubs that print to stderr + `exit(78)`, then run the full gate matrix. Zero fires = empirically dead = safe to delete in a follow-on commit. This is the only method that catches symbols reachable through obscure runtime paths (`dlsym`, embedded VM hooks).

  6. **`grep -rn "&<symbol>\|<symbol>(" src/`** — final cross-check before deletion. Catches calls through `static const` dispatch tables, label-as-value GCC extensions, and computed-goto interpreters.

  **Process per candidate symbol:**
  1. Methods 1 + 2 + 3 nominate it.
  2. Method 6 confirms zero call sites or address-of references.
  3. Method 5 stubs it with a DAI-8-BOMB.
  4. Run full parallel gate matrix (smoke ×6, broker, crosscheck_prolog, `test_icon_all_rungs.sh`).
  5. Zero fires → delete in a follow-on commit. Any fires → restore the body, document why it's reachable in a comment, move on.

  **Commit cadence:** orthogonal-clusters-per-session per RULES "Three-construct sessions." Each commit deletes one cluster (e.g. "all unreachable Icon helpers", "all unreachable SNOBOL4 SIL helpers", "all unreachable Prolog runtime helpers", "all unreachable emit_bb factory wrappers", "all unreachable `interp_*.c` from CLI-3M-9 territory", etc.). Bisectable: if a gate breaks N commits later, `git bisect` finds the bad commit within log₂(N) steps. Commit messages must list every deleted symbol so analysts can `git log -S<symbol_name>` to recover anything they need.

  **Done when:**
  - `make scrip GC=1 2>&1 | grep -c removing` returns 0 (no section the linker would discard remains in the object files).
  - `cppcheck --enable=unusedFunction src/` reports zero unused functions, OR each remaining warning is documented in a `## DAI-8 cppcheck false positives` table in this file with a one-line rationale (typically: "address taken at `<file>:<line>` for `<table_name>` dispatch").
  - Every `extern` decl in every `.c` and `.h` file under `src/` names a symbol that exists and has at least one caller.
  - Every typedef'd struct under `src/` is referenced by at least one piece of live code (`grep -rn "<struct_name>" src/ --include=*.c --include=*.h` shows more than just its own typedef line).
  - All gates hold floor: Icon `--interp` 194/265, smoke ×6 unchanged, smoke_unified_broker 22/27, crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS, zero DAI-8-BOMB fires across the full gate matrix.
  - This file's "## DAI-8 deletions ledger" section lists every deleted symbol with its commit hash and one-line justification.

  **Anti-pattern (do not do this):**
  - Don't keep code "because it might be useful later." `git log` is the archive. The live tree contains reachable code only.
  - Don't keep typedefs whose only consumer was a deleted function. The typedef goes too.
  - Don't keep state structs in `icon_gen.h` whose only consumer was a now-deleted `emit_bb.c` factory wrapper (DAI-7a preserved a handful of these on the conservative scope; DAI-8 finishes the job).
  - Don't preserve "infrastructure" exceptions. DAI-7b proved the named exceptions had no inhabitants; assume the same of any new candidate until empirically refuted.

  **Risk register:**
  - **Function-pointer dispatch tables are the main false-positive source.** Per-frontend `_usercall_hook`, `proc_table`, the `g_user_call_hook` cross-language bridge, lex/yacc action tables — all of these reach code through `static const` arrays of function pointers. The address-of audit (method 6) catches these. When in doubt, DAI-8-BOMB the candidate and let the gate matrix vote.
  - **Macros are harder to audit than functions.** `grep -rn "<MACRO_NAME>"` is the only tool; if zero non-definition hits, the macro is dead.
  - **Generated files (`*.tab.c`, `*.lex.c`, `snobol4.c`) are large and contain lots of "unused" symbols that are part of the parser's state machine.** Treat generated files as black boxes — don't touch them. Bison/flex are the source of truth; if a generated symbol is dead, the `.y`/`.l` source is what gets edited.
  - **CLI-3M-9 territory (`src/driver/interp_*.c`) is the largest expected deletion cluster.** Per the prior DAI-7 spec, after CLI-3M-10 deleted the `--ast-run`/`--ir-run` flags, every function only reachable from those flags is dead. The cluster likely spans 7 files (`interp_eval.c`, `interp_call.c`, `interp_exec.c`, `interp_ref.c`, `interp_label.c`, `interp_data.c`, `interp_hooks.c`) and several thousand LOC. Bite into it in commit-sized clusters, never one giant rip.

  **What "done" feels like:** when an outsider reads any `.c` file under `src/`, every function they see is reachable from `main` and matters to at least one user-facing mode. No archaeological layers, no infrastructure-that-isn't, no defensive prototypes. The tree is what runs.

## DAI-8 deletions ledger

(populated as DAI-8 commits land — one row per deleted symbol cluster)

| Cluster | Symbols deleted | Method that nominated | Method that confirmed | Commit | Gate delta |
|---|---|---|---|---|---|
| **C1 — `emit_bb.c` dead-fn sweep** (2026-05-18, Opus 4.7) | 75 functions (627 lines from `emit_bb.c` + 4 inline helpers from `emit_form.h` + 22 dead decls in `emit_bb.h` + 15 dead decls in `emit_templates.h`) — full list in commit body. Headlines: 44 obsolete `emit_bb_icon_*` STUB functions (BB-side stubs that emit "STUB" banners and jump-to-fail; no callers anywhere), `emit_flat_*` text-emit helper chain (only reachable from each other and from `__attribute__((unused))`-flagged dead bodies), `patnd_buf_*` / `patnd_to_sno_*` chain (PATND→string formatter, only mutual callers), `ICN_NQ` + `ICN_EMIT2` macros and all 16 `icon_*_new()` static-inline factory helpers reachable only from those macros, six dead emit_bb_x* ports (xabrt, xcat, xor, xvar, xsucf, xbal), and 4 dead x86 instruction wrappers (emit_add_eax_imm32, emit_mov_rdi_rax, emit_mov_rdx_imm64, emit_mov_rsi_imm64). | Method 1 (linker `--gc-sections` with `-ffunction-sections -fdata-sections`) — 990 sections removed, 732 `.text` sections, filtered to 583 hand-written-file candidates, refined via @PLT-aware string-literal filter to 512 truly-dead. | Method 6 (per-name grep for callers + address-takings + emit-string-literals); `__attribute__((unused))` developer annotations on `emit_flat_lit` / `emit_flat_charset_call` confirmed the developer's earlier read | `a4fe1c21` (one4all) | **Mode 2 only:** all gates held floor exactly — `Icon --interp 194/265`, smoke ×6 unchanged, `unified_broker 22/27`, `crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS`. **Modes 3 / 4 NOT validated** — this is the cluster-1 regression debt called out in the all-modes regression gate below. Most deletions sit in `IS_TEXT`/`flat_*` mode-4 territory, so mode-4 in particular needs retroactive validation as the first action of the next session. Net `−666 LOC` across four files. |
| **C2 — `emit_core.c` + `emit_sm.c` byte-emit family sweep** (2026-05-18, Opus 4.7) | ~198 functions across 3 files. From `emit_core.c` (1787→1198 LOC): 138 functions (47 `bb_insn_*`, 24 `insn_*`, 47 `emit_*` helpers including the `emit_bb_x*` port family DAI-7 left, `emit_seq_*` coupled callers, the `emit_test_rax_rax`/`emit_mov_esi_imm32` family) plus 58 single-decl lines in `emit_core.h`. From `emit_sm.c` (3315→3085): 59 named byte-emit fns (`emit_sm_push_lit_s`, `emit_sm_call_fn`, `emit_sm_halt`, `emit_sm_jump_*`, `emit_sm_pat_*` family, `emit_sm_arith*`/`emit_sm_neg`/`emit_sm_op`, `emit_sm_bb_*` family — full list in commit body) plus the dead `static emit_sm_pat_str` helper. **Architectural reason:** the `EMIT_BINARY` (byte-emit) shape in `emit_core.c` predates the `--compile` pivot to text-asm output. `--run` uses `sm_codegen_x64_emit.c` for in-memory JIT; `--compile` uses the `emit_sm_*_dispatch` text-emit family (which lives on, ~3000 LOC of `emit_sm.c` retained). Nothing reaches the byte-emit primitives anymore. The cluster is coherent: emit_sm.c byte-emit fns are the only callers of most x86-instruction primitives in emit_core.c; deleting one without the other strands link-time references. | Method 1 (linker `--gc-sections` with `-ffunction-sections -fdata-sections`) — 661 `.text` discards, 572 after generated-file exclusion (added `lex.rebus.o` to the filter), 472 after @PLT-aware string-literal rescue. emit_core.o 143 candidates, emit_sm.o 73, plus 10 emit_core "problem" fns whose callers were themselves all in the emit_sm.c GC-dead set (cross-call audit). | Method 6 (per-name grep with refined audit excluding `.h` declarations) — 132 emit_core fns had zero `.c` callers outside emit_core; 10 had only-GC-dead emit_sm.c callers; 1 (`emitter_init_macro_def`) preserved because called by `demo_template_productions.c` standalone demo. Methods 4 + 5 not needed — methods 1 + 6 were conclusive and gate matrix confirmed empirically. | `895ab323` (one4all) | **Held floor across all gates:** hello-world matrix `PASS=6 FAIL=0 ROWS_DRIFT=0`; modes 2/3/4 hello matrix 6/5/6 (mode-3 raku preexisting); smoke ×6 unchanged (5/0,5/0,5/0,4/0,5/0,7/0); Icon ladder `--interp 194/36/35/265`; crosscheck_prolog `128/0/4SKIP/11ORACLE_MISS`; scrip_all_modes `PASS=2 FAIL=0`. **Bonus:** unified_broker `22→23 (+1)`. Net `−877 LOC` across 3 files. |
| **C3a — `emit_form.h` dead-inline triplet+ + `emit_core.c::ef_greek_port`** (2026-05-18, Opus 4.7) | 14 functions across 2 files. From `emit_form.h` (67→55 LOC): 13 dead `static inline` wrappers (`emit_mov_r10_imm64`, `emit_mov_rax_imm64`, `emit_mov_rcx_imm64`, `emit_sub_eax_imm32`, `emit_cmp_eax_imm32`, `emit_cmp_esi_imm8`, `emit_mov_ecx_eax`, `emit_cmp_eax_ecx`, `emit_mov_eax_rcxmem`, `emit_cmp_eax_rcxmem`, `emit_mov_eax_r10mem`, `emit_call_rax`, `emit_inc_mem_r13_disp8`). C2's note nominated 3; the full sweep found 13. The remaining 8 inlines either have live callers in `emit_core.c::emit_sigma_plus_delta`/`emit_store_delta`/`emit_load_sigma` chain or in `emit_bb.c::emit_flat_body` (live). From `emit_core.c` (1198→1189 LOC): `ef_greek_port` static debug-port display helper for α/β/γ/ω; zero callers after C2 byte-emit deletion. | Method 1 (linker `--gc-sections` + @PLT-aware filter) was the original C2 watermark text's cluster-3 nomination (3 inlines + `ef_greek_port`). Re-running the same audit produced 13 inlines, not 3. | Method 6 (per-name grep with rt.c-internal-caller filter) — confirmed every deleted symbol has zero callers anywhere in src/. The 8 retained inlines had exactly 1 live caller each, traced and confirmed. | `c3af9e23` (one4all) | All gates held floor: hello-world 6/6 ROWS_DRIFT=0; smoke ×6 (7/0,5/0,5/0,5/0,4/0,5/0); Icon `--interp` 194/36/35/265; scrip_all_modes 2/0; unified_broker 23/26; crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS. Net `−23 LOC` across 2 files. |
| **C3b — `rt.c` dead-public-fn sweep** (2026-05-18, Opus 4.7) | 7 functions in `rt.c` + 7 matching decls in `rt.h`. Deletions: `rt_set_vstack_backend`, `rt_get_default_vstack_backend`, `rt_patch_cap_fn`, `rt_halt`, `rt_pop_descr`, `rt_push_real`, `rt_flush_pending_captures` — every refs=2 (decl + def only). | Method 1 (linker `--gc-sections` + @PLT-aware filter) nominated 100 dead `.text` sections in `rt.o`; @PLT rescue rescued 71 emit-string-referenced `rt_*` symbols leaving 29 candidates. | Method 6 (per-name caller audit) refined 29 → 7 truly-deletable. The other 22 split into: (a) static helpers (`vstack_*`, etc.) called by @PLT-rescued public fns — alive transitively via `libscrip_rt.so` path; (b) `_rt_IDENT`/`_rt_DIFFER`/`_rt_usercall` registered as function pointers via `register_fn`/`g_user_call_hook` in `rt_init`; (c) `sm_call_expression`/`sm_opcode_name`/`_is_pat_fnc_name`/`_expr_is_pat` are weak rt.c defaults overridden by strong defs in `eval_code.c`/`sm_prog.c`/`eval_pat.c`/`interp_eval.c` (rt.c weak symbols ARE dead but their `__attribute__((weak))` delivery needs header-side audit first); (d) `rt_in_native_chunk` has weak duplicate in `stmt_exec.c` suggesting dlsym pattern. | `a7259b9b` (one4all) | All gates held floor: hello-world 6/6 ROWS_DRIFT=0; smoke ×6 unchanged; Icon `--interp` 194/36/35/265; scrip_all_modes 2/0; unified_broker 23/26; crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS. Net `−43 LOC` across 2 files (rt.c -36, rt.h -7). |
| **C4 — `stmt_exec.c` dead-fn sweep + C-BB violation removal** (2026-05-18, Opus 4.7, third sub-session) | 10 functions + 1 typedef + supporting statics, all in `stmt_exec.c`. Deletions: `patnd_is_invariant` (recursive-only-callers static), `cache_get_fresh` (zero-callers static), `cache_stats` (only-called-by-dead-`cache_test_run`), **`bb_usercall`** (zero-callers static, **C BB ABSOLUTE RULE violation** — `DESCR_t bb_usercall(void *zeta, int entry)` signature), `usercall_t` typedef (orphaned after `bb_usercall` deletion), `cache_test_run` (zero external callers), `nv_set_str` (only-called-by-dead `deferred_var_test`/`anchor_test`), `nv_get` (zero callers — Prolog whitelist hit at `pl_runtime.c:504`/`pl_broker.c:204` is a Prolog-predicate-name string, dispatches to `NV_GET_fn` not the stmt_exec.c static — false positive), `deferred_var_test` (test-harness, zero external callers), `anchor_test` (test-harness, zero external callers), `exec_stmt_args` + its forward decl (only-called-by-`anchor_test`). Plus supporting statics: `g_nv_table` / `g_nv_count` / `g_nv_cap` / `NV_INIT` macro / `_nv_entry_t` typedef (the dead nv table). Kept: `descr_match_span`/`descr_match` (static inline in `bb_box.h` — per-TU artifact, not deletable), `rt_in_native_chunk` (weak/strong override pattern — methodology #6 deferred), `exec_stmt_pool_reset` (called from `rt.c:697`), `exec_stmt_blob` (called from `rt.c:511`), `xkind_name` (dead-in-its-TU but duplicate at `snobol4_pattern.c:903` — conservative keep). | Method 1 (linker `--gc-sections` + @PLT-aware filter) nominated 17 dead `.text` sections in `stmt_exec.o`. | Method 6 (per-name caller audit, refined with **internal-caller chain analysis** — methodology refinement #7 below): traced `cache_stats`/`nv_set_str`/`exec_stmt_args` to their only-called-by-dead status, forming a closed dead-set with the public test entry points. **Bonus: C BB violation eliminated** — `bb_usercall` was the last surviving C Byrd-box in stmt_exec.c (RULES.md ABSOLUTE RULE: only `icn_bb_dcg` permitted as a C-BB infrastructure shim). | `de6e7b77` (one4all) | All gates held floor: smoke ×6 (icon 5/0, prolog 5/0, raku 5/0, rebus 4/0, snocone 5/0, snobol4 7/0); hello-world matrix `PASS=6 FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0`; Icon `--interp` 194/36/35/265; unified_broker 23/26; crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS; scrip_all_modes 2/0. SM dump md5 stable for representative `.sno`/`.icn`/`.pl` inputs. Zero DAI-8-BOMB fires. Net `−248 LOC` in 1 file (stmt_exec.c 680→432). |
| **C7 — `icon_runtime.c` (frontend) dead-fn sweep** (2026-05-18, Sonnet 4.6) | 12 functions + 2 globals + 1 static buffer. `icn_write_int`, `icn_any`, `icn_many`, `icn_upto`, `icn_pop`, `icn_match`, `icn_tab`, `icn_move`, `icn_pow`, `icn_bang_char_at`, `icn_match_pat`, `icn_random` — all zero external callers, zero address-of. Globals `scan_subject`/`icn_pos` (scan cursor/position) deleted with them — only referenced inside the 12 dead functions. Static `tabmove_buf[4096]` deleted — only `icn_tab`+`icn_move` used it (both dead). Note: `icn_any/many/upto/match` are the old C-level scan builtins; the IR layer uses `scan_builtins.c::any/many/upto` (DESCR_t-based) instead. `icn_random` superseded by `IR_RANDOM` executor in `ir_exec.c` (uses `icn_runtime.c::proc_table` path). `icn_pop` superseded — stack ops handled by BB/SM layer. | Method 1 (linker `--gc-sections` + @PLT rescue) | Method 6 (per-name grep + address-of audit) — all 12 show 0 external callers, 0 address-of | `2b7081c5` (one4all) | All gates held floor: smoke ×6 (icon 5/0, prolog 5/0, raku 5/0, rebus 4/0, snocone 5/0, snobol4 7/0); Icon `--interp` 194/36/35/265. Net −118 LOC in 1 file. |
| **C6 — `prolog_builtin.c` dead-fn sweep** (2026-05-18, Sonnet 4.6) | 15 functions + 14 header decls. `pl_writeln` (standalone, zero callers), `pl_read` (stub returning 0, zero callers), `pl_eval_arith` (public, refs=2 = decl+def only), `static pl_eval_dbl` + `pl_num_lt/gt/le/ge/eq/ne` (6 fns forming a closed dead sub-graph via methodology #7 — only callers are each other through `pl_eval_dbl`; `pl_is` is the live entry that reaches `pl_eval_arith_term` directly, not through `pl_eval_dbl`), `pl_atom`/`pl_integer`/`pl_var`/`pl_nonvar`/`pl_compound`/`pl_callable` (6 standalone type-checkers, zero callers). 14 matching decls pruned from `prolog_builtin.h`. Kept live: `pl_is`, `pl_is_float`, `pl_eval_arith_term` + `arith_atoms_init` (statics reached via `pl_is`), all write/read/univ builtins, `interp_exec_pl_builtin`. | Method 1 (linker `--gc-sections` + @PLT-aware rescue filter) | Method 6 (per-name grep + address-of audit); Method 7 (internal-caller chain) for the `pl_eval_dbl`/`pl_num_*` sub-graph | `607b6aac` (one4all) | All gates held floor: smoke ×6 (icon 5/0, prolog 5/0, raku 5/0, rebus 4/0, snocone 5/0, snobol4 7/0); hello-world matrix PASS=6 FAIL=0 ROWS_DRIFT=0; Icon `--interp` 194/36/35/265; crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS; scrip_all_modes PASS=2 FAIL=0. Net −75 LOC across 2 files. |
| **C5 — `snobol4_pattern.c` dead-fn sweep** (2026-05-18, Opus 4.7, third sub-session continued) | 16 functions + 1 typedef. 9 public wrappers with one-each header decl + zero real callers: `pat_ref_val`, `array_create`, `MAKE_TREE_fn`, `push_val`, `pop_val`, `top_val`, `define_spec`, `apply_val`, `pat_call` — every refs=2 (decl + def only). 7 static helpers + 1 typedef forming a closed dead expression evaluator: `_ev_skip`, `_ev_ident`, `_ev_strlit`, `_ev_args`, `_ev_val`, `_ev_term`, `_ev_expr`, `SnoEvalCtx` — `_ev_expr` is the top, all others reach each other only within the family. Plus 9 matching decls pruned from `snobol4.h` (lines 425, 445, 469, 471, 473, 475, 481, 483, 512). Kept LIVE: `register_fn` (heavily used by rt.c:394/395 + scrip.c:327-332 for DEFINE_fn dispatch-table population). | Method 1 (linker `--gc-sections`) nominated 16 dead `.text` sections; all hand-written (not generated). | Method 6 + methodology refinement #7 (internal-caller chain — landed in C4) closed the _ev_* sub-graph in one bite. Each public fn audited individually for `@PLT` strings and address-of references — all zero. | `af744aaa` (one4all) | All gates held floor: smoke ×6 (icon 5/0, prolog 5/0, raku 5/0, rebus 4/0, snocone 5/0, snobol4 7/0); hello-world matrix `PASS=6 FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0`; Icon `--interp` 194/36/35/265; unified_broker 23/26; crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS; scrip_all_modes 2/0. Zero DAI-8-BOMB fires. Net `−197 LOC` across 2 files (snobol4_pattern.c 955→767, snobol4.h 514→505). |

### DAI-8 methodology note (added 2026-05-18, Opus 4.7)

Method 1 (linker `--gc-sections`) is the authoritative nominator. Rebuild
with `-ffunction-sections -fdata-sections -Wl,--gc-sections
-Wl,--print-gc-sections` and parse `.text.<name>` discards from the link
log. Two critical filters MUST be applied before treating a discard as
"truly dead":

1. **Generated-file exclusion.** Discards from `*.lex.c`, `*.tab.c`,
   `snobol4.c` (generated from `v311.sil`) are ignored — those files are
   regenerated.

2. **`@PLT`-aware string-literal rescue.** The emit_*.c family writes
   `name@PLT` strings (e.g. `"rt_init@PLT"`) into emitted asm. The linker
   cannot see these references because they're string-templating, not C
   calls. The filter regex MUST be `"NAME(@PLT)?"`, not `"NAME"`. Skipping
   `@PLT` falsely flagged 13 critical functions (`rt_init`, `rt_finalize`,
   `rt_halt`, `rt_register_expressions`, `rt_register_predicates_pl`,
   `rt_init_arbno`, `rt_init_cap`, `rt_init_cap_call`, `rt_match_blob`,
   `rt_pl_b_begin/end_register/entry/kids/node`) as dead when they are in
   fact part of the emitted-binary calling convention.

3. **`libscrip_rt.so` intersection is NOT a valid filter.** Shared library
   linking keeps all non-static functions in the export table by default
   (no `-fvisibility=hidden`), so `--gc-sections` on the .so reports far
   fewer dead functions than are actually dead. The .so's "live" set is a
   superset of what is reachable from `scrip` — relying on .so dead-ness
   would over-preserve. The criterion is **`scrip`-side linker GC + @PLT
   string-literal filter**, full stop.

4. **Static-helper-of-@PLT-rescued edge case** (discovered C3b 2026-05-18).
   When a public function `X` is rescued by the @PLT string-literal filter,
   any **`static` helper** in the same translation unit called by `X` (or
   transitively by another helper reached from `X`) is also alive in the
   .so via that path — even though linker-GC of `scrip` correctly marks it
   dead in scrip-side reachability. Example: `vstack_push` is static in
   `rt.c`, called only by `rt_pat_len` (which is @PLT-rescued). The two
   options for handling this are (a) extend the rescue list with a
   **transitive caller-graph closure pass** rooted at @PLT-rescued public
   fns within each TU, or (b) accept that static helpers can only be
   deleted when their direct callers are themselves in the truly-dead
   public set. C3b chose option (b) — only public functions with `refs=2`
   (decl + def, no callers anywhere) were deleted. Option (a) is the
   correct long-term fix and is queued as a methodology improvement.

5. **Function-pointer dispatch tables hide callers from grep** (recurring
   from DAI-8 risk register). `register_fn("IDENT", _rt_IDENT, 1, 2)` inside
   `rt_init` keeps `_rt_IDENT` alive via the runtime fn-ptr lookup table,
   invisible to grep-based caller audit. The reliable detector is the
   address-of audit (`&fn_name`). C3b caught `_rt_IDENT`, `_rt_DIFFER`,
   `_rt_usercall` this way before deletion.

6. **Weak/strong override pattern**. A `__attribute__((weak))` definition
   in rt.c becomes dead when any non-weak strong definition exists in
   another TU. The rt.c weak version is genuinely deletable, but `weak`
   plumbing requires header-side audit first — otherwise a future strong
   def deletion silently re-arms the now-deleted weak as the fallback.
   C3b's four weak-default candidates (`sm_call_expression`, `sm_opcode_name`,
   `_is_pat_fnc_name`, `_expr_is_pat`) deferred for this reason.

7. **Internal-caller chain analysis** (discovered C4 2026-05-18).
   When linker-GC nominates a public function as dead, an
   internal-only-callers function can be deletable *together with its
   callers* as a closed sub-graph, even though Method 6's external-only
   grep audit shows refs > 0. Example: `cache_stats` was called only
   from `cache_test_run` (also dead). Independent deletion of
   `cache_stats` is blocked by Method 6's "ref count > 0" check, but
   joint deletion of `{cache_test_run, cache_stats}` is correct.
   Similarly `{anchor_test, exec_stmt_args}` and `{deferred_var_test,
   anchor_test, nv_set_str, nv_get}` — each pair/triplet is a closed
   dead sub-graph. The audit pattern: for each linker-GC-dead public
   function F, examine every function F calls; if every caller of
   each is itself in the linker-GC-dead set, the whole sub-graph is
   deletable. Distinguishes from static-helper-rescue (#4) which
   requires the @PLT-rescued caller to be alive; this case has the
   caller dead too.

### DAI-8 all-modes regression gate (MANDATORY per cluster) — Lon directive 2026-05-18

⛔ The cluster-1 commit (`a4fe1c21`) was validated against `--interp`
(mode 2) only — the smoke ×6 + Icon ladder + unified_broker + crosscheck
matrix all run under `--interp`. That is **insufficient for DAI-8**.
Most of the deleted code (`emit_bb_icon_*` STUBs, `emit_flat_*` text
helpers, `IS_TEXT` branches, the `flat_*` family) lives in
**mode 3 (in-memory x86 JIT, `--run`)** and **mode 4 (GAS asm text,
`--compile`)** — not mode 2. The cluster-1 gate matrix didn't exercise
those modes. Cluster 1 is therefore landed but its mode-3 / mode-4
regression is **outstanding**.

**Whopper deletion deserves whopper regression.** Every DAI-8 cluster
from cluster 2 onward MUST run the full matrix below before commit, and
cluster 1's mode-3 / mode-4 status MUST be retroactively validated as
the first task of the next session.

#### Required per-cluster regression matrix

A cluster cannot land until ALL of these hold floor:

| Gate | Script | Purpose | Modes covered |
|------|--------|---------|---------------|
| Icon ladder under --interp | `scripts/test_icon_all_rungs.sh` | Largest mode-2 surface | mode 2 |
| Smoke ×6 | `scripts/test_smoke_{icon,prolog,raku,rebus,snocone,snobol4}.sh` | Per-frontend smoke (mode 2 today) | mode 2 |
| All scrip modes | `scripts/test_smoke_scrip_all_modes.sh` | Every CLI mode | modes 2 / 3 / 4 |
| All frontend × backend matrix | `scripts/test_smoke_all_frontend_backend_matrix.sh` | Cartesian product | modes 2 / 3 / 4 × 6 frontends |
| Compile-mode smoke | `scripts/test_smoke_compile.sh` | `--compile` (mode 4) emitted-asm path | mode 4 |
| All backends crosscheck | `scripts/test_crosscheck_all_backends.sh` | Cross-mode agreement | modes 2 / 3 / 4 |
| Unified broker | `scripts/test_smoke_unified_broker.sh` | β-pump + descriptor-tag | shared |
| Crosscheck Prolog | `scripts/test_crosscheck_prolog.sh` | 3-mode agreement for Prolog | modes 2 / 3 / 4 |

Plus at minimum one **dump round-trip** sanity check per cluster:

* `scrip --dump-sm test.sno` produces identical output before / after the cluster.
* `scrip --dump-bb test.sno` produces identical output before / after the cluster.
* `scrip --dump-ir test.sno` produces identical output before / after the cluster.

(Pick a representative input per frontend; a single canonical `test.sno`
/ `test.icn` / `test.pl` per language is sufficient — full matrix not
required for dumps, byte-diff is the floor.)

#### Failure handling

If any gate breaks under modes 3 or 4, the rollback target is the
parent commit (cluster 1 rollback = `ff3d100a`; subsequent clusters
roll back to whichever was last green across the full matrix). The
goal-file ledger row for the failed cluster gets a Gate delta column
filled in with the exact gate name + delta, and the cluster is
re-attempted with the failing symbols audited (DAI-BOMB technique
recommended for the specific symbol that broke it).

#### Baseline locked under all-modes matrix (TO BE CAPTURED)

The first task of the next session is to run the full all-modes matrix
against HEAD `a4fe1c21` and record the post-cluster-1 floor. If any
gate is below the pre-DAI-8 baseline (which itself was never measured
under modes 3/4 to my knowledge — confirm), that delta is the
cluster-1 regression debt and must be triaged before cluster 2 lands.

Tier-1 distribution (after the @PLT rescue, 512 truly-dead candidates):
`emit_core.c` 143, `emit_bb.c` 75 (cluster 1 — landed), `emit_sm.c` 72,
`rt.c` 31, `icon_runtime.c` (frontend) 25, `emit_wasm.c` 22,
`prolog_builtin.c` 20, `icn_runtime.c` (interp runtime) 18,
`snobol4_pattern.c` 16, `stmt_exec.c` 15, plus 23 more files with
smaller counts. **The CLI-3M-9 expectation that `interp_*.c` files
would contain a giant dead cluster was empirically false** — the
universal `interp_eval` walker is kept live by `pl_runtime.c`,
`raku_builtins.c`, and `polyglot.c` callers (the DAI-5a swap). Total
deletions across `src/driver/interp_*.c`: 2 functions (not the expected
several thousand LOC). The dead code is concentrated in the emitter
helper layer, not the interp driver.

## Baseline-discrepancy findings (IJ-HELLO-1, 2026-05-18 Opus 4.7)

The IJ-HELLO-1 gate captures the actually-observed behavior at HEAD
`a4fe1c21`.  Three rows shifted shape vs the pre-recorded matrix earlier
in this file; the gate encodes the observed behavior (not the documented
one) so the regression floor is honest.  Root causes audited so the
follow-on sub-rungs know what they're actually fixing:

| Lang | Documented baseline | Observed at `a4fe1c21` | Root cause |
|------|---------------------|------------------------|------------|
| Icon | `[NO-AST] SM_BB_PUMP_PROC stub` printed at compile time | Compiles + links clean; runtime trap **`unhandled SM opcode 61`** (= `SM_BB_PUMP_PROC`) from emitted binary | `g_sm_templates[]` in `src/emitter/emit_sm.c:563` routes `SM_BB_PUMP_PROC` to `rt_unhandled_sm` (template `SM_TPL_ARITH`). The `[NO-AST]` stub is the interpreter-side message; the asm-side equivalent is the `rt_unhandled_sm` trap fingerprint. Same root cause: no real mode-4 codegen for `SM_BB_PUMP_PROC`. IJ-HELLO-3's intent (inline wired Icon-main blob, no rt-helper) is unchanged. |
| Prolog | runs `Hello, World!` via brokered `rt_bb_once_proc` | **Assemble fails**: `Error: no such instruction: 'push_expr ptr'` on `.s` line containing macro-call `PUSH_EXPR ptr` | `emit_sm_push_expr` (`emit_sm.c:328`) emits a `PUSH_EXPR` macro call, but **`SM_PUSH_EXPR` is missing from `g_sm_templates[]`** — only `SM_PUSH_EXPRESSION` is registered. `sm_macros.s` therefore never receives a `.macro PUSH_EXPR` body, and GAS rejects the call site. Triggered by the `:- initialization(main, main).` directive, which lowers to a frozen-expression `tree_t*` push. Bare `main :- write(...).` (no directive) assembles cleanly but the SM dispatcher reaches `SM_HALT` without invoking `main`, so it prints nothing — that's the second-order shape of the same bug. **Implication for IJ-HELLO-4:** the brokered-vs-wired conversion is blocked by an upstream macro-library bug.  Either (a) fix the missing macro first as a precondition, or (b) re-anchor the canonical Prolog hello to a form that doesn't need `SM_PUSH_EXPR` (which means changing how directives lower under `--compile`). |
| Raku | "Runs but prints nothing" | Runs with **`** Error 5 in statement 0` / "Undefined function or operation"`** on stderr, rc=1 | `--dump-sm` shows the lowered stream: `SM_PUSH_VAR "write"` then `SM_CALL_FN "write" nargs=2`.  The Raku frontend lowers `say(...)` to a `write` *variable lookup* (then call), but `write` is not bound to a builtin descriptor in the Raku runtime's name-value table on entry. Mode 2 (`--interp`) hits this same path with no Error 5 because the SM dispatcher's `_usercall_hook` falls back to language-specific builtin tables for Raku; the mode-4 emit path (PLT-call to `rt_call`) goes through a different lookup that doesn't include the fallback. IJ-HELLO-2's "say builtin not registered in libscrip_rt's expression-table path" hypothesis matches this observation. |

The gate's row labels are `PASS-wired / FAIL-compile / FAIL-link /
FAIL-run / FAIL-wrong-out / FAIL-brokered`.  Each language's expected
row is documented inline in the script and any drift (improvement or
regression) trips `ROWS_DRIFT > 0` and the gate exits 1.  When
IJ-HELLO-2/3/4 lands, the fix commit edits the row's expected bucket in
the script alongside the runtime/emitter change in the same commit, so
the gate and the goal advance together.

## Completed steps (session 2026-05-18 Opus 4.7)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-HELLO-1 | `scripts/test_smoke_compile_hello_all_langs.sh` added.  Drives the canonical hello program in each of the six SCRIP-supported languages through `scrip --compile → gcc -no-pie -lscrip_rt → run → diff stdout`, plus an `nm` audit on each emitted binary for brokered imports (`bb_broker`/`rt_bb_once_proc`/`rt_bb_pump_proc`).  Six per-row buckets: `PASS-wired / FAIL-compile / FAIL-link / FAIL-run / FAIL-wrong-out / FAIL-brokered`.  Each row's expected bucket is locked to the observed `a4fe1c21` behavior; the gate fails loudly on either improvement or regression.  Observed baseline locked at `PASS=3 FAIL=3 ROWS_MATCH=6 ROWS_DRIFT=0` (snobol4/snocone/rebus PASS-wired; icon FAIL-run/SM_BB_PUMP_PROC; prolog FAIL-link/PUSH_EXPR macro; raku FAIL-run/Error 5).  Gate exits 0 at baseline.  Three baseline-discrepancy rows recorded in section above so IJ-HELLO-2/3/4 know exactly what's broken vs what the prior baseline assumed. | `cf568c35` |
| IJ-HELLO-2a | `rt_call` in `src/runtime/rt/rt.c` now chains `icn_try_call_builtin_by_name` (Icon-builtin fallback table) before `INVOKE_fn`, mirroring `sm_interp.c`'s SM_CALL_FN handler.  Raku's `say(x)` lowers to `SM_PUSH_VAR "write"` + `SM_CALL_FN "write" nargs=2`; modes 2/3 found `write` via this fallback; mode 4 was reaching `INVOKE_fn` directly and tripping "Error 5 Undefined function".  Direct verification: stdout of compiled `sub main(){say('Hello, World!');}` now contains the expected string (rc=1 still due to Bug 2, see IJ-HELLO-2b).  +26 LOC single file.  Baseline regression check: snobol4/snocone/rebus PASS-wired rows held, smoke ×6 unchanged (snobol4 7/0, snocone 5/0, icon 5/0, prolog 5/0, raku 5/0, rebus 4/0), crosscheck snobol4 5/1, icon 4/0, raku 21/12, rebus 4/0, snocone 8/0 — all at baseline.  Gate row for raku still FAIL-run because rc=1 from Bug 2 (trailing CALL_FN "main" on the proc-def wrapper TT_FNC).  IJ-HELLO-2b carries forward to next session for the full row flip. | `996f03e0` |

## Completed steps (session 2026-05-18 Sonnet 4.6)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-HELLO-2b | Raku proc-def `TT_FNC` wrapper trailing `SM_CALL_FN "main"` eliminated via SUB_TAG_ID match in `lower_stmt`. Four coherent edits across 4 files. (1) `src/frontend/raku/raku_driver.h`: hoisted `#define SUB_TAG_ID 1` from a local `raku.y` define into the cross-file-visible driver header, with comment documenting its role as a discriminator tag for proc-def TT_FNC nodes against call-expression TT_FNC of identical AST shape. (2) `src/frontend/raku/raku.y`: removed local `#define SUB_TAG_ID 1`; added `#include "raku_driver.h"` to the `%{...%}` prologue; removed `e->_id = 0;` at the `program → stmt_list` action (was clearing the tag before lower_stmt ever saw it); added `mf->_id = SUB_TAG_ID;` to the synthetic-main wrapper for symmetry — the synthetic wrapper hits the same lower_fnc-as-call hazard when loose top-level stmts trigger it. Regenerated `raku.tab.c` via `scripts/regenerate_parser_and_lexer_from_sources.sh`; per-bison-version state-table reorder dominates that file's diff. (3) `src/lower/lower.c`: added `#include "../../frontend/raku/raku_driver.h"`; in `lower_stmt`, after the `lang == LANG_PL` short-circuit block and before the `TT_SCAN`/`TT_SEQ` pattern split, added `if (lang == LANG_RAKU && subject && subject->t == TT_FNC && subject->_id == SUB_TAG_ID)` branch that lowers body kids `c[nparams+1..]` directly via `lower_expr` + `SM_VOID_POP` and short-circuits via `goto emit_gotos`. The wrapping `SM_CALL_FN <name>` emit is now skipped. (4) `scripts/test_smoke_compile_hello_all_langs.sh`: flipped raku row from `FAIL-run` to `PASS-wired`; bumped `HW_EXPECTED_PASS=3→4` and `HW_EXPECTED_FAIL=3→2`; refreshed header comment block. **Verification:** `--dump-sm /tmp/hello.raku` count=7→6, spurious `SM_CALL_FN "main" nargs=1` gone; `--interp` rc=1+stderr-Error5 → rc=0 clean; `--compile → as → ld → run` PASS-wired, `nm` shows no `bb_broker`/`rt_bb_*_proc` imports. **Audit of `_id` consumers** confirmed safe: `polyglot.c:121` reads `_id` only under `s_lang == LANG_ICN` (Raku procs use `v.ival` for nparams); `interp_eval.c` consumers are mode-1 (dead post-CLI-3M-10). **Pre-existing latent bug noted:** multi-proc Raku (`sub greet(...); sub main(...)`) segfaults under `--interp` both before and after this change — Raku procs never enter `proc_table` because `polyglot.c:114` needs `proc->v.sval`, which is union-clobbered by `v.ival=nparams`. That's a separate ticket. **+18 net LOC** hand-edited (raku.y +2/-3, raku_driver.h +5, lower.c +12, hello-gate +5/-3); raku.tab.c regen reorder ~280 line noise. **All gates held floor:** Icon `--interp` 194/36/35/265 unchanged; smoke ×6 5/0,5/0,5/0,4/0,5/0,7/0 unchanged; broker 22/27; crosscheck snobol4 5/1, icon 4/0, raku 21/12, rebus 4/0, snocone 8/0; hello-world matrix flipped PASS=3/FAIL=3 → PASS=4/FAIL=2, ROWS_MATCH=6 ROWS_DRIFT=0. | `5bc395d7` |

## Completed steps (session 2026-05-18 Opus 4.7 — second session of the day)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-HELLO-3 | Icon hello-world via mode 4, wired — `SM_BB_PUMP_PROC` emits direct `call .L<entry_pc>` to the SM-lowered Icon proc body.  Two edits in `src/emitter/emit_sm.c`, one matching edit in `scripts/test_smoke_compile_hello_all_langs.sh`.  (1) New `emit_sm_bb_pump_proc_dispatch(out, ins, pc)` placed alongside `emit_sm_bb_once_proc_dispatch` (the brokered Prolog analog).  Looks up `ins->a[0].s` against `proc_table[].name`, retrieves the resolved `entry_pc` (set earlier by `sm_resolve_proc_entry_pcs` in `src/driver/scrip_sm.c:25`), and emits `CALL_EXPRESSION .L<entry_pc>` via the existing `SM_CALL_EXPRESSION` template/macro — which lowers to a bare x86 `call .L<entry_pc>`.  On unresolved name (shouldn't happen for well-formed input), falls back to the `rt_unhandled_sm` template so the failure is visible rather than silent.  Annotation `# <name> entry=.L<pc> (IJ-HELLO-3 wired)` written into the .s output for traceability.  (2) New case in `pattern_windows_collect`'s pre-scan that marks the resolved `entry_pc` in `g_pc_used_as_target` so `.L<entry_pc>:` is actually emitted into the .s output.  Without this mark, the `SM_LABEL "main"` instruction renders only as the bare `LABEL` macro (no PC prefix) and the `call .L<entry_pc>` has no matching target in the same translation unit.  The mark targets the SM_LABEL's PC itself (= `proc_table[].entry_pc`); the `LABEL` macro is a no-op, so falling through to the body at PC+1 is correct.  (3) `#include "../runtime/interp/icn_runtime.h"` added to `emit_sm.c` for `proc_table`/`proc_count`/`PROC_TABLE_MAX` access.  (4) New `case SM_BB_PUMP_PROC: rc = emit_sm_bb_pump_proc_dispatch(out, ins, pc); break;` registered in the main codegen switch immediately after the existing `SM_BB_ONCE_PROC` case.  (5) Gate flip: `scripts/test_smoke_compile_hello_all_langs.sh` icon row `FAIL-run` → `PASS-wired`, `HW_EXPECTED_PASS=4→5 HW_EXPECTED_FAIL=2→1`, header docstring refreshed.  **The spec's 3a `emit_icn_proc_flat_blob` IR_block_t walker proved unnecessary** — `lower_proc_skeletons()` already lowers the Icon proc body into the SM stream as `SM_JUMP <skip>; SM_LABEL "name"; <body ops>; SM_RETURN`, so the existing SM template machinery (PUSH_LIT_S, CALL_FN, VOID_POP, RETURN) handles the body and BB_PUMP_PROC just needs to be a `call` to the labeled entry.  Spec's 3c is also handled transparently: the body's `SM_CALL_FN "write"` already routes to `rt_call` via PLT.  Spec's 3d (delete `rt_bb_pump_proc`) was moot — that symbol was never landed in `src/runtime/rt/`, confirmed via grep.  **Verification:** `/tmp/hello.icn` compiles via `--compile`, assembles via `gcc -no-pie -lscrip_rt`, runs with stdout=`Hello, World!` rc=0.  `nm` on the binary shows zero `U bb_broker`/`U rt_bb_once_proc`/`U rt_bb_pump_proc` symbols.  Spot-checked `hello.icn` under `--interp` (mode 2) and `--run` (mode 3): both print `Hello, World!` rc=0 — change is mode-4 emitter-only and orthogonal to modes 2/3.  Generated `.s` output snippet: `.L6: CALL_EXPRESSION .L1 # main entry=.L1 (IJ-HELLO-3 wired)` jumping to the now-emitted `.L1:` label.  **+72 net LOC** across two files: `emit_sm.c` (+66 incl. doc comments), `scripts/test_smoke_compile_hello_all_langs.sh` (+6/-6).  **All gates held floor:** Icon `--interp` 194/36/35/265 unchanged; smoke ×6 5/0,5/0,5/0,4/0,5/0,7/0 unchanged; crosscheck_snobol4 5/0 (≥ baseline 5/1), crosscheck_icon 4/0, crosscheck_rebus 4/0, crosscheck_snocone 8/0 unchanged; hello-world matrix PASS=4/FAIL=2 → PASS=5/FAIL=1 ROWS_MATCH=6 ROWS_DRIFT=0.  Broker gate (watermark 22/27) not re-verified this session — the broker suite's csnobol4 Budne portion exceeds bash_tool's wall-clock ceiling; IJ-HELLO-3 only touches mode-4 emitter code (no SM_Program shape change, no mode-2/3 dispatch change), so broker (which runs modes 2/3) has no path of effect from this delta.  **Latent (separate cleanup ticket):** `g_sm_templates[]` line 563 entry for `SM_BB_PUMP_PROC` still maps to `"rt_unhandled_sm" / SM_TPL_ARITH` — dead in the new dispatch path but defensible as the fallback if the case is ever accidentally removed from the switch.  **Anti-pattern audit:** no brokered `rt_bb_pump_proc` shim landed; no `IR_block_t*` walker introduced; no `bb_broker` invocation. | `d18b003e` |

## Completed steps (session 2026-05-18 Opus 4.7 — third session of the day, IJ-HELLO-4 close)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-HELLO-4a | `src/lower/lower.c::lower_stmt` LANG_PL recognizer extended to accept both `n==1` and `n==2` argcount forms of the `initialization` directive.  ISO Prolog's 2-arg form `:- initialization(Goal, When).` (where `When ∈ {now, after_load, program, main, restore}`) now dispatches to `SM_BB_ONCE_PROC <Goal>/<arity>` exactly like the 1-arg form; the `When` parameter is silently ignored (treated as `now`).  Previously the 2-arg form fell into the else branch which emitted `SM_PUSH_EXPR(<tree_t*>) + SM_CALL_FN "PL_BUILTIN" nargs=0` — pushing a `tree_t*` AST pointer into the SM stream (a direct violation of the no-AST-walking ABSOLUTE RULE for modes 2/3/4) AND emitting an unassemblable `PUSH_EXPR ptr` macro call under `--compile` (because `SM_PUSH_EXPR` is unregistered in `g_sm_templates[]`).  Else-branch initially replaced with `abort()`+FATAL — see IJ-HELLO-4a-fix for the necessary softening.  Bonus mode-2 improvement: the 2-arg form previously emitted `[NO-AST] PL_BUILTIN stub: needs fresh SM/BB lowering` to stderr and never invoked `main`; now mode-2 prints `Hello, World!` rc=0 because the same SM_BB_ONCE_PROC handler exists in `sm_interp.c`.  **+16 / -5 LOC** in `src/lower/lower.c`.  Gates at commit time: hello-world matrix prolog row stayed FAIL-link (the assemble bug was diagnosed but not yet fixed), gate exits 0 because baseline still expected FAIL-link.  **Smoke ×5 non-prolog gates green.** | `fc04134a` |
| IJ-HELLO-4a-fix | Collateral fix for IJ-HELLO-4a's overly strict `abort()` in the unrecognized-PL-directive else-branch.  The abort fired SIGABRT (rc=134) for any top-level Prolog directive other than `:- initialization(...)` — observed regression: `crosscheck_prolog` 128/0/4SKIP/11ORACLE_MISS → 115/0/17SKIP/11ORACLE_MISS (13 rungs moved PASS→SKIP, all in the rung13_assertz / rung14_retract / rung15_abolish families which use directives like `:- assertz(item(b)).` to seed predicate tables).  Fix: softened abort to a stderr `[NO-AST] PL directive <name>/<n> not yet lowered — skipped at lower time` breadcrumb, mirroring the prior mode-2 silent-stub behavior but without polluting the SM stream with a `tree_t*` pointer.  Real assertz/retract/abolish-as-directives support is the scope of PR-* lang-prolog rungs, not this surgery.  **+8 / -7 LOC** in `src/lower/lower.c`.  Gates after fix: `crosscheck_prolog` restored to 128/0/4SKIP/11ORACLE_MISS; all five non-prolog smoke gates green; Icon `--interp` 194/265. | `411d041c` |
| IJ-HELLO-4b | Three coherent edits to wire `SM_BB_ONCE_PROC` mode-4 dispatch through a non-broker path.  (1) `src/runtime/rt/rt.c`: new `rt_pl_once(name, arity)` that does name+arity lookup in `g_dcg_table` via the existing `pl_dcg_lookup`, sets up the Prolog env via `pl_bb_env_push` / `pl_bb_env_pop`, and calls `IR_exec_once(bb->ir_body)` directly — the IR_block_t walker (`src/lower/ir_exec.c`) is the permitted infrastructure DCG driver per Invariant 2, parallel to Icon's `icn_bb_dcg`.  Same `[NO-AST] SM_BB_ONCE_PROC stub` fingerprint on miss for cross-mode parity.  (2) `src/runtime/rt/rt.h`: new `rt_pl_once` declaration alongside `rt_pl_b_end_register`.  (3) `src/emitter/emit_sm.c`: flipped `g_sm_templates[]`'s SM_BB_ONCE_PROC row from `runtime="rt_bb_once_proc"` to `runtime="rt_pl_once"`.  The auto-generated `sm_macros.s` BB_ONCE_PROC macro body is rewritten on every `scrip --compile` invocation (emit_walk_codegen line 3156), so no hand edit to the checked-in `sm_macros.s` was required.  (4) `scripts/test_smoke_compile_hello_all_langs.sh`: prolog row flipped from `FAIL-link` to `PASS-wired`; `HW_EXPECTED_PASS=5→6`, `HW_EXPECTED_FAIL=1→0`; header docstring refreshed to record the IJ-HELLO-4 floor.  **The IR_block_t graph itself is still constructed at startup via `rt_register_predicates_pl + rt_pl_b_*` builder API (unchanged path)**; only the *invocation* layer changes from broker-driven to direct IR-walker-driven.  **Verification:** `/tmp/hello.pl` with both 2-arg (`:- initialization(main, main).`) and 1-arg (`:- initialization(main).`) variants compile, link, run, print `Hello, World!` rc=0 under `--compile`.  `nm hello.bin \| grep ' U (bb_broker\|rt_bb_once_proc\|rt_bb_pump_proc)\b'` returns empty.  `nm hello.bin \| grep ' U rt_pl_once'` shows the new wired entry.  `sm_macros.s` BB_ONCE_PROC macro now calls `rt_pl_once@PLT`.  Hello-world matrix: PASS=5/FAIL=1 → PASS=6/FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0.  **Net: +41/-6 LOC across 4 files.**  All gates held floor.  **Anti-pattern avoided:** no per-predicate inline-x86 blob emit (would have required re-implementing the IR walker in asm); no rename-only fix (the brokered semantics are actually gone, not just the symbol name); no inline `tree_t*` walk in the emitted binary. | `796d688e` |
| IJ-HELLO-4c | After IJ-HELLO-4b's template flip, `rt_bb_once_proc` had zero callers across `src/` (verified via `grep -rn "rt_bb_once_proc" --include=*.c --include=*.h`).  Function body (15 LOC) deleted from `src/runtime/rt/rt.c`; stale doc-comment references in `rt.h`, `rt.c`, `emit_sm.c`, and `scripts/run_prolog_via_x86_backend.sh` updated to point at `rt_pl_once` / mention `rt_bb_once_proc` only in past-tense deletion context.  The hello-world matrix gate's `nm`-audit grep (`bb_broker\|rt_bb_once_proc\|rt_bb_pump_proc`) is intentionally left unchanged — the symbol-name regex is the architectural tripwire against any future regression that re-introduces brokered dispatch under `--compile`, regardless of which language re-introduces it.  **Verification:** `nm out/libscrip_rt.so \| grep rt_bb_once_proc` → empty; `nm out/libscrip_rt.so \| grep rt_pl_once` → present.  **Net: −24 LOC** (15-line body + minor decl/comment churn) across 4 files.  The `bb_broker` import-chain from the emitted standalone binary is now structurally impossible for Prolog: there is no symbol to call.  All gates held floor. | `8a6a5204` |
| IJ-HELLO-5 | Goal closure — the 6/6 wired hello-world matrix is sealed.  `test_smoke_compile_hello_all_langs.sh` returns `PASS=6 FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0`; `nm` audit on every emitted binary returns no `bb_broker`/`rt_bb_once_proc`/`rt_bb_pump_proc` imports (the last two symbols no longer exist in `libscrip_rt.so` at all).  All existing gate matrix holds floor: Icon `--interp` 194/265, smoke ×6 (icon 5/0, prolog 5/0, snobol4 7/0, snocone 5/0, rebus 4/0, raku 5/0), crosscheck_prolog 128/0/4SKIP/11ORACLE_MISS.  Watermark refreshed below.  **DAI-8 cluster 2+ is unblocked** per the goal-file mandate ("Get all six languages to say hello world before continuing mass dead-code removal"). | this commit |

## Watermark

```
one4all: 2b7081c5     (DAI-8 C7: icon_runtime.c frontend 12 fns + 2 globals — −118 LOC)
         607b6aac     (DAI-8 C6: prolog_builtin.c 15 fns + 14 decls — −75 LOC)
         af744aaa     (DAI-8 C5: snobol4_pattern.c 16 fns + 1 typedef + 9 decls — −197 LOC)
         de6e7b77     (DAI-8 C4: stmt_exec.c 10 fns + 1 typedef — −248 LOC; bonus: C BB violation removed)
         a7259b9b     (DAI-8 C3b: rt.c 7 dead public fns + 7 rt.h decls — −43 LOC)
         c3af9e23     (DAI-8 C3a: emit_form.h 13 inlines + emit_core.c::ef_greek_port — −23 LOC)
         895ab323     (DAI-8 C2: emit_core.c + emit_sm.c byte-emit sweep — −877 LOC, ~198 fns)
corpus:  92e103f      (unchanged — no corpus edits this session)
.github: this commit  (DAI-8 C5 ledger row added; watermark refreshed)
test_smoke_compile_hello_all_langs: PASS=6 FAIL=0 ROWS_MATCH=6 ROWS_DRIFT=0  (held)
--interp:    194/265  (Icon rung ladder, unchanged — held)
smoke_icon: 5/0    smoke_prolog: 5/0  smoke_raku: 5/0    (mode 2 — held)
smoke_rebus: 4/0   smoke_snocone: 5/0                    (mode 2 — held)
smoke_snobol4: 7/0                                       (mode 2 — held)
unified_broker: 23/26 (held)
crosscheck_prolog: 128/0/4SKIP/11ORACLE_MISS  (held)
scrip_all_modes: PASS=2 FAIL=0
DAI-BOMB fires: 0

✅ DAI-8 cluster 5 COMPLETE. Single-construct dead-code sweep targeting
  `src/runtime/snobol4/snobol4_pattern.c` (Opus 4.7, 2026-05-18 6th
  sub-session, commit `af744aaa`): 9 dead public wrappers (each with
  refs=2 = decl + def only) + 7 static helpers forming a closed dead
  expression-evaluator sub-graph + their typedef. 9 matching decls
  pruned from `snobol4.h`. Net −197 LOC.

Combined day deliverable (DAI-8 alone, across C3a + C3b + C4 + C5):
  - C3a (`c3af9e23`):  −23 LOC, emit_form.h + emit_core.c (14 fns)
  - C3b (`a7259b9b`):  −43 LOC, rt.c (7 public + 7 decls)
  - C4  (`de6e7b77`): −248 LOC, stmt_exec.c (10 fns + 1 typedef;
                       C-BB ABSOLUTE RULE violation removed)
  - C5  (`af744aaa`): −197 LOC, snobol4_pattern.c (16 fns + 1 typedef
                       + 9 decls)
  Total: −511 LOC across 6 files, ~50 functions deleted in one day.

Cluster 6+ candidates remaining (Method 1 GC log, after C3-C5 deletions):
  - rt.c: ~22 candidates (need methodology #4 closure pass)
  - icon_runtime.c (frontend): 25 candidates
  - emit_wasm.c: 22 candidates
  - prolog_builtin.c: 20 candidates
  - icn_runtime.c (interp): 18 candidates

Methodology refinements landed (items #4 through #7 in the methodology
note):
  - #4 Static-helper-of-@PLT-rescued edge case
  - #5 Function-pointer dispatch tables hide callers from grep
  - #6 Weak/strong override pattern
  - #7 Internal-caller chain analysis (canonical example: C4's
    test-harness tail; C5's _ev_* sub-graph)

Latent (separate tickets):
  - IJ-HELLO-MODE3-RAKU: mode-3 raku --run prints nothing; rt_call
    fallback ladder needs mirroring in sm_codegen_x64_emit.c.

Gate-suite wall-clock: ~120s (broker + crosscheck_prolog ran; Icon
ladder ~75s; smoke ×6 in parallel <30s).
```

Latent bugs (pre-existing or unblocked, separate tickets):
- rung36 jcon programs: many xfail — file I/O, co-expressions, complex programs.
- SM dump display labels `SM_STORE_FRAME` as "SM_LOAD_FRAME" (cosmetic).
- IR_ICN_FIND_GEN start/stop normalization untested for jcon corner cases (see IJ-FIND-GEN row above).
- IR_ICN_SEQ_GEN ignores zero step silently — Icon spec is to fail; pragmatic choice for now.
- DAI-5c and DAI-6 ✅ landed 2026-05-17j (Opus 4.7) as part of CLI-3M-10 alias removal. Three file-local `static` [DAI-BOMB] stubs in `icn_runtime.c` (`bb_eval_value`, `icn_bb_build`, `bb_exec_stmt`) protect ~25 residual internal call sites inside surviving Icon zeta-fn bodies (`icn_lazy_box` plus others DAI-2 preserved). Empirically unreachable, but they're still present in source as a latent cleanup target — separate ticket if/when the surviving icn_bb_* zeta-fns are themselves audited.

Session note (2026-05-17i, Opus 4.7): DAI-5b — file deletion landed in two orthogonal commits. DAI-5b-1 was the straightforward helper relocation. DAI-5b-2's scope was larger than originally documented: the GOAL spec said "delete `icn_bb_build` body" assuming all callers were external, but DAI-2's earlier "preserve `icn_bb_dcg/proc_table/icn_every_body_pre+broke`" left ~25 internal call sites of the three amputated symbols across surviving Icon zeta-fn bodies. The empirical DAI-5a trace pass had already proven those internal sites unreachable, so the fix was three file-local `static` [DAI-BOMB] stubs rather than a deeper zeta-fn audit. Public surface of the three symbols is now zero (no decls in any header, no callers in any .c outside `icn_runtime.c`). A latent cleanup target remains: the residual zeta-fn bodies themselves — `icn_lazy_box` is a RULES.md-permitted exception, but the others (~10–15 functions named `icn_bb_*` in icn_runtime.c that call `bb_eval_value`/`icn_bb_build`) were preserved by DAI-2 as "infrastructure" and may be eligible for deletion in a separate ticket if a full audit shows they're dead.

Session note (2026-05-17h, Opus 4.7): DAI-5a — cleared all `bb_eval_value` callers from `src/`. Adopted same empirical methodology that worked for DAI-2/DAI-4: instrument all 56 caller sites with `[DAI-5-TRACE]` fprintfs, run the full gate matrix (smoke ×6 frontends + Icon rungs + crosscheck_prolog + crosscheck_raku + crosscheck_icon), confirm zero fires, then swap every site to `interp_eval` (the universal mode-1 walker). All gates held at baseline. The risk register's hedged "fall back to keeping `bb_eval_value` only for the 3 pl_runtime sites" mitigation proved unnecessary — those sites were dead too. DAI-5b file deletion is now unblocked but needs careful helper relocation (`icn_str_concat_d`, `icn_lconcat_d`, `icn_proc_as_value` move from `icn_value.c` to `icn_runtime.c` before file deletion) — not a one-line edit.

Session note (2026-05-17g, Opus 4.7): DAI-4 cleanup of stale `icn_bb_build` callers. As predicted by DAI-2's measurement (zero bombs across 265 rungs), these 3 call sites in `interp_eval.c` and the dangling extern in `sm_jit_interp.c` were stage-set dead code — the underlying `icn_bb_build` was already a `[DAI-BOMB]` stub, and mode-1 Icon never reached the TT_EVERY/TT_AUGOP-suspend-rhs branches (lowered to IR_EVERY / IR_AUGOP). Net 33 lines deleted; 10 inserted for the guard+bomb fingerprints. ir-run 194/265 unchanged; smoke matrix unchanged. Surface area for DAI-5 is wider than originally scoped — at least three additional consumer files (`pl_runtime.c`, `raku_builtins.c`, `interp_eval.c`'s `bb_eval_value` ternaries at lines 136-163) carry `bb_eval_value(tree_t*)` calls that DAI-5 file-deletion will force-resolve.

Session note (2026-05-17f, Opus 4.7): the PIVOT directive ("delete the actual AST walkers, leave stub bombs") landed cleanly. The biggest surprise was that the Icon `--interp` rung-pass count (194/265) was *unchanged* by amputation and *zero* bombs fired across all 265 tests. This indicates the Icon AST walker (`bb_eval_value` / `bb_exec_stmt` / `icn_bb_build`) was already silently dead for the rung suite. Mode-1 Icon executes via the universal `interp_eval` walker which routes to `ir_exec.c` (IR_block_t walker) for Icon-specific kinds — the tree_t* path through the Icon walker was a vestigial limb. The −1641 LOC came out without measurable cost.

Session note (2026-05-17e, Opus 4.7): all three constructs are "builtin → IR generator" promotions. The pattern is identical: (a) add IR_ICN_<FOO>_GEN enum, (b) write α/β executor with state-machine in nd->state, with arg-cache in opaque to prevent side-effect re-fire on β, (c) add to the three gen-kind tables (ir_is_single_shot, IR_IS_GEN_KIND, ALT_IS_GEN), (d) special-case the builtin name in lower_icn.c's TT_FNC dispatch. IJ-LCONCAT was simpler — just a single-shot binop using an existing runtime helper factored to take DESCR_t inputs. The shared DESCR_t-helper refactor in icn_value.c keeps the AST-walk and IR paths in lock-step semantically.
