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

## Rung ladder — closed rungs

Status code: `[x]` = done, `[~]` = deferred/partial, `[ ]` = open.
Full detail for closed rungs lives in the archive; one-line status here.

### Phase 1 — IR-run (DONE: SN-1..SN-5, SN-14..SN-16, SN-19)

- [x] **SN-20** — NAM push/pop self-unwinding (thaw folded into `name_commit_value`). one4all @ `8964586e`.
- [x] **SN-21** — Unified `NAME_t` + flat NAM stack; one lvalue concept. Landed SN-21a..e. one4all @ `8964586e`.
- [x] **SN-17** — Porter stemmer gap closed (2026-04-19). IR + SM both 100.00% / 23531 on porter.sno. Landed via SN-17a (new `SM_PAT_USERCALL`) + SN-17d (FAIL propagation in `bb_usercall`).
- [x] **SN-17a** — Added `SM_PAT_USERCALL` opcode. one4all @ `f2cf3494`.
- [~] **SN-17b** — Unify `bb_build` dispatch. **DEFERRED** — two dispatchers produce different artifacts (C closure vs x86 trampoline); unification not required once SN-17d landed.
- [~] **SN-17c** — Unify SM opcode handlers. **DEFERRED** for same reason as SN-17b.
- [x] **SN-17d** — Fixed `*fn()` FAIL propagation in `bb_usercall`. one4all @ `9d9d2dd3`.
- [x] **SN-6** — Full corpus PASS=225/225 in all three modes (2026-04-20). SN-6a added `SM_PAT_REFNAME` opcode for `--sm-run` self-recursive patterns.
- [x] **SN-22** — NAM API reduction: push + pop only, no marks, no rollback (2026-04-19). Landed SN-22a..d; broker recovered +1 (48→49).
- [~] **SN-6b** — expr_eval arithmetic path. DT_E thaw gap closed 2026-04-19; expr_eval flipped PASS via SN-23g.
- [x] **SN-6c** — Recursive pattern NAM corruption closed for `--ir-run` via SN-23d-follow-up. one4all @ `d61a580e`.
- [x] **SN-23** — Per-pattern NAM context, SIL-matching API (2026-04-19). Final API is 5 entries mapping 1:1 to SIL NMD primitives. one4all @ `a556167b`.

### Phase 2 — SM-run (gated on SN-6, DONE)

- [x] **SN-7** — beauty subsystem drivers self-host (2026-04-19). Gate at PASS=51/51 (17 drivers × 3 modes). **Overclaimed** — see SN-7-note and SN-26.
- [x] **SN-8** — Args-on-stack SM opcodes for `. *fn(args)` / `$ *fn(args)` / bare `*fn(args)` (2026-04-19). Added `SM_PAT_CAPTURE_FN_ARGS` and `SM_PAT_USERCALL_ARGS`.
- [~] **SN-7-note** — 2026-04-20 reassessment: SN-7's 51/51 tests subsystem unit drivers, NOT literal `beauty.sno < beauty.sno` self-application. Real self-host work tracked in SN-26.

### Phase 3 — JIT-run (gated on SN-9, DONE)

- [x] **SN-9** — JIT/codegen parity with `sm_interp`. Closed via SN-9a..c. Gate at 207/207/207 on crosscheck.
- [x] **SN-9a** — Closed `SM_PUSH_EXPR` gap in codegen (2026-04-19). Porter `--jit-run` from 7979-line diff to 0-line diff vs ref.
- [x] **SN-9b** — Closed remaining codegen handler gaps — `SM_BB_PUMP`, `SM_BB_ONCE` (2026-04-19). one4all @ `f8b06dc6`.
- [x] **SN-9c** — JIT parity gate: three-mode sweep codified, 207/207/207 on crosscheck (2026-04-19). 7 JIT-only failures closed via SN-9c-a..e.

### Closed: SPITBOL -f structural-keyword (won't-fix)

- [~] **SN-25** — SPITBOL `-f` bootstrap fix. **CLOSED won't-fix 2026-04-21.** Per Lon: ingress-at-lex applies to one4all only; legacy SPITBOL/CSNOBOL4 keep their `GTNVR`/`GENVUP` fold. **Consequence:** programs requiring case-sensitive structural keywords run under CSNOBOL4 `-bf`. Sub-rungs SN-25a..f + SN-25.x32 all closed with SN-25.

### SN-26 self-host sub-rungs (closed portions)

- [x] **SN-26b** — Installed `beauty.sno` (627 lines, from original SNOBOL4 bundle) + 16 minimal `.inc` files at `corpus/programs/snobol4/demo/beauty/`. Corpus commit `d85fd7e`. beauty.sno itself is the `.ref` (already beautified).

---

## Open rungs — summaries

Detail for SN-27 and SN-28 moved to the archive.  Pickers below are
enough to resume; consult archive when actually picking up one of these.

### SN-27 — UPPERCASE DATATYPE for SPITBOL x64  (opened 2026-04-21)

**Done-when:** `sbl -b` on `output=datatype('')` prints `STRING`
(not `string`).  All builtin datatypes return uppercase.

**Why:** x32, CSNOBOL4, snobol4jvm, one4all all return uppercase.
x64 is the outlier (Cheyenne Wills commit `39c9dc9`, Jan 2022 —
introduced `.culc` define in `sbl.min`).

**Preferred fix path (per SN-27a-history):** undefine `.culc` in
`sbl.min` — one-line change, rebuild via `make sbl`.  Alternative
paths (surgical output flip, full literal rewrite) in archive.

**Sub-rungs:**
- [x] **SN-27a** — Located DATATYPE table at `bootstrap/sbl.asm:1377-1421`.
- [~] **SN-27a-history** — git blame pinned `.culc` as the lever.
- [ ] **SN-27b** — Toggle `.culc` in `sbl.min`.
- [ ] **SN-27c** — Rebuild via `make sbl`.
- [ ] **SN-27d** — Verify `STRING` not `string`.
- [ ] **SN-27e** — Update RULES.md DATATYPE table.
- [ ] **SN-27f** — Decide snobol4dotnet — Lon.
- [ ] **SN-27g** — Corpus `.ref` audit for lowercase DATATYPE hardcodes.

**Gate:** Smoke=7, Broker=49, SN-7=51/51, Broad=225/225 all green against rebuilt x64.
**Dependencies:** none.  Orthogonal to SN-26 and SN-28.

