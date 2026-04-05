# MILESTONE-CMPILE-UTF8.md — Full UTF-8 Unicode Support in CMPILE

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-05
**Session:** Track C — scrip-interp / SIL, sprint RT-107+
**Status:** ACTIVE — UTF8-1 through UTF8-5 queued

---

## Governing Principle

SNOBOL4 source files are UTF-8 in the real world. CMPILE must accept
UTF-8 source without aborting. The fix is **table-driven throughout** —
new action codes and new chrs[] entries, not byte guards bolted on
outside the scanner. Every change lives inside the `syntab_t` / `acts_t`
/ `stream()` architecture.

Full UTF-8 support means:

- **Comment lines** (`*`-cards): arbitrary Unicode, silently skipped
- **String literals**: UTF-8 bytes pass through SQLITB/DQLITB as-is
  into `DESCR_t` value (already almost correct — see UTF8-2)
- **Identifiers / labels**: UTF-8 letter sequences (Greek, Latin
  extended, etc.) valid as identifier-start and identifier-continue
  in ELEMTB → VARTB and LBLTB → LBLXTB (see UTF8-3 / UTF8-4)
- **Operators and delimiters**: ASCII-only, unchanged
- `-INCLUDE` paths: UTF-8 filenames byte-transparent via POSIX
  `fopen()` — audit only (UTF8-5)

SPITBOL oracle (`snobol4ever/x64`) is the correctness reference for
runtime string behaviour. CSNOBOL4 is the correctness reference for
parse/scan behaviour.

---

## Current Table State — What Is Already Correct

Reading the actual chrs[] arrays before writing any code:

| Table | 0x80-0xFF entry | Effect | Status |
|-------|----------------|--------|--------|
| **CARDTB** | `4` -> `actions[3]` = `{NEWTYP, ACT_STOPSH}` | High byte in col-1 -> NEWTYP (normal stmt) | correct — can't appear in *-comment col-1 |
| **ELEMTB** | `2` -> `actions[1]` = `{VARTYP, ACT_GOTO, VARTB}` | High byte at token start -> identifier | correct |
| **VARTB** | `0` -> `ACT_CONTIN` fast-path | High byte inside identifier -> continue | correct |
| **LBLTB** | `1` -> `actions[0]` = `{0, ACT_GOTO, LBLXTB}` | High byte in label -> goto LBLXTB | correct |
| **LBLXTB** | `0` -> `ACT_CONTIN` | High byte continues label | correct |
| **SQLITB** | `0` -> `ACT_CONTIN` | High byte inside '...' -> accumulate | already correct |
| **DQLITB** | `0` -> `ACT_CONTIN` | High byte inside "..." -> accumulate | already correct |

**Key finding:** identifiers and string literals are **already byte-transparent
for high bytes** at the table level. The actual UTF-8 bug is narrower than
previously described.

---

## Where the Bug Actually Is

The sil_error trigger is in `ELEMNT()`:

```c
stream_ret_t r = stream(&XSP, &TEXTSP, &ELEMTB);
if (r == ST_ERROR) {
    sil_error("ELEMNT: illegal character");
    return NULL;
}
```

`ELEMTB` has no `ACT_ERROR` entry for high bytes — they dispatch as
`VARTYP -> VARTB`. So the `ST_ERROR` path is not triggered by high bytes
in token position. The actual trigger for corpus failures is:

**Non-ASCII bytes in *-comment lines reach `ELEMNT()` at all.**

When `cmpile_lower()` calls the CMPILE path, comment line content reaches
statement-body parsing if the comment-skip in `forrun()` does not fire
correctly. The root issue: `forrun()` CMTTYP skip must be unconditional
before `stream()` touches the card.

---

## Invariant — Green Throughout

**Baseline (RT-106, one4all `081cce9`):**
```
PASS=190  FAIL=13  (203 total)   [sno_parse path]
```

Every UTF8 commit must hold PASS >= 190 on the `sno_parse` path.
Primary goal: `cmpile_lower()` path reaches PASS >= 190.

```bash
cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
```

---

## Milestone Ladder

| Milestone | Scope | Tables touched | Gate |
|-----------|-------|---------------|------|
| **UTF8-1** | Comment skip in `forrun()` before any `stream()` call | none — pre-table guard | cmpile_lower PASS >= 108 |
| **UTF8-2** | Comment skip audit — all CARDTB call sites | CARDTB | No regression |
| **UTF8-3** | New `ACT_UTF8` action + table changes for multi-byte identifier sequences | ELEMTB, VARTB, LBLTB, LBLXTB | Greek identifiers parse |
| **UTF8-4** | Unicode category filter — which codepoints are valid identifier chars | new `utf8_is_id_char()` lookup | Corpus identifier tests pass |
| **UTF8-5** | `-INCLUDE` path audit | none — POSIX byte-transparent | Include of UTF-8 named file works |

