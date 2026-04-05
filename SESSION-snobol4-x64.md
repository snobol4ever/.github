# SESSION-snobol4-x64.md — SNOBOL4 × x86 (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86

There is no such thing as a "DYN session" or "B session". There is only
**SNOBOL4 × x86**. The milestone track (sno4parse, Byrd box, TINY/beauty)
is clear from the sprint number and the NOW table. Session prefixes are
for sprint numbering only — they do not define separate session types.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### v311.sil and two-way MONITOR script locations
**Date:** 2026-04-05

When a STREAM table sequence is unknown: **read v311.sil first**, then syn.c for bytes:
```bash
/home/claude/snobol4-2.3.3/v311.sil      # SIL procedure bodies
/home/claude/snobol4-2.3.3/syn.c         # chrs[] table bytes (authoritative)
/home/claude/snobol4-2.3.3/syn_init.h    # action put/act/go assignments
```

Two-way MONITOR scripts are checked in beside the csnobol4 patches:
```bash
one4all/csnobol4/dyn89_sweep.sh   # sweep corpus/programs/snobol4/
one4all/csnobol4/stream.c         # CSNOBOL4 patch → /tmp/sno_csno.trace
one4all/csnobol4/main.c           # CSNOBOL4 patch
one4all/csnobol4/README.md        # full workflow
```

Standard diff workflow:
```bash
SNO_TRACE=1 /home/claude/snobol4-2.3.3/snobol4 /tmp/x.sno 2>/dev/null  # → /tmp/sno_csno.trace
SNO_TRACE=1 /home/claude/sno4parse /tmp/x.sno 2>/tmp/sn.trace
diff /tmp/sno_csno.trace /tmp/sn.trace | head -30
```



Patches are checked in. Copy and build — never re-instrument from scratch:
```bash
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0"
```
Files: `one4all/csnobol4/stream.c`, `main.c`, `README.md`, `dyn89_sweep.sh`

### P2A — binary `?` operator (sprint 94)
**Date:** 2026-04-04

`?` (byte 63) was already in BIOPTB chrs[] → action 14 → `BIQSFN` (214).
The entire fix: `op_prec(BIQSFN) = 1` — lowest binary precedence per SPITBOL spec.
No new table. No new actions. No g_bioptb pointer. One line.

### True streaming — no linebuf, no pre-joining (sprint 92)
**Date:** 2026-04-04

CSNOBOL4 XLATNX keeps TEXTSP = one physical line. FORWRD/FORBLK call FORRUN on ST_EOS
to fetch the next card. NEWCRD dispatches: CNTTYP → strip '+', re-drive; NEWTYP → save
as pending. We do the same. linebuf pre-join is permanently banned.

SIL STREAM 6-arg convention:
  `STREAM out, in, table, error_branch, eos_branch, stop_branch`
  C stream() returns: ST_ERROR→arg4, ST_EOS→arg5, ST_STOP→arg6 (omitted = fall through)

All five stream() call-site bugs fixed in sprint 92 (one4all `229b04e`):
- FORWRD: ST_EOS → forrun(), not BRTYPE=EOSTYP
- FORBLK: ST_EOS → forrun(); ST_ERROR = RTN1 (no blank) — leave BRTYPE as-is
- ELEMTB: ST_EOS + STYPE==0 → sil_error (ELEILI)
- GOTOTB: ST_EOS → sil_error (CERR12)
- LBLTB: ST_ERROR → sil_error (CERR1)

Result: 84/84 sweep.

Correctness = **agreement with CSNOBOL4**, not independent correctness:
- CS succeeds + sno4parse succeeds → OK
- CS errors + sno4parse errors → OK (both reject — positive AND negative tests count)
- CS succeeds + sno4parse errors → **BUG**
- CS errors + sno4parse succeeds → **BUG** (too permissive)

For hard bugs: `SNO_TRACE=1` on both, diff `/tmp/sno_csno.trace` vs stderr. First divergence = root cause.

### sno4parse build and -I flags
**Date:** 2026-04-04

```bash
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c

IFLAGS="-I/home/claude/corpus/programs/lon/sno \
  -I/home/claude/corpus/programs/lon/rinky \
  -I/home/claude/corpus/programs/lon \
  -I/home/claude/corpus/programs/beauty \
  -I/home/claude/corpus/programs/gimpel \
  -I/home/claude/corpus/programs/include \
  -I/home/claude/corpus/programs/aisnobol \
  -I/home/claude/corpus/programs/snobol4/beauty \
  -I/home/claude/corpus/programs/snobol4/demo \
  -I/home/claude/corpus/programs/snobol4/smoke \
  -I/home/claude/corpus/lib \
  -I/home/claude/corpus/crosscheck/library/lib"
```

### Sweep baselines
**Date:** 2026-04-04

