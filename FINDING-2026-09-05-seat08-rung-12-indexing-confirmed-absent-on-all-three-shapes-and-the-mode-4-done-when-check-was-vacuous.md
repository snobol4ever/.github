# FINDING 2026-09-05 seat08 — rung 12 (first-argument indexing) confirmed absent on all three required structural shapes; the task's own mode-4 DONE-WHEN check was vacuous (asm labels escape `/` as `$2F`, never literal `/`)

**Seat:** seat08 (hq_C lane) · **Mode:** FLEET-20 · **Tree:** SCRIP `674319235` · corpus `4e11cb9ee` · `.github` `eaa774b05`
**Task:** `prolog-rung-12-first-argument-indexing-no-clause-step-on-a-bound-first-arg` (minted by hq_C, 2026-09-04)

## 1. Role and scope

Per the task's own GOAL text, this row splits in two: "THE ENGINE HALF ... indexing is a performance
box" belongs to the engine owner (hq_C/hq_U under the current 20-seat cut); "THE WALK" — cutting the
required witnesses, running them, and filing the reds — is the seat's job. This FINDING is the walk. It
does not implement first-argument indexing.

## 2. The walk: three structural witnesses, all measured fresh on today's tree

hq_C's own mint-time witness already proved the mode-3 structural criterion RED (case (a) below). The
task GOAL asks for two more shapes to bound the class. All three use `fact(a,1). fact(b,2). fact(c,3).`
and are graded on swipl's answer (functional correctness) AND on the structural criterion from ARCH sec
E row 12 — `--compile` emits ZERO clause-dispatch (`_step`) sites for the call, trace shows `Exit` not
`*Exit`/no `Fail: ... -> <pred>_step` line — never on the answer alone.

| case | call | swipl oracle | m3 answer | m3 clause-step `Fail` lines | verdict |
|---|---|---|---|---|---|
| (a) bound, matches middle clause | `fact(b,X)` | `2` | `2` | 1 (`Fail: n2_call $unify -> fact/2_step`) | RED — reconfirms hq_C's mint-time measurement, unchanged on today's tree |
| (b) unbound first argument | `fact(X,2)` | `b` | `b` | 1 (`Fail: n5_call $unify -> fact/2_step`) | CONTROL, not a defect — no index (static or dynamic) can prune an unbound argument, so walking every clause is the *correct* behavior; included to prove the other two cases aren't measuring a case indexing couldn't help anyway |
| (c) bound, matches LAST clause | `fact(c,X)` | `3` | `3` | 2 (two `Fail: ... -> fact/2_step` lines) | RED — the worst case: with N=3 clauses a linear scan pays N−1 failed unifications, the most visible instance of the missing structural property |

All three answers match the swipl oracle — functional correctness is intact throughout; only the
structural/performance property named by ARCH sec E row 12 is missing, exactly as the row frames it.

## 3. Root cause, precisely: not merely "unlanded" — deleted by the rung-0 cut and never rebuilt

ARCH-PROLOG-BYRD-BOX-TRANSLATION.md § B.3 describes the mechanism as already sunk: "the `$ix_g` guards
(`lower_prolog.c:827-838`, sunk at `bb_call_fn.cpp:379`) become the WAM's `switch_on_term` at `P.α`...".
Measured directly against today's tree: **neither citation describes real code.**

- `lower_prolog.c:827-838` today is the `assertz`/`retract`/`clause` builtin-dispatch block (unrelated).
- `bb_call_fn.cpp` is 140 lines total; there is no `ix_g` anywhere in it (confirmed by direct grep).
- The *only* surviving reference to `$ix_g` in the whole tree is a dead dispatch-table string,
  `src/runtime/by_name_dispatch.c:227`, that nothing in the current lowerer ever names or reaches.

`git log -S'ix_g'` shows why: `$ix_g` was a real, shipped optimization —
`de84e601b`/`bd7a695a8` "PL-SPEED-5 slice A: first-arg pre-try indexing guards", `4a40e3733`/`caea68f72`
"PL-SINK-4: emitted $ix_g specialized index guard (97.1% leaf-call elimination, 1.068x)",
`0f9110ff3`/`85f09f79a` "PL-ZK-2b/2c" — built on top of the **old**, pre-rung-0 Prolog control machine
(the `plc_*` solver / by-name cascade). `db299d417` ("prolog: RUNG 0 — THE CUT... -5,050 lines",
2026-09-02) deleted that entire machine wholesale, per Lon's rebuild-from-zero ruling. `$ix_g`'s
lowering and emission sites were part of what got deleted; the feature was never re-implemented against
the new Byrd-box construct-ladder engine. The ARCH doc's B.3 bullet is a stale pointer to deleted code —
measured, not assumed. **Correction annotation added in place at the B.3 bullet** (not a rewrite — the
bullet still correctly describes the *intended* design, WAM `switch_on_term` at α with a compile-time
candidate bitmask; it just no longer describes anything that exists).

## 4. A second, independent bug found while walking: the task's own mode-4 DONE-WHEN check is vacuous

