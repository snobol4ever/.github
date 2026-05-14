# GOAL-ICON-BB-JCON.md — Icon BB emitters (43 JCON constructs)

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ No coro subsystem. Icon is pure BB. Do NOT touch coro_runtime.c or coro_*.
⚠ BB RULE: Read `.github/jcon_irgen.icn` before touching any BB.

---

## Architecture — what a BB emitter IS

Each Icon generator construct maps to an `emit_bb_icon_*` function in `src/emitter/emit_bb.c`.
That function emits **inline x86 assembly** implementing alpha/beta directly — no C helper called.

Reference sources for alpha/beta logic of each construct:
1. `jcon_irgen.icn` — JCON IR: four-port wiring (start/resume/success/failure) for each AST node.
2. Deleted `icon_gen.c` — recoverable via `git show HEAD~1:src/runtime/interp/icon_gen.c`.
   Each `DESCR_t icn_bb_*(void *zeta, int entry)` body IS the alpha (entry==0) / beta (entry==1) logic.
   Use it as the direct specification for the inline x86.

Emitter pattern (TEXT mode):

  void emit_bb_icon_to(bb_label_t *s, bb_label_t *f, bb_label_t *b) {
      emit_bb_box_banner("ICN_TO", "");
      if (IS_TEXT) {
          int id = g_flat_node_id++;
          // Emit .data: zeta struct as zero-init .quad slots
          // Emit .text: alpha inline x86 — read zeta fields, compute, jmp s or f
          // emit_label_define(b)
          // Emit .text: beta inline x86 — advance state, jmp s or f
          return;
      }
      // binary mode: same logic via insn_* helpers
  }

Key rules:
- Zeta lives in .data as .quad 0 slots. SM populates fields at runtime before broker drives.
- Blob reads/writes zeta fields via [rip + zlbl + offset] (TEXT) or immediate ptr (binary).
- Blob jumps directly to s (success) or f (fail) — no rax test, no C call.
- Replace each ICN_EMIT2(...) one-liner with a real inline emitter body.
- Remove the corresponding `extern DESCR_t icn_bb_*` declaration when done.
- NO `DESCR_t foo(void *zeta, int entry)` C functions created anywhere, ever.

Simple state structs (start here):
  icn_to_state_t    = { long lo; long hi; long cur; }            3 quads, 24 bytes
  icn_to_by_state_t = { long lo; long hi; long step; long cur; } 4 quads, 32 bytes

TT_TO alpha/beta (from deleted icon_gen.c):
  α: cur=lo; if cur>hi → jmp f; else jmp s (value=cur)
  β: cur++; if cur>hi → jmp f; else jmp s (value=cur)

TT_TO_BY alpha/beta:
  α: cur=lo; if step>0 && cur>hi → jmp f; if step<0 && cur<hi → jmp f; else jmp s
  β: cur+=step; same bounds test; jmp s or f

Value delivery: the broker reads the value from wherever the emitter stores it
(a scratch slot in the zeta, or a shared DESCR_t result area). Look at how
existing inline boxes (emit_bb_xbal, emit_bb_xarbn) deliver results — adapt
that pattern for integer values.

---

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

---

## Active steps

### IJ-19-emit — write inline x86 BB emitters for the 43 JCON constructs

Replace each ICN_EMIT2 one-liner in emit_bb.c with real inline x86.
Start with the simplest (pure integer state, no pointers):

- [ ] emit_bb_icon_to      (TT_TO,    3-long state)   GATE-1..4. Commit.
- [ ] emit_bb_icon_to_by   (TT_TO_BY, 4-long state)   GATE-1..4. Commit.
- [ ] emit_bb_icon_iterate (TT_ITERATE, string state)  GATE-1..4. Commit.
- [ ] ... remaining 40 in order of state complexity.

Per-emitter procedure:
  1. `git show HEAD~1:src/runtime/interp/icon_gen.c` → find `icn_bb_CONSTRUCT` → read alpha/beta.
  2. Read `jcon_irgen.icn` `ir_a_CONSTRUCT` for four-port wiring.
  3. Write inline x86 body using bb3c_format (TEXT path).
  4. Replace ICN_EMIT2 one-liner. Remove extern DESCR_t declaration.
  5. GATE-1..4. Commit.

---

## Done when

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

  one4all: 58e1814a  corpus: 1fe096c
  ir-run:  PASS=191 FAIL=39 XFAIL=35
  honest:  PASS=276 FAIL=1 ABORT=0   broker: 23/49
  NEXT: IJ-19-emit — emit_bb_icon_to inline x86 (TT_TO, simplest 3-long state)
