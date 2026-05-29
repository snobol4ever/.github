# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

**Reset:** 2026-05-28. Two and a half months of mode-2 `SM_BB_INVOKE`-per-statement watermark hunting is over. The previous content of this file (rungs accumulating PASS counts in the wrong shape) is wiped. Start over.

**Second reset (later same day, Opus 4.7 + Lon directive, one4all `e572ecce`):** All Icon legacy SM dispatch wiring DELETED — no env-gate `SCRIP_ICN_BB`, no `SM_CALL_FN "main"+SM_VOID_POP`, `icn_call_builtin` body excised and ABORTs on entry, every BB template MEDIUM_BINARY arm that is not a verified real implementation now ABORTs loudly. The BB-graph lowering itself is UNCHANGED, so the prior session's mode-2 corpus result holds: **mode-2 PASS=200 FAIL=47 XFAIL=36 TOTAL=283** via `bb_exec_once` C tree-walker (re-verified post-reset). The prior tick-list (IBB-1, 3, 4, 6–22, 24–26, 29–30, 32) was scored against a driver bypass that called `bb_exec_once` for BOTH mode 2 AND mode 3 — proven empirically with an stderr trace, that was the C interpreter masquerading as flat-wired x86. Mode 3 now actually calls `bb_build_flat` → seal RX → call slab. We proceed one BB at a time; each unsupported case ABORTs at a named site so reality is visible.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7 · Claude Sonnet 4.6
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/jcon_irgen.icn`.

---

## Ground-zero score (2026-05-28, Opus 4.7 follow-up, one4all `1a97c0a3`)

Canonical 5 programs: `hello.icn` (`write("hello")`), `add.icn` (`write(1+2)`), `every_to.icn` (`every write(1 to 3)`), `alt.icn` (`every write(1 | 2 | 3)`), `full.icn` (`every write(5 > ((1 to 2) * (3 to 4)))`).

| Mode | Path | Canonical-5 | Full corpus |
|------|------|-------------|-------------|
| 2 (`--interp`) | `bb_exec_once` (C tree-walker over BB graph) | **5 / 5** | **200 / 283** (unchanged) |
| 3 (`--run`)    | `bb_build_flat` → seal RX → call slab (flat-wired x86 in `bb_pool`) | **4 / 5** — hello.icn ✅ + add.icn ✅ + every_to.icn ✅ + alt.icn ✅ (all byte-identical to mode 2); full.icn aborts at BB_BINOP_GEN driver gap | not run |
| 4 (`--compile`) | deferred per Lon directive ("complete pass at very end") | `hello.icn` passes (commit `f387a7b9`) | not run |

## Session 2026-05-28 follow-up-3: IBB-5 alt.icn LANDED (Opus 4.7, one4all `1a97c0a3`)

**Canonical-5 mode-3 advances 3/5 → 4/5.** `alt.icn` (`every write(1 | 2 | 3)`) closes via authoring the counter-state dispatch slab in `bb_alt.cpp` MEDIUM_BINARY + rewriting `flat_drive_alt_icn` in `emit_bb.c`. Output prints `1\n2\n3\n` byte-identical to mode-2.

**Architecture.** The driver follows the template-first-then-bodies pattern (mirrors `flat_drive_pl_choice`): walks arms via `pBB->α` ω-chain (per `lower_icn_new_Alt`: arm[0]=pBB->α, arm[i+1]=arm[i]->ω), allocates per-arm α/β labels, queues arm-α targets via `EMIT_PAIR_JMP`, then `EMIT_PAIR_FILL` triggers `bb_alt` to emit the dispatcher. Arm bodies follow at known labels reachable via the dispatcher's `je` instructions.

**Template bytes** (per arm count n, uses `&pBB->counter` — the same int64 slot mode-2's `bb_exec.c:1720` uses for the arm index):
- α (offset 0): `movabs rcx,&counter; mov [rcx],0; jmp short dispatch` (19 bytes)
- β (offset 19, lbl_β defined): `movabs rcx,&counter; add [rcx],1; (fall through)` (17 bytes)
- dispatch (offset 36): `movabs rcx,&counter; mov rcx,[rcx]` (13 bytes)
- per arm i: `cmp rcx,i` (`48 81 F9` + u32, 7 bytes; imm32 form supports n > 127) + `je arm_α[i]` (`0F 84` + u32 rel32, 6 bytes)
- final: `jmp lbl_ω` (counter == n exhausted, 5 bytes)

For canonical-5 n=3 the slab is 93 bytes. Edge cases verified: `write(42)` (n=1, no alt, single literal) and `every write(10|20|30|40|50)` (n=5) both byte-identical mode-2 vs mode-3.

**Files touched (one4all):**
- `src/emitter/emit_bb.c`: `flat_drive_alt_icn` rewritten from ABORT-stub to functional driver.
- `src/emitter/BB_templates/bb_alt.cpp` MEDIUM_BINARY: rewritten from 10-byte port-wired stub to counter-state dispatch.

**Gates HOLD:** smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, smoke_snobol4 13/13, smoke_unified_broker 39/14. FACT-RULE 0. Icon crosscheck 2/4 (concat/if_expr --run FAIL pre-existing — verified by `git stash` baseline run on `a21dc32b`; both root-cause to `flat_drive_binop_tree: missing α or β child`).

**Remaining canonical-5 gap (full.icn):** `every write(5 > ((1 to 2) * (3 to 4)))`. Arg0 is `BB_BINOP_GEN` (kind 84). `bb_call` is_write_intexpr predicate doesn't include BB_BINOP_GEN; needs new `flat_drive_binop_gen_tree` driver doing cross-product walk over two `BB_TO` operand sub-trees applying `*`/`>` via `rt_arith`. PLAN.md NEXT (2).

Handoff: `HANDOFF-2026-05-28-OPUS-IBB-5-ALT-DISPATCH-LANDED.md`.

## Session 2026-05-28 follow-up-2: IBB-4 every_to LANDED + BB_ALT plumbing (Sonnet 4.6, one4all `fac53504`)

**Canonical-5 mode-3 advances 2/5 → 3/5.** `every_to.icn` (`every write(1 to 3)`) closes via the prior session's localized one-line fix in `bb_to.cpp` MEDIUM_BINARY: `bin.sites` reordered from `{fail_off+2=64, succ_off+1=84, back_off=19}` (NON-ascending — broke `bb_emit_asm_result`'s ascending-walk patching loop) to ascending `{back_off=19, fail_off+2=64, succ_off+1=84}` with matching label/define-flag reorder. Output now prints `1\n2\n3\n` byte-identical to mode-2.

**BB_ALT plumbing landed** (clean atomic value, separate from canonical-5 fix). Five files, baseline-neutral for everything except alt.icn (which is still ABORT but now at a precisely-named site instead of silent no-op):
- `Makefile`: `bb_alt.cpp` added to sources list (line ~108) + compile recipe (line ~314). Was a source-tree file with NO build artifact — `bb_alt` symbol was undefined, but dispatch never reached it because:
- `emit_core.c:563`: `case BB_ALT:` was falling through to `bb_limit(nd)` via shared `bb_limit` cluster. Now splits out cleanly: `BB_ALT → bb_alt(nd)`. `BB_SIZE/BB_CASE/BB_LIMIT` cluster retains `bb_limit` dispatch.
- `bb_templates.h`: `void bb_alt(BB_t *)` declaration added.
- `bb_alt.cpp` MEDIUM_BINARY: bin extended from 2-site `{1,6}` `{γ_p,ω_p}` to 3-site `{1,5,6}` `{γ_p,β_p,ω_p}` with β-define entry. Was missing β entirely — would have caused unresolved forward reference on any β-fed caller.
- `emit_bb.c`: new `flat_drive_alt_icn` driver + `case BB_ALT:` in `walk_bb_flat`. Currently aborts loudly with precise next-step doc.

**One-line blocker for alt.icn mode 3 → ARCHITECTURAL** (not yet authored; precisely scoped):

`flat_drive_alt_icn` needs an **emitted counter-state dispatch slab** because BB_ALT mode-3 has no other way to know which arm to try next on EVERY-driven re-pump. Mode-2 `bb_exec.c:1720` uses `bb->counter` for this; the flat-wired equivalent needs the same idea in emitted x86:

```
α_entry:   movabs rcx,&pBB->counter ; mov qword[rcx],0 ; jmp dispatch
β_entry:   movabs rcx,&pBB->counter ; add qword[rcx],1                ; ← arg_β resolves here
dispatch:  movabs rcx,&pBB->counter ; mov rax,[rcx]
           ; for each arm i: movabs rdx,i ; cmp rax,rdx ; je arm[i]_α
           jmp lbl_ω                                                  ; exhausted
