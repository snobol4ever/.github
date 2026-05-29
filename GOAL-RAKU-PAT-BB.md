# GOAL-RAKU-PAT-BB.md — Raku regex/grammar onto an isolated BB_NFA_* family

**Repo:** one4all + corpus + .github
**Sister:** GOAL-RAKU-BB.md (split out) · GOAL-SNOBOL4-BB.md (`BB_PAT_*` owner — we do NOT touch it) · GOAL-PROLOG-BB.md (`BB_CHOICE` β precedent)
**Prereq:** GOAL-RAKU-BB RK-BB-1..5.4b ✅. BB-TEMPLATE-LADDER invariants 0..9 apply. RULES.md FACT RULE binds every emitted byte.

---

## Decision (locked 2026-05-29, Opus 4.8 + Lon)

Build a **NEW, ISOLATED `BB_NFA_*` opcode family** for Raku regex. Do **NOT** reuse SNOBOL4's `BB_PAT_*`. Reasons, in order of weight:

1. **Isolation removes the chief risk.** `BB_PAT_*` templates are SHARED with SNOBOL4's hot path; a Raku lowering bug in a shared kind would regress SNOBOL4 pattern emission. A separate family makes that regression class impossible during development.
2. **The NFA basis is more generic / more reducible.** `BB_PAT_SPAN/BREAK/TAB/RTAB/FENCE/ABORT/ARB` are high-level SPITBOL *pattern functions*, not primitive match ops. The NFA kinds are a smaller orthogonal basis that DERIVES them: `SPAN(cset)=CLASS+`, `BREAK(cset)=(-cset)*`. NFA primitives are the foundation; PAT high-level kinds sit above.
3. **Captures genuinely cannot reuse.** SNOBOL4 `$`/`.` (immediate/conditional assignment, `BB_PAT_ASSIGN_IMM`/`_COND`) write GLOBAL variables through SNOBOL4's variable model. Raku `$0`/`$1`/`$<name>` are SCOPED match-object captures. The cross-language variable model is NOT yet unified, so forcing Raku captures through the SNOBOL4 assignment kinds would be semantically wrong.
4. **The mode-2 executor seam.** `src/runtime/snobol4/snobol4_pattern.c` has ZERO language awareness (grep-verified) — it is bound to SNOBOL4's runtime value/cursor representation. There is no generic four-port mode-2 walker for PAT to reuse anyway.

**Convergence is a DEFERRED, PARTIAL, post-Phase-1 goal (RK-PAT-CONV):** once `BB_NFA_*` primitive matchers are byte- AND semantics-identical to their `BB_PAT_*` counterparts, collapse the PAIR into ONE language-agnostic enum value (e.g. `BB_MATCH_CHAR/CSET/LEN/POS`). Under the FACT RULE "merge" means RETIRING a kind so both languages lower to one template — NOT a shared byte-emitting helper (forbidden). Topology (`SPLIT`) and capture/assignment kinds STAY separate (semantics diverge; vars not unified).

---

## Why this goal exists (unification thesis)

Raku regex runs today on a parallel Thompson NFA interpreter (`src/frontend/raku/raku_re.c`; `raku_nfa_build`/`raku_nfa_exec`), reached from `raku_match`/`raku_match_global`/`raku_nfa_compile` in `raku_builtins.c`. It is a fourth bolted-on "try again" subsystem outside the shared BB backtracking spine (Icon `BB_SUSPEND`/`BB_EVERY`, Prolog `BB_CHOICE`, SNOBOL4 `BB_PAT_*`). A regex retry, a Prolog redo, an Icon resume, a SNOBOL4 backtrack are the SAME primitive — the `β` (retry) port. `BB_NFA_*` joins that spine: distinct KINDS, identical PORT semantics, driven by `BB_PUMP`. Payoff: ONE backtracking story; mode-3 regex = flat-wired native x86, no interpreter loop. The NFA's `Nfa_state.bb_id` field is the dormant hook for the state→BB-node walk.

## Raku semantics that scope the work (verified docs.raku.org + S05, 2026-05-29)

HYBRID engine:

| Construct | model | target |
|---|---|---|
| quantifiers `* + ? {m,n}`, `\|\|` (ordered alt), `regex` decl, subrule retry | **backtracking** | `BB_NFA_*` (β = next-state edge) |
| `\|` alternation (declarative LONGEST-TOKEN), proto/grammar dispatch | **declarative LTM** (parallel/forward) | Phase 2 — `BB_NFA_LTM` or retained parallel sim |

