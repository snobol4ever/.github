# FINDING — 2026-07-26 — SN4-ASM-SEP-1 session: `.Lbynamefn` DUPLICATE LABELS — beauty has NEVER been mode-4 assemblable

**MEASURED.** `scrip --compile beauty.sno` emits `.Lbynamefn183:` **267 times** in one `.s` (first duplicates by line ~54,856); `as` rejects with `symbol '.LbynamefnN' is already defined`. calc-1 emits 2 such labels, distinct — fine. The whole crosscheck corpus (315 programs, m4 309 PASS) never mints enough of them to collide, which is why the m4 gate never saw it.

**MECHANISM.** The label is minted in `src/templates/bb_call.cpp:290` as `".Lbynamefn" + _.nid`. `nid` is the per-chain node id — it RESETS for every emitted chain (every proc), while the `.L` local-label namespace is FILE-global. Hundreds of procs ⇒ hundreds of chains reusing the same nids ⇒ collisions. Pre-existing by construction: `bb_call.cpp` is untouched by the SN4-ASM-SEP-1 diff (`git status` five files, not among them).

**WHY IT HID.** beauty's Milestone-1 proof is MODE-3 vs the SPITBOL oracle (md5 `abfd19a7…`); the s169/s170 funnel proofs used beauty for BYTE-IDENTITY diffs of the text stream, never `as`-accepted it (as-accept 4/4 was hello/calc-1/hello.icn/class_twigil only). So mode-4 beauty was never linked, and the collision is plausibly as old as the by-name call template.

**FIX SHAPE (next rung, not done here).** Either (a) mint from the file-global uid (`g_emit.x86_uid`-style counter) instead of `nid`, or (b) prefix with the chain/proc (`.L<prefix>_bynamefn<N>` — prefix already flows into `emit_chain`). Sweep for SIBLING minting sites that use `_.nid` in file-scope labels before declaring done (grep `".L` + `nid` across `src/templates/`). Completion test: beauty `--compile` (budget ≥5 min; the emission alone exceeded a 110 s timeout at 13.8 M lines partial) then `as` accepts; plus crosscheck watermark unchanged.

**SESSION CONTEXT.** Found during the SN4-ASM-SEP-1 beauty scale-check (format itself holds at scale: 0 orphan rules, 21,093 `====`, 838,649 `----`). Source commit SCRIP `a31ea94a`; regen commits corpus `0e5df2d3` (bench) + `6b29ce95` (demo+icon, beauty.s excluded for the above), SCRIP `d998b1bb` (feature).
