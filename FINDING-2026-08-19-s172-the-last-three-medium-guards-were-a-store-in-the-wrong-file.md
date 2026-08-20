# FINDING s172 (seat6, Opus 5) — the last three `MEDIUM_` guards were never three problems: they were ONE STORE LIVING IN THE WRONG FILE. Hoist it to where `g_medium` already lives, let the allocator answer NULL for TEXT, and the ratchet closes **3 → 0** with zero bytes moved in either medium

**Front:** queue row 10 `ab-cell-hoist` (seat1 GROUP-B follow-on; HQ-59 attached site `:427`). Closes the lane opened by `FINDING-2026-08-19-s170-the-29-medium-guards-were-five-classes-and-only-twelve-were-the-forbidden-shape.md` (seat1, rungs 1–4: 31 → 3).

**Build:** `make pristine` (RC=0, zero `error:`) at SCRIP `51b73ce9`, **RT_OPT `-O0`** (FACT RULE O0-DEV). Baseline arm = the same tree with the three files reverted to `2d436ea7`, also pristine. corpus `de42b605`, .github at this commit. Oracle `x64/bin/sbl` present and verified before any verdict (CLAUDE.md false-all-FAIL class).

⛔ **RE-PROVEN AFTER A REBASE.** The first full A/B ran at `aaf9d96b`; a `git pull --rebase` then landed `2d436ea7` (seat2's CN-EVAL-FAILS) under me. **Every number below was re-measured from scratch at the new base** — two more pristine builds, both arms — per RULES.md ("re-prove your goal's gate/watermark after a rebase"). Both A/Bs agree exactly, which is itself a datapoint: seat2's EVAL-failure semantics move none of these counts.

## 1. Why a FLOOR was not a floor

RULES.md had ruled the 3 survivors **"A RULED FLOOR, NOT DEBT"** — 2 gate C-side live-image state rather than output, plus `:427`, their emission twin. That ruling is correct about the *code* and wrong about the *conclusion*, and the difference is worth naming because it generalises.

The three sites are all in `bb_define.cpp` and all ask the same question:

| site (at `aaf9d96b`) | what it was | who reaches it |
|---|---|---|
| `:103` | `if (MEDIUM_BINARY) fn_cell_ptr = bb_ab_cell_addr(fname);` — allocate the activation block's cell | every DEFINE |
| `:488` | `if (MEDIUM_BINARY) { … *cell = bb_emit_buf + al->offset; }` — the post-block C-store that binds `fn_cell$<FN>` to the JIT address | every DEFINE |
| `:420` (HQ's `:427`) | `if (MEDIUM_BINARY) return …;` — the role-2 bind returns WITHOUT the three store instructions | `SCRIP_AB=1` only |

They are not three decisions. They are one fact asked three times: **does this image have a C-side cell at all?** In BINARY it does — `g_ab_fn_cells[]` is a live array in the compiling process. In TEXT it does not: the compile emits a `fn_cell$<FN>` `.data` quad and gas/ld resolves it at link time, so there is nothing to store into and nothing to store.

**The template had to ask the medium because the store lived inside the template.** `g_ab_fn_cells` and `bb_ab_cell_addr` were file-static in `bb_define.cpp`, so the allocator could not know the medium and the caller had to. That is the whole defect. ⭐ **The generalisable rule: when a template branches on the medium to ask about STATE rather than about an instruction, the cure is to move the state to where the medium already lives and let the accessor answer — never to duplicate the arm.**

## 2. The move

`AB_FNCELL_MAX` / `g_ab_fn_cells` / `g_ab_fn_cell_n` / `g_ab_fn_names` / `bb_ab_slot_for` / `bb_ab_cell_addr` / `bb_ab_fn_cell_ptr` were hoisted **verbatim** from `src/templates/bb_define.cpp` to `src/emitter/emit.cpp`, beside `drive_arg_slots_reserve` — the precedent whose own comment already names this move: *"promoted non-static for `bb_ab_emit_nodes` (bb_define.cpp) — the `bb_ab_fn_cell_ptr` precedent; ONE allocator authority, declared emit.h"*. `emit.cpp` owns `g_medium` (`:23`), which is exactly why it is the right home.

⛔ **NO NEW GLOBAL — THIS IS AN EXISTING-GLOBAL RELOCATION**, which is what the row's brief authorises ("Existing-global relocation, banner discipline"). The same three file-scope objects, the same `static` linkage, the same initialisers, one file over; the diff carries a matched `-`/`+` pair for each and the tree's file-scope count is unchanged. Nothing is created, exported, or widened. (FACT RULE NO-NEW-GLOBALS, Lon 2026-08-13.)

## 3. ⛔ ONE ALLOCATOR, **TWO FACES** — and the split is what preserves TEXT

The obvious implementation — one accessor that returns NULL in TEXT — is **wrong**, and this is the one thing a future seat must not undo:

- **`bb_ab_cell_addr(fname)` — the LIVE-IMAGE face. NULL in TEXT.** The honest answer to "does this image have a cell?". Consumed by the three retired sites.
- **`bb_ab_fn_cell_ptr(fname)` — the OPERAND face. Never NULL, BOTH MEDIA.** It hands out the cell's **address as an operand baked into emitted code**: `x86_jmp_via_cell` in `bb_call_proc_staged.cpp` (`:341/:358/:621/:640`) and `bb_goto_dyn.cpp`, the `body$<ENTRY>` operand in `bb_define.cpp`, and the seals in the m3 driver (`scrip.c:1682/1721/1814`) and `runtime_eval.c:249`. The slot exists in the **compiling** process whatever the medium, and TEXT renders the assembler symbol rather than the baked value.

Both go through the one allocator `bb_ab_slot_for`, so both name the same slot. **Collapsing them into a single NULL-in-TEXT accessor would bake `0` into every TEXT cross-chain jump.** That is why the guards could not simply be deleted, and why "the floor" looked like a floor.

Each site then became a test of the returned pointer — the shape seat1's rung 3 had already blessed at `bb_define:359` (*"`fn_cell_ptr` is assigned in the BINARY arm above and nowhere else"*). At `:488` the pointer is fetched **first** and `emit_label_intern` stays inside the guarded block, so TEXT interns nothing it did not intern before.

**`:420` is the interesting one and HQ-59 was right to attach it.** It is not state — it is emission: in BINARY those three instructions would write `0` over the address the post-block C-store already placed (`x86_load_ro` bakes a `movabs` immediate with no forward patch, the RTX-FUNC-0 defect); in TEXT they **are** that C-store's twin. The site now asks the allocator instead of the medium, which says the same thing and says it once — the same class the row calls "one class, one rung".

## 4. Receipts — pristine, both arms, re-measured after the rebase

| instrument | baseline (`2d436ea7`) | with the hoist (`51b73ce9`) | movers |
|---|---|---|---|
| mode-4 `.s` md5 (TEXT) | 527 comparable / 529 attempted | 527 comparable | **0** |
| mode-3 run-output md5 (BINARY) | 575 programs | 575 | **0** |
| `SCRIP_AB=1`, 11 DEFINE witnesses × 2 modes | — | — | **0** (output md5 and `.s` md5 alike) |
| corpus SNOBOL4 | m3 326/11 · m4 323/13 SKIP=1 | identical | **0**, and fail-sets identical **by name** |
| crosscheck SNOBOL4 | m3 308/9 · m4 306/10 SKIP=1 · DIVERGE=1 | identical | **0**, fail-sets identical by name |
| Icon smoke | 14/14 both modes | 14/14 | 0 |
| Prolog smoke | 3/5 both modes (recorded watermark) | 3/5 | 0 |
| RULES step-4 regen (independent second path) | — | benchmark/feature/demo/programs/prolog-bench all `changed=0`; 623 + 22 programs emitted | **0 bytes** |

**`SCRIP_AB=1` is not optional diligence — it is the only arm that reaches `:420` at all** (`SCRIP_AB` defaults OFF, and `bb_define_bind` returns before that line when it is off). Without it the third site would have shipped unmeasured.

⛔ **The `util_out_sweep` flaky row did not fire this session, and that was checked, not assumed.** seat1's rung-3 FINDING warns that `141_pat_eval_double_fn_arbno` oscillates `RUN_RC_139` ↔ md5 and manufactures a false mover in either direction. The control arm was swept **twice before any patch existed**: self-diff **0 rows**. A single-mover result would otherwise have been unreadable.

**DIVERGE=1 (`141_pat_eval_double_fn_arbno`) is unchanged and is not this rung's**: it is the standing named breach carried by queue row 13, from B1c residue R1's wall 2.

## 5. The gate is now an invariant, not a ratchet

`scripts/test_gate_template_medium_invisible.sh` ceiling lowered **3 → 0**, and the comment records why so the next seat cannot read the zero as an accident. **Negative-tested by injection**, the discipline seat1 established: one `MEDIUM_TEXT` token appended to `bb_fail.cpp` → `rc=1` with `RATCHET FAIL: 1 … > ceiling 0`; reverted → `rc=0`. A ceiling of 0 that has never been seen to fail is not a gate.

RULES.md's `NO MEDIUM_* IN TEMPLATES` paragraph is updated in the same commit: the ledger now ends at zero, and it carries the two-faces warning above so the split is not "simplified" back into one accessor by a later cleanup.

## 6. What this closes and what it does not

**Closes:** the `medium-retire` lane entirely — 31 → 0 across five rungs (seat1 ×4, seat6 ×1). `bb_*.cpp` no longer names a medium anywhere.

**Does NOT close, and is the honest residue:** the gate's *other* half — the raw-byte/medium-branch producer count — still reports **8, all in `src/templates/xa_flat.cpp`**. `xa_flat.cpp` is not a `bb_*.cpp` and was never inside this ratchet's scope, so nothing here regressed; it is simply the next census if HQ wants the whole `src/templates/` tree medium-invisible rather than just the boxes. **It is a different file, a different shape (raw-byte producers, not `MEDIUM_*` guards), and it wants its own row** — naming it here so the zero above is not misread as "all of `src/templates/` is clean".