Correction vs Perl5 intuition: Raku `\|` = LTM (longest, declarative); `\|\|` = ordered/first-match. `:ratchet`/`token`/`rule` disable term-level backtracking but `\|`/`\|\|` candidates still retry on failure. Grammars are the SAME engine (namespace of named `token`/`rule`/`regex`; subrule `<name>` = backtrackable method call). The 6 open mode-3 CRASHes are PLAIN regex (only single-char `a\|b` where LTM≡ordered), so Phase 1 needs no LTM machinery.

---

## The BB_NFA_* opcode family (1:1 with existing Nfa_kind)

The parser in `raku_re.c` already emits `Nfa_kind`; lowering is a direct transcription — assign each `Nfa_state` a BB node, wire `out1→γ`, `out2→β` (`SPLIT`), terminal `ACCEPT→` graph γ.

| `Nfa_kind` (today) | `BB_NFA_*` kind | port wiring | Phase |
|---|---|---|---|
| `NK_CHAR`   | `BB_NFA_CHAR`   | match→γ(out1), mismatch→ω; β rescan | 1 |
| `NK_ANY`    | `BB_NFA_ANY`    | non-`\n`→γ, else ω | 1 |
| `NK_CLASS`  | `BB_NFA_CLASS`  | cset bitset test→γ/ω | 1 |
| `NK_SPLIT`  | `BB_NFA_SPLIT`  | try out1; β→out2; both fail→ω | 1 |
| `NK_EPS`    | `BB_NFA_EPS`    | pass-through γ=out1 | 1 |
| `NK_ANCHOR_BOL` | `BB_NFA_BOL` | pos==0→γ else ω | 1 |
| `NK_ANCHOR_EOL` | `BB_NFA_EOL` | pos==len→γ else ω | 1 |
| `NK_CAP_OPEN`  | `BB_NFA_CAP_OPEN`  | record start[idx], γ | 1 |
| `NK_CAP_CLOSE` | `BB_NFA_CAP_CLOSE` | record end[idx], γ | 1 |
| `NK_ACCEPT` | `BB_NFA_ACCEPT` | terminal → graph γ | 1 |
| `NK_CODE_ASSERT`/`PRED` | `BB_NFA_ASSERT`/`BB_NFA_PRED` | code callout | 2 |
| `NK_SUB_CALL` | `BB_NFA_SUBCALL` | backtrackable subrule (grammars) | 2 |

Driver: `BB_PUMP`. Phase-2-only / not-in-Nfa_kind-yet: `BB_NFA_LTM` (declarative longest-token alternation — does NOT reduce to `BB_NFA_SPLIT`).

---

## Rungs and Steps

### Phase 1 — plain regex on BB_NFA_* (closes the 6 mode-3 CRASHes)

- [x] **RK-PAT-0 — scoping artifact ✅** (this file; BB_NFA_* family locked, mapping + ladder + convergence plan recorded). PLAN.md row added.

- [ ] **RK-PAT-1 — wire the family + mode-2 walk: literal & dotstar.** PARTIAL — verdict-walk PROVEN (L1-L12 standalone oracle, 12/12), but SM dispatch gap found (see watermark): `~~` regex never reached the SM path.
  - [x] 1a. `BB_NFA_*` enum block added to `src/include/BB.h`. ✅
  - [ ] 1b. `raku_nfa_to_bb(Raku_nfa*) → BB_graph_t*` state→node walk via `bb_id`. **TODO** (gate to mode-4).
  - [x] 1c. Isolated mode-2 backtracking matcher `raku_nfa_bb_match` (`raku_nfa_bb.c`); `raku_nfa_start/accept` accessors + `raku_nfa_states` defined. RK_PAT_BB=1 gate in tree-walk handler. ✅
  - [x] 1d. L1–L3 (and through L12) verdict == `raku_nfa_exec`, standalone oracle, 0 mismatches. ✅
  - [ ] 1e. **BLOCKER:** register `raku_match` on the SM path so `--interp` reaches it (option A: byname table; option B: TT_SMATCH→SM_BB_INVOKE). Until then GATE-PAT-O cannot run inside scrip. **NEXT.**

- [ ] **RK-PAT-2 — mode-2: csets + anchors + ordered alt.** `\d+`/`[a-z]+` (`BB_NFA_CLASS`+`BB_NFA_SPLIT` loop, reuse `cc_fill_*` already in raku_re.c); `^x$` (`BB_NFA_BOL`/`EOL`); `a\|\|b` (`BB_NFA_SPLIT`). GATE: rk_re32/rk_re33 PASS mode-2 + oracle on L4–L12.

- [ ] **RK-PAT-3 — mode-2: captures.** `( )`→`BB_NFA_CAP_OPEN/CLOSE` surfaced as `$0`/`$1`; `<word>( )`/`$<word>` named. GATE: rk_re34/rk_re35 PASS mode-2 + oracle on L13–L15.

