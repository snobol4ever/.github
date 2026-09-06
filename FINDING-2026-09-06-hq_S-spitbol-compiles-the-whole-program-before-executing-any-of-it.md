# FINDING — SPITBOL compiles the whole program before executing any of it, and that refutes the VALUE-quirk mechanism as stated

**Measured by** hq_S, 2026-09-06, FLEET-12 · oracle `/home/resources/x64/bin/sbl -bf` (the correctness oracle) ·
**Row** `snobol4-value-call-poisons-next-lazy-comparator-oracle-quirk` · builds on seat03's correction that
`/home/resources/spitbol-pristine` exists (HEAD `4fe74db`).

## The question this answers

The row's own NEXT block named two things as "the actual work for whoever picks this up". The second was:

> whether this SPITBOL compiles the full program before executing any of it, or compiles in smaller
> per-statement/per-block chunks interleaved with execution — this decides whether VALUE's runtime lookup can
> precede a later line's compile-time codegen.

It had been carried unanswered across four sessions, against a 1.27 MB hand-written assembly file.

## The measurement

Two three-line programs, and the second exists to kill the obvious confound.

```
        OUTPUT = "EARLY LINE RAN"
        X = (((
END
```
`sbl -bf` → **rc=231**, `ERROR 226 -- syntax error: missing right paren`, and **`EARLY LINE RAN` is never printed.**

```
        OUTPUT = "EARLY LINE RAN"
        X = UNDEFINEDFUNC(1)
END
```
`sbl -bf` → **`EARLY LINE RAN` IS printed**, then `ERROR 022 -- undefined function called`.

⛔ **The control is the whole finding.** Without it, the first program proves nothing: "output was buffered and
lost on the error exit" explains it just as well. Line 1 runs when line 2 fails at RUNTIME and does not run
when line 2 fails at COMPILE time. Therefore compilation of the entire source completes before execution
begins.

## What it refutes

The row's leading mechanism — traced from real code by seat03 (`cgv05`–`cgv13` at `sbl.asm:11158-11212`,
`cgv36` at `:11398-11403`) — is that SPITBOL bakes a builtin's `vrfnc` pointer into generated code once, at
the moment that call expression is compiled, so a call site compiled while the callee's `vrblk` still held the
`stndf` sentinel is permanently poisoned and raises ERROR 22 through `o_fun` (`:3627`).

The baking is real. The **story built on it is not**: it required `VALUE`'s RUNTIME lookup to precede a LATER
LINE's compile-time codegen. With whole-program compilation that ordering is impossible — every call site is
already baked before the first `VALUE()` call executes.

## What survives, and what is now hypothesis

Surviving fact: a call site **can** be permanently poisoned by whatever the `vrblk` held at its own compile
moment. So the poisoning must happen **at compile time**: compiling the `VALUE(...)` expression itself must
leave the shared name-lookup machinery in a state where the next `gtnvr` call for a predefined name fails to
wire `vrfnc`. Candidate state, all static scratch belonging to that routine: `gnvsp` (the `vsrch` table
pointer), `gnvhe` (hash-chain end), and `hshnb` (`:2856`, stored *for* `gtnvr` by its caller) — i.e. a
save/restore that is not one.

⛔ **That is a hypothesis with a named mechanism and it has not been measured.** It is written here so nobody
re-derives it, not as a result.

Also established: **the entry point of the `gnvNN` blocks is `gtnvr`** (`sbl.asm:14314`, marked `prc e 1`,
ending `enp` at `:14494`), with **33 call sites**. The row's remaining open question is whether `gtnvr` is
entered identically for a compile-time first reference and for a runtime resolution from a computed string.

## The reusable part

⭐ The answer took two three-line programs and under a minute, against a question that had survived four
sessions of reading assembly. The source reading was necessary to know *what to ask* — it was not what
answered it. **When the open question is about observable behaviour, the oracle is the cheapest instrument in
the room, and unlike a 1.27 MB assembly listing it cannot be misread.**

⭐ And the control is not optional. A single program showing an absent output is consistent with two different
worlds; the pair separates them. This is the same discipline as keeping a green control in a gate: the arm
that *cannot* distinguish the hypotheses is the one that makes the other arm mean something.
