# FINDING — an outer capture over a group loses its value when the pattern holds a pattern-valued VARIABLE

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-09-04 ~18:30 CDT · **Tree:** SCRIP `cfde5756f` · corpus `31d94b2cc` · RT_OPT `-O0`, incremental `make` · oracle `sbl -bf` (the patched 18:25 build)
**Row:** `snobol4-outer-capture-over-a-group-containing-a-pattern-valued-variable` (rank 1, hq_C), found while walking the gimpel suite under the SNOBOL4-only order.

## ⛔⛔ CORRECTION, 2026-09-04 ~19:05 — THIS FILE'S TITLE AND ORIGINAL CLAIM NAME THE WRONG INGREDIENT

**The trigger is NOT a pattern-valued variable.** It is **an ALTERNATION as the second element of a concatenation inside a captured group**. The variable in my original witness merely *held* an alternation (`SEIZE = BREAK(",") | REM`) — correlated, never causal. Everything below about the MECHANISM stands and was measured directly; only the attribution of the trigger changes. The title is left as landed so the correction is findable from what people already cite.

**The factorial that settled it**, all at top level, all against `sbl -bf`:

| pattern | SCRIP |
|---|---|
| `(LEN(1) . IC REM) . COMMON` | ✅ correct |
| `POS(0) "," (LEN(1) . IC REM) . COMMON` | ✅ correct |
| `(LEN(1) . IC (BREAK\|REM)) . COMMON` | ⛔ loud refusal |
| `POS(0) "," (LEN(1) . IC (BREAK\|REM)) . COMMON` | ⛔ loud refusal |
| `(LEN(1) (BREAK\|REM)) . COMMON` | ⛔ **silent `COMMON=[]`** |
| `(ANY("a") (BREAK\|REM)) . COMMON` | ⛔ silent |
| `("a" (BREAK\|REM)) . COMMON` | ⛔ silent |
| `(ARB (BREAK\|REM)) . COMMON` | ⛔ loud refusal |
| `(BAL . IC (BREAK\|REM)) . COMMON` | ✅ correct |
| `((BREAK\|REM)) . COMMON` | ✅ correct |
| `(LEN(1) . IC) . COMMON` | ✅ correct |
| `(LEN(1) (BREAK REM)) . COMMON` | ✅ agrees (`nomatch`) |

The prefix is irrelevant. An alternation **alone** is fine. A concatenation **without** an alternation is fine. Any ordinary element — literal, `ANY`, `LEN`, `ARB` — followed by an alternation breaks it. ⭐ **`BAL` is the one exception that does NOT trigger it**, which is a lead rather than a curiosity. The inner capture only decides the SYMPTOM: silent empty without it, loud `rt_dcap_pump` refusal with it.

## ⛔⭐ HOW THE WRONG TRIGGER SURVIVED NINE ABLATIONS — THE PART WORTH REUSING

My original witness carried **four** unusual ingredients at once: two pattern-valued variables, `BAL`, an inner capture, and an alternation. I ablated the ones I *suspected* — `BAL`, the function activation, local-vs-global, the nested capture — and when removing each left the failure standing, I credited the one ingredient I had never removed.

**Every one of those ablations was individually sound. The SET was not exhaustive.** And an ablation set that never removes the true cause will confidently name whatever is left standing, with as many confirmations as you care to run. The eight negative results I was proud of are all still true; they simply could not reach the answer.

⭐ **The fix is not more single ablations, it is the factorial** — vary the ingredients against each other rather than removing them one at a time from a fixed witness. Nine one-at-a-time removals produced a confident wrong answer; twelve crossed cells produced the right one, and cost less.

⚠ Note this is the SECOND correction on this defect in one session — the first overturned a base-mismatch theory. The mechanism survived both, because it was **measured** (`c->subj == Σ`, end offset correct, start garbage by exactly `len`) rather than inferred. **A measured mechanism outlives a wrong trigger.** That is the whole argument for spending the extra command on the `fprintf`.

## THE CLAIM

`P . VAR` over a group returns the WRONG value whenever the matched pattern contains a pattern held in a **variable**. The inner capture is always right; only the outer one is lost. Depending on where the variable sits it is either **silent** (the target becomes the null string, rc=0) or **loud** (`rt_dcap_pump: CORRUPT CAPTURE ENTRY refused`).

**Minimal witness — 7 lines, no function, no `BAL`, no includes:**

