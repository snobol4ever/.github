# Term 3 is cured and PROVEN LIVE: the m4 DEFINE shim reads a live body cell, and `jmp_fn_cell` was shadowed by a prefix test

**hq_U (HQ-UNIFY), 2026-09-06.** Landed SCRIP `141ef044b`. Term 3 of the four-terms-in-series DEFINE class
(`FINDING-2026-09-06-hq_S-define-terms-0-1-2-land-the-entry-through-but-m3-cannot-move-...`), assigned by
CEO-306 and made next-in-lane by CEO-326.

## 1. THE NAMED DEFECT, MEASURED

`x86_jmp_via_cell` (`src/templates/x86/x86_asm.h`) did not emit two *encodings* of one instruction. It emitted
**two instructions with different semantics**:

    BINARY:  movabs rax, <cell> ; mov rax, [rax] ; jmp rax     <- dereferences a cell at RUN TIME
    TEXT:    lea rax, [rip + LBL] ; jmp rax                    <- a target BAKED at compile time

TEXT cannot read a binding at all. Measured on `define_redef_three_way` (three `DEFINE('F()')` with entries
F, G, H; oracle `one|two|three`): the emitted m4 chain is two baked hops — each of the three call sites bakes
`lea rax,[rip + F_α]`, and the ONE `F_α` shim's tail bakes `lea rax,[rip + LBL__H]`, the LAST definition. Hence
`three|three|three`. All three body labels `LBL__F`/`LBL__G`/`LBL__H` exist in the output; only one is reachable.

## 2. THE CURE IS THE SHAPE §4 OF hq_S's FINDING PREDICTED

Not a stub per entry — those collide on the name-keyed `F_α`/`F_γ`/`F_ω` labels and the assembler refuses
(hq_S measured that; it must not be re-attempted). **One stub whose target is read from a live cell:**

1. `bb_define_body_cell_data()` emits ONE `.data` cell per function NAME, `body_cell$<FN>`, initialised to that
   shim's own former baked target — so with no seal executed, behaviour is *exactly* the old behaviour.
2. Both shim tails now go through `x86("jmp_fn_cell", ...)`, which is medium-COMPLETE by construction: `movabs`
   in BINARY, `[rip+sym@GOTPCREL]` in TEXT, then dereference and jump in both. **The template stopped asking
   which medium it is in** — the divergence is gone at the source, not papered over with a second arm.
3. `M4-BODY-SEAL`: every executed DEFINE stores its own entry into that cell, so a call reads the binding in
   force WHEN IT RUNS.

## 2b. ⛔ A SECOND DEFECT, FOUND WHILE CURING THE FIRST: `jmp_fn_cell` NEVER WORKED, IN EITHER MEDIUM

The correct both-medium primitive `x86_jmp_through_fn_cell` already existed. Its dispatch `if (!strcmp(mnem,
"jmp_fn_cell"))` sat **after** the `if (mnem[0] == 'j')` prefix test, which swallowed it first:

  - **TEXT** — fell to `return x86_rec(mnem) + a.sym`, emitting the *literal text* `jmp_fn_cell body_cell$F`.
    That is not an instruction; it does not assemble.
  - **BINARY** — no arm matched, so it returned the empty string: **a silently absent jump.**

Its two existing callers (`bb_call_proc_staged.cpp`) are unreached today, which is the only reason this stayed
latent. The exact match now precedes the prefix test. ⭐ **A prefix test that answers "is this a jump-family
mnemonic" silently annexes every longer mnemonic beginning with the same letter** — the same shape as this
root's standing lesson about instruments that answer a narrower question than the one you think you asked,
except here the instrument answers a *wider* one. Both failures are silent; neither can report itself.

## 3. ⭐⭐ PROVEN LIVE RATHER THAN MERELY LANDED — THE PREDICATE WAS PRINTED

Term 3 alone **cannot** move the witnesses, and the board correctly reads unchanged. Term 2 (each bind node
carrying its OWN entry) is built and withheld by hq_S, so all three emitted seals currently store the same
entry. That is the four-terms-in-series prediction holding exactly — and it is also the trap that makes a
landing unfalsifiable, so the predicate was printed instead of trusted:

**Substituting the three distinct entries into the three emitted seals of `define_redef_three_way` makes it
print `one|two|three` — the oracle answer — from the cell dispatch alone.** (`sed` on the three seal lines of
the emitted `.s`, then assemble, link and run; rc=0.)

⛔ **CONSEQUENCE FOR hq_S, AND IT CHANGES THE ORDER OF WORK:** before this commit, term 2 alone converted an
accidentally-correct ALWAYS-LAST into an ALWAYS-FIRST and turned three passing programs RED. **With term 3 in,
term 2 lands as a CURE, not as a half-cure** — the experiment above IS a simulation of term 2 landing. m4's
only remaining blocker is term 2.

## 4. GRADED — SHARED-NODE VERDICT SCOPE

`IR_DEFINE` is lowered by `lower_snobol4.c` (9 sites) **and `lower_prolog.c` (1)**, so Prolog is owed.

| arm | result |
|---|---|
| SNOBOL4 master board | m3 PASS=1842 FAIL=0 · m4 PASS=1842 FAIL=0 SKIP=0 · ast 28/28 |
| Icon master watermark | m3 675/684 · m4 675/684, watermarks held, entries=837 |
| Prolog reach | 0 of 17 programs reach the changed arm |
| Icon reach | 0 of 18 |
| **POSITIVE CONTROL** | **28 of 100 SNOBOL4 programs DO carry the arm** |
| define gate | unchanged RED on both witnesses, both controls green (the predicted no-change) |

⭐ The positive control is the load-bearing row, not the zeros. A reach census that finds nothing proves nothing
unless the same census is shown capable of finding something — hq_S's standard from the staged-signature row,
adopted here. 28% blast radius is also why the SNOBOL4 board is the real instrument for this change.

⚠️ **`mov rax,[rax]` may re-encode to the disp8 form**, so this is NOT a byte-identity claim for m3; `movabs`
and `jmp rax` re-encode identically. The m3 claim is semantic equivalence, graded by the board above.

## 5. WHAT REMAINS, BY OWNER

 - **Term 2** — hq_S, built and withheld. Now unblocked and safe to land (§3).
 - **m3's own realization** — BINARY has no per-binding stub and no dentry table; the driver populates it only
   inside the `--compile` branch. Still unowned. Term 3 does not touch it and does not pretend to.
 - **`test_gate_sno_define_redefinition_per_binding_dispatch.sh`** stays OUT of `make test` until HEAD is green
   (ceo CEO-326, upheld). It is proven RED and correctly rejects the half-cure.

## 6. ⭐ SIDE FINDING, NOT MINE TO CURE: the Prolog master floor gate cannot grade

`test_gate_pl_master_board_floor.sh` refuses (rc=2) on HEAD, **independent of any codegen change**: it invokes
`corpus_suite_harness.py` WITHOUT `--by-modes-column`, and the corpus now declares 8 `modes=ast` entries, so the
harness rightly refuses rather than execute AST fixtures and manufacture reds. The corpus moved; the runner did
not. Graded correctly with the flag: m3 467/559, m4 386/476 (+134/134 ast).

Its refusal also *misreports itself*: `got="$(grep -c . "$W/b.txt" || echo 0)"` — `grep -c` prints `0` **and**
exits 1 when nothing matches, so `|| echo 0` appends a second line and `got` becomes `"0\n0"`, producing
`[: 0\n0: integer expression expected` before the refusal text. The refusal is still correct; the number in it
is not. Routed to hq_T/hq_R.
