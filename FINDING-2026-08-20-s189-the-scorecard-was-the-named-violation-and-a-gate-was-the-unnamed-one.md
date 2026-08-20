# FINDING s189 (seat5, `/home/claude5`, Claude Opus 5) — queue row `scorecard-drop-lon`

## ⛔ THE HEADLINE: THE BRIEF NAMED ONE VIOLATION AND THERE WERE TWO. THE SECOND IS A GATE, AND IT COMPILED ALL 99 OFF-LIMITS PROGRAMS ON EVERY RUN.

The row was scoped to `scorecard_snobol4.sh`, which executes the `lon` suite through `run_one` in both
engines and both modes — so "run the SNOBOL4 scorecard" was itself an instance of Lon's ruling being
broken. That is real and it is fixed. But the same ABSOLUTE RULE carries a clause the brief did not
quote, and the clause is what found the second one:

> ⛔ Tooling that walks the corpus **by wildcard** must EXCLUDE this directory **by construction**
> rather than by skipping it at run time (row `scorecard-drop-lon`), so the violation cannot be
> reintroduced by a flag. — `RULES.md`, ABSOLUTE RULE 1

**A wildcard walker does not have to name the tree to reach it.** `scripts/test_gate_argnote_sweep.sh`
roots at `CORPUS=${CORPUS:-$S4E/corpus}` — the corpus **root** — does `find "$CORPUS" -name '*.sno'`,
and runs **`$SCRIP --compile`** on every file it gets back. Measured: **1766 files before the prune,
1667 after, difference exactly 99** — the whole off-limits tree, compiled on every run of a
`test_gate_*` script, i.e. inside the set of things that must never regress. Against a rule whose
words are *"NEVER RUN, NEVER COMPILE … in any mode, under any harness"* and whose second reason is
that those files may carry live Personal Access Tokens.

**The searchable name found the scorecard; only the *shape* found the gate.** `grep -rn 'programs/lon'
scripts/` returns exactly one file, and it is the one the brief already knew about. Nothing in the
gate's text contains the string `lon`. Any future audit of this rule that greps for the directory name
will report all-clear while the gate keeps compiling the tree.

## ⛔ AND THE RULE'S OWN PROPAGATION CLAIM IS FALSIFIED — IT NAMED A PATH THAT DOES NOT EXIST AND MISSED THE ONE THAT DID

`RULES.md` states: *"`scripts/scorecard_snobol4.sh` executes the `lon` suite … **and every board/bench
script that calls it inherits that**."* Measured across the whole SCRIP tree: **the scorecard has ZERO
callers.** The only other hit is `scorecard_icon.sh:2`, a comment reading *"Sibling of
scorecard_snobol4.sh"*. So the exposure was never a call graph — it was two independent direct
executions, one named and one not. Recorded so the next seat does not go hunting an inheritance chain
that isn't there, and so the rule's text can be corrected rather than trusted.

## WHAT LANDED — SCORECARD (`SCRIP/scripts/scorecard_snobol4.sh`)

**1. The `lon` row is DELETED from the suite table, which IS the weight table.** `cmd_report` builds
`W[]` and `ORD[]` from the same `$SUITES` string the runner filters, so one deletion removes the suite
from running *and* from scoring. Deleted, per HQ's ruling on form, rather than skipped at run time —
a run-time skip is re-openable by anyone passing `--suites lon`; a deleted row is not.

**2. An unknown `--suites` name is REFUSED (rc=2), not ignored.** This is the door the deletion alone
leaves open, and it is worse than it looks. The suite filter is `grep -q ",$name,"` against the table,
so a name absent from the table matches nothing — `--suites lon` would have run zero programs,
**truncated `results.tsv`**, and then reported a META over an empty denominator that looks like a
board. That is precisely the failure the file's own s182 warning describes, reached by a *typo* rather
than by two runs sharing one `--out`. So the refusal covers every unknown name, not just `lon`:

```
$ scorecard_snobol4.sh run --suites lon
⛔ REFUSED --suites lon: Lon ruled corpus/programs/lon is not to be run, and the suite was DELETED
   from this scorecard at s189. There is no flag that runs it.                              rc=2
$ scorecard_snobol4.sh run --suites crosschek
⛔ REFUSED --suites crosschek: no such suite. Known: beauty_self beauty_suite demos benchmarks
   bb_probes patterns crosscheck feature_test probes_misc csnobol4_suite gimpel misc         rc=2
$ scorecard_snobol4.sh run --suites patterns,lon     → same lon refusal, rc=2
```
⭐ **The refusal fires BEFORE the out dir is created or truncated** — verified: none of the three
refused invocations left a directory behind. A refused call cannot destroy a previous board's results.

