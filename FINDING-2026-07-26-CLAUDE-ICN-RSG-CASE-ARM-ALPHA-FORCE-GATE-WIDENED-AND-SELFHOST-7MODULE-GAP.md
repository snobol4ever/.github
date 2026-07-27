# FINDING (2026-07-26, s167 Sonnet 4.6) — RSG CLOSED (8/8 bench); JCON self-host 7-module gap root-caused

**SCRIP `f0e1e011` · suite 250/11/32 (was 249/12/32) · bench correctness 8/8 IDENTICAL (was 7/8) · RT_OPT=-O0**

---

## PART 1 — RSG FIX: CASE-ARM ALPHA-FORCE GATE WIDENED

### Root cause (LIVE CURSOR FINDING-2026-07-25 hypothesis confirmed)

`lower_icon.c` ~L584 alpha-force gate: `if (is_resumable(t->c[bi])) lc_γ_to_α(idc, be)`.

The predicate tests the SOURCE arm body in the parse tree, but the β-stamp lands on the
ENTRY NODE `be` (the first IR node built from that body). A COMPOUND arm
`{ pending := [1,2] | [9]; n +:= 0 }` is a `TT_SEQ_EXPR` ending in a plain assign, so
`is_resumable(body) == 0` and the α-force was skipped — even though `be` was the disjunction
itself, already auto-β-stamped by `build()`. The selector then entered at β, which falls
straight into the af glue (alt_i += 1) and selected the LAST arm → `int=9` instead of `int=1 int=2`.

Canonical `ir_a_Case` (`refs/jcon-master/tran/irgen.icn` L276) targets `L[i].body.ir.START`
unconditionally. The faithful predicate is therefore `ir_is_generator_kind(be->op)` — keyed on
the ENTRY NODE, not the source tree.

### Fix (1 line, `src/lower/lower_icon.c`)

```c
- if (is_resumable(t->c[bi])) lc_γ_to_α(idc, be);
+ if (is_resumable(t->c[bi]) || (be && ir_is_generator_kind(be->op))) lc_γ_to_α(idc, be);
```

### Verification

| Test | Pre-fix | Post-fix | Oracle |
|---|---|---|---|
| `case type(x) of { "string": { pending:=[1,2]\|[9]; n+:=0 } }` | `int=9 iters=2` | `int=1 int=2 iters=3` | `int=1 int=2 iters=3` |
| `rsg` bench | 1000 blank lines | 5000 lines / 1604 distinct | 5000 lines / 1604 distinct |
| Full suite | 249/12/32 | **250/11/32** | — |
| `honest_icon_correctness.sh` | 7/8 IDENTICAL | **8/8 IDENTICAL** | — |

`not` repro and s164 scan repro both remain fixed (not regressed by this change).

---

## PART 2 — JCON SELF-HOST 7-MODULE GAP ROOT-CAUSED

### Background

Live cursor claimed `key()` ordering was "the sole remaining self-host divergence". This session
ran SCRIP-jtran on **all 17 modules** individually, not just `irgen.icn`.

### Module-by-module results

| Module | SCRIP classes | Oracle classes | Verdict |
|---|---|---|---|
| dump | 5 | 5 | COMPLETE ✅ |
| do_ops | 0 | 4 | SHORT ❌ |
| preprocessor | 8 | 29 | SHORT ❌ |
| lexer | 6 | 8 | SHORT ❌ |
| ast | 1 | 1 | COMPLETE ✅ |
| parse | 47 | 47 | COMPLETE ✅ |
| ir | 1 | 1 | COMPLETE ✅ |
| keyword | 2 | 2 | COMPLETE ✅ |
| **irgen** | **113** | **113** | **COMPLETE ✅** |
| gen_bc | 42 | 87 | SHORT ❌ |
| gen_symbolic | 9 | 9 | COMPLETE ✅ |
| gen_dot | 6 | 6 | COMPLETE ✅ |
| gen_ucode | 60 | 60 | COMPLETE ✅ |
| optimize | 3 | 17 | SHORT ❌ |
| interface | 0 | 65 | SHORT ❌ |
| bytecode | 9 | 50 | SHORT ❌ |
| jtran_main | 9 | 9 | COMPLETE ✅ |

**10/17 COMPLETE, 7/17 SHORT.**

### Root cause of the 7-module gap: elided start-position argument in `many`/`any`

SCRIP's runtime `many()` and `any()` builtins fail when the start-position (3rd) argument is
**elided** — passed as `&null` via Icon's empty-slot syntax `f(a,,b)`.

