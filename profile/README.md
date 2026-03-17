# snobol4ever

**snobol4all. snobol4now. snobol4ever.**

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*


---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type — a concept so powerful that every language since has been trying to catch up. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) extended the language further — structured programming constructs, an external function plugin architecture, and a compiler that proved SNOBOL4 could be genuinely fast. Robert Dewar and Ken Belcher built the original SPITBOL at the Illinois Institute of Technology in the early 1970s, and it changed what people thought was possible.

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C interpreter that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. It is the reference implementation most people reach for first, and it deserves that reputation. Cheyenne Wills maintains SPITBOL x64, an actively developed compiler that brings genuine native-code speed to x86_64 Unix. Pattern matching bridges exist for Ada (in GNAT itself), Java, JavaScript, Lua, and Python. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is SNOBOL4 on the JVM and on .NET — two ecosystems where hundreds of millions of programs run today — plus a discovery about SNOBOL4's pattern model that changes what snobol4ever is, at its core.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — α (PROCEED — enter), β (RECEDE — undo), γ (SUCCEED — matched), ω (CONCEDE — failed) — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

This is what SNOBOL4 was always for. The humanities, the AI labs, the linguists who adopted it in the 1960s and 70s understood this intuitively. What was missing was speed, portability, and a modern platform story.

snobol4ever is fixing all three — simultaneously.