---

## UTF8-1 — Comment Skip Before `stream()` in `forrun()`

**Files:** `src/frontend/snobol4/CMPILE.c` — `forrun()` function
**Blocks:** RT-107 (cmpile_lower as default path)
**Gate:** `1010_func_recursion.sno` -> `--dump-parse` non-empty;
cmpile_lower path PASS >= 108

### Design

`forrun()` currently calls `stream(&tok, &card, &CARDTB)` on the full
raw line before dispatching on `STYPE`. For a *-comment line the first
byte is `*` (0x2A) which CARDTB maps to `CMTTYP/STOPSH` — the stop fires
before any non-ASCII bytes are reached. However the `spec_t card` still
points at the full raw line including any UTF-8 prose, and subsequent
internal stream state or a second call on the remainder could touch those
bytes.

The fix: before `stream()` fires, check `rawline[0] == '*'` and skip the
card immediately. This mirrors CSNOBOL4 FORRN0 exactly — comment branch
executes before any card content is processed.

```c
/* UTF8-1: comment cards may contain arbitrary UTF-8 prose.
 * Skip before stream() sees any byte of the card body.
 * Mirrors CSNOBOL4 FORRN0 — comment branch fires before NEWCRD body. */
if (rawline[0] == '*') goto retry;
```

This is not a bypass of the table architecture — it is the correct
pre-table guard, exactly as CSNOBOL4 implements FORRN0.

### Verification

```bash
cd /home/claude/one4all
./scrip-interp --dump-parse \
  /home/claude/corpus/crosscheck/rung10/1010_func_recursion.sno 2>&1 | head -5
# Must show at least one STMT line, not empty / sil_error abort

CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
# sno_parse path: PASS >= 190
```

---

## UTF8-2 — Comment Skip Audit (All CARDTB Call Sites)

**Files:** `src/frontend/snobol4/CMPILE.c`
**Gate:** No regression; UTF-8 comments in `-INCLUDE`d files handled

### Design

There is a second card reader loop in `cmpile_file_internal()` separate
from `forrun()`. Audit every `stream(*, *, &CARDTB)` call site:

```bash
grep -n "CARDTB" src/frontend/snobol4/CMPILE.c
```

For each site, verify that a *-card is either:
- Pre-guarded with `rawline[0] == '*'` before the `stream()` call, or
- Provably unreachable on comment input (document why)

Add the same pre-guard wherever missing.

---

## UTF8-3 — New `ACT_UTF8` Action: Multi-Byte Identifier Sequences

**Files:** `src/frontend/snobol4/CMPILE.c`
**Gate:** Program with Greek identifier parses; VARTB accumulates full
multi-byte sequence into token spec

### Background

The current tables are already byte-transparent for high bytes in
identifier position (ELEMTB chrs[0x80-0xFF]=2 -> VARTB; VARTB
chrs[0x80-0xFF]=0 -> ACT_CONTIN). A Greek letter sequence passes through
and lands in the token buffer. However `stream()` is byte-at-a-time and
does not know that bytes `0xCE 0xB1` (alpha, U+03B1) are one codepoint.
This is fine for token accumulation — the bytes are gathered into the
spec — but it creates two correctness problems:

1. **Continuation bytes 0x80-0xBF as identifier-start**: ELEMTB
   chrs[0x80-0xFF]=2 currently treats a bare continuation byte as
   identifier-start (VARTYP). That is wrong — a continuation byte
   appearing outside a lead sequence is invalid UTF-8 and must be
   rejected.

2. **LBLTB**: same issue for bare continuation bytes in label position.

### New action: `ACT_UTF8`

Add a new action type to `action_t`:

```c
typedef enum {
    ACT_CONTIN=0, ACT_STOP, ACT_STOPSH, ACT_ERROR, ACT_GOTO,
    ACT_UTF8   /* consume N continuation bytes per UTF-8 lead byte */
} action_t;
```

`stream()` handles `ACT_UTF8`: inspect the lead byte already consumed
to determine sequence length (2 for 0xC2-0xDF, 3 for 0xE0-0xEF, 4 for
0xF0-0xF4), consume that many additional bytes from `sp2`, append all
to the token buffer in `sp1`, then continue in the current table
(ACT_CONTIN semantics after the multi-byte consume).

