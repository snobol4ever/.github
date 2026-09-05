# FINDING 2026-09-05 seat15 — XDump prints an ARRAY's header but never enumerates its elements (TABLE dumping is unaffected); untracked, currently red on the SNOBOL4 master board

**Measured:** seat15, 2026-09-05 ~13:15 CDT, SCRIP `a55e7202e`, corpus `241579669`. Not cured here. Unrelated to my row this sitting (`snobol4-xfail-class-blanks-differ-unary-prototype-misc-4-entries`) — surfaced while re-verifying the full `test_corpus_snobol4.sh` board.

## What happened

`test_corpus_snobol4.sh` currently shows the SNOBOL4 master board RED (m3 FAIL=2, m4 FAIL=1). One of the two failing entries, `code_eval_len_table_replace_1`, is NOT in `ALL.xfail` and has no existing `.github/FINDING-*` — it is untracked. `corpus_suite_harness.py run --by-modes-column` names it:

    FAIL m3 code_eval_len_table_replace_1: output mismatch
    FAIL m4 code_eval_len_table_replace_1: output mismatch

## Root cause

The entry's fixture (`test/beauty` XDump subsystem driver) exercises `XDump()` over INTEGER, STRING, ARRAY, TABLE, REAL, PATTERN and a nested TABLE. The entry chains three top-level `-INCLUDE`s (`global.inc`, `Qize.inc`, `XDump.inc`, all under `corpus/include/`) — extracting it in isolation without those companions produces a misleading harness-side failure, the SAME class as the sibling FINDING filed this session (`corpus-suite-harness-companion-copy-not-transitive`). **That is NOT what is happening here**: I copied all three companions in by hand and re-ran directly — the harness-side noise goes away, and a genuine SCRIP/oracle divergence remains underneath it:

    oracle:  arr = ARRAY['1:1']
             arr[1] = 'alpha'          <- SCRIP never prints this line
             PASS: 4 array dump
    scrip:   arr = ARRAY['1:1']
             PASS: 4 array dump

Both m3 and m4 agree with each other and both omit the per-element line for the ARRAY case specifically. The TABLE case (single-key `t['key']`) and the nested TABLE case (`t2[1]`, `t2[2]`) both correctly enumerate and print their element lines immediately below the header — only the ARRAY path fails to iterate its elements. This reads as a real, narrow gap in whatever runtime/library routine implements `XDump`'s array-vs-table element-enumeration (table iteration works; array iteration over the same dump machinery does not), not a harness artifact.

## Why I did not cure it myself

Out of scope for my row (SPAN/BLANKS/DIFF misc-semantic entries); I have no context on the XDump subsystem's implementation or which HQ's lane owns it, and per this session's own new law (THE DEMO-SET CONTROL ARM, `.github` `07195ce5`) a fix touching shared dump/enumeration machinery may need the demo-set control arm run beside it — bigger than a drive-by fix.

## Blast radius

One master-suite entry currently red and uncounted (no xfail marker), contributing to the SNOBOL4 gate's current FAIL=1(m4)/FAIL=2(m3) alongside the unrelated `simple_output_67` harness-gap finding filed this session. Anyone landing SNOBOL4 work right now will see this same red and should not mistake it for something their own change caused.

## Routed

hq_T (my HQ), asked, topic `xdump-array-dump-omits-elements`, with this file's path.
