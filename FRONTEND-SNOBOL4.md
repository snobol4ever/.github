# FRONTEND-SNOBOL4.md — SNOBOL4/SPITBOL Frontend (L3)

SNOBOL4 and SPITBOL are treated as a single frontend (SPITBOL is a SNOBOL4
superset with minor extensions). This frontend is implemented in all three repos.

*Implementation internals (sno2c) → IMPL-SNO2C.md. Testing protocol → TESTING.md.*
*Session state → TINY.md / JVM.md / DOTNET.md.*

---

## Status by Repo

| Repo | Implementation | Active sprint | Milestone |
|------|---------------|---------------|-----------|
| TINY | sno2c (C compiler) | `beauty-crosscheck` | M-BEAUTY-CORE |
| JVM | Clojure interpreter + JVM codegen | `jvm-inline-eval` | M-JVM-EVAL |
| DOTNET | C# interpreter + MSIL JIT | `net-delegates` | M-NET-DELEGATES |

---

## The Proof Program — beauty.sno

`beauty.sno` is the canonical correctness test for the SNOBOL4 frontend.
It is a self-contained SNOBOL4 parser and pretty-printer written in SNOBOL4.
If a backend can run `beauty.sno` self-beautification correctly, the SNOBOL4
frontend is correct on that backend.

**Self-beautification oracle test:**
```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle.sno
<backend-binary> < $BEAUTY > compiled.sno
diff oracle.sno compiled.sno   # empty = frontend correct on this backend
```

Key patterns/functions in beauty.sno (verified from corpus source):
- `Parse` / `Compiland` — top-level: `nPush() ARBNO(*Command) ("'Parse'" & nTop()) nPop()`
- `Command` — `nInc()` then FENCE(*Comment | *Control | *Stmt); one statement or directive
- `Stmt` — full statement: `*Label (*White *Expr14 FENCE(...) | ...) FENCE(*Goto | ...) *Gray`
- `Label` — `BREAK(' ' tab nl ';') ~ 'Label'`
- `Expr14` — subject expression (leftmost expr in a statement)
- `Goto` — `*Gray ':' *Gray FENCE(*Target ... | *SorF *Target ... | ...)`
- `pp(x)` — walk Shift/Reduce tree, emit beautified output
- `ss(x,len)` — measure flat width (lookahead for line-break decisions; called by pp)

**Seven Stmt children** (from Stmt pattern structure): Label, Expr14 (subject),
pattern-slot, `=` indicator, Expr (replacement), goto1, goto2.
`nInc()` called per Command; `nPush()`/`nPop()` bracket Parse/Compiland.

Includes 19 helper libraries via `-INCLUDE` from `SNOBOL4-corpus/programs/inc/`.

---

## Four-Paradigm TDD Protocol (TINY → M-BEAUTY-FULL)

| Sprint | Paradigm | Catches | Trigger |
|--------|----------|---------|---------|
| `beauty-crosscheck` | Crosscheck — diff vs oracle | Wrong output | beauty/140_self → **M-BEAUTY-CORE** |
| `beauty-probe` | Probe — &STLIMIT frame-by-frame | WHERE divergence first appears | All failures diagnosed |
| `beauty-monitor` | Monitor — TRACE double-trace | Deep recursion / call-return bugs | Trace streams match |
| `beauty-triangulate` | Triangulate — cross-engine | Edge cases, oracle quirks | Empty diff → **M-BEAUTY-FULL** |

---

## Rung 12 Test Format (TINY crosscheck)

Tests in `SNOBOL4-corpus/crosscheck/beauty/`:
- `NNN_name.input` — SNOBOL4 snippet piped into beauty_full_bin
- `NNN_name.ref` — oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN_name.input`

Runner: `SNOBOL4-tiny/test/crosscheck/run_beauty.sh` (pre-compiled binary).

Test progression (one at a time, never skip):
```
101_comment      * a comment
102_output           OUTPUT = 'hello'
103_assign           X = 'foo'
104_label        LOOP    X = X 1
105_goto             :(END)
109_multi        5-line program
120_real_prog    20-line program
130_inc_file     program using -INCLUDE
140_self         full beauty.sno → M-BEAUTY-CORE
```

Generate oracle: `snobol4 -f -P256k -I$INC $BEAUTY < NNN.input > NNN.ref`

---

## Probe Script (Paradigm 2)

```bash
python3 /home/claude/SNOBOL4-harness/probe/probe.py \
    --oracle csnobol4 --max 200 failing.sno
```
Probe targets: `pp`, `Command`, `Label`, `ss`, `pp_Parse`.
TRACE gotcha: `TRACE(...,'KEYWORD')` non-functional — use `TRACE('var','VALUE')`.
`&STCOUNT` broken in CSNOBOL4 (always 0) — use `&STLIMIT` binary search.

---

## Monitor Script (Paradigm 3)

Prepend to beauty.sno:
```snobol4
        TRACE('pp','CALL')    TRACE('pp','RETURN')
        TRACE('ss','CALL')    TRACE('ss','RETURN')
        TRACE('pp_Parse','CALL')  TRACE('Command','CALL')
```
```bash
snobol4 -f -P256k -I$INC beauty_trace.sno < input.sno 2>oracle_trace.txt
./beauty_full_bin_trace < input.sno 2>compiled_trace.txt
diff oracle_trace.txt compiled_trace.txt | head -20
```

---

## Triangulate Script (Paradigm 4 — M-BEAUTY-FULL trigger)

```bash
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle_csn.txt
./beauty_full_bin < $BEAUTY > compiled_out.txt
diff oracle_csn.txt compiled_out.txt   # empty = M-BEAUTY-FULL FIRES
```
SPITBOL excluded from full beauty.sno (error 021 at END).
Two oracles agree, compiled differs → our bug. Oracles disagree → check Gimpel §7.

---

## compiler.sno (post-M-BEAUTY-FULL bootstrap path)

`compiler.sno` = `beauty.sno` + `compile(x)` replacing `pp(x)`.
Same parse tree, same grammar (`Parse`/`Compiland`/`Stmt`/`Command`). Final action emits C Byrd boxes instead of SNOBOL4.
Proof: M-BEAUTY-FULL proves tree correct; `compile()` just walks it differently.

Architecture A (future): sprinkle emit actions into pattern alternations via
`epsilon . *action(...)` — like `iniParse` in `programs/inc/ini.sno`. Post-M-BOOTSTRAP.
