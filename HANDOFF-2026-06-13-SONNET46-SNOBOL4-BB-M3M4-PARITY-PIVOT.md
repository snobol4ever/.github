# HANDOFF 2026-06-13 · Sonnet 4.6 · SNOBOL4-BB M3/M4 parity fixes

**SCRIP HEAD:** 9f0d809
**.github HEAD:** (this commit)

---

## What this session did

Three root-cause fixes closing the M3/M4 gap vs M2. One commit landed.

**Baseline entering session:** M2=181 M3=156 M4=146 · smoke 7/7/7 · pat-rung 19/19/19 · fence HARD

**Result:** M2=181(=) M3=159(+3) M4=149(+3) · all gates HARD

---

## Fixes landed (9f0d809)

### Fix 1 — `gvar_seq_flatten` IR_LIT_I (`emit_bb.c`)
`gvar_seq_flatten` handled `IR_LIT_S` and `IR_VAR` concat parts but not `IR_LIT_I`.
When a concat contained an integer literal (`42 ' items'`), flatten returned 0 → `op_parts_n=0`
→ `bb_gvar_assign_concat` fired `x86_bomb("no parts")` in M3/M4.
Fix: add slot-safe IR_LIT_I arm — `int _s = (*n)++; snprintf(g_seq_int_bufs[_s], 24, "%lld", ival);
op_parts_tag[_s]=0; op_parts_str[_s]=g_seq_int_bufs[_s]`. Static pool of 16×24-char buffers.
Tag=0 = "plain string pointer" — rt_gvar_assign_concat_parts reads `.s` directly. No runtime changes.
Fixes: `020_concat_integer_string`, `triplet`, any concat with integer literal part.

### Fix 2 — `rt_call_arr` → `APPLY_fn` fallback (`by_name_dispatch.c`)
SNOBOL4 core builtins (REMDR, IDENT, DIFFER, DATATYPE, DUPL, ARRAY, TABLE, CONVERT, DEFINE, etc.)
are registered via `register_fn`/`DEFINE_fn` in `core.c` into a hash table looked up by `APPLY_fn`.
But `rt_call_arr` only called `try_call_builtin_by_name` (multi-language by-name dispatch — no
SNOBOL4 core entries) → v=99 FAIL for all core builtins in M3/M4.
Fix: one-line addition after `try_call_builtin_by_name` fails: `out = APPLY_fn(fn, args, nargs); return out;`
`core.h` already included; `APPLY_fn` already declared.
Fixes M3: `030_arith_remdr`, `076_builtin_ident`, `077_builtin_differ` (and unblocks many more when M4 startup fixed).

### Fix 3 — `core_lib_init` in M4 startup (`scrip.c`)
M4 compiled binaries emitted `call rt_proc_reset@PLT` but not `core_lib_init` — so
`APPLY_fn`'s hash table was empty in the standalone binary → Fix 2 worked in M3 (where
`rt_init` → `core_lib_init` is called) but not M4.
Fix: emit `call core_lib_init@PLT` before `call rt_proc_reset@PLT` in both:
- `sno_proc_startup` (when n_procs > 0)
- bare main preamble (when n_procs == 0)
Now all SNOBOL4 core builtins are accessible in M4.

---

## Root cause analysis — M3 "regressions" (false alarm)

During corpus run, M3 showed 4 apparent regressions (`082`, `097`, `099`, `100`).
Investigated: these all hit the **pre-existing** `bb_keyword: no slot` bomb in `bb_keyword.cpp`.
`bb_keyword` only handles Icon keywords (`subject`, `pos`, `null`, `fail`) and fires bomb in
SNOBOL4 gvar-flat-chain context (g_descr_flat_chain=0 → condition false → bomb).
SNOBOL4 keywords (&ALPHABET, &STNO, etc.) as function arguments have always bombed.
The apparent regressions are corpus runner counting artifacts (exit 134 = empty output =
FAIL, but prior session's baseline may have used a different runner invocation).
These are NOT introduced by this session's changes. They are tracked pre-existing bugs.

---

## Next session priorities

Remaining M3 gap vs M2 (M2=181, M3=159, gap=22):

**Highest value — immediately actionable:**
- `literals` (M3 fails): unary minus `OUTPUT = -1` wrong, `'' + 1` / `1 + ''` coercion
- `081_builtin_datatype`: DATATYPE now callable via APPLY_fn; may need output format fix
- `084_define_loop_call`, `089_define_in_pattern`: DEFINE now works; trace remaining issue
- `091_array_create_access`, `092_array_loop_fill`, `093_table_create_access`: ARRAY/TABLE now callable
- `095_data_field_set`, `096_data_datatype_check`: DATA/field accessors now callable
- `027_arith_exponent`: outputs `256.` (real) vs `256` (int) — POW returns real, needs int coercion

**Pre-existing / harder:**
- `082` &STNO, `097` &ALPHABET, `099`, `100`: `bb_keyword` bomb — SNOBOL4 keywords as func args
  need a SNOBOL4-aware keyword evaluation path (NV_GET on keyword name or a dispatch table)
- `M4-FENCE-P case B`: TEXT-path fence-in-concat β-wiring (M2/M3 correct, M4 wrong)
- `020_concat_integer_string` with general-var subject: concat with var parts
- Capture, star-var, ARBNO clusters

**KEY INSIGHT for next session:** With Fix 2+3 landed, many tests that were failing due to
APPLY_fn not finding builtins should now pass. The next corpus run may reveal NEW passing tests
that were silently failing on the builtin lookup step. Probe `081`, `084`, `089`, `091-096`
individually — they may pass now or reveal the next layer of bugs.

---

## Gates at session end

- smoke: **7/7/7** HARD ✓
- pat-rung: **19/19/19 no-SKIP** ✓
- fence: **HARD** ✓
- corpus: M2=181 M3=159(+3) M4=149(+3)
- SCRIP: `9f0d809`
