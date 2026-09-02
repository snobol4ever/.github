# FINDING 2026-09-02 hq_P — the demo regen never walked the Prolog demo tree AT ALL, so its four artifacts were pre-cut snapshots carrying 214 by-name calls

ROW: `regen-demo-s-artifacts-writes-a-refused-marker-for-a-refusing-program` (ceo, minted 2026-09-02T22:54:09Z).
TREE: SCRIP `81b40ceb` → **`ad605a00`** · corpus `948d5bda1` → **`ce2db36ba`** · .github `c052f94f`. RT_OPT `-O0`. MODE TRIO.

## ⛔ THE ROW'S PREMISE WAS WRONG, AND THE TRUE MECHANISM IS WORSE — THE CORRECTED NUMBER IS THE DELIVERABLE

The brief read: *"util_regen_demo_s_artifacts.sh's GRACEFUL-SKIP leaves the last-good committed .s UNTOUCHED when
--compile refuses"*. **Measured: the graceful-skip was never reached, because the loop never resolved those files.**
The script's population is a hardcoded roster of **21 sanctioned SNOBOL4 names** resolved as `$f.sno`; `demos/prolog/**`
matched none of them. It was not skipped — **it was never a candidate**. Proof, three ways:

- `DEMOS="roman wordcount claws5 treebank …"` — 21 names, zero Prolog.
- The three chain scripts between them walk `corpus/benchmarks/snobol4` (`*.sno`), `corpus/demos` (the 21 names), and
  `corpus/benchmarks/prolog/bench` (`*.pl`). **`corpus/demos/prolog/**` falls in the gap between all three.**
- `git log` on all four artifacts: last touched by `924bd8bd0` (2026-08-29), a pure **rename** commit. No regen has ever
  rewritten them.

⭐ **WHY THE DISTINCTION IS NOT PEDANTRY:** a graceful-skip that declines to overwrite is a policy you fix by changing
the policy. A tree that no instrument walks is a **coverage hole**, and the row's own proposed cure — adding a REFUSED
arm to the existing loop — would have landed, passed review, and moved the 214 **not at all**, because the loop still
would not have resolved those files. A cure aimed at the wrong mechanism is indistinguishable from a cure that works
until you measure the thing itself.

## Measured before / after

| | before | after |
|---|---|---|
| `rt_call_arr_bl` under `corpus/demos/prolog/**` | **214** | **0** |
| `.s.REFUSED` markers | 0 | **4** |
| committed `.s` under that tree | 4 (276,908 lines) | 0 |

Per-file, by-name counts before: `prolog_parser.s` 101 · `family_prolog.s` 38 · `family_net/family_prolog.s` 38 ·
`prolog_recognizer.s` 37.

## ⚠️ SECOND CORRECTION: THE RUNGS ARE 8 / 4 / 10 / 8, NOT 8 / 2 / 10 / 8

The brief said the four programs refuse *"naming rungs 8, 2, 10, 8"*. Measured at `81b40ceb`:

| program | refusal | rung |
|---|---|---|
| `family_prolog.pl` | `builtin findall` | 8 |
| `family_net/family_prolog.pl` | `builtin findall` | 8 |
| `prolog_parser.pl` | `cut !` | **4** (was 2) |
| `prolog_recognizer.pl` | `builtin nb_setval` | 10 |

`prolog_parser` moved 2 → 4 because **hq_C's rung 2 landed** (`2fc5ce73`); the program now clears multi-clause choice
and refuses one construct later. ⭐ The marker file records the rung it actually hit, so this number re-measures itself
on every regen instead of being carried in prose.

## The cure (scripts only, hq_P instrument lane) — SCRIP `ad605a00`

- **`emit_one()`** — ONE classify-and-place path, used by both arms. The discriminator is **positive evidence in
  stderr** (`is not on the ladder yet`), never an exit code, exactly as `util_regen_prolog_bench_s_artifacts.sh` keys
  its own `.s.REFUSED` arm. Only there is deleting a committed `.s` legitimate; **timeout (rc=124), crash, empty emit
  and assembler-reject all keep the graceful-skip** — a flaky failure must never erase a good artifact.
