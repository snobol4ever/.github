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
bash /home/claude/one4all/scripts/test_smoke_snocone.sh              # PASS=5
bash /home/claude/one4all/scripts/test_beauty_snocone_all_modes.sh   # PASS=42 SKIP=3
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh       # PASS=44
```

---

## Architecture (TWO STEPS)

**Step 1 — .sno subsystem files + beauty.sc:**
scrip handles mixed-extension multi-file linkage natively. Pass subsystem
`.sno` files as libraries, `beauty.sc` as main program:

```bash
./scrip --ir-run \
    corpus/programs/snobol4/beauty/global.sno \
    ... \
    corpus/programs/snobol4/beauty/trace.sno \
    test/beauty-sc/beauty/beauty.sc < input.sno
```

Oracle: `smoke/beauty_oracle.sno` (NOT `demo/beauty.sno` — crashes error 021).

**Step 2 — Replace .sno subsystem files with .sc equivalents:**
Substitute from `corpus/programs/include-sc/` one by one, gate stays green.

---

## Current state (2026-04-16, one4all HEAD 311ec18c)

SB-1..SB-3 DONE.

NEXT STEP: SB-5 — diagnose why beauty.sc produces no output with .sno libs.
pat_cat warning from io.sno is suspect. beauty.sc main loop
`while (DIFFER(Line = INPUT))` may not be reading input.

---

## Steps

- [x] **SB-1** — Diagnose underflows.
- [x] **SB-2** — Fix $'...' lexer.
- [x] **SB-3** — Fix scan+replacement lowering. 0 underflows.
- [ ] **SB-5** — Fix: beauty.sc produces no output with .sno libs.
- [ ] **SB-6** — Self-beautify. Gate: diff empty.
- [ ] **SB-7** — Gate script. Commit. Push.

---

## Invariants

- Gate = PASS=36 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Oracle: corpus/programs/snobol4/smoke/beauty_oracle.sno
- Commit identity: LCherryholmes / lcherryh@yahoo.com.
