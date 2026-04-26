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

## Active rung — SN-26c-parseerr (opened 2026-04-25, session #4)

### SN-26c-stmt637 — CLOSED 2026-04-25 (session #4)

**Root cause:** `lt_find` in `src/runtime/x86/sm_lower.c:84-90` used
`strcasecmp` for label-table lookup.  Under SN-31's case-sensitive
default (the policy for one4all's `.sno`/`.inc` ingress), this
collided distinct labels like `visitEnd` (lowercase, the end label
of the `visit(...)` SNOBOL function block) and `VisitEnd` (capital,
the double-function-trick partner of `visit`).  Both labels are
present in beauty.sno; the SM goto `:go visitEnd` from
`DEFINE('visit(x,fnc)i') :go visitEnd` was being resolved to
`VisitEnd`, sending SM control flow off into the wrong static
region.  IR's goto resolution at `interp.c:148` already used
`strcmp` (case-sensitive) ✓, so this was an SM-only bug.

**Diagnostic chain (the work that pinned the casing bug):**

The previously-suspected "stmt-counting drift" hypothesis was
wrong.  Both IR and SM emit/dispatch exactly one `comm_stno`
boundary per source `STMT_t` (single emit site at
`sm_lower.c:929`), and the static-counter `g_sm_stno` accumulating
across monitor reruns (1+2+...+637 ≈ 203,203) is by design, not
a bug.  The real divergence was found by:

1. `--dump-sm` to enumerate every SM_STNO opcode's static PC
   (1102 SM_STNOs, one per STMT_t, in source order).
2. Build pc → static-stmt-index map.
3. From the env-gated `SMSTEP %d sm_stno=%d pc=%d` trace
   (committed `4d12a99363` in session #3), decode the **printed**
   pc back to (pc-1) — the print fires after `st->pc++`, so the
   actual SM_STNO that fired was at pc-1 — and look up its
   static stmt index.
4. From the IRSTEP trace, use the printed `label=X` field plus
   a label→static-stmt-index map (built from `--dump-ir`) to
   identify the static stmt IR was dispatching as its Nth.
5. Compare the two sequences, step by step.

The first divergence appeared at step 631:
* SM step 631 → SM_STNO at pc=3745 → static stmt 382 = `VisitEnd`
* IR step 631 → label=`visitEnd` → static stmt 1052
Both step 630 dispatched static stmt 1047, which is
`DEFINE('visit(x,fnc)i') :go visitEnd`.  The same `:go visitEnd`
in the same source statement resolved to two different targets
under the two executors — proof that the bug was in label
resolution, not in counting.

**Fix landed in this session:**
```c
/* src/runtime/x86/sm_lower.c:84-90 */
static int lt_find(const LabelTable *lt, const char *name)
{
    /* SN-26c-stmt637: case-SENSITIVE label compare per SN-31 ... */
    for (int i = 0; i < lt->nlabels; i++)
        if (strcmp(lt->labels[i].name, name) == 0)
            return lt->labels[i].instr_idx;
    return -1;
}
```

One-character substantive change (`strcasecmp` → `strcmp`) plus
explanatory comment.  No other call site of `strcasecmp` in
`sm_lower.c` — the only label-resolution path.

**Verification (session #4):**
* `bash scripts/test_smoke_snobol4.sh` → **PASS=7** ✓
* `bash scripts/test_smoke_unified_broker.sh` → **PASS=49** ✓
* `scrip --ir-run beauty.sno < beauty.sno` now runs further than
  before but still **does not** byte-match the oracle output
  (38-line truncated output ending with "Parse Error" vs oracle's
  649 lines, md5 `408fc788ca2ef425fc1f87e26d45a7a5`).  IR is
  unaffected by the SM lt_find fix; this is a separate latent
  issue in IR's beauty self-host, tracked below as
  SN-26c-parseerr.
* The 4-way scrip-monitor was **not yet re-run** after the fix
  (build artifact rebuild deferred for next session — see
  build-system note below).  Smoke + Broker green is the proven
  evidence; full monitor re-run is owed.

**Collateral correction:** any one4all SM program with two
identifiers that differ only in case AND that one is used as a
goto target was silently mis-routing under SM/JIT before this
fix.  Beauty's double-function trick (`shift`/`Shift`,
`reduce`/`Reduce`, `pop`/`Pop`, `visit`/`Visit`) was the
visible victim because it deliberately uses paired labels.

### SN-26c-parseerr — `Parse Error` at line ~38 of `scrip --ir-run beauty.sno < beauty.sno`

### SN-26c-stmt153 — CLOSED 2026-04-24 (session #3)

**Root cause:** `sm_lower.c lower_stmt` emitted `SM_STNO` **before** the
`SM_LABEL` for labeled statements.  Branches (forward and backward)
target the label, so they landed on `SM_LABEL` at index N+1 and
**skipped the `SM_STNO` at index N**.  Consequences:

- `&STCOUNT` / `&STNO` under-counted for every branch to a labeled stmt.
- `g_sm_steps_done` under-counted, so `sm_interp_run_steps(prog, st, n)`
  ran more *source* statements than IR did at the same step limit —
  loop bodies re-executed one extra time before the limit tripped.

At beauty's G1 loop (`i = 0 / G1: i = i + 1 / $UTF_Array[i,2]=... :S(G1)`):
- IR step-limit check is at the top of `while (s)` — fires **before**
  any statement executes, so stopping at step N means stmts 1..N-1 ran
  and stmt N is about to run (with `i` reflecting N-1 executions).
- SM `SM_JUMP_S -> G1_label` used to land AFTER `SM_STNO`, letting the
  arithmetic `i = i + 1` opcodes run a second time before the step
  limit caught up.  Now it lands BEFORE `SM_STNO`, firing the limit
  on re-entry — matching IR.

**Fix (pending commit in one4all):** swap emit order in `lower_stmt`:
```c
/* 0. Define label BEFORE SM_STNO ... */
if (s->label && s->label[0]) {
    int lbl_idx = sm_label(p);
    lt_define(lt, s->label, lbl_idx);
}
/* 1. Statement counter tick */
sm_emit(p, SM_STNO);
```

**Verification (session #3):**
- Minimal probe (`i = 0 / G1: i = i+1 / LT(i,3) :S(G1)`) — monitor now
  reports `all 7 statements agree across IR/SM/JIT`.  Pre-fix: DIVERGE
  at stmt 5, `i` IR=1 vs SM=2.
- Beauty monitor — stmts 1..636 now `IR=SM=JIT agree`.  stmt 153 is
  clean.  New first DIVERGE at stmt 637 (see SN-26c-stmt637 below).
- Gates: Smoke **PASS=7**, Broker **PASS=49** (summary line also now
  reads 49 correctly; previously the counter itself was off-by-one).

**Collateral correction:** The fix also corrects forward-goto step
counting.  Every `DEFINE('…') :F(XEnd)` idiom in beauty was a forward
branch that previously skipped the target's STNO.  Post-fix, both
forward and backward branches to labeled statements correctly tick
the step counter.  All beauty source programs use this idiom heavily
(328 labeled statements total).

### SN-26c-stmt637 — IR `doDebug=0` vs SM/JIT `doDebug=""` at stmt 637

**Captured 2026-04-25 (session #4) after SN-26c-stmt637 closed:**
```
$ scrip --ir-run beauty.sno < beauty.sno
*-----------------------------------------------------------------------
* Program:       SNOBOL4 Beautifier
* Author:        Lon Cherryholmes
... (37 lines of comments and the leading ppStop preamble) ...
Parse Error
                  ppStop         =  ARRAY('1:4')
```

scrip exits 0, prints 38 lines.  CSNOBOL4 oracle (`-bf -P 64k -S 64k`)
and SPITBOL x64 oracle (`-bf` with SETL4PATH) both produce 649 lines,
md5 **`408fc788ca2ef425fc1f87e26d45a7a5`**, byte-identical.

scrip's output truncates inside beauty's INTERNAL parser stage —
"Parse Error" is a beauty-emitted message (search beauty.sno for
that string).  Beauty has parsed 38 lines of its own source-as-input
and then rejected something the oracles accept.  This is a
**runtime semantic divergence** in scrip's IR-run path: scrip
correctly parses beauty.sno itself, but when beauty.sno's runtime
SNOBOL4 parser (running inside scrip) tries to parse its own input
(also beauty.sno), it chokes.

**Likely candidates for next session:**

1. **Another case-sensitivity site** somewhere outside `sm_lower.c`
   — the SN-26c-stmt637 fix only addressed SM's lt_find.  IR's
   tree-walk runtime, the snobol4 frontend lexer, and the
   pattern-matching primitives could each have their own case-fold
   bugs that fire only when running case-sensitive source against
   case-sensitive input.  Audit grep:
   ```
   grep -rn "strcasecmp\|tolower\|toupper\|TOLOWER\|TOUPPER" \
       src/runtime/x86/ src/driver/interp.c \
       src/frontend/snobol4/ | grep -v test
   ```
2. **Pattern primitive miscompare** — beauty's parser uses heavy
   pattern matching (POS, RPOS, SPAN, BREAK, ANY, NOTANY).  If
   any of these treat a SPAN string case-insensitively when they
   shouldn't, beauty's tokenizer produces wrong tokens.
3. **`is.inc` IsSpitbol/IsSnobol4 dialect detection broken** —
   per RULES.md `is.sno` warning, `IDENT/DIFFER(.NAME, 'NAME')`
   discriminator may misclassify the runtime, sending beauty
   down the wrong include path.  Inspect what beauty/global.inc
   does with the result.
4. **`OPSYN` dispatch under case-sensitive lookup** —
   `io.inc` does `OPSYN('INPUT', ...)` style aliases.  If the
   runtime's OPSYN table lookup is folded but the user-visible
   identifier is preserved (or vice versa), the alias doesn't
   resolve.

**Session 2026-04-26 (#5) diagnostic update — BUG DECOMPOSED INTO TWO:**

Reproduced cleanly with a 2-line probe: `printf "                  x =
'hello'\nEND\n" > /tmp/probe3.sno` fed as stdin to `scrip <mode>
beauty.sno < /tmp/probe3.sno`.  All three modes diverge from CSNOBOL4
oracle (which beautifies the assignment correctly).

| Mode | Behaviour on probe3 |
|------|---------------------|
| CSNOBOL4 oracle | beautifies `x = 'hello'` to `                  x              =  'hello'`, exit 0 |
| scrip `--ir-run` | **silent** — no output at all, exit 0 |
| scrip `--sm-run` | prints `Parse Error\n                  x = 'hello'`, exit 0 |
| scrip `--jit-run` | same as SM |

The same 4-way scrip-monitor DIVERGE seen on full beauty self-host
also reproduces on probe3 — symptom is identical, just an order of
magnitude smaller corpus.  Monitor reports DIVERGE at stmt 637
(`DEFINE('TX(lvl,pat,name)omega') :go TXEnd` in omega.inc) with
`doDebug IR=0 SM=` — but this is **misleading**: stmt 637 is just
the snapshot point, not the bug site.

Root analysis via env-gated step trace (`ONE4ALL_STEP_TRACE=1`):

| | IR | SM |
|---|---|---|
| total stmts run | 654 | 648 |
| main00 iterations | 1 | 1 |
| main01 iterations | **2** | 1 |
| main02 iterations | **2** | 1 |
| reaches main05 | yes (stno=652) | no |
| reaches mainErr1 | no | yes (sm_stno=646) |

**Bifurcation point:** SM's parse pattern at static stmt 1092 (`snoSrc
POS(0) *snoParse *snoSpace RPOS(0) :goF mainErr1`) **fails** on
`x = 'hello'\n` — this is the "Parse Error" path.  IR's same parse
pattern **succeeds** — so IR loops back to main01 for a 2nd iteration,
hits EOF in main02's INPUT, jumps to main05, runs parse on
`END\n`, and calls `pp(sno)` — but **`pp(sno)` produces no OUTPUT**.

**Two distinct bugs feed the same observable:**

**Bug A — SM/JIT pattern matching: `*snoParse` deferred reference
fails to match valid SNOBOL4 statements.**  In SM/JIT lanes,
`SM_PAT_REFNAME s="snoParse"` (pc 9627 in this build) is consulted
via the BB pattern-match driver.  The pattern is a 175+ alternation
defining beauty's grammar (lines 50-200 of beauty.sno).  Something
in this dispatch — the deferred-reference resolution itself, or
how the variable-bound pattern is bound to the BB machinery, or
how the alternation's components are evaluated — diverges from
IR/oracle behaviour.  Look at:
- `bb_boxes.c` deferred-reference handler for `*var` patterns
- `SM_PAT_REFNAME` / `SM_PAT_USERCALL` (the non-arg versions)
  emitted by `sm_lower.c` for `*var` pattern primitives
- `bb_build` dispatch for the deferred-reference case
- Whether the pattern `*snoParse` is being re-resolved per match
  attempt or cached at lower-time (caching it would break beauty
  because `snoParse` is built from many `*sub_pattern` deferrals
  whose values are themselves pattern variables defined later in
  source)

**Bug B — IR `pp(sno)` emits no OUTPUT.**  In IR lane the parse
succeeds, so beauty's main loop calls `pp(sno)` to format and emit
the parsed statement.  CSNOBOL4 emits the formatted line; scrip's
IR emits nothing.  Either:
- `pp` is being called but its `OUTPUT = ...` assignments fail
  silently (perhaps an OPSYN issue: `OUTPUT` opsyn'd to a function
  in `io.inc` that returns null on the IR path?)
- `pp` returns early due to a pattern-match conditional that takes
  a different branch in IR than in oracle
- `sno` (the parse tree returned by Pop()) is malformed in IR's
  Pop semantics, causing pp to walk an empty tree

**Symptom hierarchy:**
```
SN-26c-parseerr (visible: scrip can't run beauty)
├── Bug A: SM/JIT *snoParse fails  → "Parse Error" output
└── Bug B: IR pp(sno) emits nothing → silent empty output
```

**Sub-rungs:**
- [x] **SN-26c-parseerr-a** — Reproduce minimally; decompose into A+B.
- [ ] **SN-26c-parseerr-b** — Investigate Bug A: SM/JIT `*snoParse`
  deferred-reference dispatch.  Smaller probe needed: write a
  10-line test that uses `*var` pattern matching with an
  alternation; see if probe agrees IR vs SM.  If probe diverges,
  the bug is generic to `*var` dispatch.  If probe agrees, the bug
  is specific to beauty's deeply-nested alternation structure.
- [ ] **SN-26c-parseerr-c** — Investigate Bug B: IR `pp(sno)`
  emits nothing.  Probe: define `pp(x)` as a trivial OUTPUT-only
  function in a standalone test, see if IR's call/return mechanics
  are broken; or call beauty's pp on a hand-built sno tree.

**Re-verified baseline (this session):**
- Both oracles self-host beauty cleanly: CSNOBOL4 (`b3aeb9f`) and
  SPITBOL x64 (SN-30 build) both produce 649-line output with md5
  `408fc788ca2ef425fc1f87e26d45a7a5` from the canonical commands:
  ```
  cd /home/claude/corpus/programs/snobol4/demo/beauty
  /home/claude/csnobol4/snobol4 -bf -P 64k -S 64k \
      -I. -I/home/claude/corpus/programs/include \
      beauty.sno < beauty.sno
  SETL4PATH=".:/home/claude/corpus/programs/include" \
      /home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno
  ```
- Gates: Smoke **7**, Broker **49** (after corpus repo cloned —
  Broker drops to 48 without it because `rung01 ICN` SKIPs).
- 4-way scrip-monitor confirms: beauty<beauty and probe3<probe3
  produce IDENTICAL DIVERGE signature at stmt 637.



**Setup to resume (fresh session):**
```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
cd /home/claude/one4all
# IMPORTANT: build_scrip.sh populates /tmp/si_objs/; scrip-monitor
# needs that first.  Always run build_scrip.sh before make scrip-monitor.
bash scripts/build_scrip.sh
make scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Reproduce SN-26c-parseerr — full self-host:
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
SNO_LIB=/home/claude/corpus/programs/include \
    timeout 60 /home/claude/one4all/scrip --ir-run \
    $BEAUTY/beauty.sno < $BEAUTY/beauty.sno > /tmp/scrip_ir.out 2>&1
wc -l /tmp/scrip_ir.out      # current: 38 lines (oracle: 649)
grep "Parse Error" /tmp/scrip_ir.out  # confirms repro

# Reproduce SN-26c-parseerr — minimal probe (session #5):
printf "                  x = 'hello'\nEND\n" > /tmp/probe3.sno
SNO_LIB=/home/claude/corpus/programs/include \
    /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno < /tmp/probe3.sno
# Expected: silent (no output) on IR.  CSNOBOL4 oracle prints the
# beautified line.  This is Bug B (IR pp(sno) silent).
SNO_LIB=/home/claude/corpus/programs/include \
    /home/claude/one4all/scrip --sm-run $BEAUTY/beauty.sno < /tmp/probe3.sno
# Expected: "Parse Error\n                  x = 'hello'".
# This is Bug A (SM/JIT *snoParse fails).

# Decompose IR vs SM step-by-step (proves the bifurcation):
SNO_LIB=/home/claude/corpus/programs/include ONE4ALL_STEP_TRACE=1 \
    /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno \
    < /tmp/probe3.sno 2> /tmp/ir.trace > /dev/null
SNO_LIB=/home/claude/corpus/programs/include ONE4ALL_STEP_TRACE=1 \
    /home/claude/one4all/scrip --sm-run $BEAUTY/beauty.sno \
    < /tmp/probe3.sno 2> /tmp/sm.trace > /dev/null
echo "IR steps: $(grep -c '^IRSTEP' /tmp/ir.trace) (expect 654)"
echo "SM steps: $(grep -c '^SMSTEP' /tmp/sm.trace) (expect 648)"
echo "IR main01 iterations: $(grep -c 'label=main01' /tmp/ir.trace) (expect 2)"
echo "SM main01 iterations (via pc=9586): $(grep -c 'pc=9586' /tmp/sm.trace) (expect 1)"

# Oracle reference for comparison:
cd /home/claude/corpus/programs/snobol4/demo/beauty
/home/claude/csnobol4/snobol4 -bf -P 64k -S 64k \
    -I. -I/home/claude/corpus/programs/include \
    beauty.sno < beauty.sno > /tmp/csn_beauty.out 2>/dev/null
md5sum /tmp/csn_beauty.out   # should match 408fc788ca2ef425fc1f87e26d45a7a5
SETL4PATH=".:/home/claude/corpus/programs/include" \
    /home/claude/x64/bin/sbl -bf beauty.sno < beauty.sno > /tmp/sbl_beauty.out
md5sum /tmp/sbl_beauty.out   # should match 408fc788ca2ef425fc1f87e26d45a7a5
```

**Required clones (session #5 footgun):** Broker gate fails 48/49
unless `corpus` is cloned (the missing PASS is `rung01 ICN`,
which SKIPs when `/home/claude/corpus/programs/icon` doesn't
exist).  Always clone `corpus` even if your goal doesn't seem to
need it.  Same applies to `csnobol4` and `x64` — both build
scripts FAIL without the source repo present.  Fresh-session
clone list: `.github`, `one4all`, `corpus`, `csnobol4`, `x64`.

**Build-system latent issue** (carried forward from session #3):
`scripts/build_scrip.sh` uses a different Makefile path
(`src/Makefile`) that does NOT populate `/tmp/si_objs/`.  The
top-level `Makefile`'s `scrip-monitor` target depends on
`/tmp/si_objs/*.o`.  Workflow is: run `build_scrip.sh` first
(populates si_objs as a side effect of that Makefile), then
`make scrip-monitor`.  Both paths happen to coexist because
`build_scrip.sh` invokes the top-level Makefile internally.  Not
a bug; just a footgun — `make scrip-monitor` from a clean tree
fails with undefined references until `build_scrip.sh` has run
once.  After modifying `sm_lower.c` (or any file in `runtime/x86/`),
the corresponding `.o` in `/tmp/si_objs/` is stale; force a refresh
with `rm -f /tmp/si_objs/sm_lower.o && bash scripts/build_scrip.sh`
before `make scrip-monitor`.

**Gate:** Smoke=7, Broker=49 after any fix for SN-26c-parseerr.

**Dependencies:** SN-26c-stmt637 fix landed (`sm_lower.c lt_find`
→ `strcmp`).  No other open dependencies.

---

## Closed historical detail — SN-26c-char-ir investigation

### SN-26c-char-ir — CLOSED 2026-04-24

**Root cause:** `nv_snapshot` in `src/runtime/x86/snobol4.c:2349` allocated
its `pairs[]` array with plain `malloc`, making Boehm GC blind to the
DT_S pointers it held.  Sequence:

1. Monitor takes IR snapshot at stmt N (pointers into live NV table bytes).
2. `exec_snapshot_restore(&baseline)` calls `NV_CLEAR_fn` — removes the
   NV table's references to the captured strings.
3. SM re-runs (fresh allocations trigger GC).  Unreachable bytes get
   reclaimed; Boehm reuses the memory for SM temporaries.
4. `snap_diff` later dereferences the stale DT_S pointers in
   `ir_snap.nv_pairs` — reads whatever SM wrote there.
5. Classic signature: shared `\n~` tail across many diverging vars.

**The IR runtime itself was never wrong.**  `bb_cap` / `NAME_commit` /
`dup_substr` already produce GC-tracked bytes correctly.  Bug was
entirely at the snapshot layer.

**Fix (one4all, pending commit):**
- `src/runtime/x86/snobol4.c` `nv_snapshot`: `malloc` → `GC_MALLOC` (+ comment).
- `src/driver/sync_monitor.c` `exec_snapshot_free`: removed
  `free(s->nv_pairs)` (GC reclaims).

**Result:** stmts 1–152 now cleanly `IR=SM=JIT agree`.  Broker
recovered 48 → 49.  Smoke 7.  New first DIVERGE surfaces at stmt 153
— exactly as the old notes predicted — but with a far cleaner
signature (single variable `i`, integer, one-line diff).  Stmt 153
closed in session #3 — see SN-26c-stmt153 section at top of file
(root cause was `SM_LABEL` / `SM_STNO` emit order in `sm_lower.c`).

---

## Closed historical detail — SN-26c-char-ir investigation

### Parent goal: SN-26 — True beauty.sno self-host (4-way monitor)

**Done-when:** scrip reproduces SPITBOL's output byte-for-byte on
`beauty.sno < beauty.sno` in all three modes (--ir-run, --sm-run,
--jit-run).  4-way monitor (IR/SM/JIT + CSN) reports zero DIVERGE.

**Oracle chain (verified 2026-04-24, both green):**

| Oracle | Mode | Result |
|--------|------|--------|
| SPITBOL | `-b` | error 217 duplicate label on double-function pairs. Expected — beauty needs `-f`. |
| SPITBOL | `-bf` (SN-30 build) | **exit 0, 649 lines, 0 stderr.**  `SETL4PATH=".:<corpus/include>" sbl -bf beauty.sno < beauty.sno`. |
| CSNOBOL4 | `-b` | Duplicate labels. Expected. |
| CSNOBOL4 | `-bf` | **exit 0, 649 lines, 0 stderr.**  `snobol4 -bf -P 64k -S 64k -I. -I<corpus/include> beauty.sno < beauty.sno`. |

Both oracle outputs are byte-identical (md5
`408fc788ca2ef425fc1f87e26d45a7a5`).  **The PDLPTR SEGV at stmt 1074
described in the previous active rung (SN-26c-pre-CSN-a3) does not
reproduce on CSNOBOL4 HEAD `b3aeb9f`** — presumably closed by some
intervening fix, or the required `-P 64k -S 64k` stack sizing (per
SN-29c) was the missing piece.  SN-26c-pre-CSN-a3 moved to closed/
unreproducing below.

### SN-26c-char-ir — first 4-way monitor DIVERGE: IR char-constant garbage at stmt 18

**Setup verified 2026-04-24.**  `scrip-monitor` (the IM-15b 4-way
build linking `libcsnobol4.a`) runs beauty self-host without aborting
on framework errors.  It iterates stmt-by-stmt comparing IR, SM, JIT
ExecSnapshots; at the final stmt it additionally compares IR to
CSNOBOL4 (CSN runs once at the end — globals cannot be safely
re-initialised between sub-runs per IM-16).

**First DIVERGE at stmt 18.**  Statements 1–17 all report
`IR=SM=JIT agree`.  At stmt 18 the monitor reports 12 variables
differ between IR and (SM, JIT).  SM and JIT agree with each other;
**IR is the outlier**.

```
DIVERGE at stmt 18 [label: -, line 0]
  IR   last_ok=?      (SM=1  JIT=1)
  IR vs SM (12 var(s) differ):
    FF            IR=)N~                SM=<FF byte>
    VT            IR=)N~                SM=<VT byte>
    TAB           IR=)N~                SM=<TAB byte>
    NUL           IR=)N~                SM=<NUL byte>
    BS            IR=)N~                SM=<BS byte>
    BSLASH        IR=                   SM=\
    CR            IR=)N~                SM=<CR byte>
    SEMICOLON     IR=0)N~               SM=;
    NL            IR=P)N~               SM=<NL byte>
    LF            IR= )N~               SM=<LF byte>
    FSLASH        IR=`)N~               SM=/
    HT            IR=)N~                SM=<HT byte>
  IR vs JIT (12 var(s) differ):  [same 12 vars, same IR values]
```

**Signal pattern.**  The recurring `)N~` three-byte suffix across many
variables is not coincidence — it's a shared stale buffer being
aliased or copied wholesale into descriptors.  The variation in
prefix byte (`0` for SEMICOLON, `P` for NL, space for LF, backtick
for FSLASH, empty for BSLASH) is the *correct* result byte for each
of those characters, suggesting the builder writes one good byte
then concatenates garbage.  Classic "result buffer not
NUL-terminated / not duplicated" bug in the IR tree-walk path.

**Probable locus.**  `CHAR(n)` or equivalent character-constant
builder in `src/driver/interp.c` — only SM/JIT go through the BB
pump and likely use arena-duplicated strings; the IR path likely
grabs a char into a short-lived buffer and stores the descriptor
without duplicating the content.  SM/JIT correctness means the SM
opcode (likely `SM_CHAR` or inline in `SM_FUNC_CALL`) is fine — the
divergence is IR-specific.

**The actual stmt 18.**  Source counting is offset from naive
column-1 parsing.  My quick awk scan of `beauty.sno` said stmt 18
is `snoBuiltinVar = SPAN(…)`, but the variables that differ
(`BSLASH`, `SEMICOLON`, `FF`, `HT`, …) do not appear anywhere in
`beauty.sno` or its beauty-local `.inc` files.  These names are
defined somewhere earlier in the include chain — probably in
`global.inc` (which beauty.sno `-INCLUDE`s first) or in the
`is.inc`/`FENCE.inc`/`io.inc` compatibility includes added by
SN-29b.  Pin the exact file next session.

**Next-session work order:**

1. `grep -rn "BSLASH\b" /home/claude/corpus/programs/` — find the
   defining `.inc`.  Expected format:
   `BSLASH = CHAR(92)` or similar.  Verify `CHAR()` is the
   constructor in every case.
2. Write a 2-line probe program that hits the bug in isolation:
   ```snobol4
           &FULLSCAN = 1
           x = CHAR(92)
           OUTPUT = x
   END
   ```
   Run under `--ir-run`, `--sm-run`, `--jit-run`.  If IR outputs
   garbage and SM/JIT output `\`, the bug is confirmed in `CHAR()`.
   Commit probe under `test/` as the regression gate.
3. Inspect the IR path for `CHAR(n)` in `interp.c`.  Hypothesis:
   result descriptor points into a stack or temp buffer that is
   reused before the descriptor is consumed; fix is `strdup`
   (or arena-alloc) on the result.  Compare to SM handling in
   `sm_interp.c` to identify the good pattern.
4. After fix: re-run 4-way monitor on beauty self-host.  Next DIVERGE
   is expected at stmt 153 per the old notes (`UTF_Array='797163616:32490'`
   IR vs `'124,2'` SM/JIT) — but now on a freshly understood baseline.

**Setup commands to resume:**

```bash
# Oracles (both already self-host beauty):
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
# SPITBOL rebuild (manual — build_spitbol_oracle.sh SKIPs on prebuilt bin/sbl):
cd /home/claude/x64 && rm -f bin/sbl bootsbl *.o
make bootsbl && make BASEBOL=./bootsbl sbl && make bininst

# scrip + 4-way monitor:
cd /home/claude/one4all
bash scripts/build_scrip.sh
make scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Reproduce the stmt-18 divergence:
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
SNO_LIB=/home/claude/corpus/programs/include \
    timeout 120 /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty.sno < $BEAUTY/beauty.sno 2>&1 | grep -A 40 "DIVERGE at stmt 18"
```

**Side quest unblocked this session:** `/home/claude/one4all/Makefile`
was missing a compile step for `src/runtime/x86/name_t.c`.  The
top-level `make scrip-monitor` path (as distinct from
`scripts/build_scrip.sh` which uses the in-tree `src/Makefile`)
rm's `/tmp/si_objs/*.o` then rebuilds, but did not recompile
`name_t.c`, causing a link failure on `name_commit_value` /
`name_init_as_call`.  Fixed: added `$(CC) $(CRT) -c $(RT)/x86/name_t.c
-o $(OBJ)/name_t.o` after the `snobol4_nmd.c` compile (line 71 of
Makefile).

**Gate:** Smoke=7, Broker=49 after any `interp.c` fix — these run
without needing the new sbl, so they validate scrip independently
of SN-30.  SN-30 regressions are SN-30f; hold for a separate sweep.

**Dependencies:**
- SN-30 closed (oracles both self-host beauty) — no longer gating.
- SN-26c-pre-CSN-a3 PDLPTR SEGV unreproducing — no longer gating.

### SN-26c-pre-CSN-a3 — pin the PDLPTR corruption site  [UNREPRODUCING 2026-04-24]

**Status 2026-04-24:** does not reproduce on CSNOBOL4 HEAD `b3aeb9f`.
`snobol4 -bf -P 64k -S 64k -I. -I<corpus/include> beauty.sno <
beauty.sno` runs to completion, exit 0, 649 lines of beautified
output, 0 stderr.  No SEGV at stmt 1074 or anywhere.  Either
(a) an intervening fix between the session-8/9 work and `b3aeb9f`
closed the underlying issue, or (b) the `-P 64k -S 64k` stack sizing
(discovered in SN-29c) was always the missing piece and session-8/9
ran with defaults (`-P 8k -S 4k`).  Leaving this rung in place for
forensic reference; not picking it back up unless a future beauty-
related SEGV recurs.  Strategy-A (AddressSanitizer) and Strategy-B
(31-site breakpoint sweep) write-ups below remain accurate as
technique if the bug ever returns.

### SN-26c-pre-CSN-a3 (historical detail) — pin the PDLPTR corruption site

**Problem:** CSNOBOL4 `-bf` SEGVs at `beauty.sno:616 stmt 1074`
(`snoLine = INPUT` in `main02`).  Crash site is `SCIN1` at
`isnobol4.c:11459` (`D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)`).

**Memory state at SEGV** (sessions 8 and 9 agree):
- `PDLPTR.a.i = 0xc0 (192)` — **tiny int; should be heap pointer**
- `PDLHED.a.i = 0x60 (96)` — **tiny int; should be heap pointer**
- `PDLEND.a.i` = valid heap pointer (intact)
- `LENFCL.a.i` = valid heap pointer (intact)
- 256 bytes of PDL stack ending at PDLEND = all zeros

**SCAN frame arithmetic:** PDLPTR − PDLHED = 96 = 2 scan frames ×
3 descriptors × 16 bytes.  At SCAN entry (`v311.sil:2716`
`MOVD PDLHED,PDLPTR`), PDLPTR was already 96; MOVD propagated it;
two subsequent INCRA +48 → 192.  **The corruption predates this
SCAN invocation.**

**SIL inventory of PDLPTR writes:** `MOVD`/`INCRA`/`DECRA` plus
bulk `PUSH`/`POP` only.  No direct `SETAC`/`SETAV`/`PUTAC`/`SPCINT`.
Corruption must propagate through a legitimate-looking op —
likely a bad `POP` restoring a saved value from a smashed
interpreter stack.

**Source-of-truth for any patch:** `v311.sil`.  `snobol4.c` and
`isnobol4.c` are generated.  Patch SIL, rebuild via
`make -f Makefile2 OPT='-O0 -g' xsnobol4`.

**Environment gotcha — hardware watchpoints silently fail in this
sandbox.**  Unconditional `watch res.pdlptr[0].a.i` fires zero
times while PDLPTR transitions from 0x0 to 0xc0.  Cause:
container kernel restricts `PTRACE_POKEUSER` / DR0-DR7.  Software
watchpoints work but single-step every instruction — intractable
for beauty.sno's million-instruction workload.

**Environment gotcha — csnobol4 catches SIGSEGV itself.**
`lib/init.c:688` registers `err_catch` for SIGSEGV; it longjumps
back to the interpreter main loop.  **No core dump is produced,
regardless of `ulimit -c unlimited`.**  Use gdb with
`handle SIGSEGV stop` instead.

**Environment gotcha — gdb `run < file` wipes `set args`.**
Correct incantation:
```
file /home/claude/csnobol4/snobol4_dbg
handle SIGSEGV stop nopass
run -b -f -I. beauty.sno < beauty.sno
```
Args on the `run` line; stdin redirect at end.

**⚠ Do NOT run top-level `make clean` in csnobol4.**  It wipes
`Makefile2` (generated from `Makefile2.m4`) AND the `snobol4`
binary.  Recovery: `git restore . && git clean -fd && bash
/home/claude/one4all/scripts/build_csnobol4_oracle.sh`.

### Next-session work order

**Strategy A — AddressSanitizer (try first).**  If corruption is a
buffer overrun from an adjacent `res` field clobbering
`res.pdlptr[0]` (consistent with session-8's all-zero PDL region),
ASan names the write site directly.  No hardware watchpoints needed.

```bash
cd /home/claude/csnobol4
rm -f *.o xsnobol4
make -f Makefile2 \
     OPT='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
     LDOPT='-fsanitize=address' xsnobol4
cp xsnobol4 snobol4_asan
# Validate with trivial program first:
echo "        output = 'ok'" > /tmp/ok.sno
echo "END" >> /tmp/ok.sno
/home/claude/csnobol4/snobol4_asan -b /tmp/ok.sno
# Then run beauty self-host:
cd /home/claude/corpus/programs/snobol4/demo/beauty
ASAN_OPTIONS=abort_on_error=1:halt_on_error=1 \
    /home/claude/csnobol4/snobol4_asan -b -f -I. beauty.sno < beauty.sno
```

If `Makefile2` rejects `LDOPT`, patch `Makefile2.m4` to pipe
`$(OPT)` through to the link line.  `ASAN_OPTIONS=detect_odr_violation=0`
may be needed if CSN globals are oddly aligned.

**Strategy B — 31-site breakpoint sweep (if ASan silent).**  Full
PDLPTR write-site inventory from `isnobol4.c`:

```
7667  PUSH(PDLPTR)            # cstack save
7718  POP(PDLPTR)             # cstack restore
11433 +=3*DESCR               # SCIN frame push
11463 -=3*DESCR               # SCIN frame pop
11590 +=3*DESCR
11698 +=3*DESCR
11707 +=3*DESCR
11734 -=3*DESCR
11937 -=6*DESCR
11972 -=3*DESCR
12006 PUSH(PDLPTR)
12026 POP(PDLPTR)
12075 -=3*DESCR
12153 +=3*DESCR
12236 +=3*DESCR
12250 PUSH(PDLPTR)
12256 +=3*DESCR
12270 POP(PDLPTR)
12276 D(PDLPTR) = D(PDLHED)   # full-struct copy from PDLHED
12281 POP(PDLPTR)
12289 +=3*DESCR
12300 D(PDLPTR) = D(PDLHED)
12305 +=3*DESCR
12343 +=DESCR+SPEC
12419 PUSH(PDLPTR)
12439 POP(PDLPTR)
12448 +=3*DESCR
12474 +=3*DESCR
12577 D(PDLPTR) = D(PDLHED)
12595 +=3*DESCR
12607 +=3*DESCR
```

Gdb breakpoints with `commands {silent; printf; continue}` handlers,
redirect to log, grep for first "sane → tiny" transition.  Watch
PDLHED in parallel — the three `D(PDLPTR) = D(PDLHED)` sites
(12276, 12300, 12577) simply propagate a PDLHED corrupted earlier.

PUSH/POP semantics (`include/macros.h:152-153`):
```
#define PUSH(x)  D(cstack+1) = D(x); cstack++; OFCHK()
#define POP(x)   cstack--; UFCHK(); D(x) = D(cstack+1)
```
Full-descriptor 16-byte copy — POP propagates corruption without
a direct `PDLPTR = <value>` statement.

### After the SEGV closes

1. Patch `v311.sil` (not generated C), rebuild, verify past stmt 1074.
2. Gate sweep: Smoke=7, Broker=49, SN-7=51/51, Broad=225/225.
3. Return to **SN-26c** step 3: walk 4-way monitor divergences.
   First known DIVERGE at stmt 153 (`[START] → [G1]`):
   IR `UTF_Array='797163616:32490'` vs SM/JIT `'124,2'`.
4. Clean up ~40 `sm_lower: unresolved label 'error'/'err'` warnings.
5. **SN-26c-pre-CSN-b** — bare-minimum repro for upstream (Phil Budne).
6. **SN-26d** — `test_smoke_beauty_self_host.sh` standing gate.

### Baseline reproduction

```bash
DEST=/home/claude/corpus/programs/snobol4/demo/beauty
cd $DEST
/home/claude/csnobol4/snobol4 -b -f -I. beauty.sno < beauty.sno
# expect: 32 stdout lines, exit 1, "Caught signal 11 in statement 1074 at level 0"
```

**Debug binaries in place:**
- `/home/claude/csnobol4/snobol4` — release O3, no debug info
- `/home/claude/csnobol4/snobol4_dbg` — O3 -g
- `/home/claude/csnobol4/snobol4_O0` — O0 -g

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

## Current state

**HEADs after 2026-04-26 session #7:**
- one4all @ pending commit (SN-26c-parseerr-d: extend E_FNC arg-defer
  to E_VAR — closes the isolated shift probe but does NOT close beauty
  self-host; deeper diagnosis needed)
- corpus @ `9a62ff9` (unchanged; SN-29b commit)
- .github @ this commit (session #7 progress recorded)
- x64 @ unchanged (SN-30 build, bin/sbl resync still owed)
- csnobol4 @ `b3aeb9f` (unchanged; beauty self-hosts under both
  oracles to 649-line output, md5
  `408fc788ca2ef425fc1f87e26d45a7a5`)

**Gates (verified 2026-04-26 session #7 after E_VAR defer extension):**
Smoke **7** · Broker **49**.  No regressions from the 6-site change.

**Session 2026-04-26 (#7) deltas — root cause refined; isolated probe
closed; beauty still broken:**

- **New isolated probe pins the bug at one site.**  14-line
  `/tmp/probe_shift.sno` reproduces SN-26c-parseerr without any of
  beauty's machinery:
  ```snobol4
                    DEFINE('Shift_t(t,v)')                     :(Shift_t_end)
  Shift_t           OUTPUT = '  Shift_t called: t=' t ' v=' v
                    Shift_t = .dummy                           :(NRETURN)
  Shift_t_end
                    word    = SPAN(...)
                    shifty  = EVAL("word . thx . *Shift_t('idtag', thx)")
                    'hello world' shifty
  END
  ```
  Pre-fix: oracle prints `v=hello`; all three scrip lanes print `v=`
  (empty).  Post-fix: all four agree `v=hello`.  This is the same shape
  beauty's `~ 'name'` OPSYN produces via `EVAL("p . thx . *Shift('name',
  thx)")` — the cursor-captured `thx` was being eagerly read at pattern-
  build time instead of at match time.

- **Refined diagnosis vs session #6.**  Session #6 said the bug was
  E_FNC args evaluating eagerly; that was real but **incomplete**.  The
  larger pattern is: **any arg of `*fn(args)` whose value depends on
  later events (cursor capture, ARBNO progress, etc.) must be deferred
  to match time, not just E_FNC args**.  E_VAR was the missed case —
  a comment at `interp.c:4018` literally said "Plain E_LIT and E_VAR
  args don't need this", which was wrong for E_VAR when the variable
  is set by a cursor capture earlier in the same pattern.

- **Fix landed (in working tree, will commit at handoff):**

  | File | Site | Change |
  |------|------|--------|
  | `src/driver/interp.c` ~3125 | E_CAPT_COND_ASGN E_DEFER(E_FNC) defer-loop | E_FNC → (E_FNC ∥ E_VAR) |
  | `src/driver/interp.c` ~3157 | E_INDIRECT(E_FNC) Snocone variant defer-loop | same |
  | `src/driver/interp.c` ~4027 | bare `*fn(args)` defer-loop | same |
  | `src/runtime/x86/sm_lower.c` ~337 | SM E_CAPT_COND_ASGN args defer-loop | same |
  | `src/runtime/x86/sm_lower.c` ~374 | SM E_CAPT_IMMED_ASGN args defer-loop | same |
  | `src/runtime/x86/sm_lower.c` ~449 | SM bare `*fn(args)` args defer-loop | same |

  Mechanism unchanged from session #6: wrap arg as DT_E (frozen
  EXPR_t*); `bb_usercall` and `name_commit_value(NM_CALL)` already
  thaw DT_E via EVAL_fn at match time.  Extending the kind check to
  include E_VAR was a one-line edit per site.

- **Side investigation (ultimately a wash): EVAL_fn parser.**  Spent
  effort on the hand-rolled `_ev_expr` parser in `snobol4_pattern.c`
  — added a `defer_idents` parameter and `_ev_make_dt_e_var` helper.
  Then discovered that path is unreachable in the current scrip
  config: `g_eval_str_hook` is wired to `_eval_str_impl_fn` in
  `scrip.c:399`, which routes through `parse_expr_pat_from_str` (real
  bison parser) → `interp_eval_pat`.  `_ev_expr` is fallback only.
  Reverted those changes to keep the diff minimal.  If anyone ever
  NULLs `g_eval_str_hook`, the same bug exists in `_ev_val` and
  needs the same fix.

- **CRITICAL: probe3 (beauty minimal, `x = 'hello'\nEND\n`) STILL
  FAILS post-fix.**  This was the surprise of the session.  The
  isolated shift probe passes cleanly but beauty self-host on the
  same 2-line input still shows the same divergence:

  | Lane | probe3 result | shift probe result |
  |------|---------------|--------------------|
  | oracle | `                  x              =  'hello'` | `v=hello` ✓ |
  | --ir-run | `                                 'hello'` (x missing) | `v=hello` ✓ FIXED |
  | --sm-run | `Parse Error\n                  x = 'hello'` | `v=hello` ✓ FIXED |
  | --jit-run | same as --sm-run | `v=hello` ✓ FIXED |

  The shift probe and beauty's actual shift call should produce the
  same EXPR_t lowering for `*Shift('snoLabel', thx)`.  Both reach
  `interp_eval_pat`'s E_DEFER(E_FNC) handler; both should hit the
  patched defer-loop.  But beauty doesn't close.  Possibilities:

  1. Beauty's `shift` template differs structurally from my probe in
     a way that bypasses the patched site — perhaps the call goes
     through `pat_assign_callcap` (which I patched at one site) but
     a different path through `bb_build` that I missed.
  2. `thx` gets reset/clobbered between the cursor capture and the
     `*Shift` fire by an intervening pattern operation.
  3. There's a SECOND eager-eval site in the deferred-arg
     materialisation (in `bb_boxes.c` or `bb_build.c`) that
     evaluates DT_E args before the Shift call fires.

- **Decisive next-session move:**  add a one-line trace in
  `bb_usercall`'s thaw loop printing `(name, arg.v, arg.s, arg.ptr)`
  for each thawed arg.  Run beauty's probe3 with the trace.  If the
  arg comes in as DT_E and thaws to `''`, the bug is in `eval_node`
  for E_VAR (NV_GET_fn at thaw time).  If the arg comes in as DT_S
  with empty value, the defer-wrapping never happened — meaning
  beauty takes a DIFFERENT codepath that I didn't patch.  The trace
  decides.

**Sub-rung status:**
- SN-26c-parseerr-a `[x]`: decompose bug — closed session #5.
- SN-26c-parseerr-b `[~]`: Bug A — Closed for the isolated probe in
  session #6/#7.  Beauty's full self-host still produces "Parse
  Error" on SM/JIT, so closure is incomplete.
- SN-26c-parseerr-c `[~]`: Bug B — Closed for the isolated probe in
  session #6/#7 (E_FNC defer + E_VAR defer).  Beauty's IR self-host
  still emits the LHS as empty, so closure is incomplete.
- SN-26c-parseerr-d `[~]`: NEW sub-rung — extend defer to E_VAR.
  Closes the isolated shift probe but not beauty.  See diagnosis
  above for next session.

**Current step: SN-26c-parseerr** — sub-step d (E_VAR defer landed but
beauty still broken; trace bb_usercall thaw to find the real path).

**Next-session work order (resume here):**
1. Run the canonical setup chain (install_system_packages, build_scrip,
   build_csnobol4_oracle, build_spitbol_oracle, build_csnobol4_archive,
   make scrip-monitor).  Required clones: `.github`, `one4all`,
   `corpus`, `csnobol4`, `x64`.
2. Confirm working tree clean and HEAD has SN-26c-parseerr-d.
3. Re-run the shift probe to confirm it still passes:
   ```bash
   /home/claude/one4all/scrip --sm-run /tmp/probe_shift.sno
   # expect: Shift_t called: t=idtag v=hello
   ```
4. Reproduce beauty failure:
   ```bash
   printf "                  x = 'hello'\nEND\n" > /tmp/probe3.sno
   BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty
   SNO_LIB=/home/claude/corpus/programs/include \
       /home/claude/one4all/scrip --ir-run $BEAUTY/beauty.sno < /tmp/probe3.sno
   # current: 33 spaces + 'hello' (x missing).  Oracle: x then 14 spaces then = then 'hello'.
   ```
5. Add one-line trace in `bb_usercall` (`stmt_exec.c:423`) at the start
   of the thaw loop.  Print each arg's `(v, s, ptr)`.  Re-run probe3.
   The trace tells you whether args arrive as DT_E (defer worked,
   thaw broken) or DT_S empty (defer never happened, different codepath).
6. If args are DT_E and thaw to empty: inspect `eval_node` for E_VAR
   at the moment the cursor capture fires.  Expect NV_GET_fn(thx) to
   return the captured substring; if it returns empty, the cursor
   capture itself isn't writing to NV table (different bug).
7. If args are DT_S empty: hunt for the unpatched codepath.  Likely
   candidates: `bb_build.c` materialisation, the trampoline path in
   `bb_boxes.c`, or a third eager-eval site in `interp.c` I missed.
8. Once probe3 closes for IR: the SM/JIT \"Parse Error\" is likely a
   downstream consequence — verify by re-running.
9. Once probe3 fully closes: full beauty self-host, all 3 modes,
   md5-match `408fc788ca2ef425fc1f87e26d45a7a5`.
10. Re-run gates (Smoke 7, Broker 49) and 4-way scrip-monitor.
11. Commit with proper SN-26c-parseerr closure.


**Latent follow-ups** (small, not gating):
- SN-8a latent: named-args path in `SM_PAT_USERCALL` all-E_VAR stash never consumed.
- SN-22/23 cleanups: `NAME_push` return `void *` → `void`; `cache_get_fresh` template purity.
- SN-26 scout: `IR last_ok=?` on DIVERGE — uncaptured in `sync_monitor.c`,
  one-line fix at `sync_monitor.c:330` (add `ir_snap.last_ok = ...` after
  `exec_snapshot_take(&ir_snap)` — but IR has no equivalent of `sm_st.last_ok`
  to copy from, so the fix is non-trivial after all).  Cosmetic for now.
- `build_spitbol_oracle.sh` SKIPs on prebuilt `bin/sbl` — add capability probe
  so it auto-rebuilds when the checked-in binary predates the source.
- ~40 `sm_lower: unresolved label 'ERROR'/'ERR'` warnings during beauty compile.
  Cosmetic but noisy.  May be related to Bug A — `:S(error)` and `:F(err)` in
  beauty's parser definitions could be unresolved goto targets that SM treats
  as Error 24 halt, potentially explaining why some pattern alternatives
  silently halt instead of failing-and-trying-the-next-alternative.
- SN-26c-stmt637 env-gated probes (`ONE4ALL_STEP_TRACE=1`) are now
  permanent diagnostic infrastructure — proven invaluable in session #5
  for pinning the IR-vs-SM step-count divergence.  Keep.
