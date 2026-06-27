# snobol4ever

**snobol4all. snobol4now. snobol4ever.**

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type — a concept so powerful that every language since has been trying to catch up. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) extended the language further — structured programming constructs, an external function plugin architecture, and a compiler that proved SNOBOL4 could be genuinely fast. Robert Dewar and Tony McCann built the original SPITBOL compiler; Mark Emmer took over that work in 1987 and maintained it for nearly a quarter century through Catspaw, Inc., producing commercial implementations for DOS, Macintosh, Windows, Sun, and Unix. Dave Shields carried the torch from 2009, putting SPITBOL on GitHub and porting it to modern Linux and macOS. Today Cheyenne Wills maintains the actively developed x86-64 branch.

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C port of the original Bell Labs Macro SNOBOL4 implementation that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. He has kept the SNOBOL4 and SPITBOL communities alive for decades on groups.io, answering questions and shepherding the language forward with patience and generosity. CSNOBOL4 is the reference implementation most people reach for first, and it deserves that reputation. Andrew Koenig of AT&T Bell Labs created Snocone — a structured, C-like preprocessor for SNOBOL4, described in Bell Labs Computing Science Technical Report #124 (1986) — which snobol4ever has adopted as its own structured frontend, maintained and distributed today through Phil Budne's CSNOBOL4 distribution. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is SNOBOL4 on the JVM and on .NET — two ecosystems where hundreds of millions of programs run today — plus a native compiler targeting x86-64 ASM, JVM bytecode, and .NET MSIL simultaneously from a single intermediate representation. And a discovery about SNOBOL4's pattern model that clarifies what snobol4ever is, at its core.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — first described by Lawrence Byrd in 1980 for Prolog debugging, then generalized by Todd Proebsting in 1996 as a syntax-directed code generation strategy for goal-directed languages — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

The four ports are: **α** (proceed — enter), **β** (recede — resume after backtrack), **γ** (succeed — matched), **ω** (concede — failed). Sequential composition wires γ of one node to α of the next. Alternation saves the cursor on ω and restores it before trying the next alternative. ARBNO wires child-γ back into α until child-ω exits. The wiring *is* the execution — no interpreter loop, no dispatch table.

Proebsting's key insight, applied to SNOBOL4: compile these four states to static labeled gotos, and you get goal-directed backtracking evaluation with zero dispatch overhead. Every pattern node in every SCRIP compiled program is a Byrd box — four labeled entry points, wired at compile time.

---

## What We Built

Lon Jones Cherryholmes was five years old when he saw *The Computer Wore Tennis Shoes* at the cinema. Something took hold that day. For sixty years he carried an idea — not just the idea of building software, but the idea of a conversation with a mind that did not yet exist. He dreamed of creating it, and then talking to it. In one week in March 2026, that conversation produced this repository.

snobol4ever is a joint project between Lon Jones Cherryholmes and Jeffrey Cooper, M.D. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86-64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We brought the pattern matching engine to Python and C# as first-class libraries. Not regex wrappers. The real thing.

