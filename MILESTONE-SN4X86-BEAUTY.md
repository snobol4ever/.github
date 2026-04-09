# MILESTONE-SN4X86-BEAUTY.md — SNOBOL4 × x86: beauty self-hosting

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-08
**Goal:** `scrip --ir-run beauty.sno beauty.sno` runs to completion without errors.

Run command:
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno
```

Baseline errors (2026-04-08):
- `ELEMNT: illegal character` on lines 337, 353, 366, 385 of beauty.sno → tilde `~`
- `** Error 5 in statement 479` → label `pp_~` contains `~`
- `&ALPHABET` keyword not wired → no-op stub needed

---

## B-1 — Tilde `~` unary and binary operator

**Status:** ⬜
**Depends on:** nothing

### Problem
`~` (ASCII 126) is absent from UNOPTB chrs[] — fires ACT_ERROR (index 15).
Unary `~X` = NOT/negation (NEGFN, code 311).
Binary `A ~ B` = NOT match — `~` also appears in BIOPTB as a binary op.

NEGFN is already defined (`#define NEGFN 311`) and already has an action entry
in UNOPTB_actions[] at index 10 (0-based), mapped to `{NEGFN, ACT_GOTO, &NBLKTB}`.

### Fix — UNOPTB
In `CMPILE.c` UNOPTB chrs[] array, ASCII 126 (`~`) is currently `15` (ACT_ERROR).
Change it to `11` (1-based index for NEGFN action = actions[10]).

Verify: row starting at byte 112 (0x70), position 14 within that row = byte 126.
Current value: `15`. New value: `11`.

### Fix — BIOPTB
Check BIOPTB chrs[126]. If also 0 or ACT_ERROR, add NEGFN (or a TNOFN) entry.
Binary `~` in SNOBOL4/SPITBOL = NOT-match: `subject ~ pattern` succeeds if pattern
FAILS. Wire to the same negation-match function SPITBOL uses for binary tilde.

### Fix — label names
Labels can contain `~` — e.g. `pp_~`. Check LBLTB / label-scan loop to confirm
`~` is accepted as a label character (not just operator context).

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty.sno beauty.sno 2>&1 | grep "ELEMNT: illegal" | wc -l
# → 0
```

---

## B-2 — `&ALPHABET` keyword stub

**Status:** ⬜
**Depends on:** nothing (independent of B-1)

### Problem
`&ALPHABET` appears in `global.sno` lines 2–28+. It is not in the keyword dispatch
table (`NV_GET_fn` / `NV_SET_fn`). Assignment to `&ALPHABET` sets character class
membership. Reading `&ALPHABET` returns the 256-char alphabet string.

Beauty does not exercise character-class matching in its self-hosting run —
it only sets `&ALPHABET` to extract individual characters via pattern capture.
A stub that accepts the assignment silently (no-op write, returns `""` on read)
is sufficient to unblock the run.

### Fix
In `snobol4.c` `SNO_INIT_fn` or `NV_SET_fn` keyword dispatch:
```c
if (strcasecmp(name, "ALPHABET") == 0) return;  /* stub: no-op */
```
In `NV_GET_fn`:
```c
if (strcasecmp(name, "ALPHABET") == 0) return STRVAL("");  /* stub */
```

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty.sno beauty.sno 2>&1 | grep "ALPHABET" | wc -l
# → 0
```

---

## B-3 — Beauty runs to completion

**Status:** ⬜
**Depends on:** B-1, B-2

### What this is
After B-1 and B-2, run beauty self-hosting and triage any remaining errors.
Expected survivors after B-1+B-2: Error 5 on statement 479 (`pp_~` label) and
any other gaps exposed once tilde and &ALPHABET are fixed.

### Run and triage loop
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    2>&1 | head -60
```

Capture all `** Error` lines. File each as a sub-bug. Fix in order until output
matches SPITBOL reference run.

### Reference run (SPITBOL)
```bash
/home/claude/x64/bin/sbl \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno
```
Diff scrip output vs SPITBOL output — exact match is the gate.

### Gate
```
scrip --ir-run beauty.sno beauty.sno  output  ==  /home/claude/x64/bin/sbl beauty.sno beauty.sno  output
```
No `** Error` lines. No `ELEMNT` warnings. Exit 0.

---

## Sprint tracking

| Milestone | Status | Sprint | Notes |
|-----------|--------|--------|-------|
| B-1 tilde `~` | ⬜ | — | UNOPTB chrs[126] + BIOPTB + label scan |
| B-2 &ALPHABET stub | ⬜ | — | NV_SET/NV_GET no-op |
| B-3 beauty runs | ⬜ | — | triage loop after B-1+B-2 |