- [ ] **RK-PAT-4 — mode-4 emission.** NEW `src/emitter/BB_templates/bb_nfa_*.cpp` (one per kind; FACT-pure; modelled on `bb_pat_*.cpp` four-port discipline but isolated). GATE: rk_re33/34/35 mode-4 vs `.expected`; FACT grep 0; GATE-RK/RK4 hold; SNOBOL4 pat suite UNCHANGED (must be — different files).

- [ ] **RK-PAT-5 — mode-3 native (closes the cluster).** `SCRIP_M3_NATIVE=1`; arrive with mode-2+mode-4 proven, so only native wiring (rel32, ascending sites) remains. GATE: **rk_re32/33/34/35/37, rk_regex23 CRASH→PASS**; default `~~`→BB path; NFA demoted to harness oracle. Retires M3-RK-NOINTERP-1e in GOAL-RAKU-BB.md.

### Phase 2 — DEFERRED (own sessions)

- [ ] **RK-PAT-6** bounded `{m,n}`, non-greedy `*?`.
- [ ] **RK-PAT-7** LTM `\|` → `BB_NFA_LTM` (parallel/declarative; NOT `BB_NFA_SPLIT`).
- [ ] **RK-PAT-8** subrules `<rule>` → `BB_NFA_SUBCALL` (reuse Prolog call/`BB_CHOICE` precedent).
- [ ] **RK-PAT-9** `:ratchet` cut + proto/grammar dispatch + actions class.

### Convergence — DEFERRED (after Phase 1 green)

- [ ] **RK-PAT-CONV** — where `BB_NFA_CHAR/CLASS/ANY/BOL/EOL` are byte- AND semantics-identical to `BB_PAT_LIT/ANY/LEN/POS/RPOS`, collapse each PAIR to one `BB_MATCH_*` enum value (retire a kind; both languages lower to one template). `SPLIT` and `CAP_*`/`ASSIGN_*` STAY separate (topology + var-model divergence). Requires SNOBOL4 pat suite + GATE-RK all green before AND after each merge.

---

## Incremental TEST LADDER (climb in order)

GATE-PAT-O (mode-2, asserts `bb_nfa_exec` verdict == `raku_nfa_exec` verdict) then `.expected` gates. Each step adds exactly one BB_NFA_* kind.

```
L1  literal            'x' ~~ /x/                 → match     [BB_NFA_CHAR, ACCEPT]
L2  dotstar empty      '' ~~ /.*/                  → match     [+BB_NFA_ANY, BB_NFA_SPLIT]
L3  dotstar str        'xyz' ~~ /.*/               → match
L4  cset class         'hello' ~~ /[a-z]+/         → match     [+BB_NFA_CLASS]
L5  cset negative      '123' ~~ /[a-z]+/           → no-match
L6  builtin cset       'abc123' ~~ /\d+/           → match     [cc_fill_digit]
L7  builtin cset neg   'abc' ~~ /\d+/              → no-match
L8  ordered alt hit    'cat' ~~ /a||b/             → match     [BB_NFA_SPLIT branch]
L9  ordered alt miss   'dog' ~~ /a||b/             → no-match
L10 BOL/EOL anchor     'x'  ~~ /^x$/               → match     [+BB_NFA_BOL/EOL]
L11 anchor too-long    'xy' ~~ /^x$/               → no-match
L12 anchor empty       ''   ~~ /^x$/               → no-match
L13 pos capture $0     'John'   ~~ /([A-Za-z]+)/   → $0=John   [+BB_NFA_CAP_OPEN/CLOSE]
L14 two captures       'John Smith' ~~ /(\w+) (\w+)/ → $0,$1
L15 named capture      'John' ~~ /<word>([A-Za-z]+)/ → $<word> [name slot]
```

L1–L3 = RK-PAT-1; L4–L12 = RK-PAT-2; L13–L15 = RK-PAT-3. Mode-4 = RK-PAT-4; mode-3 native = RK-PAT-5 (the 6 corpus tests green).

---

## Gates

```
GATE-PAT-O   scripts/test_raku_pat_oracle.sh   # mode-2 bb_nfa_exec == raku_nfa_exec on L1..L15 (NEW @ RK-PAT-1)
GATE-RK      test_raku_ir_rungs.sh             # mode-2, hold/improve
GATE-RK4     test_raku_mode4_rung.sh           # mode-4 vs .expected, hold/improve
GATE-RK3     /tmp/gate_rk3.sh                  # mode-3 native; the 6 CRASHes are the scoreboard
GATE-RK-SM   test_smoke_raku.sh                # smoke hold
GATE-SBL-PAT test_snobol4_pat_rung_suite.sh    # SNOBOL4 BB_PAT_* MUST be byte-unchanged (isolation proof)
FACT         grep per RULES.md == 0
```

