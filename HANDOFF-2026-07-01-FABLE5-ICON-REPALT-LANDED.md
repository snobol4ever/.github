# HANDOFF 2026-07-01 — Claude Fable 5 — 38_repalt LANDED (flat_drive_repalt built) — audit 63/66, corpus 185→190

## Context
Continuation of the same-day wholesale-audit sessions on `GOAL-IR-IMMUTABLE-EMIT.md`. The named rung was
38_repalt: `flat_drive_repalt` was a PHANTOM (three emit.cpp comments cited it as owning e's four edges;
zero definitions, zero calls; yield/exhausted fragments orphaned in `bb_repalt.cpp`). SCRIP commit
`7edb9b9a` (on top of `0225b85a`) lands it, plus the three LOWER edge-stamp fixes and one slot-grant fix
the bring-up forced out. `.github` gets this doc + the goal-file watermark continuation.

## What landed (SCRIP `7edb9b9a`, 3 files)
1. **`flat_drive_repalt` built** (`src/emitter/emit.cpp`). Four stubs per JCON `ir_a_RepAlt`
   (irgen.icn:206-229): α clear(flag:=0)+jmp-e ≡ MoveLabel(t,fail);Goto e.start · yield (`ra_y`: copy
   e_sa→off, flag:=1, jmp-γ) ≡ MoveLabel(t,start);Goto success · exhausted-test (`ra_t`: flag==1 ?
   je-α-restart : jmp-ω) ≡ IndirectGoto(t) · β → e-β gated `ir_is_generator_kind(e_root)`, else ra_t
   (non-generator's resume IS its failure — the ml ival=0 rule; also avoids referencing a β label no
   template ever defines). Per-node `ra_y`/`ra_t` labels minted beside lbls/betas; e_root's γ/ω
   redirected onto them at edge-resolution time — emit-time READ, never a graph write. The design-note
   header's stale `IR_OP_COUNT` token corrected to `IR_REPALT`.
2. **Three β-mis-stamp-on-PRODUCE-edge fixes** (`src/lower/lower_icon.c`) — the LIMIT lesson's
   "exportable rule for Case/RepAlt" cashed in: (a) statement spine — `lower_proc_body` (the executed
   sequencer) + `TT_SEQ`/`TT_SEQ_EXPR`, guarded restamp `if (val->γ.node == succ) lc_γ_to(val, succ)`
   (the guard matters: `every` re-aims its γ internally; an unguarded restamp would rewire it); (b)
   `TT_REPALT`'s own γ — auto-β into generator-kind LIMIT sent the yield into the resume pump, infinite
   spin; (c) `TT_LIMIT`'s count→generator-entry edge, live only when the entry IS the repalt node (a
   TO's entry is a literal — why rung14 never tripped).
3. **`ir_drive_slot_assign`: IR_REPALT `k+=2` grant** (`src/contracts/scrip_ir.c`) — 16-byte value +
   int64 flag at +16, the LIMIT/ITERATE shape. Previously fell through and ALIASED onto e_root's tmp;
   with e=TO the flag landed exactly on TO's counter, so TO's α write (counter:=from) set the flag, the
   test read yielded, `|(1 to 0)` restarted forever.

## How the last bug was found (method note)
Not by reading code: ran the mode-4 binary, attached gdb to the live spin, `info symbol $rip` parked in
TO's retest, then dumped the frame slots by address (`from=1 to=0 cnt=1`, stable) — the clear's operand
[r12+128] equaled TO's counter slot, naming the alias in one look. Two-step spin-bracket, per RULES.md,
monitor waived per the standing 2026-06-27 Lon directive for this work.

## Verification (all rerun after the final edit)
- Probe: `every |1` → `3`; `rung13_repalt_empty` (`every write(|(1 to 0)\3)`) → `done`. Both modes.
- `scripts/audit_jcon_wholesale.sh`: **63/66 both modes, every row oracle `=exp`** (icont freshly built).
- Corpus `scripts/test_icon_all_rungs.sh`: **185→190**, per-program diff vs pristine `0225b85a` =
  exactly +5 FAIL→PASS (`rung13_repalt_{int,str,to,to3,var}`), **ZERO PASS→FAIL** (stash/rebuild cycle).
  Note: `rung13_repalt_empty` passed at baseline only because broken repalt instant-failed — right
  answer, wrong reason; it passes for the right reason now.
- Smoke 12/12×2; no_stack=0; one_reg=0; semicolon prison green; mutation gate HARD=4 baseline unchanged;
  `update_icon_bench_asm.sh` baseline (total=13 updated=0 unchanged=1 compile-err=12).

## Fresh-sandbox environment facts (they LOOK like regressions; they are not)
The harness's PASS=0/NOASM-everywhere state on a fresh clone has three causes, all environmental:
`apt-get install libgc-dev` (core.h includes <gc/gc.h>); `make libscrip_rt` (the harness links
`-Lout -lscrip_rt`); build the oracle from the icon-master upload with **plain `make Configure
name=linux`** (`X-Configure` demands X11/xpm.h and is the wrong target) — `build_rc=2` afterward is a
non-essential later target; `bin/icont`+`bin/iconx` exist and run. The `refs/` symlinks per RULES.md's
CONSULT CANONICAL SOURCES recipe make the harness auto-probe find icont. Corpus suite wants the corpus
clone at `/home/claude/corpus` (symlink suffices).

## Remaining audit ladder (3)
if_value_else (fix-shape documented in the goal file) · revassign (missing conversion — bare IR_FAIL
placeholder) · section_plus (pending arms). Parked items unchanged: x86() silent-drop dispatcher audit,
initial once-per-depth, r10 preamble reconciliation.

## Push status
Local commits only at time of writing — push pending credential (public clone needs none; push does).
Per RULES.md's FACT RULE this handoff is **BLOCKED** until `scripts/handoff_status.sh` prints otherwise;
only that script's verbatim stdout may claim completion.
