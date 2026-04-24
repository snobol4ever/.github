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
- [~] **SN-29d** — SPITBOL x64 4.0f cannot self-host beauty —
  **upstream v4.0f `-f` bug.**  Without `-f`, duplicate-label errors
  fire on the double-function trick (`shift`/`Shift`, `reduce`/`Reduce`,
  `pop`/`Pop`, `visit`/`VISIT`).  This matches RULES.md's
  "SPITBOL `-f` is broken in v4.0f" guidance and SN-25's won't-fix
  closure.  **Consequence:** beauty's `.ref` for self-host lane comes
  from CSNOBOL4 only, not from both oracles.
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

## Active rung — SN-26c-char-ir (needs re-capture post-SN-31)

Full detail below.  This is where work resumes next session.

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

**HEADs after 2026-04-24 session:**
- one4all @ `fcc66d13` (SN-31: scrip default case-sensitive)
- corpus @ `88be074` (unchanged)
- .github @ pending (SN-31 close, SN-26c-char-ir needs re-capture)
- x64 @ pending (bin/sbl + bootstrap/ resync for SN-30g)
- csnobol4 @ `b3aeb9f` (unchanged; beauty self-hosts)

**Gates (last verified 2026-04-20):**
Smoke **7** · Broker **49** · SN-7 drivers **51/51** · Broad corpus **225/225**
in all three modes · SN-9c-e JIT parity **207/207/207** on crosscheck.
Not re-verified this session.  SN-30f sweep owed.

**Session 2026-04-24 deltas:**
- **SN-30 closed** (a/b/c/d/e/g done; f deferred to regression sweep).
  x64 sbl rebuilt from `cc68516` UPPERCASE sources; beauty self-host
  byte-identical to CSNOBOL4 output on both oracles.
- **SN-26c-pre-CSN-a3 unreproducing** on CSNOBOL4 HEAD `b3aeb9f`.
  Moved to closed/historical below.
- **SN-26c-char-ir opened** — first real IR-vs-SM/JIT divergence at
  stmt 18, 12 char-constant vars, IR produces `)N~`-family garbage
  while SM=JIT correct.  Probable locus: IR `CHAR()` result buffer
  not duplicated.  Active rung.
- **Makefile build-path bug fixed** — `name_t.c` now compiled when
  invoking `make scrip-monitor` from clean.

**Session 2026-04-24 (cont.) deltas:**
- **SN-31 fully closed** — scrip default flipped to case-sensitive
  (`snobol4.l:60 sno_fold_on = 0`, `scrip.c:137 opt_case_sensitive = 1`).
  Lexer regenerated (`snobol4.lex.c`).  Gates: Smoke **PASS=7**,
  Broker **PASS=49** on new default, no regressions.
- **Goal-file hypothesis on SN-26c-char-ir disproven** in isolation —
  `POS(n) LEN(1) . var` probe against `&ALPHABET` agrees IR=SM=JIT
  on single-char extraction.  The `BSLASH/SEMICOLON/FF/HT` names in
  the old monitor capture were folded forms of `bSlash/semicolon/ff/ht`
  from `global.inc`, captured before case-sensitive default was in
  force.  The real first-DIVERGE under correct case semantics has
  not been captured yet.
- **RULES.md** — "Case-sensitive name space" section added; oracle
  invocation table reflects new scrip default.

**Current step: SN-26c-char-ir (re-capture).**  Next session: build
csnobol4 + spitbol oracles, build `scrip-monitor CSN_A=...`, run the
4-way monitor on beauty self-host with the new case-sensitive scrip,
capture the actual first DIVERGE (could well be somewhere entirely
different from stmt 18), and form a new hypothesis from that evidence.
The old notes about char-constant `)N~` garbage are superseded.

**Latent follow-ups** (small, not gating):
- SN-8a latent: named-args path in `SM_PAT_USERCALL` all-E_VAR stash never consumed.
- SN-22/23 cleanups: `NAME_push` return `void *` → `void`; `cache_get_fresh` template purity.
- SN-26 scout: `IR last_ok=?` on DIVERGE — uncaptured in `sync_monitor.c`, one-line fix.
- `build_spitbol_oracle.sh` SKIPs on prebuilt `bin/sbl` — add capability probe
  so it auto-rebuilds when the checked-in binary predates the source.
- ~40 `sm_lower: unresolved label 'ERROR'/'ERR'` warnings during beauty compile.
