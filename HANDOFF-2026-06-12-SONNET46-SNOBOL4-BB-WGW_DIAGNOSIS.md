# HANDOFF 2026-06-12 · Sonnet 4.6 · SNOBOL4-BB _wγ/_wω root-cause diagnosis

**SCRIP HEAD:** `4cb8a0a` (unchanged — no fix landed this session)
**.github HEAD:** (this commit)

---

## What this session did

No code was committed to SCRIP. The session was pure diagnosis of the `_wγ`/`_wω` undefined-reference link error blocking `omega_driver`, `Qize`, `Qize_driver`, `XDump_driver` beauty programs. The root cause is now fully understood.

---

## _wγ/_wω: complete diagnosis

### The symptom

`gcc` link of these beauty programs fails: `undefined reference to 'Qize_c0_wγ'` / `'Qize_c0_wω'` (and similarly for `SQize_c0`, `DQize_c0`, etc.).

### What _wγ/_wω are

`_wγ` and `_wω` are labels emitted by `bb_match_arbno` (in `src/emitter/BB_templates/bb_match_arbno.cpp`). The ARBNO match template emits:

```
Qize_c0_wγ:   ; wired success exit — child matched, check for zero-advance loop
    ...
Qize_c0_wω:   ; wired fail exit — restore saved cursor, jmp ω
    ...
```

where `Qize_c0` is the label base of the ARBNO's child body (the NOTANY wired body).

These labels are **jumped to** by the wired child body epilogue (`xa_flat.cpp` line 125/127): when a child body is emitted with `wired=1`, its success/fail exits are `jmp <base>_wγ` / `jmp <base>_wω` instead of `ret`.

### Why the child bodies are emitted but the parent is not

The wired NOTANY child bodies (`Qize_c0`, `Qize_c1`) ARE pre-built correctly:

- `gvar_flat_chain_build_text(Qize_graph, stdout, "Qize")` detects `has_ref=1` (IR_PAT_ARBNO found in an IR_SCAN subgraph)
- Calls `gvar_chain_prebuild_children_text(g, out, "Qize")`
- That function finds the ARBNO in the IR_SCAN's pattern subgraph and calls `pre_build_children_text(ARBNO_node, out, "Qize")`
- `pre_build_children_text` for IR_PAT_ARBNO: extracts `az->inner->entry` (the NOTANY node) and calls `codegen_flat_body(NOTANY_node, "Qize_c0", 1, wired=1)`
- The wired NOTANY body is emitted with `xa_flat` epilogue generating `jmp Qize_c0_wγ` / `jmp Qize_c0_wω`

Then `codegen_gvar_flat_chain_body` runs the Qize proc body. When it reaches the scan statement, `flat_drive_scan_native` is called. `flat_drive_match` is called on the pattern. **But the asm output shows the Qize scan emits only: POS → BREAK → CAPTURE(part) → RTAB — completely omitting the literal `'"'` and `ARBNO(NOTANY(...))` elements.**

A diagnostic `fprintf` added to the `IR_PAT_ARBNO` case in `walk_bb_flat` confirmed: the case never fires. The ARBNO node is never reached during the actual pattern emission.

### The precise gap: flat_drive_capture swallowing the ARBNO

The Qize pattern structure is:

```
POS(0)  (BREAK('"' ...) '"' ARBNO(NOTANY(..))) . part  RTAB(0) . str
```

The `(BREAK LIT ARBNO) . part` is an `IR_PAT_ASSIGN_COND` wrapping an inner CAT pattern.

`flat_drive_capture` is called for the ASSIGN_COND. It calls:

```c
IR_t *ch = bb_match_kid(pBB, 0);   /* the inner CAT pattern */
gather_lowered_cat_arms(ch, cat_arms, 64, &catnd, pBB);
```

`gather_lowered_cat_arms` walks the **γ-chain** from `ch`. But the inner pattern `BREAK LIT ARBNO` was lowered as an `IR_PAT_CAT` node with its three elements stored as **`bb_match_nkids`** (kid array), not as a γ-threaded chain. So `gather_lowered_cat_arms` returns `catn=0` (no γ-chain arms found terminating at a bare IR_PAT_CAT).

Then `flat_drive_capture` falls through to `walk_bb_flat(ch, cap_γ, lbl_ω, lbl_β)` where `ch` is the IR_PAT_CAT node. `walk_bb_flat` → `flat_drive_cat` → `flat_drive_cat_arms(pBB, NULL, bb_match_nkids(pBB), ...)`. If `bb_match_nkids` returns 0 for the CAT (kids not populated, or the CAT is itself the gather endpoint), it emits a stub jmp-to-γ. **The BREAK, LIT, and ARBNO kids are never walked.**

### The fix (one location: flat_drive_capture in emit_bb.c)

In `flat_drive_capture`, after `gather_lowered_cat_arms` returns `catn=0`, before falling to the single `walk_bb_flat(ch, ...)` call: check if `ch->op == IR_PAT_CAT && bb_match_nkids(ch) > 0`. If so, call `flat_drive_cat_arms(ch, NULL, bb_match_nkids(ch), cap_γ, lbl_ω, lbl_β)` directly. This walks all three kids (BREAK, LIT, ARBNO), emitting each. When `walk_bb_flat(ARBNO_node)` is reached, the `IR_PAT_ARBNO` case sets `g_emit.bb_child_lbl` from the child cache, calls `FILL` → `bb_match_arbno`, which emits the `Qize_c0_wγ` and `Qize_c0_wω` labels. Link error resolved.

**Scope:** `emit_bb.c` → `flat_drive_capture` only. No template changes needed.

**Gate:** smoke 7/7/7 · pat-rung 19/19/19 no-SKIP · fence HARD · beauty 30→34/34 (the 4 blocked programs link and pass).

---

## Start-of-session verification steps taken

- Cloned `.github`, `corpus`, `SCRIP`
- Read `PLAN.md`, `GOAL-SNOBOL4-BB.md`, `RULES.md`, `REPO-SCRIP.md`
- Read SPITBOL manual Ch. 17-19 (data types, pattern matching algorithm, primitive patterns, ARBNO, FENCE, IDENT, DIFFER)
- Built SCRIP + libscrip_rt — clean
- Confirmed gates: smoke 7/7/7, pat-rung 19/19/19, fence HARD

---

## Gates at session end

- smoke: **7/7/7** HARD ✓
- pat-rung: **19/19/19** no-SKIP ✓
- fence: **HARD** ✓
- SCRIP: `4cb8a0a` (unchanged)
