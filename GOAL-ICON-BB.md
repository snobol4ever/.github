# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.


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

> **⚠️ SHARED-LOWERER LOCKSTEP NOTE (Sonnet, 2026-05-31, Prolog PLG-4 commit).** Two shared three-language
> helpers in `lower.c` changed SEMANTICS as STRICT GENERALIZATIONS during Prolog backtracking work:
> `wire_seq`'s fail-chain now walks back past bounded elements to the nearest resumable predecessor (was a
> single hop that dead-ended after one bounded element), and `wire_alt` now lowers arms right-to-left so each
> arm's exhaustion threads to the next arm's entry via its own deepest-fail edge (was patching only the
> wrapper node's ω, which missed multi-element arms). Both fix latent backtracking bugs that also affect
> Icon sequences/alternations with 2+ bounded elements after a generator. Re-proven non-regressive for Icon
> (m2 6/0 HARD GATE · m3 5/1 · corpus 34/283 — byte-identical via stash/rebuild/compare). No action needed
> unless you edit `wire_seq`/`wire_alt`; the FACT RULE policy below is unchanged.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

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

## 🧹 #1 — GROUND ZERO COMMENT & BLANK-LINE PURGE — DONE 2026-05-31

**First-place task this session (Lon).** Every hand-written `.c/.h/.y/.l` file under `SCRIP/src`
had **all** C-style (`/* */`) and C++-style (`//`) comments stripped, **all blank lines deleted**,
and a **200-char `/*----…----*/` separator** inserted between functions and at top-level
partitions. Rationale: a comment is wrong the moment after it is written because it is never
rewritten when its referent changes — at ground zero we carry **zero** stale comments to confuse us.
- **187 files, 72,442 → 60,455 lines.** Stripper is string/char-literal aware (`"http://"`, `'/'`,
  `"//"` operators all survive). Seed intact: `scrip --interp` prints `hello`. Build green.
- **EXCLUDED — do NOT strip these (they break the build / are machine output):** the 12 checked-in
  flex/bison generated files compiled directly by the Makefile — `*.lex.c`, `*.tab.c`, `*.tab.h`,
  `lex.*.c` under `src/frontend/*/`. Restored from HEAD after the purge.
- **`.cpp` NOT included** — Lon's spec named C/H/Y/L only. `src/emitter/**/*.cpp` still carry their
  comments; extend the purge to `.cpp` if desired (same stripper, add the extension).
- Naming: the icn-derived `gen_` rascal strip (prefix + `g_gen_*`/`lower_gen_*`/`rt_gen_*` infixes,
  e.g. `g_gen_frame_active → g_frame_active`) landed in the same Ground Zero pass; genuine generator
  tokens (the 7 pre-existing `gen_*`, `bb_gen_scan/alt`, `BB_GEN_*`, `binop_gen_state_t`) preserved.

## ⛔⛔ GROUND ZERO 3 — STACKLESS REBUILD (Reset 2026-05-30) ⛔⛔

**This is the THIRD ground-zero reset. The premise that was wrong both prior times: a value stack.**

There is NO value stack. Not an SM value stack, not a `vstack`, not `r12`-as-TOS, not
`rt_push_*`/`rt_pop_*` for Icon value flow. A complete stackless static SNOBOL4/Icon BB
emitter existed ~1.5–2 months ago (archived at `SCRIP/archive/backend/emit_emitters/emit_x64.c`)
and benchmarked **faster than SPITBOL precisely because there is no stack**. The current
mode-3 Icon path regressed by making an SM value stack the inter-box value mechanism
(`rt_push_int` ×39, `rt_pop_nv_set` ×21, underflow guard in `rt.c`). GROUND ZERO 3 rebuilds
from `write("hello")` upward on the stackless model and never reintroduces the value stack.

**The stackless model (verbatim from the archive + the references):**
- **Values live in flat per-box DATA slots**, addressed at stable emit-time addresses
  (the existing `&pBB->value` / `&pBB->counter` / `&pBB->state` idiom). `emit_x64.c:10` —
  *"All pattern variables live flat in .bss as QWORD (resq 1) slots."*
- **Value flow is static wiring, not push/pop.** A box writes its result into its OWN slot;
  a consumer reads its operand boxes' slots directly (operands are known at emit time via
  α/β). Proebsting `plus`: `plus.value ← E1.value + E2.value` — read children by name.
- **Backtrack state for unbounded depth = a per-box .bss ARENA**, not a global stack. ARBNO
  (`emit_arbno`, `emit_x64.c:932`) and recursion use a per-box frame array indexed by depth
  (`test_sno_1.c` `_1[64]`; `test_sno_3.c` lazy `enter()/ζζ` heap frame). NOT push/pop.
- **Inter-box transitions are direct `jmp`.** No `call`/`ret`, no dispatch loop, no walker.
- The hardware C stack (`rsp`) may be used ONLY as transient scratch inside a single node
  (e.g. protect an arithmetic operand across a nested sub-eval, as the archive does) — never
  to thread values between boxes.

**References (now in-repo at `SCRIP/refs/bb/`):**
- `Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` — the four-port templates
  (literal N §4.1, uminus §4.2, plus §4.3, LessThan §4.3, to §4.4, ifstmt §4.5). Figure 1/2
  are the exact target for `5 > ((1 to 2) * (3 to 4))`.
- `test_icon.c` — that same expression as flat C goto-graph, named-slot values, ZERO stacks.
  The byte-exact structural target for GZ-1..GZ-6.
- `test_sno_1.c` — SNOBOL4 ARBNO over alternation: the per-box `_1[64]` arena (the only stack).
- `test_sno_2.c` — recursion as four-port functions (`group`→`group`), `_λ` landing pads.
- `test_sno_3.c` — **the EVAL/CODE/`*P` deferred solution**: each deferred sub-pattern is a
  four-port function `str_t E(E_t **ζζ, int entry)`, frame lazily `calloc`'d by `enter()`,
  resumable at α/β, `empty` decoded as failure at `_λ`. This is the model for GZ-DEFER.
- `SCRIP/archive/backend/emit_emitters/emit_x64.c` — the prior working stackless emitter.

**NEW GATE (enforces stacklessness, parallel to the FACT gate):**
```bash
# Icon emission path must contain ZERO value-stack push/pop:
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target: 0 for every Icon box family as it is rebuilt
```
Plus the existing per-rung gate: `m2==m3` byte-identical, `--dump-sm` count=0 (zero SM),
FACT 0, smokes hold.

### ⛔ ALWAYS TEST ALL THREE MODES (Icon GOAL policy — set 2026-05-31)

**Every SCRIP execution test for this GOAL runs the program through ALL THREE modes on the SAME source, and reports all three. Never test fewer than all three.**
- **mode 2 — `--interp`** (BB port-walker oracle) — **HARD GATE**: must be all-PASS (the source-of-truth output; build sanity).
- **mode 3 — `--run`** (stackless native x86) — **TRACKED**: floor `MODE3_MIN` (env, default 1), ratchets up as GZ rungs rebuild each box family stackless.
- **mode 4 — `--compile`** (standalone x86-64 asm → assemble with `gcc -no-pie` → link `out/libscrip_rt.so` → run → compare output) — **TRACKED**: floor `MODE4_MIN` (env, default 0). **REBUILT 2026-05-31 (Sonnet 4.5): Icon smoke m4 0/6 → 5/6 (matches m3).** No longer severed for Icon — `--compile` emits a C-ABI `main` wrapper (`rt_frame`→ζ, esi=0 → `call main_α`) + the flat BB body via `codegen_flat_build`, reusing the SAME BB templates mode-3 emits (mode-3 = `MEDIUM_BINARY` into a pool + `jmp`; mode-4 = `MEDIUM_TEXT` GAS asm). Non-Icon `--compile` still stubs loud (not yet crossed). (GZ-8, 2026-05-31: `if_expr` — previously the lone m4/m3-red case, fork-blocked in the ring→tree adapter — is now GREEN in m3 AND m4 via the flat-chain relop-as-branch; Icon smoke m2/m3/m4 = **6/6/6**, the first all-three-modes pass.) A new GZ rung is not "done" until its mode-2 oracle is green AND mode-3 + mode-4 are tracked against it.
- **Canonical harnesses already wired for all three:** `scripts/test_smoke_icon.sh` (per-frontend gate) and `scripts/test_crosscheck_icon.sh` (mode-consistency). Any NEW or edited Icon test script MUST run `--interp`, `--run`, AND `--compile` (mode-4 via the asm→assemble→link→run path; if `out/libscrip_rt.so` is absent or `--compile` emits nothing, mode-4 simply fails/tracks — never silently skipped). The per-rung `test_icon_ir_rung_*.sh` scripts are mode-2 oracle tests today; migrate each to all-three as it is next touched.
- **What "mode-3 == mode-4" means — the equivalence LEVEL (verified by disassembly 2026-05-31, Sonnet 4.8):** the two modes share the IDENTICAL codegen pipeline — `icn_flat_chain_build` (m3) and `icn_flat_chain_build_text` (m4) both call the SAME `codegen_flat_chain_body` → `walk_bb_flat` → templates; the ONLY fork is `emitter_init_binary` vs `emitter_init_text`, which selects the `MEDIUM_BINARY` vs `MEDIUM_TEXT` arm *per instruction*. Slot allocation (`bb_slot_alloc16`/`bb_varslot`), the operand-ref DFS, and the γ/ω branch wiring are all medium-independent → IDENTICAL instruction stream (same mnemonics, operands, order, control flow) and IDENTICAL slot offsets. **The maintained bar is codegen-path + instruction + behavioral parity** (exactly what `test_crosscheck_icon.sh` checks: `--compile agrees`). It is **NOT byte-identical machine code, and never has been**: the `MEDIUM_TEXT` arm emits mnemonic asm and lets `gas` relax in-range jumps to short rel8 (`eb`/`7x`), while `MEDIUM_BINARY` hand-encodes every jump as near rel32 (`E9`/`0F 8x` + 4 bytes). Census on `if x>5 then write("big") else write("small")`: assembled m4 `.text` = **16 short + 2 near**; m3 slab = **all 18 near**. This near-vs-short divergence is PERVASIVE — present in every box (LIT_I/VAR/CALL/relop alike), a property of the text backend, not a per-rung bug; GZ-8 introduced none of it (its relop's BINARY opcode byte and TEXT mnemonic both come from the one `gen_rel_fail_jcc` switch, so they cannot drift). **When verifying a rung's m3≡m4, compare the disassembled INSTRUCTION stream + behavior, not raw bytes.** TRUE byte-identity (if ever required) would need a branch-relaxation pass in the BINARY emitter (choose short rel8 when the target is in range) OR `.byte`-level emission in the TEXT arm — a SHARED-emitter change across all three languages (lockstep per the TEMPLATE-ONLY FACT RULE); tracked here, not scheduled.
- Mode-4 needs `out/libscrip_rt.so` (`make libscrip_rt`) and `gcc`; the harnesses degrade gracefully (mode-4 FAIL/TRACK) when either is missing so the mode-2 HARD gate still runs in any environment.

### Rung ladder (HELLO WORLD up — each gated, stackless, no `rt_push`/`rt_pop`)

- [x] **GZ-0 — Scaffold + gates.** Pin the no-stack gate above into `scripts/`. Confirm the
  per-box slot idiom (`&pBB->value`) is the value-storage primitive. Decide the slot/arena
  conventions by reading `emit_arbno` + one full pattern-node body in the archived `emit_x64.c`
  end-to-end, and `test_icon.c` for the Icon arithmetic shape. No code change beyond the gate script.
- [x] **GZ-1 — `write("hello")`.** One box, literal value in its own slot, write reads the slot.
  No push. m2==m3, zero-SM, no-stack gate = 0 for this box family.
- [x] **GZ-2 — `write(42)`.** Literal-N template (PDF §4.1): `lit.start: lit.value ← N; goto succeed`.
  Value in `&lit->value`. write reads it.
- [x] **GZ-3 — `write(1 + 2)`.** plus template (PDF §4.3): `plus.value ← E1.value + E2.value`,
  read from the two child slots. No operand push/pop.
- [x] **GZ-4 — `every write(1 to 3)`.** to template (PDF §4.4): `to.I`, `to.value` slots; β
  re-pumps via `to.resume: to.I++`. Mirror `test_icon.c` `to1`. **mode-2 oracle DONE** (session 8).
  **mode-3 stackless DONE (session 9):** `bb_to.cpp` MEDIUM_BINARY literal-bounds arm rewritten
  from single-shot to the full stackless pump (`β: cur=[r12+off]; inc; store; if cur>hi → ω; jmp γ`),
  lo/hi sealed RO `[rip+disp]`. `scrip.c icn_rt_arity` gained `IR_EVERY → 1` so the ring→tree adapter
  reconstructs `every(body)`. m2==m3 `1\n2\n3`, dump-bb count=0, FACT 0, no-stack 113, one-reg-frame 20.
  Icon smoke m3 4/6→5/6 (`every` green). No `rt_push`/`rt_pop` added.
- [x] **GZ-5 — `every write(1 | 2 | 3)`.** alt: arms fail-chain via ω, each arm γ→ALT funnel
  (JCON `ir_a_Alt` / lower2 `wire_alt`). **mode-2 oracle DONE (session 9):** was infinite-looping
  (`1 1 1…`) — the `every` ival==0 driver restarted forward through the success port so the first
  literal re-succeeded forever. Fix in `bb_exec.c` IR_EVERY ival==0: a guarded branch firing ONLY
  when `start` heads a sibling alt-chain (`start->ω->γ == start->γ`) AND all arms are single-shot,
  resuming from the second arm (`start->ω`, since the main exec loop already produced the first).
  `to`/all-else fall through BYTE-IDENTICAL. Corpus 31→34 (+`rung13_alt_alt_{every_write,filter,int}`),
  zero regressions, m2 6/6 HARD. **(session 10 update:** that guarded all-single branch was REMOVED when GZ-6
  made the chain self-drive; `every write(1|2|3)` now flows through the self-advancing IR_ALT collector and the
  EVERY terminator — still m2 green, `→ 1,2,3`, `(1 to 2)|(5 to 6)`→1,2,5,6.)
  **mode-3 STILL fork-blocked** — the ring→tree adapter NULLs `IR_ALT`
  (arms hang off ω-branches, not the γ-chain), so mode-3 emits nothing (no false-pass, no crash).
  NEXT (mode-3 alt): (1) `icn_ring_to_tree` special-case `IR_ALT` — pop first arm off the postfix
  stack, set `ALT.α`, gather ω-siblings while `sibling->γ==ALT`, terminate the last arm's ω for
  `flat_drive_alt_icn`; (2) `bb_alt.cpp` — replace absolute `&pBB->counter` with a stackless
  `[r12+off_c]` counter that stores the active arm's literal into `[r12+off_v]`; (3) `bb_call.cpp` —
  `write(alt)` reads `[r12+off_v]` instead of `rt_pop_write_any_nl`.
- [x] **GZ-6 — `every write(5 > ((1 to 2) * (3 to 4)))`.** The paper's full example. Must be
  byte-identical to `test_icon.c` output AND structurally mirror Figure 1 (nine four-port
  templates, no stack). This rung proves stackless generator-nesting end to end. MILESTONE.
  **mode-2 oracle DONE (session 10):** `→ 3,4` (verified; `(1 to 2)*(3 to 4)`→3,4,6,8; `5>(1 to 4)`→1,2,3,4;
  `(1|2)+(10|20)`→11,21,12,22). FIVE-part fix, grounded in jcon `irgen.icn` (ir_a_Every L309 / ir_a_Alt L167 /
  ir_a_Binop L471 / ir_a_Call L360). (1) `lower.c` `wire_det_builtin1`: CALL.resume → arg.resume (`aβ`) so the
  write re-pumps a generator argument (jcon `call.resume → last-arg.resume`) — GATED via `g_icn_postfix_resume`
  (mode-2 only; see seam below). (2) `lower.c` `v_binop`: each operand → its OWN named slot in the `operand_aux`
  sidecar (jcon `ir_a_Binop` opfn reads `[lv,rv]`; replaces the documented push-only-ring mis-count). (3)
  `bb_exec.c` IR_BINOP postfix arm reads the two named slots when present, ring-peek fallback otherwise. (4)
  `bb_exec.c` IR_EVERY ival==0 is now a pure terminator (returns γ): with the resume ports wired the generator
  chain SELF-DRIVES under the top-level port-walker and the EVERY node is reached exactly once via gen.ω — the
  old general/all-single restart loop was double-driving. (5) `bb_exec.c` IR_ALT postfix collector now
  self-advances on resume (re-pumps a generator arm via the `operand_aux` arm-value nodes, else fail-chains to
  the next alternative), and `lower.c` `wire_alt` stores the arm VALUE nodes (not resumes) in `operand_aux`.
  **mode-2/mode-3 SEAM (`g_icn_postfix_resume`, lower.c; set in scrip.c only for `--interp`+`is_icon`):** edit (1)
  introduces a CALL→arg.resume cycle in the shared γ-chain that the mode-3 ring→tree adapter (`icn_ring_to_tree`)
  cannot yet walk (it overflows the linear-chain guard → NULL). Gating (1) to mode-2 keeps the mode-3 IR
  BYTE-IDENTICAL to the pre-GZ6 graph (CALL.resume=ω_in, gen.γ=EVERY) → mode-3 `every write(1 to 3)` restored,
  no regression. Edits (2)–(5) are mode-2-only (operand_aux + bb_exec.c; the mode-3 flat emitter reads neither).
  **mode-3 STILL fork-blocked** — both GZ-5 `IR_ALT` and now GZ-6's CALL-resume cycle need the adapter reworked;
  that IS Lon's Path-1/Path-2 fork (rewrite the mode-3 emitter to walk the γ-chain/ring natively vs per-shape
  scaffold). Removing the seam + teaching the adapter the resume topology is the next mode-3 step.
