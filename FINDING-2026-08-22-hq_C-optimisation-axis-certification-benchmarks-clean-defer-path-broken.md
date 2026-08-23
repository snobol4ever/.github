# FINDING — the optimisation axis, certified: hq_P's benchmark corpus is CLEAN at `-O2`; the defer/nested-match path is not

**Seat:** `hq_C` · **Date:** 2026-08-22 (s258) · **Tree:** SCRIP `3f951354` · **Class:** MEASURED · **Origin:** Lon, in-chat — *"Would it not be best to concentrate on getting completeness for all things related to performance so that your partner HQ SEAT can have a better time?"*

## THE ANSWER hq_P NEEDED: TAKE YOUR `-O2` NUMBERS

All 15 benchmark programs carrying a `.ref`, run in **fixed-work mode** (`echo 200 | scrip prog.sno` — the deterministic arm used under callgrind), grading the deterministic `check:` line:

| RT_OPT | result |
|---|---|
| `-O0` | **15/15 OK** |
| `-O2` | **15/15 OK** |
| **arm delta** | **ZERO — no program changes behaviour between the arms** |

hq_P's three P-0 kernels specifically: `roman` OK/OK · `table_access` OK/OK · `string_manip` OK/OK.

## SO THE `-O2` BREAKAGE IS NARROW, AND THAT IS THE USEFUL HALF

It hits the **pattern-defer + nested-match** path and nothing else found so far:

| program | `-O0` | `-O1` | `-O2` |
|---|---|---|---|
| beauty self-host (m3 and m4) | 40,971 ✅ | 278 ⛔ | 278 ⛔ |
| `161_pat_defer_fn_nested_match` | matches oracle ✅ | **SEGV rc=139** ⛔ | **wrong answer, rc=0** ⛔ |
| all 15 benchmarks | ✅ | — | ✅ |

Corpus delta `-O0`→`-O2`: m3 357/359 → **355/359**, m4 355/359 → **354/359**. The two new reds are `161_pat_defer_fn_nested_match` (both modes) and `demo_porter` (m3).

## ⭐ THE WITNESS IS 17 LINES — AND IT CORRECTS THE STANDING ROW

`corpus/crosscheck/patterns/161_pat_defer_fn_nested_match.sno`, **703 bytes**, reproduces the whole thing:

```
oracle : fail / calls=1 / match2 / calls=2
-O0    : fail / calls=1 / match2 / calls=2     ✅
-O1    : SEGV (rc=139, core dumped)            ⛔
-O2    : fail / calls=1 / fail2  / calls=3     ⛔  wrong answer, no crash
```

**Three different behaviours at three optimisation levels on seventeen lines.** This is the minimal witness the whole C-0 hunt needed, and the corpus handed it over as soon as the corpus was run on the optimised arm — which had never been done.

⛔ **It corrects `161-o2-red`, which is a standing rank-8 row.** That row states the test *"SEGVs BOTH modes at -O2 only."* Measured: it does **not** SEGV at `-O2` — it returns rc=0 and silently computes the wrong answer; it SEGVs at **`-O1`**. That matters because the two point at different hunts: a SEGV suggests memory corruption, while a wrong answer with an **extra function call** (`calls=3` vs `calls=2`) points at control flow and evaluation count.

## THE MECHANISM, AS FAR AS IT IS MEASURED

The witness's own header names it: *"`*F()` deferred value: re-fetched at EVERY match-time reference … F's body runs a NESTED MATCH — which clobbers r14/r15 inside the callee graph."*

`rtx_abi.inc` declares **r14 and r15 as BLOB PINS** — `r14 delta` (subject cursor), `r15 Delta` (subject length/end) — long-lived global machine state, not per-frame values. And:

| RT_OPT | `%r14`/`%r15` references in `pattern_match.o` |
|---|---|
| `-O0` | **0** |
| `-O1` | **621** |
| `-O2` | **686** |

At `-O0` GCC never allocates r14/r15 in the matcher, so the pins survive by accident. From `-O1` on it uses them heavily. r14/r15 are callee-saved under SysV, so GCC restores them **when a C function returns** — but a pin must hold **while C is running**, and SCRIP re-enters emitted code *from inside* C on a deferred `*F()` with a nested match. The ABI guarantee and the pin discipline are answering different questions.

⛔ **HYPOTHESIS, NOT YET PROVEN — marked as such.** What is measured is the register-count table, the three-point curve, and the pin declaration. The causal chain above is inference and the next seat should try to refute it.

⛔ **A correction to my own earlier pass:** I first reported `rtx_match.S` and four `rtx_icn*.S` files as "uses r14/r15 but never saves them." That was **grep counting COMMENT text**, not instructions — those files *document* that the pins are preserved. Retracted.

## ⛔ AND A HARNESS FAILURE OF MY OWN, RECORDED BECAUSE IT IS THE CLASS I POLICE

My first certification run reported **0/17 OK in both arms**. That was not 17 broken benchmarks; it was my comparison. These programs are **time-based by default** and print nondeterministic `iters:`/`ns:`/`ms:` lines, while each `.ref` holds only the deterministic `check:` value — so a full-stdout diff can never match. A complete, plausible, entirely false all-FAIL table, produced by the seat that spent the day warning others about exactly that.

⭐ **What caught it: 0/17 in BOTH arms is not the shape a real defect makes.** A genuine optimisation bug is selective. **A result too uniform to be interesting is evidence about the instrument, not the subject** — the same lesson as *"BAD as expected"* is not a measurement, arriving from the opposite direction.

## ⭐⭐⭐ LOCALISED: THE WHOLE OPTIMISATION DEFECT IS TWO FILES OUT OF 261

Two automated file-level bisections over every runtime object (bounds confirmed before each: all-`-O0` passes, all-`-O2` fails):

| bisect | target | rounds | culprit |
|---|---|---|---|
| #1 | `161_pat_defer_fn_nested_match` | 8 | **`src/runtime/rt/rt.c`** |
| #2 | beauty self-host (rt.c already at `-O0`) | 8 | **`src/runtime/pattern_match.c`** |

**With 259 of 261 objects at `-O2` and only those two at `-O0`:**

```
161 witness  : fail calls=1 match2 calls=2      = oracle  ✅
beauty m3    : 40,971 bytes  md5 6f1671c0...    FIXED POINT ✅
beauty m4    : 40,971 bytes  md5 6f1671c0...    FIXED POINT ✅
corpus       : m3 PASS=357 FAIL=2 · m4 PASS=355 FAIL=2 SKIP=2
```

That corpus line **is the `-O0` baseline exactly** — both `-O2`-only reds (`161_pat_defer_fn_nested_match`, `demo_porter` m3) are gone, and nothing else moved.

⛔ **THIS IS A WORKAROUND, NOT A FIX, AND MUST NOT BE SHIPPED AS ONE.** De-optimising two files hides real undefined behaviour rather than removing it; the same UB can resurface through any other file that inlines the offending code. What it buys is (a) a usable optimised build today and (b) a hunt narrowed from 261 files to 2. The real fix is in `rt.c` and `pattern_match.c`, and `-fsanitize=undefined` on exactly those two is the obvious next probe.

⭐ Note the interaction is **non-additive**: `rt.c` alone fixes the 17-line witness but leaves beauty broken (614 bytes — a third distinct signature, after 278 plain and 259 under `-ffixed-r14/r15`); `pattern_match.c` alone fixes neither. Beauty needs both. Whatever this is, it is one defect class reachable through two files, not two independent bugs.
