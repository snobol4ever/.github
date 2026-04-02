# SESSION-dynamic-byrd-box.md — DYNAMIC BYRD BOX (SNOBOL4 × x86)

**Session prefix:** DYN- · **Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86
**Deep reference:** `ARCH-byrd-dynamic.md` — open only when needed, grep sections, do NOT cat in full.

## The one-line model

Everything is `stmt_exec_dyn`. Pattern statements compile to:
subject-name → `emit_pat_to_descr` → `call stmt_exec_dyn` → `:S`/`:F`.
No inline NASM Byrd boxes. No named-pattern trampolines. One path.

## Key files

| File | Role |
|------|------|
| `src/backend/emit_x64.c` | Pattern statement emission, `emit_pat_to_descr`, VAR=pat-expr fix |
| `src/runtime/snobol4/snobol4_pattern.c` | `pat_*` constructors (already in runtime) |
| `src/runtime/snobol4/stmt_exec.c` | `stmt_exec_dyn` — five-phase executor |
| `src/runtime/asm/bb_pool.c` | mmap pool (M-DYN-0 ✅) |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives (M-DYN-1 ✅) |

## ARCH-byrd-dynamic.md — grep, don't cat

Relevant sections by task:

| Task | Section to grep |
|------|----------------|
| emit_pat_to_descr nodes | `## M-DYN-S1 Implementation Plan` |
| stmt_exec_dyn phases | `## The SNOBOL4 Statement` |
| E_SEQ/E_CONCAT unification | `## M-DYN-SEQ` |
| Static .s must call stmt_exec_dyn | `## Static .s Path Must Also Use Five Phases` |
| Anonymous inline constants | `## Anonymous Inline Pattern Constants` |

## §NOW — DYN-21

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-21 | one4all `9e1e769` · .github `5a62f5a` · corpus `31ad542` | **M-DYN-OPT**: invariance detection → static pre-build |

## DYN-21 first task — invariance detection

M-DYN-S1 ✅ — 142/142 gate passed.

Next milestone: M-DYN-OPT. Detect provably invariant patterns at emit time
(no XDSAR/XVAR/XATP/capture nodes in subtree) and emit a one-time pre-build
sequence in the program preamble instead of rebuilding on every stmt_exec_dyn call.
See ARCH-byrd-dynamic.md §M-DYN-OPT for the invariance detection spec.

## DYN-20 first task — one edit

**File:** `src/backend/emit_x64.c` line ~5050  
**Where:** `Case 1` VAR=expr handler, `} else { /* General path */` block  
**Fix:** split on `expr_is_pattern_expr(s->replacement)`:
- true → `emit_pat_to_descr(s->replacement)` + `SET_VAR` (no FAIL_BR — pat constructors don't fail)
- false → current path unchanged

**Also check:** `E_CAPT_CUR` in `emit_pat_to_descr` switch (~line 4281) — needed for `cross.sno` `@NH`/`@NV`.  
Check `pat_at_cursor` signature in `snobol4_pattern.c` first.

**Gate:** `CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86` → 142/142

**After gate:**
```bash
CELLS=snobol4_x86 CORPUS=/home/claude/corpus bash test/run_emit_check.sh --update
cd /home/claude/corpus && git add -A && git commit -m "regen: DYN-20 post M-DYN-S1 artifacts" && git push
```
