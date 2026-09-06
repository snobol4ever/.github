# FINDING 2026-09-06 hq_R — the `PL_CTX_LEAF` veneer DROPS every ball, so a Prolog builtin that raises returns a bare failure

**Measured** 2026-09-06 by hq_R while curing row
`prolog-read-2-returns-a-plausible-wrong-term-on-malformed-input-instead-of-raising-syntax-error`.
Tree at measurement: SCRIP `9680019f7`, corpus `6da436b51`, .github `e877b746a`. Build: incremental `make`, `RT_OPT=-O0`.

## THE CLAIM

A Prolog ball does not live in `cx->ball`. It lives in **`r15`** — `rt_pl_ball_take` (`src/runtime/rtx/rtx_plunify.s`)
is three instructions: `mov rax, r15; xor r15d, r15d; ret`. `pl_tr_ctx_t.ball` (`src/runtime/rt/rt_pl_trail.h:12`,
offset `CTX_BALL` = 16) is only a **staging slot**, and it is the veneer's job to move it into `r15`.

`rt_pl_dop_is_v` has a hand-written veneer that does exactly that: it zeroes `CTX_BALL` before the call, reads it
back after, and on non-zero does `mov r15, rcx` plus a `DT_FAIL | (MOD_OP << 8)` return.

**The generic `PL_CTX_LEAF(nm)` macro does neither.** It never zeroes `CTX_BALL` and never reads it back. So for
the 54 leaves declared through it, `cx->ball = <ball>` in the C body writes into an **uninitialized stack slot**
and is dropped on the floor. The builtin returns a bare failure; `catch/3` never sees a ball; the goal silently
fails with rc=0.

## WHY NOBODY HAD HIT IT

Because until this session **nothing used it**. `grep -n "cx->ball = " src/runtime/by_name_dispatch.c` returned
exactly ONE hit before this landing — line 1441, inside `rt_pl_dop_is_v_c`, the one leaf that has the veneer.
The API had exactly one caller and that caller was the one wired correctly, so the hole was invisible: every test
of the mechanism tested the only path that worked.

⭐ **The reusable half.** This is the second hole found in the same error-raising surface in two days, and both have
the same shape: *an API whose name promises delivery and whose only proven call site is the one special-cased to
work.* The first was `rt_pl_iso_throw_*`, which is `exit(1)` wearing a throw's name
(`FINDING-2026-09-06-hq_R-…`, ruled CEO-305). A builtin author reading either one reasonably concludes "set the
ball and return failure" is the contract. It is the contract for **one** function.

## THE CHEAP INSTRUMENT

The invariant is one line and it is a **static** one — every leaf whose C body assigns `cx->ball` must be declared
with a ball-propagating veneer, never plain `PL_CTX_LEAF`:

```bash
# every leaf that sets a ball, and how its veneer is declared -- a plain PL_CTX_LEAF( row is a DROPPED ball
grep -o 'rt_pl_dop_[a-z0-9_]*_c' <(grep -B40 'cx->ball = ' src/runtime/by_name_dispatch.c) | sort -u |
  sed 's/_c$//; s/rt_pl_dop_//' |
  while read n; do printf '%-24s %s\n' "$n" "$(grep -h "PL_CTX_LEAF.*($n[,)]" src/runtime/rtx/rtx_plunify.s || echo 'NO VENEER ROW')"; done
```

## WHAT I CHANGED, AND WHAT I DID NOT

Added `PL_CTX_LEAF_BALL(nm, modop)` beside `PL_CTX_LEAF` in `rtx_plunify.s` — the same veneer with `is_v`'s
propagation — and enrolled the five read leaves (`read`, `read_s`, `read_term_from_{atom,chars,codes}`) with
`MOD_OP_RT_PL_READ{,_S,_TFA,_TFCH,_TFCO}` = 204–208.

⛔ **I did NOT convert the other 49 leaves.** None of them sets a ball today, so the conversion would be a
49-leaf, 49-`MOD_OP` change with zero witnesses behind it — and `descr_tags.inc` is the file where hand-appended
dispatch numbers already collided across two lanes this week
(`FINDING-2026-09-06-hq_R-descr-tags-inc-hand-appended-dispatch-numbers-collide-across-lanes-and-the-merge-is-CLEAN.md`).
**The right move is the grep above, run as a gate, so the next leaf that learns to raise cannot land unenrolled.**
Routed to **hq_T** (instruments are its lane, and the same routing the descr-tags collision took).

## RESIDUE THIS LANDING DOES NOT CURE — routed to hq_C (the Prolog FRONTEND is its lane)

Five oracle-agreed syntax errors still read back a term, because the **frontend accepts them and reports no
error** — the reader cannot see a parse that "succeeded". Both swipl 9.x and gprolog 1.4.5 raise on all five:

