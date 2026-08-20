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

---

# ADDENDUM 1 — THE CLASS-A WILD JUMP IS `RETURN` POPPING Δ OFF THE ζ-SPINE

Written after HQ's three mid-session messages arrived (row `a-m1-composed-wild-jump`). **HQ's numbers were taken at SCRIP `ffbc1425`; the polarity has MOVED at HEAD `2dbb8a56` and the ladder must be re-taken.**

## ⛔ HQ'S MINIMAL CRASHER NO LONGER CRASHES — THE WALL MOVED ONE ELEMENT RIGHT
Same harness (copy the beauty dir, override ONE grammar line, feed `m1_lad_empty.in`), 3–5 runs each, at HEAD:
| override | HQ @ `ffbc1425` | HEAD `2dbb8a56` |
|---|---|---|
| `Parse = *Stmt nl` | **CRASH** | **rc=0, 3/3** — cured, and cured in ALL THREE arms (default · `SCRIP_PATSALT=0` · `SCRIP_RTSEQ_RESUME=0`), so **not** by this session's PATSALT |
| `Parse = *Stmt ("'Stmt'" & 7) (nl \| ";")` | **CLEAN** (HQ: *"inserting an epsilon-capture between the defer and the variable CURES it"*) | **rc=139, 5/5** |
| `Parse = nPush() ARBNO(*Command) ("'Parse'" & 'nTop()') nPop()` (the real line) | rc=139 | rc=139 default · rc=139 `PATSALT=0` · **rc=0 `RTSEQ_RESUME=0`** |
**So HQ's discriminator (3) is inverted at HEAD: the intervening epsilon-capture no longer cures — it is now REQUIRED to crash.** Anything resting on it should be re-taken.

## THE REDUCED WITNESS — THREE GRAMMAR LINES, ONE-TOKEN GREEN/RED PAIR
`scripts/util_beauty_m1_reduce.sh` (checked in; `--green` for the control) applies:
```
Label = epsilon ~ 'Label'
Stmt  = *Label *Label          ← RED (rc=139, 5/5).   *Label alone ⇒ GREEN (rc=0, 5/5)
Parse = *Stmt ("'Stmt'" & 7) nl
```
**All three ingredients are load-bearing, each removable one token at a time:**
| ablation | rc |
|---|---|
| `*Stmt ("'Stmt'" & 7) nl` | **139** |
| `*Stmt reduce("'Stmt'", 7) nl` (named call, not the OPSYN'd operator) | **139** — so the operator spelling is NOT the discriminator |
| `*Stmt ("'Stmt'" & 7)` · `*Stmt reduce("'Stmt'", 7)` (drop the tail) | 0 |
| `*Stmt ("'Stmt'" & 7) ";"` (**literal** tail instead of the variable `nl`) | 0 |
| `*Stmt "" nl` · `*Stmt LEN(0) nl` · `*Stmt "" "" nl` (middle is not a call result) | 0 |
| `*Comment ("'Stmt'" & 7) nl` (leading defer to a **static** pattern) | 0 |
So the shape is **defer-to-a-runtime-composed-pattern + a function-call-result element + a VARIABLE-held operand**, and `Label` reduces all the way to `epsilon ~ 'Label'`.
⛔ **A standalone (no-include) witness still does not reproduce** — two attempts, both oracle-identical. This confirms HQ's negative result: **beauty's include context is load-bearing.** The reduction script is therefore the artifact, not a `.sno`.

## ⭐⭐ THE ROOT CAUSE, MEASURED — `RETURN` POPS Δ AND JUMPS TO IT
gdb on the reduced RED witness (plain build, `CSN_NO_SEGV_HANDLER=1`, no monitor, no ZSM):
```
rip = 0x7ffff7ffd000   (_rtld_global, .data of ld.so)   bt: #1 0x0 — destroyed, as the brief warned
rcx = 0x7ffff7ffd000   r15 = 0x7ffff7ffd000   r13 = 0x0   r14 = 0x41bd68
rsp = 0x7fffffff88c0   [rsp-24] = 0x7fff8e0196c0   [rsp-16] = 0x00007ffff7ffd000   [rsp-8] = 0x41bd68
```
There are exactly **158** `jmp rcx` sites in the emitted `.s`, and a census of the instruction feeding each one places the crash: 78 set `rax, rdi` (γ), 78 set `eax, 104` (ω), and **two are the global trampolines**
```
RETURN:   pop rcx
          add rsp, 8;   jmp rcx
```
`rax = 0xffffffff` matches neither γ nor ω arm (no site anywhere sets `eax` to −1), and `pop rcx; add rsp,8` leaves `rsp` exactly where it started — which is what the crash shows. **`rcx` was loaded from `[rsp-16]`, and `[rsp-16]` holds `0x7ffff7ffd000` = the live `r15`.**

**R13/R14/R15 are Σ/δ/Δ** (register contract of record). The three words under `rsp` are **`[rsp-24]=Σ` (a heap pointer), `[rsp-16]=Δ`, `[rsp-8]=δ`** — a match-state save frame sitting exactly where the function-call return record belongs.

> **IN ONE SENTENCE: a match-state save and a function-return record collide on the ζ-SPINE, so SNOBOL4's `RETURN` trampoline pops Δ as its continuation and jumps to it.**

This is not "a corrupted pointer" — it is an **RSP-depth accounting error of one spine cell per composed element**, which is why the crash is *element-count* sensitive (one `*Label` green, two red), why a **literal** tail is green while a **variable** tail is red (the variable operand allocates a spine cell the literal does not), and why HQ's ladder flipped polarity the moment another rung changed the depth by one.

## ⭐ POSSIBLY ONE FAMILY WITH seat7's s184 — CROSS-REFERENCE BEFORE EITHER IS FIXED
`FINDING-2026-08-20-s184-the-armed-carve-moves-rsp-and-no-flat-spine-operand-is-rebased.md` (seat7, row `span-frame-flip`) names *"the armed carve moves `rsp` for the whole graph and not one flat ζ-SPINE operand offset is rebased"* on `TDump_driver` under `SCRIP_SPAN_FRAME=1`. That is **a different witness and a different arm** — seat7's is a coherent wrong answer at α, mine is a wild jump through `RETURN` — but both are *"rsp moved and something that indexes off it was not told"*. Whoever fixes either should read the other first; a single depth-accounting authority may retire both.

## NEXT
1. **Find the unbalanced `sub rsp` / `add rsp` pair** on the runtime-composed concat road — the α that allocates a ζ-SPINE cell per element against the ω/whack that frees them. The green/red pair is one element apart, so their emitted `.s` differ by exactly that allocation.
2. Re-take any ffbc1425 ladder number (see the table above) before building on it.
3. `ptw_min_opsyn_elem` / `ptw_min_argpat_arbno` (FINDING body) remain owed and are unrelated to this jump.
