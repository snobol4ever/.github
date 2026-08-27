# ARCH-LANGUAGES.md — the seven frontends, one file

**Consolidated 2026-08-27 by `hq_C`** from eight files, under the method in `arch-consolidate-engine`'s LINKS: truth-check every checkable claim in BOTH directions, move-not-rewrite true content, correct false content citing its FINDING, resolve RETIRED NAMES, sweep references.

⛔ **This file is FRONTEND/LANGUAGE truth only.** The shared engine, the register contract, the zeta taxonomy and the x86 substrate live in `ARCH-ENGINE.md` and `RULES.md`. Where a language section used to restate engine law, it now points instead — that restatement is exactly how the eight files drifted apart from each other.

⭐ **Why one file, stated once so it is not re-litigated.** The eight sources disagreed *with each other* about live code, not merely with the tree. Measured during this consolidation: `ARCH-PROLOG.md` said the `bb_node_state_t` snapshot/restore mechanism "is being removed", while the 2026-08-27 CEO audit of `ARCH-x86.md` listed `bb_snapshot_state`/`bb_restore_state` under "verified correct". Both readings were defensible in isolation and the code is unchanged: `emit.h:179,237-238` and `rt_runtime.c:465` are live today. A reader could obey either file and be misinformed by the other.

---

## RETIRED NAMES

Everything a reader might arrive with, and where it went. ⛔ Entries here are **resolutions, not deletions** — a name is listed because something still cites it.

