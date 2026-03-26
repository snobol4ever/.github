# ARCH-grids.md — Comparison Tables

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

---

## Grid 5 — Startup Benchmark (cold / warm)

> **STATUS: STUB — requires M-GRID-STARTUP to fire.**
> Startup latency matters for scripting use. Cold = first invoke after reboot. Warm = second invoke, same binary.
> Units: milliseconds. Machine spec: TBD. `—` = not yet run.

| Program | CS4 cold | CS4 warm | SPIT cold | SPIT warm | dotnet cold | dotnet warm | jvm cold | jvm warm | x-asm cold | x-asm warm | x-jvm cold | x-jvm warm | x-net cold | x-net warm |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| null.sno (zero work) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| hello.sno (one OUTPUT) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| roman.sno (real work) | — | — | — | — | — | — | — | — | — | — | — | — | — | — |

**Interpretation guide:** x-asm cold ≈ CSNOBOL4 cold (no JVM/CLR spin-up). jvm/dotnet cold includes JIT compile overhead.
Warm numbers show steady-state scripting cost.

---

## Grid 6 — Operator Coverage

> **STATUS: STUB — requires M-GRID-OPERATOR to fire.**
> SNOBOL5 column filled from documentation only (not a live run). All other columns from harness.
> Rating: ✅ correct · ⚠ partial/diverges · 🔧 skeleton · ❌ missing · — N/A

### Arithmetic and Numeric Relational

| Operator | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `+` `-` `*` `/` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `**` (exponentiation) | ✅ | ✅ | ✅ | — | — | — | — | — |
| `REMDR(a,b)` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `-` unary negation | ✅ | ✅ | ✅ | — | — | — | — | — |
| `EQ NE LT LE GT GE` | ✅ | ✅ | ✅ | — | — | — | — | — |
| `IDENT DIFFER LGT` | ✅ | ✅ | ✅ | — | — | — | — | — |

### Pattern Operators

| Operator | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Concatenation (juxtaposition) | ✅ | ✅ | ✅ | — | — | — | — | — |
| `\|` alternation | ✅ | ✅ | ✅ | — | — | — | — | — |
| `~` complement (SPITBOL ext.) | ❌ | ✅ | — | — | — | — | — | — |
| `.` conditional assign | ✅ | ✅ | ✅ | — | — | — | — | — |
| `$` immediate assign | ✅ | ✅ | ✅ | — | — | — | — | — |
| `@N` cursor capture | ✅ | ✅ | ✅ | — | — | — | — | — |
| `*var` unevaluated / named ref | ✅ | ✅ | ✅ | — | — | — | — | — |

### Indirect Reference and Other

| Operator | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `$expr` indirect reference | ✅ | ✅ | ✅ | — | — | — | — | — |
| OPSYN user-defined operators | ✅ | ✅ | ⚠ | — | — | — | — | — |
| Operator precedence (standard) | ✅ | ✅ | ✅ | — | — | — | — | — |

---

## Grid 7 — Source Volume (per-repo)

> **STATUS: STUB — populated when M-VOL-{repo} fires.**
> Categories are **logical function**, comparable across all repos regardless of implementation language.
> Numbers from `wc -l` on checked-out source. Generated artifacts excluded.

### snobol4x ✅ M-VOL-X 2026-03-22

| Category | Files | Lines | Blank-stripped | % total |
|----------|------:|------:|:--------------:|--------:|
| Parser / lexer | 20 | 6,368 | 5,728 | 20.5% |
| Code emitter | 11 | 17,291 | 15,936 | 55.6% |
| Pattern engine | 10 | 1,588 | 1,421 | 5.1% |
| Runtime / builtins | 7 | 4,614 | 4,120 | 14.8% |
| Driver / CLI | 1 | 140 | 128 | 0.5% |
| Extensions / plugins | 3 | 1,085 | 969 | 3.5% |
| Tests | 47 | 6,265 | 5,495 | — |
| Benchmarks | 12 | 1,603 | 1,541 | — |
| Docs / Markdown | 2 | 1,080 | 814 | — |
| **Total (src)** | **54** | **31,090** | **28,306** | **100%** |

### snobol4jvm ✅ M-VOL-JVM 2026-03-22

