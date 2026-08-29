# FINDING: seat09's op_zres-gated ω-pop experiment fixes `pb34` cleanly, refutes the "shouldn't pop at all" half of item 7's question for `boolptr`/`boolidx` — and breaks SNOBOL4 (52 programs). Reverted, not shipped.

**seat12 · 2026-08-29 · row `pascal-restore-prezeta`** (continuing seat09's same-day `## NEXT`, itself
continuing my own `FINDING-2026-08-29-seat12-pascal-zd-omega-pop-ignores-value-diamond-continuation.md`)

**Ran the exact experiment seat09's `## NEXT` proposed and did not implement: does `boolptr.pas`'s failure
survive if `x86_asm.h`'s ω-exit pop (`op_wpop`) is simply skipped whenever `op_zres` is set?** One-line gate,
fully reverted after measurement. Answer is not the clean yes/no either side of item 7's framing expected —
it fixes one previously-unexplained defect, refutes nothing about the other two, and is unshippable as
written because it silently assumes `op_zres` distinguishes "value-diamond continuation" from "genuine
pattern-match backtrack", which is false.

## 0. The experiment, exactly

`x86_asm.h`, the shared ω-exit glue (line numbers re-confirmed live, moved again since my last citation):

```c
// line 2144, was:
if (site == X86H_JMP && port == X86P_OMEGA && _.op_wpop > 0) s += x86_add("rsp", (long)_.op_wpop);
// changed to:
if (site == X86H_JMP && port == X86P_OMEGA && _.op_wpop > 0 && !_.op_zres) s += x86_add("rsp", (long)_.op_wpop);
```

Rebuilt (`make`, RT_OPT=-O0 default), tested, then **reverted** (`git diff --stat` empty, confirmed via
`git status --short` before and after). No commit made at any point.

## 1. Read `bb_binop_relop_val.cpp` first — `op_zres` is not what item 7's phrasing implied

Before running anything I re-read the box (`src/templates/bb/bb_binop_relop_val.cpp`) rather than trust the
prior sessions' prose-only description. Two dispatch arms exist, both gated by `_.op_node_kind`
(`emit.cpp:1048` sets this to the real IR opcode before the `emit.cpp:1118` switch dispatches):

- `IR_BINOP_TEST` arm (lines 17-50, "IR_BINOP_TEST zd" comment): **genuinely calls `x86_omega(...)` twice**
  (once per int/slow-path). This is real, taken-at-runtime branch-and-bail — not dead code. Confirmed on
  `boolptr.pas` itself: statement 2 (`i<3`, i=7, false) takes exactly this omega exit at runtime.
