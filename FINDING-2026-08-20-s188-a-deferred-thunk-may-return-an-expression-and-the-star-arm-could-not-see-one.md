# FINDING — 2026-08-20 s188 (seat3, Opus 5; queue row `m1-class-b-stmt-parse-error`)

## ⭐ HEADLINE
**Class B is CURED, and it was ONE MISSING ARM.** `rt_defer_get_pat_dtp`'s STAR arm — the road a
compiler-minted deferred thunk takes — had a `DT_P` arm and **no `DT_X` arm**. Its by-name sibling ten lines
below has had one all along. When the thunk's result is itself an EXPRESSION (which is exactly what
`Expr = *Expr0` produces, manual v3.7 p.196), the star arm parked it and returned NULL; the site then fell to
the **SCALAR** road, which resolved the EXPRESSION correctly to a **genuine PATTERN** and handed that PATTERN to
`c_rt_defer_close` — a closer that can only literal-match a scalar, and therefore `-1`s it. **The pattern was
found and thrown away one line later**, in both media. beauty's object expression is reached exactly this way,
so `*Expr` silently failed and every real statement came back `Parse Error`.
Cured, killswitched (`SCRIP_DEFER_XSTAR`), landed at SCRIP `2c8d2b34`, with the **first standalone witness**
this class has ever had. **The four class-B beauty witnesses no longer print `Parse Error`; they now reach the
class-A SEGV of row `m1-composed-wild-jump` — precisely what the brief predicted curing B would expose.**

