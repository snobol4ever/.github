# HANDOFF 2026-05-31 — Opus 4.8 — RK-LOWER-3: lazy map/grep as Seq consumers

## Summary

RK-LOWER-3 landed for **mode-2**. Raku `map { BODY } SOURCE` and `grep { PRED } SOURCE` now
lower to two NEW resumable Seq-CONSUMER kinds `IR_MAP` / `IR_GREP`, eager-draining a producer
Seq (a range `IR_TO` or a `gather` `IR_GATHER`) through a transform (map) or filter (grep).
All via the ONE shared `src/lower/lower.c` (Raku-only arms, additive, FACT 0) + the mode-2
oracle `src/lower/bb_exec.c`. ZERO emitter files touched.

SCRIP HEAD at handoff: **`fd54615`** (parents RK-LOWER-2 keystone `3571829`). Build clean
(`scrip` + `libscrip_rt` rc=0).

Semantics grounded in the official docs BEFORE coding (per the standing instruction):
- docs.raku.org/routine/map (+ /type/List): "invokes &code for each element and gathers the
  return values in a sequence and returns it. This happens lazily." Topic `$_`. Returns a Seq.
- docs.raku.org/routine/grep (+ /type/List): "Returns a sequence of elements against which
  $matcher smartmatches … in the order in which they appear in the original list." A `{ }`
  block matcher applies to `$_` and the element is KEPT iff the block returns a true value.

## Mode-3 ≡ mode-4 invariant — KEPT (by construction)

The invariant (`MIGRATION-MODE4-IS-MODE3-DUMP.md`: one template per box, one `bb_emit_mode`
switch, "divergence between modes is impossible by construction") governs EMITTED template
bytes. RK-LOWER-3 is mode-2-only by design (emission deferred to RK-EMIT), so I added NO
`emit_core.c` dispatch case and NO `bb_rk_*.cpp` template. Both mode 3 and mode 4 therefore
process `IR_MAP`/`IR_GREP` through the SAME shared dispatch (by-design SMX abort, identical to
the already-landed for-range/gather — same `kind=115` abort at a common structural node).
Nothing to diverge. Verified the byte-identity gate (`test_gate_em_template_byte_identity.sh`)
is unchanged: `git stash` of my 6 files + rebuild of clean `18357d4` → identical `PASS=1 FAIL=3`.

## What landed (all in `src/lower/lower.c` unless noted)

1. **Two new IR kinds** `IR_MAP`, `IR_GREP` — `src/include/IR.h` (enum, before `IR_SNO_PROG`);
   `src/lower/scrip_ir.c` (name table + `bb_reset` counter-preservation list, since the SOURCE
   sub-graph ptr rides on `.counter` and must survive reset — the `IR_GATHER` idiom).

2. **`v_raku_map_grep(cx, is_grep, closure_t, src_t, …)`** — ONE helper, `is_grep` selects the
   kind and the exec semantics. SOURCE → its own value sub-graph (`lower_value_subgraph`, cursor
   carries `IR_LANG_RKU`), ptr on `.counter`; closure BODY → second sub-graph, ptr on `.ival`;
   resume cursor on `.state`. Node is its OWN resume (β=self, like `IR_TO`/`IR_GATHER`) so the
   EXISTING generator PUMP via `v_raku_for` re-pumps it (body.γ → gen.β) — NO new pump machinery.

3. **Reach points (both Raku-gated; non-Raku → `lower_unhandled`):** the shared `TT_EVERY` guard
   now admits `TT_MAP`/`TT_GREP` iterate children (alongside `TT_TO`/`TT_TO_BY`/`TT_GATHER`), so
   `for map/grep {..} SOURCE -> $v` reaches `v_raku_for` → `lower2(TT_MAP/GREP)`; AND a dedicated
   `case TT_MAP: case TT_GREP:` (pulled out of the `lower_unhandled` group) for the bare form.

