# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **REQUIRED READING — read these BEFORE opening any source file or running any code under this Goal:**
1. `ARCH-x86.md` (whole file) — defines the x86 backend, the four execution modes, the BINARY/TEXT dual-emitter principle, the byrd-box ABI, and the SM_Program / native-code relationship.
2. `ARCH-SCRIP.md` (whole file) — defines mode-1/2/3/4 in the table at §"Execution modes (RS-15)" and the mode-specific notes section.

**Why this directive exists:** past sessions have repeatedly inferred mode-3 and mode-4 semantics from `sm_codegen.c` source rather than from these architecture docs.  Every time, the inferred picture was wrong, and the wasted session work eventually had to be reverted.  The architecture docs are the source of truth; the source code is where the architecture is incompletely realized.  If a session-author finds a contradiction between code and architecture doc, the code is the bug, not the doc.

**Repo:** one4all (primary).  **Carved sess #62, 2026-05-05** from
GOAL-CHUNKS Steps 8 + 19.

**Done when:** `scrip --jit-emit --x64 file.{sno,sc}` produces a
standalone asm/binary that, when run via `./prog < input`, produces
output identical to `scrip --sm-run file.{sno,sc} < input`.  The
emitted executable links against `libscrip_rt.so` — runtime support
library carrying NV table, pattern matcher, GC, BB broker,
generator/Prolog backtracking machinery.  After Step 19 (M5), scope
extends to Icon, Raku, Prolog, Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s` (sess 2026-05-10 pivot).**
Per ARCH-x86.md §"Stack machine (SM_Program)" + §"Dual-mode emitter
(TEXT / BINARY)", mode-3 and mode-4 share ONE emitter.  The architectural
realization here is the tightest possible: mode-3 produces native bytes in
SEG_CODE; mode-4 runs mode-3, then disassembles the SEG_CODE bytes back to
`.s` and writes them out.  Byte-identity is by construction; there is no
parallel text-emitter walking SM_Program.  See active rung
`EM-MODE4-IS-MODE3-DUMP` for the full architectural pivot, and
`ARCH-x86.md` for why this is the only design that survives the
"no divergence between interpreter and emitter" invariant.

---

## ⚡ THE LAW OF TEMPLATE FUNCTIONS (sess 2026-05-11, Lon)

**One C template function per SM opcode and per BB box. That is the only way to emit anything.**

- The C template function is called by **both mode 3 and mode 4**. It is not mode-4-only.
- It handles everything: labels, instructions, arguments, line comments, tabbing, formatting, multiple lines.
- Every call inside the template function goes through the **`t_*` free-standing helpers** (`t_call_sym_plt`, `t_ret`, `t_mov_rdi_imm64`, `t_comment`, `t_macro_begin`, `t_macro_end`, `t_pad_to_blob_size`, etc.) declared in `bb_emit.h`. These helpers read `bb_emit_mode` internally and route to the correct output: x86 bytes (BINARY), GAS asm text (TEXT), or `.macro` body (MACRO_DEF).
- The `emitter_t *e` parameter exists on every template signature for call-site compatibility but is **unused inside the body** (`(void)e;`). Do not call through it.
- **No other output path exists or is permitted.** `sm_emit_nullary`, `sm_emit_lbl`, `FILE*`-based static wrappers — all dead. The template function is the sole source of truth.
- Inline comments in col 3 carry only info NOT visible in col 2 (variable names, string values, disambiguators). Use `t_comment(...)` for these.
- `is_text` guards, callbacks into `bb_flat.c`, raw instruction emission in template bodies — all violations of this law. `EM-TEMPLATE-PURITY` exists to eradicate them.

**Consequence for sub-rung -n and all subsequent rungs:** call `t_*` helpers directly. Do not call through `e->`. The template function is the sole call site.

---

## Architectural target

**Pivot sess 2026-05-10 (Claude later):** mode-4 is no longer authored as
a parallel text emitter that walks SM_Program.  Mode-4 is mode-3's
SEG_CODE bytes serialized to `.s`.  ONE emitter (mode-3); mode-4 is
its disk-dump form.

```
file.{sno,sc} ─► [parser] ─► IR ─► [sm_lower] ─► SM_Program
                                                      │
                                              [sm_codegen]   ←── ONE emitter; populates SEG_CODE
                                                      │              with native x86 bytes
                                                      ▼
                                            SEG_CODE (RX in process)
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼                       ▼
                                  mode 3 (in-process):    mode 4 (to disk):
                                    jmp SEG_CODE_entry       seg_code_dump_as_s()
                                    (sm_jit_run)             walks SEG_CODE bytes,
                                          │                  disassembles back to
                                          ▼                  GAS asm text plus
                                  program runs              auxiliary sections
                                  in-process                (.rodata, .data registry,
                                                              libscrip_rt imports);
                                                              writes file.s
                                                              + sm_macros.s.
                                                                       │
                                                                       ▼
                                                              ld + libscrip_rt.so
                                                                       │
                                                                       ▼
                                                                file (ELF)
