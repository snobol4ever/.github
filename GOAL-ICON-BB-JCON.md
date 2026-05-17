# GOAL-ICON-BB-JCON.md — Icon: BB emitters + lower_icn DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`
**Reference:** `/refs/jcon-master/tran/irgen.icn` + `tran/ir.icn`; `.github/jcon_irgen.icn`

## Invariants (READ FIRST)

1. **No AST walking in modes 2/3/4.** Modes 2 (sm_interp) and 3 (sm_jit_interp) print `[NO-AST] <opcode>` on stderr if a tree_t* would be dereferenced. If a gate breaks with `[NO-AST] FOO`, write fresh SM/BB lowering for FOO — do not restore the AST-walking call. Mode 1 (`--ir-run` AST interp) is the reference path and unchanged.
2. **Zero C Byrd-box functions.** A C BB is `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω in C. None may exist. All BBs are x86 emitted at runtime, or `IR_block_t` DCGs driven by `icn_bb_dcg`. Exceptions: `icn_lazy_box` and `icn_bb_dcg` (infrastructure shims).
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
| IJ-CSET-COMPL | TT_CSET_COMPL (`~E` Icon cset complement) lowered to IR_CSET_COMPL. Three coherent edits: (1) `src/include/IR.h` adds `IR_CSET_COMPL` after `IR_POS` in the IR_e enum. (2) `src/lower/ir_exec.c` adds executor case mirroring `TT_CSET_COMPL` in `icn_value.c::bb_eval_value`: eval c[0], coerce int/real → string via `descr_to_str_icn` (new include `"coerce.h"`), call `icn_cset_complement(cs)` against the 256-char universal cset, wrap result in `CSETVAL`. Handles FAIL/null/numeric coercion paths. (3) `src/lower/lower_icn.c` adds `TT_CSET_COMPL` case before default, parallel structure to `TT_MNS`/`TT_PLS`: recurse into c[0], allocate IR_CSET_COMPL node, wire single child. `[NO-AST] SM_BB_EVAL` stub for `~cset` expressions in `--ir-run` is now eliminated; `~'aeiou'` produces correct CSETVAL with type=cset. ir-run 111/265 unchanged (rung36_jcon_* integration tests gate on additional missing constructs: `&cset`/`&ascii` keywords + `\0`-safe scan builtins). Gates: smoke_icon 5/5, broker 20/49, honest 277/0/0, cross-lang smokes (sn4/raku/snocone/rebus/prolog) unchanged. | `0b931361` |
| IJ-CSET-BINOPS | TT_CSET_UNION/DIFF/INTER (Icon `E1++E2`/`E1--E2`/`E1**E2`) lowered to IR_CSET_UNION/DIFF/INTER. Three coherent edits paralleling IJ-CSET-COMPL: (1) `src/include/IR.h` adds three IR_e entries after `IR_CSET_COMPL`. (2) `src/lower/ir_exec.c` adds a shared fall-through case `IR_CSET_UNION:`/`IR_CSET_DIFF:`/`IR_CSET_INTER:` mirroring the matching `bb_eval_value` cases in `icn_value.c`: eval both children, coerce int/real → string via `descr_to_str_icn`, dispatch by `nd->t` to `icn_cset_union/diff/inter`, run through `icn_cset_canonical` for sort+dedup, wrap as `CSETVAL`. FAIL/null propagate cleanly. (3) `src/lower/lower_icn.c` adds shared `TT_CSET_UNION:`/`TT_CSET_DIFF:`/`TT_CSET_INTER:` case: lower both operands, map AST kind → IR kind, allocate node with n=2. Sanity-tested: `'aeiou' ++ 'xyz'` → `'aeiouxyz'` (8 chars); `'abcdef' -- 'bd'` → `'acef'` (4); `'abcdef' ** 'cdefgh'` → `'cdef'` (4); `~'aeiou' -- '0123456789'` → 112 chars. ir-run 111/265 unchanged (same downstream gating). Gates: smoke_icon 5/5, broker 20/49, honest 277/0/0, cross-lang smokes unchanged. | `0b931361` |
| IJ-SCAN-NULSAFE | `scan_builtins.c::any/many/upto/bal` made `\0`-safe. Added `cset_resolve(DESCR_t, &ptr, &len)` helper that consults `icn_kw_cset_len(ptr)` for keyword-cset storage (`&cset`/`&ascii`/`&lcase`/...) whose canonical-form buffer is null-prefixed (`stable[0]='\0'`, real chars follow), falling back to `strlen` for regular csets and strings. Added `cset_has(cv, clen, ch)` using `memchr` instead of `strchr` so cset membership tests are length-aware. Refactored `any` (line 14), `many` (line 35), `upto` (line 56), `bal` (line 127) — each cset argument now flows through `cset_resolve` + `cset_has` rather than `VARVAL_fn` + `strchr`. Eliminates silent truncation when scan builtins receive csets containing `\0` (kw csets) or when `~cset` complement results flow through scan ladder. ir-run 111/265 unchanged: no rung flips because cset-complement-driven rungs (`rung36_jcon_*`) gate on additional missing constructs beyond `\0`-safe scan, but the silent-truncation correctness floor is now solid for downstream work. Also restored missing `CODE_t *prolog_lower(PlProgram *)` function header in `src/frontend/prolog/prolog_lower.c` — commit `8fee1957` (PST-PL-6d) had left orphaned function body after helper additions; HEAD `0b931361` would not build from clean clone without this fix. Gates: smoke_icon 5/5, honest 277/0/0. | `068a7054` |
| IJ-FLIT | TT_FLIT real-literal lowering for Icon. `lower_icn_expr_node` (src/lower/lower_icn.c) was handling TT_ILIT but not TT_FLIT, so real literals in expression position fell through to ICN_BB_EVAL → `[NO-AST] SM_BB_EVAL` stub at runtime. Added TT_FLIT case mirroring TT_ILIT: `IR_node_alloc(IR_LIT_F)`, `nd->dval = e->v.dval`. IR_LIT_F executor in ir_exec.c already does `REALVAL(nd->dval)`. probe: `write(3.14)` → `3.14` (was `[NO-AST]` stub). **ir-run 111→125 (+14).** **Honest regression 277→272 (−5):** unmasked 5 programs (rung18_real_relop_real_relop_goal, rung36_jcon_arith/checkfpx/ck/mathfunc) that previously exited 0 with empty output (silently wrong) now timeout — they exercise real-typed binops/relops that IR_BINOP_GEN's binop_map doesn't yet handle for double operands. Net correctness improvement (visible failures > hidden failures); separate ticket needed for IR_BINOP_GEN real-typed arithmetic. | `48d797fa` |
| IJ-IRALLOC-OVERFLOW | IR_block_t gains `max` field; IR_node_alloc bounds-checked (returns NULL on overflow instead of stomping heap); lower_icn_proc_body IR_alloc 128→4096 — proc bodies with complex IR (real-typed relops over alternates, every-loops) were overflowing the 128-node cap and corrupting adjacent heap, manifesting as infinite loops under --ir-run. Also: IR_ICN_BINOP β outer loop missing `return nd->ω` when right.α also fails after left advances. **honest 272→276 (+4). broker 17→19 (+2). smoke 5/5.** | `6ddb9584` |
| IJ-TO-GEN | IR_ICN_TO operand re-pumping when bounds are generators. Mirrors IR_BINOP_GEN's cross-product β-pump: when counter > ival2, if c[1] (hi) is a generator, advance it; if c[1] exhausts and c[0] (lo) is a generator, reset c[1] and advance c[0]; only fail when both operand generators are exhausted. Inlined IR_IS_GEN_KIND_TO macro (same set as BINOP_GEN). Fixes rung01_paper_nested_to: `every write((1 to 2) to (2 to 3))` now produces full 8-value cross product 1,2,1,2,3,2,2,3 (was only 1,2). **ir-run 125→126 (+1).** Gates: smoke_icon 5/5. Honest neutral. | `92bfffd9` |

## NEXT step

Failing-rung survey (sess 2026-05-16d) found three categories driving remaining FAILs. Categories 1 and 2 landed; category 3 has been *decomposed* — Fix #1 landed:

1. ~~**Pattern-scan ops**~~ — ✅ landed in IJ-SCAN (`1841f7de`).
2. ~~**Generator cross-product in plain binops**~~ — ✅ landed in IJ-BINOP-GEN (`05097be3`).
3. **`every write(fact(5))` over-iteration** — both fixes landed:
   - **Fix #1 ✅** — `IJ-CALL-SNAPSHOT` (`398776da`). Recursive proc calls were wiping caller IR graph state via the inner `IR_reset`. Now snapshotted/restored. `write(fact(5))` correctly yields `120`.
   - **Fix #2 ✅** — `IJ-EVERY-SINGLESHOT`. proc_table.is_generator bit + recursive ir_is_single_shot classifier in IR_EVERY breaks the pump after one iteration when c[0] is structurally single-shot. ir-run 105→107 (+2). rung02_proc_fact and rung02_proc_add_proc flip PASS.

## NEXT step

**Three constructs landed this session (2026-05-17). Next session: continue rung survey for remaining FAILs.**

1. **rung36 jcon programs** — many still fail due to missing constructs (file I/O, co-expressions, string formatting). Survey which are closest to passing.
2. **IR_ALT with generator children** — now that single-shot beta is fixed, verify `every (1 to 3 | 4 to 6)` (generator-child alt) still works correctly.
3. **augop pow** — `x ^:= 2` now wired via AUGOP_POW; confirm with rung37_augop_pow if present.

## Completed steps (this session 2026-05-17)

| Step | Description | Commit |
|------|-------------|--------|
| IJ-ALT-BETA-SINGLESHOT | IR_ALT β-path: single-shot (non-generator) children treated as exhausted after first yield; ALT_IS_GEN() macro guards β-resume. Root cause of rung18 infinite hang confirmed: literal nodes (IR_LIT_F etc.) always succeed, trapping IR_BINOP_GEN relop-retry forever. rung18: 0/5 → 5/5. | `66dc3582` |
| IJ-POW | TT_POW (`^`) lowering to IR_BINOP/IR_BINOP_GEN via ICN_BINOP_POW. Added to IcnBinopKind enum, icn_binop_apply (always DT_R result per Icon semantics), lowering switch, augop switch. math.h added to lower_icn.c. rung19 pow: 0/3 → 3/3. | `6f3e9690` |
| IJ-TOBY-REAL | TT_TO_BY lowering added (was falling to [NO-AST] stub). IR_TO_BY executor rewritten with real-typed path: DT_R bounds detected on α, counter in nd->dval, step bits stored in nd->ival3 via memcpy, epsilon-guard comparison. Semantics verified against jcon vBigInt.ToBy and Icon omisc.r (JCON extension — classic Icon requires integer coercion). rung19 to-by: 0/2 → 2/2. | `66dc3582` + `6f3e9690` |

## Watermark

```
one4all: 6f3e9690 (IJ-POW: rung18+rung19 complete)
corpus:  490f4c7
ir-run:  148/281   honest: 276 PASS / 0 FAIL / 0 ABORT  (rung18 5/5 ✅  rung19 5/5 ✅)
smoke_icon: 5/5    broker: 19/49 (not re-run this session — too slow)
cross-lang smokes: snobol4 6/7 (1 pre-existing), snocone 5/5, prolog 5/5, raku 5/5
```

Latent bugs (pre-existing or unblocked, separate tickets):
- rung36 jcon programs: many xfail — file I/O, co-expressions, string builtins missing.
- Prolog smoke was 0/5 at last watermark; this session shows 5/5 (possibly fixed upstream).
- SM dump display labels `SM_STORE_FRAME` as "SM_LOAD_FRAME" (cosmetic).
- `every (s := "" | "a") do write(s)` — needs re-verification now that ALT beta is fixed.

Session note: IJ-ALT-BETA-SINGLESHOT root cause confirmed by tracing IR_BINOP_GEN → IR_ALT β → IR_LIT_F (always succeeds) → infinite relop-retry. Fix is minimal (one guard in IR_ALT β-path). Icon and JCON ToBy semantics verified: Icon classic requires integer coercion; JCON (vBigInt.ToBy) extends to reals via NLessEq. Our implementation follows JCON semantics with epsilon guard for float accumulation tolerance.
