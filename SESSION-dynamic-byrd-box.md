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
    src/frontend/snobol4/snobol4.tab.o src/frontend/snobol4/snobol4.lex.o \
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

---

## DYN-58 Architecture Clarification (added 2026-04-03)

**Q: Does scrip-interp simulate Byrd box goto by calling bb_*.c functions?**
**A: YES — this is correct and by design.**

The execution path for pattern statements:

```
scrip-interp.c: interp_eval(s->pattern)
  → snobol4_pattern.c: pat_cat/pat_arb/pat_len/... → PATND_t tree (DT_P)
  → exec_stmt(subj_name, pat_d, ...)           [= stmt_exec_dyn]
  → stmt_exec.c: bb_build(PATND_t*)
      → bb_node_t { α fn*, β fn* }             [Byrd box C structs]
  → five-phase executor drives α/β ports        [Byrd goto via C fn ptrs]
```

`bb_node_t.α` and `bb_node_t.β` are C function pointers. `stmt_exec.c`
calls them directly — this IS the Byrd box protocol, implemented in C.
The `src/runtime/dyn/bb_*.c` files are the C implementations of each box.

**What was wrong in DYN-56/57/58:** `interp_eval` had a `pat_ctx` / `_expr_is_pat`
workaround in the `E_SEQ` handler trying to dispatch between `pat_cat` and
`CONCAT_fn` at eval time. This is the wrong layer. The correct fix is:
`interp_eval` for a pattern expression should always use `pat_cat` for
concatenation — the caller (`exec_stmt` path) already knows it is a pattern
context. Pass context down rather than inferring it in `interp_eval`.

**DYN-59 first action:** Remove `pat_ctx` / `_expr_is_pat` from `E_SEQ` handler.
Instead, add an `int in_pat_ctx` parameter to `interp_eval` (or a global flag
set before calling `interp_eval(s->pattern)`), so `E_SEQ` and `E_CAT` always
call `pat_cat` when evaluating a pattern expression. Then re-run corpus.

---

## M-DYN-PATGEN — Pattern BB Sequence Generation in Executable Area (added DYN-67)

**Motivation (from Lon, 2026-04-04):** We have DATA+EXE in memory working for simple cases. The pivot: instead of tree-walking patterns at match time, the interpreter should *generate* the Byrd box x86 sequences into the executable pool at pattern-build time. This validates the full bb_pool → bb_emit → bb_seal → call chain under real corpus load, and prepares the code-gen path for the compiler backend.

### What exists (✅)
- `bb_pool.c` — mmap RW slab, `bb_alloc/bb_seal/bb_free`, M-DYN-0 ✅
- `bb_emit.c` — dual-mode emitter, `bb_emit_byte/u32/u64/rel32`, label/patch system, M-DYN-1 ✅. All functions have `if (bb_emit_mode == EMIT_TEXT) { ... return; }` guards — binary branches are **empty stubs**.
- `src/runtime/boxes/*/bb_*.s` — 25 Byrd box implementations in NASM (used by scrip-interp-s via assembly)
- `stmt_exec.c` — `bb_build(PATND_t*)` → `bb_node_t` C structs, five-phase executor drives α/β ports via C function pointers

### What M-DYN-PATGEN adds
- **EMIT_BINARY branches in bb_emit.c**: fill in the raw x86-64 byte emission for each primitive (`bb_emit_byte`, `bb_emit_u32`, `bb_emit_rel32`, `bb_insn_call_rax`, `bb_insn_ret`, etc.)
- **`bb_build_binary(PATND_t*)`**: new function in `stmt_exec.c` or new `bb_build_bin.c` — walks a PATND_t tree and emits x86 bytes via `bb_emit_*` into a `bb_pool` buffer, then `bb_seal()` → RX. Returns an executable function pointer to the α port.
- **scrip-interp-s integration**: before calling `exec_stmt`, if pattern is invariant (no runtime captures), call `bb_build_binary` instead of `bb_build`. The returned α fn ptr is called directly — no C-struct dispatch overhead.
- **Gate**: all 178 broad corpus tests pass with `bb_build_binary` active for invariant patterns. Output identical to C-struct path.
- **Oracle**: the `.s` box files are the spec — `bb_build_binary` must produce semantically equivalent byte sequences.

### Milestone gate
- 178/178 broad corpus with EMIT_BINARY path active for ≥1 box type (LIT first, then extend)
- Two-way MONITOR: run failing test through both C-struct path and EMIT_BINARY path — diff must be empty

### First steps for DYN-68+ after M-DYN-INTERP-FULL
1. Fill in `bb_emit_byte/u32/rel32` binary branches — these are trivial (`memcpy` into pool buf)
2. Implement `bb_insn_call_imm64` — `mov rax, imm64 / call rax` (10 bytes) for calling C runtime fns
3. Write `bb_build_lit_binary(const char *s, int len)` — LIT box: α port checks subject[cursor..cursor+len] == s, advances cursor or jumps to ω
4. Test standalone with a hand-written subject: `bb_pool_alloc → emit LIT bytes → bb_seal → call α`
5. Wire into scrip-interp-s for E_QLIT pattern nodes → run corpus, compare vs C-struct path
