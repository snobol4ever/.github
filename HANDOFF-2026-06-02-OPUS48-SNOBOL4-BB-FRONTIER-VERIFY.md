# HANDOFF — SNOBOL4 BB: VERIFY session, stale-handoff correction + true live frontier

**Author:** Claude Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = `1adcf09` (UNCHANGED — no code touched); `.github` = the commit carrying this file.

This session made **NO code changes**. It oriented from the SPITBOL manual + the goal/rules/handoffs, VERIFIED the
live state against the actual test suite, and found that the recent x86()-revamp handoffs are STALE — their
"NEXT STEPS" list items that subsequent sessions already completed. The deliverable is the corrected frontier
(this file + the dated VERIFY block at the top of `GOAL-SNOBOL4-BB.md`), so the next session starts on real work
instead of re-confirming finished work (which is what consuming the stale handoffs led me to do first).

---

## 1. Why this handoff exists — the stale-handoff trap

Reading V3-KEYSTONE, V4-ABORT-TAB-ATP, and BB-VAR (all 2026-06-02, earlier) as the live frontier is WRONG. I
verified by reading the actual `src/emitter/BB_templates/*.cpp` and `emit_core.c`:

- **Every loop-free + single-loop SNOBOL4 box is already x86()-converted** on the ratified registers
  (Σ=r13 / δ=r14 / Δ=r15 / ζ=r12), pBB-free, parameterless dispatch:
  `bb_pat_abort`, `bb_pat_tab` (TAB+RTAB), `bb_pat_atp`, `bb_pat_pos`, `bb_pat_span`, `bb_pat_len`, `bb_pat_rem`,
  `bb_pat_any`, `bb_pat_notany`, `bb_pat_arb`, `bb_pat_defer`, `bb_pat_break` (BREAK + BREAKX, internal labels
  L0..L3), `bb_pat_fence` (niladic cursor-guard), `bb_lit`, `bb_lit_scalar`, `bb_var` (SNO pass-through + ICN
  16-byte DESCR slot-copy).
- **The variable-length define/jmp-pair loop — flagged "STILL OPEN across all four sessions" in V3/V4 — IS
  SOLVED.** `x86_pair_loop()` lives in `src/emitter/BB_templates/x86_asm.h` (~line 416). It walks the
  driver-supplied `g_emit.xa_bb_emit_pair_n/_define/_jmp` arrays and emits, per pair: BINARY `E <idx>` (define
  the driver's label) and `0xE9` + `F <idx>` (rel32 patch to the driver's jmp target); TEXT prints the named
  label / `jmp name`. The walker `bb_emit_x86` handles the new `E`/`F` tags (alongside `L`/`J`/`D`). Both
  `bb_pat_cat` and `bb_pat_alt` are now just `return x86_pair_loop();`.
- **OP-A-PROMOTE landed:** `emit_core.c:389` sets `g_emit.op_a_slot = nd->α ? bb_slot_get(nd->α) : -1;` and the
  `bb_gvar_assign` int-binop arm reads it via `FRQ(slot)`. Result: **`OUTPUT = 2 + 3` PASSES mode-3** — the
  `arith` smoke is GREEN (it was the prior frontier; it has moved).

Lesson for the next author: **derive the frontier from failing tests, not from the previous handoff's NEXT list.**
`bash scripts/test_smoke_snobol4.sh` then decode any `walk_bb_node: kind=N unhandled` with a tiny probe
(`printf` the `IR_*` enum value from `src/contracts/IR.h`).

## 2. True live mode-3 frontier (failing smokes; IR kinds decoded)

`./scrip --run` smoke results this session: output✅ arith✅ concat✗ pattern✗ goto_s✗ define✗.

| Smoke | Program | Failing IR kind | What it needs |
|-------|---------|-----------------|---------------|
| `concat` | `OUTPUT = 'ab' 'cd'` | **10 = IR_SEQ** | VALUE-side STITCH_SEQ (≠ IR_PAT_CAT) |
| `pattern` | `S = 'abc'; S 'b' = 'X'; OUTPUT = S` | **28 = IR_SCAN** | ch.18 unanchored outer match loop |
| `goto_s` | `'x' 'x' :S(HIT)` | **28 = IR_SCAN** | same |
| `define` | `DEFINE('DOUBLE(X)')` + call + `RETURN` | (empty out) | DEFINE reg + SNOBOL4 call frame + RETURN |

Decode method used: compiled a one-liner including `IR.h` → `IR_SEQ=10`, `IR_SCAN=28`, `IR_SUSPEND=26`,
`IR_PROC=27` (the enum is 0-based from `IR_LIT_I`, no leading sentinel).

## 3. NEXT (smallest real unit) — IR_SEQ value-concatenation, grounded

**Semantics (SPITBOL Manual, ch.3 "Simple Operators", p.18):** concatenation is the juxtaposition operator (blank/
tab between operands; the whitespace is the operator and is NOT in the result). The result is the right string
appended to the end of the left; both operands are unchanged; a fresh third string emerges. Non-string operands
are CONVERTED to string form first (integer `7`→`"7"`, real→`"0.666..."`). This matches the oracle exactly.

