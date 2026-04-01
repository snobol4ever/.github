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
| **M-SNO2SC-GIMPEL01** | Fibonacci | Gimpel Ch.2 | trivial | ❌ |
| **M-SNO2SC-GIMPEL02** | Sieve of Eratosthenes | Gimpel Ch.3 | easy | ❌ |
| **M-SNO2SC-GIMPEL03** | Quicksort | Gimpel Ch.5 | easy | ❌ |
| **M-SNO2SC-GIMPEL04** | Binary search tree | Gimpel Ch.7 | medium | ❌ |
| **M-SNO2SC-GIMPEL05** | Expression evaluator | Gimpel Ch.9 | medium | ❌ |
| **M-SNO2SC-AI01** | Simple tokenizer | ai-snobol | easy | ❌ |
| **M-SNO2SC-AI02** | Pattern-based NER | ai-snobol | medium | ❌ |
| **M-SNO2SC-AI03** | Recursive descent parser | ai-snobol | medium | ❌ |
| **M-SNO2SC-CLAWS5** | CLAWS5 POS tagger | corpus/claws5.sno | hard | ❌ |
| **M-SNO2SC-TREEBANK** | Treebank parser (wholesale PAT) | corpus/treebank.sno | hard | ❌ |
| **M-SNO2SC-BEAUTY** | beauty.sc full port | beauty.sno | very hard | ❌ |

**All fire → M-SNO2SC-SELFTEST: beauty.sc compiles itself**

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
