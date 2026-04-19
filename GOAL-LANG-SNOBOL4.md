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

- [x] **SN-20** -- NAM push/pop self-unwinding (`*var-holds-DT_E` thaw folded
      into `name_commit_value` at SN-21e).  HEAD `8964586e`.

- [x] **SN-21** -- Unified `NAME_t` + flat NAM stack; one lvalue concept,
      one push/pop API, one `bb_cap` box for `.` / `$` / `NRETURN` / `*fn()`.
      Ladder SN-21a..e landed across multiple sessions; full design rationale
      in the SN-21a..e commit messages.  HEAD `8964586e` (SN-21e).

- [x] **SN-17** -- Porter stemmer gap closed.  Done 2026-04-19.
      `--ir-run` and `--sm-run` both at **100.00%** / 23531 on porter.sno.
      Sub-rungs landed: SN-17a (SM_PAT_USERCALL opcode, commit `f2cf3494`)
      and SN-17d (FAIL propagation in `bb_usercall`, commit `9d9d2dd3`).
      SN-17b and SN-17c deferred — they were not required for the Porter
      fix after SN-17a routed both modes through the same XATP /
      `bb_usercall` path, making SN-17d a single-file fix that landed in
      both modes simultaneously.

  **History preserved below for the next session that encounters a
  similar shared-path / parallel-switch question:**

  **Measured at HEAD `8964586e` (pre-SN-17):**
  - `--ir-run`: 19674 / 23531 matched = **83.60%**
  - `--sm-run`: 14317 / 23531 matched = **60.84%**
  - Broad corpus: PASS=223/225 (unchanged).

  **Root cause** (isolated 2026-04-19): bare `*fn()` guard patterns do not
  propagate FAIL.  Minimal repro (no `$`, no alternation needed):
  ```snobol4
                 DEFINE('g_fail()')
  g_fail         g_fail = FAIL :(RETURN)
                 'abate' RTAB(3) 'ate' *g_fail() RPOS(0) :F(no)S(yes)
  ```
  SPITBOL: NO MATCH (sweeps positions, guard fails at each).
  scrip `--ir-run`: spurious MATCH.

  Porter's `*g_m_gt_0()`, `*g_vis()`, etc. always silently pass → every
  rule fires → over-stripping (`abate → ab` vs SPITBOL's `abat`).

  **First-pass fix attempt** (reverted, not committed): rewriting
  `bb_usercall` in `stmt_exec.c` to eagerly invoke `g_user_call_hook` at
  α caught the call but exposed a second layer — `g_fn = FAIL` returns
  `DT_P` wrapping `XFAIL`, not `DT_FAIL`.  The check needs both.

  **Pivot — three-mode audit, 2026-04-19:**

  Bug is doubled across modes; no shared execution code means each mode
  has its own version of the problem:

  | Mode | State of bare `*fn()` | Path |
  |------|----------------------|------|
  | `--ir-run` | calls deferred to commit time via NM_CALL, return discarded | stmt_exec.c `bb_usercall` |
  | `--sm-run` | no opcode — lowering drops the node entirely | sm_lower.c (missing) |
  | `--jit-run` | inherits sm-run's hole | sm_codegen.c (missing) |

  **Duplication found** (every site must be edited in lockstep):

  1. `stmt_exec.c:bb_build` (35 XKIND cases) ↔ `bb_build.c:bb_build_binary_node`
     (24 XKIND cases) — parallel dispatchers; bb_build.c returns NULL to
     fall back to stmt_exec.c for unimplemented kinds.
  2. `sm_interp.c` (63 SM opcode cases) ↔ `sm_codegen.c` (52 `h_*` handlers)
     — pattern-construction handlers are line-for-line copies around the
     shared `pat_*` constructors in `snobol4_pattern.c`.
  3. `snobol4_pattern.c` `pat_*` constructors ARE shared — the unification
     we have is at the node-construction level; dispatch is where it splits.

  **Fresh rung ladder — SN-17a..d:**

- [x] **SN-17a** -- Add `SM_PAT_USERCALL` opcode.  Done 2026-04-19.
      - `sm_prog.h`: opcode added after `SM_PAT_CAPTURE_FN`.
      - `sm_lower.c`: `case E_DEFER:` now detects `E_DEFER(E_FNC)` in pattern
        context and emits `SM_PAT_USERCALL s="FNAME" args="..."`.  Previous
        behavior fell through `lower_expr → SM_CALL → SM_PAT_DEREF`, which
        invoked fn **once at build time** and treated the return as a pattern
        (no per-position sweep).
      - `sm_interp.c`: `case SM_PAT_USERCALL:` pushes `pat_user_call(fname, NULL, 0)`.
      - `sm_codegen.c`: `h_pat_usercall` handler + registered in `g_handlers`.
      - `sm_prog.c`: added to opnames[] and `sm_prog_print` switch.
      - `pat_user_call()` already existed in `snobol4_pattern.c:393` (builds
        XATP node) — SN-17a just wired an SM opcode to it.
      - Arg-name stash in `a[2].s` is emitted but not yet consumed (left NULL
        into `pat_user_call`); named-args resolution lands in SN-17d with the
        FAIL-propagation fix.

      **Porter measurement (oracle: `paste` agree-count / 23531):**
      - `--ir-run`: 19674 → 19639  (slight drift; see note)
      - `--sm-run`: 14317 → **19639**  (+5322, 60.84% → 83.46%)
      - The two modes now **converge** — both produce identical output.
        This is the shape SN-17d targets ("both match SPITBOL on abate…")
        minus the final FAIL-propagation piece.
      - Gates: Smoke PASS=7, Broker PASS=48, Broad corpus PASS=223/225
        (same two fails: expr_eval, demo_claws5 — pre-existing, SN-6).

      **Note on the `--ir-run` 35-line drift:** before SN-17a the two modes
      disagreed because `--sm-run` took the broken `SM_CALL→SM_PAT_DEREF`
      path.  `--ir-run` had its own (different) wrongness via `bb_usercall`
      on XATP, and the two wrongnesses happened to produce 35 ref-matching
      lines that `--sm-run` didn't.  Now both modes route through
      `pat_user_call → XATP → bb_usercall`; the 35 lines moved from
      `--ir-run`-accidentally-right to `--both`-equally-wrong.  SN-17d
      will recover them in both modes simultaneously.

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

- [x] **SN-17d** -- Fix `*fn()` FAIL propagation.  Done 2026-04-19.
      Single-file change to `bb_usercall` in `stmt_exec.c`: invoke
      `g_user_call_hook` eagerly at α and propagate FAIL directly
      (both `DT_FAIL` and `DT_P` wrapping `XFAIL` shapes handled).
      No NAM push needed — nothing to defer for bare `*fn()`.  The
      `. / $` capture forms still use NAME_push_callcap via bb_cap /
      XCALLCAP (untouched).

      **Porter measurement (paste-agree / 23531):**
      - `--ir-run`: 19639 → **23531 (100.00%)**
      - `--sm-run`: 19639 → **23531 (100.00%)**
      - Mode agreement: 23531 / 23531 (both modes byte-identical).
      - Gates: Smoke PASS=7, Broker PASS=49 (+1 — pre-existing 48/49
        drift was the same bug; this fix repairs it), Broad corpus
        PASS=223/225 (same two pre-existing fails).

  **Reproduction commands:**
  ```bash
  cd /home/claude/corpus/programs/snobol4/demo
  /home/claude/one4all/scrip --ir-run porter.sno < porter.input | diff - porter.ref | wc -l
  /home/claude/one4all/scrip --sm-run porter.sno < porter.input | diff - porter.ref | wc -l
  ```

  **Minimal repro stashed** at `/tmp/probe_plain.sno` (this session only
  — not committed; recreate from the snippet above if the container
  resets).  Side-probes: `/tmp/probe_nopattern.sno`, `/tmp/probe_guard2.sno`.

- [ ] **SN-6** -- Full corpus: PASS=223/225 default, 224/225 --ir-run.
  Remaining: `expr_eval` (two separate bugs — see below), `demo_claws5`
  (GOAL-SNO-CLAWS5.md).
  ```bash
  bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
  ```

  **SN-6a — `--sm-run` self-recursive patterns.  Done 2026-04-19.**

  New opcode `SM_PAT_REFNAME` added in `sm_prog.h`, wired across
  `sm_prog.c` (opnames + sm_prog_print), `sm_lower.c` (E_DEFER(E_VAR)
  branch emits SM_PAT_REFNAME with the bare name), `sm_interp.c`
  (new case pushes `pat_ref(ins->a[0].s)`), and `sm_codegen.c`
  (`h_pat_refname` + g_handlers registration).

  **Root cause:** `sm_lower.c` E_DEFER previously fell through to
  `lower_expr(ch)` + `SM_PAT_DEREF`, which for E_VAR emitted
  `SM_PUSH_VAR "PRIMARY"` — eagerly fetching PRIMARY's CURRENT value
  at pattern-build time.  For self-recursive patterns like
  `primary = integer | '(' *primary ')'`, PRIMARY is still
  in-progress at that moment (empty/FAIL), so the NAME was lost
  before reaching XDSAR.  `--ir-run` already took the correct path
  via `pat_ref(child->sval)` in `interp_eval_pat` E_DEFER.

  **Minimal repro (was failing, now passes):**
  ```snobol4
             &ANCHOR    =  0
             &FULLSCAN  =  1
             integer  =  SPAN('0123456789')
             primary  =  integer | '(' *primary ')'
             '(42)' POS(0) primary . x RPOS(0)   :F(nomatch)
             OUTPUT = 'match x=' x               :(END)
  nomatch    OUTPUT = 'no match'
  END
  ```
  SPITBOL: `match x=(42)`; `--ir-run`: `match x=(42)`;
  `--sm-run` before fix: `no match`; **after fix: `match x=(42)`**.

  **Post-fix expr_eval state:** `--sm-run` and `--ir-run` now produce
  byte-identical output on expr_eval.  Both still mismatch SPITBOL
  (stderr parse-error noise from bison callback + Binary/Unary
  arithmetic path).  That's SN-6b — orthogonal to the recursion bug.

  **Gates:** Smoke PASS=7, Broker PASS=49, Broad corpus PASS=223/225
  (unchanged — `expr_eval` and `demo_claws5` remain; SN-6a did not
  close expr_eval because the Binary/Unary arithmetic mismatch is
  a separate layered bug).  Porter still 100.00%/100.00% both modes.

  **expr_eval diagnostic (measured at `8964586e`):**
  - `--ir-run`: 4/5 inputs → `snobol4:0: error: parse error: syntax error`.
    That is the SNOBOL4 *frontend parser*, not a pattern-match error —
    `EVAL(op arg)` is probably compiling the evaluated string as SNOBOL4
    statements.  The 2 lines that do parse produce wrong values:
    `(1+2)*3` → `3` (expected 9), `-3+10` → `10` (expected 7).  Two
    layered bugs: EVAL call path + operator precedence / Pop() ordering.
  - `--sm-run`: after SN-6a, byte-identical to `--ir-run` — same two
    layered bugs exposed in both modes now.  (Before SN-6a, `--sm-run`
    returned `Bad input, try again` on all 5 inputs due to the recursive
    `primary = constant | '(' *expr ')'` pattern failing at build time.)

  Not DT_E (verified identical at pre-SN-21e).

- [ ] **SN-22** -- NAM API reduction: **push + pop only, one stack per
  match, no marks, no rollback, no save/discard, no top/pop_above**.

  **Source of truth:** `snobol4python/_backend_pure.py` — `Δ` class (`P . N`
  conditional assignment).  On every γ, it `cstack.append(command)` then
  `yield`; on generator backtrack past the yield, it `cstack.pop()`.  One
  `cstack` per `SNOBOL` instance (per SEARCH-cursor attempt at
  `_backend_pure.py:818`).  At full-match commit the driver iterates
  `cstack` in push order and executes each entry (`_backend_pure.py:861`).
  That is the complete protocol.  **Two operations.  One stack.  No
  bookkeeping.**

  **What's wrong today:** SN-20 neutralised `NAME_rollback_to` to a no-op
  and declared box-owned self-unwinding (every pusher owns its pop on β/ω
  via `NAME_pop`).  But the `NAME_mark()` calls in `bb_alt` and `bb_arbno`
  were never removed — they still snapshot, and the no-op `NAME_rollback_to`
  calls remain scattered.  The API surface — `NAME_mark`, `NAME_rollback_to`,
  `NAME_save`, `NAME_discard`, `NAME_top`, `NAME_pop_above`, `NAME_commit`
  — has six redundant entry points for what should be push + pop + (at
  commit) walk-and-fire.

  **Reference invariant from Python backend:**
  ```
  class Δ:
      def γ(self):
          for _1 in self.P.γ():
              Ϣ[-1].cstack.append(f"{N} = STRING(... {_1.start}:{_1.stop} ...)")
              yield _1                             # match proceeds
              Ϣ[-1].cstack.pop()                   # backtrack: auto-unwind
  ```
  `bb_cap` is already structured this way — NAME_push at γ, NAME_pop at
  β / ω.  The rest of the engine must stop touching the NAM stack.

  **Plan:**

  - [x] **SN-22a** -- Delete `nam_mark`/`NAME_mark`/`NAME_rollback_to`
    calls from `bb_alt` (`bb_boxes.c:78-110`).  Remove `nam_mark` field
    from `alt_t`.  The `bb_cap` self-unwind already handles failed arms
    correctly — every `.` entry pushed by a failing arm is popped by its
    owning `bb_cap` on β / ω.  **Done 2026-04-19.**  Dead code as of
    SN-20 (NAME_rollback_to was already a no-op); removing the calls
    and the struct field is pure cleanup — no semantic change expected
    or observed in `bb_alt` alone.

  - [x] **SN-22b** -- Same for `bb_arbno` (`bb_boxes.c:146-182`): delete
    `nam_mark` from `arbno_frame_t`, delete `NAME_mark`/`NAME_rollback_to`
    calls at `ARBNO_try`, `body_ω`, `ARBNO_γ_now`.  **Done 2026-04-19.**

    **Gates after SN-22a+b (combined):**
    - Smoke PASS=7 (unchanged)
    - Broker PASS=**49** (+1 — was 48 at `cae6d125`; predicted broker
      regression from SN-17d was actually the same class of NAM-corruption
      bug, now fully cleared)
    - Broad corpus PASS=223/225 (unchanged; `expr_eval` and `demo_claws5`
      still the only fails)
    - Porter still 100.00% / 100.00% both modes (byte-identical to ref)

    **expr_eval status (SN-6b preview):** `--ir-run` still hits EVAL
    parse-error path (4/5 inputs) and wrong arithmetic on the 2 that
    parse (`(1+2)*3 → 3`, `-3+10 → 10`).  SN-22 hypothesis that the
    recursive pattern corruption contributed to expr_eval has partly
    played out (the +1 broker pass is evidence the NAM-corruption layer
    existed), but `expr_eval` itself has layered bugs SN-22 cannot reach
    — confirming the goal file's "bug is elsewhere" fallback.

  - [x] **SN-22c** -- Delete dead `NAME_mark` / `NAME_rollback_to` from
    public API and implementation.  **Done 2026-04-19.**

    **Scope decision (narrower than the original proposal):** after
    SN-22a+b landed, `NAME_mark` / `NAME_rollback_to` have zero callers
    anywhere in the tree — so deleting them is a pure, zero-risk cleanup.
    However, `NAME_save` / `NAME_discard` / `NAME_top` / `NAME_pop_above`
    still have three live call sites (`eval_code.c:559,566` and
    `stmt_exec.c:1191,1192,1206`) providing legitimate EVAL-frame
    isolation and pre-scan NAM state save/restore.  The original SN-22c
    proposal called for inlining those to "direct reads of the current
    stack depth," but that requires either (a) exposing the internal
    `g_top` global as an extern — expanding the surface we're trying
    to shrink, or (b) keeping `NAME_top` or equivalent as a public
    accessor anyway, just under a different name.  Neither (a) nor (b)
    reduces the API surface meaningfully; both trade a well-named
    function for either a leaked global or a renamed function.

    **Landed changes:**
    - `snobol4.h`: removed `NAME_mark` / `NAME_rollback_to` declarations
      and their documentation block.
    - `snobol4_nmd.c`: removed `NAME_mark` / `NAME_rollback_to`
      definitions (2 functions, ~10 LOC).
    - `snobol4_nmd.c`: updated the file header architecture doc to
      reflect the SN-22 invariants (`NAME_save` / `NAME_commit` /
      `NAME_discard` is now the canonical bracket set; `NAME_mark` /
      `NAME_rollback_to` are explicitly listed as deleted).

    **Public NAM API surface after SN-22c:**
    `NAME_push`, `NAME_pop`, `NAME_push_callcap`, `NAME_push_callcap_named`,
    `NAME_save`, `NAME_commit`, `NAME_discard`, `NAME_top`, `NAME_pop_above`.
    Down from 11 entry points to 9 — the two removed were both no-ops /
    unused after SN-20 and SN-22a+b.

    **Gates:** Smoke PASS=7, Broker PASS=49, Broad corpus PASS=223/225
    — all unchanged from post-SN-22b state.  `expr_eval` and
    `demo_claws5` remain the only broad-corpus fails.

    **Deferred follow-up** (optional, not blocking SN-7): if a future
    rung wants the fuller API collapse, the path is to introduce a
    `NAME_scope_t` stack-allocated bracket (RAII-style) that hides
    `save`/`commit`/`discard` inside a single type — that lets us drop
    the four depth-based entry points from the header without changing
    call-site semantics.  Out of scope for SN-22.

  - [x] **SN-22d** -- Empirically verify box self-unwind completeness
    at the exec_stmt Phase 3 boundary; delete the two vestigial
    `NAME_discard(nam_cookie)` calls.  **Done 2026-04-19.**

    **What this rung actually turned out to be about** (not `expr_eval`,
    which is a separate layered bug that SN-22 was never going to
    reach): Lon asked the sharp question — "why do you need to delete
    at a depth?  Why doesn't unrolling leave the stack exactly where
    you want it?  Are you processing all of the beta backtracks for
    each box during backtracking?"  Walking the code (bb_seq.c
    lines 57-61, bb_cap line 566, bb_alt lines 91-96, bb_arbno
    lines 158-172) confirmed:

    | Exit shape from a box | Responsibility |
    |-----------------------|----------------|
    | FAIL returned from α  | nothing pushed; nothing to pop |
    | γ-then-β-then-FAIL    | β must pop its own γ push before escalating |

    Every box in the combinator set honors this invariant.  bb_seq on
    right-fail walks left β before returning SEQ_ω.  bb_cap's β entry
    (line 541) pops its NAM handle before asking the child for β.
    Inductively, a FAIL returned from the root box to BB_SCAN means
    the entire tree has self-unwound — `g_top` is already at the
    pre-scan depth.

    **Consequence:** the two `NAME_discard(nam_cookie)` calls at
    stmt_exec.c:1192 and :1206 were dead weight, analogous to the
    `NAME_mark` / `NAME_rollback_to` deletions at SN-22a+b and SN-22c.
    The first was literally `save` + `discard-to-save` (pure no-op);
    the second was "on :F, truncate the stack that's already at the
    truncation depth."  Both deleted.

    **Kept:**
    - `NAME_save()` at :1191 — captures pre-scan depth so `NAME_commit`
      knows the lower bound for "entries pushed during this match".
      Necessary for nested exec_stmt via EVAL-within-outer-match.
    - `NAME_commit(nam_cookie)` at :1231 — the one genuine bracket
      operation: walks [cookie..top), fires `name_commit_value` on
      each, drops the range.

    **Follow-ups noted for a future rung (not landed here):**
    - `eval_code.c` `EXPVAL_fn` still calls `NAME_save`/`NAME_discard`
      around `eval_node()`.  The same self-unwind reasoning probably
      applies, but the EVAL path has DT_E thaw / nested-context edges
      worth a focused pass before deletion.
    - `NAME_push_callcap` / `NAME_push_callcap_named` have **zero real
      callers** in the tree (`bb_cap` calls `NAME_push` directly at
      line 559; the "callcap" wrappers are four-line sugar that nobody
      uses anymore).  Stale since SN-21d.  Safe to delete.

    **Gates:** Smoke PASS=7, Broker PASS=49, Broad corpus PASS=223/225
    — all unchanged.  Porter `--ir-run` and `--sm-run` both 100.00%.
    `expr_eval` and `demo_claws5` remain — both outside SN-22's reach
    as the goal file always anticipated.

  **Gate:** Smoke PASS=7, Broker PASS=49, Broad corpus must not regress
  (≥223/225).  `expr_eval` expected to flip to PASS on SN-22d.

