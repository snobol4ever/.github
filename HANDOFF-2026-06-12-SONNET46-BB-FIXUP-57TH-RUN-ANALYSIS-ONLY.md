# HANDOFF — BB-FIXUP 57th Attended Run
**Date:** 2026-06-12  **Model:** Sonnet 4.6  **Goal:** GOAL-BB-FIXUP-Z-to-A.md

---

## What happened this session

Orientation + deep analysis of cursor file `bb_gvar_assign.cpp`. No commits to SCRIP. Law-7 context stop at ~75%.

### Session open state
- SCRIP @ `a1a2191` (no change)
- GRAND = 2014 (125 files / 108 dirty / 17 clean) — reduced from 2075 at 56th close by concurrent commits

### Ring stop: bb_gvar_assign.cpp — ANALYSIS COMPLETE

TOTAL=66: mt=7 rp=30 hc=14 sd=4 cl=1 bp=10

**Finding 1 — Dead descr arm:**
`bb_gvar_assign` is dispatched ONLY when `!g_descr_flat_chain` (emit_core.c line 449). The internal branch `if (g_descr_flat_chain)` at the top of the template body is dead code — it can never be reached when the template runs. **Action: delete it.**

**Finding 2 — IR_SEQ arm ONE-MEDIUM violation + load-bearing BINARY/TEXT split:**
- BINARY arm: `x86_load_ro("rsi","??",lhs_graph()) + x86_load_ro("rdx","??",rhs_graph())` — movabs raw in-process graph pointers. ONE-MEDIUM violation.
- TEXT arm: `bga_seq_parts(bb_slot_claim(16*_.op_parts_n))` — parts loop via `rt_gvar_assign_concat_parts`.
- Per 56th-run Lon directive "mode 3 and mode 4 should be identical": delete BINARY movabs arm, keep TEXT parts path only.
- [S] NOTE: this means mode-3 IR_SEQ gvar_assign loses its direct concat fast-path. Acceptable because `g_descr_flat_chain=1` in all production paths (confirmed by `flat_drive_gvar_assign` in emit_bb.c line 1833 which only populates `op_parts_n` for MEDIUM_TEXT).

**Finding 3 — IF(MEDIUM_TEXT, label+comment) wrappers:**
5 arms have `IF(MEDIUM_TEXT, x86("label",...) + x86("comment",...))` head wrappers. Per RULES.md + 56th-run directive: `x86("label")` and `x86("comment")` are medium-complete. **Delete all wrappers — label+comment unconditional.**

**Finding 4 — bga_seq_parts multi-emit helper (R2):**
`static std::string bga_seq_parts(int off)` composes ≥2 x86/x86_* emission calls. **Inline at its single call site, delete the helper.**

**Finding 5 — bypass conversions (R4/bp):**
- `x86_frame_load64("reg", off)` → `x86("mov", "reg", FRQ(off))` — dispatch XK_REG+XK_FR64 (x86_asm.h:567)
- `x86_frame_store64(off, "reg")` → `x86("mov", FRQ(off), "reg")` — dispatch XK_FR64+XK_REG (x86_asm.h:563)
- `x86_ro_load_q("reg", n)` — NO dispatch equivalent (XK_ROSLOT parses integer offset from `"qword ptr [rip + N]"` but x86_internal_name(n) produces a label string, not an integer). **Remains as bp= residue.**
- `x86_ro_seal_str(n, s)` — NO dispatch equivalent. **Remains as bp= residue.**
- `x86_load_ro("rsi","??",graph_ptr)` — in the BINARY concat arm being deleted → disappears with deletion.

**Finding 6 — static inline helper constellation (15 helpers, hc=14):**
`dst_name`, `dst_addr`, `dst_label`, `rhs_sval`, `rhs_addr`, `rhs_label`, `fn_lit_s`, `fn_var`, `fn_int`, `lhs_graph`, `rhs_graph`, `fn_concat`, `fn_concat_parts`, `fn_descr`, `bga_plbl`. These are zero-emit character-on-a-line fragment builders — they DON'T compose x86() calls themselves. Per the R2 rule KEEP zero-emit helpers? No — R4/hc rule says dissolve helper constellations. **Inline all expressions at call sites, delete all helpers.**

**Finding 7 — IR_CALL arm merge:**
The TEXT path adds `x86("label",...) + x86("comment",...)` at top; BINARY path omits them. After dropping the IF(MEDIUM_TEXT) wrapper, both paths become identical. **Single return path.**

