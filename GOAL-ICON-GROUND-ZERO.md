# GOAL-ICON-GROUND-ZERO.md — Icon, 100% Byrd Boxes, from zero

**Carved:** 2026-05-28
**Author:** Claude Opus 4.7 under direction from Lon
**Supersedes for new work:** `GOAL-ICON-BB.md` (watermark frozen as legacy reference).

---

## Premise

`ARCH-ICON.md` says it. `GOAL-ICON-BB-NATIVE.md` says it. `ARCH-x86.md` says it. `test_icon.c` shows it. Lon has said it across at least nine sessions since 2026-03-10:

**Icon IS a Byrd Box graph. Every construct is a box. The whole program is a connected port-graph. The SM around it is the thinnest possible boot — two or three instructions total, for the whole program, not per statement.**

The convalescent shape that took over the codebase (`SM_BB_INVOKE` per statement, every-loop scaffolding in `lower.c`, `bb_exec_*` C walker, `SM_CALL_FN "main"` epilogue) is not the target. It is the abandoned wrong turn that `GOAL-ICON-BB-NATIVE.md` already called *"one month lost."* Two and a half months on, it is two and a half months lost. Start over.

---

## The SM boot — final form

Two SM opcodes per Icon program. Total. For the whole program.

```
SM_BB_RUN_THE_DAMN_ICON   a[0].ptr = root BB_graph_t*   ; jump into root.α; runs until root.γ or root.ω
SM_HALT
```

Mode 2: handler in `sm_interp.c` calls `bb_exec_node(root, ENTRY_α)` exactly once, no surrounding loop, no every-scaffold, no pump, no switch. Returns when the graph reaches its own root γ or ω. Done.

Mode 3/4: emits `lea r10, [rip + Δ_root_data]; jmp .Lroot_α` and that's it. Then `SM_HALT`. The graph IS the program. Boxes are CODE+DATA in `bb_pool` (mode 3) or in the linked binary's `.text`/`.data` (mode 4). Inter-box transitions are `jmp rel32`. No `call`, no `ret`, no SM dispatch loop, no broker, no C walker in the runtime binary.

Whether to fold to a single opcode `SM_BB_RUN_THE_DAMN_ICON_AND_HALT` is GZ-2's decision. Default plan is two ops for symmetry with HALT semantics elsewhere.

---

## Banned in Icon SM streams (post-GZ-N)

- `SM_BB_INVOKE` — per-statement BB invocation. Wrong granularity.
- `SM_BB_SWITCH` — per-statement BB switch. Wrong granularity.
- `SM_BB_PUMP_PROC`, `SM_BB_ONCE_PROC` — proc-level pump wrappers.
- `SM_CALL_FN "main"` + `SM_VOID_POP` boot. `main` is a BB. There is no SM call.
- The every-loop scanner in `lower.c` that looks for `SM_BB_INVOKE` to wire a `SM_JUMP_F`/back-edge harness around. Every-loops are BB edges (`body.γ → self.β`, `body.ω → self.γ`), not SM control flow.
- `SM_PUSH_NULL` + `SM_VOID_POP` + `SM_RETURN` proc epilogue. Procedures are BBs.

These opcodes remain in `sm.h` for other languages (SNOBOL4 patterns, Prolog choice frames, Raku) until those languages' own ground-zero rewrites. Icon does not use them.

---

## Rungs

Each rung is one BB kind, one template file in `src/emitter/BB_templates/`, mode 2 + mode 4 from the start. **No mode-2-only debt.** A rung is not done until both modes produce byte-identical output for that rung's test program.

### GZ-0 — Carve

- This file written.
- `PLAN.md` row "ICON-BB" replaced by "ICON-GROUND-ZERO" with step GZ-1.
- `GOAL-ICON-BB.md` marked superseded (watermark preserved as legacy reference).

### GZ-1 — `procedure main() write("hello") end` runs mode 2

The smallest live program. No generators, no arithmetic. Proves the new boot.

