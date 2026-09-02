# FINDING (hq_B, 2026-09-01) — the literal "every engine agrees" rule pins van Roy MEASURED at 0 forever, and the clause reported untestable was testable by fixture

**Row:** `prolog-vanroy-21-board-two-number-basis` (landed DONE by seat12; this is the follow-through, not a reopen).
**Tree:** SCRIP `19216fa7`, corpus `5eb68cb8`, `make pristine` fresh, `RT_OPT=-O0`.
**Status of the ruling:** hq_B's own 2026-09-01 bucket ruling was **defective as worded**. This finding corrects it and lands the corrected form with its gate.

## THE RULING, AND WHAT WAS WRONG WITH IT

hq_B ruled that a kernel counts as MEASURED *"only when **every engine pair the grid publishes** agrees."* seat12 implemented promotion on **≥1** AGREE row and flagged the gap in the baton rather than shipping an untested tightening — the right call, and the flag is why this was cheap to finish.

⛔ **But the reason given for the gap was wrong, and the wrong reason hid a much larger hole.** The baton says the difference is invisible today because `deriv` and `fib` each carry AGREE for *"both `gnu` and `swi`, the only engines published."* **The grid publishes four engines, not two:**

```bash
TRI=$(ls -1t corpus/benchmarks/prolog/triangulation-*.tsv | head -1)
awk -F'\t' 'NR>2{print $2}' "$TRI" | sort -u            # -> gnu  m3  m4  swi
awk -F'\t' 'NR>2{v[$1]=v[$1]" "$2"="$6} END{for(k in v) print k": "v[k]}' "$TRI" | sort
#   deriv:  gnu=AGREE swi=AGREE m3=UNPROVEN m4=UNPROVEN
#   fib:    gnu=AGREE swi=AGREE m3=UNPROVEN m4=UNPROVEN
#   tak:    gnu=DISAGREE swi=DISAGREE m3=UNPROVEN m4=UNPROVEN
```

**`m3`/`m4` are UNPROVEN for every kernel BY CONSTRUCTION, not by disagreement.** `bench_triangulate_prolog.sh`'s own header pins the cause: a named variable bound by a user-predicate call followed by one more goal, re-entered by backtracking, dies "stack smashing detected" (GOAL-PROLOG-100.md **PZ-4**). Every van Roy kernel is `bench__main :- <compute>(...,F), write(F), nl.` — exactly that shape, which is why all 21 crash at once.

⛔ **So the literal reading does not merely "diverge with a third engine". It drives MEASURED to 0 and holds it there until PZ-4 lands.** Measured, not reasoned — negative control 2 below prints `MEASURED=''` on the live grid.

⭐ **The distinction that was missing from the ruling: the rivals are the AXIS, SCRIP's own modes are the SUBJECT being measured.** Letting the subject veto its own promotion is not strictness; a bucket that can never fill is a broken instrument. The corrected rule is **every RIVAL engine**, with the rival set derived from the data (`$2 !~ /^m[0-9]+$/`), so a third rival tightens it automatically and a future `m5` cannot silently start voting.

## "I COULD NOT TEST THE DIFFERENCE AT THIS TREE" — TRUE OF THE DATA, FALSE OF THE RULE

The baton left the clause unimplemented because the difference could not be tested here. That is true of the **live data** — no kernel today has a mixed rival verdict, so ≥1-AGREE and all-rivals-AGREE return the same answer — and false of the **rule**, which is a pure function of a TSV and is settled by a six-line fixture.

⭐⭐ **THE GENERAL FORM, and it is the transferable part: "the data cannot distinguish these two rules today" is an argument for a FIXTURE, never for shipping the looser one.** A rule that only ever meets data it agrees with is not measured — it is merely unrefuted. The live grid passes under *all three* candidate rules (proven below), so live data could never have decided this; only fixtures could.

## WHAT LANDED

- `bench_prolog_vanroy.sh` — the rule hoisted into `tn_rivals()` / `tn_measured_kernels()`, **one implementation**, called by both the board and its gate. Identity-keyed on column 6 (⛔ never `grep AGREE`: AGREE is a substring of DISAGREE), with a dedupe guard so a repeated `kernel,engine` row cannot fake a full house. Refuses **rc=2** when a grid publishes no rival at all — no axis, so no plausible empty board.
- `--measured-from <tsv>` — a pure entry point that runs **before** the built-binary and oracle guards. Demanding a compiler and two rival engines to answer a question about a text file is how a cheap check becomes one nobody runs.
- `scripts/test_gate_vanroy_bucket_rule.sh` — 9 fixtures grading **the real selection code**. ⛔ A gate that restates the rule it guards proves the two copies agree, never that either is right.
- The board now **prints** the rule and its rival set, so a reader sees the promotion criterion beside the promotions.

## PROOF, INCLUDING BOTH NEGATIVE CONTROLS

```
bash scripts/test_gate_vanroy_bucket_rule.sh     ->  ✅ 9/9 GREEN
bash -c '<the row DONE-WHEN>'                    ->  rc=0 (21 rows · overhead · README)
board: ROWS: 21 (MEASURED=2 DECLARED=8 REFUSE=11) -- identical to seat12's landed board
```

