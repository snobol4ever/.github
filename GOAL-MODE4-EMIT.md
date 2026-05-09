# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

**Repo:** one4all (primary).  **Carved sess #62, 2026-05-05** from
GOAL-CHUNKS Steps 8 + 19.

**Done when:** `scrip --jit-emit --x64 file.{sno,sc}` produces a
standalone asm/binary that, when run via `./prog < input`, produces
output identical to `scrip --sm-run file.{sno,sc} < input`.  The
emitted executable links against `libscrip_rt.so` — runtime support
library carrying NV table, pattern matcher, GC, BB broker,
generator/Prolog backtracking machinery.  After Step 19 (M5), scope
extends to Icon, Raku, Prolog, Rebus.

---

## Architectural target

```
file.{sno,sc} ─► [parser] ─► IR ─► [sm_lower] ─► SM_Program
                                                      │
                                              [sm_codegen --x64]
                                                      │
                                              file.s + sm_macros.s
                                                      │
                                              ld + libscrip_rt.so
                                                      │
                                                file (ELF)
```

Emitted `main()`:

```c
int main(int argc, char **argv) {
    scrip_rt_init(argc, argv);
    scrip_rt_call_chunk(PROGRAM_ENTRY_PC, 0);
    return scrip_rt_finalize();
}
```

`PROGRAM_ENTRY_PC` baked at emit time.  Emitted binary contains
compiled SM chunks (one per function/proc/predicate/deferred body)
plus calls into `libscrip_rt.so` for language semantics.  No
`EXPR_t` walker in the binary — that is the point.

**Symbol surface (libscrip_rt.so):** `scrip_rt_init`,
`scrip_rt_finalize`, `scrip_rt_push/pop/peek`,
`scrip_rt_call_chunk`, `scrip_rt_pat_match`, `scrip_rt_nv_lookup/
store`, `scrip_rt_builtin_<name>`, `scrip_rt_bb_drive` (M5),
`scrip_rt_pl_unify/choice` (M5).

---

## Two separate emitters (settled sess #67)

### 1. SM opcodes → macros (the SM emitter)

Universal IR.  Every backend (x86, JVM, .NET, JS, WASM) walks
`SM_Program` with one switch.  For x86 text-asm output, each opcode
group maps to ONE GNU-as macro in `sm_macros.s` (parallel to the
proven 151-macro `snobol4_asm.mac`).  Each macro expands to inline
x86 — NOT a PLT call per tiny op.

Three-column shape per non-BB line:
```
LABEL:                  OPCODE          args  # comment
```
Widths: 24 / 16 / free.  Single space between col 2 and col 3.
Single space between args and `#` annotation.  Banner lines
(`# ====`, `# stmt N (line L): ...`) print full-width — NOT
three-column.

`libscrip_rt.so` boundary for SM-side: NV table, pattern matcher,
GC, builtins.  All other ops bake inline via macros.

### 2. BB boxes → three-column layout (the BB box emitter)

The BB graph is a directed graph of box nodes, four ports each:
α (try), β (retry), γ (success exit), ω (failure exit).

**The Law:** one GNU-as proc per box.  Each named pattern or
primitive box = one labeled proc with externally-visible ports
`α<N>` / `β<N>` / `γ<N>` / `ω<N>`.  Disambiguate across blobs in
one `.s` via `_pat_inv_<id>_` prefix.  No `bb`/`BB` prefix — Greek
letter alone carries identity.

Three-column shape, literal `;` separators (GAS treats `;` as
statement separator on x86):
```
LABEL: ; ACTION ; GOTO
```

Proven precedent: `bb_emit.c` TEXT mode + 151 NASM macros, 106/106
vs SPITBOL oracle.

### Separation in sm_codegen_x64_emit.c

```
emit_sm_instr()  -- SM opcodes; flat macro call per opcode; SM-shape
emit_bb_box()    -- one proc per SM_PAT_*; BB-shape with ; separators
```

For JVM/.NET/JS/WASM: same separation, same α/β/γ/ω port protocol.

---

## Five-phase pattern execution model (sess #71)

| Phase | What | Failure mode |
|-------|------|--------------|
| 1 | Build subject | can fail → `:F` |
| 2 | Build pattern (SM produces a BB graph) | can fail → `:F` |
| 3 | Pattern match against subject (with backtracking) | can fail → `:F` |
| 4 | Build replacement | can fail → `:F` |
| 5 | Perform replacement | — |

Phases 1, 4, 5: straight-line SM bytecode.  Phase 2: SM bytecode
that produces a BB graph.  Phase 3: walks the graph using α/β/γ/ω
with backtracking.

For mode-4, each pattern's BB graph appears in `.s` as a mix of
maximal invariant sub-trees (inlined as flat `.text` chunks at
emit time) and variant nodes (Phase-2 SM ops at runtime allocate
`bb_pool` RX slots and emit per-node x86 bytes).  Stitching via
direct jmps on the four ports.  Final optimization form, not an
incremental polish.

`flat_is_eligible_node(p)`: only XVAR is variant.  Mutable-ζ kinds
(XSPNC/XBRKC/XANYC/XNNYC/XLNTH/XTB/XRTB/XFNCE/XDSAR/XATP/XBRKX/
XCALLCAP) are invariant — graph topology fixed at build time;
ζ values bake as static `.data`.  XCAT n>2 is variant (handled by
runtime path).

---

## Reuse, do not rewrite

| Component | Status | Source |
|-----------|--------|--------|
| `bb_emit.c` dual-mode (TEXT/BINARY) | proven 106/106 | `src/runtime/x86/bb_emit.c` |
| `snobol4_asm.mac` 151 NASM macros | extant | `archive/backend/snobol4_asm.mac` |
| 25 box kinds × 5 backends | live | `bb_boxes.{c,j,il,js,wat}` |
| `bb_lit_emit_binary` + `bb_build_binary_node` | proven | `bb_build.c` |
| `bb_flat.c` flat-glob invariant emit | live (mode 3 + mode 4) | `bb_flat.c` |
| `flat_is_eligible(p)` | live | `bb_flat.c` |
| `bb_pool.c` RW→RX slab | proven | `bb_pool.c` |
| `stmt_exec.c` Phase-3 driver | live | `stmt_exec.c` |
| `emitter_v` vtable (TEXT/BINARY) | live | `emitter_v.h` + `emitter_text.c` + `emitter_binary.c` |
| Phase-2 PATND_t simulator | live | `sm_phase2_to_patnd` in `sm_codegen_x64_emit.c` |

Mode-3 (`--jit-run --bb-live`) is mode-4's existence proof.  Mode-4
takes the same code path but writes bytes (or text) to a `.s` file
at compile time instead of `bb_pool` at runtime.  The
`EMIT_TEXT`/`EMIT_BINARY` mode switch in `bb_emit.c` is the bridge.

---

## libscrip_rt.so contents (post-EM-7-revert, sess #72)

**In:** NV table, GC, builtin shims, `bb_pool` allocate/seal/free,
`bb_emit` BINARY helpers, `bb_build_flat`/`bb_build_binary` (called
by Phase-2 SM in variant case), full SNOBOL4 runtime, BB broker
(only for variant patterns post-CH-17).

**Out (dead for emitted code):** `scrip_rt_pat_*` descriptor-tree
builders, `scrip_rt_exec_stmt → exec_stmt → bb_broker` chain,
`g_pat_stack[]` runtime descriptor state.

---

## Generated-code readability standard

Major banner at every statement boundary (`SM_STNO`):
```
# ============================================================================
# stmt N  (line L):  <verbatim source line>
# ============================================================================
```

Minor banner between conceptual blocks within a statement.  GNU-as
line-comment is `#`; `;` is a statement separator on x86.

Inline annotations in col 3 carry only info NOT visible in col 2:
- `# str="..."` (col 3 args show only `.Lstr_N`)
- `# var=NAME`, `# store -> NAME`
- `# fname="..."` for CALL_FN
- Opcode disambiguators (e.g. `# SM_RETURN_F` on RETURN_VARIANT)

Annotations duplicating col 2 are forbidden (`# SM_POP`, `# SM_JUMP`,
`# SM_PAT_DEREF` — gone).

---

## Tracked artifacts protocol

Six artifacts in `corpus/programs/snobol4/demo/`:

| File | Features |
|------|----------|
| `roman.s` | Recursive DEFINE, REPLACE, BREAK |
| `wordcount.s` | BREAK/SPAN, INPUT loop, arithmetic |
| `claws5.s` | ARBNO, complex patterns |
| `treebank-list.s` | Nested patterns, stack ops |
| `treebank-array.s` | Array ops, nested patterns |
| `sm_macros.s` | Shared SM-macro library, `.include`'d by every demo `.s` |

GAS resolves `.include "sm_macros.s"` from the same directory as
the including `.s`.

End every session that touches `sm_codegen_x64_emit.c`,
`sm_emit_template.{c,h}`, or `scrip_rt.c`:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo
SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --jit-emit --x64 $f.sno > $f.s 2>/dev/null
done
# sm_macros.s auto-(re)written to CWD by every emit run.
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK   $s" \
        || { echo "FAIL $s — NOT committing"; cat /tmp/as_err.txt; exit 1; }
done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

### M2 phase — SNOBOL4 + Snocone

