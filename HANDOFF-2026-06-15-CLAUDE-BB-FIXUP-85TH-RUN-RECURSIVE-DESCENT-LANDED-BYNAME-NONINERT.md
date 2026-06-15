# HANDOFF — 85th attended run (Claude Opus 4.8) — GOAL-BB-FIXUP-A-to-Z / FIX-3-iii

**Date:** 2026-06-15 · **Lon attending** ("What % ... Continue." x3; opened ~15% → handoff called ~69%).
**One file landed:** `SCRIP f958c8e` — `src/emitter/emit_bb.c` (recursive arg-block producer descent).
**Cursor:** stays `bb_call.cpp`.

## TL;DR
- **LANDED (STEP 2 of the 84th plan):** the recursive arg-block walk in `resolve_call_kinds_descr/_gvar`. Proven **inert** (normalized A/B empty) and **stamp-complete** (stamp==route 0-mismatch for all 4 stampable kinds across 1386 files). The 84th run's `g->all[]` coverage gap is **CLOSED** — the 56 SNOBOL BYNAME under-stamps go to **zero** with the recursion.
- **NEW BLOCKER (the 84th never reached this):** **BYNAME stamping is NON-inert.** Adding the (correct, stamp-complete) BYNAME conditions changes emission for nested-call programs (13 normalized diffs) because an **un-normalized consumer in the arg-marshaling/slot path** reads a nested arg's `op` and treats `IR_CALL_BYNAME != IR_CALL`. BYNAME conditions were **reverted**; recursion-only landed.

## What landed (emit_bb.c, f958c8e)
Both producers now, after the per-node stamp, descend into argument sub-graphs:
- nested calls live in `IR_EXEC(nd).counter` (cast `IR_graph_t**`, length `IR_LIT(nd).ival`, gated `dval ∈ {2,3,5}`) — **not** in `g->all[]`, **not** in `bb->operands[]` (confirmed via `--dump-ir` + `SCRIP_DUMP_X=1` on `068_builtin_trim.sno`).
- snapshot `iscall = (IR_CALL || IR_CALL_DEFINE || ir_is_call_kind)` **before** stamping; old `continue` → `else if` so PROC_STAGED/GVAR_USERPROC parents also descend; each producer recurses with **itself** (per-emission-path consistency).

### Proof (all reverted instrumentation/binaries were temporary)
- **Inertness, structural:** `emit_core.c:412–415` — all 5 call-kinds + `IR_CALL` share one dispatch body (`bb_call`); `bb_call_route_classify` reads `dval`/`g_*_flat_chain`, never `op`. Stamping `op` is observationally inert until the cleanup rung.
- **Inertness, empirical:** normalized A/B (`sed -E 's/bb[0-9]+/bbN/g; s/\.Lcall[0-9]+/.LcallN/g; s/\.S[0-9]+/.SN/g; s/\.Lbb[0-9]+/.LbbN/g; s/\.Lbyname[0-9]+/.LbynameN/g; s/flat_[0-9]+/flat_N/g'`) old-vs-recursion **EMPTY** across the 14-file problem set + 0 raw diffs across all 850 SNOBOL. (NB: raw `bbNNNNN` labels are pointer-derived → non-deterministic even old-vs-old; **always normalize**.)
- **Stamp-completeness (STEP 4):** `SCRIP_VERIFY_KIND` assertion in `bb_call` → **0 mismatches** for BUILTIN / BYNAME / PROC_STAGED / GVAR_USERPROC across SNOBOL 850 + Raku 186 + Icon 350 = **1386 files**. Exact invariants: `BUILTIN ⟺ (route==FN && fn∉{write,writes})`, others `KIND ⟺ route==KIND`. The write-as-FN residual (`op=9 route=11 fn=write`) correctly stays `IR_CALL`.
- Full gate battery GREEN at floors pre+post; rank no-growth (GRAND 771 — producer is `emit_bb.c` infra, not a tracked `bb_*.cpp`).

