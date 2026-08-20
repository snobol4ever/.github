# FINDING s184 — THE STORED-PATTERN MEMO COMPARED A DANGLING FRAGMENT-AST POINTER AGAINST ITSELF

**Seat:** seat4 (Opus 5), 2026-08-20, queue row 1 `m1-composed-wild-jump`. **Tree:** SCRIP `30a705de`, corpus `cdcebe25`, **pristine build at RT_OPT=-O0** (`make pristine`, rc=0) before every verdict below, and **re-proven after the rebase** that brought in seat-N's `8d7c5917`.
**Brief:** extend the s183 ladder with beauty's remaining ingredients IN ORDER — value-capture inside a composed element, the OPSYN'd operators, `epsilon ~ ''`, then MUTUAL recursion. ASM-DIFF-FIRST; gdb last.

## ⭐ THE HEADLINE — ONE MEMO HAS THE GUARD, ITS TWIN NEVER RECEIVED IT
`sno_expr_collect` (`lower_snobol4.c:86`) has carried a salt guard on its memo since the `EXPR$<n>F<salt>` naming landed:
```c
if (g_sno_exprs[i].salt == g_sno_expr_salt && sno_expr_eq(g_sno_exprs[i].expr, expr)) return …;
```
`sno_pat_collect` (`:1929`), the STORED-PATTERN twin, compared **`sno_expr_eq` alone**. Without the guard a `g_sno_pats[]` row's `pat` is a **DANGLING pointer into an EVAL fragment AST that `ast_tree_free_dyn` already released**. The arena hands the 5th fragment the 1st fragment's addresses, and `sno_expr_eq`'s opening `if (a == b) return 1;` then declares two unrelated patterns identical **without reading a single field** — so composed element 5 is wired into element 1's blob.

**This is s183's shape one function over.** s183: *"s121 half B1 solved this exact problem for the STATIC road and the JIT road never received it."* s184: the salt guard was written for one memo and never given to the other.

## THE PROOF, MEASURED NOT INFERRED (gdb, plain build, no monitor, no ZSM)
`probe/passthru/ptw_min_epsshift8` — eight `epsilon ~ 'x'` elements, i.e. beauty's `Stmt` empty-alternative run:

| fragment | incoming `pat` | rows 0..3 hold | outcome |
|---|---|---|---|
| 1..4 | `0x43e180` `0x43dd70` `0x43e0b0` `0x43f300` | filling | miss → `PAT$0..PAT$3` |
| **5..8** | **`0x43e180` `0x43dd70` `0x43e0b0` `0x43f300`** | the identical four | **`a == b` HIT — `npat` FREEZES at 4** |

At match time the deferred-capture records read `*EXPR$0F1 *EXPR$1F2 *EXPR$2F3 *EXPR$3F4` — **twice**, so the program prints `a b c d a b c d` where the oracle prints `a b c d e f g h`. Cross-checked: `sno_expr_collect` minted **eight distinct** `EXPR$kF<salt>` names and `rcp_of` minted **eight distinct** `OPQ$k` over **eight distinct DTP pointers** — every layer below the memo was already correct.
⛔ **The EVAL chain cache was exonerated first, by measurement:** all eight keys are textually distinct (`GET`/`PUT` traced), all eight miss and compile fresh. So is the count: the wrap is **not** mod-4 but "however many fragments the arena allocates before recycling" — the 1-capture variant wraps after **5**, not 4.

## THE LADDER THAT GOT THERE (the brief's order, and what each rung answered)
| rung | verdict |
|---|---|
| value-capture `. var` / `. *fn()` in a composed element | **GREEN** — cured by s183 |
| the same through `EVAL` of a **formal parameter** | RED (separate class, filed below) |
| OPSYN'd `~` / `&` operator as a composed element | RED (separate class, filed below) |
| **`epsilon ~ ''`, ONE** | GREEN |
| **`epsilon ~ ''` × 4** | GREEN |
| **`epsilon ~ ''` × 6 and × 8** | **RED — this rung** |
| mutual recursion (X3/X4/Expr5 chain) | GREEN with and without ARBNO |

FENCE, parens and nesting are all irrelevant — **only the element count matters** — and six *distinct* target functions wrap identically, so the aliasing is POSITIONAL, not name-keyed. Splitting the build across six statements does not move it, which put the defect runtime/lowering-side, not in single-statement lowering.