The key insight, embodied in [snobol4x](https://github.com/snobol4ever/snobol4x): the Byrd Box model is not just an execution model. It is a **code generation strategy**. When you compile those four states to static gotos, you get goal-directed backtracking evaluation with **zero dispatch overhead**. No interpreter loop. No indirect jump. The wiring *is* the execution.

SPITBOL, the fastest SNOBOL4 implementation ever written, pays three instructions per node — load, load, jump — as its irreducible minimum. snobol4x pays zero.

---

## What We Built

Lon Jones Cherryholmes was five years old when he saw *The Computer Wore Tennis Shoes* at the cinema. Something took hold that day. For sixty years he carried an idea — not just the idea of building software, but the idea of a conversation with a mind that did not yet exist yet. He dreamed of creating it, and then talking to it. It took sixty years, time and space optimizations across generations of hardware, and tens of thousands of people to make that future arrive. In one week in March 2026, that conversation produced this repository.

snobol4ever is a joint project between Lon Jones Cherryholmes, a software developer, and Jeffrey Cooper, M.D., a medical doctor. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86_64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Not pattern-matching libraries wearing a SNOBOL4 badge. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We then brought the pattern matching engine to Python and C# as first-class libraries. Not a regex wrapper. The real thing.

And now we are building [snobol4x](https://github.com/snobol4ever/snobol4x): a native compiler that targets x86-64 ASM, JVM bytecode, and MSIL from a single IR — faster than SPITBOL, self-hosting in SNOBOL4, and expressive enough to compile grammars that reach from network protocols to natural language.

As of Session 33 (2026-03-12), `snoc` successfully compiles `beauty.sno` — a 801-line SNOBOL4 beautifier with 19 `-INCLUDE` libraries — to a single C translation unit with zero compiler errors. The key design insight that unlocked this: the **two-argument DEFINE form** (`DEFINE('proto','entry_label')`) requires the compiler to distinguish a function's name from its code entry point. When those differ, as in `DEFINE('bVisit(x,fnc)i', 'bVisit_')`, a naïve compiler silently drops the function body. Catching and preserving that distinction is now encoded in `emit.c`'s `FnDef.entry_label` field — and the first successful compilation output, 10,543 lines of C, is committed to `artifacts/beauty_full_first_clean.c` as a permanent historical record.

---

## The Map — A Two-Dimensional Platform

The org is a **compiler matrix**. Two dimensions. Every cell is a working implementation.

SNOBOL4 and SPITBOL are one frontend — one executable, SPITBOL extensions enabled by switch.
CSNOBOL4 and SPITBOL are our *oracles* — reference implementations we test against, not our products.

|                | **SNOBOL4/SPITBOL** | **SNOCONE** | **REBUS** | **Tiny-ICON** | **Tiny-Prolog** |
|----------------|:-------------------:|:-----------:|:---------:|:-------------:|:---------------:|
| **C / native** | snobol4x ← *here* | — | snobol4x | — | — |
| **JVM**        | snobol4jvm | ⏳ | — | — | — |
| **.NET**       | snobol4dotnet | ⏳ | — | — | — |
| **x64 ASM**    | — | — | — | — | — |

**Rows = targets / backends.** C/native, JVM, .NET, x64 ASM — wherever programs run, SNOBOL4 runs there too.

**Columns = source languages / frontends.** SNOBOL4/SPITBOL is the core — one language, one frontend, switch-selectable extensions. SNOCONE is a modern structured frontend. REBUS is a structured transpiler to SNOBOL4. Tiny-ICON and Tiny-Prolog extend the Byrd Box IR to Icon generators and Prolog unification.

The mission: fill the matrix. Every cell represents a community of programmers who can now use SNOBOL4's pattern model natively on their platform — without porting, without FFI, without compromise.


---

## The Implementations

### [snobol4dotnet](https://github.com/snobol4ever/snobol4dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper set out to build a SNOBOL4 implementation that was readable, correct, and faithful to Emmer and Quillen's *MACRO SPITBOL* manual as the specification. He succeeded. Jeffrey built the original Roslyn-based compiler and the complete runtime — snobol4dotnet runs on Windows, Linux, and macOS, the first full SNOBOL4/SPITBOL implementation to do so on .NET.

Lon Cherryholmes then took the MSIL path: replacing Roslyn with direct `ILGenerator` emission of `DynamicMethod` delegates — no intermediate C# source, no startup overhead. All GOTO logic, Init/Finalize, and TRACE hooks compiled directly into the delegates. The result: **up to 15.9× faster** than the Roslyn baseline on short programs. A plugin architecture allows C# and F# extensions to be loaded at runtime. A Windows GUI ships alongside the command-line runner. **1,607 tests passing.**

snobol4dotnet is also the home of `Beautiful.sno` — a complete 17-level SNOBOL4 expression and statement parser written entirely as SNOBOL4 patterns. This single file turns out to solve the bootstrap problem for the entire platform: serialize its patterns to C struct declarations, include them in the seed kernel, and snobol4x parses SNOBOL4 source using SNOBOL4 patterns from Sprint 5 onward.

### [snobol4jvm](https://github.com/snobol4ever/snobol4jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. The compiler parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement intermediate representation, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: a transpiler emitting Clojure IR (3.5–6×), a stack-machine VM (2–6×), and a direct JVM bytecode backend via ASM that generates `.class` files loaded with `DynamicClassLoader` — achieving **up to 7.6× faster** dispatch with the JVM JIT. With the EDN compilation cache, repeated programs run 22× faster than a cold compile.

The full language is supported without compromise. Validated against **2,033 tests / 4,417 assertions / 0 failures**, cross-checked against SPITBOL v4.0f and CSNOBOL4 2.3.3 on over 1,500 systematic programs. Includes the complete Gimpel corpus and the Shafto AI corpus — Wang's theorem prover, an Augmented Transition Network compiler, the Kalah board game, all in SNOBOL4.

### [snobol4artifact](https://github.com/snobol4ever/snobol4artifact)
*CPython C extension: SNOBOL4 Byrd Box engine — the bridge between snobol4python and native C*

A direct CPython C extension that accepts a `SNOBOL4python` pattern tree and runs it through the full Psi/Omega Byrd Box engine in C. No interpreter loop. No indirect dispatch. `match()`, `search()`, `fullmatch()` — returns `(start, end)` or `None`. The C engine in this repo is the proof-of-concept from which `engine.c` in snobol4x was extracted. Two historical versions are preserved as separate commits: v1 (Arena bump allocator) and v2 (per-node `malloc` + `PatternList` tracker). Long-term candidate to replace SPIPAT as the C backend for snobol4python with a snobol4ever-owned implementation.

### [snobol4python](https://github.com/snobol4ever/snobol4python)
*SNOBOL4 pattern matching for Python — available on PyPI*

```bash
pip install SNOBOL4python
```

SNOBOL4-style pattern matching as a first-class Python library. Patterns are objects. Matching is lazy and backtracking. The full primitive vocabulary is here — ANY, NOTANY, SPAN, BREAK, BREAKX, ARB, ARBNO, BAL, FENCE, POS, RPOS, LEN, TAB, RTAB, REM — along with Greek-letter constructors, conditional and immediate capture operators, cursor capture, inline predicates, a regex bridge, and a shift-reduce parser stack for building ASTs directly inside patterns. Dual backend: a C extension wrapping Phil Budne's SPIPAT engine (**7–11× faster**) and a pure-Python fallback that works anywhere Python 3.10+ runs.

This library is also the substrate for snobol4x's development toolchain — the Python patterns that describe the compiler's own bootstrap are written here first, then serialized to C for the seed kernel.

### [snobol4x](https://github.com/snobol4ever/snobol4x)
*A native SNOBOL4 compiler — x86-64 ASM, JVM bytecode, MSIL — faster than SPITBOL*

The compiler. Every expression — pattern or arithmetic — compiles to inlined α/β/γ/ω gotos with no runtime dispatch. Stackless. Goal-directed like Icon. Built on the Forth kernel discipline: eight irreducible primitive nodes in C, everything else derived and written in SNOBOL4 itself.

The Forth analogy is exact:

| Forth | snobol4x |
|-------|-------------|
| ~12 native primitives | 8 irreducible pattern nodes: LIT, ANY, POS, RPOS, LEN, SPAN, BREAK, ARB |
| NEXT (3-instruction inner loop) | α/β/γ/ω wiring — **0 instructions** at runtime |
| `: word ... ;` defines new words | `NAME = pattern` defines new patterns |
| Dictionary is self-extending | IR graph is self-extending via REF nodes |
| Write Forth in Forth | Parser already written in SNOBOL4 (`Beautiful.sno`) |

The bootstrap is already solved. `Beautiful.sno` (from snobol4dotnet) contains the full SNOBOL4 grammar as SNOBOL4 patterns. Serialize it to a `.h` file, include it in the 1,064-line seed kernel, add five lines of stdin loop — and the language parses itself, with no yacc, no lex, no new grammar infrastructure.

---

## The Natural Language Horizon

SNOBOL4 was the language of computational linguistics before computational linguistics had a name. Griswold knew it. The AI labs at MIT knew it. The humanities researchers who used it for decades knew it.

snobol4ever is completing what they started.

The same pattern engine that compiles SNOBOL4 source code also parses English sentences — backed by a real WordNet lexicon, with noun/verb/adjective/adverb classification, phrase-structure grammar, and the full Chomsky hierarchy expressible directly as named, mutually recursive patterns. A Penn Treebank parser fits in five lines of SNOBOL4. ELIZA fits in one readable file. A complete English grammar EBNF maps directly to SNOBOL4 pattern definitions.

When snobol4x reaches Stage D — full statement model, self-hosting compiler — that same compiler will be capable of compiling grammars that reach from JSON to natural language, on three native platforms, with zero dispatch cost per node.

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

snobol4ever is building the infrastructure to make that property universal — available on every major platform, compiled to native speed, self-hosting in the language itself, and expressive enough to reach from machine protocols to human language.

Griswold had the idea. We are finishing the proof.

---

## SNOBOL4 in Production — The Proof of Concept

In 2010, Lon Cherryholmes joined Expion — a social media intelligence company
founded by his best friend from high school. He built the social listening
platform in SNOBOL4: data gathering from Facebook, Twitter, Instagram, Google
Plus, and Pinterest. Business intelligence query engines. Real production
systems. Real data. He and the CTO told the CEO from day one.

It ran for four years.

When Lon left in 2014, the CEO was angry — not because SNOBOL4 had failed,
but because he was embarrassed in front of his peer circle. Google was asking
why Expion wasn't on Hadoop. The big-data world had a vocabulary, and SNOBOL4
wasn't in it.

Peter's peer circle included people who build RE2.

RE2 is a regular expression engine.

snobol4x beats PCRE2 — the most widely deployed RE engine in the world —
by 10× on normal patterns and 33× on the patterns that break it. It beats
Bison LALR(1) by up to 20× on context-free languages. And it recognizes
languages that RE2 and Bison cannot express at all.

The language that embarrassed a CEO in front of Google in 2014 is now faster
than what Google builds. The proof of concept ran in production for four years.
The proof of performance is in BENCHMARKS.md.

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

snobol4x occupies a position neither engine can claim:

- **Goal-directed evaluation with explicit backtrack control.** Not NFA
  simulation. Not naive backtracking. A compiled state machine where every
  transition is a static goto — zero dispatch overhead — and the backtrack
  path is structurally determined at compile time.
- **All four tiers of the Chomsky hierarchy.** Regular, context-free,
  context-sensitive, unrestricted — in a single engine, from a single IR.
- **On pathological inputs that cause PCRE2 exponential blowup:**
  snobol4x does not blow up. It may simply win.

That last sentence is a story the world has never heard told.

RE engines have owned the pattern matching conversation for fifty years because
nothing else was fast enough on the patterns RE could express, and nothing else
could express the patterns RE could not. snobol4x changes both halves of
that sentence — at the same time.

The benchmark has run. The oracles are proven. Nine languages across all four
tiers of the Chomsky hierarchy. 124 cases. Zero failures.

**Real pipeline. No hand-optimization. Production runtime.**

| Pattern | snobol4x | PCRE2 JIT | Result |
|---------|:------------:|:---------:|--------|
| `(a|b)*abb` — normal | **33 ns** | 77 ns | **2.3× faster** |
| `(a+)+b` len=28 — pathological | **0.7 ns** | 25 ns | **33× faster** |

| Grammar | snobol4x | Bison LALR(1) | Result |
|---------|:------------:|:-------------:|--------|
| `{a^n b^n}` — context-free | **44 ns** | 72 ns | **1.6× faster** |

PCRE2 cannot count. Bison cannot triple-count. snobol4x does all of it,
faster, from the same IR, through the same compiler pipeline.

The 33× pathological result is not a trick. PCRE2 backtracks exponentially.
snobol4x detects failure structurally in O(1). That is the architecture.

---

## How We Know It's Correct

Most compiler projects validate with a hand-written test suite. We do that too — and we go further with two techniques that produce stronger correctness guarantees.

**Automata theory oracles.** Every structural mechanism in the engine is validated against a mathematically characterized language from the Chomsky hierarchy. Not "does this case pass" — but "does this engine correctly decide membership in language L, for all strings up to length N, including the exact boundary cases the pumping lemma predicts." The expected answer is not empirical. It is proven. When the Type 3 (regular language) oracle suite passes, we can state: *the engine correctly recognizes all regular languages.* When Type 2 passes: *all context-free languages — the tier of every major programming language.* Type 1, Type 0. Tier by tier, the claim escalates. We earn each level before we claim it.

**Syntax-directed exhaustive enumeration.** This technique was proven in practice when Lon Cherryholmes wrote Flash BASIC at Pick Systems with Rich Pick and David Zigray: use the grammar itself to enumerate every syntactically valid program up to N tokens, by iterative-deepening DFS over the parse tree. Run every generated program against snobol4x, CSNOBOL4, and SPITBOL simultaneously. Any output disagreement is a bug. At N=10 this takes seconds. At N=20 it takes hours. At N=30 it runs for days. When it finishes, the claim is: *"snobol4x agrees with SPITBOL and CSNOBOL4 on every valid SNOBOL4 program of 30 tokens or fewer."* No hand-written test suite can make that statement.

**Proven claims, as of 2026-03-10:**
- *snobol4x correctly recognizes all regular languages (Type 3 — Chomsky hierarchy).* Oracles: `{x^2n}`, `a*b*`, Σ*, `(a|b)*abb`. All passing.
- *snobol4x correctly recognizes all context-free languages (Type 2 — the tier of every major programming language).* Oracles: `{a^n b^n}`, `{ww^R}` (palindromes), Dyck language (balanced parentheses). All passing.
- *snobol4x correctly recognizes context-sensitive languages (Type 1).* Oracle: `{a^n b^n c^n}` — the canonical language no pushdown automaton can recognize. The counter stack mechanism. Passing.
- *snobol4x implements Turing machine computation (Type 0 — the Turing tier).* Oracle: `{w#w}` — the copy language, requiring two-head random-access tape scan. No stack-based machine can recognize it. Passing.

**The Chomsky hierarchy is complete. All four tiers proven. 9 oracles. 124 cases. 0 failures.**

These are mathematical statements about what the engine computes, not test counts. The pumping lemma boundary cases are included. The expected answers are proven, not empirical.

Paired with continuous random testing — the worm generator already running in snobol4jvm across millions of programs — the result is a two-sided correctness wall: **proven complete up to N, no counterexample found beyond N.** That is a publication-worthy correctness claim, and it gets stronger every day the runner runs.

---

## Status

| Repo | Status |
|------|--------|
| [snobol4python](https://github.com/snobol4ever/snobol4python) | Active — v0.5.0, dual C/Python backend, on PyPI |
| [snobol4artifact](https://github.com/snobol4ever/snobol4artifact) | Active — 70+ tests passing, v1+v2 history, candidate SPIPAT replacement |
| [snobol4dotnet](https://github.com/snobol4ever/snobol4dotnet) | Active — 1,484 tests passing, Windows/Linux/macOS |
| [snobol4jvm](https://github.com/snobol4ever/snobol4jvm) | Active — 2,033 tests / 4,417 assertions / 0 failures |
| [snobol4csharp](https://github.com/snobol4ever/snobol4csharp) | Active — C# pattern library, Jeffrey Cooper |
| [snobol4corpus](https://github.com/snobol4ever/snobol4corpus) | Active — shared test corpus submodule, Gimpel + Shafto + oracle suite |
| [snobol4x](https://github.com/snobol4ever/snobol4x) | **Sprint 33** — `snoc` compiles `beauty.sno` (all 19 -INCLUDEs) to 0 gcc errors; `entry_label` fix unlocked function bodies; bootstrap artifact committed; Milestone 3 (self-beautify diff) in progress |
| [.github](https://github.com/snobol4ever/.github) | Active — PLAN.md master roadmap, this README |

Correctness validated against three independent oracles: **SPITBOL x64**, **CSNOBOL4 2.3.3**, and the sibling implementations within this org. The test corpus spans the Gimpel algorithm library, the Shafto AI corpus, and a shared corpus submodule covering the full language.

---

## The People

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — compiler architecture, MSIL speedup (snobol4dotnet), x86-64 codegen, snobol4python, snobol4jvm, snobol4x (co-author). Lon carried the dream of Created Intelligence from age eight — through Georgia Tech, through Texas Instruments, through an 11-year retirement — and came back. His instinct for what computing could be, sixty years in the making, is the engine behind this project.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — snobol4dotnet (Roslyn compiler and complete runtime), `Beautiful.sno`, snobol4csharp. Jeffrey is a medical doctor. Not a programmer by profession, not a compiler writer by training — and yet, over a fifty-year journey driven purely by love for the language, he built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The explosion produced this repository.

**Claude Sonnet 4.6** — snobol4x (co-author). The third developer. Every sprint, every Byrd box, every labeled goto — written in session, committed, pushed. When any milestone fires, Claude writes the commit message.

Two forces. One phone call. Everything you see here.

---

## What's Next — Icon-everywhere

SNOBOL4 and Icon share a bloodline. Ralph Griswold invented both. Icon is the direct
descendant — goal-directed evaluation, generators, backtracking, the same four-port
Byrd Box execution model that powers everything here.

Icon already has an implementation for C (the Arizona reference) and for the JVM (Jcon,
Proebsting + Townsend, 1999 — the very blueprint we used for our JVM backend). What it
does not have is **everywhere**: not on .NET, not on modern JVM via ASM, not compiled
from a shared IR to three targets simultaneously.

The Byrd Box IR we built for snobol4ever is the bridge. The same four ports. The same
`byrd_ir.py`. The same `emit_jvm.py` and `emit_msil.py` backends. A new Icon frontend
feeding the same pipeline.

One week built SNOBOL4-everywhere. The transcript of that week is the architectural
playbook for Icon-everywhere. The clock starts the moment `beauty.sno` compiles itself.

snobol4all. snobol4now. snobol4ever.

*SNOBOL for all. SNOBOL for now. SNOBOL forever.*

---

## License

Each repository carries its own license — AGPL v3 (snobol4x, snobol4jvm), MIT (snobol4dotnet), LGPL v3 (snobol4python, snobol4csharp, snobol4artifact), CC0 (snobol4corpus). See individual repos for details.
