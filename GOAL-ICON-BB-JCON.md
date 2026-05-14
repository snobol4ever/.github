# GOAL-ICON-BB-JCON.md — Icon BB: lower.c DCG + inline x86 emitters (43 JCON constructs)

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ No coro subsystem. Icon is pure BB. Do NOT touch coro_runtime.c or coro_*.
⚠ BB RULE: Read `.github/jcon_irgen.icn` before touching any BB.
⚠ NO C BB BOXES. No `DESCR_t foo(void *zeta, int entry)` functions anywhere, ever.

---

## Architecture — the two steps

### Step 1 — lower.c builds the DCG for Icon (FIRST)

Currently `lower.c` for Icon is a no-op: every TT_* node hits `ICN_BB_EVAL(t)` which
registers the raw `tree_t*` and emits `SM_BB_EVAL(id)`. The DCG is never built at
compile time — `icn_bb_build` walks the live AST at runtime on every call.

**The fix:** write `src/lower/lower_icn.c` (mirrors `lower_pat_dcg.c` for SNOBOL4).
For each Icon TT_* kind, build a compile-time `IR_block_t` graph with four ports
(start / resume / success / fail) wired per `jcon_irgen.icn`'s `ir_a_*` procedures.
Emit `SM_EXEC_BB(ptr)` instead of `SM_BB_EVAL(id)`.

Reference: `jcon_irgen.icn` — each `ir_a_CONSTRUCT` procedure shows exactly how the
four ports connect. That IS the DCG wiring for Icon.
Reference: `src/lower/lower_pat_dcg.c` — the SNOBOL4 equivalent; copy its structure.

### Step 2 — inline x86 emitters for each construct (AFTER Step 1)

Each `IR_block_t` node points to an `emit_bb_icon_*` function in `src/emitter/emit_bb.c`.
That function emits **inline x86** implementing alpha/beta directly — no C helper called.

Alpha/beta logic source: deleted `icon_gen.c` via
  `git show HEAD~1:src/runtime/interp/icon_gen.c`
Each `DESCR_t icn_bb_*(void *zeta, int entry)` body IS the alpha/beta spec.

Simple state structs (start here):
  icn_to_state_t    = { long lo; long hi; long cur; }             3 quads
  icn_to_by_state_t = { long lo; long hi; long step; long cur; }  4 quads

Replace each `ICN_EMIT2(...)` one-liner with a real inline x86 body.
Remove the corresponding `extern DESCR_t icn_bb_*` declaration when done.

---

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

---

## Active steps

### IJ-19-lower — write lower_icn.c: DCG for all Icon TT_* (Step 1)

- [ ] Create `src/lower/lower_icn.c` and `src/lower/lower_icn.h`.
      For each Icon TT_* kind, build `IR_block_t` graph following `jcon_irgen.icn` `ir_a_*`.
      Wire four ports: start→resume→success→fail per JCON wiring.
      Call from `lower.c` instead of `ICN_BB_EVAL(t)` for each TT_* kind.
      Emit `SM_EXEC_BB(ptr)` not `SM_BB_EVAL(id)`.
      Add to Makefile. GATE-1..4. Commit.

### IJ-19-emit — inline x86 emitters for 43 constructs (Step 2, after Step 1)

- [ ] emit_bb_icon_to      (TT_TO,    3-long state)   GATE-1..4. Commit.
- [ ] emit_bb_icon_to_by   (TT_TO_BY, 4-long state)   GATE-1..4. Commit.
- [ ] emit_bb_icon_iterate (TT_ITERATE)                GATE-1..4. Commit.
- [ ] ... remaining 40 in order of state complexity.

Per-emitter procedure:
  1. `git show HEAD~1:src/runtime/interp/icon_gen.c` → `icn_bb_CONSTRUCT` → alpha/beta logic.
  2. `jcon_irgen.icn` `ir_a_CONSTRUCT` → four-port wiring.
  3. Write inline x86 via bb3c_format (TEXT path). Zeta in .data as .quad slots.
     Blob jumps directly to s or f — no rax test, no C call.
  4. Replace ICN_EMIT2 one-liner. Remove extern DESCR_t declaration.
  5. GATE-1..4. Commit.

---

## Done when

  lower_icn.c builds DCG for all Icon TT_* at compile time.
  All 43 ICN_EMIT2 lines replaced with inline x86 emitters.
  No `extern DESCR_t icn_bb_*` declarations remain in emit_bb.c.
  ir-run PASS >= 230. Honest PASS >= 268. GATE-1..4 green.

---

## Invariants

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: broker PASS=23. Never regress.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. One construct per commit (or small coherent batch).
6. No `DESCR_t foo(void *zeta, int entry)` C functions anywhere — ever.
7. No corpus source modified to work around runtime bugs.

---

## Watermark

  one4all: b389062e  corpus: 1fe096c
  ir-run:  PASS=191 FAIL=39 XFAIL=35
  honest:  PASS=276 FAIL=1 ABORT=0   broker: 23/49
  NEXT: emit_bb_icon_to — first real inline x86 emitter (TT_TO, 3-long state {lo,hi,cur})