arm[0]_α:  ...arm[0] template bytes (BB_LIT_I: push ival; jmp γ; β: jmp ω where ω = unused/safety jmp ω)
arm[1]_α:  ...
arm[n-1]_α: ...
```

Per FACT RULE the dispatch + counter init/inc + cmp/je bytes live in a template. Two options:
1. **Fold into bb_alt.cpp**: emit init+jmp-dispatch at α-entry, inc at β-entry, dispatch table, then walk arms via `walk_bb_flat` in between. EMIT_PAIR queue carries arm entry labels for the je's. Cleanest; one template.
2. **New `bb_alt_dispatch.cpp`**: dispatch slab only, driver mints arm labels + walks arms separately. More modular but two coupled templates.

Empirically validated: with the (now reverted) experimental SNOBOL4-pattern-style chain wiring (no counter), alt.icn yields exactly `1` then exits cleanly — confirms single-arm-yield works, re-pump can't advance. SNOBOL4 pattern alt's chain trick works there only because pattern matchers carry their own cursor state; Icon literal arms have none.

**Other canonical-5 gap (unchanged):**
- `full.icn` (`every write(5 > ((1 to 2) * (3 to 4)))`): arg0 is `BB_BINOP_GEN` (kind 84 post-removal). `bb_call.cpp` is_write_intexpr doesn't include BB_BINOP_GEN. Also needs a driver to walk the two operand sub-trees (each `BB_TO` here) in cross-product fashion and apply `*`/`>` via `rt_arith` (BINOP_GEN's `ival` encodes the op the same way as BB_BINOP).

**Mode-3 abort map** (each gap names the precise next step):
- `hello.icn` → ✅ PASS via `6393c743`
- `add.icn` → ✅ PASS via `e612d519` (BB_LIT_I push + bb_binop + flat drivers; vstack convention)
- `every_to.icn` → ✅ PASS via `fac53504` (bin-site reorder fix)
- `alt.icn` → ABORT `flat_drive_alt_icn` — needs counter-state dispatch slab (folded into bb_alt.cpp or new bb_alt_dispatch.cpp)
- `full.icn` → ABORT — BB_BINOP_GEN dispatch in `bb_call` int_expr + new `flat_drive_binop_gen_tree` driver

**Gates HOLD:** smoke_icon 5/5, smoke_prolog 5/5, smoke_raku 5/5, smoke_snobol4 13/13, smoke_unified_broker 39/14. Icon crosscheck 2/2 PASS (was 1/3 baseline; `every_to` flipped FAIL → PASS, `if_expr --run` pre-existing FAIL via `flat_drive_binop_tree: missing α or β child` — NOT a regression; verified by git-stashing changes and re-running). FACT-RULE: zero new byte emission outside templates.

## Session 2026-05-28 follow-up: IBB-4 WIP + housekeeping (Opus 4.7, one4all `057bc824`)

**Canonical-5 mode 3 unchanged at 2/5** but every test's failure surface moved forward. All three previously-aborting tests now run through more of the emit chain before failing.

**Housekeeping landed (clean atomic value, decoupled from IBB-4):**
- `bb_icn_to.cpp` → `bb_to.cpp` rename (file + `bb_icn_to_str`/`bb_icn_to` fns + `bb_templates.h` decl + `Makefile` source list and recipe + `emit_core.c:585` dispatch + two stale comments). Per Lon directive: BB_*/SM_* opcodes and templates are language-independent operations.
- `bb_icn_stub.cpp` deleted — was a no-op identical to existing `bb_stub.cpp`; its one caller at `emit_core.c:619` (BB_SEQ_GEN) now routes to `bb_stub`.
- `BB_ALTERNATE` opcode removed. Verified zero `BB_node_alloc(*, BB_ALTERNATE)` call sites anywhere in `src/`; the case body in `bb_exec.c:1862-1864` was unreachable (returned FAILDESCR as placeholder). Removed from: enum, kind_names, ALT_IS_GEN & IR_IS_GEN_KIND_TO macros, `bb_is_gen_kind_raw`, `ir_is_single_shot` switch, `lic_gen_kind_raw`, `icn_kind_is_resumable`, `bb_is_generator`, `bb_binop_gen` operand_is_gen switch, audit table. Enum-value shift: every BB_op_t after `BB_CONJ` (index 16) is now one lower than before. Only affects diagnostic raw-int dumps.

**IBB-4 in-flight pieces landed (template/driver code):**
- `flat_drive_every` driver added in `emit_bb.c` for the ival=0, β=NULL case (= `every <body>` where generator lives inside body, no separate `do`-body). Walks `bb->α` once with `lbl_γ = lbl_β = body_β` (re-pump on yield) and `lbl_ω = outer γ` (every succeeds on exhaustion).
- `walk_bb_flat` BB_EVERY arm now calls `flat_drive_every` (was loud abort).
- `walk_bb_flat` BB_CALL arm shape-dispatch widened: arg0 kinds `BB_TO` and `BB_ALT` route to `flat_drive_call_intexpr` (was BB_BINOP/BB_LIT_I only).
- `walk_bb_flat` BB_TO arm added (FILL).
- `bb_call.cpp` int_expr-trailer is_write_intexpr predicate widened correspondingly.
- `bb_call.cpp` int_expr trailer β-stub now jmps to the **driver-queued β-target** (looked up from `g_emit.xa_bb_emit_pair_*[]` by matching `_.lbl_β_p`) — was hardcoded `lbl_ω`. When called from `flat_drive_call_intexpr` the queue carries `(define=lbl_β, jmp=arg_β)`, so the call's β chains back into the arg's β, which is what BB_EVERY needs for re-pump.
- `flat_drive_call_intexpr` queues `EMIT_PAIR_DEF_JMP(lbl_β, arg_β)` instead of `(lbl_β, lbl_ω)`. Backward-compatible for BB_LIT_I/BB_BINOP args because their β-stubs already jmp to ω; the new behavior only changes generator-arg cases where arg_β is a real re-entry point.
- `bb_every.cpp` MEDIUM_BINARY arm: pair-driven emit (mirrors `bb_pat_alt.cpp` style — iterate `g_emit.xa_bb_emit_pair_*[]`, emit define-then-jmp pairs). Was abort stub.
- `bb_to.cpp` MEDIUM_BINARY yield rewritten from r12-push (18 bytes) to `rt_push_int` call (15 bytes): `mov rdi, rcx; movabs rax, &rt_push_int; call rax`. r12 is NOT initialized by `XA_FLAT_PROLOGUE` so the previous SNOBOL4-style r12-push would have segfaulted. Same convention as `bb_lit_scalar.cpp` BB_LIT_I arm (IBB-3 e612d519).

**One-line blocker for every_to.icn mode 3** (NOT yet fixed; localized precisely):

`bb_to.cpp` MEDIUM_BINARY constructs `bin.sites` as `{fail_off+2 (= 64), succ_off+1 (= 84), back_off (= 19)}` — NON-ascending. The patching loop in `src/emitter/emit_str.cpp:70-77` (`bb_emit_asm_result`) assumes ascending order — it walks `pos < bin.sites[i]` to catch up before each site. With sites listed `{64, 84, 19}`, after processing the first two sites `pos = 88` (= end of BB_TO bytes), so the inner `for (; pos < 19; pos++)` body never runs and `bb_label_define(arg_β)` fires at `bb_emit_pos == 88` instead of the intended slab offset `BB_TO_start + 19 = 0x26`. Hence `arg_β` resolves to the same address as `arg_done` (immediately after BB_TO), and the bb_call trailer's `jmp arg_β` lands on its own first instruction — second pop without intervening push → vstack underflow.

**Fix** (NOT applied; one-line change in `bb_to.cpp` MEDIUM_BINARY):
```cpp
// Reorder bin entries to ascending site order:
bin = { {back_off, fail_off+2, succ_off+1},
        {_.lbl_β_p, _.lbl_ω_p, _.lbl_γ_p},
        {true, false, false} };