### SN-30 — Align SPITBOL x64 keyword case with x32 (UPPERCASE canonical)  (opened 2026-04-24)

**Done-when:** SPITBOL x64 `sbl -bf` accepts UPPERCASE keywords
(`END`, `OUTPUT`, `INPUT`, `SPAN`, `BREAK`, etc.) instead of the
current lowercase canonical form.  Source programs written in the
common UPPERCASE SNOBOL4 convention (including `beauty.sno`) should
then self-host under x64 `-bf`, just as they do under x32 `-bf` and
CSNOBOL4 `-bf`.

**Why:** the "SPITBOL `-f` is broken" problem noted in RULES.md and
SN-25 is not actually broken — x64's canonical keyword form is
lowercase, an artifact of Cheyenne Wills's 2022 lowercasing of the
entire `sbl.min` source.  x32's `s.min` (derived from the same
MINIMAL lineage) kept UPPERCASE.  Aligning x64 to x32 fixes beauty's
self-host lane, unblocks portable `-bf` programs across all oracles,
and restores consistency with CSNOBOL4 and one4all.

**Diagnosis (from session 2026-04-24):**
- x64 `lex.sbl:209` — opcode table `'else[else]end[none end]...'`
  (lowercase).
- x32 `lex.spt:308` — `'ELSE[ELSE]END[NONE END]...'` (UPPERCASE).
- x64 `sbl.min` contains 171 lowercase `dtc /.../` directives; x32
  `s.min` contains 169 UPPERCASE `DTC /.../` directives.
- First 26 DTCs are keyword tokens that differ only in case
  (`/doub/` vs `/DOUB/` etc.).  Starting at DTC #27 the strings are
  **diagnostic messages** (`/Dump of Keyword Values/` on x32 vs
  `/DUMP OF KEYWORD VALUES/` on x64) — these are not keyword
  tokens; leave them alone.  Surgical fix, not blanket uppercasing.
- Probe evidence: `OUTPUT = 'hello'` with x64 `sbl -bf` exits 0
  silently — `OUTPUT` became a user variable because it didn't
  match the lowercase keyword table.  With `output = 'hello'` it
  prints.  With `sbl -b` (folding on) both work.

**Sub-rungs:**
- [x] **SN-30a** — Landed upstream on `x64 @ cc68516` (SN-30 agent,
  2026-04-24): 173 DTC strings in `sbl.min` flipped lowercase → UPPERCASE
  to match x32, plus FLC/FLSTG fold direction inverted (lowercase →
  UPPERCASE) via `asm.sbl` g_flc emitter change and `flstg` range-check
  byte swap.  374-line diff to `sbl.min`, 6-line diff to `asm.sbl`.
- [x] **SN-30b** — Same commit `cc68516` applied the substitutions.
  Alphabet constants (`&LCASE`/`&UCASE`), version strings, and mixed-case
  diagnostic messages left unchanged per surgical-fix discipline.
- [x] **SN-30c** — Session 2026-04-24: fresh rebuild chain exercised.
  `rm -f bin/sbl && make bootsbl && make BASEBOL=./bootsbl sbl &&
  make bininst`.  The prebuilt `bin/sbl` in the x64 checkout was
  pre-SN-30 (lowercase-canonical); `build_spitbol_oracle.sh` SKIPped
  on its presence, so the rebuild had to be forced manually.  Fix for
  next session: add a capability probe to the build script.
- [x] **SN-30d** — Verified: `OUTPUT='upper-ok' / END` prints `upper-ok`
  under new `sbl -bf`.  Inverse `output='x' / end` fails with "No END
  statement found" (correctly rejected under case-sensitive mode).
- [x] **SN-30e** — `beauty.sno < beauty.sno` under new `sbl -bf` with
  `SETL4PATH=.:/home/claude/corpus/programs/include` exits 0, produces
  649 stdout lines, 0 stderr.  Output is **byte-identical to CSNOBOL4
  HEAD `b3aeb9f`** on the same input (md5
  `408fc788ca2ef425fc1f87e26d45a7a5` on both).  Include-path mechanism
  on SPITBOL is `SETL4PATH` (not `SNOLIB` as sometimes documented);
  source of truth: `x64/osint/port.h:293` `#define SPITFILEPATH
  "SETL4PATH"`.
- [ ] **SN-30f** — Deferred until SN-26c sorts out.  Smoke/Broker gates
  depend on scrip build state, not the sbl binary; SN-30 changes are
  scoped to the oracle lane.  Explicit regression of SN-7 (51/51),
  Broad (225/225), SN-9c (207/207/207) under the new sbl still owed.
- [x] **SN-30g** — `bootstrap/{sbl.asm,err.asm,sbl.lex}` updated in
  session 2026-04-24 via manual copy (equivalent to `make makeboot`
  minus the sanity-check gate which needs a tty).  Rebuild from new
  bootstrap verified: `make bootsbl` produces a working sbl that
  prints from `OUTPUT = 'x'` under default fold.  A fresh clone of x64
  can now build SN-30 sbl from scratch without needing a pre-built
  uppercase sbl as BASEBOL.

**Notes / risks:**
- The lowercased `sbl.min` is in x64 upstream (spitbol/x64).  This
  divergence from x32 wasn't documented as intentional — it reads
  like a code-cleanliness pass that had side effects on user-facing
  keyword case.  Fix is local to our fork.
- String constants like `/abcdefghijklmnopqrstuvwxyz/` and
  `/ABCDEFGHIJKLMNOPQRSTUVWXYZ/` (lines 6121, 6125 in sbl.min) are
  the `&LCASE` / `&UCASE` keyword values and must remain their
  current case.
- Diagnostic messages (lines 27+ of DTC table) stay lowercased on
  x64 — that's cosmetic and doesn't affect `-bf`.
- Supersedes the "won't fix" closure on SN-25: SN-25's symptom
  ("No END statement found under `-f`") is now understood as a
  direct consequence of the lowercase canonical table.

**Dependencies:** orthogonal to SN-26/28/29; may interact with
SN-27 (DATATYPE case) — both are sequels of the same upstream
lowercasing pass.  Investigate whether a single pass can address
both.

---

### SN-29 — Beauty under original oracles  (opened 2026-04-23)

**Done-when:** `beauty.sno < beauty.sno` runs to completion under the
*pre-modification* oracles, using only existing corpus programs and
existing `.inc` files (no new files created).

