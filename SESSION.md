## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `crosscheck-ladder` — Sprint 3 of 6 toward M-BEAUTY-CORE |
| **Milestone** | M-BEAUTY-CORE (mock includes first) → M-BEAUTY-FULL (real inc, second) |
| **HEAD** | `4e0831d` — fix(emit_byrd): bare builtin patterns + dynamic POS/RPOS/TAB/RTAB args |

---

## ⚡ SESSION 92 FIRST ACTION — Fix rung 7 capture (3 failures)

Rungs 1–6 are 57/57 clean. Rung 7 capture: 4/7. Fix these three in order:

### Failure 1: 061_capture_in_arbno (off-by-one with POS(N))
```
X = 'aaa'
N = 0
LOOP  X POS(N) 'a' . V   :F(DONE)
      OUTPUT = V
      N = N + 1
      :(LOOP)
```
Expected: a / a / a. Got: a / a (only 2). Dynamic POS(N) now works.
Debug: add trace prints — check if N reaches 2 and POS(2) fails on 'aaa' (len=3, pos 2 is valid).
POS(2) should match position 2 ('a'). If cursor resets to 0 each statement, POS(N) with N=2
checks cursor==2 but cursor starts at 0 — ARB must advance to 2 first. Check ARB emit.

### Failure 2 & 3: 062/063 — _mstart bug (replacement splices from pos 0)

Root cause: `_mstart = _cur` set BEFORE ARB prefix scan. ARB advances cursor to find match,
but _mstart stays 0. Replacement then splices `subject[0.._mstart]` = entire subject.

**Fix in emit.c — insert SNO_MSTART synthetic node:**

```c
/* In emit.c, the ARB-prepend block: */
if (!pat_is_anchored(s->pattern)) {
    EXPR_t *arb = expr_new(E_FNC);
    arb->sval = strdup("ARB");
    arb->nargs = 0;

    /* NEW: synthetic zero-width node that captures cursor into _mstart */
    EXPR_t *mstart = expr_new(E_FNC);
    mstart->sval = strdup("SNO_MSTART");
    mstart->nargs = 0;

    EXPR_t *seq1 = expr_new(E_CONC);
    seq1->left  = arb;
    seq1->right = mstart;

    EXPR_t *seq2 = expr_new(E_CONC);
    seq2->left  = seq1;
    seq2->right = s->pattern;
    scan_pat = seq2;
}
```

**In emit_byrd.c E_FNC handler, add before the existing builtin checks:**
```c
if (strcasecmp(n, "SNO_MSTART") == 0) {
    /* Zero-width: capture current cursor into _mstart for this statement.
     * The _mstart var name is _mstartN where N is the statement uid.
     * We need the uid — thread it via a global or encode in sval. */
    /* Approach: store uid in pat->ival when building the node in emit.c */
    int u = (int)pat->ival;   /* uid set by emit.c when building node */
    char mstart_var[32]; snprintf(mstart_var, sizeof mstart_var, "_mstart%d", u);
    PL(alpha, gamma, "%s = %s;", mstart_var, cursor);
    PLG(beta, omega);
    return;
}
```

**In emit.c:** set `mstart->ival = u` (the statement uid) when building the node.
**Also:** remove the upfront `E("_mstart%d = _cur%d;\n", u, u)` line (it becomes wrong).

**Build commands:**
```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
CORPUS=/home/claude/SNOBOL4-corpus/crosscheck

# Run rung 7:
for sno in $CORPUS/capture/*.sno; do
    name=$(basename $sno .sno); ref="${sno%.sno}.ref"
    [[ -f "$ref" ]] || continue
    src/sno2c/sno2c -trampoline "$sno" > /tmp/t.c 2>/dev/null
    gcc -O0 -g /tmp/t.c $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
        $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
        -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o /tmp/tbin 2>/dev/null
    got=$(timeout 5 /tmp/tbin </dev/null 2>/dev/null || true)
    exp=$(cat "$ref")
    if [[ "$got" == "$exp" ]]; then echo "PASS $name"
    else echo "FAIL $name"; diff <(echo "$exp") <(echo "$got") | head -4 | sed 's/^/  /'; fi
done
```

