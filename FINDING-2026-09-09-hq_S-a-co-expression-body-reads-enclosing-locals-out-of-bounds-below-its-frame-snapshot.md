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