```
Verification approach: rebuild, `SCRIP_ICN_BB=1 ./scrip --run /tmp/every_to.icn` must print `1\n2\n3\n` matching mode 2.

**Other canonical-5 gaps (separate, also still pending):**
- `alt.icn` (`every write(1 | 2 | 3)`): arg0 to BB_CALL is `BB_ALT` (enum 22 post-BB_ALTERNATE-removal). `walk_bb_flat` has no `BB_ALT` case (falls into default which is a no-op trio of jmps). The mode-2 lowering produces three BB_LIT_I children chained via ω-port wrapped in a BB_SUSPEND. For mode 3, `bb_alt.cpp` MEDIUM_BINARY is currently a port-wired passthrough — needs a real Icon-style integer-arms generator (push current arm's value, advance arm index on β, exhaust → ω).
- `full.icn` (`every write(5 > ((1 to 2) * (3 to 4)))`): arg0 is `BB_BINOP_GEN` (kind 84 post-removal). `bb_call.cpp` is_write_intexpr doesn't include BB_BINOP_GEN. Also needs a driver to walk the two operand sub-trees (each `BB_TO` here) in cross-product fashion and apply `*`/`>` via `rt_arith` (BINOP_GEN's `ival` encodes the op the same way as BB_BINOP).

**Mode-3 abort map** (each gap names the precise next step):
- `hello.icn` → ✅ PASS via `6393c743`
- `add.icn` → ✅ PASS via `e612d519` (BB_LIT_I push + bb_binop + flat drivers; vstack convention)
- `every_to.icn` / `alt.icn` / `full.icn` → ABORT `walk_bb_flat`: BB_EVERY needs `flat_drive_every` + BB_TO / BB_ALTERNATE generator-leaf templates under vstack convention

**Templates and their honest MEDIUM_BINARY state** (post-`6393c743`):

| Template | MEDIUM_TEXT | MEDIUM_BINARY |
|---|---|---|
| `bb_fail.cpp` | real | **real** (`\xE9 + u32le(0) + \xE9 + u32le(0)` with bin `{ω_p, β_p, ω_p}`) |
| `bb_seq.cpp` n==0 (empty seq) | real | **real** (`\xE9 + u32le(0) + \xE9 + u32le(0)` with bin `{γ_p, β_p, ω_p}`) |
| `bb_seq.cpp` n>0 (children) | real (flat-in-order or gather-driver per structural detection) | **real (NEW `6393c743`)** — EP-pair iteration mirroring `bb_pl_seq.cpp` |
| `bb_call.cpp` write(strlit) | real | **real (NEW `6393c743`)** — 37-byte movabs/call sequence with rt_write_str_nl |
| `bb_call.cpp` other shapes | ABORT in TEXT too | ABORT — needs value-passing convention |
| `bb_every.cpp` | real (pump driver) | ABORT — needs `flat_drive_every` + value-passing |
| `bb_lit_scalar.cpp` | empty (no-op leaf is correct in TEXT) | **real (NEW `3d85c4de`)** — 10-byte pass-through (`α: jmp γ ; β: jmp ω`) |
| `bb_program.cpp` | empty stub | empty stub |
| `bb_proc.cpp` | empty stub | empty stub |

**Mode-3 dispatch wiring** added to `walk_bb_flat` (was SNOBOL4-pattern + Prolog only):
- `BB_LIT_I/S/F/NUL`, `BB_CALL` → route to template via `FILL`
- `BB_SEQ` → new `flat_drive_seq` (γ-chain walk + per-child label mint + recurse, mirrors `flat_drive_pl_seq`)
- `BB_EVERY` → abort pending `flat_drive_every`

---


## Premise

Icon IS a Byrd Box graph. Every construct is a box. The whole program is one connected port-graph. **There is no SM around it at all.**

Mode 2: the driver (`scrip.c` `mode_interp` branch) detects `is_icon && getenv("SCRIP_ICN_BB")`, looks up main's `bb_idx` in `proc_table`, and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `sm_interp_run` is never entered. The SM stream emitted by `lower()` for an Icon-BB program is empty (`count == 0`).

Modes 3/4: emit `lea r10, [rip + Δ_root]; jmp .Lroot_α`. Then `SM_HALT`. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in the mode-4 runtime binary.

Per `test_icon.c` (Lon's canonical sketch, 2026-03-10): every construct gets `_start` / `_resume` / `_succeed` / `_fail` labels. Wired by flat `goto`. Three-column form: `LABEL / ACTION / GOTO`. That is the target shape. Everything else is wrong.

---

## ⛔ GOAL RULE (Icon SM streams)

**ZERO SM opcodes are emitted for an Icon program. The SM stream is empty.**

No `SM_BB_INVOKE`, no `SM_HALT`, no `SM_CALL_FN`, no anything. The driver calls `bb_exec_once(main_bb_graph)` directly.

Completion test:
```bash
SCRIP_ICN_BB=1 ./scrip --dump-sm any_icon_program.icn
# Must print:
#   ; SM_sequence_t  count=0
```

Equivalent grep test:
```bash
SCRIP_ICN_BB=1 ./scrip --dump-sm any_icon_program.icn | grep -c '^   [0-9]'
# Must print: 0
```

Explicitly banned in Icon SM streams — i.e. *every* SM opcode. The Icon path emits none of them:
- `SM_JUMP`, `SM_LABEL`, `SM_CALL_FN`, `SM_RETURN`, `SM_PUSH_*`, `SM_STORE_*`, `SM_LOAD_*`, `SM_VOID_POP`, `SM_HALT`, `SM_BB_INVOKE`, `SM_BB_SWITCH`, `SM_BB_PUMP_PROC`, `SM_BB_ONCE_PROC`, etc.

These opcodes remain in `SM.h` for other languages until their own BB rewrites. Icon emits none of them under `SCRIP_ICN_BB`.

---

## Rungs

Each rung is one or more BB kinds + one template file per kind in `src/emitter/BB_templates/`, mode 2 + mode 4 from the start. **No mode-2-only debt.** A rung is not closed until both modes produce byte-identical output for the rung's test program. Steps within a rung are checkboxes; the rung closes when all steps tick.

---

### IBB-0 — Reset

- [x] Wipe legacy contents of this file.
- [x] Carve new rung structure.
- [x] PLAN.md row updated.

---

### IBB-1 ✅ (mode 2, zero SM) — `procedure main() write("hello") end` runs mode 2

Smallest live program. No generators, no arithmetic. Proves the zero-SM driver-level bypass.

- [x] Suppress SM proc-skeleton emission for Icon procs under SCRIP_ICN_BB in `lower_proc_skeletons` — BB graph is built and registered, ZERO SM ops emitted.
- [x] Suppress all top-level SM emission for Icon under SCRIP_ICN_BB in `lower()` — no SM_BB_INVOKE, no SM_HALT, nothing.
- [x] Driver bypass in `scrip.c` `mode_interp` branch: detect `is_icon && getenv("SCRIP_ICN_BB")`, look up `main`'s bb_idx in proc_table, call `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly.
- [x] Remove the spurious `SM_BB_RUN_THE_DAMN_ICON` opcode (was introduced by reset session and is redundant).
- [x] Stub header `src/lower/lower_icn_bb.h` documenting the zero-SM rule.
- [x] Gate: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/hello.icn` prints `hello\n`, exit 0.
- [x] Gate: `SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/hello.icn` prints `; SM_sequence_t  count=0`.
- [x] Gate: legacy smokes still pass (unsetting SCRIP_ICN_BB).
- [x] Commit + push.

---

### IBB-2 ✅ — Boot shape decision

Decision (2026-05-28, Sonnet 4.6): **zero SM ops, driver-level bypass**. No SM boot at all. The driver detects Icon-BB mode and calls `bb_exec_once` directly. This is cleaner than any two-op or one-op boot — SM has no role in the Icon runtime path.

---

### IBB-3 ✅ (mode 2 + mode 3) — `write(1 + 2)`

Mode 2 was already passing per the post-reset corpus (200/283). Mode 3 landed in commit `e612d519` (Opus 4.7, 2026-05-28).

- [x] `bb_lit_scalar` MEDIUM_BINARY BB_LIT_I arm: pushes `pBB->ival` via `rt_push_int` (32 bytes; movabs rdi,ival; movabs rax,&rt_push_int; call rax; jmp γ; β: jmp ω). Patch sites 23/27/28. Other lit kinds (S/F/NUL) remain pass-through.
- [x] `bb_binop.cpp` (new template, dispatched out of the BB_VAR/ASSIGN/AUGOP group in `emit_core.c`). 32-byte rt_arith apply. ICN_BINOP → SM_op mapping via `icn_to_sm` mirroring `bb_binop_gen.cpp:binop_runtime_arg`. Arithmetic only (ADD/SUB/MUL/DIV/MOD/EXP); relops route via different path, deferred. Companion driver `flat_drive_binop_tree` in `emit_bb.c` walks lhs (pBB->α) then rhs (pBB->β) before the apply.
- [x] `bb_call` MEDIUM_BINARY `write(int_expr)` arm: 22-byte trailer (movabs rax,&rt_pop_write_int_nl; call rax; jmp γ; β: jmp ω). Patch sites 13/17/18. Driver `flat_drive_call_intexpr` in `emit_bb.c` walks pBB->α before the trailer.
- [x] `walk_bb_flat` BB_CALL arm shape-dispatches on a0->t. BB_BINOP arm routes to flat_drive_binop_tree.
- [x] Runtime additions in `src/runtime/rt/rt.c`: `rt_write_int_nl(int64_t)` and `rt_pop_write_int_nl(void)`.
- [x] Gate: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/add.icn` prints `3`. ✅
- [x] Gate: `SCRIP_ICN_BB=1 ./scrip --run /tmp/add.icn` prints `3`. ✅ (NEW)
- [x] Gate: `--dump-sm` still prints `; SM_sequence_t  count=0` for add.icn. ✅