Isolation makes GATE-SBL-PAT a near-tautology (we touch no `bb_pat_*` files) — but it is the explicit proof the family is separate, so it runs every rung.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip libscrip_rt > /tmp/build.log 2>&1
[ -x scrip ] || { grep -E "error:" /tmp/build.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash scripts/test_raku_ir_rungs.sh
bash scripts/test_raku_mode4_rung.sh
bash scripts/test_smoke_raku.sh
bash scripts/test_snobol4_pat_rung_suite.sh   # isolation baseline
```

## Watermark

```
RK-PAT-1 PARTIAL — backtracking verdict-walk PROVEN; SM dispatch gap discovered.

DONE this session (Opus 4.8, 2026-05-29, NOT yet committed):
  - RK-PAT-1a: BB_NFA_* enum block added to src/include/BB.h (CHAR/ANY/CLASS/SPLIT/EPS/
    BOL/EOL/CAP_OPEN/CAP_CLOSE/ACCEPT). Isolated; no BB_PAT_* touched.
  - RK-PAT-1c: src/frontend/raku/raku_nfa_bb.c — isolated mode-2 BACKTRACKING matcher
    (nfa_bt depth-first over Nfa_state; β=SPLIT.out2 backtrack edge; raku_nfa_bb_match
    unanchored sweep mirroring raku_nfa_exec). Added raku_nfa_start/accept accessors +
    DEFINED raku_nfa_states (was declared-only, never implemented) in raku_re.c/.h.
    Wired into Makefile (source list + compile rule + auto-linked via wildcard).
  - THESIS PROVEN: standalone oracle (/tmp/oracle.c) — backtracking BB verdict ==
    parallel NFA verdict on L1-L12, 12/12, ZERO mismatches (literals, dotstar, csets
    [a-z]+/\d+, ordered alt a|b, ^x$ anchors incl too-long/empty). The architectural
    bet is validated: backtracking is correct for the whole Phase-1 regex subset.
  - Gated RK_PAT_BB=1 hook added in raku_try_call_builtin (raku_builtins.c).
  - Regression-clean: GATE-RK 35/42 (unchanged), smoke 5/5, SNOBOL4 pat suite M2 19/0
    M4 18/1 (BYTE-IDENTICAL — isolation proven), FACT grep 0.

CRITICAL DISCOVERY (reshapes the rung) — THE SM DISPATCH GAP:
  The 6 target tests (rk_re32/33/34/35/37, rk_regex23) FAIL in mode-2 too, not only
  mode-3 — "** Error 5 Undefined function or operation". ROOT CAUSE: `~~ /re/` lowers
  (lower.c:2492 TT_SMATCH) to `SM_CALL_FN raku_match`, but the ONLY handler for
  raku_match is `raku_try_call_builtin(tree_t *call, ...)` in raku_builtins.c — it takes
  an AST node and lives in the LEGACY TREE-WALK interpreter. The SM `--interp` path
  (sm_interp_run) dispatches SM_CALL_FN by name and has NEVER known "raku_match" →
  undefined. Regex is STRANDED off the modern SM/BB pipeline; it only ever ran in the
  retired tree-walk interp. The RK_PAT_BB=1 gate sits in the tree-walk handler, so it
  cannot be exercised from `--interp`. (This also explains why these were "deferred CRASH"
  — they were never on the SM path at all.)

  This VALIDATES the goal: moving regex onto the BB spine is exactly what re-attaches it
  to the modern modes. The verdict-walk being proven means the matcher logic is sound;
  the remaining Phase-1 work is PLUMBING regex into SM/BB dispatch, not matcher correctness.

NEXT (RK-PAT-1 completion, revised): make raku_match reachable from the SM path. Two
  options to weigh next session: (A) register raku_match/_global/_subst in the SM byname
  table (raku_builtins_byname.c) so SM_CALL_FN resolves it — fastest route to oracle
  inside scrip; gate the BB-vs-NFA choice there. (B) have lower TT_SMATCH emit an
  SM_BB_INVOKE over a BB_NFA_* graph built by raku_nfa_to_bb (RK-PAT-1b, NOT yet written)
  — the real ladder destination but bigger. Recommend (A) first to get GATE-PAT-O running
  end-to-end in `--interp`, then (B) for mode-4/3. RK-PAT-1b (raku_nfa_to_bb state→node
  walk via bb_id) still TODO and is the gate to mode-4.

GATE-RK3 mode-3 native: 6 CRASH (rk_re32/33/34/35/37, rk_regex23) — Phase-1 scoreboard.
FACT RULE grep: 0
```
