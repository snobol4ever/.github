# Five IPL `.std` refs are zero-byte dead pins that match no run of their own program

**hq_R, 2026-09-09. Measured, NOT re-cut — the coo has an IPL board in flight and a
ref change moves its denominator under it.**

## The class

Five of the 89 committed IPL `.std` refs are **zero bytes**, all stamped
`Sep 5 14:59`:

```
progs/catlines.std  progs/colm.std  progs/lineseq.std  progs/longest.std  progs/streamer.std
```

Run under `test_icon_ipl_suite.sh`'s own isolation, `.argv` and `.fixtures`
conventions, the **Icon oracle disagrees with all five** — it emits one empty line
where each ref claims no output at all. SCRIP emits exactly what the oracle emits.
All five are scored against SCRIP today.

## Why "zero bytes" is wrong independent of any oracle

`catlines.icn` in full:

```icon
procedure main()
   local line
   line := ""
   while line ||:= read()
   write(line)
end
```

The last statement is an **unconditional `write()`**. The program cannot produce
empty output for *any* input, including none. So the ref is impossible on the
source alone — no oracle needed, and no argument about fixtures can rescue it. The
other four fail the same way against the oracle.

⭐ This is the strongest form of ref evidence available: a ref that contradicts the
program's own control flow is wrong before you run anything.

## What this is NOT — and the trap that has to be checked first

⛔ **A zero-byte ref is not automatically "re-cut me".** Earlier today
`duplfile` presented identically — oracle reproduced our output, ref disagreed,
"clearly a stale ref" — and re-cutting it would have been **destructive**. The ref
was right and the *tree* was incomplete: a vendored fixture
(`iiencode.fixtures/fixture.txt`) had gone missing, and re-cutting would have baked
that gap in permanently behind a green board. An oracle diff proves ref and tree
disagree; **it never says which of the two is wrong.**

So the same question is put here rather than assumed, and it does not fully close:

- The package convention **is** to give stdin-reading programs a `.dat` sidecar —
  11 exist (`knapsack`, `lisp`, `delta`, `parse`, `blnk2tab`, `delam`, …).
- `catlines` and `streamer` **read stdin and have no `.dat`.**

So two cures are available and they are not equivalent:

1. **Re-cut to one empty line.** Correct against the tree as it stands, and pins a
   *degenerate* test that exercises nothing but the program's exit path.
2. **Mint the missing `.dat` fixtures first, then cut.** Restores a test with
   content, matching what the other 11 already do.

⛔ (2) is the better cure for `catlines`/`streamer` and (1) silently forecloses it —
cutting first makes the missing fixture invisible, which is precisely the duplfile
failure in a new costume. `colm`, `lineseq` and `longest` do not call `read()`
directly and want checking on their own terms before either cure.

## Recommendation

Do not grade these five against SCRIP: they are dead pins, and SCRIP already
matches the oracle on all five. Mint `.dat` fixtures for the stdin readers, then
re-cut all five through `util_cut_icon_ipl_refs.sh`, in one commit, when no board is
in flight. Sequenced to the coo rather than done here.

## Provenance

Reproduced with the runner that called them red, per hq_B's standing rule, before
proposing any re-cut. Nothing in `corpus/` was changed by this finding.
