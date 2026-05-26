# HANDOFF — 2026-05-26 — Opus 4.7 Session (GOAL-ICON-BB Phase J-2 + THE FOUR FACTS)

**Goal:** GOAL-ICON-BB, Phase J — mode 3 (`--run`) executes the SHARED emitter's flat-wired x86,
killing the JIT's C-walker bridge so mode 3 ≡ mode 4 modulo the process boundary.
**one4all:** `106b7c51` PUSHED (rebased onto upstream `1af97d90`, clean).
**.github:** `388fa609`+ PUSHED (this file + PLAN.md watermark + GOAL-ICON-BB.md FOUR FACTS).
**Build:** ✅ GREEN. **Gates:** smoke_icon 5/5 · broker 23 (×stable) · rungs --interp 195 — all == baseline.

---

## THE FOUR FACTS (now permanently recorded at top of GOAL-ICON-BB.md)

Lon has stated these for ~2 months; every session re-derives them. They are written into the goal
file so they cannot be missed. They are ALL THE SAME RULE:

1. **C walkers live in MODE 2 ONLY.** Mode 2 (`--interp`, SM dispatch) is the reference path;
   C four-port walkers (`icn_bb_dcg`/`pl_bb_dcg`/`bb_exec_once`/`bb_exec_resume`/`bb_exec.c`) belong here.
2. **NO C walkers in mode 3 or mode 4. PERIOD.** Those symbols stay DEFINED (mode 2 needs them) but
   become UNREACHABLE from `--run`/`--compile`.
3. **In mode 3/4 the SM and BB structures DO NOT EXIST at run time.** They exist only at emit time;
   the emitter consumes them ONCE and bakes relocations into the BYTES (never graph pointers).
   `scrip.c` frees SM+BB before the runner executes (which gets `NULL`). Keeping a structure alive
   past the free = the PJ-AGW-1c mistake, REVERTED upstream `1af97d90`. Do NOT re-attempt for any language.
4. **Both SM and BB are x86 from the SHARED template emitter.** One source (`src/emitter/` +
   `BB_templates/`/`SM_templates/`/`XA_templates/`), two consumers: mode 4 = bytes to a binary run as a
   separate process; mode 3 = same bytes into a `PROT_EXEC` buffer called in-process. A second x86
   producer (e.g. replicating templates in the JIT `sl_*` byte-emitters) is FORBIDDEN — copies drift.

**One rule:** run time in mode 3/4 = self-contained x86 blob + fixed PLT symbols, nothing else.
**Completion test (verifiable):** reachability to the 4 C-walker symbols from any mode-3/mode-4 entry == ZERO.

---

## What landed — J-2 (commit `106b7c51`)

`src/emitter/sm_codegen_x64_emit_test.c` (+123) and `Makefile` (+1 char).

J-2 = "emitter binary sink usable from the JIT (in-memory, not FILE)". Implemented a `--memcheck`
mode in the existing emit-test harness that emits the canonical SM programs (EM-2 lit+halt, EM-3
arith, EM-4b loop) twice — once to a real file via `emit_to()`, once to an `open_memstream` `FILE*`
via `emit_to_mem()` — and asserts byte-identity. **Result: 3/3 BYTE-IDENTICAL.**

This proves the in-memory `FILE*` sink (which J-3 will load into `PROT_EXEC`) faithfully captures
the SAME bytes mode 4 writes to a `.s` file. `open_memstream` was chosen as the sink so no new buffer
API is introduced (honors Lon's 2026-05-28 "no growable buffer" ruling — memstream IS the FILE*).

### Finding: `codegen_sm_x86` is single-shot-per-process
First attempt (two emits in ONE process) FAILED (4481 vs 4578 bytes, then segfault). Cause: the
emitter carries PROCESS-GLOBAL accumulators (strtab, expression/pl registries, macro-library state)
not reset between calls. The faithful contract is single-shot-per-process — which is EXACTLY how
mode-3 and mode-4 each invoke the emitter (once). So `run_memcheck` fork-isolates each emission
(pristine global state per child). This is not a workaround; it mirrors real invocation.

### Makefile fix
`make out/sm_codegen_x64_emit_test` failed at clean HEAD (missing `-I$(SRC)/include`; `SM.h` lives
there). Added the include to that one target. Pre-existing gap, unrelated to J-2 logic.

### scrip binary UNTOUCHED
Only the standalone test harness + one Makefile target changed. Therefore smoke/broker/rungs and
mode-1/mode-4 emit baselines are preserved BY CONSTRUCTION (the binary is bit-for-bit the same).

---

## J-3 — deletion surface PINNED (do this next)

The exact mode-3 → C-walker edge to SEVER (the FACT-2 violation):
- `sm_jit_interp.c:2072` — `sl_call(rt_bb_pump_proc)` (bakes the call into the mode-3 blob)
- `sm_jit_interp.c:1648` — `bake_blob_call_si(rt_bb_pump_proc, ...)` (same, with args)
- `rt_bb_pump_proc` (sm_jit_interp.c:233, JIT-local) → `icn_bb_pump_proc_by_name` →
  `bb_node_t{.fn=icn_bb_dcg}` → `bb_exec_once`/`bb_exec_resume` = THE C WALKER.

These two bake sites must be replaced with the shared emitter's flat-wired BB x86 — the SAME x86
mode 4 already emits (captured via the J-2 memstream, loaded into `PROT_EXEC`, fixups applied
in-process, entry registered in `g_label_blob_map`). The walker symbols themselves STAY (mode 2).
`sm_interp.c` reaching the walker is FINE — that is mode 2.

**Symptom that J-3/J-4 fixes:** `./scrip --run hello.icn` → `sm_eval_subexpr: invalid entry_pc 1`
(while `--interp` prints `hello`). Cause is FACT 3: the baked `call rt_bb_pump_proc` reads
`bb_table` AFTER `stage2_free_bb_after_emit` freed it (scrip.c:442-444) → NULL → oneshot →
`sm_eval_subexpr` on the freed SM → invalid pc. Fix is NOT to delay the free; fix is to make the
blob self-contained so nothing reads `bb_table` at run time, after which the pre-run free is correct.

### J-3 steps (in goal file)
- J-3 loader: memstream bytes → JIT `PROT_EXEC` buffer, apply `bb_fixup_*`, register entry by name.
  Gate: loader unit runs the loaded `main` blob for `hello.icn` and prints "hello".
- J-4: behind `SCRIP_JIT_FLAT_BB`, replace the two bake sites with emit-via-J-2 + load-via-J-3 +
  `call <blob_addr>`. ⛔ The flag is BRING-UP SCAFFOLDING ONLY — deleted at J-5/J-6 (FACT 2). It is
  NOT a permanent C-path escape hatch.

---

## Gates at handoff (one4all `106b7c51`)
```
smoke_icon              5/5      (== baseline)
unified_broker          23       (≥19, stable ×)
icon_all_rungs --interp 195      (≥195 invariant)
J-2 --memcheck          3/3 byte-identical
```

## Pre-existing, NOT regressed
- `scripts/test_smoke_compile.sh` FAILS at clean HEAD on missing `/home/claude/one4all/sm_macros.s`
  ("FAIL no push_int call in sm_macros.s"). Verified by git-stash test against `7fe1e31a`. Not a
  Phase J invariant gate. Environment/path issue, separate investigation.

## Environment note
- `libgc-dev` must be installed for the build (`apt-get install -y libgc-dev`) — `gc/gc.h`.