**Minimal repro (runs correctly under iconx, fails under SCRIP):**
```icon
procedure main();
   write(image(many('ab', "aab", , 0)));   # iconx: 4; SCRIP: fails
   write(image(any('a',  "aab", , 0)));    # iconx: 2; SCRIP: fails
   write(image(upto('b', "aab", , 0)));    # iconx: 3; SCRIP: 3 (CORRECT — upto unaffected)
end
```

**Causal proof:** `lexer.icn` contains exactly two `many(cset,,,limit)` calls in `lex_quoted`.
Replacing both elided slots with explicit `&subject, &pos`:
```icon
many('0123456789abcdefABCDEF', &subject, &pos, &pos+2|0)
many('01234567',               &subject, &pos, &pos+3|0)
```
takes `lexer.icn` from **6 classes → 8 classes** (oracle parity), error 500 gone.

**Why the error is 500:** the failing modules hit `default: runerr(500, p)` in `ast2ir`
(`irgen.icn`) because SCRIP's broken `many`/`any` execution corrupts the parse result, which
then delivers a node type the dispatch doesn't recognise.

**`upto` is correct; `many` and `any` are not.** The fix lives in the runtime builtin
implementations. The prior FINDING-2026-07-24-...-ANY-MANY-UPTO-2ARG-STARTPOS-FIXED covered
the 2-arg form; the elided-slot (3-arg with slot 3 empty) form was not covered.

### Second trigger: trailing semicolon in braced compound (SCRIP-jtran front-end, lower priority)

A separate, independent trigger produces error 500 in the JCON pipeline:
```icon
procedure f(s); { tab(0); }; end   # SCRIP-jtran: rc=1 error 500
procedure f(s); { tab(0) };  end   # SCRIP-jtran: rc=0
```
The trailing `;` inside the brace produces a `TT_NUL`/empty-expr node at the tail of the
compound; `ast2ir` hits `default: runerr(500, &null)` on it. This is distinct from the
`many`/`any` defect and from the `FZ-B1/FZ-B2` cluster. Not confirmed as the primary cause
of any specific module failure (all seven short-circuit modules have elided-slot `many`/`any`
calls; this trigger may contribute additionally in `gen_bc`, `bytecode`, `optimize`).

### ir.class blowup (SEPARATE — not explained by key() ordering)

`ir.class` is **142,605 bytes (SCRIP) vs 14,860 bytes (oracle)** — 9.6×. Across all of
`irgen.icn`: 625KB vs 451KB, 77 files larger / 22 smaller / 14 equal. Constant-pool reordering
from `key()` ordering cannot produce size changes of this magnitude; there is a second defect
in JVM bytecode generation independent of the ordering issue. Not yet diagnosed.

### `do_ops.icn` divergence confirmed (key() ordering, not a new defect)

SCRIP generates `do_ops.icn` (611 lines, same count as oracle) with **operators in different
order** (`%` first vs oracle's `@` first). Only ordering differs; operator set identical.
This was the documented `key()` defect. Confirmed still present, still the root cause for
`do_ops` short-circuit.

### Performance benchmark (10 verified-equal-work modules, RT_OPT=-O0 vs iconx -O)

| Module | SCRIP ms | iconx ms | Ratio |
|---|---|---|---|
| ir | 23 | 14 | 1.64× |
| ast | 29 | 16 | 1.81× |
| keyword | 22 | 12 | 1.83× |
| jtran_main | 68 | 34 | 2.00× |
| gen_symbolic | 95 | 47 | 2.02× |
| parse | 733 | 360 | 2.03× |
| gen_dot | 112 | 49 | 2.28× |
| gen_ucode | 1237 | 509 | 2.43× |
| dump | 139 | 49 | 2.83× |
| **irgen** | **6230** | **1396** | **4.46×** |
| **GEOMEAN** | | | **2.22× slower** |

All timings labeled RT_OPT=-O0. `iconx` was built `-O`. Asymmetric in SCRIP's disfavor.
`gen_bc`/`lexer` excluded — they short-circuited (unequal work). Previously reported 0.79×
for `gen_bc` was a false reading (42 vs 87 classes emitted).

Translator compile times: `scrip --compile` (17 mods) = 6.2s → 514,385 asm lines, 0 bombs;
`icont` (17 mods) = 80ms → iconx bytecode. Both produce `jtran` that compiles `irgen.icn`
to 113 valid `CAFEBABE` class files + `links` file byte-identical to oracle.
