# SNOBOL4-plus

**SNOBOL4 everywhere. SNOBOL4 now.**

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type — a concept so powerful that every language since has been trying to catch up. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) extended the language further — structured programming constructs, an external function plugin architecture, and a compiler that proved SNOBOL4 could be genuinely fast. Robert Dewar and Ken Belcher built the original SPITBOL at the Illinois Institute of Technology in the early 1970s, and it changed what people thought was possible.

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C interpreter that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. It is the reference implementation most people reach for first, and it deserves that reputation. Cheyenne Wills maintains SPITBOL x64, an actively developed compiler that brings genuine native-code speed to x86_64 Unix — and whose changelog credits Jeffrey Cooper for testing and feedback. Pattern matching bridges exist for Ada (in GNAT itself), Java, JavaScript, Lua, and Python. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is SNOBOL4 on the JVM and on .NET — two ecosystems where hundreds of millions of programs run today. On the JVM, pattern libraries exist in Java (Dennis Heimbigner's jpattern, a port of Dewar's Ada SPITBOL primitives), but no one had built a full SNOBOL4 language implementation: no GOTO execution model, no DEFINE/DATA/FIELD, no CODE() or EVAL(), no named I/O channels. On .NET, there was nothing at all — not even a pattern library. We built both: a full JVM compiler and runtime in Clojure, and a full .NET compiler and runtime in C# with a Windows GUI. And we brought idiomatic pattern libraries to Python and C# for their native communities. That is our contribution.

---

## What We Built

SNOBOL4-plus is a joint project between Lon Jones Cherryholmes, a software developer, and Jeffrey Cooper, M.D., a medical doctor. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86_64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Not pattern-matching libraries wearing a SNOBOL4 badge. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We then brought the pattern matching engine — the heart of what makes SNOBOL4 SNOBOL4 — to Python and C# as first-class libraries. Not a regex wrapper. The real thing.

---

## The Implementations

### [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper set out to build a SNOBOL4 implementation that was readable, correct, and faithful to Emmer and Quillen's *MACRO SPITBOL* manual as the specification. He succeeded. SNOBOL4-dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET.

The original backend generated C# via Roslyn. The current backend emits MSIL `DynamicMethod` delegates directly via `ILGenerator` — no Roslyn, no intermediate C# source, no startup overhead. All GOTO logic, Init/Finalize, and TRACE hooks are compiled directly into the delegates. The hot execute path is a tight two-case loop. The result: **up to 15.9× faster** than the Roslyn baseline on short programs. A plugin architecture (LOAD/UNLOAD) allows C# and F# extensions to be loaded at runtime A Windows GUI (Snobol4W) ships alongside the command-line runner. **1,484 tests passing.**

### [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. The compiler parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement intermediate representation, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends provide progressively faster performance: a transpiler emitting Clojure IR (3.5–6× faster), a stack-machine VM (2–6× faster), and a direct JVM bytecode backend via ASM that generates `.class` files and loads them with `DynamicClassLoader` — achieving **up to 7.6× faster** dispatch with the JVM JIT compiling to native x64. With the EDN compilation cache, repeated programs run 22× faster than a cold compile. Cumulative speedup from cold start: approximately 190×.

