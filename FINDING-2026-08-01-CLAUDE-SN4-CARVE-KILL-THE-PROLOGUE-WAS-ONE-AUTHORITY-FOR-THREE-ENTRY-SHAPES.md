# FINDING 2026-08-01 — SN4 CARVE-KILL: THE PROLOGUE EMITTER WAS ONE AUTHORITY FOR THREE ENTRY SHAPES, AND DELETING IT TOOK THE COMPLIANT ONE WITH THE CORPSE

**Session:** s22n (Claude) · **EMERGENCY HANDOFF — CORPUS IS RED BY DESIGN, NOT BY ACCIDENT**
**SCRIP:** `983f24d3` (deletion) + `ba46bb5e` (dead-helper sweep), from `f143fd48`. All builds `-O0`.
**Directive:** Lon — *"Whatever code in SCRIP is generating that, DELETE IT NOW … Accept whatever breaks."* Restated when the first cut was too narrow: *"I want the ENTIRE function … deleted."* Then: *"We except that something will break. Perform emergency hand off."*

---

## 0 ⛔ STATE — READ FIRST

**The corpus is RED and that is the authorized outcome, not a regression to hunt.**

| runner | before (`f143fd48`) | after (`ba46bb5e`) |
|---|---|---|
| crosscheck m3 (317) | 276/41 | **77/240** |
| crosscheck m4 | 276/40 | **5/311/1** |
| DIVERGE | 3 | **72** |

Revert is one command: `git revert ba46bb5e 983f24d3`. Do not "fix" this by chasing individual reds.

---

## 1 WHAT WAS DELETED

The whole emission authority, not a guarded branch. 247 + 42 lines:

| symbol | file | note |
|---|---|---|
| `xa_flat_prologue_str()` | `src/templates/xa_flat.cpp` | 231 lines, BOTH mediums |
| `xa_flat_prologue()` | `src/templates/xa_flat.cpp` | the `extern "C"` wrapper |
| declaration | `src/templates/xa_templates.h` | |
| `case XA_FLAT_PROLOGUE:` | `src/emitter/emit.cpp:320` | dispatch |
| `xa_dispatch(XA_FLAT_PROLOGUE)` | `src/emitter/emit.cpp:2061` | call site → tombstone comment |
| `XA_FLAT_PROLOGUE` | `src/include/XA.h:15` | enum member |
| 19 `xaf_*` helpers | `src/templates/xa_flat.cpp` | orphaned; swept to fixpoint |

`grep -rn "xa_flat_prologue\|XA_FLAT_PROLOGUE" src/` → zero. `xa_flat.cpp` 821 → 532 lines.

**Proof at HEAD:** `proc_LBL__ROMAN_α:` now falls DIRECTLY into `proc_LBL__ROMAN_α_body:` with zero instructions between. `sub rsp, 1344` 2→0 · `rep stosb` 0 · `mov rbp, rsp` 0. The 36 residual `sub rsp` in roman.s are per-BB ζ self-allocations from other templates — the model, not the carve.

---

## 2 ⭐⭐⭐ THE FINDING: ONE FUNCTION, THREE ENTRY SHAPES, ONLY ONE OF THEM THE CORPSE

The collapse is total (m4 → 5/317) rather than graceful, and the reason is structural, not incidental. `xa_flat_prologue_str` was the SINGLE authority for **every** graph entry shape. Three lived in one body:

1. **The jmp-entry carve** — `sub rsp, K` + rcx/rdx wire header + `emit_jmp_pin_rbp` + NOFILL/EAGER zero-fill. **This is the roman anti-pattern named in the design of record, and the only one anybody wanted dead.**
2. **`GEN_RESUMABLE`** — the heap-frame adopt (`rt_proc_call_gen_h` → box adopts fb as rbp base) for generators / resumable procs, whose frame must survive β-resume.
3. **`STMT_FRAME`** — the arm that carves **nothing** but an 8-byte parity pad, no region, no stosb, no anchor, no rbp touch. **That is the s21x-c design-of-record per-BB shape — the thing the whole ζ ladder has been building toward.**

Deleting the function necessarily deleted (3) alongside (1). Every graph lost its entry protocol, including the graphs already doing it the right way. **A decline count is not a backlog and a red count here is not a debt census** — 311 m4 reds is one missing authority, not 311 problems.

⭐ **CONSEQUENCE FOR THE RE-LAND:** the correct shape is NOT `git revert`. It is re-landing **`STMT_FRAME` alone, as its own function**, with the carve arms never coming back. The three arms were always separable; nothing but co-tenancy in one `if/else` chain ever joined them. That separation is now the head rung.

---

## 3 ⚠ MEASUREMENT TAKEN BEFORE THE CUT (kept — it is the reason the collapse was predictable)

The carve was **not** dead code for SNOBOL4, unlike Prolog (`FINDING-2026-07-31j`, 2,642 pairs no instruction addresses). In the ROMAN blob alone at cut time:

- **93** `[rsp+N]` refs into the carve region, 46 distinct offsets (0…664, 1296, 1304)
- **57** `[rbp+N]` refs, 26 distinct offsets, incl. `[rbp+1320]`/`[rbp+1336]` — the wires the prologue itself wrote

With no carve, rsp/rbp keep the caller's values, so those 150 instructions read and write the **caller's live frame**. The failure mode is silent corruption, not a clean fault. `zeta_storage.c:730` had already recorded roman among the five pattern programs a blanket suppression breaks (with `mixed_workload`, `pattern_bt`, `pattern_bt_deep`, `string_pattern`).

---

## 4 HOUSEKEEPING

- **NO FILE BECAME EMPTY OR UNUSED.** Verified across all tracked files: zero empty, zero comment-only as a result of this rung. The ~800 empty files under `baselines/per_kind/**` are **pre-existing** placeholders for the dormant jvm/net/js/wasm backends — not this rung's debris, not touched.
- **Artifacts under `corpus/` are STALE** against this HEAD. No regen run: regenerating would commit a corpus-wide diff of broken output over a known-red tree.
- ⚠ **INSTRUMENT NOTE:** the first helper sweep used `sed` line patterns and cut the opening line of multi-line definitions, leaving orphaned bodies and a broken build (restored from HEAD, redone by brace-matching). **Delete C functions by brace-matching, never by line regex.**
- ⚠ **CONCURRENCY:** `RULES.md` records 3–4 parallel sessions, and `FINDING-2026-07-31j` proves a parallel writer shares this container's clones. This HEAD is red corpus-wide; any parallel session rebasing onto it inherits that. Flagged, not resolved.

---

## 5 NEXT — ORDERED

1. ⭐⭐⭐ **`STMT_FRAME` RE-LAND AS ITS OWN FUNCTION** (§2). Not a revert. The 8B parity-pad arm, standing alone, carve arms gone for good.
2. ⭐⭐ **`GEN_RESUMABLE` re-land**, same treatment — generators need the heap-fb adopt or β-resume has no surviving frame.
3. Re-measure the watermark after each; expect the reds to fall in large blocks, not singly.
4. Inherited from s22m, untouched this session: TREEBANK H11 `Pop_list` RSP imbalance (gdb available) · FAMILY A `bb_call_proc_staged` ZD arm · `151` · CARVE-ERAD steps 2–3 (step 1's readers are now moot for jmp-entry) · NOFC per-kind bisect.
