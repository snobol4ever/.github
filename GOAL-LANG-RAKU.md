# GOAL-LANG-RAKU.md — Raku Frontend Ladder

**Repo:** one4all
**Done when:** Raku rung ladder reaches rung-30 under all three modes
(--ir-run, --sm-run, --jit-run). gather/take maps cleanly to BB_PUMP.
Hash support, typed variables, and for-loop iteration complete.

**Cross-pollination:** Raku shares icn_proc_table and icn_call_proc with Icon.
Any fix to the ICN frame stack or BB_PUMP path immediately benefits Raku.
Raku's sub/return fix benefits interp.c E_RETURN used by all frontends.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh              # PASS=5
bash /home/claude/one4all/scripts/test_raku_ir_rungs.sh           # PASS=12
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh    # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_raku.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.raku → raku_compile() → Program* [LANG_RAKU]  (no AST layer — FI-3 done)
    --ir-run  → execute_program() → interp_eval() with ICN_CUR frame stack
                (Raku shares icn_proc_table + icn_call_proc with Icon)
    --sm-run  → sm_lower() → SM_BB_PUMP per stmt → bb_broker(BB_PUMP)
    --jit-run → sm_lower() → SM_BB_PUMP → sm_codegen() → sm_jit_run()

gather/take → E_SUSPEND box (icn_bb_suspend in icon_gen.c — shared with Icon)
for @arr -> $x → E_EVERY + E_BANG (icn_bb_every + icn_bb_bang — to be written)
```

---

## Rung ladder — all modes, x86

Current baseline: PASS=12 FAIL=0 --ir-run (rk_hello through rk_vars).
RK-16 is next per PLAN.md.

### Phase 1 — IR-run rung ladder

- [x] **RK-1 through RK-15** — PASS=12 --ir-run. (done)

- [x] **RK-16** — `for @arr -> $x` real array iteration.
  E_ITERATE extended in icn_drive (icn_runtime.c): detects loop variable name
  stored in E_ITERATE->sval (set by raku.y grammar action), splits SOH-delimited
  array string, binds each element to the frame slot via icn_scope_get.
  E_EVERY fixed in interp.c: sets body_root before calling icn_drive for
  non-E_TO generators. raku.tab.c regenerated from raku.y.
  Gate: rk_for_array PASS under --ir-run. PASS=13 total.

- [x] **RK-17** — Hash `%h<key>` and `%h{$k}` full support.
  Added KW_EXISTS/KW_DELETE tokens + lexer rules. VAR_HASH as standalone expr.
  exists %h<k> / delete %h<k> grammar rules. hash_pairs and hash_delete in
  interp.c. Gate: rk_hash17 PASS, test_raku_ir_rungs PASS=14 FAIL=0.

- [x] **RK-18** — Byrd box wiring + `given/when` smartmatch proper.
  **Root cause:** icn_drive() hand-rolls E_TO/E_TO_BY/E_ITERATE inline in C,
  bypassing the bb_broker/BB_PUMP Byrd box machinery that already exists in
  icon_gen.c. All generators must flow through bb_broker(BB_PUMP) to support
  --sm-run, --jit-run, and goal-directed backtracking.
  Sub-steps:
  - [x] RK-18a: icn_drive E_TO  → bb_broker(icn_bb_to, BB_PUMP, body_cb, &ctx)
  - [x] RK-18b: icn_drive E_TO_BY → bb_broker(icn_bb_to_by, BB_PUMP, body_cb, &ctx)
  - [x] RK-18c: icn_drive E_ITERATE → bb_broker(icn_bb_iterate, BB_PUMP, body_cb, &ctx)
  - [x] RK-18d: add icn_bb_smartmatch Byrd box in icon_gen.c; given/when uses it
  - [x] RK-18e: gate: smoke PASS=5, rungs PASS=14+, broker PASS=31
  Gate: all gates green after Byrd box refactor.

- [x] **RK-19** — Typed variables: `my Int $x`, `my Str $s`.
  Added 6 grammar rules to raku.y: typed scalar/array/hash with and without initialiser.
  Type annotation (IDENT token) consumed and free()'d at parse time — no IR change needed.
  raku.tab.c regenerated. Gate: rk_typed_vars PASS, test_raku_ir_rungs PASS=16 FAIL=0.

- [x] **RK-20** — `unless`, `until`, `repeat/until`.
  Added KW_UNLESS/KW_UNTIL/KW_REPEAT tokens to raku.l and raku.y.
  unless → E_IF(E_NOT(cond), body); until → E_UNTIL(cond, body);
  repeat → E_REPEAT(body) grammar wired (runtime test deferred — needs 'last').
  Gate: rk_unless_until PASS, test_raku_ir_rungs PASS=17 FAIL=0.

- [x] **RK-21** — `gather { take $_ for @list }` end-to-end.
  gather → anonymous proc __gather_N registered in icn_proc_table.
  E_ITERATE(E_FNC_call) in icn_eval_gen → icn_bb_suspend via icn_gather_trampoline
  (proc stored in ss->gather_proc, bypassing icn_coro_stage staging race).
  E_EVERY saves caller_depth before pump; body runs at caller_depth so
  E_VAR reads hit caller frame, not suspended coroutine frame.
  raku.tab.c/raku.lex.c regenerated. rk_gather.raku/.expected replaced with
  real gather/take test. Gate: PASS=17 smoke PASS=5 broker PASS=36. HEAD 915680ce.

- [x] **RK-22** — String ops: `substr`, `index`, `rindex`, `uc`, `lc`, `trim`, `chars`/`length`.
  Implemented in interp.c E_FNC dispatch block (same site as arr_get/hash_get).
  All ops use correct Raku semantics (0-based indexing, both-ends trim).
  INDEX/RINDEX written from scratch in C (no APPLY_fn equivalent).
  Gate: rk_str22 PASS, rungs PASS=18 FAIL=0, broker PASS=37. HEAD 08a5ef8a.

- [ ] **RK-23** — Regex basic: `$s ~~ /pattern/`.
  Maps to E_SCAN + pattern IR nodes (shared with SNOBOL4).
  Gate: basic regex match test PASS.

- [ ] **RK-24** — `map`, `grep`, `sort` list ops.
  Higher-order functions using E_FNC + BB_PUMP generators.
  Gate: map/grep/sort test PASS.

- [x] **RK-25** — `try`/`CATCH`/`die` exception handling.
  Lexer: "try","catch"/"CATCH","die" keywords. Grammar: try block and
  try block CATCH block as block-level stmts (no semicolon).
  Interp: g_raku_exception global; raku_die sets it; raku_try fires
  CATCH only when g_raku_exception non-empty (distinguishes real die
  from Icon fall-off-end FAILDESCR).
  Also fixed SN-6 build break: match_pattern_at stub in snobol4_stmt_rt.c.
  Gate: rk_try_catch25 PASS, rungs PASS=21 FAIL=0, broker PASS=40. HEAD 839ef99e.

- [ ] **RK-26** — `class` / `method` / `new` basic OO.
  Raku OO maps to E_RECORD (class def) + E_FIELD (method call).
  Gate: basic class test PASS.

- [ ] **RK-27** — Write `scripts/test_raku_ir_full_suite.sh`.
  Runs all RK-1 through RK-26 tests. Gate: all PASS.

### Phase 2 — SM-run (BB_PUMP, x86)

- [ ] **RK-28** — rk_hello through rk_vars under --sm-run.
  Gate: PASS=12.

- [ ] **RK-29** — RK-16 through RK-24 under --sm-run.
  Fix sm_lower.c gaps as needed.
  Gate: all rungs passing under --ir-run also pass under --sm-run.

### Phase 3 — JIT-run (x86 in-memory)

- [ ] **RK-30** — rk_hello through rk_vars under --jit-run.
  Gate: PASS=12.

- [ ] **RK-31** — RK-16 through RK-24 under --jit-run.
  Gate: all diffs vs --sm-run empty.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/raku/raku.y` | Bison grammar |
