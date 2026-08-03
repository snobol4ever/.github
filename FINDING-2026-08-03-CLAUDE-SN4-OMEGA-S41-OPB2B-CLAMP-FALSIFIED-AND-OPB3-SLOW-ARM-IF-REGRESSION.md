# FINDING-2026-08-03-CLAUDE-SN4-OMEGA-S41 — O-PB-2b CLAMP FALSIFIED AND O-PB-3 SLOW-ARM IF REGRESSION

**Session:** s41 (2026-08-03, Sonnet). **Parent:** SCRIP `8ec8dfa2` (post ALPHA ZD-PATREF inflation fix, pulled during session). **SCRIP code changes this session: ZERO** — both experiments reverted after falsification. `.github` receives this FINDING + cursor update only.

---

## FINDING 1 — O-PB-2b CROSS-STMT CLAMP IS VACUOUS (11 regressions)

**Hypothesis:** The 224B residual Kc inflation (after O-PB-2a) is cross-statement closure contamination that can be eliminated by clamping `umin` to `run_umin` (min zls offset of this run's K=0 members). Logic: blob-closure members from stmt1 are pulled into stmt2's `cm[]` via PATREF operand walk, dragging umin to 0.

**Experiment:** Added `run_umin` clamp in `zd_plan`'s Kc span walk, behind `SCRIP_ZD_GAP_CLAMP=1`. Measured: stmt2 Kc 480→224B (correct direction). Ran full 318 crosscheck with DYNARM=7 PATREF=1 CLAMP=1.

**Result: 11 regressions** in the arbno/fence/defer family (119, 121, 123, 125, 129, 148, 149, 151, 162, 173, 182). Reverted immediately.

**Root cause of falsification:** The blob-closure members whose zls offsets appear below run_umin are NOT spurious foreign-statement slots — they are **genuine accesses** via PATREF runtime indirection. A PATREF that invokes pattern `T` (defined by stmt1) reads T's zls slots at those lower offsets through the stored-pattern mechanism. The `cm[]` closure walk correctly includes them; their addresses are real. Clamping `umin` above them makes the claim too small to cover what the runtime actually reads, causing crashes.

**Architectural verdict:** The 224B residual is NOT cross-statement contamination. It is the real size of what PATREF-bearing stmt2 needs to reference. This is **ALPHA terrain** (zvo_resolve closure scoping). OMEGA cannot eliminate it without coordination on how the closure walk scopes per-statement ownership. The PATREF seal (graph-scope decline for graphs containing PATREF/DEFER) correctly keeps ZW frame from arming where these live accesses would conflict.

**Gate at default (PATREF gate off):** BY SET identical to bracket — 282P/24F/11T m3, 274P/32F/10T m4.

---

## FINDING 2 — O-PB-3 op_zres ARM CAUSES REGRESSION VIA IF(!op_zres) SLOW-ARM WRAPPING

**Hypothesis:** Adding an `op_zres` arm to `bb_match_defer.cpp` — routing null-fn-ptr to ω when ZD-armed, and wrapping the slow arm in `IF(!_.op_zres, ...)` — correctly skips the FRAMED slow path for K=0 transfer boxes.

**Experiment v1:** `IF(_.op_zres, x86("jz", PORT_OMEGA))` + `IF(!_.op_zres, x86("jz", "L0"))` + full slow arm in `IF(!_.op_zres, ...)`. Result: W02/W03 and recursive pattern regressions. The nested `bb_glue_pass_wires(7, 8)` inside `IF(!_.op_zres, ...)` was suspected.

**Experiment v2:** Keep `x86("jz", "L0")` unconditional, keep L0 label always, add `IF(_.op_zres, x86_omega())` AT L0, wrap only the slow-arm body in `IF(!_.op_zres, ...)`. Result: still regressions — W02_seq_basic, W02_seq_nested (value-spine programs with NO DEFER nodes).

**Confirmed by stash A/B:** W02 PASSES with the original binary under DYNARM=7+PATREF=1. The arm IS the regression source.

**Root cause diagnosis (not fully closed):** The `IF(!_.op_zres, ...)` wrapper changes something in the side-effect ordering of label registration or wire-pair tracking even for the `op_zres=0` (non-ZD) case. The `IF` macro is `(c) ? (expr) : std::string()` — at **runtime** this is a branch, so side effects inside the false branch should not fire. However, the behavior of `bb_glue_pass_wires(7, 8)` or the string-label system under nested `IF` calls may be registering/flushing label pairs in a different order that shifts internal state even for programs that never touch `bb_match_defer` — possibly through the global flush state in `bb_emit_x86`.

**The correct approach for O-PB-3 (for next session):** Do NOT use `IF(!_.op_zres, ...)` to wrap the slow arm. Instead, use a runtime early-return at the C function level: move the slow arm into a helper or guard it with a `if (_.op_zres) return ...;` at the start of the function body before the concatenation chain, completely outside the `+` expression. This avoids any label/wire side-effect ordering issue. Per R8 (side effects only in `bb_emit_x86`), this early-return pattern is the correct form.

**Gate at default:** BY SET identical to bracket after revert.

---

## SESSION MEASUREMENTS

- Bracket at session start: m3 282P/24F/11T · m4 274P/32F/10T (matches s40 cursor exactly).
- ALPHA `8ec8dfa2` pulled during session (ZD-PATREF inflation fix — blob-closure SPAN exclusion + stale-rpos cross-contamination fix). No gate impact measured at default settings.
- All OMEGA code changes REVERTED. SCRIP HEAD at handoff = `8ec8dfa2` (ALPHA's commit, OMEGA added nothing).

---

## NEXT (ordered, for O-PB-3 in next session)

1. **O-PB-3 correct form:** In `bb_match_defer.cpp`, add a C-level guard at function start: `if (_.op_zres) return x86_alpha() + <fast-arm-only> + x86_beta();` — or equivalently, build two separate return paths using a local `std::string` variable rather than nested `IF()` macros. The fast arm (rax != 0 → `bb_glue_pass_wires(4,5)`, L4/L5 exits) is already correct for K=0. The null-fn-ptr case routes to `x86_omega()` directly. No slow arm emitted. Gate: BY SET identical at default; WITH DYNARM=7 PATREF=1 must be zero P→F vs pre-arm baseline (`nopatref.tsv` shape: 277P/29F/11T m3, 268P/38F/10T m4).
2. **O-PB-3 flip:** Once arm is green, flip `SCRIP_ZD_PATREF` default ON (own commit, own gate).
3. **O-PB-4:** ARBNO/FENCE1 own frames — nested `push rbp; mov rbp,rsp` at iteration/commit entry, `mov rsp,rbp; pop rbp` at success exit. Independent of MATCH_BEGIN's frame.
4. **O-9 RECONCILIATION:** Wait on ALPHA A-9 (already landed at `7f92a607`). Pull-rebase, run §7 completion tests.
