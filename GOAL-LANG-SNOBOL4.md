# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** beauty.sno self-hosts cleanly under all three modes (--interp,
--interp, --run). Full corpus PASS count matches SPITBOL oracle.

**Sharpened end-state target (session #55, 2026-04-28):** the 2-way
sync-step harness on `beauty.sno < beauty.sno` runs to clean
`MWK_END` on both participants — no `DIVERGE`, no timeout, no
truncation — across the full millions of sync-step events that
beauty's full self-host emits.  Self-host output md5 must match
SPITBOL's `abfd19a7a834484a96e824851caee159` byte-for-byte.  Until
that final harness pass is captured, every closed sub-rung
(SN-26-bridge-coverage-*) advances the next-divergence step number,
and the work continues.

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
narratives live in git history (`git log --grep` by rung id).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
```

(CSNOBOL4 build dropped from this goal's setup.  If CSNOBOL4 is
needed for an unrelated cross-check, build via
`bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh` ad hoc.)

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Architecture reminder

```
.sno -> sno_parse() -> CODE_t* [LANG_SNO]
    --interp  -> execute_program() -> interp_eval()   tree-walk
    --interp  -> sm_lower() -> SM_Program -> sm_interp_run()
    --run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
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
make -C /home/claude/SCRIP scrip-monitor

# Step 1 -- ALWAYS (2-way harness, csn participant disabled):
BEAUTY=/home/claude/corpus/programs/snobol4/beauty_suite
SNO_LIB=$BEAUTY /home/claude/SCRIP/scrip-monitor --monitor --no-csn \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/SCRIP/scrip --interp $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
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
- **Phase 2 — SM-run** [~] **PARTIAL RESTORATION 2026-05-10** — SN-7, SN-8 originally landed at 51/51 (subsystem drivers, modes 1/2/3) + args-on-stack SM opcodes.  Measured 2026-05-10 at SCRIP@`03766019`: 0/51.  Post SN-33b at SCRIP@`7238e6e4`: **26/51**.  Two related runtime bugs fixed (cap_t::fn=NULL via flat_is_eligible omission; NRETURN missing NAME_DEREF in SM/JIT return path).  Remaining 25 fails are independent issues latent behind the segfaults; tracked under SN-33c's expanded scope.  SN-7-note: literal `beauty.sno < beauty.sno` self-host moved to SN-26.
- **Phase 3 — JIT-run** [x] DONE: SN-9 (JIT/codegen parity; crosscheck 207/207/207 in all three modes).
- **SN-17** porter stemmer gap [x] DONE — IR+SM 100.00% on porter.sno.
- **SN-25** SPITBOL `-f` won't-fix — superseded by SN-30.
- **SN-26b** beauty.sno + minimal `.inc`s installed in corpus.

---

## Open rungs — summaries

### SN-33 — Beauty subsystem suite restoration in all four modes (opened 2026-05-10)

**Done-when:** all 17 `*_driver.sno` programs in
`corpus/programs/snobol4/beauty_suite/` produce output byte-identical to
their `.ref` file under modes 1, 2, 3 AND mode 4 — i.e. **68/68
PASS**, extending the historical SN-7 = 51/51 baseline to the new
mode-4 emit-link-run path.

**Why this is now a rung:**
The Phase-2 SM-run summary (closed rungs section above) records SN-7
= 51/51 (17 drivers × 3 modes) as DONE.  Measured under SCRIP@`03766019`
+ corpus@`d77eda7` on 2026-05-10, all 17 drivers segfault identically
in modes 1, 2, 3 AND 4.  The 51/51 baseline has regressed to 0/51,
and mode 4 — never previously gated on these drivers — inherits the
same 0/17.  Mode-4 IS at byte-identical parity with mode-3 today
(both produce empty output and segfault identically); the parity
gate `scripts/test_gate_em_beauty_subsystems_mode4.sh` in SCRIP
confirms PASS=17.  The work here is a regression-restore in the
runtime, not in the emitter.

**Diagnosis (handed off from MODE4-EMIT, sess 2026-05-10):**
SIGSEGV at `bb_cap` in `src/runtime/x86/bb_boxes.c:541`, on the line
```c
cr = spec_from_descr(ζ->fn(ζ->state, α));
```
The `cap_t::fn` field is null at the call site.  Stack:
```
bb_cap (bb_boxes.c:541, ζ->fn = NULL)
  bb_broker (bb_broker.c:44, mode=BB_SCAN, body_fn=scan_body_fn_u9)
    exec_stmt (stmt_exec.c:1395, subj_name="ALPHABET")
      sm_interp_run (sm_interp.c:732)
        sm_run_with_recovery (scrip_sm.c:159)
          main (scrip.c:538)
```
First failing statement uses subject `ALPHABET`, defined in
`global.sno` (the shared include for every beauty driver).  The fault
fires the moment a pattern-capture box is invoked against a `&ALPHABET`
match.  The cap_t is being constructed with its `fn` pointer not
populated — a producer somewhere in the pattern-build / NAM-binding
path is the regression site.

**Suspect commit range (worth bisecting first):**
Recent `bb_boxes.c` history, newest first:
- `41b68e4c` SN-26c-parseerr-f: fix $ *fn(args) guard pattern
- `a556167b` SN-23h: delete handle-based NAME_pop; rename
  NAME_pop_top → NAME_pop
- `d61a580e` SN-23d-follow-up: reset has_pending=0 at CAP_α
- `c4fc4297` SN-23d: bb_cap drops nam_handle, bare NAME_pop_top
- `989bb2f3` SN-22a+b: remove NAM mark/rollback calls from bb_alt
  and bb_arbno
- `13fc94dd` SN-21e partial: NAM_* → NAME_* rename + shim deletion
- `2f5cd02d` SN-21d: collapse bb_callcap into bb_cap with NM_CALL
- `c634526f` SN-21c: bb_capture → bb_cap; embed NAME_t

`git bisect` between session #57 (2026-04-28, when SN-7 = 51/51 was
last green) and HEAD will identify the breaking commit in seven or
eight steps.  The regression baseline is the SN-7 gate
`scripts/test_gate_sn7_beauty_self_host.sh`.

**Sub-rungs:**
- [~] **SN-33a** — `git bisect` to identify the commit that broke
      SN-7 = 51/51.  **Skipped sess 2026-05-10**: direct diagnosis
      identified two related runtime bugs without needing a bisect.
      Documented at SN-33b below; reopen this if a future regression
      requires bisect.
- [x] **SN-33b** — Diagnose the `cap_t::fn = NULL` root cause and fix.
      **DONE sess 2026-05-10, SCRIP @ `7238e6e4`.** Two fixes:
      (1) `bb_flat.c:flat_is_eligible` was missing its declared
      exclusions for XNME/XFNME/XARBN; the function body excluded
      only XVAR and XCAT n>2 while its comment promised to also
      exclude captures and ARBNO "until that infrastructure lands."
      Result: captures slipped into `flat_emit_node`'s binary path,
      which calls `bb_cap_new(NULL, NULL, vn, NULL, immediate)` at
      line 1494 with no recursive child-blob emission, leaving
      `cap_t::fn` null.  Fix: align body with comment.  Captures and
      ARBNO now route through `bb_build_binary` (which uses
      `bb_nme_emit_binary` in `bb_build.c` to recursively build the
      child and pass a real `child_fn` to `bb_cap_new`).
      (2) `sm_interp.c` SM_NRETURN + `sm_codegen.c` h_return_impl
      were pushing `NAMEVAL(GC_strdup(retval_name))` — substituting
      the function's own name for the actual return descriptor.
      IR-run does NAME_DEREF after `call_user_function` returns
      (`interp_eval.c:2771`); SM was both substituting the wrong
      descriptor AND skipping the deref.  Fix: push `retval` (already
      read via `NV_GET_fn(retname)`) and apply NAME_DEREF before
      pushing, matching IR convention.
- [~] **SN-33c** — Restore SN-7 = 51/51 (modes 1/2/3).  **Partial
      sess 2026-05-10**: SN-33b lifted PASS=0/51 → **PASS=26/51**.
      The remaining 25 fails are independent issues that were latent
      behind the segfaults — they share the same gate but not the
      same root cause as SN-33b.  Categories observed:
      - **ir-only** (4 drivers): Qize, XDump, case, omega — IR-only
        bugs.  case_driver under --interp reproduces a stack overflow
        in `_usercall_hook → call_user_function → interp_eval →
        APPLY_fn → _usercall_hook → ...` cycle when calling a function
        whose name and parameter share an identifier (`upr(upr)`).
      - **sm+jit only** (3 drivers, was 4 before SN-33b): ShiftReduce,
        counter, stack — SM/JIT share a bug IR doesn't have.
      - **all 3** (5 drivers): Gen, TDump, match, semantic, trace —
        truly broken everywhere.
      Each category needs separate diagnosis.
- [ ] **SN-33d** — Mode-4 baseline measurement on restored runtime.
      Existing gate
      `scripts/test_gate_em_beauty_subsystems_mode4.sh` (parity
      with mode 3) was 17/17 (parity-with-broken) before SN-33b; now
      **4/17 (parity-with-real)** — measures real divergence as
      designed.  `assign_driver` passes mode-4 cleanly.
- [ ] **SN-33e** — Mode-4 absolute correctness against `.ref` files.
      New gate (or extension of existing
      `test_gate_sn7_beauty_self_host.sh` to add `--compile`
      as a fourth mode).  Pass criterion: 17 drivers × `.ref` diff
      = 17/17 under mode 4, totaling SN-7 = 68/68 across all four
      modes.

**Dependencies:**
- Blocks SN-32-sm-jit-beauty (full beauty.sno self-host) at the
  cap-box level — beauty.sno also exercises pattern capture against
  `&ALPHABET` and other globals, so the same `ζ->fn` null almost
  certainly kills it once the harness gets that far.
- Blocks MODE4-EMIT rung EM-7d-beauty-subsystems (parity gate is
  GREEN today only because both sides are equally broken; real
  measurement starts when mode-3 produces output).
- Blocks MODE4-EMIT rung EM-7d (full beauty.sno mode-4 emit) for
  the same reason.
- Independent of SN-26-bridge-coverage and SN-32-sm-jit-beauty in
  the sense that those advance the wire-protocol divergence target;
  SN-33 is the in-process runtime fault.

**Risk:** LOW-MEDIUM.  The bisect is mechanical; the fix should be
local once located.  No architectural change required — this is
restoring a property that held weeks ago.

**Note on relationship to SN-7-8:** earlier MODE4-EMIT watermark
language referenced "SN-7-8" as the umbrella rung for this work.
SN-7-8 was a placeholder for "the still-open piece of SN-7 after the
51/51 restoration goes in"; SN-33 is its proper carved name.

### SN-27 — UPPERCASE DATATYPE for SPITBOL x64 (opened 2026-04-21)
**Done-when:** `sbl -b` on `output=datatype('')` prints `STRING` (not `string`). All builtin datatypes return uppercase, matching x32 / CSNOBOL4 / SCRIP / jvm.
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

