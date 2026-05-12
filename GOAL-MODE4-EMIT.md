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

  - [ ] **EM-TEMPLATE-PURITY-1 — Audit.** For each BB template with `is_text`/callback, record: what output does the text path emit per port, what bytes does the binary path emit per port. This is the spec for the `t_*` helpers needed.

  - [ ] **EM-TEMPLATE-PURITY-2 — Add port-call helpers to `bb_emit.h`.** `t_bb_port_alpha(kind, args, lbl_succ, lbl_fail)` and `t_bb_port_beta(kind, args, lbl_fail)`. TEXT writes `KIND_α args, lbl_succ, lbl_fail`. BINARY emits the port's byte sequence. Both fully implemented.

  - [ ] **EM-TEMPLATE-PURITY-3 — Rewrite each BB template.** One `t_bb_port_alpha` call, one `t_bb_port_beta` call, `t_bb_box_banner`, done. No `is_text`, no callbacks, no raw instruction emission in the template body.

  - [ ] **EM-TEMPLATE-PURITY-4 — Delete dead infrastructure.** All `bb_*_text_fn` typedefs from `bb_flat.h`. All `*_text_body` callbacks from `bb_flat.c`. All callback parameters from template signatures.

  - [ ] **EM-TEMPLATE-PURITY-5 — Verify.** `grep -r 'is_text\|text_body_fn\|text_body_arg' src/runtime/x86/templates/` returns empty. Gates green. Artifacts byte-identical.
  - [ ] -s Remaining BB boxes: fix all six BB templates (bb_xchr, bb_xspnc, bb_xlnth, bb_xbrkx, bb_xposi, bb_xfarb) to use `t_*` helpers only. No `is_text`, no callbacks, no `e->...` calls. Add `t_bb_port_alpha`/`t_bb_port_beta` helpers to bb_emit.h as needed.
  - [ ] -t `sm_macros.s` + `bb_macros.s` become generated artifacts.
  - [ ] -u Rung close: beauty-subsystems gate improves from PASS=4 baseline; delete legacy emitter files.

- [ ] **EM-7d-beauty-subsystems** — Mode-4 parity with `--sm-run` across all 17 `*_driver.sno` beauty programs. Gate: `scripts/test_gate_em_beauty_subsystems_mode4.sh`. Pass criterion: mode-4 vs mode-3 byte-identical (not `.ref`-correct). **Baseline: PASS=4 FAIL=13. BLOCKED on EM-MODE4-IS-MODE3-DUMP.**

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

**SESSION HANDOFF — sess 2026-05-11 (Claude Sonnet 4.6)**

**one4all `d8fec035` on remote.**

### SM templates complete (all SM opcodes covered)

| Template file | Ops covered | Key helpers |
|---------------|-------------|-------------|
| `sm_halt.c` | SM_HALT | t_inc_mem_r13_disp8, t_ret |
| `sm_push_lit_i.c` | SM_PUSH_LIT_I | t_mov_rdi_imm64, t_call_sym_plt |
| `sm_void_pop.c` | SM_VOID_POP | t_call_sym_plt |
| `sm_jump.c` | SM_JUMP/S/F | t_test_rax_rax, t_emit_jmp |
| `sm_arith.c` | SM_ADD..SM_MOD | t_mov_rdi_imm64, t_call_sym_plt |
| `sm_nullary_rt.c` | SM_CONCAT/PUSH_NULL/COERCE_NUM | t_call_sym_plt |
| `sm_label_stno.c` | SM_LABEL/SM_STNO | t_noop_macro, t_banner_stno |
| `sm_call_fn.c` | SM_CALL_FN (MACRO_DEF only) | t_lea_rdi_strtab_sym, t_mov_esi_imm32 |
| `sm_return.c` | SM_RETURN/RETURN_VARIANT (MACRO_DEF only) | t_mov_edi_imm32, t_test_eax_eax, t_jz_retskip, t_retskip_label, t_ret |
| `sm_pat_nullary.c` | SM_PAT_EPS/ARB/REM/FAIL/SUCCEED/ABORT/BAL/FENCE/FENCE1/SPAN/BREAK/ANY/NOTANY/LEN/POS/RPOS/TAB/RTAB/ARBNO/CAT/ALT/DEREF | t_call_sym_plt |
| `sm_pat_lbl.c` | SM_PAT_LIT/REFNAME/USERCALL | t_lea_rdi_strtab_sym |
| `sm_pat_capture.c` | SM_PAT_CAPTURE/USERCALL_ARGS | t_lea_rdi_strtab_sym, t_mov_esi_imm32 |
| `sm_pat_capture_fn.c` | SM_PAT_CAPTURE_FN/CAPTURE_FN_ARGS | t_lea_rdi_strtab_sym, t_lea_rdx_strtab_sym, t_mov_esi_imm32, t_mov_edx_imm32 |

### t_* helpers surface (bb_emit.h / bb_emit.c)

`t_comment`, `t_bb_box_banner`, `t_inc_mem_r13_disp8`, `t_ret`, `t_pad_to_blob_size`,
`t_mov_rdi_imm64`, `t_call_sym_plt`, `t_macro_begin`, `t_macro_end`,
`t_test_rax_rax`, `t_emit_jmp`, `t_noop_macro`, `t_banner_stno`,
`t_lea_rdi_strtab_sym`, `t_lea_rdx_strtab_sym`,
`t_mov_esi_imm32`, `t_mov_edi_imm32`, `t_mov_edx_imm32`,
`t_test_eax_eax`, `t_jz_retskip`, `t_retskip_label`.

### BB templates — still violating (all six use is_text / callbacks / e->...)

`bb_xchr.c`, `bb_xspnc.c`, `bb_xlnth.c`, `bb_xbrkx.c`, `bb_xposi.c`, `bb_xfarb.c`

All must be rewritten per EM-TEMPLATE-PURITY. Next rung: **-s** (fix all six BB templates).

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`, `MIGRATION-MODE4-IS-MODE3-DUMP.md` in full.
2. Confirm baseline: smoke 7/7, snocone 5/5, template-byte-id 4/4.
3. **All SM templates are complete and clean** (zero violations — verified sess 2026-05-11). Do not re-audit SM templates; go straight to BB.
4. Next rung: **EM-TEMPLATE-PURITY → -s** — fix all six BB templates.
   - Each currently uses `e->is_text`, `EMIT_OPT`, `EMIT_JMP`, `EMIT_LABEL`, or text callbacks.
   - Add `t_bb_port_alpha` / `t_bb_port_beta` to `bb_emit.h` as needed.
   - Rewrite to pure `t_*` calls. No `(void)e` needed — `e` can be dropped from signature once all BB templates are clean.
   - Verify: `grep -r 'is_text\|EMIT_OPT\|EMIT_JMP\|EMIT_LABEL\|text_body' src/runtime/x86/templates/bb_*.c` returns empty.
5. After BB templates clean: rung -t (generated artifacts), then -u (rung close).
