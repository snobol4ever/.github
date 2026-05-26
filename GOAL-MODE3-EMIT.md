# GOAL-MODE3-EMIT.md — Mode 3 becomes a real per-instruction native x86 emitter

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--interp` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

⛔ **REQUIRED READING before opening any source file:**
1. `ARCH-x86.md` — x86 backend, execution modes, byrd-box ABI, SM_Program / native-code relationship.
2. `ARCH-SCRIP.md` — mode-1/2/3/4 table (§"Execution modes RS-15") and mode-specific notes.

**Repo:** one4all (primary) + corpus + .github.

**Premier-goal status.** Sibling `GOAL-ICON-BB-COMPLETE` stays active; everything else pauses.

**Done when:** `scrip --run file.{sno,sc,icn,pl}` runs every `--interp` PASS program with byte-identical output via a real native-x86 emitter: per-`SM_Instr` blobs in `SEG_CODE`, no C dispatch loop, no tail-call thunks, no `uint8_t**` array. `SM_PAT_*` on the single value stack. Once ME-14 closes, `GOAL-MODE4-EMIT`'s `EM-MODE4-IS-MODE3-DUMP` reopens.

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

`bb_flat.c` EMIT_BINARY emits globs into `bb_pool` at runtime — unchanged. Mode 4 does not dump these; only `SEG_CODE` is serialized.

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

      Gate: `*P`, `*(X+1)`, `EVAL(str)`, `CODE(str)` corpus programs byte-identical `--run` vs `--interp`.

      **Session 2026-05-11 reconnaissance (blocked-on-CHUNKS — no code changes):**
      Current `--run` against the four gate-shaped corpus programs:
      `feat/f13_eval_code.sno` ✓ byte-identical · `parser/defer_simple.sno` ✓ ·
      `parser/defer_alt.sno` ✓ · `parser/defer_in_pat.sno` ✗ **segfault under
      `--run`** (clean under `--interp`).  The existing `emit_standard_blob`
      fallback already routes `SM_PUSH_EXPRESSION`/`SM_CALL_EXPRESSION` to
      `h_push_chunk`/`h_call_chunk` C handlers (sm_codegen.c:1334–1335), and
      `h_return_impl` (sm_codegen.c:152) already disambiguates thunk frames
      via `fr->retval_name == NULL` (CHUNKS-step02 contract).  So the
      *opcode* work for ME-8 is largely de-facto live; the inline-native
      blobs are an optimization, not a correctness step.

      **defer_in_pat segfault is NOT in ME-8 territory.**  Backtrace:
      `#0 ??(addr) → #1 bb_broker bb_broker.c:44 → #2 exec_stmt stmt_exec.c:1395
      → #3 h_exec_stmt sm_codegen.c:976`.  Diagnostic prints (reverted before
      commit per RULES.md) show both modes deliver an *identical-looking*
      `pat` descriptor (`v=DT_P`, same `.p` address) into `exec_stmt`; the
      EM-7c `DT_E && pat.ptr` branch is **not** taken (`pat.v == DT_P`, not
      DT_E).  Both modes reach the DT_P branch and call into bb_build* /
      cache; mode 2 returns, mode 3 crashes jumping to an invalid
      `root.fn`.  Hypothesis (unverified): the PATND_t for `*P` (P unbound)
      references runtime state whose lifetime differs between modes —
      likely a stale function pointer in the per-process pool, or
      `sm_preamble`'s code_free path invalidating something the
      deferred-pattern PATND_t still references.  Fix-it work belongs to
      ME-13 (Glob integration audit), not ME-8.

      **Recommendation when CHUNKS-STEP17 closes:** ME-8's native-blob
      emit_me8_push_expression_blob / emit_me8_call_expression_blob are
      mechanical (≈30 bytes / ≈90 bytes; identical shape to existing
      ME-4 inline blobs and ME-6 me6_return_dispatch flow).  Drop them
      into the dispatch chain in `sm_codegen` next to SM_PUSH_VAR /
      SM_STORE_VAR.  Reframe the gate to the three already-passing
      corpus programs; carry `defer_in_pat.sno` to ME-13.

