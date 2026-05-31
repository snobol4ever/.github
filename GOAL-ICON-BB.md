# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

## 🧹 #1 — GROUND ZERO COMMENT & BLANK-LINE PURGE — DONE 2026-05-31

**First-place task this session (Lon).** Every hand-written `.c/.h/.y/.l` file under `one4all/src`
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
emitter existed ~1.5–2 months ago (archived at `one4all/archive/backend/emit_emitters/emit_x64.c`)
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

**References (now in-repo at `one4all/refs/bb/`):**
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
- `one4all/archive/backend/emit_emitters/emit_x64.c` — the prior working stackless emitter.

**NEW GATE (enforces stacklessness, parallel to the FACT gate):**
```bash
# Icon emission path must contain ZERO value-stack push/pop:
grep -rnoE 'rt_(push|pop)_[a-z_]+' src/emitter/BB_templates/ src/emitter/emit_bb.c \
  | grep -v _pl_ | wc -l        # target: 0 for every Icon box family as it is rebuilt
```
Plus the existing per-rung gate: `m2==m3` byte-identical, `--dump-sm` count=0 (zero SM),
FACT 0, smokes hold.

### Rung ladder (HELLO WORLD up — each gated, stackless, no `rt_push`/`rt_pop`)

- [x] **GZ-0 — Scaffold + gates.** Pin the no-stack gate above into `scripts/`. Confirm the
  per-box slot idiom (`&pBB->value`) is the value-storage primitive. Decide the slot/arena
  conventions by reading `emit_arbno` + one full pattern-node body in the archived `emit_x64.c`
  end-to-end, and `test_icon.c` for the Icon arithmetic shape. No code change beyond the gate script.
- [x] **GZ-1 — `write("hello")`.** One box, literal value in its own slot, write reads the slot.
  No push. m2==m3, zero-SM, no-stack gate = 0 for this box family.
- [x] **GZ-2 — `write(42)`.** Literal-N template (PDF §4.1): `lit.start: lit.value ← N; goto succeed`.
  Value in `&lit->value`. write reads it.
- [ ] **GZ-3 — `write(1 + 2)`.** plus template (PDF §4.3): `plus.value ← E1.value + E2.value`,
  read from the two child slots. No operand push/pop.
- [ ] **GZ-4 — `every write(1 to 3)`.** to template (PDF §4.4): `to.I`, `to.value` slots; β
  re-pumps via `to.resume: to.I++`. Mirror `test_icon.c` `to1`.
- [ ] **GZ-5 — `every write(1 | 2 | 3)`.** alt: `α save cursor → left_α; left_ω → right_α`
  (archive ALT wiring). Choice index in a per-box slot.
- [ ] **GZ-6 — `every write(5 > ((1 to 2) * (3 to 4)))`.** The paper's full example. Must be
  byte-identical to `test_icon.c` output AND structurally mirror Figure 1 (nine four-port
  templates, no stack). This rung proves stackless generator-nesting end to end. MILESTONE.
