# GRAND_MASTER_REORG_2.md — Grand Master Reorganization, Second Attempt
*2026-03-31 — authored by Claude Sonnet 4.6 (G-10 session)*

---

## Why a second reorg

G-1 through G-9 stalled mid-stream. The folder restructure (Phase 2) landed and
the unified IR header exists, but:

1. **Naming law never applied.** Zero Greek-letter usage found across all 10
   emitter files. The 9-class similarity pass (Phase 3) was never executed.
2. **Folder structure is partially done.** Emitters are flat in `src/backend/`
   — not in `x64/`, `jvm/`, `net/`, `wasm/` subdirs. Frontend files exist under
   `src/frontend/` correctly. The `backend/` split never happened.
3. **ir_emit_common.c is nearly empty.** Only `ir_nary_right_fold` was extracted
   (99 lines). None of the Phase 4 shared Byrd box wiring was done.
4. **Emitter dev continued in parallel through G-1–G-9.** The 11 surviving
   emitter files total ~41,600 lines. New frontends (Snocone, WASM ×3) were
   added without naming law compliance. Duplication compounded.
5. **The naming freeze was never called before a naming pass**, per the rule
   you've now stated. The freeze/name/unfreeze cycle must be respected this time.

The clean solution: **scrap the old plan, do it right.**

---

## What "right" means this time

1. **All emitter dev finishes first.** Every session completes its current
   milestone before the freeze is called. No emitter is touched during reorg.
2. **Freeze is called once, respected by all sessions.**
3. **Consolidation happens before naming.** Duplicated code across the 11
   emitters is extracted into `ir_emit_common.c` (or backend-pair shared files)
   before any rename pass. You cannot rename consistently across files that still
   have duplicated logic — you'll rename in one place and miss it in another.
4. **Naming pass happens under freeze, one file at a time, with gate after each.**
5. **Unfreeze.** New pipelines open.

---

## Current emitter inventory (G-10 baseline)

| File | Lines | Frontend(s) | Backend |
|------|-------|-------------|---------|
| `emit_jvm_prolog.c` | 9,972 | Prolog | JVM |
| `emit_jvm_icon.c` | 8,361 | Icon | JVM |
| `emit_x64.c` | 5,404 | SNOBOL4, Snocone | x86 |
| `emit_jvm.c` | 4,953 | SNOBOL4 | JVM |
| `emit_net.c` | 2,841 | SNOBOL4 | .NET |
| `emit_x64_icon.c` | 2,782 | Icon | x86 |
| `emit_x64_prolog.c` | 1,931 | Prolog | x86 |
| `emit_wasm.c` | 1,575 | SNOBOL4 | WASM |
| `emit_wasm_prolog.c` | 1,399 | Prolog | WASM |
| `emit_wasm_icon.c` | 1,372 | Icon | WASM |
| `emit_x64_snocone.c` | 1,056 | Snocone | x86 |
| `ir_emit_common.c` | 99 | — | shared |
| **Total** | **41,745** | | |

---

## Milestones

### Phase 0 — All Emitter Dev Complete (prerequisite to everything)

The freeze cannot be called until every active session has landed its current
milestone. G-10 tracks completion, does not do the work.

| ID | Session | Current milestone | Status |
|----|---------|------------------|--------|
| **M-G10-DONE-IX** | Icon x86 (IX-18) | rung10–35 | 🔲 |
| **M-G10-DONE-IW** | Icon WASM (IW-9) | M-IW-R01 activation frame stack | 🔲 |
| **M-G10-DONE-IJ** | Icon JVM (IJ-58) | per SESSION-icon-jvm.md | 🔲 |
| **M-G10-DONE-PW** | Prolog WASM (PW-14) | M-PW-B01 env-slot aliasing fix | 🔲 |
| **M-G10-DONE-PJ** | Prolog JVM (PJ-84a) | per SESSION-prolog-jvm.md | 🔲 |
| **M-G10-DONE-PX** | Prolog x86 (PX-1) | per SESSION-prolog-x64.md | 🔲 |
| **M-G10-DONE-SC** | Snocone x86 (SC-5) | M-SC-B05 alternation | 🔲 |
| **M-G10-DONE-SW** | SNOBOL4 WASM (SW-12) | M-SW-C02 is_idxassign + ARRAY/TABLE | 🔲 |
| **M-G10-DONE-SD** | Scrip Demo (SD-37) | per SCRIP_DEMOS.md | 🔲 |
| **M-G10-DONE-B** | TINY backend (B-292) | per SESSION-tiny.md | 🔲 |
| **M-G10-DONE-J** | TINY JVM (J-216) | per SESSION-tiny.md | 🔲 |
| **M-G10-DONE-N** | TINY NET (N-253) | per SESSION-tiny.md | 🔲 |
| **M-G10-DONE-D** | DOTNET (D-164) | per SESSION-dotnet.md | 🔲 |

