# FINDING: the ω-exit-pop defect is cured — two bugs stacked (a missing admission and a pass-ordering bug), and the fix must be gated on run-reconvergence or it breaks SNOBOL4

**seat14 · 2026-08-29 · row `pascal-restore-prezeta`** (continuing seat12's same-day
`FINDING-2026-08-29-seat12-pascal-zd-omega-pop-ignores-value-diamond-continuation.md` and
`FINDING-2026-08-29-seat12-pascal-op-zres-gated-omega-pop-fixes-pb34-breaks-snobol4.md`)

**Cured. `boolptr`/`boolidx`/`pb34` now byte-match `.ref` in both modes. Pascal gates: M3 FAIL=4→2
(remaining: `deep5`, `witness:bubble` — both pre-existing, out of this defect's scope), M4 FAIL=4→1
(remaining: `deep5` only). SNOBOL4 blocking set re-verified clean at 1377/1377 FAIL=0 both modes
(independent measurement, exit-code and printed-number agree). Icon 241 (floor 232), Raku/Prolog/
Snocone/Rebus all unchanged from baseline. Committed as SCRIP `<hash filled at push>`.**

## 0. Line numbers, re-confirmed against the live tree at push time (re-grep before trusting — this
row's own history shows citations drift within days)

- `zd_omega_head`: `emit.cpp:2502` (was 2500 before this session's two new helper functions were
  inserted above it).
- `zd_omega_seed` (new), `zd_omega_test_idx` (new): `emit.cpp:2504`, `2506`.
- `zd_plan`: `emit.cpp:2506` region, entry at what was `emit.cpp:2502` before the two new helpers.
- The per-run seed line (was `int zd = 0` unconditionally): now `emit.cpp` inside `if (ok) { int zd =
  (vd_tidx >= 0) ? zd_omega_seed(...) : 0; ...`.
- `x86_asm.h`'s JMP-site pop emission: **`x86_asm.h:2143-2144`** (drifted from seat12's `2156-2157`
  citation — `op_zgpop`/`op_wpop`, both now guarded `!= 0` instead of `> 0`).
- `x86_asm.h`'s JCC-dispatch guard (the third site seat12 flagged but didn't need to touch): **line
  449-450** — this ALSO needed the same `> 0` → `!= 0` relaxation; a negative `op_wpop`/`op_zgpop` was
  being silently dropped here too, routing through the plain-JCC path that never consumes either field.

## 1. Root cause, confirmed by direct instrumentation (`SCRIP_ZD_MAP`/`SCRIP_ZD_DIAG`) on `boolptr.pas`,
not inferred

Two independent bugs stack to produce the observed defect. Both had to be fixed for any output to
change.