| Sweep | OK | FAIL | Notes |
|-------|----|------|-------|
| No -I, after ? fix | 487 | 64 | |
| No -I, after -INCLUDE | 486 | 65 | INFINIP transitive |
| All -I flags | 449 | 102 | real bugs exposed |

199 unique missing include paths — not sno4parse bugs.

---

### Chained [] subscript fix (sprint 96)
**Date:** 2026-04-04

CMPILE calls `ELEMNT()` for subject, not `EXPR()` — `expr_prec_continue` never runs.
Fix: inline postfix-`[]` loop after `ELEMNT()` in CMPILE subject path.
After `ACT_STOP` on `]`, `BRTYPE==RBTYP=7` (not NBTYP=1). Check only
`TEXTSP.len>0 && *TEXTSP.ptr=='['` — no BRTYPE guard. Loop handles triple+ chaining.
When `TEXTSP.len==0 && BRTYPE==RBTYP` (segment exhausted), call `FORWRD()` first.

Remaining P2D (`A[J=J+1]`): EQTYP fires inside ELEARY subscript loop → terminates early.
Fix: when `BRTYPE==EQTYP` inside `[]` subscript parse, treat `=` as assignment op,
parse `J=J+1` as an expression (call `EXPR()` which handles `=` as binary op if P2D implemented,
or handle via CMPFRM-style sub-parse). MONITOR on Listen2WordPress.sno first.


### P2D — assignment inside subscript `A[J=J+1]` (sprint 97)
**Date:** 2026-04-05

`A[J=J+1]` is NOT parsed as an ASSIGN node. CSNOBOL4 ELEARG re-enters EXPR after
EQTYP: IBLKTB consumed `=`; two `FORWRD()` calls skip past `=` and its trailing
space; next EXPR yields `J+1` as a second subscript arg. Result: two-arg subscript.

Fix in all three subscript loops (ELEARY `<>`, postfix `[]`, CMPILE subject `[]`):
```c
if (BRTYPE == EQTYP) { FORWRD(); FORWRD(); continue; }
```
Key: SIL UNOP calls FORWRD before UNOPTB (v311.sil:2507); our ELEMNT does not.
The two FORWRDs bridge this gap. Sweep 84/84 confirmed.

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/sno4parse.c` | Single-file SNOBOL4 parser / stream oracle |
| `one4all/csnobol4/` | CSNOBOL4 STREAM trace patches |
| `src/backend/emit_x64.c` | Pattern statement emission |
| `src/runtime/snobol4/stmt_exec.c` | `stmt_exec_dyn` — five-phase executor |
| `src/runtime/asm/bb_pool.c` | mmap pool ✅ |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives ✅ |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations ✅ frozen |
| `src/driver/scrip-interp.c` | tree-walk interpreter |
| `src/backend/emit_x64.c` | x64 emitter |

---

## §NOW

One track. Current sprint is whatever Lon is working on — the sequence is
rearrangeable at any time. Past sprints live in SESSIONS_ARCHIVE.md.

| Sprint | HEAD | Next milestone |
|--------|------|----------------|
| 97 | one4all `badbbf9` · corpus `8d5cc6a` | P2D ✅ sweep 84/84 — next: P2B alt-eval `(e1,e2,en)` or P2F `;` multi-stmt |
| 100 | one4all `888c282` · corpus `65494e7` | PASS=188/201; beauty blocked by `;` stmt-separator + `&ALPHABET` gaps. Fix `;` first → ~195/201. Then sil_macros.h Option C + RT-3. |

**Current milestone docs:**
- `MILESTONE-SN4PARSE-VALIDATE.md` — active; Phase 1 84/84 ✅; Phase 2 P2D ✅; next P2B or P2F
- `MILESTONE-SN4PARSE.md` — complete (SIL-faithful parser built)

**Next session first actions:**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-snobol4-x64.md        # §INFO then §NOW
cat .github/MILESTONE-SN4PARSE-VALIDATE.md  # current milestone phases + remaining bugs
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
bash one4all/csnobol4/dyn89_sweep.sh   # confirm 84/84
# P2B: (e1,e2,en) alternative eval — NSTTYP branch in ELEMNT, comma-list → E_SELECT
# P2F: semicolon multi-statement — loop in parse_program() after ST_EOS on ';'
```

*(TINY/beauty: sprint B-292, one4all `acbc71e`, next: M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR — parked)*

