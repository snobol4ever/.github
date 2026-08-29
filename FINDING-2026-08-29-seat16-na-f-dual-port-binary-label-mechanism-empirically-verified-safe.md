# FINDING — hq_P's dual-port ruling (bb-label-prefix-uniform): the BINARY-mode label mechanism handles two independent same-address labels correctly. Empirically verified, not just read.

**Seat:** seat16 · **Date:** 2026-08-29 · **Row:** `bb-label-prefix-uniform`

## THE OPEN QUESTION

hq_P's ruling (QA `hq_P·2026-08-29c`) proposes curing `na_f`'s dual γ/ω role by emitting **both**
greek-suffixed labels at the same instruction address (no code between them), rather than a rename or a
two-pass resolver. hq_P flagged this explicitly as **unverified**: *"BINARY mode is: labels are
name→offset records (`x86_Lrec`, `x86_asm.h:78`) — two records emitted back-to-back with no code between
*should* land on one offset by construction, but this has NOT been run. If the binary label table rejects
a duplicate offset, or any consumer assumes offset→name is 1:1 — BOTH-MEDIA MANDATORY makes that a real
blocker, not a detail — report back."*

seat11 (same day) did a reading-level trace of `bb_label_t`/`bb_patch_t` and called it "a reading-level
plausibility check, not the empirical BINARY-mode test the ruling explicitly demands" — and explicitly
declined to run it, citing the row's own "~10x rework in the wrong direction" risk class on foundational
7-language shared code.

## WHAT WAS DONE — AN ACTUAL EMPIRICAL RUN, ZERO SHARED FILES TOUCHED

Traced the full consumer chain first (`x86_asm.h:2487`'s `'D'`-record dispatch → `bb_label_define` →
`emit.cpp:255`), which shows structurally why this should work: each `bb_label_t` is an independent
struct with its own `offset` field (never a shared offset-keyed table), and `bb_emit_patch_rel32`/
`bb_label_define`'s patch-resolution loop matches patches to labels **by pointer** (`p->label != lbl`),
never by offset. There is no code path that could reject or misresolve a duplicate offset.

Rather than stop at the trace (which is what "reading-level plausibility" already was), wrote a standalone
probe (`/tmp/.../dual_label_probe.cpp`, not committed anywhere — pure scratch) that **links against the
real, already-built `out/libscrip_rt.so`** (`bb_label_define`, `bb_emit_patch_rel32`, `bb_emit_buf`,
`bb_emit_pos`, `bb_patch_list` are all exported symbols — confirmed via `nm -D`) and exercises the
**actual production functions**, not a reimplementation:

1. Two independent `bb_label_t` structs (`test_a`, `test_b`), both `BB_LABEL_UNRESOLVED`.
2. Two separate `bb_emit_patch_rel32()` calls at two different code sites, each referencing its own label,
   registered **before** either label is defined (so both go through the real unresolved-patch path).
3. `bb_label_define(&test_a); bb_label_define(&test_b);` back-to-back, zero bytes emitted between them —
   exactly hq_P's proposed mechanism.
4. Read back both patched `rel32` displacements and independently computed what address each resolves to.

**Result, actual run output:**
```
shared_offset=58
test_a.offset=58  test_b.offset=58  (equal: YES)
site_a: reloc@17 disp=37 -> resolves to offset 58 (expected 58) : PASS
site_b: reloc@46 disp=8 -> resolves to offset 58 (expected 58) : PASS
OVERALL: PASS
```

Both labels received the identical offset. Both independently-registered patches (each computed at a
different site, against a different label pointer, before either label existed) resolved to the exact
correct, shared address. No modification to any tracked file was needed or made — the probe is pure
scratch space, linked against the pre-existing build.

## ANSWER TO HQ_P'S EXACT QUESTION

**No, the binary label table does not reject a duplicate offset, and no consumer assumes offset→name is
1:1.** There is no offset-keyed table at all — resolution is entirely pointer-based, per-patch. **Option
(C) from hq_P's ruling ("emit both greek-suffixed labels at the same address") is confirmed mechanically
safe at the label/patch layer.** This specific risk, the one the ruling was gated on, is cleared.

## WHAT THIS DOES NOT ANSWER — NOT ATTEMPTED, NOT THIS PASS

The actual **implementation** is unchanged in scope and risk from every prior session's assessment: per
seat11's own trace, `emit.cpp:3077`/`:3093`'s `node_γ`/`node_ω` ternary today hands out `na_f[k]` as
**either** role, never both — making a graph where `gamma_is_phi && omega_is_phi` are simultaneously true
for the same `na_f[k]` requires that site (and unenumerated siblings — `ra_y`/`ra_t`/`fc_sig` mint
similarly, per the `hq_P·2026-08-29` QA entry) to hand out **two** label pointers, not one. That is real,
non-mechanical logic work on foundational 7-language shared code (`emit.cpp`), and it still owes the row's
own standing **SHARED-NODE verdict scope** (SNOBOL4 1299+/1299+ both modes FAIL=0, plus icon/prolog/raku/
snocone/rebus/polyglot control arms) before landing — this FINDING does not shrink that bar, only removes
one specific, previously-open uncertainty about whether the underlying mechanism could work at all.

## DISPOSITION

Not implementing here — this row's own standing discipline (every session to date) treats emission-logic
changes to `emit.cpp`/`x86_asm.h` as needing dedicated focus, not a same-pass addition after an unrelated
verification spike. Routing back to the task file's `## NEXT` and messaging hq_P directly, since this
answers the explicit gate their own ruling set before implementation could proceed.
