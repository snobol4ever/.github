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
| **HEAD** | `17526bb` — EMERGENCY WIP: parse_expr4 LexMark fix — | alternation works, segfault on SPAN(&UCASE &LCASE) = replacement stmt |

## Last Thing That Happened

**Two parser bugs fixed this session, one new segfault found.**

### Fix 1 — parse_expr0 LexMark revert ✅
`parse_expr0` had LexMark restore incorrectly applied. Reverted to synthetic T_WS
injection (exact code from previous SESSION.md). This was the intended one-liner fix.

### Fix 2 — parse_expr4 | alternation bug ✅
Root cause found and fixed. `parse_expr4` (concat level) called `skip_ws()` after
consuming WS for lookahead. `skip_ws` advanced `lx->pos` past the next token (e.g. `|`).
Then synthetic T_WS injection put WS back in the peek slot — but `pos` was already past
the `|`. `parse_expr3`'s `|` loop then saw the synthetic WS, consumed it, and then saw
ANOTHER real WS (the one before `|`), not T_PIPE — so it restored and gave up.

**Fix:** Replace `lex_next(lx); skip_ws(lx);` in parse_expr4 with `LexMark mc` +
`lex_next(lx)` + `lex_restore(lx, mc)` on non-concat-start. Now `| alternation`
and `FENCE(*a | *b | *c)` both emit correctly.

**Verified:**
- `*a | *b | *c` → `sno_pat_alt(sno_pat_alt(ref(a),ref(b)),ref(c))` ✓
- `'a' 'b' 'c'` → `concat(concat("a","b"),"c")` ✓
- `FENCE(*a | *b | *c)` → `sno_pat_fence_p(sno_pat_alt(...))` ✓

### New segfault — replacement statement with builtin call ❌
`sno2c` segfaults (exit 139) on replacement statements where the pattern contains
a builtin with a complex argument. Isolated minimal reproducer:

```snobol4
               X POS(0) SPAN(&UCASE &LCASE) =
END
```

These work fine:
- `X 'hello' =` ✓
- `X LEN(1) =` ✓
- `X POS(0) =` ✓
- `X = POS(0) SPAN(&UCASE &LCASE)` (assignment, not replacement) ✓
- `X POS(0) SPAN(&UCASE &LCASE)` (match without replacement) ✓

So: pattern with function-call builtin inside a **replacement** stmt (`pat =`) crashes.
The `=` at the end of a pattern match statement means "replace matched portion with
empty string." This is parsed differently from assignment. Likely the replacement
parser is calling into parse_expr0/parse_expr4 in a state where the LexMark
interacts badly with something.

**Affected files from is.sno (and likely others):**
```
is.sno line 15:  types  POS(0) SPAN(&UCASE &LCASE) . type (',' | RPOS(0)) =
io.sno — also crashes
case.sno — also crashes
```

## One Next Action

**Find and fix the replacement-statement segfault in sno2c.**

Start here:
```bash
cat > /tmp/test_segfault.sno << 'EOF'
               X POS(0) SPAN(&UCASE &LCASE) =
END
EOF
# Run under gdb or add ulimit to get stack trace
ulimit -c unlimited
cd /home/claude/SNOBOL4-tiny
src/sno2c/sno2c /tmp/test_segfault.sno
# or:
gdb -batch -ex run -ex bt src/sno2c/sno2c --args src/sno2c/sno2c /tmp/test_segfault.sno
```

Likely cause: the replacement `=` in `parse_body_field` is calling `parse_expr0`
to parse the replacement value (empty in this case). `parse_expr0` sees WS then
something, calls into `parse_expr4`, which with LexMark now restores state — but
in some combination with the arglist parsing of `SPAN(...)`, this creates a cycle.

Check `parse_body_field` in parse.c for how replacement is handled. Look for any
path where parse_expr0 or parse_expr4 could be re-entered with the same lex state.

After fix:
1. `make -C src/sno2c`
2. Verify `X POS(0) SPAN(&UCASE &LCASE) =` no longer crashes
3. Run smoke tests → 21/21
4. Recompile beauty.sno + rebuild binary
5. Run smoke tests on binary
6. Diff vs oracle

## New Direction — 100-Test Suite

**Agreed with Lon this session:** Before pushing on beauty.sno, build a proper
100-test suite (one program per SNOBOL4 feature). Designed and documented at:

  `/mnt/user-data/outputs/TEST_SUITE_100.md` — but this is local only.

The full design is in SESSIONS_ARCHIVE.md (append it there). Key structure:

```
test/sno/
  001_output_string_literal.sno   through   100_full_smoke.sno
  run_all.sh
  expected/001.out ... 100.out
```

Six milestone gates: G-A (001–008) through G-F (001–100), then M-BEAUTY-FULL.
Each test is ~5-10 lines, diff'd against CSNOBOL4. Living suite — add tests as
bugs are found.

**Start Group A (001–008) after segfault is fixed.**

## Rebuild Commands

```bash
cd /home/claude/SNOBOL4-tiny

# Deps (if fresh container)
apt-get install -y libgc-dev m4
cd /home/claude && tar xzf /path/to/snobol4-2_3_3_tar.gz ...
# OR: snobol4 already at /home/claude/snobol4-2.3.3/bin/snobol4

# Rebuild sno2c
make -C src/sno2c

# Segfault test
src/sno2c/sno2c /tmp/test_segfault.sno   # should not crash after fix

# Smoke test (needs binary)
bash test/smoke/test_snoCommand_match.sh /tmp/beauty_full_bin

# Recompile beauty.sno
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > /tmp/beauty_full.c

# Build binary
R=src/runtime/snobol4
gcc -O0 -g /tmp/beauty_full.c \
    $R/snobol4.c $R/snobol4_inc.c $R/snobol4_pattern.c \
    src/runtime/engine.c \
    -I$R -Isrc/runtime -lgc -lm -w \
    -o /tmp/beauty_full_bin

# Oracle
SNO=/home/claude/snobol4-2.3.3/bin/snobol4
$SNO -f -P256k -I /home/claude/SNOBOL4-corpus/programs/inc \
    /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    < /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
    > /tmp/beauty_oracle.sno 2>/dev/null

# Diff
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno
```

## Pivot Log

| Date | What changed | Why |
|------|-------------|-----|
| 2026-03-13 | 100-test suite designed — G-A through G-F gates before M-BEAUTY-FULL | Lon: need lampposts on the road |
| 2026-03-13 | parse_expr4 | bug fixed — LexMark replaces skip_ws+synthetic injection | Double-WS caused | to be swallowed |
| 2026-03-13 | parse_expr0 LexMark reverted — synthetic T_WS injection restored | context full last session |
| 2026-03-13 | Sprint 3 (`beauty-runtime`) complete — clean exit | first run worked |
| 2026-03-13 | Sprint 2 (`smoke-tests`) complete — 21/21 | hand-rolled lex/parse works |
| 2026-03-13 | `snoc` renamed `sno2c`; src/snoc → src/sno2c | name reflects function |
| 2026-03-13 | hand-rolled lex.c + parse.c replace flex/bison | grammar confirmed LALR(1) |
| 2026-03-13 | M-REBUS fired → `rebus-roundtrip` sprint complete | Rebus milestone done |
| 2026-03-12 | Bison/Flex → `hand-rolled-parser` decision | Session 53: LALR(1) unfixable (139 RR) |
| 2026-03-12 | M-BEAUTY-FULL inserted before M-COMPILED-SELF | Lon's priority: beautifier first |
