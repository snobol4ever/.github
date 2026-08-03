# FINDING 2026-08-02h — the ZW5 per-depth ladder wedged 067, ZD_MATCH is exonerated, and the ruled RBP bracket ALREADY EXISTS in-tree as STF

**Seat:** observer (third session, Lon-directed). **SCRIP commit:** `542776a5` (SCRIP_ZW5 default OFF). **Supersedes the attribution in `FINDING-2026-08-02g` — ALPHA's LIT admission was the TRIGGER, not the defect.**

## 1. The bracket (gdb attach, not the monitor — the hang is post-output)
067 under defaults prints the CORRECT output "both correct" once, then hangs (rc=124 after the print). gdb attach to the live process: `#0 _IO_new_file_overflow(f=0x1eb51990, ch=<garbage>)` ← `#1 output_val io_format.c:13` ← `#2 NV_SET_fn(name="OUTPUT") core.c:2222` ← `#3 emitted code` ← `#4 0x0000000c00000002` — frame 4's "return address" is adjacent data words, i.e. **the emitted code entered the runtime with rsp mispositioned**; the second traversal wedges inside stdio on a garbage FILE. One output line in the file disproves a re-print loop; the wedge is a claim/release imbalance downstream of the armed statement.

## 2. The bisect that exonerates ALPHA
`SCRIP_ZD_MATCH=0` cures (2026-08-02g's variable) — but **`SCRIP_ZW5=0` ALSO cures with `ZD_MATCH=1`** (rc=0, correct output). The 2026-08-02g bisect variable gated the POPULATION on which zw5's wpop-steal fires; the defect is in the zw5 machinery (emit.cpp ~2195–2203 pool mint, ~2510–2520 wpop steal + stub bodies). LIT admission widened zw5's reach onto 067's statements and exposed it. ALPHA owes nothing on 067.

## 3. The mess, quantified (roman.s, benchmarks, pre-flip artifact)
100 `*_zw5s*_ω_d*` per-depth stubs (`add rsp,K; jmp …` ladder). 107 `_β:` labels, only 38 ever jumped to — ~69 dead β trampolines (witness `n5_lit_string_β`, a box that never backtracks).

## 4. THE DESIGN LON RULED ALREADY EXISTS — STF
`flat_stmt_frame` is the RBP statement bracket, complete and law-documented: ZGPOP-STF at emit.cpp:836 ("fail edge = bracket cut; ZERO hand-counted pops"; "mov rsp,rbp reclaims EVERY statement/BB carve at any depth" — seed `seed/test_sno_stmt_frame_1.s`); head stubs st_pre/st_x ~2275/2350 (`bb_glue_framed_enter/leave`); chain-exit cuts 2581; edge retarget 2499 ("inline pops become DEAD-BUT-HARMLESS"). **WHY the ladder was born beside it:** the gate at 2827 excludes `flat_pat` graphs, and zws (2004) excludes STF graphs to avoid nesting two rbp disciplines — so O-2 built parallel per-depth machinery for exactly the population STF declines, instead of extending STF to it.

## 5. Landed (this seat) + gates run
`SCRIP_ZW5` default OFF (`542776a5`), `=1` preserved for archaeology. Gates: 067 green in default env; crosscheck patterns dir m3 = PASS 107 / FAIL 15 / TIMEOUT 0 (fails are the pre-existing segv baseline class); 164 (O-2's one claimed m3-visible relative) verdict equal both regimes. **OWED next session (context-bounded seat):** full 318 both modes + bench board + regen ×4 — the flip is O-2's own certified byte-identical revert, so exposure is bounded to O-2's m4-only 164 delta.

## 6. THE RULED FIX (Lon 2026-08-02) — hours, not days
1. Extend the rbp statement bracket to the armed-pattern population zw5 covered: pin at statement head (`bb_glue_framed_enter`), cut at BOTH exits (γ success WHACK FREE and ω fail-at-any-depth) via `bb_glue_framed_leave` — the existing encoders, both media already.
2. Reconcile with zws: ONE rbp discipline per statement. Either the match frame nests (push/pop is naturally reentrant) or its 56-byte slot block absorbs into the statement bracket — needs Lon's ruling, it is the only open design point.
3. Delete the zw5 pool outright once covered (grep `_zw5` → 0).
4. β hygiene: emit a box's β define ONLY when referenced — compute a referenced-bit over the betas[] wiring (flat_drive_match_alt resume edges, FIX-1 blob-leaf→MATCH_BEGIN.β wires, DRIVE_PAIR consumers) and gate `DRIVE_PAIR_DEF_JMP`. ~69 dead labels in roman today.
