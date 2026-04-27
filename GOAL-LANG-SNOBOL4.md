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

**HEADs after 2026-04-27 session #29:**
- one4all @ unchanged this session (no code changes)
- corpus @ unchanged this session
- .github @ this commit (session #29 forensic notes added)
- x64 @ unchanged this session
- csnobol4 @ `b83db40` (unchanged this session)

**Gates (verified 2026-04-27 session #29):** Smoke **7** · Broker **49** · csn-bridge-a smoke **1** · csn-bridge-b smoke **1** · spl-bridge smoke **1** · auto-binary smoke **1**.

### Forensic notes from session #29 (2026-04-27)

No code changed.  Session focused on driving SN-26c-parseerr-h sub-h2
through the new SN-26-harness-rewrite 3-way auto harness.  Two
findings worth recording for whoever picks this up next.

**Finding #1 — bridge fire-point coverage gap (new sub-rung
SN-26-csn-bridge-c + SN-26-spl-bridge-d).**

The 3-way auto harness on `beauty.sno < /tmp/asg.sno` reports
`DIVERGE step 1`:
```
csn: VALUE (id=0) = INT=1
spl: VALUE (id=0) = INT=1
scr: VALUE (id=0) = STRING(1)='\x00'
```
Both oracles' first VALUE is `TRUE = 1` from `global.inc:23`.  Scrip's
first VALUE is `nul = '\x00'` from `global.inc:2`'s
`&ALPHABET POS(0) LEN(1) . nul`.  This is **not** a runtime bug — it
is asymmetric instrumentation coverage between the bridges.

- **scrip** fires `comm_var` (VALUE record) on every `NV_SET_fn` —
  including pattern-match conditional captures (`.`-stores).
- **CSNOBOL4 bridge** (SN-26-csn-bridge-b) fires `monitor_emit_value`
  only at `ASGNVV` (line ~5938) and `SJSRV1` (line 3510) in
  `v311.sil`.  The `.`-capture commit at **`NMD4` line 6166**
  (`NMD PROC` — "Value Assignment in Pattern Matching", `PUTDC TVAL,
  DESCR,VVAL`) currently has NO fire-point.
- **SPITBOL bridge** (SN-26-spl-bridge-b) fires `sysmv` at `b_vrs`
  (line 11086) for the standard variable-store opcode, plus `sysmc`
  at `bpf09` and `sysmr` at `retrn`.  Pattern `.`-captures route
  through `pnth4` (line 12257) → `asinp` (line 17847), **bypassing
  `b_vrs` entirely**.  No fire-point at the pattern-assign path.

Until both gaps close, the binary 3-way harness compares apples to
oranges on any program that uses `.`-captures (i.e., almost every
non-trivial SNOBOL4 program — anything using `&ALPHABET POS(N) LEN(N) . name`,
which `global.inc` does 13 times before any user code runs).

**Suggested sub-rungs (open):**
- **SN-26-csn-bridge-c** — Add `XCALLC monitor_emit_value,(TVAL,VVAL)`
  immediately after `NMD4 PUTDC TVAL,DESCR,VVAL` (line 6166) in
  `v311.sil`.  Hand-apply equivalent C-level edit at the `L_NMD4`
  (or equivalent label) sites in `snobol4.c` and `isnobol4.c` per
  the SN-26-csn-bridge-a-xcallc precedent (genc.sno regen still
  drops FNCP; SN-26-csn-regen-fix still owed).  Validate by re-running
  `bash scripts/test_smoke_sn26_csn_bridge_b.sh` (must stay green at
  PASS=1 with 7 records) plus a new probe that uses `.`-capture
  (e.g., `S = 'AXBYC'; S ANY('AB') . captured`) and confirming the
  oracle now emits the captured-value VALUE record.
- **SN-26-spl-bridge-d** — Add a fire-point in `pnth4` immediately
  before (or after, with proper register saves) the `jsr asinp` at
  line 12257 of `sbl.min`.  At entry: `wa` = name offset, `xl` =
  name base, `wb` = value just sliced.  Wrap with the same
  save/restore pattern session #27 used for `bpf09`:
  ```minimal
       mov  -(xs),wb         save value
       mov  -(xs),xl         save name base
       ; xr = name vrblk = xl + wa (or similar reconstruction)
       ; jsr sysmv
       mov  xl,(xs)+         restore
       mov  wb,(xs)+         restore
  ```
  Then `jsr asinp` proceeds.  Validate via `test_smoke_sn26_spl_bridge.sh`
  (must stay PASS=1 with 6 records) plus the same `.`-capture probe.
  Note SN-30g: regenerate `bootstrap/sbl.{asm,lex}` after `sbl.min`
  edits so fresh clones can build.

Both rungs are scaffolding-equivalent in shape to existing landed
rungs (SN-26-csn-bridge-a-xcallc, SN-26-spl-bridge-b).  Estimate:
~half-session each, dominated by validation rather than code.

**Finding #2 — sub-h2 manifests as wrong arg[1] to Reduce, not as
wrong call ordering (bypassed canonical workflow to find this).**

Caveat first.  This finding came from reading `ONE4ALL_USERCALL_TRACE`
stderr directly (~291 lines of NM_CALL records), which is precisely
what RULES.md "Sync-step monitor — read the divergence point, not
the trace" forbids.  The reason it happened: with the bridge
coverage gap above, the binary harness can't be apples-to-apples
on any beauty program, so the canonical last-agree/first-disagree
output isn't trustworthy.  Whoever picks this up next should land
SN-26-csn-bridge-c + SN-26-spl-bridge-d **first**, then re-run the
3-way and let the controller report the divergence point.  This
finding is recorded as a hint, not as confirmed forensic ground
truth.

With that caveat: when scrip-only NM_CALL trace on `beauty.sno <
/tmp/asg.sno` is compared against a SPITBOL `&FTRACE = 999999`
trace on the same input (technique: prepend a 1-line `.sno` setting
`&FTRACE`, since the prepend trick works under `sbl -bf`), the
**call sequence is identical**: 4×Shift, nested PushCounter+IncCounter
×2, Shift('snoString',''hello''), Reduce('..',...), PopCounter,
Reduce('|',...), PopCounter, Shift, Shift, Reduce('snoStmt',7),
Reduce('snoParse',1), PopCounter.  No reordering, no missing calls.
The Goal file's older description of "5 Shifts, then Reduce, then
2 Shifts" is from a pre-sub-h1 state and is now stale.

The first divergence is in the **arg values**, not the call order:

| Site | SPITBOL arg[1] | scrip arg[1] |
|------|----------------|--------------|
| `Reduce('..', ...)` | `EXPRESSION` (string-tag, the bound value of the bare identifier) | `DT_FAIL` |
| `Reduce('|', ...)` | `EXPRESSION` (same) | `DT_FAIL` |
| `Reduce('snoStmt', ...)` | `7` (integer literal) | `7` (integer literal — agrees) |
| `Reduce('snoParse', ...)` | `1` (integer literal) | `1` (integer literal — agrees) |

In `ShiftReduce.inc:21`, beauty does `IDENT(DATATYPE(t), 'EXPRESSION')`
to test type tags.  The bare identifier `EXPRESSION` is used elsewhere
in beauty as a sentinel value.  In SPITBOL/CSNOBOL4 an unbound
identifier read in value context returns the empty string; `Reduce`
receives the bound (or empty-string-fallback) value.  In scrip the
same read produces `DT_FAIL`, and that FAIL flows through `EVAL_fn`
inside `name_commit_value`'s `DT_E` thaw at `name_t.c:43` rather than
becoming an empty string.

The likely root cause is in the **interp.c E_VAR fallback to APPLY_fn
for zero-arg builtins** path that landed in session #18.  Session #18
documented: *"now treats FAIL returns as 'unset variable' (NULVCL)
rather than propagating the FAIL — matches CSNOBOL4 / SPITBOL
semantics where bare unbound `VALUE` (and similar) is the empty
string when used as a function arg, not a hard failure aborting the
enclosing call."*  That fix appears to cover the direct E_VAR
fallback case but not the **deferred** path where a bare identifier
is reached via `DT_E` thaw inside `name_commit_value` for an
NM_CALL slot.  When `Reduce('..', EXPRESSION)` is built as
`pat_assign_callcap` with `EXPRESSION` lowered as a DT_E expression,
the thaw at match-commit time evaluates `EXPRESSION` and the FAIL
return isn't intercepted with the same NULVCL fallback.

**Code locations for next session to investigate:**
| File | Role |
|------|------|
| `src/runtime/x86/name_t.c:35-43` | `name_commit_value` DT_E thaw before dispatch |
| `src/runtime/x86/name_t.c:84-100` | NM_CALL DT_E thaw of fn args |
| `src/driver/interp.c` E_VAR fallback (session #18 site) | the working path; compare to NM_CALL thaw |
| `src/runtime/x86/eval_code.c` `EVAL_fn` | what does it return when the expression resolves an unbound identifier? |

**Reproducer (single line, fast):**
```bash
printf "                  x              =  'hello'\nEND\n" > /tmp/asg.sno
SETL4PATH=".:/home/claude/corpus/programs/include" /home/claude/x64/bin/sbl -bf \
    /home/claude/corpus/programs/snobol4/demo/beauty/beauty.sno < /tmp/asg.sno
# →                   x              =  'hello'   (correct)
SNO_LIB=/home/claude/corpus/programs/include /home/claude/one4all/scrip --ir-run \
    /home/claude/corpus/programs/snobol4/demo/beauty/beauty.sno < /tmp/asg.sno
# →                                  'hello'      (wrong — LHS dropped)
```

**SPITBOL `&FTRACE` ground-truth technique** (one-line, no source mod):
```bash
printf "        &FTRACE = 999999\n" > /tmp/trace_on.sno
SETL4PATH=".:/home/claude/corpus/programs/include" /home/claude/x64/bin/sbl -bf \
    /tmp/trace_on.sno /home/claude/corpus/programs/snobol4/demo/beauty/beauty.sno < /tmp/asg.sno \
    > /tmp/spl_traced.out 2>&1
grep -E "Shift|Reduce|PushCounter|IncCounter|PopCounter" /tmp/spl_traced.out
# Note: cap is 999999; 1000000+ trips ERROR 210 "keyword value too large"
```

**Once the bridge gaps close (SN-26-csn-bridge-c, SN-26-spl-bridge-d):**
re-run `bash scripts/test_monitor_3way_sync_step_auto.sh
$BEAUTY/beauty.sno` with `STDIN_SRC=/tmp/asg.sno` and let the
controller report the first divergence.  Expected: at the step
where scrip's `Reduce('..', DT_FAIL)` lands while the oracles emit
`Reduce('..', EXPRESSION-as-string)`.  That is the canonical
last-agree / first-disagree pair to drive the fix.



- [x] **SN-26-harness-rewrite** — Sync-step harness family collapsed to
  one canonical script (`test_monitor_3way_sync_step_auto.sh`) plus three
  thin 2-way wrappers.  Deleted 5 obsolete harnesses (ASM/JVM/NET-era
  and the inject-based `_3way_sync_step_bin.sh`).  Generalized the auto
  harness with a `PARTICIPANTS` env var (`{csn, spl, scr}`, first entry
  is oracle).  All four remaining `test_monitor_*.sh` scripts run via
  env-var-driven binary IPC — no source preprocessing, no LOAD-chain.
  Net diff `scripts/`: −1078 lines.  Detail in the SN-26-harness-rewrite
  closed sub-rung above.  No regressions: Smoke=7, Broker=49,
  csn-bridge-a=1, csn-bridge-b=1, spl-bridge=1.

  **Active set after this rung:**
  ```
  scripts/test_monitor_3way_sync_step_auto.sh    — canonical (any subset of csn/spl/scr)
  scripts/test_monitor_2way_sync_step.sh         — wrapper: PARTICIPANTS="csn spl"
  scripts/test_monitor_2way_sync_step_bin.sh     — wrapper: PARTICIPANTS="csn spl"
  scripts/test_monitor_2way_spitbol_vs_ir.sh     — wrapper: PARTICIPANTS="spl scr"
  ```

  **Latent follow-ups (out of scope, none gating):**
  - `build_monitor_ipc_*_library.sh` (3 scripts) build the legacy LOAD()
    `.so` modules; now unreferenced by any harness but harmless.  Could
    be deleted in a cleanup pass alongside their `monitor_ipc*.c` sources
    in `scripts/monitor/`.
  - `runtime/x86/snobol4.c` `MONITOR_SO=builtin` sentinel (session #18)
    is dead code now that no harness sets it.  Trim in a future runtime
    pass.
  - README.md and Makefile in `one4all/` still mention `monitor_ipc.so`;
    historical context, no action needed.

### Closed in session #27 (2026-04-27)

- [x] **SN-26-spl-bridge-a** + **SN-26-spl-bridge-b** — SPITBOL x64
  monitor bridge landed.  Three new MINIMAL externs `sysmv`/`sysmc`/`sysmr`
  declared in `sbl.min`, thunked in `int.asm`, implemented in
  `osint/monitor_ipc_runtime.c` (468 lines, mirror of CSNOBOL4's with
  SPITBOL block layout via `spitblks.h`).  Three fire-points patched:
  `b_vrs` (universal var-store) → sysmv, `bpf09` predecessor (function
  call gate) → sysmc, retrn body → sysmr.  End-to-end probe at
  `corpus/programs/snobol4/demo/spl_bridge/probe.sno` produces the
  expected 6-record wire (VALUE+CALL+VALUE+RETURN+VALUE+END).
  Bootstrap files (`bootstrap/sbl.{asm,lex}`, `bootstrap/err.asm`)
  regenerated via `make makeboot` so a fresh clone can build.
  SN-30 invariant preserved: `beauty.sno < beauty.sno` still md5
  `408fc788ca2ef425fc1f87e26d45a7a5`.  Permanent gate
  `scripts/test_smoke_sn26_spl_bridge.sh` PASS=1 added.

  Cross-oracle asymmetry observed and tracked as new sub-rung
  **SN-26-spl-bridge-c** (deferred): SPITBOL's pattern-substitute
  store doesn't traverse `b_vrs`, so the SPITBOL probe drops one
  record vs the CSNOBOL4 probe (`S 'world' = 'there'`).  Not
  blocking — both probes individually validate their respective
  oracle's bridge.  Full detail in the SN-26-spl-bridge sub-rung
  table above.

### Closed in session #26 (2026-04-27)

- [x] **SN-26-csn-bridge-b** — Three remaining XCALLC sites wired into
  `v311.sil` and hand-applied to `snobol4.c`/`isnobol4.c`:
  `monitor_emit_value` at SJSRV1 (pattern-substitute assignment),
  `monitor_emit_call` at DEFF18 (function entry),
  `monitor_emit_return` at DEFF20 (function exit, payload is &RTNTYPE
  per SIL trace convention — clarified in monitor_ipc_runtime.c
  header).  End-to-end probe `corpus/programs/snobol4/demo/csn_bridge_b/probe_b.sno`
  produces the expected 7-record wire stream (3xVALUE + 1xCALL +
  1xVALUE + 1xRETURN + 1xEND).  Permanent gate
  `scripts/test_smoke_sn26_csn_bridge_b.sh` PASS=1 added.  No
  regressions: Smoke=7, Broker=49, csn-bridge-a=1 all green.

  Full detail in the SN-26-csn-bridge-b sub-rung above; key items
  for resumption: (1) SIL XCALLC pattern, (2) hand-edit-the-C
  workaround due to genc.sno regen breaking FNCP — `SN-26-csn-regen-fix`
  remains owed as a follow-up rung, (3) RETPCL is &RTNTYPE not
  result-value, with the result delivered as the preceding VALUE
  record on the function-name variable.

### Closed in session #25 (2026-04-27)

- [x] **SN-26-csn-bridge-a-xcallc** — `XCALLC monitor_emit_value,(XPTR,YPTR)`
  inserted at `ASGNVV` in `v311.sil` (line 5938 region of `ASGN PROC ,` —
  the central simple-assignment store for `X = Y`).  Equivalent
  `monitor_emit_value(XPTR, YPTR);` hand-applied at `L_ASGNVV` in both
  `snobol4.c` and `isnobol4.c` because regenerating from `v311.sil` on
  current csnobol4 HEAD breaks the link (FNCP/FNCA..FNCD inlined to
  labels but referenced as functions by data_init.c — pre-existing,
  reproduces without any XCALLC edit) and also wipes the IM-15b hook
  block (commit `b3aeb9f`).  See SN-26-csn-bridge-a-xcallc detail above
  for the full footgun analysis and suggested follow-up rung
  `SN-26-csn-regen-fix`.  End-to-end FIFO probe: `x = 'hello' / END`
  produces one VALUE record (name_id=0, STRING(5)=`hello`) + MWK_END
  on the wire, sidecar dumps `id=0: X`.  Smoke=7, Broker=49,
  csn-bridge smoke=1 all green.

### Closed in session #24 (2026-04-27)

- [x] **SN-26-csn-bridge-a** — `monitor_ipc_runtime.c` (412 lines, no
  internal-header deps) + standalone `test_monitor_ipc_runtime.c` smoke
  harness landed in csnobol4 @ `c1843eb`.  Build wiring via
  `Makefile2.m4` (source of truth) — regenerated `Makefile2` committed
  alongside per RULES.md.  Three public C entry points
  (`monitor_emit_value` / `_call` / `_return`) ready for XCALLC use
  from `v311.sil`.  End-to-end validation: 6 wire records (3xVALUE
  STRING/INTEGER/REAL + CALL + RETURN + END), 4 names sidecar, all
  decode byte-equal on controller side.  Silent no-op fallback when
  env vars unset confirmed.  Companion smoke script
  `scripts/test_smoke_sn26_csn_bridge.sh` + minimal wire reader
  `scripts/monitor/read_one_wire.py` landed in one4all @ `3f6bdbb3`.
  Smoke=7, Broker=49 unchanged.  SIL XCALLC test-site held out as
  -a-xcallc to keep this commit pure-scaffolding.

### Closed in session #23 (2026-04-26)

- [x] **SN-26-auto-harness** — `test_monitor_3way_sync_step_auto.sh`
  written.  No inject step.  4-part-spec controller invocation,
  per-participant names sidecars, `SCRIP_ONLY=1` mode for
  single-participant validation.  Validated end-to-end on a DEFINE+SQR
  probe in SCRIP_ONLY mode: 14 steps, rc=0.  one4all @ `2042f294`.

### Closed in session #22 (2026-04-26)

- [x] **SN-26-auto-controller** — `monitor_sync_bin.py` 4-part spec
  `NAME:READY:GO:NAMES`, per-participant name resolution, tuple compare
  on `(kind, name_string, type, value)`.  Backward compatible with
  legacy 3-part spec.  Three synthetic tests + one end-to-end with real
  scrip all PASS.  one4all @ `05ae400b`.

### Closed in session #20 (2026-04-26)

- [x] **SN-26-scrip-env-gate** — `SCRIP_FTRACE` / `SCRIP_TRACE` env vars in
  `src/runtime/x86/snobol4.c` `SNO_INIT_fn` auto-activate `kw_ftrace` /
  `kw_trace` at startup.  Set the env var, run an unmodified `.sno`, and
  every CALL/RETURN/VALUE event emits on the monitor wire — no
  `&FTRACE = 1` / `&TRACE = 1` in the source.  Verified in all three
  modes: `--ir-run`, `--sm-run`, `--jit-run` all emit identical
  text-format records via `mon_send` for a 6-stmt probe with one
  `DEFINE`/`SQUARE(7)` call.  This is the scrip side of "super
  automatic" sync tracing.  Smoke=7, Broker=49 green.  Tiny diff
  (~22 lines) just before the `Register numeric comparison builtins`
  block in `SNO_INIT_fn`.

### Active rung — SN-26-auto (binary catch-all, oracle bridges)

**Done-when:** `MONITOR_BIN=1 MONITOR_READY_PIPE=fifo MONITOR_GO_PIPE=go
MONITOR_NAMES_OUT=names.out SCRIP_TRACE=1 SCRIP_FTRACE=1 scrip --ir-run
beauty.sno < beauty.sno` produces a binary wire stream readable by
`monitor_sync_bin.py`, plus a names sidecar at `names.out`, with no
source modification of `beauty.sno`.  Same env vars on CSNOBOL4 +
SPITBOL produce comparable streams; controller resolves names per
participant and reports first divergence.

**Sub-rungs:**

- [x] **SN-26-scrip-env-gate** — landed this session (above).

- [x] **SN-26-auto-binary-scrip** — switch scrip's catch-all
  `comm_var`/`comm_call`/`comm_return` to emit binary records via
  `mon_send_bin` when `MONITOR_BIN=1` is set.  Names auto-interned
  into `g_bin_names` via a new `intern_name_bin(name, len)` helper
  that grows the table on demand.  At process exit (atexit handler),
  dump the table to `MONITOR_NAMES_OUT` and emit a final `MWK_END`
  record on the wire.  Landed this session (2026-04-26 session #21):
  forward decls for `mon_at_exit`, `g_names_out_path_ref`,
  `monitor_bin_mode`, and `intern_name_bin` placed at file scope
  immediately after `monitor_fd`/`monitor_ack_fd`/`monitor_ready` —
  this is the fix for session #20's build failure where the same
  symbols had been declared `extern` inside `SNO_INIT_fn` and so
  weren't visible to the compiler when the body of `mon_at_exit`
  was reached.  Smoke=7, Broker=49 green.  Validated end-to-end via
  `scripts/test_smoke_sn26_auto_binary.sh`: 14 records emitted
  (VALUE×11 + CALL×1 + RETURN×1 + END×1) for a 6-statement probe
  with one `DEFINE`/`SQR(7)` call, names sidecar lists 7 names
  (`a`,`b`,`c`,`SQR`,`x`,`f`,`d`).  No source modification —
  `MONITOR_BIN=1 SCRIP_TRACE=1 SCRIP_FTRACE=1` env vars only.

  Notable side-observation: comm_var fires VALUE records on local-arg
  unbinding too, so the wire shows `x → 7 → NULL` and `f → NULL → NULL`
  bracketing each call — useful telemetry for sub-h2 forensics later
  (the local-arg push/pop traffic is exactly the NM_CALL ordering work
  that diverges).

- [x] **SN-26-auto-controller** — `monitor_sync_bin.py` now accepts
  per-participant names sidecars via the `NAME:READY:GO:NAMES` 4-part
  spec.  Comparison tuple flipped from `(kind, name_id, type, value)` to
  `(kind, name_string, type, value)` — participants that assign different
  ids to the same logical name now agree.  Sidecars are loaded at startup
  and lazily re-read when divergences appear or on partial-EOF (the
  participant's atexit handler may write the sidecar after the controller
  opens the pipe).  Legacy 3-part shape (`NAMES_FILE NAME:READY:GO ...`)
  detected by colon-presence in `argv[1]` and kept working unchanged so
  existing harnesses still run until SN-26-auto-harness rewrites them.
  Validated three ways: synthetic 2-participant test with intentionally
  misaligned id maps (rc=0, names resolve), synthetic value-divergence
  test (rc=1 at correct step), legacy compat test (rc=0).  End-to-end
  with real scrip + `MONITOR_BIN=1` + the existing
  `test_smoke_sn26_auto_binary.sh` probe (DEFINE+SQR(7), 14 records,
  7-name sidecar): controller consumes the wire, sees MWK_END, exits 0.
  Smoke=7, Broker=49 green.

- [x] **SN-26-auto-harness** — `scripts/test_monitor_3way_sync_step_auto.sh`
  written.  No inject step.  Each participant gets its own FIFO pair
  + `MONITOR_NAMES_OUT` sidecar.  Controller called with the new 4-part
  `NAME:READY:GO:NAMES` spec (one entry per participant).  scrip is
  always launched; CSN/SPL are launched only when oracle bridges land.
  `SCRIP_ONLY=1` env var activates single-participant mode, useful for
  validating the auto path while CSN/SPL bridges (SN-26-csn-bridge,
  SN-26-spl-bridge) are pending.  Default mode (3-way) fails fast with
  a pointer to `SCRIP_ONLY=1` when the oracles aren't built.
  Validated: `SCRIP_ONLY=1 bash test_monitor_3way_sync_step_auto.sh
  /tmp/auto_probe.sno` (DEFINE+SQR(7) probe) → controller consumes 14
  records, hits END, rc=0, 7-name sidecar written.

- [ ] **SN-26-csn-bridge** — patch `csnobol4/v311.sil` at the five
  trace fire-points identified in session #19's Goal-file scout
  (lines 2641–2647 INIT1/STNO, 3516–3520 SJSRV2/VALUE, 4471–4478
  DEFF18/CALL, 4500–4507 DEFF20/RETURN; FAIL trap at 2662–2666 is
  out-of-scope) to call new `XCALLC monitor_emit_*` functions.  Add a
  shared `monitor_ipc_runtime.c` (next to `monitor_ipc_bin_csn.c` but
  loaded statically into the runtime, not as a `.so`) that opens
  `MONITOR_READY_PIPE` / `MONITOR_GO_PIPE` on first emit, marshalls
  CSNOBOL4-internal type tags → `MWT_*`, and writes the binary record
  + reads ack.  Catch-all gate: emit when `kw_trace > 0` /
  `kw_ftrace > 0` (CSNOBOL4-side counters), independent of any
  per-name `LOCAPT`/`LOCAPV`.  Build path:
  `make Makefile2 && make -f Makefile2 xsnobol4`.

- [ ] **SN-26-spl-bridge** — same shape for SPITBOL `sbl.min`.  Trace
  fire-points to identify next session: search around `trace`,
  `fentr` (sites at 15602, 15705, 15707), function-return at 16353,
  and the `sjsr`-equivalent for value assignment (needs grep).  Add
  `XCALLC monitor_emit_*` calls (or `.if` blocks gated on a build
  flag).  Build path: `make bootsbl && make BASEBOL=./bootsbl sbl &&
  make bininst`, plus `bootstrap/sbl.asm` regen per RULES.md SN-30g.

**Architecture note (one paragraph).**  The "super automatic" model
has two halves.  *Half one (scrip side, SN-26-scrip-env-gate, done):*
env vars set the keyword counters at startup so the user's `.sno`
runs unmodified.  *Half two (cross-runtime, SN-26-auto-* + bridges):*
each runtime emits `monitor_wire.h`-format binary records on every
trace event when `MONITOR_BIN=1` is set, auto-interning names into
its own per-participant sidecar.  The controller post-resolves
name_ids to strings via the sidecars and compares string tuples.
This decouples participants completely — they no longer need a
shared, pre-baked names file (which the source-injection era required).

**Gate after each sub-rung:** Smoke=7, Broker=49.

**Dependencies:** SN-26-scrip-env-gate done; rest of SN-26-auto blocks
on a build-then-test cycle that didn't fit in session #20's budget.

**3-way binary harness:** broken pending oracle-side instrumentation
(SN-26-csn-bridge / SN-26-spl-bridge) and harness-script rewrite
(SN-26-harness-rewrite).  Pre-#19 design loaded the .so via SNOBOL4
LOAD() calls injected by Python; that violated the new rule.

### Active rung — drive SN-26c-parseerr-h sub-h2 via 3-way (session #19)

#### Pivot in session #19 (this session)

The 3-way binary harness as designed in sessions #16–#18 had a
Python-driven instrumentation layer (`inject_traces_bin.py`) that
rewrote each `.sno` source to insert per-name `TRACE()` registrations
and a `LOAD()`ed dispatcher.  Lon's direction in this session: **no
source preprocessing of any kind**, in any language.  The user's
`.sno` runs unmodified.  Instrumentation lives in the C runtime,
triggered by env vars and `&FTRACE`/`&TRACE` catch-alls.  See
`RULES.md → Sync-step monitor — keyword catch-alls only, no source
preprocessing`.

**Removed** in this session: `scripts/monitor/inject_traces.py`,
`scripts/monitor/inject_traces_bin.py`.  The controllers
(`monitor_sync.py`, `monitor_sync_bin.py`) and the C-side IPC
libraries **remain** — they are the cross-process comparison engine.

**scrip catch-all keyword wiring** landed in `runtime/x86/snobol4.{c,h}`:
- `kw_trace` global added next to existing `kw_ftrace`.
- `&TRACE` wired into the keyword get/set/ptr tables.
- `comm_var` now emits a VALUE wire record when `kw_trace > 0`,
  bypassing the per-name `trace_registered()` filter.
- `comm_call`/`comm_return` already emitted CALL/RETURN when
  `kw_ftrace > 0`; that wiring needed no change.

scrip is the only participant that conforms to the rule today — it
reads `MONITOR_READY_PIPE` at startup (`SNO_INIT_fn` line 1729) and
its `comm_*` C functions write the binary record format directly to
`monitor_fd`.  Smoke=7, Broker=49 still green.

#### Oracle-side gap — concrete instrumentation map (session #19 scout)

Both SPITBOL and CSNOBOL4 currently require SNOBOL4-level `LOAD()`
calls in the user's source to attach the IPC `.so`.  That's the
source modification the rule bans.  The clean fix is to **patch each
oracle's source-of-truth** so:

1. At process startup, the runtime reads `MONITOR_READY_PIPE` /
   `MONITOR_GO_PIPE` env vars and opens the FIFO — same shape as
   scrip's `SNO_INIT_fn`.
2. Existing trace fire-points emit a binary record on the wire,
   gated on `&FTRACE > 0` / `&TRACE > 0` in catch-all mode (no
   per-name `LOCAPT`/`LOCAPV` lookup required).
3. Four event kinds: VALUE, LABEL/STNO, CALL, RETURN.

##### CSNOBOL4 — `v311.sil`  (12 405 lines, regenerated via `genc.sno`)

Source-of-truth fire-points already exist in the SIL, gated on
`&TRACE` (the `TRAPCL` constant) and using `XCALLC` to call C:

| Event kind | Site (label / line)         | Currently fires | Catch-all patch shape                                      |
|------------|-----------------------------|-----------------|------------------------------------------------------------|
| LABEL/STNO | `INIT1` area, lines 2641–2647 | `STNOKY` keyword trace via `LOCAPT TKEYL,STNOKY` + `RCALL TRPHND` | Add `XCALLC monitor_emit_stno,(EXNOCL)` immediately after the existing TRPHND, gated on `kw_trace > 0` only |
| FAIL       | `INTRP0`, lines 2662–2666     | `FALKY` keyword trace                                          | (out of scope; not one of the four kinds Lon listed)       |
| VALUE      | `SJSRV2`, lines 3516–3520     | `LOCAPT ATPTR,TVALL,WPTR` per-name trace                        | Add `XCALLC monitor_emit_value,(WPTR,ZPTR)` — variable name + value descriptor |
| CALL       | `DEFF18`, lines 4471–4478     | `LOCAPT ATPTR,TFENTL,ATPTR` per-name trace                      | Add `XCALLC monitor_emit_call,(ATPTR)` — function name descriptor |
| RETURN     | `DEFF20`, lines 4500–4507     | `LOCAPT ATPTR,TFEXTL,ATPTR` per-name trace                      | Add `XCALLC monitor_emit_return,(ATPTR,RETPCL)` — function name + return value |

Build path:
```bash
cd /home/claude/csnobol4
# edit v311.sil — patch the five sites above
make Makefile2
make -f Makefile2 xsnobol4   # NOT top-level make xsnobol4 (that tries to bootstrap)
```
The new C functions (`monitor_emit_*`) live in a new file
`monitor_ipc_runtime.c` linked into the runtime alongside `data.c`,
`isnobol4.c`, etc.  They open the FIFO once on first call (lazy init
gated on the env var), then write `monitor_wire.h`-format records
followed by a 1-byte ack read on the go FIFO.

##### SPITBOL x64 — `sbl.min`  (29 310 lines)

`sbl.min` uses different idiom (MINIMAL macro language compiled to
x86_64 asm via the in-tree assembler).  Trace fire-points need
identification next session:
- Function entry trace: search around `trace` and `fentr` (sites at
  lines 15602, 15705, 15707 already known to call the trace handler).
- Function return trace: site at line 16353 (`* here for print trace
  of function return`).
- Value-assignment trace: needs grep for `sjsr` equivalent and the
  &TRACE check.
- STNO trace: needs identification.

Build path:
```bash
cd /home/claude/x64
# edit sbl.min — patch the four trace sites
rm -f bin/sbl
make bootsbl
make BASEBOL=./bootsbl sbl
make bininst
```
SPITBOL also has the `bootstrap/sbl.asm` regen path documented in
RULES.md SN-30g — needed for fresh-clone builds.

##### Shared C-side runtime (new file)

`monitor_ipc_runtime.c` — single file, included in both runtime
builds.  Provides:
```c
void monitor_emit_value (const char *name, void *descr);
void monitor_emit_call  (const char *fname);
void monitor_emit_return(const char *fname, void *retval);
void monitor_emit_stno  (long stno);
```
Each function:
1. On first call, reads `MONITOR_READY_PIPE` env var; opens FIFO; sets
   static `monitor_fd`; reads `MONITOR_GO_PIPE`; reads
   `MONITOR_NAMES_FILE` to populate name → name_id map.
2. Looks up name in name_id map (or assigns a new id if extending the
   map dynamically — TBD whether we keep static names file or move to
   variable-length name records).
3. Marshalls the descriptor's type tag → `MWT_*` and value bytes per
   `monitor_wire.h` rules.
4. `writev()` the 13-byte header + value bytes to FIFO.
5. `read()` 1-byte ack from go FIFO; if 'S' or EOF, exit cleanly.

The dialect-to-MWT mapping is the only dialect-specific glue: each
oracle's internal type tag is a different value, so the function
needs ABI-specific glue (one set of `monitor_emit_*` per oracle, or
one shared file with a small dialect-detect at compile time).

##### Sub-rung sequence (revised)

- [x] **SN-26-csn-bridge-a** — Wrote `monitor_ipc_runtime.c` (412 lines,
  self-contained, no csnobol4 internal header deps).  Three public
  C entry points (`monitor_emit_value` / `_call` / `_return`) ready
  for XCALLC use.  Lazy FIFO open from `MONITOR_READY_PIPE` /
  `MONITOR_GO_PIPE`; auto-interns names; dumps sidecar to
  `MONITOR_NAMES_OUT` and emits MWK_END at process exit; silent
  no-op when env vars unset.  Linked into xsnobol4 via Makefile2.m4
  edit (source of truth, regenerated Makefile2 committed alongside
  per RULES.md).  Validated end-to-end via standalone harness:
  6 wire records (3xVALUE STRING/INTEGER/REAL + CALL + RETURN +
  END), 4 names in sidecar, all decode byte-equal on controller side.
  csnobol4 @ `c1843eb`.  one4all @ `3f6bdbb3` (smoke script + reader).
  Smoke=7, Broker=49 unchanged (runtime symbol unused until SIL XCALLC
  sites land in -a-xcallc / -b).
- [x] **SN-26-csn-bridge-a-xcallc** — Wired `XCALLC monitor_emit_value,(XPTR,YPTR)`
  at `ASGNVV` in `v311.sil` (the central simple-assignment store, line 5938
  region of the `ASGN PROC ,` block — `X = Y`).  End-to-end FIFO probe with
  `x = 'hello' / END` produces exactly one VALUE record on the wire: `kind=VALUE
  name_id=0 STRING(5)=b'hello'` followed by `MWK_END`, sidecar `id=0: X`.
  SIL→C boundary proven.  csnobol4 @ session #25 commit (this rung).
  Smoke=7, Broker=49, csn-bridge smoke=1 all green.

  **Build-path footgun discovered (worth a follow-up rung).**  The Goal file's
  plan assumed `edit v311.sil → regenerate snobol4.c/isnobol4.c → build` would
  work.  It does not on current HEAD (`c1843eb`):
  1. **IM-15b (commit `b3aeb9f`)** is a hand-edit on the generated `snobol4.c`
     (typedef + 3 externs at top, hook firing site at `D_A(EXNOCL)++`).  Top-level
     `make snobol4.c` wipes both blocks.
  2. **`genc.sno` regenerates a broken `isnobol4.c`** on this HEAD: the tsort
     inlining decisions promote `FNCP`/`FNCA..FNCD` from top-level C functions
     to mere labels, but `data_init.c` references `FNCP` as a function symbol
     via `(int_t)(FNCP)`.  Result: `undefined reference to FNCP` at link time.
     Reproduces with no XCALLC edit at all — pre-existing.

  **Pragmatic compromise shipped:** treat `v311.sil` as documentation-source-of-
  truth for the XCALLC, and apply the equivalent C-level edit directly to
  `snobol4.c` and `isnobol4.c` at `L_ASGNVV` (with explanatory comment in
  `snobol4.c`).  Mirrors the precedent set by IM-15b.  This is what regen
  *would* produce if regen worked.

  **Suggested follow-up rung** (not opened): `SN-26-csn-regen-fix` — diagnose
  why `genc.sno` regen drops FNCP/FNCA..FNCD top-level definitions, fix
  `with`/`procs` inlining config, regenerate cleanly once, commit the fresh
  baseline.  Then future XCALLC additions can follow the proper edit-SIL-and-
  regenerate workflow without manual restoration.

- [x] **SN-26-csn-bridge-b** — Patched the four trace fire-points in
  `v311.sil` to emit unconditionally on the wire when env vars are
  set: `XCALLC monitor_emit_value,(WPTR,ZPTR)` at SJSRV1 (the
  pattern-substitute store, e.g. `S 'world' = 'there'`), `XCALLC
  monitor_emit_call,(ATPTR)` at DEFF18 (function entry), `XCALLC
  monitor_emit_return,(ATPTR,RETPCL)` at DEFF20 (function exit).
  Hand-applied equivalent C edits to `snobol4.c` and `isnobol4.c` per
  the SN-26-csn-bridge-a-xcallc precedent (genc.sno regen still
  drops FNCP top-level — `SN-26-csn-regen-fix` rung still owed).

  Catch-all gating: nothing in the SIL — the runtime's
  `monitor_init()` short-circuit handles "env vars unset" cleanly
  (returns 0; no FIFO open; emit is a no-op).  No new field on the
  scrip-style `kw_trace` keyword in CSNOBOL4; instrumentation is
  unconditional and free when monitoring is off.

  RETPCL semantics clarified in `monitor_ipc_runtime.c` header
  comment for `monitor_emit_return`: SIL passes &RTNTYPE (a NAME
  pointing to RETURN/NRETURN/FRETURN), not the function's result
  value.  The actual result is delivered via the preceding VALUE
  record on the function-name variable (e.g. `SQR = N*N` inside
  the body fires `monitor_emit_value(SQR, INTEGER(49))` at
  ASGNVV before the RETURN record carrying STRING("RETURN")).
  Wire consumers should treat the RETURN payload as exit-type, not
  result.

  End-to-end probe (`corpus/programs/snobol4/demo/csn_bridge_b/probe_b.sno`):
  ```
  #0 VALUE  S    STRING(11)='hello world'   (ASGNVV)
  #1 VALUE  S    STRING(11)='hello there'   (SJSRV1)
  #2 CALL   SQR                             (DEFF18)
  #3 VALUE  SQR  INTEGER(49)                (ASGNVV inside body)
  #4 RETURN SQR  STRING(6)='RETURN'         (DEFF20: &RTNTYPE)
  #5 VALUE  N    INTEGER(49)                (ASGNVV)
  #6 END
  ```
  Smoke=7, Broker=49, csn-bridge-a=1, csn-bridge-b=1 all green.
  Permanent gate: `bash scripts/test_smoke_sn26_csn_bridge_b.sh`.

- [x] **SN-26-spl-bridge-a** — Identified trace fire-points in `sbl.min`
  (29 310 lines).  Calling convention is **`sysxx`-family externs**, NOT
  XCALLC: each external is declared `sysxx exp N` in `sbl.min`, has a
  thunk in `int.asm` (`%macro syscall %1,%2`), and is implemented as
  `int zysxx(void)` in `osint/sysxx.c`.  Args reach the C function
  through `reg_xr` / `reg_xl` / `reg_wa` / `reg_wb` / `reg_wc` / `reg_xs`
  globals (saved by `syscall_init`).  Wrapper macros `XR(t)`, `WA(t)`,
  `XS(t)` etc. live in `osint/osint.h`.

  | Event | sbl.min line | Site label | Args at call site |
  |-------|------|------|-------------------|
  | VALUE (universal) | 11043 | `b_vrs ent` (untrapped vrsto) | `xr` → vrsto field of vrblk; `(xs)` → value-block ptr |
  | VALUE (trapped path; alt) | 11095 | `b_vrv ent` | already trace-aware via `asign` line 17597; not used in catch-all model |
  | CALL  | 10850 | `bpf09` (function-call gate) | `xl` → pfblk; `pfctr(xl)` is trace trblk |
  | RETURN | 16337 | retrn body (function-return gate) | `xr` → pfblk; `kvrtn` (& via `wa`) → "RETURN"/"FRETURN"/"NRETURN" |
  | STNO  | 16521 / 16543 | `stmgo` body / `stgo3` | `kvstn ← cdstm(xr)` — advisory only |

  Wire protocol identical to `csnobol4/monitor_ipc_runtime.c` so a
  single controller can compare the two oracles byte-for-byte.

  SPITBOL value-block discrimination: read first word of value pointer
  and compare to `TYPE_SCL` / `TYPE_ICL` / `TYPE_RCL` from `osint.h`.
  Other type tags (nmblk/ptblk/atblk/tbblk/cdblk/efblk) lack public
  externs in `osint.h` today — they fall through to MWT_UNKNOWN; the
  wire still carries the kind+name so divergence detection remains
  meaningful.

  vrblk name extraction: `vr->vrlen > 0` → name in `vr->vrchs[]`;
  `vrlen == 0` → system variable, name in svblk via vrsvp (skipped
  for now; user-written code is the catch-all target).

  Build path:
  ```bash
  cd /home/claude/x64
  # 1. Add osint/monitor_ipc_runtime.c (zysmv/zysmc/zysmr).
  # 2. Add 3 sysxx thunks to int.asm (sysmv/sysmc/sysmr).
  # 3. Add 3 `<n> exp N` declarations + jsr fire-points to sbl.min.
  # 4. Add monitor_ipc_runtime.o to osint Makefile OBJS.
  # 5. Rebuild:
  rm -f bin/sbl
  make bootsbl
  make BASEBOL=./bootsbl sbl
  make bininst
  # 6. Regen bootstrap/sbl.asm so fresh clones can build (RULES.md SN-30g):
  make makeboot
  ```

- [x] **SN-26-spl-bridge-b** — Patched sbl.min/int.asm/osint with three
  new MINIMAL externs `sysmv`/`sysmc`/`sysmr` and their C
  implementations (`zysmv`/`zysmc`/`zysmr`) in
  `osint/monitor_ipc_runtime.c`.  Fire-points landed:
  - `b_vrs` (line 11077, after `ent`): `jsr sysmv` before the actual
    store, so wire records reflect pre-write state.
  - `bpf09` predecessor (line ~10867, immediately before
    `mov wa,kvtra` of the existing trace-trblk gate): `mov wb,xl;
    mov xr,pfvbl(xl); jsr sysmc; mov xl,wb` — saves/restores xl, leaves
    xr ready for the C side.
  - retrn body (line 16363 region, after `mov r_cod,wc`): `mov -(xs),xr;
    mov -(xs),wa; mov xr,pfvbl(xr); jsr sysmr; mov wa,(xs)+; mov xr,(xs)+`
    — saves/restores xr+wa around the call.

  Catch-all gating: nothing in the SIL.  The runtime's `monitor_init()`
  short-circuit handles "env vars unset" cleanly (returns 0; FIFO
  never opened; emits become no-ops).  No new field on a SPITBOL keyword;
  instrumentation is unconditional and cheap when monitoring is off
  (verified: SN-30 invariant `beauty.sno < beauty.sno` md5 still
  `408fc788ca2ef425fc1f87e26d45a7a5`).

  End-to-end probe `corpus/programs/snobol4/demo/spl_bridge/probe.sno`
  produces 6 wire records:
  ```
  #0 VALUE  S    STRING(11)='hello world'   (b_vrs)
  #1 CALL   SQR                             (bpf09)
  #2 VALUE  SQR  INTEGER(49)                (b_vrs inside body)
  #3 RETURN SQR  STRING(6)='RETURN'         (retrn: &RTNTYPE)
  #4 VALUE  N    INTEGER(49)                (b_vrs)
  #5 END
  ```
  Smoke=7, Broker=49, csn-bridge-b=1, spl-bridge=1 all green.
  Permanent gate: `bash scripts/test_smoke_sn26_spl_bridge.sh`.

  bootstrap files (`bootstrap/sbl.asm`, `bootstrap/err.asm`,
  `bootstrap/sbl.lex`) regenerated via `make makeboot` so a fresh clone
  can build SN-26-spl-bridge-b sbl from scratch via
  `make bootsbl && make BASEBOL=./bootsbl sbl && make bininst`.

  **Cross-oracle asymmetry observed (low priority follow-up):**
  CSNOBOL4's SJSRV1 site fires monitor_emit_value for the
  pattern-substitute store `S 'world' = 'there'`, but SPITBOL's
  pattern-match path doesn't traverse `b_vrs` — substring replacement
  writes via a different path inside `bpat`/`assn`.  The SPITBOL probe
  drops that line; the controller will see one fewer record than the
  CSNOBOL4 probe.  Tracked as **SN-26-spl-bridge-c** (deferred): find
  the SPITBOL pattern-substitute store-back point (likely inside
  `match` epilog around the `pmval` flag), insert a fourth fire-point
  so the two oracles emit identical wires for identical programs.

- [ ] **SN-26-spl-bridge-c** — Pattern-substitute store-back fire-point
  for SPITBOL.  Recover the missing record from the CSNOBOL4-vs-SPITBOL
  asymmetry above.  Low priority; deferred.
- [x] **SN-26-harness-rewrite** (session #28, 2026-04-27) — Generalized
  `test_monitor_3way_sync_step_auto.sh` with a `PARTICIPANTS` env var
  accepting any subset of `{csn, spl, scr}` (first entry is the oracle).
  Rewrote the three 2-way scripts as thin 18-line wrappers around the
  auto harness:
    * `test_monitor_2way_sync_step.sh` → `PARTICIPANTS="csn spl"`
    * `test_monitor_2way_sync_step_bin.sh` → `PARTICIPANTS="csn spl"`
    * `test_monitor_2way_spitbol_vs_ir.sh` → `PARTICIPANTS="spl scr"`
  Deleted five harnesses targeting retired pipelines:
    * `test_monitor_3way.sh` (ASM backend retired commit `2c760e3d`)
    * `test_monitor_3way_sync_step_bin.sh` (superseded by `_auto.sh`)
    * `test_monitor_5way_ipc.sh` (ASM/JVM/NET retired)
    * `test_monitor_sync_step.sh` (ASM/JVM/NET retired)
    * `test_monitor_precheck_prerequisites.sh` (precheck for retired pipeline)
  Net diff `scripts/`: −1078 lines.  No external `.sh`/`.md`/`Makefile`
  references to the deleted scripts in `one4all/`.  `SCRIP_ONLY=1`
  back-compat preserved as alias for `PARTICIPANTS="scr"`.  Validated
  in 7 PARTICIPANTS configurations on a simple `x = 'hello' / END`
  probe (rc=0 each).  Smoke=7, Broker=49, csn-bridge-a=1, csn-bridge-b=1,
  spl-bridge=1 all green.

The minimum unit of progress is **SN-26-csn-bridge-a-xcallc** — a single
runnable XCALLC from a test site, proving the runtime can open the
FIFO and emit one record.  Build it on the smaller, easier oracle
first; SPITBOL follows the same pattern.

#### Divergence-point workflow (RULES.md)

When the harness reports a divergence, read **only** the last-agree
record + the first-disagree record.  The bug is in the runtime work
between those two timestamps.  Do not paste long trace dumps into
chat.

#### Sub-h2 reproducer (sub-h2 still open)

Confirmed in this session via plain stdout diff:

```bash
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
printf "        x = 'hello'\nEND\n" > /tmp/simple.sno

# Both oracles produce the same correct output:
SETL4PATH=".:/home/claude/corpus/programs/include" \
    /home/claude/x64/bin/sbl -bf $BEAUTY/beauty.sno < /tmp/simple.sno
# →                   x              =  'hello'
# → END

# scrip drops the LHS:
SNO_LIB=/home/claude/corpus/programs/include \
    /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno < /tmp/simple.sno
# →                                  'hello'
# → END
```

The "Parse Error" output sometimes seen above this is beauty's own
mainErr1 branch firing — beauty detects its parse state is broken
(c[1..2] null in pp_snoStmt) and prints "Parse Error" before the
broken stmt.

#### Next session work order (session #20)

1. Standard setup chain.
2. Land **SN-26-scrip-env-gate**: `SCRIP_FTRACE` / `SCRIP_TRACE` env
   vars in `runtime/x86/snobol4.c`'s `SNO_INIT_fn`.  ~5 lines.
3. Confirm `MONITOR_READY_PIPE=fifo SCRIP_FTRACE=N` produces wire
   records on `fifo` from beauty.sno without any source modification.
4. Triage the 9 harness shell scripts: rewrite to remove the inject
   step.  At minimum, rewrite `test_monitor_3way_sync_step_bin.sh`
   for the no-preprocessing model — even if scrip is the only
   participant emitting events until SN-26-oracle-monitor-bridge
   lands, the harness shape should be correct.
5. With scrip emitting against a one-time captured SPITBOL reference,
   apply the divergence-point workflow to drive sub-h2 to root cause.

### Closed in session #19

- [x] **SN-26-keyword-catchall** — `kw_trace` global + `&TRACE` keyword
  + `comm_var` catch-all branch landed in `runtime/x86/snobol4.{c,h}`.
  Smoke=7, Broker=49 green.  Source rewriters
  (`inject_traces.py`, `inject_traces_bin.py`) deleted from
  `scripts/monitor/`.

### Active rung — binary-protocol sync-step monitor (session #17)

Session #16 implemented the binary-protocol scaffolding but was blocked
by a SPITBOL/CSNOBOL4 type-check at LOAD prototype level on non-string
values.  Session #17 closed that blocker.

#### Investigation findings (session #17)

Read SPITBOL `sbl.min:14681-14770` and CSNOBOL4 `v311.sil:4564-4636`:
both LOAD prototype parsers behave identically — they recognize a small
fixed set of type-name tokens (`STRING`, `INTEGER`, `REAL`, `FILE`)
and stamp each formal-arg slot with that code.  Unrecognized tokens
fall through to a "no convert" path (code 0) — `zer wb` at sbl.min:14755,
`PUSH ZEROCL` at v311.sil:4628.

The type check that produces ERROR 039 / Error 1 happens at *call*
time when the runtime tries to convert each actual arg according to
the formal slot's stamped code.  STRING-stamped slot + non-string
actual → error.  No-convert slot (code 0) → raw block-pointer
pass-through.

Cannot use no-convert path on SPITBOL alone, however: `syslinux.c:188`
overwrites `cargs[i].v = LDESCR_INT` for every default-branch arg,
losing the type tag the C side relies on.  Therefore typed entry
points are the right fix.

#### What was implemented (session #17)

Eight new LOAD-able entry points, four for VALUE and four for RETURN,
each declaring its second arg with the matching prototype token so the
runtime accepts the call.  Wrapper preamble in `inject_traces_bin.py`
dispatches via `DATATYPE($N)` against runtime-derived tokens
(`MON_DT_S_ = DATATYPE('')`, etc.) — portable across CSNOBOL4
UPPERCASE and SPITBOL x64 lowercase DATATYPE conventions.

| Channel | Prototype | Wire emit |
|---------|-----------|-----------|
| `MON_PUT_S_VALUE` / `MON_PUT_S_RETURN` | `(STRING,STRING)INTEGER` | type=STRING, raw bytes |
| `MON_PUT_I_VALUE` / `MON_PUT_I_RETURN` | `(STRING,INTEGER)INTEGER` | type=INTEGER, 8 LE bytes |
| `MON_PUT_R_VALUE` / `MON_PUT_R_RETURN` | `(STRING,REAL)INTEGER` | type=REAL, 8 LE bytes |
| `MON_PUT_O_VALUE` / `MON_PUT_O_RETURN` | `(STRING,STRING)INTEGER` | type from name string, len=0 |

SPITBOL REAL handling: SPITBOL's syslinux.c routes REAL through the
default branch, stuffing the rcblk pointer into `args[1].a.i` (NOT the
marshalled double in `.a.f`).  C side reads the double from
`blk + sizeof(word)` per the rcblk struct layout
(`x64/osint/spitblks.h:115`).  Both runtimes now agree on REAL values.

Legacy `MON_PUT_VALUE` / `MON_PUT_RETURN` retained for direct C-side
test programs but no longer LOAD()ed by the injected preamble.

#### Validation (session #17)

| Probe | Events | Result |
|-------|-------:|--------|
| `x='hello' / y=42 / END` | 3 | ✅ all byte-equal, clean EOF |
| Mixed: STRING/INTEGER/REAL/ARRAY/TABLE/PATTERN/CODE | 8 | ✅ all byte-equal |
| Function CALL/RETURN (`SQUARE(7)`, `GREET('world')`) | 5 | ✅ all byte-equal |
| beauty.sno with 5-line input | 162 | ✅ all byte-equal |
| `beauty.sno < beauty.sno` (full self-host) | 162 (then DIVERGE) | First real cross-oracle divergence — see below |

`beauty.sno < beauty.sno` ran 162 events deep before the first real
CSNOBOL4-vs-SPITBOL semantic divergence:
```
[ctrl] DIVERGE step 162
  csn: VALUE PushCounter = STRING(5)='dummy'
  spl: VALUE PushCounter = NAME(0)=''
```
This is exactly what the binary protocol is designed to expose.  The
divergence relates to the NRETURN convention (RULES.md "NRETURN
functions — dot-star calls": return `.dummy` as a NAME).  CSNOBOL4 sees
the STRING value of `dummy`; SPITBOL sees the NAME descriptor.

This divergence is **not** SN-26c-parseerr-h sub-h2 (which is a
scrip-vs-oracle bug).  It's an oracle-vs-oracle representation
difference around NRETURN.  Tracked as a new sub-rung below.

#### Sub-rungs

- [x] **SN-26-binmon-typed (session #17, this commit)** — typed entry
  points + DATATYPE dispatch landed.  ARRAY/TABLE/PATTERN/CODE/REAL
  all flow through binary harness without runtime type-check failures.
- [ ] **SN-26-binmon-nreturn-divergence** — oracle-vs-oracle divergence
  on `dummy` (STRING vs NAME) at step 162 of beauty self-host.  Likely
  rooted in how each runtime represents the `.dummy` NRETURN value when
  the dot-star call happens.  Low priority — exposes a real semantic
  gap but does not gate scrip work.  Investigate by adding an EXCLUDE
  for `dummy` and `PushCounter` and seeing how far the run gets, OR
  understand the SIL-level convention for NRETURN return values.
- [x] **SN-26-binmon-3way (session #18, 2026-04-26)** — scrip --ir-run
  wired in as third participant in the binary harness.  All three
  participants run the SAME instrumented `.sno` source, hitting the
  source-level `MON_OPEN(...)` gate at the same statement number —
  startup synchronization is automatic.  Architecture follows the
  historic `run_monitor_3way.sh` pattern (commit `a4a27ab7`) per
  `MONITOR-BINARY-DESIGN.md` (commit `669b3b4`):
    * scrip pre-registers `MON_OPEN`, `MON_PUT_S/I/R/O_VALUE`,
      `MON_PUT_S/I/R/O_RETURN`, `MON_PUT_CALL`, `MON_CLOSE` as C
      builtins (`_b_MON_*` in `src/runtime/x86/snobol4.c`).
    * scrip exposes a `LOAD` stub that succeeds for any `MON_*`
      prototype so the preamble's LOAD-chain doesn't take MON_NOOP_.
    * Harness sets `MONITOR_SO=builtin` (sentinel non-empty string)
      so the preamble's `IDENT(MON_SO_)` doesn't short-circuit.
    * scrip's `_TRACE_` honors the 4-arg form `TRACE(var,type,tag,fn)`:
      registers a callback that fires via `APPLY_fn` on every assignment.
      Re-entry guard prevents recursion when the callback itself assigns.
    * `comm_var` moved post-commit in `NV_SET_fn` so `$N` lookups inside
      the callback see the new value.  `set_and_trace` updated to avoid
      double-emission (NV_SET_fn already fires for normal-store path).
    * `interp.c` E_VAR fallback to `APPLY_fn` for zero-arg builtins now
      treats FAIL returns as "unset variable" (NULVCL) rather than
      propagating the FAIL — matches CSNOBOL4 / SPITBOL semantics where
      bare unbound `VALUE` (and similar) is the empty string when used
      as a function arg, not a hard failure aborting the enclosing call.

  **Sanity probes (all PASS, byte-equal across CSN/SPL/scrip):**
    * probe1_basic — 3 steps (STRING + INTEGER)
    * probe2_mixed — 8 steps (STRING/INT/REAL/ARRAY/TABLE/PATTERN/CODE)
    * probe4_beauty5 — 6 steps (5-line beauty-style block)
    * probe5_arith — 9 steps (arithmetic, real division, str concat)

  **Beauty status:** `beauty.sno < beauty.sno` through 3-way harness now
  isolates a real scrip-vs-oracle divergence — scrip exits silently
  during beauty's pre-MON_OPEN include processing (`global.inc`,
  `is.inc`, etc.).  CSN and SPL both reach `VALUE ppStop = ARRAY` at
  step 1; scrip emits nothing and EOFs.  This is exactly the kind of
  divergence the 3-way harness was designed to surface — likely
  SN-26c-parseerr-h sub-h2 or a related parser/runtime gap.  Tracked as
  **SN-26c-parseerr-h sub-h2** (the active rung this work was driving
  toward).  Investigate by capturing scrip's preamble execution trace
  with `ONE4ALL_USERCALL_TRACE=1` and comparing to the oracles' MV
  callback timeline.

#### Next-session work order

1. Standard setup chain (`.github`, `one4all`, `corpus`, `csnobol4`,
   `x64` clones; install_system_packages.sh; build_scrip.sh;
   build_spitbol_oracle.sh; build_csnobol4_oracle.sh).
2. Build the binary-IPC libraries:
   `bash scripts/build_monitor_ipc_bin_libraries.sh`.
3. Sanity check the 2-way binary harness with the four probes:
   `probe_bin.sno` (string+int), mixed-types probe, function CALL/RETURN
   probe, beauty short-input.  All should hit clean EOF.
4. Investigate **SN-26-binmon-nreturn-divergence** OR jump to
   **SN-26-binmon-3way**.  3-way is the higher-value path — it directly
   surfaces sub-h2.
5. For 3-way: write `test_monitor_3way_sync_step_bin.sh` (template:
   the existing 2-way), add a third participant pipe set, and add
   binary-emit code to scrip's `mon_send` (or a new `mon_send_bin`).
   Per MONITOR-BINARY-DESIGN.md §5: scrip's runtime is C-internal, no
   LOAD ABI dance — just inspect the descriptor's `.v` tag and emit
   the matching wire record.

#### Notes

- **CALL/RETURN trace 4-arg form** does not invoke the callback in
  either oracle — only the dialect's built-in trace OUTPUT fires.
  Pre-existing limitation, both protocols affected equally.  Inserting
  explicit `MC(name,'')` calls at function entry/exit would track these
  but only matters once we hit a CALL/RETURN-only divergence.
- **Session #15 completed:** restored 2-way text-protocol harness as
  reference (`scripts/monitor/monitor_ipc_sync.c` + `inject_traces.py`
  + `monitor_sync.py` + `test_monitor_2way_sync_step.sh`); fixed
  `interp.c:953` E_ASSIGN trace hook bypassing `set_and_trace`.
  See commit `5ad12633`.
- **Session #17 finding for archive:** SPITBOL `sbl.min:14755` and
  CSNOBOL4 `v311.sil:4628`-style fall-through to "no convert"
  *would* allow non-string args to flow through if SPITBOL didn't
  also stamp `cargs[i].v = LDESCR_INT` in `syslinux.c:188`.  Patching
  syslinux.c to preserve the original block's type tag (read first
  word, compare to `b_scl`/`b_icl`/`b_rcl` / etc.) could enable a
  single polymorphic entry point — but only `b_scl`, `b_icl`, `b_rcl`,
  `b_xnt` are exported globals; ARRAY/TABLE/PATTERN/CODE/NAME aren't,
  so cross-translation-unit comparison is awkward.  Typed entry
  points are the cleaner fix and that is what shipped.

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
