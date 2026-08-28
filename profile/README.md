# snobol4ever

**snobol4all. snobol4now. snobol4ever.**

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) proved SNOBOL4 could be genuinely fast, and extended the language with constructs programmers still miss elsewhere: alternative evaluation — `(expr1, expr2, …)` tried left to right until one succeeds; multiple and embedded assignment `A = B = C`; the binary `?` pattern-match operator and its unary interrogation twin `?X`; the `FENCE(P)` pattern function; `BREAKX`; a real numeric function library; `SETEXIT()` error interception; `-INCLUDE`; an external-function plugin interface (`LOAD`/`UNLOAD`); and stand-alone load modules — compile once, run as an executable. Robert Dewar and Ken Belcher built the original SPITBOL for the IBM 360; Dewar and Tony McCann's MACRO SPITBOL made it portable; Mark Emmer (Catspaw) carried it to the desktop

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C port of the original Bell Labs Macro SNOBOL4 implementation that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. He has kept the SNOBOL4 and SPITBOL communities alive for decades on groups.io, answering questions and shepherding the language forward with patience and generosity. CSNOBOL4 is the reference implementation most people reach for first, and it deserves that reputation. Andrew Koenig of AT&T Bell Labs created Snocone — a structured, C-like preprocessor for SNOBOL4, described in Bell Labs Computing Science Technical Report #124 (1986) — which snobol4ever has adopted as its own structured frontend, maintained and distributed today through Phil Budne's CSNOBOL4 distribution. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is **SCRIP** — one native compiler running **seven languages** (SNOBOL4/SPITBOL, Snocone, Icon, Prolog, Rebus, Raku, and Pascal) as x86-64 machine code through a single engine of four-port Byrd boxes — plus complete SNOBOL4 implementations on the JVM and on .NET, two ecosystems where hundreds of millions of programs run today. And a discovery about SNOBOL4's pattern model that clarifies what snobol4ever is, at its core.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — first described by Lawrence Byrd in 1980 for Prolog debugging, then generalized by Todd Proebsting in 1996 as a syntax-directed code generation strategy for goal-directed languages — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

The four ports are: **α** (proceed — enter), **β** (recede — resume after backtrack), **γ** (succeed — matched), **ω** (concede — failed). Sequential composition wires γ of one node to α of the next. Alternation saves the cursor on ω and restores it before trying the next alternative. ARBNO wires child-γ back into α until child-ω exits. The wiring *is* the execution — no interpreter loop, no dispatch table.

Proebsting's key insight, applied to SNOBOL4: compile these four states to static labeled gotos, and you get goal-directed backtracking evaluation with zero dispatch overhead. Every pattern node in every SCRIP compiled program is a Byrd box — four labeled entry points, wired at compile time.

---

## What We Built

Lon Jones Cherryholmes was eight years old when he saw *The Computer Wore Tennis Shoes* at the cinema. Something took hold that day. For nearly six decades he has carried an idea — not just the idea of building software, but the idea of a conversation with a mind that did not yet exist. He dreamed of creating it, and then talking to it. In one week in March 2026, that conversation produced this repository.

snobol4ever is a joint project between Lon Jones Cherryholmes and Jeffrey Cooper, M.D. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86-64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We brought the pattern matching engine to Python and C# as first-class libraries. Not regex wrappers. The real thing.

