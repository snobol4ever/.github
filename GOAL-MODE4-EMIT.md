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
  - [~] **TC-SPLIT-1** — `sm_arith.c` → `sm_add.c sm_sub.c sm_mul.c sm_div.c sm_mod.c` (5 files). Old file deleted. *Superseded by TC-UNSPLIT-1 (sess 2026-05-12g).*
  - [~] **TC-SPLIT-2** — `sm_nullary_rt.c` → `sm_concat.c sm_push_null.c sm_coerce_num.c` (3 files). Old file deleted. *Superseded by TC-UNSPLIT-2 (sess 2026-05-12g). Note: `sm_nullary_rt.c` was later renamed to `sm_rtcall.c` in commit 980e2d1c; that bundle is the source of truth.*
  - [~] **TC-SPLIT-3** — `sm_var.c` → `sm_push_var.c sm_store_var.c` (2 files). Old file deleted. *Superseded by TC-UNSPLIT-3.*
  - [~] **TC-SPLIT-4** — `sm_jump.c` → `sm_jump.c sm_jump_s.c sm_jump_f.c` (already 1 per opcode; rename to 3 single-op files). Old file deleted. *Superseded by TC-UNSPLIT-4 (sess 2026-05-12g).*
  - [~] **TC-SPLIT-5** — `sm_label_stno.c` → `sm_label.c sm_stno.c` (2 files). Old file deleted. *Superseded by TC-UNSPLIT-5.*
  - [~] **TC-SPLIT-6** — `sm_return.c` → `sm_return.c sm_return_variant.c` (2 files). Old file deleted. *Superseded by TC-UNSPLIT-6 (sess 2026-05-12g). Also folds back in the 8 conditional return per-ops created fresh in commit 3cc8b399 (sm_freturn, sm_nreturn, sm_return_s, sm_return_f, sm_freturn_s, sm_freturn_f, sm_nreturn_s, sm_nreturn_f).*
  - [~] **TC-SPLIT-7** — `sm_exec_stmt.c` → `sm_push_expression.c sm_call_expression.c sm_exec_stmt.c` (3 files). Old file deleted. *Superseded by TC-UNSPLIT-7 (sess 2026-05-12g).*
  - [~] **TC-SPLIT-8** — `sm_pat_nullary.c` → 22 individual files (one per PAT opcode). Old file deleted. *Superseded by TC-UNSPLIT-8 (sess 2026-05-12g). `sm_pat_nullary.c` was later renamed to `sm_pat_rtcall.c` in commit 980e2d1c; that bundle is the source of truth.*
  - [~] **TC-SPLIT-9** — `sm_pat_lbl.c` → `sm_pat_lit.c sm_pat_refname.c sm_pat_usercall.c` (3 files). Old file deleted. *Superseded by TC-UNSPLIT-9 (per-op files were never actually created).*
  - [~] **TC-SPLIT-10** — `sm_pat_capture.c` → `sm_pat_capture.c sm_pat_usercall_args.c` (2 files). Old file deleted. *Superseded by TC-UNSPLIT-10 (per-op file was never actually created).*
  - [~] **TC-SPLIT-11** — `sm_pat_capture_fn.c` → `sm_pat_capture_fn.c sm_pat_capture_fn_args.c` (2 files). Old file deleted. *Superseded by TC-UNSPLIT-11 (per-op file was never actually created).*

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

