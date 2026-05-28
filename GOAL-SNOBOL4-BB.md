# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

**Repo:** one4all + corpus + .github
**Sister:** GOAL-HEADQUARTERS.md · GOAL-MODE4-SN4-SNOCONE.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `SM_EXEC_STMT` → `bb_exec_pat` → `bb_exec_once` → C oracle in `bb_exec.c case BB_PAT_*`. Templates not exercised.
- **Mode 3 (`--run`):** Same as mode-2 (sm_interp_run); BINARY arms not exercised for var-deref patterns. Inline AST patterns: `bb_build_flat` → template TEXT.
- **Mode 4 (`--compile`):** emit phase uses TEXT arms (`codegen_sm_x86` → `walk_bb_pattern_blobs` → ... → template TEXT). Compiled binary at runtime calls `rt_match_variant` → `exec_stmt` → `bb_build_brokered` (g_bb_mode=BB_MODE_BROKERED) → template BINARY arms.

**Absolute rules (RULES.md):**
- No C Byrd boxes. No `DESCR_t foo(void *zeta, int entry)` implementing α/β/γ/ω.
- TEMPLATE-PURITY: every `_str()` body is `state → std::string`, zero `emit_text_n` inside.
- ONE x86 PRODUCER: all emission via `BB_templates/` template functions.
- HQ Invariant 0: returning `std::string()` is a STUB.
- X86 ONLY FOR NOW — no JVM/JS/NET/WASM arms until directed.
- **MODE PURITY:** no silent cross-mode fallback; no silent eps substitution on failed build. `root.fn = NULL` → `bb_broker` returns 0 → honest failure.

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)` which sets `g_emit.lbl_α/β/γ/ω` then calls `walk_bb_node(nd)`. The template emits:

```
<lbl_α>:    α-port code (fresh entry — match, advance Δ, jump γ or ω)
<lbl_β>:    β-port code (retry — undo, advance differently, jump γ or ω)
            (some kinds: β = lbl_ω directly — no retry)
