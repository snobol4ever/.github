# SESSION-snocone-beauty.md — Snocone × BEAUTY ramp-up

**Repo:** one4all + corpus · **Frontend:** Snocone · **Backend:** x86
**Session prefix:** `SCB` · **Trigger:** "snocone beauty" or "beauty ramp snocone"

---

## §OVERVIEW

Mirror the 19-subsystem BEAUTY ramp-up from SNOBOL4 (all ✅) but for Snocone.

**Key difference from SNOBOL4 BEAUTY:** The include library lives in
`corpus/programs/include/*.inc` and is written in SNOBOL4 syntax.
These must be converted to Snocone syntax (`.sc` files).
Converted files live in `corpus/programs/include-sc/` (new directory).
Drivers live in `one4all/test/beauty-sc/<subsystem>/`.

**Oracle strategy:** Each Snocone driver output must match the corresponding
SNOBOL4 driver output byte-for-byte. The SNOBOL4 `.ref` files in
`test/beauty/` double as the oracle for the Snocone drivers.

---

## §CONVERSION RULES — SNOBOL4 → Snocone

| SNOBOL4 | Snocone |
|---------|---------|
| `DEFINE('f(a,b)')` + label `f` + `:(RETURN)` skip | `procedure f(a, b) { ... return; }` |
| `:(RETURN)` | `return;` |
| `:(NRETURN)` | `nreturn;` |
| `:(FRETURN)` | `freturn;` |
| `:S(RETURN)F(FRETURN)` | `if (...) { return; } else { freturn; }` |
| `* comment` | `// comment` |
| `-INCLUDE 'foo.inc'` | source the .sc file inline in driver |
| `$name = expr` | `$name = expr;` (indirect assign — same) |
| `DATA('foo(f1,f2)')` | `struct foo { f1, f2 }` |
| `:(end_label)` skip-to-end | remove (use block structure) |
| `f = value :(NRETURN)` | `f = value; nreturn;` |
| Continuation lines (`+`) | single line with semicolons |

**Tricky patterns:**
- `$'#N'` indirect ref to symbol-named var — same in Snocone
- `.dummy` unevaluated result — same, Snocone supports `.`
- `do { } while (expr with fn call)` — known hang, workaround:
  rewrite as `while(1) { ...; if (!(cond)) break; }`

---

## §MILESTONE LADDER — M-SCB-*

| ID | Subsystem | .inc source | Depends on | Status |
|----|-----------|-------------|------------|--------|
| **M-SCB-ASSIGN** | assign.sc — conditional assignment in pattern | assign.inc | — | ❌ |
| **M-SCB-MATCH** | match.sc — match/notmatch | match.inc | — | ❌ |
| **M-SCB-IS** | is.sc — IsSnobol4/IsSpitbol predicates | is.inc | — | ❌ |
| **M-SCB-FENCE** | FENCE.sc — FENCE primitive wrapper | FENCE.inc | IS | ❌ |
| **M-SCB-GLOBAL** | global.sc — char constants, &ALPHABET | global.inc | — | ❌ |
| **M-SCB-CASE** | case.sc — UpperCase/LowerCase | case.inc | GLOBAL | ❌ |
| **M-SCB-COUNTER** | counter.sc — counter stack | counter.inc | — | ❌ |
| **M-SCB-STACK** | stack.sc — value stack | stack.inc | — | ❌ |
| **M-SCB-TREE** | tree.sc — DATA tree type | tree.inc | STACK | ❌ |
| **M-SCB-SR** | ShiftReduce.sc — Shift/Reduce | ShiftReduce.inc | TREE,COUNTER | ❌ |
| **M-SCB-TDUMP** | TDump.sc — tree pretty-printer | TDump.inc | TREE | ❌ |
| **M-SCB-IO** | io.sc — INPUT/OUTPUT OPSYN | io.inc | FENCE | ❌ |
| **M-SCB-GEN** | Gen.sc — code generation output | Gen.inc | IO | ❌ |
| **M-SCB-QIZE** | Qize.sc — quoting/unquoting | Qize.inc | GLOBAL | ❌ |
| **M-SCB-READWRITE** | ReadWrite.sc — buffered I/O | ReadWrite.inc | IO | ❌ |
| **M-SCB-XDUMP** | XDump.sc — extended dump | XDump.inc | TDUMP | ❌ |
| **M-SCB-SEMANTIC** | semantic.sc — semantic actions | semantic.inc | SR,GEN | ❌ |
| **M-SCB-OMEGA** | omega.sc — omega pattern helpers | omega.inc | SEMANTIC | ❌ |
| **M-SCB-TRACE** | trace.sc — xTrace helpers | trace.inc | — | ❌ |

**All 19 fire → M-SCB-SELFTEST: run beauty.sc (Snocone port of beauty.sno)**

---

## §BUILD

```bash
FRONTEND=snocone BACKEND=x64 TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
cd /home/claude/one4all
# Convert one subsystem and test:
CORPUS=/home/claude/corpus bash test/beauty-sc/run_beauty_sc_subsystem.sh assign
# Gates:
CORPUS=/home/claude/corpus bash test/run_emit_check.sh              # 1286/0
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 snocone_x86
```

---

## §FIRST ACTION — SCB-1

1. Create `corpus/programs/include-sc/` directory
2. Create `test/beauty-sc/run_beauty_sc_subsystem.sh` (mirrors run_beauty_subsystem.sh,
   uses `-sc -asm` pipeline, compares to SNOBOL4 `.ref` oracle)
3. Convert `assign.inc` → `assign.sc` (13 lines, simplest, no dependencies)
4. Write `test/beauty-sc/assign/driver.sc`
5. Run → fire M-SCB-ASSIGN

Recommended work order (simplest-first):
ASSIGN → MATCH → IS → FENCE → GLOBAL → CASE → COUNTER → STACK → TREE →
SR → TDUMP → IO → GEN → QIZE → READWRITE → XDUMP → SEMANTIC → OMEGA → TRACE

---

## §OPEN ISSUE FROM SC-14/SC-15

`do { } while (fn())` hangs in sc_compile_paren_expr — paren depth not tracked
for nested function call parens. Fix in SC-15 (Track A). Workaround in SCB
drivers: avoid do-while, use `while(1) { ...; if (!(cond)) break; }`.
