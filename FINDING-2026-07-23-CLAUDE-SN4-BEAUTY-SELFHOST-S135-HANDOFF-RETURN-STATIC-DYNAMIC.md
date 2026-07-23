# FINDING 2026-07-23 (Claude s135) — SN4: beauty self-host — RETURN is a static graph-exit edge; one-flat-graph requires it become a runtime AR unwind

**Goal:** GOAL-SNOBOL4-BB.
**Session directive:** "Get beauty test suite then beauty self host. Continue." / "Compile ONE STATEMENT at a time from SNOBOL4. That is the proper granularity."
**Tree at handoff:** PRISTINE (no commits from this session). s134 commits already in HEAD.

---

## What this session did

1. **Cloned** `.github` + `corpus` + `SCRIP` (public, no credential). Symlinked canonical paths.
2. **Built** `scrip` + `libscrip_rt.so` at `-O0` (default, O0-DEV satisfied).
3. **Reproduced baseline** (tree is s134 HEAD — the O(n²) fix is already landed):
   - SN-7 gate: **48/51 PASS**, only `omega_driver` failing (×3, gate loops `--run --run --run` — mode-3 thrice, latent gate bug, not a regression).
   - Beauty self-host: **`zls: entry table overflow (65536)`** both modes (Blocker 1 from s134 FIXED finding).
   - eim.sno guard: `fact(5)=120 / fact(8)=40320` ✅.
4. **Isolated root cause empirically** — two stress tests that split count vs overlap:
   - 100 tiny **non-overlapping** DEFINEs (Gimpel jump-around: `DEFINE ... :(END)`): **compiles and runs correctly**. `sno_reach_body` scales fine with count alone.
   - 100 **overlapping** DEFINEs (shared fall-through tail, no jump-around): **`zls: scope table overflow (4096)`**. Each body's reachability closure pulls in the shared tail → bodies sum to O(N²) → cascade.
   - beauty is the second case: its DEFINEs don't universally jump around — they fall into shared code, so the reachable body of each is large and overlapping.
5. **Grounded DEFINE semantics in SPITBOL manual Ch. 8** (pp. 102–106):
   - *"the DEFINE function must be executed for the definition to occur… Most other programming languages process function definitions when a program is compiled."*
   - *"SPITBOL does not know or care what statements belong to a particular function. There is no explicit END statement for individual functions."*
   - Control transfers to the label with the function's name; RETURN/FRETURN unwind the activation record (dummy args + locals saved/restored on a pushdown stack at call/return).
6. **Diagnosed why "one flat graph" requires RETURN to become dynamic** (the load-bearing seam the s134 share-graph probe SEGVd on):
   - In the current lowerer (`lower_snobol4.c:1777–78`), RETURN/FRETURN lower to **static edges** to the graph's own `exitnd`/`failnd`. That is the *only* reason per-DEFINE graphs exist — each function body needs its own exit so RETURN returns to its caller, not to program end. IR_SUCCEED's emission interprets this statically via `resumable_callable`/`dyn_scope` on the graph config.
   - If body statements live in the one flat main graph, their `:S(RETURN)` edges resolve to **main's** exit → program termination instead of function return → SEGV/wrong behavior.
   - `sno_reach_body` is a partial mitigation — it shrinks each body graph, but can't prevent overlap when functions share code without jump-arounds.

---

## The architectural change Lon's directive requires

**"Compile ONE STATEMENT at a time."** Every SNOBOL4 statement is one box, lowered once, emitted once, in program order. The main graph already does this. Per-DEFINE sub-graphs are duplication of that work.

### What stays the same
- Main graph build: `g = sno_build_graph(st, nst, 0, is_def, NULL)` — emits every statement once. ✅
- Call mechanism: `rt_proc_call_open` → `rt_proc_call_prologue` (rt.c:965) → transfer to entry label → `rt_proc_call_epilogue_ret` (rt.c:576) unwinds. All runtime-mediated. ✅
- Entry label dispatch: `bynamefn`/`rt_goto_transfer` already resolve label-name → code address at runtime. ✅

