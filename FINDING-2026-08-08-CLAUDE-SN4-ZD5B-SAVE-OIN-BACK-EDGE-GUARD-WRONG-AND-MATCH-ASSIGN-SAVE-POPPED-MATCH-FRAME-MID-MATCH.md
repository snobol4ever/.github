# FINDING 2026-08-08 (CLIMB s14) — `k>r` OIN GUARD WRONG FOR SCAN-RETRY BACK-EDGES; `MATCH_ASSIGN_SAVE` POPPED THE ENTIRE MATCH FRAME MID-MATCH

**Rung:** GOAL-SN4-ZETA-CLIMB C-6 · **Fix:** SCRIP `912c0dbf`
**Symptom:** `pb_snapshot_imm` rc=134 (stack canary) — output `S A` correct, canary fires

---

## THE LAND MINE

`pb_snapshot_imm` (`'AZB' ? 'A' $ X X`) crashes with stack smashing after the
correct output `S A`.  s13 cursor attributed this to "PB-1s snapshot machinery
misclassifying `$ X` capture-target."  **That theory is wrong.**

Manual p.86/87 is unambiguous: the second `X` is a plain name, which snapshots
at BUILD time (pattern construction), not match time.  The pattern is effectively
`'A' $ X 'Z'` — it matches `AZ`, assigns `A` to X via immediate assignment, and
on success X='A'.  Output `S A` is exactly correct.  The snapshot was fine;
only the stack was not.

## ROOT CAUSE

`IR_MATCH_ASSIGN_SAVE` has **ω = MATCH_BEGIN** (the scan-retry back-edge: on
failure, retry the match from the next subject position).  In `zd_plan`, the
non-blob path for oin is:

```c
for (int k = 0; k < rl; k++) {
    if (nodes[run[k]] == gt && k > r) gin = 1;
    if (nodes[run[k]] == ot && k > r) oin = 1;   // k>r guard — WRONG for oin
}
```

MATCH_BEGIN sits at `k = hpos` in the run.  For SAVE at `r = 5`, `hpos = 4`
satisfies `k < r`, so the `k > r` guard always fails → `oin = 0`.

With `oin = 0`, line 2105 fires:

```
zwpop[SAVE] = _wzdepth - K + kc = 32 - 16 + 144 = 176 + 16 - 16 = 176
```

The template emits `add rsp, 16` (SAVE's own K) **followed by** `add rsp, 176`
at the β port.  That releases the entire 192-byte match frame (Kc=144 +
pre-match producer cells 48 = 192 minus SAVE's own 16) while MATCH_LIT,
MATCH_ASSIGN_IMM, and MATCH_DEFER are still live inside it.  Every subsequent
write from those nodes lands in the caller's frame.  The canary in `main` fires
at the function epilogue.

## THE GUARD ASYMMETRY

`k > r` is **correct** for `gin` (γ must point forward in the run — a node
whose γ exits the run IS a terminal and should carry zgpop).

It is **wrong** for `oin` (ANY intra-run ω target, forward OR backward,
means the node is not a statement-exit and must NOT carry wpop).  A node
whose ω back-edges to an earlier run member is still inside the match — the
scanner is retrying, not leaving.  MATCH_END is the sole release authority.

The blob path (line 2096) already gets this right:
```c
if (nblob > 0) { for k in cm[]:
    if (nodes[k] == ot) oin = 1;   // no positional guard — any cm[] member
}
```

The non-blob path inherited the wrong positional guard from the gin clause.

## THE FIX

Drop `k > r` from the `oin` side only:

```c
else for (int k = 0; k < rl; k++) {
    if (nodes[run[k]] == gt && k > r) gin = 1;
    if (nodes[run[k]] == ot) oin = 1;   // ← k>r guard removed
}
```

**Effect:** ZD trace confirms `wpop=0` for SAVE, `wpop=192` for MATCH_END (sole
release authority).  Rogue `add rsp, 176` absent from emitted asm.

**Byte-identical** for all nodes with forward ω (the prior population) — their
targets are already `k > r` so the guard change doesn't fire.  Only back-edge
ω nodes are newly protected.

## MEASURED

m3 135/7/0/0 · m4 132/10/0/0 — unchanged from the zdhh fix, 0 REGRESSION.

Regen ×3: 19 feature `.s` files changed (wpop suppressed on SAVE nodes in
scan-retry patterns), 3 benchmarks changed, 7 demo programs changed.
Representative oracle checks: word4.sno, wordcount.sno, calculator-1.sno,
pattern_test.sno — all match SPITBOL oracle.  `string_pattern.sno` benchmark
crashes under SCRIP (rc=139) **at the s13 watermark commit too** — pre-existing,
not caused by this fix.

## STILL OPEN — SECOND CRASH SOURCE IN pb_snapshot_imm

The `add rsp, 176` is gone.  **pb_snapshot_imm still crashes** (rc=134).

Second source: PATCTX saves (`outer_Σ/δ/Δ/cap_gen/old_rbp`) are emitted as
`[rbp + 88/96/104/112/120]` via `FRQ()` in the MATCH_BEGIN template.  In mode 3
(in-process JIT), `rbp` has not been updated — it retains the compiler-generated
rbp from `main`'s prologue, which in this build is a `.data`-section address
(`0x433fd0`).  Those writes land in `.bss`/`.data`, hitting the stack canary at
`rbp + 128`.

Affected corner: `Kc > 0 AND nblob_real = 0 AND zws = 0 AND zwr = 0`.  In this
configuration no frame-establishing instruction (`push rbp; lea rbp,[rbp+8]` for
ZW/mechanism-2, or `mov rbp,rsp` for STF) is emitted before the PATCTX saves.

D07 (Kc=256, nblob=0) takes mechanism-2 (`zwr=1`, confirmed by `push rbp` in
emitted asm) — so its FRQ expands to `[rbp - negative]` after the valid `push rbp`
and is safe.  pb_snapshot_imm hits the unframed corner.

**Fix direction:** for the `nblob=0 / zws=0 / zwr=0 / Kc>0` arm, the template
must either push a minimal rbp frame (aligning with mechanism-2's `push rbp; mov
rbp,rsp`) or route PATCTX saves to RSP-relative addresses.  This is a template
structural change — MECH territory (new claim/frame protocol for this corner).

Confirmed pre-existing: identical rc=134 at `01440ed4` (s13 watermark).  Does
NOT affect any of the 135 currently-passing probes (all take ZW, mechanism-2, or
avoid MATCH_ASSIGN_SAVE in the unframed corner).
