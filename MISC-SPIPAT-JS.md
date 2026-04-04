# ARCH-spipat-js.md — spipatjs Architecture Lessons for SNOBOL4×JS

**Source:** `github.com/philbudne/spipatjs` — ES6 port of GNAT.SPITBOL.PATTERNS
**Studied:** SJ-3, 2026-04-01, Claude Sonnet 4.6
**Relevance:** Authoritative reference for SNOBOL4 pattern matching in JavaScript.
Phil Budne is a core SPITBOL contributor (author of SPITBOL x32/x64 fork).
This is the definitive JS pattern engine — study before writing any pattern runtime.

---

## What spipatjs Is

A native ES6 reimplementation of SNOBOL4/SPITBOL pattern matching, translated
from Phil Budne's C port of GNAT (GNU Ada Translator) `gnat.spitbol.patterns`.
Lineage: Ada (AdaCore 1998–2013) → C (Budne) → JavaScript (Budne 2019).

Single file: `spipat.mjs` — 3090 lines, ES6 module. Test suite: `tests.mjs`.

---

## Core Architecture: PE Node Graph + Explicit Stack

spipatjs uses the **GNAT model**, NOT the Byrd-box trampoline model.
These are two different correct implementations of the same SNOBOL4 semantics.

### GNAT model (spipatjs)

```
Pattern = immutable linked graph of PE (Pattern Element) nodes
Match   = mutable match state: subject, cursor, explicit Stack
Engine  = while(node) { switch(node.match(m)) { M_Succeed/M_Fail/M_Continue/M_Pattern_Success/M_Pattern_Fail } }
```

- Each PE subclass implements `match(m)` returning one of 5 M_* constants.
- `M_Succeed` → follow `pthen` (forward link).
- `M_Fail` → pop stack frame (restore cursor + node), retry from there.
- `M_Continue` → node changed itself (e.g. Alt stacks alt, moves to pthen).
- Backtrack state stored in explicit `Stack` of `{cursor, node}` pairs.
- No recursion. No JS call stack growth.

### Byrd-box trampoline model (our emit_js.c)

```
Compiled pattern = set of labeled JS functions (ports α/β/γ/ω per node)
Engine           = let pc = block_START; while(pc) pc = pc();
Backtrack        = ω ports follow static wiring back up the tree
```

- Pattern is compiled to code, not a runtime graph.
- No explicit stack object — backtrack is encoded in port wiring.
- ARBNO backtrack uses a JS array (`_saved[]`) for cursor history.

**KEY DECISION (SJ-1, do not re-debate):** We emit Byrd-box trampoline, not
GNAT model. Reasons: (1) consistent with x64/JVM/.NET emitters; (2) no runtime
graph construction overhead; (3) JIT-friendly integer switch dispatch.

---

## What to Borrow from spipatjs

### 1. Unicode-correct subject scanning

spipatjs explodes the subject string into a rune array:
```js
this.subject = Array.from(subject);  // handles surrogate pairs
this.length  = this.subject.length;  // rune count, not UTF-16 unit count
```

Our `sno_runtime.js` currently uses raw JS string indexing (`subject[i]`).
**Action (M-SJ-A04+):** adopt `Array.from()` for subject. Positions become
rune indices. `subject.slice(start, end).join('')` for substring extraction.
This is the correct model for any non-ASCII SNOBOL4 program.

### 2. Unanchored scan loop

spipatjs handles unanchored matching via a sentinel PE node `PE_Unanchored`
stacked at `init`. On failure it increments cursor and retries. In our model:

```js
// emitted in block_START for each MATCH statement:
for (let _scan = 0; _scan <= subject.length; _scan++) {
    cursor = _scan;
    let result = _trampoline(pat_entry);
    if (result === MATCHED) break;
}
```

This is already our approach. spipatjs confirms it is correct.

### 3. Assign-on-match (E_CAPT_COND) scan after success

spipatjs scans the history stack after `M_Pattern_Success` to fire
`CP_Assign` callbacks. In our Byrd-box model, the γ (success) port of
the capture node fires immediately on match thread — no post-scan needed.
This is an **advantage of the Byrd-box model** over GNAT: captures are
simpler.

### 4. ARBNO correct zero-advance guard

```js
// PE_Arbno_Y.match():
if (m.cursor === old_cursor) return M_Fail;  // no progress → fail
```

Our current ARBNO stub does not implement this. The zero-advance guard
is **mandatory** — without it, ARBNO can loop forever on a zero-width match.

**Action (M-SJ-A03):** implement in our ARBNO γ port:
```js
function P_ARBNO_Y_gamma() {
    if (cursor === _arbno_entry_cursor) return omega_outer;  // no progress
    _saved[_sp++] = cursor;
    return P_ARBNO_Y_alpha;  // try another iteration
}
```

### 5. BAL implementation

spipatjs `PE_Bal.match()` counts parens inline — simple loop. Copy directly
into our `sno_runtime.js` as `_sno_bal(subject, cursor)` → new cursor or -1.

### 6. Rune-aware character sets (ANY/NOTANY/SPAN/BREAK)

spipatjs uses `Set` of rune strings (from `cset(str)`), not char codes.
For ANY/NOTANY/SPAN/BREAK/NSPAN with a string argument, our emitter
should emit the set as a JS `Set` literal in the emitted code:
```js
const _set_N = new Set([..."AEIOU"]);  // emitted once per pattern
```
This handles multi-byte chars correctly.

