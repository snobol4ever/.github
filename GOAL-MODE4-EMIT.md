# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **REQUIRED READING before opening any source file:**
1. `ARCH-x86.md` — x86 backend, four execution modes, BINARY/TEXT dual-emitter, byrd-box ABI, SM_Program / native-code relationship.
2. `ARCH-SCRIP.md` — mode-1/2/3/4 definitions at §"Execution modes (RS-15)".

Past sessions inferred mode-3/4 semantics from `sm_codegen.c` instead of these docs — every time the inferred picture was wrong. Architecture docs are the source of truth; source code is the incomplete realization.

**Repo:** one4all (primary). **Carved sess #62, 2026-05-05.**

**Done when:** `scrip --jit-emit --x64 file.{sno,sc}` produces a standalone binary that, run via `./prog < input`, outputs identically to `scrip --sm-run`. Emitted binary links against `libscrip_rt.so`. After Step 19 (M5), scope extends to Icon, Raku, Prolog, Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** Mode-3 and mode-4 share ONE emitter. Mode-3 produces native bytes in SEG_CODE; mode-4 runs mode-3 then disassembles SEG_CODE bytes back to `.s`. Byte-identity is by construction; no parallel text-emitter walking SM_Program.

---

## ⚡ THE LAW OF TEMPLATE FUNCTIONS

**One C template function per SM opcode and per BB box. That is the only way to emit anything.**

- Called by **both mode 3 and mode 4**. Not mode-4-only.
- All output goes through **`t_*` free-standing helpers** declared in `bb_emit.h`. These read `bb_emit_mode` internally and route to BINARY / TEXT / MACRO_DEF output.
- The `emitter_t *e` parameter exists for call-site compatibility but is **unused inside the body** (`(void)e;`). Do not call through it.
- **No other output path exists or is permitted.**
- Inline comments in col 3 carry only info NOT visible in col 2.

---

## Architectural target

```
file.{sno,sc} ─► [parser] ─► IR ─► [sm_lower] ─► SM_Program
                                                      │
                                              [sm_codegen]   ← ONE emitter; populates SEG_CODE
                                                      │
                                            SEG_CODE (RX in process)
                                                      │
                                    ┌─────────────────┴─────────────────┐
                                    ▼                                   ▼
                            mode 3 (in-process):              mode 4 (to disk):
                              jmp SEG_CODE_entry                seg_code_dump_as_s()
                              program runs in-process           writes file.s + sm_macros.s
                                                                      │
                                                                ld + libscrip_rt.so
                                                                      │
                                                                file (ELF)
```

---

## Two separate emitters (settled sess #67)

### 1. SM opcodes → macros

Universal IR. For x86 text-asm output, each opcode group maps to ONE GNU-as macro in `sm_macros.s`. Three-column shape: `LABEL: OPCODE args  # comment` (widths 24/16/free). `libscrip_rt.so` boundary: NV table, pattern matcher, GC, builtins. All other ops bake inline via macros.

### 2. BB boxes → three-column layout

One GNU-as proc per box. Three-column shape, literal `;` separators: `LABEL: ; ACTION ; GOTO`.

### Separation in sm_codegen_x64_emit.c

```
emit_sm_instr()  -- SM opcodes; flat macro call per opcode; SM-shape
emit_bb_box()    -- one proc per SM_PAT_*; BB-shape with ; separators
```

---

## Five-phase pattern execution model

| Phase | What | Failure mode |
|-------|------|--------------| 
| 1 | Build subject | can fail → `:F` |
| 2 | Build pattern (SM produces BB graph) | can fail → `:F` |
| 3 | Pattern match with backtracking | can fail → `:F` |
| 4 | Build replacement | can fail → `:F` |
| 5 | Perform replacement | — |

---

## Key components

| Component | Status | Source |
|-----------|--------|--------|
| `bb_emit.c` dual-mode (TEXT/BINARY) | live | `src/runtime/x86/bb_emit.c` |
| `sm_templates.c` — 91 SM opcode emitters | live | `src/runtime/x86/sm_templates.c` |
| `bb_templates.c` — 35 BB box emitters | live | `src/runtime/x86/bb_templates.c` |
| `bb_flat.c` flat-glob invariant emit | live | `bb_flat.c` |
| `bb_pool.c` RW→RX slab | live | `bb_pool.c` |
| `stmt_exec.c` Phase-3 driver | live | `stmt_exec.c` |

**libscrip_rt.so in:** NV table, GC, builtin shims, `bb_pool`, full SNOBOL4 runtime, BB broker.
**libscrip_rt.so out:** `scrip_rt_pat_*` descriptor-tree builders, `exec_stmt→bb_broker` chain.

---

## Generated-code readability standard

Major banner at `SM_STNO`: `# ====…====  # stmt N  (line L):  <source line>  # ====…====`
Inline col-3 annotations: `# str="…"`, `# var=NAME`, `# fname="…"` — nothing that duplicates col 2.

---

## Tracked artifacts protocol