- [ ] **TC-UNSPLIT** — Reverse over-eager file splits.  The Law of Template Functions
  (sess 2026-05-11) requires "one C template **function** per SM opcode and per BB box."
  It does NOT require one **file** per opcode.  TC-SPLIT-1 through TC-SPLIT-11 over-applied
  the Law at the file level and produced fragmentation without architectural benefit, plus
  an inconsistent on-disk state: some bundle files remain in `src/runtime/x86/templates/`
  but are orphaned (not in Makefile, defining duplicate symbols of the per-op files).
  For SPLITs 9/10/11, the per-op files were never created — the rungs were marked `[x]`
  prematurely; the bundle files remain on disk but unbuilt; legacy `g_sm_templates[]`
  dispatch via SM_TPL_LBLOPT covers the opcodes through the macro-table path.

  **Pre-existing state audit (HEAD `c9b7428d`, sess 2026-05-12 Opus 4.7):**

  | TC-SPLIT | Bundle file | Per-op files | In Makefile | Status |
  |----------|-------------|--------------|-------------|--------|
  | -1 sm_arith.c | exists (helper-only: `emit_sm_arith_op`) | sm_add/sub/mul/div/mod.c (5) | per-op | OK — bundle is a helper, not a duplicate; leave as-is |
  | -2 sm_nullary_rt.c | DELETED | sm_concat/push_null/coerce_num.c (3) | per-op | OK — fully split, delete confirmed |
  | -3 sm_var.c | EXISTS, ORPHAN | sm_push_var.c / sm_store_var.c | per-op | **BROKEN** — bundle is dead code with duplicate symbols |
  | -4 sm_jump.c | repurposed (single op) | sm_jump_s.c / sm_jump_f.c | all three | OK |
  | -5 sm_label_stno.c | EXISTS, ORPHAN | sm_label.c / sm_stno.c | per-op | **BROKEN** — bundle dead, duplicate symbols |
  | -6 sm_return.c | repurposed (single op) | sm_return_variant.c | both | OK |
  | -7 sm_exec_stmt.c | repurposed (single op) | sm_push_expression.c / sm_call_expression.c | all three | OK |
  | -8 sm_pat_nullary.c | DELETED | 22 individual sm_pat_*.c | per-op | OK |
  | -9 sm_pat_lbl.c | EXISTS, ORPHAN | sm_pat_lit/refname/usercall.c — **DO NOT EXIST** | — | **NEVER ACTUALLY DONE** — bundle dead; dispatch via SM_TPL_LBLOPT table-only |
  | -10 sm_pat_capture.c | EXISTS, ORPHAN | sm_pat_usercall_args.c — **DOES NOT EXIST** | — | **NEVER ACTUALLY DONE** |
  | -11 sm_pat_capture_fn.c | EXISTS, ORPHAN | sm_pat_capture_fn_args.c — **DOES NOT EXIST** | — | **NEVER ACTUALLY DONE** |

  **Decision (sess 2026-05-12, Lon):** unsplit.  "One template function per opcode" is
  the binding rule; file count is incidental.  Restore the bundle files as the source of
  truth for each group; delete the per-op fragments where they exist.

  **Per-rung procedure (apply to each TC-UNSPLIT-N below):**

  1. **Git-archaeology each function in the bundle.**  For each `emit_sm_*` function the
     bundle should contain, run `git log --all -p -- src/runtime/x86/templates/<file>` and
     `git log --all -p -S 'emit_sm_<opcode>'` to find every commit that touched it.  The
     latest version of each function body wins.  This step is required because:
     - Some functions were edited inside the bundle before the split.
     - Some functions were edited inside the per-op file after the split.
     - Some functions exist in both with different bodies (especially `sm_var.c` /
       `sm_label_stno.c` / `sm_pat_lbl.c` / `sm_pat_capture.c` / `sm_pat_capture_fn.c`
       which retained their pre-split content while per-op files were also added).
     Walk every relevant commit; pick the implementation with the latest meaningful
     edit per function.  If both edited concurrently, prefer the per-op file (it was
     the active build artifact).

  2. **Rewrite the bundle `.c` file** containing all `emit_sm_*` functions for the group,
     each at its latest version per step 1, plus any shared helper used only inside the
     group (e.g. `emit_sm_lbl_rt` inside `sm_var.c`).

  3. **Delete the per-op fragments** with `git rm` (for files that exist on disk).

  4. **Update `Makefile`:** remove every `$(RT)/x86/templates/sm_<perop>.c` source-list
     entry AND every `$(CC) -c $(RT)/x86/templates/sm_<perop>.c -o $(OBJ)/template_sm_<perop>.o`
     recipe line for the per-op files; add the bundle `.c` if not already listed.

  5. **Rebuild scrip + libscrip_rt:** `bash scripts/build_scrip.sh && make libscrip_rt`.
     Both must succeed clean.

  6. **Gate** before commit: `bash scripts/test_smoke_snobol4.sh` (PASS=7),
     `bash scripts/test_gate_em_template_byte_identity.sh` (PASS=4),
     `bash scripts/test_smoke_snocone.sh` (PASS=5),
     `bash scripts/test_gate_em_beauty_subsystems_mode4.sh` (PASS≥6).

  Sub-rungs:

  - [x] **TC-UNSPLIT-3** — `sm_var.c` is the source of truth.  Keep `emit_sm_lbl_rt`
    static helper plus `emit_sm_push_var` + `emit_sm_store_var`.  Delete
    `templates/sm_push_var.c` + `templates/sm_store_var.c`.  Update Makefile:
    remove the two per-op entries; add `$(RT)/x86/templates/sm_var.c` source-list
    entry and matching recipe line.

  - [x] **TC-UNSPLIT-5** — `sm_label_stno.c` is the source of truth.  Keep
    `emit_sm_label` + `emit_sm_stno`.  Delete `templates/sm_label.c` +
    `templates/sm_stno.c`.  Update Makefile per step 4.

  - [x] **TC-UNSPLIT-9** — `sm_pat_lbl.c` is the source of truth (only place these
    functions exist).  Verify it contains `emit_sm_pat_lit`, `emit_sm_pat_refname`,
    `emit_sm_pat_usercall` (or whatever names the bundle currently uses).  No per-op
    files to delete (they were never created).  Add `$(RT)/x86/templates/sm_pat_lbl.c`
    to Makefile and recipe.  After this rung, the SM_TPL_LBLOPT table dispatch and
    the template-function path both reach the same code.

  - [x] **TC-UNSPLIT-10** — `sm_pat_capture.c` source of truth.  Verify it contains
    both `emit_sm_pat_capture` + `emit_sm_pat_usercall_args`.  Add to Makefile.

  - [x] **TC-UNSPLIT-11** — `sm_pat_capture_fn.c` source of truth.  Verify it
    contains both `emit_sm_pat_capture_fn` + `emit_sm_pat_capture_fn_args`.
    Add to Makefile.

  - [x] **TC-UNSPLIT-1** *(sess 2026-05-12g)* — `sm_arith.c` source of truth: 5 emit
    functions (`emit_sm_add/sub/mul/div/mod`) + non-static `emit_sm_arith_op` helper.
    Deleted: `sm_add.c sm_sub.c sm_mul.c sm_div.c sm_mod.c`.  Duplicate
    `emit_sm_arith_op` removed from `sm_helpers.c`.

  - [x] **TC-UNSPLIT-2** *(sess 2026-05-12g)* — `sm_rtcall.c` source of truth (formerly
    `sm_nullary_rt.c`, renamed in commit 980e2d1c).  Already contained 3 emit functions
    (`emit_sm_concat/push_null/coerce_num`) + static `emit_sm_rtcall` helper.  Deleted:
    `sm_concat.c sm_push_null.c sm_coerce_num.c`.

  - [x] **TC-UNSPLIT-4** *(sess 2026-05-12g)* — `sm_jump.c` source of truth: 3 emit
    functions (`emit_sm_jump/jump_s/jump_f`) + static `make_pc_label` helper (restored
    from pre-split state in commit accf4477^).  Deleted: `sm_jump_s.c sm_jump_f.c`.

  - [x] **TC-UNSPLIT-6** *(sess 2026-05-12g)* — `sm_return.c` source of truth: 10 emit
    functions: `emit_sm_return`, `emit_sm_return_variant`, plus the 8 conditional
    return wrappers (`emit_sm_freturn`, `emit_sm_nreturn`, `emit_sm_return_s/_f`,
    `emit_sm_freturn_s/_f`, `emit_sm_nreturn_s/_f`).  The 8 conditional returns were
    NEW templates added by commit 3cc8b399 (not pre-split bundle content), but per
    the binding rule "one C template function per opcode; file count is incidental"
    they all live in `sm_return.c`.  Deleted: `sm_return_variant.c sm_freturn.c
    sm_nreturn.c sm_return_s.c sm_return_f.c sm_freturn_s.c sm_freturn_f.c
    sm_nreturn_s.c sm_nreturn_f.c` (9 files total).

  - [x] **TC-UNSPLIT-7** *(sess 2026-05-12g)* — `sm_exec_stmt.c` source of truth: 3 emit
    functions (`emit_sm_push_expression`, `emit_sm_call_expression`, `emit_sm_exec_stmt`)
    restored from pre-split state in commit accf4477^.  Deleted: `sm_push_expression.c
    sm_call_expression.c`.

  - [x] **TC-UNSPLIT-8** *(sess 2026-05-12g)* — `sm_pat_rtcall.c` source of truth
    (formerly `sm_pat_nullary.c`, renamed in commit 980e2d1c).  Already contained 22
    emit functions (`emit_sm_pat_eps/arb/rem/fail/succeed/abort/bal/fence/fence1/
    span/break/any/notany/len/pos/rpos/tab/rtab/arbno/cat/alt/deref`) + static
    `emit_sm_pat_rtcall` helper.  Deleted 22 per-op files: `sm_pat_abort.c
    sm_pat_alt.c sm_pat_any.c sm_pat_arb.c sm_pat_arbno.c sm_pat_bal.c sm_pat_break.c
    sm_pat_cat.c sm_pat_deref.c sm_pat_eps.c sm_pat_fail.c sm_pat_fence0.c
    sm_pat_fence1.c sm_pat_len.c sm_pat_notany.c sm_pat_pos.c sm_pat_rem.c
    sm_pat_rpos.c sm_pat_rtab.c sm_pat_span.c sm_pat_succeed.c sm_pat_tab.c`.

  - [x] **TC-UNSPLIT-CLOSE** — After 3/5/9/10/11 close, flip TC-SPLIT-3/5/9/10/11
    from `[x]` to `[~]` (with note `superseded by TC-UNSPLIT-N`).  Leave TC-SPLIT-1/2/4/6/7/8
    as `[x]` — those were genuinely correct splits.  Confirm
    `find src/runtime/x86/templates -name 'sm_*.c' | wc -l` decreases by 8
    (= 4 deleted per-op for SPLIT-3/5 × 2; no deletions for 9/10/11 since per-op
    files never existed). *Actual delta sess 2026-05-12f: -4, not -8 (93→89). The
    "-8" in the original rung text was a miscount; SPLIT-3 deletes 2 per-op files
    (sm_push_var, sm_store_var) and SPLIT-5 deletes 2 (sm_label, sm_stno) = 4 total.
    9/10/11 deleted 0 files (per-op never existed). All five bundles (sm_var.c,
    sm_label_stno.c, sm_pat_lbl.c, sm_pat_capture.c, sm_pat_capture_fn.c) now wired
    into Makefile. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5,
    beauty-subsystems mode4 PASS=6 FAIL=11 (baseline preserved).*

    *Reopened and extended sess 2026-05-12g: Lon corrected the audit's
    "OK — leave as-is" verdicts for TC-SPLIT-1/2/4/6/7/8.  The binding rule applies
    uniformly to all splits, not just the orphan-bundle cases.  Extended scope:
    TC-UNSPLIT-1/2/4/6/7/8 added above.  After all 11 unsplits: 43 additional per-op
    files deleted in sess 2026-05-12g (89 → 46 sm_*.c template files).  Total
    cumulative delta from peak-split state: 89 - 46 = 43 (sess 2026-05-12g) plus
    -4 (sess 2026-05-12f) = -47 from the 93-file peak that existed at HEAD
    `c9b7428d`.  All eleven TC-SPLITs are now `[~]` (superseded).  Gates remain:
    smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty-subsystems mode4 PASS=6
    FAIL=11 (baseline preserved across both sessions).*

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

