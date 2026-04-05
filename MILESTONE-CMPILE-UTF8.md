# MILESTONE-CMPILE-UTF8.md — Full UTF-8 Unicode Support in CMPILE

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-05
**Session:** Track C — scrip-interp / SIL, sprint RT-107+
**Status:** ACTIVE — UTF8-1 through UTF8-4 queued

---

## Governing Principle

SNOBOL4 string values are byte strings at the runtime level, but
**source files are UTF-8 in the real world**. CMPILE must accept
UTF-8 source without aborting. Every place where a raw byte ≥ 0x80
can reach `stream()` and trigger `sil_error` is a bug.

Full UTF-8 support means:
- Comment lines (`*`-cards): arbitrary Unicode, silently skipped
- String literals: UTF-8 bytes pass through as-is into `DESCR_t` value
- Variable names and labels: ASCII-only (SIL identifier rule preserved)
- Operators and delimiters: ASCII-only (unchanged)
- `-INCLUDE` paths: UTF-8 filenames allowed

SPITBOL oracle (`snobol4ever/x64`) is the correctness reference for
runtime string behaviour. CSNOBOL4 is the correctness reference for
parse/scan behaviour.

---

## Invariant — Green Throughout

**Baseline (RT-106, one4all `081cce9`):**
```
PASS=190  FAIL=13  (203 total)   [sno_parse path]
```

Every UTF8 commit must hold PASS ≥ 190 on the `sno_parse` path.
Primary goal: `cmpile_lower()` path reaches PASS ≥ 190.

Run after every change:
```bash
cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
```

---

## Strategy — Layer by Layer

Each milestone targets one UTF-8 exposure surface in CMPILE.
No changes to the runtime `DESCR_t` representation — bytes are bytes.
No changes to the Byrd box pattern engine — it operates on runtime strings.

| Layer | Exposure | Milestone |
|-------|----------|-----------|
| `*`-comment lines in `forrun()` | Non-ASCII bytes fed to `stream()` via CARDTB | UTF8-1 |
| `*`-comment lines in `cmpile_file_internal()` inline reader | Same exposure in alternate read path | UTF8-2 |
| String literal scan in ELEMTB / `str_lit()` | Bytes ≥ 0x80 inside `'...'` delimiters | UTF8-3 |
| `-INCLUDE` path argument | Non-ASCII filename in `resolve_include_path()` | UTF8-4 |

---

## UTF8-1 — Comment Lines in `forrun()` (FORRN0 path)

**Files:** `src/frontend/snobol4/CMPILE.c`
**Gate:** `1010_func_recursion.sno` → `--dump-parse` returns non-empty stmt list;
`cmpile_lower()` path PASS ≥ 107 + 1 (at minimum 1010 now passing)

### Root cause

In `forrun()`, `CARDTB` is called via `stream()` on the raw line.
`CARDTB` is a byte-dispatch table. A line beginning `* foo — bar`
where `—` is U+2014 (bytes `0xE2 0x80 0x94`) correctly stops at
`CMTTYP` on the first `*` byte before any non-ASCII bytes are scanned.
However, `stream()` initialises internal state from the full `spec_t`
(pointer + length), and depending on table action sequencing, bytes
beyond the stop may be accessed. Additionally, any second `stream()`
call on the same card's `spec_t` remainder reaches non-ASCII bytes.

### Fix

Before calling `stream(&tok, &card, &CARDTB)` in `forrun()`, add:

```c
/* UTF8-1: skip comment cards before any byte reaches stream().
 * '*'-cards may contain arbitrary UTF-8 in prose descriptions.
 * CARDTB would stop at CMTTYP on the '*' byte, but defensive
 * early-exit costs nothing and prevents any scanner exposure. */
if (rawline[0] == '*') goto retry;
```

This mirrors what CSNOBOL4's FORRN0 does: the comment branch
executes before any further card processing.

### Verification

```bash
cd /home/claude/one4all
./scrip-interp --dump-parse /home/claude/corpus/crosscheck/rung10/1010_func_recursion.sno 2>&1 | head -5
# Must show at least one STMT line, not empty / sil_error

CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
# Must hold PASS >= 190 on sno_parse path
```

---

## UTF8-2 — Comment Lines in Inline Reader

**Files:** `src/frontend/snobol4/CMPILE.c`
**Gate:** No regression; UTF-8 comments in `-INCLUDE`d files handled

### Context

`cmpile_file_internal()` has an inline card reader loop separate from
`forrun()` (used for direct file iteration in some paths). Apply the
same `rawline[0] == '*'` guard before any `stream()` call there.

Audit all sites matching `stream.*CARDTB` — each needs the guard or
proof that it is unreachable on comment input.

---

## UTF8-3 — String Literals

**Files:** `src/frontend/snobol4/CMPILE.c` (ELEMTB / string literal scan)
**Gate:** Program containing UTF-8 string literal parses and runs correctly;
output matches SPITBOL oracle

### What to do

Inside the string-literal scanning action (ELEMTB stop code for `'`
delimiter), bytes ≥ 0x80 must pass through into the `DESCR_t` string
value without triggering an error action. Currently, any non-ASCII byte
in the ELEMTB byte-dispatch table hits the default error action.

Fix: add a UTF-8 multi-byte passthrough in the string literal accumulator.
When inside a `'...'` scan, bytes `0xC2`–`0xF4` (UTF-8 lead bytes) and
`0x80`–`0xBF` (UTF-8 continuation bytes) are accumulated as-is.

Oracle test program:
```snobol4
        X = 'héllo'
        OUTPUT = X
```
Expected output: `héllo` (bytes `68 C3 A9 6C 6C 6F`).

---

## UTF8-4 — `-INCLUDE` Path Arguments

**Files:** `src/frontend/snobol4/CMPILE.c` (`resolve_include_path()`)
**Gate:** `-INCLUDE path/with/ünïcödé.sno` resolves and opens correctly

### What to do

`resolve_include_path()` uses `strcat`/`strcpy` on the raw argument
bytes. UTF-8 filenames are byte-transparent in POSIX `fopen()`, so
no decoding is needed — just ensure no ASCII-only `isalpha()`/`isdigit()`
guards strip high bytes from the path argument. Audit and remove any
such guards.

---

## Relationship to RT Milestone Chain

UTF8-1 is a **prerequisite blocker for RT-107** (wiring `cmpile_lower()`
as the default path). UTF8-2 through UTF8-4 are Track C quality items
queued after RT-107 lands.

UTF-8 support does **not** change the runtime `DESCR_t` layout,
the Byrd box engine, the SM instruction set, or any emitter.
It is purely a frontend / CMPILE concern.

---

## PLAN.md Component Map Entry

Add to component map:

| **CMPILE UTF-8** | `MILESTONE-CMPILE-UTF8.md` | ⬜ UTF8-1 blocks RT-107 |

---

*MILESTONE-CMPILE-UTF8.md — created RT-107 session, 2026-04-05, Lon Jones Cherryholmes + Claude Sonnet 4.6.*
