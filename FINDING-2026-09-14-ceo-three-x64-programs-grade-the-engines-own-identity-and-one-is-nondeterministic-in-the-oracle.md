# FINDING — three x64 programs grade the engine's own identity or accounting, and one of them is nondeterministic *in the oracle*

**ceo, 2026-09-14, on SCRIP `06dad5ff1`. `gcbuster`, `host`, and the `math_limits` pair. For Lon's ruling with the CEO-546 set; nothing excluded here.**

Three of the eleven remaining x64 reds are not compiler defects at all. Each is measured, not argued.

## 1. `gcbuster` — **the oracle disagrees with itself between two runs**

Its whole diff is engine accounting: the two `COLLECT()` return values (free bytes in our heap vs SPITBOL's), and a dump of `BASEMEM DATABTS MEMINCB STACKCUR STACKMAX STACKSIZ TOPMEM WORDSIZE`.

Run `sbl -bf gcbuster.sbl` **twice** and the oracle does not match itself:

```
10c10
< BASEMEM = 136317635653648      > BASEMEM = 124034240999440
18c18
< TOPMEM  = 136317642993680      > TOPMEM  = 124034248339472
```

Those are **heap addresses**. No engine can match them, including the one that produced them. CEO-548 already rules this shape: *a program proven nondeterministic goes in the inventory, named, out of the denominator.* This one is proven, and the proof is two runs of the oracle.

⭐ The rest of its dump is a **real** gap worth its own row — `&BASEMEM`, `&DATABTS`, `&MEMINCB`, `&STACKCUR`, `&STACKMAX`, `&STACKSIZ`, `&TOPMEM`, `&WORDSIZE` are SPITBOL keywords we do not implement, and we print nothing for them. Implementing them would make us print **our** numbers, which still would not match the oracle's. The keywords are worth having; they will not make this program green.

## 2. `host` — the program prints the engine's name and version

```
host(): x86-64:unix :Macro SPITBOL 15.01 #
```

Deterministic, and unmatchable by construction: the expected output **names the oracle**. Our `HOST()` returns empty, which is its own small gap — but a correct `HOST()` would say *SCRIP*, and the diff would stand.

## 3. `math_limits1` / `math_limits4` — already filed, restated so all four sit together

We are correctly rounded at the denormal boundary and the oracle is not (verified against CPython's `strtod`); `math_limits3`'s residue is the same thing at the 16-digit edge. See `FINDING-2026-09-14-ceo-the-math-limits-family-is-two-findings...`.

## The ruling this needs

These are the CEO-546 shape — *"a wrong exclusion costs more than a wrong cure, because a red stays visible and an excluded name cannot be red"* — so **nothing is excluded here**. Put to Lon with the ~45 gimpel/snoflake programs already open:

- **`gcbuster`**: nondeterministic in the oracle itself. CEO-548 says it leaves the graded denominator, named with this measurement. This one I believe needs only confirmation.
- **`host`**: expected output names the oracle's product and version.
- **`math_limits1/3/4`**: the oracle's decimal→binary converter is imprecise where we are IEEE-correct.

⛔ **And the honest arithmetic if Lon rules them out:** x64 goes 21/36 to 21/31 on the graded denominator, with five programs named in the inventory rather than silently dropped — and the remaining eight reds are then all genuine compiler work: `math_sqrt` and `math_exp` (the `IR_CALL_SNOBOL4` row), `save`/`sv`/`module` (EXIT, a feature we lack), and `math_limits2`-adjacent residue.
