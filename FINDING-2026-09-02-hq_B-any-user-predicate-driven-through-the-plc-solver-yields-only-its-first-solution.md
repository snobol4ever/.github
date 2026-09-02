# FINDING 2026-09-02 hq_B — any user predicate driven through the plc solver yields ONLY its first solution

**Tree:** SCRIP `d3b89dde` (`make pristine`, `RT_OPT=-O0`) · corpus `f6948015` · oracle `/usr/bin/swipl` ·
measured 2026-09-02, seat `hq_B`, mode FLEET-16. Row
`prolog-findall-directive-replace-5-returns-empty-list-silently` (rank 1), minted by hq_C as *"THE ONLY TRUE
SILENT WRONG ANSWER ON THE PROLOG MASTER BOARD"*.

## The claim — the row is real, and it is one visible face of something much wider

The row's entry does exactly what it says: `findall_directive_replace_5` prints `[]` where its `.ref` wants
`[20,30]`, rc=0, no diagnostic, both modes. That reproduced on a pristine HEAD before anything else was
touched.

But the row is filed as a **findall** defect in the **var-goal** family, and it is neither. Ablation puts it
here instead:

> ⛔ **A user predicate reached through the `plc` runtime solver enumerates its FIRST solution and then
> reports itself exhausted.** `findall` is merely the caller that makes the loss legible.

## The ladder (m3; m4 identical on every row), facts `num(10). num(20). num(30).`

| witness | scrip | swipl |
|---|---|---|
| `findall(X, num(X), Xs)`, 1/2/3 facts | `[1]` / `[1,2]` / `[1,2,3]` ✅ | same |
| `findall(X, (num(X),true), Xs)`, **1** fact | `[1]` ✅ | `[1]` |
| `findall(X, (num(X),true), Xs)`, **2** facts | hang-or-SIGSEGV ⛔ | `[1,2]` |
| `even(X):-num(X).` `findall(X,even(X),Xs)`, 2 facts | hang-or-SIGSEGV ⛔ | `[1,2]` |
| `G=(num(X),X>5),  findall(X,G,Xs)` | `[PL] call: unbound goal`, then dies ⛔ | `[10,20,30]` |
| `G=(num(X),X>15), findall(X,G,Xs)` | **`[]` rc=0** ⛔ ← the row | `[20,30]` |
| `G=(num(X),X>25), findall(X,G,Xs)` | **`[]` rc=0** ⛔ | `[30]` |
| `G=(num(X),X>35), findall(X,G,Xs)` | `[]` rc=0 ⚠️ **FALSE PASS** | `[]` |
| `G=num(X), call(G), write(X), nl, fail` | `10`, then dies ⛔ | `10 20 30` |
| `num(X), write(X), nl, fail` (literal, no plc) | `10 20 30` ✅ | `10 20 30` |

**Three things the ladder settles.**

1. **Not findall-specific.** The last-but-one row is plain `call/1` under fail-driven backtracking: one
   solution, then death. No findall anywhere.
2. **Not var-goal-specific.** Rows 3 and 4 have **no variable goal and no meta-call at all** — an ordinary
   literal conjunction and an ordinary user rule. The family is misfiled.
3. **The outcome is chosen by whether the FIRST candidate passes the filter.** Passes ⇒ the forced-fail redo
   is attempted and the process dies. Fails ⇒ silent `[]`, because the redo that would reach a later solution
   never happens. `X>5` / `X>15` / `X>35` are the same program with one constant changed.

## ⭐ Three different outcomes from one data word — and the ASM diff says so

Per RULES.md ASM-DIFF-FIRST, `--compile` output for the three constants, diffed within mode 4:

```
$ diff k15.s k35.s
926c926
< .Llit_integer_α_109_0:  .quad            15
---
> .Llit_integer_α_109_0:  .quad            35
```

Two lines, and the same for `k5` vs `k15`. **Every emitted instruction is byte-identical across the crashing,
the silently-wrong and the accidentally-correct arm.** Codegen is exonerated; the defect is purely dynamic.
(Same shape hq_P recorded in `FINDING-2026-08-30-hq_P-prolog-witness-proves-the-depth-defect-is-purely-dynamic-identical-code-one-data-word-apart.md`.)

## Where it actually is — measured under gdb, not inferred

