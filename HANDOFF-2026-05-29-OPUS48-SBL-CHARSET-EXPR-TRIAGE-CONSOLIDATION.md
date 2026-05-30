# HANDOFF 2026-05-29 — Opus 4.8 — SBL charset-EXPRESSION arg: 3 GOAL items → ONE root cause (TRIAGE; no code landed)

**Repo:** one4all `77a39e82` (UNCHANGED — clean floor, nothing committed to source). **Goal:** GOAL-SNOBOL4-BB.md.
**Docs:** `.github` `195066df` + `84daf610` (pushed) — consolidated triage written into GOAL.
**Net:** No FAIL-list change (deliberate — no fix shipped). Two previously-untriaged mode-2 gaps
(`XDump_driver`, `Qize_driver`) are now fully triaged and proven to share ONE root cause with test `064`.
A new native-only gap (`fence_driver`) is flagged. Both candidate fixes are fragile and were NOT forced
into the session budget without a full mode-2 gate; the next session has an exact locus + a documented red herring.

## Baseline verified green (matches watermark)
- Build: install_system_packages / build_scrip / `make libscrip_rt` all rc=0.
- GATE-1 smoke 13/13 (mode-2 AND `SCRIP_M3_NATIVE=1`). Rung M2=19/0, M4=18/1 (`053_pat_alt_commit` pre-existing FAIL-M4). FACT rule = 0.
- Broad corpus: native (`SCRIP_M3_NATIVE=1`) **256/280**; true mode-2 (`--interp`) **253/280**.
- mode-2-only gaps (fail m2, pass native), 4: `064_pat_fence_fn_capture`, `124_pat_regex_keyword_seal`, `Qize_driver`, `XDump_driver`.
- native-only gaps (fail native, pass m2), 1: **`fence_driver`** (NEW — emerged after FENCE-SEAL `77a39e82`; contradicts the older "ZERO native-only" milestone; re-check).
- mode-2 harness: stock `test_interp_broad_corpus_and_beauty.sh` runs **bare scrip = mode-3 native** (`scrip.c:135`). For true mode-2 use a copy with `--interp` injected (kept at `/tmp/test_m2.sh`).

## THE FINDING — one charset-EXPRESSION root cause covers XDump_driver + Qize_driver + 064
Both drivers fail on the IDENTICAL diff: `Qize('hello')` → `'' '' '' '' '' '' '' '' '' '' '' '' 'hello'`
(12 spurious empty captures) vs ref `'hello'`. (XDump test 2 "string dump" and Qize_driver test 2 "Qize simple"
are the same call into `beauty_suite/Qize.sno`.) Source pattern (two quote-branches in Qize.sno):
`(BREAK('"' "'" QizeWierd) '"' ARBNO(NOTANY("'" QizeWierd))) . part RTAB(0) . str`.

### Trigger (bisected — ALL THREE required)
1. A pattern primitive `BREAK/ANY/NOTANY/SPAN` whose charset arg is a **concatenation expression**
   (`'"' "'"`, or literal+var `'"' "'" QizeWierd`). A single literal is fine; a single `TT_VAR` is fine
   (SBL-BREAK-VAR handles it).
2. An `ARBNO` in the surrounding group.
3. The full anchored capture shape.

Minimal repros (rebuildable; were at `/tmp/min4.sno`):
- **case P (decisive, WRONG):** `str POS(0) (BREAK('"' "'") '"' ARBNO(NOTANY("'"))) . p RTAB(0) . r` on `str='cat'` → mode-2 MATCHES empty.
- case G (correct): same but `BREAK('"')` (single literal) → NO-MATCH.
- case Q (correct): same but `BREAK(bset)` with `bset='"' "'"` (variable) → NO-MATCH.
- case R/S (correct): concat-literal BREAK but NO ARBNO → NO-MATCH.

### Routing (why native / single-lit / var are correct, concat is not)
`lower.c:752-757` emits BOTH paths per match stmt: `lower_pat_expr` (runtime PATND — native consumes,
concat handled correctly) AND `BB_lower_pat` (mode-2 oracle BB graph). `build_node` (`lower_pat_dcg.c:91-101`
for BREAK; ANY/NOTANY/SPAN siblings same) accepts ONLY `TT_QLIT`|`TT_VAR`; a `TT_SEQ` concat → returns NULL
→ `BB_lower_pat` fails → `bb_idx=-1`.
- single-lit / var: `BB_lower_pat` SUCCEEDS → mode-2 uses the correct `bb_exec.c` oracle directly (verified: G/Q emit no translator traces).
- concat: `bb_idx=-1` → `stmt_exec.c exec_stmt`; PATND contains `XARBN` → `patnd_needs_xlate` (`stmt_exec.c:237-311`)
  routes through `patnd_to_bb_graph`→`build_patnd` (`lower_pat_dcg.c:368`).