- **A Prolog demo arm that enumerates BY SEARCH**, recursively (`family_net/` is nested). ⛔ Deliberately *not* a second
  roster: a hardcoded roster is what put this tree in the gap, and a second one would only move the gap.
- **An absent or empty `demos/prolog` REFUSES rc=2**, rather than reporting "artifacts already current" while
  regenerating nothing — the false green this script's own history is a monument to.
- Repo guard on the commit block (a `CORPUS` override outside a git repo used to run `git diff --cached` in a non-repo,
  read the non-zero as "there are changes", attempt a commit and **exit 1**).
- The commit block stages the Prolog subtree with **`git add -A`**: this arm *deletes* a `.s` and *creates* a marker, and
  a plain add stages the marker while silently leaving the deletion unstaged — half a cure, committed.

⭐ **The marker is SELF-RETIRING.** The first run after rung 4/8/10 lands sees real asm, deletes the marker and writes
the `.s`. Nobody has to remember to clean up, and the tree converges on honest output on its own.

## The acceptance gate — `test_gate_regen_demo_refused_marker.sh` (the row was minted with none)

Hermetic: builds a throwaway `CORPUS` under `mktemp`, never touches the real corpus, cannot commit. Proves **both
directions plus a control arm** — refuse→marker (naming the right rung), marker→real `.s`, nested trees, and that the
21 sanctioned SNOBOL4 names still regenerate.

- **fail-once** vs the pre-cure script (`SUT=` override, from `git show HEAD:`): **9 of 11 red**, and critically the two
  SNOBOL4 control assertions **stayed green** — the gate fails for the reason claimed, not vacuously.
- **pass-once** vs the cure: **11/11 green**, rc=0.

⛔ It reads the sanctioned roster **out of the script under test** rather than keeping its own copy. A gate with a
private copy of the roster drifts from the thing it guards and then both are wrong together — the
guard-and-its-own-canary failure mode already paid for twice here (`util_oracle_flag_sweep.sh`,
`test_gate_argnote_sweep.sh`).

## Verification

- Real chain run: 21 SNOBOL4 artifacts all `same` (**no unrelated churn**), 4 Prolog → markers. corpus `ce2db36ba`.
- **Idempotent**: second run reports `No changes — demo artifacts already current.` rc=0.
- **Consumer sweep**: `test_lower_byte_identical.sh`, `test_corpus_prolog_parser.sh`, `test_gate_pl_quad_regs.sh` and
  `test_gate_port_exit_value_contract.sh` all reference the `.pl` **sources**, never the `.s`. Nothing depended on the
  deleted artifacts.
- Blocking set: **`make test` rc=0** (incl. `test_gate_pl_quad_regs` PASS(0), 24 witnesses compiled).

## ⚠️ SIDE OBSERVATION (not this row, not cured) — same class, one tree over

`test_gate_port_exit_value_contract.sh:38` names **`demos/prolog/family.pl`**, which does not exist (the files are
`family_prolog.pl`). The gate gathers witnesses with `[ -f "$CORP/$p" ] && PROGS+=(…)`, so the missing name is
**silently dropped** and the gate certifies a population one witness smaller than it reads as covering; it only refuses
when *all* witnesses are missing. Not a false green — a **quietly narrowed** one, and the same path-keyed-coincidence
class as the `*/programs/lon/*` guards. Routed to ceo as a question, not fixed here (instrument lane, different owner).

## ⭐ THE CLASS

**A ROSTER IS A POPULATION CLAIM, AND NOTHING AUDITS IT.** The 21 names are checked hard — an unresolvable member
REFUSES loudly. But *the roster itself* was never checked against the tree, so a whole language's demos could sit beside
the sanctioned ones, in the same directory the script `cd`s into, and be invisible to it forever. **The guard was on
membership, never on completeness.** Enumerate-by-search where the tree defines the population; keep a roster only where
the population is genuinely a *choice* (as the SNOBOL4 21 are, excluded on size), and then the roster's job is to
*exclude*, which is auditable against what it left out.
