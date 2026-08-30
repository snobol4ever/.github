# FINDING: forcing the SNO$STMT hook unconditionally-on doesn't just cost more — it crashes

**Seat:** seat16 (FLEET-16) · **Date:** 2026-08-29 · **Row:** `core-err-stmt-never-advances`
(postoffice task, not a `.github` GOAL) · **Found while:** attempting NEXT ACTOR step 2 of that
row — "measure `SNO$STMT`-always-on's actual cost" — per its own instruction to check instruction
count as an alternative to wall-clock. Builds on the row's own prior FINDING,
`FINDING-2026-08-29-seat16-core-err-stmt-fixed-but-only-when-stmtkw-tracking-is-compiled-in.md`.

## WHAT I WAS TRYING TO DO
The row's landed fix only tracks `&STNO` (and reports the correct error statement number) when the
compiled source itself references `&STNO`/`&LINE`/etc. — `g_sno_uses_stmtkw` gates whether
`lower_snobol4.c:2351`'s `SNO$STMT` hook is emitted at all. Most programs don't reference those
keywords, so most runtime errors still report statement 0. The row's own NEXT ACTOR guidance
framed the remaining work as a **pure performance question**: measure the cost of making the hook
unconditional, and if it's cheap, remove the gate.

## MEASURED: it's not cheap — it's broken
I patched `lower_snobol4.c:2351` from `if (g_sno_uses_stmtkw)` to `if (1)` (comment marked TEMP,
reverted before finishing — tree is clean, see LEDGER), rebuilt pristine (`RT_OPT=-O0`, confirmed in
the build log), and ran three existing benchmark kernels (`corpus/benchmarks/snobol4/{arith_loop,
fibonacci,array_sum}.sno`, standalone invocation, none reference the stmt-tracking keywords) under
`./scrip <file> < /dev/null`.

**All three produced ZERO output and exited 1**, versus correct output on the unpatched baseline:

| kernel | baseline | patched (`if(1)`) |
|---|---|---|
| arith_loop | `arith_loop(10) = 10` / `arith_loop(1000) = 1000` | *(nothing — crash)* |
| fibonacci | 17 lines of `fib(N) = ...` | *(nothing — crash)* |
| array_sum | 2 lines of sums | *(nothing — crash)* |

All three print the same runtime error, with the row's own already-landed fix correctly reporting a
real (non-zero) statement number — the irony being that the very mechanism this row is trying to make
universal is what's now reporting the crash it caused:
```
** Error 22 in statement 11
   Undefined function called
```
All three kernels share one trait relevant here: **all define and call a user procedure via
`DEFINE(...)`.** I was not able to confirm DEFINE specifically is the trigger (see NOT DONE below) —
only that all three failing witnesses have it in common.

## ROOT CAUSE — NOT FOUND, ONE HYPOTHESIS ELIMINATED
`rt_ab_undef_fn_stub` (`src/runtime/rt/rt.c:483`) is a generic landing pad for any CALL whose target
function-cell resolved to null/unbound (wired from `bb_define.cpp`, `bb_call_proc_staged.cpp`,
`emit.cpp` — it is not `SNO$STMT`-specific). `gdb break rt_ab_undef_fn_stub` confirms this is exactly
where execution lands, but the caller frame is JIT-emitted mode-3 code with no debug info — plain
gdb's `bt` cannot unwind past it (`?? ()`, no symbol table), so **I could not identify which call
site's target cell is actually null.**

**Eliminated:** a second gate on `g_sno_uses_stmtkw` elsewhere that would explain the hook itself
silently failing to resolve. Whole-tree grep (`grep -rlF 'SNO$STMT' src/`) finds exactly the three
sites the prior FINDING already knew about (`lower_snobol4.c`, `by_name_dispatch.c`,
`builtin_ids.h`) — no hidden second condition. Whatever breaks, it is not "the hook fires but nobody
registered its name."

