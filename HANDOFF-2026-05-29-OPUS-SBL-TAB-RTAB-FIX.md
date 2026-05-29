# HANDOFF — SBL-TAB-RTAB-FIX

**Author:** Opus 4.7
**Date:** 2026-05-29
**Goal:** GOAL-SNOBOL4-BB.md — M3-NATIVE-4 rung (046/047 TAB/RTAB native SIGSEGV)

---

## Problem statement (carried from prior session)

After `SBL-POS-RPOS-FLAG-FIX` (commit `dbdec9bb`) on this same date, the predecessor
handoff identified `046/047 TAB/RTAB SIGSEGV native` as the next quick fix:

> Quick check if there's a sibling alignment bug in `bb_pat_tab.cpp` BINARY arm beyond
> the flag fix. 046 (`TAB(3) LEN(2).V`) hits TAB in first position with non-zero offset.

Both 046_pat_tab and 047_pat_rtab segfaulted under `SCRIP_M3_NATIVE=1 --run`, even
in trivial cases like `X TAB(0)` alone. Mode-2 `--interp` handled both correctly.

## Diagnosis

Three bugs found in `bb_pat_tab.cpp` BINARY arm, all introduced by commit `c01959f4`
(the original bb_bin_t conversion):

### Bug 1: TAB sites off-by-one (`{9, 23, 28, 29}`)

Same pattern as the POS-PATCH-OFFSET fix from `61ae501e` (last week) and POS-RPOS-FLAG
from `dbdec9bb` (yesterday). The patcher convention (per `bb_emit_asm_result` in
`emit_str.cpp:70-77`) is: `bin.sites[i]` is the byte offset where the **rel32 BEGINS**
(or where the label-define resolves). The author used a "last byte of opcode" convention,
shifting site[0] by -1. TAB layout:

```
[0-2]   41 8B 02              mov eax, [r10]
[3-7]   3D + u32le(imm)       cmp eax, imm32
[8-9]   0F 8F                 jg opcode (2 bytes)
[10-13] rel32                 → ω         site SHOULD be 10, was 9
[14-18] B8 + u32le(imm)       mov eax, imm32
[19-21] 41 89 02              mov [r10], eax
[22]    E9                    jmp opcode
[23-26] rel32                 → γ         site 23 (already correct)
[27]    E9                    jmp opcode  β-define HERE (was 28)
[28-31] rel32                 → ω         site SHOULD be 28, was 29
```

The +1 on site[0] caused the patcher to write the u32le rel32 starting at offset 9,
overwriting the `8F` opcode byte of `0F 8F jg` → corrupted instruction → SIGSEGV at
runtime. The +1 on site[2]/[3] shifted the β-define and final rel32 patch — they were
defining the label at offset 28 (the rel32 byte, not the E9 jmp opcode) and writing
the rel32 starting at offset 29 (one byte into the rel32 word), corrupting both.

### Bug 2: RTAB sites off-by-one (`{25, 32, 37, 38}`)

Same pattern as bug 1, just shifted by the 16-byte Σlen-load preamble. site[0] should
be 26 (rel32 starts there, opcode at 24-25).

### Bug 3: RTAB success-path writeback is the wrong instruction

This is the headline find. At offset 30 in the RTAB BINARY arm, after the jg-ω check,
the success path needs to store the new cursor (Σlen-N) into Δ. The TEXT arm shows
the intent clearly:

```
mov dword ptr [rax], ecx    ; rax = address of Δ, ecx = Σlen - N
```

The BINARY arm at line 31 had `bytes(2, "\x89\xC1")` = `mov ecx, eax`. That instruction:
1. Is not a memory write at all — it's a register-to-register move.
2. Overwrites ecx (which still held Σlen-N) with eax (which holds Δ).
3. Leaves Δ unchanged.

Result: RTAB(N) on success "matches" but doesn't advance the cursor. Subsequent
operations see stale Δ and either fail or crash.

