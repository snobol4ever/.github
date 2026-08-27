# FINDING 2026-08-27 seat07 — `rt_jmp_frame_lexprep2` no-op cured for the non-retry path (mode-4 correct); multi-clause predicates that actually backtrack still crash in both modes, root cause NOT found

**Row:** `prolog-multiclause-uninit-lexprep-frame`. **SCRIP** `bf694b2b` + this session's two commits (pristine-built at `-O0`). **DONE-WHEN not met** — rung13/14/15 are unchanged (0/5, 2/5, 1/5) from the pre-session baseline, because every program in those rungs exercises actual backtracking, which hits the second, unresolved bug below. This is not a scoped fix; it's real, verified progress plus an honest handoff of what's left.

## What was found and fixed

`rt_jmp_frame_lexprep2` (`src/runtime/rt/rt.c`) was a complete no-op (`{ (void)fb; (void)suffix_off; (void)region_bytes; }`), called from every multi-clause/generator predicate's frame prologue (`xa_flat_zframe_prologue_str`, `src/templates/xa_flat.cpp:281-294`, the `g_flat_dc_np < 0` branch). Two separate defects in that path, both now fixed:

**(1) The frame was never zeroed, and pending retry state was never installed.** The sibling branch (`g_flat_dc_np >= 0`, ordinary det calls) zeroes the frame then calls `rt_icn_zframe_args_install`; this branch did neither. The runtime already had a complete, working "staging" mechanism for retry state — `rt_pl_zf_resume_set(cursor, tm_lo, tm_hi, tm_off, cursor_off)` (`rt.c:1725`, called from `bb_call_proc_staged.cpp`'s `pl_zf_resume` arm, PL-FR-4) stashes the retained resume-continuation pointer and two trail-mark longs into globals (`g_pl_zf_pending_cursor` etc.) right before jumping back into the callee's α entry — but nothing ever consumed them. Fixed:

```c
void rt_jmp_frame_lexprep2(void *fb, long suffix_off, long region_bytes)
{
    (void)suffix_off;
    memset(fb, 0, (size_t)region_bytes);
    if (g_pl_zf_pending_cursor) {
        *(void **)((char *)fb + g_pl_zf_pending_cursor_off) = g_pl_zf_pending_cursor;
        *(long  *)((char *)fb + g_pl_zf_pending_tm_off)     = g_pl_zf_pending_tm_lo;
        *(long  *)((char *)fb + g_pl_zf_pending_tm_off + 8) = g_pl_zf_pending_tm_hi;
        g_pl_zf_pending_cursor = (void *)0;
    }
}
```
Verified by breakpointing `rt_jmp_frame_lexprep2` for a genuine resume call and reading the frame back afterward: the cursor and both trail-mark longs land at exactly `fb+cursor_off` / `fb+tm_off` as expected (gdb session, see below).

**(2) The generator branch's args-install call re-zeroed what (1) had just written.** My first cut added a call to `rt_icn_zframe_args_install(fb, np, nl)` right after lexprep2, mirroring the det branch, to install the caller's staged arguments (`g_call_args[]`) — needed because a 1-param call like `foo(X)` was reading `X` back as an all-zero `DESCR_t`, corrupting downstream dispatch (root-caused via `gdb`: `r13`/`r14` reading 0 at the crash, `rt_icn_zframe_args_install` breakpoint showing `nparams=0` for the wrong call — see full trace in this row's LEDGER discussion). But `rt_icn_zframe_args_install`'s locals-zero loop assumes locals sit immediately after params (`base+(np+j+1)*16`); in the generator-frame layout that's false — `zeta_storage.c` reserves `resume_off` (and `zeta_mark_off` where applicable) *between* params and named locals (`zeta_storage.c:447-466`, computed strictly after the main per-node slot-granting loop). Passing the real `nlocals` re-zeroed the resume/trail-mark slots (1) had just restored. Fixed by passing `nlocals=0` always — the locals region is already correctly zeroed by lexprep2's `memset`; the args-install call now exists purely for its param-copy loop, which *is* offset-compatible (params always occupy `[16, base)` in both layouts).

**Verified, mode-4 (`--compile`), non-retry case** — `foo(1). foo(2). main :- foo(X), write(X), nl.` now correctly prints `1` (was: SIGSEGV nondeterministically, or silent empty output — matching the parent finding's description exactly). No `Term`/heap involvement, no new globals; consistent with Lon's s273 design ruling.

## What's still broken

**(A) Mode-3 (`--run`, BINARY/JIT) crashes even on the fixed non-retry case above**, though mode-4 is correct. `m3 ≡ m4` is supposed to be a design invariant (shared codegen) — this divergence means the remaining bug is mode-3/BINARY-medium-specific, not a codegen-shape bug. gdb (ASLR disabled by default under gdb, ptrace stops cleanly, no env var needed): crash PC lands inside the JIT slab (confirmed via `info proc mappings` — executable, anonymous, not corrupted-jump-to-nowhere), at a `mov r12, [rcx*2 − 0x7bf01b7b]`-shaped instruction (hand-decoded from raw bytes independent of disassembler alignment: `4d 8b 24 4d` + disp32 `85 e4 0f 84`). `rcx` at the fault holds `&rtccb` (the RTCC register-liberation state block address, per `info symbol`), used as a scaled index — that's a type confusion, not a sane address computation. Traced back through the `$trail_mark` builtin call and the RTCC save/restore veneer (`movabs &rtccb,rcx; mov r8,[rcx+0x28]; ...`) without finding where `rcx` is supposed to be reloaded before this point, or which encoder emits the faulting instruction. Not resolved.

**(B) Multi-clause predicates that actually backtrack still crash in *both* modes** (`fact(a). fact(b). fact(c). main :- fact(X), write(X), nl, fail ; true.` — `test_smoke_prolog.sh`'s long-standing red `clause`/`recursion` rows, and every rung13/14/15 program). Root cause NOT found. What's confirmed:
- `rt_pl_zf_resume_set` stages sane values (`cursor=<n4_suspend_β>`, a real code label; `tm_off`/`cursor_off` plausible offsets).
- `rt_jmp_frame_lexprep2` (fixed per (1)) correctly writes that cursor and both trail-mark longs into the new frame at the right offsets — verified by reading the memory back with gdb immediately after the call returns.
- `fact$2F1_α_body`'s *own* compiled prologue (the few instructions right after the lexprep2/args-install pair) unconditionally does `lea rax,[rip+n4_suspend_β]; mov [rsp+0x1c0],rax` — i.e. it writes a *fixed* code label into the exact same resume-slot offset, on every entry, fresh or resumed. In the one retry this test exercises, that fixed label and the retained cursor happened to be identical, so this coincidence masked whether it's a real conflict. **Whether this unconditional write is intentional (e.g. establishing "where to resume if this activation itself suspends," a different concept from "which clause to try next") or a second instance of the same defect class is not determined.** Mode-4 fails with SIGILL/SIGSEGV (varies by which of my two fixes is in place) inside `__libc_start_call_main`'s return path — the CPU jumps to a stack address holding raw uninitialized bytes, with a plausible real code address (`0x402f96`) sitting unused in `rax` at the fault. That shape (a good address computed but never actually used as the jump target) says the bug is downstream of correct-looking state, same texture as (A).

## Verification this session (control arms, no regression)

Same-session measurement, per `GOAL-ICON-100.md`'s binding rule (no DONE-WHEN may rely on a quoted historical score):
- **SNOBOL4** `bash scripts/test_corpus_snobol4.sh`: **365/365 both modes, FAIL=0 SKIP=0** — identical before/after (pristine `-O0`, this session's tree, before any edit and after both fixes).
- **Icon** `bash scripts/test_icon_rung_suite.sh --mode {interp,run,compile}`: **245/17/1/30, 245/17/1/30, 243/19/1/30** before and after — fail-set **name-for-name identical** across all three modes (diffed, not just totals). Confirms `GOAL-ICON-100.md`'s own s247 finding that Icon never reaches `xa_flat_zframe_prologue_str` (`g_emit.zframe_graph` is always 0 for Icon graphs) — this row's changes are structurally inert for Icon, measured rather than assumed.
- Prolog `write_atom`/`unify`/`arith` smoke rows: unchanged PASS, all three modes.

## Disposition

Pushed as real, verified, non-regressing progress — not a claim that this row is done. Recommend the next session start from (B) with a fresh, focused repro (the `fact/1` 3-clause case above, minimal already) and pull the *whole* compiled body of `fact$2F1` (mode-4, real symbols, `objdump -d` or gdb `disassemble`) rather than incremental breakpoint archaeology — establishing what `n4_suspend_β`/the `0x1c0` slot's write-once-vs-restore contract is actually supposed to be will very likely explain (A) too, since both crashes have the same "a correct-looking value exists somewhere but the wrong one gets used as a control-flow target" shape.
