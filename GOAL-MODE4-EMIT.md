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

> Closed-rung details (implementation notes, samples, gate counts, file lists)
> are in this file's git log.  Each closed bullet shows landed-date and the
> one4all commit that landed it; `git log -p .github/GOAL-MODE4-EMIT.md`
> recovers the full prose for any rung.

### M2 phase — SNOBOL4 + Snocone

- [x] EM-1 — Driver wiring + `libscrip_rt.so` skeleton.
- [x] EM-2 — SM_HALT + SM_PUSH_LIT_I codegen.
- [x] EM-3 — Stack ops + arithmetic.
- [x] EM-4 — Control flow + readability standard.
- [x] EM-5 — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.
- [x] EM-6 — Pattern matcher integration. (Retired by EM-7-revert.)
- [x] EM-7-revert — Tear out brokered Phase-3 from emitted-code path.
- [x] EM-7-default-bb-live — Flip BB-mode default to bb-live.
- [x] EM-7-default-jit-run — Flip exec-mode default to jit-run.
- [x] EM-7-emit-determinism — Fix dangling `s->subject->sval` pointer.
- [x] EM-7a — Phase-2 SM simulator (PATND_t reconstruction).
- [x] EM-7b — `bb_flat.c` EMIT_TEXT mode + external α/β/γ/ω labels.
- [x] EM-7b' — `emitter_t` vtable refactor.
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
- [x] EM-7c-sm-three-column — Three-column SM dispatch + macro library externalised + SM_ prefix stripped.
- [x] EM-7c-three-column-non-bb — Three-column shape extended to every non-BB line + redundant annotations stripped. (2026-05-09)
- [x] EM-7c-bb-three-column — BB-blob bodies converted to three-column shape, `;` separators interim. (2026-05-09)
- [x] EM-7c-stmt-banner-fidelity — `SM_TPL_NOOP` shape for SM_LABEL/SM_STNO + `emit_sm_pat_baked` rewrite; no naked `.LpcN:`. (2026-05-09)
- [x] EM-7c-s-file-beautify — Removed `;` separators from BB; converted 12 raw `EV_TEXT` blocks in `bb_flat.c` to three-column form. (2026-05-09; subsumed EM-7c-bb-three-column-data)
- [x] EM-7c-bb-three-column-split — Real three columns: col-2 = mnemonic alone, col-3 = operands. New `bb3c_op` / `bb3c_jmp` split helpers. (2026-05-09)
- [x] EM-7c-no-trailing-ws — Right-trim at every emission chokepoint. (2026-05-09)
- [x] EM-7c-sm-three-column-verify — `--audit` mode in `sm_codegen_x64_emit_test.c` + Test 14 (I0–I3a invariants). (2026-05-09)
- [x] EM-7c-bb-macros — BB-side macro library `bb_macros.s` (44 lines) + Greek suffixes on every internal label. (2026-05-09, one4all `baceff42`)
- [x] EM-FORMAT-SM — Single-pass bitset gates `.LpcN:` to jump targets only (89% label drop); leading underscore stripped from every label; CHUNK→EXPRESSION rename in macro names. (2026-05-09)
- [x] EM-FORMAT-SM-BANNER-FIDELITY — Parser fix: `g_stmt_lineno` tracker in `snobol4.l`; `s->lineno` falls back to it for unlabeled stmts in `snobol4.y`. Banner `(line L): <text>` now matches actual source. (2026-05-09)
- [x] EM-ONE-LINE-STRINGS + EM-NO-INTERNAL-COMMENTS — `.Lstr_N: .string ...` on one line; removed all internal comments from emitted `.s`. (2026-05-09, one4all `203426c6`)
- [x] EM-COMBINED-QUADS — `.quad .Lstr_N` and `.quad .LpcM` pairs merged onto one line with `;`. Audit I1 updated. (2026-05-09, one4all `b19f75ba`)
- [x] EM-FORMAT-BB-LONE-LABELS — Pending-label buffer in `bb3c_format`; UTF-8 visual-width padding for Greek labels. Strategic flush points at section boundaries. (2026-05-09, one4all `68490fd6`)
- [x] EM-FORMAT-BB-BOX-BANNERS — 120-char `#=` rule + `# pattern <prefix>: <src>` per blob; 120-char `#-` rule + `# BOX <kind>(<args>) [<label-prefix>]` per leaf-box α. (2026-05-09, one4all `95192caa`; XCAT/XOR/varname/RPOS-indexing carved as follow-ons)
- [x] EM-FORMAT-BB-FUSED-GOTOS — Adjacent cond+uncond jmp pairs fuse onto one line via `;` separator. cjmp deferral state in `bb_emit.c`; `bb3c_emit_jmp` entry point. (2026-05-09)
- [x] EM-FORMAT-BB-PORT-COMPLETION — Survey: port emission structurally correct on all 5 corpora. ALSO fixed regression: removed `bb3c_flush_pending()` from `flat_emit_banner_rule` (was emitting 12 lone labels before banners). (2026-05-09)
- [x] EM-FORMAT-BB-COL3-COMMENTS — `# KIND(args)` annotations on leaf-box α-line emissions. (2026-05-09, one4all `70b76571`, corpus `f11fb1e`)

- [x] **EM-FORMAT-BB-LAW** — Four-tab BB layout (LABEL/MNEMONIC/ARGS/GOTO at file cols 0/24/41/68); SM-side keeps 3-tab.  TRIPLE-FUSION absorbed `cmp/test + cond_jmp + uncond_jmp` onto single lines via `flat_box_dispatch_jne_jmp` / `flat_box_entry_dispatch` in `bb_flat.c` (sess 2026-05-10).  Signed off sess 2026-05-10.  Audit clean: 0 lone labels, 0 lone jmps, 0 jmp+jmp.  Gates 14/14 GREEN.

- [x] **EM-FORMAT-BB-DATA-CONSOLIDATE** — Per-blob deferred-data buffer in `bb_flat.c`.  Every `flat_data_section`/`flat_text_section` pair now buffers into `g_flat_data_buf`; one consolidated `.section .data` block emitted at end of each blob via `flat_emit_body_v`.  Original sites get a `# data: <labels>` comment.  In-buffer label-fusion (`data_buf_pend_label` / `data_buf_three_col`) keeps `.Lcap1_data: .quad 0` on one line.  4-5 section ping-pongs per blob → 1.  (sess 2026-05-10)

      **Tracked artifact line counts:**
      | File | Lines | Was (LAW) | Δ |
      |------|------:|----------:|---:|
      | roman.s          |  151 | 153 | -2 |
      | wordcount.s      |  124 | 124 |  0 |
      | claws5.s         |  949 | 951 | -2 |
      | treebank-list.s  | 1176 | 1178 | -2 |
      | treebank-array.s | 1355 | 1357 | -2 |

      Net 2 lines saved per banner-bearing artifact (4-5 inline ping-pongs collapsed → 1 trailing block + 1-3 `# data:` annotation lines).  All 5 `gcc -c` clean.  Gates 14/14 GREEN.

- [x] **EM-FORMAT-BANNER-COLLAPSE-SPACE** — Banner shape collapsed `# ====...` → `#====...` and `# ----...` → `#----...` (drop the space between `#` and the rule character; keep total width at 120 columns).  Three sites in two files: `flat_emit_banner_rule` in `bb_flat.c` (BB-side major + minor); `emit_major_break` and `emit_minor_break` in `sm_codegen_x64_emit.c` (SM-side stmt banners); plus the `#-- epilogue` mini-banner.  Adjacent doc-comment shapes updated to match.  No effect on `# === BEGIN/END ... ===` macro-library markers (those have inline text and are not rule banners).  All 5 tracked artifacts regenerate clean (`gcc -c`).  Line counts unchanged from EM-FORMAT-BB-DATA-CONSOLIDATE.  Gates 13/13 GREEN (mode-4 smoke).  (sess 2026-05-10)

- [x] **EM-FORMAT-SUBLIME-GAS-INTEL** — Authored a proper GAS-Intel-syntax Sublime highlighter from scratch in `corpus/editor/sublime/`, replacing the previous `SCRIP-x86.sublime-syntax` Nasm-base-plus-overlay layer cake.  Result: 1779-line single file (Nasm base + overlay) → `GAS-x86.sublime-syntax` (467 ll) + `SCRIP-x86.sublime-syntax` (194 ll, thin overlay via `extends:`).  Total 661 ll vs 1779 ll — 63% smaller, with substantially better correctness on `;` (statement separator), `.section .note.GNU-stack` (handled via `section-name-tail` push), `.macro/.endm` (structured block with `\arg` recognition), ELF decorations (full family), and label color uniformity (`.L*` and user labels share one scope, `entity.name.label.gas` — eliminating the historic white-vs-orange split).  (sess 2026-05-10 later)

      **Why this is a MODE4-EMIT rung:** the readability of `.s` artifacts directly determines reviewability of mode-4 emit work.  EM-FORMAT-BB-LAW, EM-FORMAT-BB-DATA-CONSOLIDATE, EM-FORMAT-BANNER-COLLAPSE-SPACE, EM-7c-no-trailing-ws, EM-7c-bb-macros all aimed at making the emitted `.s` legible to a reviewer; the highlighter is the last leg of that.  A proper GAS highlighter is the editor-side complement of those emitter-side rungs.

      **Done-when:** a single `corpus/editor/sublime/GAS-x86.sublime-syntax` (or similar name) authored from scratch — no Nasm base — that:
      1. Owns scope `source.asm.gas.intel` (or `source.asm.gas` with a sub-context for Intel syntax).
      2. Recognizes GAS directives as first-class `support.function.directive.gas`: `.section`, `.text`, `.data`, `.rodata`, `.bss`, `.intel_syntax`, `.att_syntax`, `.string`, `.ascii`, `.asciz`, `.byte`, `.word`, `.long`, `.quad`, `.zero`, `.fill`, `.align`, `.balign`, `.p2align`, `.globl`, `.global`, `.local`, `.weak`, `.hidden`, `.type`, `.size`, `.set`, `.equ`, `.eqv`, `.include`, `.incbin`, `.macro`, `.endm`, `.endmacro`, `.if`, `.ifdef`, `.ifndef`, `.elseif`, `.else`, `.endif`, `.ident`, `.file`, `.loc`, `.cfi_*` (a family).
      3. Recognizes `;` as a *statement separator*, NOT a comment.  Inherent to GAS — fundamental for SCRIP triple-fusion and a primary reason for authoring this rather than patching Nasm.
      4. Recognizes `#` at column 0 (and `/*…*/`) as comments, per GAS's actual lexer behaviour.
      5. Recognizes GAS macros as a structured block: `.macro NAME args` opens, body nested, `.endm`/`.endmacro` closes.  Args, `\arg` references, and `.if/.endif` conditionals inside a macro body all scoped properly.
      6. Recognizes Intel-syntax x86_64 instruction forms with GAS quirks: `[rip + label]` rip-relative addressing, `[rax + rbx*4 + 8]` SIB scaling, register names without `%` prefix (post-`.intel_syntax noprefix`), size hints (`byte ptr`, `word ptr`, `dword ptr`, `qword ptr`), and dest-then-source operand order.
      7. Recognizes ELF decorations `@PLT`, `@GOT`, `@GOTPCREL`, `@function`, `@object`, `@progbits`, `@nobits`, `@notype`, etc. as a single `support.other.elf-decoration.gas` family.
      8. Inherits or co-installs with a `SCRIP-x86.sublime-syntax` overlay that preserves the SCRIP-specific contexts already designed (`scrip-banners`, `scrip-jumpfuse`, `scrip-mnemonics`, `scrip-labels`).  Architecturally the SCRIP overlay is a thin layer ON the GAS base, not a fork of it.

      **Sub-rungs:**
      - [x] **EM-FORMAT-SUBLIME-GAS-INTEL-a** — Reference inventory done.  Across 5 tracked `.s` artifacts + `sm_macros.s` + `bb_macros.s`: 17 distinct GAS directives (`.align .else .endif .endm .global .globl .ifnb .include .intel_syntax .long .macro .quad .section .size .text .type .zero`); 14 raw x86_64 mnemonics (`call cmp jmp jne jnz jz lea mov movabs movsxd pop sub test xor`); 13 registers; 3 ELF decorations (`@PLT @function @progbits`); 56 SCRIP SM macros + 10 BB macros; Greek-letter vocabulary `Δ Σ α β γ ω`.
      - [x] **EM-FORMAT-SUBLIME-GAS-INTEL-b** — `GAS-x86.sublime-syntax` authored from scratch, 467 lines.  Owns scope `source.asm.gas`.  Directive families: section/symbol/attribute/data/alignment/macro/conditional/debug/mode/cfi.  Mnemonic families: move/stack/address/arith/branch/call/set/string/bit/fpu/simd/flag.  Register vocabulary by width.  ELF decorations as one family.  Critical correctness wins: `;` is `punctuation.separator.statement.gas` (NOT a comment); `#` and `/* */` are comments; `.macro/.endm` is a structured `meta.macro.gas` block with `\arg` recognition; `.section .note.GNU-stack,"",@progbits` paints as one section name via dedicated `section-name-tail` context; directive catch-all uses `(?!L)` to defer `.L*` to `local-labels`.  Validated by `gas_syntax_sim.py` walking all 7 files with all regexes compiling cleanly.
      - [x] **EM-FORMAT-SUBLIME-GAS-INTEL-c** — `SCRIP-x86.sublime-syntax` rewritten as 194-line thin overlay.  Uses Sublime's `extends: Packages/User/GAS-x86.sublime-syntax` (build 4080+) and `meta_prepend: true` to inject SCRIP-specific contexts: `scrip-banners`, `scrip-jumpfuse`, `scrip-mnemonics`, `scrip-port-labels`.  Activated by `first_line_match: '^\s*\.include\s+"(sm|bb)_macros\.s"'` so plain GAS files fall through to the base.  Greek-port labels get the more-specific `entity.name.label.box.scrip` scope as an additive refinement, NOT a replacement — themes without override get one consistent label colour, themes with override get a distinct accent.
      - [x] **EM-FORMAT-SUBLIME-GAS-INTEL-d** — `corpus/editor/sublime/README.md` updated.  Title now lists four products (SNOBOL4, Snocone, GAS-x86, SCRIP-x86); Files table extended; new "GAS-x86 — base GAS Intel-syntax x86_64 highlighter" section explaining what's right vs Nasm bases (specifically including the white/orange-fix mechanism); "SCRIP-x86" section rewritten as "thin overlay" with the per-overlay scope table and a label-color-uniformity explainer.  Authors section credited and updated.
      - [x] **EM-FORMAT-SUBLIME-GAS-INTEL-e** — Visual A/B captured as `corpus/editor/sublime/MIGRATION-GAS-SCRIP.md`.  Side-by-side textual comparison on a representative claws5.s slice showing OLD vs NEW painting of every token type; quantitative summary table across all 5 tracked artifacts (`Other label-named scopes outside the unified families = 0` across the board); architectural diff (1779 ll → 661 ll, 63% smaller).

      **Risk:** LOW.  No emitter changes; no runtime changes; no build-system changes.  Pure editor support.  Scope is bounded by the GAS manual.

      **Dependencies:** none.  Independent of EM-7d-beauty-subsystems and EM-7d.  Could be picked up by anyone with a fresh context-window.

      **Why it isn't done yet:** sess 2026-05-10 ran the SCRIP-x86 work at the end of an already-loaded session; context budget did not permit authoring a from-scratch GAS base.  Honest scope: what was delivered (Nasm + overlay) is workable but not pride-worthy; this rung carves the gap.