- [x] **GZ-7 — `x := 42; write(x)`.** Flat slot for `x` (the archive's flat .bss var model). **mode-2
  oracle already passing.** **mode-3 + mode-4 DONE (flat goto-graph named-slot model, no ring — Lon's
  test_sno_*.c law for modes 3/4):** built `icn_flat_chain_build` (+ text twin `icn_flat_chain_build_text`)
  and `codegen_flat_chain_body` in `emit_bb.c` — a two-pass emitter that (1) postfix-analyzes the γ-chain to
  record each consumer's operand REFERENCES on α/β (NOT for re-walk — `icn_chain_operand_refs`), then (2)
  BFS-emits EVERY box exactly once, wired by its native γ/ω ports (jmp rel32), via `g_icn_flat_chain`-gated
  slot-leaf template arms. Each box writes its result into its OWN ζ=r12 frame slot; a consumer reads the
  producer's slot directly (`bb_slot_get`) — the `str_t POS0; … = POS0` model. A variable `x` is ONE named
  frame slot (`bb_varslot`, name-keyed) shared by its IR_ASSIGN writer and IR_VAR readers. **NO ring** (the
  AG ring is the mode-2 oracle's model ONLY); **NO value stack.** Four templates gained flat-chain slot arms
  (BINARY+TEXT): `bb_lit_scalar.cpp` (LIT_I writes a 16-byte DESCR — `{v:DT_I,slen:0}` + int — to its slot),
  `bb_var.cpp` (named var slot → own slot, 16-byte copy), `bb_assign.cpp` (RHS producer slot → named var
  slot; restricted to DESCR-producing RHS = LIT_I/VAR, binop-RHS falls through loud — GZ-8 adds the binop
  DESCR producer), `bb_call.cpp` (`write(E)` reads operand slot by value into rdi:rsi → new by-value
  `rt_write_any_nl(DESCR_t)` in `rt.c`, type-dispatching int/real/string). Driver (`scrip.c`) routes Icon
  mode-3/mode-4 to the chain builder when `icn_ring_to_tree` can't linearize. **m2==m3==m4 `42`** (verified
  assembled+linked+run). Icon smoke **m2 6/6 HARD · m3 5/6 · m4 0/6→5/6** (mode-4 was severed at session
  start when libscrip_rt was absent — the flat-chain TEXT arms rebuilt it for write_str/write_int/arith/
  string_op/every). GATES: FACT 0 · no-stack 114 ≤ 127 · one-reg-frame 20 ≤ 20 · prove_lower2 PASS ·
  template-purity advisory 7 (byte-identical before/after) · Prolog m2 5/5 unaffected. NO `rt_push`/`rt_pop`
  added; the chain arms are register-relative `[r12+off]` only.
- [x] **GZ-8 — `if`/relop control, relop routes its OWN γ/ω. DONE (2026-05-31, Sonnet 4.8).**
  `x:=10; if x>5 then write("big") else write("small")` → **m2==m3==m4 `big`**; Icon smoke
  **m2 6/6 HARD · m3 5/6→6/6 · m4 0/6→6/6** (first time all three modes 6/6). The branch is BAKED
  INTO THE RELOP (grounded in `test_icon.c` `mult_succeed: if (x5_V<=mult_V) goto mult_resume; else …
  goto succeed` — the fail-jump is the NEGATED relation): NO `LAST_OK` flag, NO `BB_IF` router,
  NO `rt_acomp`/value stack. The `IR_IF` node is vestigial in the γ/ω graph (the relop carries γ→then,
  ω→else directly; verified `IR_IF` is never collected by the flat-chain BFS). FOUR edits, all gated to
  mode-3/4 emission (mode-2 oracle `bb_exec.c` untouched → HARD gate safe; SNOBOL4/Prolog byte-identical,
  stash-verified m3 2/6 & 5/5 unchanged): (1) `bb_binop.cpp` flat-chain numeric-relop arm —
  `mov rax,[r12+sa+8]; mov rcx,[r12+sb+8]; cmp rax,rcx; jcc ω; jmp γ` (BINARY+TEXT), operand int payloads
  at `[r12+slot+8]` via `bb_slot_get(α)`/`bb_slot_get(β)`, fail-jcc per op (`<`→jge,`<=`→jg,`>`→jle,
  `>=`→jl,`=`→jne,`~=`→je); relop value discarded in if-context (no slot write). (2) `walk_bb_flat`
  IR_BINOP — flat-chain relop routes to FILL (emit only the relop box; operands are sibling chain boxes,
  NOT re-walked via `flat_drive_binop_tree`). (3) `icn_chain_operand_refs` BFS→DFS (γ-first, then ω for
  binops) — BFS interleaved a relop's two arms (then-lit, else-lit, then-call, else-call) breaking the
  linear postfix stack so branch-arm CALLs grabbed the wrong operand; DFS keeps each arm contiguous so
  each `write(strlit)` resolves its true γ-predecessor LIT_S. (4) `bb_var.cpp` `bb_slot_alloc`→`alloc16`
  (VAR writes a 16-byte DESCR; the 8-byte reservation let a following producer's slot overlap VAR's int
  payload at +8, corrupting a two-operand relop). Verified all 6 operators × both arms (14 cases) m2==m3;
  m4 binary assembled+linked+run `big`/`small`. GATES: FACT 0 · no-stack 114≤127 · one-reg-frame 20≤20 ·
  prove_lower2 PASS · template-purity advisory 7 (unchanged) · crosscheck 4/4 (if_expr m4 agrees) ·
  Prolog m2 5/5 · broker 20. NO `rt_push`/`rt_pop` added. OBSERVATION (pre-existing, out of scope): a
  bare `if C then E` (no else) whose cond fails does not continue to the next statement in EITHER m2 or
  m3 (consistent; an IR_SEQ statement-failure-continuation quirk in the mode-2 oracle, untouched here).
- [x] **GZ-9 — `while`/`until`/`repeat` (+ `break`/`next`). DONE (2026-05-31, Sonnet 4.8) — m2==m3==m4.**
  All three loop constructs self-drive under the top-level port-walker (Model B: the loop NODE is a pure
  forwarder/terminator; the cond's OWN relop ports + the body's γ/ω edges carry the loop — NO internal
  exec-arm driver loop, NO `FRAME.loop_*` flags, NO router, NO value stack). Grounded in JCON `ir_a_While`
  (cond.γ→body, cond.ω→loop-exit) / `ir_a_Until` (cond.γ→exit, cond.ω→body) / `ir_a_Repeat` (body.γ/ω→
  body.start) / `ir_a_Break` / `ir_a_Next`. Icon smoke **m2 6/6→9/9 · m3 9/9 · m4 9/9** (added `while`,
  `until`, `repeat_break`). SEVEN edits (Icon-gated; SNOBOL4 m2 7/7 & Prolog m2/m3 5/5 unchanged):
  (1) `lower.c` `v_until` rewritten to structurally mirror `v_while` (cond.γ→until-node/exit, cond.ω→body)
  — this also FIXED A PRE-EXISTING MODE-2 ORACLE BUG (`until` previously produced EMPTY output for every
  input, because the old wiring hung the body off `IR_UNTIL.α` which neither the port-walker nor the
  flat-chain BFS visits, and the `bb_exec.c` IR_UNTIL arm treated `α` as the cond). (2) `lower.c` `v_repeat`
  rewritten to self-drive (`rp->γ = body-start` as the loop-back edge; the only NORMAL exit is a `break`).
  (3) `lower.c` `with_loop(cx, γ_in, reentry)` now wraps the body lowering of all three loops (was defined
  but UNUSED), so `break`→`cx.loop_ω`(=γ_in, the loop's exit continuation) and `next`→`cx.loop_next`(=cond/
  body re-entry). (4) `lower.c` new `v_loop_break`/`v_loop_next` + dedicated `TT_LOOP_BREAK`/`TT_LOOP_NEXT`
  dispatch cases (Icon-gated) lowering to `IR_BREAK`/`IR_NEXT` forwarders with γ==ω==target — and the STALE
  duplicate `TT_LOOP_BREAK/NEXT` labels in the `TT_FNC` fall-through group were removed (they fell into the
  call handler — wrong, and never fired since these nodes were never produced before). (5) `bb_exec.c`
  `IR_BREAK`/`IR_NEXT`/`IR_REPEAT` exec arms rewritten as pure port-forwarders (break/next → `bb->γ`;
  repeat → `bb->α`); the old `FRAME.loop_*`-flag internal-driver bodies (Model A — dormant, since the
  lowering never produced these nodes) deleted. (6) `bb_binop.cpp` GZ-9 flat-chain integer-ARITHMETIC arm
  (BINARY+TEXT) — `i := i + 1` etc.: reads each operand's int payload `[r12+slot+8]` (`bb_slot_get`),
  computes register-to-register (ADD/SUB/MUL/DIV/MOD uniform — rax op rcx; DIV/MOD via `cqo;idiv rcx`),
  writes a re-tagged `{DT_I,result}` 16-byte DESCR to its OWN `bb_slot_alloc16` slot (the `test_icon.c`
  `mult_V=a*b` named-slot model — NO value stack, NO ring). (7) `emit_bb.c` `walk_bb_flat`: flat-chain
  ARITH binops route to FILL (operands are sibling chain boxes already BFS-collected — do NOT re-walk via
  `flat_drive_binop_tree`, which would duplicate them with fresh slots and clobber the slotmap); added
  `IR_BREAK`/`IR_NEXT`/`IR_REPEAT` cases as pure `jmp γ` forwarders. Also `bb_assign.cpp` flat-chain RHS
  guard widened to accept `IR_BINOP`, and `emit_core.c` IR_ASSIGN routing to `bb_sno_assign` gated
  `!g_icn_flat_chain` (so Icon flat-chain ASSIGN reaches `bb_assign`, not the SNOBOL4 path). Verified
  m2==m3==m4: `while` × `<`,`>`,`<=`,`>=` with ADD/SUB/MUL; `until i>3`→1,2,3 & `until i<=0`→5,4,3,2,1;
  `repeat{if i>=3 then break else write(i); i:=i+1}`→0,1,2; `while{...; if i=5 then break else write(i)}`
  →1,2,3,4. GATES: no-stack **114 ≤ 127** (break/next/repeat add ZERO push/pop — pure forwarders),
  one-reg-frame **20 ≤ 20**, FACT 0, ZERO-SM (dump-sm count=0), prove_lower2 PASS, crosscheck 4/4.
  **OUT OF SCOPE (pre-existing, documented at GZ-8):** a bare `if C then break` (no `else`) whose cond
  FAILS does not fall through to the next statement in m2 OR m3 (the IR_SEQ statement-failure-continuation
  quirk) — so `break`/`next` must use the `if … then break else …` form until that quirk is fixed. The
  optional `break E` expression value is lowered as a plain transfer (E-value-as-loop-result is a later
  refinement). `next` self-tested via the same forwarder path as `break`.
- [ ] **GZ-10 — user procedure as a four-port FLAT box** (not a C-stack `call`). Model on
  `test_sno_3.c`: `(ζζ, entry)` calling convention, frame lazily allocated, `_λ` landing pad.
  Recursion depth lives in per-box arenas / heap frames, never a value stack.
  **mode-2 oracle DONE incl. RECURSION (2026-06-01, Opus 4.8 — `602e107`):** user procs + `return E`
  + RECURSION all run in mode-2. Verified: non-recursive `answer()`→42, `id(99)`→99, `double(21)`→42,
  `add(3,4)`→7, `cmp(0)`→111, `cmp(5)`+else→222; recursive `fact(5)`→120, `fib(10)`→55, `sumto(100)`→5050,
  `ack(2,3)`→9, mutual `iseven(10)`/`isodd(7)`→1, and the SAME proc called 3× (`fact` →120,720,24 — proves
  the AST is no longer consumed/mutated). **THE RECURSION BLOCKER FIX (the recommended `lower_sc` approach):**
  the prior `dval==3.0` exec arm bound param names by walking the LIVE `proc->c[1]` (TT_VLIST) AST at every
  activation; on 2nd+ re-entry the shared param `TT_VAR` nodes read EMPTY (mutated by the nested
  arg-subgraph/scope path), so `args[0]` resolved wrong and recursion degenerated (`fact(5)`→5). TWO edits,
  both Icon-gated, mirroring SNOBOL4's `proc_table[].lower_sc`: (1) `lower_program.c` — after
  `lower_icon_body` succeeds, capture the proc's param names into `lower_sc` ONCE via `lp_strdup` (stable GC
  strings, slot-keyed; inside the `LANG_ICN` block); (2) `bb_exec.c` `dval==3.0` arm — bind `env[slot]` from
  `lower_sc` instead of re-walking `proc->c[1]` each call. The AST is NEVER read at exec time → no mutation
  dependency → per-activation correct. Earlier GZ-10 PARTIAL edits (still in place): `lower.c`
  `TT_RETURN`/`TT_NRETURN`→`IR_RETURN` (value chain γ→return, AG-ring read); `lower.c` `TT_FNC`
  user-proc-call→`IR_CALL dval=3.0` (args as isolated value sub-graphs on `counter`, jcon `ir_a_Call`);
  `bb_exec.c` per-activation `GenFrame` + ring/snapshot-protected `bb_exec_once` + `g_ir_return_val` harvest;
  `bb_exec.c` `IR_RETURN` generic arm reads AG ring when α==NULL; `scrip_ir.c` `bb_reset` preserves `counter`
  for `IR_CALL dval==3.0`; `lower.c` `lower_value_subgraph` inherits caller lang. **GATES: Icon m2 10/10
  HARD (added `proc_recursion` `fact(5)`→120 smoke case) · m3 9/10 · m4 9/10 (proc_recursion m3/m4 not yet
  built — that's the GZ-10 modes-3/4 work below); SNOBOL4 m2 7/7 · Prolog m2/m3 5/5 · broker 23 · FACT 0 ·
  no-stack 117≤127 · one-reg-frame 20≤20 · prove_lower2 PASS · ZERO-SM 0.** **OUT OF SCOPE (pre-existing,
  NOT GZ-10):** bare `if C then E` (no else) cond-FALSE fails the whole proc instead of falling through —
  the documented GZ-8/GZ-9 IR_SEQ statement-failure-continuation quirk; workaround = explicit `else` (all
  recursion tests above use the `if … then … else …` form). **modes-3/4 FOUNDATION — ZERO-ARG DONE
  (2026-06-01, Opus 4.8 — `da3a786`):** a zero-arg user procedure now runs STACKLESS in mode-3 —
  `write(answer())` → **m2 == m3 == 42** (m4 deferred). Landed the `test_sno_3.c` `(ζζ,entry)` convention:
  `rt_icn_call_proc_descr(name,nargs)` allocates a FRESH frame from a depth-indexed arena (recursion-safe
  per-activation storage, NOT a value stack), binds staged args into param slots, runs the callee slab, and
  returns the callee's RETURN-slot DESCR (`rax:rdx`); frame layout `[0,16)`=return DESCR, param i at
  `16*(i+1)`. New: `icn_flat_chain_build_proc` (proc body built with that convention — reserves return slot,
  pre-seeds param varslots); `icn_chain_arity(IR_RETURN)=1` so `RETURN.α`=value producer; `IR_RETURN`/`IR_CALL`
  in the flat chain route to FILL (no re-walk, the GZ-8/9 sibling-slot pattern); `bb_return.cpp` flat arm
  (producer slot → frame return slot `[0]`); `bb_call.cpp` flat user-proc arm (call helper, store DESCR to own
  slot; mode-4 TEXT is a loud abort stub); driver builds proc slabs eagerly under the ζ-frame prologue and
  registers their fns. Also landed `rt_icn_arg_stage(idx,v)` — the transient single-call arg marshalling
  primitive (DESCR by value in `rsi:rdx`, consumed by the helper on entry before any nested call), ready for
  the arg-emission hook. **GATES: Icon m2 11/11 HARD (added `proc_zeroarg` regression case) · m3 10/11 · m4
  9/11 (proc_recursion m3/m4 still red — needs arg emission); SNOBOL4 m2 7/7 · Prolog m2 5/5 · Raku m2 22/22
  · no-stack 117≤127 · one-reg-frame 20≤20 · prove_lower2 PASS.**
  **modes-3/4 ARGS + RECURSION — DONE (2026-06-01, Opus 4.8 — `5249921`):** user procedures WITH arguments,
  recursion, and mutual recursion now run STACKLESS in mode-3, m2==m3. `proc_recursion` smoke flips PASS →
  **Icon m3 11/11**. Three Icon-flat-chain-gated edits + a driver two-phase split: (1) `emit_bb.c`
  `flat_drive_icn_userproc` + `flat_emit_arg_subchain` — a dval==3.0 call's args are isolated value
  sub-graphs on `counter` (NOT the γ-chain); for each arg the driver runs `icn_chain_operand_refs` then emits
  the WHOLE sub-graph as an inline flat chain (BFS over γ + BINOP.ω, the `codegen_flat_chain_body` model) so
  every producer box emits once and claims its ζ=r12 slot. ROOT BUG FIXED: a bare `walk_bb_flat(entry)`
  emits ONLY the entry node, so a multi-node arg like `n - 1` (VAR/LIT/BINOP) never emitted its BINOP and
  staging read a garbage slot. (2) `icn_chain_arity` — a dval==3.0 call is a LEAF producer (arity **0**) in
  the flat-chain model, like dval==2.0: args live on `counter`, NOT the γ-chain. The old `(int)n->ival`
  (legacy value-stack `flat_drive_call_userproc` path) made `fact(n-1)` wrongly pop the sibling `n` off the
  operand stack, corrupting the enclosing `n * fact(n-1)` binop's α (→ a RETURN/garbage slot → `rt_arith`
  abort). (3) `bb_call.cpp` dval==3.0 arm — emit per-arg staging (`mov edi,i; mov rsi,[r12+slot]; mov
  rdx,[r12+slot+8]; call rt_icn_arg_stage`) before `rt_icn_call_proc_descr`, reading each arg sub-graph's
  TERMINAL producer slot (new `bb_chain_terminal`: follow γ to the node `lower_value_subgraph` left with
  γ==NULL); DESCR = two INTEGER eightbytes → SysV idx in edi, eb0 in rsi, eb1 in rdx. (4) `scrip.c` — split
  proc registration and slab emission into TWO phases so a call to a forward / mutually-recursive proc
  (`iseven` calling later-registered `isodd`) passes the `rt_proc_is_registered` gate during slab build.
  Verified m2==m3: `id(99)` `double(21)` `add(3,4)` `f(g(5))` `fact(5)`=120 `fib(10)`=55 `ack(2,3)`=9
  `sumto(100)`=5050 mutual `iseven(10)`/`isodd(7)`=1 `fact` called 3× =120,720,24 (AST not consumed/mutated).
  **GATES: Icon m2 11/11 HARD · m3 11/11 · m4 11/11 (GZ-10 mode-4 DONE `b8f48bf`); SNOBOL4 m2 7/7 · Prolog m2 5/5 m3 5/5 · no-stack 117≤127
  · one-reg-frame 20≤20 · sm_dead 0 · prove_lower2 PASS · ZERO-SM 0.** (SNOBOL4 m3 FAIL=1 pre-existing,
  identical at `da3a786`.) **GZ-10 mode-4 DONE (`2de9ff5`, Claude Sonnet 4.6):** proc slabs emitted as
  named GAS asm (`icn_proc_<name>_α` globally-visible labels), startup stub (`icn_proc_startup`) calls
  `rt_proc_set_fn` to wire each name→slab before `main_α`; `bb_call.cpp` MEDIUM_TEXT arm replaced
  `abort` stub with PLT-relative staging (`rt_icn_arg_stage@PLT` per arg + `rt_icn_call_proc_descr@PLT`);
  `g_flat_node_id` no longer reset between proc slabs so xchainN labels are unique; `rt_proc_set_fn`
  creates a new entry when name not yet registered (needed for mode-4 startup). m2==m3==m4 for
  `proc_zeroarg` (42) and `proc_recursion` (fact(5)=120). **Icon smoke m2/m3/m4 11/11/11 — first
  all-three-modes 11/11/11.** **BARE-IF-NO-ELSE DONE (`b8f48bf`, Claude Sonnet 4.6):** `lower_icon_body` now wires
  each non-last statement's `ω_in = next_a` (the NEXT statement's entry) per JCON `ir_a_Compound`
  lines 1253-1254; last statement -> PFAIL. A bare `if c then e` whose cond fails silently
  falls through to the next statement. Smoke 11->12 m2/m3/m4 (+`bare_if` case).
  **NEXT:** GZ-DEFER (EVAL/CODE/`*P` deferred patterns, `test_sno_3.c` model); then GZ-11+
  corpus features stackless.
