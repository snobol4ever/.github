# HANDOFF-2026-05-29-OPUS48-SBL-SPAN-VERIFIED-DEFER-NESTED-XDSAR

**Session:** Opus 4.8, 2026-05-29. Goal: GOAL-SNOBOL4-BB, watermark NEXT = "SBL-SPAN-2 BINARY arm".
**Outcome:** Analysis only. No code landed. Baseline gates restored bit-for-bit (zero regression).
**Reason no commit:** The watermark's stated next step was based on a false premise; the real blocker
is a different, deeper bug whose correct fix could not be validated within this session's budget.
Per RULES.md ("No broken commits", "Run goal's gate before every commit"), nothing speculative was committed.

---

## Baseline confirmed (matches prior watermark exactly)

GATE-1 smoke 13/13 · GATE-1 native 13/13 · rung M2=19 M4=17 · GATE-3 mode4 184/280 · native mode-3 223/280.
HEAD at session start: `ce99d578`. No commits this session.

---

## Finding 1 — SPAN already works in mode-3 native. "SBL-SPAN-2" is a phantom.

The watermark said: *"SBL-SPAN-2 BINARY arm — largest remaining cluster (~10 tests) … β yields
successively shorter spans."* This is already done. `bb_pat_span.cpp` has a complete MEDIUM_BINARY
arm (committed `4ce8c385`, escape-fixed `44766d91`) with two process-lifetime deque-int slots
(z, z_orig) and a working β backtracking path.

Verified by direct native test (SCRIP_M3_NATIVE=1, no flag → g_bb_mode=BROKERED) — all PASS:
- Deep backtrack: `"aaaaab" SPAN("a") "aab"` → MATCH (m2==m3)
- Two SPAN boxes: `"aaabbb" SPAN("a") SPAN("b")` → MATCH
- SPAN in ARBNO (re-entrancy): `"a1b2c3" ARBNO(SPAN(&LCASE) SPAN("123")) RPOS(0)` → MATCH
- SPAN capture: `"hello world" SPAN(&LCASE) . W` → "hello"
- **"071 minus deref"** — `"hello world" POS(0) SPAN(&LCASE) . V1 ' ' SPAN(&LCASE) . V2 RPOS(0)`
  → "hello, world" (m2==m3). This is 071 with the `*WORD` replaced by inline SPAN — it passes,
  proving the SPAN/POS/CAT/capture machinery is sound in native.

The "SPAN cluster" native failures (071, 124, 138, 139, expr_eval) all fail on a DIFFERENT feature
that happens to co-occur with SPAN in those programs. SPAN is innocent. **Do not spend a session on
SBL-SPAN-2 — it is complete.** Mark it ✅ and move the budget to Finding 2.

---

## Finding 2 — The real blocker: nested XDSAR (`*var`) inside a combinator fails under sm_run_native.

`*WORD` (deferred pattern-valued name ref) lowers to `SM_PAT_REFNAME` → `pat_ref()` → a **XDSAR**
PATND node. Behavior split, isolated precisely:

| Pattern shape | m2 (sm-interp) | m3 native (SCRIP_M3_NATIVE=1) |
|---|:---:|:---:|
| top-level deref to PATTERN  `"hello" *WORD`            | MATCH | **MATCH** |
| top-level deref to LITERAL  `"hello" *W`               | MATCH | **MATCH** |
| nested deref in combinator  `"hello" POS(0) *WORD`     | MATCH | **NOMATCH** ← bug |
| full 071 `… POS(0) *WORD . V1 ' ' *WORD . V2 RPOS(0)`  | hello, world | **fail** ← bug |

**Why top-level works but nested fails:** `stmt_exec.c:335-341` (SBL-DCG-DEFER) resolves the XDSAR
**only when it is the top-level pattern** (`pp0->kind == XDSAR`). When the XDSAR is a *child* of an
`XCAT` (the `POS(0) *WORD` case), `pp0->kind == XCAT`, so the early resolution never fires; the nested
XDSAR survives into the builder.

**Why m2 works but m3 native fails on the nested case:** Both run `g_bb_mode == BB_MODE_BROKERED`
(no-flag default sets `mode_interp` → `bb_driver=1` → BROKERED, even with SCRIP_M3_NATIVE set — see
`scrip.c:155-161`). Same builder, same `rt_pat_*`, same `exec_stmt` C code. The ONLY divergence is the
SM-execution engine: m2 = `sm_interp_run` (C dispatch loop); m3 = `sm_run_native` (`sm_native.c:61`,
emits x86 that calls the same `rt_*`). So the bug lives in how the native SM byte-stream builds/matches
this pattern — a MODE3-DISPATCH-GAP instance (see MODE3-DISPATCH-GAP.md), now narrowed to the smallest
reproducer for SNOBOL4: **a single nested XDSAR child of XCAT.**