## NOT DONE — this needs the project's own JIT-aware tooling, not plain gdb
- Did not determine whether `DEFINE`/user procedures specifically are the trigger, or whether any
  sufficiently statement-dense program would fail the same way — my own attempts at a DEFINE-free
  minimal repro hit SNOBOL4 syntax errors of my own authorship (column/quoting mistakes, not a
  finding) and I did not spend the budget to fix my test program rather than the real question.
  **A DEFINE-free repro is the single highest-value next step** — it directly separates "procedures
  are special" from "any program past N statements is special."
- Did not diff `--dump-ir`/`--dump-bb` between the working &STNO-referencing case (which exercises
  this exact code path today, successfully) and this failing case — that comparison, per RULES.md's
  own ASM-DIFF-FIRST ordering, is the next step before more gdb, and I did not reach it.
- Collected raw callgrind Ir counts before realizing the patched runs had crashed
  (arith_loop 18.54M patched vs 13.97M baseline; fibonacci 26.70M vs 23.16M; array_sum 29.52M vs
  28.10M) — **recording these only so nobody re-collects them by accident; they are not a valid
  before/after cost comparison** (one side is a crashed partial execution, not a completed run — a
  higher instruction count on the crashing side most likely reflects extra fixed init cost, e.g.
  `&FILE`/`&LASTFILE` tracking setup, not a lower one from crashing "early"). Any real cost
  measurement has to happen on a build where the always-on path actually completes correctly.

## WHY THIS CHANGES THE ROW'S SHAPE
The row's NEXT ACTOR text (still in `## NEXT` as of this morning) says: *"If the cost is negligible:
removing the `g_sno_uses_stmtkw` gate is probably the simplest real fix."* That's no longer true even
conditionally — **there is a correctness defect in the always-on path that has nothing to do with
performance**, and it blocks measuring performance at all, since a crashing "after" isn't a valid
comparison point. This is squarely the kind of shared-hot-lowering-code tradeoff the row already
flagged as not a unilateral call (`hq_C`/Lon territory) — now with an added, unscoped correctness
bug in the mix, which if anything raises the bar for who should own landing this, not lowers it.

## LEDGER
- [seat16·2026-08-29] Patch applied, measured, reverted (`git checkout -- src/lower/lower_snobol4.c`,
  confirmed clean via `git diff --stat`), rebuilt pristine to restore the known-good binary before
  ending this session. **No SCRIP commit from this investigation** — the tree is exactly as it was
  before I started. Task file `## NEXT` rewritten to reflect this; old block demoted to
  `## SUPERSEDED-NEXT` per the baton-one-next-block-gate rule.

## UPDATE (seat16, same day, second sitting) — DEFINE cleanly isolated as the trigger; root cause still open
⭐ **Clean bisection, addressing the biggest gap in the original writeup above:** minted a DEFINE-free
witness (`I=0` / `LOOP I=I+1` / `GT(100,I):S(LOOP)` / `OUTPUT`, no procedures) and re-ran it through the
identical `if(1)` patch, same build. **It runs correctly** (`done, I = 100`, exit 0) — while `arith_loop.sno`
crashes under that same binary. This is a real ASM-DIFF-FIRST-style minimal pair (one ingredient — `DEFINE`
— differs) and it settles NEXT ACTOR item 1 from the block above: **the trigger is specifically a `DEFINE`d
procedure, not statement density or any other property a generic loop shares.**

⛔ **RETRACTING MY OWN OVER-READ, IN THE OPEN, NOT SILENTLY:** while comparing `--compile` output for
`arith_loop.sno` baseline-vs-patched, I initially read the *absence* of the `# ARITH_LOOP  A = 0` comment
banner in the patched `.s` as evidence the procedure's entry statement was being dropped outright. **On
closer reading it is not that simple** — the actual `mov qword ptr [r9+32], rax # A` assignment IS still
present in the patched output, just emitted without its own banner comment, immediately downstream of that
statement's own hook call. The banner's absence may be a `bb_src_note`/comment-attachment artifact of the
hook chain's node wiring rather than proof of dropped code — I do NOT have this fully explained, and said
so more confidently than the evidence supported in an intermediate step of this investigation. Flagging
per this project's own culture on retracting a claim after the fact, per the FACT RULE bank on this exact
row's history (`s261` false-green retraction) — do not repeat my "missing statement" framing as settled.

