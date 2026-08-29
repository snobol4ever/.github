# FINDING — 2026-08-29 (seat08) · THE s193 DISCRIMINATING PAIRS WENT INERT TOO — `leafsib` IS NOW 12/12 GREEN ON BOTH `SCRIP_SPAN_FRAME` ARMS

**Row:** `corpus-crosscheck-probe-total-conversion` (clause 3, `leafsib` slice). **Disposition: MEASURED AND
FLAGGED, NOT ROOT-CAUSED — out of this row's lane (corpus format conversion, not frame codegen).** Converting
`probe/leafsib` to suite format required re-verifying its live regression-instrument claim first; the claim
measures FALSE at HEAD.

**Tree:** measured pre-pull (SCRIP `dc817e01`) and re-measured on a fresh `make pristine` binary at SCRIP
`7817f370` after pulling 3 commits (`32a2d9df`, `73e567d3`, and the icon-N2 transitive-reserve landing) — none
touching `sn4_span_frame`/leaf-frame code; the one touched file, `emit.cpp`, changed only in Icon N-2
generator-frame territory (`codegen_flat_chain_body`, `g_last_flat_fp`). Both measurements agree. Oracle-pinned
`.ref` unchanged throughout (`id=iffoo`, all twelve).

---

## 1. WHAT s193 ESTABLISHED, AND WHAT IS DIFFERENT NOW

s193 (`FINDING-2026-08-20-s193-the-leafsib-set-went-inert-and-both-declines-outlived-their-refuser.md`) found the
original eight `leafsib` witnesses inert (byte-identical `--compile` output under both `SCRIP_SPAN_FRAME` arms)
but the four padded pairs minted that same session (`{arb,bal}_flat_{red,grn}`) still discriminating: **12/12
default (`=1`) · 10/12 under `=0`**, with `arb_flat_red`/`bal_flat_red` failing specifically at **m4 rc=139
(SIGSEGV)** under the OFF arm.

Re-measured 2026-08-29, `bash SCRIP/scripts/probe_leafsib_measure.sh` both with and without
`SCRIP_SPAN_FRAME=0`:

```
default (=1): m3 12/12   m4 12/12
=0           : m3 12/12   m4 12/12
```

**All twelve are green on both arms.** `arb_flat_red` and `bal_flat_red` — the two witnesses s193 minted
specifically because they still crashed under `=0` — no longer crash. Re-confirmed after conversion, against the
new `tests/snobol4/probe/leafsib.sno`/`.ref` suite via `corpus_suite_harness.py run --modes m3,m4` under both
arms: same result, `m3_pass=12 m4_pass=12` both times.

## 2. WHY THIS IS FLAGGED, NOT FIXED, AND NOT EVEN ROOT-CAUSED

This row is a corpus-format conversion (`corpus-crosscheck-probe-total-conversion`), not a frame-codegen
investigation. The `emit.cpp` diff pulled in during this sitting is confined to Icon N-2 generator-frame
registration (`codegen_flat_chain_body`'s `flat_gen` arm, `g_last_flat_fp`'s registry pairing) — nothing near
`sn4_span_frame()`, `leaf_frame_member()`, or the SNOBOL4 scratch-cell leaf road. Whatever fixed the OFF arm's
SIGSEGV did so **before** this pull, or via some other change already on `origin/main` pre-pull (the pre-pull
measurement at `dc817e01` already showed 12/12 both arms — this is not something the 3 pulled commits caused).
Given the family's own history (s173's "6/8 is not a cure," s193's "8/8 both arms is a dead instrument, not
success"), **12/12 both arms is exactly the shape that should NOT be assumed benign without checking whether the
instrument still discriminates anything at all** — and by the same test s193 used (diff the emitted `.s` across
the arm), it currently does not, for any of the twelve.

## 3. WHAT THIS MEANS FOR THE KILLSWITCH

`SCRIP_SPAN_FRAME` (`emit.cpp:2255`) is still live in source, still read by `leaf_frame_member()`
(`emit.cpp:2271`), and still the ONE arm this family was ever built to exercise. If no witness anywhere still
discriminates on it, it is a candidate for the same treatment `ZC_STORAGE`/`ZC_PORT` got under Lon's "ZETA HAS NO
MODES" ruling (2026-08-27, RULES.md) — a killswitch nobody's instrument can see is memory of a mode, not a live
configuration. **This is named as a candidate, not claimed as a ruling**: it would need its own census (does
ANYTHING in the corpus still discriminate on this arm — `cn_alt_leaf_flat_red`/`lit_red` were named as still-red
controls in s193's FINDING; unchecked here) before anyone acts on it. Out of this row's lane; flagging for
whoever owns `SCRIP_SPAN_FRAME`/frame-widening.

## 4. WHAT LANDED IN THIS ROW (see the conversion commit for the full account)

`corpus/probe/leafsib/` (12 `.sno`/`.ref` pairs + README) converted to
`corpus/tests/snobol4/probe/leafsib.{sno,ref}` (corpus-suites-consolidation format), byte-equal validated both
directions, both modes, **both `SCRIP_SPAN_FRAME` arms**, before the loose files were deleted.
`SCRIP/scripts/probe_leafsib_measure.sh` re-pointed to extract from the suite (same idiom as the `fz`/`retry`
re-points); full stdout captured before and after the re-point, both arms — byte-identical. The README moved
alongside the suite as `leafsib.README.md` with this finding appended; nothing in its s131/s173/s193 history was
edited, only marked historical where superseded.

## 5. GATES

`make pristine` EXIT=0 (SCRIP `7817f370`). `python3 corpus_suite_harness.py convert --modes m3,m4`: 12/12 OK,
on-disk re-validation passed both directions both modes. Independent second-pass `run --modes m3,m4`:
`m3_pass=12 m4_pass=12` both arms. `probe_leafsib_measure.sh` before/after re-point: byte-identical stdout, both
arms, exit 0 both times.

## 6. ⭐ GENERALISABLE

**"Both arms agree" can mean the defect is fixed, or that the instrument stopped watching — the two are
indistinguishable from the pass/fail count alone, and s193 already burned a session on exactly this ambiguity
once.** The only way to tell them apart is s193's own test, applied again: diff the emitted `.s` across the arm.
Not done here (out of lane) — this FINDING exists so the next seat who touches `SCRIP_SPAN_FRAME` does not have to
re-discover that the family went quiet a second time before deciding what it means.
