# KEYWORD_GRID.md — SNOBOL4 Keyword Implementation Status
## Source-verified against each oracle and our runtime

> **Purpose**: Every `&KEYWORD` across the three SNOBOL4 implementations
> relevant to this project. For each: is it implemented, read-only or
> read-write, what it does, and what state our runtime (`snobol4.c`) is in.
> When a keyword is missing or stubbed in an oracle, a patch to that
> oracle's C source is recorded here with the fix.
>
> **Sources**:
> - CSNOBOL4: `snobol4-2.3.3/v311.sil`, `data_init.h`, `isnobol4.c`, `snobol4.c`
> - SPITBOL: `x64-main/bootstrap/sbl.lex` (symbol table, keyword dispatch)
> - SNOBOL4-tiny: `src/runtime/snobol4/snobol4.h`, `snobol4.c`
>
> **Key for Status column**:
> `✓` = fully implemented and wired
> `~` = declared/stubbed, not enforced
> `✗` = not present at all
> `R` = read-only (assignment raises error)
> `RW` = read-write
> `RW*` = read-write with special assignment logic

---

## The Grid

| Keyword | R/W | CSNOBOL4 | SPITBOL | SNOBOL4-tiny | What It Does |
|---------|-----|----------|---------|--------------|--------------|
| `&ABEND` | RW | ✓ | ✓ | ✗ | If nonzero, abnormal exit on error |
| `&ALPHABET` | R | ✓ | ✓ | ✓ | All 256 characters in order |
| `&ANCHOR` | RW | ✓ | ✓ | ~ stub | Nonzero = anchored match at position 0 |
| `&CASE` | RW | ✓ | ✓ | ✗ | 0 = fold to upper; 1 = no fold (`-f` sets this) |
| `&CODE` | R | ✓ | ✓ | ✗ | Return code from last `EXIT()` call |
| `&COMPARE` | RW | ✓ | ✓ | ✗ | String comparison mode |
| `&DUMP` | RW | ✓ | ✓ | ✗ | Nonzero = dump variables on termination |
| `&ERRLIMIT` | RW | ✓ | ✓ | ✗ | Max errors before abort; 0 = abort on first |
| `&ERRTEXT` | R | ✓ | ✓ R | ✗ | Text of last error message |
| `&ERRTYPE` | R | ✓ | ✓ R | ✗ | Numeric code of last error |
| `&FNCLEVEL` | R | ✓ | ✓ R | ✗ | Current function call depth |
| `&FTRACE` | RW | ✓ | ✓ | ✗ | Function trace counter; fires N times |
| `&FULLSCAN` | RW* | ✓ | ✓ RW* | ~ stub | Nonzero = disable heuristic match optimizations |
| `&GTRACE` | RW | ✓ | — | ✗ | CSNOBOL4 extension: goto trace |
| `&INPUT` | R | ✓ | ✓ | ✗ | **Not wired to stdin** — suspected hang cause |
| `&LASTFILE` | R | ✓ | ✓ R | ✗ | Source file of last executed statement |
| `&LASTLINE` | R | ✓ | ✓ R | ✗ | Source line number of last statement |
| `&LASTNO` | R | ✓ | ✓ R | ✗ | Statement number before current |
| `&LCASE` | R | ✓ | ✓ R | ~ | `sno_lcase[]` declared; not exposed as `&LCASE` |
| `&MAXLNGTH` | RW | ✓ | ✓ | ~ stub | Max string length; default varies |
| `&OUTPUT` | RW | ✓ | ✓ | ✗ | **Not wired to stdout** — suspected hang cause |
| `&PROFILE` | RW | — | ✓ | ✗ | SPITBOL extension: execution profiling |
| `&RTNTYPE` | R | ✓ | ✓ R | ✗ | Return type: 'RETURN', 'FRETURN', 'NRETURN' |
| `&STCOUNT` | R | ✓ | ✓ R | ~ partial | Incremented (P001 fix) but not readable as variable |
| `&STLIMIT` | RW* | ✓ | ✓ RW* | ~ partial | P001: now enforced; default 50000 |
| `&STNO` | R | ✓ | ✓ R | ~ partial | Emitted via COMM; not readable as `sno_var_get("STNO")` |
| `&SUBJECT` | R | ✓ | ✓ R | ✗ | Current subject string during match |
| `&TRACE` | RW | ✓ | ✓ | ✗ | Master TRACE switch; arm before TRACE() calls |
| `&TRIM` | RW | ✓ | ✓ | ~ stub | Declared `sno_kw_trim=1`; partially used in INPUT |
| `&UCASE` | R | ✓ | ✓ R | ~ | `sno_ucase[]` declared; not exposed as `&UCASE` |