| Category | Files | Lines | Blank-stripped | % total |
|----------|------:|------:|:--------------:|--------:|
| Parser / lexer | 5 | 926 | 847 | 12.8% |
| Code emitter | 3 | 1,402 | 1,236 | 19.4% |
| Pattern engine | 5 | 921 | 833 | 12.8% |
| Runtime / builtins | 7 | 2,140 | 1,999 | 29.6% |
| Driver / CLI | 2 | 234 | 221 | 3.2% |
| Extensions / plugins | 2 | 29 | 29 | 0.4% |
| Tests | 55 | 19,352 | 17,159 | — |
| Benchmarks | 1 | 152 | 133 | — |
| Docs / Markdown | 2 | 456 | 353 | — |
| **Total (src)** | **28** | **7,220** | **6,562** | **100%** |

### snobol4dotnet ✅ M-VOL-DOTNET 2026-03-22

| Category | Files | Lines | Blank-stripped | % total |
|----------|------:|------:|:--------------:|--------:|
| Parser / lexer | 8 | 3,681 | 3,206 | 16.6% |
| Code emitter | 13 | 2,825 | 2,484 | 12.7% |
| Pattern engine | 33 | 2,260 | 1,701 | 10.2% |
| Runtime / builtins | 201 | 11,938 | 9,909 | 53.7% |
| Driver / CLI | 12 | 1,040 | 915 | 4.7% |
| Extensions / plugins | 7 | 548 | 476 | 2.5% |
| Tests | 160 | 28,008 | 25,102 | — |
| Benchmarks | 5 | 474 | 435 | — |
| Docs / Markdown | 5 | 668 | 471 | — |
| **Total (src)** | **272** | **22,212** | **18,626** | **100%** |

## Grid 8 — Feature Completeness (per-repo)

> **STATUS: STUB — requires M-FEAT-{repo} to fire.**
> Rating: ✅ complete · ⚠ partial · 🔧 skeleton · ❌ missing · — N/A for this repo type

| Feature Area | snobol4x | snobol4jvm | snobol4dotnet | snobol4python | snobol4csharp |
|-------------|:---:|:---:|:---:|:---:|:---:|
| Core language (labels, GOTO, subject/pat/repl) | — | — | — | — | — |
| String operations (SUBSTR/REPLACE/DUPL/etc) | — | — | — | — | — |
| Numeric operations + integer/real types | — | — | — | — | — |
| Pattern primitives (all ~25) | — | — | — | — | — |
| Capture operators (`.` `$` `@`) | — | — | — | — | — |
| Built-in functions (n / ~50 total) | — | — | — | — | — |
| Keywords / &-vars (n / ~30 total) | — | — | — | — | — |
| DATA / ARRAY / TABLE types | — | — | — | — | — |
| User-defined functions + recursion | — | — | — | — | — |
| I/O — INPUT/OUTPUT named channels | — | — | — | — | — |
| I/O — file I/O (DETACH, multi-channel) | — | — | — | — | — |
| LOAD / UNLOAD external functions | — | — | — | — | — |
| EVAL / CODE (dynamic compilation) | — | — | — | — | — |
| OPSYN (operator synonyms) | — | — | — | — | — |
| TRACE / DUMP / debugging support | — | — | — | — | — |
| CLI switches (n / total engine-specific) | — | — | — | — | — |
| INCLUDE preprocessing | — | — | — | — | — |
| Error handling (&ERRLIMIT, SETEXIT) | — | — | — | — | — |
| Real number support | — | — | — | — | — |
| Unicode / &ALPHABET beyond ASCII-26 | — | — | — | — | — |

---

## Grid 9 — CLI Switches (full, all engines)

> **STATUS: STUB — requires M-GRID-SWITCH-FULL to fire.**
> Extends Grid 4 CLI section with all engine-specific switches.
> `✅` supported · `⚠` partial · `❌` not supported · `—` N/A for this engine

