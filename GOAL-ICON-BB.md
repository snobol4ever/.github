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

- [ ] **GZ-0 — Scaffold + gates.** Pin the no-stack gate above into `scripts/`. Confirm the
  per-box slot idiom (`&pBB->value`) is the value-storage primitive. Decide the slot/arena
  conventions by reading `emit_arbno` + one full pattern-node body in the archived `emit_x64.c`
  end-to-end, and `test_icon.c` for the Icon arithmetic shape. No code change beyond the gate script.
- [ ] **GZ-1 — `write("hello")`.** One box, literal value in its own slot, write reads the slot.
  No push. m2==m3, zero-SM, no-stack gate = 0 for this box family.
- [ ] **GZ-2 — `write(42)`.** Literal-N template (PDF §4.1): `lit.start: lit.value ← N; goto succeed`.
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

## Watermark

GROUND ZERO 3 — stackless rebuild. The IBB-* corpus numbers (the old 166-PASS line) are NOT a
baseline for this build; they were produced by the value-stack path now being removed.

| Step | State | Notes |
|------|-------|-------|
| Demolition (in progress) | Icon value-stack consumers being stubbed to abort at named sites | `g_vstack` and the SM stack machine stay LIVE for SNOBOL4. Icon-only `rt_*` consumers stubbed with `ICN_STACKLESS_ABORT` in `rt.c`. So far: `rt_pop_nv_set`, `rt_pop_store_i64`, `rt_push_stored_i64`, `rt_pop_store_descr`, `rt_case_eq`. Remaining: write trailers (`rt_pop_write_int_nl`, `rt_pop_write_any_nl`), `rt_unop_*`, the `rt_icn_*` family, and the Icon templates' own `rt_push_int`/`rt_vstack_pop` emissions (cut at the template level). Verified: SNOBOL4 `--interp`/`--run` unaffected; Icon `--interp` (oracle) unaffected; Icon `--run` aborts loudly at the first stubbed box (e.g. `x := 5` → `rt_pop_nv_set`). |
| GZ-0 … GZ-11+ | not started | Rebuild from `write("hello")` upward per the ladder above. |
