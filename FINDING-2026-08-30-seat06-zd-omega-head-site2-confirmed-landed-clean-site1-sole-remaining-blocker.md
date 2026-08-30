# FINDING 2026-08-30 seat06 — `zd-omega-head-per-op-filter-...`: Site 2 (`ff1df7782`) CONFIRMED landed and clean via a real pristine-build gate run — Site 1 is now the sole remaining blocker, not a live-edit collision

## CONTEXT
This row sat through 9+ prior sessions (seat03 ×3, seat08, seat05 ×3, seat11, seat16), every one of them releasing without touching `emit.cpp`/`zd_plan`/`x86_asm.h` because Site 2's fix was a live, uncommitted, actively-defended edit by seat14 on `pascal-restore-prezeta`. This session found that row now reads **DONE** (seat04, per the fleet board) and Site 2's fix has actually landed: `ff1df7782` "pascal-restore-prezeta: cure the ω-exit-pop defect behind boolptr/boolidx/pb34 — admit IR_BINOP_TEST into zd_omega_head, defer zgpop/zwpop to a reconvergence-gated final pass" — matching seat14's own verbatim description of their in-flight fix, reported to this row several sessions ago.

## VERIFICATION (not inference — a real `make pristine` + this row's own acceptance gate)
Tree `8640e02be` (already contains `ff1df7782` — confirmed via `git pull --rebase`: "Already up to date"). `make pristine` then `bash scripts/test_gate_zd_omega_head_acceptance.sh`:

```
✅ PASS structural-zd-omega-head -- the known-bad single-op filter string is gone
✅ PASS pascal-boolptr-m3 / m4 -- byte-matches .ref
✅ PASS pascal-boolidx-m3 / m4 -- byte-matches .ref
✅ PASS a_plainvar-m3 / m4 -- matches expected (hq_B's regression detector, still correctly green)
✅ PASS f_const_then_relop-m3 / m4 -- matches expected
⛔ FAIL pascal-bubble-m4-5x -- 0/5 clean under setarch -R
⛔ FAIL pascal-quick-m4-5x -- 0/5 clean under setarch -R
--- shared-node control battery ---
✅ PASS snobol4-blocking -- GATE OK m3 PASS=1672 FAIL=0 · m4 PASS=1672 FAIL=0 SKIP=0 · MISSING=0
✅ PASS icon-floor -- PASS=259 (>=232 standing floor)
✅ PASS raku-smoke, prolog-crosscheck, snocone-smoke, rebus-smoke, polyglot-demos-floor -- all clean
=== 2 CHECK(S) FAILED ===
```

**Site 2 is unambiguously done**: the per-op filter is gone, both named witnesses byte-match, both of hq_B's own regression detectors (the ones that killed the naive 2-line candidate cure) still pass, and the full SHARED-NODE VERDICT SCOPE battery this row's DONE-WHEN demands is clean across every language. This is not a new fix — it is the first *confirmed, gate-verified* landing report for a fix every predecessor session tracked only second-hand.

**Site 1 (`bubble`/`quick` m4, the +496B/visit for-loop back-edge over-release) is the sole remaining failure**, exactly as every predecessor's own analysis predicted ("EVEN A FULLY CORRECT SITE-2 FIX WILL NOT CLOSE THIS ROW'S DONE-WHEN"). This is not a regression from Site 2 landing — it is the separate, pre-existing, already-owned mechanism.

## WHY NOT ATTEMPTED HERE
Site 1 has its own dedicated row, `pascal-m4-site1-forloop-backedge-64byte-excess`, currently under active, deep investigation (seat08's current `## NEXT`, 2026-08-30: traced Site 2's reconvergence gate and proved it correctly excludes the embedded-conditional shape bubble/quick's swap/pivot tests present — ruling out "widen the gate" as the fix; open next steps are pass-0 K/REL tracing for that shape, naming quicksort's own partition conditional, and an unexplained m3-clean/m4-wrong asymmetry on `quick.pas`). That row's own standing rule reserves the fix for hq_C ("this is zd_plan's arming/depth/wall computation, not a local carve/release pairing — not solo-fixable"). Duplicating that investigation on this row would be wasted, redundant work — this row's job is to stay the acceptance bar, not a second investigation site, matching every predecessor's own stated reasoning.

## TASK FILE STATE
Updated this row's `## NEXT` to record Site 2 as gate-confirmed done and point at the sibling row for Site 1's live status. Released (`unclaim`, not `done`) — the DONE-WHEN is not yet met (bubble/quick still fail) and the remaining work belongs to the sibling row, not this session.
