# FINDING 2026-07-24 (Claude) — SN4 beauty self-host: the 1-node DEFINE entry-stub is PROVEN end-to-end; only re-emission-free label registration remains

**Goal:** GOAL-SNOBOL4-BB. **Directive:** "process SNOBOL4 statements ONE at a time" (Lon) — i.e. the ⭐⭐ FINAL DIRECTION of FINDING-2026-07-23-...-SHARE-GRAPH-BLOCKED-ON-REEMISSION.md.

## TL;DR — a real advance past three prior sessions
The 1-node entry-stub ("DEFINE is a single statement") is **implemented and validated end-to-end on `eim.sno`**: `SCRIP_SN4_STUB=1 scrip --run eim.sno` → `fact(5)=120 / fact(8)=40320`. Prior sessions (2026-07-22, s134, s135, 2026-07-23) all *diagnosed* this direction but **none got it running**. This session did. The DEFINE O(n²) is dead. **One wire remains:** re-emission-free registration of the ~39 DEFINE entry labels.

Committed (local, gated, default-safe): **`d39d3b20`** "SN4 beauty self-host: 1-node DEFINE entry-stub (gated WIP, validated on eim)". Push pending Lon's credential.

## WHAT LANDED (all gated behind env `SCRIP_SN4_STUB`; default path BYTE-IDENTICAL)
Guard re-confirmed with the edits present: **crosscheck m3 307/3, m4 307/3, DIVERGE=0**, fail-set `{140_pat_eval_double_fn_trick, 141_pat_eval_double_fn_arbno}` (watermark, unchanged). `eim.sno` default (no flag) green.