1. Add `SM_BB_RUN_THE_DAMN_ICON` to the SM enum in `src/include/sm*.h`.
2. Mode-2 handler in `sm_interp.c`: pop root pointer, call `bb_exec_node(root, ENTRY_α)`, halt.
3. Add BB kinds: `BB_ICN_PROGRAM`, `BB_ICN_PROC`, `BB_ICN_CALL`, `BB_ICN_SLIT`.
4. Mode-2 executors in `bb_exec.c` for those four kinds. Each is α/β only; γ/ω are wires, not handlers.
5. New file `src/lower/lower_icn_gz.c` with `lower_icn_ground_zero(STMT_t *program) -> BB_graph_t*`. Walks the whole Icon AST, returns one root `BB_graph_t`.
6. Lower epilogue (Icon path only): emit `SM_BB_RUN_THE_DAMN_ICON root; SM_HALT`. Two SM ops. Verifiable via `--dump-sm`.
7. `lower_icn_gz.c` is the ONLY caller from `lower.c` for `g_lang == LANG_ICN`. The legacy lower_icn paths stay compiled but unreached for Icon programs that go through ground-zero.

**Gate GZ-1:**
- `./scrip --interp /tmp/hello.icn` prints `hello\n` and exits 0.
- `./scrip --dump-sm /tmp/hello.icn` shows exactly two opcodes: `SM_BB_RUN_THE_DAMN_ICON`, `SM_HALT`.
- Legacy tests (smokes, broker, all rungs at current watermark) still pass — because we have NOT yet rerouted them to ground-zero. Ground-zero is opt-in via a new flag or simply by being the new path for programs Lon writes against this goal.

**Decision at GZ-1 close:** when does ground-zero become default? Plan: after GZ-7 (the full `test_icon.c` expression works mode 2 + mode 4), flip the default and start deleting legacy.

### GZ-2 — Boot shape decision

After GZ-1 runs, decide: keep two ops or fold to one. Lock in. One paragraph here.

### GZ-3 — `write(1 + 2)` mode 2

1. `BB_ICN_ILIT` — α pushes `DT_I(ival)` via γ, β goes ω.
2. `BB_ICN_BINOP_ADD` — α drives left.α; on left.γ captures value, drives right.α; on right.γ pushes sum via γ. β drives right.β. On right.ω drives left.β then right.α. On left.ω → self.ω.
3. `BB_ICN_CALL` already from GZ-1; extend to take a BB-typed arg (not just SLIT).

**Gate GZ-3:** `write(1 + 2)` prints `3`. Mode 2.

### GZ-4 — `every write(1 to 3)` mode 2

The whole point. The first generator.

1. `BB_ICN_TO` — α: `cur = lo; if cur > hi → ω; γ`. β: `cur += 1; if cur > hi → ω; γ`. State (cur) lives in node-local data.
2. `BB_ICN_EVERY` — the test_icon.c shape:
   - α: jmp body.α
   - body.γ wired to self.β (re-pump the body — its β will yield the next value or ω out)
   - body.ω wired to self.γ (every always succeeds when its generator exhausts)
   - self.β unused (every yields nothing then ω, but the structure is body.ω → self.γ then γ→consumer)
   - Actually: every is a statement-level wrapper that doesn't yield values up — it drives a generator to exhaustion and succeeds. Simplification: self.γ is reached when body exhausts. Eight lines.

**Gate GZ-4:** `every write(1 to 3)` prints `1\n2\n3\n`. Mode 2.

### GZ-5 — `every write(1 to 3)` mode 4

The architecture target. End-to-end native binary.

1. Extend `bb_icn_to.cpp` literal-bounds path: `MEDIUM_TEXT` + `MEDIUM_BINARY` produce real flat x86 per `ARCH-x86.md`. State `cur` at `[r10+0]`, hi as immediate (literal fast-path). α: `mov rax, lo_imm; mov [r10+0], rax; cmp rax, hi_imm; jg .Lω; jmp .Lγ`. β: `mov rax, [r10+0]; inc rax; mov [r10+0], rax; cmp rax, hi_imm; jg .Lω; jmp .Lγ`.
2. New `bb_icn_every.cpp` — TEXT + BINARY. α jmps body.α; body.γ jmps self.β; body.ω jmps self.γ. Tiny.
3. New `bb_icn_call.cpp` — TEXT + BINARY. For builtin `write(int)`: drive arg to γ, capture int in rdi, `call rt_icn_write_int@PLT`, jmp γ. β jmps ω.
4. New `bb_icn_program.cpp` + `bb_icn_proc.cpp` — TEXT + BINARY. Program: preamble `lea r10, [rip + Δ_root_data]`, then jmp into first proc.α. Proc: named label, body BB inline.
5. `./scrip --compile /tmp/every.icn` → `.s` → `as` + `ld` → `./a.out` → `1\n2\n3\n`.

