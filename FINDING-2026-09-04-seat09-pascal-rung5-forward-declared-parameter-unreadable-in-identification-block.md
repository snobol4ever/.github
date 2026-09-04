# FINDING: Pascal forward-declared procedure parameters are unreadable (print empty, not zero) in the block supplied later via bare procedure-identification

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16), row `pascal-ladder-every-feature-in-isolation-with-variations`, rung5 FORMS mint (`ladder__rung05_proc_func_forward`).

## What the rung5 FORMS walk found

ISO 7185 §6.6.1 gives procedure-declaration three alternatives: `procedure-heading ';' directive` (the `forward` declaration itself) | `procedure-identification ';' procedure-block` (the later bare definition — `procedure-identification = 'procedure' procedure-identifier`, i.e. the name ONLY, never the parameter list again) | `procedure-heading ';' procedure-block` (the existing `ladder__rung05_proc_func` baseline's shape — heading and block together, no forward). The standard is explicit that the block reached via the identification form is associated with the *same* procedure-identifier whose formal-parameters were already fixed by the original heading (§6.6.1: "The occurrence of a formal-parameter-list in a procedure-heading ... shall define the formal-parameters of the procedure-block ... to be those of the formal-parameter-list" + "The occurrence of a procedure-block in a procedure-declaration shall associate the procedure-block with the identifier in the procedure-heading, **or with the procedure-identifier in the procedure-identification**"). The vendored spec's own worked example (§6.6.2, `ReadExpression`) uses exactly this shape for a function; `fpc -Miso` accepts and correctly threads it through for a procedure too, confirmed before filing.

```pascal
program m1;

procedure announce(n: integer); forward;

procedure announce;
begin
  writeln('n=', n)
end;

begin
  announce(42)
end.
```

| | m3 (`--run`) | m4 (`--compile`) | `fpc -Miso` oracle |
|---|---|---|---|
| output | `n=` (blank, no digits) | `n=` (blank, no digits) | `n=         42` |

Both SCRIP modes agree with each other and disagree with the oracle identically (shared lowering/binding defect, not a per-mode emission divergence). Further isolated (not the master witness, ablated further for this report) to rule out a formatting-only bug: replacing the `writeln('n=', n)` with `r := n; writeln(r); writeln(n)` (a plain local var assigned from `n`, then two separate bare prints) still produces two **blank** lines, not `0` or garbage — `n` is not merely mis-formatted, it reads as empty in every position tried. Contrast confirmed on the same body with `forward` removed (heading+block only, the baseline's existing shape, no re-declaration): `n` prints correctly (`n=         42`) — the defect is specific to the identification-reopens-the-parameter-list path, not to reading a procedure parameter in general.

## Not cured by me

Construct-level declaration/binding defect (a forward-declared parameter loses its binding across the identification boundary), outside "fixture, xfail, or instrument" scope for a walker seat. Not investigated past a read-only grep: `grep -rln forward src/parsers/pascal src/lower` names only `src/parsers/pascal/pascal.l` (the lexer keyword); `grep -n "identification\|forward" src/parsers/pascal/pascal.y` returns **nothing at all** — the grammar appears to carry no dedicated production for procedure-identification/function-identification as a distinct case from a fresh procedure-heading, which is consistent with (but not proof of) a re-declaration being parsed as a brand-new zero-parameter procedure rather than as reopening the forward-declared one. A pointer for whoever cures this, not a diagnosis — no further `src/` reading done.

## Disposition

`ladder__rung05_proc_func_forward` (rank 187) added to the master **RED on both modes** — THERE IS NO XFAIL. `LADDER.tsv` rung5's FORMS/STATUS reflect it; `ladder__rung05_proc_func_no_params` and `ladder__rung05_proc_func_multi_param` (ranks 188-189) are clean, both modes, and stay green. `ask`ed hq_P (`q-pascal-forward-declared-parameter-unreadable-in-identification-block`). Continuing the FORMS walk on rung6 while this cures behind me, per THE LADDER RECIPE point 6.
