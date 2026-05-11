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
- Every call inside the template function goes through the `emitter_t` vtable.
- The vtable routes to the correct backend: `emitter_binary` (native x86 bytes), `emitter_text` (GAS `.s` lines), or `emitter_macro_def` (`.macro` definitions for `sm_macros.s` regen).
- **No other output path exists or is permitted.** `sm_emit_nullary`, `sm_emit_lbl`, `FILE*`-based static wrappers — all dead. The template function is the sole source of truth.
- Inline comments in col 3 carry only info NOT visible in col 2 (variable names, string values, disambiguators). The template function is responsible for emitting these via the vtable.
- `is_text` guards, callbacks into `bb_flat.c`, raw instruction emission in template bodies — all violations of this law. `EM-TEMPLATE-PURITY` exists to eradicate them.

**Consequence for sub-rung -n and all subsequent rungs:** the `FILE*`-based static wrapper pattern (e.g. `emit_sm_concat_insn` calling `emitter_text_new` then the template) is wrong. Mode 3 and mode 4 both call the template function directly with an appropriate emitter. The template function is the call site, not a wrapper around it.

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
- [ ] **EM-MODE4-IS-MODE3-DUMP** — One template per SM opcode/BB box; three backends (binary/text/macro_def). ⛔ Read `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` first — it is the design. Gates: smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4, 5 artifacts gcc-c clean.

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
  - [ ] **-n SM: CONCAT/COERCE_NUM/PUSH_NULL and similar nullary RT-call ops** ← **NEXT**. Pattern identical to sm_void_pop.

- [ ] **EM-TEMPLATE-PURITY** — Remove all `is_text` guards and callback parameters from every BB template. Make every template a pure sequence of vtable calls with no branching.

  **The invariant:** a template function calls emitter methods only. No `if (e->is_text)`. No callback parameter. No `void *arg`. The vtable routes each call to the right backend.

  **The correct shape — one macro invocation per port.**

  Looking at the byrd-reference `.s` files, a POS box emits:
  ```
  seq_l0_α:   RPOS_α  1, cursor, subject_len_val, seq_r0_α, P_3_ω  ; RPOS(%ld)
  seq_l0_β:   RPOS_β  cursor, P_3_ω
  ```
  One macro call per port. The macro body in `bb_macros.s` contains the actual `cmp`/`jmp` instructions. The template does NOT emit raw instructions — it emits one macro invocation per port via the vtable. The binary backend emits the corresponding bytes directly. The text backend emits the macro invocation line. Same vtable call; different backend rendering.

  **What went wrong in sub-rungs -d through -m:** templates emitted raw instructions (`emit_load_delta`, `emit_cmp_eax_imm32`, `EMIT_JMP`) for the binary path, and delegated text emission to callbacks into `bb_flat.c`. This inverted the design. The template should emit ONE port-call per port (`e->bb_port_alpha(...)`, `e->bb_port_beta(...)`), and each backend decides what that means — bytes or macro text.

  **The vtable surface for BB templates:**

  Each box port becomes one call on the emitter: `e->bb_α(e, kind, args, lbl_succ, lbl_fail)`, `e->bb_β(e, kind, args, lbl_fail)`. The text backend formats these as `KIND_α args, lbl_succ, lbl_fail` in three-column GAS. The binary backend emits the port's byte sequence. The `EMIT_OPT` macro (null-safe vtable call) is the call site.

  **Steps to fix:**

  - [ ] **EM-TEMPLATE-PURITY-1 — Audit.** For each BB template with `is_text`/callback, record: what macro name does the text path emit per port, what bytes does the binary path emit per port. This is the spec for the vtable slots needed.

  - [ ] **EM-TEMPLATE-PURITY-2 — Add port-call slots to `emitter_t`.** `bb_port_alpha(e, kind, args, lbl_succ, lbl_fail)` and `bb_port_beta(e, kind, args, lbl_fail)`. Text backend emits `KIND_α args, lbl_succ, lbl_fail`. Binary backend emits the port's byte sequence. Both implemented fully — no NULL slots.

  - [ ] **EM-TEMPLATE-PURITY-3 — Rewrite each BB template.** One `bb_port_alpha` call, one `bb_port_beta` call, banner comment, done. No `is_text`, no callbacks, no raw instruction emission in the template body.

  - [ ] **EM-TEMPLATE-PURITY-4 — Delete dead infrastructure.** All `bb_*_text_fn` typedefs from `bb_flat.h`. All `*_text_body` callbacks from `bb_flat.c`. All callback parameters from template signatures.

  - [ ] **EM-TEMPLATE-PURITY-5 — Verify.** `grep -r 'is_text\|text_body_fn\|text_body_arg' src/runtime/x86/templates/` returns empty. Gates green. Artifacts byte-identical.
  - [ ] -m BB: XFARB+XEPS+XFAIL (one rung).
  - [ ] -n..p Further SM/BB alternation (SM_LABEL/SM_STNO, SM_CALL_FN, SM_RETURN family, remaining BB boxes, SM_PAT_*).
  - [ ] -q SM_LABEL / SM_STNO structural markers.
  - [ ] -r SM_CALL_FN (big; uses lea_rip_sym, expression-registry).
  - [ ] -s SM_RETURN / SM_NRETURN / SM_FRETURN family incl. conditional variants. ABI alignment fixed here for both mode-3 and mode-4.
  - [ ] -t Remaining BB boxes: XFNCE, XDSAR, XATP, XCALLCAP, XCAT, XOR, XSTAR, XFARB, XPOSI, XRPSI, XNME, XFNME, XARBN, XFAIL.
  - [ ] -u Pattern SM opcodes (SM_PAT_*).
  - [ ] -v `sm_macros.s` + `bb_macros.s` become generated artifacts.
  - [ ] -w Rung close: beauty-subsystems gate improves from PASS=4 baseline; delete legacy emitter files.

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

