# GOAL-RAKU-BB.md — Raku: goal-directed ~20% onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (kinds REUSED) · GOAL-RAKU-FRONTEND.md.
**Prereq:** HEADQUARTERS PP-1..6 ✅. BB-TEMPLATE-LADDER invariants 0..9 apply.

## Two IRs

- **SM** — flat stack-machine spine (`src/include/SM.h`).
- **BB** — four-port Byrd-box graph (`src/include/BB.h`). Kinds are **language-agnostic**.
  `BB_graph_t.lang` tags origin (`BB_LANG_RKU=6`); node kinds are reused.

SM emits `SM_BB_SWITCH` with `a[2].i` tag handing control to a BB graph.
Tags: `SM_BBSW_ICN_GEN` (0x49434E47), `SM_BBSW_PL_ENTRY` (0x504C454E),
`SM_BBSW_RK_GEN` (0x524B474E "RKGN"). Raku reuses the ICN_GEN emit-time
contract verbatim — `sm_bb_switch.cpp` / `emit_sm.c` / `sm_interp.c` arms
accept both tags.

**Where Raku sits:** Icon/Prolog are ~100% BB. SNOBOL4/Snocone/Rebus are mixed.
Raku today is ~100% eager SM in practice; the goal-directed ~20% is what
this goal moves onto shared BB kinds.

**Rules (RULES.md):** no C Byrd boxes; no SM/BB walking at runtime in modes 3/4;
ports are α/β/γ/ω; no `rt_*`/`raku_*` *port-logic* helpers (conversion/effect
helpers via `@PLT` are fine). X86 arms only.

