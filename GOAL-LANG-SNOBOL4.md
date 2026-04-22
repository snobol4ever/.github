# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

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

## Rung ladder

### Phase 1 -- IR-run  DONE (SN-1..SN-5, SN-14, SN-15, SN-16, SN-19)
### Phase 2 -- SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 -- JIT-run (SN-10..SN-12, gated on SN-9)

- [x] **SN-20** — NAM push/pop self-unwinding. `*var-holds-DT_E` thaw folded
  into `name_commit_value` at SN-21e. one4all @ `8964586e`.

- [x] **SN-21** — Unified `NAME_t` + flat NAM stack. One lvalue concept, one
  push/pop API, one `bb_cap` box for `.` / `$` / `NRETURN` / `*fn()`. Landed
  across SN-21a..e. one4all @ `8964586e`.

- [x] **SN-17** — Porter stemmer gap closed (2026-04-19). `--ir-run` and
  `--sm-run` both 100.00% / 23531 on porter.sno. Landed via SN-17a (new
  `SM_PAT_USERCALL` opcode, `f2cf3494`) + SN-17d (FAIL propagation in
  `bb_usercall`, `9d9d2dd3`). SN-17b, SN-17c deferred — not required.

- [x] **SN-17a** — Added `SM_PAT_USERCALL` opcode. one4all @ `f2cf3494`.

- [~] **SN-17b** -- Unify `bb_build` dispatch.  **DEFERRED**: inspection
      at SN-17a found that stmt_exec.c's `bb_build` and bb_build.c's
      `bb_build_binary_node` produce *different* artifacts (C closure
      `bb_node_t` vs native x86 trampoline `bb_box_fn`), not parallel
      dispatchers answering the same question.  They share the XKIND
      switch skeleton but each case emits a fundamentally different
      object.  Neither goal-file option fits cleanly: (i) with a mode
      flag forces every case body to branch on mode, reducing clarity;
      (ii) a single function-pointer table can't carry two return
      types.  More importantly, SN-17d landed with a single-file fix
      to `bb_usercall` — unification was not required to get the
      Porter fix into both modes, because SN-17a had already routed
      them through the same XATP / bb_usercall path.  Keep as optional
      cleanup; not on the SN-7 critical path.

- [~] **SN-17c** -- Unify SM opcode handlers.  **DEFERRED** for the
      same reason as SN-17b: the duplication cost was paid once in
      SN-17a (adding SM_PAT_USERCALL in sm_interp.c + sm_codegen.c)
      and SN-17d didn't need it.  Still a defensible cleanup, but
      not required for SN-7.

- [x] **SN-17d** — Fixed `*fn()` FAIL propagation in `bb_usercall`.
  Porter reached 100.00% / 23531 in both modes. one4all @ `9d9d2dd3`.

- [x] **SN-6** — Full corpus: PASS=225/225 in all three modes (2026-04-20).
  Closed via a one-word gate-script fix at
  `test_interp_broad_corpus_and_beauty.sh:67`. SN-6a (new `SM_PAT_REFNAME`
  opcode for `--sm-run` self-recursive patterns) landed with it.

- [x] **SN-22** — NAM API reduction: push + pop only, one stack per match,
  no marks, no rollback (2026-04-19). Landed via SN-22a..d:
  - SN-22a/b: removed `NAME_mark` / `NAME_rollback_to` calls from `bb_alt`
    and `bb_arbno`; dropped `nam_mark` fields. Broker recovered +1 (48→49).
  - SN-22c: removed `NAME_mark` / `NAME_rollback_to` declarations and
    definitions. Public API down from 11 → 9 entries.
  - SN-22d: deleted two vestigial `NAME_discard(nam_cookie)` calls at
    `stmt_exec.c:1192,1206` after verifying box self-unwind completeness.
  Reference: Python `_backend_pure.py` `Δ.γ` pattern (append / yield / pop).

- [~] **SN-6b** -- expr_eval arithmetic path.  **DT_E thaw gap closed
  2026-04-19**; expr_eval still fails — additional layered bugs.

  DT_E descriptor union-aliasing bug fixed in 4 constructor sites; DT_E thaw
  added to `bb_deferred_var`.  expr_eval closed later via SN-23g (NAM API
  collapse fixed the underlying EVAL-within-match corruption).  Full
  diagnostics in commit log.