### Table changes

**ELEMTB** — split the 0x80-0xFF range:

| Byte range | UTF-8 meaning | New chrs[] action | Effect |
|------------|--------------|-------------------|--------|
| 0x80-0xBF | Continuation byte (invalid at token start) | ACT_ERROR | Reject bare continuation |
| 0xC0-0xC1 | Overlong 2-byte (invalid UTF-8) | ACT_ERROR | Reject |
| 0xC2-0xDF | 2-byte lead (U+0080..U+07FF) | ACT_UTF8 -> VARTB | Consume 2-byte sequence |
| 0xE0-0xEF | 3-byte lead (U+0800..U+FFFF) | ACT_UTF8 -> VARTB | Consume 3-byte sequence |
| 0xF0-0xF4 | 4-byte lead (U+10000..U+10FFFF) | ACT_UTF8 -> VARTB | Consume 4-byte sequence |
| 0xF5-0xFF | Invalid UTF-8 | ACT_ERROR | Reject |

**VARTB** (identifier continuation) — same split. Since `ACT_UTF8` in
`stream()` consumes the entire multi-byte sequence atomically, VARTB
only needs `ACT_UTF8` for new lead bytes encountered mid-identifier.
Continuation bytes 0x80-0xBF inside VARTB are unreachable after a
correct `ACT_UTF8` consume, but set them to ACT_ERROR for safety.

**LBLTB / LBLXTB** — same treatment as ELEMTB/VARTB.

---

## UTF8-4 — Unicode Category Filter for Identifier Characters

**Files:** `src/frontend/snobol4/CMPILE.c` — new `utf8_is_id_char()` helper
**Gate:** Greek letters (U+0370-U+03FF) valid in identifiers; CJK and
emoji rejected; corpus identifier tests pass

### Design

`ACT_UTF8` in `stream()` accumulates the byte sequence. After accumulation,
a category check determines whether the codepoint is a valid identifier
character. Add:

```c
/* Returns 1 if the UTF-8 sequence at p (length len) is a codepoint
 * allowed in SCRIP identifiers. Does not use locale or wctype.h. */
static int utf8_is_id_char(const unsigned char *p, int len);
```

Decodes the codepoint from UTF-8 bytes and checks against an explicit
range table. No `<wctype.h>` — locale-dependent and not available in
all build environments.

Initial approved ranges (expand by request):

| Range | Block | Status |
|-------|-------|--------|
| U+00C0-U+024F | Latin Extended A/B | included |
| U+0370-U+03FF | Greek and Coptic | included |
| U+0400-U+04FF | Cyrillic | included |
| U+0590-U+05FF | Hebrew | included |
| U+0600-U+06FF | Arabic | included |
| U+4E00-U+9FFF | CJK Unified Ideographs | excluded (too wide) |
| U+1F000+      | Emoji | excluded |

If `utf8_is_id_char()` returns 0, `ACT_UTF8` fires `ACT_ERROR` instead
of accumulating — `ELEMNT` reports "illegal character".

---

## UTF8-5 — `-INCLUDE` Path Audit

**Files:** `src/frontend/snobol4/CMPILE.c` — `resolve_include_path()`
**Gate:** `-INCLUDE path/with/unicode.sno` opens correctly

### Design

`resolve_include_path()` uses `strcat`/`strcpy` on raw bytes. POSIX
`fopen()` is byte-transparent — no decoding needed. Audit for any
`isalpha()`/`isalnum()` guards on path characters that could strip
high bytes. Remove any such guards. No new tables needed.

---

## Relationship to RT Milestone Chain

**UTF8-1** is a prerequisite blocker for **RT-107** (wiring
`cmpile_lower()` as the default path).

**UTF8-2** through **UTF8-5** are Track C quality items queued after
RT-107 lands. They do not block any RT milestone.

UTF-8 support does **not** change the runtime `DESCR_t` layout, the
Byrd box pattern engine, the SM instruction set, or any emitter.
It is purely a CMPILE / frontend concern.

---

## PLAN.md Component Map Entry (add when updating PLAN.md)

```
| **CMPILE UTF-8** | `MILESTONE-CMPILE-UTF8.md` | UTF8-1 blocks RT-107 · UTF8-3 adds ACT_UTF8 |
```

---

*MILESTONE-CMPILE-UTF8.md — rewritten RT-107 session, 2026-04-05,
Lon Jones Cherryholmes + Claude Sonnet 4.6.*
