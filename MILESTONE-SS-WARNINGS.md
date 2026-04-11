# MILESTONE-SS-WARNINGS.md — Silly SNOBOL4: Zero Warnings

**Goal:** `gcc -Wall -Wextra -std=c99` produces zero warnings on all `src/silly/*.c`.  
**Baseline:** 48 warnings (2026-04-11, one4all `22e1bd79`)  
**Gate:** `gcc -Wall -Wextra -std=c99 -g -O0 src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep "warning:" | wc -l` → 0

---

## Warning Inventory (baseline)

| Count | File | Warning | Fix |
|-------|------|---------|-----|
| 36 | platform.c | `-Wmissing-braces` — DESCR_t array initialisers like `{0}` instead of `{{0}}` | Add inner braces: `{.a={.i=0},.f=0,.v=0}` or cast |
| 1 | platform.c | `-Wunused-const-variable` — `FRZNSTR` defined but not used | Remove or use it |
| 1 | argval.c:257 | `-Wimplicit-function-declaration` — `INTR1_fn` undeclared | Forward-declare in errors.h or argval.c |
| 1 | interp.c:208 | `-Wimplicit-function-declaration` — `chk_break` undeclared | Forward-declare or move declaration |

---

## Fix Plan (one commit per category)

1. **platform.c missing-braces** — replace `{0}` initialisers in DESCR_t arrays with `{{0}}` or `ZEROD`
2. **platform.c FRZNSTR unused** — remove the definition (or add `(void)FRZNSTR` if needed)
3. **argval.c INTR1_fn** — add `void INTR1_fn(void);` to errors.h
4. **interp.c chk_break** — add forward declaration at top of interp.c

---

## Status

| Fix | Status |
|-----|--------|
| platform.c missing-braces (36) | ⬜ |
| platform.c FRZNSTR unused (1) | ⬜ |
| argval.c INTR1_fn implicit (1) | ⬜ |
| interp.c chk_break implicit (1) | ⬜ |

**Priority:** after M-SS-STUBS (implement stubs first, then silence warnings).