### Charset is correctly resolved (RULED OUT)
`build_patnd` XBRKC (`lower_pat_dcg.c:384`) sets `bb->sval = pp->STRVAL_fn`. Wired-graph dump (DBG instrumentation,
since REMOVED) shows the BREAK node (`BB_PAT_BREAK` = kind 35) with `sval=["']` — the correct 2-char set.
So the empty match is a **structural / brokered-walk wiring bug**, NOT a charset bug.

### Execution path (VERIFIED this session — avoids a red herring)
mode-2 `--interp` → `bb_driver=1` (`scrip.c:157`) → `g_bb_mode=BB_MODE_BROKERED` (`scrip.c:161`). So `exec_stmt`
takes the BROKERED branch: ARBNO pattern (`needs_xlate`, no defer) → `patnd_to_bb_graph` (γ-CHAIN builder) →
**`bb_build_brokered`** → `bb_broker` (`bb_broker.c:14`, mode `bb_scan`). This γ-chain + `bb_build_brokered`
is the INTENDED pairing → the defect is a genuine brokered box-template WALK bug for capture+ARBNO, **NOT** the
flat-driver-drops-γ mismatch the `SBL-DEFER-NESTED` comment (`stmt_exec.c:396`) describes (that is a separate
mode-3/flat case fixed via `patnd_to_bb_tree`). **Do NOT chase "switch to `patnd_to_bb_tree`" here.**

Wired graph for case P (entry #6):
```
#6 POS(0)     γ→#2
#2 cap[part]  α→#5  γ→#0  ω=NULL
#5 BREAK["']  γ→#4  ω=NULL
#4 lit["]     γ→#3  ω→#5
#3 ARBNO      γ→#2  ω→#4
#0 cap[rest]  γ=NULL(accept)  ω→#5
#1 RTAB(0)    γ→#0
```
A static trace under `bb_exec_once` *should* fail (BREAK→ω=NULL→FAIL); the empty success arises in the
brokered box-template arms walking this graph. **Next concrete step: instrument the box-template brokered arms
`BB_templates/{bb_capture,bb_assign,bb_arbno,bb_pat_break}.cpp` on this repro.**

## Fix routes (NONE implemented — both fragile)
- **Route A (GOAL-preferred, larger):** lower charset-expression args correctly — emit SM ops to compute the
  concatenated charset and feed the pattern node (as native does). Touches `build_node` + **mode-4 emit**
  (`emit_bb.c:1482-1485` reads `nd->sval` for BB_PAT_SPAN/ANY/BREAK/NOTANY → must teach mode-4 the dynamic case).
  Constant-folding the all-literal sub-case alone is SAFE but lifts ≈0 corpus tests (corpus concats are nearly
  all literal+var: `SPAN(' ' tab)`×7, `SPAN(' ' nl)`×4, `SPAN('.' digits &UCASE '_' &LCASE)`×8, `BREAK(nl ';')`, Qize family).
- **Route B (contained, mode-2-only):** fix the brokered box-walk wiring for capture+ARBNO. Charset already
  correct; bug is structural. KNOWN-FRAGILE: the `stmt_exec.c:237` gate comment warns the legacy cast "has been
  compensating for latent issues in fence-heavy and capture-heavy PATND trees"; routing changes here have
  regressed 146/147/152/1011/1013/1017. Requires the full mode-2 broad-corpus gate with FAIL-list diff.

**HARD CONSTRAINT:** do NOT overload `bb->sval` with a binary "recipe" to carry literal+var concat data —
`emit_bb.c:1482` consumes `sval` as a plain C charset string and would emit corrupt mode-4 x86.

**Payoff when fixed:** the 2 driver tests + a sizable latent cluster (the `SPAN(' ' tab)` / `SPAN(' ' nl)` /
`SPAN('.' digits &UCASE '_' &LCASE)` families) + test 064.

## Repo / gate state at handoff
- one4all: **clean at `77a39e82`** — all DBG instrumentation reverted (`git diff` empty; verified against `/tmp/lower_pat_dcg.c.bak`). Build green; gates as in Baseline above.
- .github: GOAL triage committed + pushed (`195066df` consolidate, `84daf610` brokered-mode refinement), both rebased cleanly over parallel Icon/other-goal commits.
- NOT touched: PLAN.md goals table (per RULES — no edit on routine handoff).

## Suggested next session
1. Box-template instrumentation pass on the brokered capture+ARBNO walk (Route B), with the full mode-2 gate
   staged to catch the 146/147/152/1011/1013/1017 cluster; OR
2. A dedicated Route-A session (charset-expr SM-op lowering + mode-4 emit), if the larger fix is preferred.
3. Separately: re-triage the NEW native-only gap `fence_driver` (post-FENCE-SEAL).

Reference (full repros, dumps, command outputs): prior transcript + GOAL-SNOBOL4-BB.md triage block
(search "ONE root cause covering").