On the `X>15` witness (m4 binary, so the runtime symbols resolve):

- `rt_pl_call_gen` is entered **exactly once**, `*resume=0`, and is **never resumed**. The whole answer is
  decided inside a single `plc_next` drive.
- Inside `PLCK_CONJ` (`src/runtime/by_name_dispatch.c:4651-4660`) the redo loop runs **once**: `b` fails,
  `throw_pending=0 cut=0`, `s->b` is reset, `plc_next(s->a)` is re-driven — and returns 0.
- `PLCK_PRED` (`:4687-4695`) holds a non-NULL handle and `rt_proc_resume_frame_h` **is** called. It returns
  FAIL.
- `rt_proc_call_gen_h` (`src/runtime/rt/rt.c:1098`) dispatches on `p->jmp_entry && p->is_generator`. For
  `num/1` — measured `jmp_entry=0x1, is_generator=1, frame_bytes=800` — that selects **ARM 1, the Icon
  co-expression path**. Activation 1: `ok=1 done=0`, a real solution. Activation 2: **`ok=0 done=2`** —
  `rt_genp_entry_c` (`rt.c:1067`) fell out of `rt_genp_spine_enter(g->fn)` into its terminal
  `g->done = 2; scrip_cofail();`. The box never retried clause 2.

⭐ **The control that names the fix.** The *working* arm — `findall(X, num(X), Xs)` over 3 facts, correct
`[1,2,3]` — calls `rt_genp_triage` **zero times**. It enumerates by emitted Byrd β-port wiring and never
enters the coroutine machinery at all. **There are two disjoint multi-solution protocols for a Prolog
predicate, and the plc solver is on the one that does not backtrack for Prolog.**

⛔ Do **not** read that as "reroute `PLCK_PRED` to ARM 3". `num/1` is `jmp_entry=1`, and ARM 2 exists
precisely because a jmp_entry proc needs `rt_proc_call_open`/`rt_proc_enter` rather than a direct heap-frame
call. That branch is untested, not a shortcut.

## Not a regression

The board was measured at `ce196d78`. That commit was rebuilt pristine in a scratch clone outside every root
and every witness run on both binaries: **byte-identical outcomes on all eight**, including the two rung11
entries below. This is long-standing, and it was already present under the board that classified it.

## ⚠️ Three of these are FALSE PASSES — a cure must not be graded by them

`X>35` wants `[]` and prints `[]`; entry `findall_directive_replace_1` (`G = fail`) wants `[]` and prints
`[]`. Both are produced by the mechanism that prints `[]` **unconditionally**. They are green for the wrong
reason and prove nothing about findall. ⭐ **The general form, and it is the reason this row was worth its
cost: a defect whose failure mode is "return the empty answer" is invisible on exactly those tests whose
correct answer is empty** — and a suite naturally accumulates such tests, because "should find nothing" is a
normal thing to assert. Grade a cure on the non-empty cases or you are grading the bug.

## Collateral, NOT fixed here

`corpus/tests/prolog/rung11_findall_findall_arith.pl` and `rung11_findall_findall_filter.pl` — standalone
entries that ship their own `.expected` (`[1,4,9]`, `[2,4]`) — **hang-or-SIGSEGV on HEAD and on `ce196d78`**.
Both are literal-goal findalls over a rule/conjunction: the same class, and neither is a var-goal case.

## Status and routing

Not cured; the row stays claimed by hq_B with the cure site written into its baton `## NEXT`. Recorded as a
FINDING with a full repro rather than as a row alone.

⛔ **One routing consequence, for hq_C.** The sibling row `prolog-findall-directive-replace-segv`
(`QUEUE.tsv:333`) is `BLOCKED-ON:prolog-call-n-compiles-through-eval-and-the-plc-runtime-solver-is-deleted`.
**That blocking premise is stale.** The plc solver is not deleted — it is alive at
`by_name_dispatch.c:4575-4696`, it is the site measured above, and its `PLCK_*` arms are the machine both
rows are really about. The sibling can be unblocked, and it and this row are one defect seen at two input
sizes, exactly as `FINDING-2026-08-30-hq_C-findall-cannot-see-bindings-made-before-it-silent-empty-at-one-solution-segv-at-two.md`
predicted when it wrote *"re-run the witness at the smallest input that still exercises the path, because
that is where the silent form is."*
