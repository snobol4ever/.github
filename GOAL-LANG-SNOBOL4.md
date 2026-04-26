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

---

## Current state

**HEADs after 2026-04-26 session #16:**
- one4all @ `988b7a70` (binary-protocol monitor scaffolding)
- corpus @ `9a62ff9` (SN-29b)
- .github @ this commit
- x64 @ `fef193e` (monitor_ipc_bin_spl.c + .gitignore)
- csnobol4 @ `b3aeb9f`

**Gates (verified 2026-04-26 session #16):** Smoke **7** · Broker **49**.

### Active rung — binary-protocol sync-step monitor (session #16)

Implemented MONITOR-BINARY-DESIGN.md.  Files added in `one4all @ 988b7a70`
and `x64 @ fef193e`:

| Path | Role |
|------|------|
| `one4all/scripts/monitor/monitor_wire.h` | 13-byte fixed header + value bytes; type tags MWT_NULL..MWT_FILE. |
| `one4all/scripts/monitor/monitor_ipc_bin_csn.c` | CSNOBOL4 LOAD()able .so. |
| `x64/monitor_ipc_bin_spl.c` | SPITBOL ABI .so (lowercase + UPPERCASE entry points). |
| `one4all/scripts/build_monitor_ipc_bin_libraries.sh` | Idempotent builder for both .so files. |
| `one4all/scripts/monitor/inject_traces_bin.py` | Trace injector + names-file emission. |
| `one4all/scripts/monitor/monitor_sync_bin.py` | Controller: tuple-equality compare; treats simultaneous EOF as clean END. |
| `one4all/scripts/monitor/tracepoints_bin.conf` | INCLUDE/EXCLUDE rules; **no IGNORE rules**. |
| `one4all/scripts/test_monitor_2way_sync_step_bin.sh` | 2-way harness. |

**Validation:** 2-way binary harness on probe (`x='hello' / y=42 / END`)
and 4-event probe (CALL/RETURN added) — both exit 0, agree byte-for-byte
on every event, clean EOF.

**Blocker:** beauty self-host through binary harness fails at first MV
call on a non-string variable (`ppStop = ARRAY('1:4')`).  Both oracles
type-check the LOAD prototype's STRING declaration before invoking the
C function:

- CSNOBOL4: `Error 1 — Illegal data type`
- SPITBOL:  `ERROR 039 — external function argument is not a string`

Earlier reading of `lib/load.h` ("XXX check nargs?? check datatypes??")
was misleading — the type-check happens before the C call, not within it.

#### Three options for the fix

1. **Pass NAME instead of value** — declare 2nd arg as NAME, call
   `MON_PUT_VALUE(N, .N)`.  C-side dereferences via runtime's
   NAME→value lookup.  More elegant; ABI-specific work in each .so.

2. **Typed entry points + DATATYPE() dispatch** — recommended.
   Declare separate `MON_PUT_STRING(N,$N)` / `MON_PUT_INTEGER(N,$N)` /
   `MON_PUT_REAL(N,$N)` / `MON_PUT_OPAQUE(N, type_string)`.  SNOBOL4
   wrapper does `DATATYPE($N)` discrimination.  ~1 hour of work.

3. **CONVERT to STRING with type tag prefix** — defeats the redesign;
   reject.

#### Next-session work order

1. Standard setup chain.  Required clones: `.github`, `one4all`,
   `corpus`, `csnobol4`, `x64`.
2. Implement option 2: add `MON_PUT_STRING` / `MON_PUT_INTEGER` /
   `MON_PUT_REAL` / `MON_PUT_OPAQUE` to both `monitor_ipc_bin_csn.c`
   and `monitor_ipc_bin_spl.c`.  Update `inject_traces_bin.py`
   `MONITOR_PREAMBLE` MV callback to dispatch via DATATYPE($N).
3. Re-run probes (probe_bin, probe_bin2) — should still pass.
4. Re-run `beauty.sno < beauty.sno` 2-way binary — target: 0
   divergences across all events.  Expected 1000s of events.
5. Wire scrip --ir-run as 3rd participant.  First divergence event
   IS SN-26c-parseerr-h sub-h2.  Same for --sm-run, --jit-run.

#### Notes

- **CALL/RETURN trace 4-arg form** does not invoke the callback in
  either oracle — only the dialect's built-in trace OUTPUT fires.
  Pre-existing limitation, both protocols affected equally.  CALL/RETURN
  tracking would need explicit `MC(name,'')` calls inserted at function
  entry/exit.  Defer until needed.
- **Session #15 completed:** restored 2-way text-protocol harness as
  reference (`scripts/monitor/monitor_ipc_sync.c` + `inject_traces.py`
  + `monitor_sync.py` + `test_monitor_2way_sync_step.sh`); fixed
  `interp.c:953` E_ASSIGN trace hook bypassing `set_and_trace`.
  See commit `5ad12633`.

---

## Closed-rung pointers (one-line summaries; full detail in git log)

Each entry: `SN-XX (commit-hash)` — outcome.

- **SN-26c-stmt637 (`6225ce4e`)** — `lt_find` strcasecmp → strcmp; fixes case-sensitive label collisions like `visitEnd` vs `VisitEnd` in SM lane.
- **SN-26c-stmt153 (`187c227a`)** — `sm_lower lower_stmt` swap SM_LABEL/SM_STNO emit order; fixes &STCOUNT and step-limit accounting on labeled-stmt branches.
- **SN-26c-char-ir** — `nv_snapshot` malloc → GC_MALLOC; snapshot-layer GC bug, IR runtime never wrong.
- **SN-26c-parseerr-c..g (`09d73258`..`7e41175c`)** — defer chain for `*fn(args)` patterns: E_FNC subargs, E_VAR extension, anchored-match string mishandling, `$ *fn(args)` immediate XCALLCAP, value-context E_SEQ with E_DEFER children.
- **SN-26c-parseerr-h sub-h1 (`223a1284`)** — bare `*fn()` with NRETURN now epsilon-matches.
- **SN-26c-pre-CSN-a3** — PDLPTR corruption [UNREPRODUCING on csnobol4 b3aeb9f]; closed without patch.

For diagnostic technique on any of these (Strategy-A AddressSanitizer,
Strategy-B PDL-write-site sweep, env-gated trace decomposition), consult
the commit message of the listed hash.