**SESSION HANDOFF — sess 2026-05-11 (Claude Opus 4.7, fourth instance)**

**one4all `39e25002` on remote.** Three commits this session, on top of upstream `4b2a8700` (ICON-BB rung06) and `14d6fabf` (SI-6 PARTIAL emergency):
- `8d07b386` — three-way helper infrastructure + sm_halt ported
- `f4b14e8d` — sm_push_lit_i ported (+ t_mov_rdi_imm64, t_call_sym_plt, t_macro_begin/end helpers)
- `39e25002` — sm_void_pop ported (no new helpers needed)

### The architectural shift this session implements

Lon's specification (clarified through several rounds of Q&A this session):
**SM C templates are plain C functions that call free-standing helpers.
Each helper consults `bb_emit_mode` internally and does one of three
things — write x86 bytes (BINARY), write a GAS text line (TEXT), write a
`.macro`-body line (MACRO_DEF) — one of which may be "do nothing".  No
`emitter_t` is consulted from inside a template body or from inside a
helper.  No vtable.  No `EMIT_OPT`.  No `e->method(e, ...)` indirection.**

The shift supersedes every prior framing of EM-TEMPLATE-PURITY that tried to extend or patch the `emitter_t` vtable.  The vtable was a wrong turn; the correct shape is plain C functions with the three-way decision at the leaf.  `emitter_t` and its backends stay alive temporarily because untouched templates still reference them; once all templates are ported the struct and `emitter_text.c`/`emitter_binary.c`/`emitter_macro_def.c` delete.

### What landed (additive — no callers outside templates changed)

In `src/runtime/x86/bb_emit.h` and `bb_emit.c`:

