# HANDOFF — SNOBOL4-BB — GROUND-ZERO REPRIORITIZE (Opus 4.8, 2026-06-08)

## TL;DR
- **PLANNING / REPRIORITIZATION session — NO SCRIP code written.** Only `.github/GOAL-SNOBOL4-BB.md` changed (watermark + 3 priority/scope edits).
- Lon directive: move pattern-building-through-RT-functions to the **TOP** of the GOAL as #1; ground zero **EXCLUDES all BB_INVARIANT/REF_INVARIANT optimizations**.
- Gates at floor, no regression: smoke **7/7/7** · pat-rung **M4 19/19, M2/M3 18/19** (053) · corpus **M2 184 / M3 161 / M4 155** of 280 · fence HARD. SCRIP `origin/main` unchanged.
- **NEXT: D7-RB-1, start with LIT.**

## The parity break (diagnosed + verified this session)
- B7 nullary (REM/FAIL/SUCCEED/ARB) and 053 work in **m4 only** — EMPTY in m2 and m3 (probe `P=REM` → `CDEF` m4, empty m2/m3).
- Cause: the generic RT build/stitch fns **exist** — `rt_pattern_build` / `rt_pattern_stitch_cat` / `rt_pattern_stitch_alt` at `src/runtime/pattern_match.c:748/756/762` — but **ZERO `bb_pattern_*.cpp` builders call them.** All 8 still inline copy/fill/patch as `ins*` text-only (counts: unary_s 116, unary_i 37, lit 30, nullary 25, arb 24, alt 19, dtp_assign 19, cat 13 = 283). `ins*` has no binary encoding (→ m3 empty) and there is no m2 build arm (→ m2 empty). Same root cause for 053.

## Scope — HARDENED, verified by code-read (do NOT re-derive)
- **`bb_match_*` is the crib.** All 23 `bb_match_*.cpp` are `ins*`-FREE pure `x86()` and pass m3 18/19 → the matching logic is already binary-encodable.
- **Encoders mostly EXIST:** the disp32 lea/load/store BINARY arms ARE present (`x86_asm.h` 348–366) — the recipe's "step-0: add `lea reg,[reg+disp32]`" is **STALE, do NOT re-add.** `x86_movzx_subj_byte` (158) / `x86_load_indexed8` (394) / `XK_MEMIDX8` / `movzx` dispatch (605) all present.
- **r12-SIB trap:** the GENERIC disp32 path omits the SIB byte → mis-encodes `[r12+off]`/`[rsp+off]`. A SIB-correct r12-frame family exists (`x86_r12_modrm` emits 0x24; `FR`/`FRQ`, lines 289–343). Converted builders MUST address the ζ frame via `FR`/`FRQ`, never raw `[r12+N]` through disp32 — `bb_match_*` already does exactly this.
- **Only genuinely NEW encoder work:** parameterize the index register in the membership-scan helpers (`x86_movzx_subj_byte` hardcodes `[r13+rcx]`; builders diverged to `r9`) OR align the builders to `rcx` like `bb_match_*`.

## Per-builder conversion shape (D7-RB-1 → RB-2)
1. **Machinery** (copy/fill/patch) → `marshal regs → call rt_pattern_*`.
2. **Proto α/β body** → keep as PIC data; rewrite the `ins*` to MIRROR `bb_match_*`'s `x86()` forms.
3. **m2 arm** — `IR_interp.c` case per build kind calling the same `rt_*` fn (this is what makes m2 match m3/m4).
4. **Zero BB_INVARIANT** — 12 refs still live across `emit_bb.c · lower.c · IR_interp.c · IR.h · prove_lower.c`; retire reliance as builders cover each shape.

## NEXT — D7-RB-1, start with LIT (trivial proto body; validates the whole mechanism)
`bb_pattern_lit.cpp`: label proto sites (`.Ls/.La/.Lg/.Lw/.Lop1/.Le`); emit a `DTP_PROTO_DESC` data blob; replace the copy/fill/patch `ins*` with `marshal regs → call rt_pattern_build`; add the `IR_interp.c` `IR_PATTERN_LIT` case calling the same fn; `emit_bb.c` FILL marshals proto/desc/operand regs. PROVE a LIT pattern across **m2==m3==m4**. Then ALT + DTP_ASSIGN (→ 053/050/051 → `b`/`dog`/`banana` parity), then **D7-RB-2** (unary_i/unary_s/nullary/arb/cat box-by-box, frag held 3-field/24B, `ins*` in pattern builders → 0), then **D7-RB-3** (the `P=LEN(3)` value-assign lowering gap — unrouted in all modes). FINAL: coordinated frag-widening → first-class β (closes B9).

## GATE (replaces the mode-4-only stance — Lon: "modes 3 and 4 are IDENTICAL")
smoke 7/7/7 · pat-rung **m2==m3==m4** (053 included, no SKIP) · corpus non-decreasing in all three modes · fence HARD.

## Session Setup
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64   # oracle: /home/claude/x64/bin/sbl -b file.sno
```
Gates (run all three modes):
```bash
bash scripts/test_smoke_snobol4.sh                               # 7/7/7
bash scripts/test_snobol4_pat_rung_suite.sh                      # M4 19/19; M2/M3 18/19 (053 is the parity target)
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh  # M2 184 / M3 161 / M4 155 floors
bash scripts/test_gate_sno_pat_reg.sh                            # fence HARD
```

— Opus 4.8, co-dev. GATE: m2==m3==m4.
