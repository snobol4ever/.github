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

## Next rung: (open — see Deferred)

SN-7-8 LANDED. PARSER-FAMILY-LOOP closed by owner — no further cross-pollination iterations planned.

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
beauty.sno crosscheck: 433/433 STMTs, 0 mismatches. New ops: E_INDIRECT E_NAME E_ASSIGN E_NOT E_CAPT_CURSOR E_INTERROGATE E_OPSYN. reduce_opsyn()/ReduceOpsyn() added. subj/pat split guarded by E_VAR. goto ordering fixed. beauty_crosscheck in gate. 10 new fixtures. PARSER-FAMILY-LOOP closed by owner.
