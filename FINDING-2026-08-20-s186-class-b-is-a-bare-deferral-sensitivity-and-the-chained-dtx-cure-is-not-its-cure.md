# FINDING — 2026-08-20 s186 (seat3, Opus 5; queue row rank 1 `m1-class-b-stmt-parse-error`)

## ⭐ HEADLINE
**Class B is NOT a parser bug, a FENCE bug, or a semantic-action bug. `*Stmt` MATCHES — it just stops ONE
CHARACTER SHORT (cursor 5 of 7 where the oracle reaches 6), so the terminator `(nl | ';')` sees `1` instead of
the newline and Command's third arm fails.** The controlling ingredient is ONE line, `beauty.sno:121
`Expr = *Expr0``, whose entire value is a **bare unevaluated expression**. Anything that makes that value a
CONCATENATION cures class B outright; anything that leaves it bare does not. **A genuine chained-`DT_X`
deferral defect was found on this road, root-caused, cured, killswitched and landed (SCRIP `06358b06`) — and it
is MEASURED NOT to be class B's cure.** Class B is investigation-only this rung, with the mechanism narrowed
to a one-line A/B and the next measurement named.

## WATERMARK
Broad corpus **m3 332/5 · m4 325/11 SKIP 1** — the s184/s185 watermark, unchanged, on BOTH arms of the new
killswitch, with output **byte-identical** and fail-sets identical by name. All five RULES step-4 regen scripts:
**zero `.s` artifacts moved** (runtime-only change, as expected). `test_gate_emit_no_lang.sh` OK. Zero new globals.

## 1. THE FOUR WITNESSES CONFIRMED, AND THE BRIEF'S UNMEASURED ITEM ANSWERED
All four class-B witnesses reproduce at HEAD, rc=0 with a wrong ANSWER (never a crash), and **all four `.ref`
files are LIVE** — byte-identical to today's oracle output, re-run this session, nothing pinned. SCRIP prints
`Parse Error` + the echoed source line; the oracle beautifies. Class A (`m1_lad_empty` · `m1_lad_barelabel` ·
`m1_lad_end` · `m1_lad_comment`) SEGVs, independent and untouched, exactly as the brief says.

⛔ **`SCRIP_RTSEQ_RESUME=0` CHANGES NOTHING** — all four witnesses are **byte-identical to the default arm**
under the killswitch. The brief flagged this as important and unmeasured: **class B PREDATES the s183 M1 rung.**

## 2. WHERE IT FAILS — MEASURED WITH beauty'S OWN IDIOM, NOT WITH A DEBUGGER
Instrumenting `Command`'s third arm with cursor capture and an immediate-assignment tracer
(`@qb (epsilon $ *TR('...' qb))` — beauty's own `. *fn()` ploy, manual v3.7 p.196) on `Src = " A = 1\n"` (7 chars):

| | oracle | SCRIP |
|---|---|---|
| `C1-try-stmt` | at 0 | at 0 |
| `C2-stmt-end` | **at 6** of 7 | **at 5** of 7 |
| `C3-after-reduce` | at 6 | at 5 |
| `C4-terminator-ok` | at 7 | **never reached** |

`Stmt` matched in both engines. The oracle took the arm `'=' ~ '=' *White *Expr` (object `1`, ending at 6);
SCRIP settled one short at 5 = after `' A = '`, i.e. the **empty-object** arm with `Gray` eating the trailing
space. Every non-empty object fails identically (`1`, `B`, `'x'`, `(1)`, `-1`, `1 + 2`, `F(1)`, `1 2`, `B C`)
while `` A ='' (empty object), `` A B'' (a match statement, which uses `*Expr1`), `` :(X)'', `` 'x''' and a bare
label all PASS — so the failing element is the OBJECT expression, not its content.

## 3. THE ONE-LINE A/B — `Expr = *Expr0` (beauty.sno:121)
| ablation | Expr's value | class B |
|---|---|---|
| `Expr = *Expr0` (HEAD) | bare `DT_X` | **PERR** |
| `Expr = (*Expr0)` | bare `DT_X` | **PERR** |
| `Expr = *(Expr0)` | bare `DT_X` | **PERR** |
| `Expr = epsilon *Expr0` | `DT_P` concat | **CURED** → class-A SEGV |
| `Expr = *Expr0 epsilon` | `DT_P` concat | **CURED** → class-A SEGV |
Parenthesising does not change the descriptor and does not cure; concatenating ANYTHING on EITHER side does.
Curing B exposes A on the same witness — exactly what the brief predicted.

## 4. ⛔ A HEISENBUG, AND WHY HQ'S "ABLATE DOWN, DON'T BUILD UP" IS LOAD-BEARING
Wrapping `Expr` in a tracer (`@ea (epsilon $ *TR(...)) *Expr0 @eb (...)`) **also cures class B** — the traced run
reports `Expr-enter@5 / Expr1-enter@5 / Expr1-exit@6 / Expr-exit@6`, identical to the oracle, then dies in class
A. Instrumenting `Command` (outside `Expr`) does NOT perturb. So the observable is destroyed by observing it at
the perturbing site, and every build-up repro of the shape is green. This is why the brief's method is the
method.

## 5. ⛔ FALSIFIED — DO NOT RE-DERIVE
1. **NOT the semantic actions.** `~`/`&` are OPSYN'd to `shift`/`reduce`, which build `p . thx . *Shift(...)` and
   `epsilon . *Reduce(t,n)` — **conditional** assignment, so by the manual (v3.7 p.62: *"assignment occurs only
   if the pattern match is successful"*) they are match-INERT. Confirmed by measurement: with `xTrace` on, the
   oracle emits 72 action lines and **SCRIP emits ZERO** — the match dies before any action runs.
2. **NOT the reduce `("'='" & 2)`, and NOT `Expr0`'s alternation.** An earlier ablation matrix appeared to convict
   both. **Every one of those verdicts was a FALSE GREEN** — see §7. Re-run hardened, all `Expr0` ablations
   diverge.
3. **NOT deferral depth.** Chains of 5/8/10/12/16/20 levels of `Pk = *P(k-1) epsilon` and of
   `Pk = *P(k-1) FENCE(epsilon)` (beauty's exact `ExprN` shape) are green in both engines.
4. **NOT head position.** `epsilon *P(k-1)` and `*P(k-1) epsilon` behave identically — bareness is the variable,
   position is not.
5. **NOT the chained-`DT_X` defect of §6** — measured, see §6's last paragraph.

## 6. ⭐ CHAINED `DT_X` DEFERRAL — TWO SEATS, ONE FACT, ONE SURVIVING SPELLING
⛔ **CONVERGENCE, RECORDED HONESTLY.** seat2 (row `defer-depth-floor`, SCRIP `fccc81cc`, `FINDING-…-s187-…`) root-caused the SAME fact independently and inside the same hour. The rebase merged BOTH loops into `rt_defer_xpat_dtp`; seat2's drain runs first, so this seat's loop behind it was **dead code**, and two spellings of one fact is the spelled-twice disease. **seat2 owns the row and seat2's line stays**; this seat's loop, its `#define` and its killswitch were removed in SCRIP `213771e2`, re-measured at watermark. What survives from this seat is the **ladder, the two witnesses, and the measurement that this cure is NOT class B's cure.** The original seat3 cure was SCRIP `06358b06`.
A pattern variable whose entire value is a bare unevaluated expression **IS** a `DT_X` descriptor. So resolving
`*P3` where `P3 = *P2`, `P2 = *P1` lands on ANOTHER `DT_X`, not on a pattern. `rt_defer_xpat_dtp`
(`src/runtime/pattern_match.c`) resolved **exactly one hop**, parked the intermediate `DT_X` and returned NULL,
which fails the match. Ladder, independent of leaf kind (`SPAN` or literal), of a preceding element and of `RPOS`:

    hops=1 both match · hops=2 both match · hops=3,4,5 oracle match / SCRIP NOMATCH

