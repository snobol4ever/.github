# MILESTONE-SNO2SC.md — SNOBOL4 → Snocone Conversion Program

**Owner:** SC session · **Prefix:** `SNO2SC` · **Trigger:** "sno2sc" or "snobol4 to snocone"

---

## §GOAL

Build a library of idiomatic Snocone programs converted from:
1. **Gimpel** — classic SNOBOL4 programs from Gimpel's *Algorithms in SNOBOL4*
2. **AI-SNOBOL** — AI/NLP programs from the AI-SNOBOL corpus
3. **beauty.sno** — the full beauty compiler (final milestone, depends on all beauty-sc subsystems)

Flagship programs:
- **claws5.sc** — CLAWS part-of-speech tagger (corpus linguistic tool)
- **treebank.sc** — Penn Treebank-style parser (wholesale POS(0)...RPOS(0) pattern approach)

**Final target:** `beauty.sc` compiles itself via `scrip-cc -sc -asm`.

---

## §CONVERSION PHILOSOPHY

Snocone is NOT a line-for-line transliteration of SNOBOL4.
Write idiomatic Snocone — use `while`, `if`, `procedure`, `struct`.

| SNOBOL4 idiom | Snocone idiom |
|---------------|---------------|
| Goto-based loops | `while (1) { ...; if (cond) break; }` |
| `DEFINE + label + :(RETURN)` | `procedure f(a,b) { ... return; }` |
| `DATA('t(f1,f2)')` | `struct t { f1, f2 }` |
| `val = COND(x,y) expr` | `if (COND(x,y)) { val = expr; }` |
| `str POS(0) PAT . cap =` (subject replace) | `SUBSTR` index walk — see NOTE below |
| `+expr` (numeric coerce) | drop it — integers are integers |
| `~(strval)` empty check | `GT(i, SIZE(arr))` or `IDENT(x,'')` carefully |
| `fn = .dummy; nreturn` | keep — correct SPITBOL idiom (deref to '' on call) |
| `epsilon . *fn()` | same in Snocone — works natively |

**NOTE on wholesale pattern approach for treebank.sc:**
SNOBOL4's `str POS(0) PAT RPOS(0) . result` — match full string.
In Snocone: `if (str ? (POS(0) && PAT && RPOS(0) . result)) { ... }`
The `.` capture in pattern context works. `&&` = sequence concat.
Avoid subject replacement (`= rhs`) — use SUBSTR + SIZE walk instead.

---

## §MILESTONE LADDER — M-SNO2SC-*

| ID | Program | Source | Difficulty | Status |
|----|---------|--------|------------|--------|
| **M-SNO2SC-STRINGS** | strings.sc — string utility library | new | easy | ❌ |
| **M-SNO2SC-ARITH** | arith.sc — number utilities | Gimpel | easy | ❌ |
| **M-SNO2SC-ROMAN** | roman.sc — Roman numeral converter | corpus/roman.sno | easy | ❌ |
| **M-SNO2SC-WCOUNT** | wordcount.sc — word counter | corpus/wordcount.sno | trivial | ❌ |
| **M-SNO2SC-TREEBANK** | treebank.sc — Penn Treebank parser (position threading) | corpus/treebank.sno | medium | ❌ |
| **M-SNO2SC-CLAWS5** | claws5.sc — CLAWS5 POS tagger (ARBNO wholesale) | corpus/claws5.sno | medium | ❌ |
| **M-SNO2SC-IO** | io.sc — INPUT/OUTPUT OPSYN | inc/io.sno | hard | ❌ |
| **M-SNO2SC-GEN** | Gen.sc — code generation output | inc/Gen.sno | hard | ❌ |
| **M-SNO2SC-QIZE** | Qize.sc — quoting (needs subj replacement) | inc/Qize.sno | hard | ❌ |
| **M-SNO2SC-TDUMP** | TDump.sc — tree pretty-printer | inc/TDump.sno | hard | ❌ |
| **M-SNO2SC-BEAUTY** | beauty.sc — full port | demo/beauty.sno | very hard | ❌ |

**Tier 1 (no blockers):** STRINGS → ARITH → ROMAN → WCOUNT
**Tier 2 (one non-trivial conversion):** TREEBANK → CLAWS5
**Tier 3 (needs dynamic / io / Gen infrastructure):** IO → GEN → QIZE → TDUMP → BEAUTY

---

## §TIER 1 DETAILS

### strings.sc — 8 utility functions
All pure value operations, no subject replacement needed:
```snocone
procedure Reverse(s, i, n, out)   // SUBSTR walk backwards
procedure Trim(s)                 // strip leading/trailing spaces
procedure TrimLeft(s, i, n)
procedure TrimRight(s, i, n)
procedure Split(s, sep, arr, i, n, start, pos)  // → ARRAY
procedure Join(arr, sep, i, n, out)              // ← ARRAY
procedure StartsWith(s, prefix)   // IDENT(SUBSTR(s,1,SIZE(prefix)), prefix)
procedure EndsWith(s, suffix, n, sn)
```