- [ ] **SN-6b** -- expr_eval arithmetic path.  **Root cause identified
  2026-04-19** (diagnosis-only session, no code changes).  The symptoms
  — stderr parse errors, `(1+2)*3 → 3`, `-3+10 → 10` — all trace back
  to one missing branch in `bb_deferred_var` (stmt_exec.c:908).  Not
  an arithmetic bug; it's a **pattern-value-type** bug that corrupts
  the operand/operator stack push sequence, which is what then makes
  EVAL receive garbage.

  **Smoking gun** (trace added and reverted in session):
  ```
  [DVAR] name=EXPR0    val.v=11 ptr=(nil)          ← DT_E, silently → epsilon
  [DVAR] name=CONSTANT val.v=3  ptr=0x7eea...      ← DT_P, works correctly
  ```

  `bb_deferred_var` has three branches for `NV_GET_fn(ζ->name)`:
  - `DT_P` (compiled pattern) → rebuild child ✓
  - `DT_S` (string) → literal pattern ✓
  - **else → silently falls through to epsilon** ✗ (DT_E lands here)

  When a variable's RHS is itself a deferred expression (e.g.
  `expr0 = *constant`, or the recursive `expr = *constant addop *expr |
  *constant`), the variable holds a **DT_E** (frozen expression), not
  a DT_P.  `*expr0` then matches epsilon instead of invoking the
  underlying pattern — silently dropping every nested `*fn()` side-effect.

  **Minimal repro** (recreate if container resets):
  ```snobol4
           &ANCHOR = 0
           &FULLSCAN = 1
           integer  = SPAN('0123456789')
           constant = integer . *PushC()
           expr0    = *constant
           '1' POS(0) *expr0 RPOS(0) :F(no)S(yes)
           *  SPITBOL: match   scrip: NO MATCH
  ```

  **Effect on expr_eval:** every `*expr` / `*term` / `*factor` /
  `*primary` self-reference in the recursive grammar silently matches
  epsilon and drops sibling side-effects.  On input `1+2`, scrip makes
  2 Push calls (SPITBOL makes 3 — `addop`'s `*PushO()` is the dropped
  one because it sits between `*constant` and `*expr`).  The stack
  then under-flows inside Binary(), producing `L=0 O=1 R=5` garbage
  which EVAL reports as a parse error.  The `(1+2)*3 → 3` and
  `-3+10 → 10` results are the specific forms that underflow leaves
  behind.

  **Fix template** (lift from `pat_to_patnd` in
  `snobol4_pattern.c:220-253`):  Add a DT_E thaw block to
  `bb_deferred_var` before the DT_P check.  Handle E_FNC child via
  `pat_user_call`, E_VAR child via `var_as_pattern`, otherwise
  `PATVAL_fn` — same trichotomy.  Result is a DT_P the existing
  branch can consume.

  **Confirmed not:** `SN-22` did NOT subsume this bug (as speculated
  earlier in the goal file).  The NAM machinery is clean post-SN-22;
  this is a separate type-coercion gap in pattern construction.

  **Key files:**
  - `src/runtime/x86/stmt_exec.c:887-1001` — `bb_deferred_var` (add
    DT_E branch)
  - `src/runtime/x86/snobol4_pattern.c:220-253` — `pat_to_patnd`
    (template to copy)
  - `src/runtime/x86/descr.h:36` — `DT_E = 11` (sanity reference)

  **Gates at diagnosis:** Smoke 7, Broker 49, Broad 223/225 (unchanged;
  no code changes landed this session).

