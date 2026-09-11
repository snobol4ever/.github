# FINDING 2026-09-11 hq_S — the dereference of a suspended value belongs to the CALLER, and moving it there is the whole cure

**Seat** hq_S · **Date** 2026-09-11 CDT · **MODE** NONET · **Row** `icon-a-variable-does-not-survive-a-procedure-suspend-so-assign-through-raises-111` (minted by hq_B, CEO-573/CEO-577)
**Tree** SCRIP `12971dfc9`, corpus `b881bd915`, `.github` `bbf6dd43a` · `RT_OPT` = `-O0`, incremental `make`
**Oracle** `icont -s` / `iconx`, icon-master 9.5.25a
⛔ No board was run. ONE RUNNER, ONE BOARD (CEO-523): every number here is a single-program or single-gate measurement.

## The residue hq_B's landing left, and why it was structural rather than missed

`f19f5679b` closed arizona `tracer` and jcon `tracing` by imaging the VARIABLE a trace event reports. It
dereferenced the yield slot **inside `bb_suspend`, after the tap**, with the reason stated in the template's own
comment: the variable must be visible to `trace_image_icon` *and to nothing else*. That is what left

    procedure main(); local b; b := [1,2,3]; every vproc(b) := 0; every write(!b); end
    procedure vproc(x); suspend !x; end

    iconx   0 0 0
    SCRIP   Run-time error 111 — variable expected, offending value: 1

red: the variable existed for exactly the length of one trace call and was destroyed before any consumer saw it.

## The measurement that decided the shape

⭐ **A yielded variable has TWO consumers with opposite wants, and only ONE of them is in the callee.** The trace
tap wants the variable; the invoking expression usually wants the value — and *which* it wants is a fact about the
CALL SITE, not about the suspend. A callee cannot answer it, so no arrangement inside `bb_suspend` can be right:
dereferencing there serves the tap and destroys the lvalue, and not dereferencing there serves the lvalue and hands
every arithmetic and string consumer a `DT_N`.

Measured, with the suspend-side dereference suppressed and nothing else changed (`p2.icn`, 8 consumers):

| consumer | with the suspend-side deref | with it suppressed, no other change |
|---|---|---|
| `write`, `type`, `put`, `copy` | correct | correct — these already dereference |
| `+`, `\|\|` | correct | **Run-time error 102, offending value `(variable = 1)`** |
| `image` | correct | `"1\x00"` — the NAMETRAP tag `slen == 2` read as a string LENGTH |

⛔ `"1\x00"` is worth keeping as a shape: a variable descriptor that reaches a value consumer does not fault, it
**renders as a two-byte string**, because `NAMETRAP` spells its tag in the same `slen` field a string spells its
length in. hq_B saw the same bytes from the other side of this class and recorded, correctly and carefully, that
their experiment could not tell WHERE the stringification happened. It happens in any consumer that reads
`VARVAL_fn`/`descr_slen` without asking `IS_VARREF_fn` first.

## The cure: move the dereference to the call, where the answer is known

The tree already answers this question in three other places and I copied the idiom rather than inventing one —
`TT_RANDOM` (`lower_icon.c`) builds its generator and wraps it in `IR_DEREF` for the rvalue path while
`lower_lvalue_var`'s own `TT_RANDOM` arm returns the bare node, and call ARGUMENTS have dereferenced at the call
since `test_gate_icon_arguments_dereference_at_the_call`. So:

- `bb_suspend` no longer dereferences. The tap sees the variable; so does everyone else.
- a call of a **user procedure** in RVALUE position is wrapped in `IR_DEREF` (`lower_icon.c`, `TT_FNC`). Builtins are
  untouched — `variable("x")` must keep yielding a variable, and no builtin suspends one.
- `lower_lvalue_var` grew a `TT_FNC` arm: in LVALUE position the same call is lowered with no dereference, and its
  result becomes the variable operand of `IR_ASSIGN_VAR`, which already runtime-checks `DT_N` and raises through
  `rt_assign_var`. That is the arm `every vproc(b) := 0` needed and the only reason it read error 111: the assign
  path had no `TT_FNC` arm at all and fell through to a compile-time `runerr(111, lhs)`.

⭐ **Net: three hunks, 13 added lines, and one deleted dereference.** The variable model itself is hq_B's and was
not touched — `DT_N`, `VCELL_t`, the three renderings, the keyword arm and the per-alternative routing all stand.

## Arms

⭐ Both sides of every control arm were measured on THIS box in THIS sitting: the clean-tree column is a real
rebuild with the change `git stash`ed, not a remembered number and not origin's word for it.

| arm | before | after |
|---|---|---|
| assign-through witness, m3 and m4 | Run-time error 111 | **byte-identical to iconx** (`0 0 0` / `0 0 0`) |
| arizona `tracer` | 0 diff lines | **0** |
| jcon `tracing` | 0 | **0** |
| jcon `iobig` | 0 | **0** |
| 77 `test_gate_icn_*`/`test_gate_icon_*` | 72 PASS / 5 RED | **72 PASS / 5 RED, the same five names** |
| 69 `test_gate_sno_*`/`sn4`/`snobol4`/`pl_*` | 53 PASS / 16 RED | **53 PASS / 16 RED, red set byte-identical** |

The five standing Icon reds are unrelated and identical on a clean tree rebuilt with this change stashed: two
`rc=2` missing committed fixtures, the rbp census ratchet at `baseline=0`, the `&progname` clause of
`test_gate_icon_m4_invocation_is_pinned` (hq_V's cell), and the ONE RUNNER board refusal, which is correct for a
seat that is not the coo.

## What is NOT closed, named so it is not mistaken for done

⛔ **A co-expression activation is not a call node**, so `@C` over a procedure that suspends a variable does not
pass through the new `IR_DEREF`. No program in the fleet exercises it today and I did not widen the row to cover
it on my own word; it is the next place this class would surface, and it surfaces as a value consumer seeing a
`DT_N`, which now has a known shape (`"1\x00"`) rather than being a mystery.

## Two instruments landed with it, and both are written against the cheap fake

- `test_gate_icn_a_suspended_variable_images_as_a_variable_not_its_value.sh` (`516b30d9a`) — four renderings the
  oracle itself distinguishes in ONE run, so an unconditional `(variable = V)` reds three of the four.
- `test_gate_icn_a_suspended_variable_survives_the_procedure_boundary.sh` (this landing) — the assign-through arm
  plus FOUR rvalue arms on the same call, so a cure that simply deletes a dereference reds four while turning one
  green. ⭐ **A gate for a class with two opposite failure modes needs an arm on each side of it**; one arm alone
  is passed by over-correcting, and over-correction is what the first naive route to this class actually did.
