# HANDOFF-2026-06-10-OPUS-ICON-NL-CONSTRUCT-SWEEP.md

**Session:** 2026-06-10 · Claude (Opus)
**Goal:** GOAL-ICON-FULL-PASS — β-CHAIN-REST + missing-construct sweep
**HEAD (SCRIP):** `d6964d4`
**m2:** 155 → **178** (+23)

---

## Method

Built the REAL `15608cf` oracle binary in a git worktree (the prior handoff's `SCRIP_NL=0`
oracle was vacuous — after `lower_icon.c` was deleted, `SCRIP_NL=0` selects nothing different):

```bash
git worktree add /tmp/oracle 15608cf
cd /tmp/oracle && make -j4 scrip      # build_scrip.sh hard-codes $ROOT/SCRIP, so make directly
```

Per failing rung: `diff <(./scrip --dump-bb f.icn) <(/tmp/oracle/scrip --dump-bb f.icn)`, make NL
match, **then confirm by output** — `--dump-bb` does NOT print `operand_aux`, so two graphs can
print identically yet behave differently.

**Correction to the prior handoff:** it claimed the 16 regressions had byte-identical dumps. That
was NL-vs-NL. Against the real oracle binary, 15/16 genuinely differed and were fixable.

## Fixes (8 commits, all gated: icon m2 12/12 HARD · prolog 5/5 HARD · one-box PASS)

1. **`c9ec94c`** write/writes chaining call resumes to last-arg β. NL declared the driver-set
   `g_icn_postfix_resume` and ignored it, unconditionally resetting `cx->beta=ω`. → `rung01_paper_nested_to`. +1
2. **`20bee0e`** subgraph-path generator calls (`find`/`upto`/generator-procs) self-resume β=call via new
   `icn_call_allow_gen` (mirrors oracle `icn_det_call`). → `find_gen` + suspend_gen trio. +4
3. **`38382a1`** `not E` → distinct IR_NOT (was mis-routed through `is_unop_tt`→IR_UNOP). +2
4. **`c734630`** bang `!x` (TT_ITERATE) → IR_LIST_BANG with self-resume β (was unhandled→IR_SUCCEED). +11 (widely used)
5. **`1f57db3`** `s[i:j]` section (TT_SECTION/PLUS/MINUS) → IR_SECTION, 3 operands, ival 0/1/2. +3
6. **`35718b7`** `x op:= y` rewritten at AST level to `x := (x op y)`, recursing through normal ASSIGN/BINOP
   (mirrors oracle `lower_icn`). Hand-built TT_AUGOP BINOP set neither `operand_aux` nor the β-chain. +1
7. **`d6964d4`** `&` conjunction (TT_SEQ) routed through IR_CONJ like TT_SEQ_EXPR (oracle: both→`v_conj`).
   Old TT_SEQ handler chained each operand's FAILURE to the next entry, so a failed left operand still ran the
   right (e.g. `any('aeiou') & (found:=1)` set found=1 on a non-vowel). +1

`g_stage2` access added to `lower_icon_nl.c` (`#include "stage2.h"`) for `icn_proc_is_generator`.

## Key learnings (carry forward)

- **`operand_aux` is invisible in `--dump-bb`.** The augop bug (`every sum +:= (1 to 5)` → 20 not 15) had a
  byte-identical dump and `IR_interp.c` is unchanged 15608cf→HEAD — it looked like a phantom interp regression
  but was a missing `bb_operand_aux_set` on the hand-built BINOP. Always confirm by output.
- **Interp operand convention changed 15608cf→HEAD.** IR_NOT/IR_SECTION/IR_LIST_BANG read `bb->operands[0]`
  at HEAD (the oracle read `operand_aux`). When porting from the oracle, push via `ir_operand_push`, not
  `bb_operand_aux_set`. The residual NOT/SECTION/BANG dump deltas (an `ops:[N]` annotation) are exactly this.

## State (all gates green)

- m2 icon rung suite **178**/247 non-xfail · m3 27 · m4 30
- icon smoke m2 12/12 HARD · m3 10/12 · m4 10/12 (same 2 pre-existing: proc_zeroarg, proc_recursion)
- prolog smoke m2 5/5 HARD · one-box gate PASS · no value stack · no C byrd-box · no bb_bin_t

## Open

- **FULL-14 scan-alt** — `rung08_strbuiltins_match`: `"world" ? write(match("xyz") | 0)` yields nothing,
  expects `0`. Top-level dump identical to oracle; the `IR_ALT` β-resume inside the GEN_SCAN subgraph doesn't
  fall to `0` when `match` fails. Consult JCON `ir_a_Alt` + `ir_a_Scan`; dump the arg_block subgraph to compare.
- Untouched goal items: FULL-12 coerce, FULL-13 keyword residuals, FULL-15 str relop, FULL-16 mutual recursion,
  FULL-17 sort(), FULL-18 alt cross-arg.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
