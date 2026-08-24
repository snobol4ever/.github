# FINDING — a suspend-generator's activation frame CANNOT live on the C stack below the caller's rsp

**Seat:** hq_P · **Session:** s271 · **Date:** 2026-08-24 · **Row:** `icon-n2-generator-activation-frames` (rank 0, hq_P)
**Status:** PROVEN with a memory-level witness. This **invalidates the storage half of the row's own brief** and re-shapes the rung.

## What the row's brief said to do

> *generators become R-4(b) activation frames … α push rbp/carve; γ-SUSPEND retains frame+pair and builds the resume record through rcx per emit.cpp's blob shape; β re-entry restores rbp through the record; ω-exhausted = FRETURN retire*

That is a faithful description of the pattern-blob path (`emit.cpp:3145` / `:3085` / `:3178`), and it was implemented this session — all five slices, behind `SCRIP_ICN_GENFRAME2`. **The port protocol is right. The storage location is not, and it cannot be made right by adjusting offsets.**

## The witness

`rung03_suspend_gen.icn`, 9 lines, `every write(upto(4))`. With the protocol armed, the generator carves a 304-byte frame at α and yields a descriptor to the caller. Measured with gdb at two moments on the *same address*:

| moment | `[0x7fffffffde30]` |
|---|---|
| the instant `rt_proc_call_epilogue_γ` hands the yielded DESCR back (`ptr=0x7fffffffde30 len=1`) | `0x0000000000000000  0x0000000000000000` |
| inside `write`, when `NV_GET_fn` dereferences that same DESCR | `0x00007fffffffdf90  0x0000000000402008` |

`write`'s own call frame has overwritten it. The crash is `NV_GET_fn (name=0x1)`.

## Why — and why it is structural, not a bug in the slices

The caller's `rsp` during the call is `0x7fffffffdf80`. The generator's frame base is `0x7fffffffde30` — **336 bytes below it**. Everything below a C stack pointer is scratch: the next `call` owns it.

⛔ **A suspended generator is not a suspended pattern blob, and the difference is exactly the thing that makes R-4(b) safe.** The blob's caller is a `*P DEFER` match driver, which does not run arbitrary code below the retained frame. **A generator's caller does — in this witness it is the very `write` that consumes the yielded value.** So both the frame *and* every descriptor pointing into it die at the caller's next call.

⭐ This also explains why the pre-frame emitter, for all three of its corruptions, still *produced values*: with nothing carved, the generator's ζ slots lived **inside the caller's own live frame**, above `rsp`. That is why the defect has read for sessions as "values almost work, the stack is wrecked" — the two halves are the same trade seen from opposite ends, and no offset adjustment gets both.

## What this means for the rung

The activation record must be **off the C stack** — heap- or GVA-allocated, with α allocating and ω freeing — so that it and anything pointing into it survive the caller's arbitrary execution. That is what `rt_gen_save_wires` / `icn_zframe_gen` were groping toward.

⛔ **Therefore slice (v)'s deletion list needs revisiting before it is executed.** The row schedules deletion of `rt_gen_save_wires` + the shadow globals + `icn_zframe_gen`'s stamp/consultation sites *once the new arm is default-on*. The new arm cannot be default-on with stack storage, so deleting the only existing off-stack machinery first would remove the very thing the corrected design needs. Delete after the replacement allocator exists, not before.

⛔ **And an off-stack activation record is very likely a NO-NEW-GLOBALS conversation with Lon** (an allocator handle or free-list is exactly the file-scope mutable state the law names). That ask must be a large ⛔ banner naming the proposed global, its type, its owning file, and why registers and the stack cannot carry it — and the honest answer to "why not the stack" is now *measured*, in this file, rather than asserted.

## What landed this session

All five slices, behind `SCRIP_ICN_GENFRAME2`, **default OFF**:

1. **α** — the missing third prologue arm (`emit.cpp`): `push rbp; mov rbp,rsp; sub rsp,frame_total` + args install. The graph previously reached *neither* existing arm and carved nothing.
2. **γ** — the 4-word resume record built off `rbp` (pair read in place at `[rbp+8]`/`[rbp+16]`, not banked at α), caller's `rbp` restored, `jmp rcx`.
3. **res** — `mov rbp,[rsp+24]; add rsp,32`, falling through to β.
4. **ω** — `mov rsp,rbp; pop rbp` + **the pre-frame return contract left byte-identical** (`DT_FAIL` in eax, `ret` through the `[rsp+0]` slot), so the retire arm cannot move the caller's arithmetic.
5. **caller** — `bb_call_proc_staged.cpp`: `L(3)` is a **shared** landing reached from both ports, so it now branches on the port tag in `al` before touching `rsp`.

⭐ Two defects found and fixed *within* the slices, both worth keeping as lessons:
- **γ must set the port tag last and never omit it.** Leaving `eax` alone does not mean "no tag" — it means the tag is whatever the body last computed, so the shared landing took the *retire* arm at random and unwound a live frame.
- **Both landing arms must join at the same `rsp`.** They did not, and the 8-byte disagreement showed up as `write` reading its argument slot one word off — a wrong *value*, not a crash, which is the harder failure to attribute.

## Proof obligations met

- **Byte-identity, killswitch OFF:** 7 witnesses spanning generator, mutual-recursion, list, alternation, proc and two real programs (`rung03_suspend_gen`, `rung37_mutual`, `rung22_lists_push_put_size`, `rung13_alt_alt_int`, `rung02_proc_fact`, `roman`, `queens`) emitted from clean `0e57de3b` and from this tree — **`diff -rq` reports zero differences.** The generator witness is the load-bearing one.
- **Gates (pristine `-O0`):** `test_gate_emit_no_lang` rc=0 · `test_gate_template_medium_invisible` rc=0.
- **SNOBOL4 corpus:** m3 363/364, m4 363/364, SKIP=0, `TDump_driver` the only red — the pinned expectation exactly, and that red is `hq_C`'s `822bc8a1` regression, not this work.
- ⛔ **Not claimed:** the armed path fixes nothing yet. With `SCRIP_ICN_GENFRAME2=1` the D2-suspend witnesses still SIGSEGV, for the structural reason above. **Zero Icon programs move either way.**

## Related

- [[FINDING-2026-08-24-hq_P-icon-generator-has-no-activation-frame]] — the root cause this builds on.
- [[FINDING-2026-08-24-hq_P-shared-node-cure-regresses-icon-47-programs]] — unrelated defect that currently moves the Icon denominator; do not read N-2 deltas against a tree carrying it.