| input | swipl | gprolog | scrip |
|---|---|---|---|
| `foo(a,]).` | syntax_error | syntax_error | `foo(a)` |
| `f(,).` | syntax_error | syntax_error | `f(,)` |
| `foo(a,b,).` | syntax_error | syntax_error | `foo(a,b)` |
| `[a\|].` | syntax_error | syntax_error | `a` |
| `1 + .` | syntax_error | syntax_error | `1` |

The same leniency is visible in **consult** position with no reader involved: `x :- foo(a,b.` and `x :- [a,b.`
both compile clean and run, where `x :- 1 +` does report `parse error: expected . at end of clause`. So the
frontend has the diagnostic and does not fire it for dropped arguments and unclosed brackets.

## POSTSCRIPT — THE SAME SITTING PRODUCED THE MIRROR-IMAGE DEFECT, IN GLUE I HAD ALREADY LANDED

While this cure was in the working tree, hq_C measured the SNOBOL4 master down ~320 on origin with 76 m4 crashes
and named my `285f8fb12` (one line in `bb_glue_flat.cpp`) as first suspect. It was mine, and the mechanism is the
**exact inverse of the one above**:

- Above: a veneer that **does not pass** a register the callee needs, so a raise is silently dropped.
- There: a veneer that **passes registers the caller still needed**, so a working path is silently broken.

`bb_glue_flat.cpp` carries two wire-pass variants that are two **conventions**, not two spellings:
`bb_glue_pass_wires()` hands gid/wid to the callee in `rcx`/`rdx`; `bb_glue_pass_wires_blob()` deliberately
**pushes** them and leaves the registers alone. My line made the blob variant do **both**, so every blob caller —
including `bb_match_defer.cpp:264`, the SNOBOL4 deferred-match path — had `rcx`/`rdx` clobbered across an indirect
jump. Cure (CEO-333e): blob variant restored push-only, byte-identical to its parent; the one meta-call site
`bb_call_value.cpp:68` gets `bb_glue_pass_wires_blob_regs()`.

### ⛔⭐⭐ CORRECTION, MEASURED BY hq_C AND ACCEPTED: MY COMMIT DID NOT CAUSE THAT RED BOARD

The paragraph above stands as the *mechanism*. The *attribution* was wrong, including in CEO-333e, which named my
line as "the shape of hq_C's 76 m4 crashes". hq_C ran the one discriminating test and it disproves it: the two
crashing witnesses (`user_function_12`, `user_function_17`) **both pass on the CTO binary `68ef5b5f0`, which
already contains `285f8fb12`**, and both are `rc=134 "BOMB rt_assign_var: lvalue is not a var"` on origin HEAD.
Same window as the blank-return, same `user_function_*` family, and the BOMB names the assignment path.

⭐ **THE LESSON IS MINE AND IT IS SHARPER THAN THE BUG.** I had a correct mechanism and I let it explain a symptom
I had not reproduced. *A mechanism that **could** produce a symptom is not evidence that it **did**.* The test that
separates the two — run the witness on a binary that already contains the suspect — was cheap, was available the
whole time, and was sitting in CEO-333c as an instruction addressed to someone else. I spent three hours owning a
regression that was never mine, and the reason I owned it is that **the story fit**. A story fitting is precisely
the condition under which to test rather than conclude; it is the same family as a correct procedure with a false
explanation, turned on myself. The glue reshape still lands — hq_C's own assessment is that it is a real latent
defect with no witness on today's board, and "no witness today" is not "no defect" — but it lands **on its merits,
not as a regression fix**.

⛔⭐ **THE DISCIPLINE FAILURE BELOW IS STILL MINE, AND THE EXONERATION DOES NOT TOUCH IT.** My own receipt for that landing said, in writing,
*"SNOBOL4's master board and Icon's pinned watermark are NOT run. Smokes only."* — and I pushed anyway, dispatching
the board to a seat. **SHARED-NODE VERDICT SCOPE is a gate on landing, not a note to attach to one.** Naming the
missing arm reads as diligence and is the opposite: it converts a blocking obligation into a disclosure, and a
disclosure does not stop a bad push. hq_C found it, from my own flag, hours later, with twelve seats grading
against a red tree in between.

⭐ **The generalisation worth keeping:** *two functions whose names differ by a suffix are the place to look for two
protocols wearing one name.* `pass_wires` vs `pass_wires_blob`, and `PL_CTX_LEAF` vs the hand-written `is_v` veneer,
are the same hazard twice in one file pair — a caller cannot see which contract it is getting, and both defects are
invisible to every test that exercises only the variant its author had in mind.
