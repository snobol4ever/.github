# FINDING 2026-09-13 hq_S — a parameter declared only in a `forward` heading is invisible to field resolution, so its record fields read blank and assign nowhere

**Tree:** SCRIP `3d6fc82c6`, corpus `7205e4a47`, `.github` `b8f9c197a`. Build: incremental `make`, `RT_OPT=-O0`
(read from `Makefile`, not typed). Oracle: `fpc -Miso` 3.2.2 at `/usr/bin/fpc`. Measurer: hq_S.

## THE WITNESS — 13 lines, `fpc -Miso` compiles and runs it, we do not

```pascal
program v3;
type item = record typ: integer end;
var g: item;
procedure p(var x: item); forward;
procedure p;
  var y: item;
begin
  y.typ := 1;
  if x.typ = y.typ then writeln('eq') else writeln('ne')
end;
begin
  g.typ := 1; p(g)
end.
```

`fpc -Miso` → rc=0, prints `eq`. `scrip` → **rc=134 in BOTH modes**, `FATAL emit_drive: IR op=6 ... REFUSED AT A GUARD`.

## ⛔ THE LOUD HALF IS THE SMALL HALF — EVERY OTHER USE IS A SILENT WRONG ANSWER, rc=0

Only the **relop** use aborts. Narrowed by four one-line bodies over the same skeleton:

| body | scrip m4 | fpc |
|---|---|---|
| `writeln(x.typ)` | rc=0 | rc=0 |
| `x.typ := 2` | rc=0 | rc=0 |
| `if x.typ = 1 then writeln(1)` | **rc=134** | rc=0 |
| `writeln(1)` (control, never touches `x`) | rc=0 | rc=0 |

Graded for **output**, not exit status — which is where it turns bad. Body
`writeln(x.typ); x.typ := 9; writeln(x.typ)` with caller `g.typ := 4; p(g); writeln(g.typ)`:

```
fpc -Miso :  4 / 9 / 9
scrip m3  :  <blank> / <blank> / 4      rc=0
scrip m4  :  <blank> / <blank> / 4      rc=0
```

**The read prints an empty line instead of `4`; the assignment through the var parameter silently does
nothing, so the caller's record is unchanged; and the process exits 0.** ⭐ The crash is the case we are
lucky to get. Every other use of a forward-declared parameter's record field is a wrong answer with no
diagnostic and a successful exit — the shape that survives a green board.

## THE CHAIN, MEASURED — three layers, each of which looks innocent alone

1. **Parser.** `pas_arrrec_flatten` normally rewrites `base.field` into an indexed access
   (`src/parsers/pascal/pascal.tab.c:2721`); when it cannot resolve the field it falls back to a raw
   `bin(TT_FIELD, base, leaf_s(TT_VAR, fld))` (`:703`, and the `else` at `:2721`). A parameter declared
   **only in a `forward` heading** is not in scope for that resolution when the body — which under ISO 7185
   repeats the name and **no parameter list** — is parsed. So `x.typ` emits a raw `TT_FIELD`.
2. **Lowerer.** `lower()` in `src/lower/lower_pascal.c:506` has **no `case TT_FIELD`**. The node falls to
   `default:` at **`:571`**: `{ IR_t * s = build(cx, IR_GOTO, γ, γ); *res = s; return s; }` — it builds an
   `IR_GOTO` and **assigns it to `*res`, the node's VALUE**. A jump is handed back as an expression result.
3. **Emitter.** The `IR_GOTO` has no value slot, so `emit_binop_opnd_slot` returns `-1`,
   `src/emitter/emit.cpp:1616`'s `if (sa < 0 || sb < 0)` refuses, and `emit_drive` `abort()`s.

gdb at `lower_pascal.c:571`, conditional on the node kind, censuses exactly what reaches the arm on
`corpus/packages/pascal/p5/sample_programs/pascals.pas`:

```
  31  TT_SUCCEED (38), 0 children
   4  TT_FIELD  (113), base TT_VAR "x", field "typ"
```

and at `emit.cpp:1616`, conditional on `sa < 0 || sb < 0`:

```
REFUSED sa=-1 sb=2528
child0 = IR_GOTO,  n_operands=0
child1 = IR_CALL "arr_get"(VAR "y", LIT 0)     # i.e. y.typ, resolved correctly
```

⭐ **`y.typ` resolves and `x.typ` does not, in the same procedure, on the same record type.** `y` is an
ordinary local; `x` is the forward-declared parameter. That asymmetry is the whole defect, and it is why no
amount of staring at the record or the field finds it.

## ⛔⭐ THE `default:` ARM IS THE REAL DEFECT, NOT THE MISSING `TT_FIELD` CASE

A `default:` that turns *any* unhandled tree kind into a GOTO-used-as-a-value converts every future
front-end gap into either a wrong answer or an abort three layers away, with **no source location and a
message that actively misdirects**: `emit_drive` prints *"This is NOT a missing template: do NOT implement
op=6"* — correct about the emitter, and it sends the reader to `bb_binop_relop.cpp` when the cause is a
parser scope rule. 31 `TT_SUCCEED` nodes ride the same arm today and are harmless only by luck (a no-op
statement whose value nobody reads). The arm should **refuse by name** — print the unhandled `tree_e` and
the construct — rather than manufacture a value.

## ⛔⭐⭐ THE NUMBER IN THE OLD REPORT MOVED UNDER THE DEFECT — "op=5" AND "op=6" ARE THE SAME NODE

