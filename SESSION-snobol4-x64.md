# SESSION-snobol4-x64.md — SNOBOL4 × x86 (one4all)

**Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** x86

There is no such thing as a "DYN session" or "B session". There is only
**SNOBOL4 × x86**. The milestone track (sno4parse, Byrd box, TINY/beauty)
is clear from the sprint number and the NOW table. Session prefixes are
for sprint numbering only — they do not define separate session types.

---

## ⛔ §INFO — session invariants (append-only, read every session)

### Architecture: unified SCRIP executable (RT-125, 2026-04-06)

**scrip-interp and scrip-cc are retired as separate concepts.**
There is now ONE executable: `scrip`, with two modes:
- `scrip --interp source.sno` — Mode I: interpretive (existing tree-walk, correctness reference)
- `scrip --gen   source.sno` — Mode G: in-memory generative (x86 bytes → mmap slab → jump in)
- `scrip          source.sno` — Mode G by default

No .s file emission. No nasm subprocess. No ld subprocess. No disk round-trips.
`bb_emit.c` EMIT_BINARY mode writes bytes directly into `mmap(MAP_ANON)` slabs.
`bb_pool.c` segment 3 (Byrd box pool) unchanged. Segments 0–2, 4 are new mmap slabs.

**Read `SCRIP-UNIFIED.md` for full design.** Development sequence: U0 → U1 → U2 → U3 → U4 → U5.
Two-way MONITOR: `scrip --interp` vs SPITBOL (existing); `scrip --interp` vs `scrip --gen` (new JIT axis).

**HARNESS:** change `INTERP=scrip-interp` → `INTERP=scrip` after M-SCRIP-U0.
**Binary target in Makefile:** rename `scrip-interp` → `scrip`.



### EVAL(DT_E) dispatch hijack suspect (RT-120, 2026-04-06)

ir.h struct fix applied (RT-120), sizeof=56 confirmed. EVAL_fn debug
shows _EVAL_ wrapper is NOT called at all when EVAL(E) runs with E=DT_E.
Suspect: E_FNC dispatch in interp_eval checks label_lookup(e->sval) before
APPLY_fn. If prescan_defines somehow registered "EVAL" as a user label,
call_user_function runs instead → returns NULVCL, never touches EVAL_fn.
Fix path: add fprintf to _EVAL_ in snobol4.c; if absent, audit label_lookup
and add builtin-exempt guard for known builtins (EVAL, CODE, DATA, etc.).

### EVAL(DT_E) root cause — EXPR_t struct layout mismatch (RT-119, 2026-04-06)

GC_MALLOC fix (RT-119) applied but EVAL(DT_E) still returns empty.
True root cause: snobol4_pattern.c includes scrip_cc.h which defines
EXPR_t with ival=long (32-bit); eval_code.c/scrip-interp.c use ir.h
EXPR_t with ival=long long + extra fields. cmpnd_to_expr allocates
scrip_cc.h-sized struct; eval_node reads children/nchildren at ir.h
offsets → wrong memory → NULL children → NULVCL returned.
Fix: add #include "../../ir/ir.h" BEFORE the scrip_cc.h line in
snobol4_pattern.c. EXPR_T_DEFINED guard in scrip_cc.h will skip its
own definition, leaving ir.h layout active for cmpnd_to_expr.

### EVAL(DT_E) bug — calloc/GC mismatch (RT-118, 2026-04-06)

EVAL(CONVERT(s,"EXPRESSION")) returns empty. Root cause: cmpnd_to_expr()
uses calloc() throughout; Boehm GC cannot see calloc'd memory, so EXPR_t
children are collected between CONVERT and EVAL. Fix: replace every
calloc(1,sizeof *e) and calloc(n,sizeof(EXPR_t*)) in cmpnd_to_expr
(snobol4_pattern.c) with GC_malloc + zero-init (or GC_MALLOC).
Same audit needed in eval_code.c. Gate: PASS=178; EVAL('2 + 3')=5 via
DT_E path (not just string path).

### M-DYN-B* REDO — inline-blob ABI, no push/pop (RT-120, 2026-04-06)

