# FINDING: the `bb_call_proc_staged.cpp` `+16` fix is empirically confirmed insufficient (patched and tested,
# not just hand-calculated); the `+288` lead is refuted; and whether that code path even runs is now in doubt

**Who/when:** seat08, 2026-08-30, `icon-n2-recursive-generator-per-activation-storage` row, continuing directly
from my own prior pass (`FINDING-2026-08-29-seat08-geddump-error3-not-host-region-overlap-real-defect-in-call-
site-plus16-constant.md`, `.github` `8a6dd4a3`). This pass executes that FINDING's own "NEXT ACTOR item 1" —
patch and rebuild, don't just hand-calculate — and the result changes the picture.

## Part 1 — the `+16` fix, ACTUALLY APPLIED, is confirmed insufficient (empirically, not by hand this time)

Made the local, uncommitted, diagnostic-only edit `bb_call_proc_staged.cpp` predicted would matter: computed
the self-rec condition once (`n2_selfrec_1word`) and used it both at the pad-push site and at the region LEA,
replacing the hardcoded `+ 16` with `+ (n2_selfrec_1word ? 8 : 16)`. Compiled clean (`make`, exit 0). Re-ran the
minimal 15-line repro from the prior FINDING under `SCRIP_ICN_N2_SELFREC=1`:

- **Still `Error 3` (rc=1), byte-for-byte identical failure.**
- gdb at `subscript_get`, same breakpoint/frame-2 methodology as before: `$rsp` at the crash frame is
  **bit-for-bit identical** to the pre-patch run (`0x7fffffbee618`), `[rsp+496]` is identical
  (`{0x100000028, rsp+1440}`), and **`[rsp+1440]` (the corrupted `id` slot) holds the exact same garbage
  bit pattern as before the patch** (`{0x00007fff8b3fe040, 0x0}`).

Byte-for-byte identity under a patch that changes an address computation by 8 bytes is strong evidence the
patched code is either (a) not on the path that produces this corruption, or (b) on the path but the 8-byte
change doesn't reach far enough to matter, exactly as the prior FINDING's hand arithmetic predicted (an 8-byte
overshoot lands inside the already-reserved `[1552, 44560)` region, nowhere near the corrupted offset 1440).
**Reverted the diagnostic edit** (`git checkout --`) — confirmed insufficient, not landed, matching this row's
standing discipline against patching shared N-2 arithmetic without full-rigor validation.

## Part 2 — the `+288` lead from the prior FINDING is refuted, not just unchased

The prior FINDING flagged, as an unchased lead: `walk`'s compiled prologue does `mov rax,[rsp+16]; mov
[rax+288],rbp` — writing saved-rbp at offset **+288** from the region pointer, and speculated this might mean
landing in "slot index 1" instead of slot 0 of the 64-slot self-rec table.

**Checked, and it is not a bug.** `SCRIP_N2_OFFSET_SELFTEST=1` on this repro reports `host=proc_walk ... total=
21168` and `host=main ... total=21504`, and `21504/64 = 336 = align16(fb_walk)+48`, so `align16(fb_walk) =
288` — i.e. `walk`'s own registered frame size rounds to exactly 288. Per the documented header layout
(`emit.cpp`'s own comment: "header H=R+ft: [H+0]=saved caller rbp..."), `H = R + ft = R + 288`. The prologue's
`mov [rax+288],rbp` is therefore `mov [R+288],rbp` = `mov [H+0],rbp` — **exactly the documented `[H+0]=saved
caller rbp`, not an off-by-one-slot error.** The coincidence that `ft` and the self-rec per-slot size share the
value 288 in this particular repro (and in `gedwalk`'s case too) is what made this look suspicious; it is not.

## Part 3 — a real doubt, not resolved this pass: is `bcps_spine_gen_arm` even the path that runs here?

While re-verifying Part 1, checked whether the emitted `.s` actually contains this function's own distinctive
content for `main`'s call to `walk`. It contains **some** of it (`rt_gen_spine_pass_γ`/`_ω`,
`rt_gen_spine_resume_enter` — all declared and used only in this function) — but **none** of its `x86("comment",
...)` text (`"seed depth 0"`, `"I am the recursive call"`, `"PL-CALL-ALIGN"`, `"N-2 STEP 3 REGION HAND-OFF"` all
return zero grep hits in the compiled `.s`). This could mean either (a) comments are stripped from this build's
`.s` output regardless of which branch ran (in which case the absence proves nothing), or (b) a genuinely
different branch of the same function executes than the depth-push/region-LEA one every session on this row —
including mine, twice — has been reading and reasoning about. **I could not resolve which, this pass**, and
flag it explicitly rather than assume either way: the `SEAT01_N2_STEP3_DBG` diagnostic (which DOES fire, and
DID report `off=0 base=1552` matching the arithmetic in Part 1) proves `icn_gen_host_reserve_offset` gets
called for this node, but that call happens at the very top of the function (line ~749, before ANY branching) —
it does **not** by itself prove execution continues into the specific pad-push/region-LEA code 40+ lines later
that I (and the prior FINDING) patched and reasoned about.

**Concrete, cheap next step to resolve this cleanly** (not attempted this pass, time-boxed out): assemble+link
a real mode-4 binary from the repro (`--compile` without `-o` writes to stdout; needs an explicit `as`+`gcc`
step this pass didn't take) and `objdump -d` it to get REAL addresses for `n51_proc_gen`'s instructions, then
break by address in gdb rather than by comment-grep in the `.s` — this settles definitively which branch runs,
which comment-grepping on `.s` text cannot.

## Not attempted

No fix landed, no source touched (diagnostic edit reverted). Root cause 2 (reservation formula) and mutual
recursion (c) remain untouched, still Lon/hq design territory per this row's GOAL.

## Suggested next step, not decided here

1. Resolve Part 3's doubt directly (assemble a real mode-4 binary, `objdump -d`, break by address) before
   trusting ANY further reasoning about `bcps_spine_gen_arm`'s pad-push/region-LEA code on this witness —
   including everything in my own two FINDINGs on this row and the underlying assumption behind genqueen's
   Root-Cause-1 fix recommendation (seat12), which reasoned about the same function's `[rsp+32]` depth read in
   `emit.cpp`'s callee prologue via the same kind of static comment-adjacent reading.
2. If Part 3 confirms a different branch runs, the actual corruption mechanism is still fully open and needs a
   fresh trace from that confirmed starting point, not a continuation of the region-LEA hypothesis.
3. Root cause 2 and mutual recursion (c): unchanged.
