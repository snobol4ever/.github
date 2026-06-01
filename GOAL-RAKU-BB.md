# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

## ⏸ ON HOLD → SPINNING UP (2026-05-31)

**Lon directive (2026-05-31): Raku is being re-prioritized as the FOURTH concurrent BB session,
peer to SNOBOL4 / Icon / Prolog.** This file was revamped to match the other three musketeers:
same three FACT RULES (byte-identical bodies), same MANDATORY-READ pipeline, same post-SMX-4
reality (no Stack Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; the BB run-path
via `bb_exec_once`). The prior ON-HOLD content (SM-era `BB_*`/`SM_*` vocabulary, `BB.h`,
`SM_BB_INVOKE`) is preserved verbatim under **APPENDIX A — PRE-SMX-4 RAKU STATE (historical)**
at the foot of this file; its numbers are NOT reachable today (the SM engine it ran on was
deleted by SMX-4) and must not be cited as live.

**LANGUAGE LIFE (per the correction in GOAL-SNOBOL4-BB, Lon 2026-05-31):** "tombstoned" was
over-broad. SMX-4 deleted the SM EXECUTION BACKEND, not any language. After the AST and before
the IR — exactly where `lower()` sits — ALL SIX languages are alive. LIVE: SNOBOL4, Icon, Prolog.
VICARIOUS (through SNOBOL4): Snocone, Rebus. Raku was the ONE flagged DEAD only in the sense of
being ON HOLD — it still parses + builds AST; what is NOT yet wired is Raku *lowering* onto the
unified `lower.c` four-port IR + *execution* over the BB run-path. **That wiring is this goal.**

**Spin-up entry rung:** RK-LOWER-0 (below) — first Raku arm into the unified `lower.c`, proven via
`scripts/prove_lower2.sh` (topology), then a mode-2 `say("hello")` through `bb_exec_once`.

---

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

> **⚠ FOURTH-MUSKETEER NOTE (Raku spin-up, 2026-05-31).** The FACT RULE body above is reproduced
> **byte-identical** to the three existing carriers so its md5 (`5097ed94`) still matches — Raku
> joins as a fourth carrier of the SAME block. The roster line still names three files and the body
> still says "three" by design: expanding "three → four" (roster + every "three"/"all three") is a
> **lockstep edit of all four GOAL files in ONE commit** per clause 5, to be performed when the Raku
> session is actually fired up, not piecemeal here. Until then Raku obeys the rule exactly as written
> (its `cx.lang==IR_LANG_RKU` arms go INSIDE existing cases; missing arms fall to `lower_unhandled`).

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `307534d6`); Raku is a fourth carrier.
> Raku's emitter boxes live under their own `bb_rk_*` prefix (e.g. `bb_rk_seq.cpp`, `bb_rk_jct.cpp`,
> `bb_rk_nfa_*.cpp`) so clause 3's "edit only your own boxes" holds with zero overlap onto the
> SNOBOL/Prolog/Icon prefixes. The "three → four" roster expansion is the same lockstep edit noted above.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `8255d653`). Raku is a Seq/generator
> language, NOT a subject-scanning pattern language at the top level: the Σ/δ/Δ subject triad is used
> ONLY inside the isolated `IR_NFA_*` regex slab (RK-NFA), where Σ=subject base, δ=match pos, Δ=slen —
> exactly the pattern-lang use. Raku's generative core (Seq pull) uses ζ (r12) for the per-box RW frame
> (resume cursors / counters) and the SysV caller-saved scratch for transport; it does not claim the
> subject triad outside regex. Any change to this table is the lockstep all-files edit per the rule.

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline (post-SMX-4 — the SM engine is GONE; this is the BB run-path all four languages share):**
```
Raku source → raku.l / raku.y → tree_t* (TT_* AST)
    → src/lower/lower.c  lower2()  [cx.lang = IR_LANG_RKU, role VALUE]
        → IR_t four-port graph (alpha/beta/gamma/omega; ports are POINTERS → goto-chains collapse)
    → [mode 2] bb_exec.c: bb_exec_once(entry) / bb_exec_resume   (correctness ORACLE)
    → [mode 3] --run native runner → SM/BB/XA template BINARY arms → sealed RX → jump in
    → [mode 4] --compile --target=x86 → template TEXT arms → as → gcc -no-pie -lscrip_rt → run
```

- **Mode 2 (`--interp`):** `bb_exec_once` C oracle over the lowered `IR_t` graph. The reference.
- **Mode 3 (`--run`):** native runner → `{BB,SM,XA}_templates/*.cpp` MEDIUM_BINARY arms. (For SNOBOL4
  this AOT path is not yet rebuilt; for Raku it does not exist yet either — see the rungs.)
- **Mode 4 (`--compile`):** template MEDIUM_TEXT arms → GAS → gcc link → run the binary.

> **⛔ TESTING DIRECTIVE (mirrors the other three GOAL files, Lon 2026-05-31) — ALWAYS RUN ALL THREE
> MODES.** Every time you test Raku, exercise mode 2 (`--interp`), mode 3 (`--run`), AND mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Mode 2 is the **HARD gate**
> (exit 0 requires mode-2 all-pass); modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked
> with `MODE3_MIN`/`MODE4_MIN` PASS floors, default 0) so the full native picture is always visible.
> Never report a mode-2 number alone. Raise the floors as 3/4 come back so regressions in them also fail.

**Mandatory reads, in order, every Raku session:**
1. `GOAL-ICON-BB.md` (the live ground-zero goal + the canonical four-port generator model Raku REUSES).
2. `RULES.md` in full (No C Byrd boxes · TEMPLATE-PURITY · ONE x86 PRODUCER · stub LOUD via `bomb_bytes()`
   · X86 ONLY · MODE PURITY — no silent cross-mode fallback / no silent eps substitution).
3. This file. Find the first incomplete `- [ ]` rung in the ladder.
4. `GOAL-RAKU-FRONTEND.md` (parser/lexer state) and `GOAL-PST-RAKU.md` (pure-syntax-tree track) if touching the frontend.
5. If touching corpus → `CORPUS-LOCATIONS.md`. If MODE3/4-EMIT → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY. No `rt_*`/`raku_*` port-logic helpers; conversion/effect helpers via `@PLT` (mode-4) or absolute `movabs+call` (mode-3) are fine.

---