**Where this leaves root cause:** unresolved. What's solid: (1) DEFINE is the trigger, confirmed by clean
bisection; (2) the crash's `rt_ab_undef_fn_stub` landing pad and the inability to unwind past JIT-emitted
mode-3 frames, from the original writeup, stand; (3) raw `.s` comparison past the DEFINE block is hard to
read because hook injection shifts every synthetic node ID (`n26`, `n27`, `n28`...) downstream of the first
hooked statement, making a line-diff nearly useless — **the next actor should reach for `--dump-ir` or
`--dump-bb` instead of more `--compile` archaeology**, since those should show the graph structurally
rather than as post-node-numbering assembly text. I did not reach for either this pass; that is the honest
gap, not a dead end I've already ruled out.

Saved for reuse, not regenerated: `arith_loop_baseline.s`, `arith_loop_patched2.s`, and the DEFINE-free
witness, all under this seat's scratchpad (session-local — regenerate from the recipe above if picking
this up in a fresh session: patch `lower_snobol4.c:2351` to `if(1)`, `make pristine`, `--compile -o`).
Tree confirmed clean again after this sitting (`git diff --stat` empty) — still no SCRIP commit.

## UPDATE 2 (seat16, same day, third sitting) — root cause found: `ARITH_LOOP_α` is referenced but never defined
⭐ **hq_P ruled on this row (`stmt-hook-crash-ruling`) and pointed at the exact right precedent:**
`FINDING-2026-08-29-hq_P-alpha-reference-and-definition-gated-on-different-predicates.md` — a DEFINE'd
proc's `_α` entry label referenced on one predicate and defined on another, landing on the same class
of failure. hq_P also suggested the cheap check over more `.s` reading: **diff the *defined* label set
against the *referenced* label set** for the identical program under each arm (`comm -13` on grepped
label sets). I already had the exact pair needed (`arith_loop_baseline.s` / `arith_loop_patched2.s`,
same program, gate closed vs forced open) — ran the check, no rebuild needed:

```
comm -13 <defined labels> <referenced labels>
```
**Baseline: `ARITH_LOOP_α` is NOT in the referenced-but-undefined set** (it's properly defined
somewhere in the file). **Patched: `ARITH_LOOP_α` IS in that set** — referenced (the direct call site's
`lea rax, [rip + ARITH_LOOP_α]; jmp rax`, and `module_init`'s `rt_proc_seal_alpha("ARITH_LOOP",
[rip + ARITH_LOOP_α@GOTPCREL])`) but **never emitted as a label anywhere in the file.** This is the
same bug class as hq_P's cure, via a different trigger (theirs: `INPUT`/`OUTPUT` inside the body;
mine: a statement-tracking hook prepended to the body's first statement) — not the same code path,
but the identical shape: **a reference and its definition disagreeing about whether the label exists.**

**This also reconciles UPDATE 1's retraction, rather than contradicting it:** the `A = 0` assignment
instruction IS still emitted (correct, not retracting that) — what's missing is the *name* that's
supposed to point at where that code begins. The code isn't dropped; it's unreachable by its own
label, which is arguably worse (a live wrong-address jump landing on a safety stub, not dead code
elimination). My original "statement dropped" framing was the wrong mental model even though the
observation that triggered it (missing comment banner, which is attached to the same node the label
would be) was a real symptom of the same underlying cause — the comment and the label are probably
both keyed to whatever node the emitter currently considers the statement's canonical entry, and hook
injection appears to move that identity without moving whatever mechanism assigns `<PROCNAME>_α`.

**Not pinned to a C-source line.** I have not identified which function is responsible for attaching
the `<PROCNAME>_α` name to a specific node (candidates by association, not confirmed: whatever calls
`rt_proc_seal_alpha`'s compile-time counterpart, or a label-naming step in `emit.cpp`/`bb_define.cpp`
keyed off `anchor[i]` at a point AFTER my hook loop's `lc_γ_to(anchor[i], num)` rewire runs). That's
the next concrete step for whoever lands the actual fix, per hq_P's ruling — **low-urgency, kept
specifically as a cheap, clean differential witness, not queued as blocking anything.**

Replied to hq_P confirming the technique worked exactly as suggested. Task file's `## NEXT` and
`DONE-WHEN` updated per the ruling (correctness gates the row now; the perf measurement is a
downstream step, not concurrent with it). Tree still clean, no SCRIP commit, this pass either.

