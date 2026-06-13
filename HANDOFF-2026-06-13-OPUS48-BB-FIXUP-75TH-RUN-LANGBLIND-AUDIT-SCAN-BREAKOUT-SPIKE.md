# HANDOFF — BB-FIXUP-A-to-Z, 75th attended run (Opus 4.8)
2026-06-13 · Lon attending ("…Add the audit… Break out the IR by the lower stage… Break out a BB by common form. Continue." ×3)

This run: **W1 LANDED** (LANGUAGE-BLIND audit), **W2 SPIKED** (scan-builtin IR breakout — recipe + blocker, NOT landed). Cursor STAYS `bb_call.cpp`. SCRIP @ `1f9f595` on origin.

---

## ENV SETUP (fresh container — do FIRST, this is not code)
1. `apt-get install -y libgc-dev` (provides `gc/gc.h`; build fails without it).
2. `bash scripts/build_scrip.sh` (→ `./scrip`).
3. `make libscrip_rt` (→ `out/libscrip_rt.so`) — **required for mode-4**; without it smoke shows `<mode4-build-failed>` (NOT a code regression).
Baseline then GREEN at floors: sno m4 7/7 HARD · pat M2/M3/M4 19/0 · prolog 5/5 ×3 · prove_lower 0 rc=0 VACUOUS · purity 1 (`bb_call_write_slot`) · bin_t 0 · vstack 3 · handencoded 0 · sno_pat_reg HARD. **Run the Icon battery too before W2: `scripts/test_icon_all_rungs.sh` (m2 12/12 HARD + m3=m4 10/2).**

---

