# GOAL-ICON-BB-JCON.md — Icon: 43 BB emitters + lower_icn DCG

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

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

### ✅ EMERGENCY — REVERT icn_bb_every AND icn_bb_to — DONE `bb48e6c3`

`icn_bb_to` → `IR_ICN_TO` DCG (ir_exec.c executor + lower_icn_to + icn_bb_dcg wire).
`icn_bb_every` → `IR_ICN_EVERY` DCG (ir_exec.c executor + lower_icn_every + icn_bb_dcg wire).
TT_SEQ filter path also wired to lower_icn_every. Gates: smoke_icon 5/5, broker 21/49.

### IJ-19-debug — fix upto scalar dispatch in icn_bb_build (FIRST)

- [x] Add debug print, confirm `fn` and position in TT_FNC block.
      Fix dispatch condition so `upto('aeiou', "hello world")` → `icn_bb_dcg`.
      Verify: `./scrip --ir-run /tmp/test_upto.icn` prints `2\n5\n8` (positions in "hello world").
      GATE-1..4. Commit.
      Root causes fixed: (1) IR_ICN_UPTO stored hay in nd->value.s which IR_reset zeroed —
      moved to new IR_t.sval2 field. (2) icn_bb_every was returning icn_lazy_box stub —
      implemented and wired. one4all `a82b42c5`.

### IJ-19-to — implement TT_TO generator (smoke_icon every test)

- [x] Implemented as IR_ICN_TO DCG (icn_bb_to C BB deleted). lower_icn_to+icn_bb_dcg wire.
      Verify: `every write(1 to 3)` prints 1,2,3. GATE-1 PASS=5. one4all `bb48e6c3`.

### IJ-19-to-by — implement TT_TO_BY

- [x] IR_ICN_TO_BY DCG. ival=lo,ival2=hi,ival3=step. lower_icn_to_by+icn_bb_dcg.
      rung07_control_to_by PASS, rung19_pow_toby_* int/var PASS. one4all `a0b0700b`.

### IJ-19-iterate — implement TT_ITERATE (!str, !list, !table)

- [x] IR_ICN_ITERATE string path. sval2=str, ival=len, counter=pos; GC_malloc 1-char per tick.
      lower_icn_iterate + icn_bb_dcg wire. list/table/Raku remain lazy (future). one4all `8cf94938`.

### IJ-19-alternate — implement TT_ALTERNATE (A|B)

- [x] IR_ICN_ALTERNATE DCG. icn_alt_dcg_t{gen[2],which} in opaque. n-ary chain. one4all `51460d4f`.
      ir-run 153→159 (+6), honest 271→275 (+4).

### IJ-19-limit — implement TT_LIMIT (gen\\N)

- [x] IR_ICN_LIMIT DCG. icn_lim_dcg_t{gen,max,count} in opaque. one4all `b7d74bf9`.
      ir-run 159→164 (+5), honest 275→276 (+1).

### IJ-19-binop-gen — arith/relop with generative operands

- [x] IR_ICN_BINOP DCG. icn_binop_dcg_t in opaque. icn_binop_apply in lower_icn.c.
      binop_map[] + TT_CAT cross-product wired. one4all `f63c60f0`.
      ir-run 164→174 (+10), broker 22→23.

### IJ-19-remaining — remaining constructs in order of complexity

**RESOLVED:** `rung13_alt_alt_filter` now passes (fixed in prior session).

**RESOLVED:** `fail` keyword in proc bodies now propagates correctly (IJ-19-fail, sess 2026-05-14).
Two bugs in `sm_interp.c`: (1) `SM_BB_EVAL` did not check `FRAME.returning` after `bb_eval_value`
drives `TT_PROC_FAIL` via alternation arm (`expr | fail`). (2) `sm_call_expression` read stack
top instead of `FAILDESCR` when `SM_FRETURN` fired at top-level of nested SM_State. Both fixed.
Fixes `if cond then fail`, `expr | fail`, bare `fail` as statement. `rung36_jcon_roman` now passes.
one4all `992a2a18`.

Next DCGs to implement (highest ir-run yield first):
- TT_SUSPEND (rung03_suspend_gen_*) — user proc suspend/resume — blocked on CH-17g
- TT_ITERATE list/table paths (rung22, rung13_table_iterate)
- rung36_jcon_* suite residual — most remaining failures: `every f(gen_arg)` doesn't
  re-pump arg generators (blocked on CH-17g). Landed this session: math builtins nargs>=1,
  list() nargs, ||| list concat, any/many/upto 2-arg, cset identity, image(DT_FH).
  rung36_jcon_kross now PASS. Remaining: fncs1 (global/record-field name collision),
  endetab (infinite loop), coerce (pre-existing segfault).

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

  one4all: e2d80506  corpus: 1fe096c
  ir-run:  PASS=202 FAIL=28
  honest:  PASS=275
  smoke_icon: 5/5   broker: 23/49
  NEXT: IJ-19-remaining — TT_SUSPEND (user proc generators, blocked on CH-17g coroutine prereq);
        rung32_strretval_strret_every (generative arg through user proc);
        rung36_jcon_scan: every (("a"|"b") ? write(upto(!&lcase))) only yields 2 values instead
        of 6 — icn_bb_scan_gen β path not re-pumping body gen (upto+generative-cset) when
        subject alternates; body exhausts and doesn't try next subject correctly;
        rung36_jcon_string: find/match/any/upto with generative pos args (1 to 10) missing output;
        rung36_jcon_wordcnt: sort(table, 3) — 2-arg sort not implemented;
        rung36_jcon_substring H/I: !str := val string frame-local writeback;
        rung36_jcon_* suite (various builtins and features)

  Session fixes (+1, 1 commit this session):
    e2d80506 IJ-19-remaining: fix icn_bb_scan_gen integer subject crash (honest 273->275)
  Prior session fixes:
    11c43e0d IJ-19-remaining: image(DT_FH) fix; any/many/upto 2-arg in icn_try_call_builtin_by_name
    fec85821 IJ-19-remaining: any/many/upto 2-arg outside scan, cset identity (slen=0xFFFFFFFF) fix
    390335c3 IJ-19-remaining: math nargs>=1, list() nargs>=0, ||| list concat, scan_pos default
    992a2a18 IJ-19-fail: fix fail keyword in proc bodies (SM_BB_EVAL + sm_call_expression) — roman +1
