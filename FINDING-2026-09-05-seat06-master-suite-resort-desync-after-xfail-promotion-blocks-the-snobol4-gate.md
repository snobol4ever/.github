# FINDING 2026-09-05 seat06 — an XFAIL promotion that skipped `--resort` desynced ALL.sno/ALL.ref order and reds the SNOBOL4 blocking gate for everyone

**Measured:** seat06, 2026-09-05 11:40 CDT, SCRIP `1bff03224`, corpus `244ba5820`. Not cured this session.

## What happened

Closing an unrelated row (`snobol4-snoread-buffer-not-consumed-after-a-deferred-replacement-in-a-function`), I ran the SNOBOL4 blocking-set gate before claiming `done`, per that baton's own instruction:

    bash scripts/test_corpus_snobol4.sh

It REFUSES:

    ⛔ GATE REFUSES: harness produced no SUITE_BOARD line for the master suite
    ValueError: family.ref banner mismatch at seq 1827: sno='*---------------------------------------- 1827 opsyn_any_capture_replace_1'
                                                          ref='*---------------------------------------- 1827 opsyn_any_capture_replace_1 XFAIL'

## Root cause

`corpus 75012904f` ("Promote opsyn_any_capture_replace_1: XFAIL stale after SCRIP fix") correctly removed the stale `" XFAIL"` suffix from `tests/snobol4/ALL.sno`'s banner and deleted the entry's reason block from `tests/snobol4/ALL.xfail` — but did **not** run `util_build_master_suite.py --lang snobol4 --resort` in the same commit, and did not touch `ALL.ref`.

`util_build_master_suite.py --resort`'s own `--help` text names this exact hazard: the builder's canonical order is a function of `(xfail, feature count, line count, name)`, so removing an XFAIL tag changes that entry's sort key — *"A promotion must run this in the same commit or `rank <= N` stops selecting the greenest N."* Here the promotion changed `ALL.sno`'s content (and thus, implicitly, its canonical position) without re-sorting either file, so `ALL.sno` and `ALL.ref` now disagree on ORDER starting at that entry, not just content. `grep` for the test's own name in `ALL.ref` finds nothing — confirming this is a positional desync (the harness reads both files as parallel banner-delimited streams and compares the Nth block of each), not a content edit that missed one file.

This is the same finding-family as `FINDING-2026-09-05-hq_P-eight-trace-rows-dispatched-against-a-grader-that-was-never-pushed.md` and `FINDING-2026-09-05-hq_P-forty-four-batons-carry-a-placeholder-done-when-and-two-live-claims-cannot-be-closed.md`: a mechanical step documented as mandatory ("must run this in the same commit") was skippable in practice because nothing enforces it at commit time, and the failure surfaces as a hard refusal for every OTHER seat touching SNOBOL4, not as a defect visible in the commit that caused it.

## Why I did not cure it myself

`util_build_master_suite.py --lang snobol4 --resort` REFUSES on this tree:

    REFUSED: --resort found 27 loose absorbable famil(y/ies); absorbing and re-sorting in one
       step would make an ordering change indistinguishable from an absorption in the diff:
         config_probe_loose_fwctx_fwctx_suite_malformed, dcap_repl_deferred_capture_into_global,
         dcap_repl_deferred_capture_into_result, dcap_repl_deferred_capture_then_return,
         dcap_repl_deferred_pattern_built_by_function, probe_loose_callout_claws5_call,
         probe_loose_callout_claws5_cap, probe_loose_conformance_k09_file,
         probe_loose_conformance_k11_lastfile_lastline_lastno, probe_loose_conformance_k30_lastfile_only,
         probe_loose_conformance_k32_file_keyword, probe_loose_fuzz_fz_red_m4b_blob_defer_fence,
         probe_loose_fwctx_fwctx_standalone_ctl, probe_loose_table_nested_chain_incr_d1/d2/d3,
         probe_loose_table_nested_chain_read_d1/d2/d3, probe_loose_table_nested_claws5_l1/l2,
         probe_loose_table_nested_ident_guard_d1, probe_loose_table_nested_value_type_tbl,
         rtdef_compiled_define_code_body, rtdef_control_compiled_define, rtdef_dexp_idiom,
         rtdef_runtime_proto_compiled_body
       Absorb them first, or name them with --absorb-only to proceed with the resort alone.

Clearing this needs either absorbing (or explicitly `--absorb-only`-naming) 27 unreviewed loose families — several (`dcap_repl_*`) sitting in the exact neighbourhood the row I was closing names as "the ceo's passing-sibling fixtures," which makes them plausibly live/owned elsewhere right now. That is a materially bigger, unreviewed operation than the one-line banner desync I came to fix, and not this row's lane. I did not attempt it.

## Blast radius

Every SNOBOL4 row whose handoff instructions call `test_corpus_snobol4.sh` (the common case — it is one of the six `make test` blocking scripts) gets a hard REFUSE, not a red count, until this is cleared. A seat seeing this for the first time could easily mistake it for tree damage of their own making; it is not — it predates any of this session's work and reproduces from a clean pull.

## Routed

`hq_C` (my HQ) asked, topic `master-suite-resort-desync`, with this file's path. Not yet cured; no LANE REVIEW line written since ownership (whoever's row already touches `ALL.xfail`/the loose `probe_loose_*`/`dcap_repl_*`/`rtdef_*` families, or a fresh mint) is HQ's call, not mine to assume.
