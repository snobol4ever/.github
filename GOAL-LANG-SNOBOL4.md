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

- [x] **SN-26-bridge-coverage-g — symmetric lvalue coverage.**
  Closed session #43. `comm_var()` fire-point landed at both
  subscript-set call sites in `interp.c`: `execute_program`
  (stmt-level `A<i>=val`) and `call_user_function` (function-body
  path). Base name extracted from `idx_e->children[0]->sval` when
  base is `E_VAR`; no fire for complex expressions. New smoke test
  `test_smoke_sn26_scr_subscript_bridge.sh` PASS=1 — verifies
  `a<1>='x' / a<2>='y' / d<'k'>='z'` → 3 STRING VALUE records,
  names `[a, a, d]`. Note: SPITBOL still emits `<lval>` for
  subscript stores (pre-existing behavior, latent follow-up);
  controller will flag sbl vs scrip subscript records as "diverge"
  until SPITBOL's bridge is updated. one4all @ `311993c6`.
  Gate: Smoke=7, Broker=49.

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

- [x] **SN-26-bridge-coverage-k — LABEL stno numbering disagreement
  on beauty.** **CLOSED session #44.** Two distinct bugs were both
  fixed in scrip:

  **Bug 1 — blank lines not parsed as statements.** `snobol4.l:113`
  consumed blank lines without emitting `T_STMT_END`, so the parser
  never created an empty STMT_t for them. SPITBOL/CSNOBOL4 (and the
  Green Book / Griswold spec) treat blank lines as empty statements
  that advance &STNO. Fix: blank-line lex rule now returns
  T_STMT_END.  `unlabeled_stmt: opt_subject opt_repl opt_goto
  T_STMT_END` already accepts the all-empty case, so no grammar
  change.

  **Bug 2 — `&STNO` was aliased to `kw_stcount`.**
  `runtime/x86/snobol4.c:2825` returned `INTVAL(kw_stcount)` for
  `&STNO` — so `&STNO` and `&STCOUNT` were the same variable.
  Fix: added `kw_stno` global; `execute_program` updates it on
  every iteration; the keyword read returns `INTVAL(kw_stno)`.
  `&STCOUNT` (executed-stmts counter) is unchanged — the empty-stmt
  path skips `comm_stno()` so `kw_stcount` doesn't bump for blanks.

  **Verification:**
  - probe `a='A' / blank / b='B' / OUTPUT &STNO &STCOUNT`:
    SPITBOL stno=4 stcount=3, scrip stno=4 stcount=3 ✓
  - 3 blanks: SPITBOL stno=6 stcount=3, scrip stno=6 stcount=3 ✓
  - no blanks: scrip stcount=3 ✓ (no regression)
  - 2-way harness on `beauty.sno < "  a = 1"` advances cleanly
    from step 26 (was DIVERGE on LABEL stno) to step 49 (next real
    divergence — sub-rung -l).
  - All LABEL stnos in trail (23, 24, 25, 27, 29) match SPITBOL
    exactly; both runtimes skip 22, 26, 28 (blank stmts).

  **Files touched:**
  - `src/frontend/snobol4/snobol4.l` (blank-line returns T_STMT_END)
  - `src/frontend/snobol4/snobol4.lex.c` (regenerated)
  - `src/runtime/x86/snobol4.h` (kw_stno extern)
  - `src/runtime/x86/snobol4.c` (kw_stno definition, &STNO read fix)
  - `src/driver/interp.c` (empty-stmt detection in execute_program;
    kw_stno update on real-stmt path)

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-l — SPITBOL lvalue name fix at
  asign/asinp fire-points.** Session #45 (2026-04-27).

  **Root cause confirmed:** `spl_vrblk_name()` was called for all
  paths through `asg01`/`asinp` — including aggregate-element stores
  where `xl` is mid-arblk/teblk/vcblk/pdblk, not a real vrblk.  The
  bytes at `xl - vrvlo` happened to spell `"ss"` (or similar junk)
  for `UTF[k]='NO_BREAK_SPACE'`, passing the ASCII filter and getting
  emitted as the variable name.

  **Fix:** Split fire-points at the SIL level.  At `asg01` and `asinp`
  untrapped paths, check `(xl - *vrvlo)` against `=b_vrs`.  For real
  vrblks, `vrsto` holds `b_vrs` → natural-var path → call `sysmw`
  (`zysmw`) which emits `<lval>` unconditionally without name
  synthesis.  For natural-var path, continue to call `sysmv` with the
  real vrblk.  Added `sysmw  exp  0` declaration in `sbl.min`,
  `sysmw`/`zysmw` syscall id 43 in `int.asm`, `zysmw()` in
  `osint/monitor_ipc_runtime.c`.

  **Verification:** 2-way harness on `beauty.sno < "  a = 1"` now
  advances past the former step-49 `UTF[k]` divergence to step 306.
  Steps 1–305 all agree. New divergence at step 306 is a LABEL stno
  disagreement (spl=160, scr=162) — a separate loop-counting issue,
  not a -l artifact.  SN-30 invariant md5
  `abfd19a7a834484a96e824851caee159` preserved on beauty.sno
  self-host.

  **Also fixed:** Pre-existing `test_smoke_sn26_label_flow.sh`
  FAIL=2 from -k: sm-run/jit-run expected 4 LABELs but got 5 after
  blank-line fix. Updated to expect 5 (1 blank + 3 stmts + END).
  Fixed `UnboundLocalError` in `monitor_sync_bin.py` (redundant
  local `from collections import deque` shadowed top-level import).

  **Gates:** Smoke=7, Broker=49, all bridge smokes PASS (csn skipped
  — csnobol4 not built this session).  x64 @ new HEAD.
  `MONITOR_SOFT_LABEL=1` on `beauty.sno < "  a = 1"` reaches step 49,
  the first store into `UTF[CHAR(194) CHAR(160)] = 'NO_BREAK_SPACE'`.
  Values agree (`STRING(14)='NO_BREAK_SPACE'`); names diverge:
  SPITBOL `VALUE ss = ...`, scrip `VALUE UTF = ...` (correct, our -g
  enrichment).

  **Root cause:** `osint/monitor_ipc_runtime.c:spl_vrblk_name()` runs
  the printable-ASCII filter on a "fake vrblk" synthesized by the
  asign/asinp fire-points from `xl - vrsto_offset` when xl is mid-arblk
  / mid-tbblk during a subscript store. The bytes at the fake vrblk's
  vrlen/vrchs slots happen to be `len=2, "ss"` for `UTF[k]=...` —
  passes validation, gets emitted as the variable name. The filter
  cannot distinguish a real 2-char variable from junk based on bytes
  alone — the call site is the only place that knows the path was
  a subscript store.

  **Fix path (architectural, asign/asinp side):** at the SIL level in
  `sbl.min`, the asign/asinp fire-points already know whether they
  reached `asg01` via the natural-variable path (xr = real vrblk) or
  via an aggregate-element path (xl = mid-arblk/mid-tbblk, fake vrblk
  synthesized). Pass an explicit flag to a new entry point (e.g.
  `zysmv_lval` for "this is a subscript store, name is `<lval>`")
  separate from `zysmv` (natural store, real name). The current
  conflated entry point is the bug — the C-side validator is doing
  guesswork the SIL caller has the answer to.

  Alternative (suppress entirely): the parent's existence is already
  recorded at `a = ARRAY(...)` time. A subscript store's individual
  emission is decorative; suppressing it on the SPITBOL side would
  match the cleaner-than-`<lval>` design suggested in the latent
  follow-up note. Trade-off: scrip currently DOES emit the collection
  name on subscript stores (-g), so suppression on SPITBOL would
  introduce an asymmetry the controller would need to absorb (extend
  `<lval>` wildcard to "any name when other side suppressed"). Pick
  the explicit-flag path for symmetry with -g.

  **Gate:** 2-way harness with current `MONITOR_SOFT_LABEL=1` reaches
  step >49 cleanly past `UTF[k]='NO_BREAK_SPACE'`; SPITBOL bridge
  emits `<lval>` (or the collection name `UTF` if the fix takes the
  collection-name route) on every aggregate-element store, never
  junk like `ss`. Smoke=7, Broker=49 preserved. SN-30 invariant md5
  `408fc788ca2ef425fc1f87e26d45a7a5` preserved on x64 self-host of
  the OLD beauty.

  **Sequencing note:** -l is independent of -k. -l unblocks deeper
  semantic comparison on aggregate-store paths.