```
	SEIZE = BREAK(",") | REM
	ANC = POS(0) ","
	LIST = ",a"
	LIST  ANC (LEN(1) . IC  SEIZE) . COMMON		:F(NO)
	OUTPUT = "COMMON=[" COMMON "]"			:(END)
NO	OUTPUT = "nomatch"
END
```

| | oracle `sbl -bf` | SCRIP |
|---|---|---|
| above (both variables) | `COMMON=[a]` | `rt_dcap_pump: CORRUPT CAPTURE ENTRY refused — … exceeds subject length 2 (target 'COMMON', frame depth 1). Deferred re-entry invalidated the outer frame; capture skipped rather than reading out of bounds.` |
| `SEIZE` only, variable INSIDE the captured group | `COMMON=[a]` | **`COMMON=[]` — silent, rc=0** |
| `ANC` only, variable BEFORE the group | `COMMON=[a]` | the loud refusal |

⭐ **The silent arm is the dangerous one.** A capture that yields the null string is a wrong answer with no diagnostic, and the loud arm proves the engine can detect the same corruption — so the two arms are the same defect with and without its own alarm.

## WHAT IS EXONERATED — MEASURED, DO NOT RE-CHASE

- **`BAL` is innocent.** The identical shape written with `BAL` and INLINE patterns is byte-correct in both implementations. `BAL` was my first suspect and it is wrong.
- **A function activation is NOT required.** The witness above is top level. ⚠ I said "inside a function" earlier in the same session, on a smaller set of arms; this measurement corrects it. Recording the correction because the wrong version was already in a message.
- **Declared-local vs global target is irrelevant** — both fail identically, and a capture into a declared local on its own is correct.
- **A nested capture inside a captured group is fine on its own**: `LIST (LEN(1) . IC REM) . COMMON` is correct in both.

**The one ingredient that flips it is a pattern held in a VARIABLE and concatenated into the matched pattern.** The implicated site names itself in the refusal: `rt_dcap_pump`, the deferred-capture pump, and its own wording — *"Deferred re-entry invalidated the outer frame"* — describes the mechanism.

## WHY IT BURNS TWO WHOLE PROGRAMS

Both remaining `ERROR 246 -- stack overflow` reds in the gimpel suite, `HYPHENAT_driver` and `LINE_driver` (LINE includes HYPHENAT), are this one defect. `OR.sno` builds `SEIZE` and `ANC` as pattern variables and relies on the outer capture to set `COMMON`:

```
OR_EXTRACT
	LIST    ANC  (BAL . IC  SEIZE) . COMMON		:S(ORX_0)
	...
ORX_5	OR_EXTRACT  =  P  COMMON  OR(SUBLIST)		:(RETURN)
```

`COMMON` comes back empty, so the next statement consumes the wrong text, `SUBLIST` is built as **the same string `OR` was called with**, and `OR`/`OR_EXTRACT` recurse forever. Traced live on the minimal input `OR(",a")`: `LIST` reads `,a` at *every* recursion level, and at `ORX_5` the oracle has `COMMON=[a] SUBLIST=[,]` where SCRIP has `COMMON=[] SUBLIST=[,a]`.

⭐ **The stack overflow is the symptom of a wrong answer, not a depth problem.** Anyone who reads `ERROR 246` and starts sizing stacks is chasing the wrong thing — this is a matcher defect that happens to end in recursion.

## ⭐⭐ MECHANISM MEASURED — AND IT REFUTED THE THEORY I WAS ABOUT TO WRITE DOWN AS FACT

The refusal prints two enormous numbers, and reading them was worth more than guessing at them. `len=1314904096`, `saved_delta=2980063202`. Taken as **signed**, `saved_delta = -1314904094`, and

```
signed_delta + len  ==  2  ==  the subject length, exactly
```

So the entry's **END offset is CORRECT** and its **START is garbage by exactly `len`**. The span arithmetic is internally consistent; only the origin is wrong. That immediately suggests the deferred re-entry is resolving offsets against a different subject base — and **that theory is wrong.** A one-line diagnostic settled it:

```
[DCAP-DIAG] c->subj=0x1718f490 Sigma=0x1718f490 Sigmalen=2
            delta_as_signed=-1314904094 len=1314904096 signed_delta_plus_len=2 subj_minus_Sigma=0
```