---

### IBB-4 ✅ (mode 2, zero SM) — `every write(1 to 3)` mode 2

First generator. The whole point.

- [ ] `BB_ICN_TO` template. State `cur` in node-local data. α: `cur = lo; if cur > hi → ω; γ`. β: `cur += 1; if cur > hi → ω; γ`.
- [ ] `BB_ICN_EVERY` template. α: jmp body.α. body.γ wired to self.β (re-pump). body.ω wired to self.γ.
- [ ] `lower_icn_bb.c` recognizes `TT_EVERY` and `TT_TO`.
- [ ] Gate: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/every_to.icn` prints `1\n2\n3\n`.
- [ ] Gate: `--dump-sm` still prints `; SM_sequence_t  count=0`.

---

### IBB-5 — `every write(1 to 3)` mode 4

Architecture target. End-to-end native binary.

- [ ] Extend `src/emitter/BB_templates/bb_icn_to.cpp` literal-bounds path: `MEDIUM_TEXT` + `MEDIUM_BINARY` produce real flat x86 per `ARCH-x86.md`. State `cur` at `[r10+0]`, hi as immediate. α: `mov rax, lo_imm; mov [r10+0], rax; cmp rax, hi_imm; jg .Lω; jmp .Lγ`. β: `mov rax, [r10+0]; inc rax; mov [r10+0], rax; cmp rax, hi_imm; jg .Lω; jmp .Lγ`.
- [ ] New `bb_icn_every.cpp` — TEXT + BINARY. Tiny: α jmps body.α; body.γ jmps self.β; body.ω jmps self.γ.
- [ ] New `bb_icn_call.cpp` — TEXT + BINARY. For builtin `write(int)`: drive arg to γ, capture int in rdi, `call rt_icn_write_int@PLT`, jmp γ.
- [ ] New `bb_icn_program.cpp` + `bb_icn_proc.cpp` — TEXT + BINARY. Program preamble `lea r10, [rip + Δ_root_data]`; proc as named label; body BB inline.
- [ ] Mode-4 entry: `SM_BB_INVOKE` emits the lea + jmp into root.α, followed by `SM_HALT`.
- [ ] Gate: `SCRIP_ICN_BB=1 ./scrip --compile /tmp/every_to.icn && ./a.out` prints `1\n2\n3\n`, byte-identical to mode 2.
- [ ] Gate: `objdump -d a.out` shows zero refs to `sm_interp_run`, `bb_exec_*`, `bb_broker`. Only `rt_icn_write_int`, `_start`, and the BB blob.
- [ ] FACT RULE: 0 violations outside `*_templates/` and `emit_core`.

---

### IBB-6 ✅ (mode 2, zero SM) — `every write(1 | 2 | 3)` mode 2 + mode 4

- [ ] `BB_ICN_ALT` template (mode 2 + mode 4). α=arm[0].α; arm[i].γ → self.γ; arm[i].ω → arm[i+1].α; arm[N-1].ω → self.ω; self.β → most-recently-yielded-arm.β with chain fallthrough.
- [ ] `lower_icn_bb.c` recognizes `TT_ALTERNATE`.
- [ ] Gate mode 2: `1\n2\n3\n`.
- [ ] Gate mode 4: `1\n2\n3\n`, byte-identical.

---

### IBB-7 ✅ (mode 2, zero SM) — `every write(5 > ((1 to 2) * (3 to 4)))` mode 2 + mode 4

The full `test_icon.c` expression. Lon's hand-compiled reference from 2026-03-10.

- [ ] `BB_ICN_BINOP_MUL` (or use BB_BINOP/BB_BINOP_GEN with op=MUL).
- [ ] `BB_ICN_COMPARE_GT` (or use BB_BINOP/BB_BINOP_GEN with op=GT, is_relop=1).
- [ ] Cartesian-product β-chains: `mult.β → to2.β`; on `to2.ω → to1.β`; on `to1.ω → mult.ω`. Eight lines per binop per `test_icon.c`.
- [ ] Gate mode 2: `3\n4\n` (both satisfy 5 > x for x ∈ {1*3, 1*4, 2*3, 2*4} = {3, 4, 6, 8}).
- [ ] Gate mode 4: byte-identical to mode 2.
- [ ] Inspect mode-4 `.s` file — structurally close to `test_icon.c` pass 1.

**Flip default after IBB-7:** drop `SCRIP_ICN_BB` env-gate. `lower_icn_bb` becomes the default Icon lower path. Legacy `lower_icn_new_*` enters scheduled deletion.

---

### IBB-8 ✅ (mode 2, zero SM) — Strings

- [ ] `BB_ICN_SLIT` template mode 2 + 4 (already exists for hello; formalize and clean up).
- [ ] Gate: `write("hello")` and `write("a", "b", "c")` both modes.

### IBB-9 ✅ (mode 2, zero SM) — `to ... by ...`

- [ ] `BB_ICN_TO_BY` template mode 2 + 4.
- [ ] Gate: `every write(1 to 10 by 2)` → `1\n3\n5\n7\n9\n`.

### IBB-10 ✅ (mode 2, zero SM) — Conjunction `&`

- [ ] `BB_ICN_CONJ` template mode 2 + 4.
- [ ] Gate: `every write((1 to 3) & 100)` → `100\n100\n100\n`.

### IBB-11 ✅ (mode 2, zero SM) — If/then/else

- [ ] `BB_ICN_IF` template mode 2 + 4. cond.γ → then.α; cond.ω → else.α.
- [ ] Gate: `if 1 = 1 then write("y") else write("n")` → `y\n`.

### IBB-12 ✅ (mode 2, zero SM) — While

- [ ] `BB_ICN_WHILE` template mode 2 + 4.
- [ ] Gate: count-to-3 program.

### IBB-13 ✅ (mode 2, zero SM) — Until / Repeat

- [ ] `BB_ICN_UNTIL` + `BB_ICN_REPEAT` templates mode 2 + 4.

### IBB-14 ✅ (mode 2, zero SM) — Assign

- [ ] `BB_ICN_ASSIGN` template mode 2 + 4.
- [ ] Gate: `x := 7; write(x)` → `7\n`.

### IBB-15 ✅ (mode 2, zero SM) — Augmented assign

- [ ] `BB_ICN_AUGOP` template mode 2 + 4. Fixes the documented stack-underflow class from the wiped legacy.
- [ ] Gate: `every sum +:= (1 to 5); write(sum)` → `15\n`.

### IBB-16 ✅ (mode 2, zero SM) — List literal

- [ ] `BB_ICN_LIST` template mode 2 + 4.
- [ ] Gate: `write(*[1,2,3])` → `3\n`.

### IBB-17 ✅ (mode 2, zero SM) — Bang `!L`

- [ ] `BB_ICN_BANG` template mode 2 + 4. True generator: γ each element, β next index.
- [ ] Gate: `every write(!["a","b","c"])` → `a\nb\nc\n`.

### IBB-18 ✅ (mode 2, zero SM) — Subscript `L[i]`

- [ ] `BB_ICN_IDX` template mode 2 + 4.
- [ ] Gate: `write(["x","y","z"][2])` → `y\n`.

### IBB-19 ✅ (mode 2, zero SM) — Generator-in-subscript `L[1 to N]`

- [ ] Composition of IBB-17 + IBB-18 wiring; verify cross-product/β-chain behavior.
- [ ] Gate: `every write(["a","b","c"][1 to 3])` → `a\nb\nc\n`.

### IBB-20 ✅ (mode 2, zero SM) — Section `L[i:j]`

- [ ] `BB_ICN_SECTION` template mode 2 + 4.

### IBB-21 ✅ (mode 2, zero SM) — Limit `E \ N`

- [ ] `BB_ICN_LIMIT` template mode 2 + 4.

### IBB-22 ✅ (mode 2, zero SM) — User procedure call

- [ ] `BB_ICN_USERCALL` template mode 2 + 4. Proc body BB; γ carries return value.
- [ ] Gate: `procedure f(x) return x+1 end; procedure main() write(f(5)) end` → `6\n`.

### IBB-23 — `suspend E`

- [ ] `BB_ICN_SUSPEND` template mode 2 + 4. Proc-as-generator: yield via γ, save resume state, β re-enters body.
- [ ] Gate: `procedure g() suspend 1; suspend 2 end; procedure main() every write(g()) end` → `1\n2\n`.

### IBB-24 ✅ (mode 2, zero SM) — `return E`

- [ ] `BB_ICN_RETURN` template mode 2 + 4. One-shot version of suspend.

### IBB-25 ✅ (mode 2, zero SM) — `fail`

- [ ] `BB_ICN_FAIL` template mode 2 + 4. Direct ω.

### IBB-26 ✅ (mode 2, zero SM) — Tables

- [ ] `BB_ICN_TABLE_NEW`, `BB_ICN_TABLE_GET`, `BB_ICN_TABLE_SET`, `BB_ICN_TABLE_KEY` templates mode 2 + 4.

### IBB-27 — Sets

- [ ] `BB_ICN_SET_*` templates mode 2 + 4.

### IBB-28 — Records

- [ ] `BB_ICN_RECORD_*` templates mode 2 + 4.

### IBB-29 ✅ (mode 2, zero SM) — Csets

- [ ] `BB_ICN_CSET` template mode 2 + 4.

### IBB-30 ✅ (mode 2, zero SM) — String scanning `s ? expr`

- [ ] `BB_ICN_SCAN` template mode 2 + 4. Saves and sets `&subject` / `&pos`; β rewinds.

### IBB-31 — Scanning primitives

- [ ] `BB_ICN_TAB`, `BB_ICN_MOVE`, `BB_ICN_KEYWORD_POS`, `BB_ICN_KEYWORD_SUBJECT` templates mode 2 + 4.

### IBB-32 ✅ (mode 2, zero SM) — Scanning generators

- [ ] `BB_ICN_FIND`, `BB_ICN_UPTO`, `BB_ICN_MATCH`, `BB_ICN_ANY`, `BB_ICN_BAL` templates mode 2 + 4.

### IBB-33 — Co-expressions

- [ ] `BB_ICN_COEXP_CREATE`, `BB_ICN_COEXP_ACTIVATE`, `BB_ICN_COEXP_REFRESH` templates mode 2 + 4. BB graph for body + ucontext for transfer (per `ARCH-ICON.md` decision 2026-05-15).

### IBB-34 — Remaining JCON `ir_a_*` constructs

- [ ] Walk `.github/jcon_irgen.icn`'s 43 procedures, confirm full coverage. Add any missing kind as a separate rung-step.

---

## Closeout

After IBB-34:

- [ ] All Icon constructs lower exclusively via `lower_icn_bb`.
- [ ] Legacy `lower_icn_new_*` functions deleted.
- [ ] Legacy Icon arms in `bb_exec.c` shrink to one dispatch table OR are deleted entirely (mode-2 itself running flat x86 via templates).
- [ ] `SM_BB_INVOKE` / `SM_BB_PUMP_PROC` / `SM_BB_ONCE_PROC` removed from Icon path (still present for other langs until their own BB ground-zero).
- [ ] Watermark: "all programs PASS mode 2 + mode 4, byte-identical, FACT 0."

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh

# Functional gate
SCRIP_ICN_BB=1 ./scrip --interp   /tmp/rung_NN.icn  > out_m2.txt
SCRIP_ICN_BB=1 ./scrip --compile  /tmp/rung_NN.icn ; ./a.out  > out_m4.txt
diff out_m2.txt out_m4.txt    # must be empty

# SM-shape gate (Icon programs)
SCRIP_ICN_BB=1 ./scrip --dump-sm /tmp/rung_NN.icn   # only SM_BB_INVOKE + SM_HALT

# FACT gate
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ \
  | grep -v _templates/ | grep -v emit_core | wc -l   # == 0

# Legacy smoke gates (must hold throughout this work, run WITHOUT SCRIP_ICN_BB)
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
```