**3. A structural guard on the table itself, fired at source time for EVERY subcommand.** One `case`
over `$SUITES`: if the table names `programs/lon` at all, the script exits 2. **Negative-tested by
injection, two ways** — (a) re-adding the `lon` row: refused; (b) leaving no `lon` row at all and
merely appending `programs/lon/sno` to *`gimpel`'s* lib column: **also refused**. (b) is the one that
matters, because that is what `lon-include-root` was in the business of doing, and no amount of
row-deletion would have caught it.

**4. `report` now says when it is ignoring measured rows.** The awk silently drops rows for any suite
not in the table — correct scoring (a pre-s189 `results.tsv` still holds `lon` rows and they must not
enter META) but silence is how a plausible wrong number ships. It now prints
`⛔ IGNORED (rows measured, suite not in the table — excluded from every number below, including META): lon`.

## WHAT LANDED — THE GATE (`SCRIP/scripts/test_gate_argnote_sweep.sh`)

The tree is `-prune`d out of the find *by construction*, and the resulting list is then **re-checked**
rather than trusted, because a prune is one edit away from being lost and this gate's `CORPUS` is
env-overridable. The assertion prints a **count, never a path** from that tree.
**Negative-tested by injection:** with the prune removed and the assertion left in, the gate fails
`FAIL off-limits tree reached: 99 file(s) …` at **exactly 99**, and it fails *before compiling
anything*. With the prune in place the gate is **GREEN**.

⛔ **A TRAP THAT VOIDED MY FIRST NEGATIVE TEST, AND IT WILL VOID YOURS.** Both this gate and the
scorecard derive `S4E`/`SC` from **their own `dirname`**. I first ran the injected copy from a
scratchpad directory: `$CORPUS` resolved to a path that does not exist, `find` returned nothing, the
assertion passed over an empty list — and **the gate printed `GATE GREEN` on zero programs**. A
control copy of either script must live in `SCRIP/scripts/` or it measures nothing while looking like
it measured everything (the s68 vacuous-gate class, hit twice in one session: the same trap first
produced `SKIP scrip not built` for the scorecard control arm). ⭐ Independently of this row, **that
gate reports GREEN on an empty program list** — it has no floor. Not fixed here; named.

## ⭐⭐ THE META ANSWER — DROPPING `lon` MOVES THE HEADLINE NUMBER **UP**, AND THAT IS THE THING TO SAY OUT LOUD

The DONE-WHEN asks for META recomputed without `lon`. The rigorous form of that question is a
**controlled A/B on identical rows** — same measurements, old script vs new — which isolates the
drop's arithmetic from five days of compiler change. The only board in this tree that ever measured
`lon` is the s91 baseline, reconstructed as a 13-suite union (`…-115505-combined` minus its
`csnobol4_suite` run, plus `…-115505-part2`, the continuation run that re-ran `csnobol4_suite` wider
and added `gimpel`/`lon`/`misc`): **1291 rows.**

| arm | suites scored | effective weight `tw` | META |
|---|---|---|---|
| **A** — script as it was, `lon` SCORED | 12 | **113** | **38.2** |
| **B** — script as of this row, `lon` DROPPED | 11 | **108** | **38.9** |

The other **12 suite lines are byte-identical** between the arms. `lon` scored **23.8** (N=21,
UNSCR=78 — the pre-s185 state), well under the board's own 38.2, so removing it **raises META by
+0.7**. Under `lon`'s post-s185 honest score of **12.5** (seat1, after the include fix took UNSCR
78→43 and N 21→56) the same arithmetic gives **37.7 → 38.9, +1.2**.

⛔ **THEREFORE: A POST-s189 META IS NOT COMPARABLE TO A PRE-s189 ONE, AND THE DIFFERENCE IS IN THE
FLATTERING DIRECTION.** The scorecard's headline number improves because it stopped running its
worst-scoring suite. This is HQ-73's law — *UNSCR hides SCRIP reds* — in its mirror image: **dropping
a suite hides them too, and it hides them upward.** Any comparison across s189 must say which side of
the drop it is on.

## THE TOTAL IS SHORT BY 5 AND STAYS SHORT — `lon`'s POINTS ARE NOT REDISTRIBUTED

Per the brief, the weights are **Lon's knob**. The declared table total is now **113, deliberately
short of 118**, and where those 5 points go is Lon's call — a question for Lon, not a drive-by.