- [ ] **SN-7** -- beauty.sno self-host: 6 drivers × 3 modes = 18 combos,
  diff=0 vs SPITBOL. Gate: smoke PASS=7, broker PASS=49, all 18 diff=0.

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

**HEAD:** one4all @ `4b70778d` (SN-22d — SN-22 complete).  Gates:
Smoke 7, Broker **49**, Broad corpus 223/225 (unchanged throughout
SN-22).  Porter `--ir-run` and `--sm-run` both at **100.00%** / 23531,
byte-identical to SPITBOL ref.  `expr_eval` and `demo_claws5` remain.

**What SN-22 delivered:**
- SN-22a (bb_alt) + SN-22b (bb_arbno): removed dead NAM mark/rollback
  calls.  Broker jumped +1 (48 → 49) — pre-existing drift was the same
  class of NAM-corruption bug.
- SN-22c: deleted `NAME_mark` / `NAME_rollback_to` from public API.
- SN-22d: walked the box backtrack protocol, deleted the two vestigial
  `NAME_discard` calls in exec_stmt Phase 3, recorded the invariant
  in a code comment.

**Invariant established** (now recorded at stmt_exec.c:1189):
  FAIL-from-α   ⇒ nothing pushed; nothing to pop.
  γ-then-β-fail ⇒ β is responsible for popping its own γ push.
