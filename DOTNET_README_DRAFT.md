# snobol4dotnet

**Full SNOBOL4/SPITBOL compiler and runtime for .NET — C#, Windows, Linux, macOS**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![.NET](https://img.shields.io/badge/.NET-10-512BD4)](https://dotnet.microsoft.com)
[![Tests](https://img.shields.io/badge/tests-1911%20passing-brightgreen)](https://github.com/snobol4ever/snobol4dotnet)

---

## What This Is

snobol4dotnet is a complete, production-quality implementation of SNOBOL4 and SPITBOL — not a subset, not a research prototype. It covers the full SPITBOL language: every built-in function, every keyword, every data type, named I/O channels, the `-INCLUDE` preprocessor, `TRACE`/`STOPTR`, and `CODE()` / `EVAL()` / `OPSYN`. It runs on Windows, Linux, and macOS. **1,911 tests passing.**

Built by Jeffrey Cooper, M.D. — a physician who spent fifty years implementing SNOBOL4 out of pure love for the language. When he called Lon Jones Cherryholmes to say he had a complete implementation, two fifty-year journeys collided. The result is this repository.

---

## How It Works

The compiler pipeline runs in three stages.

**Parse → threaded code → optional MSIL.**  
The lexer and parser produce an AST. The code builder lowers that AST to an `Instruction[]` thread — a flat array of tagged opcodes and operands, one entry per SNOBOL4 statement. Execution is a tight `ThreadedExecuteLoop.cs` dispatch: a loop over the thread array with a switch on `OpCode`. For hot paths, the MSIL delegate JIT compiles statement sequences to `Func<Executive,int>[]` chains — zero switch overhead on the critical loop.

```
SNOBOL4 source
      │
      ▼
Lexer + Parser (Token.cs, Lexer.cs, Parser.cs)
      │
      ▼
Builder (Builder.cs)  →  Instruction[]  →  ThreadedExecuteLoop.cs
                          │
                          ▼
                     BuilderEmitMsil.cs  →  Func<Executive,int>[]  (hot path JIT)
```

**Pattern matching** is handled by `Scanner.cs` using an `AbstractSyntaxTreeNode` graph. Each pattern primitive is its own class — `LiteralPattern`, `ArbNoPattern`, `AnyPattern`, `PosPattern`, etc. The scanner runs an outer unanchored loop over cursor positions. Each terminal node's `Scan()` method either advances the cursor (SUCCESS), triggers backtrack (FAILURE), or propagates immediately (ABORT). The same four-state model — proceed, recede, succeed, concede — that underlies every other snobol4ever backend.

---

## The Architecture Jump — From Roslyn to Threaded Code

The original snobol4dotnet used Roslyn to JIT-compile hot statements to C# at runtime. It worked. It was also 96ms on a roman-numerals benchmark that should have taken 7ms.

The rewrite replaced Roslyn with a hand-crafted threaded interpreter and a focused MSIL delegate JIT. The result:

| Benchmark | Roslyn (before) | Threaded + MSIL (after) | Speedup |
|-----------|----------------:|------------------------:|--------:|
| Roman numerals | 96 ms | 7 ms | **13.7×** |
| Pattern scan | 40 ms | 4 ms | **10.3×** |
| String concat (500) | 3.0 ms | 0.4 ms | **−87%** |
| Function call overhead (3000) | 8.2 ms | 5.0 ms | **−39%** |

This is the headline number: **13.7× faster** after the threaded rewrite. Not a different algorithm — the same SNOBOL4 programs, now running through a dispatch loop that knows what it is doing.

---

## The Plugin System — SPITBOL LOAD() on .NET

snobol4dotnet implements the full SPITBOL external function protocol: `LOAD()` / `UNLOAD()`, `XNBLK` opaque persistent state, and the C-ABI calling convention used by SPITBOL x32. This means C shared libraries written for SPITBOL work with snobol4dotnet — the same `.so` or `.dll` that SPITBOL loads, loaded here.

Beyond C, .NET assembly extensions work natively. You can write a SNOBOL4 extension in C#, F#, or VB.NET, load it at runtime via `LOAD()`, and call it from SNOBOL4 with full type marshalling. A VB.NET test fixture ships with the repo. The Windows GUI runner ships alongside the command-line tool.

```snobol
*  Load a .NET extension and call it from SNOBOL4
        LOAD('MYFUNCTION(STRING)STRING', 'MyExtension.dll')
        RESULT = MYFUNCTION('hello')
        OUTPUT = RESULT
END
```

---

## What's Implemented

Full SNOBOL4/SPITBOL — every feature the language defines.

| Category | What |
|----------|------|
| Execution | GOTO-driven labeled-statement execution; conditional `:S()` / `:F()` routing |
| Patterns | LIT, ANY, NOTANY, SPAN, BREAK, BREAKX, ARB, ARBNO, FENCE, ABORT, BAL, CONJ, POS, RPOS, TAB, RTAB, REM, cursor capture (`@`) |
| Functions | DEFINE / RETURN / FRETURN / NRETURN; recursive functions; APPLY; OPSYN |
| Data types | STRING, INTEGER, REAL, PATTERN, ARRAY, TABLE, DATA/FIELD, CODE, NAME |
| CODE() | Dynamic compilation of SNOBOL4 source at runtime |
| EVAL() | Expression evaluation in string context |
| I/O | Named channels (`INPUT(N)`, `OUTPUT(N)`); TERMINAL; file I/O |
| Preprocessor | `-INCLUDE` for multi-file programs |
| Debugging | TRACE / STOPTR with all standard trace types |
| Plugins | LOAD / UNLOAD; C-ABI `.so`/`.dll`; .NET assembly extensions; XNBLK; VB.NET |
| CLI | All SPITBOL command-line switches (`-e`, `-m`, `-b`, size suffixes) |
| Platforms | Windows, Linux, macOS via .NET 10 |

**Currently excluded (known gaps):**

| Issue | Status |
|-------|--------|
| `Pattern.Bal` — hangs under threaded execution | Medium priority |
| `pos(*A)` deferred expressions (TEST_Pos_009) | Low priority |
| `CODE()` dynamic GOTO (TestGoto_DIRECT) | Medium priority |
| `Function.InputOutput` on Linux (hardcoded Windows paths) | Low priority |

---

## Test Suite

```bash
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true
```

**1,911 passing. 2 skipped (platform-specific).**

The suite covers every layer of the stack:

| Group | Coverage |
|-------|----------|
| ThreadedCompilerTests | Compile pipeline: every AST node type |
| ThreadedExecutionTests | Runtime: all opcodes, branching, functions |
| Numeric (95 tests) | Integer + real arithmetic, conversions |
| Pattern tests | All pattern primitives; complex compositions |
| Gimpel library | Griswold & Gimpel standard SNOBOL4 functions |
| Arrays + Tables | All access patterns, resize, copy |
| StringComparison | LGT / IDENT / DIFFER exhaustive |
| LOAD/UNLOAD | Plugin lifecycle, C-ABI, XNBLK, .NET assembly |
| MSIL emitter (Steps 1–13) | Generated delegate correctness |
| TRACE hooks | All TRACE types verified end-to-end |
| Snocone parser | Andrew Koenig's structured frontend |
| SPITBOL switches | 26 CLI option unit tests |

### Test count history

From first committed test suite to today:

| Milestone | Tests |
|-----------|------:|
| `master` (Roslyn) | 1,271 |
| Threaded execution | 1,386 |
| Post-threaded-dev | 1,413 |
| MSIL emitter merged | 1,484 |
| All merged to `main` | 1,466 |
| Snocone parser (Step 2) | 1,607 |
| SPITBOL switches (D-163) | **1,911** |

---

## Build

**.NET 10 required.**

```bash
# Clone
git clone https://github.com/snobol4ever/snobol4dotnet
cd snobol4dotnet

# Build (Linux / macOS — EnableWindowsTargeting required for Windows-targeting code)
dotnet build -c Release -p:EnableWindowsTargeting=true

# Test
dotnet test TestSnobol4/TestSnobol4.csproj -c Release -p:EnableWindowsTargeting=true

# Run a SNOBOL4 program
dotnet run --project Snobol4/Snobol4.csproj -c Release -- myprogram.sno
```

On Linux, the .NET 10 SDK must be on your PATH:
```bash
export PATH=/usr/local/dotnet10:$PATH
```

---

## Quick Example

```snobol
*  Classic SNOBOL4: extract words from a sentence
        SENTENCE = "the quick brown fox"
        WORD     = SPAN(&LCASE)
LOOP    SENTENCE WORD . W =              :F(DONE)
        OUTPUT   = W                     :(LOOP)
DONE
END
```

Output:
```
the
quick
brown
fox
```

Patterns in SNOBOL4 are not regular expressions. `SPAN(&LCASE)` matches one or more lowercase letters and **removes the matched text from** `SENTENCE` via the `=` replacement. The loop runs until the match fails — no counter, no index, no explicit iteration. Just pattern, replacement, goto.

---

## Conformance

snobol4dotnet takes *MACRO SPITBOL* (Emmer & Quillen) as its specification, with Griswold, Poage & Polonsky's *The SNOBOL4 Programming Language* as the base reference. When CSNOBOL4 and SPITBOL MINIMAL diverge, SPITBOL MINIMAL wins.

CSNOBOL4 2.3.3 (Phil Budne) and SPITBOL x64 4.0f (Cheyenne Wills) serve as conformance oracles. The shared `snobol4corpus` crosscheck ladder (106 programs, 11 rungs + `beauty.sno`) is the acceptance test. Current status: **79/80** (one known failure: `@N` cursor capture when match position > 0 — fix in progress, sprint `net-polish`).

---

## The Snocone Frontend

snobol4dotnet includes a parser for Snocone — Andrew Koenig's structured C-like preprocessor for SNOBOL4, described in Bell Labs Computing Science Technical Report #124 (1986). Snocone programs look like C but compile to SNOBOL4. The parser lives in `SnoconeParser.cs` (shunting-yard expression parser) with 35 dedicated tests.

```snocone
/* Snocone — structured syntax, SNOBOL4 semantics */
define fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
output = fibonacci(10);
```

---

## Part of snobol4ever

snobol4dotnet is one implementation in the [snobol4ever](https://github.com/snobol4ever) compiler matrix — a project building SNOBOL4 everywhere: the JVM, .NET, and native x86-64, from shared frontends and a shared IR. The same `snobol4corpus` crosscheck ladder runs against every backend. The same oracle — CSNOBOL4 2.3.3 — validates every output.

The five-way monitor (in progress) will run the same SNOBOL4 programs through CSNOBOL4, SPITBOL/x64, and all three snobol4x compiled backends simultaneously, comparing trace streams event-by-event. snobol4dotnet provides the `.NET MSIL` output path for the snobol4x compiler; the monitor will close the loop.

---

## Authors

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — original author, architect, runtime, compiler, pattern engine, plugin system, MSIL emitter, Windows GUI, VB.NET fixture, 50 years in the making.

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — snobol4ever org, integration, corpus, cross-platform CI, SPITBOL conformance testing.

---

## License

MIT. See [LICENSE](LICENSE).

---

*Part of [snobol4ever](https://github.com/snobol4ever) — snobol4all. snobol4now. snobol4ever.*
