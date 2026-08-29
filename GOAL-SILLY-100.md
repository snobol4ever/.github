# GOAL-SILLY-100 — Silly SNOBOL4 (CSNOBOL4 hand-port oracle project) — CLOSED/ABANDONED

⛔⭐⭐ **RULED CLOSED 2026-08-29 — Lon, verbatim in substance, in-chat to CEO: "Leave SILLY folder deleted,
it was a failed experiment."** Authority: `.github FINDING-2026-08-29-ceo-silly-stays-deleted-failed-
experiment-lon-ruling.md`. **No restore, to either repo, ever.** This file is now pure history — the
design/progress record below is preserved for the record, not as resumable work. Do not start any step
below; do not resurrect this project under this or any other name without a fresh Lon ruling.

## What happened, for the record

**`SILLY/`'s entire 25-file C tree was deleted from BOTH SCRIP and corpus on 2026-08-29** by two
independently-reasonable, uncoordinated repo-hygiene commits, six minutes apart:
```
corpus 29e47ac16   "miscellaneous/SILLY: add, relocated here from SCRIP/SILLY"
SCRIP  ee0f1508    "Remove SILLY: relocated to corpus/miscellaneous/SILLY"          (09:50:49)
corpus e42689daf   "Delete miscellaneous/SILLY: C source does not belong in corpus" (09:56:48, +6min)
```
Full incident report (also carries these same recovery commands, for whoever investigates the deletion
itself rather than the project): `.github FINDING-2026-08-29-seat13-silly-snobol4-source-deleted-from-
both-repos-no-live-home.md`. **Git history is the archive, per the ruling — this is not a live recovery
path, just the record of where the bytes last existed:**
```bash
git show ee0f1508~1:SILLY/main.c              # SCRIP, last commit with the tree present
git checkout ee0f1508~1 -- SILLY/             # SCRIP, historical reference only
git checkout 29e47ac16 -- miscellaneous/SILLY/  # corpus, same content, alternate source
```
⚠️ **The cross-repo composition hazard this deletion exposed is a real, standing class regardless of this
ruling** (hq_B's framing, `.github` mail): two locally-correct actions in two different repos' histories
composed into total, silent loss — no single `git log` in either repo shows the composition, and no
instrument was watching the aggregate. Abandoning SILLY does not moot that lesson for the next
cross-repo relocate-then-hygiene sequence.

## ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — applies if/when this resumes

A C Byrd box (C BB) is any C function `DESCR_t foo(void *zeta, int entry)` implementing four-port
(α/β/γ/ω) logic. Zero of these anywhere in the *SCRIP compiler* codebase — all Byrd boxes are x86
assembly emitted at runtime by the emitter (only `icn_lazy_box`/`icn_bb_dcg` are exempt infrastructure).
**This rule governs `SCRIP/src/`, not SILLY** — SILLY is a standalone hand-port of CSNOBOL4's own SIL
source (a different, older implementation technique entirely, evaluated only against the external SIL
spec + oracle `snobol4.c`, never mixed into the compiler's own emitter). Carried here only because all 4
source files led with it; SILLY's own code has no BB shape to violate in the first place.

## What this is

One project, four coordinated sub-goals, evaluating a hand-written C port of CSNOBOL4's SIL
(SNOBOL Implementation Language) source against two grounds of truth simultaneously: the SIL spec itself
(`v311.sil`) and its own machine-generated C translation (`snobol4.c`) — three-way, never two-way.

- **SWEEP-FORWARD** / **SWEEP-BACKWARD** — independent watermark walks through all 12,293 SIL lines
  (forward from line 955, backward from line 1), verifying each labeled block already translated is
  *correct*. No convergence point, no handoff between them.
- **COMPLETE** — orthogonal to the sweeps: tracks *completeness* (is every block translated at all, stub
  or missing vs. real), not correctness of what's already there.
- **SYNC-MONITOR** — a separate verification tool: an event-level lock-step comparator running CSNOBOL4
  (oracle, by construction — the *only* SCRIP-adjacent context where CSNOBOL4 outranks SPITBOL) against
  Silly, function-call by function-call, to name the first diverging function directly instead of
  bisecting by hand.

## Corrected paths (fix in the SAME commit that next touches source, per this row's citation-sweep rule)

All 4 source files cited **`src/silly/`** or **`SCRIP/SILLY/`** — both stale even before today's deletion
(the live convention at time of writing was top-level `SCRIP/SILLY/`, itself now gone, see blocker above).
**Filename convention was also wrong in every source file**: none of them use a `sil_*.c` prefix as all 4
files assumed — real files used CSNOBOL4's own module names (`main.c`, `func.c`, `arena.c`, `define.c`,
`platform.c`, `expr.c`, `asgn.c`, `trace.c`, `argval.c`, `forwrd.c`, `patval.c`, `arrays.c`, `data.c`,
`scan.c`, `io.c`, `cmpile.c`, `pred.c`, and others — 25 total, confirmed against the pre-delete tree via
`git show 29e47ac16 --stat`, reproduced in the FINDING).

**External SIL spec + oracle** (unaffected by the SILLY deletion — this is a separate, shared resources
tree, confirmed present):
```
/home/resources/snobol4-2_3_3_tar/snobol4-2.3.3/v311.sil      # SIL spec, 12293 lines
/home/resources/snobol4-2_3_3_tar/snobol4-2.3.3/snobol4.c     # generated C ground truth
```
All 4 source files instead said `/home/claude/work/snobol4-2.3.3/...` (a D-17 PORTABLE-HOME violation —
hardcoded a single seat's home — and also just the wrong location; no session needs to `tar -xzf` a
private copy, the shared resources tree already has it). CSNOBOL4 oracle binary itself:
`/home/resources/csnobol4/` (also shared, also unaffected by the SILLY deletion).

**Build gate** (path TBD until source is restored to a chosen repo — update this line, don't guess):
```bash
gcc -Wall -Wextra -std=c99 -g -O0 <SILLY-dir>/*.c -lm -o /tmp/silly-snobol4 -I <SILLY-dir> 2>&1 | grep -E "error:|warning:"
# must be empty
```

**Two now-dangling scripts still hardcode the old SCRIP-side path** — `SCRIP/scripts/build_silly_snobol4.sh`
(`$ROOT/SILLY`) and `SCRIP/scripts/test_ss_monitor_silly_vs_csnobol4.sh` — need the same path fix once a
home is chosen; not fixed here (script-lane work, not a GOAL-doc consolidation, and fixing them now would
just re-hardcode a path that may change again pending the restore/abandon call).

## Sub-goal: SWEEP-FORWARD

**Done when:** forward watermark reaches v311.sil line 12293 (skip §20 BLOCKS, lines 7038–10208: jump
7037→10209).
**Watermark at last verified session (2026-08-29, pre-deletion):** line **6927**, next block `RPLACE`.
⛔ The watermark recorded here is the sole authority once restored — re-verify against actual translated
content, don't trust this number blind after any gap.

Methodology: one labeled SIL block per commit, three columns compared simultaneously for every SIL
instruction (spec / oracle C / our C) — two-way (skip the spec, or skip the oracle) is wrong, always all
three. Find next block: `grep -n "^[A-Z][A-Z0-9]*\b" v311.sil | awk -F: '$1>6927' | head -1`.

## Sub-goal: SWEEP-BACKWARD

**Done when:** backward watermark reaches v311.sil line 1 (same BLOCKS skip, opposite direction: at
10209, jump to 7037). Runs fully independently of SWEEP-FORWARD — no convergence, no handoff.
**Watermark at last verified session (2026-08-29, pre-deletion):** line **6427**, next block `CMA2`.

**Known stubs at that watermark (fix when reached, not before):**
| Block cluster | Status |
|---|---|
| `CNVRT`/`CODER`/`CONVE`/`CONVEX`/`CONVR`/`CONIR`/`CONRI`/`CNVIV`/`CNVVI`/`CNVRTS`/`CNVTA`/`ICNVTA`/`CNVTA1-8`/`CNVAT`/`CNVAT2` | ⚠️ stub — all return FAIL |
| `OPSYN`/`BNBF`/`BNCN`/`BNAF`/`BNCF2-5`/`BNYOP`/`BNYOP2-5`/`UNAF`/`UNCF`/`UNYOP`/`OPPD`/`UNBF` | ⚠️ stub — returns FAIL |

Find next block: `grep -n "^[A-Z][A-Z0-9]*\b" v311.sil | awk -F: '$1<6427' | tail -1`.

## Sub-goal: COMPLETE (completeness tracking, orthogonal to both sweeps)

**Done when:** every labeled SIL block (all 12,293 lines, BLOCKS included) has a faithful C translation.
Zero stubs, zero bare `return FAIL` placeholders. Build clean.

⛔ **Do not start Phase 2 (BLOCKS) until SWEEP-FORWARD and SWEEP-BACKWARD both reach done-when.**

⚠️ **This file's own done-when check has a confirmed blind spot** (caught 2026-08-29, verified by direct
per-item reading, not trusted from the grep): the canonical check
`grep -rn "return FAIL; /* TODO\|return FAIL; /* STUB" <SILLY-dir>/*.c` only catches ONE comment style.
At least 5 of the 10 Phase-1 items below use a bare `return FAIL;` with no tracked comment, or a
differently-worded one (`func.c:660`'s `TODO M19`, `func.c:844`'s uncommented stub) — this grep alone
undercounts. **Whoever next verifies completeness must check the Phase-1 checklist items individually,
not trust a single grep pattern's zero-count as proof.**

### Phase 1 — Non-BLOCKS gaps (10 steps; 8 of 10 independently confirmed still-open 2026-08-29 by direct
source reading, not by trusting the checklist's own `[ ]` marks)

**Group A — Compiler re-entry cluster (`func.c`)** — SIL §19 lines 6492–6551, oracle `snobol4.c`
8841–8955. All called functions already exist (`CMPILE_fn`/`SPLIT_fn`/`EXPR_fn`/`TREPUB_fn`) —
previously mislabeled "M19 blocker," that was wrong.
- [ ] A1 `RECOMP` (6492–6494 / 8841–8847) — sets SCL=1, falls into RECOMJ. **Confirmed open**: bare
  `TODO M19` comment at `func.c:660` (pre-deletion), not caught by the file's own done-when grep.
- [ ] A2 `RECOMJ/RECOMT/RECOM1/RECOM2/RECOMF/RECOMN/RECOMZ/RECOMQ` (6495–6531 / 8848–8939) — compiler
  re-entry: alloc code block, run CMPILE loop, SPLIT (~80 lines C).
- [ ] A3 `CODER_fn` stub → real (6530–6533 / 8911–8920) — VARVAL + fall into RECOMJ.
- [ ] A4 `CONVE_fn` stub → real + `CONVEX` (6534–6551 / 8921–8955) — SETAC SCL,2 + RECOMJ; EXPR+TREPUB+
  E-type. **Confirmed open**: `{ return FAIL; }` with no tracked comment at all, `func.c:844`.

**Group B — `DEFFNC_fn` (`define.c`)** — SIL §12 lines 4310–4470, oracle 5530–5665 (~80 SIL lines →
~150 C lines). `INTERP_fn` already exists. Internal labels: `DEFF1..DEFF20`, `DEFFF`, `DEFFC`, `DEFFN`,
`DEFFNR`, `DEFFGO`, `DEFFVX`, `DEFFS1`, `DEFFS2`.
- [ ] B1 Replace `DEFFNC_fn` stub — full argument-binding save/restore + `INTERP` call.

**Group C — `CONVV` (`func.c`)** — SIL §19 ~line 6675, oracle ~8040–8060 (21 lines). String-to-string
conversion in `CNVRT_fn` — currently that path returns FAIL.
- [ ] C1 Translate `CONVV`, wire into `CNVRT_fn`'s STRING→STRING path.

**Group D — Platform XCALL stubs (`platform.c`)** — **confirmed open, all 4**, still bare or
differently-commented FAIL-stubs as of 2026-08-29:
- [ ] D1 `XCALL_IO_FILE` — attach/detach file to I/O unit by name (§15 ~5350).
- [ ] D2 `XCALL_XINCLD` — open include file, push onto input stack (§15 ~5380).
- [ ] D3 `XCALL_GETPMPROTO` — get prototype string for LOAD (§13 ~4490).
- [ ] D4 `LOAD2_fn` stub → real — `dlopen`/`dlsym` dynamic symbol load.

### Phase 2 — BLOCKS feature (new file `sil_blocks.c`; gated behind both sweeps completing)

v311.sil lines 7038–10208 (3,171 lines). Oracle `snobol4.c` has 133 BLOCKS functions (from line 9685)
plus 269 lines of `.IF BLOCKS` inline additions in existing functions.

- [ ] E1 Add BLOCKS constants to `types.h` (full `#define` list: `BL_TYPE 44`, `ORG_ DESCR`, `REG_
  (2*DESCR)`, `TOP_ DESCR`, `FIRST_ (3*DESCR)`, `ELEMENT_ (2*DESCR)`, `NAME_ (2*DESCR)`, `ID_ DESCR`,
  `BL_ (2*DESCR)`, `FRAME_ (3*DESCR)`, `ARRAY_ (4*DESCR)`, `AEDGDT 40`, `EDGDT 41`, `TNDT 42`, `SBDT 43`,
  `SER_ 1`, `PAR_ 2`, `OVY_ 3`, `MERGE_ 4`, `IT_ 5`, `REP_ 6`, `NODE_ 7`, `DEF_ 8`, `PHY_ 9`).
- [ ] E2 Create `sil_blocks.c` skeleton.
- [ ] E3–E135 Translate all 133 BLOCKS functions, one per commit, three-way sync. Oracle order (from
  `snobol4.c` line 9685): `ADD_NP AF_MERGE AFRAME B_PB BMORG4 BMORG5 BMORG6 BMORG7 BCOPY BHEAD BLAND
  BLANK HEIGHT WIDTH DEPTH BLS2 BLOCKSIZ BLS1 BLOKVAL FRONT VER HOR BOX BOXIN BTAIL CAE BCHAR CIR CLASS
  COAG COMPFR DISTR DUMP_B DUMP_A DUP DUPE E_ATTACH EMB_PHY FICOM FIX FIXINL FORCING F_JOIN HOR_REG
  VER_REG NORM_REG GR1 IDENT_SB INIT_SUB INSERT JE_LONGI JE_ORTHO JOIN LOC LRECL CC LSOHN MIDREG MINGLE
  MORE NRMZ_REG N_REG PAR SER OVY MERGE OPS1 CCATB PAR_CONG PRE_SUF PRINTB NEW_PAGE P_BLOCK NP_BLOCK
  REPL SLAB SUBBLOCK STRIP_F T_LEAF IT REP NODE UDCOM DEF UNITS WARNING`.
- [ ] E136 Add inline `.IF BLOCKS` branches to 7 existing functions: `BEGIN_fn`/`INIT_fn` (main.c, print
  BLOCKS version title), `BINOP_fn` (expr.c, BL-type operator dispatch BINOP6/BINOP7), `CMPILE_fn`
  (cmpile.c, `AEQLC BLOKCL,0` parse path), `CONCAT_fn` (asgn.c, `VEQLC XPTR,BL`/`VEQLC YPTR,BL` type
  checks), `DMPK1_fn` (func.c, string-quoting DMPKV/DMPK2/DMPK3), `KEYT_fn` (platform.c, keyword-dump
  string quoting), `data_init()` (data.c, `BLOKCL` keyword + BL type in type tables).
- [ ] E137 Register all BLOCKS functions in `init_syntab()`; add `BLOKCL` keyword.

### Confirmed NOT missing (three-angle gap analysis, 2026-04-11 — worth preserving so nobody re-derives
this list from scratch): `LOCA1`→`GENVAR_fn`(arena.c), `KEYN`/`KEYC`→`KEYWRD_fn`(asgn.c), `RPAD0`→
`rpad_common()`(pred.c), `STOPTP`→`STOPTR_fn`(trace.c), `TRPRT`/`TRI2`/`TRV`/`VALTR1-4`/`DEFDT`/`VXOVR`/
`FXOVR`→`VALTR_fn`(trace.c, multiple inline paths), `FENTR3`→`FENTR_fn`(trace.c), `FNEXT1`→`FNEXT2_fn`
(trace.c), `EXPVJN`/`EXPVJ2`→`EXPVAL_fn`(argval.c), `FORJRN`→`FORWRD_fn`(forwrd.c), `ELEILI`/`ELEMN9`→
`ELEMNT_fn`(expr.c), `EXPR2`→`EXPR_fn`(expr.c), `ENDFIL`→`ENDFL_fn`(io.c, name mismatch only), `SALF`/
`SALT`/`SCOK`→scan.c macros (longjmp targets, not callable), `SCIN1`→`do_SCIN1A`(scan.c), `SORT1`→
`RSORT_fn`(arrays.c), `CHARZ`→scan.c inline, `NAM5`/`PATNOD`→patval.c inline, `SETXIT`→`SETEXIT_fn`
(trace.c), `TRACEP`→`tracep()`(trace.c), `FORRUN`→`forrun()`(forwrd.c), `ARG1`→data.c global (data, not
a proc).

## Sub-goal: SYNC-MONITOR

**Done when:** `hello.sno` runs through the two-way sync-step monitor, both participants reach clean EOF,
controller exits 0, Silly produces correct output.

⚠️ **Oracle exception, this sub-goal only:** CSNOBOL4 is the oracle here by construction (Silly is a
faithful C rewrite of CSNOBOL4's own SIL source — there is nothing else to grade against). Every other
SCRIP goal uses SPITBOL x64 as the oracle; do not port that assumption into this one. **Confirmed NOT a
naming collision with root CLAUDE.md's own IPC sync-step monitor** (`test_monitor_2way_sync_step_bin.sh`
family, used for SCRIP's own mode-3/mode-4 bracketing) — verified 2026-08-29: zero cross-hits for
`sbl`/`spitbol`/`csnobol`/`silly` between the two families. Unrelated infrastructure, same "sync-step"
name, different everything else.

**Location, confirmed live 2026-08-29 (this part of the tree was NOT touched by the SILLY deletion above
— `test/ss-monitor/` lives in SCRIP, separate from the deleted `SILLY/` source dir):**
`SCRIP/test/ss-monitor/`. CSNOBOL4 oracle binary: `/home/resources/csnobol4/snobol4` (shared, not a
per-seat path — the 4 source files' `/home/claude/csnobol4/snobol4` was a D-17 violation).

**Real file layout diverged from the original plan — confirmed present 2026-08-29:** `inject_silly.py`,
`inject_snobol4.py`, `sly_fns.txt`, `ping_test`/`ping_test.c`, `mon_hooks.c`/`mon_hooks.h`,
`monitor_sync.py`, `wrap_snobol4.py`, `Makefile` all exist. **`run_ss_monitor.sh` — named in the original
"files to build" list — does NOT exist**; `inject_silly.py`/`inject_snobol4.py`/`sly_fns.txt` exist and
were never named in that list. Reconcile the checklist against the real layout before resuming, don't
tick boxes against the planned filenames.

- [ ] S-1 Infrastructure builds — gate: `make` in `test/ss-monitor/` succeeds. **Confirmed PASSING
  2026-08-29** (rc=0).
- [ ] S-2 Ping test: controller + two trivial one-function C programs through the monitor, prints
  `MATCH ENTER ping` / `MATCH EXIT ping OK`, confirms FIFO plumbing end to end. **`ping_test` binary
  confirmed present and runs (rc=0, correctly reports missing `MON_EVT`/`MON_ACK` env vars rather than
  crashing) — strong evidence this is functionally close, full controller+FIFO harness pass not
  independently re-confirmed 2026-08-29.**
- [ ] S-3 CSNOBOL4 instrumented (`snobol4-mon` binary), runs `hello.sno` alone, full call trace as
  ground truth.
- [ ] S-4 Silly instrumented (`silly-mon` binary) — **blocked on the SILLY source restoration above**,
  runs `hello.sno` alone, trace compared visually against S-3.
- [ ] S-5 Two-way sync-step: both run together, lock-stepped event by event. First print is `MATCH ENTER
  BEGIN` / `DIVERGE` / `TIMEOUT [sly]`.
- [ ] S-6 `hello.sno` passes to completion, both FIFOs close cleanly, exit 0, `PASS hello.sno`.

**Monitor architecture:** `csn.evt`/`csn.ack` (CSNOBOL4 side), `sly.evt`/`sly.ack` (Silly side) — per
hook, a participant writes `"ENTER funcname\n"`/`"EXIT funcname result\n"` to its `.evt` then blocks on
`read()` from its `.ack`; controller reads one event from each `.evt`, writes `G` to both `.ack` if
names/kinds match, `S` (stop) plus a divergence print if not. Timeout on any FIFO for >10s = that
participant is looping; last event before silence names the never-returning function. Never modify
`snobol4.c` logic — wrapper layer only. Monitor infra stays in `test/ss-monitor/`, never mixed into
`src/`.

## RETIRED NAMES (interlock (b) — every deleted GOAL filename must resolve here)

| Retired file | Content now lives at |
|---|---|
| `GOAL-SILLY-SWEEP-FORWARD.md` | this file, § Sub-goal: SWEEP-FORWARD |
| `GOAL-SILLY-SWEEP-BACKWARD.md` | this file, § Sub-goal: SWEEP-BACKWARD |
| `GOAL-SILLY-COMPLETE.md` | this file, § Sub-goal: COMPLETE |
| `GOAL-SILLY-SYNC-MONITOR.md` | this file, § Sub-goal: SYNC-MONITOR |

## Commit identity / rules (unchanged from all 4 source files)

Always `LCherryholmes` / `lcherryh@yahoo.com`, author and committer. Build gate clean (0 errors, 0
warnings) before every commit. One SIL block per commit for the sweeps; watermark update + `.github`
push before the next block. See root `CLAUDE.md` / `RULES.md` for the full standing rules (D-17
PORTABLE-HOME, commit identity, handoff protocol) — not restated here beyond the SILLY-specific items
above.

## Session Setup (once source is restored)

```bash
bash $S4E_HOME/SCRIP/scripts/install_system_packages.sh
bash $S4E_HOME/SCRIP/scripts/build_csnobol4_oracle.sh
# SYNC-MONITOR only, additionally:
bash $S4E_HOME/SCRIP/scripts/build_spitbol_oracle.sh
bash $S4E_HOME/SCRIP/scripts/build_monitor_ipc_shared_library.sh
bash $S4E_HOME/SCRIP/scripts/build_ss_monitor_harness.sh
```
(corrected from all 4 source files' hardcoded `/home/claude/SCRIP/...` — D-17 PORTABLE-HOME.)
