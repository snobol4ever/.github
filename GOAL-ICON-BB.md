# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

**Reset:** 2026-05-28. All Icon legacy SM dispatch deleted. No env-gate `SCRIP_ICN_BB`. The BB-graph lowering is the only path. Every BB template MEDIUM_BINARY arm that isn't real ABORTs loudly at a named site.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7 · Claude Sonnet 4.6
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/jcon_irgen.icn`.

---

## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.**

- Mode 2: driver detects Icon and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. Icon SM stream is empty.
- Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in mode-4.

Per `test_icon.c`: every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels wired by flat `goto`. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes emitted for an Icon program.** No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, nothing. Driver calls `bb_exec_once(main_bb_graph)` directly.

Completion tests:
```bash
./scrip --dump-sm any_icon_program.icn        # ; SM_sequence_t  count=0
./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'   # 0
```

---

## Current state (2026-05-29, IBB-7 closed, one4all `d1c55b0c`)

| Mode | Path | Canonical-5 | Full corpus (m2-OK filter, 250) |
|------|------|-------------|---------------------------------|
| 2 (`--interp`) | `bb_exec_once` C tree-walker | **5 / 5** | 200 / 283 |
| 3 (`--run`) | `bb_build_flat` → seal RX → call slab | **5 / 5** | **17 PASS / 45 FAIL / 186 ABORT / 2 SEGV** |
| 4 (`--compile`) | deferred per Lon directive | hello.icn ✅ (`f387a7b9`) | n/a |

Canonical-5: `hello.icn`, `add.icn`, `every_to.icn`, `alt.icn`, `full.icn`. All byte-identical m2 vs m3.

Mode-3 corpus delta IBB-6 → IBB-7: **+4 PASS** (13→17 over a `--run`-clean-baseline rebuild). New PASSes: rung10_augop_augplus, rung10_augop_augstar, rung10_augop_augsub_mod, rung10_augop_break_while. Zero regressions.

ABORT breakdown after IBB-7 (~186):
- `bb_call: unsupported call shape` — non-write fn calls (user-proc dispatch), write(BB_CALL/proc result), write(BB_LIT_S in non-write fn) — main remaining cluster.
- `flat_drive_binop_tree: missing α or β child` — relop in if-condition (~16).
- `flat_drive_every: every-with-do-body` (~4).
- Two new SEGVs: `rung26_pow_pow_expr`, `rung37_augop_pow` — DT_R via `^`, fprintf(`%g`) inside slab. Pre-existing latent stack-alignment issue, exposed by IBB-7 progressing past the prior ABORT site. Both were ABORTing in baseline.

---

## Closed rungs

| Rung | Closed | Test | Commit |
|------|--------|------|--------|
| IBB-0 | Reset | — | — |
| IBB-1 | mode-2 hello | `write("hello")` | reset session |
| IBB-2 | Boot shape decision: zero SM, driver-level bypass | — | — |
| IBB-3 | mode-2 + mode-3 add | `write(1+2)` | `e612d519` |
| IBB-4 | mode-2 + mode-3 every-to | `every write(1 to 3)` | `fac53504` (bin-site reorder) |
| IBB-5 | mode-2 + mode-3 alt | `every write(1\|2\|3)` | `1a97c0a3` (counter-state dispatch) |
| IBB-6 | mode-2 + mode-3 full | `every write(5 > ((1 to 2)*(3 to 4)))` | `3aa200cd` (BINOP_GEN odometer) |
| IBB-7 | write(BB_VAR) + BB_ASSIGN flat-wire (AG-PURE deep-thread aware) | `x := 42; write(x)` byte-identical | `d1c55b0c` |
| IBB-1..32 (mode-2 only) | 22 programs verified zero-SM mode-2 | various | `936b8182` |

Mode-2 verified programs: write_str, arith, every_to/by, alt, conj, if, while, repeat, assign, augop, list-len, bang, idx, idx-gen, section, limit, user-proc, return, fail, table, cset, scan, scan-gens, recursion.

---

## Rungs

### IBB-8 (next) — DT_R fprintf SEGV + remaining mode-3 corpus

Two distinct fronts:

- [ ] **DT_R fprintf SEGV** — 2 corpus cases (`rung26_pow_pow_expr`, `rung37_augop_pow`) + any DT_R write going forward. Symptom: `fprintf(stdout, "%g\n", d.r)` inside `rt_pop_write_any_nl` SEGVs when reached from a slab. Standalone C reproduces fine. Hypothesis: latent x86_64 ABI stack-alignment in `xa_flat` prologue/epilogue — slab entered with rsp%16==8 (from outer `call fn`); template `call rax` chains keep rsp%16==8 at internal call sites, so callee enters at rsp%16==0 (correct). But variadic SSE-using callees (printf %g, %f) appear to fault. Investigate first with a minimal test: empty slab that just calls fprintf("%g", 1.0). If repro, fix in `xa_flat_prologue` (`sub rsp,8` + paired `add rsp,8` in epilogue, before `ret`). Touches all slabs — verify canonical-5 stays byte-identical after the fix.
- [ ] **relop in if-condition** — 16 cases. `flat_drive_binop_tree: missing α or β child` — relop reaches binop_tree with one operand missing in cond context.
- [ ] **every E do body** — 4 cases. `flat_drive_every` with `bb->β` set.
- [ ] **write(BB_CALL)** — user-proc result → vstack → write trailer. Requires BB_CALL-as-arg semantics + BB_RETURN flat-wire.
- [ ] **user-proc dispatch (non-write fn calls)** — large remaining cluster. Requires BB_CALL of arbitrary fn name + caller-side rt_call_proc helper.

### IBB-23 (open) — `suspend E`

Top-level `procedure g() suspend 1; suspend 2; end; every write(g())` prints nothing in both mode-2 and legacy. Pre-existing — needs `lower_icn_proc_gen`'s GeneratorState bridge wired through to outer `every` loop.

### IBB-8..34 — remaining (deferred mode-3 + mode-4)

Strings, to-by, conj, if, while, until/repeat, assign, augop, list, bang, idx, idx-gen, section, limit, user-call, suspend, return, fail, tables, sets, records, csets, scan, scan-prims, scan-gens, co-expressions, JCON ir_a_* sweep.

---

## Mode-3 abort map (canonical-5)

| Test | State |
|------|-------|
| hello.icn  | ✅ `6393c743` |
| add.icn    | ✅ `e612d519` |
| every_to.icn | ✅ `fac53504` |
| alt.icn    | ✅ `1a97c0a3` |
| full.icn   | ✅ `3aa200cd` |

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp  /tmp/rung_NN.icn  > out_m2.txt
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
diff out_m2.txt out_m3.txt    # must be empty
./scrip --dump-sm /tmp/rung_NN.icn  # ; SM_sequence_t  count=0

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# Smokes (must hold)
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md`.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## Watermark

Programs PASS, both modes, byte-identical.

| State | Programs PASS | Notes |
|-------|---------------|-------|
| IBB-6 ✅ | 5/5 canonical (m2 + m3) | `3aa200cd`. BB_BINOP_GEN odometer. |
| IBB-7 ✅ | 5/5 canonical; corpus 13→17 (+4) | `d1c55b0c`. BB_VAR + BB_ASSIGN flat-wire; AG-PURE deep-thread gates (ival==1 / dval==1.0). |
| IBB-8 (next) | TBD | DT_R fprintf SEGV (xa_flat alignment hypothesis) + relop in if + write(BB_CALL) + user-proc dispatch. |
