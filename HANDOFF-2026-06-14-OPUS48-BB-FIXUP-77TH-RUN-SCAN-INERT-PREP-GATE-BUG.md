# HANDOFF — BB-FIXUP-A-to-Z 77th attended run (Opus 4.8)

**Date:** 2026-06-14 · **Operator:** Lon Cherryholmes (attending) · **Cursor:** `bb_call.cpp` (STAYS)
**Net:** ICN-SCAN-3 **INERT PREP landed** (SCRIP `7880ef1`) + scan-gate bug found + retag designed & surfaced for pin (NOT landed, Lon endorsed stopping: "I'm with you").

---

## SESSION OPEN
- SCRIP cloned at origin **763938b** (concurrents past 76th-run 9ce94ca: `521ab64` Icon m3 jcc-encoder fix, `62ab2d2` **bb_list Z-to-A → 0 CLEAN**, `763938b` Pascal if-without-else, + Prolog GZ findall/aggregate work). During handoff push, two more rebased under us: `f9e6c02` (SNOBOL4 DEFINE abolish per-proc VIEW sub-graphs), `4a8ba14` (SNOBOL4 scan literal-pattern IR-free rt_scan_lit).
- ENV: `install_system_packages.sh` (libgc-dev → gc/gc.h) + `make scrip` + `make libscrip_rt`. **Corpus was ABSENT** (`/home/claude/corpus` missing) — cloned from `github.com/snobol4ever/corpus` (293 Icon programs). This matters: the scan gate needs it.
- Baseline GREEN: SNOBOL4 7/7/7, Icon 12/12/12, Prolog 5/5/5; floors bin_t 0 / vstack 3 / icn_no_stack 0 / purity 1 (bb_call_write_slot). GRAND **972** at open (down from 76th ceiling 1101 — concurrents cleaned ~129 incl bb_list); 134/94/40.

## THE dval BLOCKER — RESOLVED FROM SOURCE (the thing 75th + 76th deferred)
`lower_icon.c` `lower_call` (~line 75): a builtin call is **`subgraph`** (args in sub-graphs) unless **`chains`** (name is write/writes OR any arg `is_resumable`). 
- `subgraph` → `lc_call_argblks(call, 3.0, …)` → **dval = 3.0**.
- `chains` → **dval = 1.0** (flat-chain).

So a scan builtin is dval=3.0 with constant args (`tab(5)`) but dval=1.0 with a resumable arg (`tab(find("x"))`). **This is the "dual representation" both prior runs flagged — now confirmed, not guessed.** The correct retag discriminator is **"sval ∈ scan-names, inside a scan body" — never dval.** dval is retained and still drives marshalling.

`5091102` understood: it routed scan via emit-time (`g_icn_scan_regs_live`) with "lowerer + m2 UNTOUCHED" because the templates were bomb-stubs *then* and "oracle builtin-gen resume resists cheap delegation." The gen-resume hooks are all `sval`-keyed (m2 classifier/exec) or explicit (`icn_subchain_node_is_generator`) — every one mirrorable. The templates were later filled in (ICN-SCAN ladder); the family WORKS today via emit-time routing.

## INERT PREP — LANDED (SCRIP `7880ef1`, was c28e231 pre-rebase)
Make every `IR_CALL` scan-touch consumer ready for the retag **without flipping any node** (behavior-neutral by construction — lowerer emits zero `IR_SCAN_*`). Edits:
- **emit_bb.c:** new `static int ir_is_scan_kind(IR_e)` helper (the nine kinds); `IR_SCAN_*` case-labels stacked onto the `IR_CALL` arm in `binop_operand_streams` (~1509), `walk_bb_flat` prep switch (~2617), `descr_chain_arity` size switch (~3294); `icn_subchain_node_is_generator` (~1849) follows `IR_SCAN_{UPTO,FIND,BAL}`; `flat_emit_arg_subchain` ω-queue (~1868) follows all nine via `ir_is_scan_kind`.
- **IR_interp.c (mode-2):** `IR_SCAN_*` stacked onto `IR_CALL` in `ir_is_single_shot` classifier (~282) and `IR_interp_node` main exec (~2381) — retagged nodes keep sval/dval → identical path.

**PROOF of neutrality:** baseline scan-gate probe parity **PASS=20 FAIL=8 identical pre/post** via git-stash A/B rebuild; smokes 7/7/7 · 12/12/12 (HARD) · 5/5/5; floors held; GRAND unchanged by my edits (they live in infra, not bb_*.cpp). Re-certified on the rebased combined head (clean rebuild per build-hygiene lesson) before push.

