## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `crosscheck-ladder` — Sprint 3 of 6 toward M-BEAUTY-CORE |
| **Milestone** | M-BEAUTY-CORE (mock includes first) → M-BEAUTY-FULL (real inc, second) |
| **HEAD** | `dd0a57f` — artifact: beauty_tramp_session94.c — CHANGED, 15641 lines |

---

## ⚡ SESSION 95 FIRST ACTION — Fix 082_keyword_stcount and 100_roman_numeral, then rung 10

### Bug 1: 082_keyword_stcount — &STNO off-by-one

Test: `GT(&STNO, 1) :S(YES)F(NO)` after 2 assignments.
&STNO is mapped to `kw_stcount` in NV_GET_fn. `trampoline_stno(n)` increments
`kw_stcount` at the TOP of each stmt. At the GT statement (stmt 3, line 4 of source),
`kw_stcount` has been incremented 3 times → value is 3. GT(3, 1) should succeed.
But test still outputs "wrong" — so GT is failing. Check: does `kw_stcount` start at 0
or 1? Is it incremented BEFORE or AFTER the GT reads it?

Debug:
```bash
cat > /tmp/stno_debug.sno << 'EOF2'
      X = 1
      X = 2
      OUTPUT = &STNO
EOF2
cd /home/claude/SNOBOL4-tiny && src/sno2c/sno2c -trampoline /tmp/stno_debug.sno > /tmp/t.c 2>/dev/null
gcc -O0 -g /tmp/t.c src/runtime/snobol4/snobol4.c src/runtime/snobol4/mock_includes.c \
    src/runtime/snobol4/snobol4_pattern.c src/runtime/mock_engine.c \
    -Isrc/runtime/snobol4 -Isrc/runtime -Isrc/sno2c -lgc -lm -w -o /tmp/tb 2>/dev/null
timeout 3 /tmp/tb
```
Expected: 3 (or 4 if stcount incremented before OUTPUT line too).
Actually expected for GT(&STNO,1): STNO at that point should be >=2.

### Bug 2: 100_roman_numeral — block_roman_end undefined

Root cause: `roman_end` is a top-level label on a stmt that is inside the
function-body stmt range. Pass 2 block walker emits blocks for top-level stmts
but the range [roman: ... roman_end] is in the function body — those stmts are
skipped in Pass 2. So `block_roman_end` is forward-declared (line 16) and
in the label table (line 555) but never defined as a block function.

Fix location: `src/sno2c/emit.c` Pass 2 block walker (~line 1982).
The walker skips function-body stmts. After the walker loop, we need to
emit block stubs for any labeled stmt that has a label, appeared in Pass 1,
but whose block was never opened/closed in Pass 2.

Track which labels got block functions defined. For any label in the
forward-decl list that was NOT defined, emit:
```c
static void *block_roman_end(void) {
    { void *_r = stmt_1(); if (_r != _tramp_next_73) return _r; }
    ... (stmts in this block) ...
    return block_END;
}
```

Actually simpler: in the Pass 2 loop, DON'T skip function-body stmts for
block grouping — just emit them as their own blocks. The function body stmts
already have their C function (`_sno_fn_roman`) generated separately; the
block grouping just needs to wrap the top-level flow labels.

Simplest fix: track a set `emitted_block_labels`. After Pass 2, for any
label in `tramp_labels[]` that is NOT in `emitted_block_labels` AND is NOT
already covered by the undefined-stub loop, emit a proper block:

```c
// after the block walker loop, before "undefined label stubs":
for each label L in tramp_labels that was NOT emitted as a block:
    find the stmt S with s->label == L
    E("static void *block%s(void) {\n", cs_label(L));
    E("    { void *_r = stmt_%d();\n", sid_of(S));
    E("      if (_r != _tramp_next_%d) return _r; }\n", uid_of(S));
    // find following unlabeled stmts...
    E("    return block_END;\n}\n\n");
```

Check emit.c around lines 1858-1870 (forward decl loop) and 2022-2030
(undefined stub loop) for the full label tracking logic.

### Build commands
```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev
make -C src/sno2c

RT=src/runtime
CORPUS=/home/claude/SNOBOL4-corpus/crosscheck
bash /tmp/run_rung.sh $RT $CORPUS keywords    # target: 11/11
```

