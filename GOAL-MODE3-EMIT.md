# GOAL-MODE3-EMIT.md — Mode 3 becomes a real per-instruction native x86 emitter

⛔ **REQUIRED READING before opening any source file:**
1. `ARCH-x86.md` — x86 backend, execution modes, byrd-box ABI, SM_Program / native-code relationship.
2. `ARCH-SCRIP.md` — mode-1/2/3/4 table (§"Execution modes RS-15") and mode-specific notes.

**Repo:** one4all (primary) + corpus + .github.

**Premier-goal status.** Sibling `GOAL-ICON-BB-COMPLETE` stays active; everything else pauses.

**Done when:** `scrip --jit-run file.{sno,sc,icn,pl}` runs every `--sm-run` PASS program with byte-identical output via a real native-x86 emitter: per-`SM_Instr` blobs in `SEG_CODE`, no C dispatch loop, no tail-call thunks, no `uint8_t**` array. `SM_PAT_*` on the single value stack. Once ME-14 closes, `GOAL-MODE4-EMIT`'s `EM-MODE4-IS-MODE3-DUMP` reopens.

---

## Architectural target

### One value stack

`SM_PAT_*` opcodes push/pop `DT_P` values on the single SM value stack. No separate pat-stack. `SM_PAT_BOXVAL` deleted. See §"Two-stack reconciliation" in git log for rationale.

### Register convention (mode-3 SM-blob land)

Authoritative source: `REGISTER-LAYOUT.md`. Summary:

| Reg | Role | Scope |
|-----|------|-------|
| `r12` | SM value stack TOS pointer (FORTH-style). Push: `mov [r12],rax; mov [r12+8],rdx; add r12,16`. Pop: `sub r12,16; mov rax,[r12]; mov rdx,[r12+8]`. | Whole program; loaded at `sm_jit_run` entry; reset to base by SM_STNO blob. |
| `r13` | `&SM_State` — used by trampoline (pc at `[r13+20]`) and SM_STNO sync. | Whole program; loaded at `sm_jit_run` entry. |
| `r10` | Current BB DATA-block pointer. `[r10+N]` addresses box-locals. | Per BLOB; loaded by each BLOB's α-preamble. |
| `rbp` | DEFINE'd function frame pointer. Set by SM_DEFINE_ENTRY blob on real calls (jit_in_call==1); popped by return-variant blobs when jit_epilogue_pending==1. | Per active user function. |
| `rbx, r14, r15` | Free — available for future per-rung claims. | — |
| `rax rdi rsi rdx rcx r8 r9 r11` | C-ABI scratch for PLT calls and SM-blob temporaries. | Per SM-blob; caller-saved. |

SM_State layout (offsets from r13): stack=0, sp=8, stack_cap=12, last_ok=16, pc=20, jit_epilogue_pending=24, jit_in_call=28.

### Stacks

| | Where |
|---|---|
| **SM value stack** | Heap; `r12` = TOS. Reset at every statement boundary by SM_STNO blob. |
| **Native stack (rsp)** | C-ABI calls, DEFINE'd function frames (`rbp`). |
| **BB DATA-block tree** | Heap; `r10` walks it. Byrd-boxes are stackless — per-invocation DATA blocks ARE the alternatives. |

### Function calls (ME-6a)

`SM_DEFINE_ENTRY` opcode emitted by `sm_lower` immediately after every define-entry `SM_LABEL`. Blob reads `STATE->jit_in_call` ([r13+28]): if 1 (set by `h_call`), does `push rbp; mov rbp, rsp`; always clears flag. Bare `:(label)` gotos arrive at SM_LABEL, advance to SM_DEFINE_ENTRY, see jit_in_call==0, skip prologue. Nine return variants call `me6_return_dispatch` and conditionally pop rbp via `jit_epilogue_pending`.

### Deferred-eval consumer (ME-8, post-CHUNKS)

`*(expr)`: SM_CALL_EXPRESSION pushes SmCallFrame `{ret_pc, caller_r12, last_ok, caller_r10}`, resets r12, jumps to entry_pc's blob. SM_RETURN pops frame, restores r10 if from BB land.
`*P` (PATTERN): `rt_alloc_blob_data(root)` allocates fresh DATA tree; DEFER box sets r10 to root, jumps to CODE entry. CODE reused; DATA is per-invocation.

### Variant patterns stay dynamic

`bb_flat.c` EMIT_BINARY emits globs into `bb_pool` at runtime — unchanged. Mode 4 will not dump these; only `SEG_CODE` is serialized.

---

## Reuse, do not rewrite