| Helper | What it does (3-way switch on `bb_emit_mode`) |
|--------|-----------------------------------------------|
| `emit_mode_set(mode, out)` | central setter; called once per emit pass |
| `t_comment(text)` | TEXT/MACRO_DEF: `    # text` line; BINARY: no-op |
| `t_bb_box_banner(kind, args)` | TEXT/MACRO_DEF: 120-char `#---` rule + caption; BINARY: no-op |
| `t_inc_mem_r13_disp8(disp)` | BINARY: `41 ff 45 <disp>`; TEXT/MACRO_DEF: `inc dword ptr [r13+disp]` |
| `t_ret()` | BINARY: `c3`; TEXT/MACRO_DEF: `ret` |
| `t_pad_to_blob_size()` | no-op all 3 (hook for future) |
| `t_mov_rdi_imm64(val)` | BINARY: `48 BF <8>` (10 bytes); TEXT/MACRO_DEF: `mov rdi, 0x<val>` |
| `t_call_sym_plt(sym, fn_fallback)` | BINARY: `mov rax,fn; call rax` (12 bytes); TEXT/MACRO_DEF: `call sym@PLT` |
| `t_macro_begin(name, params[], n)` | TEXT: invocation line; MACRO_DEF: `.macro NAME params`; BINARY: no-op |
| `t_macro_end()` | MACRO_DEF: `.endm`; TEXT/BINARY: no-op |

Also: `bb_emit_byte()` abort tightened from "TEXT-only" to "non-BINARY-only" — now catches MACRO_DEF leaks too.

Also: `bb_emit_mode_t` enum extended from 2-value (TEXT/BINARY) to 3-value (TEXT/BINARY/MACRO_DEF).

The `t_` prefix exists only to avoid name collision with the existing `emit_X(emitter_t *e, ...)` inlines in `emitter.h` during the transition.  When the vtable deletes, the `t_` prefix can be dropped in a rename pass.

### SM templates ported (signature unchanged; body uses only t_* helpers)

| Template | Helpers used | Status |
|----------|--------------|--------|
| `sm_halt.c` | t_comment, t_inc_mem_r13_disp8, t_ret, t_pad_to_blob_size | ✅ ported, byte-identical |
| `sm_push_lit_i.c` | t_comment, t_macro_begin, t_mov_rdi_imm64, t_call_sym_plt, t_macro_end, t_pad_to_blob_size | ✅ ported |
| `sm_void_pop.c` | t_comment, t_macro_begin, t_call_sym_plt, t_macro_end, t_pad_to_blob_size | ✅ ported |
| `sm_jump.c` (JUMP/JUMP_S/JUMP_F) | needs `t_emit_jmp`, `t_test_rax_rax` | 🔲 next |
| `sm_arith.c` (ADD/SUB/MUL/DIV/MOD) | reuses `t_mov_rdi_imm64`, `t_call_sym_plt` (no new helpers) | 🔲 after sm_jump |

### How callers wire up (unchanged)

The three places that drive SM templates:
- `sm_codegen.c:emit_halt_blob_via_template` — calls `emitter_binary_new(buf, size)` which sets `bb_emit_mode = EMIT_BINARY` and `bb_emit_buf/pos/size`.  Then calls `emit_sm_halt(e)`.  The body ignores `e` but the mode and bb_emit globals it set are exactly what `t_*` helpers consult.
- `sm_codegen_x64_emit.c:775` — mode-4 text-emit driver.  Same shape: text-emitter construction sets `bb_emit_mode = EMIT_TEXT` and `bb_emit_out = FILE*`.
- Two demos (`test_template_byte_identity.c`, `demo_template_productions.c`) — gated, unchanged.

### Gates at handoff

- `test_smoke_snobol4.sh` — **PASS=6 FAIL=1** (`define` fails — upstream SI-6 regression)
- `test_smoke_unified_broker.sh` — **PASS=45 FAIL=4** (same upstream cause)
- `test_gate_em_template_byte_identity.sh` — **PASS=4 FAIL=0** ← this is *my* gate

**The smoke 6/7 and broker 45/49 regressions are upstream `14d6fabf` (SI-6 PARTIAL emergency).  Verified by checking out `14d6fabf` alone and running the gates — same failures.  No contribution from my work.**

