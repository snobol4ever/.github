# GRIDS.md — Comparison Tables (stubs — numbers TBD from official runs)

> **STATUS: ALL NUMBERS ARE PLACEHOLDERS.**
> These tables will be populated from three official milestone runs:
> - **M-GRID-BENCH** — benchmark grid: all engines timed against same programs via snobol4harness
> - **M-GRID-CORPUS** — corpus grid: all engines run against snobol4corpus crosscheck ladder
> - **M-GRID-COMPAT** — compatibility grid: feature/switch/behavior differences verified per engine
>
> Do not publish these tables until all three milestones have fired.
> Oracle for all runs: CSNOBOL4 2.3.3 (`snobol4 -f -P256k -I$INC file.sno`)

---

## Columns (all three grids)

| Abbreviation | Full name | Notes |
|---|---|---|
| **CSNOBOL4** | CSNOBOL4 2.3.3 (Phil Budne) | Reference oracle — C port of Macro SNOBOL4 |
| **SPITBOL** | SPITBOL x64 4.0f (Cheyenne Wills) | Native x64 compiler — speed reference |
| **dotnet** | snobol4dotnet (Jeffrey Cooper) | Full C# implementation, .NET 10, MSIL JIT |
| **jvm** | snobol4jvm (Lon Cherryholmes) | Full Clojure implementation, JVM bytecode |
| **x-net** | snobol4x / .NET backend | TINY compiler, CIL output |
| **x-jvm** | snobol4x / JVM backend | TINY compiler, Jasmin/JVM output |
| **x-asm** | snobol4x / x86-64 ASM backend | TINY compiler, NASM output |

---

## Grid 1 — Benchmarks

> Source programs: `snobol4corpus/benchmarks/`
> Runner: `snobol4harness/` — all engines, same input, wall-clock time
> Machine: TBD (specify CPU, RAM, OS, date of run)
> Units: milliseconds unless noted. `—` = not yet run. `DNF` = did not finish / error.

| Program | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|---:|---:|---:|---:|---:|---:|---:|
| roman.sno (roman numeral conversion) | — | — | — | — | — | — | — |
| wordcount.sno (word frequency count) | — | — | — | — | — | — | — |
| fibonacci_18 (recursion depth ~21k calls) | — | — | — | — | — | — | — |
| arith_loop_1000 (tight counter loop) | — | — | — | — | — | — | — |
| beauty.sno self-beautify (full 801-line program) | — | — | — | — | — | — | — |
| pcre_compare: `(a\|b)*abb` (normal pattern) | — | — | — | — | — | — | — |
| pcre_compare: `(a+)+b` len=28 (pathological) | — | — | — | — | — | — | — |
| cfg_compare: `{a^n b^n}` n=100 | — | — | — | — | — | — | — |

**Notes (fill in at M-GRID-BENCH):**
- PCRE2 JIT baseline for comparison: TBD
- Bison LALR(1) baseline for comparison: TBD
- Process-spawn overhead for CSNOBOL4/SPITBOL: ~15ms (subtract for fair comparison)

---

## Grid 2 — Corpus Ladder

> Source: `snobol4corpus/crosscheck/` — 106 programs across 11 rungs + rung 12 (beauty)
> Pass = output byte-for-byte matches CSNOBOL4 oracle `.ref` file
> `—` = not yet run. Numbers = passing / total.

| Rung | What it tests | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 — hello/output | Basic output | oracle | — | — | — | — | — | — |
| 2 — assign | Variable assignment | oracle | — | — | — | — | — | — |
| 3 — concat | String concatenation | oracle | — | — | — | — | — | — |
| 4 — arith | Arithmetic | oracle | — | — | — | — | — | — |
| 5 — control | GOTO / :S() / :F() | oracle | — | — | — | — | — | — |
| 6 — patterns | LIT/ANY/SPAN/BREAK/ARB/ARBNO/etc | oracle | — | — | — | — | — | — |
| 7 — capture | `.` and `$` operators | oracle | — | — | — | — | — | — |
| 8 — strings | SIZE/SUBSTR/REPLACE/DUPL | oracle | — | — | — | — | — | — |
| 9 — keywords | IDENT/DIFFER/GT/LT/EQ/DATATYPE | oracle | — | — | — | — | — | — |
| 10 — functions | DEFINE/RETURN/FRETURN/recursion | oracle | — | — | — | — | — | — |
| 11 — data | ARRAY/TABLE/DATA types | oracle | — | — | — | — | — | — |
| 12 — beauty.sno | Self-beautification (full program) | oracle | — | — | — | — | — | — |
| **TOTAL** | | **oracle** | **—/106** | **—/106** | **—/106** | **—/106** | **—/106** | **—/106** |

