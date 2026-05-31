# SESSION HANDOFF — 2026-05-22 (session ~10, EC-UNI-INLINE-ALL closure)

## Repos at handoff

| Repo | HEAD |
|------|------|
| SCRIP | `302a1207` |
| .github | `b3c84f08` |
| corpus | unchanged from session start |

## Gate

**PASS=408 FAIL=0 STUB=651** throughout. Zero regressions.

## What was done this session

### INLINE-6 — full dead-machinery sweep of emit_sm.c + headers

Four commits to SCRIP:

| Commit | Work | Net |
|--------|------|-----|
| `1318fede` | Delete `g_sm_nullary`, `emit_sm_nullary_rt`, `emit_sm_op`, all `emit_sm_pat_*` wrappers, `emit_sm_coerce_num/exp/neg`, `g_sm_arith`, `emit_sm_arith_op`, `emit_sm_int_arg`, `emit_sm_acomp/lcomp`; orphaned dispatch decls from `emit_sm.h` + `emit_templates.h` | −379 lines/decls |
| `2c4cc75c` | Dedup 3 include clusters → 1, remove stale comment blocks | emit_sm.c 1766→1414 |
| `845af881` | Delete `emit_sm_op_*` family from `emit_sm.h` (53 decls, no definitions anywhere) | −53 decls |
| `302a1207` | Delete `emit_sm_selftest` dead decl; `git rm sm_pat_control.c sm_pat_position.c`; Makefile updated | −2 stub files |

**emit_sm.c: 1766 → 1414 lines (−352). SM_templates/: 15 → 13 files.**

### EC-UNI-22 — closure docs

Two commits to .github:

- `1ed9537a` — HQ SESSION ACCOUNTING updated (session ~10)
- `b3c84f08` — EC-UNI-22 ✅: invariant #11 added to HQ, `ARCH-IR.md` new-opcode guide rewritten for INLINE-ALL world, EC-UNI-22 marked complete, Phase B opened

## Architecture state (INLINE-ALL complete)

Every SM/BB code-generation path now lives exclusively in:
- `src/emitter/SM_templates/*.c` (13 files, grouped by opcode family)
- `src/emitter/BB_templates/*.c` (one file per BB box kind)

`emit_sm.c` carries only: walker, string-table, pattern-window, pc-label infrastructure, and `emit_sm_macro_library`.

**No wrapper functions. No table-driven dispatch. No per-opcode helpers outside template files.**

## Remaining EC-UNI work

| Rung | Status | Notes |
|------|--------|-------|
| EC-UNI-REFAITH | Open (no current FAILs) | Repair protocol; activates if FAIL > 0 |
| EC-UNI-19 | Open | Add-backend cost measurement (EMIT_NULL=99), patch+revert |
| EC-UNI-20 | Open | Add-opcode cost measurement (SM_NOP), patch+revert |
| EC-UNI-21 | Open | M1 baseline reconciliation — **awaits Lon decision** |
| emit_bb.c residue | Blocked | `flat_fill_and_call/bin/charset + emit_flat_ir` still live; INLINE-3-GROUP rejected; **awaits Lon directive** |
| Phase B | Open | Fill STUB=651 cells with real emission per backend/kind |

## Decisions needed from Lon

1. **EC-UNI-21:** Which M1 baseline? (a) re-converge to `abfd19a7` 646 lines, or (b) retire, stamp `9cddff25` 622 lines
2. **emit_bb.c residue:** retire the INLINE-3-GROUP blocker, or find alternate path to delete `flat_fill_*` cluster
3. **Next goal:** CHUNKS, PST, TEXTF, EC-UNI-19/20, or Phase B backend work?

## Session start protocol for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus /home/claude/corpus
# Read PLAN.md, RULES.md, then goal file
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
bash scripts/test_per_kind_diff.sh
# Expect: PASS=408 FAIL=0 STUB=651 at SCRIP 302a1207
```
