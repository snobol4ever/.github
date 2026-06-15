# HANDOFF 2026-06-15 — Icon local-VAR builtin-call arg marshalling — ✅ LANDED (Claude)

**Goal:** GOAL-ICON-FULL-PASS — the `rung29_builtins_type_mixed` wrong-output bug ("`type(x)`/`image(x)` of a var → null/&null: builtin-call arg not marshalling the VAR value, arg DESCR uninitialised").
**Result:** LANDED & PUSHED. SCRIP commit = **`5f54227`** (on origin/main; rebased clean over concurrent Prolog landing `cedad93`, re-gated identical). The fix turned out to be a whole CLASS bug — it swept FIVE FAILs, not just the named target.

## Tally
m3 **133 → 138** · m4 **133 → 138** (+5 each). FAIL **23 → 18**. EXCISED 91 unchanged. XFAIL 36. Total 283. m3/m4 FAIL sets at parity.

FAIL→PASS (both modes):
- `rung29_builtins_type_mixed` — the named target. `type(x)` now → `integer`, `image(x)` → `100` (x=100).
- `rung22_lists_get`, `rung22_lists_pull` — were **rc=139 SEGFAULTS**.
- `rung31_sort_sort_already_sorted`, `rung31_sort_sort_every` — were **rc=139 SEGFAULTS**.

The four segfaults were the SAME root cause as the wrong-output: a local list/table VAR passed to `get`/`pull`/`sort` arrived as a garbage/uninitialised DESCR, and the runtime crashed dereferencing the bogus pointer. Fixing the marshal fixed all of them.

## Root cause
`bb_call_fn_str` (`bb_call.cpp`, the builtin-call template that calls `rt_call_arr`) pre-allocates a fresh 16-byte slot for EVERY arg:
```c
for (int i = 0; i < nargs; i++) { IR_t *ai = ...; bb_slot_alloc16(ai ? ai : pBB); }
```
For a bare local VAR arg that is NOT walked as a separate producer box (the builtin path fills the CALL box directly and marshals args itself — there is no `bb_var` box in the asm), this allocation is the ONLY thing that ever touches the VAR node's slot. It hands the VAR a fresh slot (e.g. `[r12+64]`) that NOTHING writes. Then `marshal_call_arg` line ~349 does `int ps = bb_slot_get(lf)` = 64 (≥0) → takes the "nested producer-box slot" path → marshals `[r12+64]`→`[r12+aoff]`, copying the uninitialised slot. `args[0]` arrives as `DT_SNUL` (tag 0). Meanwhile the VAR's actual value lives in its frame VARSLOT (where `x := 100`'s `bb_assign_local` box wrote it — `[r12+16]` in the repro).

`marshal_call_arg` ALREADY had the correct fallback for this (line ~357: `int voff = bb_varslot(lf->sval); load [r12+voff]`), but the phantom producer slot at line 349 intercepted it.

## The fix (1 line + 1 extern, `bb_call.cpp`)
- Added extern `int is_global(const char * name);`.
- Changed `int ps = bb_slot_get(lf);` to:
```c
int ps = (lf->op == IR_VAR && IR_LIT(lf).sval && IR_LIT(lf).sval[0] != '&' && !is_global(IR_LIT(lf).sval)) ? -1 : bb_slot_get(lf);
```
A bare LOCAL VAR arg (`IR_VAR`, has sval, not a `&keyword`, not a global) now forces `ps=-1`, so it falls through to the existing varslot path and reads `bb_varslot(name)` — the var's real frame home where its value lives. Globals (which carry their NV value in a real producer slot via `bb_var_global`), literals, and nested-call args are all untouched (the guard explicitly excludes globals; `is_global` keeps the global arm on the producer-slot path).

This is IR-shape dispatch (VAR vs not, local vs global by name property), not language-specific logic — `marshal_call_arg` already had a gvar-VAR arm and a varslot fallback. Adds ZERO emission code (only changes which existing path is taken).

## Verification
The repro asm marshal comment changed from `nested producer-box slot [r12+64] -> [r12+64]` (self-copy of an empty slot) to `varslot [r12+16] -> [r12+64]` (reads where `x := 100` wrote). Both modes verified by explicit FAIL-name AND EXCISED-name diffs: the diff is purely DELETIONS (5 FAILs gone), no new FAIL, no EXCISE→FAIL, EXCISED unchanged. m4 confirmed standalone (`--compile`→`as`→`gcc`→run prints `integer`/`100`/`8`).

Cross-language safety (`bb_call.cpp` is shared by SNOBOL4/Prolog/Raku call paths): **snobol4 7/7 m4**, prolog 5/5 m3+m4, icon 12/12 m3+m4. Gates: no-stack 0 · one-reg-frame 0 · FACT 0 · g_vstack 0 · bb_bin_t 0 · template-medium-invisible 0. Diff adds zero byte-producers.

## Key intel (reusable)
- A builtin call (`type`/`image`/`numeric`/`get`/`pull`/`sort`/…) whose arg is a bare local VAR does NOT emit a separate `bb_var` producer box — `bb_call_fn_str` marshals args inline. So the VAR node's slot is whatever `bb_call_fn`'s pre-alloc set, NOT its varslot. Any future "VAR arg to a direct-fill call" path must marshal from `bb_varslot`, not `bb_slot_get`.
- Symptom signature: a builtin returning `null`/`&null`/segfault for a VAR arg while a literal arg works = arg-marshal reading an unwritten slot. Check the `marshal arg%d = ...` asm comment: `varslot` good, `nested producer-box slot [r12+N] -> [r12+N]` (same N both sides) = the phantom-slot bug.

## Still open in this class (NOT fixed here)
- Global VAR arg to a direct-fill builtin (if it ever lacks its NV producer slot) is untouched by this fix — none in the current FAIL set, so not exercised. `image(cset)` for a cset LITERAL arg (`IR_CSET_LIT`) is a different marshal path (not in `marshal_call_arg`'s LIT cases) — also not in the current FAIL set.

**Author:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
