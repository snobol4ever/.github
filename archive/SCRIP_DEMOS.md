# SCRIP_DEMOS.md — The Demo Ladder

Ten self-contained Scrip programs. Same algorithm in SNOBOL4, Icon, Prolog.
Same input, same output, three idioms. Each demo is a **product milestone** —
it fires when all three snobol4ever frontends compile the program through the
JVM backend and produce the correct output.

**Three frontends:** SNOBOL4 · Icon · Prolog  
**One backend:** JVM

Reference interpreters (spitbol, swipl, icont) were used to establish
`.expected` output only. They are not the product.

---

## The Ladder

| # | File | Algorithm | Key contrast |
|---|------|-----------|--------------| 
| DEMO1 | `hello.md` | Hello World | `OUTPUT =` vs `write()` vs `write/1` |
| DEMO2 | `wordcount.md` | Count words | SPAN patterns vs `!str` generator vs DCG |
| DEMO3 | `roman.md` | Integer → Roman numerals | Table-driven goto vs `suspend` vs arithmetic rules |
| DEMO4 | `palindrome.md` | Is string a palindrome? | `REVERSE` vs subscript walk vs `reverse/2` |
| DEMO5 | `fib.md` | Fibonacci first 10 | Labeled goto vs `suspend` generator vs `fib/2` rule |
| DEMO6 | `sieve.md` | Primes to 50 (Sieve) | ARRAY bitset vs list+every vs trial division |
| DEMO7 | `caesar.md` | ROT13 cipher | `REPLACE` parallel strings vs `map()` vs `maplist` |
| DEMO8 | `sort.md` | Sort 8 integers | Insertion sort vs `isort` vs `msort/2` |
| DEMO9 | `rpn.md` | RPN calculator | Pattern-driven stack vs list-as-stack vs DCG |
| DEMO10 | `anagram.md` | Detect anagrams | SORTCHARS+TABLE vs canonical+table vs `msort+assert` |

---

## Milestone Map

```
M-SD-1   hello       ← NEXT
M-SD-2   wordcount
M-SD-3   roman
M-SD-4   palindrome
M-SD-5   fib
M-SD-6   sieve
M-SD-7   caesar
M-SD-8   sort
M-SD-9   rpn
M-SD-10  anagram
```

**Product demo fires when all 10 milestones are green.**

---

## Milestone firing condition

Each `M-SD-N` fires when:
1. SNOBOL4 block compiles via snobol4jvm → JVM → correct output
2. Icon block compiles via icon_driver -jvm → JVM → correct output
3. Prolog block compiles via scrip-cc -pl -jvm → JVM → correct output
4. All three match `demo/scrip/demoN/NAME.expected`
5. Session note added to `SESSIONS_ARCHIVE.md`

---

## §NOW

| Milestone | SCRIP_CC-JVM | ICON-JVM | PROLOG-JVM | XLINK |
|-----------|-----------|----------|------------|-------|
| M-SD-1  hello      | ✅ | ✅ | ✅ | ⏳ |
| M-SD-2  wordcount  | ✅ | ✅ | ✅ | ⏳ |
| M-SD-3  roman      | ✅ | ✅ | ✅ | ⏳ |
| M-SD-4  palindrome | ✅ | ✅ | ✅ | ⏳ |
| M-SD-5  fibonacci  | ✅ | ⏭ | ❌ forall/2 meta-call | ⏳ |
| M-SD-6  sieve      | ✅ | ⏭ | ✅ | ⏳ |
| M-SD-7  rot13      | ✅ | ⏭ | ❌ | ⏳ |
| M-SD-8  sort       | ✅ | ⏭ | ✅ | ⏳ |
| M-SD-9  rpn        | ✅ | ⏭ | ❌ | ⏳ |
| M-SD-10 anagram    | ❌ | ⏭ | ❌ | ⏳ |

**Legend:** ✅ pass · ❌ fail · ⏭ skipped (compiler gap) · ⏳ not yet started

