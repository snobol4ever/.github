# FINDING — the "6 wrong-answer Prolog bugs" were 2 files with the wrong oracle entirely, plus ONE shared backtracking defect (`between/3` never produces a 2nd solution), not 3-4 unrelated bugs

**seat14 · 2026-08-29T15:49Z · row `tests-consolidate-prolog`** (item 7 of the row's standing NEXT block — the
6 "tractable, not externally blocked" wrong-answer files seat09 originally characterized as "rc=0, real content
divergence from swipl")

**Not fixed. Root-caused and correctly bucketed, verified against BOTH stated oracles, not assumed.**

## 0. THE MISTAKE IN THE STANDING CHARACTERIZATION

CLAUDE.md names the Prolog oracle as "GNU/SWI-Prolog" — both, not just SWI. Diffing all 6 files against SWI alone
first, then checking stderr, showed 4 of the 6 fail with `swipl`'s own `Unknown procedure` error on the exact
predicate under test: `current_stream/1`, `unget_char/2`, `number_atom/2`, `for/3`. **None of these are SWI
builtins.** All 4 exist in GNU Prolog (confirmed: `gprolog` is installed at `/usr/bin/gprolog`). Diffing against
the oracle the file actually targets changes the verdict for half the set.

## 1. TWO OF THE SIX ARE NOT BUGS — MISCLASSIFIED BY COMPARISON AGAINST AN ORACLE THAT DOESN'T IMPLEMENT THE
   PREDICATE UNDER TEST

- **`rung72_unget.pl`** (`unget_char/2`, `unget_code/2` family) — scrip output **byte-identical** to `gprolog`:
  `char(A,A)` / `code(66,66)` / `byte(200,200)` / `done`. (Its self-pinned `.expected` also matches, for once
  correctly.)
- **`rung75_number_atom.pl`** (`number_atom/2`) — scrip output **byte-identical** to `gprolog`, all 9 lines.
  (Self-pinned `.expected` matches too.)

**Verdict: correct as shipped. Remove from the "wrong-answer" bucket entirely; these were never divergent from
the oracle they actually exercise, only from the wrong one.**

## 2. ONE SHARED MECHANISM ACROSS THE REMAINING THREE: A MULTI-SOLUTION BUILTIN NEVER PRODUCES ITS SECOND SOLUTION

**`rung50_between_enum.pl`** — `main :- (between(1,3,X),write(X),nl,fail ; true), findall(Y,between(1,5,Y),L),
write(L),nl, findall(Z,between(2,2,Z),S), write(S),nl, findall(W,between(3,1,W),E), write(E),nl.`

| engine | output |
|---|---|
| `gprolog` (correct) | `1` `2` `3` `[1,2,3,4,5]` `[2]` `[]` |
| scrip `--run` (m3) | `1` `[1]` *(stops — nothing further printed, rc=0, no error)* |
| scrip `--compile` (m4) | `1` `[1]` `[2]` `[]` |

**The pattern is exact: every `between/3` call that has ≥2 solutions returns only the first one on backtracking
(`X=1` then stop instead of retrying to `X=2,3`; `Y=1` instead of `[1,2,3,4,5]`). Every call with exactly 0 or 1
solutions is unaffected** (`between(2,2,Z)`→`[2]` and `between(3,1,W)`→`[]` are both CORRECT in m4). This is not
"wrong answer" in the sense of a computed value being incorrect — **the choice point is never being retried past
its first success.**

**`rung50_for_alias.pl`** — same shape, different builtin: `for(X,1,4)` via `findall` gives scrip `[1]` (gprolog:
`[1,2,3,4]`); the following `(for(Y,1,2),write(Y),nl,fail ; true)` gives scrip `1` only (gprolog: `1` then `2`).
`for/3` is GNU Prolog's own between-style generator — same "first solution only" signature.

**`rung66_current_stream.pl`** — confirms the mechanism from a third angle, via `current_stream/1`. A *direct*,
already-bound call (`current_stream(S)` for a specific, just-opened `S`) succeeds correctly (`found_bound`,
matches gprolog). The SAME predicate called for **enumeration** (`findall(X, current_stream(X), L)`, forcing
backtracking through every open stream) undercounts: gprolog's `L` contains `S` (`in_enum`) and has ≥4 entries
(`has_std_plus_open`, the 3 standard streams + the one just opened); scrip's `L` is missing `S`
(`not_in_enum`) and has <4 entries (`too_few`). **Same defect as `between`/`for`: the first solution born under
`findall`'s backtracking is retained, subsequent ones are dropped.**

⭐ **Three builtins, one mechanism: a nondeterministic call driven by an external `fail`/`findall` retry produces
exactly one solution and no more, regardless of which builtin it is or how many real solutions exist.** This is
the "no per-op filter on a family" shape this codebase names elsewhere, transposed to Prolog builtins instead of
BB nodes — worth checking whether it is in fact ONE shared retry/choice-point path (plausible, not yet proven;
see §4).

## 3. ⚠️ M3 AND M4 DIVERGE PAST THE SHARED DEFECT — NOTE FOR WHOEVER OWNS `GOAL-MODE34-IDENTICAL.md`

Both modes reproduce the identical first-solution-only truncation. **But m3 (`--run`) then goes silent after the
first (wrong) `findall` result — the two remaining goals in the same conjunction (`between(2,2,Z)`,
`between(3,1,W)`) never print anything, no error, rc=0.** m4 (`--compile`) executes those same two goals
correctly (`[2]`, `[]`) after the same wrong first two results. **This is a second, separate divergence** — not
just "the same bug in both modes" but "m3 additionally drops two whole subsequent goals that m4 does not." Flagged
per CLAUDE.md's own note that the m3≡m4 identity claim is currently unconfirmed either way; this is direct
evidence the two are NOT currently identical for this program, whatever the ruling on whether they're allowed to
differ.

## 4. NOT ATTEMPTED

Root mechanism inside the Prolog interpreter/emitter for **why** a retried choice point doesn't advance — that
needs RULES.md's ASM-DIFF-FIRST order applied properly (m3 is `sm_interp_run` tree-walking per CLAUDE.md, so
"diff the .s" doesn't directly apply to m3; m4's `.s` is available and could be diffed against a passing
single-solution `between` call as the minimal-repro pair). Out of time-box for this pass; this row's charter is
format conversion, not runtime debugging (RULES.md's cross-language-scope ruling permits it, doesn't obligate it).

## 5. DISPOSITION

Corrects `tests-consolidate-prolog`'s own item 7 characterization (task file LEDGER updated). Mailed hq_C
(runtime bugs are this task's standing convention for that lane). Nothing committed to SCRIP or corpus — this is
diagnosis only, no code changed, no `.pl`/`.expected` touched (all 6 files remain loose, none KEEP.md'd — the
between/for/current_stream trio should NOT be KEEP.md'd, they're real and fixable once someone takes the
interpreter question; unget/number_atom should be re-pointed at `gprolog` as their real oracle whenever this row's
conversion tooling reaches them, not left implying a SWI divergence that doesn't exist).
