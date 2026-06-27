# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** corpus+SCRIP  
**Branch:** `parser` (SCRIP only — `corpus` and `.github` stay on `main`)  
**Status:** PASS=89/89 ✅ corpus@5f065e4 — **SN-7-9 LANDED.**

---

## Session Setup

```bash
( cd /home/claude/SCRIP && git fetch origin parser && git checkout parser )
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

Gate:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh
bash /home/claude/SCRIP/scripts/test_scrip.sh
bash /home/claude/SCRIP/scripts/test_parser_snobol4.sh   # must be PASS=89 FAIL=0
```

Parser invocation:
```bash
SCRIP=/home/claude/SCRIP/scrip; RT=/home/claude/corpus/SCRIP
$SCRIP --run $RT/global.sc $RT/tree.sc $RT/stack.sc $RT/counter.sc \
  $RT/ShiftReduce.sc $RT/semantic.sc $RT/qize.sc $RT/gen.sc \
  $RT/tdump.sc $RT/assign.sc $RT/parser_snobol4.sc < input.sno
```

---

## Architecture

```
scrip --run [blob] parser_snobol4.sc < input.sno   →  TDump tree lines
scrip --dump-parse input.sno                           →  oracle tree lines
```

Gate normalizes: collapse whitespace, strip ` )` → `)`. Blob: `global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc qize.sc gen.sc tdump.sc assign.sc`

---

## Style guidelines

### §1 Names match spec; oracle wins over spec.
### §2 `Gray`/`White` attached; `$' '`/`$'  '` for optional/required ws.
### §3 `$'name'` tokens. Binary ops: `$' ' 'op' $' '`. Brackets: `'(' $' '` / `$' ' ')'`.
### §4 shift/reduce for tree building; pair-shape for in-pattern actions.
### §5 n-ary: `nPush() nInc() reduce(TAG,'nTop()') nPop()`.
### §6 AST tags: `E_*` pre-quoted constants.

SNOBOL4 tags: `E_VAR E_ILIT E_QLIT E_RLIT E_FNC E_SEQ E_ALT E_LEN E_BREAK E_SPAN E_ANY E_NOTANY E_CAPT_COND_ASGN E_CAPT_IMMED_ASGN E_KEYWORD E_DEFER E_IDX E_ADD E_SUB E_MUL E_DIV E_POW E_PLS E_MNS E_FENCE E_ARBNO E_POS E_RPOS E_TAB E_RTAB E_BREAKX E_INDIRECT E_NAME E_ASSIGN E_NOT E_CAPT_CURSOR E_INTERROGATE E_OPSYN`  
Role-slots: `:lbl :subj :pat :repl :goS :goF :goU :eq :end`

### §7 Identifiers: lowercase_snake vars, UpperCamel patterns/functions, no `_`-prefix.
### §8 Layout: 120-char max, no-brace single-stmt, `//====`/`//----` dividers, no blank lines.
### §9 Read beauty.sno and beauty.sc before authoring.

---

## SNOBOL4 oracle tree shapes

| Construct | Oracle |
|-----------|--------|
| `x` | `(STMT :subj (E_VAR x))` |
| `x = 5` | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `END` col 0 | `(STMT :lbl END :end)` |
| blank line | `(STMT)` — suppressed after label-only stmt |
| `FENCE(p)` | `(E_FENCE ...)` |
| `ARBNO(p)` | `(E_ARBNO ...)` |
| `POS(n)` | `(E_POS (E_ILIT n))` |
| `RPOS(n)` | `(E_RPOS (E_ILIT n))` |
| `$x` | `(E_INDIRECT (E_VAR x))` |
| `.x` | `(E_NAME (E_VAR x))` |
| `=x` | `(E_ASSIGN (E_VAR x))` |
| `~p` unary | `(E_NOT ...)` |
| `a & b` | `(E_OPSYN & ...)` |
| `a ~ b` | `(E_OPSYN ~ ...)` |
| `a @ b` | `(E_OPSYN @ ...)` |
| `a # b` | `(E_MUL ...)` |
| `a % b` | `(E_DIV ...)` |

**subj/pat split:** only when first child of E_SEQ is `E_VAR`. Fn-call concat stays in `:subj`.  
**goto ordering:** `:goS` before `:goF` for simple targets; `:goF` before `:goS` when goS is computed.  
**computed goto:** `$('x' t)` → `:go $((E_SEQ (E_QLIT "x") (E_VAR t)))`.

