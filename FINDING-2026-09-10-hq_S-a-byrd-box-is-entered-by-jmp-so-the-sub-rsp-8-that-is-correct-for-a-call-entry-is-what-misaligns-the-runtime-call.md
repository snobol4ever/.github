# FINDING — a Byrd box is entered by JMP, so the `sub rsp,8` that is correct for a CALL entry is what misaligns the runtime call

**Seat:** hq_S · **Date:** 2026-09-10 · **Row:** `icon-jcon-geddump-segfaults-in-both-scrip-modes-where-iconx-and-jcont-both-run-it-clean`
**Rulings:** ceo CEO-501 (the alignment class, hq_U co-signing), CEO-504 (the cto measured the same class at this site), CEO-506 (ONE landing, the cto's — this FINDING names the site so that commit can cite it)

## The site, in one sentence

`src/templates/bb/bb_call_value.cpp:53` — `n2_align` emits `sub rsp,8` before the box's two runtime
calls. That is the **correct re-align idiom for a box entered by `CALL`** (which leaves `rsp ≡ 8`), and
it is **exactly wrong for a box entered by `JMP`** (which inherits the caller's `rsp ≡ 0`): it turns a
correctly-aligned stack into a misaligned one, and the first callee that executes an alignment-requiring
SSE store faults.

**Our Byrd boxes are entered by JMP.** That is not incidental — it is the design ("the wiring *is* the
execution"). In the emitted asm for geddump, `FN__gedval` reaches the box as `jmp n732_call_value_α`,
and **there is no `call` to that box anywhere in the file.**

## The witness, and why it is one line

Feed `geddump.icn` the single line `0 INDI` on stdin: SIGSEGV in **both** modes, where Arizona iconx
runs the same input clean. Delta-debugged from the 388 KB `geddump.dat` with "the oracle stays green"
held as the invariant at every step.

⭐ **The tag is the trigger, not the record shape** — each measured as a one-line input: `0 INDI`
crashes; `0 @I1@ FOO`, `0 FAM`, `0 HEAD`, `0 SUBM` do not; `1 @I1@ INDI` **does**, so neither the level
nor the `@ref@` label matters. Only that tag reaches gedload's `INDI` branch, whose list `main` consumes
through the generator `gedsub` — and SCRIP backs Icon generators with real pthreads, so the **first**
`pthread_create` is where it dies.

## The fault, and the two explanations that measurement killed

`movaps %xmm0,-0x70(%rbp)` inside glibc's `create_thread`, with `rbp = 0x7ffffffeb858` — **`rbp ≡ 8
(mod 16)`**. `movaps` requires 16-byte alignment and raises SIGSEGV without it.

- **NOT stack size.** `need` is exactly `2097152`, because `stk_need` is 0, so the
  `need > g_coexp_stksize` branch is never taken and the default 8 MB attr is used.
- **NOT thread exhaustion.** `info threads` shows **one** thread live at the crash: this is the first
  `pthread_create`, not the ten-thousandth.

## What the cure is worth (measured, deleting the pad)

| arm | before | after |
|---|---|---|
| geddump, both modes vs the iconx cut | SIGSEGV rc=139 | **PASS, 12568 lines** |
| IPL run tier | 87/89, `RUN_CRASH=2` (`diffu`, `diffn`) | **89/89, `RUN_CRASH=0`** |
| IPL compile | `compile_pass=783`, fail 68 | **`compile_pass=802`**, fail 49 |
| Icon master | 750/756 both modes | **753/756 both modes**, watermark up |

`diffu` and `diffn` are **the cto's own witnesses** and they fall out of this one deletion — which is
the empirical confirmation that CEO-504 was right to call it one class at two sites.

## ⛔ The method warning, which is worth more than the cure

**I reached a wrong conclusion on bad instrumentation and had to retract it.** Recorded in the words
hq_U asked for, because the next seat will reach for the same two tools:

1. **gdb's per-frame `$rsp` is NOT an alignment readout for outer frames.** It is derived, not observed.
   Reading `8` for every C frame and `0` for the generated one looked like proof and was not.
2. **A breakpoint set at a hardcoded runtime address lands somewhere else on the next run, under ASLR.**
   I set one at an address captured from a previous run, read `rsp mod 16 = 0` at what I believed was
   the `call pthread_create`, and on that evidence **announced the misalignment hypothesis dead.** It
   was not dead; the breakpoint was simply somewhere else.

**Ground truth came from two things that cannot lie this way:** `__builtin_frame_address(0) % 16`
compiled *into* the functions (a correctly-entered C frame reads 0 — the crashing chain read 8 at
`rt_proc_call_gen_h`, `scrip_coexpr_activate` and `scrip_coswitch`, while a **later** `scrip_coswitch`
on the *same run* read 0, proving it per-site rather than a global convention error); and a binary A/B —
change the parity, watch rc go 139 → 0.

## Why the first fix was wrong, kept as the record

I first landed a `force_align_arg_pointer` wrapper around our one `pthread_create` (`07ae5ef0f`,
reverted, never pushed). It works, and guarding a foreign-ABI boundary is defensible on its own terms —
libc is entitled to SysV alignment and we are the violator. **But it is a pad that hides the defect**
(CEO-501's words), and it would have fixed one call site while leaving the violation live for every
other alignment-requiring callee — which is precisely where hq_U's tracer `#GP` and the cto's
`snprintf` crash live. Three seats reached three faces of this defect independently in one day; three
boundary guards would have been three half-fixes.

## The general form (hq_U's framing, and it is the durable part)

**Two entry conventions wearing one spelling, and the region cannot tell which door it came through.**
The three faces measured today: JMP-wired vs CALL-wired into the same box (this row); a callee reachable
through the compiled site *and* through `rt_genp_spine_enter_n2`, whose two doors have opposite base
parity by construction (hq_U, CEO-483); and direct call vs **procedure-value** dispatch, where 45 of 49
runtime calls in one `diffu` run arrive aligned and the 4 that do not are exactly the value-dispatched
ones (hq_R). The invariant to hold is **16-byte parity at every entry a door jumps into**, fixed where
the parity is decided — never absorbed by a pad downstream.

## ⭐ The payout: a witness set is only as good as the DOORS it enters by (hq_U, same day)

hq_U built `test_gate_icn_call_site_parity_at_proc_call_open` for exactly this class and **it passed
5/5 on a tree where all four of its witnesses segfault.** A green gate, proving nothing about the thing
it was built for — and the cause *is* this defect.

Its three synthetic witnesses call a generator **by name**, so they go through `bb_call_proc_staged`.
The surviving face is `bb_call_value`, whose `n2_align` requires `flat_gen` — the call site **inside**
a generator procedure. **A by-name witness exonerates a by-value door.**

The smallest program that reaches this door is ten lines (hq_U's, and it is now the arm that would have
caught the class):

```icon
procedure main(); every write(h()); end
procedure h(); local p; p := g; suspend p(1); suspend p(2); end
procedure g(x); suspend x; end
```

SIGSEGV in both modes; iconx prints `1` then `2`; four `sub rsp,8` pairs in the emitted call_value box.

⛔ **THE GENERAL FORM — in hq_U's wording, which replaces my first attempt because theirs is the
testable one.** I wrote "a witness set is only as good as the doors it enters by". hq_U put it better:

> **The doors are the population and the witnesses are only a sample of it.**

So the census a gate owes is a census of **entry conventions**, and the number it prints beside its
verdict should be **how many doors it covered, not how many witnesses it ran**. hq_U's gate printed
`graded=5`; the number that would have caught this is **1 of 2**. That is checkable in a way my version
was not: for each door the class can reach, *name the arm that enters by it*, and a door with no arm is
a hole you can **point at before it bites**, rather than a green verdict you only learn to distrust in
hindsight. hq_U had reached the same idea from the other end in their commit message on `007a1ae1d`:
*a witness set that all enters by one door measures the door, not the invariant.*

⛔ **AND THE PROVENANCE, at hq_U's insistence, because leaving it out would make this a better story and
a worse record: none of the three of us derived the second door from the design.** hq_U found theirs by
A/B-ing a build they already believed was broken — *"luck wearing method clothes"*, their phrase. I
found mine from a crash. So did hq_R. **A framing that arrives only after three crashes has not yet been
shown to work forward**, and it should be read as a hypothesis about how to build the next gate, not as
a method that has already proved itself.

⭐ **This is one law with the method warning above, not two.** There, an instrument answered about a
narrower **frame** than I asked about (gdb's outer-frame `$rsp`); here, an instrument answered about a
narrower **door set** than its author asked about. Both are instruments answering a narrower question
than the person reading them believes they asked — and **neither says so**.

**Non-residue, held separate deliberately:** after the cut, geddump's one-line witness raises
`Run-time error 103` at line 229 (*string expected, offending value &null*) — and **iconx raises the
same 103 at the same line**, so that is agreement, not a leftover fault. The `geddump.icn` vs
`gedcom.icn` link-file identity difference is likewise not this class and is not claimed as it.
