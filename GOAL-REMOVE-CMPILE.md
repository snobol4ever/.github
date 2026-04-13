# GOAL-REMOVE-CMPILE — Remove CMPILE.c from the build

**Repo:** one4all
**Done when:** `CMPILE.c` and `CMPILE.h` are never compiled or linked.
They remain on disk as historical artifacts. `make scrip` clean. No regression.

---

## Problem

`CMPILE.c` is a hand-written recursive-descent SNOBOL4 parser — a faithful C
translation of the SIL v311 CMPILE procedure. It predates the Bison/Flex parser
(`snobol4.y` / `snobol4.lex.c`) which is now the authoritative execution path.

CMPILE was used in three ways:
1. `--dump-parse` / `--dump-ir` diagnostics in `scrip.c` — **migrated** to Bison path
2. `CODE()` builtin in `eval_code.c` via `cmpile_string` + `cmpile_lower` — **open**
3. `cmpile_lower()` in `scrip.c` — **deleted** (moved into `eval_code.c`)

The CMPILE parser emits `E_FNC` for pattern primitives rather than typed IR nodes
(`E_ANY`, `E_SPAN`, etc.) — this is the core architectural debt that motivated
the `GOAL-SNOBOL4-PAT-IR` goal. As long as CMPILE is in the build it creates
confusion about which parser is authoritative.

## Session 2026-04-13 progress

DONE:
- `cmpile_lower()` removed from `scrip.c`, moved into `eval_code.c` as static
- `scrip.c` `--dump-parse` / `--dump-ir` branches rewired to use `sno_parse` (Bison)
- `#include "CMPILE.h"` removed from `scrip.c`
- `cmpile_init()` / `cmpile_add_include()` calls removed from `scrip.c`
- `scrip.c` default execution mode comment corrected to `--ir-run`
- `make scrip` clean; smoke PASS

OPEN: `eval_code.c` still `#include`s `CMPILE.h` and calls `cmpile_string()` /
`cmpile_free()`. The `CODE()` builtin depends on CMPILE for parsing
dynamically-evaluated SNOBOL4 strings. This is the last live use.

---

## Steps

- [x] **S-1** — Remove `cmpile_lower()` from `scrip.c`; move into `eval_code.c` as static.
  Gate: `make scrip` clean.

- [x] **S-2** — Rewire `scrip.c` `--dump-parse` / `--dump-ir` to use Bison path (`sno_parse`).
  Remove `cmpile_init()` / `cmpile_add_include()` calls. Remove `#include "CMPILE.h"`.
  Gate: `make scrip` clean; `--dump-ir-bison` still works.

- [ ] **S-3** — Wire `CODE()` builtin in `eval_code.c` to use `sno_parse` via a
  string-to-FILE* adapter (e.g. `fmemopen` or a temp-file path), eliminating
  `cmpile_string()` / `cmpile_free()` / `#include "CMPILE.h"` from `eval_code.c`.
  Gate: `make scrip` clean; `CODE()` corpus tests still PASS.

- [ ] **S-4** — Remove `CMPILE.c` and `CMPILE.h` from the Makefile (if present) and
  confirm they are not referenced by any compiled translation unit.
  Gate: `grep -r 'CMPILE' src/ | grep -v 'CMPILE\.\(c\|h\):' | grep -v '\.o:'` → zero hits.

- [ ] **S-5** — Full regression: `bash test/run_interp_broad.sh`.
  Gate: PASS count ≥ pre-goal baseline.

- [ ] **S-6** — Update PLAN.md ☑ done.

---

## Rules
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- `CMPILE.c` and `CMPILE.h` stay on disk — do not delete them.

---

## Session 2026-04-13 (this session)

Done in scrip.c / eval_code.c:
- `cmpile_lower()` removed from `scrip.c`, moved as static into `eval_code.c`
- `scrip.c` `--dump-parse` / `--dump-ir` rewired to `sno_parse` (Bison path)
- `cmpile_init()` / `cmpile_add_include()` calls removed from `scrip.c`
- `#include "CMPILE.h"` removed from `scrip.c`
- `make scrip` clean; smoke PASS (ir-run, sm-run)
- one4all HEAD: 99ef4a3d