**`c->subj == Σ`. The bases AGREE.** It is not a base mismatch. Since the end offset is right and start = end − len, both bad numbers derive from **one** bad input: the capture's **banked START cursor**. The runtime's own message says which event does it — *"Deferred re-entry invalidated the outer frame"*.

⭐ **THE CORRECTED CLAIM: a deferred re-entry clobbers the OUTER capture's saved start cursor.** The end is taken live at commit and stays correct, so the corruption is invisible in any test whose capture ends where it begins, and the inner capture is unaffected because it banks and commits without a re-entry in between.

**NEXT ACTOR, exact site.** `src/templates/bb/bb_match_capture.cpp` banks the start cursor in phase 0 and reads it back at commit:

```
16  #define havehome()  (_.op_zres || _.op_cap_anchor || _.op_off >= 0)
30  #define writehome() (_.op_zres ? ZRESD(0)   : FR(_.op_off))
31  #define readhome()  (_.op_zres ? ZOPD(1, 0) : FR(_.op_off))
```

⚠ The frame-relative arm writes and reads the **same** expression, `FR(_.op_off)`. The ζ arm does **not**: it writes `ZRESD(0)` and reads `ZOPD(1, 0)`. Whether those two name the same cell across a deferred re-entry is the first thing to measure — not to assume, because I have now been wrong once on this defect by reasoning one step past the evidence.

⛔ **AND THAT IS THE REUSABLE PART OF THIS SECTION.** The base-mismatch story explained every number I had, was mechanically plausible, and would have sent the next actor into the subject-rebinding code for nothing. What killed it was a single `fprintf` of the two pointers I was *assuming* differed. **When a theory explains the evidence, the cheap next move is not to write it up — it is to print the one value the theory says must differ.**

## HOW IT WAS NARROWED, AND THE ONE THING THAT MADE IT CHEAP

Nine ablations, each one killing a hypothesis rather than confirming the headline: recursive pattern via deferred self-reference (works), capture into the subject variable itself (works), the `ORX_0` recursion-breaker (agrees), the match-and-replace that shrinks the global (agrees), a callee writing a caller's local by assignment (agrees), the same by pattern replacement (agrees), capture into a declared local (works), capture into a global (works), nested capture with inline patterns (works).

⭐ **Every one of those is a NEGATIVE result, and they are what makes the row actionable.** The positive finding alone would have sent the next actor into `BAL`, into dynamic scoping, or into stack sizing — three plausible, expensive, wrong roads that are now closed with receipts.

## STATUS

Not cured; mechanism narrowed to the banked start cursor (see above). Row minted with the DONE-WHEN above, **proven RED as written in the baton** (extracted from the file and run, rc=1). The criterion refuses rc=2 if the oracle itself drifts off `COMMON=[a]`, so a later green means the compiler moved and not the oracle. SHARED-NODE: the pattern engine is reached by SNOBOL4 and Snocone, so a cure grades both plus the SNOBOL4 master over its printed denominator.

## ⭐⭐ EXTENSION, 2026-09-04 ~19:15 CDT (seat04) — THE TRIGGER SHAPE ABOVE IS SUFFICIENT, NOT NECESSARY; A BARE ALTERNATION FAILS TOO, NO LOOP REQUIRED

Working row `snobol4-gimpel-diff-self-match-own-name-cluster` (ORDER/PERMUTAT/RPERMUTE/CARDPAK/ONEWAY, the "self-match into the function's own name-variable" cluster hq_C flagged in-chat not to trust without re-applying the factorial). **That hypothesis is now falsified directly**, and the real cause is this same defect family, reached by a route this file's factorial table does not cover.

**The falsification, all against `sbl -bf`:** the exact ORDER algorithm (`S LEN(1).T=` pop a char, `&ALPHABET BREAK(T) REM.HIGHS` compute the "≥T" charset, `ACC (BREAK(HIGHS)|REM).S1=S1 T` insert-at-sorted-position, loop) reproduces `aannaannanab` for `ORDER('banana')` even with the accumulator renamed to a plain `ACC` at TOP LEVEL — no `DEFINE`, no function activation, no variable sharing a name with anything. Self-reference-to-a-function's-own-name is not an ingredient.

