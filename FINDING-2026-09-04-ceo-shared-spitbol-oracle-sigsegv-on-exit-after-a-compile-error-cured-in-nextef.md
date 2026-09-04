# FINDING — CURED: the shared SPITBOL correctness oracle SIGSEGVed on exit after a compile error; the cause was the EXTFUN exit-time heap walk in `nextef`, cured in the fork (`snobol4ever/x64` `c0dc231`) and swapped in by the ORACLE-SWAP PROCEDURE

**ceo, 2026-09-04 18:18 CDT, on Lon's word (2026-09-04 18:05, in-chat to ceo, verbatim: *"Fix those oracle crashes,"*). Row `snobol4-oracle-sbl-bf-sigsegv-on-error-212-recovery-cuts-refs-silently` (seat07's find, FINDING-2026-09-04-seat07-rung04-…-and-oracle-sigsegv.md § 2).**

## The symptom, measured

| witness | shared `x64/bin/sbl -bf` (before) | bench oracle (official + 2 patches) | pristine 4.0f |
|---|---|---|---|
| green-book p.72 literal subject (`"MASH" "M" = "B"`, ERROR 212) | rc=139 on 10 of 12 runs (rc=231 otherwise) | rc=231, 6 of 6 | — |
| SPITBOL testpgms-test1 (Diagnostics Phase One) | rc=0, 140 lines | rc=0, identical | — |
| testpgms-test2 (Diagnostics Phase Two) | rc=139 on 2 of 3 runs | rc=231, ERROR 214 at line 239 | rc=1 "No END statement found" (its `-f` inverts) |
| testpgms-test3, -test4 | rc=139 after 19 lines | rc=231, ERROR 214 at line 1 (the stray `./*` first line of the split files) | — |

A seat cutting a `.ref` from any error-exit shape on an unlucky run got a truncated ref SILENTLY; the crash blocked SPITBOL's own test suite (row `snobol4-spitbol-testpgms-four-programs-to-100-percent-both-modes`: `graded=1 oracle_crash=3` at mint).

## The cause

gdb: `nextef ()` ← `zysej ()` ← `sysej ()` — the EXIT routine. The fork builds with `-DEXTFUN=1` (LOAD() support, B-231…B-233); the bench and pristine binaries do not, so they never run this code. At exit, `zysej` calls `scanef()` then `while(nextef(&bufp, 1))` to run the shutdown callbacks of LOAD()ed external functions. `nextef` walks the WHOLE dynamic block heap from `dnamb` to `dnamp`, calling MINIMAL `BLKLN` on every block to step to the next. After a compile-error exit the region is not a well-formed run of blocks: `BLKLN` returns a junk length, `scanp` strides into junk, and the next `scanp->scb.sctyp` read faults — the faulting `rax` was `0x464cc57ef7bfffec`, ELF-header bytes (`\x7fELF`), i.e. the walk had landed inside a mapped shared object. The fork's 2026-03-23 commit `2d4554a` ("Fix segfault-on-exit in nextef(): SET_WA(scanp) not SET_WA(type)") had made the walk *usually* survive and added a "skip one word on unknown type" arm, which is exactly how a walk strides through junk.

## The cure (`osint/syslinux.c`, 9 lines)

1. `static int ef_loaded`, incremented in `loadef` when a function node is built. In `nextef`, `io == 1 && ef_loaded == 0` returns at once: no callback can exist, so there is no reason to walk the heap at exit — and every program that never LOAD()ed (all of the corpus but the fork's own `test_spl_add.sno`) takes this path.
2. The walk BREAKS, never skips, on `blksize == 0`, a misaligned `blksize`, or a stride past `dnamp`.

## Proof on a private copy (`cp -a` to `/home/resources/x64-private-ceo`, `make sbl` 3 s), then the shared tree

- ERROR 212 witness: 12 of 12 runs rc=231 (was 10 of 12 rc=139).
- testpgms 1–4: rc and output BYTE-IDENTICAL to the bench oracle (test1 rc=0 140 lines; tests 2–4 rc=231 with their ERROR 214).
- `test_spl_add.sno` (LOAD() path, callbacks): identical output to the old binary (`PASS: spl_add(3,4) = 7`).
- The shared tree's build (`c0dc231`, `make sbl`): 12 of 12 clean on the witness while the old `bin/sbl` beside it still read 139 on 1 of 3.

## What it cannot change

Every byte a program prints is printed before `zysej` runs, so no non-crashing program's output can differ; the only observable change is that crashes become the clean error exit the bench binary already produced. The re-baseline (procedure step d) is therefore the two live-graded suites: gimpel (hq_C) and testpgms (hq_T/hq_P) re-run on the new binary, plus the ladder's next ref cut.

## The swap record

Procedure (RULES.md § Oracles): (a) fleet-quiet boundary — QUARTET, all seats stopped 18:03, the swap landed before the FLEET-16 role telegrams; (b) Lon's go — *"Fix those oracle crashes,"*; (c) announcement to all 20 mailboxes 18:16 (`oracle-swap-announcement-1825`); (d) this FINDING and the ORACLES.md line are the re-baseline notice; the old binary is kept as `bin/sbl.bak-<stamp>`.