The new opcode vs the passing "071-minus-deref" stream is exactly **`SM_PAT_REFNAME` (instr 7)**
sitting between `SM_PAT_POS` and `SM_PAT_CAT`. `SM_PAT_REFNAME` alone (top-level) works, so the defect
is the *interaction*: the XDSAR value built by `rt_pat_refname` must be correctly cat'd by
`SM_PAT_CAT` and then resolved during `SM_EXEC_STMT`'s brokered build (`patnd_to_bb_graph` /
`bb_build_brokered` translating the nested XDSAR). That resolution path produces a match in the C loop
but not when the identical calls are driven from the native blob.

### Dead-end paths ruled out this session (do not re-investigate)
- `bb_pat_defer.cpp` MEDIUM_BINARY arm: it WAS empty (silent eps — a latent MODE-PURITY landmine),
  and I wrote a correct flat arm (movabs varname + rt_defer_match, push r10/r11 align, POS-style
  `{ω,γ,β-def,ω}` sites). **But it is never reached** for this failure: the nested-XDSAR pattern goes
  through the dynamic `rt_pat_refname`/`exec_stmt` brokered path, not the flat BB_PAT_DEFER template.
  Reverted. (If DEFER flat-wiring is ever enabled, that arm is the right shape — see git stash/this doc.)
- `lower_flat_invariant` (`emit_sm.c:583`) returns 0 for BB_PAT_DEFER: that gate governs the **mode-4**
  `walk_bb_pattern_blobs` emit path, NOT the runtime `bb_build_flat`/brokered path. Flipping it had no
  effect on this failure. Reverted.

### NEXT — where to actually dig
Instrument `sm_run_native`'s execution of the 071 stream (instrs 5-11) and compare the built pattern
value + `exec_stmt` outcome against the m2 path. Likely candidates, in order:
1. `SM_PAT_CAT` BINARY arm (`sm_pat_combine.cpp`) vstack handling when a child is XDSAR.
2. `SM_EXEC_STMT` BINARY arm — does the brokered build of the nested XDSAR see the same globals
   (Σ/Σlen/Δ/Ω) the C loop sets up? Check whether sm_run_native leaves any global mismatched at
   EXEC_STMT entry vs sm_interp_run.
3. The brokered translation `patnd_to_bb_graph` of XCAT-over-XDSAR under the native call sequence.
This unblocks a large cluster: 056, 070-074 (star_var), 108-115 (fence-via-var also routes through
deferred name resolution), 140-141 (eval-fn tricks), 147 — collectively the biggest native-only group.

---

## ROOT CAUSE FOUND (same session, continued) — supersedes the "dig order" above

Probe (`PROBE_MV` fprintf in `rt_match_variant`, reverted) revealed:
- **m2 never calls `rt_match_variant`.** Mode-2's `SM_EXEC_STMT` handler (`sm_interp.c:582`) uses a
  **pre-lowered BB graph**: `pat_bb = a[2].i>=0 ? bb_table[a[2].i] : NULL; if (pat_bb) ok =
  bb_exec_pat(pat_bb,…)`. `bb_exec_pat` is a mode-2-only C BB walker (forbidden in modes 3/4 by RULES).
  So m2 matches the nested XDSAR via the statically-lowered graph and succeeds.
- **m3 native calls `rt_match_variant` → `exec_stmt`**, which returns **ok=0** (pat.v=3=DT_P, Σ/Σlen
  correct). Mode-3 cannot use `bb_exec_pat`; it must build+match the *dynamic* PATND on the vstack.

The dynamic build fails because of the **translator-eligibility gate** in `stmt_exec.c`:
- BROKERED mode (the no-flag + SCRIP_M3_NATIVE default — `scrip.c:155-161` sets bb_driver→BROKERED):
  `patnd_needs_xlate(pp)` (`stmt_exec.c:301`) = `contains_arbno || is_simple_atom ||
  is_capture_wrapped_safe`. For `XCAT(XPOSI, XDSAR)` all three are false → `pp_cfg=NULL` →
  `pp_bb = (BB_t*)pp` — **the legacy PATND→BB cast that misreads opcodes** (documented at
  `stmt_exec.c:237`) → garbage box → no match.
- LIVE mode (`--run` forces it, though plain `--run` today still falls to sm_interp): the gate is
  `patnd_is_combinator_root` → `patnd_tree_eligible` (`stmt_exec.c:271`). XDSAR is NOT in its switch
  → `default: return 0`, so any XCAT/XOR/XFNCE *containing* an XDSAR child is rendered ineligible →
  same legacy-cast fallback.

`build_patnd` (`lower_pat_dcg.c:468`) DOES translate XDSAR → `BB_PAT_DEFER` correctly. The problem is
purely that the gate refuses to *invoke* the translator for XDSAR-bearing trees, so the legacy cast
runs instead.