`src/lower/lower_snobol4.c`:
1. **`sno_build_call_stub(entry_label)`** (added just before `sno_build_graph`, ~line 1804): mints `IR_alloc(64)` with `IR_SUCCEED` exitnd, `IR_FAIL` failnd, and an `IR_GOTO_DEFERRED` node (γ=exitnd, ω=failnd) whose `IR_LIT.sval = lp_strdup(entry_label)`; `g->entry = gd`. This is the whole stub: α runtime-transfers by NAME into main's already-emitted body; its own exit/fail catch RETURN/FRETURN.
2. **Entry-in-main DEFINE branch** (the `else` after `if (eidx < 0) continue;`, ~line 2247): gated `if (getenv("SCRIP_SN4_STUB")) { gf = sno_build_call_stub(defs[di].entry); } else { ...original sno_reach_body + sno_build_graph... }`. The proc still registers with `dyn_scope=1`, `nparams`, `result_name`; `bb_idx` = the stub graph; `proc_entry_node` left NULL (so `bb_proc_entry` uses `g->entry` = the stub's `IR_GOTO_DEFERRED`).
3. **SCAFFOLD (TEMPORARY, must be replaced — commented in-code as `SN4-STUB SCAFFOLD`):** the LBL__ label-registration loop condition was widened `if (g_sno_uses_code || getenv("SCRIP_SN4_STUB"))` so the DEFINE entry labels get registered (via LBL__/arm-4) and the stub's `rt_goto_transfer` resolves. **This is what proved the stub on eim.** BUT it re-lowers ALL labels (`sno_reach_body`+`sno_build_graph`), re-introducing the O(n²) → **beauty still overflows HERE** (`zls: entry table overflow (65536)` from the LBL__ loop, NOT the DEFINE loop). It is a test-enabler only.

## WHY THE STUB IS CORRECT (mechanism, fully traced — resolves the doubts in the prior finding)
- **RETURN routing works.** FINDING-2026-07-23 line 44 was right and is now empirically confirmed: `RETURN`/exitnd is **not graph-specific at runtime**. `rt_proc_call_prologue` (rt.c:965) pushes the activation record (dyn-scope: `rt_name_save_push` of the formals, pcall record); the stub's own exitnd → `rt_proc_call_epilogue_ret` (rt.c:1158) unwinds it and hands the DESCR back to the caller; the *value* comes from the name dictionary (`NV_GET_fn(rname)`), correct under sharing. So the body's `:S(RETURN)` returns fact's value to fact's caller even though the body lives in main's graph.
- **Recursion is safe.** `rt_goto_transfer` (runtime_eval.c:271) resolves the label and calls `rt_chain_enter(fn)` (runtime_eval.c:283), which **runs the target on a FRESH 64KB frame** (`GOTO_FRAME_BYTES`, per-crossing-fresh, GC-visible). Each recursive `fact(n-1)` is a fresh crossing → its own frame → no clobber. Cost: 64KB + one C-stack level per crossing, never freed (fine for beauty's finite recursion; a frame-recycling tail-transfer is a later rung). This is why the earlier "shared-frame SIGBUS/clobber" worry does **not** bite — the fresh-frame-per-crossing sidesteps it entirely.
- **No re-emission from the stub.** `emit_chain` on the 1-node stub emits only the stub's own nodes (α prologue + the deferred goto) — collision-free. The body is emitted exactly once, as part of main.

## THE ONE REMAINING WIRE — re-emission-free registration of the DEFINE entry anchors
`rt_goto_transfer(name)` resolution order (runtime_eval.c:271-294): (1) `$X` indirect, (2) END, (3) **`g_lbl_tab` via `rt_label_get_fn`** (arm 3), (4) `LBL__<name>` pseudo-proc via `rt_proc_get_fn` (arm 4), (5) variable holding a CODE value, (6) fatal `transfer to undefined label`.
- **Arm 3 (`g_lbl_tab`, set by `rt_label_set_fn`) has ZERO emit-side callers today** — grep confirms `rt_label_set_fn` is called nowhere in `src/` outside its own definition. It is effectively dead; nothing populates it.
- **Arm 4 (LBL__) is the only working route, and it RE-EMITS** (`emit_chain(proc_entry_node)` re-walks main's suffix, re-minting node-id-keyed `bb<nid>_α` / `.Lbynamefn<nid>` → duplicate symbols + bloat for beauty's 163 labels). This is the scaffold's O(n²).

So **no re-emission-free registration exists** — it must be built. All clean routes converge on ONE missing capability: **during main's single emission, attach a stable entry point (symbol for m4, box-fn address for m3) at each DEFINE entry anchor, and register it** so `rt_goto_transfer` arm 3 (or a non-re-emitting arm 4) resolves the name → the in-main address.

### Implementation options (for the next, focused session — this is BB-CODEGEN: read `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` FIRST)
**Option 1 — main-emission-time anchor label attachment (RECOMMENDED; covers BOTH modes cleanly).** Teach `emit_chain`/`emit_drive` to, when emitting a node flagged as a DEFINE entry anchor, ALSO emit a stable exported entry (m4: a `.globl sno_entry_<name>` label aliasing the box; m3: capture the box-fn pointer into a node→fn map). Then register via `rt_label_set_fn(name, addr)` — m4 at `proc_startup` (`lea rsi,[rip+sno_entry_<name>]`), m3 by direct call with the captured fn. Requires threading "which nodes are entry anchors" to the emitter — snapshot main's label→anchor **right after main's build** (`lower_snobol4.c` ~2185, BEFORE the LBL__ loop / any body-DEFINE `sno_build_graph` resets the GLOBAL `g_bb_labels` registry, `lower_common.c:15-30`) and stash on the proc-table entry (add a field, e.g. `IR_t *body_anchor`, to `ProcEntry` in `stage2.h`; init NULL in `sm_prog.c:49`).

**Option 2 — m4-only driver-level `bb_node_id` trick (partial; NOT sufficient alone — m3 needs Option 1).** `bb_node_id` (emit.cpp:293) is memoized by node identity across the whole m4 compile (dense counter, `g_nid_key` not reset between procs). So from the driver one can `lea rsi,[rip+bb<bb_node_id(anchor)>\xce\xb1]` and it resolves to main's emitted label **regardless of emission order** (calling `bb_node_id` in `proc_startup` assigns the id; main's emission emits the actual `bb<nid>\xce\xb1:` — memoization keeps them equal). Snag: there are **multiple m4 driver paths** (`scrip.c` ~1085/1195 text; the `proc_entry_node` loop at 1177; a `flat` path at 1264) — registration must go in each. And m3 (JIT, ~1291/1458) has **no asm symbol** to `lea` and `emit_chain` returns only the ENTRY box-fn, so m3 CANNOT use this — it needs Option 1's node→fn capture. ⇒ Option 1 is the real fix; Option 2 is a possible m4 stopgap if a mode-split is acceptable.

**Option 3 — by-node deferred goto (avoids arm-3 registration but needs emitter reference-not-walk).** Make the stub's goto target the anchor NODE (not a name); emit `jmp bb<bb_node_id(anchor)>\xce\xb1`. Needs `emit_chain` to reference an external (already-emitted, different-graph) node WITHOUT walking it (else it re-emits main's suffix — the collision). Equivalent difficulty to Option 1; no clear advantage.

