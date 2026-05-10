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

- [ ] **EM-7d-beauty-subsystems** — Mode-4 parity with `--sm-run` across all 17 `*_driver.sno` programs in `corpus/programs/snobol4/beauty/`.  Each driver exercises one subsystem (assign, case, fence, match, omega, semantic, stack, trace, tree, counter, global, Gen, Qize, ReadWrite, ShiftReduce, TDump, XDump) with its own `.ref` oracle.  Gate: `bash scripts/test_gate_em_beauty_subsystems_mode4.sh` — for each driver, emit (`--jit-emit --x64`), assemble, link against `libscrip_rt.so`, run, then `diff` against the same driver's `--sm-run` output.  Pass criterion is mode-4-vs-mode-3 byte-identical, *not* `.ref`-correct: the absolute-correctness gate (drivers vs `.ref`) is `test_gate_sn7_beauty_self_host.sh` and lives under GOAL-LANG-SNOBOL4 rung SN-33.  Mode-4 cannot be more correct than mode-3; what this rung enforces is that the emitter pipeline reproduces SM-interpreter behaviour exactly.  Rationale: 17 small, self-contained subsystem programs surface category-specific divergences (pattern matching, FENCE, capture, indirection, function calls, tracing) one subsystem at a time — strictly easier to diagnose than chasing them simultaneously inside the 646-line beauty.sno.  This rung is a precondition to EM-7d; EM-7d cannot pass while subsystems diverge, and any subsystem mode-3 fix automatically lifts mode-4 here.  **Baseline sess 2026-05-10 post-SN-33b:** PASS=4 FAIL=13 (emit=0 link=0 diff=13).  Up from PASS=17 FAIL=0 with the prior baseline being parity-with-broken (both modes segfaulting identically); SN-33b restored mode-3 to producing real output, so the parity gate now compares mode-4 against working mode-3, surfacing real divergences as designed.  `assign_driver` passes mode-4 (and modes 1/2/3) cleanly.

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

**EM-7d-beauty-subsystems Option-1-attempt-2 — dual-entry semantics ruled out simple `prev==SM_JUMP` predicate — sess 2026-05-10 (Claude later)**

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
