# HANDOFF 2026-06-04 (Opus 4.8) — Prolog-BB: PT-4a aggregate/nb on the meta rail (m4 101→105) + the 2026-06-04 directives (Proebsting canon · PL-M34 · PL-BBL · PT-4b→B-full)

## TL;DR

Two landings. **Code:** SCRIP `c5d1737` — `aggregate_all/3` + `nb_setval/2` + `nb_getval/2` emit and run
natively in mode 4; the 4 rung27 aggregate/nb rungs PASS m2==m3==m4; GATE-3 m4 **101 → 105 / 0 / 10**,
m2/m3 **115/115 HELD**, zero FAILs, all FACT gates green, siblings stash-proven byte-identical at clean
HEAD. **Doctrine:** `.github` `1f3afe10` + `a4508461` — a dynamic-DB diagnostic proved the m2 oracle
already compiles asserted clauses to executable BB graphs, which retired the PT-4 term-store spec and
produced three Lon directives now written into GOAL-PROLOG-BB.md: PROEBSTING IS THE CANON, the PL-M34
mode-3≡mode-4 parity ladder, and the PL-BBL pull-GDE-into-boxes ladder; the PT-4b fork is RESOLVED to
B-full (runtime JIT via the RX slab). Remaining 10 EXCISED = retract×5 + abolish×5, all PT-4b.

## PT-4a — what landed (`c5d1737`, 4 files, 131 insertions)

Why a new rt entry: `rt_aggregate_all_term` drives the goal predicate via `IR_interp_once` over the BB
**registry graph** — live in-process (m2/m3), absent in the standalone m4 binary. The PT-2b answer is the
**term rail**: `rt_meta_solve`/`rt_meta_redo` over the PT-0 installed predicate table.

1. `src/interp/IR_interp.c` — `rt_aggregate_all_meta(tmpl, goal, result)`: `rt_findall_term`'s drive
   skeleton (save env/cut/barrier · trail mark · entry CP · solve/redo loop · CP-truncate-to-entry ·
   trail unwind · restore) with the m2 IR_BUILTIN fold transcribed EXACTLY — count/sum/max/min, int→double,
   integral collapse to int else float, and the m2 quirk that max/min over ZERO solutions yields int 0
   (no acc_first guard on the result; m2 parity over SWI fidelity, flagged below).
2. `src/emitter/BB_templates/bb_builtin_aggregate_nb.cpp` — MEDIUM_TEXT arms: per-template
   `agg_build_term` (the bb_goal `build_arg` shape, duplicated per RULES — IR_STRUCT →
   `emit_build_compound_term`, else scalar marshal); aggregate_all uses the findall push/pad marshal
   (3 pushes + sub 8 = 32, aligned) → `call rt_aggregate_all_meta@PLT`; nb_setval/nb_getval marshal with
   strtab RIP-relative sres. ZERO raw-byte producers, ZERO baked pointers in the TEXT arms. The legacy
   MEDIUM_BINARY (mode-3 baked-pointer) arms untouched.
3. `src/emitter/BB_templates/bb_builtin_common.h` — `rt_aggregate_all_meta` extern (additive).
4. `src/driver/scrip.c` — RICH-gate admission: nb_setval/nb_getval (ival==2, operand chain
   `pl_findall_term_buildable`), aggregate_all (ival==3, all three buildable). Flat gate untouched.
   NOTE: per the new PL-M34 law this "m4-native, m3-interpreted" admission pattern is now DECLARED DEBT.

## The diagnostic that changed PT-4 (read this before touching retract/abolish)

Traced in-source, not assumed:
- m2 `IR_GOAL` arm (`IR_interp.c:4244`): `resolve_bb_lookup` → no graph → **fail to ω**. No AST fallback.
  So directive-asserted predicates MUST reach the BB registry to pass m2.
- m2 `assertz` arm → `pl_rt_assertz` (`src/lower/lower_program.c:351`): Term → `pl_assert_term` (AST
  clause) → **`lower_pl_clause_graph` (the REAL lowerer → executable BB clause graph)** → append to the
  predicate's live `IR_CHOICE.bodies[]`, registering the pred (with SUCCEED/FAIL ports) if new.
- m2 `retract` arm (`IR_interp.c:5121`): head-matches by **EXECUTING each clause body sub-graph**
  (`IR_interp_once(body)` under a fresh clause env + trail mark) and on match **splices `bodies[]`**
  (`zc->nbodies--`). `abolish`: `zc->nbodies = 0`.

