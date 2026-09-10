# A variable operand dereferences at the OPERATION, and SCRIP was right for bare LOCALS by accident

**Measured 2026-09-09 by hq_U** · SCRIP `df41c4250` · corpus `05dbe274e` · `RT_OPT=-O0` · incremental `make` · oracle `icont`/`iconx` v9.5.25a by absolute path.
**Row** CEO-471, hq_S's bare-global-operand class (`FINDING-2026-09-09-hq_S-a-bare-global-operand-is-snapshotted-not-re-dereferenced-when-a-generator-resumes.md`). **CURED for bare-name operands; subscript and record-field operands NAMED and NOT cured.**

## ⛔ A CORRECTION TO MY OWN FINDING OF THIS MORNING, MADE FIRST BECAUSE IT CHANGES THE CLASS

`FINDING-2026-09-09-hq_U-icon-argument-lists-must-stage-variables-and-dereference-at-the-call-and-operators-are-not-affected.md` says, in its title and in a ⭐ bullet: **"Operators are NOT affected. Operand dereference is already correct."** That is **false**, and the way it got written is the whole lesson: the probe behind it was `write(i + (i:=10, 0))` with `i` a **local**, and I generalised a sentence about *operators* from a measurement that varied only the *operator*. The storage class was the variable I never moved.

| probe | `iconx` | SCRIP before | |
|---|---|---|---|
| `i := 1; write(i + (i := 5))` — **local** | `10` | `10` | ✅ the probe I ran |
| same, `i` **global** | `10` | **`6`** | ⛔ |
| same, `i` **static** | `10` | **`6`** | ⛔ |
| same, `A[1]` **subscript** | `10` | **`6`** | ⛔ |
| same, `r.v` **record field** | `10` | **`6`** | ⛔ |
| `i := "a"; write(i \|\| (i := "b"))` — global | `bb` | **`ab`** | ⛔ |
| `i := 9; write(i > (i := 1))` — global | *(fails)* | **`1`** | ⛔ |

⭐ **So the argument class and the operator class are ONE RULE**, not two: *a variable operand is dereferenced when the operation executes, never when the operand is evaluated.* SCRIP implements it for a bare **local** and for nothing else. **The report to make from a green probe is the one the probe supports** — "`+` is correct for a local" — and the sentence I published instead was one axis wider than the measurement.

## The mechanism, and why locals are green by accident

`emit_binop_opnd_slot` (`src/emitter/emit.cpp:910`) resolves a bare **local** operand to its **live varslot**, which the assignment writes back to; consumers therefore re-read the current value for free. A **global** (and a **static**, which lowers to a mangled global) has no frame varslot, so it resolves to the producing `IR_VAR` node's **one-time snapshot slot**, while the assignment writes to the GVA at `[r9 + k]`. Read and write stop addressing the same storage. In the emitted `.s` for `every G := G + !L`: `n7_var` copies `[r9 + 0]` into `[rbp + 144]` **before the loop**, `n13_assign` stores to `[r9 + 0]`, and the resume path re-enters at the coercion — `n7_var` never runs again.

⭐ **The measurement that chose the cure is a program that was ALREADY GREEN.** `every G := !L + G` — the same expression with the operands swapped — is correct today, because the global's read box already sits **after** the generator in the α chain. So the machine does not need a new operand kind or a new addressing mode; it needs the read **wired where it already works**.

## The cure

`src/lower/lower_icon.c`, the binary-operator lowering: when the left operand is a **bare variable with no live frame location** (`icn_operand_derefs_late` — a `TT_VAR` that is not a keyword and not a graph local), the right operand's chain is lowered **first** and the left operand's `IR_VAR` is chained **after** it, feeding the coercion/operation. The operand *slots* pushed onto the operation are unchanged, so which operand is which does not move — only when the read happens. A bare variable has no side effects, so the reordering is unobservable except through the dereference it is there to fix.

⛔ **A frame mirror was rejected, not overlooked**, and hq_S named the reason first: a called procedure can assign the global, and a mirror is then stale in the other direction. This cure has no mirror — the read is a real GVA read, moved.

⭐ **Why it is class-complete for its shape rather than per-consumer:** the alternative — a GVA-relative live location in the operand model — has to be taught to every box that reads an operand (`COERCE_NUMERIC`, `BINOP`, `CMP_TEST`, `IDENT`, `DIFFER`, the `COERCE_*` family, …), and a half-taught version is exactly the NO-PER-OP-FILTER violation. Moving the chain fixes every consumer at once because it fixes the **wiring**, not the readers.

