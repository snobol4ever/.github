# MILESTONE-SN4PARSE-VALIDATE.md — sno4parse Parser Validation & Extension Milestones

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Session:** SNOBOL4 × x86, sprint 89
**Status:** ACTIVE — Phase 1 in progress

---

## Context

`sno4parse` is the SNOBOL4 frontend parser for the SCRIP stack. It must parse
the full SPITBOL-extended dialect used in the corpus, not just standard SNOBOL4.
The parser replicates CSNOBOL4's `stream()`/syntab mechanism exactly — **the
256-byte chrs[] table values are authoritative from CSNOBOL4 and must never be
changed**. All fixes are in code logic, not table bytes.

The two-way STREAM trace oracle (SNO_TRACE=1) compares sno4parse vs patched
CSNOBOL4 stream-by-stream. Sweep script: `one4all/csnobol4/dyn89_sweep.sh`.

---

## DYN-89 Baseline (session start)

| Status | Count |
|--------|-------|
| OK     | 14    |
| ERR    | 71    |
| HANG   | 0     |
| Total  | 84    |

---

## Phase 1 — Standard SNOBOL4 Parse Correctness (DYN-89)

**Target: 84/84 OK on corpus/programs/snobol4/**

### Fixes applied this session (DYN-89)

| Fix | Root Cause | Result |
|-----|-----------|--------|
| ELEFNC: FORWRD before arg loop | Missing first FORWRD past `(` | arg-whitespace class fixed |
| ELEFNC: second FORWRD after comma | `F(a, b)` space-after-comma | `, b` now positioned correctly |
| ELEFNC: empty arg `F(a,,b)` and `F(a, ,b)` | loop entered EXPR on `,` | NULL node emitted |
| ELEARY: mirror of ELEFNC fixes | `A[i, j]` subscript with space | subscript-whitespace fixed |
| CMPFRM/CMPASP: FORBLK→FORWRD | `=` already consumed separator | replacement value parsed |
| EQTYP at statement start | unindented `OUTPUT = 'x'` → label+EQTYP | CMPFRM routed correctly |
| NSTTYP: FORWRD after `(` | `( SPAN('x') )` space after paren | inner expr positioned correctly |
| Unary+space: FORWRD after unary chain | `? X` space between op and operand | NBLKTB root cause (see below) |

### Fixes applied this session (DYN-90)

| Fix | Root Cause | Result |
|-----|-----------|--------|
| CMPGO UTOTYP/STOTYP/FTOTYP: FORWRD before/after EXPR | Space after `<` hit ELEMTB before token | `:< C >` direct goto fixed |

### DYN-90 end state

| Status | Count |
|--------|-------|
| OK     | 76    |
| ERR    | 8     |
| HANG   | 0     |

### Remaining bugs (sprint 91 priority order)

**1. BRTYPE=1 postfix subscript on call result `f(g(x)[i])`** (6 files)
- In ELEFNC arg loop, after parsing `g(x)`, `[1]` hits BRTYPE=1 (`[`) → error
- Fix: in `expr_prec_continue`, detect `[` as postfix subscript on any expression
- Same fix as M-SN4PARSE-P2C ([] alias for <>)
- Files: beauty_ShiftReduce_driver, beauty_tree_driver, demo/beauty.sno, claws5, TDump, beauty_oracle

**2. Phantom "illegal character" — Qize.sno, io.sno** (2 files)
- SNO_TRACE shows full parse completing with no ST_ERROR
- `sil_error()` fires but parse output looks correct
- Hypothesis: `g_error` not cleared between statements, OR sweep grep picks up error from earlier statement in same file
- Action: check `g_error` lifecycle; verify with `grep -c "ELEMNT: illegal" <output>`

---

## Phase 2 — SPITBOL Extensions (new syn tables)

### Extensions identified from SPITBOL manual (Appendix C + Chapter 15)

**RULE: All 256-byte chrs[] arrays are authoritative from CSNOBOL4/SPITBOL syn.c.
New tables get their own fresh chrs[] matching SPITBOL semantics. Never modify
existing table bytes.**

#### 2A. `?` as binary pattern-match operator (priority 1, left-associative)

From SPITBOL manual §AppC p275-276:
> The question mark symbol (?) is defined to be an explicit binary pattern-matching
> operator. It is left associative and has priority lower than all operators except
> assignment (=). It returns as its value the substring matched from its left argument
> (a string) by its right argument (a pattern).

```
ABCD ? LEN(3) $ OUTPUT ? LEN(1) REM $ OUTPUT
→ prints ABC then BC
```

- **Current:** `?` is unary only (QUESFN — interrogation, returns null if operand succeeds)
- **SPITBOL adds:** `?` as BINARY op at priority 1 (between `=`=0 and `|`=3)
- **Required:**
  - Add `BISNFN` (already defined as 215 in CMPILE.c) to BIOPTB at priority 1
  - Disambiguate: unary `?` (prefix) vs binary `?` (infix after an expression)
  - The parser already distinguishes unary/binary by context — BIOPTB handles binary
  - Check BIOPTB chrs[63]('?') — currently not in BIOPTB → add if missing
- **New table needed:** None — modify BIOPTB entry (but chrs[] bytes are authoritative!)
  - Alternative: BIOPTB is from CSNOBOL4 which does NOT have binary `?`
  - Therefore a NEW table `BIOPTB_SPITBOL` or an extension mechanism is needed
  - Or: post-processing in `expr_prec_continue` to recognize `?` as binary op

#### 2B. Alternative evaluation `(e1, e2, e3)` — comma-list in parens

From SPITBOL manual §AppC p275:
> A selection or alternative construction: (e1, e2, e3, ..., en)
> Evaluate left to right until one succeeds; failure if all fail.

```snobol4
A = ( EQ(B,3), GT(B,20) ) B+1
NEXT = ( INPUT , %EOF )
```

- **Current:** NSTTYP `(expr)` parses one EXPR. Comma inside parens is only
  valid inside function arg lists (ELEFNC).
- **Required:** When ELEMNT sees NSTTYP `(`, parse a comma-separated list of EXPR.
  Each comma-separated item is an alternative. Build E_ALT node (or new E_SELECT).
- **IR node:** `E_SELECT` (new EKind) — n-ary, children = alternatives
- **Execution:** SM_SELECT instruction — try each child, return first success
- **No new syn table needed** — parsing is code logic in NSTTYP branch of ELEMNT

#### 2C. `[]` square-bracket subscripts as alias for `<>`

From SPITBOL manual §AppC p275:
> The array brackets [] may be used instead of <> if desired.
> Thus X[I,J] and X<I,J> are equivalent.

- **Current:** VARTB fires ARYTYP on `<`, nothing on `[`
- **VARTB chrs[] is authoritative** — cannot add `[` to it
- **Required:** New `VARTB_SPITBOL` table OR post-processing:
  - After ELEMTB, if next char is `[`, treat as array subscript
  - Cleanest: in `expr_prec_continue`, recognize `[` as postfix subscript operator
  - This also fixes bug #2 (postfix subscript on call result)

#### 2D. Multiple assignment `A = B = C + 1`

From SPITBOL manual §AppC p275:
> = is treated as a right-associative operator of lowest priority (0).
> Multiple assignments: A[J=J+1] = INPUT

- **Current:** `=` is handled structurally by CMPILE, not as an expression operator
- **Required:** In `expr_prec_continue`, treat `=` as right-assoc binary op at priority 0
- **No new syn table needed** — code logic in BINOP/expr_prec_continue

#### 2E. Embedded pattern match `A = (B ? C = D) + 1`

- Binary `?` inside an expression triggers an embedded match+replace
- Depends on 2A (binary `?`)

#### 2F. Semicolon `;` as statement separator (multiple statements per line)

From SPITBOL manual §Ch15 p188:
> The semicolon character may be used to place several statements on one line.
> Each semicolon terminates the current statement and behaves like a new column one.

- **Current:** `;` is EOSTYP in FRWDTB — treated as end-of-statement
- **Required:** At the top-level read loop, after a `;` is seen, continue parsing
  the same line buffer as a new statement
- **No new syn table needed** — loop logic in `parse_program()`

---

## Phase 2 Validation — crosscheck/ suite — 2026-04-05 (sprint 101)

**Result: 181/181 OK · 0 ERR · 0 HANG** ✅

All 181 `.sno` files in `corpus/crosscheck/` parse cleanly with zero errors.
This is the Phase 2 validation gate per MILESTONE plan. **PASSED.**

Broader sweeps:
- `corpus/programs/snobol4/` — 84/84 OK (baseline)
- `corpus/programs/gimpel/` — 143/145 OK, 2 ERR (both CSNOBOL4-confirmed), 0 HANG
  - PHRASES.sno: grammar data file, not SNOBOL4 source
  - TR.sno: unresolved `-INCLUDE "push.sno"` — CSNOBOL4 Error 30

---

## Phase 3 — UTF-8 / Unicode Support

### Design

SNOBOL4's string model is byte-oriented (each `stream()` call operates on bytes).
UTF-8 adds multi-byte code points. The syntab mechanism (256-byte chrs[] arrays)
operates on individual bytes — which is exactly right for UTF-8 prefix bytes.

**Key insight:** UTF-8 byte ranges are disjoint and well-defined:
- `0x00–0x7F`: ASCII (single-byte, handled by existing tables unchanged)
- `0xC0–0xDF`: 2-byte sequence lead byte
- `0xE0–0xEF`: 3-byte sequence lead byte
- `0xF0–0xF7`: 4-byte sequence lead byte
- `0x80–0xBF`: continuation bytes

**Strategy: Extension tables, not modification of existing tables.**

### Milestone 3A — UTF8TB: UTF-8 lead-byte dispatcher

New 256-byte table `UTF8TB`:
- `0x00–0x7F` → ACT_CONTIN (fast path, ASCII unchanged)
- `0x80–0xBF` → ACT_ERROR (bare continuation byte — malformed)
- `0xC0–0xDF` → ACT_GOTO → UTF8_2TB (2-byte sequence)
- `0xE0–0xEF` → ACT_GOTO → UTF8_3TB (3-byte sequence)
- `0xF0–0xF7` → ACT_GOTO → UTF8_4TB (4-byte sequence)
- `0xF8–0xFF` → ACT_ERROR (invalid in modern UTF-8)

### Milestone 3B — VARTB_U / ELEMTB_U: Unicode identifiers

SPITBOL identifiers are `[A-Za-z][A-Za-z0-9_]*`. For Unicode:
- Lead bytes of Unicode letters (U+0080+) should be VARTYP in ELEMTB_U
- Continuation bytes absorbed by VARTB_U
- New tables ELEMTB_U and VARTB_U extend the ASCII tables with UTF-8 awareness

### Milestone 3C — String primitives: SIZE, SUBSTR, REPLACE in UTF-8

- `SIZE(s)` → character count (not byte count)
- `SUBSTR(s,i,n)` → substring by character position
- Pattern primitives: `LEN(n)` matches n characters (not bytes)
- Implementation: runtime functions become UTF-8 aware; parser is unaffected

### Milestone 3D — QLITB_U: UTF-8 in quoted string literals

- Quoted strings `'...'` and `"..."` already pass bytes through unchanged
- SQLITB/DQLITB need no change for parsing
- Runtime storage: strings are byte arrays; UTF-8 is transparent
- Only SIZE/SUBSTR/pattern primitives need character-vs-byte awareness

---

## Milestone Summary Table

| Milestone | Description | Deps | Status |
|-----------|-------------|------|--------|
| **M-SN4PARSE-P1** | 84/84 standard SNOBOL4 parse | — | ⚠️ 76/84 |
| M-SN4PARSE-P1a | Unary+space fix (NBLKTB logic) | — | ✅ already works — was phantom |
| M-SN4PARSE-P1b | Postfix subscript `f()[i]` | — | ⬜ sprint 91 |
| M-SN4PARSE-P1c | Qize/io g_error lifecycle | — | ⬜ sprint 91 |
| **M-SN4PARSE-P2A** | Binary `?` pattern-match operator | P1 | ✅ sprint 94 |
| **M-SN4PARSE-P2B** | Alternative eval `(e1,e2,en)` | P1 | ✅ sprint 98-ext |
| **M-SN4PARSE-P2C** | `[]` subscript = `<>` + postfix subscript | P1 | ✅ sprint 96 |
| **M-SN4PARSE-P2D** | Multiple assignment `A=B=C+1` | P1 | ⬜ |
| M-SN4PARSE-P2E | Embedded match `(B?C=D)` | P2A+P2D | ⬜ |
| **M-SN4PARSE-P2F** | Semicolon multi-statement | P1 | ✅ sprint 92 |
| **M-SN4PARSE-P3A** | UTF8TB dispatch table | P2 | ⬜ |
| **M-SN4PARSE-P3B** | VARTB_U / ELEMTB_U Unicode idents | P3A | ⬜ |
| M-SN4PARSE-P3C | UTF-8 string primitives (runtime) | P3A | ⬜ |
| M-SN4PARSE-P3D | QLITB_U (transparent, low risk) | P3A | ⬜ |

---

## Implementation Notes

### Table authority rule
> **The 256-byte chrs[] array of every table that exists in CSNOBOL4 syn.c is
> authoritative and must not be modified.** All SPITBOL and Unicode extensions
> use NEW tables with their own chrs[] arrays. Linkage (`.go` pointers) from
> existing tables to new tables is permitted via `init_tables()` patching.

### BIOPTB extension for binary `?`
CSNOBOL4's BIOPTB does not include `?`. SPITBOL adds it at priority 1.
Since we cannot modify BIOPTB chrs[], the approach is:
- In `BINOP()`, after BIOPTB returns ST_ERROR for `?`, check if current char is `?`
  and return `BISNFN` (215) with priority 1 as a special case.
- Or: build `BIOPTB_EXT` that starts from BIOPTB and adds `?`.

### Sweep script
`one4all/csnobol4/dyn89_sweep.sh` — run against corpus/programs/snobol4/.
Output: one line per file, OK/ERR/HANG + first error message.

### Session start for next DYN session
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/MILESTONE-SN4PARSE-VALIDATE.md
gcc -O0 -g -Wall -o one4all/sno4parse one4all/src/frontend/snobol4/CMPILE.c
bash one4all/csnobol4/dyn89_sweep.sh   # baseline: ~73 OK / 11 ERR / 0 HANG
```