**Conclusion:** in m2/m3 facts and rules — INCLUDING dynamically asserted ones — are EXECUTABLE CODE; the
only data structure is the clause CHAIN. `assertz` is already the SNOBOL4 EVAL()/CODE() mirror. The m4 gap
in one sentence: **native `bb_choice` bakes `n` and the cmp/je ladder as immediates — the standalone
binary's clause chain is frozen.** The old "store TERMS / term resolver / minus byte-code" spec is RETIRED
(it would make m4 dynamics data while the oracle's are code, and grow the C meta rail).

## The 2026-06-04 directives (full text in GOAL-PROLOG-BB.md; `.github` `a4508461`)

1. **PROEBSTING IS THE CANON.** gprolog/SWI demoted to OBSERVABLE-SEMANTICS ORACLES (what a conforming
   program prints), never implementation authority; no further transcription of WAM/byte-code/CP-layout
   internals. The SWIPL/GPROLOG study docs are historical grounding for landed work only.
2. **PL-M34 — mode-3 ≡ mode-4.** One program, one template body, two media (m3 = MEDIUM_BINARY → RX slab
   in-process; m4 = MEDIUM_TEXT → as+gcc). Rungs PL-M34-0 (divergence audit, no code) → -1 (native m3
   hello) → -2 (dual-medium via the x86() revamp, m3-NATIVE ratchet column in GATE-3) → -3 (kill the
   @PLT/movabs call-site fork) → -4 (retire the `sm_interp_run` carve-out) → FENCE (m3 and m4 print
   identical pass/excised sets; per-rung admission verdicts byte-identical). The MANDATORY-READ "DO NOT
   TOUCH" on mode 3 is re-annotated PL-M34-owned.
3. **PL-BBL — pull GDE back into BB land.** The SNOBOL4 standard (stackless control AND data-passing;
   needed stacks live INSIDE the box — ARBNO/ALT precedent). PL-BBL-0 coupling ledger pre-seeded:
   CANDIDATEs = clause cursor (heap `resolve_choice` `[rax+48]` → ζ-frame slot), activation env
   (`g_resolve_env` calloc/swap → ζ slots like Icon), `last_ok` flag (→ γ/ω return routing), cut flag;
   SPINE = trail, (slimmed) CP parent chain; META RAIL = second GDE engine in C, policy STARVE;
   catch longjmp = TBD. One rung per CANDIDATE, each gated three-mode-identical.
4. **PT-4b fork RESOLVED → B-full.** Dynamic preds emit a DATA-DRIVEN choice (cursor indexes a runtime
   clause TABLE; chain=data, bodies=code); runtime assert runs `pl_rt_assertz`'s exact pipeline in-process
   + MEDIUM_BINARY emit into the RX slab (lowerer + emitters + slab are ALL in libscrip_rt, linked into
   the standalone binary; the in-process pointer trap does not apply at runtime). Under PL-M34 this is the
   SAME code path in m3 and m4 — EVAL()/CODE(), the dynamic DB, and mode 3 collapse into one machine.
   B-lite (term rows) admissible only as a transitional scaffold; completion test = JIT'd clause bodies.

## Latent oracle divergences (ledger; re-baseline class WAM-CP-9/PT-3 — do NOT fix silently)

- m2 retract matches a RULE by executing its whole clause graph INCLUDING the body; SWI unifies (H:-B)
  without executing B. Unobservable in the 5 fact-only rungs.
- aggregate_all max/min over zero solutions: m2 (and the meta twin, by parity) yields int 0; SWI fails.
- Pre-existing from PT-3: m2 `rt_catch`/`rt_throw` lack CP-truncate + ball-copy.
- aggregate over a MISSING predicate: m2 graph-rail fails (no gcfg); the meta twin would count 0 and
  succeed. No rung exercises it.

## Gate state (verified at merged HEAD `c5d1737` after rebase over PB-9e/LB-3)

| Gate | Before | After |
|---|---|---|
| GATE-3 rung suite | m2 115 · m3 115 · m4 101/0/14 | m2 **115** · m3 **115** · m4 **105/0/10** |
| GATE-1 smoke | 5 · 4 (known artifact) · 5 | unchanged |
| PL-HY-FENCE · pl-no-value-stack · seg_byte/SL_B · g_vstack | PASS · PASS · 0 · 0 | unchanged |
| Siblings (stash-proven at clean HEAD) | Icon interp 129/118/36 · SNO-pat M2 18/1 M4 0/18 | **identical** |

Remaining 10 EXCISED: retract×5 + abolish×5 — ALL PT-4b/B-full.

## Repo state

SCRIP `c5d1737` · corpus clean (suite `.s` churn checked out, nothing committed) · `.github`
`1f3afe10` (PT-4a watermark + PT-4b finding) → `a4508461` (directives + ladders) → this handoff's
watermark commit. PLAN.md: one transparent cleanup — the Prolog row's stale parenthetical
(`111/111; m4 75/0/36`) stripped to the bare goal-file pointer (SSoT rule); one-line revert if Lon objects.

## Build / verify

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_prolog_rung_suite.sh --mode all   # m2 115 · m3 115 · m4 105/0/10
for r in agg_count agg_sum agg_max_min nb_setval_getval; do
  bash scripts/run_prolog_via_x86_backend.sh corpus/programs/prolog/rung27_aggregate_$r.pl; done
```
The suite regenerates `corpus/programs/prolog/*.s`; `git -C /home/claude/corpus checkout -- programs/prolog/` to re-clean.

Authors: LCherryholmes · Claude Opus 4.8
