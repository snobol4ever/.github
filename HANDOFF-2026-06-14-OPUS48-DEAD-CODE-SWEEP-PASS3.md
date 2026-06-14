# HANDOFF 2026-06-14 · Opus 4.8 · DEAD-CODE SWEEP PASS 3 — reproducible oracle + closed-subgraph law

**Goal:** GOAL-DEAD-CODE-SWEEP.md. **SCRIP base 3f3786d → 2a35216 (pushed).** **.github → 0ad6bb17 (pushed).**
**Gates green, zero regress:** smoke M3 7/7 · M4 7/7 (HARD) · pat-rung M4 19/19 0-SKIP / M3 15/19 · fence TIER1=TIER2=0.

## Landed
1. **3 self-contained whole-dead TUs → attic (14 fns):** `runtime/core/invoke.c` (ARGVAL_fn, INVOKE_fn) ·
   `parser/rebus/rebus_emit.c` (8 fns) · `parser/rebus/rebus_print.c` (4 fns). Dead count **594 → 580**.
   Makefile: 6 lines dropped (3 RT_PIC_SRCS entries + 3 `scrip:` recipe lines — most dead files appear in both).
2. **`scripts/util_gc_dead_oracle.sh`** — the deterministic instrument, now reproducible: recompiles all TUs with
   `-ffunction-sections -fdata-sections` via the Makefile `WARN` hook (concatenated into CBASE/CRT/CXXRT, NOT the
   link line), re-links scrip with `--gc-sections --print-gc-sections` → `/tmp/dead_current.txt`. Re-run to
   regenerate; never hand-maintain the list. (This is why the goal file's old 580-name block is now a pointer.)

## ⛔ THE CLOSED-SUBGRAPH LAW (do-not-re-derive)
`--gc-sections` strips dead caller+callee together, so the oracle binary always links. The REAL build has no
`--gc-sections`, so removing a leaf dead TU in isolation leaves still-compiled dead callers dangling →
`undefined reference`. First pass-3 attempt removed 6 fully-dead TUs at once and the link failed on
`bb_cap_new`/`bb_cap_new_call`/`bb_arbno_new` (dead callers in emit_bb.c+rt.c), `interp_eval_ref`
(gen_runtime.c:185), `name_commit_value` (name_save.c:123). **Safe-removal gate: a fully-dead TU is removable in
isolation iff `make scrip` links with ZERO unresolved after deletion** (ld lists all unresolved at once). Reverted
the 3 entangled (name_t/bb_boxes/interp_ref), kept the 3 clean.

## VALIDATION (3 deterministic proofs — all passed; required before any batch lands)
1. GC-binary gate parity: `SCRIP=/tmp/scrip_gc` (594 fns physically stripped) passes smoke/pat-rung/fence == baseline.
2. All-6-language `--compile` emit byte-identical real-vs-GC after `sed -E 's/bb[0-9]+_/bbN_/g'` (Icon/Prolog
   differ ONLY in heap-derived label numerals; normalize → match). Also verified new scrip == pre-removal binary.
3. `comm -12 <emitted-call-targets> /tmp/dead_current.txt` == 0 over ~290 corpus programs (closes the
   runtime-called-only-from-emitted-`call` false-positive class; currently empty).

## NEXT (regenerate oracle first)
- **`tree.c`** (7 fns) — fully-dead candidate, UNTESTED for entanglement; apply the link gate.
- **`name_t` / `bb_boxes` / `interp_ref`** — ENTANGLED; need coordinated closure removal (excise their dead callers
  in name_save.c / emit_bb.c+rt.c / gen_runtime.c in the SAME commit) or remove the whole closure.
- **~560 partial-dead fns**, per-function excision by cluster: interpreter-era runtime (`rt_pat_*`, `resolve_*`,
  `rt_findall`/`rt_aggregate`/meta-interp), value-stack residue (`rt_push_*`/`rt_pop_*`/`rt_vstack_*`), Prolog
  GZ-cell arith, dead lex/yy accessor families, superseded `lower_<lang>` entries. Each: verify in
  `/tmp/dead_current.txt`, excise→attic w/ provenance, run the 3 proofs + gates, regenerate oracle, commit.
