# REPO-corpus.md — corpus

**What:** Test corpus for all frontends. `.sno`, `.icn`, `.pl`, `.sc` test programs
plus `.ref` expected output files. Used by all repos.
**Clone:** `git clone https://TOKEN_SEE_LON@github.com/snobol4ever/corpus.git /home/claude/corpus`
**Path:** `/home/claude/corpus`

---

## Layout

```
corpus/
  crosscheck/          — self-contained programs × all engines, fast, CI-safe
  programs/
    snobol4/
      beauty/          — 19 beauty drivers + .ref files
      demo/
        inc/           — include files (-INCLUDE path for beauty suite)
      smoke/
    lon/               — Lon's programs
    gimpel/            — Gimpel's SNOBOL4 programs
  lib/                 — shared .inc include files
```

---

## Oracle for .ref files

Derive expected output with SPITBOL:
```bash
/home/claude/x64/bin/sbl -b file.sno > file.ref
# with includes:
/home/claude/x64/bin/sbl -I/home/claude/corpus/programs/snobol4/demo/inc file.sno > file.ref
```

`.ref` files are pre-baked — SPITBOL not required to run test gates.

---

## Testing ladder (canonical protocol)

Stop at first failing rung. Fix it. Move up.

| Rung | Content |
|------|---------|
| 1 | 1 token — `OUTPUT = 'hello world'` |
| 2 | assign |
| 3 | concat |
| 4 | arith |
| 5 | control — goto, :S(), :F() |
| 6 | patterns — LIT, ANY, SPAN, BREAK, LEN, POS, RPOS, ARB, ARBNO |
| 7 | capture — . and $ operators |
| 8 | strings — SIZE, SUBSTR, REPLACE, TRIM, DUPL |
| 9 | keywords — IDENT, DIFFER, GT/LT/EQ, DATATYPE |
| 10 | functions — DEFINE, RETURN, FRETURN, recursion |
| 11 | data — ARRAY, TABLE, DATA types |
| 12 | beauty.sno — full program |
