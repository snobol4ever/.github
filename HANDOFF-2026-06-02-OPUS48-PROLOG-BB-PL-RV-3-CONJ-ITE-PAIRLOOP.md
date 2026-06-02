# HANDOFF — Prolog BB · PL-RV-3 · bb_conj + bb_ite → x86() via shared `x86_pair_loop()`

**Date:** 2026-06-02 · **Model:** Opus 4.8 · **Area:** GOAL-PROLOG-BB, x86() TEMPLATE-REVAMP
**Status:** ✅ LANDED + pushed + gate-verified (incl. re-verify atop sibling rebase)

## Verified HEADs (both on `origin/main`)
- **SCRIP:** `acea982` — "PL-RV-3: bb_conj + bb_ite onto x86() via shared x86_pair_loop() combinator"
- **.github:** `80613ca7` — "GOAL-PROLOG-BB + REVAMP-RULES: record PL-RV-3 …" (this handoff doc adds one more commit on top)

---

## What landed

Converted the two Prolog **combinator** templates to the `x86()` self-encoding API, and in doing so designed +
landed the formerly-**STILL-OPEN** variable-length define/jmp-pair loop as a **shared primitive** so all four
languages can stop hand-rolling it:

- `src/emitter/BB_templates/bb_conj.cpp` (IR_GCONJ) — now `return x86_pair_loop();`, pBB-free, `(void)` sig.
- `src/emitter/BB_templates/bb_ite.cpp` (IR_ITE) — `return IF(MEDIUM_TEXT, s_comment(…β-tombstone…)) + x86_pair_loop();`, pBB-free, `(void)`.
- `src/emitter/BB_templates/x86_asm.h` (additive +~28L) — **`inline std::string x86_pair_loop()`** + two new
  `bb_emit_x86` records.
- `bb_templates.h` (protos → `(void)`), `emit_core.c` (dispatch `bb_conj()`/`bb_ite()`).

### The `x86_pair_loop()` design (record it; it's the cross-language combinator idiom)
A combinator box does **not** own its glue labels — the driver (`flat_drive_pl_seq`/`flat_drive_pl_ite` for
Prolog; the cat/alt sub-region walkers for SNOBOL4) mints externally-owned `bb_label_t*` into
`g_emit.xa_bb_emit_pair_{n,define,jmp}[0..n)`. Each pair OPTIONALLY defines a label at its point and OPTIONALLY
emits `jmp` to one (def-only / jmp-only / def+jmp all occur). This is the variable-length analogue of
`x86_jmp`/`x86_deflabel`: instead of baking a FIXED port/internal id into the record, the record carries the
**PAIR INDEX** and the walker fetches the pointer out of `g_emit` by index — **so no raw pointer rides in the
1-byte-id record stream** (the whole point — keeps the record stream pointer-free).

Two new walker records (BINARY only; TEXT is passthrough GAS):
- **`'E' <idx>`** → `bb_label_define(g_emit.xa_bb_emit_pair_define[idx])` here, 0 bytes (if non-null).
- **`'F' <idx>`** → `bb_emit_patch_rel32(g_emit.xa_bb_emit_pair_jmp[idx])` (if non-null); the **preceding `'L'`
  carries the `E9`**, exactly like `'J'`. (`bb_emit_patch_rel32` emits the 4 placeholder bytes AND registers the
  patch, mirroring the existing `'J'` handler.)

TEXT emits the identical GAS the four boxes hand-rolled: `emit_fmt("%s:\n", name)` (= `LABEL:\n`) and
`s_1asm(emit_fmt("jmp %s", name))` (= `" jmp LABEL\n"`). **Net result: byte-identical in BOTH media** to the
loop it replaces — this conversion is byte-preserving, not just behavior-preserving.