- [ ] **EM-DOPPELGANGER-PURGE** — Now that `sm_templates.c` and `bb_templates.c` are the single source of truth (sess 2026-05-12h, 91 SM emitters + 35 BB emitters covering all SM_t and XKIND_t entries), eradicate every parallel SM-opcode / BB-box emission path that still exists outside those two files.  Final result: deleting any template function from `sm_templates.c` / `bb_templates.c` either breaks the corresponding opcode's emission, or — better — fails the link with "undefined reference".  No silent fallback paths.

  **Suspects (sess 2026-05-12h inventory):**
  - `src/runtime/x86/sm_codegen.c` — mode-3 byte emitter; per-opcode inline emission.
  - `src/runtime/x86/sm_codegen_x64_emit.c` — mode-4 text emitter; per-opcode inline emission; also hosts the legacy `g_sm_templates[]` macro-table dispatch (SM_TPL_LBLOPT etc.).
  - `src/runtime/x86/sm_emit_template.c` — bridge between `g_sm_templates[]` and templates; contains `render_macro_body` / `render_call_line` that produce parallel output to template functions.
  - `src/runtime/x86/bb_flat.c` — `flat_emit_eps`, `flat_emit_fail`, `flat_emit_pos`, `flat_emit_rpos`, `flat_emit_arb`, `flat_emit_fence`, `flat_emit_rem`, `flat_emit_atp`, `flat_emit_dvar`, etc. per-XKIND helpers.
  - `src/runtime/x86/bb_build.c` — `bb_lit_emit_binary`, `bb_build_binary_node`, C-struct BB tree builder.
  - `src/runtime/x86/bb_boxes.c` — 26 C-function BB boxes (`bb_lit`, `bb_span`, `bb_arb`, ...).
  - `src/runtime/x86/bb_box.h` — heap ζ struct typedefs (`lit_t`, `span_t`, `arb_t`, ...) and `bb_<kind>_new()` constructors.
  - `Makefile` `-Wl,--allow-multiple-definition` — the smoking gun that tells us doppelgangers exist.

  **Gate after every sub-rung:**
  - `test_smoke_snobol4.sh` PASS=7
  - `test_gate_em_template_byte_identity.sh` PASS=4 (byte-identical mode-3 vs mode-4)
  - `test_smoke_snocone.sh` PASS=5
  - `test_smoke_unified_broker.sh` no regression
  - `test_gate_em_beauty_subsystems_mode4.sh` ≥ PASS=7

  **The template-byte-id gate is the lynchpin:** if deleting a doppelganger changes emission bytes, the doppelganger WAS the live path and the template needs to match its output first.

  Sub-rungs:

  - [x] **EDP-1 — Audit script.**  Write `scripts/util_audit_doppelgangers.sh` that walks the `SM_t` enum in `sm_prog.h` and the `XKIND_t` enum in `snobol4_patnd.h`, greps `src/runtime/x86/*.c` for `case SM_<X>:` / `case X<X>:` and `emit_sm_<x>` / `emit_bb_<x>` occurrences, and reports file:line for every match outside `sm_templates.c` / `bb_templates.c`.  Output is a checklist of candidate deletions for EDP-2..-10.  Commit script + initial audit report. (Sonnet 4.6, one4all `59d96aea`) Initial count: SM=299, BB=190, Total=489 hits. Candidates: sm_codegen.c, sm_codegen_x64_emit.c, sm_emit_template.c, bb_flat.c, bb_build.c, bb_boxes.c.

  - [ ] **EDP-2 — `sm_emit_template.c` legacy table purge.**  Delete `g_sm_templates[]`, `render_macro_body`, `render_call_line`, `SM_TPL_LBLOPT` and friends.  Template functions in `sm_templates.c` become the only dispatch surface.  Callers using `g_sm_templates[i]` rewire to `emit_sm_<x>` directly.

  - [ ] **EDP-3 — `sm_codegen.c` reduced to dispatch.**  For each per-opcode case body that does inline `bb_emit_byte(0x...)` emission, replace with a call to `emit_sm_<x>(e, args)`.  After this, `sm_codegen.c` is a thin `switch (ins->op) { case SM_X: emit_sm_x(e, ...); break; ... }` walker over SM_Program.

  - [ ] **EDP-4 — `sm_codegen_x64_emit.c` reduced to dispatch.**  Same treatment for the text-emit path.  After this, both mode-3 (binary) and mode-4 (text) walk SM_Program by dispatching to the SAME template functions through `bb_emit_mode` switching.  The architectural goal of "ONE emitter, two output-time forms" from ARCH-x86.md is realised.

  - [ ] **EDP-5 — `bb_flat.c` `flat_emit_*` helpers folded into templates.**  Each `flat_emit_<x>` either calls `emit_bb_<x>(e, ...)` from `bb_templates.c` or is deleted entirely if the template already covers the call surface.  After this, `bb_flat.c` becomes a thin walker that dispatches each PATND node to the right template.

  - [ ] **EDP-6 — Activate `EM-BB-PURGE-1` above.**  Add `EMIT_BINARY_BROKERED` to `bb_emit_mode_t`. Implement port-call preamble for brokered mode.

  - [ ] **EDP-7 — Activate `EM-BB-PURGE-2` above.**  Add `bb_build_brokered(pp)`. Wire `BB_MODE_DRIVER` to use it.

  - [ ] **EDP-8 — Activate `EM-BB-PURGE-3` above.**  Delete `bb_build()` from `stmt_exec.c`.

  - [ ] **EDP-9 — Activate `EM-BB-PURGE-4` above.**  Delete all 26 C-function BB boxes from `bb_boxes.c`.

  - [ ] **EDP-10 — Activate `EM-BB-PURGE-5` above.**  Delete heap ζ struct typedefs and `bb_<kind>_new()` constructors.

  - [ ] **EDP-11 — Remove `-Wl,--allow-multiple-definition`.**  From `Makefile`'s libscrip_rt link line.  If any duplicate-symbol errors surface at link time, that IS a residual doppelganger — find and delete.  After clean link, EM-DOPPELGANGER-PURGE closes.

  - [ ] **EDP-12 — Close-out report.**  Re-run EDP-1's audit script.  Output should show every SM opcode and every XKIND_t kind reaches exactly ONE emitter — the template function in `sm_templates.c` / `bb_templates.c`.  No remaining matches outside those two files.  Commit the clean audit as the close artifact.

  **Done when:** all gates green; `-Wl,--allow-multiple-definition` removed; EDP-1 audit shows zero matches outside `sm_templates.c` / `bb_templates.c`.

  **Architectural significance:** this rung realises ARCH-x86.md §"Stack machine (SM_Program)"'s "EMITTER walks same SM_Program → native code.  One instruction set.  No divergence between interpreter and emitter." literally — there will be exactly one place in the codebase where SM_X (or X<KIND>) gets emitted as native code, regardless of mode-3 / mode-4 output form.


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

