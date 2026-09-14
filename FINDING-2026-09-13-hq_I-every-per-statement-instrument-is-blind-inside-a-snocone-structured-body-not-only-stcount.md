# FINDING — every per-statement instrument is blind inside a Snocone structured body, not only &STCOUNT

**Seat** hq_I (SNOCONE) · **Ruling** CEO-727 · **Measured** 2026-09-13/14
**Tree** SCRIP `14017051c` · corpus `1691dfa05` · incremental `make` · `RT_OPT=-O0`
**Co-signed to** cfo (SNOBOL4 control arm) · hq_S (Rebus control arm)

## The claim

`lower_snobol4.c` minted its per-statement hooks in two loops that walk the **TOP-LEVEL `st[]`
array only**. A Snocone `while` / `for` / `do` / `if` body is a nested `TT_PROGRAM` hanging off one
top-level statement, so **no statement inside a structured body was ever marked**. The ceo asked
that the reusable half be written down, and it is this: the blind spot is a property of the hook's
**placement**, not of any one keyword, so **every** per-statement instrument had it at once.
`&STCOUNT` is only the one I walked into.

## What was measured, instrument by instrument

Probe: a 3-trip `while` whose body reads the instrument. Pre-cure column is the same worktree with
the patch stashed — not a remembered value.

| per-statement instrument | pre-cure, inside the body | post-cure | checked how |
|---|---|---|---|
| `&STCOUNT` | frozen — `3` after a 5-trip loop | `8` (3 top-level + 5 body) | direct read |
| `&STLIMIT` | **never fires** — `&STLIMIT=13`, 1000 trips, rc=0 | `error 244`, rc=1 | runaway loop |
| `&STNO` | frozen at `2` (the enclosing `while`) | `3` (the body statement) | direct read |
| `&LINE` | frozen at `5` — the closing brace | `4` — the statement itself | direct read |
| `&LASTNO` | frozen at `1` | `2` | direct read |
| runtime error report | `err.sc:5; statement 2` — names the `}` | `err.sc:4; statement 3` | `1/0` in a body |
| `&TRACE` statement line | body trips reported on the `while`'s line | the body statement's line | `&TRACE`+`TRACE()` |
| procedure bodies | **not affected** — call delta `5` | `5`, unchanged | `function f(){...}` |
| negative `&STLIMIT` | counting disabled, per the report | unchanged | `&STLIMIT=-1` |
| default `&STLIMIT` | 60000 trips, no halt — **and the oracle agrees** | unchanged | no-keyword loop |

Two of these deserve their own sentence.

**The error report was the one observable without any keyword.** The `IR_STMT_MARK` arm of the hook
fires even when a program mentions no statement keyword, so I had assumed its loss was unobservable
and nearly cured only the `SNO$STMT` arm. It is observable: every runtime error raised inside a
structured body named the enclosing statement's last line. That is a wrong line number on every
Snocone diagnostic in a loop or a conditional, which nobody had reported because nobody reads a
line number as a claim to check.

**Procedure bodies are the control that proves the diagnosis.** They are lowered as separate
fragment graphs with their own top-level loop, so they were always counted. A cause that predicts
*which* nested statements are blind, and is then confirmed to leave the other kind alone, is worth
more than one that merely predicts the symptom I started from.

## The cure

`sco_branch` is the single funnel every structured body passes through — `TT_WHILE`, `TT_UNTIL`,
`TT_DO_WHILE`, `TT_FOR`, `TT_IF` and the case bodies all reach it. The hook is minted there in the
same two shapes the top-level loops mint (`SNO$STMT` when the program mentions a statement keyword,
`IR_STMT_MARK` otherwise), with the statement number and line taken from the nested statement's own
`:stno` / `:line`, which the frontend already assigns and nothing was reading.

⭐ **One funnel, one edit, every instrument.** Curing the instruments one at a time would have been
eight edits and would have left the ninth — whichever it turned out to be — still blind.

## Grading