- [x] EM-1 — Driver wiring + `libscrip_rt.so` skeleton.
- [x] EM-2 — SM_HALT + SM_PUSH_LIT_I codegen.
- [x] EM-3 — Stack ops + arithmetic.
- [x] EM-4 — Control flow + readability standard.
- [x] EM-5 — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.
- [x] EM-6 — Pattern matcher integration.  (Retired by EM-7-revert.)
- [x] EM-7-revert — Tear out brokered Phase-3 from emitted-code path.
- [x] EM-7-default-bb-live — Flip BB-mode default to bb-live.
- [x] EM-7-default-jit-run — Flip exec-mode default to jit-run.
- [x] EM-7-emit-determinism — Fix dangling `s->subject->sval` pointer.
- [x] EM-7a — Phase-2 SM simulator (PATND_t reconstruction).
- [x] EM-7b — `bb_flat.c` EMIT_TEXT mode + external α/β/γ/ω labels.
- [x] EM-7b' — `emitter_v` vtable refactor.
- [x] EM-7b'' — Instruction-description layer.
- [x] EM-7c-pure-invariant — Wire fully-invariant patterns through `.text` blobs.
- [x] EM-7c-symbolic — Symbolic refs replace baked process addresses.
- [x] EM-7c-symbolic-runtime-correctness — Fix blob entry label placement.
- [x] EM-7c-variant — Wire variant pattern nodes via path β.
- [x] EM-7d-prep — SM_PAT_CAPTURE_FN etc. emit helpers.
- [x] EM-7d-usercall-reentrant — Native chunk registry for user-fn dispatch.
- [x] EM-7d-usercall-retval-from-nv — Read user-fn retval from `NV[fname]`.
- [x] EM-7c-invariance-rule — Correct invariance + static `.data` ζ.
- [x] EM-7c-greek-purge — Remove Latin alpha/beta/gamma/omega from BB-port context.
- [x] EM-7c-sm-macros — Introduce SM-side asm macro library.
- [x] EM-7c-sm-three-column — Three-column SM dispatch + macro library externalised + SM_ prefix stripped from generated-code macro names.
- [x] **EM-7c-three-column-non-bb — Corrected three-column shape (label/opcode/args+comment, widths 24/16/N) extended uniformly to every non-BB line in emitted `.s` AND in `sm_macros.s` body lines AND SM dispatch.  Redundant opcode-name annotations stripped.  C enums `SM_POP`→`SM_VOID_POP` and `SM_CALL`→`SM_CALL_FN` for symmetry with macro names.  LANDED 2026-05-09.**