The correct instruction is `mov [r10], ecx` (3 bytes: `41 89 0A`). This adds 1 byte
to the BINARY arm length (42 → 43 bytes), shifting site[1]/[2]/[3] up by 1.

## Fix

Single-hunk str_replace to `bb_pat_tab.cpp`:

- TAB sites: `{9, 23, 28, 29}` → `{10, 23, 27, 28}`
- RTAB sites: `{25, 32, 37, 38}` → `{26, 34, 38, 39}` (accounts for both off-by-one and +1 byte from writeback fix)
- RTAB byte at line 31: `bytes(2, "\x89\xC1")` → `bytes(3, "\x41\x89\x0A")`
- 36-line documentation comment above the assignment recording the layout for both TAB and RTAB.

## Validation

| Gate                  | Before  | After   | Delta |
|-----------------------|---------|---------|-------|
| GATE-1 default        | 13/13   | 13/13   | —     |
| GATE-1 native         | 13/13   | 13/13   | —     |
| GATE-2 broker         | 39      | 39      | —     |
| GATE-3 mode-4         | 184/280 | 184/280 | —     |
| GATE-4 mode-2         | 252/280 | 252/280 | —     |
| Native broad          | 220/280 | 223/280 | **+3** |
| Rung M2               | 19/19   | 19/19   | —     |
| Rung M4               | 17/19   | 17/19   | —     |
| Prolog/Raku/Icon smokes | 5/5/5 | 5/5/5   | —     |
| FACT                  | 0       | 0       | —     |
| audit_m3_native       | GATE OK | GATE OK | —     |

**Newly-passing native:** 046_pat_tab, 047_pat_rtab, W06_tab. **Zero regressions.**

Modest +3 (compared to POS-RPOS-FLAG-FIX's +25 yesterday) because TAB/RTAB are used in
fewer corpus tests than RPOS(0).

GATE-3 mode-4 and GATE-4 mode-2 unchanged because the TEXT arm of TAB/RTAB was already
correct, and only the BINARY arm had the off-by-one sites and writeback bugs.

## Files changed

```
src/emitter/BB_templates/bb_pat_tab.cpp  (3 bytes changed in the byte stream + 4 site
                                          values updated + 36-line layout comment added)
```

## Next session — options

The remaining ~57 native failures cluster as:

1. **SPAN ~10 tests** — SBL-SPAN-2 BINARY arm with `std::deque<int>` slot pattern from
   `bb_capture.cpp`. SPAN needs TWO persistent int slots (z, z_orig); β yields successively
   shorter spans using ABSOLUTE z_orig (not `[r10]`-relative — sibling boxes in concat
   mutate `[r10]` between α and β re-entry).

2. **ARBNO ~8 tests** — SBL-ARBNO-3 with deque-int pattern + brokered child call. ARBNO
   uses `nd->counter` for generator state, β re-enters child.

3. **FENCE ~6 tests** — bytes ready via EP-BINARY; need to identify which ones
   are still gated.

4. **REM/ARB/TWO atoms ~10** — individual BINARY arms (smaller scope).

5. **Capture-multiple / complex compositions ~10** — derive from atomic fixes above.

Recommend (1) SBL-SPAN-2 next — largest cluster, deque pattern established in
bb_capture, semantic spec available in `bb_exec.c case BB_PAT_SPAN`.

## Convention re-confirmed (third time)

The `bin.sites[i]` value is the byte offset where the **rel32 BEGINS** (for patches)
or where the **label resolves** (for is_def=true entries). Two-byte opcodes like
`0F 8F` mean the rel32 starts at opcode_offset + 2. One-byte opcodes like `E9` mean
rel32 starts at opcode_offset + 1.

This is now fixed in three templates: bb_pat_pos (`61ae501e`), bb_pat_tab (this commit).
Worth a global audit of remaining sites against the convention — could find more latent
landmines.