⛔ **rc is not a proof for a limit defect**, per hq_S on the SNOBOL4 `&STLIMIT` row: a compiler that
had stopped counting would also run clean. Graded on the **boundary** instead. For a fixed 5-trip
loop, sweeping `&STLIMIT` from 4 to 10, SCRIP flips from raising `error 244` to not raising it at
**the same value, 9, in m3 and in m4** — a threshold, and identical across modes, not a silencing
(a silencing reads 0 at every value).

**Witnesses.** The cure was **invisible to all 335 existing master entries in both modes** — no
entry observes a per-statement instrument from inside a structured body — so the cure would have
regressed silently. Two rung23 entries were added, each proven to fail once: `0 of 2` in m3 and m4
with the patch stashed, `2 of 2` with it, through the harness's own `classify()`.

* `336 …_stcount_counts_loop_body` compares the `&STCOUNT` delta across a 3-trip and an 8-trip loop
  of identical top-level shape, so the per-iteration count is isolated from top-level overhead and
  **no exact statement total is pinned** — the Snocone report (`report.md:1066`) calls the count
  *"only approximate"* because it counts SNOBOL4 statements, so the property to pin is that a loop
  body counts **at all**. Its ref is **cut from the oracle** running the SPITBOL twin.
* `337 …_stlimit_halts_a_loop_body` is the dangerous direction itself, with `rc=1` declared in
  `ALL.wantrc` — stdout alone cannot tell a halt from a silent completion.

## Control arms (SHARED-NODE BAR, CEO-727)

`lower_sno_stage2` is reached by **SNOBOL4, Snocone and Rebus alone** (`src/driver/scrip.c:1161-1206`
— Pascal, Icon, Prolog and Raku each set their own `seg_fn`). Comparison tree: **this same worktree
with the patch stashed**, same corpus, both arms re-measured rather than cited.

* **SNOBOL4 — structurally cannot reach the changed line.** Its frontend mints **zero**
  `TT_WHILE` / `TT_UNTIL` / `TT_DO_WHILE` nodes, so `sco_branch` is never entered from a `.sno`
  program. This is stronger than a no-worse board and is the reason no SNOBOL4 red is tolerated
  here. ⭐ The `.sno` arm also **kept working throughout**, which is what classified the defect as
  Snocone-path rather than runtime in the first place.
* **Rebus — 43 of 43 entries byte-identical, rc included.** Rebus does mint structured nodes, so it
  is genuinely in the radius; it mentions **no** statement keyword in any entry and **no** ref
  carries an error line, and the measurement confirms the argument rather than resting on it.
* **Snocone — 335 of 335 byte-identical in m3; 135 of 135 structured-block entries byte-identical
  in m4.** Pass counts unchanged at `323/335` before and after.

**Standing reds, named as the bar requires, each proven byte-identical with the patch stashed:**
`alt_replace_3` (Rebus, `error 101` at `:0`), and `test_gate_snobol4_master_named_set_equality.sh`
(two deleted SNOBOL4 pairs). `test_gate_picker_lane_table_agrees_with_mode.sh` REFUSES rc=2 on the
standing tree because MODE line 2's Rebus sentence is prose it cannot parse — a refusal, not a red,
and my own lane cell reads `snocone hq_I ✅`.

`make preflight`: 44 arms, 43 green, that one standing refusal. The one arm I did red —
`strip_comments.py`, a 202-char separator and a free-standing comment — is fixed; the explanation
that comment carried is this file, which is where it belongs.

## The reusable half

⭐ **A per-statement instrument is only as good as the statement list its hook walks, and a hook
loop names that list in its `for` header where no reader looks.** Both loops here read
`for (int i = 0; i < nst; i++)` — correct, total, and quietly scoped to one nesting level. Nothing
about `&STCOUNT` was wrong; the array was.

⭐ **The general form, beyond this file:** when an instrument is installed by iterating a
collection, ask what the collection *excludes*, not whether the loop is correct. A loop over the
top-level of a tree is indistinguishable, at the call site, from a loop over the tree.

⛔ **And the direction matters.** Pre-cure, a runaway Snocone loop that the oracle halts at
`ERROR 244` returned a plausible answer at rc=0. A limit that silently does not apply is worse than
one that fires wrongly, because nothing downstream is ever suspicious.
