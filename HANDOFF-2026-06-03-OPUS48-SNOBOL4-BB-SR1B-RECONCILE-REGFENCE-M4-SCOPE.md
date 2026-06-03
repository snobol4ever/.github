# HANDOFF 2026-06-03 — SNOBOL4-BB — SR-1b reconcile + REG-FENCE authored + m4 wiring scoped (OPUS48)

## TL;DR

Session opened on the SNOBOL4-BB goal, discovered the goal file's live frontier (SR-1b) was **already
walked back** by the prior session but never reconciled, fixed that, audited the REG ladder against reality
(correcting several stale/wrong claims), landed ONE safe test-only deliverable (the **REG-FENCE** gate), and
converted the SNOBOL **mode-4** blocker from "pending wiring" into a concrete executable recipe. **No
emitter/runtime code changed.**

- **SCRIP `341b59f`** — adds `scripts/test_gate_sno_pat_reg.sh` only (rebased onto RUNTIME-REORG `5893518`).
- **.github this commit** — `GOAL-SNOBOL4-BB.md` reconciliation + this handoff.

## Gate (verified green on the actually-pushed, rebuilt tree)

SNOBOL4 m2 **7/7 HARD** / m3 **6/6** (`DOUBLE(21)`→`42`) / m4 0/6. REG-FENCE TIER 1 (`TEMPLATE_ADDR_SIG*`) = 0.
`prove_lower2` / `no_bb_bin_t` green. Rebuilt `scrip` + `libscrip_rt` against the rebased tree (5893518 +
the new gate) before/after the SCRIP push — m2 still 7/7.

## What this session did

### 1. SR-1b reconciliation (the prior session's explicit loose end)
Git (`bd8d6453`) + `HANDOFF-…-SR-1B-BOX-APPROACH-REJECTED.md` showed SR-1b (box-ify the call save/restore)
was **explored and REJECTED** by Lon, partial impl fully reverted, SCRIP clean at `3610475` (SR-1a). The
prior session deliberately left `GOAL-SNOBOL4-BB.md` untouched, so its CURRENT FRONTIER line, SR-1b bullet,
and Watermark still said "NEXT: SR-1b (3-box plan)" — a live contradiction. Reconciled:
- Frontier header re-pointed; added a **SR-1b WALK-BACK note** at top (the durable reasoning: a SNOBOL4 call
  is single-shot, not a backtrackable generator, so the FENCE/ALT save-on-α/restore-on-β model has no resume
  edge; save/restore stays **fused** in `rt_call_named_proc` via the SR-1a helpers `rt_name_save_push` /
  `rt_name_restore`; box-ification = zero test delta + premature; the caller-side `BB_SAVE_RESTORE`+`BB_CALL`
  pairing was incoherent — caller graph vs callee body). SR-1b bullet struck through. **SR-2** ("save-area IS
  the ζ-frame") remains the right *future* shape if ever revisited — NOT the rejected 3-box spelling.

### 2. REG-ladder audit (corrected stale + wrong claims)
- **REG-1 was DONE but left unchecked** → flipped to `[x]`. `bb_lit.cpp` carries `[REG-1 Σ=r13 δ=r14 Δ=r15]`,
  reads cursor=r14 / base=r13 / length=r15, zero `TEMPLATE_ADDR_SIG*`.
- **The `&Σ`/`&Σlen` process-local-address bake — the ladder's claimed "m4 blocker" — is GONE family-wide**
  (`grep -lE 'TEMPLATE_ADDR_SIG(MA|LEN)' bb_pat_*.cpp bb_lit.cpp` == empty).
- **Corrected an in-session miscount:** the r10 residue is **20 refs / 7 files** (`bb_lit`, `bb_pat_atp`,
  `bb_pat_break`, `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_defer`) — push/pop guards around
  memcmp/strchr + bb_lit's `[r10]` cursor-mirror writes — NOT the "bb_lit + bb_pat_atp only" first stated
  (that came from an incomplete file list).
- **BB-HYGIENE #0 ladder counts are stale / subsumed by the x86() revamp** (e.g. `bb_pat_cat`/`alt` cited
  194/185 are now **14** lines; `bb_capture` cited 226 is **gone**; `bb_pat_break` cited 349 is 200) — same
  verdict as the Prolog hygiene audit `4063911c`.
