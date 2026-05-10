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

- [ ] **EM-7d-beauty-subsystems** — Mode-4 parity with `--sm-run` across all 17 `*_driver.sno` programs in `corpus/programs/snobol4/beauty/`.  Each driver exercises one subsystem (assign, case, fence, match, omega, semantic, stack, trace, tree, counter, global, Gen, Qize, ReadWrite, ShiftReduce, TDump, XDump) with its own `.ref` oracle.  Gate: `bash scripts/test_gate_em_beauty_subsystems_mode4.sh` — for each driver, emit (`--jit-emit --x64`), assemble, link against `libscrip_rt.so`, run, then `diff` against the same driver's `--sm-run` output.  Pass criterion is mode-4-vs-mode-3 byte-identical, *not* `.ref`-correct: the absolute-correctness gate (drivers vs `.ref`) is `test_gate_sn7_beauty_self_host.sh` and lives under GOAL-LANG-SNOBOL4 rung SN-33.  Mode-4 cannot be more correct than mode-3; what this rung enforces is that the emitter pipeline reproduces SM-interpreter behaviour exactly.  Rationale: 17 small, self-contained subsystem programs surface category-specific divergences (pattern matching, FENCE, capture, indirection, function calls, tracing) one subsystem at a time — strictly easier to diagnose than chasing them simultaneously inside the 646-line beauty.sno.  This rung is a precondition to EM-7d; EM-7d cannot pass while subsystems diverge, and any subsystem mode-3 fix automatically lifts mode-4 here.  **Baseline sess 2026-05-10:** PASS=17 FAIL=0 (emit=0 link=0 diff=0) — every driver currently segfaults identically under mode-3 and mode-4 due to an unrelated runtime regression tracked under SN-33 (root cause diagnosed: `cap_t::fn` null at `bb_boxes.c:541` in `bb_cap`); once mode-3 starts producing output, mode-4 must continue to match it byte-for-byte.

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

**EM-FORMAT-COMMENT-PURGE — sess 2026-05-10 (latest)**

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
