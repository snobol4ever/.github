# MILESTONE-SS-TRANSLATE.md — Translate Every Missing SIL Block

**Goal:** Every non-BLOCKS SIL labeled block that currently has only a stub (`return FAIL`)
must be replaced with a faithful C translation, three-way synced against v311.sil and snobol4.c.
No runtime dependency can block translation. Writing the C is not running the C.

**Method:** One block at a time. Three-way sync. Build clean. Commit.

---

## The missing blocks (as of 2026-04-11)

### Group A — Compiler re-entry path (func.c)

These three blocks share the RECOMJ common path. They call `CMPILE_fn` (already exists),
`SPLIT_fn` (already exists), `EXPR_fn` (already exists), `TREPUB_fn` (already exists).
Nothing is missing. They were stubbed under the false label "M19 blocker."

| Block | SIL lines | File | Status |
|-------|-----------|------|--------|
| `RECOMJ/RECOMT/RECOM1/RECOM2/RECOMF/RECOMN/RECOMZ/RECOMQ` | 6492–6531 | func.c | ⬜ not translated — add as `recom_fn()` shared helper |
| `CODER_fn` | 6530–6533 | func.c | ⬜ stub → translate: VARVAL + branch to RECOMJ |
| `CONVEX` | 6544–6551 | func.c | ⬜ not translated — EXPR + TREPUB + set E type + RECOMZ |
| `CONVE_fn` | 6534–6543 | func.c | ⬜ stub → translate: SETAC SCL,2 + branch to RECOMJ |

### Group B — DEFFNC (define.c)

Full argument-binding save/restore + INTERP call. `INTERP_fn` already exists.
Nothing missing. Stubbed under false "M19 blocker."

| Block | SIL lines | File | Status |
|-------|-----------|------|--------|
| `DEFFNC_fn` (+ DEFF1..DEFF20, DEFFF, DEFFC, DEFFN, DEFFNR, DEFFGO, DEFFVX, DEFFGO, DEFFS1, DEFFS2) | 4310–4470 | define.c | ⬜ stub → full translation (~80 SIL lines) |

### Group C — LOAD_fn (extern.c)

Written this session but does not compile. Fix the 3 include/declaration errors.

| Block | SIL lines | File | Status |
|-------|-----------|------|--------|
| `LOAD_fn` / `LOAD2` | 4471–4535 | extern.c | ⚠️ written but broken — fix STREAM_fn/VARATB/LODCL declarations |

### Group D — Platform stub signature mismatches (platform.c)

SIL translation in io.c is correct. Platform stubs have wrong signatures.
The io.c extern declarations are the spec; fix platform.c to match.

| XCALL | What io.c expects | What platform.c defines | Fix |
|-------|-------------------|--------------------------|-----|
| `XCALL_IO_OPENI` | `RESULT_t (DESCR_t, SPEC_t*, SPEC_t*, DESCR_t*)` | `void (DESCR_t, SPEC_t*)` | Fix sig in platform.c |
| `XCALL_IO_OPENO` | `RESULT_t (DESCR_t, SPEC_t*, SPEC_t*)` | `void (DESCR_t, SPEC_t*)` | Fix sig in platform.c |
| `XCALL_IO_SEEK` | `RESULT_t (DESCR_t, DESCR_t, DESCR_t)` | `void (DESCR_t, DESCR_t)` | Fix sig in platform.c |

---

## Order of work

1. **Group D** — fix platform stub signatures. Trivial. Gets io.c callers correct.
2. **Group C** — fix LOAD_fn compile errors. Add missing extern decls to extern.c.
3. **Group A** — translate RECOMJ path, then CODER_fn, CONVE_fn, CONVEX.
4. **Group B** — translate DEFFNC_fn fully (~80 SIL lines).

---

## Done when

All stubs replaced. Build clean (0 errors, 0 warnings). Every SIL line outside BLOCKS
has a corresponding C translation. M-SS-STUBS can then be closed.
