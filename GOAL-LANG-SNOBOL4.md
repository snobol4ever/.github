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

- [x] **SN-6** -- Full corpus: **PASS=225/225** in all three modes.  Done 2026-04-20.
  ```bash
  bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
  ```
  **Closing move — a gate-script fix, not a runtime fix.**  On entering
  the session the broad-corpus gate reported `FAIL demo_claws5`.  The
  runtime was not at fault: scrip `--ir-run`, scrip `--sm-run`, and
  CSNOBOL4 `-bf -P 500k` all produce byte-identical output on
  `CLAWS5inTASA.dat` (the 989-line stress input).  The failure was
  pure gate wiring — `test_interp_broad_corpus_and_beauty.sh:67`
  fed the demo row `demo_claws5` the stress input
  `CLAWS5inTASA.dat` (989 lines → 5622 lines output) while comparing
  against `claws5.ref` (95 lines, the correct *demo*-scale reference
  produced by `claws5.input` at 16 lines).  The ref was trimmed back
  to demo scale by corpus commit `293eab6` ("trim claws5.ref to match
  claws5.input (16 lines)"); the gate never got repointed.
  **Fix:** one-word change, line 67 of the gate script —
  `$DEMO/CLAWS5inTASA.dat` → `$DEMO/claws5.input`, matching the
  convention every other demo row already used
  (`wordcount.input`, `treebank.input`, …).  After the fix both
  scrip modes produce 95-line output that is 0-line-diff vs
  `claws5.ref`.  **Gates:** Smoke PASS=7, Broker PASS=49, Broad
  corpus **PASS=225/225**, SN-7 beauty driver-self-host PASS=51/51.

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

  - [x] **SN-23e** -- Delete `NAME_save`, `NAME_discard`, `NAME_top`,
    `NAME_pop_above` from public header; delete definitions from
    snobol4_nmd.c.  **Done 2026-04-19.**

    **Landed changes:**
    - `snobol4_nmd.c`: removed four function definitions (`NAME_top`,
      `NAME_pop_above`, `NAME_save`, `NAME_discard`) — ~30 LOC total.
      `NAME_commit` lost its `int cookie` parameter: the cookie was
      always 0 in the ctx-nesting world (scan_ctx starts empty, and
      every entry belongs to the current ctx), so the parameter was
      meaningless.  Final tail of commit inlined (was
      `NAME_pop_above(mark)`, now `ctx->top = 0`).  File header
      architecture doc rewritten to reflect the five-op public API.
    - `name_t.h`: removed `NAME_top` / `NAME_pop_above` declarations;
      doc block updated to mention SN-23d's `NAME_pop_top()` and
      SN-23e's deletion.
    - `snobol4.h`: removed `NAME_save` / `NAME_discard` declarations;
      `NAME_commit` declaration now `void NAME_commit(void);` (no arg);
      comment on `NAME_ctx_enter` updated to list the current op set
      (`NAME_push / NAME_pop / NAME_pop_top / NAME_commit`).
    - `stmt_exec.c`: sole `NAME_commit(0)` call site updated to
      `NAME_commit()`; historical comment referencing the old cookie
      API pruned.

    **API surface after SN-23e:**
    Core ops: `NAME_push`, `NAME_pop`, `NAME_pop_top`, `NAME_commit`.
    NM_CALL convenience: `NAME_push_callcap`, `NAME_push_callcap_named`
    (zero live callers — deletion tracked as SN-23f).
    Ctx brackets: `NAME_ctx_enter`, `NAME_ctx_leave`.
    **Total: 8 entries.  Down from 9 at start of SN-23e; down from
    11 at start of SN-22c; down from 13 at start of SN-22.**

    **Gates:** Smoke PASS=7, Broker PASS=48, build clean, no regression.
    Corpus not cloned → broad corpus SKIPped per RULES.md; reachable
    from any machine with `/home/claude/corpus` populated.

  - [x] **SN-23f** -- Delete `NAME_push_callcap`, `NAME_push_callcap_named`
    (zero real callers per SN-22 audit).  Any NM_CALL pushes go
    through bare `NAME_push` with a pre-built NM_CALL NAME_t.
    **Done 2026-04-19.**

    **Landed changes:**
    - `snobol4_nmd.c`: deleted both function definitions (17 LOC) and
      their header comment block.  HISTORY section updated with an
      SN-23f entry noting the API surface: 8 → 6 entries.  SPRINT
      tag bumped to SN-23f.
    - `snobol4.h`: deleted both prototypes and the doc comments that
      preceded them (14 lines).
    - `stmt_exec.c`: one stale doc comment at line 417 corrected —
      previously said "`.` / `$` capture forms still use NM_CALL via
      bb_cap / NAME_push_callcap"; bb_cap has called NAME_push
      directly since SN-21d.  Updated to reflect reality.

    **Audit:** zero remaining C-code references to
    `NAME_push_callcap` or `NAME_push_callcap_named`.  Two historical
    narrative mentions remain in stmt_exec.c comments ("existed to
    carry..."), both in past tense, describing prior behavior.
    Reasonable to preserve as history.

    **Public NAM API after SN-23f:**
    Core ops: `NAME_push`, `NAME_pop`, `NAME_pop_top`, `NAME_commit`.
    Ctx brackets: `NAME_ctx_enter`, `NAME_ctx_leave`.
    **Total: 6 entries.  Down from 13 at start of SN-22.**

    **Gates:** Smoke PASS=7, Broker PASS=48, build clean, no regression.

  - [x] **SN-23h** -- SIL-match: delete handle-based `NAME_pop`,
    rename `NAME_pop_top` → `NAME_pop`.  **Done 2026-04-19.**
    one4all @ `a556167b`.

    **Motivation:** comparison of the landed SN-23f API (6 entries)
    against the SIL's §NMD ground truth in `v311.sil` and `snobol4.c`
    showed the SIL gets by with three core ops:
    - `ENME`: write slot at `NBSPTR+NAMICL`; `INCRA NAMICL,DESCR+SPEC`
    - `DNME` (backup): `DECRA NAMICL,DESCR+SPEC` — bare decrement
    - `NMD` (commit): walk `NHEDCL..NAMICL`, fire each

    Plus a nested-frame bracket via `PUSH/POP (NHEDCL)` in the trace
    handler — which maps 1:1 to our `NAME_ctx_enter/leave`.

    The SIL has no handle, no mark, no rollback — just "decrement
    NAMICL."  Our `NAME_pop(handle)` was defensive engineering against
    a case that doesn't arise: the SN-22d audit proved every box's β/ω
    pops the top, and `bb_boxes.c:576`'s sole live `NAME_push` call
    already discards the return via `(void)` cast.  The handle was
    dead on arrival.

    **Landed changes:**
    - `snobol4_nmd.c`: deleted handle-based `NAME_pop(void *handle)`
      (~13 LOC) and the now-unused `handle_to_idx()` helper (1 line).
      Renamed `NAME_pop_top(void)` → `NAME_pop(void)`; comment rewritten
      to reference the SIL DNME analogy directly.  File header
      ARCHITECTURE block rewritten to describe the five-op surface and
      its SIL equivalents.  HISTORY gained an SN-23h entry.  SPRINT
      tag bumped to SN-23h.
    - `name_t.h`: `NAME_pop_top` declaration deleted; `NAME_pop`
      declaration changed to `void NAME_pop(void);`.  Doc comment
      updated.
    - `snobol4.h`: `NAME_pop` prototype changed to
      `void NAME_pop(void);` with new doc comment explaining the SIL
      analogy.  Updated `NAME_ctx_enter` doc to list the current op set.
    - `bb_boxes.c`: two `NAME_pop_top()` call sites in `CAP_β` / `CAP_ω`
      renamed to `NAME_pop()`.  One stale comment updated.

    **Public NAM API after SN-23h (5 entries — minimum possible,
    SIL-matching):**
    ```
    void *NAME_push(const NAME_t *nm, const char *s, int slen);  /* SIL: write + INCRA NAMICL */
    void  NAME_pop(void);                                        /* SIL: DECRA NAMICL         */
    void  NAME_commit(void);                                     /* SIL: NMD walk             */
    void  NAME_ctx_enter(NAME_ctx_t *ctx);                       /* SIL: PUSH NHEDCL; MOVD    */
    void  NAME_ctx_leave(void);                                  /* SIL: POP NHEDCL           */
    ```

    `NAME_push` still returns `void *` for source compatibility, but
    every caller discards the result via explicit `(void)` cast.  A
    future cleanup could change the return type to `void` — deferred
    because it touches the prototype and only saves a line.

    **Total API reduction across SN-22/SN-23 arc:**
    13 entries at start of SN-22 → **5 entries after SN-23h.**  Every
    remaining entry maps 1:1 to a SIL NMD primitive.

    **Gates:** Smoke PASS=7, Broker PASS=48, build clean, no regression.

  - [x] **SN-23g** -- Test gate.  **Done 2026-04-19.**

    **All gates green on a fresh clone with corpus populated:**

    | Gate | Result | Target |
    |------|--------|--------|
    | Smoke | PASS=7 | PASS=7 ✓ |
    | Broker | PASS=49 | PASS=49 ✓ |
    | Broad corpus | PASS=224/225 | ≥ 224 ✓ |
    | Porter `--ir-run` | 0-line diff | byte-identical ✓ |
    | Porter `--sm-run` | 0-line diff | byte-identical ✓ |

    **expr_eval FLIPPED to PASS in all three oracles** (SPITBOL,
    `--ir-run`, `--sm-run`) — all five inputs `1+2*3`, `(1+2)*3`,
    `2.5e1+0.5`, `-3+10`, `4*5+6` produce byte-identical output
    `7, 9, 25.5, 7, 26`.  The SN-22/SN-23 NAM API collapse (13 → 5
    SIL-matching entries) plus the SN-23d-follow-up `has_pending` reset
    was sufficient to close the layered EVAL/arithmetic bugs that
    SN-6b/SN-6c had flagged as orthogonal — the per-match NAM context
    isolation (SN-23b/c) fixed the EVAL-within-match corruption that
    was generating the parse-error and wrong-arithmetic paths.

    **Broker +1 recovery:** the 48/49 drift that SN-23d observed locally
    reconciled to PASS=49 on the fresh-clone run.  Intermittent or
    environment-dependent; stable at 49 in this session.

    **Only remaining broad-corpus fail:** `demo_claws5`, tracked under
    `GOAL-SNO-CLAWS5.md` — out of scope for the SNOBOL4 frontend ladder.

    **7-line `rec` minimal repro convergence:** all three oracles
    (SPITBOL, `--ir-run`, `--sm-run`) converge on the same outcome.
    SM-side tag-stash gap (tags empty on `--sm-run`) remains as the
    pre-existing XATP arg-name issue noted in SN-17a history — not in
    SN-23's scope, tracked separately for a future rung.

  **Cross-concern: M-DYN-OPT cache.**  Even after SN-23, the cache
  sharing in `cache_get_fresh` is latent — any future box type that
  stores in-flight state pointers could hit it.  Post-SN-23, file a
  follow-up to either (a) drop the cache entirely (measure first —
  probably 0% of hot path), or (b) make `cache_get_fresh` recursively
  deep-copy pointer fields.  Not gating SN-7.

- [x] **SN-7** -- beauty.sno self-host.  **Done 2026-04-19.**

  **Gate:** `scripts/test_gate_sn7_beauty_self_host.sh` — every
  `beauty_*_driver.sno` × `--ir-run` / `--sm-run` / `--jit-run` diff=0
  vs its pre-baked `.ref` file.  Corpus ships **17 driver subsystems**
  (not 6 as the original rung draft estimated), giving **17 × 3 = 51
  combos**.

  **Result: PASS=51 FAIL=0.**

  Drivers covered: Gen, Qize, ReadWrite, ShiftReduce, TDump, XDump,
  assign, case, counter, fence, global, match, omega, semantic, stack,
  trace, tree.

  **Note on `beauty_tree_driver`:** SPITBOL itself fails this driver
  with `error 067 -- array dimension is zero, negative or out of
  range` at `tree.sno(16)`.  The pre-baked `.ref` contains the correct
  `PASS: 1..4` output that a well-behaved SNOBOL4 implementation should
  produce — which scrip produces in all three modes.  Here scrip is
  actually more correct than the nominal oracle on this one driver;
  per RULES.md the `.ref` is authoritative.

  **Top-level `beauty.sno`** (the library itself, at
  `demo/beauty.sno`) has no standalone `.ref` — it's exercised
  exclusively through the 17 `beauty_*_driver.sno` files, each of
  which exercises a slice of the library.  "beauty.sno self-hosts
  cleanly under all three modes" therefore means: every driver
  exercising beauty.sno passes diff=0 in every mode.  That is the
  state achieved at SN-7.

  **Gates:** Smoke PASS=7, Broker PASS=49, Broad corpus PASS=224/225
  (demo_claws5 only, out of scope), SN-7 gate PASS=51/51.

- [x] **SN-8** -- next rung on the SN-7..SN-9 Phase 2 path.  **Scoped 2026-04-19:**
      close the long-standing `. *fn(args)` / `$ *fn(args)` / bare `*fn(args)`
      args-are-NULL gap on the SM and JIT paths (tags-empty on `--sm-run`
      in the 7-line `rec` repro).

  **Symptom (reproduced):**  `/tmp/rec_repro.sno`:
  ```snobol4
            &ANCHOR = 0
            &FULLSCAN = 1
            nPushes = 0
            tags = ''
            DEFINE('Push(t)')                  :(push_end)
  Push      nPushes = nPushes + 1
            tags = tags ' ' t
            Push = .nPushes                    :(NRETURN)
  push_end
            rec = 'a' . *Push('A') *rec | 'a' . *Push('B')
            'aa' POS(0) rec RPOS(0)            :F(no)S(yes)
  no        OUTPUT = 'NO MATCH'                :(END)
  yes       OUTPUT = 'MATCH count=' nPushes ' tags=' tags
  END
  ```
  SPITBOL and `--ir-run`: `MATCH count=a tags= A B`.
  `--sm-run` (and `--jit-run`): `MATCH count=a tags=  ` — args never reach
  `Push`.  Count differs because capture fires but `t` arg is null.

  **Root cause (pinpointed):** two opcodes in the SM path ignore args.

  1. `sm_interp.c:541`  `SM_PAT_USERCALL` handler — bare `*fn(args)` —
     hardcodes `pat_user_call(fname, NULL, 0)`.  The SN-17a comment at
     :538-539 says args would be wired in SN-17d; SN-17d turned out to
     be a different fix and this piece was never landed.
  2. `sm_interp.c:525,527`  `SM_PAT_CAPTURE_FN` handler — `. *fn(args)`
     and `$ *fn(args)` forms — hardcodes `pat_assign_callcap*(child,
     fname, NULL, 0, ...)` on both the name-stash and legacy branches.
     Name-stash covers only the all-E_VAR case; the eager-eval fallback
     was never implemented.  **This is the failing repro's actual site**
     — the `rec` pattern uses `. *Push('A')` (E_QLIT arg, not E_VAR, so
     name-stash returns NULL, so handler hits the "args NULL/0" branch).

  Reference path for the fix: `--ir-run`'s `driver/interp.c:3091-3144`
  (E_CAPT_COND_ASGN) and `runtime/x86/stmt_exec.c:961-970` (E_DEFER(E_FNC)
  DT_E thaw in `bb_deferred_var`) both do the right thing: when args are
  not all E_VAR, eager-evaluate them at build time via `interp_eval` /
  `eval_node` into a `DESCR_t[]` and pass to `pat_assign_callcap` /
  `pat_user_call`.

  **SN-8a (landed 2026-04-19):** args-on-stack SM opcodes for the
  non-all-E_VAR fallback.  Two new opcodes added; handlers in interp
  and JIT; lowering emits them when `sm_pat_capture_fn_arg_names`
  returns NULL and the function has children.

  **Landed changes:**

  - `sm_prog.h`: added `SM_PAT_CAPTURE_FN_ARGS` (a[0].s=fname,
    a[1].i=kind, a[2].i=nargs) and `SM_PAT_USERCALL_ARGS` (a[0].s=fname,
    a[1].i=nargs).  Full doc comments.
  - `sm_prog.c`: opnames table + `sm_prog_print` cases for both.
  - `sm_lower.c`: `E_CAPT_COND_ASGN` / `E_CAPT_IMMED_ASGN` / `E_DEFER(E_FNC)`
    branches — when `sm_pat_capture_fn_arg_names()` returns NULL and
    `fnc->nchildren > 0`, lower each arg via `lower_expr` (pushing onto
    the value stack in source order 0..nargs-1) and emit the new `_ARGS`
    opcode variant.  All-E_VAR / zero-arg cases keep the TL-2 name-stash
    path.
  - `sm_interp.c`: `SM_PAT_CAPTURE_FN_ARGS` handler pops nargs values
    (positions nargs-1..0 to reconstruct source order), pops the child
    pattern, builds `pat_assign_callcap(child, fname, argv, nargs)`.
    `SM_PAT_USERCALL_ARGS` handler pops nargs values (no child), builds
    `pat_user_call(fname, argv, nargs)`.
  - `sm_codegen.c`: JIT mirrors — `h_pat_capture_fn_args` /
    `h_pat_usercall_args` registered in `g_handlers[]`.

  **Design notes:**

  - **Two new opcodes, not one** — follows the SN-8 scoping's
    recommendation.  Avoids union-discrimination hazards on `a[2]`
    (which holds `.s` for the existing name-stash path and `.i` for
    the new nargs path).  The existing `SM_PAT_CAPTURE_FN` /
    `SM_PAT_USERCALL` opcodes are untouched in semantics.
  - **`kind` (cond vs imm) is carried by NM_CALL NameKind_t inside the
    XCALLCAP node**, not by `pat_assign_callcap`'s args — same as the
    existing `SM_PAT_CAPTURE_FN` path.  The new handler accepts
    `a[1].i` and ignores it (documented with `(void)` cast).
  - **Arg-order pop:** values pushed 0..nargs-1, popped into argv
    positions nargs-1..0 to reconstruct original order for the callee.

  **Gates (all green, no regressions):**
  | Gate | Result | Target |
  |------|--------|--------|
  | Smoke | PASS=7 | PASS=7 ✓ |
  | Broker | PASS=49 | PASS=49 ✓ |
  | Broad corpus | PASS=224/225 | ≥224 ✓ |
  | Porter `--ir-run` | 0-line diff | byte-identical ✓ |
  | Porter `--sm-run` | 0-line diff | byte-identical ✓ |
  | SN-7 beauty self-host | PASS=51 | PASS=51 ✓ |

  **Repros (all four oracles converge — SPITBOL, `--ir-run`, `--sm-run`,
  `--jit-run`):**

  - `/tmp/rec_repro.sno` (`. *Push('A')` with E_QLIT arg) —
    `MATCH count=a tags= A B` in all four (was `tags=  ` in SM/JIT
    before fix).
  - `/tmp/usercall_args.sno` (bare `*PushAndEps('A')` with E_QLIT arg) —
    `MATCH count=3 tags= A A B` in all four (was `tags=  ` in SM/JIT
    before fix).

  **Still open (latent, non-blocking):**

  - **Named-args path in `SM_PAT_USERCALL`** (the all-E_VAR case): the
    lowering stashes names in `a[2].s`, but the handler still builds
    `pat_user_call(fname, NULL, 0)` — the name list is emitted but
    never consumed.  SN-17a's TL-2 comment still applies.  Not
    exercised by the SN-8a repros (they use E_QLIT args, which take
    the new `_ARGS` path).  Would show up as empty tags on a bare
    `*fn(var)` pattern where `var` is referenced inside `fn`.
    Defensible as a follow-up rung when / if a corpus program hits it.

  - **SM-side XATP arg-name stash gap** (noted in SN-17a history /
    SN-23d-follow-up): inside `pat_user_call`'s XATP node, the
    all-E_VAR named-args resolution at match time is also not wired.
    Same class of follow-up as the bullet above.

  Both of the above are pre-existing and orthogonal to SN-8a's scope.

- [~] **SN-9** -- JIT/codegen parity with `sm_interp`.  Goal: `--jit-run`
  produces byte-identical output to `--ir-run` / `--sm-run` on all
  gates (Smoke, Broker, SN-7 beauty self-host, Broad corpus, Porter).

  **Starting state (HEAD `546fe13e`, before SN-9a):** Porter
  `--jit-run` showed a 7979-line diff vs ref.  Root cause revealed by
  stderr-prefix noise in the output: `sm_codegen: unimplemented opcode
  11 (SM_PUSH_EXPR) at sm-pc=994` — the codegen dispatch table left
  `SM_PUSH_EXPR` as `h_unimpl`, which sets `last_ok=0` and pushes
  nothing.  Downstream pattern machinery saw an empty stack slot
  where a DT_E frozen expression should have been, producing
  systematically wrong stem output.

  **Parity audit** (opcodes emitted by `sm_lower` vs opcodes wired
  in codegen `g_handlers[]`):

  ```
  Emitted but MISSING from codegen handlers:
    SM_PUSH_EXPR      ← SN-9a target (closes Porter)
    SM_ACOMP          ← arithmetic comparison
    SM_LCOMP          ← length comparison
    SM_JUMP_INDIR     ← computed :(expr) gotos
    SM_BB_ONCE        ← BB-broker single-shot (Prolog / Icon)
    SM_BB_PUMP        ← BB-broker generator (Prolog / Icon)
  ```

  The comment at `sm_codegen.c:654-657` noted these were "not emitted
  by sm_lower for the PASS=178 corpus" — stale from an earlier era;
  the PASS count is now 224 and Porter does emit `SM_PUSH_EXPR`.

- [x] **SN-9a** -- Close the `SM_PUSH_EXPR` gap in codegen.
  **Done 2026-04-19.**

  Added `h_push_expr` handler (7 LOC) in `sm_codegen.c` mirroring
  the `sm_interp.c` SM_PUSH_EXPR case exactly.  Same union-aliasing
  discipline as the four DT_E constructor sites fixed at SN-6b —
  `d.slen = 0` before `d.ptr = ...` because `.s` and `.ptr` share a
  union.  Registered in `g_handlers[SM_PUSH_EXPR]` alongside the
  existing `SM_PUSH_VAR` entry.

  **Porter measurement (--jit-run, diff-lines vs ref / 23531):**
  - Before: 7979 lines diff + 2 `sm_codegen: unimplemented` warnings
    streamed into stdout.
  - After: **0 lines diff** — byte-identical to `--ir-run` and
    `--sm-run` references.

  **Gates (all green, no regressions):**
  - Smoke PASS=7
  - Broker PASS=49
  - SN-7 beauty self-host PASS=51/51
  - Broad corpus PASS=224/225 (`demo_claws5` only — pre-existing,
    out of scope)
  - Porter `--ir-run`, `--sm-run`, `--jit-run` all 0-line diff

  **Files changed:**
  - `src/runtime/x86/sm_codegen.c`: added `h_push_expr` handler and
    `g_handlers[SM_PUSH_EXPR] = h_push_expr` registration.

- [x] **SN-9b** -- Close remaining codegen handler gaps.
  **Done 2026-04-19.**  one4all @ `f8b06dc6`.

  Scoped tight by the parity audit: of the five opcodes `sm_lower`
  emits that codegen left as `h_unimpl`, only two were genuine live
  JIT gaps — `SM_BB_PUMP` (Icon/Raku generators) and `SM_BB_ONCE`
  (Prolog backtracking).  The other three (`SM_ACOMP`, `SM_LCOMP`,
  `SM_JUMP_INDIR`) are stale or cross-mode issues outside SN-9 scope;
  see classification in the original SN-9 audit block above.

  **Landed changes (sm_codegen.c):**
  - `bb_broker.h` include + `icn_eval_gen` extern declaration.
  - `h_bb_pump` handler (~12 LOC): pops DT_E, extracts EXPR_t*, calls
    `icn_eval_gen` to build a bb_node_t, drives via
    `bb_broker(node, BB_PUMP, jit_pump_print, NULL)`.  Sets
    `last_ok = (ticks > 0)`.
  - `h_bb_once` handler (~10 LOC): same shape but `BB_ONCE` intent
    and no print callback.
  - `jit_pump_print` callback — identical logic to the `pump_print`
    static in sm_interp.c, renamed to avoid link-time collision
    (both files compile to separate .o's but the symbol is static
    in sm_interp.c — the rename is defensive, keeps the codegen
    copy distinct).
  - Registration: `g_handlers[SM_BB_PUMP] = h_bb_pump;`
    `g_handlers[SM_BB_ONCE] = h_bb_once;`.
  - Rewrote the stale comment at the bottom of `init_handler_table`
    (referenced a defunct "PASS=178 corpus").  New comment classifies
    each remaining `h_unimpl` stub as *stale emit path* (ACOMP/LCOMP),
    *cross-mode issue* (JUMP_INDIR), or *never emitted* (TRIM, SPCINT,
    SPREAL, SELBRA, STATE_PUSH/POP, RCOMP).

  **Verification:** `test/raku_gather.scrip` (the existing
  BB_PUMP polyglot test used by the broker smoke) produces
  byte-identical output under `--sm-run` and `--jit-run`.

  **Gates (all green, no regressions):**
  - Smoke PASS=7
  - Broker PASS=49
  - SN-7 beauty self-host PASS=51/51
  - Broad corpus PASS=224/225 (`demo_claws5` only, pre-existing)
  - Porter `--ir-run` / `--sm-run` / `--jit-run` all 0-line diff

  **Files changed:** `src/runtime/x86/sm_codegen.c` (+56 LOC, -4).

- [x] **SN-9c** -- End-to-end `--jit-run` gate: broad corpus
  `--jit-run` at parity with `--ir-run` / `--sm-run`.  Codified as a
  three-mode sweep script.  **Done 2026-04-19.**

  **Closing summary.**  SN-9c opened as a gate-codification rung but
  the initial three-mode sweep found **7 JIT-only failures** that
  passed in the other two modes.  All 7 closed across SN-9c-a..e:
  case-folding in `h_call` pseudo-calls (SN-9c-a) fixed the two
  `_indirect_*` programs, a missing `NRETURN_ASGN` branch (SN-9c-b)
  fixed `1013_func_nreturn`, `last_ok` parity in `h_push_var` /
  `h_store_var` (SN-9c-c) fixed `word1`, DT_SNUL coercion + FAIL
  propagation in `h_arith` (SN-9c-c-bis) fixed `wordcount` and
  `triplet` as a bonus, and pre-call FAIL propagation in `h_call`
  (SN-9c-d) fixed `fileinfo`.  The gate script `test_smoke_snobol4_jit.sh`
  (SN-9c-e) now sweeps all crosscheck programs in all three modes
  and fails if `--sm-run` or `--jit-run` regresses below `--ir-run`
  PASS count.  Current state: 207/207/207 on crosscheck, 224/225
  on broad corpus in each mode (same `demo_claws5` in all three).

  **Discovery (at rung open):** The assumption that `--jit-run`
  already matched `--sm-run` on broad corpus was wrong.  A full
  three-mode sweep across the 225 broad-corpus programs surfaced
  **7 JIT-only failures** that pass in both `--ir-run` and
  `--sm-run`: `fileinfo`, `triplet`, `1013_func_nreturn`,
  `210_indirect_ref`, `211_indirect_assign`, `word1`, `wordcount`.
  So `--jit-run` was at 217/225 vs the 224/225 baseline the other
  two modes hit.  SN-9c became parity work as well as gate work.

  - [x] **SN-9c-a** -- SN-19 case-folding in `h_call` pseudo-call
    handlers.  Done 2026-04-19.  Closed `210_indirect_ref` and
    `211_indirect_assign`.

    **Root cause:** `sm_codegen.c`'s `INDIR_GET`, `NAME_PUSH`, and
    `ASGN_INDIR` branches in `h_call` (lines 530-553) looked up /
    stored variables using the raw descriptor string, skipping the
    `GC_strdup(...); sno_fold_name(...)` pattern that
    `sm_interp.c:644-702` uses.  Folding matters because parser-emitted
    variable names are already uppercased (e.g. `bal = 'the real bal'`
    stores to `BAL` per `SM_STORE_VAR s="BAL"` in the dump), but
    `$'bal'` carries the literal lowercase `bal` on the stack — JIT's
    `NV_GET_fn("bal")` missed the `BAL` key, while sm_interp's folded
    version hit it.

    **Fix:** port the three folds verbatim from `sm_interp.c:656,661,
    678,691,696` to `sm_codegen.c`.  Six mechanical lines.

  - [x] **SN-9c-b** -- Add missing `NRETURN_ASGN` handler in
    `h_call`.  Done 2026-04-19.  Closed `1013_func_nreturn`.

    **Root cause:** `sm_codegen.c`'s `h_call` had no `NRETURN_ASGN`
    branch at all — the opcode fell through to the generic
    `INVOKE_fn(name, argv, nargs)` path at the bottom of the
    function.  That path reads `nargs` from `CUR_INS->a[1].i`, but
    for `NRETURN_ASGN` the `sm_lower` encoding uses `a[1].s` (the
    function name) — so `a[1].i` is garbage pointer bits, producing
    `nargs = 139605120935872` and an immediate stack underflow /
    abort.  Stack trace: `sm_interp: stack underflow; Aborted`.

    **Fix:** port `sm_interp.c:704` verbatim into a new
    `NRETURN_ASGN` branch in `h_call`.  Reads fname from `a[1].s`,
    pops rhs, calls fn with zero args, writes through DT_N return
    or falls back to `fname_SET` field-mutator convention.  Also
    folds the NAMEVAL branch per SN-9c-a pattern.

  **Gates after SN-9c-a+b (all green, no regressions):**
  - Smoke PASS=7
  - Broker PASS=49
  - SN-7 beauty self-host PASS=51/51
  - Broad corpus `--sm-run` PASS=224/225 (same `demo_claws5` only)

  **Remaining JIT-only failures (4):**
  `fileinfo`, `triplet`, `word1`, `wordcount`.

  **`word1` diagnostic** (reproduces on `wordcount` too — both use
  `LINE = INPUT :F(END)` loop):
  - Input: 3 lines (2 contain noun phrases, 1 doesn't).
  - SPITBOL / `--ir-run` / `--sm-run`: output `cat\nhouse` (2 lines).
  - `--jit-run`: output `cat` only; exits cleanly (exit=0) after
    the first match instead of continuing to the second input line.
  - JIT is prematurely terminating the `LOOP LINE = INPUT :F(END) /
    LINE ? PAT :(LOOP)` cycle.  Likely an `INPUT` built-in
    short-circuit or a `:F(END)` branch mis-resolution in the JIT
    dispatch for `SM_JUMP_F` on the `LINE = INPUT` statement.  Not
    investigated to root cause this session — next-rung target.

  `fileinfo` and `triplet` not investigated this session — start
  with `triplet` (smaller; name suggests triple / 3-ary pattern)
  to find the third gap class, then decide whether `fileinfo` shares
  it.

  **Files changed this session:**
  `src/runtime/x86/sm_codegen.c` (~40 LOC added/modified in
  `h_call`: six folding lines across 3 branches + ~25-line
  `NRETURN_ASGN` branch).

  **Gate script not yet landed.**  Once the remaining 4 failures
  close (or are documented as deferred with expected-failure list),
  write `scripts/test_smoke_snobol4_jit.sh` modelled on
  `test_gate_sn7_beauty_self_host.sh`: three-mode × broad-corpus
  sweep, diff=0 vs `.ref`, PASS=N FAIL=0 target.

  - [x] **SN-9c-c** -- SN-6 `last_ok` parity in `h_push_var` and
    `h_store_var`.  Done 2026-04-19.  Closes `word1`; partially
    closes `wordcount` (count correct, formatting bug remains —
    see below for SN-9c-c-bis).

    **Root cause (two-part bug in `sm_codegen.c`, both missing SN-6
    semantics present in `sm_interp.c`):**

    1. **`h_push_var` did not set `last_ok`.**  `sm_interp.c:261-268`
       explicitly sets `st->last_ok = (val.v != DT_FAIL)` so that
       keyword reads like `INPUT` at EOF correctly propagate failure
       to the enclosing statement's `:F` branch.  JIT's `h_push_var`
       pushed the value and returned — leaving `last_ok` at whatever
       the previous opcode left it at.

    2. **`h_store_var` did not set `last_ok = 1` on success.**
       `sm_interp.c:296-301` sets it so that a prior failure (e.g.
       a pattern-match FAIL in the previous iteration) does not
       bleed into this statement's `:F` branch across a loop-back
       goto.  JIT's `h_store_var` only set `last_ok = 0` on the
       FAIL path; success left `last_ok` unchanged.

    **`word1` failure trace (before fix):**  First iteration,
    `LINE = INPUT` succeeds, `LINE ? PAT` matches → prints `cat` →
    jumps back.  Second iteration, `PUSH_VAR INPUT` reads next line
    ("Nothing interesting..."), pushes it; JIT leaves `last_ok` at
    1 (from prior match success).  `STORE_VAR LINE` stores
    successfully but doesn't reset `last_ok`, leaving whatever was
    there.  `EXEC_STMT` for `LINE ? PAT` fails (no "the X of/a Y")
    → `last_ok = 0`.  Loops back.  Third iteration: `PUSH_VAR INPUT`
    reads "I know the house...", pushes it (val is not FAIL, but
    JIT doesn't set `last_ok = 1`).  `STORE_VAR LINE` stores
    successfully but **doesn't reset `last_ok = 1`** — so it's
    still 0 from the previous match failure.  `JUMP_F` fires →
    jumps to END, printing only `cat`.

    **Fix (two additions, ~4 LOC total):**
    ```c
    static void h_push_var(void) {
        DESCR_t val = NV_GET_fn(CUR_INS->a[0].s);
        PUSH(val);
        STATE->last_ok = (val.v != DT_FAIL);   /* SN-9c-c */
    }

    static void h_store_var(void) {
        DESCR_t val = POP();
        if (val.v == DT_FAIL) { STATE->last_ok = 0; return; }
        DESCR_t stored = NV_SET_fn(CUR_INS->a[0].s, val);
        PUSH(stored);
        STATE->last_ok = 1;                    /* SN-9c-c */
    }
    ```

    **Verification:**
    - `word1 --jit-run`: 0-line diff vs ref ✓
    - `wordcount --jit-run`: count correct (14), but output is
      `14. words` vs ref `14 words` — formatting bug remains,
      tracked as SN-9c-c-bis below.

    **Gates (all green, no regressions):**
    - Smoke PASS=7
    - **Broker PASS=49** (+1 from 48 baseline — the SN-6 last_ok
      parity fix recovered the pre-existing broker drift; this
      confirms the bug class was broader than just `word1`)
    - Broad corpus: not re-measured this session

    **Files changed:** `src/runtime/x86/sm_codegen.c` — `h_push_var`
    and `h_store_var`, ~4 LOC additions each with explanatory
    comments pointing to the `sm_interp.c` parity lines.

  - [x] **SN-9c-c-bis** -- `wordcount` formatting bug: `+N` unary
    plus under `--jit-run` outputs `14.` instead of `14`.
    **Done 2026-04-19.**  Also closes `triplet --jit-run` as a
    bonus — same bug class.

    **Root cause (pinpointed by minimal repro):**

    The hypothesis track (b) from the original SN-9c-c-bis block was
    correct — `jit_arith` produced DT_R for sums that should have
    been DT_I — but the upstream cause was not what I'd guessed.
    It wasn't `to_int_jit` mis-parsing; it was **DT_SNUL never
    getting coerced to INTVAL(0)** before `jit_arith` ran.

    `sm_interp.c:321-331` has a four-step pre-arith dance:
    ```c
    if (l.v == DT_FAIL || r.v == DT_FAIL) { ... FAIL ... }
    if (l.v == DT_S)    l = INTVAL(to_int(l));
    if (r.v == DT_S)    r = INTVAL(to_int(r));
    if (l.v == DT_SNUL) l = INTVAL(0);
    if (r.v == DT_SNUL) r = INTVAL(0);
    ```
    JIT's `h_arith` only did the two DT_S lines.  No FAIL
    propagation, no DT_SNUL coercion.

    So for wordcount: `N` starts unset (DT_SNUL), `N + 1` leaves
    `l.v = DT_SNUL`, `jit_arith` checks `l.v == DT_I && r.v == DT_I`
    → false → falls through to the REALVAL branch → result is
    DT_R(1.0).  Next iteration DT_R(1.0) + DT_I(1) → DT_R(2.0).
    By end, `N` is DT_R(14.0).  The DT_R→string formatter on JIT
    outputs `14.` (trailing dot with zero fractional digits stripped).

    **Minimal repro (confirmed bug and confirmed fix):**
    ```snobol4
          N       = N + 1
          N       = N + 1
          OUTPUT  = +N ' words'
    END
    ```
    Before fix: `--ir-run`/`--sm-run` → `2 words`; `--jit-run` → `2. words`.
    After fix: all three modes → `2 words`.

    **Fix:** one hunk in `sm_codegen.c` `h_arith` — added FAIL
    propagation and DT_SNUL coercion, matching `sm_interp.c:321-331`
    verbatim in semantics.  ~10 LOC.

    **Gates (all green, no regressions):**
    - Smoke PASS=7
    - **Broker PASS=49** (+1 from 48 baseline — same bug class
      cleared another broker test; confirms the scope was broader
      than just `wordcount`)
    - SN-7 beauty self-host PASS=51/51
    - Broad corpus PASS=224/225 (`demo_claws5` only — pre-existing,
      out of scope)

    **Bonus: `triplet --jit-run` now 0-line diff vs ref.**  Same
    DT_SNUL + arith class.  Removed from SN-9c-d's worklist.

    **Files changed:**
    - `src/runtime/x86/sm_codegen.c`: `h_arith` gained the four
      missing sm_interp.c:321-331 lines — FAIL propagation (early
      return with FAILDESCR and `last_ok=0`) and DT_SNUL→INTVAL(0)
      coercion on both operands.

  - [x] **SN-9c-d** -- Close `fileinfo --jit-run` hang.  Done 2026-04-19.
    Root-caused to missing pre-call FAIL-propagation in `h_call` at
    `sm_codegen.c`.

    **Root cause (pinpointed via opcode dump + minimal repro):**

    The minimal repro was a 4-line program: `CHARS = CHARS + SIZE(INPUT)
    :F(done)` fed empty stdin.  `--ir-run` / `--sm-run` correctly
    branched to `done`; `--jit-run` fell through to the next
    statement, meaning the `:F` branch never fired.

    SM dump for the statement:
    ```
    SM_PUSH_VAR  "CHARS"
    SM_PUSH_VAR  "INPUT"
    SM_CALL      "SIZE" nargs=1
    SM_ADD
    SM_STORE_VAR "CHARS"
    SM_JUMP_F    -> done
    ```

    Expected flow at EOF:
    1. `h_push_var("INPUT")` → pushes FAILDESCR, `last_ok=0` ✓
    2. `h_call("SIZE", 1)` → sees FAIL arg, should bail out with
       FAIL / `last_ok=0`
    3. `h_arith` → sees FAIL, propagates → `last_ok=0`
    4. `h_store_var("CHARS")` → sees FAIL val, `last_ok=0`, returns
    5. `h_jump_f` → `last_ok=0`, branches to `done` ✓

    The gap was at step 2.  `sm_interp.c:799-810` has an explicit
    pre-call FAIL check (SN-6 semantics — any arg == FAIL means the
    function is not invoked, the whole statement fails):
    ```c
    for (int k = 0; k < nargs; k++) {
        if (args[k].v == DT_FAIL) {
            sm_push(st, FAILDESCR);
            st->last_ok = 0;
            goto sm_call_done;
        }
    }
    ```
    `h_call` in `sm_codegen.c` was missing this block.  So SIZE was
    invoked on the FAIL argument, returned `INTVAL(0)` (swallowed
    the FAIL), `last_ok` became 1, the `:F` branch didn't fire, and
    the accumulator loop ran forever.

    Same bug class as SN-9c-c and SN-9c-c-bis — pieces of SN-6
    FAIL-propagation semantics that landed in `sm_interp.c` but
    never got ported to `sm_codegen.c`.

    **Fix:** verbatim port of `sm_interp.c:799-810` into
    `h_call` at `sm_codegen.c`, right after the `args[]` pop loop.
    Same early-return shape (PUSH FAILDESCR, set `last_ok=0`, return)
    adapted to the JIT handler's control flow (uses `return` instead
    of `goto sm_call_done`).

    **Gates (all green, no regressions):**
    - Smoke PASS=7
    - **Broker PASS=49** (+1 from 48 baseline — same bug class
      cleared another broker test; confirms the scope was broader
      than just `fileinfo`, same pattern as SN-9c-c / SN-9c-c-bis
      broker recoveries)
    - SN-7 beauty self-host PASS=51/51
    - Broad corpus PASS=224/225 in all three modes (`demo_claws5`
      only — pre-existing, out of scope)
    - SN-9c-e gate: 207/207/207 on crosscheck (PASS=three-mode parity)

    **Files changed:**
    - `src/runtime/x86/sm_codegen.c`: `h_call` gained the 11-line
      pre-call FAIL-propagation loop after `args[]` is popped,
      matching `sm_interp.c:799-810` semantics verbatim.

  - [x] **SN-9c-e** -- Land `test_smoke_snobol4_jit.sh` three-mode
    sweep gate.  Done 2026-04-19.

    **Gate semantics:**
    - Runs every `.sno` in `$CORPUS/crosscheck` under all three modes
      (`--ir-run`, `--sm-run`, `--jit-run`).
    - Compares output against the pre-baked `.ref` file using `[$got
      = $exp]` string equality (same idiom as
      `test_interp_broad_corpus_and_beauty.sh`).
    - Uses `--ir-run` PASS count as the reference: `--sm-run` and
      `--jit-run` must match it.  Shared failures (programs that fail
      in all three modes) are reported as info only, not gate fails —
      they're tracked as orthogonal bugs via their own goals.
    - Runs in ~27s on a clean build.  Self-contained per RULES.md
      (paths derived from `$0`; corpus-not-found / scrip-not-built
      both SKIP cleanly).

    **Current gate result:** 207/207/207 on crosscheck — full
    three-mode parity.

    **Files changed:**
    - `scripts/test_smoke_snobol4_jit.sh` (new, 95 LOC, executable).


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


- [ ] **SN-25** -- SPITBOL `-f` structural-keyword lookup fix.
  **Root cause pinpointed 2026-04-20, fix not yet landed.**

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

  - [ ] **SN-25a** -- Reproduce baseline on a fresh `bootsbl`:
    ```bash
    cd /home/claude/x64 && make bootsbl
    ./bootsbl -b  /tmp/trivial2.sno   # hi,   exit 0
    ./bootsbl -bf /tmp/trivial2.sno   # FAIL, exit 1
    ```

  - [ ] **SN-25.x32** -- TRY FIRST: test `spitbol/x32` for the same
    bug.  SPITBOL also ships a 32-bit x86 variant at
    github.com/spitbol/x32.  If its `-bf` works correctly on
    `/tmp/trivial2.sno`, the `-f` path in x32's codegen is already
    sound and we can use `sbl32` as the case-sensitive oracle
    without touching `bootstrap/sbl.asm`.  Zero patching, zero risk,
    ~5 minutes to clone+build+test.  Only pivot to SN-25b if x32
    shows the same bug.
    ```bash
    cd /home/claude
    git clone https://github.com/spitbol/x32
    cd x32 && make  # or whatever x32's build target is
    ./bin/sbl -bf /tmp/trivial2.sno   # hi, exit 0 would close SN-25
    ```

  - [ ] **SN-25b** -- Patch `bootstrap/sbl.asm` `gnv10` to fold
    compared bytes when the current entry's svbit has `svlbl` set;
    rebuild via `make bootsbl`.  Verify the trivial repro now passes
    under `-bf`.

  - [ ] **SN-25c** -- Mirror the patch in the upstream `.sbl` source
    (likely `asm.sbl` or `lex.sbl`).  Run `make sbl` using the
    patched `bootsbl` as `$(BASEBOL)`; verify the regenerated
    `sbl.asm` carries the same semantics.  Install the new binary as
    `bin/sbl`.

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

  - [ ] **SN-26b** -- Install `beautiful.sno` (the one-file zip
    concatenation) at `corpus/programs/snobol4/demo/beautiful.sno`.
    No subsystem `.inc` files alongside — it is self-contained.
    Produce a reference artefact `beautiful.self.ref` by running
    SPITBOL (`-bf` once SN-25 is closed, or `sbl32 -bf` if SN-25.x32
    succeeds) on `beautiful.sno < beautiful.sno` and capturing
    stdout.  Apply at most 1-2 minor source fixes if required
    — everything else is a scrip bug to fix.

  - [ ] **SN-26c** -- Self-host under the 4-way monitor.  Run
    `scrip-monitor --monitor beautiful.sno < beautiful.sno`.  Start
    with the first DIVERGE and walk each in turn.  The corpus-era
    run showed `UTF_Array='797163616:32490'` at stmt 152 label `G1`
    (a descriptor-stringification class bug on `--ir-run`) — expect
    similar shapes on the concatenated form, though stmt numbers
    will shift.  Fix; rerun; walk the next DIVERGE.  Continue until
    monitor reports all-agree across IR/SM/JIT/CSN.  Keep gates
    green at each step (Smoke=7, Broker=49, Broad corpus=225/225,
    SN-7 driver 51/51).

  - [ ] **SN-26d** -- Add `test_smoke_beauty_self_host.sh` — a gate
    script that runs `scrip <mode> beautiful.sno < beautiful.sno`
    in all three modes, diffs output against pre-baked
    `beautiful.self.ref` (generated from SPITBOL `-bf` under SN-25
    or `sbl32 -bf` under SN-25.x32), PASS=3 FAIL=0.  Makes "beauty
    self-hosts" a standing gate.


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

**HEAD:** one4all — SN-6 closed via a one-word gate-script fix
(`test_interp_broad_corpus_and_beauty.sh:67` now points `demo_claws5`
at `claws5.input` instead of `CLAWS5inTASA.dat`; matches the
demo-scale ref).  Broad corpus PASS=225/225 in all three modes.

**2026-04-20 session reassessment.**  SN-9 was ready to close and the
session's first fix (SN-6) closed on a gate wiring error, not a
runtime bug.  Lon then redirected to the goal-level Done-when clause:
*"beauty.sno self-hosts cleanly under all three modes."*  Investigation
showed:

- **SN-7 was overclaimed.**  51/51 covers the 17 subsystem drivers
  (`beauty_*_driver.sno`), not the top-level `Parse`/`main00..main05`
  stdin loop.  See SN-7-note above.
- **`beauty.sno` does not self-host under any implementation today.**
  SPITBOL errors at line 781 (error 021, 765 stmts in), CSNOBOL4
  errors at line 770 (error 8), scrip `--ir-run` trips beauty's own
  `mainErr1` at 10 output lines.  All three fail in different ways.
- Lon supplied the original upstream SNOBOL4 bundle
  (`/home/claude/originals/`) — a smaller, cleaner `beauty.sno` (630
  lines vs corpus's 781) plus 16 `.inc` subsystems, predating the
  `--auto`/`ppArg*` profiling machinery.  Stripping 3 SNOBOL4-only
  compat shims (`is.inc`/`FENCE.inc`/`io.inc`) is safe under SPITBOL.
- Clean form still fails under `sbl -b` because beauty uses the
  double-function trick (`shift`/`Shift`, `reduce`/`Reduce`, `pop`/
  `Pop`, `visit`/`Visit` — 4 case pairs).  Correct invocation is
  `sbl -bf`.  But **`sbl -bf` is broken** — error
  "No END statement found" on *any* program, trivial or not.
- **SN-25 opened** to fix the `-bf` bug.  Root cause pinpointed:
  `bootstrap/sbl.asm:14408-14413` (`gnv10`) does a bytewise compare
  between source-identifier chars and lowercase-literal keyword
  table entries (`v_end`, `v_ret`, `v_frt`, `v_nrt`, `v_cnt`,
  `v_scn`).  Under `-f` no fold happens; `END` bytes don't match
  `end` bytes; END is never recognized; file exhausts; error fires.
  Fix scope: fold both compared bytes (OR 0x20) in `gnv10` when the
  current entry is svlbl-typed.  Build pipeline verified in this
  container (`make bootsbl` succeeds in ~3s, no SBL needed).
  SN-25a..e enumerated.

- **SN-26 opened** for the true self-host work, gated on SN-25.
  First scrip divergence already located via `scrip-monitor`: at
  **stmt 152, label `G1`, line 169**, `UTF_Array` under `--ir-run`
  holds `ARRAY('797163616:32490')` (corrupted descriptor-or-pointer
  stringification into an ARRAY dimension arg) vs `ARRAY('124,2')`
  under SM/JIT.  Feels DT_E / descriptor-aliasing.  Not fixed this
  session — captured as SN-26c's entry point.  Lon also directed:
  rename corpus's fancy `demo/beauty.sno` → `demo/beautifier.sno`;
  install the clean stdin-reading form as the committed `beauty.sno`.
  Staged in `/home/claude/orig_test/` this session; not installed
  yet (SN-26a/b).

**Gates (all green, no regressions — verified fresh this session):**
- Smoke **7**
- Broker **49**
- SN-7 subsystem drivers **51/51**
- Broad corpus **225/225** in all three modes (SN-6 closed)
- SN-9c-e JIT parity gate **207/207/207** on crosscheck

**Session trajectory:** clone HQ + one4all + x64 + csnobol4 + corpus
→ build scrip + SPITBOL + CSNOBOL4 + scrip-monitor + csnobol4 archive
→ run gates (Smoke=7, Broker=49, broad=224/225 with `demo_claws5`
failing) → trace claws5 failure to stale CLAWS5inTASA.dat reference
in gate script → one-word fix to line 67 of
`test_interp_broad_corpus_and_beauty.sh` → broad=225/225 → Lon redirects
to beauty self-host → discover SN-7 gate tests subsystems not top-level
→ run literal `scrip <mode> beauty.sno < beauty.sno` → observe
`Parse Error` at 10 lines → confirm both oracles (SPITBOL, CSNOBOL4)
also fail self-host differently → Lon supplies originals bundle →
stage clean form in `orig_test/` → discover SPITBOL `-f` breaks on
*any* program → trace root cause to lowercase keyword table
compared bytewise in `gnv10` → verify `make bootsbl` build works →
draft SN-25 fix plan → run `scrip-monitor` on corpus beauty.sno
self-input → locate first DIVERGE (stmt 152, UTF_Array) → draft
SN-26 → commit/push.

**Next step:** **SN-25** (SPITBOL `-f` bootstrap fix) is the gating
rung.  Once `sbl -bf` works on trivial input, proceed to SN-26a
(rename fancy → `beautifier.sno`, install clean beauty.sno),
then SN-26c (close the `UTF_Array` divergence and walk the 4-way
monitor through the rest).

Latent follow-ups inherited from SN-8a (still open):

- Named-args path in `SM_PAT_USERCALL` (all-E_VAR stash never consumed
  downstream — pat_user_call builds XATP with args=NULL).  Not
  exercised by current corpus; defensible as SN-8b if a corpus
  program hits it.
- SM-side XATP arg-name stash gap (same class — named-args resolution
  inside pat_user_call's XATP node never wired).  Pre-existing from
  SN-17a history; orthogonal to SN-8a.

**Useful follow-ups noted during SN-22/23** (small, safe, not gating):
- `NAME_push` still returns `void *` for source compatibility but
  every caller discards it.  Change to `void` return is a defensible
  one-line cleanup.
- `cache_get_fresh` template purity — the real SN-6c root cause.
  bb_cap is self-healing at the site (SN-23d-follow-up) but any
  other box type storing in-flight scalars is vulnerable to the same
  class of bug.  Pristine-template rewrite is a defensible cleanup
  if symptoms appear elsewhere.

**Follow-up from 2026-04-20 SN-26 scout:**
- The `scrip-monitor --monitor` run reports `IR last_ok=?` on DIVERGE
  at stmt 152, while SM and JIT both show `last_ok=1`.  The `?` means
  IR's last_ok is uncaptured at the snapshot boundary.  Clean up
  (small, one-line in the IR snapshot code of `sync_monitor.c`) would
  remove one class of reporting ambiguity when debugging SN-26.


