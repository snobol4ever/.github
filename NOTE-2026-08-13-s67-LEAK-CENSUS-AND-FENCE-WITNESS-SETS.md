# NOTE s67 — THE TWO WITNESS SETS, BY NAME (so the next seat inherits names, not a dead /tmp)

Both sets below were derived at SCRIP `e34f5d83`/`b7793080`, corpus `9c96a110`. The census TSVs lived in
/tmp and are gone; these lists are the durable part. Regenerate with
`bash SCRIP/scripts/test_bug_hunt_census.sh out.tsv` (mode 1) and the same under `SCRIP_FN_RBP=2`.

## SET A — THE LEAK CENSUS (7): masked by the RBP bracket, PASS in mode 1, RED (SIG11) in mode 2
**All 7 contain `DEFINE`. All 7 carry nw=0** — ledger 2 is blind to statement-boundary depth drift.

    corpus/probe/bb/probes/X12.sno                     (already a named W-1 witness: m3 exits via NULL jump)
    corpus/probe/bb/test_sno_call2bb_1.sno
    corpus/probe/bb/test_sno_call2bb_2.sno
    corpus/probe/bb/test_sno_stmt_frame_1.sno          (4 lines: DEFINE('ADD3(N)') + OUTPUT = ADD3(4 * 2) + 1)
    corpus/probe/bb/test_sno_stmt_frame_2.sno
    corpus/programs/snobol4/demo/csn_bridge_b/probe_b.sno
    corpus/programs/snobol4/demo/spl_bridge/probe.sno

`test_sno_stmt_frame_1.sno` is the CHEAPEST member — 4 lines, one DEFINE, one call in an arithmetic
expression. Use it, not the bridges. ⭐ Single mode-2 REPAIR (RED m1 → PASS m2): `probes/X08.sno` (TIMEOUT).

**How to re-derive the set:** run the census twice, join on program, take `m1==PASS && m2!=PASS`.
⛔ Do NOT read the mode-2 net count as a score (168 vs 174) — the churn is the signal, the delta is not.

## SET B — THE FENCE(P) 2×3 (crash confined to ONE cell: failure edge AND carving interior)
| interior | success edge | **failure edge (backup passes through)** |
|---|---|---|
| zero-footprint (literals / alternation) | H02, H04 PASS | **H06 PASS** |
| carving — capture `.` / `$` | H14, H15 PASS | **H26, H27 SIG11** |
| carving — ARBNO (unbounded) | H11, H24, H25 PASS | **H08, H10 SIG11** |

All in `corpus/probe/bb/probes/`. **Bare-FENCE controls that PASS on the identical failure edge:**
`G22` (`POS(0) LEN(2) . W FENCE 'ZZ'`) and `G23` (the `$` twin) — these are what exonerate the failure
edge per se and prove the defect is FENCE(P)-specific. `H06` is the control that kills any "failure edge
crashes" claim: failure-edge FENCE(P) that PASSES because its interior carves nothing.

**Oracle expectations (sbl -b):** H26 → `ab` then `=F` (the `$` fires on the sub-match even though the
overall match fails — manual Ch.7). H27 → `=F` then `W=<unset>` (the `.` correctly does NOT fire).
H08, H10 → `=F` (ARBNO is shy, needs backup to extend, FENCE(P) hides its alternatives on backup, so
RPOS(0) is unreachable). **HEAD prints H26's `ab` and then SEGVs before `=F`; H27 SEGVs with no output.**

## THE ONE-LINE ORIENTATION FOR THE NEXT SEAT
The RBP bracket cleans an un-whacked leak IFF the statement runs inside a FUNCTION activation (Set A is
what it was hiding). Everything else — 37 of the 51 residual reds have no `DEFINE` at all — has no bracket
to clean it, and that is where a whack, or an earned STATEMENT frame, is really necessary.