**Bug A (hq_B's original finding, unchanged): `zd_omega_head` admits only `IR_CMP_TEST`.** Pascal's
(and Raku's, and Icon's) relop-as-value lowers to the sibling `IR_BINOP_TEST` — confirmed via
`grep -rn IR_BINOP_TEST src/lower/*.c`: emitted by `lower_pascal.c`, `lower_raku.c`, `lower_icon.c`;
**never** by `lower_snobol4.c` or `lower_prolog.c`/`lower_rebus.c`. So the two-node dead-end chain a
Pascal value-diamond's ω branch materializes through (`LIT(0) → ASSIGN __pbtN`) is never claimed by
any `zd_plan` run — it stays `zon=0, zout=-1` forever, confirmed directly in the `SCRIP_ZD-MAP` GRAPH/
PLAN dump on `boolptr.pas` (nodes i=12,13 in that dump: `claim=-1 zon=0 zout=-1` at baseline).

**Bug B (new this session, the actual reason Bug A's fix alone never worked in six prior sessions'
hands): `zgpop[]`/`zwpop[]` are computed INLINE, interleaved with claiming, inside a single two-pass
loop (`for(pass=0..1){for(hi..){ if(ok){ ...compute zout AND zgpop/zwpop for every node in this run,
right here... } } }`).** A node's own `zwpop` is fixed the moment ITS OWN run is processed — using
whatever `zon[]`/`zout[]` state exists at that exact point in `hi`-order, within that pass. Pascal's
`IR_BINOP_TEST` test node (e.g. `boolptr`'s first relop, `i=9` in the dump) is claimed and processed
in **pass 0** (it's on the direct gamma-flow from the statement root). Its ω-target dead-end chain
(Bug A, once admitted) can only be claimed in **pass 1**, which runs strictly after ALL of pass 0
completes. So by the time the test node's own `zwpop` is computed, the very run that would supply its
`oback` lookup doesn't exist yet — **no seed choice for the pass-1 run can retroactively reach a
computation that already happened.** This is exactly what seat12's two implementations of hq_B's item
5 hit: both achieved the *predicted* internal consistency (both diamond branches converging on the
same `zout`) and neither changed the emitted `add rsp,N` at the test's own ω-exit by one byte, because
that instruction's value was frozen in pass 0, before pass 1 (where the seed would apply) ever ran.

**The fix for Bug B: split "claim + compute zout" from "compute zgpop/zwpop"** — leave the existing
per-run inline computation untouched (so nothing about run-claiming or `zout` assignment changes), but
ALSO stash each node's `gt`/`ot`/`gin`/`oin`/`zdh_match`-at-that-point into new parallel arrays, and add
a **new pass that runs once, after both claiming passes complete**, which recomputes `zgpop[i]`/
`zwpop[i]` for eligible nodes using the now-FINAL `zon[]`/`zout[]`. This is a genuinely general
ordering fix, not specific to any op — Bug A's admission alone cannot reach the test node's own pop
without it.

## 2. First attempt: unscoped Bug-B fix breaks SNOBOL4 — 26-27 FAIL, same signature as the reverted
op_zres experiment

Applying the Bug-B reorder to **every** zon-armed node (both pass-0 and pass-1 claimed, regardless of
which op admitted the run) — plus Bug A's admission, plus seeding every pass-1 run's `zd` from the
originating test's own `zout` instead of `0` — fixed `boolptr`/`boolidx`/`pb34`/`a_plainvar`/
`f_const_then_relop` cleanly (9/9 on the acceptance gate's Pascal-side checks). **`test_corpus_snobol4.sh`
then read 26 FAIL (m3) / 27 FAIL (m4), concentrated in exactly `*_driver`/`crosscheck/{beauty,functions}`/
`demo_{roman,treebank}`/several `probe/*` — the same cluster seat12's reverted `op_zres`-gate experiment
broke.** Isolated by reverting only the `x86_asm.h` guard relaxation and re-running SNOBOL4 with the
emit.cpp reorder alone: **identical 26-FAIL set, byte-for-byte same names.** This proves the regression
traces entirely to the emit.cpp reorder/seed, not the guard relaxation — the guard relaxation was
independently confirmed necessary (reverting it alone puts `boolptr` back to `1,1`) but not the cause
of the SNOBOL4 break.

**Why: `IR_CMP_TEST` (SNOBOL4's own pattern-match test node) ALSO goes through pass 1 today, and the
unscoped fix silently changed ITS behavior too** — both the seed (every pass-1 run now started from the
test's `zout` instead of `0`) and the deferred pop-recompute (now touching every zon-armed node, not
just the newly-admitted ones) applied uniformly to `IR_CMP_TEST`'s existing, previously-correct runs.
SNOBOL4's pattern-match backtrack genuinely needs the OLD behavior (unwind the whole run back to its
own origin on failure) — that's not a bug in the old code, it's the correct semantics for a different
construct that happens to share the same admission mechanism.

## 3. The actual fix: gate Bug B's seed/override on run-reconvergence, not on op identity

`op_zres` was already shown (seat12's reverted experiment) not to discriminate Pascal's value-diamond
from SNOBOL4's genuine backtrack. Neither does op identity — extending the fix to "only when the test
is `IR_BINOP_TEST`" would be exactly the per-op filter RULES.md bans, and would still be fragile (Raku
and Icon also emit `IR_BINOP_TEST`, for constructs not yet audited for the same shape). The behavioral,
class-based discriminator that actually distinguishes the two cases: **does the claimed ω-chain, followed
forward via γ, rejoin a node already claimed by the SAME run as the originating test node?** For
`boolptr`'s value diamond: the ω chain's tail (`i=13`, `ASSIGN`) has γ-target `i=14` (the merge `VAR`
read), and `claim[14] == claim[9]` (both `0`, the same pass-0 run the test itself belongs to) — genuine
local reconvergence. For SNOBOL4's pattern-match backtrack, the ω target does not rejoin the test's own
run (it goes to a materially different continuation elsewhere in the pattern).

Implementation (`emit.cpp`, `zd_plan`): right after a pass-1 run is claimed (so `run[]`/`rl`/the
claiming loop's final `cur` are already known) and found valid (`ok`), look up the originating test
node's index (new helper `zd_omega_test_idx`), and check whether the claiming loop's stopping point
(`cur`) belongs to the same run as that test node (`claim[cur's index] == claim[test index]`). Only if
so: seed this run's `zd` from `zd_omega_seed(...)` (the test's own `zout`, matching seat12's Attempt B)
instead of `0`, and mark the **test node itself** (not the ω-chain's own nodes — see below) eligible
(`zvd_ok[test_idx] = 1`) for the deferred final pass to override its `zgpop`/`zwpop`.

**The ω-chain's own new nodes (`i=12,13`) do NOT need the deferred pass at all**, and are deliberately
left out of `zvd_ok` — confirmed by direct trace: they're processed in pass 1, which runs strictly
after pass 0 completes, so their own inline `gback`/`oback` lookups already see the complete pass-0
state (that's the normal, un-buggy direction — Bug B only bites nodes processed *before* the run that
would answer their lookup, i.e. pass-0 nodes referencing pass-1 targets). Confirmed: `boolptr`'s `i=13`
computed `gpop=0` correctly via the ORIGINAL inline code, unchanged by this session's edits, matching
the `SCRIP_ZD_MAP` dump exactly.

This is the general form of the class already implicit in the existing code's own `-K` asymmetry
between `zgpop`'s and `zwpop`'s fallback formulas (tuned, apparently, for `IR_CMP_TEST`'s
success/failure semantics) — the reconvergence check is what decides which semantics apply, without
naming either op.

## 4. Verification, this session, `make pristine` (RT_OPT=-O0)

- `boolptr`, `boolidx`, `pb34`: byte-match `.ref`, both modes, both direct execution and `--compile`
  binary re-run.
- `a_plainvar`, `f_const_then_relop` (this row's own regression detectors): unchanged/correct, both
  modes.
- Standing regression detector (`if 1=2 then writeln(7) else writeln(9)`): prints `9`, both modes.
- Previously-cured cluster (`boolassign`/`boolarg`/`boolchain`/`boolmix`/`boolnot`, landed at
  `8ebf6535`): all still byte-match, no regression.
- `scripts/test_gate_zd_omega_head_acceptance.sh` (seat03's acceptance bar, `7fa01b46`): 9/9 Pascal-side
  checks pass (was 0/9 at baseline minus the two structurally-unrelated ones). Remaining 4 reported
  FAILs are `pascal-bubble-m4-5x`/`pascal-quick-m4-5x` (pre-existing, the `pascal-m4-for-spine-leak-
  64b-per-iter` twin row's own Site-1 defect — confirmed by seat03/hq_P this same session as a
  *different* mechanism, a back-edge join-depth mismatch, not this row's ω-exit-pop; predicted
  unaffected by this fix and confirmed unaffected), `snobol4-blocking` (the acceptance script's own
  regex expects `m3 PASS=`/`m4 PASS=` but `test_corpus_snobol4.sh` actually prints `mode-3 (--run):
  PASS=`/`mode-4 (--compile): PASS=` — an instrument bug in the acceptance script unrelated to this
  fix, present identically at baseline; the real number was independently verified below), and
  `polyglot-demos-floor` (present identically at baseline, unrelated to Pascal — traces to unrelated
  same-day commits on `main`, flagged separately, not investigated further here — out of lane).
- **Independent `test_corpus_snobol4.sh` run** (not trusting the acceptance script's broken regex):
  `mode-3 (--run): PASS=1377 FAIL=0` / `mode-4 (--compile): PASS=1377 FAIL=0 SKIP=0` — clean, matches
  the pre-session baseline exactly. (The script's own `⛔ GATE REFUSES: 4 hardcoded corpus path(s)`
  rc=2 banner — `probe/rtx11_dynvar_{include,inline}`, `probe/rtx_func_11_{include,inline}` — is present
  identically before and after this session's changes; a pre-existing corpus-layout gap, not a
  correctness regression, out of this row's scope. Flagged to HQ separately.)
- Icon `test_icon_rung_suite.sh`-class floor check: `PASS=241` (≥232 standing floor, matches baseline).
- Raku smoke: `FAIL=0` both modes (matches baseline). Prolog crosscheck: `PASS=101 FAIL=0` (matches
  baseline). Snocone/Rebus smoke: `FAIL=0` (matches baseline).
- Pascal gates, isolated `RESULTS=`: **M3 PASS=161 FAIL=2** (`deep5` — pre-existing, unrelated
  `PAS-DISPLAY` bomb; `witness:bubble` — pre-existing, Site-1, out of scope) **M4 PASS=153 FAIL=1**
  (`deep5` only). Both gates still exit 1 (FAIL>0) — row `DONE-WHEN` not fully met; see Disposition.

All gated behind `SCRIP_ZD_VALDIAMOND` (the emit.cpp reorder+seed+gate, default ON) and
`SCRIP_ZD_TESTFAM` (the `zd_omega_head` admission widening, default ON) — set either to `0` as a
killswitch/control-arm per the Instrument Laws.

## 5. What's left, and why it's out of this defect's scope

- **`deep5`**: unrelated, self-diagnosing `PAS-DISPLAY L>=4 fallback unimplemented` bomb. Never
  claimed related by any prior session on this row; not touched.
- **`bubble`/`quick`** (`witness:*`, the `pascal-m4-for-spine-leak-64b-per-iter` twin row, "Site 1"):
  confirmed this session (seat03 → hq_P, `.github`
  `FINDING-2026-08-29-hq_P-pascal-m4-spine-leak-is-a-backedge-join-depth-mismatch-exact-node-isolated.md`)
  to be a **different** `zd_plan` defect — a for-loop back-edge join whose two predecessors disagree on
  runtime depth, where `zd_plan` still emits one static pop constant. Neither `SCRIP_ZD_OMEGA_HEAD=0`
  nor `SCRIP_ZD_BACKEDGE=0` (nor both) cures it, and this session's fix does not touch it (predicted by
  seat12's ordering proof last session; confirmed by direct measurement this session — `bubble`/`quick`
  unchanged before and after). hq_P's ruling: cure shape is "refuse, don't repair" — decline to
  zd-claim a run whose predecessors disagree on depth, rather than compute a cleverer constant. In
  scope for whoever holds `pascal-m4-for-spine-leak-64b-per-iter` (seat03 as of this session), not this
  row.
- **Corpus-layout gap** (4 missing `probe/` paths making `test_corpus_snobol4.sh` exit rc=2): pre-
  existing, unrelated to Pascal, present identically before this session. Flagged to HQ, not fixed here
  (out of lane — this is a corpus reorganization matter, not a compiler defect).
- **`polyglot-demos-floor` regression**: pre-existing as of this session's baseline measurement (before
  any of this row's edits), traces to unrelated same-day commits. Flagged to HQ, not investigated
  further — out of lane.

## Disposition

Committed to SCRIP (hash filled at push time). `DONE-WHEN` for this row (`test_gate_pascal_m3.sh &&
test_gate_pascal_m4.sh && test_corpus_snobol4.sh`, all `>/dev/null 2>&1`) is **still not met** — both
Pascal gates still exit 1 (the `deep5`/`bubble` remainder), and `test_corpus_snobol4.sh` itself exits
**2** (refuse) rather than 0, due to the pre-existing corpus-layout gap above, independent of Pascal's
own state. This is the row's headline mechanism cured after seven prior sessions' worth of diagnosis
(seat05 through seat12, hq_B) — what remains is two independently-tracked, out-of-scope items (`deep5`,
and the corpus-layout gap) plus one item now explicitly owned by a sibling row (`bubble`/`quick`, Site
1). Releasing the claim (`unclaim`) — task file `## NEXT` rewritten with this finding's summary,
`## LEDGER` updated. Mailed hq_B, hq_C, seat03 (holds the Site-1 sibling row and was coordinating live
on the shared `zd_plan` edits this session), seat11 (briefly held and released the acceptance-gate
sibling row this same session), seat05 (was queued behind Site-1).
