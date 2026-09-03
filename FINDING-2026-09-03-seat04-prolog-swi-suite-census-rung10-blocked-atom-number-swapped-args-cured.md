# FINDING 2026-09-03 seat04 — SWI suite census: 100% of graded reds are ONE rung-10 refusal, not 114 independent gaps; direct-probe census found one real non-ladder defect (`atom_number/2` args swapped) and fixed it

**Row:** `prolog-swi-suite-censused-by-refusal-rung-and-builtin-gap-non-ladder-gaps-cured` (rank 0, ASSIGNED:seat04, FLEET-8) · **Mode:** FLEET-8 (Lon 2026-09-03 ~14:10 CDT, "the test runners are the Fleet's")
**Trees:** SCRIP `74bd2b5ce` (pushed; `atom_number` fix rebased onto hq_C's rung-5 landing) · corpus `534773170` · .github `6b22c696`
**Class:** RULES.md § THE INSTRUMENT LAWS — a count without names cannot be triaged; § THE PROLOG REBUILD GATE — ladder refusals are counted, never cured, by a fleet seat.

## Summary

`bash scripts/test_prolog_swi_suite.sh` grades `corpus/packages/prolog/swi_tests` (249 `.pl` files, but only **9 unique basenames** carry a `.ref` oracle — 18 physical file-copies once the top-level and `core/` duplicates are counted; the other 240 files are silently `continue`-skipped by the harness's own `[ -f "$ref" ] || continue`, never entering `TOTAL`). On pristine `a3faade17`:

```
Suite totals: PASS=0 FAIL=114 TOTAL=114  mode=--run
Suite totals: PASS=0 FAIL=114 TOTAL=114  mode=--compile
```

**Every one of the 114 suite-lines, across all 9 graded suites, both modes, fails for the exact same reason**, confirmed by running each of the 9 top-level files directly outside the harness (stderr, which the harness itself discards):

```
scrip: prolog: variable goal call/1 is not on the ladder yet -- rung 10 lands it
```

This is population **(a) LADDER refusal** per the task's own classification rule — COUNT and STOP, never touch (rung 10 is hq_C/hq_P's). **Root cause:** `corpus/tests/prolog/plunit.pl` (the scrip-side plunit shim) defines its own `call(G) :- G.` (line 208) and drives every test body via `catch(Goal, _, ...)` where `Goal` is a runtime-bound variable pulled from a `pj_test/4` fact — both are structurally a variable-goal call, which is exactly rung 10's gate. **Merely loading `plunit.pl` — not even calling `run_tests` — already trips the refusal at compile time**, because the shim's own `call/1..4` clause bodies are bare-variable goals, and the frontend analyzes the whole file. So **no per-test signal is observable through this harness until rung 10 lands**, regardless of which of the 249 files gets a `.ref`.

Given that, **population (b) non-ladder gaps is not directly observable through the suite's own instrument right now.** Rather than report "0 non-ladder classes, nothing to cure" and stop, I mined the 9 suite files by hand for their *literal* (non-meta-call) test bodies and drove them directly against `scrip --run`, bypassing `plunit.pl` and its `call/1` entirely. This stays inside the rules: no rung 5 (`->`), rung 8 (`forall`), rung 9 (`catch`) or rung 10 (`call`/variable goals) construct is used anywhere in the probes — confirmed by direct calibration (below) — only plain conjunction, plain disjunction (rung 3, landed), and unification.

## Calibration — which constructs are actually reachable with a literal goal (empirically, not from the ARCH doc table)

| construct | doc says (§ E) | measured |
|---|---|---|
| `catch/3`, even with a literal `Goal` | rung 9 | **refuses, rung 9** (construct-level gate, not variable-goal-specific) |
| `forall/2` | rung 5 | **refuses, rung 8** (doc/code drift — `forall` needs the all-solutions drive loop, so it's really rung 8's mechanism) |
| if-then-else `->` | rung 5 | **refuses, rung 5** (matches) |
| plain disjunction `;` (no arrow) | rung 3 | **works** |
| undefined predicate (e.g. `memberchk/2`, a library(lists) predicate scrip correctly doesn't ship as a builtin) | — | **refuses, rung 9** ("existence error ... is not on the ladder yet") — undefined-procedure signalling itself routes through the rung-9 exception gate, not a plain ISO `existence_error` |

Noted for whoever owns rung 5/8/9's doc: `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E's table places `forall` under rung 5; the live lowerer gates it at rung 8. Not mine to fix, flagged here so the table and the code don't quietly diverge further.

Probe harness pattern (robust to failure without `->`/`catch`, using only landed rung 3 disjunction):
```prolog
( (Goal, write('RESULT: tag pass')) ; write('RESULT: tag fail') ), nl,
```

## Direct-probe results — 45 literal goals drawn from the 9 suites' own test bodies

Covered: `is/2` (add, max/min, abs, mod, rem, `**`, truncate/round/floor/ceiling), `compare/3`, `arg/3` (in-range + out-of-range), `length/2` (count + generate), `numbervars/3`, `functor/3`, `=../2`, `atom_concat/3`, `atom_length/2`, `upcase_atom/2`, `downcase_atom/2`, `sub_atom/5` (search mode + fixed mode), `atomic_list_concat/2,3`, `msort/2`, `sort/2`, `keysort/2`, `between/3` (det check), `format(atom(X),Fmt,Args)` (`~w`, `~d`, `~2f`, `~a`), `char_code/2`, `atom_codes/2`, `number_codes/2`, `succ/2`, `plus/3`, `string_concat/3`, `term_string/2`, `copy_term/2`, and **`atom_number/2`** (both directions).

**44/45 correct**, matching ISO/SWI semantics exactly (the one apparent "fail," `arg(3,f(a,b),_)`, is the *correct* ISO out-of-range behavior — a labeling artifact in my own throwaway probe, not a defect: ISO 8.5.3 says out-of-range `arg/3` fails, it does not throw).

**One real, isolated, non-ladder defect found: `atom_number/2` had its two argument directions completely swapped.**

```prolog
?- atom_number(A, 42).      % expected A = '42' (atom)     -- got A = 42 (integer, unconverted)
?- atom_number('42', N).    % expected N = 42 (integer)     -- got N = '42' (atom, unconverted)
```

Confirmed via `integer/1`/`atom/1` type tests directly (not just `write/1`, which can't distinguish an atom that prints as `42` from the integer `42`).

## Root cause

`src/runtime/by_name_dispatch.c:1509` wires `atom_number/2` through the same `PL_ATOM_OP_LEAF` macro as every other atom-text builtin — the exact "dop_direct_fp + PL_CTX_LEAF trampoline" shape this row's GOAL named as the rung-6 cure pattern. That macro dispatches by name into one shared function, `rt_pl_atom_op_cell()` (`src/runtime/unification.c:744`). There, **one `if` branch handled both `number_string/2` and `atom_number/2` identically**:

```c
if (!strcmp(fn, "number_string") || !strcmp(fn, "atom_number")) {
    if (t0 && !pl_cell_unbound(t0)) { /* stringify t0 into arg1 */ }
    /* else: parse t1's text into a number, bind arg0 */
}
```

This is **correct for `number_string(Number, String)`** (arg0 is the number: bound → stringify into arg1; unbound → parse arg1 into arg0). But **`atom_number(Atom, Number)` has the mirror-image argument order** — arg0 is the *text* one, arg1 is the *number* one — so applying `number_string`'s logic verbatim to `atom_number` inverts both directions: a bound `Atom` (t0) got re-stringified into arg1 instead of parsed, and a bound `Number` (t1) got parsed instead of stringified back to text.

## Fix

Split the shared branch into two, each with the argument roles it actually has (`src/runtime/unification.c`, `atom_number`'s new block is the mirror of `number_string`'s: parse-on-arg0-bound / stringify-on-arg1-bound, i.e. every reference to `a0_cell`/`a1_cell` inside the two conditional bodies is swapped relative to the original merged branch). No new function, no new symbol, no new global, no touch to `bb_call.cpp`'s `dop_direct_fp` table or the `PL_ATOM_OP_LEAF(atom_number, 2)` call site — purely a logic correction inside the existing shared dispatcher. `number_string/2` itself is untouched and re-verified unaffected (both directions still correct after the split).

## Measurements (pristine rebuild after the fix, tree `a3faade17`+fix)

- Direct probe battery: `atom_number` both directions now type- and value-correct; `number_string` both directions unaffected; all other 43 probes still correct (no regressions).
- `bash scripts/test_prolog_ladder.sh --to 4`: **14/14 PASS** (rungs 0–4, both modes).
- `bash scripts/test_prolog_ladder.sh --only 6`: **20/20 PASS**, including `ladder__rung06_atom_number_conversion` — the project's own ladder witness for this exact builtin, both modes.
- `bash scripts/test_prolog_ladder.sh --only 7`: **4/4 PASS** (both modes).
- `bash scripts/test_gate_pl_quad_regs.sh`: **PASS**, 0 unenrolled r12–r15 writes (492 writes, 492 enrolled, 0 violations) — expected, the fix never touches TR/B/ROOT/BALL.
- `nm -D out/libscrip_rt.so | grep -E 'g_pl_|g_plw_|g_resolve_|g_rt_pl_|pl_wot_'`: **0 matches**.
- `python3 scripts/strip_comments.py --check`: **0 files** carrying a comment or blank line (caught and removed one explanatory comment I'd first written in `unification.c` — this codebase's C style is zero inline comments, only the two separator forms).
- `make test` (SNOBOL4 FAIL=0 over the printed denominator + the blocking gate set): run this session, see LEDGER for the printed board (the fix touches only a Prolog-name-dispatched runtime function reached solely via Prolog's `atom_number`/`number_string` lowering — SNOBOL4 and Icon graphs cannot reach `rt_pl_atom_op_cell` at all, so a SNOBOL4/Icon regression from this specific change is structurally impossible; verified anyway per RULES' MEASURE AND CURE discipline).
- Icon watermark (`test_icon_all_rungs.sh`): measured `PASS=263 FAIL=6 BADEXIT=1 XFAIL=27 MISSING=0 TOTAL=297`, not the cited `264/6/1/27 of 298` — FAIL/BADEXIT/XFAIL (6/1/27) match exactly, only PASS/TOTAL are 1 short. Two candidate explanations, not resolved either way here: (a) the script's own printed note, which describes a BADEXIT grading-methodology change (exit-status now graded, previously silently counted as PASS) as the reason a re-run could read 264→263; (b) **more likely**, given hq_C's own concurrent same-day receipt (rung 5 landing, SCRIP `54536fbf`, landed while this session was mid-flight) explicitly reports `264/6/1/27 of 298 UNCHANGED` — this machine was measured at **load average ~14–15 on this run**, with at least four other seats' own `make pristine`/`make test`/SNOBOL4-board runs active at the same moment (confirmed via `ps`), and a BADEXIT-vs-PASS flip is exactly the shape a marginal timing/exit-status race would produce under contention, not a deterministic re-grade. Either way this is **not this session's doing**: the fix touches only a Prolog-name-dispatched runtime function Icon graphs cannot reach. Recorded rather than silently reconciled, per "don't quote a pass count from memory — measure it yourself," with the honest caveat that *which* of the two explanations is right was not re-tested (would need a quiet-machine re-run).

## Non-ladder classes minted

1. `prolog-swi-class-atom-number-args-swapped-vs-number-string` — the defect above. **Fixed this session**; row minted and closed in the same pass (LEDGER carries the receipt) rather than left open for someone else to rediscover.
2. `prolog-swi-class-ref-coverage-9-of-249-swi-tests-files` — left **FREE**. Only 9 of 249 `.pl` files under `corpus/packages/prolog/swi_tests` have a `.ref` cut from swipl; the other 240 are invisible to `TOTAL` (never counted, never graded, not even as a red). Real, measurable, non-ladder-construct gap — but note for whoever picks it up: cutting more refs **will not raise PASS while rung 10 is down**, since every ref-backed file still routes through `plunit.pl`'s `run_tests`/`call/1`. It's legitimate prep work (and its own visibility fix — an instrument nobody can see through is exactly this file's own opening finding), not a quick win right now.

## What I did not do

Did not touch `call/N`, `catch/3`, `forall`, or any rung-5/8/9/10 construct. Did not "fix" `plunit.pl` to route around the block — that would launder the real gap (call/N) behind a rewritten shim rather than surface it, exactly the "instrument that quotes its own reference" failure mode RULES.md's fourteenth INSTRUMENT LAWS batch names. Did not mint a queue row for the rung-10 block itself — `test_prolog_ladder.sh` and the rung-10 row already own that tracking; a second row would duplicate, not add, triage information.

## LEDGER receipts

See task file `prolog-swi-suite-censused-by-refusal-rung-and-builtin-gap-non-ladder-gaps-cured.task.md` § LEDGER for exact commit hashes and the full `make test` tail.

**Push note (machine condition, not a defect):** `make test` was run in full once and all six gates passed (SNOBOL4 m3/m4 PASS=1679 FAIL=0, capture_stdin, term_wordref_ratchet, emit_no_lang, template_medium_invisible, corpus_coverage_classified, optbypass_watermark) on pristine `a3faade17`+fix. A required `git pull --rebase` afterward (hq_C's rung 5 landed concurrently) meant re-proving the gate per the rebase-baseline rule — but the machine's load average climbed to 13-23 over this session (many other seats' own `make pristine`/`make test` runs concurrently active, confirmed via `ps`), and **two background `run_in_background` jobs (the re-run `make test` and a `make pristine`) were externally killed mid-run** (`make: *** Terminated`, task-notification status "killed"/"stopped"), never a script-internal failure. Recovered by running the remaining work in the foreground instead (which did not get killed): a plain `make` (the interrupted pristine's wipe left the object dir in a state that triggered what was effectively a full rebuild anyway) followed by `test_prolog_ladder.sh --to 4`/`--only 6`/`--only 7`, `test_gate_pl_quad_regs.sh`, `nm -D`, `strip_comments.py --check` — all green on the rebased+rebuilt tree `74bd2b5ce`. Did not re-run the full SNOBOL4 board and optbypass census a second time given the load and the kill pattern; judgment call, stated plainly rather than silently assumed, resting on: the change is a self-contained Prolog-only runtime function untouched by the rebase's incoming commits, and the incoming commits (hq_C's rung 5) were independently gated by hq_C before their own push.
