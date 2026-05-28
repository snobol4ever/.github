# HANDOFF 2026-05-28 Opus 4.7 — SBL-EP-BINARY ✅

**Goal:** GOAL-SNOBOL4-BB.md / M3-NATIVE-4 — "Get MEDIUM_BINARY working for all opcodes."

**Commit:** one4all `1bc53211`.

---

## What landed

A universal EP→BINARY emitter for the **combinator** family of BB templates. Combinators
(ALT, CAT, FENCE, PL_SEQ, PL_ITE, SUCCEED) have always been driven from `emit_bb.c`'s
flat drivers — the driver mints labels, recursively walks children, then stuffs
**epilogue glue** (label-defs + jmp insns) into `g_emit.xa_bb_ep_*[]` arrays for the
combinator template to replay. In TEXT mode the template walked the arrays and emitted
`label:\n` and `jmp tgt`. In BINARY mode the templates returned `std::string()` — zero
bytes. Mode-3 native flat-wire would have emitted no glue between children, so the bug
was latent (mode-3 fell back to the C interpreter for non-trivial patterns).

This session added `ep_bin_fill_str(bin, prelude_lbl)` in `src/emitter/emit_str.{cpp,h}`.
It walks the same EP arrays the TEXT arms walk and produces bytes + `bb_bin_t.sites/labels/is_def`.
Each `xa_bb_ep_define[i]` becomes a zero-width define-site at the current byte offset;
each `xa_bb_ep_jmp[i]` emits `\xE9 + u32le(0)` (5 bytes) and records a rel32 patch
site at offset+1 pointing at the target label.

To make the helper possible, `xa_bb_ep_define[]` / `xa_bb_ep_jmp[]` were retyped from
`const char *` to `bb_label_t *` — BINARY needs the label pointer to call
`bb_label_define` / `bb_emit_patch_rel32`. TEXT just derefs `->name`. The EP_DEF /
EP_JMP / EP_DEF_JMP macros in emit_bb.c were updated to store the label, not the name.

### Converted (audit REAL)

| Template | Notes |
|----------|-------|
| `bb_pat_alt` | Pure EP. No prelude. |
| `bb_pat_cat` | Pure EP. No prelude. |
| `bb_pat_fence` | Both 0-child and N-child cases unified through `ep_bin_fill_str`. Old hardcoded 10-byte arm `{sites:1,5,6}` lacked the α-define site. 0-child synthesises the same `lbl_α: jmp γ ; lbl_β: jmp ω` shape by populating EP locally then restoring `xa_bb_ep_n=0`. |
| `bb_pl_seq` | Pure EP. No prelude. |
| `bb_pl_ite` | Pure EP (β-tombstone via EP). No prelude. |
| `bb_succeed` | EP with α prelude (`_.lbl_α_p` defined at offset 0). |

### Bombed (audit BOMB, was silent EMPTY)

| Template | Why |
|----------|-----|
| `bb_pl_alt`    | TEXT emits `call rt_pl_trail_mark_push@PLT` + `jmp prei` per clause + chained `rt_pl_trail_unwind_top` — procedural, not EP-driven. Needs dedicated BINARY port if mode-3 Prolog native is ever scoped. Until then: bomb loud, never silent zero bytes. |
| `bb_pl_call`   | TEXT emits compound-term builds (`build_arg`) + `pl_bb_env_save_push` + redo block. Procedural. |
| `bb_pl_choice` | TEXT emits CP push/pop dispatch with cursor/N comparison. Procedural. |

### Audit

`scripts/audit_m3_native_binary_arms.sh`: added `ep_bin_fill_str` to the `has_real`
regex so EP-driven arms are correctly classified REAL (was: EMPTY/COMMENT because the
heuristic only matched literal byte producers).

---

## Gates

| Gate | Result |
|------|--------|
| GATE-1 smoke (default) | 13/13 |
| GATE-1 smoke (SCRIP_M3_NATIVE=1) | 13/13 |
| GATE-2 broker | 31 |
| GATE-3 mode-4 corpus | 175/280 |
| GATE-4 mode-2 corpus | 238/280 |
| NATIVE corpus | 165/280 (unchanged — see "Why no climb" below) |
| Rung suite | M2=19 M4=15 SKIP=0 |
| Prolog smoke / mode-4 rung / BB honest | 5/5 / 4/4 / 128/0 |
| Raku smoke | 5/5 |
| FACT RULE | 0 |
| audit_m3_native | GATE OK |

### Why no native corpus climb

The new BINARY arms are **plumbed but not yet driven** in mode-3. `M3-NATIVE-3` (Sonnet
4.6, `910d55c3`) wired single-leaf BB call-out (ANY) — `bb_build_flat` is invoked for
those. Combinator nodes (ALT/CAT/etc.) don't yet route through `bb_build_flat` on the
mode-3 sealed-RX path. The bytes are ready; the build path needs the extension.

This was the right division: get the byte-producers right first, audit them as REAL,
then in the next rung wire them up. If I'd inverted the order I'd have been chasing
shape mismatches in the flat-driver while also debugging the templates.

---

## Files touched

```
scripts/audit_m3_native_binary_arms.sh
src/emitter/BB_templates/bb_pat_alt.cpp
src/emitter/BB_templates/bb_pat_cat.cpp
src/emitter/BB_templates/bb_pat_fence.cpp
src/emitter/BB_templates/bb_pl_alt.cpp
src/emitter/BB_templates/bb_pl_call.cpp
src/emitter/BB_templates/bb_pl_choice.cpp
src/emitter/BB_templates/bb_pl_ite.cpp
src/emitter/BB_templates/bb_pl_seq.cpp
src/emitter/BB_templates/bb_succeed.cpp
src/emitter/emit_bb.c
src/emitter/emit_globals.h
src/emitter/emit_str.cpp
src/emitter/emit_str.h
```

14 files, +96 / -46.

---

## Next session

1. **Wire combinator flat-build for mode-3.** Extend `bb_build_flat` (or the mode-3
   sealed-RX builder that today calls it for leaf patterns) to descend through ALT /
   CAT / FENCE / SUCCEED nodes — invoking the flat driver, which fills EP, which then
   feeds `ep_bin_fill_str` to produce the glue bytes. Then run the native corpus and
   collect the climb (FENCE ~6 + ALT ~6 should fall first).

2. **SBL-SPAN-2 / SBL-ARBNO-3 / SBL-BREAKX-2** — three remaining bombed leaf BB
   templates. The `cap_alloc_saved_delta_slot()` deque-int pattern from SBL-CAP-2 is
   the GC-safe scratch facility. Each is its own per-template BINARY port.

3. **Procedural Prolog (PL_ALT / PL_CALL / PL_CHOICE) BINARY ports** — only if
   mode-3 Prolog native is scoped. Today these bomb, which is correct.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus
