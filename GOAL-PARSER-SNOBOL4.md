# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all  
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)  
**Status:** PASS=78/78 ✅ corpus@0fba291 — SN-7-7c LANDED. **Next: SN-7-8** beauty.sno full crosscheck.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh
bash /home/claude/one4all/scripts/test_scrip.sh
bash /home/claude/one4all/scripts/test_parser_snobol4.sh   # must be PASS=78 FAIL=0
```

Parser invocation (for manual testing):
```bash
SCRIP=/home/claude/one4all/scrip
RT=/home/claude/corpus/programs/scrip
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

Whitespace-normalized byte-diff of both = gate. Shared blob:
`global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc qize.sc gen.sc tdump.sc assign.sc`

---

## Style guidelines (binding — canonical home for all PARSER-* family)

### §1 Names match language spec
Pattern names mirror BNF + existing frontend's token enum and IR-tag enum. Operational oracle wins over spec where they disagree.

### §2 White/Gray attached, never in main grammar
```
Gray  = White | epsilon;
White = ( SPAN(' ' tab) FENCE(nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) | epsilon)
        | nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon)
        );
$' '  = Gray;   // optional ws
$'  ' = White;  // required ws
```
Exception: `*White` appears in 5 places in parser_snobol4.sc where SNOBOL4 column-sensitive grammar requires it (annotated inline with `// ws-here-is-required:<reason>`).

### §3 `$'name'` tokens; `$' '`/`$'  '` for optional/required ws
Non-identifier punctuation uses `$'...'`. Binary ops: `$' ' 'op' $' '`. Open bracket: `'(' $' '`. Close bracket: `$' ' ')'`. Keywords: `$' ' 'kw' $' '`.

### §4 shift/reduce for tree building
Use `shift(p, t)` / `reduce(t, n)` (function-call form — INFRA-11b means `~`/`&` infix not yet usable). Anti-pattern: `$'do_X'` action wrappers + parallel helper globals. Use the stack instead.

