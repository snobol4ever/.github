# GOAL-RAKU-BB.md — Raku: move the goal-directed ~20% from SM onto shared BB generators

**Repo:** one4all + corpus + .github
**Sister:** GOAL-ICON-BB.md (generator templates this goal REUSES) · GOAL-RAKU-FRONTEND.md
(already specifies `gather`/`take`→BB_PUMP — this goal is its BB-emitter companion).
**Prereq:** GOAL-HEADQUARTERS.md PP-1..6 ✅. GOAL-BB-TEMPLATE-LADDER.md invariants 0..9 apply verbatim.

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Two IRs (verified 2026-05-27 code scan).** SCRIP has TWO intermediate representations:
- **SM** — flat stack-machine IR (`src/include/SM.h`, guard `SM_PROG_H`). The program spine.
- **BB** — four-port Byrd-box generator/pattern IR (`src/include/BB.h`, guard `SCRIP_IR_H`).
  The goal-directed substrate. Kinds are **shared/language-agnostic** (`BB_TO_BY` is commented
  "shared SNOBOL4/Icon/Snocone"; the BB_ICN_*→BB_* rename collapsed per-language kinds). A
  `BB_graph_t` carries a `lang` tag (`BB_LANG_RKU = 6` already exists) but the node kinds are reused.

They compose: SM is the spine; where goal-direction is needed, SM emits `SM_BB_SWITCH` with a tag
operand (`a[2].i`) that hands control into a BB graph. Tags today: `SM_BBSW_ICN_GEN` (0x49434E47),
`SM_BBSW_PL_ENTRY` (0x504C454E). This goal adds `SM_BBSW_RK_GEN` (0x524B474E "RKGN").

**Where the languages sit (verified):** Icon/Prolog are ~100% BB for their characteristic
constructs (`lower_icn.c`/`lower_pl.c` = 0 SM_emit, 77/62 BB-graph ops). SNOBOL4/Snocone/Rebus are
mixed: SM spine + BB patterns. **Raku today is ~100% eager SM in practice** — `grep BB_RK_ src/`==0,
`map`/`grep` lower to eager `SM_CALL_FN raku_map`/`raku_grep` (lower.c:1872-1881), `gather` is
hoisted to `__gather_N` subs (lower.c:2043+). The goal-directed ~20% is documented intent, not yet
built. THIS GOAL builds it — by REUSING the shared Icon generator kinds, not inventing `BB_RK_*`.

**Absolute rules (RULES.md):** No C Byrd boxes. No SM/BB walking at runtime in Mode 3/4. Four ports
= Greek letters (α/β/γ/ω). No `rt_*`/`raku_*` *port-logic* helpers; conversion/effect helpers
(`raku_substr`/`raku_index`/`raku_uc`/`raku_nfa_exec`/GC alloc) permitted via `@PLT`. X86 arms only.

## The one insight that makes this small and fast

Per the official Raku docs (docs.raku.org/type/Seq, /syntax/gather%20take, /language/list):
**almost everything generative in Raku produces the same type — `Seq`.** `gather`/`take`, the
sequence operator `...`, lazy ranges (`1..∞`), `map`, `grep` — all "generate a `Seq`" evaluated
"on demand." So we do NOT need a per-construct BB kind family. We need ONE four-port pull protocol
(yield-one-at-β = Icon `BB_SUSPEND`/`BB_EVERY` driven `BB_PUMP`), and every Raku generative
construct is either a PRODUCER into it or a CONSUMER of it. That collapses a would-be 10-kind ladder
to ~3 rungs on already-templated shared kinds. This is the "better, maybe faster" path.

## Port semantics (Raku — identical to Icon generators)

| Port | Direction | Raku meaning |
|---|---|---|
| γ | inherited DOWN | success / `take` yield / next `Seq` element delivered |
| ω | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep predicate false to end) |
| α | synthesized UP | fresh-pull entry (first `.pull-one`) |
| β | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = **`BB_PUMP`** (Icon "produce every value until ω"), per BrokerMode table (ARCH-IR) and
GOAL-RAKU-FRONTEND.md. NOT Prolog's `BB_ONCE`.

## Pipeline

```
Raku source
  → frontend (raku.y/raku.l)
  → lower_gather_hoist_pass (existing) — keep for now; RK-BB-2 retargets its output to a Seq box
  → SM spine: eager scalar builtins (say/substr/uc/sort/try) stay SM_CALL_FN
             generative constructs → lower_raku_expr_top → BB_graph(lang=BB_LANG_RKU)
             → SM_emit_sii(SM_BB_SWITCH, NULL, bb_idx, SM_BBSW_RK_GEN)   (mirror lower_to @ lower.c:1355)
  → sm_bb_switch.cpp SM_BBSW_RK_GEN arm (copy of SM_BBSW_ICN_GEN arm: walk_bb_flat inline four-port)
  → SHARED BB templates (already exist): bb_to_by.cpp, bb_upto.cpp, bb_iterate.cpp, bb_gen_alt.cpp
  → emitted x86 (Mode 4)
```