**Finding 8 — multiple returns (rp=30):**
All the `static inline` helper functions contribute return count. After inlining helpers, the main function has one return per arm (6 arms + 1 bomb + 1 empty). The arms are if-chain → each returns. Per v2: ONE return per PLATFORM. Structure: chain the arms into a single `return` expression using the if-else chain (the if-bomb-early-exit pattern for the descr arm is already gone; use `x86_bomb` inline for the slot-check guards since they're single-line early exits — these count as "the 2 allowed returns").

---

## Regeneration recipe for next session

1. `git pull --rebase` on SCRIP
2. `git stash` to capture baseline for asm-diff
3. `bash scripts/build_scrip.sh` — compile baseline
4. Capture baseline asm: `./scrip --compile -o /tmp/bga_probe.s test/snobol4/smoke/01_hello.sno` (or suitable probe that exercises IR_ASSIGN with non-flat-chain path — check test suite)
5. Write regenerated `bb_gvar_assign.cpp`:
   - Includes: same header block (keep `bb_slot_claim` extern)
   - Remove all 15 static inline helpers and `bga_seq_parts`
   - `x86_begin()` at top of `bb_gvar_assign()`
   - Guard: `if (!PLATFORM_X86) return std::string();`
   - **descr arm: DELETE** (dead — `g_descr_flat_chain` is always 0 when bb_gvar_assign is called)
   - IR_LIT_S arm: `x86("comment","IR_ASSIGN") + x86("lea","rdi","[rip+__]",dst_addr_expr,dst_label_expr) + ...`
   - IR_LIT_I arm: similarly
   - IR_VAR arm: similarly
   - IR_BINOP arm: `if (_.op_a_slot < 0) return x86_bomb(...)` then single chain
   - IR_SEQ arm: TEXT parts path only (delete BINARY movabs); `if (_.op_parts_n <= 0) return x86_bomb(...)`; inline the bga_seq_parts loop
   - IR_CALL arm: merge TEXT/BINARY (same after dropping label/comment head wrapper); `if (_.op_a_slot < 0) return x86_bomb(...)`
   - Trailing `return x86_bomb("bb_gvar_assign other: unhandled rhs shape");`
   - Trailing `return std::string();` (for `!PLATFORM_X86`)
6. `audit_bb_fixup_file.sh bb_gvar_assign.cpp` → target 0
7. Full gate battery
8. Asm-diff proof: baseline vs new — expected diff: label/comment lines added (R1 sanctioned transform); IR_SEQ BINARY arm removed (sanctioned per Lon "m3==m4" directive, noted as [S])
9. Commit: `FIXUP bb_gvar_assign.cpp: mt→0 hc→0 rp→2 bp→2 [S]:IR_SEQ-BINARY-arm-deleted`
10. Advance cursor to next file in Z→A ring

---

## End state

| Metric | Value |
|--------|-------|
| SCRIP | `a1a2191` (unchanged) |
| .github | this commit |
| GRAND | 2014 (session open = session close, no SCRIP commits) |
| Cursor | `bb_gvar_assign.cpp` (analysis done, regeneration next session) |

**Gate floors (all verified at session open, no changes):** sno m4 7/7 HARD · pat M2 19 M4 19/0 · icon m2 12/12 HARD m3=m4 10/2 · prolog 5/5 ×3 · prove 0P rc=0 VACUOUS · purity 1 · bin_t 0 · vstack 3 · handencoded 0 · med_inv 102 · sno_pat_reg HARD · emit-blind 0.

---

## Outstanding verdicts (standing set, no changes)

- x86_movimm uint32-trunc (bb_call_fn)
- prove rc=0-on-FAIL hardening
- m2 disj-backtrack (PROLOG-BB)
- IRD-2b ratify
- ml false-positive
- counter-scope trio
- bb_arith + bb_atom dead-dispatch retirement
- ceiling-ratify
- prove-vacuous ratify (owner IR-REDESIGN — URGENT)
- c3b1dbb icon alternation (RESOLVED, ICON-NL to claim)
- two-chunk template design
- **bb_findall BINARY/TEXT split — PIN NEEDED**
- **bb_gather [S] residue — UNPINNED**
- rk gather/take m3/m4 silent (RAKU-BB)
- flat_drive_every dead-code (IR-REDESIGN)
- pK m4 silent-empty (PROLOG-BB/RAKU-BB)
- NL-flip prove_lower harness narrowed
- **bb_gvar_assign IR_SEQ BINARY arm deletion — [S] stated, Lon veto window open**

---

## Next session entry

```
# Cursor: bb_gvar_assign.cpp — analysis complete, execute regeneration
# Design fully pinned — see HANDOFF findings 1–8 above
# Key decisions stated (vetoable):
#   (a) descr arm deleted (dead code — g_descr_flat_chain=0 at dispatch site)
#   (b) IR_SEQ BINARY movabs arm deleted (Lon "m3==m4" directive; g_descr_flat_chain=1 in production)
# x86_ro_load_q + x86_ro_seal_str remain as bp= residue (no dispatch equivalent)
# Session env: tokenize .github remote before first push
```