| `src/frontend/raku/raku.l` | Flex lexer |
| `src/frontend/raku/raku_driver.c` | `raku_compile()` entry point |
| `src/frontend/icon/icon_gen.c` | Generator boxes — shared with Raku |
| `src/runtime/interp/icn_runtime.c` | Frame stack — shared with Raku |
| `scripts/test_raku_ir_rungs.sh` | Full rung sweep |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Never modify icn_proc_table layout — Icon shares it.
- Share generator boxes with Icon session — write once in icon_gen.c.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-15, one4all HEAD — post RK-25)

RK-1 through RK-25 done. PASS=21 --ir-run, broker PASS=40. HEAD 839ef99e.
RK-26 next: class/method/new basic OO — E_RECORD (class def) + E_FIELD (method call).

Session RK-22..RK-25 summary:
  RK-22: substr/index/rindex/uc/lc/trim/chars string ops
  RK-23: $s ~~ /pattern/ regex match (context-sensitive / lexing)
  RK-24: map/grep/sort list ops (closure rule, $_ frame-slot binding,
          INTVAL elem coercion, grep truthy=!IS_FAIL)
  RK-25: try/CATCH/die (g_raku_exception distinguishes die from fall-off-end)
  Also fixed SN-6 build break: match_pattern_at stub in snobol4_stmt_rt.c

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

