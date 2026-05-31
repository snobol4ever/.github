# HANDOFF — SBL-POS-PATCH-OFFSET ✅

**Date:** 2026-05-28
**Author:** Opus 4.7
**Repo:** SCRIP
**Commit:** `61ae501e`
**Parent:** `a21dc32b` (SWI-NEXT step 1, concurrent upstream — rebased onto, no conflict)
**Pre-rebase parent:** `4471b80d` (SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix)

---

## Summary

Fixed off-by-one in `bb_pat_pos.cpp` BINARY-arm sites that was corrupting the `0F 85` jne opcode at runtime patch time. Two-line change to the bin sites list; rung 044 native segfault → PASS. **Native broad corpus 171 → 187 (+16). Default-mode broad corpus 237 → 246 (+9). Zero regressions in any gate.**

---

## Diagnosis

`bb_emit_asm_result` in `src/emitter/emit_str.cpp:63-80` defines the patcher convention:

```c
for (int i = 0; i < n; i++) {
    for (; pos < bin.sites[i]; pos++) bb_emit_byte(out[pos]);
    if (bin.is_def[i]) {
        bb_label_define(bin.labels[i]);
    } else {
        bb_emit_patch_rel32(bin.labels[i]);
        pos += 4;
    }
}
```

So **`site` = byte offset where the rel32 begins** (for patches) or **where the label resolves** (for defines). The patcher streams bytes from `out` until `pos == site`, then either defines a label at that position OR writes a 4-byte rel32 at `[site, site+4)`.

`bb_pat_any.cpp` follows this convention exactly. Its 104-byte annotated layout:

```
[15-16] 0F 8D                 jge opcode (2 bytes)
[17-20] rel32 → ω             site 17 — first byte of rel32
[70-71] 0F 84                 je opcode
[72-75] rel32 → ω             site 72
[85]    E9                    jmp opcode (1 byte)
[86-89] rel32 → γ             site 86
[90]    β label-define here   site 90 (is_def)
...
[99]    E9                    jmp opcode
[100-103] rel32 → ω           site 100
```

ANY's sites `{17, 72, 86, 90, 100}` all point at the byte AFTER the opcode bytes. This is the canonical convention.

`bb_pat_pos.cpp` was wrong. Its bytes:

```
[0-2]   41 8B 02              mov eax, [r10]
[3-7]   3D + u32le(imm)       cmp eax, imm32
[8-9]   0F 85                 jne opcode (2 bytes)
[10-13] rel32 → ω             site should be 10
[14]    E9                    jmp opcode
[15-18] rel32 → γ             site 15 (was already correct)
[19]    E9                    jmp opcode  β label resolves here, site 19
[20-23] rel32 → ω             site should be 20
```

Prior sites: `{9, 15, 20, 21}` (POS) / `{25, 31, 36, 37}` (RPOS). The +1 on site 1 caused `bb_emit_patch_rel32` to write a u32le rel32 starting at offset 9 (POS) / 25 (RPOS) — **overwriting the `0F 85` opcode byte itself**. gdb traces from earlier sessions showed the corrupted opcode as `0F 32` (rdmsr) → SIGSEGV on rung 044 (`POS(0) LEN(3)` over `'hello'`), confirmed pre-existing at HEAD.

Sites 3/4 were off by +1 to compensate (β-define and final ω-jmp), keeping the byte stream consistent but in the wrong positions. Site 2 (γ-jmp rel32) was correct only because `E9` is a single-byte opcode.

Looks like the author used **"last byte of `0F xx` opcode"** as the convention for site 1, then mechanically shifted 3/4 to keep the byte arithmetic consistent — a self-consistent but wrong interpretation of `bin.sites`.

---

## Fix

`src/emitter/BB_templates/bb_pat_pos.cpp` lines 16-18, inside the existing `PLATFORM_X86` branch:

```cpp
bin = rpos
    ? bb_bin_t{ {26, 31, 35, 36}, {_.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p}, {false, false, true, false} }
    : bb_bin_t{ {10, 15, 19, 20}, {_.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p}, {false, false, true, false} };
```

(Was `{25, 31, 36, 37}` / `{9, 15, 20, 21}`.) The PR adds a 23-line comment block above the assignment documenting the byte layout and the patcher convention so the next person reading this template understands the offset arithmetic without re-deriving it.

Bytes emitted by the template are byte-identical pre/post-fix; only the sites list changed.

---

## Gates

Baseline measurements taken with `git stash` of the working tree to confirm pre/post-fix deltas. Each broad-corpus measurement re-run after a stash/pop cycle to confirm reproducibility — the `head -40` truncation in `test_interp_broad_corpus_and_beauty.sh` initially gave a false "demo_claws5/demo_roman regression" signal; `head -300` reveals those two tests fail identically pre and post (confirmed by running each in isolation under stashed vs unstashed worktrees).

