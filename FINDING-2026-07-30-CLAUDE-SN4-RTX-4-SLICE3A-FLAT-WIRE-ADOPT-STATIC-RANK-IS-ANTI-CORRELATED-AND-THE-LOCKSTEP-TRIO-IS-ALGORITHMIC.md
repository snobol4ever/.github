# FINDING-2026-07-30-CLAUDE-SN4-RTX-4-SLICE3A-FLAT-WIRE-ADOPT-STATIC-RANK-IS-ANTI-CORRELATED-AND-THE-LOCKSTEP-TRIO-IS-ALGORITHMIC.md

## Session: s226

## Ports landed

**`rt_flat_wire_adopt` → `rtx_call.S` beside its already-asm sibling `rt_flat_ret_snap`.**
SCRIP `65574fa2`.  C body renamed `c_rt_flat_wire_adopt` in the same commit.

- 20 asm instructions vs 41 in the C (both from the object, not estimated).
- -O0 C waste: full rbp frame for a strict leaf, all four args spilled, g_pcall_top loaded twice,
  g_pcall_wires loaded twice, w pointer spilled across five stores.
- Port: each global loaded once, args stay in their incoming SysV registers (rdi/rsi/rdx/rcx),
  no frame, no spill.
- 0(c) on rt.o (NOT the .so): g_pcall_top and g_pcall_wires are GLOBAL HIDDEN and absent from
  the dynamic table.  [rip+sym] is direct; GOTPCREL is not owed.  Zero visibility promotions.
- 0(d): 23,743,053 entries corpus-wide; exactly 10,000,000 on func_call == the loop count.
  1:1 with SNOBOL4 procedure calls, which is a LANGUAGE property (Ch.8: every DEFINE'd function
  reaches RETURN exactly once per activation), not a benchmark artifact.
- 0(f): 10,000,000 entries / 0 bails / 10,000,000 commits; no cold arm.
- Two-sided ud2 planted on the COMMIT path; gate ON rc=132, gate OFF rc=0 and correct.
- Revert bit-identical three ways (grep=0, src md5, .so md5).

## S225 DEBT DISCHARGED FIRST

Three gates the s225 LIVE CURSOR recorded as NOT RUN were run and verified live this session
BEFORE the new port touched anything:

- `test_rtx_unit.sh` — ALL PASS (21 + 36 + 8,426 checks, 0 mismatches)
- `test_gate_rtx_store_width.sh` — GATE PASS (16 GOT-tainted stores checked)
- `test_gate_rtx_killswitch_sets.sh MATCH /corpus/crosscheck 4 both` — GATE PASS, zero movers
  (m3 316/1/0, m4 313/1/0 SKIP 3; quarantine: 160_pat_alt_inner_gen_resume, ON and OFF sets
  overlap, gate's own argument applies — C-side instability, asm cannot have caused it)

Slice 10 (`rt_dcap_step`) is now legitimately landed, not just claimed.

## THE RESULT THAT OUTRANKS THE PORT: STATIC RANK IS ANTI-CORRELATED FOR A THIRD TIME

Dynamic census via `util_rtx_count_syms.sh` across all 21 SNOBOL4 benchmarks, 20 still-C symbols.

| symbol | static sites | static rank | dynamic entries | verdict |
|---|---|---|---|---|
| rt_call_arr | 99 | #1 | 12,455,596 | warm — 10M is string_manip alone |
| NV_SET_fn | 43 | #2 | **24,700,581** | HOT, all 21 progs |
| rt_flat_wire_adopt | 6 | #16 | **23,743,053** | HOT, 6 progs |
| rt_goto_transfer | 6 | #17 | **23,743,053** | HOT, 6 progs |
| rt_proc_call_open_slim | 13 | #11 | **23,742,553** | HOT, 5 progs |
| rt_defer_step | 12 | — | **0** | confirms s225 strike |
| rt_arg_stage | 13 | — | **0** | unfalsifiable on this corpus |
| dtp_fn_of | 6 | — | **0** | unfalsifiable |
| rt_proc_set_nparams | 16 | — | **0** | unfalsifiable |

The s188 lesson (call-site count measures the EMITTER'S REACH, not execution) arrived for the
third time.  Only step 0(d) sees it.

## THE LOCKSTEP TRIO IS ALGORITHMIC, NOT AN ASM RUNG

`rt_flat_wire_adopt` (23.7M) fires in exact lockstep with `rt_goto_transfer` (23.7M) and
`rt_proc_call_open_slim` (23.7M — the 500 delta is `indirect_dispatch` taking the non-slim arm).
On `func_call` and `func_call_overhead` all three are exactly 10,000,000.

`rt_goto_transfer` (runtime_eval.c:276) is a linear `strcmp` scan over `g_lbl_tab` then
`rt_proc_find`.  `rt_proc_call_open_slim` (rt.c:1150) calls `rt_proc_find` on every invocation.
These are ALGORITHMIC rungs — a hash lookup or cached pointer would dwarf any asm port of the
bodies as written.  Scope with Lon before treating as an asm target.

## RTX-7 DOWNGRADE PREMISE IS NON-REPRESENTATIVE

s208 measured NV_SET_fn at zero on seven benchmarks and concluded an upper bound of 0.58%.
Those seven zeros reproduce exactly in this census.  But 18M of the 24.7M total live in
`string_pattern` (10M) and `pattern_bt_deep` (8M), which were not in that sample.  The "population
in the same sentence" rule (s224) applied to the measurement itself: 7 of 21 benchmarks is a
SAMPLE, not the corpus.  The 0.58% bound was correct for those seven programs; it is not a
corpus-wide bound.  Recommend re-measuring before quoting that ceiling in a rung.

## Gates (live, this session — NOT prose carried from the committed message)

- Watermark: **m3 312/4/0 · m4 312/2/2 · DIVERGE=2** — held exactly, 23s.
- CALL kill-switch MODE=both, 317 programs, N=4: m3 316/1/0 · m4 313/1/0 SKIP 3 — **GATE PASS**.
- MATCH kill-switch (s225 debt): m3 316/1/0 · m4 313/1/0 — **GATE PASS**.
- unit: **ALL PASS** (8,426/0). Store-width: **PASS**.
- Zero templates touched → zero .s regen owed, verified not inherited.
- RT_OPT=-O0 throughout. No speed number claimed (s224 hugepage bimodality still blocks the rail).

## handoff_status.sh is the push truth — NOT this block.