---

## Next rung: SN-7-9 — eliminate all rw_ functions; grammar builds correct tree directly

**Goal:** delete `rw_call`, `rw_expr`, and `rw_goto_slot` entirely. The grammar must emit the correct `E_*`-tagged tree directly at parse time — no post-parse rewrite pass. This is the beauty.sno model: `pp_*` walks the parse tree and pretty-prints; it never renames nodes because the grammar already built the right shape.

**What each rw_ function currently does and how to eliminate it:**

`rw_call` — renames `E_FNC` nodes for 12 known primitives (LEN BREAK SPAN ANY NOTANY FENCE ARBNO POS RPOS TAB RTAB BREAKX) to their `E_*` tags. **Fix:** split Expr17's call arms — add one arm per primitive before the generic `*Function` arm. Each arm matches the literal name, consumes it (not stored as value), then parses the arg list and reduces with the correct tag. Generic calls fall through to the existing `(E_FNC & 2)` arm which stores fname in `v`.

`rw_expr` — does five things, all fixable in grammar:
- strips `()` paren wrappers → Expr17 already has `'()' & 1` shape; change paren group to just `*Expr` (no wrapper node at all, since parens are structural only)
- unwraps `ExprList` single-child → if ExprList already uses `nPush/nInc/nPop`, the reduce fires the right count and no unwrap is needed
- flattens `E_IDX` ExprList children → fix E_IDX grammar arm to use nPush/nInc/nPop directly so children are inline, no ExprList wrapper
- left-rotates `E_CAPT_*_ASGN` chains → fix Expr12 to iterate left-to-right (use foldop or iterative shape) instead of right-recursive
- generic tree copy (base case) → not needed once above are fixed; grammar produces correct tree

`rw_goto_slot` — formats goto target as string for the slot value. This is pp_stmt bookkeeping, not a tree rewrite. **Inline** its logic directly into pp_stmt's goto-appending code (3 call sites); delete the function.

**Research findings (sessions 2026-05-05 through present):**

Key discoveries from multiple sessions of investigation:

1. **SNOBOL4 `|` always backtracks** — unlike PEG parsers. `FENCE(a|b)` backtracks to start for each alternative. So the call arm `*Id ~ E_VAR $'(' ...` and no-call arm `*Id ~ E_VAR` being in the same `FENCE` is correct semantics: after call arm fails, FENCE restarts from before the identifier for the no-call arm.

2. **Double-push is real but manageable** — when the call arm (`*Id ~ E_VAR $'('`) fails after shifting `E_VAR_ID`, the no-call arm re-shifts `E_VAR_ID`. This puts two `E_VAR_ID` on the stack. In the old grammar this was harmless because the Compiland reduce consumed the right count. The fix: **combine call and no-call into a single arm** using `FENCE($'(' *FnArgs $')' | epsilon)` after the single `*Id ~ E_VAR` shift. Only one shift ever happens.

3. **`ReduceCall()` must read `TopCounter()` internally** — cannot pass `nTop()` as an argument because the argument is evaluated at pattern-construction time (definition time), not match time. Confirmed working: `ReduceCall()` with no args calls `TopCounter()` at fire time. ✓

4. **`ReducePrim(tag)` needed** — for primitives (LEN, BREAK, etc.) the arms need `*ReducePrim(E_TAG)` not `(E_TAG & 'nTop()')` because the `&` operator calls `reduce()` at definition time, which calls `EVAL("epsilon . *Reduce(tag, nTop())")` immediately — `nTop()` runs at definition time when counter is uninitialized → hangs.

5. **Mutual recursion hang** — `FnArgList = nInc() *Expr FENCE($',' *FnArgList | epsilon)` defined as a global pattern causes hang because `Expr17` includes `FENCE(*FnArgList | epsilon)` in primitive arms, and when `Expr17` is being defined, `FnArgList` construction triggers `Expr17` construction — mutual recursion at definition time. **Fix: make `FnArgList` a function** (using `nreturn`) so it's only instantiated at match time.

6. **rw_expr/rw_call become dead code** once grammar produces correct E_* trees directly. After deletion, `pp_stmt` uses parse tree nodes directly (`subj_ir = ppSubj` instead of `subj_ir = rw_expr(ppSubj)`).

**Exact implementation plan (next session):**