**Gate:** All rows ✅ before Phase 1 begins. G-10 calls freeze.

---

### Phase 1 — Freeze

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-FREEZE** | G-10 announces freeze in PLAN.md NOW table. All sessions acknowledge — no emitter file is touched until M-G10-UNFREEZE. | PLAN.md updated; all session leads confirm |

---

### Phase 2 — Consolidation Audit

Identify all duplicated logic across the 11 emitter files before touching anything.
Produce a written inventory. No code changes in this phase.

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-AUDIT-SNO** | Diff SNOBOL4 handling across `emit_x64.c`, `emit_jvm.c`, `emit_net.c`, `emit_wasm.c`. List every function body that is structurally identical modulo output macro letter. | `doc/CONSOLIDATION-sno.md` exists |
| **M-G10-AUDIT-ICON** | Same for Icon: `emit_x64_icon.c`, `emit_jvm_icon.c`, `emit_wasm_icon.c`. | `doc/CONSOLIDATION-icon.md` exists |
| **M-G10-AUDIT-PROLOG** | Same for Prolog: `emit_x64_prolog.c`, `emit_jvm_prolog.c`, `emit_wasm_prolog.c`. | `doc/CONSOLIDATION-prolog.md` exists |
| **M-G10-AUDIT-CROSS** | Identify logic duplicated *across* frontend groups (e.g. strlit interning, data segment emission, Byrd box wiring skeletons). | `doc/CONSOLIDATION-cross.md` exists |

---

### Phase 3 — Consolidation (extract before rename)

For each item in the audit docs, extract the shared logic into `ir_emit_common.c`
or a backend-pair shared file. One milestone per extraction unit. Gate after each:
full invariant suite must hold.

| ID | Shared unit | Destination | Verify |
|----|-------------|-------------|--------|
| **M-G10-CON-STRLIT** | String literal interning (`strlit_intern/abs/len/count/reset`) — duplicated across WASM emitters | `emit_wasm.c` shared (already partially done) | 981/4 ✅; all WASM invariants hold |
| **M-G10-CON-DATA-SEG** | `emit_data_segment` / `emit_blk_reloc_tables` — appears in x64 + JVM | `ir_emit_common.c` or backend header | 981/4 ✅; x86+JVM invariants hold |
| **M-G10-CON-SNO-BYRD** | SNOBOL4 Byrd box wiring (E_CONCAT, E_OR, E_SEQ, E_ARBNO) — structural skeleton identical across x64/JVM/NET/WASM | `ir_emit_common.c` with `emit_fn_t` callback | 981/4 ✅; all 4 SNOBOL4 backends hold |
| **M-G10-CON-ICON-BYRD** | Icon generator wiring (E_TO, E_TO_BY, E_SUSPEND, E_ALT_GEN, E_ITER, E_LIMIT) — x64 vs JVM vs WASM | `ir_emit_common.c` | 981/4 ✅; all 3 Icon backends hold |
| **M-G10-CON-PROLOG-BYRD** | Prolog unification/clause/cut/trail wiring — x64 vs JVM vs WASM | `ir_emit_common.c` | 981/4 ✅; all 3 Prolog backends hold |
| **M-G10-CON-GLOBALS** | Global state structs (`out`, `nvar`, `vars`, `cur_fn`, `uid_ctr`) — all emitters have private copies of the same concept | Shared header with typed accessors | 981/4 ✅; all invariants hold |
| **M-G10-CON-VERIFY** | Final: run full invariant suite. Confirm line counts reduced. Document new `ir_emit_common.c` size and what was extracted. | Suite PASS; `doc/CONSOLIDATION-result.md` |

