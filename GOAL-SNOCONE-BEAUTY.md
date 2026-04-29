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

## Current state (2026-04-29)

SB-1..SB-3 DONE.

SC sources live at `corpus/programs/snocone/demo/beauty/` (session #62, finalized).
Source modules at top level. Subsystem tests flat in `test/` as `test_<subsys>.sc` + `test_<subsys>.ref`.
Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.
Script paths updated in one4all. Gates green: PASS=5, PASS=42 SKIP=3, PASS=49.

NEXT STEP: SB-5 — beauty.sc produces no output with .sno libs. Development work
needed: identify which procedures in beauty.sc are incomplete/missing and implement them.

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

---

## Canonical destination — corpus/programs/snocone/demo/beauty/

SC sources live at `corpus/programs/snocone/demo/beauty/` as of session #62.
This is the permanent home.

**Naming distinction (decided in session-#NN with Lon):**

- **BEAUTY** — `demo/beauty/` — SNOBOL4 implementation reading SNOBOL4
  source. Self-host = beauty.sno reads its own .sno source.
- **BEAUTIFY** — `demo/beautify/` — Snocone implementation reading
  SNOBOL4 source. The implementation language is Snocone; the input
  and output language remain SNOBOL4. BEAUTIFY does NOT read or write
  Snocone code (yet — that would be a future BEAUTIFY-extended).

The BEAUTIFY self-host gate produces output matching the BEAUTY md5
`abfd19a7a834484a96e824851caee159` because both pretty-print the same
SNOBOL4 source. This auto-cross-checks the Snocone implementation
against the SNOBOL4 implementation.

**Move plan (when SB-5 is green):**

1. `git mv one4all/test/beauty-sc/beauty/` content into
   `corpus/programs/snobol4/demo/beautify/`. This includes
   `beauty.sc`, `Gen.sc`, `Qize.sc`, `TDump.sc`, `XDump.sc`,
   `case.sc`, `io.sc`, `omega.sc`, `driver.sc` (auto-assembled).
2. `git mv` each of the 14 subsystem folders
   (`arith/`, `assign/`, `counter/`, `fence/`, `global/`, `match/`,
   `roman/`, `semantic/`, `ShiftReduce/`, `ReadWrite/`, `stack/`,
   `strings/`, `trace/`, `tree/`) into the same `beautify/` —
   each carrying its `driver.sc` and `driver.ref`. These are the
   subsystem-level beauty regression tests.
3. Update path constants in:
   - `scripts/test_beauty_snocone_all_modes.sh` —
     `BEAUTY_DIR=$HERE/../test/beauty-sc` →
     `BEAUTY_DIR=$CORPUS/programs/snobol4/demo/beautify`
   - `scripts/test_beauty_snocone_subsystems.sh` — analogous
   - `scripts/util_run_beauty_sc.sh` —
     `DRIVER=$ROOT/test/beauty-sc/beauty/driver.sc` →
     `DRIVER=$CORPUS/programs/snobol4/demo/beautify/driver.sc`
   - `scripts/test_crosscheck_beauty_snocone.sh` — analogous
4. The `.ref` files in each subsystem are byte-identical to the
   BEAUTY oracle outputs (they should be — the Snocone driver
   produces the same SNOBOL4-formatted output). RULES.md
   self-contained-demo exception applies: copies allowed,
   sync discipline required, byte-diff CI verification.
5. Update REPO-corpus.md to document the new `demo/beautify/`
   directory.
6. Gate after move: `test_beauty_snocone_all_modes.sh` PASS=42 SKIP=3
   still green; `test_smoke_unified_broker.sh` total still ≥ 36.

**Why move only when SB-5 is green:** moving broken code into corpus
locks in a debugging session that has to find issues across two
locations. Easier to land the move when the implementation works.

**Compatibility with GOAL-CORPUS-LAYOUT.md:** When the broader
corpus reorg executes (CL-1..CL-8), `demo/beautify/` becomes
`programs/beautify/snocone/` — the language sub-folder pattern the
new layout adopts. The current move is forward-compatible: the
.sc files are already in `beautify/`, just under a different parent.

**Active rung remains SB-5.** The destination decision does not
change what blocks progress — it only documents where the work
lands when unblocked. SB-7 (gate script + commit + push) becomes
the natural place to do the corpus move as part of the same commit
sequence that lands the gate.
