# MILESTONE-SN4PARSE-VALIDATE — SN4 Parser Validation Suite

**Milestone ID:** M-SN4PARSE-VALIDATE  
**Session type:** DYN- (parser/frontend)  
**Prerequisite:** M-SN4PARSE (sn4parse.c passes SQRT.sno with zero errors)  
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6  
**Created:** DYN-85 · 2026-04-04  
**Gate:** All three phases pass. See Gate Criteria section.

---

## Why This Exists

M-SN4PARSE produced a SIL-faithful standalone parser (`sn4parse.c`) and fixed
all four root-cause bugs (`**`, FORBLK after `)`, pattern field, juxtaposition).
Before we use sn4parse as the oracle for SM-LOWER and for replacing scrip-interp's
lex.c/parse.c, we need to know it parses the full language correctly.

Three complementary checks cover this:

| Phase | What it tests | What it catches |
|-------|--------------|-----------------|
| **1 — Corpus sweep** | sn4parse on all 550+ SNOBOL4 `.sno` and 154 `.inc` files | Crashes, infinite loops, error-rate, edge-case syntax not in SQRT |
| **2 — Bison/Flex diff** | sn4parse IR tree vs scrip-interp's Bison/Flex IR tree | Semantic divergence between the two parsers on same input |
| **3 — CSNOBOL4 oracle** | Instrument CSNOBOL4 to emit S-expressions; diff vs sn4parse | Ground-truth: the reference implementation's own parse agrees |

Phase 3 is the strongest check: if CSNOBOL4's CMPILE produces the same tree as
sn4parse.c, we have confirmed SIL fidelity at the source level.

---

## Phase 1 — Corpus Sweep

### What to run

```bash
cd /home/claude

# Build
gcc -O0 -g -Wall -o sn4parse one4all/src/frontend/snobol4/sn4parse.c

# Sweep all SNOBOL4 .sno files (exclude icon/prolog/rebus/snocone sub-corpora)
find corpus -name "*.sno" \
  | grep -v /icon/ | grep -v /prolog/ | grep -v /rebus/ | grep -v /snocone/ \
  | sort \
  | while read f; do
      result=$(timeout 5 ./sn4parse "$f" 2>&1)
      errs=$(echo "$result" | grep -c "^line.*:" || true)
      stmts=$(echo "$result" | grep "=== [0-9]* statements ===" | grep -o "[0-9]*" | head -1)
      echo "$errs $stmts $f"
    done | tee /tmp/sn4parse_sweep.txt

# Sweep all .inc files
find corpus -name "*.inc" | sort \
  | while read f; do
      result=$(timeout 5 ./sn4parse "$f" 2>&1)
      errs=$(echo "$result" | grep -c "^line.*:" || true)
      echo "$errs $f"
    done | tee /tmp/sn4parse_sweep_inc.txt

# Summary
echo "Files with errors:"
grep -v "^0 " /tmp/sn4parse_sweep.txt | wc -l
echo "Total files:"
wc -l < /tmp/sn4parse_sweep.txt
echo "Total errors:"
awk '{sum+=$1} END{print sum}' /tmp/sn4parse_sweep.txt
```

### Gate: Phase 1

- Zero crashes (no segfaults, no infinite loops — timeout catches the latter)
- Error rate ≤ 5% of files (target: 0%; tolerate edge-cases not in SIL grammar)
- No regressions on the 13 SQRT.sno statements

### Triage protocol for errors

For each erroring file, run:
```bash
./sn4parse <file> 2>&1 | head -30
```
Classify error as:
- **BUG-SN4**: sn4parse bug (fix it)
- **EXT-SPITBOL**: SPITBOL extension not in SNOBOL4 grammar (acceptable, note it)
- **CORPUS-BAD**: corpus file itself is invalid SNOBOL4 (note it)

---

## Phase 2 — Bison/Flex Diff

### What to run

