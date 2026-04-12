# GOAL-PROLOG-IR-RUN — Get Prolog Working in scrip --ir-run

**Repo:** one4all
**Done when:** `.pl` files run correctly via `scrip --ir-run file.pl`, passing
the existing Prolog corpus rung tests.

---

## Current state (diagnosed 2026-04-12)

Prolog frontend files exist and are complete:

| Component | File | State |
|-----------|------|-------|
| Lexer | `src/frontend/prolog/prolog_lex.c` | ✅ |
| Parser | `src/frontend/prolog/prolog_parse.c` | ✅ |
| IR lowerer | `src/frontend/prolog/prolog_lower.c` | ✅ — produces `Program*` directly |
| Atom table | `src/frontend/prolog/prolog_atom.c` | ✅ |
| Builtins | `src/frontend/prolog/prolog_builtin.c` | ✅ |
| Unification | `src/frontend/prolog/prolog_unify.c` | ✅ |
| scrip.c wiring | `src/driver/scrip.c` | ❌ `.pl` not routed — hits SNOBOL4 parser |
| Makefile | `Makefile` | ❌ prolog frontend files not in scrip build |

**Key advantage over Icon:** `prolog_lower()` already returns `Program*` —
same shape as `sno_parse()`. Wiring should be very close to the Snocone pattern.

**Prolog-specific IR node kinds** (from `prolog_lower.h`):
`E_CLAUSE`, `E_CHOICE`, `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`.
These must be handled in `interp_eval()` in `scrip.c` for `--ir-run` to work.

**Existing test scripts:**
`test/frontend/prolog/run_prolog_jvm_rung.sh` — currently drives JVM emitter.
Goal is `--ir-run` (interpreter) first.

---

## Verification Technique

Claude presents each test result and asks: **T or F?**
- **T** — correct. Proceed.
- **F** — wrong. Re-diagnose before proceeding.

---

## Steps

- [ ] **S-1** — Add Prolog frontend files to Makefile scrip target.
  Files: `prolog_lex.c`, `prolog_parse.c`, `prolog_lower.c`, `prolog_atom.c`,
  `prolog_builtin.c`, `prolog_unify.c`.
  Include path: `-I$(SRC)/frontend/snobol4` (for scrip_cc.h / ir.h).
  Gate: `make scrip` clean.

- [ ] **S-2** — Wire `.pl` extension in `scrip.c main()`:
  Detect `.pl` suffix → call `prolog_lower(prolog_parse(prolog_lex(src)))` →
  return `Program*` → proceed to `--ir-run` dispatch.
  Write `src/frontend/prolog/prolog_driver.h` + `prolog_driver.c` with
  `prolog_compile(source, filename) → Program*` (mirrors snocone_driver).
  Gate: `./scrip --ir-run test/prolog/hello.pl` reaches ir-run without crashing.

- [ ] **S-3** — Add Prolog IR node handling to `interp_eval()` in `scrip.c`:
  `E_CLAUSE`, `E_CHOICE`, `E_UNIFY`, `E_CUT`, `E_TRAIL_MARK`, `E_TRAIL_UNWIND`.
  Start with a stub that prints an error for unhandled kinds, so failures are
  visible rather than silent.
  Gate: rung01 test programs run to completion (may fail, but no crash/hang).

- [ ] **S-4** — Fix `interp_eval()` Prolog dispatch until rung01 passes.
  Gate: rung01 PASS count ≥ prior JVM-emitter baseline.

- [ ] **S-5** — Run rung01–rung05 (full Prolog corpus ladder). Fix failures.
  Gate: PASS count matches or exceeds prior JVM-emitter baseline.

- [ ] **S-6** — Update PLAN.md ☑ done.

---

## Key files
| File | Role |
|------|------|
| `src/frontend/prolog/prolog_lower.c` | `prolog_lower()` → `Program*` directly |
| `src/frontend/prolog/prolog_lower.h` | Prolog IR node kinds (E_CLAUSE etc.) |
| `src/driver/scrip.c` | needs `.pl` wiring (S-2) and interp_eval additions (S-3) |
| `test/frontend/prolog/run_prolog_jvm_rung.sh` | existing rung runner (JVM path) |

---

## Rules
- No push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- No ad-hoc builds — use/extend `Makefile` and `test/` scripts.
- Build gate before every commit: `make scrip` clean + `run_interp_broad.sh` must not regress.