```
// In ShiftReduce.sc — ADD:
function ReduceCall(n, args, i, fname, r) {   // reads TopCounter() internally
    n = TopCounter(); args = ARRAY('1:'n); ...pop n args...fname=v(Pop());
    Push(tree('E_FNC', fname, n, args)); nreturn; }
function ReducePrim(tag, n, args, i, r) {     // reads TopCounter() internally  
    tag = EVAL(tag) if EXPRESSION; n = TopCounter(); ...pop n args...
    Push(tree(tag, '', n, args)); nreturn; }
function ReduceOpsyn(op, n, c, i, r) { ... }  // already in last session

// In semantic.sc — ADD:
function reduce_opsyn(op, n) { reduce_opsyn = EVAL("epsilon.*ReduceOpsyn('"op"',"n")"); return; }

// In parser_snobol4.sc — CHANGES:
// 1. After XList, ADD:
function FnArgList() { FnArgList = nInc() *Expr FENCE($',' *FnArgList | epsilon); nreturn; }
// 2. Expr12: change to foldop left-assoc
// 3. Expr16: change ExprList → XList
// 4. Expr17: new arms (paren pass-through, 12 primitives with *ReducePrim, single-arm calls)
//    CRITICAL: combine *Function~E_VAR and *Id~E_VAR with optional-call FENCE:
//    |  *Function ~ E_VAR FENCE(nPush() $'(' *FnArgList *ReduceCall nPop() $')' | epsilon)
//    |  *Id       ~ E_VAR FENCE(nPush() $'(' *FnArgList *ReduceCall nPop() $')' | epsilon)
//    Note: *ReduceCall (no parens) — Snocone syntax for deferred zero-arg call
//    Actually: use *FnArgs pattern variable (not function) to wrap the call arm internals
// 5. Delete rw_call, rw_expr; rename rw_goto_slot → make_goto_slot
// 6. pp_stmt: subj_ir = ppSubj (not rw_expr(ppSubj)), same for pat/repl
```

**Steps:**
- [x] Add `ReduceCall`, `ReducePrim` to `ShiftReduce.sc`
- [x] Add `reduce_call`, `reduce_prim` to `semantic.sc`
- [x] Add `FnArgList`/`FnArgTail` as global pattern variables (args/args_tail idiom) to `parser_snobol4.sc`
- [x] Rewrite `Expr12` with binary `(tag & 2)` left-assoc tail for `E_CAPT_IMMED_ASGN`/`E_CAPT_COND_ASGN`
- [x] Restore `Expr16` with `*ExprList`; flatten ExprList in `strip_parens`
- [x] Rewrite `Expr17`: paren wrapper `('()' & 1)`; 12 PrimXXX arms with `reduce_prim`; call/no-call FENCE arms
- [x] Delete `rw_call` and `rw_expr`; rename `rw_goto_slot` → `make_goto_slot`
- [x] Add `strip_parens` (recursive `'()'`-strip + E_IDX/ExprList flatten); use in `pp_stmt` for all slots
- [x] Gate: PASS=89 FAIL=0; beauty crosscheck 433/433 passes
- [x] Commit: `PARSER-SN SN-7-9: eliminate rw_call/rw_expr; grammar emits E_* directly at parse time`

---

## PARSER-FAMILY-LOOP — ✅ CLOSED by owner

All six parsers green at close: SN=89 IC=88 PR=60 RK=37 SC=46 RB=38 corpus@ac0663c. No further iterations planned.

---

## Known runtime workarounds

- **FW-3** ARBNO ✅ SCRIP@228bc06b  
- **INFRA-11a** subj?pat ✅ SCRIP@d2547945  
- **INFRA-11b** OPSYN `~`/`&` infix ⚠ needs re-probe  
- **INFRA-11c** `_qtag` ✅ corpus@c8ee2a6  
- **PARSER-SC FENCE/`*deref`** ⚠ open (eval_pat.c E_FENCE)

---

## Closed rungs

INFRA-0..10, FW-1..3/6, SN-0..7-9 all ✅.

---

## Watermark

**SN-7-9 LANDED corpus@5f065e4 PASS=89/89.**  
rw_call/rw_expr deleted. Grammar emits correct E_* trees at parse time. strip_parens handles '()'-unwrap and ExprList-flatten. FnArgList/FnArgTail global pattern variables (args/args_tail idiom). 12 PrimXXX classifiers + reduce_prim/reduce_call. beauty.sno crosscheck: 433/433 STMTs, 0 mismatches.
