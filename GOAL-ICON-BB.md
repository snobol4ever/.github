# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

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


## NEXT SESSION — UNIFIED REGISTER LAYOUT (design, not yet implemented)

**Context (2026-05-30):** Icon is *not* in proper development yet — GROUND ZERO 3 only started scaffolding (GZ-0/1/2), not real development. Before going further, design ONE x86-64 register layout for all 6 languages. The work below is grounded in the archive + live code; nothing here is implemented yet.

**The standardized floor is System V AMD64.** Caller-saved/scratch (9): RAX(ret), RCX/RDX/RSI/RDI/R8/R9(args), R10(static-chain), R11(PLT). Callee-saved (7): RBX, RBP(frame ptr), RSP(stack ptr), R12, R13, R14, R15. Int-arg order RDI,RSI,RDX,RCX,R8,R9; return RAX(+RDX). Claimable durable globals = RBX,R12,R13,R14,R15 (+RBP if -fomit-frame-pointer).

**Core principle:** anything that must live across a C `call` (our global-type pointers) goes in a CALLEE-SAVED register, so it survives every `rt_*` call with NO per-call save/restore. The only save is once, at a cross-language boundary. Today SNOBOL4's cursor is in caller-saved R10 (`&Δ`) → it pays a `push r10`/`pop r10` tax on every call; moving it to a callee-saved reg deletes that tax.

**Two kinds of BB locals, two bases (this is the existing convention, NOT new):**
- READ-WRITE locals → `[R12 + off]`. R12 is the BB-local frame base (Technique-2 / `M-T2-EMIT-SPLIT`: "r12 = DATA-block ptr; all locals [r12+offset]"). The ARBNO arena (`z`/`zo`), capture `saved_Δ`, Icon runtime values all live here. (NOTE: the Icon frame was wrongly wired to R15 this session — it must move to R12 to rejoin the convention. Also: live SNOBOL4 `BB_PAT_*` regressed to per-slot `movabs rcx,<abs>` and must come back to `[r12+off]`.)
- READ-ONLY locals → `[RIP + disp]` from the sealed blob (literals, baked addresses). No register.

**Proposed durable assignments (to ratify next session):**
| reg | role | who |
|---|---|---|
| R12 | ζ = BB-local RW frame base, `[r12+off]` | all langs |
| R13 | subject base Σ | pattern langs (SNOBOL4, Icon scan) |
| RBX | cursor Δ (move off caller-saved R10) | pattern langs |
| R14 | value-stack top → `g_vstack` | SNOBOL4·Snocone·Rebus·Raku. Prolog: reuse for trail/choice-point ptr. Icon/Prolog have NO value stack → free |
| R15 | free / reserve | (was mistakenly the Icon frame) |
| RDI | ζ inbound transport → copied to R12, then scratch | — |
| RSI | α/β entry selector transport → scratch | — (see x86 selector note) |
| RAX | result / γ value (DESCR_t) | — |
| RCX/RDX/R8/R9/R10/R11 | rt_* args + scratch | — |
| RSP/RBP | C stack / frame ptr (RBP free if -fomit-frame-pointer → NV-table base) | — |

**Long-lived global state (grounded, the register-cache candidates):** `g_vstack[VSTACK_CAP]` (DESCR_t value stack, rt.c) · `Σ/Δ/Ω/Σlen` (bb_box.h subject scan) · `NV_GET_fn/NV_SET_fn` (named-value table = global variables, by name-hash) · `DESCR_t` (16-byte universal value) · the per-sequence RW frame.

