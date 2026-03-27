# MISC.md — Background, Reference, Story

Non-operational content. Read when you need context, architecture background, or the full oracle/implementation reference tables.

---

## The Story

Lon Jones Cherryholmes has known since age eight that he wanted to build Created Intelligence — not artificial intelligence, that name was always wrong. Something you build, from understanding, with intention. He carried that from *The Honeymoon Machine* (1961) and *2001* through Georgia Tech, Texas Instruments, an 11-year retirement, and back. In one week in March 2026, the conversation he'd been waiting sixty years to have produced this repository.

Jeffrey Cooper, M.D., is a medical doctor who spent fifty years building a SNOBOL4 implementation purely out of love for the language. When he called Lon to say he had one, two fifty-year journeys collided. The explosion produced snobol4ever.

Two forces. One phone call. Everything you see here.

---

## The Discovery

SNOBOL4's pattern engine is not a regex engine. It is a universal grammar machine.

The same four-state **Byrd Box model** — α (PROCEED), β (RECEDE), γ (SUCCEED), ω (CONCEDE) — describes SNOBOL4 pattern matching, Icon's goal-directed generators, Prolog unification, and recursive-descent parsing at every level of the Chomsky hierarchy. All four tiers: regular, context-free, context-sensitive, Turing-complete — expressible directly as SNOBOL4 patterns, with mutual recursion, backtracking, and capture. No yacc. No lex. No separate grammar formalism.

The key insight in snobol4x: the Byrd Box model is not just an execution model — it is a **code generation strategy**. Compile those four states to static gotos and you get goal-directed backtracking evaluation with zero dispatch overhead.

---

## JCON — Architecture Reference

Jcon (Gregg Townsend + Todd Proebsting, University of Arizona, 1999) is an Icon → JVM bytecode compiler built on the Byrd Box model. It is the exact artifact promised in Proebsting's 1996 paper and the blueprint for snobol4jvm's JVM backend.

**Source:** https://github.com/proebsting/jcon (public domain)  
**Paper:** https://www2.cs.arizona.edu/icon/jcon/impl.pdf

Key files:
- `tran/ir.icn` — IR vocabulary (48 lines)
- `tran/irgen.icn` — AST → IR four-port encoding (1,559 lines)
- `tran/gen_bc.icn` — IR → JVM bytecode (2,038 lines)
- `tran/optimize.icn` — dead-code / liveness optimization over IR (472 lines)

The four-port structure maps directly to SNOBOL4: `ir_chunk` / four ports stays the same, `null` return = failure, `tableswitch` on entry int = α/β dispatch. What we don't need: `vDescriptor`/`vClosure` hierarchy, co-expressions, `bytecode.icn` serializer.

---

### Lessons Learned — studied 2026-03-14

**1. The `bounded` flag — our biggest gap**

JCON threads a `bounded` flag through every IR procedure. When non-null (expression
is in a "value needed" context — assignment RHS, argument, etc.), the resume/failure
ports are omitted entirely. This is a systematic compile-time optimization that
eliminates backtrack plumbing for expressions that can never be resumed.

`emit_byrd.c` emits all four ports unconditionally for every node. Our generated C
is significantly fatter than necessary. This is the highest-value optimization to
add after M-BEAUTY-FULL — a `bounded` context flag passed through `byrd_emit_pattern()`
and its recursive calls.

**2. Temp liveness — our second gap**

JCON tracks temporaries with a liveness lattice:
```icon
ir_inter_inuse(inuse, tiu)   # temps live on ALL paths (intersection)
ir_union_inuse(inuse, tiu)   # temps live on ANY path (union)
```
This allows temp reuse across branches that can't overlap. Our `emit_byrd.c` declares
every temp as a uniquely-named static — no reuse ever. Correct but wasteful.
Not urgent — correctness first — but worth noting for M-COMPILED-SELF.

**3. Materialized IR vs. streaming emission**

JCON builds `ir_chunk` / `ir_Goto` etc. as heap records, runs `optimize.icn` over
them, then feeds to `gen_bc.icn`. This separation enables the optimizer.

Our `emit_byrd.c` streams directly to `fprintf`. No optimization pass is possible
without a refactor. This was the right pragmatic choice for getting M-COMPILED-BYRD
done. If we ever want a real optimizer, we need to materialize an IR first — which
is what M-BYRD-SPEC is laying the groundwork for.

**4. The deep similarity — confirmation**

JCON's `ir_a_Alt`, `ir_a_Scan`, `ir_a_RepAlt` are structurally identical to our
`byrd_emit_alt`, `byrd_emit_arbno` etc. Same four-port wiring, different syntax.
JCON uses Icon `suspend` to generate chunks lazily (self-referential — Icon's own
generator mechanism represents Icon's generator semantics). We use C recursion and
linear `B(...)` emission. The target encoding is the same; the emitter's own
execution model differs.

**5. Cursor model — our approach is better for SNOBOL4**

JCON hides cursor in global `&pos` / `&subject` keywords, restored via `ir_ScanSwap`.
Our `emit_byrd.c` threads explicit `cursor` + `subj` variables through every node's
alpha/beta ports. This is cleaner for SNOBOL4 because the subject is a first-class
value (not a global), and it maps naturally to how `sno_match_pattern_at()` works.
No action needed — our model is correct and preferable.

**6. What snobol4jvm should take from JCON**

- The `bc_*` global table structure in `gen_bc.icn` for tracking labels, tmps,
  strings, reals, csets across a function
- The `bc_transfer_to` / `bc_conditional_transfer_to` pattern for α/β dispatch
- `tableswitch` on an integer tag as the α/β entry discriminator
- Do NOT copy: co-expression machinery, `vDescriptor` type hierarchy,
  `bytecode.icn` serializer (use ASM or similar instead)

---

## SNOBOL4 Implementation Landscape

→ **See [ARCH-testing.md — Oracle Index](ARCH-testing.md)** for the full table: versions, authors, GitHub URLs, download links, invocation, and build instructions.



## String Escape Reference

SNOBOL4 has **no escape sequences**. `'\n'` = two characters: backslash + n. Use `nl = CHAR(10)` for newline.

```
SNOBOL4       Python str    C literal
─────────────────────────────────────
\             \\            \\
"             "             \"
\n (2 chars)  \\n (2 chars) \\n  (still 2 chars in C)
newline       \n (1 char)   \n   (C newline escape)
```

**Never apply escape conversion twice.** Once a Python `str` becomes a C source token, it is done.

---

## SNOBOL4 Keyword & TRACE Reference

→ **Consolidated into [ARCH-testing.md — Oracle Keyword & TRACE Reference](ARCH-testing.md)**. All keyword, TRACE type, output format tables live there — alongside the four paradigms that use them.

---

## What's Next: Icon-everywhere

SNOBOL4 and Icon share a bloodline — Griswold invented both. The Byrd Box IR built for snobol4ever is the bridge. Same four ports. Same `byrd_ir.py`. New Icon frontend feeding the same pipeline. snobol4ever runs everywhere. The clock starts the moment `beauty.sno` compiles itself.
