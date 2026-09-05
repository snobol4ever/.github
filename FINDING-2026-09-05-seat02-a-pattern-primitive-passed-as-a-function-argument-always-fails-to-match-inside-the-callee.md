# FINDING 2026-09-05 seat02 — a non-literal pattern primitive passed as a DEFINE'd function's argument always fails to match inside the callee

**Row:** `snobol4-aisnobol-ending-suffix-strip-wrong-output-four-words` (hq_B lane, aisnobol census).
**Status:** ROOT MECHANISM ISOLATED AND MINIMAL, SOURCE SITE NOT YET PINNED. Not cured. Routing to hq_C
(shared-engine, not aisnobol-specific — see § SCOPE).

## THE DEFECT, MINIMAL

```
	DEFINE('MATCH(L,PAT)')
	WRD = "LEAV"
	MATCH(1,LEN(1))            :S(OK)F(BAD)     <- SCRIP: BAD    ORACLE: OK
	:(END)
MATCH
	WRD PAT RPOS(L - 1)        :S(RETURN)F(FRETURN)
END
```

`LEN(1)` matches any single character; `WRD` is non-empty. This must always succeed — and does, on
`/home/resources/x64/bin/sbl -bf`. SCRIP fails it, unconditionally and deterministically (5 repeat runs,
identical). No concatenation, no alternation, no capture, no recursion — the smallest possible use of a
built-in pattern primitive as a user-DEFINE'd function's argument.

## SCOPE: THIS IS THE GENERAL CASE, NOT A ONE-OFF

Confirmed the same failure for every non-literal-primitive shape tried, both inline-at-call-site and
pre-assigned to a variable then passed by name:

```
MATCH(1,ANY("CGSVZ"))                 SCRIP=FAIL  ORACLE=SUCCEED
MATCH(1,ANY("LRSVZ"))                 SCRIP=FAIL  ORACLE=SUCCEED   (any charset content tried)
MATCH(3,VOWEL)      VOWEL=ANY(...)    SCRIP=FAIL  ORACLE=SUCCEED   (pre-built, passed by name)
MATCH(1,LEN(1))                       SCRIP=FAIL  ORACLE=SUCCEED
MATCH(2,ANY("SZ") ANY("SZ"))          SCRIP=FAIL  ORACLE=SUCCEED   (concatenation of 2 primitives)
MATCH(2,LEN(1) LEN(1))                SCRIP=FAIL  ORACLE=SUCCEED
MATCH(1,LIQUID | NOEND)               SCRIP=FAIL  ORACLE=SUCCEED   (alternation of 2 primitives)
```

Two shapes are NOT affected:

```
MATCH(2,"SS")                         SCRIP=SUCCEED  ORACLE=SUCCEED   (bare literal)
MATCH(2,"S" "S")                      SCRIP=SUCCEED  ORACLE=SUCCEED   (concatenation of LITERALS)
WRD ANY("SZ") ANY("SZ") RPOS(1)       SCRIP=SUCCEED  ORACLE=SUCCEED   (same pattern, INLINE, no function call)
```

**The defect is exactly: a pattern value built from a non-literal primitive (`ANY`, `LEN`, and by
inference `SPAN`/`BREAK`/`NOTANY`/`ARB`/`BAL`/etc.), when it crosses a user-DEFINE'd function's argument
boundary, does not match correctly inside the callee — regardless of arity, concatenation, alternation, or
whether it was built at the call site or pre-assigned to a variable.** Literal-string patterns as
arguments are unaffected (very likely because the optimizer/lowering folds them to a plain value early,
before whatever breaks at the boundary). The same primitives used directly inline, never crossing a call
boundary, are unaffected.

Every non-trivial `DEFINE`'d SNOBOL4 helper that takes a pattern-typed parameter and is called with
anything but a bare literal is a candidate victim of this class. This is not aisnobol-specific.

## A FALSE-GREEN-BY-COINCIDENCE THIS CAUSED, WORTH RECORDING FOR THE CLASS

