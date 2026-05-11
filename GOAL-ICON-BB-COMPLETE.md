# GOAL-ICON-BB-COMPLETE.md — All Icon Byrd-Box constructs in modes 1/2/3 (then 4)

**Repo:** one4all + .github
**Sister docs:** `GOAL-CHUNKS.md`, `GOAL-CHUNKS-STEP17.md`, `GOAL-LANG-ICON.md`
**Carved:** 2026-05-10

**Done when:**
1. Every AST kind reachable from a `--ir-run` PASS Icon program lowers via `lower.c` to pure SM — no `emit_push_expr + SM_BB_PUMP` legacy fallthrough fires. Legacy block physically deleted.
2. `--ir-emit` byte-identical to pre-rung baseline for every corpus program.
3. `SCRIP_NO_AST_WALK=1 ./scrip --sm-run` == `./scrip --ir-run` for every program in the `--ir-run` PASS set (the *honest* gate).
4. Every SM opcode emitted by Icon lowering has a `sm_codegen_x64` mirror.
5. `is_suspendable` / `coro_eval` not reachable from SM dispatch under `SCRIP_NO_AST_WALK=1`.

⛔ **"Cheating":** `--sm-run` silently calls `coro_eval` for un-migrated kinds. `SCRIP_NO_AST_WALK=1` aborts on this. Output equality alone is not sufficient.

---

## Architecture

```
.icn → icon_parse() → AST_t*
  --ir-emit  → ir_print_program()                        Mode 1
  --ir-run   → execute_program() → interp_eval()         Mode 2  (AST walker)
  --sm-run   → lower() → SM_Program → sm_interp_run()   Mode 3
  --jit-run  → lower() → sm_codegen_x64() → run         Mode 3.5
  --jit-emit → lower() → sm_codegen_x64() → binary      Mode 4
```

