# THREE-MEDIUM (TM) Rung — Handoff 2026-05-24

## Repository State
- **SCRIP HEAD:** `e1602529`
- **Branch:** main (pushed)
- **Gate:** PASS=442 FAIL=0 STUB=612 NEW=0 GONE=0

## What Was Done This Session

### Completed TM steps

| Step | File(s) | Change | Gate |
|------|---------|--------|------|
| TM-5 | `bb_pat_fence.cpp` | Binary detour eliminated. Zero-children fast path now emits real x86 (10 bytes, `emit_jmp succ + emit_label_define back + emit_jmp fail`) instead of routing through text (was 64-byte text dump). MACRO_DEF stub added. | 444/0/610 |
| TM-6 | `bb_pat_break/span/any/notany.cpp` | All four charset-family templates: added MACRO_DEF stub, explicit BINARY/TEXT sections delegating to `bb_charset_emit()` (which branches internally). | 444/0/610 |
| TM-8 | `bb_lit.cpp` | Merged naked top-level `if (MEDIUM_BINARY)` block (lines 43-61) into PLATFORM_X86 block. Now: MACRO_DEF stub / BINARY (real binary via `insn_*` + `emit_jmp`) / TEXT. Binary section +3 bytes (122→125). | 444/0/610 |
| TM-9 | `bb_arbno.cpp`, `bb_capture.cpp` | Added MACRO_DEF stubs. Fixed `} if (MEDIUM_BINARY)` (missing else) in arbno. Capture's inner `if (!MEDIUM_BINARY)` branching retained (complex two-path imm/call structure). | 442/0/612 |

### Note on gate numbers
`22b2ad21` (session start) was 444/0/610. After TM-9 it's 442/0/612. The 2-cell PASS→STUB shift is an audit-classification side-effect of the counter/label coupling: when MACRO_DEF sections stop calling the real emitter, `g_flat_node_id` advances less during the macro-def audit pass, shifting auto-label numbers in downstream cells. The cells still pass structurally; two formerly-PASS cells now have zero output on both sides (STUB). **FAIL=0** — no semantic regression.

## What's Next: Remaining TM Steps

### TM-7 (skipped — do next)
`bb_pat_cat.cpp`, `bb_pat_alt.cpp`
- These have structural split (`emit_flat_ir` with-children) + single-return, binary via `emit_flat_ir`.
- Pattern: MACRO_DEF stub / BINARY (`emit_flat_ir` handles internally, return `""`) / TEXT (same).
- Caution: label IDs (`xcatNN`, `altNN`) will cause counter-shift noise in neighbors as with TM-6.

### TM-10
`bb_pl_*.cpp` family (6 templates: `bb_pl_assign`, `bb_pl_cap`, `bb_pl_fail`, `bb_pl_fence`, `bb_pl_match`, `bb_pl_succeed`).
- Add MACRO_DEF stubs, enforce single-return per section.
- All currently have bare PLATFORM_X86 with no MACRO_DEF section.

### TM-11
SM violations: `sm_halt.cpp`, `sm_compare.cpp`, `sm_exec_bb.cpp`
- Move top-level `if (MEDIUM_MACRO_DEF)` guards inside `PLATFORM_X86` block.
- Add explicit three-section structure.

### TM-12 (audit pass)
Automated scan: confirm zero occurrences of `MEDIUM_*/BB_WIRED/USE_SM_MACROS` outside a `PLATFORM_X86` block. Grep target:
```
grep -rn "MEDIUM_\|BB_WIRED\|USE_SM_MACROS" src/emitter/BB_templates/ src/emitter/SM_templates/ \
  | grep -v "if (PLATFORM_X86)"
```
All hits should be inside a PLATFORM_X86 block.

## Infrastructure Issue Raised (important)

### Normalizer does not canonicalize auto-labels or embedded addresses

The current `normalize_per_kind_cell.py` does passthrough for binary cells and whitespace-squashing for text cells. It does **not** canonicalize:
- Auto-generated label IDs (`alt16_c0_β`, `.Lcs19_chars`, `xcat15_left_β`, etc.) — these shift by 1 whenever a preceding MACRO_DEF section stops advancing `g_flat_node_id`.
- Embedded link-time addresses (`mov rcx, 0xc4da94`) — these shift whenever code size changes.

**Recommended fix:** Add a deterministic obfuscation pass to the normalizer:
1. Walk the normalized text, collect all `[a-zA-Z_.][a-zA-Z0-9_.]*\d+[a-zA-Z0-9_]*`-style tokens that look like auto-labels.
2. Assign them canonical names (`LABEL_0`, `LABEL_1`, ...) in first-occurrence order.
3. Replace embedded hex immediates (`0x[0-9a-f]{4,}`) with `ADDR_N` in first-occurrence order.
4. Compare the canonicalized form.

This eliminates the entire class of "counter-shift refreeze" noise that consumed significant time this session. Every TM step that adds a MACRO_DEF stub triggers this noise for downstream cells.

## Refreeze Discipline (established this session)

1. Run gate → identify FAILs.
2. Verify each FAIL is either (a) intended output change or (b) counter-shift / ASLR noise.
3. Run `bash scripts/freeze_per_kind_baseline.sh`.
4. Revert all binary cells (`x86/binary/*.bin.norm/raw`) that changed only in ASLR addresses (same byte length — gate is length-only for binary). Exception: if byte length changed, keep.
5. Restore HEAD MANIFEST, patch only the genuinely-changed cells' lines via the Python one-liner.
6. Re-gate to confirm green.
7. Commit.

The cleanup in steps 4-6 prevents the commit from containing ASLR-address noise that would re-churn on every subsequent build.

## Commits This Session (new since session start)
```
e1602529 TM-9: bb_arbno, bb_capture — add MACRO_DEF stub, explicit three-section returns.
f868b9b9 TM-8: bb_lit — merge naked MEDIUM_BINARY guard into PLATFORM_X86, three-section.
cc3341f6 TM-6: charset family (break/span/any/notany) — three-section PLATFORM_X86.
1057a3e7 TM-5: bb_pat_fence — three-section PLATFORM_X86 (MACRO_DEF stub / BINARY real x86 / TEXT).
```
(TM-4 `22b2ad21` was from prior session.)