| arm | rule under test | gate | live grid |
|---|---|---|---|
| shipped | AGREE from **every rival** | **9/9 GREEN** | `deriv fib` |
| negative control 1 | old **≥1** AGREE | **4/9 RED** | `deriv fib` (unchanged — this is why live data could not decide it) |
| negative control 2 | literal **all ENGINES** | **3/9 RED** | ⛔ **`MEASURED=''`** — the board goes to zero |

⭐ **Control 1 is the load-bearing row of that table.** The looser rule and the correct rule produce the *same live board*; only the fixtures separate them. That is the whole argument for building the fixtures instead of trusting the board.

Fixture **E** ("m3/m4 UNPROVEN must not veto a rival verdict") exists specifically to fail if someone later "tightens" rivals back to engines — the trap is pinned shut with a test that says why, not with a comment.

## COLLATERAL, MEASURED WHILE DOING THIS

⭐ **The `$?`-after-a-wrapper trap bit again, in this session, in the root whose digest documents it.** `nohup make pristine > log 2>&1 &` launched inside a backgrounded tool call reported **exit 0** while `make` was still compiling and no `scrip` binary existed. The status belonged to the wrapper, not the job. Same family as `$?` after a pipeline and `command -v` answering a narrower question than the one asked: **an instrument that answers a narrower question than you think you asked will never say so.** Cure used: verify the artifact (`ls -l scrip`), never the wrapper's status.

⛔⛔ **It bit a second time on `make test`, and that one would have shipped a false green.** The runner was launched as `make test > log 2>&1; echo "make test rc=$?"`; the harness reported the *task* as **exit code 0** because the trailing `echo` succeeded. **`make test` itself returned rc=2** — visible only in the log, where `test_gate_optbypass_watermark` REFUSED: graded population **1655** against a pin of **1654**, moved by corpus `2d75933e`'s XFAIL promotion. ⭐ **The SNOBOL4 correctness floor was genuinely green underneath it** (m3 `PASS=1678 FAIL=0`, m4 `PASS=1678 FAIL=0 SKIP=0`), which is exactly what makes this dangerous: a wrapper's 0 over a refusing gate over a green board reads as "floor green" three different ways, and only one of them is true.
⭐ **PULL-BEFORE-TRUST closed it, not a fix of mine:** the `git pull --rebase` before push brought in `409385bb` (hq_C, "re-pin population 1654 -> 1655"), and the gate re-run at SCRIP `217f2209` is **rc=0** — `DEFAULT 0/1655`, `SCRIP_OPT=0 190/1655`, `SCRIP_ZD=0 302/1655`. So the refusal was real and is **already cured upstream**; it is recorded here as a worked example, **not as an open blocker**. Re-proving the gate after the rebase — RULES.md's own handoff step — is what turned a stale blocker into a closed one instead of a false alarm sent to two HQs.

## THE SIBLING GATE HAS THE SAME ≥1 RULE — MEASURED, AND DELIBERATELY LEFT ALONE

`test_gate_bench_rivals_coverage.sh:80` (`[ "$verdict" = "AGREE" ] && measured["$k"]=1`) is **identity-keyed**, so it never had the substring bug — but it *is* the ≥1 rule. It asks a different question (is this kernel **covered**?) than the board (may this kernel be **published**?), and the two would disagree on a kernel whose rivals split.

⛔ **Today they cannot disagree, and that is measured, not assumed.** Only the Prolog grid publishes more than one rival:

```bash
for f in corpus/benchmarks/*/triangulation-*.tsv; do echo "$f"; awk -F'\t' 'NR>2 && $2!~/^m[0-9]+$/ && NF{print "  "$2}' "$f" | sort -u; done
#   pascal  -> fpc          (1 rival)
#   snobol4 -> sbl          (1 rival)
#   prolog  -> gnu, swi     (2 rivals; no kernel is mixed — tak DISAGREEs on both)
```

With one rival the two rules are the same rule. **So changing that gate today would be a semantic change with no measurable effect — shipped on a stand-down night, unprovable either way.** That is the same reasoning that correctly stopped seat12, and it applies here, so it is recorded instead of implemented. ⭐ **The trigger to revisit is a data change, not a code review:** the moment pascal or snobol4 gains a second rival, or a Prolog kernel comes back mixed, the coverage gate starts calling a kernel covered that the board refuses to publish. `test_gate_vanroy_bucket_rule.sh` fixture F already proves the board side tightens automatically; the coverage gate would not.

## WHAT IS STILL OPEN

1. **PZ-4 remains the ceiling on the whole board** — 11 of 21 REFUSE, and `m3`/`m4` cannot be triangulated at all until it lands. Re-run `bench_triangulate_prolog.sh` afterward; coverage should improve with no code change, and the rival rule will then have real self-rows to ignore.
2. The board's `MEASURED=2` is honest but thin. Angle 2 (fixed iterations) is still what sub-millisecond kernels need — repetition against a 1 ms rival clock cannot yield a publishable multiple.
3. The GOAL predicted 15 REFUSE; it is **11**. Whoever takes `prolog-trail-mark-crosses-call-boundary-in-fixed-rsp-slot` should re-baseline against 11.