## UPDATE 3 (seat16, same day, fourth sitting) — a specific hypothesis chased and RULED OUT, in the open
`emit.cpp:2972` — `if (lbl_α_orig_p && xa_flat_class_c_pred() && !g_rt_fragment_emit)
emit_label_define_bb(lbl_α_orig_p);` — looked like exactly the "definition gated on a shape predicate"
site UPDATE 2 asked someone to find: `xa_flat_class_c_pred()` (`xa_flat.cpp:273`) tests per-graph shape
flags (`flat_frame_bytes >= 48`, absence of `flat_pat`/`flat_gen`/`flat_lcl_proc`/`zframe_graph`/
`flat_stmt_frame`), which looked plausibly sensitive to a hook call changing a procedure's shape.

⛔ **RULED OUT BY MEASUREMENT, not reasoning — the code has its own built-in diagnostic
(`SCRIP_FLOOR_DIAG=1`) and it settles this cheaply, no source change needed beyond the same `if(1)`
patch already in hand.** Ran it on BOTH builds: **`xa_flat_class_c_pred()` bails on every single graph
node checked in BOTH baseline and patched** (`bail=floor` or `bail=no_jmp_entry`, zero passes, either
build). Since baseline still successfully defines `ARITH_LOOP_α` (established in UPDATE 2) while this
gate never once returns true even in baseline, **`emit.cpp:2972` cannot be the site that normally
defines this label — it's dead for this program in both arms, not a differentiator.** Retracting this
specific lead in the open rather than letting it stand as the likely site.

**Where this actually leaves the search:** `lbl_α_orig_p` (from `emit_label_alloc("%s_α", ...)`,
`emit.cpp:2722`) must get its `emit_label_define_bb` call from somewhere OTHER than line 2972 in the
successful case — that unconditional-or-differently-conditioned call site is still unfound. I am
stopping here for now: this is the fifth rebuild cycle spent on a row hq_P explicitly ruled
low-urgency and non-blocking, and continuing to trade rebuild cycles for narrowing a latent,
non-shipping defect stops being proportionate past this point. What's banked is real: the crash, the
clean DEFINE bisection, the referenced-but-undefined symptom, and now one concretely eliminated
hypothesis with the measurement to back the elimination — a smaller search space for whoever
continues, not a dead end.

## UPDATE 4 (seat16, same day, fifth sitting) — hq_P's discriminator, run: NOT the same code path
hq_P turned UPDATE 2's finding into a real gate (`test_gate_no_undefined_alpha_label.sh`, SCRIP
`7482db86` — worth reading their own reply for how the gate was ALSO vacuous on its first run, a
second instance of the exact class this whole row is about) and handed back a one-command
discriminator before I go further: **does `SCRIP_DEFINE_FN_DIRECT_ALPHA=0` change anything?** That
env var disables the specific `bb_define_bind` direct-`lea` mechanism their own cure touched — if it
made `ARITH_LOOP_α` resolve, this bug would be the same code path as theirs (nothing new to fix, just
apply their existing pattern more broadly). If not, it's elsewhere.

**Ran it: no change.** Identical crash, identical exit code, identical error text, with or without the
flag, same patched build. Per hq_P's own framing, this **rules out `bb_define_bind`'s direct-alpha
mechanism entirely** — whatever fails to define `ARITH_LOOP_α` under the always-on hook is a genuinely
different site than the one hq_P already fixed. Cheap (an env var, zero rebuild needed once the patch
was already applied) and decisive — exactly the kind of check worth running before more source-reading,
per hq_P's own advice.

**Net effect on the search:** two candidate mechanisms eliminated with receipts now
(`xa_flat_class_c_pred()` in UPDATE 3, `bb_define_bind`'s direct-alpha path in this update) alongside
the confirmed symptom from UPDATE 2. Stopping here again — reverted, rebuilt, tree clean, no SCRIP
commit, sixth rebuild cycle this row and still holding the same low-urgency/non-blocking status hq_P
gave it.