---

## What NOT to adopt

### Do NOT adopt the PE node graph at runtime

spipatjs builds Pattern objects at runtime (user-level `arbno(span("AEIOU"))` etc.).
We compile patterns to code at compile time. Our emitter IS the "pattern compiler".
Do not add a runtime Pattern graph — it adds allocation overhead for no gain.

### Do NOT adopt the Stack class

Our Byrd-box wiring encodes backtrack in port functions statically. We only need
a `_saved[]` array for ARBNO cursor history (one array per ARBNO node, pre-allocated).
The explicit Stack object is GNAT-model only.

### Do NOT adopt M_* return constants

Our port functions return the next port function (trampoline), not enum constants.
The `for(;;) switch(_pc)` dispatch is our integer-switch model — keep it.

---

## Relationship to Our IR Nodes

| spipatjs export | Our IR E_ node | Notes |
|----------------|---------------|-------|
| `arb` | `E_ARB` | Arb_X (push alt) + Arb_Y (extend) |
| `arbno(p)` | `E_ARBNO` | Simple (Arbno_S) or complex (Arbno_X+Y) |
| `or(a,b)` | `E_ALT` | PE_Alt stacks alt arm |
| `and(a,b)` | `E_SEQ` | pthen chaining |
| `any(str)` | `E_ANY` | Set membership |
| `notany(str)` | `E_NOTANY` | Set non-membership |
| `span(str)` | `E_SPAN` | Greedy set match ≥1 |
| `nspan(str)` | `E_NSPAN` (E_NSPAN) | Non-backtracking span |
| `breakp(str)` | `E_BREAK` | Match up to set char |
| `breakx(str)` | `E_BREAKX` | Break with backtrack extension |
| `len(n)` | `E_LEN` | Match exactly n chars |
| `pos(n)` | `E_POS` | Assert cursor at position n |
| `rpos(n)` | `E_RPOS` | Assert cursor at n from end |
| `tab(n)` | `E_TAB` | Advance cursor to n |
| `rtab(n)` | `E_RTAB` | Advance cursor to n from end |
| `rem` | `E_REM` | Match rest of subject |
| `fail` | `E_FAIL` | Always fail |
| `fence` | `E_FENCE` | Match null, cut on backtrack |
| `abort` | `E_ABORT` | Abort entire match |
| `bal` | `E_BAL` | Balanced paren match |
| `succeed` | `E_SUCCEED` | Always succeed (with backtrack) |
| `cursor(v)` | `E_CAPT_CUR` | Capture cursor position |
| `imm(p,f)` | `E_CAPT_IMM` | Immediate action on match |
| `onmatch(p,f)` | `E_CAPT_COND` | Action deferred to match success |
| `pat(str)` | literal string → `E_QLIT` | |

---

## Unicode Positions: 1-based vs 0-based

spipatjs uses **1-based** positions (`start`, `stop`) matching SNOBOL4 semantics
(`POS(1)` is start of string). Internally cursors are 0-based rune indices.

Our emitter: cursors are 0-based. `POS(n)` in SNOBOL4 → `E_POS` with n-1 internally,
OR emit `if (cursor !== n-1) return omega`. Confirm against SPITBOL oracle.

---

## ARBNO: Simple vs Complex

spipatjs distinguishes:
- **Simple ARBNO** (`PE_Arbno_S`): pattern always matches ≥1 char, no stack
  entries. Cheaper — just loop.
- **Complex ARBNO** (`PE_Arbno_X` + `PE_Arbno_Y`): general case with region
  stack management.

Our `emit_js.c` should emit the simple form when `ok_for_simple_arbno` is true
(i.e. the pattern body cannot match empty). Check `ir.h` for this flag — the
x64 emitter already distinguishes these cases.

---

## Practical Import Strategy

spipatjs is GPL-3 + GCC Runtime Library Exception.
**Do NOT copy code into one4all** (different license).
**DO use it as:**
1. Behavioral oracle for pattern matching tests — run spipatjs on same inputs
   as our emitter, compare outputs.
2. Architecture reference for correct ARBNO/BAL/BREAKX semantics.
3. Unicode-correct subject handling reference.

For the corpus, `.ref` files are generated by SPITBOL (authoritative).
spipatjs can generate additional `.ref` candidates for pure-pattern tests.

---

## Summary: Decision Log for SJ-3

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Pattern engine model | Byrd-box trampoline (keep) | Consistent with all other backends; compile-time not runtime |
| Unicode subject | `Array.from(subject)` (adopt M-SJ-A04+) | Correct surrogate-pair handling |
| ARBNO zero-advance guard | Adopt (M-SJ-A03) | Mandatory correctness |
| Character sets | `new Set([...str])` (adopt M-SJ-B05+) | Unicode-correct |
| BAL runtime helper | Copy logic (not code) into sno_runtime.js | Simple paren counter |
| spipatjs as oracle | Yes, for pure pattern rungs | Behavioral reference |
| License | GPL-3 + Runtime Exception — reference only | Do not import source |

---

*ARCH-spipat-js.md — created SJ-3, 2026-04-01, Claude Sonnet 4.6.*
