# FINDING — 2026-08-12t (s48, Claude Sonnet 5, SOLO) — EARN-1's diagnostic was unreachable for every op-kind it exists to classify; fixed. EARN-2 census landed on top of the fix: OWED=214, UNEARNED=36. A third thing surfaced building it — genuine, unexplained, NOT the same bug — flagged and left open.

## (1) EARN-1's `SCRIP_EARN_DIAG=1` column was dead code

`frame_need_of()` (emit.cpp:662) returns 1 for exactly five op-kinds: `IR_MATCH_ARBNO`,
`IR_MATCH_FENCE1`, `IR_MATCH_ASSIGN_IMM`, `IR_MATCH_ASSIGN_COND`, `IR_MATCH_ASSIGN_SAVE`.
The verdict is staged and the `[EARN]` diagnostic line is printed from a single choke,
`bb_prepare(IR_t *nd)` (emit.cpp:674-683).

Full-tree grep of every `bb_prepare(` call site (`grep -rn "bb_prepare(" src/`) found 21
call sites, ALL in one dispatch switch in emit.cpp, and NONE of them for the five
op-kinds above. The switch arms that actually emit those five kinds (lines 1012, 1052,
1053, 1054, 1056 at the pre-fix HEAD) go straight to `bb_emit_x86(...)` — `bb_prepare`
is never invoked from any of them. Net effect: `frame_need_of`'s `return 1` branches
were live code with zero observers — `[EARN] need=1` could not print, on any program,
ever, since s47's landing. EARN-1's own gate ("emitted bytes byte-identical to HEAD")
still passed correctly, because `op_frame_need` has no reader yet either — the gate was
never testing the diagnostic's reachability, only emission neutrality. Same failure
CLASS as RULES.md's MONITOR-FIRST law exists to catch (instrument dark for the class
under test) — it just hadn't been named for this instrument yet.

**Fix** (SCRIP `e73f66b4`): `bb_prepare(nd);` inserted as the first statement in the
five case-arms. Verified safe before landing: the four fields `bb_prepare` zeroes
(`bb_ls`/`bb_rs`/`bb_op_lbl`/`bb_lk`) are written ONLY inside `bb_prepare` itself
(full-tree grep, including the `_.` template-macro spelling); none of the three
templates these five arms call (`bb_match_arbno`, `bb_match_capture`, `bb_match_fence1`)
appear anywhere in the reader list.

**Gate before landing:** byte-identical `.s`, diag OFF (default), prefix-vs-postfix
BINARY (not source — built both, compared outputs), correct invocation
(`--compile FILE > out.s`, per `util_regen_crosscheck_s_artifacts.sh`, NOT `-o`, which
links straight through and leaves no `.s`) — crosscheck/patterns 122/122, probe/bb
14/14, zero diffs, zero rc mismatches.

