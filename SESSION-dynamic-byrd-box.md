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
| `src/driver/scrip-interp.c` | tree-walk interpreter (M-INTERP-A01 ✅) |
| `src/runtime/dyn/bb_test.c` | per-box unit test harness (M-INTERP-B01 TODO) |

## ARCH-byrd-dynamic.md — grep, don't cat

| Task | Section to grep |
|------|----------------|
| emit_pat_to_descr nodes | `## M-DYN-S1 Implementation Plan` |
| stmt_exec_dyn phases | `## The SNOBOL4 Statement` |
| E_SEQ/E_CONCAT unification | `## M-DYN-SEQ` |
| Static .s must call stmt_exec_dyn | `## Static .s Path Must Also Use Five Phases` |
| Anonymous inline constants | `## Anonymous Inline Pattern Constants` |

## §NOW — DYN-29

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-29 | one4all `eb273e1` · .github `4df1169` · corpus `d5058ef` | **DYN-30**: debug word*/cross/$.var · fix REM/capture/rung11-ARRAY · target ≥130p broad |

## scrip-interp build command

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

## DYN-30 first tasks (in order)

1. **Build scrip-interp** — use build command above. Baseline one4all `eb273e1`.
2. **Run gate** — `CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86` → must be 142/142.
3. **Run broad** — inline runner in SESSIONS_ARCHIVE.md §DYN-29. Expect 120p/25f.
4. **Debug strings/word1** — `./scrip-interp corpus/crosscheck/strings/word1.sno < corpus/crosscheck/strings/word1.input 2>&1` vs `.ref` — isolate `&TRIM`/`INPUT`/pattern issue.
5. **Debug rung2/210 `$.var`** — printf in `interp_eval` E_INDR: print `e->children[0]->kind`. Likely `E_FIELD` or different parser node.
6. **Fix rung11 ARRAY/DATA** — `./scrip-interp corpus/crosscheck/rung11/1110_array_1d.sno 2>&1` vs `.ref`; check `_b_ARRAY` arg passing.
7. **Fix patterns/048 REM** — add `E_REM` case in `interp_eval` → `pat_rem()`.
8. **Broad re-run** → target ≥130p. **Gate**: snobol4_x86 142/142.

## Known open issues

- `$.var` (210/212): `$'literal'` works; `$.var` fails — child node kind not yet traced.
- word*/cross: not `&alphabet`; likely `&TRIM` or `INPUT` reading.
- rung11 ARRAY/DATA: builtins registered; dispatch or arg-passing is the bug.
- patterns 048/056/057: E_REM/star-deref/FAIL-builtin not wired in `interp_eval`.
- capture 060/063: multiple captures / null-replace edge cases.
- rung10 1010–1018: recursion/NRETURN/OPSYN/EVAL/APPLY — deeper call-stack.
