# snobol4ever

**snobol4all. snobol4now. snobol4ever.**

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) proved SNOBOL4 could be genuinely fast, and extended the language with constructs programmers still miss elsewhere: alternative evaluation — `(expr1, expr2, …)` tried left to right until one succeeds; multiple and embedded assignment `A = B = C`; the binary `?` pattern-match operator and its unary interrogation twin `?X`; the `FENCE(P)` pattern function; `BREAKX`; a real numeric function library; `SETEXIT()` error interception; `-INCLUDE`; an external-function plugin interface (`LOAD`/`UNLOAD`); and stand-alone load modules — compile once, run as an executable. Robert Dewar and Ken Belcher built the original SPITBOL for the IBM 360; Dewar and Tony McCann's MACRO SPITBOL made it portable; Mark Emmer (Catspaw) carried it to the desktop

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C port of the original Bell Labs Macro SNOBOL4 implementation that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. He has kept the SNOBOL4 and SPITBOL communities alive for decades on groups.io, answering questions and shepherding the language forward with patience and generosity. CSNOBOL4 is the reference implementation most people reach for first, and it deserves that reputation. Andrew Koenig of AT&T Bell Labs created Snocone — a structured, C-like preprocessor for SNOBOL4, described in Bell Labs Computing Science Technical Report #124 (1986) — which snobol4ever has adopted as its own structured frontend, maintained and distributed today through Phil Budne's CSNOBOL4 distribution. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition: **complete, modern homes for SNOBOL4 — everywhere, not just on x86-64 Unix.** A full SNOBOL4/SPITBOL compiler and runtime on **.NET**, another on the **JVM** — two ecosystems where hundreds of millions of programs run today — a special SPITBOL build for Windows, first-class pattern-matching libraries for Python and C#, and a native compiler that runs seven languages through one engine. Full implementations, not stubs — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

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

## The Implementations

### [snobol4dotnet](https://github.com/snobol4ever/snobol4dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper built a complete SNOBOL4/SPITBOL implementation in C#, taking Emmer and Quillen's *MACRO SPITBOL* manual as its specification. snobol4dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET. A threaded-code JIT compiles hot statement paths to MSIL delegates at runtime. A plugin architecture supports C#, F#, and VB.NET extensions, and the full SPITBOL XNBLK protocol for native C shared libraries. A Windows GUI ships alongside the command-line runner. **1,874 / 1,876 tests passing.**

Alongside it, Jeffrey maintains **spitbol4win** — a special build of SPITBOL for Windows, bringing the classic native implementation to the platform where most desktops live.

### [snobol4jvm](https://github.com/snobol4ever/snobol4jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. Parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement IR, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: interpreter, Clojure IR transpiler (3.5–6×), stack-machine VM (2–6×), and direct JVM bytecode via ASM (up to 7.6× faster with JVM JIT). EDN compilation cache gives 22× speedup on repeated programs. **2,033 tests / 4,417 assertions / 0 failures.** The JVM backend has achieved `beauty.sno` self-beautification — byte-for-byte identical to the CSNOBOL4 oracle (M-JVM-BEAUTY ✅).

### [corpus](https://github.com/snobol4ever/corpus)
*The shared program universe — libraries, tests, and interesting programs — CC0*

The corpus is two things at once. It is the home of the **include/import libraries** — the shared `-INCLUDE` and import-able SNOBOL4 code that every implementation in this organization draws on — and it is the home of **interesting programs**: the Gimpel algorithm library, the Shafto AI corpus, classic and newly written SNOBOL4/SPITBOL programs, and per-language benchmark and demo suites. **Submissions are welcome** — if you have written a SNOBOL4 program worth reading, this is where it belongs, beside the test universe that keeps it running forever: the SNOBOL4 board graded in both execution modes against SPITBOL (1,299 entries as of 2026-08-28 — the denominator grows as loose files consolidate into suites), in a suite format of one test per line beside its expected output, made to be read in color.

