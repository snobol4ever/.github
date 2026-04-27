# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

**Forensic history:** closed rungs are summarized below; full session
narratives live in `archive/ARCHIVE-LANG-SNOBOL4-HISTORY.md` and in git.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

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

## scrip-monitor Protocol

Step 1 (--monitor) runs EVERY iteration, unconditionally.
Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 -- ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 -- only if Step 1 shows problem: OUTPUT probe -> fix -> rebuild -> repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

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

- [ ] **SN-26-bridge-coverage-h — apples-to-apples on beauty.**
  With -e/-f/-g landed, re-run 3-way harness on
  `beauty.sno < beauty.sno`. Read last-agree + first-disagree
  pair only; hand off to SN-26c-parseerr-h sub-h2.
  `is.inc` / `FENCE.inc` / `io.inc` interaction RESOLVED in corpus
  `7041a14` — those three includes are no longer pulled in by
  beauty.sno on the self-host path (beauty reads stdin / writes
  stdout, so io.inc's INPUT/OUTPUT-arity shim never fires; FENCE
  is built into all 3 target runtimes; is.inc is invalid per
  RULES.md and was only kept to feed FENCE.inc and io.inc).  This
  unblocks -h but exposes two real runtime bugs the includes were
  hiding — see -i (csn FENCE(P) builtin segfault) and -j (scrip
  vs SPITBOL formatting divergence).  -h proper cannot run cleanly
  on csn until -i lands, and cannot terminate cleanly on scrip
  until -j lands.
  Gate: Smoke=7, Broker=49, all bridge smokes, harness reaches
  ≥1000 steps or runs clean to MWK_END.

