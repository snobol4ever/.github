# FINDING 2026-08-09g (Opus) — the SNOBOL4 bench SEGV tail is ONE stack leak: MATCH_BEGIN's stfh carve is 64B and zd_k reports it as 0

**Session shape:** measurement only. **ZERO source edits, zero codegen touched, no regen owed.**
Repos at open: SCRIP `b3133412`, corpus `095ac7d8`, .github `d932c2ca`. Build clean, 0 `error:`.

## 0. WATERMARK RE-PROVED AT HEAD (before any work)

SNOBOL4 benchmark corpus, m4, `test_bench_snobol4_modes.sh`: **OK=17 FAIL=0 CRASH=5 (of 22)** — reproduces
the 09f cursor exactly. The five: `eval_dynamic` (30s hang), `pattern_bt`, `pattern_bt_deep`, `roman`,
`string_pattern` (SEGV).

## 1. THE FOUR SEGVs ARE ONE DEFECT, AND IT IS NOT A PATTERN-ELEMENT BUG

Found MECHANICALLY (mode split → sibling diff → rlimit scaling → path swap), no compiler code read until
the mechanism was already named.

- **Mode split:** `pattern_bt` is m3-GREEN (matches ref) / m4-SEGV. The other three SEGV in BOTH modes.
- **The sibling pair is the whole discriminator:** `pattern_bt.sno` and `pattern_bt_deep.sno` are
  BYTE-IDENTICAL except the iteration count (500,000 vs 8,000,000). The crash is COUNT-DEPENDENT ⇒
  accumulation, not logic.
- **It is stack exhaustion, proved by rlimit scaling** (`setarch -R`, verified `ulimit -s` propagation):
  8 MB → max_ok ≈ 129,873 iterations; 32 MB → max_ok ≈ 522,353. **4x the stack buys 4.02x the iterations.**
  Linear. Per-iteration cost ≈ **64 bytes** at both stack sizes (64.59 / 64.24).

## 2. ⛔ INSTRUMENT CORRECTION — my first bisect harness was UNSOUND and its numbers are void

The first per-element bisect reported the IDENTICAL figure (129,395 / 64.8 B) for all six arms INCLUDING a
literal-only pattern that a prior run had shown clean at 3M. Cause: the harness wrapped EVERY pattern in
`PAT = …` + `S PAT`, so all six arms were measuring the plain-ref leak and none were measuring the element.
Caught by the POSITIVE-CONTROL LAW. Every number in §3 comes from the rebuilt harness whose control
(`inline SPAN`) reports NO LEAK to 8M. **Do not cite the 129,395-for-everything table; it is void.**

## 3. LEAK IS IN THE PLAIN-REF PATH — ALTERNATE AND SPAN ARE EXONERATED

Controlled, 3M iterations, `setarch -R`:

| construct | result |
|---|---|
| arithmetic only (positive control) | clean |
| **inline** literal / **inline** alternation / **inline** bare `SPAN` | **clean** |
| inline `SPAN('abcd') . W` (capture) | leaks |
| `PAT = 'bbb'` + `S PAT` (plain ref, ordinary STRING value) | leaks ≈65 B/iter |
| `PAT = SPAN('abcd')` + `S PAT` | leaks ≈65 B/iter |

Two facts worth keeping: (a) ALTERNATE and SPAN unwind CORRECTLY today — they are not W-3 customers;
(b) the plain-ref path leaks even when the variable holds a plain string, so the leak is on the REF path
itself, independent of the value's datatype.

## 4. ROOT CAUSE (mechanism named, killswitch-confirmed)

`IR_MATCH_VALUE` in the graph sets `flat_deep_arrival` (the PB-2 cursor already recorded this), which drives
`stfh()` in `bb_match_begin.cpp:26`, which fires **`x86_zclaim(64)`** at `bb_match_begin.cpp:48`.