| Switch | Description | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|--------|-------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Run `.sno` file | Basic invocation | ✅ | ✅ | ✅ | — | — | — | — | — |
| `-f` | Don't fold identifiers to uppercase | ✅ | ✅ | ✅ | — | — | — | — | — |
| `-F` | Fold identifiers to uppercase (default) | ✅ | ✅ | — | — | — | — | — | — |
| `-b` | Suppress sign-on banner | — | ✅ | — | — | — | — | — | — |
| `-l` | Show source listing | ✅ | ✅ | — | — | — | — | — | — |
| `-n` | Compile only, no execution | ✅ | ✅ | — | — | — | — | — | — |
| `-I dir` | Include search path | ✅ | ✅ | ✅ | — | — | — | — | — |
| `-P n` | Stack/heap size | ✅ | — | — | — | — | — | — | — |
| `-r` | INPUT reads lines after END statement | ✅ | ✅ | — | — | — | — | — | — |
| `-x` | Execution statistics | ✅ | ✅ | — | — | — | — | — | — |
| `-w` | Write save/DLL file | — | ✅ | — | — | — | — | — | — |
| Save file / DLL reload | Persist compiled form | — | ✅ | — | — | — | — | — | — |
| `-asm` | Emit x64 ASM (NASM) output | — | — | — | — | — | ✅ | — | — |
| `-jvm` | Emit JVM bytecode output | — | — | — | — | — | — | ✅ | — |
| `-net` | Emit .NET CIL output | — | — | — | — | — | — | — | ✅ |
| `-sc` | Use Snocone frontend | — | — | — | — | — | ✅ | ✅ | ✅ |
| Engine-specific (TBD from source) | various | — | — | — | — | — | — | — | — |
| SNOLIB / SNOPATH env var | Library search | ✅ | ✅ | ✅ | — | — | — | — | — |

*Additional engine-specific switches documented in each repo README.*

---

## Grid 10 — Program Keywords / &-variables (full, all engines)

> **STATUS: STUB — requires M-GRID-REFERENCE to fire.**
> Complete list of all SNOBOL4/SPITBOL program keywords (&-variables).
> Standalone grid split from Grid 4 for the README v2 sprint.
> Three comparison columns (CSNOBOL4 · SPITBOL · SNOBOL5) + seven engine columns.
> Rating: `✅` fully supported · `⚠` partial or diverges from oracle · `🔧` skeleton · `❌` not implemented · `—` N/A
> SNOBOL5 column filled from documentation, not live runs.

| Keyword | Read/Write | CSNOBOL4 | SPITBOL | SNOBOL5 | dotnet | jvm | x-asm | x-jvm | x-net |
|---------|:----------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| &ALPHABET | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &ANCHOR | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &CODE | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &DUMP | R/W | ✅ | ✅ | — | — | — | — | — | — |
| &ERRLIMIT | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &ERRTEXT | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &ERRTYPE | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &FTRACE | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &FULLSCAN | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &INPUT | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &LCASE | R | ✅ | ⚠ 26 ASCII | ✅ | — | — | — | — | — |
| &LASTNO | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &MAXLNGTH | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &OUTPUT | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &STCOUNT | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &STLIMIT | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &SUBJECT | R | ✅ | ✅ | ✅ | — | — | — | — | — |
| &TRACE | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &TRIM | R/W | ✅ | ✅ | ✅ | — | — | — | — | — |
| &UCASE | R | ✅ | ⚠ 26 ASCII | ✅ | — | — | — | — | — |
| &ABEND (SPITBOL ext.) | R/W | ❌ | ✅ | — | — | — | — | — | — |
| &CASE (SPITBOL ext.) | R/W | ❌ | ✅ | — | — | — | — | — | — |
| &LINE (SPITBOL ext.) | R | — | ✅ | — | — | — | — | — | — |
| &FILE (SPITBOL ext.) | R | — | ✅ | — | — | — | — | — | — |
| &NARGS (SPITBOL ext.) | R | — | ✅ | — | — | — | — | — | — |
| &VERSION | R | ✅ | ✅ | ✅ | — | — | — | — | — |

**Notes:**
- CSNOBOL4 and SPITBOL columns pre-filled from documentation; verify against oracle at M-GRID-REFERENCE.
- SNOBOL5 column from SNOBOL5 language reference; no live run.
- SPITBOL extensions (`&ABEND`, `&CASE`, `&LINE`, `&FILE`, `&NARGS`) are SPITBOL-only; not in CSNOBOL4 by design.
- `&LCASE` / `&UCASE` divergence: CSNOBOL4 uses full locale alphabet; SPITBOL uses exactly the 26 ASCII letters.
- `&TRIM` semantics: trailing blanks stripped from INPUT when non-zero.

---

*GRIDS.md updated 2026-03-22. Grids 5–9 added for README v2 sprint. Grid 10 added to complete the 10-grid taxonomy.*
*All `—` cells require their respective milestones (see PLAN.md §README v2 — Grid Sprint).*
