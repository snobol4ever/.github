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

**SESSION HANDOFF — sess 2026-05-11 (Claude Sonnet 4.6)**

Sub-rungs -h through -m landed this session. All gates green throughout.

| Rung | Kind | Template | one4all hash |
|------|------|----------|------|
| -h | SM | `sm_void_pop.c` — call rt_pop_void@PLT | `87f59f43` |
| -i | BB | `bb_xbrkx.c` — BREAKX; callback pattern | `1fcb9437` |
| -j | SM | `sm_jump.c` — JUMP/JUMP_S/JUMP_F | `cc21cf01` |
| -k | BB | `bb_xposi.c` — POS/RPOS; callback | `30b19814` |
| -l | SM | `sm_arith.c` — ADD/SUB/MUL/DIV/MOD | `3b431771` |
| -m | BB | `bb_xfarb.c` — XFARB/XEPS/XFAIL; nullary callback | `1fcb9437` |

**Gates at handoff (one4all `1fcb9437`):** smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4. claws5.s + treebank-list.s + treebank-array.s byte-identical.

**Files created:** `sm_void_pop.c`, `sm_jump.c`, `sm_arith.c`, `bb_xbrkx.c`, `bb_xposi.c`, `bb_xfarb.c`.
**Files modified:** `templates.h`, `bb_flat.h` (three new typedef), `bb_flat.c` (callbacks+wrappers+dispatch), `sm_codegen_x64_emit.c` (routes through templates), `Makefile`.

**Template pattern (established, follow for all subsequent sub-rungs):**

*SM:* one `.c` per opcode; rename old `emit_sm_<op>(FILE*,...)` to `_line`; new wrapper: `emitter_text_new` → template → `emitter_free`. Add to `templates.h` + Makefile scrip rule (NOT RT_PIC_SRCS).

*BB:* one `.c` per kind; add `bb_*_text_fn` typedef to `bb_flat.h`; text callback in `bb_flat.c`; `flat_emit_node` dispatch one-liner. Add to `templates.h` + Makefile scrip rule AND RT_PIC_SRCS.

**Next sub-rung: -n — SM-axis: CONCAT/COERCE_NUM/PUSH_NULL and other nullary RT-call ops.**
Pattern: identical to sm_void_pop (SM_TPL_NULLARY entries in sm_emit_template.c). One file, one function per opcode, each: `call rt_<name>@PLT`.

**Remaining after -n:** -o (SM_LABEL/SM_STNO), -p (SM_CALL_FN big), -q (SM_RETURN family + ABI), -r (remaining BB: XFNCE/XDSAR/XATP/XCAT/XOR/XSTAR/XCALLCAP/XNME/XFNME/XARBN), -s (SM_PAT_*), -t (generated macros), -u (close).