## What moves to BB vs stays SM (the determination)

**MOVES to BB (goal-directed — reuse shared kinds):**

| Raku construct | official semantics | shared BB kind REUSED | rung |
|---|---|---|---|
| lazy range `$a..$b`, `$a,$b ... $c` | lazy `Seq`, on-demand, deduced step | `BB_TO_BY` (`bb_to_by.cpp` ✅) | RK-BB-1 |
| `gather { … take … }` | take yields in dynamic scope; lazy Seq | `BB_SUSPEND` + `BB_EVERY` PUMP (`bb_upto.cpp` ✅) | RK-BB-2 |
| `…` sequence operator | initial elems + generator + endpoint | same Seq box as RK-BB-2 | RK-BB-2 |
| lazy `map` | returns Seq, on-demand | `BB_ITERATE`/`BB_LIST_BANG` consuming the Seq box (`bb_iterate.cpp` ✅) | RK-BB-3 |
| lazy `grep` | returns Seq, on-demand filter | Seq consumer + predicate test on γ (`bb_iterate.cpp` ✅) | RK-BB-3 |
| junctions `any`/`all`/`one`/`none`, `\|` `&` | autothreading: `f(1\|2\|3)`→`f(1)\|f(2)\|f(3)`, collapse in Bool ctx | `BB_ALTERNATE`/`BB_ALT` (`bb_gen_alt.cpp`/`bb_alt.cpp` ✅) + collapse policy on ω/γ | RK-BB-4 |

**STAYS eager SM (not goal-directed — leave as SM_CALL_FN):** scalar builtins (`uc`/`lc`/`substr`/
`trim`/`index`/`rindex`), `say`/`print`, arithmetic, hash/array element ops, class/method dispatch,
`sort` (inherently eager — needs whole list), `try`/`CATCH` (exception control flow, not generation;
existing inline `raku_exc_*` SM at lower.c:843-897 is the right shape).

**SPLIT OUT to a sibling goal (GOAL-RAKU-PAT-BB, not this ladder):** regex / grammar backtracking.
Official docs: Raku regex is "a backtracking NFA algorithm"; grammar `parse` backtracks; `|` =
declarative-longest-token, `||` = ordered backtracking alternation. This is the SNOBOL4 pattern axis
(`BB_SCAN` + `BB_PAT_*`) plus Prolog-style `BB_ONCE`+OR-retry for rule selection. It overlaps
GOAL-SNOBOL4-BB and GOAL-PROLOG-BB and is the heaviest lift — do NOT fold it in here. Today Raku
regex is eager `raku_nfa_exec`; leave it until the pattern ladders are further along.

## Ladder steps — Raku (committed: lazy map/grep IN; junctions IN)

- [x] **RK-BB-1** ✅ (2026-05-27, Opus) — lazy range → `BB_TO_BY`. Added
  `SM_BBSW_RK_GEN` (0x524B474E) to SM.h; `lower_raku_range` synthesizes a `TT_TO_BY`
  node and reuses `lower_icn_expr_top` to build the `BB_TO_BY` graph (retagged
  `BB_LANG_RKU`); `lower_for_range` gated on `LANG_RAKU && !exclusive` emits
  `SM_BB_SWITCH NULL bb_idx SM_BBSW_RK_GEN` + every-loop body drive; widened the
  ICN_GEN arms in `sm_bb_switch.cpp` (mode-4), `emit_sm.c` (exit-PC mark), and
  `sm_interp.c` (mode-2) to accept RK_GEN. `bb_to_by.cpp` REUSED unchanged.
  Created `scripts/test_raku_mode4_rung.sh` (GATE-RK4) + `run_raku_via_x86_backend.sh`
  + `test/raku/rk_range_for.{raku,expected}` (real inclusive range). Range verified
  under `--interp` AND `--compile`. Shared runtime fix: `rt_nv_set` made
  non-consuming (peek) to match mode-2 SM_STORE_VAR — the STORE_VAR;VOID_POP codegen
  underflowed in mode-4 (pre-existing, surfaced here). GATE-PK 455/64/590/6 HELD.
  GATE-RK mode-2 7/29→8/30. GATE-RK4 mode-4 PASS=8/30 (incl rk_range_for).