| retired name / path | resolution | evidence |
|---|---|---|
| `ARCH-SNOBOL4.md` · `ARCH-SN4-CONSTANTS.md` · `ARCH-ICON.md` · `ARCH-PROLOG.md` · `ARCH-PROLOG-DESCR-ZETAS-hq_C.md` · `ARCH-SNOCONE.md` · `ARCH-REBUS.md` · `ARCH-C.md` | **this file** | consolidated 2026-08-27 |
| `src/runtime/interp/pl_runtime.{c,h}` | **gone from the tree.** `pl_choice` now lives in `src/lower/lower_prolog.c` — the choice-point mechanism moved into the lowerer | verified: no `pl_runtime.*` under `SCRIP/`; `grep -rl pl_choice src/` → `src/lower/lower_prolog.c` |
| `SCRIP/archive/frontend/prolog/prolog_emit.c` | **not in this root** — lives at `one4all/archive/frontend/prolog/prolog_emit.c` (ceo's root) | matches the 2026-08-27 CEO x86/Prolog audit |
| `SCRIP/doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md` | **`SCRIP/docs/`** — one-letter path error, the file is present | `ls SCRIP/docs/` |
| `GOAL-PROLOG-BB.md` | **`GOAL-PROLOG-100.md`** (one GOAL file per language) | `ls .github/GOAL-PROLOG*` |
| `x86_r12_modrm` | **`x86_frame_modrm`** | zero hits for the old name; new name live in `src/templates/x86/x86_asm.h` |
| `ZC_FRAME_R12` accessor arm | **genuinely deleted.** Its only two survivors are comments *documenting* the deletion (`rtx_match.S:863`, `rtx_abi.inc:17`) | ⭐ checked because a raw grep count reads as "still present" — it is not |
| flat `src/templates/*.cpp` | **re-gridded** into `bb/` (137) · `x86/` (2) · `xa/` (19); zero top-level `.cpp` | ⚠️ the 2026-08-27 CEO x86/Prolog audit's own context line says "no `xa/` subdir" — that line went stale within hours of being written; the ICON audit is the correct one |
| `src/machine/` | **does not exist** | ⛔ still named in per-root `CLAUDE.md` digests, which are untracked and cannot be updated by a commit here |
| `corpus/programs/snobol4/demo/beauty_c/` | **absent** — no `beauty_c` directory exists anywhere in `corpus/`. Live relatives: `corpus/demo/snobol4/beauty`, `corpus/tests/snobol4/beauty_suite`, `corpus/tests/snobol4/smoke/beauty_compiled.sno` | ⚠️ and `corpus/programs/` is ruled non-test material entirely (Lon 2026-08-27, `RULES.md:55`) |

---

## REBUS

Frontend: REBUS → shared IR (`EXPR_t`/`STMT_t`). See `ARCH-ENGINE.md`.

*(Absorbed whole from `ARCH-REBUS.md`, which was three lines and carried no checkable claim beyond the IR types and the cross-reference — both verified.)*

## C backend

Backend: C source output. **Status: inactive** — `scrip-cc` fails on `word*`/`pat_alt_commit`. Not maintained; no active goals.

*(Absorbed whole from `ARCH-C.md`. ⚠️ Status is carried forward as written and was NOT re-measured — the row's method requires truth-checks on live mechanisms, and an explicitly-inactive backend has none. Anyone reviving it re-derives the failure first.)*

---

## ICON

Frontend: Icon → shared IR. See `ARCH-ENGINE.md`.

### Execution model — MOVED UNCHANGED (verified)
Icon is goal-directed: every expression **Succeeds** (γ, may resume for more) or **Fails** (ω). That IS the Byrd-box four-port model — **α** proceed · **β** recede · **γ** succeed · **ω** concede. Icon uses `BB_PUMP` (generate until ω); SNOBOL4 uses `BB_SCAN` (try each cursor position).

**NO SOFTWARE VALUE STACK** (GROUND ZERO 3; renamed from "STACKLESS" — that name is VOID per Lon 2026-08-27, `RULES.md`: all three zetas ARE on the stack, and Icon walks the ladder RSP spine → RBP activation frame → root, with γ-SUSPEND-capable graphs keeping ζ in an RBP activation frame). Icon emits **zero** SM opcodes, no software value stack, no r12-TOS, no `rt_push`/`rt_pop`. Each box's value lives in a flat per-box DATA slot; consumers read operand boxes' slots directly (Proebsting: `plus.value ← E1.value + E2.value`). Inter-box transitions are direct `jmp`. Reference embodiment: `corpus/probe/bb/test_icon.c`.
✅ *Spot-checked (RULING-vs-CODE): `grep -c 'SM_' src/lower/lower_icon.c` → **0**. The zero-SM-opcodes ruling holds.*

⛔ **One clause CORRECTED, not moved:** the old text said unbounded backtrack state (ARBNO, recursion) is a *"per-box `.bss` arena by depth"*. That is **wrong twice**, per the 2026-08-27 CEO ICON audit: the state is the **stack-carved** `jcon_value_region` / `zls_g_region()`, folded into `flat_frame_bytes` (`emit.cpp:3308/3414`).

**Relational ops are NOT booleans** — a comparison is a `{0,1}` generator: γ yields a value, ω fails; constructs only choose where γ/ω go (verified against canonical `ocomp.r` and JCON `ir_opfn`).

### Variable model (Lon 2026-06-03) — two backends, switch-selected, BOTH kept
- **OLD** per-procedure frame slots (`g_bb_varslot`) — fast, per-graph namespace.
- **NEW** shared NV dictionary (`NV_GET_fn`/`NV_SET_fn`, the same hash dict as SNOBOL4/Snocone/Rebus) — one cross-language global namespace. Only the GLOBAL arm of `IR_VAR`/`IR_ASSIGN` reroutes; locals stay frame slots. Kept side by side for A/B perf and standalone-Icon compilation. Ladder: `GOAL-ICON-100.md` (GVA superseded NV for native globals; NV remains the reflective/cross-language binding).

### ⛔⛔ REGISTER CONTRACT — REMOVED FROM THIS FILE, NOT MOVED
`ARCH-ICON.md` carried what it called *"the LIVE REGISTER CONTRACT that every BB template (all languages) obeys"* — the file's own stated reason for existing. **It was wrong in five load-bearing specifics** and is not reproduced here. Authority: `FINDING-2026-08-27-ceo-arch-audit-icon-pair-major-drift-register-contract-names-a-frame-base-that-is-not-there.md` and `FINDING-2026-08-27-hq_P-arch-icon-register-contract-describes-a-selector-that-was-eradicated.md`.

**LIES GET CONSEQUENCES — what this one cost, and would have kept costing:** the section taught `emit_jmp_pin_rbp()` (no such symbol — the live pair is `emit_jmp_pin_legacy()`/`emit_rec_pin()`), a per-graph RBP/RSP duality via `x86_fb()` (unconditionally `"rsp"`), and `x86_fb_pinned()` as the selector (a compile-time **constant zero**). ⛔ **A template author obeying it literally emits against a frame base that is not there.** hq_P found it by *complying* with Lon's read-the-ARCH-docs order before starting rung N-2 — the order paid for itself on first use, and the doc it validated against was the thing that was wrong.
✅ **The register contract is ENGINE law, not Icon law.** It belongs in `ARCH-ENGINE.md` / `RULES.md` § BB FRAME-PLACEMENT CRITERION, and having it live in a *language* file is precisely how it drifted unnoticed: nobody auditing the engine looked in the Icon doc.

### String scanning — the ICN-SCAN BB family (verified section, moved untouched)
Canonical set closed: `fstranl.r` any/bal/find/many/match/upto · `fscan.r` move/pos/tab · control `?` live, `?:=`, `=s` sugar.
Two semantic families, **do not blur them**: *position-returners*, δ-untouched — `any`/`match`/`many` are `{0,1}`; `upto`/`find`/`bal` are `{*}` generators (suspend each position, β re-pumps via `bb_to`). *Cursor-movers*, reversed-on-resume — `tab`/`move` write δ and restore the saved δ on β then fail; `pos` is a stateless compare. Genuinely different from SNOBOL4 pattern leaves (which thread the cursor); the reuse is the Σ/δ/Δ walk plus the cset test loop.

### Box structure (from `corpus/probe/bb/test_icon.c`, verified present)
```
construct_α: init state; first value; goto γ or ω
construct_β: advance;    next value; goto γ or ω
construct_γ: value ready — wire to caller success
construct_ω: exhausted   — wire to caller fail
```
State lives in the per-α DATA block; CODE is shared.

### JCON reference
`refs/jcon-master/tran/irgen.icn` — 43 `ir_a_*` procedures; `ir_info(start,resume,failure,success)` is the four-port record. Ground truth for every construct's port topology. ⚠️ `SCRIP/refs/` is gitignored and not auto-created — `ls` it before trusting a grep.

### Co-expressions
**LANDED 2026-07-01**, both modes: `create` / `@` / `coret` / `cofail` via pthread + semaphore. C-function Byrd constructs remain banned.
✅ *Spot-checked: `src/runtime/rt/rt_coexpr.c` present, and all four of `bb_create` / `bb_activate` / `bb_coret` / `bb_cofail` present under `src/templates/bb/`.*