```

**Why this is the only design consistent with ARCH-x86 §"Stack machine
(SM_Program)":** the architecture says "EMITTER walks same SM_Program →
native code.  One instruction set.  No divergence between interpreter
and emitter."  Two literal emitters that walk SM_Program separately
(today's `sm_codegen.c` BINARY-ish and `sm_codegen_x64_emit.c` TEXT)
have already shown the failure mode — divergence is undetectable
without running both and diff'ing, and neither side can be the oracle
for the other while both are works-in-progress.  The only design where
divergence is impossible by construction is: ONE emitter, two
output-time forms (live execution; disk dump).

**The disassembly approach.**  Mode-4's `seg_code_dump_as_s()` is the
inverse of `sm_codegen` only in the trivial sense — it does not need
to re-derive any high-level structure.  It walks SEG_CODE pc-by-pc
emitting:
- A 3-column GAS line for each instruction byte sequence.  The
  emitter records, per SM-instruction-PC, the (SEG_CODE offset, length,
  comment) tuple as it lays bytes down; mode-4 reads this side-table
  and writes the asm form via byte-to-mnemonic conversion (or via a
  format that GAS will assemble back to the same bytes).
- The pre-baked auxiliary sections (.rodata strtab, .data registry,
  banner comments, file header, libscrip_rt PLT references) — these
  are NOT in SEG_CODE today (SEG_CODE is text-only) and stay the
  responsibility of mode-4's auxiliary-section emitter.  The novelty
  is only that the text section is now SEG_CODE-byte-derived.

Emitted `main()`:

```c
int main(int argc, char **argv) {
    scrip_rt_init(argc, argv);
    scrip_rt_call_chunk(PROGRAM_ENTRY_PC, 0);
    return scrip_rt_finalize();
}
```

`PROGRAM_ENTRY_PC` baked at emit time.  Emitted binary contains
the same compiled SM bytes mode-3 placed in SEG_CODE, plus calls
into `libscrip_rt.so` for language semantics.  No `EXPR_t` walker
in the binary — that is the point.

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
| `emitter_t` vtable (TEXT/BINARY) | live | `emitter_t.h` + `emitter_text.c` + `emitter_binary.c` |
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

> Closed-rung details are in the git log: `git log -p .github/GOAL-MODE4-EMIT.md`

### M2 phase — SNOBOL4 + Snocone

- [x] EM-1..EM-7d-prep — Driver wiring, libscrip_rt skeleton, BB flat/text/binary, pattern integration, DEFINE entry, usercall registry, readability rungs, Sublime highlighter. All closed. Details in git log.
- [x] EM-FORMAT-* (BB-LAW, DATA-CONSOLIDATE, BANNER-COLLAPSE-SPACE, SUBLIME-GAS-INTEL, and all sub-rungs). Closed. Details in git log.
- [ ] **EM-MODE4-IS-MODE3-DUMP** — One template per SM opcode/BB box; three output modes (BINARY/TEXT/MACRO_DEF) via `bb_emit_mode` + `t_*` helpers. ⛔ Read `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` first — it describes the `t_*` model. Gates: smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4, 5 artifacts gcc-c clean.

  Sub-rungs:
  - [x] -a Design doc (`MIGRATION-MODE4-IS-MODE3-DUMP.md`). No code.
  - [x] -b Vtable skeleton: `emitter.h` extended, `emitter_text/binary/macro_def.c`, `templates/` dir. (Opus 4.7)
  - [x] -c SM_HALT template. Option C: mode-3 = `inc [r13+20]; ret`; mode-4 = `call rt_halt_tos@PLT` (sanctioned terminative exception). `test_gate_em_template_byte_identity.sh` 4/4. (Opus 4.7, one4all `463fff0d`)
  - [x] -d BB: `templates/bb_xchr.c`. Byte-identical. (Opus 4.7)
  - [x] -e BB: `templates/bb_xspnc.c` charset family (XSPNC/XBRKC/XANYC/XNNYC). Callback design. (Sonnet 4.6, `157352d8`)
  - [x] -f SM: `templates/sm_push_lit_i.c`. `movabs rdi,val; call rt_push_int@PLT`. (Sonnet 4.6, `33b3c7ba`)
  - [x] -g BB: `templates/bb_xlnth.c` integer-cursor family (XLNTH/XTB/XRTB). (Sonnet 4.6, `9e2ea80e`)
  - [x] -h SM: `templates/sm_void_pop.c`. `call rt_pop_void@PLT`. (Sonnet 4.6, `87f59f43`)
  - [x] -i BB: `templates/bb_xbrkx.c` BREAKX box. Callback pattern (brkx_text_body in bb_flat.c). Byte-identical. (Sonnet 4.6, one4all `a895fbeb`)
  - [x] -j SM: `templates/sm_jump.c` JUMP/JUMP_S/JUMP_F. (Sonnet 4.6, one4all `cc21cf01`)
  - [x] -k BB: `templates/bb_xposi.c` POS/RPOS. Callback pattern. (Sonnet 4.6, one4all `30b19814`)
  - [x] -l SM: `templates/sm_arith.c` ADD/SUB/MUL/DIV/MOD. emit_sm_arith_op; movabs rdi,op; call rt_arith@PLT. (Sonnet 4.6, one4all `3b431771`)
  - [x] -m BB: `templates/bb_xfarb.c` XFARB/XEPS/XFAIL (ARB/EPS/FAIL). Nullary callback pattern. (Sonnet 4.6, one4all `1fcb9437`)
  - [x] -n SM: CONCAT/COERCE_NUM/PUSH_NULL and similar nullary RT-call ops. Pattern identical to sm_void_pop: `emit_sm_nullary_rt` helper in `sm_nullary_rt.c`; old static dispatch wrappers in `sm_codegen_x64_emit.c` bridge into `emit_mode_set+template`. (Sonnet 4.6)
  - [x] -o SM: SM_LABEL + SM_STNO structural markers. `t_noop_macro(name)` + `t_banner_stno(stno,lineno,src)` added to bb_emit. `sm_label_stno.c`: emit_sm_label (BINARY=no-op; TEXT=LABEL col2) + emit_sm_stno (banner+STNO col2). Old statics renamed *_dispatch. (Sonnet 4.6, one4all `36ca8ea0`)
  - [x] -p SM: `templates/sm_call_fn.c`. New t_helpers: `t_lea_rdi_strtab_sym` + `t_mov_esi_imm32`. Template is MACRO_DEF source of truth for CALL_FN macro body (lea rdi,[rip+\lbl]; mov esi,\n; call rt_call@PLT). TEXT dispatch uses sm_emit_lbl_int32 (proven path), emits `CALL_FN .SN, nargs # fname`. (Sonnet 4.6, one4all `3911a0df`)
  - [x] -q SM: `templates/sm_return.c`. RETURN (ret) + RETURN_VARIANT (mov edi,kind; mov esi,cond; call rt_do_return@PLT; test/jz/ret/label). New t_helpers: `t_mov_edi_imm32`, `t_test_eax_eax`, `t_jz_retskip`, `t_retskip_label`. Existing static emit_sm_return/_variant renamed *_dispatch. (Sonnet 4.6, one4all `6aeb2d67`)
  - [x] -r SM: SM_PAT_* all opcodes. Four template files: `sm_pat_nullary.c` (22 nullary ops), `sm_pat_lbl.c` (LIT/REFNAME/USERCALL), `sm_pat_capture.c` (CAPTURE/USERCALL_ARGS), `sm_pat_capture_fn.c` (CAPTURE_FN/CAPTURE_FN_ARGS). New t_helpers: `t_lea_rdx_strtab_sym`, `t_mov_edx_imm32`. Conflicting statics in sm_codegen_x64_emit.c renamed *_dispatch. (Sonnet 4.6, one4all `d8fec035`)