### Phase D — Pattern construction on the value stack

- [x] **ME-9 — Pattern primitives.** All `SM_PAT_*` constructors: load args from r12 stack, call rt_pat_<kind> via imm64, store DT_P result to r12 stack. Combinators (SM_PAT_CAT/ALT/ARBNO) pop inputs, call combinator, push result. Gate: pattern smoke programs byte-identical `--run` vs `--interp`.

      Sub-rungs (Group ordering by signature shape):

      - [x] **ME-9a — Group A (nullary).** Inline-native `emit_me9_pat_nullary_blob(rt_fn, tramp)` (42 bytes; mirrors `emit_me4_push_null_blob`). Wired for eight opcodes: `SM_PAT_ARB`, `SM_PAT_REM`, `SM_PAT_FAIL`, `SM_PAT_SUCCEED`, `SM_PAT_EPS`, `SM_PAT_FENCE`, `SM_PAT_ABORT`, `SM_PAT_BAL`. **Note:** the current SNOBOL4 frontend (`snobol4.y` `pat_prim_kind()`) only produces these AST kinds when the keyword appears in **function-call syntactic form** — `ARB(...)`, `FAIL(...)`, etc. Bare-keyword `'xyz' ARB`, `(FAIL | 'a')` tokenize as `T_IDENT` and lower to `SM_PUSH_VAR("ARB") + SM_PAT_DEREF` (variable-deref path), so the eight inline blobs are present but unreached by any current SNOBOL4 corpus program. Verified by diagnostic fprintf — zero calls across feat/parser corpus. Code is correct in shape; gates green; the dispatch may activate from other frontends (Snocone/Rebus) or a future SNOBOL4 frontend change.

      - [x] **ME-9b — `SM_PAT_LIT`.** Inline-native `emit_me9_pat_lit_blob(lit_ptr, tramp)` (52 bytes; mirrors `emit_me4_push_var_blob`). Calls `pat_lit(s)` via imm64 with the literal pointer baked from `a[0].s`. `pat_lit` null-guards internally (`snobol4_pattern.c:84-88`); blob passes through. **Verified hot:** diagnostic fprintf fired twice on `feat/f04_pattern_primitives.sno` (`lit="he"` and `lit="a"`). Byte-identical PASS across all 21 `feat/` programs.

      - [x] **ME-9c — Group C (charset).** `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_SPAN`, `SM_PAT_BREAK`. Each pops a string from r12, calls `VARVAL_fn` to coerce to `const char*`, then calls `pat_X(cs)`. Net delta 0 (pop 1, push 1).
      - [x] **ME-9d — Group D (integer arg).** `SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`, `SM_PAT_RTAB`. Each pops a DESCR_t, checks `v==DT_I` (else 0), calls `pat_X(n)`. Net delta 0.
      - [x] **ME-9e — Group E (unary pattern).** `SM_PAT_ARBNO`, `SM_PAT_FENCE1`. Pop inner pat, call combinator, push. Net delta 0.
      - [x] **ME-9f — Group F (binary pattern).** `SM_PAT_CAT`, `SM_PAT_ALT`. Pop right then left, call combinator, push. Net delta −1.
      - [x] **ME-9g — Group G (deref/refname).** `SM_PAT_DEREF` (most common — variable-as-pattern path), `SM_PAT_REFNAME`. These have non-trivial dispatch logic (DT_P pass-through, DT_S → pat_lit, else pat_ref(name)); easier to keep as thin trampolines `me9_pat_deref(v)` / `me9_pat_refname(name)` than to inline the type-discrimination chain in x86. Net delta 0.