**Verified working after the fix:** `SUBJ ? ARBNO(LEN(1))` → `op=93(ARBNO) need=1
haz=1`. `FENCE(...)` → `op=96 need=1`. A `$`-capture spanning an ARBNO → `op=99
need=1 haz=1`. A bare `*P` DEFER → `op=104 need=0 haz=1` — DEFER is itself hazardous
material (haz=1) but never the frame OWNER (need=0), which is the diagnostic's first
empirical confirmation of Ruling (1) in GOAL-RBP-EARN.md ("`*P` owns nothing; the
frame belongs to whoever must read a cell after it's run").

## (2) EARN-2: census re-cut from raw frame count to UNEARNED/OWED

Built on the now-working diagnostic (SCRIP `5547de99`, `scripts/test_census_rbp_frames.sh`
rewritten in place, not forked — same file, same lineage as the PT-0 raw-count
instrument, whose region-classification AWK is still needed for the ESTABLISHED side).

**Opcode table is machine-derived from `IR.h` fresh every run** (the script's own
`awk` pass over the real `typedef enum`), not a baked-in table — refuses to run if
the five names it needs aren't found, rather than silently drifting if the enum is
ever reordered. Cross-checked against 7 independent empirical `[EARN]` firings
before being trusted (93=ARBNO, 96=FENCE1, 99=ASSIGN_IMM, 100=ASSIGN_COND,
101=ASSIGN_SAVE, 87=LEN, 104=DEFER — all matched).

**Design decisions made this session** (stated to Lon, proceeded on his go-ahead —
see chat, not reproduced here):
- OWED = need=1 tally for {ARBNO, ASSIGN_IMM, ASSIGN_COND, ASSIGN_SAVE}. FENCE1
  EXCLUDED — needs=1 always, but is established today via its own keeper mechanism
  (`bb_match_fence1.cpp`'s explicit LEAVE), unlike the other four which have NO
  per-node established mechanism at all today (ARBNO's carve died at DEL-T1 per the
  s46 hand-check; ASSIGN_* never had one) — so every one of the four counted firings
  is unpaid by construction.
- UNEARNED = PAT-BLOB-class established count only (T1-T3 deletion-target remnants).
- KEEPER CLASS (MAIN=STATEMENT/MATCH_BEGIN/FENCE1, AB-ACT=FUNCTION) reported
  separately, counted toward NEITHER debt — EARN-8 hasn't ruled on STATEMENT/FUNCTION
  yet, and scoring them as UNEARNED here would silently answer a question EARN-8
  owns. ⛔ KNOWN GAP, stated in the script header: MAIN-class label scanning can't
  separate STATEMENT's establishment from FENCE1's — both land in the same unlabeled
  `main:` block. FENCE1's EARNED status is asserted from the design doc + its
  unconditional need=1, not independently proven per-construct — the `[EARN]` line
  carries no node id, so a real proof needs that added first.
- m3 (BINARY in-process) ESTABLISHED side: NOT instrumented. No persisted artifact to
  disassemble (checked first: `test_census_wreg_artifacts.sh`'s objdump target is
  `libscrip_rt.so`, the fixed runtime, not per-program JIT'd code — doesn't transfer).
  m4 stands in for both modes' ESTABLISHED count, licensed by the product's own 1:1
  mode contract — flagged, not silently assumed.

**Baseline this HEAD** (213 files: crosscheck/patterns, probe/bb, probe/earn0,
programs/snobol4/demo, benchmarks/snobol4):
```
OWED      = 214   (arbno=100  assign_imm=4  assign_cond=110  assign_save=0)
UNEARNED  = 36     (PAT-BLOB established -- T1-T3 deletion-target remnants)
KEEPER, not counted, EARN-8 pending: MAIN=174  AB-ACT=0  PROC=20
FENCE1 need=1 total: 66  (asserted earned, not independently proven -- see gap above)
```
`owed` is expected to be large and to rise further as classification coverage
improves — this is the s29 phase note's prediction, and it held.

## (3) A third thing, found building the census, deliberately kept separate

The census script spot-checks m3 vs m4 diag-stream parity per file (medium-invariance
check). Two DIFFERENT things showed up under that check, and conflating them would
have poisoned the census — they are reported here as two distinct, sized findings.

**(3a) RULED OUT, not EARN's:** `scrip --run` (mode-3) crashes (rc 134/139) on ~41/213
corpus files. Verified PRE-EXISTING and NONDETERMINISTIC before concluding anything —
built a saved pre-fix binary (`git stash` around the EARN-1 fix, rebuilt, saved both
binaries) and ran each candidate file 6x per binary. Both binaries scatter across rc
0/134/139 on the SAME file across repeated runs, e.g. `153_pat_operand_edge_matrix`:
prefix `134 139 134 0 134 0`, postfix `134 0 134 0 134 134`. Smells like the ASLR-class
flakiness this repo has hit before (`FINDING-2026-08-01-*-ASLR-ROOTS-M4-OSCILLATION`).
Not chased further — out of GOAL-RBP-EARN's scope. **Flag for whoever owns mode-3
runtime stability; this seat did not identify which goal that is and did not go
looking (RULES: read only the goal Lon names).**

**(3b) OPEN, genuine, NOT root-caused — this is the one worth a dedicated look:** 11
files where BOTH modes exited 0 but the `[EARN]` diag stream itself differs between
m3 and m4 for the identical program: `porter`, `roman` (×2, different corpus dirs),
`treebank-array`, `treebank-list`, `func_call`, `func_call_overhead`,
`indirect_dispatch`, `mixed_workload`.

Two sub-patterns observed, not yet shown to be the same mechanism:
- **Pattern-free programs** (`func_call.sno`, 17 lines, no `?` match anywhere): m3's
  diag stream is an EXACT verbatim doubling of m4's — same 3 lines, printed twice
  back to back (`cmp` confirmed `m4+m4 == m3` byte-for-byte). Both firings show
  identical `need` values (both 0, for `IR_COERCE_NUMERIC`/`IR_CMP_TEST` — neither is
  a classified kind). Program's actual output (`result:`/`ms:` lines) printed ONCE,
  correctly — so this is emission-time duplication, not a runtime re-execution.
  Ruled out as the cause: `gva_collect_graph` (emit.cpp:3073) — read its body
  directly, it never calls `bb_prepare`, it's a standalone scan for
  `IR_VAR`/`IR_ASSIGN`/`IR_VAR_REF` names only. Ruled out: the lazy PAT-blob
  `emit_chain(..., NULL, "pat_flat")` path (scrip.c ~1602) — irrelevant, this program
  has no pattern constructs to lazily compile.
- **Pattern-bearing programs** (`roman.sno`): NOT a clean doubling (14 m3 lines vs 11
  m4 lines — `m4+m4 != m3`). The extra lines are pattern-family ops (`LEN`, `RPOS`,
  `BREAK`, `ASSIGN_SAVE`, `ASSIGN_COND`, `DEFER`), which func_call's divergence never
  touched. `ASSIGN_COND` is one of the five classified kinds — but every extra
  occurrence actually inspected showed `need=0`, so nothing sampled so far would have
  changed an OWED count even if m3 had been the tallying source. Working hypothesis,
  UNVERIFIED: on-demand JIT compilation of stored/`*`-deferred pattern blobs under
  mode-3's in-process model, which mode-4's ahead-of-time text/gcc model can't defer
  the same way. Not confirmed — did not trace far enough to prove it, and the
  divergence was not checked across all 11 files for a case where an extra line shows
  `need=1` (which WOULD threaten a future m3-sourced census, though not this one).

**Impact on (2)'s numbers: none.** OWED/UNEARNED were computed from m4 exclusively;
m4 never showed either (3a) or (3b) in anything tested this session.

## State at handoff of this finding

SCRIP: 2 commits ahead of the cloned HEAD (`0954198b`), both local only —
`e73f66b4` (diag fix) then `5547de99` (census re-cut). Not pushed — this session was
instructed to hold the push/credential request to session end.
.github: unchanged by this seat except this file; HEAD verified == origin before
writing it (no concurrent-seat collision this session).

**Next, no strong pull recorded either way:** (a) root-cause 3b properly — probably
fast, probably instructive, given func_call already narrowed it to "not
gva_collect_graph, not the pat_flat lazy path for pattern-free programs" in a few
targeted greps; (b) EARN-3 (anchor propagation) per the s47 cursor's own framing as
the higher-leverage next rung; (c) add a node id to the `[EARN]` line to close the
FENCE1 correlation gap noted in (2), which would also make a real 3b root-cause
easier to nail down positionally instead of by line-count diffing.