---

### Phase 4 — Folder Restructure

Mechanical moves only. No logic changes. One move per milestone.

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-DIRS** | Create `src/backend/x64/`, `src/backend/jvm/`, `src/backend/net/`, `src/backend/wasm/` | Dirs exist; Makefile still builds |
| **M-G10-MOVE-X64** | Move `emit_x64.c`, `emit_x64_icon.c`, `emit_x64_prolog.c`, `emit_x64_snocone.c` → `src/backend/x64/` | x86 invariants hold |
| **M-G10-MOVE-JVM** | Move `emit_jvm.c`, `emit_jvm_icon.c`, `emit_jvm_prolog.c` → `src/backend/jvm/` | JVM invariants hold |
| **M-G10-MOVE-NET** | Move `emit_net.c` → `src/backend/net/` | .NET invariants hold |
| **M-G10-MOVE-WASM** | Move `emit_wasm.c`, `emit_wasm_icon.c`, `emit_wasm_prolog.c` → `src/backend/wasm/` | WASM invariants hold |
| **M-G10-MOVE-VERIFY** | Full suite. Confirm folder layout matches target architecture exactly. | 981/4 ✅; all invariants hold |

---

### Phase 5 — Naming Pass (under freeze, one file at a time)

**Prerequisite:** M-G10-FREEZE must be active. Do not begin any naming pass
until consolidation and folder moves are complete and verified.

Each sub-milestone is a **full 9-class similarity pass** on one file per
`ARCH-reorg-design.md §THE LAW`. Greek letters replace all ASCII spellings.
Label schemes unify. Prefix/suffix conventions normalize.

Gate after each: full invariant suite for that backend must hold before the
next file is touched.

| ID | File | Lines | Key changes | Verify |
|----|------|-------|-------------|--------|
| **M-G10-NAME-X64** | `emit_x64.c` | 5,404 | α/β/γ/ω ports; `sno_<id>_α` labels; `out`/`nvar`/`uid_ctr` roots | x86 SNOBOL4 106/106 |
| **M-G10-NAME-JVM** | `emit_jvm.c` | 4,953 | Same. `J` macro letter. | JVM SNOBOL4 holds |
| **M-G10-NAME-NET** | `emit_net.c` | 2,841 | Same. `N` macro letter. | .NET holds |
| **M-G10-NAME-WASM** | `emit_wasm.c` | 1,575 | Same. `W` macro letter. | WASM SNOBOL4 holds |
| **M-G10-NAME-X64-ICON** | `emit_x64_icon.c` | 2,782 | `icn_<id>_α` labels; Icon-specific naming | Icon x86 holds |
| **M-G10-NAME-JVM-ICON** | `emit_jvm_icon.c` | 8,361 | Same naming law, JVM output | Icon JVM holds |
| **M-G10-NAME-WASM-ICON** | `emit_wasm_icon.c` | 1,372 | Same | Icon WASM holds |
| **M-G10-NAME-X64-PROLOG** | `emit_x64_prolog.c` | 1,931 | `pl_<id>_α` labels; Prolog-specific naming | Prolog x86 holds |
| **M-G10-NAME-JVM-PROLOG** | `emit_jvm_prolog.c` | 9,972 | Same naming law, JVM output | Prolog JVM holds |
| **M-G10-NAME-WASM-PROLOG** | `emit_wasm_prolog.c` | 1,399 | Same | Prolog WASM holds |
| **M-G10-NAME-X64-SNOCONE** | `emit_x64_snocone.c` | 1,056 | Snocone-specific; `sno_` prefix where applicable | Snocone x86 holds |
| **M-G10-NAME-COMMON** | `ir_emit_common.c` | TBD post-consolidation | Law applied from first write; verify no violations crept in | All invariants hold |
| **M-G10-NAME-VERIFY** | Cross-file diff audit. Confirm: diff of any two same-concept emitters shows only output macro letter + platform-specific sequences, nothing else. | Diff audit doc in `.github/` |

---