- [x] **SN-6c** — Recursive pattern NAM corruption closed for `--ir-run`
  via SN-23d-follow-up (`has_pending` reset at top of CAP_α). one4all @
  `d61a580e`. Root cause: `cache_get_fresh` memcpys dirty template ζ into
  every "fresh" cap_t. Defensive fix at the site; underlying cache flaw
  (template aliases first match's live state) remains latent.

- [x] **SN-23** — Per-pattern NAM context, SIL-matching API (2026-04-19).
  Introduced `NAME_ctx_t` with enter/leave brackets; nested EVAL isolated
  by ctx nesting. Landed across SN-23a..h. Final API is 5 entries mapping
  1:1 to SIL NMD primitives (ENME / DNME / NMD / PUSH+MOVD NHEDCL / POP
  NHEDCL): `NAME_push`, `NAME_pop`, `NAME_commit`, `NAME_ctx_enter`,
  `NAME_ctx_leave`. Down from 13 entries at start of SN-22. Closing gates:
  Smoke=7, Broker=49, Broad=224/225, Porter byte-identical both modes,
  `expr_eval` flipped PASS. Final rung SN-23h at one4all @ `a556167b`.
  Cross-concern: `cache_get_fresh` template aliasing is still latent — a
  defensible future rung if symptoms appear in other box types.

- [x] **SN-7** — beauty subsystem drivers self-host (2026-04-19). Gate
  `test_gate_sn7_beauty_self_host.sh` at PASS=51/51 (17 drivers × 3 modes).
  **Overclaimed as "beauty.sno self-hosts"**: drivers test subsystems
  individually, not the top-level `Parse` / `main00..main05` loop. See
  SN-7-note and SN-26 for the true self-host work.

- [x] **SN-8** — Args-on-stack SM opcodes for `. *fn(args)` / `$ *fn(args)`
  / bare `*fn(args)` non-all-E_VAR fallback (2026-04-19). Added
  `SM_PAT_CAPTURE_FN_ARGS` and `SM_PAT_USERCALL_ARGS`; wired handlers in
  `sm_interp.c` + `sm_codegen.c`; `sm_lower` emits the new opcodes when
  `sm_pat_capture_fn_arg_names` returns NULL. All four oracles (SPITBOL,
  IR, SM, JIT) converge on rec / usercall_args repros. Latent: named-args
  path in all-E_VAR case + SM-side XATP stash gap — SN-8b if hit.

- [x] **SN-9** — JIT/codegen parity with `sm_interp`. Closed via SN-9a..c:
  opening audit found `SM_PUSH_EXPR`, `SM_BB_PUMP`, `SM_BB_ONCE` missing
  from `g_handlers[]`; plus 7 latent JIT-only failures surfaced in SN-9c
  three-mode sweep. All closed. Gate `test_smoke_snobol4_jit.sh` now at
  207/207/207 on crosscheck.

- [x] **SN-9a** — Closed `SM_PUSH_EXPR` gap in codegen (2026-04-19). Added
  `h_push_expr` handler mirroring `sm_interp.c`. Porter `--jit-run` from
  7979-line diff to 0-line diff vs ref. Same DT_E union-aliasing
  discipline as SN-6b.

- [x] **SN-9b** — Closed remaining codegen handler gaps (2026-04-19).
  one4all @ `f8b06dc6`. Wired `SM_BB_PUMP` and `SM_BB_ONCE` (Icon/Raku
  generators + Prolog backtracking); other audit opcodes classified as
  stale / cross-mode / never-emitted. `test/raku_gather.scrip` byte-
  identical under `--sm-run` and `--jit-run`.

- [x] **SN-9c** — JIT parity gate: three-mode sweep codified
  (`test_smoke_snobol4_jit.sh`), 207/207/207 on crosscheck (2026-04-19).
  Opening scan found 7 JIT-only failures; all closed via sub-rungs
  SN-9c-a..e (case-folding, NRETURN_ASGN branch, last_ok parity, DT_SNUL
  coercion, pre-call FAIL propagation). Bonus: `expr_eval` flipped PASS
  in all three modes. See `scripts/test_smoke_snobol4_jit.sh` and commit
  log for details.

- [~] **SN-7-note** -- 2026-04-20 reassessment.  SN-7 above ("beauty
  self-host 51/51") was **overclaimed** — the 51 combos test the 17
  `beauty_*_driver.sno` files (subsystem unit tests), which exercise
  `assign.sno`, `case.sno`, `counter.sno`, `match.sno`, `fence.sno`,
  `ShiftReduce.sno`, etc. individually via hand-crafted inputs and
  PASS/FAIL strings.  **Zero driver consumes `beauty.sno`'s own
  top-level `Parse` pattern or the `main00..main05` stdin loop.**  The
  goal-level "Done when" clause in the header — *"beauty.sno
  self-hosts cleanly under all three modes"* — requires literal
  self-application: `scrip <mode> beauty.sno < beauty.sno` reproduces
  `beauty.sno`.  That is not demonstrated anywhere today.  See SN-26.

- [~] **SN-25** -- SPITBOL `-f` structural-keyword lookup fix.
  **CLOSED 2026-04-21 (session 7) — won't fix.**  Per Lon's
  directive: "belay my order to make enhancement to SPITBOL and/or
  CSNOBOL4 to case on ingress. Just do as they have always done and
  continue with fixes for crash and END recognition, etc."  Further:
  "Never going to worry about ingress for old products, just we'll
  use that technique for one4all."

  SPITBOL and CSNOBOL4 fold inside `GTNVR` / `GENVUP` gated on
  `&case` / `CASECL`.  That is the settled design; it stays.  The
  ingress-at-lex principle applies to one4all only, going forward.

  Historical work from sessions 2-6 below is preserved for the
  record only.  Do not reopen SN-25 / SN-25a-f without a direct
  directive from Lon.

  **Historical record (do not pursue):**

  **Symptom (verified on `/tmp/trivial2.sno` — a single
  `OUTPUT = 'hi'` line with the required leading whitespace):**
  - `sbl -b trivial2.sno`  → `hi`, exit 0.  ✓
  - `sbl -bf trivial2.sno` → `No END statement found in source
    file(s).` exit 1.  ✗  **Any** simple program with `-f` produces
    this error — it has nothing to do with beauty.sno or size.

  **Why this matters for the SNOBOL4 ladder:** `beauty.sno` uses the
  double-function trick (`shift`/`Shift`, `reduce`/`Reduce`,
  `pop`/`Pop`, `visit`/`Visit` — 4 pairs in the SPITBOL-side
  subsystems), which requires case-sensitive label resolution.  Per
  RULES.md, the blessed fallback is CSNOBOL4 `-bf`, but CSNOBOL4
  SEGVs on beauty.sno at line 616 (`snoLine = INPUT` in main02).
  A working `sbl -bf` would restore the oracle-on-the-happy-path
  configuration for all double-function-trick programs.

  **Root cause:** in `/home/claude/x64/bootstrap/sbl.asm`, the
  compiler's keyword table stores 6 structural system labels in
  **lowercase**:
  ```
  1563: v_end:  d_word svlbl ;                                 [followed by]
  1565:         d_char 'e','n','d',0,0,0,0,0     ; /end/
  1921: v_ret:  d_word svlbl ; return    — 'r','e','t','u','r','n',0,0
  1972: v_frt:  d_word svlbl ; freturn   — 'f','r','e','t','u','r','n',0
  1981: v_nrt:  d_word svlbl ; nreturn   — 'n','r','e','t','u','r','n',0
  2025: v_cnt:  d_word svlbl ; continue  — 'c','o','n','t','i','n','u','e'
  2072: v_scn:  d_word svlbl ; scontinue — 's','c','o','n','t','i','n','u','e'
  ```
  The generic lookup at `gnv09`/`gnv10` (lines 14396-14414) does a
  pointerwise bytewise compare between the source identifier's chars
  (at `gnvst`) and the table entry's chars.  With the default `-F`
  (fold to lowercase) set, source `END` has already been folded to
  `end` upstream, so byte-by-byte `e==e, n==n, d==d` ✓.  With `-f`
  (no fold), source `END` stays uppercase; `E != e` at byte 0 → the
  lookup misses `v_end`.  Nothing ever recognizes the `END` statement;
  the file exhausts; `swcinp.c:215` fires the "No END" error.

  Identifier lookup for user-defined names is already case-sensitive
  by design under `-f` — that's the feature.  Only structural
  keywords (END / RETURN / FRETURN / NRETURN / CONTINUE / SCONTINUE)
  need to remain case-insensitive regardless of `-f`.

  **Proposed fix** (surgical, one routine):

  Make the comparison loop at `gnv10` (`bootstrap/sbl.asm:14408-14413`)
  fold both operands to lowercase via `OR 0x20`-per-byte before
  comparing, **but only for `svlbl`-typed entries** (svbit already
  discriminates the six lines).  Alternative route: add a second
  prefolded-source pointer and consult it only in the svlbl branch.

  **Upstream source:** the lowercase-literal table is generated from
  `asm.sbl` / `lex.sbl` / supporting source in `/home/claude/x64/`.
  Any change to `bootstrap/sbl.asm` must also land in the upstream
  `.sbl` sources so `make sbl` (which regenerates sbl.asm from
  `.sbl`) doesn't revert the fix next rebuild.

  - [x] **SN-25a** -- Reproduce baseline on a fresh `bootsbl`.
    **Done 2026-04-21 (session 2).**
    ```bash
    apt-get install -y nasm
    cd /home/claude/x64 && make bootsbl        # ~3s, no SBL needed
    ./bootsbl -b  /tmp/trivial2.sno   # hi,  exit 0  ✓
    ./bootsbl -bf /tmp/trivial2.sno   # FAIL "No END statement found", exit 1  ✓
    ```
    Bug reproduces deterministically on fresh clone.

  - [~] **SN-25b** -- Patch `bootstrap/sbl.asm` `gnv10`.  **Attempted
    2026-04-21 (session 2), REVERTED — more work needed.**

    **What was tried:** two variants of the `gnv10` fold patch
    (see `/tmp/sbl.asm.orig` for upstream baseline):

    **Variant A — conditional fold on `svlbl` bit only:**
    ```asm
    gnv10:
            mov  w0,m_word [xl]             ; load table chars
            test wc,svlbl                   ; svlbl-typed?
            jz   gnv10a                     ; no: exact compare
            mov  r10,m_word [xr]            ; load source
            mov  r11,0x2020202020202020     ; ASCII fold mask
            or   w0,r11                     ; fold table
            or   r10,r11                    ; fold source
            cmp  r10,w0                     ; compare folded
            jmp  gnv10b
    gnv10a: cmp  m_word [xr],w0             ; original exact compare
    gnv10b: jnz  gnv11
            ... rest unchanged
    ```
    **Result:** trivial `output='hi' / END` worked under both `-b`
    and `-bf`.  But a larger test with `DEFINE('f()')` + `RETURN`
    under `-bf` failed with `error 022 -- undefined function called`
    on statement 1 — meaning `DEFINE` itself wasn't being recognized.
    `DEFINE` is a system function (`svfnc` bit, not `svlbl`), so the
    conditional fold didn't apply to it.

    **Key discovery at this point:** the original rung's premise —
    that only the 6 *structural* keywords (END/RETURN/FRETURN/
    NRETURN/CONTINUE/SCONTINUE, marked `svlbl`) need case-insensitive
    matching — is wrong.  **ALL system names need case-insensitive
    matching** under `-bf`, because every entry in the compile-time
    `vsrch` table (system functions like `DEFINE`, `SIZE`, `OUTPUT`,
    `INPUT`; keywords like `ANCHOR`, `TRACE`; patterns like `LEN`,
    `POS`, `RPOS`) is stored lowercase.  The `gnv10` lookup path is
    reached ONLY for system entries (user vars go through the hash
    chain `gnv03..gnv07`; `gnv08` is the entry point to the system-
    var table after hash-miss — see `sbl.asm:14359,14389-14396`).
    So `gnv10` needs unconditional fold, not svlbl-gated.

    **Variant B — unconditional fold:**
    ```asm
    gnv10:
            mov  w0,m_word [xl]             ; load table chars
            mov  r10,m_word [xr]            ; load source chars
            mov  r11,0x2020202020202020
            or   w0,r11                     ; fold table (idempotent)
            or   r10,r11                    ; fold source
            cmp  r10,w0
            jnz  gnv11
            ... rest unchanged
    ```
    **Result: PRODUCED SILENT FAILURES.**  Trivial `output='hi' / END`
    under `-b` (default) still worked, but under `-bf` produced
    zero output and exit=0 — no error, but the OUTPUT statement
    never fired.  A program with `OUTPUT = 'hi'` **at column 1**
    (no leading whitespace) under `-bf` SEGV'd.  Under `-b`
    everything behaved fine.

    **Unresolved — next session starts here:**

    The SEGV and silent-failure under `-bf` with Variant B means the
    unconditional fold is causing a *false positive* match somewhere
    — folding an uppercase source identifier causes it to match a
    system-table entry it shouldn't have matched.  Specific
    hypothesis not yet pinned down.  Candidates to probe:

    1. **User-defined labels fall into `gnv08`.**  Re-examine
       `sbl.asm:14359 jz gnv08` — I claimed user-vars never reach
       `gnv10`, but that may be wrong for *labels* (which aren't
       hashed the same way).  If a user label `OUTPUT` (some
       program's own label) reaches `gnv10`, the fold would falsely
       match it to the system OUTPUT function.

    2. **Order of table entries.**  If two system entries at same
       length differ only in case in the source but map to lowercase
       in the table, one might match first under the fold and claim
       a descriptor for the other.  Unlikely (all table entries are
       unique-lowercase), but verify.

    3. **Pad-byte interaction.**  `d_char 'o','u','t','p','u','t',0,0`
       has NUL pad bytes; `OR 0x20` turns those into `0x20` (space).
       If the source buffer has garbage or different padding in
       bytes >= length, the fold-both-sides comparison could
       spuriously match (both become 0x20 by coincidence) where
       unfolded would have differed.  This is the leading hypothesis.

    **Recommended fix (to try next session):** fold only the first
    `wa` bytes (the actual name length), leaving pad bytes untouched.
    But the current code compares entire 64-bit words at once —
    rewriting to byte-at-a-time would be a larger change.  Alternative:
    mask out bytes beyond position `wa` BEFORE folding.  Alternative:
    ensure source buffer pad bytes are NUL-initialized and match
    table pad bytes exactly (so fold idempotently preserves NUL — 
    but OR 0x20 doesn't preserve NUL, that IS the issue).

    **Simplest correct patch** (to try first): compute a byte-wise
    fold mask that is 0x20 for ASCII letter positions and 0x00
    elsewhere, by checking each byte against `ch_ua..ch_uz`.  That's
    what the SIL macro `fold1` style does.  This is the path
    `flstg` itself uses (see line 8093 in sbl.asm).  Look there for
    the reference pattern.

    **Current state:** `bootstrap/sbl.asm` REVERTED to upstream at
    start-of-session.  No change committed.  Patch work continues
    next session.

  - [~] **SN-25b-retry** -- **In progress 2026-04-21 (session 3).**
    Patch applied to `/home/claude/x64/bootstrap/sbl.asm` at `gnv10`
    using byte-wise fold-both-sides compare (the `flstg` reference
    pattern at `sbl.asm:13318`ff, NOT line 8093 — that was a call
    site; the routine itself is at 13318).  **Not committed, not
    built, not verified.**  Next session picks up at the build step.

    **Investigation done this session — compile-time path traced:**
    `cmp11` at `sbl.asm:11614-11627` is the compiler's label-
    recognition site.  It builds an scblk from the scanned label
    text (`sbstr` at 11614) and calls `gtnvr` (14315).  `gtnvr`
    calls `flstg` at line 14339, which is a no-op when `kvcas=0`
    (i.e. under `-f`).  Execution then falls through `gnv02..gnv09`
    to `gnv10` for the system-keyword table compare.  With upper-
    case source and lowercase table, the word-wise compare at
    `gnv10` misses.  `v_end` is never found at line 11627.  File
    exhausts.  `swcinp.c:215` fires "No END statement found".

    **Confirms:** the SN-25 root-cause hypothesis was correct.
    `gnv10` is the right fix site, and it serves both compile-time
    keyword recognition and runtime name lookups via the same path.

    **Patch landed in `bootstrap/sbl.asm` (uncommitted, this
    session's working copy only):** between the `gnv10:` label and
    the `gnv11:` label, the word-cmp was replaced with a byte-wise
    fold-both-sides compare.  Uses `r9` to save the outer word
    counter, `wb` as inner per-word byte counter (8 at entry to
    each word), `r10`/`r11` as byte scratch for the two folded
    bytes, `w0`/`al` for the zero-extended byte loads.  Per-byte
    range-check: `if ch>='A' && ch<='Z': ch+=32` on each side
    independently, then `cmp r10,r11`.  Mismatch path rewinds `xl`
    to the start of the current word (subtract bytes consumed)
    then falls through to the existing `gnv11` cleanup, which
    still works because `wb` has been restored from `r9` (the
    outer word counter).  Match path jumps directly to the success
    code (`xor wc,wc` etc).

    **Why byte-wise (not full-word `OR 0x20`):** variant B in the
    prior session folded whole 8-byte words via `OR 0x20`, which
    turned NUL pad bytes (value 0) into space (0x20).  Two entries
    whose name chars differ but whose pad bytes both become 0x20
    would then match spuriously.  Byte-wise fold with explicit
    range-check leaves NUL bytes (0 < 'A') untouched — the canonical
    `flstg` pattern does exactly this at `sbl.asm:13335-13343`.

    **Baseline confirmed this session before patching:**
    `./bootsbl -b /tmp/sn25/trivial.sno` → `hello` exit 0 ✓
    `./bootsbl -bf /tmp/sn25/trivial.sno` → "No END statement found"
    exit 1 ✗ — same as all prior sessions.

    **Next session pickup (exact commands):**
    ```bash
    # Restore baseline first if needed:
    #   cp /tmp/sbl.asm.orig /home/claude/x64/bootstrap/sbl.asm
    # (/tmp/sbl.asm.orig was saved but is lost with container;
    #  re-clone x64 if reverting is needed.)
    cd /home/claude/x64
    make clean && make bootsbl     # force rebuild — .o's were stale
    ./bootsbl -b  /tmp/sn25/trivial.sno   # expect: hello (baseline OK)
    ./bootsbl -bf /tmp/sn25/trivial.sno   # expect: hello (SN-25b fix)
    ```
    Then run through all 4 verification items in the old
    SN-25b-retry list (below).  On green, advance to SN-25c
    (mirror into `asm.sbl`/`lex.sbl`, `make sbl`, install as
    `bin/sbl`).

    **Unfinished verification checklist** (still applies):
    1. Trivial `output='hi' / END` under both `-b` and `-bf`.
    2. Larger program exercising `DEFINE`, `OUTPUT`, `INPUT`,
       `SIZE`, `RETURN` under `-bf`.
    3. All 6 structural keywords (END/RETURN/FRETURN/NRETURN/
       CONTINUE/SCONTINUE) under `-bf`.
    4. A program with a user-defined label named like a system
       function (e.g., `output` as a user label) under `-bf` —
       must NOT match the system entry.  (User-vars go through
       `gnv05` not `gnv10` per the hash-chain logic, so this
       should still work — the fold only affects `gnv10`.)
    If all 4 checks pass, advance to SN-25c.

  - [~] **SN-25b (session 4, 2026-04-21)** — bootstrap patch built,
    verified, **reverted per hand-off rule (do not patch generated
    code)**.

    **What worked:** byte-wise fold-both-sides compare at `gnv10`
    in `bootstrap/sbl.asm` (r10/r11 scratch, wa pushed/popped as
    per-word byte counter, rewind xl/xr on mismatch before jumping
    to `gnv11`).  All 4 checklist items passed:
    1. Trivial OUTPUT under `-b` and `-bf` — both print `hello`.
    2. DEFINE/SIZE/OUTPUT/RETURN under `-bf` — prints
       `hello, world` / `size=6`.
    3. All 6 structural keywords under `-bf` — RETURN/FRETURN
       exercised inline; NRETURN via `*f()` separately; END/CONTINUE
       implicit (exit 0 no-error).
    4. Double-function trick `shift`/`Shift` under `-bf` — both
       functions distinct, both print their own output.  Under `-b`
       the fold collapses them (expected, not a regression).
    `-b` behavior unchanged on every test.

    **Landed and reverted on x64:**
    - `6530c15` — SN-25b bootstrap patch (forward)
    - `5843f5d` — revert of the above (both pushed to origin/main)

    **Why reverted:** `bootstrap/sbl.asm` is generated from
    `sbl.min` via `make sbl`.  Patching the bootstrap works
    immediately but any future `make sbl` → `make makeboot` cycle
    reverts the fix.  Per Lon's mid-session direction, the proper
    rung is SN-25c: patch the SIL source, regenerate, install.

    **SIL source located:** `/home/claude/x64/sbl.min:23093-23096`
    contains the gnv10 block:
    ```
    gnv10  cne  (xr),(xl),gnv11  jump if name mismatch
           ica  xr               else bump new name pointer
           ica  xl               bump svblk pointer
           bct  wb,gnv10         else loop until all checked
    ```
    `cne (xr),(xl),lbl` is word-wise compare-not-equal (8 bytes at
    once).  SIL has no built-in byte-wise fold-compare; the patch
    must spell out a nested inner loop using `lch`/`blt`/`bgt`/`flc`/
    `beq`/`bct` primitives, mirroring the `flstg` pattern at
    `sbl.min:21501-21530`.

    **SIL patch draft** (for SN-25c next session — refine
    register-liveness before applying):
    ```
    gnv10  mov  -(xs),wa        save wa across byte loop
           mov  wa,=cfp_c       8 bytes per word
    gnv10a lch  wc,(xl)+        load table byte
    *      NOTE: wc is LIVE (holds svbit from gnv09).  Must push wc
    *      too, OR use a different temp register.  w0 is free;
    *      consider `lch w0,(xl)+` + a second temp for the source
    *      side.  Register pressure analysis pending.
           blt  wc,=ch_ua,gnv10b
           bgt  wc,=ch_uz,gnv10b
           flc  wc
    gnv10b lch  w0,(xr)+        load source byte
           blt  w0,=ch_ua,gnv10c
           bgt  w0,=ch_uz,gnv10c
           flc  w0
    gnv10c beq  wc,w0,gnv10d    match -> next byte
           [rewind xl,xr by (cfp_c-wa); pop wa; pop wc; brn gnv11]
    gnv10d bct  wa,gnv10a       8-byte inner loop
           mov  wa,(xs)+        restore
           bct  wb,gnv10        outer word loop
           [fall through to existing success path]
    ```

    **Critical register-liveness constraint:** `wc` holds `svbit`
    loaded at `gnv09` (sbl.min:23085) and read at `gnv11`→`gnv12`
    (sbl.min:23108 `rsh wc,svnbt`).  Any temp use of `wc` in the
    byte loop MUST save/restore it.  The draft above uses `wc` —
    must be corrected, OR push `wc` at gnv10 entry and pop at both
    exit paths.

    **Build pipeline verified:**
    - `make sbl` uses `$(BASEBOL)=./bin/sbl` (which exists) to process
      `lex.sbl` → `sbl.lex`, `asm.sbl` → `sbl.asm`, `err.sbl` →
      `err.asm`, then NASM + cc → `sbl` binary (sbl.min is input to
      asm.sbl macro processing).
    - `make makeboot` (after sanity-check) persists the regenerated
      `sbl.asm`/`err.asm`/`sbl.lex` into `bootstrap/`.
    - `flc` macro expands at `asm.sbl:2505` to
      `cmp cl,'A'; jb t2; cmp cl,'Z'; ja t2; add cl,32; t2:` —
      byte-level fold on low byte of target register.  Good.

  - [x] **SN-25.x32** -- Probe `spitbol/x32` `-bf`.  **Done 2026-04-21.**
    Confirmed the `-f` bug is shared with x64 — x32 is NOT a zero-patch
    alternative oracle.  Pivot to SN-25b (source fix) stands.

    **But the session produced two useful deliverables:**

    **(1) Working x32 runner recipe for this sandbox.**  gVisor
    (runsc kernel 4.4.0) blocks native 32-bit execution even with
    `libc6-i386` installed (`Exec format error`).  qemu-user-static
    emulates fine, but SPITBOL's MINIMAL architecture `call`s into
    its data segment (symbol `minimal:` at `0x080644aa` in the
    pre-built binary) — the ELF marks segment 02 (`.data`/`.bss`)
    `RW`, real Linux historically didn't enforce NX on such
    segments; qemu-user does, so the first dispatch SEGVs.

    One-byte ELF patch resolves it:
    ```bash
    apt-get install -y libc6-i386 qemu-user-static
    cd /home/claude && git clone https://github.com/spitbol/x32
    cp x32/bin/spitbol /home/claude/sbl32
    # Segment 02 p_flags at ehdr+2*phent+24 = 116: 0x6 (RW) -> 0x7 (RWX)
    python3 -c "
    import struct
    with open('/home/claude/sbl32','r+b') as f:
      f.seek(52 + 2*32 + 24)
      f.write(struct.pack('<I', 0x7))
    "
    qemu-i386-static /home/claude/sbl32 -b file.sno    # works
    ```
    Probe result on a trivial program (just `output='hello' / end`):
    - `sbl32 -b`  → `hello` exit 0 ✓
    - `sbl32 -bf` → `No END statement found in source file(s).` exit 1 ✗
    Same bug as x64.

    **(2) x32 DATATYPE is UPPERCASE.**  x32 SPITBOL returns
    `STRING`/`INTEGER`/`REAL`/`PATTERN`/`ARRAY`/`TABLE` — all upper.
    Distinct from x64 (lowercase) and missing from the RULES.md
    DATATYPE case table.  Source location in `s.min` lines 5250-5308
    (symbols `SCARR`/`SCBUF`/`SCCOD`/`SCEXP`/`SCINT`/`SCNAM`/`SCNUM`/
    `SCPAT`/`SCREA`/`SCSTR`/`SCTAB`).  This turns into the new
    **SN-27** rung: port the upper-case to x64 to eliminate the
    DATATYPE-compat problem.

    **Follow-ups to land next session** (captured here; blocked only
    on context, not on decisions):
    - Commit this edit of the goal file.
    - Add x32 row to RULES.md DATATYPE table (UPPERCASE).
    - Land `scripts/build_spitbol_x32_runner.sh` (the install + patch
      recipe above) for future sessions.  Self-contained per RULES.md
      (paths from `$0`, SKIP cleanly if qemu-user-static absent).
    - Commit + push under `LCherryholmes / lcherryh@yahoo.com`.

  - [ ] **SN-25b** -- Patch `bootstrap/sbl.asm` `gnv10` to fold
    compared bytes when the current entry's svbit has `svlbl` set;
    rebuild via `make bootsbl`.  Verify the trivial repro now passes
    under `-bf`.

  - [~] **SN-25c** -- **Session 6 (2026-04-21): SIL patch drafted and
    compiles; architecturally redirected before landing.**

    **What happened this session:**

    1. Applied byte-wise fold-both-sides compare to `sbl.min:23093`
       (gnv10 block).  First attempt used 6-character labels
       (`gnv10a`..`gnv10z`) — rejected by the MINIMAL lexer because
       `p.minlabel` at `lex.sbl:161` requires exactly 5 characters
       (2 letters + 3 alphanumerics).  **Gotcha for future SIL
       patches: all new labels must be 5 chars, first 2 letters.**

    2. Renamed to `gn10a`..`gn10z`.  Lex pass and asm pass both
       completed cleanly; build stopped only because `nasm` was not
       installed in the container (`apt-get install -y nasm` is the
       one-command fix; the SN-25a notes already document this).

    3. **REDIRECTED BEFORE BUILD COMPLETED** per Lon's directive:
       *"Ensure that casing happens only during lexical/parse and
       user input strings used as names."*

       Fold-both-sides at `gnv10` violates that principle.  `gnv10`
       is the standard-variable-table lookup hot path — it runs for
       **every** identifier resolution at compile time AND at run
       time (via `gtnvr` from multiple sites).  Folding there:
         - Pays the cost on every lookup, not just case-sensitive
           lookups.  The canonical form should have already been
           established at ingress.
         - Imposes a policy ("fold structural keywords case-
           insensitively") at the lookup layer instead of at the
           layer that decides canonical form (lexer / CONVERT /
           indirection).
         - Couples two orthogonal concerns: "what is this
           identifier's spelling?" (ingress decision) vs "does this
           spelling match a table entry?" (pure lookup).

       **Patch reverted.**  Working tree clean.  `sbl.min` restored
       to upstream at lines 23093-23102.

    **Revised approach — SN-25d (new rung, replaces old SN-25c):**

    Folding must happen at one of these correct sites, NOT at gnv10:

       (i) **Lexer (asm.sbl or lex.sbl)**: when the scanner
           identifies a token as a structural keyword (END, RETURN,
           FRETURN, NRETURN, CONTINUE, SCONTINUE), it can fold
           that specific lexeme to lowercase before handing it to
           `gtnvr` — regardless of `kvcas`.  User identifiers and
           other labels continue to respect `kvcas` as today.  This
           preserves case-sensitive user names while keeping
           structural keywords uniformly recognized.

      (ii) **`flstg` selective fold**: introduce `flkwd` (fold
           keyword) — a fold routine that respects `kvcas` for
           user content but always folds on the 6 structural-keyword
           token classes.  Called from the same sites as `flstg`
           but only for known-keyword-candidate positions.

     (iii) **Keyword-recognition pre-pass**: before `gtnvr` enters
           the hash chain, a dedicated 6-entry check against
           uppercase-or-lowercase END/RETURN/.../SCONTINUE short-
           circuits to the already-known svblk.  This is
           architecturally similar to (i) but implemented at the
           pre-lookup stage, not at the scan stage.

    Lon to choose the correct level between (i)/(ii)/(iii).  Each
    is smaller in scope than the gnv10 fold and none pollutes the
    common lookup path.  The original SN-25 diagnosis remains
    valid — only the proposed fix site changes.

  - [ ] **SN-25e** -- Gate: add `test_smoke_spitbol_case_sensitive.sh`
    — a short script that runs `sbl -bf` on a handful of fixture
    programs covering each of the 6 keywords.  PASS when all return
    the expected output.

  - [ ] **SN-25f** -- SIL patching gotchas (captured 2026-04-21 s6
    for future authors):
      * MINIMAL labels are exactly 5 characters: 2 letters + 3
        alphanumerics (`lex.sbl:161 p.minlabel`).  6-char labels
        produce `source line syntax error`, one per offending line.
      * `nasm` must be installed (`apt-get install -y nasm`) — not
        persisted across container resets.
      * Build flow: `make sbl` runs `./bin/sbl lex.sbl` →
        `./bin/sbl -x asm.sbl` → `./bin/sbl -x err.sbl` →
        `nasm *.asm` → `cc *.o`.  Errors in any stage halt the
        pipeline with a numeric exit code.  Lex errors appear as
        `* *???*` markers in `sbl.lex`; count via
        `grep -c '\?\?\?' sbl.lex`.

  - [ ] **SN-25d** -- Verify a slightly larger program under `-bf`
    that exercises all 6 structural keywords
    (END + RETURN + FRETURN + NRETURN + CONTINUE + SCONTINUE).

  - [ ] **SN-25e** -- Gate: add `test_smoke_spitbol_case_sensitive.sh`
    — a short script that runs `sbl -bf` on a handful of fixture
    programs covering each of the 6 keywords.  PASS when all return
    the expected output.

  **Build pipeline known working in this container:**
  `cd /home/claude/x64 && make bootsbl` succeeds in ~3s (nasm + cc
  against `bootstrap/sbl.asm` + `osint/*.c`, no SBL needed for this
  target).  Baseline `./bootsbl -b /tmp/trivial2.sno` was verified to
  match `sbl -b` (hi, exit 0) and `./bootsbl -bf` was verified to
  match the bug in `sbl -bf` (No END, exit 1).

- [ ] **SN-27** -- UPPERCASE DATATYPE for SPITBOL x64.  **Opened
  2026-04-21.**  Origin: session discovered x32 returns UPPERCASE
  DATATYPE while x64 returns lowercase — a previously-unrecorded
  fork.  Unifying on UPPERCASE (the same choice one4all, CSNOBOL4,
  snobol4jvm, and now x32 already make) eliminates the DATATYPE-case
  compat problem across the entire stack permanently.  Only
  snobol4dotnet would remain lowercase, and its lowercase choice was
  itself done to mimic x64 — so it follows x64 here.

  **Done-when:** `sbl -b` on `output=datatype('')` prints `STRING`
  (not `string`).  All builtin datatypes return uppercase:
  `STRING`, `INTEGER`, `REAL`, `PATTERN`, `ARRAY`, `TABLE`, `NAME`,
  `CODE`, `EXPRESSION`, `NUMERIC`, `EXTERNAL`, `BUFFER`, `FILE`,
  `FRETURN`, `NRETURN`, `RETURN`.

  **Why do this now:** the RULES.md DATATYPE table records SPITBOL
  x64 as lowercase with that tagged as "authoritative, intentional
  per runtime."  But that's a historical accident — SPITBOL x32
  (the older, hardbol-lineage SPITBOL) returns UPPERCASE, and the
  archive decision **D-002** (`archive/GENERAL-DECISIONS.md:32`)
  explicitly chose UPPERCASE for one4all because:
  *"The traditional SNOBOL4 spec uses uppercase datatype names.
  PATTERN and CODE are canonical and widely documented in uppercase.
  Changing to lowercase would break existing SNOBOL4 programs that
  test `DATATYPE(x) = 'PATTERN'`."*  x64 is the outlier; every other
  runtime we care about already agrees on uppercase.

  **Source location (verified in x32):** `s.min` lines 5250-5308,
  symbols `SCARR`/`SCBUF`/`SCCOD`/`SCEXP`/`SCEXT`/`SCINT`/`SCNAM`/
  `SCNUM`/`SCPAT`/`SCREA`/`SCSTR`/`SCTAB`/`SCFIL` and the
  return-type names `SCFRT`/`SCNRT`/`SCRTN`.  Each entry is:
  ```
  SCSTR  DAC  B_SCL            STRING
         DAC  6
         DTC  /STRING/
  ```
  The `DAC` count is the character length; the `DTC /.../` is the
  literal.  In x64, the analogous file is presumably `s.min` in the
  x64 repo — if not, locate via `grep -rn "DTC.*STRING\|DTC.*string"
  /home/claude/x64/`.  x64 will have the literals lowercased
  (`DTC  /string/`, DAC count = 6) in whichever source file builds
  the runtime string table.

  **Scope note:** this is a source-level change to the MINIMAL
  runtime input, not to the compiler binary.  One `s.min`-style
  file edit, rebuild via `make sbl` (not `make bootsbl` — the
  bootstrap binary needs regenerating from the patched source using
  itself as `$BASEBOL`), install, verify.  Effort is comparable to
  SN-25b/c.

  - [x] **SN-27a** -- Locate the DATATYPE string table in the x64
    source tree.  **Done 2026-04-21.**

    **Found at `/home/claude/x64/bootstrap/sbl.asm` lines 1377-1421.**
    16 entries spanning `scarr` / `sccod` / `scexp` / `scext` /
    `scint` / `scnam` / `scnum` / `scpat` / `screa` / `scstr` /
    `sctab` / `scfil` / `scfrt` / `scnrt` / `scrtn` — each a
    3-descriptor block: `d_word b_scl` (header), `d_word N` (length),
    `d_char 'c','h','a','r','s',0,...` (name as lowercase byte list).
    The table is followed by `scnmt:` at line 1422 (pointer table
    indexed by block-code at `dtype+12397`).

    **The table is NOT generated from `.min` or `.sbl` source in the
    tree** — `grep -rn "DTC.*string"` across `asm.sbl`, `lex.sbl`,
    `sbl.min`, `z.sbl` turned up zero hits; the only `"string"`
    occurrence is in a generated `err.asm` message ("179 string" —
    an error message, unrelated to DATATYPE).  The literals live
    directly in the hand-maintained `bootstrap/sbl.asm`.

    **MAJOR SCOPE FINDING — SN-27 is broader than the rung text
    estimated.**  Full SN-27 requires more than flipping 16 table
    literals.  Three additional factors discovered this session:

    **(1) `CONVERT(x, 'STRING')` parsing at `slod3` (line 8088ff).**
    The CONVERT parser takes the user's datatype string, calls
    `flstg` at line 8093 to fold it (to lowercase), then compares
    via `ident` against each `sc*` table pointer (line 8098
    `scstr`, 8109 `scint`, 8120 `screa`, etc.).  If the table
    literals flip to uppercase but `flstg` still folds to lowercase,
    **every CONVERT datatype call breaks** — the user's `'STRING'`
    gets folded to `'string'` then fails to match the now-UPPERCASE
    table.  Same for `'string'` (already lowercase, still doesn't
    match UPPERCASE).  The fold direction must flip, or the CONVERT
    path must be restructured to not pre-fold.

    **(2) `flstg` direction flip is global.**  `flstg` is called
    from six different sites — not just CONVERT.  Flipping its
    direction from add-32 to sub-32 (plus range-check inversion
    from `ch_ua..ch_uz` / `'A'..'Z'` to `ch_la..(ch_la+25)` /
    `'a'..'z'`) changes the internal canonical form of every
    identifier in the compiler.  The current x64 binary consistently
    normalises to lowercase; flipping flips the entire binary to
    uppercase normalization.

    **(3) 188 lowercase `d_char` entries throughout `sbl.asm`.**
    Every keyword/function/builtin in the identifier tables is
    stored in lowercase (`cos`, `end`, `input`, `output`, etc. —
    count confirmed via `grep -c "d_char '[a-z]" sbl.asm` → 188).
    Because `flstg` folds user input to lowercase for keyword
    lookup, these table entries must match.  If `flstg` flips to
    fold-to-upper, all 188 entries must flip to uppercase too, or
    every identifier lookup breaks.

    **Revised SN-27 scope:** this is NOT "patch 13 DTC literals,
    rebuild, done" (the original rung description's estimate).
    It's **a whole-binary re-normalization** — 16 DATATYPE
    literals + `flstg` direction + 188 keyword-table literals +
    possibly additional call sites that read table chars directly.
    Effort is **much larger** than SN-25b/c comparison suggested.

    **Three viable implementation paths, ranked by risk:**

    **Path A — Surgical output-only (narrowest).**  Leave the
    16 DATATYPE table literals lowercase.  Leave `flstg` alone.
    Leave all 188 keyword entries lowercase.  **Only change the
    `dtype` output boundary** (line 12390ff) to translate the
    returned string chars to uppercase via a new `raise` routine
    — similar to existing `RAISE2`/`flstg` but folding lower→upper.
    One self-contained function, one call site added.  Pros:
    tiny, reversible, doesn't touch 188 tables or any fold path.
    Cons: `CONVERT(x, 'STRING')` still returns lowercase match
    (so user sees UPPERCASE from DATATYPE but must use lowercase
    literal for CONVERT comparison) — that's internally inconsistent.

    **Path B — Intercept at `dtype` + CONVERT parser tweak.**
    Path A's output flip + add a parallel uppercase path at `slod3`
    so CONVERT accepts both cases.  Two small, isolated changes.
    Less inconsistent than A.  Still doesn't touch `flstg` or the
    188 keyword tables.

    **Path C — Full re-normalization (cleanest architecture, most
    work).**  Flip `flstg` direction + all 16 DATATYPE literals +
    all 188 keyword-table literals.  Single atomic change; binary
    is now uppercase-canonical throughout.  Matches x32/CSNOBOL4/
    one4all.  Proper SN-27 as originally envisioned — but requires
    ~200+ literal edits across `sbl.asm` and careful verification
    that every `d_char`-using site was accounted for.

    **Recommendation:** start with **Path A** (smallest, lowest
    risk, validates the DATATYPE-output change in isolation).  If
    gates stay green, escalate to Path B for CONVERT consistency.
    Path C is a separate, much larger commitment — worth doing
    but not in a single session.  SN-27b below should be re-scoped
    to Path A first, with SN-27c/d/e following accordingly.

    **Session context when this finding landed:** context window
    at ~88%; no patch attempted.  The bootstrap build is verified
    working (`make bootsbl` succeeds in ~3s per SN-25 notes).

  - [~] **SN-27a-history** -- git blame of x64 changes.  **Done 2026-04-21.**

    **Cheyenne Wills commit `39c9dc9` (Jan 9, 2022) is the source
    of x64's lowercase canonicalization.**  Title: *"Enable support
    for the &case keyword."*  Body:

    > Currently spitbol fails to recognize upper case source files
    > (typically failing with a message about missing the END
    > statement).  Define `.culc` in `sbl.min` so the source code
    > will fold upper case source files into lower case.  The
    > default for &case is 1.  This change allows older spitbol
    > source code that is typically in upper case to be used without
    > change while still supporting source files that are lower case.

    **Before Jan 2022, x64 was UPPERCASE-canonical like x32.**  The
    188 lowercase `d_char` entries and the `flstg` fold-to-lower
    routine are products of this one commit.  **x64 is fundamentally
    a port of x32**, and in its pre-2022 form shared x32's uppercase
    convention.  SN-27 is therefore a *revert* of 39c9dc9's
    normalization direction, not a forward-engineering change.

    **Reverting the canonicalization (the proper Path C fix):**
    the actual lever is a one-line toggle in `sbl.min`:

    ```
    -.def   .culc                 define to include &case (lc names)
    +*      .culc                 define to include &case (lc names)
    ```

    Undefining `.culc` makes the Minimal preprocessor regenerate
    the binary in uppercase-canonical form — all 188 keyword table
    entries, the DATATYPE table, and the `flstg` routine are
    regenerated mechanically from the one Minimal source pass.  No
    manual editing of 200+ literal `d_char` lines.

    **Tradeoff:** undefining `.culc` also removes `&case` keyword
    support entirely (commit message: "define to include &case").
    Under uppercase-canonical x64, `-f` loses meaning — there's no
    longer a fold pass to disable.  The 11 structural keywords
    (END, RETURN, etc.) become strictly uppercase-only.  RULES.md's
    "Always uppercase END" mandate aligns perfectly.

    **Impact on beauty.sno double-function trick:**  `shift`/`Shift`
    / `reduce`/`Reduce` / `pop`/`Pop` / `visit`/`Visit` pairs were
    the reason RULES.md adopted case-sensitive handling.  Without
    `.culc`, x64 becomes case-insensitive (fold-to-upper would happen
    always, or folding is gone entirely depending on which branch
    of the Minimal conditional compilation gets preserved).
    **Re-read `sbl.min` around `.culc` carefully before committing
    to this path** — need to understand whether the non-`.culc`
    branch preserves case-distinct labels under a different
    mechanism or collapses them all.

    **Revised SN-27 implementation plan:**
    1. Undefine `.culc` in `sbl.min` (one-line change).
    2. Run `make sbl` (NOT `make bootsbl`) so the current `bin/sbl`
       regenerates an uppercase-canonical `sbl.asm` from `sbl.min`.
    3. Verify: `sbl -b /tmp/dt.sno` (with `output=datatype('')`)
       prints `STRING` not `string`.
    4. Audit corpus `.ref` files for lowercase DATATYPE hardcodes
       (same as original SN-27g).
    5. Full gate sweep.

    **Remaining SN-27 sub-rungs (SN-27b..g) can be collapsed** —
    the `.culc` toggle is the atomic change; everything else is
    verification.  Rewrite SN-27b as "toggle `.culc`; make sbl;
    verify," delete SN-27c's mechanical-literal-patching plan
    (obviated), keep SN-27d (verify), SN-27e (RULES.md update),
    SN-27f (snobol4dotnet decision), SN-27g (corpus ref audit).

    **Risk:** the 2022 commit touched 803 lines of `sbl.asm`, 86
    lines of `sbl.lex`, so the regenerated binary differs
    substantially from pre-2022.  All existing x64-based tests
    (gates: Smoke=7, Broker=49, Broad=225, SN-7=51, SN-9c-e=207)
    must still pass against the regenerated binary.  If they
    don't, the bug isn't `.culc` — it's a separate regression in
    either scrip's expectations or a `.ref` hardcoding lowercase.

  - [ ] **SN-27b** -- Patch 13 DTC literals (plus any `DAC` length
    fields that change) to uppercase.  Keep the symbol names
    (`SCSTR` etc.) unchanged.

  - [ ] **SN-27c** -- Rebuild via `make sbl` using the current
    `bin/sbl` as `$BASEBOL`.  Install as `bin/sbl`.  (If `make sbl`
    can't be driven because the x64 build rules differ, fall back
    to the `.sbl → .asm` regeneration path per SN-25c.)

  - [ ] **SN-27d** -- Verify: `sbl -b /tmp/dt.sno` (with `dt.sno`
    from this session: `output=datatype('')` etc.) prints `STRING`
    not `string`.  All 13 categories correct.

  - [ ] **SN-27e** -- Update RULES.md DATATYPE table: x64 row flips
    from "lowercase" to "UPPERCASE"; add x32 row (UPPERCASE);
    delete the "authoritative, intentional per runtime" language
    (it's now uniform, not divergent).  Remove the portable-test
    complexity from the same section — tests can now rely on
    uppercase across every runtime we care about (snobol4dotnet
    excluded as a noted exception; see below).

  - [ ] **SN-27f** -- Decide what to do with snobol4dotnet.  Two
    options:
      (i) flip snobol4dotnet to UPPERCASE too, closing the whole
          compat gap.  Requires changes in the .NET runtime
          (dotnet uses `ToLowerInvariant()` per RULES.md).
      (ii) leave snobol4dotnet as the lone lowercase runtime.  Its
          users know the convention; portable tests can still
          REPLACE-to-uppercase cheaply.
    Lon to choose.  Either way, this rung is about x64, not .NET.

  - [ ] **SN-27g** -- Corpus `.ref` file audit.  Any
    `.ref` under `corpus/programs/snobol4/` that hardcodes lowercase
    DATATYPE strings (`'string'`, `'pattern'` etc.) in expected
    output will flip correctness when x64 is rebuilt.  Sweep,
    identify, update.  Cross-reference with
    `GOAL-DATATYPE-PORTABLE-TESTS.md` (S-1) — the two goals
    converge on the same audit.

  **Gate:** after SN-27c, all existing gates must stay green with
  the new UPPERCASE x64.  Smoke PASS=7, Broker PASS=49, SN-7 beauty
  self-host PASS=51/51, Broad corpus PASS=225/225.  Any regression
  is a `.ref` file that hardcoded lowercase and needs updating
  (SN-27g), not a scrip runtime bug.

  **Risk:** LOW.  The change is mechanical; the tree already
  defended against case differences via D-002/D-003 (ignore-point
  in monitor, case-insensitive test comparisons).  The worst-case
  failure mode is a set of `.ref` files that need regeneration,
  which is exactly the kind of fix the portable-test goal already
  targets.

  **Dependencies:** none.  Orthogonal to SN-25 and SN-26.  Can be
  worked in parallel with either.

- [ ] **SN-26** -- True beauty.sno self-host (4-way monitor).
  **Rung opened 2026-04-20.**  Gated on SN-25.

  **Done-when:** on the same form of `beauty.sno` that SPITBOL
  processes cleanly, scrip reproduces SPITBOL's output byte-for-byte
  in all three modes.  The 4-way monitor (`scrip-monitor`, IR/SM/JIT
  + CSN) reports zero DIVERGE and zero "IR vs CSN" variance over the
  full statement trace.

  **Work done this session — scouting / triage, no fix yet:**

  1. **Oracle self-host behavior documented.**
     `beauty.sno` does not self-host cleanly under *any*
     implementation today, as committed to corpus:
     - `sbl -b beauty.sno < beauty.sno` (`cwd=beauty/`): runs 765
       statements, emits 25 lines, crashes at line 781 (`END`) with
       *error 021 — function called by name returned a value*.
     - `snobol4 -b beauty.sno < beauty.sno`: emits 7 lines (header),
       halts at line 770 with *Error 8 — Variable not present where
       required*.
     - `scrip --ir-run beauty.sno < beauty.sno` (with `SNO_LIB=
       /home/claude/corpus/programs/snobol4/beauty`): emits 10 lines
       including beauty's own `Parse Error` via `mainErr1`.
     Different errors in different places — each implementation has
     a distinct triggering mismatch vs beauty's own `Parse` pattern.

  2. **Clean reference form of beauty.sno obtained.**  Lon provided
     the original SNOBOL4 source bundle (`/home/claude/originals/
     SNOBOL4/`), which predates the corpus entirely.  The original
     `beauty.sno` is 630 lines (the corpus version is 781 — the
     delta is the `ppArg*` / `--auto` / profiles machinery added
     later).  Removing the three SNOBOL4-only compat shims
     (`is.inc`, `FENCE.inc`, `io.inc`) is safe: `IsSpitbol`/
     `IsSnobol4`/`IsType` have no references from any of beauty's
     16 other includes; `FENCE(...)` in beauty.sno is SPITBOL's
     native pattern operator, not the stub; `input_`/`output_` are
     the SNOBOL4 polyfills and beauty.sno never calls them.  The
     staged clean copy lives at `/home/claude/orig_test/`.

  3. **Under-SPITBOL errors cataloged.**  The clean `orig_test`
     beauty.sno under `sbl -b` (default fold-to-lower) trips on
     `semantic.inc`: duplicate labels.  `shift`, `reduce`, `pop`
     are defined alongside `Shift`, `Reduce`, `Pop`; with folding
     on, all pairs collapse to the lowercase form and SPITBOL
     rejects the duplicates.  This is the double-function trick
     (the whole *point* is to distinguish `shift` from `Shift`), so
     the correct invocation is `sbl -bf` — which is blocked by
     SN-25.

     Only **4 case-collision pairs** exist across all beauty source
     (including corpus beauty dir): `shift`/`Shift`, `reduce`/
     `Reduce`, `pop`/`Pop`, `visit`/`Visit`.  A path-A rewrite
     (rename the lowercase members to avoid collision under fold)
     is tractable but would fight the idiom — SN-25 is the cleaner
     solution.

  4. **First scrip divergence already located via the monitor.**
     On the corpus beauty.sno self-input, `scrip-monitor --monitor`
     (built this session via `bash scripts/build_csnobol4_archive.sh
     && make scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a`)
     reported: IR/SM/JIT agreed for 151 statements, then at
     **stmt 152 (label `G1`, line 169)**:
     ```
     IR vs SM (1 var(s) differ):
       UTF_Array   IR=ARRAY('797163616:32490')  SM=ARRAY('124,2')
     IR vs JIT (1 var(s) differ):
       UTF_Array   IR=ARRAY('797163616:32490')  JIT=ARRAY('124,2')
     ```
     `--ir-run` holds a corrupted `UTF_Array` dim string
     (`'797163616:32490'` — looks like a descriptor or pointer value
     stringified into the ARRAY dimension argument), while SM and
     JIT agree on the sensible `'124,2'`.  Feels like a DT_E /
     descriptor-aliasing bug of the class SN-6b addressed — lives
     in the `--ir-run` path between the preceding `ARRAY('1:4')`
     (line 151) and the first read of `UTF_Array` at line 169.
     **Not fixed this session.**  Good starting point once SN-25
     unblocks the oracle.

  **Rename and install (deferred until SN-25 unblocks testing):**

  Per Lon's direction: the current fancy corpus beauty.sno (781
  lines, `ppArg*` / `--auto` / profiles) becomes `beautifier.sno`
  (same directory).

  **Install a single self-contained `beautiful.sno` — no -INCLUDE
  at all.**  Concatenate the 16 `.inc` files of the upstream bundle
  (minus the 3 SNOBOL4-only compat shims `is.inc`/`FENCE.inc`/
  `io.inc`) into a single flat file in the original inclusion order,
  bracketing each with a banner comment.  One file + one input.
  Hermetic test artefact.  Keep case sensitive (the whole zip is
  written case-sensitive; Lon writes all SNOBOL4 that way).  Staged
  this session at `/home/claude/orig_test/beautiful.sno` (1521
  lines); sanity-check rebuild:
  ```bash
  BEAUTY=/home/claude/originals/SNOBOL4/sno/beauty.sno
  INC=/home/claude/originals/SNOBOL4/inc
  OUT=/home/claude/orig_test/beautiful.sno
  first=$(grep -n '^-INCLUDE' $BEAUTY | head -1 | cut -d: -f1)
  last=$(grep -n '^-INCLUDE' $BEAUTY | tail -1 | cut -d: -f1)
  head -$((first-1)) $BEAUTY > $OUT
  for f in global case assign match counter stack tree ShiftReduce \
           TDump Gen Qize ReadWrite XDump semantic omega trace; do
    printf '\n*%s\n*                 %s.inc\n*%s\n' \
           "$(printf '=%.0s' {1..80})" "$f" "$(printf '=%.0s' {1..80})" >> $OUT
    cat $INC/$f.inc >> $OUT
  done
  tail -n +$((last+1)) $BEAUTY >> $OUT
  ```

  **"Take the zip as-is with one or two minor fixes to get working.
  It has run for decades."**  So: the program is trusted; any
  behavior difference between `sbl -bf beautiful.sno < beautiful.sno`
  and `scrip <mode> beautiful.sno < beautiful.sno` is a **scrip bug**.
  SPITBOL is the oracle.

  - [ ] **SN-26a** -- Rename `demo/beauty.sno` → `demo/beautifier.sno`
    in corpus (the fancy --auto / ppArg* form).  Also move any doc
    strings that name "beauty.sno" for that behavior.

  - [x] **SN-26b** -- Install `beauty.sno` + its minimal .inc set in
    `corpus/programs/snobol4/demo/beauty/`.  **Done 2026-04-20.**
    Lon provided the original SNOBOL4 bundle as an upload
    (`SNOBOL4.zip`) containing `sno/beauty.sno` (630 lines) and a
    large `inc/` directory.  Approach revised from the SN-26 opening
    plan: **do NOT concatenate** into a single `beautiful.sno` —
    keep `-INCLUDE` directives and place the minimal set of `.inc`
    files alongside `beauty.sno` in one folder.  That is what Lon
    directed this session.

    **Landed at `corpus/programs/snobol4/demo/beauty/` (17 files):**
    - `beauty.sno` (627 lines — 630 minus the 3 `-INCLUDE` lines for
      the SNOBOL4-only compat shims `is.inc`, `FENCE.inc`, `io.inc`;
      trailing lowercase `end` fixed to uppercase `END` per RULES.md).
    - 16 minimal `.inc` files: `global.inc`, `case.inc`, `assign.inc`,
      `match.inc`, `counter.inc`, `stack.inc`, `tree.inc`,
      `ShiftReduce.inc`, `TDump.inc`, `Gen.inc`, `Qize.inc`,
      `ReadWrite.inc`, `XDump.inc`, `semantic.inc`, `omega.inc`,
      `trace.inc`.

    **Reference form:** `beauty.sno` itself is the `.ref` — it is
    already beautified, so `scrip <mode> beauty.sno < beauty.sno`
    should reproduce `beauty.sno` byte-for-byte.

    **Oracle for this work:** CSNOBOL4 (not SPITBOL).  The 4-way
    `scrip-monitor` (IR / SM / JIT / CSN) is the arbiter.  SN-25
    (SPITBOL `-f` bootstrap fix) **deferred** — it is not required
    to make progress on self-host, because CSNOBOL4 `-bf` handles
    the case-sensitive double-function-trick correctly through the
    first 1073 statements of `beauty.sno < beauty.sno`.

    **Corpus commit:** `d85fd7e` (pushed to origin/main).

  - [ ] **SN-26c** -- Self-host under the 4-way monitor.  Run
    `scrip-monitor --monitor beauty.sno < beauty.sno` (with
    `SNO_LIB=/home/claude/corpus/programs/snobol4/demo/beauty` and
    `cd` to that directory).  Start with the first DIVERGE and walk
    each in turn.  Fix; rerun; walk the next DIVERGE.  Continue
    until monitor reports all-agree across IR/SM/JIT/CSN.  Keep
    gates green at each step (Smoke=7, Broker=49, Broad
    corpus=225/225, SN-7 driver 51/51).

    **Baseline measured 2026-04-20 at corpus `d85fd7e`:**

    - **CSNOBOL4 `-bf`** on `beauty.sno < beauty.sno`: produces
      33 lines of output (comment header echoes correctly) then
      SEGVs at `beauty.sno:616 stmt 1074` (`snoLine = INPUT` in
      main02).  **Memory CLI switches do NOT help** — tested
      `-P 500k -S 100k -d 4m` with identical SEGV at same stmt.
      This is a real CSN bug, not a memory limit.  Past the Goal
      file's previously-recorded CSN error location (was stmt 1072
      on the 781-line corpus/demo beauty.sno), so the 627-line form
      gets 2 statements further before the same `snoLine = INPUT`
      path trips.

    - **CSNOBOL4 `-b`** (case-fold): fails with duplicate-label
      errors on the double-function-trick pairs (`shift`/`Shift`,
      `reduce`/`Reduce`, `pop`/`Pop`, `visit`/`Visit`).  Expected
      — beauty.sno requires case-sensitive labels.

    - **scrip `--ir-run`** on `beauty.sno < beauty.sno`: produces
      **0 stdout lines**; stderr floods with cascading `Error 1`
      (GE first argument is not numeric) starting at stmt 1063,
      1069, 1071, 1083, 1085, 1097, 1098, 1224, ....  All three
      modes (IR/SM/JIT) fail to even emit the comment-header echo.

    - **4-way `scrip-monitor --monitor`** first divergence:
      ```
      scrip --monitor: DIVERGE at stmt 153
        path: [START] -> [G1]
        IR  last_ok=?    i=1       (outlier)
        SM  last_ok=1    i=2
        JIT last_ok=1    i=2
      ```
      IR is the outlier here — SM and JIT agree.  Start fix at
      `driver/interp.c` path for whatever `global.inc` statement
      lands at stmt 153 in the [START] -> [G1] arc.

    - **Also seen in monitor stderr** (~40+ occurrences):
      `sm_lower: unresolved label 'error'` and
      `sm_lower: unresolved label 'err'`.  Forward-reference gap
      in `sm_lower.c` for labels named `error` / `err` referenced
      before their textual definition (a `global.inc` pattern).
      Separate from the stmt 153 divergence; fix both.

    **Useful follow-up (small):** the IR `last_ok=?` field on
    DIVERGE is uncaptured at the snapshot boundary — see
    `sync_monitor.c` IR snapshot code.  Fixing this (one line)
    removes a class of reporting ambiguity while debugging SN-26.

    **Possible scrip CLI switches (for future investigation):**
    scrip currently lacks visible `--help` output.  CSNOBOL4's
    memory switches (`-d`, `-P`, `-S`) were tried on the CSN
    oracle and do not help; scrip's default arena / pattern stack
    sizes may or may not be configurable — if scrip hits memory
    limits during self-host runs, check for equivalents, or adjust
    `arena_init` / default stack sizes in the runtime.  Not a
    current blocker — the stmt 153 divergence fires well before
    any memory pressure.

    **2026-04-21 session — oracle prerequisite established.**

    Lon's direction: *"Does both SPITBOL and CSNOBOL4 run the beauty
    self-host?  That is the first two steps for this goal.  Then we
    get ours working once we prove the code works spotless."*

    Answer verified this session: **NO, neither oracle runs beauty
    self-host cleanly today.**  Full matrix:

    | Oracle | Mode | Result |
    |--------|------|--------|
    | SPITBOL | `-b` (fold) | `error 217 — syntax error: duplicate label` at beauty.sno(566) on the double-function-trick pairs.  Expected — beauty requires case-sensitive labels. |
    | SPITBOL | `-bf` (case-sensitive) | `No END statement found in source file(s).`  SN-25 bug — `gnv10` lowercase keyword table in `bootstrap/sbl.asm`. |
    | CSNOBOL4 | `-b` (fold) | Same class of failure as SPITBOL `-b` — duplicate labels. |
    | CSNOBOL4 | `-bf` | 32 stdout lines (comment header echoes correctly), then SEGV at `beauty.sno:616 stmt 1074` (`snoLine = INPUT` in `main02`).  Deterministic regardless of `-P 500k -S 100k -d 4m` or `-P 2m -S 500k -d 10m` or bare. |
    | scrip `--ir-run` | | 0 stdout lines; stderr cascading `Error 1 — GE first argument is not numeric` from stmt 1063 onward. |

    **Implication for SN-26c's current plan:** the goal-file's stated
    protocol — "use CSNOBOL4 as oracle via 4-way `scrip-monitor`, walk
    DIVERGEs one at a time" — assumes CSN produces an authoritative
    reference trace to diverge *from*.  With CSN SEGVing at stmt 1074,
    the CSN lane of the 4-way monitor produces only 32 lines of
    ground truth before going dark.  scrip divergences beyond that
    point have no oracle to validate against.

    **The first two steps must therefore be:**

    1. **Close SN-25** (SPITBOL `-bf` bootstrap fix in
       `bootstrap/sbl.asm` `gnv10`).  Root cause already pinpointed
       in the SN-25 block below; fix plan SN-25a..e enumerated.
    2. **Close CSNOBOL4 SEGV at stmt 1074** (`snoLine = INPUT`
       in `main02` on line 616 of beauty.sno).  New sub-rung —
       open as **SN-26c-pre-CSN** when next session picks it up.
       Starting point: run CSN under gdb/valgrind on beauty.sno
       self-input; capture the signal-11 site.  The statement is
       `snoLine = INPUT :F(mainEnd)` — a bare file read driving the
       main loop.  Possibly a CSN INPUT handler / file descriptor
       / line-length issue on the specific content at line 616 of
       its own self-input.

    After both oracles produce clean self-host output, then (and only
    then) does scrip's divergence become meaningful to debug.  The
    `i=1` vs `i=2` at stmt 153 stays queued as SN-26c step 3.

    **Verification done this session:**

    - **Source integrity confirmed.**  All 16 `.inc` files in
      `corpus/programs/snobol4/demo/beauty/` are **byte-identical**
      to the original SNOBOL4 bundle ZIP Lon re-uploaded
      (`Gen.inc`, `Qize.inc`, `ReadWrite.inc`, `ShiftReduce.inc`,
      `TDump.inc`, `XDump.inc`, `assign.inc`, `case.inc`,
      `counter.inc`, `global.inc`, `match.inc`, `omega.inc`,
      `semantic.inc`, `stack.inc`, `trace.inc`, `tree.inc`).
      `beauty.sno` is 627 lines vs the ZIP's 630 — delta is exactly
      the 3 `-INCLUDE` lines for SNOBOL4-only compat shims
      (`is.inc`, `FENCE.inc`, `io.inc`), intentionally dropped per
      SN-26b.  Trailing `END` uppercase in both.  The zip "has run
      for decades" (Lon's words) and the repo source is exactly
      that code.  **Confirmed: divergences are scrip bugs, not
      source corruption.**

    - **Step-counter analysis for stmt 153 divergence (diagnostic,
      not yet fixed).**  Traced `g_ir_steps_done` vs
      `g_sm_steps_done` across the monitor's `sm_interp_run_steps`
      repeated invocations.  Both counters increment once per
      source statement by design:
      - IR: `driver/interp.c:4069`, top of `while (s)` dispatch.
      - SM: `sm_interp.c:218`, inside `SM_STNO` opcode handler.
        `SM_STNO` is emitted exactly once per source statement by
        `lower_stmt` (`sm_lower.c:920`).
      At n=153, both should stop after executing stmt 153 (G1 =
      `i = i + 1`).  IR's `i=1` matches that expectation; SM/JIT's
      `i=2` does not.  The G1 backedge `:S(G1)` jumps to
      `SM_LABEL` at position 1753, which is **after** the
      `SM_STNO` at 1752 — so re-iterations via the backedge do
      NOT re-tick the SM step counter.  This should make IR and
      SM agree, but they don't.  **Smoking gun candidate
      identified but not yet confirmed:** `sm_interp.c:214` has
      `static int g_sm_stno = 0;` (file-scope, never reset between
      monitor invocations).  Same at `sm_codegen.c:205` with
      `g_sm_stno_jit`.  These statics accumulate across the
      monitor's 153 repeated `sm_interp_run_steps` calls.
      Whether this actually perturbs `g_sm_steps_done` (which IS
      reset per call) requires reading `comm_stno`'s body in
      `snobol4.c` and checking whether `comm_stno` has any
      feedback into the step-limit path.  **Next session:**
      confirm or refute this hypothesis; if confirmed, add
      `g_sm_stno = 0` / `g_sm_stno_jit = 0` reset to
      `sm_interp_run_steps` / `sm_jit_run_steps` entry.  If
      refuted, the bug is elsewhere.

      **Important caveat:** this diagnostic work becomes moot if
      the stmt 153 divergence resolves as a side-effect of the
      SN-25 / CSN-SEGV oracle fixes above, because the monitor
      may well report a different first-DIVERGE once the CSN lane
      produces meaningful output past stmt 32.  Do not invest
      further in this diagnostic until the two oracle prereqs
      close.

  - [~] **SN-26c-pre-CSN** -- CSNOBOL4 SEGV at `beauty.sno:616
    stmt 1074` (`snoLine = INPUT` in `main02`).

    **Opened 2026-04-21.**  Prerequisite for SN-26c's 4-way
    monitor lane to produce authoritative ground truth beyond 32
    lines of comment header.  CSNOBOL4 `-bf` is deterministic at
    this site — `-P 500k -S 100k -d 4m` / `-P 2m -S 500k -d 10m`
    / bare all SEGV identically.  Signal 11 at stmt 1074 points
    to the INPUT read path on the specific content of beauty.sno
    read at that iteration.  Repo: `snobol4ever/csnobol4`.

    Entry point: `gdb /home/claude/csnobol4/snobol4 --args ./snobol4
    -bf -I<beauty-dir> beauty.sno < beauty.sno` and look at the
    INPUT / stream / `popen2` handling in `ptyio_obj.c` / `io.c` /
    `stream.c`.  Lon prior session noted the corpus's 781-line
    fancy `beauty.sno` also SEGV'd CSN at stmt 1072; the 627-line
    form trips the same path two statements later.  Implication:
    it's a function of the total statement history by time stmt
    1074's INPUT fires, not the specific 627-vs-781 content
    difference.  A bare repro (simple program, many iterations,
    `X = INPUT :F(END)` loop) may or may not trigger; start there.

  - [~] **SN-26c-pre-CSN-a** -- Session 7 (2026-04-21) characterization.

    **SEGV is deterministic across all optimization levels** (`-O0`,
    `-O1`, `-O2`, `-O3`, `-O3 -g`, `-Og -g`).  All produce exactly
    32 stdout lines (the comment header of `beauty.sno`), exit 1,
    `beauty.sno:616: Caught signal 11 in statement 1074 at level 0`.
    This rules out uninitialized-memory bugs sensitive to optimizer
    layout.

    **gdb perturbs the process — do not trust gdb-attached runs
    as characterization of this bug.**  Running the same binary
    with `set args -b -f -I. beauty.sno` / `run < beauty.sno`
    under gdb produces *compile-time* "Previously defined label"
    errors on the `shift`/`Shift` / `reduce`/`Reduce` / `pop`/`Pop`
    / `VISIT` / `VISIT_1` / `VISITEND` pairs at `semantic.inc:16-18`
    and in the generated pseudo-input — but the *same binary* run
    outside gdb accepts the labels and reaches stmt 1074 before
    SEGV.  Either gdb's `set args` tokenization, its handling of
    `< beauty.sno` stdin redirection, or its `LD_PRELOAD` /
    address-space setup changes `CASECL` effective state at compile
    time.  **Use a core dump instead:** `ulimit -c unlimited`,
    run outside gdb, `gdb snobol4_dbg core`.

    **GENVUP is working correctly** — the duplicate-label mechanism
    in `CMPILE` at `snobol4.c:958-962` correctly skips `CERR2`
    ("Previously defined label") under `-f` because `GENVUP` at
    `isnobol4.c:4474-4484` returns without folding when
    `D_A(CASECL) == 0`.  Label pairs `shift`/`Shift` etc. are
    compiled as distinct entries.  The compile-time behavior is
    not the bug.

    **The SEGV is a runtime bug, not a compile-time bug.**  32
    lines of stdout proves the compiled program started executing.
    `main02` reads INPUT repeatedly; after ~32 output lines
    (roughly corresponding to the comment header echoing through
    the parse/pretty-print path), something in statement-1074's
    code path dereferences bad memory.

    **Source-of-truth for any CSNOBOL4 patch:** `v311.sil`.  The
    files `snobol4.c` and `isnobol4.c` carry the header
    `/* generated from v311.sil by genc.sno on 04/12/2026 ... */`.
    Do **not** patch the generated C.  All patches go in `v311.sil`
    and are rebuilt via `make -f Makefile2 xsnobol4`.

    **v311.sil landmarks already identified:**
    - `GENVUP` at `v311.sil:1317-1323` — 6 SIL lines, generates the
      11-line block at `isnobol4.c:4474-4484`.  Maps 1:1:
      `AEQLC CASECL,0,,GENVAR` → `if (D_A(CASECL)==0) BRANCH(GENVAR)`,
      `XRAISP SPECR1` → `RAISE1(SPECR1)`, etc.
    - `CMPILE` (the outer label-scanner) generates the code at
      `snobol4.c:922` (`static int CMPILE(...)`).  The `goto L_CERR2`
      at line 962 corresponds to wherever CMPILE raises emsg2 in
      the SIL.  Locate in `v311.sil` by searching for `EMSG2` or
      `"Previously defined"` adjacency if needed.

    **Debug artifacts left in place for next session:**
    ```
    /home/claude/csnobol4/snobol4        (release O3, no debug info)
    /home/claude/csnobol4/snobol4_dbg    (O3 -g, debug + release behavior)
    /home/claude/csnobol4/snobol4_O0     (O0 -g, same release behavior)
    ```
    All three reproduce the SEGV identically outside gdb.

    **Next-session pickup:**
    1. `ulimit -c unlimited && cd beauty_dir && /home/claude/csnobol4/snobol4_dbg -b -f -I. beauty.sno < beauty.sno` — produce core
    2. `gdb /home/claude/csnobol4/snobol4_dbg core` — bt, identify the exact frame
    3. From that frame, cross-reference back to the SIL PROC name
       in `v311.sil` that generated it
    4. Patch in `v311.sil`, `make -f Makefile2 xsnobol4`, re-test

  - [ ] **SN-26c-pre-CSN-b** -- Bare-minimum repro for the SEGV.
    Open after SN-26c-pre-CSN-a identifies the crashing frame.
    Goal: strip beauty.sno down to a ~20-line reproducer that still
    crashes CSN at an analogous statement.  Makes the bug filable
    upstream (Phil Budne) without requiring the beauty corpus.

  - [ ] **SN-26d** -- Add `test_smoke_beauty_self_host.sh` — a gate
    script that runs `scrip <mode> beauty.sno < beauty.sno` in all
    three modes from `corpus/programs/snobol4/demo/beauty/`, diffs
    output against `beauty.sno` itself (the source IS the ref — it
    is already beautified), PASS=3 FAIL=0.  Makes "beauty
    self-hosts" a standing gate.

- [ ] **SN-28** -- Compact DESCR_t: 16 → 8 bytes via arena aliasing,
  dual-mode (32-bit offsets / 64-bit pointers).  **Opened 2026-04-21.**

  **Motivation:** today's `DESCR_t` is 16 bytes:
  ```c
  typedef struct DESCR_t {
      DTYPE_t  v;      /* 4 bytes — type tag  */
      uint32_t slen;   /* 4 bytes — string len cache */
      union {          /* 8 bytes — pointer/int/real */
          char *s;  int64_t i;  double r;  void *ptr;
          struct _PATND_t *p;  struct _ARBLK_t *arr;
          struct _TBBLK_t *tbl;  struct _DATINST_t *u;
      };
  } DESCR_t;
  ```
  (verified: `sizeof(DESCR_t)=16`, align 8 at `descr.h:50`).

  A SNOBOL4 workload holds hundreds to thousands of live `DESCR_t`
  cells at steady state: the NV table (global variables), NAM stack
  (per-match lvalue captures), argument stacks for user calls,
  generator state for BB_PUMP, array/table slots, and per-statement
  temporaries.  Halving cell size **directly halves** L1/L2 cache
  footprint for variable access, NV table walks, and arg marshalling
  — the three hot-path operations that dominate interpreter time on
  large corpus (Porter, claws5, beauty).

  **Reference model — Silly SNOBOL4 arena aliasing:**

  Silly (`src/silly/types.h:61-68`) uses a faithful SIL DESCR: 9
  bytes packed, with `a.i` holding an arena offset when the value
  points to a block.  One flat 128 MB `mmap` slab at `arena_base`;
  `A2P(off) → ptr` and `P2A(ptr) → off` translate the two views.
  All string blocks, array blocks, pattern nodes live *inside* the
  arena — so every "pointer" is a 32-bit offset, and the full DESCR
  is effectively: tag (1 byte) + value-or-offset (4 bytes) + size
  (4 bytes).  SIL's nine-byte cell shrinks further in our world
  because we don't need the SIL `v` size field on every cell — we
  keep it only on block titles.

  **Target 8-byte DESCR_t (design sketch):**
  ```c
  typedef struct DESCR_t {
      uint32_t tag_flags;   /* low 8: DTYPE_t; high 24: slen or flags */
      uint32_t payload;     /* arena offset, small int, or float32 bits */
  } DESCR_t;    /* exactly 8 bytes, align 4 */
  ```
  or (if `slen` needs >16 bits for long strings):
  ```c
  typedef struct DESCR_t {
      uint8_t  tag;         /* DTYPE_t */
      uint8_t  flags;       /* reserved / GC bits */
      uint16_t slen;        /* string len, 0 = use strlen() */
      uint32_t payload;     /* arena offset or small int */
  } DESCR_t;
  ```
  Payload is either:
  - **`DT_I` (small integer):** 32-bit value directly (int32_t).
    Integers > 2³¹-1 need arena-boxed full int64_t (DT_I_LONG tag,
    or payload points at an 8-byte int block).
  - **`DT_R` (real):** either 32-bit float directly (loses double
    precision vs today), or arena-boxed double.  Decide per
    measurement.  SNOBOL4 programs rarely need double precision —
    start with float32 inline.
  - **`DT_S, DT_P, DT_A, DT_T, DT_DATA` (pointer types):** arena
    offset (32-bit) into the arena slab.
  - **`DT_SNUL, DT_FAIL`:** payload = 0.

  **Dual-mode (Lon's requirement):**

  Two compile-time modes, selected by a single `#define`:
  ```
  DESCR_MODE_64    — today's 16-byte DESCR_t, raw pointers (default)
  DESCR_MODE_32    — 8-byte DESCR_t, arena offsets
  ```
  Every DESCR access that touches the payload goes through macros:
  ```c
  D_TAG(d)         → d.tag              (both modes)
  D_INT(d)         → d.i  | A2P(d.payload) depending on mode
  D_STR(d)         → d.s  | (char*)A2P(d.payload)
  D_SET_STR(d, p)  → d.s = p | d.payload = P2A(p)
  ```
  Today's code touches `d.s`, `d.i`, `d.v`, `d.slen` directly in
  ~hundreds of sites across `src/runtime/x86/`, `src/driver/interp.c`,
  `src/frontend/*/`.  Step SN-28a is the rote translation to macros;
  the 8-byte mode rides on top once macros are in place.

  **Honest cost assessment:**

  This is a **large** retrofit — not a one-session rung.  Scope:

  1. **Arena infrastructure.**  one4all today uses Boehm GC
     (`<gc/gc.h>`, `GC_strdup`, `GC_MALLOC`) with raw pointers.
     Silly's arena is a single flat mmap with bump allocation plus
     compacting GC (GC/GCM procedures).  Adopting the arena means
     either (a) displacing Boehm with a new bump+compact allocator,
     or (b) keeping Boehm but routing all DESCR-referenced blocks
     through it so their offsets are stable.  Option (a) is cleaner;
     option (b) is incremental but breaks if Boehm ever moves blocks
     (it doesn't compact by default, so this is safer than it sounds).

  2. **Macro-ize every DESCR field access.**  Today's `d.s`, `d.i`,
     `d.v`, `d.slen` occur in ~hundreds of sites.  A mechanical sed
     pass can do most; the rest need human review (union aliasing
     cases — `d.slen = 0` before `d.ptr = ...` in DT_E construction).

  3. **Integer overflow.**  `int64_t` payloads today cover full
     SNOBOL4 integer range.  Compact mode forces arena-boxing for
     values outside `[INT32_MIN, INT32_MAX]`.  Measure: probably
     rare in typical workloads, but the boxing path must exist.

  4. **Real precision.**  `double` → `float` in-line loses 23 bits
     of mantissa.  Programs doing numerical work (rare in SNOBOL4,
     but not zero) will see wrong answers unless we arena-box.  Same
     decision as #3.

  5. **Debugging & tooling.**  gdb pretty-printers, valgrind
     interpretation of the arena, `.ref` file expectations — all
     need review.

  **Payoff:**

  - **Cache footprint.**  Halved.  Measured Porter at ~2100 live
     DESCRs at peak: 33 KB → 16 KB.  L2 fits easily in both cases,
     but L1 (32 KB typical) goes from tight to comfortable.
  - **NV table walk speed.**  Should measure 15-25% faster on
     variable-heavy programs (beauty, claws5) from halved
     cache-line pressure alone.
  - **GC pause.**  Fewer bytes to scan.
  - **Prepares the ground for `scrip` on 32-bit targets** (WASM,
     embedded) where 64-bit pointers are dead weight.

  **Ladder SN-28a..h:**

  - [ ] **SN-28a** -- Macro-ize DESCR field access.  Introduce
    `D_TAG(d)`, `D_STR(d)`, `D_SET_STR(d, p)`, `D_INT(d)`,
    `D_SET_INT(d, v)`, `D_REAL(d)`, `D_PAT(d)`, `D_ARR(d)`,
    `D_TBL(d)`, `D_DATA(d)` in `descr.h`.  Default implementations
    expand to today's raw-pointer form (`d.s`, `d.i`, etc.) — no
    behavior change.  Mechanically rewrite every direct field access
    across `src/runtime/x86/`, `src/driver/`, `src/frontend/*/` to
    go through the macros.  Gate: Smoke=7, Broker=49, Broad=225/225,
    SN-7=51, JIT parity=207 — all unchanged, byte-identical.  **This
    rung is pure refactoring; no semantic change.**  Likely
    ~500-1000 lines touched mechanically, maybe a dozen human-review
    sites.

  - [ ] **SN-28b** -- Introduce arena infrastructure in one4all.
    Port `arena_init`, `arena_alloc`, `A2P`, `P2A` from Silly
    (`src/silly/arena.c`, `src/silly/arena.h`) to
    `src/runtime/x86/one4all_arena.{c,h}` — **without** yet switching
    DESCR_t.  Initialize the arena at `scrip` startup; keep using
    Boehm for everything else.  Gate: unchanged.

  - [ ] **SN-28c** -- Migrate string allocation through the arena.
    `GC_strdup("foo")` → `arena_strdup("foo")`.  All string payloads
    live in the arena; their raw pointers remain stable (arena is
    non-compacting at this stage — just bump allocate).  DESCR_t
    stays 16 bytes; we're staging.  Gate: unchanged.

  - [ ] **SN-28d** -- Migrate PATND, ARBLK, TBBLK, DATINST allocation
    through the arena.  Same pattern: arena pointers are stable, so
    `d.p`, `d.arr`, `d.tbl`, `d.u` continue to work unchanged.
    Gate: unchanged.

  - [ ] **SN-28e** -- Introduce `DESCR_MODE_32` build flag.  New
    8-byte `DESCR_t` layout behind the flag; `A2P/P2A` expansion of
    the `D_*` macros when enabled.  Build both modes; verify
    `DESCR_MODE_64` is byte-identical to pre-SN-28 behavior.  Gate:
    both modes pass all existing gates.  This is the hard rung —
    the int64→int32 boxing and float→arena-box for >32-bit ints
    and doubles gets wired here.

  - [ ] **SN-28f** -- Performance gate.  Measure Porter, claws5,
    beauty self-host under both modes.  If 32-bit mode is not at
    least 10% faster on `--sm-run` or `--jit-run`, investigate: the
    retrofit is worth doing only if the cache savings materialize.

  - [ ] **SN-28g** -- Documentation.  Update `RULES.md` with the
    DESCR_MODE selection convention and the arena invariants.
    Update this Goal file with measured numbers.

  - [ ] **SN-28h** -- Decide default.  Based on SN-28f numbers and
    the state of the retrofit, either:
      (i)  flip default to `DESCR_MODE_32` and retire 64-bit mode;
      (ii) keep 64-bit default, offer 32-bit as build option;
      (iii) abandon 32-bit mode if the retrofit cost outweighs the
           gain.
    Lon to choose.

  **Dependencies:** orthogonal to SN-25, SN-26, SN-27.  Can be worked
  in parallel with any of them.  SN-28a (macro-ize) alone is a
  defensible standalone cleanup — it improves code readability
  regardless of whether SN-28b..h ever land.

  **Risk:** MEDIUM-HIGH.  The retrofit touches every file that
  handles values.  Gate discipline (byte-identical outputs through
  SN-28a..d) is the only defense against silent corruption.  If any
  rung breaks Porter or beauty `--ir-run`, abandon the rung and
  restore prior HEAD.

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
| corpus/programs/snobol4/beauty/ | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=49 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state

**HEADs:** one4all @ `9c2246d6` · corpus @ `88be074` · .github @ pending
this commit · x64 @ `5843f5d` (untouched this session — SN-25 closed
won't-fix; no further x64 work planned).

**Gates (last verified 2026-04-20, not re-measured sessions 3-7):**
Smoke **7** · Broker **49** · SN-7 drivers **51/51** · Broad corpus **225/225**
in all three modes · SN-9c-e JIT parity **207/207/207** on crosscheck.

**Current step: SN-26c-pre-CSN-a.**  Session 7 closed SN-25 entirely
per Lon's directive ("never going to worry about ingress for old
products, just we'll use that technique for one4all").  SPITBOL and
CSNOBOL4 fold inside `GTNVR` / `GENVUP` gated on `&case` / `CASECL` —
that is the settled design and it stays.  The ingress-at-lex rule in
RULES.md has been scoped to one4all only.

Session 7 characterized the CSNOBOL4 SEGV at beauty stmt 1074:
- Deterministic across `-O0`..`-O3`, with and without debug info
- gdb perturbs arg handling and produces misleading compile-time
  errors (Previously defined label) that do not appear outside gdb
- GENVUP at `isnobol4.c:4474-4484` / `v311.sil:1317-1323` is
  working correctly — labels like `shift`/`Shift` are intentionally
  distinct under `-f`
- The SEGV is a runtime bug that fires ~32 stdout lines into
  execution, not a compile-time issue
- CSN source of truth is `v311.sil`; generated files
  (`snobol4.c`, `isnobol4.c`) carry a header marking them generated
  and must never be patched directly

**Order of work next session:**
1. Produce a core dump: `cd beauty_dir; ulimit -c unlimited;
   /home/claude/csnobol4/snobol4_dbg -b -f -I. beauty.sno < beauty.sno`
2. `gdb /home/claude/csnobol4/snobol4_dbg core`, `bt 50`, identify
   the crashing C frame
3. Cross-reference the frame back to its SIL PROC in `v311.sil`
4. Patch `v311.sil`, rebuild via `make -f Makefile2 xsnobol4`
5. Re-verify: 32 lines → at least 33 lines (progress), ideally
   `beauty.sno < beauty.sno` runs to completion with exit 0

**Reproduce the baseline:**
```bash
DEST=/home/claude/corpus/programs/snobol4/demo/beauty
cd $DEST
/home/claude/csnobol4/snobol4 -b -f -I. beauty.sno < beauty.sno
# expect: 32 stdout lines, exit 1, "Caught signal 11 in statement 1074 at level 0"
```

**After SN-26c-pre-CSN-a:** return to SN-26c step 3 — walk the
4-way monitor divergences.  First known DIVERGE at stmt 153:
IR `UTF_Array='797163616:32490'` vs SM/JIT `'124,2'` (see SN-26
block).  Plus ~40 `sm_lower: unresolved label 'error'/'err'`
warnings to clean up.

**Latent follow-ups** (small, not gating):
- SN-8a latent: named-args path in `SM_PAT_USERCALL` all-E_VAR stash never
  consumed; SM-side XATP arg-name stash gap. Defensible as SN-8b if hit.
- SN-22/23 cleanups: `NAME_push` return `void *` → `void`; `cache_get_fresh`
  template purity (SN-6c root cause — bb_cap self-heals, other box types
  still vulnerable if they store in-flight scalars).
- SN-26 scout: `IR last_ok=?` on DIVERGE — uncaptured at snapshot boundary
  in `sync_monitor.c`, one-line fix.
