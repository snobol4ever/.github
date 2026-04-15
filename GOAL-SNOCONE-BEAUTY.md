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

## Current state (2026-04-15, one4all HEAD db91b92c)

SB-1 DONE: 9 underflow sites diagnosed — dollar-quoted idents + scan+replacement.
SB-2 DONE: $'...' lexer fix — both lex loops patched. Gate passes.
SB-3 DONE: ~(subj ? pat) parser fix + scan+replacement lowerer fix. 0 underflows.
beauty.sc runs to completion (no underflows). Next: SB-4 — compare output to oracle.

1. **`$'...'` dollar-quoted identifiers** — e.g. `$'=' = *White && '=' && *White;`
   The lexer treats `$` as an identifier character but does not tokenize `$'...'`
   as a quoted-name literal. The parser/lowerer never sees a valid lvalue.

2. **`*deref` in replacement position** — e.g. `ppArgs ? ('--' && *ppTokNamePat . ppTokName) = ;`
   Indirect pattern reference on the LHS of a replacement. The lowerer's
   expression stack underflows when it tries to pop the replacement target.

These are the two blockers. Fix them in order.

---

## Steps

- [x] **SB-1** — Diagnose: confirmed 9 underflow sites — two categories:
  (a) `$'...'` dollar-quoted identifiers (lines 477,489,517,523,525)
  (b) `subject ? pattern = ;` scan+replacement (lines 21,25,28,64).
  Added line-number annotation to es_pop() for diagnosis. one4all HEAD db91b92c.

- [x] **SB-2** — Fix `$'...'` dollar-quoted identifier lexing.
  snocone_lex.c: intercept `$'` before operator longest-match in both lex
  loops; emit SNOCONE_IDENT with spelling `$<content>` (e.g. `$=`, `$Id`).
  Gate: `$'=' = 'hello'; OUTPUT = $'=';` prints `hello`. ✅

- [x] **SB-3** — Fix scan+replacement lowering (two fixes):
  1. snocone_parse.c parse_operand_into: grouping paren now fully recurses
     into balanced interior via snocone_parse() — fixes `~(subject ? pat)`.
  2. snocone_lower.c SNOCONE_ASSIGN handler: detects empty-LHS postfix and
     builds E_ASSIGN(E_SCAN, empty-repl); assemble_stmt unwraps into proper
     scan+replacement STMT. Fixes `subject ? pat = ;` form.
  Gate: `s ? SPAN('abc') = ; OUTPUT = s;` prints `def`. ✅
  beauty.sc: 0 underflows (was 9). one4all HEAD db91b92c.

- [ ] **SB-4** — Run beauty.sc on a trivial SNOBOL4 input, compare to SPITBOL oracle.

  **IN PROGRESS (2026-04-15):** beauty.sc silently produces no output.
  Root cause diagnosed: Snocone parser silently fails on something inside
  `if (DIFFER(ppAutoMode)) {` block (lines 45–97), discarding rest of file.
  Binary search confirmed: lines 1–44 + sentinel fires; lines 1–45 + sentinel does not.
  Exact failing construct not yet pinpointed — use bisect script in HANDOFF file.
  Polyglot invocation (all .sno libs except ReadWrite + beauty.sc) is correct approach.
  ReadWrite.sno excluded: has unresolved `err` label (sm_lower bug); beauty.sc
  never calls Read() or Write() directly so exclusion is safe.
  See HANDOFF-SNOCONE-BEAUTY-SB4.md for exact next steps and bisect script.

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