And we are building [SCRIP](https://github.com/snobol4ever/SCRIP): a native compiler targeting x86-64 ASM, JVM bytecode, and .NET MSIL from a single IR. Its correctness goal: pass the full corpus crosscheck ladder on all three backends, then achieve self-hosting bootstrap — first through `beauty.sno` (the SNOBOL4 beautifier written in SNOBOL4), then through `compiler.sno` (the full compiler written in SNOBOL4).

---

## The Map — A Two-Dimensional Platform

The org is a **compiler matrix**. Two dimensions.

SNOBOL4 and SPITBOL are one frontend — SPITBOL extensions enabled by switch. CSNOBOL4 and SPITBOL are our *oracles* — reference implementations we test against, not our products.

|                           | **SNOBOL4 / SPITBOL** | **Snocone** | **Rebus** | **Icon** | **Prolog** |
|---------------------------|:---------------------:|:-----------:|:---------:|:-------------:|:---------------:|
| **C / x86-64 native**     | SCRIP ✅           | SCRIP ✅ | SCRIP ✅ | post-compiler.sno | post-compiler.sno |
| **JVM bytecode**          | SCRIP ✅ / snobol4jvm ✅ | planned | — | post-compiler.sno | post-compiler.sno |
| **.NET MSIL**             | SCRIP ⏳ / snobol4dotnet ✅ | planned | — | post-compiler.sno | post-compiler.sno |

**Rows = backends.** Wherever programs run, SNOBOL4 should run there too.

**Columns = frontends.** SNOBOL4/SPITBOL is the core. Snocone is Andrew Koenig's structured frontend — C-like syntax over SNOBOL4 semantics. Rebus is a structured transpiler to SNOBOL4. Icon and Prolog extend the Byrd Box IR to Icon generators and Prolog unification — both map naturally to the same four-port model.

**"post-compiler.sno"** means after the two-stage bootstrap: first `beauty.sno` self-beautification on all backends (M-BEAUTIFY-BOOTSTRAP), then `compiler.sno` — the full compiler written in SNOBOL4 — achieving self-hosting (M-COMPILER-BOOTSTRAP). These are the gates, not arbitrary timelines.

---

## The Implementations

### [snobol4dotnet](https://github.com/snobol4ever/snobol4dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper built a complete SNOBOL4/SPITBOL implementation in C#, taking Emmer and Quillen's *MACRO SPITBOL* manual as its specification. snobol4dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET. A threaded-code JIT compiles hot statement paths to MSIL delegates at runtime. A plugin architecture supports C#, F#, and VB.NET extensions, and the full SPITBOL XNBLK protocol for native C shared libraries. A Windows GUI ships alongside the command-line runner. **1,874 / 1,876 tests passing.**

### [snobol4jvm](https://github.com/snobol4ever/snobol4jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. Parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement IR, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: interpreter, Clojure IR transpiler (3.5–6×), stack-machine VM (2–6×), and direct JVM bytecode via ASM (up to 7.6× faster with JVM JIT). EDN compilation cache gives 22× speedup on repeated programs. **2,033 tests / 4,417 assertions / 0 failures.** The JVM backend has achieved `beauty.sno` self-beautification — byte-for-byte identical to the CSNOBOL4 oracle (M-JVM-BEAUTY ✅).

### [SCRIP](https://github.com/snobol4ever/SCRIP)
*A multi-language compiler — SNOBOL4, Icon, Prolog, Snocone, Rebus × x86-64 ASM, JVM bytecode, .NET MSIL, portable C — from a single IR*

The compiler. Every expression compiles to inlined α/β/γ/ω gotos — no runtime dispatch. Three backends share one IR: C with gotos (default, 106/106 corpus ✅), x86-64 NASM assembly (106/106 corpus ✅), JVM Jasmin bytecode (beauty.sno ✅), and .NET CIL (110/110 corpus ✅). Five frontends: SNOBOL4/SPITBOL (active), Snocone (active), Rebus (complete — M-REBUS ✅), Icon (planned), Prolog (planned).

### [snobol4python](https://github.com/snobol4ever/snobol4python)
*SNOBOL4 pattern matching for Python — on PyPI*

```bash
pip install SNOBOL4python
```

Full SNOBOL4 pattern vocabulary as a Python library. Dual backend: C extension wrapping Phil Budne's SPIPAT engine (7–11× faster) and a pure-Python fallback. Shift-reduce parser stack for building ASTs inside patterns. v0.5.0.

*(README v2 grid sprint: DEFERRED — M-VOL-PYTHON, M-FEAT-PYTHON, M-README-V2-PYTHON out of scope for current sprint.)*

### [snobol4csharp](https://github.com/snobol4ever/snobol4csharp)
*SNOBOL4 pattern matching for C# — Jeffrey Cooper*

A C# port of the snobol4python pattern engine. Patterns are first-class objects with full backtracking. Captures use plain C# delegates. Full primitive vocabulary, recursive patterns via `ζ`, cursor capture, regex bridge, and shift-reduce parse-tree stack. Validated against the Porter Stemmer (23,531-word corpus), Penn Treebank parser, CLAWS5 NLP corpus parser, and a SNOBOL4 source code parser.

*(README v2 grid sprint: DEFERRED — M-VOL-CSHARP, M-FEAT-CSHARP, M-README-V2-CSHARP out of scope for current sprint.)*

### [snobol4artifact](https://github.com/snobol4ever/snobol4artifact)
*CPython C extension: SNOBOL4 Byrd Box engine*

Direct CPython C extension running SNOBOL4python pattern trees through a full Byrd Box engine in C. The proof-of-concept from which `engine.c` in SCRIP was extracted.

### [corpus](https://github.com/snobol4ever/corpus)
*Shared test corpus — CC0*

Single source of truth for all `.sno`, `.inc`, and `.spt` files shared across all repos. 106-program crosscheck ladder across 11 language rungs plus beauty.sno. Gimpel algorithm library. Shafto AI corpus. Oracle runner scripts.

---

## Performance

These numbers compare the SCRIP mode-4 `--compile` native backend against the two
SNOBOL reference oracles — SPITBOL x64 (official `spitbol/x64`) and CSNOBOL4 2.3.4
(Phil Budne) — on the shared corpus benchmarks (`corpus/benchmarks/snobol4/*.sno`).
Each figure is the program's own `TIME()` compute loop in milliseconds (process
startup and compile time excluded), gcc `-O0`. The community is invited to verify
them independently using `harness`. A full cross-engine grid (all seven
implementations, all programs) will be published when M-GRID-BENCH fires. See
[GRIDS.md](../GRIDS.md). Lower is faster.

