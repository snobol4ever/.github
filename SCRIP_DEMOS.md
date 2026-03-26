# SCRIP_DEMOS.md — The Demo Ladder

Ten self-contained Scrip programs. Same algorithm in SNOBOL4, Icon, Prolog.
Same input, same output, three idioms. Each is a unit test for the Scrip
unified compiler.

---

## The Ladder

| # | File | Algorithm | Key contrast |
|---|------|-----------|--------------|
| DEMO1 | `hello.md` | Hello World | `OUTPUT =` vs `write()` vs `write/1` |
| DEMO2 | `wordcount.md` | Count words | SPAN patterns vs `!str` generator vs DCG |
| DEMO3 | `roman.md` | Integer → Roman numerals | Table-driven goto vs `suspend` vs arithmetic rules |
| DEMO4 | `palindrome.md` | Is string a palindrome? | `REVERSE` vs subscript walk vs `reverse/2` |
| DEMO5 | `fib.md` | Fibonacci first 10 | Labeled goto vs `suspend` generator vs `fib/2` rule |
| DEMO6 | `sieve.md` | Primes to 50 (Sieve) | TABLE bitset vs list+every vs `exclude/sieve` |
| DEMO7 | `caesar.md` | ROT13 cipher | `MAP` vs `map()` vs `maplist+rot13_char` |
| DEMO8 | `sort.md` | Sort 8 integers | Insertion sort vs `isort` vs `msort/2` |
| DEMO9 | `rpn.md` | RPN calculator | Pattern-driven stack vs list-as-stack vs DCG |
| DEMO10 | `anagram.md` | Detect anagrams | SORTCHARS+TABLE vs canonical+table vs `msort+assert` |

---

## Milestone Map

```
M-SD-DEMO1   hello       ← NEXT
M-SD-DEMO2   wordcount
M-SD-DEMO3   roman
M-SD-DEMO4   palindrome
M-SD-DEMO5   fib
M-SD-DEMO6   sieve
M-SD-DEMO7   caesar
M-SD-DEMO8   sort
M-SD-DEMO9   rpn
M-SD-DEMO10  anagram
             ↓
M-SCRIP-DEMO   family tree (funny linkage) — was DEMO1, now DEMO4
M-SCRIP-DEMO2  puzzle solver              — was DEMO2, now DEMO5
M-SCRIP-DEMO3  tiny compiler              — concept
```

Each milestone fires when:
1. `demo/scrip/demoN/NAME.md` exists in snobol4x
2. `run_demo.sh demoN` passes — all three backends match `.expected`
3. Session note added to `SESSIONS_ARCHIVE.md`

---

## §NOW

| Milestone | Status |
|-----------|--------|
| M-SD-DEMO1 | ❌ **NEXT** — file exists, needs runtime wiring in run_demo.sh |
| M-SD-DEMO2 | ❌ |
| M-SD-DEMO3 | ❌ |
| M-SD-DEMO4 | ❌ |
| M-SD-DEMO5 | ❌ |
| M-SD-DEMO6 | ❌ |
| M-SD-DEMO7 | ❌ |
| M-SD-DEMO8 | ❌ |
| M-SD-DEMO9 | ❌ |
| M-SD-DEMO10 | ❌ |
| M-SCRIP-DEMO (family tree) | ❌ blocked — StackMapTable work needed |

---

## The Philosophy

Same algorithm, three idioms. Not "look, they interoperate" — that comes later.
This is: **the same thought expressed three ways, each beautiful in its own language.**

SNOBOL4: patterns consume input structurally.  
Icon: generators produce output lazily.  
Prolog: rules define truth declaratively.

One algorithm. Three windows into it.

---

## SD-10 Pick-up

```bash
cd /home/claude/snobol4x
# Wire up csnobol4 + swipl paths in run_demo.sh
# Test: bash demo/scrip/run_demo.sh demo/scrip/demo1 demo/scrip/demo1/hello.expected
# Fire M-SD-DEMO1 when all three pass
# Then proceed through the ladder
```

*SCRIP_DEMOS.md — the ladder. Each rung is a green test.*