**Gate GZ-5:**
- Mode-4 binary produces `1\n2\n3\n`, byte-identical to mode-2.
- The `.s` file contains flat x86 with `_α`/`_β`/`_γ`/`_ω` labels per the three-column convention.
- `objdump -d a.out` shows zero references to `sm_interp_run`, `bb_exec_*`, `bb_broker`. The runtime binary has no SM machinery and no C walker. It has `rt_icn_write_int` (runtime support function for the write builtin) and `_start` and the BB blob. Nothing else.
- FACT RULE: 0 violations outside templates.

### GZ-6 — `every write(1 | 2 | 3)` mode 2 + mode 4

`BB_ICN_ALT` — α=arm[0].α; arm[i].γ → self.γ; arm[i].ω → arm[i+1].α; arm[N-1].ω → self.ω; self.β → most-recently-yielded-arm.β with chain fallthrough.

**Gate GZ-6:** mode 2 + mode 4 both produce `1\n2\n3\n` for `every write(1|2|3)`.

### GZ-7 — The full test_icon.c expression

`every write(5 > ((1 to 2) * (3 to 4)))` mode 2 + mode 4.

Adds: `BB_ICN_BINOP_MUL`, `BB_ICN_COMPARE_GT`. Cartesian-product behavior falls out — each binop drives its operands as generators; β-chains propagate through the multiply, comparison, and write. The eight lines per binop from `test_icon.c`'s pass 1.

**Gate GZ-7:** mode 4 emits a `.s` file structurally close to `test_icon.c` pass 1. Output `4\n` (both 1*3=3 and 1*4=4 satisfy 5>x, so really `3\n4\n` — verify with mode 2 first, then mode 4 matches byte-identical).

After GZ-7: **flip the default**. New programs go through `lower_icn_gz`. Legacy `lower_icn_new_*` functions enter scheduled deletion.

### GZ-8..GZ-34 — Full Icon coverage

See the rung table in the next session. In rough dependency order:

| Rung | Construct | BB kind |
|------|-----------|---------|
| GZ-8 | Strings (`write("x")`) | `BB_ICN_SLIT` (extend from GZ-1) |
| GZ-9 | `to ... by ...` | `BB_ICN_TO_BY` |
| GZ-10 | Conjunction `&` | `BB_ICN_CONJ` |
| GZ-11 | If/then/else | `BB_ICN_IF` |
| GZ-12 | While | `BB_ICN_WHILE` |
| GZ-13 | Until / repeat | `BB_ICN_UNTIL` / `BB_ICN_REPEAT` |
| GZ-14 | Assign `x := E` | `BB_ICN_ASSIGN` |
| GZ-15 | Augmented assign `x op:= E` | `BB_ICN_AUGOP` (fixes a documented stack-underflow class) |
| GZ-16 | List literal `[1,2,3]` | `BB_ICN_LIST` |
| GZ-17 | Bang `!L` | `BB_ICN_BANG` |
| GZ-18 | Subscript `L[i]` | `BB_ICN_IDX` |
| GZ-19 | Subscript with generator `L[1 to N]` | uses GZ-17 + GZ-18 wiring |
| GZ-20 | Section `L[i:j]` | `BB_ICN_SECTION` |
| GZ-21 | Limit `E \ N` | `BB_ICN_LIMIT` |
| GZ-22 | User procedure call | `BB_ICN_USERCALL` |
| GZ-23 | `suspend E` | `BB_ICN_SUSPEND` |
| GZ-24 | `return E` | `BB_ICN_RETURN` |
| GZ-25 | `fail` | `BB_ICN_FAIL` |
| GZ-26 | Tables | `BB_ICN_TABLE_*` |
| GZ-27 | Sets | `BB_ICN_SET_*` |
| GZ-28 | Records | `BB_ICN_RECORD_*` |
| GZ-29 | Csets | `BB_ICN_CSET` |
| GZ-30 | Scanning `s ? expr` | `BB_ICN_SCAN` |
| GZ-31 | `tab`, `move`, `&pos`, `&subject` | scanning builtins |
| GZ-32 | `find`, `upto`, `match`, `any`, `bal` | scanning generators |
| GZ-33 | Coexpression `create E`, `@C`, `^C` | BB graph + ucontext for transfer |
| GZ-34 | Remaining JCON `ir_a_*` constructs | full coverage |

