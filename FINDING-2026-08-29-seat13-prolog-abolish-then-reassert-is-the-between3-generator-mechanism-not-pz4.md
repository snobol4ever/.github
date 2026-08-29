# FINDING — `abolish_then_reassert`'s SCRIP-DIFF settles seat06's open question: it shares seat14's
# `between/3` mechanism (the shared by-name generator dispatcher `rt_call_arr_gen`), NOT PZ-4/lexprep —
# and the same shared idiom is confirmed present in at least 2 of the family's `_gen` functions

**seat13 · 2026-08-29 · row `tests-consolidate-prolog`** (closes the question seat06's own FINDING left
open: `FINDING-2026-08-29-seat06-prolog-abolish-does-not-raise-existence-error-...md`, "plausible same-root-
cause link to seat14's between/3 finding... needs verification, not assumed")

**Not fixed — diagnosis only, ASM-DIFF-FIRST discipline applied, nothing committed to SCRIP/corpus.**

## 0. The question on the table

`rung15_abolish_abolish_then_reassert.pl` backtracks into 2 `assertz`'d facts via `color(X), write(X), nl,
fail` and SCRIP prints only the first (`green`, not `green\nyellow`). seat06 asked: is this the SAME
mechanism as seat14's already-documented `between/3`/`for/3`/`current_stream/1` "first-solution-only"
defect, or a coincidental symptom match? **Answer: the same shared mechanism — confirmed by ASM-diff and
by reading two of the family's C implementations, not by symptom comparison.**

## 1. Minimal ablation ladder — `abolish` is irrelevant; the trigger is in-body `assertz`

Four purpose-built witnesses (not the original 9-line corpus file), `--run` (m3) then `--compile` (m4):

| witness | shape | m3 | m4 |
|---|---|---|---|
| `mini_static_backtrack.pl` | `color(green). color(yellow).` static clauses | **green/yellow** | (not needed, control) |
| `mini_assertz_backtrack.pl` | `:- assertz(color(green)). :- assertz(color(yellow)).` top-level directives | **green/yellow** | **green/yellow** |
| `abz_inbody.pl` | `main :- assertz(color(green)), assertz(color(yellow)), color(X), write(X), nl, fail.` | **green only** | **green only, rc=1** |
| `abz_inbody_abolish.pl` | same + a leading `abolish(color/1)` | **green only** | (redundant, same as above) |

**`abolish` changes nothing — `abz_inbody.pl` (2 lines, no abolish) reproduces the bug exactly.** The
sole differentiator is whether `assertz` executes as a top-level directive (before `main` starts) or as a
goal inside the same clause body that later backtracks — i.e., whether `color/1`'s clause set is knowable
at compile time or only at runtime. Existing corpus sibling `rung13_assertz_asserta_order.pl` (converted,
`.ref` = `a\nb\nc`, currently PASSING) independently confirms the directive form works for 3 facts, not
just 2 — a real, already-graded control, not a new one.

## 2. Why this refutes "PZ-4/lexprep" as the differentiator, even though the test harness labels it that

`scripts/test_prolog_rung{13,14,15,30}.sh` print `FAIL ... (loose -- known PZ-4 prolog-multiclause-uninit-
lexprep-frame, rc=$rc)` **unconditionally for every failure in those scripts** — it's a blanket label
baked into the printf, not a per-file diagnosis (checked: identical string, all 4 scripts, `git log -p`
shows it landed as one generic UX change in `6cae73e1`, unrelated to this file). Taking it at face value
would be exactly the "trust a subset-count label without checking the right thing" mistake this row has
flagged before (seat02/seat14's own standing lesson).

Checked directly instead: **both the PASSING `color$2F1` (mini_assertz_backtrack.pl, static/directive
form) and the FAILING `between$2F3` (mini_between.pl) call `rt_jmp_frame_lexprep2@PLT` in their own frame
prologue** (`grep lexprep2` on both `.s` outputs). Since the passing case also goes through the exact
function PZ-4 targets, `rt_jmp_frame_lexprep2` being broken is not what differentiates pass from fail here
— ruling out the harness's generic label for this specific file. (This does not touch whether PZ-4 is
still needed elsewhere — rung14/15's other residue may well be exactly that; this finding is scoped to
`abolish_then_reassert` and its mechanism only.)

## 3. What `--dump`/`.s` diff actually shows: this is `rt_call_arr_gen`, seat14's exact family

`abz_inbody.pl`'s compiled `color/1` does **not** get the static per-clause `n4_suspend`/`n9_suspend`
shape `mini_assertz_backtrack.pl` gets. It compiles to a single `n2_call_builtin_gen` node:
```
.Lcall_builtin_gen_bynamegenfn3: .string "$dyn_iter"
lea rdi, [rip + .Lcall_builtin_gen_bynamegenfn3]
call rt_call_arr_gen@PLT
```
— the exact same by-name generator dispatcher `between/3` uses with `"$between"` (confirmed: compiled
`mini_between.pl`, `between$2F3` calls `rt_call_arr_gen@PLT` with `.string "$between"`, and reproduces
seat14's bug live: `--run` on `main :- between(1,3,X), write(X), nl, fail. main.` prints `1` only).

`rt_call_arr_gen` (`src/runtime/by_name_dispatch.c:4764`) is a single dispatcher fanning out to **13+
named constructs by string match**: `$between`, `$dyn_iter`, `$call`, `$clause`, `$current_predicate`,
`$predicate_property`, `$current_op`, `$current_prolog_flag`, `$current_stream`, `$stream_property`,
`$sub_atom`, `$for`, `$bag_group`, plus `find`/`upto`. seat14 independently found 3 of these
(`$between`, `$for`, `$current_stream`) broken the same way; this session adds a 4th (`$dyn_iter`) via a
completely different corpus file family (rung15 vs rung50/66), which is exactly the cross-check this
row's own standing lesson asks for before trusting a bucket. **One shared dispatcher, one shared defect,
now confirmed from two independent starting points.**

## 4. Went one step further than either prior FINDING: checked the retry-path ASM and two `_gen` bodies — inconclusive on exact fault line, but rules out the obvious suspects

Per RULES.md's ASM-DIFF-FIRST (diff before gdb): read `between$2F3`'s full retry wiring.
`n4_suspend_β → n3_call_builtin_gen_β → .Lcall_builtin_gen_α_11_60` — the retry entry **skips the
`mov qword ptr [rsp+128], 0` resume-cell zeroing** that only the fresh α path executes, then re-issues
`lea rcx, [rsp+128]; call rt_call_arr_gen@PLT` with the **same** resume-cell address. This is the correct
shape per `bb_call.cpp`'s own comment ("alpha zeroes resume cell, beta re-pumps invoke with persisted
cell") — **no obvious emitter bug at this site.**

Read two of the family's C bodies (`rt_pl_between_gen` at `by_name_dispatch.c:4546`, `rt_pl_dyn_iter_gen`
at `unification.c:1481`) — **byte-for-byte the same idiom**: `if (*resume==0) { allocate iterator via
rt_ws_alloc; *resume = (int64_t)(intptr_t)it; }` then `while (it->cur...) { ...; return first success; }`,
relying on `*resume` surviving as a live pointer across the suspend↔retry boundary. Neither function looks
locally wrong in isolation. `rt_ws_alloc` itself (`src/runtime/rt/rt_arena.c`) is used pervasively for
long-lived tables (atom tables, hash tables) — not obviously a backtrack-scoped/rewound arena, so "the
iterator gets freed out from under itself" is not confirmed either.

**Net: the bug is real, shared, and now has a single named mechanism (`rt_call_arr_gen`'s resume-cell
protocol), but the exact fault line is still open** — candidates not yet distinguished: (a) the `[rsp+128]`-
class stack slot not actually surviving the suspend→intervening-execution→retry window (would tie back to
activation-frame retention after all, just a layer deeper than the lexprep call itself — needs a gdb watch
on the resume-cell address across one retry, the next ASM-DIFF-FIRST step, not done here), or (b) the
shared `n4_suspend_α`/`rt_pl_cp_push3`/`rt_pl_zf_resume_clear` choice-point plumbing common to both the
generator and static-clause paths, not traced this session.

## 5. Disposition

- **Corrects the bucket, not just the hypothesis**: `abolish_then_reassert.pl` should move from "8th
  SCRIP-DIFF, ASM-diff needed" into the **same bucket as seat14's `between_enum`/`for_alias`/
  `current_stream`** (real, individually-tractable-looking but actually one shared-mechanism bug) — NOT
  into the 33-file PZ-4-blocked bucket despite the harness's generic label. Left loose, NOT KEEP.md'd
  (converting it would enshrine the truncated output).
- Gate unchanged this session (no conversions attempted, this is diagnosis): `total: 156 converted: 100
  loose: 56`, matching seat06's handoff exactly.
- Mailed hq_C (this row's standing convention for runtime-bug findings) with the pointer to §4's open
  fault-line question — a gdb watchpoint on the resume-cell stack slot across one retry is the concrete
  next step for whoever takes the actual fix, and it now has 4 independently-discovered witness programs
  (`between`, `for`, `current_stream` enumeration, `$dyn_iter`) to choose the cheapest repro from.
- Witnesses (`mini_static_backtrack.pl`, `mini_assertz_backtrack.pl`, `abz_inbody.pl`,
  `abz_inbody_abolish.pl`, `mini_between.pl`) are scratch files, not committed — trivially small,
  reproduce from this FINDING's inline content rather than re-deriving.
