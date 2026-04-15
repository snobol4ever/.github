# GOAL-SNOCONE-BEAUTY — beauty.sc Self-Beautifies via scrip

**Repo:** one4all
**Done when:** `./scrip --ir-run test/beauty-sc/beauty/beauty.sc < input.sno`
produces output byte-for-byte identical to SPITBOL running `beauty.sno` on
the same input. Gate script reports PASS.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snocone.sh        # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh  # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh # PASS=36
```

---

## Current state (2026-04-15, one4all HEAD 6a63a77b)

All 14 beauty-sc subsystems PASS all 3 modes. beauty.sc itself does NOT run.

**Root cause:** `snocone_lower.c` hits stack underflow on constructs in beauty.sc
that the subsystem drivers don't use:

1. **`$'...'` dollar-quoted identifiers** — e.g. `$'=' = *White && '=' && *White;`
   The lexer treats `$` as an identifier character but does not tokenize `$'...'`
   as a quoted-name literal. The parser/lowerer never sees a valid lvalue.

2. **`*deref` in replacement position** — e.g. `ppArgs ? ('--' && *ppTokNamePat . ppTokName) = ;`
   Indirect pattern reference on the LHS of a replacement. The lowerer's
   expression stack underflows when it tries to pop the replacement target.

These are the two blockers. Fix them in order.

---

## Steps

- [ ] **SB-1** — Diagnose: confirm the two blockers above are the only lowerer
  failures. Add a `--parse-only` or line-number annotation to snocone_lower.c
  to print the offending statement before underflow. Run beauty.sc, collect
  all underflow sites, map to line numbers.
  Gate: list of failing constructs is complete and matches the two categories above.

- [ ] **SB-2** — Fix `$'...'` dollar-quoted identifier lexing.
  In `snocone_lex.c`: when lexer sees `$` followed immediately by `'`, read
  the quoted string content as the identifier name. Emit a NAME token whose
  spelling is e.g. `$=`, `$?`, `$|` etc.
  In `snocone_lower.c`: treat dollar-name tokens as ordinary variable names
  (they already are — just need the lexer to produce the right token).
  Gate: `$'=' = 'hello';  OUTPUT = $'=';` in a trivial .sc file prints `hello`.

- [ ] **SB-3** — Fix `*deref` in replacement context.
  `subject ?= *pat_var <- repl` and `subject ? (*pat_var . cap) = ;` forms.
  The lowerer must handle E_DEREF on the pattern side of a replacement stmt.
  Gate: a small .sc test using `*deref` replacement passes --ir-run.

- [ ] **SB-4** — Run beauty.sc on a trivial SNOBOL4 input, compare to SPITBOL oracle.
  ```bash
  echo '        X = 1' | ./scrip --ir-run test/beauty-sc/beauty/beauty.sc
  /home/claude/x64/bin/sbl -b /home/claude/one4all/test/beauty-sc/beauty/beauty.sno <<< '        X = 1'
  ```
  Gate: outputs match. (beauty.sno path TBD — may need corpus clone.)

- [ ] **SB-5** — Self-beautify: feed beauty.sc to itself, compare to SPITBOL oracle
  running beauty.sno on beauty.sc.
  Gate: diff is empty.

- [ ] **SB-6** — Write `scripts/test_snocone_beauty_self.sh`: end-to-end runner.
  Gate: PASS reported, integrated into CI.

- [ ] **SB-7** — Broker gate: `test_smoke_unified_broker.sh` PASS=36 FAIL=0.
  Commit. Push. Update PLAN.md ☑.

---

## Key constructs to fix

| Construct | Example | Fix location |
|-----------|---------|-------------|
| `$'...'` quoted identifier | `$'=' = *White && '=' && *White;` | `snocone_lex.c` |
| `*deref` in pattern/replacement | `ppArgs ? ('--' && *ppTokNamePat . cap) = ;` | `snocone_lower.c` |

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- SPITBOL is the oracle. .ref from `sbl -b`.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
