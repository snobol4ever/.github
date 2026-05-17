# HANDOFF — Session 2026-05-16g (GOAL-PST-ICN-RAKU)

**Date:** 2026-05-16
**Goal:** GOAL-PST-ICN-RAKU — Pure Syntax Tree: Icon + Raku SCRIP mirror cleanup
**Claude:** Sonnet 4.6

---

## Headline

**GOAL-PST-ICN-RAKU is DONE.** All hard PST violations fixed in both C parsers
and both SCRIP mirror files. `parser_icon.sc` reduced from 525→381 lines;
`parser_raku.sc` fully rewritten from 1788→953 lines, 95→39 functions.
`AST_t` confirmed absent from `icon_parse.c` and `raku.y`. All gates green.

---

## Work completed this session

### PST-ICN-4a — one4all@c52b724c
- `TT_MATCH_UNARY` added to `ast.h` (replaces synthetic `TT_FNC(TT_VAR('match'),inner)`)
- `icon_parse.c` unary `=` emits `TT_MATCH_UNARY(inner)` directly
- `TT_FIELD` layout changed: `c[0]=object`, `c[1]=TT_VAR(fieldname)`, no `v.sval`
- `ICN_FIELD_NAME(e)` macro added to `ast.h`; all consumers updated:
  `lower.c`, `icn_value.c`, `icn_runtime.c`, `interp_eval.c`, `interp_ref.c`
- `lower_icn.c`: `TT_MATCH_UNARY` → `IR_CALL("match", inner)`

### PST-ICN-4b — corpus@0ecae06
- `parser_icon.sc`: 525→381 lines, 9 structural helpers eliminated
- Eliminated: `push_field`→`reduce('TT_FIELD',2)`, `push_match`→`reduce('TT_MATCH_UNARY',1)`,
  `push_section`→`reduce('TT_SECTION',3)`, `push_subscript`→`reduce('TT_IDX',2)`,
  `decompose_proc/push_record/push_global_top`→`nPush/nInc/reduce/reduce(':subj',1)/reduce('STMT',1)/nPop`,
  `push_local_stmt`→`reduce('TT_LOCAL','nTop()')`,
  `push_static_stmt`→`reduce('TT_STATIC_DECL','nTop()')`
- Retained 5 PST-allowed functions: `notmatch` (predicate), `push_qlit/cset/flit/kw` (leaf constructors)

### PST-RAKU-5a — audit (HQ@264761fb)
- R1: `flatten_add/sub/mul/div/cat` — t(lhs) inspection + in-place append
- R2: `finish_given` — t(val) TT_QLIT test = semantic in parser
- R3: `finish_class` — t(item) split + v(item)/v(c[1]) mutation
- R4: `finish_for_range` — c(body)[i] copy = lowering in parser
- R5: ~95 finish_*/push_* named-function reduce equivalents

### PST-RAKU-5b — corpus@31cc6f2
- R1 fixed: `flatten_*` deleted; grammar→`reduce('TT_ADD/SUB/MUL/DIV/CAT',2)`
- R2 fixed: `finish_given` t(val) inspection removed; emits [val,body] pairs
- R3 fixed: `finish_class` t(item)/v() mutations removed; all items→TT_RECORD children
- R4 fixed: `finish_for_range` desugaring→`Tree('TT_FOR',for_iter,3,lo,hi,body)`

### PST-RAKU-5c — corpus@3cb7ada ← **FINAL**
Complete rewrite of `parser_raku.sc`: 1788→953 lines, 95→39 functions.
All `finish_*` tree-assembly helpers eliminated and replaced with:
- 55 `Push_fn_*` pattern variables (one per synthetic builtin name)
- Single `push_fn(nm)` leaf factory function
- Inline `Push_fn_X  reduce('TT_FNC', N)` in every grammar rule
Remaining 39 functions are all PST-compliant:
- 22 `push_*` leaf constructors from token captures
- 1 `push_fn` (literal sval factory)
- 3 `set_*` state setters, 1 `store_for_iter`, 1 `dq_unescape`, 1 `push_interp_str`
- 10 `finish_*` counter-based variable-arity assemblers (TopCounter+loop,
  no child-kind inspection, cannot be expressed as single reduce)

---

## Watermark

```
one4all: ef2f90e4   corpus: 3cb7ada   .github: 4fa92dfb
smoke_icon: 5/5     smoke_raku: 5/5
crosscheck_snobol4: 6/6
ir-run: 108/265 (up from 107 — bonus from pulled commits)
```

---

## AST_t status

`AST_t` confirmed absent from both `icon_parse.c` and `raku.y`.
Clean since PST-RAKU-3b. Verified this session.

---

## Next

GOAL-PST-ICN-RAKU is DONE. Suggested next goals per PLAN.md:
- **Icon BB JCON** — `rung03_suspend_gen*` (TT_SUSPEND with do-body, 3 rungs failing)
- **PST: SNOBOL4 + Snocone** — PST-SC-4a (Snocone TT_AUGOP to lower)
- **PST: Rebus + Prolog** — PST-PL-6c (verifier)