Proebsting four-port template (start/resume/succeed/fail) → `SM_SUSPEND_VALUE` + goto wiring.
JCON gold: `/home/claude/jcon-extract/jcon-master/tran/irgen.icn` (69 `ir_a_<Construct>` procedures).

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/build_spitbol_oracle.sh
```

Baseline gates (all green before picking up next rung):
```bash
bash scripts/test_smoke_icon.sh                 # PASS=5
bash scripts/test_smoke_unified_broker.sh       # PASS=49
bash scripts/test_isolation_ir_sm.sh            # PASS
bash scripts/test_icon_ir_all_rungs.sh          # 185/48/30
bash scripts/test_icon_sm_no_ast_walk.sh        # honest dial (194/45/1 at sess 2026-05-11)
```

---

## Honest-mode-3 protocol

Probe helpers live in `scripts/icon_bb_probes.sh`:
- `bb_probe_detect` / `bb_probe_detect_anchor` — is the rung needed?
- `bb_probe_complete` / `bb_probe_complete_anchor` — checks output + honest + audit + smokes
- `bb_probe_scoreboard` — FLIPPED/REGRESSED/STILL-PASS/STILL-FAIL
- Regression tripwire: smoke ×6 + broker md5 diff vs `baselines/icon-bb/smoke-*.md5`
- Bisection: `scripts/icon_bb_bisect.sh`

A rung is **honestly complete** iff: (a) output matches `--ir-run`, (b) passes under `SCRIP_NO_AST_WALK=1`, (c) audit counter zero for kind, (d) smokes unchanged, (e) ≥1 program flipped honest.

---

## Phase A — drain legacy fallthrough

Six kinds at `lower.c` legacy block emit `emit_push_expr + SM_BB_PUMP`:
`AST_BANG_BINARY`, `AST_LIMIT`, `AST_RANDOM`, `AST_SECTION`, `AST_SECTION_MINUS`, `AST_SECTION_PLUS`, plus generative `AST_LCONCAT` variant.

#### A1 — CH-17i-bang-concat-gen — `AST_BANG_BINARY` + `AST_LCONCAT` (generative)
- [ ] JCON: `ir_a_Binop` with closure. Reuse `icn_bang_binary_state_t` / `icn_binop_gen_state_t`.
- [ ] Anchor: `rung15_real_swap_lconcat.icn` (sm-run gives stack underflow today)
- [ ] Files: `sm_prog.h/c`, `sm_interp.h/c`, `sm_codegen.c`, `lower.c`
- [ ] Gate: smoke ×6, isolation PASS, rung15 flips FAIL→PASS honest
- [ ] Doc: `docs/CHUNKS-icon-bb-bang-concat-gen-validation.md`

#### A2 — CH-17i-section — `AST_SECTION*`
- [ ] JCON: `ir_a_Sectionop`. State: `icn_section_state_t { subj, lo, hi, kind }`.
- [ ] Anchor: TBD (gen subscript in section). Gate: standard + anchor honest.

#### A3 — CH-17i-limit-random — `AST_LIMIT` + `AST_RANDOM`
- [ ] JCON: `ir_a_Limitation`. Random: one-shot α, re-randomize β.
- [ ] Anchor: TBD (`every write(seq() \ 5)`, `?L`). Gate: standard + anchor.

#### A4 — CH-17i-iterate — `AST_ITERATE` (`!E`)
- [ ] JCON: `ir_a_Unop` with closure. Existing: `icn_bb_iterate`.
- [ ] Anchor: TBD (`every write(!list)`). Gate: standard + anchor.

#### A5 — CH-17i-seqexpr-gen — `AST_SEQ_EXPR` (generative `;`-parens)
- [ ] JCON: `ir_conjunction`. State: `icn_seq_expr_state_t`.
- [ ] Anchor: TBD. Gate: standard + anchor.

#### A6 — CH-17i-fallthrough-delete
- [ ] After A1–A5: delete legacy block, replace with `abort()` + message.
- [ ] Gate: zero `SM_PUSH_EXPR` fires corpus-wide in `--sm-run` and `--jit-run`.

---

## Phase B — generative reductions

Scalar ops become generators when `is_suspendable(child)`. Extend scalar arms in `lower.c`; no new opcodes (use existing `SM_SUSPEND_VALUE` + goto wiring).

- [ ] **B1** CH-17i-arith-gen — `AST_ADD/SUB/MUL/DIV/MOD/…` gen children. Anchor: `every write((1 to 3) + (1 to 2))`
- [ ] **B2** CH-17i-rel-gen — relops gen children. Anchor: `every write(2 < (1 to 4))`
- [ ] **B3** CH-17i-cat-gen — `AST_CAT`/`AST_LCONCAT` mixed. Anchor: `every write("v=" || (1 to 3))`
- [ ] **B4** CH-17i-deref-gen — `AST_NONNULL`/`AST_NULL`/`AST_IDENTICAL` gen. Anchor: `every write(\(1 | &null | 3))`
- [ ] **B5** CH-17i-idx-gen — `AST_IDX` gen index. Anchor: `every write(s[1 to 3])`
- [ ] **B6** CH-17i-assign-gen — `AST_ASSIGN` gen RHS + `AST_REVASSIGN`/`AST_REVSWAP`. Anchor: `every x := (1 to 3); write(x)`

---

## Phase C — control-flow generator-awareness

- [ ] **C1** CH-17i-fnc-gen — `AST_FNC` gen arg / user proc with `suspend`. Anchor: `every write(seq())`
- [ ] **C2** CH-17i-loop-cond-gen — `while/until/repeat` gen condition. Anchor: `while (i := find("x",s)) do …`
- [ ] **C3** CH-17i-if-gen — `AST_IF` gen condition (Proebsting §4.5). Anchor: `every write(if 1=1 then (1 to 3) else 0)`
- [ ] **C4** CH-17i-not-gen — `AST_NOT` gen subexpr. Anchor: `every write(not (1=2 | 1=3))`

---

## Phase D/E (owned by CHUNKS-STEP17)

| Rung | Prereqs |
|------|---------|
| CH-17g-irrun-prep — `_usercall_hook` Icon-builtin dispatch | after Phase C |
| CH-17g-irrun-execution — route `--ir-run` non-SNO through `sm_preamble+sm_run_with_recovery` | after prep |
| CH-17i-mode3-completeness / mode4-icon-prolog / final-isolation | after Phases A–D |

---

## Active next targets (honest dial: 194/45/1 at sess 2026-05-11)

Remaining honest fails rungs 01–35:

| Program | Symptom | Root cause |
|---------|---------|------------|
| `rung02_proc_locals` | local `total` reads 0 in `every` body | `sm_call_proc` doesn't patch AST_VAR ival → fix in progress |
| `rung06_cset_any_fail` | `any()` returns 1 not 0 (inverted) | scan context / `any()` fail case |
| `rung11_bang_augconcat_bang_concat` | `every result ||:= !s` empty output | augop + generator RHS |
| `rung13_alt_alt_filter` | `every (x:=…)>2 & write(x)` empty | conjunction in `every` body; needs CH-17g-irrun-execution |
| `rung23_table_table_key` | `key(t)` returns 0 | `key()` generator not wired |
| `rung24_records_record_loop` | `every c.n := 1 to 3` writes 0s | record field assign + gen RHS |

---

## Invariants

1. Mode 1 (`--ir-emit`) byte-identical at every rung.
2. Icon `--ir-run` corpus 185/48/30 byte-identical until CH-17g-irrun-execution lands.
3. No `EXPR_t*` in SM bytecode — BB-pump opcodes take integer registry IDs.
4. Fallthrough delete (A6) is one-way: future generative kinds must add their own lowering.
5. `is_suspendable` stays in sync with lowering rungs.

---

## Closed rungs

| Rung | Commit | Honest gain | Notes |
|------|--------|-------------|-------|
| A0 — CH-17i-cheat-tripwire | — | — | `SCRIP_NO_AST_WALK=1` guard in `coro_eval`/`interp_eval`/etc. |
| A3-seed-fix | — | 116→117 | Unified 3 LCG seeds → `bb_icn_rnd_seed` in `coro_value.c` |
| A4 — CH-17i-alternate | — | 117→122 | `AST_ALTERNATE` → `SM_BB_PUMP_AST`; value-context assign works |
| CH-17g-smcall-proc | `60656fce`/`e0d7e4f5` | 126→130 | `SM_CALL_FN` scans `proc_table` before NV dispatch; trampoline guard |
| CH-17g-augop-inline | `bb6d4ee7` | 130→140 | `AST_AUGOP` inline read-compute-writeback for frame/NV vars |
| CH-17g-loop-stack | `864fe914` | 140→143 | `SM_VOID_POP` before `SM_PUSH_NULL` at while/until exit |
| CH-17g-scan | `d8760856` | 143→152 | `AST_CSET`→string; `AST_SCAN`→`ICN_SCAN_PUSH/POP`; scan builtins |
| CH-17g-builtin-batch | `c95eb2bd` | 141→167 | `SIZE/NONNULL/NULL/FIELD_GET/SET/MAKELIST/RECORD_MAKE/insert/delete/member/key/push/put/get/pull/sort/sortf`; `AST_ASSIGN` IDX+FIELD LHS; `subscript_set` DT_DATA |
| CH-17g-case-swap-null | `7adfdc20` | 167→174 | `AST_CASE` pair-layout; `AST_SWAP` inline; `AST_NULL` (`/E`) |
| AST_IF condition leak | `2f3dbc65` | 174→177 | `SM_VOID_POP` after `SM_JUMP_F` drains stale condition value |
| CH-17g-scan-subject | `5f6d9d8b` | 180→185 | `NV_GET/SET_fn` for `&subject`/`&pos` via `scan_subj`/`scan_pos` |
| CH-17g-icon-conjunction | `74faf1d0` | — | `AST_SEQ` + `LANG_ICN` → goal-directed conjunction via `SM_JUMP_F` |
| CH-17g-initial-once | `b4d7ee18` | 172→175 | `initial {}` sentinel via NV `__initial_<ptr>__`; vars excluded from frame scope |

---

## File ownership

| Path | Touches? |
|------|----------|
| `src/runtime/x86/lower.c` | Yes (every rung) |
| `src/runtime/x86/sm_prog.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_interp.h/c` | Yes (Phase A) |
| `src/runtime/x86/sm_codegen.c` | Yes (Phase A JIT mirrors) |
| `src/runtime/interp/coro_runtime.c` | Fixes (sm_call_proc etc.) |
| `src/runtime/interp/coro_runtime.h` | Fixes (IcnProcEntry) |
| `src/runtime/interp/interp_eval.c` | Builtin additions |
| `docs/CHUNKS-icon-bb-*-validation.md` | Per rung |