## VALIDATION LADDER for the next session (unchanged gates)
1. `SCRIP_SN4_STUB=1 scrip --run eim.sno` stays `fact(5)=120/fact(8)=40320` after replacing the scaffold with clean registration (m3).
2. Same in `--compile` (m4).
3. `SNO_LIB=. scrip --run beauty.sno < beauty.sno` → **622 lines, md5 `9cddff2534472b822438801d8db58a99`** (oracle via `scripts/util_run_beauty_oracle.sh`). Then `--compile`.
4. Remove the `|| getenv("SCRIP_SN4_STUB")` scaffold; if the stub path proves out, consider making it the DEFAULT (drop the env gate) and re-run crosscheck — MUST hold 307/0 DIVERGE=0, smokes 7/7×2.
5. If codegen touched: regen `.s` artifacts (handoff step 4: `util_regen_{benchmark,feature,demo}_s_artifacts.sh`).
MONITOR-FIRST on any SEGV; `eim.sno` (at `/tmp/bsh/eim.sno`, NOT committed — recreate from below) is the 6-line repro, then beauty.

### eim.sno (recreate; scratch, never committed)
```
        DEFINE('fact(n)')                   :(factEnd)
fact    fact = LE(n,1) 1                    :S(RETURN)
        fact = n * fact(n - 1)              :(RETURN)
factEnd
        OUTPUT = 'fact(5)=' fact(5)
        OUTPUT = 'fact(8)=' fact(8)
END
```

## KEY PATHS
- `src/lower/lower_snobol4.c`: ~1804 `sno_build_call_stub` (NEW); ~2185 main build + snapshot point; ~2220 LBL__ loop (scaffold widened); ~2247 entry-in-main DEFINE stub gate; :43 `g_sno_uses_code`; :603 RETURN lowering (`IR_GOTO` → `bb_label_landing("RETURN")`); :673 `sno_goto_target` (`IR_GOTO_DEFERRED` shape).
- `src/lower/lower_common.c:15-30`: GLOBAL `g_bb_labels` (reset per `sno_build_graph`) — snapshot BEFORE body-DEFINE builds.
- `src/runtime/runtime_eval.c:250 rt_label_set_fn` (arm-3 registry — no emit-side callers), `:264 rt_label_get_fn`, `:271 rt_goto_transfer`, `:283 rt_chain_enter` (fresh 64KB frame).
- `src/runtime/rt/rt.c:965 rt_proc_call_prologue`, `:1158 rt_proc_call_epilogue_ret`.
- `src/contracts/stage2.h:20-34 ProcEntry` (add `body_anchor`); `src/machine/sm_prog.c:49` init.
- `src/driver/scrip.c`: m4 text ~1085/1195, `proc_entry_node` loop 1177, `flat` 1264; m3 ~1291/1458. All skip `"main"`; `proc_startup` is where startup registration goes.
- `src/emitter/emit.cpp:293 bb_node_id` (identity-memoized), `:554 bb<nid>\xce\xb1` mint; `src/templates/bb_call.cpp:290 .Lbynamefn<nid>`.
- `src/contracts/zeta_storage.c:12,14,17` ZLS_MAX_ENTRIES/SCOPES/MARKS (65536/4096/65536) — overflow aborts.

## STATE AT HANDOFF
- Tree: commit `d39d3b20` on top of the prior HEAD; ONLY `src/lower/lower_snobol4.c` changed (gated). `scrip` built `-O0`; `libscrip_rt.so` unchanged from session start (lower-only edits). Default crosscheck 307/0, beauty suite 48/51 (omega ×3, the `for mode in --run --run --run` gate quirk — not a regression), oracle 622 reproduced.
- **NOT pushed** — awaiting Lon's credential. No `handoff_status.sh` run (push not done).