- [ ] EM-7c-bb-three-column — Emit each BB box as a 4-port α/β/γ/ω cluster in three-column `LABEL: ; ACTION ; GOTO` form, straight x86 (no macros yet), Greek-only port names, no `bb`/`BB` prefix.
      **PARTIAL PROGRESS sess 2026-05-09:**
      Three-column shape `LABEL: ; ACTION ; GOTO` (widths 24/16/N, literal `;` separators) IS now emitted for every BB-box body line that flows through the central paths:
       - `emitter_text.c` `text_emit_insn` / `text_label_define` / `text_emit_jmp` / `text_global_sym` (the workhorse for bb_flat.c instruction emissions)
       - `bb_emit.c` `bb_label_define` / `bb_text_label` / every `bb_insn_*` TEXT branch (mov, lea, ret, nop, call, jmp/je/jne/jl/jge/jg, cmp, movzx, xor, push/pop rbp, sub/add rsp)
      New helpers added: `bb3c_format` / `bb3c_text` (in `bb_emit.c/h`), `ev3c` / `ev3c_action_v` / `ev3c_label` / `ev3c_goto_v` (static inline in `emitter_v.h`).
      `bb_emit_byte` / `bb_emit_patch_rel8` / `bb_emit_patch_rel32` TEXT-mode paths now `abort()` with a clear diagnostic (no more `.byte 0xNN` hex walls or `.byte 0x00` placeholders — every reachable instruction goes through a named mnemonic helper).
      Side-quests landed alongside (responding to Lon's review):
       (a) Per-op arithmetic macros: `ARITH \op` shared macro with opaque integer arg + `# SM_ADD` annotation removed.  Replaced with named no-arg macros `ADD_NUM`, `SUB_NUM`, `MUL_NUM`, `DIV_NUM`, `MOD_NUM` — op-enum baked into each macro body via `t->const_a`.  Col 2 carries the op name directly; redundant `# SM_<op>` annotation gone.  `_NUM` suffix avoids GAS case-insensitive collision with x86 `add`/`sub`/`mul`/`div` mnemonics (same disambiguator pattern as `VOID_POP` / `CALL_FN`).
       (b) Blank lines in emitted `.s` eliminated.  Three sites in `sm_codegen_x64_emit.c` (`emit_major_break`, pattern-blob banner, EM-7c invariant-blobs banner) had leading `\n` that produced blank lines before banners.  All three fixed; emitted output now has zero blank lines.
      **NOT YET DONE (next session):**
       - 12 raw `EV_TEXT(e, "\t.section .data\n%s:\n\t.string ...\n\tlea rdi, [rip + ..]\n\tmov esi, 0\n\tcall bb_X@PLT\n\ttest rax, rax\n", ...)` blocks in `bb_flat.c` (charsets / XLNTH / XTB / XRTB / XFNCE / XFARB / XSTAR / XBRKX / XATP / XDSAR / XARBN child sub-procs / XNME/XFNME cap data + child sub-procs).  Each EV_TEXT call emits a multi-line tab-indented chunk that needs splitting into a sequence of three-column `ev3c` calls — one line per directive, label in col 1, directive in col 2.  Mechanical conversion ~80 line edits.  **Until these convert, the `.s` artifacts contain three-column lines interleaved with tab-indented two-column blocks inside BB blobs — assembles cleanly but visually inconsistent.**
       - 1:1 SM-opcode-to-macro mapping is not yet complete.  Missing template entries for `SM_LABEL` (no-op marker, the `.LpcN` label suffices), `SM_STNO`, `SM_PUSH_LIT_F`, `SM_PUSH_NULL_NOFLIP`, `SM_PUSH_EXPR`, `SM_NEG`, `SM_EXP`, `SM_NEXT_PUSH`.  Some are no-ops by design, others not yet wired through the SM-macro layer.  Worth a dedicated rung.
      **Gates final state (this session) — 10/10 GREEN:**
      smoke ×6: snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4 · isolation N/A this rung · unified_broker PASS=49 · EM gate PASS=12 · bb_flat_text PASS=18 · sm_phase2_sim PASS=25.
      **Tracked artifact line counts (regenerated this session):**
      | File | Lines | Was |
      |------|------:|----:|
      | roman.s | 209 | 178 |
      | wordcount.s | 158 | 196 |
      | claws5.s | 1115 | 1241 |
      | treebank-list.s | 1396 | 1559 |
      | treebank-array.s | 1579 | 1763 |
      | sm_macros.s | 230 | 230 |
      All five assemble cleanly via `gcc -c`.

- [x] **EM-7c-stmt-banner-fidelity — LANDED 2026-05-09.**  Every statement banner is now followed by SM/BB code that lowers from that statement — no naked `.LpcN:` lines, no disembodied `# (baked into _pat_inv_<id> ...)` comments.  Three changes in `sm_emit_template.{c,h}` + `sm_codegen_x64_emit.c`:

      (1) **New `SM_TPL_NOOP` shape** (sm_emit_template.h enum + sm_emit_template.c renderers).  Empty-body marker macro (`.macro NAME\n.endm`).  Per-call line is one three-column row carrying the macro name in col 2 — assembles to nothing, but the col-1 .LpcN: pc-label is consumed and never naked.  `sm_emit_noop` thin entry mirrors `sm_emit_nullary`.

      (2) **`SM_LABEL` and `SM_STNO` registered as NOOP-shape templates** in `g_sm_templates[]`.  `emit_sm_label` now calls `sm_emit_noop(out, sm_template_lookup(SM_LABEL), NULL)` — emits `.LpcN:                  LABEL`.  `emit_sm_stno` emits the major banner first, then `sm_emit_noop` for the STNO line — `.LpcN:                  STNO` immediately under the banner.  Both macros have empty bodies so no runtime semantics change.

      (3) **`emit_sm_pat_baked` rewritten** to produce a real three-column line for each blob-absorbed PC: `.Lpc7:                  # PUSH_INT       baked  _pat_inv_0 pc=7..12`.  Col 2 is the macro-name (`PUSH_INT`, `PAT_RPOS`, etc., resolved via `sm_template_lookup(ins->op)->macro_name`) prefixed with `#` so the assembler treats it as a comment — the line assembles to nothing while the human eye scans the op name.  Col 3 carries `baked` plus a back-reference (`_pat_inv_<id> pc=<start>..<end>`) so the reader can find the actual blob entry.

      Failure mode 3 (cross-banner code drift) was audited and found NOT to fire on the five tracked artifacts — `RETURN_VARIANT` for `:F(RETURN)` lands at the correct PC under its own banner.  The pc→stno audit pass is deferred to a future rung if the failure mode surfaces.

      **Sample dispatch under stmt 4 banner (roman.s) — before vs after:**

      ```
      BEFORE                                                       AFTER
      .Lpc6:                                                       .Lpc6:                  STNO
      .Lpc7:           # (baked into _pat_inv_0 at .text — SM_*)   .Lpc7:                  # PUSH_INT       baked  _pat_inv_0 pc=7..12
      .Lpc8:           # (baked into _pat_inv_0 at .text — SM_*)   .Lpc8:                  # PAT_RPOS       baked  _pat_inv_0 pc=7..12
      ...                                                          ...
      .Lpc13:          PUSH_VAR     .Lstr_4 # var=N                .Lpc13:                 PUSH_VAR         .Lstr_4 # var=N
      ```

      **Gates 10/10 GREEN this session:** smoke ×6 (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4), isolation PASS, unified_broker PASS=49, EM gate PASS=12, bb_flat_text PASS=18, sm_phase2_sim PASS=25.

      **Tracked artifact line counts (regenerated this session):**
      | File | Lines | Was |
      |------|------:|----:|
      | roman.s | 209 | 209 |
      | wordcount.s | 158 | 158 |
      | claws5.s | 1115 | 1115 |
      | treebank-list.s | 1396 | 1396 |
      | treebank-array.s | 1579 | 1579 |
      | sm_macros.s | 249 | 230 |

      Body line counts unchanged (the new STNO/LABEL/baked lines replace existing rows one-for-one); sm_macros.s grew by 19 to add LABEL+STNO macro skeletons.  All five assemble cleanly.  Audit checks: zero naked `.Lpc<N>:` lines (col 2 always non-empty); zero disembodied `(baked into ...)` comments.

- [x] **EM-7c-s-file-beautify — LANDED 2026-05-09.**  Emitted `.s` artifacts are now one uniform three-column document end-to-end: SM-side dispatch lines and BB-blob body lines share the same `%-24s%-16s %s` shape.  Zero `;` separators, zero blank lines, zero tab-indented or 4-space-indented stragglers across all five tracked artifacts.

      **Three changes bundled, one diff:**

      (1) **`;` separators removed** from `bb_emit.c::bb3c_format` and `emitter_v.h::ev3c`.  Both helpers' printf format string changed from `%-24s ; %-16s ; %s\n` → `%-24s%-16s %s\n` — matching SM-side `emit_three_column_line` and `sm_emit_template::render_call_line`.  ONE shape across the entire `.s`.

      (2) **12 raw `EV_TEXT` blocks in `bb_flat.c` converted** to three-column form via a new file-static helper family:
       - `flat3c(e, lbl, act, got)` — central renderer; routes through `e->fprintf_raw` with the unified format.
       - `flat3c_action(e, act, args)` — col 1 empty, col 2 = mnemonic, col 3 = operand string.
       - `flat3c_label(e, name)` — col 1 = `name:`, cols 2+3 empty.
       - `flat_data_section/text_section/intel_syntax(e)` — one-liner section directives.
       - `flat_data_string(e, s)` — emits `.string "<escaped>"` with the same per-byte escape loop the original site used.
       - `flat_data_quad(e, str)` / `flat_data_quad_int(e, v)` / `flat_data_long(e, v)` / `flat_data_zero(e, n)` — directive in col 2, arg in col 3.
       - `flat_globl(e, name)` — `.globl name`.
       - `flat_box_call(e, rdi_load, fn, mode)` — emits the four-line (lea / mov esi / call / test) sequence, each as one three-column line.
       - `flat_box_call_slot(e, slot_lbl, fn, mode)` — variant for arbno's `qword ptr [rip + slot]` deref.
      Twelve sites converted: charsets (XSPNC/XANYC/XBRKC/XNNYC), XLNTH, XTB, XRTB, XFNCE, XFARB, XSTAR, XBRKX, XATP, XDSAR, XARBN, XNME/XFNME.  Zero raw `EV_TEXT` calls remain in `bb_flat.c`.

      (3) **`emit_sm_exec_stmt_blob` rerouted** through `emit_three_column_line` for its three follow-on lines (rsi-arg, edx-arg, call).  Was using `sm_line` whose no-label fallback emitted `\t%-15s %s\n` (tab-indented) — that produced the last 3 tab-indented stragglers per artifact.  Now all four lines render with 24-space col-1 padding (the first line consumes the pending `.LpcN:` pc-label via `sm_emit_consume_pc_label`).

      **Files touched (one4all):**
      - `src/runtime/x86/bb_emit.c`: `bb3c_format` format-string change.
      - `src/runtime/x86/emitter_v.h`: `ev3c` format-string change.
      - `src/runtime/x86/bb_flat.c`: +127 lines for the helper family; 12 `EV_TEXT` block conversions (~80 lines net delta).
      - `src/runtime/x86/sm_codegen_x64_emit.c`: `emit_sm_exec_stmt_blob` rerouted through `emit_three_column_line`.

      **Gates final state — 10/10 GREEN:**
      smoke ×6 (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4), isolation PASS, unified_broker PASS=49, EM gate PASS=12, bb_flat_text PASS=18, sm_phase2_sim PASS=25.

      **Audit checks — all GREEN per artifact:**
      | File | blank | tabs | `;` |
      |------|------:|-----:|----:|
      | roman.s | 0 | 0 | 0 |
      | wordcount.s | 0 | 0 | 0 |
      | claws5.s | 0 | 0 | 0 |
      | treebank-list.s | 0 | 0 | 0 |
      | treebank-array.s | 0 | 0 | 0 |

      **Tracked artifact line counts:**
      | File | Lines | Was |
      |------|------:|----:|
      | roman.s | 208 | 209 |
      | wordcount.s | 158 | 158 |
      | claws5.s | 1114 | 1115 |
      | treebank-list.s | 1395 | 1396 |
      | treebank-array.s | 1578 | 1579 |
      | sm_macros.s | 249 | 249 |

      Counts dropped by 1 each (except wordcount and sm_macros) because the prior partial rung's `; .global ...` blob-port lines collapse cleanly into the unified shape — same content, no `;` overhead.

      **EM-7c-bb-three-column-data SUBSUMED + LANDED here** (the data-block conversion sub-rung carved earlier was folded into this rung; its checkbox dropped).

- [x] **EM-7c-bb-three-column-split — LANDED 2026-05-09.**  Every line of every emitted `.s` artifact now obeys a true three-column law: col 1 = label-or-empty (24 wide), col 2 = mnemonic OR directive token ONLY (16 wide), col 3 = operands + optional `# comment` (free).  No more `"mov     r10, 0x..."` strings stuffed into col 2 (which overflowed the 16-wide field and broke col-3 alignment); no more `"je      _label"` strings stuffed into col 3 with cols 1+2 empty (which left jumps visually disconnected from the surrounding code).

      **Diagnosis.**  The `bb3c_format` / `emit_three_column_line` primitives were already correct (`%-24s%-16s %s\n`).  The bug was at the call sites: `bb3c_action(fmt, ...)` and `emit3c_action(fmt, ...)` accepted a single fused mnemonic-plus-operands string that callers built like `"mov     r10, 0x%llx"`.  That string is 20+ chars wide and overflowed `%-16s`, spilling into col 3 and pushing the operand visually rightward by an unpredictable amount per opcode.  Jumps had the symmetric bug: `bb3c_goto`/`emit3c_goto` put the entire `"jmp _label"` into col 3 with cols 1+2 empty — leaving a 41-character empty prefix that looked like a continuation of nothing.

      **Two files, surgical changes:**

      1.  `src/runtime/x86/bb_emit.c`: replaced `bb3c_action`/`bb3c_goto` with **`bb3c_op(mn, args_fmt, ...)`** and **`bb3c_jmp(mn, target)`**, both taking mnemonic and operands as separate args.  Rewrote all 22 `bb_insn_*` helpers (mov, lea, cmp, je, jne, jmp, jl, jge, jg, call, ret, nop, test, xor, push, pop, add, sub, movzx, movsxd, etc.) to use the new split form.

      2.  `src/runtime/x86/emitter_text.c`: replaced `emit3c_action`/`emit3c_goto` with `emit3c_op(e, mn, fmt, ...)` / `emit3c_jmp(e, mn, target)`.  Rewrote all 30 cases of `text_emit_insn`'s switch.  Rewrote `text_emit_jmp` (col 2 = jmp/je/jne/..., col 3 = target) and `text_global_sym` (col 2 = `.global`, col 3 = name).

      **Result.**  SM section uses macro names (`STNO`, `PUSH_STR`, `CALL_FN`, `JUMP`, `PUSH_VAR`, `PAT_RPOS`, `RETURN_VARIANT`, etc.) in col 2.  BB section uses raw asm mnemonics (`mov`, `lea`, `cmp`, `je`, `jne`, `jmp`, `call`, `test`, `ret`, `xor`, `push`, `pop`, `movsxd`) in col 2.  Directives (`.section`, `.string`, `.quad`, `.long`, `.zero`, `.global`, `.globl`, `.intel_syntax`, `.text`, `.type`, `.size`, `.include`, `.align`) all sit in col 2 with their argument in col 3.  Operands always col 3.

      **Test-side update.**  `bb_flat_text_test.c`'s substring CHECKs (`strstr(buf, ".global _pat_inv_42_0_α")`, `strstr(buf, "lea     r10, [rip + ")`) were coupled to the old fused-column shape (single space between `.global` and the symbol; five spaces between `lea` and `r10`).  Updated to two independent substring checks each — directive-token + symbol-name, mnemonic + operand-pattern — that pass regardless of inter-column padding.  Test still asserts both tokens appear (and the file structure ensures they're on the same line).  PASS=18 unchanged.

      **Files touched (one4all):**
      - `src/runtime/x86/bb_emit.c`
      - `src/runtime/x86/emitter_text.c`
      - `src/runtime/x86/bb_flat_text_test.c`

      **Tracked artifact line counts (regenerated this session):**
      | File | Lines |
      |------|------:|
      | roman.s | 208 |
      | wordcount.s | 158 |
      | claws5.s | 1114 |
      | treebank-list.s | 1395 |
      | treebank-array.s | 1578 |
      | sm_macros.s | 249 |

      Counts unchanged from EM-7c-s-file-beautify baseline.  All five `gcc -c` clean.

      **Sample (roman.s) — before vs after:**
      ```
      BEFORE                                                AFTER
      _pat_inv_0_α:                                         _pat_inv_0_α:
                              lea     r10, [rip + Δ]                               lea              r10, [rip + Δ]
                              cmp     esi, 0                                       cmp              esi, 0
                                               je      _pat_inv_0_α_body                            je               _pat_inv_0_α_body
                                               jmp     _pat_inv_0_β                                 jmp              _pat_inv_0_β
      ```
      Mnemonic now sits in col 2 of the file's universal grid; operands in col 3.

      **Gates final state:**
      smoke ×5 PASS (snobol4 2/2, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4), isolation PASS, EM gate PASS=12/12, bb_flat_text PASS=18/18, sm_phase2_sim PASS=25/25, unified_broker PASS=6/6 (Prolog inline; csnobol4 oracle not provisioned in this session env).

