# FINDING 2026-08-01 — SN4 WIREREG: the DEFINE return wires were caller stack garbage, and the A/B artifact is the `.so`, not the `scrip` binary (s22u)

Session: s22u (Claude). Scope: `SCRIP/src/templates/bb_save_restore.cpp` (one arm, 4 instructions) + demo/benchmark/feature `.s` artifact regen. SCRIP `2edd3497`; corpus `67b6cbc5` + the benchmark/feature artifact commits. Opened by Lon's own observation, from reading `roman.s`, that a `call exit@PLT` was being performed inside a PROC — followed by the question "where is the BB_SAVE_RESTORE and BB_CALL_FUNCTION linkage which is supposed to be created from the DEFINE constant folding?"

---

## THE ANSWER TO LON'S QUESTION: THE LINKAGE IS THERE. WHAT IT READ WAS NOT.

DEFINE constant folding is producing the two-BB shape correctly. In `roman.s` at HEAD the stub blob `proc_ROMAN_α` is exactly `n117_save_restore_α` (role-3 WIRE-ADOPT) → `n118_goto_deferred_α`, and the call sites (`n12/n81/n131_call_α`) and the RETURN/FRETURN floaters (`n19/n29/n89/n117/n123_save_restore`) are all emitted. Nothing in the family was missing.

**The defect was in what the wire-adopt box READ.** It marshalled `[rsp+kt-24]` / `[rsp+kt-16]` into the pcall wire quad. Those header bytes were written by `xa_flat`'s jmp-entry prologue — **which CARVE-KILL (s22o) deleted.** `proc_ROMAN_α:` has no prologue instructions at all. With no writer, the box shipped **caller stack garbage** as the γ/ω return wires, and every DEFINE'd function returned through a wild jmp.

This is a **CARVE-ERAD casualty on the return path** — the same class as the s22r `envp` corruption (an unarmed frame-relative reader addressing a region nobody establishes anymore), except reading garbage rather than writing through live process state.

### The measurement that localized it, in four steps and no template bisect
1. `roman.sno` at HEAD: **both modes rc=139, ZERO output.** (Not a stale artifact — swept the compiler, per the RULES clause.)
2. Break on the RETURN floater: it reaches `jmp *rcx` with **rcx = `0x7ffff4dba3d8`**, which `info symbol` cannot name and which disassembles as zero bytes — inside `libscrip_rt.so`'s zero pages. Hence the `#1 0x0` backtrace.
3. `c_rt_flat_ret_snap`'s `if (!w->gw || !w->ww)` guard **passed, because garbage is non-null.** A loud guard that only tests for NULL cannot see a stale-address class.
4. Read the caller: **both** paths (`rt_proc_call_open` classic and `rt_proc_call_open_slim`) do `lea rcx,<γ>; lea rdx,<ω>; jmp rax`. The wires were in registers the whole time.

### The fix — THE MODEL applied, zero storage
Wire-adopt is the FIRST box of the stub blob, so rcx/rdx are still live and rsp is still blob-entry rsp:

    mov rdi, rcx        ; γ wire, from the register
    mov rsi, rdx        ; ω wire, from the register
    lea rdx, [rsp+0]    ; entry rsp — no header, rsp IS the base
    mov rcx, rbp        ; caller rbp, live

Zero header, zero carve, zero prologue dependency. ⛔ **Marshal order is load-bearing:** `rdi←rcx` and `rsi←rdx` must precede the rdx/rcx overwrites.

Scoped to the depth-static arm (`!emit_jmp_pin_rbp()`), which is what DEFINE stubs take — they are jmp-entry but not pat/gen/deep. The pinned and island arms are untouched; they were not shown to be broken and speculative edits to them would have been unmeasured.

---

## MEASURED — 2-arm A/B, corpus/crosscheck (318), set-diffed

| | m3 | m4 | DIVERGE |
|---|---|---|---|
| base | 197 P / 111 F / 9 T | 195 P / 112 F / 9 T / 1 LERR | 2 |
| new  | 203 P / 103 F / 11 T | 200 P / 105 F / 11 T / 1 LERR | 2 |

**FIXED in BOTH modes, ZERO BROKEN in either:** `084_define_loop_call` · `1010_func_recursion` · `1013_func_nreturn` · `1014_func_freturn` · `213_indirect_name`.

That set is **exactly the functional-linkage family and nothing else** — the same "N failures is ONE authority" shape as s22n's 311 and s22q's 244. Each of the five verified **3/3 FAIL in base, 3/3 PASS in new** under bare interactive exec, not just inside the sweep.