- [ ] **EM-MODE4-IS-MODE3-DUMP** — One template per SM opcode; three backends (binary / text / macro_def) walk it.  ⛔ **Read `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` first; it is the design.**  Outcome unchanged from earlier framing (mode-4's `.s` matches mode-3's bytes by construction).  Mechanism *changed* sess 2026-05-11 (Lon pivot): not literal SEG_CODE disassembly, but a per-opcode C template walked by an `emitter_t` vtable with binary / text-invocation / macro-definition backends.  The text backend keeps `.s` readable by emitting macro invocations (`PUSH_INT 42`), and the same templates regenerate `sm_macros.s` so the macro body is not a parallel source of truth.  Per Lon (sess 2026-05-11): "use the BB templates to produce the macros. We still want S readable."

      **The principle (ARCH-x86.md §"Stack machine (SM_Program)" + §"Dual-mode emitter (TEXT / BINARY)"):**

      > INTERP dispatches instructions.  **EMITTER walks same SM_Program → native code.  One instruction set.  No divergence between interpreter and emitter.**

      The previous attempt (rung `EM-SM-NATIVE-BYTES`, withdrawn 2026-05-10) read this as "lift the BB-side TEXT/BINARY vtable to SM side so two backends share one walker."  That works on the BB side because both the TEXT and BINARY BB backends actually emit instructions.  On the SM side it's overkill: there is no need for a TEXT backend to walk SM_Program at all when the BINARY backend already produces the bytes.  Mode-4 is not "the text twin of mode-3" — mode-4 is "mode-3 plus disk dump."

      **The mode definitions (ARCH-x86.md §"scrip unified executable"):**

      | Mode | Flag (canonical) | Legacy alias | What it does |
      |------|------------------|--------------|--------------|
      | 3 | `--sm-native` | `--jit-run` | `SM_Program → x86 bytes → mmap slab → jump in` (no emit to disk; in-process) |
      | 4 | `--sm-emit --target=x64` | `--jit-emit --x64` | Run mode-3 to populate SEG_CODE; **then** dump SEG_CODE to `.s` plus auxiliary sections; toolchain link |

      ARCH-SCRIP.md table:

      | # | Mode | Flag | Purpose | Pipeline |
      |---|------|------|---------|----------|
      | 3 | SM gen / exec | `--jit-run` | speed without asm/link/process overhead | IR → `sm_lower` → `sm_codegen` → `sm_jit_run` |
      | 4 | SM gen / asm / link / exec | future | full native binary path | IR → `sm_lower` → `sm_codegen` → `seg_code_dump_as_s` → asm + link → exec |

      The mode-4 row in ARCH-SCRIP previously read `IR → sm_lower → asm-emit → link → exec`, which left "asm-emit" undefined.  It is now defined: `asm-emit = sm_codegen + seg_code_dump_as_s`.

      **What's wrong today (sess 2026-05-10 audit):**

      1. Mode-3 (`sm_codegen.c`) does NOT walk SM_Program → native code per ARCH-x86 §"Stack machine".  It builds:
         - per-OPCODE 12-byte tail-call thunk (`mov rax,<handler>; jmp rax`) into `SEG_DISPATCH`;
         - `SEG_CODE` as a `uint8_t **` array of pointers, one per SM instruction, pointing into the per-opcode thunks;
         - `sm_jit_run` is a C `while` loop indirecting through the array.

         This is interpretation, not native compilation.  Mode-4 cannot be a SEG_CODE dump while SEG_CODE holds pointers, not instructions.

      2. Mode-4 (`sm_codegen_x64_emit.c`) is the FIRST native-x86 SM emitter.  Every alignment/prologue/chunk-frame question has been solved from scratch in this file with no oracle.  Once mode-3 produces real bytes, mode-4 becomes a `seg_code_dump_as_s()` call and most of `sm_codegen_x64_emit.c`'s control-flow logic deletes.

      **Done-when:**
      - `sm_codegen` lowers each `SM_Instr` to a contiguous native x86 blob in `SEG_CODE` (per-instruction, NOT per-opcode-shared); SM control flow (LABEL/JUMP/JUMP_S/JUMP_F/CALL_FN entry/RETURN/NRETURN/FRETURN) is real native `jmp`/`call`/`ret` with 32-bit displacements patched at end of codegen.
      - `sm_jit_run` is `setup_state ; jmp <SEG_CODE entry>` — no C dispatch loop, no per-instruction pointer-array.
      - `seg_code_dump_as_s(out, prog)` walks SEG_CODE pc-by-pc using a side-table populated during `sm_codegen` (per-PC: `{seg_code_offset, byte_count, mnemonic_hint, comment}`) and writes GAS asm text that reassembles to the exact same bytes.  Auxiliary sections (.rodata strtab, .data registry, banner comments, libscrip_rt PLT references, file header, expression registry, sm_macros.s, the emitted-main wrapper) stay in mode-4's auxiliary-section emitter — that part of `sm_codegen_x64_emit.c` is preserved.
      - `--sm-emit --target=x64` calls `sm_codegen` (populates SEG_CODE), then calls `seg_code_dump_as_s` (writes the .text section of the .s file), then writes the auxiliary sections.

      **Test gate** (new): `test_gate_em_mode4_is_mode3_dump.sh`.
      For each .sno in a small fixture set:
      1. Mode-4: `scrip --sm-emit --target=x64 file.sno > file.s`; assemble: `as -o file.o file.s`; `objdump -d file.o > file.s.disasm`.
      2. Mode-3 with debug variant: `scrip --sm-native --dump-seg-code file.sno > file.bin`; `objdump -D -b binary -m i386:x86-64 file.bin > file.bin.disasm`.
      3. `diff file.s.disasm file.bin.disasm` must be empty modulo a known short whitelist (loader-relative vs absolute static-data addrs; PLT stubs vs direct calls — link-time vs run-time differences only).

      The whitelist IS the precise quantification of "99.999%".  Any divergence outside it is a bug in mode-3 (since mode-4 is mode-3-plus-dump, mode-4 cannot diverge from mode-3 by construction once the dump path works).

      **Sub-rungs (sess 2026-05-11 pivot, second pass — co-equal SM+BB):**

      - [x] **EM-MODE4-IS-MODE3-DUMP-a — Design doc + this amendment.**  `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` lands; the rung header above is amended to point at it.  Second pass (later sess 2026-05-11) clarifies: SM and BB are co-equal under this architecture — every SM opcode AND every BB box gets its own template C file from day one.  Sprinkle model: a template can issue any call on the `emitter_t` surface (instruction, comment, banner, blank line, formatting) and each backend chooses to implement or no-op each one.  No code in this sub-rung.

      - [x] **EM-MODE4-IS-MODE3-DUMP-b — Vtable skeleton.**  `src/runtime/x86/emitter.h` extended with the new SM-template surface (structural markers, BB-port primitives, formatting, macro hooks) on top of the existing narrow-vtable `emit_insn`/`bb_insn_desc_t` shape.  Implementations land in `emitter_text.c` (real GAS asm output) and `emitter_binary.c` (no-op where the design says so; faithful stubs where bytes might be needed).  New file `emitter_macro_def.c` is a thin wrapper that constructs a text emitter in `TEXT_MODE_DEFINITION`.  `src/runtime/x86/templates/` directory created with a README explaining the per-opcode-template convention and the static-analysis invariant for BB-template macro-discipline.  Both new files wired into the Makefile (scrip rule + RT_PIC_SRCS).  Nothing calls the new surface yet.  Sub-rung -c (SM_HALT, the first template) will be the first caller.

      - [x] **EM-MODE4-IS-MODE3-DUMP-c — First SM opcode end-to-end: SM_HALT.**  `templates/sm_halt.c`.  mode-3 through it (replaces `emit_halt_blob`); mode-4 through it (replaces `emit_sm_halt`); `sm_macros.s` HALT generated from it via new `tools/regen_macros.c`.  New gate `test_gate_em_template_byte_identity.sh`.

      **PARTIAL LANDING — sess 2026-05-11 (Claude Opus 4.7):** The mode-3 portion is fully wired and gated; mode-4 wiring blocked on a design question.  See watermark for the full picture.  At a glance:

      - ✅ `templates/sm_halt.c` written; describes SM_HALT as `inc [r13+20]; ret` (the mode-3 form, also the design-doc form).
      - ✅ `templates/templates.h` created to aggregate template declarations.
      - ✅ `BB_INSN_INC_MEM_R13_DISP8` added to emitter.h; impl in both text and binary backends.
      - ✅ Mode-3 routed through the template via a capture-and-flush adapter (`emit_halt_blob_via_template` in `sm_codegen.c`); legacy `emit_halt_blob` retained with `__attribute__((unused))` as a one-line revert path.
      - ✅ Two gates: `test_gate_em_template_byte_identity.sh` (behavioral parity, 4/4 PASS) and `build_and_run_test_template_byte_identity.sh` (byte-level: drives `emit_sm_halt` into a buffer and compares to the literal expected sequence `41 ff 45 14 c3`).
      - ✅ Visual demo `demo_template_productions.c` exercises all three backends on the template and prints the productions side-by-side.
      - ⛔ **Mode-4 NOT wired.**  Mode-4 today emits `call rt_halt_tos@PLT` for SM_HALT (via `sm_emit_template.c` SM_TPL_NULLARY arm), which is structurally different from the template's `inc [r13+20]; ret`.  Resolving the discrepancy is a Lon-decision: either change mode-4 to match the template (Option A — strong "one source of truth"), or accept that mode-3 and mode-4 differ for some opcodes because their host environments differ (Option B — but the design doc forbids backend-conditional template bodies).  See `templates/sm_halt.c` header comment ("KNOWN OPEN ARCHITECTURAL QUESTION") and the watermark for details.
      - ⛔ **`sm_macros.s` regeneration NOT done.**  Blocked on the same question — the macro_def backend's HALT body has the same divergence problem as the text-INVOCATION backend's per-call-site line.  `tools/regen_macros.c` not authored.

      Reopens for a follow-up session: either close mode-4 via the chosen option, or carve `-c-mode4` as a new sub-rung once the decision lands.

      - [x] **EM-MODE4-IS-MODE3-DUMP-d — First BB box end-to-end: bb_xchr.**  `templates/bb_xchr.c`.  Simplest box (one-character — actually arbitrary-length — literal compare).  Wires `bb_flat.c`'s XCHR emit calls through the new vtable.  Proves BB side of the surface.  Sess 2026-05-11 (Claude Opus 4.7): byte-identical lift of `flat_emit_lit` + the inline banner-emission in `flat_emit_node`'s XCHR case into `emit_bb_xchr(emitter_t *e, PATND_t *p, lbl_succ, lbl_fail, lbl_β)`.  Unlike SM_HALT, XCHR has NO mode-3-vs-mode-4 divergence — both modes call into the same runtime symbols (memcmp, bb_label_*); the binary-vs-text difference is fully absorbed by the existing emitter vtable's symbolic helpers (BB_INSN_LEA_RCX_SYM, BB_INSN_CALL_SYM_PLT) — so -d landed cleanly without any A/B/C decision needed.  Two byte-identity verifications: (1) `claws5.s` emission `git stash`/`pop` diff: empty (byte-identical); (2) `--sm-run` 197/64 == `--jit-run` 197/64 unchanged across the 261-program jit smoke crosscheck.  Legacy `flat_emit_lit` retained with `__attribute__((unused))` as a rollback reference.  Two free functions (`flat_emit_banner_rule`, `flat_emit_box_banner`) promoted from `static` to external linkage and declared in `bb_flat.h` so templates can call them.

      - [x] **EM-MODE4-IS-MODE3-DUMP-e — charset-family BB box template (XSPNC/XBRKC/XANYC/XNNYC).**  `templates/bb_xspnc.c` + `emit_bb_charset()` callback design. Byte-identical. Gates 7/7+49/49+5/5+4/4, claws5.s diff empty. (sess 2026-05-11 Claude Sonnet 4.6, one4all `157352d8`)
      - [x] **EM-MODE4-IS-MODE3-DUMP-f — sm_push_lit_i template (SM-axis).**  `templates/sm_push_lit_i.c`; mode-4 routed through it. Byte-identical.  emit_sm_halt/emit_sm_push_lit_i in sm_codegen_x64_emit.c renamed to avoid conflict with template symbols.  Gates 7/7+49/49+5/5+4/4, roman.s+claws5.s diff empty. (sess 2026-05-11 Claude Sonnet 4.6, one4all `33b3c7ba`)
      - [x] **EM-MODE4-IS-MODE3-DUMP-g — integer-cursor family (XLNTH/XTB/XRTB).**  `templates/bb_xlnth.c`. 69 inline lines -> 3 dispatch one-liners. Byte-identical.  Gates 7/7+49/49+5/5+4/4, treebank-list.s diff empty. (sess 2026-05-11 Claude Sonnet 4.6, one4all `9e2ea80e`)
      - [ ] **EM-MODE4-IS-MODE3-DUMP-h through -p — Remaining emission units, alternating SM ↔ BB.**  Suggested order: sm_void_pop, bb_xbrkx, sm_jump, bb_xposi+xrpsi (one rung), sm_jump_s+sm_jump_f, bb_xfarb+xeps+xfail (one rung), sm_add+sub+mul+div+mod+exp.

      - [ ] **EM-MODE4-IS-MODE3-DUMP-q — SM_LABEL / SM_STNO** (structural markers; one rung).

      - [ ] **EM-MODE4-IS-MODE3-DUMP-r — SM_CALL_FN.**  Big SM rung; uses `lea_rip_sym`, `call_plt`, expression-registry interaction.

      - [ ] **EM-MODE4-IS-MODE3-DUMP-s — SM_RETURN / SM_NRETURN / SM_FRETURN family** including conditional variants.  ABI alignment work decided inside ONE template file; fixes mode-3 and mode-4 by construction.

      - [ ] **EM-MODE4-IS-MODE3-DUMP-t — Remaining BB boxes.**  XFNCE, XDSAR, XATP, XBRKX, XCALLCAP, XCAT, XOR, XSTAR, XFARB, XPOSI, XRPSI, XNME, XFNME, XARBN, XFAIL.  Bundle in 2-3 rungs by structural similarity.

      - [ ] **EM-MODE4-IS-MODE3-DUMP-u — Pattern SM opcodes** (`SM_PAT_*`).  Same discipline.

      - [ ] **EM-MODE4-IS-MODE3-DUMP-v — `sm_macros.s` and `bb_macros.s` become generated artifacts**, make rule added, files dropped from git in favor of build-time regen (or kept with a "DO NOT EDIT — generated" header).

      - [ ] **EM-MODE4-IS-MODE3-DUMP-w — Rung close.**  `test_gate_em_beauty_subsystems_mode4.sh` improves from baseline.  Delete `emitter_t.h` / `emitter_text.c` / `emitter_binary.c` (BB-side legacy vtable subsumed by `emitter.h`).  Delete `sm_emit_template.c` / `sm_emit_template.h` (SM-side macro-renderer subsumed by templates + `emitter_text.c`).

      **Superseded sub-rungs (prior framing, recorded for git-log archaeology only — do not implement these as written):** -a (audit/design doc with SEG_CODE-disassembly framing), -b (rewrite sm_codegen.c control flow as standalone task), -c (libscrip_rt cfn-call ABI fix at the call site — re-evaluate after template retrofit; may be unnecessary), -d (`sm_jit_run` rewrite — happens naturally as templates land), -e (`seg_code_dump_as_s` side-table — replaced by template vtable), -f (mode-4 collapses to call-mode-3-then-dump — replaced by mode-4 walks SM_Program with text backend).

      **Dependencies:** none.  Blocks `EM-7d-beauty-subsystems`, `EM-7d`, `EM-8`, `EM-9`.  Does NOT block `EM-FORMAT-SUBLIME-GAS-INTEL` (editor support, independent).

      **Risk:** HIGH but bounded.  Touches `sm_codegen.c` (mode-3) and `sm_codegen_x64_emit.c` (mode-4).  Mitigation: sub-rungs are sequenced so each one passes its own gate before the next opens.  After sub-rung -b mode-3 emits real bytes; the smoke gate `test_smoke_snobol4.sh` PASS=7 invariant is the tripwire.  After sub-rung -e the dump exists but mode-4 still uses the old text emitter (gates unchanged).  Sub-rung -f flips mode-4 to the dump path; this is the single risky change, and it's a pure replacement of emission method, not a reordering of pipeline.

      **Why this is the right pivot, finally:** the watermark's three-step plan (DEFINE-flag in sm_lower; registry filter; prologue/epilogue) was answering "how do chunks get prologues."  The previous rung's plan (lift the BB-side vtable) was answering "how do mode-3 and mode-4 share a walker."  Both questions assume the answer is "two emitters that walk SM_Program."  ARCH-x86 says one emitter.  Mode-3 IS the emitter.  Mode-4 is mode-3 plus dump.  The session that opens this rung must read `ARCH-x86.md` and `ARCH-SCRIP.md` first; without that grounding, the same wrong answers will be re-derived from inference.

- [ ] **EM-7d-beauty-subsystems** — Mode-4 parity with `--sm-run` across all 17 `*_driver.sno` programs in `corpus/programs/snobol4/beauty/`.  Each driver exercises one subsystem (assign, case, fence, match, omega, semantic, stack, trace, tree, counter, global, Gen, Qize, ReadWrite, ShiftReduce, TDump, XDump) with its own `.ref` oracle.  Gate: `bash scripts/test_gate_em_beauty_subsystems_mode4.sh` — for each driver, emit (`--jit-emit --x64`), assemble, link against `libscrip_rt.so`, run, then `diff` against the same driver's `--sm-run` output.  Pass criterion is mode-4-vs-mode-3 byte-identical, *not* `.ref`-correct: the absolute-correctness gate (drivers vs `.ref`) is `test_gate_sn7_beauty_self_host.sh` and lives under GOAL-LANG-SNOBOL4 rung SN-33.  Mode-4 cannot be more correct than mode-3; what this rung enforces is that the emitter pipeline reproduces SM-interpreter behaviour exactly.  Rationale: 17 small, self-contained subsystem programs surface category-specific divergences (pattern matching, FENCE, capture, indirection, function calls, tracing) one subsystem at a time — strictly easier to diagnose than chasing them simultaneously inside the 646-line beauty.sno.  This rung is a precondition to EM-7d; EM-7d cannot pass while subsystems diverge, and any subsystem mode-3 fix automatically lifts mode-4 here.  ⛔ **BLOCKED on EM-MODE4-IS-MODE3-DUMP.**  Once that rung lands, this rung's gate becomes derived: if mode-4 IS mode-3-dump, then mode-3-vs-mode-4 byte-identity is by construction and this rung's job reduces to verifying that mode-3 itself runs the 17 drivers correctly (which is GOAL-LANG-SNOBOL4 SN-33's territory).  This rung may collapse into SN-33 as a result.  **Baseline sess 2026-05-10 post-SN-33b:** PASS=4 FAIL=13 (emit=0 link=0 diff=13) — frozen.

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

**SESSION HANDOFF — sess 2026-05-11 (Claude Sonnet 4.6) — GOAL-MODE4-EMIT template retrofit**

**What this session did (sub-rungs -c through -g):**

- **-c (mode-4 closure):** Lon delegated A/B/C to Claude. **Option C chosen:**
  SM_HALT is a sanctioned terminative exception — mode-3 keeps `inc [r13+20]; ret`
  (in-process), mode-4 keeps `call rt_halt_tos@PLT` (standalone binary). Recorded in
  `templates/sm_halt.c` header. Both opcodes use `emit_halt_line` / `emit_sm_halt`
  (renamed in `sm_codegen_x64_emit.c` to avoid symbol collision with templates).