- [ ] **GZ-11 SUSPEND — user-defined generators via `suspend E do BODY`** (jcon `ir_a_Suspend`).
  **mode-2 oracle DONE (2026-06-01):** a procedure that `suspend`s is now an Icon GENERATOR; `every write(gen())`
  re-pumps it for successive values. Grounded in canonical `refs/jcon-master/tran/irgen.icn` `ir_a_Suspend`
  (lines 937-978: `p.expr.ir.success -> Succeed(susp, t)`; `t -> run body -> re-seek E`; `p.expr.ir.failure ->
  p.ir.failure` = proc fails when E exhausts). **Mode-2 model = the established EAGER-DRAIN idiom** (same as
  IR_GATHER / map-grep): while a proc activation's body runs, each `IR_SUSPEND` node appends its value(s) to a
  per-activation collection buffer (`SuspendBuf g_suspend_buf`, save/restored so nested suspending calls each
  collect into their own frame), running the `do` body between yields; when the body finishes, the `IR_CALL`
  (dval==3.0) site harvests the buffer — NON-empty => the call is a generator, the collected list cached on a
  node-keyed sidecar (`susp_gen_cache`, keyed by call IR_t* so two `every` sites get independent lists), one
  value yielded per re-entry via the call node's `state`/`counter` cursor (exactly like IR_TO); EMPTY => ordinary
  deterministic call (single `g_ir_return_val`, unchanged). **Five edits:** (1) `lower.c` dedicated Icon
  `TT_SUSPEND` arm -> `IR_SUSPEND` (dval=1.0, E -> `counter` value-subgraph, `do` body -> `ival` subgraph) +
  Icon no-op arm for `TT_LOCAL`/`TT_GLOBAL`/`TT_STATIC_DECL` (declarations are pass-through `IR_SUCCEED`) +
  `icn_proc_is_generator(name)` helper wiring a generator call's β (resume) -> the call node itself (resumable),
  a deterministic call's β -> ω (bounded); (2) `lower_program.c` `proc_subtree_has_suspend`/`proc_body_has_suspend`
  + a PRE-PASS that marks `proc_table[].is_generator` for ALL Icon procs BEFORE any body is lowered (a caller may
  lower before its suspending callee); (3) `bb_exec.c` `SuspendBuf` + `susp_gen_cache` + `IR_SUSPEND` exec arm
  (enumerates E — re-pumps only if `!ir_is_single_shot(E.entry)`, else one value — runs `do` after each) +
  `IR_CALL` dval=3.0 generator harvest/resume; (4) `scrip_ir.c` added `IR_SUSPEND` to the `bb_reset` counter-
  preserve whitelist (its `counter` holds the E subgraph); (5) `prove_lower2.c` supplies a local `g_stage2`
  (proc_count=0) so the standalone topology harness links the new `icn_proc_is_generator` g_stage2 reference.
  Verified m2: `rung03_suspend_gen` (1,2,3,4), `_filter` (downto 4,3,2,1), `_compose` (1,2,3,1,2 — independent
  re-runs), `_return` (6,14), `_fail` (1,3). **GATES: Icon smoke m2/m3/m4 12/12/12 (HARD green) · corpus
  `test_icon_all_rungs` 90 -> 107 PASS (+17) · no-stack 117<=127 · one-reg-frame 20<=20 · FACT 0 · C-byrd-box 0 ·
  prove_lower2 64/64 PASS · Prolog m2 5/5 m3 5/5 · SNOBOL4 `hi-sno` OK · unified broker 24/42 (identical to
  session start — no regression).** mode-2 ORACLE ONLY (emits zero x86; the emission gates are untouched);
  native mode-3/4 `suspend` is a later rung. **OUT OF SCOPE:** `suspend E` where E is a multi-value generator
  consumed WITHOUT an enclosing loop (the per-visit enumeration handles it, but corpus coverage is the `while
  ... suspend` form); co-expression `@`/`^` resume; `suspend` inside nested control beyond `while/until/every`.
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.

---

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---

