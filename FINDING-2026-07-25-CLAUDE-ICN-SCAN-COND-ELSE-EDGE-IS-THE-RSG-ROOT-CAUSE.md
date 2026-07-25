# FINDING 2026-07-25 (s164) — ICN: A FAILING SCAN AS AN `if` CONDITION NEVER REACHES `else`; THIS IS `rsg`'s ROOT CAUSE

**Status: ROOT CAUSE PINNED TO A 2-LINE REPRO. NOT FIXED.** One candidate fix was tried and
**falsified** (details below, so the next session does not re-try it).

## THE DEFECT, IN TWO LINES

```icon
procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end
procedure main(); write(f("noun") | "*** PROC FAILED ***"); end
```

`iconx` → `ELSE`. SCRIP (both modes) → **the whole procedure FAILS**; `else` is never taken.

## IT IS SCAN-SPECIFIC — THE DISCRIMINATING TABLE

Same `if C then return "THEN" else return "ELSE"`, only `C` varies, subject `"noun"`:

| Condition `C` | iconx | SCRIP |
|---|---|---|
| `s ? (="'")` — **scanning expression** | ELSE | ❌ **procedure fails** |
| `s == "zzz"` — comparison | ELSE | ✅ ELSE |
| `="q"` — bare match, no scan env | ELSE | ✅ ELSE |

So the failure edge of a **scan environment** (`e1 ? e2`, `TT_SCAN`) is misrouted when the scan
fails; every other failing condition takes `else` correctly. Subject kind is NOT the trigger —
parameter, local, and literal subjects all fail identically.

## WHY THIS IS THE `rsg` ROOT CAUSE (the whole chain, measured)

`rsg.icn`'s `defnon` is exactly the broken shape:

```icon
procedure defnon(sym);
   if sym ? { ="'" & chars := cset(tab(-1)) & ="'" }
   then return charset(chars)
   else return nonterm(sym);
end
```

For an ordinary nonterminal (`"noun"`) the scan fails, so `defnon` must return `nonterm(sym)`.
In SCRIP `defnon` **fails instead**. Then, measured at each level:

- `syms(alt)` puts `tab(many(nonbrack)) | defnon(2(="<",tab(upto('>')),move(1)))`. For
  `"<noun> runs."` arm A fails (first char is `<`) and arm B is `defnon(...)` → fails →
  `put` fails → `while` ends immediately → **`syms` returns `[]`**.
- Instrumented dump at the `gener` lookup: oracle `ALT s[1] nsym=2`
  (`nonterm(noun)` + `" runs."`), **SCRIP `ALT s[1] nsym=0`**.
- `gener` therefore expands `<s>` to nothing: oracle walks `s, noun, s, noun…`,
  SCRIP walks `s, s, s`.
- Net program behaviour: **1,000 blank lines** vs the oracle's 5,000 lines / 1,604 distinct
  sentences. This is the short-circuit that made `rsg` look 2.83–3.40× "faster".

`defs` itself is NOT at fault — verified by instrumenting `define`: SCRIP stores the identical
keys and value shapes as the oracle (`KEY=[noun] list(2)`, `KEY=[s] list(1)`, `nkeys=10`).

## FALSIFIED HYPOTHESES — DO NOT RE-TRY

Each was tested standalone against `iconx` and came back **IDENTICAL**, i.e. NOT the bug:

| Suspected | Verdict |
|---|---|
| `(!plist)(line)` — generated procedure value invoked, backtracking on failure | ✅ works |
| Table assign with scanning subscript AND scanning RHS (`defs[(="<",tab(find(">::=")))] := (move(4),…)`) | ✅ works, correct evaluation order |
| Integer-as-selector `2(a,b,c)` (index 2, not just `write := 1`'s index 1) | ✅ works |
| `?list` random element · `\x` non-null · `x ||| y` list concat · `x ||| []` | ✅ all work |
| `static` + `initial` local (`static nonbrack; initial nonbrack := ~'<'`) | ✅ works |
| `while put(L, A | B)` inside a scan, arm A failing | ✅ works |
| Subject kind (param vs local vs literal) | ✅ not the trigger |

**The 2026-07-25 goal-file hypothesis that `rsg` was a procedure-value-list dispatch defect is
FALSIFIED** — `(!plist)(line)` is fine. That guess is retracted.

## CANDIDATE FIX TRIED AND FALSIFIED

`src/lower/lower_icon.c`, `case TT_SCAN`, the subject-β rewiring:

```c
IR_t * subj_beta = cx->beta;
if (subj_beta && subj_beta != ω) { γ_to(leave_fail, subj_beta); ω_to(leave_fail, subj_beta); }
```

This has **no `ir_is_generator_kind` guard**, while the BODY's β assignment three lines below
does (`cx->beta = (bv && ir_is_generator_kind(bv->op)) ? leave_succ : …`). The asymmetry looked
like the bug: a non-generator subject should leave `leave_fail`'s γ/ω on ω.

Adding `&& sr && ir_is_generator_kind(sr->op)` **did not change behaviour at all** — the repro
still fails identically. So either `subj_beta` is already ω on this path (the rewiring never
fires) and the misrouting happens elsewhere, or `leave_fail` is not the node whose edge is
consumed by the enclosing `if`. **The edit was REVERTED; the tree is clean.** Next session should
start by DUMPING THE IR for the 2-line repro and reading where `IR_SCAN`'s ω actually lands,
rather than reasoning from the lowering source — that reasoning has now been wrong once.

## LIKELY BLAST RADIUS

The goal file already carries `FZ-E scan root (recogn/scan/scan1/scan2)` with the note
*"emitter wires the SCAN_MATCH fail-edge to arm-B beta (resume, mid-flight) not alpha (fresh
start)"* — the same family. This finding supplies that cluster with a 2-line deterministic
repro, which the cluster previously lacked. Worth re-testing after a fix: `rung36_jcon_scan`,
`scan1`, `scan2`, `recogn`, and the `rsg` benchmark.

## METHOD NOTE — AN INSTRUMENTATION TRAP WORTH REMEMBERING

A first instrumentation pass rewrote `define`'s `return line ? expr` as
`r := line ? expr; write(…); return r`. In Icon a failing statement does **not** propagate out
of a procedure body — so `define` began returning `&null` (succeeding) on every line, `(!plist)`
stopped at `define`, and `generate` was never reached. **Both engines then produced zero
sentences, which looks exactly like the bug under investigation.** In a goal-directed language,
probe code must preserve success/failure semantics (`return \r`, not `return r`), or it
manufactures the very symptom being chased.

## ADDENDUM (same session, after the IR dump) — IT IS NOT MERELY A MISROUTED FAIL EDGE

The IR for the repro is structurally CORRECT, which rules out the obvious reading:

```
1   γ=2@ ω=2@  DISJUNCTION  [3,15@,16,15@,.,.]     <- the if: arm0 entry=3 (scan path), arm1 entry=16 (else)
3   γ=4  ω=1   VAR "s"
4   γ=5  ω=1   SCAN_ENTER [3]
6   γ=7  ω=13@ SCAN_MATCH [5]
7   γ=8@ ω=13@ SCAN_TAB [6]
13@ γ=14 ω=14  GOTO                                 <- fail trampoline (alpha-forced, correct)
14  γ=1  ω=1   SCAN [4]                             <- leave_fail: restore env, then -> node 1 (DISJUNCTION beta)
16  γ=17@ ω=2@ LIT_INTEGER 2                        <- the else arm IS present and wired
```

The else arm exists, and `leave_fail` does route back to the DISJUNCTION. So the defect is in
EXECUTION of that wiring, not its construction.

**The decisive behavioural evidence — two DIFFERENT wrong behaviours from one failing scan:**

| Program | iconx | SCRIP |
|---|---|---|
| `return (s ? (="'")) \| "ALT-ELSE"` | `ALT-ELSE` | **returns null/empty** — NOT a failure, and NOT the alternative's value |
| `if s ? (="'") then return "THEN" else return "ELSE"` | `ELSE` | **procedure fails** |
| `every 1 to 1 do { if s ? (="'") then return "THEN" }; return "AFTER"` | `AFTER` | (masked by the failure above) |

The alternation case is the informative one: the arm does not fail cleanly — it **delivers an
empty value slot**. That is the signature of DISJUNCTION **arm VALUE-SLOT** delivery for a
scan-containing arm (the `op_parts` / CV10 channel in `emit.cpp`, and the `na_s`/`na_f`
success/fail glue labels), not of a mis-stamped α/β edge in LOWER.

**THEREFORE: START IN THE EMITTER, NOT IN `lower_icon.c`.** Specifically the nary-DISJUNCTION
glue that reads an arm's value slot and its fail-glue label when that arm's tail is an `IR_SCAN`
(`leave_fail`, which is itself a GENERATOR-kind node with a value slot it never fills on the
fail path). The LOWER-side guard hypothesis is already falsified above; do not spend a second
budget there.
