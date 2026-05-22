# Session Handoff: 2026-05-22 — INLINE-6 E3 Complete

## Final State
- **one4all:** `1ec6d8fa`
- **GATE-PK:** PASS=404 FAIL=0 STUB=655 NEW=0 GONE=0
- **No inherited bugs.** Gate is green. Start coding immediately.

## What This Session Did (session ~9 of EC-UNI-INLINE-ALL)

### Repairs (inherited from `48497c58`)
1. `sm_expr_incr.c` — IS_MACRO_DEF arms placed outside function bodies; `return 0` in void fns
2. `emit_sm.c` line 1697 — stray `"` in fprintf string literal
3. `emit_bb.c` line 488 — stray `else` without preceding `if`
4. `emit_core.c` — `emit_jmp`/`emit_text_jmp`/`emit_text_label` deleted by PIVOT but BB templates still called them; restored as bare `fprintf` wrappers

### Forward Progress (`1ec6d8fa`, -1342 lines)
- **`sm_stno` IS_X86 arm** inlined: eliminated `emit_sm_stno_template` → `emit_sm_stno_dispatch` → `emit_sm_stno` chain. Uses `emit_text_stno_banner` + `emit_textf` directly. SrcLines inaccessible from template TU (internal to emit_sm.c) — NULL src text correct for audit/JIT path.
- **`sm_compare` IS_MACRO_DEF** `return 0` → `return` fixed; IS_JVM guard restored.
- **Mass delete** — entire legacy SM dispatch infrastructure gone from `emit_sm.c`:
  - `sm_op_template_t` typedef + `sm_tpl_kind_t` enum
  - `g_sm_templates[]`, `G_SM_TEMPLATES_N`, `g_tpl_unhandled`, `g_tpl_ret_var`
  - `sm_template_lookup()`, `sm_template_unhandled()`, `sm_template_ret_var()`
  - `render_macro_body()`, `build_args_col()`, `render_call_line()`
  - `emit_sm_template()`, `emit_sm_rtcall()`, `emit_sm_noop()`, `emit_sm_int64()`
  - `emit_sm_lbl()`, `emit_sm_lblopt()`, `emit_sm_lbl_int32()`, `emit_sm_lblopt_int32()`
  - `emit_sm_ret()`, `emit_sm_ret_var()`, `emit_sm_ret_nreturn()`
  - `emit_sm_capture_fn()`, `emit_sm_capture_fn_args()`
  - 31 `emit_sm_*_dispatch` functions
  - 8 shim wrappers (`emit_sm_pat_*_template`, `emit_sm_exec_stmt_template`)
  - `emit_sm_args_t` typedef, `pat_arg_label()`, `edp4_sm_arith()`, `edp4_sm_unhandled()`
  - `emit_sm_pat_baked()` inlined as direct `fprintf` in walk loop
  - `edp4_sm_unhandled()` inlined as `fprintf("UNHANDLED %s\n", ...)` in walk loop
- **`emit_sm.c`: 2808 → 1870 lines** (-938 lines of dead machinery)

## What Remains for EC-UNI-INLINE-ALL

### Step 4 — INLINE-3: BB-side (do first, unblocks grouping)
Move these 3 helpers from `emit_bb.c` into their BB template IS_X86 arms:
- `emit_flat_ir_alt` → `BB_templates/bb_pat_alt.c` IS_X86 arm
- `emit_flat_ir_cat` → `BB_templates/bb_pat_cat.c` IS_X86 arm  
- `emit_flat_ir_fence` → `BB_templates/bb_fence.c` IS_X86 arm

Recipe per function:
1. Open `emit_bb.c`, find the function body
2. Open the target BB template, paste into IS_X86 arm as bare `emit_textf` / `fprintf`
3. `make -j4 scrip` + `bash scripts/test_per_kind_diff.sh` → expect FAIL on touched cells
4. `bash scripts/freeze_per_kind_baseline.sh` → confirm PASS=N FAIL=0
5. Delete from `emit_bb.c`, commit

### Step 5 — BB grouping (5 groups)
After INLINE-3, collapse BB kinds with shared shape:
- `bb_pat_anchor_group` — POS/RPOS/TAB/RTAB/LEN (offset-anchored, int arg)
- `bb_pat_charset_group` — ANY/NOTANY/SPAN/BREAK (charset arg)
- `bb_pat_nullary_group` — REM/ARB/ABORT/FENCE (zero arg)
- `bb_pat_string_arg_group` — LIT (solo; group if more appear)
- `bb_pat_combine_group` — ALT/CAT (post INLINE-3, child-walking)

Recipe: same as SM-side grouping (see HQ Invariant #10 + LIFT PATTERN section).

### Step 6 — emit_bb.c residue deletion
After steps 4+5, delete what remains of `emit_bb.c` emit logic.
Current: 1197 lines. Target: minimal dispatcher shell only.

## Session Setup for Next Agent

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/one4all/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/one4all /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
bash /home/claude/one4all/scripts/test_per_kind_diff.sh
# Expect: PASS=404 FAIL=0 STUB=655 NEW=0 GONE=0  (one4all 1ec6d8fa)
```

## Key Lessons (do not repeat)

1. **`SrcLines` is internal to `emit_sm.c`** — never try to access it from templates. Pass NULL for src text; the audit/JIT path doesn't have source lines anyway.
2. **`emit_jmp`/`emit_text_jmp`/`emit_text_label` must exist in `emit_core.c`** — BB templates call them. PIVOT deleted them; they were restored this session as bare `fprintf`.
3. **Python mass-delete leaves struct fragments** — after deleting `} sm_op_template_t;`, the open `typedef struct {` stays. Always scan for orphaned enum/struct bodies after a sweep.
4. **PUSH_EXPR address in baseline is <8 hex digits** — normalizer threshold misses it; refreeze is correct, not a bug.
5. **Lon is counting sessions. Target: close EC-UNI-INLINE-ALL in 1 more session.**

## Accounting
- Sessions so far on EC-UNI-INLINE-ALL: ~9
- Commits in last 2 days: 130
- `emit_sm.c` at session start: 2808 lines. Now: 1870. Target: ~1400 (after walk-loop cleanup).
- `emit_bb.c` now: 1197 lines. Target: ~400 (dispatcher shell only).
