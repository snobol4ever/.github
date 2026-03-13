# SESSION.md — Live Handoff

> This file is fully self-contained. A new Claude reads this and nothing else to start working.
> Updated at every HANDOFF. History lives in SESSIONS_ARCHIVE.md.

---

## Active Session

| Field | Value |
|-------|-------|
| **Repo** | SNOBOL4-tiny |
| **Sprint** | `beauty-full-diff` (4 of 4 toward M-BEAUTY-FULL) |
| **Milestone** | M-BEAUTY-FULL |
| **HEAD** | `f359079` — fix(sno2c): parse_expr2 for pattern field — replacement-stmt segfault fixed |

## Last Thing That Happened

### What was fixed this session

**Fix 1 — parse_expr4 | alternation ✅ (prior session, confirmed working)**
`parse_expr4` concat loop used `LexMark` instead of `skip_ws` + synthetic T_WS injection.
`*a | *b | *c` and `FENCE(*a | *b | *c)` now emit correct `sno_pat_alt` chains.
`snoCommand` in beauty_full.c now has all three branches — confirmed in compiled C.

**Fix 2 — replacement-statement segfault ✅ (this session)**
`parse_body_field` called `parse_expr0` for the pattern field. `parse_expr0` saw the
trailing `=` of a replacement statement (`subject pattern =`) as an assignment operator,
building `E_ASSIGN(pattern_expr, NULL)`. `emit_expr` then called `cs(e->left->sval)` on
a non-variable node (sval=NULL) → SIGSEGV.

Fix: changed `parse_body_field` line 712 to call `parse_expr2` instead of `parse_expr0`.
`parse_expr2` handles `&` (reduce) but not `=` or `?`, so the trailing `=` is left for
`parse_body_field` to handle as the replacement separator.

Verified: `X POS(0) SPAN(&UCASE &LCASE) =` no longer crashes.
`is.sno`, `io.sno`, `case.sno` all compile clean.
`beauty.sno` compiles to 12,744 lines of C, gcc clean.

**Fix 3 — parse_expr2 broke | in pattern field ❌ (new regression)**
Using `parse_expr2` for the pattern field ALSO stopped `|` alternation in patterns from
working — `|` is handled at `parse_expr3`, which is above `parse_expr2`.

So smoke tests are STILL 0/21 and binary still outputs only 10 lines.

**Root cause of remaining problem:**
The pattern field needs a level that:
- INCLUDES `|` alternation (parse_expr3 level)
- EXCLUDES `=` assignment (parse_expr0 level)
- EXCLUDES `?` conditional scan (parse_expr0 level)

The correct fix: add a new `parse_pat_expr()` function that calls `parse_expr3` directly,
bypassing `parse_expr0`'s `=`/`?` handling. OR: make `parse_expr0` stop at `=` when
a `in_pattern` flag is set.

**Simplest correct fix:**
```c
/* In parse_body_field, replace: */
s->pattern = parse_expr2(lx);

/* With: */
s->pattern = parse_expr3(lx);   /* includes |, excludes =, excludes ? */
```

`parse_expr3` handles `|` alternation and calls down to `parse_expr4` (concat) and
`parse_expr5+` (atoms). It does NOT handle `=` or `?`. This is exactly right for
the pattern field.

BUT: after `parse_expr3` returns, `parse_body_field` checks for WS then `=`.
With `parse_expr3`, the pattern includes `&` (reduce) too — that's fine for SNOBOL4
patterns. Test carefully with:
- `X 'hello' = 'world'` (replacement with literal pattern)  
- `X POS(0) SPAN(&UCASE &LCASE) =` (was segfaulting)
- `X ('a' | 'b' | 'c')` (alternation in pattern)
- `snoLabel = BREAK(' ' tab nl ';') ~ 'snoLabel'` (complex assignment pattern)

## One Next Action

**Change `parse_expr2` → `parse_expr3` on line ~712 of parse.c:**

```bash
cd /home/claude/SNOBOL4-tiny
# The line currently reads:
#   s->pattern = parse_expr2(lx);
# Change to:
#   s->pattern = parse_expr3(lx);

python3 -c "
import re
with open('src/sno2c/parse.c') as f: c = f.read()
old = 's->pattern = parse_expr2(lx);'
new = 's->pattern = parse_expr3(lx);  /* includes |, excludes = and ? */'
assert old in c
c = c.replace(old, new)
open('src/sno2c/parse.c','w').write(c)
print('done')
"

make -C src/sno2c

# Verify no segfault
cat > /tmp/test_repl.sno << 'EOF'
        X = 'hello world'
        X POS(0) SPAN(&UCASE &LCASE) =
        OUTPUT = X
END
EOF
src/sno2c/sno2c /tmp/test_repl.sno > /dev/null && echo "no crash"

# Verify | still works in pattern
cat > /tmp/test_alt.sno << 'EOF'
        X = 'b'
        X ('a' | 'b' | 'c') . V  :S(YES)
        OUTPUT = 'fail'
        :(END)
YES     OUTPUT = V
END
EOF
src/sno2c/sno2c /tmp/test_alt.sno > /tmp/test_alt.c && \
R=src/runtime/snobol4 && \
gcc -O0 /tmp/test_alt.c $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c -I$R -Isrc/runtime -lgc -lm -w -o /tmp/test_alt_bin && \
/tmp/test_alt_bin && echo "alt works"

# Rebuild beauty
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c

R=src/runtime/snobol4
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c \
    -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

# Smoke tests
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin
```

After smoke tests pass → run crosscheck suite → diff oracle.

## Debug Context — nl Variable Issue

During debugging this session, found that `subj=(0)` in pattern debug means subject
is empty. Traced to `nl` variable initialization. `global.sno` sets `nl` via:

```
&ALPHABET  POS(10)  LEN(1) . nl
```

This is a PATTERN MATCH on `&ALPHABET` to capture the newline character into `nl`.
Our runtime may not be executing this correctly (it's in init code, not a function).
IF parse_expr3 fix doesn't fully resolve smoke tests, the nl init is the next suspect.
Check: does `snoSrc = snoSrc snoLine nl` produce a non-empty string in our binary?

## Rebuild Commands

```bash
cd /home/claude/SNOBOL4-tiny

# sno2c rebuild
make -C src/sno2c

# beauty compile
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c

# beauty binary
R=src/runtime/snobol4
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c \
    -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

# smoke tests
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin

# crosscheck suite (after smoke passes)
bash /home/claude/SNOBOL4-corpus/crosscheck/run_all.sh

# oracle
SNO=/home/claude/snobol4-2.3.3/bin/snobol4
$SNO -f -P256k -I /home/claude/SNOBOL4-corpus/programs/inc \
    /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    < /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    > /tmp/beauty_oracle.sno 2>/dev/null

diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
```

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | parse_expr2 for pattern field — segfault fixed, but | broken | parse_expr0 ate trailing = |
| 2026-03-13 | 106-test crosscheck suite built, committed to corpus | Lon: need lampposts |
| 2026-03-13 | parse_expr4 | alternation fixed via LexMark | double-WS ate | token |
| 2026-03-13 | parse_expr0 LexMark reverted — synthetic T_WS restored | context full |
| 2026-03-13 | Sprint 3 (`beauty-runtime`) complete — clean exit | first run worked |
| 2026-03-13 | Sprint 2 (`smoke-tests`) complete — 21/21 | hand-rolled lex/parse works |
| 2026-03-13 | M-REBUS fired → rebus-roundtrip complete | Rebus milestone done |
| 2026-03-12 | Bison/Flex → hand-rolled-parser | LALR(1) unfixable (139 RR) |