- `IR_BINOP_RELOP_VAL` arm (lines 51-87, seat10's ROOT CAUSE #2 fix): never calls `x86_omega` at all — always
  γ-succeeds. `op_wpop` consumption is structurally unreachable for this arm regardless of any gate.

`boolptr`/`boolidx` dispatch through the **first** arm (`lower_pascal.c` never emits `IR_BINOP_RELOP_VAL`,
confirmed by seat09's own grep, `grep -c RELOP_VAL src/lower/lower_pascal.c` = 0 — reconfirmed here). So
seat09's framing ("never actually takes the ω exit at runtime, so zwpop's value may be dead code for it")
does not describe `boolptr`'s own mechanism — its omega exit is live, exercised code. `op_zres` here just
means "this node is inside a `zd_plan`-claimed run" (`emit.cpp:1030-1032`,
`g_zd_arm` ≈ `zd_on[i]`), not "this omega branch is unreachable at runtime." That distinction matters for
part 3 below.

## 2. Results, all four target names + the full previously-cured cluster + the standing regression detector

Isolated build, m3 (`--run`) and m4 (`--compile`) both checked and agree (no new m3/m4 divergence):

| program | baseline (unpatched) | with `!op_zres` gate | verdict |
|---|---|---|---|
| `boolptr` | `1,1` (wrong, ref `1,0`) | `1,1` (unchanged) | **not fixed** |
| `boolidx` | empty, rc=1 (crash) | empty, rc=1 (unchanged) | **not fixed** |
| `pb34` | `2,0` (wrong, ref `1,0`) | **`1,0` — matches ref** | **FIXED** |
| `deep5` | PAS-DISPLAY bomb (unrelated) | same bomb (unchanged) | unaffected, as expected |
| `boolassign`/`boolarg`/`boolchain`/`boolmix`/`boolnot` | all match ref (seat10's fix) | all still match ref, byte-for-byte | **no regression** |
| `ifwit` (`if 1=2 then writeln(7) else writeln(9)`, seat05's historical regression witness) | `9` (correct) | `9` (unchanged) | **no regression** |

`pb34` was previously believed unrelated to this mechanism ("smells like a numeric-coercion or unrelated
arithmetic bug, not a boolean-value-write bug" — seat10's `## NEXT`, and "not investigated... probably
unrelated" — seat09's own `FINDING`). **It is the same ω-exit-pop mechanism.** `pb34.pas` has no pointer or
array-lvalue relop shape at all — it's a `repeat...until (sy in statbegsys) or done`-style control structure
(SET membership test) with a `test : boolean` local — a third, structurally distinct trigger for the same
root cause, not a coincidence: this genuinely widens the known blast radius of the ω-exit-pop defect beyond
"relop into a pointer/array lvalue."

## 3. Then it broke SNOBOL4 — 52 programs, driver-heavy — before anything was considered for shipping

Standing constraint 1 ("SNOBOL4 stays green... outranks this row") is not optional and was checked before
any conclusion was drawn. `bash scripts/test_corpus_snobol4.sh`, full run (496s under concurrent FLEET-16
load — the first attempt timed out at 120s, matching my own and hq_B's prior sessions' note about corpus
runs under fleet contention; re-ran with a longer budget rather than trust a truncated result):

```
mode-3 (--run):     PASS=1275 FAIL=52
mode-4 (--compile): PASS=1275 FAIL=52 SKIP=0  (1327 total)
⛔ GATE FAIL: mode-4 FAIL=52
```

Baseline (this same tree, unpatched, per hq_B's same-day measurement) is 1327/1327 FAIL=0 both modes. All 52
new failures are pattern-matching-heavy: 14 named `*_driver` programs (`assign_driver`, `case_driver`,
`counter_driver`, `Gen_driver`, `match_driver`, `omega_driver`, `Qize_driver`, `ReadWrite_driver`,
`semantic_driver`, `ShiftReduce_driver`, `stack_driver`, `TDump_driver`, `trace_driver`, `XDump_driver`),
7 `demo_*` programs, and the `crosscheck`/`probe` suite files. This is exactly the failure shape you'd
expect if genuine pattern-match backtracking (a match alternative fails, needs the FULL unwind back to the
run's origin to try the next alternative) got silently truncated to "pop nothing" whenever the failing test
node happened to have `op_zres` set — which, per §1, is simply "inside a claimed run," a condition SNOBOL4
pattern matching hits constantly and legitimately.

**This directly answers item 7's disjunction, but not the way either side expected:** it is not cleanly
"wrong pop amount" (a single corrected nonzero formula would fix `boolptr`/`boolidx`/`pb34` uniformly) nor
cleanly "pop emitted for code that should never pop" (unconditionally skipping it is catastrophic
elsewhere). **`op_zres` alone cannot be the discriminator** — the same flag is true both for Pascal's
value-diamond continuations (which must not fully unwind) and for SNOBOL4's genuine backtrack omega-exits
(which must). Whatever correctly distinguishes these two cases has to be a narrower signal than `op_zres` —
candidates not yet tested: `op_node_kind` (is the omega-target itself part of a `zd_plan`-claimed run vs.
genuinely "no further alternative", i.e. exactly what `zd_omega_head`'s admission list was already trying
and failing to gate — see hq_B's finding) or a purely Pascal/value-diamond-local marker distinct from the
general "am I inside a run" flag.

## 4. Revert, verified — not assumed

`git diff --stat` empty before rebuild; rebuilt (`make`); re-ran the two highest-value spot checks rather
than trust the revert blindly:
- `boolptr`/`pb34` back to the exact documented baseline (`1,1` / `2,0`).
- `beauty_suite/assign_driver.sno` (one of the 52 new SNOBOL4 failures) diffed clean against its `.ref` in
  both m3 and m4 post-revert.

No full re-run of the 8-minute SNOBOL4 corpus gate after revert — the two-sided spot check (a Pascal
baseline number AND a specific broken-then-fixed SNOBOL4 driver, both m3+m4) is the same class of evidence
this row's own history treats as sufficient for "the tree is back to known-good," and the change was a
single line, mechanically reverted to the exact prior text. Flagging this choice rather than omitting it,
per this row's own STEP 1 discipline about not silently assuming.

## 5. Recommendation for the next actor

1. **`pb34` is now confirmed in-scope for this exact mechanism** — any future fix to the ω-exit pop
   (narrower than a blanket `op_zres` gate) should be graded against `pb34` alongside `boolptr`/`boolidx`,
   not treated as a separate unclustered defect.
2. **`op_zres` is refuted as a sufficient gate.** Don't re-try the blanket version. The next narrowing
   attempt needs a condition that is true for Pascal's `IR_BINOP_TEST`-as-value-diamond-arm but false for
   SNOBOL4's `IR_BINOP_TEST`/`IR_CMP_TEST`-as-pattern-match-alternative — `op_node_kind` combined with
   whether the *specific* omega target is itself claimed inside the same `zd_plan` run (i.e., resolving
   `zd_omega_head`'s per-op-filter gap directly, rather than routing around it at the pop site) is the most
   promising unexplored angle, since that's the one place the two cases are already known to differ
   structurally (a value-diamond's ω target IS a sibling materialize node in the same source-level
   statement; a pattern-match alternative's ω target is a genuinely different, unrelated continuation).
3. Standing item 7's original instrumentation suggestion (instrument the ω-exit pop site directly, on a
   witness, before the next formula change) remains the right methodology — this session used it, and it's
   why the SNOBOL4 break was caught before being proposed as a fix rather than after.

## Disposition

No code shipped — `git status` clean, confirmed both before writing this FINDING and by the spot-checks in
§4. `boolptr`/`boolidx`/`deep5` unchanged from every prior session's citation. `pb34` newly and correctly
understood to share this row's core mechanism (not fixed — the only tested fix for it broke SNOBOL4).
Standing constraint 1 (SNOBOL4 green) verified BROKEN by the experiment and verified RESTORED after revert
via targeted spot-check (§4), not a full re-gate. Pascal gates unchanged: still FAIL=4 both modes (same four
names). Claim released via `unclaim` — DONE-WHEN nowhere close, and this session's own standing discipline
(the same "don't guess at this shared ζ-accounting mechanism without a specific instrumented answer" that
seat05/08/09/10/15/hq_B have all cited) is exactly what caught the SNOBOL4 regression before it could ship.