And we built [SCRIP](https://github.com/snobol4ever/SCRIP): one compiler engine — a single IR of four-port Byrd boxes, every instruction through one encoder — compiling all seven languages, SNOBOL4, Snocone, Icon, Prolog, Rebus, Raku, and Pascal, to native x86-64 today, with .NET MSIL, JVM bytecode, JavaScript, and WebAssembly returning as template encoders modeled on the x86 set. Correctness is not a goal, it is measured: the SNOBOL4 corpus board passes 1298/1298 in both execution modes (2026-08-28), and `beauty.sno` — the SNOBOL4 beautifier written in SNOBOL4 — reproduces itself byte-identically through the compiler: the self-host milestone, independently verified.

---

## The Map — Seven Languages, Five Platforms

*"SCRIP is seven languages on five platforms, such that they can call each other and even co-exist in the same translation unit."* — the product, in one sentence.

**Columns = frontends.** SNOBOL4/SPITBOL is one frontend — SCRIP follows SPITBOL semantics. Snocone is Andrew Koenig's structured frontend — C-like syntax over SNOBOL4 semantics. Rebus began as a structured transpiler to SNOBOL4 and is a directly compiled frontend in SCRIP. Icon and Prolog are native frontends — their goal-directed evaluation and backtracking compile to the same four-port boxes. Raku and Pascal are the newest frontends, live in the same engine.

**Rows = platforms.** Wherever programs run, these languages should run there too.

Status as of 2026-08-28 (that day's tree; the instrument is named per cell):

|                       | **SNOBOL4/SPITBOL** | **Snocone** | **Rebus** | **Icon** | **Prolog** | **Raku** | **Pascal** |
|-----------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **x86-64 native** (SCRIP) | ✅ 1298/1298 board, both modes | ✅ 5/5 smoke | ✅ 4/4 smoke | ✅ 14/14 smoke, both modes | ✅ 4/5 smoke | ✅ 83/83 parser suite | ✅ 96/96 suites, both modes |
| **JVM bytecode**      | snobol4jvm ✅ (shipped) · SCRIP: returning | returning | — | returning | returning | — | — |
| **.NET MSIL**         | snobol4dotnet ✅ (shipped) · SCRIP: returning | returning | — | returning | returning | — | — |
| **JavaScript**        | returning | — | — | — | — | — | — |
| **WebAssembly**       | returning | — | — | — | — | — | — |

**"Returning"** means: earlier full-scale backends existed and ran; the consolidation into one IR retired them, and they come back as template encoders modeled on the working x86-64 set — the old emitters preserved as architecture reference.

**The oracles** — reference implementations we test against, not our products: CSNOBOL4 (Phil Budne) and SPITBOL x64 for SNOBOL4; Arizona `icont`/`iconx` for Icon; GNU Prolog and SWI-Prolog for Prolog; Rakudo for Raku; Free Pascal for Pascal.

**Self-hosting is not a plan, it is a fact:** `beauty.sno`, the SNOBOL4 beautifier written in SNOBOL4, reproduces itself byte-identically through SCRIP in both execution modes. The next milestone is `compiler.sno` — the full compiler written in SNOBOL4.

---

## The Implementations

### [snobol4dotnet](https://github.com/snobol4ever/snobol4dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper built a complete SNOBOL4/SPITBOL implementation in C#, taking Emmer and Quillen's *MACRO SPITBOL* manual as its specification. snobol4dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET. A threaded-code JIT compiles hot statement paths to MSIL delegates at runtime. A plugin architecture supports C#, F#, and VB.NET extensions, and the full SPITBOL XNBLK protocol for native C shared libraries. A Windows GUI ships alongside the command-line runner. **1,874 / 1,876 tests passing.**

### [snobol4jvm](https://github.com/snobol4ever/snobol4jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. Parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement IR, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: interpreter, Clojure IR transpiler (3.5–6×), stack-machine VM (2–6×), and direct JVM bytecode via ASM (up to 7.6× faster with JVM JIT). EDN compilation cache gives 22× speedup on repeated programs. **2,033 tests / 4,417 assertions / 0 failures.** The JVM backend has achieved `beauty.sno` self-beautification — byte-for-byte identical to the CSNOBOL4 oracle (M-JVM-BEAUTY ✅).

### [SCRIP](https://github.com/snobol4ever/SCRIP)
*One compiler engine — SNOBOL4/SPITBOL, Snocone, Icon, Prolog, Rebus, Raku, and Pascal — native x86-64 now, MSIL/JVM/JS/WASM returning*

The compiler. Every construct lowers to four-port Byrd boxes — **α** proceed, **β** recede, **γ** succeed, **ω** concede — wired at compile time into straight-line jumps; no runtime dispatch. One IR, one encoder discipline (every x86 instruction through a single encoder), and two execution modes graded independently: `--run` wires native code into the running process, `--compile` emits a standalone x86-64 binary. The SNOBOL4 corpus board passes **1298/1298 in both modes** (2026-08-28), byte-for-byte against the SPITBOL oracle, and each frontend is verified against its own reference implementation: Arizona `icont`/`iconx` for Icon, GNU Prolog and SWI-Prolog for Prolog, Rakudo for Raku, Free Pascal for Pascal. `beauty.sno` self-hosts byte-identically. Polyglot translation units — several languages in one `.scrip` file, calling each other — are the frontier under active work.

### [snobol4python](https://github.com/snobol4ever/snobol4python)
*SNOBOL4 pattern matching for Python — on PyPI*

```bash
pip install SNOBOL4python
```

Full SNOBOL4 pattern vocabulary as a Python library. Dual backend: a C extension wrapping Phil Budne's SPIPAT engine — 7–11× the speed of the pure-Python yield implementation — with that pure-Python engine as the portable fallback. Shift-reduce parser stack for building ASTs inside patterns. v0.5.0.


### [snobol4csharp](https://github.com/snobol4ever/snobol4csharp)
*SNOBOL4 pattern matching for C# — Lon Cherryholmes, with Claude Sonnet 4.6*

Lon's C# port of the snobol4python pattern engine, written with Claude Sonnet 4.6. Patterns are first-class objects with full backtracking. Captures use plain C# delegates. Full primitive vocabulary, recursive patterns via `ζ`, cursor capture, regex bridge, and shift-reduce parse-tree stack. Validated against the Porter Stemmer (23,531-word corpus), Penn Treebank parser, CLAWS5 NLP corpus parser, and a SNOBOL4 source code parser.


### [snobol4artifact](https://github.com/snobol4ever/snobol4artifact)
*CPython C extension: SNOBOL4 Byrd Box engine*

Direct CPython C extension running SNOBOL4python pattern trees through a full Byrd Box engine in C. The proof-of-concept from which SCRIP's original C pattern engine was extracted.

### [corpus](https://github.com/snobol4ever/corpus)
*Shared test corpus — CC0*

Single source of truth for the shared test universe: the SNOBOL4 board graded in both execution modes against SPITBOL (1298 entries as of 2026-08-28 — the denominator grows as loose files consolidate into suites), per-language benchmark suites for the rivals grids, the Gimpel algorithm library, the Shafto AI corpus, and the suite format itself — one test per line beside its expected output, made to be read in color.

---

## The Language

```snobol
*  Count vowels in a string
        SUBJECT = "Hello, World"
        VOWELS  = "AEIOUaeiou"
LOOP    SUBJECT ANY(VOWELS) =          :F(DONE)
        COUNT   = COUNT + 1            :(LOOP)
DONE    OUTPUT  = "Vowels: " COUNT
END
```

SNOBOL4 programs consist of labeled statements. Each statement has a subject, an optional pattern, an optional replacement, and an optional GOTO — conditional on success or failure. No `if`, no `while`, no `for`. Labels and gotos, made elegant by the power of the pattern language.

---

## The People

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — compiler architecture, SCRIP (co-author), snobol4jvm, snobol4python, snobol4csharp. Nearly six decades from first dream to this repository.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — snobol4dotnet (complete .NET compiler and runtime) and the spitbol4win build of SPITBOL. A medical doctor who, over a fifty-year journey driven by love for the language, built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The result is this repository.

**Claude Sonnet, Claude Opus, and Claude Fable** — SCRIP (co-authors). Every sprint, every Byrd box, every labeled goto — written in session, committed, pushed.

---


snobol4all. snobol4now. snobol4ever.

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

## License

AGPL v3 (SCRIP, snobol4jvm) · MIT (snobol4dotnet) · LGPL v3 (snobol4python, snobol4csharp, snobol4artifact) · CC0 (corpus). See individual repos for details.