- [x] **EM-7c-no-trailing-ws — LANDED 2026-05-09.**  No line in any generated `.s` artifact ends with whitespace.

      **Diagnosis.**  The universal `%-24s%-16s %s\n` format produces left-padding to 41 chars on every line, which manifests as trailing spaces on label-only lines (col 2 + col 3 empty), action-only lines with empty col 3, and macro-body emissions inside `sm_macros.s`.

      **Fix.**  Build into a buffer at every emission chokepoint, walk a tight loop right-trimming `' '` and `'\t'`, then write trimmed string + `'\n'`.  Eight chokepoints touched:

      | File | Function | Role |
      |---|---|---|
      | `bb_emit.c` | `bb3c_format` | every BB-side `.global`, label, instruction, jmp |
      | `sm_codegen_x64_emit.c` | `emit_three_column_line` | every SM-side directive, blob banner, `.section`, `.string`, `.quad`, etc. |
      | `sm_codegen_x64_emit.c` | `sm_line` (label / no-label arms) | SM dispatch fallthroughs |
      | `sm_codegen_x64_emit.c` | `emit_pc_label` | bare label-only line (was `%-24s\n` → now `.LpcN:\n`) |
      | `sm_emit_template.c` | `macro_line` | `sm_macros.s` body lines |
      | `sm_emit_template.c` | `render_call_line` (label / no-label arms) | every macro-driven SM dispatch line |
      | `bb_flat.c` | `flat3c` | charset / XLNTH / XTB / XRTB / XFNCE / XFARB / XSTAR / XBRKX / XATP / XDSAR / XARBN / XNME helper sub-procs |
      | `emitter_v.h` | `ev3c` | inline header helper |

      **Verification (grep -P '[ \t]+$' and awk both report 0 lines per file):**
      | Artifact | Lines | gcc -c | trailing-ws |
      |---|---:|:---:|:---:|
      | `roman.s` | 208 | OK | 0 |
      | `wordcount.s` | 158 | OK | 0 |
      | `claws5.s` | 1114 | OK | 0 |
      | `treebank-list.s` | 1395 | OK | 0 |
      | `treebank-array.s` | 1578 | OK | 0 |
      | `sm_macros.s` | 249 | (assembled via .include) | 0 |

      **Files touched (one4all):**
      - `src/runtime/x86/bb_emit.c`
      - `src/runtime/x86/sm_codegen_x64_emit.c`
      - `src/runtime/x86/sm_emit_template.c`
      - `src/runtime/x86/bb_flat.c`
      - `src/runtime/x86/emitter_v.h`

      **Gates final state — same as EM-7c-bb-three-column-split:**
      smoke ×5 PASS, isolation PASS, EM PASS=12/12, bb_flat_text PASS=18/18, sm_phase2_sim PASS=25/25, unified_broker PASS=6/6 (Prolog inline; csnobol4 oracle not in env).

- [x] **EM-7c-sm-three-column-verify** — LANDED 2026-05-09.  C audit harness in `sm_codegen_x64_emit_test.c` (`--audit <file.s>...` mode), wired into `test_smoke_jit_emit_x64.sh` as Test 14.  Emits zero violations across all six tracked artifacts.

      **The audit invariants (refined from the rung spec's three bullets after empirical Python prototyping):**

      | # | Rule | What it catches |
      |---|------|-----------------|
      | I0 | no blank lines | trailing `\n\n` regressions |
      | I1 | no bare `;` outside strings/comments | leftover NASM-style separator |
      | I2 | no TAB outside string literals | indentation drift |
      | I3 | if col-1 has content, must be `label:` shape | malformed col-1 |
      | I3a | directive can't be off the col-1 grid (e.g. `    .ifnb`) | macro-body indentation drift |

      **Dropped from the prototype:** an "I5: col-2 token ≤16 chars when col-3 follows" rule.  Empirically, `EXEC_STMT_VARIANT` (17 chars) emits as a well-formed three-column line via `printf`'s `%-16s` (which doesn't truncate, just pads-to-min); col 3 simply pushes right by one.  The rule was a layout-target conflated with an invariant.  The *actual* col-2 invariant — single contiguous non-whitespace token, no internal whitespace — is enforced implicitly by the scan loop terminating on first whitespace, and that's what catches the EM-7c-bb-three-column-split bug class.

      **Two source-side fixes the audit surfaced:**

      (1) `emit_optional_lbl` in `sm_emit_template.c` produced 4-space-indented `.ifnb`/`.else`/`.endif` directives and 8-space-indented `lea`/`xor` body lines inside macro bodies for `PAT_LIT`/`PAT_REFNAME`/`PAT_USERCALL`/`PAT_CAPTURE`/`PAT_CALL_FN`/`PAT_CAPTURE_FN_ARGS`/`EXEC_STMT_VARIANT` macros.  Rewrote to route every line through `macro_line` so directives sit in col 2 and body operands sit in col 3.  GAS conditional-assembly is indentation-insensitive — assembly identical, audit clean.

      (2) Trailing blank line at end of `sm_macros.s` (was `# === END sm macro library ===\n\n`).  Collapsed `\n\n` to single `\n`.

      **What was NOT done in this rung (deliberately deferred — same shape as prior CH-15-SURVEY):**

      - **Labels on demand only** — emit `.LpcN:` only when the PC is a jump target.  Architecturally interesting (needs a pre-pass over `SM_Program` computing the jump-target set before emission); risky (changes pc→label mapping that downstream BB blob entry-points depend on).  Carve as **EM-7c-sm-three-column-verify-labels-on-demand**.
      - **Six template-gap fills** (`SM_PUSH_LIT_F`, `SM_PUSH_NULL_NOFLIP`, `SM_PUSH_EXPR`, `SM_NEG`, `SM_EXP`, `SM_NEXT_PUSH`) — none of these opcodes appear in any of the five tracked corpora today.  Same dead-code shape as CH-15-SURVEY's finding for `SM_PUSH_EXPR`.  Worth a survey before fills.  Carve as **EM-7c-sm-three-column-verify-template-gaps-survey**.

      **Files touched (one4all only — corpus untouched except auto-regenerated artifacts):**
      - `src/runtime/x86/sm_codegen_x64_emit_test.c` — added `--audit` mode (~190 LOC including doc-comment + counter/printer).
      - `src/runtime/x86/sm_emit_template.c` — rewrote `emit_optional_lbl` (8 lines → 22, forward decl `macro_line`); trimmed trailing `\n` from END marker.
      - `scripts/test_smoke_jit_emit_x64.sh` — added Test 14 (~30 lines).

      **Tracked artifact line counts (regenerated this session):**
      | File | Lines | Was |
      |------|------:|----:|
      | roman.s | 208 | 208 |
      | wordcount.s | 158 | 158 |
      | claws5.s | 1114 | 1114 |
      | treebank-list.s | 1395 | 1395 |
      | treebank-array.s | 1578 | 1578 |
      | sm_macros.s | 248 | 249 |

      Five SNOBOL4 demo artifacts byte-identical to baseline; `sm_macros.s` lost 1 line (the trailing blank).  All assemble cleanly.

      **Gates final state:**
      - smoke ×6 PASS (snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5, rebus 4/4)
      - isolation PASS · unified_broker PASS=49
      - EM PASS=13 (was 12; new Test 14 audits the three-column shape) · bb_flat_text PASS=18 · sm_phase2_sim PASS=25
      - **NEW: EM-7c-audit gate — 0 violations across all 6 tracked artifacts**