**C BB BOX DEMOLITION (forbidden by RULES line 11; exemption REVOKED — `icn_bb_dcg` is NOT exempt, strike that clause).** A C BB box = a C function that (a) switches on entry α/β AND (b) wires four ports (α/β/γ/ω) inside. Those must be deleted and rebuilt as emitted wired graphs. VERIFIED genuine four-port C boxes (α AND β entry switch + γ and ω labels wired inside) = exactly TWO: `bb_deferred_var` (SNOBOL4 deferred, stmt_exec.c — `entry==α goto DVAR_α; entry==β goto DVAR_β;` + DVAR_γ/ω, re-enters child_fn) and `pl_cat_fn` (Prolog seq, pl_broker.c — `entry==α goto CAT_α; goto CAT_β;` + left_γ/ω, right_γ/ω). Exhaustive scan: only stmt_exec.c + pl_broker.c hold any `(void*,int entry)` fn with both γ and ω labels. NOT boxes by the test: `pl_choice_fn`/`pl_chunk_fn` (switch α/β but NO γ/ω labels — value-returning); `pl_true/fail/builtin/unify/head_unify/cut/alt/deferred_env_fn`, `icn_bb_oneshot`, `icn_fail_box` (single-entry leaves/wrappers); `pl_bb_dcg`, `icn_bb_dcg` (α-only bb_exec_once drivers). The x86 α/β selector (`cmp esi,0; jne β` in XA_FLAT_PROLOGUE + XA_ENTRY_DISPATCH) is LIVE: it's how brokered boxes are re-entered at β from `stmt_exec.c`/`pl_runtime.c`. It can only be deleted after those re-entries become wired `jmp`s.


## Watermark

**HEAD (one4all):** `a641bfb0` (2026-05-30, session 2). **Gates:** FACT 0; no-stack ratchet 129; one-reg-frame ratchet 20; Icon smoke mode-2 6/6 (hard), mode-3 2/6; Prolog 5/5; broker 61 — ALL HELD. **Done this session:** (1) Designed the unified x86-64 register layout for all 6 languages — see "NEXT SESSION — UNIFIED REGISTER LAYOUT" section above (durable globals in callee-saved regs; RW locals `[R12+off]`, RO locals `[RIP+disp]`; R12=frame, R13=Σ, RBX=Δ, R14=value-stack/Prolog-trail/free-for-Icon, R15=reserve; the Icon frame wrongly on R15 must move to R12). (2) Established the C BB box test (C + α/β entry switch + γ/ω labels) and DELETED the two genuine ones, stub-to-loud-abort: `bb_deferred_var` (SNOBOL4 deferred, stmt_exec.c) + `pl_cat_fn` (Prolog seq, pl_broker.c) — both were on legacy/unexercised paths, so all gates held. These two are the only real users of the x86 α/β entry selector (`cmp esi,0; jne β` in XA_FLAT_PROLOGUE + XA_ENTRY_DISPATCH); rebuilding them as emitted wired graphs (β = jmp target) is what lets that selector be deleted. (3) `icn_bb_dcg` exemption in RULES line 11 is REVOKED (no C BB box exempt) — strike that clause next session. Icon is NOT yet in proper development. **NEXT:** ratify the register layout, then (a) move Icon frame R15→R12 + restore SNOBOL4 ARBNO/capture scattered `movabs rcx` slots to `[r12+off]`; (b) rebuild `bb_deferred_var`/`pl_cat_fn` as wired graphs; (c) delete the x86 α/β entry selector.

GROUND ZERO 3 — stackless rebuild. The IBB-* corpus numbers (the old 166-PASS line) are NOT a
baseline for this build; they were produced by the value-stack path now being removed.