**sno4parse next session first actions (sprint 91):**
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/SESSION-snobol4-x64.md
cat .github/MILESTONE-SN4PARSE-VALIDATE.md
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/sno4parse.c
cp one4all/csnobol4/stream.c snobol4-2.3.3/lib/stream.c
cp one4all/csnobol4/main.c   snobol4-2.3.3/main.c
cd snobol4-2.3.3 && make -j$(nproc) COPT="-DTRACE_STREAM -g -O0" 2>&1 | tail -3
cd /home/claude
# 1. g_error lifecycle: grep -n "g_error\|sil_error" one4all/src/frontend/snobol4/sno4parse.c | head -30
# 2. SNO_TRACE=1 ./sno4parse corpus/programs/snobol4/demo/inc/Qize.sno 2>&1 | grep "ret=ERROR"
# 3. BRTYPE=1 postfix subscript: sed -n around ELEFNC + expr_prec_continue '[' detection
```

### ✅ LINEBUF PRE-JOIN REMOVED (sprint 92)
**Date:** 2026-04-05 → implemented 2026-04-04

True streaming implemented. linebuf gone. forrun() is the canonical continuation handler.


### Sprint 95 §INFO addendum
**Date:** 2026-04-04

**FORWRD must be called before RHS in expr_prec_continue (sprint 95)**
Binary operators with double-space after them (e.g. `'A'  |  'B'`) lost the
RHS because ELEMNT was called with TEXTSP pointing at leading whitespace.
Fix: unconditional `FORWRD()` before `expr_prec(next_min)` in expr_prec_continue.
Mirrors CSNOBOL4's IBLKTB call between operator and RHS.

**CMPGO SGOTYP/FGOTYP need FORWRD before EXPR (sprint 95)**
Computed goto `:S($('label' VAR))` requires FORWRD() in SGOTYP and FGOTYP
branches — not just STOTYP/FTOTYP. One unconditional FORWRD() covers both
paren and angle-bracket forms.

### Sprint 98 first actions (scrip-interp / SIL track) — appended 2026-04-05
**Date:** 2026-04-05

```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/MILESTONE-RT-SIL-MACROS.md    # READ FIRST — vocabulary for all RT work
cat .github/MILESTONE-RT-RUNTIME.md
cat .github/SESSION-snobol4-x64.md

# Build with argval.c now in the loop:
# Add src/runtime/snobol4/argval.c to the runtime for-loop in the build command
# x86_stubs_interp.c provides stmt_init — use instead of snobol4_stmt_rt.c
# Confirm PASS=177 FAIL=1

# PRIORITY 1: sil_macros.h
#   Create src/runtime/snobol4/sil_macros.h (Groups 1+2 of MILESTONE-RT-SIL-MACROS.md)
#   TESTF, VEQLC, DEQL, AEQLC, INCRA, DECRA
#   IS_INT, IS_REAL, IS_STR, IS_PAT, IS_NAME, IS_KW, IS_EXPR, IS_CODE
#   SPCINT_fn, SPREAL_fn, REALST_fn, INTSP_fn stubs → forward to RT functions

# PRIORITY 2: SCRIP-SM.md update — 12 new SM ops
#   SM_JUMP_INDIR, SM_SELBRA, SM_STATE_PUSH, SM_STATE_POP
#   SM_INCR, SM_DECR, SM_LCOMP, SM_RCOMP, SM_TRIM, SM_ACOMP, SM_SPCINT, SM_SPREAL

# PRIORITY 3: Fix PLS — one line in SNO_INIT_fn in snobol4.c:
#   register_fn("PLS", _b_pos, 1, 1)

# Commit: "RT-SIL: sil_macros.h + 12 new SM ops + PLS unary fix; PASS=177"

# PRIORITY 4: RT-3 NAME_fn + ASGNIC_fn + DT_K keyword dispatch
#   src/runtime/snobol4/snobol4.c — use sil_macros.h TESTF/IS_KW from day one
#   Gate: PASS >= 177
```

### Sprint 100 §INFO addendum — 2026-04-05

**Beauty driver root cause: `;` separator + `&ALPHABET`**

`demo/inc/global.sno` uses `;*` inline comments:
```snobol4
    &ALPHABET      POS(0)  LEN(1) . nul    ;* null character
```
Two parser gaps:
1. `;` as statement separator — SNOBOL4 spec allows multiple stmts per line separated by `;`.
   After `;`, `*` starts a comment (`;*` = rest-of-line comment). Our parser does not handle `;`.
   Fix: in lex BODY state, emit end-of-statement on `;`, then check if next char is `*` (→ comment).
2. `&ALPHABET` — not in our keyword table. Assignment to `&ALPHABET` sets character class.
   Can stub as no-op (ignore RHS) since corpus tests don't exercise char class matching.

**Build prerequisites (sprint 100+):**
```bash
apt-get install -y libgc-dev flex
```
`libgc-dev` for Boehm GC headers. `flex` to regenerate `snobol4.lex.c` after `.l` changes.

**Object file rule (CRITICAL):**
- INCLUDE: `x86_stubs_interp.o` (provides `stmt_init` stub + `subject_data`/`subject_len_val`/`cursor` globals)
- EXCLUDE: `snobol4_stmt_rt.o` (conflicts on `stmt_init`)

**PLS registered** (sprint 100): `register_fn("PLS", _b_pos, 1, 1)` in `snobol4.c`.
**-INCLUDE transitive dir** (sprint 100): `snobol4.l` all three handlers add resolved dir to `inc_dirs`.