**Oracle (`src/interp/IR_interp.c:1978`, the `bb->dval == 1.0` two-operand branch):** reset+interp the left
sub-graph (`lblk = (IR_graph_t*)bb->counter`), fail→ω; reset+interp the right (`rblk = bb->ival`), fail→ω;
`binop_apply(BINOP_CONCAT, lv, rv)`; result→`bb->value`→γ. So IR_SEQ is a VALUE COMBINATOR over two child graphs,
not a leaf.

**Plan (mode-3 BINARY first, follow the SPAN/ζ-frame + keystone idioms):**
1. Give `rt_concat` a real two-arg string implementation (it is currently `STACKLESS_ABORT("rt_concat")` at
   `src/runtime/rt/rt.c:791`). Decide the calling convention that fits the ζ-frame model — e.g.
   `rt_concat_str(const char *l, const char *r) -> const char *` (GC-allocated), or operate on DESCR slots.
   Ground the coercion in `binop_apply(BINOP_CONCAT,…)` / `str_concat_d` (`builtins/gen_value.h`).
2. IR_SEQ box: emit left child graph (result → its ζ-slot), right child graph (→ ζ-slot), load both into arg
   regs, `call rt_concat*` (RO call like ATP/SPAN's strchr — `push/pop r10`, keep rsp 16-aligned), store the
   returned pointer into THIS box's own ζ-slot (`bb_slot_claim`), → γ; β → ω (single-shot value).
3. Replace the `bb_gvar_assign` concat-arm bomb ("relocatable form is STITCH_SEQ") with a store: read the IR_SEQ
   result slot via `FRQ`/`FR`, `lea rdi,[rip+dstname]`, `call rt_gvar_assign_str` (or a var-from-slot variant),
   → γ; def β; → ω.
4. The child-graph emission likely reuses the `x86_pair_loop()` / `xa_bb_emit_pair_*` machinery the pattern
   combinators use (the driver already marshals define/jmp pairs for sequenced sub-graphs) — check
   `emit_bb.c` `walk_bb_flat` IR_SEQ + `flat_drive_*` to see what the driver already supplies before inventing.
5. Gate: `concat` smoke green (m2 is already the oracle), plus the standing set in §4. Byte-verify any NEW encoder
   vs `as` BEFORE use (RULES). Keep the box pBB-free + `_.node`-free.

THEN: **IR_SCAN** (the ch.18 unanchored outer loop — `bb_match` + `bb_sno_subject` slot, BB-VAR handoff NEXT(2);
the long pole; follow `bb_pat_span` + the internal-label keystone). THEN **define** (call frame + RETURN).

## 4. Gate state (GREEN; == baseline `1adcf09`, build `make scrip` then `make libscrip_rt`)
- SNOBOL4 m2 **7/7 HARD**; Icon m2 **12/12 HARD** (mode-3 Icon 3/12, mode-3 SNOBOL4 2/6 — both tracked floors,
  the box-by-box climb).
- `prove_lower2` PASS; `no_bb_bin_t` **0**; `audit_concurrency_invariants` OK (FACT RULES byte-identical ×3 —
  this session touched ONLY `.github` docs, so the audit pins LOWER `5097ed94` / EMITTER `307534d6` are
  untouched); `test_gate_sm_dead` **0**; `g_vstack` **3** (the known VSX-scaffolding baseline in rt.c/rt.h,
  target 0, NOT a regression).
- `util_template_purity_audit` 1 (pre-existing Icon `bb_every`) and `test_gate_template_medium_invisible` 1
  (pre-existing Icon `bb_unop`) — both informational WIP baselines, owned by the Icon lane.
- PAT-BB probes `scripts/test_sno_pat_bb_probe.sh` are 0/3 but FAIL AT COMPILE (`undefined reference to
  sno_flat_chain_build` — the symbol was renamed to `descr_flat_chain_build`). The probe `.c` files in
  `test/snobol4/pat_bb/` still call the old name. Pre-existing; a trivial future fix (s/sno_flat_chain_build/
  descr_flat_chain_build/ in the three probes), not a code regression.

## 5. Divvy-up (unchanged; this session = SNOBOL4, verify-only)
- **SNOBOL4 (live frontier):** IR_SEQ value-concat → IR_SCAN (`bb_match`+`bb_sno_subject`) → `define`/call-frame;
  then `bb_capture`/`bb_arbno` for pattern-with-replacement. All leaf/single-loop/combinator-pair boxes DONE.
- **Icon:** bb_iterate, bb_binop_gen, bb_upto, bb_to/to_by, bb_seq, bb_every, bb_suspend, bb_unop medium-branch,
  bb_assign (Icon var-store).
- **Prolog:** bb_builtin, bb_goal, bb_choice, bb_disj, bb_unify, bb_catch.
- **Raku:** bb_nfa leaves.

Each session edits only its own boxes; `x86_asm.h` is shared but additive; `git pull --rebase` before push.

## 6. Handoff sequence (RULES.md) — done this session
Working tree was clean (no SCRIP changes), so nothing to commit in the code repo. Marked the GOAL watermark
(single source of truth) with the dated VERIFY block; did NOT edit the PLAN.md table (routine handoff); committed
`.github` (this file + the GOAL block); `git pull --rebase && git push`. ENV: `apt-get install -y libgc-dev`
(`core.h` / `raku_nfa_bb.c` include `<gc/gc.h>`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