| Gate                                       | Baseline (`4471b80d`) | Post-fix (`61ae501e`) | Δ      |
|--------------------------------------------|----------------------|----------------------|--------|
| G1 smoke (default)                          | 13/13                | 13/13                | 0      |
| G1 smoke (`SCRIP_M3_NATIVE=1`)              | 13/13                | 13/13                | 0      |
| G2 unified_broker                           | 39                   | 39                   | 0      |
| G4 broad corpus (default, mode-2)           | 237/280              | **246/280**          | **+9** |
| Native broad corpus (`SCRIP_M3_NATIVE=1`)   | 171/280              | **187/280**          | **+16**|
| Rung suite                                  | M2=19 M4=15          | M2=19 M4=15          | 0      |
| `audit_m3_native_binary_arms.sh`            | GATE OK              | GATE OK              | —      |
| Prolog smoke                                | 5/5                  | 5/5                  | 0      |
| Raku smoke                                  | 5/5                  | 5/5                  | 0      |
| Icon smoke                                  | 5/5                  | 5/5                  | 0      |
| FACT RULE grep                              | 0                    | 0                    | —      |

**Native +16 breakdown:** 044_pat_pos, 045_pat_rpos (direct), 8 FENCE tests (061/068/102/104/106/107/117/151 — FENCE templates internally use POS for cursor anchoring), 143_pat_regex_quantified_class, plus 5 drivers (Qize, ShiftReduce, stack, trace, tree).

**Default +9 breakdown:** Qize_driver, ShiftReduce_driver, assign_driver, fence_driver, global_driver, match_driver, stack_driver, trace_driver, tree_driver. These exercise POS/RPOS through a runtime-PATND path (likely `bb_build_brokered` invoked from `--interp` for certain pattern shapes — confirmed empirically; the BINARY arm runs even in mode-2 default mode for these drivers). The BINARY arm was silently miscompiling and SIGSEGV'ing in the runtime → those drivers were failing for the same reason 044 failed natively.

---

## Test methodology note (for future sessions)

The `head -40` truncation in `test_interp_broad_corpus_and_beauty.sh` (line 72) can give false positives/negatives when comparing failure-list deltas. When the script reports >40 failures, the displayed FAILURES list is truncated. To compare deltas robustly:

```bash
cp scripts/test_interp_broad_corpus_and_beauty.sh /tmp/test_full.sh
sed -i 's|head -40|head -300|' /tmp/test_full.sh
INTERP=/home/claude/SCRIP/scrip bash /tmp/test_full.sh 2>&1 | grep "FAIL " | sort > /tmp/run.txt
```

(Must override `INTERP` because `$HERE` resolves to `/tmp` after the copy.)

---

## NEXT

Now that the POS arm is healthy, the next priorities from GOAL-SNOBOL4-BB.md remain:

1. **Enable combinator flat-wire in mode-3** (`patnd_to_bb_tree` + extend `patnd_needs_xlate` for combinator roots) — bytes already ready via SBL-EP-BINARY, label arena landed (`744ae342`), prerequisites cleared. The May 28 investigation transcript above the rung documents the diagnosis and approach. Expect 050_pat_alt_two / 055_pat_concat_seq to flip native to "dog" / "ab cd ef".

2. **SBL-ARBNO-inside-combinators** — rung 052 (`POS(0) ARBNO('a') . V RPOS(0)` over `'aaa'`) still produces empty natively. The POS fix unblocked the segfault, but ARBNO inside an anchored concat still isn't matching. `patnd_tree_eligible` currently rejects XARBN subtrees; extending it to allow XARBN inside CAT (with the existing nested-block ARBNO shape) is the next ARBNO step.

3. **SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms** — still bombing or simplified; use the `std::deque<int>` slot-pair pattern from bb_capture.cpp.

4. **Native broad climb toward 260+/280** — 187/280 today; SPAN/ARBNO/FENCE-inside-var remaining clusters.

---

## Files touched

- `src/emitter/BB_templates/bb_pat_pos.cpp` (+25 lines, -2)

That's it. One file, one logical change, one commit.

---

## Cross-reference (concurrent upstream)

Upstream commit `fac53504` (IBB-4: every_to.icn mode-3 PASS via bb_to.cpp bin-site reorder) landed during this session — a sibling fix to the `bb_emit_asm_result` patcher convention in a different file. The bb_to.cpp fix was about NON-ASCENDING sites order (the patcher assumes ascending order so it can stream bytes forward in one pass), while this POS fix was about OFF-BY-ONE site positions (sites declared at opcode-end instead of rel32-start). Two different ways for templates to violate the patcher's invariants. Worth a quick audit pass at some point to scan every `bb_bin_t { ... }` literal in the codebase for both classes of bug: (a) non-ascending sites, (b) site pointing inside an opcode byte rather than at first byte of rel32. The audit script `scripts/audit_m3_native_binary_arms.sh` doesn't catch either — it checks for fake-jmp placeholders and substantive `bin.sites.push_back` calls, but doesn't validate site offsets against the actual byte string.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