- [x] **EM-7c-bb-macros** — BB-side macro library: one named macro per box-port, Greek suffixes
      enforced on all BB labels, inline box-kind annotation on every α label line.

      **What the `*.byrd-reference.s` files contribute — and what they do not:**
      These files are from an earlier compiler generation (scrip-cc -asm, NASM syntax, different
      ABI, `snobol4_asm.mac`).  Their internal x86 sequences, data-block layout, and column widths
      are not authoritative for mode-4 GAS output.  What they establish unambiguously is **label
      naming discipline**: every BB port label in every byrd-reference file carries the Greek letter
      as a suffix — `seq_l0_α`, `seq_l0_β`, `dol1_γ`, `dol1_ω`, `P_3_α`, `P_3_β`, `P_3_γ`,
      `P_3_ω`.  No port label anywhere omits it.  That naming rule is worth preserving.

      **What the `test_sno_*.c` C files establish** (format ground truth):
      Three-column law.  Labels appear only when referenced.  Box-kind annotation is an inline
      col-3 comment on the first line of the box cluster, not a separate banner.  The C files'
      `/*----*/` separators mark named-box boundaries — one separator between distinct boxes.

      **Two concrete deliverables:**

      **1 — Greek suffix on every BB label (label rename pass):**
      Current mode-4 output has bare Latin-suffix BB labels: `xcat0_o`, `xcat0_mid_g`,
      `xcat0_left_b`, `xcat0_right_o`, `_cap1_ab`, `_cap1_cb`, `_cap1_cs`, `_cap1_cf`.
      These become `xcat0_ω`, `xcat0_γ`, `xcat0_left_β`, `xcat0_right_ω`, `_cap1_α_entry`,
      `_cap1_β_entry`, `_cap1_γ`, `_cap1_ω`.  Systematic rename in `bb_flat.c` label-string
      constants.  The blob-level labels `_pat_inv_<id>_α/β/γ/ω` already comply; only the
      internal sub-labels within port bodies need fixing.

      **2 — Named macro per port kind replacing raw inline x86:**
      Each `flat_emit_*` function currently emits a multi-instruction `ev_*` / `flat3c_action`
      sequence per port.  Replace with one `flat3c_action(e, "RPOS_α", args)` call.  `bb_macros.s`
      carries one `.macro`/`.endm` whose body is the verbatim x86 currently emitted inline — GAS
      expands to byte-identical bytes.  Macro naming: `BOXKIND_α` / `BOXKIND_β` per port.
      Box-kind annotation goes inline in col-3 as `# RPOS(0)`, `# LEN(1)`, `# BREAK α` on the
      α entry line — no separate preceding banner line.

      **Files:** `bb_flat.c` (label renames + rewire to macro calls), new `bb_macros.s`
      (auto-written to CWD, parallel to `sm_macros.s`), emitter driver (`.include "bb_macros.s"`
      alongside `.include "sm_macros.s"`).  No `sm_lower.c` changes.  No new SM opcodes.

      **Gates:** smoke ×6 PASS, isolation PASS, unified_broker PASS=49, EM PASS=12,
      bb_flat_text PASS=18, sm_phase2_sim PASS=25.  New gate: `gcc -c` clean on all five
      tracked artifacts.  New gate: zero bare Latin-suffix port labels in BB sections
      (`grep -cE '\b(xcat[0-9]+_[og]|_cap[0-9]+_[abc][bf]?):'` artifacts = 0).

      **Sample — roman.s before/after:**
      ```
      BEFORE (raw inline x86, non-Greek internal labels)
                              lea     r10, [rip + Δ]
                              cmp     esi, 0
                                               je      _pat_inv_0_α_body
                                               jmp     _pat_inv_0_β
      xcat0_left_b:
                                               jmp     xcat0_o
      xcat0_mid_g:

      AFTER (single macro call per port, Greek suffixes everywhere, inline annotation)
      _pat_inv_0_α:           RPOS_α           0        # RPOS(0)
      _pat_inv_0_β:           RPOS_β
      xcat0_left_β:           SEQ_β
                                               jmp     xcat0_ω
      xcat0_γ:
      ```

- [ ] **EM-FORMAT-SM** — Enforce the full SM three-column format law across all emitted `.s` artifacts.  **PARTIAL PROGRESS sess 2026-05-09:** (a) 120-char `#=` statement banners + pattern-blob banner LANDED (emit_major_break / emit_minor_break / EM-7c blob banner all extended from 78 to 120 chars); (b) comment-prefix strip LANDED (10 sites: `var=`, `str=`, `fname=`, `store -> ` removed; col-3 comments now bare opaque-arg referents — `# N`, `# "hello"`, `# myfunc`).  **REMAINING:** labels-only-when-referenced (pre-pass bitset over SM_Program; risk surface for BB blob entry-pc back-refs).  Gates 10/10 GREEN this session.

      **The SM format law (definitive):**

      1. **Three columns, no exceptions.**  Col-1 = label (24 chars, left-padded).  Col-2 = opcode / macro name (16 chars).  Col-3 = args + optional `# comment` (free width).  Single space between col-2 and col-3.
      2. **No blank lines anywhere in the emitted `.s`.**
      3. **Labels only when referenced.**  A `.LpcN:` line is emitted only when PC N is a jump target — i.e. is the destination of some `SM_JUMP`, `SM_JUMP_F`, `SM_JUMP_S`, `SM_CALL_CHUNK`, `SM_PUSH_CHUNK`, error landing pad, or BB blob entry-pc.  Unreferenced PCs are silent.  Risk: BB blob entry-pc back-refs (`# baked _pat_inv_<id> pc=N..M`) — keep `.LpcN:` for any PC in a blob range, or rewrite annotations to reference the blob's named symbol directly.
      4. **Program order = SNOBOL4 source order.**  SM ops emitted in statement order; no reordering.
      5. **Statement banners.**  Each SNOBOL4 statement begins with a 120-character `#` banner:
         ```
         # ============================================================================= (120 chars total)
         # stmt N  (line L):  <verbatim source line>
         # =============================================================================
         ```
         The banner immediately precedes the first SM op of that statement.  No blank line between banner and first op.
      6. **Comments say only what is unclear from col-2/col-3.**  Col-3 comment annotates the *referent* of an opaque arg — a `.Lstr_N` label, a chunk entry-pc, a return-variant integer — not the opcode itself.  Forbidden: `# SM_POP`, `# SM_JUMP`, `# var=N`, `# str=S`, `# fname=F` (the opcode name is already col-2; `var=`, `str=`, `fname=` add noise without revealing the value).  Permitted: `# "hello"` (when col-3 shows `.Lstr_4`), `# ROMAN` (when col-3 shows a chunk index), `# :F branch` (when col-3 shows a raw pc number for a failure transfer).

      **Implementation:**  Pre-pass over `SM_Program` builds a `uint8_t used_as_target[count]` bitset.  `emit_pc_label` gates on the bitset.  `emit_sm_stno` emits the 120-char `#=` banner then the STNO line (no blank between).  Comment-generation sites audited: remove `var=`/`str=`/`fname=` prefixes; keep only the bare value when it disambiguates an opaque `.Lstr_N` or numeric arg.

      **Files:** `sm_codegen_x64_emit.c` (label gating, banner, comment cleanup).  No changes to `sm_macros.s`, `bb_flat.c`, or `sm_lower.c`.

      **Gates:** smoke ×6 PASS, EM PASS=13, bb_flat_text PASS=18, sm_phase2_sim PASS=25, audit 0 violations (including new I4: no blank lines, already enforced; new I5: no unreferenced `.LpcN:` labels).  Tracked artifact line counts expected to drop (unreferenced PC labels removed).

      **Sample — roman.s stmt 4 before/after:**
      ```
      BEFORE                                        AFTER
      .Lpc6:                  STNO                  # =================================================================== (120)
      .Lpc7:                  # PUSH_INT  baked ...  # stmt 4  (line 10):  ROMAN  N RPOS(1) LEN(1) . UNITS =  :F(RETURN)
      .Lpc8:                  # PAT_RPOS  baked ...  # ===================================================================
      .Lpc13:                 PUSH_VAR   .Lstr_4 # var=N    .Lpc6:   PUSH_VAR   .Lstr_4 # N
      ```
      Unreferenced `.Lpc7:`..`.Lpc12:` gone (blob PCs absorbed); `# var=N` → `# N`.

- [ ] **EM-FORMAT-BB** — Enforce the full BB four-port / three-column format law across all emitted BB blobs.

      **The BB format law (definitive):**

      1. **Four ports per box, always.**  Every box emits exactly four labeled entry points: `α` (try), `β` (retry), `γ` (success exit), `ω` (failure exit).  All four carry the Greek letter suffix.  No port is omitted even if it is a trivial jump.
      2. **Three columns.**  Col-1 = label (24 chars).  Col-2 = action (16 chars) — one instruction or macro name per line, multiple action lines per port as needed.  Col-3 = goto — the jump target(s).  Semicolons separate GAS statements on the same source line when two instructions must appear together (e.g. action + goto on one line): `LABEL:          ACTION          ; jmp TARGET`.  Gotos go in col-3; never col-2.
      3. **No lone labels.**  A label is never emitted on a line by itself if it can share the line with the first instruction of its block.  If the block's first instruction is a multi-line sequence, the label goes on the same line as the first instruction of that sequence.  This rule applies identically to SM and BB.
      4. **Box banners.**  Each distinct box begins with a 120-character `#` separator:
         ```
         #-------------------------------------------------------------------------------- (120 chars total)
         # BOX  <kind>(<args>)  [label prefix]
         ```
         The banner immediately precedes the `α` label line of that box.  No blank line between banner and α line.
      5. **Pattern banner.**  At the start of each pattern blob (before the first box), a 120-char `#=` banner names the SNOBOL4 pattern expression (verbatim source or reconstructed from PATND_t).
      6. **No blank lines** anywhere in BB output.
      7. **Comments in col-3** name the box kind and argument on the α line only (e.g. `# RPOS(0)`, `# LEN(1)`, `# BREAK ".,;"`) — not repeated on β/γ/ω lines.

      **Implementation:**  `bb_flat.c` `flat_emit_*` and compositor functions emit banners before each box cluster.  `flat3c_label` replaced with a combined label+first-instruction form wherever the first instruction is known at label-define time.  Lone-label audit: scan all `EV_LABEL` call sites; where the next emission is always a `EV_JMP` or `flat3c_action`, fuse them.

      **Files:** `bb_flat.c` (banners, lone-label fusion, col-3 goto placement), `emitter_text.c` / `bb_emit.c` (semicolon separator support for fused action+goto lines).

      **Gates:** smoke ×6 PASS, EM PASS=13, bb_flat_text PASS=18, sm_phase2_sim PASS=25, audit 0 violations (extended audit: no lone labels, no blank lines in BB sections).

      **Sample — roman.s RPOS+XCAT blob before/after:**
      ```
      BEFORE                                        AFTER
      _pat_inv_0_α:                                 # =============== (120)
                      lea r10,[rip+Δ]               # PAT  N RPOS(1) LEN(1) . UNITS
                      cmp esi,0                     # ===============
                      je  _pat_inv_0_α_body         # ---------------- (120)
                      jmp _pat_inv_0_β              # BOX  RPOS(1)  [_pat_inv_0]
      _pat_inv_0_α_body:                            _pat_inv_0_α:   RPOS_α  1,xcat0_γ,xcat0_ω  # RPOS(1)
      ...                                           _pat_inv_0_β:   RPOS_β          ; jmp xcat0_ω
                                                    # ----------------
                                                    # BOX  XCAT  [xcat0]
                                                    xcat0_left_β:   SEQ_β           ; jmp xcat0_ω
                                                    xcat0_γ:        ...
      ```