### run_rung.sh (recreate if container is fresh)
```bash
cat > /tmp/run_rung.sh << 'SCRIPT'
RT=$1; CORPUS=$2; RUNG=$3
pass=0; fail=0
for sno in $CORPUS/$RUNG/*.sno; do
    name=$(basename $sno .sno)
    ref="${sno%.sno}.ref"
    inp="${sno%.sno}.input"
    [ -f "$ref" ] || continue
    /home/claude/SNOBOL4-tiny/src/sno2c/sno2c -trampoline "$sno" > /tmp/t.c 2>/dev/null
    gcc -O0 -g /tmp/t.c $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
        $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
        -I$RT/snobol4 -I$RT -I/home/claude/SNOBOL4-tiny/src/sno2c -lgc -lm -w -o /tmp/tbin 2>/dev/null
    if [ -f "$inp" ]; then
        got=$(timeout 5 /tmp/tbin < "$inp" 2>/dev/null || true)
    else
        got=$(timeout 5 /tmp/tbin </dev/null 2>/dev/null || true)
    fi
    exp=$(cat "$ref")
    if [ "$got" = "$exp" ]; then
        echo "PASS $name"; pass=$((pass+1))
    else
        echo "FAIL $name"
        diff <(echo "$exp") <(echo "$got") | head -6 | sed 's/^/  /'
        fail=$((fail+1))
    fi
done
echo "--- $RUNG: $pass pass, $fail fail ---"
SCRIPT
```

---

## Crosscheck ladder status (Session 94)

| Rung | Dir | Tests | Status |
|------|-----|-------|--------|
| 1 output | output/ | 8 | ✅ 8/8 |
| 2 assign | assign/ | 8 | ✅ 8/8 |
| 3 concat | concat/ | 6 | ✅ 6/6 |
| 4 arith | arith_new/ | 8 | ✅ 8/8 |
| 5 control | control_new/ | 7 | ✅ 7/7 |
| 6 patterns | patterns/ | 20 | ✅ 20/20 |
| 7 capture | capture/ | 7 | ✅ 7/7 |
| 8 strings | strings/ | 17 | ✅ 17/17 |
| 9 keywords | keywords/ | 11 | ⏳ 9/11 — 2 failures |
| 10 functions | functions/ | 8 | ❌ not started |
| 11 data | data/ | 6 | ❌ |
| 12 beauty.sno | TBD | TBD | ❌ |

**Total so far: 88/90 pass**

Rung 9 remaining failures:
- `082_keyword_stcount` — &STNO reads kw_stcount but GT still fails
- `100_roman_numeral` — block_roman_end not defined in Pass 2 block walker

---

## Fixes made this session (Session 94)

| Fix | File | What |
|-----|------|------|
| E_ATP varname | emit_byrd.c | use pat->left->sval (unary @ via unop uses left, not right) |
| E_ATP beta | emit_byrd.c | beta → omega (was beta → gamma, infinite backtrack loop) |
| DIFFER | snobol4.c | returns NULVCL on success (predicate), not first arg |
| BREAKX | emit_byrd.c | emit_breakx from SPITBOL p_bkx/s_bkx: beta advances 1 past cs-char |
| kw_anchor in ARB | emit_byrd.c | ARB beta checks kw_anchor — if set, beta → omega |
| Keywords wired | snobol4.c | &STCOUNT/&STNO/&STLIMIT/&ANCHOR/&TRIM/&FULLSCAN in NV_GET/SET |

---

## CRITICAL Rules

- **NEVER write the token into any file**
- **NEVER link engine.c** — mock_engine.c only
- **ALWAYS run `git config user.name/email` after every clone**
- **beauty_core (mock includes) FIRST — beauty_full (real inc) SECOND**
- **beauty.sno is NEVER modified — it is syntactically perfect**
- **-INCLUDE is a noop in sno2c lexer — no -I flag needed**
- **Do NOT build SPITBOL or CSNOBOL4 — .ref files ARE the oracle**

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
| 2026-03-15 | Session 90 | Rungs 1-5 37/37; -INCLUDE noop; mock_engine renamed; 5 bugs fixed |
| 2026-03-15 | Session 91 | Rung 6 20/20; bare builtins as E_VART; dynamic POS/TAB args |
| 2026-03-15 | Session 92 | Rung 7 7/7; SNO_MSTART; null replace; pat_is_anchored POS(0) only |
| 2026-03-15 | Session 93 | Rung 8 15/17; ? op; E_NAM cond; coerce_numeric; E_ATP stub |
| 2026-03-15 | Session 94 | Rung 8 17/17; Rung 9 9/11; E_ATP fix; DIFFER fix; BREAKX; keywords |
