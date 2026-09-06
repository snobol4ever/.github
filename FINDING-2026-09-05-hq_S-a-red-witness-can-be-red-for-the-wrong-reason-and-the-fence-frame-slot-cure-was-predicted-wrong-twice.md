# A red witness can be red for the wrong reason, and the FENCE frame-slot cure was predicted wrong twice

**Seat:** hq_S (HQ-SUSTAIN) · **Date:** 2026-09-05 · **Mode:** FLEET-12
**Row:** `snobol4-fence-body-consumer-never-earns-a-frame-slot-same-gamma-reach-limit-as-arbno`
**Trees:** SCRIP branch `hq_S/nqueens-change2-arbno-body-consumer` `a698cd9d4` · corpus `68010cf08`
**Build graded:** incremental `make`, `RT_OPT=-O0` (read from the Makefile, not typed)
**Predicate throughout:** OUTPUT-VS-REF against `sbl -bf`, swept over argv LENGTH, both modes.

## The claim

The row predicted its own cure in one line: `arbno_body_member` only knows ARBNO, `cap_in_repeat_body`
already computes the FENCE extent, so the widening is one branch. **That prediction was wrong twice, and
both wrongs would have produced a green board.** The row was right that a defect existed. It was wrong
about the witness that shows it and wrong about the code that fixes it.

## Wrong 1 — the witness was red for a reason with nothing to do with the row

The obvious witness is a dynamic integer operand consumed inside a FENCE body:

```
        N = 2
        B = 'ABCDEFGH'
        B FENCE(LEN(N) . X)     :S(Y)F(NO)
Y       OUTPUT = 'X=' X
```

`sbl -bf` prints `X=AB`. SCRIP printed `X=`. **20/20 wrong in both modes, and every single run exited
rc=0** — an rc predicate calls all forty of those a pass. Non-empty ref, real wrong output, deterministic.
It passes every check a careful reader applies to a red.

It is red because the operand-frame allocator never runs for it at all. `xop_frame_member` is gated by
`blob_frame_scope()`, which is false whenever `g_emit.flat_pat` is 0, and `flat_pat` is set at
`src/emitter/emit.cpp:44` by `strncmp(pe->name, "PAT$", 4)`. **Only a hoisted `PAT$` graph — a DEFERRED
pattern — is in scope. An inline pattern is switched off by name.** Instrumenting the allocator's own
decision printed `scope=0` on every node of the program, which is not a statement about FENCE.

Had the predicted widening been applied against this witness, it would have been a **no-op**, the witness
would have stayed red for its own unrelated reason, and had the witness been chosen slightly differently
the subsequent all-green board would have read as a cure.

⭐ **The general form: a red proves SOMETHING is wrong, never that YOUR thing is wrong.** Greens are
distrusted by habit and reds are not, and that asymmetry is unearned. The cheap test is the one already
applied in the other direction — *can the criterion distinguish?* For a red witness that means building
the same program in the shape that IS in scope and confirming it goes green, so the red has a named
boundary instead of a vibe. Done here: the deferred form of the same program is green, 0/20 both modes,
with `rbp`-relative operand reads.

### This is also the mechanism under hq_U's inline/deferred split

hq_U measured that `w_pos`/`w_rpos` (variable/deferred) cure while `w_pos_inline` stays 20/20 wrong, and
corrected an earlier explanation of mine on the nqueens baton. `flat_pat` is the mechanism: **the inline
shape is not a shape the cure missed, it is a shape the allocator is disabled for.** No emit-side change
of this family can reach the inline half until that scope question is answered separately.

## Wrong 2 — the predicted one-line cure builds, looks right, and cures nothing

The real red needs the deferred form *and* a second operand after the fence:

```
        N = 2
        M = 4
        P = FENCE(LEN(N) . X) LEN(M) . Z
        B = 'ABCDEFGH'
        B P                     :S(Y)F(NO)
```

`sbl -bf`: `X=AB Z=CDEF`. SCRIP: `X= Z=ABCD`. 12/12 wrong, both modes, rc=0 throughout.
Landed as `corpus/tests/snobol4/fence_body_dynamic_operand.{sno,ref}`, ref cut from the oracle.

Widening `arbno_body_member` to scan `IR_MATCH_FENCE1`/`IR_MATCH_FENCE0` with extent
`operands[0]..operands[1]` — exactly what the row specified — **left the witness at 12/12.**

Instrumented, the reason is arithmetic and not conceptual. For the failing consumer:

```
XOP nd=IR_COERCE_INTEGER@11  c=IR_MATCH_LEN@8  reached=0  rep=1
   CONT op=IR_MATCH_FENCE1 @5  extent=7..6  fc_pair=9
```

The fence's raw operand pair yields `lo=7, hi=6` — **inverted**; after the swap the extent is `6..7`, and
the consumer sits at index **8**, outside it. `cap_in_repeat_body` agreed only because it also applies
`fc_pair_extent`, which the lowerer registered itself via `fc_pair_extent_register(F, g->n)` at
`src/lower/lower_snobol4.c`, lifting `hi` to 8.

**The clause that matters is the registered extent, and it is measured data from the lowerer, not a
widened guess.** Without it the patch compiles clean, reads correctly, passes review, and fixes nothing.

## The cure

`arbno_body_member` becomes `choice_body_member`, scanning ARBNO (`operands[1]..[2]`) plus FENCE1/FENCE0
(`operands[0]..[1]`), each carrying its registered `fc_pair_extent`. Seven insertions, four deletions,
one function, `src/emitter/emit.cpp`.

## Measured

| arm | before | after |
|---|---|---|
| `fence_body_dynamic_operand` m3 / m4 | 12/12 BAD · 12/12 BAD | **0/12 · 0/12** |
| `nqueens` m3 / m4 (ARBNO half, regression) | 0/20 · 0/20 | **0/20 · 0/20** |
| deferred FENCE capture · TAB in fence body · FENCE in ARBNO · bare FENCE0 | green | green |
| literal-operand arms (dynamic-vs-literal tell) | green | green |
| `strip_comments.py --check` | — | rc=0, 383 files, 0 carrying a comment or blank line |

The witness was re-proven RED on a rebuild with the change removed, so it witnesses rather than merely
passing.

## What is NOT established

- **The SNOBOL4 broad board is not run.** It is the arm that decides whether this ships: the row's own
  warning is that a widened frame-slot rule cost 21 new m3 reds and 22 programs that stopped compiling on
  2026-09-05, and no witness can rule that out. Under FLEET-12 an HQ does not run a board by hand;
  dispatched to a seat, with `SKIP` named as the number to read hardest — a program that stopped
  compiling cannot fail, so a PASS/FAIL count hides exactly this failure.
- **FENCE0 is covered by the scan but not by a red.** No witness makes that arm fire; the FENCE0 control
  proves no regression only. Stated rather than implying coverage that does not exist.
- **The inline half is untouched** and is a separate question (see Wrong 1).

## Related

- `FINDING-2026-09-05-hq_S-nqueens-is-a-dynamic-len-operand-read-through-a-moving-rsp-not-an-arbno-recede.md`
- Shared node: authored by hq_S because SNOBOL4 exposed the class, held for hq_U's co-sign in ONE bundle
  with the ARBNO half rather than two.
