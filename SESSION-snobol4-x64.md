# SESSION-snobol4-x64.md — SNOBOL4 × x86 (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86

There is no such thing as a "DYN session" or "B session". There is only
**SNOBOL4 × x86**. The milestone track (sno4parse, Byrd box, TINY/beauty)
is clear from the sprint number and the NOW table. Session prefixes are
for sprint numbering only — they do not define separate session types.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### M-DYN-B1 orientation — binary boxes (RT-115, 2026-04-05)

bb_pool.c and bb_emit.c are NOT yet in the Makefile for scrip-interp.
bb_emit.c BINARY mode instruction helpers (bb_insn_*) are fully implemented — not stubs.
bb_build (PATND_t → bb_node_t C graph) already lives in stmt_exec.c and drives PASS=178.
exec_stmt Phase 3 calls root.fn(root.ζ, α) — same signature as .s box files.
The gap: bb_build_bin.c with bb_lit_emit_binary(), Makefile additions, Phase 2 wiring.
CODE() uses sno_parse/fmemopen (low priority — fix to cmpile_string later).
E_SCAN (X ? Y value context) is a stub in eval_node — low priority.

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
gcc -O0 -g -Wall -o sno4parse one4all/src/frontend/snobol4/CMPILE.c

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

### RT-116 type-system audit findings (2026-04-06)

Two-pass audit against v311.sil — datatype/coercion vertical.

**GAP 3 ✅ fixed (937d5ef):** ARRAY/TABLE stringify.
  ARBLK_t gains lo2/hi2; ndim restored to actual dim count.
  TBBLK_t gains init/inc; table_new_args() wires TABLE(n,m) args.
  VARVAL_fn DT_A → ARRAY('n') / ARRAY('lo:hi') / ARRAY('lo1:hi1,lo2:hi2').
  VARVAL_fn DT_T → TABLE(init,inc).

**GAP 2 ✅ fixed (4200cf1):** CONVERT() complete.
  compile_to_expression(src) in snobol4_pattern.c: parse→DT_E, no eval.
  NUMERIC: int-first, then real, FAIL otherwise.
  CODE/EXPRESSION/PATTERN all wired. Type guards on INTEGER/REAL coercions.

**GAP 4 ⬜ next:** sno_runtime_error(code, msg) infrastructure.
  to_int / to_real on DT_P/DT_A/DT_T → should abort with Error 1.
  Format: "Error 1 in statement N at level M\nIllegal data type"
  Mechanism: longjmp from stmt executor jmp_buf, or exit(1) with message.

**GAP 5 ⬜ small:** COPY() TABLE branch missing.

**Audit verticals not yet done:**
  Keywords (&ANCHOR/&TRIM/&ALPHABET/etc.), string builtin edge cases,
  pattern primitive completeness (XBAL, XEQFN, XDNME).

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/CMPILE.c` | Single-file SNOBOL4 parser / stream oracle |
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
| diag-01 | one4all `3a3d91d` · corpus `3fd44d0` · PASS=178/203 | P1c fix (IBLKTB 3-action) OR P2E (E_SCAN eval) OR milestone table update |
| RT-116 | one4all `ce3f5c6` · corpus `3fd44d0` · PASS=178/203 | GAP 4: sno_runtime_error() + to_int/to_real type guards → Error 1 on illegal types |
| RT-115 | one4all `b62c081` · corpus `3fd44d0` · PASS=178/203 | **M-DYN-B1** — emit LIT box as x86 binary into bb_pool, seal RW→RX, Phase 3 jumps to it. Gate: same PASS=178, binary path active for DT_S literal patterns. See BB-GEN-X86-BIN.md. |
| RT-114 | one4all `5a7e16e` · corpus `3fd44d0` · PASS=178/203 | M-CMPILE-MERGE Phases 0-2 ✅ COMPLETE (aliases already purged, cmpile_lower is live path) — next: Phase 3 --parser switch OR RUNTIME-6 DT_E blocker (expr_eval.sno → PASS≥179) |
| RT-108 | one4all `b107c67` · corpus `3fd44d0` · PASS=187/203 | RT-4 NMD ✅ NAM_push/save/commit/discard + last-write-wins — next: Option A (non-ASCII comment fix → cmpile_lower≥190) or Option B (RT-5 ASGN &OUTPUT hooks) |
| RT-106 | one4all `081cce9` · corpus `3fd44d0` · PASS=190/203 | cmpnd_to_expr KEYFN+ARYTYP fixed ✅ cmpile_lower label/subj wiring ✅ — next: non-ASCII comment fix → cmpile_lower as default (PASS=107→190) |
| RT-105 | one4all `805c390` · corpus `3fd44d0` · PASS=190/203 | --dump-parse ✅ cmpile_lower stub ✅ — next: cmpnd_to_expr() audit → wire cmpile_lower() as default execution path |
| RT-104 | one4all `d16f152` · corpus `3fd44d0` · PASS=190/203 | **M-CMPILE-MERGE** ✅ — next: --dump-parse/--dump-parse-flat flags in scrip-interp, then wire CMPILE as top-level file parser replacing sno_parse |
| 101 (sno4parse) | one4all `601890a` · corpus `65494e7` | 3 bugs fixed (include-hang, UNOPTB ST_EOS, BINOP ORFN-at-EOL); crosscheck 181/181 ✅ PASSED; gimpel 143/145 0 HANG — **Phase 2 gate DONE** — next: beauty/demo -I sweep OR pivot to EMITTER-X86 |

**Current milestone docs:**
- `BB-GEN-X86-BIN.md` — **M-DYN-B1 ACTIVE** (binary LIT box → Phase 2/3 wiring)
- `MILESTONE-SN4PARSE-VALIDATE.md` — Phase 2 crosscheck gate ✅ PASSED (sprint 101)
- `MILESTONE-SN4PARSE.md` — complete (SIL-faithful parser built)

**Next session first actions (sprint RT-115 — Track BB / binary boxes):**
```bash
cd /home/claude
apt-get install -y libgc-dev flex
tail -120 .github/SESSIONS_ARCHIVE.md
grep "^## " .github/GENERAL-RULES.md
cat .github/PLAN.md
cat .github/SESSION-snobol4-x64.md   # §INFO then §NOW
cd one4all && make scrip-interp
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh   # confirm PASS=178