- **REG-RO is NOT trivial and was DEFERRED** (see ordering below): the `[r10]` cursor field is still
  **live-coupled** to `xa_flat.cpp:140` (`movsxd rcx, dword ptr [r10]`) in the **non-frame-active** epilogue
  path, which is **SHARED with Icon**; the cursor lives in BOTH r14 (boxes) and `[r10]` (flat driver). And the
  native `bb_lit`+`xa_flat` flat-chain that REG-RO would polish is **NOT the load-bearing m3 pattern driver**
  (that is `rt_scan`/`IR_SCAN`); the flat chain is exercised ONLY by the un-wired `test_sno_pat_bb_probe.sh`.
  So REG-RO is zero-test-delta debt on an ungated, Icon-shared path — do it only AFTER the flat chain is the
  real m3 driver (PB-RB-CONV) AND under a gate.

### 3. REG-FENCE — authored (the one code deliverable, test-only)
`scripts/test_gate_sno_pat_reg.sh` (house style: informational baseline → `--strict`, like
`test_gate_no_vstack.sh`):
- **TIER 1 (HARD):** `TEMPLATE_ADDR_SIGMA|TEMPLATE_ADDR_SIGLEN` in the SNOBOL pattern family == 0. Passes now,
  `--strict`-enforced — locks the bake-removal invariant.
- **TIER 2 (informational):** r10 residue count (currently 20). Flips to HARD when REG-RO lands (one marked
  line in the script). Added to the goal's Session Setup gate list.

### 4. Mode-4 blocker corrected + scoped into an executable recipe
The ladder claimed removing `&Σ`/`&Σlen` would lift m4. **False/stale:** the bake is already gone, m4 is still
0/6 because `--compile` aborts at `src/driver/scrip.c:801` with *"sno_ring_to_tree REMOVED … mode-4 emission
must come from LOWER producing the four-port statement-BB graph directly … wiring gap."* The abort site
ALREADY holds `sbbg` (the four-port `IR_graph_t` for `main` from `sm_preamble`) and just `(void)sbbg`-aborts.
Wrote a concrete recipe under **PB-RB-8** (the real SNOBOL m4 unblocker):
- REUSE `gvar_flat_chain_build_text(IR_graph_t*, FILE*, prefix)` (`emit_bb.c:2153`) — it emits the statement
  BODY only (not header/prologue/epilogue/strtab).
- Mirror the **Prolog mode-4 block immediately above (scrip.c:~770-787)** for the scaffolding: `xa_file_header`
  → `main` C-entry stub (SNOBOL runtime init like the define m3 path: `rt_proc_register` /
  `gvar_flat_chain_build` / `rt_proc_set_fn`) → per-proc `xa_flat_prologue` + body + `xa_flat_epilogue` under
  `g_frame_active=1` (the GZ-10 frame epilogue path — NOT the non-frame `[rip+Σ]/[r10]` path, so Icon's shared
  epilogue is untouched) → `xa_emit_strtab_rodata` → `return rc` (replace the abort).
- Then the **real assembly-debug tail**: `--compile → as → gcc -no-pie -lscrip_rt → run`, chase TEXT-arm bugs
  box-by-box until `test_smoke_snobol4.sh` mode-4 climbs (raise `MODE4_MIN`). **Deliberately NOT started this
  session** — it is a standalone rung that needs a fresh budget to land cleanly + gated, and replacing the
  abort with a half-working call would be a broken build.

## NEXT (re-pointed, in order)

1. **PB-RB-8 — LOWER four-port m4 wiring at `scrip.c:801`** (recipe above). The real m4 unblocker; real test
   delta (m4 0/6 → >0/6). Start fresh.
2. **REG-RO — DEFERRED behind (1)** (7 files + Icon-shared `xa_flat` epilogue; ungated, zero-test-delta until
   the flat chain is the m3 driver + gated). When done, flip REG-FENCE TIER 2 to HARD.
3. **SR-2** only if the call-frame is ever revisited (save-area = ζ-frame; NOT the rejected 3-box spelling).

## Files

- **SCRIP `341b59f`:** `scripts/test_gate_sno_pat_reg.sh` (new, test-only). Rebased onto `5893518`.
- **.github (this commit):** `GOAL-SNOBOL4-BB.md` (frontier + SR-1b walk-back + REG-1 [x] + REG-FENCE [~] +
  REG-LADDER/m4 reconciliation + PB-RB-8 recipe + Session-Setup gate line + Watermark) and this handoff.
- **Untouched:** all emitter/runtime/driver code; PLAN.md goals table (per RULES — routine handoff).