**Why:** pins a known-good baseline.  Our modifications to the oracles
(FENCE(P) for CSNOBOL4, LOAD/UNLOAD for SPITBOL x64) sit on top of an
original that self-hosted beauty.  If self-host breaks on current HEAD,
we can regression-diff against this baseline.

**Approach:** beauty.sno was missing three compatibility `-INCLUDE`
lines present in the older `beauty/expression.sno` and `portable.inc`
usage pattern:
```
-INCLUDE 'is.inc'       # IsSnobol4() / IsSpitbol()
-INCLUDE 'FENCE.inc'    # stub FENCE(p) on SNOBOL4 (pass-through)
-INCLUDE 'io.inc'       # INPUT/OUTPUT OPSYN on SNOBOL4
```
Add these to `beauty.sno` in corpus (not duplicates — authoritative
copies already live at `corpus/programs/include/`).

**Sub-rungs:**
- [x] **SN-29a** — Build original csnobol4 at `a509cd7` (Initial
  import, pre-FENCE(P) work).  Makefile2 generation: `make Makefile2`
  first, then `make -f Makefile2 xsnobol4`.  Do **not** run top-level
  `make xsnobol4` — it tries to regen data.c2 via a bootstrap `snobol4`
  in PATH and fails.  Committed generated files (data.c, equ.h, etc.)
  are sufficient at this commit.
- [x] **SN-29b** — Add three `-INCLUDE` lines to
  `corpus/programs/snobol4/demo/beauty/beauty.sno` after
  `global.inc`.  3-line addition, no other changes.
- [x] **SN-29c** — Verify beauty self-hosts under original csnobol4
  `a509cd7` with `-bf -P 64k -S 64k -I. -I<corpus/include>`.
  **PASS** — 649 lines of beautified output, exit 0, no errors.
  Pattern-stack default (8k) and interp-stack default (4k) are **not**
  sufficient — `-P 64k -S 64k` is the minimum for beauty self-host.
- [x] **SN-29d** — Originally `[~]` because SPITBOL x64 4.0f could not
  self-host beauty under `-f`.  **Superseded by SN-30** (2026-04-24):
  the lowercase-canonical-keyword bug in `sbl.min` was patched, and
  SPITBOL x64 now self-hosts beauty under `-bf` to byte-identical
  output (md5 `408fc788ca2ef425fc1f87e26d45a7a5`).  Re-verified
  2026-04-26 (this session) on a fresh clone of x64 with the SN-30
  build.  Both oracles produce identical 649-line output.
- [ ] **SN-29e** — Idempotency scout: `beauty(beauty_output)` is **not**
  byte-identical to `beauty(beauty.sno)`.  Running beauty on its own
  beautified output emits "Parse Error".  Likely the emitted form
  includes idioms the parser rejects — `;*` inline comments get split
  onto their own lines which may or may not survive re-parse.
  Non-blocking for SN-29 completion; capture as a defect to fix later.
- [ ] **SN-29f** — Capture canonical `.ref` from csnobol4 a509cd7 run.
  Location: adjacent to `beauty.sno` in corpus.  Blocked on Lon's call
  whether this file belongs in corpus at all.

**Gate:** csnobol4 a509cd7 run produces exit 0 and 649 stdout lines.
Minimum invocation:
```bash
cd /home/claude/corpus/programs/snobol4/demo/beauty
/home/claude/csnobol4_a509cd7/snobol4 -bf -P 64k -S 64k \
    -I. -I/home/claude/corpus/programs/include \
    beauty.sno < beauty.sno
```
**Dependencies:** orthogonal to SN-26, SN-27, SN-28.

---

### SN-28 — Compact DESCR_t: 16 → 8 bytes (opened 2026-04-21)

**Goal:** halve DESCR_t cell size via arena aliasing (32-bit offsets
into an mmap slab instead of raw 64-bit pointers).  Dual-mode:
`DESCR_MODE_64` (today, default) vs `DESCR_MODE_32` (compact).
Reference model: Silly SNOBOL4 (`src/silly/arena.{c,h}`).

**Payoff:** halved cache footprint; 15–25% expected speedup on
variable-heavy programs (beauty, claws5); prepares 32-bit targets.

**Sub-rungs:**
- [ ] **SN-28a** — Macro-ize DESCR field access (`D_TAG`, `D_STR`, etc.) — pure refactor.
- [ ] **SN-28b** — Port Silly arena infrastructure to one4all.
- [ ] **SN-28c** — Migrate string allocation through the arena.
- [ ] **SN-28d** — Migrate PATND/ARBLK/TBBLK/DATINST through the arena.
- [ ] **SN-28e** — Introduce `DESCR_MODE_32` build flag + 8-byte layout.
- [ ] **SN-28f** — Performance gate (Porter/claws5/beauty).
- [ ] **SN-28g** — Documentation.
- [ ] **SN-28h** — Decide default (Lon).

**Risk:** MEDIUM-HIGH.  Gate discipline = only defense against silent corruption.
**Dependencies:** orthogonal to SN-26, SN-27.  SN-28a alone is a defensible standalone cleanup.

---

### SN-31 — scrip default case-sensitive (opened & closed 2026-04-24)

**Done-when:** scrip, run with no flag, treats `bSlash` and `BSLASH`
as distinct variables.  `.sno`/`.inc` corpus parses without
identifier collisions.

**Why:** Lon clarified 2026-04-24 that we always run SNO and INC
with case-sensitive name space.  Per ingress-at-lex rule, the canonical
form for identifiers in `.sno`/`.inc` **is** the source form.  SN-19
added `--case-sensitive` as opt-in; default remained fold-to-upper.
That default caused the stale monitor capture in SN-26c-char-ir
(variables reported as `BSLASH`, `SEMICOLON` from folded `bSlash`,
`semicolon`) and obscured whatever the real bug is.

**Sub-rungs:**
- [x] **SN-31a** — Flip `sno_fold_on` default from 1 → 0 in
  `src/frontend/snobol4/snobol4.l:60`.  Regenerated `.lex.c`
  (generated file committed per RULES.md).
- [x] **SN-31b** — Update `opt_case_sensitive` default in
  `src/driver/scrip.c:137` to 1; `--case-sensitive` flag is now a
  no-op kept for script compatibility.  Usage text updated.