---

## SPITBOL-Specific Notes (from sbl.lex)

**Protected keywords** (read-only — assignment raises error 209):
SPITBOL defines `k_p__` as the boundary. Keywords at offset ≥ `k_p__`
are protected. From the symbol table:
- Protected: `&FNCLEVEL`, `&LASTNO` and everything in the `k_alp` group
- The `k_alp` group (special access): `&ALPHABET`, `&RTNTYPE`, `&STCOUNT`,
  `&ERRTEXT`, `&FILE`, `&LASTFILE`, `&STLIMIT`, `&LCASE`, `&UCASE`

**Special assignment logic** (RW* keywords):
- `&STLIMIT` — `asg16`: subtracts old limit from `kvstl` on assignment.
  Sets the *remaining* budget, not the absolute limit. Semantics differ
  subtly from CSNOBOL4 which just stores the value.
- `&FULLSCAN` — `asg26`: validates the value before storing (must be nonzero
  to enable, any value to disable).

**Keywords in SPITBOL not in CSNOBOL4**:
- `&PROFILE` — execution profiling, SPITBOL extension
- `&FILE` / `&LINE` — source tracking (SPITBOL names differ from CSNOBOL4's
  `&LASTFILE` / `&LASTLINE`)

**Keywords in CSNOBOL4 not in SPITBOL**:
- `&GTRACE` — goto trace, CSNOBOL4 extension

---

## CSNOBOL4 Implementation Notes (from isnobol4.c / snobol4.c)

- `TRACE()` — fully implemented as a C function (`isnobol4.c:10950`).
  Dispatches to TRPHND in the interpreter loop. TRACE on `&STNO` fires
  per statement. **Verified working.**
- `DUMP()` — fully implemented (`isnobol4.c:412`). Terminal dump possible;
  `NODMPF` error string defined in `data.c`.
- `TRIM()` — fully implemented (`isnobol4.c:8020`).
- `&STLIMIT` / `&STCOUNT` — implemented in the SIL interpreter loop
  (`v311.sil` lines ~2617-2650). The C translation in `isnobol4.c` /
  `snobol4.c` carries this through.
- **Weird behavior confirmed**: TRACE dispatch counts against `&STLIMIT`.
  `TRACE('&STNO','KEYWORD')` with `&STLIMIT=5000` exhausted at stmt 207
  (inside `case.inc` init). Not a bug — working as designed. See MONITOR.md.

---

## SNOBOL4-tiny Patch Requirements

Keywords needed for the monitor to function (P1):

| Keyword | Current State | Fix Required |
|---------|--------------|--------------|
| `&STLIMIT` | ~ declared, now enforced (P001) | ✓ Done |
| `&STCOUNT` | ~ incremented but not readable | Wire to `sno_var_get("STCOUNT")` |
| `&STNO` | ~ emitted to COMM, not readable | Wire to `sno_var_get("STNO")` |
| `&INPUT` | ✗ not wired to stdin | P2 — suspected hang root cause |
| `&OUTPUT` | ✗ not wired to stdout | P2 — needed for output sync |
| `&TRACE` | ✗ not implemented | P3 — needed for oracle-style tracing |

When a keyword is patched in CSNOBOL4 C source to restore missing
functionality, that patch goes in this file under a **CSNOBOL4 Patches**
section with the file, line, what was stubbed, and what was restored.

