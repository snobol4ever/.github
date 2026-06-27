# ARCHIVE-LANG-SNOBOL4-HISTORY.md — forensic archive

Full forensic history of the SNOBOL4 frontend ladder — snapshotted
2026-04-22 when the active goal file (`GOAL-LANG-SNOBOL4.md`) was
trimmed to reduce session-startup context cost.

The active goal file now carries:
- Header, setup, architecture, scrip-monitor protocol
- Closed rungs as one-liner status rows
- Full detail on the active rung only
- Current state + next-session pickup

Everything below is the pre-trim file verbatim, preserved for
reference.  Git history is the authoritative source; this file
just makes the detail retrievable without digging through commits.

---

# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** SCRIP
**Done when:** beauty.sno self-hosts cleanly under all three modes (--run,
--run, --run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh   # PASS=49
```

---

## Architecture reminder

```
.sno -> sno_parse() -> Program* [LANG_SNO]
    --run  -> execute_program() -> interp_eval()   tree-walk
    --run  -> sm_lower() -> SM_Program -> sm_interp_run()
    --run -> sm_lower() -> SM_Program -> sm_codegen() -> sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

Step 1 (--monitor) runs EVERY iteration, unconditionally.
Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/SCRIP/scripts/build_csnobol4_archive.sh
make -C /home/claude/SCRIP scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 -- ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/SCRIP/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 -- only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/SCRIP/scrip --run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
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
  into `name_commit_value` at SN-21e. SCRIP @ `8964586e`.

- [x] **SN-21** — Unified `NAME_t` + flat NAM stack. One lvalue concept, one
  push/pop API, one `bb_cap` box for `.` / `$` / `NRETURN` / `*fn()`. Landed
  across SN-21a..e. SCRIP @ `8964586e`.

- [x] **SN-17** — Porter stemmer gap closed (2026-04-19). `--run` and
  `--run` both 100.00% / 23531 on porter.sno. Landed via SN-17a (new
  `SM_PAT_USERCALL` opcode, `f2cf3494`) + SN-17d (FAIL propagation in
  `bb_usercall`, `9d9d2dd3`). SN-17b, SN-17c deferred — not required.

- [x] **SN-17a** — Added `SM_PAT_USERCALL` opcode. SCRIP @ `f2cf3494`.

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
  Porter reached 100.00% / 23531 in both modes. SCRIP @ `9d9d2dd3`.

- [x] **SN-6** — Full corpus: PASS=225/225 in all three modes (2026-04-20).
  Closed via a one-word gate-script fix at
  `test_interp_broad_corpus_and_beauty.sh:67`. SN-6a (new `SM_PAT_REFNAME`
  opcode for `--run` self-recursive patterns) landed with it.

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

- [x] **SN-6c** — Recursive pattern NAM corruption closed for `--run`
  via SN-23d-follow-up (`has_pending` reset at top of CAP_α). SCRIP @
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
  `expr_eval` flipped PASS. Final rung SN-23h at SCRIP @ `a556167b`.
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
  `h_push_expr` handler mirroring `sm_interp.c`. Porter `--run` from
  7979-line diff to 0-line diff vs ref. Same DT_E union-aliasing
  discipline as SN-6b.

- [x] **SN-9b** — Closed remaining codegen handler gaps (2026-04-19).
  SCRIP @ `f8b06dc6`. Wired `SM_BB_PUMP` and `SM_BB_ONCE` (Icon/Raku
  generators + Prolog backtracking); other audit opcodes classified as
  stale / cross-mode / never-emitted. `test/raku_gather.scrip` byte-
  identical under `--run` and `--run`.

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
  **CLOSED 2026-04-21 (session 7) -- won't fix.**  Per Lon's directive:
  "Never going to worry about ingress for old products, just we'll
  use that technique for SCRIP."

  Sessions 2-6 explored patching SPITBOL x64 at `bootstrap/sbl.asm`
  `gnv10` and at the SIL level in `sbl.min:23093`.  Patches compiled
  and ran correctly in-session but were reverted (generated-code rule
  for the former, architectural redirect for the latter).  Session 7
  closed the rung entirely after Lon clarified that the ingress-at-lex
  principle applies to SCRIP only.

  **Consequence:** SPITBOL cannot run programs that rely on case-
  sensitive structural keywords (programs requiring the double-function
  trick).  Those programs must run under CSNOBOL4 `-bf` per RULES.md.

  Full session-by-session forensic record is in the git history:
  ```
  git log --all --oneline -- GOAL-LANG-SNOBOL4.md | grep -i SN-25
  ```
  commits `85e57cf` (session 5 redirect), `321880d` (session 4
  revert), `5843f5d` (x64 revert), `79f59a7` (session 7 close).

  Sub-rungs SN-25a, SN-25b, SN-25b-retry, SN-25c, SN-25d, SN-25e,
  SN-25f, SN-25.x32: all closed with SN-25.

- [ ] **SN-27** -- UPPERCASE DATATYPE for SPITBOL x64.  **Opened
  2026-04-21.**  Origin: session discovered x32 returns UPPERCASE
  DATATYPE while x64 returns lowercase — a previously-unrecorded
  fork.  Unifying on UPPERCASE (the same choice SCRIP, CSNOBOL4,
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
  explicitly chose UPPERCASE for SCRIP because:
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
    SCRIP.  Proper SN-27 as originally envisioned — but requires
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
     - `scrip --run beauty.sno < beauty.sno` (with `SNO_LIB=
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
     `--run` holds a corrupted `UTF_Array` dim string
     (`'797163616:32490'` — looks like a descriptor or pointer value
     stringified into the ARRAY dimension argument), while SM and
     JIT agree on the sensible `'124,2'`.  Feels like a DT_E /
     descriptor-aliasing bug of the class SN-6b addressed — lives
     in the `--run` path between the preceding `ARRAY('1:4')`
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

    - **scrip `--run`** on `beauty.sno < beauty.sno`: produces
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
    | scrip `--run` | | 0 stdout lines; stderr cascading `Error 1 — GE first argument is not numeric` from stmt 1063 onward. |

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

  - [~] **SN-26c-pre-CSN-a2** -- Session 8 (2026-04-22) findings.

    **"gdb perturbation" mystery SOLVED — not a real bug.**  The
    session 7 note speculated "ASLR / libc init / LD_PRELOAD"
    changed CASECL under gdb.  Actual cause: in gdb, `run < file`
    **replaces** previously-set args — gdb treats the argument
    line starting at `run` as a fresh argv.  When session 7 did
    `set args -b -f -I. beauty.sno; run < beauty.sno`, the program
    received `argc=1` (no args), so `-f` never ran, CASECL stayed
    at its default of 1, and the double-function pairs got folded
    → spurious "Previously defined label" errors.

    **Correct gdb incantation** (verified with minimal argv-dump
    binary and with snobol4_dbg):
    ```
    file /home/claude/csnobol4/snobol4_dbg
    handle SIGSEGV stop nopass
    run -b -f -I. beauty.sno < beauty.sno
    ```
    Args directly on the `run` line; stdin redirect stays at end.

    **SEGV backtrace captured cleanly:**
    ```
    #0  SCIN1         isnobol4.c:11459    D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)
    #1-#10  SCIN / SCIN1 alternation, 5 levels of pattern-match recursion
    #11 SCNR          isnobol4.c:12604
    #12 SCAN          isnobol4.c:12674
    #13 INVOKE        isnobol4.c:3177
    #14 INTERP        isnobol4.c:3492
    #15 BEGIN         isnobol4.c:14203
    #16 snobol4_run   main.c:73
    #17 main          main.c:97
    ```

    **SIL origin:** `v311.sil:3611` — `SALT1 GETDC LENFCL,PDLPTR,3*DESCR`
    (scan-alt backtrack: pop length-failure history from PDL).

    **Key memory state at SEGV** (from `gdb_full.cmd` dump):
    | global  | .a.i value | interpretation |
    |---------|------------|----------------|
    | PDLPTR  | 192 (0xc0) | **tiny int; should be heap pointer** |
    | PDLHED  | 96  (0x60) | **tiny int; should be heap pointer** |
    | PDLEND  | 0x55d29f0bebf0 | correct heap pointer, intact |
    | NAMICL  | 18 | |
    | NHEDCL  | 18 | |
    | MAXLEN  | 49 | |
    | LENFCL  | 0x55d29f09fbe0 | real heap pointer |
    | sizeof(struct descr) | 16 | |

    The 256 bytes of PDL stack memory ending at PDLEND are **all
    zeros** — nothing was written into the scan-history region
    this execution.

    **Bug characterization:**  PDLPTR and PDLHED hold small integers
    where they should hold heap pointers.  PDLEND (real pointer) is
    intact.  PDLPTR - PDLHED = 96 bytes = 6 descriptor slots = 2
    scan frames (each is 3 descriptors per `INCRA PDLPTR,3*DESCR` at
    `v311.sil:3551/3563/3588`).  Arithmetic is consistent with a
    healthy SCAN PUSH sequence — so **the corruption happened
    BEFORE this SCAN call fired**, not during it.  At SCAN entry
    line 2716 (`MOVD PDLHED,PDLPTR`), PDLPTR was already the garbage
    value 96; the MOVD faithfully propagated that to PDLHED.  Two
    subsequent INCRA +48 each → 192.

    **SIL inventory of PDLPTR writes:**  `MOVD` / `INCRA` / `DECRA`
    only, plus bulk `PUSH`/`POP`.  No direct `SETAC` / `SETAV` /
    `PUTAC` / `SPCINT` assignments to PDLPTR anywhere in `v311.sil`.
    So the tiny values must have propagated through one of those
    legitimate-looking ops from a corrupted source — most likely a
    bad `POP` that restored a saved value from the interpreter
    stack (which itself got smashed by pattern-match code indexing
    past its frame).

    **Debug binary built:**  `/home/claude/csnobol4/snobol4_dbg`
    via `make -f Makefile2 OPT='-O0 -g' xsnobol4`.  Rebuild
    procedure (post-top-level-clean accident on 2026-04-22):
    ```
    cd /home/claude/csnobol4
    git restore . && git clean -fd
    bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
    rm -f *.o xsnobol4
    make -f Makefile2 OPT='-O0 -g' xsnobol4
    cp xsnobol4 snobol4_dbg
    ```

    **⚠ Do NOT run top-level `make clean` in csnobol4** — it
    wipes `Makefile2` (generated from `Makefile2.m4`) AND the
    `snobol4` binary, creating a bootstrap chicken-and-egg
    (Makefile2 regenerates data.c2 by running `snobol4 -b gendata.sno`
    against v311.sil).  Recovery: `git restore .` then rerun
    `build_csnobol4_oracle.sh`.

    **csnobol4 catches SIGSEGV with its own handler** at
    `lib/init.c:688` (`signal(SIGSEGV, err_catch)`).  `err_catch`
    sets `D_A(SIGNCL)=sig` and calls `SYSCUT(NORET)` — longjumps
    back to the interpreter main loop to print the error and exit
    cleanly.  **No core dump is ever produced**, regardless of
    `ulimit -c unlimited`.  The session 7 pickup note step 1
    ("produce a core dump via ulimit -c unlimited") is therefore
    obsolete — use gdb with `handle SIGSEGV stop` instead, which
    catches the signal before `err_catch` runs.

  - [~] **SN-26c-pre-CSN-a3** -- Pin the exact PDLPTR-corruption
    write site.

    **Opened 2026-04-22.  Session 9 (2026-04-22 continued):
    hardware watchpoints do not function in this sandbox —
    plan revised.**

    **Session 9 findings:**

    1. **SEGV reproduced identically to session 8.**  32 stdout
       lines, exit 1, `beauty.sno:616: Caught signal 11 in
       statement 1074 at level 0`.  Crash site `SCIN1` at
       `isnobol4.c:11459` (`D(LENFCL) = D(D_A(PDLPTR) + 3*DESCR)`).

    2. **Values at SEGV match session 8 exactly:**
       `res.pdlptr[0].a.i = 0xc0 (192)` ·
       `res.pdlhed[0].a.i = 0x60 (96)` ·
       `res.pdlend[0].a.i = 0x5599e48efbf0` (valid heap ptr) ·
       `res.lenfcl[0].a.i = 0x5599e48d0be0` (valid heap ptr).
       PDLPTR and PDLHED are tiny integers where they should be
       heap pointers; PDLEND/LENFCL intact.

    3. **Hardware watchpoints silently fail in this environment.**
       An *unconditional* `watch res.pdlptr[0].a.i` with the
       unambiguous address `0x56119c238250` fires **zero** times
       across the full run, yet PDLPTR transitions from `0x0`
       (BSS zero-init at `main`) to `0xc0` (SEGV).  Verified
       against a trivial standalone program (`long g; g=1; g=2;
       g=3;`) — `watch g` under `gdb -batch` also fires zero
       times while printing `g=3`.  **Cause:** container kernel
       restricts `PTRACE_POKEUSER` / DR0-DR7 debug register
       access; `warning: Error disabling address space
       randomization: Invalid argument` is the corroborating
       symptom in every gdb run.  `set can-use-hw-watchpoints 0`
       (software watch) works correctly on the trivial test but
       single-steps every instruction — intractable for the
       million-instruction beauty.sno workload.

    4. **Consequence:** the session-8 plan
       (`watch ... if PDLPTR < 0x100000`) is unworkable in this
       sandbox.  Two alternative strategies queued below.

    **Strategy A — AddressSanitizer (recommended first).**  If
    the root cause is a buffer overrun from an adjacent `res`
    field clobbering `res.pdlptr[0]` (consistent with session-8's
    finding that the PDL stack region near PDLEND is all zeros —
    nothing was written via the legitimate `INCRA`/`DECRA` path),
    ASan will name the write site directly.  ASan write-buffer-
    overflow detection does not rely on hardware watchpoints.

    ```bash
    cd /home/claude/csnobol4
    rm -f *.o xsnobol4
    make -f Makefile2 \
         OPT='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
         LDOPT='-fsanitize=address' xsnobol4
    cp xsnobol4 snobol4_asan

    cd /home/claude/corpus/programs/snobol4/demo/beauty
    ASAN_OPTIONS=abort_on_error=1:halt_on_error=1 \
        /home/claude/csnobol4/snobol4_asan -b -f -I. \
        beauty.sno < beauty.sno
    ```

    CSNOBOL4's `Makefile2` may need the `LDOPT` flag added; if
    it doesn't accept it, patch `Makefile2.m4` to pipe `$(OPT)`
    through to the link line.  Some CSNOBOL4 globals are
    intentionally aligned oddly; `ASAN_OPTIONS=detect_odr_violation=0`
    may be needed.  Validate the ASan build runs a trivial
    `output='ok'` program before attempting beauty self-host.

    **Strategy B — Breakpoint sweep at the 31 known PDLPTR write
    sites.**  Bounded volume, no hardware-watchpoint requirement.
    Full inventory (verified session 9 from `grep -n "D_A(PDLPTR)
    [+-]=\\|D(PDLPTR) =\\|PUSH(PDLPTR\\|POP(PDLPTR" isnobol4.c`):

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

    Gdb script pattern: break at each line with a `commands
    {silent; printf PDLPTR/PDLHED; continue}` handler, redirect
    log to a file, grep for the first "sane → tiny" transition.
    Note the three `D(PDLPTR) = D(PDLHED)` sites (12276, 12300,
    12577) specifically: if PDLHED is *already* corrupt at those
    sites, PDLPTR inherits the bad value via legitimate
    structure assignment.  Watch PDLHED at every breakpoint in
    parallel — its corruption may predate PDLPTR's.

    **PUSH/POP semantics** (from `include/macros.h:152-153`):
    ```
    #define PUSH(x)  D(cstack+1) = D(x); cstack++; OFCHK()
    #define POP(x)   cstack--; UFCHK(); D(x) = D(cstack+1)
    ```
    Each is a full-descriptor copy, so POP writes 16 bytes into
    the target descriptor — if `cstack+1` is corrupt, POP
    propagates corruption without a direct `PDLPTR = <value>`
    statement.

    **Staged gdb scripts left in /home/claude** (next-session
    scratch; not committed):
    - `gdb_segv.cmd` — basic SEGV reproduction with args fix
    - `gdb_pdl.cmd` — PDL bounds dump at SEGV
    - `gdb_full.cmd` — full descriptor + memory dump at SEGV
    - `gdb_watch.cmd` — obsolete (hardware watch doesn't fire)
    - `gdb_probe_segv.cmd` — session 9: prints
      PDLPTR/PDLHED/PDLEND/LENFCL at SEGV (reproduces session 8
      numbers exactly)
    - `gdb_watch_pdlptr.cmd` — session 9: conditional hardware
      watch attempt, fires zero times
    - `gdb_watch_all.cmd` — session 9: unconditional hardware
      watch attempt, also fires zero times (proves the hardware
      watchpoint mechanism itself is broken, not a conditional-
      expression issue)
    - `gdb_addr_watch.cmd` — session 9: address-typed
      (`*(long*)$addr`) hardware watch, also fires zero times
    - `hw_test.c` / `hw_test` — session 9: trivial standalone
      proof that hardware watchpoints fail on any program here

    **Order of work for next session:**
    1. Rebuild `snobol4_asan` with `-fsanitize=address`.  Validate
       it runs a trivial program first.
    2. Run the beauty self-host repro under ASan; capture the
       named write site.
    3. Map the C line back to its `v311.sil` PROC, patch source
       of truth, rebuild via `make -f Makefile2 OPT='-O0 -g'
       xsnobol4`.
    4. If ASan reports nothing (legitimate-looking struct copy
       from already-corrupt source), fall back to Strategy B:
       the 31-site breakpoint sweep.

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

  1. **Arena infrastructure.**  SCRIP today uses Boehm GC
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

  - [ ] **SN-28b** -- Introduce arena infrastructure in SCRIP.
    Port `arena_init`, `arena_alloc`, `A2P`, `P2A` from Silly
    (`src/silly/arena.c`, `src/silly/arena.h`) to
    `src/runtime/x86/SCRIP_arena.{c,h}` — **without** yet switching
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
    least 10% faster on `--run` or `--run`, investigate: the
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
  rung breaks Porter or beauty `--run`, abandon the rung and
  restore prior HEAD.

---

## Key files

| File | Role |
|------|------|
| src/frontend/snobol4/snobol4.y | Bison grammar |
| src/frontend/snobol4/snobol4.l | Flex lexer |
| src/driver/interp.c | --run tree-walk |
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

**HEADs:** SCRIP @ `9c2246d6` · corpus @ `88be074` · .github @ pending
this commit · x64 @ `5843f5d` (untouched this session — SN-25 closed
won't-fix; no further x64 work planned).

**Gates (last verified 2026-04-20, not re-measured sessions 3-7):**
Smoke **7** · Broker **49** · SN-7 drivers **51/51** · Broad corpus **225/225**
in all three modes · SN-9c-e JIT parity **207/207/207** on crosscheck.

**Current step: SN-26c-pre-CSN-a3.**  Session 9 (2026-04-22
continued) reproduced session 8's SEGV exactly and discovered
that **hardware watchpoints silently fail in this
sandbox/container environment.**  Unconditional
`watch res.pdlptr[0].a.i` fires zero times while PDLPTR
transitions from `0x0` to `0xc0` — confirmed against a trivial
standalone program, so the mechanism itself is broken, not the
expression.  Software watchpoints work but single-step every
instruction, intractable for beauty.sno's million-instruction
workload.  Next session: switch to AddressSanitizer (Strategy A)
or a 31-site breakpoint sweep (Strategy B).  Full inventory of
PDLPTR write sites captured in the SN-26c-pre-CSN-a3 block.

Session 8 (2026-04-22) solved the "gdb perturbation" mystery
(just `run < file` wiping `set args`), captured the clean SEGV
backtrace, and characterized PDLPTR/PDLHED as small integers
(192/96) while PDLEND remains a valid heap pointer.  The PDL
corruption predates the crashing SCAN invocation.

Session 7 closed SN-25 entirely per Lon's directive ("never going
to worry about ingress for old products, just we'll use that
technique for SCRIP").  SPITBOL and
CSNOBOL4 fold inside `GTNVR` / `GENVUP` gated on `&case` / `CASECL` —
that is the settled design and it stays.  The ingress-at-lex rule in
RULES.md has been scoped to SCRIP only.

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
1. **Strategy A — AddressSanitizer rebuild** (recommended first):
   ```bash
   cd /home/claude/csnobol4
   rm -f *.o xsnobol4
   make -f Makefile2 \
        OPT='-O0 -g -fsanitize=address -fno-omit-frame-pointer' \
        LDOPT='-fsanitize=address' xsnobol4
   cp xsnobol4 snobol4_asan
   ```
   If `Makefile2` doesn't accept `LDOPT`, patch `Makefile2.m4` to
   pipe `$(OPT)` through to the link line.  Validate with a
   trivial `output='ok'` program first.
2. Run beauty self-host repro under ASan; capture the named
   write site.
3. Map the C line back to its `v311.sil` PROC via the
   `/* line NNN */` markers; patch `v311.sil` (NOT the generated
   C), rebuild via `make -f Makefile2 OPT='-O0 -g' xsnobol4`.
4. If ASan is silent (corruption came in via a legitimate-
   looking struct copy from already-bad source), fall back to
   **Strategy B — 31-site breakpoint sweep** on the PDLPTR writes
   enumerated in the SN-26c-pre-CSN-a3 block.  Watch PDLHED in
   parallel; the three `D(PDLPTR) = D(PDLHED)` sites (lines
   12276/12300/12577) may simply propagate a PDLHED that was
   corrupted earlier.
5. Re-verify beauty self-host past stmt 1074 once the patch lands.
6. Gate sweep once the CSN SEGV closes.

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