The baton's DONE-WHEN mode-4 arm is `grep -cE "fact/2_step" file.s`, required to read 0. Measured: it
reads 0 **on all three witnesses, including case (a) and (c) where the feature is definitely absent** —
so this check cannot distinguish "indexing landed" from "indexing was never implemented, and the pattern
can't match anyway." Cause: **`/` is not a legal assembly-label character and is never emitted literally.**
`bb_call_proc_staged.cpp:254,462` mangles any non-`[A-Za-z0-9_$.]` byte in a compiled name to `$` + its
uppercase hex value (`$%02X`) before building a label; `/` is `0x2F`, so `fact/2` becomes `fact$2F2`, and
the actual label built at `emit.cpp:2731` (`emit_label_alloc("%s_step", fam)`) is `fact$2F2_step`.
Confirmed directly in the emitted `.s` for all three witnesses: `fact$2F2_step:` appears (one dispatch
site per candidate clause — 3 sites for cases (a)/(c), matching the clause count), `fact/2_step` never
does and structurally cannot. This is the same class hq_P named today in a different row ("a generated
witness/artifact deserves the same suspicion as a generated number") — a DONE-WHEN that reads green for
a reason unrelated to the property it claims to grade is a false-negative gate waiting to fire the moment
someone actually lands the fix and the check keeps reporting 0 for the wrong reason.

**Fixed** (instrument-level — in scope for the walking seat per today's onboarding ruling: "cure only
fixture-, xfail-, or instrument-level reds yourself"): the baton's DONE-WHEN mode-4 line now checks
`grep -cF "fact\$2F2_step"` for the real mangled label. Note the SECOND, nested trap found while fixing
the first: this seat's `grep` is wrapped (`exec -a ugrep ...`), and unlike GNU grep, its `-E` mode treats
a mid-pattern `$` as a line-end anchor even when the shell delivers a correctly-escaped literal `\$` —
so a first fix attempt (`grep -cE "fact\$2F2_step"`) *silently kept reading 0*, for a third, independent
reason, and would have shipped a "corrected" check that was still vacuous had it not been sanity-tested
against a witness's `.s` known to contain the label before being trusted. `-F` (fixed-string, no regex
metacharacters at all) sidesteps the anchor question entirely and was verified to read the true count
(14 sites) on case (a)'s `.s`. Filed here because the same wrapped-`grep`-plus-mid-pattern-`$` trap can
bite any other DONE-WHEN in this tree that greps for a literal `$`-mangled name — not audited beyond
this row, out of scope for the walk. This does not change the row's verdict — it was RED before for the
right reason (m3) and stays RED now for both the right m3 reason and a *now-truthful* m4 reason (the
labels are genuinely present, one per clause, for all three witnesses).

## 5. Unrelated pre-existing reds surfaced by the required control arm — not this row's, already tracked

The baton's DONE-WHEN also requires `test_prolog_ladder.sh --to 9` to print `LADDER OK`. Measured fresh
(same tree): it does not — `LADDER RED: 10 of 380 witness x mode gradings FAIL`, all four in rungs
unrelated to indexing: `ladder__rung01_unification_occurs_check`, `ladder__rung06_streams_read_term_empty_options`,
`ladder__rung07_repeat_repeat_bounded_by_counter`, `ladder__rung07_repeat_repeat_with_cut`,
`ladder__rung08_bagof_setof_free_variable_grouping`. Checked before treating this as news: all are
already tracked as FREE rank-1 rows owned by hq_C in QUEUE.tsv
(`prolog-bagof-setof-free-variable-grouping-with-caret-is-rung-8b`,
`prolog-read-term-from-atom-3-unimplemented`,
`prolog-inria-bagof-setof-free-var-identity-and-grouping-broken`) or an existing FINDING
(`FINDING-2026-09-04-seat04-unify-with-occurs-check-2-does-not-exist-in-scrip-prolog.md`). No source
under `src/` was touched before this measurement (build was a plain incremental `make` of an unmodified
tree), so these are pre-existing, not caused by this session. Recorded here only so the next reader of
this row's DONE-WHEN is not surprised that the ladder arm fails for reasons that have nothing to do with
indexing — landing indexing alone will not turn this row's DONE-WHEN green while those four remain open.

## 6. Disposition

Not claiming `done` — the actual engine fix (WAM-style `switch_on_term`/compile-time candidate-set
pruning in the shared clause-dispatch path, `bb_call_proc_staged.cpp` + `lower_prolog.c`) has not
landed; claiming green here would be exactly the false-green class this whole row exists to correct.
Walk is complete: three witnesses cut and measured (§2), root cause precisely isolated to the rung-0 cut
deleting the old mechanism (§3), one instrument-level bug found and fixed (§4), one unrelated pre-existing
control-arm gap surfaced and cross-referenced rather than chased (§5). Handed to hq_C (own lane; message
sent same session) with a note that the shared-box touch point (`bb_call_proc_staged.cpp` is common to
Icon/SNOBOL4/Prolog) may make this a shared-node class for hq_U for hq_C to route to accordingly.