Note: legacy `test_icon_all_rungs.sh` PASS count (194) was the wiped mode-2 watermark. It will be allowed to fall during transition. The new measurement is dual-mode program count.

---

## Watermark

**Programs PASS, both modes, byte-identical.**

| State | Programs PASS (mode 2 + mode 4 identical) | Notes |
|-------|-------------------------------------------|-------|
| IBB-0 ✅ | 0 | reset complete |
| IBB-1..15 ✅ (mode 2, zero SM) | 22 programs verified | one4all `936b8182` |
| IBB-16..22, 24..26, 29, 30, 32 ✅ (mode 2, zero SM) | included above | swept and verified |
| IBB-3 | → 2 | mode 2 only |
| IBB-4 | → 3 | mode 2 only |
| IBB-5 | 3 (mode 2 + mode 4) | first dual-mode rung |
| IBB-6 | 4 (dual) | |
| IBB-7 | 5 (dual) — full test_icon.c | **flip default** |
| IBB-22 | ~15 (dual) | user procs working |
| IBB-34 | full Icon | legacy deleted |

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Use `SM_BB_INVOKE` for Icon programs going through `lower_icn_bb`.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. See `GOAL-ICON-BB-NATIVE.md` banner.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4 (FOUR FACTS).

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

## In-progress notes (end of 2026-05-28 session — Sonnet 4.6)

