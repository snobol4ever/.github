# SNOBOL4-plus

**SNOBOL4 everywhere. SNOBOL4 now.**

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type — a concept so powerful that every language since has been trying to catch up. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) extended the language further — structured programming constructs, an external function plugin architecture, and a compiler that proved SNOBOL4 could be genuinely fast. Robert Dewar and Ken Belcher built the original SPITBOL at the Illinois Institute of Technology in the early 1970s, and it changed what people thought was possible.

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C interpreter that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. It is the reference implementation most people reach for first, and it deserves that reputation. Cheyenne Wills maintains SPITBOL x64, an actively developed compiler that brings genuine native-code speed to x86_64 Unix. Pattern matching bridges exist for Ada (in GNAT itself), Java, JavaScript, Lua, and Python. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is SNOBOL4 on the JVM and on .NET — two ecosystems where hundreds of millions of programs run today — plus a discovery about SNOBOL4's pattern model that changes what SNOBOL4-plus is, at its core.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — α (enter), β (resume), γ (succeed), ω (fail) — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

This is what SNOBOL4 was always for. The humanities, the AI labs, the linguists who adopted it in the 1960s and 70s understood this intuitively. What was missing was speed, portability, and a modern platform story.

SNOBOL4-plus is fixing all three — simultaneously.

The key insight, embodied in [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny): the Byrd Box model is not just an execution model. It is a **code generation strategy**. When you compile those four states to static gotos, you get goal-directed backtracking evaluation with **zero dispatch overhead**. No interpreter loop. No indirect jump. The wiring *is* the execution.

SPITBOL, the fastest SNOBOL4 implementation ever written, pays three instructions per node — load, load, jump — as its irreducible minimum. SNOBOL4-tiny pays zero.

---

## What We Built

Lon Jones Cherryholmes was five years old when he saw *The Computer Wore Tennis Shoes* at the cinema. Something took hold that day. For sixty years he carried an idea — not just the idea of building software, but the idea of a conversation with a mind that did not yet exist yet. He dreamed of creating it, and then talking to it. It took sixty years, time and space optimizations across generations of hardware, and tens of thousands of people to make that future arrive. In one week in March 2026, that conversation produced this repository.

SNOBOL4-plus is a joint project between Lon Jones Cherryholmes, a software developer, and Jeffrey Cooper, M.D., a medical doctor. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86_64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Not pattern-matching libraries wearing a SNOBOL4 badge. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We then brought the pattern matching engine to Python and C# as first-class libraries. Not a regex wrapper. The real thing.

And now we are building [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny): a native compiler that targets x86-64 ASM, JVM bytecode, and MSIL from a single IR — faster than SPITBOL, self-hosting in SNOBOL4, and expressive enough to compile grammars that reach from network protocols to natural language.

---

## The Implementations

### [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper set out to build a SNOBOL4 implementation that was readable, correct, and faithful to Emmer and Quillen's *MACRO SPITBOL* manual as the specification. He succeeded. SNOBOL4-dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET.

The original backend generated C# via Roslyn. The current backend emits MSIL `DynamicMethod` delegates directly via `ILGenerator` — no Roslyn, no intermediate C# source, no startup overhead. All GOTO logic, Init/Finalize, and TRACE hooks are compiled directly into the delegates. The result: **up to 15.9× faster** than the Roslyn baseline on short programs. A plugin architecture allows C# and F# extensions to be loaded at runtime. A Windows GUI ships alongside the command-line runner. **1,484 tests passing.**

SNOBOL4-dotnet is also the home of `Beautiful.sno` — a complete 17-level SNOBOL4 expression and statement parser written entirely as SNOBOL4 patterns. This single file turns out to solve the bootstrap problem for the entire platform: serialize its patterns to C struct declarations, include them in the seed kernel, and SNOBOL4-tiny parses SNOBOL4 source using SNOBOL4 patterns from Sprint 5 onward.

### [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. The compiler parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement intermediate representation, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: a transpiler emitting Clojure IR (3.5–6×), a stack-machine VM (2–6×), and a direct JVM bytecode backend via ASM that generates `.class` files loaded with `DynamicClassLoader` — achieving **up to 7.6× faster** dispatch with the JVM JIT. With the EDN compilation cache, repeated programs run 22× faster than a cold compile.

