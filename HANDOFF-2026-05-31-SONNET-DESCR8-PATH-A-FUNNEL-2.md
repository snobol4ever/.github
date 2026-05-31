# HANDOFF 2026-05-31 SONNET — DESCR8 PATH A FUNNEL (continuation 2)

**Author:** Claude Sonnet · **Director:** Lon · **Branch:** `descr8-macro-funnel` (SCRIP)
**Status:** exploration, NOT an active PLAN goal. Continues
`HANDOFF-2026-05-31-SONNET-DESCR8-MACRO-FUNNEL.md`. PLAN.md goals UNTOUCHED.

## What this session did — Path A C funnel, the big push

Continued the descr.h GET_/SET_/MK_ accessor funnel. Branch base `22b4355`.
Converted every confirmed-DESCR field access (READ/WRITE) outside the macro
layer across the whole runtime/lowering/driver surface. Method per the prior
handoff's NO-REGEX rule: hand-verified each receiver is genuinely a DESCR_t,
edited by exact line+text match, rebuilt, ran smokes, committed per file.

### Commits (base 22b4355 → HEAD ea6a0fb)
| Commit | File(s) | Sites |
|--------|---------|-------|
| 51d4188 | core.c | 41 + 2 MK_DATA |
| 06420d5 | pattern.c | 36 |
| 02d52da | bb_exec.c | 31 |
| 390bdea | gen_runtime.c | 47 (6 false-pos skipped) |
| ede61cb | rt.c | 16 |
| 41cc0b7 | eval_code.c + stmt_exec.c + eval_pat.c | 20 |
| 818833f | tail: interp_call/data/ref, invoke, name_t, lower_program, runtime_shim.h, core.c, core.h, name_save.c | 23 |
| 462a6ac | final 3 genuine (interp_call named.ptr, lower_program DT_S build, gen_runtime td.tbl) | 3 |
| ea6a0fb | gen_runtime cset discriminators → IS_CSET | 2 |

**~221 field-access sites funneled.** Scanner: 314 → real-field-access(READ/WRITE)
remaining = 17, all confirmed exclusions (see below). 72 SENTINELs remain
(step-2 tranche, below).

### Constructors used
- `BSTRVAL(s,len)` for `{.v=DT_S,.slen=len,.s=s}` designated-inits.
- `MK_DATA(p)` for `{.v=DT_DATA,.ptr/.u=p}`; `MK_TBL(t)` for `{.v=DT_T,...tbl=t}`.
- `GET_*`/`SET_*` for all reads/writes; `IS_CSET` for cset discriminators.

### FALSE POSITIVES confirmed + left raw (NOT DESCR_t)
- `_var_reg[].ptr` (core.c 2320/2449/2460/2536) — variable-registry struct.
- `g_kw_cset_names[].ptr` (gen_runtime 1895/1900/1910/1916/1941/1960) —
  `struct {const char*ptr; const char*name; int len;}`, NOT DESCR.
- `ctx.p` (snocone_parse.tab.c) — LexCtx. `tbl[i].p/.a/.n` (prolog_builtin) —
  builtin table. `e->slen` (name_save) — entry struct (the DESCR built from it
  WAS converted to BSTRVAL).
- `core.h` lines 21/318/319 — the BSTRVAL/TABLE_VAL/ARRAY_VAL constructor-macro
  DEFINITIONS themselves; stay raw by definition.
- `bb_box.h` 8/10 — function signatures (`int δ`), scanner artifact.
- `bb_iterate.cpp:98` — a comment.

## Verification — every commit byte-identical to baseline
Baseline (= prior handoff): snobol4 smoke 3/13, icon m2 5/6 (HARD), m3 0/6,
byte-identity gate FAIL=4 (pre-existing SMX SNOBOL4 mode-3 severance, NOT a
regression). EVERY commit above held all four numbers identical. Build needs
`libgc-dev`. GATE-PK is N/A on this branch (PASS=0/GONE=1115 — branch predates
main's LOWER2 per-kind restructuring; smokes are this branch's gate, per the
prior handoff).

## NEXT — step 2: the 72 SENTINELs (name discriminators) — DECISION NEEDED
Breakdown: 7 cset (2 done → IS_CSET; rest are partial-exprs/macro-defs),
20 `slen==1` name-PTR, 41 `slen==0` (name-VAL reads + `.slen=0` field-builds),
4 other.

**The clean macros ALREADY EXIST but in the WRONG header for runtime scope:**
`src/emitter/sil_macros.h:79-80` defines
`IS_NAMEPTR(d) ((d).v==DT_N && (d).slen==1 && (d).ptr)` and
`IS_NAMEVAL(d) ((d).v==DT_N && (d).slen==0 && (d).s)`. These are EMITTER-side
and not in scope across the runtime where most of the 72 sentinels live.

**⚠ DECISION FOR LON:** to funnel the name-discriminator tranche, move (or
mirror) `IS_NAMEPTR`/`IS_NAMEVAL` (+ a `MK_NAMEVAL`/`MK_NAMEPTR` constructor
pair for the `.slen=0/1`+`.ptr/.s` builds) into `descr.h` so they're in scope
everywhere (descr.h is pulled via core.h universally). This is the same
"put accessors in descr.h" rationale as Path A. Once relocated, the 61
name-discriminator sentinels convert mechanically (byte-identical expansions).
Did not do this unilaterally — it's a header-ownership/naming call.

## THEN — steps 3/4/5 (unchanged from prior handoff)
3. C-funnel GATE: grep proves ZERO raw DESCR field access outside
   descr.h/sil_macros.h/core.h. After step 2 + the false-positive allowlist,
   this should be reachable.
4. Emitter-side funnel (layer 3): add `descr_off_*`/`descr_stride` to
   `sm_emit_t g_emit`; route the ~6 inline-descriptor x86 build sites through
   `s_descr_push()` (already exists, emit_str.cpp, used by bb_iterate). The
   layout-mode global `g_descr_layout` (default DESCR_LAYOUT_16) is in place.
5. 8-byte struct + RBP basing behind a CLI flag. GC: prototype option A
   (arena as single Boehm root), end-state option C (mmap-reserve stable base).
   B is off the table. (Full rationale in prior handoff's GC GATE section.)

## Files touched this session
All under SCRIP `src/` (see commit table). No new scripts; reused
`scripts/descr8_scan.py`. `.github` gets this handoff doc.