⚠ **`042_pat_break`'s apparent m3 FAIL→PASS is VOIDED as cushioning noise.** It segfaults **3/3 in BOTH arms** on bare exec; only the sweep's env shape hid it. This is the s22t instrument law earned a second time, and it is the sole reason the naive DIVERGE reading (2→3) is wrong — DIVERGE is **unchanged at 2**. Counts from a sweep are not evidence until the movers survive a bare-exec repeat.

⚠ `test_case` / `test_math` move FAIL→TIMEOUT. Both were already failing; they now get further and hang. Not a regression, but a real behaviour change worth naming.

---

## ⛔⭐⭐⭐ INSTRUMENT LAW — THE A/B ARTIFACT IN THIS TREE IS `out/libscrip_rt.so`, NOT `scrip`

`scrip` is a thin driver. **The emitter and every template compile into `libscrip_rt.so`**, which is simultaneously the mode-4 runtime. Therefore:

**Snapshotting the `scrip` executable for a base/new comparison yields two binaries with IDENTICAL md5 that BOTH load the CURRENT templates.** The A/B is perfectly vacuous and reports "identical by set" no matter what was changed — the most dangerous possible null, because it looks exactly like a clean neutrality result.

I hit this exactly. Three snapshots (`scrip_base`, `scrip_new`, `scrip_chk`) came back md5-identical **while demonstrably emitting different code**, and it was caught ONLY by running `--compile` through each arm and diffing the emitted box — the METHOD LAW's positive control (s22r: *"before believing any null, grep the emitted output for the thing you injected"*), which has now paid for itself twice in two sessions.

**The correct procedure:** copy `out/libscrip_rt.so` into a per-arm directory, select the arm with `LD_LIBRARY_PATH`, and **prove the probe is present in BOTH arms** (`--compile` one witness, diff the box) before running a single sweep.

⚠ Second trap in the same dance: after `git checkout` of one template, `make` **silently no-ops** and returns `rc=0` — the s126 timestamp class. `touch` the TU and re-verify emission; never trust the return code.

---

## METHOD NOTE — the canonical crosscheck script still dies detached (s22t, re-confirmed)

Replaced with a lean resumable 2-arm runner: `xc.sh <scrip> <out.tsv> <start> <count>`, `RTDIR` selecting the arm, TSV per program (`name, m3verdict, m3rc, m4verdict, m4rc`), 8s timeouts, chunked ~110 programs per invocation to stay inside per-tool-call limits. Set-diffing is then a `join` on the two TSVs. Rebuild from this description if needed.

---

## WHAT THIS BUYS THE ~1054-READER LADDER

WIREREG is a **proof of method for CARVE-ERAD**, on the smallest possible instance: **one reader family, converted from a dead frame header to its true per-BB/register source, +5 programs in each mode, zero regressions.** The pattern-blob ZD family is the same operation at ~1054× the scale. The `>344 max_rsp_off` bucket remains the progress metric; nothing this session moved it, and nothing this session claims to have.

---

## OPEN, AND THE FIRST ONE IS DIAGNOSED AND READY

1. ⭐⭐⭐ **The α/γ whack asymmetry.** `α`'s rbp pin is guarded (`emit.cpp:2153`); the `γ/ω` whack (`emit.cpp:2512-2513`, `bb_glue_outer_γ/ω` → unconditional `bb_glue_framed_leave()`) is **not guarded at all**. A jmp-entry DEFINE stub therefore never pins rbp and whacks through it anyway — which is the literal source of the `mov rsp,rbp; pop rbp; ...; call exit@PLT` Lon read in `roman.s`, and is the trap `bb_glue_flat.cpp`'s own comment names (*"omitting (1) while keeping (3) loads the CRT caller's rbp into rsp"*). **Both sites are inside one function** (`codegen_flat_chain_body`), so the cure is a function-local capture — compute the predicate once at α, consume it at γ/ω — i.e. law-4 RBP enforced as a matched pair under ONE authority. ⚠ Suppressing the whack alone still leaves `exit@PLT` on a proc graph; the live `n0_goto_β → proc_LBL__ROMAN_ω` edge ought to route to the ω wire (an FRETURN), not kill the process. That is a semantics decision, not a codegen tweak.
2. **`roman` now runs but its arguments are unbound** — every line prints `" -> "`; m3 dies `Error 101 ... eq first argument is not numeric`. The wild jmp is gone, so this is the next bracket and it is MONITOR territory. Suspect the staged-arg install / nparams registration: `proc_startup` registers `LBL__ROMAN` with **nparams=0** and `ROMAN` with **nparams=2** (pnames `N`,`UNITS`) although `DEFINE('ROMAN(N)UNITS')` declares ONE formal and ONE local.