## THE CURE — PATSALT (`SCRIP_PATSALT=0` restores the unguarded memo)
The salt guard, transplanted verbatim, plus a `salt` field on the existing `g_sno_pats[]` row. **Zero new globals**: an existing table's row widens (the `g_sno_seal` `val` precedent RULES already blesses) and the killswitch is a function-local `static` (the `rt_defer_xpat_on` construction). Every static pattern is collected at salt 0, so **the guard is inert for a program with no EVAL**.

## RECEIPTS (pristine, RT_OPT=-O0; every A/B is the killswitch, never a recorded number)
- **CURED, oracle-identical:** `ptw_min_epsshift6` · `ptw_min_epsshift8` · `ptw_min_epsshift_distinct`. Control `ptw_min_epsshift4_ctl` (4 elements, under the wrap) unchanged in both arms.
- **CORPUS m3 332/5 · m4 325/11 — FAIL-SET BYTE-IDENTICAL** across the A/B (`diff` empty), measured both arms, and **re-measured at the post-rebase HEAD**.
- ⭐ **BLAST RADIUS ZERO.** 1254 mode-4 `.s` md5s swept in both arms → **1** differing row, `programs/snobol4/parser/unary_not.sno` — which **self-differs four times in the control arm**. A second control-arm sweep names that same single row as the entire noise floor, so the true mover count is **0/1254**. All five RULES step-4 regens independently report `No changes`.
- **PASSTHRU BOARD m3 127 → 130 (+3), m4 117/139 unchanged.** Red-set diff is **removals only** — a pure cure, zero new reds.
- **BEAUTY: 12 false pattern-identity collisions removed** — `npat` 74 → 86 on the one-byte input. Twelve of beauty's runtime-composed patterns were being wired into a *different pattern's* blob.

## ⛔ BEAUTY STILL SIGSEGVs — STATED PLAINLY, NOT BURIED
`printf '\n' | scrip beauty.sno` is **still rc=139** in both arms. This rung does not finish M1; it removes one wall standing behind it. The brief's DONE-WHEN — *a standalone oracle-refed witness that reproduces rc=139 and is green under `SCRIP_RTSEQ_RESUME=0`* — **is NOT met**: every witness minted this session is a wrong answer, not a crash, and every one is red in **both** arms of `SCRIP_RTSEQ_RESUME` (i.e. pre-existing, not s183's rung). The row is not finished.
**What the input shape says, and it is new:** beauty segvs on `\n`, on `X\n`, on `\n\n` — the **empty-statement / bare-label** road — but answers `Parse Error` (rc=0) on `  A = 1` and is **correct** on `* hi`. Empty input is correct. So the crash road is `Stmt`'s empty alternative, which is the four consecutive `epsilon ~ ''` this rung's witness class was minted from.

## TWO SEPARATE CLASSES FILED, BOTH OWED (witnesses checked in, corpus `cdcebe25`)
1. **A generator in ARGUMENT position dies.** `mk(ARBNO('a'))` → `nomatch`; `A = ARBNO('a'); mk(A)` → `match`. `SPAN`, `LEN`, `BREAK`, `ARB`, and a bare alternation in the same slot are all GREEN — **only `ARBNO`, only when constructed in the argument slot**. `ptw_min_argpat_arbno` + two controls.
2. **The OPSYN'd binary operator loses the whole blob.** One line apart: `ARBNO('a') reduce("'A'", 1)` → `match`; `ARBNO('a') ("'A'" & 1)` → `nomatch`. **ASM-DIFF (before any gdb):** the green arm emits a 115-line `FN__PAT$N` blob with `match_arbno_α/β/as/af`; **the red arm emits no `PAT$` blob at all** — the OPSYN'd operator keeps the expression off the static road entirely. `ptw_min_opsyn_elem` + `ptw_min_opsyn_named_ctl`.
3. Incidental: `ptw_min_opsyn_named_ctl` is **m3-green, m4-red** — an m3≢m4 divergence, which is a design-invariant violation.

## NEXT, IN ORDER
1. **Beauty's remaining SIGSEGV**, now with a three-input handle (`\n` / `X\n` crash · `  A = 1` `Parse Error` · `* hi` correct) that brackets the crash to `Stmt`'s empty alternative.
2. Class 2 above — the OPSYN'd operator's missing blob is a *static-road refusal*, cheap to chase and it is on every beauty grammar line.
3. Class 1 — `ARBNO` in argument position.
4. The m3≢m4 divergence on `ptw_min_opsyn_named_ctl`.