Emitted-asm diff, clean vs leaking, same program shape:
- **unpinned (clean):** MATCH_BEGIN stores the PATCTX quartet into STATEMENT-OWNED POSITIVE slots
  `[rsp+48..72]`. Carves NOTHING. Nothing to release. Non-popping law intact.
- **stfh arm (leaking):** `sub rsp, 64` + stores to NEGATIVE homes `[rbp-40..-48]`. **There is no
  `add rsp, 64` anywhere in the emitted file.**

**A/B with the existing killswitch (decisive):** `SCRIP_OS_CAP=0` — which `bb_match_begin.cpp:26` documents
as restoring the bare `flat_stmt_frame` predicate — makes 3M iterations pass rc=0. Default: SEGV.

**WHY NOTHING RECLAIMS IT.** `HKQ`'s own comment (`bb_match_begin.cpp:27`) states the contract: the carve is
*"reclaimed by the bracket leave's `mov rsp,rbp` for free."* True for the `flat_stmt_frame` disjunct.
The OS-2·SLICE-1 widening added a SECOND disjunct (the GLUE-O legacy-deep-main class) which has **no bracket
leave** — the carve came along, the reclaim did not.

**AND THE ACCOUNTING CONFIRMS IT.** `zd_k` (emit.cpp:1991, "THE ONE AUTHORITY for K") lists
`IR_MATCH_BEGIN` in the **K=0** class, with the trailing note *"the quartet's own storage is the statement
claim … never a 16B value cell."* That was TRUE of the positive-slot spelling and is FALSE of the stfh arm.
So the template carves 64 and `op_zgpop` — which emit.cpp:3013 names the SOLE release authority, fed the
planner's K_total — releases 0. The statement under-frees by EXACTLY the carve.

This is the ZD-8 "SPELLED TWICE" disease, verbatim from its own comment: *"editing one alone made them
disagree by exactly K, a silent stack skew on every node of the admitted kind."* Measured skew: 64 B.
Predicted by the codebase; not caught because no gate watches rsp conservation across a loop.

## 5. FIX DIRECTION (NOT LANDED — scope + the one-authority hazard)

The law is not in dispute (emit.cpp:3013, Lon's words): a BB allocates its own K at α, and the WHOLE
accumulation is freed by ONE statement-terminal release, `op_zgpop`. The head's 64 must therefore be IN the
statement's K_total whenever the stfh arm fires AND no bracket leave exists.

⛔ **DO NOT** simply return 64 from `zd_k` for `IR_MATCH_BEGIN`: the carve is CONDITIONAL on `stfh()`, and
re-spelling that predicate inside emit.cpp is the very second-spelling sin that caused this bug. The correct
shape is ONE shared authority for "does the head carve, and does anything reclaim it" consulted by BOTH the
template (to carve) and the planner (to account). Note also the flat_stmt_frame disjunct must keep
contributing 0 — emit.cpp:841 already forces `op_zgpop = 0` there because the bracket reclaims.

**Gates the fix owes:** the loop-conservation witness below (rc=0 at 3M, both modes) · 141-probe BY SET both
modes · xc318 BY SET both modes · bench ≥ 17 with the four SEGVs cleared · `SCRIP_OS_CAP=0` byte-identical
· regen x3 (it is codegen).

**Prediction to falsify:** this one fix clears `pattern_bt`, `pattern_bt_deep`, `string_pattern` and should
move `roman` (whose inline captures leak by the same head, plus 100k recursive activations). Bench should go
**17 → 21 of 22**, leaving only `eval_dynamic`.

## 6. UNTOUCHED

`eval_dynamic` hangs 30s in BOTH modes — a SEPARATE defect, not this leak, not investigated. It is the sole
remaining bench crasher after the above.

## 7. WITNESS

`corpus/probe/bb/probes/zleak_matchbegin_stfh.sno` — plain-ref match in a 3M loop. rc=0 required;
SEGV at HEAD. Its value is that it fails on RSP CONSERVATION, which no existing gate watches: every probe
in the 141 suite is short enough that a 64 B/iteration leak never reaches the guard page.