**The new minimal witness needs no loop at all.** Two capture statements (`SD LEN(1).TD=`, then `&ALPHABET BREAK(TD) REM.HIGHSD`) followed by the self-referential alternation-capture (`ACCD (BREAK(HIGHSD)|REM).S1D=S1D TD`), written out **twice in straight-line code, no GOTO**, on input `"cba"`: first pass correct (`ACCD=[c]`), second pass gives `ACCD=[bac]` where the oracle gives `[bc]` — a spurious `a` injected between the correct insertion and the correctly-preserved suffix.

**This is a BARE alternation** — `(BREAK(HIGHS)|REM) . S1`, no ordinary element preceding it inside the group — which row 23 of the factorial table above (`((BREAK|REM)) . COMMON`) marked ✅ correct. It still corrupts. So "an ordinary element followed by an alternation inside a captured group" is A trigger, not THE trigger; row 23's own test apparently never forced backtrack-with-a-surviving-suffix on a repeat pass, which is why it read clean.

**Narrowed to exactly two prerequisites, both measured by substitution, not assumed:**
- A single-shot execution of the identical alternation-capture-replace (any combination of zero-length match, nonzero suffix, real long HIGHS string) is always correct. It takes a **second-or-later execution of the same statement**.
- Feeding that second execution with **literal** (non-captured) HIGHS/T values that change between rounds is still correct. It takes HIGHS/T to themselves be **captured** from a preceding statement.
- One preceding capture alone (either just the `T` capture with HIGHS literal, or just the `HIGHS` capture with T literal) is still correct. It takes **both** — i.e. exactly ORDER's own shape: two capture statements in a row feeding a self-referential alternation-capture, on that alternation-capture's second-or-later execution.

**`--dump-zeta` rules out static slot aliasing.** Both textual occurrences of the alternation-capture statement get fully independent, non-overlapping persistent (ζ-STANDING/RBP) frame slots for every field, including `alt.entry/resume/next-entry`, `break.cnt/cur`, `match.cursor save`, and `capture.stack`. So this is not a compile-time layout collision — it is runtime state that outlives a single match. The zeta dump's own comments name the suspects: `head.dcap_mark` ("REG-6 PEND-PROMOTE: α saves live-r12 pend top = this match's MARK; ω/RELEASE truncate r12 from it") and `head.capgen_save` (a monotonic per-match generation id — the same comment block records a prior incident: "the inner match stamp invalidated the outer SAVE bracket, pop no-opd, top returned 0"). Both are the `rt_dcap_pump` apparatus this file's own loud-refusal arm already names.

**Working theory, not yet verified by instrumentation the way the base-mismatch theory above was killed by one `fprintf`:** the r12 dcap-pend-island and/or the capture-generation counter is not being fully unwound/reset by two ordinary (non-alternation) capture statements executing in between, so by the time a self-referential alternation-capture's DEFERRED RE-ENTRY fires on its next pass, it reads back state left by an unrelated, already-finished match rather than its own.

## ⛔⛔ RETRACTION, 2026-09-04 ~19:35 CDT (seat04) — THE ABOVE THEORY IS WRONG. MEASURED, NOT ASSUMED: THIS IS A DIFFERENT DEFECT.

Same trap this file's author already named twice: a plausible theory that explains the evidence is not yet a measurement. Before committing to "same code path," I traced the actual dcap-pump entry for the failing capture with gdb: **the S1D capture entry itself is exactly correct** (`saved_delta=0, len=0, subj="c"` — precisely right for a zero-length match on ACCD's true value) at the pump call that produces the wrong final answer. The corruption is not in the capture value at all — it is in the REPLACE step's reassembly of prefix+replacement+suffix, and it is fixed by `SCRIP_CAP_SLICE=0` (a *different* toggle, in `rt_dcap_pump`'s zero-copy slice branch, `src/runtime/pattern_match.c:708-711`, not the ZRESD/ZOPD banked-cursor path above). Cross-checked directly: `SCRIP_CAP_SLICE=0` does **not** fix this file's own witness (still refuses identically) — so these are two distinct defects sharing only a refusal path, not one root cause. Full writeup, corrected witness chain, and the (also-ruled-out) SXT in-place-extend tangent are now in their own row: `snobol4-deferred-capture-slice-goes-stale-across-subject-reassignment`. Apologies for the noise on this file in the meantime — recorded rather than deleted, per this file's own convention, so the dead end is findable.

Not cured (this defect). `snobol4-gimpel-diff-self-match-own-name-cluster` re-parked `BLOCKED-ON` the new row, not this one.
