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
| `src/runtime/boxes/bb_*.java` | Java ports of all 25 boxes + bb_executor.java (J-217 ✅) — oracle for JVM backend; M-INTERP-B03 test target |
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

## §NOW — DYN-50

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **DYNAMIC BYRD BOX** | DYN-50 | one4all `16e820a` · corpus `2f2bbe3` | **DYN-51**: Fix remaining 17 failures → ≥125p. word*/cross (&TRIM/INPUT), expr_eval (line-continuation), 1012/1013 (locals/NRETURN), 1015 (OPSYN), 1016 (EVAL). Then MONITOR diff vs SPITBOL → 169p/9f. |

**Broad baseline: 115p/17f** (DYN-50 r1: scrip-interp build fixed + 5 lexer/parser fixes).

Remaining failures: `1013/003` · `1015_opsyn` · `1016_eval` · `cross` · `expr_eval` · `test_case` · `test_math` · `test_stack` · `test_string`
## scrip-interp build command

```bash
cd /home/claude/one4all
ROOT=$(pwd); RT="$ROOT/src/runtime"; BOXES="$RT/boxes"; DYN="$RT/dyn"
SCRIP_CC_INC="$ROOT/src"
DYNFLAGS="-I$BOXES/shared -I$RT/snobol4 -I$RT -I$SCRIP_CC_INC -DDYN_ENGINE_LINKED"

mkdir -p /tmp/ib
gcc -O2 -c "$RT/snobol4/snobol4.c"         -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/snobol4.o
gcc -O2 -c "$RT/snobol4/snobol4_pattern.c" -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/pat.o
gcc -O2 -c "$RT/mock/mock_engine.c"         -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/mock_eng.o
gcc -O2 -c "$RT/asm/snobol4_stmt_rt.c"     -I"$RT/snobol4" -I"$RT" -I"$SCRIP_CC_INC" -w -o /tmp/ib/stmt_rt.o
gcc -O2 -c "$RT/asm/x86_stubs_interp.c"    -o /tmp/ib/x86_stubs.o
# Boxes now live in per-box subdirs: src/runtime/boxes/<name>/bb_<name>.c
for box in lit alt seq arbno pos rpos tab rtab fence abort \
           len span any notany brk breakx arb rem succeed fail eps bal \
           atp capture dvar not interr; do
  f="$BOXES/$box/bb_${box}.c"
  [ -f "$f" ] && gcc -O2 -c "$f" $DYNFLAGS -w -o "/tmp/ib/bb_${box}.o"
done
gcc -O2 -c "$DYN/stmt_exec.c" $DYNFLAGS -w -o /tmp/ib/stmt_exec.o
gcc -O2 -c "$DYN/eval_code.c" $DYNFLAGS -w -o /tmp/ib/eval_code.o

gcc -O0 -I src -I "$RT/snobol4" -I "$RT" -I "$BOXES/shared" -I "$RT/dyn" -DDYN_ENGINE_LINKED \
    src/driver/scrip-interp.c \
    src/frontend/snobol4/lex.o src/frontend/snobol4/parse.o \
    /tmp/ib/*.o -lgc -lm -o scrip-interp
```

*(Box paths updated for SJ-5 reorg — one subfolder per box under `src/runtime/boxes/`.)*



## Known open issues

- `$.var` (210/212): `$'literal'` works; `$.var` fails — child node kind not yet traced.
- word*/cross: not `&alphabet`; likely `&TRIM` or `INPUT` reading.
- rung11 ARRAY/DATA: builtins registered; dispatch or arg-passing is the bug.
- patterns 048/056/057: E_REM/star-deref/FAIL-builtin not wired in `interp_eval`.
- capture 060/063: multiple captures / null-replace edge cases.
- rung10 1010–1018: recursion/NRETURN/OPSYN/EVAL/APPLY — deeper call-stack.