## The insight (Raku is a Seq language → ONE four-port pull protocol)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, the
`…` sequence operator, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port
pull protocol (yield-one-at-β, identical to Icon's generator `SUSPEND`/`EVERY` PUMP) suffices; every
generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on the
SHARED Icon generator kinds — Raku adds almost no new IR kinds, it REUSES Icon's.

## Port semantics (identical to Icon generators — REUSE, do not reinvent)

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = the Icon generator PUMP (`IR_EVERY` / the `IR_*` resumable family). NOT Prolog's once-driver.

## Moves to BB (shared IR) vs stays eager

**MOVES (goal-directed, REUSE shared Icon IR kinds — Raku adds `cx.lang==IR_LANG_RKU` arms INSIDE the existing cases):**

| Raku construct | shared IR kind (Icon's) | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b … $c` | `IR_TO` / `IR_TO_BY` | RK-LOWER-1 |
| `gather { … take … }`, `…` operator | `IR_*` SUSPEND + PUMP (Icon generator) | RK-LOWER-2 (keystone) |
| lazy `map` / `grep` | `IR_*` ITERATE consumer (eager-drain) | RK-LOWER-3 |
| junctions `any`/`all`/`one`/`none`, infix bar/amp | `IR_ALT` + Bool-collapse | RK-LOWER-4 |

**STAYS eager (lower to straight-line `IR_*`, no generator):** scalar builtins, `say`/`print`,
arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**REGEX / GRAMMAR (RK-NFA rungs):** regex backtracking onto an ISOLATED `IR_NFA_*` family (NOT
SNOBOL4's pattern opcodes — isolation decision below). Grammar/LTM deferred to Phase 2.

---

## Rung ladder (REVAMPED for the unified `lower.c` + BB run-path)

All prior `BB_*`/`SM_*` rungs are SUPERSEDED by these `lower.c`-based rungs. The old rungs' *findings*
(what worked semantically in mode-2/mode-4 on the SM engine) are preserved in APPENDIX A as design input,
but the *mechanism* (SM opcodes, `SM_BB_INVOKE`, `BB.h`) is gone. Each rung: lower a `cx.lang==IR_LANG_RKU`
arm in `lower.c`, prove TOPOLOGY via `scripts/prove_lower2.sh` (append Raku cases in the RAKU section), then
prove BEHAVIOR via mode-2 `bb_exec_once`, then (later) the mode-3/4 template arms.

- [x] **RK-LOWER-0 — spin-up: first Raku arm + `say("hello")`.** ✅ DONE (2026-05-31, Opus). Add `IR_LANG_RKU` to the lang enum if
  absent; route the Raku frontend through `lower2_value_entry`. Lower `say(STR)` / `print(STR)` via the
  SHARED `wire_det_builtin1` (the same role-agnostic builtin-call wirer Icon `write` and Prolog `write`
  already use — another sharing seam). Prove: `prove_lower2.sh` gains a RAKU `say("hello")` case (node count
  + gamma/omega); mode-2 `say("hello world")` → one record. Gate suite green (below). **This is the entry rung.**
- [x] **RK-LOWER-1 — lazy range → `IR_TO`/`IR_TO_BY`.** ✅ DONE (2026-05-31, Opus). `for $a..$b { }` and `$a,$b … $c`. REUSE Icon's
  `IR_TO`/`IR_TO_BY` case; add the Raku arm inside it (range sigil/step semantics per docs.raku.org §Range).
  Prove topology + mode-2 `for 1..3 { say $_ }` → 1,2,3.
- [x] **RK-LOWER-2 — KEYSTONE: lazy Seq `gather`/`take` → resumable generator PUMP.** ✅ DONE (2026-05-31).
  `gather { take E1; take E2; ... }` lowers to a NEW resumable Seq-producer kind `IR_GATHER` (its own resume,
  β=self, exactly like `IR_TO`) realizing the APPENDIX-A `RK-M2-GATHER` spec — counter-as-resume-cursor: yield
  ONE take per (re)entry, walking past the last (or empty gather) → FAIL (Seq drained). Driven by the EXISTING
  generator PUMP via `v_raku_for` (no new pump machinery): reached BOTH as the iterate source of
  `for gather {..} -> $v` (the `TT_EVERY` Raku guard now admits a `TT_GATHER` iterate child) AND as a bare value
  expr (dedicated `TT_GATHER` case, Raku arm; non-Raku → `lower_unhandled`). Take payloads lower into SEPARATE
  value sub-graphs (the SNOBOL4 call-arg idiom — `lower_value_subgraph`, cursor carries `IR_LANG_RKU`); the
  subs-array ptr rides on `IR_GATHER.counter` (now PRESERVED across `bb_reset` — the drain-on-first-entry fix),
  the take COUNT on `.ival`, the resume cursor on `.state`. Mode-2 `for gather { take(10);take(20);take(30) } ->
  $v { say $v }` → `10,20,30,done`. FLAT-take model (corpus/keystone are flat); dynamic-scope takes (inside
  loops/conditionals, the docs.raku.org `factors()` example) are a later refinement on this same node.
- [x] **RK-LOWER-3 — lazy `map`/`grep` as Seq consumers.** ✅ DONE (2026-05-31, Opus). Eager-drain a producer Seq through a
  transform/filter. NEW resumable Seq-consumer kinds `IR_MAP`/`IR_GREP` (own resume, β=self, like `IR_TO`/`IR_GATHER`),
  reached from the Raku arm of the shared `TT_EVERY` (guard now admits `TT_MAP`/`TT_GREP` iterate children) AND a
  dedicated Raku-gated `TT_MAP`/`TT_GREP` case (non-Raku → `lower_unhandled`). SOURCE → its own value sub-graph
  (`lower_value_subgraph`, ptr on `.counter`, preserved across `bb_reset`); closure BODY → second sub-graph (ptr on
  `.ival`); resume cursor on `.state`. Mode-2 exec arm eager-drains SOURCE via the `aggregate_all` idiom
  (`bb_reset`+`bb_exec_once`+`bb_exec_resume`) into a node-keyed `DESCR_t` cache, binds `$_` with `NV_SET_fn` per
  element, runs the closure: map yields the transform; grep keeps the element iff the closure is truthy
  (`binop_apply` rel-fail = false). Semantics per docs.raku.org/routine/{map,grep}. Mode-2:
  `for map { $_ * 2 } 1..3 -> $v` → 2,4,6; `for grep { $_ > 2 } 1..5 -> $v` → 3,4,5; map/grep over `gather` compose.
- [x] **RK-LOWER-4 — junctions `any`/`all`/`one`/`none` + infix bar/amp.** ✅ DONE (2026-05-31, Opus 4.8). Constructor + infix forms share
  ONE lowering (the APPENDIX-A `RK-BB-4a/4b` finding: infix bar/amp build the SAME `TT_FNC` the constructors
  do; same-flavor chains flatten at parse time). Mode-2 collapse via the tagged-junction value; the `IR_ALT`
  fail-chain is the eventual mode-3/4 substrate.
- [ ] **RK-LOWER-5 — eager core onto straight-line IR.** `say`/`print` (done in RK-LOWER-0), arithmetic,
  hash/array element ops, `sort`, `try`/`CATCH`, class/method dispatch — each a deterministic `IR_*` arm
  (beta=omega_in, no generator). Port the APPENDIX-A RK-HASH / RK-IO / RK-EXCEPTIONS / RK-CLASS *semantics*
  onto the four-port IR (they worked on the SM engine; the behaviors are the spec, the SM opcodes are not).
  **5a DONE (2026-05-31, Opus 4.8): read-only value ops** — list construction `(e1,..)`→`__rk_arr`, `@a[i]`→`arr_get`,
  `%h<k>`/`%h{k}`→`hash_get`, membership→`hash_exists`, `sort(@a)`→`array_sort`, plus the `elems`/`reverse`/`join`/
  `sum`/`unique`/`head`/`tail`/`chars`/`length`/`lc`/`uc`/`trim`/`substr`/`index`/`rindex` whitelist — all via the
  SHARED `v_raku_det_call`→`IR_CALL` (dval=2.0, det). **5b STILL OPEN:** mutating ops (`push`/`pop`/`arr_set`/`hash_set`/
  `hash_delete`) need vname-threaded writeback (IR_t is LEAN per PEERS — clean path = pure-variant runtime + `IR_ASSIGN`,
  except `pop` which truly needs vname). **5c:** `try`/`CATCH`/`die` (exception propagation through shared SEQ/sub-call
  exec — FACT-RULE-sensitive). **5d:** class/method/field/new + `say(jct)`/`say(list)` composite output.
- [ ] **RK-EMIT-1..N — mode-3/4 template arms.** Once the lowered Raku arms are mode-2-proven, fill the
  `bb_rk_*.cpp` MEDIUM_BINARY (mode-3) + MEDIUM_TEXT (mode-4) arms, ONE box per file, dispatched from
  `emit_core.c`, per the TEMPLATE-ONLY FACT RULE. Gate each via `--run` / `--compile` corpus delta + the
  emitter purity/byte-identity gates. (Mirrors SNOBOL4's "TOP PRIORITY: complete all pattern BB BINARY/TEXT
  arms" rung — Raku's is the generator + junction + NFA box set.)
  - **RK-EMIT-1/2/3 LANDED (2026-05-31, Opus 4.8) — m3 0→16/22, m4 0→16/22 (Icon 9/9/9 + SNOBOL4 7/7 m2 intact):**
    Raku now rides **Icon's existing LOWER-direct native driver** (scrip.c: `is_raku` flag → the `is_icon || is_raku`
    mode-3 `--run` and mode-4 `--compile` branches). The prior "blocked on the severed `[SBB]` driver" diagnosis was
    WRONG: `.raku` simply set no routing flag, so it fell into the SNOBOL `[SBB]` abort. Raku's IR is built from Icon's
    kinds, so Icon's `icn_flat_chain_build` + the SHARED `bb_*` templates emit it. **0 new `bb_rk_*` files** — instead
    extended SHARED templates: `bb_call.cpp` (dval==2.0 general builtin call → marshal arg-leaf DESCRs into a per-call
    ζ-frame vector → new `rt_rk_call_arr`), `bb_lit_scalar.cpp` (`IR_LIT_S` → slot), `bb_assign.cpp` (producer guard
    widened to `IR_LIT_S`/`IR_CALL`), `bb_binop.cpp` (junction-collapse relop on `__rk_jct_` operands → new
    `rt_rk_jct_relop`), and `emit_bb.c` (`IR_CONJ` flat-chain pass-through so statements after an `if`/block aren't
    dropped; `icn_chain_arity` returns 0 for dval==2.0 calls; string-literal concat duplicate-label short-circuit).
    Runtime trampolines in `gen_runtime.c` reuse the mode-2 `try_call_builtin_by_name`/`junction_collapse` ⇒ m2==m3==m4,
    NO bb-walking at m3/m4 run time, NO value stack (per-call arg vector is the sanctioned ARBNO-style frame array).
  - **STILL FAILING (5/22 m3 & m4, was 6 — `jct_nested` LANDED 2026-06-01 via RK-EMIT-2-NEST recursive arg marshalling):**
    the 5 generators `gather_take`/`map_range`/
    `grep_range`/`map_over_gather`/`grep_over_gather` (need NEW `bb_rk_gather`/`bb_rk_map`/`bb_rk_grep` templates for
    `IR_GATHER`/`IR_MAP`/`IR_GREP` resumable-pump boxes — the largest remaining lift, genuinely Raku-only `bb_rk_*`).

### RK-NFA — Raku regex onto an ISOLATED `IR_NFA_*` family

**Decision (locked w/ Lon, 2026-05-29 — STILL HOLDS post-SMX-4, renamed `BB_NFA_*`→`IR_NFA_*`):** build a
NEW isolated `IR_NFA_*` opcode family; do NOT reuse SNOBOL4's shared pattern opcodes. Reasons: (1) isolation
removes the chief regression risk (shared templates would let a Raku bug hit SNOBOL4's hot path); (2) NFA
kinds are the more-generic basis (SNOBOL4's `SPAN`/`BREAK` derive from `CLASS+`); (3) captures genuinely
diverge — SNOBOL4 `$`/`.` write GLOBALS, Raku `$0`/`$<n>` are scoped Match-object captures; (4) the mode-2
SNOBOL4 matcher is SNOBOL4-runtime-bound. Convergence into language-agnostic `IR_MATCH_*` is DEFERRED
(RK-NFA-CONV) only where byte+semantics are identical; `SPLIT` + captures stay separate.

**Raku semantics (verified docs.raku.org + S05):** HYBRID — quantifiers / `||` (ordered) / `regex`-decl /
subrule-retry = backtracking (→ `IR_NFA_*`); `|` = declarative LONGEST-TOKEN + proto = parallel/forward
(→ Phase 2). Grammars are the SAME engine (namespace of `token`/`rule`/`regex`; subrule `<name>` = a
backtrackable method call). Family 1:1 from `Nfa_kind`: `IR_NFA_{CHAR,ANY,CLASS,SPLIT,EPS,BOL,EOL,CAP_OPEN,
CAP_CLOSE,ACCEPT}` (Phase 1); `{ASSERT,PRED,SUBCALL,LTM}` (Phase 2). Driver = the generator PUMP, β = the
next-state / backtrack edge.

> **⛔ TIER-SEAM DECISION (Lon + Claude, 2026-05-29 — KEEP).** Leaf single-pattern BB *emission* is
> ceremony, not value: 9 of the 10 NFA kinds don't backtrack (single-shot leaves whose β just forwards to ω);
> only SPLIT is a real choice point. The C matcher (`raku_nfa_*`, `nfa_bt`) already returns correct verdicts
> in all modes. **WHERE BBs EARN THEIR KEEP = the subrule seam:** `<name>` is a backtrackable method call that
> must yield its NEXT match recursively while building the Match tree — exactly resume-and-yield-next across a
> call boundary, the job the SHARED four-port generators already do. So Raku regex routes leaf matching through
> the (kept-but-dormant) isolated NFA slab and routes subrule/grammar backtracking through the generator PUMP —
> NOT a new NFA-internal subcall opcode. Do not re-open leaf-emission grinding.

- [ ] **RK-NFA-1 — isolated `IR_NFA_*` enum + graph builder + mode-2 backtracking walk.** (APPENDIX-A RK-NFA-1a..1e
  landed this on the SM-era enum/builder; re-home onto the `IR_*` taxonomy: enum block in `IR.h`, `raku_nfa_to_bb`
  → `IR_graph_t*`, isolated `raku_nfa_bb_match`, oracle vs parallel NFA on L1-L15.)
- [ ] **RK-NFA-2 — mode-2 csets + anchors + ordered alt** (L4-L12).
- [ ] **RK-NFA-3 — mode-2 captures** `$0`/`$1`/`$<name>` → `IR_NFA_CAP_*` (L13-L15).
- [ ] **RK-NFA-4/5 — mode-3/4 emission. ⏸ leaf-emission SHELVED** per the tier-seam decision; default `~~`
  stays on the C matcher. The dormant leaf templates stay behind a flag; `bb_nfa_split` is NOT written.
- [ ] **RK-GRAM-3 (THE SEAM) — subrule `<name>` backtracking via the generator PUMP.** The real BB destination
  and the #1 grammar goal: resume-and-yield-next across the subrule call boundary, Match-tree build. Routes
  through `IR_*` SUSPEND/ALT/PUMP (already exist), NOT a new opcode.
- [ ] **RK-GRAM-4..6 — LTM + proto dispatch; actions + Match tree + captures; convergence/control/adverbs.** (Deferred.)
- [ ] **RK-NFA-CONV (DEFERRED) — collapse `IR_NFA_CHAR/CLASS/ANY/BOL/EOL` ↔ SNOBOL4 `IR_PAT_*` into `IR_MATCH_*`**
  only where byte+semantics identical; SPLIT + captures stay separate.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh            # or: make -j4 scrip   (rc=0; seed `scrip --interp` → hello)
make libscrip_rt                       # rc=0
```

## Gates (run ALL THREE MODES per the TESTING DIRECTIVE; behavioral gates stay INVARIANT under byte-neutral change)

```bash
make scrip                                    # rc=0
make libscrip_rt                              # rc=0
bash scripts/prove_lower2.sh                  # topology — Raku cases ADDITIVE in the RAKU section; stays green
bash scripts/test_smoke_raku.sh               # mode 2 HARD; m3/m4 tracked (floors MODE3_MIN/MODE4_MIN)
bash scripts/test_smoke_icon.sh               # m2 6/6 (HARD) — REUSED generator kinds; must not regress
bash scripts/test_smoke_snobol4.sh            # m2 7/7 (HARD) — NFA isolation proof: must stay byte-unchanged
bash scripts/audit_concurrency_invariants.sh  # OK — no dup case TT_/IR_, FACT RULES byte-identical
bash scripts/util_template_purity_audit.sh    # no bytes outside templates (baseline)
```

**Isolation gate (every RK-NFA step):** `test_smoke_snobol4.sh` + the SNOBOL4 pattern-rung suite must stay
byte-identical (no SNOBOL4 pattern template touched), FACT grep 0, Icon/Prolog smokes invariant.

---

## Architecture reference

- Unified lowerer: `src/lower/lower.c` — `lower2()`, role-seeded `lower2_{value,pattern,goal}_entry`; Raku arms are `cx.lang==IR_LANG_RKU` branches INSIDE the shared `tree_e` cases.
- Shared four-port builders: `wire_seq` (n-ary sequence-with-backtrack), `wire_alt` (n-ary fail-chain), `wire_det_builtin1` (role-agnostic deterministic builtin call — Raku `say`/`print` reuse this).
- Semantic oracle (mode 2): `src/lower/bb_exec.c` — `bb_exec_once` / `bb_exec_resume` over `IR_t`.
- Topology proof harness: `src/lower/prove_lower2.c` (+ `scripts/prove_lower2.sh`); `main()` is sectioned SNOBOL4 / ICON / PROLOG — ADD a RAKU section (BEGIN/END markers) so concurrent appends auto-merge.
- Emitter dispatch: `src/emitter/emit_core.c`; Raku templates: `src/emitter/BB_templates/bb_rk_*.cpp`.
- Register source of truth: `src/emitter/bb_regs.h` (the BBREG_*/BBREGN_* names; the subject triad is used only in the NFA slab).
- Raku frontend: `src/frontend/raku/raku.l`, `raku.y`; goal files `GOAL-RAKU-FRONTEND.md`, `GOAL-PST-RAKU.md`.
- Isolated regex matcher (C reference / oracle): `src/frontend/raku/raku_nfa*.c` (`nfa_bt`), `raku_re.c`.

---

## Watermark

**CHECKPOINT (2026-06-01, Opus 4.8) — RK-EMIT-2-NEST: jct_nested crosses to m3/m4.** Net deliverable:
the `jct_nested` case (nested junctions — `all(50, any(50|60))`, per docs.raku.org/type/Junction) now passes
modes 3 AND 4. **Raku m2 22/22 (HARD ✓), m3 16→17/22, m4 16→17/22**; **Icon 10/10 m2, 9/9 m3/m4 UNCHANGED**;
**SNOBOL4 7/7 m2, 5 m3, 0 m4 UNCHANGED** (no peer regression). prove_lower2 **64/0** unchanged (lowering
untouched — emitter-only fix); concurrency invariants OK (FACT RULES byte-identical x3/x4); template-purity
**7** unchanged (bb_call.cpp fprintf count 4→4, ZERO new side-effects). SCRIP HEAD: `c1f8e2e` (pushed; rebased
onto peer base `67ce946` — PROLOG-BB PLG-5 + GZ-10 zero-arg user-proc, which also touched bb_call.cpp/bb_exec.c/
lower.c/emit_bb.c; rebuilt + re-verified the COMBINED tree green: Raku m2 22/22·m3 17·m4 17, Icon m2 11/11·m3 10·m4 9,
SNOBOL4 7/7·5·0, prove_lower2 64/0, concurrency OK — no cross-session regression). Pushed to origin this handoff.

- **THE FIX (ONE file — `src/emitter/BB_templates/bb_call.cpp`):** the prior RK-EMIT-2 `dval==2.0` arm required
  EVERY arg sub-graph entry to be a SIMPLE leaf (`IR_LIT_I/S/F/NUL`/`IR_VAR`); a junction member that is itself a
  junction (`any(50|60)` inside `all(...)`) has a sub-graph entry that is a NESTED `IR_CALL dval==2.0`, so
  `leaves_ok` went 0 → the loud `[IBB] FATAL bb_call: unsupported call shape … arg0_kind=-1` abort fired. Added a
  recursive `static rk_marshal_call_arg(lf, aoff, owner, idx)` helper (TEMPLATE-PURE — all bytes stay inside this
  one BB_template, reached only via the emit_core dispatch): a LEAF is loaded exactly as before (byte-identical →
  the 16 prior m3/m4 passes are unchanged); a NESTED `IR_CALL dval==2.0` is emitted INLINE — its own args go into
  a FRESH contiguous ζ arg-vector region (allocated AFTER this level's vector so contiguity holds), `rt_rk_call_arr`
  is invoked, and its rax:rdx result DESCR is stored into the outer arg slot `[r12+aoff]`, EXACTLY mirroring the
  mode-2 oracle (which `bb_exec_once`s the nested sub-graph to a DESCR and passes THAT) ⇒ m2==m3==m4. Verified
  general to ARBITRARY nesting depth (3-level `1|(2&(7|9))`) and to variable members (`7|($a&8)`), all three modes
  agreeing. The arg-acceptance check widened `leaves_ok`→`args_ok` to admit `IR_CALL dval==2.0`. NO value stack (the
  per-call arg vector is the sanctioned ARBNO-style per-activation frame array); NO name-table round-trip; NO new
  `bb_rk_*` file (the nested-call path reuses the SAME `rt_rk_call_arr` runtime trampoline). Build trap re-confirmed:
  `bash scripts/build_scrip.sh && make libscrip_rt` (templates compile into BOTH `scrip` and `libscrip_rt`).

- **EXACT REMAINING m3/m4 FAILURES (5, same in both):** `gather_take`, `map_range`, `grep_range`, `map_over_gather`,
  `grep_over_gather` — the genuinely Raku-only generators needing NEW `bb_rk_gather`/`bb_rk_map`/`bb_rk_grep` templates
  for the `IR_GATHER`/`IR_MAP`/`IR_GREP` resumable-pump boxes (the largest remaining lift; the next session's work).

**SESSION HANDOFF (2026-05-31 late, Opus 4.8) — RK-EMIT-1/2/3.** Net deliverable: **Raku crossed onto modes 3 & 4**
for the eager/junction/array tier — **m2 22/22 (HARD GATE), m3 0→16/22, m4 0→16/22**, with **Icon 9/9/9** and
**SNOBOL4 7/7 m2** unchanged (no peer regression; the shared-template edits are additive arms gated on Raku
conditions or generic producer-kind widening). prove_lower2 PASS; concurrency invariants OK (FACT RULES byte-identical
x3); template-purity unchanged from baseline (same 7 pre-existing `fprintf`-in-FATAL flags, exits 1 at baseline — I added
zero new side-effects; verified fprintf counts identical to HEAD in every touched file).

**THE KEY CORRECTION:** the previous handoff's claim that "Raku m3/m4 = 0/22 is blocked on SHARED SNOBOL-family `[SBB]`
infrastructure, NOT a Raku-fixable gap" was **WRONG**. Raku fell into the `[SBB]` abort ONLY because `.raku` set no
routing flag in `scrip.c`. Raku's lowered IR is built entirely from Icon's kinds (IR_CALL/IR_LIT_*/IR_VAR/IR_TO/IR_ASSIGN/
IR_IF/IR_WHILE/IR_BINOP/IR_ALT + the Raku-only IR_GATHER/IR_MAP/IR_GREP), so routing Raku through **Icon's own proven
LOWER-direct driver** (`icn_flat_chain_build` for m3, `codegen_flat_build`/`icn_flat_chain_build_text` for m4) + the
SHARED `bb_*` templates lights up every shared kind immediately. No `[SBB]` adapter was touched.

**Which BBs this session (created / reused):** Byrd-Box emitter templates — **0 new `bb_rk_*` files created; 4 SHARED
templates REUSED/extended** (`bb_call`, `bb_lit_scalar`, `bb_assign`, `bb_binop`) plus the shared chain emitter
(`emit_bb.c`) and 2 runtime trampolines (`gen_runtime.c`: `rt_rk_call_arr`, `rt_rk_jct_relop`). The deliberate choice was
to REUSE Icon's path rather than author new boxes, exactly as the ladder anticipated ("REUSE the existing bb_lit/bb_call…
for shared kinds; bb_rk_* only for generator/junction/NFA boxes"). The genuinely Raku-only `bb_rk_gather`/`map`/`grep`
generator boxes remain UNWRITTEN (the 5 generator failures).

**EXACT REMAINING FAILURES (6 in m3, same 6 in m4):** `jct_nested` (nested `IR_CALL` arg sub-graph — dval==2.0 arm
declines nested-call args; needs recursive sub-graph emission in `bb_call.cpp`), `gather_take`, `map_range`, `grep_range`,
`map_over_gather`, `grep_over_gather` (need `IR_GATHER`/`IR_MAP`/`IR_GREP` resumable-pump templates). These are the next
session's work and are the larger lift.

**BUILD TRAP (cost a cycle):** `bb_*.cpp` compile into BOTH `scrip` AND `libscrip_rt`. After editing a template you MUST
`bash scripts/build_scrip.sh && make libscrip_rt` — a stale `scrip` gives misleading aborts that look like emitter bugs.
Also: a C comment containing `IR_LIT_` followed by `*` then `/` closes the comment early — write `IR_LIT scalars`, not the
glob form. SCRIP HEAD before this session: `80431d0`; this session committed as `47e84d7`.

---


Net deliverable this session: **RK-LOWER-5a** (Raku read-only eager value ops — hash/array reads, `sort`, list ctor,
`elems`/`reverse`/… whitelist — onto the unified `lower.c`, mode-2) PLUS the **3-mode TESTING DIRECTIVE restored** in
`scripts/test_smoke_raku.sh`. Verified 3-mode matrix at handoff (clean step-zero rebuild, rc=0):

| frontend | mode-2 `--interp` | mode-3 `--run` | mode-4 `--compile` |
|---|---|---|---|
| Raku    | **22/22** (HARD ✓) | 0/22 | 0/22 |
| Icon    | 6/6 ✓ | 6/6 ✓ | 6/6 ✓ |
| SNOBOL4 | 7/7 ✓ | 0/6  | 0/6  |

prove_lower2 **61/0**; FACT-rule md5 `5097ed94` ×4; concurrency audit baseline-7-staleness pre-existing (Icon/SNOBOL,
zero Raku). **Why Raku m3/m4 = 0/22 (DIAGNOSED, NOT a Raku-fixable gap):** Raku rides the SNOBOL4-family `[SBB]` mode-3/4
driver, severed by Lon 2026-05-31 (`sno_ring_to_tree` removed; LOWER-direct path unwired) — same root cause as SNOBOL4's
0/6. Icon is 6/6/6 because it has its own native path. So modes 3/4 need the SNOBOL4-BB / Ground-Zero `[SBB]` LOWER-direct
driver rewired FIRST (shared infra, not a Raku-session task); then Raku reuses Icon's proven `bb_call`/`bb_lit`/`bb_to`
templates for shared kinds + `bb_rk_*` only for generator/junction/NFA boxes. **NEXT:** (A) RK-LOWER-5b redo (mutating
hash/array writeback via the sound dval=3.0 exec-vname-recovery — fix the statement-position call's γ/ω return so a
successful mutation continues the sequence); (B) coordinate the `[SBB]` LOWER-direct driver with the SNOBOL4-BB session.
**STILL DEFERRED:** the lockstep "three → four" FACT-RULE roster expansion across all four GOAL files.

---

**3-MODE TESTING DISCIPLINE RESTORED + 5b REVERTED (2026-05-31, Opus 4.8).** Correcting a process violation: the
GOAL "TESTING DIRECTIVE — ALWAYS RUN ALL THREE MODES" (Lon 2026-05-31, "Never report a mode-2 number alone") was
NOT being honored — `scripts/test_smoke_raku.sh` ran only `--interp`. It now runs mode 2 (`--interp`, HARD),
mode 3 (`--run`), AND mode 4 (`--compile --target=x86` → `as` → `gcc -no-pie -lscrip_rt` → run) on the SAME program
per case, reporting all three, mirroring `test_smoke_icon.sh` (floors `MODE3_MIN`/`MODE4_MIN` default 0). **The honest
full picture (the point of the directive):** mode-2 **22/22** (HARD ✓), mode-3 **0/22**, mode-4 **0/22**. Modes 3/4 are
by-design SMX abort because **RK-EMIT is entirely unbuilt — there are ZERO `bb_rk_*.cpp` emitter templates.** EVERYTHING
in RK-LOWER-0..5a is mode-2 only (the `bb_exec.c` IR oracle); nothing Raku exists in the modes-3/4 EMITTER yet. The
in-flight RK-LOWER-5b (mutating hash/array writeback via an exec-side vname-recovery branch keyed on `IR_CALL` dval=3.0)
was UNCOMMITTED + broken (push-as-statement produced no output — the mutating call's success/fail port wiring needs
rework) so it was **reverted to the clean committed 5a baseline** (`git checkout src/lower/{lower.c,bb_exec.c}`); it will
be redone under the 3-mode discipline. SCRIP HEAD: `137e930` (RK-LOWER-5a). Build clean (`scrip` + `libscrip_rt` rc=0);
prove_lower2 **61/0** unchanged; Icon 6/6, SNOBOL4 7/7 m2 unchanged. FACT-rule md5 `5097ed94` ×4. The pre-existing
`audit_concurrency_invariants` 7>6 baseline staleness (Icon/SNOBOL emitter `fprintf`s, zero Raku) is still owed by Icon/HQ.

- **BB ACCOUNTING (clarified for the record):** "BBs created for Raku" splits by stage. In modes 3/4 (EMITTER / actual
  Byrd Box templates): **0 created, 0 reused** — RK-EMIT unstarted. In mode-2 (LOWER-stage `IR_*` kinds): **3 created** —
  `IR_GATHER` (RK-LOWER-2), `IR_MAP` + `IR_GREP` (RK-LOWER-3), all lazy-Seq generators with no pre-existing analog;
  **~13 reused** — `IR_LIT_I/S/F/NUL` (literals — Raku invents NO literal kind; flows through the SHARED `v_literal`
  arm, NOT a custom `BB_ILIT/SLIT/DLIT` — those names do not exist), `IR_VAR`, `IR_KEYWORD`, `IR_CALL`, `IR_TO/IR_TO_BY`,
  `IR_ASSIGN`, `IR_IF`, `IR_WHILE`, `IR_BINOP/IR_UNOP`, `IR_ALT`, the generator PUMP (`v_raku_for`), `IR_SUCCEED/IR_FAIL`.
  When RK-EMIT lands, Raku literals/arith/etc. will likewise REUSE the existing `bb_lit.cpp`/`bb_lit_scalar.cpp` and
  peer templates; only the generator/junction/NFA box set gets the `bb_rk_*` prefix.

**NEXT (two tracks, both now gated by the 3-mode smoke):** (A) RK-LOWER-5b redo — mutating hash/array writeback (the
dval=3.0 exec-recovery approach is sound; the bug was port wiring of the statement-position call — fix the γ/ω return so a
successful mutation continues the sequence). (B) **Modes 3/4 — DIAGNOSED 2026-05-31 (Opus 4.8):** Raku `--run`/`--compile`
abort with `[SBB] sno_ring_to_tree REMOVED (VIOLATION, Lon 2026-05-31) ... must come from LOWER producing the four-port
statement-BB graph directly ... not yet wired. Aborting (by design).` i.e. Raku routes through the SNOBOL4-family `[SBB]`
mode-3/4 driver, which Lon SEVERED 2026-05-31 (ring→tree adapter removed; LOWER-direct path unwired) — the SAME reason
SNOBOL4 is 0/6 in m3/m4. Icon is 6/6 because it has its OWN native path. **So Raku m3/m4 = 0/22 is blocked on SHARED
SNOBOL-family infrastructure (SNOBOL4-BB / Ground-Zero track), NOT a Raku-only RK-EMIT task. Writing `bb_rk_*.cpp` templates
is necessary but NOT SUFFICIENT until that upstream `[SBB]` driver consumes the four-port LOWER graph directly (or Raku is
given its own LOWER-direct m3/m4 driver like Icon's).** Recommended sequencing: coordinate with the SNOBOL4-BB session on
the statement-BB-graph-from-LOWER driver; once Raku can reach its `IR_CALL`/generator nodes in m3/m4, reuse the proven Icon
templates (`bb_call`/`bb_lit`/`bb_to`/…) for the shared kinds and add `bb_rk_*` only for the generator/junction/NFA box set.

---

**RK-LOWER-5a LANDED (2026-05-31, Opus 4.8).** Raku eager-core READ-ONLY value ops cross onto the unified `lower.c`
for mode-2. SCRIP HEAD before this work: `641e45d` (the RK-LOWER-4 junction commit). My 3 files: `src/lower/{lower.c,
prove_lower2.c}`, `scripts/test_smoke_raku.sh`; ZERO emitter files — same discipline as RK-LOWER-0/1/2/3/4. Build clean
(`scrip` + `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION (no emitter touched ⇒ both modes process
the new `IR_CALL`s through the SAME shared dispatch → by-design SMX abort, RK-EMIT deferred; nothing can diverge).

- **The lowering (lower.c):** ONE new SHARED helper `v_raku_det_call` (byte-for-byte the junction arm's packing: ONE
  `IR_CALL`, `dval=2.0`, each operand in its OWN `lower_value_subgraph`, ptr array on `.counter`, count on `.ival`, det
  so β=ω_in). It is the reach into the already-proven script-builtin runtime (`script_builtins_byname.c`, via the
  RK-LOWER-4 tail delegation). Wired through (a) FOUR newly-split dedicated cases — `TT_HASH_GET`→`hash_get`,
  `TT_HASH_EXISTS`→`hash_exists`, `TT_ARR_GET`→`arr_get`, `TT_SORT`→`array_sort` (pulled out of the loud-fall group;
  non-Raku still → `lower_unhandled`, zero peer change); and (b) a PURE-builtin WHITELIST arm in the existing `TT_FNC`
  case (`__rk_arr`/`elems`/`reverse`/`sort`/`join`/`sum`/`unique`/`head`/`tail`/`chars`/`length`/`lc`/`uc`/`trim`/`substr`/
  `index`/`rindex` + the explicit-call read forms). List literal `(e1,e2,..)` desugars (parser) to `__rk_arr(..)`, so
  list CONSTRUCTION + multi-element `sort`/`reverse`/`@a[i]` reads are all reachable. Semantics per docs.raku.org/type/
  {List,Hash,Array} + /routine/{elems,reverse,sort}. **0 NEW BBs — reuses `IR_CALL`** (Raku's footprint stays 3 invented
  : ~13 reused).
- **THE CRITICAL EXCLUSION (logged for the next dev):** the MUTATING builtins (`push`/`pop`/`arr_set`/`hash_set`/
  `hash_delete`) and the effectful ones (`open`/`close`/`slurp`/`spurt`/`die`/`meth_call`/`obj_new`/grammar/regex/nfa)
  are DELIBERATELY NOT whitelisted — routing them through the pure value path would compute a result but silently DROP
  their variable-writeback / side effect. Per the FACT RULE they instead fall LOUD to `lower_unhandled`, landing properly
  in 5b/5c. Consequence: hash reads (`hash_get`/`hash_exists`) are WIRED + correct but only round-trip-testable once
  `hash_set` lands in 5b; the array read+construct+sort path is fully self-contained and proven now.
- **TWO TRAPS HIT + FIXED (for the next dev):** (1) `make scrip` left a STALE `lower.c` object — use `bash scripts/
  build_scrip.sh` for a reliable rebuild. (2) A C comment containing `grammar_*/re_*/nfa_*` had `*/` sub-sequences that
  CLOSED the comment early (stray-`\342` / "5b integer-suffix" errors downstream); rewrote without glob asterisks.

**Gates at handoff:** prove_lower2 **61 PASS** / 0 FAIL (RAKU section +4: `__rk_arr(1,2,3)`, `@a[1]`, `sort(@a)`,
`elems(@a)` — all 1-principal-node, PASS). Mode-2 HARD all green: Raku **22/22** (added list_construct_read, array_sort,
array_elems, array_reverse, str_reverse), Icon 6/6 (UNCHANGED — Raku-gated + `IR_LANG_RKU`-gated edits), SNOBOL4 7/7
(UNCHANGED — NFA isolation intact). FACT-rule md5 `5097ed94` byte-identical ×4; no dup `case IR_`/`TT_` (the four split
cases route to ONE `v_raku_det_call`, the whitelist lives inside the existing `TT_FNC` case — no new case label).
**Pre-existing baseline confirmed NOT mine:** `audit_concurrency_invariants.sh` purity COUNT 7 > baseline 6 — all 7 are
loud-error `fprintf`s in ICON/SNOBOL emitter boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku/`lower.c`
(I touched no emitter file). **FIX STILL OWED BY ICON/HQ: bump baseline 6→7.** Modes 3/4 = by-design SMX abort for Raku
(floors MODE3_MIN/MODE4_MIN=0). NOTE: committed LOCALLY as a checkpoint; push-to-origin awaits the next `perform hand off`.

**NEXT:** RK-LOWER-5b — hash/array MUTATING ops with writeback. Cleanest path (IR_t is LEAN, no new field per PEERS):
add pure-variant runtime twins (`*_pure` returning the new container string, no `NV_SET`) and lower `push(@a,x)`/`%h<k>=v`
/`@a[i]=v` as `var = pure_op(var, args)` (IR_ASSIGN over IR_CALL). `pop($p=pop(@a))` is the exception — it returns a
DIFFERENT value than the new container, so it genuinely needs vname threading (exec-side peek of the first sub-graph's
`IR_VAR`, or a sanctioned marker). Then 5c try/CATCH/die, 5d class/method/field/new.

---

**RK-LOWER-4 LANDED (2026-05-31, Opus 4.8).** Raku junctions `any`/`all`/`one`/`none` + infix `|`/`&` cross onto
the unified `lower.c` for mode-2. SCRIP HEAD before this work: `8a01bb3`. My 5 files: `src/lower/{lower.c,
lower_program.c,prove_lower2.c}`, `src/runtime/interp/gen_runtime.c`, `scripts/test_smoke_raku.sh` (+ session design
note `SCRIP/RK-LOWER-4-DESIGN.md`); ZERO emitter files — same discipline as RK-LOWER-0/1/2/3. Build clean (`scrip`
+ `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION (no emitter touched ⇒ both modes process the
junction `IR_CALL` through the SAME shared dispatch → by-design SMX abort, RK-EMIT deferred; nothing can diverge).

- **The lowering (lower.c, TT_FNC value-role, `cx.lang==IR_LANG_RKU` arm):** constructor `any(…)`/`all(…)`/`one(…)`/
  `none(…)` AND infix forms share ONE arm — the parser's `mk_junction` flattens same-flavor infix chains into the
  SAME `TT_FNC(sval=flavor, c[0]=TT_VAR(flavor), c[1..]=members)` the constructors produce. Lowers to ONE `IR_CALL`
  to `__rk_jct_{any,all,one,none}` with `dval=2.0` (the SNOBOL4 isolated-value-subgraph call idiom); each member →
  its OWN `lower_value_subgraph` (cursor keeps `IR_LANG_RKU` so a NESTED junction member re-enters this arm), sub-graph
  ptr array on `.counter`, member count on `.ival`, det (β=ω_in). Semantics per docs.raku.org/type/Junction.
- **THE NESTING BUG (logged for the next dev):** the first cut wired members into a FLAT α/γ chain (dval=0.0); that
  flattened mixed-flavor nesting — `10 | (50 & 60)` collapsed to `10 | 50`, losing the nested `all` (`cat -v` on the
  value: `^Ca^A10^A50^D`). FIX: lower each member as an isolated value sub-graph (dval=2.0 idiom), so a nested-junction
  member evaluates to ONE opaque ETX-tagged value; `junction_collapse` already recurses on `\x03` members via `\x04`
  EOT spans. After the fix flat + nested + precedence + var-roundtrip + string-collapse all pass.
- **DISPATCH-GAP FIX #1 (gen_runtime.c):** the mode-2 `IR_CALL` exec arm calls `try_call_builtin_by_name` (gen_runtime.c),
  but `__rk_jct_*` lives in `script_try_call_builtin_by_name` (script_builtins_byname.c) which post-SMX-4 had NO live call
  site (orphaned SM-era arm). Added a TAIL delegation: names gen_runtime rejects fall through to script's dispatcher.
  Placed AFTER every gen_runtime arm so the 6 overlapping names (close/open/pop/push/reverse/trim) keep gen_runtime's
  semantics and NO live path is disturbed — only previously-REJECTED names newly served. The documented APPENDIX-A
  "SM dispatch-gap fix" shape. Side benefit: the whole script-builtin layer (hash/IO/regex/array) is now reachable in
  mode-2 for later rungs (RK-LOWER-5, RK-NFA).
- **DISPATCH-GAP FIX #2 (lower_program.c binop_apply):** a junction collapses to Bool only in a relop. The mode-2 relop
  evaluator is `lower_program.c`'s `binop_apply` (NOT rt.c's — that's compiled mode-3/4 runtime). Added a prologue: if
  either operand `junction_is()` (ETX-tagged), call `junction_collapse(scalar, jct, tt_op, numeric)` threading the relop
  (any=OR, all=AND, one=XOR1, none=NONE). Covers numeric relops (`==`/`<`/…) AND string relops (`eq`/`lt`/… → numeric=0).
  ETX prefix is unused by any SNOBOL4/Icon/Prolog value ⇒ FACT-RULE-safe in shared C (Icon 6/6, SNOBOL4 7/7 unchanged).
- **RAKU VOID-IF FIX (lower.c v_if):** the canonical test interleaves passing + FAILING `if`s and expects the sequence to
  continue past a failed condition. A failed scalar `if ($x==7)` was aborting the whole statement sequence — confirmed
  PRE-EXISTING (clean tree, `git stash`), independent of junctions. Per docs.raku.org/language/control an `if` with no
  `else` whose condition is false yields `Empty` and CONTINUES (does NOT fail). Fixed inside shared `v_if` (FACT RULE:
  branch on `cx.lang`): for `IR_LANG_RKU` a no-else condition-failure routes to `γ_in` (continue) not `ω_in` (fail);
  Icon/SNOBOL/Prolog keep `ω_in` (goal-directed expression failure, jcon ir_a_If).

**Gates at handoff:** prove_lower2 **57 PASS** / 0 FAIL (RAKU section: say + print + for-loop + gather + map + grep +
**any(1,2,3)** + **any(1,all(5,5)) nested**, all PASS). Mode-2 HARD all green: Raku **17/17** (added jct_any, jct_all,
jct_one, jct_none, jct_infix, jct_str, jct_nested), Icon 6/6 (UNCHANGED — shared binop_apply ETX-guard + v_if lang-gate
did NOT regress), SNOBOL4 7/7 (UNCHANGED — NFA isolation intact). The three canonical junction corpus files
(`test/raku/rk_junctions.raku`, `rk_junction_nest.raku`, `rk_junction_prec.raku`) all MATCH their `.expected`.
**Pre-existing baseline items confirmed NOT mine (verified by `git stash` on clean `8a01bb3`):** (a)
`audit_concurrency_invariants.sh` purity COUNT 7 > hardcoded baseline 6 — all 7 are loud-error `fprintf`s in ICON/SNOBOL
boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku; **FIX STILL OWED BY ICON/HQ: bump baseline 6→7**;
(b) `test_gate_em_template_byte_identity.sh` = 1/4 (SM/BB emitter migration mid-flight). FACT-rule md5 `5097ed94`
byte-identical ×4; no dup `case IR_`/`TT_` within any one switch (the junction arm added NO new case label — it lives
inside the existing `TT_FNC` value case). Modes 3/4 = by-design SMX abort for Raku (floors MODE3_MIN/MODE4_MIN=0).

---

**RK-LOWER-3 LANDED (2026-05-31, Opus 4.8).** Raku `map`/`grep` cross onto resumable Byrd-Box Seq CONSUMERS for
mode-2. SCRIP HEAD at this handoff: `fd54615` (committed; parents the RK-LOWER-2 keystone `3571829`). My 6 files:
`src/include/IR.h`, `src/lower/{scrip_ir.c,lower.c,bb_exec.c,prove_lower2.c}`, `scripts/test_smoke_raku.sh` (+ the
session design note `SCRIP/RK-LOWER-3-DESIGN.md`); ZERO emitter files — same discipline as RK-LOWER-0/1/2. Build
clean (`scrip` + `libscrip_rt` rc=0). Mode-3≡mode-4 invariant kept BY CONSTRUCTION: no emitter touched ⇒ both
modes process `IR_MAP`/`IR_GREP` through the SAME shared dispatch (by-design SMX abort, RK-EMIT deferred), nothing
can diverge; the byte-identity gate is unchanged (proved via `git stash` — identical 1/4 before my edits).

- **RK-LOWER-0 (`say`/`print`):** `TT_SAY`/`TT_PRINT` arm in `lower.c` routes through the SHARED `wire_det_builtin1`
  → `IR_CALL` (say→`"write"` = .gist+newline, print→`"writes"` = .Str+no-newline per docs.raku.org/routine/{say,print};
  for str/int `.gist`≡`.Str` so only the trailing newline differs — the Icon write/writes split, ZERO runtime change).
  The eager core (arith/var/while/concat) came FOR FREE through the already-shared lang-agnostic value arms. Raku smoke clean.
- **RK-LOWER-1 (lazy range → loop):** dedicated Raku-gated `v_raku_for` helper in `lower.c` (reached only from the
  `cx.lang==IR_LANG_RKU` arms of the shared `TT_EVERY` and the `TT_FOR_RANGE` case). Reuses Icon's resumable
  `IR_TO`; wires the four ports directly — `gen.γ→bind(IR_ASSIGN)`, `bind.γ→body`, `body.γ/ω→gen.β` (re-pump:
  `IR_TO` is its own resume), `gen.ω→γ_in` (range drained ⇒ `for` STATEMENT completes & falls through). Handles
  `for 1..3 { say $_ }` ($_ default) AND `for 1..3 -> $i {…}`; `..^` exclusive; empty range falls through.
- **RK-LOWER-2 (KEYSTONE — gather/take):** NEW resumable Seq-producer kind `IR_GATHER` in `lower.c`'s `v_raku_gather`,
  its OWN resume (β=self, like `IR_TO`). Realizes the APPENDIX-A `RK-M2-GATHER` spec — counter-as-resume-cursor:
  yield ONE take per (re)entry, drain (cursor ≥ count, or empty gather) → FAIL→ω. Driven by the EXISTING generator
  PUMP via `v_raku_for` — NO new pump machinery. Reached BOTH as the iterate source of `for gather {..} -> $v`
  (the `TT_EVERY` Raku guard now admits a `TT_GATHER` iterate child) AND as a bare value expr (dedicated `TT_GATHER`
  case, Raku arm; non-Raku → `lower_unhandled`). Take payloads → SEPARATE value sub-graphs (`lower_value_subgraph`,
  cursor carries `IR_LANG_RKU`); subs-array ptr on `IR_GATHER.counter`, count on `.ival`, cursor on `.state`.
  **THE BUG (logged for the next dev):** `bb_reset` zeroes `.counter` for every node except a special list — it was
  wiping the subs-array ptr → drain-on-first-entry (output `done` only). FIX: added `IR_GATHER` to the `bb_reset`
  counter-preservation list (cursor lives in `.state`, correctly reset; subs-array in `.counter`, now preserved),
  exactly as `IR_CALL`(dval==2.0)/`IR_SCAN`/`IR_PAT_ARBNO` do. New IR kind wired additively in 7 sites (enum, name
  table, `kind_is_resumable`, `ir_is_single_shot`, `bb_is_gen_kind_raw`, `ALT_IS_GEN`, exec case). Mode-2
  `for gather { take(10);take(20);take(30) } -> $v { say $v }` → `10,20,30,done`. FLAT-take model only; dynamic-scope
  takes (inside loops/conditionals, docs.raku.org `factors()`) are a later refinement on this SAME node.
- **RK-LOWER-3 (map/grep Seq consumers):** TWO NEW resumable Seq-consumer kinds `IR_MAP`/`IR_GREP` in `lower.c`'s
  `v_raku_map_grep` (one helper, `is_grep` flag selects kind + filter-vs-transform), each its OWN resume (β=self,
  like `IR_GATHER`). REUSES the gather producer MODEL + the Prolog `aggregate_all` eager-drain idiom — NO new pump.
  AST (verified `--dump-ast`): `map {C} S` / `grep {P} S` = `TT_MAP`/`TT_GREP`(c0=closure-body-expr reading `$_`,
  c1=SOURCE). Reached BOTH as the iterate source of `for map/grep {..} SOURCE -> $v` (the `TT_EVERY` Raku guard now
  admits `TT_MAP`/`TT_GREP`) AND as a bare value expr (dedicated case, Raku arm; non-Raku → `lower_unhandled`).
  SOURCE → its own value sub-graph (ptr on `.counter`, added to the `bb_reset` preserve-list alongside `IR_GATHER`);
  closure BODY → second sub-graph (ptr on `.ival`); resume cursor on `.state`. Exec arm (mode-2 oracle): on FRESH
  entry eager-drains SOURCE (`bb_reset`+`bb_exec_once`+`bb_exec_resume` loop) into a NODE-KEYED `DESCR_t` side-cache
  (`rk_seq_cache_t`, so re-yields across PUMP re-entries don't re-drain), then per (re)entry binds `$_` via
  `NV_SET_fn("_",elem)` and runs the closure: **map** yields the closure RETURN (failing transform → NULVCL, one
  per element); **grep** KEEPS the source element iff the closure is NOT FAIL (`binop_apply`'s relational arms
  return FAIL when false — the value-model truthiness convention), skips on FAIL. Drain → ω (for completes).
  Wired additively in the same site-set as `IR_GATHER` (enum, name table, `bb_reset` preserve, `kind_is_resumable`,
  `ir_is_single_shot`, `bb_is_gen_kind_raw`, `ALT_IS_GEN`, exec case, `TT_EVERY` guard). Semantics grounded in
  docs.raku.org/routine/{map,grep} (map gathers each element's return into a lazy Seq; grep returns matching
  elements in original order — order + duplicates preserved). SCOPE = the for-driven consumer form (mirrors
  RK-LOWER-2's for-driven gather scope); bare-value `say map {…} 1..3` (List-as-value) waits on RK-LOWER-5.

**Gates at handoff:** prove_lower2 **55 PASS** / 0 FAIL (RAKU section: say + print + for-loop + gather + **map** +
**grep**, all PASS). Mode-2 HARD all green: Raku **10/10** (added `map_range`, `grep_range`, `map_over_gather`,
`grep_over_gather`), Icon 6/6 (UNCHANGED — Raku-gated edits), SNOBOL4 7/7 (UNCHANGED — NFA isolation intact).
**Pre-existing baseline items confirmed NOT mine (verified by `git stash` → identical on clean `18357d4`):**
(a) `test_gate_em_template_byte_identity.sh` = 1/4 (SM/BB emitter migration mid-flight per `MIGRATION-MODE4-IS-MODE3-DUMP.md`);
(b) `audit_concurrency_invariants.sh` template-purity COUNT 7 > hardcoded baseline 6 — all 7 are loud-error
`fprintf`s in ICON/SNOBOL boxes (`bb_assign/binop/call/every/field/list_bang/swap`), ZERO Raku; the 7th
(`bb_call.cpp` `[GZ-3] FATAL`) is from Icon peer `582c3bc`. **FIX STILL OWED BY ICON/HQ: bump baseline 6→7.**
FACT-rule md5 `5097ed94` byte-identical ×4; no dup `case IR_`/`TT_`. Modes 3/4 = by-design SMX abort for Raku
(RK-EMIT not built; floors MODE3_MIN/MODE4_MIN=0) — same shape as SNOBOL4, identical across both modes.

**NEXT:** RK-LOWER-5 — eager core onto straight-line IR: arithmetic (mostly free already), hash/array element
ops, `sort`, `try`/`CATCH`, class/method dispatch, and `say(jct)`/`say(list)` composite-value output. Port the
APPENDIX-A RK-HASH / RK-IO / RK-EXCEPTIONS / RK-CLASS *semantics* onto the four-port IR (the behaviors are the
spec; the SM opcodes are not). NOTE the dispatch-gap delegation landed in RK-LOWER-4 already makes the whole
script-builtin layer (hash/IO/regex/array in `script_builtins_byname.c`) reachable in mode-2 — RK-LOWER-5 lowers
the Raku AST arms that feed it. Also still open: the `…` sequence operator — `IR_SEQ_GEN` already exists as the
infinite `…` counter generator (SM-era exec at `bb_exec.c`, not yet lowered); keep it DISTINCT from `IR_GATHER`.

**STILL DEFERRED (NOT done this session):** the lockstep "three → four" roster/body expansion across all four GOAL
files (the FACT-RULE clause-5 obligation) — high-blast-radius, best as its own focused commit. The FACT RULES remain
byte-identical x3 with Raku as the fourth carrier (md5 `5097ed94` / `307534d6` / `8255d653` unchanged); audit passes.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus

---
---

## APPENDIX A — PRE-SMX-4 RAKU STATE (historical; SM engine deleted — numbers NOT reachable today)

> Preserved from the prior GOAL-RAKU-BB.md so no design knowledge is lost. The MECHANISM below
> (SM opcodes `SM_BB_INVOKE`/`SM_CALL_FN`/`SM_LOAD_FRAME`, `BB.h`, `BB_*` kinds, mode-3 `sm_run_native`)
> was removed by SMX-4. Treat these as SEMANTIC SPECS for the re-homed `lower.c` rungs above, not live state.

**Gates at the 2026-05-30 hold (SM engine):** GATE-RK m2 45/46, GATE-RK4 m4 46/46, GATE-RK3 m3 45/46
CRASH 0, smoke 5/5/5/13/5, SNOBOL4 iso M2 19/0 M4 18/1. SCRIP HEAD `290af6b9`. Build clean.

**SM-era completed rungs (semantic specs to port):**
- RK-BB-1: `for $a..$b -> $i` → `BB_TO_BY`. → re-home: RK-LOWER-1.
- RK-BB-2 (keystone): lazy Seq `gather`/`take` + `…` → `BB_SUSPEND`+`BB_EVERY` PUMP (reused `bb_upto.cpp`). → RK-LOWER-2.
- RK-BB-3: lazy `map`/`grep` as Seq consumers (eager-drain). → RK-LOWER-3.
- RK-BB-SEGFAULT-CLUSTER: polyglot union-clobber, multi-sub `TT_SUB_DECL`, `lower_return` value preservation.
- RK-BB-SM-FRAME-MODE4: named-sub frame slots (`rt_frame_enter/leave/load/store` + `SM_LOAD/STORE_FRAME`). → re-home onto the BB-local ζ frame.
- RK-GIVEN-MODE4: `given`/`when` as if-chain (no `SM_PUMP_CASE`, no thunks).
- RK-HASH: hash builtins (set/get/exists/keys/values/pairs/delete), SOH/STX encoding. → RK-LOWER-5.
- RK-IO: `rk_fileio38`+`rk_stdio39`; `TT_ITERATE(TT_FNC)` arm; `raku_capture` returns FHVAL; line-buffered stdout. → RK-LOWER-5.
- RK-EXCEPTIONS: try/CATCH/die; SSE-safe `raku_die`; exc_clear/check/get. → RK-LOWER-5.
- RK-CLASS: `lower_class_decl` emits `RECORD_REGISTER` before `RECORD_MAKE`; idempotent `icn_record_register`. → RK-LOWER-5.
- RK-M2-GATHER: mode-2 gather multi-yield — counter-as-resume-cursor, yield ONE take per (re)entry; walking past last SUSPEND → FAIL. **This is the RK-LOWER-2 spec on `bb_exec_resume`.**
- RK-M2-ACOMP: `SM_ACOMP` string→numeric coercion (`if l.v==DT_S lv=to_real(l)`); shared across langs.
- RK-BB-4a: constructor junctions any/all/one/none mode-2 — tagged-string junction value `ETX+flavor+SOH-separated members`; `rk_junction_collapse` threads the relop (any=OR, all=AND, one=XOR1, none=NONE). → RK-LOWER-4.
- RK-BB-4b: infix bar/amp build the SAME `TT_FNC` as the constructors; same-flavor chains flatten at parse time. → RK-LOWER-4.
- RK-NFA-1a..1e: isolated `BB_NFA_*` enum + `raku_nfa_to_bb` graph builder + isolated mode-2 backtracking matcher; oracle == parallel NFA on L1-L12; the SM dispatch-gap fix (`raku_try_call_builtin_by_name` twins for `raku_match`/`_global`/`subst`/`nfa_compile`/`re_capture`/`named_capture`) lit the whole regex cluster (GATE-RK m2 35→41, m4 36→42). → re-home: RK-NFA-1.
- M3-RK-NOINTERP-1a..1d: SM-native MEDIUM_BINARY arms (`bb_to_by`/`SM_BB_INVOKE`/`bb_iterate`/`bb_seq` gather-driver) — mode-3 native 19→26. → superseded; re-home onto the `bb_rk_*` template arms (RK-EMIT).

**SM-era open at hold:** SM-2 `when`-arm reroute (BB_ITERATE/SM_CALL_FN mode-4 crash on rk_given18 in_loop).
Superseded by the `lower.c` `given`/`when` arm under RK-LOWER-5.

**Test corpus (REUSE):** `corpus/.../raku/rk_*.raku` (rk_for_array, rk_gather, rk_given18, rk_map_grep_sort24,
rk_junctions, rk_fileio38, rk_stdio39, rk_class26, rk_re32..37, rk_regex23). The L1-L15 regex verdicts/captures
are oracled by the C matcher.