- [x] **SN-26-bridge-coverage-j — scrip --ir-run linear-stno bug
  in execute_program.  CLOSED session #46 (2026-04-27).**

  **Real root cause (revised):** the prior hypothesis about beauty's
  parser / `Reduce(snoStmt, 7)` dropping `c[4]`/`c[5]` was a downstream
  symptom, not the cause.  The actual bug was in `execute_program()`:
  `interp.c:4199` initialised `int stno = 0;` and used `++stno` on
  every iteration of the main loop.  This made `&STNO` and the
  MWK_LABEL stno payload a **linear execution counter**, not the
  source statement number.  For purely forward execution `stno`
  happened to equal the source `&STNO`, hiding the bug — but on the
  first backward goto (`:S(label)`), scrip's `stno` kept incrementing
  while SPITBOL's `&STNO` correctly snapped back to the source line
  number.

  **Manifestation (the visible bug — session #43 trace):**
  In beauty's `global.inc:158-163`:
  ```snobol4
      UTF_Array = SORT(UTF)
      i = 0
  G1  i = i + 1
      $UTF_Array[i, 2] = UTF_Array[i, 1]  :S(G1)
      UTF_Array =
      i =
  ```
  At the FIRST iteration of this loop, scrip's `stno` matched
  SPITBOL's because everything had been linear so far.  After the
  first `:S(G1)` backward goto, scrip emitted LABEL stno=162 (its
  next linear counter) while SPITBOL emitted LABEL stno=160 (the
  real `&STNO` of `G1`).  The harness reported divergence at
  step 306 — the very first goto-backward event in the program.

  The values were correct (loop iterated, NO_BREAK_SPACE etc. all
  got assigned), so end-to-end output was nearly right and the bug
  hid behind the noisier formatting divergence.  The 523-vs-646
  line output difference is also resolved by this fix
  (post-fix: scrip beauty self-host emits 646 lines matching
  SPITBOL's structure on the assignment-statement formatting; one
  step-882 divergence remains — see -m).

  **Fix:**
  - `frontend/snobol4/scrip_cc.h`: added `int stno;` field to
    `STMT_t` (1-based, sequential, includes blank statements).
  - `frontend/snobol4/snobol4.y` `sno4_stmt_commit_go()`:
    `s->stno = ++pp->prog->nstmts;` at the head of every commit
    (replaces the trailing `nstmts++` so the assignment is
    pre-incremented and matches SPITBOL's 1-based numbering).
  - `driver/interp.c` `execute_program()`: replaced both
    `++stno` sites with `stno = s->stno;` — once for the
    empty-statement path (preserves `&STCOUNT` not bumping for
    blank lines from -k), once for the executed-statement path.
    `kw_stno = stno;` and `mon_emit_label_bin(stno)` now report
    the source stno on every entry, including after a backward
    goto.
  - `frontend/snobol4/snobol4.tab.c`, `snobol4.tab.h`,
    `snobol4.lex.c` regenerated by
    `scripts/regenerate_parser_and_lexer_from_sources.sh`.

  **Note — sm_interp.c / sm_codegen.c carry the same bug pattern**
  (`g_sm_stno` counter in `SM_STNO` opcode).  The 2-way harness uses
  `--ir-run`, so the SM/JIT paths don't gate the immediate harness
  goal.  Tracked as latent follow-up: extend `SM_STNO` to take an
  operand (the source stno, lowered from `s->stno`) so SM-run and
  JIT-run get the same fix.

  **Verification:**
  - 2-way harness on `beauty.sno < beauty.sno` advances from
    step 306 → step 882.  All UTF_Array loop iterations
    (steps 302..798 roughly) flow with matching LABEL stno=160 ↔
    LABEL stno=161 cycles between SPITBOL and scrip.
  - 2-way harness on the smaller probe2.sno (`&FULLSCAN=1` +
    `global.inc` + tail) advances from step 306 → step 806.
  - Smoke=7, Broker=49.
  - The historical SN-30 invariant md5 still applies on the OLD
    beauty (pre-corpus-7041a14); current beauty md5s are different
    and tracked separately in the closing notes for SN-29.

- [ ] **SN-26-bridge-coverage-m — record-ordering / control-flow
  divergence at goto-to-bare-label statement.**  After -j closure,
  the 2-way harness on `beauty.sno < beauty.sno` reaches step 882
  cleanly, then diverges:
  ```
    spl #882: LABEL stno=INT=463
    scr #882: LABEL stno=INT=461
  ```
  Last-agreed trail steps 877-881 show alternating LABEL events
  at stnos 440, 441, 442, 443 (matching) followed by `VALUE indent
  = STRING(120)='<120 spaces>'` (matching).  After that, SPITBOL
  jumps to stno=463 while scrip jumps to stno=461 — divergent
  control flow rather than divergent record ordering.

  On the smaller probe2.sno repro the analogous pattern was
  observed at step 806: SPITBOL fired LABEL stno=165 (a bare
  label statement `end_pgm`) while scrip emitted VALUE OUTPUT
  before the next LABEL.

  Likely culprits to investigate:
  (1) does scrip emit MWK_LABEL for bare label-only statements
  reached via goto?  (2) is the goto-to-label landing on the
  wrong STMT_t — e.g. landing on the previous statement's
  trailing position?  (3) does empty-statement skip-logic in
  `execute_program` (the `!s->label && !s->subject && ...` guard
  at interp.c:4214) need updating to fire LABEL before skipping?

  **Gate:** 2-way harness on `beauty.sno < beauty.sno` advances
  past step 882 to clean MWK_END or to a divergence rooted in a
  different subsystem.  PLUS Smoke=7, Broker=49 preserved.

**Dependencies (post 2026-04-27 pivot, post -j closure session #46):**
-e → -f → -g → (-k, -l) → -j → -m → -h.
-i is LIFTED to GOAL-CSN-FENCE-FIX and no longer gates -h.
-j CLOSED (linear-stno bug).
-m is the new active rung for the harness flow on beauty.

**Latent follow-up — SM/JIT linear-stno parity.**  The fix in -j
landed in the IR-run path only.  `sm_interp.c SM_STNO` and
`sm_codegen.c h_stno` still use a `g_sm_stno` linear counter.
Extend `SM_STNO` to take an operand (the source stno) so SM-run
and JIT-run report the same `&STNO` semantics.  Not gating the
2-way harness (`--ir-run` only).  Tracked as latent until a Goal
explicitly needs SM/JIT &STNO correctness on backward gotos.

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
- one4all @ new HEAD (post session #46)
- corpus @ `7041a14`
- x64 @ new HEAD (post session #45)
- csnobol4 @ `1d225f8` (managed by GOAL-CSN-FENCE-FIX from now on)
- active step → SN-26-bridge-coverage-m (record-ordering /
  control-flow divergence at goto-to-bare-label statement).
  -j CLOSED session #46: linear-stno bug in `execute_program` —
  `int stno = 0; ++stno` was a linear execution counter, made
  `&STNO` and MWK_LABEL stno wrong on backward gotos.  Added
  `STMT_t.stno` (source stno, set at parse time, 1-based);
  `execute_program` now reads `stno = s->stno;` instead of
  `++stno;`.  2-way harness on beauty.sno self-host advances
  306 → 882; on probe2.sno 306 → 806.
  -l CLOSED session #45; -k CLOSED session #44; -g CLOSED session #43;
  -i lifted to GOAL-CSN-FENCE-FIX; -h unblocked once -m lands.

**Session #46 (2026-04-27) — SN-26-bridge-coverage-j root cause:**
The prior hypothesis (beauty parser `Reduce(snoStmt, 7)` dropping
c[4]/c[5]) was a downstream symptom.  Real cause was `int stno = 0;
++stno;` in `execute_program` — a linear counter that pretended to
be `&STNO` and matched SPITBOL only as long as execution was
purely forward.  The first backward goto in beauty (the
`UTF_Array` / `:S(G1)` loop at `global.inc:158-163`) exposed the
divergence at step 306.  Fix: `STMT_t.stno` field set during parse;
`execute_program` reads `s->stno` instead of incrementing a counter.
Empty-statement path also updated to use `s->stno` (preserves
session #44 -k semantics: blank lines bump &STNO not &STCOUNT).
Same bug pattern still present in `sm_interp.c SM_STNO` /
`sm_codegen.c h_stno` (`g_sm_stno` counter); deferred as latent
follow-up since the harness uses --ir-run only.

**Files touched (session #46):**
- `src/frontend/snobol4/scrip_cc.h` (added `STMT_t.stno` field)
- `src/frontend/snobol4/snobol4.y`
  (`s->stno = ++pp->prog->nstmts;` at commit head; removed
   trailing `nstmts++`)
- `src/frontend/snobol4/snobol4.tab.c`, `snobol4.tab.h`,
  `snobol4.lex.c` (regenerated)
- `src/driver/interp.c` (`execute_program`: replaced both
  `++stno` sites with `stno = s->stno;`)

**Gates:** Smoke=7, Broker=49.

**Earlier session #44 — sync-step harness probe of beauty:**
2-way harness on `beauty.sno < "  a = 1"` initially agreed through
step 25 (VALUE bSlash; 12 ALPHABET captures clean), then diverged
at step 26 on a LABEL-only event: spl=15, scr=14. Reading the
divergence point per RULES.md (not the trace) revealed two real
scrip bugs:

1. **Blank lines not parsed as statements.** `snobol4.l:113`
   consumed blank `\n` without emitting `T_STMT_END`. SPITBOL,
   CSNOBOL4, and the Green Book all treat blank lines as empty
   statements that advance &STNO. Fix landed in -k.

2. **`&STNO` aliased to `kw_stcount`.** `snobol4.c:2825` returned
   `INTVAL(kw_stcount)` for `&STNO`, making them literally the
   same variable. Added `kw_stno` global, fixed read site, made
   `execute_program` update `kw_stno` on every iteration (real
   and empty stmts). `&STCOUNT` semantics unchanged — empty stmts
   don't bump it. Fix landed in -k.

After -k closure: harness flows naturally from step 1 to step 48
with NO diagnostic overrides. Step 49 is the next divergence,
which is the genuine SPITBOL `<lval>`/`ss` lvalue-name issue
(sub-rung -l).

Diagnostic features added to `monitor_sync_bin.py` during
investigation: `MONITOR_LAST_AGREE_TRAIL=N` (kept — useful
long-term per RULES.md "read the divergence point"),
`MONITOR_SOFT_LABEL=1` and `MONITOR_SOFT_LVAL_NAME=1` (both
reverted before commit per RULES.md "diagnostic patches don't
ship"). Lesson learned: the soft overrides masked the real
bugs and pushed the divergence 1009 steps downstream — reading
the FIRST divergence (step 26) without overrides was the
correct play and immediately surfaced two real bugs.

**Gates:** Smoke=7, Broker=49. Bridge smokes (csn-bridge-a/b/c,
spl-bridge, spl-bridge-d, auto-binary, label-flow,
scr-subscript-bridge) all PASS as of session #43.

**Pivot 2026-04-27 (session #42):** Oracle policy revised — SPITBOL
x64 is sole oracle for SCRIP development.  CSNOBOL4 excluded from
the sync-step monitor harness pending GOAL-CSN-FENCE-FIX closure
(beauty.sno triggers a builtin FENCE(P) segfault under nested
recursion, a runtime bug that is independent of any SCRIP work).
Sub-rung -i is lifted to that goal; -h pivoted from 3-way to 2-way.

**-j diagnostic state (session #43):**
2-way monitor (SPITBOL + scrip) on `beauty.sno < "  a = 1"` agrees
on all initialization VALUE events. First semantic divergence: SPITBOL
emits `<lval>` for `UTF[k]='NO_BREAK_SPACE'` subscript store while
scrip emits `UTF` (correct — our -g fire-point). That is a
wire-protocol difference (SPITBOL still uses `<lval>`), not a real
semantic divergence.

The actual OUTPUT divergence (scrip drops LHS name `a` and `=` from
assignment statements): confirmed by direct SPITBOL vs scrip diff.
In-process `--monitor` (IR vs SM vs JIT) diverges at stmt 629:
`snoLine = INPUT` — IR reads correctly, SM/JIT get empty string.
That is a separate SM/JIT bug unrelated to the -j formatting issue.

Wire trace of actual Reduce('snoStmt', 7) during `a=1` parse: c[4]
(should be `=` tree) and c[5] (should be `snoInt 1` tree) arrive as
NULL from Pop(). c[1..3,6,7] are correct tree objects. This means the
`=` and `snoInt` Shift calls during the FENCE first alternative do not
push to `$'@S'` in the full beauty context — despite isolated unit
tests of FENCE+Shift working correctly in scrip.

**Next diagnostic step:** Inject `xTrace=5` via a thin wrapper (not
modifying corpus) to trace every Shift/Reduce/Push/Pop call during the
actual parse. The wrapper should `-INCLUDE` all of beauty's `.inc`
files, override `xTrace=5`, then define the main loop. The trace
output from SPITBOL vs scrip on `a=1` input will show exactly which
Shift calls fire (and which don't) in each runtime, pinpointing the
stack divergence to a specific FENCE alternative or `*snoExpr` level.
An alternative: intercept at the `E_DEFER` node in `bb_boxes.c` or
`interp_eval()` — `snoParse` is stored as `E_DEFER(snoParse)` in the
IR; if the deferred re-evaluation doesn't see the same `snoParse`
pattern value that was built during init, the whole parse would be
wrong in a different way.

**Beauty self-host status (session #43, post corpus `7041a14`):**
- SPITBOL x64 `-bf`: **CLEAN** — 646 lines, md5
  `abfd19a7a834484a96e824851caee159`
- scrip `--ir-run`: clean run, 523 lines, md5
  `195f9320d836948a0f21b63a4fc68b08` — drops LHS var+`=` on
  assignment statements. See SN-26-bridge-coverage-j.

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
