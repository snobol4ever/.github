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
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations (DYN-23 ✅ frozen) |
| `src/driver/scrip-interp.c` | M-INTERP-A01: tree-walk interpreter driver (TODO) |
| `src/runtime/dyn/bb_test.c` | M-INTERP-B01: per-box unit test harness (TODO) |

## ARCH-byrd-dynamic.md — grep, don't cat

Relevant sections by task:

| Task | Section to grep |
|------|----------------|
| emit_pat_to_descr nodes | `## M-DYN-S1 Implementation Plan` |
| stmt_exec_dyn phases | `## The SNOBOL4 Statement` |
| E_SEQ/E_CONCAT unification | `## M-DYN-SEQ` |
| Static .s must call stmt_exec_dyn | `## Static .s Path Must Also Use Five Phases` |
| Anonymous inline constants | `## Anonymous Inline Pattern Constants` |

## §NOW — DYN-23

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-23 | one4all `27300c5` · .github (this) · corpus `31ad542` | **M-DYN-OPT** (wire Pass 2b + preamble), then **M-INTERP-A01** (scrip-interp + bb_test) |

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

## §NOW — DYN-26

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-26 | one4all `61639ca` · .github (this) | **M-INTERP-A03**: wire DEFINE/call-stack → fix 083–090 cluster → broad ≥85p |

## scrip-interp build command (M-INTERP-A01 baseline)

```bash
cd /home/claude/one4all
ROOT=$(pwd); RT="$ROOT/src/runtime"; DYN="$RT/boxes"; DYNENG="$RT/dyn"
SCRIP_CC_INC="$ROOT/src"
DYNFLAGS="-I$DYN -I$RT/snobol4 -I$RT -I$SCRIP_CC_INC -DDYN_ENGINE_LINKED"

mkdir -p /tmp/ib
gcc -O2 -c "$RT/snobol4/snobol4.c"         -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/snobol4.o
gcc -O2 -c "$RT/snobol4/snobol4_pattern.c" -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/pat.o
gcc -O2 -c "$RT/mock/mock_engine.c"         -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/mock_eng.o
gcc -O2 -c "$RT/asm/snobol4_stmt_rt.c"     -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/stmt_rt.o
gcc -O2 -c "$RT/asm/x86_stubs_interp.c"    -o /tmp/ib/x86_stubs.o
for f in bb_lit bb_alt bb_seq bb_arbno bb_pos bb_rpos bb_tab bb_rtab bb_fence bb_abort \
          bb_len bb_span bb_any bb_notany bb_brk bb_breakx bb_arb bb_rem bb_succeed bb_fail bb_eps bb_bal; do
  gcc -O2 -c "$DYN/${f}.c" $DYNFLAGS -w -o /tmp/ib/${f}.o
done
gcc -O2 -c "$DYNENG/stmt_exec.c" $DYNFLAGS -w -o /tmp/ib/stmt_exec.o
gcc -O2 -c "$DYNENG/eval_code.c" $DYNFLAGS -w -o /tmp/ib/eval_code.o

gcc -O0 -I src -I "$RT/snobol4" -I "$RT" -I "$RT/boxes" -I "$RT/dyn" -DDYN_ENGINE_LINKED \
    src/driver/scrip-interp.c \
    src/frontend/snobol4/lex.o src/frontend/snobol4/parse.o \
    /tmp/ib/*.o -lgc -lm -o scrip-interp
```

## M-INTERP-A02 first task — wire pattern nodes in interp_eval

The 28 broad-set failures are all E_CAPT_* / E_ALT nodes falling through to `default: return NULVCL`.
Add cases to `interp_eval` switch in `scrip-interp.c`:

```c
case E_ALT: {
    /* children[0] | children[1] | ... — build pat_alt chain */
    if (e->nchildren == 0) return NULVCL;
    DESCR_t acc = interp_eval(e->children[0]);
    for (int i = 1; i < e->nchildren; i++)
        acc = pat_alt(acc, interp_eval(e->children[i]));
    return acc;
}
case E_CAPT_COND: {
    /* pat . var — conditional assignment on match */
    DESCR_t pat  = interp_eval(e->children[0]);
    DESCR_t var  = interp_eval(e->children[1]);  /* E_VAR → name */
    const char *nm = (e->nchildren>1 && e->children[1]->sval)
                     ? e->children[1]->sval : NULL;
    return nm ? pat_capture(pat, nm) : pat;
}
case E_CAPT_IMM: {
    /* pat $ var — immediate assignment */
    DESCR_t pat = interp_eval(e->children[0]);
    const char *nm = (e->nchildren>1 && e->children[1]->sval)
                     ? e->children[1]->sval : NULL;
    return nm ? pat_imm_assign(pat, nm) : pat;
}
case E_CAPT_CUR: {
    /* @var — cursor capture */
    const char *nm = (e->nchildren>0 && e->children[0]->sval)
                     ? e->children[0]->sval : NULL;
    return nm ? pat_at_cursor(nm) : NULVCL;
}
```

Check `pat_alt`, `pat_capture`, `pat_imm_assign`, `pat_at_cursor` signatures in
`src/runtime/snobol4/snobol4_pattern.c` before using — names may differ slightly.
Gate: 60+ of the 65p+28f broad tests should now pass.