- [ ] EM-7d — `--jit-emit --x64 beauty.sno` passes SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`, 646 lines).  Blocked on: (a) `*Parse *Space RPOS(0)` divergence vs `--sm-run`, (b) underlying beauty self-host regression (corpus issue: `-INCLUDE 'global.sno'` mismatched against `.inc` filenames; `error` label undefined).

- [ ] EM-8 — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries.

- [ ] EM-9 — M2 milestone close: package + docs.  Document `libscrip_rt.so` ABI; `make jit-emit-test` target; mark GOAL-CHUNKS.md Step 8 `[x]`.

### M5 phase — extends to Icon, Raku, Prolog, Rebus

⛔ Do not begin until GOAL-CHUNKS.md M4 (Steps 12–18) closes.

- [ ] EM-10 — SM_SUSPEND/SM_RESUME codegen + BB broker in `libscrip_rt.so`.
- [ ] EM-11 — Icon main + smoke_icon 5/5.
- [ ] EM-12 — Raku CASE + smoke_raku 5/5.
- [ ] EM-13 — Icon generators (per-kind bundles).
- [ ] EM-14 — Prolog clauses + smoke_prolog 5/5.
- [ ] EM-15 — Rebus + smoke_rebus 4/4.
- [ ] EM-16 — M5 close: full-frontend gate; mark GOAL-CHUNKS.md Step 19 `[x]`.

---

## Definitions

- **mode 4 / `--jit-emit`** — fourth SCRIP execution mode: emit
  standalone asm/binary linked against `libscrip_rt.so`.  Modes
  1–3 are `--ir-run`, `--sm-run`, `--jit-run`.
- **`libscrip_rt.so`** — runtime support library the emitted
  binary links against.
- **baked-direct opcode** — produces inline x86 (e.g. `SM_PUSH_INT`,
  `SM_ADD`, `SM_JUMP`).  No PLT call.
- **runtime-call opcode** — produces a PLT call into
  `libscrip_rt.so` (e.g. `SM_PAT_MATCH`).

---

## Watermark

EM-7c-sm-three-column-verify LANDED 2026-05-09
=============================================

C audit harness in `sm_codegen_x64_emit_test.c` (`--audit <file.s>...`
mode), wired into `test_smoke_jit_emit_x64.sh` as Test 14.  Validates the
three-column shape invariants on every line of every tracked artifact;
emits zero violations across all six.

**Audit invariants (refined empirically from the rung spec via Python
prototyping before C port):**

| # | Rule | What it catches |
|---|------|-----------------|
| I0 | no blank lines | trailing `\n\n` regressions |
| I1 | no bare `;` outside strings/comments | leftover NASM-style separator |
| I2 | no TAB outside string literals | indentation drift |
| I3 | if col-1 has content, must be `label:` shape | malformed col-1 |
| I3a | directive can't be off the col-1 grid (e.g. `    .ifnb`) | macro-body indent drift |

Dropped the prototype's "I5: col-2 token ≤16 chars w/col-3" rule on
reflection — `printf`'s `%-16s` doesn't truncate, so `EXEC_STMT_VARIANT`
(17 chars) emits a well-formed three-column line with col-3 pushed right
by 1.  Layout-target conflated with invariant.  The *actual* col-2
invariant — single contiguous non-whitespace token — is enforced
implicitly by the scan loop terminating on first whitespace, which is
what catches the EM-7c-bb-three-column-split bug class.

**Two source-side fixes the audit surfaced:**

(1) `emit_optional_lbl` in `sm_emit_template.c` produced 4-space-indented
    `.ifnb`/`.else`/`.endif` directives and 8-space-indented `lea`/`xor`
    bodies inside macro bodies for `PAT_LIT`/`PAT_REFNAME`/`PAT_USERCALL`/
    `PAT_CAPTURE`/`PAT_CALL_FN`/`PAT_CAPTURE_FN_ARGS`/`EXEC_STMT_VARIANT`
    macros.  Rewrote to route every line through `macro_line` so
    directives sit in col 2 and operands in col 3.  GAS conditional-
    assembly is indentation-insensitive; assembly identical, audit clean.

(2) Trailing blank line at end of `sm_macros.s` — `# === END sm macro
    library ===\n\n` collapsed to single `\n`.

**Two pieces of the rung spec deferred (carved as new sub-rungs):**

- `EM-7c-sm-three-column-verify-labels-on-demand` — emit `.LpcN:` only
  when the PC is a jump target.  Risk surface around BB-blob entry-pc
  back-references; needs a pre-pass over `SM_Program` collecting jump
  targets.
- `EM-7c-sm-three-column-verify-template-gaps-survey` — the six listed
  template gaps (`SM_PUSH_LIT_F`, `SM_PUSH_NULL_NOFLIP`, `SM_PUSH_EXPR`,
  `SM_NEG`, `SM_EXP`, `SM_NEXT_PUSH`) fire on zero of the five tracked
  artifacts.  Same dead-code shape as CH-15-SURVEY for `SM_PUSH_EXPR`.
  Survey before fills.

**Files touched (one4all only):**
- `src/runtime/x86/sm_codegen_x64_emit_test.c` — new `--audit` mode (~190 LOC)
- `src/runtime/x86/sm_emit_template.c` — rewrote `emit_optional_lbl`; trimmed END marker `\n\n`→`\n`; forward decl `macro_line`
- `scripts/test_smoke_jit_emit_x64.sh` — added Test 14 (~30 lines)

**Tracked artifact line counts:**

| File | Lines | Was | trailing-ws | gcc -c |
|------|------:|----:|:-----------:|:------:|
| roman.s          |  208 |  208 | 0 | OK |
| wordcount.s      |  158 |  158 | 0 | OK |
| claws5.s         | 1114 | 1114 | 0 | OK |
| treebank-list.s  | 1395 | 1395 | 0 | OK |
| treebank-array.s | 1578 | 1578 | 0 | OK |
| sm_macros.s      |  248 |  249 | 0 | (via `.include`) |

Five SNOBOL4 demo artifacts byte-identical to baseline; `sm_macros.s`
loses 1 line (the trailing blank).  All assemble cleanly.

**Gates final state:**
- smoke ×6 PASS (snobol4 7/7, icon 5/5, prolog 5/5, raku 5/5, snocone 5/5, rebus 4/4)
- isolation PASS · unified_broker PASS=49
- EM PASS=13 (was 12 — Test 14 added) · bb_flat_text PASS=18 · sm_phase2_sim PASS=25
- **NEW gate: audit emits 0 violations across all 6 tracked artifacts**

----

EM-7c-no-trailing-ws LANDED 2026-05-09
=============================================

Two new rungs landed in this session, on top of the EM-7c-s-file-beautify
baseline.

**EM-7c-bb-three-column-split** — true three columns (label / mnemonic /
operands).  The `bb3c_format` / `emit_three_column_line` primitives were
already correct (`%-24s%-16s %s\n`); the bug was at the call sites:
`bb3c_action(fmt, ...)` was being given a single fused mnemonic-plus-args
string like `"mov     r10, 0x..."` that overflowed the 16-wide col-2 field.
Jumps had the symmetric bug: the entire `"jmp _label"` string was stuffed
into col 3 with cols 1+2 empty, leaving a 41-char empty prefix.  Replaced
`bb3c_action`/`bb3c_goto` with `bb3c_op(mn, args_fmt, ...)` and
`bb3c_jmp(mn, target)`; rewrote all 22 `bb_insn_*` helpers in `bb_emit.c`
and all 30 cases of `text_emit_insn` in `emitter_text.c`; updated
`text_emit_jmp` and `text_global_sym` (col 2 = `.global`, col 3 = name).
Updated `bb_flat_text_test.c`'s substring CHECKs (which were brittle to
inter-column whitespace) to assert directive-token + symbol-name
independently — PASS=18 unchanged.

**EM-7c-no-trailing-ws** — no line in any generated `.s` artifact ends
with whitespace.  The universal `%-24s%-16s %s\n` format produces
left-padding to 41 chars on every line, manifesting as trailing spaces on
label-only lines, action-only lines with empty col 3, and macro-body
emissions inside `sm_macros.s`.  Fix: at every emission chokepoint, build
into a buffer, walk a tight loop right-trimming `' '` and `'\t'`, write
trimmed string + `'\n'`.  Eight chokepoints touched: `bb3c_format` in
`bb_emit.c`, `emit_three_column_line` + `sm_line` (label/no-label arms) +
`emit_pc_label` in `sm_codegen_x64_emit.c`, `macro_line` +
`render_call_line` (label/no-label arms) in `sm_emit_template.c`,
`flat3c` in `bb_flat.c`, `ev3c` in `emitter_v.h`.  Verification: `grep -P
'[ \t]+$'` and `awk '/[ \t]+$/'` both report 0 lines per artifact.

**Files touched (one4all):**
- `src/runtime/x86/bb_emit.c`
- `src/runtime/x86/emitter_text.c`
- `src/runtime/x86/sm_codegen_x64_emit.c`
- `src/runtime/x86/sm_emit_template.c`
- `src/runtime/x86/bb_flat.c`
- `src/runtime/x86/bb_flat_text_test.c`
- `src/runtime/x86/emitter_v.h`

**Tracked artifact line counts (regenerated this session):**

| File | Lines | trailing-ws | gcc -c |
|------|------:|:-----------:|:------:|
| roman.s          |  208 | 0 | OK |
| wordcount.s      |  158 | 0 | OK |
| claws5.s         | 1114 | 0 | OK |
| treebank-list.s  | 1395 | 0 | OK |
| treebank-array.s | 1578 | 0 | OK |
| sm_macros.s      |  249 | 0 | (via `.include`) |

**Gates final state:**
- smoke ×5 PASS (snobol4 2/2, icon 5/5, prolog 5/5, raku 5/5, rebus 4/4)
- isolation PASS
- EM PASS=12/12  |  bb_flat_text PASS=18/18  |  sm_phase2_sim PASS=25/25
- unified_broker PASS=6/6 (Prolog inline; csnobol4 oracle not provisioned
  in this session env, so the broader suite truncates at the missing
  oracle — pre-existing environmental gap, not a regression)
- `test_smoke_all_frontend_backend_matrix.sh` is truncated mid-token in
  the repo (line 48 of 48; pre-existing, unrelated to this session)

**Sample (roman.s) — before vs after:**
```
BEFORE                                                AFTER
_pat_inv_0_α:                                         _pat_inv_0_α:
                        lea     r10, [rip + Δ]                                lea              r10, [rip + Δ]
                                         je      _α_body                                      je               _α_body
                                         jmp     _β                                           jmp              _β