- [x] **SN-31c** — Probe verifies: `bSlash='lower-b' / BSLASH='upper-B'`
  produces distinct values on default scrip (was same value under old
  default).  `POS/LEN . var` pattern-match probe against `&ALPHABET`
  agrees IR=SM=JIT on single-char extraction.
- [x] **SN-31d** — Update RULES.md "Case-sensitive name space" section
  and "How to invoke the oracles" table to reflect new default.
- [x] **SN-31e** — Gate sweep under new default: Smoke **PASS=7**,
  Broker **PASS=49** (2026-04-24, session cont.).  No regressions from
  the default flip.  Broad/crosscheck/SN-7 sweeps owed in a subsequent
  session; the two fast gates suffice for closure.
- [~] **SN-31f** — No regressions, so no triage needed.  Closing as
  not-required.

**Gate:** `bash scripts/test_smoke_snobol4.sh` PASS=7 and
`bash scripts/test_smoke_unified_broker.sh` PASS=49 on new default.

**Dependencies:** none.  Precedes SN-26c-char-ir — the monitor
capture for that rung needs redoing under case-sensitive default.

---

## Active rung — SN-26-bridge-coverage (opened 2026-04-27, session #29)

**Goal of this rung:** make the 3-way binary harness apples-to-apples
on `beauty.sno < beauty.sno` so that subsequent SN-26c-parseerr-h
sub-h2 work can use the canonical RULES.md "read the divergence
point, not the trace" workflow.  Currently the bridges' fire-point
coverage is asymmetric, so the harness reports DIVERGE at step 1 on
a coverage gap rather than a real runtime bug.  Until this closes,
sub-h2 cannot be driven via the binary harness — it has to be driven
by reading raw stderr trace, which RULES.md forbids.

This rung is **the gate** on SN-26c-parseerr-h sub-h2 progress.