**Cure (seat2's, now the single authority):** drain the chain under a bounded cycle guard, then park the FINAL
value under the ORIGINAL name — so the close path still literal-matches a scalar tail and each expression still
runs exactly once.
Witnesses (they now stand as regression cover for seat2's cure, and both PASS under it): `corpus/probe/m1/`
`m1_defer_chain` (red pre-fix, green BOTH modes after) and `m1_defer_chain_ctl`
(the 2-hop control, always green — it is what proves the defect is the SECOND hop, not deferral as such).

⛔ **IT IS NOT CLASS B'S CURE, AND THAT IS MEASURED, NOT ASSUMED.** A gated `[DEFER]` trace over beauty's whole
failing run shows **69 defer events, of which exactly 7 are `DT_X`** — `Comment`, `Control` (Command arms 1–2)
and `ProtKwd`, `UnprotKwd`, `Function`, `Id`, `BuiltinVar` (Expr17's leaf alternatives) — and **every one resolves
to `DT_P` at hop 1**. No `DT_X → DT_X` chain occurs anywhere in beauty's failing run, so the new loop never
fires there. beauty's witnesses are byte-identical before and after the cure. (`v=0` slots in that trace are
beauty's `epsilon`, an intentionally UNSET variable = the null string: correct, not a defect.)

## 7. ⛔ INSTRUMENT HAZARD THAT COST THIS SEAT AN HOUR — AND A SECOND REAL DEFECT
**SCRIP's own front end rejects a statement carrying TRAILING WHITESPACE and no goto field** —
`snobol4:N: error: parse error: syntax error`, reported on the FOLLOWING line, no code generated. Assignment and
match statements alike; a goto field, a label-only line, and the `END` line are all unaffected. The oracle
accepts all of them. Witness: `corpus/probe/m1/m1_trailing_ws` (uncured, investigation only).
`beauty.sno` has **zero** trailing-whitespace lines, so **M1 is not blocked by it** — but an ablation harness
that pads a replacement line with spaces makes beauty **uncompilable**, and a verdict function that scores
"no `Parse Error` in the output" as OK then reports a **FALSE CURE**. Every `Expr0` conviction in §5.2 came from
exactly that. ⛔ **Any harness that grades beauty by its stdout MUST fail loudly on empty output and on
`no code generated`** — the hardened verdict function used for every number in this FINDING does.

## 8. NEXT — THE NAMED NEXT MEASUREMENT
The `[DEFER]` trace stops after `BuiltinVar` and **never resolves `EXPR$172` (`*Stmt`) nor ANY of the six
`Expr`-reading thunks** (`EXPR$75/131/146/148/162/167`), although the in-beauty tracer proves the `Stmt` arm IS
entered and `Stmt` DOES match to 5. Either those sites are resolved by a non-`DT_X` route (slot memoised to
`DT_P` after first use — `rt_spk_take` CONSUMES its park) or Expr17's alternation abandons its remaining arms
(`SpecialNm`, plain `*Id`, `String`, `Real`, `Integer`) after `BuiltinVar` fails — and `Integer` is precisely the
arm that must match the object `1`. **That is the next measurement: instrument each Expr17 arm and count which
are tried, on both engines.** It is stated as a lead, not a conclusion.
Also still open and untouched here: `rt_defer_take` carries the SAME single-resolve shape, but its `DT_X` arm is
dead because every caller pre-sets `dtx_used` — worth a rung of its own, with a witness, before it is cured.