| Component | Status | Source |
|-----------|--------|--------|
| `bb_emit.c` dual-mode (TEXT/BINARY) | proven 106/106 | `src/runtime/x86/bb_emit.c` |
| `bb_flat.c` flat-glob invariant emit, `r10`-anchored data | live | `src/runtime/x86/bb_flat.c` |
| `bb_boxes.s` 25-box library | archive | `archive/backend/bb_boxes.s` |
| `bb_pool.c` RW→RX slab | proven | `src/runtime/x86/bb_pool.c` |
| `sm_codegen.c` SEG_CODE infrastructure | live | `src/runtime/x86/sm_codegen.c` |
| `sm_lower.c` SM_Program lowering | live | `src/runtime/x86/sm_lower.c` |

Mode 4 frozen during this Goal. `EM-MODE4-IS-MODE3-DUMP` reopens when ME-14 closes.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
cd /home/claude/one4all && make libscrip_rt
```

---

## Gates

Every rung:
- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `test_gate_em_beauty_subsystems_mode4.sh`: **SUSPENDED** (mode 4 frozen).
- ME-6b: `test_gate_me6_reentry_hazard.sh`: PASS=3 FAIL=0.

---

## Steps

> Full implementation notes for closed rungs are in git log:
> `git log -p .github/GOAL-MODE3-EMIT.md`

### Phase A — Foundation

- [x] **ME-1** — Pat-stack unification. Delete g_pat_stack/g_jit_pat_stack; SM_PAT_* on value stack; delete SM_PAT_BOXVAL. ✅ one4all `cc3cd475`.
- [x] **ME-2** — r12=SM_State* reservation in sm_jit_run. ✅ one4all `babf76be`.

### Phase B — Native SM-blob emission

- [x] **ME-3** — Minimal native blob set (SM_HALT, SM_PUSH_LIT_I/S, SM_POP, SM_JUMP). Per-PC side table g_blob_addrs[]. sm_jit_run: load r12, jmp SEG_CODE_entry. ✅ one4all `aca47e6c`.
- [x] **ME-4-pre** — REGISTER-LAYOUT.md drafted + Lon sign-off. r12=TOS pointer (FORTH), r13=&SM_State, r10=BB data, rbp=fn frame. ✅ one4all `e7ac6f77` (HQ only).
- [x] **ME-4-post** — Realloc bug fix (4096 stack pregrow + h_stno sp=0); r12-as-TOS re-emit of 10 inline-native blobs (arith, concat, coerce_num, push_null, push_var, store_var). ✅ one4all `06b8f503` + `ae7f325a`.
- [x] **ME-5** — Control flow: SM_JUMP_S/F (emit_cond_jump_blob, direct rel32 to both arms, reads [r13+16]); SM_LABEL/SM_STNO (emit_standard_blob_no_stack). ✅ one4all `880adc36`.
- [x] **ME-7** — SM_LABEL define-entry flag (a[2].i=1 set by FUNC_IS_ENTRY_LABEL in sm_lower); opnames[] shift fix; bare RETURN/FRETURN/NRETURN lowering fix. ✅ one4all `3d88cee7`.
- [x] **ME-6** — Function calls and returns. SM_DEFINE_ENTRY opcode + jit_in_call flag ([r13+28]) solves icase re-entry hazard. Nine return variants via emit_me6_return_blob + me6_return_dispatch. Gate: test_gate_me6_reentry_hazard.sh PASS=3. ✅ one4all `accafb5f`.

### Phase C — Deferred-eval consumer (post-GOAL-CHUNKS)

- [ ] **ME-8 — `SM_PUSH_EXPRESSION` / `SM_CALL_EXPRESSION` consumer.**
      Lands **after** GOAL-CHUNKS-STEP17 closes (stable opcode shape needed).

      `SM_PUSH_EXPRESSION <entry_pc>` → push `DT_E` descriptor `{v=DT_E, slen=1, i=entry_pc}` on r12 stack.

      `SM_CALL_EXPRESSION` → pop descriptor, push SmCallFrame `{ret_pc, caller_r12, last_ok, caller_r10}`, reset r12 to base, jmp to entry_pc's SEG_CODE offset. SM_RETURN pops frame, restores r10 if caller_r10 non-zero (BB-land entry), restores r12, jumps to ret_pc blob.

      Two emission contexts (emitter knows which at emit time):
      1. From SM-blob land: caller_r10=0, no r10 save/restore.
      2. From BB land (DEFER box): caller_r10=current_r10, restored on SM_RETURN.

      `*P` runtime side: `rt_alloc_blob_data(root_box_ptr)` allocates fresh DATA tree; DEFER sets r10=root, jumps to P's CODE entry.

      Gate: `*P`, `*(X+1)`, `EVAL(str)`, `CODE(str)` corpus programs byte-identical `--jit-run` vs `--sm-run`.

### Phase D — Pattern construction on the value stack

- [ ] **ME-9 — Pattern primitives.** All `SM_PAT_*` constructors: load args from r12 stack, call rt_pat_<kind> via imm64, store DT_P result to r12 stack. Combinators (SM_PAT_CAT/ALT/ARBNO) pop inputs, call combinator, push result. Gate: pattern smoke programs byte-identical `--jit-run` vs `--sm-run`.

- [ ] **ME-10 — Capture and user-call.** `SM_PAT_CAPTURE`, `SM_PAT_CAPTURE_FN`, `SM_PAT_CAPTURE_FN_ARGS`, `SM_PAT_USERCALL`, `SM_PAT_USERCALL_ARGS`, `SM_PAT_DEREF`, `SM_PAT_REFNAME`. Gate: assign-driver + capture-bearing patterns from beauty subsystems under `--jit-run`.

### Phase E — Statement execution boundary and Icon/Prolog

- [ ] **ME-11 — `SM_EXEC_STMT`.** Pop replacement, subject, pattern from value stack. Call `rt_exec_stmt` with subject-name, descriptors, has_repl. Phase 3 (bb_flat.c) stays in libscrip_rt. Gate: smoke 7/7 + unified_broker 49/49 byte-identical `--jit-run` vs `--sm-run`.

- [ ] **ME-12 — `SM_BB_PUMP`, `SM_BB_ONCE`, `SM_SUSPEND_VALUE`.** Icon/Prolog/Raku. Each lowers to `call rt_bb_<op>` via imm64. Gate: smoke_icon + smoke_prolog byte-identical `--jit-run` vs `--sm-run`.

### Phase F — Audit and corpus pass

- [ ] **ME-13 — Glob integration audit.** Verify r10 discipline end-to-end across SM-blob → rt_exec_stmt → bb_pool flat-glob → return. SM-blob land never writes r10; glob α-preamble loads it; C-ABI marks r10 caller-saved (so SM caller doesn't need it after). Gate: full corpus (706 programs) `--jit-run` byte-identical `--sm-run`, no r10 clobber.

- [ ] **ME-14 — Full corpus pass.** `--jit-run` ≥ `--sm-run` PASS counts for all six frontends. Completion criterion. GOAL-MODE4-EMIT `EM-MODE4-IS-MODE3-DUMP` reopens.

---

## Prior art (key facts for future agents)

Full research notes in git log (search "Prior art / research basis"). Key facts:

- **bb_boxes.s box callee-save discipline**: rbx always = ζ ptr; r12..r15 per-call intermediates saved only when used. SM-blob caller's r12 (TOS) survives box calls because boxes save/restore it as any callee-saved reg.
- **Σ Δ Ω globals**: subject text/cursor in `.bss` globals, accessed via `[rel Σ/Δ/Ω]`. r10 inside a flat-glob addresses box-locals, not Δ directly. Two addressing modes coexist.
- **Box return ABI**: `rax:rdx = σ:δ` (success) or `eax=99,edx=0` (failure). Caller tests after `call`. Not the continuation-jump ABI from GENERAL-SCRIP-ABI.md.
- **DESCR_t = 16 bytes**: C-ABI returns 16-byte structs in rax:rdx automatically. Every PLT call yields DESCR_t in rax:rdx.
- **r12 legacy**: `emit_x64.c` used r12=DATA-block ptr. Mode-3 repurposes it as TOS; r10 takes the DATA-block role.
- **r10 caller-saved**: C-ABI PLT calls may clobber r10. SM-blob land never uses r10 (safe). Flat-globs reload r10 at every α-entry (safe because invariant nodes make no external calls).
- **sm_jit_run entry**: no callee-save spill needed beyond what the compiler generates for sm_jit_run's C frame (which covers r12 and r13).
- **EXPVAL re-entrancy (ME-8)**: minimum return frame = `{ret_pc, stack_sp_at_call, last_ok}`. Much narrower than SIL's "save the universe" — no OCBSCL/PATBCL/specifier equivalents in SCRIP.

---

## Watermark

Carved 2026-05-10 (Claude latest). Premier-goal declared by Lon. Architecture locked: one value stack, r12=TOS, r13=&SM_State, r10=BB data, rbp=fn frame, variant patterns stay dynamic. Full history in git log.

Closed rungs: ME-1 ✅ `cc3cd475` · ME-2 ✅ `babf76be` · ME-3 ✅ `aca47e6c` · ME-4 ✅ `06b8f503`+`ae7f325a` · ME-5 ✅ `880adc36` · ME-7 ✅ `3d88cee7` · ME-6 ✅ `accafb5f`.