Pair-shape for in-pattern semantic actions (iter#5 canonical):
```
function push_foo() { Push(tree(E_FOO, val)); push_foo = .dummy; nreturn; }
function Push_foo() { Push_foo = epsilon . *push_foo(); return; }   // Form 1 (no args)
function Push_bar(a) { Push_bar = EVAL("epsilon . thx . *push_bar_w()"); return; }  // Form 2 (args)
```

### §5 n-ary trees: `nPush() ... nInc() ... reduce(TAG, 'nTop()') ... nPop()`
`nPush/nInc/nTop/nPop` are pattern-producing functions — embed as patterns, not side-effect calls.

### §6 AST tags use `E_*` from `EXPR_t`
SNOBOL4 tags: `E_VAR E_ILIT E_QLIT E_RLIT E_FNC E_SEQ E_ALT E_LEN E_BREAK E_SPAN E_ANY E_NOTANY E_CAPT_COND_ASGN E_CAPT_IMMED_ASGN E_KEYWORD E_DEFER E_IDX E_ADD E_SUB E_MUL E_DIV E_POW E_PLS E_MNS E_POS E_RPOS`.  
Role-slot tags: `:lbl :subj :pat :repl :goS :goF :goU :eq :end`.

### §7 Identifier conventions
| Kind | Convention | Examples |
|------|-----------|---------|
| Variable | lowercase_snake | `tx`, `str_body`, `cur_line` |
| Function | UpperCamelCase | `Push`, `TDump`, `FoldOp`, `Push_qlit` |
| Pattern rule | UpperCamel | `Id`, `Expr0`, `Compiland` |
| Token (special) | `$'...'` | `$'='`, `$','`, `$' '` |
| AST tag constant | `E_*` pre-quoted | `E_VAR = "'E_VAR'"` |
No `_`-prefix identifiers in user code.

### §8 Layout
120-char max. Single-statement bodies: no braces (`if (x) stmt ;`). Section dividers: `//====` (120 chars, major) and `//----` (120 chars, minor). No blank lines — use dividers. Horizontal packing of related short rules.

### §9 Read beauty.sno and beauty.sc before authoring

---

## SNOBOL4 oracle tree shapes

| Construct | Oracle shape |
|-----------|-------------|
| `x` | `(STMT :subj (E_VAR x))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `'hi'` | `(STMT :subj (E_QLIT "hi"))` |
| `END` at col 0 | `(STMT :lbl END :end)` |
| `x = 5` | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `S 'a' 'b'` | `(STMT :subj (E_VAR S) :pat (E_SEQ ...))` |
| `S 'a' \| 'b'` | `(STMT :subj (E_ALT (E_SEQ ...) ...))` (alt eats LHS) |
| `S 'a' = 'b'` | `(STMT :eq :subj ... :pat ... :repl ...)` |
| `S = ` (empty) | `(STMT :eq :subj (E_VAR S) :repl (E_QLIT ""))` |
| `S 'a' :S(L1)` | `(STMT :subj ... :pat ... :goS L1)` |
| `LEN(3)` | `(E_LEN (E_ILIT 3))` |
| `F(X)` | `(E_FNC F (E_VAR X))` |
| `*Id` | `(E_DEFER (E_VAR Id))` |
| `&KW` | `(E_KEYWORD KW)` |
| `x[i]` | `(E_IDX (E_VAR x) (E_ILIT i))` |
| `POS(n)` | `(E_POS (E_ILIT n))` |
| `RPOS(n)` | `(E_RPOS (E_ILIT n))` |
| blank line | *(nothing emitted)* |

**`:subj`/`:pat` split rule:** parse body as one expr. If top is `E_SEQ` with N≥2 → child 1 is `:subj`, rest is `:pat`. Anything else → whole expr is `:subj`, no `:pat`.

**Operator precedence** (loose→tight): `|` < concat < `.$` < `^!**` < `*` < `/` < `+-` < unary `+-` < atom. `.` and `$` left-associative.

---

## Active rung: SN-7-8 — beauty.sno full crosscheck

**Goal:** parser output on `beauty.sno` matches `--dump-parse` oracle (whitespace-normalized).

**Current state (session 2026-05-05):**
- Oracle (no-include): 433 STMTs. Parser: 424 STMTs. Gap: 9 missing.
- Blank-line bug: **FIXED this session** — driver now skips TDump when `pp_stmt` returns 0-child STMT.
- Parser invocation reads stdin; oracle expands `-INCLUDE`. Gate should compare parser vs `--dump-parse /tmp/beauty_no_inc.sno` (beauty.sno with `-INCLUDE` lines stripped).

**Known missing constructs** (9 STMTs gap after blank-line fix):
`POS`, `RPOS` used as pattern primitives in beauty.sno (in `TxInList`, `Compiland`). The classifier tables `Functions`/`BuiltinVars`/etc. already list them as Functions so they parse via `E_FNC` path — but oracle emits `E_POS`/`E_RPOS`. Need dedicated Expr14/Expr17 alternatives or `rw_call` dispatch for these.

**Steps:**
- [x] Fix blank-line: skip TDump on 0-child STMT — `if (DIFFER(n(result))) TDump(result);`
- [ ] Add `beauty_crosscheck` test script comparing parser vs oracle on beauty.sno (no-include)
- [ ] Identify all 9 missing/wrong STMTs by diffing normalized outputs
- [ ] Add `E_POS`/`E_RPOS` (and any other missing primitives) to `rw_call` dispatch in `parser_snobol4.sc`
- [ ] Add fixtures for the new constructs to `corpus/programs/snobol4/parser/`
- [ ] Gate: `test_parser_snobol4.sh` PASS increases + beauty crosscheck passes
- [ ] Commit: `PARSER-SN-7-8: beauty.sno full crosscheck (PASS=N/N)`

**Gate:** beauty.sno parser output ≡ oracle output (whitespace-normalized).

---

## PARSER-FAMILY-LOOP — six-parser cross-pollination

All six parsers at 100% as of corpus@0fba291 (session 2026-05-05):

| Parser | Gate |
|--------|------|
| snobol4 | PASS=78/78 ✅ |
| icon | PASS=88/88 ✅ |
| prolog | PASS=60/60 ✅ |
| raku | PASS=37/37 ✅ |
| snocone | PASS=46/46 ✅ |
| rebus | PASS=38/38 ✅ |

Loop rules: (1) one concept per iteration, (2) identical shape in all six files, (3) all gates 100% throughout, (4) one commit per iteration, (5) SN first, (6) fix SCRIP bugs before working around them, (7) update table below each iteration.

**Next loop iteration candidates:**
- iter#11: cross-pollinate `foldop()`/`FoldOp()` to IC/PR/SC (same-tier mixed-op bug; RK already closed)
- iter#10b: remove `is_rotate_op` from SN `rw_expr` once runtime `E_CAPT_*_ASGN` goes n-ary
- Cleanup CR-3..CR-5: Rebus RExpr→EXPR_t (CR-1/CR-2 done; CR-3/CR-4/CR-5 pending)
- FENCE sweep second pass (iter#10 Phase E) across remaining five parsers

**Iteration log:**

| # | Concept | SN | IC | PR | RK | SC | RB | Commit |
|---|---------|----|----|----|----|----|----|--------|
| 1 | White-encodes-comments + `$' '`/`$'  '` canonical | 59 | 51 | 54 | 32 | 21 | 38 | session 2026-05-04 cont.#6 |
| 2 | Aligned token blocks | 59 | 51 | 54 | 32 | 21 | 38 | corpus@d41add5 |
| 3 | Correct bracket/keyword ws per SN model | 59 | 51 | 54 | 32 | 21 | 38 | corpus@3e58061 |
| 4 | SUPERSEDED → iter#5 | — | — | — | — | — | — | — |
| 5 | Pair-shape semantic instrumentation + bare names | 59 | 51 | 54 | 32 | 21 | 38 | session 2026-05-05 |
| 6 | `$'X'` token variables in productions | 59 | 51 | 54 | 32 | 21 | 38 | session 2026-05-05 |
| 7 | SN only: grammar emits E_* directly; delete rw_tag | 59 | 51 | 54 | 32 | 21 | 38 | session 2026-05-05 |
| 8 | FENCE around all right levels | 59 | 51 | 54 | 32 | 21 | 38 | session 2026-05-05 |
| 9 | n-ary trees everywhere; flatten arith/concat/alt in C frontends | 62 | 88 | 54 | 31 | 46 | 38 | one4all@4393ce1e + corpus@61d825d |
| 10 | SN: iterative left-recursive arith with foldop() | 62 | 88 | 54 | 31 | 46 | 38 | corpus@408fbe0 |
| 11 | (pending — foldop cross-pollination to IC/PR/SC/RK) | | | | | | | |

---

## Known runtime workarounds

### FW-3 — ARBNO deferred-call firing ✅ FIXED one4all@228bc06b
`interp_eval_pat E_FNC` guards restored for ARBNO/FENCE (removed in RS-5).

### INFRA-11a — `subj ? pat` value context ✅ FIXED one4all@d2547945
Returns matched substring per spec. New SM opcode `SM_PUSH_LAST_MATCH`.

### INFRA-11b — OPSYN `~`/`&` infix — ⚠ NEEDS RE-PROBE
Quick probe after 11a/11c shows `~` may work. If confirmed, PARSER-* can use `~`/`&` verbatim from beauty.sno.

### INFRA-11c — `_qtag(t)` auto-quoting in shift/reduce ✅ FIXED corpus@c8ee2a6

### PARSER-SC FENCE/`*deref` silent-fail bug — ⚠ OPEN
`*Id FENCE('=' *Id | epsilon)` against `'x=y'` captures `[x]` not `[x=y]`. Probable fix: `eval_pat.c E_FENCE`. Documented in GOAL-PARSER-SNOCONE.md.

---

## Closed rungs (summary only)

| Rung | Title | Gate |
|------|-------|------|
| INFRA-0..10 | Runtime infrastructure | all ✅ |
| FW-1..3,6 | Framework: TValue, role-slots, Compiland spine, multi-line TDump | all ✅ |
| SN-0..6 | atom, assign, tree pivot, concat/arith, control, patterns, functions | PASS=58 |
| SN-7-0..7-0a | Scaffold rewrite + style audit | PASS=0→0 (style) |
| SN-7-1 | Labels + assignment + full tree-shape rewrite (role-slots, IR tags, alt-eats-LHS, left-assoc, paren-strip, 1-arg-call, goto-direction-in-tag) | PASS=59/59 |
| SN-7-2 | &KEYWORD recognition (consume `&`, shift name-only) | PASS=66/66 |
| SN-7-3 | Bracket index `x[i]`, `x[i,j]` | PASS=70/70 |
| SN-7-4 | `+`/`.` continuation lines | PASS=73/73 |
| SN-7-5 | Comment/control lines | PASS=74/74 |
| SN-7-6 | `*Id` deferred-pattern reference | PASS=77/77 |
| SN-7-7 | `;` mid-line separator | PASS=78/78 |
| SN-7-7b | Grammar emits E_* directly; rw_tag deleted | PASS=78/78 corpus@0390853 |
| SN-7-7c | Full keyword/function/builtin inventory + classifier patterns | PASS=78/78 corpus@0fba291 |

---

## Deferred

- **PARSER-SN-FW-4** — `scrip --parser-crosscheck` C-side flag (tree_equal + Snocone bridge)
- **PARSER-SN-FW-5** — TLump function-name-slot wart root-cause (defensive)
- **Cleanup CR-3..CR-5** — Rebus RExpr→EXPR_t (CR-1/CR-2 done; low priority since RB green)

---

## Watermark

**SN-7-7c LANDED PASS=78/78 corpus@0fba291.** Cross-runtime symbol inventory complete (SPITBOL x64/x32 + csnobol4 union). Functions(123) UnprotKwds(21) ProtKwds(28) BuiltinVars(7) SpecialNms(8). SN-7-7b: E_* tags direct, rw_tag deleted.

**Session 2026-05-05 (this session):** Blank-line fix landed in driver (`if (DIFFER(n(result))) TDump(result)`). SN-7-8 investigation started: oracle(no-inc)=433 STMTs, parser=424. Gap=9. Known missing: POS/RPOS as pattern primitives. Next: add beauty crosscheck script, identify all 9 gaps, fix rw_call dispatch.
