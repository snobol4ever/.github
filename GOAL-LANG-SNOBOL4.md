# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

**Oracle policy (revised 2026-04-27):** SPITBOL x64 is the **sole**
oracle for scrip development.  CSNOBOL4 is excluded from the
sync-step monitor harness for SCRIP work until `GOAL-CSN-FENCE-FIX`
closes — see that goal for the current FENCE(P) builtin segfault on
nested-recursion patterns.  All harness work proceeds 2-way
(SPITBOL ⇄ scrip) per the updated protocol below.

**Forensic history:** closed rungs are summarized below; full session
narratives live in `archive/ARCHIVE-LANG-SNOBOL4-HISTORY.md` and in git.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

(CSNOBOL4 build dropped from this goal's setup.  If CSNOBOL4 is
needed for an unrelated cross-check, build via
`bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh` ad hoc.)

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Architecture reminder

```
.sno -> sno_parse() -> Program* [LANG_SNO]
    --ir-run  -> execute_program() -> interp_eval()   tree-walk
    --sm-run  -> sm_lower() -> SM_Program -> sm_interp_run()
    --jit-run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol (2-way: SPITBOL + scrip)

CSNOBOL4 is excluded from this harness while GOAL-CSN-FENCE-FIX is
open.  Once that goal closes, the 3-way protocol can be restored;
until then, SPITBOL x64 is the sole oracle.

Step 1 (--monitor) runs EVERY iteration, unconditionally.
Steps 2 and 3 only if Step 1 shows DIVERGE.

```bash
# Build once per session (no csn archive needed for 2-way):
make -C /home/claude/one4all scrip-monitor

# Step 1 -- ALWAYS (2-way harness, csn participant disabled):
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor --no-csn \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 -- only if Step 1 shows problem: OUTPUT probe -> fix -> rebuild -> repeat
# Rebuild: make scrip && make scrip-monitor
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

**Note on `--no-csn`:** if `scrip-monitor` does not yet support a
flag to suppress the csn participant, the controller's startup logic
must be patched to skip the csn ready-pipe wait and the csn record
absorption.  This is tracked under SN-26-bridge-coverage-g sub-rung
"2-way protocol mode" (sequence with the active step there).

---

## Closed rungs — phase summary

Status code: `[x]` = done, `[~]` = deferred/partial, `[ ]` = open.
Full detail for closed rungs lives in the git log. Search by rung id
(e.g. `git log --grep SN-17`) for the commit that landed each.

- **Phase 1 — IR-run** [x] DONE: SN-1..SN-6, SN-14..SN-23 (NAM unification, per-pattern context, expr_eval, recursive patterns).
- **Phase 2 — SM-run** [x] DONE: SN-7, SN-8 (subsystem drivers 51/51; args-on-stack SM opcodes). SN-7-note: literal `beauty.sno < beauty.sno` self-host moved to SN-26.
- **Phase 3 — JIT-run** [x] DONE: SN-9 (JIT/codegen parity; crosscheck 207/207/207 in all three modes).
- **SN-17** porter stemmer gap [x] DONE — IR+SM 100.00% on porter.sno.
- **SN-25** SPITBOL `-f` won't-fix — superseded by SN-30.
- **SN-26b** beauty.sno + minimal `.inc`s installed in corpus.

---

## Open rungs — summaries

### SN-27 — UPPERCASE DATATYPE for SPITBOL x64 (opened 2026-04-21)
**Done-when:** `sbl -b` on `output=datatype('')` prints `STRING` (not `string`). All builtin datatypes return uppercase, matching x32 / CSNOBOL4 / one4all / jvm.
**Fix path:** undefine `.culc` in `sbl.min`, rebuild via `make sbl` (per SN-27a-history).
**Sub-rungs:** SN-27b..g open. **Gate:** Smoke=7, Broker=49, SN-7=51/51, Broad=225/225.
**Dependencies:** none. May share a single pass with SN-30.

