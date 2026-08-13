<!-- GOAL-MODE34-IDENTICAL · mode-3 (--run, x86 BINARY) ≡ mode-4 (--compile, x86 TEXT), strictly 1:1 corresponding -->

**LIVE CURSOR (Claude Sonnet 4.6, 2026-08-13):** **5b FIXED** (SCRIP `3ed6dc90`). **BugB (`var=subj?pat`) FIXED** (same commit). Both oracle-verified, both modes. Corpus: IDENTICAL 254→263, DIFFER 16→14, M3-MISS 46→39, zero regressions (set-diff verified). Full detail: `FINDING-2026-08-13-CLAUDE-SN4-MODE34-5b-SPAN-VAR-INLINE-ARM-FIX-AND-VAR-ASSIGN-MATCH-BUGB.md`.

**Still open:** M34-3 (DCR-2 both-medium) · M34-4 (driver unify) · M34-5c (LOUD-IN-M4/SILENT-IN-M3 sweep) · 175_pat_bal_generator_retry BAL-generator bug (pre-existing, nondeterministic at HEAD, not this session's work).

---

# MANDATE

SCRIP has EXACTLY TWO execution modes and they MUST be 1:1 corresponding:
- **mode 3 = `--run`** — x86 BINARY assembled in-process into a sealed RX slab, jumped into.
- **mode 4 = `--compile`** — x86 TEXT (GAS `.s`) to stdout, assembled by `as`/`gcc`, linked against `libscrip_rt.so`.

Both share ONE emitter (`bb_*`/`xa_*` templates) and MUST share ONE driver setup. SAME source → SAME IR → SAME logical instruction sequence; the ONLY permitted difference is LEAF materialization inside `x86(...)`: bytes for BINARY, GAS text for TEXT. Any different code PATH, missing fast path, different runtime call, or different operand source is a **DEFECT to be driven to zero (99.999% identity)**. "Same output" is necessary but NOT sufficient — two engines can print the same bytes via different code. This rung targets the CODE, then the output.

**MODES 1 AND 2 DO NOT EXIST** (AST-walk evaluator + IR-graph interpreter, both DELETED; driver exposes only `--run`/`--compile`). What survives is RESIDUE: stale strings/comments in live code, dead `src/attic/` files, stale prose in authoritative docs — purge on sight. **Scope guard:** archival HANDOFF/SESSION/FINDING records are history, NOT live descriptions — never rewritten. Target only surfaces a reader consults to understand SCRIP *today*.

---

## CONFIRMED DIVERGENCES

- **D1 — ✅ CLOSED 2026-08-12c (Claude Sonnet 5), measured not assumed.** Claim was a ~7–8× mode-3 penalty from by-name global hashing (862ms vs 113ms on `arith_loop`). Re-measured `corpus/benchmarks/snobol4/arith_loop.sno` (1M-iteration loop, global `N` hit every iteration — D1's own shape), same box/build, `RT_OPT` unset → `-O0`, 3 runs each: **mode-3 22/22/24ms · mode-4 22/23/23ms** (oracle `sbl -b` 58ms, sanity only). No gap. `rt_gva_island()` pinned-VA (shared with Icon/Prolog/Raku) already covers SNOBOL4 mode-3; no driver edit needed. The old M34-2a/b plan is DELETED — it was written against the retired `rbx=GVA base` model. A different globals-heavy shape showing a gap = NEW step number + its own measurement, never a reopen of 2a/b.
- **D2 — The driver runs TWO separate, drifting setup blocks.** `mode_compile_x86` (TEXT) and `mode_run` (BINARY) each independently do proc registration, global collection, preamble construction, per-language dispatch. Parallel but NOT identical. Duplicated setup is the ROOT CAUSE: a fast path added to one is invisible to the other. Cure = ONE shared setup, parameterized only by emission medium. → M34-4.
- **D3 — DCR-2 mid-flight, currently mode-4-only.** Direct-dispatch (`__proc[]` + `rt_call_proc_direct`): TEXT arm landed in `bb_call.cpp`, driver wiring NOT done, `g_proc_direct_active` never set ⇒ DORMANT in both modes (behavior-neutral). When activated it MUST be both-medium or it becomes a fresh D1-class divergence. This rung GOVERNS its completion. → M34-3.
- **D4 — The crosscheck gate is mode-4 ONLY** (`test_crosscheck_snobol4.sh` header, "Lon directive 2026-06-06"). SUPERSEDED by this rung: gates must assert `m3 == m4 == .ref`. Until then mode-3 regressions are invisible. → M34-6a.
- **D5 — Mode-3 coverage gaps.** Mode-3 soft-falls on shapes mode-4 handles. → M34-5.

## CENSUS OF RECORD

**TOTAL=318 · IDENTICAL=254 · DIFFER=16 · M3-MISS=46 · M4-MISS=1 · BOTH-FAIL=1** (2026-08-12b, post-5a-fix, harness `94d283c`+`dbd85305`). Committed: `SCRIP/docs/MODE34-PARITY-CENSUS-2026-08-12b.tsv`.

⛔ Any future census MUST state corpus size and harness commit — the 2026-06-25 baseline (262 programs) is void for comparison: corpus grew, and its harness carried the `-no-pie` bug. **Diff the SETS, never just the counts** (s22b law). The 5a fix moved ZERO of the 16 DIFFER — `*_pat_arbno_defer_*` / `*_pat_cap_*` remain the obvious shared-mechanism candidate.

## ROUTED IN (open)

**`treebank-array` m4-only SEGV** (rc=139, m3 green) — routed from GOAL-RBP-EARN (Lon-approved split, 2026-08-12 s40); a MODE34-IDENTICAL violation, not a defer-boundary item, so it bills HERE. Repro + prior analysis: GOAL-RBP-EARN s38 FIX PLAN STEP 2 (verbatim there until this file adopts it) + `archive/ARCHIVE-RBP-EARN-CURSOR-HISTORY.md`.
> ⚠ **Read through M34-5c first.** "m4-only SEGV, m3 green" is EXACTLY the shape 5a wore, and 5a was not m4-only at all — m3 ran the same defective shared path, had no assembler to complain with, emitted wrong code, and looked green. **"m3 green" is not evidence m3 is correct; it is evidence m3 did not CRASH.** Before treating this as m4 codegen: diff m3's output against the ORACLE (not against m3's prior output, not against "it ran"), and check whether the faulting path sits behind a `g_is_text` conditional.

## STEPS

### M34-3 — Close D3: finish DCR-2 both-medium
- [ ] **M34-3a — mode-4 driver wiring.** SNOBOL4 mode-4 block: after `gva` emission, `proc_collect_reset()` + `proc_collect_graph(sbbg)`; if `proc_slot_count()>0` emit `.bss __proc: .space n*8` + `.rodata __proc_names` + preamble `lea rdi,__proc_names; lea rsi,__proc; mov edx,n; call rt_proc_table_fill@PLT` (AFTER `gva_register` — `proc_startup` must register first). Set `g_proc_direct_active=1` around `gvar_flat_chain_build_text`.
- [ ] **M34-3b — mode-3 binary arm + activation.** BINARY arm in `bb_call_gvar_userproc_str`: bake `mov edi, idx` via `rt_proc_index_of(fn)` at emit time (valid — mode-3 driver registers all procs before chain build), then `x86_call_ro("rt_call_proc_direct", &rt_call_proc_direct)`. Set `g_proc_direct_active=1` in the mode-3 block (no `.bss` table; the immediate is baked).
- [ ] **M34-3c — gate.** Crosscheck BOTH modes byte-identical to pristine HEAD fail-set, zero regressions. Census: func_call/fibonacci/roman IDENTICAL both modes. A/B both modes vs HEAD. Re-ground 3-way vs oracle.

### M34-4 — Close D2: unify driver setup (the structural guarantee)
- [ ] **M34-4a — extract ONE shared setup.** Factor per-language setup (proc registration, `gva_collect`, `proc_collect`, preamble plan) out of both mode blocks into one routine returning a setup descriptor. The blocks then differ ONLY in emission leaf (binary slab vs text `.s`) and entry (`m3_enter_with_rbx`/in-process call vs `main:` + `call flat_α`). After this, D1-class drift is structurally impossible.
- [ ] **M34-4b — gate.** Census unchanged-or-better; crosscheck BOTH modes byte-identical; all language gates green (Icon/Prolog/Pascal/Raku must not regress).

### M34-5 — Close D5: mode-3 coverage parity
⚠ **SCOPE CORRECTION (learned from 5a):** this step was written as if every mode-3 gap were a MISSING ARM (M3-MISS — a soft-fall you can see). 5a was neither: a defect on the SHARED path whose mode-4 arm failed LOUDLY (`as` rejects a duplicate symbol) while its mode-3 arm failed SILENTLY (no assembler to complain ⇒ wrong code, kept going). That class is invisible to M3-MISS enumeration AND to any gate checking mode-3 only for absence-of-output. 5c is that class; it is not optional and is probably larger than the M3-MISS list.
- [ ] **M34-5a — enumerate M3-MISS** from the census; triage each shape's missing BINARY arm.
- [ ] **M34-5b — fill the missing binary arms** shape-by-shape until M3-MISS == 0 for SNOBOL4. Each fix is a both-medium template completion; gate per shape.
- [ ] **M34-5c — ⭐ sweep the LOUD-IN-M4 / SILENT-IN-M3 class.** For every mode-4 assembler/link failure (duplicate symbol, undefined symbol, relocation error): does the SAME shared path run in mode-3, and what does mode-3 do instead of erroring? The mode-4 diagnostic is a free detector for a defect mode-3 cannot report. Method that worked for 5a: instrument the suspect emit-time identity, dump `codegen_flat_chain_body`'s `nodes[]` per chain, compare the node MULTISET against the graph — a node appearing twice is the bug, whichever medium noticed. Start at `grep -n 'g_is_text' src/emitter/emit.cpp`: every hit is a place the modes can silently part company, and one (the group-root pass) was already wrong.

### M34-6 — All gates run BOTH modes (standing requirement)
- [ ] **M34-6a — crosscheck.** Rewrite `test_crosscheck_snobol4.sh` to run both modes per program and assert `m3==m4==ref`. Retire the "MODE-4 ONLY" header. `DIFFER` = hard FAIL.
- [ ] **M34-6b — every other gate.** Same assertion for `test_bench_snobol4_modes.sh`, the feature/demo `.s` regen flows, and the Icon/Prolog/Pascal/Raku gates. Every rung gate in every goal file inherits this.
- [ ] **M34-6c — harness in CI.** `test_mode34_parity.sh` becomes first-class, invoked by handoff whenever codegen is touched.
- [ ] **M34-6d — ⛔ THE HARNESS MUST SELF-CHECK BEFORE IT REPORTS.** The `-no-pie` bug (fixed `94d283c`) failed every mode-4 link, and the harness reported `IDENTICAL=0 DIFFER=0 M4-MISS=271` — a clean-LOOKING census that PASSED its own exit gate (nonzero only on DIFFER) while measuring nothing. **A gate that can silently degrade to measuring nothing is worse than no gate: it manufactures false confidence.** Fix: before the corpus loop, run a trivial known-good program (`OUTPUT = "x"`) through the FULL mode-4 pipeline; if not IDENTICAL, `exit 2` "HARNESS BROKEN — not a corpus result" + verbatim toolchain error. Also refuse to print a census where `M4-MISS + BOTH-FAIL > 50%` of TOTAL without `--allow-mass-failure`. Apply to every both-mode gate 6a/6b create — the class is generic, not PIE-specific.

### M34-7 — Template-level 1:1 audit (defense in depth)
- [ ] **M34-7a — both-arm presence.** Every `bb_*.cpp`/`xa_*.cpp` must have BOTH a BINARY and a TEXT arm corresponding instruction-for-instruction. Reuse `test_gate_template_medium_invisible.sh --strict` + the RULES.md `MEDIUM_*` greps. Raw bytes outside `x86_asm.h`, or output gated on `MEDIUM_*`, is already forbidden — prove zero tree-wide. (Baseline debt at 2026-08-12b: 12 — `bb_glue_flat.cpp` 4, `xa_flat.cpp` 8.)
- [ ] **M34-7b — encoder coverage.** Every `x86("…")` mnemonic used by a template needs BOTH a binary encoder (`x86_asm.h`) and a text form, so neither medium silently drops an instruction. Enumerate; assert both.
- [ ] **M34-7c — ⭐ audit medium-conditional guards, starting with a provably vacuous one.** `codegen_flat_chain_body`'s group-root pass reads `if (g_emit_cfg && (!g_is_text || entry == g_emit_cfg->entry))`. Both halves defective: (i) `!g_is_text` makes the guard a no-op in mode-3, so the pass fires unconditionally there — the asymmetry that let 5a corrupt mode-3 silently; (ii) `entry == g_emit_cfg->entry` evidently meant "only main's own top-level chain" but is TRUE for ANY graph whose entry equals its own `g->entry` — every single-node stub, every proc chain. **The 5a fix routes AROUND this guard rather than repairing it**, deliberately. Someone must decide: give it a predicate that actually names "main's own chain", or delete it as vacuous. Until then it reads like a restriction and restricts nothing. Same audit for every other `g_is_text`/`MEDIUM_*` conditional outside the `x86()` leaf — by this rung's mandate a medium-conditional guard on a WALK is a defect by construction.

---

## GATE PHILOSOPHY (every step)
1. **Code parity before output parity.** Done = the mode-3 and mode-4 instruction streams correspond for the targeted shape AND outputs match.
2. **Both modes, every gate.** `m3==m4==ref` or FAIL.
3. **Oracle-grounded.** `/home/claude/x64/bin/sbl -b` (token-free) is the semantic oracle for SNOBOL4/Snocone. Never assert speedups from SCRIP-vs-SCRIP alone.
4. **No regression.** Crosscheck fail-SET stays byte-identical to pristine HEAD across the whole rung.

## Prereq reads (NON-NEGOTIABLE for any step touching emission)
⛔ **`src/emitter/bb_regs.h` DOES NOT EXIST** (confirmed by `find`; `REGISTER-LAYOUT.md` carries its own correction banner; `emit.h` says it "was dead and dropped"). Register contract of record = **`ARCH-ICON.md` §REGISTER CONTRACT** (2026-07-18, billed as register truth for ALL BB codegen, all languages), backed by live `src/templates/x86_asm.h`: **r13=Σ subject base · r14=δ cursor · r15=Δ length · r12=DCAP/CAS top (NOT the ζ frame) · rbx=WS/GC bump-frontier top · GVA globals address absolutely via `ABSQ(RT_GVA_VA + k*16)`, no register base.** This CONTRADICTS the older `rbx=GVA base` claim still repeated in places; `REGISTER-LAYOUT.md` is stale on the r12 row by its own admission — read it only for the SPITBOL/CSNOBOL4 oracle maps.
Also: `ARCH-x86.md` §"Boxes are stackless" + §"Flat-BB ABI" · `src/emitter/XA_templates/xa_flat.cpp` (glob preamble) · `ARCH-SCRIP.md` · for driver work, `src/driver/scrip.c` `mode_compile_x86` and `mode_run` blocks side by side.

## Build / probe
⛔ Boehm GC is GONE (deleted by GC-U-4 s67) — no `libgc-dev`, no `-lgc`. `scripts/install_system_packages.sh` is the ONE authority for box packages; run it, never hand-rolled apt.
```bash
bash scripts/install_system_packages.sh && make -j4 scrip && make libscrip_rt
```
Tri-probe in BOTH modes (⛔ **`-no-pie` MANDATORY** — this container's gcc defaults to PIE and SCRIP's `.o` carries `R_X86_64_32S` relocations illegal in a PIE link; omitting it is exactly the bug that silently broke the parity harness until `94d283c`):
`./scrip --run p.sno` vs `./scrip --compile p.sno > p.s; gcc -no-pie p.s -Lout -lscrip_rt -lm -Wl,-rpath,$PWD/out -o p.bin; ./p.bin` vs oracle `/home/claude/x64/bin/sbl -b p.sno`.