## The blocker (why BYNAME is parked)
With recursion present, the BYNAME conditions (descr `dv2 && builtin`; gvar `!registered && (dv3 || (dv2 && !builtin))`) give **stamp==route 0-mismatch** (incl. TRIM in `068`). But:
- recursion-only normalized A/B = **0 diffs**; recursion **+ BYNAME** = **13 diffs** → BYNAME stamping breaks inertness.
- mechanism (`my $r = abs(int(sqrt($x)))`): stamping the **nested** operand calls `IR_CALL_BYNAME` shifts frame-slot offsets (`[r12+48]→[r12+32]` …) and the arg-marshaling structure.
- root cause: an un-normalized consumer in the **arg-marshaling / slot-allocation path** (run-82 "missed consumer" pattern). **Ruled out:** `arg_entry_terminal` (emit_bb.c:1966 — op-independent) and the `gvar_drive_call_arg_slots` precompute (gates on `arg_entry_terminal` + `IR_BINOP` shapes). The read is **deeper, in `marshal_call_arg`** (per-arg emitter — not yet pinpointed).
- this violates Law 1 (behavior-neutral) for nested-call programs → not landable until normalized.

## NEXT SESSION (de-risked)
- **STEP A — pinpoint + normalize the consumer.** Trace `marshal_call_arg`'s per-arg `op` handling (and any `bb_slot_claim`/`bb_slot_alloc16` keyed on the arg node's op). Find the `== IR_CALL` read / call-kind branch that is **not** normalized; normalize via `ir_norm_call_kind` so a nested `IR_CALL_BYNAME` marshals byte-identically to `IR_CALL`. Validate: re-run recursion+BYNAME normalized A/B → the 13 diffs must go to **0**.
- **STEP B — land BYNAME** (conditions already written+correct, stamp==route already 0-mismatch) as a 1-file `emit_bb.c` commit: normalized A/B EMPTY + VK=2 0-mismatch + full gate battery.
- **STEP C — CLEANUP rung:** convert dispatch + consumer `dval`-reads → kind-reads; DELETE `bb_call_route_classify` + the `bb_call.cpp` switch; residual ONLY for genuinely-emit-time routes (write-family `op_write_route`, RK_BOOL, DVAL2_BOMB, write-as-FN, FATAL).

## Reusable tooling (all reverted from tree)
- **Stamp==route assertion:** env-gated block in `bb_call` immediately after `g_emit.op_call_route = bb_call_route_classify(_.node);` — `SCRIP_VERIFY_KIND=1` (BUILTIN-only) / `=2` (4-kind). `_ = g_emit`; `_.node->op` = stamped op; `_.op_call_route` = route. `IR_CALL=9`, `IR_CALL_BYNAME=198`, `IR_CALL_BUILTIN=199`, `CALL_ROUTE_FN=11`, `CALL_ROUTE_BYNAME=1`.
- **Normalized-A/B** sed recipe above. **IR structure:** `--dump-ir` + `SCRIP_DUMP_X=1`.
- **Sweep harness:** compile each corpus file `--compile --target=x86 </dev/null`, collect stderr; per-file `timeout 3s`; redirect job-control noise (`2>/dev/null` at the loop level — files that hit pre-existing `abort()`/bomb shapes are harmless, they just stop emitting).

## ENV / gotchas
- corpus + x64 absent by default → clone `snobol4ever/{corpus,x64}` (corpus = 850 sno / 1312 icn / 186 raku; x64 = SPITBOL oracle `bin/sbl`). Clone them **sequentially**, not in parallel (`&` racing clobbers one).
- `/bin/sh` lacks `time` → use bare `make -j4 scrip` (NOT `time make`); `libscrip_rt` builds to `out/libscrip_rt.so`.
- `make clean` after `IR.h`/enum edits; use `bash -c` for process substitution (`<(...)`).
- add/commit → `git pull --rebase` → push; rebuild+regate every merged tree.

## Baseline at open (matched 84th; carried inherited reds)
sno m4 7/7 HARD · pat M4 19/0 HARD (M2 0/19 inherited) · icon m3/m4 12/12 HARD · prolog m3/m4 5/5 (m2 0/5 inherited) · purity 1 (bb_call_write_slot) · bin_t 0 · vstack 3 · medium_invisible 0 · handencoded 0 · prove_lower VACUOUS rc=0 (IR-REDESIGN). Rank: GRAND 771 / 129 / 77 dirty / 52 clean.

## FLAG for Lon (unresolved)
The shared tracker `BB-REVAMP-TRACKER.md` `# CURSOR:` line reads **`bb_match_arbno.cpp`** — that is the **Z-to-A twin's** footprint (it cleaned bb_match_break/atp/arbno/any since the 84th). This A-to-Z goal's own cursor is **`bb_call.cpp`** (goal footer + watermark). Proceeded on `bb_call.cpp`. The twins sharing one `# CURSOR:` line needs a decision (separate per-twin cursor markers?).

**SCRIP @ f958c8e verified on origin → .github @ this commit.**