- [ ] **RK-BB-2** — THE KEYSTONE: lazy `Seq` box. `gather`/`take` and `...` lower to a
  `BB_SUSPEND`+`BB_EVERY` PUMP graph (the pull protocol). Retarget `lower_gather_hoist_pass` output
  (or replace it) so `take` becomes a γ-yield in the Seq box rather than a sub call. REUSE
  `bb_upto.cpp` PUMP machinery. Verify `test/raku/rk_gather.raku` under `--compile`. GATE-PK + GATE-RK (Mode 2 13/0) hold.
- [ ] **RK-BB-3** — lazy `map`/`grep` as Seq CONSUMERS of the RK-BB-2 box (committed lazy: large
  data ✅). REUSE `bb_iterate.cpp`; `grep` adds a predicate test on the γ port (loop on false, γ on
  true, ω on source ω). Migrate lower.c:1872-1881 OFF eager `SM_CALL_FN raku_map`/`raku_grep` for the
  lazy path. Verify `test/raku/rk_map_grep_sort24.raku` under `--compile` (sort stays eager). GATE holds.
- [ ] **RK-BB-4** — junctions `any`/`all`/`one`/`none` + infix `|`/`&` → `BB_ALTERNATE` with a
  Boolean-collapse policy on ω/γ (autothreading = generate each disjunct, collapse in Bool context).
  REUSE `bb_gen_alt.cpp`/`bb_alt.cpp`. Add a junction test to `test/raku/`. GATE holds.
- [ ] **RK-BB-5..N** — remaining lazy producers (`reverse`/`tail`/`from-loop`) as Seq consumers,
  one rung each, all on the shared kinds. `zip`/`cross` = multi-Seq drivers (later).

## Rung files — REUSE existing suite

Raku has a test suite (29 `.raku`+`.expected` in `test/raku/`, harness `scripts/test_raku_ir_rungs.sh`
Mode-2 gate PASS=13/0, upstream roast reference). The generative cases already have goldens:
`rk_forloop.raku`/`rk_for_array.raku` (range), `rk_gather.raku` (gather/take),
`rk_map_grep_sort24.raku` (map/grep/sort), `rk_control.raku` (control). **The job is the Mode-4
regression** against those same goldens (Prolog GATE-4 pattern), not correctness-from-zero — Mode 2
passes today. Add NEW flat files only for laziness probes the eager suite can't express (e.g. an
infinite range `(1..Inf)[4]` that must terminate). Put them beside the others in `test/raku/`.

## Mode-3 (`--run`) — ⚠ needs a Lon directive

RULES.md/ARCH-SCRIP sanction exactly ONE temporary SM-walk exception (Prolog `--run`→`sm_interp_run`,
AGW-1c): "No new exceptions without a Lon directive recorded here." Do NOT route Raku `--run` through
`sm_interp_run` until Lon records it. Mode-4 is this ladder's target; Mode-3 follows for free once the
templates land (the same `bb_*.cpp` serve both per ARCH-SCRIP §"Mode 4").

## ⛔ NO rt_*/raku_* PORT-LOGIC HELPERS

NEVER add `raku_seq_pull`/`rk_take_yield`/`raku_grep_step`/junction dispatch helpers. Those are
port-logic (α/β/γ/ω) helpers — forbidden by RULES.md INVARIANT 9. The shared `bb_*.cpp` templates
emit the port logic inline as x86; Raku reuses them unchanged. If a rung seems to need a new
`raku_*` helper to work, the lowering is wrong — fix the BB graph, not the runtime.

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /home/claude/one4all/scripts/test_per_kind_diff.sh        # GATE-PK baseline
bash /home/claude/one4all/scripts/test_raku_ir_rungs.sh        # GATE-RK Mode-2 baseline (PASS=13 FAIL=0)
```

## Gates

```
GATE-PK   bash scripts/test_per_kind_diff.sh          # always — must hold/improve
GATE-RK   bash scripts/test_raku_ir_rungs.sh          # EXISTING Mode-2 (PASS=13/0) — must NOT regress
GATE-RK4  bash scripts/test_raku_mode4_rung.sh        # NEW (RK-BB-1) — Mode-4 vs same .expected goldens
GATE-RK-SM bash scripts/test_smoke_raku.sh            # smoke must hold
```

## How to write a rung (mostly REUSE, not write)

Unlike the Icon/Prolog ladders (which FILL empty templates), this ladder mostly WIRES Raku lowering
into ALREADY-FILLED shared templates. Per rung: (1) lower the Raku construct to the shared BB kind
in `lower_raku_expr_top`; (2) confirm the existing `bb_<kind>.cpp` template covers it (it should —
Icon proved it); (3) only if Raku semantics genuinely differ, extend that shared template behind a
`lang==BB_LANG_RKU` guard (last resort — prefer making the lowering match the existing template);
(4) run GATE-RK4 + GATE-PK + GATE-RK. Commit when the Mode-4 golden matches and nothing regresses.

## Watermark

```
one4all: 13cef01a (RK-BB-1 ✅ COMPLETE — lazy range on shared BB_TO_BY, mode-2 + mode-4; rebased onto 6deb9f71)
.github: HEAD (GOAL-RAKU-BB.md RK-BB-1 marked done; PLAN.md row updated)

