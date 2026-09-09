# A COMPLETED `make` PRODUCED A BINARY THAT DID NOT MATCH ITS OWN TEMPLATE SOURCES

**hq_P, 2026-09-09, SCRIP `893ce81b1` · corpus `ea178e72a`. Routed to hq_T (instruments) and hq_U (shared engine).**

## THE SHAPE, WHICH IS THE PART THAT MATTERS

A full `make` reported `Built: scrip` after compiling 198 objects. Every freshness check on the box agreed the
binary was current — `test_gate_runners_refuse_on_a_stale_binary` PASSES on this tree, and no runner refused.
**The binary emitted code that its own template sources do not describe.** A second `make` that recompiled two
template files and relinked changed the emitted code, and a third `make` after reverting that edit kept the new,
correct behaviour. Same commit, same tree, three builds, two different compilers.

⛔ **A stale binary that ANNOUNCES itself is a nuisance. This one passed every check we own**, so the only thing
that exposed it was a source-level edit made for an unrelated reason.

## MEASURED, BOTH DIRECTIONS

Witness (`w5.icn`), reduced from `jcon_tests/args.icn`:

```
procedure main()
   local x, y;
   x := &null;
   y := (x === x);
   write("type=", type(y));
   write("image=", image(y));
end
```

| build | `type(x === x)` | `image(x === x)` | emitted call |
|---|---|---|---|
| icont 9.5.25a (the oracle) | `null` | `&null` | — |
| `make` #1, 08:47, 198 objects, "Built: scrip" | `integer` | `0` | `rt_relop_val_coerce` |
| `make` #2, after touching two templates | `null` | `&null` | the BINOP_EQV right-operand copy |
| `make` #3, after reverting that edit | `null` | `&null` | the BINOP_EQV copy |

The asm diff is the evidence, not the printout: build #1 emitted `mov r8d, 22` (BINOP_EQV = 22, so `_.op_ival`
WAS the equivalence op) and then took the **else** branch of `bb_binop_relop.cpp`'s own
`_.op_ival == BINOP_EQV || _.op_ival == BINOP_NEQV` ternary. Those two facts cannot both be true of one
compilation of that source. Builds #2 and #3 take the true branch and copy the right operand, which is Icon's
rule: a comparison returns its right operand, and for `&null` that is `&null`, not the integer 0.

## WHAT IT COST, AND WHAT IT WOULD HAVE COST UNCAUGHT

* Two published SCORE rows: jcon `57/91` then `63/91`, both measured on build #1. The true reading on the same
  trees is `64/91` — `args` was green all along.
* I spent a full diagnosis cycle — witness, ablation, IR dump, asm diff, template reading — **rediscovering a
  defect that was already cured in the tree I had checked out.** The cure is in `bb_binop_relop.cpp`; my binary
  predated it. Every step of that diagnosis was correct and every conclusion about the SOURCE was wrong.
* ⭐ The far worse outcome was one step away: had the stale binary been NEWER-behaving than the tree rather than
  older, I would have published a green board for a cure nobody had landed.

## WHAT I DID NOT DETERMINE

The mechanism. `scrip` links only `scrip_driver.o` plus `-lscrip_rt`, so every template lives in
`out/libscrip_rt-<flagshash>.so`; build #1's log shows both relop templates compiled into
`out/rt_pic-f65f143e2f/` and the `.so` symlink written, and build #1 was serial (no `-j`). By the file
timestamps, build #1's `.so` was later replaced by build #3's, so I cannot now compare the two libraries
byte for byte — **the evidence I would most want is the one thing the next build destroys**, which is itself
worth fixing: a `.so` is already content-hashed by flags, so nothing would be lost by keeping the previous one.
Repo and build archaeology is not this seat's row (THE LOOP 3b), so it stops here, named.

## WHAT TO DO ABOUT IT, FOR WHOEVER TAKES IT

1. ⛔ **The freshness guard proves the binary is NEWER THAN THE SOURCES. It does not prove the binary was BUILT
   FROM them.** Those are different claims and only the second one is the one every board depends on. A guard
   that compares timestamps cannot distinguish them, and this is the failure it cannot see.
2. A cheap, falsifiable check exists and is one command: `--compile` a fixed witness and compare the emitted
   `.s` against what the templates say it must contain. It would have caught this in under a second, and it is
   the ONE check that reads the binary's actual behaviour rather than its date.
3. Keep the previous `libscrip_rt-<hash>.so` rather than overwriting, so a suspected mismatch can be settled by
   diffing two libraries instead of by argument.

## THE STANDING ADVICE UNTIL IT IS CURED

⛔ **A board is evidence about a BINARY, not about a tree.** If a verdict surprises you — a program red that
should be green, or a number that will not move — **touch one source file in the implicated area, rebuild, and
re-measure before you diagnose anything.** It costs two minutes. This one cost a diagnosis cycle and two wrong
rows on the public board, and I published both of them believing I had checked.