### Pre-existing issues observed but not addressed (not in scope)

- **Mode-4 `.s` files crash scrip when re-run** at every commit checked back to `57d272e0`.  Unrelated to template-shape work.  Likely a `--jit-emit --x64` driver issue, not a template issue.
- **`sm_macros.s` uses `movabs rdi, \val`** which GAS rejects when val is a small immediate (movabs requires a 64-bit immediate operand).  Pre-existing.
- **`text_macro_begin` sets `g_text_macro_suppress` but nothing reads it** — so TEXT mode emits BOTH the invocation line AND the body, when the design says one OR the other.  `t_macro_begin` preserves this behavior shape-for-shape; do not fix incidentally; the right fix is a separate body-suppression rung.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md` in full (no exceptions).
2. Confirm baseline gates: template-byte-id should still be 4/4.  Smoke/broker remain at upstream-emergency baseline until the SI-6 session lands its repair.
3. Port `sm_jump.c`:
   - Add `t_test_rax_rax()` — BINARY: `48 85 C0`; TEXT/MACRO_DEF: `test rax, rax` line via `bb3c_format(bb_emit_out, "", "test", "rax, rax")`.
   - Add `t_emit_jmp(bb_label_t *target, jmp_kind_t kind)` — BINARY: 1-byte opcode (unconditional `0xE9`) or 2-byte opcode `jmp_rel32[k]` (conditional) + `bb_emit_patch_rel32(target)`; TEXT/MACRO_DEF: `bb3c_emit_jmp(bb_emit_out, mn, target->name)` where `mn` indexes into `{"jmp","je","jne","jl","jge","jg"}`.
   - Replace `EMIT_JMP(e, ...)` and `emit_test_rax_rax(e)` in `sm_jump.c` with the `t_` versions.  Mark `(void)e`.
4. Port `sm_arith.c`:
   - Reads op enum into rdi via `t_mov_rdi_imm64`, then `t_call_sym_plt("rt_arith", 0)`.  Both helpers exist.
5. Once all 5 SM templates are ported, **the SM axis is done**.  BB templates (xchr/xspnc/xbrkx/xlnth/xposi/xfarb) come next — and **the BB family is where the prior reverted attempt failed** (binary data section vs heap-allocated zeta).  The three-way pattern resolves this naturally: `t_data_section_begin`, `t_data_label`, `t_data_quad_sym`, `t_data_long`, `t_data_section_end` are no-ops in BINARY (no `.data` in bb_pool); they emit text in TEXT/MACRO_DEF.  The binary path heap-allocates the zeta directly in the template (still plain C; no `if (mode)` branch needed because the data-section helpers harmlessly no-op).
6. Eventually: delete `emitter_t`, `emitter_text.c`, `emitter_binary.c`, `emitter_macro_def.c`, all `EMIT_OPT` macros, all `static inline void emit_X(emitter_t *e, ...)` declarations in `emitter.h`.  Rename `t_*` helpers to drop the prefix.

### The pattern, for quick reference

```c
/* helper in bb_emit.c — three-way switch on bb_emit_mode */
void t_FOO(args) {
    switch (bb_emit_mode) {
    case EMIT_BINARY:    /* bb_emit_byte(...) bytes here */       return;
    case EMIT_TEXT:      /* bb3c_format(bb_emit_out, ...) line */ return;
    case EMIT_MACRO_DEF: /* same shape as TEXT for body lines */  return;
    }
}

/* template body — plain C calling plain C helpers */
void emit_sm_FOO(emitter_t *e, args) {
    (void)e;                  /* transitional: caller still passes e */
    t_comment("SM_FOO");
    t_macro_begin("FOO", params, n);
    t_FOO_helpers(...);
    t_macro_end();
    t_pad_to_blob_size();
}
```

That's the shape.  Three-way at the leaf, plain C above.