### SN-28 — Compact DESCR_t: 16 → 8 bytes (opened 2026-04-21)
**Goal:** halve DESCR_t cell size via arena aliasing (32-bit offsets into an mmap slab). Dual-mode `DESCR_MODE_64` (default) vs `DESCR_MODE_32`. Reference model: Silly SNOBOL4 (`src/silly/arena.{c,h}`).
**Sub-rungs:** SN-28a (macro-ize DESCR field access — defensible standalone refactor) → SN-28b..h open.
**Risk:** MEDIUM-HIGH. **Dependencies:** orthogonal to SN-26, SN-27.

### SN-29 — Beauty under original oracles (partially superseded)
SN-29c/d closed: csnobol4 `a509cd7` and SPITBOL x64 (post-SN-30)
self-hosted the OLD beauty.sno (with `is.inc`/`FENCE.inc`/`io.inc`
includes) to byte-identical output md5 `408fc788ca2ef425fc1f87e26d45a7a5`.
That md5 is **historical** — it does not apply to the post-corpus-7041a14
beauty.sno (those three includes are gone).  New per-runtime md5s
captured session #36 on the cleaned beauty.sno:
SPITBOL x64 `abfd19a7a834484a96e824851caee159` (646 lines, clean run);
CSNOBOL4 segfaults — see SN-26-bridge-coverage-i;
scrip `195f9320d836948a0f21b63a4fc68b08` (523 lines, clean run but
diverges from SPITBOL — see SN-26-bridge-coverage-j).
SN-29 cross-oracle byte-identical state will return only after both
SN-26-bridge-coverage-i and SN-26-bridge-coverage-j land.
Open: SN-29e (idempotency scout — `beauty(beauty_output)` non-byte-
identical, non-blocking) and SN-29f (canonical `.ref` capture, blocked
on Lon's call AND on -i/-j convergence).

### SN-30 — UPPERCASE keyword case for SPITBOL x64 (mostly closed)
SN-30a..e and SN-30g landed; x64 @ `cc68516` accepts UPPERCASE keywords under `-bf` and self-hosts beauty to byte-identical output with CSNOBOL4. Open: SN-30f (explicit regression sweep of SN-7=51/51, Broad=225/225, SN-9c=207/207/207 under new sbl). Supersedes SN-25.

### SN-31 — scrip default case-sensitive [CLOSED 2026-04-24]
`sno_fold_on` flipped 1→0 in `snobol4.l:60`; `opt_case_sensitive` default flipped to 1 in `scrip.c:137`; `--case-sensitive` now a no-op (back-compat). Smoke=7, Broker=49.

---

## Active rung — SN-26-bridge-coverage (opened session #29)

**Done-when:** 3-way harness on `beauty.sno < beauty.sno` advances
to a divergence rooted in runtime semantic disagreement, not
protocol/coverage artifacts. Then hand off to SN-26c-parseerr-h
sub-h2 with the last-agree + first-disagree pair as ground truth.

**Closed sub-rungs:**

- [x] **SN-26-bridge-coverage-a** — csn fire-points landed for all 5 LOCAPT-TVALL sites (NMD4, ENMI3, ATP) + `lvalue_name_id` helper for `<lval>` sentinel on array/table stores. csnobol4 @ `ad993fe`. Smoke `test_smoke_sn26_csn_bridge_c.sh` PASS=1. Closed session #30.

- [x] **SN-26-bridge-coverage-b** — spl fire-points at `asign:asg01` (sbl.min:17596) + `asinp` (17853) + ASCII guard in `spl_vrblk_name`. Critical detail: natural-var fire-points need `sub xr,*vrvlo` to back-step from vrval to vrsto field. x64 @ `3cd2dcc`, one4all @ `5ffd3af7`. Smoke `test_smoke_sn26_spl_bridge_d.sh` PASS=1. SN-30 md5 `408fc788ca2ef425fc1f87e26d45a7a5` preserved. Closed session #32.

- [~] **SN-26-bridge-coverage-c** — Diagnostic run session #33 surfaced scrip's missing fire-point on `subscript_set` / `subscript_set2` (DIVERGE step 24 on `UTF[k]='NO_BREAK_SPACE'` vs `VALUE ARRAY`). Subsumed by -e..-h.

- [~] **SN-26-bridge-coverage-d** — Hand sub-h2 the result. Deferred behind -e..-h.

---

### SN-26-bridge-coverage — open sub-rungs

- [x] **SN-26-bridge-coverage-e — streaming intern on the wire.**
  Closed session #35.  New record kind `MWK_NAME_DEF = 6` carries
  (id -> name bytes) inline on the wire: emitted by each runtime's
  intern_name function on first use, consumed by controllers into a
  per-participant intern table.  No sidecar file is read or written.
  Touch points landed: `monitor_wire.h` (constant + doc); scrip
  `runtime/x86/snobol4.c` (intern_name_bin emits NAME_DEF; mon_at_exit
  drops sidecar dump but keeps MWK_END; SNO_INIT_fn drops
  MONITOR_NAMES_OUT env read); csnobol4 `monitor_ipc_runtime.c`
  (same pattern); x64 `osint/monitor_ipc_runtime.c` (same).
  `monitor_sync_bin.py` rewritten with `read_semantic_record` that
  absorbs NAME_DEFs and acks transparently; legacy CLI mode + sidecar
  refresh logic removed; spec is now `NAME:READY:GO`.  `read_one_wire.py`
  absorbs NAME_DEF and writes optional back-compat names file from wire.
  `test_smoke_sn26_auto_binary.sh` rewritten to verify NAME_DEF-on-wire
  semantics and assert no sidecar gets written.  LABEL records remain
  fully comparison-eligible — a LABEL divergence (different STNO at
  the same step) is a real structural-flow bug and surfaces immediately.
  Gate: Smoke=7, Broker=49, all 7 bridge smokes PASS, SN-30 invariant
  md5 `408fc788ca2ef425fc1f87e26d45a7a5` preserved, negative tests
  confirm all 3 runtimes ignore MONITOR_NAMES_OUT.

- [x] **SN-26-bridge-coverage-f — MWK_LABEL events.** Closed
  session #34. `monitor_wire.h` adds `MWK_LABEL = 5` with
  `name_id=NONE`, `type=INTEGER`, 8-byte LE STNO payload —
  sidesteps label-table reverse lookup. CSN: `XCALLC
  monitor_emit_label,(STNOCL)` in `v311.sil INIT` (post-`MOVA
  STNOCL,XCL`); hand-applied to `snobol4.c` and `isnobol4.c`.
  SPL: `sysml exp 0` declared in `sbl.min`; `mov wa,kvstn / jsr
  sysml` fire-points in `stmgo` and `stgo3`; `int.asm` syscall id
  42. scrip: `mon_emit_label_bin()` helper called from
  `interp.c:execute_program` (--ir-run), `sm_interp.c SM_STNO`
  (--sm-run), `sm_codegen.c h_stno` (--jit-run). Gate
  `test_smoke_sn26_label_flow.sh` PASS=5 (csn=3 LABELs, sbl=4,
  scrip ir-run=3, sm-run=4, jit-run=4 — SPL counts END as a
  stmt). All existing bridge smokes updated for new record
  ordering and PASS. Smoke=7, Broker=49 preserved. SN-30
  beauty md5 `408fc788ca2ef425fc1f87e26d45a7a5` preserved.

- [ ] **SN-26-bridge-coverage-g — symmetric lvalue coverage.**
  scrip is missing the subscript-set fire-point. Land in
  **interp.c callers**, not inside `subscript_set` helper, so the
  base name (`s->subject->children[0]->sval`) reaches the wire as
  the real name (e.g. `"UTF"`), not an `<lval>` sentinel. Same
  treatment for SM-run path if subscript-set fires through it.
  Audit `&keyword=X`, DEFINE-arg binding, DATA/DEFINE/OPSYN/FIELD
  identifier creation per the latent extras note. Gate: new
  `test_smoke_sn26_scr_subscript_bridge.sh` PASS=1 on
  `a<1>='x' / a<2>='y' / d<'k'>='z'` (3 VALUE records, names
  `a`, `a`, `d`).

- [ ] **SN-26-bridge-coverage-h — apples-to-apples on beauty (2-way).**
  With -e/-f/-g landed, re-run **2-way SPITBOL+scrip** harness on
  `beauty.sno < beauty.sno`. Read last-agree + first-disagree
  pair only; hand off to SN-26c-parseerr-h sub-h2.

  **Pivot 2026-04-27:** csn participant excluded from this harness
  pending GOAL-CSN-FENCE-FIX closure (csn segfaults on the new
  beauty.sno via FENCE(P) builtin under nested recursion).  The
  3-way variant returns once that fix lands.

  `is.inc` / `FENCE.inc` / `io.inc` interaction RESOLVED in corpus
  `7041a14` — those three includes are no longer pulled in by
  beauty.sno on the self-host path (beauty reads stdin / writes
  stdout, so io.inc's INPUT/OUTPUT-arity shim never fires; FENCE
  is built into all target runtimes; is.inc is invalid per
  RULES.md).  This unblocks -h on the 2-way path; -j (scrip vs
  SPITBOL formatting divergence) still gates clean termination.
  Gate: Smoke=7, Broker=49, all bridge smokes, 2-way harness
  reaches ≥1000 steps or runs clean to MWK_END.

- [~] **SN-26-bridge-coverage-i — LIFTED to GOAL-CSN-FENCE-FIX.**
  CSNOBOL4 FENCE(P) builtin segfault on nested-recursion patterns.
  Sessions #37–#41 history (cstack-overwrite root-cause; partial fix
  via fnc_save_push/pop in lib/pat.c migrated cstack save to
  C-helper stack; new crash signature L_SCIN4 ZCL deref still
  reproduces) lives in `GOAL-CSN-FENCE-FIX.md` and the csnobol4
  git log.  This sub-rung is no longer a blocker for SCRIP work
  per the 2026-04-27 oracle pivot — see top-of-file note.

