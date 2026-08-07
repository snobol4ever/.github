# REPO-corpus.md — corpus

**What:** Test corpus for all frontends: `.sno`/`.icn`/`.pl`/`.sc` programs + `.ref` expected outputs.
**Clone:** `git clone https://github.com/snobol4ever/corpus.git /home/claude/corpus` (public; push needs credential).

## Session Start
```bash
git clone https://github.com/snobol4ever/corpus /home/claude/corpus
git clone https://github.com/snobol4ever/SCRIP  /home/claude/SCRIP
```
Build: none — data only. `.ref` regen: `bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh` (CSNOBOL4 variant exists).

## Layout
```
corpus/
  crosscheck/          — self-contained programs × all engines, CI-safe
  probe/               — witness programs (bb/ = 141-probe suite)
  programs/snobol4/    — beauty/ (19 drivers + refs) · demo/inc/ (-INCLUDE) · smoke/
  programs/{lon,gimpel,icon,prolog,...}
  benchmarks/
  lib/                 — shared .inc
```

## Oracle for .ref
```bash
/home/claude/x64/bin/sbl -b file.sno > file.ref
/home/claude/x64/bin/sbl -I<incdir> file.sno > file.ref   # with includes
```
`.ref` files are pre-baked — SPITBOL not required to run gates.

## Testing ladder (stop at first failing rung, fix, move up)
1 hello · 2 assign · 3 concat · 4 arith · 5 control (:S/:F, goto) · 6 patterns (LIT ANY SPAN BREAK LEN POS RPOS ARB ARBNO) · 7 capture (. $) · 8 strings (SIZE SUBSTR REPLACE TRIM DUPL) · 9 keywords (IDENT DIFFER GT/LT/EQ DATATYPE) · 10 functions (DEFINE RETURN FRETURN recursion) · 11 data (ARRAY TABLE DATA) · 12 beauty.sno
