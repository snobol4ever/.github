# SCRIP_DEMO3.md — Tiny Compiler: Polyglot Proof of Concept #3

**Status: CONCEPT — not yet cooked. Capture only. No implementation plan yet.**

**Companion to:** SCRIP_DEMO.md (family tree) · SCRIP_DEMO2.md (puzzle solver)
**Difficulty:** Hardest of the three. Four languages. Three compiler phases. One orchestrator.
**The thesis:** A real compiler — parse → codegen → optimize → format — built from
four languages each owning exactly the phase it is best at.

---

## The Concept

A tiny infix arithmetic expression compiler targeting a simple stack machine:

```
input:   "3 + 4 * (2 - 1)"
output:  PUSH 3
         PUSH 4
         PUSH 2
         PUSH 1
         SUB
         MUL
         ADD
```

Each compiler phase is owned by the language built for it.

---

## The Four-Language Breakdown

### Snocone — Phase 1: Parse

Snocone reads the infix expression string and builds a parse tree.
This is Snocone's core strength: pattern-driven structural decomposition.
Operator precedence handled by named patterns. Output: a flat serialized
tree format (S-expression or pipe-delimited node list) passed to Prolog.

```snocone
expr    := term (('+' | '-') term)*
term    := factor (('*' | '/') factor)*
factor  := '(' expr ')' | number
number  := [0-9]+
```

One pass. No recursion in the host language — the pattern grammar *is* the parser.

### Prolog — Phase 2: Codegen

Prolog takes the serialized parse tree and applies rewrite rules to produce
raw stack instructions. This is exactly what Prolog does best: tree-to-tree
transformation via structural pattern matching on term shapes.

```prolog
compile(num(N),   [push(N)]).
compile(add(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [add|Code]).
compile(sub(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [sub|Code]).
compile(mul(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [mul|Code]).
compile(div(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [div|Code]).
```

No search. No backtracking. Pure deterministic tree rewriting.
Output: flat instruction list, newline-delimited, passed to Icon.

### Icon — Phase 3: Optimize + Orchestrate

Icon owns two things:

**Orchestrator:** Icon drives the full pipeline. It calls Snocone to parse,
calls Prolog to compile, runs its own optimizer pass, then calls Snocone
to format. The `every`/`suspend` model makes the pipeline lazy and composable.

**Peephole optimizer:** Icon's generator model is the natural fit for
sliding-window pattern matching over an instruction stream:

```icon
# Constant-fold PUSH a / PUSH b / ADD → PUSH (a+b)
procedure optimize(instrs);
  local i;
  every i := 1 to *instrs - 2 do
    if instrs[i][1:5] == "PUSH " & instrs[i+1][1:5] == "PUSH " &
       instrs[i+2] == "ADD" then {
      suspend "PUSH " || (integer(instrs[i][6:0]) + integer(instrs[i+1][6:0]));
      i +:= 2; next;
    };
    suspend instrs[i];
  suspend instrs[*instrs];
end
```

Sliding window, generator output — exactly what `every`/`suspend` is for.

### Snocone — Phase 4: Format

The same Snocone instance (or a second call) takes the optimized instruction
list and formats it: right-aligns opcodes, pads operands, adds a column header,
optionally adds an address column. Output: human-readable assembly listing.

```
Addr  Instr
----  -----
0000  PUSH 3
0001  PUSH 4
0002  PUSH 2
0003  PUSH 1
0004  SUB
0005  MUL
0006  ADD
```

Snocone's OUTPUT formatting patterns handle alignment without manual padding logic.

---

## Why This Demo Is The Best Argument For Scrip

- Demo 1 (family tree): three languages, data pipeline, each does its specialty
- Demo 2 (puzzle solver): paradigm reversal — Prolog as store, Icon as search
- **Demo 3 (tiny compiler): a real software artifact — a compiler — assembled from parts**

A compiler is the canonical example of a multi-phase pipeline. Every CS student
knows: lex → parse → codegen → optimize → emit. Scrip Demo 3 shows that
each phase can be written in the language that owns it, wired together with funny
linkage, and the result is smaller and clearer than any single-language version.

The optimizer in Icon is ~10 lines. The codegen in Prolog is ~5 rules.
The parser in Snocone is ~5 patterns. The formatter in Snocone is ~3 patterns.
Total: ~25 lines of actual logic. The rest is plumbing — and the plumbing
is what Scrip provides.

---

## What Needs To Be True Before This Can Be Built

- **M-SCRIP-DEMO** ✅ (funny linkage architecture proven)
- **M-SCRIP-DEMO2** ✅ (four-language orchestration proven)
- **Snocone JVM emitter** — Snocone currently has no JVM backend (only x64 ASM)
- **Icon as orchestrator** — needs M-IJ-STRING-RETVAL fix + multi-call sequencing

## Open Design Questions (not yet cooked)

1. **Snocone → JVM:** Does Snocone get a JVM emitter, or does it compile to a
   String-passing interpreter called from Icon via `invokestatic`?
2. **Parse tree serialization format:** S-expression? Pipe-delimited? JSON?
   Must be something both Snocone (output) and Prolog (input) can handle easily.
3. **Two Snocone phases:** Same `.scrip` block used twice (parse + format),
   or two separate fenced blocks? The formatter is a different program.
4. **Optimizer scope:** Constant folding only, or also dead-push elimination,
   strength reduction (x*2 → x+x), etc.?
5. **Error handling:** What does the pipeline do with malformed input?

---

## Milestone

**M-SCRIP-DEMO3** fires when:
1. `demo/scrip3/expr.scrip` exists
2. `run_demo3.sh` compiles and runs clean
3. Output matches `expr.expected` (diff clean)
4. Optimizer demonstrably fires on at least one constant-fold case

*Not scheduled. Concept capture only. Revisit after M-SCRIP-DEMO2 fires.*

---

*SCRIP_DEMO3.md = L4. Concept doc. No session state here until work begins.*
