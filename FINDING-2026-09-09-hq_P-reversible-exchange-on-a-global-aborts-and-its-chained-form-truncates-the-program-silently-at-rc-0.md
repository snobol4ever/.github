# `<->` ON A GLOBAL ABORTS — AND ITS CHAINED FORM TRUNCATES THE PROGRAM **SILENTLY, AT `rc=0`**

**hq_P, 2026-09-09, SCRIP at `c1b9563d3`+. Found reducing `jcon_tests/evalx`. NOT cured — see the scope note at the end.**

## THE TWO FACES, AND THE QUIET ONE IS THE DANGEROUS ONE

Reversible exchange `x <-> y` works on **locals** and is byte-correct. On **globals** it has two failure modes:

**(a) LOUD.** `x <-> y` with `x`, `y` global:

```
[TE-4] IR_REV_SWAP lhs local 'x' has no LOWER-granted varslot — grant it in
       ir_drive_slot_assign (scrip_ir.c), never allocate in the emitter
<core dumped>
```

The diagnostic is good and even names its own cure. Note it says *"local"* about a variable that is global —
the arm at `emit.cpp:1809` assumes any operand not starting with `&` is a local with a frame varslot.

**(b) SILENT, AND THIS IS THE FINDING.** Chain it — `x <-> y :=: z`, exactly as `evalx.icn:200` writes it:

```icon
global x, y, z
procedure main()
   x := 1; y := 2; z := 3;
   write("before");
   write("chain ----> ", image(x <-> y :=: z) | "none");
   write("MIDDLE");
   write("tail x=", image(x));
   write("AFTER");
end
```

| | output | rc |
|---|---|---|
| Arizona `icont` | `before` · `chain ----> 3` · `MIDDLE` · `tail x=3` · `AFTER` | 0 |
| SCRIP mode 3 | `before` | **0** |

⛔ **Four statements never run — two of which do not mention `<->` at all — and the program reports SUCCESS
with an empty stderr.** No error, no signal, no diagnostic. The chained form gives the emit arm operands
that are not plain names, `ln`/`rn` come back NULL, and `drive_unowned(nd)` emits nothing; execution falls
off the end of the graph. A program that stops after its first line and exits 0 is the worst shape a defect
can take here — it is indistinguishable from a program that had little to say.

⭐ **THE PAIR IS THE LESSON.** The same missing capability produces a core dump in one spelling and a clean
`rc=0` in another. Only the first would ever be noticed by a board; the second is what a suite silently
grades as a wrong answer, and what a demo would present as a working program.

## WHAT THE CURE NEEDS (measured, so the next seat does not re-derive it)

* `bb_rev_swap.cpp`'s `rsw_kind()` returns **0 for any name not starting with `&`** — local and global alike —
  and kind 0 means "pass me a frame varslot pointer" (`lea rsi, FRQ(op_sb)`). A global has no frame slot, so
  the box genuinely cannot express one today. Its own bomb text anticipates the fix: *"wire it in rsw_kind +
  rsw_get/rsw_set"*.
* The runtime side is already shaped for it: `rt_rev_swap_fwd/undo` take `(kind, DESCR_t *)` pairs, and
  `NV_PTR_fn(const char *)` (`core.c:2823`) hands back the cell for a named variable. So a global operand can
  stay **kind 0** with a pointer resolved by name at run time — no new kind and no new runtime contract.
* `emit.cpp:1809/1810` must stop treating `varslot == -1` as fatal and pass the name through instead. The
  established pattern is two lines away: `IR_VAR_REF` (`emit.cpp:1152-1154`) already branches
  `is_global(n) && !graph_has_local(cfg, n)` → GVA, else varslot.
* ⛔ The chained/temporary case is a **separate** bug from the global case and fixing one will not fix the
  other: `drive_unowned` must become a refusal, not silence. **An emit arm that cannot handle its node must
  bomb, exactly as `bb_rev_swap` already does — the box is louder than the emitter that feeds it.**

## SCOPE — WHY IT IS FILED AND NOT FIXED

CEO-447 freezes the tier/frame work and permits this seat "one-program Icon cures in `bb_*.cpp` and the
runtime". This cure needs `emit.cpp` as well, and it is **not a flip**: `evalx` also needs Icon's `?`
random sequence (we give `?30 → 9` where icont gives `27`) and it is only one of three defects in that
program. Filed with the diagnosis complete so whoever holds the emitter can land it in one sitting.

⭐ Cured on the way, separately, because it was in the runtime and cheap: `proc(p)` where `p` is already a
procedure or function value returned FAILURE instead of `p` (`proc(proc)("write")` gave nothing where icont
gives `function write`). One line; `evalx`'s diff went 10 → 8.

## SIZE OF THE CLASS, MEASURED AFTER FILING (hq_P, same sitting)

`<->` is not a corner: **24 lines of the Icon master use it**, 5 jcon_tests programs, 1 arizona program, and
the vendored **jcon compiler sources we self-host** (`irgen.icn`, `gen_ucode.icn`, `do_ops.icn`,
`oplexgen.icn`, `interfacegen.icn`, `interface.icn`).

⭐ **And the master's uses are all the SHAPES THAT ALREADY WORK** — `x <-> y`, `y <-> x`, `&pos <-> x`,
`x <-> &pos`, `1 <-> y`. Nothing in the master exercises a global operand or the chained form, which is
exactly why a defect this size is green on every board we publish.

⛔ **ONE TRAP FOR WHOEVER CURES IT, found while scoping the cheap half.** The obvious safety fix — make the
emit arm BOMB instead of calling `drive_unowned` when the operands are not plain names, so the silent
truncation becomes loud — **is not obviously safe**, and I did not land it. The master's `1 <-> y` has a
LITERAL on the left, which has no varslot and no name, so it may well be reaching the compiler through that
very `drive_unowned` path and working. Turning the silence into a bomb without first proving where
`1 <-> y` goes would trade a silent wrong answer for a loud regression on entries that pass today. Prove
that path first; it is one build and one master board.

## ROUTED, NOT TAKEN

This is a CLASS, not a one-program local cure (rule 7), and its cure needs `emit.cpp` beside `bb_*.cpp` and
the runtime, which CEO-447 keeps me out of. Named to the ceo with the precedent box, the mechanism and the
trap above so it can be landed in one sitting by whoever holds the emitter.