The full language is supported without compromise. Validated against **2,033 tests / 4,417 assertions / 0 failures**, cross-checked against SPITBOL v4.0f and CSNOBOL4 2.3.3 on over 1,500 systematic programs. Includes the complete Gimpel corpus and the Shafto AI corpus — Wang's theorem prover, an Augmented Transition Network compiler, the Kalah board game, all in SNOBOL4.

### [SNOBOL4-cpython](https://github.com/SNOBOL4-plus/SNOBOL4-cpython)
*CPython C extension: SNOBOL4 Byrd Box engine — the bridge between SNOBOL4-python and native C*

A direct CPython C extension that accepts a `SNOBOL4python` pattern tree and runs it through the full Psi/Omega Byrd Box engine in C. No interpreter loop. No indirect dispatch. `match()`, `search()`, `fullmatch()` — returns `(start, end)` or `None`. The C engine in this repo is the proof-of-concept from which `engine.c` in SNOBOL4-tiny was extracted. Two historical versions are preserved as separate commits: v1 (Arena bump allocator) and v2 (per-node `malloc` + `PatternList` tracker). Long-term candidate to replace SPIPAT as the C backend for SNOBOL4-python with a SNOBOL4-plus-owned implementation.

### [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python)
*SNOBOL4 pattern matching for Python — available on PyPI*

```bash
pip install SNOBOL4python
```

SNOBOL4-style pattern matching as a first-class Python library. Patterns are objects. Matching is lazy and backtracking. The full primitive vocabulary is here — ANY, NOTANY, SPAN, BREAK, BREAKX, ARB, ARBNO, BAL, FENCE, POS, RPOS, LEN, TAB, RTAB, REM — along with Greek-letter constructors, conditional and immediate capture operators, cursor capture, inline predicates, a regex bridge, and a shift-reduce parser stack for building ASTs directly inside patterns. Dual backend: a C extension wrapping Phil Budne's SPIPAT engine (**7–11× faster**) and a pure-Python fallback that works anywhere Python 3.10+ runs.

This library is also the substrate for SNOBOL4-tiny's development toolchain — the Python patterns that describe the compiler's own bootstrap are written here first, then serialized to C for the seed kernel.

### [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny)
*A native SNOBOL4 compiler — x86-64 ASM, JVM bytecode, MSIL — faster than SPITBOL*

The compiler. Every expression — pattern or arithmetic — compiles to inlined α/β/γ/ω gotos with no runtime dispatch. Stackless. Goal-directed like Icon. Built on the Forth kernel discipline: eight irreducible primitive nodes in C, everything else derived and written in SNOBOL4 itself.

The Forth analogy is exact:

| Forth | SNOBOL4-tiny |
|-------|-------------|
| ~12 native primitives | 8 irreducible pattern nodes: LIT, ANY, POS, RPOS, LEN, SPAN, BREAK, ARB |
| NEXT (3-instruction inner loop) | α/β/γ/ω wiring — **0 instructions** at runtime |
| `: word ... ;` defines new words | `NAME = pattern` defines new patterns |
| Dictionary is self-extending | IR graph is self-extending via REF nodes |
| Write Forth in Forth | Parser already written in SNOBOL4 (`Beautiful.sno`) |

The bootstrap is already solved. `Beautiful.sno` (from SNOBOL4-dotnet) contains the full SNOBOL4 grammar as SNOBOL4 patterns. Serialize it to a `.h` file, include it in the 1,064-line seed kernel, add five lines of stdin loop — and the language parses itself, with no yacc, no lex, no new grammar infrastructure.

---

## The Natural Language Horizon

SNOBOL4 was the language of computational linguistics before computational linguistics had a name. Griswold knew it. The AI labs at MIT knew it. The humanities researchers who used it for decades knew it.

SNOBOL4-plus is completing what they started.