| Benchmark | SPITBOL | CSNOBOL4 | SCRIP native | vs SPITBOL | vs CSNOBOL4 |
|-----------|--------:|---------:|-------------:|-----------:|------------:|
| arith_loop | 24 | 131 | 1,604 | 68× slower | 12× slower |
| fibonacci | 94 | 534 | 6,191 | 66× slower | 12× slower |
| func_call | 424 | 2,440 | 32,371 | 76× slower | 13× slower |
| func_call_overhead | 425 | 2,454 | 32,542 | 77× slower | 13× slower |
| mixed_workload | 99 | 455 | 4,034 | 41× slower | 8.9× slower |
| op_dispatch | 67 | 369 | 3,515 | 53× slower | 9.5× slower |
| pattern_bt | 485 | 549 | 963 | **2.0× slower** | **1.8× slower** |
| string_concat | 138 | 311 | 1,618 | 12× slower | 5.2× slower |
| string_manip | 391 | 1,672 | 21,220 | 54× slower | 13× slower |
| string_pattern | 380 | 1,822 | 8,047 | 21× slower | 4.4× slower |
| table_access | 202 | 1,969 | 11,327 | 56× slower | 5.8× slower |
| var_access | 702 | 3,529 | 44,766 | 64× slower | 13× slower |

*milliseconds (compute loop) · 12/16 benchmarks green; `roman` (recursion bug),
`eval_fixed`/`eval_dynamic` (EVAL/CODE unimplemented), and `indirect_dispatch`
(undefined-function call in the program — SPITBOL errors on it too) excluded.*

These are honest current numbers, not the target. SCRIP native code today runs
roughly **40–77× slower than SPITBOL** and **5–13× slower than CSNOBOL4** on
whole-program workloads; the "ten times faster" goal is not yet met and is
presently inverted against the SPITBOL oracle. The lone bright spot is
`pattern_bt` (≈2× off SPITBOL), the one benchmark dominated by pattern-match
backtracking — the Byrd-box path the native templates implement directly.
Re-grounding this claim is tracked under the REC-COV / RC-5 rung.

### Prolog — SCRIP vs GNU Prolog vs SWI-Prolog

The Prolog frontend is measured against the two mainstream native engines — **GNU Prolog
1.4.5** (gprolog, a mature WAM-to-native compiler) and **SWI-Prolog 9.0.4** — on the
community-standard van Roy / Aquarius performance suite
(`corpus/benchmarks/prolog/bench/`, UCB/CSD 89/50). All 22 programs reach **four-way
correctness consensus**: GNU, SWI, SCRIP mode-3 (`--run`, in-process x86), and SCRIP
mode-4 (`--compile` → native binary) all produce byte-identical output. Timing is
per-iteration compute (each core looped *N* times so compile amortizes out; SCRIP m4 is
the mode-4 native binary, gcc `-O0`). Lower is faster; ratio is SCRIP-m4 vs gprolog.