**Reset:** 2026-05-30 (GROUND ZERO 3). All prior IBB-* rungs (the two vstack-based builds) removed
from this file — they were the regression, not a foundation. The build now starts again from
`write("hello")` on the stackless model. Demolition of the Icon value-stack consumers is the first
step (see Watermark).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/test_sno_1.c` · `.github/test_sno_3.c` · `.github/jcon_irgen.icn` · `SCRIP/refs/bb/Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` · `SCRIP/archive/backend/emit_emitters/emit_x64.c` (prior working stackless emitter).

---

## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.** **There is no value stack.**

- Mode 2: driver detects Icon and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. Icon SM stream is empty.
- Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in mode-4, **no `rt_push`/`rt_pop` value-stack traffic**.

Per `test_icon.c`: every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels wired by flat `goto`, and every value lives in a named per-box slot read directly by its consumer. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes emitted for an Icon program.** No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, nothing. Driver calls `bb_exec_once(main_bb_graph)` directly.

Completion tests:
```bash
./scrip --dump-sm any_icon_program.icn        # ; SM_sequence_t  count=0
./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'   # 0
```

## ⛔ CONSULT CANONICAL SOURCES (JCON + Icon)

**Every time a question arises during new SM/BB or feature work — port topology, resume/backtrack wiring, builtin semantics — `grep`/read the relevant canonical procedure FIRST and ground the implementation in it.** Do NOT assume; you do not know until you check. Authority: `refs/jcon-master/tran/irgen.icn` (`ir_a_Every`, `ir_a_Limitation`, `ir_a_Call`, `ir_a_Alt`, … define control-flow/ports) and `refs/icon-master/src/runtime/*.r` (`fstranl.r`, `ocomp.r`, `fscan.r`, … define runtime/builtin semantics). The mode-2 oracle `bb_exec.c` is a transcription, not the source of truth — when they disagree, the canonical source wins. Full statement in `RULES.md`. (Extract the uploaded `icon-master.zip` / `jcon-master.zip` into `refs/` at session start if not present.)

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp  /tmp/rung_NN.icn  > out_m2.txt
./scrip --run     /tmp/rung_NN.icn  > out_m3.txt
diff out_m2.txt out_m3.txt    # must be empty

./scrip --dump-sm /tmp/rung_NN.icn  # ; SM_sequence_t  count=0

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# NO-STACK gate (GROUND ZERO 3): Icon emission path contains ZERO value-stack push/pop.
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target 0 for every Icon box family as it is rebuilt
bash scripts/test_gate_icn_no_stack.sh            # pinned ratchet (baseline lowers as families rebuild)

# ONE-REGISTER FRAME gate (ICON STACKLESS ONE-REGISTER FRAME FACT RULE, RULES.md): all per-box
# storage is [reg+off] into ONE per-sequence local frame — NO absolute &pBB->slot immediates.
bash scripts/test_gate_icn_one_reg_frame.sh       # pinned ratchet; target 0 as families migrate

# Smokes (must hold)
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families. **They keep their SM and their value stack (`g_vstack`). The stack removal is Icon-only.**
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md`.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4.
- Reintroduce the value stack for Icon value flow in any form (SM vstack, `vstack`, `r12`-as-TOS, `rt_push_*`/`rt_pop_*`).

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

---


## RATIFIED — UNIFIED REGISTER LAYOUT (2026-05-30, session 3)

**Context (2026-05-30):** Icon is *not* in proper development yet — GROUND ZERO 3 only started scaffolding (GZ-0/1/2), not real development. Before going further we designed AND RATIFIED ONE x86-64 register layout for all 6 languages (this session). The layout below is grounded in the archive + live code and is now the reference all rungs build against; nothing is emitted onto it yet (first rung = R-HW below).

**The standardized floor is System V AMD64.** Caller-saved/scratch (9): RAX(ret), RCX/RDX/RSI/RDI/R8/R9(args), R10(static-chain), R11(PLT). Callee-saved (7): RBX, RBP(frame ptr), RSP(stack ptr), R12, R13, R14, R15. Int-arg order RDI,RSI,RDX,RCX,R8,R9; return RAX(+RDX). Claimable durable globals = RBX,R12,R13,R14,R15 (+RBP if -fomit-frame-pointer).

**Core principle:** anything that must live across a C `call` (our global-type pointers) goes in a CALLEE-SAVED register, so it survives every `rt_*` call with NO per-call save/restore. The only save is once, at a cross-language boundary. Today SNOBOL4's cursor is in caller-saved R10 (`&Δ`) → it pays a `push r10`/`pop r10` tax on every call; moving it to a callee-saved reg deletes that tax.

**Two kinds of BB locals, two bases (this is the existing convention, NOT new):**
- READ-WRITE locals → `[R12 + off]`. R12 is the BB-local frame base (Technique-2 / `M-T2-EMIT-SPLIT`: "r12 = DATA-block ptr; all locals [r12+offset]"). The ARBNO arena (`z`/`zo`), capture `saved_Δ`, Icon runtime values all live here. (NOTE: the Icon frame was wrongly wired to R15 this session — it must move to R12 to rejoin the convention. Also: live SNOBOL4 `BB_PAT_*` regressed to per-slot `movabs rcx,<abs>` and must come back to `[r12+off]`.)
- READ-ONLY locals → `[RIP + disp]` from the sealed blob (literals, baked addresses). No register.

**RATIFIED durable register layout — six callee-saved registers carry durable state. They survive every `rt_*` call via the SysV ABI; saved once at the cross-language boundary, never per-call:**
| reg | durable role | who |
|---|---|---|
| R12 | ζ — BB-local RW frame base, `[r12+off]` | all langs |
| R13 | Σ — subject base pointer (UPPERCASE = the fixed whole string) | pattern langs (SNOBOL4, Icon scan); free otherwise |
| R14 | δ — subject cursor / current offset (lowercase = the moving position) | pattern langs; free otherwise |
| R15 | Δ — subject length / end offset (UPPERCASE = the bound) | pattern langs; free otherwise |
| RBX | NV / globals base (named-value table) | all langs |
| RBP | RESERVED — untouched. The sixth durable reg ONLY if needed. Claimed (if ever) by NOT emitting a frame-pointer prologue — NOT by any compiler flag (the ABI makes RBP callee-saved unconditionally; `-fomit-frame-pointer` only governs the C runtime's own use of RBP, irrelevant to ours). NEVER used for value flow. | — |

Transition note: SNOBOL4/Snocone/Rebus/Raku keep a value stack (`g_vstack`) only until BB-converted; being pattern or non-Icon, they park it in an unused one of R13/R14/R15 (or memory) during transition. Icon and Prolog have NO value stack. Goal: `g_vstack` retires entirely (the BB win — see Premise).

**Caller-saved — clobbered by every call; scratch / ABI transport ONLY, never durable:**
| reg | role |
|---|---|
| RAX (:RDX) | result / γ value (DESCR_t lo:hi) |
| RDI | inbound ζ transport → copied to R12, then scratch |
| RSI | scratch. (α/β entry selector RETIRED from the Icon flat-wired path — β is a `jmp` target there. Still consumed ONLY by the Prolog brokered re-entry — `pl_runtime.c` / `pl_broker.c` `fn(ζ,β)` — until those become wired `jmp`s; selector dies then.) |
| RCX, RDX, R8, R9, R10, R11 | rt_* args + scratch |
| RSP | C control stack — the ONE stack. Return addresses + transient per-node scratch ONLY; NO value flow between boxes. |

**Subject model — four names, zero redundancy.** Σ base ptr (R13) · σ transient `Σ+δ` (scratch, computed at deref, not durable) · δ cursor (R14) · Δ length/end (R15). Casing carries meaning: UPPERCASE = the fixed whole/bound (Σ, Δ); lowercase = the moving position (σ, δ). Convention inherited from the snobol4jvm Clojure SNOBOL4. **The old `Ω` and `Σlen` BOTH retire into Δ** — verified to be one quantity under two names: `Ω` in the mode-2 `refs/bb/test_*.c` oracle, `Σlen` in the mode-3/4 emitter templates (`bb_pat_*.cpp`), always moved in lockstep (`rt.c` rebase sets `Σlen = sublen; Ω = sublen` together; saved/restored together). Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), not in a second length register — so ONE length reg suffices. Rename sweep: `Δ(old=cursor)→δ`, `Ω→Δ`, fold `Σlen→Δ`. Touch points: `bb_box.h` (decls), `xa_flat.cpp`/`emit_bb.c`/`emit_globals.h` (`TEMPLATE_ADDR_DELTA`/`ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN` macros, 63 `Σlen` sites), `refs/bb/*.c`. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`.

**Long-lived global state (grounded, the register-cache candidates):** `g_vstack[VSTACK_CAP]` (DESCR_t value stack, rt.c) · `Σ/Δ/Ω/Σlen` (bb_box.h subject scan) · `NV_GET_fn/NV_SET_fn` (named-value table = global variables, by name-hash) · `DESCR_t` (16-byte universal value) · the per-sequence RW frame.

**C BB BOX DEMOLITION (forbidden by RULES line 11; exemption REVOKED — `icn_bb_dcg` is NOT exempt, strike that clause).** A C BB box = a C function that (a) switches on entry α/β AND (b) wires four ports (α/β/γ/ω) inside. Those must be deleted and rebuilt as emitted wired graphs. VERIFIED genuine four-port C boxes (α AND β entry switch + γ and ω labels wired inside) = exactly TWO: `bb_deferred_var` (SNOBOL4 deferred, stmt_exec.c — `entry==α goto DVAR_α; entry==β goto DVAR_β;` + DVAR_γ/ω, re-enters child_fn) and `pl_cat_fn` (Prolog seq, pl_broker.c — `entry==α goto CAT_α; goto CAT_β;` + left_γ/ω, right_γ/ω). Exhaustive scan: only stmt_exec.c + pl_broker.c hold any `(void*,int entry)` fn with both γ and ω labels. NOT boxes by the test: `pl_choice_fn`/`pl_chunk_fn` (switch α/β but NO γ/ω labels — value-returning); `pl_true/fail/builtin/unify/head_unify/cut/alt/deferred_env_fn`, `icn_bb_oneshot`, `icn_fail_box` (single-entry leaves/wrappers); `pl_bb_dcg`, `icn_bb_dcg` (α-only bb_exec_once drivers). The x86 α/β selector (`cmp esi,0; jne β` in XA_FLAT_PROLOGUE + XA_ENTRY_DISPATCH) is LIVE: it's how brokered boxes are re-entered at β from `stmt_exec.c`/`pl_runtime.c`. It can only be deleted after those re-entries become wired `jmp`s.


## RUNG R-HW — `write("hello world");` (first rung on the ratified layout)

**Program:** `/tmp/rung_hw.icn` containing exactly `write("hello world")`.

**What it is — the read-only-string-literal write box (the string analog of GZ-2's `write(42)`).**
`"hello world"` is a READ-ONLY constant: it lives in the SEALED segment next to the box's own
blob and is read `[rip+disp]` (emit-time displacement — no patch, no abs immediate, no stack).
The box loads it into `rdi` and calls `rt_write_str_nl`. Because the value is a constant, this
rung uses NONE of the durable registers — no frame (R12), no subject regs (Σ/δ/Δ), no value
stack (there is none, ever). It exercises ONLY: sealed-blob RO data + `[rip+disp]` read + one
`rt_*` call + the four-port shell (γ → halt; ω unreached). Deliberately the minimal rung, so the
ratified layout gets a clean, fully-gated first proof point.

**Relationship to GZ-1:** GZ-1 already landed `write("hello")` on the OLD R15-frame build. R-HW
re-grounds the string-write path as the FIRST rung of the *ratified* layout and re-confirms every
gate. The string-write path does not touch the frame register, so the R15→R12 frame migration is
ORTHOGONAL to it — R-HW should pass with no frame work. Frame work (R12 + slot allocation) begins
at the first rung carrying RW state (`x := …` / `write(1+2)`), NOT here.

### Steps (each independently gated)

- [ ] **R-HW-0 — Bake & verify layout.** Ratified register table + subject naming written into
  this file (DONE — see "RATIFIED — UNIFIED REGISTER LAYOUT" above). Run Session Setup
  (`build_scrip.sh`, the three smokes). Confirm `scripts/test_gate_icn_no_stack.sh` and
  `scripts/test_gate_icn_one_reg_frame.sh` exist and pass at their pinned ratchet. No code change.

- [ ] **R-HW-1 — Rung program + mode-2 oracle (HARD GATE).** Create `/tmp/rung_hw.icn`. Then
  `./scrip --interp /tmp/rung_hw.icn` ⇒ `hello world` + newline. Driver detects Icon and calls
  `bb_exec_once(main_bb)` directly; `sm_interp_run` is never entered. This output is the ORACLE
  the other modes must match byte-for-byte.

- [x] **R-HW-2 — Mode-3 (`--run`) stackless RO-string box.** DONE (2026-05-30). write box emits string as sealed RO blob, reads ADDRESS via `lea rdi,[rip+disp]`; no frame/subject regs/push/pop. Three edits: `emit_bb.c` BB_CALL guard (strlit falls to direct FILL not γ-walk), `bb_call.cpp` strlit arm (RO-IP-relative lea), `bb_lit_scalar.cpp` BB_LIT_S → pure four-port pass-through (was the pusher). Gate: m2==m3, dump-sm 0, FACT 0, no-stack ratchet 129→127.

- [x] **R-HW-3 — Mode-4 (`--compile`) parity.** DONE (2026-05-31, Sonnet 4.5). `write("hello world")`
  assembles + links libscrip_rt.so + runs ⇒ `hello world\n`, byte-identical to m2/m3. The asm is a
  C-ABI `main` wrapper (`call rt_frame` → rdi, `xor esi,esi` → `call main_α`) + the flat body via
  `codegen_flat_build` in `MEDIUM_TEXT`. The body reuses the SAME BB templates as m3; mode-3 and mode-4
  differ ONLY at the boundary (return-to-driver vs C `main` returning 0), proving the model is
  mode-agnostic. Four enabling fixes: (1) `emit_core.c` `emitter_init_text/binary` set `g_medium` +
  `g_emit_sink` (templates were taking the binary arm in text mode + prologue/epilogue text was dropped);
  (2) `xa_flat.cpp` TEXT prologue/epilogue honor `g_frame_active` (push r12/fall-through to α_body, no
  esi-dispatch/β/r10, constant-success epilogue + pop r12); (3) `scrip.c` real mode-4 driver (Icon only);
  (4) `Makefile` `lower_program.c` → `RT_PIC_SRCS` so the .so is link-complete.

- [ ] **R-HW-4 — Full gate sweep + smokes.** All per-rung gates green; `test_smoke_icon.sh`
  mode-2 6/6 (HARD) with mode-3 now including hello-world; `test_smoke_prolog.sh` 5/5;
  `test_smoke_unified_broker.sh` ≥35. Ratchets (no-stack, one-reg-frame) unmoved. This rung is
  the ratified-layout baseline; later rungs may only lower ratchets, never raise them.

---



**HEAD (SCRIP):** `a2a606b` GZ-11+ mode-2 — THREE generator-correctness fixes closing the named binop/`to`
cluster + `proc_locals` accumulation (jcon `ir_a_Binop` / `ir_a_ToBy`). Mode-2 ORACLE ONLY (`bb_exec.c` +
`lower.c`; emitter UNTOUCHED → m3/m4 flat-chain byte-identical, verified `every write(1 to 3)` m2==m3). 2 files
(+74/−14). Rebased CONFLICT-CLEAN twice onto parallel SNOBOL4 `a06b2a1`/`706d665` (PB-RB-3 BB_MATCH) and Prolog
`f5170a0` (PLG-9e) — disjoint files, FACT-rule isolation held.

**Done this session (Opus 4.8):** All grounded per CONSULT-CANONICAL-SOURCES in `refs/jcon-master/tran/irgen.icn`.
1. **RELOP GENERATOR-TRANSPARENCY OVER A NESTED BINOP.** A relational op whose operand is a generator-bearing
   arithmetic `IR_BINOP` (a cross-product like `(1 to 3)*(1 to 2)`) dead-ended on the first FALSE comparison:
   `bb_is_gen_node` recognized `IR_BINOP_GEN` but NOT the plain `IR_BINOP` that `v_binop` emits for `*`/`+`, so
   the `rel_fail` arm fell to `return bb->ω` and terminated the `every`. New `gen_resume_target(e)` (`bb_exec.c`)
   descends a plain `IR_BINOP` to its RIGHT operand's resume (jcon `ir_binary`: `binop.resume → right.resume` —
   a postfix binop is NOT its own resume; re-running it recomputes the SAME product), recursing `aux[1]` then
   `aux[0]`; the `rel_fail` arm re-enters that resume instead of ω. `3 < ((1 to 3)*(1 to 2))`→4,6 ;
   `(1 to 3)+(1 to 3) > 4`→4,4,4. **corpus +2** (`rung01_paper_compound`, `rung02_arith_gen_nested_filter`),
   **broker +1** (`ICN: rung01 compound`).
2. **GENERATOR-BOUNDED `to`.** `(1 to 2) to (2 to 3)` produced EMPTY: the Icon postfix `to` arm read its bounds
   once from the AG ring and on counter-exhaustion returned ω, never re-pumping generator bounds. `v_to` now
   stores the `{from,to}` bound chains in `operand_aux` (PEERS sidecar, like `v_binop`); the postfix `IR_TO` arm
   reads bounds from operand VALUES (position-independent under re-pump) and on counter-exhaustion re-pumps
   `gen_resume_target(aux[1])` then `aux[0]`, resetting `state=0` to re-read fresh bounds (jcon `ir_a_ToBy`:
   `by.failure→to.resume`, `to.failure→from.resume`). Constant bounds yield no resume target → ω as before.
   `(1 to 2) to (2 to 3)`→1,2,1,2,3,2,2,3 ; `1 to (2 to 3)`→1,2,1,2,3 ; `(1 to 2) to 3`→1,2,3,2,3 ; constant
   `to`/`to by` (`1 to 3`, `1 to 5 by 2`, `5 to 1 by -1`) UNCHANGED. **corpus +1** (`rung01_paper_nested_to`).
3. **BINOP VARIABLE RE-DEREFERENCE ON GENERATOR RESUME (Icon-gated).** `every total := total + (1 to n)` gave the
   last addend not the sum (`sum_to(5)`→5 not 15; minimal `every total:=total+(1 to 3)`→3 not 6): the loop
   `VAR→TO→BINOP→ASSIGN→TO` re-enters the BINOP each pass but NOT the VAR box, so `aux[0]->value` stayed the
   stale initial value (each pass computed `initial+i`). The postfix `IR_BINOP` arm now refreshes a plain
   `IR_VAR`/`IR_KEYWORD` operand via `bb_exec_node` before reading `lv`/`rv` (idempotent frame-slot/NV read; jcon
   `ir_a_Binop` reads `[lv,rv]` each opfn) — NEVER a generator operand (re-exec would advance it). Guarded
   `g_current_cfg->lang==IR_LANG_ICN` so the shared SNOBOL4/Prolog binop path is BYTE-IDENTICAL. **corpus +1**
   (`rung02_proc_locals`).

**GATES (stash-verified vs pristine `c2b352d`):** Icon smoke **m2/m3/m4 12/12/12** (HARD m2 green) · corpus
`test_icon_all_rungs` **110→114 PASS** (FAIL 137→133, XFAIL 36) · broker **24→25** · Prolog m2/m3 **5/5** ·
SNOBOL4 `hello` OK · FACT **0** · C-byrd-box **0** · no-stack **117≤127** · one-reg-frame **20≤20** ·
prove_lower2 **65 PASS** · ZERO-SM **0**.

**NEXT:** GZ-DEFER (EVAL/CODE/`*P` deferred patterns, `test_sno_3.c` model); then GZ-11+ corpus features
stackless (lists, tables, records, scanning, csets, builtins). The remaining mode-2 generator-cluster odds-and-
ends still open (lower priority): nested cross-products consumed without an enclosing loop; `to by` with a
GENERATOR step/bound (this session did generator FROM/TO bounds for plain `to`, not `to by`); co-expression
`@`/`^` resume. None block GZ-DEFER.

**PREV (SCRIP):** `c353d68` GZ-11+ mode-2 RELATIONAL BINOP GENERATOR-TRANSPARENCY (jcon `ir_a_Binop`). A
FALSE relational comparison (`rel_fail`) is not the binop's failure — per jcon a relop is generator-transparent
and re-seeks the next operand value. The postfix `IR_BINOP` exec arm (`bb_exec.c`) re-enters the generator
operand's chain head (`operand_aux[1]`=right, then `[0]`=left) on `rel_fail` instead of returning ω; `v_binop`
already wired right.failure→left.resume so a both-generators case cascades and a drained chain reaches the
binop's own ω; with no generator operand (e.g. `3 < 2`) it collapses to plain failure. Fixed `2 < (1 to 4)`→3,4
and gen-on-left `(1 to 5) > 3`→3,3 (Icon relops return the right operand). **GATES:** corpus 107→110. Pushed;
rebased CONFLICT-CLEAN onto upstream `202bbba`. (This session's HEAD extended this exact mechanism to relops
over NESTED binops via `gen_resume_target`, plus generator-bounded `to` and binop variable re-deref.)

**PREV (SCRIP):** `a3728c0` GZ-11 SUSPEND mode-2 — user-defined Icon generators via `suspend E do BODY`
(jcon `ir_a_Suspend`). A suspending procedure is now a generator; `every write(gen())` re-pumps it. Eager-drain
model: the proc body's `IR_SUSPEND` nodes append to a per-activation `SuspendBuf`, the `IR_CALL` (dval==3.0) site
harvests into a node-keyed `susp_gen_cache` and yields one value per re-entry via `state`/`counter` (like IR_TO);
the resume-wiring crux is a generator call's β port -> the call node itself (resumable) vs ω (bounded) for a
deterministic call, decided by an `is_generator` pre-pass in `lower_program.c`. 5 files (+213): `lower.c`
(TT_SUSPEND arm + TT_LOCAL/GLOBAL/STATIC no-op arm + `icn_proc_is_generator`), `lower_program.c` (suspend
detection + pre-pass), `bb_exec.c` (SuspendBuf + susp_gen_cache + IR_SUSPEND exec + IR_CALL harvest/resume),
`scrip_ir.c` (IR_SUSPEND in the bb_reset counter-preserve whitelist), `prove_lower2.c` (local g_stage2 for the
standalone link). **GATES: Icon smoke m2/m3/m4 12/12/12 (HARD green) · corpus `test_icon_all_rungs` 90→107
PASS (+17) · no-stack 117≤127 · one-reg-frame 20≤20 · FACT 0 · C-byrd-box 0 · prove_lower2 64/64 · Prolog
m2/m3 5/5 · SNOBOL4 hi-sno OK · unified broker 24/42 (== session start).** mode-2 ORACLE ONLY (zero x86 emitted;
emission gates untouched); native mode-3/4 suspend is a later rung. Pushed; rebased CONFLICT-CLEAN onto the
parallel SNOBOL4 `77bbebc` (PB-RB-1 bb_ref_invariant emit arm) — disjoint files, FACT-rule isolation held.
NEXT: GZ-DEFER (EVAL/CODE/`*P` deferred patterns, `test_sno_3.c` model), then GZ-11+ corpus features stackless.

**HEAD (SCRIP):** `2de9ff5` GZ-10 modes 3/4 ARGS + recursion — stackless Icon user-procedure calls with
arguments, recursion, and mutual recursion now run in mode-3, m2==m3. `proc_recursion` smoke flips PASS →
**Icon m3 11/11**. Built on the GZ-10 modes-3/4 ZERO-ARG foundation `da3a786`; rebased CONFLICT-CLEAN onto the
parallel Raku session `c1f8e2e` (RK-EMIT-2-NEST) — both added a new static helper to `bb_call.cpp`
(`rk_marshal_call_arg` upstream, `bb_chain_terminal` here), kept side-by-side; FACT-rule isolation held.

**Done this session (GZ-10 modes 3/4 ARGS — Opus 4.8):** Completed argument passing for the stackless
`(ζζ,entry)` user-proc call so procs with args (incl. recursion) run in `--run`. THREE Icon-flat-chain-gated
edits + a driver two-phase split. **(1)** `emit_bb.c` `flat_drive_icn_userproc` + `flat_emit_arg_subchain`:
a dval==3.0 call's args are isolated value sub-graphs on `counter` (NOT the γ-chain); for each arg the driver
runs `icn_chain_operand_refs` then emits the WHOLE sub-graph as an inline flat chain (BFS over γ + BINOP.ω,
the `codegen_flat_chain_body` model) so every producer box emits once and claims its ζ=r12 slot. **ROOT BUG:**
a bare `walk_bb_flat(entry)` emits ONLY the entry node, so a multi-node arg like `n - 1` (VAR/LIT/BINOP)
never emitted its BINOP → staging read a garbage slot (zero-arg + single-leaf-arg cases happened to work,
hiding it). **(2)** `icn_chain_arity`: a dval==3.0 call is a LEAF producer (arity **0**) in the flat-chain
model, like dval==2.0 — args live on `counter`, not the γ-chain. The old `(int)n->ival` (legacy value-stack
`flat_drive_call_userproc` path) made `fact(n-1)` wrongly pop the sibling `n` off the operand stack,
corrupting the enclosing `n * fact(n-1)` binop's α (→ RETURN/garbage slot → `rt_arith` abort). **(3)**
`bb_call.cpp` dval==3.0 arm: emit per-arg staging (`mov edi,i; mov rsi,[r12+slot]; mov rdx,[r12+slot+8]; call
rt_icn_arg_stage`) before `rt_icn_call_proc_descr`, reading each arg sub-graph's TERMINAL producer slot (new
`bb_chain_terminal`: follow γ to the node `lower_value_subgraph` left with γ==NULL); DESCR = two INTEGER
eightbytes → SysV idx in edi, eb0 in rsi, eb1 in rdx. **(4)** `scrip.c`: split proc registration and slab
emission into TWO phases so a call to a forward/mutually-recursive proc (`iseven` calling later-registered
`isodd`) passes the `rt_proc_is_registered` gate during slab build. **Verified m2==m3:** `id(99)`
`double(21)` `add(3,4)` `f(g(5))` `fact(5)`=120 `fib(10)`=55 `ack(2,3)`=9 `sumto(100)`=5050 mutual
`iseven(10)`/`isodd(7)`=1 `fact` called 3× =120,720,24. **GATES (all green):** Icon m2 **11/11 HARD** · m3
**11/11** · m4 0/11; SNOBOL4 m2 **7/7** · Prolog m2/m3 **5/5** · no-stack **117 ≤ 127** · one-reg-frame
**20 ≤ 20** · sm_dead **0** · prove_lower2 **PASS** · ZERO-SM **0**. (SNOBOL4 m3 FAIL=1 is pre-existing —
identical at `da3a786`, verified by stash.) **NEXT:** GZ-10 **mode-4** (`--compile`) — the `bb_call` dval==3.0
TEXT arm was a loud abort stub — **DONE `2de9ff5`**: proc slabs as named GAS asm `icn_proc_<name>_α`,
startup registration stub, PLT-relative arg staging + call. **NEXT:** bare-`if C then E`-no-else fall-through
quirk (shared with SNOBOL4/Prolog), then GZ-DEFER, then GZ-11+ corpus features stackless.

---




is disjoint from the parallel SNOBOL4 work that advanced `origin/main` to `80431d0` (SBL-PAT-BB PB-0 subject
BB) → rebased conflict-free (different files, FACT-rule isolation held; pre-rebase local hash was `602e107`).

**Done this session (GZ-10 RECURSION FIX — Opus 4.8):** Closed the one remaining GZ-10 mode-2 blocker —
recursion. The prior `dval==3.0` Icon general-call exec arm bound param names by walking the LIVE
`proc->c[1]` (TT_VLIST) AST at every activation; on 2nd+ re-entry of a recursive proc the shared param
`TT_VAR` nodes read EMPTY (mutated by the nested arg-subgraph/scope path), so `args[0]` resolved wrong and
recursion degenerated (`fact(5)`→5 instead of 120). Implemented the RECOMMENDED `lower_sc` fix (mirrors
SNOBOL4's `proc_table[].lower_sc`), TWO edits, both Icon-gated: (1) `lower_program.c` — after
`lower_icon_body` succeeds (inside the `LANG_ICN` block), capture the proc's param names into `lower_sc`
ONCE via `lp_strdup` (stable GC strings, slot-keyed); (2) `bb_exec.c` `dval==3.0` arm — bind `env[slot]`
from `lower_sc` instead of re-walking `proc->c[1]` each call. The AST is NEVER read at exec time → no
mutation dependency → per-activation correct. **Verified m2:** recursive `fact(5)`→120, `fib(10)`→55 (double
recursion per activation), `sumto(100)`→5050 (100-deep), `ack(2,3)`→9 (2-param deep nesting), mutual
`iseven(10)`/`isodd(7)`→1, SAME proc called 3× (`fact` →120,720,24 — proves the AST is no longer
consumed/mutated); non-recursive `answer/id/double/add` and `cmp` (if-else) unchanged. **Smoke:** added a
`proc_recursion` case (`fact(5)`→120) to `test_smoke_icon.sh` so the gate permanently covers recursion.
**GATES (all green):** Icon m2 **10/10 HARD** · m3 9/10 · m4 9/10 (the new `proc_recursion` is m3/m4-red —
GZ-10 modes 3/4 are the next rung, the `test_sno_3.c` `(ζζ,entry)` flat-box model, NOT yet built);
SNOBOL4 m2 **7/7** · Prolog m2/m3 **5/5** · broker **23** · FACT **0** · no-stack **117 ≤ 127** (my edits are
in `src/lower/`, OUTSIDE the gate's `src/emitter/` grep scope — the 117 vs prior-watermark 114 is pre-existing
baseline drift from a parallel session, not this change) · one-reg-frame **20 ≤ 20** · prove_lower2 **PASS** ·
ZERO-SM **0**. **OUT OF SCOPE (pre-existing, NOT GZ-10):** bare `if C then E` (no else) cond-FALSE fails the
whole proc instead of falling through — the documented GZ-8/GZ-9 IR_SEQ statement-failure-continuation quirk
(workaround = explicit `else`, which every recursion test uses). **NEXT:** GZ-10 mode-3/4 (`test_sno_3.c`
`(ζζ,entry)` lazily-allocated flat-box model, `_λ` landing pad, recursion depth in per-box arenas — never a
value stack); then the bare-if-no-else fall-through quirk (shared with SNOBOL4/Prolog).

---


held). Icon smoke **m2 9/9 HARD · m3 9/9 · m4 9/9** UNCHANGED (purely additive Icon mode-2 lowering+exec; no
regression). Prolog m2 5/5, broker 23/43, FACT 0, no-stack 114, one-reg-frame 20, prove_lower2 PASS — all
unmoved from session start.

**Done this session (GZ-10 mode-2 PARTIAL — Opus 4.8):** Stood up Icon user-procedure CALLS + `return` in the
mode-2 oracle, grounded per CONSULT-CANONICAL-SOURCES in jcon `ir_a_Call` (call.start→fn.start; last-arg
resume threading) + `ir_a_ProcDecl`/`ir_a_ProcBody` (genuine per-activation params/locals). FIVE edits, all
Icon-gated (SNOBOL4 m2 7/7 & Prolog m2/m3 5/5 unaffected — verified): (1) `lower.c` `TT_RETURN`/`TT_NRETURN`
Icon arm → `IR_RETURN`; the value chain flows γ→return so the result is on the AG ring (RETURN does NOT
re-exec α — that would yield only the chain-entry leaf); (2) `lower.c` `TT_FNC` general user-proc call Icon
arm (after the write/writes check) → `IR_CALL dval=3.0` with each arg lowered into its OWN isolated value
sub-graph on `counter` (the proven dval==2.0 SNOBOL4 call idiom); (3) `bb_exec.c` NEW `IR_CALL dval==3.0`
exec arm — evaluates the arg subgraphs, finds the callee in `proc_table`, runs its four-port BB graph under a
FRESH `GenFrame` whose `Scope` binds the proc's PARAM NAMES to env slots (so the body's IR_VAR/IR_ASSIGN
resolve per-activation via `scope_get`→`env[slot]` — Icon-correct, distinct from the SNOBOL4 global
save/restore frame), ring+node-state snapshot/restored around the nested `bb_exec_once`, harvests
`g_ir_return_val` on `FRAME.returning`; (4) `bb_exec.c` `IR_RETURN` generic arm reads `ag_ring_peek` when α
is unset; (5) `scrip_ir.c` `bb_reset` preserves `counter` for `IR_CALL dval==3.0` (the arg-subgraph array was
being zeroed → `(nil)` — caught via a counter trace). Plus `lower.c` `lower_value_subgraph` now inherits the
caller's `cx.lang` (strict generalization; SNOBOL4 callers still pass IR_LANG_SNO → byte-identical).
**Verified m2:** `answer()`→42, `id(99)`→99, `double(21)`→42, `add(3,4)`→7, `cmp(0)`→111, `cmp(5)`+else→222.
**TWO bugs found, CLEANLY SEPARATED (diagnosed, not fixed):** (a) PRE-EXISTING (NOT GZ-10): bare `if C then E`
(no else) cond-FALSE fails the whole proc instead of falling through — the documented GZ-8/GZ-9 IR_SEQ
statement-failure-continuation quirk; workaround = explicit `else`. (b) **THE GZ-10 BLOCKER (recursion):** on
RE-ENTRY of the same proc graph the proc's AST is MUTATED — the param name (`TT_PROC_DECL` param
`TT_VAR.v.sval`) reads EMPTY on the 2nd+ activation and `args[0]` reads wrong, so `fact(5)`→5 (recursion
degenerates to returning `n`). Single non-recursive calls are unaffected. ROOT SUSPECT: reading param names
from the LIVE AST at exec time is fragile — the nested `bb_exec_once`/arg-subgraph path (likely `scope_patch`,
which writes `TT_VAR.v.ival`, or AST sharing between the body graph and the arg subgraphs) clobbers the
shared param nodes.
**NEXT (recommended — the recursion fix):** stop reading param names from the AST in the `dval==3.0` arm;
capture them at LOWERING time into a stable per-proc structure — mirror SNOBOL4's `proc_table[].lower_sc`:
have `lower_icon_body` (`lower_program.c`) populate `lower_sc` with the param names (+locals) ONCE, and have
the `dval==3.0` exec arm bind `env[scope_get(&lower_sc,name)]` from that stable scope rather than walking
`proc->c[1]` each call. That removes the AST-mutation dependency and is the cleaner per-activation model.
Then the bare-if-no-else fall-through quirk (shared with SNOBOL4/Prolog), then mode-3/4 (the `test_sno_3.c`
`(ζζ,entry)` lazily-allocated flat-box model, `_λ` landing pad, recursion depth in per-box arenas).

---

**HEAD (SCRIP):** `109fded` GZ-9 `while`/`until`/`repeat` + `break`/`next` — Model B self-driving loops
(loop node = pure forwarder/terminator; cond relop ports + body γ/ω carry the loop; NO router, NO
`FRAME.loop_*` flag, NO value stack). Icon smoke **m2 9/9 HARD · m3 9/9 · m4 9/9** (added `while`,
`until`, `repeat_break`). Rebased conflict-free onto parallel `afb6995` (Prolog PLG-9b + SNOBOL4
SBL-M3-CHAIN + Raku RK-LOWER-4 — FACT-rule isolation held). Built on GZ-8 `febef10`.

**Done this session (GZ-9 — Sonnet 4.8):** `while`/`until`/`repeat` (+ `break`/`next`), all **m2==m3==m4**.
Grounded per CONSULT-CANONICAL-SOURCES in JCON `ir_a_While` (cond.γ→body, cond.ω→exit) / `ir_a_Until`
(cond.γ→exit, cond.ω→body) / `ir_a_Repeat` (body.γ/ω→body.start) / `ir_a_Break` / `ir_a_Next`. The loops
**self-drive** under the top-level port-walker (Model B): the relop's OWN γ/ω ports + the body's edges
carry the loop, and the `IR_WHILE/UNTIL/REPEAT` node is a pure forwarder/terminator — there is NO internal
exec-arm driver loop and NO `FRAME.loop_*` flag mechanism (Model A, which was dormant: the old lowering
never produced `IR_BREAK`/`IR_NEXT`, and `while`/`until`/`repeat` were never driven by their exec arms'
internal loops on the passing paths). SEVEN edits, all Icon-gated (SNOBOL4 m2 7/7, Prolog m2/m3 5/5,
broker 20 unchanged — verified post-rebuild AND post-rebase):
1. `lower.c` **`v_until` rewritten** to structurally mirror `v_while` (cond.γ→until-node/exit, cond.ω→body).
   This FIXED A PRE-EXISTING MODE-2 ORACLE BUG: `until` previously produced **EMPTY output for every input**
   (the old wiring hung the body off `IR_UNTIL.α`, which neither the port-walker nor the flat-chain BFS
   visits, and `bb_exec.c`'s IR_UNTIL arm mistreated `α` as the condition). Now `until i>3`→1,2,3 and
   `until i<=0`(i=5)→5,4,3,2,1 in all three modes.
2. `lower.c` **`v_repeat` rewritten** to self-drive (`rp->γ = body-start` as the loop-back edge); the only
   NORMAL exit is a `break` in the body (wired straight to γ_in via the loop context).
3. `lower.c` **`with_loop(cx, γ_in, reentry)`** now wraps the body lowering of all three loops (it was
   DEFINED BUT UNUSED): `break`→`cx.loop_ω`(=γ_in exit), `next`→`cx.loop_next`(=cond/body re-entry).
4. `lower.c` new **`v_loop_break`/`v_loop_next`** + dedicated **`TT_LOOP_BREAK`/`TT_LOOP_NEXT` dispatch**
   (Icon-gated) → `IR_BREAK`/`IR_NEXT` forwarders with γ==ω==target. Removed the STALE duplicate
   `TT_LOOP_BREAK/NEXT` labels from the `TT_FNC` fall-through group (they routed break/next into the call
   handler — wrong, and never fired since the nodes were never produced).
5. `bb_exec.c` **`IR_BREAK`/`IR_NEXT`/`IR_REPEAT` exec arms → pure port-forwarders** (break/next → `bb->γ`;
   repeat → `bb->α`); deleted the dormant `FRAME.loop_*`-flag Model-A bodies.
6. `bb_binop.cpp` **GZ-9 flat-chain integer-ARITHMETIC arm** (BINARY+TEXT) — `i := i + 1` etc.: reads each
   operand's int payload `[r12+slot+8]` (`bb_slot_get`), computes register-to-register (ADD/SUB/MUL/DIV/MOD
   uniform — `rax op rcx`; DIV/MOD via `cqo; idiv rcx`), writes a re-tagged `{DT_I,result}` 16-byte DESCR to
   its OWN `bb_slot_alloc16` slot (the `test_icon.c` `mult_V=a*b` named-slot model — NO value stack, NO
   ring). NB the tag-store `mov qword [r12+off],imm32` is **12 bytes** (4 op/ModRM/SIB + 4 disp32 + 4 imm32)
   — an initial 11-byte miscount caused a mode-3 SIGILL, caught via an emitted-byte hexdump.
7. `emit_bb.c` `walk_bb_flat`: flat-chain ARITH binops route to **FILL** (operands are sibling chain boxes
   already BFS-collected — do NOT re-walk via `flat_drive_binop_tree`, which duplicated them with fresh
   slots and clobbered the slotmap); added `IR_BREAK`/`IR_NEXT`/`IR_REPEAT` cases as pure `jmp γ` forwarders.
   Also `bb_assign.cpp` flat-chain RHS guard widened to accept `IR_BINOP`; `emit_core.c` IR_ASSIGN→
   `bb_sno_assign` routing gated `!g_icn_flat_chain` (so Icon flat-chain ASSIGN reaches `bb_assign`).
`scripts/test_smoke_icon.sh` gained `while`, `until`, `repeat_break` (smoke 6→9 cases).
**Validation (all m2==m3==m4):** `while` × `<`,`>`,`<=`,`>=` with ADD/SUB/MUL; `until i>3`→1,2,3 &
`until i<=0`→5,4,3,2,1; `repeat{if i>=3 then break else write(i); i:=i+1}`→0,1,2; `while{i:=i+1; if i=5
then break else write(i)}`→1,2,3,4. **GATES (all green):** Icon smoke m2 **9/9 HARD** · m3 9/9 · m4 9/9;
no-stack **114 ≤ 127** (break/next/repeat add ZERO push/pop — pure forwarders); one-reg-frame **20 ≤ 20**;
FACT 0; ZERO-SM (`--dump-sm` count=0); prove_lower2 PASS; crosscheck 4/4; Prolog m2 5/5 · m3 5/5;
SNOBOL4 m2 7/7; broker 20.
**NEXT:** GZ-10 (user procedure as a four-port FLAT box — `test_sno_3.c` `(ζζ,entry)` model, lazy frame,
`_λ` landing pad; recursion depth in per-box arenas, never a value stack). **OUT OF SCOPE (pre-existing,
documented at GZ-8 — recommend fixing before/with GZ-10):** a bare `if C then E` (no `else`) whose cond
FAILS does not fall through to the next statement in m2 OR m3 (the IR_SEQ statement-failure-continuation
quirk) — this is why `break`/`next` currently require the `if … then break else …` form. The optional
`break E` expression value is lowered as a plain transfer (E-as-loop-result is a later refinement).

---

**HEAD (SCRIP):** GZ-8 `if`/relop control — relop-as-branch (cmp+jcc, no LAST_OK/BB_IF router/vstack).
Icon smoke **m2 6/6 HARD · m3 6/6 · m4 6/6** (first all-three-modes-6/6). Built on `febef10`.

**Done this session (GZ-8 — Sonnet 4.8):** `if x>5 then write("big") else write("small")` →
m2==m3==m4 `big`. The relop bakes its own branch grounded in `test_icon.c` (negated-relation fail-jump);
the `IR_IF` node is vestigial in the γ/ω graph. Four mode-3/4-gated edits (mode-2 oracle untouched →
HARD gate safe; SNOBOL4 m3 2/6 & Prolog 5/5 stash-verified unchanged): (1) `bb_binop.cpp` flat-chain
numeric-relop arm `mov rax,[r12+sa+8]; mov rcx,[r12+sb+8]; cmp; jcc ω; jmp γ` (BINARY+TEXT); (2)
`walk_bb_flat` IR_BINOP flat-chain relop → FILL (no operand re-walk); (3) `icn_chain_operand_refs`
BFS→DFS so branch arms stay contiguous (fixes branch-arm CALL operand resolution); (4) `bb_var.cpp`
`bb_slot_alloc`→`alloc16` (VAR writes a 16-byte DESCR; prevents two-operand slot overlap). All 6
operators × both arms verified m2==m3; m4 assembled+linked+run. GATES: FACT 0 · no-stack 114≤127 ·
one-reg-frame 20≤20 · prove_lower2 PASS · template-purity 7 (unchanged) · crosscheck 4/4 · Prolog m2
5/5 · broker 20. **NEXT:** GZ-9 (`while`/`until`/`repeat`; JCON `ir_a_While`: body.success/failure →
cond.START). Note the pre-existing out-of-scope observation: bare `if C then E` (no else) failing-cond
does not continue to the next statement in m2 OR m3 (consistent IR_SEQ statement-failure quirk).

---



**Done this session (GZ-7 mode-3 + mode-4 — flat goto-graph, named slots, NO ring):** Lon's architectural
law restated and enforced: **mode 2 = AG ring (correct); modes 3/4 = NO ring** — the `test_sno_*.c` model,
where every box owns a NAMED SLOT, writes its result there, and a consumer reads the producer box's slot
DIRECTLY (`str_t POS0; … seq = cat(seq, POS0)`); wiring is pure `goto` (α/β/γ/ω → `jmp rel32`); values flow
UP the BB graph chain via slots, never a ring. GZ-7 is the first multi-statement / variable-bearing rung
crossed in compiled modes. The single-expression-tree adapter `icn_ring_to_tree` returns NULL for it (it
un-flattens ONE tree; this graph is `LIT_I→ASSIGN→VAR→CALL`, two statement roots), so a NEW path was built:
- **`emit_bb.c`** — `icn_flat_chain_build` + `icn_flat_chain_build_text` + `codegen_flat_chain_body`: pass
  (1) `icn_chain_operand_refs` walks the γ-chain, a postfix stack records each consumer's operand boxes as
  REFERENCES on α/β (NOT for re-walk); pass (2) BFS-emits every box ONCE wired by native γ/ω. `g_icn_flat_
  chain` gates the slot-leaf template arms. Name-keyed `bb_varslot`/`bb_varslot_peek`: an Icon variable is
  ONE `[r12+off]` frame slot shared by IR_ASSIGN(name) + IR_VAR(name) — the x86 analog of `str_t POS0`.
- **Templates** (BINARY+TEXT slot arms): `bb_lit_scalar` LIT_I writes a 16-byte DESCR (`{v:DT_I,slen:0}` +
  int value) to its slot; `bb_var` copies named-var slot → own slot; `bb_assign` copies RHS-producer slot →
  named-var slot (restricted to DESCR-producing RHS LIT_I/VAR; binop-RHS falls through LOUD — GZ-8 adds the
  binop DESCR producer); `bb_call` `write(E)` reads operand slot by value (rdi:rsi) → `rt_write_any_nl`.
- **`rt.c`** — new by-value `rt_write_any_nl(DESCR_t)` (type-dispatch int/real/string).
- **`scrip.c`** — mode-3 + mode-4 Icon drivers route to the chain builder when `icn_ring_to_tree` returns
  NULL (multi-statement / variable / branch).
**Validation:** `x := 42; write(x)` → **m2==m3==m4 `42`** (m4 assembled with `gcc -no-pie` + linked
`out/libscrip_rt.so` + run). Mode-4 asm reads exactly as test_sno_1.c: each box reads/writes named `[r12+off]`
slots, jmp-wired. **GATES (all green):** Icon smoke **m2 6/6 HARD · m3 5/6 · m4 5/6** (m4 was 0/6 at session
start — libscrip_rt absent; the flat-chain TEXT arms rebuilt write_str/write_int/arith/string_op/every);
Prolog m2 5/5 · m3 5/5 (Icon-only edits); broker 19 (unchanged baseline); FACT 0; no-stack 114 ≤ 127
(comment-string artifact, zero real push/pop added); one-reg-frame 20 ≤ 20 (all `[r12+off]`); prove_lower2
PASS; template-purity advisory 7 (byte-identical before/after, verified via stash). Icon crosscheck arith/
concat/every_to PASS m2+m3+m4. **Only `if_expr` remains m3/m4-red** — the branching CFG; the flat-chain BFS
already follows ω at relop nodes, so it is the natural next rung (needs the relop slot arm + branch wiring).
**NEXT:** GZ-8 (`write(1+2)` already works as a tree; extend the binop to write a DESCR slot so `x := 2+3`
and `if x>5` work) then `if_expr` mode-3/4 (relop writes a bool/value slot, IR_IF branch already BFS-collected
via ω). The mode-2-only OPEN BUGS below (relop filtering asymmetry; if-as-arith-operand) remain valid and are
independent of this compiled-mode work — and note the bug-(b) analysis is a MODE-2 (ring) concern only.

---

**Rebase/merge note (shared-file concurrency):** the parallel SNOBOL4 session ALSO landed mode-4 the
same session, touching the SAME two shared files — `xa_flat.cpp` (the flat TEXT prologue/epilogue made
`g_frame_active`-aware) and `scrip.c` (the `mode_compile_x86` driver). Both conflicts resolved by UNION:
(a) `xa_flat.cpp` frame-active TEXT prologue/epilogue is now ONE shared form serving both languages
(prologue `push r12; mov r12,rdi; lea r10,[rip+Δ]` → fall through to α_body; constant-success epilogue
+ `pop r12`, no Σ/r10 deref) — the epilogue bodies were already byte-identical between the two sessions;
(b) `scrip.c` `mode_compile_x86` now dispatches by language — `is_icon` → the Icon driver (C-ABI main
wrapper + `icn_ring_to_tree` + `codegen_flat_build`), `!is_prolog` (SNOBOL4) → the SNOBOL4 driver
(`xa_file_header`/footer + `sno_ring_to_tree` + `codegen_flat_build("stmt0")`), Prolog → loud stub. Both
verified post-merge: Icon m4 5/6 AND SNOBOL4 m4 1/5 intact, all gates green.

**Done this session (PIVOT — get modes 2/3/4 working on the Icon programs already passing m2 — Sonnet 4.5):**
Lon's PIVOT: rather than push deeper on new mode-2 rungs, get **all three modes** green on the smoke
set. mode-2 was already 6/6 and mode-3 5/6; **mode-4 was fully severed (0/6)**. Rebuilt mode-4
(`--compile`) BB-native and took it to **5/6, matching mode-3 exactly.** ONE commit, 7 files, all gated.

**KEY INSIGHT:** mode-3 and mode-4 share the SAME BB templates. Mode-3 emits `MEDIUM_BINARY` into the
`bb_pool` and `jmp`s into it; mode-4 emits `MEDIUM_TEXT` GAS asm to stdout, assembled with `gcc -no-pie`
+ linked against `out/libscrip_rt.so` + run. The templates already HAD `MEDIUM_TEXT` arms for the shell;
mode-4 was severed only at the driver (SMX stub) AND the per-box stackless TEXT arms had never been
written (only the BINARY arms were rebuilt for GZ-2/3/4). Five enabling pieces:
1. **`emit_core.c` `emitter_init_text`/`emitter_init_binary`** now set `g_medium` (the `MEDIUM_TEXT`/
   `MEDIUM_BINARY` macro driver) AND `g_emit_sink`. They previously set only `bb_emit_mode`, so in text
   mode the templates still saw `MEDIUM_BINARY` (took the byte arm → `bb_emit_byte` abort), and the
   prologue/epilogue text was silently dropped because `g_emit_sink` was only set later inside
   `walk_bb_node` (the body), AFTER the prologue had already run. THE root unblock.
2. **`xa_flat.cpp` TEXT prologue/epilogue** honor `g_frame_active` (Icon stackless): prologue =
   `push r12; mov r12,rdi` then fall straight through to `α_body` (the esi-dispatch + `jmp β` + `lea r10`
   are all dead at the C-ABI boundary — esi is always 0, the Icon body uses r12+rip-relative not r10);
   epilogue = constant success (`mov eax,1; xor edx,edx`) + `pop r12`, NO Σ/r10 deref. NON-ICON
   (`g_frame_active==0`) keeps the original `lea r10,[rip+Δ]` dispatch + Σ/r10 epilogue → byte-identical.
3. **`scrip.c` mode-4 driver** (Icon only): `sm_preamble` → register procs → `icn_ring_to_tree` → emit a
   C-ABI `main` wrapper (`.intel_syntax noprefix`; `push rbp/mov rbp,rsp`; `call rt_frame@PLT`;
   `mov rdi,rax`; `xor esi,esi`; `call main_α`; `xor eax,eax`; `pop rbp`; `ret`) then `codegen_flat_build
   (icn_root, stdout, "main")` under `g_frame_active=1`. Non-Icon `--compile` keeps the loud stub.
4. **`Makefile`** adds `src/lower/lower_program.c` to `RT_PIC_SRCS` so `libscrip_rt.so` is link-complete
   (it defines `lower`/`binop_apply`/`bb_label_landing`/`lower_proc_gen`, previously only in the `scrip`
   binary → the `.so` had undefined refs that broke the `-no-pie` link).
5. **`bb_call.cpp`/`bb_binop.cpp`/`bb_to.cpp` stackless TEXT arms** mirroring the proven BINARY arms:
   GZ-2 `write(RO-int)` → `.rodata .quad` + `mov rdi,[rip+lbl]`; GZ-3 `write(binop/to)` → `mov rdi,[r12+off]`
   (off via `bb_slot_get`); GZ-4 concat → `str_concat_d` into `[r12+off]` DESCR, write reads `[r12+off+8]`;
   GZ-4 `to`-pump → `.rodata` lo/hi + `[r12+off]` cursor with α-seed/β-increment. CRUCIALLY `bb_call`'s
   GZ-3 TEXT arm now DEFINES the β re-pump label and `jmp`s to the `EMIT_PAIR`-registered target (the
   arg generator's β resume) — exactly what `every` needs to re-drive the `to` (this was the last fix:
   without it `every write(1 to 3)` had an undefined `xevery0_body_β` link error).

**Validation (mode-4, assembled+linked+run, all byte-identical to m2/m3):** `write("hello")`→hello;
`write(42)`→42; `write(2+3)`→5; `write(10-4)`→6; `write("ab"||"cd")`→abcd; `every write(1 to 3)`→1,2,3;
`every write(5 to 8)`→5,6,7,8.

**GATES (all green, zero regressions):** Icon smoke **m2 6/6 HARD · m3 5/6 · m4 5/6** (`if_expr` is the
only m4-red — fork-blocked in BOTH m3 and m4); Prolog m2 5/5; unified broker 10 (severed baseline,
unaffected — Icon-only edits); Icon corpus m2 43/283 (unchanged); FACT 0; no-stack 113 ≤ 127;
one-reg-frame 20 ≤ 20. Non-Icon `--compile` correctly stubs loud. mode-3 BINARY arms untouched
(byte-identical). `refs/` (uploaded oracle zips) added to `.gitignore`.

**NEXT:**
1. **`if_expr` (the last m4/m3 gap)** is Lon's Path-1/Path-2 fork: the `icn_ring_to_tree` adapter NULLs
   control-flow shapes (IF/IR_ALT/CALL-resume cycle) → mode-3 AND mode-4 emit nothing for them. Resolving
   the fork (rework the adapter to walk the γ-chain/ring natively, drop the `g_icn_postfix_resume` seam)
   unblocks `if_expr` in both compiled modes at once.
2. **Extend mode-4 to more corpus features** as their BINARY arms get stackless TEXT twins (same
   mechanical mirror done here for GZ-2/3/4). Each new box family: add its `MEDIUM_TEXT` arm next to the
   `MEDIUM_BINARY` one, defining the β label + EMIT_PAIR target if it's a generator.
3. The mode-2-only OPEN BUGS from the prior Opus 4.8 handoff (relop filtering asymmetry; if-as-arith-
   operand) remain valid and independent of the mode-3/4 fork.



**HEAD (SCRIP):** `aabf060` (mode-2 foundation correctness, Opus 4.8; on `origin/main`, rebased conflict-free onto parallel SNOBOL4 `af6c8ae` + a `descr8-macro-funnel` branch). Handoff `HANDOFF-2026-05-31-OPUS48-ICON-BB-MODE2-FOUNDATION-FIXES.md`.

**Done this session (mode-2 foundation correctness — 5 commits — Opus 4.8):** Took GZ-7 (`x := 42; write(x)`; mode-2 oracle already passing) and while grounding it fixed FOUR real mode-2 oracle bugs, all grounded in canonical Icon (`oarith.r`/`bigpowii`, `ir_a_ToBy`, `ir_binary`) per CONSULT-CANONICAL-SOURCES, all gated, all non-regressive. (1) `8615c04` **`IR_UNOP` exec arm** — the lowerer emits `IR_UNOP`(ival=tree kind) but `bb_exec.c` had only the dead per-kind `IR_NEG/POS/SIZE/NONNULL/CSET_COMPL` arms, so every unary op fell to the loud default and FAILED (`write(-7)`→∅); added `IR_UNOP` mirroring `IR_BINOP`'s dual postfix/tree form dispatching on `(tree_e)ival` (`-`/`+`/`*`/`\`/`~`); SNOBOL4 `X=-5`→`-5` too. (2) `de0ce21` **integer `BINOP_POW`** — was always real (`2^10`→`1024.0`); int^int(exp≥0)→integer per `oarith.r` (`2^10`→`1024`, reals stay real); shared Icon+SNOBOL4 path. (3) `16e28db` **regression gate** `scripts/test_icon_arith_unary_mode2.sh` (additive, 27 cases). (4) `7dc77be` **`v_to` `TO_BY` step** — `c[2]` was dropped so `to by` always stepped 1 (`1 to 5 by 2`→`1 2 3 4 5`, neg steps→∅); `to_by_const_step()` bakes a constant step (int/real/signed `TT_MNS`-`TT_PLS`) into `node->ival` (`1 to 5 by 2`→`1 3 5`, `3 to 1 by -1`→`3 2 1`); plain `TT_TO` untouched; variable step still default-1 (limitation). (5) `aabf060` **`v_assign` Icon `:=` generator-transparent** — `:=` is a `funcs` member (`ir_binary`), so unbounded its resume→rhs resume; `every i := (1 to 3) do write(i)`→`1 2 3` (was `1`); Icon-gated + `rβ`-guarded so SNOBOL4/Rebus and `x := 42` unchanged. **GATES (unmoved): Icon m2 6/6 HARD · m3 5/6 · SNOBOL4 m2 7/7 · Prolog m2 5/5 · regression 27/27 · no-stack 113 · one-reg-frame 20 · FACT 0.** NO mode-3/emitter work.

**OPEN BUGS (root-caused, NOT fixed — handoff doc has full detail):** (a) **`if`-as-arithmetic-operand** `(if C then E)+1`→∅ (want value): `v_binop` patches the IF node's γ but `v_if` lowered THEN/ELSE against the original NULL `γ_in` so the branch leaf dead-ends; fix = route THEN/ELSE success through the IF node as one funnel (jcon `ir_a_If` success-chunk). (b) **relational filtering asymmetry**: only `<bounded> > <gen-on-right>` works (GZ-6 shape: `3 > (1 to 5)`→`1 2`); `<` (`2 < (1 to 5)`→∅, want `3 4 5`) and generator-on-left (`(1 to 5) > 3`→∅) both fail — the shared `IR_BINOP` relop arm re-pumps only the right operand / builds the fail→resume edge for one order; ground in jcon `ir_a_Binop` (relop is generator-transparent in BOTH operands). Both are the SAME "continuation/resume threading through a node" class as the `v_to`/`v_assign` fixes that landed. **Recommended next: fix (b) then (a) in mode-2 (low-risk), before the larger fork-gated GZ-7 mode-3.**

---

**HEAD (SCRIP):** `81d721b` (session 10 — GZ-6 mode-2 nested-generator oracle; pushed, rebased cleanly onto the parallel `440deba` — zero conflicts, FACT-rule isolation held).

**Done this session (10, GZ-6 mode-2 oracle — MILESTONE — Opus 4.x):** `every write(5 > ((1 to 2) * (3 to 4)))` → **3,4** (was `12,16`). The paper's full example now runs stackless in the mode-2 port-walker. FIVE contained edits across 3 files (`src/lower/lower.c`, `src/lower/bb_exec.c`, `src/driver/scrip.c`), all grounded per CONSULT-CANONICAL-SOURCES in jcon `tran/irgen.icn` (ir_a_Every L309 / ir_a_Alt L167 / ir_a_Binop L471 / ir_a_Call L360) + `test_icon.c` named-slot goto-graph. Detailed in the GZ-6 ladder step above. Summary: (1) `wire_det_builtin1` — CALL.resume → arg.resume (`aβ`) so write re-pumps a generator argument; (2) `v_binop` — operands into OWN named `operand_aux` slots (replaces push-only-ring mis-count); (3) IR_BINOP arm reads those slots; (4) IR_EVERY ival==0 → pure terminator (chain self-drives, no double-drive); (5) IR_ALT collector self-advances on resume + `wire_alt` stores arm VALUE nodes in `operand_aux`. **ROOT CAUSE:** with the resume ports wired the generator chain self-drives under the top-level driver (entry = generator α, not the EVERY node), so the EVERY node — reached once via gen.ω — must just succeed; the old restart loop re-drove the whole cross-product (doubling), and the removed all-single alt branch had masked an ALT collector that re-yielded literals forever on resume.

**mode-2/mode-3 SEAM — `g_icn_postfix_resume` (NEW global, `lower.c`).** Edit (1) changes the SHARED IR: CALL.resume becomes `aβ`, so CALL.γ resumes the argument generator instead of EVERY → a CALL→arg.resume CYCLE in the γ-chain. The mode-3 ring→tree adapter `icn_ring_to_tree` (driver/scrip.c) builds a LINEAR postfix chain by following `cur->γ`; the cycle overflows its 256-guard → NULL → no mode-3 output (m3 `every` regressed 5→4 before gating). Restructuring that adapter to model the re-pump cycle IS Lon's Path-1/Path-2 fork. INTERIM FIX: `scrip.c` sets `g_icn_postfix_resume = 1` ONLY in the `--interp` branch under `if (is_icon)`, BEFORE `sm_preamble` lowers; `wire_det_builtin1` gates `call_resume = g_icn_postfix_resume ? aβ : ω_in`. Result — mode-3 IR is PROVABLY byte-identical to the pre-GZ6 graph (CALL.resume=ω_in, gen.γ=EVERY): m3 `every write(1 to 3)` restored, no regression. Edits (2)–(5) are mode-2-only (operand_aux + bb_exec.c arms; the mode-3 flat emitter reads neither operand_aux nor bb_exec.c). **mode-3 remains fork-blocked for GZ-5 IR_ALT AND GZ-6 CALL-resume** — removing the seam + teaching `icn_ring_to_tree` the resume topology is the next mode-3 step, gated on the fork decision.

**Validation (mode-2, all correct):** gz6 `5>((1 to 2)*(3 to 4))`→3,4; cross `(1 to 2)*(3 to 4)`→3,4,6,8; `5>(1 to 4)`→1,2,3,4; `1 to 3`→1,2,3; `1|2|3`→1,2,3; `(1 to 2)|(5 to 6)`→1,2,5,6; `(1|2)+(10|20)`→11,21,12,22; `2+3`→5; `"ab"||"cd"`→abcd. **GATES:** Icon smoke **m2 6/6 HARD**, m3 **5/6** (only `if_expr` fork-blocked — == baseline; `every` m3 restored by the seam); no-stack **113 ≤ 127**; one-reg-frame **20 ≤ 20**; sm_dead **1 ≤ 1**; lower/stage2/runtime isolation OK. Prolog **2/5** & broker **7/59** (severed baseline, provably unaffected — Icon-only edits). SNOBOL4 m2 **6/7** (output/concat/arith/pattern[incl. alternation `('x'|'b')`→aYc verified]/goto_s/arith_sm green; `define` is a pre-existing mode-2 proc-definition gap, untouched by these changes); SNOBOL4 m3 0/6 (severed). `test_gate_em_template_byte_identity` 0/4 is the pre-existing SMX baseline (SNOBOL `--run` aborts 134 by design). No x86 templates touched.

**NEXT (recommended):** GZ-7 `x := 42; write(x)` (flat .bss slot for `x`) is the next mode-2 rung and is independent of the mode-3 fork. For mode-3, Lon's Path-1/Path-2 fork now gates BOTH GZ-5 (IR_ALT) and GZ-6 (CALL-resume cycle) — pick the fork, then rework `icn_ring_to_tree` (or replace the flat emitter with a γ-chain/ring walker) and drop the `g_icn_postfix_resume` seam.




**HEAD (SCRIP):** `72aa1d8` (session 9 — GZ-4 mode-3 `to`-pump + GZ-5 mode-2 alt oracle; pushed, rebased cleanly onto the parallel SNOBOL4 `687aa58` SBL-EXEC-2 — zero conflicts, FACT-rule isolation held).

**Done this session (9, GZ-4 mode-3 + GZ-5 mode-2 — Sonnet 4.x):** Two pieces, both gated green, zero regressions.

**(A) GZ-4 `every write(1 to 3)` mode-3 stackless — DONE.** The `to` generator's β-resume PUMP
(the part `every` needs, fork-blocked at session 8) now lands stacklessly. TWO edits: (1) `bb_to.cpp`
MEDIUM_BINARY literal-bounds arm rewritten from single-shot (`β: jmp ω`) to the full pump grounded in
`test_icon.c` `to1` — `α: rax=lo; if lo>hi → ω; [r12+off]=lo; jmp γ` · `β: rax=[r12+off]; inc rax;
[r12+off]=rax; if rax>hi → ω; jmp γ`; lo/hi sealed RO data adjacent to the blob, read `[rip+63]`/`[rip+64]`
(α) and `[rip+19]` (β), ζ=r12, off via `bb_slot_alloc`. 5 patch sites (2×ω, 2×γ, 1×β-def). (2) `scrip.c`
`icn_rt_arity` gained `case IR_EVERY: return 1;` so the ring→tree adapter pops the body sub-tree as
EVERY.α (previously any `IR_EVERY` made the adapter return NULL → raw-ring fallback → no output). The
existing `flat_drive_every` ival==0 bodyless arm (`walk_bb_flat(pBB->α, body_β, lbl_γ, body_β)`) then
wires the re-pump. m2==m3 `1\n2\n3`; verified `5 to 1`→∅, `2 to 5`, `10 to 10`, `0 to 100`. **Icon smoke
m3 4/6→5/6** (`every` green; only `if_expr` remains, fork-blocked). NO `rt_push`/`rt_pop` added.

**(B) GZ-5 `every write(1 | 2 | 3)` mode-2 oracle (HARD gate) — DONE.** Was infinite-looping `1 1 1…`.
ROOT CAUSE (grounded in JCON `ir_a_Alt` + lower2 `wire_alt`, per CONSULT-CANONICAL-SOURCES): lower2
emits the alternation as a fail-chain — `EVERY.α = LIT_I(1)`; `LIT_I(1).ω→LIT_I(2)→LIT_I(3)→ω_in`; each
arm's γ funnels to the same `IR_ALT` node (whose own `α=NULL`, peeks the AG ring); `ALT.γ→CALL→EVERY`.
The mode-2 `every` ival==0 driver RESTARTED forward through the success port each pump (`cur=start=LIT_I(1)`),
and a literal always re-succeeds (`IR_LIT_I` returns γ unconditionally), so it re-yielded `1` forever.
The proper resume must propagate through the ω fail-chain to advance alternatives. FIX (`bb_exec.c`
IR_EVERY ival==0): a tightly-guarded branch that fires ONLY when `start` heads a sibling alt-chain
(`start->ω && start->γ && start->ω->γ == start->γ`) AND a pre-scan finds all arms single-shot
(`ir_is_single_shot`); it then walks the arms from `start->ω` (the main `bb_exec_once` loop already
produced the first arm's value before reaching EVERY — exactly as it produces value 1 for the `to`
case), each arm a forward walk to the ALT funnel → body. `to`, generator-arm alts, and all other shapes
fall through to the original restart loop **byte-identical** (the guard's `start->ω->γ != start->γ` for
the `to` operand-chain). Verified `1|2|3`, `10|20|30|40`. **Corpus 31→34 PASS, ZERO regressions**
(+`rung13_alt_alt_every_write`, `rung13_alt_alt_filter`, `rung13_alt_alt_int`); Icon m2 **6/6 HARD**.

**(C) GZ-5 mode-3 — STILL FORK-BLOCKED (honest).** `every write(1|2|3)` mode-3 emits nothing (exit 0,
no false-pass, no crash): `icn_ring_to_tree` returns NULL because `IR_ALT` arms hang off ω-branches, not
the γ-chain the postfix adapter walks. The mode-3 alt plan is pinned in the GZ-5 ladder step above
(adapter `IR_ALT` special-case + stackless `bb_alt.cpp` counter/value slots + `bb_call.cpp` write(alt)
slot read). Not started this session to avoid a half-landed byte emitter.

**GATES (this session):** FACT 0; no-stack ratchet 113 (unchanged — the `to`-pump adds no push/pop);
one-reg-frame 20 (unchanged — `[r12+off]` register-relative); Icon m2 6/6 HARD / m3 5/6; Prolog 2/5 &
broker 6/66 unchanged (non-Icon execution severed by design, provably unaffected — edits are Icon-only).

**INCIDENTAL FINDING (not fixed, not regressed, out of scope):** bodyless `every` over a *fully
single-shot* body (e.g. `every write(7)`) infinite-loops in the original ival==0 restart loop. Pre-existing;
no passing test exercises it (every passing every-test has a generator or alt-chain body). The clean fix
(detect a fully-single-shot body → produce once → return γ) is deferred.

PRIOR (session 8) ↓

**HEAD (SCRIP):** `f4f4d9a` (session 8 — GZ-4 every mode-2 oracle + string_op & to-single-shot mode-3 stackless; pushed, rebased cleanly onto the parallel Prolog `e1a6557` PLG-2 + SNOBOL4 `1eef20d` LOWER2-EXEC — zero conflicts, FACT-rule isolation held).

**Done this session (8, GZ-4 mode-2 oracle + string_op mode-3 stackless concat — Sonnet 4.5):**
Two fork-INDEPENDENT pieces (no commit yet; `refs/` re-extracted from the uploaded zips):

**(A) GZ-4 mode-2 `every` oracle — the independent HARD-GATE bug, FIXED.** `every write(1 to 3)`
printed only `1` because `lower2`'s `v_every` builds an `IR_EVERY` node with `ival==0` and the
generator embedded mid-chain (the EVERY node sits at the chain TAIL — both `TO.ω` and `CALL.γ`
flow back into it), but `bb_exec.c`'s `IR_EVERY` only had the deleted `lower_icn.c`'s `ival==1/2/3`
arms + a fallthrough `while` that did `bb_exec_node(bb->α)` ONCE — stepping the single-shot chain-
head `LIT_I`, so it broke after the first value. FIX: a new `ival==0` arm (grounded in JCON
`ir_a_Every`: `expr.success → body(empty=fail) → expr.resume; expr.failure → every.failure`) that
re-drives the whole expr chain from `bb->α` following ports, looping until the node that flows back
into EVERY fails (generator exhausted → done) or the chain hits a sink. Legacy `ival==1/2/3` arms
UNTOUCHED. Verified across `1 to 5`, empty `5 to 1`, `every i:=1 to 3 do write(i)`, nested
`(1 to 2)*10`, bare `write(1 to 3)`→one value. **Icon smoke m2 5/6→6/6 (HARD GATE green, smoke
exits 0 for the FIRST time)**; rung ladder `--interp` 28→31 (zero regressions, stash-verified
before/after); broker 4→5 (`ICN: 1 to 5`); Prolog 1 unchanged.

**(B) GZ-4 string_op (`write("ab"||"cd")`) — mode-3 stackless concat, the `string_op` smoke green.**
The handoff (7) flagged this as "doable in the Icon lane, same kind as GZ-3." Same graph shape as
GZ-3's int binop (adapter un-flattens `LIT_S/LIT_S` into `BINOP.α/β`); mode-3 aborted at GZ-3's
`write(binop)` slot-miss because the CONCAT arm allocated no slot. FIX, 4 contained files, NO value
stack: (1) `emit_bb.c` `bb_slot_alloc16` (DESCR is 16B). (2) `rt.c` `rt_write_strz_nl(const char*)`
(fwrite+strlen+nl — the concat buffer is NUL-terminated). (3) `bb_binop.cpp` stackless CONCAT arm
(both operands `IR_LIT_S`): bytes sealed RO in-blob, addresses read `lea …,[rip+disp]`, `call
str_concat_d` (gen_runtime.c; SysV a→rdi:rsi b→rdx:rcx, returns 16B DESCR rax:rdx), result stored
`[r12+off]`/`[r12+off+8]` (ζ=r12). (4) `bb_call.cpp` write(binop) split on `a0->ival==BINOP_CONCAT`
→ reads payload ptr `[r12+off+8]` + `rt_write_strz_nl`; int arm (ADD/SUB) keeps `[r12+off]` +
`rt_write_int_nl`. **Icon smoke m3 3/6→4/6** (`string_op` green, `diff m2 m3` empty). Verified
`hello||world`, `""||"x"`. Nested 3-way `"a"||"b"||"c"` fails mode-3 — the SAME pre-existing leaf-
only limitation as nested int `write(1+2+3)` (both literals required), NOT a regression.

**GATES (both pieces):** FACT 0; no-stack 113 (unchanged — `str_concat_d` is not a vstack helper);
one-reg-frame 20 (unchanged — `[r12+off]` register-relative); peers Prolog 1 / broker 5 unaffected.
**BONUS:** `--dump-bb` now prints each port's TARGET NODE INDEX (was `set`/`NULL`) — `scrip_ir.c`
`bb_index_of`; reusable wiring-trace infra for all three BB sessions.

**(C) GZ-4 `to` SINGLE-SHOT (α-port) — bare `write(1 to 3)` mode-3 stackless.** The `to` generator's
α-port (first value) is straight-line and fork-INDEPENDENT (only the β-resume PUMP that `every` needs
is fork-blocked). 3 contained edits, mirrors GZ-3 exactly: (1) `scrip.c` adapter `icn_rt_arity` —
`IR_TO`/`IR_TO_BY` arity 2 (un-flatten `LIT,LIT,TO` → `TO(α=lo,β=hi)`); previously arity −1 NULLed the
whole graph. (2) `bb_to.cpp` stackless single-shot arm (both bounds `IR_LIT_I`): lo/hi sealed RO in-blob
read `[rip+disp]`, `α: rax=lo; if lo>hi → ω; [r12+off]=rax → γ; β: jmp ω` (single-shot — pump deferred
to the fork), off via `bb_slot_alloc`. Grounded in `test_icon.c` `to1` α arm. (3) `bb_call.cpp` write
arm broadened to `IR_TO`/`IR_TO_BY` (TO value is int → reuses the int read `[r12+off]`+`rt_write_int_nl`;
the `BINOP_CONCAT` check now guarded to `IR_BINOP`). NO shared-driver change — `flat_drive_call_intexpr`
+ `case IR_TO: FILL` already walk arg-then-write correctly. Verified `write(1 to 3)`→1, `write(5 to 1)`
→∅, `write(2 to 5)`→2, `write(10 to 10)`→10, `write(0 to 100)`→0 — all m2==m3. **`every write(1 to 3)`
mode-3 STILL fails cleanly (exit 0, no crash, no false-pass)** — its graph has `IR_EVERY` (arity −1) so
the adapter still NULLs it → correctly fork-blocked; smoke unchanged m2 6/6 / m3 4/6 (the generator
smoke is `every`-wrapped, not bare). no-stack ratchet stays 113 (the dead `rt_push_int` literal/dynamic
paths remain until the full `to` rebuild under the fork; the single-shot arm adds zero push/pop).

**STILL fork-blocked (unchanged from 7):** mode-3 `if_expr` + `every` are CONTROL-FLOW rungs the
ring→tree adapter NULLs out. They need Lon's Path-1 vs Path-2 vs Path-1-lite decision (touches the
SHARED flat driver / the no-per-language-fork FACT RULE) before proceeding. `bb_to.cpp` still has 7
`rt_push_int` (value stack) — must go stackless under any path.

PRIOR (session 7) ↓

**HEAD (SCRIP):** `88bfc4e` (session 7 — GZ-3 stackless `write(1+2)` + mode-3 ring→tree adapter + Icon epilogue r10 fix; pushed, rebased onto the parallel session's `d17425a`).

**Done this session (7, GZ-3 + mode-3 unblock — Sonnet):** **ROOT FINDING (architecture-wide):** the unified `lower2` produces a postfix γ-chain for Icon (operands precede their operator in γ-order, every node `α=β=NULL`, operands read from the AG ring at exec — the mode-2 oracle's model). The mode-3 flat emitter (`emit_bb.c` `walk_bb_flat`/`flat_drive_binop_tree`/`flat_drive_call_intexpr`) and EVERY GROUND-ZERO template expect the OLD `lower_icn.c` **tree-shape** (operands in `α`/`β` children; verified in deleted blob `d2d8c8e1`: `bb->α=lhs;bb->β=rhs`, `bb->α=args[0]`). The two are incompatible: the flat walker starts at the entry leaf (a pass-through whose γ targets the slab exit), emits ONLY that one box, and returns → mode-3 silently emitted nothing. Mode-2's `bb_exec.c` was taught the ring shape (so m2 worked); mode-3 never was. **WATERMARK CORRECTION:** the prior "m2 6/6, m3 2/6" was stale/never-rebuilt — actual at session start (clean build from `03acf1be`, after `apt-get install libgc-dev`) was **m2 5/6** (`every` fails in MODE-2 — a separate pre-existing HARD-gate bug) and **m3 0/6** (GZ-2 would crash on the r10 clobber; GZ-1 only escaped by luck). Now honestly **m3 3/6**. **THREE-PART FIX (5 files, all contained or Icon-gated):** (1) `scrip.c` Icon mode-3 ring→tree adapter `icn_ring_to_tree` (Path 1-lite — un-flattens the straight-line γ-chain into the α/β tree by postfix arity; Icon `--run` only; emits no x86; fallback to `bbg->entry` on non-subset shapes; `lower.c`+templates untouched). (2) `xa_flat.cpp` Icon-gated (`g_frame_active`) epilogue → constant success, no Σ/r10 deref (fixes the r10 caller-saved clobber segfault; NON-ICON byte-identical). (3) GZ-3's four edit sites: `emit_bb.c` node→slot map + `bb_slot_alloc`/`bb_slot_get` (site 2, reset per sequence) and `flat_drive_binop_tree` RO-int skip (site 4); `bb_binop.cpp` stackless RO-int ADD/SUB arm — operands baked `[rip+disp]`, result `[r12+off]`, ζ=r12 FIRST real use (site 1); `bb_call.cpp` write(binop) reads `[r12+off]` (site 3). Grounded in `test_icon.c` `mult` (`mult_V=a*b`) per CONSULT-CANONICAL-SOURCES. **GATES:** FACT 0; no-stack ratchet observed **113** (≤127 — the watermark's 127 was stale; GZ-3 adds no push/pop so gate green either way; re-pin to 113 is optional hygiene, NOT done); one-reg-frame **20** (≤20 — `[r12+off]` is register-relative, no absolute `&pBB` added). SNOBOL4 (`hi-sno`) + Prolog (severed-loud) unaffected. **OPEN — the Path 1 vs Path 2 fork now GATES further mode-3 progress.** Remaining m3 fails split: `string_op` (`"ab"||"cd"`) is a straight-line concat rung (`rt_gen_concat` is still the stubbed vstack path) — doable IN THE ICON LANE next, same kind as GZ-3. `if_expr`/`every` are CONTROL-FLOW rungs: the adapter returns NULL for them (postfix un-flattening cannot express branch/iterate) → they fall back to no-output. They CANNOT advance without resolving the fork: **Path 1** (rewrite the mode-3 emitter to walk the γ-chain/ring natively — architecturally consistent with lower2 + mode-2, but touches the SHARED flat driver and discards GZ template bytes) vs **Path 2** (Icon tree-shape lowering — fights the SHARED-LOWERER no-per-language-fork FACT RULE) vs keeping **Path 1-lite** as a per-shape scaffold. `every` ALSO fails mode-2 (independent bug). Recommend Lon pick the fork before the control-flow rungs.

PRIOR (session 6) ↓

**HEAD (SCRIP):** `03acf1be` (session 6 — ζ→R12; pushed). This handoff folded onto the parallel SNOBOL4 session's `e06b5201` *SMX-CARRIER-1: decouple BB-graph table from SM_sequence_t into standalone bb_program_t* (clean rebase; combined tree builds + Icon smoke holds). R-HW-2 (`802521f1`) + ζ→R12 (`03acf1be`) now both pushed (prior pushed HEAD `690149e6`, session 4).

**Done this session (6, ζ→R12 + handoff):** Switched the Icon one-register frame register ζ from r15 to the RATIFIED **r12** (UNIFIED REGISTER LAYOUT) in XA_FLAT_PROLOGUE/EPILOGUE (`push r12`/`mov r12,rdi`/`pop r12`, Icon-gated). Byte-length-identical to the r15 form → NO bin-site offsets shifted; non-Icon arm untouched → SNOBOL4/Prolog byte-identical. Frame remains loaded-but-unused (GZ-3 is its first reader/writer via `[r12+off]`). Verified behavior-neutral: Icon m2 6/6, m3 2/6, FACT 0, no-stack 127, one-reg-frame 20, SM-death 11 all unmoved. Then performed the full handoff (rebase onto the SNOBOL4 SM-carrier work, push SCRIP, this goal file last). **Gates (re-run session 5):** FACT 0; no-stack ratchet **127** (lowered from 129 — string-write family rebuilt stackless in R-HW-2; baseline re-pinned in `test_gate_icn_no_stack.sh`); one-reg-frame ratchet 20 (unmoved — R-HW-2 is `[rip+disp]` only); death ratchet `test_gate_sm_dead.sh` 11 (unmoved); Icon smoke mode-2 6/6 (HARD), mode-3 **2/6** (`write_str` + `write_int` — `write_str` flipped green HONESTLY this session); Prolog 0/5 & broker 5/66 **intentionally RED** (non-Icon execution severed by design, SMX-1; provably unaffected by R-HW-2 — Prolog emits zero `BB_LIT_S` scalar nodes, edits are Icon-write-isolated). Survivors `write("hello")` and `write(42)` → mode-2==mode-3, dump-sm count=0.

**Done this session (5, R-HW-2 — honest stackless string write):** Made Icon mode-3 `write(string_literal)` genuinely stackless, flipping `write_str` mode-3 green for real (mode-3 1/6 → 2/6). Root cause (verified by live `addr2line` backtrace: slab → `rt_push_str` → `vstack_push` → `_default_push`): `write("…")` routed through the value-stack builtin-dispatch path, AND the standalone `BB_LIT_S` box (wired `LIT_S.γ→CALL`) pushed via `rt_push_str`. THREE coordinated edits (the bb_call arm alone was necessary-but-insufficient): (1) `emit_bb.c` — added the strlit shape to the BB_CALL `write_simple1` guard so `write("…")` bypasses `flat_drive_call_builtin` and takes the direct FILL arm; (2) `bb_call.cpp` — strlit MEDIUM_BINARY arm rewritten from `movabs rdi,&"…"` (abs AST-pool ptr, not relocatable, not RO-IP-relative) to sealed-blob `lea rdi,[rip+27]` + `mov esi,slen` + `call rt_write_str_nl`, mirroring GZ-2; (3) `bb_lit_scalar.cpp` — `BB_LIT_S` made a pure four-port pass-through identical to `BB_LIT_I` (the consumer reads the string RO via `[rip+disp]`; removed `rt_push_str` + its decl → no-stack ratchet −2). Mode-4 (`--compile`) TEXT arm confirmed already RO-IP-relative (`lea rdi,[rip + .Lcall_str]` + `.ascii` + `call rt_write_str_nl@PLT`); R-HW-3 needs assemble+run verification.

**NEXT — GZ-3 `write(1 + 2)` (the first RW-frame rung):** plus template reads RO operands `[rip+disp]`, computes, stores the RW result at `[reg+off]` in the one-register frame; write reads `[reg+off]`. This is the FIRST box carrying READ-WRITE state, so it engages the one-register frame (and the R15→R12 migration the layout ratified). Should flip the `arith` smoke to mode-3 PASS (→ 3/6). Per the ladder: ground the plus port topology in Proebsting §4.3 + `test_icon.c` `mult`/`greater` before emitting. R15→R12 frame move DONE (session 6). Also still pending (session 2): Ω/Σlen→Δ rename; strike `icn_bb_dcg` exemption (RULES line 11). Rollback tag: `pre-smx`.

**GZ-3 GROUNDING (session 5 — machinery inventory, so the next continuation executes directly):**
- *Graph shape* (verified `--dump-bb`): `write(1+2)` = tree-shape `BB_BINOP` (α→`LIT_I 1`, β→`LIT_I 2`, both pure RO operands with NO γ/ω wiring) consumed by `BB_CALL write`. Current m3 aborts on a **pop** (binop pushes operands + `rt_arith`, write pops) — full value-stack path.
- *Frame plumbing* (`xa_flat.cpp`, `g_icn_frame_active`): **DONE session 6 — ζ now on r12** (`push r12`/`mov r12,rdi`/`pop r12`); byte-neutral, all smokes green. The frame is loaded-but-unused; GZ-3 is its first reader/writer via `[r12+off]`.
- *Slot allocator* `g_flat_slot_count` (emit_bb.c:129): reset to 0 per `bb_build_flat`/`bb_build_brokered` but otherwise UNUSED. GZ-3 must drive it: a box claims `int off = g_flat_slot_count; g_flat_slot_count += 8;`. Need a per-node `BB_t* → off` map (add one; none wired yet) so a consumer reads its producer's slot offset.
- *Producer→consumer hand-off*: `bb_operand_aux_set/get` (`scrip_ir.c:150`) records a box's operand SOURCE nodes (binop's are the two LIT_I; write's is the binop). Use it (or the node→off map) so `write` reads the binop's result slot.
- *Stackless plus topology* (grounded in `test_icon.c` `mult`: `mult_V = to1_V * to2_V`; operands here are RO consts so plus is single-shot): `plus.α: mov rax,[rip+d1]; add rax,[rip+d2]; mov [r15+off],rax; jmp γ` · `plus.β: jmp ω`. Bake the two int64 operand values as sealed RO data in plus's own blob (like GZ-2 bakes its int), `d1`/`d2` emit-time disps.
- *Four edit sites*: (1) `bb_binop.cpp` MEDIUM_BINARY — add an all-RO-int-operands arm (read `pBB->α->ival`, `pBB->β->ival`; bake; mov/add; store `[r15+off]`); (2) the node→off map (new, in emit_bb.c); (3) `bb_call.cpp` write(int_expr) trailer — when arg0 is the binop, read `[r15+off]` + `rt_write_int_nl` instead of `rt_pop_write_int_nl`; (4) `flat_drive_binop_tree` (emit_bb.c:810) — for RO-const operands do NOT walk them as pushing boxes (the binop reads them directly), add the stackless arm. Gate exactly like R-HW-2 (m2==m3, dump-sm 0, FACT 0, no-stack→lower, one-reg-frame: this rung ADDS `[r15+off]` RW slots — those are register-relative, so the one-reg-frame ratchet stays 0/unchanged for abs-`&pBB` immediates; smoke `arith` → m3 PASS, → 3/6).

PRIOR SESSION 4 (SM EXCISION PHASE 0) watermark retained below for context.

**HEAD (SCRIP) [session 4]:** `690149e6` (2026-05-30 — SM EXCISION PHASE 0).

**Done this session (4, SM EXCISION):** Decided the Stack Machine is subsumed by the BB port-graph (carrying both was redundant; the SM/BB boundary was itself a bug source). Began **PHASE 0 — SM EXCISION** ("GROUND ZERO ALMOST": rip out SM execution, everything breaks but Icon still says hello). Method = sever execution + leave SM structures/emitter templates as **inert detonators** (deleted at the terminal rung as each language crosses), NOT a half-finished struct refactor. Build green and gated after each cut. **SMX-0** new death ratchet `scripts/test_gate_sm_dead.sh` (SM execution surface: `sm_interp_run`/`sm_run_native`/`g_vstack`; baseline 13→11; deliberately does NOT match per-box arenas or the `SM_sequence_t` container). **SMX-1** `scrip.c` — non-Icon mode-2 (`sm_interp_run`) + mode-3 (`sm_run_native`) entries → loud abort. **SMX-2** `sm_interp.c` — `sm_interp_run` dispatch loop → detonator at top (body kept as unreachable corpse so the struct still compiles until SMX-5). **SMX-3** `rt.c` — the three `g_vstack` storage primitives (`_default_push/pop/peek`) → detonator; array + ~159 consumers (not-yet-crossed langs, already severed at driver) removed at terminal. **PLAN CORRECTION confirmed:** `SM_sequence_t` (`src/include/SM.h`) carries the Icon `bb_table/bb_count/bb_cap` — SMX-5 **slims it (strip `instrs/count/cap/stno_*`), does NOT delete it.** **FINDING (survivor gate caught it):** nuking the value stack EXPOSED that Icon mode-3 `write("hello world")` was never stackless — emitted box → `rt_push_str` → `vstack_push` → `_default_push` (backtrace verified). GZ-1's "DONE / `rt_write_str_nl` / m2==m3" claim **does not match the binary.** `write_int` (GZ-2, genuine RO `[rip+disp]`) survives the nuke in mode-3; `write_str` (GZ-1) drops → mode-3 2/6→1/6, the dropped box is exactly hello. SNOBOL4 + Prolog confirmed detonating loudly in both modes.

**NEXT (two tracks; recommend the rebuild first):** **(A) ICON REBUILD — R-HW-2 (recommended):** make Icon mode-3 `write("hello world")` genuinely stackless — the string-write box loads `"hello world"` `[rip+disp]` and calls `rt_write_str_nl` directly, NO `rt_push_str`/value-stack. This flips `write_str` mode-3 back to green *honestly* (→ 2/6) and is the first box that, done right, is never touched again. Then GZ-3 (`write(1+2)`) onward per the ladder. **(B) FINISH DEMOLITION — SMX-4/SMX-5/terminal (deferred):** SMX-4 abort non-Icon SM *lowering*; SMX-5 **slim** `SM_sequence_t` (strip `instrs/count/cap/stno_*`, KEEP `bb_table/bb_count/bb_cap`) — requires gutting `sm_native.c` body first so it stops referencing stripped fields; terminal `rm` of `sm_native.c`/`sm_interp.c`/SM templates + the 11 corpse refs once every language has crossed (death ratchet → 0). Also still pending from session 2: move live Icon frame R15→R12; Ω/Σlen→Δ rename sweep; strike `icn_bb_dcg` exemption (RULES line 11). Rollback tag: `pre-smx`.

GROUND ZERO 3 — stackless rebuild. The IBB-* corpus numbers (the old 166-PASS line) are NOT a
baseline for this build; they were produced by the value-stack path now being removed.

| Step | State | Notes |
|------|-------|-------|
| Demolition | DONE | All Icon value-stack runtime consumers stubbed to `ICN_STACKLESS_ABORT` (23 sites): `rt_pop_nv_set`, `rt_pop_store_i64`, `rt_push_stored_i64`, `rt_pop_store_descr`, `rt_case_eq`, `rt_pop_write_int_nl`, `rt_pop_write_any_nl`, six `rt_unop_*`, ten vstack-using `rt_icn_*` (`call_proc`, `call_builtin`, `concat`, `field_get/set`, `idx_get/set`, `list_bang`, `limit_begin`, `toby_real`). Slot-based `rt_icn_limit_more/inc`, `proc_*` registry, `builtin_is_known`, and Raku `rt_load_frame`/`rt_store_frame` left LIVE. SNOBOL4/Prolog unaffected; Icon `--interp` 5/5; Icon `--run` aborts loudly at every value-stack box. |
| GZ-0 | DONE | No-stack gate pinned `scripts/test_gate_icn_no_stack.sh` (ratchet baseline 129). Slot/arena conventions grounded in archived `emit_arbno` + `test_icon.c`. |
| Smoke (two-mode) | DONE | `test_smoke_icon.sh` runs mode-2 (`--interp`, HARD GATE) AND mode-3 (`--run`, tracked) AND mode-4 (`--compile`); cases: write_str/write_int/arith/string_op/if_expr/every + GZ-9 while/until/repeat_break. Current m2 **9/9** (HARD green), m3 **9/9**, m4 **9/9** — GZ-8 (2026-05-31) made `if_expr` green in all three modes; GZ-9 (2026-05-31) added the three loop constructs green in all three modes. |
| GZ-1 `write("hello")` | **m2 DONE; m3 DONE (R-HW-2, s5)** | mode-2 stackless & green. mode-3 NOW genuinely stackless: the write box reads the literal `lea rdi,[rip+27]` from sealed RO bytes in its own blob + `call rt_write_str_nl` (no push). The earlier `rt_push_str` came from the standalone `BB_LIT_S` box (walked via `LIT_S.γ→CALL`) + the builtin-dispatch arg-walk, BOTH fixed in R-HW-2. `diff m2 m3` empty, dump-sm 0, no-stack 127. |
| GZ-2 `write(42)` | DONE (RO-IP-relative) | Literal int is a READ-ONLY constant: `BB_LIT_I` is pass-through; the write box emits the int64 as sealed RO data inside its own blob and reads it `mov rdi,[rip+22]` (emit-time disp, no patch/abs/stack), then `rt_write_int_nl`. m2==m3 `42`, count=0. Conforms to BOTH new FACT rules; no register frame needed for a constant. one-reg-frame abs-slot 22->20. |
| READ-ONLY LOCALS IP-RELATIVE (new FACT RULE 2026-05-30) | in force | RULES.md: per-box RO constants live in the SEALED segment next to their blob, read `[rip+disp]` (disp = emit-time const when data+access share the blob); only RW state uses the one-register frame. Applied to GZ-2. Shares the no-stack + one-reg-frame ratchets (no abs `&pBB->slot`). |
| ONE-REGISTER FRAME (new FACT RULE 2026-05-30) | frame ESTABLISHED | RULES.md: all Icon BB seqs/graphs (flat-wired AND brokered) stackless with ONE per-sequence local frame indexed by ONE BB-frame register (distinct from `r10` broker / `r13` SM-state); slots `[reg+off]` (the `ζ` model). 22 absolute `&pBB/a0->(value|counter|state)` emissions (incl. GZ-2's 2) are LEGACY -> ratchet `scripts/test_gate_icn_one_reg_frame.sh` (baseline 22) to 0. NEXT (grounded 2026-05-30): mode-3 entry is `bb_build_flat(entry)` -> driver calls `fn(zeta,entry)` (scrip.c ~564: `(void)fn(NULL,0)`); the `bb_box_fn(void*zeta,int entry)` convention ALREADY carries a frame pointer in `zeta`/rdi (currently NULL). `g_flat_slot_count` (emit_bb.c:129) is a per-sequence slot counter reset in `bb_build_flat`/`bb_build_brokered` but UNUSED — the intended slot allocator. `bb_build_brokered` already emits `push rbp; mov rbp,rsp`. PLAN: (a) driver allocates a per-sequence frame and passes it as zeta instead of NULL (or slab allocates); (b) `bb_build_flat` emits a prologue loading the BB-frame register (r15, callee-saved, survives rt_* calls; distinct from r10/r13) from rdi, and a single epilogue all exits reach (preserve caller's r15 across the slab `ret`); (c) assign each box its slot offset via `g_flat_slot_count`; (d) migrate GZ-2 literal store + write read from `&pBB->value`/`&a0->value` to `[r15+off]`; gate m2==m3, one-reg-frame ratchet 22->20. OPEN: r15 push/pop across the slab's ret structure (verify single vs multi exit). |
| Frame plumbing | DONE — **ζ on R12** (session 6) | BB-frame register ζ = **r12** (RATIFIED layout; callee-saved, survives rt_* calls; distinct from broker r10 / SM-state r13). XA_FLAT_PROLOGUE (Icon-gated `g_icn_frame_active`): `push r12`(`41 54`)`; mov r12,rdi`(`49 89 FC`) (replaces `sub rsp,8` — same rsp adjust, alignment preserved); XA_FLAT_EPILOGUE: `pop r12`(`41 5C`) before each ret. Byte-length-identical to the prior r15 form, so NO bin-site offsets shifted. Driver sets the flag around `bb_build_flat(main)` and passes `rt_icn_frame()` (static per-seq buffer) as zeta. SNOBOL4/Prolog byte-identical (flag off, non-Icon arm untouched). Frame still loaded-but-unused (first reader/writer = GZ-3); switch verified behavior-neutral: Icon m2 6/6, m3 2/6, all gates unmoved. |
| **SMX-0** (session 4) | DONE | Death ratchet `scripts/test_gate_sm_dead.sh` over SM execution surface (`sm_interp_run`/`sm_run_native`/`g_vstack`), baseline 13→11. Does NOT match per-box arenas or the `SM_sequence_t` container. `git tag pre-smx`. |
| **SMX-1** sever driver | DONE | `scrip.c`: non-Icon mode-2 (`sm_interp_run`) + mode-3 (`sm_run_native`) entries → loud `[SMX] FATAL` abort. Icon (`bb_exec_once`/`bb_build_flat`) untouched. |
| **SMX-2** gut interpreter | DONE | `sm_interp.c`: detonator at top of `sm_interp_run`; dispatch loop now unreachable corpse (kept compilable until SMX-5). |
| **SMX-3** nuke value stack | DONE | `rt.c`: `_default_push/pop/peek` → detonators. `g_vstack` array + ~159 consumers (not-yet-crossed langs, severed at driver) removed at terminal. |
| **SMX-CARRIER-1** decouple BB table | **DONE 2026-05-30 (SCRIP `e06b5201`)** | Lon directive (2026-05-30) SUPERSEDES old SMX-5 "keep bb_table inside SM_sequence_t": delete `SM_t`/`SM_sequence_t` ENTIRELY; the BB-graph table moves OUT to a standalone carrier. New `src/include/bb_program.h` `bb_program_t {table,count,cap}` + `bb_program_add`/`bb_program_free` (scrip_ir.c). `stage2_t` gains `bbp`; all 16 `SM_seq_bb_add` in lower.c + every `bb_table`/`bb_count` reader (scrip.c, scrip_sm.c, icn/pl runtime shims, sm_bb_invoke.cpp, sm_interp.c corpse) repointed to `bbp`. `sm` field kept TEMPORARILY (dead SM codegen/interp still read `s2->sm`). Verified: Icon m2 6/6 (HARD)/m3 1/6 IDENTICAL to pre-change — `lower_icn.c` emits zero SM so `bbp` is a transparent drop-in. FACT 0, no-stack 129, SM-death 11 unmoved. |
| **SMX-4** delete SM | **DONE 2026-05-30 Opus 4.8** | Deleted `sm_interp.c`/`sm_native.c`/`sm_codegen.c`/`sm_image.c`/`emit_sm.c`/`SM_templates/*` + all SM headers + SM test/tool sources. `lower.c` 3159→~440 (Icon-only; ~563 `SM_emit` sites + `g_p` gone; `lower()`/`lower_proc_skeletons` build BB graphs only). `SM.h` trimmed to the `SM_op_t` ENUM + `sm_opcode_name` (kept as shared opcode constants for `shared_arith`/`rt_protected`); **`SM_t`/`SM_sequence_t`/`SM_arg_t`/`SM_expr_t`/`SM_State` DELETED.** `stage2_t.sm` field removed. `emit_core.c` SM→backend walkers + `codegen_program` deleted (byte/label/patch primitives + relocated `strtab_label` kept). Driver SM paths (`--dump-sm`, mode-4 `sm_codegen_text`, JVM/JS/NET/WASM `codegen_program`, mode-3 `sm_run_native`) removed. `lower_ctx.c` `labtab_*` gone. `sm_prog.c` → only `stage2_*` helpers. New `smx_dead_stubs.c` (loud-abort `generator_state_new_proc`/`bb_broker_drive_sm_one` for dead SNOBOL4/Prolog generator branches). **Build green; Icon m2 6/6 (HARD)/m3 1/6 IDENTICAL; FACT 0; SM-death ratchet 11→1** (only `g_vstack` array storage remains — belongs to GZ-3/not-yet-crossed langs, out of scope). Handoff `HANDOFF-2026-05-30-OPUS48-SMX-4-DELETE-SM.md`. |
| **SMX terminal** delete | mostly folded into SMX-4 | Remaining: drop `g_vstack` (GZ-3 stackless work), delete/port the orphaned `emit_per_kind_audit.c` tool (carries synthetic `SM_t`; unbuilt). Death ratchet 1→0 when `g_vstack` goes. |
| **SNOBOL4 → BB directed graph** | NEXT (parallel) | Lon directive: SNOBOL4 lowers AST → `BB_graph_t` directed graph (like `lower_icn.c`), NOT a flat SM array. FIRST PROGRAM: `OUTPUT = "hello world"` → one `BB_ASSIGN`(target=OUTPUT global, value=`BB_LIT_S "hello world"`) registered as `main` in proc_table, routed through `bb_exec_once` in the scrip.c mode_interp branch exactly like Icon. Four-port AG: assign box α does the store+print, exits γ; ω unused for a total expression. SNOBOL4 `OUTPUT` semantics (SPITBOL manual): predefined var wired to stdout; assignment writes value + newline. |
| GZ-3 `write(1+2)` | **DONE (88bfc4e, session 7)** | Stackless integer binop. `bb_binop.cpp` RO-int ADD/SUB arm: bakes both operand int64s as sealed RO data in its own blob, reads them `mov rax,[rip+25]`/`add\|sub rax,[rip+26]`, stores the result `mov [r12+off],rax` into the one-register frame (ζ=r12, FIRST real use), off via `bb_slot_alloc`. `bb_call.cpp` write(binop) reads `mov rdi,[r12+off]` via `bb_slot_get` + `rt_write_int_nl`. `flat_drive_binop_tree` skips walking RO-int operands (they're baked, not pushed). PREREQUISITE: the ring→tree adapter (below) — lower2 emits all α=β=NULL postfix γ-chain, so the BINOP had no α/β children for the flat driver until reconstructed. m2==m3 `5`; round-trip verified ADD/SUB across values; FACT 0, no-stack 113, one-reg-frame 20. `arith` smoke m3 PASS → 3/6. |
| **Mode-3 ring→tree adapter** (session 7) | **DONE (88bfc4e)** | `scrip.c` static `icn_ring_to_tree` (Icon `--run` only, emits no x86). ROOT FIX: lower2 (the unified lowerer) produces a postfix γ-chain (operands precede operator in γ-order, all α=β=NULL, read from the AG ring at exec) but the mode-3 flat emitter + every GZ template expect the OLD `lower_icn.c` tree-shape (operands in α/β children; deleted blob `d2d8c8e1`: `bb->α=lhs;bb->β=rhs` / `bb->α=args[0]`). The mismatch made mode-3 silently emit ONLY the entry leaf → no output. Adapter un-flattens the straight-line chain into the α/β tree by postfix arity, sets entry=root, falls back to `bbg->entry` on shapes outside the GZ subset (control-flow → no regression). `lower.c` + templates UNTOUCHED. This is Path 1-lite (scaffold): carries straight-line rungs only. |
| **Icon epilogue r10 fix** (session 7) | **DONE (88bfc4e)** | `xa_flat.cpp` XA_FLAT_EPILOGUE, **g_frame_active-gated (Icon only)**: success path returns constant success (`mov eax,1; xor edx,edx`) with NO Σ/r10 deref. BUG: the shared epilogue did `movsxd rcx,[r10]` expecting r10 to still hold Δ from the prologue, but r10 is SysV CALLER-saved and `rt_write_int_nl`→`fprintf("%lld")` clobbers it (r10=1 at deref) → SEGFAULT after printing. The driver IGNORES the Icon slab return value so the Σ/r10 computation was vestigial. **NON-ICON (g_frame_active==0) keeps the original Σ/r10 bytes VERBATIM → SNOBOL4/Prolog byte-identical (verified `hi-sno` unaffected).** Not a shared-helper signature/semantic change → does NOT trigger the FACT lockstep clause; flagged here for the SNOBOL4/Prolog sessions' awareness. This unmasked that GZ-1's earlier "m3 DONE" + GZ-2's "m3 PASS" never honestly held post-SMX-4. |
| GZ-3 `write(1+2)` OLD ROW (superseded) | — | (prior text referenced `[r15+off]`; ζ is r12 since session 6.) |
| GZ-4 ... GZ-11+ | not started | Build on the one-register frame per the ladder. |