**SESSION HANDOFF — sess 2026-05-12h (Claude Opus 4.7)**

**case_driver mode-4 unblocked. Beauty-subsystems PASS 6 → 7.** one4all
HEAD `baa29424`. Three fixes landed this session:

### 1. BB-blob R10 corruption — diagnosed and fixed

The "Diagnose the BB-blob R10 corruption" next-up from the previous
three handoffs (sess 2026-05-12d/e/f/g) is closed.  Root cause was the
canonical "caller-saved register lost across a runtime call":

- A flat-BB BLOB's α-preamble does `lea r10, [rip + Δ_data]`.
- The BLOB body then issues `call bb_<kind>@PLT` (e.g. bb_deferred_var_exported)
  to the runtime.
- The AMD64 SysV ABI marks `r10` as **caller-saved** — the called
  function is free to clobber it.  Many do.
- The BLOB's γ-success branch resumes after the call and does
  `movslq (%r10), %rcx` to load Δ — against garbage R10 → segfault.

Gdb evidence: R10=0x1 (a residue of ESI=1 from the β port call) at the
crash site `0x7ffff7060069` in a bb_deferred_var XDSAR blob,
`bb_broker:44` calling into the blob.

**Fix** (per ARCH-x86.md §"Intra-BLOB vs extra-BLOB jumps":
"Source BLOB emits `push r10` before the outbound jump and `pop r10`
at the resume point"):

- Added `BB_INSN_PUSH_R10` (41 52) and `BB_INSN_POP_R10` (41 5A) to
  `emitter.h` BB_INSN enum.
- Added `emit_push_r10()` / `emit_pop_r10()` inline helpers.
- Added corresponding cases in `emitter_binary.c` and `emitter_text.c`.
- Wrapped both α and β port calls in `bb_flat.c::flat_emit_box_call`
  with `emit_push_r10` / `emit_pop_r10`.
- Also wrapped `flat_box_call` and `flat_box_call_slot` (text-mode
  variants) for symmetry.
- Also wrapped `t_bb_port_call` in `bb_emit.c` (the template-side
  helper that BB templates call via `t_*`).

**Verification**: `case_driver.sno` previously segfaulted at
`bb_broker:44` on statement 1.  Now produces all 9 expected PASS lines
matching `--sm-run` byte-for-byte.  Beauty-subsystems mode-4 gate:
PASS=6 FAIL=11 → PASS=7 FAIL=10 (case_driver moved from diff-fail
[segfault → empty output] to pass).

### 2. lower.c DEFINE_ENTRY labtab fix re-applied

Re-applied the fix from sess 2026-05-12d handoff: at FUNC_IS_ENTRY_LABEL,
overwrite the just-defined labtab entry's `instr_idx` to point AFTER
the SM_DEFINE_ENTRY instruction.  Internal `:(fname)` gotos now skip
the prologue; external rt_call entries still hit it.  Verified the
emitted `.s` shows `.L<entry>: DEFINE_ENTRY` / `.L<body+1>: PUSH_VAR`
shape on case_driver.

### 3. Template consolidation (per Lon directive this session)

78 per-opcode template files in `src/runtime/x86/templates/` → 2 files:

- `src/runtime/x86/sm_templates.c` (45 SM opcode emitters)
- `src/runtime/x86/bb_templates.c` (33 BB box emitters)

Processing:
- All C source comments (`/* */` and `//`) stripped.
- All blank lines stripped.
- 120-char `/*===...===*/` divider between each function.
- `templates/` directory deleted.
- `sm_helpers.h` deleted; its three helper declarations
  (`emit_sm_rtcall`, `emit_sm_pat_rtcall`, `emit_sm_lbl_rt`) replaced
  by static-in-file forward declarations at the top of
  `sm_templates.c`.  These helpers are now `static` (private to the
  bundle); `emit_sm_arith_op` remains non-static (called externally
  from `sm_codegen_x64_emit.c`; declared in `templates.h`).
- `templates.h` and `sm_helpers.h` move from `templates/` up to
  `src/runtime/x86/`.
- All `"../emitter.h"` etc. in template bodies become `"emitter.h"`.
- All `"templates/templates.h"` includes in non-template files
  (`bb_flat.c`, `sm_codegen.c`, `sm_codegen_x64_emit.c`,
  `test_template_byte_identity.c`, `demo_template_productions.c`)
  become `"templates.h"`.
- Makefile: removed 78 source-list entries (the `RT_PIC_SRCS` list)
  and 78 `gcc -c .../sm_X.c -o .../template_sm_X.o` recipe lines;
  added 2 of each (`sm_templates.c`, `bb_templates.c`).

The Law of Template Functions ("one C template function per SM opcode
and per BB box") is structurally satisfied — there are 45 SM template
functions and 33 BB template functions, each as a distinct C function
inside its bundle.  File count is incidental, per the same Law.

### Gates

| Gate | Before sess | After sess |
|---|---|---|
| `test_smoke_snobol4.sh`                  | PASS=7 FAIL=0   | PASS=7 FAIL=0   |
| `test_gate_em_template_byte_identity.sh` | PASS=4 FAIL=0   | PASS=4 FAIL=0   |
| `test_smoke_snocone.sh`                  | PASS=5 FAIL=0   | PASS=5 FAIL=0   |
| `test_gate_em_beauty_subsystems_mode4.sh`| PASS=6 FAIL=11  | **PASS=7 FAIL=10** |
| `test_smoke_unified_broker.sh`           | PASS=22 FAIL=27 | PASS=22 FAIL=27 |

Remaining beauty-subsystems failures (9 diff + 1 link):
Qize_driver, ReadWrite_driver, TDump_driver, XDump_driver (link),
global_driver, match_driver, omega_driver, semantic_driver,
stack_driver, tree_driver.  All distinct bugs from the R10
corruption — now they are content-divergence bugs, not segfaults.
omega_driver was confirmed to run to completion and produce 15 lines
of output diverging from --sm-run starting at line 1 (different
PASS/FAIL semantics — likely a separate Phase-4 or replacement issue).

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`,
   `MIGRATION-MODE4-IS-MODE3-DUMP.md`.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5,
   beauty-subsystems mode4 PASS=7.
3. **⛔ DIRECTIVE FROM LON (this session, after handoff): finish ALL
   SM and BB C templates before attempting any beauty-suite or beauty
   self-host work.**  Do not pick up the remaining 9 beauty-subsystems
   diff-fails (Qize/ReadWrite/TDump/global/match/omega/semantic/stack/
   tree) or the XDump link-fail until every SM opcode and every BB
   box has its template function present and registered.

   Audit the current state under `EM-TEMPLATE-COMPLETE` in this goal
   file (the SM-total / BB-total audit at the head of that rung).
   The 78-file consolidation in sess 2026-05-12h preserved every
   template function that existed, but did NOT add missing ones — so
   the EM-TEMPLATE-COMPLETE TC-SM-* and TC-BB-* check-marks reflect
   the state at the time the audit was written, and remain authoritative
   for what still needs to land.  Walk the SM_t enum and the XKIND_t
   enum, grep each opcode/kind for an `emit_sm_<x>` / `emit_bb_<x>`
   function in `sm_templates.c` / `bb_templates.c`, and add any that
   are missing.  Register each new function in `g_sm_templates[]`
   where applicable; ensure `templates.h` declares it.

   The consolidation removed file-level fragmentation, but the Law
   of Template Functions ("one C template function per SM opcode and
   per BB box") still applies at the function level — gaps in
   coverage remain a violation.

4. After EM-TEMPLATE-COMPLETE closes, return to the beauty-subsystems
   diff-fails.  omega_driver is the smallest output divergence;
   XDump_driver is the only link-fail and may be a separable rt
   symbol gap.  For each diff-fail, capture mode-3 vs mode-4 output,
   identify the first divergent line, and trace back to the lowering
   or codegen difference.

### Lesson recorded

The "R10 corruption" bug had been pending across four sessions
(2026-05-12d/e/f/g).  Each prior session correctly identified the
crash site (`bb_broker:44`, R10=1, inside an XSPNC/XDSAR blob doing
`movslq (%r10), %rcx`) but stopped short of identifying that R10 is
caller-saved per the AMD64 SysV ABI and that BB port calls were
emitting `call fn@PLT` with no register-save bracket.

The fix is purely structural and the simplest possible reading of
ARCH-x86.md §"Intra-BLOB vs extra-BLOB jumps": *every* runtime call
from inside a flat-BB BLOB body needs `push r10` before and `pop r10`
after, because the call is by definition an extra-BLOB call where
control returns inside the source BLOB.

Future debugging hint for this class of "register clobbered across
runtime call inside a flat BLOB": check that the call sites in
`bb_flat.c` and `bb_emit.c` bracket every PLT call in `push <reg>` /
`pop <reg>` for every register the BLOB body relies on.  Today only
r10 matters; future BLOB-LOCAL register additions would need the
same treatment.

---

**SESSION HANDOFF — sess 2026-05-12g (Claude Opus 4.7)**

**TC-UNSPLIT-1, -2, -4, -6, -7, -8 all closed this session** plus
TC-UNSPLIT-CLOSE re-amended.  one4all `802c88ee`.  All six bundle files
(`sm_arith.c`, `sm_rtcall.c`, `sm_jump.c`, `sm_return.c`,
`sm_exec_stmt.c`, `sm_pat_rtcall.c`) are now the source of truth for
their opcode groups.  43 per-op files deleted; Makefile updated.
Baseline preserved on all gates.

`find src/runtime/x86/templates -name 'sm_*.c' | wc -l`: 89 → 46
(Δ this session = -43).  Cumulative from peak-split state (sess
2026-05-12e baseline `c9b7428d` had 93): -47 across two sessions.

### Why this session reopened TC-UNSPLIT

Sess 2026-05-12f closed TC-UNSPLIT-3/5/9/10/11/CLOSE based on the
audit table in the goal file, which marked TC-SPLIT-1/2/4/6/7/8 as
"OK — leave as-is".  Lon corrected this: the audit's "OK" verdicts
were wrong calls.  The binding rule "one C template function per
opcode; file count is incidental; restore the bundle files as the
source of truth; delete the per-op fragments" applies uniformly to
**all eleven** TC-SPLITs, not just the five with orphan-bundle
duplicates.  The "OK" cases survived because of
`-Wl,--allow-multiple-definition` in the Makefile, but that's
tolerance, not correctness.

### What this session did

1. **TC-UNSPLIT-1: `sm_arith.c`.**  Recreated with 5 emit functions
   (`emit_sm_add/sub/mul/div/mod`) + non-static `emit_sm_arith_op`
   helper.  Removed duplicate `emit_sm_arith_op` from `sm_helpers.c`.
   Deleted 5 per-op files.

2. **TC-UNSPLIT-2: `sm_rtcall.c`.**  Bundle already contained all 3
   emit functions (`emit_sm_concat/push_null/coerce_num`) + static
   `emit_sm_rtcall` helper — no recreation needed.  Deleted 3 per-op
   files.  Note: `sm_rtcall.c` is the renamed form of
   `sm_nullary_rt.c` (rename commit 980e2d1c); the rename is
   orthogonal to the unsplit.

3. **TC-UNSPLIT-4: `sm_jump.c`.**  Recreated as 3-function bundle
   (`emit_sm_jump/jump_s/jump_f`) + static `make_pc_label` helper
   (restored from pre-split form in commit accf4477^).  Deleted
   `sm_jump_s.c` and `sm_jump_f.c`.

4. **TC-UNSPLIT-6: `sm_return.c`.**  Recreated as 10-function bundle:
   `emit_sm_return`, `emit_sm_return_variant`, plus the 8 conditional
   return wrappers.  The 8 conditional returns were NEW templates
   added by commit 3cc8b399 (not pre-split bundle content) but folded
   into `sm_return.c` per the binding rule.  Deleted 9 per-op files.

5. **TC-UNSPLIT-7: `sm_exec_stmt.c`.**  Recreated as 3-function bundle
   (`emit_sm_push_expression`, `emit_sm_call_expression`,
   `emit_sm_exec_stmt`) restored from pre-split form.  Deleted 2
   per-op files.

6. **TC-UNSPLIT-8: `sm_pat_rtcall.c`.**  Bundle already contained all
   22 emit functions + static `emit_sm_pat_rtcall` helper — no
   recreation needed.  Deleted 22 per-op `sm_pat_*.c` files.  Note:
   `sm_pat_rtcall.c` is the renamed form of `sm_pat_nullary.c`
   (rename commit 980e2d1c).

7. **`sm_helpers.c` cleanup partial.**  Removed duplicate
   `emit_sm_arith_op` and `emit_sm_lbl_rt` definitions (both are
   now `static` inside their bundles).  Retained `emit_sm_rtcall`
   and `emit_sm_pat_rtcall` because many other single-opcode template
   files (`sm_push_null_noflip.c`, `sm_suspend.c`, `sm_resume.c`,
   `sm_define.c`, `sm_define_entry.c`, etc.) still call them.  Full
   deletion of `sm_helpers.c` is blocked on a future broader fold —
   those single-opcode files could also be merged into a generic
   "rtcall family" bundle, but that exceeds this session's scope.

8. **Makefile updated.**  Removed 43 source-list entries and 43
   recipe lines for the per-op files.  Added entries/recipes for the
   5 newly-recreated bundles (sm_arith.c, sm_jump.c, sm_return.c,
   sm_exec_stmt.c) plus the 2 already-extant bundles that weren't yet
   wired in (sm_rtcall.c, sm_pat_rtcall.c).

### What this session did NOT do

- **Did not re-apply the lower.c DEFINE_ENTRY labtab fix** from sess
  2026-05-12d.  Still pending.
- **Did not diagnose the BB-blob R10 corruption.**  Beauty-subsystems
  PASS still 6/17.
- **Did not delete `sm_helpers.c`.**  Two functions remain
  (`emit_sm_rtcall`, `emit_sm_pat_rtcall`) because many single-opcode
  template files outside the unsplit scope still call them.

### Lesson recorded

The original TC-UNSPLIT audit table labelled 6 of the 11 splits as
"OK — leave as-is".  Three of those (TC-SPLIT-2, TC-SPLIT-8) were
labelled OK because the bundle file's rename had been mistaken for a
delete; one (TC-SPLIT-1) was labelled OK because the bundle was
considered "a helper, not a duplicate" (true at the helper level, but
the per-op files were still violating the one-function-per-opcode
shape); the others (TC-SPLIT-4, -6, -7) were labelled OK because the
bundle file was "repurposed" as a single-op file — but repurposing a
bundle file as a single-op file still leaves the surrounding per-op
files as fragments that violate the binding rule.

**The audit should have applied the binding rule uniformly to all 11
splits.**  Future audits in similar refactoring rungs should not
exempt cases on the grounds that the build still works — `--allow-multiple-definition`
and helper-only bundles both mask the violation.  The test is purely
structural: does each opcode have one template function, and is that
function in the bundle file with its sibling opcodes' functions?

### Next session must

1. Read `RULES.md`, `ARCH-x86.md` (esp. §"Intra-BLOB vs extra-BLOB jumps"),
   `ARCH-SCRIP.md`, `MIGRATION-MODE4-IS-MODE3-DUMP.md`.

2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5,
   beauty-subsystems mode4 PASS=6.

3. **Re-apply the lower.c DEFINE_ENTRY labtab fix** from sess 2026-05-12d.

4. **Diagnose the BB-blob R10 corruption** that case_driver /
   omega_driver hit at `bb_broker:44`.  See sess 2026-05-12d's
   analysis.

5. (Optional cleanup, lower priority) Consider folding the remaining
   single-opcode template files that wrap `emit_sm_rtcall` (currently:
   `sm_push_null_noflip.c`, `sm_suspend.c`, `sm_resume.c`, `sm_define.c`,
   `sm_define_entry.c`, `sm_gen_tick.c`, `sm_suspend_value.c`,
   `sm_load_glocal.c`, `sm_store_glocal.c`, `sm_load_frame.c`,
   `sm_store_frame.c`, `sm_icmp_gt.c`, `sm_icmp_lt.c`,
   `sm_bb_pump*.c`, `sm_bb_once*.c`, `sm_exp.c`, `sm_neg.c`,
   `sm_acomp.c`, `sm_lcomp.c`, `sm_incr.c`, `sm_decr.c`) into a single
   `sm_rtcall_ops.c` bundle.  Would let `sm_helpers.c` be deleted
   entirely.  Currently out of scope.

---

**SESSION HANDOFF — sess 2026-05-12f (Claude Opus 4.7)**

**TC-UNSPLIT-3, -5, -9, -10, -11, -CLOSE all closed this session.**
one4all `c074dd7e`.  All five bundle files (`sm_var.c`,
`sm_label_stno.c`, `sm_pat_lbl.c`, `sm_pat_capture.c`,
`sm_pat_capture_fn.c`) are now the source of truth
and are wired into the Makefile.  Four orphan per-op files deleted
(`sm_push_var.c`, `sm_store_var.c`, `sm_label.c`, `sm_stno.c`).
Baseline preserved: smoke 7/7, template-byte-id 4/4, snocone 5/5,
beauty-subsystems mode4 PASS=6 FAIL=11.

`find src/runtime/x86/templates -name 'sm_*.c' | wc -l`: 93 → 89 (Δ = -4).
The goal file's prior "-8" claim was a miscount and has been corrected
in TC-UNSPLIT-CLOSE.

### Done this session

1. **Session setup complete.** Repos cloned, scrip + libscrip_rt built,
   all four baseline gates green.

2. **TC-UNSPLIT-3 (sm_var) closed.**
   - Bundle `sm_var.c` (containing `emit_sm_lbl_rt` static helper +
     `emit_sm_push_var` + `emit_sm_store_var`) confirmed as most
     recent (touched commit `3468bb67`).
   - Per-op files `sm_push_var.c` and `sm_store_var.c` deleted.
   - Makefile: removed two per-op source-list entries and recipe
     lines; added `sm_var.c`.
   - Gates green.

3. **TC-UNSPLIT-5 (sm_label_stno) closed.**
   - Bundle `sm_label_stno.c` (containing `emit_sm_label` +
     `emit_sm_stno`) confirmed as most recent (touched commit
     `3468bb67`).
   - Per-op files `sm_label.c` and `sm_stno.c` deleted.
   - Makefile updated analogously.
   - Gates green.

4. **TC-UNSPLIT-9, -10, -11 closed (bundle-only; per-op files never
   existed on disk despite prior `[x]` claims).**
   - `sm_pat_lbl.c`: contains `emit_sm_pat_lit`, `emit_sm_pat_refname`,
     `emit_sm_pat_usercall` (+ static helper `emit_sm_pat_lbl_rt`).
   - `sm_pat_capture.c`: contains `emit_sm_pat_capture`,
     `emit_sm_pat_usercall_args`.
   - `sm_pat_capture_fn.c`: contains `emit_sm_pat_capture_fn`,
     `emit_sm_pat_capture_fn_args`.
   - All three signatures match `templates.h` declarations.
   - Makefile: added three source-list entries and three recipe lines.
   - Gates green.

5. **TC-UNSPLIT-CLOSE closed.**  TC-SPLIT-3, -5, -9, -10, -11 flipped
   from `[x]` to `[~]` with `Superseded by TC-UNSPLIT-N` notes.
   TC-SPLIT-1/2/4/6/7/8 left as `[x]` — those were genuine splits.

### What this session did NOT do

- **Did not re-apply the lower.c DEFINE_ENTRY labtab fix** from sess
  2026-05-12d.  That work is now next-up on critical path along with
  the BB-blob R10 corruption diagnosis.
- **Did not diagnose the BB-blob R10 corruption.**  Beauty-subsystems
  PASS still 6/17; expected to move to 8/17 once the R10 corruption
  + DEFINE_ENTRY patch land together.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md` (esp. §"Intra-BLOB vs extra-BLOB jumps"),
   `ARCH-SCRIP.md`, `MIGRATION-MODE4-IS-MODE3-DUMP.md`.

2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5,
   beauty-subsystems mode4 PASS=6.

3. **Re-apply the lower.c DEFINE_ENTRY labtab fix** from sess 2026-05-12d
   handoff (preserved below).  Verify the emitted `.s` shows the expected
   `.L<entry>: DEFINE_ENTRY` / `.L<body+1>: PUSH_VAR` shape on case_driver.

4. **Diagnose the BB-blob R10 corruption** that case_driver / omega_driver
   now hit at `bb_broker:44`.  See sess 2026-05-12d's analysis for the
   gdb trace, the `bb_pool` mapping address, and the candidate fix
   locations (`bb_flat.c` γ-port emission OR a BB template's port
   wiring).

5. After both fixes land, commit them together as
   `EM-MODE4-IS-MODE3-DUMP-DEFINE-ENTRY-LOOP` + a follow-up rung name
   for the BB-blob R10 fix.

### Lesson recorded

The original TC-UNSPLIT-CLOSE rung text claimed the file-count delta
would be -8; arithmetic of "4 deleted per-op for SPLIT-3/5" is in fact
4 files, and SPLIT-9/10/11 deleted 0.  The correction is recorded in
the rung text and reflected in the actual on-disk delta of -4.  Future
rung text that prescribes an expected file-count delta should derive
the number from the per-rung deletion list rather than asserting it
inline.

---

**SESSION HANDOFF — sess 2026-05-12e (Claude Opus 4.7)**

**No commits this session.** Baseline unchanged on all remotes (one4all
`c9b7428d`).  Working tree clean.

Baseline reconfirmed at session start: smoke 7/7, template-byte-id 4/4,
snocone 5/5, beauty-subsystems mode4 PASS=6 FAIL=11.

### Done this session

1. **Session setup complete.**  Repos cloned, scrip + libscrip_rt built,
   all four baseline gates green.

2. **Re-applied the lower.c DEFINE_ENTRY labtab fix from the previous
   handoff (sess 2026-05-12d) and verified architectural shape.**
   Emitted `case_driver.s` shows the expected pattern:
   ```
   .Lexpression_registry:  .quad .S175 ; .quad .L1838     # external entry
   .L1838:                 DEFINE_ENTRY                    # prologue here
   .L1839:                 PUSH_VAR  .S176 # str           # first body op
   ...
   jmp .L1839                                              # internal :(icase)
   ```
   External callers run the prologue; internal loop-backs skip it.
   PASS still 6/17 — the BB-blob R10 corruption masks any improvement,
   exactly as the prior handoff predicted.  **Patch reverted before
   handoff to keep tree clean.**  The exact patch text remains in the
   sess 2026-05-12d watermark below; re-apply from there.

3. **Confirmed the BB-blob R10 corruption is mode-4-specific.**
   `--jit-run` (mode 3) on the same case_driver.sno produces all 9
   expected PASS lines and exits cleanly.  The mode-4 binary segfaults
   on the **first statement's** EXEC_STMT_VARIANT call (gdb backtrace
   shows `main → rt_match_variant → exec_stmt → bb_broker:44`, with
   R10=1 and RIP inside an XSPNC blob doing `movslq (%r10),%rcx`).
   The crash is **before any user function is invoked**, ruling out
   the DEFINE_ENTRY / RETURN macro hypothesis explored in this session.

4. **Audited the template-split state and discovered TC-SPLIT
   inconsistency on HEAD `c9b7428d`** — see TC-UNSPLIT rung above for
   the full audit table.  Summary:
   - TC-SPLIT-1/2/4/6/7/8 are correct.
   - TC-SPLIT-3 (sm_var) and -5 (sm_label_stno): bundle files are
     orphaned (still on disk, not in Makefile, duplicate-symbol with
     the per-op files which are the active artifacts).
   - TC-SPLIT-9/10/11: the per-op files **were never created** despite
     `[x]` checkmarks; the bundles (sm_pat_lbl.c / sm_pat_capture.c /
     sm_pat_capture_fn.c) sit on disk but aren't built either.
     SM_PAT_LIT/REFNAME/USERCALL etc. dispatch via the legacy
     `g_sm_templates[]` table through `render_macro_body` /
     `render_call_line` (SM_TPL_LBLOPT), which is why the system
     functions even with the template-function files unbuilt.

5. **Added TC-UNSPLIT rung to the goal file** with audit table,
   per-rung procedure (git-archaeology, recombine, delete fragments,
   update Makefile, gate), and 6 sub-rungs (3/5/9/10/11/CLOSE).

### Investigation that did not pan out this session

- **DEFINE_ENTRY/RETURN macro alignment hypothesis was wrong.**
  Initially hypothesized that the regenerated `sm_macros.s` had an
  unbalanced `RETURN` macro (only `ret` with no matching `pop rbp`),
  based on a stale `sm_macros.s` in `corpus/programs/snobol4/demo/`.
  But the **freshly-regenerated** `sm_macros.s` produced by
  `sm_emit_macro_library_to_path()` correctly emits `mov rsp, rbp; pop
  rbp; ret` for RETURN, matching the corresponding `push rbp; mov rbp,
  rsp` in DEFINE_ENTRY.  Macros are balanced; this is not the bug.

  The stale demo `sm_macros.s` is committed in corpus from an older
  state — orthogonal cleanup candidate, not on critical path.

- **The handoff's stated "DEFINE_ENTRY loop hazard is a JIT hazard"
  still holds.**  The real mode-4 hazard is the BB-blob R10
  corruption, which fires on statement 1 before any user function
  runs, ruling out everything DEFINE_ENTRY-related as the proximate
  cause of the case_driver crash.

### Next session must

1. Read RULES.md, ARCH-x86.md (esp. §"Intra-BLOB vs extra-BLOB jumps"),
   ARCH-SCRIP.md, MIGRATION-MODE4-IS-MODE3-DUMP.md.

2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5,
   beauty-subsystems mode4 PASS=6.

3. **Work TC-UNSPLIT-3 first** (smallest scope: 2 per-op files +
   1 bundle file).  Follow the per-rung procedure in the goal file
   exactly.  Then -5, then 9/10/11 (largest — git-archaeology
   required for the orphaned bundle files since they may contain
   stale code that hasn't been touched since the original split).

4. After TC-UNSPLIT-CLOSE, return to the lower.c DEFINE_ENTRY patch
   (re-apply from sess 2026-05-12d handoff below) and then to the
   BB-blob R10 corruption diagnosis (sess 2026-05-12d analysis
   stands: it's an extra-BLOB jump landing mid-body instead of at
   α-preamble; fix likely in bb_flat.c γ-port emission or one of the
   BB templates' port wiring).

### Lessons recorded

- Past sessions marked TC-SPLIT-9/10/11 `[x]` without verifying the
  per-op files existed on disk; the build system's tolerance for
  this (legacy table dispatch covering the gap) hid the lie.  Before
  marking any future template-split rung `[x]`, the close gate must
  include `ls src/runtime/x86/templates/<expected>.c` for every
  per-op file the rung names.

- File-level fragmentation is not the Law of Template Functions.
  The Law is "one C template **function** per opcode."  When a
  group of functions naturally shares a static helper (e.g. the
  `emit_sm_lbl_rt` inside `sm_var.c`), keeping them in one file is
  fine and arguably better than fragmenting the helper across
  per-op files or extracting it to `sm_helpers.c` solely to enable
  fragmentation.

---

**SESSION HANDOFF — sess 2026-05-12d (Claude Opus 4.7)**

**No commits this session.** Baseline unchanged on all remotes.
Baseline reconfirmed: smoke 7/7, template-byte-id 4/4, snocone 5/5,
beauty-subsystems mode4 PASS=6 FAIL=11.

### Done this session

1. **Session setup complete.** Repos cloned, scrip + libscrip_rt built,
   all four baseline gates green.

2. **Corrected sess 2026-05-12c's root-cause analysis for case_driver / omega_driver.**
   The prior handoff said `:(icase)` looping back through `SM_DEFINE_ENTRY`
   re-executes `push rbp; mov rbp, rsp` and grows the stack. That is the
   **mode-3 (JIT) hazard**, not the **mode-4 (TEXT) hazard**.

   In mode-4 the `DEFINE_ENTRY` macro body in regenerated `sm_macros.s` is:
   ```
   .macro DEFINE_ENTRY
       call rt_define_entry@PLT
       push rbp
       mov  rbp, rsp
   .endm
   ```
   `rt_define_entry` is a no-op (rt.c:1109). The prologue *is* present.
   Re-execution on `:(icase)` loop-back does push rbp again, but the
   crash is not stack growth — `RETURN` only fires once per call.

   Actual gdb evidence after my fix below (RIP / RSP / R10 / backtrace
   captured this session):
   ```
   #0  0x7ffff7060069 in ?? ()         ← bb_pool RX mapping
   #1  0x7ffff7884197 in bb_broker (..., body_fn=scan_body_fn_u9, ...)
        at bb_broker.c:44                ← fn(root.ζ, α) call
   #2  0x7ffff7868173 in exec_stmt (...) at stmt_exec.c:1400
   #3  0x7ffff78427f4 in rt_match_variant (...) at rt.c:937
   r10 = 0x1                            ← *** should be &Δ ***
   ```
   Disassembly at the crash address shows a γ-fallthrough path in an
   XSPNC blob doing `mov (%rcx),%rax ; movslq (%r10),%rcx`. R10 holds
   the integer `1` (a `last_ok` / count residue) instead of `&Δ`.
   The BB blob was entered without its α-preamble running.

   Per ARCH-x86.md §"Intra-BLOB vs extra-BLOB jumps": every cross-BLOB
   entry must land on the α-preamble (`lea r10, [rip + Δ_data]`).
   This blob is being entered at a non-α offset and R10 is stale.

3. **Architectural fix for DEFINE-ENTRY-LOOP applied and verified (NOT COMMITTED).**

   The handoff's Option A is the correct shape. Single-point fix in
   `src/runtime/x86/lower.c` at the FUNC_IS_ENTRY_LABEL branch:

   ```c
   if (FUNC_IS_ENTRY_LABEL(label)) {
       g_p->instrs[g_p->count - 1].a[2].i = 1;
       sm_emit(g_p, SM_DEFINE_ENTRY);
       /* EM-MODE4-IS-MODE3-DUMP-DEFINE-ENTRY-LOOP: internal :(fname)
        * gotos must skip the DEFINE_ENTRY prologue.  External call
        * (rt_call → chunk_reg_lookup → call_native_chunk) reaches the
        * function via expression registry pointing at SM_LABEL+1 =
        * SM_DEFINE_ENTRY.  Internal goto reaches it via labtab.
        * Re-point the labtab entry to the PC AFTER SM_DEFINE_ENTRY. */
       tbl->labels[tbl->nlabels - 1].instr_idx = g_p->count;
   }
   ```

   No new labtab API needed — directly mutate the just-appended entry.
   No template / sm_macros.s change needed (the legacy `render_macro_body`
   in `sm_emit_template.c:307` already emits prologue when t->macro_name
   == "DEFINE_ENTRY"; that path remains the source of truth for the
   `.macro` body).

   **Verified in emitted asm:** with the patch applied,
   `case_driver.s` shows:
   ```
   .Lexpression_registry: .quad .S175 ; .quad .L1838    ← external entry
   .L1838:  DEFINE_ENTRY                                 ← prologue here
   .L1839:  PUSH_VAR  .S176 # str                        ← first body op
   ...
   jmp .L1839                                            ← internal :(icase)
   ```
   External callers run the prologue; internal loop-backs skip it. The
   old `.L1837` label (SM_LABEL "icase") is correctly elided by the
   `pc_used_as_target` pre-pass — nothing references it any more.

   **Result with patch:** PASS still 6/17. The fix DOES make progress —
   the case_driver crash moved from `call_native_chunk:rt.c:428`
   (RIP=`0x7fffffffe2b8`, a stack address — classic ret-to-corrupted-
   stack) to `bb_broker:44` with R10 corruption (above). The downstream
   BB-blob bug masks the PASS improvement.

   **Reverted before handoff** to keep diff minimal — RULES says
   commit-with-pass-improvement; a fix with no observable PASS gain
   muddies the rung close. The patch is saved at
   `/tmp/define-entry-loop-fix.patch` but that path will not survive
   the next container. Re-apply from this handoff text.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md` (esp. §"Intra-BLOB vs extra-BLOB jumps"),
   `ARCH-SCRIP.md`, `MIGRATION-MODE4-IS-MODE3-DUMP.md`.

2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5,
   beauty-subsystems mode4 PASS=6.

3. **Re-apply the lower.c patch above as the first action.** Verify
   the emitted `.s` shows the expected `.L1838: DEFINE_ENTRY` /
   `.L1839: PUSH_VAR` shape on case_driver.

4. **Diagnose the BB-blob R10 corruption** that case_driver / omega_driver
   now hit at `bb_broker:44`. Approach:

   a. Identify the blob whose γ-fallthrough is entering without R10 set.
      The crash blob is an XSPNC charset box at `0x7ffff7060000`. Use
      `bb_emit` / `bb_flat` debug logging to dump the per-blob α-preamble
      offsets, then add a watch-equivalent C `_check(r10_value, blob_id)`
      assertion at the head of each blob template (per RULES.md
      "Debugging — gdb hardware watchpoints DO NOT work" — use
      `__builtin_trap()` instrumentation, not gdb watchpoints).

   b. Trace: which extra-BLOB jump landed here without going through
      α-preamble? Candidates per ARCH-x86: a γ-port exit that resumed
      into this blob's β / mid-body, OR a tail-extra-jump where the
      source BLOB was supposed to push/pop r10 and didn't.

   c. The fix is likely in `bb_flat.c` (extra-BLOB γ-port emission)
      or in one of the BB templates' port wiring — NOT in lower.c
      or in rt.c.

5. After case_driver + omega_driver pass (expected PASS 6→8), commit
   both fixes together as `EM-MODE4-IS-MODE3-DUMP-DEFINE-ENTRY-LOOP`
   and a follow-up rung name for the BB-blob R10 fix.

6. Then move to match_driver (separate bb_pool crash), then XDump_driver
   (link failure), then the 7 remaining diff-fails.

### Lessons recorded

- "Loop re-entry of DEFINE_ENTRY grows stack" is a JIT hazard, not a
  mode-4 hazard.  Mode-4's symptom is downstream — the prologue/epilogue
  do balance correctly when no other corruption happens.

- When a fix correctly applies but PASS count doesn't move, the architecturally
  correct change still belongs in the tree — but the handoff must say
  *what's between the fix and the next PASS bump*, in enough detail that
  the next session doesn't redo the analysis.  This handoff does that
  for the BB-blob R10 corruption.

