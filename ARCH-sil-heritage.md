# ARCH-sil-heritage.md — SIL Name Lineage for IR Nodes

**Source:** CSNOBOL4 2.3.3, file `v311.sil` (Phil Budne, final revision 2022-02-17)
**Purpose:** Document the origin of every `E_*` IR node name, connecting it to
the SIL token type codes (`xxxTYP EQU N`) and runtime operation names that
Lon ported three times and knows intimately.

---

## Background

SNOBOL4's original implementation language is SIL (SNOBOL4 Implementation Language),
a macro assembler portable across architectures. CSNOBOL4 (Phil Budne's C port)
preserves the SIL naming conventions throughout `v311.sil`.

The `E_` prefix in our IR means **Expression node**. The names derive from SIL's
`xxxTYP` token type codes — integer discriminants used by the compiler's lexer and
parser to classify tokens and expression nodes.

**SIL `xxxTYP` naming convention:** `VARTYP EQU 3` means "Variable token has type
code 3". The `TYP` suffix = type code. The prefix (VAR, QLIT, ILIT, etc.) = the
semantic category. Our `E_VAR` came from `VARTYP` — the T is the first letter of
TYP, compressed for the C identifier.

**The `E_` prefix** was added when sno2c.h defined the C enum — `E_` for Expression
kind, distinguishing from `S_` (statement kinds) and other prefix families.

---

## Token Type Codes (v311.sil lines 871–896)

```sil
ARYTYP EQU     7       Array reference          → E_IDX (absorbed E_ARY)
FLITYP EQU     6       Literal real             → E_FLIT
FNCTYP EQU     5       Function call            → E_FNC
ILITYP EQU     2       Literal integer          → E_ILIT
QLITYP EQU     1       Quoted literal           → E_QLIT
VARTYP EQU     3       Variable                 → E_VAR  (T = first letter of TYP)
```

Note: `EQTYP EQU 4` (Equal sign) became `E_ASSIGN` (not `E_EQTYP`) —
we preferred operation name over SIL token name here.

---

## Data Type Codes (v311.sil lines ~900–915)

Single-letter codes for runtime value types:

```sil
A  EQU  4    ARRAY
I  EQU  6    INTEGER
K  EQU  10   KEYWORD (NAME)    → E_KW uses K
P  EQU  3    PATTERN
R  EQU  7    REAL
S  EQU  1    STRING
T  EQU  5    TABLE
E  EQU  11   EXPRESSION
N  EQU  9    NAME
```

---

## Pattern Function Indexes (v311.sil XATP, XARBN, XPOSI etc.)

SIL's `XATP=4`, `XARBN=3`, `XPOSI=24` etc. are the integer dispatch table indexes
for pattern-matching operations. These give us the definitive mapping:

```sil
XANYC  =  1    ANY(cset)
XARBF  =  2    ARB (first — zero chars)
XARBN  =  3    ARBNO                           → E_ARBNO
XATP   =  4    @ cursor capture                → E_CAPT_CUR  (was E_ATP)
XCHR   =  5    single char match
XBAL   =  6    BAL
XBRKC  =  8    BREAK(cset)
XBRKX  =  9    BREAKX
XEARBNO = 13   ARB extended (non-zero advance) → E_ARB
XFARB  = 17    ARB first (0-char try)          → E_ARB (alt encoding)
XNNYC  = 21    NOTANY
XPOSI  = 24    POS(n)                          → E_POS
XRPSI  = 25    RPOS(n)                         → E_RPOS
XRTB   = 26    RTAB
XSALF  = 28    scan alternation fail
XSCOK  = 29    scan continuation ok
XSCON  = 30    scan continuation               → E_MATCH
XSPNC  = 31    SPAN(cset)
XSTAR  = 32    *X deferred reference           → E_DEFER
XRTNL3 = 34    RTNL (return null)
XFNCE  = 35    FENCE                           → E_CUT
XSUCF  = 36    SUCCEED/FAIL
```

---

## Runtime Procedure Names → IR Nodes

Key SIL procedure names that map to our IR nodes:

```sil
ASGN   proc   Assignment X = Y                 → E_ASSIGN  (was E_ASGN)
MNSM   proc   Unary minus (integer)            → E_NEG     (was E_MNS)
MNSR   proc   Unary minus (real)               → E_NEG
PLS    proc   Unary plus — coerces '' to 0     → E_PLS     (NEW; not identity!)
SWAP   proc   :=: exchange                     → E_SWAP
CONCAT proc   Concatenation                    → E_SEQ     (was E_CONC/CONCAT)
ORPP   proc   Pattern alternation OR           → E_ALT     (was E_OR)
SCONCL label  Scan continuation                → E_MATCH
CONCL  label  Concatenation node descriptor    → E_SEQ
```

---

## The `E_PLS` Note — Unary Plus Is Not Identity

In SNOBOL4, unary `+X` is not a no-op. From v311.sil `PLS` proc:

```sil
PLS    PROC   ,          +X
       RCALL  ZPTR,ARGVAL,,FAIL    Get argument
       VEQLC  ZPTR,I,,ARTN         Is it INTEGER? → return as-is
       VEQLC  ZPTR,S,,PLSV         Is it STRING?  → convert
       VEQLC  ZPTR,R,INTR1,ARTN    Is it REAL?    → return as-is
PLSV   LOCSP  XSP,ZPTR             Get specifier
       SPCINT ZPTR,XSP,,ARTN       Convert STRING to INTEGER
       SPREAL ZPTR,XSP,INTR1,ARTN  Convert STRING to REAL
```

The empty string `''` converts to integer 0. A non-numeric string fails.
This is **not** the same as leaving the value alone. `E_PLS` is a genuine
distinct operation — it belongs in the IR alongside `E_NEG`.

---

## Names Where We Departed from SIL

| SIL name | Our name | Why |
|----------|----------|-----|
| `VARTYP` → `VART` | `E_VAR` | Kept — too woven into existing code to change |
| `CONCAT`/`CONCL` | `E_SEQ` | SEQ is more universal (sequence across all 6 languages) |
| `ORPP`/alternation | `E_ALT` | ALT clearer than OR for pattern alternation |
| `MNSM` | `E_NEG` | NEG signals unary clearly; MNS is opaque |
| `EXPOP` | `E_POW` | POW is universally understood |
| `ARYTYP` | `E_IDX` | IDX covers all subscript forms, not just arrays |
| `ATP` | `E_CAPT_CUR` | Shorter; matches `@` operator directly |

---

## The Naming Principle Going Forward

`E_` + **short description of the operation**, not the SIL discriminant number.
Where SIL names are clear (QLIT, ILIT, FLIT, FNC, PLS, NEG, ARB, ARBNO,
POS, RPOS, SWAP), we kept them. Where they were opaque or language-specific
(CONC, OR, MNS, EXPOP, NAM, DOL, ATP, ARY, ASGN), we chose clearer names.

The SIL lineage is documented here so future sessions can trace any `E_*` name
back to its origin — whether it came from a `xxxTYP EQU N` code, a runtime
procedure name, or a pattern dispatch index.
