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
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh              # PASS=5
bash /home/claude/one4all/scripts/test_raku_ir_rungs.sh           # PASS=12
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh    # PASS=31
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

- [ ] **RK-16** — `for @arr -> $x` real array iteration.
  E_EVERY + E_BANG on list/array. Add `icn_bb_bang` to icon_gen.c (also
  needed by Icon IC-18 — write once, both sessions benefit).
  Gate: for-array test PASS under --ir-run.
  Test: `scripts/test_raku_ir_rung_16_for_array.sh`.

- [ ] **RK-17** — Hash `%h<key>` and `%h{$k}` full support.
  RK-15 added hash basics. This rung: `keys %h`, `values %h`, `pairs %h`,
  `exists %h<k>`, `delete %h<k>`.
  Gate: hash test suite PASS.

- [ ] **RK-18** — `given/when` (Raku switch).
  Maps to E_CASE → BB_PUMP chain.
  Gate: given/when test PASS.

- [ ] **RK-19** — Typed variables: `my Int $x`, `my Str $s`.
  Type annotations parsed and stored in E_VART; runtime ignores type
  (no type enforcement yet — just parse clean).
  Gate: typed var programs parse and run correctly.

- [ ] **RK-20** — `unless`, `until`, `repeat/until`.
  Maps to E_UNTIL, E_REPEAT already in interp_eval (shared with Icon).
  Gate: unless/until test PASS.

- [ ] **RK-21** — `gather { take $_ for @list }` end-to-end.
  gather → E_SUSPEND box (coroutine). take → suspend with value.
  for → E_EVERY + E_BANG. Full polyglot .scrip test.
  Gate: raku_gather.scrip PASS under --ir-run.

- [ ] **RK-22** — String ops: `substr`, `index`, `rindex`, `uc`, `lc`, `trim`.
  Wire to existing SNOBOL4 builtins or write Raku-specific wrappers.
  Gate: string rung PASS.

- [ ] **RK-23** — Regex basic: `$s ~~ /pattern/`.
  Maps to E_SCAN + pattern IR nodes (shared with SNOBOL4).
  Gate: basic regex match test PASS.

- [ ] **RK-24** — `map`, `grep`, `sort` list ops.
  Higher-order functions using E_FNC + BB_PUMP generators.
  Gate: map/grep/sort test PASS.

- [ ] **RK-25** — `do`/`try`/`CATCH` exception handling.
  Maps to E_CHOICE (try) + E_CUT (on success). Basic throw/catch.
  Gate: try/catch test PASS.

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

## Current state (2026-04-14, one4all HEAD 43dc03da)

RK-1 through RK-15 done. PASS=12 --ir-run.
RK-16 next: for @arr -> $x real array iteration.
RK-16 shares icn_bb_bang with GOAL-LANG-ICON IC-18 — coordinate.