- [x] **ME-10 — Capture and user-call.** `SM_PAT_CAPTURE`, `SM_PAT_CAPTURE_FN`, `SM_PAT_CAPTURE_FN_ARGS`, `SM_PAT_USERCALL`, `SM_PAT_USERCALL_ARGS`, `SM_PAT_DEREF`, `SM_PAT_REFNAME`. Gate: assign-driver + capture-bearing patterns from beauty subsystems under `--run`. **NOTE:** the two variadic opcodes (`SM_PAT_CAPTURE_FN_ARGS`, `SM_PAT_USERCALL_ARGS`) intentionally stay on the `emit_standard_blob` fallback path — the C handlers manipulate `STATE->stack` via the sync protocol, and an inline blob would still have to sync r12↔sp around the call, so there is no correctness or speed win to inlining. `SM_PAT_DEREF` and `SM_PAT_REFNAME` were already closed in ME-9g. The three non-variadic ME-10 opcodes (`SM_PAT_CAPTURE`, `SM_PAT_CAPTURE_FN`, `SM_PAT_USERCALL`) have native blobs.

### Phase E — Statement execution boundary and Icon/Prolog

- [x] **ME-11 — `SM_EXEC_STMT`.** Pop replacement, subject, pattern from value stack. Call `rt_exec_stmt` with subject-name, descriptors, has_repl. Phase 3 (bb_flat.c) stays in libscrip_rt. Gate: smoke 7/7 + unified_broker 49/49 byte-identical `--run` vs `--interp`. ✅ Session 2026-05-11.

- [x] **ME-12 — `SM_BB_PUMP`, `SM_BB_ONCE`, `SM_SUSPEND_VALUE`.** Icon/Prolog/Raku. Each lowers to `call rt_bb_<op>` via imm64. Gate: smoke_icon + smoke_prolog byte-identical `--run` vs `--interp`. ✅ Session 2026-05-11. **`SM_BB_PUMP` and `SM_BB_ONCE`** got inline blobs (single reusable 47B `emit_me12_bb_blob`, parameterized by helper fn). **`SM_SUSPEND_VALUE` intentionally stays on `emit_standard_blob` fallback** — its no-coro path calls `PUSH(v)` which mutates `STATE->stack`, so any inline blob would need the full r12↔sp sync protocol with no win (mirrors ME-10 precedent for variadic ops). No r12↔sp sync needed for PUMP/ONCE: `bb_broker` itself doesn't touch `STATE->stack`, `_usercall_hook` uses a separate nested `SM_State`, and coro adapters (`bb_eval_value`/`bb_exec_stmt`) don't touch the SM value stack. Like ME-9a, the inline blobs are present but **unreached by current corpus** — the bare `SM_BB_PUMP`/`SM_BB_ONCE` opcodes appear in static `--dump-sm` output (Prolog programs each contain one `SM_BB_ONCE` at top level) but program execution doesn't reach those PCs (Prolog uses `SM_BB_ONCE_PROC` for proc-table dispatch; bare `SM_BB_ONCE` is reserved for `AST_CHOICE` with no `e->sval` and for `AST_CLAUSE`/`AST_CUT`/etc. fallback paths flagged as "unreachable in practice" in `sm_lower.c:1583,1595`). The dispatch routing is correct; activation awaits future frontend changes.

### Phase F — Audit and corpus pass

