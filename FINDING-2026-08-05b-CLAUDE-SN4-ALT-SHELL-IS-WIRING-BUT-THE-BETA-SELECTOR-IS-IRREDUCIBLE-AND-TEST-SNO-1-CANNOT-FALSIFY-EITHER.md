# FINDING 2026-08-05b — SN4 ALT: THREE OF FOUR PORTS ARE WIRING, THE β PORT IS NOT, AND `test_sno_1.c` IS VACUOUS ON THE QUESTION

**Seat:** Claude Opus, GOAL-SNOBOL4-BB. **Question put by Lon:** *"the ALT Byrd boxes ... keep track of a
counter and just move straight through. I speculate that it does not need to be a BB box of its own, but that
just like IR_SEQUENCE it can be accomplished with only wiring. Let's verify this is true or false."*

**ANSWER: HALF TRUE, AND THE HALVES SPLIT CLEANLY ALONG THE PORT BOUNDARY.**
The ALT **shell** (α, γ, ω + the value copy + its identity as a third party) **IS** wiring — deleted, oracle-exact,
**−19 instructions** on the `test_sno_2/3` shape. The **β port is NOT** wiring — falsified by exhaustion over the
closed set of static targets. **Do not attempt a SEQUENCE-style eradication of `bb_pat_alt`; it will break, and
this doc names the exact port that breaks.**

---

## ⛔ HEADLINE 1 — `test_sno_1.c`'s ALT PROBE IS VACUOUS. ITS β SELECTOR FIRES **ZERO** TIMES.

MEASURED, not inferred (instrumented counters on `alt_β`, `BIRD_β`, `BLUE_β`, `LEN1_β`):

```
[SEL fired=0  arm1=0 arm2=0 arm3=0 | BIRD_b=0 BLUE_b=0 LEN1_b=0]
```

`SUBJ ? (POS(0) ARBNO('Bird' | 'Blue' | LEN(1)) $ OUTPUT RPOS(0)) $ OUTPUT` on `'BlueGoldBirdFish'` succeeds on
the greedy extension path. Backtracking goes to `ARBNO_β` (extend), **never** to `alt_β` (retract into the
alternation). The dispatcher and all three arm β ports are DEAD CODE on this probe.

**CONSEQUENCE — THE FALSE GREEN.** I deleted the counter outright and wired `A_β` to each of the three static
candidates. **All three produced byte-identical oracle output.** Had I stopped there I would have reported
"the counter is wiring, proved by deletion" — and been wrong. ⚠ **A session testing counter-elimination on
`test_sno_1.c` gets a GREEN that means nothing.** Same failure mode as the ICN-RTX "vacuous by symmetry"
family; the instrument was the only thing that caught it.

## ⭐ HEADLINE 2 — THE SHELL IS WIRING (PROVED BY DELETION, ORACLE-EXACT)

Arms wire DIRECTLY to the consumer's ports; the box vanishes as a third party, exactly as SEQUENCE did:

```
    A_α → M1_α           (folded into the consumer's β edge)
    Mi_γ → A_γ           (A_γ IS the consumer's consumption site -- no trampoline, no copy)
    Mi_ω → M(i+1)_α      (static chain)
    Mn_ω → A_ω           (A_ω IS the consumer's retract site)
```

| shape | insns (-O0) | oracle |
|---|---|---|
| ALT box + per-arm value copy (**`test_sno_2.c`/`test_sno_3.c` shape**) | 339 | exact |
| ALT box, no value copy (`test_sno_1.c` shape) | 322 | exact |
| **SHELL DELETED, counter kept** | **320** | **exact** |

**−19 instructions (5.6%)** against the value-copy shape; **−2** against the already-minimal `test_sno_1.c`
shape. The bulk of the win is the **per-arm value copy** (`alt10 = V11;` in `test_sno_3.c:288`), which the
DERIVE-DON'T-ACCUMULATE ruling already makes unnecessary — the consumer derives `str(Σ+Δ0, Δ−Δ0)` from its own
entry cursor and never needs the arm's value hoisted into a box-owned member.

Re-proved independently on `test_sno_1.c` itself: **341 → 339, oracle-exact.**

## ⛔ HEADLINE 3 — THE β PORT IS **NOT** WIRING. FALSIFIED BY EXHAUSTION.
## ⛔ CORRECTION (same session, after Lon's challenge "if it requires an integer, then it requires a box"):
## **LON IS RIGHT. THE PORTS ARE ELIMINABLE; THE BOX — BY THIS CODEBASE'S OWN DEFINITION — IS NOT.**

**RETRACTED:** this doc originally implied the selector rides free in "the consumer's already-allocated cell."
**MEASURED FALSE for `test_sno_1.c`:** `typedef struct _1 { int alt_i; } _1_t;` has EXACTLY ONE member.
ARBNO's own state (`ARBNO_i`, `ARBNO_Δ0`) is plain scalars OUTSIDE the array. **`_1[64]` exists SOLELY for the
alternation** — and this doc's own `d2` variants already proved the biconditional without noticing it: deleting
`alt_i` deleted the entire cell array. `alt_i` ⟺ the cell, one to one. (`test_sno_4.c` IS the shared-cell case —
`_iter { int alt_i; int cap_Δ0; cap_t cap; }`, where the capture needs its two members at depth regardless — so
the claim was generalized from the file where it holds to the file where it does not.)

**THE OPERATIVE DEFINITION OF "BOX" IN THIS TREE IS STORAGE, NOT PORTS.** `zls_grant_locals` dispatches on IR
KIND to answer "does this get locals?"; claim-depth arithmetic prices the partition. That machinery is the box
test. **Anything requiring a claim at UNBOUNDED DEPTH is a box in the only sense the emitter implements.**
ALT requires exactly that. Precise statement of what was proved:

> **ALT's DISPATCH SURFACE is eliminable (α/γ/ω → wiring, measured −19 insns). ALT's STORAGE is not.
> Ports go; the claim stays. That does not make it "not a box" — it makes it a box with three fewer ports.**

⚠ **AND THE ORIGINAL RECOMMENDATION BELOW WAS A TRAP — DO NOT FOLLOW IT NAIVELY.** "Collapse the shell, inline
the selector on the consumer's retract edge" removes `IR_MATCH_ALT` as a dispatch kind **while the datum still
needs a depth-indexed claim — so `zls_grant_locals` would have NO CASE TO FIRE ON and NOTHING WOULD CLAIM IT.**
That is **verbatim the SE-6 failure mode of the live cursor**: the SEQ container was deleted and the elements'
claim arithmetic went on pricing a partition that no longer existed (the 5 remaining SIGSEGVs are a nested-ARBNO
`saved_rsp` slot aliasing a claim). The C embodiments CANNOT expose this — `_1[64]` is a literal array
declaration and C allocates it regardless of what calls itself a box. **Any ALT rung must keep a claim
authority: either retain the kind for `zls_grant_locals` purposes, or transfer the 4 bytes to a consumer that
independently claims at the same depth — and PROVE the consumer's claim exists (it does in `test_sno_4.c`, it
does NOT in `test_sno_1.c`).**

---

## (original headline 3, evidence unchanged and still valid)

The static target set for `A_β` is **CLOSED**: each arm's β, or `A_ω`. Two probes, deliberately built so the
live arm at the retract differs (**D0 → arm 2**, **D5 → arm 1**, both confirmed by instrumentation, both
oracle-validated against `sbl -b` BEFORE use):

| `A_β` static wiring | D0 (needs arm 2) | D5 (needs arm 1) |
|---|---|---|
| → arm 1 (`ABC_β`) | **FAIL** | PASS |
| → arm 2 (`AB_β`) | PASS | **FAIL** |
| → arm 3 (`A1_β`) | **FAIL** | **FAIL** |
| → `A_ω` (non-resumable) | **FAIL** | **FAIL** |
| **→ dynamic selector (counter)** | **PASS** | **PASS** |

A perfect diagonal: **each static choice passes exactly the probe whose live arm it happens to name.** No
element of the closed set passes both. The counter is irreducible.

**MECHANISM (why it cannot be otherwise).** ARBNO's depth is unbounded and **each live iteration independently
bound a different alternative** — that is why the cell array is `_1[64]` and not a scalar. Static wiring is ONE
copy of the code; it cannot carry N independent "which arm" facts. The selector datum is **DATA, not CONTROL**.
Re-encoding it as a label pointer (`goto *resume`) is the same datum at 8 bytes instead of 4 — a re-spelling,
not an elimination.

## ⭐ THE ASYMMETRY WITH SEQUENCE, IN ONE LINE

> **Sequence's β port = last member's β — STATIC. Alternation's β port = the LIVE arm's β — DYNAMIC.**

SEQUENCE collapsed completely because member order is fixed at compile time: `Mi_γ → M(i+1)_α` is knowable
statically **because there is no choice**. Alternation's whole purpose is that there IS a choice, and SPITBOL
semantics require resuming *after the bound alternative* — manual §Pattern Matching p.58: *"If none of the
alternatives in a column match, the needle is pulled back to the previous column, and other alternatives are
tried there"*, and p.59 on backtracking: SPITBOL *"backtracks, unbinding patterns until another alternative can
be tried."* **Which alternative is bound is exactly the fact the counter holds.**

**3 of 4 ports collapse to wiring. The 4th is irreducible per-iteration state.**

## CONSEQUENCE FOR THE LIVE CURSOR (SEQ-ERAD)

The current cursor is chasing nested-ARBNO stack corruption created by SE-6's deletion of the SEQ container.
**This finding predicts that an analogous `bb_pat_alt` ERADICATION CANNOT WORK** — not as a geometry bug to be
fixed, but structurally: SEQUENCE genuinely had no per-instance datum, ALT has one, and the ALT datum needs a
claim at unbounded depth. **The two are not the same shape and must not be given the same rung.**

⚠ **AND THE SAFE-LOOKING MIDDLE PATH IS THE TRAP** (see the CORRECTION above): collapsing ALT's ports while
deleting its IR kind leaves the claim unowned — `zls_grant_locals` dispatches on kind, so nothing fires — which
is the SE-6 defect reproduced exactly. **The port collapse (−19 insns) is real and worth having, but it is only
safe if a claim authority survives the collapse. Name that authority in the rung before writing any code, and
prove it claims at the same depth.**

## ARTIFACTS

`corpus/probe/bb/test_sno_alt_d0.c` (retract resumes arm 2, Success) · `test_sno_alt_d5.c` (retract resumes
arm 1, Success) + `.ref` files + `p4.sno`/`p5.sno` sources. **These are the probes `test_sno_1.c` could not be.**
Every measurement `-O0` (RT_OPT=`-O0`, O2-DIRECTED-ONLY rule honored — no `-O1`/`-O2` used anywhere).

## LIMITATION — DO NOT OVERSELL

Falsification is exhaustive over **static wiring of the β port**, which is the claim actually under test. It does
NOT rule out eliminating the counter by a *different mechanism* that is not wiring — e.g. duplicating the
consumer's continuation per arm (trades the datum for code growth that is exponential under nesting), or
re-deriving the bound arm from the cursor delta (works only when all alternatives have distinct lengths — false
for `'Bird' | 'Blue'`, which are both 4). Neither is wiring, and neither was proposed. Both are open.