scrip-interp's Bison/Flex parser (`snobol4.y` / `snobol4.l`) produces EXPR_t/STMT_t IR.
sn4parse.c produces the same tree in S-expression form.
Add a `-dump` flag to scrip-interp (or use its existing IR printer) to get its S-expression,
then diff against sn4parse output.

#### Step 2a — Add IR dump mode to scrip-interp

In `one4all/src/driver/scrip-interp.c`, add a flag `--dump-ir` that:
1. Parses the source file (existing lex+parse path)
2. Prints the STMT_t/EXPR_t tree as S-expressions to stdout
3. Exits without interpreting

The S-expression format must match sn4parse's output schema:
- Nodes printed as `(TYPENAME "text" child1 child2 ...)`
- Use the same EKind name strings that stype_name() uses

#### Step 2b — Run diff script

```bash
cd /home/claude

# For each corpus .sno file:
find corpus/programs/gimpel -name "*.sno" | sort | while read f; do
    sn4=$(timeout 5 ./sn4parse "$f" 2>/dev/null)
    interp=$(timeout 5 ./scrip-interp --dump-ir "$f" 2>/dev/null)
    if [ "$sn4" != "$interp" ]; then
        echo "DIFF: $f"
        diff <(echo "$sn4") <(echo "$interp") | head -20
    fi
done
```

#### Step 2c — Resolve each divergence

For each diff:
1. Run SPITBOL oracle: `snobol4ever/x64/spitbol "$f"` — which parser agrees with SPITBOL?
2. Fix the wrong parser.

Rule: sn4parse (SIL-faithful) is considered authoritative over scrip-interp
(lex.c/parse.c hand-written) when they disagree. Exceptions: if scrip-interp
has been deliberately extended beyond SIL (e.g. for Snocone syntax), note it.

### Gate: Phase 2

- Zero divergences on `corpus/programs/gimpel/*.sno` (13 Gimpel programs)
- Zero divergences on `corpus/crosscheck/rung1/*.sno` through `rung5/*.sno`
- Any remaining divergences documented in `PARSER-SNOBOL4.md` as known differences

---

## Phase 3 — CSNOBOL4 Oracle Instrumentation

### What to do

Instrument CSNOBOL4 2.3.3 (`/tmp/snobol4-2.3.3/snobol4.c`) to emit S-expression
parse trees from its own CMPILE loop. This is the strongest possible oracle:
it is the reference implementation whose parser sn4parse.c faithfully translates.

#### Step 3a — Locate the hook points in snobol4.c

The CMPILE procedure in `/tmp/snobol4-2.3.3/snobol4.c` (line 914) has labeled
branch points matching v311.sil exactly:

```
L_CMPIL0  — after STREAM(XSP, TEXTSP, &LBLTB)            → label in XSP
L_CMPILA  — after FORBLK()                                → body starts
L_CMPSUB  — after STREAM(XSP, TEXTSP, &ELEMTB) for subj  → subject element
L_CMPAT2  — pattern field start                            → pattern element
L_CMPFRM  — = replacement (no pattern)
L_CMPGO   — after STREAM(XSP, TEXTSP, &GOTOTB)            → goto type
```

Each `D(...)` / `D_A(...)` macro accesses the SIL descriptor at a named offset.
`TEXTSP`, `XSP`, `BRTYPE`, `STYPE` are all accessible as SIL globals.

#### Step 3b — Add a `-sexp` command-line flag

In `/tmp/snobol4-2.3.3/main.c`, add flag `-sexp` that:
1. Sets a global `g_sexp_mode = 1` before the compile loop
2. After each successful CMPILE call, calls `sexp_print_stmt()` with the
   just-compiled statement's descriptor block

#### Step 3c — Implement sexp_print_stmt()

```c
/* Hook in snobol4.c after L_CMPILA completes each statement */
#ifdef SEXP_MODE
void sexp_print_stmt(void) {
    /* Read BOSCL..CMOFCL range of compiled descriptors.
     * Walk the descriptor array and emit S-expressions.
     * Output mirrors sn4parse.c print_stmt() exactly. */
}
#endif
```