### The fix is two-part (both required; neither alone suffices)
1. **Gate** (`stmt_exec.c`): add `patnd_contains_defer(pp)` (mirror `patnd_contains_arbno`) and OR it
   into `patnd_needs_xlate` (BROKERED). Add `case XDSAR: return 1;` to `patnd_tree_eligible` (LIVE)
   — or add XDSAR to `patnd_is_simple_atom` (it lowers to a leaf BB_PAT_DEFER box, atom-like). This
   routes XDSAR trees to `patnd_to_bb_graph`/`patnd_to_bb_tree` → real `BB_PAT_DEFER` node.
2. **DEFER box bytes** (`bb_pat_defer.cpp`): the `MEDIUM_BINARY` arm is **empty** (returns ""). Under
   `bb_build_brokered` (EMIT_BINARY_BROKERED) and `bb_build_flat` (EMIT_BINARY_WIRED) the node hits
   that empty arm → no bytes → broken box. Implement it. NOTE the ABI differs by mode:
   - BROKERED (`emit_bb.c:1217`, `codegen_flat_body` after `push rbp;mov rbp,rsp`): C-ABI box,
     rdi=ζ, esi=port, `ret`. The TEXT arm's logic (call rt_defer_match(varname,ival,Δ); test; js ω;
     writeback; γ) must be expressed in the brokered byte ABI, not flat jmp-threading.
   - WIRED (flat): r10=&Δ, jmp γ/ω. (My earlier flat draft — reverted — had this shape and is a
     correct starting point for the WIRED arm; redo per the brokered ABI for the BROKERED arm.)

### Validation checklist for the fix
- Must NOT regress the 6 tests the `stmt_exec.c:237` comment warns about: **146, 147, 152, 1011,
  1013, 1017** (fence-heavy / capture-heavy PATND trees that the legacy cast was "compensating" for).
  Run these in m2, m4, and native after the change.
- Target newly-passing native: **056, 070-074, 108-115, 140-141, 147** (star_var, fence-via-var,
  eval-fn). Expect native 223 → ~235+.
- Full gates: G1 13/13 (default+native), G3 184/280, G4 252/280, native ≥223, rung M2=19/M4=17, FACT 0.

---

## ATTEMPTS THAT ARE CONFIRMED INSUFFICIENT (same session, empirical — skip these)

Both parts of the spec above were implemented and tested together; **nested deref still → NOMATCH**.
All reverted; baseline intact (13/13 native). So there is a THIRD factor beyond the two-part spec.

1. **Gate fix alone** (route XDSAR through translator): added `patnd_contains_defer` → OR'd into
   `patnd_needs_xlate`; added `if (pp->kind == XDSAR) return 1;` to `patnd_tree_eligible`. Built clean.
   Result: nested deref still NOMATCH in native. (The DEFER node now routes to the translator but its
   empty MEDIUM_BINARY arm emits a broken box.)
2. **Gate fix + DEFER flat MEDIUM_BINARY arm** (the exact flat-ABI bytes drafted earlier: movabs
   varname + rt_defer_match, push r10/r11, test/js ω/writeback/jmp γ, β=jmp ω, POS-style sites
   `{42,50,54,55}` `{ω,γ,β-def,ω}`). Built clean. Result: **STILL NOMATCH** in native (071 still `fail`).

**Implication:** the remaining defect is NOT just the gate + DEFER box bytes. Candidates for the THIRD
factor (next session, instrument before coding):
- `patnd_to_bb_graph(XCAT(XPOSI,XDSAR))` may return NULL/no-entry → BROKERED path falls back to the
  legacy `(BB_t*)pp` cast anyway (line ~388: `pp_bb = (pp_cfg && pp_cfg->entry) ? … : (BB_t*)pp`).
  CHECK FIRST: does `build_patnd` produce a valid entry for XCAT with a DEFER child? Add a stderr at
  the `pp_cfg->entry` branch to see whether the translator or the legacy cast is taken after the gate fix.
- If the translated graph IS used, then `bb_build_brokered` over a multi-node CAT(POS, DEFER) graph may
  mis-wire the DEFER child (brokered child ABI vs the flat bytes I emitted — the brokered builder wraps
  with `push rbp;mov rbp,rsp` and may expect child boxes to use the rdi=ζ/esi=port/ret C-ABI, NOT the
  flat r10/jmp ABI). If so the DEFER arm needs the BROKERED ABI specifically, not the flat one.
- Verify `rt_defer_match` is actually CALLED (re-add the `PROBE_MV`-style fprintf inside rt_defer_match
  itself). If it never fires, the box isn't reaching the call → build/wiring problem, not a bytes problem.

The cheapest next diagnostic is the two stderr probes (translator-vs-cast branch; rt_defer_match entry).
Those two prints localize the THIRD factor in one build, before any byte-level work.