⚠️ NEVER write the token into any file
⚠️ NEVER link engine.c — mock_engine.c only
⚠️ beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno`

---

## Crosscheck ladder status (Session 91)

| Rung | Dir | Tests | Status |
|------|-----|-------|--------|
| 1 output | output/ | 8 | ✅ 8/8 |
| 2 assign | assign/ | 8 | ✅ 8/8 |
| 3 concat | concat/ | 6 | ✅ 6/6 |
| 4 arith | arith_new/ | 8 | ✅ 8/8 |
| 5 control | control_new/ | 7 | ✅ 7/7 |
| 6 patterns | patterns/ | 20 | ✅ 20/20 |
| 7 capture | capture/ | 7 | ⏳ 4/7 — 3 failures |
| 8 strings | strings/ | 17 | ❌ |
| 9 keywords | keywords/ | 11 | ❌ |
| 10 functions | functions/ | 8 | ❌ |
| 11 data | data/ | 6 | ❌ |
| 12 beauty.sno | TBD | TBD | ❌ |

**Total so far: 61/64 pass**

---

## Fixes made this session (Session 91)

| Fix | File | What |
|-----|------|------|
| Bare builtin patterns as E_VART | emit_byrd.c | REM/ARB/FAIL/SUCCEED/FENCE/ABORT w/o parens now route to correct emitters |
| Dynamic POS/RPOS/TAB/RTAB args | emit_byrd.c | Non-literal args emit to_int(NV_GET_fn("var")); added _expr variants |
| Artifact session79 | artifacts/ | beauty_tramp_session79.c — 15452 lines, md5=e0ebfbf38e866f92e28a999db182a6a2 |

---

## Generative oracle plan (after rungs 1–11 pass)

After all rungs clean: generate tiny SNOBOL4 programs from length 0 upward (0 tokens, 1 token, 2 tokens…). Claude generates candidates, Lon cherry-picks keepers into corpus. Grows the test suite systematically from first principles.

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — mock_engine.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND**
- **beauty.sno is NEVER modified — it is syntactically perfect**
- **-INCLUDE is a noop in sno2c lexer — no -I flag needed**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 85 cleanup | agreement breach resolved, rename audit |
| 2026-03-14 | Session 87 renames | inc_stubs→inc_mock, snobol4_inc→mock_includes |
| 2026-03-14 | Session 88 bug fix | nInc beta now emits NDEC_fn() — ntop leak resolved |
| 2026-03-15 | Session 89 PIVOT | crosscheck-ladder replaces smoke test |
| 2026-03-15 | Session 90 | Rungs 1-5 37/37; -INCLUDE noop; inc_mock deleted; engine_stub→mock_engine; 5 bugs fixed |
| 2026-03-15 | Session 91 | Rung 6 20/20; bare builtins as E_VART fixed; dynamic POS/TAB args fixed; rung 7 4/7 |

Rungs 1–5 are 37/37 clean. Next: rung 6 patterns.

**Build commands:**
```bash
cd /home/claude/repos/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
CORPUS=/home/claude/repos/SNOBOL4-corpus/crosscheck

# Run a rung:
for sno in $CORPUS/patterns/*.sno; do
    name=$(basename $sno .sno); ref="${sno%.sno}.ref"
    [[ -f "$ref" ]] || continue
    src/sno2c/sno2c -trampoline "$sno" > /tmp/t.c 2>/dev/null
    gcc -O0 -g /tmp/t.c $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
        $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
        -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o /tmp/tbin 2>/dev/null
    got=$(timeout 5 /tmp/tbin </dev/null 2>/dev/null || true)
    exp=$(cat "$ref")
    if [[ "$got" == "$exp" ]]; then echo "PASS $name"
    else echo "FAIL $name"; diff <(echo "$exp") <(echo "$got") | head -4 | sed 's/^/  /'; fi
done
```

⚠️ -INCLUDE is a noop in lexer — no -I flag needed for sno2c
⚠️ engine_stub.c is now mock_engine.c
⚠️ NEVER write the token into any file
⚠️ NEVER link engine.c — mock_engine.c only
⚠️ beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND

Oracle: `test/smoke/outputs/session50/beauty_oracle.sno`

---

## Crosscheck ladder status (Session 90)

| Rung | Dir | Tests | Status |
|------|-----|-------|--------|
| 1 output | output/ | 8 | ✅ 8/8 |
| 2 assign | assign/ | 8 | ✅ 8/8 |
| 3 concat | concat/ | 6 | ✅ 6/6 |
| 4 arith | arith_new/ | 8 | ✅ 8/8 |
| 5 control | control_new/ | 7 | ✅ 7/7 |
| 6 patterns | patterns/ | 20 | ⏳ next |
| 7 capture | capture/ | 7 | ❌ |
| 8 strings | strings/ | 17 | ❌ |
| 9 keywords | keywords/ | 11 | ❌ |
| 10 functions | functions/ | 8 | ❌ |
| 11 data | data/ | 6 | ❌ |
| 12 beauty.sno | TBD | TBD | ❌ |

**Total so far: 37/37 pass**

---

## Fixes made this session (Session 90)

| Fix | File | What |
|-----|------|------|
| &ALPHABET SIZE=256 | snobol4.c | Registered in NV; SIZE checks pointer identity |
| POWER_fn integer | snobol4.c | int**int returns int, not real |
| REMDR builtin | snobol4.c | Integer remainder, registered |
| E_MNS e->left | emit.c + emit_cnode.c | Unary minus used e->right (NULL) — fixed to e->left |
| null assign | emit.c + parse.c + sno2c.h | STMT_t.has_eq flag; X= emits NV_SET_fn(var,NULVCL) |
| -INCLUDE noop | lex.c | Silently dropped — no file open, no error |
| inc_mock/ deleted | — | 19 comment-only stubs removed |
| engine_stub→mock_engine | runtime/ | Rename for clarity |
| crosscheck-ladder Sprint 3 | PLAN.md | Formally added as Sprint 3 of 6 with rung table |

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — mock_engine.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND**
- **beauty.sno is NEVER modified — it is syntactically perfect**
- **-INCLUDE is a noop in sno2c lexer — no -I flag needed**

---

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-14 | PIVOT: block-fn + trampoline model | complete rethink with Lon |
| 2026-03-14 | Session 84 SIL rename | DESCR_t/DTYPE_t/XKIND_t/_fn/_t throughout |
| 2026-03-14 | Session 85 cleanup | agreement breach resolved, rename audit |
| 2026-03-14 | Session 87 renames | inc_stubs→inc_mock, snobol4_inc→mock_includes |
| 2026-03-14 | Session 88 bug fix | nInc beta now emits NDEC_fn() — ntop leak resolved |
| 2026-03-15 | Session 89 PIVOT | crosscheck-ladder replaces smoke test |
| 2026-03-15 | Session 90 | Rungs 1-5 37/37; -INCLUDE noop; inc_mock deleted; engine_stub→mock_engine; 5 bugs fixed |