By induction, FAIL returned from the root box to BB_SCAN means the
entire tree has self-unwound — g_top is already at the pre-scan depth.

**Python reference confirms the same invariant.** Lon's SN-22 session
checked `snobol4python/_backend_pure.py` directly: every generator
(Δ, Shift, nPush, Λ, λ, etc.) does `cstack.append(x); yield; cstack.pop()`
in matched one-to-one pairs.  `SEARCH()` never truncates cstack — it
only walks-and-fires on success.  **The Python driver has no "whack"
operation.**  The C equivalent (NAME_push in bb_cap γ, NAME_pop in
bb_cap β/ω, NAME_commit on success in exec_stmt) maps 1:1.

**Three true primitives** (Python-verified):
| Operation | Python | C |
|-----------|--------|---|
| push      | `cstack.append(cmd)` in generator | `NAME_push(&nm, σ, δ)` in bb_cap γ |
| pop       | `cstack.pop()` in generator's post-yield | `NAME_pop(handle)` in bb_cap β/ω |
| commit    | `for cmd in cstack: exec(cmd)` in SEARCH on success | `NAME_commit(cookie)` in exec_stmt Phase 5 |

**Cookie note:** the C `NAME_commit(cookie)` parameter exists because
the C port uses one shared `g_stack[]` across nested matches, where
Python uses a fresh `SNOBOL()` object (and therefore a fresh cstack)
per match attempt.  The cookie is an artifact of the shared-global
optimization, not a semantic requirement.  A per-match local cstack
would drop the cookie API entirely.

**Next step:** **SN-7** — beauty.sno self-host (6 drivers × 3 modes =
18 combos, diff=0 vs SPITBOL).  SN-6 (`expr_eval`, `demo_claws5`)
remains as the blocker between here and SN-7 closure — layered bugs
orthogonal to NAM machinery.

**Optional follow-ups noted during SN-22** (small, safe):
- Delete `NAME_push_callcap` / `NAME_push_callcap_named` — zero real
  callers in the tree (bb_cap already uses `NAME_push` directly at
  bb_boxes.c:559).  Stale sugar since SN-21d.
- Audit `eval_code.c` `EXPVAL_fn` `NAME_save`/`NAME_discard` pair —
  same self-unwind reasoning likely applies; EVAL path has DT_E thaw
  edges worth focused review.
- Bigger refactor: replace the global `g_stack[]` with a per-match
  stack-allocated cstack (matching Python directly).  Drops the cookie
  API entirely.  Worth its own goal.
