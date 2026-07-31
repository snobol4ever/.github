# GOAL-DESCR-TAG-ENCODING.md — CLASS-IN-THE-LOW-TWO-BITS DESCR TAGS

**Minted s228 (2026-07-31), Lon + Claude. DESIGN ONLY — NOT LANDED, NOT MEASURED. Do not cite any number here as a result.**

## 1. THE ENCODING (Lon, s228)

`tag & 3` is the CLASS:

| low 2 | class | members |
|---|---|---|
| `00` | other / aggregate | everything non-scalar |
| `01` | integer | `DT_I` |
| `10` | string | `DT_S`, `DT_SNUL` |
| `11` | real | `DT_R` |

**Within the string class, bit 2 separates NULL from non-NULL** (Lon's refinement): `DT_S = 2`, `DT_SNUL = 6`. So string-ness and null-ness are two independent single-bit tests instead of two compares.

⭐ **VALUE 4 IS DELIBERATELY UNUSED.** No type may take it, so the constant `4` is free to serve as the null-mask immediate without ever colliding with a real tag. `DT_A` currently occupies 4 and MUST move.

```c
DT_I    =  1,   /* 01 — the ONLY tag == 1  */
DT_S    =  2,   /* 10 — string, has chars  */
DT_R    =  3,   /* 11 — the ONLY tag == 3  */
/*         4      RESERVED — null mask, never a type */
DT_SNUL =  6,   /* 10 | 4 — string, null   */
DT_P    =  8, DT_A = 12, DT_T = 16, DT_C = 20, DT_N = 24, DT_K = 28,
DT_E    = 32, DT_FH = 36, DT_PLVAR = 40, DT_PLREF = 44, DT_X = 48,
DT_BLK  = 52, DT_FAIL = 96, DT_DATA = 100,       /* all ≡ 0 mod 4 */
```

## 2. THE TESTS THAT FALL OUT

| predicate | code | today |
|---|---|---|
| both int (**hottest**) | `or eax,ecx` · `cmp eax,1` | 2 cmp + **2 branches** |
| both real | `and eax,ecx` · `cmp eax,3` | 2 cmp + 2 branches |
| both numeric | `and eax,ecx` · `test al,1` | per-operand compares |
| is scalar | `test al,3` | — |
| is string family | `and al,3` · `cmp al,2` | `cmp al,DT_S` · `ja` |
| is NULL string | `test al,4` (after class) | separate compare |

⭐ **THE OR/AND DUALITY IS THE HEART OF IT.** `DT_I` is the only tag equal to 1, so `(L|R)==1` ⟺ both int. `DT_R` is the only tag equal to 3, so `(L&R)==3` ⟺ both real. Neither needs a per-operand branch.

⭐ **MEASURED s228: 156 sites discriminate SNUL from S** (126 C + 30 asm) ⇒ the bit-2 split is not a micro-optimisation, it is the commonest tag question in the tree after "is it a string at all".

## 3. ⛔ TWO LANDMINES — BOTH BUILD CLEAN AND FAIL AT RUNTIME

1. **`DT_FAIL = 99` ⇒ `99 mod 4 == 3 == REAL`.** FAIL would test as numeric in every `and/test al,1` guard. Move it to ≡0 mod 4 (96 above). ⚠ This is the single most dangerous line in the migration: nothing in the build catches it, and it only fires in arms that reach FAIL with a numeric guard upstream.
2. **`DT_SNUL` must stay in the STRING class.** Today `SNUL=0, S=1` powers a `tag <= DT_S` unsigned trick (`rtx_arith.S:75`). If SNUL fell into class `00` that trick dies and the STRING arm gets *worse*, not better.

## 4. ⛔⛔ THE GREP THAT WILL LIE TO YOU (measured s228)

Searching for relational tag tests returns **EMPTY**, and it is a **FALSE NEGATIVE**. `rtx_arith.S:75` is exactly such a test:
```
cmp  eax, DT_S
ja   .Lcd_real
```
The `cmp` and the `ja` are on **SEPARATE LINES**, so a line-oriented grep cannot see the pairing. A session that runs that grep concludes "no relational tests, safe to renumber" and is WRONG.
⇒ **Find range assumptions by READING each arm, or by a two-line-window grep. Never by a single-line pattern.** Same false-null class as the census contamination (§ s228 FINDING) and the `rt_dcap_lazy_init` zero.

## 5. FEASIBILITY — SMALLER THAN IT LOOKS

✅ **The asm is SYMBOLIC.** `DT_*` are `#define`s in `src/runtime/rtx/rtx_abi.inc`, pulled into every `.S` through cpp. Renumber `descr.h` + `rtx_abi.inc` in lockstep and the assembly follows automatically. No hand-edited immediates.
✅ 12 `_Static_assert`s in `rtx_init.c` already reference DT_/tag and will catch some drift.
⛔ **NOT CONCURRENCY-SAFE.** Touches `descr.h`, `rtx_abi.inc`, every `.S`, and the templates, while the ζ ladder holds 41 red pattern programs.

## 6. ⚠ DESIGN PUSHBACK — DO NOT LEAD WITH A 16-WAY INDIRECT DISPATCH

The 4×4 matrix is real (`idx = (L&3)<<2 | (R&3)`; both-numeric ⟺ `idx & 5 == 5`), but a `func[idx]` indirect **call** with 16 targets is a branch-target-predictor hazard — a mispredict (~15–20 cycles) can exceed the entire integer add being accelerated. Only 4 of 16 cells are the numeric×numeric quadrant; the other 12 are string-coercion and error paths that are cold.

**Preferred shape:** inline `or/cmp` for int-int (the dominant cell) → `and/test al,1` for both-numeric → bit 1 of each tag selects int-vs-real, a 2×2 with **no table at all**. If a table is still wanted for the cold quadrant, use `jmp [tbl+idx*8]` INSIDE one function — no ABI spill, no PLT, one I-cache footprint.

## 7. ⛔ MEASURE THIS FIRST — THE RUNG MAY BE AIMED AT A BYPASSED PATH

s203 recorded that integer inlining made `rt_num_arith` go **cold** — the emitter learned to inline the int case and stopped calling the dispatcher. **Run 0(d) on `arith_int`/`arith_loop`/`arith_mixed` BEFORE renumbering** to confirm the arithmetic dispatcher is actually entered. If it is not, this rung optimises a path the emitter already bypasses — the RTX-7 "bypassed family" class, and the exact reason five sessions produced no speed number.

⚠ And per the s228 rule: `sbl.asm` **does** have a mixed-mode arithmetic dispatcher, so unlike `comm_var` this family has a real oracle counterpart — check the shape there before choosing ours.

## 8. STEPS

- [ ] **TAG-0** 0(d) on the three arith benchmarks — is the dispatcher entered at all? If no, STOP and re-aim.
- [ ] **TAG-1** Read `sbl.asm`'s mixed-mode arithmetic dispatch; record the shape.
- [ ] **TAG-2** Two-line-window audit of EVERY relational/range assumption on `.v` (§4 — the single-line grep lies).
- [ ] **TAG-3** Renumber `descr.h` + `rtx_abi.inc` in ONE commit; move `DT_A` off 4; move `DT_FAIL` off 99. Watermark must hold EXACTLY.
- [ ] **TAG-4** Replace per-operand compares with the OR/AND forms, one family at a time, each gated.
- [ ] **TAG-5** Only then consider the 2×2 (NOT the 16-way call).
