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

### SBL-NOTANY-2, SBL-BREAK-2, SBL-SPAN-2, SBL-ARBNO-3 — BINARY arms ⏳

Same template as SBL-ANY-2 (continued-15). Mirror TEXT arm byte-for-byte; sites table; `movabs` for in-process addresses; `bb_bin_t` listing rel32 offsets. Reference: `bb_pat_any.cpp` (104 bytes, sites {17,72,86,90,100}).

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
LIT, LEN, POS, UPTO (ref). ANY (SBL-ANY-2, continued-15). All others still stub.

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
GATE-2 unified broker       = 30 (sibling-influenced)
GATE-3 broad corpus mode-4  = 175/280
GATE-4 broad corpus mode-2  = 238/280
Rung suite                  = M2=19, M4=15, SKIP=0
HEAD one4all                = 828f9134 (SBL-XNME-XLATE prep)
GATE-PK status              = stale (re-freeze deferred)
```

---

## Session log (terse)

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