### Phase 6 — Unfreeze

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-UNFREEZE** | Remove freeze notice from PLAN.md. All sessions resume. Full invariant suite run. | Suite PASS; all sessions notified |

---

### Phase 7 — New Pipelines (post-unfreeze, parallel)

With clean shared IR and law-conformant emitters, new frontend×backend pipelines
are cheap. Each is a separate session.

| ID | Pipeline | Prerequisite | Verify |
|----|----------|-------------|--------|
| **M-G10-ICON-NET** | Icon → .NET | M-G10-UNFREEZE | Icon .NET rung01 PASS |
| **M-G10-PROLOG-NET** | Prolog → .NET | M-G10-UNFREEZE | Prolog .NET rung01 PASS |
| **M-G10-SNOCONE-JVM** | Snocone → JVM | M-G10-UNFREEZE | Snocone JVM corpus PASS |
| **M-G10-SNOCONE-NET** | Snocone → .NET | M-G10-UNFREEZE | Snocone .NET corpus PASS |
| **M-G10-SNOCONE-WASM** | Snocone → WASM | M-G10-UNFREEZE | Snocone WASM rung01 PASS |

---

### Phase 8 — Style Pass

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-STYLE-DOC** | Write `doc/STYLE.md` — one style document for all `src/` files | Doc exists |
| **M-G10-STYLE-PASS** | Apply style to all files in `src/` — no logic changes | Full suite PASS |

---

### Phase 9 — Repo Rename

After unfreeze. Administrative only.

| ID | Action | Verify |
|----|--------|--------|
| **M-G10-RENAME-PLAN** | Audit all cross-repo refs to `snobol4dotnet` | Checklist in `.github/` |
| **M-G10-RENAME-EXEC** | Rename GitHub repo → `snobol4net` | `git ls-remote` resolves |
| **M-G10-RENAME-REFS** | Update all references in `.github`, `one4all`, `harness` | No broken refs |

---

## Dependency Graph

```
Phase 0: All emitter dev done (M-G10-DONE-*)
    └── Phase 1: FREEZE (M-G10-FREEZE)
            └── Phase 2: Consolidation Audit (M-G10-AUDIT-*)
                    └── Phase 3: Consolidation / extraction (M-G10-CON-*)
                            └── Phase 4: Folder restructure (M-G10-DIRS → MOVE-* → VERIFY)
                                    └── Phase 5: Naming pass (M-G10-NAME-*, sequential, one file at a time)
                                            └── Phase 6: UNFREEZE (M-G10-UNFREEZE)
                                                    ├── Phase 7: New pipelines (parallel)
                                                    ├── Phase 8: Style pass
                                                    └── Phase 9: Repo rename
```

---

## Success Criteria

The reorg is complete (M-G10-UNFREEZE fires) when:

1. `src/backend/` has four subdirs: `x64/`, `jvm/`, `net/`, `wasm/`. All emitters
   are in the correct subdir.
2. `ir_emit_common.c` contains all shared Byrd box wiring. No wiring logic is
   duplicated across emitter files.
3. Every emitter file passes the diff test: diffing two same-concept files shows
   only output macro letter and platform-specific sequences — no naming drift.
4. Greek letters (α β γ ω) are used everywhere ports are named — parameters,
   locals, labels, comments. Zero ASCII spellings.
5. Every corpus test that passed before the freeze still passes after unfreeze.
6. `doc/STYLE.md` exists and all source files conform.

---

## Rules for this attempt

1. **No naming pass without freeze.** If the freeze is not active, no file in
   `src/backend/` or `src/ir/` has its names changed.
2. **Consolidation before naming.** Extract first. Rename second. Never both
   in the same commit.
3. **One file per naming milestone.** Gate (full invariant suite for that
   backend) before touching the next file.
4. **Emitter dev is done before freeze.** If a session needs to push a fix
   during the freeze, it goes through G-10 for review. The default answer is no.
5. **G-10 owns the freeze/unfreeze signal.** No other session calls either.

---

*GRAND_MASTER_REORG_2.md — living document.*
*Supersedes GRAND_MASTER_REORG.md for active tracking.*
*Old doc retained in git history; move to MILESTONE_ARCHIVE.md at M-G10-UNFREEZE.*