The full language is supported without compromise: DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, TRACE/STOPTR, and the complete SPITBOL function library. Validated against **2,033 tests / 4,417 assertions / 0 failures**, cross-checked against SPITBOL v4.0f and CSNOBOL4 2.3.3 as reference oracles on over 1,500 systematic programs. Includes the complete Gimpel corpus (135 library routines, 10 runnable programs from *Algorithms in SNOBOL4*) and the Shafto AI corpus (SNOLISPIST — a full Lisp-style list-processing system in SNOBOL4, including Wang's theorem prover, an Augmented Transition Network compiler, and the Kalah board game).

### [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python)
*SNOBOL4 pattern matching for Python*

```bash
pip install SNOBOL4python
```

SNOBOL4-style pattern matching as a first-class Python library. This is not a regex wrapper. Patterns are objects. Matching is lazy and backtracking. The full primitive vocabulary is here — ANY, NOTANY, SPAN, BREAK, BREAKX, NSPAN, ARB, ARBNO, BAL, FENCE, POS, RPOS, LEN, TAB, RTAB, REM — along with Greek-letter constructors, conditional and immediate capture operators, cursor capture, inline predicates, a regex bridge, and a shift-reduce parser stack for building ASTs directly inside patterns. The library ships with a dual backend: a C extension wrapping Phil Budne's excellent SPIPAT engine (**7–11× faster**) and a pure-Python fallback that works anywhere Python 3.10+ runs.

### [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp)
*SNOBOL4 pattern matching for C#*

A direct C# port of the SNOBOL4python pattern engine — the same semantics, the same primitives, the same composability, in idiomatic C#. Patterns are first-class objects with lazy, backtracking matching and captures via plain C# delegates — no global state, no string keys. Recursive patterns via `ζ(() => p)`. A .NET regex bridge with named-group capture. The full shift-reduce parse-tree construction system. Full TRACE support at Off / Warning / Info / Debug levels. The Porter Stemmer test alone validates against a 23,531-word corpus. **263 tests passing.**

### [SNOBOL4](https://github.com/SNOBOL4-plus/SNOBOL4)
*Shared corpus — programs, libraries, and grammars*

Lon Cherryholmes's personal SNOBOL4 library, accumulated over decades: ~90 `.inc` library files, ~72 `.sno` programs covering everything from a full SNOBOL4 beautifier/pretty-printer to SQL tools to web API clients, 33 social-media listener programs from the early Twitter/Facebook era, and formal EBNF grammar definitions for SNOBOL4 and SPITBOL. This corpus is the shared test and demo foundation for the whole project, included as a submodule in SNOBOL4-jvm.

---

## Did We Meet the Bar?

The SNOBOL4 community has two things it demands from any serious implementation:

**Full feature fidelity.** Not just pattern matching — the whole language. DEFINE, DATA, FIELD. CODE() and EVAL(). OPSYN. TABLE and ARRAY. Named I/O. The -INCLUDE preprocessor. TRACE. All of it. We did not stub out the hard parts. Both full implementations (dotnet and jvm) pass comprehensive test suites that cover every major feature of the language, validated against the reference oracles.

**Real performance.** SNOBOL4's reputation for slowness is a legacy of interpreter implementations. SPITBOL proved in 1971 that SNOBOL4 can be compiled and made fast. We took the same lesson to heart. SNOBOL4-dotnet's MSIL backend achieves 15.9× speedup over its Roslyn baseline. SNOBOL4-jvm's bytecode backend compiles directly to JVM `.class` files and lets the JIT do the rest.

What the community gets from us that it doesn't get anywhere else: SNOBOL4 on the JVM. SNOBOL4 on .NET, with a Windows GUI. SNOBOL4 patterns in Python, on PyPI, with a C backend. SNOBOL4 patterns in C#, NuGet-ready. A plugin architecture for extending the runtime from C# and F#. LOAD/UNLOAD actually working.

---

## The Language

SNOBOL4 programs consist of labeled statements. Each statement has a subject, an optional pattern, an optional replacement, and an optional GOTO. The GOTO can be conditional on success or failure. That's the whole control-flow model — no `if`, no `while`, no `for`. Just labels and gotos, made elegant by the power of the pattern language.

```snobol
*  Count vowels in a string
        SUBJECT = "Hello, World"
        VOWELS  = "AEIOUaeiou"
LOOP    SUBJECT ANY(VOWELS) =          :F(DONE)
        COUNT   = COUNT + 1            :(LOOP)
DONE    OUTPUT  = "Vowels: " COUNT
END
```

The pattern language is where SNOBOL4 lives. Patterns compose. They backtrack. They capture. They can reference themselves recursively. They can express context-free grammars. They were the original inspiration for everything that came after — and they are still more powerful than what came after.

---

## The People

**Lon Jones Cherryholmes** is the author of SNOBOL4-jvm, SNOBOL4-python, SNOBOL4-csharp, and the shared corpus. He has been writing SNOBOL4 for decades.

**Jeffrey Cooper, M.D.** is the author of SNOBOL4-dotnet — a complete, readable, correct C# implementation of SNOBOL4 and SPITBOL, built with care and precision.

---

## License

Each repository carries its own license. See the individual repos for details.
