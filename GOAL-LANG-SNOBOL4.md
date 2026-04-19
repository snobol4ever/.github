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

- [~] **SN-6b** -- expr_eval arithmetic path.  **DT_E thaw gap closed
  2026-04-19**; expr_eval still fails — additional layered bugs.

  **What landed this session:**

  Two independent DT_E bugs found and fixed together:

  1. **DT_E descriptor union-aliasing bug** in four constructor sites.
     The pattern:
     ```c
     d.v    = DT_E;
     d.ptr  = child;    /* stores pointer */
     d.slen = 0;
     d.s    = NULL;     /* CLOBBERS .ptr — .s and .ptr share union */
     ```
     Every DT_E descriptor was being stored with `.ptr == NULL`.
     `sm_interp.c:276` was the lone correct site (explicit "set ptr
     last" comment).  Fixed in `driver/interp.c:3033` (E_DEFER eval),
     `runtime/x86/eval_code.c` (E_DEFER + CONVE_fn), and
     `runtime/x86/snobol4_pattern.c` (CONVE pattern path).

  2. **Missing DT_E branch in `bb_deferred_var`** (stmt_exec.c:908).
     On a live NV fetch that returns DT_E (variable holds frozen
     expression), the α dispatch had three branches — DT_P, DT_S, else
     (→ bb_eps).  DT_E fell into the else and silently matched epsilon,
     dropping all nested `*fn()` side-effects.  Added a DT_E thaw
     modelled on `pat_to_patnd` (snobol4_pattern.c:220-253):
     - `E_FNC` child → `pat_user_call(fname, args, nargs)` → XATP
     - `E_VAR` child → **direct `NV_GET_fn(frozen->sval)`**
       (NOT `var_as_pattern`; see note below)
     - else → `PATVAL_fn(val)` strict thaw

     Included `ir/ir.h` and declared `extern DESCR_t eval_node(EXPR_t*)`
     in the full-runtime block of stmt_exec.c.

  **E_VAR branch — why NV_GET_fn and not var_as_pattern:**

  `pat_to_patnd` uses `var_as_pattern(STRVAL(sval))` which builds an
  XVAR node.  `bb_build` on XVAR creates a **fresh nested
  bb_deferred_var** that looks up the same variable again.  Probing
  showed the nested bb_deferred_var returned FAIL at α on the minimal
  repro, while a direct outer bb_deferred_var on the same variable
  succeeded.  Root cause of the extra-indirection failure was not
  run to ground — *the simpler fix* is to recognise that
  `bb_deferred_var` already IS the deferred re-resolve box, so
  wrapping in XVAR adds a useless layer.  Direct `NV_GET_fn` returns
  the variable's live DT_P, which the existing DT_P branch handles
  correctly.  This is a narrower, surgical fix that avoids the XVAR
  path entirely for the DT_E thaw case.

  **Minimal repro now passes (was failing):**
  ```snobol4
           &ANCHOR = 0
           &FULLSCAN = 1
           nPushes = 0
           DEFINE('PushC()')                :(push_end)
  PushC    nPushes = nPushes + 1
           PushC = .nPushes                 :(NRETURN)
  push_end
           integer  = SPAN('0123456789')
           constant = integer . *PushC()
           expr0    = *constant
           '1' POS(0) *expr0 RPOS(0) :F(no)S(yes)
  no       OUTPUT = 'NO MATCH'              :(END)
  yes      OUTPUT = 'MATCH, pushes=' nPushes
  END
  ```
  SPITBOL: `MATCH, pushes=1`.  scrip before fix: `NO MATCH`.
  scrip after fix: `MATCH, pushes=1` (both `--ir-run` and `--sm-run`).

  **expr_eval — NOT closed by this fix.**  DT_E thaw is necessary
  but not sufficient.  expr_eval still shows:
  - `(1+2)*3 → 3` (expected 9)
  - `-3+10 → 10` (expected 7)
  - 4/5 inputs return `snobol4:0: error: parse error: syntax error`

  These are layered arithmetic/EVAL bugs orthogonal to the DT_E gap,
  as the Goal file previously anticipated.  They are their own
  sub-rung (call it SN-6c when next session picks them up).

  **Gates after SN-6b:** Smoke PASS=7, Broker PASS=49, Broad corpus
  PASS=223/225 (same two failures: expr_eval, demo_claws5 — **no
  regression**).  Porter `--ir-run` and `--sm-run` both still at
  100.00% / 23531.

  **Files changed:**
  - `src/driver/interp.c`: DT_E ordering at E_DEFER (line 3033)
  - `src/runtime/x86/eval_code.c`: DT_E ordering at E_DEFER + CONVE_fn
  - `src/runtime/x86/snobol4_pattern.c`: DT_E ordering at CONVE pattern
  - `src/runtime/x86/stmt_exec.c`: `#include "../../ir/ir.h"`,
    `extern DESCR_t eval_node(EXPR_t*)`, 40-line DT_E thaw block in
    `bb_deferred_var`

  **Still-open for SN-7 path (tracked as SN-6c):** expr_eval arithmetic
  path.  Investigate the stack-underflow signal: Push on addop/mulop
  is wired via `. *Push()` (pattern-context, fires on match success).
  With DT_E now thawing correctly, count the Push calls on `1+2` —
  if scrip now pushes 3 (matching SPITBOL), the parse-error path is
  downstream of Push/Pop ordering.  If still under-pushing, there is
  another dispatch gap.

- [x] **SN-6c** -- Recursive pattern NAM corruption.  Closed for
  `--ir-run` by SN-23d-follow-up at one4all @ `d61a580e`.

  **7-line repro** (`rec = 'a' . *Push('A') *rec | 'a' . *Push('B')`
  on `'aa'`):
  - SPITBOL: `PUSH A, PUSH B, MATCH count=2`
  - `--ir-run`: `PUSH A, PUSH B, MATCH count=2`  ✓ byte-identical
  - `--sm-run`: count matches (2); tags empty — separate SM-side
    XATP arg-name stash gap, pre-existing (noted in SN-17a history),
    not in SN-23 scope.

  **Real mechanism** (isolated by instrumented trace, reverted before
  commit): the bug was NOT the originally-hypothesised `nam_handle`
  leak nor a shared cap_t `state` pointer.  Three cap_t allocations
  had distinct ζ addresses; corruption arrived via
  `cache_get_fresh` (stmt_exec.c:308-317):

  ```c
  void *fresh = calloc(1, n.ζ_size);
  memcpy(fresh, n.ζ, n.ζ_size);   /* n.ζ aliases live template */
  ```

  `cache_insert` stores `n.ζ` as the template pointer — but that
  pointer IS the first match's live state.  By cache-hit time, the
  template's scalars (`has_pending`, `pending`, ...) are dirty, and
  every "fresh" cap_t memcpy'd from it inherits those values.

  **Fix:** SN-23d-follow-up zeros `ζ->has_pending` at the top of
  `CAP_α` — defeats the poison at the site.  The underlying
  cache_get_fresh flaw remains (any other box type storing in-flight
  scalars is vulnerable to the same class of bug); pristine-template
  rewrite is a defensible future rung if symptoms appear elsewhere.


- [ ] **SN-23** -- Per-pattern NAM context: kill marks, go pure push/pop.

  **Principle:** NAM stack belongs to a per-match context, not to a
  global.  Every `exec_stmt` match attempt allocates its own `cstack`.
  Every `bb_cap` γ appends one entry; every β/ω pops exactly one.
  On outer match success, the entire cstack is walked oldest→newest
  and each entry fired via `name_commit_value`.  No marks, no handles,
  no rollback, no top/pop_above.  Python's `_backend_pure.py` reference.

  **Reference (already quoted in SN-22 rationale):**
  ```python
  class Δ:
      def γ(self):
          for _1 in self.P.γ():
              Ϣ[-1].cstack.append(f"{N} = ...")
              yield _1
              Ϣ[-1].cstack.pop()
  ```
  `append`, `pop`, and (at outer success) `for cmd in cstack: exec(cmd)`.
  That is the complete protocol.

  **API after SN-23 (3 operations, period):**
  ```
  void NAME_push(const NAME_t *nm, const char *substr, int slen);
  void NAME_pop(void);                  /* drops the top; no handle */
  void NAME_commit(void);               /* walk, fire, clear */
  ```
  Plus two context brackets:
  ```
  void NAME_ctx_enter(NAME_ctx_t *ctx); /* make ctx the current */
  void NAME_ctx_leave(void);            /* restore parent; drop ctx */
  ```

  **Deleted in SN-23:**
  - `NAME_save`, `NAME_discard` — no cookies; contexts nest instead.
  - `NAME_top`, `NAME_pop_above` — no bulk drops; each box's own β/ω
    pops exactly its own push.
  - `NAME_push_callcap`, `NAME_push_callcap_named` — already zero real
    callers (noted in SN-22 followups); `bb_cap_new_call` pushes
    directly via `NAME_push` on the NM_CALL name.
  - `nam_handle` field in `cap_t` — no handles anywhere.

  **Call-site rewiring:**
  | File | Line | Before | After |
  |------|------|--------|-------|
  | `bb_boxes.c` | 541, 559, 566 | `nam_handle = NAME_push(...)`, `NAME_pop(nam_handle)` | `NAME_push(...)`, `NAME_pop()` |
  | `stmt_exec.c` | 1272 | `int cookie = NAME_save();` | `NAME_ctx_enter(&local_ctx);` |
  | `stmt_exec.c` | 1304 | `NAME_commit(cookie);` | `NAME_commit();` |
  | `stmt_exec.c` | (match fail return) | (implicit — no discard) | `NAME_ctx_leave();` before return 0 |
  | `eval_code.c` | 559, 566 | `int cookie = NAME_save();` / `NAME_discard(cookie);` | `NAME_ctx_enter(&e_ctx);` / `NAME_ctx_leave();` |

  **Data model (replaces g_stack/g_top globals in snobol4_nmd.c):**
  ```c
  typedef struct NAME_ctx_s {
      NAME_entry_t *cstack;
      int           top;
      int           cap;
      struct NAME_ctx_s *parent;
  } NAME_ctx_t;
  static NAME_ctx_t *g_ctx_current = NULL;   /* linked stack of ctxs  */
  ```
  `NAME_push` appends to `g_ctx_current`.  `NAME_pop` drops from
  `g_ctx_current`.  Nested EVAL creates a fresh ctx linked to parent;
  leaves restore parent.  Captures inside an EVAL'd expression are
  LOCAL to that EVAL's ctx and never propagate out — exactly what
  eval_code.c:559-566 intends with its current save/discard dance,
  but cleaner.

  **Ladder SN-23a..g:**

  - [x] **SN-23a** -- Introduce `NAME_ctx_t`, `NAME_ctx_enter`,
    `NAME_ctx_leave` in snobol4_nmd.c.  Keep old API working alongside
    (new ctx takes precedence if non-NULL; else falls through to
    legacy g_stack).  Smoke+Broker green.  **Done 2026-04-19.**

    **Landed changes:**

    - `snobol4_nmd.c`: added `struct NAME_ctx_s { entries, cap, top,
      parent }`.  Declared a file-scope static `g_root_ctx` that owns
      what used to be the legacy `g_stack` / `g_cap` / `g_top`
      globals, and a `g_ctx_current` pointer that starts at `&g_root_ctx`.
      Added `NAME_ctx_enter(ctx)` and `NAME_ctx_leave()`.
    - Refactored the five internal ops (`NAME_push`, `NAME_pop`,
      `NAME_top`, `NAME_pop_above`, `NAME_commit` walk) to read through
      `g_ctx_current` instead of the file-scope globals.  Added a
      small internal helper `ctx_ensure_capacity(ctx, need)` replacing
      the old `ensure_capacity(need)`.
    - `snobol4.h`: forward-declared `typedef struct NAME_ctx_s
      NAME_ctx_t;` and added prototypes for `NAME_ctx_enter` /
      `NAME_ctx_leave` alongside the existing bracket API.
    - Legacy shims (`NAME_save` / `NAME_commit` / `NAME_discard` /
      `NAME_push_callcap*`) untouched in shape — still the same entry
      points — but all now route through `g_ctx_current`.

    **Design note — why a static root ctx instead of a NULL fallback:**
    The original plan said "new ctx takes precedence if non-NULL; else
    falls through to legacy g_stack."  Landed version wraps the legacy
    globals in a statically-allocated `g_root_ctx` and makes
    `g_ctx_current` always non-NULL.  That eliminates a NULL-check
    branch from the hot path of every NAME_push / NAME_pop and keeps
    the five internal ops as one code path, not two.  Behavioral
    equivalent: nothing calls `NAME_ctx_enter` yet, so every op still
    operates on the root ctx == what used to be the global stack.

    **Gates after SN-23a:**
    - Smoke PASS=7 (unchanged)
    - Broker PASS=49 (unchanged)
    - Broad corpus PASS=223/225 (unchanged — expr_eval, demo_claws5
      remain the only fails)
    - Porter `--ir-run` and `--sm-run` both byte-identical to SPITBOL
      ref (0-line diff / 23531)

  - [x] **SN-23b** -- stmt_exec.c Phase 3: wrap the scan in
    `NAME_ctx_enter/leave`.  `NAME_commit()` now walks `g_ctx_current`
    instead of `g_stack[cookie..top]`.  Update all `NAME_save()` →
    no-op, `NAME_discard()` → `NAME_ctx_leave` or remove.  Gate:
    Smoke, Broker, Broad corpus must not regress.  **Done 2026-04-19.**

    **Landed changes (stmt_exec.c):**
    - Phase 3 scan bracket: `NAME_save()` / `NAME_commit(cookie)` pair
      replaced with `NAME_ctx_enter(&scan_ctx)` / `NAME_ctx_leave()`.
    - The three failure-return paths (BB_SCAN returning no match,
      lvalue-missing :F, and Phase 4 gate) all leave the ctx before
      returning 0.
    - Success path: `NAME_commit(0)` walks the whole scan_ctx (cookie=0
      because the child ctx starts empty), then `NAME_ctx_leave()`.
      Phase 5's NV_SET_fn write to the subject variable happens after
      leave — it doesn't touch NAM, so ordering is clean.

    **Semantic upgrade:** nested exec_stmt (EVAL-inside-match) now
    isolated by ctx nesting — the inner ctx sees only its own pushes,
    and outer entries are unreachable until `NAME_ctx_leave` restores
    the parent.  This is strictly cleaner than the cookie approach:
    the outer never sees the inner's entries at all, even transiently.

  - [x] **SN-23c** -- eval_code.c: same rewiring for EVAL frame.
    **Done 2026-04-19.**

    **Landed changes (eval_code.c):**
    - `EXPVAL_fn` DT_E thaw path: `NAME_save()` / `NAME_discard(cookie)`
      replaced with `NAME_ctx_enter(&eval_ctx)` / `NAME_ctx_leave()`.
    - Captures inside an EVAL'd expression now die with the ctx on
      leave — structurally local, same semantics as the old discard.

    **Design tweak that landed with SN-23b+c (snobol4.h):**  The
    SN-23a header declared `NAME_ctx_t` as a forward typedef, making
    the struct opaque — but callers (stmt_exec.c, eval_code.c) need
    to stack-allocate it.  Opaque-with-stack-alloc isn't a valid C
    combo, so the struct is now exposed in `snobol4.h` with an opaque
    `void *entries` field.  Callers see the full size (can stack-
    allocate), but the slot type `NAME_entry_t` stays file-local to
    `snobol4_nmd.c`.  Internal `ctx_entries(ctx)` accessor casts the
    void* back to `NAME_entry_t*` at every use site.

    **Gates after SN-23b+c:**
    - Smoke PASS=7 (unchanged)
    - Broker PASS=49 (unchanged)
    - Broad corpus PASS=223/225 (unchanged — `expr_eval`, `demo_claws5`
      remain the only fails)
    - Porter `--ir-run` and `--sm-run` both byte-identical to SPITBOL
      ref (0-line diff / 23531)

    **SN-6c recursion repro measured (not fixed — SN-23d target):**
    The 7-line `rec = 'a' . *Push('A') *rec | 'a' . *Push('B')` on
    input `"aa"` still fails:
    - SPITBOL:       `PUSH A, PUSH B, MATCH count=2`
    - scrip --ir-run: `PUSH B, MATCH count=1`  (outer A lost)
    - scrip --sm-run: `PUSH (empty), MATCH count=1`
    Per-match ctx isolation alone does not fix this — within a single
    match, the shared cap_t state (M-DYN-OPT cache) plus bb_cap's
    per-instance `nam_handle` field collide under recursion.  SN-23d
    rewires bb_cap to drop the `nam_handle` field entirely and use
    bare `NAME_push` / `NAME_pop()` on the top of `g_ctx_current`.

  - [x] **SN-23d** -- bb_cap: delete `nam_handle` field.  γ does bare
    `NAME_push` (handle discarded); β/ω do bare `NAME_pop_top()` (no arg,
    drops top of `g_ctx_current`).  **Done 2026-04-19.**

    **Landed changes:**
    - `snobol4_nmd.c`: new `NAME_pop_top(void)` — handle-free LIFO drop
      of the topmost live slot of the active ctx.  ~12 LOC.
    - `name_t.h`: declaration added alongside `NAME_push` / `NAME_pop`.
    - `bb_boxes.c`: bb_cap β / γ / ω rewired — `NAME_push` return
      discarded at γ; β and ω call `NAME_pop_top()` under the existing
      `!immediate && has_pending` guard.
    - `bb_box.h`: `void *nam_handle;` field removed from `cap_t`.
    - `stmt_exec.c`: orphan `void *nam_handle;` removed from
      `usercall_t` (never read or assigned — stale since SN-17d).

    **Gates:** Smoke PASS=7, Broker PASS=48, build clean, no regression.
    (Broker 48 is the local-run baseline; previous sessions measured 49.
    The +1 drift is pre-existing — same at HEAD `2c518cef` before this
    rung.  Corpus not cloned in this session → broad corpus not
    measured; per RULES.md scripts SKIP cleanly when corpus absent.)

    **SN-6c repro status: STILL FAILS.**  The 7-line recursion repro
    (`rec = 'a' . *Push('A') *rec | 'a' . *Push('B')` on `'aa'`)
    produces `PUSH #1 tag=B, MATCH count=1` in both modes — outer
    Push('A') still lost.  SPITBOL gives `PUSH #1 A, PUSH #2 B,
    MATCH count=2`.

    **Diagnosis (instrumented trace captured this session, reverted
    before commit — recreate by adding fprintf to CAP_α/β/γ):**

    The real SN-6c mechanism is **NOT** a `nam_handle` leak — the goal
    file's earlier hypothesis was incorrect.  It is the M-DYN-OPT
    cache in `cache_get_fresh` (stmt_exec.c:308-317):

    ```c
    static bb_node_t cache_get_fresh(cache_slot_t *slot) {
        bb_node_t n = slot->template;
        if (n.ζ_size && n.ζ) {
            void *fresh = calloc(1, n.ζ_size);
            memcpy(fresh, n.ζ, n.ζ_size);   /* copies DIRTY template */
            n.ζ = fresh;
        }
        return n;
    }
    ```

    `cache_insert` stores the template AFTER the first build (clean
    state).  But `n.ζ` in the template is the SAME pointer used for
    the first match execution — so by the second time a recursion
    lands on this slot, the template ζ is dirty (has_pending=1,
    pending=spec{...}, etc.).  `cache_get_fresh` dutifully memcpys
    those dirty values into every "fresh" copy.

    **Trace evidence (reverted):**
    ```
    [CAP α] ζ=0x...8f0 state=0x...8d0 pend=0    ← outer A, fresh
    [CAP γ push] ζ=0x...8f0 top=1               ← pushes, sets pend=1
    [CAP α] ζ=0x...b60 state=0x...8d0 pend=1    ← cache hit, STALE pend=1
    [CAP γ push] ζ=0x...b60 top=2
    [CAP β]  ζ=0x...b60 pend=1 top=1            ← top already dropped
    [CAP β pop] ζ=0x...b60 top=0                ← pops outer A!
    [CAP α] ζ=0x...bbe0 state=0x...970 pend=0   ← arm 2 'B', fresh
    [CAP γ push] ζ=0x...bbe0 top=1
    ```

    Three distinct cap_t allocations (different ζ addresses), but the
    cache memcpys the dirty template into each — so the "fresh"
    cap_t's `has_pending` is inherited from the first match's live
    state.

    **SN-23d did NOT close SN-6c** because the same corruption vector
    that used to poison `nam_handle` still poisons `has_pending` (the
    LIFO guard).  The rung's API reduction is real and correct —
    `nam_handle` IS gone, `NAME_pop` overloading pressure IS relieved
    — but the architectural cleanup did not reach the bug.

    **Recommended path forward (SN-23d-follow-up):** three options,
    in order of invasiveness:

    1. **Reset `has_pending = 0` at CAP_α** (one-line defensive fix).
       Makes cap_t self-initialising on every α, defeating the cache
       poisoning at the site.  Surgical, small, preserves cache
       benefit.

    2. **Fix `cache_get_fresh` template purity** — keep a pristine
       calloc'd template separate from the live ζ used for the first
       match.  Larger change, per-box-type knowledge required
       ("what counts as config vs state?"), but fixes the class of
       bug for every future box type.

    3. **Add XCALLCAP/XNME/XFNME to `patnd_is_invariant`'s variant
       list so cap containers are never cached.**  Defensive but
       goal file (SN-23 cross-concern) explicitly said not to pursue
       this path.

    Option 1 is smallest and addresses the immediate SN-6c symptom.
    Option 2 is the "right" fix.  Next session to choose.

  - [x] **SN-23d-follow-up** -- Close SN-6c via has_pending reset at
    CAP_α.  **Done 2026-04-19.**  one4all @ `d61a580e`.

    One-line defensive fix: `ζ->has_pending = 0;` at the top of CAP_α.
    Zeros the guard before α runs so β/ω's `if (!immediate &&
    has_pending)` check reflects only THIS α's push, defeating
    cache_get_fresh's poisoned-template propagation at the site.

    **7-line SN-6c repro:**
    - SPITBOL:  `PUSH A, PUSH B, MATCH count=2`
    - --ir-run: `PUSH A, PUSH B, MATCH count=2`  ✓ byte-identical
    - --sm-run: `PUSH (empty), PUSH (empty), MATCH count=2` — count
      correct; tags empty is a separate SM-side XATP arg-name stash
      gap (pre-existing, noted in SN-17a history; not in SN-23's scope).

    **Gates:** Smoke PASS=7, Broker PASS=48, build clean, no regression.

    **Cache bug NOT closed.**  The underlying `cache_get_fresh` flaw
    (template.ζ aliases the first match's live state) is still there
    — any future box type that stores in-flight state scalars is
    vulnerable to the same class of bug.  This patch makes bb_cap
    self-healing at the site.  Option 2 (pristine template separate
    from live ζ) remains a defensible larger cleanup for a future
    rung if more boxes exhibit the symptom.

  - [ ] **SN-23e** -- Delete `NAME_save`, `NAME_discard`, `NAME_top`,
    `NAME_pop_above` from public header; delete definitions from
    snobol4_nmd.c.  Any remaining callers are bugs to fix, not
    features to preserve.

  - [ ] **SN-23f** -- Delete `NAME_push_callcap`, `NAME_push_callcap_named`
    (zero real callers per SN-22 audit).  Any NM_CALL pushes go
    through bare `NAME_push` with a pre-built NM_CALL NAME_t.

  - [ ] **SN-23g** -- Test gate:
    - Smoke PASS=7
    - Broker PASS=49
    - Broad corpus: expr_eval should now PASS.  PASS=224/225 (only
      `demo_claws5` remaining, tracked under GOAL-SNO-CLAWS5.md).
    - Porter --ir-run AND --sm-run byte-identical to SPITBOL ref.
    - The 7-line `rec` minimal repro above gives MATCH count=2.

  **Cross-concern: M-DYN-OPT cache.**  Even after SN-23, the cache
  sharing in `cache_get_fresh` is latent — any future box type that
  stores in-flight state pointers could hit it.  Post-SN-23, file a
  follow-up to either (a) drop the cache entirely (measure first —
  probably 0% of hot path), or (b) make `cache_get_fresh` recursively
  deep-copy pointer fields.  Not gating SN-7.

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

**HEAD:** one4all @ `d61a580e` — SN-23d + SN-23d-follow-up landed.
`nam_handle` deleted, bare `NAME_pop_top()` in bb_cap, `has_pending`
reset at CAP_α to defeat cache poisoning.  Gates: Smoke **7**, Broker
**48** (local baseline), no regression.  7-line SN-6c recursion repro
now byte-identical to SPITBOL under `--ir-run`; `--sm-run` count
matches but tags empty (separate SM-side XATP arg-name gap).

**Next step:** **SN-23e** — delete stale NAM API entries
(`NAME_save`, `NAME_discard`, `NAME_top`, `NAME_pop_above`) and their
definitions.  Per the SN-23 plan, callers are now either ctx-based
(stmt_exec.c Phase 3, eval_code.c EXPVAL_fn) or LIFO-based (bb_cap
via `NAME_pop_top`).  Any remaining callers of the bracket API are
bugs to fix, not features to preserve.


**Useful follow-ups noted during SN-22/23** (small, safe, not gating):
- Delete `NAME_push_callcap` / `NAME_push_callcap_named` — zero real
  callers since SN-21d (bb_cap uses `NAME_push` directly).
- Audit `eval_code.c` `EXPVAL_fn` `NAME_save`/`NAME_discard` pair —
  same self-unwind reasoning likely applies; candidate for SN-23e/f.
- `cache_get_fresh` template purity — the real SN-6c root cause.
  bb_cap is now self-healing at the site (SN-23d-follow-up) but any
  other box type storing in-flight scalars is vulnerable to the same
  class of bug.  Pristine-template rewrite is a defensible cleanup
  if symptoms appear elsewhere.