This is the defect the coo relayed to this seat as **`emit_drive` FATAL op=5**. It is **op=6** today, and
nothing about it changed. `src/ir/IR.h`'s op enum began `IR_ACTIVATE` (numbering from **0**) at the coo's
stage tree `aa4a139f4`; commit **`926628d49`** ("mint_op is ONE numbering from 1") re-based it to
`IR_ACTIVATE = 1`. Under the old numbering op=5 is `IR_BINOP_TEST`; under the new one op=5 is
`IR_BINOP_RELOP_VAL` and `IR_BINOP_TEST` is op=6.

⭐ **So a reader who carried "op=5" forward one day and greped today's tree lands on the wrong IR node and
diagnoses a different defect** — and the two are adjacent members of the same family, so the wrong answer
looks right. This is the project's own transcription doctrine with a new edge on it: it is not enough that a
number carry its tree, because **a positional identifier can change meaning while the thing it names does
not move at all**. A guard that prints `IR op=%d` should print the op's **name**; the number is the part
that rots. Filed as part of the row below.

## WHAT THIS DOES NOT CLAIM

Not suite-graded — this is a witness plus a root cause, not a board. `pascals.pas` is in
`corpus/packages/pascal/p5/sample_programs/`, which no graded suite reaches, and `fpc -Miso` rejects
`pascals.pas` itself for unrelated reasons (`Illegal expression` at 298/300), so it is evidence of the
mechanism and never an oracle pair. The 13-line witness above is the gradable one: `fpc -Miso` compiles and
runs it, and it is the fail-once case for the row.

## THE CURE — the missing half of a pair that already existed

`src/parsers/pascal/pascal.y`. A `forward` heading (`:896`/`:897`) ends with
`pas_ptrvar_release(); pas_recvar_release();` — it unwinds **both** registrations its parameter list made.
`pas_fwd_save()` saved only the **ptrvar** half and `pas_fwd_restore()` re-added only the ptrvar half. So a
**pointer**-typed forward parameter survived into the body and a **record**-typed one did not, and because
the ISO body repeats the name with no parameter list, nothing ever re-registered it.

1. `:429` — the recvar entry struct gains the tag `pas_recvar_s`, so it can be held by value elsewhere.
2. The forward table gains `struct pas_recvar_s rvsave[16]; int rvn;`.
3. `pas_fwd_save` saves the recvars from `g_pas_rvmarks[...]` exactly as it already saved the ptrvars;
   `pas_fwd_restore` re-appends them. Each half is now guarded by **its own** mark — the old shared
   `g_pas_npvmark == 0` early return would have skipped the entire save for a heading that has record
   parameters and no pointer ones. No new global; both marks already existed.

⛔ **The `.y` alone changes nothing.** The generated parsers are TRACKED and the Makefile carries no bison
rule, so editing the grammar builds clean and the edit is simply not in the program.
`scripts/regenerate_parser_and_lexer_from_sources.sh` is the step, and `pascal.tab.c`/`.tab.h` commit with it.

## ARMS

- `scripts/test_gate_pas_a_forward_declared_parameters_record_fields_resolve.sh` — **PASS=6 FAIL=0**, and the
  identical gate read **PASS=2 FAIL=4** before the cure. ⭐ Its PASS=2 is a **control** witness (the same
  program with the parameter list on the body instead of forward-declared) which the gate REFUSES rc=2 on if
  it fails: a stuck-red instrument and a real defect otherwise print the same thing. It grades **stdout
  against the oracle, never exit status** — an rc-only gate here reads green over three wrong answers.
- **Control arm (CEO-589):** output-hash census of `corpus/packages/pascal/{pat,fpc_tests}`, **305 programs
  x 2 modes = 610**, measured with the change stashed and the tree rebuilt, then restored and re-measured —
  **diff empty, zero output changed in either mode.**
- Pascal gates **PASS=22 FAIL=1 REFUSED=2 of 25**; both non-green re-measured **identical** with the change
  stashed, so both are standing. `test_gate_pas_port_trace.sh` reads 13 failed of 70 examined.
  ⛔ The other — `test_gate_pascal_m3/m4` refusing rc=2 on `master: 0 entries` — was cured by hq_B at SCRIP
  `dfac88bcf` while this was being written, **and the shape of it corrects what I implied here.** The gate
  refused **correctly**; what was wrong was its **stated cause**. It said "path defect or unpopulated
  master"; the real stop was ONE RUNNER, ONE BOARD (the harness refuses a board run to every seat but the
  coo) with a `2>/dev/null` discarding the sentence that said so. ⭐ It cost me a census of
  `corpus/tests/pascal/` to confirm `ALL.pas` was populated — a trip manufactured by a diagnostic
  confidently wrong about itself. **A red I cannot explain costs a measurement; a red that explains itself
  wrongly costs a measurement plus the belief I form at the end of it.** Same family as the
  `CSN_NO_SEGV_HANDLER` class: a correct procedure with a false explanation, here worn by an instrument.
- `make preflight` **44 arms, 0 red** — after it caught three free-form comments in my own patch, which the
  house style forbids.

## STILL OWED — named here rather than folded in, so the census above stays clean

1. `lower_pascal.c:571`'s `default:` arm still manufactures a value for any unhandled tree kind. 31
   `TT_SUCCEED` nodes ride it today, harmless only by luck. It should **refuse by name**.
2. `emit_drive` should print the op's **name**, not its ordinal — see the op=5/op=6 section above.
3. `lower_pascal.c` still has no `case TT_FIELD`; any other unresolved field reaches (1) again.
