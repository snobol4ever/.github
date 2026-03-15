# SNOBOL4ever

**snobol for all. snobol for now. snobol forever.**

---

SNOBOL4 is one of the great languages. Invented at Bell Labs in the 1960s by Ralph Griswold, Ivan Polonsky, and David Farber, it introduced pattern matching as a first-class data type — a concept so powerful that every language since has been trying to catch up. SNOBOL4 patterns compose. They backtrack. They capture intermediate results. They reference themselves recursively. They can express BNF grammars directly — something regular expressions simply cannot do. Patterns in SNOBOL4 are objects you build, store, pass to functions, and combine at runtime. They are not strings. They are not syntax. They are values.

SPITBOL (Speedy Implementation of SNOBOL) extended the language further — structured programming constructs, an external function plugin architecture, and a compiler that proved SNOBOL4 could be genuinely fast. Robert Dewar and Ken Belcher built the original SPITBOL at the Illinois Institute of Technology in the early 1970s, and it changed what people thought was possible.

The tradition is alive today. Phil Budne maintains CSNOBOL4 — a faithful, actively maintained C interpreter that builds on nearly any platform with a C89 compiler: Linux, macOS, Windows, FreeBSD, and beyond. It is the reference implementation most people reach for first, and it deserves that reputation. Cheyenne Wills maintains SPITBOL x64, an actively developed compiler that brings genuine native-code speed to x86_64 Unix. Pattern matching bridges exist for Ada (in GNAT itself), Java, JavaScript, Lua, and Python. This is a community of serious, generous people who have kept a great language alive for decades, and we are proud to stand alongside them.

What we add to that tradition is SNOBOL4 on the JVM and on .NET — two ecosystems where hundreds of millions of programs run today — plus a discovery about SNOBOL4's pattern model that changes what SNOBOL4ever is, at its core.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a **universal grammar machine**.

The same four-state **Byrd Box model** — α (PROCEED — enter), β (RECEDE — undo), γ (SUCCEED — matched), ω (CONCEDE — failed) — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification and backtracking, and recursive-descent parsing at every level of the Chomsky hierarchy. Regular grammars, context-free grammars, context-sensitive grammars, unrestricted grammars — all expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism. The language *is* the grammar tool.

This is what SNOBOL4 was always for. The humanities, the AI labs, the linguists who adopted it in the 1960s and 70s understood this intuitively. What was missing was speed, portability, and a modern platform story.

SNOBOL4ever is fixing all three — simultaneously.

The key insight, embodied in [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny): the Byrd Box model is not just an execution model. It is a **code generation strategy**. When you compile those four states to static gotos, you get goal-directed backtracking evaluation with **zero dispatch overhead**. No interpreter loop. No indirect jump. The wiring *is* the execution.

SPITBOL, the fastest SNOBOL4 implementation ever written, pays three instructions per node — load, load, jump — as its irreducible minimum. SNOBOL4-tiny pays zero.

---

## The Commands

The original Unix SNOBOL4 implementation was invoked as **`sno3`** — short, lowercase, a number that means something. That tradition continues here.

Each backend in SNOBOL4ever has its own command name:

| Command | What it does |
|---------|-------------|
| **`sno4now`** | Native compiler — SNOBOL4 → C → x86-64. No VM. No JIT warmup. Runs *now*, on bare metal. |
| **`sno4jvm`** | JVM backend — SNOBOL4 → JVM bytecodes via the Byrd Box IR. |
| **`sno4net`** | .NET backend — SNOBOL4 → MSIL via `ILGenerator`. (Note: `sno4.net` was considered and rejected — it's a URL.) |

```bash
sno4now < program.sno        # compile and run natively
sno4jvm < program.sno        # compile and run on the JVM
sno4net < program.sno        # compile and run on .NET CLR
```

The line of succession:

```
sno3  (Unix, 1974)
  ↓
snobol4  (CSNOBOL4 — Phil Budne)
spitbol  (SPITBOL x64 — Cheyenne Wills)
  ↓
sno4now / sno4jvm / sno4net  (SNOBOL4ever, 2026)
```

Three characters. SNOBOL4 started as three characters. It's three characters again.
But now it runs everywhere.

---

## What We Built

Lon Jones Cherryholmes was five years old when he saw *The Computer Wore Tennis Shoes* at the cinema. Something took hold that day. For sixty years he carried an idea — not just the idea of building software, but the idea of a conversation with a mind that did not yet exist. He dreamed of creating it, and then talking to it. It took sixty years, time and space optimizations across generations of hardware, and tens of thousands of people to make that future arrive. In one week in March 2026, that conversation produced this repository.

SNOBOL4ever is a joint project between Lon Jones Cherryholmes, a software developer, and Jeffrey Cooper, M.D., a medical doctor. Working independently across different platforms and runtimes, we arrived at the same conviction: SNOBOL4 deserves a modern home — everywhere, not just on x86_64 Unix.

We built two complete, independent implementations of the full SNOBOL4/SPITBOL language. Not stubs. Not subsets. Not pattern-matching libraries wearing a SNOBOL4 badge. Full implementations — with compilers, runtimes, GOTO-driven execution models, DEFINE/DATA/FIELD, CODE(), EVAL(), OPSYN, TABLE, ARRAY, named I/O channels, the -INCLUDE preprocessor, and TRACE/STOPTR — validated against SPITBOL and CSNOBOL4 as reference oracles on thousands of programs.

We then brought the pattern matching engine to Python and C# as first-class libraries. Not a regex wrapper. The real thing.

And now we are building [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny): a native compiler that targets x86-64 ASM, JVM bytecode, and MSIL from a single IR — faster than SPITBOL, self-hosting in SNOBOL4, and expressive enough to compile grammars that reach from network protocols to natural language.

---

## The Implementations

### [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet)
*Full SNOBOL4/SPITBOL compiler and runtime for .NET — written in C# — Windows, Linux, macOS*

Jeffrey Cooper set out to build a SNOBOL4 implementation that was readable, correct, and faithful to Emmer and Quillen's *MACRO SPITBOL* manual as the specification. He succeeded. SNOBOL4-dotnet runs on Windows, Linux, and macOS — the first full SNOBOL4/SPITBOL implementation to do so on .NET.

The original backend generated C# via Roslyn. The current backend emits MSIL `DynamicMethod` delegates directly via `ILGenerator` — no Roslyn, no intermediate C# source, no startup overhead. All GOTO logic, Init/Finalize, and TRACE hooks are compiled directly into the delegates. The result: **up to 15.9× faster** than the Roslyn baseline on short programs. A plugin architecture allows C# and F# extensions to be loaded at runtime. A Windows GUI ships alongside the command-line runner. **1,484 tests passing.**

### [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm)
*Full SNOBOL4/SPITBOL compiler and runtime for the JVM — written in Clojure — any platform Java runs on*

A complete implementation of SNOBOL4 and SPITBOL built from the ground up in Clojure. The compiler parses SNOBOL4 source through an instaparse PEG grammar, emits a labeled-statement intermediate representation, and runs programs through a GOTO-driven interpreter faithful to the original execution model. Multiple execution backends: a transpiler emitting Clojure IR (3.5–6×), a stack-machine VM (2–6×), and a direct JVM bytecode backend via ASM that generates `.class` files loaded with `DynamicClassLoader` — achieving **up to 7.6× faster** dispatch with the JVM JIT. With the EDN compilation cache, repeated programs run 22× faster than a cold compile.

Validated against **2,033 tests / 4,417 assertions / 0 failures**, cross-checked against SPITBOL v4.0f and CSNOBOL4 2.3.3 on over 1,500 systematic programs. Includes the complete Gimpel corpus and the Shafto AI corpus.

### [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny)
*`sno4now` — the native SNOBOL4 compiler. Also the source of `sno4jvm` and `sno4net`.*

The compiler. Every expression — pattern or arithmetic — compiles to inlined α/β/γ/ω gotos with no runtime dispatch. Stackless. Goal-directed like Icon. Built on the Forth kernel discipline: eight irreducible primitive nodes in C, everything else derived and written in SNOBOL4 itself.

**Sprint 32 status**: `snoc` (the SNOBOL4→C compiler) compiles `beauty.sno` — a complete self-beautifying SNOBOL4 formatter — with zero gcc errors, including all 19 `-INCLUDE` helper libraries. The compiled binary is being driven to self-hosting. Milestone 3 (bootstrap proof: compiled binary output matches oracle output, diff is empty) is one bug away.

### [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python)
*SNOBOL4 pattern matching for Python — available on PyPI*

```bash
pip install SNOBOL4python
```

### [SNOBOL4-cpython](https://github.com/SNOBOL4-plus/SNOBOL4-cpython)
*CPython C extension: SNOBOL4 Byrd Box engine*

### [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp)
*SNOBOL4 pattern matching for C#*

### [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus)
*Shared test corpus — Gimpel library, Shafto AI programs, oracle suite*

---

## The Natural Language Horizon

SNOBOL4 was the language of computational linguistics before computational linguistics had a name. Griswold knew it. The AI labs at MIT knew it. The humanities researchers who used it for decades knew it.

SNOBOL4ever is completing what they started.

The same pattern engine that compiles SNOBOL4 source code also parses English sentences — backed by a real WordNet lexicon, with noun/verb/adjective/adverb classification, phrase-structure grammar, and the full Chomsky hierarchy expressible directly as named, mutually recursive patterns. A Penn Treebank parser fits in five lines of SNOBOL4. ELIZA fits in one readable file. A complete English grammar EBNF maps directly to SNOBOL4 pattern definitions.

When `sno4now` reaches full self-hosting — the compiled binary compiling itself — that same compiler will be capable of compiling grammars that reach from JSON to natural language, on three native platforms, with zero dispatch cost per node.

That is the horizon.

---

## The Story the RE World Has Never Heard

Regular expression engines are the gold standard for pattern matching performance. PCRE2. RE2. `java.util.regex`. Python `re`. .NET `Regex`. The world runs on them. They are fast, mature, and trusted.

They also have a problem.

Backtracking RE engines — PCRE2 and most of the RE world — can be made to run **exponentially slow** on adversarial inputs. The pattern `(a+)+b` on the string `"aaaa...a"` causes PCRE2 to explore an exponential number of paths before failing. This is not a bug. It is a structural consequence of how backtracking RE engines work. It has caused real-world outages. It has a name: **catastrophic backtracking**.

RE2 (Google) avoids this via NFA simulation — O(n) guaranteed, no blowup. But RE2 pays a price: it cannot handle backreferences, recursion, or any pattern beyond the regular language tier. It cannot recognize `{a^n b^n}`. It cannot parse balanced parentheses. It is fast and safe but fundamentally limited.

SNOBOL4-tiny occupies a position neither engine can claim:

- **Goal-directed evaluation with explicit backtrack control.** Not NFA simulation. Not naive backtracking. A compiled state machine where every transition is a static goto — zero dispatch overhead — and the backtrack path is structurally determined at compile time.
- **All four tiers of the Chomsky hierarchy.** Regular, context-free, context-sensitive, unrestricted — in a single engine, from a single IR.
- **On pathological inputs that cause PCRE2 exponential blowup:** SNOBOL4-tiny does not blow up.

| Pattern | SNOBOL4-tiny | PCRE2 JIT | Result |
|---------|:------------:|:---------:|--------|
| `(a|b)*abb` — normal | **33 ns** | 77 ns | **2.3× faster** |
| `(a+)+b` len=28 — pathological | **0.7 ns** | 25 ns | **33× faster** |

| Grammar | SNOBOL4-tiny | Bison LALR(1) | Result |
|---------|:------------:|:-------------:|--------|
| `{a^n b^n}` — context-free | **44 ns** | 72 ns | **1.6× faster** |

PCRE2 cannot count. Bison cannot triple-count. SNOBOL4-tiny does all of it, faster, from the same IR, through the same compiler pipeline.

---

## How We Know It's Correct

**The Chomsky hierarchy is complete. All four tiers proven. 9 oracles. 124 cases. 0 failures.**

- *Type 3 (regular):* `{x^2n}`, `a*b*`, Σ*, `(a|b)*abb` — all passing.
- *Type 2 (context-free — the tier of every major programming language):* `{a^n b^n}`, `{ww^R}` (palindromes), Dyck language (balanced parentheses) — all passing.
- *Type 1 (context-sensitive):* `{a^n b^n c^n}` — the canonical language no pushdown automaton can recognize — passing.
- *Type 0 (Turing-complete):* `{w#w}` — the copy language, requiring two-head random-access tape scan — passing.

These are mathematical statements about what the engine computes, not test counts. The pumping lemma boundary cases are included. The expected answers are proven, not empirical.

---

## Status

| Repo | Status |
|------|--------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | **Sprint 32** — `snoc` compiles `beauty.sno` (0 gcc errors, all 19 -INCLUDEs). Bootstrap proof (Milestone 3) in progress. |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | Active — 2,033 tests / 4,417 assertions / 0 failures |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | Active — 1,484 tests passing, Windows/Linux/macOS |
| [SNOBOL4-python](https://github.com/SNOBOL4-plus/SNOBOL4-python) | Active — v0.5.0, dual C/Python backend, on PyPI |
| [SNOBOL4-cpython](https://github.com/SNOBOL4-plus/SNOBOL4-cpython) | Active — 70+ tests passing |
| [SNOBOL4-csharp](https://github.com/SNOBOL4-plus/SNOBOL4-csharp) | Active — C# pattern library |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | Active — shared corpus, Gimpel + Shafto + oracle suite |
| [.github](https://github.com/SNOBOL4-plus/.github) | Active — PLAN.md master roadmap |

---

## The People

**Lon Jones Cherryholmes** ([@LCherryholmes](https://github.com/LCherryholmes)) — compiler architecture, x86-64 codegen, SNOBOL4-python, SNOBOL4-jvm, SNOBOL4-tiny. Lon carried the dream of Created Intelligence from age eight — through Georgia Tech, through Texas Instruments, through an 11-year retirement — and came back. His instinct for what computing could be, sixty years in the making, is the engine behind this project.

**Jeffrey Cooper, M.D.** ([@jcooper0](https://github.com/jcooper0)) — SNOBOL4-dotnet, MSIL target, `Beautiful.sno`, SNOBOL4-csharp. Jeffrey is a medical doctor. Not a programmer by profession, not a compiler writer by training — and yet, over a fifty-year journey driven purely by love for the language, he built a complete SNOBOL4 compiler and runtime. When he called Lon to say he had an implementation, two fifty-year journeys collided. The explosion produced this repository.

Two forces. One phone call. Everything you see here.

---

## What's Next — Icon-everywhere

SNOBOL4 and Icon share a bloodline. Ralph Griswold invented both. Icon is the direct descendant — goal-directed evaluation, generators, backtracking, the same four-port Byrd Box execution model that powers everything here.

Icon already has an implementation for C (the Arizona reference) and for the JVM (Jcon, Proebsting + Townsend, 1999 — the very blueprint we used for our JVM backend). What it does not have is **everywhere**: not on .NET, not on modern JVM via ASM, not compiled from a shared IR to three targets simultaneously.

The Byrd Box IR we built for SNOBOL4ever is the bridge. The same four ports. The same `byrd_ir.py`. The same `emit_jvm.py` and `emit_msil.py` backends. A new Icon frontend feeding the same pipeline.

snobol4ever runs everywhere. The clock starts the moment `beauty.sno` compiles itself.

---

## License

Each repository carries its own license. See the individual repos for details. Core libraries: GPL-3.0-or-later.
