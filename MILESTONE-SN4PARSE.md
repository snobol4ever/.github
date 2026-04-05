# MILESTONE-SN4PARSE — SIL-Faithful SNOBOL4 Lexer/Parser

**Milestone ID:** M-SN4PARSE  
**Session:** DYN-84 · 2026-04-04  
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6  
**Gate:** `./sn4parse corpus/programs/gimpel/SQRT.sno` → zero errors, correct IR tree for all 13 statements  

---

## Why This Exists

scrip-interp's parser (`lex.c` / `parse.c`) has known fragility — the E_SEQ vs
E_CAT ambiguity, the label/subject confusion, deferred patterns not handled as
first-class EXPRESSION type. Before writing SM-LOWER we need a correct parser as
oracle.

SIL v311.sil IS the oracle. Its lexer/parser is a 3-layer 256-byte syntax table
system with `stream()` as the only scanner primitive. This milestone extracts that
system faithfully into a standalone C program that produces our IR tree.

When this milestone passes, we have:
1. A correct standalone parser usable as oracle against SPITBOL
2. A basis for replacing scrip-interp's lex.c/parse.c
3. Confirmed understanding of the 5 missing runtime types (EXPRESSION, CODE, NAME, + captures)

---

## Architecture — How SIL Streams

### The Three Scanning Layers

```
Layer 1 — Card type (CARDTB)
  stream(CARDTB): classifies entire line as NEW / CMT / CTL / CNT
  NEWTYP=1  → new statement (body follows)
  CMTTYP=2  → comment (* in col 1) → skip
  CTLTYP=3  → control card (- directive) → skip
  CNTTYP=4  → continuation (+ in col 1) → NEWCRD called; strips +, TEXTSP set to remainder; FORWRD restarts on new line (TRUE STREAMING — no pre-joining)

Layer 2 — Inter-field scanning (IBLKTB → FRWDTB)
  FORBLK: stream(IBLKTB) — skips leading blanks, stops at field boundary
  FORWRD: stream(FRWDTB) — finds next non-blank token boundary
  BRTYPE set after each call — the delimiter that ended the field:
    EQTYP=4  → = (assignment/replacement separator, consumed by AC_STOP)
    CLNTYP=5 → : (goto field, consumed)
    EOSTYP=6 → end of statement
    RPTYP    → ) consumed
    CMATYP   → , consumed
    NBTYP    → non-blank, NOT consumed (next char is start of token)

Layer 3 — Token content
  LBLTB → LBLXTB : label field (col 1, alphanumeric run)
  ELEMTB → VARTB / INTGTB → FLITB / SQLITB / DQLITB : element type
  BIOPTB → TBLKTB / STARTB : binary operator (STARTB disambiguates * vs **)
  UNOPTB : unary prefix operators
  GOTOTB → GOTSTB / GOTFTB : goto field type
```

### The stream() Function (verbatim from lib/stream.c)

```c
// Consumes chars from sp2, sets sp1=prefix, sp2=remainder, STYPE=put.
// AC_CONTIN: keep going (fast path: index==0)
// AC_STOP:   cp++; len--; then STOPSH (consume current char)
// AC_STOPSH: stop WITHOUT consuming (next char stays in sp2)
// AC_ERROR:  STYPE=0; return ST_ERROR immediately
// AC_GOTO:   tp = ap->go; continue in new table
```

**Critical:** AC_STOP consumes the delimiter. AC_STOPSH does not.
- `=`, `)`, `,`, `:` → AC_STOP (consumed — field separator gone before next ELEMNT)
- Non-blank token start → AC_STOPSH (not consumed — ELEMNT sees the char)
- EOS → AC_STOP (consumed)

### FRWDTB Action Ordering (verified from syn_init.h)

```
actions[0] = {EQTYP,  AC_STOP}    chrs['='=61] = 1
actions[1] = {RPTYP,  AC_STOP}    chrs[')'=41] = 2
actions[2] = {RBTYP,  AC_STOP}    chrs['>'=62] = 3
actions[3] = {CMATYP, AC_STOP}    chrs[','=44] = 4
actions[4] = {CLNTYP, AC_STOP}    chrs[':'=58] = 5
actions[5] = {EOSTYP, AC_STOP}    chrs[';'=59] = 6
actions[6] = {NBTYP,  AC_STOPSH}  chrs[other]  = 7
```