- [ ] **SN-26-bridge-coverage-j — scrip --ir-run formatting
  divergence vs SPITBOL on new beauty.**  After corpus `7041a14`,
  scrip --ir-run produces 523 lines of output vs SPITBOL's 646
  lines (md5s differ: scrip `195f9320d836948a0f21b63a4fc68b08`
  vs sbl `abfd19a7a834484a96e824851caee159`).  Diff shows scrip
  drops the LHS variable name and `=` separator on assignment
  statements after the first one, e.g.:
  ```
    sbl:                  &FULLSCAN      =  1
    scr:                                  1
  ```
  This is beauty's tab-stop / column-alignment pattern set
  (`ppStop[1..4]`, `ppSmBump`, `ppLgBump`) interacting with
  scrip's pattern matching such that the LHS column doesn't get
  emitted.  Almost certainly a scrip pattern-matching bug, not a
  beauty bug, since SPITBOL (the oracle) handles the same source
  correctly.  Without -i, the 3-way harness can't run; once -i is
  fixed, the harness on beauty.sno will surface this as a value
  divergence and pinpoint the exact statement/iteration where
  scrip first diverges.
  Gate: scrip --ir-run beauty.sno < beauty.sno output md5 matches
  SPITBOL x64 -bf output md5.  PLUS Smoke=7, Broker=49 preserved.

