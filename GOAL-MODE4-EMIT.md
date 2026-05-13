# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md`. Past sessions that inferred mode-3/4 from `sm_codegen.c` arrived at the wrong picture every time.

**Repo:** one4all. **Done when:** `scrip --jit-emit --x64 file.{sno,sc}` → standalone binary outputting identically to `scrip --sm-run`. Binary links `libscrip_rt.so`. M5 extends to Icon/Raku/Prolog/Rebus.

**Mode-4 is mode-3's SEG_CODE dumped to `.s`.** One shared emitter; no parallel text-emitter walking SM_Program.

---

## Law of Template Functions

One C template function per SM opcode / BB box. Output only via `t_*` helpers (`bb_emit.h`); they read `bb_emit_mode` and route to BINARY/TEXT/MACRO_DEF. `emitter_t *e` is unused (`(void)e;`). No other output path.

---

## Architecture

```
IR ─► sm_lower ─► SM_Program ─► sm_codegen ─► SEG_CODE
                                                  ├─ mode 3: jmp in-process
                                                  └─ mode 4: seg_code_dump_as_s() → .s → ld → ELF
```

Two emitter shapes in `sm_codegen_x64_emit.c`:
- `emit_sm_instr()` — SM opcodes → GNU-as macros (`sm_macros.s`), 3-column `LABEL: OPCODE args`
- `emit_bb_box()` — BB boxes → GNU-as procs, 4-column `LABEL: ; ACTION ; jmp target`

Five-phase pattern execution: (1) build subject, (2) build pattern, (3) match+backtrack, (4) build replacement, (5) write-back. Phases 1/2/4 can fail → `:F`.

---

## Key components

`bb_emit.c` (TEXT/BINARY dual), `sm_templates.c` (91 SM emitters), `bb_templates.c` (35 BB emitters), `bb_flat.c`, `bb_pool.c`, `stmt_exec.c`.

**libscrip_rt.so boundary** — in: NV table, GC, builtins, `bb_pool`, BB broker. Out: `scrip_rt_pat_*` builders, `exec_stmt→bb_broker`.

Readability: `SM_STNO` banner `# ==…==  # stmt N  (line L):  <src>  # ==…==`. Col-3 annotations add info not in col 2.

---

## Tracked artifacts protocol

Seven artifacts in `corpus/programs/snobol4/demo/`. Run after any session touching `bb_emit.c`, `bb_templates.c`, `sm_templates.c`, `sm_codegen_x64_emit.c`, or `rt.c`:

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

**All closed through EXVAL-3** (`e31ab505`) — EM-1..7d-prep, FORMAT-*, MODE4-IS-MODE3-DUMP -a..-u, TEMPLATE-COMPLETE TC-SM/BB, TC-UNSPLIT, DOPPELGANGER-PURGE, BB-PURGE, EC-1..8, BB-TEXT-ADDR, BB-R10-FIX, BB-FORMAT-ARCH..9, SPEC-T-ERADICATE, EXVAL-1..3, ESA-1..3, EM-XVAL-DESCR.

**Open:**

- [ ] **EM-MODE4-IS-MODE3-DUMP** (parent) — Gates: smoke 7/7, broker 49/49, snocone 5/5, template-byte-id 4/4, artifacts gcc-c clean. ⛔ Read `one4all/MIGRATION-MODE4-IS-MODE3-DUMP.md` first.
- [ ] **EM-BB-FORMAT** (parent) — closes when smoke 7/7, template-byte-id 4/4, snocone 5/5, `gcc -c` clean, beauty ≥10. Spec: each BB port = one 4-column `;`-separated GAS line, widths 24/16/32/free. ⛔ No if-statements in template functions.
- [ ] **EM-7d** — beauty.sno PASS=14/17. Remaining FAILs: `counter_driver` (pre-existing mode-2 bug, parity break), `semantic_driver` (tests 4–7 silent-skip in mode-4 — **root cause: bb_pool exhaustion**, see watermark), `stack_driver` (pre-existing lowering bug). Accept counter/stack as known divergence.
- [ ] **EM-8** — `--jit-emit --x64 beauty.sc` + smoke_snocone 5/5 on emitted binaries.
- [ ] **EM-9** — M2 close: document `libscrip_rt.so` ABI; `make jit-emit-test`; mark GOAL-CHUNKS Step 8 `[x]`.

### M5 phase — Icon, Raku, Prolog, Rebus

⛔ Do not begin until GOAL-CHUNKS M4 (Steps 12–18) closes.

- [ ] EM-10..EM-16 — SM_SUSPEND/RESUME, multi-frontend, M5 close. Details deferred.

---

## Definitions

- **mode 4 / `--jit-emit`** — emit standalone asm/binary linked against `libscrip_rt.so`.
- **baked-direct opcode** — inline x86 (SM_PUSH_INT, SM_ADD, SM_JUMP); no PLT call.
- **runtime-call opcode** — PLT call into `libscrip_rt.so` (SM_PAT_MATCH etc.).

---

## Watermark

**SESSION HANDOFF — sess 2026-05-13d (Claude Sonnet 4.6)**

**Diagnosis: semantic_driver tests 4–7 = bb_pool exhaustion.** one4all HEAD `c0675506` (no code changes — diagnosis only). Gates: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty 14/17.

### Root cause

`global.sno` runs ~163 `&ALPHABET POS(N) LEN(M) . var` pattern-match statements at startup. Each allocates a page-aligned `bb_pool` entry (4 KB minimum). `BB_POOL_SIZE = 4 MB` (`bb_pool.h:35`). By the time `'' nPush()` executes in semantic_driver, the pool is exhausted. `bb_alloc` calls `abort()` on exhaustion, but the binary exits 0 silently because `sm_run_with_recovery`'s `setjmp` catches it. Standalone tests without beauty includes pass; full beauty includes trigger the silent skip.

### Fix direction

Two options: (a) increase `BB_POOL_SIZE` 4 MB → 16 MB; (b) add `bb_pool_reset()` (set `pool_top = pool_base`) called after each `exec_stmt` — patterns don't outlive their statement, so this reclaims all memory without freeing the mmap slab. Option (b) is architecturally correct.

### Next session must

1. Read `RULES.md`, `ARCH-x86.md`, `ARCH-SCRIP.md`.
2. Confirm baseline: smoke 7/7, template-byte-id 4/4, snocone 5/5, beauty 14/17. one4all HEAD `c0675506`.
3. **Fix bb_pool exhaustion** — implement `bb_pool_reset()` in `bb_pool.c`; call it in `rt_match_variant` after `exec_stmt` returns (or in `stmt_exec.c` at Phase-5 end). Gate: beauty ≥15/17 (semantic_driver tests 4–7 now passing).
4. counter_driver / stack_driver: pre-existing mode-2 bugs — accept as known divergence.
