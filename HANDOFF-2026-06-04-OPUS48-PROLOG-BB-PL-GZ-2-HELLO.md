# HANDOFF — 2026-06-04 — Opus 4.8 — PROLOG-BB — PL-GZ-2 HELLO LANDED

## What landed
**PL-GZ-2 (hello, write/nl) — the first rung on the Proebsting-pure Byrd-Box path — SCRIP `de8c4ad`**
(one commit, rebased atop Lon's concurrent `b59c9e6` ICN-SCAN-13a; re-verified green post-rebase).
m2 == m3 == m4 stdout byte-identical (`hello\n`); m3 native via RX slab (no INTERP-FALLBACK banner);
m4 same bodies as `.s` → as → gcc+libscrip_rt. ONE x86() body per box served BOTH mediums.

## Architecture (the decisions future rungs inherit)
- **New IR kinds at the end of the Prolog block** (`IR.h`): `IR_QUERY_FRAME`, `IR_DET_WRITE`, `IR_DET_NL`
  (+ names in `scrip_ir.c`). The **m2 oracle never sees them**: `pl_gz_admit` (driver, scrip.c, beside
  `pl_flat_body_root`) is a driver-side graph REWRITE — admit the hello class (zero slots, single GCONJ
  or lone SUCCEED of write(ATOM|LIT_I)/nl/SUCCEED, no GOAL/CHOICE/UNIFY/CUT/DISJ/ITE/CATCH/ARITH/
  LOGICVAR/STRUCT) and return a fresh `IR_QUERY_FRAME` root whose α-chain (γ-linked) is the det goals;
  NULL = fall through to today's tiers untouched. Called FIRST by BOTH the mode-3 (~scrip.c flat branch)
  and mode-4 branches — the PL-M34 equal-sets LAW holds at the boundary by construction.
- **bb_query_frame.cpp — one box file, TWO aspects via `g_emit.op_sa`** (set by the drive; templates
  never read pBB): `op_sa==0` prologue = `push r12; mov r12,rdi` (ζ activation) + `rt_trail_mark` →
  `[ζ+0]` (frame row; `g_flat_slot_count=16` reserves it) + `jmp PORT_GAMMA` (body head). `op_sa==1`
  epilogue = `def PORT_GAMMA` → rax=1/pop/ret, `def PORT_OMEGA` → `rt_trail_unwind([ζ+0])`+rax=0/pop/ret.
  The epilogue DEFINES the landing labels the chain targets — verdict-in-rax per the seed ABI.
- **bb_det_write.cpp / bb_det_nl.cpp** — det VALUE calls (`rt_write_atom`/`rt_write_int`/`putchar`),
  atom operand sealed RO **in-box** via `x86_ro_seal_str` (`[rip+disp]` both mediums — BINARY seals the
  host pointer quad, fine in-process; TEXT emits `.quad`+`.string`). det β = own label, `jmp PORT_OMEGA`
  (det redo = fail, seed-correct). NO conj box: `flat_drive_gz_query` (emit_bb.c) is wiring only —
  per-goal α/β labels, goal_i.γ → goal_{i+1}.α, last → land_γ.
- **Consumers share the walk**: `pl_gz_build` (m3: bb_alloc/emitter_init_binary/walk_bb_flat/seal) and
  `pl_gz_codegen` (m4: emitter_init_text + `main_α` label + walk). GZ bypasses XA_FLAT_PROLOGUE/EPILOGUE
  entirely (those are SNOBOL-flavored: FAILDESCR 99). m4 shell = legacy flat shell minus env-alloc/strtab.
- **x86_asm.h**: added the missing `ret` encoder (zero-arg dispatcher) — one place, both mediums.

## Verification (all on the pushed `de8c4ad`)
- `scripts/test_gate_pl_gz2.sh` GREEN: hello probe byte-identical ×3, both took the new path (m3 stderr
  clean, m4 .s has `gzq` labels); non-admitted probe `X = a` declined identically (m3 LOUD marker, m4
  zero `gzq`). **Negative proven**: corrupted marker → gate exits 1; restored → green.
- GATE-1 unchanged 5/5 · 2/0/3-EXC · 5/5. GATE-3 unchanged 115/115 · 12/0/103-EXC · 105/0/10
  (hello rows moved flat-tier→gz-tier, same PASS). Coupling 19/10/others-0/rung05-39 (new files 0).
  One-box PASS · no_bb_bin_t PASS · no_vstack rc=0 (the 3 refs are the tracked baseline, none in new
  files). SNOBOL4 smoke 19/19. Icon 5/7+5/7 == pre-change HEAD (**stash-verified**, not assumed).
  Corpus clean.

## Gotchas hit (don't repeat)
- str_replace that consumes a function header in old_str must restore it in new_str (`flat_drive_conj`
  header got eaten once — file-scope parse explosion at distant lines was the symptom).
- Per-goal β labels are mandatory: passing one shared label as several boxes' β makes every
  `def PORT_BETA` redefine it.
- The Makefile lists template .cpp files TWICE (sources ~L164, compile rules ~L372); link is
  `$(OBJ)/*.o` wildcard, so two edits suffice.

## Next (in order, per GOAL-PROLOG-BB.md)
1. **PL-GZ-3 — facts + unify**: ground facts, head unify via the surviving bb_unify arms (var-const,
   var-var), EVERY binding trailed — extends `pl_gz_admit`'s class; the query-frame trail row is already
   live. 2. PL-GZ-4 — choice (THE seed-transcription rung). Also open: PL-GZ-1c FENCE sub-step (e)
   (delete the fallback) and CORPUS-S-HYGIENE (b) (needs Lon's keep-list).