**Key trap:** chrs[] values are 1-based indices into actions[]. chrs[x]=N means
actions[N-1]. When rewriting actions[], the chrs[] values must remain verbatim
from syn.c — only the actions[] ordering changes.

### CMPILE — Statement Compiler (v311.sil line 1608)

```
stream(LBLTB)          → label (col 1 alphanumeric; STOPSH on blank/EOS)
FORBLK()               → skip to body; sets BRTYPE
if BRTYPE==EOSTYP      → label-only line
if BRTYPE==CLNTYP      → goto field only (no subject)
ELEMNT() → subject     
FORBLK()               → BRTYPE after subject
if BRTYPE==EQTYP       → CMPFRM: FORBLK(); replacement=EXPR()
if BRTYPE==CLNTYP      → CMPGO
if BRTYPE==EOSTYP      → bare invoke (done)
else                   → pattern=EXPR()
  FORBLK()
  if BRTYPE==EQTYP     → CMPASP: FORBLK(); replacement=EXPR()
  if BRTYPE==CLNTYP    → CMPGO
CMPGO:
  stream(GOTOTB)       → :S/:F/: type
  EXPR() for each label
```

### ELEMNT — Element Analysis (v311.sil line 1924)

```
loop: stream(UNOPTB)   → collect unary prefix operators
stream(ELEMTB)         → classify atom; GOTO chains to VARTB/INTGTB/SQLITB/DQLITB
dispatch on first char of XSP (not STYPE — GOTO chains change STYPE):
  digit  → ILITYP: text=XSP, ival=atoll; or FLITYP if INTGTB→FLITB
  letter → VARTYP/FNCTYP/ARYTYP from VARTB final STYPE
           FNCTYP: loop { arg=EXPR(); FORWRD(); break on RPTYP, cont on CMATYP }
           ARYTYP: loop { sub=EXPR(); FORWRD(); break on RBTYP, cont on CMATYP }
  quote  → QLITYP: strip delimiters from XSP
  '('    → NSTTYP: atom=EXPR() (recursive)
wrap atom in unary chain (innermost last)
BRTYPE = STYPE at end
```

### EXPR — Expression Compiler (v311.sil line 2093)

```
left = ELEMNT()
loop:
  op = BINOP() via stream(BIOPTB)
  if no op → break
  prec = op_prec(op); next_min = right_assoc ? prec : prec+1
  right = expr_prec(next_min)
  left = binop_node(op, left, right)
Juxtaposition (blank-separated elements):
  BINOP returns 0 on blank; need separate detection
  blank + element-start → E_CAT (value ctx) or E_SEQ (pattern ctx)
```

**Operator precedences (from SIL function descriptor CODE+2*DESCR field):**
```
&  BIAMFN  prec=1   (lowest)
|  ORFN    prec=2
+- ADDFN/SUBFN prec=3
*/ MPYFN/DIVFN prec=4
** EXPFN   prec=5   right-assoc
@  BIATFN  prec=6   right-assoc
.$ NAMFN/DOLFN prec=7 right-assoc (highest explicit binary)
   juxtaposition prec=10 (highest of all)
```

---

## What SIL Builds vs What We Build

SIL builds **object code** (a flat descriptor array for its interpreter).
We build an **IR tree** (EXPR_t / STMT_t for SM-LOWER).
The grammar is identical — only the output differs.

---

## Missing Runtime Types (found in DYN-84)

These must be added to DESCR_t / ir.h before SM-LOWER is correct:

| SIL Type | Code | Meaning | Status |
|----------|------|---------|--------|
| EXPRESSION | E=11 | Unevaluated expr (`*X`) — CODE pointer with type tag | ❌ missing |
| CODE | C=8 | Compiled code block (DEFINE/EVAL result) | ❌ missing |
| NAME | N=9 | Name descriptor (`.X` — pointer to variable cell) | ❌ missing |
| Conditional capture | XNME | Buffer on name list, commit at Phase 5 | ⚠️ partial |
| Immediate capture | XFNME | Assign live, push unravel entry | ⚠️ conflated with XNME |

