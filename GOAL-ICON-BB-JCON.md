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

(none — DAI-7 closed the IJ-DEL-ICN-AST arc. Next active row for this goal will be opened as new Icon work, or referred out to `GOAL-CLI-3MODE.md` CLI-3M-9 for the `interp_*.c` big rip.)

## Watermark

```
one4all: ff3d100a (DAI-7b: stubs + icn_lazy_box + find_leaf_suspendable deleted)
corpus:  92e103f  (unchanged — no corpus edits this session)
.github: this commit (DAI-7 done; RULES.md Invariant 2 + GOAL Invariant 2 updated)
--interp:    194/265   (Icon rung ladder, unchanged from DAI-5c floor)
smoke_icon: 5/0    smoke_prolog: 5/0  smoke_raku: 5/0
smoke_rebus: 4/0   smoke_snocone: 5/0
smoke_snobol4: 7/0
smoke_unified_broker: 22/27
crosscheck_prolog: 128/0/4SKIP/11ORACLE_MISS (unchanged)
DAI-BOMB fires: 0 (the stubs no longer exist)
Gate-suite wall-clock: ~90s parallel.
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
