# SCRIP_DEMOS.md — The Demo Ladder

Ten self-contained Scrip programs. Same algorithm in SNOBOL4, Icon, Prolog.
Same input, same output, three idioms. Each demo is a **product milestone** —
it fires when all three snobol4ever frontends compile the program through the
JVM backend and produce the correct output.

**Three frontends:** SNOBOL4 · Icon · Prolog  
**One backend:** JVM

Reference interpreters (csnobol4, swipl, icont) were used to establish
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
3. Prolog block compiles via sno2c -pl -jvm → JVM → correct output
4. All three match `demo/scrip/demoN/NAME.expected`
5. Session note added to `SESSIONS_ARCHIVE.md`

---

## §NOW

| Milestone | Status |
|-----------|--------|
| M-SD-1  | ✅ hello — SNO2C-JVM + ICON-JVM + PROLOG-JVM all PASS |
| M-SD-2  | ❌ **NEXT** — wordcount; blocked on Icon scanning + Prolog string builtins |
| M-SD-3  | ❌ |
| M-SD-4  | ❌ |
| M-SD-5  | ❌ |
| M-SD-6  | ❌ |
| M-SD-7  | ❌ |
| M-SD-8  | ❌ |
| M-SD-9  | ❌ |
| M-SD-10 | ❌ |

---

## The Philosophy

Same algorithm, three idioms. Not "look, they interoperate" — that comes later.
This is: **the same thought expressed three ways, each beautiful in its own language.**

SNOBOL4: patterns consume input structurally.  
Icon: generators produce output lazily.  
Prolog: rules define truth declaratively.

One algorithm. Three frontends. One backend. One result.

---

*SCRIP_DEMOS.md — the ladder. Each rung is a green test through snobol4ever.*