**EXPVAL protocol (re-entrant eval for EXPRESSION type):**
```
save: OCBSCL, OCICL, PATBCL, PATICL, WPTR, XCL, YCL, TCL
      MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL
      HEADSP, TSP, TXSP, XSP (specifiers)
set:  OCBSCL = expression code block; OCICL = DESCR (first slot)
run:  inner interpreter loop
restore: all saved state
```
SM dispatch loop must support this as a proper C stack frame (sm_interp() called
recursively with new SM_Program* and ip=0).

---

## sn4parse.c Current State

**File:** `one4all/src/frontend/snobol4/sn4parse.c`  
**Commit:** `59ada3d`  

**Working:**
- Card type dispatch (CARDTB): comments, directives, continuations skipped
- Label field (LBLTB): column-1 alphanumeric labels
- FORBLK/FORWRD: inter-field blank scanning
- ELEMNT: variables, integer/float literals, quoted strings, function calls with args, subscripts, unary operators
- EXPR: binary operators with precedence, right-associativity
- CMPILE: assignment (X=Y), bare invoke, :S/:F/: goto fields
- Corpus test: `LT(Y,0) :S(FRETURN)` → correct tree

**Remaining bugs (fix in order):**

**Bug 1: `**` exponent not parsed**
- BIOPTB `*` → STARTB → `*` → EXPFN/TBLKTB
- BINOP() saves/restores TEXTSP on ST_ERROR but STARTB succeeds
- Likely expr_prec_continue exits after first element before looping
- Fix: trace why BINOP returns 0 on `**`

**Bug 2: FORBLK error after `)` before tab+`:`**
- After `LT(Y,0)`, TEXTSP=`\t:S(RETURN)`
- FORBLK→IBLKTB: tab(9)→1→GOTO FRWDTB→`:`→CLNTYP AC_STOP → should work
- Actual: "FORBLK: scan error" — IBLKTB sees something unexpected
- Fix: add debug print inside FORBLK to see what char IBLKTB errors on

**Bug 3: Pattern field not reached**
- `SUBJECT PATTERN :S/:F` form (most SNOBOL4 statements)
- After subject ELEMNT, FORBLK returns NBTYP for non-blank
- CMPILE should call EXPR() for pattern — check branch condition

**Bug 4: Juxtaposition (blank-separated CAT/SEQ)**
- `'HELLO' LEN(5)` → should produce E_CAT (value) or E_SEQ (pattern)
- BINOP() returns 0 on blank; expr_prec_continue exits loop
- Fix: after BINOP fails, peek at TEXTSP — if non-blank element follows,
  build CAT/SEQ node in_pattern_ctx flag

---

## Gate Criteria

```bash
cd /home/claude
./sn4parse corpus/programs/gimpel/SQRT.sno 2>&1
# Expected: 13 statements, 0 errors
# Every statement shows correct subject/pattern/replacement/goto tree
# SQRT = Y ** 0.5 → replace: (EXPFN(**) (VAR Y) (FLIT 0.5))
# LT(Y,0) :S(FRETURN) → subject: (FNC LT (VAR Y) (ILIT 0)) :S(FRETURN)
```

Secondary gate — run full Gimpel suite:
```bash
for f in corpus/programs/gimpel/*.sno; do
  echo "=== $f ===" && timeout 5 ./sn4parse "$f" 2>&1 | grep "error\|=== [0-9]"
done
```

---

## Relationship to DYN-82 (SM_Program)

sn4parse.c is NOT a replacement for scrip-interp's parser. It is:
1. **Oracle** — run both parsers on same input, diff IR trees
2. **Documentation** — the grammar is now executable
3. **Precursor** — when sn4parse passes corpus, port its ELEMNT/EXPR/CMPILE
   into scrip-interp replacing lex.c/parse.c, then SM-LOWER can be written
   on a correct foundation

**DYN-82 sequence (unchanged):**
```
M-SN4PARSE (this) → correct parser
  → SM_Instr + SM_Program structs
  → SM-LOWER (IR → SM_Program)
  → sm_interp dispatch loop
  → replace tree-walker in scrip-interp.c
  → corpus ≥177p/0f → M-DYN-SM-INTERP
```

---

*Written: DYN-84 session 2026-04-04*  
*File: MILESTONE-SN4PARSE.md*