---

## Grid 3 — Feature / Compatibility Matrix

> Behavior verified against CSNOBOL4 2.3.3 oracle.
> `✅` = supported and correct  `⚠` = partial or differs from oracle  `❌` = not supported  `—` = not yet tested
> When CSNOBOL4 and SPITBOL differ, the SPITBOL column notes the divergence.

### Core Language

| Feature | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Labeled statements | ✅ | ✅ | — | — | — | — | — |
| Subject / pattern / replacement | ✅ | ✅ | — | — | — | — | — |
| Conditional GOTO :S() :F() | ✅ | ✅ | — | — | — | — | — |
| Unconditional GOTO :() | ✅ | ✅ | — | — | — | — | — |
| String literals / concatenation | ✅ | ✅ | — | — | — | — | — |
| Integer arithmetic | ✅ | ✅ | — | — | — | — | — |
| Real arithmetic | ✅ | ✅ | — | — | — | — | — |
| Indirect reference `$var` | ✅ | ✅ | — | — | — | — | — |
| DEFINE / user functions | ✅ | ✅ | — | — | — | — | — |
| RETURN / FRETURN / NRETURN | ✅ | ✅ | — | — | — | — | — |
| Recursive functions | ✅ | ✅ | — | — | — | — | — |
| APPLY(fn, args) | ✅ | ✅ | — | — | — | — | — |
| ARRAY(dims, fill) | ✅ | ✅ | — | — | — | — | — |
| TABLE(size) | ✅ | ✅ | — | — | — | — | — |
| DATA('type(fields)') / FIELD | ✅ | ✅ | — | — | — | — | — |
| EVAL(expr) | ✅ | ✅ | — | — | — | — | — |
| CODE(source) | ✅ | ✅ | — | — | — | — | — |
| OPSYN | ✅ | ✅ | — | — | — | — | — |
| -INCLUDE preprocessor | ✅ | ✅ | — | — | — | — | — |

### Pattern Primitives

| Pattern | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| LIT (string literal) | ✅ | ✅ | — | — | — | — | — |
| ANY(s) | ✅ | ✅ | — | — | — | — | — |
| NOTANY(s) | ✅ | ✅ | — | — | — | — | — |
| SPAN(s) | ✅ | ✅ | — | — | — | — | — |
| BREAK(s) | ✅ | ✅ | — | — | — | — | — |
| BREAKX(s) | ✅ | ✅ | — | — | — | — | — |
| ARB | ✅ | ✅ | — | — | — | — | — |
| ARBNO(p) | ✅ | ✅ | — | — | — | — | — |
| BAL | ✅ | ✅ | — | — | — | — | — |
| LEN(n) | ✅ | ✅ | — | — | — | — | — |
| POS(n) | ✅ | ✅ | — | — | — | — | — |
| RPOS(n) | ✅ | ✅ | — | — | — | — | — |
| TAB(n) | ✅ | ✅ | — | — | — | — | — |
| RTAB(n) | ✅ | ✅ | — | — | — | — | — |
| REM | ✅ | ✅ | — | — | — | — | — |
| FENCE | ✅ | ✅ | — | — | — | — | — |
| FENCE(p) | ✅ | ✅ | — | — | — | — | — |
| ABORT | ✅ | ✅ | — | — | — | — | — |
| FAIL | ✅ | ✅ | — | — | — | — | — |
| SUCCEED | ✅ | ✅ | — | — | — | — | — |
| Cond. assign `.` | ✅ | ✅ | — | — | — | — | — |
| Immediate assign `$` | ✅ | ✅ | — | — | — | — | — |
| Cursor capture `@N` | ✅ | ✅ | — | — | — | — | — |
| Named ref `*var` | ✅ | ✅ | — | — | — | — | — |

### Keywords and I/O

| Feature | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| &STLIMIT / &STCOUNT | ✅ | ✅ | — | — | — | — | — |
| &ANCHOR / &FULLSCAN | ✅ | ✅ | — | — | — | — | — |
| &DUMP | ✅ | ✅ | — | — | — | — | — |
| &TRACE / &FTRACE | ✅ | ✅ | — | — | — | — | — |
| &ALPHABET | ✅ | ✅ | — | — | — | — | — |
| &UCASE / &LCASE | ✅ | ✅ | — | — | — | — | — |
| TRACE() / STOPTR() | ✅ | ✅ | — | — | — | — | — |
| DUMP() | ✅ | ✅ | — | — | — | — | — |
| INPUT() / OUTPUT() named channels | ✅ | ✅ | — | — | — | — | — |
| LOAD() external functions | ✅ | ✅ | — | — | — | — | — |
| UNLOAD() | ✅ | ✅ | — | — | — | — | — |

