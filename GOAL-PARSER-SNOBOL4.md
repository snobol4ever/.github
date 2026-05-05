# GOAL-PARSER-SNOBOL4.md — PARSER-SNOBOL4 pattern-based frontend in Snocone

**Repo:** corpus+one4all  
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)  
**Status:** PASS=78/78 ✅ corpus@634d2bb — SN-7-8 in progress.

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

Crosscheck script (for beauty.sno):
```bash
SCRIP=/home/claude/one4all/scrip; RT=/home/claude/corpus/programs/scrip
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty/beauty.sno
grep -v '^-INCLUDE' $BEAUTY > /tmp/beauty_noinc.sno
$SCRIP --ir-run $RT/global.sc $RT/tree.sc $RT/stack.sc $RT/counter.sc \
  $RT/ShiftReduce.sc $RT/semantic.sc $RT/qize.sc $RT/gen.sc \
  $RT/tdump.sc $RT/assign.sc $RT/parser_snobol4.sc < $BEAUTY > /tmp/p.txt 2>/dev/null
$SCRIP --dump-parse /tmp/beauty_noinc.sno > /tmp/o.txt 2>/dev/null
# normalize and compare with python3 STMT-block split (see session notes)
```

---

## Architecture

```
scrip --ir-run [blob] parser_snobol4.sc < input.sno   →  TDump tree lines
scrip --dump-parse input.sno                           →  oracle tree lines
```

Gate normalizes: collapse whitespace, strip ` )` → `)`. Shared blob:
`global.sc tree.sc stack.sc counter.sc ShiftReduce.sc semantic.sc qize.sc gen.sc tdump.sc assign.sc`

---

## Style guidelines (canonical home for all PARSER-* family)

### §1 Names match language spec
Pattern names mirror BNF + existing frontend's token/IR-tag enums. Operational oracle wins over spec.

### §2 White/Gray attached, never in main grammar
```
Gray  = White | epsilon;   $' '  = Gray;   $'  ' = White;
White = ( SPAN(' ' tab) FENCE(nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) | epsilon)
        | nl ('+' | '.') FENCE(SPAN(' ' tab) | epsilon) );
```
Exception: `*White` at 5 annotated sites in parser_snobol4.sc where column-sensitive grammar requires it.

### §3 `$'name'` tokens; `$' '`/`$'  '` for optional/required ws
Binary ops: `$' ' 'op' $' '`. Open bracket: `'(' $' '`. Close bracket: `$' ' ')'`.

### §4 shift/reduce for tree building; pair-shape for in-pattern actions
```
function push_foo() { Push(tree(E_FOO, val)); push_foo = .dummy; nreturn; }
function Push_foo() { Push_foo = epsilon . *push_foo(); return; }
```

### §5 n-ary: `nPush() ... nInc() ... reduce(TAG, 'nTop()') ... nPop()`
Pattern-producing functions — embed as patterns, not side-effect calls.

### §6 AST tags: `E_*` pre-quoted constants
SNOBOL4: `E_VAR E_ILIT E_QLIT E_RLIT E_FNC E_SEQ E_ALT E_LEN E_BREAK E_SPAN E_ANY E_NOTANY E_CAPT_COND_ASGN E_CAPT_IMMED_ASGN E_KEYWORD E_DEFER E_IDX E_ADD E_SUB E_MUL E_DIV E_POW E_PLS E_MNS E_FENCE E_ARBNO E_POS E_RPOS E_TAB E_RTAB E_BREAKX`  
Role-slots: `:lbl :subj :pat :repl :goS :goF :goU :eq :end`

### §7 Identifiers: lowercase_snake vars, UpperCamel patterns/functions, `$'...'` tokens, no `_`-prefix

### §8 Layout: 120-char max, no-brace single-stmt bodies, `//====`/`//----` dividers, no blank lines

### §9 Read beauty.sno and beauty.sc before authoring

---

## SNOBOL4 oracle tree shapes

