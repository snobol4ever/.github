# FINDING 2026-08-28 seat06 — `test_gate_call2bb_stub_regime.sh` and `test_gate_wreg_claim_binary.sh` are RED at HEAD, independent of the probe-consolidate-bb conversion that surfaced them

**Date:** 2026-08-28 · **Seat:** seat06 (row `probe-consolidate-bb`) · **Tree:** SCRIP at HEAD (`git status`: up to date with origin/main, clean before this session's edits), fresh `make pristine`, `RT_OPT=-O0`.

## Headline

While re-pointing these two gates to survive the probe/bb suite conversion (they hardcoded exact paths
into `corpus/probe/bb/probes/`, now retired), both gates came back RED under the new file-resolution path.
**Verified this is NOT caused by the conversion**: running the exact same checks directly against the
**original, untouched, not-yet-deleted files at their original paths**, on the exact same fresh pristine
build, reproduces the identical failures. These are pre-existing regressions at HEAD, not artifacts of the
suite conversion or of `corpus_suite_harness.py extract`.

## Evidence

**`test_gate_call2bb_stub_regime.sh`** (tests `DEFINE`'s stub blob under `SCRIP_STMT_FRAME=1
SCRIP_CALL2BB=1`, witnesses `test_sno_call2bb_1`/`_2`):

```
$ SCRIP_STMT_FRAME=1 SCRIP_CALL2BB=1 ./scrip --run corpus/probe/bb/test_sno_call2bb_1.sno   # ORIGINAL file, original path, untouched
0
0
$ ./scrip --run corpus/probe/bb/test_sno_call2bb_1.sno                                       # same file, default (ungated) mode
10
42
```
Expected `10`/`42` (matches the oracle and the default-mode `.ref`); the gated path alone produces `0`/`0`.
The gate's own m4 checks (`proc_DOUBLE_α:` stack-frame byte count) fail identically. Full gate output after
re-pointing (same result as against the original file, confirmed above):
```
PASS m3 default  dbl
FAIL m3 gated    dbl: got [0 0 ] want [10 42 ]
FAIL m3 gated    fib: got [  ] want [55 1 ]
FAIL m4 gated stub kt: got [] want [48]
FAIL m4 default stub kt=[] must be legacy != 48
FAIL m4 gated    dbl: got [0  ] want [10 42 ]
GATE RED
```

**`test_gate_wreg_claim_binary.sh`** (disassembles the runtime slab at `bb_seal` for 19 named DEFER/ARBNO
witnesses, asserts every r10/r11 instruction shape is allowlisted):

```
$ gdb -batch -x g.cmds --args ./scrip --run corpus/probe/bb/probes/D09.sno   # ORIGINAL file, original path, untouched
$ objdump -D -b binary ... | grep r1[01] | ...
mov N(%rcx),%r10      <- NOT in the allowlist
mov N(%rcx),%r11      <- NOT in the allowlist
```
Same unallowlisted `mov N(%rcx),%r10`/`%r11` shapes appear on D09, D12, and X02 (the `--quick` set) against
the original untouched files. The re-pointed gate (extracting the same three witnesses from
`bb_probes.sno`/`.ref` via the harness) reports the identical shapes — no divergence introduced by extraction.

## What this means

Both gates are currently RED at HEAD for reasons entirely unrelated to the probe/bb suite conversion: a
real regression somewhere in the CALL2BB/STMT_FRAME stub-compilation path (first gate) and in the
DEFER/ARBNO r10/r11 wiring shapes the WREG allowlist was built against (second gate). Neither was caught by
this session's `make pristine` + `test_gate_*` run because — per this row's own task, not the general
gate suite — these two specific gates were not part of `make test`'s blocking set, and nobody had reason to
re-run them recently. Not root-caused here: that is real compiler-codegen debugging (ASM-DIFF-FIRST per
RULES.md), out of scope for a corpus-consolidation row, and belongs to whoever owns the CALL2BB/WREG
feature area.

**This finding does NOT block `probe-consolidate-bb`.** The re-pointed gates faithfully reproduce
whatever the original files would have reported — they are telling the truth about a real, independent
defect rather than a false green or a conversion artifact. Sent non-blocking to hq_C alongside the row's
completion; whoever owns CALL2BB/WREG codegen should treat this as a fresh, unfiled regression and start
from the exact repro commands above (both are two-line reproductions with no suite/harness involvement
needed at all).