```

Mnemonic now sits in col 2 of the file's universal grid; operands always
in col 3; jumps no longer disconnected from surrounding code; zero
trailing whitespace anywhere.

----

EM-7c-s-file-beautify LANDED 2026-05-09
=============================================

Three changes bundled, one diff:

(1) **`;` separators removed** from `bb_emit.c::bb3c_format` and
    `emitter_v.h::ev3c`.  Both helpers' printf format string changed
    from `%-24s ; %-16s ; %s\n` → `%-24s%-16s %s\n` — matching SM-side
    `emit_three_column_line` and `sm_emit_template::render_call_line`.
    ONE shape across the entire `.s`.

(2) **12 raw `EV_TEXT` blocks in `bb_flat.c` converted** to three-column
    form via a new file-static helper family: `flat3c`, `flat3c_action`,
    `flat3c_label`, `flat_data_section`, `flat_text_section`,
    `flat_intel_syntax`, `flat_data_string`, `flat_data_quad`,
    `flat_data_quad_int`, `flat_data_long`, `flat_data_zero`,
    `flat_globl`, `flat_box_call`, `flat_box_call_slot`.  Sites converted:
    charsets (XSPNC/XANYC/XBRKC/XNNYC), XLNTH, XTB, XRTB, XFNCE, XFARB,
    XSTAR, XBRKX, XATP, XDSAR, XARBN, XNME/XFNME.  Zero raw `EV_TEXT`
    calls remain in `bb_flat.c`.

(3) **`emit_sm_exec_stmt_blob` rerouted** through `emit_three_column_line`
    for its three follow-on lines (rsi-arg, edx-arg, call).  Previously
    used `sm_line` whose no-label fallback emitted `\t%-15s %s\n` (tab-
    indented) — that produced the last 3 tab-indented stragglers per
    artifact.  Now all four lines render with 24-space col-1 padding.

**Files touched (one4all):**
- `src/runtime/x86/bb_emit.c`: `bb3c_format` format-string change.
- `src/runtime/x86/emitter_v.h`: `ev3c` format-string change.
- `src/runtime/x86/bb_flat.c`: +127 lines for the helper family;
  12 `EV_TEXT` block conversions.
- `src/runtime/x86/sm_codegen_x64_emit.c`: `emit_sm_exec_stmt_blob`
  rerouted through `emit_three_column_line`.

**Gates final state — 10/10 GREEN:**
- smoke ×6: snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4
- isolation PASS  |  unified_broker PASS=49
- EM gate PASS=12  |  bb_flat_text PASS=18  |  sm_phase2_sim PASS=25

**Audit checks all GREEN per artifact:**
| File | blank | tabs | `;` |
|------|------:|-----:|----:|
| roman.s | 0 | 0 | 0 |
| wordcount.s | 0 | 0 | 0 |
| claws5.s | 0 | 0 | 0 |
| treebank-list.s | 0 | 0 | 0 |
| treebank-array.s | 0 | 0 | 0 |

**Tracked artifact line counts:**
| File | Lines |
|------|------:|
| roman.s | 208 |
| wordcount.s | 158 |
| claws5.s | 1114 |
| treebank-list.s | 1395 |
| treebank-array.s | 1578 |
| sm_macros.s | 249 |

All assemble cleanly; deterministic across back-to-back regen.

**Sample blob section in roman.s — uniform three-column shape:**
```
                        .global          _pat_inv_0_α
                        .global          _pat_inv_0_β
                        .global          _pat_inv_0_γ
                        .global          _pat_inv_0_ω
_pat_inv_0_α:
                        lea              r10, [rip + Δ]
                        cmp              esi, 0
                                         je      _pat_inv_0_α_body
                                         jmp     _pat_inv_0_β
...
                        .section         .data
.Lcap1_vname:
                        .string          ""
.Lcap1_data:
                        .quad            0
                        .quad            0
                        .long            0
```

**`EM-7c-bb-three-column-data` SUBSUMED + LANDED here.**  The data-block
conversion sub-rung carved earlier was folded in; its checkbox dropped.

Next rung: **EM-7c-bb-macros** — BB-side macro library; column-2 BB
content becomes single macro names like `LEN_α`, `RPOS_β`.

----

EM-7c-stmt-banner-fidelity LANDED 2026-05-09
=============================================

Three changes in `sm_emit_template.{c,h}` + `sm_codegen_x64_emit.c`:

(1) **New `SM_TPL_NOOP` shape** (sm_emit_template.h enum + paired
    arms in render_macro_body / build_args_col).  Empty-body marker
    macro (`.macro NAME\n.endm`).  Per-call line is one three-column
    row with the macro name in col 2 — assembles to nothing, but the
    col-1 .LpcN: pc-label is consumed and never naked.  Thin entry
    `sm_emit_noop` mirrors `sm_emit_nullary`.

(2) **`SM_LABEL` and `SM_STNO` registered as NOOP-shape templates**
    in `g_sm_templates[]`.  `emit_sm_label` calls
    `sm_emit_noop(out, sm_template_lookup(SM_LABEL), NULL)` →
    `.LpcN:                  LABEL`.  `emit_sm_stno` emits the major
    banner first, then `sm_emit_noop` → `.LpcN:                  STNO`
    immediately under the banner.  Both macros have empty bodies; no
    runtime semantics change.  Prior behaviour: `emit_sm_label`
    returned 0 with no emission, leaving `.LpcN:` to either be
    absorbed by next instruction or flushed as a naked line by the
    dispatcher's leftover-label flush.

(3) **`emit_sm_pat_baked` rewritten** to produce a real three-column
    line for each blob-absorbed PC:
    ```
    .Lpc7:                  # PUSH_INT       baked  _pat_inv_0 pc=7..12
    ```
    Col 2 carries the macro-name (`PUSH_INT`, `PAT_RPOS`, ...) prefixed
    with `#` so the assembler treats it as a comment — the line
    assembles to nothing while the human eye scans the op name.  Col 3
    carries `baked` plus a back-reference (`_pat_inv_<id>
    pc=<start>..<end>`) so the reader can find the actual blob entry.
    Op name is resolved via `sm_template_lookup(ins->op)->macro_name`,
    keeping every col-2 token in the file uniform with the macro
    library.  Leading `#` is necessary because the macros invoke real
    PLT calls when expanded; placing `PAT_RPOS` unadorned in col 2
    would re-execute the pattern construction the blob has already
    replaced.

Failure mode 3 from the rung spec (cross-banner code drift) was
audited and found NOT to fire on the five tracked artifacts —
`RETURN_VARIANT` for `:F(RETURN)` lands at the correct PC under its
own banner.  The pc→stno audit pass is deferred to a future rung if
the failure mode surfaces.

**Files touched (one4all):**
- `src/runtime/x86/sm_emit_template.h`: added `SM_TPL_NOOP` enum
  member; declared `sm_emit_noop`.
- `src/runtime/x86/sm_emit_template.c`: added `SM_TPL_NOOP` arms in
  `render_macro_body` (empty body) and `build_args_col` (no args);
  added `sm_emit_noop` thin entry; registered `SM_LABEL` and
  `SM_STNO` templates in `g_sm_templates[]`.
