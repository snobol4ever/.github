# SNOBOL4-plus

**SNOBOL4 everywhere. SNOBOL4 now.**

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class language feature — decades before regular expressions became commonplace. Its execution model is unlike anything else. Its syntax is unlike anything else. And its community has never stopped loving it.

This organization exists because two people — a software developer and a medical doctor — working independently, on different platforms, in different languages, arrived at the same conviction: SNOBOL4 deserves a modern home. Together we are bringing it to every major platform and every major language ecosystem, with full fidelity to the original language and its SPITBOL extensions.

---

## The Implementations

### [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. The compiler parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement intermediate representation, and executes programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends provide progressively faster performance: a transpiler emitting Clojure IR, a stack-machine VM, and a direct JVM bytecode backend via ASM achieving up to 7.6× faster dispatch. The full language is supported: DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, TRACE/STOPTR, and the complete SPITBOL function library. Validated against 2,033 tests across 28 test catalogs — zero failures — cross-checked against SPITBOL and CSNOBOL4 as reference oracles. Includes the Gimpel corpus (135 library routines, 10 runnable programs) and the Shafto AI corpus (SNOLISPIST — a complete Lisp-style list-processing system in SNOBOL4).

### [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C#*

A complete implementation of SNOBOL4 and SPITBOL in C#, running on Windows, Linux, and macOS. Designed for readability and correctness, with Emmer and Quillen's *MACRO SPITBOL: The High-Performance SNOBOL4 Language* as the specification. The compiler originally generated full C# via Roslyn; the current backend emits MSIL DynamicMethod delegates directly via ILGenerator — eliminating Roslyn entirely and achieving up to 15.9× speedup. All GOTO logic, Init/Finalize, and TRACE hooks are absorbed into the delegates; the hot execute path is a tight two-case loop with no switch overhead. Supports a plugin architecture (LOAD/UNLOAD) for C# and F# extensions. Includes a Windows GUI (Snobol4W), a full benchmark suite, and 1,484 passing tests.

### [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python)
*SNOBOL4 pattern matching for Python*

```bash
pip install SNOBOL4python
```

SNOBOL4-style pattern matching as a first-class Python library. Patterns are objects. Matching is lazy and backtracking. The library ships with a dual backend: a C extension wrapping Phil Budne's SPIPAT engine (7–11× faster) and a pure-Python fallback that works anywhere Python 3.10+ runs. The full primitive vocabulary is supported — ANY, NOTANY, SPAN, BREAK, BREAKX, NSPAN, ARB, ARBNO, BAL, FENCE, POS, RPOS, LEN, TAB, RTAB, REM — plus Greek-letter constructors, conditional and immediate capture operators, cursor capture, inline predicates, a regex bridge, and a shift-reduce parser stack for building ASTs directly inside patterns.

### [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp)
*SNOBOL4 pattern matching for C#*

A direct C# port of the SNOBOL4python pattern engine. Patterns are first-class objects with lazy, backtracking matching and captures via plain C# delegates — no global state, no string keys. The full primitive vocabulary is supported alongside recursive patterns via `ζ(() => p)`, a .NET regex bridge with named-group capture, and the same shift-reduce parse-tree construction system as the Python and Clojure siblings. Full TRACE support at Off / Warning / Info / Debug levels. 263 tests passing.

### [SNOBOL4](https://github.com/SNOBOL4-plus/SNOBOL4)
*Shared corpus — programs, libraries, and grammars*

Lon Cherryholmes's personal SNOBOL4 library, accumulated over decades: ~90 `.inc` library files, ~72 `.sno` programs covering everything from a SNOBOL4 beautifier/pretty-printer to SQL tools to web API listeners, 33 social-media listener programs from the early Twitter/Facebook era, and formal EBNF grammar definitions for SNOBOL4 and SPITBOL. This corpus serves as a submodule in SNOBOL4-jvm and as the shared test and demo foundation for the whole project.

---

## The People

**Lon Jones Cherryholmes** is the author of SNOBOL4-jvm, SNOBOL4-python, SNOBOL4-csharp, and the shared corpus. He has been writing SNOBOL4 for decades.

**Jeffrey Cooper, M.D.** is the original author of SNOBOL4-dotnet, which he built as a complete, readable, correct C# implementation of SNOBOL4 and SPITBOL. The threaded bytecode compiler, MSIL emitter, and plugin architecture were added in collaboration.

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

The pattern language is where SNOBOL4 lives. Patterns compose. They backtrack. They capture. They can reference themselves recursively. They were the original inspiration for everything that came after.

---

## License

Each repository carries its own license. See the individual repos for details.