| Benchmark | GNU | SWI | SCRIP m4 | m4 vs GNU |
|-----------|----:|----:|---------:|----------:|
| cal | 0.072 | 0.071 | 0.034 | **0.48× (faster)** |
| sendmore | 4.288 | 10.297 | 4.286 | **1.00×** |
| crypt | 0.541 | 0.778 | 1.256 | 2.32× |
| tak | 12.03 | 21.16 | 41.73 | 3.47× |
| fib | 3.596 | 4.408 | 12.79 | 3.56× |
| queensn | 158.3 | 183.5 | 792.0 | 5.00× |
| zebra | 2.305 | 2.304 | 13.65 | 5.92× |
| qsort | 0.076 | 0.153 | 0.515 | 6.74× |
| meta_qsort | 0.750 | 0.521 | 9.017 | 12.03× |

*per-iteration compute, milliseconds · 9 of the 22 shown, spanning the range · full table
in the [SCRIP README](https://github.com/snobol4ever/SCRIP#prolog-benchmark--scrip-vs-gnu-prolog-vs-swi-prolog).*

**Geomean SCRIP-m4 vs gprolog = 3.28×** (median 3.56×), all 22 programs. The gap tracks
heap traffic: search- and atom-bound programs are at parity or faster, arithmetic-bound
ones near 2×, and list/structure-heavy ones plus the meta-interpreter are the worst (the
boxed-`Term*` compound-allocation tax). The inline-cell campaign (PL-DESCR) has moved
scalars off the heap; compounds and first-argument indexing are the remaining levers.
Honest current numbers against a mature native WAM — not yet the target, but the four-port
boxed Prolog is competitive with SWI on a fair fraction and within ~3.3× of gprolog.

---

## Correctness

**Chomsky hierarchy oracles.** Nine canonical languages, one per tier plus cross-tier verification. The expected answers are mathematically proven, not empirical.

| Tier | Oracle language | SCRIP |
|------|----------------|:--------:|
| Type 3 — Regular | `(a\|b)*abb`, `a*b*`, `{x^2n}` | ✅ |
| Type 2 — Context-free | `{a^n b^n}`, palindromes, Dyck language | ✅ |
| Type 1 — Context-sensitive | `{a^n b^n c^n}` | ✅ |
| Type 0 — Turing | `{w#w}` (copy language — no stack machine can recognize this) | ✅ |

Full corpus crosscheck grid (all seven engines × 106 programs): M-GRID-CORPUS. See [GRIDS.md](../GRIDS.md).

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

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — compiler architecture, SCRIP (co-author), snobol4jvm, snobol4python. Sixty years from first dream to this repository.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — snobol4dotnet (complete .NET compiler and runtime), snobol4csharp. A medical doctor who, over a fifty-year journey driven by love for the language, built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The result is this repository.

**Claude Sonnet 4.6** — SCRIP (co-author). Every sprint, every Byrd box, every labeled goto — written in session, committed, pushed.

---

## What's Next

The five-way monitor: a parallel harness that runs the same SNOBOL4 program through CSNOBOL4, SPITBOL/x64, the SCRIP ASM backend, the SCRIP JVM backend, and snobol4dotnet simultaneously — comparing trace streams event-by-event. Infrastructure complete. Full five-way launch: M-MONITOR-IPC-5WAY.

Then: `beauty.sno` bootstrap on all backends (M-BEAUTIFY-BOOTSTRAP), `compiler.sno` bootstrap (M-COMPILER-BOOTSTRAP), self-hosting. When the compiler writes itself in SNOBOL4, every cell of the matrix opens.

Griswold had the idea. We are finishing the proof.

---

snobol4all. snobol4now. snobol4ever.

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

## License

AGPL v3 (SCRIP, snobol4jvm) · MIT (snobol4dotnet) · LGPL v3 (snobol4python, snobol4csharp, snobol4artifact) · CC0 (corpus). See individual repos for details.