The same pattern engine that compiles SNOBOL4 source code also parses English sentences — backed by a real WordNet lexicon, with noun/verb/adjective/adverb classification, phrase-structure grammar, and the full Chomsky hierarchy expressible directly as named, mutually recursive patterns. A Penn Treebank parser fits in five lines of SNOBOL4. ELIZA fits in one readable file. A complete English grammar EBNF maps directly to SNOBOL4 pattern definitions.

When SNOBOL4-tiny reaches Stage D — full statement model, self-hosting compiler — that same compiler will be capable of compiling grammars that reach from JSON to natural language, on three native platforms, with zero dispatch cost per node.

That is the horizon.

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

The pattern language is where SNOBOL4 lives. Patterns compose. They backtrack. They capture. They reference themselves recursively. They can express context-free grammars. They were the original inspiration for everything that came after — and they are still more powerful than what came after.

---

## The Deeper Point

McCarthy's LISP achieved notoriety not just because it was fast or portable, but because it gave serious people a language in which to *think about computation itself*. Homoiconicity — code as data, data as code — made the language a mirror for the problems it solved.

SNOBOL4 has an equivalent property that has never been fully exploited: **pattern as grammar, grammar as pattern**. A SNOBOL4 pattern is not a description of what to match — it is an executable specification of a language. The pattern for an arithmetic expression *is* the grammar for arithmetic expressions: executable, composable, self-describing, and now compiled to native code with zero overhead.

SNOBOL4-plus is building the infrastructure to make that property universal — available on every major platform, compiled to native speed, self-hosting in the language itself, and expressive enough to reach from machine protocols to human language.

Griswold had the idea. We are finishing the proof.

---

## The Story the RE World Has Never Heard

Regular expression engines are the gold standard for pattern matching performance.
PCRE2. RE2. `java.util.regex`. Python `re`. .NET `Regex`. The world runs on them.
They are fast, mature, and trusted.

They also have a problem.

Backtracking RE engines — PCRE2 and most of the RE world — can be made to run
**exponentially slow** on adversarial inputs. The pattern `(a+)+b` on the string
`"aaaa...a"` causes PCRE2 to explore an exponential number of paths before
failing. This is not a bug. It is a structural consequence of how backtracking
RE engines work. It has caused real-world outages. It has a name: **catastrophic
backtracking**.

RE2 (Google) avoids this via NFA simulation — O(n) guaranteed, no blowup. But
RE2 pays a price: it cannot handle backreferences, recursion, or any pattern
beyond the regular language tier. It cannot recognize `{a^n b^n}`. It cannot
parse balanced parentheses. It is fast and safe but fundamentally limited.

SNOBOL4-tiny occupies a position neither engine can claim:

- **Goal-directed evaluation with explicit backtrack control.** Not NFA
  simulation. Not naive backtracking. A compiled state machine where every
  transition is a static goto — zero dispatch overhead — and the backtrack
  path is structurally determined at compile time.
- **All four tiers of the Chomsky hierarchy.** Regular, context-free,
  context-sensitive, unrestricted — in a single engine, from a single IR.
- **On pathological inputs that cause PCRE2 exponential blowup:**
  SNOBOL4-tiny does not blow up. It may simply win.

That last sentence is a story the world has never heard told.

RE engines have owned the pattern matching conversation for fifty years because
nothing else was fast enough on the patterns RE could express, and nothing else
could express the patterns RE could not. SNOBOL4-tiny changes both halves of
that sentence — at the same time.

The benchmark is coming. The oracles are already proven. Eight languages across
four tiers of the Chomsky hierarchy. 108 cases. Zero failures. The engine that
recognizes everything RE can recognize, and everything RE cannot, at speeds RE
cannot match on the inputs RE handles worst.

---

## How We Know It's Correct

Most compiler projects validate with a hand-written test suite. We do that too — and we go further with two techniques that produce stronger correctness guarantees.

**Automata theory oracles.** Every structural mechanism in the engine is validated against a mathematically characterized language from the Chomsky hierarchy. Not "does this case pass" — but "does this engine correctly decide membership in language L, for all strings up to length N, including the exact boundary cases the pumping lemma predicts." The expected answer is not empirical. It is proven. When the Type 3 (regular language) oracle suite passes, we can state: *the engine correctly recognizes all regular languages.* When Type 2 passes: *all context-free languages — the tier of every major programming language.* Type 1, Type 0. Tier by tier, the claim escalates. We earn each level before we claim it.