**Done-when:** `bash scripts/test_monitor_3way_sync_step_auto.sh
$BEAUTY/beauty.sno` with `STDIN_SRC=/tmp/asg.sno` reports its first
DIVERGE at a real runtime divergence between scrip and the oracles
(not on the `nul = '\x00'` coverage asymmetry from
`global.inc:2`'s `&ALPHABET POS(0) LEN(1) . nul`).  Both oracles
must emit a VALUE wire record for every `.`-capture commit, just
as scrip does today.

**Sub-rungs (sequenced — work in order):**

- [x] **SN-26-bridge-coverage-a — SN-26-csn-bridge-c** — Closed
  2026-04-27 session #30 (csnobol4 @ `ad993fe`, corpus @ `fab43a1`,
  one4all @ `dfc88e8e`, x64 @ `040d063`).  Coverage went beyond the
  originally-scoped NMD4-only patch when Lon flagged that catch-all
  must handle every lvalue form: `PAT . X`, `PAT $ X`, `@X`, plus
  array/table element stores via `a<i,j>` and `d<'k'>`.

  **Landed in v311.sil + snobol4.c + isnobol4.c:**
    * **NMD4 (line 6167)** — `XCALLC monitor_emit_value,(TVAL,VVAL)`
      for `PAT . X` and `PAT . *f(X)`.  Both forms converge here
      because EXPEVL resolves the `*f(X)` deferred form back through
      NMD5 → NMD4.
    * **ENMI3 (line 4254)** — `XCALLC monitor_emit_value,(YPTR,VVAL)`
      for `PAT $ X` (immediate value-assignment in pattern match).
    * **ATP (line 3930)** — `XCALLC monitor_emit_value,(XPTR,NVAL)`
      for `@X` (cursor-position capture).
  Hand-applied equivalent C edits at L_NMD4, L_ENMI3, L_ATP1 in both
  generated C files per the SN-26-csn-bridge-a-xcallc precedent
  (`SN-26-csn-regen-fix` remains owed but unblocking).  All 5
  LOCAPT-TVALL sites in v311.sil now emit a wire record on the same
  step the trace machinery already chose as a "post-store commit"
  point.

  **NEW lvalue_name_id() helper in monitor_ipc_runtime.c:**
  Array element (a<i,j>) and table slot (d<'k'>) stores route
  through ASGNVV with a NAME descriptor whose `.a.i` points into
  anonymous element storage rather than at a vrblk with a name
  field.  Reading +BCDFLD bytes yielded GC bookkeeping / ARBLK
  headers that corrupted the wire when interned naively.  Helper
  validates candidate name characters as printable-ASCII identifier
  bytes; on failure it interns the sentinel `<lval>` so the wire
  stays well-formed.  Symmetric edit in
  `x64/osint/monitor_ipc_runtime.c` (zysmv): empty-name vrblks
  (system variables, anonymous slots) now emit `<lval>` instead of
  silently dropping.

  **Validation (probe_complex.sno, all 5 LHS forms):**
  ```
  myname='unset'                    record #0  (ASGNVV)
  S='AXBYC' / S ANY('AB') . dotcap  records #1-2  (ASGNVV+NMD4)
  S2='AXBYC' / S2 ANY('AB') $ dolcap  records #3-4 (ASGNVV+ENMI3)
  S3='AXBYC' / PAT . *myfn('hi')   records #5-9 (NMD4 via *f, with
                                     interleaved CALL/inner-VALUE/RETURN)
  a=ARRAY(...); a<1,2>='array_elem'  records #10-11 (#11 uses <lval>)
  d=TABLE();   d<'mykey'>='tbl_elem' records #12-13 (#13 uses <lval>)
  END                                record #14
  ```
  Sidecar names: `myname S dotcap S2 dolcap S3 myfn a <lval> d`.

  **Permanent gate** added: `scripts/test_smoke_sn26_csn_bridge_c.sh`
  PASS=1 (3 records: ASGNVV+NMD4+END from a minimal probe).

  **3-way auto harness on `beauty.sno < /tmp/asg.sno`** now reaches a
  clean first-divergence:
  ```
  [ctrl] DIVERGE step 1
    csn: VALUE (id=0) = STRING(1)='\x00'
    spl: VALUE (id=0) = INT=1
    scr: VALUE (id=0) = STRING(1)='\x00'
  ```
  csn and scr **agree** on the first record (`nul='\x00'` from
  `global.inc:2`'s `&ALPHABET POS(0) LEN(1) . nul` — NMD4 fires now).
  SPITBOL still diverges because its bridge doesn't fire on `.`-capture
  yet (sbl.min `pnth4` site), so its first record is `TRUE=1` from
  global.inc:23.  Closing -b will eliminate this asymmetry.

  **Gates:** Smoke=7, Broker=49, csn-bridge-a=1, csn-bridge-b=1,
  csn-bridge-c=1, spl-bridge=1, sn26_auto_binary=1.  SN-30 invariant
  preserved (beauty md5 still `408fc788ca2ef425fc1f87e26d45a7a5`).

- [ ] **SN-26-bridge-coverage-b — SPL fire-point coverage to match
  SN-26-bridge-coverage-a** — The CSN side patched 5 LOCAPT-TVALL
  sites in v311.sil.  SPL needs symmetric coverage but achieves it
  with **only two fire-points** by exploiting SPL's natural
  assignment chokepoints.  Plan revised in session #31 (2026-04-27)
  after reading sbl.min and `osint/monitor_ipc_runtime.c` directly.

  **Why two fire-points cover all five SIL sites.**  SPITBOL routes
  every non-direct-vrsto store through one of two procedures:

  | Procedure | Line | Calling convention | What goes through it |
  |-----------|-----:|--------------------|----------------------|
  | `asign`   | 17592 | xl=name base, wa=offset, wb=value | `o_ass` (X=Y when not direct vrsto), `o_rpl` (pattern substitute, merges into `oass0`), `a<i,j>=v`, `d<'k'>=v`, expression-variable evaluation |
  | `asinp`   | 17843 | same as asign            | `pnth4` (`PAT . X`), `p_imc` (`PAT $ X`), `p_cas` (`@X`); falls through to `asign` for trapped vars |

  Both procedures unconditionally execute `add xl,wa` then `mov (xl),wb`
  to perform the in-place store on the untrapped fast path
  (`asign:asg01` line 17596–17601 and `asinp` line 17844–17849).
  After `add xl,wa`, **`xl` holds the vrsto-field pointer** —
  exactly what `zysmv` expects in `xr` per the existing b_vrs contract
  (`b_vrs` at sbl.min line 11082 calls `jsr sysmv` with `xr` = vrsto
  field, value at `(xs)+1` after the syscall macro pops the return
  address).

  **The fire-point shape (4 instructions + comment).**  Inserted
  immediately before each procedure's `mov (xl),wb` in-place store:

  ```minimal
  *  SN-26-bridge-coverage-b: monitor fire-point.
  *  At entry: xl = vrsto field (post add at line ~17596 / ~17844),
  *            wb = value pointer.
  *  zysmv contract: xr = vrsto field, (xs)+1 = value (after RA push).
         mov  -(xs),wb         stack value pointer for sysmv
         mov  xr,xl            xr = vrsto field = xl
         jsr  sysmv            emit VALUE record on monitor wire
         mov  wb,(xs)+         pop value back
         mov  (xl),wb          [orig: in-place store]
  ```

  No save/restore of `xl`/`wa`/`xr` needed — the syscall thunk
  already preserves all caller-saved registers via the
  `syscall_init`/`syscall_exit` save-globals discipline (int.asm
  lines 624–652).  Only `wb` needs explicit handling because we
  use it to feed `(xs)+1` for the C side.

  **Why no overlap with the existing `b_vrs` fire-point.**
  `b_vrs` is invoked by **direct vrsto dispatch** from generated
  code (when the compiler emits `lcw xr ; bri (xr)` after loading
  a vrblk's vrsto field — the fast path for ordinary `X = Y` on
  simple variables).  `asign` and `asinp` are reached by an
  entirely different chain: `o_ass`, `o_rpl`, `o_amn`/`o_amv`
  (array-ref `arref`), pattern-match procedures.  The two paths
  do not intersect on the same statement.  Verified via the
  existing SN-26-spl-bridge-b probe: `S = 'hello world'` produced
  one b_vrs record (no asign trip) and `S 'world' = 'there'`
  produced no record at all (b_vrs not invoked for o_rpl) — that
  missing record is the SN-26-spl-bridge-c gap, exactly what the
  asign fire-point will close.

  **C-side guard needed: printable-ASCII validation in
  `spl_vrblk_name`.**  For `a<i,j>=v` and `d<'k'>=v`, the post-
  `add xl,wa` pointer is mid-arblk / mid-tbblk, not a real vrblk.
  Back-computing `vr = xl - vrsto_offset` (the existing zysmv
  trick at lines 333–335) yields a fake vrblk whose `vrlen` field
  reads whatever the previous arblk slot held — could be a positive
  integer, in which case `spl_vrblk_name` reads garbage from
  `vr->vrchs` into the names sidecar.  CSN handles this with
  `lvalue_name_id()` (printable-ASCII validation, fall through to
  `<lval>` on failure).  SPL needs the same.  Add a guard in
  `spl_vrblk_name` (or equivalently in `zysmv` after the call):

  ```c
  /* Validate name as printable ASCII identifier.  If any byte is
   * non-printable or len is absurdly large (>255), fall through
   * to <lval> sentinel.  Mirrors CSN's lvalue_name_id() per
   * SN-26-bridge-coverage-a. */
  if (nl > 0) {
      if (nl > 255) { nl = 0; }
      else {
          for (int i = 0; i < nl; i++) {
              unsigned char c = (unsigned char)np[i];
              if (c < 0x20 || c >= 0x7f) { nl = 0; break; }
          }
      }
  }
  if (nl == 0) { np = "<lval>"; nl = 6; }
  ```

  **Sites to patch in sbl.min:**

  | Site | Line (current HEAD) | Insert position |
  |------|--------------------:|-----------------|
  | `asign:asg01` | 17596 (`add xl,wa`) | between line 17596 and line 17599 (`mov (xl),wb`) |
  | `asinp` body  | 17844 (`add xl,wa`) | between line 17844 and line 17847 (`mov (xl),wb`) |

  Both insertion points are 4 lines of new code, no register save
  beyond the explicit `wb` push/pop.

  **Sites to patch in `osint/monitor_ipc_runtime.c`:**

  | Function | Line range | Change |
  |----------|-----------:|--------|
  | `spl_vrblk_name` | 289–300 | Add printable-ASCII validation; clamp `nl=0` on failure so caller sees empty name and falls to `<lval>` |
  | (no thunk changes needed — sysmv already exists at int.asm:832–834) |

  **Why this is better than the originally-suggested pnth4 shape.**
  The session #29 plan suggested four separate fire-points
  (pnth4 / pnth5 / pnth6 indexed-array / table) with custom register
  arithmetic at each site (`mov xr,xl ; add xr,wa`).  After reading
  the actual sources, every one of those sites lands at `jsr asinp`
  with the same calling convention.  Instrumenting the *callee*
  (asinp itself) replaces four sites with one, and incidentally
  closes the SJSRV1 gap (SN-26-spl-bridge-c) by also instrumenting
  asign — which o_rpl falls through into.  The "tbd — analog of
  pnth4 for `$`" / "tbd — indexed stores" entries in the table
  above are subsumed: `p_imc` (line 12095) and `p_cas` (line 11893)
  both call `jsr asinp`, and `arref`-mediated stores call `o_ass`
  → `asign`.

  **Build chain (RULES.md SN-30g, full rebuild required):**
  ```bash
  cd /home/claude/x64
  # 1. Edit osint/monitor_ipc_runtime.c (add ASCII guard).
  # 2. Edit sbl.min (insert 2 fire-point blocks).
  # 3. Force rebuild — build_spitbol_oracle.sh SKIPs on prebuilt sbl:
  rm -f bin/sbl
  make bootsbl
  make BASEBOL=./bootsbl sbl
  make bininst
  # 4. Regen bootstrap so fresh clones can build:
  make makeboot
  ```

  **Validation:**
  1. `bash scripts/test_smoke_sn26_spl_bridge.sh` PASS=1
     (regression — existing 6-record b_vrs probe must still pass).
  2. `probe_complex.sno` (planted at
     `corpus/programs/snobol4/demo/csn_bridge_c/probe_c.sno`)
     produces a wire with `dotcap`, `dolcap`, `<lval>` records
     symmetric to CSN's output (CSN shape: 14 records + END;
     SPL must match record-for-record).
  3. **SN-30 invariant**: `beauty.sno < beauty.sno` under
     `sbl -bf` md5 still `408fc788ca2ef425fc1f87e26d45a7a5`.
  4. Smoke=7, Broker=49 must stay green.
  5. New permanent gate `scripts/test_smoke_sn26_spl_bridge_d.sh`
     (PASS=1) for the `.`-capture probe specifically — landed
     alongside the patch.

  **Key sbl.min insight that makes this plan work** (not in
  archive — discovered session #31): `asinp` and `asign` share
  identical untrapped-fast-path shape (`add xl,wa` then
  `mov (xl),wb`).  This means a single fire-point shape covers
  both call sites, and both procedures together cover every
  non-vrsto-direct store.  The `vrsto` offset is 1 word
  (`vrsto equ vrget+1` at sbl.min:5456), so after `add xl,wa`,
  `xl` IS the vrsto-field pointer the C-side `zysmv` expects
  via its `vrsto_field - offsetof(vrsto)` trick.

- [ ] **SN-26-bridge-coverage-c — 3-way validation on beauty
  self-host** — With both oracles' bridges now firing on
  `.`-captures, re-run the 3-way auto harness:
  ```bash
  BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
  cd /home/claude/one4all
  STDIN_SRC=/tmp/asg.sno MONITOR_TIMEOUT=60 \
      bash scripts/test_monitor_3way_sync_step_auto.sh \
      $BEAUTY/beauty.sno
  ```
  Expected: the first DIVERGE no longer appears at step 1 on
  `nul = '\x00'`.  All three participants now agree through the
  `&ALPHABET ... . nul/bs/ht/...` chain in `global.inc`.  The
  controller advances to a step where scrip and the oracles
  genuinely disagree on the value of a real assignment.  Read
  **only** that divergence record's last-agree + first-disagree
  pair.  This is the canonical hand-off point to SN-26c-parseerr-h
  sub-h2.

- [ ] **SN-26-bridge-coverage-d — Hand sub-h2 the result** — Once
  the canonical divergence point is known from sub-rung -c above,
  re-open SN-26c-parseerr-h sub-h2 with a clean ground-truth
  record pair and proceed to fix the runtime.  Session #29's
  forensic hint (`Reduce('..', DT_FAIL)` vs `Reduce('..', EXPRESSION)`,
  likely caused by E_VAR fallback not covering DT_E thaw inside
  NM_CALL) should be **verified** against the controller's
  divergence record before any code change — RULES.md "read the
  divergence point, not the trace".

**Gate after each sub-rung:** Smoke=7, Broker=49 plus the new and
existing bridge smoke scripts (csn-bridge-a=1, csn-bridge-b=1,
csn-bridge-c=1, spl-bridge=1, spl-bridge-d=1, auto-binary=1).

**Dependencies:** None open.  This rung sequences before any further
sub-h2 runtime work.

**Estimated session count:** 2 (one each for -a and -b, then -c and
-d in a single follow-up session).  Both -a and -b are
scaffolding-equivalent in shape to existing landed work
(SN-26-csn-bridge-a-xcallc, SN-26-spl-bridge-b) and dominated by
validation rather than new code.

---

## Active rung — SN-26c-parseerr (opened 2026-04-25)

Sub-rungs `stmt153` and `stmt637` closed in sessions #3 and #4
(commits `187c227a` and `6225ce4e` — see Closed-rung pointers
at end of file for one-line summaries).  Active sub-rung:

### SN-26c-parseerr — `Parse Error` at line ~38 of `scrip --ir-run beauty.sno < beauty.sno`

**Active blocker for SN-26 self-host.**  Sub-rungs `a`..`g` closed in
sessions #5–#11 (commit hashes in git log).  Sub-rung `h` decomposed
into two distinct bugs in session #12 (commit `223a1284`):

- [x] **sub-h1** — bare `*fn()` with NRETURN treated as anchored-match
  instead of epsilon.  Fixed in `223a1284`.  Did not move beauty.
- [ ] **sub-h2** — chained `.`-captures (`epsilon . *Shift(...)`) across
  nested pattern calls don't all commit by the time `Reduce(snoStmt, 7)`
  runs.  **Open.**  Sessions #13–#16 below.

#### Diagnostic state (session #13, 2026-04-26)

NM_CALL timeline in scrip diverges from oracle on first beauty stmt
(`x = 'hello'`):

```
oracle: 7×Shift, then Reduce(snoStmt,7), then Reduce(snoParse,1)
scrip:  5×Shift, Reduce(snoStmt,7), 2×Shift, Reduce(snoParse,1)
```

Reduce fires before the trailing 2 Shifts complete → c[1..7] in pp_snoStmt
ends with 2 nulls instead of the expected snoLabel/snoId at c[1..2].
Beauty's pp_snoStmt sees `c[2]=null`, takes the no-LHS branch, prints just
the RHS — visible as the missing `x = ` prefix in scrip's output.

Probe series h1..h15 isolated this:
- Single `*fn()` NRETURN: works (sub-h1 fix).
- Chained `*f() *f()` with RETURN: works.
- Chained `epsilon . *Push()` deep nests: works in isolation.
- Beauty's snoStmt+snoCommand+nInc nesting: bug reproduces.

The bug is **specifically nested pattern-call boundaries** that beauty
combines:  `*snoStmt` inside `snoCommand`'s FENCE alternation, with
the outer `& 7` reduce pushed as a sibling of `*snoStmt`'s captures,
and nInc()'s NM_CALL slot also in the active NAM ctx.

#### Code locations to investigate (next session)

| File | Role |
|------|------|
| `src/runtime/x86/snobol4_nmd.c` | NAM ctx, NAME_push/commit |
| `src/runtime/x86/bb_boxes.c` `bb_cap` | γ/β/ω deferred-capture FSM |
| `src/runtime/x86/bb_broker.c` | nested pattern-call entry/exit |
| `src/driver/interp.c` E_DEFER, E_INDIRECT | `*var` deferred reference |

Watch for code that calls `name_commit_value` on the *current* ctx
mid-pattern (not just at top-level statement boundary).  A premature
commit between Shift#5 and Shift#6 fires the pending Reduce slot early.

#### Reproduce (next session)

```bash
# Standard setup chain
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh

# 1-line repro of beauty failure:
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
printf "                  x              =  'hello'\nEND\n" > /tmp/asg.sno
SNO_LIB=/home/claude/corpus/programs/include \
    /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno < /tmp/asg.sno
# oracle: full beautified output with `x = ` prefix
# scrip:  emits only `'hello'` (LHS missing)

# NM_CALL timeline trace (the smoking gun):
SNO_LIB=/home/claude/corpus/programs/include ONE4ALL_USERCALL_TRACE=1 \
    /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno < /tmp/asg.sno \
    > /tmp/scrip.out 2> /tmp/scrip.err
grep "^NM_CALL" /tmp/scrip.err   # shows misorder: 5×Shift, Reduce, 2×Shift

# Oracle reference (md5 408fc788ca2ef425fc1f87e26d45a7a5):
cd /home/claude/corpus/programs/snobol4/demo/beauty
SETL4PATH=".:/home/claude/corpus/programs/include" \
    /home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno | md5sum
```

#### Setup footguns

- **Required clones for clean gates:** `.github`, `one4all`, `corpus`,
  `csnobol4`, `x64`.  Broker drops 49→48 if `corpus` missing
  (rung01 ICN SKIPs).
- **build_spitbol_oracle.sh** SKIPs on prebuilt `bin/sbl`.  The
  prebuilt in current x64 IS the SN-30 build; SKIP is correct.
- **scrip-monitor needs build_scrip.sh first** to populate
  `/tmp/si_objs/`.  Workflow: `build_scrip.sh` then
  `make scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a`.
  After modifying `runtime/x86/*.c`, force-refresh with
  `rm -f /tmp/si_objs/<file>.o && bash scripts/build_scrip.sh`.

**Gate:** Smoke=7, Broker=49 after any fix.
**Dependencies:** None open.

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
- **SN-26-spl-bridge-c** — Pattern-substitute store-back fire-point for SPITBOL. SPITBOL's pattern-substitute store doesn't traverse `b_vrs`, so SPL probe drops one record vs CSN probe (`S 'world' = 'there'`). Find SPITBOL's store-back point (likely inside `match`/`bpat`/`assn` epilog around the `pmval` flag). Now subsumed by SN-26-bridge-coverage-b's SJSRV1-counterpart work.
- **SN-26-binmon-nreturn-divergence** — Oracle-vs-oracle divergence on `dummy` (CSN: STRING, SPL: NAME) at step 162 of beauty self-host. Likely rooted in how each runtime represents the `.dummy` NRETURN value when the dot-star call happens. Low priority — exposes a real semantic gap but does not gate scrip work.
- **MWK_LABEL events** — If structural-flow events are desired in future, add `MWK_LABEL` to `monitor_wire.h` and fire on STNO advancing. Not gating sub-h2.
- **Legacy LOAD-based monitor cleanup** — `build_monitor_ipc_*_library.sh` (3 scripts) build the legacy LOAD() `.so` modules; now unreferenced by any harness but harmless. Could be deleted in a cleanup pass alongside their `monitor_ipc*.c` sources in `scripts/monitor/`. `runtime/x86/snobol4.c` `MONITOR_SO=builtin` sentinel is dead code now that no harness sets it.

---

## Current state

**HEADs after 2026-04-27 session #31:**
- one4all @ `dfc88e8e` — csn-bridge-c smoke + libcsnobol4.a archive monitor link (unchanged from #30)
- corpus @ `fab43a1` — csn_bridge_c/probe_c.sno (unchanged from #30)
- x64 @ `040d063` — `<lval>` sentinel for empty-name stores in zysmv (unchanged from #30)
- csnobol4 @ `ad993fe` — NMD4 + ENMI3 + ATP fire-points + lvalue_name_id helper (unchanged from #30)
- .github @ this commit — SN-26-bridge-coverage-b plan revised to asign+asinp two-fire-point approach (session #31)

**Gates (verified 2026-04-27 session #31):** Smoke **7** · Broker **49** · csn-bridge-a smoke **1** · csn-bridge-b smoke **1** · csn-bridge-c smoke **1** · spl-bridge smoke **1** · auto-binary smoke **1**.

**SN-30 invariant:** beauty.sno < beauty.sno md5 still `408fc788ca2ef425fc1f87e26d45a7a5` under SPL `-bf`.

**Session #31 outcome (HQ-only, no source changes):** Re-grounded the
SN-26-bridge-coverage-b plan in actual sbl.min reading.  Replaced the
session-#29-suggested four-site approach (pnth4 / `$`-analog / indexed
array / indexed table) with a **two-fire-point** plan at `asign` (line
17596 region) and `asinp` (line 17844 region) — the central
chokepoints all five SIL-counterpart sites route through.  Plus C-side
printable-ASCII guard in `spl_vrblk_name` to match CSN's
`lvalue_name_id` discipline.  See SN-26-bridge-coverage-b sub-rung
above for full detail and build chain.  Pruned 1069 lines of stale
session narrative from the goal file (1818→785→823 lines, the +38 is
the revised plan).  No source edits this session — actual SPL patch is
the next session's work.

---

## Closed-rung pointers (one-line summaries; full detail in git log)

Each entry: `SN-XX (commit-hash)` — outcome.

### SN-26 self-host

- **SN-26c-stmt637 (`6225ce4e`)** — `lt_find` strcasecmp → strcmp; fixes case-sensitive label collisions like `visitEnd` vs `VisitEnd` in SM lane.
- **SN-26c-stmt153 (`187c227a`)** — `sm_lower lower_stmt` swap SM_LABEL/SM_STNO emit order; fixes &STCOUNT and step-limit accounting on labeled-stmt branches.
- **SN-26c-char-ir** — `nv_snapshot` malloc → GC_MALLOC; snapshot-layer GC bug, IR runtime never wrong.
- **SN-26c-parseerr-c..g (`09d73258`..`7e41175c`)** — defer chain for `*fn(args)` patterns: E_FNC subargs, E_VAR extension, anchored-match string mishandling, `$ *fn(args)` immediate XCALLCAP, value-context E_SEQ with E_DEFER children.
- **SN-26c-parseerr-h sub-h1 (`223a1284`)** — bare `*fn()` with NRETURN now epsilon-matches.
- **SN-26c-pre-CSN-a3** — PDLPTR corruption [UNREPRODUCING on csnobol4 b3aeb9f]; closed without patch.

### SN-26 monitor / 3-way harness (sessions #15–#28)

- **SN-26-keyword-catchall** (session #19) — `kw_trace` global + `&TRACE` keyword + `comm_var` catch-all branch in `runtime/x86/snobol4.{c,h}`; source rewriters (`inject_traces*.py`) deleted from `scripts/monitor/`.
- **SN-26-binmon-typed** (session #17) — typed LOAD entry points (`MON_PUT_S/I/R/O_VALUE/RETURN`) + DATATYPE dispatch landed; ARRAY/TABLE/PATTERN/CODE/REAL flow through binary harness without runtime type-check failures.
- **SN-26-binmon-3way** (session #18) — scrip --ir-run wired in as third participant in binary harness; pre-registers `MON_*` as C builtins; LOAD stub for `MON_*` prototypes; `_TRACE_` 4-arg form honored with re-entry guard; `interp.c` E_VAR fallback treats FAIL returns as NULVCL.
- **SN-26-scrip-env-gate** (session #20) — `SCRIP_FTRACE`/`SCRIP_TRACE` env vars in `SNO_INIT_fn` auto-activate `kw_ftrace`/`kw_trace` at startup; ~22-line diff.
- **SN-26-auto-binary-scrip** (session #21) — scrip's `comm_var`/`comm_call`/`comm_return` emit binary records via `mon_send_bin` when `MONITOR_BIN=1`; names auto-interned; atexit dump to `MONITOR_NAMES_OUT`. Smoke `test_smoke_sn26_auto_binary.sh` PASS=1.
- **SN-26-auto-controller** (`05ae400b`, session #22) — `monitor_sync_bin.py` 4-part `NAME:READY:GO:NAMES` spec; per-participant name resolution; tuple compare on `(kind, name_string, type, value)`. Backward compatible with legacy 3-part spec.
- **SN-26-auto-harness** (`2042f294`, session #23) — `test_monitor_3way_sync_step_auto.sh` written; no inject step; `SCRIP_ONLY=1` mode for single-participant validation.
- **SN-26-csn-bridge-a** (`c1843eb`/`3f6bdbb3`, session #24) — `monitor_ipc_runtime.c` (412 lines, no internal-header deps) + standalone smoke harness in csnobol4; build wiring via `Makefile2.m4`. Three public C entry points (`monitor_emit_value`/`_call`/`_return`) ready for XCALLC. End-to-end FIFO probe validated.
- **SN-26-csn-bridge-a-xcallc** (session #25) — `XCALLC monitor_emit_value,(XPTR,YPTR)` at ASGNVV in `v311.sil` (line 5938). Hand-applied equivalent at `L_ASGNVV` in both generated C files. Build-path footgun: regen drops FNCP top-level (see SN-26-csn-regen-fix latent). End-to-end probe: `x = 'hello'` → 1 VALUE record + MWK_END.
- **SN-26-csn-bridge-b** (session #26) — Three remaining XCALLC sites: `monitor_emit_value` at SJSRV1, `monitor_emit_call` at DEFF18, `monitor_emit_return` at DEFF20. RETPCL is &RTNTYPE (not result-value); result delivered via preceding VALUE record. End-to-end probe (DEFINE+SQR(7)) produces 7-record wire. Smoke `test_smoke_sn26_csn_bridge_b.sh` PASS=1.
- **SN-26-spl-bridge-a/b** (session #27) — SPITBOL x64 monitor bridge: three new MINIMAL externs `sysmv`/`sysmc`/`sysmr` in sbl.min, thunked in int.asm, implemented in `osint/monitor_ipc_runtime.c` (468 lines) using SPITBOL block layout via `spitblks.h`. Three fire-points: `b_vrs` → sysmv (universal var-store), `bpf09` predecessor → sysmc (function call), retrn body → sysmr. Bootstrap files regenerated via `make makeboot`. End-to-end probe at `corpus/programs/snobol4/demo/spl_bridge/probe.sno` → 6-record wire. SN-30 invariant preserved. Smoke `test_smoke_sn26_spl_bridge.sh` PASS=1.
- **SN-26-harness-rewrite** (session #28) — Sync-step harness family collapsed to one canonical `test_monitor_3way_sync_step_auto.sh` plus three thin 2-way wrappers via `PARTICIPANTS` env var (`{csn, spl, scr}`). Deleted 5 obsolete harnesses (ASM/JVM/NET-era). Net diff `scripts/`: −1078 lines. `SCRIP_ONLY=1` back-compat preserved. Validated in 7 PARTICIPANTS configurations.

For diagnostic technique on any of these (Strategy-A AddressSanitizer,
Strategy-B PDL-write-site sweep, env-gated trace decomposition), consult
the commit message of the listed hash.
