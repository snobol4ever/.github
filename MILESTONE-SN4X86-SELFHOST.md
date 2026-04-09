# MILESTONE-SN4X86-SELFHOST.md — beauty self-hosting runs clean

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-08
**Status:** ⬜

## Goal
`scrip --ir-run beauty.sno beauty.sno` output matches CSNOBOL4 exactly.

## Depends on
MILESTONE-SN4X86-TILDE.md, MILESTONE-SN4X86-ALPHABET.md

## Run
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno
```

## Reference
```bash
/home/claude/snobol4-2.3.3/snobol4 \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno \
    /home/claude/corpus/programs/snobol4/demo/beauty.sno
```

## Gate
Diff scrip output vs CSNOBOL4 output = empty. No `** Error` lines. Exit 0.