Six artifacts in `corpus/programs/snobol4/demo/`: `roman.s`, `wordcount.s`, `claws5.s`, `treebank-list.s`, `treebank-array.s`, `sm_macros.s`, `bb_macros.s`.

Run after every session touching `bb_emit.c`, `bb_templates.c`, `sm_templates.c`, `sm_codegen_x64_emit.c`, or `rt.c`:

```bash
DEMO=/home/claude/corpus/programs/snobol4/demo; SCRIP=/home/claude/one4all/scrip
cd $DEMO
for f in roman wordcount claws5 treebank-list treebank-array; do
    $SCRIP --jit-emit --x64 $f.sno > $f.s 2>/dev/null; done
for s in roman.s wordcount.s claws5.s treebank-list.s treebank-array.s; do
    gcc -c "$s" -o /tmp/$(basename "$s" .s).o 2>/tmp/as_err.txt \
        && echo "OK $s" || { echo "FAIL $s"; cat /tmp/as_err.txt; exit 1; }; done
cd /home/claude/corpus
git add programs/snobol4/demo/{roman,wordcount,claws5,treebank-list,treebank-array,sm_macros,bb_macros}.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen <rung>"
```

---

## Steps

> Closed-rung details: `git log -p .github/GOAL-MODE4-EMIT.md`

### M2 phase — SNOBOL4 + Snocone

**Closed (all details in git log):**
- [x] EM-1..EM-7d-prep — Driver wiring, libscrip_rt skeleton, BB flat/text/binary, pattern integration, DEFINE entry, usercall registry, readability rungs.
- [x] EM-FORMAT-* — BB-LAW, DATA-CONSOLIDATE, BANNER-COLLAPSE-SPACE, SUBLIME-GAS-INTEL, all sub-rungs.
- [x] EM-MODE4-IS-MODE3-DUMP -a..-u — design doc; all SM + BB templates; PURITY-1..5; artifacts; beauty-subsystems PASS=9. (`7e123dc6`)
- [x] EM-TEMPLATE-COMPLETE TC-SM-1..37, TC-BB-1..14 — 91 SM + 35 BB template functions. (`baa29424`)
- [x] TC-UNSPLIT-1..11 — reversed per-op file splits; 47 fragments deleted; bundles are source of truth. (`802c88ee`)
- [x] EM-DOPPELGANGER-PURGE EDP-1..12 — all parallel emitters deleted; `-Wl,--allow-multiple-definition` removed; clean link. (`a21a6e19`)
- [x] EM-BB-PURGE EDP-6..10 — `bb_build_brokered`; C BB bodies deleted; heap ζ typedefs deleted. (`267429d0`)
- [x] EC-1..8 — `rt_bb_*` runtime functions; `emit_bb_stateful`; merged duplicates; fixed intcur; removed `is_text` guards; `bb_emit.h` trimmed; `ARCH-EMITTER.md`. (`08707cb0`)
- [x] EM-BB-TEXT-ADDR — RIP-relative lea for Σ/Σlen in TEXT mode. (`e9808467`)
- [x] EM-BB-R10-FIX — `t_push_r10`/`t_pop_r10`; wrap memcmp in `emit_bb_xchr`. beauty PASS 8→10. (`d96d5520`)
- [x] EM-BB-FORMAT-ARCH..FORMAT-9 — port-context accumulator; all BB kinds in 4-column FORMAT; Icon BB boxes. (`cd0b5964`)
- [x] EM-SPEC-T-ERADICATE EST-1..4 — `spec_t` deleted; `bb_convert.h` deleted; locals migrated to `DESCR_t`. (`a2b65fb9`)
- [x] EXVAL-1 — audit bb_box_fn call sites for σ/δ assumptions; `doc/xval_audit.md`. (`799f8492`)

**Open:**

- [ ] **EM-MODE4-IS-MODE3-DUMP** (parent rung) — Gates: smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4, 5 artifacts gcc-c clean. ⛔ Read `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` first.

- [ ] **EM-BB-FORMAT** (parent rung) — `--bb-format` flag wired; FORMAT-ARCH..FORMAT-9 all closed. Parent closes when: smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty-subsystems PASS≥10.

  Key spec: each BB port = ONE 4-column `;`-separated GAS line. `LABEL: ; instr operands ; jmp target`. Widths 24/16/32/free. `⛔ No if-statements in C template functions — only t_* calls.`

- [x] **EM-XVAL-DESCR** — Cross-language BB value protocol complete: `descr_match_span`/`descr_bool` constructors; SNOBOL4/Prolog box returns updated; `scan_body_fn_u9` and `rt_bb_cap` type-tag guards added. *(EXVAL-1..3 all closed, `e31ab505`)*

- [x] **EM-S-ARTIFACTS-COMMIT** — `.s` artifacts committed every session touching emitter. Protocol block above covers all 7 files with `gcc -c` gate.
  - [x] **ESA-1** — Protocol updated to include `bb_macros.s` and use `gcc -c`. *(goal reorg)*
  - [x] **ESA-2** — Artifacts verified current; no emitter changes in EXVAL-2/3. *(Sonnet 4.6)*
  - [x] **ESA-3** — `scripts/util_regen_demo_s_artifacts.sh` added. *(Sonnet 4.6, `b8ef6b18`)*

