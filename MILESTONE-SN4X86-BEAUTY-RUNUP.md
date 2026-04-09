# MILESTONE-SN4X86-BEAUTY-RUNUP.md — SNOBOL4 × x86: beauty runup tests

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-09
**Goal:** All beauty runup tests pass under `scrip --ir-run`.

Two test suites must both pass:
1. **Crosscheck** (6 tests) — `corpus/crosscheck/beauty/*.input` piped through beauty, diffed against `.ref`
2. **Subsystem drivers** (19 tests) — `corpus/programs/snobol4/beauty/*_driver.sno` run directly, output diffed against `.ref`

---

## Diagnostic context (2026-04-09)

Beauty.sno **does not compile** under scrip — 7 ELEMNT errors, zero stdout, exit 0.
Confirmed by: stderr-only output, zero lines produced.

Debug instrumentation revealed the actual offending characters:

| Error | Line | Char | Context |
|-------|------|------|---------|
| 1 | 57 | `\|` (0x7c) | `\| "'" . *assign(.In` |
| 2 | 6 | space (0x20) | `&ALPHABET` subject line (global.sno include 1) |
| 3 | 6 | space (0x20) | `&ALPHABET` subject line (global.sno include 2) |
| 4 | 337 | `\|` (0x7c) | `\| *Id ~ 'Id' $'(' *E` |
| 5 | 353 | `\|` (0x7c) | `\| (*SGoto \| *FGoto)` |
| 6 | 366 | `\|` (0x7c) | `\| ($'?' \| *White)` |
| 7 | 385 | `\|` (0x7c) | `\| *Control ~ 'Contro` |

**Root causes:**
- **5 of 7 errors: `|` in FENCE continuation lines** — ELEMTB chrs[124]=6 (ACT_ERROR).
  `|` appears as the first non-space token on a `+` continuation line inside a FENCE() argument.
  BINOP→BIOPTB handles `|` as ORFN *between* two elements, but when `|` is the *first* character
  after FORWRD on a continuation (i.e. no left-hand element yet in that sub-expression),
  ELEMNT is called and ELEMTB fires before BINOP gets a chance.
- **2 of 7 errors: space on `&ALPHABET` lines** — `&ALPHABET` in subject position;
  ELEMTB sees a space after FORWRD because `&ALPHABET` is in the subject field
  and the keyword parsing path isn't consuming it correctly before ELEMNT.

---

## BRU-1 — `|` accepted in FENCE continuation context

**Status:** ⬜
**Depends on:** nothing

### Problem
In beauty.sno, FENCE() arguments span multiple continuation (`+`) lines, with `|` (alternation)
starting each alternative:
```
Expr17  =  FENCE(
+             nPush() $'(' ...
+           | *Function ~ 'Function' ...
+           | *Id ~ 'Id' ...
```
When the parser resumes on a `+` line beginning with `|`, it calls ELEMNT to parse the next
element. ELEMTB chrs[124] = 6 (ACT_ERROR) — `|` is not a valid element start.

In SNOBOL4/SPITBOL, `|` inside a FENCE() argument IS valid as alternation — it's a binary
operator between pattern alternatives. The parser should recognize `|` in this position as
ORFN (binary OR) and treat the entire FENCE() argument as a pattern expression, not as
an isolated element.

### Fix
`|` as a continuation-line leader is a binary operator with an implicit `epsilon` left operand,
or alternatively the expression parser must handle `|` as a prefix (unary alternation) in
pattern context.

Two approaches:
1. **UNOPTB approach:** Add `|` to UNOPTB as a unary operator that produces ORFN/BARFN.
   UNOPTB chrs[124] is currently `12` → BARFN (unary `|` = user-definable). Check: is that
   already wired? If so, why does ELEMTB still fire?
2. **ELEMTB approach:** If `|` reaches ELEMTB in this context, wire ELEMTB chrs[124] to
   handle it — but this is likely wrong; ELEMTB should not see operators.

