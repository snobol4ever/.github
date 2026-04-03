# MILESTONE-DYN-INTERP — scrip-interp: SNOBOL4 Tree-Walk Interpreter

**Session prefix:** DYN- · **Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** interp

---

## What it is

`scrip-interp` is a SNOBOL4 interpreter that reuses the existing frontend
(lex + parse → `Program*` IR) and executes statements by tree-walking the IR.
It serves two purposes:

1. **Fast corpus runner** — no compile/assemble/link overhead per test
2. **Debug tool** — run `.sno` programs directly, diff vs SPITBOL oracle

**Architecture (per ARCH-byrd-dynamic.md):**

- Non-pattern statements (assignment, arithmetic, I/O): evaluated directly
  by `interp_eval()` tree-walking the `EXPR_t` IR.
- **Pattern statements**: `interp_eval()` evaluates subject and pattern
  expressions using `snobol4_pattern.c` constructors (`pat_lit`, `pat_cat`,
  `pat_arb`, etc.) which return `DT_P` descriptors (live `PATND_t` trees).
  These are handed to **`stmt_exec_dyn()`** which calls **`bb_build()`** to
  assemble a Byrd box graph, then runs it through the five-phase executor
  (subject → build pattern → match → replacement → S/F branch).

This means `scrip-interp` DOES use Byrd boxes for pattern execution —
it just builds them at interpretation time rather than emitting static NASM.
The `interp_eval` pattern-expression path must NOT attempt to match patterns
directly; it must always route through `stmt_exec_dyn`.

---

## What already exists (reuse)

| Component | File | Status |
|-----------|------|--------|
| Lexer | `src/frontend/snobol4/lex.c` | ✅ shared |
| Parser | `src/frontend/snobol4/parse.c` | ✅ shared |
| Pattern constructors | `src/runtime/snobol4/snobol4_pattern.c` | ✅ shared |
| NV store (variables) | `src/runtime/snobol4/snobol4.c` | ✅ shared |
| Statement executor | `src/runtime/dyn/stmt_exec.c` | ✅ shared |
| bb_*.c boxes (25+) | `src/runtime/boxes/*/bb_*.c` | ✅ |
| Driver | `src/driver/scrip-interp.c` | ✅ 1090 lines |

---

## Milestone chain

| Milestone | Description | Gate | Status |
|-----------|-------------|------|--------|
| **M-INTERP-A01** | `scrip-interp` binary: parse + execute trivial programs | 20 corpus smoke tests pass | ✅ `200543f` DYN-25 |
| **M-INTERP-A02** | Pattern matching: E_ALT / E_CAPT_* wired | 60 corpus pattern tests pass | ✅ `61639ca` DYN-26 |
| **M-INTERP-A03** | DEFINE / call-stack / user functions | ≥130/142 match | ✅ `1ebaa02` DYN-27 |
| **M-INTERP-A04** | Broad corpus: 169p/9f — OPSYN alias, INDIRECT, ITEM, NRETURN 001/002 | 169/178 broad | ✅ `d411c48` DYN-41 |
| **M-INTERP-A05** | Fix remaining 9 failures → ≥175p broad | ≥175p broad · 142/142 gate | ⬜ DYN-42 next |
| **M-INTERP-B01** | `bb_test.c` per-box unit harness — 25/25 C boxes | 25/25 unit tests pass | ⬜ not started |
| **M-INTERP-B02** | Same harness vs `bb_*.s` objects — C/ASM parity | 25/25 `.s` boxes match `.c` | ⬜ not started |
| **M-INTERP-B03** | Same harness vs `bb_*.java` — Java/C parity | 25/25 Java boxes match `.c` | ⬜ not started — bb_*.java landed J-217 (`7c35456`) |

---

## M-INTERP-A05 — Remaining 9 failures

| Test | Root cause | Fix |
|------|-----------|-----|
| `1013_func_nreturn` 003 | NRETURN lvalue-assign: `ref_a() = 26` — parser doesn't see `(` after IDENT at NRETURN site | Option A: `skip_ws(lx)` in `parse_expr17` before `T_LPAREN` check |
| `1015_opsyn` | OPSYN operator interaction | Trace vs ref |
| `1016_eval` | EVAL edge cases | Trace vs ref |
| `cross`, `expr_eval` | DEFINE/named-pattern interaction | Trace vs ref |
| `test_case`, `test_math`, `test_stack`, `test_string` | scrip harness failures | Trace vs ref |

**DYN-42 approach for 1013/003:** Try Option A first (2-line parser change in
`parse_expr17` — `skip_ws(lx)` after consuming IDENT, before `T_LPAREN` check).
If it breaks anything, fall back to Option B (runtime guard in statement executor).

---

## Build command

```bash
cd /home/claude/one4all
gcc -O0 -g -I src -I src/frontend/snobol4 -I src/runtime/snobol4 \
    -I src/runtime/boxes/shared \
    src/driver/scrip-interp.c \
    src/frontend/snobol4/lex.c src/frontend/snobol4/parse.c \
    src/runtime/snobol4/snobol4.c src/runtime/snobol4/snobol4_pattern.c \
    src/runtime/dyn/stmt_exec.c src/runtime/dyn/eval_code.c \
    $(find src/runtime/boxes -name "bb_*.c") \
    -lgc -lm -o scrip-interp
```

(See `SESSION-dynamic-byrd-box.md §scrip-interp build command` for the
current exact flags — they may have evolved.)

---

## Routing

- **Session doc:** `SESSION-dynamic-byrd-box.md` (DYN- session)
- **Deep ref:** `ARCH-byrd-dynamic.md`
- **Related:** `MILESTONE-NET-INTERP.md` — .NET analogue (Pidgin + C# bb boxes)

---

*MILESTONE-DYN-INTERP.md — updated D-166, 2026-04-02, Claude Sonnet 4.6.*
*A01/A02/A03/A04 complete. A05 = DYN-42 next (9 remaining failures). B01/B02 not started.*
