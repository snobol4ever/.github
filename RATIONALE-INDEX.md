# RATIONALE-INDEX — symbol/function -> recovered design rationale

**What this is.** `e25a5daf` (2026-08-20, GOAL-STYLE-200COL REACTIVATION 4) stripped 6,919 comments across 162 files enforcing the C style rule (RULES.md: 200-char lines, zero blank lines, exactly one comment form). Most of that was decoration; a real fraction was the project's hardest-won measured rationale — the only record of *why* a piece of code refuses the case it refuses. RULES.md's comment restriction is not being relitigated (do not put prose back in the source); this index is the promised alternative home: an "indexed appendix" mapping a symbol name to wherever its rationale now lives, so a session grep on the *symbol* finds the doc instead of needing to know a doc exists first. See `.github/FINDING-2026-08-22-recover-stripped-design-rationale-classification.md` for the recovery methodology and counts.

**How to use this file.** Looking for "why does X do Y": `grep -n "^- \`X\`" .github/RATIONALE-INDEX.md`. Adding a new relocation: append one line per symbol it covers, pointing at the doc (ARCH file, FINDING, or this file's own inline section for something too small to deserve a standalone doc).

## Index

- `sn4_blob_choice_scan` -> `.github/ARCH-ENGINE.md` §3.2
- `resume_carrier_ok` -> `.github/ARCH-ENGINE.md` §3.3 (the seat04 cluster: tier-3 admission, `lf`/`fn`/`nc` witnesses)
- `blob_choice_rbp_scan` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_choice_rbp_off` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_alt_carrier` -> `.github/ARCH-ENGINE.md` §3.1
- `blob_frame_bytes` -> `.github/ARCH-ENGINE.md` §3.5
- `zdp_tier` / ZDP lattice (`zeta_depth.c`/`.h`) -> `.github/ARCH-ENGINE.md` §3.6 (⛔ verified NOT the live admission path for the choice-carrier decisions as of the recovery commit — re-verify before trusting either way)

### `src/templates/x86/x86_asm.h` — the sole `x86(...)` encoder (relocated hq_P 2026-09-11, row `rationale-x86-asm-h`)

- `x86_tabs_on` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (TAB RECORD: tab-delimited fields, occupancy-keyed `x86_rec_kind`, `SCRIP_ASM_TABS=0` killswitch)
- `x86_rec` -> `.github/ARCH-X86-ASM-ENCODER.md` §2
- `x86_rec_kind` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (⛔ keys off FIELD OCCUPANCY, never off text)
- `x86_rec_split` -> `.github/ARCH-X86-ASM-ENCODER.md` §2 (the no-TAB legacy fallthrough — additive, not a cutover)
- `x86_rtcc_wb_bin` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (writeback order; R11 restored last in BINARY only)
- `x86_rtcc_rl_bin` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (PARTIAL RELOAD: scratch tier only — arg-tier reload would restore BSS zero over the return value)
- `x86_rtcc_wb_text` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (rip-addressed slots: the "R11 last" constraint does NOT apply in TEXT)
- `x86_rtcc_rl_text` -> `.github/ARCH-X86-ASM-ENCODER.md` §1
- `x86_rtcc_call` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (void/int/ptr form; CLASS N decline)
- `x86_rtcc_call_descr` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (⛔ RETURN-BEFORE-RELOAD LAW — capture RAX:RDX before reload or read a stale VM global as the return value)
- `x86_rtcc_clob` / `x86_rtcc_clob_raw` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (per-CALLEE decline, not a per-op filter)
- `x86_rtcc_live_mask` / `x86_rtcc_veneer_mask` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`SCRIP_RTCC_VENEER`; R9 dropped when `gva_count()==0`)
- `rtccb` / `RTCC_SLOT_R9` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (slot-offset table; ⛔ H2 — the R9/GVA slot is deliberately NOT written back, and skipping the store is what makes the documented BLOCK-CANONICAL EXCEPTION true)
- `GVARQ` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`RC-5-GVA` disp8 form, 4B vs 7B for `ABSQ`)
- `rtcc_anchor_cmp` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (`RC-5-ANCHOR`: `test r8, r8`, 3 bytes, identical ZF semantics)
- `RTCC_GLOBAL_R8_ANCHOR` / `RTCC_GLOBAL_R9_GVA` -> `.github/ARCH-X86-ASM-ENCODER.md` §1 (⛔⭐ the `s11` defect: duplicated unguarded macros + tree-wide `-w` meant no `-D` reached the emitter, and TWO GRADED RUNGS were decided on arms that were the same binary)
- ⛔ `x86_rtcc_writeback` / `x86_rtcc_reload` -> **names no longer exist**; see `.github/ARCH-X86-ASM-ENCODER.md` §1 last subsection (superseded by the `_bin`/`_text` medium split)

## Remaining clusters, not yet relocated (see QUEUE.tsv / tasks/ for the dispatched rows)

Ranked by stripped-RATIONALE-comment count (heuristic classifier, see the FINDING above for the caveat that this is a lower bound):

| rank | file | stripped RATIONALE (est.) | queue row |
|---|---|---|---|
| 1 | `src/emitter/emit.cpp` (remainder, beyond §3 above) | ~600 | `rationale-emit-cpp-remainder` |
| ~~2~~ | `src/templates/x86/x86_asm.h` (⭐ path moved; **RC-4/RC-5 + TAB RECORD relocated 2026-09-11** -> `ARCH-X86-ASM-ENCODER.md`) | 186 blocks recovered, ~20 relocated | `rationale-x86-asm-h` ✅ CLOSED · remainder row `rationale-x86-asm-h-objnote-remainder` |
| 3 | `src/lower/lower_snobol4.c` | 232 | `rationale-lower-snobol4-c` |
| 4 | `src/contracts/zeta_storage.c` | 132 | `rationale-zeta-storage-c` |
| 5 | `src/emitter/emit.h` | 119 | `rationale-emit-h` |
| 6 | `src/runtime/rt/rt.c` | 106 | `rationale-rt-c` |
| 7 | `src/driver/scrip.c` | 105 | `rationale-scrip-c` |
| 8 | `src/templates/bb_call_proc_staged.cpp` | 81 | `rationale-bb-call-proc-staged` |

Each row's baton carries the file, the recovery method (`scripts/` extraction under `/tmp/.../scratchpad/rationale/` this session — not yet promoted to a checked-in script; see the FINDING), and the same DECORATION/RATIONALE split instructions as this row. Row-factory rule carried forward: a session picking one of these should relocate its highest-value sub-cluster and spin off further rows rather than trying to clear an entire file's ~100-600 comments in one sitting.

⚠️ **Two of this table's provenance links are now DEAD, for two different and both legitimate reasons (found by hq_P 2026-09-11 while working row 2).** `FINDING-2026-08-22-recover-stripped-design-rationale-classification.md` — the methodology file every one of these rows names as a prerequisite — was removed by `f78d8b3f` under Lon's 2026-09-04 order *"Remove old FINDING-\*.md files"* (826 August FINDINGs), and `ARCH-PATTERN-CHOICE-CARRIER.md`, the worked precedent, was folded into `ARCH-ENGINE.md` by `9e0e624a`. ⛔ **The remaining rows in this table still cite both in their batons.** Neither loss is an error — but a row whose STEP 2 says *"read the parent FINDING before trusting a DECORATION verdict"* now names a file nobody can open, and **a prerequisite nobody can satisfy is either a blocker or a dead letter.** ⭐ **What survives is enough:** this file's own header carries the methodology summary, and `ARCH-ENGINE.md` §3 is the live precedent shape. Use those.