# M-DYN-B1: emit LIT box as x86-64 binary, wire into exec_stmt Phase 2
#
# ORIENTATION (verified RT-115 session, 2026-04-05):
#   bb_pool.c  ✅  bb_alloc/bb_seal(mprotect RW→RX)/bb_free — NOT YET in Makefile
#   bb_emit.c  ✅  bb_emit_byte/u32/u64, bb_insn_*, BINARY label/patch — NOT YET in Makefile
#   bb_build   ✅  PATND_t → bb_node_t C graph, in stmt_exec.c — working, drives PASS=178
#   exec_stmt  ✅  5-phase; Phase 3 calls root.fn(root.ζ, α) — C fn ptr today
#   EVAL_fn    ✅  DT_E thaw + string → eval_via_cmpile — working
#   CODE()     ⚠️  uses sno_parse (Bison) via fmemopen — low priority, fix later
#   E_SCAN     ⬜  eval_node E_SCAN stub — low priority
#
# STEP 1 — Add bb_pool.c + bb_emit.c to Makefile (2 lines):
#   $(CC) $(CRT) -c $(RT)/asm/bb_pool.c -o $(OBJ)/bb_pool.o
#   $(CC) $(CRT) -c $(RT)/asm/bb_emit.c -o $(OBJ)/bb_emit.o
#
# STEP 2 — Create src/runtime/asm/bb_build_bin.c:
#   bb_box_fn bb_lit_emit_binary(const char *lit, int len)
#   Emits the LIT box as raw x86-64 bytes mirroring bb_lit.s exactly:
#     push rbx/r12; entry dispatch (cmp esi,0 / je LIT_α / jmp LIT_β);
#     LIT_α: bounds check (Δ+len > Ω → ω); memcmp via mov rax,&memcmp/call rax;
#     on match: rax=Σ+Δ, rdx=len, Δ+=len, ret; LIT_β: Δ-=len; LIT_ω: rax=0,rdx=0,ret
#   Globals Σ/Δ/Ω accessed via: mov rax, imm64(&global) / mov eax,[rax]
#   bb_alloc(512) → bb_emit_begin → emit bytes → bb_emit_end → bb_seal → return buf
#   lit/len baked as imm64/imm32 directly into emitted instructions (no zeta needed)
#
# STEP 3 — Wire into exec_stmt Phase 2, DT_S branch:
#   if (getenv("SNO_BINARY_BOXES")) {
#       bb_box_fn bfn = bb_lit_emit_binary(pat.s, strlen(pat.s));
#       if (bfn) { root.fn = bfn; root.ζ = NULL; goto phase3; }
#   }
#   /* fallback: existing C bb_lit path */
#
# GATE: PASS=178 with SNO_BINARY_BOXES unset (no regression)
#       PASS=178 with SNO_BINARY_BOXES=1 (binary path active for string literals)
#
# AFTER LIT WORKS: repeat for EPS, then wire bb_build binary walk for DT_P.
```

*(TINY/beauty: sprint B-292, one4all `acbc71e`, next: M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR — parked)*

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

### Sprint 98 §INFO addendum — 2026-04-05

**P2B root cause (FRWDTB ACT_STOP does not consume stopping char):**
Inside the NSTTYP SELECT loop, TEXTSP is positioned AT `,` after BINOP1
restores it. Must manually `TEXTSP.ptr++; TEXTSP.len--` before `FORWRD()`.
BRTYPE=CMATYP (not TEXTSP position) is the correct loop trigger.

**SELTYP=50** — new synthetic stype for SELECT/alt-eval nodes. stype_name()
returns `"SELECT"` for it. No conflict with any SIL stype (all ≤ 7).

**Sweep invariant:** always use `bash -c '...'` explicitly — the container
`/bin/sh` is dash, which rejects `[[` and `((` syntax.

### sil_macros.h — now wired to all RT files (sprint 103)
**Date:** 2026-04-05

`src/runtime/snobol4/sil_macros.h` is the SIL macro translation header (dual-axis:
RT functions + SM instruction dispatch). It is now `#include`d in:
- `src/driver/scrip-interp.c` — after `snobol4.h`, before `runtime_shim.h`
- `src/runtime/snobol4/snobol4.c`, `argval.c`, `invoke.c` — after `"snobol4.h"`
- `src/runtime/dyn/eval_code.c`, `stmt_exec.c` — after `"../snobol4/snobol4.h"`

**Rule:** All new RT-3+ code MUST use macros from `sil_macros.h`:
- Type tests: `IS_NAME(d)`, `IS_INT(d)`, `IS_STR(d)`, `IS_PAT(d)`, `IS_KW(d)`
- DT_N discriminator: `slen==1` → NAMEPTR (interior ptr); `slen==0` → NAMEVAL (name string)
  - Do NOT use `d.ptr != NULL` — NAMEVAL's `.s` and `.ptr` alias the same union field
  - Use `NAME_DEREF(d)` and `NAME_SET(nd, val)` for all DT_N read/write
- ASGNIC: use `INTVAL(to_int(val))` not `INTVAL_fn(val)` — the shim macro shadows `INTVAL_fn`

### Makefile added (sprint 103)
**Date:** 2026-04-05

`one4all/Makefile` now builds both targets:
- `make scrip-interp` — canonical interpreter build (matches sprint 100 canonical build)
- `make scrip-cc` — delegates to `src/Makefile`
- `make test` — runs `test/run_interp_broad.sh`
- `make clean` — removes `/tmp/si_objs` and `scrip-interp`

### CMPILE.c is now the authoritative parser — sno4parse retired (sprint 104)
**Date:** 2026-04-05

`sno4parse.c` is gone. `CMPILE.c` is the one SNOBOL4 lex/parser.
- Types: `CMPND_t` (parse node, was `NODE`), `CMPILE_t` (statement, was `STMT`)
- Public API in `CMPILE.h`: `cmpile_init`, `cmpile_file`, `cmpile_string`, `cmpile_free`
- `cmpnd_print_sexp(n, FILE*, oneline, depth)` — S-expression dump, pretty or flat
- `cmpile_print(s, FILE*, oneline, idx)` — statement dump
- `snobol4_pattern.c`: `cmpnd_to_expr()` replaces `node_to_expr()` using named SIL stype constants
- `eval_via_cmpile()` replaces `eval_via_sno4parse()` — EVAL() builtin path
- Top-level file parse still uses old bison `sno_parse` — replacement is next sprint
- one4all HEAD after this sprint: `d16f152`

### BINOP ST_EOS + operator-at-EOL fix (sprint 101)
**Date:** 2026-04-05

`BIOPTB['|']` action is `{ORFN, ACT_GOTO, &TBLKTB}`. When `|` is the last char
on a physical line before a continuation, TBLKTB hits ST_EOS (no trailing blank).
BINOP was returning CATFN unconditionally on ST_EOS, discarding STYPE=ORFN.

**Fix (CMPILE.c BINOP):** `if (or_ == ST_EOS && STYPE != 0) return STYPE;`

Same pattern applies to any operator at EOL before continuation. The subsequent
`FORWRD()` in `expr_prec_continue` loads the continuation via `forrun()`.

**Also fixed:** unresolved `-INCLUDE` now calls `sil_error()` (abort) not silent continue.
UNOPTB ST_EOS in UNOP loop now breaks (safety net).

Committed: one4all `601890a`. Sweeps: 84/84 ✅ · crosscheck 181/181 ✅ · gimpel 143/145 0 HANG.

### T_ Bison token → CMPILE SIL name rename (pending — RT-114)
**Date:** 2026-04-05

The Bison/Flex files (`snobol4.tab.h`, `snobol4.tab.c`, `snobol4.lex.c`, `test_lex.c`)
use `T_*` token names that must be renamed to their CMPILE SIL equivalents.
The authoritative mapping was written in a prior session but not committed to HQ.

**ACTION REQUIRED:** Lon to provide the complete T_ → CMPILE mapping so it can be
written here and executed. Do NOT attempt this rename without the full mapping —
multiple T_ tokens sharing a target name is wrong (collapses distinct parser states).

Known-correct subset (1:1, from CMPILE.c #defines):
| T_ name | CMPILE name |
|---|---|
| `T_ADDITION` | `ADDFN` |
| `T_SUBTRACTION` | `SUBFN` |
| `T_MULTIPLICATION` | `MPYFN` |
| `T_DIVISION` | `DIVFN` |
| `T_EXPONENTIATION` | `EXPFN` |
| `T_ALTERNATION` | `ORFN` |
| `T_COND_ASSIGN` | `NAMFN` |
| `T_IMMEDIATE_ASSIGN` | `DOLFN` |
| `T_CONCAT` | `CATFN` |
| `T_MATCH` | `BIQSFN` |
| `T_UN_PLUS` | `PLSFN` |
| `T_UN_MINUS` | `MNSFN` |
| `T_UN_PERIOD` | `DOTFN` |
| `T_UN_DOLLAR_SIGN` | `INDFN` |
| `T_UN_ASTERISK` | `STRFN` |
| `T_UN_AT_SIGN` | `ATFN` |
| `T_ASSIGNMENT` | `EQTYP` |
| `T_FUNCTION` | `FNCTYP` |
| `T_GOTO_S` | `SGOTYP` |
| `T_GOTO_F` | `FGOTYP` |
| `T_COMMA` | `CMATYP` |
| `T_RBRACK` | `RBTYP` |
| `T_INT` | `ILITYP` |
| `T_STR` | `QLITYP` |
| `T_REAL` | `FLITYP` |
| `T_IDENT` | `VARTYP` |
| `T_STMT_END` | `EOSTYP` |

Uncertain (need authoritative mapping):
`T_LABEL`, `T_END`, `T_KEYWORD`, `T_GOTO`, `T_GOTO_LPAREN`, `T_GOTO_RPAREN`,
`T_UN_AMPERSAND`, `T_UN_TILDE`, `T_UN_QUESTION_MARK`, `T_UN_EXCLAMATION`,
`T_UN_PERCENT`, `T_UN_SLASH`, `T_UN_POUND`, `T_UN_EQUAL`, `T_UN_VERTICAL_BAR`,
`T_POUND`, `T_PERCENT`, `T_TILDE`, `T_PIPE`, `T_PLUS`, `T_MINUS`, `T_STAR`,
`T_STARSTAR`, `T_SLASH`, `T_DOT`, `T_DOLLAR`, `T_QMARK`, `T_AT`, `T_HASH`,
`T_PCT`, `T_EQ`, `T_ERR`, `T_WS`, `T_EOF`, `T_BANG`, `T_CARET`, `T_AMPERSAND`,
`T_AT_SIGN`, `T_LPAREN`, `T_RPAREN`, `T_LBRACK`, `T_LANGLE`, `T_RANGLE`,
`T_LBRACKET`, `T_RBRACKET`

### P1c — IBLKTB 3-action bug (diagnosed 2026-04-05, diag-01 session)
**Date:** 2026-04-05

CSNOBOL4 IBLKTB has exactly 3 actions (GOTO FRWDTB / EOSTYP STOP / ERROR).
Our CMPILE.c has 4 actions: action[3]={NBTYP, ACT_STOPSH} is unreachable because
no chrs[] value of 4 is assigned. All non-special chars have chrs[x]=3 → actions[2]
= {EOSTYP, ACT_STOP} — NOT ST_ERROR as CSNOBOL4 does.

Effect: when BINOP calls IBLKTB with TEXTSP at a non-blank char (no leading space
= BINOP1 path), IBLKTB returns ST_STOP/STYPE=EOSTYP instead of ST_ERROR. BINOP
misroutes → EXPR() terminates early → NSTTYP force-sets BRTYPE=RPTYP → downstream
mispositioning → ELEMNT: illegal character on the following token.

**Fix:**
```c
static acts_t IBLKTB_actions[] = {
    {0,      ACT_GOTO,  &FRWDTB},  /* 0: space/tab → FRWDTB */
    {EOSTYP, ACT_STOP,  NULL},     /* 1: ';' → EOSTYP */
    {0,      ACT_ERROR, NULL},     /* 2: non-blank → ST_ERROR (BINOP1 path) */
    /* NO action[3] */
};
```
chrs[] bytes unchanged (authoritative). Only actions[] fixed.
Verified with two-way MONITOR: SNO_TRACE=1 diff shows IBLKTB divergence on '|'.