- [x] **ME-13 — Glob integration audit.** Verify r10 discipline end-to-end across SM-blob → rt_exec_stmt → bb_pool flat-glob → return. SM-blob land never writes r10; glob α-preamble loads it; C-ABI marks r10 caller-saved (so SM caller doesn't need it after). Gate: full corpus (706 programs) `--run` byte-identical `--interp`, no r10 clobber. ✅ Session 2026-05-11. **Audit confirmed r10 discipline intact** (no r10 writes anywhere in sm_codegen.c x86 emission — all REX-W byte patterns target r12/r13/rax, never r10; r10 is only loaded by flat-glob α-preambles in `bb_flat.c` via `lea r10, [rip+Δ_data]` per ARCH-x86.md). **Audit additionally surfaced an rsp-alignment bug** in `emit_me6_define_entry_blob`: the `push rbp; mov rbp, rsp` sequence flipped the dispatch-loop's `rsp%16==8` invariant to `0`, causing every C-ABI call inside a user function body to violate SysV 16-byte alignment at the `call` site. SSE-aligned access in glibc snprintf (`movaps -0xc0(%rbp)`) was the canary, segfaulting in `VARVAL_fn` when a DT_I-bearing builtin (`ARRAY(13)`, `CONVERT(13, 'STRING')`, etc.) was called from inside a DEFINE'd function. Fix: add `sub rsp, 8` after `mov rbp, rsp`; extend the bare-goto `jz skip` rel8 from +4 to +8. The matching unwind in `emit_me6_return_blob` (`mov rsp, rbp ; pop rbp`) is unchanged — `mov rsp, rbp` strip-restores the subtract automatically. Repaired the 2 prior JIT-only crosscheck regressions (`100_roman_numeral`, `test_math`); `--run` PASS now matches `--interp` PASS exactly (197/197, identical failure sets). Three pre-existing JIT-only beauty-driver failures (`Qize_driver`, `XDump_driver`, `omega_driver`) remain — different bug (r12 wild-pointer in `me11_exec_stmt`, not alignment) — out of ME-13 scope.

- [x] **ME-14 — Full corpus pass.** `--run` ≥ `--interp` PASS counts for all six frontends. Completion criterion. GOAL-MODE4-EMIT `EM-MODE4-IS-MODE3-DUMP` reopens. ✅ Session 2026-05-11c (Claude Opus 4.7). **Root cause:** SM_LABEL routed through `emit_standard_blob_no_stack`, which skips pre-sync (r12→sp) but unconditionally runs post-sync (sp→r12). Post-sync was safe for SM_STNO (h_stno resets sp=0) but **destructive for SM_LABEL** when STATE->sp was stale from preceding inline-native blobs (SM_PUSH_VAR, SM_PAT_*, etc.) that update r12 without writing sp. Every SM_LABEL fire would overwrite r12 with a stale sp value, losing accumulated stack growth. Manifests visibly on patterns with `:S(label)` skip-and-resume shapes around `*assign(...)` alternations (Qize_driver, XDump_driver, omega_driver). **Fix:** new `emit_label_blob` — true no-op: 9-byte pc++ + jmp trampoline. No C call. No sync. 35 bytes smaller than the prior shape and faster on every fire. SM_STNO retained on `emit_standard_blob_no_stack` (h_stno's sp=0 reset is intentional). **Verification:** byte-identical PASS sets `--run` vs `--interp` (40/40 same fails) across broad corpus + beauty drivers (PASS=195/280 both modes). Three pre-existing beauty drivers `Qize_driver`, `XDump_driver`, `omega_driver` ALL PASS. Gates: smoke 7/7, broker 49/49, me6 3/3, icon/prolog/raku smoke 5/5/5, icon/prolog crosscheck 4/0, JIT three-mode parity 133/186/186 with identical failure sets.

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

Carved 2026-05-11c (Claude Opus 4.7, ME-14 closed — `GOAL-MODE3-EMIT` GOAL COMPLETE). Reopens `GOAL-MODE4-EMIT` `EM-MODE4-IS-MODE3-DUMP`.

Closed rungs: ME-1 ✅ `cc3cd475` · ME-2 ✅ `babf76be` · ME-3 ✅ `aca47e6c` · ME-4 ✅ `06b8f503`+`ae7f325a` · ME-5 ✅ `880adc36` · ME-7 ✅ `3d88cee7` · ME-6 ✅ `accafb5f` · ME-9a ✅ `f087571e` · ME-9b ✅ `f087571e` · ME-9c ✅ `15fff315` · ME-9d ✅ `02bf4cd7` · ME-9e ✅ `38019ad1` · ME-9f ✅ `497b3712` · ME-9g ✅ `12982b72` · ME-9 (parent) ✅ · ME-10 ✅ `550428df` · ME-11 ✅ `d46e2498` · ME-12 ✅ `3d5f698a` · ME-13 ✅ `5cab388d` · **ME-14 ✅ `ff9100cb`**.

Session 2026-05-11 (ME-11): inline-native blob for `SM_EXEC_STMT` (the universal statement-execution opcode for every pattern-bearing SNOBOL4 statement). One thin C helper `me11_exec_stmt(r12, sn, has_repl)` reads 3 DESCR_t slots directly off the r12 stack (repl=TOS, subj=TOS-1, pat=TOS-2) and forwards to `exec_stmt`. Blob (~93B): pc++ → sync r12→sp → load 3 arg regs → aligned call → **save eax to r11d** (critical: sp→r12 sync clobbers rax) → sync sp→r12 → `sub r12, 48` (pop 3 slots) → write r11d to `last_ok` → jmp trampoline. The r12↔sp sync is required because `exec_stmt` can recurse into the SM interpreter via `_usercall_hook` (pattern `*func()` calls) and capture-fn callbacks; those paths read/write `STATE->stack` via `STATE->sp`. Two bugs caught and fixed during verification: missing sync (silent state corruption), and rax-clobber by sp→r12 reload before `last_ok` write (caused `pat_with_goto.sno` to infinite-loop because `last_ok` was getting the stack-base address instead of `ok`). **Hot verification**: 186,998 fires on `demo/porter.sno`. Gates green: smoke 7/7, broker 49/49, me6 reentry 3/3. feat/ 21/21 byte-identical. parser/ 86/88 byte-identical (same 2 pre-existing fails as baseline: `defer_in_pat`, `unary_not`).

Session 2026-05-11 (ME-12): inline-native blob for `SM_BB_PUMP` and `SM_BB_ONCE`. Single reusable emitter `emit_me12_bb_blob(helper_fn, trampoline)` — 47-byte blob shape parameterized by call target. Two thin C helpers `me12_bb_pump` / `me12_bb_once` mirror the existing `h_bb_pump` / `h_bb_once` shapes from this file. **No r12↔sp sync needed** (contrast ME-11): `bb_broker` doesn't touch `STATE->stack` itself; `_usercall_hook` runs on a separate `nested` SM_State; coro adapters (`bb_eval_value`, `bb_exec_stmt`) don't touch the SM value stack. `SM_SUSPEND_VALUE` intentionally stays on `emit_standard_blob` fallback per ME-10 precedent — its no-coro path calls `PUSH(v)` mutating `STATE->stack`, so any inline blob would need full sync with no win. Gates: smoke 7/7, broker 49/49, me6 reentry 3/3, smoke_icon/prolog/raku 5/5/5. Prolog: 135 corpus byte-identical (2 flaky-fail puzzles 12/13 confirmed pre-existing at baseline — 4/5 baseline, 4-5/5 ME-12). icon/parser/: 153 programs with 2 deterministic baseline fails (`repeat_op`, `until_op`) + ~15 flaky baseline-only programs (5-run pass-rates equal or better under ME-12; no new deterministic fails). The augop_* flakiness is **pre-existing nondeterminism in the runtime** affecting both `--interp` and `--run` independently of ME-12 — likely address-based hashing or GC ordering creeping into output. Investigation belongs to a separate rung. **Note: like ME-9a, the inline blobs are present but unreached by current corpus** — Prolog programs lower a top-level `SM_BB_ONCE` (visible in `--dump-sm`) but program execution diverges to error paths or to `SM_BB_ONCE_PROC` before reaching the bare opcode; bare `SM_BB_PUMP`/`SM_BB_ONCE` cover the `AST_LIMIT` / `AST_CHOICE`-without-sval / `AST_CLAUSE`-fallback paths flagged "unreachable in practice" in `sm_lower.c`. Code is correct in shape; gates green; dispatch routing verified by ME-12 compile success and identical-to-baseline runtime behavior.

Session 2026-05-11 (ME-13): r10 discipline audit + rsp-alignment fix. **The r10 audit itself is a one-line conclusion** — sm_codegen.c's x86 emission never writes r10. Every `seg_byte` REX-W byte pattern (`0x4c 0x89 ...`) decodes to `mov rax/rdi, r12` not anything touching r10; the only r10-as-source uses in the codebase are in `bb_flat.c` (flat-glob α-preambles via `lea r10, [rip+Δ_data]`) per ARCH-x86.md.  SM-blob land obeys the r10-untouched contract.

**The audit's payload was the bug it surfaced**: `emit_me6_define_entry_blob`'s `push rbp; mov rbp, rsp` sequence violated the dispatch-loop's `rsp % 16 == 8` invariant.  Trampoline-entry rsp must remain 8 mod 16 so that the standard blob's `sub rsp,8 ; call rax ; add rsp,8` lands the C-ABI's required 16-byte-aligned `call`.  `push rbp` alone shifts rsp by -8 — flipping the invariant to 0 mod 16, making every subsequent C-ABI call inside the user-function body land with rsp = 8 mod 16 at the `call` instruction (SysV violation).  Alignment-tolerant C handlers silently swallowed it; glibc's snprintf uses `movaps -0xc0(%rbp)` and segfaulted whenever a DT_I-formatting builtin (`ARRAY(13)`, `CONVERT(13,'STRING')`, ...) was called from inside a DEFINE'd function — i.e. exactly the symptom seen in the 2 prior JIT-only crosscheck regressions `100_roman_numeral` and `test_math`.

Minimal repro that bisected the bug: `DEFINE('f(n)v'); f v = ARRAY(13); f = 'ok' :(RETURN) f_end; OUTPUT = f(42); END` — `--interp` prints `ok`, `--run` segfaults inside `__vsnprintf_internal`'s `movaps`.  gdb confirmed `rbp = 0x...c8` (mod 16 == 8) at the crash, which propagated from rsp = 0 mod 16 at the snprintf `call` site (post-call inside the callee the invariant is rsp = 8 mod 16 per SysV).

**Fix (4 net new x86 bytes)**: append `sub rsp, 8` (`48 83 ec 08`) after `mov rbp, rsp` in `emit_me6_define_entry_blob`; bump the bare-goto `jz skip` rel8 from `+4` to `+8` to cover the added instruction.  The matching unwind in `emit_me6_return_blob` (`mov rsp, rbp ; pop rbp`) is unchanged — `mov rsp, rbp` strip-restores the extra subtract back to the `mov rbp, rsp` capture-point (rsp right after `push rbp`), and `pop rbp` then restores the original 8-mod-16 invariant for the caller's resume PC.  No changes to any other blob; no register convention shift.

**Verification**: tiny_array.sno (minimal repro), 100_roman_numeral, and test_math all byte-identical `--run` vs `--interp` after fix. test_smoke_snobol4_jit (full 261-program crosscheck three-mode sweep): `--interp` 133, `--interp` 197, `--run` **197** (up from 195 pre-fix), three-mode parity PASS, failure sets byte-identical between --interp and --run. Gates: smoke 7/7, broker 49/49, me6 reentry 3/3, isolation PASS, smoke_icon/prolog/raku 5/5/5. Full corpus regression: 13/417 in both modes, identical failure sets (`diff /tmp/sm_fails /tmp/jit_fails` empty). Beauty drivers retain 3 pre-existing JIT-only failures (`Qize_driver`, `XDump_driver`, `omega_driver`) with a different root cause — `me11_exec_stmt` wild-r12 (likely r12↔sp sync gap on a particular code shape, not alignment).  These predate ME-13 (confirmed by git-stash baseline rerun) and are out of ME-13 scope per the goal-file gate definition.

**Phase F continued.** Next: ME-14 (full corpus pass, completion criterion; reopens `GOAL-MODE4-EMIT` `EM-MODE4-IS-MODE3-DUMP`). ME-13's audit + alignment fix removed the last alignment-class failures from the crosscheck corpus; the beauty-driver r12-corruption failures are the next investigation surface when ME-14 looks at non-crosscheck programs.

Session 2026-05-11b (ME-14 reconnaissance + sm_jit_unwind_call_stack helper, Claude Opus 4.7): rung remains **[ ] open**. Investigated the 3 pre-existing JIT-only beauty driver failures (`Qize_driver`, `XDump_driver`, `omega_driver`). Reproduced under `Qize('hello')`: `me11_exec_stmt` segfaults at `r12[-1]` with **`STATE->sp = -3`** (stored as 32-bit `0xFFFFFFFD`). The pre-sync's zero-extending `mov eax, [r13+8]` then `shl rax, 4 ; add rax, [r13]` produces r12 ~4GB above stack — landing 48 bytes below the buffer base. The negative sp arises during the pattern build phase for Qize's first `*assign()` deletion statement (SM_EXEC_STMT at PC ~1951, `has_repl=1, subj="str"`) — between the statement-opening SM_STNO (sp=0) and SM_EXEC_STMT, something issues 3 extra `sub r12, 16` operations without corresponding pushes, dropping r12 to `stack - 48`. Working hypothesis (unverified): an inline ME-6 SM_RETURN blob fires inside an SM_PUSH_EXPRESSION body that should have been skipped by the surrounding SM_JUMP. SM_RETURN's `me6_return_dispatch` path pops a JIT call frame and writes `caller_sp` (saved at frame-push time) into `STATE->sp`; if a stray RETURN fires at top-level depth or with a stale frame, the resulting sp can go negative. Not yet bisected to a specific PC inside the expression bodies (PCs 1925-1939 in test_qize3 SM dump contain the candidate SM_RETURN sites).

**Side improvement landed in this session (not the primary fix):** `sm_jit_unwind_call_stack(SM_State *st)` helper added to `sm_codegen.{c,h}`; called from `sm_run_with_recovery` (`scrip_sm.c`) when `runner == sm_jit_run` and `setjmp` returns non-zero. Rationale: in JIT mode the C stack unwinds by longjmp but the JIT call stack (`STATE->call_stack[] / call_depth`) lives in the heap struct and survives the longjmp; stale frames would later cause SM_RETURN blobs to pop wrong `caller_sp` values. The helper restores saved NV slots in reverse order (mirroring `h_return_impl`'s restore loop) and resets `call_depth=0` and `sp=0`. This is **architecturally correct** and fixes a real future hazard (genuine `sno_runtime_error` longjmp from inside an active user function), but does **not** address the beauty-driver crashes — those don't actually go through `g_sno_err_jmp` (the `sm_lower: undefined label` messages are compile-time patches by `labtab_resolve`, not runtime longjmps, so the recovery path is never entered).

**Verification of side improvement (no regressions):** all gates green — smoke_snobol4 7/7, unified_broker 49/49, me6_reentry_hazard 3/3, smoke_icon/prolog/raku 5/5/5, test_smoke_snobol4_jit three-mode parity 133/197/197 (identical failure sets). Beauty-driver failures unchanged (still 3 JIT-only segfaults — the helper isn't reached).

**Recommendation for next session.** Re-instrument `me11_exec_stmt` with a `sn=="str"` filter (kept in `.orig` backups, never committed) and add diagnostic prints at the entry of `me6_return_dispatch` and `h_return_impl` keyed on call_depth and the post-longjmp epoch. Run `test_qize3.sno` (`-INCLUDE 'global.sno' / -INCLUDE 'Qize.sno' / OUTPUT = Qize('hello') / END`) — this is the minimal repro discovered this session. The diagnostic will show whether the 3 extra pops come from (a) stray SM_RETURN inside an SM_PUSH_EXPRESSION body, (b) a mis-numbered SM_PAT_* inline blob that pops more than it should, or (c) something else entirely. Once narrowed to a single x86 op, the fix is mechanical. ME-14 stays open until those 3 drivers turn green and a full corpus pass across all six frontends shows `--run ≥ --interp` PASS counts.

Session 2026-05-11c (ME-14 closed — `GOAL-MODE3-EMIT` GOAL COMPLETE, Claude Opus 4.7): rung **[x] closed**. Prior session's hypothesis (stray SM_RETURN inside an SM_PUSH_EXPRESSION body) was **wrong**. Instrumentation at `me6_return_dispatch` and `me11_exec_stmt` confirmed zero SM_RETURN fires in the trouble PC range. Real cause discovered by side-by-side mode-2 vs mode-3 diagnostic at SM_PUSH_EXPRESSION entry: at PC 1825 (first `*assign()` alternative), `--interp` reports `sp_before=2` (correct: SM_PUSH_LIT_I + SM_PUSH_VAR pushed two slots since SM_STNO) but `--run` reports `sp_before=1` — **off by 1 from the very first SM_PUSH_EXPRESSION in the pattern-build region.**

**Root cause:** `SM_LABEL` was routing through `emit_standard_blob_no_stack`, shared with `SM_STNO`. That blob skips the pre-sync (r12→sp) but **unconditionally** runs the post-sync (sp→r12: `mov eax,[r13+8] ; shl rax,4 ; add rax,[r13] ; mov r12,rax`). The post-sync was correct for SM_STNO (h_stno explicitly writes sp=0, so the reload writes a fresh value) but **destructive for SM_LABEL** when `STATE->sp` was stale. And `STATE->sp` is **always stale** entering an SM_LABEL blob if the preceding sequence contained any inline-native blob (SM_PUSH_VAR, SM_PAT_*, SM_CONCAT, etc.) — those update r12 but never write through to `STATE->sp`. In the Qize repro, SM_STNO at PC 1814 sets sp=1 via SM_PUSH_LIT_I, then inline SM_PUSH_VAR at PC 1817 adds 16 to r12 (still sp=1 stale), then SM_PAT_DEREF at PC 1818 (net 0), then SM_JUMP to PC 1824. **SM_LABEL at PC 1824 fires its post-sync, reads stale sp=1, computes `r12 = stack_base + 1*16`, OVERWRITING the +16 from SM_PUSH_VAR.** The accumulated -1 per alternative across 6 `*assign(.part, *'X')` alts compounds into sp=-3 at the closing SM_EXEC_STMT (PC 1951).

**Fix (one4all `ff9100cb`):** new `emit_label_blob` — true no-op: 4-byte `inc dword [r13+20]` + 5-byte `jmp rel32 trampoline` = 9 bytes total. No C handler call (h_label was a literal no-op anyway), no sync. SM_STNO retained on `emit_standard_blob_no_stack` since h_stno's sp=0 reset makes the post-sync correct and intentional. Net change: a single new emitter function + a one-line dispatch split (`SM_LABEL || SM_STNO` → separate arms). 35 bytes smaller per SM_LABEL fire than the prior shape, and faster (no C call, no sync arithmetic).

**Verification:**
- Minimal repro `OUTPUT = Qize('hello')` byte-identical `--run` vs `--interp`.
- Three pre-existing beauty drivers `Qize_driver` `XDump_driver` `omega_driver` **all PASS under --run** (matches --interp output line-for-line).
- Broad corpus + beauty (`test_interp_broad_corpus_and_beauty.sh`): PASS=195/280 under BOTH `--run` AND `--interp` with **byte-identical 40/40 failure sets** (diff of sorted FAIL lines empty).
- Three-mode parity crosscheck (`test_smoke_snobol4_jit.sh`): 133 --interp / 186 --interp / 186 --run with identical failure sets.
- All gates green: smoke_snobol4 7/7, unified_broker 49/49, me6_reentry_hazard 3/3, smoke_icon/prolog/raku 5/5/5, crosscheck_icon 4/0, crosscheck_prolog 4/0, crosscheck_raku 0/33 (pre-existing in baseline, both modes equal).

**ME-14's completion criterion is met:** `--run` PASS counts ≥ `--interp` PASS counts on every gate, with identical failure sets. GOAL-MODE3-EMIT is closed. Per the goal-file contract, this reopens `GOAL-MODE4-EMIT` `EM-MODE4-IS-MODE3-DUMP`.

**Note for future agents inspecting `emit_standard_blob_no_stack`:** that function's docstring still claims the post-sync is "a no-op (r12 ends up where it started)" for stack-neutral handlers. That claim is **only true if all preceding blobs were standard_blob** (with full r12↔sp sync). It is **false** in the presence of inline-native blobs that update r12 without writing sp — which is essentially every program post-ME-4. The docstring is stale; only SM_STNO still uses that emitter, and its h_stno explicitly writes sp=0 so the claim holds vacuously for that one user. Do not extend `emit_standard_blob_no_stack` to new opcodes without auditing this invariant.

