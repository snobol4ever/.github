# GOAL-SNOCONE-BEAUTY — Get beauty.sc (Snocone port of beauty.sno) Working

**Repo:** one4all
**Blocked by:** GOAL-SCRIP-BEAUTY — beauty.sno must pass all 18/18 drivers first.
**Done when:** `beauty.sc` self-beautifies correctly via `scrip -sc -x86`, producing
output byte-for-byte identical to the SPITBOL oracle on `beauty.sc` itself.

---

## What this is

`beauty.sc` is a Snocone port of `beauty.sno` — the SNOBOL4 beautifier written in
SNOBOL4, now expressed in Snocone's structured C-like syntax. It lives at:

```
one4all/test/beauty-sc/beauty/beauty.sc
```

The subsystem test infrastructure already exists:
- `test/beauty-sc/run_beauty_sc_subsystem.sh` — compiles `.sc` via `scrip -sc -x86`,
  assembles with NASM, links against runtime archive, runs, diffs vs `.ref`
- Individual subsystem drivers in `test/beauty-sc/<subsystem>/driver.sc` + `driver.ref`
  covering: assign, match, counter, stack, tree, ShiftReduce, TDump, ReadWrite, XDump,
  semantic, omega, trace, fence, global, strings, arith, roman

The full `beauty.sc` (main program body) includes all library procedures via `-sc` includes.

---

## Prerequisite check

Before starting any step, confirm GOAL-SCRIP-BEAUTY is ☑ done in PLAN.md.
If not done, stop and work on GOAL-SCRIP-BEAUTY first.

```bash
grep "SCRIP-BEAUTY" /home/claude/.github/PLAN.md
```

---

## Verification Technique

Claude reads the output / test result sentence by sentence (or diff line by line).
For each issue, Claude presents it clearly and asks: **T or F?**

- **T** — assessment is correct. Proceed with fix.
- **F** — assessment is wrong. Claude re-diagnoses before proceeding.

---

## Steps

- [ ] **S-1** — Confirm prerequisite: GOAL-SCRIP-BEAUTY ☑ done.
  Gate: `grep "Scrip Beauty" PLAN.md` shows ☑.

- [ ] **S-2** — Run all subsystem drivers to establish baseline:
  ```bash
  cd /home/claude/one4all
  CORPUS=/home/claude/corpus bash test/beauty-sc/run_beauty_sc_subsystem.sh \
      assign match counter stack tree ShiftReduce TDump ReadWrite XDump \
      semantic omega trace fence global strings arith roman
  ```
  Record PASS/FAIL/SKIP counts. These are the starting failures.
  Gate: baseline counts in hand.

- [ ] **S-3** — Fix each failing subsystem one at a time, in order of simplest first.
  For each failure: compile error → fix Snocone frontend or runtime; output mismatch →
  diagnose via SPITBOL oracle diff; link error → fix runtime archive.
  Gate: all subsystem drivers PASS.

- [ ] **S-4** — Run `beauty.sc` self-beautification end-to-end:
  ```bash
  cd /home/claude/one4all
  # Compile beauty.sc with all includes
  ./scrip -sc -x86 test/beauty-sc/beauty/beauty.sc -o /tmp/beauty_sc.s
  nasm -f elf64 -I src/runtime/x86/ /tmp/beauty_sc.s -o /tmp/beauty_sc.o
  gcc -no-pie /tmp/beauty_sc.o out/rt_cache/snocone_rt.a -lgc -lm -o /tmp/beauty_sc_bin
  # Self-beautify
  /tmp/beauty_sc_bin < test/beauty-sc/beauty/beauty.sc > /tmp/beauty_sc_out.sc
  # Oracle: SPITBOL on beauty.sno self-beautifies
  /home/claude/x64/bin/sbl -b \
      /home/claude/corpus/programs/snobol4/beauty/beauty.sno \
      < /home/claude/corpus/programs/snobol4/beauty/beauty.sno \
      > /tmp/beauty_sno_oracle.txt
  diff /tmp/beauty_sc_out.sc /tmp/beauty_sno_oracle.txt
  ```
  Gate: diff is empty — byte-for-byte match with SPITBOL oracle.

- [ ] **S-5** — Add `run_beauty_sc_full.sh` to `one4all/test/beauty-sc/`:
  End-to-end runner that compiles, assembles, links, and self-beautifies.
  Diffs against SPITBOL oracle. Reports PASS or FAIL.
  Gate: script runs cleanly, PASS reported.

- [ ] **S-6** — Update PLAN.md: mark this goal ☑ done.
  Gate: handoff committed.

---

## Key files

| File | Role |
|------|------|
| `one4all/test/beauty-sc/beauty/beauty.sc` | Main program (Snocone port of beauty.sno) |
| `one4all/test/beauty-sc/run_beauty_sc_subsystem.sh` | Subsystem test runner |
| `one4all/test/beauty-sc/<subsystem>/driver.sc` | Per-subsystem Snocone test driver |
| `one4all/test/beauty-sc/<subsystem>/driver.ref` | Expected output (SNOBOL4 golden) |
| `corpus/programs/snobol4/beauty/beauty.sno` | SNOBOL4 original (oracle reference) |

---

## Rules
- Do not push until "perform hand off".
- Commit identity: `LCherryholmes` / `lcherryh@yahoo.com`.
- SPITBOL (`/home/claude/x64/bin/sbl`) is the oracle.
- No ad-hoc builds — use or extend scripts in `one4all/build/` or `test/beauty-sc/`.
