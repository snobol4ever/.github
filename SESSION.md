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
| **HEAD** | `8f68962` — fix(sno2c): emit_pat E_DEREF dangling-if, unop left/right contract |

## Last Thing That Happened

**Sprint 3 (`beauty-runtime`) COMPLETE.** Binary exits cleanly on first run.
- `beauty_full_bin < beauty.sno` → 801 lines, no crash, no hang, exit 0.

**Sprint 4 (`beauty-full-diff`) started.** Oracle diff analyzed:
- Oracle: 790 lines. Compiled: 801 lines. Diff: 1383 lines.
- Root cause 1 (minor): **indentation/column spacing** — 19 lines differ only in
  leading space count. Subject column alignment slightly off.
- Root cause 2 (major): **line wrapping** — the beautifier wraps long lines with
  `+` continuation at column stops from `ppStop[1..4]`. Compiled output wraps
  at different points. This is the core beautifier logic — `ppStop` values depend
  on correct runtime behavior of the `snoStmt` pattern match + `Gen()` calls.

The binary is functionally correct. The diff is about formatting fidelity.

## One Next Action

**Diagnose the wrapping difference.** Start by comparing a known short section:

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
SNO=/home/claude/snobol4-2.3.3/snobol4

# Oracle
$SNO -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno 2>/dev/null

# Compiled
/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno 2>/dev/null

diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno | head -60
```

Look at lines 29-30 first — `&FULLSCAN = 1` has indentation difference only.
That suggests the body column (subject alignment) is slightly off in sno2c output.
Check `ppWidth` and `GetLevel()` logic in beauty.sno pass 2.

## Rebuild Commands

```bash
cd /home/claude/SNOBOL4-tiny

# Rebuild sno2c
make -C src/sno2c

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
SNO=/home/claude/snobol4-2.3.3/snobol4
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
| 2026-03-13 | Sprint 3 (`beauty-runtime`) complete — clean exit | first run worked |
| 2026-03-13 | Sprint 2 (`smoke-tests`) complete — 21/21 | hand-rolled lex/parse works |
| 2026-03-13 | `snoc` renamed `sno2c`; src/snoc → src/sno2c | name reflects function |
| 2026-03-13 | hand-rolled lex.c + parse.c replace flex/bison | grammar confirmed LALR(1) |
| 2026-03-13 | Sprint 1 (`space-token`) PIVOTED, dumb-lexer rewrite begun | architecture fix |
| 2026-03-13 | Sprint 1 (`space-token`) complete → Sprint 2 (`smoke-tests`) active | 0 conflicts |
| 2026-03-13 | M-REBUS fired → `rebus-roundtrip` sprint complete, bf86b4b | Rebus milestone done |
| 2026-03-12 | Bison/Flex → `hand-rolled-parser` decision | Session 53: LALR(1) unfixable (139 RR) |
| 2026-03-12 | M-BEAUTY-FULL inserted before M-COMPILED-SELF | Lon's priority: beautifier first |
