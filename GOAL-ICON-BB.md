# GOAL-ICON-BB.md — Icon, 100% Byrd Boxes, from zero

**Reset:** 2026-05-28. Two and a half months of mode-2 `SM_BB_INVOKE`-per-statement watermark hunting is over. The previous content of this file (rungs accumulating PASS counts in the wrong shape) is wiped. Start over.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7 · Claude Sonnet 4.6
**Architecture pointers:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md` · `.github/test_icon.c` · `.github/jcon_irgen.icn`.

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

### IBB-1 — `procedure main() write("hello") end` runs mode 2

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

### IBB-3 — `write(1 + 2)` mode 2

- [ ] `BB_ICN_ILIT` template (mode-2 only at this rung). α pushes `DT_I(ival)` via γ. β → ω.
- [ ] `BB_ICN_BINOP_ADD` (or use existing `BB_BINOP` with op=ADD). α drives left.α; on left.γ captures value, drives right.α; on right.γ pushes sum via γ. β drives right.β; on right.ω, drives left.β then right.α; on left.ω → self.ω.
- [ ] `BB_ICN_CALL` for `write(int_expr)` — extend IBB-1's BB_CALL to accept a BB-typed integer arg.
- [ ] `lower_icn_bb.c` recognizes `TT_ADD` and integer literal cases.
- [ ] Gate: `SCRIP_ICN_BB=1 ./scrip --interp /tmp/add.icn` prints `3`.
- [ ] Gate: `--dump-sm` still prints `; SM_sequence_t  count=0`.

---

### IBB-4 — `every write(1 to 3)` mode 2

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

### IBB-6 — `every write(1 | 2 | 3)` mode 2 + mode 4

- [ ] `BB_ICN_ALT` template (mode 2 + mode 4). α=arm[0].α; arm[i].γ → self.γ; arm[i].ω → arm[i+1].α; arm[N-1].ω → self.ω; self.β → most-recently-yielded-arm.β with chain fallthrough.
- [ ] `lower_icn_bb.c` recognizes `TT_ALTERNATE`.
- [ ] Gate mode 2: `1\n2\n3\n`.
- [ ] Gate mode 4: `1\n2\n3\n`, byte-identical.

---

### IBB-7 — `every write(5 > ((1 to 2) * (3 to 4)))` mode 2 + mode 4

The full `test_icon.c` expression. Lon's hand-compiled reference from 2026-03-10.

- [ ] `BB_ICN_BINOP_MUL` (or use BB_BINOP/BB_BINOP_GEN with op=MUL).
- [ ] `BB_ICN_COMPARE_GT` (or use BB_BINOP/BB_BINOP_GEN with op=GT, is_relop=1).
- [ ] Cartesian-product β-chains: `mult.β → to2.β`; on `to2.ω → to1.β`; on `to1.ω → mult.ω`. Eight lines per binop per `test_icon.c`.
- [ ] Gate mode 2: `3\n4\n` (both satisfy 5 > x for x ∈ {1*3, 1*4, 2*3, 2*4} = {3, 4, 6, 8}).
- [ ] Gate mode 4: byte-identical to mode 2.
- [ ] Inspect mode-4 `.s` file — structurally close to `test_icon.c` pass 1.

**Flip default after IBB-7:** drop `SCRIP_ICN_BB` env-gate. `lower_icn_bb` becomes the default Icon lower path. Legacy `lower_icn_new_*` enters scheduled deletion.

---

### IBB-8 — Strings

- [ ] `BB_ICN_SLIT` template mode 2 + 4 (already exists for hello; formalize and clean up).
- [ ] Gate: `write("hello")` and `write("a", "b", "c")` both modes.

### IBB-9 — `to ... by ...`

- [ ] `BB_ICN_TO_BY` template mode 2 + 4.
- [ ] Gate: `every write(1 to 10 by 2)` → `1\n3\n5\n7\n9\n`.

### IBB-10 — Conjunction `&`

- [ ] `BB_ICN_CONJ` template mode 2 + 4.
- [ ] Gate: `every write((1 to 3) & 100)` → `100\n100\n100\n`.

### IBB-11 — If/then/else

- [ ] `BB_ICN_IF` template mode 2 + 4. cond.γ → then.α; cond.ω → else.α.
- [ ] Gate: `if 1 = 1 then write("y") else write("n")` → `y\n`.

### IBB-12 — While

- [ ] `BB_ICN_WHILE` template mode 2 + 4.
- [ ] Gate: count-to-3 program.

### IBB-13 — Until / Repeat

- [ ] `BB_ICN_UNTIL` + `BB_ICN_REPEAT` templates mode 2 + 4.

### IBB-14 — Assign

- [ ] `BB_ICN_ASSIGN` template mode 2 + 4.
- [ ] Gate: `x := 7; write(x)` → `7\n`.

### IBB-15 — Augmented assign

- [ ] `BB_ICN_AUGOP` template mode 2 + 4. Fixes the documented stack-underflow class from the wiped legacy.
- [ ] Gate: `every sum +:= (1 to 5); write(sum)` → `15\n`.

### IBB-16 — List literal

- [ ] `BB_ICN_LIST` template mode 2 + 4.
- [ ] Gate: `write(*[1,2,3])` → `3\n`.

### IBB-17 — Bang `!L`

- [ ] `BB_ICN_BANG` template mode 2 + 4. True generator: γ each element, β next index.
- [ ] Gate: `every write(!["a","b","c"])` → `a\nb\nc\n`.

### IBB-18 — Subscript `L[i]`

- [ ] `BB_ICN_IDX` template mode 2 + 4.
- [ ] Gate: `write(["x","y","z"][2])` → `y\n`.

### IBB-19 — Generator-in-subscript `L[1 to N]`

- [ ] Composition of IBB-17 + IBB-18 wiring; verify cross-product/β-chain behavior.
- [ ] Gate: `every write(["a","b","c"][1 to 3])` → `a\nb\nc\n`.

### IBB-20 — Section `L[i:j]`

- [ ] `BB_ICN_SECTION` template mode 2 + 4.

### IBB-21 — Limit `E \ N`

- [ ] `BB_ICN_LIMIT` template mode 2 + 4.

### IBB-22 — User procedure call

- [ ] `BB_ICN_USERCALL` template mode 2 + 4. Proc body BB; γ carries return value.
- [ ] Gate: `procedure f(x) return x+1 end; procedure main() write(f(5)) end` → `6\n`.

### IBB-23 — `suspend E`

- [ ] `BB_ICN_SUSPEND` template mode 2 + 4. Proc-as-generator: yield via γ, save resume state, β re-enters body.
- [ ] Gate: `procedure g() suspend 1; suspend 2 end; procedure main() every write(g()) end` → `1\n2\n`.

### IBB-24 — `return E`

- [ ] `BB_ICN_RETURN` template mode 2 + 4. One-shot version of suspend.

### IBB-25 — `fail`

- [ ] `BB_ICN_FAIL` template mode 2 + 4. Direct ω.

### IBB-26 — Tables

- [ ] `BB_ICN_TABLE_NEW`, `BB_ICN_TABLE_GET`, `BB_ICN_TABLE_SET`, `BB_ICN_TABLE_KEY` templates mode 2 + 4.

### IBB-27 — Sets

- [ ] `BB_ICN_SET_*` templates mode 2 + 4.

### IBB-28 — Records

- [ ] `BB_ICN_RECORD_*` templates mode 2 + 4.

### IBB-29 — Csets

- [ ] `BB_ICN_CSET` template mode 2 + 4.

### IBB-30 — String scanning `s ? expr`

- [ ] `BB_ICN_SCAN` template mode 2 + 4. Saves and sets `&subject` / `&pos`; β rewinds.

### IBB-31 — Scanning primitives

- [ ] `BB_ICN_TAB`, `BB_ICN_MOVE`, `BB_ICN_KEYWORD_POS`, `BB_ICN_KEYWORD_SUBJECT` templates mode 2 + 4.

### IBB-32 — Scanning generators

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
| IBB-1 ✅ | 1 (`hello`) | mode 2 only; one4all `9ccf95e1` |
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

- IBB-0 ✅ closed.
- IBB-1 ✅ closed — **ZERO SM SHAPE**. The driver in `scrip.c` (`mode_interp` branch) detects `is_icon && getenv("SCRIP_ICN_BB")`, looks up `main`'s `bb_idx` in `proc_table`, and calls `bb_exec_once(s2->sm.bb_table[main_bb_idx])` directly. `lower()` emits ZERO SM ops for Icon under SCRIP_ICN_BB (proc-skeleton suppressed in `lower_proc_skeletons`; top-level `has_icn` block skipped; terminal `SM_HALT` skipped). `--dump-sm` prints `; SM_sequence_t  count=0`.
- IBB-2 ✅ closed (decision: zero SM, driver-level bypass).
- IBB-3 ✅ closed: `write(1 + 2)` mode 2 prints `3`. Zero SM ops.
- IBB-4 ✅ closed: `every write(1 to 3)` mode 2 prints `1/2/3`. Zero SM ops.
- IBB-6 ✅ closed: `every write(1 | 2 | 3)` mode 2 prints `1/2/3`. Zero SM ops.
- IBB-7 ✅ closed: full `test_icon.c` expression `every write(5 > ((1 to 2) * (3 to 4)))` mode 2 prints `3/4`. Zero SM ops.
- IBB-9 ✅ closed: `every write(1 to 10 by 2)` mode 2 prints `1/3/5/7/9`. Zero SM ops.
- IBB-11 ✅ closed: `if 1 = 1 then write("y") else write("n")` mode 2 prints `y`. Zero SM ops.
- IBB-14 ✅ closed: `x := 7; write(x)` mode 2 prints `7`. Zero SM ops.
- IBB-15 ✅ closed: `sum := 0; every sum +:= (1 to 5); write(sum)` mode 2 prints `15`. Zero SM ops.

All of the above achieved with NO code change beyond the IBB-1 driver bypass + lower suppression. The existing `lower_icn_proc_body` already covered the Icon vocabulary; pulling the SM dispatch out of the way exposed the truth: SM was never doing useful work for Icon. The BB graph alone runs everything.

Gates: smoke_icon 5/5, smoke_prolog 5/5, broker 36/17, FACT 0, `--dump-sm` count=0 for every Icon program tested.

**NEXT: IBB-5** — mode-4 (native) for `every write(1 to 3)`. This needs real x86 BB templates per `ARCH-x86.md` — the first dual-mode rung. The remaining Icon rungs likely all pass mode 2 with no code change; a sweep over the corpus will tell what's left.
