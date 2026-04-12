# GOAL-ICON-IR-RUN — Get Icon Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.icn` files run correctly via `scrip --ir-run file.icn`, passing
the existing Icon corpus rung tests.

---

## Current state (diagnosed 2026-04-12)

Icon frontend files exist and are complete:

| Component | File | State |
|-----------|------|-------|
| Lexer | `src/frontend/icon/icon_lex.c` | ✅ |
| Parser | `src/frontend/icon/icon_parse.c` | ✅ |
| IR lowerer | `src/frontend/icon/icon_lower.c` | ✅ — produces `EXPR_t**` (one per procedure) |
| Driver | `src/frontend/icon/icn_main.c` | ✅ — originally standalone, needs wiring |
| Emitter (x64/JVM/WASM) | `src/backend/emit_x64.c` etc. | ✅ — emit path exists |
| scrip.c wiring | `src/driver/scrip.c` | ❌ `.icn` not routed — hits SNOBOL4 parser |
| Makefile | `Makefile` | ❌ icon frontend files not in scrip build |

**Key difference from Snocone:** `icon_lower_file()` returns `EXPR_t**` (array of
procedure trees), NOT `Program*`. The ir-run interpreter expects `Program*`.
Need a thin wrapper: allocate `Program*`, walk `EXPR_t**` procedures, wrap each
as a `STMT_t`, link into `prog->head`.

**Existing test scripts** (use emitter path, not ir-run):
`test/frontend/icon/run_rung01.sh` … `run_rung36.sh` — these currently drive
`scrip --jit-emit --x64`. Goal is to make `--ir-run` work first (simpler).

---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

- [ ] **S-1** — Add Icon frontend files to Makefile scrip target.
  Files: `icon_lex.c`, `icon_parse.c`, `icon_lower.c`, `icon_ast.c`,
  `icon_runtime.c`, `icn_main.c`.
  Include path: `-I$(SRC)/frontend/snobol4` (for scrip_cc.h).
  Gate: `make scrip` clean.

- [ ] **S-2** — Write `src/frontend/icon/icon_driver.h` + `icon_driver.c`:
  ```c
  Program *icon_compile(const char *source, const char *filename);
  ```
  Pipeline: `icn_lex_init()` → `icon_parse_file()` → `icon_lower_file()` →
  wrap `EXPR_t**` into `Program*` (one `STMT_t` per procedure, kind=`E_FNC` or
  a new `E_ICON_PROC` wrapper — confirm with existing ir-run dispatch).
  Gate: `icon_compile()` returns non-NULL on a trivial `.icn` program.

- [ ] **S-3** — Wire `.icn` extension in `scrip.c main()`:
  Detect `.icn` suffix → call `icon_compile()` → proceed to `--ir-run` dispatch.
  Gate: `./scrip --ir-run test/icon/hello.icn` produces output.

- [ ] **S-4** — Run rung01 tests via `--ir-run`. Fix any ir-run dispatch gaps
  (Icon-specific IR node kinds not handled in `interp_eval()`).
  Gate: rung01 PASS count ≥ prior emitter baseline.

- [ ] **S-5** — Run rung01–rung11 (full corpus ladder). Fix failures.
  Gate: PASS count matches or exceeds prior emitter-path baseline.

- [ ] **S-6** — Update PLAN.md ☑ done.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/icon/icon_lower.c` | `icon_lower_file()` → `EXPR_t**` |
| `src/frontend/icon/icn_main.c` | old standalone driver — reference |
| `src/driver/scrip.c` | needs `.icn` wiring (S-3) |
| `test/frontend/icon/run_rung01.sh` … | existing rung runners |
| `corpus/crosscheck/` (Icon rungs) | test programs |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- SPITBOL is oracle for SNOBOL4; for Icon use existing `.ref` files in corpus.
- No ad-hoc builds — use/extend `Makefile` and `test/` scripts.