| Step | State | Notes |
|------|-------|-------|
| Demolition | DONE | All Icon value-stack runtime consumers stubbed to `ICN_STACKLESS_ABORT` (23 sites): `rt_pop_nv_set`, `rt_pop_store_i64`, `rt_push_stored_i64`, `rt_pop_store_descr`, `rt_case_eq`, `rt_pop_write_int_nl`, `rt_pop_write_any_nl`, six `rt_unop_*`, ten vstack-using `rt_icn_*` (`call_proc`, `call_builtin`, `concat`, `field_get/set`, `idx_get/set`, `list_bang`, `limit_begin`, `toby_real`). Slot-based `rt_icn_limit_more/inc`, `proc_*` registry, `builtin_is_known`, and Raku `rt_load_frame`/`rt_store_frame` left LIVE. SNOBOL4/Prolog unaffected; Icon `--interp` 5/5; Icon `--run` aborts loudly at every value-stack box. |
| GZ-0 | DONE | No-stack gate pinned `scripts/test_gate_icn_no_stack.sh` (ratchet baseline 129). Slot/arena conventions grounded in archived `emit_arbno` + `test_icon.c`. |
| Smoke (two-mode) | DONE | `test_smoke_icon.sh` runs mode-2 (`--interp`, HARD GATE) AND mode-3 (`--run`, tracked); added `write_int` case. Current m2 6/6, m3 2/6. |
| GZ-1 `write("hello")` | DONE | Stackless literal-string (`MEDIUM_TEXT` -> `rt_write_str_nl`). m2==m3, count=0. |
| GZ-2 `write(42)` | DONE (RO-IP-relative) | Literal int is a READ-ONLY constant: `BB_LIT_I` is pass-through; the write box emits the int64 as sealed RO data inside its own blob and reads it `mov rdi,[rip+22]` (emit-time disp, no patch/abs/stack), then `rt_write_int_nl`. m2==m3 `42`, count=0. Conforms to BOTH new FACT rules; no register frame needed for a constant. one-reg-frame abs-slot 22->20. |
| READ-ONLY LOCALS IP-RELATIVE (new FACT RULE 2026-05-30) | in force | RULES.md: per-box RO constants live in the SEALED segment next to their blob, read `[rip+disp]` (disp = emit-time const when data+access share the blob); only RW state uses the one-register frame. Applied to GZ-2. Shares the no-stack + one-reg-frame ratchets (no abs `&pBB->slot`). |
| ONE-REGISTER FRAME (new FACT RULE 2026-05-30) | frame ESTABLISHED | RULES.md: all Icon BB seqs/graphs (flat-wired AND brokered) stackless with ONE per-sequence local frame indexed by ONE BB-frame register (distinct from `r10` broker / `r13` SM-state); slots `[reg+off]` (the `ζ` model). 22 absolute `&pBB/a0->(value|counter|state)` emissions (incl. GZ-2's 2) are LEGACY -> ratchet `scripts/test_gate_icn_one_reg_frame.sh` (baseline 22) to 0. NEXT (grounded 2026-05-30): mode-3 entry is `bb_build_flat(entry)` -> driver calls `fn(zeta,entry)` (scrip.c ~564: `(void)fn(NULL,0)`); the `bb_box_fn(void*zeta,int entry)` convention ALREADY carries a frame pointer in `zeta`/rdi (currently NULL). `g_flat_slot_count` (emit_bb.c:129) is a per-sequence slot counter reset in `bb_build_flat`/`bb_build_brokered` but UNUSED — the intended slot allocator. `bb_build_brokered` already emits `push rbp; mov rbp,rsp`. PLAN: (a) driver allocates a per-sequence frame and passes it as zeta instead of NULL (or slab allocates); (b) `bb_build_flat` emits a prologue loading the BB-frame register (r15, callee-saved, survives rt_* calls; distinct from r10/r13) from rdi, and a single epilogue all exits reach (preserve caller's r15 across the slab `ret`); (c) assign each box its slot offset via `g_flat_slot_count`; (d) migrate GZ-2 literal store + write read from `&pBB->value`/`&a0->value` to `[r15+off]`; gate m2==m3, one-reg-frame ratchet 22->20. OPEN: r15 push/pop across the slab's ret structure (verify single vs multi exit). |
| Frame plumbing | DONE (no-op verified) | BB-frame register = r15 (callee-saved, survives rt_* calls). XA_FLAT_PROLOGUE (Icon-gated `g_icn_frame_active`): `push r15; mov r15,rdi` (replaces `sub rsp,8` — same rsp adjust, alignment preserved); XA_FLAT_EPILOGUE: `pop r15` before each ret. Driver sets the flag around `bb_build_flat(main)` and passes `rt_icn_frame()` (static per-seq buffer) as zeta. SNOBOL4/Prolog byte-identical (flag off). Icon hello/42 m2==m3, run exit 0. |
| GZ-3 `write(1+2)` | NEXT | plus reads RO operands `[rip+disp]`, computes, stores RW result at `[r15+off]`; write reads `[r15+off]`. Should flip the `arith` smoke to m3 PASS (-> 3/6). |
| GZ-4 ... GZ-11+ | not started | Build on the one-register frame per the ladder. |