- **-e (BB: charset family XSPNC/XBRKC/XANYC/XNNYC):** `templates/bb_xspnc.c`.
  `emit_bb_charset()` owns binary path; text path via `bb_charset_text_fn` callback
  into `bb_flat.c` (avoids externalizing statics). `g_flat_node_id` extern-promoted.
  `bb_charset_text_fn` typedef in `bb_flat.h`.

- **-f (SM: sm_push_lit_i):** `templates/sm_push_lit_i.c`.
  `movabs rdi, val; call rt_push_int@PLT`. No mode-3/mode-4 divergence.
  `sm_codegen_x64_emit.c` wired: `emit_push_lit_i_line()` constructs text emitter,
  calls template. `templates/templates.h` included in `sm_codegen_x64_emit.c`.

- **-g (BB: integer-cursor XLNTH/XTB/XRTB):** `templates/bb_xlnth.c`.
  Same callback pattern as -e. `flat_emit_box_call` extern-promoted.
  `bb_intcur_text_fn` typedef in `bb_flat.h`. 69 inline lines → 3 dispatch one-liners.
  XLNTH: 1 long in `.data`; XTB/XRTB: 2 longs (n + padding).

**Commits (all pushed):**
- one4all `463fff0d` — -c + -e
- one4all `33b3c7ba` — -f
- one4all `9e2ea80e` — -g (HEAD)
- corpus `fd5c8a9`  — artifact regen (-e)
- .github multiple commits (watermarks + PLAN.md)

**Gates at handoff (one4all `9e2ea80e`):**
- `test_smoke_snobol4.sh`: 7/7
- `test_smoke_unified_broker.sh`: 49/49
- `test_smoke_snocone.sh`: 5/5
- `test_gate_em_template_byte_identity.sh`: 4/4
- treebank-list.s + claws5.s + roman.s stash/pop diff: empty (byte-identical)

**Template pattern established (follow for all subsequent sub-rungs):**

*BB templates* — one `.c` file per kind or structurally-identical family:
1. Template owns binary path: allocate zeta, call `flat_emit_box_call`.
2. Text path: `bb_flat.c` provides a `bb_*_text_fn` callback (arg struct carries
   all needed state: fn ptr, fn name, kind name, operands).
3. `bb_flat.c` provides `flat_emit_x*()` wrappers that build arg struct and call template.
4. `flat_emit_node` dispatch cases call `flat_emit_x*()` — one-liners.
5. Add new callback typedef to `bb_flat.h`; expose any needed statics as extern there.
6. Add template to `templates.h`, `RT_PIC_SRCS`, and scrip compile rule.

*SM templates* — one `.c` file per opcode (or tight family):
1. Function signature: `emit_sm_<opcode>(emitter_t *e, <operands>)`.
2. Body: `EMIT_OPT(e, comment, ...)` + `emit_*` helpers + `EMIT_OPT(e, macro_begin/end, ...)`.
3. In `sm_codegen_x64_emit.c`: rename the old `emit_sm_<opcode>(FILE*, ...)` static to
   `emit_<opcode>_line(FILE*, ...)` (avoids symbol conflict). New function constructs
   `emitter_text_new(out)`, calls template, `emitter_free(e)`.
4. Add template to `templates.h` and scrip compile rule (NOT RT_PIC_SRCS — SM templates
   called only from `sm_codegen_x64_emit.c` / `sm_codegen.c`).

**Next sub-rung: `-h` — SM-axis: `sm_void_pop`**

`SM_VOID_POP` pops and discards TOS. Mode-4 currently:
```
sm_emit_nullary(out, sm_template_lookup(SM_VOID_POP), NULL)
→ VOID_POP macro → call rt_pop_void@PLT
```
Template: `emit_sm_void_pop(emitter_t *e)` — `call rt_pop_void@PLT` only.
Same pattern as `sm_push_lit_i` but no operand. Rename `emit_sm_void_pop(FILE*,...)` →
`emit_void_pop_line(FILE*,...)` in `sm_codegen_x64_emit.c`.

After `-h`: `-i` (BB: XBRKX), then alternating per the revised sequence in the goal file.

**Files created this session:**
- `src/runtime/x86/templates/bb_xspnc.c`
- `src/runtime/x86/templates/sm_push_lit_i.c`
- `src/runtime/x86/templates/bb_xlnth.c`

**Files modified this session:**
- `src/runtime/x86/templates/sm_halt.c` (Option C decision)
- `src/runtime/x86/templates/templates.h` (new declarations)
- `src/runtime/x86/bb_flat.c` (callbacks + wrappers + dispatch + externs promoted)
- `src/runtime/x86/bb_flat.h` (typedefs + externs)
- `src/runtime/x86/sm_codegen_x64_emit.c` (renames + template wiring + include)
- `Makefile` (new template files)

----

**EM-MODE4-IS-MODE3-DUMP-g landed — sess 2026-05-11 (Claude Sonnet 4.6)**

`templates/bb_xlnth.c` — `emit_bb_intcur()` + per-kind wrappers for XLNTH/XTB/XRTB.
Same callback pattern as -e (charset). Binary path: `bb_len_new`/`bb_tab_new`/
`bb_rtab_new` + `flat_emit_box_call`. Text path: `intcur_text_body` in `bb_flat.c`.
Key difference from charset: XLNTH emits 1 long in `.data`; XTB/XRTB emit 2 longs.
`flat_emit_box_call` promoted from static to extern. 69 inline lines → 3 one-liners.
**one4all commit:** `9e2ea80e`. Gates: 7/7+49/49+5/5+4/4. treebank-list.s diff empty.

**Next: `-h`** — SM-axis: `sm_void_pop` (simplest SM pop opcode).

----

**EM-MODE4-IS-MODE3-DUMP-f landed — sess 2026-05-11 (Claude Sonnet 4.6)**

`templates/sm_push_lit_i.c` — `emit_sm_push_lit_i(emitter_t *e, int64_t val)`.
Emits `movabs rdi, val; call rt_push_int@PLT`. No mode-3/mode-4 divergence —
both modes call rt_push_int at runtime. Macro begin/end hooks included for
future sm_macros.s regeneration via macro_def backend.

`sm_codegen_x64_emit.c` changes:
- `emit_sm_halt` → `emit_halt_line` (avoid link conflict with template's
  `emit_sm_halt(emitter_t*)`; SM_HALT dispatch updated).
- `emit_sm_push_lit_i(FILE*,...)` → `emit_sm_push_lit_i_legacy` (unused rollback).
- New `emit_push_lit_i_line`: constructs text emitter, calls template.
- `templates/templates.h` included; SM_PUSH_LIT_I dispatch → `emit_push_lit_i_line`.

**Gates:** smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4.
roman.s + claws5.s stash/pop diff: empty. Static analysis clean.
**one4all commit:** `33b3c7ba`.

**Next sub-rung: `-g`** — BB-axis: `bb_xlnth` + `xtb` + `xrtb` (integer-cursor family).

----

**EM-MODE4-IS-MODE3-DUMP-c(closed) + EM-MODE4-IS-MODE3-DUMP-e landed — sess 2026-05-11 (Claude Sonnet 4.6)**

**-c mode-4 closure — Option C decision recorded.**

Lon delegated the A/B/C choice to Claude (Sonnet 4.6). Option C chosen: SM_HALT
is a **sanctioned terminative exception**. The "no divergence" invariant
covers program semantics; termination mechanism is host-environment-specific.
Mode-3 keeps `inc [r13+20]; ret` (in-process); mode-4 keeps
`call rt_halt_tos@PLT` (standalone binary). Decision recorded in
`templates/sm_halt.c` header. No code change. Sub-rung -c now closed.

**-e: charset-family BB box template (XSPNC/XBRKC/XANYC/XNNYC).**

`templates/bb_xspnc.c` provides `emit_bb_charset()` — the binary path.
Text path lives in `bb_flat.c` as `charset_text_body()` (a `bb_charset_text_fn`
callback), avoiding externalization of `bb_flat.c`'s static helpers.
Four per-kind wrappers (`flat_emit_xspnc/xbrkc/xanyc/xnnyc`) call
`emit_bb_charset` with the right runtime fn + text callback; `flat_emit_node`
dispatch cases updated. `flat_emit_charset_call` marked `__attribute__((unused))`.
`g_flat_node_id` promoted from `static` to `extern` (declared in `bb_flat.h`).
`bb_charset_text_fn` callback typedef added to `bb_flat.h`.

**Gates (all green):**
- `test_smoke_snobol4.sh`: 7/7
- `test_smoke_unified_broker.sh`: 49/49
- `test_smoke_snocone.sh`: 5/5
- `test_gate_em_template_byte_identity.sh`: 4/4
- `git stash`/`pop` diff on `claws5.s`: **empty** (byte-identical)
- 5/5 tracked artifacts `gcc -c` clean. Line counts unchanged (71/121/868/1104/1284).

**Files touched:**
- `src/runtime/x86/templates/bb_xspnc.c` — NEW
- `src/runtime/x86/templates/sm_halt.c` — Option C decision recorded
- `src/runtime/x86/templates/templates.h` — emit_bb_charset declaration
- `src/runtime/x86/bb_flat.c` — charset_text_body + wrappers; dispatch updated; g_flat_node_id extern
- `src/runtime/x86/bb_flat.h` — g_flat_node_id extern + bb_charset_text_fn typedef
- `Makefile` — bb_xspnc.c added to scrip rule + RT_PIC_SRCS
- corpus tracked artifacts regenerated (byte-identical)

**one4all commit:** `157352d8`. **corpus commit:** `fd5c8a9`.

**Next sub-rung:** `-f` — suggested `sm_push_lit_i` (SM-axis) or `bb_xlnth`+`xtb`+`xrtb`
(BB-axis integer-cursor family). SM-axis is now unblocked (Option C decided).

----

**_v eradication CLOSED — survivors renamed/deleted sess 2026-05-11 (Claude Opus 4.7, latest)**

Sub-rung that the prior watermark (below) carved as a future task: completed in-session.  Two changes, both purely cosmetic (no emission change):

1. **`flat_emit_body_v` → `flat_emit_body`** — mechanical rename in `src/runtime/x86/bb_flat.c`.  4 sites: definition + one doc-comment reference + two callers.
2. **`ev3c` family deleted entirely** from `src/runtime/x86/emitter.h`.  Static analysis confirmed zero external callers — four dead-code helpers (`ev3c`, `ev3c_action_v`, `ev3c_label`, `ev3c_goto_v`) carrying both the banned `ev` prefix (emitter-vtable) and, for two of them, also the banned `_v` suffix.  Per Lon's fourth-pass directive ("Eradicate it from docs and source. I do not want to see it ever again"), deletion is cleaner than rename for dead code.  Doc-comment placeholder explains the eradication and the rule for future emitters (use `emit3c_label`-style names if three-column helpers are ever wanted again).

**Tightened static-analysis invariants — all three pass:**

```
grep -rE '\bemit_v\b|\bemitter_v\b|\bEMITTER_V\b' src/runtime/x86/    empty
grep -rEn '\b[a-z][a-zA-Z0-9_]*_v\s*\(' src/runtime/x86/              empty
grep -rn '\bev3c' src/runtime/x86/                                    one doc-comment archaeology hit
```

The first invariant has been in place since the fourth-pass watermark below; the second and third are newly tightened to also catch the `_v` function-name suffix and the `ev3c` family.

**Gates (all green):**
- `build_scrip.sh`, `libscrip_rt.so` rebuild: clean.
- `test_smoke_snobol4.sh`: 7/7.
- `test_smoke_unified_broker.sh`: 49/49.
- `test_smoke_snocone.sh`: 5/5.
- `test_gate_em_template_byte_identity.sh`: 4/4.
- `build_and_run_test_template_byte_identity.sh`: PASS.
- `test_smoke_snobol4_jit.sh`: `--sm-run` 197/64, `--jit-run` 197/64, three-mode parity on crosscheck: 133 programs.
- `git stash`/`pop` byte-diff on `claws5.s`: empty (byte-identical).

**one4all commit:** `55ef787f`.

----



**_v eradication-directive incomplete — three survivors flagged sess 2026-05-11 (Claude Opus 4.7, latest)**