### Cross-language reach (verified)
SNOBOL4 `bb_pat_cat`/`bb_pat_alt` carry the **byte-identical** `xa_bb_emit_pair_*` loop (confirmed by reading
both). They adopt `x86_pair_loop()` verbatim when they convert (same `g_emit` fields) — **no further shared
design needed**. `bb_disj`/`bb_catch` use a DIFFERENT structure (0 `xa_bb_emit_pair` refs), so they are NOT
pair-loop boxes. Recorded as RESOLVED in `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (vocabulary + divvy-up ledger
updated; the old "STILL OPEN — VARIABLE-LENGTH define/jmp-pair loop" section is gone).

---

## Gate status (all green; ran twice — once on my tree, once after the rebase pulled a sibling's work)
- **GATE-1** Prolog smoke: **5/5/5** (m2/m3/m4).
- **GATE-3** rung suite: m2 **111/111**, m3 **111/111**, m4 **86 PASS / 0 FAIL / 25 EXCISED** — **unchanged** (byte-identical conversion, as predicted).
- FACT greps: `g_vstack`=0, `seg_byte(SEG_CODE`/`SL_B` outside templates=0. `test_gate_pl_no_value_stack.sh` PASS.
- `b.size()` ledger **116 → 112** (bb_ite 2 + bb_conj 2 gone), 20 → 18 files. Template-purity 8 baseline (neither box flagged). No duplicated `IR_` case.
- **Siblings neutral:** Icon **12/12/12**; SNOBOL4 **12 PASS / 7 FAIL** (pre-existing baseline). My `x86_asm.h` edits are purely additive.

---

## ⚠️ Concurrency note (active sibling session on the SAME revamp)
While I worked, a sibling pushed SCRIP `2ac3fcd` (`bb_succeed` → x86()) and `c66bbc8` (`bb_pat_fence` +
`bb_pat_break` → x86()), touching `bb_templates.h` + `emit_core.c` (different lines than mine). My `git pull
--rebase` merged cleanly; I then **rebuilt and re-ran the full gate on the merged tree** (all green above) before
pushing. The `.github` rebase pulled sibling edits to `GOAL-ICON-BB.md`/`GOAL-SNOBOL4-BB.md` only (no overlap).
**Takeaway for next session:** keep `x86_asm.h` edits ADDITIVE, `pull --rebase` before push, and re-gate after any
rebase that touches shared files — a clean textual rebase is not proof of a clean build.

---

## NEXT — `bb_unify`, but it is gated on PL-HY-1a (the #0 hygiene priority)
`bb_unify` is the last single-`b.size()` Prolog box, BUT it is **live** (no dead-box shortcut) and its general
arm calls the twin walkers `emit_build_compound_term` / `emit_build_compound_term_bin` (in `bb_builtin.cpp`),
which dereference node neighbors — a direct FACT-RULE violation. So a clean conversion is correctly **coupled to
PL-HY-1a**: delete both walkers in favor of a runtime substrate, THEN convert the consumer.

**Empirical finding this session (do not re-discover):** I surveyed all 132 rungs in mode-4. **47/132 emit
`rt_pl_compound_build_n`** (compound-unify is real), and **some single `IR_UNIFY` regions build 3–5 compounds —
i.e. NESTED compounds occur in unify position.** Therefore a bounded/non-recursive builder is insufficient: the
PL-HY-1a substrate **must handle arbitrary depth**. The hard part is **mode-4**: the IR graph is dead in the
standalone binary, so the emit-time walker currently IS the serialization mechanism. A clean replacement most
likely serializes the operand subtree **driver-side** (in `bb_prepare_pl` or a pre-pass) into an RO flat array,
interns it, promotes the pointer into `_`, and the template arm becomes a single `call
rt_pl_build_term_serialized(_.ptr)` (pBB-free). The runtime walks the flat array. This is a genuine multi-file
rung — **give it its own fresh context**; do not bolt it onto a small session.

### Cheaper, completable revamp boxes if you want a safe win first (NOT pair-loop, NOT walker-coupled)
- `bb_disj.cpp` — 2 `b.size()`, 0 walker, 0 pBB-deref, but it is NOT an `xa_bb_emit_pair_*` box (own structure); inspect its shape and convert with the existing `x86()` / internal-label primitives.
- `bb_catch.cpp` — 1 `b.size()`, 0 walker, **2 pBB-derefs** → promote those two scalars into `_` (driver-side in `bb_prepare_pl`, à la `bb_arith`) FIRST, then convert.
- Larger/looping (each its own rung): `bb_choice`(6), `bb_goal`(13), `bb_builtin`(28).

### Free wins for the SNOBOL4 session
`bb_pat_cat`/`bb_pat_alt` → `… + x86_pair_loop();` (byte-identical; the primitive already exists and reads the same `g_emit` fields). Plus the loop-free SNOBOL4 remainder noted in the RULES-DRAFT divvy-up ledger.

---

## Reproduce (build + gate)
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh    # nasm/m4/libgc
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh           # GATE-1 (5/5/5)
bash scripts/test_prolog_rung_suite.sh      # GATE-3 (m2/m3 111/111, m4 86/0/25)
# single mode-4 file: bash scripts/run_prolog_via_x86_backend.sh <file.pl>
# FACT greps:
grep -rn 'g_vstack' src/ | wc -l                                          # 0
bash scripts/test_gate_pl_no_value_stack.sh                               # PASS
bash scripts/test_gate_no_handencoded_bytes.sh | grep 'BAD sites'         # 112 across 18 files
# siblings (must stay neutral):
bash scripts/test_smoke_icon.sh             # 12/12/12
bash scripts/test_smoke_snobol4.sh          # 12 PASS / 7 FAIL (baseline)
```
Refs (gitignored symlinks; restore if needed): `refs/gprolog`→gprolog-master, `refs/swipl`→swipl-devel-master.

## Commit identity / credential
`git config user.name "LCherryholmes"` · `user.email "lcherryh@yahoo.com"`.
Push token: the `ghp_…` PAT used throughout the session (NOT embedded here — GitHub push-protection blocks
literal PATs; it's supplied in the working context / ask Lon). Remote URL form
`https://<TOKEN>@github.com/snobol4ever/<repo>.git`. Push order: code repos first, `.github` last.
