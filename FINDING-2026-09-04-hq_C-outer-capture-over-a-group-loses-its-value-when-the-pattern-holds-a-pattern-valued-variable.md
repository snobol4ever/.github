# FINDING — an outer capture over a group loses its value when the pattern holds a pattern-valued VARIABLE

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-09-04 ~18:30 CDT · **Tree:** SCRIP `cfde5756f` · corpus `31d94b2cc` · RT_OPT `-O0`, incremental `make` · oracle `sbl -bf` (the patched 18:25 build)
**Row:** `snobol4-outer-capture-over-a-group-containing-a-pattern-valued-variable` (rank 1, hq_C), found while walking the gimpel suite under the SNOBOL4-only order.

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
