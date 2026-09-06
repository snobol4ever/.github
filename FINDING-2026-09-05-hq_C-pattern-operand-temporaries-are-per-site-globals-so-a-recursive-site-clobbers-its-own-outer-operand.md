# FINDING — a pattern-construction operand temporary is a PER-SITE GLOBAL, so re-entering the site clobbers the outer activation's operand

**Seat:** hq_C · **Date:** 2026-09-05 (FLEET-12) · **Tree:** SCRIP `b6c17b331`, corpus `7ffe8b899`, `RT_OPT=-O0` read from the Makefile, incremental `make`, no stale-binary refusal · **Oracle:** `/home/resources/x64/bin/sbl -bf` (⛔ `-bf`, s189) · **Modes:** m3 and m4, identically.

## The claim

`V = A | B` — any pattern-valued assignment whose RHS is a pattern expression — stages its operands in **global variables named after the SOURCE SITE**, not after the activation. `src/lower/lower_snobol4.c:2212` mints `PAT$n$V0`, `PAT$n$V1`, … ; `:2546` registers them with `sno_reg_var` and points the static pattern graph's `MATCH_DEFER` nodes at those same names; `SNO$MKPAT` then reads them to snapshot the operands into the pattern value.

The emitted γ chain is:

```
store $V0 <- operand0
evaluate operand1          <-- MAY CALL USER CODE
store $V1 <- operand1
MKPAT reads $V0 and $V1
```

If operand1's call re-enters **the same source site**, directly or indirectly, the inner execution overwrites `$V0`, and the outer `MKPAT` snapshots **the inner activation's operand** into the outer pattern. The window between the first store and the read is open to arbitrary user code.

## Witness (19 lines, zero single quotes, both modes)

```
	DEFINE("F(N)")				:(FE)
F	EQ(N,0)					:S(FZ)
	F = "a" N
	F = F | INNER(N)			:S(RETURN)F(RETURN)
FZ	F = "z"					:(RETURN)
FE	DEFINE("INNER(N)")			:(IE)
INNER	EQ(N,1)					:S(IFAIL)
	INNER = F(N - 1)			:(RETURN)
IFAIL						:(FRETURN)
IE
	&ANCHOR = 1
	X = F(2)
	"a2" X					:S(S1)F(S2)
S1	OUTPUT = "PASS a2"			:(T)
S2	OUTPUT = "FAIL a2"
T	"a1" X					:S(S3)F(S4)
S3	OUTPUT = "PASS a1"			:(END)
S4	OUTPUT = "FAIL a1"
END
```

`sbl -bf` prints `PASS a2` / `PASS a1`. SCRIP prints `FAIL a2` / `PASS a1` in **both** modes: the outer pattern is `a1 | a1`, its left operand `a2` having been overwritten by the inner activation.

## The ablations, each with an oracle control arm

| ablation | result | what it rules out |
|---|---|---|
| hoist the call out of the alternation into its own statement | **cures** | — |
| hoist only the left operand into a temp | does not cure | the left operand's *read* is not the defect |
| write the two recursion levels as **two distinct source sites** | **cures** | ⭐ this is the one that proves the storage is per-SITE, not per-ACTIVATION |
| same recursion shape through `IR_BINOP` (concatenation, addition) | correct | not a general operand-lifetime defect |
| same recursion shape through a two-argument **user function call** | correct | not general call-argument staging |
| a global written by the callee, read as the left operand | correct | evaluation order is left-to-right and is **not** the defect |

## What it costs, and why nobody read it as this

`corpus/packages/snobol4/gimpel` `HYPHENAT_driver` and `LINE_driver` both die `ERROR 246 -- stack overflow`. That is the symptom of an infinite pattern recursion, and the recursion is caused by this defect four steps upstream:

1. `HYPHENAT.sno` builds `HYPH_SUFF = OR(UPLO(BALREV(...)))`. Oracle: `HYPH_SUFF` matches `noit`. SCRIP: it matches the **null string**.
2. `BALREV`/`UPLO` are byte-identical to the oracle; the divergence is entirely inside `OR()`.
3. `OR()`'s **control flow is byte-identical to the oracle** — an instrumented copy traced the same call sequence and the same returns on both. Only the VALUE differs. `OR(",a,b")` is `a | b` in the oracle and `"" | b` in SCRIP (anchored it matches every subject and consumes nothing: `subject a -> matched [] size=0`).
4. `OR` accumulates `OR = OR | OR_EXTRACT()` and `OR_EXTRACT` recursively calls `OR()` — re-entering that very site.
5. So `HYPH_PAT = HYPH_SUFF @K (*GT(K,MIN) | FENCE *HYPH_PAT)` recurses on a left factor that consumes nothing → `ERROR 246`.

⭐ **The control arm that matters:** a genuinely null-recursive pattern overflows in the ORACLE too. The overflow is *correct behaviour for the pattern SCRIP actually built*. The defect is that it built the wrong pattern — so every instrument pointed at the crash was pointed one causal step too late.

## The lessons

⛔⭐ **A per-SITE temporary is invisible to every test that runs the site once.** This storage has been correct in every non-recursive program since it was written, and it is correct for two *sequential* executions of the same site (measured: `MK("x","y")` then `MK("q","r")` leaves the first pattern intact). It fails only when the site is on its own call graph. A fixture set built by calling a constructor twice cannot stage that; one built by calling it recursively is the only witness that can.

⛔⭐ **THE FINDING AGAINST MY OWN METHOD, and it is the reusable one: I built the right witness and asked it the wrong question, and recorded "not reproduced" for a full ablation round.** An earlier arm of this hunt (`r4`) had the *exact* failing shape — recursive re-entry of the in-flight alternation statement — and I graded it by asking only "does the pattern match null?" and "does it reject an unrelated subject?". Both answers were the same whether or not the clobber happened, because the clobbered value `a1` is itself a perfectly ordinary non-null pattern. I concluded the shape did not reproduce and went looking elsewhere. It reproduced the whole time; re-running the identical program and asking *"does it still match `a2`?"* — **the value my theory said must differ** — turned it red immediately. A witness proves nothing that its assertions do not ask, and a null-check is the weakest assertion available against a defect that substitutes one real value for another.

⚠ **Not measured, named rather than assumed:** the `$A%d` twin on that same `:2212` line (the non-`snapg` arm) has the identical shape and this witness never exercised it. Establish whether it shares the hazard before cutting a cure that only covers `$V`.

## Routed

Minted **`snobol4-pattern-operand-temporaries-are-per-site-globals-clobbered-by-reentry`** (rank 1, owner **hq_P** — `lower_snobol4.c` is SNOBOL4-only lowering, no shared node, no hq_U co-sign). Its DONE-WHEN carries the witness inline (deliberately **not** added to `corpus/tests/snobol4`, because a red program there moves the master denominator and breaks every seat's FAIL=0 floor); proven rc=1 as written in the baton today, and its refusal arm proven rc=2 with `S4E_HOME` unset. Row `snobol4-gimpel-suite-126-to-100-percent-by-class` handed to hq_P with this measurement in its `## NEXT` (ceo health check 19:06: gimpel-by-class is hq_P's lane under THE 12-SEAT CUT).