| Construct | Oracle |
|-----------|--------|
| `x` | `(STMT :subj (E_VAR x))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `'hi'` | `(STMT :subj (E_QLIT "hi"))` |
| `END` col 0 | `(STMT :lbl END :end)` |
| `x = 5` | `(STMT :eq :subj (E_VAR x) :repl (E_ILIT 5))` |
| `S 'a'\|'b'` | `(STMT :subj (E_ALT (E_SEQ ...) ...))` (alt eats LHS) |
| `*Id` | `(E_DEFER (E_VAR Id))` |
| `&KW` | `(E_KEYWORD KW)` |
| `LEN(3)` | `(E_LEN (E_ILIT 3))` |
| `FENCE(p)` | `(E_FENCE ...)` |
| `ARBNO(p)` | `(E_ARBNO ...)` |
| `POS(n)` | `(E_POS (E_ILIT n))` |
| `RPOS(n)` | `(E_RPOS (E_ILIT n))` |
| blank line | `(STMT)` |

**`:subj`/`:pat` split:** if top is `E_SEQ` N≥2 → child 1 is `:subj`, rest is `:pat`. Else whole expr is `:subj`.  
**Precedence** (loose→tight): `|` < concat < `.$` < `^!**` < `*` < `/` < `+-` < unary < atom.

---

## Active rung: SN-7-8 — beauty.sno full crosscheck

**Goal:** `parser(beauty.sno)` ≡ `oracle(beauty_noinc.sno)` whitespace-normalized.

**This session landed (corpus@634d2bb):**
- `rw_call`: FENCE/ARBNO/POS/RPOS/TAB/RTAB/BREAKX → E_* primitives (was E_FNC)
- `tdump.sc` TLump_normal: 0-child typed nodes now bracket as `(STMT)` not bare `STMT`

**Current crosscheck state:**
- `parser(beauty.sno)`: 434 STMTs, 10 bare `(STMT)`  
- `oracle(beauty_noinc.sno)`: 433 STMTs, 9 bare `(STMT)`  
- Gap: **1 extra `(STMT)` in parser.** Root cause: beauty.sno line 25 is blank (between the 13 `-INCLUDE` Control lines and `&FULLSCAN`). Oracle with `-INCLUDE` expansion never sees that blank line as a visible STMT (the included file content occupies the slot). Our stdin parser sees it as a blank Control → blank Stmt → `(STMT)`. Fix: strip blank lines that immediately follow a run of Control lines, OR use `beauty_noinc.sno` as the stdin input (which has the `-INCLUDE` lines removed, so the blank line at line 25 of the original is now at a different position relative to Content).
- **Remaining structural mismatches after the 1-STMT realignment:** unknown — need to rerun with aligned inputs.

**Next steps:**
- [ ] Determine the right stdin input: feed `beauty_noinc.sno` to the parser instead of `beauty.sno` so that `-INCLUDE` Control lines (and their trailing blank) are absent. Gate oracle also uses `beauty_noinc.sno`.
- [ ] Run normalized STMT-block diff on aligned inputs; find remaining mismatches.
- [ ] Fix any remaining structural differences (check E_ASSIGN in pattern context, `:(ppEnd)` goto targets in beauty.sno main body — 9 STMTs in oracle come from pp* / main* section that parser currently doesn't reach because it stops at END).
- [ ] Add beauty crosscheck to `test_parser_snobol4.sh` or a new `test_parser_snobol4_beauty.sh`.
- [ ] Commit: `PARSER-SN-7-8: beauty.sno full crosscheck passes (PASS=N/N)`

**Key insight on the 9 missing STMTs:** oracle has 9 extra at the tail — these are `pp*`/`main*` function bodies and the final `END`. The parser currently stops when Compiland's END-consumer fires. beauty.sno's `:(ppEnd)` label causes the SNOBOL4 parser to skip to `ppEnd` — but our Compiland doesn't have that skip logic. The parser probably just runs off the end of the grammar section and stops early. Check: does `beauty_noinc.sno` have the same 9 extra at the tail in oracle?

**Gate:** `test_parser_snobol4.sh` PASS=78 (current) + beauty crosscheck 0 diff.

---

## PARSER-FAMILY-LOOP

All six parsers at 100%: SN=78 IC=88 PR=60 RK=37 SC=46 RB=38 corpus@634d2bb.

Next iteration candidates: iter#11 foldop cross-pollination (IC/PR/SC); FENCE sweep Phase E; CR-3..CR-5 Rebus RExpr cleanup.

| # | Concept | SN | IC | PR | RK | SC | RB | Commit |
|---|---------|----|----|----|----|----|----|--------|
| 1–10 | (see prior sessions) | 78 | 88 | 60 | 37 | 46 | 38 | corpus@634d2bb |

---

## Known runtime workarounds

- **FW-3** ARBNO deferred-call ✅ one4all@228bc06b  
- **INFRA-11a** `subj?pat` value context ✅ one4all@d2547945  
- **INFRA-11b** OPSYN `~`/`&` infix ⚠ needs re-probe  
- **INFRA-11c** `_qtag` auto-quoting ✅ corpus@c8ee2a6  
- **PARSER-SC FENCE/`*deref`** silent-fail ⚠ open (eval_pat.c E_FENCE)

---

## Closed rungs

INFRA-0..10, FW-1..3/6, SN-0..7-7c all ✅. See git history for detail.

---

## Watermark

**corpus@634d2bb** SN-7-8 partial. E_FENCE/ARBNO/POS/RPOS/TAB/RTAB/BREAKX primitives landed. tdump.sc 0-child bracket fix. Parser 434 vs oracle 433 — 1 extra (STMT) from blank line after -INCLUDE block. Next: feed beauty_noinc.sno to align inputs, diff, fix remaining gaps, land full crosscheck.
