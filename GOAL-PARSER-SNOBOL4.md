# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all  
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)  
**Status:** PASS=89/89 ✅ corpus@ac0663c — **SN-7-8 LANDED.**

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser && git checkout parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh
bash /home/claude/one4all/scripts/test_scrip.sh
bash /home/claude/one4all/scripts/test_parser_snobol4.sh   # must be PASS=89 FAIL=0
```

Parser invocation:
```bash
SCRIP=/home/claude/one4all/scrip; RT=/home/claude/corpus/programs/scrip
$SCRIP --ir-run $RT/global.sc $RT/tree.sc $RT/stack.sc $RT/counter.sc \
  $RT/ShiftReduce.sc $RT/semantic.sc $RT/qize.sc $RT/gen.sc \
  $RT/tdump.sc $RT/assign.sc $RT/parser_snobol4.sc < input.sno
```

---

## Architecture

```
scrip --ir-run [blob] parser_snobol4.sc < input.sno   →  TDump tree lines
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

**Steps:**
- [ ] Fix Expr17: add 12 primitive call arms (LEN BREAK SPAN ANY NOTANY FENCE ARBNO POS RPOS TAB RTAB BREAKX), each `'NAME' nPush() $'(' *XList (E_TAG & 'nTop()') nPop()` — no name stored, args as children
- [ ] Fix paren group in Expr17: emit no wrapper node — the `'()' & 1` arm currently tags the group; change to pass-through (the paren just groups, Expr handles the value)
- [ ] Fix E_IDX in Expr15/16: use nPush/nInc/nPop so bracket-group children are direct children of E_IDX, no ExprList wrapper
- [ ] Fix Expr12 E_CAPT_*_ASGN: use iterative foldop shape so tree is already left-associative at parse time
- [ ] Delete `rw_call`, `rw_expr`, `rw_goto_slot` functions
- [ ] In pp_stmt: inline the 3 `rw_goto_slot` call sites; inline the 3 `rw_expr` call sites (now just use the stack-popped tree directly)
- [ ] Gate: PASS=89 FAIL=0 throughout; beauty crosscheck still passes
- [ ] Commit: `PARSER-SN-7-9: eliminate all rw_ functions — grammar builds correct tree directly (PASS=N/N)`

---

## PARSER-FAMILY-LOOP — ✅ CLOSED by owner

All six parsers green at close: SN=89 IC=88 PR=60 RK=37 SC=46 RB=38 corpus@ac0663c. No further iterations planned.

---

## Known runtime workarounds

- **FW-3** ARBNO ✅ one4all@228bc06b  
- **INFRA-11a** subj?pat ✅ one4all@d2547945  
- **INFRA-11b** OPSYN `~`/`&` infix ⚠ needs re-probe  
- **INFRA-11c** `_qtag` ✅ corpus@c8ee2a6  
- **PARSER-SC FENCE/`*deref`** ⚠ open (eval_pat.c E_FENCE)

---

## Closed rungs

INFRA-0..10, FW-1..3/6, SN-0..7-8 all ✅.

---

## Watermark

**SN-7-8 LANDED corpus@ac0663c one4all@104f270d PASS=89/89.**  
beauty.sno crosscheck: 433/433 STMTs, 0 mismatches. PARSER-FAMILY-LOOP closed by owner. SN-7-9 step written: eliminate rw_call, inline 12 primitive call tags in Expr17.