## The insight (validated by RK-BB-1)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**.
`gather`/`take`, `…`, lazy ranges, `map`, `grep` — all "generate a Seq" on demand.
ONE four-port pull protocol (yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` PUMP)
suffices; every generative construct is a PRODUCER or CONSUMER of it. A would-be
10-kind ladder collapses to ~3 rungs on already-templated shared kinds.

## Port semantics (identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | `take` yield / next Seq element |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`**. NOT Prolog's `BB_ONCE`.

## Pipeline

```
Raku source → frontend (raku.y/.l)
  → SM spine: scalar/eager → SM_CALL_FN
             generative   → lower_raku_* → BB_graph(lang=BB_LANG_RKU)
                          → SM_emit_sii(SM_BB_SWITCH, NULL, bb_idx, SM_BBSW_RK_GEN)
  → SHARED templates (already filled): bb_to_by.cpp, bb_upto.cpp,
                                       bb_iterate.cpp, bb_gen_alt.cpp
  → emitted x86 (Mode 4)
```

## Moves to BB vs stays SM

**MOVES (goal-directed, REUSE shared kinds):**

| Raku construct | shared BB kind | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | `BB_TO_BY` | RK-BB-1 ✅ |
| `gather { … take … }`, `…` operator | `BB_SUSPEND` + `BB_EVERY` PUMP | RK-BB-2 |
| lazy `map` / `grep` | `BB_ITERATE` consumer (γ predicate for grep) | RK-BB-3 |
| junctions `any`/`all`/`one`/`none`, infix `\|`/`&` | `BB_ALTERNATE` + Bool-collapse on ω/γ | RK-BB-4 |

**STAYS eager SM:** scalar builtins (`uc`/`lc`/`substr`/`trim`/`index`/`rindex`),
`say`/`print`, arithmetic, hash/array element ops, class/method dispatch,
`sort` (whole-list), `try`/`CATCH` (the existing inline `raku_exc_*` SM is the
right shape).

**SPLIT OUT to GOAL-RAKU-PAT-BB:** regex / grammar backtracking. SNOBOL4 pattern
axis (`BB_SCAN`+`BB_PAT_*`) plus Prolog `BB_ONCE`+OR-retry for rule selection.
Heaviest lift; defer until SNOBOL4-BB and PROLOG-BB land more rungs. Today's
eager `raku_nfa_exec` stays.

## ⛔ No `rt_*`/`raku_*` port-logic helpers

Never add `raku_seq_pull` / `rk_take_yield` / `raku_grep_step` / junction
dispatch helpers. Port logic (α/β/γ/ω) lives in the shared `bb_*.cpp` templates,
emitted inline as x86. If a rung "needs" a new `raku_*` helper, the lowering is
wrong — fix the BB graph, not the runtime.

## Ladder steps

- [x] **RK-BB-1** ✅ (2026-05-27, Opus, one4all `13cef01a`) — lazy inclusive range
  `for $a..$b -> $i` → shared `BB_TO_BY`. `lower_raku_range` synthesizes
  `TT_TO_BY`, reuses `lower_icn_expr_top`, retags `BB_LANG_RKU`. `lower_for_range`
  gated `LANG_RAKU && !exclusive`. Arms widened in `sm_bb_switch.cpp` /
  `emit_sm.c` / `sm_interp.c`. `bb_to_by.cpp` REUSED unchanged. GATE-RK4 +
  `run_raku_via_x86_backend.sh` + `rk_range_for` test added. Shared runtime fix:
  `rt_nv_set` made non-consuming (peek) so mode-4 STORE_VAR matches mode-2.
  Open follow-on (RK-BB-1b): exclusive `..^` + non-literal-bound ranges
  (currently fall through to eager SM).

- [ ] **RK-BB-2** ⛔ NEXT — KEYSTONE lazy `Seq` box. `gather`/`take` + `…`
  → `BB_SUSPEND`+`BB_EVERY` PUMP. Retarget `lower_gather_hoist_pass` so `take`
  becomes γ-yield in the Seq box (lower-risk than full replacement). REUSE
  `bb_upto.cpp`. Verify `test/raku/rk_gather.raku` under `--compile`.

- [ ] **RK-BB-3** — lazy `map`/`grep` as Seq CONSUMERS. REUSE `bb_iterate.cpp`;
  grep adds γ-port predicate test (loop on false, γ on true, ω on source ω).
  Migrate `lower.c:1872-1881` off eager `SM_CALL_FN raku_map`/`raku_grep` for
  the lazy path. `rk_map_grep_sort24.raku` under `--compile` (sort stays eager).

- [ ] **RK-BB-4** — junctions + infix `|`/`&` → `BB_ALTERNATE` with Bool-collapse
  policy on ω/γ. REUSE `bb_gen_alt.cpp`/`bb_alt.cpp`. Add junction test.

- [ ] **RK-BB-5..N** — `reverse`/`tail`/`from-loop` as Seq consumers, one rung
  each. `zip`/`cross` = multi-Seq drivers (later).

## Rung methodology (mostly REUSE)

Per rung: (1) lower the Raku construct to the shared BB kind via
`lower_raku_*` (parallel `lower_icn_*`); (2) confirm existing `bb_<kind>.cpp`
covers it (Icon proved most cases); (3) only if Raku semantics differ, extend
the shared template behind a `lang==BB_LANG_RKU` guard (last resort — prefer
making the lowering match the template); (4) run GATE-RK4 + GATE-PK + GATE-RK
(mode-2) + smoke. Commit when the Mode-4 golden matches and nothing regresses.

## Test corpus — REUSE

`test/raku/*.{raku,expected}` (30 cases). The job is mode-4 conformance to
those goldens (the Prolog GATE-4 pattern), not correctness-from-zero — mode-2
already runs them. Add NEW flat files only for laziness probes the eager suite
can't express (e.g. `(1..Inf)[4]` that must terminate).

## Mode-3 (`--run`) — needs a Lon directive

RULES.md sanctions exactly one temporary SM-walk exception (Prolog `--run`,
AGW-1c). Do NOT route Raku `--run` through `sm_interp_run` without a Lon
directive. Mode-4 is this ladder's target; Mode-3 follows for free when the
templates land (same `bb_*.cpp` serves both per ARCH-SCRIP §"Mode 4").

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh    # GATE-RK mode-2 baseline
bash scripts/test_raku_mode4_rung.sh  # GATE-RK4 mode-4 baseline
bash scripts/test_smoke_raku.sh       # smoke baseline
# GATE-PK currently SEGFAULTS — see watermark; do not block on it.
```

## Gates

```
GATE-PK    test_per_kind_diff.sh        # currently segfaults (NOT this goal — see watermark)
GATE-RK    test_raku_ir_rungs.sh        # mode-2, must hold/improve
GATE-RK4   test_raku_mode4_rung.sh      # mode-4 vs .expected, must hold/improve
GATE-RK-SM test_smoke_raku.sh           # smoke must hold
```

## Watermark

```
one4all: 13cef01a (RK-BB-1 ✅, rebased onto 6deb9f71)
.github: HEAD (this prune; RK-BB-1 marked done; PLAN row reflects 13cef01a)

Gates at 13cef01a:
  GATE-RK mode-2: 8/30  (was 7/29 — +1 from rk_range_for)
  GATE-RK4 mode-4: 8/30 (rk_range_for, rk_forloop, rk_arith, rk_strings,
                         rk_typed_vars, rk_unless_until, rk_vars, rk_control)
  Smoke: 5/0 HOLD
  Prolog mode-4: 1/4 HOLD
  GATE-PK: ⛔ harness segfault — INHERITED FROM upstream 6deb9f71 (SBL-ANY-1
           + flat-driver α-label fix), bisect-confirmed independent of RK-BB-1.
           Pre-6deb9f71 baseline was 455/64/590/6. Owed: SBL-ANY session.

NOTE on SWITCH a[0].i: carries every-loop exit PC (mode-4 ω jmp) AND mode-2
  fresh/resume flag. Same overlap Icon's lower_every has and tolerates
  (bb_exec_resume self-inits an unstarted graph). Revisit only if a future
  rung needs a[0].i for a third purpose.

NEXT: RK-BB-2 (gather/take Seq box on bb_upto.cpp).
SCOPE (Lon, 2026-05-27): lazy map/grep IN; junctions IN; regex/grammar
  SPLIT→GOAL-RAKU-PAT-BB; sort/try/scalar STAY eager SM.
```

## Open questions for Lon

1. `lower_gather_hoist_pass`: retarget `__gather_N` sub output to feed the
   Seq box (RK-BB-2, lower-risk), or replace the pass with direct `BB_SUSPEND`
   lowering?
2. Junction Boolean-collapse: port policy in shared `BB_ALTERNATE` (guarded
   `lang==BB_LANG_RKU`), or SM wrapper opcode? Determines whether RK-BB-4
   touches a shared template.
3. GOAL-RAKU-PAT-BB (regex/grammar): stub sibling now, or defer until
   SNOBOL4-BB and PROLOG-BB land more rungs (it reuses their `BB_SCAN`/`BB_ONCE`
   machinery)?

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