## ⛔ NEW FINDING — THE SCAN GATE IS RED ON ITS OWN TERMS (load-bearing)
`scripts/test_gate_icn_scan.sh:233` filters the corpus bucket with `case "$dump" in *IR_GEN_SCAN*)` — but `--dump-bb` prints **`GEN_SCAN`** (the dump strips the `IR_` prefix on EVERY kind: `SUCCEED`, `FAIL`, `GEN_SCAN`). So the filter **never matches → N=0 unconditionally → floors m2≥31/m3≥11/m4≥11 are UNMEETABLE → the gate returns FAIL regardless of code.** The project-state belief "scan gate floors m3/m4≥11 green" is **incorrect**; it's been dark since the dump format dropped the prefix.
- Verified the corpus is fine: **14 of the first 60** corpus programs DO produce `GEN_SCAN` graphs. This is a one-token bug, almost certainly a silent regression from a dump-format change.
- **Owner = GOAL-ICON-BB** (the gate's own header names it), NOT this goal → **NOT patched here.** 
- **Recommended fix (GOAL-ICON-BB):** line 233 `*IR_GEN_SCAN*` → `*GEN_SCAN*`. That re-lights the corpus section (~70/293 programs carry scan graphs) and re-establishes the true scan baseline — the proof any scan-path retag needs.

The 8 probe FAILs (section b) are separately pre-existing/by-design: the X34 `=s` var-operand shape + `augop_scan` LOUD-EXCISE probes (two SIGABRT under `--compile`), identical at baseline.

## ⛔ RETAG — DESIGNED, BLAST RADIUS MAPPED, NOT LANDED (pin-gated)
The 75th-run recipe listed ~4 sites; the **real blast radius is ~12**. Core consumers (FATAL/gross-break risk) are covered by the inert prep above. **RETAG-additional sites** (must be added in the retag commit — in every one, `IR_SCAN_*` behaves like a value-producing call = like `IR_CALL`):
- emit_bb.c arg-shape classifiers: **2541** (wintexpr), **2739** (sibling), **2847** (relop-descr), **2915** (gvar-assign trigger).
- emit_bb.c chain-queue walkers: **3083**, **3322** (`c->op == IR_CALL || IR_CALL_DEFINE` → add `|| ir_is_scan_kind`).
- emit_bb.c **2661** (tab-arg = call: the arg-entry sa-slot path; tab's arg can be `IR_SCAN_FIND` etc.).
- emit_core.c **451** (gvar_assign arg-shape).

**The retag commit itself** = (a) `lower_icon.c` TT_SCAN: after `arg_block` builds the body sub-graph `bsg`, walk `bsg->all[i]` and retag `IR_CALL` whose sval ∈ the nine names → `IR_SCAN_<X>`, scoped to the scan body, **keeping dval + sval** (the 74th-run DEFINE-carve technique); (b) DELETE the now-dead emit_core.c live string-keyed scan block (**471–489**, `g_icn_scan_regs_live && sval` → bb_scan_*) — the dormant kind-cases (499–507) already cover it; (c) add the RETAG-additional parallels above.

**Why NOT landed this session (genuine blocker, not a stall):**
1. It is the `dval==2/3` channel marked `⛔ LON PIN REQUIRED`, "three-revert lesson governs"; `5091102` deliberately chose the opposite routing.
2. The Icon smoke exercises **zero** scan builtins, so the only behavioral proof for a scan-path retag is the scan gate — which is **dark** here (the token bug above + corpus-default-absent). Flipping the scan representation with no working validation of the changed path is the cowboy move the goal forbids.
3. The gate is another goal's artifact.

**Plan to land the retag (next session, gated):** once GOAL-ICON-BB lands the line-233 token fix and the scan corpus bucket is live, land the retag and prove neutrality with a **byte-identical scan-corpus output differential** (m2/m3/m4 vs the inert-prep baseline across all GEN_SCAN-bearing corpus programs) — that IS the care the pin demands. Revert the retag (keep inert prep) if ANY gate regresses.

## CEILING / FLOORS (combined head after concurrent rebase)
GRAND **992** / 136 files / 96 dirty / 40 clean (concurrents `f9e6c02`+`4a8ba14` added +20/+2 files, git-attributable; my inert prep = 0 to GRAND). Floors: bin_t 0 · purity 1 (bb_call_write_slot) · icn_no_stack 0 · vstack 3. Smokes 7/7/7 · 12/12/12 HARD · 5/5/5.

## OUTSTANDING VERDICTS (carried + updated)
m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated (ICON/lowering) · rank rp-patch ratify · rank cv9/cv10 desync · **ceiling-ratify 992** · LANGUAGE-BLIND audit category · Makefile header-dep gap · g_icn_scan_regs_live reconciliation (sanctioned driver-mode flag) · **NEW: scan-gate `IR_GEN_SCAN`/`GEN_SCAN` token bug — owner GOAL-ICON-BB** · scan-breakout direction A (carried — inert prep landed, retag PENDING gate-restore + pin). No LADDER rungs closed (FIX-3 open; FIX-3-iii inert prep landed, retag pending).

## NEXT SESSION
ENV setup (libgc-dev + `make scrip` + `make libscrip_rt`) → **clone corpus** (absent by default) → baseline GREEN → **IF GOAL-ICON-BB has landed the scan-gate token fix:** execute the retag (lower_icon bsg-walk + emit_core 471-489 delete + the RETAG-additional parallels) and prove with the scan-corpus differential; **ELSE** re-surface the gate fix / take a fresh pin. `make clean && make` after any header edit. Cursor STAYS `bb_call.cpp`.

⛔ **Shared-cursor note:** the tracker `BB-REVAMP-TRACKER.md` `# CURSOR:` header currently reads **bb_resolve.cpp** — that is the **Z-to-A twin's** position (last writer; the twin flagged "shared-cursor"). The A-to-Z cursor is **bb_call.cpp**, authoritative in THIS goal's watermark — read it from here, not the shared tracker field. Tracker left untouched to avoid clobbering the twin.

SCRIP @ `7880ef1` verified on origin · .github @ this commit.
