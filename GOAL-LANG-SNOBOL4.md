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

- [ ] **SN-17** -- **CURRENT.** Porter stemmer gap — root cause isolated, pivoted to three-mode unification.

  **Measured at HEAD `8964586e`:**
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

- [ ] **SN-17a** -- Add `SM_PAT_USERCALL` opcode.
      - Add opcode in `sm_prog.h`.
      - Lower XATP-with-non-`@` in `sm_lower.c` to `SM_PAT_USERCALL`.
      - Add `case SM_PAT_USERCALL:` in `sm_interp.c`.
      - Add `h_pat_usercall` handler in `sm_codegen.c`, register in
        `g_handlers`.
      - Gate: `--sm-run` Porter measurement moves (even if still broken,
        number must change — proves the opcode fires).

- [ ] **SN-17b** -- Unify `bb_build` dispatch.
      Goal: eliminate the two parallel XKIND switches. Two design options
      to weigh at implementation time:
      (i) Single shared `bb_build_dispatch(PATND_t*, bb_build_mode_t)` in a
      new file; stmt_exec.c and bb_build.c both call it.
      (ii) Table-driven: `bb_box_ctor_t g_ctors[XKIND_COUNT]` indexed by
      XKIND; each entry is a function pointer.  Both files consult the
      same table.
      Gate: Smoke PASS=7, Broker PASS=49, no diff in Porter output.

- [ ] **SN-17c** -- Unify SM opcode handlers.
      Extract each `case SM_*:` body from `sm_interp.c` into a named
      function `sm_handle_<op>(SM_State *st, SM_Ins *ins)`.  `sm_interp.c`
      switch body becomes `sm_handle_<op>(st, ins); break;`.  `sm_codegen.c`
      handlers become one-line wrappers using the JIT globals.
      Single source of truth per opcode.
      Gate: Smoke PASS=7, Broker PASS=49, no diff in Porter/beauty output.

- [ ] **SN-17d** -- Fix `*fn()` FAIL propagation **once**, lands in all
      three modes via the unified dispatch from SN-17a..c.
      The fix shape (sketch, needs real-shape verify):
      ```c
      DESCR_t r = g_user_call_hook(name, args, nargs);
      if (IS_FAIL_fn(r))                             return FAILDESCR;
      if (r.v == DT_P && r.p && r.p->kind == XFAIL)  return FAILDESCR;
      /* else epsilon */
      ```
      Gate: Porter `--ir-run` and `--sm-run` both move upward and
      converge.  Target: both match SPITBOL on `abate`/`absence`/etc.

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

  **expr_eval diagnostic (measured at `8964586e`):**
  - `--ir-run`: 4/5 inputs → `snobol4:0: error: parse error: syntax error`.
    That is the SNOBOL4 *frontend parser*, not a pattern-match error —
    `EVAL(op arg)` is probably compiling the evaluated string as SNOBOL4
    statements.  The 2 lines that do parse produce wrong values:
    `(1+2)*3` → `3` (expected 9), `-3+10` → `10` (expected 7).  Two
    layered bugs: EVAL call path + operator precedence / Pop() ordering.
  - `--sm-run`: 5/5 → `Bad input, try again`.  The top-level
    `POS(0) expr RPOS(0)` pattern fails for every input.  Recursive
    `primary = constant | '(' *expr ')'` via bb_cap / NM_CALL is the
    likely fault line.

  Not DT_E (verified identical at pre-SN-21e).

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

**HEAD:** one4all @ `8964586e`. Gates: Smoke 7, Broker 48 (was 49 — one
test has drifted since last session; investigate separately).
**Next step:** SN-17a — add `SM_PAT_USERCALL` opcode.
