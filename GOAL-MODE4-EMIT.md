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

- [ ] **EM-FORMAT-BB-TRAMPOLINE-ELIM** (peephole optimizer; not a layout rung) — Eliminate trampoline jumps where `X: jmp Y`; rewrite `jmp X` callers to `jmp Y`.  Current artifacts have e.g. `xcat0_right_ω: jmp xcat0_left_β`.  Do NOT pick up before EM-FORMAT-BB-LAW + EM-FORMAT-BB-DATA-CONSOLIDATE land.  Care: only safe when `X:` is a pure trampoline (no other code flows through).

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

**EM-FORMAT-BB-LAW signed off + EM-FORMAT-BB-DATA-CONSOLIDATE landed — sess 2026-05-10**

EM-FORMAT-BB-LAW closed by Lon's sign-off ("layout of the S files is looking
okay now ... fairly nice and readable").  Triple-fusion shape from prior
session retained as final.

EM-FORMAT-BB-DATA-CONSOLIDATE: per-blob deferred-data buffer added to
`bb_flat.c`.  Every `flat_data_section` / `flat_text_section` pair inside a
`pat_inv_<id>` blob now buffers data emissions into `g_flat_data_buf`
instead of emitting inline; one consolidated `.section .data` block lands
at the end of each blob's body via `flat_emit_body_v`.  The original
emission sites carry an inline `# data: <labels>` comment so the reader
still ties each box to its locals.

**Implementation (`src/runtime/x86/bb_flat.c` only):**

- File-static state: `g_flat_data_buf[32K]`, `g_flat_data_active`,
  `g_flat_data_any`, `g_flat_data_just_closed`,
  `g_flat_data_pending_lbl[160]`, `g_flat_data_block_lbls[32][96]`.
- `data_buf_three_col(lbl, act, got)` mirrors `bb3c_format`'s
  `%-24s%-16s %s` shape but writes to memory; consumes any in-buffer
  pending label as the fused col-1.
- `data_buf_pend_label(name)` defers a label to fuse with the next data
  directive (`.string`, `.quad`, `.long`, `.zero`).  `flat3c_label`'s
  data-active branch routes here instead of emitting immediately — so
  `.Lcap1_data:` and `.quad 0` land on one line, just like before.
- `flat_data_section` flips active=1; `flat_text_section` emits the
  `# data: name1, name2` comment to the main stream and flips active=0
  (and sets `just_closed` so the trailing `.intel_syntax noprefix` from
  the box's section-restore pair is suppressed — `.intel_syntax`
  persists across `.section` switches in GAS).
- `flat_intel_syntax` no-ops while active or just_closed.
- All 6 data helpers (`flat_data_string`, `flat_data_quad`,
  `flat_data_quad_int`, `flat_data_long`, `flat_data_zero`,
  `flat3c_label`) gate on `g_flat_data_active` to choose between
  `data_buf_three_col` (buffered) and `flat3c` (passthrough).
- Consolidated flush at end of `flat_emit_body_v` (TEXT-externalised
  mode only): if buffer non-empty, emit one `.section .data`, dump the
  buffer (already three-column shaped), emit `.section .text`, reset
  state.  `bb3c_flush_pending` called first to defend against
  EM-FORMAT-BB-LONE-LABELS regression.

**Tracked artifact line counts:**

| File             | Lines | Was (LAW) | Δ |
|------------------|------:|----------:|---:|
| roman.s          |   151 | 153 | -2 |
| wordcount.s      |   124 | 124 |  0 |
| claws5.s         |   949 | 951 | -2 |
| treebank-list.s  |  1176 | 1178 | -2 |
| treebank-array.s |  1355 | 1357 | -2 |
| sm_macros.s      |   248 | 248 |  0 |
| bb_macros.s      |    44 |  44 |  0 |
| **TOTAL**        |  4047 | 4055 | **-8** |

Each banner-bearing file lost 2 lines net: 4-5 inline section ping-pongs
collapsed to 1 trailing block (saving ~8-10 lines) minus the 2-3 inline
`# data: ...` readability comments.  `wordcount.s` has zero patterns
hence no changes.

**Sample (roman.s) — before vs after, BOX CAP_COND site:**

```
BEFORE                                                  AFTER
xcat0_γ:                .section         .data          # data: .Lcap1_vname, .Lcap1_data
.Lcap1_vname:           .string          ""             xcat0_γ:                .globl           cap1_child_α
.Lcap1_data:            .quad            0              cap1_child_α:           lea              r10, [rip + Δ]
                        .quad            0              ...
                        .long            0
                        ...
                        .section         .text
                        .intel_syntax    noprefix
                        .globl           cap1_child_α
cap1_child_α:           lea              r10, [rip + Δ]
```

End-of-blob now has ONE consolidated data block:

```
pat_inv_0_ω:            mov              eax, 99
                        xor              edx, edx
                        ret
                        .section         .data
.Lcap1_vname:           .string          ""
.Lcap1_data:            .quad            0
                        .quad            0
                        ...
.Llen2_z:               .long            0
                        .section         .text
```

**Section-directive count per artifact:**
| File | `.section .data` (was) | now |
|------|----:|----:|
| roman.s          | 2 | 1 |
| claws5.s         | 4 | 1 |
| treebank-list.s  | 4 | 1 |
| treebank-array.s | 4 | 1 |
| wordcount.s      | 0 | 0 |

**Gates 14/14 GREEN:** smoke ×6 (snobol4 2/2 via all_modes, icon 5/5,
prolog 5/5, raku 5/5, snocone via all_modes 5/5, rebus 4/4), all_modes
2/2, EM PASS=13 (incl. EM-7c-audit on 6 tracked artifacts),
bb_flat_text PASS=18, sm_phase2_sim PASS=25.  Audit 0 violations
across 6 tracked artifacts.

**Files touched (one4all):**
- `src/runtime/x86/bb_flat.c` — +~180 lines for buffer state + helpers
  + consolidated flush; rewrote 9 helper functions (the 6 data emitters
  plus `flat3c_label`, `flat_data_section`, `flat_text_section`,
  `flat_intel_syntax`); wired reset + flush into `flat_emit_body_v`.

**Carved follow-on rungs (none new this session):** EM-FORMAT-BB-TRAMPOLINE-ELIM
remains the next layout-style rung, scoped as a peephole optimizer pass
after EM-7d.

----

> Prior watermarks (EM-FORMAT-BB-LAW-TRIPLE-FUSION,
> EM-FORMAT-BB-LAW 3rd-attempt, EM-FORMAT-BB-LAW-still-open,
> EM-FORMAT-BB-FUSED-GOTOS, EM-FORMAT-BB-PORT-COMPLETION,
> EM-FORMAT-BB-BOX-BANNERS, EM-FORMAT-BB-LONE-LABELS, EM-COMBINED-QUADS,
> EM-ONE-LINE-STRINGS+NO-INTERNAL-COMMENTS, EM-FORMAT-SM-BANNER-FIDELITY,
> EM-FORMAT-SM, EM-7c-sm-three-column-verify, EM-7c-no-trailing-ws,
> EM-7c-s-file-beautify, EM-7c-stmt-banner-fidelity,
> EM-7c-three-column-non-bb, EM-7c-bb-macros, EM-FORMAT-SM partial)
> are recoverable via `git log -p .github/GOAL-MODE4-EMIT.md` —
> compaction sess 2026-05-10.