**Dependencies (post 2026-04-27 pivot):** -e → -f → -g → -j → -h.
-i is LIFTED to GOAL-CSN-FENCE-FIX and no longer gates -h.  -j
(scrip formatting divergence) still gates clean termination on
the 2-way harness.
**Sequencing:** active step is -g (scrip subscript-set fire-point)
in parallel with -j (scrip formatting divergence).  Both are pure
scrip work, no csnobol4 dependency.

---

## Active rung — SN-26c-parseerr (opened session #2)

**Done-when:** `scrip --ir-run beauty.sno < beauty.sno` exits 0
with byte-identical output to oracle (md5
`408fc788ca2ef425fc1f87e26d45a7a5`).

**Closed sub-rungs:** stmt153, stmt637, char-ir, parseerr-c..g,
parseerr-h sub-h1 (sessions #3–#12). See git log for commit hashes
and outcomes.

**Open sub-rung:** parseerr-h sub-h2 — chained `.`-captures
across nested pattern-call boundaries don't all commit by the
time `Reduce(snoStmt, 7)` runs. NM_CALL timeline (session #13):
oracle does 7×Shift then Reduce; scrip does 5×Shift, Reduce,
then 2×Shift — premature reduce drops c[1..2] in pp_snoStmt.

**Sub-h2 is gated behind SN-26-bridge-coverage-h.** No diagnostic
work on sub-h2 until the harness can give a clean ground-truth
divergence point. Per RULES.md "read the divergence point, not
the trace" — until -h, there is no trustable divergence point.

**Gate:** Smoke=7, Broker=49 after any fix.

---

## Key files

| File | Role |
|------|------|
| src/frontend/snobol4/snobol4.y | Bison grammar |
| src/frontend/snobol4/snobol4.l | Flex lexer |
| src/driver/interp.c | --ir-run tree-walk |
| src/runtime/x86/sm_lower.c | IR -> SM |
| src/runtime/x86/sm_interp.c | SM interpreter |
| src/runtime/x86/sm_codegen.c | x86 JIT |
| src/runtime/x86/bb_boxes.c | SNOBOL4 pattern boxes (incl. `bb_cap`) |
| src/runtime/x86/snobol4_nmd.c | Flat NAM stack: NAME_push/pop + NAME_top/pop_above |
| src/runtime/x86/stmt_exec.c | exec_stmt, bb_deferred_var |
| src/runtime/x86/name_t.h | NAME_t, NameKind_t, name_commit_value |
| src/runtime/x86/name_t.c | name_commit_value dispatch + name_init_as_* builders |
| corpus/programs/snobol4/demo/beauty/ | Beauty self-host suite (post-SN-26b) |

---

## Invariants

- SPITBOL is the primary oracle.  Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Latent follow-ups (small, not gating)

- SN-8a latent: named-args path in `SM_PAT_USERCALL` all-E_VAR stash never consumed.
- SN-22/23 cleanups: `NAME_push` return `void *` → `void`; `cache_get_fresh` template purity.
- SN-26 scout: `IR last_ok=?` on DIVERGE — uncaptured in `sync_monitor.c`.
- `build_spitbol_oracle.sh` SKIPs on prebuilt `bin/sbl` — add capability probe.
- ~40 `sm_lower: unresolved label 'ERROR'/'ERR'` warnings during beauty compile.
- Env-gated trace infrastructure permanent: `ONE4ALL_STEP_TRACE`, `ONE4ALL_USERCALL_TRACE` (BB_USERCALL, NM_CALL, PAT_USER_CALL_BUILD).
- **SN-26-csn-regen-fix** — `genc.sno` regen drops FNCP/FNCA..FNCD top-level definitions; `tsort` inlining promotes them to labels but `data_init.c` references them as functions. Hand-edit-the-C workaround used at every XCALLC landing site. Fix: diagnose `with`/`procs` inlining config, regenerate cleanly once, commit baseline.
- **SN-26-bridge-coverage-extras** — Catch-all completeness audit gaps (deferred). Sites likely missing: keyword assignment (`&keyword = X` via ASGNIC), function-arg binding at DEFINE-call entry, DATA/DEFINE/OPSYN/FIELD identifier creation/rename. Beauty's `global.inc` only does plain assigns and `.`-captures, so the 5 LOCAPT-TVALL sites suffice for sub-h2.
- **`<lval>` sentinel cleanup** — Currently `<lval>` is interned for array element / table slot stores. Cleaner: suppress the record entirely (parent's existence already recorded at `a = ARRAY(...)` time) by tightening `lvalue_name_id()` and `zysmv()` to return early without emitting when validation fails. Alternative: synthesize structured names like `a[1,2]`.
- **SN-26-spl-bridge-c** — **CLOSED 2026-04-27 session #32** by SN-26-bridge-coverage-b. Pattern-substitute store-back fire-point now fires via `o_rpl → oass0 → asign` fire-point landed at x64 @ `3cd2dcc`. Probe `S 'world' = 'there'` produces 3 records (b_vrs+asign+END). No separate work needed.
- **SN-26-binmon-nreturn-divergence** — Oracle-vs-oracle divergence on `dummy` (CSN: STRING, SPL: NAME) at step 162 of beauty self-host. Likely rooted in how each runtime represents the `.dummy` NRETURN value when the dot-star call happens. Low priority — exposes a real semantic gap but does not gate scrip work.
- **MWK_LABEL events** — If structural-flow events are desired in future, add `MWK_LABEL` to `monitor_wire.h` and fire on STNO advancing. Not gating sub-h2.
- **Legacy LOAD-based monitor cleanup** — `build_monitor_ipc_*_library.sh` (3 scripts) build the legacy LOAD() `.so` modules; now unreferenced by any harness but harmless. Could be deleted in a cleanup pass alongside their `monitor_ipc*.c` sources in `scripts/monitor/`. `runtime/x86/snobol4.c` `MONITOR_SO=builtin` sentinel is dead code now that no harness sets it.

---

## Current state

**HEADs:**
- one4all @ `78a2a98e`
- corpus @ `7041a14`
- x64 @ `3e519f9`
- csnobol4 @ `1d225f8` (managed by GOAL-CSN-FENCE-FIX from now on)
- active step → SN-26-bridge-coverage-g (scrip subscript-set fire-point)
  PARALLEL with SN-26-bridge-coverage-j (scrip formatting divergence
  on beauty).  -i lifted to GOAL-CSN-FENCE-FIX; not a SCRIP blocker.

**Gates:** Smoke=7, Broker=49. Bridge smokes (csn-bridge-a/b/c,
spl-bridge, spl-bridge-d, auto-binary, label-flow) all PASS as of
session #36.

**Pivot 2026-04-27 (session #42):** Oracle policy revised — SPITBOL
x64 is sole oracle for SCRIP development.  CSNOBOL4 excluded from
the sync-step monitor harness pending GOAL-CSN-FENCE-FIX closure
(beauty.sno triggers a builtin FENCE(P) segfault under nested
recursion, a runtime bug that is independent of any SCRIP work).
Sub-rung -i is lifted to that goal; -h pivoted from 3-way to 2-way.

**Beauty self-host status (session #36, post corpus `7041a14`):**
- SPITBOL x64 `-bf`: **CLEAN** — 646 lines, md5
  `abfd19a7a834484a96e824851caee159`
- CSNOBOL4 `-bf`: **SIGSEGV** at beauty.sno:616 statement 1074
  during `*snoParse` pattern match.  Bug in builtin `FENCE(P)`
  pattern primitive.  See `GOAL-CSN-FENCE-FIX.md`.
- scrip `--ir-run`: clean run, 523 lines, md5
  `195f9320d836948a0f21b63a4fc68b08` — but diverges from SPITBOL
  output (formatting bug).  See SN-26-bridge-coverage-j.

**Historical SN-30 invariant** md5 `408fc788ca2ef425fc1f87e26d45a7a5`
applies only to the OLD beauty.sno (pre-corpus-7041a14, with
`is.inc`/`FENCE.inc`/`io.inc` includes).  Useful as a regression
check against `git show 7041a14^:programs/snobol4/demo/beauty/beauty.sno`
but not against current beauty.sno.

---

## Closed-rung pointers

The git commit log is the permanent record. Search by rung id:

- `git log --oneline --grep "SN-26"` — SN-26 self-host sub-rungs
- `git log --oneline --grep "SN-26-bridge"` — 3-way binary harness work (sessions #15–#32)
- `git log --oneline --grep "SN-26c-parseerr"` — Parse Error sub-rung chain
- `git log --oneline --grep "SN-26-csn-bridge"` — csnobol4 bridge work
- `git log --oneline --grep "SN-26-spl-bridge"` — SPITBOL x64 bridge work

The commit message of each landed rung carries the diagnostic
technique used (Strategy-A AddressSanitizer, Strategy-B PDL-write-
site sweep, env-gated trace decomposition, etc.), the gates run,
and the rationale.
