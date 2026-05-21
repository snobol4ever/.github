# PPV-0 — Inventory of 7 Protected Pattern-Variable Names

**Rung:** EC-UNI-PROTECTED-PAT-VARS / PPV-0
**Date:** 2026-05-21 (session #4, Opus 4.7)
**Author:** Claude Opus 4.7 (third developer per Three-Milestone Authorship Agreement)
**HEAD:** one4all `9b905d26`, .github `658dc549`, corpus `5fc1427`
**Status:** ✅ COMPLETE — no code changes, read-only inventory

---

## 1. Enum inventory — all 7 pat-names confirmed present

### `TT_*` (token / tree-node kind) — `src/frontend/snobol4/snobol4.y` (pat_prim_kind table, lines 47-51)

All 7 names mapped to dedicated tree-node kinds:

| Source name | TT_*       | Mapping confirmed |
|-------------|------------|-------------------|
| REM         | TT_REM     | line 49           |
| ARB         | TT_ARB     | line 49           |
| FENCE       | TT_FENCE   | line 50           |
| FAIL        | TT_FAIL    | line 49           |
| SUCCEED     | TT_SUCCEED | line 49           |
| ABORT       | TT_ABORT   | line 50           |
| BAL         | TT_BAL     | line 50           |

Note: `pat_prim_kind()` only matches when the parser already knows the identifier is in pattern-primitive context (via `KEYWORD()` parens form per goal-file analysis). The bare-name `'hello' REM` path does NOT reach `pat_prim_kind` — it lexes as `T_IDENT` and reaches `lower_pat_expr` via `TT_VAR` (see §3).

### `SM_PAT_*` (stack machine opcodes) — `src/include/SM.h:44-52`

All 7 names have dedicated SM opcodes (zero-arg variants):

| Pat-name | SM opcode      | Line |
|----------|----------------|------|
| ARB      | SM_PAT_ARB     | 44   |
| (ARBNO)  | SM_PAT_ARBNO   | 45   |
| REM      | SM_PAT_REM     | 46   |
| BAL      | SM_PAT_BAL     | 47   |
| FENCE    | SM_PAT_FENCE0  | 48   |
| (FENCE1) | SM_PAT_FENCE1  | 49   |
| ABORT    | SM_PAT_ABORT   | 50   |
| FAIL     | SM_PAT_FAIL    | 51   |
| SUCCEED  | SM_PAT_SUCCEED | 52   |

ARBNO and FENCE1 are 1-arg variants (require a child pattern); the 7 zero-arg pat-names use the 0-arg opcodes above.

### `BB_PAT_*` / `BB_*` (Byrd-box graph kinds) — `src/include/BB.h:55-75`

| Pat-name | BB kind        | Line | Lifted template       |
|----------|----------------|------|-----------------------|
| ARB      | BB_PAT_ARB     | 62   | `bb_arb.c`            |
| (ARBNO)  | BB_PAT_ARBNO   | 63   | `bb_arbno.c`          |
| REM      | BB_PAT_REM     | 72   | `bb_rem.c` (slice 1)  |
| FENCE    | BB_PAT_FENCE   | 73   | `bb_fence.c`          |
| ABORT    | BB_PAT_ABORT   | 74   | `bb_abort.c`          |
| FAIL     | —              | n/a  | (no BB pat — see §2)  |
| SUCCEED  | —              | n/a  | (no BB pat — see §2)  |
| BAL      | —              | n/a  | (no BB pat — see §2)  |

---

## 2. FAIL / SUCCEED / BAL clarification — "variant — no BB"

The goal-file table marked FAIL/SUCCEED/BAL as "(variant — no BB)". Confirmed via enum inspection:

- **No `BB_PAT_FAIL`, `BB_PAT_SUCCEED`, `BB_PAT_BAL`** in `BB_op_t` (BB.h).
- **`BB_FAIL` (line 37) and `BB_SUCCEED` (line 38) DO exist** — these are generic control-flow primitives (used by all languages, not the SNOBOL4 pattern-primitive line). Templates `bb_fail.c`/`bb_succeed.c` exist and correspond to these generic kinds, NOT to the SNOBOL4 pattern variants.
- **No `BB_BAL`** in any form.

Implication for PPV-2: the bare-name substitution for FAIL/SUCCEED/BAL emits `SM_PAT_FAIL`/`SM_PAT_SUCCEED`/`SM_PAT_BAL` (which exist at the SM layer), and the SM dispatcher / invariant optimizer will correctly mark these windows variant — there is no BB-lower path for them, which is the correct behavior. Phase B work would add `BB_PAT_FAIL` etc. and `bb_pat_fail.c` templates if those kinds ever needed native codegen, but the rung-table note is honest: PPV does not deliver BB coverage for these 3 kinds.

---

## 3. The substitution site — `src/lower/lower.c:373`

```c
case TT_VAR:   SM_emit_s(g_p, SM_PUSH_VAR, t->v.sval); SM_emit(g_p, SM_PAT_DEREF); return;
```

This is THE site PPV-2 must modify. When pattern-context lowering sees a bare identifier (typed as `TT_VAR`), it currently emits the runtime-dereference pair `SM_PUSH_VAR` + `SM_PAT_DEREF`. PPV-2 will guard this with a name check: if `t->v.sval` matches one of the 7 protected pat-names, emit the corresponding `SM_PAT_<KIND>` directly and return.

No separate `lower_pat_atom` function exists. `lower_pat_expr` is the sole pattern-lowering entry point in lower.c (confirmed via `grep -n "lower_pat_atom\|lower_pat_expr" src/lower/lower.c` — only `lower_pat_expr` declarations / definitions / recursive calls; no `lower_pat_atom`).

### Mapping table for PPV-2's substitution

| Bare name in source | t->v.sval = | Substituted emission        |
|---------------------|-------------|------------------------------|
| `REM`               | "REM"       | `SM_emit(g_p, SM_PAT_REM)`   |
| `ARB`               | "ARB"       | `SM_emit(g_p, SM_PAT_ARB)`   |
| `FENCE`             | "FENCE"     | `SM_emit(g_p, SM_PAT_FENCE0)`|
| `FAIL`              | "FAIL"      | `SM_emit(g_p, SM_PAT_FAIL)`  |
| `SUCCEED`           | "SUCCEED"   | `SM_emit(g_p, SM_PAT_SUCCEED)`|
| `ABORT`             | "ABORT"     | `SM_emit(g_p, SM_PAT_ABORT)` |
| `BAL`               | "BAL"       | `SM_emit(g_p, SM_PAT_BAL)`   |

Note: `FENCE` bare → `SM_PAT_FENCE0` (not `SM_PAT_FENCE`, which does not exist — only the 0/1-suffixed variants are in the enum).

---

## 4. The runtime-protection site — `src/runtime/rt/rt.c:467`

```c
void rt_nv_set(const char *name)
{
    DESCR_t val = vstack_pop();
    if (val.v == DT_FAIL) {
        vstack_push(val);
        LAST_OK_SET(0);
        return;
    }
    NV_SET_fn(name ? name : "", val);
    LAST_OK_SET(1);
}
```

PPV-1 will insert a name check at the top of this function: if `name` matches one of the 7 protected pat-names, call `sno_runtime_error(42, NULL)` and return without storing.

### Error-signaling primitive — `sno_runtime_error(code, msg)`

Declared in `src/runtime/snobol4/snobol4.h:349`. Already used throughout `snobol4_pattern.c` for pattern-related errors. ERROR 042 is the standard SNOBOL4 error for "attempt to change value of protected variable" (matches SPITBOL).

### Confirmation: `rt_nv_set` is the SOLE store-var runtime entry point

`emit_sm.c:342` template binds `SM_STORE_VAR` → `"rt_nv_set"` (the C symbol that emitted x86/JVM/JS/NET/WASM code calls into for the assignment opcode). All five backends route through this one function, so the protection landing here covers every emission target.

There's also `NV_SET_fn` (the lower-level setter that `rt_nv_set` delegates to). PPV-1 should land the check in `rt_nv_set` (the public ABI boundary), not inside `NV_SET_fn` (the implementation) — the former is exactly the "any time scrip emits a variable assignment" entry point.

---

## 5. PPV-2's general-expression (PPV-3) concern

The goal file requires: `x = REM` (RHS in general-expression context) must continue to work — copying the PATTERN value into x.

`lower_expr` (the general-expression lowering) handles `TT_VAR` separately from `lower_pat_expr`. Confirmed by reading lower.c structure: `lower_expr` is a distinct function; `lower_pat_expr` is only called from pattern-specific contexts (e.g., `lower_pat_expr(pattern)` at line 625, 1668; and via the recursive calls in lines 381/394/etc.).

PPV-2's change is confined to `lower_pat_expr`'s `TT_VAR` arm at line 373. The general-expression path is untouched, so `x = REM` continues to lookup REM as a variable (whose value happens to be the PATTERN-typed primitive — exactly as SPITBOL does).

PPV-3 will write an explicit test program for `x = REM` and verify behavior post-PPV-2.

---

## 6. Phase B / out-of-scope items (recorded but not done)

- **No new BB_PAT_FAIL / BB_PAT_SUCCEED / BB_PAT_BAL.** These three kinds remain "variant — no BB" after PPV. Native codegen for them is Phase B work.
- **No new template files.** Existing templates (`bb_rem.c`, `bb_arb.c`, `bb_fence.c`, `bb_abort.c`, `bb_arbno.c`) already cover the 4 BB pat-kinds PPV will newly exercise.
- **No SM_op_t enum changes.** All 7 SM_PAT_* opcodes already exist; PPV reuses them.
- **No BB_op_t enum changes.** Likewise.

---

## 7. Gate state at PPV-0 start

Per session-start gate (`scripts/test_per_kind_diff.sh`):

```
PASS=399   FAIL=0     STUB=660   NEW=0     GONE=0
```

Matches the watermark in GOAL-HEADQUARTERS.md exactly. Clean start for PPV-1 implementation.

---

## 8. Summary — what PPV-1/PPV-2 need to do

| Step  | File touched                          | Change                                                                                  |
|-------|----------------------------------------|------------------------------------------------------------------------------------------|
| PPV-1 | `src/runtime/rt/rt.c`                  | At top of `rt_nv_set`: name check → `sno_runtime_error(42, NULL)` if protected.         |
| PPV-1 | `src/runtime/rt/rt.c` (or new header)  | Static const `g_protected_pat_names[7]` + `is_protected_pat_name(const char *)` helper. |
| PPV-2 | `src/lower/lower.c:373` (TT_VAR arm)   | Before `SM_PUSH_VAR`+`SM_PAT_DEREF`, check name → emit `SM_PAT_<KIND>` if protected.    |
| PPV-2 | (shared header for the name→op table)  | Static const `{name, SM_op_t}` lookup table reused by lower.c and rt.c.                 |

The helper `is_protected_pat_name(const char *)` and the name→op lookup table are the only new code surface. Both belong in a single small new helper module or in an existing widely-included header. Recommend `src/runtime/rt/rt_protected.{c,h}` to keep the runtime-side check self-contained, with the SM_op_t lookup table beside it; lower.c includes `rt_protected.h` for the lookup.

PPV-1 is the smaller and lower-risk change (runtime protection — purely additive, no codegen-path effects). PPV-2 changes lower-time behavior and WILL move bytes (beauty md5 will likely change) — that's the explicit Lon-decision point at PPV-5.

---

**PPV-0 done.** No code committed; this file is the deliverable. PPV-1 next.