By GZ-22 Icon's primary path is BBs and mode-4 native works. At GZ-34, legacy `SM_BB_INVOKE` / `SM_BB_PUMP_PROC` / `SM_BB_ONCE_PROC` paths are deleted from the codebase.

---

## Per-rung gate

```bash
bash scripts/build_scrip.sh
./scrip --interp   /tmp/rung_NN.icn   > out_m2.txt
./scrip --compile  /tmp/rung_NN.icn ; ./a.out  > out_m4.txt
diff out_m2.txt out_m4.txt    # must be empty
./scrip --dump-sm  /tmp/rung_NN.icn   # for Icon programs: only SM_BB_RUN_THE_DAMN_ICON + SM_HALT (post-GZ-7 default)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob|bake_blob_call' src/ | grep -v _templates/ | grep -v emit_core | wc -l   # ==0
```

---

## Watermark

Not "rungs PASS." **Programs PASS, both modes.** Mode 2 and mode 4 byte-identical output, no SM scaffolding around the BB graph, FACT 0.

| State | Programs PASS (mode 2 + mode 4 identical) |
|-------|-------------------------------------------|
| Start | 0 |
| After GZ-1 | 1 (`hello`) mode 2 only |
| After GZ-4 | 2 mode 2 only |
| After GZ-5 | 2 (mode 2 + mode 4) |
| After GZ-7 | 3 (mode 2 + mode 4) |
| Default flip after GZ-7 | legacy lower_icn enters deprecation |

---

## DO NOT

- Touch SNOBOL4 / Snocone / Rebus / Raku / Prolog lower or BB families.
- Extend the legacy `GOAL-ICON-BB.md` watermark. That goal is frozen.
- Use `SM_BB_INVOKE` for Icon programs going through ground-zero.
- Write `DESCR_t foo(void *zeta, int entry)` C Byrd box functions. Ever. See `GOAL-ICON-BB-NATIVE.md` banner.
- Add fields to `BB_t`.
- Walk SM or BB at runtime in modes 3/4 (FOUR FACTS).

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
# legacy gates — must still pass throughout ground-zero work
bash scripts/test_smoke_icon.sh                # PASS=5
bash scripts/test_smoke_prolog.sh              # PASS=5
bash scripts/test_smoke_unified_broker.sh      # PASS>=35
bash scripts/test_icon_all_rungs.sh            # PASS=194 (legacy mode-2 watermark — DO NOT extend)
```

Per-rung commands are in each rung's section above.

---

## Architecture pointers

- `ARCH-ICON.md` — *"Icon IS a Byrd Box graph. Every construct is a box."*
- `ARCH-x86.md` — flat-BB ABI, three-column emission, EMIT_BINARY_WIRED, `r10` data pointer.
- `GOAL-ICON-BB-NATIVE.md` — *"ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — ALL Byrd boxes are x86 ASSEMBLY emitted at runtime."*
- `.github/test_icon.c` — the canonical three-column α/β/γ/ω form for `every write(5 > ((1 to 2) * (3 to 4)))`. Lon's hand-written reference.
- `.github/jcon_irgen.icn` — 43 `ir_a_*` procedures, one per Icon AST construct. The canonical BB enumeration.

---

## Why this goal exists

Read the conversation around 2026-05-28. Then commit.