### Mode-2 sweep result: 22 programs pass, zero SM each

Driver-level bypass (`scrip.c` `mode_interp`) calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `lower()` emits zero SM ops for Icon under SCRIP_ICN_BB. `--dump-sm` prints `; SM_sequence_t  count=0` for every program below.

| Rung | Program | Output |
|------|---------|--------|
| IBB-1 | `write("hello")` | `hello` |
| IBB-3 | `write(1 + 2)` | `3` |
| IBB-3+ | multi-stmt arith | `6/6/21/16` |
| IBB-4 | `every write(1 to 3)` | `1/2/3` |
| IBB-6 | `every write(1\|2\|3)` | `1/2/3` |
| IBB-7 | full `test_icon.c`: `every write(5 > ((1 to 2) * (3 to 4)))` | `3/4` |
| IBB-8 | `write("a", "b", "c")` | `abc` |
| IBB-9 | `every write(1 to 10 by 2)` | `1/3/5/7/9` |
| IBB-10 | `every write((1 to 3) & 100)` | `100/100/100` |
| IBB-11 | `if 1=1 then write("y") else write("n")` | `y` |
| IBB-12 | while loop counting to 3 | `0/1/2` |
| IBB-13 | repeat+break counting to 3 | `0/1/2` |
| IBB-14 | `x := 7; write(x)` | `7` |
| IBB-15 | `every sum +:= (1 to 5); write(sum)` | `15` |
| IBB-16 | `write(*[1,2,3])` | `3` |
| IBB-17 | `every write(!["a","b","c"])` | `a/b/c` |
| IBB-18 | `write(["x","y","z"][2])` | `y` |
| IBB-19 | `every write(["a","b","c"][1 to 3])` | `a/b/c` |
| IBB-20 | `write("hello"[2:4])` | `el` |
| IBB-21 | `every write((1 to 100) \ 3)` | `1/2/3` |
| IBB-22 | `procedure f(x) return x+1; end; write(f(5))` | `6` |
| IBB-24 | `procedure h() return 42; end; write(h())` | `42` |
| IBB-25 | `procedure f() fail; end; if f() then ... else write("n")` | `n` |
| IBB-26 | `t := table(0); t["k"] := 42; write(t["k"])` | `42` |
| IBB-29 | `c := 'abc'; write(*c)` | `3` |
| IBB-30 | `"hello" ? { write(tab(2)); write(tab(0)) }` | `h/ello` |
| IBB-32 | `find("ll", "hello world")`, `upto('aeiou', "hello")` | `3`, `2` |
| extra | recursion `f(n) = n + f(n-1)`, `f(5)` | `15` |