⛔ UPSTREAM BREAKAGE (NOT RK-BB-1): commit 6deb9f71 "SBL-ANY-1 + flat-driver α-label fix"
  (a parallel session) broke the GATE-PK harness: `scrip --audit-per-kind` SEGFAULTS,
  yielding bogus PASS=5/GONE=1061. Bisect-proven at 6deb9f71 WITHOUT RK-BB-1 in tree, so
  it predates and is independent of this work. RK-BB-1 rebased cleanly on top (only SM.h
  comment conflict, resolved to upstream wording; the #define was identical on both sides —
  the other session also added the SM_BBSW_RK_GEN tag but not the arms/lowering). FIX OWED
  by the SBL-ANY session or a follow-up: debug the per-kind audit segfault (likely the new
  flat-driver α-label / r10 cursor setup running on a kind that doesn't expect it).

RK-BB-1 status — ✅ COMPLETE (2026-05-27, Opus):
  ✅ SM_BBSW_RK_GEN (0x524B474E) in SM.h.
  ✅ sm_bb_switch.cpp / emit_sm.c / sm_interp.c ICN_GEN arms widened to accept RK_GEN.
  ✅ lower_raku_range (reuses lower_icn_expr_top → BB_TO_BY, retag BB_LANG_RKU).
  ✅ lower_for_range gated LANG_RAKU && !exclusive → SM_BB_SWITCH(RK_GEN) + every-drive.
  ✅ bb_to_by.cpp REUSED unchanged (zero template work — the goal's thesis confirmed).
  ✅ GATE-RK4 + run_raku_via_x86_backend.sh created; rk_range_for.{raku,expected} added.
  ✅ rt_nv_set non-consuming fix (mode-2/mode-4 STORE_VAR parity).

Gates at 13cef01a: GATE-RK mode-2 8/30 (was 7/29). GATE-RK4 mode-4 PASS=8/30 (incl
  rk_range_for, rk_forloop, rk_arith, rk_strings...). Smoke 5/0. Prolog mode-4 1/4 HOLD.
  ⛔ GATE-PK harness SEGFAULTS at this HEAD due to upstream 6deb9f71 (see breakage note
  above) — pre-RK-BB-1 baseline was 455/64/590/6; RK-BB-1 emitter changes route RK_GEN
  through the unchanged ICN_GEN arm so they cannot have caused it (bisect-confirmed).

NOTE on a[0].i dual-use: the SWITCH's a[0].i carries the every-loop exit PC (mode-4
  ω jmp) AND the mode-2 fresh/resume flag. This is the SAME overlap Icon's lower_every
  has and tolerates (bb_exec_resume self-inits an unstarted graph). Left as-is, matching
  the Icon contract; revisit only if a future rung needs a[0].i for a third purpose.

⚠ Exclusive range `..^` and non-literal-bound ranges still fall through to the eager
  SM while-loop. A follow-on rung (RK-BB-1b) can extend lower_raku_range: exclusive →
  synthesize hi-1 operand or pass a step/exclusive flag the BB_TO_BY box honors.

NEXT: RK-BB-2 (gather/take Seq box — BB_SUSPEND + BB_EVERY PUMP, reuse bb_upto.cpp).
SCOPE (Lon, 2026-05-27): lazy map/grep IN; junctions IN; regex/grammar SPLIT→GOAL-RAKU-PAT-BB;
  sort/try/scalar-builtins STAY eager SM.
```

## Open questions for Lon

1. `lower_gather_hoist_pass` — retarget its `__gather_N` sub output to feed the Seq box (RK-BB-2),
   or replace the pass entirely with direct `BB_SUSPEND` lowering? Retarget is lower-risk.
2. Junction Boolean-collapse: implement collapse as a port policy in the shared `BB_ALTERNATE`
   template (guarded `lang==BB_LANG_RKU`), or as an SM wrapper opcode around the switch? Affects
   whether RK-BB-4 touches a shared template.
3. GOAL-RAKU-PAT-BB (regex/grammar) — spin up now as a stub sibling, or defer until SNOBOL4-BB and
   PROLOG-BB land more rungs (since it reuses their `BB_SCAN`/`BB_ONCE` machinery)?

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