- [ ] **GZ-7 — `x := 42; write(x)`.** Flat slot for `x` (the archive's flat .bss var model).
- [ ] **GZ-8 — `if`/relop control, relop routes its OWN γ/ω.** Bake the branch into the relop
  (PDF LessThan: `if (E1 ≥ E2) goto E2.resume`); NO `LAST_OK` flag, NO `BB_IF` flag-router.
  This is the reference-faithful form (the old IBB-9-RELOP-PORTS, done correctly from scratch).
- [ ] **GZ-9 — `while`/`until`/`repeat`.** body.success/failure → cond.START (JCON `ir_a_While`);
  `until` swaps the cond edges. No router node.
- [ ] **GZ-10 — user procedure as a four-port FLAT box** (not a C-stack `call`). Model on
  `test_sno_3.c`: `(ζζ, entry)` calling convention, frame lazily allocated, `_λ` landing pad.
  Recursion depth lives in per-box arenas / heap frames, never a value stack.
- [ ] **GZ-DEFER — EVAL / CODE / `*P` deferred patterns** via the `test_sno_3.c` model. This was
  the ONE thing that broke the prior stackless build; it is solved in the reference file.
- [ ] **GZ-11+ — corpus features rebuilt stackless** (lists, tables, records, scanning, csets,
  builtins, sort, ...). Each: read the canonical JCON/Icon source first, then a flat slot/arena
  template, gated m2==m3 + zero-SM + no-stack=0 + no corpus regression.

---

**Reset:** 2026-05-30 (GROUND ZERO 3). All prior IBB-* rungs (the two vstack-based builds) removed
from this file — they were the regression, not a foundation. The build now starts again from
`write("hello")` on the stackless model. Demolition of the Icon value-stack consumers is the first
step (see Watermark).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/test_sno_1.c` · `.github/test_sno_3.c` · `.github/jcon_irgen.icn` · `one4all/refs/bb/Proebsting-Simple-Translation-of-Goal-Directed-Evaluation.pdf` · `one4all/archive/backend/emit_emitters/emit_x64.c` (prior working stackless emitter).

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
cd /home/claude/one4all
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

- [x] **R-HW-2 — Mode-3 (`--run`) stackless RO-string box.** DONE (2026-05-30, session 5). The write
  box emits the string as sealed RO data inside its own blob and reads its ADDRESS `lea rdi,[rip+27]`
  (not `mov` — write_str_nl takes a pointer+len, not a loaded value); `mov esi,slen`; `movabs rax,&rt_write_str_nl`;
  `call rax`; γ → halt; β: jmp ω. NO frame, NO subject regs, NO `rt_push`/`rt_pop`. THREE coordinated
  edits were required (the single bb_call arm was necessary but not sufficient): (1) `emit_bb.c` BB_CALL
  dispatch — `write("…")` was routing through `flat_drive_call_builtin` (because `rt_icn_builtin_is_known("write")`
  is true and the old `write_simple1` guard only excluded int-expr shapes), whose arg γ-chain walk pushed
  the literal; added the strlit shape to the guard so it falls to the direct FILL arm. (2) `bb_call.cpp`
  strlit MEDIUM_BINARY arm — replaced `movabs rdi,&"…"` (abs AST-pool ptr) with the RO-IP-relative
  sealed-blob `lea rdi,[rip+27]` form, mirroring GZ-2's int box. (3) `bb_lit_scalar.cpp` — `BB_LIT_S`
  was the actual pusher (the lowering wires `LIT_S.γ → CALL`, so the standalone lit box is walked and ran
  `rt_push_str`); made it a pure four-port pass-through identical to `BB_LIT_I` (consumer reads RO via
  `[rip+disp]`). Gate: `diff out_m2 out_m3` empty; dump-sm count=0; FACT 0; no-stack ratchet 129→**127**
  (re-pinned — string-write family rebuilt stackless); one-reg-frame 20 UNCHANGED (`[rip+disp]` only).

- [ ] **R-HW-3 — Mode-4 (`--compile`) parity.** Same box in the linked binary's `.text`/`.data`;
  the only inter-box transition (entry → box → halt) is a `jmp`; run ⇒ identical `hello world\n`.
  Mode-3 and mode-4 differ ONLY at the boundary (return-to-driver vs `exit`), proving the model
  is mode-agnostic. (PEEK 2026-05-30: the MEDIUM_TEXT arm already emits `lea rdi,[rip + .Lcall_str]`
  + `.ascii` + `call rt_write_str_nl@PLT` — RO-IP-relative, no push. Needs assemble+run verification.)

- [ ] **R-HW-4 — Full gate sweep + smokes.** All per-rung gates green; `test_smoke_icon.sh`
  mode-2 6/6 (HARD) with mode-3 now including hello-world; `test_smoke_prolog.sh` 5/5;
  `test_smoke_unified_broker.sh` ≥35. Ratchets (no-stack, one-reg-frame) unmoved. This rung is
  the ratified-layout baseline; later rungs may only lower ratchets, never raise them.

---



**HEAD (one4all):** `03acf1be` (session 6 — ζ→R12; pushed). This handoff folded onto the parallel SNOBOL4 session's `e06b5201` *SMX-CARRIER-1: decouple BB-graph table from SM_sequence_t into standalone bb_program_t* (clean rebase; combined tree builds + Icon smoke holds). R-HW-2 (`802521f1`) + ζ→R12 (`03acf1be`) now both pushed (prior pushed HEAD `690149e6`, session 4).

**Done this session (6, ζ→R12 + handoff):** Switched the Icon one-register frame register ζ from r15 to the RATIFIED **r12** (UNIFIED REGISTER LAYOUT) in XA_FLAT_PROLOGUE/EPILOGUE (`push r12`/`mov r12,rdi`/`pop r12`, Icon-gated). Byte-length-identical to the r15 form → NO bin-site offsets shifted; non-Icon arm untouched → SNOBOL4/Prolog byte-identical. Frame remains loaded-but-unused (GZ-3 is its first reader/writer via `[r12+off]`). Verified behavior-neutral: Icon m2 6/6, m3 2/6, FACT 0, no-stack 127, one-reg-frame 20, SM-death 11 all unmoved. Then performed the full handoff (rebase onto the SNOBOL4 SM-carrier work, push one4all, this goal file last). **Gates (re-run session 5):** FACT 0; no-stack ratchet **127** (lowered from 129 — string-write family rebuilt stackless in R-HW-2; baseline re-pinned in `test_gate_icn_no_stack.sh`); one-reg-frame ratchet 20 (unmoved — R-HW-2 is `[rip+disp]` only); death ratchet `test_gate_sm_dead.sh` 11 (unmoved); Icon smoke mode-2 6/6 (HARD), mode-3 **2/6** (`write_str` + `write_int` — `write_str` flipped green HONESTLY this session); Prolog 0/5 & broker 5/66 **intentionally RED** (non-Icon execution severed by design, SMX-1; provably unaffected by R-HW-2 — Prolog emits zero `BB_LIT_S` scalar nodes, edits are Icon-write-isolated). Survivors `write("hello")` and `write(42)` → mode-2==mode-3, dump-sm count=0.

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

**HEAD (one4all) [session 4]:** `690149e6` (2026-05-30 — SM EXCISION PHASE 0).

**Done this session (4, SM EXCISION):** Decided the Stack Machine is subsumed by the BB port-graph (carrying both was redundant; the SM/BB boundary was itself a bug source). Began **PHASE 0 — SM EXCISION** ("GROUND ZERO ALMOST": rip out SM execution, everything breaks but Icon still says hello). Method = sever execution + leave SM structures/emitter templates as **inert detonators** (deleted at the terminal rung as each language crosses), NOT a half-finished struct refactor. Build green and gated after each cut. **SMX-0** new death ratchet `scripts/test_gate_sm_dead.sh` (SM execution surface: `sm_interp_run`/`sm_run_native`/`g_vstack`; baseline 13→11; deliberately does NOT match per-box arenas or the `SM_sequence_t` container). **SMX-1** `scrip.c` — non-Icon mode-2 (`sm_interp_run`) + mode-3 (`sm_run_native`) entries → loud abort. **SMX-2** `sm_interp.c` — `sm_interp_run` dispatch loop → detonator at top (body kept as unreachable corpse so the struct still compiles until SMX-5). **SMX-3** `rt.c` — the three `g_vstack` storage primitives (`_default_push/pop/peek`) → detonator; array + ~159 consumers (not-yet-crossed langs, already severed at driver) removed at terminal. **PLAN CORRECTION confirmed:** `SM_sequence_t` (`src/include/SM.h`) carries the Icon `bb_table/bb_count/bb_cap` — SMX-5 **slims it (strip `instrs/count/cap/stno_*`), does NOT delete it.** **FINDING (survivor gate caught it):** nuking the value stack EXPOSED that Icon mode-3 `write("hello world")` was never stackless — emitted box → `rt_push_str` → `vstack_push` → `_default_push` (backtrace verified). GZ-1's "DONE / `rt_write_str_nl` / m2==m3" claim **does not match the binary.** `write_int` (GZ-2, genuine RO `[rip+disp]`) survives the nuke in mode-3; `write_str` (GZ-1) drops → mode-3 2/6→1/6, the dropped box is exactly hello. SNOBOL4 + Prolog confirmed detonating loudly in both modes.

**NEXT (two tracks; recommend the rebuild first):** **(A) ICON REBUILD — R-HW-2 (recommended):** make Icon mode-3 `write("hello world")` genuinely stackless — the string-write box loads `"hello world"` `[rip+disp]` and calls `rt_write_str_nl` directly, NO `rt_push_str`/value-stack. This flips `write_str` mode-3 back to green *honestly* (→ 2/6) and is the first box that, done right, is never touched again. Then GZ-3 (`write(1+2)`) onward per the ladder. **(B) FINISH DEMOLITION — SMX-4/SMX-5/terminal (deferred):** SMX-4 abort non-Icon SM *lowering*; SMX-5 **slim** `SM_sequence_t` (strip `instrs/count/cap/stno_*`, KEEP `bb_table/bb_count/bb_cap`) — requires gutting `sm_native.c` body first so it stops referencing stripped fields; terminal `rm` of `sm_native.c`/`sm_interp.c`/SM templates + the 11 corpse refs once every language has crossed (death ratchet → 0). Also still pending from session 2: move live Icon frame R15→R12; Ω/Σlen→Δ rename sweep; strike `icn_bb_dcg` exemption (RULES line 11). Rollback tag: `pre-smx`.

GROUND ZERO 3 — stackless rebuild. The IBB-* corpus numbers (the old 166-PASS line) are NOT a
baseline for this build; they were produced by the value-stack path now being removed.

| Step | State | Notes |
|------|-------|-------|
| Demolition | DONE | All Icon value-stack runtime consumers stubbed to `ICN_STACKLESS_ABORT` (23 sites): `rt_pop_nv_set`, `rt_pop_store_i64`, `rt_push_stored_i64`, `rt_pop_store_descr`, `rt_case_eq`, `rt_pop_write_int_nl`, `rt_pop_write_any_nl`, six `rt_unop_*`, ten vstack-using `rt_icn_*` (`call_proc`, `call_builtin`, `concat`, `field_get/set`, `idx_get/set`, `list_bang`, `limit_begin`, `toby_real`). Slot-based `rt_icn_limit_more/inc`, `proc_*` registry, `builtin_is_known`, and Raku `rt_load_frame`/`rt_store_frame` left LIVE. SNOBOL4/Prolog unaffected; Icon `--interp` 5/5; Icon `--run` aborts loudly at every value-stack box. |
| GZ-0 | DONE | No-stack gate pinned `scripts/test_gate_icn_no_stack.sh` (ratchet baseline 129). Slot/arena conventions grounded in archived `emit_arbno` + `test_icon.c`. |
| Smoke (two-mode) | DONE | `test_smoke_icon.sh` runs mode-2 (`--interp`, HARD GATE) AND mode-3 (`--run`, tracked); added `write_int` case. Current m2 6/6, m3 2/6. |
| GZ-1 `write("hello")` | **m2 DONE; m3 DONE (R-HW-2, s5)** | mode-2 stackless & green. mode-3 NOW genuinely stackless: the write box reads the literal `lea rdi,[rip+27]` from sealed RO bytes in its own blob + `call rt_write_str_nl` (no push). The earlier `rt_push_str` came from the standalone `BB_LIT_S` box (walked via `LIT_S.γ→CALL`) + the builtin-dispatch arg-walk, BOTH fixed in R-HW-2. `diff m2 m3` empty, dump-sm 0, no-stack 127. |
| GZ-2 `write(42)` | DONE (RO-IP-relative) | Literal int is a READ-ONLY constant: `BB_LIT_I` is pass-through; the write box emits the int64 as sealed RO data inside its own blob and reads it `mov rdi,[rip+22]` (emit-time disp, no patch/abs/stack), then `rt_write_int_nl`. m2==m3 `42`, count=0. Conforms to BOTH new FACT rules; no register frame needed for a constant. one-reg-frame abs-slot 22->20. |
| READ-ONLY LOCALS IP-RELATIVE (new FACT RULE 2026-05-30) | in force | RULES.md: per-box RO constants live in the SEALED segment next to their blob, read `[rip+disp]` (disp = emit-time const when data+access share the blob); only RW state uses the one-register frame. Applied to GZ-2. Shares the no-stack + one-reg-frame ratchets (no abs `&pBB->slot`). |
| ONE-REGISTER FRAME (new FACT RULE 2026-05-30) | frame ESTABLISHED | RULES.md: all Icon BB seqs/graphs (flat-wired AND brokered) stackless with ONE per-sequence local frame indexed by ONE BB-frame register (distinct from `r10` broker / `r13` SM-state); slots `[reg+off]` (the `ζ` model). 22 absolute `&pBB/a0->(value|counter|state)` emissions (incl. GZ-2's 2) are LEGACY -> ratchet `scripts/test_gate_icn_one_reg_frame.sh` (baseline 22) to 0. NEXT (grounded 2026-05-30): mode-3 entry is `bb_build_flat(entry)` -> driver calls `fn(zeta,entry)` (scrip.c ~564: `(void)fn(NULL,0)`); the `bb_box_fn(void*zeta,int entry)` convention ALREADY carries a frame pointer in `zeta`/rdi (currently NULL). `g_flat_slot_count` (emit_bb.c:129) is a per-sequence slot counter reset in `bb_build_flat`/`bb_build_brokered` but UNUSED — the intended slot allocator. `bb_build_brokered` already emits `push rbp; mov rbp,rsp`. PLAN: (a) driver allocates a per-sequence frame and passes it as zeta instead of NULL (or slab allocates); (b) `bb_build_flat` emits a prologue loading the BB-frame register (r15, callee-saved, survives rt_* calls; distinct from r10/r13) from rdi, and a single epilogue all exits reach (preserve caller's r15 across the slab `ret`); (c) assign each box its slot offset via `g_flat_slot_count`; (d) migrate GZ-2 literal store + write read from `&pBB->value`/`&a0->value` to `[r15+off]`; gate m2==m3, one-reg-frame ratchet 22->20. OPEN: r15 push/pop across the slab's ret structure (verify single vs multi exit). |
| Frame plumbing | DONE — **ζ on R12** (session 6) | BB-frame register ζ = **r12** (RATIFIED layout; callee-saved, survives rt_* calls; distinct from broker r10 / SM-state r13). XA_FLAT_PROLOGUE (Icon-gated `g_icn_frame_active`): `push r12`(`41 54`)`; mov r12,rdi`(`49 89 FC`) (replaces `sub rsp,8` — same rsp adjust, alignment preserved); XA_FLAT_EPILOGUE: `pop r12`(`41 5C`) before each ret. Byte-length-identical to the prior r15 form, so NO bin-site offsets shifted. Driver sets the flag around `bb_build_flat(main)` and passes `rt_icn_frame()` (static per-seq buffer) as zeta. SNOBOL4/Prolog byte-identical (flag off, non-Icon arm untouched). Frame still loaded-but-unused (first reader/writer = GZ-3); switch verified behavior-neutral: Icon m2 6/6, m3 2/6, all gates unmoved. |
| **SMX-0** (session 4) | DONE | Death ratchet `scripts/test_gate_sm_dead.sh` over SM execution surface (`sm_interp_run`/`sm_run_native`/`g_vstack`), baseline 13→11. Does NOT match per-box arenas or the `SM_sequence_t` container. `git tag pre-smx`. |
| **SMX-1** sever driver | DONE | `scrip.c`: non-Icon mode-2 (`sm_interp_run`) + mode-3 (`sm_run_native`) entries → loud `[SMX] FATAL` abort. Icon (`bb_exec_once`/`bb_build_flat`) untouched. |
| **SMX-2** gut interpreter | DONE | `sm_interp.c`: detonator at top of `sm_interp_run`; dispatch loop now unreachable corpse (kept compilable until SMX-5). |
| **SMX-3** nuke value stack | DONE | `rt.c`: `_default_push/pop/peek` → detonators. `g_vstack` array + ~159 consumers (not-yet-crossed langs, severed at driver) removed at terminal. |
| **SMX-CARRIER-1** decouple BB table | **DONE 2026-05-30 (one4all `e06b5201`)** | Lon directive (2026-05-30) SUPERSEDES old SMX-5 "keep bb_table inside SM_sequence_t": delete `SM_t`/`SM_sequence_t` ENTIRELY; the BB-graph table moves OUT to a standalone carrier. New `src/include/bb_program.h` `bb_program_t {table,count,cap}` + `bb_program_add`/`bb_program_free` (scrip_ir.c). `stage2_t` gains `bbp`; all 16 `SM_seq_bb_add` in lower.c + every `bb_table`/`bb_count` reader (scrip.c, scrip_sm.c, icn/pl runtime shims, sm_bb_invoke.cpp, sm_interp.c corpse) repointed to `bbp`. `sm` field kept TEMPORARILY (dead SM codegen/interp still read `s2->sm`). Verified: Icon m2 6/6 (HARD)/m3 1/6 IDENTICAL to pre-change — `lower_icn.c` emits zero SM so `bbp` is a transparent drop-in. FACT 0, no-stack 129, SM-death 11 unmoved. |
| **SMX-4** delete SM | **DONE 2026-05-30 Opus 4.8** | Deleted `sm_interp.c`/`sm_native.c`/`sm_codegen.c`/`sm_image.c`/`emit_sm.c`/`SM_templates/*` + all SM headers + SM test/tool sources. `lower.c` 3159→~440 (Icon-only; ~563 `SM_emit` sites + `g_p` gone; `lower()`/`lower_proc_skeletons` build BB graphs only). `SM.h` trimmed to the `SM_op_t` ENUM + `sm_opcode_name` (kept as shared opcode constants for `shared_arith`/`rt_protected`); **`SM_t`/`SM_sequence_t`/`SM_arg_t`/`SM_expr_t`/`SM_State` DELETED.** `stage2_t.sm` field removed. `emit_core.c` SM→backend walkers + `codegen_program` deleted (byte/label/patch primitives + relocated `strtab_label` kept). Driver SM paths (`--dump-sm`, mode-4 `sm_codegen_text`, JVM/JS/NET/WASM `codegen_program`, mode-3 `sm_run_native`) removed. `lower_ctx.c` `labtab_*` gone. `sm_prog.c` → only `stage2_*` helpers. New `smx_dead_stubs.c` (loud-abort `generator_state_new_proc`/`bb_broker_drive_sm_one` for dead SNOBOL4/Prolog generator branches). **Build green; Icon m2 6/6 (HARD)/m3 1/6 IDENTICAL; FACT 0; SM-death ratchet 11→1** (only `g_vstack` array storage remains — belongs to GZ-3/not-yet-crossed langs, out of scope). Handoff `HANDOFF-2026-05-30-OPUS48-SMX-4-DELETE-SM.md`. |
| **SMX terminal** delete | mostly folded into SMX-4 | Remaining: drop `g_vstack` (GZ-3 stackless work), delete/port the orphaned `emit_per_kind_audit.c` tool (carries synthetic `SM_t`; unbuilt). Death ratchet 1→0 when `g_vstack` goes. |
| **SNOBOL4 → BB directed graph** | NEXT (parallel) | Lon directive: SNOBOL4 lowers AST → `BB_graph_t` directed graph (like `lower_icn.c`), NOT a flat SM array. FIRST PROGRAM: `OUTPUT = "hello world"` → one `BB_ASSIGN`(target=OUTPUT global, value=`BB_LIT_S "hello world"`) registered as `main` in proc_table, routed through `bb_exec_once` in the scrip.c mode_interp branch exactly like Icon. Four-port AG: assign box α does the store+print, exits γ; ω unused for a total expression. SNOBOL4 `OUTPUT` semantics (SPITBOL manual): predefined var wired to stdout; assignment writes value + newline. |
| GZ-3 `write(1+2)` | NEXT | plus reads RO operands `[rip+disp]`, computes, stores RW result at `[r15+off]`; write reads `[r15+off]`. Should flip the `arith` smoke to m3 PASS (-> 3/6). |
| GZ-4 ... GZ-11+ | not started | Build on the one-register frame per the ladder. |
