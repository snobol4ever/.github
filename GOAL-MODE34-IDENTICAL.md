<!-- GOAL-MODE34-IDENTICAL · mode-3 (--run, x86 BINARY) ≡ mode-4 (--compile, x86 TEXT), strictly 1:1 corresponding -->

# ▶▶▶ NEXT SESSION — START HERE (created 2026-06-25, Lon directive)

**MANDATE.** SCRIP has EXACTLY TWO execution modes and they MUST be 1:1 corresponding:
- **mode 3 = `--run`** — x86 BINARY assembled in-process into a sealed RX slab, jumped into.
- **mode 4 = `--compile`** — x86 TEXT (GAS `.s`) to stdout, assembled by `as`/`gcc`, linked against `libscrip_rt.so`.

The two modes share ONE emitter (the `bb_*`/`xa_*` templates) and MUST share ONE driver setup. For the SAME source → SAME IR → SAME logical instruction sequence; the ONLY permitted difference is the LEAF materialization inside `x86(...)`: bytes for BINARY, GAS text for TEXT. Any place where mode-3 and mode-4 produce a DIFFERENT instruction stream — a different code PATH, a missing fast path on one side, a different runtime call, a different operand source — is a **DEFECT to be driven to zero (99.999% identity)**. "Same output" is necessary but NOT sufficient: two engines can print the same bytes via different code; this rung targets the CODE, then the output.

**MODES 1 AND 2 DO NOT EXIST.** Mode 1 (the AST-walk `eval_node` evaluator) and mode 2 (`--run`, the IR-graph software interpreter) are DELETED. The driver already exposes only `--run`/`--compile` (verified 2026-06-25 — no `--run` flag remains). What survives is RESIDUE: stale strings/comments in live code, dead `src/attic/` files, and stale prose in authoritative docs. All references on LIVE/authoritative surfaces must be purged. **Scope guard:** archival HANDOFF/SESSION records are history, NOT live descriptions — they are NOT rewritten (rewriting them would falsify the record and violates the "don't touch unrelated goal files" rule). Target only surfaces a reader consults to understand SCRIP *today*.

---

## CONFIRMED DIVERGENCES (grounded — session 2026-06-25, with the live binary)

- **D1 — GVA is mode-4-ONLY for SNOBOL4 (the headline defect).** Mode-4 SNOBOL4 emits `__gva` + `gva_register` and accesses globals via `[rbx+k*16]` (zero hash calls). Mode-3 SNOBOL4 (`src/driver/scrip.c` SNOBOL4 `--run` block, ~3322–3389) NEVER calls `gva_register` nor sets `g_gva_active`, so every global read/write silently falls back to `NV_GET_fn`/`NV_SET_fn` by-name hashing. Output matches; the instruction stream does NOT; mode-3 is ~7–8× slower (goal-file timings: arith_loop 862 ms mode-3 vs 113 ms mode-4). **Prolog and Icon mode-3 ALREADY set up GVA** in-process (`pl_gva_arena = GC_MALLOC(...)` + `gva_register` + `m3_enter_with_rbx`, ~3306–3315) — SNOBOL4 mode-3 is the lone hold-out. The fix pattern already exists in the same file.

- **D2 — The driver runs TWO separate, drifting setup blocks.** `mode_compile_x86` (TEXT, ~2678–3163) and `mode_run` (BINARY, ~3169–3400) each independently do proc registration, global collection, preamble construction, and per-language dispatch. They are parallel but NOT identical (D1 is one symptom). Duplicated setup is the ROOT CAUSE: a fast path added to one block is invisible to the other. Structural cure = ONE shared setup, parameterized only by emission medium.

- **D3 — DCR-2 is mid-flight and currently mode-4-only.** The function-call direct-dispatch optimization (`__proc[]` index table + `rt_call_proc_direct`) has its TEXT arm landed in `bb_call.cpp` and the driver wiring NOT yet done; `g_proc_direct_active` is never set, so it is presently DORMANT in both modes (behavior-neutral, build-verified). When activated it MUST be both-medium (mode-3 binary arm + mode-3 driver activation), or it becomes a fresh D1-class divergence. This rung GOVERNS DCR-2's completion.

