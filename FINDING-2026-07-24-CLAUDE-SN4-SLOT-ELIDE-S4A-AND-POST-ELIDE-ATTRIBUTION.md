# FINDING s138 (2026-07-24, Claude) — SLOT-ELIDE S4a LANDED + SPAN_VAR IS DEAD CODE + POST-ELIDE ATTRIBUTION

## 1. S4a — dead locals-shifted results elided (SCRIP `7e716f02`)
Discovery that made it cheap: the locals-shifted SNOBOL4 match family's front 16B "result" quad is **runtime-dead by construction** — every runtime accessor (drive_value_slot → nd_slot → zls_off, bb_prepare scratch, fc window bases, sealed-DEFER watermark repoint) reads the +16-shifted offset; `zls_result_off`'s only consumers are the S0 census and the --dump printer. Fix: `zls_entry_t` gains `loff` (locals base), `zls_off()` returns it, the one-line +16 law dies; `zls_grant_elide` S4 arm gives a DEAD whitelisted node its locals AT the entry offset — no front quad, no aliasing, zero template edits. LIVE nodes byte-identical. Whitelist (each audited: all runtime state in grant_locals fields, no cross-box front-quad reader): SPAN BREAK BREAKX TAB RTAB REM BAL ALTERNATE SEQUENCE FENCE1 DEFER VALUE. Excluded: HEAD (RELEASE/REPLACE flat cross-reads), ARBNO (body-window geometry mn/mx), ARB (zls2 save-slot), ASSIGN_SAVE (COND), SCAN_* (Icon scans genuinely home the value DESCR in the front quad), INITIAL. Kill-switch unchanged: SCRIP_SLOT_ELIDE=0 reverts wholesale.

## 2. Gates + measurement (this container, RT_OPT=-O0)
smokes 7/7×2 · crosscheck m3 307/3 · m4 307/3 · DIVERGE=0, fail names identical to pristine baseline (140/141 class; NOTE this container's pristine m4 is 307/3 — the s137 container's 4-test EVAL m4 defect does NOT reproduce here) · trio byte-OK both modes. rep10 warm A/B (10 matches/process, m3, interleaved ×7 medians, vs pristine-HEAD binary; m3 zls path is fully in-binary, verified static): json 51→48ms (−6%) · treebank 41→**33ms (−20%)** · claws5 10→10 flat (ARBNO-class excluded, predicted). SCRIP_STACK floor <4k both builds (saturated post-s137 seal; twitter depth shallow). json graphs dropped ~58 dead quads (DEFER 23 + SEQ 14 + ALT 11 + FENCE1 5 + SPAN 4 + BREAK 1) ≈ 928B/activation-carve+stosb.

## 3. SPAN_VAR is dead code; the SPD-1 "variable arms still call strchr" clause is STALE
`IR_MATCH_SPAN_VAR` has NO producer (grep: name tables + tools/audit only; template exists unminted). BLOBBOX census proves variable cset args (SPAN(dig), ANY(hex), BREAK('"' bslash …)) already resolve at blob-compile into the LITERAL kinds and take the s106 table/range/chain machinery. The strchr calls that remain live are Icon's bb_scan_any/bb_scan_many — out of SNOBOL4 scope. Manual pinned meanwhile (ln 4852-4859): plain args freeze at pattern CONSTRUCTION; only `*X` re-fetches at match — SCRIP's freeze point is first-match blob-compile, a known recipe-model difference, unchanged by this session.

## 4. Post-elide attribution — the gap is now pure emitted-code shape
SPD-0a script (exists at HEAD; goal-file checkbox stale) on json rep10 m4: TOTAL 404M Ir, **97.7% in emitted match code**; whole C runtime ≈2% (rt_defer_close 0.32, var_hash 0.32, memset 0.27, rt_defer_open 0.14). ≈40M Ir/match ≈ the s135 2.1× SPITBOL ratio. Conclusion: after s137-seal + S4a, runtime-library cost is dead; beating SPITBOL 3-4× requires cutting emitted per-attempt instructions — SPD-2 seam-traffic diet (δ bounces through FR at every seam), SPD-3 fused superops, SPD-7/BP-9 branch-chain Σ-pop collapse.

## 5. Parked with reasons
S4b (fc frame-shadow reclaim): shadow is LOAD-BEARING under non-FORTH port modes (HEAP/ALLOC read it flat) and worth ~176B across the trio — poor leverage, real risk. S4c (ARBNO/HEAD admission): ~112B, needs the geometry walk taught entry-vs-extent. Both recorded, neither blocking.

## 6. Owed at handoff
util_regen_benchmark/feature/demo_s_artifacts (codegen-affecting change: statement-graph .s layouts shrink) + push all repos (local commits only this session).