The descriptor layout per statement (from v311.sil CMPILE object code sequence):
```
DESCR[0] = BASE function (block pointer)
DESCR[1] = INIT function
DESCR[2] = failure offset (FRNCL)
DESCR[3] = line number (LNNOCL)
DESCR[4+] = subject / pattern / replacement / goto nodes
```

Walking this is the hardest part. Alternative simpler approach: intercept at
the EXPR/ELEMNT level to capture each sub-expression as it is generated.

#### Simpler alternative: intercept ELEMNT and EXPR return values

Add hooks at the three points where SIL writes the completed nodes:
- After `ELEMNT` returns (writes ZPTR) — capture element node
- After `EXPR` returns — capture expression tree
- After `CMPILE` processes each field — emit field S-expression

These hook points all have C-level equivalents in `snobol4.c` after the
corresponding `switch (ELEMNT(NORET))` / `switch (EXPR(NORET))` calls.

#### Step 3d — Diff CSNOBOL4 output vs sn4parse output

```bash
cd /tmp/snobol4-2.3.3
make && ./snobol4 -sexp /home/claude/corpus/programs/gimpel/SQRT.sno \
  > /tmp/csnobol4_sqrt.sexp 2>&1

cd /home/claude
./sn4parse corpus/programs/gimpel/SQRT.sno > /tmp/sn4parse_sqrt.sexp 2>&1

diff /tmp/csnobol4_sqrt.sexp /tmp/sn4parse_sqrt.sexp
```

### Gate: Phase 3

- Zero diffs on `SQRT.sno` (13 statements)
- Zero diffs on all Gimpel programs
- Any remaining diffs analysed: if CSNOBOL4 produces different tree → sn4parse bug

---

## Gate Criteria (all three phases)

```
Phase 1: sn4parse sweeps 550 .sno + 154 .inc with 0 crashes, ≤5% error files
Phase 2: sn4parse and scrip-interp --dump-ir agree on Gimpel + rung1..rung5 corpus
Phase 3: sn4parse and instrumented CSNOBOL4 agree on SQRT.sno (13 stmts), then Gimpel
```

When all three pass: **M-SN4PARSE-VALIDATE is complete.**

Next milestone: replace scrip-interp's lex.c/parse.c with sn4parse's
CMPILE/ELEMNT/EXPR, then write SM-LOWER → M-DYN-SM-INTERP.

---

## Session Start Instructions

```bash
# Always read first:
cat /home/claude/.github/SCRIP-SM.md
cat /home/claude/.github/SESSIONS_ARCHIVE.md | tail -120
cat /home/claude/.github/PLAN.md
# Then this file:
cat /home/claude/.github/MILESTONE-SN4PARSE-VALIDATE.md
# Build sn4parse:
cd /home/claude && gcc -O0 -g -Wall -o sn4parse one4all/src/frontend/snobol4/sn4parse.c
# Run Phase 1 sweep immediately to see current baseline.
```

---

## File Locations

| File | Role |
|------|------|
| `one4all/src/frontend/snobol4/sn4parse.c` | SIL-faithful standalone parser (this milestone's subject) |
| `one4all/src/frontend/snobol4/snobol4.y` | Bison grammar (Phase 2 reference) |
| `one4all/src/frontend/snobol4/snobol4.l` | Flex lexer (Phase 2 reference) |
| `one4all/src/driver/scrip-interp.c` | Tree-walking interpreter (Phase 2: add --dump-ir) |
| `/tmp/snobol4-2.3.3/snobol4.c` | CSNOBOL4 compiled C source (Phase 3: instrument) |
| `/tmp/snobol4-2.3.3/main.c` | CSNOBOL4 main (Phase 3: add -sexp flag) |
| `corpus/programs/gimpel/` | Primary test suite (13 Gimpel programs) |
| `corpus/crosscheck/` | Rungs 1-8 regression corpus |

---

*Written: DYN-85 · 2026-04-04*  
*File: MILESTONE-SN4PARSE-VALIDATE.md*