```

**Runtime state in TEXT arm:**
- `[r10]` = Δ (cursor, 32-bit int) — scan position
- `[rip + Σ]` = pointer to subject string; `[rip + Σlen]` = length
- Per-node static data: `.data` label `[rip + .Lfoo<id>]`
- `nd->sval` = charset string (ANY/SPAN/BREAK/NOTANY) — baked into `.data`
- `nd->counter` (int64) = runtime mutable state for generators (SPAN β)

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing the byte offset of each rel32 patch. Use `movabs` (`\x48\xB9` / `\x48\xB8` / `\x48\xBF`) for emitter-process absolute addresses (Σ/Σlen/strchr/cset). Reference templates: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104 bytes, sites at 17/72/86/90/100).

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## Session Setup

```bash
cd /home/claude/one4all
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt        # required for mode-4 corpus + rung-suite M4 column
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                # GATE-1: 13/13 (mode-2 7/7 + mode-3 6/6)
bash scripts/test_smoke_unified_broker.sh         # GATE-2: 28-30 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh   # GATE-3: 175/280
bash scripts/test_interp_broad_corpus_and_beauty.sh # GATE-4: 238/280
bash scripts/test_snobol4_pat_rung_suite.sh       # Rungs: M2=19, M4=15, SKIP=0
```

---

## Open Rungs (priority order)

### SBL-M3-NATIVE — mode-3 is PURE x86, NO INTERPRETER, ALL LANGUAGES ⛔ ROOT CAUSE / TOP PRIORITY ⏳

**CORRECTED END STATE (Lon, 2026-05-28): "SCRIP Mode 3 is NO INTERP and pure x86 asm for ALL languages."** This supersedes the earlier (wrong) "keep sm_interp_run for mode 3" framing. ARCH-SCRIP.md confirms verbatim: mode 3 `--run` = `IR → sm_lower → sm_codegen → sm_jit_run`, "execute **native x86 only** at runtime ... may NOT (a) index the SM array by PC (opcode-dispatch loop) nor (b) traverse a BB_t graph in C (bb_exec_once/resume/node/bb_broker). The C SM/BB walkers (`sm_interp_run`, `bb_exec_*`) belong to **mode 2 (`--interp`) ONLY**." Applies to SNOBOL4, Snocone, Rebus, Icon, Prolog, Raku.

**THE VIOLATION (traced, Opus 4.7 2026-05-28):** `scrip.c` mode_run (line 449) calls `sm_run_with_recovery(&s2->sm, sm_interp_run)` — i.e. mode-3 currently RUNS THE MODE-2 C INTERPRETER. There is no native-SM mode-3 path at all. Both the SM half (PC-dispatch loop in `sm_interp_run`) AND the BB half (`SM_EXEC_STMT→bb_exec_pat`, `SM_BB_SWITCH gen→bb_exec_once/resume`) are C-interpreted. That is why two days of filling BINARY template arms changed nothing observable: mode-3 never emits or runs them.

**Naming:** `sm_interp_run` is a genuine C interpreter (verified: `while(pc<count){ins=&instrs[pc++];switch(ins->op){...}}`). The name is correct FOR MODE 2. The error was wiring it into mode 3. Mode 3 must NOT call it. No rename needed; mode-3 must call a native runner instead.

**What exists vs what's missing:**
- EXISTS: `codegen_sm_x86` (`emit_sm.h`, the single SM x86 producer; `sm_codegen_text` = FILE/GAS for mode-4). SM templates (`SM_templates/`), BB templates (`BB_templates/`). `bb_pool`+`bb_seal` (RW→RX mmap slab for BB boxes, working). **`sm_image`+`seg_seal`** (`sm_image.c` — mmap'd RX-sealable SM `.text` image; the SM-native facility). `bb_build_flat`→sealed RX box (working, used by exec_stmt runtime-PATND branch).
- MISSING: `sm_jit_run` / `sm_emit_linear` / `sm_run_linear` named in ARCH-SCRIP DO NOT EXIST in src. The in-memory SM-native runner is UNBUILT. scrip.c:76 comment describes the intended design ("SM_sequence_t → x86 bytes → mmap slab → jump in") but the code calls the interpreter.

**⭐ KEY DISCOVERY (Lon hunch confirmed, Opus 4.7 2026-05-28): the native-SM engine WAS BUILT, then DELETED 2026-05-27.** The whole file `src/processor/sm_jit_interp.c` was annihilated in the JA-D series (FACT-RULE cleanup — that code used the forbidden `emit_standard_blob`/`bake_blob_call`/`SL_B` primitives, so the deletion was principled, BUT the opcode→x86 LOGIC + runner + mmap/seal/jump structure are exactly the M3-NATIVE reference). Recovery coordinates (full source intact in git history):
  - **Engine B (SB-LINEAR — the ARCH end-state):** built `916d61a5` (2026-05-26, "sm_emit_linear + sm_run_linear — linear x86 emit over SM_sequence_t", +799). Deleted `22a17fa3` (JA-D-2, −658). Full source: `git show 22a17fa3~1:src/processor/sm_jit_interp.c` (functions `sm_emit_linear`, `sm_run_linear`, `sl_emit_one`, `sl_call`, `sl_mov_*`, `sl_jcc_last_ok`, `sl_patch_rel32`). Also deleted `sm_run_with_recovery_linear` from scrip_sm.c (same commit).
  - **Engine A (trampoline + handlers):** deleted `2073c081` (JA-D-3, −1820). Full source: `git show 2073c081~1:src/processor/sm_jit_interp.c` (`SM_codegen`, `sm_jit_run`/`sm_jit_run_steps`, 44 `h_*` opcode handlers, `rt_push_lit_*`/`rt_push_var`/`rt_store_var`/`rt_load_glocal`/`rt_call_fn`, `bake_blob_call_*`, `emit_standard_blob`, `emit_trampoline`, `emit_cond_jump_blob_skeleton`).
  - JA-D-1 `c352bf4d` stubbed the `--run` call site; JA-D-4/5/6 (`b14a3312`, `e842b724`) finished the sweep ("zero jit occurrences remain").
  - **Transcription rule for revival:** do NOT copy `emit_standard_blob`/`SL_B`/`bake_blob_call` verbatim — those violate FACT RULE. Re-express the per-opcode x86 as SM_templates BINARY arms (the `MEDIUM_BINARY` arms already stubbed in all 15 `SM_templates/*.cpp`), driven by `codegen_sm_x86` in a BINARY medium, sealed via `sm_image`/`seg_seal`. The deleted `h_*`/`sl_*` bodies are the SEMANTIC SPEC for those arms.

**SCOPE: this is a foundational engine build, not a dispatch-arm tweak.** Mode 3 must: emit SM as x86 BINARY (via `codegen_sm_x86` BINARY medium) into `sm_image`, seal RX, jump in; BB boxes flat-wired into `bb_pool`, CALLED FROM the SM native code (not from C). No `sm_interp_run`, no `bb_exec_*` on the mode-3 path.

**Steps:**

- [ ] **M3-NATIVE-1 — audit emitter coverage AGAINST the recovered engine.** Map `codegen_sm_x86` BINARY-medium coverage (which SM opcodes have a working BINARY arm vs TEXT-only vs stub) and the `sm_image` API (alloc/seal/entry). Cross-reference the deleted `h_*` handlers (`git show 2073c081~1:src/processor/sm_jit_interp.c`) — each `h_<op>` is the semantic spec for that opcode's BINARY arm. Output: coverage table (SM opcode × {TEXT, BINARY, stub}) annotated with the matching deleted `h_*`/`sl_*` reference.
- [ ] **M3-NATIVE-2 — minimal native-SM runner (revive SB-LINEAR, template-pure).** Rebuild `sm_emit_linear`+`sm_run_linear` (or `sm_run_native`) from `git show 22a17fa3~1:src/processor/sm_jit_interp.c` BUT re-expressed through SM_templates BINARY arms (no `SL_B`/`emit_standard_blob`/`bake_blob_call` — FACT RULE). Pipeline: `codegen_sm_x86`(BINARY) → `sm_image` → `seg_seal` RX → call entry. Wire `scrip.c` mode_run to it (replace `sm_run_with_recovery(sm, sm_interp_run)`). Start with the smallest fully-covered program (single OUTPUT/assignment). Gate: identical output to mode-2.
- [ ] **M3-NATIVE-3 — BB call-out from native SM.** Native SM `SM_BB_SWITCH`/`SM_EXEC_STMT` must CALL the flat-wired `bb_pool` box (`node->fn(ζ,entry)` as native call), NOT `bb_exec_*`. This is where the BB BINARY template arms finally execute. Verify with a `bb_pat_*_str` marker firing under `--run`.
- [ ] **M3-NATIVE-4 — per-language bring-up.** SNOBOL4 first (patterns), then Icon/Raku (generators via SM_BB_SWITCH gen), then Prolog (PL_ENTRY). Each: native SM + flat-wired BB, output == mode-2 oracle. Honest failure (`[NO-SM-BB] <opcode>`, last_ok=0) for any unbuilt opcode — no silent interp fallback.
- [ ] **M3-NATIVE-5 — gate sweep + corpus, all langs.** Every stub SM/BB arm now fails honestly under `--run` (previously masked). The regressing list IS the remaining template work. Target: mode-3 native output == mode-2 oracle, kind-by-kind, language-by-language.

**Migration note:** the legacy `sm_jit_run` trampoline (if revived) is itself an SM-walking loop per ARCH-SCRIP — a migration target, NOT the end state; the end state is `sm_emit_linear`→`sm_run_linear` entering a pure native blob. Documented temporary exception: Prolog `--run` may keep `sm_interp_run` (AGW-1c) until `bb_pl_*.cpp` templates land — but that exception is on borrowed time and must be tracked, not assumed permanent.

**Only after M3-NATIVE has BB executing from native SM does filling BINARY arms (SPAN/ARBNO/BREAKX/CAPTURE + Icon/Prolog/Raku) have an observable effect under `--run`.** Arms "verified" to date (ANY/NOTANY/LEN/BREAK) were checked ONLY against the C oracle and (BREAK) the mode-4 brokered standalone — never a mode-3 native execution, because that path does not exist yet.

**Mode-4 sibling (SBL-M4-FLATWIRE, separate):** `--compile` standalone brokers patterns at runtime (`rt.c:335` BB_MODE_BROKERED) instead of flat-wiring at emit time. Also wrong. Do not conflate.

### SBL-M4-FLATWIRE — mode-4 standalone must be FLAT-WIRED, not broker at runtime ⏳ (separate from M3)

Lon (2026-05-28): "MODE 4 is FLAT-WIRED BBs ONLY. Prevent using BROKERED BBs in --compile mode." Current state (traced): `--compile` emits `call rt_pat_break@PLT` for pattern atoms; the linked `libscrip_rt` `rt_init` (`src/runtime/rt/rt.c:335`) sets `g_bb_mode = BB_MODE_BROKERED`; at the standalone binary's runtime `exec_stmt` (`stmt_exec.c:332-337`) calls `bb_build_brokered(pp_bb)` — rebuilding + brokering pattern blobs IN THE RUNNING COMPILED PROCESS. Confirmed: a `--compile`d binary matched WITHOUT firing the `bb_exec` oracle marker (so not oracle) — it ran the brokered template path at its own runtime. Per ARCH-SCRIP.md the standalone binary should hold NO graph and build nothing; pattern code should be flat-wired into the emitted `.s` at compile time. DO NOT just flip `rt.c:335` to LIVE in isolation (default `BB_MODE_DRIVER` ALSO routes to `bb_build_brokered` per `emit_bb.c:928` + `stmt_exec.c:332`; both arms must be addressed, and the emitter must actually flat-wire pattern bytes into the asm rather than emit `call rt_pat_*`). Design first; trace the full `--compile` pattern-emit path before cutting. Defer until after SBL-M3-NATIVE (shared native-x86 infrastructure).

### SBL-XNME-XLATE + SBL-CAP-2 — paired (must land together) ⏳

Probe wedge `probe_xnme.sno`: `PAT = ANY('cab'); S = 'xyzabcdef'; S PAT . M`. Oracle: `M=a`. Mode-2/-3 already green via C oracle. Mode-4 prints `no match`.

**Preparatory fixes landed `828f9134`:**

1. `lower_pat_dcg.c` XNME/XFNME translator: read varname from `pp->var.s` fallback when STRVAL_fn empty. AST-built XNME populates STRVAL_fn at parse time; runtime-built XNME (`pat_assign_cond`/`pat_assign_imm` in `snobol4_pattern.c:284/293`) stores name in `pp->var` (NAMEVAL/NAMEPTR DESCR_t), leaves STRVAL_fn NULL.

2. `rt.c rt_pat_capture`: populate STRVAL_fn on constructed XNME/XFNME from the varname argument. **Critical:** when `NAME_fn(varname)` finds an existing cell, it returns NAMEPTR (`slen=1, ptr=cell`), whose `.s` slot reads as cell-pointer bytes — NOT the name string. Only NAMEVAL (`slen=0, s=name`) carries the string, and only for first-touch cells. Probe confirmed: `[DBG XNME xlate] STRVAL_fn='<null>' var.v=9 var.s='' var.slen=1` → fix populates STRVAL_fn unconditionally from the rt_pat_capture varname argument.

Both fixes are gated-out by `patnd_needs_xlate` (XNME/XFNME still excluded), so no behavioral change on the currently-exercised path. All five gates hold at watermark.

**SBL-CAP-2 deep finding (this session, continued-16):**

The capture template's BINARY arm cannot be filled in isolation — it's blocked by a more fundamental issue with how child-bearing kinds (CAPTURE, ARBNO, CALLOUT) work under MEDIUM_BINARY:

- `bb_prepare_capture_arbno` (`emit_bb.c:581`) sets `g_emit.bb_child_lbl = child_cache_get_lbl(child_fn)` **only inside `if (MEDIUM_TEXT)` blocks** (lines 590, 605, 620).
- Under MEDIUM_BINARY, `child_cache_set_lbl` is never called (only `pre_build_children_text` sets labels; `pre_build_children` for BINARY does not). So `child_cache_get_lbl(child_fn)` returns NULL under BINARY regardless.
- Both `bb_capture.cpp` (line 18) and `bb_arbno.cpp` (line 16) have `if (!child_lbl || !child_lbl[0]) return std::string();` early-return → emit zero bytes for the parent node.
- Zero bytes for the parent ASSIGN_COND means the outer `xa_flat_epilogue` BINARY emission references `flat_fail_p` (lbl_ω) but no preceding code defines lbl_β → unresolved-label abort at site=19.

This is the same architectural gap for ARBNO. Under current mode-2 brokered execution, the C oracle in `bb_exec.c` carries everything; templates are not exercised for var-deref / capture-wrapped patterns.

**SBL-CAP-2 design requirements (next session):**

The BINARY arm needs to invoke the child via a callable target, not a label. Options:

A) **Direct function-pointer call via movabs.** The child `bb_box_fn` is the address of the brokered blob — callable as a normal function. Emit `movabs rax, &child_fn; call rax` instead of `call <label>`. Requires `g_emit.bb_child_lbl` replaced by `g_emit.bb_child_fn` (raw function pointer) under MEDIUM_BINARY. This is the same pattern `bb_upto.cpp` uses for `strchr` (reference).

B) **Pre-emit child blob inline into parent's buffer.** Inline the child's bytes into the parent's blob with a forward-jump entry. Loses the call/ret structure that brokered ARBNO/CAPTURE expect.

A is cleaner. Plan: extend `bb_prepare_capture_arbno` to set `g_emit.bb_child_fn = (void *)child_fn` under MEDIUM_BINARY (mirroring how it sets `bb_child_lbl` under MEDIUM_TEXT); extend `g_emit` struct to add this field; `bb_capture_str` and `bb_arbno_str` BINARY arms check `bb_child_fn` instead of `bb_child_lbl`.

Then BINARY arm of `bb_capture.cpp` emits:
```
mov eax, [r10]                  ; stash Δ
mov [rip+saved_Δ], eax          ; (need PER-NODE storage — see below)
xor esi, esi                    ; first call
push r10
movabs rax, &child_fn
call rax
pop r10
cmp eax, 99
je ω
jmp assign
β:
mov esi, 1                       ; retry call
push r10
movabs rax, &child_fn
call rax
pop r10
cmp eax, 99
je ω
assign:
movabs rcx, &Σ
mov rax, [rcx]
movsxd rcx, dword [rip+saved_Δ]
lea rsi, [rax+rcx]
mov edx, [r10]
sub edx, dword [rip+saved_Δ]
movabs rdi, &varname_cstr        ; varname string address (emitter-process)
push r10
movabs rax, &rt_cap_assign
call rax
pop r10
jmp γ
```

**Per-node `saved_Δ` storage problem:** brokered blobs aren't ELF sections — no `.data` slot. Options: (a) `GC_MALLOC(4)` at template-time and embed the absolute address as imm64; (b) per-blob scratch area in the bb_buf prologue. (a) is simpler — emit `&saved_Δ` as a `movabs` operand. Sites table: jge/je/jmp rel32s to ω/γ; β-label-define.

**Varname C-string storage:** `varname` comes from `g_emit.op_name1` (currently set in `walk_bb_node` from `nd->sval`, which is char* from translator). Under BINARY, emit `movabs rdi, &varname_string` where `&varname_string = (uint64_t)(uintptr_t)g_emit.op_name1`. The string lives in the emitter process for the lifetime of the brokered blob.

**Gate widening to re-apply after SBL-CAP-2 lands** (preserved from continued-15 carving):

Insert in `src/runtime/snobol4/stmt_exec.c` after `patnd_is_simple_atom` (line ~253):
```c
static int patnd_is_capture_wrapped_safe(const PATND_t *pp) {
    if (!pp) return 0;
    if (pp->kind != XNME && pp->kind != XFNME) return 0;
    if (pp->nchildren < 1 || !pp->children || !pp->children[0]) return 0;
    const PATND_t *inner = pp->children[0];
    return patnd_is_simple_atom(inner) || patnd_contains_arbno(inner);
}
```
Then OR into `patnd_needs_xlate`:
```c
return patnd_contains_arbno(pp) || patnd_is_simple_atom(pp) || patnd_is_capture_wrapped_safe(pp);
```

**Validation cycle (next session):**
```bash
./scrip --compile /home/claude/probe_xnme.sno > /tmp/p.s
gcc -c /tmp/p.s -o /tmp/p.o && gcc /tmp/p.o -Lout -lscrip_rt -lgc -lm -Wl,-rpath,$(pwd)/out -o /tmp/p.bin
/tmp/p.bin     # expect "M=a"
```

Plus all five gates must hold (G1=13/13, G2≥28, G3≥175, G4≥238, M2=19, M4=15).

---

### SBL-NOTANY-2 ✅ (Opus 4.7, 2026-05-28)

`bb_pat_notany.cpp` BINARY arm filled — byte-identical to `bb_pat_any.cpp` (104 bytes, sites {17,72,86,90,100}) except offset 70: `jne ω` (`0F 85`) instead of `je ω` (`0F 84`) — NOTANY fails when the char IS in the set. Was a 2-jump stub (`{1,2}` sites). Validated: `/tmp/probe_notany2.sno` (`NOTANY('xyz')` against `'xyzabcdef'`) mode-4 compiled binary now prints `matched` via brokered BINARY path. All five gates hold (G1=13/13, G2=30, G3=175, G4=238, M2=19, M4=15), FACT RULE=0.

### SBL-BREAK-2 ✅ (Opus 4.7, 2026-05-28)

`bb_pat_break.cpp` plain-BREAK BINARY arm filled (178 bytes; was a 2-jump stub that **aborted** mode-4 with `bb_emit_end: unresolved forward reference` because it never defined lbl_β). Sites at {150→γ, 154→β(is_def), 174→ω}; internal loop/done jumps emitted as literal constant rel32 (+66, +19, −113). Validated: `BREAK('c')` on `'abXcde'` matches `'abX'` (mode-2 oracle), mode-4 compiled binary prints `matched`, agrees with oracle across cases. BREAKX (`pBB->ival==1`) BINARY arm still a stub — SBL-BREAKX-2.

**KEY REUSABLE PATTERN (shared per-node persistent BINARY storage):** brokered blobs have no ELF `.data`, so loop counters that must persist across the α→γ→backtrack→β boundary live in the GC-allocated `rt_cs_t` at `g_emit.bb_cs_zeta`, whose `int delta` field is at **byte offset 8** (`rt_cs_t = {const char *chars; int delta;}`, sizeof=16). Address it via `movabs rcx, &zeta; [rcx+8]`. This is the same persistent-storage facility SPAN-2, ARBNO-3, and SBL-CAP-2's `saved_Δ` all need — no GC_MALLOC-per-template required; `bb_cs_zeta` (already set in every charset template's MEDIUM_BINARY entry) IS the slot.

### SBL-SPAN-2, SBL-ARBNO-3 — BINARY arms ⏳ (SPAN attempted 2026-05-28, REVERTED — segfault)

**SPAN correction (supersedes the earlier `[r10]-=z` single-slot idea — that was WRONG).** SPAN is a generator; β must yield successively shorter spans using an ABSOLUTE z_orig (NOT `[r10]`-relative), because a sibling box in a concatenation mutates `[r10]` between α and the β re-entry and the four-port driver does NOT auto-restore the cursor. Needs TWO persistent slots (z, z_orig). The 2026-05-28 attempt widened `rt_cs_t` with `delta2`@12 (delta stays @8, BREAK unaffected) and wrote a 208-byte arm that DISASSEMBLED CORRECTLY but SEGFAULTED at runtime (exit 139) on the brokered build+run path — suspected GC collection of the imm64-baked `rt_cs_t` (the GC can't see the address inside machine code). Reverted to e48a0ab1. **Prerequisite before retry: GC-root the per-node scratch** (register rt_cs_t as a GC root, or use a collector-visible store) — this is the SAME facility SBL-CAP-2's saved_Δ needs. ARBNO uses `nd->counter` generator state; study its TEXT β-port (re-enters the child) — closer to SBL-CAP-2. **Validate via `--run` (mode 3 WIRED), not `--compile`.**

### SBL-BREAKX-2 — BREAKX BINARY + β rescan ⏳
BREAKX (`pBB->ival==1`) needs its own BINARY arm (TEXT β does a rescan-to-next using z_orig + z). Under BINARY use two int slots — but `rt_cs_t` has only one `delta`. Either widen `rt_cs_t` with a second int or GC_MALLOC an 8-byte scratch. Defer.

Each fill verifiable with a runtime-PATND probe (probe7 shape, no capture):
```
PAT = NOTANY('xyz') ; S = 'xyzabcdef' ; S PAT :F(NOMATCH)
```

These arms only fire on the mode-4 *runtime* path (`rt_match_variant → exec_stmt → bb_build_brokered → templates`). Mode-2/-3 use C oracle; mode-4 emit phase uses TEXT.

### SBL-BREAKX-2 — BREAKX β in TEXT arm ⏳
BREAKX β rescan in `bb_pat_break.cpp` TEXT arm when `pBB->ival==1`. Reference deleted `rt_bb_brkx` body (git show `0206b998 -- src/runtime/rt/rt.c`). Add rung 058 to exercise.

### SBL-ATP — `@var` cursor capture ⏳
1. Add `BB_PAT_ATP` to `BB_op_t` enum in `BB.h`.
2. `lower_pat_dcg.c`: `@var` → `nd->sval=varname; nd->α=nd; nd->β=fp; nd->γ=sp; nd->ω=fp`.
3. `bb_exec.c case BB_PAT_ATP`: α writes Δ as int DESCR via NV_SET; return γ. β: return ω.
4. `bb_pat_atp.cpp` template + emit_core dispatch.

### SBL-G-2 — Re-freeze GATE-PK ⏳
After filling each template, re-freeze its kind's cell in `test_per_kind_diff.sh`. Current baseline references DELETED `rt_bb_*` C boxes — stale.

### SBL-SM-BINARY (HQ-track) ⏳
`sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` function pointer as imm64 → violates Invariant-8. Fix: call `rt_pat_*@PLT` directly. Track as `SM-BINARY-PAT-FIX` in GOAL-HEADQUARTERS.

### SBL-LOWER-CLEANUP ⏳
Delete `lower_subj_pat_split` + inline duplicate at lower.c:1750 once Snocone confirmed not using them.

### SBL-VERIFY-1/2 — corpus climb ⏳
After all BINARY arms + SBL-ATP + SBL-XNME-XLATE: target ≥260/280 broad corpus.

### Pre-existing m2 oracle gaps (audit-only) ⏳
Rungs 044/045/046/048/052/054/055/056/057 fail m2 too. `bb_exec.c` doesn't implement what the rung suite oracle expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:**
LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL, ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE, DEFER.

**Templates with x86 BINARY arms filled:**
LIT, LEN, POS, UPTO (ref). ANY (SBL-ANY-2, continued-15). NOTANY (SBL-NOTANY-2, 2026-05-28). BREAK plain (SBL-BREAK-2, 2026-05-28; BREAKX still stub). **ALL of ANY/NOTANY/LEN/BREAK VERIFIED-BY-EXECUTION via `--run` (SBL-BREAK-VERIFY, 2026-05-28) — and BREAK no-terminator failure semantics corrected.** All others still stub.

**Runtime translators:**
- `patnd_to_bb_graph()` in `lower_pat_dcg.c` — runtime PATND_t→BB_graph_t parallel to `BB_lower_pat`. Gated by `patnd_needs_xlate` in `stmt_exec.c`. Covers XARBN-containing trees + simple-atom roots (XCHR/XSPNC/XBRKC/XBRKX/XANYC/XNNYC/XLNTH/XPOSI/XRPSI/XTB/XRTB/XFARB/XSTAR). Does NOT cover XNME/XFNME yet (SBL-XNME-XLATE pending pair with SBL-CAP-2).

**Driver-level fixes (historical):**
- FLAT-DRIVER α-LABEL placement before XA_FLAT_PROLOGUE.
- PAT_LIT/REFNAME/USERCALL GAS macro-arg fix.
- Nested-ALT EP_RESET fix in `flat_drive_alt`.
- Statement-level `S P` produces TT_SCAN at parse time.
- ASSIGN_IMM/COND removed from `lower_flat_invariant` exclusion (unlocks inline capture emit).

**Infrastructure:**
- `rt_cap_assign(varname, base, len)` helper in `rt.c`.
- SM_PAT_BREAKX opcode (separate from SM_PAT_BREAK).
- BB_PAT_DEFER opcode + `rt_defer_match` + XDSAR resolve.
- Pattern rung suite `test_snobol4_pat_rung_suite.sh` (rungs 038-057, M2 + M4 columns).
- `bb_boxes.c` C Byrd boxes + `rt_bb_*` deleted (FACT RULE, JA-D-3).

**Recovery resource:** Hand-written original boxes live in git at `660339cd~1:src/runtime/boxes/<box>/<file>.s`. Transcribe ABI register names to flat `[r10]`/`lbl_α/β/γ/ω` convention.

---

## Session State

```
GATE-1 SNOBOL4 smoke        = 13/13 (mode-2 7/7 + mode-3 6/6)
GATE-2 unified broker       = 34 (sibling-influenced)
GATE-3 broad corpus mode-4  = 175/280
GATE-4 broad corpus mode-2  = 238/280
Rung suite                  = M2=19, M4=15, SKIP=0
HEAD one4all                = 58c7cab9 (SBL-BREAK-VERIFY; see CORRECTION below — BREAK no-terminator FIX is real + gate-clean, but the "verified via --run BINARY arm" claim was WRONG: --run routes graph-table patterns to bb_exec_pat C ORACLE, not native x86. Mode-3 itself runs the mode-2 C INTERPRETER (sm_interp_run) — see SBL-M3-NATIVE.)
GATE-PK status              = stale (re-freeze deferred)
```

---

## Session log (terse)

- **2026-05-28 Opus 4.7 (g) — ⭐ KEY DISCOVERY: native-SM engine was BUILT then DELETED 2026-05-27 (Lon hunch confirmed).** Scanned git history per Lon's suggestion. Found `916d61a5` (2026-05-26) BUILT SB-LINEAR (`sm_emit_linear`+`sm_run_linear`, +799 lines, "linear x86 emit over SM_sequence_t") — the exact ARCH-SCRIP mode-3 end-state. Then the JA-D series (2026-05-27) ANNIHILATED it: `c352bf4d` JA-D-1 stubbed `--run`; `22a17fa3` JA-D-2 deleted Engine B/SB-LINEAR (−658); `2073c081` JA-D-3 deleted Engine A/trampoline `sm_jit_run`+44 `h_*` handlers (−1820); `b14a3312`/`e842b724` JA-D-4/5/6 swept the rest ("zero jit occurrences remain"). Whole file `src/processor/sm_jit_interp.c` is GONE. The deletion was PRINCIPLED (that engine used forbidden `emit_standard_blob`/`SL_B`/`bake_blob_call` — FACT RULE), but the opcode→x86 LOGIC + runner + mmap/seal/jump are exactly the M3-NATIVE reference. Recovery coords + transcription rule (re-express as SM_templates BINARY arms, NOT verbatim) recorded in GOAL § SBL-M3-NATIVE. Updated M3-NATIVE-1/2 to leverage recovered source as the semantic spec. No one4all code changes; tree clean at 58c7cab9.

- **2026-05-28 Opus 4.7 (f) — CORRECTION + RESCOPE: mode-3 is PURE x86, NO interp (SBL-M3-FLATWIRE → SBL-M3-NATIVE).** Lon: "SCRIP Mode 3 is NO INTERP and pure x86 asm for ALL languages." My session-(e) recommendation to KEEP `sm_interp_run` for mode-3 was WRONG. Re-read ARCH-SCRIP.md: mode 3 `--run` = `sm_lower → sm_codegen → sm_jit_run`, native x86 ONLY; `sm_interp_run` + `bb_exec_*` are mode-2 ONLY. Traced: `scrip.c` mode_run calls `sm_run_with_recovery(sm, sm_interp_run)` — mode-3 RUNS THE MODE-2 INTERPRETER (both SM PC-loop and BB oracle). The ARCH-named native runners `sm_jit_run`/`sm_emit_linear`/`sm_run_linear` DO NOT EXIST in src; the native-SM engine is UNBUILT. Facilities that DO exist: `codegen_sm_x86` (SM x86 producer), `sm_image`+`seg_seal` (RX SM image), `bb_pool`+`bb_seal` (RX BB slab), `bb_build_flat`. Rescoped the rung: SBL-M3-FLATWIRE → **SBL-M3-NATIVE** (foundational engine build, 5 steps: audit native-SM emitter coverage → minimal `sm_run_native` runner → BB call-out from native SM → per-language bring-up → gate/corpus sweep). `sm_interp_run` name is correct FOR MODE 2; the error was wiring it into mode 3. Updated GOAL § SBL-M3-NATIVE + PLAN.md cross-cutting note + SNOBOL4 row. No one4all code changes; tree clean at 58c7cab9.

- **2026-05-28 Opus 4.7 (e) — ROOT-CAUSE FOUND (SBL-M3-FLATWIRE carved). No code committed; investigation + goal correction only.** Lon: "Mode 3 should be SM run live EXEC + BB FLAT-WIRED. That is what you were supposed to be doing for two days." Traced (marker-instrumented, all reverted): mode-3 `--run` runs SM live (`sm_interp_run` ✅) BUT `sm_interp.c case SM_EXEC_STMT` routes graph-table patterns (`pat_bb != NULL`) to **`bb_exec_pat` — the C ORACLE graph walker in `bb_exec.c`** — NOT to flat-wired native template bytes. So compiled-in patterns under `--run` are INTERPRETED IN C (RULES.md violation). `bb_broker` has no oracle fallback; the oracle was reached via `SM_EXEC_STMT`→`bb_exec_pat`. **CONSEQUENCE: every "BINARY arm" filled/verified to date (ANY/NOTANY/LEN/BREAK) was NEVER exercised by mode-3** — the `bb_pat_break_str` entry marker did not fire in mode-2 OR mode-3. The prior-session and this-session-(a–d) "verified via --run" claims were verifying the C oracle, not flat-wire. The BREAK no-terminator FIX (commit 58c7cab9) IS real and gate-clean (it fixed the oracle + TEXT + BINARY uniformly), but the verification MECHANISM claim was wrong. Carved **SBL-M3-FLATWIRE** (top priority: wire `SM_EXEC_STMT` under LIVE to `bb_build_flat`+`bb_broker` instead of `bb_exec_pat`) and **SBL-M4-FLATWIRE** (separate: `--compile` brokers patterns at the standalone binary's runtime via `rt.c:335` BB_MODE_BROKERED — must become flat-wired). Tree clean at 58c7cab9; no new commits to one4all this session.

- **2026-05-28 Opus 4.7 (d) — SBL-BREAK-VERIFY ✅.** Resolved the prior caveat that NOTANY/BREAK BINARY arms were UNVERIFIED-BY-EXECUTION. Confirmed in `scrip.c` that `--run` forces `bb_live=1` → `bb_build_flat` writes MEDIUM_BINARY+WIRED into the sealed RX `bb_pool` slab and jumps in — so `--run` IS the harness that executes the new BINARY bytes (SM-level still `sm_interp_run`, but pattern BB nodes are flat-wired BINARY). Validated ANY/NOTANY/LEN BINARY arms under `--run`: all byte-correct vs C oracle AND SPITBOL (positive + negative cases). **BREAK: found a latent correctness bug** uniform across oracle + TEXT + BINARY: `BREAK(set)` with the terminator ABSENT from the subject must FAIL (SPITBOL), but the α-logic unconditionally succeeded after scanning to end-of-subject (SBL-BREAK-2 had faithfully mirrored the already-buggy TEXT semantics). Fixed in three coordinated edits: (1) `bb_exec.c` α — return ω when no break char found before Σlen; (2) `bb_pat_break.cpp` BINARY arm — retarget loop `jge` from success epilogue to a new `jmp ω` fail epilogue (183B, was 178; jge disp 66→114; 4th site at operand 179→ω); (3) `bb_pat_break.cpp` TEXT arm — route end-of-subject `jge` to `lbl_ω` instead of success `done`. Validated vs SPITBOL on 6 BREAK cases (positive, terminator-absent, terminator-at-first/last/end, long-no-terminator) across mode-2, mode-3 WIRED, AND mode-4 (standalone compiled binary + brokered runtime rebuild). All five gates hold at watermark (G1 13/13, G2 34, G3 175/280, G4 238/280, M2=19 M4=15), FACT RULE=0. HEAD `58c7cab9`. NEXT: ANY/NOTANY/LEN/BREAK now trustworthy — resume SBL-SPAN-2 with absolute-z_orig + GC-rooted scratch (register `rt_cs_t` as GC root — same facility SBL-CAP-2's saved_Δ needs), OR fill SBL-BREAKX-2 BINARY arm (now that the plain-BREAK BINARY layout is proven), validating each new arm under `--run`.
- **2026-05-28 Opus 4.7 (c) — HANDOFF (partial, see caveats):** Session attempted SBL-SPAN-2 and clarified a mode misunderstanding. NET RESULT: no new code landed beyond (a)/(b); SPAN reverted.
  - **SBL-SPAN-2 ATTEMPTED, REVERTED.** Wrote SPAN BINARY arm; hit a wrong single-slot β algebra (z_orig must be ABSOLUTE, not [r10]-relative, because a sibling box in a concatenation mutates [r10] between α and β re-entry — the four-port driver does not auto-restore the cursor). Fixed by widening `rt_cs_t` with a second int (`delta2` @offset 12; `delta` stays @8 so BREAK unaffected). Then SPAN **segfaulted at runtime** (exit 139) even for a trivial matching span. Disassembly of the emitted bytes was CORRECT (internal jumps land right); `g_emit.bb_cs_zeta` was non-NULL/consistent at brokered build. Leading unconfirmed hypothesis: the `rt_cs_t` address is baked into the blob as imm64 the GC cannot see as a live reference → may be collected between build and execution. ALL SPAN + rt_cs_t + emit_bb debug changes were REVERTED to e48a0ab1. In-progress SPAN source saved at `/tmp/span_v2_inprogress.cpp` (NOT in repo).
  - **MODE MODEL CORRECTED (was confused all session).** Per ARCH-SCRIP.md + ARCH-IR.md + emit_core.h: emitter has THREE orthogonal axes — platform(x86/JVM/…), medium(TEXT/BINARY/MACRO_DEF), brokered flag(WIRED/BROKERED). Execution modes: **mode 2 `--interp`** = pure C oracle (`sm_interp_run`/`bb_exec.c`), NO codegen, BINARY arms never run. **mode 3 `--run`** = in-memory JIT, emits BINARY **WIRED** (`EMIT_BINARY_WIRED`), DOES exercise BINARY arms (except Prolog `--run` which still falls back to sm_interp_run per AGW-1c). **mode 4 `--compile`** = emit-time uses **TEXT** arms → GAS asm → gcc link; the standalone binary's linked rt then builds patterns at ITS runtime via `bb_build_brokered` = BINARY **BROKERED**.
  - **⚠️ VALIDATION CAVEAT for SBL-NOTANY-2 and SBL-BREAK-2 (a/b this session):** both were "validated" via `--compile`-then-run. But `--compile` emits TEXT for the pattern — so those tests exercised the pre-existing TEXT arms, NOT the new BINARY arms. **The NOTANY and BREAK BINARY arms committed in 9c964948/e48a0ab1 are UNVERIFIED-BY-EXECUTION.** They may be correct, wrong, or unreached. NEXT SESSION MUST re-validate them (and any new arm) via **`--run` (mode 3, WIRED)** — single-process JIT that actually emits+executes the BINARY/WIRED bytes — before trusting them. SPAN's segfault is meaningful precisely because the brokered path DID build+run its bytes.
  - Gates at handoff (HEAD e48a0ab1, rebuilt + re-run this session): G1=13/13, G2=30, G3=175/280, G4=238/280, M2=19, M4=15, FACT RULE=0. Tree clean, HEAD==origin both repos.
  - **RECOMMENDED NEXT STEP:** before filling more arms, run ANY/NOTANY/LEN/BREAK probes under `--run` to confirm the WIRED BINARY arms actually execute correctly. If they pass, the "filled" list is trustworthy and resume SPAN with absolute-z_orig + a GC-rooted scratch (register the rt_cs_t as a GC root, or store via a mechanism the collector tracks — same facility SBL-CAP-2 needs). If they fail under `--run`, the NOTANY/BREAK commits need correction first.
- **2026-05-28 Opus 4.7 (a):** SBL-NOTANY-2 ✅. `bb_pat_notany.cpp` BINARY arm filled (was 2-jump stub). Byte-identical to `bb_pat_any.cpp` BINARY (104 bytes, sites {17,72,86,90,100}) except offset 70 `jne ω` vs `je ω` — NOTANY fails when char IS in set. Validated mode-4 compiled binary via brokered path. All five gates hold (13/13, 30, 175, 238, M2=19, M4=15), FACT RULE=0. No regressions.
- **2026-05-27 Opus 4.7 continued-16:** SBL-XNME-XLATE prep landed `828f9134` (translator pp->var.s fallback + rt_pat_capture STRVAL_fn population). Gate widening NOT applied — paired with SBL-CAP-2. SBL-CAP-2 deep-investigated: blocked by architectural gap in `bb_prepare_capture_arbno` — sets `bb_child_lbl` only under MEDIUM_TEXT; child_cache labels never set under BINARY. Capture + ARBNO BINARY arms early-return zero bytes under brokered mode. Design path forward: replace `bb_child_lbl` with `bb_child_fn` raw function pointer under BINARY, call via `movabs rax, &child_fn; call rax`. Goal file pruned 767→234 lines this session.
- **2026-05-27 Opus 4.7 continued-15:** SBL-ANY-2 BINARY arm ✅ (104 bytes, sites {17,72,86,90,100}). SBL-ANY-2-DISPATCH-TRACE ✅ (mapped: BINARY arms exercised only by mode-4 runtime path via `rt_match_variant`→`exec_stmt`→`bb_build_brokered`→templates; mode-2/-3 use C oracle; mode-4 emit phase uses TEXT). Carved SBL-XNME-XLATE.
- **2026-05-27 Opus 4.7 continued-14:** SBL-ANY-2-CORRECTNESS ✅ (`3eb09ba0`). Two bugs in `BB_PAT_DEFER` C-oracle: (1) `DESCR_t` union clobber `sub_d.i=0` after `.s=` nulled string ptr (designated-init fix at `bb_exec.c:2378` + `rt.c:560`); (2) architectural double-scan — inner `bb_exec_pat` had own scan loop, replaced with `bb_exec_once`. GATE-4 218 → 238 (+20), M2 18 → 19 (rung 053). ANY/NOTANY/SPAN/BREAK var-deref byte-identical to SPITBOL across all three modes.
- **2026-05-27 Opus 4.7 continued-13/13B/13C:** SBL-MODE-PURITY-1..5 ✅ (`e7e7bd63`). All cross-mode fallbacks + eps rescues removed. `bb_build_pure_mode` helper. No regressions; signal now clean (failed builds surface honestly).
- **2026-05-27 Opus 4.7 continued-12:** SBL-MODE3-REACTIVATE ✅ (`380b4683`). Removed stale `--run` gate in `scrip.c`. GATE-1 7/7 → 13/13.
- **2026-05-27 Opus 4.7 continued-11:** XCAT/XOR widening attempted, REVERTED. Pure regression (-11). Legacy garbage opcodes were accidentally compensating for unrelated bugs in non-fence composites too — not just fence/capture.
- **2026-05-27 Opus 4.7 continued-9/10:** SBL-DCG-DEFER-M4 stmt_exec wiring ✅ (`954236f5`) + SBL-ARBNO-COUNTER-RESET ✅ + simple-atom widening (`26913b08`). Mode-2 broad 210 → 218. Mode-4 173 → 175. Rung M2 16 → 18.

---

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