### Known Divergences (CSNOBOL4 vs SPITBOL)

> Fill in at M-GRID-COMPAT. These are known divergences from the literature and from snobol4ever session notes.

| Behavior | CSNOBOL4 | SPITBOL | Notes |
|---|---|---|---|
| `@N` cursor value | 1-based? | 0-based | SPITBOL MINIMAL wins per snobol4ever rule |
| DATATYPE() of builtins | Uppercase? | Lowercase | TBD — verify |
| DATATYPE() of user DATA types | Uppercase | ToLowerInvariant | SPITBOL MINIMAL wins |
| `beauty.sno` END statement | Runs clean | Error 021 | Indirect function call semantic difference |
| `&UCASE` / `&LCASE` scope | TBD | Exactly 26 ASCII letters | TBD |

---

*GRIDS.md is a stub. All `—` cells require M-GRID-BENCH, M-GRID-CORPUS, and M-GRID-COMPAT to fire.*
*These milestones are defined in PLAN.md.*

---

## Grid 4 — Language Reference (functions, keywords, switches)

> **STATUS: STUB — all cells require M-GRID-REFERENCE to fire.**
> This is the fine-grained complement to Grid 3.
> Grid 3 groups features by category. Grid 4 lists every individual builtin,
> keyword, and CLI switch, with a quality rating per engine.
>
> Rating scale:
> - `✅` fully supported, oracle-correct
> - `⚠` supported but diverges from oracle in known edge cases (note appended)
> - `🔧` partial — basic cases work, known gaps
> - `❌` not implemented
> - `—` not applicable to this engine

### Builtin Functions (~50)

| Function | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| APPLY(fn, args…) | ✅ | ✅ | — | — | — | — | — |
| ARRAY(dims, fill) | ✅ | ✅ | — | — | — | — | — |
| CHAR(n) | ✅ | ✅ | — | — | — | — | — |
| CODE(source) | ✅ | ✅ | — | — | — | — | — |
| CONVERT(val, type) | ✅ | ✅ | — | — | — | — | — |
| COPY(val) | ✅ | ✅ | — | — | — | — | — |
| DATA('type(fields)') | ✅ | ✅ | — | — | — | — | — |
| DATATYPE(val) | ✅ | ⚠ lowercase builtins | — | — | — | — | — |
| DATE() | ✅ | ✅ | — | — | — | — | — |
| DEFINE('proto', 'entry') | ✅ | ✅ | — | — | — | — | — |
| DIFFER(a, b) | ✅ | ✅ | — | — | — | — | — |
| DUMP(n) | ✅ | ✅ | — | — | — | — | — |
| DUPL(s, n) | ✅ | ✅ | — | — | — | — | — |
| EQ(a, b) | ✅ | ✅ | — | — | — | — | — |
| EVAL(expr) | ✅ | ✅ | — | — | — | — | — |
| FIELD(type, n) | ✅ | ✅ | — | — | — | — | — |
| GE(a, b) | ✅ | ✅ | — | — | — | — | — |
| GT(a, b) | ✅ | ✅ | — | — | — | — | — |
| HOST(n, …) | ✅ | ✅ | — | — | — | — | — |
| IDENT(a, b) | ✅ | ✅ | — | — | — | — | — |
| INPUT(var, ch, file) | ✅ | ✅ | — | — | — | — | — |
| INTEGER(val) | ✅ | ✅ | — | — | — | — | — |
| ITEM(arr, i…) | ✅ | ✅ | — | — | — | — | — |
| LE(a, b) | ✅ | ✅ | — | — | — | — | — |
| LGT(a, b) | ✅ | ✅ | — | — | — | — | — |
| LOAD('proto', 'lib') | ✅ | ✅ | — | — | — | — | — |
| LOCAL(fn, n) | ✅ | ✅ | — | — | — | — | — |
| LPAD(s, n, fill) | ✅ | ✅ | — | — | — | — | — |
| LTRIM(s) | ✅ | ✅ | — | — | — | — | — |
| LT(a, b) | ✅ | ✅ | — | — | — | — | — |
| NE(a, b) | ✅ | ✅ | — | — | — | — | — |
| OPSYN(new, old, n) | ✅ | ✅ | — | — | — | — | — |
| OUTPUT(var, ch, file) | ✅ | ✅ | — | — | — | — | — |
| REAL(val) | ✅ | ✅ | — | — | — | — | — |
| REMDR(a, b) | ✅ | ✅ | — | — | — | — | — |
| REPLACE(s, from, to) | ✅ | ✅ | — | — | — | — | — |
| REVERSE(s) | ✅ | ✅ | — | — | — | — | — |
| RPAD(s, n, fill) | ✅ | ✅ | — | — | — | — | — |
| RTRIM(s) | ✅ | ✅ | — | — | — | — | — |
| SETEXIT('label') | ✅ | ✅ | — | — | — | — | — |
| SIZE(s) | ✅ | ✅ | — | — | — | — | — |
| STOPTR(var, type) | ✅ | ✅ | — | — | — | — | — |
| SUBSTR(s, i, n) | ✅ | ✅ | — | — | — | — | — |
| TABLE(size, fill) | ✅ | ✅ | — | — | — | — | — |
| TERMINAL | ✅ | ✅ | — | — | — | — | — |
| TIME() | ✅ | ✅ | — | — | — | — | — |
| TRACE(var, type) | ✅ | ✅ | — | — | — | — | — |
| TRIM(s) | ✅ | ✅ | — | — | — | — | — |
| UNLOAD(fn) | ✅ | ✅ | — | — | — | — | — |

