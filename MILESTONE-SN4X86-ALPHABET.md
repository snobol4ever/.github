# MILESTONE-SN4X86-ALPHABET.md — &ALPHABET keyword stub

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-08
**Status:** ⬜

## Goal
`&ALPHABET` assignments and reads in `global.sno` do not produce errors.

## Problem
`&ALPHABET` is not in the keyword dispatch table. `global.sno` assigns to it
on lines 2–28+ to extract individual characters. Beauty does not exercise
character-class matching so a no-op stub is sufficient.

## Fix
In `snobol4.c` `NV_SET_fn`: no-op on `&ALPHABET`.
In `snobol4.c` `NV_GET_fn`: return `STRVAL("")` on `&ALPHABET`.

## Gate
```bash
SNO_LIB=/home/claude/corpus/programs/snobol4/demo/inc \
    ./scrip --ir-run beauty.sno beauty.sno 2>&1 | grep -i "alphabet" | wc -l
# → 0
```