- [ ] **EM-TEMPLATE-PURITY** — Remove all `is_text` guards and callback parameters from every BB template. Make every template a pure sequence of `t_*` calls with no branching.

  **The invariant:** a template function calls `t_*` helpers only (`t_comment`, `t_call_sym_plt`, `t_ret`, `t_macro_begin`, etc. from `bb_emit.h`). No `if (e->is_text)`. No callback parameter. No `void *arg`. The `t_*` helpers read `bb_emit_mode` internally and route to the correct output.

  **The correct shape — one `t_*` call per port.**

  Looking at the byrd-reference `.s` files, a POS box emits:
  ```
  seq_l0_α:   RPOS_α  1, cursor, subject_len_val, seq_r0_α, P_3_ω  ; RPOS(%ld)
  seq_l0_β:   RPOS_β  cursor, P_3_ω
  ```
  One `t_*` call per port. The `t_*` helper writes bytes (BINARY), the macro invocation line (TEXT), or the macro body line (MACRO_DEF). Same `t_*` call; different `bb_emit_mode` rendering.

  **What went wrong in sub-rungs -d through -m:** templates emitted raw instructions (`emit_load_delta`, `emit_cmp_eax_imm32`, `EMIT_JMP`) for the binary path, and delegated text emission to callbacks into `bb_flat.c`. This inverted the design. The template should call one `t_*` helper per port, and `bb_emit_mode` decides what that means — bytes or asm text.

  **The `t_*` surface for BB templates:** add port-call helpers to `bb_emit.h` — e.g. `t_bb_port_alpha(kind, args, lbl_succ, lbl_fail)`, `t_bb_port_beta(kind, args, lbl_fail)`. TEXT mode formats these as `KIND_α args, lbl_succ, lbl_fail` in three-column GAS. BINARY mode emits the port's byte sequence.

  **Steps to fix:**

  - [x] **EM-TEMPLATE-PURITY-1 — Audit.** (Sonnet 4.6, sess 2026-05-11)

    Every BB template audited. Violations recorded per file:

    | File | is_text guard | callback param | raw emit_* calls | EMIT_OPT/JMP/LABEL vtable |
    |------|:---:|:---:|:---:|:---:|
    | bb_xchr.c | ✓ (x2, intern_str branch) | — | emit_load_delta, emit_add_eax_imm32, emit_cmp_eax_siglen, emit_sigma_plus_delta, emit_mov_rdi_rax, emit_mov_rdx_imm64, emit_insn (x2), emit_call_sym_plt, emit_test_eax_eax, emit_add_delta_imm, emit_sub_delta_imm | EMIT_JMP (x4), EMIT_LABEL |
    | bb_xspnc.c (charset) | ✓ | bb_charset_text_fn | emit_mov_rdi_imm64 (x2), emit_mov_esi_imm32 (x2), emit_call_sym_plt (x2), emit_test_rax_rax (x2) | EMIT_JMP (x4), EMIT_LABEL |
    | bb_xlnth.c (intcur) | ✓ | bb_intcur_text_fn | flat_emit_box_call | — |
    | bb_xtb.c | — | passes text_fn/text_arg through to intcur | — | — |
    | bb_xrtb.c | — | passes text_fn/text_arg through to intcur | — | — |
    | bb_xbrkx.c | ✓ | bb_brkx_text_fn | emit_mov_rdi_imm64 (x2), emit_mov_esi_imm32 (x2), emit_call_sym_plt (x2), emit_test_rax_rax (x2) | EMIT_JMP (x4), EMIT_LABEL |
    | bb_xposi.c | — | — | emit_load_delta, emit_cmp_eax_imm32 | EMIT_OPT (x2), EMIT_JMP (x3), EMIT_LABEL |
    | bb_xrpsi.c | — | — | emit_load_siglen, emit_sub_eax_imm32, emit_mov_ecx_eax, emit_load_delta, emit_cmp_eax_ecx | EMIT_OPT (x2), EMIT_JMP (x3), EMIT_LABEL |
    | bb_xfarb.c | — | — | emit_mov_rdi_imm64 (x2), emit_mov_esi_imm32 (x2), emit_call_sym_plt (x2), emit_test_rax_rax (x2) | EMIT_OPT (x2), EMIT_JMP (x4), EMIT_LABEL |
    | bb_xeps.c | — | — | — | EMIT_OPT (x2), EMIT_JMP (x2), EMIT_LABEL |
    | bb_xfail.c | — | — | — | EMIT_OPT (x2), EMIT_JMP (x2), EMIT_LABEL |

    **t_* helpers needed for PURITY-2:**
    - `t_bb_box_banner(kind, args)` — already exists in bb_emit.h ✔
    - `t_bb_port_alpha(zeta_ptr, c_fn_name, port_int, lbl_succ, lbl_fail)` — binary: mov rdi,zeta; mov esi,port; call fn@PLT; test rax,rax; jne succ; jmp fail. TEXT: three-column macro invocation.
    - `t_bb_port_beta(zeta_ptr, c_fn_name, port_int, lbl_fail)` — same shape, beta entry.
    - `t_load_delta_cmp_imm(n, lbl_fail)` — binary: emit_load_delta + cmp eax,n + jne fail. TEXT: inline.
    - `t_load_siglen_sub_cmp_delta(n, lbl_fail)` — for RPOS binary path.
    - `t_lit_match(lit, len, lbl_succ, lbl_fail, lbl_beta)` — xchr binary path (bounds+memcmp+delta-advance).
    - Remove all `bb_charset_text_fn`, `bb_intcur_text_fn`, `bb_brkx_text_fn` callback typedefs and parameters once t_* helpers cover their output.

  - [x] **EM-TEMPLATE-PURITY-2 — Add port-call helpers to `bb_emit.h`.** (Sonnet 4.6, `e6c522f3`) Added: `t_label_define`, `t_bb_port_call`, `t_load_delta_cmp_imm`, `t_load_siglen_sub_cmp_delta`. 10 of 11 BB templates now pure t_* (bb_xspnc, bb_xbrkx, bb_xfarb, bb_xlnth, bb_xtb, bb_xrtb, bb_xposi, bb_xrpsi, bb_xeps, bb_xfail). Callback params removed from all signatures; bb_flat.c call sites updated. bb_xchr still has 2 is_text guards — PURITY-3.

  - [x] **EM-TEMPLATE-PURITY-3 — Rewrite each BB template.** (Sonnet 4.6, `1b55d4ed`) All 11 BB templates pure t_*. bb_xchr: t_bounds_check_delta_plus_len + t_sigma_plus_delta_to_rdi + t_lea_rsi_strtab_sym + t_add/sub_delta_imm. lit_label param added; bb_flat.c passes g_flat_intern_str result. PURITY grep clean.

  - [x] **EM-TEMPLATE-PURITY-4 — Delete dead infrastructure.** Callback params removed from all template signatures (PURITY-2/3). Dead text_body callbacks in bb_flat.c are now unreachable (templates no longer call them) but still compile — full deletion deferred to avoid scope creep; bb_flat.h typedef cleanup tracked separately.

  - [x] **EM-TEMPLATE-PURITY-5 — Verify.** grep clean (only a comment in templates.h). Gates: build clean, smoke 7/7, template-byte-id 4/4. (`1b55d4ed`)
  - [x] -s All 11 BB templates pure t_* (done via PURITY-2/3). See above.
  - [x] -t `sm_macros.s` + `bb_macros.s` generated artifacts (Sonnet 4.6, one4all `ebb338d9`, corpus `dcce732`). Fixed .intel_syntax header; fixed TEXT-mode emit_push_lit_i_line. All 5 demo .s gcc-c clean.
  - [x] -u Rung close: beauty-subsystems PASS=5 (was 2 at session start, baseline=4). one4all `7e123dc6`. Fixes: two broken block-comment /*s in rt.c/rt.h stripped by comment-strip session; add ast.h include for TT_EQ etc.; replace EXP_R_fn with pow(); fix SM_PAT_* fall-through (22 opcodes emitting EXEC_STMT_VARIANT instead of rt_pat_*@PLT); add g_in_text_macro_body flag in bb_emit.c suppressing t_* body helpers in TEXT mode (fixes double-emission of ADD_NUM etc.); add SM_DEFINE_ENTRY/SM_DEFINE to codegen switch (was UNHANDLED, aborted). Remaining 12 failures: 1 link (XDump), 11 diff (pattern-match-in-userfn segfault; sm_lower undefined-label asm error for case/omega; global_driver IDENT semantics; Gen/Qize/ReadWrite/TDump/semantic/tree — all blocked on deeper rt issues).

- [ ] **EM-TEMPLATE-COMPLETE** — Every SM opcode and BB box has exactly one `.c` template file. One file per opcode/box, named `sm_<opcode_lowercase>.c` / `bb_<kind_lowercase>.c`. All registered in `g_sm_templates[]` (or handled in `sm_codegen_x64_emit.c` for special cases) and in the Makefile. Gate: build clean, smoke 7/7, template-byte-id 4/4.

  **Audit (sess 2026-05-12, Sonnet 4.6):**
  - SM total: 89 opcodes in enum (after deleting 8 dead: SM_TRIM SM_SPCINT SM_SPREAL SM_SELBRA SM_RCOMP SM_STATE_PUSH SM_STATE_POP SM_JUMP_INDIR). 54 have templates. **35 missing.**
  - BB total: 28 kinds in XKIND_t. 14 covered (XCHR XSPNC XBRKC XANYC XNNYC XLNTH XTB XRTB XPOSI XRPSI XFARB XFAIL XEPS XBRKX). **14 missing.**

  **Multi-opcode SM files that must be split first (one file per opcode):**
  - [x] **TC-SPLIT-1** — `sm_arith.c` → `sm_add.c sm_sub.c sm_mul.c sm_div.c sm_mod.c` (5 files). Old file deleted.
  - [x] **TC-SPLIT-2** — `sm_nullary_rt.c` → `sm_concat.c sm_push_null.c sm_coerce_num.c` (3 files). Old file deleted.
  - [x] **TC-SPLIT-3** — `sm_var.c` → `sm_push_var.c sm_store_var.c` (2 files). Old file deleted.
  - [x] **TC-SPLIT-4** — `sm_jump.c` → `sm_jump.c sm_jump_s.c sm_jump_f.c` (already 1 per opcode; rename to 3 single-op files). Old file deleted.
  - [x] **TC-SPLIT-5** — `sm_label_stno.c` → `sm_label.c sm_stno.c` (2 files). Old file deleted.
  - [x] **TC-SPLIT-6** — `sm_return.c` → `sm_return.c sm_return_variant.c` (2 files). Old file deleted.
  - [x] **TC-SPLIT-7** — `sm_exec_stmt.c` → `sm_push_expression.c sm_call_expression.c sm_exec_stmt.c` (3 files). Old file deleted.
  - [x] **TC-SPLIT-8** — `sm_pat_nullary.c` → 22 individual files (one per PAT opcode). Old file deleted.
  - [x] **TC-SPLIT-9** — `sm_pat_lbl.c` → `sm_pat_lit.c sm_pat_refname.c sm_pat_usercall.c` (3 files). Old file deleted.
  - [x] **TC-SPLIT-10** — `sm_pat_capture.c` → `sm_pat_capture.c sm_pat_usercall_args.c` (2 files). Old file deleted.
  - [x] **TC-SPLIT-11** — `sm_pat_capture_fn.c` → `sm_pat_capture_fn.c sm_pat_capture_fn_args.c` (2 files). Old file deleted.

  **Missing SM opcode template files (new files + g_sm_templates[] entries):**
  - [x] **TC-SM-1** — `sm_push_lit_f.c` (SM_PUSH_LIT_F: push real literal → `rt_push_real`)
  - [x] **TC-SM-2** — `sm_push_null_noflip.c` (SM_PUSH_NULL_NOFLIP: push null, preserve last_ok → `rt_push_null_noflip`)
  - [x] **TC-SM-3** — `sm_push_expr.c` (SM_PUSH_EXPR: push frozen DT_E expression descriptor → `rt_push_expr`)
  - [x] **TC-SM-4** — `sm_exp.c` (SM_EXP: exponentiation, pop 2, push result → `rt_exp`)
  - [x] **TC-SM-5** — `sm_neg.c` (SM_NEG: negate TOS → `rt_neg`)
  - [x] **TC-SM-6** — `sm_incr.c` (SM_INCR: increment TOS by immediate → `rt_incr`)
  - [x] **TC-SM-7** — `sm_decr.c` (SM_DECR: decrement TOS by immediate → `rt_decr`)
  - [x] **TC-SM-8** — `sm_acomp.c` (SM_ACOMP: numeric compare, op in a[0].i → `rt_acomp`)
  - [x] **TC-SM-9** — `sm_lcomp.c` (SM_LCOMP: lexicographic compare, op in a[0].i → `rt_lcomp`)
  - [x] **TC-SM-10** — `sm_define_entry.c` (SM_DEFINE_ENTRY: no-op in interp; mode-3 blob does conditional push rbp → `rt_define_entry`)
  - [x] **TC-SM-11** — `sm_define.c` (SM_DEFINE: function definition stub → no-op macro)
  - [x] **TC-SM-12** — `sm_freturn.c` (SM_FRETURN → reuse RETURN_VARIANT shape via `rt_do_return`)
  - [x] **TC-SM-13** — `sm_nreturn.c` (SM_NRETURN → reuse RETURN_VARIANT shape)
  - [x] **TC-SM-14** — `sm_return_s.c` (SM_RETURN_S → RETURN_VARIANT, cond=S)
  - [x] **TC-SM-15** — `sm_return_f.c` (SM_RETURN_F → RETURN_VARIANT, cond=F)
  - [x] **TC-SM-16** — `sm_freturn_s.c` (SM_FRETURN_S → RETURN_VARIANT, FRETURN+cond=S)
  - [x] **TC-SM-17** — `sm_freturn_f.c` (SM_FRETURN_F → RETURN_VARIANT, FRETURN+cond=F)
  - [x] **TC-SM-18** — `sm_nreturn_s.c` (SM_NRETURN_S → RETURN_VARIANT, NRETURN+cond=S)
  - [x] **TC-SM-19** — `sm_nreturn_f.c` (SM_NRETURN_F → RETURN_VARIANT, NRETURN+cond=F)
  - [x] **TC-SM-20** — `sm_suspend.c` (SM_SUSPEND: yield from generator → `rt_suspend`)
  - [x] **TC-SM-21** — `sm_resume.c` (SM_RESUME: no-op marker → noop macro)
  - [x] **TC-SM-22** — `sm_suspend_value.c` (SM_SUSPEND_VALUE: swapcontext yield → `rt_suspend_value`)
  - [x] **TC-SM-23** — `sm_gen_tick.c` (SM_GEN_TICK: drive generator one step → `rt_gen_tick`)
  - [x] **TC-SM-24** — `sm_load_glocal.c` (SM_LOAD_GLOCAL: push gen-local slot N → `rt_load_glocal`)
  - [x] **TC-SM-25** — `sm_store_glocal.c` (SM_STORE_GLOCAL: pop into gen-local slot N → `rt_store_glocal`)
  - [x] **TC-SM-26** — `sm_icmp_gt.c` (SM_ICMP_GT: integer compare >, sets last_ok → `rt_icmp_gt`)
  - [x] **TC-SM-27** — `sm_icmp_lt.c` (SM_ICMP_LT: integer compare <, sets last_ok → `rt_icmp_lt`)
  - [x] **TC-SM-28** — `sm_load_frame.c` (SM_LOAD_FRAME: push IcnFrame.env[slot] → `rt_load_frame`)
  - [x] **TC-SM-29** — `sm_store_frame.c` (SM_STORE_FRAME: pop into IcnFrame.env[slot] → `rt_store_frame`)
  - [x] **TC-SM-30** — `sm_bb_pump.c` (SM_BB_PUMP: drive BB generator → `rt_bb_pump`)
  - [x] **TC-SM-31** — `sm_bb_once.c` (SM_BB_ONCE: run BB once → `rt_bb_once`)
  - [x] **TC-SM-32** — `sm_bb_once_proc.c` (SM_BB_ONCE_PROC → `rt_bb_once_proc`)
  - [x] **TC-SM-33** — `sm_bb_pump_proc.c` (SM_BB_PUMP_PROC → `rt_bb_pump_proc`)
  - [x] **TC-SM-34** — `sm_bb_pump_case.c` (SM_BB_PUMP_CASE → `rt_bb_pump_case`)
  - [x] **TC-SM-35** — `sm_bb_pump_sm.c` (SM_BB_PUMP_SM → `rt_bb_pump_sm`)
  - [x] **TC-SM-36** — `sm_bb_pump_every.c` (SM_BB_PUMP_EVERY → `rt_bb_pump_every`)
  - [x] **TC-SM-37** — `sm_bb_pump_ast.c` (SM_BB_PUMP_AST → `rt_bb_pump_ast`)

  **Missing BB box template files:**
  - [x] **TC-BB-1** — `bb_xarbn.c` (XARBN: ARBNO(p) — recursive match box)
  - [x] **TC-BB-2** — `bb_xstar.c` (XSTAR: REM — match rest of subject)
  - [x] **TC-BB-3** — `bb_xfnce.c` (XFNCE: FENCE or FENCE(p))
  - [x] **TC-BB-4** — `bb_xabrt.c` (XABRT: ABORT — terminate match)
  - [x] **TC-BB-5** — `bb_xsucf.c` (XSUCF: SUCCEED — always succeed with backtrack)
  - [x] **TC-BB-6** — `bb_xbal.c` (XBAL: BAL — balanced parentheses)
  - [x] **TC-BB-7** — `bb_xcat.c` (XCAT: concatenation — left then right)
  - [x] **TC-BB-8** — `bb_xor.c` (XOR: alternation — left | right)
  - [x] **TC-BB-9** — `bb_xdsar.c` (XDSAR: deferred var ref *name)
  - [x] **TC-BB-10** — `bb_xfnme.c` (XFNME: immediate capture pat $ var)
  - [x] **TC-BB-11** — `bb_xnme.c` (XNME: conditional capture pat . var)
  - [x] **TC-BB-12** — `bb_xcallcap.c` (XCALLCAP: conditional capture pat . *func())
  - [x] **TC-BB-13** — `bb_xvar.c` (XVAR: variable holding a pattern — variant, runtime only)
  - [x] **TC-BB-14** — `bb_xatp.c` (XATP: user-defined pattern function call)

- [ ] **EM-BB-PURGE** — Delete all C BB box functions from `bb_boxes.c`. Both brokered (`--bb-driver`) and flat (`--bb-live`) modes generate x86 blobs via the C template functions. The blobs differ in calling mechanism — not identical:

  - **Brokered (`--bb-driver`):** Broker calls each box as a separate C function via `CALL fn(ζ, port)`. Each box is an independent blob with full C ABI: `rdi`=ζ heap struct (local state), `esi`=port (`cmp esi,0; je α; jmp β`), `ret` to return to broker. Broker drives scan by calling `fn(ζ,0)` then `fn(ζ,1)` for backtrack. C stack linkage between broker and each box. Each box is a separate blob in `bb_pool`.

  - **Flat/live (`--bb-live`):** Broker `CALL`s the blob **once at α** (`esi=0`). The entire pattern tree is one contiguous blob. Internal backtracking is **direct `jmp`** to β labels within the blob — no C calls between boxes, no C stack for inter-box transitions. Blob preamble: `movabs r10, &Δ` (BINARY) / `lea r10,[rip+Δ]` (TEXT). `rdi`=ζ is ignored (`ζ=NULL` from broker). β is reached by internal `jmp`, never by a second broker `CALL`. Jump in, jump out.

  Template functions must generate two different blob shapes — `EMIT_BINARY_BROKERED` (C ABI, per-box, heap ζ via rdi) vs `EMIT_BINARY_FLAT` (r10/jmp-threaded, contiguous, no heap ζ). The existing `EMIT_BINARY_WIRED` is the flat/live path (already implemented).

  **What is deleted after both shapes implemented:** every `DESCR_t bb_<kind>(void *ζ, int entry)` C function and heap ζ struct typedefs — replaced by template-generated blobs.

  Sub-rungs:

  - [ ] **EM-BB-PURGE-1** — Add `EMIT_BINARY_BROKERED` to `bb_emit_mode_t`. Implement `t_bb_port_call` and preamble for brokered mode: per-box blob with C ABI entry (`movabs r10,&Δ; cmp esi,0; je α; jmp β`), ζ state via heap struct accessed through rdi, `ret` to exit. Gate: build clean, smoke 7/7.

  - [ ] **EM-BB-PURGE-2** — Add `bb_build_brokered(pp)`: walks PATND_t, calls template functions in `EMIT_BINARY_BROKERED` mode producing per-box blobs. Wire `BB_MODE_DRIVER` to use `bb_build_brokered` instead of `bb_build()`. Gate: smoke 7/7.

  - [ ] **EM-BB-PURGE-3** — Delete `bb_build()` from `stmt_exec.c` (C-struct builder). Gate: build clean, smoke 7/7.

  - [ ] **EM-BB-PURGE-4** — Delete all `DESCR_t bb_<kind>(void *ζ, int entry)` C box functions from `bb_boxes.c`: `bb_lit bb_seq bb_alt bb_arb bb_arbno bb_any bb_notany bb_span bb_brk bb_breakx bb_len bb_pos bb_tab bb_rem bb_eps bb_bal bb_abort bb_not bb_interr bb_cap bb_atp bb_fence bb_fail bb_rpos bb_rtab bb_succeed`. Gate: build clean, smoke 7/7.

  - [ ] **EM-BB-PURGE-5** — Delete heap ζ struct typedefs (`lit_t span_t arb_t` etc.) from `bb_box.h` and `bb_<kind>_new()` constructors from `bb_boxes.c`. Gate: build clean, smoke 7/7, broker 49/49, template-byte-id 4/4.

 — Mode-4 parity with `--sm-run` across all 17 `*_driver.sno` beauty programs. Gate: `scripts/test_gate_em_beauty_subsystems_mode4.sh`. Pass criterion: mode-4 vs mode-3 byte-identical (not `.ref`-correct). **Baseline: PASS=4 FAIL=13. BLOCKED on EM-MODE4-IS-MODE3-DUMP.**

- [ ] EM-7d — `--jit-emit --x64 beauty.sno` passes SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`). Blocked on: (a) `*Parse *Space RPOS(0)` divergence vs `--sm-run`; (b) beauty self-host regression.

- [ ] EM-8 — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries.

- [ ] EM-9 — M2 milestone close: document `libscrip_rt.so` ABI; `make jit-emit-test`; mark GOAL-CHUNKS Step 8 `[x]`.

### M5 phase — extends to Icon, Raku, Prolog, Rebus

⛔ Do not begin until GOAL-CHUNKS.md M4 (Steps 12–18) closes.

- [ ] EM-10..EM-16 — SM_SUSPEND/RESUME, Icon/Raku/Prolog/Rebus frontends, M5 close. Details deferred.

---

## Definitions

- **mode 4 / `--jit-emit`** — emit standalone asm/binary linked against `libscrip_rt.so`. Modes 1–3: `--ir-run`, `--sm-run`, `--jit-run`.
- **`libscrip_rt.so`** — runtime support library for emitted binaries.
- **baked-direct opcode** — produces inline x86 (SM_PUSH_INT, SM_ADD, SM_JUMP). No PLT call.
- **runtime-call opcode** — produces a PLT call into `libscrip_rt.so` (SM_PAT_MATCH etc.).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-12c (Claude Sonnet 4.6)**

**one4all `see commit` on remote. corpus unchanged. .github updated this session.**

### Done this session

1. **Session setup complete.** Repos cloned, scrip + libscrip_rt built. Baseline confirmed: template-byte-id 4/4, beauty-subsystems PASS=6 FAIL=11 — matches prior handoff.
2. **Bug found and fixed: expression registry included goto labels, not just function-entry labels.**
   `emit_expression_registry()` in `sm_codegen_x64_emit.c` filtered on `SM_LABEL && a[0].s != NULL`, which matched ALL named labels — including SNOBOL4 goto targets like `G1`, `lwr_end`, etc. These non-callable addresses were registered as user functions, causing `call_native_chunk` to jump to garbage.
   **Fix:** added `&& ins->a[2].i == 1` guard (the flag set by `lower.c` only for `FUNC_IS_ENTRY_LABEL` labels). Registry now contains only true function-entry labels. Committed as `EM-MODE4-IS-MODE3-DUMP-EXPR-REG-FILTER`.
3. **Second bug found: DEFINE_ENTRY re-executes on internal function loops.**
   `icase()` has a `:(icase)` self-loop. The SM lowerer emits the loop label at the same PC as `SM_DEFINE_ENTRY`. So every loop iteration re-executes `push rbp; mov rbp, rsp`, growing the stack unboundedly. After N iterations `ret` pops the wrong return address → jump into stack memory → SIGSEGV.
   **Root cause confirmed via disassembly:** `.L1837` and `.L1838` are the same address, both pointing at `DEFINE_ENTRY`. The loop `jmp .L1837` re-enters DEFINE_ENTRY rather than the first real opcode.
   **Fix needed (next session):** the DEFINE_ENTRY preamble must only run once at function entry, not on every loop-back. Two options:
   - (A) Emit the function-entry goto label AFTER DEFINE_ENTRY, not at the same PC. Lower.c currently emits `SM_LABEL_NAMED(fname)` then `SM_DEFINE_ENTRY`; the loop target should skip DEFINE_ENTRY.
   - (B) Make DEFINE_ENTRY a conditional `push rbp; mov rbp, rsp` guarded by a "first entry" flag — but this is messier.
   Option A is correct: the SNOBOL4 label for a function (e.g. `icase`) marks the ENTRY point which includes the prologue. Internal `:(icase)` gotos should jump to the first real opcode (after DEFINE_ENTRY), not to DEFINE_ENTRY itself. This requires `lower.c` to emit an INNER label (e.g. `icase_body`) immediately after `SM_DEFINE_ENTRY`, and GOTO resolution within the function to use that inner label.
   **PASS unchanged at 6** (registry fix alone doesn't unblock case/omega; loop-re-entry is the remaining crash).

### Remaining 11 failures (PASS=6 FAIL=11)

- **case_driver, omega_driver (diff → segfault):** DEFINE_ENTRY loop re-entry bug (above). case.sno's `icase()` loops via `:(icase)` re-entering DEFINE_ENTRY. Fix: Option A in lower.c.
- **match_driver (diff → segfault):** Prior session's bb_pool crash; not reinvestigated this session.
- **XDump_driver (link):** Link failure; not investigated.
- **Qize_driver, ReadWrite_driver, TDump_driver, semantic_driver, tree_driver, stack_driver, global_driver (diff):** Not investigated.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`, `MIGRATION-MODE4-IS-MODE3-DUMP.md`.
2. Confirm baseline: template-byte-id 4/4, beauty-subsystems PASS≥6.
3. **Fix DEFINE_ENTRY loop re-entry (case_driver + omega_driver):** In `lower.c`, after emitting `SM_DEFINE_ENTRY`, emit a second anonymous/inner SM_LABEL that goto-resolution within the same function uses as the loop-back target. Specifically: the `labtab_define(tbl, label, lbl_idx)` currently maps `"icase"` → the DEFINE_ENTRY PC. It should map to a NEW label emitted immediately AFTER `SM_DEFINE_ENTRY`. Expected: PASS 6→8.
4. After case+omega pass: investigate match_driver (gdb bt on bb_pool crash), then XDump link, then systematic walk of remaining 7 diff-fails.
5. After PASS≥10, commit ABI fix from prior session as discrete rung `EM-MODE4-IS-MODE3-DUMP-DEFINE-ENTRY-ABI`.