The bug was originally missed as "single-primitive arguments work fine" because of a masked result.
`corpus/packages/snobol4/aisnobol/ENDING.sno`, lines 43-44:

```
        MATCH(2,"V")                              :F(WTRY)
        ~TRY() CUT(2) ADDON("FE")                 :S(WTRY)F(RETURN)
```
and, on the path this finding traced, lines 74-76:
```
WORDEND.6
        ~MATCH(3,VOWEL) ADDON("E")                :S(WTRY)
        MATCH(1,NOEND) ADDON("E")                 :(WTRY)
```

On input "LEAVING" (WRD reduces to "LEAV" after suffix-strip), a direct trace
(`MATCH(3,VOWEL) :S()F()` in isolation, not chained) shows:

```
SCRIP:  MATCH(3,VOWEL)      -> FAIL      (should SUCCEED: WRD[1]='E', a vowel)
ORACLE: MATCH(3,VOWEL)      -> SUCCEED
```

Because SCRIP's `MATCH(3,VOWEL)` wrongly fails, `~MATCH(3,VOWEL)` (SPITBOL unary NOT) wrongly *succeeds*,
taking the **first** branch and appending "E" immediately. The oracle's `MATCH(3,VOWEL)` correctly
succeeds, so `~MATCH(3,VOWEL)` correctly fails, falls through, and reaches `MATCH(1,NOEND) ADDON("E")` on
the **second** branch instead — which (per this same class of bug) *also* wrongly fails on the oracle's
real reasoning, but the point moot for that word since the first branch already fired in SCRIP.
Both engines print "LEAVE" for this one input, via **two different branches, one of them wrong on both
sides of the `~`**. A grader watching only this witness's final output would call it green. Confirmed by
a fully traced rewrite (each `MATCH` branching directly, no `ADDON` chained onto it) showing SCRIP
disagreeing with the oracle at *every* individual `MATCH` call on this path, not zero. **Agreement on a
single input's final output is not evidence the mechanism agrees** — the same instrument-law already
named in two of hq_C's 2026-09-05 findings, hitting a third, independently-found shape.

## WHY THIS IS A DIFFERENT DEFECT FROM TODAY'S TWO HQ_C FINDINGS

Read before starting on this: `FINDING-2026-09-05-hq_C-flat-alternation-leaves-32-live-bytes-the-zeta-model-never-counted.md`
and `FINDING-2026-09-05-hq_C-outer-capture-reads-its-own-home-because-capture-and-its-operand-share-a-zeta-depth.md`.
Both are real, landed cures for a **capture (`.`) over a group containing an alternation** — zeta-depth
miscounting for `IR_MATCH_ALTERNATE`. This finding's minimal repro has **no capture and no alternation**
(`MATCH(1,LEN(1))` — a single primitive, no `.`, no `|`) and was reproduced on a binary built from origin
*after* both of those fixes landed (SCRIP `df9fe6af`, pulled and rebuilt fresh this session). Distinct
mechanism, same neighborhood (pattern-value plumbing through the shared engine).

## SOURCE LEADS (Explore sub-agent, time-boxed ~9 min — NOT a confirmed root cause, a starting point)

- SNOBOL4 has **no dedicated "pattern value" IR node** for this. `IR_PATTERN_CAT/ALT/CAPTURE/DEFER`
  (`src/ir/IR.h:111-114`) are declared and named (`src/ir/scrip_ir.c:135-138`) but never constructed
  anywhere in the repo — dead opcodes. `IR_CONJUNCTION` is Icon-only (`src/lower/lower_icon.c:669`);
  `lower_snobol4.c` never builds it.