### Keywords (~30)

| Keyword | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| &ALPHABET | ✅ | ✅ | — | — | — | — | — |
| &ANCHOR | ✅ | ✅ | — | — | — | — | — |
| &CODE | ✅ | ✅ | — | — | — | — | — |
| &DUMP | ✅ | ✅ | — | — | — | — | — |
| &ERRLIMIT | ✅ | ✅ | — | — | — | — | — |
| &ERRTEXT | ✅ | ✅ | — | — | — | — | — |
| &ERRTYPE | ✅ | ✅ | — | — | — | — | — |
| &FTRACE | ✅ | ✅ | — | — | — | — | — |
| &FULLSCAN | ✅ | ✅ | — | — | — | — | — |
| &INPUT | ✅ | ✅ | — | — | — | — | — |
| &LCASE | ✅ | ⚠ 26 ASCII only | — | — | — | — | — |
| &LASTNO | ✅ | ✅ | — | — | — | — | — |
| &MAXLNGTH | ✅ | ✅ | — | — | — | — | — |
| &OUTPUT | ✅ | ✅ | — | — | — | — | — |
| &STCOUNT | ✅ | ✅ | — | — | — | — | — |
| &STLIMIT | ✅ | ✅ | — | — | — | — | — |
| &SUBJECT | ✅ | ✅ | — | — | — | — | — |
| &TRACE | ✅ | ✅ | — | — | — | — | — |
| &TRIM | ✅ | ✅ | — | — | — | — | — |
| &UCASE | ✅ | ⚠ 26 ASCII only | — | — | — | — | — |

### CLI Switches

> Switch sets differ per engine. Only switches meaningful across engines are listed here.
> Engine-specific switches (e.g. dotnet -w save-dll, SPITBOL -b) are documented in individual repo READMEs.

| Switch / behaviour | CSNOBOL4 | SPITBOL | dotnet | jvm | x-net | x-jvm | x-asm |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Run a .sno file | ✅ | ✅ | — | — | — | — | — |
| -f (don't fold to uppercase) | ✅ | ✅ | — | — | — | — | — |
| -F (fold to uppercase, default) | ✅ | ✅ | — | — | — | — | — |
| -b (suppress sign-on) | — | ✅ | — | — | — | — | — |
| -l (show listing) | ✅ | ✅ | — | — | — | — | — |
| -n (compile only, no execution) | ✅ | ✅ | — | — | — | — | — |
| -I dir (-include search path) | ✅ | ✅ | — | — | — | — | — |
| -P n (stack/heap size) | ✅ | — | — | — | — | — | — |
| -r (INPUT reads lines after END) | ✅ | ✅ | — | — | — | — | — |
| -w (write save/dll file) | — | ✅ | — | — | — | — | — |
| -x (execution statistics) | ✅ | ✅ | — | — | — | — | — |
| Save file / .dll reload | — | ✅ | — | — | — | — | — |
| SNOLIB / SNOPATH env var | ✅ | ✅ | — | — | — | — | — |

---

*Grid 4 is a stub. All `—` cells require M-GRID-REFERENCE to fire.*
*Milestone definition: every `—` cell replaced by ✅/⚠/🔧/❌ from actual test runs via snobol4harness.*
*The CSNOBOL4 and SPITBOL columns are pre-filled from documentation and known behaviour; verify against oracle before publishing.*