**Syntax-directed exhaustive enumeration.** This technique was proven in practice when Lon Cherryholmes wrote Flash BASIC at Pick Systems with Rich Pick and David Zigray: use the grammar itself to enumerate every syntactically valid program up to N tokens, by iterative-deepening DFS over the parse tree. Run every generated program against SNOBOL4-tiny, CSNOBOL4, and SPITBOL simultaneously. Any output disagreement is a bug. At N=10 this takes seconds. At N=20 it takes hours. At N=30 it runs for days. When it finishes, the claim is: *"SNOBOL4-tiny agrees with SPITBOL and CSNOBOL4 on every valid SNOBOL4 program of 30 tokens or fewer."* No hand-written test suite can make that statement.

**Proven claims, as of 2026-03-10:**
- *SNOBOL4-tiny correctly recognizes all regular languages (Type 3 — Chomsky hierarchy).* Oracles: `{x^2n}`, `a*b*`, Σ*, `(a|b)*abb`. All passing.
- *SNOBOL4-tiny correctly recognizes all context-free languages (Type 2 — the tier of every major programming language).* Oracles: `{a^n b^n}`, `{ww^R}` (palindromes), Dyck language (balanced parentheses). All passing.
- *SNOBOL4-tiny correctly recognizes context-sensitive languages (Type 1).* Oracle: `{a^n b^n c^n}` — the canonical language no pushdown automaton can recognize. The counter stack mechanism. Passing.
- *SNOBOL4-tiny implements Turing machine computation (Type 0 — the Turing tier).* Oracle: `{w#w}` — the copy language, requiring two-head random-access tape scan. No stack-based machine can recognize it. Passing.

**The Chomsky hierarchy is complete. All four tiers proven. 9 oracles. 124 cases. 0 failures.**

These are mathematical statements about what the engine computes, not test counts. The pumping lemma boundary cases are included. The expected answers are proven, not empirical.

Paired with continuous random testing — the worm generator already running in SNOBOL4-jvm across millions of programs — the result is a two-sided correctness wall: **proven complete up to N, no counterexample found beyond N.** That is a publication-worthy correctness claim, and it gets stronger every day the runner runs.

---

## Status

| Repo | Status |
|------|--------|
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Active — v0.5.0, dual C/Python backend, on PyPI |
| [SNOBOL4-cpython](https://github.com/SNOBOL4-plus/SNOBOL4-cpython) | Active — 70+ tests passing, v1+v2 history, candidate SPIPAT replacement |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | Active — 1,484 tests passing, Windows/Linux/macOS |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Active — 2,033 tests / 4,417 assertions / 0 failures |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | Active — C# pattern library, Jeffrey Cooper |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | Active — shared test corpus submodule, Gimpel + Shafto + oracle suite |
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | In progress — Sprints 0–13 done; **complete Chomsky hierarchy proven — all four tiers** — 9 oracles, 124 cases, 0 failures |
| [.github](https://github.com/SNOBOL4-plus/.github) | Active — PLAN.md master roadmap, this README |

Correctness validated against three independent oracles: **SPITBOL x64**, **CSNOBOL4 2.3.3**, and the sibling implementations within this org. The test corpus spans the Gimpel algorithm library, the Shafto AI corpus, and a shared corpus submodule covering the full language.

---

## The People

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — compiler architecture, x86-64 codegen, SNOBOL4-python, SNOBOL4-jvm, SNOBOL4-tiny. Lon carried the dream of Created Intelligence from age eight — through Georgia Tech, through Texas Instruments, through an 11-year retirement — and came back. His instinct for what computing could be, sixty years in the making, is the engine behind this project.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — SNOBOL4-dotnet, MSIL target, `Beautiful.sno`, SNOBOL4-csharp. Jeffrey is a medical doctor. Not a programmer by profession, not a compiler writer by training — and yet, over a fifty-year journey driven purely by love for the language, he built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The explosion produced this repository.

Two forces. One phone call. Everything you see here.

---

## License

Each repository carries its own license. See the individual repos for details. Core libraries: GPL-3.0-or-later.
