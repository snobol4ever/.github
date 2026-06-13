# HANDOFF 2026-06-13 OPUS48 — BB-FIXUP-Z-to-A — bb_retract_throw redesign recipe (cursor HELD)

**Model:** Claude Opus 4.8 · **Goal:** GOAL-BB-FIXUP-Z-to-A.md · **SCRIP @ HEAD when read:** pull first.

## What this session did
1. **Encoded the SOP** into GOAL-BB-FIXUP-Z-to-A.md (.github `f7bbe920`): NEVER skip a file; redesign/rewrite each to conformance IN PLACE; cursor advances ONLY at `audit_bb_fixup_file.sh <file>` rc=0 + gates green. Rewrote FIXUP-DISCIPLINE rule 4 (killed the PIN-NEEDED/Category-C advance license) and superseded CV5's UNPINNED-defer clause. (This corrects a prior-session misread where I advanced PAST bb_retract_throw + bb_resolve as "[S] pin-needed" — that was wrong; they get fixed in place.)
2. **bb_return** — verified CLEAN on arrival (audit rc=0, CV1–CV10 by inspection; the `if (!PLATFORM_X86 || !precond) return x86_bomb(...)` guard is the sanctioned house idiom, matching bb_scan_any/find/match committed CLEAN this lap — NOT a CV8 violation). Cursor passes it (cleared nothing → no commit earned).
3. **Mapped bb_retract_throw architecture cold** (below). Did NOT edit it — a safe redesign needs one runtime verification I ran out of budget to do (step 0). Cursor HELD on bb_retract_throw.

## CURSOR STATE
- bb_return: CLEAN, passed.
- **bb_retract_throw.cpp: HELD (next stop, UNFIXED) — execute the recipe below.**
- Then bb_resolve.cpp (58/165 — the resolver itself; see "resolver track").

## bb_retract_throw — architecture
- Dispatched via `IR_BUILTIN` → `emit_core.c:517` `bb_prepare(nd); bb_emit_x86(bb_resolve(nd));`.
- `bb_retract_throw_str(IR_t *pBB, const char *fn, const std::string &hdr)` is a **sub-handler in the bb_resolve meta-resolver chain** (`bb_resolve.cpp:155` `if (!(r = bb_retract_throw_str(pBB, fn, hdr)).empty()) return r;`). Its `(pBB, fn, hdr)` signature is **resolver-dictated**.
- 18 audit violations: raw_bytes 6 · medium_any 2 · local_vars 1 · returns_plus 5 · sig_decls 1 · multi_x86 3.
- Handles 3 builtins by `strcmp(fn,...)`: `retract`, `retractall`, `throw`. **No IR_THROW/IR_RETRACT kinds exist** (only IR_CATCH).
- TEXT arm `throw`: builds term (`emit_build_compound_term` for IR_STRUCT / `rtt_ball_scalar` else) → `call rt_throw_term@PLT`. BINARY arm `throw`: bakes node ptr → `call rt_throw(node)` (raw bytes, legacy). **DIFFERENT runtime contracts.**
- retract/retractall: BINARY sets `g_sm_native_unsupported=1` + two `jmp rel32=0` (raw bytes); TEXT no-op (falls through).

## RECIPE — execute in one pass with FULL gate battery (C1–C5)
**Step 0 (BLOCKER — do first):** read `rt_throw`'s impl body (decl `rt.h:191 int rt_throw(void *alpha_ptr)`; impl NOT in rt.h — `grep -rn 'rt_throw' src/runtime/*/*.c`). Confirm whether `rt_throw(node)` internally does node→term→throw, i.e. is observably equivalent to `rt_throw_term(build_compound_term(node))`.
  - **If equivalent:** unify both mediums onto the TEXT path (build term + `x86("call","rt_throw_term",(uint64_t)(uintptr_t)(void*)rt_throw_term)` — the both-medium 3-arg call form, per bb_query_frame precedent). This is behavior-neutral.
  - **If NOT equivalent:** keep mode-3 semantics — emit `rt_throw` via the both-medium 3-arg form `x86("call","rt_throw",(uint64_t)(uintptr_t)(void*)rt_throw)` with the node ptr loaded into rdi (replace the hand-encoded `mov rdi,imm64; mov rax,imm64; call rax` with `x86("mov","rdi",<nodeptr-imm>) + x86("call","rt_throw",ptr)` — but nodeptr-as-imm is graph-derived → see CV10 note).