### arith.sc — 5 number utilities
All iterative (while loops), no SNOBOL4 idioms needed:
```snocone
procedure Fibonacci(n, a, b, t, i)   // iterative
procedure Sieve(n, arr, i, j)        // TABLE as bit array
procedure GCD(a, b, t)               // Euclidean: while DIFFER(b) { t=b; b=REMDR(a,b); a=t; }
procedure Factorial(n, acc, i)       // iterative
procedure IsPrime(n, i)              // trial division to SQRT(n)
```

### roman.sc
Original uses `N RPOS(1) LEN(1) . T =` (subject replacement to strip last digit).
Snocone rewrite: pass index, extract with SUBSTR:
```snocone
procedure Roman(n, i, len, digit, t)
    // walk digits right-to-left: i from SIZE(n) down to 1
    // for each SUBSTR(n, i, 1) look up in '0,1I,2II,...,9IX,'
    // prefix the roman numeral, shift place (I→X→C→M via REPLACE)
```

### wordcount.sc
Original: `LINE ? WPAT =` (consumes match from LINE via subject replacement).
Snocone rewrite: scan by index looking for word boundaries:
```snocone
// Walk line char by char, detect SPAN(WORD) runs
// Increment counter per run
```

---

## §TIER 2 DETAILS

### treebank.sc — Position Threading Pattern
**Key insight:** Instead of mutating `buf` with subject replacement, thread an explicit
position index through all recursive calls. This is MORE idiomatic Snocone and shows
the design difference clearly.

SNOBOL4 `group()` mutates `buf` globally (`:S(RETURN)` after `buf POS(0) ... =`).
Snocone `group(pos)` returns the NEW position — pure functional threading.

```snocone
procedure group(pos, tag, wrd, newpos) {
    // match '(' at pos → pos+1
    if (~(SUBSTR(buf, pos, 1) :: '(')) { freturn; }
    pos = pos + 1;
    // skip whitespace
    while (pos <= SIZE(buf) && SUBSTR(buf,pos,1) ? SPAN(' ' && nl)) { pos = pos + 1; }
    // match word (tag)
    // ... recursive descent, return updated pos
    group = pos;
    return;
}
```

### claws5.sc — Wholesale ARBNO Pattern
The original pattern compiles to one giant ARBNO expression.
In Snocone this translates almost 1:1:
```snocone
claws_info = POS(0) && *do_mem_init() &&
    ARBNO(
        (SPAN(digits) . num && '_CRD :_PUN' && *do_new_sent()
        | (NOTANY('_') && BREAK('_')) . wrd && '_' &&
          (ANY(UCASE) && SPAN(digits && UCASE)) . tag &&
          *do_add_tok())
        && ' ')
    && RPOS(0);
```
Risk: nested alternation through `ARBNO` — test progressively.

---

## §CLAWS5 NOTES

CLAWS5 is a rule-based POS tagger using:
- Suffix rules: `word POS(0) BREAK('') RPOS(N) . suffix` → tag lookup
- Bigram/trigram context rules
- Disambiguation tables

Snocone approach:
- Suffix patterns: `word ? (RTAB(N) . suffix)` — capture last N chars
- Tables as `TABLE()` — same as SNOBOL4
- Procedure per rule class: `procedure ApplySuffixRules(word, tag) { ... }`
- Context window: pass prev/next tokens as args

---

## §TREEBANK NOTES

The **wholesale pattern** approach in treebank.sno:
```snobol4
line  POS(0) '(' tag ' ' word ')' RPOS(0)
```
This matches the entire string at once — no loops, no subject replacement.
In Snocone:
```snocone
if (line ? (POS(0) && '(' && ANY(alpha) . tag && ' ' && REM . word_and_rest)) {
    // process
}
```
Key: `&&` for pattern sequence, `|` for alternation, `.` for capture.
Avoid nested alternation through function args (known stack underflow — SC-16 open issue).

---

## §LIBRARY LAYOUT

```
corpus/programs/snocone/library/
  gimpel/
    fibonacci.sc
    sieve.sc
    quicksort.sc
    bst.sc
    expr_eval.sc
  ai/
    tokenizer.sc
    ner.sc
    rd_parser.sc
  nlp/
    claws5.sc
    treebank.sc
one4all/test/sno2sc/
  gimpel/   ← driver.sc + driver.ref per program
  ai/
  nlp/
```

---

## §BUILD

```bash
FRONTEND=snocone BACKEND=x64 TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
cd /home/claude/one4all
# Run a conversion test:
CORPUS=/home/claude/corpus bash test/sno2sc/run_sno2sc_suite.sh gimpel/fibonacci
# Gate:
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 snocone_x86
```

---

## §FIRST ACTION — SC-17

**Before anything else:** fix `uses_nreturn` in `emit_x64.c`.

Root cause: second-pass scanner resets `cur_np = NULL` on ANY non-function label,
so NRETURN gotos inside `if(){}/while(){}` blocks are missed.
Fix: only reset `cur_np` when hitting `fname.END` (snocone proc terminator) or
a new function-entry label. Internal labels keep `cur_np`.
See SESSIONS_ARCHIVE SC-16 for full analysis and the two-line fix location.

Then:
1. Verify `assign` beauty-sc driver test 4 passes
2. Run full beauty-sc suite → 11/11
3. Commit `emit_x64.c` fix + `emit_x64_snocone.c` unary PERIOD fix
4. Start M-SNO2SC-GIMPEL01 (fibonacci.sc — trivial warm-up)