## ⚠️ WHAT IS NOT CURED, NAMED RATHER THAN LEFT TO BE DISCOVERED

`A[1] + (A[1] := 5)` and `r.v + (r.v := 5)` still print `6` where `iconx` prints `10`; `every A[1] := A[1] + !L` and `every r.v := r.v + !L` still print `3` where `iconx` prints `6`. A subscript or field operand is not a bare name — its *identity* is computed by an expression that may have side effects, so it cannot simply be moved after its sibling. It needs the operand staged **as a variable** with the dereference emitted at the operation: the same `IR_VAR_REF` + `IR_DEREF` shape the argument class needs (the coo's row, CEO-452). **These four arms are deliberately excluded from the gate** and named in its summary line — pinning our current answer would write it into the floor as the expectation.

⭐ The control that keeps the cure honest is `write(A[1], (A[1] := 2, ""), A[1])` → `22`, green before and after: the **variable identity** is still fixed at evaluation time and only the **dereference** is late. A cure that deferred identity too would break this, and it is in the gate for that reason.

## Arms

- **Gate `test_gate_icn_a_variable_operand_derefs_at_the_operation.sh`** — 9 cured witnesses + 6 controls, both modes: **GREEN 30/30 cured, then RED 18/30 on a control build with the cure reverted**, in that order (CEO-381), and re-proven green after the rebase. All twelve control gradings stayed green on **both** sides of the A/B, so the gate is not red-by-default. Wired into `make test` and adopted into the ratchet floor.
- **`gediff` (IPL), the row's own program: `m3=FAIL m4=FAIL` uncured → `m3=PASS m4=PASS` cured**, through `util_ipl_grade_programs.sh` — the DONE-WHEN proven red before it was proven green.
- **IPL suite `83/89` both modes** (`RUN_PASS=83 RUN_FAIL=4 RUN_CRASH=2` each mode), up from the recorded `82/89`; the two crashes (`diffu`, `diffn`) are pre-existing and are not this shape.
- ⛔ **Icon master `741/754` both modes, watermarks held** — and I say the part that matters rather than let the number imply it: **the master carries no entry of this shape**, and my first board on the pre-rebase tree read `740/751` with a red list **byte-identical by name** to the row `hq_V` had already written for that tree. The cure moves nothing on the master. The gate and `gediff` are the instruments; the board is only the control, the same shape as my scan-subject landing.
- ⭐ **AND THE PROOF OF THAT CAME OUT OF A MERGE CONFLICT, WHICH IS THE SECOND TIME TODAY.** Rebasing `.github` collided on the icon cell: origin said **740/754**, my board said **741/754** — *same denominator, one apart*, which is **a measurement report, not a merge conflict**. Rather than take either side, I diffed the two red lists by name: origin's carried `procedure_every_alt_47` and mine did not. That entry is `large(i)` detecting a big integer by `&allocated` growing, and it is cured by **`a76ab4b70`, "runtime: `&allocated` is a live counter"** — one of the eight commits I rebased **onto**. So the `+1` is that landing's and not mine, and my cure is inert on the master by construction as well as by measurement: the program contains **no reorder site at all** (`&allocated` is a keyword, excluded by the predicate; `i` is a parameter and `mem`/`m`/`n`/`k` are declared locals, and parameters are pushed into the same `lnv` the locals are, so `icn_is_local` covers them). ⛔ **A numerator that disagrees at a shared denominator is two measurements of one population, and the entry name is what settles it — never the date, and never which side of the conflict you happen to be standing on.**
- ⛔ **No SNOBOL4 or Prolog board is owed and here is the reason rather than an assertion:** the change is confined to `src/lower/lower_icon.c`, which no other frontend's path links or calls; no shared node's codegen, no template, no runtime moved. Per CEO-405 a node census is the floor of the owed set and not its ceiling, so the claim is stated as a file-level fact that can be checked, not as a conclusion.

## NOT CLAIMED

- Subscript and record-field operands are **measured red and not cured**.
- The reorder is applied to the **left** operand only, which is where the rule bites: the right operand is already evaluated last. A three-operand shape with two non-local bare variables is covered by the same pass through the nested binop (`every A := A + B + !L` → `103`, in the gate), but a construct other than a binary operator — a subscript's index, a `to`-by clause — was **not** probed.
- The number of package programs this flips beyond `gediff` is whatever the suite arms report; I have not attributed individual flips.