4. **Exec arms** `case IR_MAP: case IR_GREP:` — `src/lower/bb_exec.c`. On FRESH entry (state==0):
   eager-drain SOURCE via the `aggregate_all` idiom (`bb_reset` + `bb_exec_once` + `bb_exec_resume`
   loop, save/restore `g_current_cfg`) into a NODE-KEYED `DESCR_t` side-cache `rk_seq_cache_t`
   (so re-yields across PUMP re-entries don't re-drain). Then per (re)entry, advance the cursor:
   `NV_SET_fn("_", elem)`; `bb_exec_once(body_sg)`; **map** yields the closure RETURN (failing
   transform → `NULVCL`, one value per element); **grep** KEEPS the source ELEMENT iff the closure
   is NOT FAIL (`binop_apply`'s relational arms return FAIL on false — the value-model truthiness
   convention), else skips. Walking past the last element (or empty SOURCE) → reset cursor, FAIL→ω
   (Seq drained ⇒ the `for` STATEMENT completes & falls through, exactly like `IR_GATHER`).
   Also added to the gen-kind classifier lists: `bb_is_gen_kind_raw`, `ir_is_single_shot`,
   `ALT_IS_GEN` (same site-set `IR_GATHER` uses).

5. **Proofs** — `src/lower/prove_lower2.c` RAKU section: +2 cases (map ×1, grep ×1), each 4
   principal nodes (bind `IR_ASSIGN` + gen `IR_MAP`/`IR_GREP` + body `IR_CALL`+`IR_VAR`; SOURCE
   and closure are sub-graphs, NOT counted — the `IR_GATHER` idiom).

6. **Smoke** — `scripts/test_smoke_raku.sh`: +4 cases (map_range, grep_range, map_over_gather,
   grep_over_gather).

7. **Design note** — `src/../RK-LOWER-3-DESIGN.md` (in SCRIP root) records the verified docs
   semantics + the mechanism, for audit.

## FACT-rule / sibling safety

Only `src/lower/lower.c` (+ `prove_lower2.c`, `bb_exec.c`, `IR.h`, `scrip_ir.c`) touched; diff
strictly additive and Raku-gated (`cx.lang==IR_LANG_RKU`). New `case TT_MAP/TT_GREP` is a single
label (pulled cleanly out of the unhandled group — verified 0 remain there); no shared primitive
signature changed (only ADDED calls to `set_succ_fail`/`lower_value_subgraph`/`nalloc`, which the
FACT rule permits). Icon `v_every`/`IR_CALL` path and SNOBOL4 pattern path UNTOUCHED. Confirmed:
no dup `case IR_` in `emit_core.c`, no dup `case TT_` in `lower.c`, FACT-rule md5 `5097ed94`
byte-identical across all 4 GOAL files.

## Gate state at handoff

- prove_lower2 topology: **55/55** ✅ (was 53; +map, +grep, both `expected=4 PASS`)
- Raku smoke m2: **10/10** ✅ HARD (was 6/6); m3/m4 = by-design SMX abort (floors 0)
- Icon smoke m2: **6/6** ✅ HARD — UNCHANGED (reused generator kinds not regressed)
- SNOBOL4 smoke m2: **7/7** ✅ HARD — UNCHANGED (NFA isolation intact)
- FACT-rule grep: **0** ✅; no dup case labels ✅

**Pre-existing baseline items (NOT mine — proved identical on clean `18357d4` via `git stash`):**
- `test_gate_em_template_byte_identity.sh` = **1/4** — SM/BB emitter migration mid-flight
  (`MIGRATION-MODE4-IS-MODE3-DUMP.md` status "implementation underway"). Unchanged by this rung.
- `audit_concurrency_invariants.sh` template-purity COUNT **7 > hardcoded baseline 6** — all 7
  are sanctioned loud-error `fprintf`s in ICON/SNOBOL emitter boxes (`bb_assign`, `bb_binop`,
  `bb_call`, `bb_every`, `bb_field`, `bb_list_bang`, `bb_swap`), ZERO Raku. The 7th (`bb_call.cpp`
  `[GZ-3] FATAL`) is from Icon peer `582c3bc`. **FIX STILL OWED BY ICON/HQ: bump baseline 6→7.**

## NEXT

- **RK-LOWER-4 — junctions `any`/`all`/`one`/`none` + infix bar/amp.** Constructor + infix forms
  share ONE lowering (APPENDIX-A `RK-BB-4a/4b`: infix bar/amp build the SAME `TT_FNC` the
  constructors do; same-flavor chains flatten at parse time). Mode-2 collapse via the tagged-
  junction value (`ETX+flavor+SOH-separated members`; `rk_junction_collapse` threads the relop:
  any=OR, all=AND, one=XOR1, none=NONE). The `IR_ALT` fail-chain is the eventual mode-3/4 substrate.
  Ground every construct in docs.raku.org §Junction BEFORE coding (the standing instruction).
- The `…` sequence operator remains open (`IR_SEQ_GEN` already exists as the infinite `…` counter
  generator, SM-era exec not yet lowered — keep DISTINCT from `IR_GATHER`).
- Bare-value `say map {…} 1..3` (map/grep delivering a whole List as a value) waits on the
  List-value representation = RK-LOWER-5.
- STILL DEFERRED: the lockstep "three → four" roster/body expansion across all four GOAL files
  (FACT-RULE clause-5 obligation) — high-blast-radius, its own focused commit. FACT RULES remain
  byte-identical ×4 with Raku as the fourth carrier (md5 `5097ed94`/`307534d6`/`8255d653`).

## Files

- `src/include/IR.h` — `IR_MAP`, `IR_GREP` enum kinds
- `src/lower/scrip_ir.c` — name table entries + `bb_reset` counter-preservation
- `src/lower/lower.c` — `v_raku_map_grep`, `kind_is_resumable`, `TT_EVERY` guard, `TT_MAP/TT_GREP` case
- `src/lower/bb_exec.c` — `IR_MAP`/`IR_GREP` exec arms + `rk_seq_cache_t` + gen-kind classifier lists
- `src/lower/prove_lower2.c` — +2 RAKU proof cases
- `scripts/test_smoke_raku.sh` — +4 smoke cases
- `RK-LOWER-3-DESIGN.md` — session design note (verified docs semantics + mechanism)
- `.github/GOAL-RAKU-BB.md` — RK-LOWER-3 rung [x], watermark + live-state entry + gate table

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
