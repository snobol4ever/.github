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
- `+expr` (unary plus / numeric coerce) returns `''` in snocone x86 — drop it or use `INTEGER()`
- Cond-assign idiom `val = GT(a,b) expr` → rewrite as `if (GT(a,b)) { val = expr; }`
- Subject replacement `str pat =` not available — use SUBSTR/SIZE index walk
- `~(strval)` unreliable as empty check — use `GT(i, SIZE(arr))` for loop bounds
- Loop termination on SORT array: use `n = SIZE(arr); while GT(i,n)` not empty-sentinel

**Policy (SC-16+): IS and FENCE stubs dropped**
- `IsSpitbol()` / `IsSnobol4()` / `IsType()` — NOT included in any Snocone driver.
  one4all targets SPITBOL semantics exclusively; no runtime dialect detection needed.
- `FENCE` — builtin in snocone x86 (0-arg and 1-arg pattern forms). No stub .sc needed.
  `FENCE.sc` is empty. Drivers never include is.sc or FENCE.sc.
- All `.inc` guards like `IsSnobol4() :F(end)` are converted as unconditional in .sc.

---

## §MILESTONE LADDER — M-SCB-*

| ID | Subsystem | .inc source | Depends on | Status |
|----|-----------|-------------|------------|--------|
| **M-SCB-ASSIGN** | assign.sc | assign.inc | — | ✅ |
| **M-SCB-MATCH** | match.sc | match.inc | — | ✅ |
| ~~M-SCB-IS~~ | *(dropped)* | — | — | ⛔ N/A |
| **M-SCB-FENCE** | FENCE.sc (empty — builtin) | FENCE.inc | — | ✅ |
| **M-SCB-GLOBAL** | global.sc | global.inc | — | ✅ |
| **M-SCB-CASE** | case.sc | case.inc | GLOBAL | ⏭ dynamic |
| **M-SCB-COUNTER** | counter.sc | counter.inc | — | ✅ |
| **M-SCB-STACK** | stack.sc | stack.inc | — | ✅ |
| **M-SCB-TREE** | tree.sc | tree.inc | STACK | ✅ |
| **M-SCB-SR** | ShiftReduce.sc | ShiftReduce.inc | TREE,STACK | ❌ |
| **M-SCB-TDUMP** | TDump.sc | TDump.inc | TREE,GEN | ⏭ dynamic |
| **M-SCB-IO** | io.sc | io.inc | — | ❌ |
| **M-SCB-GEN** | Gen.sc | Gen.inc | IO | ❌ |
| **M-SCB-QIZE** | Qize.sc | Qize.inc | GLOBAL | ⏭ dynamic |
| **M-SCB-READWRITE** | ReadWrite.sc | ReadWrite.inc | GLOBAL | ❌ |
| **M-SCB-XDUMP** | XDump.sc | XDump.inc | TDUMP,QIZE | ⏭ dynamic |
| **M-SCB-SEMANTIC** | semantic.sc | semantic.inc | SR,COUNTER | ❌ |
| **M-SCB-OMEGA** | omega.sc | omega.inc | SR,QIZE,CASE... | ⏭ dynamic |
| **M-SCB-TRACE** | trace.sc | trace.inc | — | ✅ |

**All non-dynamic fire → M-SCB-SELFTEST: run beauty.sc**

---

## §BUILD

```bash
FRONTEND=snocone BACKEND=x64 TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/beauty-sc/run_beauty_sc_subsystem.sh assign match global counter stack tree trace
CORPUS=/home/claude/corpus bash test/run_emit_check.sh              # 1286/0
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 snocone_x86
```

---

## §OPEN ISSUES

`do { } while (fn())` hangs in sc_compile_paren_expr — paren depth not tracked
for nested function call parens. Workaround: use `while(1) { ...; if (!(cond)) break; }`.