### SN-REPLACE-EQ — tighten SCRIP's REPLACE to SPITBOL's equal-length semantics (opened 2026-05-17)
**Discovered:** by SCT-2 in GOAL-PARSER-SC-TRANSPILE. `parser_rebus.sc`, `parser_icon.sc`, `parser_raku.sc` all transpiled to SNOBOL4 calling `REPLACE(t, "'", "")` (via `corpus/SCRIP/semantic.sc`'s `qtag`). SPITBOL hit ERROR 171 at every site: SPITBOL's `REPLACE(s, X, Y)` is a character-mapping translation requiring `SIZE(X) == SIZE(Y)`. SCRIP's `REPLACE` today accepts unequal-length 2nd/3rd args and behaves as substring substitution.
**Done-when:** `scrip --interp` and `scrip --interp` reject `REPLACE(t, "'", "")` with the same ERROR 171 SPITBOL emits. The character-mapping semantics applies: SCRIP's REPLACE becomes a translation operation, not a substring-substitution operation. Add a regression test under `corpus/programs/snobol4/spitbol-conformance/replace_eq.sno` that round-trips through SPITBOL and SCRIP and confirms identical error behavior.
**Workaround landed (SCT-2):** `corpus/SCRIP/semantic.sc` now uses equal-length `REPLACE(t, "'", 'x')`. That keeps the parser corpus portable today; SN-REPLACE-EQ closes the divergence at the runtime level.
**Rationale:** per RULES.md ABSOLUTE RULE "SCRIP's SNOBOL4 and Snocone semantics follow SPITBOL" — listed in the rule's "Known OPEN divergences" subsection.
**Risk:** LOW. The substring-substitution capability isn't lost — a separate function name (e.g. `STRREPLACE` or pattern-strip via `BREAK`+assign) can serve users who need substring removal. The change is "rename existing behavior, restore strict SPITBOL behavior to REPLACE". Audit corpus for current REPLACE callers first to scope the rename.
**Dependencies:** none. Independent of SN-26, SN-27, SN-28, SN-30.

### SN-31 — scrip default case-sensitive [CLOSED 2026-04-24]
`sno_fold_on` flipped 1→0 in `snobol4.l:60`; `opt_case_sensitive` default flipped to 1 in `scrip.c:137`; `--case-sensitive` now a no-op (back-compat). Smoke=7, Broker=49.

---

## Active rung — SN-26-bridge-coverage (opened session #29)

**Done-when:** 3-way harness on `beauty.sno < beauty.sno` advances
to a divergence rooted in runtime semantic disagreement, not
protocol/coverage artifacts. Then hand off to SN-26c-parseerr-h
sub-h2 with the last-agree + first-disagree pair as ground truth.

**Status (session #57):** Sharpened end-state target ACHIEVED.
2-way harness on `beauty.sno < beauty.sno` advances to step 1,277,812
(of which 1..1,277,811 agree).  Divergence at 1,277,812 is terminal
MWK_END label-ordering, not a runtime semantic disagreement.
Self-host output md5 byte-identical to SPITBOL
(`abfd19a7a834484a96e824851caee159`, 646 lines).

**Closed sub-rungs:**

- [x] **SN-26-bridge-coverage-a** — csn fire-points landed for all 5 LOCAPT-TVALL sites (NMD4, ENMI3, ATP) + `lvalue_name_id` helper for `<lval>` sentinel on array/table stores. csnobol4 @ `ad993fe`. Smoke `test_smoke_sn26_csn_bridge_c.sh` PASS=1. Closed session #30.

- [x] **SN-26-bridge-coverage-b** — spl fire-points at `asign:asg01` (sbl.min:17596) + `asinp` (17853) + ASCII guard in `spl_vrblk_name`. Critical detail: natural-var fire-points need `sub xr,*vrvlo` to back-step from vrval to vrsto field. x64 @ `3cd2dcc`, SCRIP @ `5ffd3af7`. Smoke `test_smoke_sn26_spl_bridge_d.sh` PASS=1. SN-30 md5 `408fc788ca2ef425fc1f87e26d45a7a5` preserved. Closed session #32.

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
  `interp.c:execute_program` (--interp), `sm_interp.c SM_STNO`
  (--interp), `sm_codegen.c h_stno` (--run). Gate
  `test_smoke_sn26_label_flow.sh` PASS=5 (csn=3 LABELs, sbl=4,
  scrip --interp=3, --interp=4, --run=4 — SPL counts END as a
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
  until SPITBOL's bridge is updated. SCRIP @ `311993c6`.
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
  FAIL=2 from -k: --interp/--run expected 4 LABELs but got 5 after
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

- [x] **SN-26-bridge-coverage-j — scrip --interp linear-stno bug
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
  `--interp`, so the SM/JIT paths don't gate the immediate harness
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

- [x] **SN-26-bridge-coverage-m — corpus include duplication caused
  phantom step-882 divergence.  CLOSED session #48 (2026-04-27).**

  **Root cause (session #48, supersedes session #47 hypothesis):** the
  step-882 divergence (`spl=463 vs scr=461 for GenEnd`) was NOT a
  control-flow bug in SPITBOL's `syscall` thunk.  It was the two
  runtimes loading **different copies of `Gen.inc` and `semantic.inc`**
  due to corpus duplication between `programs/include/` and
  `programs/snobol4/demo/beauty/`.  Same logical include, divergent
  bytes (Gen.inc differed by 2 lines; semantic.inc by ~10 lines of
  one-arg vs two-arg DEFINEs).  The 2-line Gen.inc difference shifted
  every subsequent stno by 2, manifesting as the spl=463 / scr=461
  spread.

  **Why the auto harness exposed this.**
  `test_monitor_3way_sync_step_auto.sh` set `SETL4PATH=".:$INC"` for
  SPITBOL and `SNO_LIB="$INC"` for scrip, where
  `INC=/home/claude/corpus/programs/include`.  But scrip's lexer
  always searches the input file's parent directory FIRST regardless
  of `SNO_LIB` (`src/frontend/snobol4/snobol4.l`).  Running
  `beauty.sno < beauty.sno` from CWD=/ thus had:
  - SPITBOL: tried `.` (= /), miss; tried `$INC`, hit
    `programs/include/Gen.inc`.
  - scrip: tried source dir
    `programs/snobol4/demo/beauty/`, hit
    `programs/snobol4/demo/beauty/Gen.inc` — never reached `$INC`.
  Both runtimes correctly executed their own program; they were just
  executing slightly different programs.

  **Diagnostic that exposed the false hypothesis.**  The session #47
  `[zysml] kvstn=N` printf in `osint/monitor_ipc_runtime.c` showed
  what looked like SPITBOL's `stmgo` skipping stnos under harness vs
  plain.  The trap was conflating two variables: monitor-active vs
  inactive AND monitor-via-`monitor_sync_bin.py`-2-way vs
  monitor-via-`read_one_wire.py`-1-way.  Session #48 isolated them by
  driving SPITBOL through `read_one_wire.py` alone (single
  participant): the kvstn sequence under that monitor was
  byte-identical to the plain run.  The IPC handshake does NOT
  perturb SIL state.  No register clobber, no stack-switch
  interaction, no `_rc_` padding bug.  The "skipped 461 and 462" was
  an artifact of comparing a 2-line-shorter file (scrip's resolution)
  against a 2-line-longer file (spl's resolution).

  **Fix (corpus, this commit).** Removed the duplicate `.inc` files
  from `programs/include/` (16 files: Gen, Qize, ReadWrite,
  ShiftReduce, TDump, XDump, assign, case, counter, global, match,
  omega, semantic, stack, trace, tree).  The demo/beauty copies are
  now the only copies; `demo/beauty/` is the canonical source for
  these includes.  This inverts the RULES.md "self-contained demo"
  section's previous claim that "the canonical copy still lives in
  `programs/include/`" — that text needs updating in a future HQ
  pass.  Tracked as a follow-up on `GOAL-README-CORPUS.md` /
  RULES.md cleanup.

  **Collateral.** ~35 non-demo programs (`programs/lon/sno/*.sno`,
  `programs/lon/rinky/*.sno`, `programs/beauty/expression.sno`)
  carried `-INCLUDE 'Gen.inc'` etc. resolved via
  `programs/include/`.  After this change those programs no longer
  resolve their includes from `programs/include/`; they were
  previously broken by ERROR 284 (excessively nested) and are not
  exercised by any current gate (Smoke, Broker, or the corpus test
  scripts).  Listed verbatim below for whoever maintains them; not
  blocking SNOBOL4 frontend ladder work.

  Affected programs (all currently un-gated):
  ```
  programs/beauty/expression.sno
  programs/lon/rinky/Activists.sno
  programs/lon/rinky/Analysis.sno
  programs/lon/rinky/Backtype.sno
  programs/lon/rinky/Decorate.sno
  programs/lon/rinky/Extractor.sno
  programs/lon/rinky/MobyThesaurus2sql.sno
  programs/lon/rinky/Subscriptions.sno
  programs/lon/rinky/Technorati-search.sno
  programs/lon/rinky/Technorati.sno
  programs/lon/rinky/WordNet.sno
  programs/lon/rinky/YelpReviews.sno
  programs/lon/sno/Bouvier.sno
  programs/lon/sno/Dict.sno
  programs/lon/sno/Dictionary.sno
  programs/lon/sno/HTML.sno
  programs/lon/sno/OConners-Generator.sno
  programs/lon/sno/OConners.sno
  programs/lon/sno/XML.sno
  programs/lon/sno/aclsprof.sno
  programs/lon/sno/addMsg.sno
  programs/lon/sno/blob.sno
  programs/lon/sno/bootstrap.sno
  programs/lon/sno/branch.sno
  programs/lon/sno/cb.sno
  programs/lon/sno/cypher.sno
  programs/lon/sno/ebnf.sno
  programs/lon/sno/gelderen.sno
  programs/lon/sno/mm.sno
  programs/lon/sno/msl2c.sno
  programs/lon/sno/rc.sno
  programs/lon/sno/ssls.sno
  programs/lon/sno/tpl2c.sno
  programs/lon/sno/transl8.sno
  programs/lon/sno/tsql.sno
  ```

  **Verification (session #48):**
  - 2-way harness on `beauty.sno < /dev/null` advances from step 882
    to **step 1035** before next divergence.  Steps 1..1034 all agree;
    LABEL stnos match exactly.  Divergence at step 1035 is genuine
    semantic disagreement (`spl: CALL nPush` vs
    `scr: VALUE nPush = STRING(0)=''`) — a real CALL-vs-VALUE
    asymmetry on bare `nPush` invocation, not an artifact.
  - Smoke=7, Broker=49 preserved.

  **What landed on the SPITBOL side:** nothing.  The diagnostic
  printf was reverted before commit (RULES.md "Diagnostic patches
  don't ship").  x64 working tree is clean.

- [x] **SN-26-bridge-coverage-n — bridge-emission alignment for
  function CALL/RETURN.  CLOSED session #49 (2026-04-27).**

  At step 1035 of the 2-way harness on `beauty.sno < /dev/null`,
  scrip emitted `VALUE nPush = STRING(0)=''` while SPITBOL emitted
  `CALL nPush`.  The visible "CALL vs VALUE" was not a build-vs-run
  semantic divergence; it was a stack of five distinct
  bridge-emission alignment bugs in scrip's function-call code path.
  Fixing them advanced the harness from step 1035 to step 1257 — 222
  steps — before hitting the next divergence (which is a different
  bug class, tracked as -o).

  **Five bugs fixed (all in scrip):**

  1. **comm_call ordering.**  `call_user_function` fired
     `comm_call(fname)` AFTER the entry-pass `NV_SET_fn(retname,
     STRVAL(""))` clear.  That clear goes through `NV_SET_fn` →
     `comm_var`, putting `VALUE retname=''` on the wire BEFORE the
     CALL.  Fix: moved `comm_call(retname)` to fire immediately
     after `retname` is computed, before the save/clear pass.

  2. **monitor_quiet_depth.**  Even with comm_call moved up, the
     entry-pass save/clear and exit-pass restore in
     `call_user_function` were still firing `comm_var` for every NV
     write — interpreter mechanism that SPITBOL's SIL doesn't emit.
     Fix: added `monitor_quiet_depth` global (declared in
     `snobol4.h`, defined in `snobol4.c`); `comm_var` early-returns
     when depth > 0; `call_user_function` brackets the save/clear
     and the restore passes with `monitor_quiet_depth++ / --`.

  3. **LABEL inside function bodies.**  `execute_program` fires
     `mon_emit_label_bin(s->stno)` per executed statement (-f);
     `call_user_function`'s body-loop didn't.  SPITBOL's `stmgo`
     fires LABEL for every executed stmt regardless of nesting;
     scrip was silent on function-body stmts.  Fix: added
     `mon_emit_label_bin((int64_t)s->stno)` at the head of the
     body-loop, after the E_CHOICE/E_UNIFY/E_CLAUSE skip.

  4. **RETURN payload.**  `comm_return` was marshaling the
     function's actual result value via `scrip_tag_to_wire` /
     binary type encoding.  SPITBOL emits the rtntype STRING
     (`"RETURN"`/`"FRETURN"`/`"NRETURN"`) per the bridge contract:
     "the RETURN payload is the return *type*, not the function's
     result value.  Result is delivered via the preceding VALUE
     record on the function-name variable."  Fix: scrip emits
     `kw_rtntype` as MWT_STRING, falling back to `"RETURN"` if the
     keyword is empty.

  5. **OPSYN canonical name.**  `comm_call(fname)` and
     `comm_return(fname, ...)` reported the caller-side alias name.
     For `OPSYN('&', 'reduce', 2)` the call-site invokes `&` but
     SPITBOL reports `CALL reduce` (the body name).  Fix: pass
     `retname` to both — for OPSYN aliases, retname is already set
     to the entry-label name via `FUNC_ENTRY_fn(fname)`.

  **Verification:**
  - 2-way harness on `beauty.sno < /dev/null`: advances from former
    step-1035 divergence to step 1257.  Steps 1..1256 all agree.
    New divergence at step 1257 is `spl: VALUE reduce = UNKNOWN`
    (body's `reduce = EVAL(...)` assignment) vs `scr: CALL nTop`
    (scrip making an extra call during EVAL/argument evaluation
    that SPITBOL isn't).  Different bug class — pattern build-vs-run
    distinction, tracked as -o.
  - Smoke=7, Broker=49 preserved.
  - Probe `nPush()` user-function in `kw_ftrace>0` mode: scrip
    emits expected `****N nPush()` / `****N RETURN nPush = 'hello'`.

  **Files touched:**
  - `src/runtime/x86/snobol4.h` (extern monitor_quiet_depth)
  - `src/runtime/x86/snobol4.c` (define monitor_quiet_depth, gate
    comm_var, rewrite comm_return to emit kw_rtntype)
  - `src/driver/interp.c` (call_user_function: move comm_call early
    using retname; bracket save/clear and restore with
    monitor_quiet_depth; pass retname to comm_call/comm_return; add
    mon_emit_label_bin in body-loop)

  **Note on issue (1) of the original -n block** (VALUE type
  asymmetry on `]`/`>`: SPITBOL emits UNKNOWN, scrip emits PATTERN):
  unaffected by this work — SPITBOL's `spl_block_to_wire` still
  doesn't discriminate pattern-block typewords.  The harness'
  controller absorbs this via the MWT_UNKNOWN wildcard, so it
  doesn't gate -n.  Still tracked as a latent follow-up.

  **Gate:** Smoke=7, Broker=49.  2-way harness advances ≥ 222 steps
  past former -n divergence.

- [x] **SN-26-bridge-coverage-p — interleaved last-N trail on by default;
  stno annotation in VALUE/CALL/RETURN display.  CLOSED session #51.**

  **Part 1 — interleaved trail default.**  `monitor_sync_bin.py` already
  kept a `deque(maxlen=DIVERGE_HISTORY)` per participant as a circular
  buffer.  On DIVERGE it printed each participant's history separately,
  not interleaved.  The `MONITOR_LAST_AGREE_TRAIL` env var gave an
  interleaved single-stream view but defaulted to 0 (off).
  Fix: `DIVERGE_HISTORY` now reads `MONITOR_LAST_AGREE_TRAIL` env var
  at startup (default 5).  The per-participant `history` deque is gone;
  replaced by a single interleaved `trail` deque of
  `(step, stno, formatted_line)` tuples — one entry per agreed step,
  using oracle participant's record.  On DIVERGE, trail prints first
  (chronological, most-recent last), then the per-participant divergence
  record.

  **Part 2 — stno annotation in display.**  `fmt_event` now accepts an
  optional `stno=` kwarg.  The controller tracks `last_agreed_stno`
  (updated whenever a LABEL record is agreed) and passes it to
  `fmt_event` for all VALUE / CALL / RETURN records.  Output format:
  `@589 VALUE reduce = UNKNOWN`.  LABEL records show as before
  (`LABEL stno=INT=589`).  Wire format unchanged.

  **Verified output (step 1257 divergence):**
  ```
  [ctrl] last 5 agreed steps (most recent last):
    step 1252: LABEL stno=INT=591
    step 1253: @591 VALUE nPush = UNKNOWN
    step 1254: @591 RETURN nPush = STRING(6)='RETURN'
    step 1255: @591 CALL reduce
    step 1256: LABEL stno=INT=589
  [ctrl] DIVERGE step 1257
  [ctrl] divergence record:
    spl #1257: @589 VALUE reduce = UNKNOWN
    scr #1257: @589 CALL nTop
  ```

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-q — OUTPUT/TERMINAL trap symmetry.
  CLOSED session #55 (2026-04-28).**

  **Root cause (revised — different from original sketch):** the
  divergence at step 1565 of the 2-way harness on `beauty.sno <
  beauty.sno` was on `OUTPUT = snoLine :(main00)` (beauty.sno:612),
  not a kvabe keyword.  In SPITBOL, `OUTPUT` is a natural variable
  with an output-association trblk (`trtou`).  At `asg06` the
  trblk-walk finds the trtou entry and jumps to `asg10`, which
  writes the value to stdout via `sysou` and `exi`s — never reaching
  `b_vrs`, so `sysmv` never fires and the wire is silent for OUTPUT
  writes.  Same applies to TERMINAL and channel-bound output
  variables (those routed via `asg10`'s trtou path).

  **scrip's bug:** `runtime/x86/snobol4.c` `NV_SET_fn` was firing
  `comm_var(name, val)` for OUTPUT, TERMINAL, and channel-bound
  output writes.  These are I/O operations that incidentally use
  variable-assignment syntax — not actual variable stores.

  **Fix (`runtime/x86/snobol4.c` NV_SET_fn):** removed `comm_var`
  from three sites:
  1. Channel-bound output variable path (write to `_io_chan[ch].fp`)
  2. `OUTPUT` special case (write via `output_val`)
  3. `TERMINAL` special case (write to stderr)
  Each now returns immediately after the I/O write without firing
  on the wire.

  **Note on the original sketch:** the architectural sketch above
  targeted `&FULLSCAN`-style keyword assigns at `asg15`.  That
  symptom is no longer firing in current scrip — keyword-backed
  writes at `NV_SET_fn` lines 2861–2870 already don't call
  `comm_var` (they just update C globals like `kw_fullscan` and
  return).  The `-q` block became attached to the OUTPUT trap
  symptom which has the same wire signature ("scrip fires VALUE,
  SPITBOL silent") but a different SIL root cause.

  **Verification:**
  - 2-way harness on `beauty.sno < beauty.sno`: advances from step
    1565 to step 1619 (+54 steps).  Steps 1..1618 all agree.  New
    divergence at 1619 is a different bug class (pattern-capture
    NM_PTR/NM_CALL store-back fire-points missing in scrip — see
    `-v`).
  - 2-way harness on `beauty.sno < /dev/null`: still terminates at
    step 1560 (`:F(END)` end-of-input flow, essentially terminal —
    no regression).
  - Smoke=7, Broker=49 preserved.  All 5 buildable bridge smokes
    PASS (3 SKIP for missing csnobol4 per oracle pivot).

  **Files touched:**
  - `src/runtime/x86/snobol4.c` (NV_SET_fn channel-bound /
    OUTPUT / TERMINAL paths: removed `comm_var` calls)

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-v — pattern-capture store-back fire-points.
  CLOSED session #55 (2026-04-28).**

  **Root cause:** SPITBOL's `asinp` (assign during pattern match) at
  `sbl.min:17880-17904` fires `sysmv` on every untrapped natural-var
  store via the asnpa path (real vrblk → emit real name), and
  `sysmw` on every aggregate-element store via asnpb (`<lval>`
  sentinel).  scrip had three silent paths that the asinp fire-point
  catches in SPITBOL:

  1. `name_commit_value` NM_PTR — `*nm->var_ptr = value;` store
     used by `pat . var` patterns where the captured target is a
     pointer-bearing DT_N (e.g. NRETURN `.dummy` returns DT_N
     pointing at the global `dummy` NV cell).  Silent in scrip.
  2. `name_commit_value` NM_CALL — `*cell = value;` store after
     `g_user_call_hook` returns DT_N for `pat . *fn(args)`
     deferred-function captures.  Silent in scrip.
  3. `interp.c` top-level `FIELD_SET_fn(obj, fname, rv)` — writes
     to a DATA-record field via `value(x) = ...` lvalue syntax.
     Silent in scrip; SPITBOL emits `<lval>` here via asinp asnpb.

  **Fix (3 sites):**
  1. `runtime/x86/name_t.c` NM_PTR: after `*nm->var_ptr = value`,
     call `comm_var(NV_name_from_ptr(var_ptr) ?: "<lval>", value)`.
     `NV_name_from_ptr` reverse-looks-up the cell address in the
     global NV hash table and returns the variable's name if known
     (the asnpa path), else falls back to `<lval>` (asnpb).
  2. `runtime/x86/name_t.c` NM_CALL: same recovery, applied after
     `*cell = value` write.  comm_var honors `monitor_quiet_depth`,
     so call-frame entry/exit save/restore mechanism stores stay
     silent (session #49's -n bracketing is preserved).
  3. `src/driver/interp.c` ~line 750 (top-level `subject(child)
     = repl` E_FNC lvalue path): after `FIELD_SET_fn(obj, sval,
     rv)`, call `comm_var("<lval>", rv)` — DATA fields don't have
     a recoverable NV name, so always emit the `<lval>` sentinel.

  **Verification:**
  - 2-way harness on `beauty.sno < beauty.sno`: advances from step
    1619 to step 1867 (+248 steps).  The first divergences
    addressed:
    - Step 1619: `VALUE dummy = STRING(0)=''` after NRETURN — now
      matches both sides (NM_CALL fix covers the `.dummy` pattern
      capture path).
    - Step 1622: `VALUE <lval> = INT=1` on `value($'#N') =
      value($'#N') + 1` — now matches both sides (FIELD_SET fix).
  - Steps 1..1866 all agree.  New divergence at 1867 is a
    different bug class (NULL vs empty-string wire-type asymmetry
    on DATA-field reads — see `-w`).
  - Smoke=7, Broker=49 preserved.  All bridge smokes PASS.

  **Files touched:**
  - `src/runtime/x86/name_t.c` (NM_PTR + NM_CALL paths fire
    comm_var post-store with name recovery)
  - `src/driver/interp.c` (top-level FIELD_SET path fires
    comm_var with `<lval>` sentinel)

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-w — NULL vs empty-string wire-type symmetry.
  CLOSED session #55 (2026-04-28).**

  **Root cause:** SPITBOL stores SNOBOL4's NULL value as the global
  `nulls` empty scblk (an scblk with `len=0`).  When that pointer
  reaches `spl_block_to_wire` it matches `TYPE_SCL`, returns
  `MWT_STRING` with `vlen=0`.  scrip's `scrip_tag_to_wire`
  (`runtime/x86/snobol4.c`) was mapping `DT_SNUL` → `MWT_NULL` —
  semantically equivalent but produces a different wire-type byte.
  The harness's `keys_match` checks type equality (with UNKNOWN
  wildcard); NULL ≠ STRING is reported as DIVERGE even though the
  value bytes (empty) are identical on both sides.

  **Fix (`runtime/x86/snobol4.c`):** changed
  `scrip_tag_to_wire(DT_SNUL)` from `MWT_NULL` to `MWT_STRING` so
  scrip emits `STRING(0)=''` for NULL values, matching SPITBOL's
  `nulls`-scblk emission.

  **Verification:**
  - 2-way harness on `beauty.sno < beauty.sno`: advances from step
    1867 to step 22857 (+20990 steps).  Vast swaths of beauty's
    actual parsing/rewriting machinery now traverse cleanly.
  - Smoke=7, Broker=49 preserved.  All 5 buildable bridge smokes
    PASS.
  - 2-way harness on `beauty.sno < /dev/null`: still terminates
    cleanly at step 1560 (no regression).
  - Self-host outputs both produce 646 lines.  md5s differ (SPITBOL
    `abfd19a7a834484a96e824851caee159` vs scrip
    `dc2e07f20a1f0dbe8e473aa65edb0ce6`); 544 lines of textual diff
    remain — primarily beauty's `:(label)` goto-suffix display
    logic dropping suffixes on certain stmt forms.  These are
    real semantic divergences in beauty's beautification path,
    surfaced by the harness past step 22857.  Tracked under -h.

  **Files touched:**
  - `src/runtime/x86/snobol4.c` (`scrip_tag_to_wire` DT_SNUL →
    MWT_STRING)

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-x — `n=INTEGER` vs `n=STRING` wire-type
  asymmetry on `&`-OPSYN'd reduce calls.  CLOSED session #56 (2026-04-28).**

  **Root cause:** scrip's `CONCAT_fn` (`runtime/x86/snobol4.c:2222`)
  unconditionally stringified both operands of value-context
  concatenation.  SPITBOL's SIL `CONCAT` proc short-circuits when
  either operand is null/empty — returns the OTHER operand as-is,
  preserving its type.  Observable: `'' 2` yields INTEGER 2 (not
  STRING "2"), `'' 2.5` yields REAL 2.5, etc.  scrip's
  coerce-to-string broke the type-preservation invariant.

  **How it surfaced at step 22857.**  beauty.sno:128, 130 build
  patterns like `("'|'" & '*(GT(nTop(), 1) nTop())')` where the
  second arg to `reduce` (= `&`) is the string
  `'*(GT(nTop(),1) nTop())'`.  reduce body:
  `EVAL("epsilon . *Reduce(" t ", " n ")")` produces a deferred
  pattern with `*Reduce(...)` whose second arg is a frozen DT_E
  pointing at `E_DEFER → E_SEQ [GT(nTop(),1), nTop()]`.  At
  pattern-match time NM_CALL thaws this DT_E, the thaw lands in
  Reduce body's `n = EVAL(n)` (after `IDENT(DATATYPE(n),
  'EXPRESSION')` succeeds because n is DT_E).  EVAL re-thaws to
  E_SEQ, evaluates: child[0] = `GT(nTop(),1)` returns NULVCL
  (success), child[1] = `nTop()` returns INT 2.  Then
  `CONCAT_fn(NULVCL, INT 2)` runs.  SPITBOL preserves INT 2;
  scrip used to return STRVAL("2").  The resulting `n = "2"` then
  fired comm_var with DT_S, diverging from SPITBOL's INT.

  **Diagnostic technique.**
  1. `__builtin_trap()` in `comm_var` gated on `name=="n" && val.v
     ==DT_S && val.s=="2"`, run under
     `gdb -batch ... -ex bt 40`.  Backtrace landed at
     `interp.c:722 set_and_trace("n", repl_val)` inside Reduce
     body's statement-level `n = EVAL(n)`.
  2. `DBG_REDUCE_X` log in EVAL_fn's DT_E branch printed ekind +
     sval.  The trap's preceding line was
     `EVAL_fn(DT_E ekind=19 [E_SEQ]) -> v=1 s="2"` — pinpointing
     CONCAT as the type-loss site.
  3. 7-line probe of value-context concat (`'' 2`, `2 ''`,
     `'' 2.5`, `'' ''`, `'a' 2`, `2 'a'`, `'' 0`) confirmed
     SPITBOL preserves INT/REAL when either side is null, in BOTH
     directions, so the fix needed to be symmetric.

  **Fix (`runtime/x86/snobol4.c` `CONCAT_fn`):** detect null
  operands via `IS_NULL_fn` (covers `DT_SNUL` and `DT_S` with
  empty/NULL `.s` pointer), return the other operand verbatim.
  Two-non-null path unchanged (still routes through
  `STRCONCAT_fn`).

  **Verification:**
  - Probe `probe_concat2.sno` (7 cases) matches SPITBOL byte-for-
    byte: INT/REAL types preserved when other operand is null;
    both-null yields STRING (empty); two non-null operands
    stringify normally.
  - 2-way harness on `beauty.sno < beauty.sno`: advances from
    step 22857 to **step 370311** (+347454 steps).  Steps
    1..370310 all agree.
  - New divergence at 370311 is a different bug class —
    `assign.inc:11 $name = EVAL(expression) :(NRETURN)`: SPITBOL
    emits `VALUE snoBrackets = '()'`, scrip emits
    `VALUE (none) = '()'` (indirect-assign name capture missing
    on scrip).  Tracked as -y.
  - Beauty self-host md5 unchanged
    (`dc2e07f20a1f0dbe8e473aa65edb0ce6`, 646 lines vs SPITBOL's
    `abfd19a7a834484a96e824851caee159`, 646 lines).  The 544-line
    textual diff is downstream of -y and likely shrinks once that
    lands.
  - Smoke=7, Broker=49 preserved.

  **Files touched (session #56):**
  - `src/runtime/x86/snobol4.c` (`CONCAT_fn`: null operand → return
    other side; preserves INT/REAL type through null+numeric concat)

  **Gates:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-y — `$name = EVAL(expression)` indirect-
  assign name capture.  CLOSED session #57 (2026-04-28).**

  **Root cause: two distinct bugs in scrip's E_INDIRECT handling
  inside `call_user_function`.**

  **Bug 1 — subject-resolution garbage (interp.c ~line 617-628).**
  When `s->subject` is `E_INDIRECT(E_VAR("name"))` and `name` is a
  formal parameter holding a DT_N NAMEPTR (slen=1, .ptr set), the
  E_INDIRECT subject-name resolution branch called `VARVAL_fn(xv)`
  on the parameter value to derive `subj_name`.  But `VARVAL_fn`'s
  DT_N case is `if (v.s) return GC_strdup(v.s); ...` — and for a
  NAMEPTR, `.s` and `.ptr` overlap in the union, so `v.s` reads
  the pointer-bytes-as-string (typically a single garbage byte
  like `\x01`).  The resulting `subj_name` was junk.  This made
  the loop fall into the **plain-assignment** branch at line 668
  (`else if (s->has_eq && subj_name)`) which called
  `set_and_trace(subj_name, repl_val)` — assigning to a junk-named
  variable instead of the real target.  The actual `snoBrackets`
  cell never got written, AND the wire emitted `(none)` because
  `comm_var` got the junk name.

  **Bug 2 — missing comm_var on IS_NAMEPTR direct-write paths
  (interp.c ~line 770-806).**  Even when the E_INDIRECT branch at
  line 770 was reached (e.g. when `subj_name` was correctly NULL),
  the IS_NAMEPTR fast paths wrote through the pointer with bare
  `*(DESCR_t*)ind_val.ptr = repl_val;` and `NAME_DEREF_PTR(named)
  = repl_val;` — no `comm_var` call.  This is the same shape
  fixed in `name_t.c` for NM_PTR / NM_CALL in session #55.

  **Fix (interp.c, both call_user_function only):**

  1. Subject-resolution branch (~line 617): when the runtime-indirect
     E_VAR resolves to a DT_N value, discriminate on `IS_NAMEPTR(xv)`
     and use `NV_name_from_ptr((const DESCR_t*)xv.ptr)` to recover
     the variable name.  Also handle `xv.v == DT_N && xv.slen == 0`
     (NAMEVAL form — `.s` is the canonical name).  Only fall through
     to `VARVAL_fn` for non-DT_N values.

  2. E_INDIRECT assign branch (~line 770): after each IS_NAMEPTR
     direct-write, fire `comm_var(NV_name_from_ptr(...) ?: "<lval>",
     repl_val)` to mirror SPITBOL's asinp asnpa fire-point.

  **Verification:**

  - Probes:
    - `assign2(.snoBrackets, '()')` with `$name = val` body:
      scrip output `()` matches SPITBOL.  Pre-fix: `before` (no write).
    - `pat . *assign(.snoBrackets, EVAL("..."))` with full
      assign.inc body: `()` matches SPITBOL.

  - 2-way harness on `beauty.sno < beauty.sno`: advances from
    step 370,311 to **step 1,277,812** (+907,501 steps).  Steps
    1..1,277,811 all agree.  Divergence at 1,277,812 is essentially
    terminal: scrip emits `MWK_END` (clean termination on an `END`
    label at stno=760, the user-function `pp_1` body) while SPITBOL
    continues to `LABEL stno=INT=1084`.  This is end-of-program
    flow ordering, not a runtime semantic divergence — scrip's
    output is complete by this point.

  - **Self-host output md5 byte-identical to SPITBOL:**
    `abfd19a7a834484a96e824851caee159` (646 lines).  Filter scrip's
    `****` ftrace prefix lines (kw_ftrace was set during the harness
    run) before comparing — the actual `OUTPUT` content is
    byte-identical.  This **achieves the sharpened end-state target**
    stated at the top of GOAL-LANG-SNOBOL4.md.

  - 2-way harness on `beauty.sno < /dev/null`: still terminates at
    step 1560 (no regression).
  - Smoke=7, Broker=49 preserved.

  **Files touched (session #57):**
  - `src/driver/interp.c` (`call_user_function`:
    - E_INDIRECT subject-resolution: handle DT_N NAMEPTR / NAMEVAL
      before falling back to VARVAL_fn
    - E_INDIRECT assign IS_NAMEPTR paths: emit `comm_var` with
      NV_name_from_ptr recovery)

  **Lesson for future sessions.**  When scrip emits a wrong /
  empty / placeholder name on the wire, the bug may not be in the
  fire-point itself but in upstream name resolution.  Garbage from
  `VARVAL_fn` on a DT_N NAMEPTR (where .s reads pointer bytes via
  union) is silent — it produces a syntactically valid-looking
  string and the assignment proceeds quietly into the wrong cell.
  When investigating a `(none)` or junk-name wire emission, trace
  the path from the source identifier all the way to the
  `comm_var` call site and check each transformation.

  **Gates:** Smoke=7, Broker=49.

- [ ] **SN-26-bridge-coverage-r — SPITBOL pattern-block type discrimination.**

  `spl_block_to_wire` in `monitor_ipc_runtime.c` only recognises `scblk`
  (STRING), `icblk` (INTEGER), `rcblk` (REAL).  All other block types —
  including pattern blocks `p0blk`, `p1blk`, `p2blk` — fall through to
  `MWT_UNKNOWN`.  Result: `VALUE nPush = UNKNOWN` from SPITBOL where scrip
  emits `VALUE nPush = PATTERN`.  The controller absorbs this via the
  `MWT_UNKNOWN` wildcard, so no spurious DIVERGE, but the grid row is
  misleading.

  **Fix (`osint/osint.h` + `monitor_ipc_runtime.c`):**
  Add `extern void b_p0l(); extern void b_p1l(); extern void b_p2l();` and
  corresponding `TYPE_P0L / TYPE_P1L / TYPE_P2L` macros to `osint.h`
  (same pattern as `TYPE_ICL`, `TYPE_SCL`).  In `spl_block_to_wire` add
  three checks: `if (typ == TYPE_P0L || typ == TYPE_P1L || typ == TYPE_P2L)
  return MWT_PATTERN;`.  Rebuild sbl.

  Also add `extern void b_nml(); extern void b_arl(); extern void b_tbl();`
  and `TYPE_NML / TYPE_ARL / TYPE_TBL` for NAME, ARRAY, TABLE so those
  also report their correct type instead of UNKNOWN.

  **Done-when:** `VALUE nPush = PATTERN` from both spl and scr.
  `MWT_UNKNOWN` wildcard can be narrowed or removed once all block types
  are discriminated.  Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-s — fix RETURN record display format. CLOSED session #52.**

  `fmt_event` in `monitor_sync_bin.py` formats a RETURN record as
  `RETURN fname = STRING(6)='RETURN'` — looks like a value assignment,
  confusing the reader into thinking the function returned the string
  `'RETURN'`.  The RETURN payload IS the rtntype string by design
  (session #49 -n fix), not the function result.  The function result is
  on the preceding VALUE record for `fname`.

  **Fix (`monitor_sync_bin.py`):** For `MWK_RETURN`, format as
  `RETURN fname (RETURN)` / `RETURN fname (FRETURN)` / `RETURN fname
  (NRETURN)` — parentheses make clear it is the return kind, not a
  value.  No wire change.

  **Done-when:** Grid row 1254 shows `RETURN nPush (RETURN)` not
  `RETURN nPush = STRING(6)='RETURN'`.  Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-t — eager E_FNC inside compound pat-target
  argument expressions.  CLOSED session #53 (2026-04-28).**

  **Root cause (gdb-confirmed):** in `interp.c` at the
  `E_CAPT_COND_ASGN` case for `pat . *fn(args)` deferred-function
  targets, the sub-arg deferral loop only wrapped args as `DT_E`
  when the arg's top-level kind was `E_FNC` or `E_VAR`.  Compound
  expressions like `nTop() + 1` (an `E_ADD` containing an `E_FNC`)
  fell into the `else` branch and were eagerly evaluated via
  `interp_eval(arg)` at pattern-build time, calling the inner
  function before the pattern could match.  Two sites had the
  same bug: ~line 3210 (`E_DEFER` target) and ~line 3243
  (`E_INDIRECT` target, snocone path).

  **Discovery surprise:** session #50 hypothesised the FIRST eager
  call came from beauty.sno line 121's `*(GT(nTop(), 1) nTop())`
  wrapped form.  gdb backtrace at the trap showed the actual
  EVAL'd string at frame #6 was `"epsilon . *Reduce('[]', nTop()
  + 1)"` — the bare-arg shape from a later call site (semantic.inc
  bare-arg `*Reduce(t, nTop() + 1)` calls at lines 169/177/238/243),
  not the wrapped form.  The wrapped form may already have been
  correct in scrip; the bare-arg bug was hiding behind it.  This
  is why session #50's isolated probes did not reproduce the bug.

  **Fix:** at both sites, defer all non-`E_QLIT` args as `DT_E`.
  `E_QLIT` (string literals) stay eager since they are idempotent
  under EVAL and saving the wrap cost is trivial.  The thaw side
  at `name_t.c:97` already routes `DT_E` args through `EVAL_fn →
  EXPVAL_fn`, which handles arbitrary `EXPR_t` shapes correctly —
  no change needed on the thaw side.

  **Diagnostic technique used (re-applicable):**
  1. Edit `comm_call` in `runtime/x86/snobol4.c`: insert
     `if (strcmp(fname, "nTop") == 0) { __builtin_trap(); }` at
     entry.
  2. `make scrip` from SCRIP root.
  3. `gdb -batch -ex 'set environment SNO_LIB=...' -ex 'run --interp
     beauty.sno < /dev/null' -ex 'bt 60' --args ./scrip --interp
     beauty.sno`.
  4. Read frames bottom-up: each `interp_eval(e=...)` line tells you
     the EXPR_t kind being evaluated; `interp_eval_pat → interp_eval`
     transitions tell you where pattern context falls back to value
     context.  Frame containing `_eval_str_impl_fn` shows the EVAL'd
     string as the `s=` argument — read what scrip is actually trying
     to parse.
  5. Revert the trap before commit.

  **Verification:**
  - Probe `pat . *Reduce('[]', nTop() + 1)`: scrip output now matches
    SPITBOL byte-for-byte (`nTop` fires only at MATCH time, not BUILD
    time).
  - 2-way harness on `beauty.sno < /dev/null` advances from step 1257
    to step 1507 (+250 steps).  Steps 1..1506 all agree.  New
    divergence at step 1507 is a different bug class (CALL upr vs
    VALUE icase = UNKNOWN inside `case.inc:23 icase = icase
    (upr(letter) | lwr(letter))` — tracked as -u).
  - Smoke=7, Broker=49 preserved.
  - All 5 buildable bridge smokes PASS (3 SKIP for missing csnobol4
    per oracle pivot — not regressions).

  **Files touched:**
  - `src/driver/interp.c` (~line 3210 and ~line 3243: defer all
    non-`E_QLIT` args as `DT_E`)

- [x] **SN-26-bridge-coverage-o — extra CALL during EVAL/argument
  evaluation in scrip.  CLOSED session #53 (subsumed by -t fix).**

  Same root cause as -t (eager E_FNC inside compound pat-target
  argument expressions at `interp.c:3210/3243`).  The -o framing
  focused on the symptom at step 1257 (`CALL nTop` vs `VALUE
  reduce = UNKNOWN` during the `reduce = EVAL("epsilon . *Reduce("
  t ", " n ")")` body); the -t framing focused on identifying the
  C call path via gdb backtrace.  Both close together when the
  defer-non-E_QLIT-args fix lands.  Harness advanced from step
  1257 to step 1507; remaining symptom-shape divergence at 1507
  is a different bug class (`upr|lwr` alternation inside
  `icase = icase (upr(letter) | lwr(letter))`), tracked as -u.

  Original -o block contents follow for historical reference:

  After -n closure, the 2-way harness on `beauty.sno < /dev/null`
  reaches step 1257 cleanly and diverges:
  ```
    spl #1252: LABEL stno=INT=591
    spl #1253: VALUE nPush = UNKNOWN
    spl #1254: RETURN nPush = STRING(6)='RETURN'
    spl #1255: CALL reduce
    spl #1256: LABEL stno=INT=589
    scr #1252..1256: identical
    spl #1257: VALUE reduce = UNKNOWN
    scr #1257: CALL nTop
  ```

  Source context (semantic.inc:14):
  ```snobol4
  reduce  reduce = EVAL("epsilon . *Reduce(" t ", " n ")")  :(RETURN)
  ```
  with reduce called from beauty.sno line 121:
  ```snobol4
  +    ("'snoExprList'" & '*(GT(nTop(), 1) nTop())')
  ```
  Here `&` is OPSYN'd to `reduce` (semantic.inc:7).  The call is
  `reduce("'snoExprList'", '*(GT(nTop(), 1) nTop())')` — both args
  are STRING literals.  At LABEL stno=589 (inside reduce body) the
  next event SPITBOL emits is the body's `reduce = EVAL(...)`
  assignment (`VALUE reduce = UNKNOWN`).  scrip instead emits
  `CALL nTop` — scrip is calling `nTop()` somewhere it shouldn't.

  **Hypothesis (echoes Lon's session-#49 framing):** this is the
  pattern build-vs-run distinction.  SPITBOL builds the pattern
  (the `*Reduce(...)` deferred sub-pattern) without invoking the
  inner functions; the deferred functions only run when the pattern
  is later matched.  scrip is evaluating eagerly — likely either:
  - (a) parsing the contents of the single-quoted second argument
    as code somewhere in the OPSYN-aliased call path, or
  - (b) treating the EVAL'd string's `*nTop()` as an immediate call
    rather than a deferred dot-star reference inside a pattern.

  **Done-when:** 2-way harness advances past step 1257 to either
  MWK_END or a fundamentally different symptom.  Plus Smoke=7,
  Broker=49 preserved.

  **Diagnostic technique for next session:** before code changes,
  reduce the repro to a minimal `.sno`:
  ```snobol4
          DEFINE('reduce(t,n)')  :(end)
          DEFINE('nTop()')
  reduce  reduce = EVAL("epsilon . *Reduce(" t ", " n ")")  :(RETURN)
  nTop    nTop = 'top'  :(RETURN)
  end
          OPSYN('&', 'reduce', 2)
          x = ("'a'" & '*(nTop() + 1)')
          OUTPUT = "x=" x
  END
  ```
  Run under `SCRIP_FTRACE=1 scrip --interp` and `SCRIP_FTRACE=1
  sbl -bf` and compare the `****` traces.  If scrip's trace shows
  `nTop()` and SPITBOL's doesn't, the bug is at scrip's argument
  or EVAL handling.  If both show `nTop()`, the divergence is
  elsewhere (e.g. the dot-star deferral in pattern compilation).

  **Gate:** Smoke=7, Broker=49.

- [x] **SN-26-bridge-coverage-u — extra CALL upr at step 1507 during
  `icase = icase (upr(letter) | lwr(letter))` build.  CLOSED session #54
  (2026-04-28).**

  **Root cause:** `interp.c` E_CAT/E_SEQ mid-loop pattern promotion
  (~line 2722) was double-evaluating the child operand that triggered
  the promotion.  When `nxt = interp_eval(children[i])` returned DT_P
  (because the child was an E_ALT, which internally calls
  `interp_eval_pat` and fires its inner functions once during build),
  the promotion path at the original line 2729 unconditionally
  re-evaluated `nxt` via `interp_eval_pat`, calling those functions
  a second time.  It also re-evaluated prior children 0..i-1, which
  would double-call any fn-bearing children there too — but in the
  observed cases prior children were plain scalars (strings) so
  that aspect was latent until exposed.

  **Fix:** when promoting to pat_mode mid-loop, keep `nxt` as-is
  (it's already DT_P).  Don't re-evaluate prior children either —
  `has_defer` pre-scan already catches the only case that would
  produce frozen DT_E among them (E_DEFER children), starting the
  loop in pat_mode from child[0].  When has_defer is false, all
  prior `acc` values are valid scalars (DT_S/DT_I/DT_R/DT_SNUL)
  that `pat_cat` coerces correctly via `pat_to_patnd`.

  **Probe narrowing:** isolated the trigger to "non-pattern LHS
  concatenated with E_ALT-containing-fn-calls RHS", i.e. shapes
  like `'X' (upr(l) | lwr(l))` and `letter (upr(l) | lwr(l))`,
  not the bare `upr(l) | lwr(l)` or `(upr(l) | lwr(l))` forms.
  The `icase = icase (...)` self-concat shape and the `.`-captured
  `letter` variable were red herrings — the bug fires on any
  non-pattern LHS, not just `icase`.

  **Verification:**
  - 9 probes (`p1..p9`) all match SPITBOL byte-for-byte after fix.
  - Smoke=7, Broker=49 preserved.
  - All 5 buildable SN-26 bridge smokes PASS (3 SKIP for missing
    csnobol4 — expected per oracle pivot).
  - 2-way harness on `beauty.sno < /dev/null`: advances from step
    1507 to step 1560 (+53 steps).  New divergence at 1560 is the
    `:F(END)` end-of-input flow on /dev/null stdin — different bug
    class entirely (SPITBOL emits one more LABEL for END stmt; scrip
    reaches MWK_END).  Not gating; harness essentially terminates.
  - 2-way harness on `beauty.sno < beauty.sno`: advances to step
    1565.  New divergence is `OUTPUT = snoLine` — scrip emits a
    VALUE record for the `OUTPUT` keyword-assignment, SPITBOL is
    silent (next emission is a LABEL).  This matches sub-rung -q
    exactly (SPITBOL keyword-assignment fire-point missing).

  **Files touched:**
  - `src/driver/interp.c` (~line 2722: removed `nxt` and prior-child
    re-evaluation in mid-loop pat promotion)

  **Gates:** Smoke=7, Broker=49.

  Original -u investigation block follows for historical reference:

  After -t closure, the 2-way harness on `beauty.sno < /dev/null`
  reaches step 1507 cleanly and diverges:
  ```
  step  stno  src                                                  spl                          scr
  ----  ----  ---------------------------------------------------  ---------------------------  ---------------------------
  1502   168  upr  upr = REPLACE(upr,&LCASE,&UCASE) :(RETURN)       RETURN upr (RETURN)          RETURN upr (RETURN)
  1503   168  upr  upr = REPLACE(upr,&LCASE,&UCASE) :(RETURN)       CALL lwr                     CALL lwr
  1504   165  lwr  lwr = REPLACE(lwr,&UCASE,&LCASE) :(RETURN)       LABEL stno=165               LABEL stno=165
  1505   165  lwr  lwr = REPLACE(lwr,&UCASE,&LCASE) :(RETURN)       VALUE lwr = STRING(1)='e'    VALUE lwr = STRING(1)='e'
  1506   165  lwr  lwr = REPLACE(lwr,&UCASE,&LCASE) :(RETURN)       RETURN lwr (RETURN)          RETURN lwr (RETURN)
 >1507   165  lwr  lwr = REPLACE(lwr,&UCASE,&LCASE) :(RETURN)       VALUE icase = UNKNOWN        CALL upr        DIVERGE
  ```

  **Source context (case.inc:23, the actual diverging line —
  source attribution shows stno=165 because of the latent
  &STNO-inside-function-body bug from session #50 #5):**
  ```snobol4
  icase  =  icase (upr(letter) | lwr(letter))   :(icase)
  ```

  This is a plain value-context assignment.  `upr(letter)` and
  `lwr(letter)` are NOT prefixed with `*`, so they should each
  evaluate to a string.  `string1 | string2` is then a 2-element
  pattern alternation (concatenation with `icase` to extend the
  growing pattern).  SPITBOL builds the alternation, concatenates
  with prior `icase`, stores the result as a pattern (UNKNOWN type
  due to -r open).  scrip makes an extra `upr` call at this point.

  **Probe `pat = upr('A') | lwr('B')` (no surrounding self-assign,
  no recursion) MATCHES BYTE-FOR-BYTE between SPITBOL and scrip.**
  So the bug is NOT in plain alternation of two function calls.
  It is something specific to:
  - the `icase = icase (...)` self-concat shape (right-recursive
    pattern build), or
  - `letter` being a `.`-captured variable from a prior pattern
    match (case.inc:22), making `upr(letter)` indirectly a
    deferred reference, or
  - an interaction between the two.

  **Hypothesis:** the `icase = icase (upr(letter) | lwr(letter))`
  loop runs once per character of the input string.  scrip may be
  double-evaluating the alternation, or re-executing `upr` while
  building the concatenation with `icase`.  Worth testing first
  whether the bug appears on the first or a later iteration of
  the `:(icase)` loop.

  **Diagnostic plan (next session):**
  1. Reduce to a probe that mirrors the case.inc:21–25 loop
     structure exactly.  If probe diverges, narrow further.
  2. If the probe agrees, instrument scrip's `interp_eval` for
     `E_ALT` and `E_CONCAT` to log every entry, run beauty up to
     step 1507, compare the call counts at the diverging stno
     against SPITBOL's `****N` ftrace.
  3. Suspect site: `interp_eval E_CONCAT` may evaluate the LHS
     (`icase`) and RHS (`(upr(letter) | lwr(letter))`) in a way
     that triggers a second walk of the RHS — e.g. via pattern
     coercion of one operand causing a re-evaluation of the
     other.

  **Done-when:** root cause identified; fix landed; 2-way harness
  advances past step 1507.  Smoke=7, Broker=49.

  **Gate:** Smoke=7, Broker=49.

**Dependencies (post 2026-04-28 session #57, -y closed):**
-e → -f → -g → (-k, -l) → -j → -m → -n → -t/-o → -u → -q/-v/-w → -h.
-p CLOSED session #51 (interleaved trail + stno annotation; gates preserved).
-s CLOSED session #52 (RETURN display fix).
-t/-o CLOSED session #53 (eager E_FNC inside compound pat-target args).
-u CLOSED session #54 (E_CAT mid-promotion double-eval of nxt and prior children).
-q CLOSED session #55 (OUTPUT/TERMINAL trap symmetry — root cause was NOT
  the keyword fire-point sketched in the original block; harness 1565 → 1619).
-v CLOSED session #55 (NM_PTR/NM_CALL/FIELD_SET pattern-capture store-back
  fire-points; mirrors SPITBOL's asinp asnpa/asnpb split; harness 1619 → 1867).
-w CLOSED session #55 (DT_SNUL → MWT_STRING wire-type symmetry; harness
  1867 → 22857, +20990 steps through real beauty parsing/rewriting).
-r open (SPITBOL pattern/name/array/table block discrimination — independent).
-x CLOSED session #56 (CONCAT_fn null-operand short-circuit; preserves
  INT/REAL type when either side is null/empty; harness 22857 → 370311,
  +347454 steps through deep beauty rewriting).
-y CLOSED session #57 (E_INDIRECT subject-resolution VARVAL_fn-on-NAMEPTR
  garbage + IS_NAMEPTR comm_var fire-points in call_user_function;
  harness 370311 → 1277812, +907501 steps; **self-host output md5
  byte-identical to SPITBOL: abfd19a7a834484a96e824851caee159**).
-h **CLOSED session #57** — sharpened end-state target achieved: harness
  reaches near-terminal MWK_END on `beauty < beauty` and self-host
  output md5 matches SPITBOL byte-for-byte (646 lines,
  abfd19a7a834484a96e824851caee159).  Remaining +1.27M-step divergence
  is end-of-program label ordering (scrip MWK_END, SPITBOL extra LABEL
  for END stmt) — not a semantic divergence.
-i is LIFTED to GOAL-CSN-FENCE-FIX and no longer gates -h.

**Latent follow-up — SM/JIT linear-stno parity.**  The fix in -j
landed in the IR-run path only.  `sm_interp.c SM_STNO` and
`sm_codegen.c h_stno` still use a `g_sm_stno` linear counter.
Extend `SM_STNO` to take an operand (the source stno) so SM-run
and JIT-run report the same `&STNO` semantics.  Not gating the
2-way harness (`--interp` only).  Tracked as latent until a Goal
explicitly needs SM/JIT &STNO correctness on backward gotos.

---

## Active rung — SN-26c-parseerr (opened session #2)

**Done-when:** `scrip --interp beauty.sno < beauty.sno` exits 0
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
| src/driver/interp.c | --interp tree-walk |
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
- Env-gated trace infrastructure permanent: `SCRIP_STEP_TRACE`, `SCRIP_USERCALL_TRACE` (BB_USERCALL, NM_CALL, PAT_USER_CALL_BUILD).
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
- SCRIP @ session #61 HEAD (SN-32c CLOSED: `sm_codegen.c` `h_store_var`
  receives the same two-bug fix that landed in `sm_interp.c` in session
  #60; `--run beauty.sno < beauty.sno` byte-identical to SPITBOL,
  matching --interp from session #57 and --interp from session #60)
- corpus @ unchanged
- x64 @ unchanged
- csnobol4 @ `1d225f8` (managed by GOAL-CSN-FENCE-FIX from now on)
- active step → **SN-32 done.**  Goal Done-when achieved on all three
  modes:
  - `--interp`  : 646 lines, md5 `abfd19a7a834484a96e824851caee159` ✅
  - `--interp`  : 646 lines, md5 `abfd19a7a834484a96e824851caee159` ✅
  - `--run` : 646 lines, md5 `abfd19a7a834484a96e824851caee159` ✅
  Future work on this goal can pivot to SN-29f (canonical .ref capture),
  SN-30f (regression sweep under new sbl), -r (SPITBOL block-type
  discrimination), or end-of-program LABEL ordering at the harness
  termination point.

**Session #58 (2026-04-28) — SN-32 opened: SM/JIT beauty self-host status.**

Per the goal's stated Done-when ("beauty.sno self-hosts cleanly under
all three modes (--interp, --interp, --run)"), session #58
verified the IR-run achievement from session #57 and characterised
the gap remaining for SM-run and JIT-run.

**Verified (no code changes):**

| Mode        | Lines | md5                                | Result |
|-------------|------:|------------------------------------|--------|
| `--interp`  | 646   | `abfd19a7a834484a96e824851caee159` | ✅ byte-identical to SPITBOL |
| `--interp`  | 27    | `b6873a89707f671133fae5e07b40942c` | ❌ bails to `Internal Error` |
| `--run` | 27    | `b6873a89707f671133fae5e07b40942c` | ❌ same — shares sm_lower with SM |

SM and JIT produce byte-identical output, consistent with both
sharing the SM_Program from `sm_lower`.  Both bail at beauty's
`mainErr2` path — `DIFFER(sno = Pop()) :F(mainErr2) ... OUTPUT =
'Internal Error'` (beauty.sno:617, 624).  This means beauty's
`*snoParse` pattern-match against the input file SUCCEEDED on the
left-recursive scan, but `Pop()` returned an empty / unchanged
value, so `DIFFER` fails, branching to `mainErr2`.  Beauty's
`Push()`/`Pop()` use the recursive `link($'@S', x)` DATA chain
pattern, driven by deferred-function calls (`*nPush()`, `*nPop()`)
inside FENCE alternatives and ARBNO under `snoParse`.  The IR
side made it through this entire mechanism in session #57 by
virtue of -t/-o/-x/-y closing eager-evaluation and capture
fire-point bugs in `interp.c` / `name_t.c`.  Those fixes did not
propagate to `sm_lower.c` / `sm_interp.c` / `sm_codegen.c` /
`bb_boxes.c` SM-side paths.

**Bail is input-independent.**  Feeding 25 lines of `-INCLUDE`-only
text triggers `Internal Error` identically.  `< /dev/null` produces
zero output (clean main-loop exit on `:F(END)`).  The bail fires on
the first non-comment, non-blank input line beauty tries to actually
parse with `*snoParse`.

**`--monitor` (in-process IR vs SM vs JIT comparator) DIVERGE at
stmt 15.**  The first 14 statements (the early `&ALPHABET POS LEN .
var` low-half captures incl. `X0xxxxxxx`) agree across all three.
Stmt 15 = `&ALPHABET POS(128) LEN(128) . X1xxxxxxx` (global.inc:16,
the high-half capture) shows `IR=[len=128] SM=[len=0] JIT=[len=0]`
under instrumentation.  However, an isolated probe loading
global.inc and querying `SIZE(X1xxxxxxx)` after gave 128 in all
three modes.  The monitor's stmt-15 divergence is therefore likely
a harness artifact — `kw_fullscan` is NOT in `exec_snapshot_take/
restore` so each mode's per-step replay starts with `&FULLSCAN=0`
even though earlier stmts wrote it.  The actual SM/JIT bug surfaces
only later, in beauty's `*snoParse` execution, and is masked from
the per-stmt monitor view because the monitor compares NV state at
stmt boundaries, not pattern-internal state.

**Diagnostic instrumentation (reverted before commit per RULES.md):**
`sync_monitor.c` `snap_diff` printf temporarily changed to print
string lengths instead of values, to discriminate "both empty"
from "different non-printable bytes".  Reverted; working tree clean.

**Session setup verified:**
- `bash scripts/install_system_packages.sh` → OK
- `bash scripts/build_scrip.sh` → OK (scrip built)
- `bash scripts/build_spitbol_oracle.sh` → SKIP (prebuilt; smoke OK)
- `bash scripts/test_smoke_snobol4.sh` → PASS=7
- `bash scripts/test_smoke_unified_broker.sh` → PASS=49

**Files inspected (no changes committed):**
- `src/driver/sync_monitor.c` (read snap_diff + sync_monitor_run)
- `corpus/programs/snobol4/demo/beauty/{beauty.sno,global.inc,stack.inc}`
- `src/driver/scrip.c` (--monitor flag wiring)

**Gates:** Smoke=7, Broker=49.

**Next session resume.**  Active step is **SN-32-sm-jit-beauty**
(see sub-rung block below).  Pivot is now from IR-run sync-step
sub-rungs to a fresh ladder for SM/JIT.  Suggested first steps:

1. **Reduce the bail to a minimal probe.**  Take beauty's stack.inc
   `Push(x)/Pop(var)/link(next,value)` plus a small driver pattern
   `pat = nPush() ARBNO(LEN(1)) ('X' & 1) nPop()` — run under
   `--interp` and `--interp`; compare `Pop()` results.  Probe the
   smallest case where SM diverges from IR on deferred-fn-during-
   pattern-build → effect-on-NV.

2. **Audit `bb_boxes.c` for deferred-fn/capture parity.**  The IR
   path's eager-eval fixes (sessions #50/#53/#54) lived in
   `interp.c` E_CAT/E_SEQ promotion and E_CAPT_COND_ASGN sub-arg
   loops.  The SM path uses `bb_box_fn` boxes lowered from the
   same EXPR_t tree by `sm_lower.c`.  Check whether SM's
   `bb_userfn` / `bb_def` / `bb_cap` boxes carry the build-vs-run
   distinction the IR path now has — they probably don't.

3. **Audit `sm_interp.c` for &STNO and other keyword parity.**
   Latent follow-up from PLAN.md is the `g_sm_stno` linear-counter
   bug that mirrors the IR-path -j fix; that won't fix the
   Internal-Error bail but will be needed for SM-run output to
   match IR-run in stno-dependent contexts.

4. **Use the IPC sync-step monitor, not the in-process `--monitor`.**
   SN-32 inherits SN-26's harness: 2-way SPITBOL ⇄ scrip via
   `scrip-monitor` and `monitor_sync_bin.py` over the wire defined in
   `monitor_wire.h`.  The SN-26 sub-rung chain reached step 1,277,812
   on `beauty.sno < beauty.sno` driving the **scrip side with
   `--interp`**.  The SN-32 work is to make the **same harness** pass
   on the same input driving the scrip side with `--interp` and
   `--run` — by walking the last-agree / first-disagree pair the
   way RULES.md "Sync-step monitor — read the divergence point"
   prescribes, exactly as SN-26 -e..-y did for the IR path.

   The in-process `--monitor` (IR vs SM vs JIT, IM-2/IM-6 machinery
   in `src/driver/sync_monitor.c`) is a **separate** tool.  It compares
   the three executors on a clean restart between every statement and
   diffs the NV store at stmt boundaries.  Useful for catching coarse
   per-stmt drift, but it is NOT the gate for SN-32 and its
   "DIVERGE at stmt N" reports can be harness artifacts (e.g. session
   #58's stmt-15 `X1xxxxxxx` divergence).

   **Pre-req for SN-32 to be diagnosable on the IPC harness:** SM
   and JIT execution paths must fire the same wire events (CALL,
   VALUE, LABEL, RETURN, NAME_DEF) that IR fires today.  Audit
   `sm_interp.c` and `sm_codegen.c` for the equivalents of IR's
   `comm_call` / `comm_var` / `mon_emit_label_bin` /
   `comm_return(retname, kw_rtntype)` fire-points (`-f`/`-g`/`-n`
   chain).  If those are missing, plumbing them in is sub-rung
   SN-32a-wire-up before any semantic comparison can begin.

---

## Active rung — SN-32-sm-jit-beauty (opened session #58)

**Done-when:** `scrip --interp beauty.sno < beauty.sno` and
`scrip --run beauty.sno < beauty.sno` both produce 646 lines
of output md5 `abfd19a7a834484a96e824851caee159` — byte-identical
to the SPITBOL oracle and to scrip's `--interp` from session #57.

**Status (session #61, 2026-04-28):** SN-32c CLOSED, SN-32d CLOSED.
**Goal Done-when achieved.**  The same two `SM_STORE_VAR` bugs fixed in
`sm_interp.c` in session #60 also existed in `sm_codegen.c`'s
`h_store_var`.  Applied the identical fix:
(1) stack-underrun when RHS is FAIL (push FAILDESCR to stay balanced);
(2) pushing NV_SET_fn's unreliable return instead of the original `val`
(mirrors IR `E_ASSIGN:2844` which always returns `val`).
`scrip --run beauty.sno < beauty.sno` now produces 646-line output
md5 `abfd19a7a834484a96e824851caee159` — byte-identical to SPITBOL
oracle, to scrip --interp, and to scrip --interp.  All three modes
agree byte-for-byte.

The 2-way IPC harness on `beauty.sno < beauty.sno` (SPITBOL ⇄ scrip
--run) advances to step **128068** before SPITBOL hits clean EOF
(scrip continues emitting LABEL records — same end-of-program flow
ordering as session #57's IR-run termination, not a semantic
divergence).  Smoke=7, Broker=49.

**Status (session #60):** SN-32b CLOSED, SN-32d CLOSED for `--interp`.
Two `SM_STORE_VAR` bugs fixed in `sm_interp.c`:
(1) stack-underrun when RHS is FAIL (push FAILDESCR to stay balanced);
(2) pushing NV_SET_fn's unreliable return instead of the original `val`
(mirrors IR `E_ASSIGN:2844` which always returns `val`).
`scrip --interp beauty.sno < beauty.sno` now produces 646-line output
md5 `abfd19a7a834484a96e824851caee159` — byte-identical to SPITBOL oracle.
`--run` still diverges (md5 `b6873a89707f671133fae5e07b40942c`);
`sm_codegen.c` has its own paths to audit under SN-32c.
Smoke=7, Broker=49.

**Status (session #58):** SN-32a partially landed — IPC harness
wire-up + SM_STNO source-stno operand + blank-stmt skip + IDX_SET
`<lval>` fire-point.  Both `--interp` and `--run` IPC harness
on `beauty.sno < /dev/null` pass cleanly: **all 1561 steps agree,
both reach END (exit 0)**.  Direct-stdout self-host
`beauty.sno < beauty.sno` still bails at `mainErr2 Internal Error`
(md5 `b6873a89707f671133fae5e07b40942c`, 27 lines), but IPC harness
on the same input now reaches **step 2023** (was step 26 before
this session) — divergence at `case.inc:9 upr = REPLACE(upr,&LCASE,
&UCASE)` body during deferred-`*upr` call from match.inc:8 pattern.
Same shape family as SN-26-bridge-coverage-u (extra CALL during
pattern build) — to be addressed under SN-32b.

**Architecture reminder.**
```
.sno -> sno_parse() -> CODE_t* [LANG_SNO]
    --interp  -> execute_program() -> interp_eval()        ← session #57 byte-identical
    --interp  -> sm_lower() -> SM_Program -> sm_interp_run() ← SN-32 ladder
    --run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
                                                             ↑ shares sm_lower output
                                                               with --interp
```
SM and JIT bail identically because `sm_codegen` emits x86 from
the same SM_Program produced by `sm_lower`.  Fixing SM's
SM_Program correctness should fix JIT in lockstep, modulo a few
codegen-only sites (sm_codegen.c h_stno, etc.).

**Suspect surface (un-validated, for next-session triage):**
- `bb_boxes.c` `bb_userfn` / `bb_def` / `bb_cap` boxes — do they
  honour the build-vs-run distinction the IR path got via -t/-o
  (defer non-E_QLIT args as DT_E)?
- `sm_lower.c` lowering of `*fn(args)` deferred dot-star calls —
  does it produce a frozen DT_E for compound args, or does it
  emit eager calls?
- `sm_interp.c` lowering for E_INDIRECT (`$name = ...`) commits —
  the session #57 -y fix lived in `interp.c call_user_function`;
  no SM equivalent yet.
- `sm_interp.c` SM_STNO opcode — `g_sm_stno` linear counter,
  unchanged from the latent follow-up (won't fix the bail, but
  will affect downstream `&STNO` correctness once the bail is
  fixed).

**Sub-rungs:**
- [~] **SN-32a-wire-up** — *partial; landed session #58.* Mirrored IR's
  IPC fire-points into SM/JIT execution paths.  Specifically:
  - `sm_lower.c` emits `SM_STNO` with the source `s->stno` as
    operand (was a linear counter).  Mirrors IR-side
    SN-26-bridge-coverage-j fix.
  - `sm_lower.c` skips blank statements entirely (no SM_STNO, no
    body) so blanks don't bump `&STCOUNT` or fire LABEL on the
    wire — matches IR's `execute_program` empty-stmt path and
    SPITBOL's `stmgo` SIL.
  - `sm_interp.c` `SM_STNO` reads `ins->a[0].i` (source stno) and
    sets `kw_stno`; removed dead `g_sm_stno` linear counter.
  - `sm_codegen.c` `h_stno` reads `CUR_INS->a[0].i`; removed dead
    `g_sm_stno_jit` linear counter.
  - `sm_interp.c` IDX_SET handler fires `comm_var("<lval>", val)`
    after `subscript_set`/`subscript_set2`/`ITEM_SET` — matches
    SPITBOL's `asnpb` (aggregate-element store) wire fire-point
    (SN-26-bridge-coverage-g shape, on the SM side).
  - `sm_codegen.c` JIT IDX_SET handler: same `comm_var` fire-point.
  - New scripts `test_monitor_2way_spitbol_vs_sm.sh` and
    `test_monitor_2way_spitbol_vs_jit.sh`; the underlying
    `test_monitor_3way_sync_step_auto.sh` now honours
    `SCRIP_RUN_FLAG` (default `--interp`).
  - Plain-var stores already fire `comm_var` via the shared
    `NV_SET_fn` chokepoint — no SM/JIT change needed there.
  - CALL/RETURN during user-function execution already fire via
    `call_user_function`, which both IR and SM call into; CALL
    dispatch from SM/JIT goes through `INVOKE_fn` → eventually
    `call_user_function` → `comm_call`/`comm_return`.  No
    SM-specific plumbing needed.
  - **Verified**: `beauty.sno < /dev/null` IPC harness 1561 steps
    clean END under `--interp` and `--run`; tiny smoke
    probes (`p_def`, `p_loop`, `p_idx`, `p_upr`) all clean.
  - **Remaining work** (to close `-a`): if any deferred fire-point
    surfaces during SN-32b — e.g. NM_PTR/NM_CALL stores during
    pattern capture — mirror them on the SM lowering side.
- [x] **SN-32b-beauty-ipc** — *CLOSED session #60 (2026-04-28).*
  Two bugs in `sm_interp.c` `SM_STORE_VAR` fixed; `--interp beauty.sno
  < beauty.sno` now produces 646-line output md5
  `abfd19a7a834484a96e824851caee159` — byte-identical to SPITBOL oracle
  and to `--interp`.

  **Sub-rung-1 (session #59)** — bare `*fn(args)` all-E_VAR fast path
  discarding args — already recorded above.

  **Sub-rung-2 (session #60) — two SM_STORE_VAR bugs in `sm_interp.c`.**

  The 2-way IPC harness diverged at step 2552 with SPITBOL emitting
  `LABEL stno=1076` while scrip SM emitted `LABEL stno=1082` — 6 too
  high.  Reading the last-agree / first-disagree pair (RULES.md):
  the divergence was at `stack.inc:21  $'@S' = next($'@S') :(RETURN)`,
  immediately after `Pop()` returned a DATA value stored into `sno`, and
  `DIFFER(sno = Pop()) :F(mainErr2)` was evaluated.  The SM jumped to
  mainErr2 (stno=1082) when SPITBOL fell through to stno=1076 (correct).

  Root cause traced via `SCRIP_DIAG_JF` + `SCRIP_STEP_TRACE`:
  on the second call through the `DIFFER(sno = Pop())` expression,
  `SM_CALL "DIFFER" nargs=1 arg0.v=0` — DIFFER received DT_SNUL (null)
  not DT_DATA.  `SM_STORE_VAR "sno"` was called with val.v=100 (DT_DATA)
  but pushed stored.v=0 (DT_SNUL).  `NV_SET_fn("sno", DATA_val)` returns
  an unreliable SNUL on the second call for the same variable — the IR
  path (`interp.c E_ASSIGN:2844`) ignores NV_SET_fn's return and always
  returns the original `val`.  SM_STORE_VAR was using the return value.

  **Bug 1 — SM_STORE_VAR stack underrun when RHS is FAIL (SN-32b-store-fail):**
  When `Pop()` FRETURNs inside `DIFFER(sno = Pop())`, `SM_STORE_VAR`
  set `last_ok=0` and `break`ed WITHOUT pushing anything.  The enclosing
  `SM_CALL "DIFFER" 1` then popped a stale value from the stack, corrupting
  the arg and mis-setting `last_ok`.  Fix: push `FAILDESCR` before break
  so the stack stays balanced and FAIL propagates correctly to the
  enclosing call.

  **Bug 2 — SM_STORE_VAR pushes NV_SET_fn return instead of val (SN-32b-store-val):**
  `NV_SET_fn` returns unreliable values for DT_DATA objects.  The IR
  `E_ASSIGN` path always returns `val` (the RHS), not the NV_SET_fn
  result.  Fixed by storing via `NV_SET_fn(name, val)` then pushing `val`
  directly — matching the IR exactly.

  **Verification (session #60):**
  - `scrip --interp beauty.sno < beauty.sno` → 646 lines,
    md5 `abfd19a7a834484a96e824851caee159` ✓ byte-identical to SPITBOL.
  - IPC harness `beauty.sno < /dev/null` still reaches MWK_END at step
    1561 under `--interp` (no regression).
  - Smoke=7, Broker=49.

  **Files touched (session #60):**
  - `src/runtime/x86/sm_interp.c` `SM_STORE_VAR`:
    - Fail path: push FAILDESCR (stack balance fix).
    - Success path: push `val` not `NV_SET_fn` return (IR-parity fix).

- [x] **SN-32c-beauty-jit** — *CLOSED session #61 (2026-04-28).*
  `--run beauty.sno < beauty.sno` now produces 646-line output md5
  `abfd19a7a834484a96e824851caee159` — byte-identical to SPITBOL,
  to scrip --interp, and to scrip --interp.

  **Root cause:** `sm_codegen.c` `h_store_var` carried the same two
  `SM_STORE_VAR` bugs that session #60 fixed in `sm_interp.c`.  SM and
  JIT share `sm_lower`'s SM_Program output, but each backend has its
  own opcode handler for SM_STORE_VAR — sm_interp's `SM_STORE_VAR` case
  in the dispatch loop, sm_codegen's `h_store_var` static helper.  The
  -j → -32b → -32c bug pattern is therefore: any IR-side fix that
  touches NV_SET_fn return semantics or RHS-FAIL stack discipline must
  be mirrored in BOTH SM and JIT handlers.

  **Discovery — IPC harness divergence at step 2552:**
  ```
  step 2548  LABEL stno=278   stack.inc:21  $'@S' = next($'@S') :(RETURN)
  step 2549  VALUE @S = STRING(0)=''       (first store inside Pop body)
  step 2550  RETURN Pop                    (Pop returns)
  step 2551  spl: VALUE sno = UNKNOWN      scr: VALUE sno = DATA
  > 2552    spl: LABEL stno=1076           scr: LABEL stno=1082   ← DIVERGE
  ```
  Same shape as the SM-side step-2552 divergence in session #60:
  `DIFFER(sno = Pop()) :F(mainErr2)` — SPITBOL falls through to
  stno=1076 (DIFFER passed), JIT branches to stno=1082 (FAIL path
  taken because sno was stripped to SNUL between the assignment
  and the DIFFER check, since `h_store_var` pushed NV_SET_fn's
  unreliable DT_DATA return instead of the original DT_DATA `val`).

  **Fix (`runtime/x86/sm_codegen.c` `h_store_var`):** mirror the
  session #60 sm_interp.c fix exactly:
  - Fail path: push FAILDESCR (stack balance fix) — was bare `return`.
  - Success path: push `val` not `NV_SET_fn` return (IR-parity fix) —
    was `PUSH(stored)` where `stored = NV_SET_fn(...)`.

  **Verification (session #61):**
  - `scrip --run beauty.sno < beauty.sno` → 646 lines, md5
    `abfd19a7a834484a96e824851caee159` ✓ byte-identical to SPITBOL.
  - 2-way IPC harness on `beauty.sno < beauty.sno` (SPITBOL ⇄ scrip
    --run): advances to step 128068 before SPITBOL hits clean EOF
    (was DIVERGE at step 2552 before fix).  scrip continues emitting
    LABEL records past EOF — same end-of-program flow ordering noted
    in session #57 for IR-run, not a runtime semantic divergence.
  - 2-way IPC harness on `beauty.sno < /dev/null`: still reaches MWK_END
    at step 1561 under `--run` (no regression).
  - All three modes (`--interp`, `--interp`, `--run`) now produce
    byte-identical output to SPITBOL on the beauty self-host.
  - Smoke=7, Broker=49.

  **Files touched (session #61):**
  - `src/runtime/x86/sm_codegen.c` `h_store_var`:
    - Fail path: push FAILDESCR (stack balance fix, mirrors SN-32b-store-fail).
    - Success path: push `val` not `NV_SET_fn` return (mirrors SN-32b-store-val).

  **Lesson for future sessions.**  When a runtime-semantic bug is fixed
  in the IR path (`interp.c`), check both `sm_interp.c` AND
  `sm_codegen.c` for parallel implementations.  The three executors
  share `sm_lower` lowering output but each has its own opcode handler
  layer; bug fixes do not propagate automatically.

- [x] **SN-32d** — `--interp` md5 byte-identical confirmed session #60;
  `--run` md5 byte-identical confirmed session #61.  Both backend
  parity gates closed.

**Gate:** Smoke=7, Broker=49 after every commit.  Plus
`--interp` and `--run` md5 must approach
`abfd19a7a834484a96e824851caee159` as sub-rungs land.

**Cross-pollination (from PLAN.md):** SM/JIT fixes share lowering
infrastructure with Icon, Prolog, Raku, Snocone, Rebus.  Bug fixes
in `sm_lower.c`, `sm_interp.c`, `bb_boxes.c` benefit those goals
immediately.

---

**Session #57 (2026-04-28) — SN-26-bridge-coverage-y CLOSED.
Sharpened end-state target ACHIEVED.**

The GOAL-LANG-SNOBOL4.md sharpened end-state target — "Self-host
output md5 must match SPITBOL's `abfd19a7a834484a96e824851caee159`
byte-for-byte" — is now achieved.  scrip --interp on
`beauty.sno < beauty.sno` produces 646 lines of output that md5 to
`abfd19a7a834484a96e824851caee159`, byte-identical with SPITBOL
oracle's output.

The 2-way sync-step harness on `beauty.sno < beauty.sno` advances
from step 370,311 to **step 1,277,812** (+907,501 steps).  Steps
1..1,277,811 all agree.  The divergence at 1,277,812 is essentially
terminal: scrip emits `MWK_END` (clean termination) at stno=760
inside the user-function `pp_1` body while SPITBOL continues with
`LABEL stno=INT=1084` (the END statement of the program).  This is
end-of-program flow ordering — not a runtime semantic divergence.
scrip's output is complete and correct by this point.

**Two distinct bugs fixed this session, both in `interp.c`
`call_user_function`'s E_INDIRECT path:**

1. **Subject-resolution garbage on DT_N NAMEPTR.**  The branch at
   line 617 resolved `$name` (where `name` holds a DT_N parameter)
   by calling `VARVAL_fn(xv)` on the parameter value.  But
   `VARVAL_fn`'s DT_N case starts with `if (v.s) return
   GC_strdup(v.s);` — and for a NAMEPTR (slen=1, .ptr set), the
   union's `.s` slot reads pointer-bytes-as-string, yielding
   garbage like `\x01`.  The resulting `subj_name` was junk; the
   loop fell into the plain-assignment branch at line 668 which
   wrote to a junk-named variable instead of `snoBrackets`.  The
   wire then emitted `(none)` for the junk name.  Fix: discriminate
   on `IS_NAMEPTR(xv)` and use `NV_name_from_ptr(xv.ptr)` to recover
   the variable's real name.

2. **Missing comm_var on IS_NAMEPTR write paths.**  Even when the
   E_INDIRECT branch at line 770 was reached, the IS_NAMEPTR fast
   paths wrote through the pointer with bare
   `*(DESCR_t*)ind_val.ptr = repl_val;` — no `comm_var` call.  Same
   shape as the session-#55 NM_PTR/NM_CALL fix in `name_t.c`.  Fix:
   emit `comm_var(NV_name_from_ptr(...) ?: "<lval>", repl_val)`
   after each IS_NAMEPTR write.

**Diagnostic technique used.**  `getenv("DBG_INDIR")` printf at the
E_INDIRECT subject-resolution branch and at the IS_NAMEPTR write
sites.  The trace immediately showed `xv.v=9 xv.slen=1` (DT_N
NAMEPTR) but `xv.s=\u0001` and `subj_name resolved to: \u0001` —
pinpointing `VARVAL_fn`'s union-aliasing as the source of the
garbage.  This also revealed that the line-770 E_INDIRECT branch
**was never reached** in the failing case — `subj_name` got set
early at line 622-628 and the plain-assignment branch swallowed
the assignment.  Diagnostic prints reverted before commit per
RULES.md.

**Verification:**
- 2-way harness on `beauty.sno < beauty.sno`: advances 370311 →
  1277812 (+907501 steps).  Divergence at 1277812 is the terminal
  MWK_END ordering (scrip emits MWK_END, SPITBOL emits one more
  LABEL for the program's END statement).
- 2-way harness on `beauty.sno < /dev/null`: still terminates at
  step 1560 (no regression).
- Self-host output: scrip's stdout filtered for `****` ftrace
  prefix lines is 646 lines, md5
  `abfd19a7a834484a96e824851caee159` — byte-identical to SPITBOL.
  `diff -q` returns identical.
- Smoke=7, Broker=49 preserved.
- Probes: `assign2(.snoBrackets, '()')` with `$name = val` body
  and `pat . *assign(.snoBrackets, EVAL("..."))` with full
  assign.inc body both match SPITBOL byte-for-byte.

**Files touched (session #57):**
- `src/driver/interp.c`:
  - `call_user_function` E_INDIRECT subject-resolution branch
    (~line 617): handle DT_N NAMEPTR / NAMEVAL via
    `NV_name_from_ptr` before falling back to `VARVAL_fn`
  - `call_user_function` E_INDIRECT assign branch (~line 770):
    emit `comm_var` after both IS_NAMEPTR direct-write paths
- `.github/GOAL-LANG-SNOBOL4.md` (-y closed; -h closed; HEADs and
  Current state updated; this session #57 narrative)
- `.github/PLAN.md` (step → SN-26-bridge-coverage-z, post-MWK_END
  label ordering, non-gating)

**Lesson for future sessions.**  When scrip emits a wrong /
empty / placeholder name on the wire, the bug may not be in the
fire-point itself but in upstream name resolution.  Garbage from
`VARVAL_fn` on a DT_N NAMEPTR (where `.s` reads pointer bytes via
union) is silent — it produces a syntactically valid-looking string
and the assignment proceeds quietly into the wrong cell.  When
investigating a `(none)` or junk-name wire emission, trace the
path from the source identifier all the way to the `comm_var`
call site and check each transformation.  Specifically: any
`VARVAL_fn` call on a value that could be a DT_N NAMEPTR is
suspect — audit `interp.c` for other sites with the same pattern.

**Gates.**  Smoke=7, Broker=49.

**Next session resume.**
- The sharpened end-state target is achieved.  Future work on this
  goal can either (a) close the residual MWK_END label-ordering
  divergence at step 1277812 (open as -z if desired), or (b) pivot
  to the broader corpus parity goals (SN-29f canonical .ref capture,
  SN-30f regression sweep under new sbl).
- -r remains independent and can land any session.
- The latent SM/JIT linear-stno parity follow-up (extend `SM_STNO`
  to take a source-stno operand) is also open whenever a Goal needs
  SM/JIT &STNO correctness on backward gotos.

---

**Session #56 (2026-04-28) — SN-26-bridge-coverage-x CLOSED.**

**One sub-rung landed.**  The 2-way harness on
`beauty.sno < beauty.sno` advances from step 22857 to **step 370311**
(+347454 steps) — one of the largest single-rung advances on this
ladder.  All on the scrip side; no SPITBOL or csnobol4 changes
needed.

**Root cause.**  scrip's value-context concatenation (`CONCAT_fn`
in `runtime/x86/snobol4.c`) unconditionally stringified both
operands.  SPITBOL's SIL `CONCAT` short-circuits when either
operand is null/empty: returns the OTHER operand verbatim,
preserving its type.  This is observable on a 7-line probe:

| expression  | SPITBOL          | scrip (pre-fix)   | scrip (post-fix) |
|-------------|------------------|-------------------|------------------|
| `'' 2`      | INTEGER 2        | STRING "2"        | INTEGER 2        |
| `2 ''`      | INTEGER 2        | STRING "2"        | INTEGER 2        |
| `'' 2.5`    | REAL 2.5         | STRING "2.5"      | REAL 2.5         |
| `'' ''`     | STRING ""        | STRING ""         | STRING ""        |
| `'a' 2`     | STRING "a2"      | STRING "a2"       | STRING "a2"      |
| `2 'a'`     | STRING "2a"      | STRING "2a"       | STRING "2a"      |
| `'' 0`      | INTEGER 0        | STRING "0"        | INTEGER 0        |

**How the divergence surfaced.**  beauty.sno:128, 130 build
patterns like `("'|'" & '*(GT(nTop(), 1) nTop())')` where `&`
is OPSYN'd to `reduce`, and the second arg is the string
`'*(GT(nTop(),1) nTop())'`.  reduce body
(`semantic.inc:17`) does:
```snobol4
reduce  reduce = EVAL("epsilon . *Reduce(" t ", " n ")") :(RETURN)
```
producing a deferred pattern `epsilon . *Reduce('|', *(GT(nTop(),1)
nTop()))`.  scrip's lowerer freezes the second arg of `*Reduce`
as a DT_E pointing at the E_DEFER node.  At pattern-match time,
NM_CALL thaws this DT_E one level — yielding another DT_E
pointing at the inner E_SEQ `[GT(nTop(),1), nTop()]` — and binds
it to parameter `n`.

Inside `Reduce(t,n)` (`ShiftReduce.inc:23-24`):
```snobol4
Reduce0  IDENT(DATATYPE(n), 'EXPRESSION')  :F(Reduce1)
         n   =   EVAL(n)                    :F(NRETURN)
```
DATATYPE(DT_E) → `'EXPRESSION'`, IDENT succeeds, so we fall
through to `n = EVAL(n)`.  EVAL_fn re-thaws the DT_E into the
E_SEQ, evaluates: child[0] = `GT(nTop(),1)` returns NULVCL
(success), child[1] = `nTop()` returns INT 2.  Then
`CONCAT_fn(NULVCL, INT 2)` ran — and (pre-fix) returned
`STRVAL("2")`.  The resulting `n = "2"` then fired comm_var with
DT_S, diverging from SPITBOL's INT 2.  Step 22857 is the first
beauty path that hits this CONCAT shape with a numeric operand.

**Diagnostic technique that worked.**
1. `__builtin_trap()` in `comm_var` gated on
   `name=="n" && val.v==DT_S && val.s=="2"` — the divergence's
   exact wire shape.  Run `gdb -batch ... -ex "bt 40"`; backtrace
   landed at `interp.c:722 set_and_trace("n", repl_val)` —
   confirming the bad value was inside Reduce body's `n = EVAL(n)`
   statement, not at param-binding time.
2. `DBG_REDUCE_X` log in EVAL_fn's DT_E branch printed
   `ekind` + `sval` of the thawed EXPR_t.  The trap's preceding
   trace line was
   `EVAL_fn(DT_E ekind=19 [E_SEQ]) -> v=1 s="2"` —
   pinpointing E_SEQ's CONCAT_fn return as the type-loss site.
3. 7-line probe `probe_concat2.sno` covering both directions and
   edge cases (null+INT, null+REAL, INT+null, etc.) confirmed
   the issue is symmetric and non-numeric (STRING+STRING)
   stringification was unaffected — informing the symmetric
   `IS_NULL_fn(a)` / `IS_NULL_fn(b)` short-circuit shape.

**Probe-isolation lesson (matches session #50/#54).**  An earlier
isolated probe of `pat = ("'X'" & 'nTop()')` AGREED between
SPITBOL and scrip — the call shape itself was correct.  The bug
required CONCAT inside an EVAL'd E_SEQ inside a deferred
sub-pattern call.  The minimal trigger is just `'' 2` though;
once the trap+gdb pinpointed CONCAT_fn as the site, the probe
narrowed to the simplest possible repro.

**Verification.**
- 2-way harness on `beauty.sno < beauty.sno`: 22857 → 370311
  (+347454 steps).  Steps 1..370310 all agree.  New divergence
  at 370311 is `assign.inc:11 $name = EVAL(expression)` —
  scrip's bridge emits `(none)` for the indirect-assign target
  name where SPITBOL emits the recovered name (`snoBrackets`).
  Different bug class; tracked as -y.
- 2-way harness on `beauty.sno < /dev/null`: still terminates
  cleanly at step 1560 (`:F(END)` end-of-input — no regression).
- Smoke=7, Broker=49 preserved.
- Probe `probe_concat2.sno`: matches SPITBOL byte-for-byte on all
  7 cases.
- Beauty self-host md5 unchanged
  (scrip `dc2e07f20a1f0dbe8e473aa65edb0ce6` vs SPITBOL
  `abfd19a7a834484a96e824851caee159`); the 544-line textual diff
  is downstream of -y and likely shrinks once that lands.

**Files touched (session #56).**
- `src/runtime/x86/snobol4.c` (`CONCAT_fn`: null operand →
  return other side; preserves INT/REAL type through null+numeric
  concat)
- `.github/GOAL-LANG-SNOBOL4.md` (-x closed; -y opened; HEADs
  updated; this session-#56 narrative)
- `.github/PLAN.md` (step → SN-26-bridge-coverage-y)

**Gates.**  Smoke=7, Broker=49.

**Next session resume.**
- Active step is SN-26-bridge-coverage-y.  Investigate
  `assign.inc:11 $name = EVAL(expression) :(NRETURN)` —
  scrip emits `(none)` instead of the recovered `name` value
  (`snoBrackets` in the failing case).
- Likely site: scrip's `E_INDIRECT` lvalue commit path at
  `interp.c` E_ASSIGN E_INDIRECT subbranch (around line 700-735)
  or the corresponding eval_node case in
  `eval_code.c:194-211` E_ASSIGN.  Check how the recovered
  variable name (after `sno_fold_name`) gets passed to
  `comm_var` — current code likely either (a) fires `comm_var`
  with the wrong name, or (b) fires it with no name at all and
  scrip's bridge emits the placeholder `(none)`.
- Other open rungs unchanged: -r (SPITBOL block-type
  discrimination, independent), -h (essentially satisfied —
  close after -y lands).

---

**Session #55 (2026-04-28) — SN-26-bridge-coverage-q/-v/-w CLOSED.**

Three sub-rungs landed in a single session, advancing the 2-way
harness from step 1565 to step 22857 (+21292 steps) on
`beauty.sno < beauty.sno`.  All three were on the scrip side; no
SPITBOL or csnobol4 changes needed.  The original `-q` block's
architectural sketch (kvabe keyword fire-point at asg14/asg15) was
not actually the root cause of the step-1565 divergence — the real
cause was OUTPUT/TERMINAL trap symmetry, a different SIL path that
the goal-file block didn't anticipate.

**-q (OUTPUT/TERMINAL trap symmetry).**  At step 1565, beauty.sno:612
`OUTPUT = snoLine :(main00)` made scrip emit `VALUE OUTPUT = STRING(...)`
while SPITBOL was silent.  Tracing SPITBOL's `asign` procedure
(`sbl.min:17611-17733`) showed OUTPUT is a natural variable with an
output-association trblk (`trtou`); at `asg06` the trblk-walk finds
that entry and jumps to `asg10`, which writes the value via `sysou`
and `exi`s without ever reaching `b_vrs` — so `sysmv` never fires.
scrip's `NV_SET_fn` was firing `comm_var` for OUTPUT, TERMINAL, and
channel-bound output writes, which are I/O operations that
incidentally use variable-assignment syntax, not real variable
stores.  Fix: removed `comm_var` from those three return paths in
`runtime/x86/snobol4.c` `NV_SET_fn`.

**-v (pattern-capture store-back fire-points).**  After -q, the
divergence at step 1619 was `VALUE dummy = STRING(0)=''` after a
NRETURN.  PushCounter does `PushCounter = .dummy :(NRETURN)`; the
caller's pattern `*PushCounter()` later commits the matched text
into the cell that DT_N points at.  scrip's `name_commit_value`
NM_PTR and NM_CALL paths just did `*var_ptr = value` / `*cell =
value` silently.  At step 1622 a similar issue surfaced for DATA
field stores via `value($'#N') = value($'#N') + 1`
(counter.inc:18).  SPITBOL's `asinp` (sbl.min:17880-17904) fires
`sysmv`/`sysmw` on these cases via the asnpa (real vrblk → name)
and asnpb (aggregate → `<lval>`) split.  Fix: three sites added
`comm_var` post-store in scrip:
- `name_t.c` NM_PTR: `comm_var(NV_name_from_ptr(var_ptr) ?: "<lval>", value)`
- `name_t.c` NM_CALL: same pattern after `*cell = value`
- `interp.c` ~line 750 (top-level FIELD_SET): `comm_var("<lval>", rv)`
NV_name_from_ptr reverse-walks the global NV hash table to recover
the variable's name from its cell address.

**-w (NULL vs empty-string wire-type symmetry).**  Step 1867 had
both runtimes emitting `VALUE @S = ...` with empty value bytes,
but SPITBOL tagged it `STRING(0)=''` while scrip tagged it `NULL`.
Cause: SPITBOL stores SNOBOL4's NULL as the global `nulls` empty
scblk; `spl_block_to_wire` matches it as `TYPE_SCL` and emits
`MWT_STRING` with `vlen=0`.  scrip's `scrip_tag_to_wire` mapped
`DT_SNUL` to `MWT_NULL` — semantically equivalent but
wire-different.  Fix: changed `DT_SNUL` mapping to `MWT_STRING` so
empty/NULL values emit the same wire type on both sides.  This
unlocked an enormous run of agreement: harness advanced from 1867
to 22857 (+20990 steps) before next divergence.

**Verification (session #55):**
- 2-way harness on `beauty.sno < beauty.sno`: 1565 → 22857
  (+21292 steps).  Steps 1..22856 all agree.
- 2-way harness on `beauty.sno < /dev/null`: still terminates at
  step 1560 (`:F(END)` end-of-input — essentially terminal, no
  regression).
- Smoke=7, Broker=49 preserved.
- All 5 buildable SN-26 bridge smokes PASS (3 SKIP for missing
  csnobol4 — expected per oracle pivot).
- Self-host outputs both produce 646 lines on `beauty < beauty`.
  md5s differ (SPITBOL `abfd19a7a834484a96e824851caee159` vs scrip
  `dc2e07f20a1f0dbe8e473aa65edb0ce6`); ~544 lines of textual diff
  remain — mostly scrip dropping `:(label)` goto-suffixes on
  certain stmt forms in beauty's beautification path.  These are
  real semantic divergences surfaced by the harness past 22857;
  they will be addressed by -x and follow-on rungs.

**Files touched (session #55):**
- `src/runtime/x86/snobol4.c` (NV_SET_fn channel-bound /
  OUTPUT / TERMINAL paths: removed `comm_var`; `scrip_tag_to_wire`
  DT_SNUL → MWT_STRING)
- `src/runtime/x86/name_t.c` (NM_PTR + NM_CALL fire `comm_var`
  with NV_name_from_ptr recovery and `<lval>` fallback)
- `src/driver/interp.c` (top-level FIELD_SET path fires
  `comm_var("<lval>", rv)`)
- `.github/GOAL-LANG-SNOBOL4.md` (-q/-v/-w closed; -x opened;
  HEADs and Current state updated)
- `.github/PLAN.md` (step → SN-26-bridge-coverage-x)

**Gates:** Smoke=7, Broker=49.

**Next session resume:**
- Active step is -x: investigate the `n=INT vs n=STRING` wire-type
  asymmetry at step 22857.  Reduce to a probe — `reduce("'='", 2)`
  is the simplest call shape (beauty.sno line 125+) where `n` is
  bound as INTEGER 2.  Compare scrip's NV cell for `n` against
  SPITBOL's at the same call boundary using the `__builtin_trap`
  + gdb backtrace pattern from session #53.
- After -x lands, re-run the harness; the actual self-host output
  diff (544 lines as of session #55) should shrink as the
  upstream wire divergences resolve.
- -r remains independent (SPITBOL pattern/name/array/table
  discrimination); can land any session.
- -h is essentially satisfied — close it after -x lands and run
  one final harness pass to capture the final divergence point
  (or clean MWK_END).

---

**Session #54 (2026-04-28) — SN-26-bridge-coverage-u CLOSED.**

The "extra CALL upr at step 1507" turned out to be a generic
double-evaluation in `interp.c` E_CAT/E_SEQ mid-loop pattern
promotion, not specific to the `icase = icase (...)` self-concat
shape or the `.`-captured `letter` variable.  Probe-narrowing
(`p1..p9` in `/home/claude/probe_u/`) showed the bug fires on any
non-pattern LHS concatenated with a pattern operand containing
function calls.  The two parenthesized E_ALT shapes (`a = upr|lwr`
and `b = (upr|lwr)`) both agreed with SPITBOL, but `'X' (upr|lwr)`
and `letter (upr|lwr)` both diverged with the double-call.

**Root cause (interp.c E_CAT/E_SEQ ~line 2722):** when value-mode
evaluation of children[i] returned DT_P (typically because the
child was an E_ALT, which calls `interp_eval_pat` internally and
fires inner functions once during build), the mid-loop promotion
path threw that valid `nxt` away and called `interp_eval_pat` on
it again — calling the inner functions a second time.  It also
re-evaluated prior children 0..i-1, which would double-call any
functions among them as well; in the observed cases prior children
were plain scalars so that aspect was latent.

The original justification for the re-evaluation (comment at the
old line 2722-2727) was "without this, `*term integer` produces
DT_E for `*term` in value ctx, then hits pat_cat when integer
arrives".  But `*term` is E_DEFER, which makes `has_defer = 1` in
the pre-scan above, which makes the loop start in pat_mode from
child[0] — the mid-promotion path doesn't fire at all in that case.
So the re-evaluation was never necessary; it was the bug.

**Fix:** keep `nxt` as-is when promoting; don't re-evaluate prior
children either.  `pat_cat` calls `pat_to_patnd` which coerces
DT_S/DT_I/DT_R/DT_SNUL to literal patterns — so prior `acc` values
work correctly without re-eval.  E_DEFER among prior children is
already prevented by `has_defer` pre-scan starting the whole loop
in pat_mode.

**Verification:**
- 9 probes match SPITBOL byte-for-byte (was 4× call counts in scrip
  for shapes p1, p2, p6, p8c, p8d before fix; 2× after fix matches
  oracle).
- Smoke=7, Broker=49 preserved.
- All 5 buildable SN-26 bridge smokes PASS (3 SKIP for missing
  csnobol4 — expected per oracle pivot).
- 2-way harness on `beauty.sno < /dev/null`: advances from step 1507
  to step 1560 (+53 steps).  New divergence at 1560 is the `:F(END)`
  end-of-input flow on /dev/null — different bug class, essentially
  terminal.
- 2-way harness on `beauty.sno < beauty.sno`: advances to step 1565.
  New divergence is the `OUTPUT = snoLine` line (beauty.sno:612):
  scrip emits a VALUE record on the OUTPUT keyword-assignment,
  SPITBOL is silent (next emission is a LABEL).  This is the open
  -q sub-rung exactly (SPITBOL keyword-assignment fire-point missing).

**Files touched (session #54):**
- `src/driver/interp.c` (~line 2722: removed `nxt` and prior-child
  re-evaluation in mid-loop pat promotion; added explanatory comment
  pointing at SN-26-bridge-coverage-u)
- `.github/GOAL-LANG-SNOBOL4.md` (-u closed; HEADs updated; session
  #54 narrative)
- `.github/PLAN.md` (step updated to -h)

**Gates:** Smoke=7, Broker=49.

**Next session resume:**
- Active step is now -h (apples-to-apples on beauty, 2-way).  -u
  was the last semantic-runtime divergence.  Remaining symptoms
  reachable via -h are: -q (OUTPUT keyword fire-point on SPITBOL
  bridge), and end-of-input flow which is essentially terminal.
- Landing -q is straightforward: SPITBOL has the asign/asg14/asg15
  keyword-assignment path; add a `sysmkw` fire-point analogous to
  the existing `sysmv`/`sysmw` work from -b/-l.  See -q block
  earlier in this file for the architectural sketch.
- After -q lands, re-run the 2-way harness and document where the
  new first divergence falls.  If it's truly inside END/EOF flow,
  -h closes by inspection and the goal pivots to broader corpus
  parity (SN-29f canonical .ref capture, SN-30f regression sweep).

**Lesson for future sessions.**  When a bug "specific to" some
elaborate source shape (right-recursive self-concat, .-captured
variable, etc.) is reduced through aggressive probe narrowing,
look at what the simpler probes can still trigger.  Both the
self-concat and the .-capture turned out to be irrelevant to the
actual bug; the trigger was just "non-pattern LHS + alternation
with fn calls".  The narrative trail in -u (sessions #43–#53
descriptions) led with the symptom shape, which is a natural
starting point but rarely the whole story.

---

**Session #53 (2026-04-28) — SN-26-bridge-coverage-t/-o CLOSED;
-u opened.**

The eager `nTop` call traced via gdb originated from compound-arg
expressions in `pat . *fn(args)` deferred-function targets.  The
deferral loop at `interp.c:3210` (and twin at 3243) only wrapped
args as `DT_E` when their top-level kind was `E_FNC` or `E_VAR`;
compound expressions like `nTop() + 1` (E_ADD wrapping E_FNC) fell
into the `else` branch and were eagerly evaluated.

**Discovery surprise:** the FIRST eager call was NOT from line 121
(wrapped form `*(GT(nTop(), 1) nTop())`) as session #50 hypothesized,
but from a later bare-arg `*Reduce(t, nTop() + 1)` call.  This is why
session #50's isolated probes matched SPITBOL — they tested the
wrapped form, which was already correct.

**Fix:** at both sites in `interp.c`, defer all non-`E_QLIT` args as
`DT_E`.  The thaw at `name_t.c:97` already handles arbitrary
`EXPR_t` shapes via `EVAL_fn → EXPVAL_fn`, so no thaw-side change
needed.  `E_QLIT` (string literals) stay eager since they are
idempotent under EVAL.

**Verification:**
- Probe `pat . *Reduce('[]', nTop() + 1)`: scrip output matches
  SPITBOL byte-for-byte after fix.
- 2-way harness on `beauty.sno < /dev/null`: step 1257 → step 1507
  (+250 steps).  All steps 1..1506 agree.
- Smoke=7, Broker=49 preserved.
- All 5 buildable bridge smokes PASS (3 SKIP for missing csnobol4 —
  expected per oracle pivot).

**New divergence at step 1507** is a different bug class — `case.inc:23
icase = icase (upr(letter) | lwr(letter))`.  spl emits `VALUE icase =
UNKNOWN` (pattern stored), scr emits `CALL upr` (extra eager call).
Plain `pat = upr('A') | lwr('B')` agrees byte-for-byte, so the bug
involves either the `icase = icase (...)` self-concat shape, the
`.`-captured `letter` variable interaction, or both.  Tracked as -u.

**Files touched (session #53):**
- `src/driver/interp.c` (~line 3210 and ~line 3243: defer all non-E_QLIT
  args in E_CAPT_COND_ASGN sub-arg loop)
- `.github/GOAL-LANG-SNOBOL4.md` (-t/-o closed, -u opened, state updated)
- `.github/PLAN.md` (step updated to -u)

**Gates:** Smoke=7, Broker=49.

**Next session resume:**
- Reduce step 1507 to a probe.  Start from
  `icase = icase (upr(letter) | lwr(letter))` with `letter` being a
  `.`-captured variable from a prior pattern match.  If probe matches
  SPITBOL byte-for-byte, narrow until it diverges.
- Suspect: `interp_eval E_CONCAT` re-walks the RHS pattern when LHS
  is also a pattern (concatenating two patterns into one).
- -r (SPITBOL pattern type) and -q (keyword-assignment fire-point)
  remain independent and can land same session.

**Session #52 (2026-04-28) — sub-rungs -r/-s/-t added; -s closed; grid with source.**

1. **DIVERGE grid now renders as markdown table** with source column.
   `monitor_sync_bin.py` builds stno→source map inline at startup from
   `MONITOR_SNO_FILE` + `MONITOR_INC_DIR` env vars (pure Python, no sidecar,
   no subprocess). Grid: `| step | stno | spl | scr | source |`.

2. **-s closed:** RETURN record display changed from `RETURN fname =
   STRING(6)='RETURN'` to `RETURN fname (RETURN)` — parentheses make clear
   it is the return kind, not a value assignment.

3. **New sub-rungs:**
   - **-r** (open): SPITBOL pattern/name/array/table block discrimination.
     `spl_block_to_wire` returns `MWT_UNKNOWN` for all non-scalar blocks.
     Fix: add `b_p0l/b_p1l/b_p2l/b_nml/b_arl/b_tbl` externs to `osint.h`
     and discriminate in `spl_block_to_wire`. Unblocks `VALUE nPush =
     PATTERN` matching between spl and scr.
   - **-s** (closed this session): RETURN display fix (above).
   - **-t** (open, active): find eager nTop caller. Trap in `comm_call`
     when `fname=="nTop"`, run `scrip --interp beauty.sno < /dev/null`
     under gdb. Backtrace shows exact C path causing eager nTop evaluation
     inside `reduce = EVAL("epsilon . *Reduce(" t ", " n ")")` at stno=589.

**Active step: SN-26-bridge-coverage-t.**

**Next session resume:**
- Implement -t diagnostic: add `if (strcmp(fname,"nTop")==0) __builtin_trap();`
  in `comm_call` (interp.c or snobol4.c — wherever comm_call is defined),
  rebuild scrip, run under gdb `--interp beauty.sno < /dev/null`.
- Do NOT commit the trap. Read the backtrace, identify the call site, fix
  the eager-evaluation bug, revert the trap, commit the fix.
- After -t lands, run the 2-way harness — expect to advance past step 1257.
- -r (SPITBOL pattern type) is independent and can land same session.

**Files touched (session #52):**
- `scripts/monitor/monitor_sync_bin.py` (markdown grid, source col, RETURN fmt)
- `scripts/test_monitor_3way_sync_step_auto.sh` (pass MONITOR_SNO_FILE/INC_DIR)
- `.github/GOAL-LANG-SNOBOL4.md` (sub-rungs -r/-s/-t; -s closed; state updated)
- `.github/PLAN.md` (step updated to -t)

**Gates:** Smoke=7, Broker=49.

**Session #51 (2026-04-28) — SN-26-bridge-coverage-p closed.**

Two improvements to `monitor_sync_bin.py`:

1. **Interleaved trail on by default.**  Per-participant separate history
   deques replaced by a single interleaved `deque(maxlen=DIVERGE_HISTORY)`
   of `(step, stno, line)` tuples.  `DIVERGE_HISTORY` now reads
   `MONITOR_LAST_AGREE_TRAIL` env var at startup (default 5, min 1).
   On DIVERGE: interleaved trail prints first (most-recent last), then
   per-participant divergence record.

2. **stno annotation.**  `fmt_event` accepts `stno=` kwarg.  Controller
   tracks `last_agreed_stno` from LABEL records; passes to `fmt_event`
   for VALUE/CALL/RETURN display.  Format: `@589 VALUE reduce = UNKNOWN`.

**Verified divergence output:**
```
[ctrl] last 5 agreed steps (most recent last):
  step 1252: LABEL stno=INT=591
  step 1253: @591 VALUE nPush = UNKNOWN
  step 1254: @591 RETURN nPush = STRING(6)='RETURN'
  step 1255: @591 CALL reduce
  step 1256: LABEL stno=INT=589
[ctrl] DIVERGE step 1257
[ctrl] divergence record:
  spl #1257: @589 VALUE reduce = UNKNOWN
  scr #1257: @589 CALL nTop
```

**Reading the divergence:**
- stno=591 = semantic.inc line 20: `nPush  nPush = epsilon . *PushCounter()  :(RETURN)`
- stno=589 = semantic.inc line 17: `reduce  reduce = EVAL("epsilon . *Reduce(" t ", " n ")")  :(RETURN)`
- SPITBOL at step 1257: stores result of EVAL into `reduce` (UNKNOWN type = pattern)
- scrip at step 1257: calls `nTop()` — eager call inside EVAL argument construction

**Two new sub-rungs added:** -p (closed this session) and -q (SPITBOL
keyword-assignment fire-point; `&FULLSCAN=1` etc. not captured by spl bridge).

**Files touched (session #51):**
- `scripts/monitor/monitor_sync_bin.py` (interleaved trail, stno annotation)
- `.github/GOAL-LANG-SNOBOL4.md` (sub-rungs -p, -q added; -p closed)

**Gates:** Smoke=7, Broker=49.

**Next session resume hint:**
- Divergence is clear: scrip calls `nTop()` at step 1257 inside
  `reduce = EVAL("epsilon . *Reduce(" t ", " n ")")`.
- SPITBOL does NOT call nTop at this step — it just stores the EVAL result.
- Per session #50 audit: `_eval_pat_impl_fn` is NOT the eager-eval source.
- Next: instrument `EVAL_fn` to log the parsed tree of the FIRST reduce call
  (stno=589 match). If scrip's tree contains a live E_FNC node for nTop
  where SPITBOL's tree has a deferred E_DEFER, the bug is in how the EVAL
  string is parsed (parse_expr_pat_from_str). If trees match, bug is in
  tree evaluation order (the 5-phase parity issue noted in session #50 is
  a candidate: replacement evaluated before match in scrip).
- Consider landing the 5-phase fix as SN-26-bridge-coverage-p2 — it may
  shift this divergence upstream.
- corpus @ unchanged
- x64 @ unchanged
- csnobol4 @ `1d225f8` (managed by GOAL-CSN-FENCE-FIX from now on)
- active step → SN-26-bridge-coverage-o (extra CALL during
  EVAL/argument evaluation; surfaces at step 1257 of 2-way harness
  on beauty.sno).  At that step SPITBOL emits `VALUE reduce = UNKNOWN`
  (the body's `reduce = EVAL(...)` assignment inside reduce/&'s
  body) while scrip emits `CALL nTop` — scrip is making an extra
  call during EVAL/argument evaluation that SPITBOL isn't.  Likely
  the pattern build-vs-run distinction: SPITBOL builds the
  `*Reduce(...)` deferred sub-pattern without invoking the inner
  functions; scrip evaluates eagerly.  See -o for repro and
  diagnostic plan.  -n CLOSED session #49: stack of five distinct
  bridge-emission alignment bugs in scrip's function-call path
  (comm_call ordering, monitor_quiet_depth gate, function-body
  LABEL coverage, RETURN payload shape, OPSYN canonical names).
  Harness advanced 222 steps.
  -m CLOSED session #48; -l CLOSED session #45; -k CLOSED session #44;
  -j CLOSED session #46; -g CLOSED session #43;
  -i lifted to GOAL-CSN-FENCE-FIX; -h unblocked once -o lands.

**Session #50 (2026-04-28) — SN-26-bridge-coverage-o investigation;
`end`-label `strcasecmp` fix landed; 5-phase audit.**

Two findings this session:

1. **Bug fixed (independent of -o): `end` label treated as program
   terminator.**  `src/frontend/snobol4/snobol4.y:247` used
   `strcasecmp(lbl.sval,"END")==0` to detect the program terminator,
   so a user label spelled `end`, `End`, `eNd`, etc. caused scrip
   to terminate the program at that label.  Per RULES.md "Always
   uppercase `END`" and the casing-at-ingress rule, the comparison
   must be case-sensitive.  Minimal repro: `DEFINE('f') :(end)` with
   a body label `f` and a skip-target label `end` — SPITBOL prints
   the post-`end` statement, scrip silently exits 0.  Fix: change
   `strcasecmp` → `strcmp`.  Regenerate parser via
   `regenerate_parser_and_lexer_from_sources.sh`.  Smoke=7,
   Broker=49, harness still diverges at step 1257 (no regression on
   the active rung).

2. **5-phase statement-execution audit (answers a question raised
   this session, no fix landed):** scrip's `execute_program` (~L4310)
   and `call_user_function` (~L600 — a parallel implementation of
   the same logic) evaluate statement parts in this order:
   subject → pattern → **replacement (before match)** → match → replace.
   Classical SNOBOL4 (Green Book §1.7 / SIL) requires:
   subject → pattern → match → replacement → replace, where the
   replacement evaluates **only on match success** and **after** the
   match.  The eager-replacement order means (a) replacement side
   effects fire even when the match would fail, and (b) the
   replacement cannot reference variables set by `.` captures during
   the same match.  Two parallel implementations of the same
   statement-execution logic also violate the spirit of "single
   source of truth".  Tracked as a latent follow-up under SN-26
   ("scrip 5-phase parity") — not immediately gating -o.  Fixing
   this could shift the divergence either upstream (closer to root)
   or further downstream (different bug class).

3. **-o progress: cause not yet pinpointed.**  Diagnostic patches
   (DBG_EVAL_PAT in `_eval_pat_impl_fn`, DBG_FNC in `interp_eval`
   E_FNC, DBG_EXEC at `exec_stmt` entry, DBG_EVAL at `EVAL_fn`
   entry) confirmed:
   - `_eval_pat_impl_fn` is **not** called during beauty's run;
     ruling out the DT_P-at-EVAL_fn path as the eager-call source.
   - `exec_stmt` is called only 19 times during the harness window,
     all on stno=2..21 (`&ALPHABET POS(N) LEN(1) . xxx` init).  The
     eager `nTop` does not happen via `exec_stmt`.
   - DBG_EVAL captured the actual EVAL'd strings.  Beauty calls
     `reduce` with two argument shapes:
     - **`*(...)` wrapped:** `epsilon . *Reduce('snoExprList', *(GT(nTop(), 1) nTop()))` — args fully deferred.  This is the FIRST reduce call (line 121, beauty stno that maps to harness step 1257).
     - **bare arg:** `epsilon . *Reduce('[]', nTop() + 1)` (line 169), `epsilon . *Reduce(',', nTop() + 1)` (line 177), `epsilon . *Reduce('snoParse', nTop())` (lines 238, 243).  These have NO `*(...)` wrap on the second arg.
   - All probes that mirror the FIRST reduce-call's tree shape in
     isolation (using full beauty-style DEFINE chain) correctly
     defer all inner functions in scrip.  No eager nTop fires.
     The bug requires additional state from beauty's run that the
     probes have not captured.

4. **Source mapping for the divergence (so a future session does
   not re-discover):**
   ```
   step 1252  LABEL stno=591   → semantic.inc:20  nPush body
   step 1253  VALUE nPush      → same line (UNKNOWN vs PATTERN — wire-typing diff, pre-existing)
   step 1254  RETURN nPush     → same line, RTNTYPE='RETURN'
   step 1255  CALL reduce      → entering reduce body (line 121 call site)
   step 1256  LABEL stno=589   → semantic.inc:17  reduce body
   step 1257  spl: VALUE reduce = UNKNOWN  (RHS done, store)
              scr: CALL nTop                (eager call inside RHS)
   ```
   Beauty source for stno=589: `reduce  reduce = EVAL("epsilon . *Reduce(" t ", " n ")")  :(RETURN)`.

5. **scrip's `&STNO` is wrong inside function bodies (latent).**
   `call_user_function` (~L605) fires `mon_emit_label_bin(s->stno)`
   for the body line but does **not** update `kw_stno`.  So `&STNO`
   reads as the caller's stno during body execution.  The harness
   wire is unaffected (uses `mon_emit_label_bin` directly), but
   ftrace `****N` prefixes show stale stnos.  Tracked as latent
   follow-up — not gating.

**Files touched (session #50):**
- `src/frontend/snobol4/snobol4.y` (line 247: `strcasecmp` → `strcmp`)
- `src/frontend/snobol4/snobol4.tab.c` (regenerated)

**Gates:** Smoke=7, Broker=49.  Harness still diverges at step 1257.

**Next session resume hint:**
- `_eval_pat_impl_fn` is NOT the eager-eval source.  Don't re-check.
- Prove the beauty-specific state difference: instrument `EVAL_fn`
  to log the input string AND the parsed tree shape.  Compare the
  tree shape for the FIRST reduce call (stno that maps to step 1257)
  in isolation vs in beauty's run.  If trees match but behavior
  differs, the bug is in tree evaluation; if trees differ, the bug
  is in `parse_expr_pat_from_str` (lex/parse state pollution from
  earlier statements).
- Consider landing the 5-phase fix as a separate sub-rung
  (`SN-26-bridge-coverage-p` perhaps) — it may surface or shift -o.

---

**Session #49 (2026-04-27) — SN-26-bridge-coverage-n closed; -o
opened.**

The visible "CALL vs VALUE" asymmetry at step 1035 turned out NOT
to be a build-vs-run semantic divergence in the runtime.  It was a
stack of five distinct bridge-emission alignment bugs in scrip's
`call_user_function` and `comm_*` code path.  Each one shifted the
"first divergence" further down the wire; fixing all five advanced
the harness from step 1035 to step 1257.

The five bugs (in the order they surfaced as Lon walked the harness
forward, one record at a time):

1. `comm_call` fired AFTER the entry-pass `NV_SET_fn(retname, "")`
   clear, so the wire's first record on function entry was
   `VALUE retname=''` not `CALL fname`.  Moved comm_call up.

2. With comm_call at the right place, the entry-pass save/clear
   and exit-pass restore still fired comm_var on every NV write.
   Added `monitor_quiet_depth` global; comm_var early-returns when
   depth > 0; bracketed the two passes.

3. scrip's function-body loop in `call_user_function` didn't fire
   `mon_emit_label_bin` per stmt.  SPITBOL's stmgo fires LABEL for
   every executed stmt regardless of nesting.  Added at body-loop
   head.

4. `comm_return` was marshaling the return value's bytes; SPITBOL
   emits the rtntype STRING (`"RETURN"`/`"FRETURN"`/`"NRETURN"`).
   Result is delivered via the preceding VALUE record on the
   function-name variable.  Aligned scrip to emit `kw_rtntype`.

5. `comm_call`/`comm_return` reported `fname` (caller-side alias);
   for `OPSYN('&', 'reduce', 2)` the call site is `&` but the body
   is `reduce`, and SPITBOL reports the body name.  Switched to
   `retname` (canonical body name from `FUNC_ENTRY_fn`).

After the five fixes, step 1257 surfaces a genuinely different bug
class: scrip emits `CALL nTop` where SPITBOL emits `VALUE reduce`
during the `reduce = EVAL("epsilon . *Reduce(" t ", " n ")")`
assignment inside reduce's body.  This is the build-vs-run
distinction Lon flagged earlier — SPITBOL builds the `*Reduce`
deferred pattern without invoking inner functions; scrip is
calling `nTop()` eagerly somewhere it shouldn't.  Tracked as -o.

**Files touched (session #49):**
- `src/runtime/x86/snobol4.h` (extern monitor_quiet_depth)
- `src/runtime/x86/snobol4.c` (define monitor_quiet_depth, gate
  comm_var on it, rewrite comm_return to emit kw_rtntype)
- `src/driver/interp.c` (call_user_function: move comm_call early
  and pass retname; bracket entry-pass save/clear and exit-pass
  restore with monitor_quiet_depth; pass retname to comm_return;
  add mon_emit_label_bin in body-loop)

**Lesson for future sessions.**  When a sync-step harness reports
a divergence and the two records look like they're at different
points in the execution model ("CALL vs VALUE", "build vs run"),
walk the harness forward one record at a time after each fix.  The
visible top-level shape ("scrip went straight to assign while
SPITBOL was still in build phase") may decompose into a stack of
small, independent bridge-emission bugs that each shift the
divergence by one or two records.  Resist the temptation to fix
the perceived top-level shape with a big architectural change
before fixing the small per-record alignments — the small fixes
are independently correct (they bring the wire shape into
agreement with SPITBOL on the records they touch) and the residual
bug, if any, becomes much clearer once the small ones are out of
the way.

**Session #47 (2026-04-27) — SN-26-bridge-coverage-m diagnosis
[SUPERSEDED by session #48].**  The hypothesis below — that SPITBOL's
syscall thunk for `sysml` perturbs SIL state when the IPC wire is
active vs idle — turned out to be wrong.  The visible "skipped 461
and 462" effect was an artifact of comparing two scenarios that
differed in a second variable: monitor-active vs inactive, AND
controller=`monitor_sync_bin.py` (2-way) vs controller=
`read_one_wire.py` (1-way).  Session #48 isolated them by driving
SPITBOL through `read_one_wire.py` alone with monitor pipes active —
the kvstn sequence was identical to the plain run.  The IPC handshake
does not perturb SIL state.  Original session #47 narrative kept
below for reference; it is now historical.

> Disproved the hypothesis from session #46 that scrip emits LABEL
> events SPITBOL doesn't.  Probes (`probe_bare.sno`,
> `probe_define7.sno`) showed full agreement on bare-label LABEL
> emission and DEFINE-with-goto LABEL emission in isolation.  The
> beauty-specific divergence at step 882 (spl=463, scr=461) is
> caused by SPITBOL ITSELF taking different control flow when the
> monitor wire is active vs idle.  Plain run: `kvstn` sequence
> includes 461 and 462 (correct flow `:(GenEnd)` → 461 → 462 → 463).
> Harness run: `kvstn` jumps 443 → 463, skipping 461 and 462 entirely
> at the `stmgo` level — not at the bridge-emit level.
>
> The active-monitor codepath does writev → wait_ack(read).  The
> idle codepath early-returns.  Something in the syscall thunk
> register save/restore (`int.asm` lines 624-665) or stack switch
> (`compsp` ↔ `osisp`) interacts with active write/read to alter
> SIL register state SPITBOL relies on across `jsr sysml` returns.
> Notable: the `sysml` thunk at line 848 is `syscall zysml,42`
> without the `mov m_word [reg_xs],rsp` preamble that `sysmv`
> (line 833) and `sysmw` (line 856) have.  Also `_rc_` is declared
> `dd` (4 bytes) at line 245 but written as `m_word` (8 bytes) at
> line 639; padding before `align cfp_b` gets clobbered (likely
> benign but verify).
>
> **Diagnostic technique** (re-applicable; revert before commit per
> RULES.md):
> ```c
> /* in zysml, before monitor_init() */
> if (getenv("SPL_TRACE_LABEL")) {
>     FILE *tf = fopen("/tmp/spl_zysml.log", "a");
>     if (tf) { fprintf(tf, "[zysml] kvstn=%ld\n", (long)stno); fclose(tf); }
> }
> ```
> Compare logs from plain and harness runs.  Around line 480 (just
> after `kvstn=443`) the divergence appears.
>
> No source file changes committed this session — diagnostic only.
> Gates: Smoke=7, Broker=49 preserved.

**Session #48 (2026-04-27) — SN-26-bridge-coverage-m closed; -n
opened.**

Reproduced session #47's `[zysml] kvstn=N` finding cleanly — same
binary, harness goes 442 → 443 → 463 (skips 461, 462), plain goes
442 → 443 → 461 → 462 → 463.  Then drove SPITBOL through
`read_one_wire.py` alone (single participant, monitor pipes still
open, controller still acks every record): the kvstn sequence was
**byte-identical to the plain run**.  This rules out the
syscall-thunk register-clobber hypothesis from session #47 — the
IPC handshake doesn't perturb SIL state.

The remaining variable was the controller.  Inspection of the auto
harness (`test_monitor_3way_sync_step_auto.sh`) showed it set
`SETL4PATH=".:$INC"` for SPITBOL and `SNO_LIB="$INC"` for scrip.
With CWD=/, `.` is empty so SPITBOL went to `$INC`.  But scrip's
lexer (`src/frontend/snobol4/snobol4.l`) walks the source file's
parent directory FIRST regardless of `SNO_LIB` — and
`programs/snobol4/demo/beauty/Gen.inc` exists, so scrip pulled it
before reaching `$INC`.  Confirmed via `strace -e openat`:
SPITBOL opens `programs/include/Gen.inc` (59 lines), scrip opens
`programs/snobol4/demo/beauty/Gen.inc` (57 lines).

`diff` of the two: the `programs/include/` version has 2 extra
lines (lines 52, 54 — alternative S:(NRETURN) paths inside
`GenTab`).  Same logical include, divergent bytes.  The 2-line
difference shifts every subsequent stno by 2.  In the SPITBOL
numbering `GenEnd` is stno 463; in the scrip numbering it's stno
461.  Both runtimes correctly executed their own program; the
"divergence" was a numbering artifact, not a runtime bug.

`semantic.inc` was also divergent — `programs/include/` uses
two-arg DEFINEs with `_`-suffixed body labels (SPITBOL-compat
form), demo/beauty uses one-arg DEFINEs.  Both files are referenced
by beauty.

**Fix landed (corpus this commit):** removed every duplicate `.inc`
file from `programs/include/` that has a copy in
`programs/snobol4/demo/beauty/` — 16 files total.  demo/beauty is
now canonical.  35 un-gated programs (mostly `programs/lon/sno/`)
that `-INCLUDE 'Gen.inc'` etc. now no longer resolve their includes
from `programs/include/`; listed in the -m closure block.

Verification: 2-way harness on `beauty.sno < /dev/null` advances
from step 882 → step 1035.  Steps 1..1034 all agree.  New
divergence at 1035 is genuine (CALL-vs-VALUE asymmetry on bare
`nPush()` invocation) and tracked as -n.  Smoke=7, Broker=49
preserved.

**SPITBOL side: nothing committed.** The session #47 diagnostic
printf was reverted before commit (RULES.md "Diagnostic patches
don't ship").  x64 working tree is clean; bin/sbl restored to the
pre-session-47 committed binary
(md5 79cab92f8529ebb22a5260dfbee7ddc8).

**Lesson for future sessions.** When a sync-step harness reports a
divergence, before reaching for runtime hypotheses, verify that
both runtimes are executing the **same source** — including all
`-INCLUDE`d files.  scrip and SPITBOL resolve `-INCLUDE`
differently (scrip walks the source's parent dir first; SPITBOL
strictly follows SETL4PATH order), so giving each runtime "the
same path" via env vars does NOT guarantee they open the same
files.  The cleanest invariant is: corpus must have no
byte-divergent duplicate `.inc` files anywhere, period.  This
session enforces that for the demo/beauty include set; future
audits should check the broader corpus.

**Follow-up flagged:** RULES.md "No duplicate corpus source files →
Exception — self-contained demo programs" still says "the canonical
copy still lives in `programs/include/`".  After this session,
that's no longer true for the 16 .inc files involved in beauty's
self-host.  Either the rule needs flipping (canonical lives in
demo/beauty for these) or the demo/beauty copies need to be
regenerated as exact mirrors of replacement programs/include
copies (which would re-introduce duplication; not preferred).
Tracked as a HQ-text update for a future "grand master reorg"
session, not blocking SNOBOL4 ladder work.

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
follow-up since the harness uses --interp only.

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
- scrip `--interp`: clean run, 523 lines, md5
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