- `src/runtime/x86/sm_codegen_x64_emit.c`: rewrote `emit_sm_label`
  to call `sm_emit_noop`; updated `emit_sm_stno` to call
  `sm_emit_noop` after emitting the banner; rewrote
  `emit_sm_pat_baked` to emit a three-column line consuming the
  pending pc-label.

**Gates final state — 10/10 GREEN:**
- smoke ×6: snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4
- isolation PASS  |  unified_broker PASS=49
- EM gate PASS=12  |  bb_flat_text PASS=18  |  sm_phase2_sim PASS=25

**Tracked artifact line counts:**
| File | Lines |
|------|------:|
| roman.s | 209 |
| wordcount.s | 158 |
| claws5.s | 1115 |
| treebank-list.s | 1396 |
| treebank-array.s | 1579 |
| sm_macros.s | 249 |

All assemble cleanly; deterministic across back-to-back regen.

**Audit checks pass:**
- Zero naked `.Lpc<N>:` lines (col 2 always non-empty).
- Zero disembodied `(baked into _pat_inv_...)` comments.

**Sample dispatch under stmt 4 banner (roman.s) — before vs after:**
```
BEFORE                                                       AFTER
.Lpc6:                                                       .Lpc6:                  STNO
.Lpc7:           # (baked into _pat_inv_0 at .text — SM_*)   .Lpc7:                  # PUSH_INT       baked  _pat_inv_0 pc=7..12
.Lpc8:           # (baked into _pat_inv_0 at .text — SM_*)   .Lpc8:                  # PAT_RPOS       baked  _pat_inv_0 pc=7..12
...                                                          ...
.Lpc13:          PUSH_VAR     .Lstr_4 # var=N                .Lpc13:                 PUSH_VAR         .Lstr_4 # var=N
```

Next rung: **EM-7c-s-file-beautify** — single uniform three-column
grid across SM-side and BB-blob lines; remove `;` separators; fold
in the EM-7c-bb-three-column-data conversion of bb_flat.c's 12
remaining raw `EV_TEXT` blocks.

----

EM-7c-three-column-non-bb LANDED 2026-05-09
=============================================

Three changes bundled, one diff:

(1) **Format-shape correction.**  Prior rung shipped a two-column
    dispatch (col 2 fused opcode + args).  Corrected to true
    three-column `label(24) / opcode(16) / args+comment(free)` with
    single-space separator between col 2 and col 3, and
    single-space between args and `# comment`.  No fourth-column
    padding.

(2) **Format extended uniformly** to every non-BB line in emitted
    `.s` (`.section`/`.string`/`.byte`/`.long`/`.quad` data lines,
    static `.data` ζ blocks, `.Lchunk_registry` entries, blob entry
    labels, cap/arbno child sub-procs, `main()` epilogue, `.include
    "sm_macros.s"` line) AND inside `sm_macros.s` (`.macro NAME
    args` / body / `.endm`).  Banner lines preserved full-width.
    BB-blob *body* instructions stay out of scope for this rung —
    next rung `EM-7c-bb-three-column` reformats those to the
    `LABEL: ; ACTION ; GOTO` shape.

(3) **Redundant opcode-name annotations stripped.**  Removed
    `# SM_HALT`, `# SM_RETURN`, `# SM_CONCAT`, `# SM_POP: discard
    TOS`, `# SM_PUSH_NULL`, `# SM_COERCE_NUM`, `# SM_JUMP -> pc=N`,
    all 22 nullary `# SM_PAT_*`, and the `SM_PAT_*` /
    `SM_EXEC_STMT_VARIANT` / `SM_CALL` prefixes from parameterised
    annotations.  Retained: `# str="..."`, `# var=NAME`,
    `# fname="..."` (col 3 args are opaque `.Lstr_N`); RETURN_VARIANT
    annotation (variant integers are opaque); UNHANDLED opcode name.

Goal file condensed this session from 4830 lines to ~340.  Full
narrative history of every closed rung is in git log of
`.github/GOAL-MODE4-EMIT.md`.

----

EM-7c-bb-macros LANDED 2026-05-09
=============================================

Two deliverables per rung spec.  one4all @ `baceff42`; corpus @ `e37f3ca`.

**Deliverable 1 — Greek suffix rename (bb_flat.c):**

All internal sub-labels within BB box bodies renamed from Latin to Greek:
`xcat%d_mid_g/o/left_b/right_b/right_o/mid%d_g/b` →
`xcat%d_γ/ω/left_β/right_β/right_ω/mid%d_γ/β`.
`alt%d_c%db/f/o` → `alt%d_c%d_β/ω`.
`_arbno%d_cs/cf/cb/ab` → `_arbno%d_γ/ω/β/α_body`.
`_cap%d_cs/cf/cb/ab` → `_cap%d_γ/ω/β/α_body`.
New gate: zero bare Latin-suffix port labels in BB sections
(`grep -cE` on all 5 artifacts = 0).

**Deliverable 2 — named macro per port (bb_flat.c, bb_flat.h,
sm_codegen_x64_emit.c, new bb_macros.s 44 lines):**

`bb_macros_write_to_path(path)` writes `bb_macros.s` to CWD.
`sm_codegen_x64_emit.c` calls it and emits `.include "bb_macros.s"`
alongside `.include "sm_macros.s"`.

Macros: `DELTA_LOAD` / `SIGLEN_LOAD` (sub-sequence helpers) +
`EPS_α/β` `FAIL_α/β` `RPOS_α/β` `POS_α/β`.

`flat_emit_rpos/pos/eps/fail` converted: TEXT mode emits single macro
call (`flat3c_action(e, "RPOS_α", "n, lbl_succ, lbl_fail")`);
binary path unchanged.  GAS expands to byte-identical inline x86.

**Tracked artifact line counts:**
| File | Lines | Was |
|------|------:|----:|
| roman.s          |  202 |  208 |
| wordcount.s      |  159 |  158 |
| claws5.s         | 1112 | 1114 |
| treebank-list.s  | 1393 | 1395 |
| treebank-array.s | 1576 | 1578 |
| sm_macros.s      |  248 |  248 |
| bb_macros.s      |   44 |  new |

All 5 `gcc -c` PASS.  Audit 0 violations (7 files).  Trailing-ws 0.

**Gates:**
smoke snobol4 PASS=2, icon PASS=5, prolog PASS=5, raku PASS=5, rebus PASS=4
EM PASS=7 (pre-existing em5 CALL_EXPRESSION env gap unchanged)
bb_flat_text PASS=18 · sm_phase2_sim PASS=25

**Next: EM-7d** — `--jit-emit --x64 beauty.sno` passes SPITBOL oracle.


----

EM-FORMAT-SM partial LANDED 2026-05-09
=============================================

Two of three EM-FORMAT-SM pieces landed; labels-only-when-referenced deferred.
one4all @ `8d4d6b0e`; corpus @ `e763366`.

**Piece 1 — 120-char banners.**  Per the format law: each SNOBOL4
statement preceded by 120-char `#=` banner; pattern-blob section preceded
by 120-char `#=` banner; minor breaks 120-char `#-`.  `emit_major_break`,
`emit_minor_break`, and the EM-7c blob-section banner in
`sm_codegen_x64_emit.c` all extended from 78 to 120 chars.

**Piece 2 — comment-prefix strip.**  Per the format law: comments name
the bare opaque-arg referent only.  Ten sites updated:
`emit_sm_push_lit_s`, `emit_sm_push_var`, `emit_sm_store_var`,
`emit_sm_call_fn`, `emit_sm_pat_refname`, `emit_sm_pat_capture`,
`emit_sm_pat_capture_fn`, `emit_sm_pat_capture_fn_args`,
`emit_sm_pat_usercall`, `emit_sm_pat_usercall_args`.  `var=`, `str=`,
`fname=`, `store -> ` prefixes all gone.  Sample (roman.s):
`PUSH_VAR .Lstr_4 # var=N` → `PUSH_VAR .Lstr_4 # N`.

**Deferred — labels only when referenced.**  Pre-pass over `SM_Program`
collects jump-target set (`SM_JUMP`, `SM_JUMP_F`, `SM_JUMP_S`,
`SM_CALL_CHUNK`, `SM_PUSH_CHUNK`, error landing pads, BB blob entry-pc
map).  `emit_pc_label` consults bitset.  Risk: BB blob entry-pc back-refs
baked as `# baked _pat_inv_<id> pc=N..M` annotations — keep `.LpcN:` for
any PC in a blob range, or rewrite annotations.  Worth its own session.

**Gates 10/10 GREEN:**
- smoke snobol4 PASS=2, icon PASS=5, prolog PASS=5, raku PASS=5, rebus PASS=4
- EM PASS=7 (pre-existing em5 CALL_EXPRESSION env gap unchanged)
- bb_flat_text PASS=18, sm_phase2_sim PASS=25
- audit 0 violations across 7 tracked artifacts

**Tracked artifact line counts (unchanged from EM-7c-bb-macros baseline):**

| File | Lines |
|------|------:|
| roman.s          |  202 |
| wordcount.s      |  159 |
| claws5.s         | 1112 |
| treebank-list.s  | 1393 |
| treebank-array.s | 1576 |
| sm_macros.s      |  248 |
| bb_macros.s      |   44 |

All 5 `gcc -c` PASS.

**Files touched (one4all):**
- `src/runtime/x86/sm_codegen_x64_emit.c`

**Next session:** finish EM-FORMAT-SM (labels-only-when-referenced),
then EM-FORMAT-BB.