## WATERMARK — PRISTINE, ON THE REBASED TREE
`make pristine`, RT_OPT `-O0`, at SCRIP `2c8d2b34` (i.e. **after** seat8's false-accept fix `a2979dc6`, seat7's
SPAN-FRAME flip `d3251f23` and seat1's `6d4cab2d` landed under this seat) · corpus `1f3f3637`:
- broad corpus **m3 332/5 · m4 325/11 SKIP 1** — the standing watermark, unchanged
- ⭐ **the ENTIRE 337-program × 2-mode log is BYTE-IDENTICAL across the killswitch.** Zero blast radius.
- crosscheck **m3 312/5 · m4 308/8 SKIP 1 DIVERGE 3** — the s184 watermark, unchanged
- Icon crosscheck 4/0 · Prolog fail-set **identical by name** (see §6 — its NATIVE-ABORT bucket is load-flaky)
- all five RULES step-4 regen scripts: **ZERO `.s` artifacts moved** (runtime-only change, as expected)
- `test_gate_emit_no_lang.sh` OK · BOTH-MEDIUM ratchet **0** · **zero new globals**

## 1. THE ROAD, IN THREE TRACE LINES — AND THE SAME THREE IN A 10-LINE STANDALONE
A `getenv`-gated `[DFR]` trace at every `DT_X` decision point in `pattern_match.c`, over beauty's failing run on
`m1_lad_stmt`, produced **exactly one** `DT_X` sighting in 1176 events:

    get_pat_dtp ENTER    nm=*EXPR$162
    get_pat_dtp STAR     nm=*EXPR$162 thunk.v=0x58(DT_X) thunk.s=EXPR$77
    run_all  STAR-park   nm=*EXPR$162 park.v=0x58 final.v=0x8(DT_P) close=-1

The emitted asm names both thunks beyond argument: `FN__EXPR$162`'s body reads variable **`Expr`**;
`FN__EXPR$77`'s body reads variable **`Expr0`**. So `*Expr` → thunk → `Expr`'s value → `DT_X{EXPR$77}`.
`final.v=0x8` is `DT_P`: **the pattern WAS resolved**, on the road that can only close a scalar.
The standalone witness `m1_defer_x_thunk` produces the identical three lines (`*EXPR$1` / `EXPR$0`).

## 2. THE MANUAL IS THE AUTHORITY, AND IT NAMES THE CONTROLLING VARIABLE
Manual v3.7 **p.196** (Data Types → Expression): *"The unevaluated expression operator must be at the outermost
level to create an object of type EXPRESSION."* — so `Expr = *Expr0` yields an **EXPRESSION**, while
`Expr = epsilon *Expr0` yields a **PATTERN**. p.85-86: an EXPRESSION *"is only evaluated when referenced"*, and
deferred evaluation *"may also be applied to a pattern's alternate or subsequent clause or to the entire pattern."*
The datatype — not the spelling, not the depth — is the whole variable, confirmed by a four-row A/B run
in beauty itself with `util_beauty_override.sh`:

| `Expr =` | datatype | class B |
|---|---|---|
| `*Expr0` | **EXPRESSION** | **`Parse Error`** |
| `epsilon *Expr0` | PATTERN (concat) | **CURED** → class-A SEGV |
| `FENCE(*Expr0)` | PATTERN | **CURED** → class-A SEGV |
| `*Expr0 \| *Expr0` | PATTERN (alternation) | **CURED** → class-A SEGV |

The last two are new this session. `*Expr0 | *Expr0` is the sharpest of them: an alternation of one pattern with
*itself* matches exactly what the pattern matches, so it perturbs the *semantics* not at all and the *datatype*
entirely — and it cures.

## 3. ⭐ THE STANDALONE WITNESS, AND WHY NINE BUILD-UPS WERE GREEN
`corpus/probe/m1/m1_defer_x_thunk` (red pre-fix in BOTH modes) + `m1_defer_x_thunk_ctl` (green throughout),
**one datatype token apart**. The ingredient nine prior build-up attempts were missing is the **OPSYN'd binary
operator**: `lower_snobol4.c:1437` lowers `*V` with a plain `TT_VAR` inner to the **by-name** road (`op_sval` =
`"Expr"`), and only the fallback at `:1448` mints `*EXPR$n` via `sno_expr_collect`. beauty reaches that fallback
because `semantic.inc:7-8` OPSYNs `~`/`&` into the grammar-build expression. **The by-name road has had the
`DT_X` arm since s178, which is why every witness built up from ingredients agreed with the oracle** — the bug
lived on the road no minimal witness had ever taken. HQ's "ablate DOWN, don't build UP" was right for a reason
that is now nameable.

## 4. THE CURE — ONE ARM, AND ONE FEWER SPELLING THAN BEFORE
The bounded chain walk existed **twice** already (`rt_defer_take`, `rt_defer_xpat_dtp`) and was **missing** from
the third site. Rather than add a third spelling, it is extracted into `rt_dtx_drain` — ONE AUTHORITY — and all
three now call it. `DT_FAIL` (0x68) is not `DT_X` (0x58), so a failed hop exits the walk and every caller's own
`IS_FAIL` test still sees it; that is why `rt_defer_take` keeps its check and needs no per-hop one, and why the
extraction is behaviour-preserving rather than merely equivalent-looking.
**Evaluation count is unchanged on the scalar road**: the outer thunk ran once either way, and the inner hop
`run_all` used to make is the one now made in the drain. That is what keeps the scalar path — and the whole
corpus — byte-identical under the killswitch.

## 5. ⛔ ONE PRIOR OBSERVATION IS RETRACTED, NOT REFINED
The s186 FINDING recorded a **HEISENBUG** — "wrapping `Expr` in a tracer also cures class B". It is **not** a
heisenbug and nothing was destroyed by observing it: the tracer `@ea (epsilon $ *TR(...)) *Expr0 @eb (...)` is a
**concatenation**, so it changes `Expr` from EXPRESSION to PATTERN. It is the §2 A/B wearing instrument
clothing. Every "perturbation" reported at that site was the datatype flip; a tracer on `Command`, *outside*
`Expr`, left the datatype alone and duly did not perturb. ⛔ **Do not carry a heisenbug warning forward for this
class.**

## 6. ⛔ AN HONEST NEGATIVE AND A HARNESS FACT
- **The M1 board does NOT move.** `board_beauty_m1.sh --modes m3` reads **3/10, first red at 10**, byte-identical
  across the killswitch — because beauty already SEGVs (class A) at the 10-line rung, above where class B lives.
  The brief asked for the rung count to improve; **it does not, and that is the measurement, not an excuse.**
  What moved is the four class-B witnesses, which feed the FULL file a small input.
- **The Prolog crosscheck self-diffs.** Two consecutive runs of the SAME binary gave `PASS=110 FAIL=1 SKIP=78`
  and `PASS=109 FAIL=1 SKIP=79`; the float is entirely inside the `NATIVE-ABORT … native emit unimplemented`
  bucket (one row even reports `rc=132` vs `rc=139` between runs). **Self-diff the control arm before reading a
  one-row Prolog delta as a regression** — this seat did, which is the only reason the delta was not filed as one.

## 7. NEXT
Class B is closed. The four witnesses now sit on **class A** (`m1-composed-wild-jump`), which is a different
queue row and is unblocked by this landing — its own brief says a standalone witness could not be built for it,
and it should now be re-tested first, since the road this rung fixed is the road its `*Stmt` reduction runs on.
Still open and untouched, both from the s186 FINDING and unaffected by this cure:
`m1_trailing_ws` (SCRIP's front end rejects a statement with trailing whitespace and no goto field —
investigation-only, and beauty has zero such lines) and `rt_defer_take`'s dead `DT_X` arm in `rt_patv_defer_open`
(callers pre-set `dtx_used`) — its own rung, witness first.
