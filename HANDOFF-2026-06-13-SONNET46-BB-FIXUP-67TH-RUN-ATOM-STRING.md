# HANDOFF 2026-06-13 — BB-FIXUP 67th run (A→Z) — bb_atom_string.cpp 15→0 CLEAN

**Model:** Sonnet 4.6 (orientation/exec) · **Goal:** GOAL-BB-FIXUP-A-to-Z.md · **Lon:** attended ("What % … Continue" ×4)
**SCRIP landed:** `80dc1af` (verified on origin/main) · **.github:** this commit

## One ring stop
**bb_atom_string.cpp 15→0 CLEAN** — the 43rd-run [S] residue resolved (not a LOWER split; CV10 prep-relocation + both-medium unification).

### Five-file edit
1. **bb_atom_string.cpp** — regenerated whole.
2. **bb_common.h** — decl `bb_atom_string_str(const std::string&)` → `bb_atom_string()`.
3. **bb_resolve.cpp** — call site `bb_atom_string_str(hdr)` → `bb_atom_string()`.
4. **emit_bb.c** — IR_BUILTIN bb_prepare block: resolve call target (op_call_sym/op_call_fp by builtin name) + intern part labels (op_parts_lbl[0..3], placed AFTER the n>=2 str[3] population so char_type's inner arg gets a label).
5. **emit_globals.h** — sm_emit_t: NEW `op_call_sym` (const char*), `op_call_fp` (void*), `op_parts_lbl[16]` (const char*).

### Conversions applied
- **CV9** — dropped `hdr` param; `x86("label", _.lbl_α)` inlined in each of the 6 arm families.
- **BOTH-MEDIUM / CV10** — `bas_term`'s `MEDIUM_BINARY` + `x86_lit_bytes(emit_term_from_node_bin(nd))` arm (raw-byte AND TEXT-only — double violation) DELETED → `emit_build_compound_term((const IR_t*)(intptr_t)_.op_parts_ival[8/9])` inline. emit_build_compound_term is already both-medium (uses only x86() forms incl. blbl_lea→XK_RIPSEAL).
- **0 statics** — bas_cn/bas_cp/bas_lbl all relocated to prep. Template: 0 statics / 2 returns (CV8) / 0 blank / 200-col / real Greek / no MEDIUM_* / no raw bytes.
- char_type j=1 (atomgate=0) arm → `IF(_.op_parts_str[1], …)` (str-only; the `(!0||tag)&&str` reduction).

### Proofs
- **C2** — 7 firing probes (p1 copy_term-struct + c2–c7 catch-wrapped atom builtins) → normalized A/B asm-diff (bbN/.LcallN/.SN) **EXACTLY EMPTY ×7**. The 59th-run .S-renumber hazard did NOT materialize: `strtab_label` is idempotent by string, so first-appearance order held even though interning moved from emit-time to prep-time.
- **Behavior** — m2=m3=m4 identical ×6 families A↔B.
- **C3 gates at floors** — sno m4 7/7 HARD · pat M2 19 M4 19/0 · icon m2 12/12 HARD m3=m4 10/2 · prolog 5/5×3 · purity 1 · bin_t 0 · vstack 3 · handencoded 0 · **med_inv 102→84** · sno_pat_reg HARD · emit-blind 0.
- **C4** — GRAND 1344→1326, clean 40→42, no-growth on all other files.

## Probe vehicle finding (carried, law 5)
The Prolog GZ fast path now owns simple atom ops in m3/m4 (`rt_pl_atom_op_cell`). bb_atom_string fires only on **non-GZ-admitted** shapes — `catch(…)` defeats admission, which is how the per-arm probes (c2–c7) reach the box. Side effect: those catch-wrapped probes are m3/m4 silent + `Aborted` (m2-correct), and c6_chtype m4 has an undefined `.Lplpred__S0_2`/`_redo` link error. Both are **pre-existing brokered-catch breakage** (verified m2-correct, carried byte-identical), owner PROLOG-BB — NOT introduced by this stop.

## Concurrents absorbed (×2 at pull)
- `eb98b8e` + the `4fb0076`/`b7afb58` chain (bb_scan_match / bb_scan_many — Z-to-A twin scan family)
- `f8c39aa` RAKU-BB Group-C gate+emit
Rebuilt + re-certified after absorption; sno m4 7/7 HARD held.

## Cursor
`# CURSOR: bb_binop_arith.cpp` (TOTAL=4 — stale `[x]` tick from 2026-06-06 drifted via foreign edits; un-tick on arrival. bb_binop_concat_slot TOTAL=1 next.)

## Outstanding verdicts (standing set, carried — none new)
m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty pattern (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent + .Lplpred link gap (PROLOG-BB) · ceiling-ratify 1326.
