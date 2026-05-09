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

- [ ] **EM-7c-bb-three-column-data — CURRENT.**  Convert the remaining `EV_TEXT` raw-block sites in `bb_flat.c` to three-column `LABEL: ; ACTION ; GOTO` form so emitted `.s` is uniformly three-column inside BB blobs (no more interleaved tab-indented two-column stretches).

      **Scope.**  Twelve raw multi-line `EV_TEXT(e, "\t.section .data\n...\n\tlea ...\n\tmov ...\n\tcall ...@PLT\n\ttest rax, rax\n", ...)` call sites in `bb_flat.c`, one per box-kind path that builds a static `cs_t` / `len_t` / `tab_t` / `rtab_t` / `fence_t` / `arb_t` / `rem_t` / `brkx_t` / `atp_t` / `dvar_t` / `arbno_t` slot / `cap_t` slot in `.data` and then emits a four-instruction (lea / mov esi / call / test) sequence in `.text` for the α and β paths.  Affected box kinds:

       1. charsets (XSPNC, XANYC, XBRKC, XNNYC) via `flat_emit_charset_call` (lines ≈263–286 of bb_flat.c).
       2. XLNTH (lines ≈373–384).
       3. XTB (≈395–406).
       4. XRTB (≈417–428).
       5. XFNCE (≈439–450).
       6. XFARB (≈460–471).
       7. XSTAR / XREM (≈481–492).
       8. XBRKX (≈505–516).
       9. XATP (≈530–541).
       10. XDSAR (≈555–572).
       11. XARBN child sub-proc (≈589–632) — `.data` slot + child entry preamble + box call.
       12. XNME / XFNME static `cap_t` + child sub-proc + α/β cap-call (≈669–754).

      **Plan.**

      1. Add a small helper `flat_data_emit_*` family in bb_flat.c (file-static) wrapping `ev3c` for `.data`-block emission:
         - `flat_data_section(e)` → emits `; .section .data ;`
         - `flat_data_label(e, name)` → emits `name: ; ; `
         - `flat_data_string(e, s)` → emits `; .string "<escaped>" ;`
         - `flat_data_quad(e, val)` → emits `; .quad <val> ;`
         - `flat_data_long(e, val)` → emits `; .long <val> ;`
         - `flat_data_zero(e, n)` → emits `; .zero <n> ;`
         - `flat_text_section(e)` → emits `; .section .text ;` then `; .intel_syntax noprefix ;`
         - `flat_globl(e, name)` → emits `; .globl <name> ;`
         - `flat_box_call(e, ζ_lbl, fn, mode)` → emits the four lines (lea rdi, [rip + ζ_lbl] / mov esi, mode / call fn@PLT / test rax, rax) each as a three-column action-only line.

      2. Replace each of the twelve EV_TEXT call sites with sequenced helper calls.  Mechanical edit per site; no logic changes.

      3. EV_TEXT calls that emit a single short string with `\\%c`/`\\%03o` escapes inside a `.string` (charset's char-by-char escape loop, lines 265–270) need a helper that builds the escaped string buffer first, then calls `flat_data_string` once.

      4. Verify three-column shape live for ALL bb_flat-emitted lines by grepping the regenerated artifacts for `^\t` (tab-leading) or `^    ` (4-space-indent) lines — both should be empty post-rung.

      **Done when.**

      - Every line emitted from `bb_flat.c` is in the three-column shape (or a banner / comment).
      - The five tracked artifacts (`roman.s` `wordcount.s` `claws5.s` `treebank-list.s` `treebank-array.s`) regenerate, assemble cleanly, and contain zero tab-indented or 4-space-indented instruction lines (only banners and three-column lines).
      - All gates GREEN: EM 12/12, smoke ×6, unified_broker 49, bb_flat_text 18, sm_phase2_sim 25.
      - `EM-7c invariant blob` end-to-end runtime check (the EM gate test 13) still produces `output='abXc'` byte-identical to `--jit-run`.

      **Not in scope (subsequent rungs):**

      - `EM-7c-bb-macros` (BB-side macro library — turns three-column ACTION columns into single macro names like `LEN_α`, `RPOS_β`).
      - `EM-7c-1to1-sm-macros` (NEW sub-rung to track: fill in template entries for `SM_LABEL`, `SM_STNO`, `SM_PUSH_LIT_F`, `SM_PUSH_NULL_NOFLIP`, `SM_PUSH_EXPR`, `SM_NEG`, `SM_EXP`, `SM_NEXT_PUSH` so the SM-side emitter has true 1:1 opcode-to-macro coverage).

- [ ] EM-7c-bb-macros — BB-side macro library, parallel to historical `snobol4_asm.mac`.  Column-2 BB content becomes single macro names like `LEN_α`, `RPOS_β`.

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

**C enum rename** for symmetry: `SM_POP` → `SM_VOID_POP`,
`SM_CALL` → `SM_CALL_FN`.  96 sites across 12 files.  Macro names
in emitted `.s` were already `VOID_POP`/`CALL_FN`; this completes
the symmetry.  Tracked artifacts byte-identical pre/post-rename.

**Files touched (one4all):**
- `src/runtime/x86/sm_emit_template.c`: `build_op_col` →
  `build_args_col`; `render_call_line` reformatted to
  `%-24s%-16s %s`; `render_macro_body` rewritten with `macro_line`
  helper for three-column body emission.
- `src/runtime/x86/sm_codegen_x64_emit.c`: added
  `emit_three_column_line` central helper; rewrote
  `strtab_emit_rodata`, `emit_chunk_registry`, `emit_file_header`,
  `emit_file_footer`, blob header, `.include` line; fixed `sm_line`
  to `%-24s%-16s %s`; stripped redundant annotations.
- 11 other files: `SM_POP`/`SM_CALL` enum rename only.

**Gates final state — 10/10 GREEN:**
- smoke ×6: snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4
- isolation PASS  |  unified_broker PASS=49
- EM gate PASS=12  |  bb_flat_text PASS=18  |  sm_phase2_sim PASS=25

**Tracked artifact line counts:**
| File | Lines |
|------|------:|
| roman.s | 178 |
| wordcount.s | 196 |
| claws5.s | 1241 |
| treebank-list.s | 1559 |
| treebank-array.s | 1763 |
| sm_macros.s | 230 |

All assemble cleanly; deterministic across back-to-back regen.

**Sample dispatch line:**
```
.Lpc1:                  PUSH_STR         .Lstr_0, 0 # str="ROMAN(N)UNITS"
.Lpc2:                  CALL_FN          .Lstr_1, 1 # fname="DEFINE"
.Lpc3:                  VOID_POP
.Lpc4:                  JUMP             .Lpc28
.Lpc16:                 RETURN_VARIANT   0, 2, 16 # SM_RETURN_F
.Lpc19:                 PAT_DEREF
```

Goal file condensed this session from 4830 lines to ~340.  Full
narrative history of every closed rung is in git log of
`.github/GOAL-MODE4-EMIT.md`.

Next rung: **EM-7c-bb-three-column** — BB boxes as 4-port α/β/γ/ω
clusters in `LABEL: ; ACTION ; GOTO` form, Greek-only port names.