**XLINK** — cross-language linked demo: all five languages call each other through
the SCRIP object/linker model (M-LINK-* track). Gate: `GENERAL-SCRIP-ABI.md` frozen.

---

## §XLINK Track

The XLINK column fires when a demo runs as a **linked multi-language program** —
not three parallel single-language programs, but one binary where each language
handles what it does best.

| Demo | XLINK design |
|------|-------------|
| hello | SNOBOL4 `OUTPUT =` calls Prolog `hello/0` calls Icon `write()` — one linked call chain |
| wordcount | SNOBOL4 tokenizes with SPAN, calls Prolog to classify tokens, Icon counts |
| fibonacci | SNOBOL4 driver calls Icon generator `suspend`, Prolog verifies via `fib/2` |
| sieve | Icon generates candidates via `every`, Prolog filters with trial division, SNOBOL4 formats |
| palindrome | Snocone REVERSE rule → Icon subscript walk → Prolog `reverse/2` — three verifiers, one answer |

**Gate milestone:** M-LINK-JVM-4 (first cross-language SNOBOL4+Prolog JVM call) must
pass before any XLINK demo can fire.

---

## §LINKER Track (new — 2026-03-27)

Separate from the demo ladder. Tracks the compile+link infrastructure.

| ID | Milestone | Status |
|----|-----------|--------|
| M-LINK-ABI | `GENERAL-SCRIP-ABI.md` frozen — x64, JVM, .NET ABIs agreed | ⏳ DRAFT |
| M-LINK-X64-1 | EXPORT/IMPORT syntax parsed, `.globl` emitted in x64 path | ❌ |
| M-LINK-X64-2 | Static-by-default for non-exported DEFINEs | ❌ |
| M-LINK-X64-3 | `scrip compile -c` → `.o` via `as` | ❌ |
| M-LINK-X64-4 | Two-file SNOBOL4 x64 link test passes | ❌ |
| M-LINK-JVM-1 | EXPORT/IMPORT in JVM emitter | ❌ |
| M-LINK-JVM-2 | Per-file `.class` generation (not monolith) | ❌ |
| M-LINK-JVM-3 | Two-file SNOBOL4 JVM link test passes | ❌ |
| M-LINK-JVM-4 | **PROOF OF CONCEPT** — SNOBOL4 calls Prolog predicate via JVM ABI | ❌ |
| M-LINK-JVM-5 | SNOBOL4 calls Icon generator via JVM ABI | ❌ |
| M-LINK-NET-1 | EXPORT/IMPORT in .NET emitter | ✅ |
| M-LINK-NET-2 | Per-file `.dll` generation | ✅ |
| M-LINK-NET-3 | Two-file SNOBOL4 .NET link test passes | ✅ |
| M-SCRIP-XLINK-1 | hello: all 5 languages in one linked binary | ❌ |
| M-SCRIP-XLINK-2 | fibonacci: SNO calls PROLOG calls ICON | ❌ |
| M-SCRIP-XLINK-3 | wordcount: SNO tokenizes, PL classifies | ❌ |
| M-SCRIP-XLINK-4 | sieve: ICON generates, PL filters, SNO formats | ❌ |
| M-SCRIP-XLINK-5 | palindrome: four-language pipeline | ❌ |

**Critical path:** M-LINK-ABI → M-LINK-JVM-1 → M-LINK-JVM-2 → M-LINK-JVM-3 → M-LINK-JVM-4 → M-SCRIP-XLINK-1

---

## The Philosophy

Same algorithm, three idioms. Not "look, they interoperate" — that comes later.
This is: **the same thought expressed three ways, each beautiful in its own language.**

SNOBOL4: patterns consume input structurally.  
Icon: generators produce output lazily.  
Prolog: rules define truth declaratively.

One algorithm. Three frontends. One backend. One result.

**The next chapter:** One algorithm. Five frontends. One *linked* program. Each language
doing what it does best. That is XLINK. That is SCRIP Level 2.

---

*SCRIP_DEMOS.md — the ladder. Each rung is a green test through snobol4ever.*  
*XLINK column added 2026-03-27. LINKER track added 2026-03-27.*