Prior B1–B10 work (RT-116 through RT-120) used C-function trampolines.
VOIDED. New design: self-contained x86 code+data blobs in bb_pool.

**ABI:**
- `rdi` on entry = buffer base address (fn ptr == buffer start)
- `esi` = 0 (α) or 1 (β)  
- `r10`, `r11` = scratch only (caller-saved — zero push/pop)
- Prologue: `mov r10,rdi(3) + cmp esi,0(3) + je α(2) + jmp β(2)` = 10 bytes
- Data section appended after code in same sealed RX buffer
- Baked absolute ptr slots for Σ/Δ/Ω/memcmp in data section
- Mutable state (done, fired, n, count...) also in data section as writable-before-seal fields

**M-DYN-B0 first actions:**
```bash
# Reset bb_build_binary_node() to return NULL for all kinds (full C fallback)
# Remove or ifdef-out all bb_*_emit_binary() trampoline emitters
# Keep bb_pool.c / bb_emit.c / bb_build_bin.c skeleton
# PASS=178 (C path unchanged)
# Then implement B1: bb_fail_inline() = 5-byte blob
```

**Milestone B0 = reset + verified C fallback; B1 = FAIL inline; B2 onward per BB-GEN-X86-BIN.md**

### M-DYN-B10 complete — 100% binary coverage (RT-120, 2026-04-05)

All 25 PATND_t box kinds now handled in bb_build_binary_node(). Zero BIN_MISS
events across full corpus. Key structural facts for future work:

- `bb_callcap_exported()` / `bb_callcap_new()` — in stmt_exec.c, placed AFTER
  `bb_callcap` closes (~line 563). Do NOT move above bb_callcap definition.
- `bb_deferred_var_exported()` / `bb_dvar_bin_new()` — in stmt_exec.c, placed
  AFTER `bb_deferred_var` closes. Same ordering constraint.
- `bb_atp` removed from Makefile box-loop exclusion list — it is now compiled
  from boxes/atp/bb_atp.c AND has a static copy inside stmt_exec.c. No linker
  conflict (static is TU-local). Do NOT re-add bb_atp to the exclusion list.
- XATP deferred-usercall form (STRVAL_fn != "@") still falls back to C path
  (returns NULL from bb_atp_emit_binary). This is intentional and correct.
- Coverage audit: `SNO_BIN_MISS_LOG=1 SNO_BINARY_BOXES=1 scrip-interp file.sno`
  logs BIN_MISS:kind=N to stderr for any C-path fallback.

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

**Oracle: SPITBOL x64 only** — `/home/claude/x64/bin/sbl`
CSNOBOL4 is Silly SNOBOL4 track only. See SESSION-silly-snobol4.md. Not used here.

### P2A — binary `?` operator (sprint 94)
**Date:** 2026-04-04

`?` (byte 63) was already in BIOPTB chrs[] → action 14 → `BIQSFN` (214).
The entire fix: `op_prec(BIQSFN) = 1` — lowest binary precedence per SPITBOL spec.
No new table. No new actions. No g_bioptb pointer. One line.

### True streaming — no linebuf, no pre-joining (sprint 92)
**Date:** 2026-04-04

SIL XLATNX keeps TEXTSP = one physical line. FORWRD/FORBLK call FORRUN on ST_EOS
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

Correctness = **agreement with SPITBOL** (`/home/claude/x64/bin/sbl`). sno4parse era complete.

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

`A[J=J+1]` is NOT parsed as an ASSIGN node. SIL ELEARG re-enters EXPR after
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
| `src/backend/emit_x64.c` | Pattern statement emission |
| `src/runtime/snobol4/stmt_exec.c` | `stmt_exec_dyn` — five-phase executor |
| `src/runtime/asm/bb_pool.c` | mmap pool ✅ |
| `src/runtime/asm/bb_emit.c` | byte/label/patch primitives ✅ |
| `src/runtime/dyn/` | bb_*.c — 25 C box implementations ✅ frozen |
| `src/driver/scrip-interp.c` | tree-walk interpreter |
| `src/backend/emit_x64.c` | x64 emitter |

---

## §NOW

⛔ §NOW lives only in PLAN.md. Never in SESSION docs.
