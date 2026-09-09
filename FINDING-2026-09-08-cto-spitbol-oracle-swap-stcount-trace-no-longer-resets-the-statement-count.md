# FINDING 2026-09-08 (cto, MODE NONET) — the SPITBOL oracle swap: `TRACE('STCOUNT','KEYWORD')` no longer resets the statement count

Row `snobol4-trace-keyword-fnclevel-stcount-errtype-on-every-system-write` (hq_P's), STCOUNT half. The FNCLEVEL half and the trace-function arm landed as SCRIP `586722457` (FINDING-2026-09-08-cto-keyword-tracing-fires-on-the-systems-own-writes-and-spitbol-fails-its-own-manual-on-stcount.md), which measured the defect on both SPITBOL builds and asked the ceo for the ruling. The ceo ruled at 18:53 CDT: fix the oracle under the ORACLE-SWAP PROCEDURE (RULES.md § Oracles FACT RULE, Lon 2026-09-05: *"when the oracle is broken, we always stop and fix it"*; Lon 2026-09-08 to the cto: fix SPITBOL where it fails its manual), never imitate the defect, and take the END-counting cure first so refs are re-cut once. The END cure is SCRIP `397b3bd22`. This is the swap. Nothing in SCRIP changed; SCRIP already printed the manual's numbers.

## The defect, in SPITBOL's own terms

The manual (v3.7, Tutorial p150; ch16 Keywords) defines `&STCOUNT` as the total number of statements executed, incremented by one as each statement begins execution. SPITBOL keeps that total in two parts: a coarse value `kvstc` (maintained as stlimit minus count) and a fine breakout counter `stmcs`/`stmct` that `stmgo` decrements per statement and folds into `kvstc` at each breakout (`stgo4`). Reading the keyword (`acs19`) adds the two. Two sites lost the total:

1. **`trc09`** — set/reset stcount trace — called `stgcc` to recompute the breakout counters (every statement breaks out while STCOUNT is traced) WITHOUT first folding the statements already in the fine counter into `kvstc`. Every statement since the last breakout was forgotten at each `TRACE('STCOUNT',...)` and each `STOPTR('STCOUNT',...)`. The `&STLIMIT` assignment path (`asg16`) already performs that fold before its own `stgcc`, and the nine lines added at `trc09` are that fold, verbatim in shape.
2. **`stgo4`** — ran the keyword trace (`ktrex`) before `stgo5` reset `stmct`, so a traced value read the current statement twice: once in the coarse decrement just made for it, once as the still-unreset fine counter. One `mov stmct,stmcs` now precedes the trace.

## Witnesses

- Reads (statement k should read k): `OUTPUT = &STCOUNT` ×2, `TRACE('STCOUNT','K')`, `OUTPUT = &STCOUNT` ×2, `STOPTR('STCOUNT','K')`, `OUTPUT = &STCOUNT`, `END`. Stock upstream and the pre-swap fork: `1 2 2 3 5`. The cured fork and SCRIP: `1 2 4 5 7`.
- `.github/probes/trace/trace_keyword.sno` (the row's DONE-WHEN through `scripts/util_sno_trace_witness.sh`): the traced values were `3 4 5`, are `9 10 11`; PASS m3, PASS m4, byte-identical to the oracle.
- Every probe under `.github/probes/trace/` graded against the backup binary and the swapped one: the set of probes that differ from SCRIP is identical except `trace_keyword`, which moved from DIFF to IDENTICAL. The swap moved exactly one thing.

## Blast radius, measured

A census of 948 corpus SNOBOL4 programs (every `*.sno` under `corpus/`, `-bf`, stdin closed, 5 s, old binary vs new): 945 byte-identical with the same rc. Three differed: csnobol4 `setexit4` (traces STCOUNT; `stmts executed 34` where the old binary said 21 — the class), snoflake `gimpel-rseason-baseball` (a wall-clock stamp), `programs/lon_cherryholmes/sno/peg_solitaire` (both time out at 5 s, cut at different points). The SNOBOL4 master has no entry that traces STCOUNT; the gimpel `_driver` refs carry no STCOUNT text; csnobol4 grades against pinned refs. So no board running at the swap minute was moved by it. The ceo's pre-measured list of programs that TRACE STCOUNT (gimpel TPROFILE/FPROFILE, snoflake gimpel-implementation-and-timing and gimpel-l-two-compiler, csnobol4 setexit4/setexit6/keytrace/t, lon_cherryholmes debug) is the set a lane re-measures; several are already outside the baseline.

## The procedure, as executed

1. Local clone `/home/claude_cto/x64` (from `git@github.com:snobol4ever/x64`, HEAD `0e9f351`); stock `make sbl` reproduced the shared binary byte for byte before any edit.
2. Two edits to `sbl.min`; rebuilt; the probe and the witness measured on `./sbl`.
3. Fork commit `2d82089` (sbl.min and bin/sbl), pushed to origin.
4. Broadcast to every postoffice inbox at `20260909T033439Z` (22:34:39 CDT) naming the change, the blast radius, and the backup.
5. Backup `bin/sbl.bak-20260909T033439Z` beside the binary; installed binary and `sbl.min`; post-install probe `1 2 4 5 7`; the shared tree `/home/resources/x64` fast-forwarded to `2d82089` (its committed `bin/sbl` is the installed bytes, md5 `cfde224b6bcc`; pre-swap `bc694a0cc699`).
6. Receipts: RULES.md ORACLE QUIRKS RECORD **QUIRK 2** (cured in our fork, stock still carries it); `/home/resources/ORACLES.md` top line; corpus `setexit4.ref` re-cut (lines 37–38 only). setexit4 stays red for SCRIP on its own flow — the oracle takes a keyword-operand ERROR 251 path SCRIP does not — a separate row for hq_P's lane.

Rollback, if ever needed: `cp -p /home/resources/x64/bin/sbl.bak-20260909T033439Z /home/resources/x64/bin/sbl`.