### What must change

**LOWER (`lower_snobol4.c`):**
- RETURN/FRETURN must lower to **IR nodes that invoke `rt_proc_call_epilogue_ret`** at runtime, not static edges to a graph's own exit. This is the one required semantic change.
- Entry-in-main DEFINE branch: register name → entry-label anchor (from main's `bb_label_landing` snapshot, before any body-DEFINE build resets `g_bb_labels`). No `sno_build_graph`. No `sno_reach_body`. O(1) per DEFINE.
- The result-name assignment (`FUNCNAME = value`) before RETURN already lowers to IR_ASSIGN_VAR on the result cell — that's already correct; it's RETURN itself that is the static edge.

**EMIT (`scrip.c` per-proc loops, ~692 m4 / ~1125 m3):**
- A proc whose `bb_idx` points at main's graph must NOT call `emit_chain` on that graph's entry — main's boxes are already emitted. The proc entry point is the label's already-emitted box address.
- Each such proc emits only a **callable stub**: `proc_<name>_α:` that invokes `rt_proc_call_prologue` (to save dummy args + locals per the manual) and `jmp`s to the label's already-emitted anchor in main.
- `bb_node_id` keys on node identity — re-walking a shared node mints duplicate `bb<nid>_α` / `.Lbynamefn<nid>` symbols (the 18.7M-line `.s` and mode-3 NULL-chain from s134's share-graph probe). The stub sidesteps this entirely.

### Risk and guard
This changes RETURN for every function. The eim.sno guard (`fact(5)=120 / fact(8)=40320`) must stay green in BOTH modes throughout. The stress_chain test (recreate from § 4 above) must compile and produce correct output after the fix.

The change is **coupled** — LOWER alone SEGVs (s134 proof on `eim.sno`). EMIT alone has nothing to emit. They must land together, validated as a unit against: eim.sno (m3+m4), stress_chain (m3+m4), beauty self-host (m3+m4), and the full crosscheck (≥307/0 both modes).

---

## Remaining blockers after this change (from s134 FIXED finding)

### Blocker 2 — Pattern engine: *Parse recursive-grammar match
beauty's main match (line 616: `Src POS(0) *Parse *Space RPOS(0)`) fails under SCRIP.
Independent of DEFINE/LBL__ work (match is in MAIN, lowered identically).
Next: MONITOR-FIRST — 2-way sync-step to bracket first divergence in `Parse` pattern
construction vs the match execution in main.

---

## Acceptance gate (unchanged from s134)

| Gate | Status |
|---|---|
| `scrip --run beauty.sno < beauty.sno` = 622 lines md5 `9cddff2534472b822438801d8db58a99` | NOT MET (Blockers 1+2) |
| eim.sno m3 AND m4 = `fact(5)=120 / fact(8)=40320` | MET |
| crosscheck m3/m4 ≥ 307 DIVERGE=0 | MET (307/0) |
| .s artifact regen committed | MET |

---

## Key file locations for next session

- `src/lower/lower_snobol4.c:1766–1780` — `sno_build_graph` body, where `exitnd`/`failnd` are constructed and RETURN/FRETURN registered as static edges.
- `src/lower/lower_snobol4.c:1777–78` — **the two lines that must become runtime-unwind nodes.**
- `src/lower/lower_snobol4.c:2183–2215` — the entry-in-main DEFINE `else` branch (currently calls `sno_reach_body` + `sno_build_graph` → must become name-registration only).
- `src/driver/scrip.c:692` (m4) and `~1125/1156` (m3) — per-proc emission loops (must detect shared-graph procs and emit stub only).
- `src/runtime/rt/rt.c:576` — `rt_proc_call_epilogue_ret` signature (the target for dynamic RETURN lowering).
- `SPITBOL manual Ch. 8 pp. 102–106` — DEFINE/RETURN/FRETURN/local-var semantics grounding (manual on disk: `/mnt/user-data/uploads/1-spitbol-manual-v3_7.pdf`; extracted text at `/tmp/spitbol.txt` if still present).
