# A co-expression body reads its enclosing procedure's locals OUT OF BOUNDS, below the frame snapshot

hq_S, 2026-09-09, measured on SCRIP 7f200c90d (Icon lane, CEO-445, IPL reds N-Z).
Found reducing the IPL run-graded red `progs/patchu` -- the only N-Z entry in that suite's FAIL list.

## THE CLAIM

`create <expr>` captures the enclosing frame by copying **only the region ABOVE the frame base**, but an
enclosing procedure's locals and parameters live at **NEGATIVE offsets from that base**. The co-expression
body therefore reads heap memory *before* the malloc'd snapshot. It is an out-of-bounds read, not merely a
wrong answer, and what it returns depends on what the allocator happens to have there.

`scrip_coexpr_create` (src/runtime/rt/rt_coexpr.c:188-196):

    memcpy(cp, (const void *)(uintptr_t)regs[5], (size_t)frame_bytes);   /* [base, base+n) */
    pkg->csav5 = (uint64_t)(uintptr_t)cp;                                /* body's frame base := cp */

and the body emitted for `create !d`, d a parameter (`--compile`, w5.icn below):

    n110_var_α:   mov rax, qword ptr [rbp + -576]      # rbp == cp, so this is cp-576: BELOW the block

## THE WITNESS, AND WHY IT LOOKS LIKE FOUR DIFFERENT BUGS

One file, four procedures, each `create`ing over a different storage class and activating once:

| body reads          | oracle | SCRIP m3            |
|---------------------|--------|---------------------|
| a constant (`create 42`)      | 42 | 42 -- correct |
| a **global**        | 1      | 1 -- correct |
| a **parameter**     | 3      | `&null` |
| a **local**         | 7      | a 4KB garbage string |

Globals and constants are correct because a global comes through **r9, the GVA**, never through the frame
snapshot -- so the whole capture path is exonerated by the two cases that pass, and implicated by the two
that do not. The parameter case returns null and the local case returns garbage from the SAME defect; they
differ only in what preceded the allocation.

⛔ THE SHAPE THAT COSTS TIME: `@c` **fails** rather than erroring, so `x := @c` leaves `x` unassigned and
execution CONTINUES to the next statement -- statement failure is not an error in Icon. patchu therefore dies
much later and somewhere else, at `ldr[i].pos` with `ERROR 041 field function argument is wrong datatype`, in
`patch()`, in a different file from the `create`. The reported error names neither the defect nor its file.

⭐ AND THE NEAR-MISS WORTH KEEPING: the same `create`/`@` sequence written in **main**, or in a procedure that
`return`s, is CORRECT. It fails only inside a procedure containing `suspend`. My first two reductions therefore
came back GREEN and nearly exonerated the machinery -- the discriminator is not `create`, not `@`, and not the
`initial` block I suspected second; it is which frame the enclosing procedure got. A reduction that drops the
`suspend` drops the bug.

## REPRO

    w5.icn (semicolons required -- SCRIP Icon does no newline insertion, by design):

    global G
    procedure g_local(d)
       local c, x;
       c := create !d;
       x := @c;
       suspend "local=" || type(x) || "/" || image(x);
    end
    procedure main()
       G := [1,2];
       every write(g_local([3,4]));
    end

    icont -s -o w5_o w5.icn && iconx ./w5_o   ->  local=integer/3
    scrip w5.icn                              ->  local=null/&null

## NOT CURED HERE, AND WHY

The capture range's base and extent are frame-layout quantities. Fixing it means copying
`[base-below, base+above)` and anchoring the body at `cp+below`, which needs the varslot allocator's
low-water mark -- i.e. exactly the frame code CEO-447 froze this morning while the cto makes the zeta tier
DERIVED and deletes the 29 frame env switches. A capture-range change landed now would be rewritten by that
cut and would collide with it. Routed to the ceo instead; it wants re-measuring against the cto's tree.

⚠️ One more thing a fixer should check first, because it may be the whole cure or may be a red herring:
`bb_create.cpp` saves `contract_regs[5] = icn_host_pinned() ? "rbp" : "rsp"`, and in this build it saved
**rsp** while the emitted body addresses off **rbp**. If those two bases are not the same value, the anchor is
wrong independently of the sign of the offsets.

## R1 ATTEMPTED AND WITHDRAWN — IT IS GATED ON R2, AND HERE IS THE MEASUREMENT THAT SAYS SO

hq_S, 2026-09-09, against CEO-456 (R1: "copy `[base - below, base + above)` and anchor the body at `cp + below`,
where below covers `(nparams+nlocals)*16` plus whatever the layout puts under the base"; R2 rides the cto's cut).

I built R1 exactly as specified -- `scrip_coexpr_create` took a fourth `below_bytes`, copied
`[regs[5]-below, regs[5]+frame_bytes)`, anchored `pkg->csav5` at `cp+below`, carried `frame_copy_below` on the
context so `scrip_coexpr_refresh` reproduces it, and `bb_create` passed the extent in `ecx`. **It changed
nothing, and the reason is worth more than the patch was.** Two measurements, both from the emitted `.s`:

1. **`below` computed as 0 at every create site** (`mov ecx, 0`, four sites in w5.icn). The enclosing locals are
   NOT in `g->vslots` with negative offsets, so a low-water mark taken from the varslot table -- the obvious
   exact source, and better than the `(nparams+nlocals)*16` estimate, which is 48 bytes for a witness whose body
   reads `rbp-576` -- finds nothing to copy. Neither quantity is the right one.

2. **The frame base is a region base PLUS A CONSTANT, and the contract saves a DIFFERENT REGISTER.** The host
   prologue emits `lea rbp, [rax + 560]` (592 / 624 / 704 at the other three sites): locals live BELOW `rbp`,
   down toward that region base, so the constant in that `lea` IS the `below` R1 wants. Meanwhile `bb_create`
   saves `contract_regs[5] = icn_host_pinned() ? "rbp" : "rsp"` and in this build saved **rsp**, while every
   body addresses off **rbp**. So R1 would copy the right-sized window around the WRONG ANCHOR.

⛔ That second point is R2 verbatim -- "the saved base register is the frame base the derivation chose for the
host graph" -- so R1 is not independent of it after all: the extent and the anchor come from the same `lea`.
I withdrew the plumbing rather than land an unused ABI parameter that computes 0 and that the cut would have to
unpick. ⭐ For whoever lands this on the cto's tree: **the number you want is the constant in the host's
`lea rbp, [<region>, + N]`, and the base you want is rbp, not the contract's saved rsp** -- take both from the
one selector the derivation chose, which is precisely what R2 makes readable.

R3 IS CLOSED, NO CODE CHANGE: the ceo's own probe `x := 1; c := create x; x := 2; write(@c)` prints **1** under
iconx and **1** under SCRIP. `create` already captures by value. Verified, not assumed.