## W1 — LANGUAGE-BLIND audit (LANDED `1f9f595`)
New `lang_blind` category in BOTH `scripts/audit_bb_fixup_file.sh` (per-file gate; folds into TOTAL/rc) and `scripts/audit_bb_fixup_rank.sh` (lap table; folds into GRAND). Flags reads of the 4 driver-mode/LANGUAGE selector globals inside `bb_*.cpp`:
```
\bg_(gvar_flat_chain|descr_flat_chain|icn_scan_regs_live|gvar_callarg_live)\b
```
- Excluded by design: `g_emit_text_mode` (MEDIUM axis), `g_sno_m4_dense_nid` (counter).
- Precise: counts == raw grep; agrees with 71st/72nd `bb_binop_gvar_arith*` strips (read 0); no false-positive on `rt_*`/`POWER_fn` decls. Shell-only ⇒ behavior-neutral.
- **Re-baseline (accepted cascade):** GRAND **1143 → 1215** (+72) · dirty **76 → 95** (+19 flipped clean→dirty) · 28 files carry language reads (19 newly dirty, 9 already) · `bb_call` **316 → 326** (lb=10).
- Cursor STAYS `bb_call.cpp`; the 19 behind-cursor flips are re-fixed via the next-lap re-audit (goal §"THE CURSOR", line 63), NOT a backward jump.
- **Flagged, not fixed (never-widen-scope):** the rank script also lacks `cv9` + `cv10` (pre-existing desync; why the goal tracks `bb_call` rank TOTAL, not the higher per-file figure).
- **For Lon (W1 stands, flagged for veto):** `g_icn_scan_regs_live` is a FIX-3 *sanctioned driver-mode* flag in the emit_bb.c DRIVER; `lang_blind` flags only its read inside the 1 TEMPLATE (templates must be mode-blind; the driver isn't a `bb_*.cpp` file → untouched), per the 71st-run recommendation.

---

## W2 — FIX-3-iii scan-builtin IR breakout (SPIKE — recipe below; do NOT land before resolving the blocker)

### What already exists (the breakout is HALF-BUILT, DORMANT)
- 9 kinds `IR_SCAN_{POS,ANY,MATCH,MANY,TAB,MOVE,UPTO,FIND,BAL}` in `IR.h` (enum) + `scrip_ir.c` (names).
- `emit_core.c:499-507` dispatches each `IR_SCAN_*` → its `bb_scan_*()` template.
- The 9 `bb_scan_*.cpp` templates exist (directive #3 "BB by common form" effectively DONE for scan).

### Why dormant (DELIBERATE — git `-S 'IR_SCAN_POS'`)
Commit **`5091102` "ICN-SCAN-2"** added the kinds as a dormant SANCTIONED-FALLBACK: *"oracle builtin-gen resume resists cheap delegation … emit_core IR_CALL case gated on g_icn_scan_regs_live … lowerer + m2 UNTOUCHED."* A prior session with generator-resume context judged a lowering-time retag unsafe and chose emit-time routing on purpose.

### Live path today
`emit_core.c:467-478`: `g_icn_scan_regs_live && sval∈{9}` → `bb_scan_*()`, else `bb_call(nd)`. Driver op-field prep is in the `IR_CALL` scan arms `emit_bb.c:2585-2680` (gated `g_icn_scan_regs_live && dval==3.0 && sval`).

### Architecture
- `lower_icon.c:213` `TT_SCAN` → `IR_GEN_SCAN`; subject sub-graph in `IR_EXEC.counter`, **body sub-graph `IR_graph_t* bsg` in `IR_LIT.ival`**.
- Emit-time scan context = `g_icn_scan_regs_live=1` set ONLY around `flat_emit_arg_subchain(body…)` (`emit_bb.c:1962-1965`).
- Scan builtins are also callable OUTSIDE scan (implicit `&subject`) ⇒ **retag MUST be scoped to the scan body** (`bsg`).
- `IR_graph_t` exposes `IR_t ** all; int n` (IR.h:265) ⇒ walking `bsg` is clean.

### RECIPE (lower-stage breakout; behavior-neutral by the 74th DEFINE-carve technique — keep `dval`+`sval`, retag `op` ONLY)
1. **`lower_icon.c` `TT_SCAN`:** after `bsg = arg_block(...)`, `for(i<bsg->n)` retag `bsg->all[i]` where `op==IR_CALL && sval∈{9}` → `IR_SCAN_<X>`.
2. **`emit_bb.c` driver:** add `case IR_SCAN_POS..BAL:` fall-through to `case IR_CALL:` prep; add `IR_SCAN_*` to op-switches `1815` (allow-gen), `1833` (chain-walker), `3230` (size), FILL-size.
3. **`IR_interp.c` mode-2:** add `IR_SCAN_*` alongside `IR_CALL` at classifier (~`292`, the `case IR_CALL:` with scan-name `sval` check; `case IR_SCAN: return 1` is right below), `_is_strgen` (`2603`), `pos` (`3854`), and the main exec dispatch.
4. **`emit_core.c`:** DELETE the now-dead `IR_CALL` scan dispatch `467-478`.
5. **Verify:** C2 scan asm-identity (expect byte-identical) + C3 (Icon all-rungs m2 12/12 HARD + m3=m4 10/2 + sno/prolog/pat/structural).

### ⛔ BLOCKER — resolve FIRST
Driver prep gates on `IR_LIT(nd).dval == 3.0`, but **no Icon-side `dval=3.0` setter exists** (`grep -rnE 'dval *= *3' src/` → ONLY `lower_raku.c:269`, Raku). The Icon scan-builtin marshalling-state model is therefore **incomplete** — a lower-time `op` retag may desync from whatever sets `dval` (likely an emit-time/marshalling pass = the gen-resume coupling `5091102` flagged). **Empirically dump an Icon scan program's IR** (op/dval per scan-builtin node; no `--dump-ir` flag exists — add one or instrument `walk_bb_node`) to confirm the representation before retagging. If `dval` is emit-time-only, the prep must stop gating on `dval==3.0` and key on the kind instead (slightly larger).

### Recommended sequencing next session
- **Commit 1 (INERT prep, safe):** add `IR_SCAN_*` fall-through cases to driver + mode-2 + op-switches WITHOUT the lowering retag and WITHOUT deleting `467-478`. Behavior-neutral by construction (nothing emits the kinds yet) ⇒ battery green trivially. This makes the kinds "ready to receive."
- **Commit 2 (behavior-changing):** the `lower_icon` retag + `emit_core` deletion + full C2/C3. Only after the `dval` blocker is resolved.

---

## STATE
- SCRIP origin HEAD `1f9f595` (W1). `.github` @ this commit (watermark + this doc).
- Cursor `bb_call.cpp` (FIX-3 monster; rank TOTAL 326, of which lb=10). FIX-3-i (op_write_route) + FIX-3-ii (`bb_call_define`) landed prior runs; FIX-3-iii (scan + the dval==2/3 proc mass) remains.
- Ceiling: 131 files / 95 dirty / 36 clean / GRAND **1215**.
- For Lon: (1) `g_icn_scan_regs_live` reconciliation (W1 stands, veto if you meant to exempt the template read); (2) scan-breakout = Option A (lower-stage retag) per your directive — execute next session after the `dval` blocker is resolved.