- **D4 — The crosscheck gate is mode-4 ONLY.** `scripts/test_crosscheck_snobol4.sh` header: "MODE-4 ONLY (Lon directive 2026-06-06)". That directive is SUPERSEDED by this rung: gates must exercise BOTH modes and assert mode-3 output == mode-4 output == `.ref`. Until then, mode-3 regressions are invisible.

- **D5 — Mode-3 coverage gaps are unmeasured.** Mode-3 soft-falls ("[SBB] mode-3: statement shape not yet flat-emittable") on shapes mode-4 may handle. The set of programs mode-4 compiles but mode-3 cannot is unknown and must be enumerated (it is a divergence class).

---

## BASELINE CENSUS (M34-0 RUN — crosscheck corpus, 262 programs, 2026-06-25)

`scripts/test_mode34_parity.sh` landed and run over `/home/claude/corpus/crosscheck`:

**TOTAL=262 · IDENTICAL=191 · DIFFER=1 · M3-MISS=63 · M4-MISS=1 · BOTH-FAIL=6**

- **DIFFER=1 → `library/test_string`** (the priority bug — same program, different output per mode). Concretely: mode-3 prints 2 lines then **ABORTS** with `bb_scan: mode-3 non-literal pattern needs native PB-RB graph (rt_scan deleted — IR interpreter gone)` — a native-pattern hole left by the mode-2 excision that mode-3 never backfilled. mode-4 runs to completion but is **wrong** (`ltrim/rtrim/trimws` don't trim, `contains` FAILs). Both broken, differently. (Oracle `sbl -b` confirms the expected trimmed output.)
- **M3-MISS=63** — mode-4 compiles+runs, mode-3 soft-falls/empty. Dominated by native-pattern shapes: `*_pat_fence_*`, `*_pat_arbno_*`, `*_pat_calc_*`, `*_pat_json_*`, `W03/W04_*`, `word1..4`, `wordcount`, `cross`, `1017_arg_local`, `1018_apply`. These are the mode-3 BINARY-arm gaps (D5).
- **M4-MISS=1 → `expr_eval`** — mode-4 fails to compile, mode-3 runs. (mode-4 codegen gap.)
- **BOTH-FAIL=6** — `coverage_sno_nodes`, `064/065/106_pat_fence_*`, `071_builtin_ucase`, `072_builtin_lcase`.

The 191 IDENTICAL prove the shared-template design works where both arms exist; the 71 non-identical are the rung's worklist. Re-run the harness after every step; IDENTICAL must monotonically rise, DIFFER must hit 0 first.

## STEPS

### M34-0 — Parity harness + baseline census ✅ HARNESS LANDED + RUN (2026-06-25)
- [x] **M34-0a — `scripts/test_mode34_parity.sh`** — classifies every program IDENTICAL / DIFFER / M3-MISS / M4-MISS / BOTH-FAIL; `--tsv` census; exit nonzero on any DIFFER. DONE.
- [x] **M34-0b — baseline census run** over crosscheck (numbers above). NEXT: also run over benchmark + feature corpora and commit `docs/MODE34-PARITY-CENSUS-<date>.tsv`.

### M34-0-archived — (original measurement step, superseded by the run above)
- [ ] **M34-0a — `scripts/test_mode34_parity.sh`.** For each program in a corpus, run `--run` (mode 3) AND `--compile`→`as`→`gcc`→run (mode 4); capture both stdouts + exit status. Classify each program: `IDENTICAL` (3==4==ref), `DIFFER` (3≠4), `M3-MISS` (mode-3 soft-fall/empty while mode-4 produces output), `M4-MISS`, `BOTH-FAIL`. Emit a TSV census + summary counts. `timeout 8s` smoke / `timeout 30s` corpus. NO source change.
- [ ] **M34-0b — run the census over the SNOBOL4 crosscheck + benchmark + feature corpora.** Commit the TSV as `docs/MODE34-PARITY-CENSUS-<date>.tsv`. This is the ground-truth divergence list every later step closes against. Record the headline counts in this goal file's watermark.

### M34-1 — Purge mode-1/mode-2 from authoritative surfaces
- [ ] **M34-1a — live code (one site).** `src/runtime/runtime_eval.c:139` BOMB string says "(mode-1 era)" — reword to drop the dead-mode reference while keeping the message meaning ("AST-walk evaluator deleted; nothing interprets tree_t at runtime"). Grep-confirm zero live-code `mode-1`/`mode-2`/`--run`/`IR_interp`/`mode_interp` outside `src/attic/`.
- [ ] **M34-1b — authoritative docs.** Update the mode tables/prose in `PLAN.md` (architecture paragraph "mode-2 INTERP (`interp/IR_interp.c`…)"), `REPO-SCRIP.md` (the `scrip modes` table lists `--run` mode 2 — remove the row), `ARCH-SCRIP.md`, `SCRIP/README.md`, and the driver help/comments to describe ONLY modes 3 and 4. Do NOT touch HANDOFF-*/SESSION-* archival records.
- [ ] **M34-1c — dead interpreter files.** Inventory `src/attic/driver/interp_*.{c,h}` and `src/attic/interp/`. If the Makefile does not compile them (confirm), either physically delete (preferred, per the user's directive) or leave with a one-line "DEAD — mode-2 excised" banner. Gate: `make scrip` clean after; no symbol regressions.

### M34-2 — Close D1: SNOBOL4 mode-3 GVA parity (the highest-value single fix)
- [ ] **M34-2a — mirror the Prolog/Icon mode-3 GVA setup into the SNOBOL4 `--run` block.** In `src/driver/scrip.c` SNOBOL4 mode-3 path: run `gva_collect_reset()` + `gva_collect_graph(sbbg)`; if `n_gva>0`, `GC_MALLOC` the cells arena + names array, `gva_register(...)`, `g_gva_active=1`, and enter via `m3_enter_with_rbx(fn, rt_frame(), 0, gva_arena)` instead of `fn(rt_frame(),0)`. Mirror exactly the Prolog block (~3306–3315) — same arena lifetime, same rbx contract (`bb_regs.h`: `rbx=GVA base`).
- [ ] **M34-2b — gate.** mode-3 `arith_loop.s`-equivalent now takes `[rbx+k*16]`; M34-0 census shows the SNOBOL4 globals programs flip `DIFFER`(code)→`IDENTICAL`(code+output). Crosscheck (BOTH modes, M34-6) byte-identical. A/B: mode-3 arith_loop should collapse toward the mode-4 time (the ~7–8× gap is the GVA gap).

### M34-3 — Close D3: finish DCR-2 both-medium under this rung
- [ ] **M34-3a — mode-4 driver wiring.** In the SNOBOL4 mode-4 block: after `gva` emission, `proc_collect_reset()` + `proc_collect_graph(sbbg)`; if `proc_slot_count()>0`, emit `.bss __proc: .space n*8` + `.rodata __proc_names` (name strings + quad table) + preamble `lea rdi,__proc_names; lea rsi,__proc; mov edx,n; call rt_proc_table_fill@PLT` (placed AFTER `gva_register` — procs must be registered first by `proc_startup`). Set `g_proc_direct_active=1` around `gvar_flat_chain_build_text`.
- [ ] **M34-3b — mode-3 binary arm + driver activation.** Add the BINARY arm to `bb_call_gvar_userproc_str` (bake `mov edi, idx` via `rt_proc_index_of(fn)` at emit time — valid because the mode-3 driver registers all procs before chain build — then `x86_call_ro("rt_call_proc_direct", &rt_call_proc_direct)`). In the SNOBOL4 mode-3 block set `g_proc_direct_active=1` (no `.bss` table; the binary arm bakes the index immediate).
- [ ] **M34-3c — gate.** Crosscheck BOTH modes byte-identical to pristine HEAD fail-set (PASS=171 FAIL=84 SKIP=6, zero regressions). M34-0 census: func_call/fibonacci/roman `IDENTICAL` in both modes. A/B mode-4 func_call/fibonacci vs HEAD (the DCR-2 delta), AND mode-3 func_call/fibonacci vs HEAD (the binary arm delta). Re-ground 3-way (oracle `x64`, token-free).

### M34-4 — Close D2: unify the driver setup (the structural guarantee)
- [ ] **M34-4a — extract ONE shared setup.** Factor the per-language setup (proc registration, `gva_collect`, `proc_collect`, preamble plan) out of the two mode blocks into a single routine that returns a setup descriptor; the two blocks then differ ONLY in the emission leaf (binary slab vs text `.s`) and the entry (`m3_enter_with_rbx`/in-process call vs `main:` + `call flat_α`). After this, a fast path added once is visible to BOTH modes by construction — D1-class drift becomes structurally impossible.
- [ ] **M34-4b — gate.** Full M34-0 census unchanged-or-better; crosscheck BOTH modes byte-identical; all language gates green (SNOBOL4 first; Icon/Prolog/Pascal/Raku must not regress).

### M34-5 — Close D5: mode-3 coverage parity
- [ ] **M34-5a — enumerate M3-MISS.** From the M34-0 census, list every program mode-4 compiles but mode-3 soft-falls. Triage each shape's missing BINARY arm (a template whose `MEDIUM_BINARY` path is absent/bombs).
- [ ] **M34-5b — fill the missing binary arms** shape-by-shape until M3-MISS == 0 for the SNOBOL4 corpus. Each fix is a both-medium template completion; gate per shape.

### M34-6 — All gates run BOTH modes (the standing requirement)
- [ ] **M34-6a — crosscheck.** Rewrite `test_crosscheck_snobol4.sh` to run mode-3 AND mode-4 for every program and assert `m3==m4==ref`. Retire the "MODE-4 ONLY" header. A `DIFFER` is a hard FAIL.
- [ ] **M34-6b — benchmark/feature/regression + per-language gates.** Apply the same both-mode assertion to `test_bench_snobol4_modes.sh` (confirm it truly runs both), the feature/demo `.s` regen flows, and the Icon/Prolog/Pascal/Raku gates. Every "rung gate" in every goal file inherits the both-mode requirement.
- [ ] **M34-6c — parity in CI of the harness itself.** `test_mode34_parity.sh` becomes a first-class gate invoked by the handoff sequence whenever codegen is touched.

### M34-7 — Template-level 1:1 audit (defense in depth)
- [ ] **M34-7a — both-arm presence audit.** For every `bb_*.cpp`/`xa_*.cpp`, confirm BOTH a BINARY and a TEXT arm exist and correspond instruction-for-instruction (no arm that emits a different op sequence). Reuse/extend the existing BOTH-MEDIUM gate scripts (`test_gate_template_medium_invisible.sh --strict`, the `MEDIUM_*`-in-templates greps from RULES.md). Any template emitting via raw bytes outside `x86_asm.h`, or gating output on `MEDIUM_*`, is a violation already forbidden — this step proves zero across the tree.
- [ ] **M34-7b — encoder coverage.** Every `x86("…")` mnemonic used by a template must have BOTH a binary encoder (in `x86_asm.h`) and a text form, so neither medium silently drops an instruction. Enumerate mnemonics; assert both forms exist.

---

## GATE PHILOSOPHY (applies to every step)
1. **Code parity before output parity.** A step is not done because outputs match — it is done when the mode-3 and mode-4 instruction streams correspond for the targeted shape AND outputs match.
2. **Both modes, every gate.** No gate may run a single mode. `m3==m4==ref` or FAIL.
3. **Oracle-grounded.** `x64` SPITBOL (`/home/claude/x64/bin/sbl -b`, token-free) is the semantic oracle for SNOBOL4/Snocone. Re-ground perf claims against it; do not assert speedups from SCRIP-vs-SCRIP alone.
4. **No regression.** Crosscheck fail-SET stays byte-identical to pristine HEAD across the whole rung (currently PASS=171 FAIL=84 SKIP=6).

## Prereq reads (BB-CODEGEN design set — NON-NEGOTIABLE for any step touching emission)
`ARCH-x86.md` §"Boxes are stackless" + §"Flat-BB ABI"; `ARCH-ICON.md` §"register contract"; `REGISTER-LAYOUT.md`; `src/emitter/bb_regs.h` (r12=ζ, r13=Σ, r14=δ, r15=Δ, rbx=GVA base, rbp=GST hash); `src/emitter/XA_templates/xa_flat.cpp` (glob preamble); `ARCH-SCRIP.md`. Plus, for the driver work: `src/driver/scrip.c` mode_compile_x86 + mode_run blocks side by side.

## Build / probe
`apt-get install -y libgc-dev && make -j4 scrip && make libscrip_rt`. Tri-probe a program in BOTH modes:
`./scrip --run p.sno` vs `./scrip --compile p.sno > p.s; gcc -no-pie p.s -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs oracle `/home/claude/x64/bin/sbl -b p.sno`.
