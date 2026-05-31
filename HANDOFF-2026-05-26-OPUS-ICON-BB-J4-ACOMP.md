# HANDOFF 2026-05-26 — Opus 4.7 — GOAL-ICON-BB J-4 SM_ACOMP + rung quarantine

## Commits

- corpus  `d7e9ac1` — rung36 quarantine: `rung36_jcon_subjpos.xfail`
- SCRIP `cae35eb1` — rung36 timeout 30s→8s + header comment
- SCRIP `dfaf3032` — J-4: wire SM_ACOMP/SM_LCOMP in mode-3 JIT

## 1. Rung-suite speedup (was 30+ min, now ~19s)

Timing audit of all 75 `rung36_jcon_*.icn`: only 4 exceed 1s, and only ONE is a
true hang — `rung36_jcon_subjpos.icn` (~30s, infinite loop in the `--interp`
subject/&pos scanning path). The other slow ones COMPLETE (lgint 7.8s, mindfa
~1.6s, toby ~1.6s). The 30-min full-suite cost was that single hang dominating,
not "75 big files."

Fix (option chosen with Lon's go-ahead): quarantine via the script's existing
`.xfail` mechanism (instant skip, project convention) + drop rung36 per-file
timeout 30s→8s (no legitimate rung36 program needs >8s). `subjpos` now reports
`XFAIL`. Full suite 19s; fast `--rung`-loop of 01–35 only is ~3s.

⚠ `subjpos` is a REAL interp infinite-loop bug, quarantined NOT fixed. Worth a
separate investigation (subject/&pos path).

Dev-loop tip: do NOT run the full suite while iterating. Use
`bash scripts/test_icon_all_rungs.sh --rung rungNN` (instant), or the 01–35
loop (~3s). Save the full run (incl. rung36) for handoff.

## 2. J-4 — SM_ACOMP / SM_LCOMP in mode-3 JIT (`dfaf3032`)

Previously `SM_ACOMP` (arith compare, e.g. `if n <= 1`) fell through to
`rt_unimpl_op` in `sl_emit_one`, so any Icon `if` with a numeric comparison
could not run under `--run SCRIP_JIT_FLAT_BB=1`.

Added two JIT-local fns in `src/processor/sm_jit_interp.c` mirroring rt.c's
`rt_acomp`/`rt_lcomp` (numeric / string compare; push result-or-FAILDESCR; set
`g_jit_state->last_ok`): `rt_acomp_op(int op)`, `rt_lcomp_op(int op)`. Both take
the comparison token (TT_LE etc.) in rdi via `sl_mov_rdi_i64` then `sl_call` —
identical calling shape to the proven `SM_INCR`/`rt_incr` case. Added forward
decls + dispatch cases. No BB, no SM ptr, no C walker, no AST. `--interp`
(mode 2) path untouched.

LCOMP wired alongside ACOMP for free (same shape, existing rt_lcomp semantics).
`SM_ICMP_GT`/`SM_ICMP_LT` confirmed DEAD (never emitted) — correctly left unimpl.

### Verified
- `fib(7)=13` under `--run SCRIP_JIT_FLAT_BB=1` == `--interp` ✅ (the J-4 headline test)
- comparison then/else arms + if-as-value: byte-identical to `--interp` ✅
  (confirms SM_JUMP_S/SM_JUMP_F compose correctly with the new `last_ok`)
- smoke_icon 5/5, broker 23 — BOTH flag states ✅
- rungs01–35 `--interp` 189/2 unchanged (no regression) ✅

## NEXT SESSION

**Icon mode-3 frontier is now GENERATORS.** `every`/`to`/`by` abort under
`--run SCRIP_JIT_FLAT_BB=1` (`rung01_paper_to_by` → `sm_interp: stack underflow`
/ Aborted). Scalar exprs, comparisons, conditional control flow, and recursion
all run as mode-3 x86 now; generator iteration (the SM gen-tick / BB generator
pump path) does not yet. This is the substantial remaining J-5 work for Icon —
larger than the SM_ACOMP wire-up, overlaps the BB generator templates.

Out of scope for Icon J-5 (confirmed): `SM_PUMP_CASE` (Raku-only, LANG_RAKU gated,
lower.c:1281); `SM_BB_SWITCH`/`SM_BBSW_PL_ENTRY` (Prolog AGW entry, lower.c:1609,
GOAL-PROLOG-BB). Those `ignored slots` are NOT Icon.

Then J-6: flip `SCRIP_JIT_FLAT_BB` default + delete `rt_bb_pump_proc` + the two
bake sites (sm_jit_interp.c:1648, 2072); confirm `icn_bb_dcg`/`bb_exec_once`
unreachable from `--run` (stay live for `--interp`); ASAN clean per RULES.md.

Pending tidy (~5 min, standalone, NOT done — kept out to keep J-4 diff tight):
strip the dead `SCRIP_NO_AST_WALK=1` prefix from scripts/icon_bb_probes.sh +
scripts/test_prolog_bb_honest.sh. The env var is read NOWHERE in C (grep-empty);
the live tripwire is the always-on `NO_AST_WALK_GUARD` macro.