**Both-medium conversions (kill the absolutes):**
- **raw bytes → x86():** the BINARY throw block (`x86_lit_bytes(bytes...+u64le...)`) and the retract double-`jmp` (`bytes(1,"\xE9")+u32le(0)` ×2) ALL go. `x86_lit_bytes`, `bytes(`, `u32le`, `u64le` are FORBIDDEN in templates.
- **medium branches → one body:** delete `if (MEDIUM_BINARY)` / `if (MEDIUM_TEXT)`; one medium-agnostic body keyed only on `fn`.
- **retract/retractall arm → both-medium native-unsupported** (copy bb_findall's pattern, bb_findall.cpp:34): `extern int g_sm_native_unsupported; g_sm_native_unsupported = 1; return hdr + x86("jmp","ω") + x86("def","β") + x86("jmp","ω");` — VERIFY first that `g_sm_native_unsupported`'s consumer (trace it: `grep -rn g_sm_native_unsupported src/` — read sites, NOT the `=1` writes) tolerates the `jmp ω` form vs the old `jmp rel32=0` placeholder.
- **rtt_ball_scalar / rtt_lbl @PLT hazard:** `rtt_ball_scalar` uses `x86("call","rt_node_to_term@PLT")` (2-arg, @PLT-in-name) — TEXT-only-safe; in BINARY @PLT can't bake. Convert to 3-arg both-medium `x86("call","rt_node_to_term",(uint64_t)(uintptr_t)(void*)rt_node_to_term)` (confirm rt_node_to_term is a linkable decl). Same audit for any string-built `[rip + ...]` lea operands.
- **folds:** returns → one per platform via IF() combinators (CV4); split multi-`x86(` lines (CV4); remove the `IR_t *a` local (CV6) — inline `ir_call_arg(pBB,0)` or deliver via prepared field.

**CV9/CV10 (params + IR-graph access) — RESOLVER TRACK, larger:** `(pBB, fn, hdr)` and `ir_call_arg(pBB,0)`/`IR_LIT`/`a->op` are dictated by the bb_resolve resolver convention. Full CV9/CV10 conformance for bb_retract_throw is INSEPARABLE from redesigning the IR_BUILTIN resolver (split into per-builtin IR kinds dispatched from emit_core with bb_prepare-delivered `_.op_*` fields, OR change the resolver's prepared-field convention — affects ALL sub-handlers: bb_is_cmp, bb_type_test, bb_term_inspect, bb_term_io, bb_findall, bb_retract_throw). **This is a dedicated multi-session resolver-redesign track.** Until it lands, bb_retract_throw can clear raw_bytes/medium/returns/multi_x86/local (behavior-neutral, gate-green, committable WITHOUT advancing the cursor) but will retain sig_decls (params) → not rc=0 → cursor stays until the resolver track completes. Recommend: schedule the resolver redesign as the vehicle that brings the whole IR_BUILTIN sub-handler family to rc=0 together.

**Verification:** C2 throw probe e.g. `:- initialization(main).\nmain :- catch(throw(my_err), E, (write(caught(E)), nl)).\n` (confirm it fires the throw arm: `./scrip --compile --target=x86 p.pl | grep rt_throw`); m2=m3=m4 byte-identical; FULL C3 floors (smoke 7/7/7, pat M4 19/0, prove_lower 68P+3FAIL rc=0, prolog 5/5/5, icon m2 12/12, purity 2, bin_t 0, medium_invisible ≤103, handencoded 0, vstack 3, sno_pat_reg HARD).

## NOT MINE — pre-existing rebus regression
`test_smoke_compile_hello_all_langs` rebus row FAIL-compile (5/6 vs baseline 6/0), entered b063b07→fc307d9 window per prior watermarks; untouched, needs owner (NOT this goal).