Post-handoff inspection (Lon's question: "what does the v in `flat_emit_body_v` stand for?") surfaced three function names that should have been caught by sub-rung -a's fourth-pass `_v` eradication but slipped through because the static-analysis grep was scoped narrowly to `emit_v|emitter_v|EMITTER_V` literal patterns, not the broader `_v` function-name suffix convention.

**Survivors:**

| File | Symbol | Meaning of the `v` |
|------|--------|--------------------|
| `src/runtime/x86/bb_flat.c:1545` | `flat_emit_body_v` | "takes an `emitter_t *` (vtable-style emitter argument)" — exactly the banned convention |
| `src/runtime/x86/emitter.h:399` | `ev3c_action_v` | doubly cursed — `ev_` prefix + `_v` suffix; the latter may also denote vprintf-style va_args |
| `src/runtime/x86/emitter.h:417` | `ev3c_goto_v`   | same as above |

Per Lon's directive captured in the fourth-pass watermark below: "Scrap the use of the character V or v for this concept here. It means nothing. Get rid of it. Eradicate it from docs and source. I do not want to see it ever again."  The directive applies; the rename was simply missed.

**Carved as follow-on rung (not landed this session):** small mechanical rename
- `flat_emit_body_v` → `flat_emit_body` (call site at bb_flat.c lines 1637 and 1655 updated)
- `ev3c_action_v` → `emit3c_action_va` or similar (preserving va_args connotation if that's the actual reason for the `_v` here — verify before rename)
- `ev3c_goto_v` → `emit3c_goto_va` likewise
- Tighten the static-analysis invariant to also catch `_v\b` (function-name suffix) and `\bev[0-9_]` (ev3c-style prefixes), in addition to the existing `emit_v|emitter_v|EMITTER_V` patterns

**Risk:** trivial.  Pure rename, no behavior change.  Three call sites total across the codebase.

**Pre-read for the follow-on rung:** this watermark; the fourth-pass watermark below (Lon's verbatim directive); the fifth-pass watermark (which clarified `em_` → `emit_`).

**Gates:** no code change this addendum.  All gates unchanged from prior handoff hashes (one4all `f74db5bf`, .github `fd1e3fc`).

----



**EM-MODE4-IS-MODE3-DUMP-d closed (BB side proven; bb_xchr template byte-identical) — sess 2026-05-11 (Claude Opus 4.7, latest)**

Sub-rung -d lands cleanly with full closure (unlike -c, which is
partial pending the SM_HALT mode-3-vs-mode-4 A/B/C decision).  The
contrast is instructive: BB boxes are template-shaped already in
the existing codebase (`flat_emit_lit` and its siblings take an
`emitter_t *e` and call vtable methods exclusively), so the
"first BB template" rung is largely a *relocation* with namespace
cleanup, not new architecture.  The 106/106-vs-SPITBOL property
that earlier watermarks credited to the BB-side vtable carries
through unchanged — the template lives in a different file but is
the same function body.

**Key finding: BB-side templates have no mode-3/mode-4 divergence
analogous to SM_HALT's.**

Mode-3 (in-process JIT) and mode-4 (standalone binary) call the same
runtime symbols for BB-box semantics (`memcmp`, `bb_label_*`,
`bb_brk`/`bb_any`/`bb_notany`/`bb_span`, etc.) and read/write the
same global subject-string anchors (`Σ`, `Σlen`, `Δ`).  The only
binary-vs-text difference is *how* literal-string pointers are
addressed — RIP-relative symbol (text, via `BB_INSN_LEA_RCX_SYM`)
vs imm64 raw pointer (binary, fallback in the same vtable kind).
The existing emitter vtable absorbs this entirely.

This means: **for sub-rungs that touch only BB boxes, the SM_HALT
A/B/C decision is not blocking.**  The template machinery can be
populated across all BB box kinds (sub-rungs -d through -p as they
fall within the BB axis of the alternation) without waiting on Lon.
Subsequent SM-side sub-rungs do block on the decision because
SM_TPL_NULLARY and SM_TPL_RET both face the same mode-3-vs-mode-4
question (rt_halt_tos for HALT; bare `ret` for RETURN that mode-3
treats one way and mode-4 must wrap with libscrip_rt-aware exit).

**What landed:**

- `src/runtime/x86/templates/bb_xchr.c` — NEW file, 121 lines.
  Defines `void emit_bb_xchr(emitter_t *e, PATND_t *p, lbl_succ,
  lbl_fail, lbl_β)`.  Body lifted byte-for-byte from the previous
  `flat_emit_lit` (in bb_flat.c) plus the inline banner-emission
  in `flat_emit_node`'s XCHR case.  Combined into one function
  because both halves emit the *same* BB box (the banner introduces
  the literal-match sequence; they're a unit).

- `src/runtime/x86/templates/templates.h` — restructured.
  All dependency pull-ins moved to top of file (`snobol4.h`,
  `emitter.h`, `bb_emit.h`, `snobol4_patnd.h`) so any caller gets
  every type it needs by including this one header.  Avoids the
  forward-declaration ordering trap when a template references a
  type from another header.  `emit_bb_xchr` declaration added.

- `src/runtime/x86/bb_flat.h` — two prototypes added.
  `flat_emit_banner_rule(emitter_t *e, char ch)` and
  `flat_emit_box_banner(emitter_t *e, const char *kind, const char
  *args, const char *label_prefix)`.  Both were `static` in
  `bb_flat.c`; promoted to external linkage so per-box template
  files can call them.

- `src/runtime/x86/bb_flat.c` —
  - `#include "templates/templates.h"` added.
  - `flat_emit_banner_rule` and `flat_emit_box_banner` lose
    `static` keyword (definitions match the now-public declarations).
  - `flat_emit_lit` marked `__attribute__((unused))` and retained
    as rollback reference + byte-identity oracle.
  - The XCHR case in `flat_emit_node` collapses from 10 lines
    (preview formatting + banner call + `flat_emit_lit` call) to
    a single `emit_bb_xchr(e, p, lbl_succ, lbl_fail, lbl_β)` call.

- `Makefile` — `templates/bb_xchr.c` added to scrip rule (line 244)
  AND to `RT_PIC_SRCS` (libscrip_rt.so).  Unlike `sm_halt.c` which
  is called only from `sm_codegen.c` (not in libscrip_rt), `bb_xchr.c`
  is called from `bb_flat.c` which IS in libscrip_rt.  Both build
  targets include the file.

**Gates (all green):**

- `bash scripts/build_scrip.sh`: clean.
- `bash scripts/test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `bash scripts/test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `bash scripts/test_smoke_snocone.sh`: PASS=5 FAIL=0.
- `bash scripts/test_smoke_snobol4_jit.sh`: `--sm-run` 197/64,
  `--jit-run` 197/64 — three-mode parity preserved across the
  261-program crosscheck.  XCHR is exercised heavily here (literal
  match is in nearly every pattern); identical pass/fail numbers
  prove byte-for-byte preservation.
- `bash scripts/test_gate_em_template_byte_identity.sh`: 4/4 PASS
  (the sub-rung -c gate; XCHR-via-template doesn't change SM_HALT
  emission).
- `bash scripts/build_and_run_test_template_byte_identity.sh`:
  PASS (sub-rung -c unit test; still verifies the literal byte
  sequence `41 ff 45 14 c3` for SM_HALT).
- `git stash`/`pop` byte-diff on `claws5.s` (the tracked artifact
  with the most LIT BOX banners — 4 of the 6 total across the 5
  tracked artifacts): **empty diff**.  Definitive proof that the
  XCHR template lifts the body byte-for-byte; mode-4 `.s` output
  is unchanged at the byte level.
- `-Wall -Wextra -Wno-unused-parameter -Wno-unused-function` on
  the new `templates/bb_xchr.c` and on the modified `bb_flat.c`:
  zero new warnings.  (One pre-existing `unused-variable d2`
  warning inside the now-unused `flat_emit_lit` body — verified
  via `git stash`/`pop` to predate sub-rung -d; not introduced
  here, not in scope to fix.)

**Tracked-artifact post-rung confirmation:**

| File             | Lines | LIT BOX banners | `gcc -c` |
|------------------|------:|----------------:|:--------:|
| roman.s          |    71 | 0               | OK       |
| wordcount.s      |   121 | 0               | OK       |
| claws5.s         |   868 | 4               | OK       |
| treebank-list.s  |  1104 | 0               | OK       |
| treebank-array.s |  1284 | 2               | OK       |

Line counts identical to post-sub-rung-b baseline.  6 LIT BOX
banners across the 5 artifacts, all now produced by the template.

**Static-analysis invariants:**

- `grep -rE 'emit_v|emitter_v|EMITTER_V' src/runtime/x86/` — empty.  Holds.
- `grep macro_ src/runtime/x86/templates/bb_*.c` — empty.  HOLDS
  (no longer vacuously — `bb_xchr.c` exists; verified that it
  contains zero `macro_` calls, consistent with BB-template
  discipline).

**Sub-rung -e (next session — no decision required to proceed):**

The next alternating-axis rung is **sm_push_lit_i**.  This SM
opcode emits inline native code that loads a constant integer
onto the value stack via `rt_push_int`.  Like SM_HALT, it has a
mode-3 (in-process) byte-pattern and a mode-4 (macro invocation
`PUSH_INT val`) text-pattern — and likely *the same* mode-3-vs-
mode-4 divergence pattern as SM_HALT (`call rt_push_int@PLT` in
mode-4 vs inline byte sequence in mode-3).

**If Lon has decided A/B/C by then,** the SM_PUSH_LIT_I retrofit
follows the decided shape.  Mode-3 wires through the template;
mode-4 either wires through it (Option A — change mode-4 to
match mode-3) or stays inline (Option B/C — template-as-mode-3-
only, document divergence).

**If the decision is still open,** the BB-axis alternation
continues: sub-rung -e becomes another BB box (XSPNC — span box,
next-simplest after XCHR) and sm_push_lit_i waits as -e' or -f.

**Pre-read for sub-rung -e (whichever it is):**
1. `templates/sm_halt.c` and `templates/bb_xchr.c` (the two patterns).
2. `MIGRATION-MODE4-IS-MODE3-DUMP.md` §"The template-as-program".
3. The "KNOWN OPEN ARCHITECTURAL QUESTION" in sub-rung -c watermark
   (below).
4. This watermark.
5. For BB-axis: `bb_flat.c` `flat_emit_charset_call` (XSPNC's
   current emit path).
6. For SM-axis: `sm_codegen.c` `emit_push_int_lit_blob` (or
   equivalent SM_PUSH_LIT_I site) and `sm_codegen_x64_emit.c`
   `emit_sm_push_lit_i`.

----



**EM-MODE4-IS-MODE3-DUMP-c PARTIAL LANDING (mode-3 wired; mode-4 blocked on design question) — sess 2026-05-11 (Claude Opus 4.7, latest)**

Sub-rung -c was carved as "first SM opcode end-to-end: SM_HALT,
mode-3 + mode-4 + sm_macros.s through one template."  The mode-3
portion is fully landed and gated.  The mode-4 portion surfaced an
architectural contradiction between the design doc and existing
production code that I deliberately did not silently resolve.  The
sub-rung is therefore left `[ ]` with a partial-landing note, pending
Lon's decision on direction.

**The architectural contradiction.**

Mode-3's current `emit_halt_blob` emits 5 bytes:
```
  41 ff 45 14   ; inc dword [r13 + 20]  — st->pc++
  c3            ; ret                    — return to sm_jit_run's C caller
```

Mode-4's current `emit_sm_halt` (in `sm_codegen_x64_emit.c`) emits a
single GAS line:
```
  HALT                    ; macro invocation
```
whose body, defined by `sm_emit_template.c` SM_TPL_NULLARY arm, expands to:
```
  call rt_halt_tos@PLT    ; PLT call into libscrip_rt.so
```

These are NOT the same instructions.  The environments differ:
mode-3 runs in-process (r13 is a live SM_State pointer; ret unwinds
to sm_jit_run's C frame); mode-4 is a standalone binary linked
against `libscrip_rt.so` (no sm_jit_run; rt_halt_tos handles exit-
code propagation; main() wrapper handles termination).

The design doc's SM_HALT example
(`MIGRATION-MODE4-IS-MODE3-DUMP.md` §"The template-as-program") shows
the *mode-3* form as the output of *all three* backends.  But mode-4
today produces something structurally different, and the design
doc's stated invariant ("templates do not branch on the backend")
forbids the obvious workaround.

**Three coherent paths forward** (Lon decision):

| Option | Description | Cost |
|--------|-------------|------|
| **A** | Honor the design doc.  Change mode-4 to emit `inc [r13+20]; ret` like mode-3.  Mode-4's main() / libscrip_rt absorbs whatever rt_halt_tos was doing for exit-code propagation. | Behavioral change to mode-4 emission; mode-4 binaries become byte-identical to mode-3.  Strong "one source of truth." |
| **B** | Honor existing code.  Templates acknowledge per-backend dispatch via backend-conditional surface methods (e.g. `e->exit_via_ret_or_plt_halt()`).  This contradicts the design doc's "templates do not branch on backend" rule.  Effectively withdraws part of the design doc. | Documentation churn.  Templates become slightly less pure but more honest about reality.  Probably the right answer for opcodes where mode-3 and mode-4 must legitimately diverge. |
| **C** | Define different scope for some opcodes.  SM_HALT is special — it's terminative.  Most opcodes (arithmetic, pushes, jumps, calls into runtime) likely DO match across mode-3 and mode-4 because both call into the same runtime symbols.  SM_HALT can stay mode-3-only-templated; the rest of the retrofit (sub-rungs -d through -p) goes per-design and most won't surface this problem. | Smallest change; pragmatic.  Loses "every opcode through one template" property for the handful of opcodes that genuinely differ.  Probably the right operational answer: build the machinery, exempt the few opcodes that can't fit, document why. |

I cannot resolve A vs B vs C alone — the decision affects the
backbone of every subsequent sub-rung.  Stopping here for direction.

**What landed:**

- `src/runtime/x86/emitter.h`:
  - New `BB_INSN_INC_MEM_R13_DISP8` enum kind (a2 carries disp8;
    used by SM_HALT and future SM opcodes that touch SM_State
    integer fields).
  - New inline helper `emit_inc_mem_r13_disp8(e, disp)`.

- `src/runtime/x86/emitter_binary.c`:
  - Impl for the new kind: 4 bytes `41 ff 45 <disp8>`.

- `src/runtime/x86/emitter_text.c`:
  - Impl for the new kind: `inc dword ptr [r13 + N]` three-column line.

- `src/runtime/x86/templates/sm_halt.c` — NEW file, 92 lines.
  - First per-opcode template: `void emit_sm_halt(emitter_t *e)`.
  - Body (sprinkle model): `e->comment(...)`, `emit_inc_mem_r13_disp8(e, 20)`,
    `emit_ret(e)`, `e->pad_to_blob_size(e)`.
  - Extensive header comment documenting the KNOWN OPEN
    ARCHITECTURAL QUESTION (the mode-3/mode-4 divergence above),
    the byte-identity invariant, the sub-rung scope decision, and
    the rollback path.

- `src/runtime/x86/templates/templates.h` — NEW file.
  - Aggregates template declarations; `void emit_sm_halt(emitter_t *e)`.
  - Documents naming convention; will grow with each subsequent
    rung as templates are added.

- `src/runtime/x86/sm_codegen.c`:
  - `+include` for templates.h, bb_emit.h, emitter.h.
  - Legacy `emit_halt_blob` kept with `__attribute__((unused))` —
    serves as rollback reference + byte-identity oracle (the gate
    invariant is "template output == legacy output", and the legacy
    function's literal `seg_byte(SEG_CODE, 0x41); seg_byte(..., 0xff);
    seg_byte(..., 0x45); seg_byte(..., 0x14); seg_byte(..., 0xc3);`
    is the canonical reference).
  - New `emit_halt_blob_via_template()` adapter (capture-and-flush
    pattern): allocates a 16-byte temp buffer, constructs a binary
    emitter targeting it, runs the template, sanity-checks length,
    then `seg_byte`s the captured bytes into SEG_CODE.  Aborts on
    template-bug (length != 5) rather than corrupting SEG_CODE.
  - SM_HALT case in the pass-1 dispatcher (line ~3151) calls
    `emit_halt_blob_via_template()` instead of `emit_halt_blob()`.
    Single-line revert if needed.

- `src/runtime/x86/test_template_byte_identity.c` — NEW unit test.
  - Drives `emit_sm_halt` through a binary emitter, compares the
    resulting bytes to the literal expected sequence
    `41 ff 45 14 c3` byte-for-byte.  Also checks a sentinel
    (pre-fill 0xAB) past the 5-byte boundary to catch overruns.

- `src/runtime/x86/demo_template_productions.c` — NEW (not a test).
  - Drives `emit_sm_halt` through all three backends and prints the
    output side-by-side.  Useful for Lon when evaluating Option A
    vs B vs C.

- `scripts/test_gate_em_template_byte_identity.sh` — NEW gate.
  - Behavioral: runs four small SNOBOL4 programs (immediate halt,
    halt after arith, halt after match, halt after loop) under
    both `--sm-run` (interpreter, byte-identity oracle) and
    `--jit-run` (mode-3, walks SEG_CODE through the template's
    SM_HALT blob); requires output equality.  Catches any template
    bug that produces semantically-different bytes.

- `scripts/build_and_run_test_template_byte_identity.sh` — NEW.
  - Builds and runs the unit test above.  Stronger than the
    behavioral gate because it catches equivalent-but-different
    encodings of the same operation.

- `Makefile`:
  - `templates/sm_halt.c` added to scrip rule (line 243).  NOT
    added to `RT_PIC_SRCS` — libscrip_rt.so does not include
    `sm_codegen.c`, and the template is only called from there
    today.  When mode-4 wiring lands, that may change.

**Gates (all green):**

- `bash scripts/build_scrip.sh`: clean.
- `bash scripts/test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `bash scripts/test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `bash scripts/test_smoke_snocone.sh`: PASS=5 FAIL=0.
- `bash scripts/test_smoke_snobol4_jit.sh`: `--sm-run` 197/64,
  `--jit-run` 197/64 — three-mode parity preserved (and confirms
  SM_HALT-via-template is byte-identical to SM_HALT-via-legacy
  across the 261-program crosscheck).
- `bash scripts/test_gate_em_template_byte_identity.sh`: PASS=4
  FAIL=0.
- `bash scripts/build_and_run_test_template_byte_identity.sh`:
  PASS (5 bytes, exact match `41 ff 45 14 c3`, sentinel intact).
- `-Wall -Wextra -Wno-unused-parameter -Wno-unused-function` on
  `sm_halt.c`, `emitter_text.c`, `emitter_binary.c`: zero warnings.

**Visual demo output (for Lon, when deciding A/B/C):**

```
=== emit_sm_halt — BINARY backend ===
  bytes (5 total): 41 ff 45 14 c3
  meaning: inc dword [r13+20] ; ret

=== emit_sm_halt — TEXT_INVOCATION backend ===
    # SM_HALT — exit sm_jit_run via ret
                        inc              dword ptr [r13 + 20]
                        ret

=== emit_sm_halt — TEXT_DEFINITION (== MACRO_DEF) backend ===
    # SM_HALT — exit sm_jit_run via ret
                        inc              dword ptr [r13 + 20]
                        ret
```

The TEXT_DEFINITION output is identical to TEXT_INVOCATION because
the template body doesn't call `macro_begin`/`macro_end` (that would
wrap with `.macro HALT ... .endm`).  Adding those calls is trivial
once Lon picks Option A (single source of truth) over Option B/C.

**Static-analysis invariants:**

- `grep -rE 'emit_v|emitter_v|EMITTER_V' src/runtime/x86/` — empty.  Holds.
- `grep macro_ src/runtime/x86/templates/bb_*.c` — empty (vacuously,
  no BB templates yet).

**Sub-rung -d (next session, IF Lon picks Option B or C):**

Sub-rung -d (`bb_xchr`, the first BB box template) is mostly
independent of the mode-3/mode-4 SM_HALT decision because BB boxes
have no `sm_macros.s` involvement and BB invocation paths are the
same in both modes.  -d could land in parallel with the A/B/C
decision.  -c-mode4 (closing the mode-4 portion of -c) waits for
the decision.

**Pre-read for next session:**
1. `templates/sm_halt.c` (header comment in full).
2. This watermark (the "architectural contradiction" section).
3. `MIGRATION-MODE4-IS-MODE3-DUMP.md` §"The template-as-program".
4. `sm_emit_template.c` lines 273-310 (the existing
   `render_macro_body` SM_TPL_NULLARY arm — what mode-4's HALT
   does today).
5. The visual demo output above.

Required first action (sub-rung -d): no decision required, can
proceed.  Required first action (sub-rung -c-mode4 or whichever
follow-up closes -c): Lon picks A / B / C; agent reads the picked
path's implications and proceeds.

----



**EM-MODE4-IS-MODE3-DUMP-b landed (vtable skeleton, narrow-shape resolution) — sess 2026-05-11 (Claude Opus 4.7, latest)**

Sub-rung -b lands as the structural setup the sub-rung header
prescribed.  Three deliverables, zero behavior change to live code.

**Surface-design tension resolved: narrow vtable retained.**  The
fifth-pass watermark (below) flagged a choice between the existing
narrow-vtable shape (one `emit_insn(e, &desc)` method + many inline
helpers building `bb_insn_desc_t`) and the design doc's wide-vtable
proposal (one function pointer per x86 instruction).  Decision:
narrow.  Reasons:

1. Proven: the existing `emit_insn` + `bb_insn_desc_t` carries 106/106
   parity against SPITBOL on the BB side today.  Replacing it is risk
   for no gain.
2. Opcode-level primitives the design doc lists (mov_reg_imm64,
   call_reg, ret, push_reg, lea_rip_sym, ...) are already absorbed by
   `BB_INSN_*` enum members.  Sub-rung -c will add new `BB_INSN_*`
   kinds (e.g. `BB_INSN_INC_MEM_DISP8` for SM_HALT's `inc [r13+20]`)
   as templates demand them.  Bounded change per new instruction.
3. The "sprinkle" model (templates calling comment/banner/blank-line
   alongside instruction emission) works fine with narrow vtable —
   those calls *are* new methods on the vtable, orthogonal to
   `emit_insn`.
4. The wide-vtable proposal would duplicate, not replace, what the
   desc-based machinery already does — two ways to spell each
   instruction.

**What landed:**

- `src/runtime/x86/emitter.h` — new vtable methods appended after the
  existing 7 (label_define, emit_jmp, ..., intern_str):
  - **Structural markers:** `label_name`, `pc_label`, `section`,
    `directive`, `data_quad`, `data_quad_sym`, `data_string`,
    `pad_to_blob_size`
  - **BB-port primitives:** `bb_port_label`, `bb_port_jmp`,
    `bb_box_banner`
  - **Formatting:** `comment`, `banner`, `minor_break`, `blank_line`
  - **macro_def hooks:** `macro_begin`, `macro_param_ref`, `macro_end`
  - New field `text_mode` of type `emitter_text_mode_t` (enum
    `TEXT_MODE_INVOCATION` / `TEXT_MODE_DEFINITION`) selects how
    macro-begin/end render in the text backend
  - New `EMIT_OPT(e, method, ...)` NULL-safe helper macro
  - New constructor `emitter_text_new_mode(out, mode)`; legacy
    `emitter_text_new(out)` keeps the default INVOCATION mode

- `src/runtime/x86/emitter_text.c` — implementations for every new
  method above.  Text-DEFINITION mode emits `.macro NAME params ...
  .endm` blocks; text-INVOCATION mode emits a single `NAME args` line
  with subsequent body emissions suppressed by a per-backend flag
  until `macro_end`.  All implementations route through the existing
  `bb3c_format` machinery where three-column shape is expected
  (`label_name`, `pc_label`, `data_quad`, …) so the readability rules
  established by EM-FORMAT-* rungs are preserved automatically.

- `src/runtime/x86/emitter_binary.c` — vtable slots filled in.
  `data_quad` / `data_string` emit real bytes via `bb_emit_u64` /
  `bb_emit_byte`.  Everything else is a faithful no-op per the
  design doc; binary backend's only job is bytes-into-SEG_CODE, and
  the formatting/banner/comment surface has no byte equivalent.
  Stubs return cleanly so callers in -c onward don't crash on calls
  the binary backend chooses to ignore.

- `src/runtime/x86/emitter_macro_def.c` — new file, 41 lines.  Thin
  wrapper: `emitter_macro_def_new(out)` calls
  `emitter_text_new_mode(out, TEXT_MODE_DEFINITION)`.  No separate
  free needed — `emitter_free` already handles the underlying text
  emitter.

- `src/runtime/x86/templates/` — new directory + `README.md`
  documenting the per-opcode-template convention, the three-backend
  matrix (binary / text / macro_def), the SM-only nature of
  macro_def, the file-naming convention (`sm_<opcode>.c` /
  `bb_<kind>.c`), and the static-analysis invariant for BB-template
  macro discipline.

- `Makefile` — `emitter_macro_def.c` added to the `scrip` rule's
  compilation line (line 195) and to `RT_PIC_SRCS` (line 80).

**Gates (all green, both before and after this rung):**

- `bash scripts/build_scrip.sh`: clean.
- `bash scripts/test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `bash scripts/test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `bash scripts/test_smoke_snocone.sh`: PASS=5 FAIL=0.
- `bash scripts/test_gate_em_beauty_subsystems_mode4.sh`: PASS=0
  FAIL=17 (all link) — **unchanged from session start**.  Pre-
  existing link issue (libscrip_rt.so missing `coro_bb_*`,
  `bb_eval_value`, `icn_call_builtin`, `kw_assign`, and 6+ more
  symbols) is NOT a one-line Makefile edit as the prior watermark
  guessed — adding `coro_runtime.c` alone pulls in 10+ transitive
  symbols.  Carved as future housekeeping rung (call it
  `EM-MODE4-LIBSCRIPRT-LINK`).  Not in scope of -b.
- `-Wall -Wextra -Wno-unused-{parameter,variable,function}` on the
  three emitter files: zero warnings.  (Initial pass had `multichar`
  + `switch-outside-range` warnings from a `case 'α':` clause;
  fixed by dropping the Greek-glyph case labels and accepting only
  ASCII `a`/`b`/`g`/`o` as input — the design doc specifies ASCII as
  the canonical template input anyway.)

**Tracked-artifact note:** The 5 tracked `.s` artifacts emit + `gcc -c`
clean post-rung.  Line counts (71, 121, 868, 1104, 1284) differ from
the rung-header's stated baseline (151, 124, 949, 1176, 1355).  This
delta predates -b — fourth-pass watermark noted the same delta
versus corpus copies and flagged it as a *pre-existing* pattern-blob
emission regression for a separate session.  Sub-rung -b's emission
path is byte-identical to its pre-rung path (no live caller of the
new vtable surface yet), so this delta is not caused by -b.  Corpus
copies of `*.s` left untouched on disk.

**Static-analysis invariant: `_v` ban.**
`grep -rE 'emit_v|emitter_v|EMITTER_V' src/runtime/x86/` returns
empty.  Holds.

**Static-analysis invariant: BB-template macro discipline.**
`grep macro_ src/runtime/x86/templates/bb_*.c` returns nothing —
vacuously holds (no BB templates yet; sub-rung -d adds the first).

**Surface-design rationale captured for sub-rung -c:**

The sprinkle model expresses cleanly under narrow vtable.  A template
like:

```c
void emit_sm_halt(emitter_t *e) {
    e->banner       (e, "SM_HALT");
    e->comment      (e, "exit via ret");
    e->macro_begin  (e, "HALT", NULL, 0);
    /* inc qword ptr [r13+20] — pc++ */
    e->inc_mem_disp8(e, REG_R13, 20);   /* if -c adds this method,
                                         * OR routes via emit_insn
                                         * with a new BB_INSN_*    */
    e->ret          (e);                 /* same                    */
    e->macro_end    (e);
    e->pad_to_blob_size(e);
}
```

Under narrow-vtable, `inc_mem_disp8` and `ret` are added as inline
helpers (`emit_inc_mem_disp8`, `emit_ret` — the latter already
exists) building `bb_insn_desc_t` and dispatching through
`emit_insn`.  `banner`, `comment`, `macro_begin`, `macro_end`,
`pad_to_blob_size` are the vtable methods this rung added.  No
mixed-model gymnastics needed.

**Next session:** sub-rung -c (SM_HALT, the first template).
Required first action: read this watermark + the rung header (which
points at `MIGRATION-MODE4-IS-MODE3-DUMP.md`).  Sub-rung -c work:

1. Create `src/runtime/x86/templates/sm_halt.c` with
   `void emit_sm_halt(emitter_t *e)`.
2. Add any new `BB_INSN_*` kinds the template needs (likely
   `BB_INSN_INC_MEM_DISP8`) to `emitter.h` and impl in both
   `emitter_text.c` and `emitter_binary.c`.
3. Route mode-3's existing `emit_halt_blob` (or equivalent) call site
   in `sm_codegen.c` through `emit_sm_halt(emitter_binary_new(...))`.
4. Route mode-4's existing SM_HALT emission site in
   `sm_codegen_x64_emit.c` through `emit_sm_halt(emitter_text_new(...,
   TEXT_MODE_INVOCATION))`.
5. Generate `sm_macros.s` HALT entry from
   `emit_sm_halt(emitter_macro_def_new(...))` via new
   `tools/regen_macros.c`.
6. Verify byte-identity: mode-3's HALT bytes pre- vs post-rung.
   Verify text shape: mode-4's HALT line pre- vs post-rung.
7. New gate `test_gate_em_template_byte_identity.sh` validates the
   above mechanically.

⛔ **Pre-read for sub-rung -c:**
1. `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` (the design doc).
2. `ARCH-x86.md` (whole file).
3. `ARCH-SCRIP.md` (whole file).
4. The `EM-MODE4-IS-MODE3-DUMP` rung header above.
5. This watermark.

----



**EM-MODE4-IS-MODE3-DUMP-a amended (fifth pass: `em_` → `emit_`; `EMIT_V` reverted) — sess 2026-05-11 (Claude Opus 4.7, latest)**

Two corrections from Lon to the fourth pass:

1. **`em_` → `emit_`.**  The helper-namespace rename I chose
   (`ev_*` → `em_*`) used unfamiliar shorthand.  "emit" is the
   actual word and matches `emit_insn` — the vtable's central
   method — already in use everywhere.  Helpers are now named
   `emit_mov_rax_imm64`, `emit_load_delta`, `emit_call_rax`,
   `emit_jmp`, etc.  Reads as the verb the function does.

   115 substitutions across `emitter.h` (63) and `bb_flat.c` (52).
   Pre-checked for collisions: zero — `em_insn0` → `emit_insn0`
   is distinct from `emit_insn` (the vtable method).  Build and
   gates clean.

2. **`EMIT_V` in `snocone_lex.c` reverted.**  Fourth pass had
   renamed it to `EMIT_VAL`.  Lon corrected: the `V` there stands
   for *value-token* in the lexer's EMIT-this-as-a-value macro,
   not for vtable.  Unrelated to the emitter concept.  Reverted
   to original `EMIT_V` — 6 sites + 2 comment refs back to their
   pre-fourth-pass form.

**Lon's principle, captured for future sessions:** "ignore `_V`
where it does not apply to our concept, emitters, here.  So do not
change any unrelated code."  The directive targets the emitter-
vtable convention specifically.  Other code that happens to have a
`_V` or `_v` suffix for unrelated reasons (value-token macros,
math vectors, version literals, etc.) is **out of scope** and
must not be touched.

**Gates after corrections:**

- Build: clean.
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_snocone.sh`: PASS=5 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- 5/5 tracked artifacts emit + `gcc -c` clean.

**Updated static-analysis invariant:**

```
grep -rE 'emit_v|emitter_v|EMITTER_V' src/runtime/x86/
```

returns empty.  Note the scope tightened: BOTH expressions are
restricted to `src/runtime/x86/` (the emitter subsystem) so that
unrelated `_V` usage elsewhere — Snocone's value-token macro,
math/vector code, etc. — is not affected.  The directive bans
`_v`/`_V` as an *emitter-naming convention*; it does not ban the
letter V everywhere.

**Final name set for the emitter subsystem:**

| Concept | Name |
|---------|------|
| Header  | `emitter.h` |
| Vtable type | `emitter_t` |
| Backends | `emitter_binary`, `emitter_text`, `emitter_macro_def` |
| Inline helpers | `emit_*` (e.g. `emit_mov_rax_imm64`, `emit_call_rax`, `emit_load_delta`) |
| Vtable method | `emit_insn` |

**Surface-design tension flagged for sub-rung -b to resolve:**

The existing `emitter.h` has ONE primary vtable method
(`emit_insn(e, &desc)` taking a `bb_insn_desc_t` with typed
operand slots) and MANY inline helpers that build `bb_insn_desc_t`
and dispatch through it.  The design doc as currently written
proposes MANY vtable methods (one per x86 instruction: `mov_reg_imm64`,
`call_plt`, `ret`, …) with NO helper layer.

These are two different shapes:

- **Existing (BB-side prior art):** narrow vtable, wide helper
  layer.  Adding a new instruction = new kind enum + new `BB_INSN_*`
  case in each backend's `emit_insn` switch + new inline helper.
- **Proposed in design doc:** wide vtable, no helper layer.  Adding
  a new instruction = new function pointer slot + new method
  in each backend's struct.

Sub-rung -b chooses one.  Recommendation (to be confirmed at -b
entry): keep the existing narrow-vtable / wide-helper shape — it's
proven (106/106 against SPITBOL oracle), the helper layer is the
natural place for sprinkle (helpers can wrap their `emit_insn`
call with `e->comment(...)` and other formatting calls
trivially), and the kind enum + desc struct centralize what each
instruction *means* in one place rather than scattering it across
backend impls.

Design doc will be amended in sub-rung -b to reflect the chosen
shape.  Today's doc text describing the wide-vtable proposal stays
as historical context.

Ready for sub-rung -b.

----



**EM-MODE4-IS-MODE3-DUMP-a amended (fourth pass: `_v` banned; rename across source + docs) — sess 2026-05-11 (Claude Opus 4.7, later)**

Lon's directive: `_v` (and the `ev_` prefix it spawns) is banned
project-wide.  "Scrap the use of the character V or v for this
concept here.  It means nothing.  Get rid of it.  Eradicate it from
docs and source.  I do not want to see it ever again."

**Source rename landed in this commit:**

| Before              | After                              |
|---------------------|------------------------------------|
| `emitter_v.h`       | `emitter.h`                        |
| `EMITTER_V_H` guard | `EMITTER_H`                        |
| `emitter_v` struct  | `emitter_t`                        |
| `ev_*` helpers      | `em_*`                             |

7 files touched in the emitter rename:
- `src/runtime/x86/emitter.h` (renamed from `emitter_v.h`; 55+63 internal substitutions for the type and the inline helper namespace)
- `src/runtime/x86/emitter_binary.c` (11 substitutions: include + type refs)
- `src/runtime/x86/emitter_text.c` (17 substitutions: same)
- `src/runtime/x86/bb_emit.c` (1 include substitution)
- `src/runtime/x86/bb_flat.c` (39 + 52 substitutions: include, type refs, all `ev_*` helper call sites)
- `src/runtime/x86/bb_flat.h` (2 substitutions)
- `src/runtime/x86/sm_codegen_x64_emit.c` (1 include substitution)

8th file touched (Snocone lexer): `src/frontend/snocone/snocone_lex.c` — `EMIT_V` macro renamed to `EMIT_VAL` (6 sites + 2 comment refs).  Standalone `_V` suffix in capital case caught by the same directive — Lon's "I do not want to see it ever again" applies regardless of case.

Zero residuals: `grep -rE 'emit_v|emitter_v|\bev_[a-z]' src/runtime/x86/` returns empty for non-comment-stray hits.  The only remaining `ev_*` matches anywhere in `src/` are `ev_bin`, `ev_ftr`, `ev_tr` in `snobol4.c` — these are SNOBOL4 runtime event tokens (binary-event, ftrace-event, trace-event), unrelated to the emitter helper namespace, and predate this rung by years.  Left alone.

**Docs rename landed in this commit:**

`MIGRATION-MODE4-IS-MODE3-DUMP.md` — 99 occurrences scrubbed.
`emit_v.h` → `emitter.h`; `emit_v` (struct) → `emitter_t`;
`emit_v_binary.c` → `emitter_binary.c`; `emit_v_text.c` →
`emitter_text.c`; `emit_v_macro_def.c` → `emitter_macro_def.c`;
constructor/destructor names rebranded analogously.  Naming-note
section rewritten: no more "`_v` means vtable" claim; replaced with
"the existing `emitter_text.c` / `emitter_binary.c` use `emitter_t`,
and this rung extends the same vocabulary to SM."

`GOAL-MODE4-EMIT.md` — 17 occurrences scrubbed.  This watermark
appended on top; earlier third-pass watermark (the now-stale
"`_v` = vtable" pass) updated to reflect what actually landed.

**Gates after rename + rebuild:**

- `bash scripts/build_scrip.sh`: clean.
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- 5/5 tracked artifacts (`roman.s`, `wordcount.s`, `claws5.s`,
  `treebank-list.s`, `treebank-array.s`) regen + `gcc -c` clean.
  The regenerated `.s` files differ from corpus copies — but the
  un-renamed scrip at `32365d6a` produces the same 71-line roman.s
  as the renamed scrip, while corpus has 146 lines.  That delta
  predates this rename (pattern-blob emission regression already
  present at `32365d6a`).  Not caused by this rung; flagged for a
  separate session.
- Pre-existing libscrip_rt link issue from prior watermarks
  unchanged (still: `g_sm_dispatch_active` / `g_ast_pump_active`
  externs missing from the lib's Makefile rule).

**Why this rename is mandatory housekeeping for sub-rung -b:**

Sub-rung -b adds new files using this naming.  If we landed -b
without the rename, we'd introduce a *third* parallel naming
convention (the proposed `emit_v_*` files) alongside the existing
`emitter_v.h` and the legacy `ev_*` helpers — three styles for
one concept.  Doing the rename now, as part of -a, means -b adds
files that follow ONE established convention from day one.

**Next session:** sub-rung -b (vtable skeleton).  Header is
`emitter.h` (already exists; -b adds new entry-point declarations
to it).  Backends are `emitter_binary.c` (already exists; -b adds
new function pointer impls), `emitter_text.c` (already exists;
analogous), `emitter_macro_def.c` (new file).  No naming
ambiguity left.

⛔ **Static-analysis invariant for the project's life:**

```
grep -rE 'emit_v|emitter_v|\bev_(?!bin|ftr|tr)' src/
```

returns empty.  If any commit introduces `_v` or `ev_*` (other
than the three runtime-event tokens in `snobol4.c`), that commit
is regressing this directive and must be amended.

----



**EM-MODE4-IS-MODE3-DUMP-a amended (third pass: macro_def is SM-only) — sess 2026-05-11 (Claude Opus 4.7, later still)**

Third clarification from Lon, same session:

1. **macro_def is SM-only.**  BB templates never call
   `macro_begin / macro_end / macro_param_ref`; the
   `emitter_macro_def` driver never instantiates a BB template.
   Earlier doc framing left this ambiguous (showed `macro_def`
   as a generic third backend over both kinds); third pass makes
   the asymmetry explicit.

   The architectural reason: `sm_macros.s` is a library of
   parameterized GAS `.macro` definitions invoked from mode-4's
   per-call-site emission (`PUSH_INT 42`) to keep `.s` readable.
   Each SM opcode → one macro.  BB boxes have no such macro
   layer — each box appears in `.s` as straight-line asm with
   α/β/γ/ω labels, not wrapped in `.macro`.  Box parameters
   (literal bytes, csets, lengths) bake into DATA, not into macro
   args.  So there is no `bb_macros.s` regeneration counterpart
   and the macro_def driver iterates SM-only.

2. **Naming question raised about `_v` suffix.**  Earlier-pass
   note had claimed `_v` meant "vtable".  Fourth-pass watermark
   (above) records Lon's decision to ban the convention outright
   and the rename that followed.

**What changed in this amendment:**

- `MIGRATION-MODE4-IS-MODE3-DUMP.md`:
  - New section "macro_def is SM-only — the one asymmetry"
    between "SM and BB are co-equal" and "The 'sprinkle' model"
    sections.  Includes per-backend-by-template-kind matrix.
  - "Three backends" table at top gets an "Applies to" column
    noting macro_def is SM-only.
  - Sprinkle-model table gets two new rows for the BB-port
    primitives (`bb_port_label`/`bb_port_jmp` and `bb_box_banner`)
    explicitly marked "never reached" in the macro_def column.
- `GOAL-MODE4-EMIT.md`: this watermark.  Fourth-pass watermark
  (above) supersedes any naming claims made here.

**Static-analysis invariant** for the project's life:
`grep macro_ src/runtime/x86/templates/bb_*.c` returns zero hits.
If it ever returns anything, a BB template is incorrectly calling
into the SM-only macro surface and the offending file needs to
be rewritten without those calls.

**Gates:** unchanged (third pass was docs-only; fourth pass above
records the source rename + gate re-runs).

----



**EM-MODE4-IS-MODE3-DUMP-a amended (second pass: SM+BB co-equal; sprinkle model) — sess 2026-05-11 (Claude Opus 4.7, later)**

Second clarification from Lon, same session:

1. **Sprinkle model.**  A template C function can issue any call on
   the `emitter_t` surface — instruction emission, comment, banner,
   blank line, formatting, structural marker.  Each backend is free
   to implement or no-op any given call.  The surface is generous on
   purpose: comments and formatting are first-class calls, and a
   backend's right to ignore them is first-class too.  Worked SM_HALT
   example in the design doc shows the sprinkle in action.

2. **SM and BB are co-equal from day one.**  Earlier framing phased
   SM first ("BB-side discipline deferred").  Wrong — Lon corrected:
   every SM opcode AND every BB box gets its own template C file
   from the start.  They share `templates/` directory, the surface,
   and the backends.  Sequencing in the design doc updated to
   alternate SM ↔ BB landings so the gate surface is exercised
   from both directions during the retrofit.

**What changed in this amendment:**

- `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` — section
  "BB-side discipline (deferred…)" replaced with section "SM and BB
  are co-equal under this architecture"; full file-system layout
  shown with both `sm_*.c` and `bb_*.c` template files; sprinkle
  model section added with the per-call-category implement-or-no-op
  table; vtable surface expanded with BB-port primitives
  (`bb_port_label`, `bb_port_jmp`, `bb_box_banner`) and section/
  data primitives; sequencing replaced with co-equal SM+BB rungs
  (-a through -w).
- `.github/GOAL-MODE4-EMIT.md` — sub-rung list replaced to match
  (the b/c/d split is now: -b vtable skeleton, -c first SM opcode
  SM_HALT, -d first BB box bb_xchr, -e..-p alternating, -q SM_LABEL,
  -r SM_CALL_FN, -s RETURN family, -t remaining BB boxes, -u
  SM_PAT_*, -v macros generated, -w close).
- This watermark amended on top of the prior one.

**Gates:** unchanged (still docs-only).

- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `test_gate_em_beauty_subsystems_mode4.sh`: same pre-existing
  link issue documented in prior watermark below; not caused by
  this amendment.
- 5/5 tracked artifacts `gcc -c` clean.

**Next session:** sub-rung -b (vtable skeleton).  Pre-reads:
`MIGRATION-MODE4-IS-MODE3-DUMP.md` (post-amendment); `ARCH-x86.md`;
`ARCH-SCRIP.md`; this watermark.  Required first action: fix
`libscrip_rt` Makefile rule (add `coro_runtime.c`) so the
mode-4-beauty gate has a baseline to measure against.

----



**EM-MODE4-IS-MODE3-DUMP-a landed (template-vtable design doc + rung amendment) — sess 2026-05-11 (Claude Opus 4.7)**

Pivot from Lon: mode-4 will not be literal SEG_CODE disassembly.  It
will be ONE per-opcode C template per SM op, walked by an `emitter_t`
vtable with three concrete backends — binary (writes bytes to
SEG_CODE; replaces today's `sm_codegen.c` inline byte writes), text
(writes GAS asm text; replaces today's `sm_codegen_x64_emit.c`
parallel emitter), and macro_def (regenerates `sm_macros.s` so its
macros are produced from the same template, not hand-maintained).
Lon's clarification on Q5: keep `.s` readable — text backend emits
macro invocations like `PUSH_INT 42`, not the underlying instruction
sequence; the macro body is generated by macro_def from the same
template.  This means one source of truth per opcode, three
productions, divergence impossible by construction.

**What landed in this sub-rung:**

- `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` — full design: layers,
  vtable surface, three-call-site discipline, SM_HALT example
  template, sequencing plan (b through n).  This is the spec.
- `.github/GOAL-MODE4-EMIT.md` rung header amended: points at the
  design doc, replaces "SEG_CODE serialized to `.s`" framing with
  "one template per opcode, three backends."
- Sub-rung list replaced (-a through -n).  Old -a through -f
  preserved as "superseded" reference for git-log archaeology.

**What did NOT land:**

- Any code changes.  No emitter.h, no backend impls, no template
  files, no SEG_CODE plumbing changes.  Sub-rung -a is design only.
- Per Lon's expectation: "We want things almost right the first
  time."  Locking the design before any code prevents the next
  session from inferring a different architecture from
  half-implemented pieces.

**Gates:** unchanged (this commit is docs-only).

- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `test_gate_em_beauty_subsystems_mode4.sh`: **PRE-EXISTING regression observed sess 2026-05-11** — PASS=0 FAIL=17 (all link), not the watermark's stated PASS=4 FAIL=13.  Cause: `libscrip_rt.so` link fails with `undefined reference to g_sm_dispatch_active` / `g_ast_pump_active` — these are defined in `src/runtime/interp/coro_runtime.c` which is NOT in the library's source list in `Makefile`'s `libscrip_rt` rule.  Existed before this commit (this commit touches zero `.c` files; one new `.md` and two amended `.md`s).  Not caused by sub-rung -a.  Likely introduced in a recent CH-17g land where coro_runtime grew the tripwire globals but the library Makefile rule wasn't updated.  **Action for next session:** add `src/runtime/interp/coro_runtime.c` (and any sibling sources it depends on) to the `libscrip_rt` rule in `Makefile` to restore the PASS=4 baseline before opening sub-rung -b.  Should be a one-line edit to the Makefile.
- 5/5 tracked artifacts (`roman.s`, `wordcount.s`, `claws5.s`, `treebank-list.s`, `treebank-array.s`) `gcc -c` clean (verified separately).

**Files touched:**
- `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` — new (the design doc).
- `.github/GOAL-MODE4-EMIT.md` — rung header amended; sub-rung list
  replaced; this watermark added.
- `.github/PLAN.md` — to be updated to point at sub-rung -b as the
  active step.

**Next session:**

Open `EM-MODE4-IS-MODE3-DUMP-b` — vtable skeleton.  Add
`src/runtime/x86/emitter.h` with the struct from the design doc;
three skeleton backend impls (`emitter_binary.c`, `emitter_text.c`,
`emitter_macro_def.c`).  Wire into Makefile.  Nothing calls them yet.
Both gates green.  This is structural setup; SM_HALT (the first real
opcode retrofit) is sub-rung -c.

⛔ **Required pre-read for next session before touching any code:**
1. `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` (the design doc).
2. `ARCH-x86.md` (whole file).
3. `ARCH-SCRIP.md` (whole file).
4. The rung header for `EM-MODE4-IS-MODE3-DUMP` above (the amended
   one).
5. This watermark.

If a session-author finds the design doc contradicts what they think
mode-4 should do, they should resolve the contradiction by reading
the doc more carefully — the doc was written from the Lon pivot of
sess 2026-05-11 and is the source of truth for this rung.

----



**EM-7d-beauty-subsystems thunk PoC + ABI-register-handling redesign carved — sess 2026-05-10 (Claude latest)**

**Diagnosis + reverted PoC — no code landed.**  Per-chunk thunk
implementation (Option 1' from the prior watermark) was written,
built, and tested — moved the gate from PASS=4 FAIL=13 to PASS=5
FAIL=12 (Gen_driver started passing).  That confirms the alignment
hypothesis: rsp%16==8 from cfn() *is* the cause of the 13 diffs, and
inserting `sub rsp, 8` at chunk entry plus `add rsp, 8` before
returns *does* keep PLT calls aligned.  But the thunk approach is a
workaround, not a principled fix — Lon (correctly) called it out:
"why not redesign and handle registers properly and not use thunks?"
This watermark records the PoC numbers, the reverted code's shape,
and the proper redesign for the next session to land.

**Why thunks are wrong.**  A thunk shim
`.Lthunk_<pc>: sub rsp, 8 ; jmp .L<pc>` is a way to *manually* fix an
ABI violation that the chunk itself should fix in its prologue.
Production compilers don't emit thunks for alignment; they emit a
proper prologue:

```
chunk_entry:
    push rbp           ; save caller's rbp; rsp goes from %16==8 to %16==0
    mov  rbp, rsp      ; establish frame
    ...body...
    pop  rbp           ; restore caller's rbp; rsp goes from %16==0 to %16==8
    ret                ; pops 8-byte return address; rsp back to caller's
```

This is what `main()` already does in mode-4 (see `emit_file_header`
which emits `push rbp; mov rbp, rsp` at main entry).  Chunks should
do the same.  The `push rbp; mov rbp, rsp` IS the alignment-fix —
no separate `sub rsp, 8` needed.

**Why I drifted to thunks anyway.**  The dual-entry problem (a SNOBOL4
intra-function label like `assign1` in `assign_driver` is BOTH
cfn-callable via the expression registry AND fall-through-reachable
from inside the parent function) seemed to need runtime
distinction.  Per-chunk thunks side-step it by giving every cfn
entry a single-entry shim that doesn't see fall-through.

But that's solving the wrong problem.  The real issue is that
SNOBOL4 SM-lowering puts every named label in the cfn registry,
including internal labels that are NOT separate functions — they're
just intra-function jump targets that happen to be named.  The
proper fix is in SM lowering, not in the emitter:

**The proper redesign — three steps, in order:**

1. **In `sm_lower.c`, distinguish DEFINE'd functions from internal
   labels.**  Currently every named SM_LABEL gets `a[0].s` set, and
   `emit_expression_registry` puts every one of them in the cfn
   table.  Add a flag (e.g. `a[1].i = 1` for "this is a DEFINE'd
   entry, registry should include it"; default 0 for "this is a
   :S(label) target, registry should NOT include it").  The flag is
   set when the parser/lowerer emits the SM_LABEL associated with a
   `DEFINE('fn(args)')` call's body, and only there.

   Source of truth for which name is a DEFINE'd function: walk for
   `SM_CALL_FN s="DEFINE"` immediately followed by `SM_VOID_POP`
   then `SM_JUMP -> after_fn`; the SM_LABEL at `after_fn - 1` (i.e.
   the label whose pc is the JUMP target's predecessor's predecessor
   — actually, the SM_LABEL at `pc_of_JUMP + 1` *if* its name
   matches the DEFINE's first argument string).  Mark THAT SM_LABEL
   as DEFINE'd; leave all other named SM_LABELs as plain labels.

2. **Update `emit_expression_registry`** to filter on the new flag.
   Only DEFINE'd labels enter the registry.  Internal labels remain
   addressable via .L<pc> for intra-function jumps but never via
   cfn().

3. **Emit a real prologue at every DEFINE'd chunk entry, and a real
   epilogue at every return inside such a chunk:**

   ```
   .L<entry_pc>:
       push rbp                ; save caller's rbp + align rsp
       mov  rbp, rsp           ; establish frame
       <body>                  ; rsp%16==0 throughout
                               ; (PLT calls inside push 8 bytes, callee
                               ; sees %16==0 after its own prologue)
       <return point>:
       pop  rbp                ; restore caller's rbp
       ret                     ; pops cfn return address
   ```

   For RETURN_VARIANT (conditional), splice `pop rbp` between
   `jz .Lretskip_<pc>` and `ret` so it only runs on the
   taken-return path; the falsy path falls through with rbp still
   pointing at the chunk's frame, and the next return (if any)
   handles the unwinding.  This matches the structure of the
   thunk-approach inline emission already prototyped in the
   reverted code.

**Important: dual-entry case revisited under proper prologue.**

After step 1 above, `assign1` is no longer in the registry — it's
just a label inside the `assign` chunk.  cfn("assign1") returns
"undefined function".  This is correct SNOBOL4 semantics IF the
program never legitimately calls `assign1` as a function — and per
the SNOBOL4 reference, only DEFINE'd names are function calls; bare
labels are jump targets, not callables.  SPITBOL agrees (test:
calling `assign1(...)` in a SPITBOL program errors with
"function not defined").

The dual-entry concern (label reachable both via cfn AND
fall-through) dissolves once internal labels are removed from the
registry: there's only one cfn entry path per chunk, the explicit
DEFINE'd entry.  Fall-through within a chunk is just normal jump
flow with rbp already set up — `pop rbp; ret` at any return site
correctly unwinds the single frame.

**Files for the next session's implementation:**

- `src/runtime/x86/sm_lower.c` — add the DEFINE'd-flag emission.
- `src/ir/ir.h` — possibly extend SM_Instr.a to carry the flag (or
  reuse `a[1].i` for SM_LABEL; verify nothing else uses it).
- `src/runtime/x86/sm_interp.c` — the interpreter doesn't care
  about the flag (its registry behavior is fine), but any code that
  walks SM_LABEL and reads `a[0].s` should be audited.
- `src/runtime/x86/sm_codegen_x64_emit.c`:
  - `emit_expression_registry`: filter by the new flag.
  - `emit_sm_label`: emit `push rbp; mov rbp, rsp` for DEFINE'd
    chunk entries (predicate: pc is a DEFINE'd entry).
  - `emit_sm_return` / `emit_sm_return_variant`: emit
    `pop rbp` before `ret` for returns inside such chunks.
  - No thunk-emission pass.
  - No `g_pc_intra_chunk_label` bitset (intra labels not in
    registry, so don't need special treatment).
- All 5 tracked artifacts regenerate (they get prologues now
  instead of bare LABEL macros at function entries).

**Validation plan:**

After landing, the gate should reach PASS≥5 (matching the thunk PoC
since the alignment is principle-equivalent).  If higher, the
remaining failures are non-alignment-related divergences that
SN-33 owns.  If lower, there's a fall-through-into-prologue case
(some chunk reachable via fall-through from the previous chunk's
non-returning path) that needs separate treatment — likely a JUMP
emitted by sm_lower past the prologue when fall-through is
intended.

**Reverted code shape (recoverable from this commit's git log if
useful as starting infrastructure):**

- `g_pc_is_chunk_entry[]` / `g_pc_in_chunk_body[]` /
  `g_pc_intra_chunk_label[]` bitsets in `sm_codegen_x64_emit.c`,
  populated by `aligned_chunks_alloc_and_collect`.  Predicate for
  chunk-entry: named SM_LABEL preceded by SM_JUMP whose target's
  predecessor is a return variant.  Predicate distinguishes
  DEFINE'd functions from PASS/FAIL branch labels at the .s-emit
  level; the proper redesign moves this distinction up to
  sm_lower.c where it belongs.
- `emit_chunk_thunks` function emitting one
  `.Lthunk_<pc>: sub rsp,8 ; jmp .L<pc>` per registry entry,
  placed in `emit_file_footer` between main's `ret` and
  `.size main, .-main`.
- `emit_expression_registry` routing entries through `.Lthunk_<pc>`.
- `emit_sm_return` / `emit_sm_return_variant` emitting inline
  `add rsp, 8` before `ret` when pc is in a chunk body.

Useful primarily as a reference for the bitset boilerplate; the
actual fix uses `push rbp; mov rbp, rsp` / `pop rbp; ret` instead
of `sub rsp, 8` / `add rsp, 8`, and the predicate moves from the
emitter to the SM lowerer.

**Gates after revert (baseline restored):**

- `test_gate_em_beauty_subsystems_mode4.sh`: PASS=4 FAIL=13.
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.

one4all unchanged from `f78d366c`.

**Next session:**

Land Step 1 (`sm_lower.c` DEFINE'd-flag) as a standalone rung;
verify the registry shrinks to only DEFINE'd entries; then land
Steps 2 + 3 (registry filter + proper prologue emission) together.
PoC suggests PASS≥5 immediately, possibly higher.

----



**Diagnosis only — no code landed.**  One patch attempted (Option 1 from
the prior watermark, gated on `prog->instrs[pc-1].op == SM_JUMP`), broke
the gate (PASS=4 → PASS=2), and was reverted.  Repos clean at this hash
on entry and on exit.  This watermark exists so the next attempt does
not retrace and goes straight to the option that actually works.

**What was implemented (and reverted).**  In
`sm_codegen_x64_emit.c`:

1. New file-static bitset `g_pc_in_aligned_chunk[]` populated by
   walking `prog->instrs` once.  An SM_LABEL at pc `i` is an
   "aligned chunk entry" iff `ins->a[0].s != NULL && prog->instrs[i-1].op == SM_JUMP`.
   The chunk body extends from `i+1` through `(int)prev->a[0].i` (the
   JUMP's target pc) — covering intra-chunk SM_LABELs (e.g. JUMP_F
   branch landings inside a conditional return), since those genuinely
   contain returns that need `add rsp, 8` too.
2. `emit_sm_label`: emits `sub rsp, 8` after the LABEL macro line at
   chunk entries.
3. `emit_sm_return`: emits inline `add rsp, 8 ; ret` (bypassing the
   SM_RETURN macro) when `pc_is_in_aligned_chunk(pc)`.
4. `emit_sm_return_variant`: emits the entire conditional-return
   inline (`mov edi,kind ; mov esi,cond ; call rt_do_return@PLT ;
   test eax,eax ; jz .Lretskip_<pc> ; add rsp,8 ; ret ; .Lretskip_<pc>:`)
   when in an aligned chunk, splicing `add rsp, 8` between `jz` and
   `ret` so the alignment is undone only on the taken-return path.

The emitted `.s` shape is correct.  All 5 tracked artifacts assemble
clean.  But the gate regresses.

**Why it fails: the SM_JUMP predicate is necessary but not sufficient
when the chunk body contains intra-chunk named SM_LABELs.**

Concrete demonstration in `assign_driver.sno` (which previously passed,
now SIGSEGVs).  The SNOBOL4 source:

```snobol4
                          :(assign_end)              ; chunk-skip JUMP
assign      ...                                     ; pc 1778: SM_LABEL "assign", named, prev=SM_JUMP — IS chunk entry
            ...
            assign = ASGN_INDIR(EVAL(expression), name)  :(NRETURN)  ; pc 1798: SM_NRETURN
assign1     assign = ASGN_INDIR(expression, name)        :(NRETURN)  ; pc 1804: SM_NRETURN
                                                          ; pc 1799: SM_LABEL "assign1", named, prev=SM_NRETURN
assign_end                                                ; pc 1805: SM_LABEL "assign_end", named, prev=SM_NRETURN
```

The expression registry has THREE entries here: `assign → .L1779`,
`assign1 → .L1800`, `assign_end → .L1806`.  Per the predicate:

- `.L1779` (entry of `assign`): aligned chunk — gets `sub rsp, 8`. ✓
- `.L1800` (entry of `assign1`): NOT aligned — prev is SM_NRETURN, not
  SM_JUMP.  No `sub rsp, 8`.  But IS reachable via `cfn(assign1)`.
- `.L1806` (entry of `assign_end`): NOT aligned.

`.L1800` has DUAL ENTRY semantics:

1. **Path A — fall-through from inside `assign`'s body.**  Reached from
   `JUMP_F .L1799` at pc 1792 followed by fall-through past the
   `.Lretskip_1798:` (when `rt_do_return` returned 0 — though for
   unconditional NRETURN it always returns 1, so this path is
   theoretical for assign but real for FRETURN_S/NRETURN_F variants in
   other drivers).  rsp is whatever `assign`'s entry `sub rsp, 8`
   plus subsequent ops left it at — typically aligned.

2. **Path B — direct cfn() call to `assign1`.**  Reached from
   `cfn(NV[\"assign1\"]) → call_native_chunk → call *fn`.  `call`
   pushes 8-byte return address; rsp%16==8 entering body.  No `sub
   rsp, 8` because `prev != SM_JUMP`.  Body's PLT calls (e.g.
   `rt_call ASGN_INDIR`) issue with rsp%16==8.  Eventually one of
   them reaches `bb_label_initf → vsnprintf → movaps -0xc0(%rbp)`,
   which faults on misaligned rsp.  SIGSEGV.

Adding `sub rsp, 8` at `.L1800` would fix Path B but break Path A
(double-subtract, then the first NRETURN in the body's `add rsp, 8;
ret` would pop garbage from main's frame — same regression mechanism
as the prior watermark's failed Option 1 attempt).

**The dual-entry case is structural in SNOBOL4, not incidental.**  Any
function body containing a `:S(<intra_label>)` or `:F(<intra_label>)`
has the same shape: the intra-label is registered (SNOBOL4's namespace
puts every label in the registry) AND reachable from outside via
cfn() AND reachable from inside via fall-through.  Across the 17
beauty drivers, every failing driver has at least one such label
inside a function body; the 4 passing drivers (assign with my fix
masking the issue, fence, ShiftReduce, counter) either have only
single-entry chunks or never call the intra-labels from outside.

After my fix, `assign_driver` started failing because the cfn-entry
to `.L1800` (which the test exercises via some indirect call path
not yet traced — likely `EVAL`-driven dispatch or a pattern userfn
capture) now hits the dual-entry pathology.  Pre-fix, `assign_driver`
failed in Path A but the rsp%16==8 didn't reach a `movaps`-using
function before the chunk returned, so the bug was latent.

**What needs to land instead.**  Three options ranked by tractability:

1. *(Cleanest semantically — recommended next attempt)* **Per-chunk
   thunk shim.**  Replace registry entries pointing directly into chunk
   bodies with entries pointing at one-shot thunks.  Each thunk is a
   3-line proc emitted at the end of `.text`:

   ```
   .Lthunk_<entry_pc>:
       sub rsp, 8
       jmp .L<entry_pc>
   ```

   The expression registry stores `.Lthunk_<entry_pc>` instead of
   `.L<entry_pc>`.  cfn() lands at the thunk; thunk aligns rsp; jumps
   into the body.  Body executes with rsp%16==0 throughout.  Returns
   inside the body do `add rsp, 8; ret` — same as my Option-1 attempt,
   but now BOTH the thunk path AND the fall-through path enter the
   body at rsp%16==0 (the fall-through path enters via the previous
   chunk-entry's thunk-aligned state).  Single-entry-from-outside
   semantics restored at the asm level without changing SM lowering.

   Cost per chunk: 2 instructions of `.text` + 1 jump per cfn call.
   No effect on intra-program JUMP/JUMP_S/JUMP_F (those still target
   `.L<pc>` directly, bypassing the thunk).

   Predicate: emit a thunk for EVERY named SM_LABEL (every registry
   entry), not just `prev==SM_JUMP` ones.  Bitset for "in aligned
   chunk" expands to "in any function body" — set from any registered
   SM_LABEL forward to the next SM_RETURN* after which control flow
   leaves via a non-fall-through path.  Or simpler: set [pc, end-of-
   program] — too coarse but safe; unused returns at top-level get
   `add rsp, 8` they don't need but the asm is harmless because main()
   doesn't reach them (a HALT precedes).

2. **`push rbp; mov rbp, rsp` proper frame at every named SM_LABEL.**
   Distinguishes call-entry from fall-through-entry by checking rbp,
   which is set up only on call-entry.  Complex, requires runtime
   support (rbp inspection inside `rt_do_return`), and breaks the
   "chunk is just inline code, no frame" simplicity that EM-FORMAT
   work has been preserving.  Not recommended.

3. **Restructure SM lowering to never register intra-function labels.**
   `assign1`'s SM_LABEL would not get `a[0].s` set in the lowering
   from the parser.  Registry would have one entry per DEFINE'd
   function, period.  Clean semantically but invasive (touches
   `sm_lower.c` and possibly the IR), and may break SNOBOL4 idioms
   that genuinely call intra-function labels via `apply` or `$name`.
   Defer until after Option 1 lands and stabilizes.

**Validation hypothesis for Option 1 (per-chunk thunk).**  On
`assign_driver`, the thunk approach predicts:
- `cfn("assign")` enters via `.Lthunk_1779: sub rsp,8; jmp .L1779`.
  Body executes at rsp%16==0.  Both NRETURN sites hit `add rsp,8;
  ret` correctly.
- `cfn("assign1")` enters via `.Lthunk_1800: sub rsp,8; jmp .L1800`.
  Body (just the second NRETURN) executes at rsp%16==0.  Returns
  correctly.
- Fall-through from `.Lretskip_1798` to `.L1799 LABEL` to `.L1800`:
  rsp was aligned by `.Lthunk_1779` and remains aligned through the
  fall-through.  The NRETURN at pc 1804's `add rsp, 8; ret` pops the
  cfn return-address pushed by ITS thunk — but wait, it would pop the
  return-address pushed by .Lthunk_1779's thunk (the original cfn
  call), which IS what we want (the original cfn() expects to be
  returned to).  Check: does this break the `rt_do_return` semantics
  for NRETURN where the function may not actually return at this
  site?  Need to verify rt_do_return's expectation of stack shape.

**Files that need touching for Option 1 (when next session attempts):**
- `src/runtime/x86/sm_codegen_x64_emit.c` —
  `emit_expression_registry` to emit `.Lthunk_<pc>` instead of
  `.L<pc>` per entry (one-line change in the .quad emission); new
  `emit_chunk_thunks` pass after the dispatch loop to emit one
  3-line thunk per registry entry; `emit_sm_return` and
  `emit_sm_return_variant` get the inline `add rsp, 8` ahead of `ret`
  unconditionally for any pc in [first_named_label_pc, prog->count)
  range — i.e., once we're past the program's top-level main-body
  code, we're inside a function and every return needs the alignment
  undo.
- No changes to `sm_emit_template.c` (macros stay simple).
- No changes to `sm_macros.s` regeneration.
- No changes to `libscrip_rt.so`.
- All 5 tracked artifacts will need regeneration.

**Gates after revert (baseline restored):**
- `test_gate_em_beauty_subsystems_mode4.sh`: PASS=4 FAIL=13 (unchanged).
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.

**Next session:** implement Option 1 (per-chunk thunks).  The code
written and reverted this session in `sm_codegen_x64_emit.c` is a
useful starting point for the bitset infrastructure — recoverable
from `git log -p` of this commit if helpful — but the
`prev==SM_JUMP` predicate must be widened to "every named SM_LABEL"
and emission moved from inline `sub rsp, 8` at the body to a
separate thunk before the body.

one4all unchanged from `f78d366c`.

----



**Diagnosis only — no code landed.**  Three patches were attempted, broke
the gate (PASS=4 → PASS=1), and were reverted.  Repos clean at this hash
on entry.  This watermark exists so the next attempt does not retrace.

**Mechanism of the 13 mode-4 diffs (all 13 share one root cause).**  Every
failing driver SIGSEGVs identically: the emitted binary's `main()` is
ABI-correct (rsp%16==0 between calls thanks to `push rbp; mov rbp,rsp`),
but a user-function chunk emitted by `sm_codegen_x64_emit.c` has NO
prologue.  Its label (e.g. `.L1779`) is followed directly by SM ops — the
chunk inherits rsp%16==8 from `cfn()`'s `call` and never aligns it.
Every PLT call from the chunk's body therefore issues with rsp%16==8
(an ABI violation).  The misalignment propagates through `rt_match_variant
→ exec_stmt → bb_build_flat → flat_emit_body_v` until glibc's `vsnprintf`
(reached via `bb_label_initf("%s_α", ...)`) executes
`movaps -0xc0(%rbp)` — and that `movaps` requires 16-byte alignment.
The 16-byte instruction faults; SIGSEGV.

Frame walk on the SIGSEGV (gdb on `match_driver` linked against
`libscrip_rt.so`):
- `main`:               rbp%16 == 0  ✓
- `rt_match_variant`:   rbp%16 == 8  ✗ (caller misaligned)
- `exec_stmt`:          rbp%16 == 8  ✗
- `bb_build_flat`:      rbp%16 == 8  ✗
- `flat_emit_body_v`:   rbp%16 == 8  ✗
- `bb_label_initf`:     rbp%16 == 8  ✗
- crash in `__printf_buffer_init` at `movaps -0xc0(%rbp)`

Counting `rt_match_variant` invocations: the first 19 (called directly
from `main()`) all have rsp == 0x...e930 (well-aligned).  The 20th has
rsp == 0x...e2e8 — 0x648 bytes deeper, deep enough to be inside a
chunk frame.  That 20th call is the one that crashes.  Confirmed via
gdb conditional breakpoint with `bt`.

**Why `assign_driver` passes today.**  Its only chunk (the body of
`assign(name,expression)`) reaches `rt_call → call_native_chunk → cfn()`
but the chunk body never invokes anything via `rt_match_variant` /
`bb_build_flat` / `flat_emit_body_v`.  The misalignment is present but
glibc's movaps is never reached, so the ABI violation is silent.  This
will surface as soon as `assign`-style chunks call patterns that route
through `bb_label_initf` — i.e., the bug is latent for many drivers
besides the 13 currently failing.

**The naive fix that doesn't work.**  Sub `rsp, 8` after each named
SM_LABEL chunk entry, paired with `add rsp, 8` before `ret` in RETURN /
RETURN_VARIANT macros.  Result: PASS=4 → PASS=1 (regression).  Root
cause: not all named SM_LABELs are cfn-only entries.  SNOBOL4's
DEFINE-pattern compiles to:

```
... CALL_FN DEFINE              ; registers function
    JUMP after_function          ; skip body in linear flow
    LABEL                        ; (registered in expression registry)
.L1779: <chunk body>             ; reached via cfn() from rt_call
    RETURN_VARIANT
.L1799: LABEL                    ; (also registered, also a JUMP_F target)
.L1800: <body of THE NEXT chunk> ; reached BOTH via cfn() AND via fall-through from .L1799
    RETURN_VARIANT
after_function:
```

So `.L1800` has dual entry semantics: when reached via `cfn()`, the call
instruction pushed an 8-byte return address (sub-then-add balances);
when reached via fall-through after `JUMP_F .L1799`, no return address
was pushed (sub-then-add ends with `ret` popping garbage from main's
frame, jumping to a stack address).  Crash at `0x7fffffffe2e0 in ?? ()`
— the canonical signature of `ret` to a corrupted stack.

**What needs to land instead.**  Three options ranked by risk:

1. *(Most likely correct, requires careful validation)* Distinguish
   "named SM_LABEL that is the cfn entry" from "named SM_LABEL that is
   also a fall-through target".  The expression registry's entry_pc is
   `i + 1` where `i` is the SM_LABEL pc; only `.L{i+1}` actually receives
   `cfn()` calls, and that label is preceded by a `JUMP after_function`
   in linear flow.  Verify: for every registered chunk entry, the
   instruction at the previous pc is an unconditional JUMP whose target
   is past the chunk body.  If that invariant holds, emit `sub rsp, 8`
   only at chunk entries that are post-`JUMP` (i.e., not fall-through
   reachable).

2. Fix at the call site instead of the chunk site.  In `rt.c:call_native_chunk`,
   the `cfn()` call is a normal C function-pointer call; the C compiler
   already guarantees rsp%16==0 just before `call *<reg>`.  Wrap the
   call in inline asm that does `sub rsp, 8; call *cfn; add rsp, 8`,
   making the chunk's effective entry rsp%16==0 from the start.  The
   chunk's `ret` then pops the original return address one slot deeper
   — no chunk-side change needed.  But the chunk's `ret` would need to
   know to skip the extra 8 bytes; this option doesn't actually work
   without a chunk-side change.

3. *(Cleanest semantically)* Give every chunk a real x86 prologue
   (`push rbp; mov rbp, rsp`) and epilogue (`pop rbp; ret`).  Replace
   `RETURN`'s body with `pop rbp; ret`; replace `RETURN_VARIANT`'s
   taken-`ret` with `pop rbp; ret`.  This works correctly under both
   call-entry and fall-through-entry: in fall-through, no `push rbp`
   was executed, so `pop rbp; ret` pops main's `rbp` value plus
   garbage — STILL WRONG.  Need the prologue to also distinguish
   call-entry vs fall-through-entry.

Conclusion: the bug is real and ABI-rooted, but the fix requires
distinguishing dual-entry chunks from single-entry chunks — option 1
above.  The diagnosis is the deliverable of this session.

**Files touched, confirmed reverted to baseline:**
- `one4all/src/runtime/x86/sm_codegen_x64_emit.c` — three patches
  reverted (g_chunk_entry_pending static, emit_sm_label flag-set,
  dispatcher loop force-flush+sub).
- `one4all/src/runtime/x86/sm_emit_template.c` — two patches reverted
  (SM_TPL_RET add-before-ret, SM_TPL_RET_VAR add-before-ret).
- `corpus/programs/snobol4/demo/sm_macros.s` — checkout from HEAD
  (auto-regen would have re-introduced the patched macros).

**Gates after revert (baseline restored):**
- `test_gate_em_beauty_subsystems_mode4.sh`: PASS=4 FAIL=13 (matches
  prior baseline — Gen, Qize, ReadWrite, TDump, XDump, case, global,
  match, omega, semantic, stack, trace, tree drivers diff vs --sm-run).
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.

**Next session:** pick option 1 above.  Validate the JUMP-precedes-named-
SM_LABEL invariant on a corpus of inputs (beauty.sno, all 17 drivers,
roman/wordcount/claws5/treebank-* artifacts) before writing emit code.
If the invariant holds, the patch is the same one tried this session
but gated on `prev_instr.op == SM_JUMP`.

one4all unchanged from `7238e6e4`.

----

**SN-33b cap_t::fn + NRETURN deref — sess 2026-05-10 (later)**

Mode-4 was at 17/17 parity with `--sm-run`, but that parity was
*parity-with-broken*: both modes segfaulted identically on every beauty
subsystem driver because of an unrelated runtime regression in the
SM-interpreter pattern-capture path.  This session diagnosed and fixed
that regression in the runtime (NOT in the emitter), unblocking real
mode-4 measurement.

Two related fixes in `one4all`:

1. **`bb_flat.c:flat_is_eligible`** — exclude XNME/XFNME/XARBN per the
   function's own comment.  The eligibility check claimed (lines
   1508-1515) that captures and ARBNO should fall back to the runtime
   variant path "until that infrastructure lands" but only excluded XVAR
   and XCAT n>2.  Captures slipped into `flat_emit_node`'s binary path,
   which calls `bb_cap_new(NULL, NULL, vn, NULL, immediate)` at line
   1494 with no recursive child-blob emission, leaving `cap_t::fn` null.
   Fix: align body with comment; captures and ARBNO route through
   `bb_build_binary` (which does recursively build the child) instead.

2. **`sm_interp.c` SM_NRETURN + `sm_codegen.c` h_return_impl** —
   NAME_DEREF on return.  NRETURN was pushing
   `NAMEVAL(GC_strdup(retval_name))` — substituting the function's own
   name for the actual return descriptor.  `r = foo()` where foo
   `:(NRETURN)`s would store "foo" instead of the empty string SPITBOL
   produces.  IR-run gets it right via `interp_eval.c:2771`'s
   `if (IS_NAME(r)) return NAME_DEREF(r);` after `call_user_function`.
   Fix: push `retval` (already `NV_GET_fn(retname)` at line ~1338) and
   apply NAME_DEREF on the way out, matching IR convention.  Same fix
   applied symmetrically to JIT codegen handler.

**Gates:**
- `test_gate_sn7_beauty_self_host.sh` (SN-33's gate): **0/51 → 26/51**.
  `assign_driver` passes all three modes (--ir-run, --sm-run, --jit-run).
- `test_gate_em_beauty_subsystems_mode4.sh` (this Goal's parity gate):
  17/17 (parity-with-broken) → **4/17 (parity-with-real)**.  The drop
  is the design intent of the gate finally activating: mode-3 is now
  producing real output, so mode-4 either matches it or surfaces a
  divergence.  `assign_driver` mode-4 also passes.
- `test_smoke_snobol4.sh`: 7/7 (no regression).
- `test_smoke_unified_broker.sh`: 49/49 (no regression).

The 13 mode-4 diffs and 25 SN-7 fails are residual SN-33 work — distinct
real bugs in IR-only paths (e.g. `case_driver --ir-run` infinite recursion
in `_usercall_hook → call_user_function` when fn-name shadows parameter
name) and in SM-only paths (e.g. `counter_driver --sm-run`).  These were
*latent behind the segfaults*; SN-33b unblocked execution and exposed
them for individual treatment.

one4all @ `7238e6e4`.

Next: EM-7d-beauty-subsystems work continues — pick any one of the 13
remaining mode-4 diffs, isolate, fix.  Or hand back to SN-33 for further
mode-3 correctness work that will automatically lift mode-4 parity.

----

**EM-FORMAT-SUBLIME-SN-LABEL-FIX — sess 2026-05-10 (latest)**

`.S8`, `.S16` etc. were painted as directives (wrong colour) in the GAS-x86
Sublime highlighter. Fix: added `.S\d+` rule to `local-labels` context
(runs before `directives`); added `(?!S\d)` to the catch-all negative
lookahead as a defensive guard. Both get `entity.name.label.gas` (white).
corpus @ `ffe5887`.

Next: EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-BOX-ALIGN — sess 2026-05-10**

`# BOX KIND(args)` indented so `BOX` lands at col 24 (mnemonic column).
one4all @ `11d4388f`, corpus @ `b735676`.
Gates: smoke 7/7, mode-4 parity 17/17. Artifacts gcc -c clean.
Next: EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-DOUBLED-BANNER-FIX — sess 2026-05-10**

Removed four `emit_section_break()` calls that were emitting bare `#===` rules
immediately before sections already opening with their own `#===` stmt/blob banners,
producing doubled rules. Deleted the dead `emit_section_break` helper.
one4all @ `0796e673`, corpus @ `6d56405`.

Gates: smoke 7/7, mode-4 parity 17/17. Artifacts gcc -c clean.

**Next:** EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-COMMENT-PURGE — sess 2026-05-10**

Removed six categories of noisy comments from emitted `.s`:
`# data: ...` annotations, `# strings/expression registry/BB code/SM code` section captions,
`#-- epilogue ---` banner, `# pattern pat_inv_N: ...` blob caption (rule kept, text dropped).
one4all @ `9395019b`, corpus @ `8ca7c58`.

Gates: smoke 7/7, mode-4 parity 17/17. Artifacts gcc -c clean.

**Next:** EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-CHUNK-RENAME — sess 2026-05-10**

`chunk` → `expression` throughout `sm_codegen_x64_emit.c`:
`emit_chunk_registry` → `emit_expression_registry`;
`.Lchunk_registry` → `.Lexpression_registry` (emitted label + `lea` operand);
`has_chunk_registry` → `has_expression_registry`;
`chunk_reg_count` → `expression_reg_count`; comments updated.
one4all @ `b49a4b58`, corpus @ `123ed4d`.

Gates: smoke 7/7, mode-4 parity 17/17. Artifacts gcc -c clean.

**Next:** EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-LABEL-RENAME + EM-FORMAT-SECTION-BREAKS — sess 2026-05-10**

Two formatting micro-rungs landed together:

1. **EM-FORMAT-LABEL-RENAME** — `.Lstr_N` → `.SN` (string table labels in `.rodata`);
   `.LpcN` → `.LN` (PC labels / jump targets in `.text`).  Six sites across
   `sm_codegen_x64_emit.c` and `sm_emit_template.c`.  No semantic change —
   pure readability: shorter, GAS-idiomatic, less visual noise.

2. **EM-FORMAT-SECTION-BREAKS** — `emit_section_break()` helper (10 lines) added;
   four `#===` separator lines inserted between the five major sections of every
   emitted `.s` file: includes → **strings** → **expression registry** →
   **BB code** → **SM code**.  BB data stays inline inside each blob (unchanged).
   Makes the file's top-level structure immediately scannable.

Gates: smoke 7/7 PASS, mode-4 parity 17/17 PASS.
one4all @ `8fc4cd22`, corpus @ `6a3afc2`.

**Next:** EM-7d-beauty-subsystems (blocked on SN-33 `cap_t::fn` null fix).

----

**EM-FORMAT-SUBLIME-GAS-INTEL landed (all 5 sub-rungs a–e); white-vs-orange label-paint inconsistency eliminated — sess 2026-05-10 (Sublime session)**

Pure editor-support work: no emitter changes, no runtime changes, no
build-system changes.  Replaces the 1779-line Nasm-base + SCRIP-overlay
layer cake with a from-scratch GAS-Intel-syntax base + thin SCRIP
overlay.  Total: 661 lines across two files vs 1779 lines in one —
63% smaller, materially more correct on GAS semantics, and visually
uniform on label paint.

**Files landed (in `corpus/editor/sublime/`):**
- `GAS-x86.sublime-syntax` (NEW, 467 ll) — stand-alone GAS-Intel-syntax
  x86_64 highlighter authored from scratch.  Owns `source.asm.gas`.
  Activates on `[s, S, asm]`.  Comprehensive directive vocabulary
  (`section / symbol / attribute / data / alignment / macro /
  conditional / debug / mode / cfi / other`) with a `(?!L)` negative
  lookahead in the catch-all so `.L*` references defer to
  `local-labels`.  Comprehensive Intel-syntax mnemonic set
  (`move / stack / address / arith / branch / call / set / string /
  bit / fpu / simd / flag`).  Full register vocabulary by width
  (`qword / dword / word / byte / ip / flags / segment / xmm / ymm /
  zmm / mmx / cr / dr / mask`).  ELF decoration family
  (`@PLT @GOT @GOTPCREL @function @progbits @nobits @notype …`).
  Critical correctness wins: `;` is `punctuation.separator.statement.gas`
  (NOT a comment); `#` and `/* */` are comments;
  `.macro NAME args … .endm` is a structured `meta.macro.gas` block
  with `\arg` recognition; `.section .note.GNU-stack,"",@progbits`
  paints as one section name via dedicated `section-name-tail` push
  context.

- `SCRIP-x86.sublime-syntax` (REPLACED, 1779 → 194 ll) — thin overlay
  on the GAS base.  Uses `extends: Packages/User/GAS-x86.sublime-syntax`
  (Sublime Text 4 build 4080+) and `meta_prepend: true` to inject
  four SCRIP-specific contexts: `scrip-banners` (statement / pattern
  / box / data-annotation / rule banners), `scrip-jumpfuse` (triple-
  fusion shape recognition), `scrip-mnemonics` (SM opcodes, PAT
  opcodes, broker primitives, runtime calls), `scrip-port-labels`
  (Greek-suffix label refinement).  Activated by `first_line_match:
  '^\s*\.include\s+"(sm|bb)_macros\.s"'` so plain GAS files fall
  through to the base.  Owns `source.asm.scrip` (unchanged).

- `MIGRATION-GAS-SCRIP.md` (NEW) — visual A/B writeup.  Architectural
  diff table; "what the OLD version got wrong about GAS" enumeration;
  the white-vs-orange split explained; concrete claws5.s tokenization
  comparison (OLD vs NEW painting line by line); quantitative summary
  across all 5 tracked artifacts.

- `README.md` (UPDATED) — title now lists four products; Files table
  extended; new "GAS-x86 — base GAS Intel-syntax x86_64 highlighter"
  section; "SCRIP-x86" section rewritten as "thin overlay" with the
  per-overlay scope table and label-color-uniformity explainer;
  Authors section updated.

- `SCRIP-x86.LICENSE` (REMOVED) — was MIT attribution for upstream
  Nasm base.  No longer applies; new GAS base is from-scratch
  authorship.

**The white-vs-orange fix (the user-reported issue).**  Two label
families painted with two different scope vocabularies in the OLD
version: `.L*` labels (GAS local-symbol convention) painted as
`entity.name.constant.asm.x86_64` from the inherited Nasm rules,
producing white in most themes; user labels (`pat_inv_0_α`, `cap1_β`,
etc.) painted as `entity.name.label.box.scrip` from the SCRIP overlay,
producing orange in most themes.  Two label kinds, two paint families,
visually inconsistent.

The NEW version paints both under a single base scope,
`entity.name.label.gas`, by design.  The directive catch-all uses
negative lookahead `(?!L)` to refuse `.L*`-prefix tokens; `local-labels`
runs early in `statement-content` to claim them; `plain-labels` runs
last to claim everything else.  Greek-suffix port labels still get
the more-specific overlay scope `entity.name.label.box.scrip`, but
purely as an additive refinement — themes without an explicit override
see all labels at one consistent colour; themes with the override
get a distinct accent for pattern-box arms only.  The
`MIGRATION-GAS-SCRIP.md` quantitative summary confirms zero label-
named scopes outside the unified families across all 5 tracked
artifacts.

**Validation.**  Built a Sublime-syntax-engine simulator
(`/home/claude/work/gas_syntax_sim.py`, ~120 ll) that walks a
.sublime-syntax through `re.compile`/`pattern.match` honouring
push/pop/set, `meta_prepend`, anonymous push contexts, and zero-
width anchor rules.  Tokenized all 5 tracked `.s` artifacts plus
`sm_macros.s` and `bb_macros.s` under both the base alone and the
merged base+overlay; every directive paints as a directive, every
mnemonic paints as a mnemonic, every register paints by correct
width, every ELF decoration paints, every label paints under the
unified scope family, the triple-fusion shape `; je LBL ; jmp LBL`
fires correctly, the `.section .note.GNU-stack,"",@progbits`
edge case paints as one section name + ELF decoration.

**Gates:** all pre-existing tests untouched (no emitter, runtime, or
build changes).  Editor-support change only.  Tracked-artifact line
counts unchanged from prior watermark (151, 124, 949, 1176, 1355).

**Next.** EM-7d-beauty-subsystems remains the next functional rung,
blocked on SN-33 fixing `cap_t::fn` null in `bb_boxes.c:541`.

----

**EM-FORMAT-BANNER-COLLAPSE-SPACE landed; EM-7d-beauty-subsystems carved + baseline established — sess 2026-05-10 (later)**

Two small landings plus one new rung carved with a parity-baseline gate.

**(1) EM-FORMAT-BANNER-COLLAPSE-SPACE — landed.**  Banner shape collapsed
`# ====...` → `#====...` and `# ----...` → `#----...` (drop the space
between `#` and the rule character; add one more `=`/`-` to keep total
width at 120 columns).  Three sites in two files: `flat_emit_banner_rule`
in `bb_flat.c` (BB-side major + minor); `emit_major_break` and
`emit_minor_break` in `sm_codegen_x64_emit.c` (SM-side stmt banners);
plus the `#-- epilogue` mini-banner.  Doc comments adjacent to each site
updated to match.  No effect on the `# === BEGIN ... ===` macro-library
markers — those have inline text and aren't rule banners.

**(2) EM-FORMAT-BB-TRAMPOLINE-ELIM — removed from plan (not landed; the
rung itself was withdrawn).**  Open bullet in Steps section deleted;
"carved follow-on rungs" prose at end of prior watermark amended to
"none new this session"; PLAN.md goal-table cell amended to drop the
"or EM-FORMAT-BB-TRAMPOLINE-ELIM" alternative.  EM-7d is now the sole
next functional rung.

**(3) EM-7d-beauty-subsystems — new rung carved with baseline.**  New
rung sits between the closed `EM-FORMAT-BB-DATA-CONSOLIDATE` and the
still-open `EM-7d`, as a precondition to EM-7d.  Exercises mode-4
parity with `--sm-run` across the 17 `*_driver.sno` programs in
`corpus/programs/snobol4/beauty/`.  Each driver is a small
self-contained subsystem test (assign, case, fence, match, omega,
semantic, stack, trace, tree, counter, global, Gen, Qize, ReadWrite,
ShiftReduce, TDump, XDump) with its own pre-baked `.ref`.  Pass
criterion is mode-4-vs-mode-3 byte-identical, NOT `.ref`-correct: the
absolute-correctness gate is `test_gate_sn7_beauty_self_host.sh` and
lives under GOAL-LANG-SNOBOL4 rung SN-33.  Rationale: 17 small programs
surface category-specific divergences one subsystem at a time —
strictly easier to diagnose than chasing them simultaneously inside
the 646-line beauty.sno.

New gate: `scripts/test_gate_em_beauty_subsystems_mode4.sh`
(self-contained per RULES.md; paths derived from $0; uses `bash -c`
to suppress parent-shell SIGSEGV trap message).  For each driver:
emit (`--jit-emit --x64`), assemble + link against `libscrip_rt.so`,
run, then `diff` against the same driver's `--sm-run` output.

**Baseline:** `PASS=17 FAIL=0  (emit=0 link=0 diff=0)`.  Mode-4 already
achieves byte-identical parity with mode-3 on all 17 drivers — but
both segfault identically due to an unrelated runtime regression
tracked under SN-33.  Once mode-3 starts producing real output, this
gate is where mode-4 either keeps pace or surfaces a real divergence.

**Diagnosis of the segfault (handed off to SN-33):** SIGSEGV at
`bb_cap` in `src/runtime/x86/bb_boxes.c:541`, on the line
`cr = spec_from_descr(ζ->fn(ζ->state, α));`.  The `cap_t::fn` field
is null at the call site — pattern-capture-box function pointer is
not being populated during box construction.  Stack:
```
bb_cap (bb_boxes.c:541)
  bb_broker (bb_broker.c:44, mode=BB_SCAN, body_fn=scan_body_fn_u9)
    exec_stmt (stmt_exec.c:1395, subj_name="ALPHABET")
      sm_interp_run (sm_interp.c:732)
        sm_run_with_recovery (scrip_sm.c:159)
          main (scrip.c:538)
```
First failing statement uses subject `ALPHABET`, which is defined in
`global.sno` (one of beauty/'s shared includes).  The bug is upstream
of the emitter — it affects modes 1, 2, 3, and (parity-correctly)
mode 4.  Fix belongs to the runtime / pattern-builder, not mode-4.
Recommended next session: open SN-33, find the cap_t producer that
isn't populating `fn`, fix there.  When mode-3 starts producing
output, EM-7d-beauty-subsystems will start measuring real divergence
(or, if mode-4 tracks correctly, advance unprompted).

**Gates:** mode-4 smoke 13/13 GREEN; mode-4 beauty parity 17/17 GREEN;
snobol4 smoke 7/7 GREEN; unified_broker 49/49 GREEN; 5/5 tracked
artifacts (`roman.s`, `wordcount.s`, `claws5.s`, `treebank-list.s`,
`treebank-array.s`) `gcc -c` clean.  Tracked artifact line counts
unchanged from prior watermark (151, 124, 949, 1176, 1355).

**Files touched:**
- `one4all/src/runtime/x86/bb_flat.c` — banner rule shape
  (`flat_emit_banner_rule`) plus two adjacent doc-comment shapes.
- `one4all/src/runtime/x86/sm_codegen_x64_emit.c` — `emit_major_break`,
  `emit_minor_break`, epilogue mini-banner; one doc-comment shape.
- `one4all/scripts/test_gate_em_beauty_subsystems_mode4.sh` — new
  parity gate (84 lines).
- `corpus/programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array}.s`
  — regenerated with collapsed-banner shape.
- `.github/GOAL-MODE4-EMIT.md` — this watermark; trampoline-elim bullet
  removed; EM-7d-beauty-subsystems rung added before EM-7d.
- `.github/PLAN.md` — goal-table cell updated to point at new rung.

**Carved follow-on rungs:** none new beyond EM-7d-beauty-subsystems
(which IS the carve from this session).

----

> Prior watermarks (EM-FORMAT-BB-DATA-CONSOLIDATE,
> EM-FORMAT-BB-LAW + EM-FORMAT-BB-LAW-TRIPLE-FUSION,
> EM-FORMAT-BB-LAW 3rd-attempt, EM-FORMAT-BB-LAW-still-open,
> EM-FORMAT-BB-FUSED-GOTOS, EM-FORMAT-BB-PORT-COMPLETION,
> EM-FORMAT-BB-BOX-BANNERS, EM-FORMAT-BB-LONE-LABELS, EM-COMBINED-QUADS,
> EM-ONE-LINE-STRINGS+NO-INTERNAL-COMMENTS, EM-FORMAT-SM-BANNER-FIDELITY,
> EM-FORMAT-SM, EM-7c-sm-three-column-verify, EM-7c-no-trailing-ws,
> EM-7c-s-file-beautify, EM-7c-stmt-banner-fidelity,
> EM-7c-three-column-non-bb, EM-7c-bb-macros, EM-FORMAT-SM partial)
> are recoverable via `git log -p .github/GOAL-MODE4-EMIT.md` —
> compaction sess 2026-05-10.