- [ ] EM-7d — `--jit-emit --x64 beauty.sno` passes SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`). Blocked on: (a) `*Parse *Space RPOS(0)` divergence; (b) beauty self-host regression.
- [ ] EM-8 — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries.
- [ ] EM-9 — M2 milestone close: document `libscrip_rt.so` ABI; `make jit-emit-test`; mark GOAL-CHUNKS Step 8 `[x]`.

---

### M5 phase — extends to Icon, Raku, Prolog, Rebus

⛔ Do not begin until GOAL-CHUNKS.md M4 (Steps 12–18) closes.

- [ ] EM-10..EM-16 — SM_SUSPEND/RESUME, Icon/Raku/Prolog/Rebus frontends, M5 close. Details deferred.

---

## Definitions

- **mode 4 / `--jit-emit`** — emit standalone asm/binary linked against `libscrip_rt.so`.
- **`libscrip_rt.so`** — runtime support library for emitted binaries.
- **baked-direct opcode** — inline x86 (SM_PUSH_INT, SM_ADD, SM_JUMP). No PLT call.
- **runtime-call opcode** — PLT call into `libscrip_rt.so` (SM_PAT_MATCH etc.).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-12 (Claude Sonnet 4.6)**

**EXVAL-1 closed; grand master reorg.** one4all HEAD `799f8492`. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9.

### Work done

1. **EXVAL-1** (`799f8492`): audited `bb_box_fn` call sites. `bb_broker.c`/`bb_flat.c` type-agnostic ✓. `scan_body_fn_u9` (stmt_exec.c:736) uses `val.slen` without type check — SNOBOL4-specific. `rt_bb_cap` reads `cr.s`/`cr.slen` without `DT_S` guard. All other `rt_bb_*` SNOBOL4-specific by design. Filed to `doc/xval_audit.md`.
2. **Reorg**: collapsed GOAL-MODE4-EMIT.md from 2029 → ~230 lines. All closed rungs → one-liners with hash. 12 stacked watermarks deleted. Verbose preamble trimmed.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9. one4all HEAD `799f8492`.
3. **EXVAL-2** — Add `descr_match_span(σ, δ)` + `descr_bool(ok)` constructors; update SNOBOL4/Prolog box returns. Gate: build clean, smoke 7/7, broker 49/49.

---

**SESSION HANDOFF — sess 2026-05-12 (Claude Sonnet 4.6)**

**EXVAL-2 + EXVAL-3 closed; EM-XVAL-DESCR complete.** one4all HEAD `e31ab505`. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9, broker 22/49.

### Work done

1. **EXVAL-2** (`6f29d644`): `descr_match_span(σ,δ)` + `descr_bool(ok)` added to `bb_box.h`. `descr_match` aliased to `descr_match_span`. All 14 `rt_bb_*` calls in `rt.c` → `descr_match_span`. `pl_gamma()` → `descr_bool(1)`.
2. **EXVAL-3** (`e31ab505`): `scan_body_fn_u9` guards `val.slen` with `val.v == DT_S`. `rt_bb_cap cap_commit` guards `.s`/`.slen` with `cr.v != DT_S` coercion.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9. one4all HEAD `e31ab505`.
3. **ESA-2** — regenerate all 7 `.s` artifacts at HEAD and commit to corpus (`gcc -c` clean). Then **ESA-3**: add `scripts/util_regen_demo_s_artifacts.sh`.

---

**SESSION HANDOFF — sess 2026-05-12 (Claude Sonnet 4.6)**

**ESA-2 + ESA-3 closed; EM-S-ARTIFACTS-COMMIT complete.** one4all HEAD `b8ef6b18`. corpus HEAD `0843f58`. Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9.

### Work done

1. **ESA-2**: artifacts verified current (EXVAL-2/3 don't touch emitter; prior regen at corpus `1c30091` still valid). `gcc -c` clean on all 7.
2. **ESA-3** (`b8ef6b18`): `scripts/util_regen_demo_s_artifacts.sh` — emits 5 demo `.s`, verifies `gcc -c` clean on all 7, commits corpus with rung-name arg. Self-contained, idempotent (skips commit when no changes).
3. **EM-XVAL-DESCR** parent rung closed (all sub-rungs done).
4. **EM-S-ARTIFACTS-COMMIT** parent rung closed (ESA-1..3 done).

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty PASS=9. one4all HEAD `b8ef6b18`.
3. **EM-7d** — `--jit-emit --x64 beauty.sno` passes SPITBOL oracle. Blocked on: (a) `*Parse *Space RPOS(0)` divergence vs `--sm-run`; (b) beauty self-host regression. Diagnose with `--jit-emit` vs `--sm-run` diff on beauty.sno.