⛔ **Two totals, do not confuse them.** The **declared** total (118 → 113) is the weight table. The
**effective** denominator `tw` is computed per board from suites that produced scoreable rows, so META
renormalises and is *never* "out of 118" — on the union above `tw` was already 113 with `lon` present,
because `gimpel` contributed **0** (all 145 of its programs were `ORACLE_FAIL`). A reader who divides
by the declared total gets the wrong number in both eras.

## RUN-PATH A/B — THE EDIT IS INERT ON EVERY SURVIVING SUITE

`report`-only verification would not have proved the runner still works. Both arms were **run**
end-to-end over `beauty_suite` + `csnobol4_suite` (141 programs, 64s each at `--jobs 12`, same
binary): **140 of 141 rows identical** in status pair and note.

⛔ The single moving row is **exonerated, and only a self-diff could do it.** `csnobol4-suite/nqueens.sno`
came back `TIMEOUT/TIMEOUT` in arm A and `SIG11/SIG11` in arm B. Re-running the **control arm alone
three more times** gave `SIG11/TIMEOUT` every time, and the edited arm gave both `SIG11/TIMEOUT` and
`SIG11/SIG11` — so the outcomes span the same set in both arms and the row is **arm-independent
nondeterministic**. It never PASSes in any run, so it never moves a score. (seat7's s184 law, second
instance: self-diff the control arm before you attribute a mover.)

## RECEIPTS

- **Pristine.** `make pristine` rc=0 before any published number (`scrip` + `out/libscrip_rt.so`
  rebuilt), RT_OPT `-O0` per FACT RULE O0-DEV. SCRIP `23d2b914`. Oracle verified alive first
  (`sbl -b probe/m1/m1_alt_arm2_cap.sno` → `b`, rc=0) — without it every board verdict is a plausible
  all-FAIL fiction.
- ⛔ **The A/B is binary-invariant by construction** — both arms ran the same binary — so its +0.7 is a
  property of the change, not of the build. The absolute suite numbers below are the pristine build's.
- **`gawk` is NOT installed here and `report` does not need it.** The goal file's setup line says
  `report` needs gawk; measured, the default `mawk` produces the full table. `AWK=gawk` *fails*
  (`gawk: command not found`) on a container without it — the env override is a footgun, not a
  requirement.
- Off-limits discipline held throughout: **no file under `corpus/programs/lon/` was read, cat'd,
  grepped for content, or executed by this seat.** Only path counts (`99` `.sno` files) were taken, and
  only counts appear in this document, in the committed assertion, and in the postoffice.
- `lon-include-root` **confirmed still SUSPENDED**: `claims/lon-include-root.claim` = `seat1` with no
  `DONE` line, and the row is still present in `QUEUE.tsv` at rank 3 — seat1 left it locked on purpose.

## ⛔ NAMED, NOT FIXED — THREE MORE WILDCARD WALKERS, NONE A VIOLATION TODAY

All three default to roots that cannot reach the tree, so none is touched here; each becomes one if a
caller widens its root, and none would be caught by a name-grep:

| script | default root | reaches `lon`? |
|---|---|---|
| `util_sweep_dyn89_parse_errors.sh` | `${1:-corpus/programs/snobol4}` — **positional**, caller-supplied | no, by default |
| `test_gate_zdp_on_null.sh` | `${CORPUS_DIRS:-corpus/programs/snobol4 corpus/probe}` — env-overridable | no, by default |
| `util_fc_spine_census.sh` | `${CORPUS:-corpus/crosscheck}` — env-overridable | no, by default |

⛔ `util_sweep_dyn89_parse_errors.sh` is the one to watch: it takes its root as **`$1`**, and it prints
the parser's **first error line** for each file — which on a file from that tree would echo source
text into a transcript. That is the credential half of the rule, not the execution half.

⭐ **THE GENERALISABLE MOVE, for whoever audits this rule next:** *a directory is protected by name
only against tooling that says its name.* Grep the corpus **roots** that tooling walks, not the
directory being protected. The one-line census that finds this class:
`grep -rn 'find .*\$CORPUS[" ]' scripts/*.sh` — then read each hit's default root.

## SUGGESTED ROWS (asked, not worked)

1. **`rules-lon-propagation-fix`** — correct ABSOLUTE RULE 1: strike *"every board/bench script that
   calls it inherits that"* (zero callers, measured) and add the wildcard-walker census above.
2. **`argnote-gate-floor`** — `test_gate_argnote_sweep.sh` prints `GATE GREEN` over an empty program
   list. Give it a floor; it is a `test_gate_*` and currently passes when it measures nothing.
3. **`lon-weight-ruling`** — Lon's call on the orphaned 5 points (leave the total at 113, or reassign).
