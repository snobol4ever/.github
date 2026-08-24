# FINDING 2026-08-23 seat01 — N-1(b/c) landed: Icon procedure calls onto the SN4 wire-stack pair, plus a stack-parity bug found and fixed along the way

**Row:** `icon-n1-wire-stack-crossing` (rank 0, dispatched by hq_P under Lon's 100%-Icon order). **Commit:** SCRIP `15738e4a` (+ regen commits `1fbd628a` SCRIP feature artifacts, `35b7d034` SCRIP crosscheck artifacts, and three regen commits in corpus: benchmark/demo/no-op, `fdf8c865` programs (icon/prolog/rebus), prolog-bench).

## What landed

Per the GOAL-ICON-100.md s247 cursor's design (verified against the *actual* live `rt_proc_enter` asm, not just the prose): Icon procedure calls convert from raw rcx/rdx delivery to the caller-pushed `{ω,γ}` pair, matching SN4's law 0a/0a′.

- **Caller** (`bb_call_proc_staged.cpp`, all 4 `bb_glue_pass_wires(3, 4)` sites — the general fallback arm, the legacy flat-glue arm, the `is_dyn` arm, and `bcps_spine_gen_arm`): now route through two new helpers, `bcps_wire_cross(gid,wid)` and `bcps_wire_land(fname)`, gated by `SCRIP_ICN_WIRE_STACK` (default on). On: always push the real pair via the existing `bb_glue_pass_wires_blob` (no new spelling); release the pushed pair at the landing label **only** when the callee does not consume it itself (`!bcps_wire_pair_consumed(fname)` — the Icon/frame-contained case). A callee that already consumes the pair as part of its own exit (SN4 DEFINE's `pop rcx;add rsp,8;jmp rcx` floater) needs no release at landing — releasing there too would double-free. This also **deletes** the old compensation dance (`bcps_wire_pair_consumed`-gated dummy push before the old raw delivery) — a pushed pair the callee pops needs no discriminator, exactly as the rung text says.
- **Callee**: `emit.cpp`'s `flat_lcl_proc` prologue no longer stores rcx/rdx into `[kt-24]/[kt-16]`. `xa_flat.cpp`'s `xa_flat_zframe_epilogue_{γ,ω}_str` ICN-FR-2 fallback (the plain-`return` case, generator arms above it untouched — those are N-2's) does a **non-consuming** `jmp` through the caller-pushed wire at `[rsp+0]`/`[rsp+8]` (`bb_glue_wire_γ`/`_ω`) instead of reloading from the header. `xa_flat_wire_hdr_base()` is **deleted** (its formula duplicated `emit.cpp`'s own `frame_total`; inlined at its two remaining call sites) — the task's DONE-WHEN literally greps for its absence, so this isn't optional polish.
- **A fifth site the brief didn't name**: `xa_flat_dc_stub_str`'s "dc" fast-path trampoline (`<name>_dcα`). Any call the compiler can resolve to a fixed, small-arity target (e.g. `add2(3,4)` in the witness below) bypasses `bb_call_proc_staged.cpp` entirely and jumps straight here. It reaches the *same* converted callee, so it needed the same conversion — converted, scoped the same way (see the parity bug below for why this one bit).

**Both epilogue functions and the dc-stub are scoped to `icn_cells_graph && flat_lcl_proc` specifically**, not the wider `xa_flat_class_zf()`/outer-`if` predicate they sit inside — that predicate also admits pure `zframe_graph` (Prolog/Raku/Pascal), whose callee side this rung never touched. Getting this scoping wrong was the second bug found (below); it's now guarded three times (epilogue-γ, epilogue-ω, dc-stub).

## The bug: a 3-qword push is not 16-byte neutral

The dc-stub needs to preserve **three** values across the callee's run: the real return address (the stub's own caller expects one back), plus the pushed γ/ω pair. The old code preserved the return address by pushing it **twice** (`pop r12; push r12; push r12`) and consuming both copies at the landing labels (`pop r12; pop r12; jmp r12`) — two pushes, matching the pre-conversion protocol's zero-push wire delivery, net stack effect `-8` relative to the stub's entry.

My first attempt made the second push conditional on the killswitch (skip it under the new default, since only one copy is needed once the pair is pushed via `add rsp,16;pop r12;jmp r12` at landing). That's **3** real pushes net `-16` from entry instead of old's `-8` — an **8-byte** shift, not a 16-byte one. Every call through this path now entered the callee 8 bytes off the alignment class the old path established.

This is invisible for a callee whose own body never calls anything alignment-sensitive (the `add2` witness — plain arithmetic, no nested calls — ran fine both modes). It SIGSEGVs the instant the callee's body calls **any built-in** that eventually hits glibc's SSE-aligned string/printf paths — confirmed by gdb backtrace landing inside `__printf_buffer_init`/`vsnprintf` under `image()`. A nested call to a **user-defined** procedure never triggered it (BB-to-BB jumps don't care about SysV alignment); only a crossing into libc did.

**Minimal repro** (ablated from the real witness by binary-truncating the corpus `rung36_jcon_kwds.icn`'s body one `every kw(...)` line at a time — one call already crashes once the callee's body contains any nested call to a builtin):
```icon
procedure kw(label, value)
   write(label, ": ", image(value))
   return
end
procedure main()
   kw("allocated", &allocated)
end
```
No `every`, no alternation — `bcps_spine_gen_arm` was never involved; this is a plain deterministic call landing in the dc-stub.

**Fix:** keep the double-push unconditional (`pop r12; push r12; push r12`, same as the old path, always) and land the pair *on top* of that. Landing releases `24` bytes (pair + one r12 duplicate — the two duplicates are identical values, so it doesn't matter which is discarded and which is popped) instead of `16`. Net effect: `E-24` vs old's `E-8`, a clean 16-byte multiple apart — same alignment class. Verified: the minimal repro above, and the full `rung36_jcon_kwds.icn` (which was crashing on the very first keyword), now match `.expected` exactly, both m3 and m4.

**Lesson for the next rung that touches a caller-side stub carrying a stashed return address across a callee crossing: count pushes, not "does it look right" — the required invariant is that the new total differs from the old total by a multiple of 16, not that it "does the same job." A correct-looking non-consuming release is not sufficient if the push count that feeds it is parity-wrong.**

## Verification

- **Board (m3, `test_icon_all_rungs.sh`), two clean solo runs (no concurrent jobs — see the false-signal note below), fail-set byte-identical**: `PASS=232 FAIL=31 XFAIL=30 TOTAL=293` — **identical name-for-name to the pre-session baseline**, itself confirmed on two agreeing runs before I touched anything. Zero regressions, zero new passes (this rung's DONE-WHEN is about the crossing mechanism, not about closing the standing 31).
- **m4 twin** (`test_icon_x64_all_rungs.sh`): `PASS=218 FAIL=45 XFAIL=30`. The three m4-specific new-looking entries (`rung37_cset_ops` timeout, `rung37_proc_lookup` timeout, `rung37_subscript_genproc` SIGSEGV) were individually verified byte-for-byte reproducible under `SCRIP_ICN_WIRE_STACK=0` (old protocol) — pre-existing, not this rung's doing.
- **Named witnesses**, m3 and m4 both: `rung37_mutual`, `rung37_neg_pos` (exact match vs `.expected`); `add2.icn` (`procedure add2(a,b);return a+b;end` — the s247 cursor's own minted witness) prints `7` both modes.
- **SN4 crosscheck `1010_func_recursion`** (the DEFINE-shape witness the rung text names, "SN4 side must stay byte-identical"): reads `PASS 1010_func_recursion (4/4)` in both modes, **and** under `SCRIP_ICN_WIRE_STACK=0` its `.s` is byte-identical to the pre-session tree (module the compensation-block's own comment text, which now names the new switch instead of the old one — zero instruction/byte difference, TEXT-only annotation). ⚠️ Under the **new default** its `.s` is *not* byte-identical to before — it's **shorter** (the compensation dance it used to need is gone) but behaviorally identical. "Byte-identical" in the rung text is the `=0` killswitch invariant, not a claim that the default output never changes — see RULES.md's own "killswitch per behavioral family, `=0` byte-identity is a completion criterion."
- **SN4 broad corpus**: `345/1` both modes, the one fail (`demo_treebank`, Error 235) reproduced identically on the untouched pre-session tree (`git stash`, rebuilt, ran) — pre-existing.
- **Prolog honest invariant**: `PASS=1 FAIL=0 ABORT=0 ORACLE_CRASH=184` — sums to the documented 185.
- **Mandatory codegen regen** (RULES.md handoff step 4, all six scripts, in order): SN4 benchmark/demo artifacts **unchanged** (0 diffs). SCRIP feature + crosscheck: 2 files changed total, both `1010_func_recursion.s` copies (shrink, as above), both re-verified to still `PASS`/match `.ref`. **corpus programs (icon+prolog+rebus): 516 of 664 changed** — this includes Prolog files (`programs/prolog/wordcount.s` among them) because `bcps_spine_gen_arm` is a shared mechanism, not Icon-exclusive, and Prolog's generator-style calls route through the exact same 4 sites. **Verified, not assumed**: `wordcount.pl`'s actual `--run` output is byte-identical old vs new; `zebra.pl` (prolog-bench, 19/22 changed) core-dumps identically both modes (pre-existing, unrelated); a sample of the EMIT-FAIL entries (10 `jcon_*`, several `snocone/*`) reproduce identically under the killswitch. This is a real, verified side effect, not scope creep I'm asking you to trust blind — but it IS Prolog's own generator-call mechanism picking up part of the SN4-wire-stack conversion a rung early. See "THE PROLOG TWIN" in GOAL-ICON-100.md: Prolog is explicitly "one step behind on the same ladder," so this isn't incoherent, but it's worth a ruling on whether it should be called out as a PZ-ladder credit or left as an unattributed side effect.

## ⛔ False-signal note for whoever reads a future board run on this shared box

Running `test_icon_all_rungs.sh` concurrently with 3 other heavy background jobs (m4 board + SN4 broad + Prolog honest, all launched in parallel this session) produced a board output missing ~60 programs entirely from the PASS/FAIL/XFAIL tally (not failing — **absent**, as if the harness silently truncated mid-run) plus 8 spurious-looking new FAILs that vanished on a clean solo re-run. hq_P/hq_C were independently running `scorecard_icon`/`honest_icon`/`make all` pristine builds on this same box at the time (seen via `ps aux` — this is a shared machine under FLEET-4, not a dedicated one). **Always run the Icon board solo before trusting a delta**, especially when other seats or HQ may be active — this is the "non-empty is not alive" class from a new angle: a partial-but-plausible table from resource contention, not a missing oracle.

## Files touched
SCRIP: `src/emitter/emit.cpp`, `src/templates/bb_call_proc_staged.cpp`, `src/templates/xa_flat.cpp` (commit `15738e4a`).

## Not done (left for later rungs, on purpose)
- **CLASS-ZF 9× re-spellings** (gap census item #6): not collapsed to `xa_flat_class_zf()`. Located (7 of the 9 in `emit.cpp` at the `icn_cells_graph && flat_lcl_proc` predicate), not touched — lower risk than the crossing itself but a separate, mechanical cleanup; didn't want to enlarge this rung's blast radius after the parity bug.
- Everything gap-census items #1-#4 name (generator activation frames, the process-global generator side table, `icn_zframe_gen`) is explicitly N-2's, untouched here.

## LEDGER
2026-08-23 seat01, claim `icon-n1-wire-stack-crossing` (ASSIGNED-BY hq_P). Landed per above. Two things AWAITING a ruling, filed as `ask`:
1. The task's literal `DONE-WHEN` requires `PASS -ge 247`; the goal file's own s267 cursor already documents the confirmed-current watermark as 232 (a 15-program drop between s247 and s267, attributed to something other than this rung — flagged by hq_P as "a signal, not a watermark, re-baseline before attributing"). My two-clean-runs baseline (232, taken before touching any code) and my post-change result (232, identical name-set) agree exactly. I'm treating "no regression from the confirmed current baseline" as this rung's bar rather than blocking on a stale absolute number — see `ask icon-n1-247-vs-232` for the record.
2. The Prolog side-effect above — worth a ruling on whether it's PZ-ladder credit.