**First action:** Check UNOPTB chrs[124] (`|`) — it may already be 12 (BARFN), meaning
the UNOP loop consumed `|` as unary, then NBLKTB rejected the next char, then the
nospace path fired — and that path's `nxt_is_token` guard excludes `*` (indirect). Fix
the `nxt_is_token` guard to include `*`, `$`, `'`, `"`, `(` and identifiers.

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty.sno beauty.sno 2>&1 | grep "ELEMNT.*|" | wc -l
# → 0
```

---

## BRU-2 — `&ALPHABET` in subject position compiles clean

**Status:** ⬜
**Depends on:** nothing (independent of BRU-1)

### Problem
`&ALPHABET POS(0) LEN(1) . nul` (global.sno line 2+): `&ALPHABET` in subject position
causes ELEMNT to fire with char=space. The keyword `&ALPHABET` is parsed as subject,
but FORWRD then lands on the space between `&ALPHABET` and `POS(0)`, and ELEMTB
fires on that space.

Likely cause: the subject-field parser calls ELEMNT after parsing `&ALPHABET` expecting
the next element to be the pattern, but FORWRD isn't advancing past the inter-field space
before ELEMTB is invoked.

### Fix
In the statement compiler, after the subject field is parsed (which includes `&ALPHABET`
via NV_GET), ensure FORWRD() is called before ELEMNT() is invoked for the pattern field.
Alternatively, confirm that the subject/pattern boundary logic handles keyword-valued
subjects correctly.

### Gate
```bash
SNO_LIB=.../inc ./scrip --ir-run beauty.sno beauty.sno 2>&1 | grep "line 6:" | wc -l
# → 0
```

---

## BRU-3 — beauty.sno compiles and runs to completion

**Status:** ⬜
**Depends on:** BRU-1, BRU-2

### What this is
After BRU-1 + BRU-2, run beauty self-hosting and triage any remaining compile or
runtime errors. The self-hosting run:
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    2>&1 | head -40
```
Gate: no ELEMNT errors, no `** Error`, exit 0, stdout non-empty.

---

## BRU-4 — Crosscheck suite: 6/6 pass

**Status:** ⬜
**Depends on:** BRU-3

### Tests
`corpus/crosscheck/beauty/` — 6 input/ref pairs:
`101_comment`, `102_output`, `103_assign`, `104_label`, `105_goto`, `109_multi`

### Run
```bash
cd /home/claude/one4all
CORPUS=/home/claude/corpus bash test/crosscheck/run_beauty.sh
```
Note: `run_beauty.sh` expects `./beauty_full_bin`. Confirm or update to use
`scrip --ir-run beauty.sno` as the driver.

### Gate
```
Results: 6 passed, 0 failed, 0 skipped
ALL PASS
```

---

## BRU-5 — Subsystem driver suite: 19/19 pass

**Status:** ⬜
**Depends on:** BRU-3

### Tests
`corpus/programs/snobol4/beauty/*_driver.sno` — 19 driver programs:
Gen, Qize, ReadWrite, ShiftReduce, TDump, XDump, assign, case, counter,
fence, global, io, is, match, omega, semantic, stack, trace, tree

Each driver `-INCLUDE`s the component under test and exercises it.
Run each via:
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run <driver>.sno
```
Diff stdout against `<driver>.ref`.

### Gate
All 19 drivers: stdout == .ref, no `** Error` lines.

---

## Sprint tracking

| Milestone | Status | Notes |
|-----------|--------|-------|
| BRU-1 `\|` in FENCE continuations | ⬜ | Check UNOPTB chrs[124] + nxt_is_token guard first |
| BRU-2 `&ALPHABET` subject position | ⬜ | FORWRD before pattern ELEMNT |
| BRU-3 beauty self-hosting runs | ⬜ | Depends BRU-1+2; triage loop |
| BRU-4 crosscheck 6/6 | ⬜ | Depends BRU-3 |
| BRU-5 subsystem 19/19 | ⬜ | Depends BRU-3 |