- [ ] **SN-26-bridge-coverage-i — CSNOBOL4 FENCE(P) builtin
  segfault on heavy beauty pattern load.**  After corpus `7041a14`
  removed the user-defined `FENCE.inc` stub from beauty.sno, the
  builtin `FENCE(P)` 1-arg pattern primitive in csnobol4 segfaults
  during beauty self-host: `Caught signal 11 in statement 1074 at
  level 0` at beauty.sno:616 (`snoSrc POS(0) *snoParse *snoSpace
  RPOS(0)`).  Bisect confirms the crash is present at every
  csnobol4 commit from `7654cda` (the FENCE(P) implementation
  landing) onward, including `5990456` ("FENCE(P): fix S-9 bugs —
  10/10 tests pass").  Pre-FENCE(P) commit `a509cd7` produces
  Error 5 (Undefined function) on beauty.sno:51 because FENCE(P)
  was not yet implemented — i.e. csnobol4 has never run the new
  beauty.sno cleanly.  The user-defined FENCE stub from FENCE.inc
  was masking the bug because the stub never invokes the broken
  pattern opcode.  SPITBOL x64 runs the new beauty.sno cleanly
  (646 lines).

  **Session #37 progress (NOT closed — bug still reproduces):**
  - **Tiny repro found.** Single SNOBOL4 statement as input
    (`                  ppStop         =  ARRAY('1:4')` + `END`)
    fed to `beauty.sno` reproduces the segfault reliably. No need
    for the full 646-line beauty self-host to trigger it.
  - **Diagnostic infrastructure added.** `lib/init.c` now has an
    env-gated `CSN_NO_SEGV_HANDLER` bypass — when set, the SEGV
    handler is not installed, so gdb gets a clean backtrace
    instead of csnobol4's friendly "Caught signal 11" error
    message.  Use as: `CSN_NO_SEGV_HANDLER=1 gdb --args
    /home/claude/csnobol4/snobol4 -bf -P64k -S64k beauty.sno
    < /tmp/tiny.in`.  Always-off in normal runs (no perf cost).
  - **Crash location pinned:** `isnobol4.c:11468` in `L_SALT1`:
    `D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR);`  At crash,
    `res.pdlptr->a.i = 192` (= 12×DESCR), `res.pdlhed->a.i = 96`
    (= 6×DESCR) — both descriptors hold tiny integer offsets,
    not real PDL addresses.  PDLEND remains valid.  Trace shows
    PDLPTR was valid at the previous L_SALT1 hit; between hits
    something replaces both PDLPTR and PDLHED with offset-like
    values.
  - **One latent bug found and fixed (necessary, not sufficient):**
    `FNCC` PCOMP mistranslation in `isnobol4.c` and `snobol4.c`.
    The hand-edit at SN-30/S-9 fix #3 emitted `if equal goto SCOK`
    (skip seal) but the SIL `PCOMP PDLPTR,PDLHED,FNCC1,FNCC1,INTR13`
    means **less → INTR13, equal → FNCC1, greater → FNCC1** per
    `genc.sno` `DOCMP3` macro arg order `(X,Y,G,E,L)`.  Verified
    by running `./snobol4 -b genc.sno --with BLOCKS v311.sil >
    /tmp/snobol4.c2` — the regenerated FNCC has `else goto
    L_FNCC1` (no equal-to-SCOK shortcut).  Fix applied to both
    `isnobol4.c` and `snobol4.c`.  All 10 tests in
    `test/fence_function/` still PASS.  Beauty still segfaults,
    so there is a **second** bug.
  - **Bootstrap path confirmed.** `csnobol4` itself bootstraps
    its own regen: `./snobol4 -b genc.sno --with BLOCKS v311.sil
    > snobol4.c2`.  SPITBOL cannot directly run genc.sno because
    line 850 uses CSNOBOL4's `LABEL()` extension (SPITBOL has no
    `LABEL` builtin → Error 22).  The regen still does NOT emit
    FNCP/FNCA..FNCD as top-level functions (latent
    `SN-26-csn-regen-fix`); they remain inline `L_FNCP:` etc., so
    direct C surgery is still required to keep `data_init.h`
    function-pointer references resolving.
  - **Hardware watchpoint paradox RESOLVED — environmental, not
    a bug.** Session #38 verified gdb HW watchpoints don't fire
    at all in this container (trivial `long g; g=42; g=100;
    watch g` test: zero stops).  Container's ptrace doesn't
    expose debug registers.  See RULES.md "Debugging — gdb
    hardware watchpoints DO NOT work in this container" for
    full alternatives table.  Use C-level `_check()` +
    `__builtin_trap()` instead.  Software watchpoints
    (`set can-use-hw-watchpoints 0`) technically work but are
    too slow for this codebase.

  **Session #38 progress (NOT closed — root cause located,
  fix not yet implemented):**
  - **Trigger bisected to a 1-line minimum.**  Input `X` (no
    leading space) → clean.  Input ` X` (one leading space, so
    parsed as a body-statement not a label) → segfault.  Any
    real statement that exercises beauty's `*snoExpr` recursion
    chain triggers the bug.  Confirms the bug requires deep
    `*P` recursion through nested FENCE patterns, which beauty's
    grammar uses extensively (`snoExpr0..15`, `snoXList`, etc.,
    every level wraps in `FENCE(...)`).
  - **State at fault, with -g symbols:** `PDLPTR.a.i = 0xc0`
    (= 192 = 12·DESCR), `PDLHED.a.i = 0x60` (= 96 = 6·DESCR),
    `PDLEND.a.ptr = 0x7ed3...` (valid heap), `MAXLEN = 1`,
    `LENFCL = 0x31` (49).  cstack lives in heap at
    `0x7ed3065dd010..0x7ed3066dd010`, far from `&res.pdlptr` —
    so a cstack overrun cannot directly clobber `res.pdlptr`.
    All POP(PDLPTR) sites compile to plain 8-byte `mov`s, no
    SSE; the value 192 IS arriving via plain stores.
  - **Diagnostic technique:** five generations of C-level
    instrumentation (helper + `__builtin_trap()` after every
    PDLPTR-mutating site).  v6 added a 128-event circular log
    of every PUSH(PDLPTR) and POP(PDLPTR) with cstack slot
    address and the value at that slot.
  - **ROOT CAUSE LOCATED — stale cstack slot read after
    intermediate RSTSTK:**  Final v6 trace shows the failing
    `POP(PDLPTR)` at `isnobol4.c:12362` reads slot `0x...360`
    holding `0xc0`.  No PUSH(PDLPTR) in the recent 128 events
    wrote to that slot — the matching PUSH happened far
    earlier and scrolled out of the window.  Between the
    matching PUSH and the failing POP, the trace shows
    `cstack` jumped DOWN by ~41 slots in one step (a `RSTSTK`
    rewinding past many frames at once), then a normal
    P/O sequence resumed at fresh, unrelated slots.  The
    saved-PDLPTR slot `0x...360` was left exposed in
    not-currently-tracked memory; subsequent unrelated PUSHes
    of small-integer values (the `0xc0` is the integer 192,
    matching SIL idioms like `SIZE = 6*DESCR`, `12*DESCR`,
    indices, or PDL-offset arithmetic) overwrote it.
  - **The architectural tension:**  L_FNCA at `isnobol4.c:12325`
    sits **4 lines after** a `SAVSTK()` at line 12321 inside
    the STARP/RCALL block setting up `switch (SCIN1(NORET))`.
    L_FNCA is reached as fall-through from that switch when
    inner SCIN1's return code didn't match cases 1/2/3.  The
    inner SCIN1's `RSTSTK()` rewound cstack DIRECTLY to the
    SAVSTK-recorded value (not pop-by-pop) — so any recursion
    farther down that did its own SAVSTK/PUSH(PDLPTR) chain
    has a window where the saved-PDLPTR slot lives at an
    address ABOVE the current cstack and is no longer
    "protected": a later PUSH from a different recursion arm
    can land at that exact slot and overwrite it.

    SIL's FENCE design assumes FNCA's 6 cstack pushes are
    durable until matching FNCB/FNCC pops them.  In the C
    generation, FNCA, intermediate `RCALL ,SCIN1,...` (which
    emits `SAVSTK(); switch(SCIN1(NORET))`), and FNCB are all
    in the same C function (SCIN1) — so on the surface the
    cstack pushes "should" survive.  But under sufficient
    recursion depth, the combination of RSTSTK rewinds and
    re-pushes at fresh frames produces stale-slot reads.

  **Session #39 progress (analysis-only, no code changes):**
  - **SPITBOL comparison performed.**  Read sbl.min lines
    11978-12039 (`p_fna..p_fnd`) and the doc block at
    11473-11500.  SPITBOL's FENCE save list is **dramatically
    smaller**: `p_fna` saves only `pmhbs` (history-stack base)
    and the `=ndfnb` indirect pointer onto **`xs`** (the
    pattern matching stack — analog of CSNOBOL4's PDL).  No
    save of MAXLEN, no separate save of LENFCL beyond what's
    in the trap entry, no save of name-list state.
    CSNOBOL4 saves 6 things on cstack; SPITBOL saves the
    semantic-equivalent of 1-2 things on `xs`.
  - **Bug mechanism re-confirmed.**  PUSH/POP compile to
    `cstack` ops (heap-allocated descriptor stack, not the C
    call stack).  `RETURN(VALUE)` macro = `RSTSTK(); return`.
    `BRANCH(NAME)` = tail call, NO RSTSTK.  A long BRANCH
    chain inside SCIN1 (which contains L_FNCA, L_FNCB, L_FNCC
    as labels) defers all SAVSTK records until the final
    RETURN — at which point cstack rewinds bulk-style past
    FNCA's saves.  The "41-slot RSTSTK" session #38 observed
    is exactly that.  The corrupted slots (e.g., 0xc0 = 12·DESCR)
    are integer constants pushed by unrelated later code that
    landed in the now-exposed slots.
  - **ATP2 / EXPV7 / ENMI4 are NOT vulnerable.**  ATP2 wraps
    its 6-PUSH around an `RCALL ,TRPHND,...` which is a
    regular C call — TRPHND's RSTSTK rewinds only to AFTER
    ATP2's PUSHes.  EXPV7 is in EXPVAL (its own C function)
    with balanced SAVSTK at entry / RSTSTK at exit.  ENMI4
    same pattern as EXPV7.  Only FNCA is structurally
    different because FNCA/FNCB/FNCC live as labels INSIDE
    SCIN1 separated by tail-call BRANCH chains.
  - **Two fix axes identified; merit re-ranking:**
    - **Axis A (audit-then-minimize):** which of the 6 saved
      values does FNCA actually NEED to preserve across inner-P
      matching?  Hypothesis (from SPITBOL comparison): MAXLEN
      doesn't change during inner-P (SCNR reloads it from XSP);
      LENFCL is already in trap entry slot 3 (redundant on
      cstack); NAMICL and NHEDCL may have other invariants.
      If audit shrinks the save list to 1-2 values, the fix
      becomes much smaller.
    - **Axis B (relocation):** wherever the audit says state
      genuinely needs to survive, move it to PDL (extending
      FNCA's trap entry from 3 to N descriptors) rather than
      cstack.  Same mechanic as fix candidate 1 below, but
      applied to a smaller set after Axis A reduces the count.
  - **Decision deferred.**  Did not write any code.  Concluded
    that "good solid fix" requires the Axis A audit before
    committing to a structural change — otherwise we widen
    the trap entry for values that didn't need saving in the
    first place.

  **Fix candidates (ordered by likelihood, all pending):**
  1. **Audit + minimize (Axis A):** Read FNCA-FNCC and
     adjacent SIL to determine the actual minimum save set.
     Cross-reference with SPITBOL's 1-save model.  Drop any
     redundant cstack PUSH.  Likely outcome: save list
     shrinks from 6 to 1-3 items.
  2. **Save FENCE state on the PDL** (alongside FNCBCL)
     instead of cstack, for the items audit determines genuinely
     need cross-RCALL persistence.  SIL-level fix in
     `v311.sil` FNCA/FNCB/FNCC/FNCD.  Specifically: extend
     FNCA's trap entry from 3 descriptors to (3 + N)
     descriptors where N is the audit-confirmed save count.
     FNCB/FNCC read from the extended slots via positive
     offsets (with a +3*DESCR adjustment because SALT2's
     `DECRA PDLPTR,3*DESCR` runs before the dispatch).  SALT
     itself unchanged; trap-entry size customization is per-site
     and FNCB/FNCC handle their own layout.
  3. Have `genc.sno`'s RCALL macro emit additional protection
     so FNCA's cstack pushes are not exposed by RSTSTK
     rewinds (e.g., re-anchor or relocate).  More invasive;
     touches the macro layer, affects all sites.

  **Next session entry point:** start with the Axis A audit.
  Specifically:
  1. Trace `MAXLEN` through inner-P matching.  Does any
     pattern primitive write to MAXLEN between FNCA and
     FNCB/FNCC?  If no — drop the MAXLEN save entirely.
     SCNR/SCNR1 (lines 3535-3547) reloads MAXLEN from XSP
     on each scanner entry, suggesting it's recomputed and
     not preserved across pattern recursion — confirm by
     grep `MAXLEN` writes vs reads in v311.sil.
  2. Confirm LENFCL: trap entry slot 3 already saves it; the
     cstack PUSH(LENFCL) is **provably redundant** with what
     the SALT walker restores via `GETDC LENFCL,PDLPTR,3*DESCR`
     at line 3613.  Drop without further analysis.
  3. Trace `NAMICL`/`NHEDCL`: FNCA does `MOVD NHEDCL,NAMICL`
     to set inner name-list base.  How does inner-P modify
     NAMICL?  If the only modification is via NME/ENME pairs
     that always undo themselves on FAIL, the save may be
     redundant; otherwise it's needed.
  4. PDLPTR_outer: at FNCB entry (after SALT2's DECRA-3),
     PDLPTR points at `PDLPTR_outer + 3*DESCR` from the
     extended trap entry.  No save needed — compute via
     `DECRA PDLPTR,3*DESCR` to get back to PDLPTR_outer.
     Possibly: PDLPTR_outer == PDLHED_outer if FNCA is the
     first thing in the pattern — needs verification.
  5. After audit, write the SIL fix in v311.sil only.
     Regenerate via `./snobol4 -b genc.sno --with BLOCKS
     v311.sil > snobol4.c2`.  Apply the established hand-edit
     dance per latent SN-26-csn-regen-fix (regen drops
     FNCP/FNCA..FNCD as top-level functions; tsort inlines
     them).  Verify tiny repro doesn't segfault.  Verify
     beauty self-host produces N>500 lines.

  **Bypass available for blocked work:** SN-26-bridge-coverage-h
  cannot close until -i is fixed.  But -g and -j are independent
  scrip work that doesn't depend on csnobol4 stability — those
  could be picked up first by a parallel session per the active-rung
  banner ("active step → SN-26-bridge-coverage-i ‖ -g ‖ -j").

  Gate: csn `snobol4 -bf -P64k -S64k beauty.sno < beauty.sno`
  produces N>500 lines without segfault and without "Caught
  signal" diagnostic.  PLUS Smoke=7, Broker=49 preserved.

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

**Dependencies:** -e → -f → -g → -i → -j → -h.  -i (csn FENCE
bug) and -j (scrip formatting divergence) BOTH block -h since
-h needs all three runtimes producing comparable output on the
new beauty.sno.  -h may also pull SN-27 forward.
**Sequencing:** active step is -g (existing); -i is parallel-
prioritizable since it's a pure csnobol4 fix orthogonal to
scrip work.

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
- csnobol4 @ `b01b47b`
- active step → SN-26-bridge-coverage-i (csn FENCE(P) builtin
  segfault — runtime stability blocker for -h) PARALLEL with
  SN-26-bridge-coverage-g (scrip subscript-set fire-point —
  orthogonal scrip work) and SN-26-bridge-coverage-j (scrip
  formatting divergence on beauty)

**Gates:** Smoke=7, Broker=49. Bridge smokes (csn-bridge-a/b/c,
spl-bridge, spl-bridge-d, auto-binary, label-flow) all PASS as of
session #36.  Session #38 reverified Smoke=7, Broker=49 at session
start before any work.  Session #39 was analysis-only (no code
changes, no rebuilds beyond initial csnobol4 build); gates not
re-run but unchanged from session #38 since no source modified.
auto-binary verifies streaming-intern semantics end-to-end
(NAME_DEF on the wire, no sidecar written).  label-flow PASS=5
(csn=3 LABELs, sbl=4 LABELs, scrip ir-run=3, sm-run=4, jit-run=4).

**Beauty self-host status (session #36, post corpus `7041a14`):**
- SPITBOL x64 `-bf`: **CLEAN** — 646 lines, md5
  `abfd19a7a834484a96e824851caee159`
- CSNOBOL4 `-bf`: **SIGSEGV** at beauty.sno:616 statement 1074
  during `*snoParse` pattern match.  Bug in builtin `FENCE(P)`
  pattern primitive; bisected to commits `7654cda` + `5990456`
  (FENCE(P) implementation work).  See SN-26-bridge-coverage-i.
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