### The pattern libraries

[**snobol4python**](https://github.com/snobol4ever/snobol4python) brings the full SNOBOL4 pattern vocabulary to Python as a first-class library (`pip install SNOBOL4python`) — not a regex wrapper, the real thing, with a C extension backend at 7–11× the pure-Python engine. [**snobol4csharp**](https://github.com/snobol4ever/snobol4csharp) is Lon's C# port of the same engine: patterns as first-class objects with full backtracking, validated against the Porter Stemmer, Penn Treebank, and CLAWS5 corpora.

---

## The Story

In 2012, Jeff Cooper emailed Lon Cherryholmes. They knew each other the way SNOBOL people knew each other — from the community bulletin boards and mailing lists that kept a great language alive through the lean decades. Jeff mentioned he was writing SNOBOL4 in C#. Lon never got the chance to join him, and the thread went quiet — for fourteen years.

In March 2021, Lon spent a few weeks implementing a subset of SNOBOL4 in Clojure — played with it, proved the shape, set it down (the first commit of what would become snobol4jvm is dated March 5, 2021).

In March 2026, Jeff called. He had an implementation — a real one, complete, the work of years. Lon promised to help. **Two days later**, working with Claude Sonnet 4.6, Jeff's implementation was running **twenty times faster**. Then Lon thought: resurrect mine. **One day later**, the 2021 Clojure subset had become snobol4jvm — a full implementation.

And then came the thought that would not stop, each idea pulling the next one in:

*Maybe now we can write a portable bootstrap compiler in SNOBOL4. Or better — in Snocone. A SNOBOL4/Snocone compiler, written in Snocone. But Icon and Prolog are goal-directed-evaluation languages — the same machine underneath — so bring them in. And Rebus belongs, for history's sake. And we need a common 3GL and a modern scripting language: Pascal, and Raku. Call it SCRIP — **S**nobol4 · sno**C**one · **R**aku/**R**ebus · **I**con · **P**rolog/**P**ascal. What if they could link and call each other seamlessly? What if they could co-exist in the same file — SCRIPtix: triple-backtick blocks in any Markdown file, compiled and run, all languages simultaneously? What if we go further — expression embedding, pure language code-switching mid-program? What if it runs everywhere?*

The repository born that March was named **one4all**. On May 31, 2026 it was reborn as **SCRIP**. The destination is visible from here: a form of Jupyter notebook in which every code cell speaks any SCRIP language — the SCRIPtix feature delivered through interactive Python notebooks (`.ipynb`) — seven languages, one engine, anywhere and everywhere.

---

## The People

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — **architect of SCRIP**: the seven-language vision, the Byrd-box engine, the platform roadmap — and author of snobol4jvm, snobol4python, and snobol4csharp. Nearly six decades from first dream to this repository.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — snobol4dotnet (complete .NET compiler and runtime) and the spitbol4win build of SPITBOL. A medical doctor who, over a fifty-year journey driven by love for the language, built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The result is this repository.

**Claude Sonnet, Claude Opus, and Claude Fable** — SCRIP (co-authors). Every sprint, every Byrd box, every labeled goto — written in session, committed, pushed.

---

## [SCRIP](https://github.com/snobol4ever/SCRIP)
*One compiler engine — SNOBOL4/SPITBOL, Snocone, Icon, Prolog, Rebus, Raku, and Pascal — native x86-64 now, MSIL/JVM/JS/WASM returning*

The compiler. Every construct lowers to four-port Byrd boxes — **α** proceed, **β** recede, **γ** succeed, **ω** concede — wired at compile time into straight-line jumps; no runtime dispatch. One IR, one encoder discipline (every x86 instruction through a single encoder), and two execution modes graded independently: `--run` wires native code into the running process, `--compile` emits a standalone x86-64 binary. The SNOBOL4 corpus board passes **1299/1299 in both modes** (2026-08-28), byte-for-byte against the SPITBOL oracle, and each frontend is verified against its own reference implementation: Arizona `icont`/`iconx` for Icon, GNU Prolog and SWI-Prolog for Prolog, Rakudo for Raku, Free Pascal for Pascal. `beauty.sno` self-hosts byte-identically. Polyglot translation units — several languages in one `.scrip` file, calling each other — are the frontier under active work.

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — first described by Lawrence Byrd in 1980 for Prolog debugging, then generalized by Todd Proebsting in 1996 as a syntax-directed code generation strategy for goal-directed languages — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

The four ports are: **α** (proceed — enter), **β** (recede — resume after backtrack), **γ** (succeed — matched), **ω** (concede — failed). Sequential composition wires γ of one node to α of the next. Alternation saves the cursor on ω and restores it before trying the next alternative. ARBNO wires child-γ back into α until child-ω exits. The wiring *is* the execution — no interpreter loop, no dispatch table.

Proebsting's key insight, applied to SNOBOL4: compile these four states to static labeled gotos, and you get goal-directed backtracking evaluation with zero dispatch overhead. Every pattern node in every SCRIP compiled program is a Byrd box — four labeled entry points, wired at compile time.

---

## The Map — Seven Languages, Five Platforms

*"SCRIP is seven languages on five platforms, such that they can call each other and even co-exist in the same translation unit."* — the product, in one sentence.

**Columns = frontends.** SNOBOL4/SPITBOL is one frontend — SCRIP follows SPITBOL semantics. Snocone is Andrew Koenig's structured frontend — C-like syntax over SNOBOL4 semantics. Rebus began as a structured transpiler to SNOBOL4 and is a directly compiled frontend in SCRIP. Icon and Prolog are native frontends — their goal-directed evaluation and backtracking compile to the same four-port boxes. Raku and Pascal are the newest frontends, live in the same engine.

**Rows = platforms.** Wherever programs run, these languages should run there too.

Status as of 2026-08-28 (that day's tree; the instrument is named per cell):

|                       | **SNOBOL4/SPITBOL** | **Snocone** | **Rebus** | **Icon** | **Prolog** | **Raku** | **Pascal** |
|-----------------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **x86-64 native** (SCRIP) | ✅ 1299/1299 board, both modes | ✅ 5/5 smoke | ✅ 4/4 smoke | ✅ 14/14 smoke, both modes | ✅ 4/5 smoke | ✅ 83/83 parser suite | ✅ 96/96 suites, both modes |
| **JVM bytecode**      | snobol4jvm ✅ (shipped) · SCRIP: returning | returning | — | returning | returning | — | — |
| **.NET MSIL**         | snobol4dotnet ✅ (shipped) · SCRIP: returning | returning | — | returning | returning | — | — |
| **JavaScript**        | returning | — | — | — | — | — | — |
| **WebAssembly**       | returning | — | — | — | — | — | — |

**"Returning"** means: earlier full-scale backends existed and ran; the consolidation into one IR retired them, and they come back as template encoders modeled on the working x86-64 set — the old emitters preserved as architecture reference.

**The oracles** — reference implementations we test against, not our products: CSNOBOL4 (Phil Budne) and SPITBOL x64 for SNOBOL4; Arizona `icont`/`iconx` for Icon; GNU Prolog and SWI-Prolog for Prolog; Rakudo for Raku; Free Pascal for Pascal.

**Self-hosting is not a plan, it is a fact:** `beauty.sno`, the SNOBOL4 beautifier written in SNOBOL4, reproduces itself byte-identically through SCRIP in both execution modes. The next milestone is `compiler.sno` — the full compiler written in SNOBOL4.

---

snobol4all. snobol4now. snobol4ever.

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

## License

AGPL v3 (SCRIP, snobol4jvm) · MIT (snobol4dotnet) · LGPL v3 (snobol4python, snobol4csharp) · CC0 (corpus). See individual repos for details.
