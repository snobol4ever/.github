# HANDOFF — 2026-06-23 — Claude — PROLOG bench frontier registration + `--dump-ir` emit-order rewrite

## One-line
Prolog bench suite widened `green=4→6 / frontier=0→5 / broken=0` (added GREEN `fib`+`mu` with zero source change; registered 5 PB-BENCH-3 programs as honest `frontier` with full side-by-side artifacts); separately, `--dump-ir` (`bb_print`) rewritten to a COMPLETE, linear **emit-order** (γ-spine DFS) listing modeled on JCON's field-complete style.

## Repos touched (ALL committed locally; **PENDING PUSH — awaiting token**)
- **corpus** — `benchmarks/prolog/bench/` +21 files: `fib`/`mu` (`.pl`+`.expected`+real `.s` — GREEN); `crypt`/`deriv`/`sendmore`/`zebra`/`meta_qsort` (`.pl`+`.expected`+`.s.FENCED` — frontier).
- **SCRIP** — `src/contracts/scrip_ir.c` (`bb_print` rewrite — DUMP-ONLY, zero codegen impact).
- **.github** — `GOAL-PROLOG-BB.md` (STATE watermark + PB-BENCH-3 progress), this handoff.

## What happened
1. **Triaged all 7 PB-BENCH-3 programs against HEAD `pl_gz_admit`.** None admit as-is. Instrumented the admit path (PLREJ trace, reverted) to find each exact blocker (recorded verbatim in the goal STATE). Empirically DISPROVED the cheap path: bumping deriv's clause ceiling 8→16 lets it past admit but SEGFAULTS both modes — confirms it needs PL-BB-2/3 machinery, not a ceiling hack.
2. **Banked 2 free GREEN extension benches** (`fib`, `mu`) — admitted + run correct in m3∧m4 vs gprolog oracle with ZERO source change. `mu` (MU-puzzle) adds depth-bounded symbolic-rewriting/search coverage none of the seed 4 had.
3. **Registered 5 PB-BENCH-3 programs as honest `frontier`** (per the rung's own "each lands green or registers as honest frontier" rule) — `.pl` validated vs gprolog, `.expected` oracle, `.s.FENCED` marker via `util_regen_prolog_bench_s_artifacts.sh`. Suite invariant `broken=0` held throughout.
4. **`--dump-ir` rewrite** (`bb_print`, `src/contracts/scrip_ir.c`): was raw `all[]` array order (reads backwards). Now a **γ-spine depth-first traversal from `entry`** (visit node → γ → ω → operands, first-reach order) = the order `codegen_flat_body` actually emits, validated on Icon (operands threaded before their consumer, then call, then succeed/fail). Completeness: header carries `nslots`; per-kind payload decode (`callee=`/`builtin=/arity`/`slot=`/`atom=`/`arith=` + existing lit/var/binop/field); operands show on-node AND aux-map; an **unreached** section lists any `all[]` node off the emit spine so every node appears once. JCON `ir_dump`/`dump_simple` (field-complete labeled chunks in emission order) was the style reference.

## Verification (all green at handoff)
- Bench suite: `green=6 frontier=5 broken=0 total=11`.
- `bb_print` is DUMP-ONLY (called solely by `--dump-ir`) → zero codegen risk; suite unaffected by the runtime rebuild.
- `test_gate_pl_no_new_global.sh` PASS (floor 15; dump uses only local malloc/calloc, freed).
- `scrip` + `libscrip_rt` build clean; new region: 0 lines >200 chars, no inline comments.

## NOT done / next
- **Highest-leverage widening: nested-arith-expr in `is/2`** (lower + emitter) — unblocks `crypt` AND `sendmore` (and `query` among extensions). This is the single best frontier→green lever.
- `zebra`: **void-variable optimization in shared `src/lower/lower.c`** (singleton `_` must not consume a slot — zebra needs 78 > 64) — LOCKSTEP change across GOAL files if it touches `lcx_t`.
- `deriv` (PL-BB-2/3 CHOICE+structure-build), `meta_qsort` (PL-BB-5 meta) per the ladder.
- Add `poly_10` (needs `:-op` parser support) + `browse` (faithful star-match transcription) to the bench dir once their prereqs land.
- **`--dump-ir` for Prolog GZ**: current dump shows the original lowered IR in emit-order linearization; the GZ post-admit synthesized query-frame chain (`pl_gz_build`) is a separate structure not yet mirrored — a clean follow-on if GZ-chain order is wanted.
- **Stale-claim flag (unrelated to this session):** `--run` (mode-2) is unwired at HEAD (`"--run"` appears nowhere in `src/`); GATE-1 smoke shows m2 0/5 while m3/m4 are 5/5. The goal STATE's historical "GATE-1 5/5/5" looks stale on the m2 component.
