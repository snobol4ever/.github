# GOAL-CSNOBOL4-FENCE — FENCE(P) Function in CSNOBOL4

**Repo:** csnobol4 (`v311.sil`, `snobol4.c`, `data_init.c`)
**Done when:** all 10 tests in `test/fence_function/` pass against CSNOBOL4, matching SPITBOL oracle output exactly.

---

## What this is

CSNOBOL4 2.3.3 implements `&FENCE` (the 0-argument keyword pattern) but **does not** implement
`FENCE(P)` — the 1-argument function form that matches P and seals P's alternatives from
outside backtracking. This goal adds the missing form.

The 1-arg form is heavily used in the corpus (97 files). Programs currently work around the
missing function by including `corpus/programs/include/FENCE.inc`, a no-op polyfill
(`DEFINE('FENCE(FENCE)')`). Once this goal is complete, the polyfill is unnecessary for CSNOBOL4.

**Oracle:** SPITBOL x64 (`/home/claude/x64/bin/sbl`). When in doubt, SPITBOL is right.

---

## Design

Four new pattern nodes, opcodes 37–40, following the SPITBOL x64 design exactly
(`bootstrap/sbl.asm` `p_fna`–`p_fnd`; Minimal `v37.min` lines 13314–13344).

```
FENCE(P) compiles to:  [FNCA] ──▶ [P nodes] ──▶ [FNCC]

  FNCA (37): enter fence — save outer PDLHED, push FNCBCL inner-fail trap, new PDLHED
  FNCB (38): inner fail trap — P exhausted; restore outer PDLHED, fail outward
  FNCC (39): exit fence — P matched; restore outer PDLHED; if P left alts, push FNCDCL seal
  FNCD (40): outer seal — backtrack tried to re-enter P; reset PDL, fail outward
```

PDLHED (v311.sil line 10854) is CSNOBOL4's equivalent of SPITBOL's `pmhbs`.
Always paired with NHEDCL (line 10831).

Total new SIL: **108 lines** across 8 change sites. See FENCE.md in csnobol4 repo for full
line-by-line proposal.

---

## Repo setup

```bash
git config --global --add safe.directory /home/claude/csnobol4
cd /home/claude && git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4
cd /home/claude/csnobol4
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
# DO NOT run ./configure or make — see RULES.md
```

Oracle (already built):
```bash
/home/claude/x64/bin/sbl   # SPITBOL x64
```

Run tests:
```bash
cd /home/claude/csnobol4/test/fence_function
make spitbol   # verify oracle passes all 10
make csnobol4  # run against CSNOBOL4 (fails until impl complete)
```

---

## Steps

- [ ] **S-1** — Add opcodes + EQUs to v311.sil.
  Add after line 952 (after `XSUCF EQU 36`):
  ```
  XFNCA   EQU    37
  XFNCB   EQU    38
  XFNCC   EQU    39
  XFNCD   EQU    40
  ```
  Gate: v311.sil grep confirms 4 new EQUs present.

- [ ] **S-2** — Add FNCP PROC (function builder) to v311.sil after FNCE XPROC (~line 4081).
  27 lines. Allocates block, copies FNCAPT → P → FNCCPT using CPYPAT, returns ZPTR.
  Gate: v311.sil grep confirms FNCP PROC present.

- [ ] **S-3** — Add four XPROC bodies to v311.sil after FNCP PROC.
  58 lines: FNCA, FNCB, FNCC (with FNCC1 optimization branch), FNCD.
  Gate: all four labels present in v311.sil.

- [ ] **S-4** — Add descriptor cells and function node DESCRs to static data area (~line 10780).
  8 lines: FNCACL, FNCBCL, FNCCL, FNCDCL; FNCAFN, FNCBFN, FNCFN, FNCDFN.
  Gate: grep confirms all 8 symbols present.

- [ ] **S-5** — Add static pattern node templates near FNCEPT (~line 12096).
  10 lines: FNCAPT (3-descr node, FNCAFN), FNCCPT (3-descr node, FNCFN).
  Gate: FNCAPT and FNCCPT present in v311.sil.

- [ ] **S-6** — Extend SELBRA dispatch table (line ~3618).
  Append `,FNCA,FNCB,FNCC,FNCD` to existing SELBRA list.
  Gate: SELBRA line contains all four new labels.

- [ ] **S-7** — Register FENCE function in initialization (~line 995 area).
  Add `DEFINE FNCESP,FNCP,1` (or equivalent PUTDC wiring for 1-arg function).
  Gate: FENCE callable as 1-arg function at runtime.

- [ ] **S-8** — Mirror changes into snobol4.c (C interpreter).
  Add `case 37: goto L_FNCA;` through `case 40: goto L_FNCD;` in PATBRA switch.
  Add `L_FNCA:` / `L_FNCB:` / `L_FNCC:` / `L_FNCD:` C code bodies matching the SIL XPROCs.
  Wire FENCE into the function call table so `FENCE(P)` is recognized as a 1-arg builtin.
  Gate: snobol4.c compiles without errors (`gcc -Wall`).

- [ ] **S-9** — Run oracle diff.
  ```bash
  cd test/fence_function && make diff
  ```
  All 10 tests: SPITBOL output == CSNOBOL4 output.
  Fix any discrepancies.
  Gate: `make diff` shows MATCH for all 10.

- [ ] **S-10** — Run full existing CSNOBOL4 test suite to confirm no regressions.
  ```bash
  cd /home/claude/csnobol4/test && bash run.sh 2>&1 | tail -5
  ```
  Gate: same pass count as baseline (all existing tests still pass).

---

## State

**HEAD:** `a509cd7` (initial import + test cases)
**Tests passing (CSNOBOL4):** 0/10
**Tests passing (SPITBOL oracle):** 10/10 (assumed; verify at S-1)
**Current step:** S-1

---

## Rules

- Commit after each step as `LCherryholmes` / `lcherryh@yahoo.com`.
- Never build the CSNOBOL4 executable via `./configure && make` — see RULES.md.
- SPITBOL oracle is always right.
- Rebase before every .github push.
- See RULES.md for full handoff checklist.