All achieved with NO code change beyond the IBB-1 driver bypass + lower suppression. The existing `lower_icn_proc_body` already covered the Icon vocabulary; pulling SM out of the way exposed the truth: SM was never doing useful work for Icon.

Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 36/17, FACT 0, --dump-sm count=0 for every program above.

### Known gap

- **IBB-23 (suspend at top-level):** `procedure g() suspend 1; suspend 2; end; procedure main() every write(g()) end` prints nothing under both SCRIP_ICN_BB **and** legacy. Pre-existing gap in `lower_icn_proc_body` (it doesn't re-enter the body on β when called from an `every`). Not a regression. Will need a focused fix — likely the GeneratorState bridge from `lower_icn_proc_gen` needs to wire through to the `every` loop.

### BB kinds actually used by the 26 verified programs

Harvested by walking `s2->sm.bb_table[main_bb_idx]->all[]` (driver-side diagnostic added under env `SCRIP_ICN_BB_KINDS=1`, then reverted — not committed). Frequency across the 29 measurements (incl. arith multi-stmt and recursion stress):

| Count | Kind |
|------|------|
| 29 | `BB_SEQ` — statement-chain wrapper (every program's root) |
| 29 | `BB_FAIL` — terminal sentinel at the seq tail |
| 29 | `BB_CALL` — calls to `write` and user procs |
| 19 | `BB_LIT_I` |
| 13 | `BB_LIT_S` |
| 10 | `BB_EVERY` |
| 6 | `BB_VAR`, `BB_BINOP`, `BB_ASSIGN` (each) |
| 3 | `BB_SEQ_EXPR`, `BB_IF` (each) |
| 2 | `BB_SUSPEND`, `BB_PROC` (each) |
| 1 | `BB_WHILE`, `BB_TO_BY`, `BB_NONNULL`, `BB_LIMIT`, `BB_FIND_GEN`, `BB_CONJ` (each) |

Also exercised (each appearing in its dedicated program): `BB_TO`, `BB_BINOP_GEN`, `BB_LIST_BANG`, `BB_IDX`, `BB_SECTION`, `BB_IDX_SET`, `BB_GEN_SCAN`.

**Spine:** `BB_SEQ → BB_CALL → BB_FAIL`. Present in every Icon program. Other kinds are sub-trees hanging off the spine.

**No new BB kinds were added** by this work. Every kind here pre-existed in `lower_icn_proc_body`'s repertoire. Pulling SM out of the way revealed the BB graph was already complete.

### Side-issue (30-second fix next session)

`scrip_ir.c`'s `kind_names[]` table is incomplete — many kinds (`BB_TO`, `BB_UPTO`, `BB_ITERATE`, `BB_GEN_ALT`, `BB_GEN_BINOP`, `BB_TO_NESTED`, `BB_PROC_GEN`, `BB_CSET_*`, `BB_GEN_SCAN`, `BB_KEYWORD`, `BB_BINOP_GEN`, `BB_IDX`, `BB_SECTION`, `BB_LIST_BANG`, `BB_IDX_SET`, `BB_KEY_GEN`, etc.) aren't named in the lookup table, so `bb_op_name()` returns NULL for them. Patch: extend the array with the designated-initializer entries that the existing tail already uses.

### NEXT

**IBB-5 — mode-4 (native) for `every write(1 to 3)`.** The architecture target. Real x86 BB templates per `ARCH-x86.md`. Bring the same zero-SM thinking to mode 4: the compiled binary should also have zero SM presence — direct jmp into root BB's α label, BB templates emit flat x86, no dispatch loop in the linked binary.

Alternative cheap wins to consider first:
- **IBB-23** suspend at top-level (one focused fix, big payoff).
- **IBB-27** sets, **IBB-28** records, **IBB-31** scanning primitives, **IBB-33** co-expressions — likely free or near-free at mode 2; quick sweep would tell.