- Pattern concatenation-as-a-**value** (assignment, argument — as opposed to used inline in a match)
  is lowered through the **same generic path as string concatenation**: `lower_snobol4.c:117`
  (`TT_CAT -> BINOP_CONCAT`), landing at runtime in `c_str_concat_d` (`src/runtime/string_ops.c:18-20`),
  which detects a `DT_P`/`DT_X` operand and redirects to `pat_cat` (`src/runtime/pattern_match.c:216-219`):
  ```c
  DESCR_t pat_cat(DESCR_t left, DESCR_t right) {
      DESCR_t v; v.v = DT_P; v.slen = 0;
      v.p = (void *)dtp_new((void *)0, rcp_bin(TT_SEQ, rcp_of(left), rcp_of(right)));
      return v;
  }
  ```
  `rtx_init.c:38` has a static_assert explicitly documenting this routing as deliberate.
- **But the minimal repro has no concatenation at all** — `LEN(1)` alone as an argument already fails.
  So `pat_cat` cannot be the sole site; whatever `LEN(1)` alone returns as a plain value (its own DT_P
  descriptor, however constructed) already misbehaves once bound to a callee parameter.
- Callee side: `WRD PAT RPOS(L-1)` lowers `PAT` to `IR_MATCH_DEFER` (`lower_snobol4.c:1531`). Runtime
  dispatch is `bb_match_defer.cpp`'s "$V-slot"/"patv-fast" arm (lines ~80-113): reads a 16-byte slot,
  checks the `DT_P` tag, follows `.p` through `dtp_fn_of`. Argument slots are copied as a single 16-byte
  descriptor everywhere checked (`bb_call_value.cpp:46-50`; `emit.cpp:1567/1742/1815/1902`) — this is
  architecturally NOT a "one-node-only" ceiling (the recipe `rcp_bin` tree nests arbitrarily), so a naive
  "truncation" theory does not fit; something in the DEFER dispatch or in how a **parameter-bound** DT_P
  differs from a **local-variable** DT_P is the more likely shape, but this was NOT reached in the time
  budget.
- **Not yet traced, and the recommended next step:** `rcp_of()` / `dtp_new()` / the recipe→executable
  path near `pattern_match.c:216+`, and specifically whether the site that decides "build a `DT_P`
  descriptor" vs. "just copy the value" differs between an **assignment** RHS and a **call argument**
  expression for the exact same source primitive (`LEN(1)` alone, no concatenation).

## SEVERITY / WHY THIS MATTERS BEYOND aisnobol

`DEFINE`'d helper functions taking a pattern parameter and being called with anything richer than a bare
literal is an extremely ordinary SNOBOL4 idiom (this exact program is a 1972 Winograd/SHRDLU-era
example). Any master-suite or package-suite program using this idiom silently gets a wrong answer or a
false pass via the coincidence documented above — not a crash, not a parse error, nothing that shows up
as CRASH/HANG/REJECT on a board. **This is very likely under-counted in every SNOBOL4 suite's current
red/green numbers**, not just aisnobol's. Recommend hq_C (or whichever HQ takes this) also do a quick
sweep of gimpel/csnobol4_suite/snoflake for the same idiom once a fix lands, rather than trusting their
current PASS counts as unaffected.

## NOT DONE

- Exact source line(s) not pinned — see § SOURCE LEADS for where to pick up.
- Whether `DANCING`/`CURVED` (the other two wrong-output words on this same aisnobol row) trace through
  this identical mechanism was not hand-confirmed statement-by-statement (only `LEAVING` was fully
  traced) — given how pervasively `MATCH(...)` with non-literal arguments is used throughout `WORDEND`,
  and that this class is now confirmed unconditional or nearly so, treat it as the very likely
  explanation for all three non-crash words on that row, not a proven one.
- No fix attempted. This is shared pattern-engine machinery in an area today's two hq_C findings show is
  genuinely fraught (a plausible one-line fix there closed a cycle and stack-overflowed the compiler on
  its own error path); a seat attempting a blind fix here without hq_C's accumulated context on this
  subsystem risks exactly that trap. Handing off with the minimal repro and the leads above instead.

Repro files (scratch, not committed — this session's scratchpad, not durable):
`/tmp/claude-1000/-home-claude02/45621ffe-06ca-40eb-8dfb-8b6cda62af5f/scratchpad/repro_*.sno`
