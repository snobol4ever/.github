# FINDING — CURE LANDED: `insert(set, v1, v2, v3)` stored `v2` as the element instead of ignoring
# it (Icon's documented behavior: only the first value is ever inserted). Root-caused to a condition
# ordering bug in the shared table/set builtin dispatch — sets are tables with an `is_set` flag, and
# the `nargs >= 3` branch took priority over that flag instead of the other way around. One-line fix,
# full control battery clean (including a SNOBOL4 control arm that directly exercises the same
# dispatch file's non-set table logic). Landed.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (Class C, second cure landed this row
after `every`/list_bang_at).

## 1. The bug, confirmed against the witness before touching anything

`rung36_jcon_sets.icn:32`: `insert(x, 1, 4, 7)  # only inserts 1` — the source's own comment states the
intended Icon behavior. `.expected` shows the set containing `1` after this call; SCRIP produced `4`.
Full-file diff: exactly this one class of mismatch, repeating across every subsequent line that reads
the set back (the wrong element propagates through the rest of the witness).

## 2. Root cause

Icon's `set` type has no dedicated tag in this runtime — it is a `DT_T` (table) with an `is_set` flag
on the underlying `tbl` struct, and set membership is tracked purely by KEY (insert stores the element
as both key and value, `table_set_descr_d(tbl, kd, kd)`, so "is this element present" reduces to "does
this key exist"). The dispatch for Icon's `insert()` builtin
(`try_call_builtin_by_name_bl`, `src/runtime/by_name_dispatch.c` — reached via the generic
`rt_call_arr_bl`/`rt_call_arr_impl` by-name call path, not a per-builtin compiled call, confirmed by
reading the emitted `.s` directly rather than guessing from source: the call site is
`call rt_call_arr_bl@PLT` with `"insert"` as a string literal argument):

```c
DESCR_t kd = (nargs >= 2) ? args[1] : NULVCL;
DESCR_t vd = (nargs >= 3) ? args[2] : ((td.tbl && td.tbl->is_set) ? kd : NULVCL);   // BEFORE
```

For `insert(x, 1, 4, 7)`: `nargs==4`, so the `nargs >= 3` arm wins unconditionally and `vd = args[2] =
4` — the `is_set` check in the `else` branch never runs, because it's only reachable when there are
fewer than 3 total arguments. A genuine table's `insert(T, k, v)` is meant to take exactly this shape
(3 args, `v` from `args[2]`), so the code is *correct for tables* and simply never asks whether it's
looking at a set before applying that rule.

## 3. The fix

```c
DESCR_t vd = (td.tbl && td.tbl->is_set) ? kd : ((nargs >= 3) ? args[2] : NULVCL);   // AFTER
```

Check `is_set` first. A real table's behavior is byte-identical (`is_set` false → same `nargs>=3`
fallback as before). Only set-inserts with 3+ total arguments change, and only to do what the language
already documents: ignore everything past the first value.

## 4. Verification

`make pristine`; Icon smoke 14/14 both modes; Icon rung suite board — `rung36_jcon_sets` now **XPASS**;
FAIL list confirmed **byte-identical** to the pre-fix baseline via exact-list diff (not a count check —
the discipline adopted after the `&level` near-miss earlier this row); SNOBOL4 corpus control arm
**1669/1669 both modes FAIL=0 MISSING=0 GATE OK** — this control arm is unusually direct here, since it
exercises this exact same dispatch file's table logic (SNOBOL4 tables are never `is_set`, so it
directly confirms the untouched branch stayed untouched). Re-checked the other 11 remaining Class-C
candidates against the fixed binary: unchanged, confirming the fix is scoped to exactly this cause.

## 5. State

SCRIP `a03c8345`. Its `.xfail` marker's stated reason (`"runs to completion... stdout does not
match... not further diagnosed"`) was accurate, unlike `every`'s misleading SIGSEGV-era marker — no
stale-reason angle here, straightforward promotion. Marker deleted (corpus).
